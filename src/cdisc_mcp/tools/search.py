"""Search and version-comparison tools."""

from ._common import raw_prop, standard_prop, tool


SEARCH_TOOLS = [
    tool(
        "search",
        description=(
            "全局搜索 CDISC Library，可搜索标准、数据集、变量、术语等。\n"
            "命中按相关度排序；结果在客户端缓存 24h。\n\n"
            "参数说明：\n"
            "- query: 搜索关键词，如 'sdtm', 'adverse event', 'DM', 'AVAL'\n"
            "- type: 可选，按命中类型过滤（不区分大小写），如 'Analysis Variable'\n"
            "- limit / offset: 可选，客户端分页，如 limit=20, offset=20 取第 21-40 条\n\n"
            "示例: query='AVAL', type='Analysis Variable', limit=10"
        ),
        properties={
            "query": {
                "type": "string",
                "description": "搜索关键词，如 sdtm, adverse event, DM",
            },
            "type": {
                "type": "string",
                "description": "按命中类型过滤，如 'Analysis Variable'、'Variable'、'Dataset'；不传则不过滤",
            },
            "limit": {
                "type": "integer",
                "description": "最多返回的命中条数（客户端截断）",
                "minimum": 0,
            },
            "offset": {
                "type": "integer",
                "description": "跳过的命中条数（与 limit 配合做分页），默认 0",
                "minimum": 0,
            },
            "raw": raw_prop(),
        },
        required=["query"],
    ),
    tool(
        "compare_versions",
        description=(
            "比较同一标准两个版本的差异。\n\n"
            "默认返回摘要视图（各差异分区名称与行数 + Info 分区内容），"
            "因为完整 diff 载荷可达数十 MB，不适合直接进上下文。\n"
            "要看某分区详情：传 section='<分区名>'（名称来自摘要里的 sections 索引），"
            "并用 max_rows 控制返回行数（默认 200，超出会标注 truncated）。\n\n"
            "参数说明：\n"
            "- standard: 标准名称，如 sdtmig, adamig\n"
            "- old_version / new_version: 旧/新版本号，支持 '3-3'/'3.3'/'latest'；"
            "传反了会自动交换并在响应 note 中说明\n\n"
            "示例: standard='sdtmig', old_version='3-3', new_version='3-4'\n"
            "再下钻: section='Domains', max_rows=50"
        ),
        properties={
            "standard": standard_prop(),
            "old_version": {
                "type": "string",
                "description": "旧版本号，支持 '3-3'/'3.3'/'latest'",
            },
            "new_version": {
                "type": "string",
                "description": "新版本号，支持 '3-4'/'3.4'/'latest'",
            },
            "section": {
                "type": "string",
                "description": "只返回指定差异分区的明细行；不传则返回全部分区的摘要索引",
            },
            "max_rows": {
                "type": "integer",
                "description": "section 明细模式下最多返回的行数，默认 200",
                "minimum": 0,
            },
            "raw": {
                "type": "boolean",
                "description": (
                    "true 时返回未汇总的完整 diff 载荷——警告：可达数十 MB，"
                    "极耗 token，仅在确有必要时使用；默认 false（摘要视图）"
                ),
            },
        },
        required=["standard", "old_version", "new_version"],
    ),
]
