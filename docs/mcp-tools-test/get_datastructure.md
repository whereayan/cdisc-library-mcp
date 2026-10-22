# get_datastructure - 获取单个数据结构的完整变量表

## 工具描述

获取一个分析数据结构的变量表，按变量集分组，每变量一行
（`name` / `label` / `core` / `datatype`）。
这是**唯一**整表带 `core`（Required/Exp/Perm）与数据类型的来源，
因此「ADSL 有哪些变量」这类问题应该用它，而不是 `get_dataset_variables`
（后者对 ADaM 是 404）或 `search`（按文本匹配，会静默漏掉多数变量）。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructure(
  standard: string, version: string, datastructure: string, raw?: boolean
)
```

**参数**：
- `standard` (必需): `adam` / `adamig`
- `version` (必需): 如 `1-3`，可传 `latest`
- `datastructure` (必需): 如 `ADSL`、`BDS`；大小写与空格/连字符不敏感（`adsl` 可用）
- `raw` (可选): `true` 返回完整原始载荷（含每变量的 description，很大）

## 示例调用

```typescript
mcp__cdisc-library__get_datastructure({
  standard: "adamig",
  version: "latest",
  datastructure: "ADSL"
})
```

## 返回结果示例（实测 ADaMIG v1.3；变量行节选，其余同构）

```json
{
  "datastructure": "ADSL",
  "label": "Subject-Level Analysis Dataset Structure",
  "description": "One record per subject.",
  "class": "SUBJECT LEVEL ANALYSIS DATASET",
  "totalVariables": 141,
  "variableSetCount": 9,
  "variableSets": [
    {
      "varset": "Identifier",
      "label": "ADSL Identifier",
      "count": 8,
      "variables": [
        {"name": "STUDYID", "label": "Study Identifier", "core": "Req", "datatype": "Char"},
        {"name": "SITEGRy", "label": "Pooled Site Group y", "core": "Perm", "datatype": "Char"}
      ]
    },
    {
      "varset": "PopulationIndicator",
      "label": "ADSL Population Indicator",
      "count": 7,
      "variables": [
        {"name": "FASFL", "label": "Full Analysis Set Population Flag", "core": "Cond", "datatype": "Char"}
      ]
    }
  ],
  "note": "core: Req=Required, Cond=Conditionally Required, Perm=Permissible. ..."
}
```

实测 9 个变量集与计数：Identifier 8、SubjectDemographics 9、PopulationIndicator 7、
Treatment 18、Dose 3、TreatmentTiming 20、PeriodSubperiodandPhaseTiming 32、
TrialExperience 35、Stratification 9，合计 141。实测紧凑视图 15,169 字符，
同一数据结构的原始载荷 171,782 字符（11.3 倍）。

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `totalVariables` | 模式变量总数（非实际列数，见下） |
| `variableSetCount` | 非空变量集个数（空集不列入） |
| `variableSets[].varset` | 变量集 slug，可传给 `get_datastructure_varset` |
| `variables[].core` | `Req` / `Cond` / `Perm` |
| `variables[].datatype` | `Char` / `Num` |
| `note` | 口径提示 |

## 重要口径

名称中的 `xx` / `w` / `y` 是**模式占位**（周期、分层因子、分组），
ADaM IG 用它们表示「按项目展开」，所以 `totalVariables=141` 不等于任何项目
ADSL 数据集的实际列数。

## 错误行为

- 结构名不存在：报错并列出该产品可用结构名，**不会**发出无效请求
- 产品未列出任何结构（`adam` 根模型）：404 文案额外说明「名称无从校验」并指向 `adamig`

## 使用场景

- 逐变量核对项目 ADSL 是否缺 Required 变量
- 生成 ADSL 变量清单/元数据基线

## 测试状态

✅ 通过 — 实测 ADaMIG v1.3 ADSL 返回 141 变量 / 9 变量集；单测覆盖紧凑视图去
description、空变量集剔除、`raw` 透传、缓存命中。
