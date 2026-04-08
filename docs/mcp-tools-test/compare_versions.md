# compare_versions - 版本差异比较

## 工具描述

比较两个版本之间的差异，包括新增、删除、修改的内容。

## 使用方法

```typescript
mcp__cdisc-library__compare_versions(standard: string, version1: string, version2: string)
```

**参数**：
- `standard` (必需): 标准名称，如 `sdtm`
- `version1` (必需): 第一个版本，如 `1-7`
- `version2` (必需): 第二个版本，如 `1-8`

## 示例调用

```typescript
// 比较 SDTM v1.7 和 v1.8 的差异
mcp__cdisc-library__compare_versions({
  standard: "sdtm",
  version1: "1-7",
  version2: "1-8"
})
```

## 返回结果示例

```json
{
  "diff": [
    {
      "body": [
        {
          "Attribute": [{"text": "Generated"}],
          "Value": [{"text": "2026-04-08T08:40:11"}]
        },
        {
          "Attribute": [{"text": "Updated Version"}],
          "Value": [{"text": "SDTM v1.8"}]
        },
        {
          "Attribute": [{"text": "Previous Version"}],
          "Value": [{"text": "SDTM v1.7"}]
        }
      ],
      "head": ["Attribute", "Value"],
      "title": "Info"
    },
    {
      "body": [
        {
          "Column Name": [{"text": "Updated Version"}],
          "Description": [{"text": "Newer version of the standards being compared."}]
        },
        {
          "Column Name": [{"text": "Previous Version"}],
          "Description": [{"text": "Older version of the standards being compared."}]
        },
        {
          "Column Name": [{"text": "Action"}],
          "Description": [{"text": "Change to the standard; possible values are \"Add\", \"Drop\", \"Type Update\", and \"Value Update\"."}]
        }
        // ... 更多列说明
      ],
      "head": ["Column Name", "Description"],
      "title": "Column Definitions"
    },
    {
      "body": [
        // 具体的差异内容
      ],
      "head": ["Updated Version", "Previous Version", "Action", "Impact", "Description", "Reason"],
      "title": "Change Summary"
    }
  ]
}
```

## 返回字段说明

结果是一个 `diff` 数组，包含多个表格：

| 表格 | 说明 |
|------|------|
| Info | 比较的基本信息（生成时间、版本信息） |
| Column Definitions | 列定义说明 |
| Change Summary | 变化摘要，包含具体的差异内容 |

## Action 类型说明

| 值 | 说明 |
|----|------|
| Add | 新增内容 |
| Drop | 删除内容 |
| Type Update | 类型更新 |
| Value Update | 值更新 |

## Impact 说明

| 值 | 说明 |
|----|------|
| High | 高影响，可能需要修改现有数据 |
| Medium | 中等影响 |
| Low | 低影响，主要是文档或元数据变化 |

## 使用场景

- 了解标准升级带来的变化
- 评估版本迁移的影响
- 确定需要修改的数据结构

## 注意事项

- 结果数据量较大，可能返回 15MB+ 的内容
- 建议在需要详细比较时使用

## 测试状态

✅ 测试通过 - 成功比较 SDTM v1.7 和 v1.8，返回详细差异（结果存储在独立文件中，约 15MB）