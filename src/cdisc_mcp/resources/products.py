"""Product list resources."""

import json
from mcp.server import Server
from mcp.types import Resource, TextContent

from ..client import CDISCClient


async def register_product_resources(server: Server, client: CDISCClient) -> None:
    """Register product-related resources."""

    @server.list_resources()
    async def list_products_resources() -> list[Resource]:
        """List available product resources."""
        return [
            Resource(
                uri="cdisc://products",
                name="CDISC Products",
                description="所有 CDISC 产品列表 (SDTM, ADaM, CDASH 等)",
                mimeType="application/json",
            ),
            Resource(
                uri="cdisc://about",
                name="API Information",
                description="CDISC Library API 信息",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def read_product_resource(uri: str) -> TextContent:
        """Read product resource content."""
        if uri == "cdisc://products":
            data = await client.get_products()
        elif uri == "cdisc://about":
            data = await client.get_about()
        else:
            raise ValueError(f"Unknown resource: {uri}")

        return TextContent(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(data, ensure_ascii=False, indent=2),
        )