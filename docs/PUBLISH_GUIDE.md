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

### 方式一：发布到 PyPI

#### 步骤 1: 安装发布工具

```bash
pip install build twine
```

#### 步骤 2: 构建 Python 包

```bash
cd D:/AI_PROJECT/cdisc-library-mcp
python -m build
```

这将在 `dist/` 目录生成：
- `cdisc_library_mcp-0.1.0.tar.gz` (源码包)
- `cdisc_library_mcp-0.1.0-py3-none-any.whl` (wheel 包)

#### 步骤 3: 检查包内容

```bash
twine check dist/*
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