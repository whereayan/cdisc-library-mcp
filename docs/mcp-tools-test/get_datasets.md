# get_datasets - 获取数据集列表

## 工具描述

获取特定标准和版本下的所有数据集列表。

## 使用方法

```typescript
mcp__cdisc-library__get_datasets(standard: string, version: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtmig`
- `version` (必需): 版本号，如 `3-4`

## 示例调用

```typescript
// 获取 SDTMIG v3.4 的数据集列表
mcp__cdisc-library__get_datasets({
  standard: "sdtmig",
  version: "3-4"
})
```

## 返回结果示例

```json
{
  "_links": {
    "datasetVariables": [
      {
        "href": "/mdr/sdtmig/3-4/datasets/AE/variables/STUDYID",
        "title": "Study Identifier",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/AE/variables/DOMAIN",
        "title": "Domain Abbreviation",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/AE/variables/USUBJID",
        "title": "Unique Subject Identifier",
        "type": "SDTM Dataset Variable"
      }
      // ... 更多变量链接
    ],
    "parentClass": {
      "href": "/mdr/sdtmig/3-4/classes/Events",
      "title": "Events",
      "type": "Class"
    },
    "parentProduct": {
      "href": "/mdr/sdtmig/3-4",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "Implementation Guide"
    },
    "priorVersion": {
      "href": "/mdr/sdtmig/3-3/datasets/AE/variables",
      "title": "Adverse Events",
      "type": "SDTMIG Dataset Variable List"
    },
    "self": {
      "href": "/mdr/sdtmig/3-4/datasets/AE/variables",
      "title": "Adverse Events",
      "type": "SDTMIG Dataset Variable List"
    }
  },
  "datasetStructure": "One record per adverse event per subject",
  "description": "An events domain that contains data describing untoward medical occurrences in a patient or subjects that are administered a pharmaceutical product and which may not necessarily have a causal relationship with the treatment.",
  "label": "Adverse Events",
  "name": "AE",
  "ordinal": "1"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.datasetVariables` | 数据集变量列表链接 |
| `_links.parentClass` | 所属类 |
| `_links.parentProduct` | 所属产品 |
| `_links.priorVersion` | 前一版本 |
| `datasetStructure` | 数据集结构说明 |
| `description` | 数据集描述 |
| `label` | 标签 |
| `name` | 数据集名称（如 AE） |
| `ordinal` | 排序号 |

## 使用场景

- 获取特定标准版本下可用的数据集
- 了解数据集的基本结构
- 在调用 `get_dataset` 前先获取可用的数据集名称

## 测试状态

✅ 测试通过 - 返回 AE 数据集详情，包含大量变量链接