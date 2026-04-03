# CDISC Library MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP Server for CDISC Library API - 提供对临床数据标准的完整访问。

## 功能特性

- 🔧 **约 20 个 MCP Tools** - 覆盖 SDTM, ADaM, CDASH, CT 等标准
- 📦 **MCP Resources** - 产品列表、API 信息
- 💬 **MCP Prompts** - 引导式标准探索
- 🗄️ **持久化缓存** - 减少 API 调用，加速访问
- 🇨🇳 **中文错误提示** - 友好的错误消息

## 安装

```bash
pip install cdisc-library-mcp
```

## 配置

### 1. 获取 API Key

1. 访问 [CDISC Library API Portal](https://api.developer.library.cdisc.org/)
2. 登录或注册 CDISC 账号
3. 在 [Profile 页面](https://api.developer.library.cdisc.org/profile) 获取 API Key

### 2. MCP 配置

在 Claude Desktop 或其他 MCP 客户端中添加配置：

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "python",
      "args": ["-m", "cdisc_mcp.server"],
      "env": {
        "CDISC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 可用工具

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
| `get_dataset` | 获取数据集详情 |
| `get_dataset_variables` | 获取变量列表 |
| `get_variable` | 获取变量详情 |

### 控制术语
| 工具 | 描述 |
|------|------|
| `get_ct_packages` | 获取 CT 包列表 |
| `get_ct_package` | 获取 CT 包详情 |
| `get_codelists` | 获取编码列表 |
| `get_codelist` | 获取编码详情 |
| `get_codelist_terms` | 获取术语列表 |

### 搜索与比较
| 工具 | 描述 |
|------|------|
| `search` | 全局搜索 CDISC Library |
| `search_suggest` | 获取搜索建议 |
| `compare_versions` | 版本差异比较 |

## 版本号格式

CDISC Library API 使用 `-` 分隔版本号：

| 标准 | 正确格式 | 错误格式 |
|------|----------|----------|
| SDTM | `1-8`, `2-0` | `1.8`, `2.0` |
| SDTMIG | `3-4`, `3-3` | `3.4`, `3.3` |

工具会自动转换格式，支持两种输入。

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `CDISC_API_KEY` | ✅ | - | API 密钥 |
| `CDISC_BASE_URL` | ❌ | `https://library.cdisc.org/api` | API URL |
| `CDISC_CACHE_DIR` | ❌ | `~/.cdisc-mcp/cache` | 缓存目录 |
| `CDISC_CACHE_TTL` | ❌ | `86400` | 缓存时间（秒） |

## 开发

```bash
# 克隆仓库
git clone https://github.com/your-org/cdisc-library-mcp.git
cd cdisc-library-mcp

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest tests/ -v

# 运行测试覆盖率
python -m pytest tests/ --cov=src/cdisc_mcp
```

## 许可证

MIT License