"""Controlled terminology tools."""

from mcp.types import Tool


CODELIST_TOOLS = [
    Tool(
        name="get_ct_packages",
        description=(
            "获取所有 CDISC 控制术语（Controlled Terminology）包列表。\n"
            "返回包名称、生效日期等信息。\n"
            "无需参数，可直接调用。"
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_ct_package",
        description=(
            "获取指定控制术语包的详细信息。\n\n"
            "参数说明：\n"
            "- package: 包名称，格式如 'sdtmct-2024-03-29' 或简写 'p60'\n"
            "  常用: sdtmct-YYYY-MM-DD (SDTM术语), adamct-YYYY-MM-DD (ADaM术语)\n\n"
            "示例: package='sdtmct-2024-03-29'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "包名称，如 sdtmct-2024-03-29 或 p60",
                }
            },
            "required": ["package"],
        },
    ),
    Tool(
        name="get_codelists",
        description=(
            "获取指定控制术语包中的所有编码列表（Codelist）。\n\n"
            "参数说明：\n"
            "- package: 包名称，格式如 'sdtmct-2024-03-29'\n\n"
            "示例: package='sdtmct-2024-03-29'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "包名称，如 sdtmct-2024-03-29",
                }
            },
            "required": ["package"],
        },
    ),
    Tool(
        name="get_codelist",
        description=(
            "获取指定编码列表的详细信息。\n\n"
            "参数说明：\n"
            "- package: 包名称，如 'sdtmct-2024-03-29'\n"
            "- codelist: 编码列表ID，格式为 'C' + 数字，如 C667, C141657\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C141657'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "包名称，如 sdtmct-2024-03-29",
                },
                "codelist": {
                    "type": "string",
                    "description": "编码ID，格式为 C + 数字，如 C667, C141657",
                },
            },
            "required": ["package", "codelist"],
        },
    ),
    Tool(
        name="get_codelist_terms",
        description=(
            "获取指定编码列表中的所有术语（Terms），即可选的标准化值。\n\n"
            "参数说明：\n"
            "- package: 包名称，如 'sdtmct-2024-03-29'\n"
            "- codelist: 编码列表ID，如 C667\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C141657'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "包名称，如 sdtmct-2024-03-29",
                },
                "codelist": {
                    "type": "string",
                    "description": "编码ID，如 C667",
                },
            },
            "required": ["package", "codelist"],
        },
    ),
    Tool(
        name="get_term",
        description=(
            "获取指定术语的详细信息，包括定义、提交值(submissionValue)等。\n\n"
            "参数说明：\n"
            "- package: 包名称，如 'sdtmct-2024-03-29'\n"
            "- codelist: 编码列表ID，如 C141657\n"
            "- term: 术语ID，格式为 'C' + 数字，如 C174106\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C141657', term='C174106'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "包名称，如 sdtmct-2024-03-29",
                },
                "codelist": {
                    "type": "string",
                    "description": "编码ID，如 C141657",
                },
                "term": {
                    "type": "string",
                    "description": "术语ID，格式为 C + 数字，如 C174106",
                },
            },
            "required": ["package", "codelist", "term"],
        },
    ),
]