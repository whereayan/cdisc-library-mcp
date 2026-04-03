"""Configuration management for CDISC MCP Server."""

import os
from typing import Optional

from pydantic import BaseModel, Field


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