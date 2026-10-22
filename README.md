# CDISC Library MCP Server

[![PyPI version](https://img.shields.io/pypi/v/cdisc-library-mcp.svg)](https://pypi.org/project/cdisc-library-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP Server for CDISC Library API - 提供对临床数据标准的完整访问。

## 功能特性

- 🔧 **15 个 MCP Tools** - 覆盖 SDTM, ADaM, CDASH, CT 等标准
- 📦 **MCP Resources** - 产品列表、API 信息
- 💬 **MCP Prompts** - 引导式标准探索
- 🗄️ **持久化缓存** - 减少 API 调用，加速访问
- 🇨🇳 **中文错误提示** - 友好的错误消息

## 安装

### 方式一：uvx（推荐，自动安装）

无需手动安装，MCP 客户端会自动下载（依赖里已声明 `mcp>=1.6.0,<2.0.0`，`uvx` 会自动遵守该上界，**不需要**再手工加 `--with "mcp<2.0.0"`）：

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "uvx",
      "args": ["cdisc-library-mcp"],
      "env": {}
    }
  }
}
```

凭据推荐放在 `~/.cdisc-mcp/.env`（不要写进客户端配置）：

```ini
CDISC_API_KEY=your-api-key-here
```

如果必须内联，也可以把 `"env": {}` 换成 `{"CDISC_API_KEY": "your-api-key-here"}`。

### 方式二：pip 安装

```bash
pip install cdisc-library-mcp
```

然后在 MCP 客户端配置：

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "cdisc-library-mcp",
      "env": {
        "CDISC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 获取 API Key

1. 访问 [CDISC Library API Portal](https://api.developer.library.cdisc.org/)
2. 登录或注册 CDISC 账号
3. 在 [Profile 页面](https://api.developer.library.cdisc.org/profile) 获取 API Key

## MCP 客户端配置文件位置

| 客户端 | 配置文件路径 |
|--------|--------------|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| TRAE | 项目根目录 `.mcp.json` |

## 可用工具

### 全局约定（0.1.6+）

- **响应默认瘦身**：剥除 `_links`/`links`/`@search.*` 噪声，链接折叠为 `refs`（标签→href）；
  每个工具都有 `raw`（boolean，默认 false），传 true 拿未瘦身原始载荷。
- **`standard` 为 enum**：`sdtm, sdtmig, sendig, adam, adamig, cdash, cdashig`。
- **`version` 支持 `'latest'`**：自动解析为该产品当前最新版本。
- 所有工具均为只读 GET，带 `readOnlyHint=true` 注解。

### 标准查询
| 工具 | 描述 |
|------|------|
| `get_products` | 获取所有 CDISC 产品列表 |
| `get_standard` | 获取标准产品信息 |
| `get_classes` | 获取标准的类列表 |

### 数据集操作
| 工具 | 描述 |
|------|------|
| `get_datasets` | 获取数据集列表 |
| `get_dataset` | 获取数据集元数据（描述、所属类等） |
| `get_dataset_variables` | 获取数据集的完整变量列表（查变量首选） |
| `get_variable` | 获取变量详情 |

### 控制术语
| 工具 | 描述 |
|------|------|
| `get_ct_packages` | 获取 CT 包列表 |
| `get_ct_package` | 获取 CT 包详情 |
| `get_codelists` | 获取编码列表 |
| `get_codelist` | 获取编码详情 |
| `get_codelist_terms` | 获取术语列表 |
| `get_term` | 获取术语详情（term 支持 C 代码或术语名） |

### 搜索与比较
| 工具 | 描述 |
|------|------|
| `search` | 全局搜索 CDISC Library（支持 type 过滤、limit/offset 分页，结果缓存 24h） |
| `compare_versions` | 版本差异比较（默认摘要视图，section 下钻明细） |

## 版本号格式

CDISC Library API 使用 `-` 分隔版本号：

| 标准 | 正确格式 | 错误格式 |
|------|----------|----------|
| SDTM | `1-8`, `2-0` | `1.8`, `2.0` |
| SDTMIG | `3-4`, `3-3` | `3.4`, `3.3` |

工具会自动转换格式，支持两种输入；也可传 `latest` 自动解析为最新版本。

注意 standard 与 version 必须匹配（如 sdtmig 用 3-x，sdtm 用 1-x/2-x），拿不准时传 `latest`。

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `CDISC_API_KEY` | ✅ | - | API 密钥 |
| `CDISC_BASE_URL` | ❌ | `https://library.cdisc.org/api` | API URL |
| `CDISC_CACHE_DIR` | ❌ | `~/.cdisc-mcp/cache` | 缓存目录 |
| `CDISC_CACHE_TTL` | ❌ | `86400` | 缓存时间（秒） |

### `.env` 查找顺序

按以下顺序取**第一个自身声明了 `CDISC_*` 变量**的文件；只声明了别的项目变量的 `.env` 会被跳过（不会导入其键值）：

1. 当前工作目录 `./.env` —— stdio 启动时这是 MCP 客户端的项目目录，通常与本服务无关
2. 项目根目录 `.env`（源码安装 / `pip install -e` 场景）
3. `~/.cdisc-mcp/.env`（推荐落点，与 uvx / pip 安装方式无关）

三个都没命中时，退回真实环境变量（例如客户端注入的 `env`）；都没有则启动时打印未认证警告。

## 开发

```bash
# 克隆仓库
git clone https://github.com/whereayan/cdisc-library-mcp.git
cd cdisc-library-mcp

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest tests/ -v

# 运行测试覆盖率
python -m pytest tests/ --cov=src/cdisc_mcp
```

## 发布

```bash
# 使用发布脚本
python scripts/release.py 0.1.3

# 或手动发布
python -m build
twine upload dist/*
```

## 许可证

MIT License