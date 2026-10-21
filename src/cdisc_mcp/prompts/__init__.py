"""MCP Prompts for CDISC Library."""

import string

from mcp.server import Server
from mcp.shared.exceptions import McpError
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from .templates import PROMPT_TEMPLATES


def _placeholders(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


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
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        """Render a prompt template as an MCP GetPromptResult.

        The low-level server validates the handler's return value, so this must be
        a GetPromptResult (returning a bare str raises a validation error). Unknown
        prompts and missing arguments are reported as MCP errors instead of being
        rendered into the prompt text.
        """
        template = PROMPT_TEMPLATES.get(name)
        if template is None:
            known = ", ".join(sorted(PROMPT_TEMPLATES))
            raise McpError(
                ErrorData(code=-32602, message=f"Unknown prompt: {name}. Known prompts: {known}")
            )

        args = dict(arguments or {})
        wanted = _placeholders(template)
        missing = sorted(wanted - set(args))
        if missing:
            raise McpError(
                ErrorData(
                    code=-32602,
                    message=f"Prompt '{name}' is missing required argument(s): {', '.join(missing)}",
                )
            )

        try:
            text = template.format(**args)
        except (KeyError, IndexError, ValueError) as exc:
            raise McpError(
                ErrorData(code=-32603, message=f"Failed to render prompt '{name}': {exc}")
            ) from exc

        return GetPromptResult(
            description=name,
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=text))
            ],
        )


__all__ = ["register_prompts"]