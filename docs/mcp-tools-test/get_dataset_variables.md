# get_dataset_variables - 获取数据集变量列表

## 工具描述

获取特定数据集中的所有变量列表。

## 使用方法

```typescript
mcp__cdisc-library__get_dataset_variables(standard: string, version: string, dataset: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtmig`
- `version` (必需): 版本号，如 `3-4`
- `dataset` (必需): 数据集名称，如 `DM`

## 示例调用

```typescript
// 获取 DM 数据集的变量列表
mcp__cdisc-library__get_dataset_variables({
  standard: "sdtmig",
  version: "3-4",
  dataset: "DM"
})
```

## 返回结果示例

```json
{
  "_links": {
    "datasetVariables": [
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/STUDYID",
        "title": "Study Identifier",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/DOMAIN",
        "title": "Domain Abbreviation",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/USUBJID",
        "title": "Unique Subject Identifier",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/SUBJID",
        "title": "Subject Identifier for the Study",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/RFSTDTC",
        "title": "Subject Reference Start Date/Time",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/RFENDTC",
        "title": "Subject Reference End Date/Time",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/AGE",
        "title": "Age",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/AGEU",
        "title": "Age Units",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/SEX",
        "title": "Sex",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/RACE",
        "title": "Race",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/ETHNIC",
        "title": "Ethnicity",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/ARMCD",
        "title": "Planned Arm Code",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/ARM",
        "title": "Description of Planned Arm",
        "type": "SDTM Dataset Variable"
      },
      {
        "href": "/mdr/sdtmig/3-4/datasets/DM/variables/COUNTRY",
        "title": "Country",
        "type": "SDTM Dataset Variable"
      }
      // ... 更多变量
    ],
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
      "href": "/mdr/sdtmig/3-3/datasets/DM/variables",
      "title": "Demographics",
      "type": "SDTMIG Dataset Variable List"
    },
    "self": {
      "href": "/mdr/sdtmig/3-4/datasets/DM/variables",
      "title": "Demographics",
      "type": "SDTMIG Dataset Variable List"
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
| `_links.datasetVariables` | 变量列表，每个变量包含 href、title、type |
| `_links.modelDataset` | 模型数据集 |
| `_links.parentClass` | 所属类 |
| `datasetStructure` | 数据集结构 |
| `description` | 描述 |
| `label` | 标签 |
| `name` | 数据集名称 |

## DM 数据集完整变量列表

| 变量 | 标题 |
|------|------|
| STUDYID | Study Identifier |
| DOMAIN | Domain Abbreviation |
| USUBJID | Unique Subject Identifier |
| SUBJID | Subject Identifier for the Study |
| RFSTDTC | Subject Reference Start Date/Time |
| RFENDTC | Subject Reference End Date/Time |
| RFXSTDTC | Date/Time of First Study Treatment |
| RFXENDTC | Date/Time of Last Study Treatment |
| RFCSTDTC | Date/Time of First Challenge Agent Admin |
| RFCENDTC | Date/Time of Last Challenge Agent Admin |
| RFICDTC | Date/Time of Informed Consent |
| RFPENDTC | Date/Time of End of Participation |
| DTHDTC | Date/Time of Death |
| DTHFL | Subject Death Flag |
| SITEID | Study Site Identifier |
| INVID | Investigator Identifier |
| INVNAM | Investigator Name |
| BRTHDTC | Date/Time of Birth |
| AGE | Age |
| AGEU | Age Units |
| SEX | Sex |
| RACE | Race |
| ETHNIC | Ethnicity |
| ARMCD | Planned Arm Code |
| ARM | Description of Planned Arm |
| ACTARMCD | Actual Arm Code |
| ACTARM | Description of Actual Arm |
| ARMNRS | Reason Arm and/or Actual Arm is Null |
| ACTARMUD | Description of Unplanned Actual Arm |
| COUNTRY | Country |
| DMDTC | Date/Time of Collection |
| DMDY | Study Day of Collection |

## 使用场景

- 查看数据集包含的所有变量
- 了解变量的名称和标题
- 在调用 `get_variable` 前获取可用的变量列表

## 测试状态

✅ 测试通过 - 返回 DM 数据集 32 个变量