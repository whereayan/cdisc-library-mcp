# get_dataset - 获取数据集详情

## 工具描述

获取特定数据集的详细信息，包括数据集结构、描述、变量列表等。

## 使用方法

```typescript
mcp__cdisc-library__get_dataset(standard: string, version: string, dataset: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtmig`
- `version` (必需): 版本号，如 `3-4`
- `dataset` (必需): 数据集名称，如 `DM`、`AE`

## 示例调用

```typescript
// 获取 Demographics (DM) 数据集详情
mcp__cdisc-library__get_dataset({
  standard: "sdtmig",
  version: "3-4",
  dataset: "DM"
})
```

## 返回结果示例

```json
{
  "_links": {
    "modelDataset": {
      "href": "/mdr/sdtm/2-0/datasets/DM",
      "title": "Demographics",
      "type": "SDTM Dataset"
    },
    "parentClass": {
      "href": "/mdr/sdtmig/3-4/classes/SpecialPurpose",
      "title": "Special-Purpose",
      "type": "Class"
    },
    "parentProduct": {
      "href": "/mdr/sdtmig/3-4",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "Implementation Guide"
    },
    "priorVersion": {
      "href": "/mdr/sdtmig/3-3/datasets/DM",
      "title": "Demographics",
      "type": "SDTM Dataset"
    },
    "self": {
      "href": "/mdr/sdtmig/3-4/datasets/DM",
      "title": "Demographics",
      "type": "SDTM Dataset"
    }
  },
  "datasetStructure": "One record per subject",
  "description": "A special-purpose domain that includes a set of essential standard variables that describe each subject in a clinical study. It is the parent domain for all other observations for human clinical subjects.",
  "label": "Demographics",
  "name": "DM",
  "ordinal": "12"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.modelDataset` | 模型数据集链接 |
| `_links.parentClass` | 所属类（DM 属于 SpecialPurpose 类） |
| `_links.parentProduct` | 所属产品 |
| `_links.priorVersion` | 前一版本 |
| `datasetStructure` | 数据集结构（如 "One record per subject"） |
| `description` | 数据集描述 |
| `label` | 标签 |
| `name` | 数据集名称 |
| `ordinal` | 排序号 |
| `datasetVariables` | 变量列表（详细调用会包含） |

## DM 数据集常用变量

DM 数据集包含以下核心变量：

| 变量名 | 描述 |
|--------|------|
| STUDYID | 研究标识符 |
| DOMAIN | 域缩写 |
| USUBJID | 受试者唯一标识符 |
| SUBJID | 受试者标识符 |
| SITEID | 研究中心标识符 |
| AGE | 年龄 |
| AGEU | 年龄单位 |
| SEX | 性别 |
| RACE | 种族 |
| ETHNIC | 民族 |
| ARMCD | 计划分组代码 |
| ARM | 计划分组描述 |
| COUNTRY | 国家 |

## 使用场景

- 了解数据集的结构和用途
- 获取数据集包含的变量列表
- 理解数据集的数据记录规则

## 测试状态

✅ 测试通过 - 返回 DM 数据集完整详情（结果较大，包含完整变量列表）