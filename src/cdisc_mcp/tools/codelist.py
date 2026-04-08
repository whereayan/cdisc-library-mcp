"""Controlled terminology tools."""

from mcp.types import Tool


CODELIST_TOOLS = [
    Tool(
        name="get_ct_packages",
        description="获取控制术语包列表",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_ct_package",
        description="获取控制术语包详情",
        inputSchema={
            "type": "object",
            "properties": {"package": {"type": "string", "description": "包名如 p60"}},
            "required": ["package"],
        },
    ),
    Tool(
        name="get_codelists",
        description="获取编码列表",
        inputSchema={
            "type": "object",
            "properties": {"package": {"type": "string"}},
            "required": ["package"],
        },
    ),
    Tool(
        name="get_codelist",
        description="获取编码详情",
        inputSchema={
            "type": "object",
            "properties": {
                "package": {"type": "string"},
                "codelist": {"type": "string", "description": "编码ID如 C667"},
            },
            "required": ["package", "codelist"],
        },
    ),
    Tool(
        name="get_codelist_terms",
        description="获取编码术语列表",
        inputSchema={
            "type": "object",
            "properties": {
                "package": {"type": "string"},
                "codelist": {"type": "string"},
            },
            "required": ["package", "codelist"],
        },
    ),
    Tool(
        name="get_term",
        description="获取术语详情",
        inputSchema={
            "type": "object",
            "properties": {
                "package": {"type": "string"},
                "codelist": {"type": "string"},
                "term": {"type": "string", "description": "术语ID"},
            },
            "required": ["package", "codelist", "term"],
        },
    ),
]