# CDISC Library MCP Server 设计文档

> **版本**: 1.0.0
> **日期**: 2026-04-03
> **作者**: Claude (Anya persona)
> **状态**: 已批准

---

## 1. 概述

### 1.1 项目目标

创建一个 MCP (Model Context Protocol) Server，提供对 CDISC Library API 的完整访问能力，支持临床数据标准的查询和操作。

### 1.2 范围

- 提供约 25 个核心 MCP Tools，通过统一接口覆盖 163 个 CDISC Library API 操作
- 提供友好的中文错误提示
- 支持持久化缓存加速访问
- 遵循 MCP 最佳实践（Resources + Tools + Prompts）

**设计策略**：由于 163 个 API 操作数量过多，采用"统一入口"模式，将相似操作归类到同一工具中，通过参数区分具体操作。例如：
- `get_dataset` 工具通过 `standard` 参数支持 SDTM/SDTMIG/ADaM/SENDIG 等多个标准
- `get_codelist` 工具通过 `package` 参数支持所有 CT 包

### 1.3 目标用户

- 临床数据程序员
- 数据标准管理人员
- CDISC 标准研究人员
- AI 辅助编程用户

---

## 2. 技术选型

### 2.1 技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.10+ | 数据处理生态丰富，MCP SDK 支持好 |
| MCP SDK | mcp | 官方 Python SDK |
| HTTP 客户端 | httpx | 异步支持，现代化 API |
| 数据验证 | pydantic | 类型安全，自动校验 |
| 缓存 | 文件系统 | 简单可靠，无需额外依赖 |
| 测试 | pytest | Python 标准测试框架 |

### 2.2 依赖项

```
mcp>=0.9.0           # MCP Python SDK (参考 PyPI 实际版本)
httpx>=0.25.0        # 异步 HTTP 客户端
pydantic>=2.0.0      # 数据验证
pytest>=7.0.0        # 测试框架
pytest-asyncio>=0.21.0  # 异步测试支持
```

> **注意**: MCP SDK 版本号以 PyPI 发布为准，详见 https://pypi.org/project/mcp/

---

## 3. 架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client (Claude)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  MCP Server (cdisc-mcp)                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Resources  │  │    Tools    │  │   Prompts   │     │
│  │   (9个)     │  │   (~20个)   │  │    (5个)    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │              Cache Manager                       │   │
│  │         (~/.cdisc-mcp/cache/)                    │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │              CDISC API Client                    │   │
│  │         (https://library.cdisc.org/api)          │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 项目结构

```
cdisc-library-mcp/
├── src/
│   └── cdisc_mcp/
│       ├── __init__.py
│       ├── server.py           # MCP Server 入口
│       ├── config.py           # 配置管理
│       ├── cache.py            # 持久化缓存
│       ├── client.py           # CDISC API 客户端
│       ├── resources/          # MCP Resources
│       │   ├── __init__.py
│       │   ├── products.py     # 产品列表资源
│       │   ├── standards.py    # 标准版本资源
│       │   └── terminology.py  # 术语包资源
│       ├── tools/              # MCP Tools
│       │   ├── __init__.py
│       │   ├── standard.py     # 获取标准数据
│       │   ├── dataset.py      # 数据集操作
│       │   ├── variable.py     # 变量操作
│       │   ├── codelist.py     # 控制术语操作
│       │   ├── search.py       # 搜索功能
│       │   └── compare.py      # 版本比较
│       ├── prompts/            # MCP Prompts
│       │   ├── __init__.py
│       │   └── templates.py    # 提示模板
│       └── utils/
│           ├── __init__.py
│           └── errors.py       # 错误处理
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_tools.py
│   └── test_cache.py
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-04-03-cdisc-library-mcp-design.md
├── pyproject.toml
├── README.md
└── CDISC_Library_API_Documentation.md
```

---

## 4. 模块设计

### 4.1 配置管理 (config.py)

```python
from pydantic import BaseModel
import os

class CDISCConfig(BaseModel):
    """CDISC MCP 配置"""
    api_key: str                    # API 密钥（必需）
    base_url: str = "https://library.cdisc.org/api"
    cache_dir: str = "~/.cdisc-mcp/cache"
    cache_ttl: int = 86400          # 默认缓存 24 小时
    request_timeout: int = 30       # 请求超时秒数
    max_retries: int = 3            # 最大重试次数
    retry_delay: float = 1.0        # 重试初始延迟（秒）
    retry_backoff: float = 2.0      # 重试退避因子
    
    @classmethod
    def from_env(cls) -> "CDISCConfig":
        """从环境变量加载配置"""
        return cls(
            api_key=os.environ.get("CDISC_API_KEY", ""),
            base_url=os.environ.get("CDISC_BASE_URL", cls.model_fields["base_url"].default),
            cache_dir=os.environ.get("CDISC_CACHE_DIR", cls.model_fields["cache_dir"].default),
            cache_ttl=int(os.environ.get("CDISC_CACHE_TTL", str(cls.model_fields["cache_ttl"].default))),
        )
```

### 4.2 缓存管理 (cache.py)

**缓存策略**：

| 数据类型 | 缓存时间 | 缓存键格式 |
|----------|----------|------------|
| 产品列表 | 24 小时 | `products` |
| 标准版本 | 24 小时 | `standards_{type}` |
| CT 包列表 | 24 小时 | `ct_packages` |
| 标准详情 | 7 天 | `{standard}_{version}` |
| 数据集详情 | 7 天 | `{standard}_{version}_{dataset}` |
| 变量详情 | 7 天 | `{standard}_{version}_{dataset}_{variable}` |
| 编码列表 | 7 天 | `ct_{package}_{codelist}` |

**缓存目录结构**：

```
~/.cdisc-mcp/cache/
├── products.json
├── standards/
│   ├── sdtm_1-8.json
│   └── sdtmig_3-4.json
├── datasets/
│   └── sdtmig_3-4_DM.json
├── codelists/
│   └── p60_C667.json
└── metadata.json
```

**核心实现**：

```python
class CacheManager:
    """持久化缓存管理器"""
    
    def __init__(self, cache_dir: str, default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.metadata_file = self.cache_dir / "metadata.json"
    
    def get(self, key: str) -> Optional[dict]:
        """获取缓存数据，如果过期或不存在返回 None"""
        
    def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        """设置缓存数据"""
        
    def delete(self, key: str) -> None:
        """删除缓存数据"""
        
    def clear_expired(self) -> int:
        """清理过期缓存，返回清理数量"""
```

### 4.3 API 客户端 (client.py)

**核心功能**：
- 封装所有 163 个 API 调用
- 处理认证（Bearer Token）
- 统一错误处理
- 支持缓存集成

**API 分组**：

| 分组 | 端点前缀 | 工具数量 |
|------|----------|----------|
| QRS | `/mdr/qrs/` | 6 |
| Diff | `/mdr/diff/` | 2 |
| CDASH | `/mdr/cdash/` | 9 |
| CDASHIG | `/mdr/cdashig/` | 13 |
| ADaM | `/mdr/adam/` | 7 |
| SDTM | `/mdr/sdtm/` | 10 |
| SDTMIG | `/mdr/sdtmig/` | 8 |
| SENDIG | `/mdr/sendig/` | 8 |
| CT | `/mdr/ct/` | 6 |
| Integrated | `/mdr/integrated/` | 38 |
| Rules | `/mdr/rules/` | 3 |
| Documents | `/mdr/documents/` | 13 |
| Search | `/mdr/search/` | 5 |
| Products | `/mdr/products/` | 2 |
| Root | `/mdr/root/` | 14 |
| BC v1 | `/packages/` | 3 |
| BC v2 | `/packages/`, `/biomedicalconcepts/` | 6 |
| DS v1 | `/packages/` | 3 |
| DS v2 | `/sdtm/packages/`, `/datasetspecializations/` | 7 |

**核心方法签名**：

```python
class CDISCClient:
    async def get_products(self) -> dict:
        """获取产品列表"""
        
    async def get_standard(self, standard: str, version: str) -> dict:
        """获取标准详情"""
        
    async def get_classes(self, standard: str, version: str) -> dict:
        """获取类列表"""
        
    async def get_datasets(self, standard: str, version: str) -> dict:
        """获取数据集列表"""
        
    async def get_dataset(self, standard: str, version: str, dataset: str) -> dict:
        """获取数据集详情"""
        
    async def get_variable(self, standard: str, version: str, dataset: str, variable: str) -> dict:
        """获取变量详情"""
        
    async def get_ct_packages(self) -> dict:
        """获取 CT 包列表"""
        
    async def get_codelist(self, package: str, codelist: str) -> dict:
        """获取编码列表详情"""
        
    async def get_codelist_terms(self, package: str, codelist: str) -> dict:
        """获取编码术语列表"""
        
    async def search(self, query: str, scope: Optional[str] = None) -> dict:
        """全局搜索"""
        
    async def compare_versions(self, product: str, version: str, previous: str) -> dict:
        """版本差异比较"""
```

### 4.4 错误处理 (utils/errors.py)

**错误类型层次**：

```
CDISCError (基类)
├── AuthenticationError    # 认证错误 (401, 403)
├── ResourceNotFoundError  # 资源不存在 (404)
├── NetworkError          # 网络/服务错误 (500-503, Timeout)
├── ValidationError       # 参数验证错误
└── RateLimitError        # 频率限制 (429)
```

**错误响应格式**：

```json
{
  "friendly_message": "🔑 API Key 无效或已过期，请检查配置中的 CDISC_API_KEY",
  "original_error": "HTTPStatusError: 401 Unauthorized",
  "details": {
    "status_code": 401,
    "hint": "可在 https://api.developer.library.cdisc.org/profile 获取 API Key"
  }
}
```

### 4.5 MCP Server 入口 (server.py)

```python
# server.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import CDISCConfig
from .client import CDISCClient
from .cache import CacheManager
from .resources import register_resources
from .tools import register_tools
from .prompts import register_prompts

class CDISCMCPServer:
    """CDISC Library MCP Server"""
    
    def __init__(self, config: CDISCConfig):
        self.config = config
        self.cache = CacheManager(config.cache_dir, config.cache_ttl)
        self.client = CDISCClient(config, self.cache)
        self.server = Server("cdisc-library-mcp")
        
    async def setup(self):
        """注册 MCP 组件"""
        await register_resources(self.server, self.client)
        await register_tools(self.server, self.client)
        await register_prompts(self.server)
    
    async def run(self):
        """启动服务器"""
        await self.setup()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)

async def main():
    config = CDISCConfig.from_env()
    server = CDISCMCPServer(config)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. MCP 接口设计

### 5.1 Resources

| URI | 描述 | 数据来源 |
|-----|------|----------|
| `cdisc://products` | 所有产品列表 | `/mdr/products` |
| `cdisc://products/{group}` | 按分组的产品列表 | `/mdr/products/{group}` |
| `cdisc://standards/sdtm/versions` | SDTM 可用版本 | 解析 products |
| `cdisc://standards/sdtmig/versions` | SDTMIG 可用版本 | 解析 products |
| `cdisc://standards/adam/versions` | ADaM 可用版本 | 解析 products |
| `cdisc://standards/cdash/versions` | CDASH 可用版本 | 解析 products |
| `cdisc://ct/packages` | CT 包列表 | `/mdr/ct/packages` |
| `cdisc://bc/categories` | BC 分类列表 | `/categories` |
| `cdisc://about` | API 信息 | `/mdr/about` |

**Resource 示例**：

```json
// cdisc://products
{
  "products": [
    {
      "name": "SDTM",
      "href": "sdtm",
      "versions": ["1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "2-0"]
    },
    {
      "name": "SDTMIG", 
      "href": "sdtmig",
      "versions": ["3-1-2", "3-1-3", "3-2", "3-3", "3-4"]
    }
  ]
}
```

### 5.2 Tools

#### 标准查询工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `get_standard` | 获取标准产品信息 | `standard: str`, `version: str` |
| `get_classes` | 获取标准类列表 | `standard: str`, `version: str` |
| `get_class` | 获取类详情 | `standard: str`, `version: str`, `class_name: str` |

#### 数据集/域工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `get_datasets` | 获取数据集列表 | `standard: str`, `version: str` |
| `get_dataset` | 获取数据集详情 | `standard: str`, `version: str`, `dataset: str` |
| `get_dataset_variables` | 获取数据集变量列表 | `standard: str`, `version: str`, `dataset: str` |
| `get_variable` | 获取变量详情 | `standard: str`, `version: str`, `dataset: str`, `variable: str` |

#### 控制术语工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `get_ct_packages` | 获取 CT 包列表 | - |
| `get_ct_package` | 获取 CT 包详情 | `package: str` |
| `get_codelists` | 获取编码列表 | `package: str` |
| `get_codelist` | 获取编码详情 | `package: str`, `codelist: str` |
| `get_codelist_terms` | 获取编码术语列表 | `package: str`, `codelist: str` |
| `get_term` | 获取术语详情 | `package: str`, `codelist: str`, `term: str` |

#### 生物医学概念工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `get_bc_packages` | 获取 BC 包列表 | - |
| `get_biomedical_concepts` | 获取 BC 列表 | `package: Optional[str]` |
| `get_biomedical_concept` | 获取 BC 详情 | `bc_id: str`, `package: Optional[str]` |
| `get_bc_categories` | 获取 BC 分类列表 | - |

#### 搜索与比较工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `search` | 全局搜索 | `query: str`, `scope: Optional[str]` |
| `search_suggest` | 搜索建议 | `query: str` |
| `compare_versions` | 版本差异比较 | `product: str`, `version: str`, `previous: str` |

#### 辅助工具

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `get_about` | 获取 API 信息 | - |
| `get_maintenance_status` | 获取维护状态 | - |
| `get_last_updated` | 获取最后更新日期 | - |

**工具调用示例**：

```python
# 获取 SDTMIG 3-4 的 DM 数据集
result = await get_dataset(
    standard="sdtmig",
    version="3-4", 
    dataset="DM"
)

# 获取 CT P60 的编码列表
result = await get_codelists(package="p60")

# 搜索 adverse event
result = await search(query="adverse event")

# 比较 SDTM 1-8 和 1-7
result = await compare_versions(
    product="sdtm",
    version="1-8",
    previous="1-7"
)
```

### 5.3 Prompts

| Prompt 名称 | 描述 | 参数 |
|-------------|------|------|
| `explore_standard` | 引导用户探索某个标准 | `standard: str` |
| `find_variable` | 帮助用户查找特定变量 | `keyword: str` |
| `find_terminology` | 帮助用户查找控制术语 | `keyword: str` |
| `compare_standards` | 引导用户比较标准版本 | `standard: str` |
| `validate_dataset` | 检查数据集是否符合标准 | `standard: str`, `dataset: str` |

**Prompt 模板示例**：

```
# explore_standard

你是一个 CDISC 标准专家。帮助用户探索 {standard} 标准。

步骤：
1. 首先使用 get_standard 获取 {standard} 的基本信息
2. 使用 get_classes 或 get_datasets 获取可用类/数据集
3. 根据用户兴趣深入探索具体内容

可用的工具：
- get_standard(standard, version)
- get_classes(standard, version)
- get_datasets(standard, version)
- get_dataset(standard, version, dataset)
- get_variable(standard, version, dataset, variable)

参数说明：
- standard: {standard}
- version: 用户指定的版本，如未指定使用最新版
```

---

## 6. 配置说明

### 6.1 获取 API Key

1. 访问 [CDISC Library API Portal](https://api.developer.library.cdisc.org/)
2. 点击 "Sign in" 使用 CDISC 账号登录（或注册新账号）
3. 登录后访问 [Profile 页面](https://api.developer.library.cdisc.org/profile)
4. 在页面中找到或生成 API Key

### 6.2 MCP 配置

```json
{
  "mcpServers": {
    "cdisc-library": {
      "command": "python",
      "args": ["-m", "cdisc_mcp"],
      "env": {
        "CDISC_API_KEY": "your-api-key-here",
        "CDISC_CACHE_TTL": "86400"
      }
    }
  }
}
```

### 6.2 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `CDISC_API_KEY` | ✅ | - | CDISC Library API 密钥 |
| `CDISC_BASE_URL` | ❌ | `https://library.cdisc.org/api` | API 基础 URL |
| `CDISC_CACHE_DIR` | ❌ | `~/.cdisc-mcp/cache` | 缓存目录 |
| `CDISC_CACHE_TTL` | ❌ | `86400` | 默认缓存时间（秒） |

### 6.4 版本号格式说明

CDISC Library API 中的版本号使用 `-` 分隔，而非 `.`：

| 标准 | 正确格式 | 错误格式 |
|------|----------|----------|
| SDTM | `1-8`, `2-0` | `1.8`, `2.0` |
| SDTMIG | `3-4`, `3-3` | `3.4`, `3.3` |
| ADaM | `adamig-1-3` | `adamig-1.3` |
| CT Package | `p60`, `P60` | - (大小写不敏感) |

**工具调用时自动转换**：如果用户传入 `.` 格式，工具会自动转换为 `-` 格式。

### 6.5 速率限制

CDISC Library API 的速率限制规则：

| 限制类型 | 数值 | 说明 |
|----------|------|------|
| 每分钟请求数 | 约 60 次 | 具体以 API 返回的 `X-RateLimit-*` 头为准 |
| 每日请求数 | 无明确限制 | 建议合理使用 |

当触发速率限制时（HTTP 429），客户端会：
1. 读取 `Retry-After` 响应头
2. 等待指定时间后自动重试
3. 超过重试次数后抛出 `RateLimitError`

---

## 7. 测试策略

### 7.1 单元测试

- 测试配置加载和验证
- 测试缓存读写和过期清理
- 测试错误处理和类型转换
- 测试参数验证逻辑

### 7.2 集成测试

- 使用 mock 测试 API 调用
- 测试缓存与 API 的集成
- 测试完整的工具调用流程

### 7.3 测试覆盖率目标

- 核心模块：80%+
- 工具模块：70%+
- 整体：75%+

---

## 8. 发布计划

### 8.1 版本规划

| 版本 | 内容 | 状态 |
|------|------|------|
| v0.1.0 | 基础框架 + 核心工具 | 待开发 |
| v0.2.0 | 完整 Tools + Resources | 待开发 |
| v0.3.0 | Prompts + 文档 | 待开发 |
| v1.0.0 | 正式发布 | 待开发 |

### 8.2 发布清单

- [ ] 完成 pyproject.toml 配置
- [ ] 编写 README.md
- [ ] 添加 LICENSE
- [ ] 发布到 PyPI

---

## 9. 附录

### 9.1 参考资料

- [CDISC Library API Documentation](./CDISC_Library_API_Documentation.md)
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### 9.2 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| SDTM | Study Data Tabulation Model | 研究数据列表模型 |
| SDTMIG | SDTM Implementation Guide | SDTM 实施指南 |
| ADaM | Analysis Data Model | 分析数据模型 |
| CDASH | Clinical Data Acquisition Standards Harmonization | 临床数据采集标准协调 |
| CT | Controlled Terminology | 控制术语 |
| BC | Biomedical Concept | 生物医学概念 |
| QRS | Questionnaires, Ratings & Scales | 问卷、评分和量表 |
| SEND | Standard for Exchange of Nonclinical Data | 非临床数据交换标准 |

---

## 10. 变更历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| 1.0.0 | 2026-04-03 | Claude (Anya) | 初始版本 |
| 1.0.1 | 2026-04-03 | Claude (Anya) | 根据审查意见修复：澄清 Tools 覆盖策略、更新 MCP SDK 版本、添加重试机制、添加 server.py 示例、添加版本号格式说明、添加 API Key 获取指南 |