# get_ct_packages - 获取控制术语包列表

## 工具描述

获取所有 CDISC 控制术语（Controlled Terminology）包列表。

## 使用方法

```typescript
mcp__cdisc-library__get_ct_packages()
```

**参数**：无

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
    // ... 其他链接
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
| `_links` | 相关资源链接 |
| `parentPackage` | 所属控制术语包 |
| `parentCodelist` | 所属编码列表 |
| `conceptId` | 术语概念 ID |
| `definition` | 术语定义 |
| `preferredTerm` | 首选术语名称 |
| `submissionValue` | 提交值 |
| `synonyms` | 同义词列表 |

## 使用场景

- 需要查找特定术语包时
- 需要了解最新的控制术语版本时
- 为其他术语相关工具调用提供 package 参数

## 测试状态

✅ 测试通过 - 返回控制术语包信息