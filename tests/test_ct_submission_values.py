"""CT submission-value bulk access.

Background these tests pin down (measured against the live API, 2026-10-23):

* the codelist ``terms`` endpoint carries **no** per-term ``submissionValue``,
  and ``raw=true`` does not add one -- its ``_links.terms`` entries are only
  ``href``/``title``/``type``. The codelist-level ``submissionValue`` is the
  *variable* name (``LBTESTCD``), which is easy to mistake for a term value;
* the package payload inlines every term of every codelist **with**
  ``submissionValue`` (sdtmct-2024-03-29: 1106 codelists, 13.36 MB), so a whole
  table costs one request, not one per term;
* ``get_ct_package`` returning that payload untouched is what blew the 60 s
  timeout of MCP clients, so it is summarised by default.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cdisc_mcp.cache import CacheManager
from cdisc_mcp.client import (
    CDISCClient,
    build_ct_term_row,
    resolve_ct_fields,
    summarise_ct_package,
)
from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.utils.errors import ResourceNotFoundError, ValidationError

PKG = "sdtmct-2024-03-29"
CL = "C66731"
TERMS_KEY = f"ct/packages/{PKG}/codelists/{CL}/terms"
PKG_KEY = f"ct/packages/{PKG}"

# Exactly the shape the API returns: links, and no term-level submission values.
ROSTER = {
    "_links": {
        "self": {"href": f"/mdr/ct/packages/{PKG}/codelists/{CL}/terms"},
        "terms": [
            {
                "href": f"/mdr/ct/packages/{PKG}/codelists/{CL}/terms/C201971",
                "title": "Male",
                "type": "Code List Value",
            },
            {
                "href": f"/mdr/ct/packages/{PKG}/codelists/{CL}/terms/C201972",
                "title": "Female",
                "type": "Code List Value",
            },
            {
                "href": f"/mdr/ct/packages/{PKG}/codelists/{CL}/terms/C17865",
                "title": "Unknown",
                "type": "Code List Value",
            },
        ],
    },
    "conceptId": CL,
    "name": "Sex",
    "submissionValue": "SEX",
    "extensible": "false",
}

PACKAGE = {
    "name": "SDTM CT 2024-03-29",
    "label": "SDTM Controlled Terminology Package 57",
    "version": "2024-03-29",
    "effectiveDate": "2024-03-29",
    "registrationStatus": "Final",
    "description": "CDISC SDTM CT",
    "_links": {"self": {"href": f"/mdr/ct/packages/{PKG}"}},
    "codelists": [
        {
            "conceptId": CL,
            "name": "Sex",
            "submissionValue": "SEX",
            "extensible": "false",
            "terms": [
                {
                    "conceptId": "C201971",
                    "preferredTerm": "Male",
                    "submissionValue": "M",
                    "definition": "Male.",
                    "synonyms": ["Male"],
                },
                {
                    "conceptId": "C201972",
                    "preferredTerm": "Female",
                    "submissionValue": "F",
                    "definition": "Female.",
                    "synonyms": ["Female"],
                },
            ],
        },
        {
            "conceptId": "C65047",
            "name": "Laboratory Test Code",
            "submissionValue": "LBTESTCD",
            "terms": [{"conceptId": "C100429", "preferredTerm": "X", "submissionValue": "A1AGLP"}],
        },
    ],
}

MALE_DETAIL = {
    "conceptId": "C201971",
    "preferredTerm": "Male",
    "submissionValue": "M",
    "definition": "A person who belongs to the sex that normally produces sperm.",
    "synonyms": ["Male"],
}

DETAIL = {
    "C17865": {
        "conceptId": "C17865",
        "preferredTerm": "Unknown",
        "submissionValue": "U",
        "definition": "Unknown.",
        "synonyms": ["Unknown"],
    }
}


def make_client(tmp_path, seed=None):
    config = CDISCConfig(api_key="k", cache_dir=str(tmp_path), request_timeout=30)
    cache = CacheManager(str(tmp_path))
    for key, value in (seed or {}).items():
        cache.set(key, value)
    return CDISCClient(config, cache)


def mock_http(payload_by_suffix):
    """Patch httpx so each URL suffix returns its own payload; records calls."""
    calls = []

    def handler(method, url, **kwargs):
        calls.append(url)
        response = MagicMock()
        for suffix, payload in payload_by_suffix.items():
            if url.endswith(suffix):
                response.status_code = 200
                response.json.return_value = payload
                return response
        response.status_code = 404
        response.text = '{"statusCode":404}'
        return response

    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=lambda m, u, **kw: handler(m, u, **kw))
    ctx = MagicMock()
    ctx.__aenter__.return_value = mock_client
    return patch("httpx.AsyncClient", return_value=ctx), calls


# ---------------------------------------------------------------- pure helpers


class TestResolveFields:
    def test_defaults(self):
        assert resolve_ct_fields(None) == ("code", "name", "submissionValue")
        assert resolve_ct_fields([]) == ("code", "name", "submissionValue")

    def test_accepts_string_and_list_and_orders_canonically(self):
        assert resolve_ct_fields("synonyms,submissionValue") == (
            "submissionValue",
            "synonyms",
        )
        assert resolve_ct_fields(["name", "name"]) == ("name",)

    def test_rejects_unknown_with_legal_list(self):
        with pytest.raises(ValidationError) as exc:
            resolve_ct_fields(["submisionValue"])
        assert "submissionValue" in str(exc.value.message)

    def test_rejects_non_sequence(self):
        with pytest.raises(ValidationError):
            resolve_ct_fields(3)


class TestBuildRow:
    def test_prefers_api_values(self):
        row = build_ct_term_row(
            {"conceptId": "C201972", "preferredTerm": "Female", "submissionValue": "F"},
            "C999999", "Fallback Name", ("code", "name", "submissionValue"),
        )
        assert row == {"code": "C201972", "name": "Female", "submissionValue": "F"}

    def test_falls_back_to_link_when_term_missing(self):
        row = build_ct_term_row(None, "C1", "Some Term", ("code", "name", "submissionValue"))
        assert row["name"] == "Some Term"
        assert row["submissionValue"] is None

    def test_synonyms_default_to_empty_list(self):
        assert build_ct_term_row({}, "C1", "T", ("synonyms",)) == {"synonyms": []}


class TestSummarisePackage:
    def test_inline_terms_are_not_forwarded(self):
        out = summarise_ct_package(PACKAGE)
        blob = json.dumps(out, ensure_ascii=False)
        assert "A1AGLP" not in blob  # submission values stay server-side
        assert out["codelistCount"] == 2
        assert out["termCount"] == 3
        assert out["codelists"][0]["termCount"] == 2
        assert "terms" not in out["codelists"][0]

    def test_pagination_and_shrink_ratio(self):
        full = len(json.dumps(PACKAGE, ensure_ascii=False))
        page = summarise_ct_package(PACKAGE, offset=1, limit=1)
        assert page["offset"] == 1 and page["returned"] == 1
        assert page["hasMore"] is False
        assert page["codelists"][0]["conceptId"] == "C65047"
        assert len(json.dumps(page, ensure_ascii=False)) < full

    def test_limit_is_capped_and_request_echoed(self):
        out = summarise_ct_package(PACKAGE, limit=10 ** 6)
        assert out["limit"] == 2000
        assert out["limitRequested"] == 10 ** 6

    def test_points_at_the_replacement_tool(self):
        assert "get_codelist_submission_values" in summarise_ct_package(PACKAGE)["note"]


# ---------------------------------------------------------------- client tools


class TestGetCtPackageSummary:
    async def test_default_is_a_summary_not_13mb(self, tmp_path):
        client = make_client(tmp_path, {PKG_KEY: PACKAGE})
        out = await client.get_ct_package("SDTMCT-2024-03-29")
        assert out["version"] == "2024-03-29"
        assert out["codelistCount"] == 2

    async def test_raw_still_returns_the_whole_payload(self, tmp_path):
        client = make_client(tmp_path, {PKG_KEY: PACKAGE})
        out = await client.get_ct_package(PKG, raw=True)
        assert out == PACKAGE


class TestCodelistSubmissionValues:
    async def test_whole_table_needs_no_per_term_request(self, tmp_path):
        """The headline fix: roster + package payload, zero detail requests."""
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        http, calls = mock_http({})
        with http:
            # limit=2 keeps the page inside what the package payload inlines
            out = await client.get_codelist_submission_values(PKG, CL, limit=2)
        assert calls == []
        assert out["total"] == 3 and out["returned"] == 2
        assert out["terms"] == [
            {"code": "C201971", "name": "Male", "submissionValue": "M"},
            {"code": "C201972", "name": "Female", "submissionValue": "F"},
        ]
        assert out["valueSource"] == "package"
        assert out["termsResolvedByDetailRequest"] == 0
        assert out["codelistSubmissionValue"] == "SEX"
        assert out["codelistName"] == "Sex"

    async def test_missing_from_package_falls_back_to_detail(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        http, calls = mock_http({"/terms/C17865": DETAIL["C17865"]})
        with http:
            out = await client.get_codelist_submission_values(PKG, CL, limit=3)
        assert out["returned"] == 3
        assert out["terms"][2] == {"code": "C17865", "name": "Unknown", "submissionValue": "U"}
        assert out["valueSource"] == "package+term-detail"
        assert out["termsResolvedByDetailRequest"] == 1
        assert len(calls) == 1  # only the gap, not the whole page

    async def test_without_package_payload_every_term_is_a_detail_request(self, tmp_path):
        package_without_sex = {**PACKAGE, "codelists": [PACKAGE["codelists"][1]]}
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: package_without_sex})
        http, calls = mock_http(
            {f"/terms/{c}": DETAIL.get(c, {"conceptId": c}) for c in ("C17865", "C201971", "C201972")}
        )
        with http:
            out = await client.get_codelist_submission_values(PKG, CL, limit=1)
        assert out["valueSource"] == "term-detail"
        assert out["terms"][0]["submissionValue"] is None  # mock has no value
        assert out["total"] == 3

    async def test_pagination_walks_the_whole_roster(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        http, _ = mock_http({"/terms/C17865": DETAIL["C17865"]})
        with http:
            first = await client.get_codelist_submission_values(PKG, CL, limit=2)
            second = await client.get_codelist_submission_values(PKG, CL, offset=2, limit=2)
        assert first["hasMore"] is True and first["total"] == 3
        assert second["offset"] == 2 and second["hasMore"] is False
        assert [r["code"] for r in second["terms"]] == ["C17865"]

    async def test_oversized_limit_is_visible_not_silent(self, tmp_path):
        """2397 terms cannot fit one page; the clamp must be detectable.

        Without ``limitRequested`` a caller asking for the whole table gets 2000
        rows and no signal that its request was rewritten.
        """
        roster = {
            **ROSTER,
            "_links": {"terms": [
                {"href": f"/x/terms/C{i}", "title": f"T{i}"} for i in range(30)
            ]},
        }
        package = {"codelists": [{"conceptId": CL, "terms": [
            {"conceptId": f"C{i}", "preferredTerm": f"T{i}", "submissionValue": f"V{i}"}
            for i in range(30)
        ]}]}
        client = make_client(tmp_path, {TERMS_KEY: roster, PKG_KEY: package})
        out = await client.get_codelist_submission_values(PKG, CL, limit=10 ** 5)
        assert out["limitRequested"] == 10 ** 5
        assert out["limit"] == 2000
        assert out["total"] == 30 and out["returned"] == 30 and out["hasMore"] is False

    async def test_fields_select_columns(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        out = await client.get_codelist_submission_values(
            PKG, CL, fields="name,submissionValue,definition,synonyms"
        )
        assert out["fields"] == ["name", "submissionValue", "definition", "synonyms"]
        assert out["terms"][0] == {
            "name": "Male", "submissionValue": "M",
            "definition": "Male.", "synonyms": ["Male"],
        }

    async def test_raw_returns_every_api_field(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        out = await client.get_codelist_submission_values(PKG, CL, raw=True)
        assert out["terms"][0]["definition"] == "Male."

    async def test_duplicate_term_names_keep_one_row_each(self, tmp_path):
        """Enumeration comes from links, not from name-keyed slimmed refs."""
        roster = {
            **ROSTER,
            "_links": {"terms": [
                {"href": f"/x/terms/C1", "title": "Same Name"},
                {"href": f"/x/terms/C2", "title": "Same Name"},
            ]},
        }
        package = {
            "codelists": [{
                "conceptId": CL,
                "terms": [
                    {"conceptId": "C1", "preferredTerm": "Same Name", "submissionValue": "A"},
                    {"conceptId": "C2", "preferredTerm": "Same Name", "submissionValue": "B"},
                ],
            }]
        }
        client = make_client(tmp_path, {TERMS_KEY: roster, PKG_KEY: package})
        out = await client.get_codelist_submission_values(PKG, CL)
        assert [r["submissionValue"] for r in out["terms"]] == ["A", "B"]

    async def test_package_fetch_failure_degrades_to_detail_requests(self, tmp_path):
        """A failed 13 MB download must cost detail requests, not the table.

        The package payload is fetched with a single capped attempt, so on a slow
        link it can fail; the terms would otherwise have no submissionValue at all.
        """
        from cdisc_mcp.utils.errors import NetworkError

        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        real_fetch = client._fetch_json

        async def broken(cache_key, url, **kw):
            if cache_key.endswith(f"packages/{PKG}"):
                raise NetworkError(message="⏱️ 模拟整包下载超时")
            return await real_fetch(cache_key, url, **kw)

        client._fetch_json = broken
        by_detail = {**DETAIL, "C201971": MALE_DETAIL}
        http, calls = mock_http({f"/terms/{c}": by_detail[c] for c in by_detail})
        with http:
            out = await client.get_codelist_submission_values(PKG, CL, limit=1)
        assert out["valueSource"] == "term-detail"
        assert out["terms"][0]["submissionValue"] == "M"
        assert len(calls) == 1

    async def test_raw_reports_all_available_fields(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        out = await client.get_codelist_submission_values(PKG, CL, raw=True)
        assert out["fields"] == [
            "code", "name", "submissionValue", "definition", "synonyms",
        ]

    async def test_bad_codelist_propagates_404(self, tmp_path):
        client = make_client(tmp_path)  # nothing cached -> real request path
        http, _ = mock_http({})
        with http, pytest.raises(ResourceNotFoundError):
            await client.get_codelist_submission_values(PKG, "C667")

    async def test_codelist_id_is_case_insensitive(self, tmp_path):
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        out = await client.get_codelist_submission_values(PKG, f"  {CL.lower()} ")
        assert out["codelist"] == CL

    async def test_fallback_failure_yields_row_without_value(self, tmp_path):
        """A detail request that 404s must not delete the term from the page."""
        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        http, _ = mock_http({})  # everything else 404s
        with http:
            out = await client.get_codelist_submission_values(PKG, CL, limit=3)
        assert out["returned"] == 3
        assert out["terms"][2] == {"code": "C17865", "name": "Unknown", "submissionValue": None}


# ------------------------------------------------------------------- wiring


class TestToolRegistration:
    def test_tool_present_with_expected_schema(self):
        from cdisc_mcp.tools import ALL_TOOLS

        by_name = {t.name: t for t in ALL_TOOLS}
        assert len(by_name) == len(ALL_TOOLS) == 22
        tool = by_name["get_codelist_submission_values"]
        assert tool.inputSchema["required"] == ["package", "codelist"]
        props = tool.inputSchema["properties"]
        assert set(props) == {
            "package", "codelist", "fields", "offset", "limit", "raw",
        }
        # agents send either an array or "name,submissionValue"; the schema must
        # accept both, or the documented string form 400s before reaching code.
        forms = props["fields"]["anyOf"]
        assert forms[0]["items"]["enum"] == [
            "code", "name", "submissionValue", "definition", "synonyms",
        ]
        assert forms[1] == {"type": "string"}

    def test_ct_package_advertises_pagination(self):
        from cdisc_mcp.tools import ALL_TOOLS

        by_name = {t.name: t for t in ALL_TOOLS}
        assert {"offset", "limit"} <= set(by_name["get_ct_package"].inputSchema["properties"])

    def test_no_bogus_c667_sex_hint_left_in_docs(self):
        """C667 does not exist; SEX is C66731 (verified live). A doc example that
        404s is a trap an agent cannot debug from the message alone."""
        from cdisc_mcp.tools import ALL_TOOLS

        text = json.dumps(
            [{"name": t.name, "d": t.description, "s": t.inputSchema} for t in ALL_TOOLS],
            ensure_ascii=False,
        )
        assert "C667(SEX)" not in text
        assert "codelist='C667'" not in text
        assert "C66731(SEX)" in text

    def test_terms_endpoint_documents_its_own_gap(self):
        from cdisc_mcp.tools import ALL_TOOLS

        by_name = {t.name: t for t in ALL_TOOLS}
        desc = by_name["get_codelist_terms"].description
        assert "不返回逐术语的 submissionValue" in desc
        assert "get_codelist_submission_values" in desc

    async def test_dispatch_returns_envelope_unslimmed(self, tmp_path):
        """call_tool must not re-shape the envelope through the generic slimmer."""
        from cdisc_mcp.tools import register_tools

        captured = {}

        class FakeServer:
            def list_tools(self):
                return lambda f: f

            def call_tool(self):
                def deco(fn):
                    captured["fn"] = fn
                    return fn
                return deco

        client = make_client(tmp_path, {TERMS_KEY: ROSTER, PKG_KEY: PACKAGE})
        await register_tools(FakeServer(), client)
        result = await captured["fn"](
            "get_codelist_submission_values",
            {"package": PKG, "codelist": CL, "limit": 2, "raw": False},
        )
        payload = json.loads(result[0].text)
        assert payload["terms"][0]["submissionValue"] == "M"
        assert payload["valueSource"] == "package"
