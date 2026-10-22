# get_datastructure_variables - 数据结构变量名清单

## 工具描述

列出一个分析数据结构的变量名与标签。对应 API 的
`/datastructures/{ds}/variables` 端点，是最省 token 的穷举方式。

**该端点不返回 `core` 与数据类型**（API 只给链接项），要整表请用
`get_datastructure`，要单变量定义用 `get_datastructure_variable`。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructure_variables(
  standard: string, version: string, datastructure: string, raw?: boolean
)
```

**参数**：
- `standard` (必需): `adam` / `adamig`
- `version` (必需): 如 `1-3`，可传 `latest`
- `datastructure` (必需): 如 `ADSL`（大小写不敏感）
- `raw` (可选): `true` 返回原始 `_links` 载荷

## 示例调用

```typescript
mcp__cdisc-library__get_datastructure_variables({
  standard: "adamig",
  version: "latest",
  datastructure: "ADSL"
})
```

## 返回结果示例（实测 ADaMIG v1.3；节选 4/141 行）

```json
{
  "variables": [
    {"name": "STUDYID", "label": "Study Identifier"},
    {"name": "SITEGRy", "label": "Pooled Site Group y"},
    {"name": "AGE", "label": "Age"},
    {"name": "AGEU", "label": "Age Units"}
  ],
  "count": 141,
  "hrefTemplate": "/mdr/adam/adamig-1-3/datastructures/ADSL/variables/{name}",
  "product": {
    "name": "ADSL",
    "label": "Subject-Level Analysis Dataset Structure",
    "class": "SUBJECT LEVEL ANALYSIS DATASET"
  }
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `variables[].name` | 变量名，取自 href 末段，**保留 API 的准确大小写**（`SITEGRy` 不是 `SITEGRY`） |
| `variables[].label` | 变量标签 |
| `count` | 变量条数 |
| `hrefTemplate` | 替换 `{name}` 得到该变量的原始 API 路径 |

每行的 `href` 与 `type`（全部为 `Analysis Variable`）被折叠为模板与省略，
141 行重复同一路径前缀纯耗 token（实测 23 KB → 13 KB）。

## 使用场景

- 只要变量名清单（如与项目数据集列名做包含性核对）
- 给 `get_datastructure_variable` 准备准确变量名

## 测试状态

✅ 通过 — 实测 ADaMIG v1.3 = 141 条、v1.1 也可按版本取；单测覆盖大小写保留、
去 `type` 噪声、`raw` 透传。
