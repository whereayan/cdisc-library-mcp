"""Product list resources.

`RESOURCES` is the single source of truth: `resources/list` advertises exactly
what `resources/read` can serve, so the two cannot drift apart again (0.1.6
shipped a reader whose comparisons never matched the advertised URIs).
"""

import json
from typing import Any, Awaitable, Callable, Iterable

from mcp.server import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.shared.exceptions import McpError
from mcp.types import AnyUrl, ErrorData, Resource

from ..client import CDISCClient
from ..utils.slim import slim

MIME_JSON = "application/json"

# uri -> (名称, 描述, 取数函数)
RESOURCES: dict[str, tuple[str, str, Callable[[CDISCClient], Awaitable[dict[str, Any]]]]] = {
    "cdisc://products": (
        "CDISC Products",
        "所有 CDISC 产品列表 (SDTM, ADaM, CDASH 等)",
        lambda client: client.get_products(),
    ),
    "cdisc://about": (
        "API Information",
        "CDISC Library API 信息",
        lambda client: client.get_about(),
    ),
}


async def register_product_resources(server: Server, client: CDISCClient) -> None:
    """Register product-related resources."""

    @server.list_resources()
    async def list_products_resources() -> list[Resource]:
        """List available product resources."""
        return [
            Resource(
                uri=uri,
                name=name,
                description=description,
                mimeType=MIME_JSON,
            )
            for uri, (name, description, _) in RESOURCES.items()
        ]

    @server.read_resource()
    async def read_product_resource(uri: AnyUrl) -> Iterable[ReadResourceContents]:
        """Read one product resource.

        Two rules the 0.1.6 implementation broke:

        * the injected ``params.uri`` is a pydantic ``AnyUrl``, not a ``str``,
          so it must be normalised with ``str()`` before comparison; comparing it
          to a literal is always False and every read landed on the unknown-uri
          branch;
        * the handler must return ``Iterable[ReadResourceContents]``. Other
          return shapes (a ``TextContent``, say) are rejected by the wrapper's
          return-type match.

        Payloads are slimmed like tool responses: ``raw`` is a per-tool argument
        and resources take no parameters, so the agent-facing form is the only
        one served. ``refs`` still carries the drill-down hrefs.
        """
        key = str(uri)
        entry = RESOURCES.get(key)
        if entry is None:
            known = ", ".join(RESOURCES)
            raise McpError(
                ErrorData(code=-32602, message=f"Unknown resource: {uri}. Known resources: {known}")
            )

        data = await entry[2](client)
        return [
            ReadResourceContents(
                content=json.dumps(slim(data), ensure_ascii=False, indent=2),
                mime_type=MIME_JSON,
            )
        ]
