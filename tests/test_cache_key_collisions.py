"""Regression tests for cache key → file path collisions.

Bug (0.1.4): CacheManager._get_cache_file_path() used only the first two path
segments of a cache key, so every deeper key sharing the same first two
segments collapsed onto one file, e.g.

    ct/packages                          -> ct/packages.json
    ct/packages/{package}                -> ct/packages.json   (same file!)
    ct/packages/{package}/codelists      -> ct/packages.json   (same file!)

metadata.json tracked them as distinct keys, so a cached read for tool A could
return the payload last written by tool B. Same class of collision affected
standards/*, datasets/* and compare/* keys (14 of 15 tools).
"""

import json
import time
import pytest
from cdisc_mcp.cache import CacheManager

# Representative keys for every shape produced by client.py.
CLIENT_KEYS = [
    "products",
    "standards/sdtm/2-1",
    "standards/sdtm/2-1/classes",
    "standards/adam/2-1",
    "standards/adam/2-1/classes",
    "datasets/sdtmig/3-4",
    "datasets/sdtmig/3-4/DM",
    "datasets/sdtmig/3-4/DM/variables",
    "datasets/sdtmig/3-4/DM/variables/USUBJID",
    "datasets/adamig/1-3",
    "datasets/adamig/1-3/ADSL",
    "datasets/adamig/1-3/ADSL/variables",
    "datasets/adamig/1-3/ADSL/variables/AGE",
    "ct/packages",
    "ct/packages/sdtmct-2026-09-25",
    "ct/packages/sdtmct-2026-09-25/codelists",
    "ct/packages/sdtmct-2026-09-25/codelists/C667",
    "ct/packages/sdtmct-2026-09-25/codelists/C667/terms",
    "ct/packages/sdtmct-2026-09-25/codelists/C667/terms/C174106",
    "ct/packages/adamct-2024-03-29",
    "ct/packages/adamct-2024-03-29/codelists",
    "compare/sdtm/2-0/2-1",
    "compare/sdtm/2-1/2-2",
    "compare/sdtmig/3-4/3-5",
    "compare/adam/2-1/2-2",
]


class TestKeyPathUniqueness:
    def test_every_client_key_maps_to_its_own_file(self, tmp_path):
        """No two distinct cache keys may share a file (the 0.1.4 bug)."""
        cache = CacheManager(str(tmp_path))
        paths = [cache._get_cache_file_path(k) for k in CLIENT_KEYS]
        dupes = len(paths) - len(set(paths))
        assert dupes == 0, f"{dupes} key(s) collapse onto the same cache file"

    def test_paths_stay_under_cache_dir_and_readable(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        for key in CLIENT_KEYS:
            p = cache._get_cache_file_path(key)
            assert cache.cache_dir in p.parents, p
            assert p.name.endswith(".json")
            assert len(str(p)) < 260, f"path too long for Windows: {p}"
            if "/" in key:
                # first segment still used as a folder, so the tree stays browsable
                assert p.parent.name == key.split("/")[0], p


class TestCrossTalk:
    """The user-visible symptom: a cached read returning another tool's payload."""

    def test_ct_family_does_not_cross_talk(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        payloads = {
            "ct/packages": {"role": "package-list"},
            "ct/packages/sdtmct-2026-09-25": {"role": "package-detail"},
            "ct/packages/sdtmct-2026-09-25/codelists": {"role": "codelist-list"},
            "ct/packages/sdtmct-2026-09-25/codelists/C667": {"role": "codelist"},
            "ct/packages/sdtmct-2026-09-25/codelists/C667/terms": {"role": "term-list"},
            "ct/packages/sdtmct-2026-09-25/codelists/C667/terms/C174106": {"role": "term"},
        }
        for key, value in payloads.items():
            cache.set(key, value)

        # A second instance (i.e. the next server process) must read back each
        # key's own payload, not whatever was written last.
        reopened = CacheManager(str(tmp_path))
        for key, value in payloads.items():
            assert reopened.get(key) == value, f"{key} returned the wrong payload"

    def test_datasets_and_standards_and_compare_families(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        families = {
            "standards/sdtm/2-1": "std",
            "standards/sdtm/2-1/classes": "classes",
            "datasets/sdtmig/3-4": "ds",
            "datasets/sdtmig/3-4/DM": "dm",
            "datasets/sdtmig/3-4/DM/variables": "vars",
            "datasets/sdtmig/3-4/DM/variables/USUBJID": "var",
            "compare/sdtm/2-0/2-1": "diff-a",
            "compare/sdtm/2-1/2-2": "diff-b",
        }
        for key, tag in families.items():
            cache.set(key, {"tag": tag})
        reopened = CacheManager(str(tmp_path))
        for key, tag in families.items():
            assert reopened.get(key) == {"tag": tag}, key

    def test_deleting_one_entry_keeps_siblings_intact(self, tmp_path):
        """0.1.4 also unlinked the shared file, wiping sibling entries' data."""
        cache = CacheManager(str(tmp_path))
        cache.set("ct/packages", {"tag": "list"})
        cache.set("ct/packages/sdtmct-2026-09-25", {"tag": "detail"})

        cache.delete("ct/packages/sdtmct-2026-09-25")

        assert cache.get("ct/packages") == {"tag": "list"}
        assert cache.get("ct/packages/sdtmct-2026-09-25") is None


class TestKeySanitising:
    def test_keys_with_filesystem_unsafe_chars_round_trip(self, tmp_path):
        """CDISC package ids may contain '|' and ':' (e.g. cdtp|sdtm|2025-03)."""
        cache = CacheManager(str(tmp_path))
        for key in [
            "ct/packages/cdtp|sdtm|2025-03",
            "ct/packages/cdtp|sdtm|2025-03/codelists/C667",
            "ct/packages/ADaM:2024",
        ]:
            cache.set(key, {"key": key})
            assert cache.get(key) == {"key": key}

    def test_distinct_keys_similar_after_sanitising_stay_distinct(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        a = "ct/packages/pkg|1/codelists/C667"
        b = "ct/packages/pkg_1/codelists/C667"
        cache.set(a, {"which": "a"})
        cache.set(b, {"which": "b"})
        assert cache.get(a) == {"which": "a"}
        assert cache.get(b) == {"which": "b"}

    def test_long_key_does_not_exceed_windows_path_limit(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        key = "ct/packages/" + ("x" * 400) + "/codelists/C667"
        p = cache._get_cache_file_path(key)
        assert len(str(p)) < 260
        cache.set(key, {"ok": True})
        assert cache.get(key) == {"ok": True}


class TestOldCacheHandling:
    def test_pre_fix_cache_layout_is_ignored_not_misread(self, tmp_path):
        """A 0.1.4 cache dir must not be interpreted as valid data."""
        legacy_dir = tmp_path / "cache"
        (legacy_dir / "ct").mkdir(parents=True)
        (legacy_dir / "ct" / "packages.json").write_text(
            json.dumps({"stale": "from 0.1.4"}), encoding="utf-8"
        )
        (legacy_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "ct/packages": {
                        "created_at": time.time(),
                        "ttl": 10**12,
                        "file": "ct/packages.json",
                    },
                }
            ),
            encoding="utf-8",
        )

        cache = CacheManager(str(legacy_dir))
        assert cache.get("ct/packages") is None

    def test_write_is_atomic_no_temp_files_left(self, tmp_path):
        cache = CacheManager(str(tmp_path))
        cache.set("standards/sdtm/2-1", {"big": "x" * 1000})
        leftovers = [p.name for p in tmp_path.rglob("*") if p.is_file() and p.suffix != ".json"]
        assert leftovers == []
