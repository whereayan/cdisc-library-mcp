# get_variable - 获取变量详情

## 工具描述

获取特定变量的详细信息，包括数据类型、核心属性、角色等。

## 使用方法

```typescript
mcp__cdisc-library__get_variable(standard: string, version: string, dataset: string, variable: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtmig`
- `version` (必需): 版本号，如 `3-4`
- `dataset` (必需): 数据集名称，如 `DM`
- `variable` (必需): 变量名称，如 `USUBJID`

## 示例调用

```typescript
// 获取 USUBJID 变量的详情
mcp__cdisc-library__get_variable({
  standard: "sdtmig",
  version: "3-4",
  dataset: "DM",
  variable: "USUBJID"
})
```

## 返回结果示例

```json
{
  "_links": {
    "modelDatasetVariable": {
      "href": "/mdr/sdtm/2-0/datasets/DM/variables/USUBJID",
      "title": "Unique Subject Identifier",
      "type": "SDTM Dataset Variable"
    },
    "parentDataset": {
      "href": "/mdr/sdtmig/3-4/datasets/DM",
      "title": "Demographics",
      "type": "SDTM Dataset"
    },
    "parentProduct": {
      "href": "/mdr/sdtmig/3-4",
      "title": "Study Data Tabulation Model Implementation Guide: Human Clinical Trials",
      "type": "Implementation Guide"
    },
    "priorVersion": {
      "href": "/mdr/sdtmig/3-3/datasets/DM/variables/USUBJID",
      "title": "Unique Subject Identifier",
      "type": "SDTM Dataset Variable"
    },
    "rootItem": {
      "href": "/mdr/root/sdtmig/datasets/DM/variables/USUBJID",
      "title": "Version-agnostic anchor resource for SDTMIG variable DM.USUBJID",
      "type": "Root Data Element"
    },
    "self": {
      "href": "/mdr/sdtmig/3-4/datasets/DM/variables/USUBJID",
      "title": "Unique Subject Identifier",
      "type": "SDTM Dataset Variable"
    }
  },
  "core": "Req",
  "description": "Identifier used to uniquely identify a subject across all studies for all applications or submissions involving the product. This must be a unique value, and could be a compound identifier formed by concatenating STUDYID-SITEID-SUBJID.",
  "label": "Unique Subject Identifier",
  "name": "USUBJID",
  "ordinal": "3",
  "role": "Identifier",
  "simpleDatatype": "Char"
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links.modelDatasetVariable` | 模型变量链接 |
| `_links.parentDataset` | 所属数据集 |
| `_links.parentProduct` | 所属产品 |
| `_links.priorVersion` | 前一版本 |
| `_links.rootItem` | 版本无关锚点 |
| `core` | **核心属性**（Req/Exp/Perm） |
| `description` | 变量的详细描述 |
| `label` | 变量标签 |
| `name` | 变量名称 |
| `ordinal` | 排序位置 |
| `role` | **变量角色**（Identifier/Topic/Result等） |
| `simpleDatatype` | **简单数据类型**（Char/Num等） |

## 核心属性说明（Core）

| 值 | 说明 |
|----|------|
| Req | Required - 必须变量，数据集中必须包含 |
| Exp | Expected - 期望变量，强烈建议包含 |
| Perm | Permissible - 允许变量，可根据需要包含 |

## 变量角色说明（Role）

| 值 | 说明 |
|----|------|
| Identifier | 标识符变量，用于识别记录 |
| Topic | 主题变量，描述观察的内容 |
| Result | 结果变量，包含观察结果值 |
| Qualifier | 限定变量，提供补充信息 |
| Synonym Qualifier | 同义限定变量 |
| Timing | 时间变量 |

## USUBJID 变量关键信息

- **Core**: Req（必须变量）
- **Role**: Identifier（标识符角色）
- **DataType**: Char（字符型）
- **Description**: 用于在所有研究和提交中唯一识别受试者的标识符

## 使用场景

- 了解变量的数据类型和是否必须
- 确认变量的角色和用途
- 获取变量的详细定义和规范

## 测试状态

✅ 测试通过 - 返回 USUBJID 变量完整详情