# get_products - 获取所有 CDISC 产品列表

## 工具描述

获取所有 CDISC 产品列表，包括 SDTM、ADaM、CDASH 等标准。

## 使用方法

```typescript
mcp__cdisc-library__get_products()
```

**参数**：无

## 返回结果示例

```json
{
  "_links": {
    "data-analysis": {
      "_links": {
        "adam": [
          {
            "href": "/mdr/adam/adam-2-1",
            "title": "Analysis Data Model Version 2.1",
            "type": "Foundational Model"
          },
          {
            "href": "/mdr/adam/adam-adae-1-0",
            "title": "Analysis Data Model Data Structure for Adverse Event Analysis Version 1.0",
            "type": "Implementation Guide"
          },
          // ... 更多 ADaM 标准
        ]
      }
    },
    "data-collection": {
      "_links": {
        "cdash": [
          {
            "href": "/mdr/cdash/cdash-1-1",
            "title": "Clinical Data Acquisition Standards Harmonization Version 1.1",
            "type": "Foundational Model"
          }
          // ... 更多 CDASH 标准
        ]
      }
    },
    "data-tabulation": {
      "_links": {
        "sdtm": [
          {
            "href": "/mdr/sdtm/1-2",
            "title": "Study Data Tabulation Model Version 1.2",
            "type": "Foundational Model"
          },
          {
            "href": "/mdr/sdtm/1-3",
            "title": "Study Data Tabulation Model Version 1.3",
            "type": "Foundational Model"
          }
          // ... 更多 SDTM 标准
        ]
      }
    }
  }
}
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `_links` | 产品分类链接 |
| `data-analysis` | 数据分析相关标准（ADaM 系列） |
| `data-collection` | 数据采集相关标准（CDASH 系列） |
| `data-tabulation` | 数据制表相关标准（SDTM 系列） |
| `href` | 资源的 API 路径 |
| `title` | 资源标题 |
| `type` | 资源类型（Foundational Model / Implementation Guide） |

## 使用场景

- 需要了解 CDISC 有哪些可用标准时
- 要获取特定标准的版本列表时
- 作为其他工具调用的起点，确定可用的标准和版本

## 测试状态

✅ 测试通过 - 返回完整的 CDISC 产品列表