#!/usr/bin/env python
"""发布脚本 - 自动更新版本号并上传到 PyPI"""

import os
import re
import subprocess
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """更新所有文件中的版本号"""

    files = {
        "pyproject.toml": [
            (r'version\s*=\s*"[^"]*"', f'version = "{new_version}"')
        ],
        "src/cdisc_mcp/__init__.py": [
            (r'__version__\s*=\s*"[^"]*"', f'__version__ = "{new_version}"')
        ],
        "src/cdisc_mcp/server.py": [
            (r'version\s*=\s*"[^"]*"', f'version = "{new_version}"')
        ],
    }

    for file_path, patterns in files.items():
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue

        content = path.read_text(encoding="utf-8")
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        path.write_text(content, encoding="utf-8")
        print(f"✅ 更新: {file_path} -> {new_version}")


def build_package() -> None:
    """构建包"""
    print("\n📦 构建包...")
    # 清理旧构建
    dist_path = Path("dist")
    if dist_path.exists():
        import shutil
        shutil.rmtree(dist_path)

    subprocess.run([sys.executable, "-m", "build"], check=True)
    print("✅ 构建完成")


def upload_to_pypi(token: str = None) -> None:
    """上传到 PyPI"""
    print("\n📤 上传到 PyPI...")

    env = os.environ.copy()
    if token:
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = token

    result = subprocess.run(
        ["twine", "upload", "dist/*"],
        env=env,
        check=True
    )
    print("✅ 上传完成")


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/release.py <新版本号> [TOKEN]")
        print("")
        print("示例:")
        print("  python scripts/release.py 0.1.2                          # 从环境变量读取 TOKEN")
        print("  python scripts/release.py 0.1.2 pypi-xxx...              # 直接传 TOKEN")
        print("  PYPI_TOKEN=pypi-xxx... python scripts/release.py 0.1.2   # 环境变量方式")
        sys.exit(1)

    new_version = sys.argv[1]

    # 验证版本号格式
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print(f"❌ 无效版本号: {new_version}")
        print("   格式应为: X.Y.Z (如 0.1.2)")
        sys.exit(1)

    # 获取 TOKEN（优先级：参数 > 环境变量）
    token = None
    if len(sys.argv) >= 3:
        token = sys.argv[2]
    elif os.environ.get("PYPI_TOKEN"):
        token = os.environ["PYPI_TOKEN"]
    elif os.environ.get("TWINE_PASSWORD"):
        # 已有 TWINE_PASSWORD 环境变量
        pass
    else:
        print("⚠️  未检测到 PyPI Token，上传时需要手动输入")
        print("   建议：设置环境变量 PYPI_TOKEN 或作为参数传入")

    print(f"🚀 准备发布版本: {new_version}")
    print("-" * 40)

    update_version(new_version)
    build_package()
    upload_to_pypi(token)

    print("-" * 40)
    print(f"✅ cdisc-library-mcp v{new_version} 已发布到 PyPI")
    print(f"🔗 https://pypi.org/project/cdisc-library-mcp/{new_version}/")


if __name__ == "__main__":
    main()