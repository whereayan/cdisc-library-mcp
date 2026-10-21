#!/usr/bin/env python
"""发布脚本 — 带闸门的构建与 PyPI 上传。

用法:
    python scripts/release.py 0.1.5                 # 校验 + 测试 + 构建 + 检查，不上传
    python scripts/release.py 0.1.5 --upload        # 全流程并上传（凭据取自环境变量）
    python scripts/release.py 0.1.5 --upload --repo testpypi

设计约定（0.1.4 的教训）:
  * 版本号唯一来源是 src/cdisc_mcp/version.py；本脚本只在 --write-version 时改它，
    不再用正则去刷 pyproject.toml / server.py（那两处已改为动态版本 / 引用常量，
    旧正则会把它们写坏）。
  * 密钥扫描是硬闸门：跟踪文件与构建产物都要过，不过就停。0.1.4 的 sdist 里
    带了真实 CDISC_API_KEY（.roo/mcp.json），本脚本能拦住同类事故。
  * PyPI token 只从环境变量读取（TWINE_PASSWORD / PYPI_TOKEN），绝不接受命令行参数
    —— 命令行参数会留在 shell history 与进程列表里。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "src" / "cdisc_mcp" / "version.py"
DIST = ROOT / "dist"
MIN_TWINE = (7, 0)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(str(c) for c in cmd)}")
    return subprocess.run([str(c) for c in cmd], cwd=ROOT, check=True, **kw)


def current_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        sys.exit(f"✘ 读不到版本号：{VERSION_FILE}")
    return m.group(1)


def write_version(new_version: str) -> None:
    text = VERSION_FILE.read_text(encoding="utf-8")
    VERSION_FILE.write_text(
        re.sub(r'^__version__\s*=\s*"[^"]+"', f'__version__ = "{new_version}"', text, count=1, flags=re.M),
        encoding="utf-8",
    )
    print(f"✔ 版本号写入唯一来源: {new_version}")


def pypi_has_version(name: str, version: str, repo: str) -> bool:
    host = "test.pypi.org" if repo == "testpypi" else "pypi.org"
    url = f"https://{host}/pypi/{name}/{version}/json"
    try:
        urllib.request.urlopen(url, timeout=20)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise
    except OSError as e:  # 离线不该阻塞发布，但要让人知道没查到
        print(f"⚠ 无法确认 PyPI 是否已有 {version}（{e}），跳过该项检查")
        return False


def twine_ok() -> tuple[str, ...]:
    """Locate a twine that understands Metadata-Version 2.5 (>= 7.0)."""
    candidates = [
        (sys.executable, "-m", "twine"),
        (str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "twine"),
        (str(ROOT / ".venv" / "bin" / "python"), "-m", "twine"),
    ]
    for cand in candidates:
        try:
            out = subprocess.run([*cand, "--version"], capture_output=True, text=True).stdout
        except OSError:
            continue
        m = re.search(r"twine version (\d+)\.(\d+)\.(\d+)", out)
        if m and tuple(int(x) for x in m.groups()) >= MIN_TWINE:
            return cand
        print(f"⚠ {cand[0]} 的 twine 过旧（{m.group(0) if m else '?'}），需要 >= {'.'.join(map(str, MIN_TWINE))}")
    sys.exit(
        "✘ 没有可用的 twine>=7.0（旧版会把 Metadata-Version 2.5 误判为非法）。\n"
        f"  安装：{sys.executable} -m pip install -U twine"
    )


def gate_secret_scan(label: str, extra: list[str]) -> None:
    try:
        run([sys.executable, ROOT / "scripts" / "check_secrets.py", *extra])
    except subprocess.CalledProcessError:
        sys.exit(f"✘ {label}：发现疑似密钥，发布中止（详见上方输出）")

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("version", nargs="?", help="目标版本号 X.Y.Z；省略则用当前 version.py 的值")
    ap.add_argument("--upload", action="store_true", help="通过所有闸门后上传（凭据取环境变量）")
    ap.add_argument("--repo", default="pypi", choices=["pypi", "testpypi"])
    ap.add_argument("--write-version", action="store_true", help="把版本号写入 version.py")
    ap.add_argument("--skip-tests", action="store_true", help="仅用于紧急演练，正式发版禁止")
    args = ap.parse_args()

    version = args.version or current_version()
    if not re.fullmatch(r"\d+\.\d+\.\d+([a-b]\d+)?", version):
        sys.exit(f"✘ 无效版本号: {version}（应为 X.Y.Z，预发布 X.Y.Za1/b1）")

    if args.write_version and version != current_version():
        write_version(version)
    if version != current_version():
        sys.exit(f"✘ 目标版本 {version} 与 version.py 的 {current_version()} 不一致（加 --write-version 或改参数）")

    print("=" * 62)
    print(f"发布前闸门 — cdisc-library-mcp {version}")
    print("=" * 62)

    # 1) 目标版本未被占用，且包内版本自报一致
    import cdisc_mcp

    if cdisc_mcp.__version__ != version:
        sys.exit(f"✘ 已安装的包自报 {cdisc_mcp.__version__}，与目标 {version} 不一致（先重新安装本仓库）")
    if pypi_has_version("cdisc-library-mcp", version, args.repo):
        sys.exit(f"✘ {args.repo} 上已存在 {version}：版本号不能复用，请递增")
    print(f"✔ 包版本自报 {version}；{args.repo} 上尚未占用")

    # 2) 跟踪文件不得含密钥（0.1.4 的 .roo/mcp.json 教训）
    gate_secret_scan("跟踪文件密钥扫描", ["--tracked"])

    # 3) 测试
    if args.skip_tests:
        print("⚠ 已跳过测试（--skip-tests）")
    else:
        run([sys.executable, "-m", "pytest", "-q"])
        print("✔ 测试通过")

    # 4) 构建
    if DIST.exists():
        shutil.rmtree(DIST)
    if shutil.which("uv"):
        run(["uv", "build"])
    else:
        run([sys.executable, "-m", "build"])
    artifacts = sorted(DIST.glob("*.whl")) + sorted(DIST.glob("*.tar.gz"))
    if not artifacts:
        sys.exit("✘ 构建没有产出 wheel/sdist")
    print(f"✔ 构建产物: {[p.name for p in artifacts]}")

    # 5) 产物内容核对：客户端配置绝不许出现
    listing = subprocess.run(
        ["tar", "-tzf", str(next(DIST.glob("*.tar.gz")))], capture_output=True, text=True
    ).stdout if shutil.which("tar") else ""
    banned = [l for l in listing.splitlines() if re.search(r"/(\.roo|\.claude|\.env)$|/\.env\.local$|mcp\.json$", l) and "mcp.json.example" not in l]
    if listing and banned:
        sys.exit(f"✘ sdist 含禁止路径：{banned}")
    print("✔ sdist 未包含客户端配置")

    # 6) 产物密钥扫描
    gate_secret_scan("构建产物密钥扫描", [str(p) for p in artifacts])

    # 7) twine check（版本必须是 >=7）
    tw = twine_ok()
    run([*tw, "check", *(str(p) for p in artifacts)])
    print("✔ twine check 通过")

    print("-" * 62)
    if not args.upload:
        print("所有闸门通过。加 --upload 才会真正上传。")
        return

    token = os.environ.get("TWINE_PASSWORD") or os.environ.get("PYPI_TOKEN")
    if not token:
        sys.exit("✘ 缺少凭据：请设置 TWINE_PASSWORD 或 PYPI_TOKEN（勿用命令行参数）")
    env = dict(os.environ, TWINE_USERNAME="__token__", TWINE_PASSWORD=token)
    repo_url = "https://upload.pypi.org/legacy/" if args.repo == "pypi" else "https://test.pypi.org/legacy/"
    run([*tw, "upload", "--repository-url", repo_url, *(str(p) for p in artifacts)], env=env)
    host = "test.pypi.org" if args.repo == "testpypi" else "pypi.org"
    print(f"✔ 已发布: https://{host}/project/cdisc-library-mcp/{version}/")


if __name__ == "__main__":
    main()
