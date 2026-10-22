# get_datastructure_varset - 单个变量集详情（含 description）

## 工具描述

获取一个变量集的内容，**保留每个变量的 `description`**。
单个变量集体量小（ADSL 最大的一集 35 个变量），因此这是「按集下钻查定义」的
推荐入口，比拉整个数据结构（`get_datastructure`）省得多。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructure_varset(
  standard: string, version: string, datastructure: string, varset: string, raw?: boolean
)
```

**参数**：
- `standard` (必需): `adam` / `adamig`
- `version` (必需): 如 `1-3`，可传 `latest`
- `datastructure` (必需): 如 `ADSL`
- `varset` (必需): slug 或显示名皆可，见下
- `raw` (可选): `true` 返回原始载荷

## 示例调用

```typescript
// 四种写法命中同一个变量集
mcp__cdisc-library__get_datastructure_varset({
  standard: "adamig", version: "latest", datastructure: "ADSL",
  varset: "SubjectDemographics"          // 或 "subject demographics"
})                                        // 或 "ADSL Subject Demographics"
                                          // 或 "subjectdemographics"
```

## 返回结果示例（实测 ADaMIG v1.3 的 SubjectDemographics）

```json
{
  "varset": "SubjectDemographics",
  "label": "ADSL Subject Demographics",
  "datastructure": "ADSL",
  "count": 9,
  "variables": [
    {
      "name": "AGE",
      "label": "Age",
      "core": "Req",
      "datatype": "Num",
      "description": "DM.AGE. If analysis needs require a derived age that does not match the SDTM AGE, the derived age should be included in AGE, not AAGE."
    }
  ],
  "note": "变量集级视图（含 description）。core: Req=Required, Cond=Conditionally Required, Perm=Permissible"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `varset` | 解析后的准确 slug |
| `datastructure` | 从 self href 反推的所属数据结构名 |
| `variables[].description` | 变量定义与派生来源（多数写明对应的 SDTM 变量） |

每变量的 `_links` 块被去掉（同一个集内 9 份重复链接噪声），实测单集输出约 2.4 KB。

## varset 解析规则

slug 与显示名都接受，大小写/空格/连字符/逗号不敏感，且会自动去掉前导的结构名
（`ADSL `）。名称不存在时报错并列出当版全部可用变量集，不会发出无效请求。

## 使用场景

- 写 ADSL 派生文档时取每个变量的官方定义原文
- 核对项目变量是否覆盖了集内全部 Required 变量

## 测试状态

✅ 通过 — 实测 4 种拼法命中同一变量集且只发一次请求；单测覆盖 description 保留、
紧凑输出、未知变量集名报错文案。
