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
        if "CDISC_API_KEY" in os.environ:
            del os.environ["CDISC_API_KEY"]

        config = CDISCConfig.from_env()
        assert config.api_key == ""
        assert config.base_url == "https://library.cdisc.org/api"

    def test_config_validation_empty_api_key_allowed(self):
        """Test that empty API key is allowed."""
        config = CDISCConfig(api_key="")
        assert config.api_key == ""

    def test_config_invalid_cache_ttl(self):
        """Test that invalid cache TTL raises validation error."""
        with pytest.raises(Exception):
            CDISCConfig(api_key="test", cache_ttl=-1)