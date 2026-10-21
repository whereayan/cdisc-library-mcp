#!/usr/bin/env python3
"""Pre-publish secret gate for cdisc-library-mcp.

Scans build artifacts (and, optionally, the git-tracked source tree) for
credentials that must never reach PyPI. An early release shipped a local client
config containing a live API key inside its sdist, which is exactly what this
catches.

Usage:
    python scripts/check_secrets.py dist/*            # check artifacts
    python scripts/check_secrets.py --tracked         # check git-tracked files
    python scripts/check_secrets.py --configure-hooks # install as git pre-commit + pre-push

Exit code 0 = clean, 1 = findings (prints file, line and a redacted excerpt).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# value patterns: (label, regex). Keys are matched case-insensitively.
SECRET_KEYS = re.compile(
    r"""(?ix)
    ["']?                              # optional quote
    (
        cdisc_api_key | api[_-]?key | apikey |
        secret[_-]?access[_-]?key | access[_-]?token |
        refresh[_-]?token | client[_-]?secret |
        password | authorization | bearer[_-]?token |
        x[_-]?api[_-]?key
    )
    ["']?\s*[:=]\s*                    # separator
    ["']?                              # optional quote
    ([^"'\s,}\]]{8,})                  # the value
    """
)
# Token-shaped values that are secrets even without a key name next to them.
TOKEN_PATTERNS = [
    ("32-hex key (CDISC-style)", re.compile(r"\b[0-9a-f]{32}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("GitHub PAT (fine-grained)", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("AWS secret access key", re.compile(r"\b[aA][wW][sS]_[sS]e[cC]r[eE][tT]_a[cC]c[eE][sS][sS]_[kK][eE][yY]\b[^\S\n]*[:=][^\S\n]*['\"]?[A-Za-z0-9/+]{30,}")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
# Values that mean "no secret here".
PLACEHOLDERS = re.compile(
    r"""(?i)^($|your[-_]?api[-_]?key[-_]?here|your[-_]?key|<.*>|\$\{.*\}|
       changeme|placeholder|example|dummy|test[-_]?key|xxx+|
        sk-[a-z]+|REPLACE[_-]?ME.*|secret|none|null|todo)$""",
    re.VERBOSE,
)


# Trailing marker to exempt a line that legitimately looks like a credential
# (e.g. this scanner's own detection patterns and the tests that feed them).
ALLOW_MARKER = re.compile(r"allowlist secret", re.I)


def _entropy_ok(value: str) -> bool:
    """Treat a value as live when it looks random enough to be a real credential."""
    if PLACEHOLDERS.match(value.strip()):
        return False
    if len(value) < 16:
        return False
    distinct = len(set(value))
    return distinct >= 6 and not re.search(r"(?i)(readme|example|doc)", value)


def _redact(value: str) -> str:
    return f"{value[:4]}…{value[-2:]}（{len(value)} 位，已脱敏）" if len(value) > 8 else f"…（{len(value)} 位）"


def _iter_archive(path: Path):
    """Yield (member_name, text) for every text-ish file inside an archive."""
    if path.suffix == ".whl" or path.name.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                yield name, z.read(name)
    elif path.name.endswith((".tar.gz", ".tgz")):
        with tarfile.open(path) as t:
            for m in t.getmembers():
                if not m.isfile():
                    continue
                handle = t.extractfile(m)
                if handle is not None:
                    yield m.name, handle.read()
    else:
        yield None, path.read_bytes()


def scan_blob(blob: bytes, where: str) -> list[str]:
    findings: list[str] = []
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError:
        if b"-----BEGIN" in blob:
            findings.append(f"{where}: 二进制中含私钥块")
        return findings

    def _allowed(line: str) -> bool:
        """Honour the ``allowlist secret`` marker used to exempt detection patterns."""
        return ALLOW_MARKER.search(line) is not None

    lines = text.splitlines()

    def _line_at(pos: int) -> tuple[int, str]:
        no = text.count("\n", 0, pos) + 1
        return no, (lines[no - 1] if no - 1 < len(lines) else "")

    for m in SECRET_KEYS.finditer(text):
        name, value = m.group(1), m.group(2)
        line_no, line_text = _line_at(m.start())
        if _allowed(line_text):
            continue
        if _entropy_ok(value):
            findings.append(f"{where}:{line_no}: {name} = {_redact(value)}")

    for label, pat in TOKEN_PATTERNS:
        for m in pat.finditer(text):
            value = m.group(0)
            line_no, line_text = _line_at(m.start())
            if _allowed(line_text):
                continue
            if _entropy_ok(value) or "PRIVATE KEY" in value:
                findings.append(f"{where}:{line_no}: {label} → {_redact(value)}")

    return findings


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, text=True, check=True
    ).stdout
    return [Path(p) for p in out.split("\0") if p]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="files / archives / globs to scan")
    ap.add_argument("--tracked", action="store_true", help="scan git-tracked files")
    ap.add_argument("--configure-hooks", action="store_true", help="install git hooks")
    args = ap.parse_args(argv)

    targets: list[Path] = [Path(p) for p in args.paths]
    if args.tracked:
        targets += tracked_files()
    if not targets:
        targets = sorted(Path("dist").glob("*"))

    findings: list[str] = []
    scanned = 0
    for t in targets:
        if not t.exists():
            findings.append(f"{t}: 路径不存在")
            continue
        if t.is_dir():
            for sub in sorted(t.rglob("*")):
                if sub.is_file():
                    scanned += 1
                    findings += scan_blob(sub.read_bytes(), str(sub))
            continue
        scanned += 1
        for member, blob in _iter_archive(t):
            where = str(t) if member is None else f"{t}::{member}"
            findings += scan_blob(blob, where)

    if args.configure_hooks:
        hooks = Path(__file__).resolve().parent.parent / ".git" / "hooks"
        for hook, extra in (("pre-commit", "--tracked"), ("pre-push", "dist/*")):
            f = hooks / hook
            f.write_text(
                "#!/bin/sh\n"
                "# Generated by scripts/check_secrets.py --configure-hooks\n"
                f'python3 "$(dirname "$0")/../../scripts/check_secrets.py" {extra} || exit 1\n',
                encoding="utf-8",
            )
            f.chmod(0o755)
        print("已安装 git hooks: pre-commit(--tracked), pre-push(dist/*)")

    print(f"扫描 {scanned} 个目标")
    if findings:
        print(f"✘ 发现 {len(findings)} 处疑似密钥：")
        for f in dict.fromkeys(findings):  # 去重保序
            print("   -", f)
        return 1
    print("✔ 未发现密钥")
    return 0


if __name__ == "__main__":
    sys.exit(main())
