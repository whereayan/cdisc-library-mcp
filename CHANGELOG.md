# Changelog

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
