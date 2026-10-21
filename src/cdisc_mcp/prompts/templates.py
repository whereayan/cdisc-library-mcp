"""Prompt templates for CDISC Library.

Keep tool signatures below in sync with src/cdisc_mcp/tools/*.py — a prompt
that advertises a parameter the tool does not accept teaches the model to
hallucinate calls (0.1.5 shipped `search(query, scope?)`, which never existed).
"""


PROMPT_TEMPLATES = {
    "explore_standard": """你是一个 CDISC 标准专家。帮助用户探索 {standard} 标准。

步骤：
1. 首先使用 get_standard 获取 {standard} 的基本信息
2. 使用 get_classes 或 get_datasets 获取可用类/数据集
3. 根据用户兴趣深入探索具体内容

可用的工具：
- get_products() - 获取所有产品列表
- get_standard(standard, version) - 获取标准信息
- get_classes(standard, version) - 获取类列表
- get_datasets(standard, version) - 获取数据集列表
- get_dataset(standard, version, dataset) - 获取数据集元数据
- get_dataset_variables(standard, version, dataset) - 获取数据集的完整变量列表
- get_variable(standard, version, dataset, variable) - 获取变量详情

参数说明：
- standard: {standard}
- version: 用户指定的版本；如未指定，传 'latest' 自动解析为最新版
""",

    "find_variable": """帮助用户查找与 "{keyword}" 相关的变量。

步骤：
1. 使用 search 工具搜索关键词（可用 type 过滤、limit/offset 分页）
2. 分析搜索结果中的变量
3. 使用 get_variable 获取详细信息

搜索关键词: {keyword}

可用的工具：
- search(query, type?, limit?, offset?) - 全局搜索
- get_variable(standard, version, dataset, variable) - 获取变量详情（version 可传 'latest'）
""",

    "find_terminology": """帮助用户查找与 "{keyword}" 相关的控制术语。

步骤：
1. 使用 search 工具搜索关键词
2. 使用 get_ct_packages 获取 CT 包列表
3. 使用 get_codelists 获取相关编码列表
4. 使用 get_codelist_terms 获取术语详情

搜索关键词: {keyword}

可用的工具：
- search(query, type?, limit?, offset?) - 全局搜索
- get_ct_packages() - 获取 CT 包列表
- get_codelists(package) - 获取编码列表
- get_codelist(package, codelist) - 获取编码详情
- get_codelist_terms(package, codelist) - 获取术语列表
- get_term(package, codelist, term) - 获取术语详情（term 支持 C 代码或术语名，如 'Female'）
""",

    "compare_standards": """帮助用户比较 {standard} 的不同版本。

步骤：
1. 使用 compare_versions 获取差异摘要（分区索引 + Info）
2. 对关心的分区传 section='<分区名>' 下钻明细
3. 总结主要变化

标准: {standard}

可用的工具：
- get_standard(standard, version) - 获取标准信息（version 可传 'latest'）
- compare_versions(standard, old_version, new_version, section?, max_rows?) - 版本比较
""",

    "validate_dataset": """检查 {dataset} 数据集是否符合 {standard} 标准。

步骤：
1. 使用 get_dataset_variables 获取标准变量定义
2. 检查必需变量列表（Core = Req/Exp）
3. 验证变量属性是否符合要求

标准: {standard}
数据集: {dataset}

可用的工具：
- get_datasets(standard, version) - 获取数据集列表
- get_dataset(standard, version, dataset) - 获取数据集元数据
- get_dataset_variables(standard, version, dataset) - 获取变量列表
- get_variable(standard, version, dataset, variable) - 获取单变量详情
""",
}
