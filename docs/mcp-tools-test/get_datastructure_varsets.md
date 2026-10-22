# get_datastructure_varsets - 数据结构的变量集清单

## 工具描述

列出一个分析数据结构包含的变量集（Identifier、Treatment、Trial Experience 等）。
对应 API 的 `/datastructures/{ds}/varsets`。

**变量集名跨版本不稳定**，下钻前应先来这里取当版可用名称：
ADaMIG v1.1 的 slug 是 `SubjectDemographics`、显示名 `ADSL Subject Demographics Variables`，
v1.3 显示名缩为 `ADSL Identifier` 等，v1.2 的 slug 又与 v1.3 不完全一致。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructure_varsets(
  standard: string, version: string, datastructure: string, raw?: boolean
)
```

**参数**：
- `standard` (必需): `adam` / `adamig`
- `version` (必需): 如 `1-3`，可传 `latest`
- `datastructure` (必需): 如 `ADSL`
- `raw` (可选): `true` 返回原始 `_links` 载荷

## 示例调用

```typescript
mcp__cdisc-library__get_datastructure_varsets({
  standard: "adamig",
  version: "latest",
  datastructure: "ADSL"
})
```

## 返回结果示例（实测 ADaMIG v1.3，全 9 条）

```json
{
  "variableSets": [
    {"name": "Identifier", "label": "ADSL Identifier", "type": "Variable Set"},
    {"name": "SubjectDemographics", "label": "ADSL Subject Demographics", "type": "Variable Set"},
    {"name": "PopulationIndicator", "label": "ADSL Population Indicator", "type": "Variable Set"},
    {"name": "Treatment", "label": "ADSL Treatment", "type": "Variable Set"},
    {"name": "Dose", "label": "ADSL Dose", "type": "Variable Set"},
    {"name": "TreatmentTiming", "label": "ADSL Treatment Timing Variables", "type": "Variable Set"},
    {"name": "PeriodSubperiodandPhaseTiming", "label": "ADSL Period, Subperiod, and Phase Timing", "type": "Variable Set"},
    {"name": "TrialExperience", "label": "ADSL Trial Experience", "type": "Variable Set"},
    {"name": "Stratification", "label": "ADSL Stratification", "type": "Variable Set"}
  ],
  "count": 9,
  "hrefTemplate": "/mdr/adam/adamig-1-3/datastructures/ADSL/varsets/{name}"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `variableSets[].name` | 变量集 slug（href 末段，可直接传给 `get_datastructure_varset` 的 `varset`） |
| `variableSets[].label` | 当版显示名 |
| `count` | 变量集条数 |

## 使用场景

- 变量集名报错时（工具会列出可用名称），先来这里确认当版拼法
- 按变量集逐块核对项目 ADSL 是否覆盖 Required 变量

## 测试状态

✅ 通过 — 实测 ADaMIG v1.3 = 9 个变量集；单测覆盖清单解析与紧凑输出。
