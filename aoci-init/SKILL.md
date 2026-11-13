---
name: aoci-init
description: 初始化 AOCI——init 接入宿主 MCP、scan 建立 Baseline，并给出重启提示（不含建立索引）。
disable-model-invocation: true
---

# AOCI 初始化

在一个仓库里落地 AOCI：`init` 写好认知骨架与宿主 MCP 配置，`scan` 建立 Baseline，然后让用户重启 Agent 让 MCP 生效。索引本身不在这一步建立。

## 输入

- 仓库根：默认当前 git 仓库（`git rev-parse --show-toplevel`）；用户给了路径就用它。
- locale：`zh-CN` 或 `en-US`（新项目默认 en-US）。用户没说就按仓库既有语言选，问一次。
- 宿主：按 §宿主映射 判定。
- 二进制：`AOCI=$(command -v aoci || ls -d ~/.local/share/aoci/*/aoci 2>/dev/null | sort -V | tail -1)`；两者皆空就停下问用户安装路径。

## 步骤

### 1. init

```bash
"$AOCI" --repo <root> init --locale <locale> --agent <host>
```

读输出里的 Scope Proposal（受管理对象数、observe/exclude 计数、预计 token 预算）与待写 Entry 的对象数。

**完成判据**：退出码 0，且 `<root>/.aoci/config.json`、`<root>/.aoci/.gitignore`、`aoci.txt`、`aoci.meta.txt`、`aoci.code.txt` 存在，AGENTS.md 含 AOCI 受管区块。

### 2. 宿主配置落点

init 对不同宿主的写入方式不同，按 §宿主映射 逐个核对文件是否真的落盘：

- 已写入 → 回复里点名文件与条目。
- Cursor：init 只打印参考模板 → 把 §宿主映射 的 JSON 块交给用户，让他贴进 `<root>/.cursor/mcp.json`。

**完成判据**：每个宿主都有明确结论——“已写入 <文件>”或“需要你手动粘贴 <块>”。

### 3. 认知资产保持被 git 跟踪

```bash
cd <root> && git check-ignore aoci.txt aoci.meta.txt aoci.code.txt AGENTS.md
```

- 无输出 → 已就绪。
- 有输出 → 从 `.gitignore` / `.git/info/exclude` 移除这几项。理由：被忽略的文件会被 scan 静默跳过，索引建不起来。init 自己写的宿主配置忽略项（`.mcp.json` 等，含本机绝对路径）保持原样。

**完成判据**：上面命令无输出。

### 4. scan

```bash
"$AOCI" --repo <root> scan
```

已有 Baseline 时替换要加 `--force`——先向用户确认。

**完成判据**：退出码 0，`<root>/.aoci/baseline.json` 存在，输出给出纳入文件数与待写 Entry 数。

### 5. 报告与重启提示

报告内容：仓库根、locale、宿主配置落点、Baseline 文件数、待写 Entry 数、`aoci status` 的治理态（此时通常是 `authoring_required`，missing = 待写条目数），并写明索引尚未建立。

重启提示：Agent 重启后 MCP 才生效；重启时把工作目录切到 `<root>`，宿主才会发现项目级 MCP 配置。

**完成判据**：用户拿到完整报告与重启提示。

## 宿主映射

| 宿主 | `--agent` | init 写入 | 手写配置 |
|---|---|---|---|
| omp / Claude Code / Qoder | `claude` | `<root>/.mcp.json` | — |
| Codex | `codex` | `<root>/.codex/config.toml` | — |
| Cursor | `cursor` | 只打印参考模板 | `.cursor/mcp.json` |
| OpenCode | `opencode` | `<root>/opencode.json` | — |

需要手贴时用这个块（把两处绝对路径换成本机真实值）：

```json
{"mcpServers":{"aoci":{"command":"/abs/path/to/aoci","args":["--repo","/abs/path/to/repo","mcp"]}}}
```

## 注意

- 一个 MCP 进程只服务一个仓库：每个仓库各自 init、各自的 `.mcp.json`；同一会话要接多个仓库时，按仓库命名各自的 server 条目。
- 宿主配置含本机绝对路径，是机器绑定的：保持 init 写好的忽略项，不提交。
- 用发布版二进制（校验过签名的 tar 包），不是源码构建产物。

## 共享速查

二进制定位、命令清单、退出码、MCP 工具清单、宿主配置文件形状：读 `aoci-init` 技能目录下的 `AOCI-QUICKREF.md`（omp: `skill://aoci-init/AOCI-QUICKREF.md`；其他宿主按本技能目录相对解析 `../aoci-init/AOCI-QUICKREF.md`）。
