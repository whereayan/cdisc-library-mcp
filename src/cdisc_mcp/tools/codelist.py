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
        "编码列表 ID，格式为 'C' + 数字，如 C66731(SEX), C65047(LBTESTCD)。"
        "ID 不能靠直觉拼：C667 不存在（SEX 实为 C66731），"
        "C141657 是 10-Meter Walk/Run Functional Test Test Code、与 LBTESTCD 无关。"
        "不确定某变量的 codelist ID 时，用 get_variable 看其 refs 里的 CT 引用，"
        "或 get_codelists 按名称查"
    ),
}

_CT_PAGE_LIMIT_PROPS = {
    "offset": {
        "type": "integer",
        "minimum": 0,
        "description": "分页起始下标（默认 0）",
    },
    "limit": {
        "type": "integer",
        "minimum": 1,
        "description": (
            "本页最多返回多少条（默认 200，上限 2000：超订会被钳到 2000 并在"
            "limitRequested 里回显请求值）；全量条数看响应里的计数字段，"
            "hasMore 判断要不要继续翻页"
        ),
    },
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
            "获取指定控制术语包详情：包元信息 + 分页的 codelist 索引（含每张表的 termCount）。\n"
            "整包载荷内联了**全部术语及其 submissionValue**（sdtmct 实测 1106 张表 / 13 MB），"
            "因此默认只发索引、不发内联术语；raw=true 会把 13 MB 原样推送，"
            "常见 MCP 客户端会在 60s 超时，请改用 get_codelist_submission_values 按表取。\n\n"
            "示例: package='sdtmct-2024-03-29'"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "offset": _CT_PAGE_LIMIT_PROPS["offset"],
            "limit": _CT_PAGE_LIMIT_PROPS["limit"],
            "raw": raw_prop(),
        },
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
            "要拿列表里的全部术语用 get_codelist_terms；要连提交值一起拿用"
            "get_codelist_submission_values。\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C66731'"
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
            "瘦身后返回 refs: {术语名 -> 术语href}，href 末段即术语的 C 代码。\n"
            "注意：本端点**不返回逐术语的 submissionValue**（顶部的 submissionValue 是"
            "codelist 自己的，如 LBTESTCD，不是术语的）；raw=true 也没有，"
            "这是 Library API 的设计而非瘦身剔除。要术语名+C 代码+提交值三列，"
            "用 get_codelist_submission_values。大表（如 LBTESTCD 2397 术语）"
            "本工具响应可达 26 万字符，建议改用新工具分页。\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C66731'"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "codelist": _CODELIST_PROP,
            "raw": raw_prop(),
        },
        required=["package", "codelist"],
    ),
    tool(
        "get_codelist_submission_values",
        description=(
            "分页返回编码列表的全部术语及其提交值（submissionValue），三列："
            "C 代码 / 术语名 / 提交值。\n"
            "一次读取包级载荷即可覆盖整表，**不需要逐术语调用 get_term**"
            "（260 个术语实测约 150s / 260 次，本工具整表只需 1~2 次）；"
            "只有包载荷缺失的术语才回退到单条详情，并在"
            "termsResolvedByDetailRequest 里告知回数。\n"
            "可只查名字与提交值（fields='name,submissionValue'），"
            "或加上 definition / synonyms。\n"
            "翻页看 total / hasMore；LBTESTCD（2397 术语）单页上限 2000，需两页。\n"
            "单条术语的完整详情仍用 get_term（支持按术语名查）。\n\n"
            "示例: package='sdtmct-2024-03-29', codelist='C66731' -> "
            "[{code: C16576, name: Female, submissionValue: F}, ...]"
        ),
        properties={
            "package": _PACKAGE_PROP,
            "codelist": _CODELIST_PROP,
            "fields": {
                # array OR a comma/space separated string: the client accepts both,
                # so the schema must not reject the shorter form agents tend to send.
                "anyOf": [
                    {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "code", "name", "submissionValue",
                                "definition", "synonyms",
                            ],
                        },
                    },
                    {"type": "string"},
                ],
                "description": (
                    "每行要返回的列，默认 code,name,submissionValue；"
                    "可选加 definition 或 synonyms。数组或逗号分隔字符串皆可"
                ),
            },
            "offset": _CT_PAGE_LIMIT_PROPS["offset"],
            "limit": _CT_PAGE_LIMIT_PROPS["limit"],
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
            "示例: package='sdtmct-2024-03-29', codelist='C66731', term='Female'"
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
