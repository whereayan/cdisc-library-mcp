# search - 全局搜索 CDISC Library

## 工具描述

全局搜索 CDISC Library，可以搜索标准、数据集、变量、术语等。

## 使用方法

```typescript
mcp__cdisc-library__search(query: string)
```

**参数**：
- `query` (必需): 搜索关键词

## 示例调用

```typescript
// 搜索 SDTM 相关内容
mcp__cdisc-library__search({ query: "sdtm" })
```

## 返回结果示例

```json
{
  "hasMore": true,
  "hits": [
    {
      "@search.highlights": {
        "definition": [
          "Version 1.6 of the CDISC Study Data Tabulation Model (<em>SDTM</em>)."
        ]
      },
      "@search.score": 27.294525,
      "codelist": "SDTM Version Response",
      "conceptId": "C161430",
      "definition": "Version 1.6 of the CDISC Study Data Tabulation Model (SDTM).",
      "href": "/mdr/ct/packages/sdtmct-2022-12-16/codelists/C160923/terms/C161430",
      "label": "CDISC SDTM Model Version 1.6",
      "links": [
        {
          "href": "/mdr/ct/packages/sdtmct-2022-12-16/codelists/C160923",
          "linkName": "parentCodelist",
          "title": "CDISC SDTM Model Version ResponseTerminology",
          "type": "Code List"
        }
        // ... 更多链接
      ],
      "name": "CDISC SDTM Model Version 1.6",
      "parentHref": "/mdr/ct/packages/sdtmct-2022-12-16/codelists/C160923"
    }
    // ... 更多搜索结果
  ]
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `hasMore` | 是否还有更多结果 |
| `hits` | 搜索结果数组 |
| `@search.score` | 搜索匹配分数 |
| `@search.highlights` | 高亮显示匹配部分 |
| `conceptId` | 概念 ID |
| `definition` | 定义描述 |
| `href` | 资源路径 |
| `label` | 标签名称 |
| `name` | 名称 |
| `links` | 相关链接列表 |

## 使用场景

- 快速查找特定标准、数据集或术语
- 不确定具体资源路径时进行探索性搜索
- 获取某个主题相关的所有资源

## 测试状态

✅ 测试通过 - 搜索 "sdtm" 返回大量相关结果