# 发布指南

本文档说明如何将 cdisc-library-mcp 发布到 PyPI 供他人使用。

## 发布前准备

### 1. 检查必要文件

确保以下文件存在：

| 文件 | 状态 | 说明 |
|------|------|------|
| `pyproject.toml` | ✅ | 包配置 |
| `README.md` | ✅ | 项目说明 |
| `LICENSE` | ✅ | MIT 许可证 |
| `src/cdisc_mcp/__init__.py` | ✅ | 包入口 |
| `.gitignore` | ✅ | 已排除敏感文件 |

### 2. 更新 pyproject.toml

将 GitHub URL 更改为你的实际仓库地址：

```toml
[project.urls]
Homepage = "https://github.com/你的用户名/cdisc-library-mcp"
Documentation = "https://github.com/你的用户名/cdisc-library-mcp#readme"
Repository = "https://github.com/你的用户名/cdisc-library-mcp"
```

### 3. 更新 README.md

将安装说明中的仓库地址更新：

```markdown
git clone https://github.com/你的用户名/cdisc-library-mcp.git
```

## 发布步骤

> **0.1.5 起统一使用 `scripts/release.py`，它把所有闸门串成一条命令。**
> 手动步骤（下方「闸门清单」）保留作故障排查参考；不要绕过密钥扫描直接 `twine upload`。
> 教训：0.1.4 的 sdist 把 `.roo/mcp.json` 连同**真实 CDISC_API_KEY** 一起发上了 PyPI。

### 一条命令发布

```bash
# 1) 演练：跑完所有闸门但不上传
python scripts/release.py 0.1.5

# 2) 正式：凭据只从环境变量给（绝不作为命令行参数）
export TWINE_PASSWORD=pypi-AgE...    # PyPI API Token
python scripts/release.py 0.1.5 --upload

# 3) 先在测试库验证产物
python scripts/release.py 0.1.5 --upload --repo testpypi
```

脚本会依次执行：版本一致性 → PyPI 版本未被占用 → 跟踪文件密钥扫描 → pytest → 构建 →
sdist 内容核对 → 产物密钥扫描 → `twine check` → 上传。任一闸门不过即中止。

### 闸门清单（手动等价步骤 / 排查用）

```bash
python scripts/check_secrets.py --tracked      # 仓库里不得有凭据
tests: python -m pytest -q                      # 含 tests/test_repo_hygiene.py
uv build || python -m build                     # 产出 dist/*.whl + *.tar.gz
tar -tzf dist/cdisc_library_mcp-<V>.tar.gz       # 不得出现 .roo/ .claude/ .env
python scripts/check_secrets.py dist/*.whl dist/*.tar.gz
python -m twine check dist/*.whl dist/*.tar.gz   # twine 需 >= 7.0
twine upload dist/*.whl dist/*.tar.gz
```

### 方式一：发布到 PyPI

#### 步骤 1: 安装发布工具

```bash
pip install build "twine>=7" uv
```

> `twine < 7` 会把 wheel 的 `Metadata-Version: 2.5` 误判为非法而报
> `Invalid distribution metadata`，并非包本身有问题。

#### 步骤 2: 构建 Python 包

```bash
uv build          # 或 python -m build
```

这将在 `dist/` 目录生成（版本号取自 `src/cdisc_mcp/version.py`）：
- `cdisc_library_mcp-<版本>.tar.gz` (源码包)
- `cdisc_library_mcp-<版本>-py3-none-any.whl` (wheel 包)

sdist 内容由 `pyproject.toml` 的 `[tool.hatch.build.targets.sdist] only-include`
**白名单**决定。要发布新文件必须显式加入白名单——这是防止本地配置/凭据被顺手打包的关键。

#### 步骤 3: 检查包内容

```bash
python scripts/check_secrets.py dist/*     # 密钥闸门
twine check dist/*.whl dist/*.tar.gz
```

#### 步骤 4: 上传到 PyPI

**首次发布需要 PyPI 账号：**

1. 注册 PyPI 账号: https://pypi.org/account/register/
2. 创建 API Token: https://pypi.org/manage/account/token/

```bash
twine upload dist/*
```

输入用户名和密码（或使用 API Token）。

#### 步骤 5: 验证发布

发布后，用户可以这样安装：

```bash
pip install cdisc-library-mcp
```

---

### 方式二：发布到 TestPyPI（测试）

先在 TestPyPI 测试发布流程：

```bash
# 注册 TestPyPI 账号: https://test.pypi.org/account/register/

# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ cdisc-library-mcp
```

---

### 方式三：GitHub 直接安装

无需发布到 PyPI，用户可以直接从 GitHub 安装：

```bash
pip install git+https://github.com/你的用户名/cdisc-library-mcp.git
```

或者指定版本/分支：

```bash
pip install git+https://github.com/你的用户名/cdisc-library-mcp.git@v0.1.0
pip install git+https://github.com/你的用户名/cdisc-library-mcp.git@main
```

---

### 方式四：注册到 MCP 官方目录

Anthropic 维护官方 MCP 服务器目录：

**仓库：** https://github.com/modelcontextprotocol/servers

**提交步骤：**

1. Fork 该仓库
2. 在 `servers/` 目录创建新文件夹，如 `servers/cdisc-library/`
3. 添加 `README.md` 描述你的 MCP
4. 提交 PR

---

## 用户使用方式

发布后，用户可以这样配置 MCP：

### Claude Desktop 配置

在 Claude Desktop 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "python",
      "args": ["-m", "cdisc_mcp.server"],
      "env": {
        "CDISC_API_KEY": "用户的API密钥"
      }
    }
  }
}
```

**配置文件位置：**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### 其他 MCP 客户端

支持 MCP 协议的其他客户端（如 Cursor、Windsurf 等）配置方式类似。

---

## 版本更新流程

更新版本时：

1. 更新 `pyproject.toml` 中的 `version`
2. 更新 `src/cdisc_mcp/__init__.py` 中的 `__version__`
3. 更新 `README.md` 中的变更说明
4. 构建新版本：`python -m build`
5. 上传：`twine upload dist/*`

---

## 安全注意事项

⚠️ **绝对不要提交以下内容：**

- `.env` - 包含 API 密钥
- `.mcp.json` - 包含 API 密钥
- `*.egg-info/` - 构建临时文件
- `__pycache__/` - Python 缓存
- `dist/` - 发布包（发布后可删除）

✅ `.gitignore` 已正确配置，排除了这些文件。

---

## 发布检查清单

发布前确认：

- [ ] 更新了 GitHub URL
- [ ] 运行了所有测试：`python -m pytest tests/ -v`
- [ ] 检查了版本号一致性
- [ ] 确认 .gitignore 排除了敏感文件
- [ ] 确认没有提交 API 密钥
- [ ] README.md 说明完整
- [ ] LICENSE 文件存在