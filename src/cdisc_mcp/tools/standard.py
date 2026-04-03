"""Standard query tools."""

from mcp.types import Tool


STANDARD_TOOLS = [
    Tool(
        name="get_products",
        description="获取所有 CDISC 产品列表",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_standard",
        description="获取标准产品信息。支持 sdtm, sdtmig, sendig, adam, cdash, cdashig。",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string", "description": "标准名称"},
                "version": {"type": "string", "description": "版本号"},
            },
            "required": ["standard", "version"],
        },
    ),
    Tool(
        name="get_classes",
        description="获取标准的类列表",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["standard", "version"],
        },
    ),
]