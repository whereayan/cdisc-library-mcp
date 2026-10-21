# search - 全局搜索 CDISC Library

> 已按 0.1.6 更新：新增 type/limit/offset 参数与客户端缓存；响应默认瘦身。

## 工具描述

全局搜索 CDISC Library，可以搜索标准、数据集、变量、术语等。
命中按相关度排序；同一查询的结果在客户端缓存 24h（分页/过滤不重复请求）。

## 使用方法

```typescript
mcp__cdisc-library__search(query: string, type?: string, limit?: number, offset?: number, raw?: boolean)
```

**参数**：
- `query` (必需): 搜索关键词
- `type` (可选): 按命中类型过滤（不区分大小写），如 `Analysis Variable`、`Dataset`
- `limit` (可选): 最多返回的命中条数（客户端截断）
- `offset` (可选): 跳过的命中条数，与 limit 配合分页，默认 0
- `raw` (可选): true 返回未瘦身原始载荷，默认 false

说明：API 单次查询最多返回 100 条命中（`totalHits` 给出总数、`hasMore` 标注是否截断），
type/limit/offset 均在这 100 条内做客户端过滤与分页。

## 示例调用

```typescript
// 搜索 ADaM 分析变量 AVAL，只取前 10 条
mcp__cdisc-library__search({ query: "AVAL", type: "Analysis Variable", limit: 10 })

// 第二页
mcp__cdisc-library__search({ query: "AVAL", limit: 10, offset: 10 })
```

## 返回结果示例（默认瘦身视图；取自 2026-10 真实响应，长文本有截断）

```json
{
  "query": "AVAL",
  "totalHits": 237,
  "hasMore": true,
  "returned": 1,
  "typeFilter": "Analysis Variable",
  "matchedInPage": 100,
  "limit": 1,
  "hits": [
    {
      "core": "Required",
      "dataStructure": "BDS for TTE",
      "description": "AVAL is the elapsed time to the event of interest from the origin. ...",
      "href": "/mdr/adam/adam-tte-1-0/datastructures/ADTTE/variables/AVAL",
      "label": "Analysis Value",
      "name": "AVAL",
      "parentHref": "/mdr/adam/adam-tte-1-0",
      "parentName": "ADaM Basic Data Structure for Time-to-Event Analyses Version 1.0",
      "parentType": "Implementation Guide",
      "product": "ADaM BDS for TTE v1.0",
      "simpleDatatype": "Num",
      "type": "Analysis Variable",
      "variableSet": "Analysis Parameter Variables",
      "refs": {
        "parentDatastructure": "/mdr/adam/adam-tte-1-0/datastructures/ADTTE",
        "parentProduct": "/mdr/adam/adam-tte-1-0"
      }
    }
  ]
}
```

与旧版（0.1.5 及以前）的差异：
- `@search.score` / `@search.highlights` 默认被剥除（`raw=true` 可见）；
- `links` 折叠为 `refs`；
- 新增 `query` / `returned` 等元数据字段，过滤分页在客户端完成。

## 测试状态

✅ 0.1.4 实测通过（原始载荷）；0.1.6 起默认返回瘦身视图，行为由单元测试覆盖。
