"""Search tools."""

from mcp.types import Tool


SEARCH_TOOLS = [
    Tool(
        name="search",
        description="全局搜索 CDISC Library",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="search_suggest",
        description="获取搜索建议",
        inputSchema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
    Tool(
        name="compare_versions",
        description="版本差异比较",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string", "description": "标准名称"},
                "version1": {"type": "string", "description": "第一个版本"},
                "version2": {"type": "string", "description": "第二个版本"},
            },
            "required": ["standard", "version1", "version2"],
        },
    ),
]