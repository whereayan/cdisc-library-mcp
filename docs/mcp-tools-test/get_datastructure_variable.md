# get_datastructure_variable - 数据结构中的单个变量详情

## 工具描述

获取某个分析数据结构里单个变量的定义：`core`、数据类型、`description`、
所属变量集（`refs` 中）。对应 API 的 `/datastructures/{ds}/variables/{var}`。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructure_variable(
  standard: string, version: string, datastructure: string, variable: string
)
```

**参数**：
- `standard` (必需): `adam` / `adamig`
- `version` (必需): 如 `1-3`，可传 `latest`
- `datastructure` (必需): 如 `ADSL`
- `variable` (必需): 如 `AGE`；大小写不敏感

## 示例调用

```typescript
mcp__cdisc-library__get_datastructure_variable({
  standard: "adamig",
  version: "latest",
  datastructure: "ADSL",
  variable: "sitegry"          // 传小写也能命中
})
```

## 返回结果示例（实测 ADaMIG v1.3 的 AGE）

```json
{
  "core": "Req",
  "description": "DM.AGE. If analysis needs require a derived age that does no…",
  "label": "Age",
  "name": "AGE",
  "ordinal": "1",
  "simpleDatatype": "Num",
  "refs": {
    "Subject-Level Analysis Dataset Structure": "/mdr/adam/adamig-1-3/datastructures/ADSL",
    "Analysis Data Model Implementation Guide Version 1.3": "/mdr/adam/adamig-1-3",
    "ADSL Subject Demographics": "/mdr/adam/adamig-1-3/datastructures/ADSL/varsets/SubjectDemographics",
    "Age": "/mdr/adam/adamig-1-2/datastructures/ADSL/variables/AGE"
  }
}
```

`refs` 是全局瘦身结果（`_links` 折叠为标签→href），末条即上一版本的同名变量，
可顺着它做前后版对照。

## 关键实现点：大小写还原

API 路径**区分大小写**，而 ADaM 的模式变量刻意混合大小写：`SITEGRy`、`APHASEw`、
`TRxxPGy`、`STRATwR`。直接把入参 `upper()` 会得到 `SITEGRY` 并 404。
因此工具先用变量清单把入参解析成 href 末段的准确写法，再发请求。

## 错误行为

变量名不存在时报错并给出相近名（如 `AGEUUX` → 提示 `AGEU, AGE, AAGE, AGEGRy, AGEGRyN`），
且**不会**发出无效请求。

## 使用场景

- 核对某个变量的 Core 级别与派生来源（`description` 常写明来自哪个 SDTM 变量）
- 查变量所属变量集与跨版本链接

## 测试状态

✅ 通过 — 实测 AGE / SITEGRy 均命中；单测覆盖小写入参还原、未知变量名报错文案、
无效请求未发出。
