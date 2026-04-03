"""Persistent cache management for CDISC MCP Server."""

import json
import time
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """Persistent file-based cache manager.

    Cache directory structure:
        ~/.cdisc-mcp/cache/
        ├── products.json
        ├── standards/
        ├── datasets/
        ├── codelists/
        └── metadata.json
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
        """Get file path for cache key."""
        if "/" in key:
            parts = key.split("/")
            subdir = self.cache_dir / parts[0]
            subdir.mkdir(parents=True, exist_ok=True)
            return subdir / f"{parts[1]}.json"
        else:
            return self.cache_dir / f"{key}.json"

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached data if not expired."""
        if key not in self.metadata:
            return None

        entry_meta = self.metadata[key]
        created_at = entry_meta.get("created_at", 0)
        ttl = entry_meta.get("ttl", self.default_ttl)

        if time.time() - created_at > ttl:
            self._delete_entry(key)
            return None

        cache_file = self._get_cache_file_path(key)
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def set(self, key: str, value: dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set cache data with TTL."""
        ttl = ttl if ttl is not None else self.default_ttl

        cache_file = self._get_cache_file_path(key)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)

        self.metadata[key] = {
            "created_at": time.time(),
            "ttl": ttl,
            "file": str(cache_file.relative_to(self.cache_dir))
        }
        self._save_metadata()

    def delete(self, key: str) -> None:
        """Delete cache entry."""
        self._delete_entry(key)

    def _delete_entry(self, key: str) -> None:
        """Internal method to delete cache entry and its file."""
        if key in self.metadata:
            del self.metadata[key]
            self._save_metadata()

        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            cache_file.unlink()

    def clear_expired(self) -> int:
        """Clear all expired cache entries."""
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
        """Clear all cache entries."""
        count = len(self.metadata)

        for key in list(self.metadata.keys()):
            self._delete_entry(key)

        return count