# get_classes - 获取标准的类列表

## 工具描述

获取特定标准和版本下的所有类（Classes）列表。

## 使用方法

```typescript
mcp__cdisc-library__get_classes(standard: string, version: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtmig`
- `version` (必需): 版本号，如 `3-4`

## 示例调用

```typescript
// 获取 SDTMIG v3.4 的类列表
mcp__cdisc-library__get_classes({
  standard: "sdtmig",
  version: "3-4"
})
```

## 返回结果示例

```json
{
  "_links": {
    "classes": [
      {
        "href": "/mdr/sdtmig/3-4/classes/GeneralObservations",
        "title": "General Observations",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/Interventions",
        "title": "Interventions",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/Events",
        "title": "Events",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/Findings",
        "title": "Findings",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/FindingsAbout",
        "title": "Findings About",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/SpecialPurpose",
        "title": "Special-Purpose",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/TrialDesign",
        "title": "Trial Design",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/StudyReference",
        "title": "Study Reference",
        "type": "Class"
      },
      {
        "href": "/mdr/sdtmig/3-4/classes/Relationship",
        "title": "Relationship",
        "type": "Class"
      }
    ],
    "parentProduct": {
      "href": "/mdr/sdtmig/3-4",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "Implementation Guide"
    },
    "priorVersion": {
      "href": "/mdr/sdtmig/3-3/classes",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "SDTMIG Class List"
    },
    "self": {
      "href": "/mdr/sdtmig/3-4/classes",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "SDTMIG Class List"
    }
  },
  "description": "This is the implementation guide for human clinical trials corresponding to Version 2.0 of the CDISC Study Data Tabulation Model.",
  "effectiveDate": "2021-11-29",
  "label": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
  "name": "SDTMIG v3.4",
  "registrationStatus": "Final",
  "source": "Prepared by the CDISC Submission Data Standards Team",
  "version": "3-4"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.classes` | 类列表，包含 GeneralObservations、Interventions、Events、Findings 等 |
| `_links.parentProduct` | 所属产品 |
| `_links.priorVersion` | 前一版本 |
| `description` | 描述 |
| `effectiveDate` | 生效日期 |
| `label` | 标签 |
| `name` | 名称 |
| `registrationStatus` | 注册状态 |
| `source` | 来源 |
| `version` | 版本 |

## SDTMIG 主要类说明

| 类名 | 说明 |
|------|------|
| GeneralObservations | 一般观察类 |
| Interventions | 干预类 |
| Events | 事件类 |
| Findings | 发现类 |
| FindingsAbout | 关于发现类 |
| SpecialPurpose | 特殊目的类 |
| TrialDesign | 试验设计类 |
| StudyReference | 研究参考类 |
| Relationship | 关系类 |

## 使用场景

- 了解标准的数据组织结构
- 获取特定类下的数据集列表
- 理解 SDTM 数据模型的分类体系

## 测试状态

✅ 测试通过 - 返回 SDTMIG v3.4 的 9 个类