# get_codelist_terms - 获取编码术语列表

## 工具描述

获取特定编码列表中的所有术语（Terms）列表。

## 使用方法

```typescript
mcp__cdisc-library__get_codelist_terms(package: string, codelist: string)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`
- `codelist` (必需): 编码 ID，如 `C141657`

> **本端点不返回逐术语的 submissionValue**（见下方「返回结果示例」与「注意事项」）。
> 需要提交值请用 `get_codelist_submission_values`。

## 示例调用

```typescript
// 获取编码列表 C141657 中的所有术语
mcp__cdisc-library__get_codelist_terms({
  package: "sdtmct-2024-03-29",
  codelist: "C141657"
})
```

## 返回结果示例

> 以下两种载荷必须分清，否则会误以为批量接口带了提交值：

**A. 本端点（`.../codelists/{C}/terms`）实际返回的** —— 只有链接，无逐术语提交值；
顶部的 `submissionValue` 是 **codelist 自己的变量名**：

```json
{
  "conceptId": "C66731",
  "name": "Sex",
  "submissionValue": "SEX",
  "extensible": "false",
  "refs": {
    "Female": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66731/terms/C16576",
    "Intersex": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66731/terms/C45908",
    "Male": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66731/terms/C20197",
    "Unknown": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C66731/terms/C17998"
  }
}
```

`raw=true` 也只是把 `refs` 换成 `_links.terms[]`（`href` / `title` / `type`），
**仍不会多出 submissionValue 字段**——这是 Library API 的设计，不是瘦身剔除。

**B. 单个术语详情（`get_term`，即 `.../terms/{code}`）返回的** —— 才有提交值：

```json
{
  "conceptId": "C174106",
  "definition": "10-Meter Walk/Run - Was the 10-meter walk/run performed?",
  "preferredTerm": "10-Meter Walk/Run - Was Walk/Run Performed",
  "submissionValue": "TENMW101",
  "synonyms": ["TENMW1-Was Walk/Run Performed"]
}
```

## 返回字段说明

瘦身后响应把术语表放在 `refs`：**键是术语名，值是 href，href 末段即术语 C 代码**。
每个术语可用的字段：

| 字段 | 本端点 | `get_term` |
|------|--------|------------|
| 术语名 | ✅（`refs` 的键 / `_links.terms[].title`） | ✅ `preferredTerm` |
| 术语 C 代码 | ✅（href 末段） | ✅ `conceptId` |
| `submissionValue` | ❌ | ✅ |
| `definition` / `synonyms` | ❌ | ✅ |

> 注：顶部的 `submissionValue`（如 `LBTESTCD`）属于 **codelist 本身**（变量名），
> 不是术语的提交值，两者不要混淆。

## 使用场景

- 获取某个编码列表下所有可选的**术语名与 C 代码**
- 了解变量可以使用哪些标准化值（只要名字清单时比新工具更省）
- 需要 name + C 代码 + **提交值** 三列时，改用 `get_codelist_submission_values`

## 注意事项

- 如果编码列表不存在，会返回 404 错误
- **不返回逐术语提交值**，`raw=true` 也不返回；要批量提交值用
  `get_codelist_submission_values`（实测整表 1~2 次请求，而不是逐条 N 次）
- 大表响应可观：LBTESTCD（2397 术语）瘦身 **265,689** 字符、`raw=true` **457,921**
  字符，且本端点**无分页参数**，一口气全量返回；请优先考虑带分页的新工具
- `refs` 以术语名为键，同名术语会被 slim 加 `-2` / `-3` 后缀区分（不丢条目，
  但名字已不原样）；要严格按 API 名单逐行对齐，用新工具（它读 `_links` 而非名字键）

## 测试状态

✅ 测试通过 - 返回 C141657 编码列表的术语信息

⚠ 2026-10-23 校对：本文早期版本的「返回结果示例」贴的是**单术语详情载荷**（带
`submissionValue`），与本端点实际返回不符；已按实测改写为两种载荷对照。