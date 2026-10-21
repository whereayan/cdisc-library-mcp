"""Repo-hygiene tests: keep credentials out of git and out of the distribution.

Background: an early release's sdist swept in a local client config file that
held an API key. These tests fail loudly if a secret-shaped value comes back,
if such a config becomes tracked again, or if the sdist whitelist is loosened
by accident. Credentials belong in environment variables or ~/.cdisc-mcp/.env.
"""

import importlib.util
import re
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

ALLOW_PLACEHOLDER = re.compile(
    r"(?i)your[-_]?api[-_]?key[-_]?here|REPLACE[_-]?ME|changeme|^\s*$"
)


def _load_scanner():
    path = ROOT / "scripts" / "check_secrets.py"
    spec = importlib.util.spec_from_file_location("check_secrets", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pytest.skip("git unavailable or not a checkout")
    return [p for p in out.split("\0") if p]


class TestTrackedFiles:
    def test_no_client_config_with_credentials_is_tracked(self):
        """Client MCP configs must stay untracked (they can hold real keys)."""
        tracked = set(_git_files())
        for path in (".roo/mcp.json", ".claude/settings.local.json"):
            assert path not in tracked, f"{path} 被 git 跟踪，可能带上凭据"

    def test_tracked_text_files_have_no_secret_shapes(self):
        """Delegate to the pre-publish scanner: one rule set, not two.

        Re-implementing the patterns here would let the gate and the test drift
        apart (and would not honour the ``allowlist secret`` marker).
        """
        gate = _load_scanner()
        offenders = []
        for rel in _git_files():
            p = ROOT / rel
            if p.is_file():
                offenders += gate.scan_blob(p.read_bytes(), rel)
        assert not offenders, "跟踪文件中出现疑似密钥：" + "; ".join(offenders)

    def test_env_is_ignored(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".env" in gitignore
        assert ".roo/mcp.json" in gitignore


class TestSdistWhitelist:
    # A leading-dot entry is only acceptable when it is a placeholder example.
    ALLOWED_DOT_ENTRIES = {".env.example"}

    def test_sdist_uses_only_include_whitelist(self):
        cfg = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        sdist = cfg["tool"]["hatch"]["build"]["targets"].get("sdist", {})
        only = sdist.get("only-include")
        assert only, "sdist 必须使用白名单，不能靠默认规则扫全仓库"
        assert "src/cdisc_mcp" in only
        unexpected_dot = [seg for seg in only if seg.startswith(".") and seg not in self.ALLOWED_DOT_ENTRIES]
        assert not unexpected_dot, unexpected_dot

    @pytest.mark.parametrize("dot", [".roo", ".roo/mcp.json", ".claude", ".env"])
    def test_forbidden_paths_are_not_whitelisted(self, dot):
        cfg = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        only = cfg["tool"]["hatch"]["build"]["targets"]["sdist"]["only-include"]
        assert dot not in only, f"{dot} 不得进入发布产物白名单"

    def test_dot_env_example_holds_only_placeholders(self):
        """Secret-looking keys in the template must carry placeholders only.

        Non-secret defaults (base URL, cache dir, TTL) are fine to ship.
        """
        secret_key = re.compile(r"(?i)(api[-_]?key|token|secret|password|credential)")
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        for line in text.splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            name, value = line.split("=", 1)
            if not secret_key.search(name):
                continue
            assert ALLOW_PLACEHOLDER.search(value.strip()), f".env.example 含真实凭据: {line}"


class TestSecretGate:
    """The pre-publish scanner must catch live-looking keys and ignore placeholders.

    Detection patterns themselves are exempted via the ``allowlist secret``
    trailing comment, which the scanner honours (see ALLOW_MARKER).
    """

    def test_flags_a_real_looking_key(self):
        gate = _load_scanner()
        # Built at runtime so this file does not itself contain a 32-hex literal.
        fake_key = "0123456789abcdef" * 2
        blob = f'{{"env": {{"CDISC_API_KEY": "{fake_key}"}}}}'.encode()
        findings = gate.scan_blob(blob, "x.json")
        assert findings, "扫描器漏掉了明显的密钥"
        assert "0123…ef" in findings[0], findings[0]  # 输出必须已脱敏
        assert fake_key not in findings[0]

    def test_ignores_placeholders_and_docs(self):
        gate = _load_scanner()
        ok = [
            b'{"CDISC_API_KEY": "your-api-key-here"}',
            b'{"CDISC_API_KEY": "${CDISC_API_KEY}"}',
            b'{"CDISC_API_KEY": "REPLACE_ME"}',
            b"CDISC_API_KEY=\n",
            b"# version 0.1.4 released 2026-04-08",
        ]
        for blob in ok:
            assert gate.scan_blob(blob, "x") == [], blob

    def test_flags_github_and_private_key_shapes(self):
        gate = _load_scanner()
        assert gate.scan_blob(b"token: ghp_Ab1Cd2Ef3Gh4Ij5Kl6Mn7Op8Qr", "x")  # allowlist secret
        assert gate.scan_blob(b"-----BEGIN RSA PRIVATE KEY-----\nAAAA", "x")  # allowlist secret

    def test_allowlist_marker_exempts_only_the_marked_line(self):
        gate = _load_scanner()
        half = "0123456789abcdef"
        key_line = '{"CDISC_API_KEY": "' + half + half + '"}'
        assert len(gate.scan_blob(key_line.encode(), "x")) >= 1, "未标记时应命中"
        assert gate.scan_blob((key_line + "  # allowlist secret").encode(), "x") == [], "标记行应豁免"
