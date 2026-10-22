# get_datastructures - 获取 ADaM 分析数据结构清单

## 工具描述

获取 ADaM 产品（`adam` / `adamig`）包含的分析数据结构（ADSL、BDS、TTE）。
ADaM 侧**没有** `datasets` 端点，`get_datasets` 对 `adam`/`adamig` 一律 404，
必须先来这里取可用结构名。

## 使用方法

```typescript
mcp__cdisc-library__get_datastructures(standard: string, version: string, raw?: boolean)
```

**参数**：
- `standard` (必需): `adam` 或 `adamig`
- `version` (必需): 版本号，如 `1-3`，可传 `latest`
- `raw` (可选): `true` 返回未处理的原始 API 载荷

## 示例调用

```typescript
mcp__cdisc-library__get_datastructures({
  standard: "adamig",
  version: "latest"
})
```

## 返回结果示例（实测 ADaMIG v1.3，2026-10-22）

```json
{
  "datastructures": [
    {
      "name": "ADSL",
      "label": "Subject-Level Analysis Dataset Structure",
      "type": "Data Structure"
    },
    {
      "name": "BDS",
      "label": "Basic Data Structure",
      "type": "Data Structure"
    },
    {
      "name": "TTE",
      "label": "Basic Data Structure Time-to-Event",
      "type": "Data Structure"
    }
  ],
  "count": 3,
  "hrefTemplate": "/mdr/adam/adamig-1-3/datastructures/{name}",
  "product": {
    "name": "ADaMIG v1.3",
    "label": "Analysis Data Model Implementation Guide Version 1.3",
    "version": "1-3",
    "effectiveDate": "2021-11-29",
    "registrationStatus": "Final"
  }
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `datastructures[].name` | 数据结构名，取自 API href 末段（**保留准确大小写**），可直接传给其他工具的 `datastructure` 参数 |
| `datastructures[].label` | API 给出的显示名 |
| `count` | 数据结构总数 |
| `hrefTemplate` | 把 `{name}` 替换为结构名即得原始 API 路径 |
| `product` | 该产品自身的元数据 |

## 已知边界

- `standard='adam'`（ADaM 根模型 v2.1）的 `/datastructures` 端点**不列出任何结构**
  （`_links` 只有 `self`），此时 `count` 为 0。后续按名字请求会拿到带解释的 404 文案，
  提示改查 `adamig`。

## 使用场景

- 查 ADaM 变量前的第一步：确认这个项目版本里结构叫什么名
- 核对 IG 版本包含哪些数据结构

## 测试状态

✅ 通过 — 实测 ADaMIG v1.3 返回 ADSL / BDS / TTE 3 个结构；单测覆盖 URL 形状、
`latest` 解析、缓存命中与空清单边界。
