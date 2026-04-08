# get_codelists - 获取编码列表

## 工具描述

获取指定控制术语包中的所有编码列表（Codelists）。

## 使用方法

```typescript
mcp__cdisc-library__get_codelists(package: string)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`

## 示例调用

```typescript
// 获取 SDTM CT 包 57 中的所有编码列表
mcp__cdisc-library__get_codelists({ package: "sdtmct-2024-03-29" })
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
    }
    // ... 更多链接
  },
  "conceptId": "C174106",
  "definition": "10-Meter Walk/Run - Was the 10-meter walk/run performed?",
  "preferredTerm": "10-Meter Walk/Run - Was Walk/Run Performed",
  "submissionValue": "TENMW101",
  "synonyms": ["TENMW1-Was Walk/Run Performed"]
}
```

## 返回字段说明

返回包中包含的编码列表信息，包括：

| 字段 | 说明 |
|------|------|
| `_links.parentPackage` | 所属包信息 |
| `conceptId` | 概念 ID |
| `definition` | 编码列表定义 |
| `preferredTerm` | 首选术语 |
| `submissionValue` | 提交值 |

## 使用场景

- 需要了解某个包中有哪些可用的编码列表
- 在调用 `get_codelist` 前先获取可用的 codelist ID

## 测试状态

✅ 测试通过 - 返回包中的编码列表信息