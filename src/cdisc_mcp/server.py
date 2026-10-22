"""CDISC Library MCP Server Entry Point."""

import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Optional

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


# CDISC keys are always ASCII, so detection reads bytes and never depends on the
# file's text encoding (a GBK-commented .env must still be recognised).
CDISC_KEY_LINE = re.compile(rb'^[ \t]*(?:export[ \t]+)?CDISC_[A-Za-z0-9_]+[ \t]*=', re.M)


def _defines_cdisc_settings(path: Path) -> bool:
    """True if the dotenv file itself declares a ``CDISC_*`` variable."""
    try:
        return bool(CDISC_KEY_LINE.search(path.read_bytes()))
    except OSError:
        return False


def _env_file_candidates() -> list[Path]:
    """Search order: working directory > project root > user home."""
    return [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent / ".env",  # 项目根目录
        Path.home() / ".cdisc-mcp" / ".env",
    ]


def _pick_env_file(candidates: Optional[list[Path]] = None) -> Optional[Path]:
    """First candidate that actually owns CDISC config.

    The working directory is where the MCP client launched this server, so it
    usually holds an unrelated project ``.env``. Treating any existing file as a
    hit stops the search there and ``~/.cdisc-mcp/.env`` is never reached, which
    surfaces as a mysterious "not authenticated" server. Skip files that declare
    no ``CDISC_*`` variable, and never import their keys.
    """
    for env_path in _env_file_candidates() if candidates is None else candidates:
        try:
            if env_path.is_file() and _defines_cdisc_settings(env_path):
                return env_path
        except OSError:
            continue  # unreadable candidate: keep searching rather than fail startup
    return None


def _load_env_file() -> None:
    """Load environment variables from the .env file that owns CDISC config."""
    env_path = _pick_env_file()
    if env_path is not None:
        load_dotenv(env_path)


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