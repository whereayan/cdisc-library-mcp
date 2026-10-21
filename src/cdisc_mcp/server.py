"""CDISC Library MCP Server Entry Point."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

from .config import CDISCConfig
from .client import CDISCClient
from .cache import CacheManager
from .version import __version__
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools


def _load_env_file() -> None:
    """Load environment variables from .env file.

    Searches for .env file in:
    1. Current working directory
    2. Package installation directory
    3. User home directory (~/.cdisc-mcp/.env)
    """
    # 优先级：工作目录 > 包目录 > 用户目录
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent / ".env",  # 项目根目录
        Path.home() / ".cdisc-mcp" / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break


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
        self.server = Server("cdisc-library-mcp", version=__version__)

    async def setup(self) -> None:
        """Register MCP components."""
        await register_resources(self.server, self.client)
        await register_tools(self.server, self.client)
        await register_prompts(self.server)

    async def run(self) -> None:
        """Start the MCP server."""
        await self.setup()
        init_options = self.server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, init_options)


async def async_main() -> None:
    """Main async entry point."""
    # 加载 .env 文件（如果存在）
    _load_env_file()

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


def main() -> None:
    """Synchronous entry point for uvx/pip."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()