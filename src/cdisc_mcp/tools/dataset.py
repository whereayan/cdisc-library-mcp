"""Dataset tools."""

from mcp.types import Tool


DATASET_TOOLS = [
    Tool(
        name="get_datasets",
        description=(
            "获取指定标准下的所有数据集列表。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，常用: sdtmig, adamig, sendig\n"
            "- version: 版本号，格式支持 '3-4' 或 '3.4'\n\n"
            "示例: standard='sdtmig', version='3-4'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称，如 sdtmig, adamig",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 3-4 或 3.4 格式",
                },
            },
            "required": ["standard", "version"],
        },
    ),
    Tool(
        name="get_dataset",
        description=(
            "获取指定数据集的详细信息，包括结构说明、变量列表等。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtmig, adamig\n"
            "- version: 版本号，格式支持 '3-4' 或 '3.4'\n"
            "- dataset: 数据集名称（大写），常用: DM(人口统计), AE(不良事件), LB(实验室检查), VS(生命体征)\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称，如 sdtmig, adamig",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 3-4 或 3.4 格式",
                },
                "dataset": {
                    "type": "string",
                    "description": "数据集名称（大写），如 DM, AE, LB, VS",
                },
            },
            "required": ["standard", "version", "dataset"],
        },
    ),
    Tool(
        name="get_dataset_variables",
        description=(
            "获取指定数据集的所有变量列表。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtmig\n"
            "- version: 版本号，格式支持 '3-4' 或 '3.4'\n"
            "- dataset: 数据集名称（大写），如 DM, AE\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称，如 sdtmig",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 3-4 或 3.4 格式",
                },
                "dataset": {
                    "type": "string",
                    "description": "数据集名称（大写），如 DM, AE",
                },
            },
            "required": ["standard", "version", "dataset"],
        },
    ),
    Tool(
        name="get_variable",
        description=(
            "获取指定变量的详细信息，包括数据类型、核心属性(Req/Exp/Perm)、角色等。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtmig\n"
            "- version: 版本号，格式支持 '3-4' 或 '3.4'\n"
            "- dataset: 数据集名称（大写），如 DM\n"
            "- variable: 变量名称（大写），如 USUBJID, STUDYID, AGE, SEX\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM', variable='USUBJID'"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {
                    "type": "string",
                    "description": "标准名称，如 sdtmig",
                },
                "version": {
                    "type": "string",
                    "description": "版本号，支持 3-4 或 3.4 格式",
                },
                "dataset": {
                    "type": "string",
                    "description": "数据集名称（大写），如 DM",
                },
                "variable": {
                    "type": "string",
                    "description": "变量名称（大写），如 USUBJID, AGE, SEX",
                },
            },
            "required": ["standard", "version", "dataset", "variable"],
        },
    ),
]