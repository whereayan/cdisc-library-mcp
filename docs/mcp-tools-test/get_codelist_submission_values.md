# get_codelist_submission_values - 批量获取术语提交值

## 工具描述

分页返回一个编码列表（Codelist）的全部术语及其**提交值（submissionValue）**，
默认三列：`code`（C 代码）/ `name`（术语名）/ `submissionValue`。

## 为什么需要它

CDISC Library API 的 codelist `terms` 端点是**唯一的批量术语清单来源，但它不带
逐术语提交值**——`_links.terms[]` 只有 `href` / `title` / `type`，`raw=true` 也不会多给
一个字段（这是 API 设计，不是本服务瘦身删掉的）。而该端点响应**顶部**的
`submissionValue` 是 codelist 自己的变量名（`LBTESTCD`、`SEX`），极易被误读成术语提交值。

提交值只存在于两处：

| 来源 | 覆盖范围 | 请求数 |
|------|----------|--------|
| 包级载荷 `ct/packages/{package}` | 整包 1106 张表、40126 个术语，全部内联 submissionValue | **1**（13 MB，服务端缓存 24h） |
| 单术语详情 `.../terms/{code}` | 一条 | N（实测 ~566ms/条，260 条约 150s） |

本工具读前者，因此**整表一次请求**；只有包载荷缺的那几条才回退到详情请求。

## 使用方法

```typescript
mcp__cdisc-library__get_codelist_submission_values(
  package: string,          // 必需
  codelist: string,         // 必需，如 C66731(SEX)、C65047(LBTESTCD)
  fields?: string[],        // 默认 ["code","name","submissionValue"]，可加 definition / synonyms
  offset?: number,          // 默认 0
  limit?: number,           // 默认 200，上限 2000
  raw?: boolean             // true 时每行给出 API 的全部字段
)
```

## 实测示例（2026-10-23，sdtmct-2024-03-29）

```typescript
mcp__cdisc-library__get_codelist_submission_values({
  package: "sdtmct-2024-03-29",
  codelist: "C66731"
})
```

```json
{
  "package": "sdtmct-2024-03-29",
  "codelist": "C66731",
  "codelistName": "Sex",
  "codelistSubmissionValue": "SEX",
  "extensible": "false",
  "fields": ["code", "name", "submissionValue"],
  "total": 4,
  "offset": 0,
  "limit": 200,
  "returned": 4,
  "hasMore": false,
  "valueSource": "package",
  "termsResolvedByDetailRequest": 0,
  "terms": [
    { "code": "C16576", "name": "Female",   "submissionValue": "F" },
    { "code": "C45908", "name": "Intersex", "submissionValue": "INTERSEX" },
    { "code": "C20197", "name": "Male",     "submissionValue": "M" },
    { "code": "C17998", "name": "Unknown",  "submissionValue": "U" }
  ]
}
```

大表实测（LBTESTCD，2397 个术语）：

| 场景 | HTTP 请求数 | 耗时 | 提交值覆盖 |
|------|-------------|------|------------|
| 冷启动（整包 13 MB 未缓存） | 2 | 26.1s | 2397/2397 |
| 命中包缓存 | 1 | 0.1~2.6s | 全部 |
| 旧办法逐条 `get_term` | 260 | ~150s | 260/260 |

**响应体积（经 stdio，工具层带缩进）**：

| 请求 | 字符数 |
|------|--------|
| `limit=200`（默认） | 25,308 |
| `limit=300` | 30,300 |
| `limit=2000`（上限） | 247,609 |
| 同上 + `fields` 加 `synonyms` | 54,846 / 300 条 |
| `raw=true`（limit=2000） | 707,533 —— 不建议 |
| SEX（4 条，默认列） | 743 |

单页上限 2000 会被钳制（`limitRequested` 回显你请求的值），所以 **2397 条要翻两页**：

```typescript
// 第一页 limit=2000 -> returned=2000, hasMore=true
// 第二页 offset=2000, limit=2000 -> returned=397, hasMore=false
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `total` | 该表术语全量条数（来自 codelist `terms` 端点的权威名单） |
| `returned` / `hasMore` / `offset` / `limit` | 分页信息 |
| `valueSource` | `package`（全部来自包载荷）/ `package+term-detail`（有补齐）/ `term-detail`（包载荷不可用，全部逐条查） |
| `termsResolvedByDetailRequest` | 本页里靠单术语详情请求补齐的条数（0 表示零额外往返） |
| `codelistSubmissionValue` | **codelist 的变量名，不是术语提交值**，单列以免混淆 |
| `terms[]` | 按 `fields` 选列的行；名称/代码优先取 API 值，缺失时回退到链接里的 title |

## 使用场景

- 建 SDTM/ADaM 数据集时，需要某 CT 表「术语名 ↔ 提交值」的完整对照
- 做 mapping / 校验程序时把提交值整表加载成字典（一次请求，别写循环）
- 需要术语定义或同义词时加 `fields`，仍是一次请求

## 注意事项

- 名单以 codelist `terms` 端点为准，因此**同名术语各占一行**，不会被名字键合并
- Codelist ID 不能靠直觉拼：`C667` 不存在，SEX 实为 `C66731`；不确定时先
  `get_codelists` 按名称查，或 `get_variable` 看 `refs`
- 包载荷下载设置了单次 45s 封顶超时且不重试；失败时本工具自动降级为逐条详情，
  数据不丢，只是变慢（看 `valueSource` 判断）
- 只要名称+C 代码、不需要提交值时用 `get_codelist_terms`，更省
- `limit` 请求值超过 2000 会被静默钳制（靠 `limitRequested` + `hasMore` 察觉），
  不要假设一次调用能拿到任意大的表

## 测试状态

✅ 通过（单测 `tests/test_ct_submission_values.py` 31 项 + 上述真实 API 实测）
