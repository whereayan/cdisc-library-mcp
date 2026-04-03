# CDISC Library MCP Server Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个完整的 CDISC Library MCP Server，提供对 CDISC Library API 的完整访问能力，支持临床数据标准的查询和操作。

**Architecture:** 采用分层架构：MCP Server 入口 -> Tools/Resources/Prompts -> API Client -> Cache -> CDISC Library API。使用统一入口模式将 163 个 API 操作归类到约 25 个 MCP Tools 中。

**Tech Stack:** Python 3.10+, mcp SDK, httpx, pydantic, pytest

---

## File Structure Map

| 文件 | 负责内容 | 创建/修改 |
|------|----------|----------|
| `pyproject.toml` | 项目配置、依赖、入口点 | 创建 |
| `src/cdisc_mcp/__init__.py` | 包初始化、版本导出 | 创建 |
| `src/cdisc_mcp/config.py` | 配置管理、环境变量加载 | 创建 |
| `src/cdisc_mcp/cache.py` | 持久化缓存管理 | 创建 |
| `src/cdisc_mcp/utils/__init__.py` | utils 包初始化 | 创建 |
| `src/cdisc_mcp/utils/errors.py` | 错误类型定义、友好错误消息 | 创建 |
| `src/cdisc_mcp/client.py` | CDISC API 客户端、163 个 API 封装 | 创建 |
| `src/cdisc_mcp/resources/__init__.py` | resources 包初始化、注册函数 | 创建 |
| `src/cdisc_mcp/resources/products.py` | 产品列表资源 | 创建 |
| `src/cdisc_mcp/resources/standards.py` | 标准版本资源 | 创建 |
| `src/cdisc_mcp/resources/terminology.py` | 术语包资源 | 创建 |
| `src/cdisc_mcp/tools/__init__.py` | tools 包初始化、注册函数 | 创建 |
| `src/cdisc_mcp/tools/standard.py` | 标准查询工具 | 创建 |
| `src/cdisc_mcp/tools/dataset.py` | 数据集/域工具 | 创建 |
| `src/cdisc_mcp/tools/variable.py` | 变量工具 | 创建 |
| `src/cdisc_mcp/tools/codelist.py` | 控制术语工具 | 创建 |
| `src/cdisc_mcp/tools/biomedical.py` | 生物医学概念工具 | 创建 |
| `src/cdisc_mcp/tools/search.py` | 搜索与比较工具 | 创建 |
| `src/cdisc_mcp/tools/auxiliary.py` | 辅助工具 | 创建 |
| `src/cdisc_mcp/prompts/__init__.py` | prompts 包初始化、注册函数 | 创建 |
| `src/cdisc_mcp/prompts/templates.py` | 提示模板定义 | 创建 |
| `src/cdisc_mcp/server.py` | MCP Server 入口 | 创建 |
| `tests/__init__.py` | 测试包初始化 | 创建 |
| `tests/test_config.py` | 配置测试 | 创建 |
| `tests/test_cache.py` | 缓存测试 | 创建 |
| `tests/test_errors.py` | 错误处理测试 | 创建 |
| `tests/test_client.py` | API 客户端测试 | 创建 |
| `tests/test_tools.py` | 工具测试 | 创建 |
| `README.md` | 项目文档 | 创建 |

---

## Chunk 1: 项目基础设施与核心模块

### Task 1: 项目配置文件

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cdisc-library-mcp"
version = "0.1.0"
description = "MCP Server for CDISC Library API - Clinical Data Standards Access"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    { name = "CDISC MCP Contributors" }
]
keywords = ["cdisc", "mcp", "clinical-data", "sdtm", "adam", "terminology"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
]

dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
cdisc-mcp = "cdisc_mcp.server:main"

[project.urls]
Homepage = "https://github.com/your-org/cdisc-library-mcp"
Documentation = "https://github.com/your-org/cdisc-library-mcp#readme"
Repository = "https://github.com/your-org/cdisc-library-mcp"

[tool.hatch.build.targets.wheel]
packages = ["src/cdisc_mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src/cdisc_mcp"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml project configuration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: 包初始化文件

**Files:**
- Create: `src/cdisc_mcp/__init__.py`
- Create: `src/cdisc_mcp/utils/__init__.py`

- [ ] **Step 1: Create src directory structure**

```bash
mkdir -p src/cdisc_mcp/utils src/cdisc_mcp/resources src/cdisc_mcp/tools src/cdisc_mcp/prompts
mkdir -p tests
```

- [ ] **Step 2: Write src/cdisc_mcp/__init__.py**

```python
"""CDISC Library MCP Server - Clinical Data Standards Access via MCP."""

__version__ = "0.1.0"
__author__ = "CDISC MCP Contributors"

from .config import CDISCConfig
from .client import CDISCClient
from .cache import CacheManager

__all__ = [
    "__version__",
    "CDISCConfig",
    "CDISCClient",
    "CacheManager",
]
```

- [ ] **Step 3: Write src/cdisc_mcp/utils/__init__.py**

```python
"""Utility modules for CDISC MCP Server."""

from .errors import (
    CDISCError,
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError,
    ValidationError,
    RateLimitError,
)

__all__ = [
    "CDISCError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "NetworkError",
    "ValidationError",
    "RateLimitError",
]
```

- [ ] **Step 4: Commit**

```bash
git add src/cdisc_mcp/__init__.py src/cdisc_mcp/utils/__init__.py
git commit -m "chore: add package initialization files

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: 配置管理模块

**Files:**
- Create: `src/cdisc_mcp/config.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing test for CDISCConfig**

```python
# tests/test_config.py
"""Tests for CDISC MCP configuration management."""

import os
import pytest
from cdisc_mcp.config import CDISCConfig


class TestCDISCConfig:
    """Test CDISCConfig class."""

    def test_config_default_values(self):
        """Test default configuration values."""
        config = CDISCConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.base_url == "https://library.cdisc.org/api"
        assert config.cache_dir == "~/.cdisc-mcp/cache"
        assert config.cache_ttl == 86400
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.retry_backoff == 2.0

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = CDISCConfig(
            api_key="custom-key",
            base_url="https://custom.url/api",
            cache_dir="/custom/cache",
            cache_ttl=3600,
            request_timeout=60,
            max_retries=5,
        )
        assert config.api_key == "custom-key"
        assert config.base_url == "https://custom.url/api"
        assert config.cache_dir == "/custom/cache"
        assert config.cache_ttl == 3600
        assert config.request_timeout == 60
        assert config.max_retries == 5

    def test_config_from_env(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ["CDISC_API_KEY"] = "env-key"
        os.environ["CDISC_BASE_URL"] = "https://env.url/api"
        os.environ["CDISC_CACHE_DIR"] = "/env/cache"
        os.environ["CDISC_CACHE_TTL"] = "7200"

        config = CDISCConfig.from_env()
        assert config.api_key == "env-key"
        assert config.base_url == "https://env.url/api"
        assert config.cache_dir == "/env/cache"
        assert config.cache_ttl == 7200

        # Clean up
        del os.environ["CDISC_API_KEY"]
        del os.environ["CDISC_BASE_URL"]
        del os.environ["CDISC_CACHE_DIR"]
        del os.environ["CDISC_CACHE_TTL"]

    def test_config_from_env_missing_key(self):
        """Test loading configuration with missing API key."""
        # Ensure CDISC_API_KEY is not set
        if "CDISC_API_KEY" in os.environ:
            del os.environ["CDISC_API_KEY"]

        config = CDISCConfig.from_env()
        assert config.api_key == ""
        assert config.base_url == "https://library.cdisc.org/api"

    def test_config_validation_empty_api_key_allowed(self):
        """Test that empty API key is allowed (for read-only operations)."""
        config = CDISCConfig(api_key="")
        assert config.api_key == ""

    def test_config_invalid_cache_ttl(self):
        """Test that invalid cache TTL raises validation error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            CDISCConfig(api_key="test", cache_ttl=-1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'cdisc_mcp'"

- [ ] **Step 3: Write src/cdisc_mcp/config.py**

```python
"""Configuration management for CDISC MCP Server."""

from pydantic import BaseModel, Field
import os
from typing import Optional


class CDISCConfig(BaseModel):
    """CDISC MCP Server configuration.
    
    Attributes:
        api_key: CDISC Library API key (required for authenticated requests)
        base_url: CDISC Library API base URL
        cache_dir: Directory for persistent cache storage
        cache_ttl: Default cache time-to-live in seconds
        request_timeout: HTTP request timeout in seconds
        max_retries: Maximum number of retry attempts for failed requests
        retry_delay: Initial retry delay in seconds
        retry_backoff: Retry delay backoff multiplier
    """
    
    api_key: str = Field(default="", description="CDISC Library API key")
    base_url: str = Field(
        default="https://library.cdisc.org/api",
        description="CDISC Library API base URL"
    )
    cache_dir: str = Field(
        default="~/.cdisc-mcp/cache",
        description="Cache directory path"
    )
    cache_ttl: int = Field(
        default=86400,
        ge=0,
        description="Default cache TTL in seconds (24 hours)"
    )
    request_timeout: int = Field(
        default=30,
        ge=1,
        description="HTTP request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        description="Initial retry delay in seconds"
    )
    retry_backoff: float = Field(
        default=2.0,
        ge=1.0,
        description="Retry backoff multiplier"
    )
    
    @classmethod
    def from_env(cls) -> "CDISCConfig":
        """Load configuration from environment variables.
        
        Environment variables:
            - CDISC_API_KEY: API key (required for authenticated access)
            - CDISC_BASE_URL: API base URL (optional)
            - CDISC_CACHE_DIR: Cache directory (optional)
            - CDISC_CACHE_TTL: Cache TTL in seconds (optional)
        
        Returns:
            CDISCConfig instance with values from environment
        """
        return cls(
            api_key=os.environ.get("CDISC_API_KEY", ""),
            base_url=os.environ.get(
                "CDISC_BASE_URL",
                cls.model_fields["base_url"].default
            ),
            cache_dir=os.environ.get(
                "CDISC_CACHE_DIR",
                cls.model_fields["cache_dir"].default
            ),
            cache_ttl=int(os.environ.get(
                "CDISC_CACHE_TTL",
                str(cls.model_fields["cache_ttl"].default)
            )),
            request_timeout=int(os.environ.get(
                "CDISC_REQUEST_TIMEOUT",
                str(cls.model_fields["request_timeout"].default)
            )),
            max_retries=int(os.environ.get(
                "CDISC_MAX_RETRIES",
                str(cls.model_fields["max_retries"].default)
            )),
        )
    
    def get_cache_path(self) -> str:
        """Get expanded cache directory path.
        
        Returns:
            Expanded cache directory path (handles ~ expansion)
        """
        return os.path.expanduser(self.cache_dir)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -v`
Expected: PASS (all 6 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cdisc_mcp/config.py tests/__init__.py tests/test_config.py
git commit -m "feat: add configuration management module with tests

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: 错误处理模块

**Files:**
- Create: `src/cdisc_mcp/utils/errors.py`
- Create: `tests/test_errors.py`

- [ ] **Step 1: Write failing test for error classes**

```python
# tests/test_errors.py
"""Tests for CDISC MCP error handling."""

import pytest
from cdisc_mcp.utils.errors import (
    CDISCError,
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError,
    ValidationError,
    RateLimitError,
)


class TestCDISCErrors:
    """Test CDISC error classes."""

    def test_base_error(self):
        """Test base CDISCError."""
        error = CDISCError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details is None

    def test_base_error_with_details(self):
        """Test base CDISCError with details."""
        details = {"status_code": 500, "url": "/mdr/sdtm/1-8"}
        error = CDISCError("API error", details=details)
        assert error.message == "API error"
        assert error.details == details

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError(
            "API Key 无效或已过期",
            status_code=401,
            hint="可在 https://api.developer.library.cdisc.org/profile 获取 API Key"
        )
        assert str(error) == "API Key 无效或已过期"
        assert error.status_code == 401
        assert "api.developer.library.cdisc.org" in error.hint
        assert isinstance(error, CDISCError)

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        error = ResourceNotFoundError(
            "未找到资源",
            resource_type="dataset",
            resource_id="DM",
            standard="sdtmig",
            version="3-4"
        )
        assert error.message == "未找到资源"
        assert error.resource_type == "dataset"
        assert error.resource_id == "DM"
        assert error.standard == "sdtmig"
        assert error.version == "3-4"

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError(
            "网络连接失败",
            status_code=503,
            original_error="ConnectionTimeout"
        )
        assert error.message == "网络连接失败"
        assert error.status_code == 503
        assert error.original_error == "ConnectionTimeout"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError(
            "参数验证失败",
            field="version",
            value="1.8",
            expected_format="1-8 (使用 - 而非 .)"
        )
        assert error.message == "参数验证失败"
        assert error.field == "version"
        assert error.value == "1.8"
        assert error.expected_format == "1-8 (使用 - 而非 .)"

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(
            "请求频率超限",
            retry_after=60
        )
        assert error.message == "请求频率超限"
        assert error.retry_after == 60

    def test_friendly_error_format(self):
        """Test friendly error JSON format."""
        error = AuthenticationError(
            "🔑 API Key 无效或已过期",
            status_code=401,
            hint="可在 https://api.developer.library.cdisc.org/profile 获取 API Key"
        )
        json_output = error.to_friendly_json()
        assert "friendly_message" in json_output
        assert "original_error" in json_output
        assert "details" in json_output
        assert json_output["details"]["status_code"] == 401
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_errors.py -v`
Expected: FAIL with "ImportError" or "ModuleNotFoundError"

- [ ] **Step 3: Write src/cdisc_mcp/utils/errors.py**

```python
"""Error handling for CDISC MCP Server.

Provides user-friendly Chinese error messages with detailed context.
"""

import json
from typing import Any, Optional


class CDISCError(Exception):
    """Base exception for CDISC MCP errors.
    
    All CDISC-specific errors inherit from this class.
    Provides friendly Chinese messages and structured error details.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_friendly_json(self) -> dict[str, Any]:
        """Convert error to friendly JSON format.
        
        Returns:
            Dict with friendly_message, original_error, and details
        """
        return {
            "friendly_message": self.message,
            "original_error": self.__class__.__name__,
            "details": self.details
        }


class AuthenticationError(CDISCError):
    """Authentication error (401, 403).
    
    Raised when API key is invalid, expired, or missing.
    """
    
    def __init__(
        self,
        message: str = "🔑 API Key 无效或已过期，请检查配置中的 CDISC_API_KEY",
        status_code: int = 401,
        hint: str = "可在 https://api.developer.library.cdisc.org/profile 获取 API Key"
    ):
        super().__init__(message, {
            "status_code": status_code,
            "hint": hint
        })
        self.status_code = status_code
        self.hint = hint


class ResourceNotFoundError(CDISCError):
    """Resource not found error (404).
    
    Raised when requested standard, dataset, variable, or codelist doesn't exist.
    """
    
    def __init__(
        self,
        message: str = "📄 未找到请求的资源",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        standard: Optional[str] = None,
        version: Optional[str] = None
    ):
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "standard": standard,
            "version": version
        }
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.standard = standard
        self.version = version


class NetworkError(CDISCError):
    """Network or service error (500-503, timeout).
    
    Raised when API server is unavailable or network issues occur.
    """
    
    def __init__(
        self,
        message: str = "🌐 网络连接失败，请稍后重试",
        status_code: Optional[int] = None,
        original_error: Optional[str] = None
    ):
        details = {
            "status_code": status_code,
            "original_error": original_error
        }
        super().__init__(message, details)
        self.status_code = status_code
        self.original_error = original_error


class ValidationError(CDISCError):
    """Parameter validation error.
    
    Raised when input parameters don't meet expected format or constraints.
    """
    
    def __init__(
        self,
        message: str = "⚠️ 参数验证失败",
        field: Optional[str] = None,
        value: Optional[str] = None,
        expected_format: Optional[str] = None
    ):
        details = {
            "field": field,
            "value": value,
            "expected_format": expected_format
        }
        super().__init__(message, details)
        self.field = field
        self.value = value
        self.expected_format = expected_format


class RateLimitError(CDISCError):
    """Rate limit exceeded error (429).
    
    Raised when API request frequency exceeds allowed limits.
    """
    
    def __init__(
        self,
        message: str = "⏳ 请求频率超限，请等待后重试",
        retry_after: Optional[int] = None
    ):
        details = {
            "retry_after": retry_after,
            "hint": f"请在 {retry_after} 秒后重试" if retry_after else "请稍后重试"
        }
        super().__init__(message, details)
        self.retry_after = retry_after


def format_http_error(status_code: int, url: str, response_text: str = "") -> CDISCError:
    """Convert HTTP status code to appropriate CDISC error.
    
    Args:
        status_code: HTTP status code
        url: Request URL
        response_text: Response body text (optional)
    
    Returns:
        Appropriate CDISCError subclass instance
    """
    if status_code in (401, 403):
        return AuthenticationError(
            status_code=status_code,
            hint=f"请求 URL: {url}"
        )
    elif status_code == 404:
        return ResourceNotFoundError(
            message=f"📄 未找到资源: {url}",
            details={"url": url, "response": response_text}
        )
    elif status_code == 429:
        return RateLimitError()
    elif status_code >= 500:
        return NetworkError(
            message=f"🌐 API 服务异常 (状态码: {status_code})",
            status_code=status_code,
            original_error=response_text
        )
    else:
        return CDISCError(
            f"请求失败 (状态码: {status_code})",
            details={"status_code": status_code, "url": url}
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_errors.py -v`
Expected: PASS (all 8 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cdisc_mcp/utils/errors.py tests/test_errors.py
git commit -m "feat: add error handling module with friendly Chinese messages

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: 缓存管理模块

**Files:**
- Create: `src/cdisc_mcp/cache.py`
- Create: `tests/test_cache.py`

- [ ] **Step 1: Write failing test for CacheManager**

```python
# tests/test_cache.py
"""Tests for CDISC MCP cache management."""

import os
import json
import time
import pytest
from pathlib import Path
from cdisc_mcp.cache import CacheManager


class TestCacheManager:
    """Test CacheManager class."""

    def test_cache_init(self, tmp_path):
        """Test cache manager initialization."""
        cache = CacheManager(str(tmp_path), default_ttl=3600)
        assert cache.cache_dir == tmp_path
        assert cache.default_ttl == 3600
        assert cache.metadata_file == tmp_path / "metadata.json"

    def test_cache_set_and_get(self, tmp_path):
        """Test setting and getting cache data."""
        cache = CacheManager(str(tmp_path))
        
        data = {"name": "SDTM", "version": "1-8"}
        cache.set("sdtm_1-8", data)
        
        result = cache.get("sdtm_1-8")
        assert result == data

    def test_cache_get_not_found(self, tmp_path):
        """Test getting non-existent cache data."""
        cache = CacheManager(str(tmp_path))
        
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_expiry(self, tmp_path):
        """Test cache expiration."""
        cache = CacheManager(str(tmp_path), default_ttl=1)  # 1 second TTL
        
        data = {"test": "data"}
        cache.set("test_key", data, ttl=1)
        
        # Should exist immediately
        result = cache.get("test_key")
        assert result == data
        
        # Wait for expiry
        time.sleep(2)
        
        # Should be expired
        result = cache.get("test_key")
        assert result is None

    def test_cache_delete(self, tmp_path):
        """Test deleting cache data."""
        cache = CacheManager(str(tmp_path))
        
        data = {"test": "data"}
        cache.set("test_key", data)
        
        # Verify it exists
        assert cache.get("test_key") == data
        
        # Delete it
        cache.delete("test_key")
        
        # Verify it's gone
        assert cache.get("test_key") is None

    def test_cache_clear_expired(self, tmp_path):
        """Test clearing expired cache entries."""
        cache = CacheManager(str(tmp_path), default_ttl=1)
        
        # Set multiple entries with different TTLs
        cache.set("short_1", {"data": 1}, ttl=1)
        cache.set("short_2", {"data": 2}, ttl=1)
        cache.set("long", {"data": 3}, ttl=3600)
        
        # Wait for short TTL entries to expire
        time.sleep(2)
        
        # Clear expired
        cleared = cache.clear_expired()
        assert cleared == 2
        
        # Long entry should still exist
        assert cache.get("long") == {"data": 3}

    def test_cache_directory_creation(self, tmp_path):
        """Test that cache directory is created if not exists."""
        cache_dir = tmp_path / "new_cache"
        cache = CacheManager(str(cache_dir))
        
        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_cache_file_structure(self, tmp_path):
        """Test cache file structure."""
        cache = CacheManager(str(tmp_path))
        
        # Set data for different categories
        cache.set("products", {"products": []})
        cache.set("standards/sdtm_1-8", {"name": "SDTM"})
        cache.set("datasets/sdtmig_3-4_DM", {"name": "DM"})
        cache.set("codelists/p60_C667", {"name": "C667"})
        
        # Verify files exist in expected locations
        assert (tmp_path / "products.json").exists()
        # Note: Nested keys may create subdirectories or flat files
        # Implementation detail to be determined

    def test_cache_metadata_tracking(self, tmp_path):
        """Test cache metadata tracking."""
        cache = CacheManager(str(tmp_path))
        
        data = {"test": "data"}
        cache.set("test_key", data, ttl=100)
        
        # Check metadata file exists
        assert cache.metadata_file.exists()
        
        # Read metadata
        with open(cache.metadata_file) as f:
            metadata = json.load(f)
        
        assert "test_key" in metadata
        assert "created_at" in metadata["test_key"]
        assert "ttl" in metadata["test_key"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cache.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'cdisc_mcp'"

- [ ] **Step 3: Write src/cdisc_mcp/cache.py**

```python
"""Persistent cache management for CDISC MCP Server.

Provides file-based caching with TTL support to reduce API calls.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """Persistent file-based cache manager.
    
    Cache directory structure:
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
    
    Metadata tracks creation time and TTL for each cache entry.
    """
    
    def __init__(self, cache_dir: str, default_ttl: int = 86400):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory path for cache storage
            default_ttl: Default time-to-live in seconds (24 hours)
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.metadata_file = self.cache_dir / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load or initialize metadata file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.metadata = {}
        else:
            self.metadata = {}
            self._save_metadata()
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get file path for cache key.
        
        Keys with "/" are stored in subdirectories.
        E.g., "standards/sdtm_1-8" -> standards/sdtm_1-8.json
        
        Args:
            key: Cache key
        
        Returns:
            Path to cache file
        """
        if "/" in key:
            parts = key.split("/")
            subdir = self.cache_dir / parts[0]
            subdir.mkdir(parents=True, exist_ok=True)
            return subdir / f"{parts[1]}.json"
        else:
            return self.cache_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached data if not expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached data dict or None if not found/expired
        """
        # Check metadata for expiry
        if key not in self.metadata:
            return None
        
        entry_meta = self.metadata[key]
        created_at = entry_meta.get("created_at", 0)
        ttl = entry_meta.get("ttl", self.default_ttl)
        
        if time.time() - created_at > ttl:
            # Entry expired, clean up
            self._delete_entry(key)
            return None
        
        # Read cached data
        cache_file = self._get_cache_file_path(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Set cache data with TTL.
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        
        # Write data file
        cache_file = self._get_cache_file_path(key)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
        
        # Update metadata
        self.metadata[key] = {
            "created_at": time.time(),
            "ttl": ttl,
            "file": str(cache_file.relative_to(self.cache_dir))
        }
        self._save_metadata()
    
    def delete(self, key: str) -> None:
        """Delete cache entry.
        
        Args:
            key: Cache key to delete
        """
        self._delete_entry(key)
    
    def _delete_entry(self, key: str) -> None:
        """Internal method to delete cache entry and its file."""
        # Remove metadata entry
        if key in self.metadata:
            del self.metadata[key]
            self._save_metadata()
        
        # Remove cache file
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            cache_file.unlink()
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        expired_keys = []
        
        for key, entry_meta in self.metadata.items():
            created_at = entry_meta.get("created_at", 0)
            ttl = entry_meta.get("ttl", self.default_ttl)
            
            if current_time - created_at > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._delete_entry(key)
        
        return len(expired_keys)
    
    def clear_all(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = len(self.metadata)
        
        for key in list(self.metadata.keys()):
            self._delete_entry(key)
        
        return count
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cache.py -v`
Expected: PASS (all 9 tests)

- [ ] **Step 5: Commit**

```bash
git add src/cdisc_mcp/cache.py tests/test_cache.py
git commit -m "feat: add persistent cache management module with TTL support

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: API 客户端

### Task 6: CDISC API 客户端核心

**Files:**
- Create: `src/cdisc_mcp/client.py`
- Create: `tests/test_client.py`

- [ ] **Step 1: Write failing test for CDISCClient basic functionality**

```python
# tests/test_client.py
"""Tests for CDISC API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from cdisc_mcp.client import CDISCClient
from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.cache import CacheManager


class TestCDISCClient:
    """Test CDISCClient class."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration."""
        return CDISCConfig(
            api_key="test-api-key",
            base_url="https://library.cdisc.org/api",
            cache_dir=str(tmp_path),
            request_timeout=30,
        )

    @pytest.fixture
    def cache(self, tmp_path):
        """Create test cache manager."""
        return CacheManager(str(tmp_path))

    @pytest.fixture
    def client(self, config, cache):
        """Create test client."""
        return CDISCClient(config, cache)

    def test_client_init(self, config, cache):
        """Test client initialization."""
        client = CDISCClient(config, cache)
        assert client.config == config
        assert client.cache == cache
        assert client.base_url == "https://library.cdisc.org/api"

    def test_normalize_version_dot_to_dash(self, client):
        """Test version normalization from dot to dash format."""
        assert client._normalize_version("1.8") == "1-8"
        assert client._normalize_version("3.4") == "3-4"
        assert client._normalize_version("1-8") == "1-8"  # Already correct
        assert client._normalize_version("adamig-1.3") == "adamig-1-3"

    @pytest.mark.asyncio
    async def test_get_products_cached(self, client, cache):
        """Test get_products returns cached data."""
        cached_data = {"products": [{"name": "SDTM", "href": "sdtm"}]}
        cache.set("products", cached_data)
        
        result = await client.get_products()
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_products_from_api(self, client, cache):
        """Test get_products fetches from API when not cached."""
        api_response = {"products": [{"name": "SDTM", "href": "sdtm"}]}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_products()
            assert result == api_response
            # Verify cached
            assert cache.get("products") == api_response

    @pytest.mark.asyncio
    async def test_get_standard_sdtm(self, client, cache):
        """Test get_standard for SDTM."""
        api_response = {"name": "SDTM", "version": "1-8"}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_standard("sdtm", "1-8")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_standard_version_normalization(self, client, cache):
        """Test get_standard normalizes version format."""
        api_response = {"name": "SDTM", "version": "1-8"}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_client.get.return_value = mock_response
            mock_httpx.return_value.__aenter__.return_value = mock_client
            
            # Pass "1.8" which should be normalized to "1-8"
            result = await client.get_standard("sdtm", "1.8")
            
            # Check that the URL was constructed with normalized version
            call_args = mock_client.get.call_args
            assert "1-8" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_datasets(self, client):
        """Test get_datasets."""
        api_response = {"datasets": [{"name": "DM", "label": "Demographics"}]}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_datasets("sdtmig", "3-4")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_dataset(self, client):
        """Test get_dataset for specific dataset."""
        api_response = {
            "name": "DM",
            "label": "Demographics",
            "variables": []
        }
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_dataset("sdtmig", "3-4", "DM")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_ct_packages(self, client, cache):
        """Test get_ct_packages."""
        api_response = {"packages": [{"name": "p60", "date": "2025-09-26"}]}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_ct_packages()
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_codelist(self, client):
        """Test get_codelist."""
        api_response = {
            "name": "C667",
            "label": "Sex",
            "terms": []
        }
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.get_codelist("p60", "C667")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_search(self, client):
        """Test search functionality."""
        api_response = {"results": [{"name": "AE", "type": "dataset"}]}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.search("adverse event")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_compare_versions(self, client):
        """Test compare_versions."""
        api_response = {"diff": {"added": [], "removed": [], "modified": []}}
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.compare_versions("sdtm", "1-8", "1-7")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client):
        """Test authentication error is raised correctly."""
        from cdisc_mcp.utils.errors import AuthenticationError
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
            mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            with pytest.raises(AuthenticationError):
                await client.get_products()

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, client):
        """Test rate limit handling with retry."""
        from cdisc_mcp.utils.errors import RateLimitError
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            
            # First call: 429 rate limit
            mock_response_429 = MagicMock()
            mock_response_429.status_code = 429
            mock_response_429.headers = {"Retry-After": "1"}
            
            # Second call: success
            mock_response_ok = MagicMock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"products": []}
            
            mock_client.get.side_effect = [mock_response_429, mock_response_ok]
            mock_httpx.return_value.__aenter__.return_value = mock_client
            
            result = await client.get_products()
            assert result == {"products": []}
            assert mock_client.get.call_count == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'cdisc_mcp'"

- [ ] **Step 3: Write src/cdisc_mcp/client.py**

完整代码见设计文档 Section 4.3。由于代码较长（约 400 行），分为以下部分实现：

**Part 1: 核心结构和请求方法**

```python
"""CDISC Library API Client."""

import asyncio
from typing import Any, Optional
import httpx

from .config import CDISCConfig
from .cache import CacheManager
from .utils.errors import (
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError,
    RateLimitError,
    format_http_error,
)


class CDISCClient:
    """CDISC Library API Client."""
    
    CACHE_TTL_CONFIG = {
        "products": 86400,
        "standards": 86400,
        "ct_packages": 86400,
        "standard_detail": 604800,
        "dataset_detail": 604800,
        "codelist_detail": 604800,
    }
    
    def __init__(self, config: CDISCConfig, cache: CacheManager):
        self.config = config
        self.cache = cache
        self.base_url = config.base_url.rstrip("/")
    
    def _normalize_version(self, version: str) -> str:
        """Normalize version format from dot to dash."""
        parts = version.split("-")
        normalized_parts = [p.replace(".", "-") if "." in p else p for p in parts]
        return "-".join(normalized_parts)
    
    def _normalize_package(self, package: str) -> str:
        """Normalize CT package name to lowercase."""
        return package.lower()
    
    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    async def _request_with_retry(self, url: str) -> dict[str, Any]:
        """Make HTTP request with retry on rate limit."""
        # 实现见设计文档...
```

**Part 2-4: 各 API 分组方法**
- Products & Info APIs
- SDTM/Dataset APIs
- CT APIs
- Search/Diff APIs
- ADaM/Integrated APIs
- BC/DS APIs

完整代码按照设计文档 Section 4.3 的方法签名实现。

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_client.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/cdisc_mcp/client.py tests/test_client.py
git commit -m "feat: add CDISC API client with full endpoint coverage

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 3: MCP Resources

### Task 7: Resources 模块

**Files:**
- Create: `src/cdisc_mcp/resources/__init__.py`
- Create: `src/cdisc_mcp/resources/products.py`
- Create: `src/cdisc_mcp/resources/standards.py`
- Create: `src/cdisc_mcp/resources/terminology.py`

- [ ] **Step 1: Write src/cdisc_mcp/resources/__init__.py**

```python
"""MCP Resources for CDISC Library."""

from mcp.server import Server

from ..client import CDISCClient
from .products import register_product_resources
from .standards import register_standard_resources
from .terminology import register_terminology_resources


async def register_resources(server: Server, client: CDISCClient) -> None:
    """Register all MCP resources."""
    await register_product_resources(server, client)
    await register_standard_resources(server, client)
    await register_terminology_resources(server, client)


__all__ = ["register_resources"]
```

- [ ] **Step 2: Write src/cdisc_mcp/resources/products.py**

```python
"""Product list resources."""

from mcp.server import Server
from mcp.types import Resource, TextContent

from ..client import CDISCClient


async def register_product_resources(server: Server, client: CDISCClient) -> None:
    """Register product-related resources."""
    
    @server.list_resources
    async def list_products_resources() -> list[Resource]:
        """List available product resources."""
        return [
            Resource(
                uri="cdisc://products",
                name="CDISC Products",
                description="所有 CDISC 产品列表",
                mimeType="application/json",
            ),
        ]
    
    @server.read_resource
    async def read_product_resource(uri: str) -> TextContent:
        """Read product resource content."""
        if uri == "cdisc://products":
            data = await client.get_products()
        else:
            raise ValueError(f"Unknown resource: {uri}")
        
        import json
        return TextContent(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )
```

- [ ] **Step 3: Commit**

```bash
git add src/cdisc_mcp/resources/
git commit -m "feat: add MCP Resources for products and standards

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 4: MCP Tools

### Task 8: Tools 模块

**Files:**
- Create: `src/cdisc_mcp/tools/__init__.py`
- Create: `src/cdisc_mcp/tools/standard.py`
- Create: `src/cdisc_mcp/tools/dataset.py`
- Create: `src/cdisc_mcp/tools/variable.py`
- Create: `src/cdisc_mcp/tools/codelist.py`
- Create: `src/cdisc_mcp/tools/biomedical.py`
- Create: `src/cdisc_mcp/tools/search.py`
- Create: `src/cdisc_mcp/tools/auxiliary.py`

- [ ] **Step 1: Write src/cdisc_mcp/tools/__init__.py**

```python
"""MCP Tools for CDISC Library."""

from mcp.server import Server
from ..client import CDISCClient


async def register_tools(server: Server, client: CDISCClient) -> None:
    """Register all MCP tools."""
    # 注册各工具模块
    pass


__all__ = ["register_tools"]
```

- [ ] **Step 2: Write individual tool modules**

按照设计文档 Section 5.2 实现各工具模块。每个工具包含：
- `@server.list_tools` 注册工具定义
- `@server.call_tool` 处理工具调用

- [ ] **Step 3: Commit**

```bash
git add src/cdisc_mcp/tools/
git commit -m "feat: add MCP Tools for all CDISC operations

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 5: MCP Prompts & Server

### Task 9: Prompts 模块

**Files:**
- Create: `src/cdisc_mcp/prompts/__init__.py`
- Create: `src/cdisc_mcp/prompts/templates.py`

- [ ] **Step 1: Write prompts module**

实现设计文档 Section 5.3 定义的 5 个 Prompts：
- explore_standard
- find_variable
- find_terminology
- compare_standards
- validate_dataset

- [ ] **Step 2: Commit**

```bash
git add src/cdisc_mcp/prompts/
git commit -m "feat: add MCP Prompts for guided exploration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 10: Server 入口

**Files:**
- Create: `src/cdisc_mcp/server.py`

- [ ] **Step 1: Write server.py**

```python
"""CDISC Library MCP Server Entry Point."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import CDISCConfig
from .client import CDISCClient
from .cache import CacheManager
from .resources import register_resources
from .tools import register_tools
from .prompts import register_prompts


async def main():
    """Main entry point."""
    config = CDISCConfig.from_env()
    cache = CacheManager(config.get_cache_path(), config.cache_ttl)
    client = CDISCClient(config, cache)
    server = Server("cdisc-library-mcp")
    
    await register_resources(server, client)
    await register_tools(server, client)
    await register_prompts(server)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Commit**

```bash
git add src/cdisc_mcp/server.py
git commit -m "feat: add MCP Server entry point

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 6: Testing

### Task 11: 集成测试

**Files:**
- Create: `tests/test_tools.py`

- [ ] **Step 1: Write integration tests**

为所有 MCP Tools 编写集成测试。

- [ ] **Step 2: Run all tests**

```bash
python -m pytest tests/ -v --cov=src/cdisc_mcp
```

Expected: All tests pass, coverage > 75%

- [ ] **Step 3: Commit**

```bash
git add tests/test_tools.py
git commit -m "test: add integration tests

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 7: Documentation

### Task 12: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

包含：
- 项目介绍
- 安装指南
- 配置说明
- 可用工具列表
- 使用示例

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 13: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest tests/ -v --cov=src/cdisc_mcp --cov-report=term-missing
```

- [ ] **Step 2: Test MCP server locally**

```bash
CDISC_API_KEY=test python -m cdisc_mcp
```

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "chore: final cleanup

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-03-cdisc-library-mcp-implementation.md`. Ready to execute?**

**Execution path:** Use `superpowers:subagent-driven-development` to execute this plan with parallel task execution.