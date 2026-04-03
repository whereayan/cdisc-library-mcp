"""CDISC Library MCP Server Entry Point."""

import asyncio
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import CDISCConfig
from .client import CDISCClient
from .cache import CacheManager
from .resources import register_resources
from .tools import register_tools


class CDISCMCPServer:
    """CDISC Library MCP Server."""

    def __init__(self, config: CDISCConfig):
        """Initialize MCP server.

        Args:
            config: CDISC configuration
        """
        self.config = config
        self.cache = CacheManager(config.get_cache_path(), config.cache_ttl)
        self.client = CDISCClient(config, self.cache)
        self.server = Server("cdisc-library-mcp")

    async def setup(self) -> None:
        """Register MCP components."""
        await register_resources(self.server, self.client)
        await register_tools(self.server, self.client)

    async def run(self) -> None:
        """Start the MCP server."""
        await self.setup()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main() -> None:
    """Main entry point."""
    config = CDISCConfig.from_env()

    if not config.api_key:
        print(
            "警告: CDISC_API_KEY 未设置。部分功能可能受限。\n"
            "请设置环境变量: export CDISC_API_KEY=your-api-key\n"
            "获取 API Key: https://api.developer.library.cdisc.org/profile",
            file=sys.stderr
        )

    server = CDISCMCPServer(config)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())