# AOCI 速查

被 `aoci-init` / `aoci-index` / `aoci-cognition` 三个技能共享。

## 二进制定位

```bash
AOCI=$(command -v aoci || ls -d ~/.local/share/aoci/*/aoci 2>/dev/null | sort -V | tail -1)
```

发布版二进制。两者皆空 → 问用户安装路径，不要自己猜。

## 命令清单

| 命令 | 用途 |
|---|---|
| `aoci init` | 写认知骨架、治理配置、AGENTS.md、宿主 MCP 配置 |
| `aoci scan` | 建立/重建 Baseline（`--dry-run` 预演；替换已有 Baseline 需 `--force`） |
| `aoci status` | 紧凑对齐状态（只读；`--deep` 算当前差异，哈全仓较慢） |
| `aoci verify` | 治理状态（只读） |
| `aoci check` | 聚合 pre-commit 检查：blocking 与非 blocking 分开报 |
| `aoci doctor` | 环境与 Agent 集成诊断（只读、离线） |
| `aoci index agent guide` | 当前阶段、阻塞项、清除阻塞的命令 |
| `aoci index score` | 九维索引质量分（`--dim <维度>` 看某维的违规清单） |
| `aoci index inventory` | 列出有文件但无 Entry 的对象 |
| `aoci index header show` | 打印索引 Header |
| `aoci capabilities` | 当前二进制的机器能力清单（版本化事实） |
| `aoci ui --detach` | 后台起本地只读面板，打印 URL |
| `aoci ui --stop` | 停掉面板 |
| `aoci config get/set` | 读写 `.aoci/config.json` |
| `aoci update-entry` / `aoci remove-entry` | 与 MCP 同管线的 CLI 写入 |
| `aoci scope` / `aoci source` / `aoci database` / `aoci cognition` | 范围策略、源身份、数据库证据、认知布局 |

全局 flag：`--repo <绝对路径>`（覆盖自动发现）、`--json`、`--quiet`。

## 仓库根解析

`--repo` > 从 cwd 向上找 `.git` > 再向上找 `.aoci`（源码 `internal/config/paths.go` 的 `FindRepoRoot`）。cwd 在子目录也命中仓库根；找不到则报 config 错误（退出码 3）。

## 退出码

- `verify`：0 = 治理完整；1 = 有未解漂移（ActionableMissing / PendingCuration / Orphan / Stale / Unbaselined）；2 = 索引格式非法；3 = 未初始化或配置错误。
- `check`：存在 blocking 项时非 0（blocking：ActionableMissing / PendingCurationMissing / Stale / Unbaselined / 字典违规 / 格式错误 / 待处理 Entry 或 Curation 草稿）。
- `init` / `scan`：0 = 成功。
- 其它命令：非 0 = 失败，读输出里的错误文本。

## MCP 九个工具

`aoci_rules`（会话运行合同）、`aoci_overview`、`aoci_get_entries`、`aoci_search`、`aoci_maintain`、`aoci_header`、`aoci_report`、`aoci_remove_entry`、`aoci_update_entry`。

## 宿主配置文件

| 宿主 | 位置 |
|---|---|
| omp / Claude Code / Qoder | 项目根 `.mcp.json`（Claude Desktop 格式） |
| Codex | 项目根 `.codex/config.toml` |
| Cursor | `.cursor/mcp.json`（init 只打印参考模板，不落盘） |
| OpenCode | 项目根 `opencode.json` |

内容统一是这一个 server 条目：

```json
{"mcpServers":{"aoci":{"command":"/abs/path/to/aoci","args":["--repo","/abs/path/to/repo","mcp"]}}}
```

## 一个进程一个仓库

`aoci mcp` 启动时定一次仓库根（`--repo` 或 cwd）。同一会话接多个仓库 = 每个仓库一个 server 条目，条目按仓库命名；认知不跨 server，每个仓库各自 `aoci_maintain` 收尾。

## 认知资产与 git

`aoci.txt`、`aoci.meta.txt`、`aoci.code.txt`、AGENTS.md 必须保持被 git 跟踪：被忽略的文件被 scan 静默跳过，索引建不起来。宿主配置（`.mcp.json` 等）含本机绝对路径，保持 init 写好的忽略项、不提交。
