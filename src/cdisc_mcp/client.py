"""CDISC Library API Client.

Provides async HTTP client for CDISC Library API with caching and retry support.
"""

import asyncio
import difflib
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


# Diff payloads can reach tens of MB (SDTMIG 3-3 -> 3-4 is ~29 MB). Fetch them
# with a single capped attempt instead of the default retry ladder: worst case
# stays under the 60 s request timeout most MCP clients enforce, and retrying a
# 29 MB download three times helps nobody.
_DIFF_TIMEOUT = 45.0

# Sentinel version alias resolved against the product list.
_LATEST = "latest"


def _version_tuple(version: str) -> Optional[tuple[int, ...]]:
    """Parse a purely numeric dashed version ('3-4') into a sortable tuple.

    Returns None for anything non-numeric (e.g. 'adam-tte-1-0'), which callers
    treat as "cannot order, do not guess".
    """
    try:
        return tuple(int(part) for part in str(version).split("-"))
    except (TypeError, ValueError):
        return None


def _row_to_dict(head: list, row: Any) -> Any:
    """Flatten one diff table row into {column: text}.

    Diff rows come as {"<Column>": [{"text": "..."}, ...]} per head column;
    the wrapper dicts are pure overhead for an LLM reader.
    """
    if not isinstance(row, dict):
        return row
    out: dict[str, Any] = {}
    for col in head:
        cells = row.get(col)
        if isinstance(cells, list):
            texts = [
                str(c.get("text", ""))
                for c in cells
                if isinstance(c, dict) and c.get("text") is not None
            ]
            out[col] = texts[0] if len(texts) == 1 else "; ".join(texts)
        elif cells is not None:
            out[col] = cells
    return out


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

    def _product_path(self, standard: str, version: str) -> tuple[str, str]:
        """Map (standard, version) onto the API's (group, tail) path segments.

        Every product URL in the Library API is ``/mdr/{group}/{tail}[...]``
        where the tail is exactly the last segment of the product's href in
        ``/mdr/products`` (verified against the live API):

        - ADaM base model: group ``adam``, tail ``adam-{version}``
          (``/mdr/adam/adam-2-1``; the bare ``/mdr/adam/2-1`` is a 404)
        - ADaMIG:          group ``adam``, tail ``adamig-{version}``
        - SDTM/SDTMIG/SENDIG/CDASH/CDASHIG: group == standard, tail == version

        Args:
            standard: Standard name (e.g., "adam", "adamig", "sdtmig")
            version: Version string (dots already normalized or not)

        Returns:
            Tuple of (group, tail) path segments
        """
        version = self._normalize_version(version)
        if standard == "adamig":
            return ("adam", f"adamig-{version}")
        if standard == "adam":
            return ("adam", f"adam-{version}")
        return (standard, version)

    def _build_standard_url(self, standard: str, version: str, *extra_parts: str) -> str:
        """Build URL for a standard, handling the ADaM family's prefixed tails.

        Args:
            standard: Standard name (e.g., "adam", "adamig", "sdtm", "sdtmig")
            version: Version string (e.g., "2-1", "1-3", "3-4")
            *extra_parts: Additional path parts (e.g., "classes", "datasets")

        Returns:
            Full URL for the standard
        """
        group, tail = self._product_path(standard, version)
        return self._build_url(group, tail, *extra_parts)

    async def _resolve_version(self, standard: str, version: str) -> str:
        """Normalize a version, resolving the 'latest' alias via /products.

        Args:
            standard: Standard name
            version: Version string, or 'latest' (case-insensitive)

        Returns:
            Concrete normalized version string (e.g., '3-4')
        """
        if str(version).strip().lower() == _LATEST:
            return await self._latest_version(standard)
        return self._normalize_version(version)

    @staticmethod
    def _iter_href_tails(node: Any, group: str, out: list) -> None:
        """Collect single-segment href tails under /mdr/{group}/ from a payload."""
        prefix = f"/mdr/{group}/"
        if isinstance(node, dict):
            href = node.get("href")
            if isinstance(href, str) and href.startswith(prefix):
                tail = href[len(prefix):]
                if tail and "/" not in tail:
                    out.append(tail)
            for value in node.values():
                CDISCClient._iter_href_tails(value, group, out)
        elif isinstance(node, list):
            for value in node:
                CDISCClient._iter_href_tails(value, group, out)

    async def _latest_version(self, standard: str) -> str:
        """Resolve the newest numeric version of a standard from the product list.

        Only purely numeric tails count ('3-4', '2-1'); sibling IG products in
        the same group ('ap-1-0', 'md-1-1', 'adae-1-0', ...) are ignored.

        Args:
            standard: Standard name

        Returns:
            Newest version string, e.g. '3-4'

        Raises:
            ResourceNotFoundError: If the product list has no numeric version
                for this standard
        """
        products = await self.get_products()
        group = "adam" if standard in ("adam", "adamig") else standard
        prefix = f"{standard}-" if standard in ("adam", "adamig") else ""

        tails: list[str] = []
        self._iter_href_tails(products, group, tails)

        candidates: list[str] = []
        for tail in set(tails):
            if prefix:
                if not tail.startswith(prefix):
                    continue
                rest = tail[len(prefix):]
            else:
                rest = tail
            if re.fullmatch(r"\d+(-\d+)*", rest):
                candidates.append(rest)

        if not candidates:
            raise ResourceNotFoundError(
                message=(
                    f"🧭 无法为 '{standard}' 解析 latest 版本："
                    "产品列表中找不到该标准的数字版本号"
                ),
                resource_type="standard",
                resource_id=standard,
                standard=standard,
            )
        return max(candidates, key=lambda v: tuple(int(p) for p in v.split("-")))

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
        *,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        **kwargs
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            timeout: Per-attempt timeout override (default: config.request_timeout)
            retries: Retry attempts override (default: config.max_retries)
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
        timeout = self.config.request_timeout if timeout is None else timeout
        retries = self.config.max_retries if retries is None else retries

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
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
            if attempt < retries:
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
            version: Standard version ("1.8", "1-8", or "latest")

        Returns:
            Dict with standard details
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"standards/{standard}/{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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
            version: Standard version or "latest"

        Returns:
            Dict with classes list
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"standards/{standard}/{version}/classes"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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
            version: Standard version or "latest"

        Returns:
            Dict with datasets list
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"datasets/{standard}/{version}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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
            version: Standard version or "latest"
            dataset: Dataset name (e.g., "DM", "AE")

        Returns:
            Dict with dataset details
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"datasets/{standard}/{version}/{dataset}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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
            version: Standard version or "latest"
            dataset: Dataset name

        Returns:
            Dict with variables list
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"datasets/{standard}/{version}/{dataset}/variables"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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
            version: Standard version or "latest"
            dataset: Dataset name
            variable: Variable name

        Returns:
            Dict with variable details
        """
        version = await self._resolve_version(standard, version)
        cache_key = f"datasets/{standard}/{version}/{dataset}/variables/{variable}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

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

    async def _resolve_term_code(
        self,
        package: str,
        codelist: str,
        term: str
    ) -> str:
        """Resolve a term reference to its C-code.

        Accepts either a C-code ('C201972', used as-is) or a term name
        ('Female', matched case-insensitively against the codelist's term
        titles via the already-cached terms list — one extra request at most).

        Args:
            package: Normalized package name
            codelist: Codelist ID
            term: C-code or term name

        Returns:
            Term C-code (e.g., 'C201972')

        Raises:
            ResourceNotFoundError: If a name does not match any term; the
                message lists close candidates when there are any
        """
        term = str(term).strip()
        if re.fullmatch(r"(?i)C\d+", term):
            return term.upper()

        payload = await self.get_codelist_terms(package, codelist)
        items = payload.get("_links", {}).get("terms", []) or []
        titles = [
            (str(it.get("title", "")), str(it.get("href", "")))
            for it in items
            if isinstance(it, dict)
        ]
        for title, href in titles:
            if title and title.casefold() == term.casefold() and href:
                return href.rstrip("/").split("/")[-1]

        close = difflib.get_close_matches(
            term, [title for title, _ in titles if title], n=5, cutoff=0.4
        )
        hint = f"；相近的术语名: {', '.join(close)}" if close else ""
        raise ResourceNotFoundError(
            message=(
                f"🔎 编码列表 {codelist} 中没有名为 '{term}' 的术语"
                f"（按术语名匹配，共 {len(titles)} 条）{hint}。"
                "也可先 get_codelist_terms 浏览全部术语名，或直接传 C 代码"
            ),
            resource_type="term",
            resource_id=term,
        )

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
            term: Term C-code ('C201972') or term name ('Female')

        Returns:
            Dict with term details
        """
        package = self._normalize_package(package)
        code = await self._resolve_term_code(package, codelist, term)
        cache_key = f"ct/packages/{package}/codelists/{codelist}/terms/{code}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        url = self._build_url(
            "ct", "packages", package, "codelists", codelist, "terms", code
        )
        result = await self._request_with_retry("GET", url)
        self.cache.set(cache_key, result)
        return result

    # ====================
    # Search Endpoints
    # ====================

    async def search(
        self,
        query: str,
        type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search across all CDISC content, with caching and client-side paging.

        The API returns at most 100 ranked hits per query (plus totalHits and
        hasMore). Type filtering and limit/offset paging happen client-side on
        that hit list; the raw response is cached so paging through one query
        costs a single request.

        Args:
            query: Search query string
            type: Optional hit-type filter, case-insensitive (e.g., "Analysis Variable")
            limit: Optional maximum number of hits to return
            offset: Number of hits to skip (for paging)

        Returns:
            Dict with query metadata and the (filtered/paged) hits list
        """
        cache_key = f"search/{query}"
        result = self.cache.get(cache_key)
        if result is None:
            url = self._build_url("search")
            result = await self._request_with_retry(
                "GET",
                url,
                params={"q": query}
            )
            self.cache.set(cache_key, result)

        all_hits = list(result.get("hits", []) or [])
        hits = all_hits
        if type:
            wanted = str(type).strip().lower()
            hits = [h for h in hits if str(h.get("type", "")).lower() == wanted]
        matched = len(hits)
        if offset:
            hits = hits[offset:]
        if limit is not None:
            hits = hits[: max(0, int(limit))]

        out: dict[str, Any] = {
            "query": query,
            "totalHits": result.get("totalHits", matched),
            "hasMore": result.get("hasMore", False),
            "returned": len(hits),
        }
        if type:
            out["typeFilter"] = type
            out["matchedInPage"] = matched
        if offset:
            out["offset"] = offset
        if limit is not None:
            out["limit"] = limit
        out["hits"] = hits
        return out

    # ====================
    # Comparison Endpoints
    # ====================

    async def compare_versions(
        self,
        standard: str,
        old_version: str,
        new_version: str,
        section: Optional[str] = None,
        max_rows: int = 200,
        raw: bool = False,
    ) -> dict[str, Any]:
        """Compare two versions of a standard.

        Raw diff payloads reach tens of MB, so the default return is a summary:
        the section index (name + row count) plus the flattened Info section.
        Pass ``section`` to drill into one section's rows (flattened and
        truncated to ``max_rows``), or ``raw=True`` for the full payload.

        Version arguments accept 'latest'; if they are given in reverse order
        they are swapped automatically (noted in the response).

        Args:
            standard: Standard name
            old_version: Older version ('3-3', '3.3', or 'latest')
            new_version: Newer version
            section: Optional section title to return in detail
            max_rows: Row cap for section detail mode
            raw: Return the full unsummarized diff payload

        Returns:
            Summary dict, section detail dict, or raw diff payload

        Raises:
            ResourceNotFoundError: If the section name does not exist
        """
        old = await self._resolve_version(standard, old_version)
        new = await self._resolve_version(standard, new_version)

        swapped = False
        old_t, new_t = _version_tuple(old), _version_tuple(new)
        if old_t is not None and new_t is not None and old_t > new_t:
            old, new, swapped = new, old, True

        cache_key = f"compare/{standard}/{old}/{new}"
        payload = self.cache.get(cache_key)
        if payload is None:
            # URL format: /mdr/diff/{group}/{new-tail}/{old-tail} where the
            # tails follow the same product-path shape as standard URLs
            # (e.g. /mdr/diff/adam/adamig-1-3/adamig-1-2 — a bare
            # /mdr/diff/adamig/1-3/1-2 is a 404).
            group, new_tail = self._product_path(standard, new)
            _, old_tail = self._product_path(standard, old)
            url = self._build_url("diff", group, new_tail, old_tail)
            payload = await self._request_with_retry(
                "GET", url, timeout=_DIFF_TIMEOUT, retries=0
            )
            self.cache.set(cache_key, payload)

        if raw:
            return payload

        sections = payload.get("diff", []) if isinstance(payload, dict) else []
        if not isinstance(sections, list):
            sections = []

        meta: dict[str, Any] = {
            "standard": standard,
            "old_version": old,
            "new_version": new,
        }
        if swapped:
            meta["note"] = "检测到新旧版本传反，已自动交换后再比较"

        if section is not None:
            want = str(section).strip().lower()
            for sec in sections:
                if isinstance(sec, dict) and str(sec.get("title", "")).lower() == want:
                    head = sec.get("head", []) or []
                    body = sec.get("body", []) or []
                    rows = body[: max(0, int(max_rows))]
                    return {
                        **meta,
                        "section": sec.get("title"),
                        "total_rows": len(body),
                        "returned_rows": len(rows),
                        "truncated": len(rows) < len(body),
                        "rows": [_row_to_dict(head, row) for row in rows],
                    }
            available = [
                s.get("title") for s in sections if isinstance(s, dict)
            ]
            raise ResourceNotFoundError(
                message=(
                    f"📑 diff 中没有分区 '{section}'。可用分区: {available}"
                ),
                resource_type="diff-section",
                resource_id=str(section),
                standard=standard,
            )

        index = [
            {"section": s.get("title"), "rows": len(s.get("body", []) or [])}
            for s in sections
            if isinstance(s, dict)
        ]
        info = None
        for sec in sections:
            if isinstance(sec, dict) and str(sec.get("title", "")).lower() == "info":
                head = sec.get("head", []) or []
                info = [_row_to_dict(head, row) for row in (sec.get("body", []) or [])]
                break

        return {
            **meta,
            "info": info,
            "sections": index,
            "hint": (
                "此为摘要视图。传 section='<分区名>' 查看该分区明细"
                "（max_rows 控制行数，默认 200）；raw=true 返回未汇总的完整"
                " diff（可达数十 MB，谨慎使用）"
            ),
        }
