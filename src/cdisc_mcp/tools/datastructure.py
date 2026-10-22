"""ADaM data structure tools.

ADaM and ADaMIG describe their metadata as *analysis data structures* (ADSL, BDS,
OCCDS, ...) and expose them under ``/datastructures``, never under ``/datasets``.
The four dataset tools therefore cannot answer an ADaM question — these six are
the supported route, one tool per endpoint of the ADaM section of the Library API.
"""

from ._common import (
    datastructure_prop,
    raw_prop,
    standard_prop,
    tool,
    variable_prop,
    varset_prop,
    version_prop,
)


DATASTRUCTURE_TOOLS = [
    tool(
        "get_datastructures",
        description=(
            "获取 ADaM 产品（adam / adamig）包含的分析数据结构清单（ADSL、BDS 等）。\n"
            "ADaM 侧没有 datasets 端点，get_datasets 对 adam/adamig 一定 404，要先用这个看有哪些结构。\n\n"
            "示例: standard='adamig', version='latest'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "raw": raw_prop(),
        },
        required=["standard", "version"],
    ),
    tool(
        "get_datastructure",
        description=(
            "获取单个分析数据结构的完整变量表：按变量集分组，每个变量一行\n"
            "（name / label / core / datatype）。这是唯一带 core 与类型的整表来源，\n"
            "问“ADSL 有哪些变量（含 Required/Permissible）”就用它。\n\n"
            "默认返回紧凑表（已去掉每个变量的 description）；\n"
            "整包原始载荷很大，确有必要时再传 raw=true。\n\n"
            "示例: standard='adamig', version='latest', datastructure='ADSL'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "datastructure": datastructure_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version", "datastructure"],
    ),
    tool(
        "get_datastructure_variables",
        description=(
            "获取分析数据结构的变量名清单（变量名 + 标签，另给 hrefTemplate），最省 token 的穷举方式。\n"
            "注意：此端点不返回 core 与数据类型，要整表用 get_datastructure；\n"
            "单个变量的定义与描述用 get_datastructure_variable。\n\n"
            "示例: standard='adamig', version='latest', datastructure='ADSL'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "datastructure": datastructure_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version", "datastructure"],
    ),
    tool(
        "get_datastructure_variable",
        description=(
            "获取分析数据结构中单个变量的详情：core、数据类型、描述、所属变量集（在 refs 中）。\n"
            "变量名大小写不敏感（API 里是 SITEGRy / APHASEw 这类混合大小写，会自动匹配到准确写法）。\n\n"
            "示例: standard='adamig', version='latest', datastructure='ADSL', variable='AGE'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "datastructure": datastructure_prop(),
            "variable": variable_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version", "datastructure", "variable"],
    ),
    tool(
        "get_datastructure_varsets",
        description=(
            "获取分析数据结构包含的变量集（Identifier / Treatment / Trial Experience 等）清单。\n"
            "变量集名跨版本不稳定，下钻前先来这里取当版的可用名称。\n\n"
            "示例: standard='adamig', version='latest', datastructure='ADSL'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "datastructure": datastructure_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version", "datastructure"],
    ),
    tool(
        "get_datastructure_varset",
        description=(
            "获取单个变量集的内容（含每个变量的 description），适合按集下钻而不要拉整包。\n"
            "varset 可传 slug（如 Identifier、SubjectDemographics）或显示名\n"
            "（如 'ADSL Subject Demographics'、'Subject Demographics'），大小写与空格/连字符不敏感。\n\n"
            "示例: standard='adamig', version='latest', datastructure='ADSL', varset='PopulationIndicator'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop("1-3"),
            "datastructure": datastructure_prop(),
            "varset": varset_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version", "datastructure", "varset"],
    ),
]


__all__ = ["DATASTRUCTURE_TOOLS"]
