# get_ct_package - 获取控制术语包详情

## 工具描述

返回 CT 包的元信息 + **分页的 codelist 索引**（每张表带 `termCount`）。

## 使用方法

```typescript
mcp__cdisc-library__get_ct_package(package: string, offset?: number, limit?: number, raw?: boolean)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`（大小写不敏感）
- `offset` / `limit` (可选): codelist 索引分页，默认 `0` / `200`，`limit` 上限 2000
- `raw` (可选): `true` 返回 API 原始整包载荷 —— **13 MB，慎用**

## 实测示例（2026-10-23，sdtmct-2024-03-29）

```typescript
mcp__cdisc-library__get_ct_package({ package: "sdtmct-2024-03-29", limit: 2 })
```

```json
{
  "name": "SDTM CT 2024-03-29",
  "label": "SDTM Controlled Terminology Package 57 Effective 2024-03-29",
  "version": "2024-03-29",
  "effectiveDate": "2024-03-29",
  "registrationStatus": "Final",
  "description": "CDISC Controlled Terminology for SDTM is the set of ...",
  "codelistCount": 1106,
  "termCount": 40126,
  "offset": 0,
  "limit": 2,
  "returned": 2,
  "hasMore": true,
  "codelists": [
    {
      "conceptId": "C141657",
      "name": "10-Meter Walk/Run Functional Test Test Code",
      "submissionValue": "TENMW1TC",
      "extensible": "false",
      "termCount": 4
    }
  ],
  "note": "整包 13 MB 的逐术语 submissionValue 不外发；按 conceptId 取某表的全部提交值用 get_codelist_submission_values。要原始整包载荷用 raw=true（会非常大，慎用）。"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `name` / `label` / `version` / `effectiveDate` / `registrationStatus` | 包元信息 |
| `codelistCount` | 包内 codelist 全量条数（1106） |
| `termCount` | 包内术语全量条数（40126） |
| `codelists[]` | 索引页：`conceptId` / `name` / `submissionValue`（变量名）/ `extensible` / `termCount` |
| `offset` / `limit` / `returned` / `hasMore` | 分页；翻页取完整索引 |

**这里的 `submissionValue` 是 codelist 的变量名**（如 `LBTESTCD`），不是术语提交值；
`codelists[]` 里**不含**内联术语。

## 关键行为：默认不发整包

API 的 `ct/packages/{package}` 把整包内联返回 —— 1106 张 codelist **及每张表的全部术语**
（含 `submissionValue`），实测 13,359,789 字符（13.36 MB）。

0.1.9 及以前本工具把这份载荷原样推过 stdio，**在任何常见 MCP 客户端上都会超时**
（客户端侧 60s 上限；瘦身对它无效，13,359,789 → 13,359,578 字符，只少了链接壳）。
现在默认只发索引：**44,146 字符**（经 stdio、带缩进；紧凑序列化 36,110），
  **缩小 303 倍**，命中缓存 0.12~0.2s。

包载荷仍被完整读取并缓存（24h），`get_codelist_submission_values` 就从这里取提交值 ——
**数据一个都没少，只是不再从 stdio 硬推**。

## 使用场景

- 按名称找 Codelist ID（避免拼错，如 `C667` 不存在、SEX 实为 `C66731`）
- 看某包有哪些表、各表多大（`termCount`），决定要不要整表下载
- 确认包的生效日期与注册状态

## 注意事项

- `raw=true` 会尝试推 13 MB 载荷，几乎必然触发客户端超时；需要提交值请改用
  `get_codelist_submission_values`（一次请求拿一张表）
- 整包下载设 **单次 45s 封顶超时、不重试**，最坏情况仍在 60s 客户端预算内
- 索引页 `limit` 上限 2000（>2000 自动截到 2000），全量索引需 6 页

## 测试状态

✅ 通过（单测 4 项 + 上述真实 API 实测）

⚠ 2026-10-23 校对：本文早期版本贴的是**单术语详情**载荷（`conceptId: C174106` +
`submissionValue`），与本工具无关，属复制粘贴错误；已按实测整篇重写。
