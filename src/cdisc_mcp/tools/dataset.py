"""Dataset tools."""

from mcp.types import Tool


DATASET_TOOLS = [
    Tool(
        name="get_datasets",
        description="获取数据集列表",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["standard", "version"],
        },
    ),
    Tool(
        name="get_dataset",
        description="获取数据集详情",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string"},
                "version": {"type": "string"},
                "dataset": {"type": "string", "description": "数据集名称如 DM, AE"},
            },
            "required": ["standard", "version", "dataset"],
        },
    ),
    Tool(
        name="get_dataset_variables",
        description="获取数据集变量列表",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string"},
                "version": {"type": "string"},
                "dataset": {"type": "string"},
            },
            "required": ["standard", "version", "dataset"],
        },
    ),
    Tool(
        name="get_variable",
        description="获取变量详情",
        inputSchema={
            "type": "object",
            "properties": {
                "standard": {"type": "string"},
                "version": {"type": "string"},
                "dataset": {"type": "string"},
                "variable": {"type": "string", "description": "变量名称"},
            },
            "required": ["standard", "version", "dataset", "variable"],
        },
    ),
]