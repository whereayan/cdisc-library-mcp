"""Tests for response slimming (utils/slim.py)."""

from cdisc_mcp.utils.slim import slim


class TestSlim:
    def test_drops_search_metadata_keys(self):
        payload = {
            "hits": [
                {
                    "@search.score": 37.1,
                    "@search.highlights": {"description": ["<em>AVAL</em>"]},
                    "name": "AVAL",
                    "label": "Analysis Value",
                }
            ]
        }
        result = slim(payload)
        hit = result["hits"][0]
        assert hit == {"name": "AVAL", "label": "Analysis Value"}

    def test_links_block_becomes_compact_refs(self):
        payload = {
            "name": "SEX",
            "_links": {
                "self": {"href": "/mdr/x/self"},
                "parentPackage": {
                    "href": "/mdr/ct/packages/p1",
                    "title": "Package One",
                    "type": "Terminology",
                },
            },
        }
        result = slim(payload)
        assert "_links" not in result
        # self is redundant; labelled links survive as label -> href
        assert result["refs"] == {"Package One": "/mdr/ct/packages/p1"}
        assert result["name"] == "SEX"

    def test_link_list_becomes_refs_by_linkname(self):
        payload = {
            "links": [
                {"href": "/mdr/a", "linkName": "parentDatastructure", "type": "Data Structure"},
                {"href": "/mdr/b", "linkName": "parentProduct", "type": "Product"},
            ]
        }
        result = slim(payload)
        assert result["refs"] == {
            "parentDatastructure": "/mdr/a",
            "parentProduct": "/mdr/b",
        }

    def test_duplicate_labels_are_deduplicated(self):
        payload = {
            "_links": {
                "a": {"href": "/1", "title": "Same"},
                "b": {"href": "/2", "title": "Same"},
            }
        }
        refs = slim(payload)["refs"]
        assert refs["Same"] == "/1"
        assert refs["Same-2"] == "/2"

    def test_nested_structures_are_recursed(self):
        payload = {
            "variables": [
                {"name": "USUBJID", "_links": {"codelist": {"href": "/mdr/ct/x", "title": "CT"}}},
                {"name": "AGE"},
            ]
        }
        result = slim(payload)
        assert result["variables"][0]["refs"] == {"CT": "/mdr/ct/x"}
        assert result["variables"][1] == {"name": "AGE"}

    def test_products_tree_flattens_to_title_refs(self):
        payload = {"_links": {"data-analysis": {"_links": {"adam": [
            {"href": "/mdr/adam/adam-2-1", "title": "ADaM 2.1", "type": "Foundational Model"},
        ]}}}}
        result = slim(payload)
        assert result["refs"] == {"ADaM 2.1": "/mdr/adam/adam-2-1"}

    def test_scalars_and_empty_containers_pass_through(self):
        assert slim(3) == 3
        assert slim("x") == "x"
        assert slim(None) is None
        assert slim([]) == []
        # no links -> no refs key injected
        assert slim({"a": 1}) == {"a": 1}

    def test_idempotent(self):
        payload = {"_links": {"x": {"href": "/1", "title": "T"}}, "a": [1, {"b": 2}]}
        once = slim(payload)
        assert slim(once) == once
