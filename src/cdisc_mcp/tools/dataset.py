"""Dataset tools."""

from ._common import raw_prop, standard_prop, tool, version_prop


DATASET_TOOLS = [
    tool(
        "get_datasets",
        description=(
            "获取指定标准下的所有数据集列表。\n\n"
            "仅适用于 SDTM/SEND/CDASH 系列；adam / adamig 没有 datasets 端点，"
            "请改用 get_datastructures。\n\n"
            "示例: standard='sdtmig', version='3-4'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version"],
    ),
    tool(
        "get_dataset",
        description=(
            "获取指定数据集的元数据：描述、所属类、结构说明、用途等。\n"
            "只查变量清单请用 get_dataset_variables（更省 token）；"
            "查单个变量详情用 get_variable。\n"
            "仅适用于 SDTM/SEND/CDASH 系列；ADaM 的数据结构用 get_datastructure。\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "dataset": {
                "type": "string",
                "description": "数据集名称（大写），常用: DM(人口统计), AE(不良事件), LB(实验室检查), VS(生命体征)",
            },
            "raw": raw_prop(),
        },
        required=["standard", "version", "dataset"],
    ),
    tool(
        "get_dataset_variables",
        description=(
            "获取指定数据集的完整变量列表（名称、标签、核心属性 Req/Exp/Perm、角色等）。\n"
            "这是拿一个域全部变量定义的首选工具；数据集本身的元数据用 get_dataset。\n"
            "仅适用于 SDTM/SEND/CDASH 系列；查 ADaM（如 ADSL）的变量请改用 "
            "get_datastructure（含 core 与类型的整表）或 get_datastructure_variables（名称清单）。\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "dataset": {
                "type": "string",
                "description": "数据集名称（大写），如 DM, AE",
            },
            "raw": raw_prop(),
        },
        required=["standard", "version", "dataset"],
    ),
    tool(
        "get_variable",
        description=(
            "获取指定变量的详细信息：数据类型、核心属性(Req/Exp/Perm)、角色、"
            "关联的 CT codelist 引用（在 refs 中）等。\n"
            "仅适用于 SDTM/SEND/CDASH 系列；ADaM 变量用 get_datastructure_variable。\n\n"
            "示例: standard='sdtmig', version='3-4', dataset='DM', variable='USUBJID'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "dataset": {
                "type": "string",
                "description": "数据集名称（大写），如 DM",
            },
            "variable": {
                "type": "string",
                "description": "变量名称（大写），如 USUBJID, AGE, SEX",
            },
            "raw": raw_prop(),
        },
        required=["standard", "version", "dataset", "variable"],
    ),
]
