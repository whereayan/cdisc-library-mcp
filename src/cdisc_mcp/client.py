"""CDISC Library API Client.

Provides async HTTP client for CDISC Library API with caching and retry support.
"""

import asyncio
import re
from typing import Any, Optional

import httpx

from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.cache import CacheManager
from cdisc_mcp.utils.errors import (
    AuthenticationError,
    ResourceNotFoundError,
    NetworkError,
    RateLimitError,
    CDISCError,
    format_http_error,
)


class CDISCClient:
    """Async client for CDISC Library API.

    Provides methods to interact with all CDISC Library endpoints.
    Handles authentication, caching, retries, and error handling.

    Attributes:
        config: CDISCConfig instance with API settings
        cache: CacheManager for persistent caching
        base_url: API base URL
    """

    def __init__(self, config: CDISCConfig, cache: CacheManager):
        """Initialize CDISC client.

        Args:
            config: Configuration instance
            cache: Cache manager instance
        """
        self.config = config
        self.cache = cache
        # CDISC API uses /mdr/ prefix for most endpoints
        self.base_url = config.base_url.rstrip("/") + "/mdr"

    def _normalize_version(self, version: str) -> str:
        """Convert version format from dot to dash.

        CDISC API uses dash-separated version numbers in URLs.

        Args:
            version: Version string (e.g., "1.8" or "1-8")

        Returns:
            Normalized version with dashes (e.g., "1-8")

        Examples:
            >>> client._normalize_version("1.8")
            '1-8'
            >>> client._normalize_version("adamig-1.3")
            'adamig-1-3'
        """
        # Replace dots with dashes, but only in version numbers
        # Pattern: digit(s).digit(s) -> digit(s)-digit(s)
        return re.sub(r"(\d)\.(\d)", r"\1-\2", version)

    def _normalize_package(self, package: str) -> str:
        """Normalize CT package name to lowercase.

        Args:
            package: CT package name (e.g., "p60" or "P60")

        Returns:
            Lowercase package name
        """
        return package.lower()

    def _build_standard_url(self, standard: str, version: str, *extra_parts: str) -> str:
        """Build URL for a standard, handling IG series special format.

        IG (Implementation Guide) series standards have different URL formats:
        - ADaM base model: /mdr/adam/{version} (e.g., /mdr/adam/2-1)
        - ADaMIG: /mdr/adam/adamig-{version} (e.g., /mdr/adam/adamig-1-3)
        - SDTM base model: /mdr/sdtm/{version} (e.g., /mdr/sdtm/2-0)
        - SDTMIG: /mdr/sdtmig/{version} (e.g., /mdr/sdtmig/3-4) - NO prefix
        - SENDIG: /mdr/sendig/{version} (e.g., /mdr/sendig/3-1) - NO prefix
        - CDASHIG: /mdr/cdashig/{version} (e.g., /mdr/cdashig/2-3) - NO prefix

        Args:
            standard: Standard name (e.g., "adam", "adamig", "sdtm", "sdtmig")
            version: Version string (e.g., "2-1", "1-3", "3-4")
            *extra_parts: Additional path parts (e.g., "classes", "datasets")

        Returns:
            Full URL for the standard
        """
        version = self._normalize_version(version)

        # ADaMIG is special: it's under /mdr/adam/ with prefix "adamig-{version}"
        if standard == "adamig":
            url = self._build_url("adam", f"adamig-{version}", *extra_parts)
        # ADaM base model: /mdr/adam/{version}
        elif standard == "adam":
            url = self._build_url("adam", version, *extra_parts)
        # SDTMIG/SENDIG/CDASHIG: NO prefix, just /mdr/{standard}/{version}
        elif standard in ("sdtmig", "sendig", "cdashig"):
            url = self._build_url(standard, version, *extra_parts)
        else:
            # Base standards (sdtm, cdash): /mdr/{standard}/{version}
            url = self._build_url(standard, version, *extra_parts)

        return url

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dict with Content-Type and api-key header
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.api_key:
            # CDISC API uses api-key header, not Bearer token
            headers["api-key"] = self.config.api_key
        return headers

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request options

        Returns:
            JSON response data

        Raises:
            AuthenticationError: Invalid or missing API key
            ResourceNotFoundError: Resource not found
            RateLimitError: Rate limit exceeded
            NetworkError: Network or server error
        """
        last_error: Optional[Exception] = None
        delay = self.config.retry_delay

        for attempt in range(self.config.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.config.request_timeout
                ) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self._get_headers(),
                        **kwargs
                    )

                    # Handle successful response
                    if response.status_code == 200:
                        return response.json()

                    # Handle errors
                    error = format_http_error(
                        response.status_code,
                        url,
                        response.text
                    )

                    # Don't retry client errors (4xx except 429)
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        raise error

                    # Retry server errors and rate limits
                    last_error = error

            except httpx.TimeoutException as e:
                last_error = NetworkError(
                    message="⏱️ 请求超时，请稍后重试",
                    original_error=str(e)
                )
            except httpx.NetworkError as e:
                last_error = NetworkError(
                    message="🌐 网络连接失败，请检查网络设置",
                    original_error=str(e)
                )

            # Wait before retry (except on last attempt)
            if attempt < self.config.max_retries:
                await asyncio.sleep(delay)
                delay *= self.config.retry_backoff

        # All retries exhausted
        if last_error:
            raise last_error
        raise NetworkError("未知错误")

    def _build_url(self, *path_parts: str) -> str:
        """Build full URL from path parts.

        Args:
            *path_parts: URL path components

        Returns:
            Full URL string
        """
        path = "/".join(str(p).strip("/") for p in path_parts if p)
        return f"{self.base_url}/{path}"

    # ====================
    # Products Endpoints
    # ====================

    async def get_products(self) -> dict[str, Any]:
        """Get list of all CDISC products.

        Returns:
            Dict with products list and metadata
        """
        cache_key = "products"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url("products")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_about(self) -> dict[str, Any]:
        """Get API information.

        Returns:
            Dict with API version and metadata
        """
        url = self._build_url("about")
        return await self._request_with_retry("GET", url)

    # ====================
    # Standards Endpoints
    # ====================

    async def get_standard(
        self,
        standard: str,
        version: str
    ) -> dict[str, Any]:
        """Get standard information.

        Args:
            standard: Standard name (e.g., "sdtm", "adam", "cdash")
            version: Standard version (e.g., "1.8" or "1-8")

        Returns:
            Dict with standard details
        """
        version = self._normalize_version(version)
        cache_key = f"standards/{standard}/{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_classes(
        self,
        standard: str,
        version: str
    ) -> dict[str, Any]:
        """Get classes for a standard.

        Args:
            standard: Standard name
            version: Standard version

        Returns:
            Dict with classes list
        """
        version = self._normalize_version(version)
        cache_key = f"standards/{standard}/{version}/classes"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version, "classes")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    # ====================
    # Datasets Endpoints
    # ====================

    async def get_datasets(
        self,
        standard: str,
        version: str
    ) -> dict[str, Any]:
        """Get datasets for a standard.

        Args:
            standard: Standard name (e.g., "sdtmig", "adamig")
            version: Standard version

        Returns:
            Dict with datasets list
        """
        version = self._normalize_version(version)
        cache_key = f"datasets/{standard}/{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version, "datasets")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_dataset(
        self,
        standard: str,
        version: str,
        dataset: str
    ) -> dict[str, Any]:
        """Get dataset details.

        Args:
            standard: Standard name
            version: Standard version
            dataset: Dataset name (e.g., "DM", "AE")

        Returns:
            Dict with dataset details
        """
        version = self._normalize_version(version)
        cache_key = f"datasets/{standard}/{version}/{dataset}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version, "datasets", dataset)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_dataset_variables(
        self,
        standard: str,
        version: str,
        dataset: str
    ) -> dict[str, Any]:
        """Get variables for a dataset.

        Args:
            standard: Standard name
            version: Standard version
            dataset: Dataset name

        Returns:
            Dict with variables list
        """
        version = self._normalize_version(version)
        cache_key = f"datasets/{standard}/{version}/{dataset}/variables"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version, "datasets", dataset, "variables")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_variable(
        self,
        standard: str,
        version: str,
        dataset: str,
        variable: str
    ) -> dict[str, Any]:
        """Get variable details.

        Args:
            standard: Standard name
            version: Standard version
            dataset: Dataset name
            variable: Variable name

        Returns:
            Dict with variable details
        """
        version = self._normalize_version(version)
        cache_key = f"datasets/{standard}/{version}/{dataset}/variables/{variable}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build URL using helper method that handles ADaM series special format
        url = self._build_standard_url(standard, version, "datasets", dataset, "variables", variable)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    # ====================
    # Controlled Terminology Endpoints
    # ====================

    async def get_ct_packages(self) -> dict[str, Any]:
        """Get all controlled terminology packages.

        Returns:
            Dict with CT packages list
        """
        cache_key = "ct/packages"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url("ct", "packages")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_ct_package(self, package: str) -> dict[str, Any]:
        """Get controlled terminology package details.

        Args:
            package: Package name (e.g., "p60", "P60")

        Returns:
            Dict with package details
        """
        package = self._normalize_package(package)
        cache_key = f"ct/packages/{package}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url("ct", "packages", package)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_codelists(self, package: str) -> dict[str, Any]:
        """Get codelists for a CT package.

        Args:
            package: Package name

        Returns:
            Dict with codelists list
        """
        package = self._normalize_package(package)
        cache_key = f"ct/packages/{package}/codelists"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url("ct", "packages", package, "codelists")
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_codelist(
        self,
        package: str,
        codelist: str
    ) -> dict[str, Any]:
        """Get codelist details.

        Args:
            package: Package name
            codelist: Codelist ID (e.g., "C667")

        Returns:
            Dict with codelist details
        """
        package = self._normalize_package(package)
        cache_key = f"ct/packages/{package}/codelists/{codelist}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url("ct", "packages", package, "codelists", codelist)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_codelist_terms(
        self,
        package: str,
        codelist: str
    ) -> dict[str, Any]:
        """Get terms for a codelist.

        Args:
            package: Package name
            codelist: Codelist ID

        Returns:
            Dict with terms list
        """
        package = self._normalize_package(package)
        cache_key = f"ct/packages/{package}/codelists/{codelist}/terms"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url(
            "ct", "packages", package, "codelists", codelist, "terms"
        )
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    async def get_term(
        self,
        package: str,
        codelist: str,
        term: str
    ) -> dict[str, Any]:
        """Get term details.

        Args:
            package: Package name
            codelist: Codelist ID
            term: Term ID

        Returns:
            Dict with term details
        """
        package = self._normalize_package(package)
        cache_key = f"ct/packages/{package}/codelists/{codelist}/terms/{term}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url(
            "ct", "packages", package, "codelists", codelist, "terms", term
        )
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    # ====================
    # Search Endpoints
    # ====================

    async def search(self, query: str) -> dict[str, Any]:
        """Search across all CDISC content.

        Args:
            query: Search query string

        Returns:
            Dict with search results
        """
        url = self._build_url("search")
        result = await self._request_with_retry(
            "GET",
            url,
            params={"q": query}
        )
        return result

    # ====================
    # Comparison Endpoints
    # ====================

    async def compare_versions(
        self,
        standard: str,
        version1: str,
        version2: str
    ) -> dict[str, Any]:
        """Compare two versions of a standard.

        Args:
            standard: Standard name
            version1: First version
            version2: Second version

        Returns:
            Dict with comparison results
        """
        version1 = self._normalize_version(version1)
        version2 = self._normalize_version(version2)
        cache_key = f"compare/{standard}/{version1}/{version2}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # URL format: /mdr/diff/{product}/{version}/{previous}
        url = self._build_url("diff", standard, version2, version1)
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result