"""Standard query tools."""

from mcp.types import Tool


STANDARD_TOOLS = [
    Tool(
        name="get_products",
        description=(
            "获取所有 CDISC 产品列表，包括 SDTM、ADaM、CDASH 等标准。"
            "返回产品的名称、版本、类型等信息。"
            "无需参数，可直接调用。"
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_standard",
        description=(
            "获取指定标准的基本信息，包括描述、生效日期、包含的类列表等。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，可选值: sdtm, sdtmig, sendig, adam, adamig, cdash, cdashig\n"
            "- version: 版本号，格式支持两种: '1-8' 或 '1.8'（会自动转换）\n\n"
            "示例: standard='sdtmig', version='3-4' 或 version='3.4'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称: sdtm, sdtmig, sendig, adam, adamig, cdash, cdashig",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 1-8 或 1.8 格式",
                },
            },
            "required": ["standard", "version"],
        },
    ),
    Tool(
        name="get_classes",
        description=(
            "获取指定标准包含的所有类（Class）列表。\n"
            "SDTM 类包括: Events, Findings, Interventions, SpecialPurpose 等。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtm, sdtmig\n"
            "- version: 版本号，格式支持 '1-8' 或 '1.8'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称: sdtm, sdtmig, sendig, adam 等",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 1-8 或 1.8 格式",
                },
            },
            "required": ["standard", "version"],
        },
    ),
]