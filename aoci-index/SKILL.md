---
name: aoci-index
description: 确认 AOCI MCP 已接入，为当前仓库建立完整 AOCI 索引，完成后给出 AOCI 面板链接。
disable-model-invocation: true
---

# 建立 AOCI 索引

前提：仓库已经 `aoci init` + `scan`（见 `aoci-init` 技能）。本技能建立认知索引本身，结束时给出本地只读面板链接。

## 步骤

### 1. 确认 MCP 已接入

三个信号，逐个看：

- 工具可调：直接调用 MCP 工具 `aoci_rules`。返回会话合同 → server 已加载。
- `aoci doctor`（只读）：`"$AOCI" --repo <root> doctor`，看 Agent 集成那一段。
- 运行中的 server：`aoci ui --discover` 会列出本用户运行中的 aoci mcp 进程。

**完成判据**：`aoci_rules` 返回了合同。三条都没有 → 停下，告诉用户先跑 `aoci-init`，并给出重启提示：重启 Agent 时工作目录要在仓库根，宿主才会发现项目级 MCP 配置。

### 2. 读当前 Plan 与 Guide

```bash
"$AOCI" --repo <root> index agent guide
```

返回当前阶段、阻塞项、清除阻塞的命令。`"$AOCI" --repo <root> capabilities` 给当前二进制的机器能力清单（版本化事实）。

**完成判据**：知道当前阶段与还缺什么。

### 3. 写认知

顺序由 `aoci_rules` 的会话合同与 Guide 决定：

- `aoci_overview` —— 取得本仓库的完整索引认知（需要重载时带 `refresh_reasons`）。
- `aoci_update_entry` —— 为受管理对象写/更新 Entry，每条绑定真实证据与源码摘要。
- `aoci_get_entries` / `aoci_search` —— 需要定位细节时读取。
- `aoci_maintain` —— 受管理对象进入最终稳定状态后，检查并收尾认知。

Entry 的语义来自模型读到的真实证据；路径、文件名、AST、依赖扫描都推不出语义。

**完成判据**（全部满足才算索引建立）：

- `aoci verify` 退出码 0：missing / stale / orphan / unbaselined 全为 0。
- `aoci index score` 无致命维度失败（format / coverage / freshness / quota / dict / token / agent_ready / escale / tagparse）。
- `aoci status` 显示索引条目数与 Baseline 对齐。

### 4. 面板链接

```bash
"$AOCI" --repo <root> ui --detach
```

输出形如 `http://127.0.0.1:<port>/#access_token=<hex>`：后台常驻、只读、只监听 loopback。

**完成判据**：回复里给出这个 URL，并附停止方式 `aoci ui --stop`。

### 5. 报告

索引条目数、覆盖的受管理对象数、`aoci index score` 九维摘要、`aoci verify` 退出码、面板 URL。

## 注意

- 认知写入只走 MCP 工具管线（`aoci_update_entry` / `aoci_maintain`）；CLI 的 `update-entry` / `remove-entry` 走同一条管线。
- 替换 Baseline 要 `--force`：先向用户确认。
- `verify` / `check` / `index score` / `index inventory` 是只读的：正式索引与 Baseline 不变；Ledger / Verify History 的追加属于审计写入。

## 共享速查

二进制定位、命令清单、退出码、MCP 工具清单：读 `aoci-init` 技能目录下的 `AOCI-QUICKREF.md`（omp: `skill://aoci-init/AOCI-QUICKREF.md`；其他宿主按本技能目录相对解析 `../aoci-init/AOCI-QUICKREF.md`）。
