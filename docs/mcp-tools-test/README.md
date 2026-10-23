# CDISC Library MCP 工具测试文档

## 概述

本文档汇总了 cdisc-library MCP 服务的所有工具测试结果。每个工具都有独立的详细测试文档。

## 测试时间

2026-04-08（2026-10-23 复核 CT 工具组：`get_ct_package` / `get_codelist_terms` 两篇示例载荷系复制粘贴错误，已按实测重写；新增 `get_codelist_submission_values`）

## 工具列表

| 序号 | 工具名称 | 功能描述 | 测试状态 | 文档链接 |
|------|----------|----------|----------|----------|
| 1 | get_products | 获取所有 CDISC 产品列表 | ✅ 通过 | [get_products.md](get_products.md) |
| 2 | get_ct_packages | 获取控制术语包列表 | ✅ 通过 | [get_ct_packages.md](get_ct_packages.md) |
| 3 | search | 全局搜索 CDISC Library | ✅ 通过 | [search.md](search.md) |
| 4 | get_ct_package | 获取控制术语包详情 | ✅ 通过 | [get_ct_package.md](get_ct_package.md) |
| 5 | get_codelists | 获取编码列表 | ✅ 通过 | [get_codelists.md](get_codelists.md) |
| 6 | get_standard | 获取标准产品信息 | ✅ 通过 | [get_standard.md](get_standard.md) |
| 7 | get_datasets | 获取数据集列表 | ✅ 通过 | [get_datasets.md](get_datasets.md) |
| 8 | get_classes | 获取标准的类列表 | ✅ 通过 | [get_classes.md](get_classes.md) |
| 9 | get_codelist | 获取编码详情 | ✅ 通过 | [get_codelist.md](get_codelist.md) |
| 10 | get_codelist_terms | 获取编码术语列表 | ✅ 通过 | [get_codelist_terms.md](get_codelist_terms.md) |
| 11 | get_term | 获取术语详情 | ✅ 通过 | [get_term.md](get_term.md) |
| 12 | get_dataset | 获取数据集详情 | ✅ 通过 | [get_dataset.md](get_dataset.md) |
| 13 | get_dataset_variables | 获取数据集变量列表 | ✅ 通过 | [get_dataset_variables.md](get_dataset_variables.md) |
| 14 | get_variable | 获取变量详情 | ✅ 通过 | [get_variable.md](get_variable.md) |
| 15 | compare_versions | 版本差异比较 | ✅ 通过 | [compare_versions.md](compare_versions.md) |
| 16 | get_datastructures | 获取 ADaM 分析数据结构清单 | ✅ 通过 | [get_datastructures.md](get_datastructures.md) |
| 17 | get_datastructure | 获取单个数据结构完整变量表 | ✅ 通过 | [get_datastructure.md](get_datastructure.md) |
| 18 | get_datastructure_variables | 获取数据结构变量名清单 | ✅ 通过 | [get_datastructure_variables.md](get_datastructure_variables.md) |
| 19 | get_datastructure_variable | 获取数据结构单变量详情 | ✅ 通过 | [get_datastructure_variable.md](get_datastructure_variable.md) |
| 20 | get_datastructure_varsets | 获取数据结构变量集清单 | ✅ 通过 | [get_datastructure_varsets.md](get_datastructure_varsets.md) |
| 21 | get_datastructure_varset | 获取单个变量集详情 | ✅ 通过 | [get_datastructure_varset.md](get_datastructure_varset.md) |
| 22 | get_codelist_submission_values | 批量获取术语提交值（0.1.10+） | ✅ 通过 | [get_codelist_submission_values.md](get_codelist_submission_values.md) |

## 测试参数汇总

### 标准和版本

| 标准 | 测试版本 |
|------|----------|
| sdtm | 1-7, 1-8, 2-1 |
| sdtmig | 3-3, 3-4 |
| adam | 多个版本（通过 get_products 获取） |

### 控制术语包

| 包名称 | 说明 |
|--------|------|
| sdtmct-2024-03-29 | SDTM Controlled Terminology Package 57 |

### 数据集

| 数据集 | 类 | 描述 |
|--------|-----|------|
| DM | Special-Purpose | Demographics（人口统计学） |
| AE | Events | Adverse Events（不良事件） |

### 变量

| 数据集 | 变量 | 描述 |
|--------|------|------|
| DM | USUBJID | Unique Subject Identifier（受试者唯一标识符） |

### 编码和术语

| 编码 ID | 术语 ID | 描述 |
|---------|---------|------|
| C141657 | C174106 | 10-Meter Walk/Run - Was Walk/Run Performed |

## 注意事项

1. **编码 ID 必须存在**: 使用 `get_codelist`、`get_codelist_terms`、`get_term` 时，编码 ID 必须在指定的包中存在，否则返回 404 错误。例如 C667 在 sdtmct-2024-03-29 中不存在。

2. **大结果集**: 
   - `get_products`: 约 60KB
   - `search`: 约 226KB
   - `get_dataset`: 约 57KB
   - `compare_versions`: 约 15MB

   这些工具返回结果较大，建议按需使用。

3. **版本格式**: 版本号使用 `x-y` 格式，如 `1-8`、`3-4`，而非 `1.8`、`3.4`。

## 使用建议

### 快速入门流程

```
1. get_products() → 了解可用标准
2. get_standard(standard, version) → 获取标准详情
3. get_classes(standard, version) → 查看类列表
4. get_datasets(standard, version) → 查看数据集列表
5. get_dataset(standard, version, dataset) → 获取数据集详情
6. get_variable(standard, version, dataset, variable) → 获取变量详情
```

ADaM / ADaMIG 走另一条路（没有 datasets 端点）：

```
1. get_datastructures(standard='adamig', version='latest') → 看有哪些结构
2. get_datastructure(..., datastructure='ADSL') → 完整变量表（含 core / 类型）
3. get_datastructure_varsets / varset(..., varset='Treatment') → 按集下钻取 description
4. get_datastructure_variable(..., variable='AGE') → 单变量定义
```

### 术语查询流程

```
1. get_ct_packages() → 查看术语包
2. get_codelists(package) → 查看编码列表
3. get_codelist(package, codelist) → 获取编码详情
4. get_term(package, codelist, term) → 获取具体术语
```

### 搜索流程

```
search(query) → 直接搜索关键词
```

## 工具使用声明

- 使用 MCP：cdisc-library
- 调用 Skill：无
- 遵循 Rule：anya-persona-priority-rule.md、priority-rules.md、python-environment-guidelines.md、tool-usage-declaration.md
---

## 0.1.6 变更说明（2026-10）

本目录各文档是 0.1.4/0.1.5 时期的测试快照，其中「返回结果示例」为**原始 API 载荷**。
0.1.6 起工具行为有以下全局变化，阅读旧快照时请注意：

1. **响应默认瘦身**：所有工具默认剥除 `_links`/`links`/`@search.*` 噪声，
   链接块折叠为紧凑的 `refs`（标签 → href）映射；每个工具新增可选参数
   `raw`（boolean，默认 false），传 `true` 返回未瘦身的原始载荷（即旧快照中的形态）。
2. **`standard` 参数改为 enum**：只接受 `sdtm, sdtmig, sendig, adam, adamig, cdash, cdashig`。
3. **`version` 支持 `'latest'`**：所有带 version 的工具都可传 `'latest'`，
   由产品列表解析出当前最新数字版本（如 sdtmig → 3-4）。
4. **ADaM URL 修复**：ADaM 基础模型正确路径是 `/mdr/adam/adam-2-1`
   （旧版拼的 `/mdr/adam/2-1` 实为 404），`standard='adam'` 从 0.1.6 起才真正可用。
5. 签名变化的工具：`search`、`compare_versions`、`get_term`，
   详见各自文档（已按 0.1.6 更新）。
6. 所有工具带 `readOnlyHint=true` 注解（全部为只读 GET）。

---

## 0.1.9 变更说明（2026-10-22）

新增 6 个 ADaM 数据结构工具（序号 16–21），对应之前**完全没有实现**的
`/mdr/adam/{product}/datastructures` 端点组。

1. **ADaM 查变量以前只能走 `get_standard`**：实测
   `get_dataset_variables(adamig, …, ADSL)`、`get_dataset`、`get_datasets`、
   `get_variable` 全部 404（该服务拼的是 `/datasets` 路径，ADaM 产品没有这个段），
   而 `search(query='ADSL', type='Analysis Variable')` 只返回 31 条且跨四个版本混排
   —— 它按文本相关度匹配，而大多数 ADSL 变量的 label/description 里并不出现
   “ADSL”字样，属于**静默残缺**，不能用来穷举。
2. **旧 dataset 工具现在本地报错并指名正确工具**：`get_datasets` 等四个工具对
   `adam` / `adamig` 不再发出必定 404 的请求，而是报错说明「ADaM 元数据在
   datastructures 下」并给出可执行的替代调用。
3. **变量名大小写还原**：API 路径区分大小写，而 ADaM 模式变量故意混写
   （`SITEGRy` / `APHASEw` / `TRxxPGy`），故入参不 `upper()`，而是从变量清单
   解析出准确末段。实测传 `sitegry` 能命中 `SITEGRy`。
4. **默认紧凑视图**：`get_datastructure` 默认去 description（171,782 → 15,169 字符），
   清单类工具把逐行重复的 href 收敛为 `hrefTemplate`（23,048 → 13,264 字符），
   变量集详情默认保留 description（9,949 → 2,431 字符）；均保留 `raw=true` 逃生舱。
5. 未修两项（本次范围外，已实测存在）：`search` 服务端只返首页 100 条，
   `offset>100` 返 0 条但 `hasMore` 仍为 `true`；`get_standard` 对 ADaMIG 返回整本 IG
   （约 353 KB）且无按结构过滤的参数。
