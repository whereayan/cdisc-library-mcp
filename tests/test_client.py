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
        assert client.base_url == "https://library.cdisc.org/api"

    def test_normalize_version_dot_to_dash(self, client):
        assert client._normalize_version("1.8") == "1-8"
        assert client._normalize_version("3.4") == "3-4"
        assert client._normalize_version("1-8") == "1-8"
        assert client._normalize_version("adamig-1.3") == "adamig-1-3"

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
        api_response = {"results": [{"name": "AE"}]}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.search("adverse event")
            assert result == api_response

    @pytest.mark.asyncio
    async def test_compare_versions(self, client):
        api_response = {"diff": {"added": [], "removed": []}}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(
                return_value=self._create_mock_response(200, api_response)
            )
            mock_httpx.return_value.__aenter__.return_value = mock_client

            result = await client.compare_versions("sdtm", "1-8", "1-7")
            assert result == api_response

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