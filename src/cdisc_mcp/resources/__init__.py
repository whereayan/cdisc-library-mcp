"""MCP Resources for CDISC Library."""

from mcp.server import Server

from ..client import CDISCClient
from .products import register_product_resources


async def register_resources(server: Server, client: CDISCClient) -> None:
    """Register all MCP resources."""
    await register_product_resources(server, client)


__all__ = ["register_resources"]