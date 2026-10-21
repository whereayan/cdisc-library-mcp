# Changelog

## 0.1.6

针对工具设计问题的集中修复：目标是让 LLM 调用方少试错、省 token、不撞客户端超时。
含三处**破坏性变更**（参数改名 / 默认响应形态），见 Changed。

### Fixed

- **ADaM 基础模型 URL 404**：旧版拼 `/mdr/adam/2-1`，真实 API 只认
  `/mdr/adam/adam-2-1`（实测验证）。`standard='adam'` 此前实际不可用。
  URL 构造统一为 `_product_path()`（group + tail 同构规则，diff 路径复用同一规则）。
- **compare_versions 对 adamig 拼错 URL**：旧版拼 `/mdr/diff/adamig/1-3/1-2`（实测 404），
  正确形态是 `/mdr/diff/adam/adamig-1-3/adamig-1-2`（实测 200）。
- **compare_versions 超时**：完整 diff 可达 29 MB（SDTMIG 3-3→3-4 实测），旧版
  30s×4 次的重试梯子最坏情况撞穿 MCP 客户端 60s 上限。现在单次 45s 超时、不重试。
- **prompt 与工具签名漂移**：模板里宣传过不存在的 `search(query, scope?)` 和
  `compare_versions(product, version, previous?)`，已全部改为真实签名。
- **工具描述里的 LBTESTCD 示例 C 码是错的**：`get_codelist` / `get_codelist_terms` /
  `get_term` 的 `codelist` 参数描述写的是 `C141657(LBTESTCD)`，而 C141657 实际是
  *10-Meter Walk/Run Functional Test Test Code*，LBTESTCD 应为 **C65047**（经 SDTM CT
  sdtmct-2026-09-25 实测）。调用方照描述取值会直接拿到一个无关 codelist，已改正并
  在描述里补了「不确定某变量的 codelist ID 时先用 `get_variable` 看 refs」的引导。

### Changed（破坏性）

- **响应默认瘦身**：所有工具剥除 `_links`/`links`/`@search.*` 噪声，链接块折叠为
  `refs`（标签→href）；每个工具新增 `raw`（boolean，默认 false）取原始载荷。
- **compare_versions 参数改名**：`version1/version2` → `old_version/new_version`；
  传反自动交换并在响应 note 说明；默认返回摘要视图（分区索引 + Info 扁平化），
  新增 `section`/`max_rows` 按分区下钻，明细行扁平化为 {列名: 文本}。
- **get_dataset / get_dataset_variables 职责分工**：前者只回数据集元数据，
  后者是变量清单首选；描述互相引用，不再让调用方二选一靠猜。

### Added

- **version='latest'**：所有带 version 的工具可自动从产品列表解析最新数字版本
  （如 sdtmig→3-4、adam→2-1、adamig→1-3；忽略 ap-1-0/md-1-1/adae-1-0 等兄弟 IG）。
- **standard 参数 enum 化**：schema 限定 7 个主流标准，把拼写错误拦在参数校验层。
- **search 增强**：结果客户端缓存 24h；新增 `type`（命中类型过滤，大小写不敏感）、
  `limit`/`offset`（客户端分页）；响应带 totalHits/returned 等元数据。
- **get_term 支持术语名**：term 参数接受 C 代码或术语名（大小写不敏感），
  名称未命中时报错附 difflib 相近候选；缓存按解析后的 C 代码存。
- **ToolAnnotations**：全部 15 个工具标注 `readOnlyHint=true`。
- 依赖下限提升到 `mcp>=1.6.0`（ToolAnnotations 引入版本），上限 `<2.0.0` 不变。

## 0.1.5

### Security

- **发布产物不再携带客户端配置**。0.1.4 的 sdist 误将本地客户端配置一并打包，
  其中含 API Key。本次处置：
  - 本地客户端配置从 git 跟踪中摘出并加入 `.gitignore`，改提供 `.example` 占位模板；
  - sdist 改为 **白名单**（`[tool.hatch.build.targets.sdist] only-include`），
    只有显式列出的路径能进发布产物；
  - 新增 `scripts/check_secrets.py`：扫描跟踪文件与 dist 产物，命中即非零退出，
    输出已脱敏（`31b1…9b（32 位）`），支持 `# allowlist secret` 行内豁免；
  - `scripts/release.py` 重写为闸门流水线，上传前强制跑
    版本一致性 / PyPI 版本未占用 / 跟踪文件密钥扫描 / pytest / 构建 / sdist 内容核对 /
    产物密钥扫描 / `twine check`；PyPI token 只接受环境变量，不再接受命令行参数
    （旧脚本 `release.py <版本> <TOKEN>` 会把凭据留在 shell history 和进程列表里）。
  - 历史提交中该配置仍可见；凭据的后续处置由维护者自行决定。
    **给使用者的提示**：本包的凭据一律通过环境变量或 `~/.cdisc-mcp/.env` 提供，
    不要把带真实 Key 的客户端配置放进仓库或发布产物。

### Fixed

- **缓存键碰撞导致工具返回错误数据**（`CacheManager._get_cache_file_path`）。
  旧实现只用 cache key 的前两段拼路径（`parts[0]/parts[1]`），于是同一前缀下所有更深的
  key 全部塌缩到同一个文件：

  | cache key | 0.1.4 落盘文件 | 后果 |
  |---|---|---|
  | `ct/packages`、`ct/packages/{pkg}`、`.../codelists`、`.../codelists/{id}`、`.../terms`、`.../terms/{id}` | 都是 `ct/packages.json` | 6 个 CT 工具互相返回对方的载荷 |
  | `standards/{std}/{ver}` 与 `standards/{std}/{ver}/classes` | 都是 `standards/{std}.json` | `get_standard` ↔ `get_classes` 串位 |
  | `datasets/{std}/{ver}[/{ds}[/variables[/{var}]]]` | 都是 `datasets/{std}.json` | 4 个数据集工具串位 |
  | `compare/{std}/{v1}/{v2}` | `compare/{std}.json`（版本号被丢弃） | 不同版本对的差异结果互相覆盖 |

  15 个工具中 14 个受影响（只有 `get_products` 安全）。`metadata.json` 按不同 key 记录
  "已缓存"，因此首个进程冷跑结果正确，之后复用缓存的读取会返回"最后一个写入该文件的
  工具"的载荷。`_delete_entry` 同样会删除共享文件，连带把兄弟条目的数据一起清掉。

  现在 key → 文件路径是双射：key 首段仍作为目录便于浏览，文件名带完整 key 的 SHA-1 短摘要，
  并对 Windows 非法字符（`|`、`:` 等，CDISC package id 中会出现）与长度上限做处理。

- **缓存索引版本化**。`metadata.json` 现为 `{"format": 2, "entries": {...}}`。
  遇到不认识/更旧的 `format` 时索引整体视为空，0.1.4 遗留在磁盘上的文件不可能再被误读为
  有效数据（文件本身保留，由使用者自行删除以回收磁盘空间）。

- **写入原子化**。缓存数据与索引改为临时文件 + `os.replace`，中途失败不会留下半个 JSON
  被后续请求读成损坏数据。

### Added

- `tests/test_cache_key_collisions.py`：把上述回归钉成测试——26 个真实 key 形态必须各自
  落一个文件、CT/datasets/standards/compare 家族的跨工具串位检查、删除一个条目不得影响兄弟
  条目、含 `|`/`:` 的 key 往返、超长 key 不越 Windows MAX_PATH、0.1.4 旧缓存必须按 miss 处理。
- 版本号收敛到单一来源 `src/cdisc_mcp/version.py`（此前 `pyproject.toml`、`__init__.py`、
  `server.py` 三处各写一份，容易漂移）。`pyproject.toml` 改用 hatchling 动态版本，MCP server
  上报的版本与包版本一致。

### 升级说明

- 无需改配置。原有的 `CDISC_CACHE_TTL=0` 之类的规避措施可以去掉，缓存加速即恢复正常。
- 如需回收 0.1.4 遗留缓存占用的磁盘空间，可安全删除缓存目录（默认为 `~/.cdisc-mcp/cache`，
  环境变量 `CDISC_CACHE_DIR` 可改）；其中 `compare/`、`standards/` 等单个文件可达数十 MB。

## 0.1.4

- 改进工具描述，支持 `uvx` 安装。
