"""Tests for the ADaM data structure endpoints and the ADaM datasets-path guard.

Background: the Library API has no ``/datasets`` segment under ``/mdr/adam/``
(verified live), so every ADaM question routed through the dataset tools was a
guaranteed 404, and 0.1.8 shipped no tool at all for ``/datastructures``. These
tests pin the six endpoints' URL shape, the name-resolution rules that the API's
case-sensitive href tails require (``SITEGRy``, ``APHASEw``), the payload
compaction that keeps an ADSL variable list out of the hypermedia tree, and the
"this tool cannot work here" message that replaces the bare 404.
"""

import pytest
from unittest.mock import MagicMock

from cdisc_mcp.cache import CacheManager
from cdisc_mcp.client import CDISCClient
from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.utils.errors import ResourceNotFoundError


BASE = "https://library.cdisc.org/api/mdr/adam/adamig-1-3"

DS_LISTING = {
    "_links": {
        "self": {"href": f"{BASE}/datastructures", "title": "ADaMIG 1.3"},
        "dataStructures": [
            {
                "href": f"{BASE}/datastructures/ADSL",
                "title": "Subject-Level Analysis Dataset Structure",
                "type": "Data Structure",
            },
            {
                "href": f"{BASE}/datastructures/BDS",
                "title": "Basic Data Structure",
                "type": "Data Structure",
            },
        ],
    },
    "name": "ADaMIG v1.3",
    "version": "1-3",
}

ADSL = {
    "name": "ADSL",
    "label": "Subject-Level Analysis Dataset Structure",
    "description": "One record per subject.",
    "class": "SUBJECT LEVEL ANALYSIS DATASET",
    "_links": {"self": {"href": f"{BASE}/datastructures/ADSL"}},
    "analysisVariableSets": [
        {
            "name": "Identifier",
            "label": "ADSL Identifier",
            "analysisVariables": [
                {
                    "name": "STUDYID",
                    "label": "Study Identifier",
                    "core": "Req",
                    "simpleDatatype": "Char",
                    "description": "DM.STUDYID",
                    "_links": {"self": {"href": f"{BASE}/datastructures/ADSL/variables/STUDYID"}},
                },
                {
                    "name": "SITEGRy",
                    "label": "Pooled Site Group y",
                    "core": "Perm",
                    "simpleDatatype": "Char",
                    "description": "Pooling of site identifier",
                },
            ],
        },
        {
            "name": "SubjectDemographics",
            "label": "ADSL Subject Demographics",
            "analysisVariables": [
                {
                    "name": "AGE",
                    "label": "Age",
                    "core": "Req",
                    "simpleDatatype": "Num",
                    "description": "DM.AGE",
                }
            ],
        },
        {"name": "Empty", "label": "ADSL Empty", "analysisVariables": []},
    ],
}

VARIABLES_LIST = {
    "name": "ADSL",
    "class": "SUBJECT LEVEL ANALYSIS DATASET",
    "_links": {
        "self": {"href": f"{BASE}/datastructures/ADSL/variables"},
        "analysisVariables": [
            {
                "href": f"{BASE}/datastructures/ADSL/variables/STUDYID",
                "title": "Study Identifier",
                "type": "Analysis Variable",
            },
            {
                "href": f"{BASE}/datastructures/ADSL/variables/SITEGRy",
                "title": "Pooled Site Group y",
                "type": "Analysis Variable",
            },
            {
                "href": f"{BASE}/datastructures/ADSL/variables/AGE",
                "title": "Age",
                "type": "Analysis Variable",
            },
            {
                "href": f"{BASE}/datastructures/ADSL/variables/AGEU",
                "title": "Age Units",
                "type": "Analysis Variable",
            },
        ],
    },
}

VARSETS_LIST = {
    "name": "ADSL",
    "_links": {
        "self": {"href": f"{BASE}/datastructures/ADSL/varsets"},
        "analysisVariableSets": [
            {
                "href": f"{BASE}/datastructures/ADSL/varsets/Identifier",
                "title": "ADSL Identifier",
                "type": "Variable Set",
            },
            {
                "href": f"{BASE}/datastructures/ADSL/varsets/SubjectDemographics",
                "title": "ADSL Subject Demographics",
                "type": "Variable Set",
            },
        ],
    },
}

VARSET_DETAIL = {
    "name": "SubjectDemographics",
    "label": "ADSL Subject Demographics",
    "ordinal": "2",
    "_links": {
        "self": {"href": f"{BASE}/datastructures/ADSL/varsets/SubjectDemographics"},
        "parentDatastructure": {"href": f"{BASE}/datastructures/ADSL"},
    },
    "analysisVariables": [
        {
            "name": "AGE",
            "label": "Age",
            "core": "Req",
            "simpleDatatype": "Num",
            "description": "DM.AGE. Age at enrollment.",
            "_links": {"self": {"href": f"{BASE}/datastructures/ADSL/variables/AGE"}},
        }
    ],
}

AGE_DETAIL = {
    "name": "AGE",
    "label": "Age",
    "core": "Req",
    "simpleDatatype": "Num",
    "description": "DM.AGE",
    "_links": {"self": {"href": f"{BASE}/datastructures/ADSL/variables/AGE"}},
}

# /mdr/products is a pure hypermedia payload: groups of {href, title, type}.
# _latest_version reads the single-segment tails under /mdr/adam/, so the hrefs
# must be API-relative exactly as the service returns them.
PRODUCTS = {
    "_links": {
        "data-analysis": [
            {"href": "/mdr/adam/adamig-1-3", "title": "ADaMIG v1.3",
             "type": "Implementation Guide"},
            {"href": "/mdr/adam/adam-2-1", "title": "ADaM v2.1", "type": "Standard"},
            {"href": "/mdr/sdtmig/3-4", "title": "SDTMIG 3-4",
             "type": "Implementation Guide"},
        ]
    }
}


def make_client(tmp_path):
    config = CDISCConfig(
        api_key="test-api-key", cache_dir=str(tmp_path), request_timeout=30
    )
    return CDISCClient(config, CacheManager(str(tmp_path)))


def route(client, responses):
    """Serve ``responses`` (exact URL -> payload) and record every URL asked for.

    ``_request_with_retry`` hands back the *parsed* JSON, so the fake returns the
    payload dict directly. An unexpected URL fails the test on the spot instead of
    answering with a mock that surfaces later as a confusing assertion about some
    other field. A value that is already an Exception is raised, which is how a 404
    is simulated (the real method maps status codes onto these error types).
    """
    asked = []

    async def _fake(method, url, **kwargs):
        asked.append(url)
        if url not in responses:
            raise AssertionError(f"unexpected request: {url}")
        value = responses[url]
        if isinstance(value, Exception):
            raise value
        return value

    client._request_with_retry = _fake
    return asked


@pytest.fixture
def adamig(tmp_path):
    """An ADaMIG v1.3 client with every endpoint's payload routed."""
    client = make_client(tmp_path)
    asked = route(client, {
        f"{BASE}/datastructures": DS_LISTING,
        f"{BASE}/datastructures/ADSL": ADSL,
        f"{BASE}/datastructures/ADSL/variables": VARIABLES_LIST,
        f"{BASE}/datastructures/ADSL/variables/AGE": AGE_DETAIL,
        f"{BASE}/datastructures/ADSL/variables/SITEGRy": {**AGE_DETAIL, "name": "SITEGRy"},
        f"{BASE}/datastructures/ADSL/varsets": VARSETS_LIST,
        f"{BASE}/datastructures/ADSL/varsets/SubjectDemographics": VARSET_DETAIL,
        f"{BASE}/datastructures/ADSL/varsets/Identifier": {
            **VARSET_DETAIL, "name": "Identifier", "label": "ADSL Identifier"
        },
        "https://library.cdisc.org/api/mdr/products": PRODUCTS,
    })
    return client, asked


class TestUrlShape:
    def test_datastructure_url_adamig(self, tmp_path):
        client = make_client(tmp_path)
        assert client._build_datastructure_url("adamig", "1-3") == f"{BASE}/datastructures"
        assert client._build_datastructure_url("adamig", "1-3", "ADSL", "variables") == (
            f"{BASE}/datastructures/ADSL/variables"
        )

    def test_datastructure_url_adam_base_model(self, tmp_path):
        client = make_client(tmp_path)
        assert client._build_datastructure_url("adam", "2-1", "ADSL") == (
            "https://library.cdisc.org/api/mdr/adam/adam-2-1/datastructures/ADSL"
        )


class TestGetDatastructures:
    async def test_lists_exact_names_and_template(self, adamig):
        client, _ = adamig
        result = await client.get_datastructures("adamig", "1-3")
        assert result["count"] == 2
        assert [d["name"] for d in result["datastructures"]] == ["ADSL", "BDS"]
        assert result["datastructures"][0]["label"] == (
            "Subject-Level Analysis Dataset Structure"
        )
        assert result["hrefTemplate"] == f"{BASE}/datastructures/{{name}}"
        # The per-item href is replaced by the template, not repeated per row.
        assert "href" not in result["datastructures"][0]

    async def test_raw_returns_api_payload(self, adamig):
        client, _ = adamig
        assert await client.get_datastructures("adamig", "1-3", raw=True) == DS_LISTING

    async def test_latest_resolves_before_the_request(self, adamig):
        client, asked = adamig
        await client.get_datastructures("adamig", "latest")
        assert f"{BASE}/datastructures" in asked

    async def test_result_is_cached(self, adamig):
        client, asked = adamig
        await client.get_datastructure("adamig", "1-3", "ADSL")
        first = len(asked)
        await client.get_datastructure("adamig", "1-3", "ADSL")
        assert len(asked) == first, "second call re-requested a cached payload"


class TestGetDatastructure:
    async def test_compact_table_drops_descriptions_and_links(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure("adamig", "1-3", "ADSL")
        assert result["totalVariables"] == 3
        assert result["variableSetCount"] == 2, "empty variable set must not be listed"
        assert [s["varset"] for s in result["variableSets"]] == [
            "Identifier", "SubjectDemographics"
        ]
        first = result["variableSets"][0]["variables"][0]
        assert set(first) == {"name", "label", "core", "datatype"}
        assert "description" not in first
        assert result["datastructure"] == "ADSL"

    async def test_raw_returns_whole_payload(self, adamig):
        client, _ = adamig
        assert await client.get_datastructure("adamig", "1-3", "ADSL", raw=True) == ADSL

    async def test_name_is_case_insensitive(self, adamig):
        client, asked = adamig
        result = await client.get_datastructure("adamig", "1-3", "adsl")
        assert result["datastructure"] == "ADSL"
        assert f"{BASE}/datastructures/ADSL" in asked

    async def test_unknown_name_lists_available_without_requesting(self, adamig):
        client, asked = adamig
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.get_datastructure("adamig", "1-3", "ADAE")
        assert "ADSL" in exc.value.message and "BDS" in exc.value.message
        assert not any("/datastructures/ADAE" in url for url in asked)

    async def test_unlisted_product_passes_name_through_and_explains_404(self, tmp_path):
        """ADaM v2.1's datastructures endpoint lists nothing, so a name cannot be checked.

        The point of the enriched message is that a bare URL 404 reads like a typo
        in the caller's name rather than a product that has no list to consult.
        """
        client = make_client(tmp_path)
        listing = "https://library.cdisc.org/api/mdr/adam/adam-2-1/datastructures"
        child = f"{listing}/ADSL"
        asked = route(client, {
            listing: {
                "_links": {"self": {"href": "/mdr/adam/adam-2-1/datastructures"}},
                "name": "ADaM v2.1",
            },
            child: ResourceNotFoundError(
                message=f"📄 未找到资源: {child}", resource_type="url", resource_id=child
            ),
        })
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.get_datastructure("adam", "2-1", "ADSL")
        assert "没有列出任何数据结构" in exc.value.message
        assert "adamig" in exc.value.message
        assert not exc.value.message.startswith("🧭 📄"), "double emoji leak"
        assert asked == [listing, child]


class TestVariablesListEndpoint:
    async def test_rows_keep_exact_case_and_no_type_noise(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_variables("adamig", "1-3", "ADSL")
        assert result["count"] == 4
        assert [v["name"] for v in result["variables"]] == [
            "STUDYID", "SITEGRy", "AGE", "AGEU"
        ]
        assert set(result["variables"][0]) == {"name", "label"}
        assert result["hrefTemplate"] == f"{BASE}/datastructures/ADSL/variables/{{name}}"

    async def test_raw_returns_api_payload(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_variables(
            "adamig", "1-3", "ADSL", raw=True
        )
        assert result == VARIABLES_LIST


class TestVariableDetail:
    async def test_mixed_case_pattern_variable_is_recovered(self, adamig):
        """The API path is case-sensitive and ADaM names mix case on purpose."""
        client, asked = adamig
        result = await client.get_datastructure_variable(
            "adamig", "1-3", "ADSL", "sitegry"
        )
        assert result["name"] == "SITEGRy"
        assert f"{BASE}/datastructures/ADSL/variables/SITEGRy" in asked
        assert not any("SITEGRY" in url for url in asked)

    async def test_known_variable(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_variable("adamig", "1-3", "ADSL", "AGE")
        assert result["core"] == "Req"

    async def test_unknown_variable_suggests_close_names(self, adamig):
        client, asked = adamig
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.get_datastructure_variable("adamig", "1-3", "ADSL", "AGEUUX")
        assert "AGEU" in exc.value.message
        assert not any("variables/AGEUUX" in url for url in asked)


class TestVarsets:
    async def test_varsets_listing(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_varsets("adamig", "1-3", "ADSL")
        assert [v["name"] for v in result["variableSets"]] == [
            "Identifier", "SubjectDemographics"
        ]

    async def test_slug_and_display_name_both_resolve(self, adamig):
        client, asked = adamig
        for spelling in ("SubjectDemographics", "subject demographics",
                         "ADSL Subject Demographics", "subjectdemographics"):
            result = await client.get_datastructure_varset(
                "adamig", "1-3", "ADSL", spelling
            )
            assert result["varset"] == "SubjectDemographics", spelling
        assert asked.count(
            f"{BASE}/datastructures/ADSL/varsets/SubjectDemographics"
        ) == 1, "resolved through the cache, one request for all spellings"

    async def test_detail_keeps_variable_descriptions(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_varset(
            "adamig", "1-3", "ADSL", "SubjectDemographics"
        )
        assert result["count"] == 1
        row = result["variables"][0]
        assert row["description"] == "DM.AGE. Age at enrollment."
        assert row["datatype"] == "Num"
        assert result["datastructure"] == "ADSL"

    async def test_raw_returns_api_payload(self, adamig):
        client, _ = adamig
        result = await client.get_datastructure_varset(
            "adamig", "1-3", "ADSL", "SubjectDemographics", raw=True
        )
        assert result == VARSET_DETAIL

    async def test_unknown_varset_lists_available(self, adamig):
        client, _ = adamig
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.get_datastructure_varset("adamig", "1-3", "ADSL", "Demographic")
        assert "Identifier" in exc.value.message


class TestAdamDatasetsGuard:
    """The dataset tools cannot answer an ADaM question at all — say so locally."""

    @pytest.mark.parametrize(
        "method,args,replacement",
        [
            ("get_datasets", ("adamig", "1-3"), "get_datastructures"),
            ("get_dataset", ("adamig", "1-3", "ADSL"), "get_datastructure"),
            (
                "get_dataset_variables",
                ("adamig", "1-3", "ADSL"),
                "get_datastructure_variables",
            ),
            (
                "get_variable",
                ("adamig", "1-3", "ADSL", "AGE"),
                "get_datastructure_variable",
            ),
        ],
    )
    async def test_adam_family_raises_without_requesting(self, tmp_path, method, args,
                                                        replacement):
        client = make_client(tmp_path)
        asked = route(client, {})
        with pytest.raises(ResourceNotFoundError) as exc:
            await getattr(client, method)(*args)
        assert replacement in exc.value.message
        assert "datasets" in exc.value.message
        assert asked == [], "a doomed /datasets request was still sent"

    async def test_latest_is_resolved_before_the_guard(self, tmp_path):
        """The message quotes a concrete version, so 'latest' must be resolved first."""
        client = make_client(tmp_path)
        route(client, {"https://library.cdisc.org/api/mdr/products": PRODUCTS})
        with pytest.raises(ResourceNotFoundError) as exc:
            await client.get_dataset_variables("adamig", "latest", "ADSL")
        assert "1-3" in exc.value.message

    async def test_sdtmig_still_uses_the_datasets_path(self, tmp_path):
        client = make_client(tmp_path)
        asked = route(client, {
            "https://library.cdisc.org/api/mdr/sdtmig/3-4/datasets/DM/variables": {
                "name": "DM"
            }
        })
        await client.get_dataset_variables("sdtmig", "3-4", "DM")
        assert asked == [
            "https://library.cdisc.org/api/mdr/sdtmig/3-4/datasets/DM/variables"
        ]


class TestToolWiring:
    """The dispatch layer must reach the client methods with the caller's arguments."""

    async def test_six_tools_registered(self):
        from cdisc_mcp.tools import ALL_TOOLS

        tools = {t.name: t for t in ALL_TOOLS}
        expected = {
            "get_datastructures",
            "get_datastructure",
            "get_datastructure_variables",
            "get_datastructure_variable",
            "get_datastructure_varsets",
            "get_datastructure_varset",
        }
        assert expected <= set(tools), sorted(set(tools) ^ expected)
        assert len(tools) == len(ALL_TOOLS) == 21
        for name in expected:
            schema = tools[name].inputSchema
            assert "raw" in schema["properties"], name
            assert "datastructure" in schema["properties"] or name == "get_datastructures"

    @pytest.mark.parametrize(
        "tool_name,client_method,arguments",
        [
            ("get_datastructures", "get_datastructures",
             {"standard": "adamig", "version": "1-3"}),
            ("get_datastructure", "get_datastructure",
             {"standard": "adamig", "version": "1-3", "datastructure": "ADSL"}),
            ("get_datastructure_variables", "get_datastructure_variables",
             {"standard": "adamig", "version": "1-3", "datastructure": "ADSL"}),
            ("get_datastructure_variable", "get_datastructure_variable",
             {"standard": "adamig", "version": "1-3", "datastructure": "ADSL",
              "variable": "AGE"}),
            ("get_datastructure_varsets", "get_datastructure_varsets",
             {"standard": "adamig", "version": "1-3", "datastructure": "ADSL"}),
            ("get_datastructure_varset", "get_datastructure_varset",
             {"standard": "adamig", "version": "1-3", "datastructure": "ADSL",
              "varset": "Identifier"}),
        ],
    )
    async def test_dispatch_forwards_arguments(self, tool_name, client_method,
                                              arguments):
        """The tool layer must reach the client with the caller's positional order.

        A wrong order here reads as "ADSL has no variable AGE", so the shape of
        the forwarded call is worth pinning even though the client itself is tested.
        """
        from cdisc_mcp.tools import _execute_tool

        seen = {}

        async def spy(*args, **kwargs):
            seen["args"], seen["kwargs"] = args, kwargs
            return {"ok": True}

        client = MagicMock()
        setattr(client, client_method, spy)
        result = await _execute_tool(client, tool_name, dict(arguments), raw=False)
        assert result == {"ok": True}
        expected = [
            arguments["standard"], arguments["version"],
        ] + [v for k, v in arguments.items() if k in ("datastructure", "variable", "varset")]
        assert list(seen["args"]) == expected
        if client_method != "get_datastructure_variable":
            assert seen["kwargs"] == {"raw": False}

    async def test_dataset_tool_names_the_datastructure_tool_in_its_help(self):
        from cdisc_mcp.tools import ALL_TOOLS

        by_name = {t.name: t for t in ALL_TOOLS}
        for name in ("get_datasets", "get_dataset", "get_dataset_variables", "get_variable"):
            assert "get_datastructure" in by_name[name].description, name
