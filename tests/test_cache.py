"""Tests for CDISC MCP cache management."""

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
        cache = CacheManager(str(tmp_path), default_ttl=1)

        data = {"test": "data"}
        cache.set("test_key", data, ttl=1)

        result = cache.get("test_key")
        assert result == data

        time.sleep(2)

        result = cache.get("test_key")
        assert result is None

    def test_cache_delete(self, tmp_path):
        """Test deleting cache data."""
        cache = CacheManager(str(tmp_path))

        data = {"test": "data"}
        cache.set("test_key", data)

        assert cache.get("test_key") == data

        cache.delete("test_key")

        assert cache.get("test_key") is None

    def test_cache_clear_expired(self, tmp_path):
        """Test clearing expired cache entries."""
        cache = CacheManager(str(tmp_path), default_ttl=1)

        cache.set("short_1", {"data": 1}, ttl=1)
        cache.set("short_2", {"data": 2}, ttl=1)
        cache.set("long", {"data": 3}, ttl=3600)

        time.sleep(2)

        cleared = cache.clear_expired()
        assert cleared == 2

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

        cache.set("products", {"products": []})
        cache.set("standards/sdtm_1-8", {"name": "SDTM"})

        assert (tmp_path / "products.json").exists()

    def test_cache_metadata_tracking(self, tmp_path):
        """Test cache metadata tracking."""
        cache = CacheManager(str(tmp_path))

        data = {"test": "data"}
        cache.set("test_key", data, ttl=100)

        assert cache.metadata_file.exists()

        with open(cache.metadata_file) as f:
            metadata = json.load(f)

        assert "test_key" in metadata
        assert "created_at" in metadata["test_key"]
        assert "ttl" in metadata["test_key"]