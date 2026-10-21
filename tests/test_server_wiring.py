"""Tests for MCP server wiring.

These guard the registration layer, which the pure-unit tests never touched:
- 0.1.4 shipped `register_prompts` but never called it, so the prompts advertised
  in the README were not reachable over MCP.
- mcp 2.x removed the `@server.list_resources()` decorator API, so an unpinned
  dependency silently produces a server that dies at startup.
"""

import importlib.metadata

import pytest
from mcp import types
from mcp.shared.exceptions import McpError

from cdisc_mcp.config import CDISCConfig
from cdisc_mcp.prompts.templates import PROMPT_TEMPLATES
from cdisc_mcp.server import CDISCMCPServer
from cdisc_mcp.version import __version__


@pytest.fixture
def server(tmp_path):
    config = CDISCConfig(api_key="test-key", cache_dir=str(tmp_path / "cache"))
    return CDISCMCPServer(config)


async def _request(server, request):
    """Call a registered handler the way the stdio transport would, and unwrap
    the ServerResult envelope (its payload field is named ``root``)."""
    handler = server.server.request_handlers[type(request)]
    return (await handler(request)).root


class TestRegistration:
    async def test_setup_registers_all_three_component_kinds(self, server):
        await server.setup()
        handlers = server.server.request_handlers
        assert types.ListToolsRequest in handlers
        assert types.ListResourcesRequest in handlers
        assert types.ListPromptsRequest in handlers, "prompts advertised but never registered"

    async def test_all_fifteen_tools_reachable(self, server):
        await server.setup()
        res = await _request(server, types.ListToolsRequest(method="tools/list"))
        assert len(res.tools) == 15, sorted(t.name for t in res.tools)

    async def test_prompts_listed(self, server):
        await server.setup()
        res = await _request(server, types.ListPromptsRequest(method="prompts/list"))
        assert {p.name for p in res.prompts} == set(PROMPT_TEMPLATES)


class TestPromptRendering:
    async def test_get_prompt_returns_structured_result(self, server):
        await server.setup()
        req = types.GetPromptRequest(
            method="prompts/get",
            params=types.GetPromptRequestParams(
                name="explore_standard", arguments={"standard": "sdtm"}
            ),
        )
        res = await _request(server, req)
        assert isinstance(res, types.GetPromptResult)
        text = res.messages[0].content.text
        assert "{standard}" not in text and "sdtm" in text

    async def test_unknown_prompt_is_an_error_not_prompt_text(self, server):
        await server.setup()
        req = types.GetPromptRequest(
            method="prompts/get",
            params=types.GetPromptRequestParams(name="nope", arguments={}),
        )
        with pytest.raises(McpError):
            await _request(server, req)

    async def test_missing_argument_is_an_error(self, server):
        await server.setup()
        req = types.GetPromptRequest(
            method="prompts/get",
            params=types.GetPromptRequestParams(name="validate_dataset", arguments={"standard": "sdtmig"}),
        )
        with pytest.raises(McpError) as exc:
            await _request(server, req)
        assert "dataset" in str(exc.value.error)


class TestVersionConsistency:
    def test_reported_version_matches_distribution(self):
        """The MCP server must report the same version the wheel was built with."""
        assert importlib.metadata.version("cdisc-library-mcp") == __version__

    def test_mcp_dependency_upper_bound_is_declared(self):
        """mcp 2.x drops the decorator API this server is written against."""
        requires = importlib.metadata.metadata("cdisc-library-mcp").get_all("Requires-Dist") or []
        mcp_req = [r for r in requires if r.lower().startswith("mcp")]
        assert mcp_req, mcp_req
        assert "<2.0.0" in mcp_req[0].replace(" ", ""), mcp_req[0]
