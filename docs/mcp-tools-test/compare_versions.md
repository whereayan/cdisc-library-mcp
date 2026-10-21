# compare_versions - 版本差异比较

> 已按 0.1.6 更新：参数改名 old_version/new_version（原 version1/version2），
> 默认返回摘要视图，新增 section 下钻与 max_rows；version 支持 'latest'。

## 工具描述

比较同一标准两个版本之间的差异。

完整 diff 载荷可达数十 MB（实测 SDTMIG 3-3→3-4 约 29 MB），直接返回会撑爆
LLM 上下文并导致客户端超时，因此 0.1.6 起默认返回**摘要视图**：
差异分区索引（名称 + 行数）+ Info 分区内容；明细按分区下钻获取。

## 使用方法

```typescript
mcp__cdisc-library__compare_versions(
  standard: string,
  old_version: string,
  new_version: string,
  section?: string,
  max_rows?: number,
  raw?: boolean
)
```

**参数**：
- `standard` (必需): 标准名称（enum）: `sdtm, sdtmig, sendig, adam, adamig, cdash, cdashig`
- `old_version` (必需): 旧版本号，如 `3-3`（也支持 `3.3` / `latest`）
- `new_version` (必需): 新版本号，如 `3-4`；传反会自动交换并在 `note` 中说明
- `section` (可选): 只返回指定分区的明细行（名称来自摘要里的 `sections` 索引）
- `max_rows` (可选): section 明细最多返回行数，默认 200，超出标注 `truncated`
- `raw` (可选): true 返回未汇总的完整 diff 载荷（警告：可达数十 MB）

**URL 规则（0.1.6 修复）**：diff 路径与产品路径同构，
`/mdr/diff/{group}/{new-tail}/{old-tail}`；ADaMIG 为
`/mdr/diff/adam/adamig-1-3/adamig-1-2`（旧版拼的 `/mdr/diff/adamig/...` 实为 404）。
请求采用单次 45s 超时、不重试，避免撞 MCP 客户端的 60s 上限。

## 示例调用

```typescript
// 1) 摘要视图
mcp__cdisc-library__compare_versions({
  standard: "sdtmig", old_version: "3-3", new_version: "3-4"
})

// 2) 下钻某分区前 50 行
mcp__cdisc-library__compare_versions({
  standard: "sdtmig", old_version: "3-3", new_version: "3-4",
  section: "Domains", max_rows: 50
})
```

## 返回结果示例（摘要视图；取自 2026-10 真实响应）

```json
{
  "standard": "sdtmig",
  "old_version": "3-3",
  "new_version": "3-4",
  "info": [
    {"Attribute": "Generated", "Value": "2026-10-21T12:26:32"},
    {"Attribute": "Updated Version", "Value": "SDTMIG v3.4"},
    {"Attribute": "Previous Version", "Value": "SDTMIG v3.3"}
  ],
  "sections": [
    {"section": "Info", "rows": 3},
    {"section": "ReadMe for Basic Tab", "rows": 11},
    {"section": "ReadMe for Advanced Tab", "rows": 14},
    {"section": "Basic", "rows": 889},
    {"section": "Advanced", "rows": 13384},
    {"section": "Validation", "rows": 1}
  ],
  "hint": "此为摘要视图。传 section='<分区名>' 查看该分区明细（max_rows 控制行数，默认 200）；raw=true 返回未汇总的完整 diff（可达数十 MB，谨慎使用）"
}
```

section 明细模式下，每行由 `{"列名": [{"text": "..."}]}` 扁平化为 `{"列名": "..."}`，如：

```json
{"Column Name": "Updated Version", "Description": "Newer version of the standards being compared."}
```

## 测试状态

✅ 0.1.6 实测：sdtmig 3-3→3-4（完整载荷约 29 MB）首次拉取约 13s，
摘要/下钻均在客户端 60s 限制内返回（旧版直接超时）；
adamig diff URL、新旧版本自动交换、分区下钻与截断均有单元测试覆盖。
