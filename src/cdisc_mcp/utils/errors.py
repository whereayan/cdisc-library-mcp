"""Error handling for CDISC MCP Server.

Provides user-friendly Chinese error messages with detailed context.
"""

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
            resource_type="url",
            resource_id=url
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