"""Shared schema fragments and helpers for tool definitions.

Kept in one place so the 15 tool schemas cannot drift apart on the details
that matter most to an LLM caller: the legal ``standard`` values (enum, not
prose), the ``latest`` version alias, and the ``raw`` escape hatch.
"""

from typing import Any, Optional

from mcp.types import Tool, ToolAnnotations

# Legal values for the ``standard`` parameter. The Library API hosts more
# niche products (adam-tte, sendig-dart, tig, ...); those are reachable via
# search or by passing the product path to the client directly, but the tools
# intentionally constrain to the seven mainstream standards so an LLM cannot
# silently typo one.
STANDARDS = ["sdtm", "sdtmig", "sendig", "adam", "adamig", "cdash", "cdashig"]

# Standards whose metadata lives under /datastructures instead of /datasets.
ADAM_STANDARDS = ["adam", "adamig"]

# Every tool in this server is a read-only GET against the Library API.
READ_ONLY = ToolAnnotations(readOnlyHint=True)


def standard_prop() -> dict[str, Any]:
    return {
        "type": "string",
        "enum": STANDARDS,
        "description": "标准名称: " + ", ".join(STANDARDS),
    }


def version_prop(example: str = "3-4") -> dict[str, Any]:
    return {
        "type": "string",
        "description": (
            f"版本号，支持 '{example}' 或 '{example.replace('-', '.')}' 格式；"
            "传 'latest' 自动解析为该产品当前最新版本"
        ),
    }


def raw_prop() -> dict[str, Any]:
    return {
        "type": "boolean",
        "description": (
            "true 时返回未经瘦身的原始 API 载荷（含 _links 等超媒体元数据）；"
            "默认 false，返回已瘦身、更省 token 的响应"
        ),
    }


def datastructure_prop() -> dict[str, Any]:
    return {
        "type": "string",
        "description": (
            "分析数据结构名，如 ADSL(受试者级分析数据集), BDS, OCCDS, TTE。"
            "大小写不敏感；不确定时先调 get_datastructures 看可用清单"
        ),
    }


def varset_prop() -> dict[str, Any]:
    return {
        "type": "string",
        "description": (
            "变量集，可传 slug（如 Identifier, Treatment, PopulationIndicator）"
            "或显示名（如 'Subject Demographics'）；名称跨版本不稳定，"
            "先用 get_datastructure_varsets 取当版可用清单"
        ),
    }


def variable_prop(example: str = "AGE") -> dict[str, Any]:
    return {
        "type": "string",
        "description": (
            f"变量名称，如 {example}。大小写不敏感（ADSL 里存在 SITEGRy / APHASEw "
            "这类混合大小写的模式变量，会自动匹配到 API 的准确写法）"
        ),
    }


def tool(
    name: str,
    description: str,
    properties: dict[str, Any],
    required: Optional[list[str]] = None,
    annotations: ToolAnnotations = READ_ONLY,
) -> Tool:
    """Build a Tool with the server-wide defaults applied."""
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
        annotations=annotations,
    )


__all__ = [
    "STANDARDS",
    "ADAM_STANDARDS",
    "READ_ONLY",
    "standard_prop",
    "version_prop",
    "raw_prop",
    "datastructure_prop",
    "varset_prop",
    "variable_prop",
    "tool",
]
