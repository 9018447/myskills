---
name: aider-rs
description: 用 aider-rs（Claude Code 插件的 MCP 工具）快速派发单文件和零碎编码请求。一次 `aider_task` 调一轮 LLM、改文件、自动提交，回来后看工具返回的 diff 和 git stat 验收。不写正式 SPEC，要求快速完成。
tags: [user]
---

# aider-rs 快速派发（单文件 / 零碎编码）

aider-rs 是已安装的 Claude Code 插件，以 MCP 工具形式暴露在会话里，直接当无状态写文件工头用：一条 `aider_task` 派出去，它自己调 LLM、改文件、自动提交、退出；回来后看 diff 验收。目标是快——零碎编码请求不设确认门槛、不写正式 SPEC。

## 事实（已确认）

- **调用走 MCP 工具，不是 CLI/脚本**：`mcp__plugin_aider-rs_aider-rs__aider_task` 派发（参数 `task` 自然语言、`files` 目标文件数组、`reset_context` 布尔）；`aider_status` 看会话状态；`aider_undo` 回滚上一次改动。不再需要旧 aide-zh 的 `aider-env.sh`、`.env`、`aider-model-metadata.json`——那些是 headless aider 的脚手架，已闲置，见技能目录 `_legacy/`。
- **自动提交**：aider-rs 每轮成功编辑后就 auto-commit（工具返回 commit hash）。和旧 aider 的 `auto-commits: false` 相反——提交时机由它自己把握，编排者只负责验收，不再自己决定何时 commit。
- **上下文默认累积**：同一会话里多次 `aider_task` 默认共享累积上下文，直到某次传 `reset_context: true` 才清空。与旧 aider"每次调用都是新鲜上下文"相反。补丁型小任务用累积省来回成本；想要无状态就用 `reset_context: true`。
- **`files` 参数锁改动范围**：把目标文件放进 `files` 数组，aider-rs 只在这些文件里改。单文件范围由编排者通过只传目标文件控制。
- **验收看工具返回的 diff**：`aider_task` 直接在返回里给出 diff、commit hash 和 token 用量。不再写 `.agent-results/` 日志。
- **模型是网关的 `glm-5.3-flash[1m]`，配置在 `~/.config/aider-rs/`**（env 前缀 `AIDER_RS_`）。aider-rs 自己直连网关，没有旧 aider 的 litellm 不识别模型名问题，也不需要 model-metadata 补上限。
- **系统 prompt 会追加 `~/.config/aider-rs/AGENTS.md`**：文件非空时，其内容作为额外指令叠进每轮任务。曾实测带来超出请求的输出（要加一行注释却多写了一节 README）。验收时留意，发现无关改动按需回滚（`aider_undo`）或补修正任务。
- **SEARCH 块匹配失败会重试**：默认 `max_edit_retries` 为 1，改不到目标会再试一轮；两轮仍不对就停（见停止条件）。

## 硬约束（违反即任务错误）

- **只派发，不代写**。产出方式是 `aider_task` 改文件、你验收；发现自己在直接写目标文件的代码，就是走错了流程（除非 aider-rs 不可用，此时直接普通编码并告知用户）。
- **单文件范围**。一次派发只允许动一个生产文件（外加最多一个测试文件）。做法是在 `files` 里只传目标文件；`git show --stat HEAD` 看到其他生产文件被改就是越界，`aider_undo` 回滚重派。
- **task 描述必须自足**。`task` 字符串要写清目标文件路径、要做什么、期望值（用字面量）、不要做什么。不要假定 aider-rs 看过本对话之外的内容。
- **验证靠返回 diff 和 git stat**。派发后看两样：工具返回的 diff/commit；`git show --stat HEAD` 动了哪些文件。

## 快速流程

1. **判范围**：请求是否落在一个文件里？不是就停（见停止条件）。
2. **派发**：调用 `aider_task`，`task` 一段自足描述（做什么、改哪个文件、期望是什么、别动什么），`files` 传 `[<目标文件路径>]`。
3. **验收**：看返回的 diff 是否只动目标文件；`git show --stat HEAD` 确认没多改；期望值抽查一两个（跑一次性 REPL/CLI 检查）。发现问题就补一条修正 task 再派一次，或 `aider_undo` 回滚。

## 停止条件

- **任务要动多个生产文件**（跨文件重构、schema/协议迁移、改共享常量）：本技能不适用，告诉用户换方式（`/acpx` 派给实现 agent）。
- **两次派发后仍不对**：停下，把 diff 和 git stat 贴给用户，不要让它无限循环——它会开始改测试断言来"通过"。
- **aider-rs 不可用**（`aider_status` 报错、或任务超时无提交）：停下报告用户，不要自行换工具、不要反复重试。
- **SPEC 级需求**（需要用户确认行为和验收标准才敢动手的）：告诉用户这超出快速派发，先确认再派。

## 完成条件

- 目标文件的改动已落地（`git status` / `git show --stat HEAD` 可见，且只含目标文件；aider-rs 已自动提交）。
- 验收结果已向用户汇报：改了什么、怎么验证的。