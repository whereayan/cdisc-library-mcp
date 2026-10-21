"""Persistent cache management for CDISC MCP Server."""

import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

# Cache layout version, recorded inside metadata.json itself. Bumped whenever the
# key -> file mapping changes, so entries written by an older layout are ignored
# instead of being misread.
#   1 = <= 0.1.4  (buggy: only the first two key segments reached the path, so
#                  every deeper key sharing them collapsed onto one file)
#   2 = 0.1.5+    (bijective key -> file mapping)
CACHE_FORMAT_VERSION = 2

# Characters unsafe in file names on Windows (and awkward on POSIX).
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_BUCKET = 40
_MAX_STEM = 60
_DIGEST_LEN = 12


def _slug(text: str) -> str:
    """Filesystem-safe representation of a cache-key segment."""
    return _UNSAFE_CHARS.sub("_", text).strip("._") or "entry"


def cache_path_for(cache_dir: Path, key: str) -> Path:
    """Map a cache key onto a unique file path below cache_dir.

    Distinct keys always resolve to distinct files: the exact key is folded into
    a digest that is part of the file name, so keys that look alike after
    sanitising (``pkg|1`` vs ``pkg_1``), or different nesting levels that share
    the first two segments, can never overwrite each other.

    The key's first segment is kept as the sub-directory and a sanitised stem is
    kept in the file name so the cache tree stays browsable; the digest guards
    uniqueness and the length caps keep paths within Windows' MAX_PATH.
    """
    key = str(key).strip("/")
    if "/" in key:
        bucket, rest = key.split("/", 1)
        bucket = _slug(bucket)[:_MAX_BUCKET]
    else:
        bucket, rest = "misc", key
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:_DIGEST_LEN]
    return cache_dir / bucket / f"{_slug(rest)[:_MAX_STEM]}.{digest}.json"


class CacheManager:
    """Persistent file-based cache manager.

    Cache directory structure::

        ~/.cdisc-mcp/cache/
        ├── metadata.json    # {"format": 2, "entries": {key: {created_at, ttl, file}}}
        ├── misc/products.<digest>.json
        ├── standards/sdtm_2-1.<digest>.json
        ├── datasets/sdtmig_3-4_DM_variables.<digest>.json
        ├── ct/packages_sdtmct-2026-09-25_codelists.<digest>.json
        └── compare/...

    Entries written by an incompatible layout are ignored (served as a miss)
    rather than read, so a stale payload can never be returned for a key.
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
        self.metadata: dict[str, Any] = {}
        self._load_metadata()

    # ====================
    # Metadata (index)
    # ====================

    def _load_metadata(self) -> None:
        """Load cache entries, dropping anything from an incompatible layout."""
        if not self.metadata_file.exists():
            return
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        if not isinstance(loaded, dict):
            return
        if loaded.get("format") != CACHE_FORMAT_VERSION:
            # <= 0.1.4 index (flat dict of keys) or a newer layout we do not
            # understand: treat the directory as empty. Its data files are left
            # untouched, but can never be served.
            return
        entries = loaded.get("entries")
        if isinstance(entries, dict):
            self.metadata = entries

    def _save_metadata(self) -> None:
        """Save the index (layout version included) as one atomic write."""
        self._atomic_write_json(
            self.metadata_file,
            {"format": CACHE_FORMAT_VERSION, "entries": self.metadata},
        )

    @staticmethod
    def _atomic_write_json(path: Path, payload: Any) -> None:
        """Write JSON through a temp file + replace, so readers never see partial data."""
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    # ====================
    # Entry access
    # ====================

    def _get_cache_file_path(self, key: str) -> Path:
        """Get file path for cache key (one file per distinct key)."""
        return cache_path_for(self.cache_dir, key)

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached data if not expired."""
        entry_meta = self.metadata.get(key)
        if not entry_meta:
            return None

        created_at = entry_meta.get("created_at", 0)
        ttl = entry_meta.get("ttl", self.default_ttl)
        if time.time() - created_at > ttl:
            self._delete_entry(key)
            return None

        cache_file = self._get_cache_file_path(key)
        recorded = entry_meta.get("file")
        if recorded and recorded != cache_file.relative_to(self.cache_dir).as_posix():
            # Index and on-disk layout disagree: never serve this entry.
            self._delete_entry(key)
            return None
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
        self._atomic_write_json(cache_file, value)

        self.metadata[key] = {
            "created_at": time.time(),
            "ttl": ttl,
            "file": cache_file.relative_to(self.cache_dir).as_posix(),
        }
        self._save_metadata()

    def delete(self, key: str) -> None:
        """Delete cache data."""
        self._delete_entry(key)

    def _delete_entry(self, key: str) -> None:
        """Delete one cache entry and only its own file."""
        entry = self.metadata.pop(key, None)
        self._save_metadata()

        paths = {self._get_cache_file_path(key)}
        if isinstance(entry, dict) and entry.get("file"):
            paths.add(self.cache_dir / entry["file"])
        for path in paths:
            try:
                if path.is_file():
                    path.unlink()
            except OSError:
                pass

    # ====================
    # Maintenance
    # ====================

    def clear_expired(self) -> int:
        """Clear all expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self.metadata.items()
            if current_time - entry.get("created_at", 0) > entry.get("ttl", self.default_ttl)
        ]
        for key in expired_keys:
            self._delete_entry(key)
        return len(expired_keys)

    def clear_all(self) -> int:
        """Clear all cache entries."""
        count = len(self.metadata)
        for key in list(self.metadata.keys()):
            self._delete_entry(key)
        return count
