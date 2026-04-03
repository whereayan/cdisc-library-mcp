"""MCP Tools for CDISC Library."""

import json
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..client import CDISCClient
from .standard import STANDARD_TOOLS
from .dataset import DATASET_TOOLS
from .codelist import CODELIST_TOOLS
from .search import SEARCH_TOOLS


# 合并所有工具定义
ALL_TOOLS = STANDARD_TOOLS + DATASET_TOOLS + CODELIST_TOOLS + SEARCH_TOOLS


async def register_tools(server: Server, client: CDISCClient) -> None:
    """Register all MCP tools."""

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return ALL_TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = await _execute_tool(client, name, arguments)
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]


async def _execute_tool(client: CDISCClient, name: str, args: dict) -> dict:
    """Execute a tool by name."""
    # Product tools
    if name == "get_products":
        return await client.get_products()

    # Standard tools
    elif name == "get_standard":
        return await client.get_standard(args["standard"], args["version"])
    elif name == "get_classes":
        return await client.get_classes(args["standard"], args["version"])

    # Dataset tools
    elif name == "get_datasets":
        return await client.get_datasets(args["standard"], args["version"])
    elif name == "get_dataset":
        return await client.get_dataset(
            args["standard"], args["version"], args["dataset"]
        )
    elif name == "get_dataset_variables":
        return await client.get_dataset_variables(
            args["standard"], args["version"], args["dataset"]
        )
    elif name == "get_variable":
        return await client.get_variable(
            args["standard"], args["version"], args["dataset"], args["variable"]
        )

    # Controlled terminology tools
    elif name == "get_ct_packages":
        return await client.get_ct_packages()
    elif name == "get_ct_package":
        return await client.get_ct_package(args["package"])
    elif name == "get_codelists":
        return await client.get_codelists(args["package"])
    elif name == "get_codelist":
        return await client.get_codelist(args["package"], args["codelist"])
    elif name == "get_codelist_terms":
        return await client.get_codelist_terms(args["package"], args["codelist"])

    # Search tools
    elif name == "search":
        return await client.search(args["query"])
    elif name == "search_suggest":
        return await client.search_suggest(args["query"])
    elif name == "compare_versions":
        return await client.compare_versions(
            args["standard"], args["version1"], args["version2"]
        )

    else:
        raise ValueError(f"Unknown tool: {name}")


__all__ = ["register_tools", "ALL_TOOLS"]