# Changelog

## 0.1.10

### Added

- **`get_codelist_submission_values` — 批量取术语提交值（21 -> 22 个工具）**。
  起因是一条对 Library API 的事实核查：codelist 的 `terms` 端点是唯一的批量术语
  清单来源，而它**不返回逐术语 `submissionValue`** —— `_links.terms[]` 只有
  `href`/`title`/`type`，`raw=true` 也不会多给一个字段（实测 LBTESTCD：瘦身
  265,689 字符、raw 457,921 字符，两处都没有提交值）。更糟的是该端点**顶部的**
  `submissionValue` 是 codelist 自己的变量名（`LBTESTCD`、`SEX`），与术语提交值
  同名字段，看上去就像批量接口已经给了值。
  当时能取到提交值的地方只有单术语详情，于是「拿全 260 个提交值」被认定必须
  260 次调用（实测 ~566ms/次 ≈ 150s，且第二批 30 条比第一批慢 2.4 倍 —— 服务端
  限流）或改下官方 Excel。**两种都不必**：包级载荷 `ct/packages/{package}` 内联了
  整包 1106 张表 / 40,126 个术语，每个术语都带 `submissionValue`，一次请求即全覆盖。
  本工具即把这条路径做成工具：读包载荷取提交值，读 codelist `terms` 端点取权威
  名单，只有包载荷缺失的条目才回退到单术语详情（并发 8，上限=本页条数），并在
  `valueSource` / `termsResolvedByDetailRequest` 里如实告知走了哪条路。
  实测（2026-10-23）：LBTESTCD 2397 术语冷启动 26.1s / 2 次 HTTP、命中包缓存 1.6s /
  1 次 HTTP，`submissionValue` 覆盖 2397/2397；`get_term` 单条链路保持不变。
  另加 `fields`（默认 `code,name,submissionValue`，可选 `definition`/`synonyms`，
  数组与逗号串两种写法都收、大小写敏感于拼写但会拒绝未知列并列出合法值）、`offset`/`limit`
  （默认 200，上限 2000）、`raw`；名单来自 `_links` 而非瘦身后的名字键，因此**同名
  术语各占一行**、顺序与 API 一致，`total` 是全量条数便于判断要不要继续翻页。

### Fixed

- **`get_ct_package` 不再原样推 13 MB 载荷（此前必然超时）**。该端点返回整包内联
  数据，实测 `sdtmct-2024-03-29` 为 **13,359,789 字符**，而响应瘦身只减到
  13,359,578（只剥链接壳，1106 张表的术语全都留着），任何 MCP 客户端的 60s
  请求预算都吃不下 —— 0.1.9 起该工具在实调中 100% 超时（`raw=false` 与 `raw=true`
  皆然），等于「包详情」这一级元数据完全不可用。现在默认返回**包元信息 + 分页
  codelist 索引**（含每张表的 `termCount`），实测 36,110 字符 / 缩小 370 倍、
  命中缓存 0.12s，`raw=true` 仍是原始整包逃生舱。数据一个没少：提交值仍从缓存的
  包载荷里读，只是不再从 stdio 硬推。
- **包级大载荷按单次封顶超时拉取**：13 MB 用默认 `timeout=30s` + `retries=3` 时，
  最坏 4 × 30s 加退避远超客户端预算（与 0.1.x 给 `compare_versions` 定
  `_DIFF_TIMEOUT=45` 的原因同类）。现包载荷走 `timeout=45s, retries=0`，最坏情况
  仍在 60s 内；失败不报错给调用方，而是让 `get_codelist_submission_values` 降级为
  逐术语详情（数据不丢，只是变慢，`valueSource` 显示 `term-detail`）。
- **工具描述里的假 Codelist ID 全部纠正**：`_CODELIST_PROP` 与三个 CT 工具的
  `description` 示例一直写 `C667(SEX)` / `codelist='C667'`，而 **C667 不存在**
  （SEX 实为 `C66731`，4 个术语），照抄文档的调用一律 404，且 404 文案只给 URL、
  不提示 ID 本身是错的。现已改为 `C66731`，并在参数说明里点名「ID 不能靠直觉拼」。
  由 `test_no_bogus_c667_sex_hint_left_in_docs` 守住不再回潮。

### Changed

- `get_codelist_terms` 的 `description` 现在写明自己的边界：不返回逐术语提交值、
  `raw=true` 也不返回、顶部 `submissionValue` 属于 codelist，并指向新工具与大表的
  字符数量级；`get_codelist` / `get_ct_package` 描述同步说明分工。

### Docs

- 纠正两篇工具测试文档里的**复制粘贴错误载荷**：`get_ct_package.md` 与
  `get_codelist_terms.md` 的「返回结果示例」贴的都是同一个单术语详情
  （`conceptId: C174106` + `submissionValue`），与那两个工具的真实返回无关 ——
  这正是「以为批量接口带提交值」误解的来源。现按实测重写：前者给出摘要形状与
  13 MB 的来龙去脉，后者用 A/B 两段对照说清 `terms` 端点与 `get_term` 各自返回什么，
  并补上大表无分页参数的 token 警告。
  新增 `get_codelist_submission_values.md`（含实测请求数/耗时/规模对照表）；
  README 工具表与索引同步（22 个工具）。

### Tests

- 端到端（真起 stdio 服务、`list_tools` + `call_tool` 实调）抓出两个单测因绕过
  schema 校验而看不到的问题，已一并修掉：**`fields` 声明成纯 array，于是文档里
  推荐的逗号串写法在 MCP 入参校验阶段就被拒**（`'name,submissionValue' is not
  type of 'array'`，请求根本到不了解析器），现 `anyOf: [array of enum, string]`
  两种写法都通；**`limit` 超过 2000 被静默钳制而调用方无从察觉**（LBTESTCD 2397 条
  请求 2400 只拿到 2000 条），响应新增 `limitRequested` 回显请求值，
  `get_ct_package` 同步，两处都写进工具描述与文档（2397 条需翻两页）。
- 新增 `tests/test_ct_submission_values.py` 31 条：`fields` 默认/数组/逗号串/规范化
  排序/去重/拒未知列/拒非标量；行构造优先 API 值、缺载荷回退链接 title、`synonyms`
  默认空表；包摘要不外发提交值、`termCount`、分页与上限钳制、指向替代工具；
  **整表零逐条请求**（`calls == []`）、包载荷缺项时只补差集（1 条而非整页）、包载荷
  不存在时全量降级、包下载抛错时降级仍保住提交值、翻页走完整名单、`fields` 选列、
  `raw` 给全字段并上报全部可用列、**同名术语各占一行**、`limit`/`offset`/ID 大小写
  与空白归一、坏 ID 仍抛 404、注册表 22 个工具与 schema、CT 描述不再含假 ID、
  分发层不被通用瘦身改写。既有两套计数断言（`test_server_wiring`、`test_adam_datastructures`）21->22 同步。全量 162 -> **193 passed**（其余文件 162 条一条未动，仅两处工具计数从 21 改 22）。

## 0.1.9

### Added

- **ADaM 数据结构工具组（15 -> 21 个工具）**：CDISC Library 把 ADaM/ADaMIG 的元数据
  挂在 `/mdr/adam/{product}/datastructures`，而本服务只实现了 `/datasets` 路径，
  结果是 **ADaM 侧全部元数据查询在 0.1.8 之前都不可用**。实测（2026-10-22，v1.3）：
  `get_dataset_variables(adamig, 1-3, ADSL)` / `get_dataset` / `get_datasets` /
  `get_variable(adamig, 1-3, ADSL, AGE)` 均为 404，同一工具换成 sdtmig/DM 则正常，
  说明不是凭据或网络问题而是路径未实现。现按 API 文档的六个端点逐一落地：
  `get_datastructures`、`get_datastructure`、`get_datastructure_variables`、
  `get_datastructure_variable`、`get_datastructure_varsets`、`get_datastructure_varset`
  （`client.py` 新增同名方法 + `tools/datastructure.py`）。
  另外一个发现：**`search` 不能用来穷举 ADaM 变量**——`search(query='ADSL',
  type='Analysis Variable')` 只返 31 条且 v1.0/1.1/1.2/1.3 混排，因为它按文本相关度
  匹配，而大多数 ADSL 变量的 label/description 并不包含“ADSL”字样；ADSL 实际有
  141 个（模式）变量。这种“返回了但残缺”比 404 危险，已在工具描述里写明分工。
- **变量名/结构名/变量集名的大小写安全还原**：API 路径区分大小写，而 ADaM 的模式变量
  故意混写（`SITEGRy`、`APHASEw`、`TRxxPGy`、`STRATwR`），直接 `upper()` 就 404。
  现在从对应清单解析准确末段（`_index_records` + 归一化比对），入参大小写/空格/
  连字符不敏感；变量集还同时接受 slug 与显示名（`Identifier` / `ADSL Identifier` /
  `subject demographics`），因为集名跟 slug 跨版本不稳定。无法匹配时列出可用名称与
  相近候选，**且不发出无效请求**。
- **`get_standard` 不再是取 ADaM 变量的唯一出路**：0.1.8 要回答“ADSL 有哪些变量”
  只能拉整本 ADaMIG（实测瘦身完成后仍 353,083 字符，含 3 个数据结构）再在外面自己解析；
  现在 `get_datastructure(standard='adamig', version='latest', datastructure='ADSL')`
  一次请求、15,169 字符拿到同样的 141 变量与 core/类型。

### Changed

- **ADaM 上调 dataset 工具改为本地报错并指名工具**：`get_datasets`/`get_dataset`/
  `get_dataset_variables`/`get_variable` 对 `adam`/`adamig` 不再转发一个必然 404 的
  请求，而是报错列出死 URL、说清“ADaM 元数据在 datastructures 下”并给出可直接
  执行的替代调用；四个工具的 `description` 同步限定适用标准。SDTM/SEND/CDASH
  路径行为不变（有用例守住）。
- **响应尺寸收敛（均有 `raw=true` 逃生舱）**：`get_datastructure` 默认紧凑表（
  171,782 -> 15,169 字符）；清单类工具把逐行重复的 href 换成一个 `hrefTemplate`
  （23,048 -> 13,264）并去掉 141 行都相同的 `type`；变量集详情反而保留全量
  `description`（单集小，9,949 -> 2,431 来的是去掉每变量重复的 `_links`）。
  空变量集不列入；计数同时给 `totalVariables` 与每集 `count`，并在 `note` 里说明
  `xx`/`w`/`y` 是模式占位而非实际列名。
- **prompt 模板与工具签名同步**：`explore_standard`/`find_variable`/`validate_dataset`
  原本只教 `get_classes`/`get_datasets`/`get_dataset_variables`，在 ADaM 上会直接
  带出无效调用；现补上 datastructure 工具签名与适用条件。

### Tests

- 新增 `tests/test_adam_datastructures.py` 35 条：URL 形状、六个方法的默认紧凑输出
  与 `raw` 透传、`latest` 解析、缓存命中不重复请求、大小写还原（`sitegry` ->
  `SITEGRy` 且不得出现 `SITEGRY`）、slug/显示名四拼法命中同集且只请一次、
  未知结构/变量/变量集名时列出可用项且不发出无效请求、ADaM 根模型空清单的
  404 文案（并守住不要出现 `🧭 📄` 双 emoji 堆叠）、四个 dataset 工具的守卫
  （`asked == []`）、sdtmig 仍走 `/datasets` 的回归、六个工具的注册与参数转发。
  `route()` 故意让未登记的 URL 直接失败，避免 mock 漏配时变成难读的断言失败。
- `tests/test_server_wiring.py`：工具数 15 -> 21（并改名），`standard` enum 出现次数
  7 -> 13。`tests/test_cache_key_collisions.py`：补入六类 `datastructures/*` 键形状
  （含混合大小写的 `SITEGRy` 与变量集 slug）。
- 全量 127 -> 162 passed。

### Known issues（本次未修，已实测存在）

- `search` 服务端每 query 只返首页 100 条，客户端 `offset` 只能在这 100 条内滑动：
  `offset>100` 返 0 条但 `hasMore` 仍为 `true`（误导继续翻页）；缓存 key 为
  `search/{query}`，不含 type，所以首页截断结果会被缓存 24h 再复用。
- `get_standard` 无按数据结构过滤的参数，对 ADaMIG 一次返整本（约 353 KB）。
  新增的工具已覆盖常见需求，但该工具本身仍是个 token 陷阱。

## 0.1.8

### Fixed

- **`scripts/release.py --upload` 会无限挂住**：上传步骤只传 `--repository-url <裸URL>`，
  twine 因此不按名字去读 `~/.pypirc` 的 `[pypi]` 段，转而要求交互式补用户名/密码；
  没有终端时（CI、agent harness、管道 shell）它等不到输入也不报错，表现成「发版很慢」。
  0.1.7 就因此连挂两次（一次手动中止、一次 300s 超时），最后绕过脚本手传才发上去。
  现在统一走 `upload_target()`：`~/.pypirc` 有同名段就用具名 `--repository <section>`
  （凭据由 twine 自己取，环境变量 `TWINE_*` 仍优先覆盖），否则退回 `--repository-url`；
  两条分支都带 `--non-interactive`，缺凭据立即报错而不是静默挂住。
  `docs/PUBLISH_GUIDE.md` 的手动上传段同步补了该注意事项。
- **`--write-version` 后第一次跑闸门必红**：写完 `version.py` 就直接 pytest，而
  `importlib.metadata` 读的是已安装 `.dist-info`（仍停在旧版），于是
  `test_reported_version_matches_distribution` 失败，要人工重装才能继续（发 0.1.7 时踩过）。
  现在 `--write-version` 之后紧跟 `refresh_editable_install()`：有 uv 用
  `uv pip install -e . --python <exe>`，否则退回 `pip install -e . --no-deps`，两者都没有则报出
  可执行提示后退出。另加一条前置漂移闸门——手工改 `version.py` 而没走 `--write-version` 时，
  也能在跑测试与联网检查之前就报「.dist-info 与目标版本不一致」。

### Tests

- `TestReleaseUploadTarget` 4 条：具名段优先、无段时回退 URL（含 testpypi 的 URL）、
  两条分支都不得漏 `--non-interactive`、源码里不得再出现裸 `upload --repository-url`。
  全量 118 -> 122 passed。
- `TestReleaseEditableRefresh` 5 条：uv 优先 / pip 兜底 / 两者皆无返回 None /
  `installed_dist_version` 读元数据而非源码 / `write_version` 后必须紧跟 refresh。
  全量 122 -> 127 passed。

> 注：以上两条只改发布工具链（`scripts/release.py` 随 sdist 分发），**不在** 0.1.7 产物里，
> 本节随 0.1.8 首次对外发布；包的功能行为与 0.1.7 相同。

## 0.1.7

发布通道回归修复：`uvx cdisc-library-mcp` 实测可用（握手、15 工具、prompts 均通过），
但 `resources/read` 从未工作过，且 `.env` 查找会被客户端项目目录里的无关文件抢占。

### Fixed

- **`resources/read` 全部失败**：`read_product_resource` 把注入的 pydantic `AnyUrl`
  与字符串字面量直接比较（`AnyUrl("cdisc://about") == "cdisc://about"` 为 False），
  因此任何 uri 都落到 `Unknown resource` 分支；即使绕过该比较，返回 `TextContent`
  也会被 v1 包装器的返回类型匹配拒绝（且 `TextContent` 缺必填 `type`，构造即
  ValidationError）。现按 `str(uri)` 比较，并返回 `Iterable[ReadResourceContents]`。
  旧版 102 个测试只断言了 `resources/list` 注册，读路径无用例，所以缺陷随 0.1.5/0.1.6
  两次发布存活；本次补齐 `TestResourceRead` 三条用例（含遍历 `list` 声明的每个 uri）。
- **无关 `.env` 遮蔽凭据文件**：stdio 启动时工作目录是 MCP 客户端的项目目录，
  旧逻辑「第一个存在的 `.env` 即命中并 break」，于是客户端项目里一个与本服务无关的
  `.env` 会挡住 `~/.cdisc-mcp/.env`，表现为服务无凭据启动。现在只把**自身声明了
  `CDISC_*` 变量**的文件当作命中，其余跳过且不导入其键值；不可读的文件跳过而非
  中断启动。新增 `tests/test_env_discovery.py`。

### Changed

- **`resources/read` 与工具同一响应形态**：资源载荷现在过 `slim()`（剥 `_links`、
  链接折叠为 `refs`）。资源不接受参数，没有 `raw` 逃生舱，所以只服务 agent 友好形态。
- **未知资源 uri 改为协议级 Invalid Params**：旧版抛裸 `ValueError`，客户端拿到
  `code=0` 的 JSON-RPC 错误；现在按 `McpError(-32602)` 上报并在文案里列出可用资源，
  与未知 prompt 的报告方式一致。
- **资源清单单一来源**：`RESOURCES`（uri -> 名称/描述/取数）同时驱动 `resources/list`
  与 `resources/read`，两者不可能再漂移。

### Docs

- README 明确 `uvx` 无需再加 `--with "mcp<2.0.0"`（上界已写进 `pyproject.toml`，
  uv 解析时自动遵守，实测解析到 mcp 1.30.0），并把示例配置的内联密钥改为推荐
  `~/.cdisc-mcp/.env`；补充 `.env` 查找顺序说明。

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
