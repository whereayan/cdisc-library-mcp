"""Standard query tools."""

from ._common import raw_prop, standard_prop, tool, version_prop


STANDARD_TOOLS = [
    tool(
        "get_products",
        description=(
            "获取所有 CDISC 产品列表，包括 SDTM、ADaM、CDASH 等标准及各 IG 系列。\n"
            "返回产品名称、版本路径（refs）、类型等信息。\n"
            "无需参数，可直接调用。不确定某标准的可用版本时，先调这个。"
        ),
        properties={"raw": raw_prop()},
        required=[],
    ),
    tool(
        "get_standard",
        description=(
            "获取指定标准的基本信息：描述、生效日期、包含的类列表等。\n\n"
            "示例: standard='sdtmig', version='3-4'（或 '3.4' / 'latest'）\n"
            "注意: standard 与 version 必须匹配（如 sdtmig 用 3-x，sdtm 用 1-x/2-x），"
            "拿不准时 version 传 'latest'。"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version"],
    ),
    tool(
        "get_classes",
        description=(
            "获取指定标准包含的所有类（Class）列表。\n"
            "SDTM 类包括: Events, Findings, Interventions, SpecialPurpose 等。\n\n"
            "示例: standard='sdtmig', version='3-4'"
        ),
        properties={
            "standard": standard_prop(),
            "version": version_prop(),
            "raw": raw_prop(),
        },
        required=["standard", "version"],
    ),
]
