# CDISC Library MCP 工具测试文档

## 概述

本文档汇总了 cdisc-library MCP 服务的所有工具测试结果。每个工具都有独立的详细测试文档。

## 测试时间

2026-04-08

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
