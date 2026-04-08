# get_codelist - 获取编码详情

## 工具描述

获取特定编码列表（Codelist）的详细信息。

## 使用方法

```typescript
mcp__cdisc-library__get_codelist(package: string, codelist: string)
```

**参数**：
- `package` (必需): 包名称，如 `sdtmct-2024-03-29`
- `codelist` (必需): 编码 ID，如 `C141657`

## 示例调用

```typescript
// 获取编码列表 C141657 的详情
mcp__cdisc-library__get_codelist({
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

| 字段 | 说明 |
|------|------|
| `_links.parentCodelist` | 父编码列表 |
| `_links.parentPackage` | 所属包 |
| `_links.priorVersion` | 前一版本 |
| `_links.rootItem` | 版本无关锚点 |
| `conceptId` | 概念 ID |
| `definition` | 定义 |
| `preferredTerm` | 首选术语 |
| `submissionValue` | 提交值（用于实际数据提交） |
| `synonyms` | 同义词列表 |

## 使用场景

- 查找特定编码的提交值
- 了解编码的定义和使用场景
- 获取编码的标准化术语

## 注意事项

- 编码 ID 必须在指定的包中存在，否则会返回 404 错误
- 例如：C667 在 sdtmct-2024-03-29 中不存在，测试时返回 "未找到资源"

## 测试状态

✅ 测试通过 - 成功获取 C141657 编码详情
❌ 测试失败 - C667 在该包中不存在（预期行为）