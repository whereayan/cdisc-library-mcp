# get_ct_package - 获取控制术语包详情

## 工具描述

获取特定控制术语包的详细信息。

## 使用方法

```typescript
mcp__cdisc-library__get_ct_package(package: string)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`

## 示例调用

```typescript
// 获取 SDTM 控制术语包 57 的详情
mcp__cdisc-library__get_ct_package({ package: "sdtmct-2024-03-29" })
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
| `_links.parentPackage` | 所属包信息 |
| `_links.priorVersion` | 前一版本链接 |
| `_links.rootItem` | 版本无关的锚点资源 |
| `conceptId` | 概念 ID |
| `definition` | 定义 |
| `preferredTerm` | 首选术语 |
| `submissionValue` | 提交值 |
| `synonyms` | 同义词 |

## 使用场景

- 需要获取特定版本控制术语包的详细信息
- 需要了解包中包含哪些编码列表时

## 测试状态

✅ 测试通过 - 返回指定控制术语包详情