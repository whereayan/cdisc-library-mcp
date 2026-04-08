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

## 示例调用

```typescript
// 获取编码列表 C141657 中的所有术语
mcp__cdisc-library__get_codelist_terms({
  package: "sdtmct-2024-03-29",
  codelist: "C141657"
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

返回编码列表中包含的术语列表，每个术语包含：

| 字段 | 说明 |
|------|------|
| `conceptId` | 术语概念 ID |
| `definition` | 术语定义 |
| `preferredTerm` | 首选术语名称 |
| `submissionValue` | 提交值 |
| `synonyms` | 同义词列表 |

## 使用场景

- 获取某个编码列表下所有可选的术语值
- 了解变量可以使用的所有标准化值
- 进行数据标准化时查找合适的提交值

## 注意事项

- 如果编码列表不存在，会返回 404 错误

## 测试状态

✅ 测试通过 - 返回 C141657 编码列表的术语信息