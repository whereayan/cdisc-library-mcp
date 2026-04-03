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
        assert error.details == {}

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