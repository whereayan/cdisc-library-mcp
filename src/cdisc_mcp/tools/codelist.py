"""Controlled terminology tools."""

from ._common import raw_prop, tool


_PACKAGE_PROP = {
    "type": "string",
    "description": (
        "CT 包名称，如 'sdtmct-2024-03-29'（SDTM 术语）或 'adamct-2024-03-29'（ADaM 术语）；"
        "大小写不敏感。不确定有哪些包时用 get_ct_packages 查询"
    ),
}
_CODELIST_PROP = {
    "type": "string",
    "description": (
        "编码列表 ID，格式为 'C' + 数字，如 C667(SEX), C65047(LBTESTCD)。"
        "注意：C141657 是 10-Meter Walk/Run Functional Test Test Code，与 LBTESTCD 无关；"
        "不确定某变量的 codelist ID 时，用 get_variable 看其 refs 里的 CT 引用"
    ),
}

CODELIST_TOOLS = [
    tool(
        "get_ct_packages",
        description=(
            "获取所有 CDISC 控制术语（Controlled Terminology）包列表。\n"
            "返回包名称、生效日期等信息。\n"
            "无需参数，可直接调用。"
        ),
        properties={"raw": raw_prop()},
        required=[],
    ),
    tool(
        "get_ct_package",
        description=(
            "获取指定控制术语包的详细信息。\n\n"
            "示例: package='sdtmct-2024-03-29'"
        ),
        properties={"package": _PACKAGE_PROP, "raw": raw_prop()},
        required=["package"],
    ),
    tool(
        "get_codelists",
        description=(
            "获取指定控制术语包中的所有编码列表（Codelist）。\n\n"
            "示例: package='sdtmct-2024-03-29'"
        ),
        properties={"package": _PACKAGE_PROP, "raw": raw_prop()},
        required=["package"],
    ),
    tool(
        "get_codelist",
        description=(
            "获取指定编码列表的详细信息（定义、是否可扩展等）。\n"
            "要拿列表里的全部术语用 get_codelist_terms。\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C667'"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "codelist": _CODELIST_PROP,
            "raw": raw_prop(),
        },
        required=["package", "codelist"],
    ),
    tool(
        "get_codelist_terms",
        description=(
            "获取指定编码列表中的所有术语（Terms），即可选的标准化值。\n"
            "瘦身后返回 refs: {术语名 -> 术语href}，href 末段即术语的 C 代码。\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C667'"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "codelist": _CODELIST_PROP,
            "raw": raw_prop(),
        },
        required=["package", "codelist"],
    ),
    tool(
        "get_term",
        description=(
            "获取指定术语的详细信息，包括定义、提交值(submissionValue)等。\n\n"
            "term 参数支持两种写法：\n"
            "1. 术语 C 代码，如 'C201972'\n"
            "2. 术语名称（不区分大小写），如 'Female'——会自动在 codelist 内解析成 C 代码；"
            "找不到时会返回相近的候选名\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C667', term='Female'"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "codelist": _CODELIST_PROP,
            "term": {
                "type": "string",
                "description": "术语 C 代码（如 C201972）或术语名称（如 Female）",
            },
            "raw": raw_prop(),
        },
        required=["package", "codelist", "term"],
    ),
]
