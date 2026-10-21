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
        return CDISCConfig(
            api_key="test-api-key",
            base_url="https://library.cdisc.org/api",
            cache_dir=str(tmp_path),
            request_timeout=30,
        )

    @pytest.fixture
    def cache(self, tmp_path):
        return CacheManager(str(tmp_path))

    @pytest.fixture
    def client(self, config, cache):
        return CDISCClient(config, cache)

    def test_client_init(self, config, cache):
        client = CDISCClient(config, cache)
        assert client.config == config
        assert client.cache == cache
        # base_url includes /mdr prefix for CDISC API
        assert client.base_url == "https://library.cdisc.org/api/mdr"

    def test_normalize_version_dot_to_dash(self, client):
        assert client._normalize_version("1.8") == "1-8"
        assert client._normalize_version("3.4") == "3-4"
        assert client._normalize_version("1-8") == "1-8"
        assert client._normalize_version("adamig-1.3") == "adamig-1-3"

    def test_build_standard_url_sdtmig(self, client):
        """Test URL building for SDTMIG - should NOT have sdtmig- prefix."""
        # SDTMIG: /mdr/sdtmig/{version}
        url = client._build_standard_url("sdtmig", "3-4")
        assert url == "https://library.cdisc.org/api/mdr/sdtmig/3-4"

        url = client._build_standard_url("sdtmig", "3.4", "datasets", "LB")
        assert url == "https://library.cdisc.org/api/mdr/sdtmig/3-4/datasets/LB"

    def test_build_standard_url_sendig(self, client):
        """Test URL building for SENDIG - should NOT have sendig- prefix."""
        url = client._build_standard_url("sendig", "3-1")
        assert url == "https://library.cdisc.org/api/mdr/sendig/3-1"

    def test_build_standard_url_cdashig(self, client):
        """Test URL building for CDASHIG - should NOT have cdashig- prefix."""
        url = client._build_standard_url("cdashig", "2-3")
        assert url == "https://library.cdisc.org/api/mdr/cdashig/2-3"

    def test_build_standard_url_adamig(self, client):
        """Test URL building for ADaMIG - should have adamig- prefix under /adam/."""
        # ADaMIG: /mdr/adam/adamig-{version}
        url = client._build_standard_url("adamig", "1-3")
        assert url == "https://library.cdisc.org/api/mdr/adam/adamig-1-3"

    def test_build_standard_url_adam(self, client):
        """ADaM base model carries an 'adam-' prefixed tail under /adam/.

        Verified against the live API: /mdr/adam/2-1 is a 404, only
        /mdr/adam/adam-2-1 resolves. 0.1.5 and earlier built the 404 form.
        """
        url = client._build_standard_url("adam", "2-1")
        assert url == "https://library.cdisc.org/api/mdr/adam/adam-2-1"

    def test_build_standard_url_sdtm(self, client):
        """Test URL building for SDTM base model."""
        # SDTM base: /mdr/sdtm/{version}
        url = client._build_standard_url("sdtm", "2-0")
        assert url == "https://library.cdisc.org/api/mdr/sdtm/2-0"

    @pytest.mark.asyncio
    async def test_get_products_cached(self, client, cache):
        cached_data = {"products": [{"name": "SDTM", "href": "sdtm"}]}
        cache.set("products", cached_data)

        result = await client.get_products()
        assert result == cached_data

    def _create_mock_response(self, status_code, json_data=None):
        """Helper to create a properly mocked response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = ""
        return mock_response

    @pytest.mark.asyncio
    async def test_get_products_from_api(self, client, cache):
        api_response = {"products": [{"name": "SDTM", "href": "sdtm"}]}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_products()
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_standard_sdtm(self, client, cache):
        api_response = {"name": "SDTM", "version": "1-8"}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_standard("sdtm", "1-8")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_datasets(self, client):
        api_response = {"datasets": [{"name": "DM", "label": "Demographics"}]}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_datasets("sdtmig", "3-4")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_dataset(self, client):
        api_response = {"name": "DM", "label": "Demographics"}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_dataset("sdtmig", "3-4", "DM")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_ct_packages(self, client, cache):
        api_response = {"packages": [{"name": "p60"}]}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_ct_packages()
            assert result == api_response

    @pytest.mark.asyncio
    async def test_get_codelist(self, client):
        api_response = {"name": "C667", "label": "Sex"}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_codelist("p60", "C667")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_search(self, client):
        api_response = {
            "totalHits": 2,
            "hasMore": False,
            "hits": [
                {"name": "AVAL", "type": "Analysis Variable"},
                {"name": "AE", "type": "Dataset"},
            ],
        }

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.search("adverse event")
            assert result["query"] == "adverse event"
            assert result["totalHits"] == 2
            assert result["returned"] == 2
            assert result["hits"] == api_response["hits"]

    @pytest.mark.asyncio
    async def test_search_type_filter_and_paging_are_client_side(self, client):
        """type/limit/offset filter the cached hit list without new requests."""
        api_response = {
            "totalHits": 3,
            "hasMore": False,
            "hits": [
                {"name": "A", "type": "Analysis Variable"},
                {"name": "B", "type": "Dataset"},
                {"name": "C", "type": "analysis variable"},
            ],
        }

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            # type filter is case-insensitive
            result = await client.search("q1", type="analysis variable")
            assert [h["name"] for h in result["hits"]] == ["A", "C"]
            assert result["typeFilter"] == "analysis variable"
            assert result["matchedInPage"] == 2

            # paging over the cached response: still exactly one HTTP request
            result = await client.search("q1", limit=1, offset=1)
            assert [h["name"] for h in result["hits"]] == ["B"]
            assert result["offset"] == 1 and result["limit"] == 1
            assert mock_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_search_result_is_cached(self, client, cache):
        """0.1.5 hit the API for every search; identical queries now cache."""
        api_response = {"totalHits": 0, "hasMore": False, "hits": []}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            await client.search("cache me")
            await client.search("cache me")
            assert mock_client.request.call_count == 1
        assert cache.get("search/cache me") is not None

    @pytest.mark.asyncio
    async def test_compare_versions(self, client):
        """Default return is a summary: section index + flattened Info rows."""
        api_response = {"diff": [
            {
                "title": "Info",
                "head": ["Attribute", "Value"],
                "body": [{
                    "Attribute": [{"text": "Updated Version"}],
                    "Value": [{"text": "SDTMIG v3.4"}],
                }],
            },
            {
                "title": "Domains",
                "head": ["Name"],
                "body": [{"Name": [{"text": "AG"}]}, {"Name": [{"text": "ML"}]}],
            },
        ]}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.compare_versions("sdtmig", "3-3", "3-4")
            assert result["standard"] == "sdtmig"
            assert result["old_version"] == "3-3"
            assert result["new_version"] == "3-4"
            assert result["sections"] == [
                {"section": "Info", "rows": 1},
                {"section": "Domains", "rows": 2},
            ]
            assert result["info"] == [{"Attribute": "Updated Version", "Value": "SDTMIG v3.4"}]
            # diff URL uses the unified /diff/{group}/{new}/{old} shape
            assert mock_client.request.call_args[0][1] == (
                "https://library.cdisc.org/api/mdr/diff/sdtmig/3-4/3-3"
            )

    @pytest.mark.asyncio
    async def test_compare_versions_adamig_uses_adam_group_url(self, client):
        """Live-verified: /diff/adamig/1-3/1-2 is a 404; the prefixed form works."""
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, {"diff": []})
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            await client.compare_versions("adamig", "1-2", "1-3")
            assert mock_client.request.call_args[0][1] == (
                "https://library.cdisc.org/api/mdr/diff/adam/adamig-1-3/adamig-1-2"
            )

    @pytest.mark.asyncio
    async def test_compare_versions_swaps_reversed_inputs(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, {"diff": []})
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.compare_versions("sdtmig", "3-4", "3-3")
            assert result["old_version"] == "3-3" and result["new_version"] == "3-4"
            assert "交换" in result["note"]

    @pytest.mark.asyncio
    async def test_compare_versions_section_drilldown(self, client, cache):
        cache.set("compare/sdtmig/3-3/3-4", {"diff": [
            {
                "title": "Domains",
                "head": ["Name"],
                "body": [{"Name": [{"text": f"D{i}"}]} for i in range(5)],
            },
        ]})
        result = await client.compare_versions(
            "sdtmig", "3-3", "3-4", section="domains", max_rows=2
        )
        assert result["total_rows"] == 5
        assert result["returned_rows"] == 2
        assert result["truncated"] is True
        assert result["rows"] == [{"Name": "D0"}, {"Name": "D1"}]

    @pytest.mark.asyncio
    async def test_compare_versions_unknown_section_lists_available(self, client, cache):
        from cdisc_mcp.utils.errors import ResourceNotFoundError

        cache.set("compare/sdtmig/3-3/3-4", {"diff": [{"title": "Info", "head": [], "body": []}]})
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.compare_versions("sdtmig", "3-3", "3-4", section="Nope")
        assert "Info" in str(exc.value.message)

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, client):
        from cdisc_mcp.utils.errors import AuthenticationError

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(401)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            with pytest.raises(AuthenticationError):
                await client.get_products()

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, client):
        """Test rate limit handling with retry."""
        api_response = {"products": []}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()

            # First call: 429 rate limit, then success
            mock_client.request = AsyncMock(
                side_effect=[
                    self._create_mock_response(429),
                    self._create_mock_response(200, api_response)
                ]
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_products()
            assert result == api_response
            assert mock_client.request.call_count == 2

PRODUCTS_PAYLOAD = {"_links": {"data-analysis": {"_links": {
    "sdtmig": [
        {"href": "/mdr/sdtmig/3-3", "title": "SDTMIG 3.3"},
        {"href": "/mdr/sdtmig/3-4", "title": "SDTMIG 3.4"},
        {"href": "/mdr/sdtmig/3-1-3", "title": "SDTMIG 3.1.3"},
        {"href": "/mdr/sdtmig/ap-1-0", "title": "SDTMIG AP"},
        {"href": "/mdr/sdtmig/md-1-1", "title": "SDTMIG MD"},
    ],
    "sdtm": [
        {"href": "/mdr/sdtm/1-8", "title": "SDTM 1.8"},
        {"href": "/mdr/sdtm/2-0", "title": "SDTM 2.0"},
    ],
    "adam": [
        {"href": "/mdr/adam/adam-2-1", "title": "ADaM 2.1"},
        {"href": "/mdr/adam/adamig-1-2", "title": "ADaMIG 1.2"},
        {"href": "/mdr/adam/adamig-1-3", "title": "ADaMIG 1.3"},
        {"href": "/mdr/adam/adam-tte-1-0", "title": "ADaM TTE"},
    ],
}}}}


class TestLatestVersionResolution:
    """version='latest' resolves against the cached product list."""

    @pytest.fixture
    def client(self, tmp_path):
        config = CDISCConfig(
            api_key="test-api-key", cache_dir=str(tmp_path), request_timeout=30
        )
        cache = CacheManager(str(tmp_path))
        cache.set("products", PRODUCTS_PAYLOAD)
        return CDISCClient(config, cache)

    async def test_latest_ignores_non_numeric_sibling_igs(self, client):
        assert await client._resolve_version("sdtmig", "latest") == "3-4"

    async def test_latest_prefers_numeric_order_over_string_order(self, client):
        # string sort would put "1-8" after "2-0"? no: "2-0" > "1-8" either way;
        # but "3-1-3" > "3-4" as strings — tuple compare must win
        assert await client._resolve_version("sdtmig", "LATEST") == "3-4"
        assert await client._resolve_version("sdtm", "Latest") == "2-0"

    async def test_latest_for_adam_family(self, client):
        assert await client._resolve_version("adam", "latest") == "2-1"
        assert await client._resolve_version("adamig", "latest") == "1-3"

    async def test_explicit_version_passes_through_normalized(self, client):
        assert await client._resolve_version("sdtmig", "3.4") == "3-4"

    async def test_unknown_standard_raises_friendly_error(self, client):
        from cdisc_mcp.utils.errors import ResourceNotFoundError

        with pytest.raises(ResourceNotFoundError):
            await client._resolve_version("nosuchstd", "latest")

    async def test_get_standard_latest_hits_resolved_url(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"name": "SDTMIG"}
            mock_client.request = AsyncMock(return_value=response)
            mock_httpx.return_value.__aenter__.return_value = mock_client

            await client.get_standard("sdtmig", "latest")
            assert mock_client.request.call_args[0][1] == (
                "https://library.cdisc.org/api/mdr/sdtmig/3-4"
            )
        # resolved version, not the alias, is what lands in the cache key
        assert client.cache.get("standards/sdtmig/3-4") == {"name": "SDTMIG"}


TERMS_PAYLOAD = {
    "_links": {
        "self": {"href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C667/terms"},
        "terms": [
            {
                "href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C667/terms/C201971",
                "title": "Male",
                "type": "Code List Value",
            },
            {
                "href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C667/terms/C201972",
                "title": "Female",
                "type": "Code List Value",
            },
        ],
    },
    "name": "Sex",
}


class TestGetTermByName:
    """get_term accepts a term name in addition to a C-code."""

    @pytest.fixture
    def client(self, tmp_path):
        config = CDISCConfig(
            api_key="test-api-key", cache_dir=str(tmp_path), request_timeout=30
        )
        cache = CacheManager(str(tmp_path))
        cache.set(
            "ct/packages/sdtmct-2024-03-29/codelists/C667/terms", TERMS_PAYLOAD
        )
        return CDISCClient(config, cache)

    async def test_c_code_passes_through(self, client):
        assert await client._resolve_term_code(
            "sdtmct-2024-03-29", "C667", "c201972"
        ) == "C201972"

    async def test_name_resolves_case_insensitively(self, client):
        assert await client._resolve_term_code(
            "sdtmct-2024-03-29", "C667", "female"
        ) == "C201972"

    async def test_unknown_name_raises_with_close_matches(self, client):
        from cdisc_mcp.utils.errors import ResourceNotFoundError

        with pytest.raises(ResourceNotFoundError) as exc:
            await client._resolve_term_code("sdtmct-2024-03-29", "C667", "Femal")
        assert "Female" in str(exc.value.message)

    async def test_get_term_by_name_fetches_resolved_code_url(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"submissionValue": "F"}
            mock_client.request = AsyncMock(return_value=response)
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.get_term("SDTMCT-2024-03-29", "C667", "Female")
            assert result == {"submissionValue": "F"}
            assert mock_client.request.call_args[0][1].endswith(
                "/ct/packages/sdtmct-2024-03-29/codelists/C667/terms/C201972"
            )
        # cached under the resolved code, not the name
        assert client.cache.get(
            "ct/packages/sdtmct-2024-03-29/codelists/C667/terms/C201972"
        ) == {"submissionValue": "F"}
