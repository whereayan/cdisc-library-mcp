"""MCP Prompts for CDISC Library."""

from mcp.server import Server
from mcp.types import Prompt, PromptArgument

from .templates import PROMPT_TEMPLATES


async def register_prompts(server: Server) -> None:
    """Register all MCP prompts."""

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name="explore_standard",
                description="引导用户探索某个 CDISC 标准",
                arguments=[
                    PromptArgument(
                        name="standard",
                        description="标准名称 (sdtm, sdtmig, adam 等)",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="find_variable",
                description="帮助用户查找特定变量",
                arguments=[
                    PromptArgument(
                        name="keyword",
                        description="变量关键词",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="find_terminology",
                description="帮助用户查找控制术语",
                arguments=[
                    PromptArgument(
                        name="keyword",
                        description="术语关键词",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="compare_standards",
                description="引导用户比较标准版本",
                arguments=[
                    PromptArgument(
                        name="standard",
                        description="标准名称",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="validate_dataset",
                description="检查数据集是否符合标准",
                arguments=[
                    PromptArgument(name="standard", description="标准名称", required=True),
                    PromptArgument(name="dataset", description="数据集名称", required=True),
                ],
            ),
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict) -> str:
        """Get prompt template content."""
        template = PROMPT_TEMPLATES.get(name)
        if not template:
            return f"Unknown prompt: {name}"

        return template.format(**arguments)


__all__ = ["register_prompts"]