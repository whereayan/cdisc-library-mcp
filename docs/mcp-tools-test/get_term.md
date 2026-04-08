# get_term - 获取术语详情

## 工具描述

获取特定术语的详细信息。

## 使用方法

```typescript
mcp__cdisc-library__get_term(package: string, codelist: string, term: string)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`
- `codelist` (必需): 编码 ID，如 `C141657`
- `term` (必需): 术语 ID，如 `C174106`

## 示例调用

```typescript
// 获取术语 C174106 的详情
mcp__cdisc-library__get_term({
  package: "sdtmct-2024-03-29",
  codelist: "C141657",
  term: "C174106"
})
```

## 返回结果示例

```json
{
  "_links": {
    "parentCodelist": {
      "href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C141657",
      "title": "CDISC Functional Test 10-Meter Walk/Run Test Code Terminology",
      "type": "Code List"
    },
    "parentPackage": {
      "href": "/mdr/ct/packages/sdtmct-2024-03-29",
      "title": "SDTM Controlled Terminology Package 57 Effective 2024-03-29",
      "type": "Terminology"
    },
    "priorVersion": {
      "href": "/mdr/ct/packages/sdtmct-2023-12-15/codelists/C141657/terms/C174106",
      "title": "10-Meter Walk/Run - Was Walk/Run Performed",
      "type": "Code List Value"
    },
    "rootItem": {
      "href": "/mdr/root/ct/sdtmct/codelists/C141657/terms/C174106",
      "title": "Version-agnostic anchor resource for codelist term C141657.C174106",
      "type": "Root Value"
    },
    "self": {
      "href": "/mdr/ct/packages/sdtmct-2024-03-29/codelists/C141657/terms/C174106",
      "title": "10-Meter Walk/Run - Was Walk/Run Performed",
      "type": "Code List Value"
    }
  },
  "conceptId": "C174106",
  "definition": "10-Meter Walk/Run - Was the 10-meter walk/run performed?",
  "preferredTerm": "10-Meter Walk/Run - Was Walk/Run Performed",
  "submissionValue": "TENMW101",
  "synonyms": ["TENMW1-Was Walk/Run Performed"]
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.parentCodelist` | 父编码列表信息 |
| `_links.parentPackage` | 所属包信息 |
| `_links.priorVersion` | 前一版本链接 |
| `_links.rootItem` | 版本无关的锚点资源（用于跨版本引用） |
| `_links.self` | 当前资源链接 |
| `conceptId` | 术语的概念 ID（唯一标识） |
| `definition` | 术语的详细定义 |
| `preferredTerm` | 首选术语名称 |
| `submissionValue` | **提交值**（这是实际在数据中使用的值） |
| `synonyms` | 同义词列表 |

## 使用场景

- 查找特定术语的提交值用于数据填充
- 了解术语的完整定义和含义
- 确认术语的使用是否正确

## 关键信息

- `submissionValue`: "TENMW101" - 这是实际数据提交时使用的值
- `conceptId`: "C174106" - 这是术语的唯一标识符

## 测试状态

✅ 测试通过 - 成功获取术语 C174106 详情