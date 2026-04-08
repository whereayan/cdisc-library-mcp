# get_standard - 获取标准产品信息

## 工具描述

获取特定标准产品的详细信息，支持 sdtm、sdtmig、sendig、adam、cdash、cdashig 等标准。

## 使用方法

```typescript
mcp__cdisc-library__get_standard(standard: string, version: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtm`、`sdtmig`、`adam`、`cdash` 等
- `version` (必需): 版本号，如 `1-8`、`3-4` 等

## 示例调用

```typescript
// 获取 SDTM v1.8 的详情
mcp__cdisc-library__get_standard({
  standard: "sdtm",
  version: "1-8"
})
```

## 返回结果示例

```json
{
  "_links": {
    "classes": [
      {
        "href": "/mdr/sdtm/2-1/classes/GeneralObservations",
        "title": "General Observations",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/Interventions",
        "title": "Interventions",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/Events",
        "title": "Events",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/Findings",
        "title": "Findings",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/FindingsAbout",
        "title": "Findings About",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/SpecialPurpose",
        "title": "Special-Purpose",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/AssociatedPersons",
        "title": "Associated Persons",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/TrialDesign",
        "title": "Trial Design",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/StudyReference",
        "title": "Study Reference",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtm/2-1/classes/Relationship",
        "title": "Relationship",
        "type": "Class"
      }
    ],
    "parentProduct": {
      "href": "/mdr/sdtm/2-1",
      "title": "Study Data Tabulation Model Version 2.1",
      "type": "Foundational Model"
    },
    "priorVersion": {
      "href": "/mdr/sdtm/2-0/classes",
      "title": "Study Data Tabulation Model Version 2.0",
      "type": "SDTM Class List"
    },
    "self": {
      "href": "/mdr/sdtm/2-1/classes",
      "title": "Study Data Tabulation Model Version 2.1",
      "type": "SDTM Class List"
    }
  },
  "description": "This is the final Version 2.1 of the Study Data Tabulation Model Document (SDTM). This document includes additional variables related to the Tobacco Implementation Guide (TIG) v1.0, released concurrently.",
  "effectiveDate": "2024-06-07",
  "label": "Study Data Tabulation Model Version 2.1",
  "name": "SDTM v2.1",
  "registrationStatus": "Final",
  "source": "Prepared by the CDISC Submission Data Standards Team",
  "version": "2-1"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.classes` | 标准包含的类列表 |
| `_links.parentProduct` | 所属产品链接 |
| `_links.priorVersion` | 前一版本链接 |
| `description` | 标准描述 |
| `effectiveDate` | 生效日期 |
| `label` | 标签名称 |
| `name` | 标准名称 |
| `registrationStatus` | 注册状态（Final 等） |
| `source` | 来源说明 |
| `version` | 版本号 |

## 使用场景

- 获取特定标准的概览信息
- 了解标准包含哪些类
- 查看标准的生效日期和状态

## 测试状态

✅ 测试通过 - 返回 SDTM v2.1 标准详情，包含10个类