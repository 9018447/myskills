---
name: how
description: "用于 \"how does X work\"、改动某处之前的代码走读，以及位置 / 归属 / 分层问题（\"where should this live\"、\"which package owns this\"、\"is this the right layer\"）。解释子系统架构、运行时流程与新手上手所需的心智模型。探究动机请用 why。"
---

# How

在 Codex 上，遵循本 skill 之前，先阅读[平台映射](../poteto-mode/references/codex-tools.md)，包括其中针对各 skill 的注意事项。

在 GitHub Copilot 上，遵循本 skill 之前，先阅读[平台映射](../poteto-mode/references/copilot-tools.md)，包括其中针对各 skill 的注意事项。

探索代码库来回答 "how does X work?" 这类问题。产出高级工程师初接手一个子系统时所需的架构级解释：足以建立起可用的心智模型，又不至于读起来像逐行注释的源码。

下文的每次 spawn 都会指明 `pstack-models.md` 中的一行角色配置，以及[模型](#模型)一节中的默认值。将 `model` 设为该行的值；若配置表或该行缺失，则用默认值。当值为 `auto` 或 `inherit-parent` 时，保持 `model` 不设置。如果 `Agent` 工具拒绝某个 slug，就改用默认值并说明这一点。如果它连默认值也拒绝，就根据其错误信息改用同一家族中最接近的有效 slug。

## 步骤 1. 评估复杂度

如果范围不明确，先说明你的理解再开始探索。用户可以随时纠正。

- **简单**（单个模块、一个小工具，或 "how does function X work" 这类窄问题）：不派 explorer。由一个 explainer 一轮完成探索和讲解。转到步骤 2b。
- **复杂**（横跨多个文件或服务的子系统、贯穿性的功能、完整的架构概览）：先并行 spawn 多个 explorer，再交给 explainer。转到步骤 2a。

拿不准时，走简单路径。

## 步骤 2a. 探索（仅限复杂问题）

把问题拆解成 2 到 4 个探索角度，每个角度对应子系统的一个独立切面。在单条消息里 spawn 全部 explorer：

- `subagent_type`: `general-purpose`
- `model`: `how explorer` 那一行，默认值见[模型](#模型)
- `readonly`: `true`

每个 explorer 都使用 `references/explorer-prompt.md` 中的 prompt，并填入它的探索角度。然后转到步骤 3。

## 步骤 2b. 直接讲解（简单问题）

spawn 一个 `Agent` subagent，一轮完成探索和讲解：

- `subagent_type`: `general-purpose`
- `model`: `how explainer` 那一行，默认值见[模型](#模型)
- `readonly`: `true`

基于 `references/explainer-prompt.md` 构建 prompt，但去掉 explorer 发现部分。转到步骤 4。

## 步骤 3. 综合（仅限复杂问题）

等所有 explorer 返回后，spawn 一个 `Agent` subagent，把它们的发现综合成一份解释：

- `subagent_type`: `general-purpose`
- `model`: `how explainer` 那一行，默认值见[模型](#模型)
- `readonly`: `true`

基于 `references/explainer-prompt.md` 构建 prompt，填入每个 explorer 的发现。

## 步骤 4. 呈现

把 explainer 的输出呈现给用户。为清晰或贴合对话语境做轻度编辑没问题，但不要大改重写。

## 输出格式

解释使用 `references/explainer-prompt.md` 中定义的小节，不适用的小节直接省略：概览、关键概念、工作原理、代码位置、陷阱。

## 模型

各角色的默认值，取自 `plugins/pstack/models.json`（要改就在那里改，然后重跑 `tools/generate.mjs`）。运行时，`pstack-models.md` 覆盖表中匹配的角色行会覆盖这里的每一项；`/setup-pstack` 会写入该覆盖表，并按运行时列出其路径。

- how explorer: `opus`
- how explainer: `opus`

## 推理力度

覆盖表中的角色值可以在模型后面附一个推理力度，如 `opus @xhigh`。Claude Code 上的级别：`low`、`medium`、`high`、`xhigh`、`max`。哪些级别可用取决于模型。不带 `@` 的值取覆盖表的 `default effort` 行（一个级别或 `session`）；若表中没有该行，则取 `session`。`session` 不设置任何力度，因此派发方式与平常相同。读取模型前先剥掉后缀：无论处于哪个级别，`inherit-parent` 或 `auto` 仍然省略 `model`，而模型名照常作为 `model` 传入。在 Claude Code 上，一个级别会把你本要使用的 `subagent_type` 换成对应的 effort agent：`pstack:poteto-agent` 变成 `subagent_type: "pstack:poteto-agent-<level>"`；`general-purpose` 或不设 `subagent_type` 则变成 `subagent_type: "pstack:effort-<level>"`。这些 effort agent 只设置 `effort`，所以你传入的模型仍然决定最终模型。在 Codex 上，把级别作为 `spawn_agent` 的 `reasoning_effort` 传入，其余指令保持不变。
