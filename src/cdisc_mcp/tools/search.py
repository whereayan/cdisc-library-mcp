"""Search tools."""

from mcp.types import Tool


SEARCH_TOOLS = [
    Tool(
        name="search",
        description=(
            "全局搜索 CDISC Library，可搜索标准、数据集、变量、术语等。\n\n"
            "参数说明：\n"
            "- query: 搜索关键词，如 'sdtm', 'adverse event', 'DM', 'sex'\n\n"
            "示例: query='sdtm' 或 query='adverse event'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，如 sdtm, adverse event, DM",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="compare_versions",
        description=(
            "比较同一标准的两个版本之间的差异，包括新增、删除、修改的内容。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtm, sdtmig, adam\n"
            "- version1: 旧版本号，格式支持 '1-7' 或 '1.7'\n"
            "- version2: 新版本号，格式支持 '1-8' 或 '1.8'\n\n"
            "示例: standard='sdtm', version1='1-7', version2='1-8'\n"
            "注意: 返回结果可能较大，包含详细的差异对比。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称，如 sdtm, sdtmig, adam",
                },
                "version1": {
                    "type": "string",
                    "description": "旧版本号，支持 1-7 或 1.7 格式",
                },
                "version2": {
                    "type": "string",
                    "description": "新版本号，支持 1-8 或 1.8 格式",
                },
            },
            "required": ["standard", "version1", "version2"],
        },
    ),
]