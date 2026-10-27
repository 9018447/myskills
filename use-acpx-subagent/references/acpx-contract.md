# acpx 调用依据

核对基线：openclaw/acpx commit 40ecc17ec17cd8abf4eb311bbc13ba635657f798，源码 package.json 版本 0.19.6，核对日期 2026-10-21。版本来自源码，不代表本机已安装或完成 ACP 联调。

官方来源：

- https://github.com/openclaw/acpx/blob/40ecc17ec17cd8abf4eb311bbc13ba635657f798/docs/CLI.md
- https://github.com/openclaw/acpx/blob/40ecc17ec17cd8abf4eb311bbc13ba635657f798/docs/flows.md
- https://github.com/openclaw/acpx/blob/40ecc17ec17cd8abf4eb311bbc13ba635657f798/skills/acpx/SKILL.md
- https://github.com/openclaw/acpx/blob/40ecc17ec17cd8abf4eb311bbc13ba635657f798/examples/flows/two-turn.flow.ts
- https://github.com/openclaw/acpx/blob/40ecc17ec17cd8abf4eb311bbc13ba635657f798/src/flows/types.ts

## 命令

acpx [global-options] --cwd <worktree> <caller-agent> exec --file <prompt>
acpx [global-options] --cwd <worktree> --agent '<caller-command>' exec --file <prompt>
acpx [global-options] --cwd <worktree> flow run <file.ts> --input-file <input.json> --default-agent <caller-agent>
acpx [global-options] --cwd <worktree> --agent '<caller-command>' flow run <file.ts> --input-file <input.json>

不同时传 positional agent 和 --agent。不把 plugin subagent 名称当成 acpx 内置执行器。接收调用方配置的任意名称，不维护白名单。原始命令的平台支持以安装版本为准；当前官方文档将原始 --agent 限制在 Unix，Windows 可用调用方配置的命名入口。

exec 是临时单轮会话。prompt 使用持久会话，scope 由执行器命令、绝对 cwd 和可选名称决定。手工多轮先 sessions new/ensure，再固定 cwd 和 -s；内置多步流程由 flow 管会话，不用 shell 循环。--no-wait 入队成功不等于完成。

--format quiet 输出最终文本，本包要求直接 JSON；保留 stdout/stderr。--format json 输出 NDJSON ACP 事件，不能当结果对象解析。非零退出、解析失败、未完成均停止交付。

权限、超时通过调用方全局选项传入。不默认 approve-all，不修改全局配置，不把来源 tools 当隔离规则。执行器可能运行 ACP 之外的原生工具；权限标志与 cwd 不是完整 OS 沙箱。

## Flow

从 acpx/flows 导入需要的 defineFlow、acp、action、shell、compute、decision、decisionEdge、checkpoint。用 edges 声明阶段关系。模板从 manifest 构造固定图，节点不设 profile，由调用方 --default-agent 或全局 --agent 解析。

acp.cwd 可由 input 或 action 输出决定。非 isolated ACP 节点在命令、cwd 和 session handle 一致时复用会话。shell/action 运行确定性操作；函数 action 使用 context.runShell，检查 signal、exitCode 和 timedOut。

acpx 自行保存 ~/.acpx/flows/runs/；不在本技能清理范围。每次 flow run 是新运行，不虚构 resume 命令，不把只读回放说成恢复执行。

Flow API 属实验能力。升级时重新核对 API。运行器读取版本并检查 flow 帮助，只证明命令存在，不证明完整兼容。

## Flow 加载陷阱

写或改 `.ts` flow 时不用顶层 await：`.ts` 由 tsx/cjs require 路径加载，顶层 await 报 "Top-level await is currently not supported with the cjs output format"，flow 在派发秒级失败；`.mts` 才走 ESM 通道。文件级读取用 `readFileSync`（`node:fs` 直接接受 file URL），异步读取放进节点回调。依据为本机 acpx 0.15.1 实测（dist cli-BHAT_D3V.js `loadFlowRuntimeModule`）；基线 0.19.6 是否同路径未核对。

改 flow 前先 `acpx --version` 核对实际安装版本，文档基线版本（0.19.6）与本机安装可能差多个小版本且 API 不一致：0.15.1 的 action 上下文没有 `context.runShell`（0.19.6 才有），要在节点里跑命令用 `shell` 节点（`exec` 返回 command/args/cwd），或让 action 只做 `node:fs` 的文件读写。acp 节点的 `parse` 必须容错提取 JSON（取首个 `{` 到末个 `}` 的切片再 `JSON.parse`），执行器最终回复可能以进度文字开头。
