---
name: why
description: "用于“X 为什么是这样实现的”“我们为什么选了 Y”、设计缘由、回归、事后复盘，或有数据支撑的阈值等问题。会先发现可用的 MCP，并并行查询每个证据类别（版本控制、issue 跟踪器、长文档、实时聊天、基础设施可观测性、错误跟踪、产品分析数仓），然后返回一份带引用的判断，说明其中的决策与取舍。运行时行为请用 how。"
---

# Why

在 Codex 上，先阅读[平台映射](../poteto-mode/references/codex-tools.md)（包括其中针对各 skill 的备注），再遵循本 skill。

在 GitHub Copilot 上，先阅读[平台映射](../poteto-mode/references/copilot-tools.md)（包括其中针对各 skill 的备注），再遵循本 skill。

调查代码背后的动机与意图。

与 `how` skill 配套。`how` 回答代码做什么、如何运作；`why` 回答是哪些力量造就了它如今的形态。

下文的每次 spawn 都指明了 `pstack-models.md` 中的一个角色行，以及[模型](#模型)一节中的默认值。将 `model` 设为该行的值；如果清单或该行缺失，则设为默认值。当值为 `auto` 或 `inherit-parent` 时，不要设置 `model`。如果 `Agent` 工具拒绝某个 slug，就改用默认值并说明这一点。如果它连默认值也拒绝，就从其错误信息中选用同一家族中最接近的有效 slug。

## 工作姿态

以一名**细致、审慎、精确的调查员**的方式工作。对自己知道什么、什么只是推断，要诚实。阅读 `references/epistemics.md` 获取完整的置信度框架与措辞指南。综合者必须遵循它。

## 第 1 步：理解目标与问题

解析用户在问什么。**目标**通常是一段代码、一种模式、一个功能，或某个指名道姓的设计决策。**问题**通常是设计缘由、一次权衡取舍、一个促成决定的边界情况、一项外部约束、死代码，或一次宽泛的历史梳理。

如果目标模糊（比如“我们为什么这样做？”却没有明确的指涉对象），就从对话上下文中做出最佳猜测（打开的文件、最近的编辑、光标位置、刚刚讨论过的内容）。简要说明你的理解，以便理解偏了时用户能纠正你，然后继续。

## 第 2 步：建立代码锚点

在启动调查员之前，先把调查锚定在具体的代码上。你需要：

- 相关的文件路径与行号范围
- 关键符号（函数名、类名、常量）
- 一份初始 commit 列表，即最近触及该目标的几个 commit
- 来自 merge commit 的 PR 编号（subject 行中的 `(#1234)` 模式）

这一步直接内联完成。

```bash
# Blame target lines for last-touch commits
git blame -L <start>,<end> <file>

# Full file history, with patches, through renames
git log --follow -p -- <file>

# Last N commits touching the file, PR numbers visible
git log --oneline -20 -- <file>

# Extract PR numbers from a commit message
git log -1 --format=%B <commit>
```

对有实质内容的 commit，用 `gh` 拉取 PR 正文与讨论：

```bash
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

把这些捕获为种子上下文（文件路径、符号、commit、PR 编号、关联工单 ID），并传递给各位调查员。

## 第 3 步：并行启动调查员（默认姿态）

**默认执行完整的并行调查。**

### 发现

在启动调查员之前，先列出 Claude Code 环境中可用的 MCP。可以使用系统提示词顶部的工具列表（每个 MCP 都会以带 `mcp__<server>__<name>` 前缀的工具形式出现）；否则读取插件/项目中的 `.mcp.json`，或运行 `claude mcp list`。

把每个可用的 MCP 归入一个证据类别：

1. 版本控制历史
2. Issue / 工单跟踪器
3. 长文档
4. 实时团队聊天
5. 基础设施可观测性
6. 错误 / 异常跟踪
7. 产品分析数仓

版本控制通过 git 和 `gh` 总是可用。对其余六类，依据 MCP 名称、server instructions、工具名和资源描述来分类。如果某个 MCP 可能属于多个类别，就选与其主要证据相匹配的那一类，并把含糊的情形记入覆盖地图。

目标是得到一份完整的**覆盖地图**，而不是最简版。把空结果记录下来，不要跳过搜索。

在单条消息中启动所有匹配的调查员，让它们并发运行。不要让一个 agent 覆盖多个 MCP。

每个 subagent 的配置：
- `subagent_type`: `general-purpose`
- `model`: `why investigators` 那一行，默认值见[模型](#模型)
- `readonly`: `false`（agent 模式）。**不要使用 readonly/Ask 模式。**它会剥离 MCP 访问，使依赖 MCP 的调查员完全失效。调查员仍不应写入任何东西。

每位调查员会拿到：
1. 来自 `references/investigator-prompt.md` 的基础 prompt
2. 所选 MCP 对应的类别行动手册 `references/sources/<source>.md`，在 `references/source-playbook.md` 的示例基础上适配
3. 横向通用的 `references/sources/incident-postmortem.md`——**当目标代码看起来具有防御性时**（空值检查、重试逻辑、超时处理、限流、功能开关、出口防护、OOM 处理器）
4. 第 2 步的代码锚点（文件路径、符号、commit 哈希、PR 编号、工单 ID）
5. 用户的原始问题

### 调查员名册。每个可用的证据类别一名

有多少类别存在匹配的 MCP，就为该类别启动一名调查员。每人恰好负责一个工具或 MCP。

下面每一条都点明了类别，以及它能独特揭示的“为什么”是哪一种。用它来预期能拿回什么、当某类别返回为空时如何指名这个缺口，以及（只在罕见的可证明无关的情形下）为跳过提供理由。

1. **版本控制调查员**。Git 历史、用于 PR 的 `gh`、代码注释、测试。总是启动。唯一有保障的来源。最擅长发掘*评审期间记录下来的实现期理由*。

2. **Issue / 工单跟踪器调查员**（如 Linear、Jira、GitHub Issues、Plane、Shortcut MCP）。最擅长发掘*产品或业务上的推动因素*。当“为什么”源自工程之外时最有用。

3. **长文档调查员**（如 Notion、Confluence、Google Docs、Coda MCP）。最擅长发掘*成篇的设计缘由*。“为什么”在变成代码之前，往往先写在这里。

4. **实时团队聊天调查员**（如 Slack、Discord、Microsoft Teams、Mattermost MCP）。最擅长发掘*从未落进文档的实时讨论*。当版本控制、工单和文档构成的书面记录很单薄时尤其重要。

5. **基础设施可观测性调查员**（如 Datadog、New Relic、Honeycomb、Grafana、Splunk MCP）。基础设施/运行时视角。最擅长发掘*促成这段代码的基础设施与运行时实况*。当目标是对某个基础设施信号（超时、重试、限流、熔断）作出反应时最有用。

6. **错误 / 异常跟踪调查员**（如 Sentry、Rollbar、Bugsnag、Airbrake MCP）。最擅长发掘*促使人们编写防御性或纠正性代码的那些具体异常与错误轨迹*。对 catch 块、空值保护、类型检查、重试等防御手段最有用。

7. **产品分析数仓调查员**（如 Databricks、Snowflake、BigQuery、ClickHouse、dbt、Redshift MCP）。产品/数据视角。最擅长发掘*塑造了这段代码的产品与数据实况*。对由功能开关把守的代码、由实验驱动的上线、数据迁移，以及“这个数字是哪来的”一类问题最有用。

### 何时可以跳过某位调查员

只有在给出**明确的书面理由**时才可以跳过，该理由要写进最终的“已查阅来源”一节。只有两种正当理由：

- **该类别在此环境中没有可用 MCP**。要把这一点标记为缺口，而不是你的选择。示例：“跳过实时团队聊天：没有匹配的 MCP 可用，因此无法搜索对话记录。”
- **能证明该来源与问题无关**，而不只是“大概无关”。门槛很高。示例：“跳过错误 / 异常跟踪：目标是构建期脚本，不存在运行时代码路径。”

如果你的范围评估显示目标琐碎、只有单个 commit，且 PR 描述已包含完整答案，那么**只有**在确认全部七个可用类别的搜索都会是重复劳动**之后**，才可以直接内联作答。要明确说出来。这种情况应当罕见。

## 第 4 步：综合

启动一个综合者 subagent：

- `subagent_type`: `general-purpose`
- `model`: `why synthesizer` 那一行，默认值见[模型](#模型)
- `readonly`: `false`（agent 模式）。综合者的质量检查会抽验引用，这可能需要 MCP 访问权限。Readonly/Ask 模式会剥离 MCP，使这一步失效。

综合者会拿到：
1. 各调查员的发现，包括空结果，以及带理由跳过的类别
2. 第 2 步的代码锚点（文件路径、符号、commit 哈希、PR 编号、工单 ID）
3. 用户的原始问题
4. 来自 `references/epistemics.md` 的认知边界框架
5. 来自 `references/synthesizer-prompt.md` 的综合者 prompt 模板

## 第 5 步：呈现

取综合者的输出，呈现给用户。可以为清晰起见稍作编辑，或补充对话中的上下文，但**不要改写置信度措辞**。

## 输出格式

输出结构采用 `references/synthesizer-prompt.md` 中的那一份：问题、涉及的代码、我们的发现、可合理推断的内容、竞争性假设、我们不知道的、已查阅来源、置信度摘要。可以按需调整，但要保持置信度分层的完整性；“已查阅来源”要保持每位调查员一行，包括没有返回结果或被跳过的，并附上原因。

在“已查阅来源”块之后，如果用户的 `why` 问题只是真正改动这段代码的前奏，就把代码沿革的发现转化为适合规划改动的“保留 / 修改 / 避免 / 风险”约束集。

## 需要避免的常见失败模式

- **近因偏差**。假定最近的 commit 具有权威性。代码当前的形态往往是多次更早决策层层累积的结果。要向上追溯。

## 参考文件

- `references/epistemics.md`。置信层级与措辞指南。综合者必须遵循它。
- `references/investigator-prompt.md`。调查员 subagent 的基础 prompt 模板。
- `references/source-playbook.md`。指向下列类别行动手册的索引。
- `references/sources/*.md`。每个类别一份内容完备的示例行动手册，另有横切的 `incident-postmortem.md`。给调查员的只需与其类别匹配的那一个文件，并按可用 MCP 适配。
- `references/synthesizer-prompt.md`。综合者 subagent 的 prompt 模板，包含输出格式。

## 模型

角色默认值，从 `plugins/pstack/models.json` 生成（在那里编辑，然后重跑 `tools/generate.mjs`）。`pstack-models.md` 覆盖清单中匹配的角色行会在运行时覆盖这里的各项默认值；`/setup-pstack` 会写入该清单，并列出它在各运行时中的路径。

- why investigators: `opus`
- why synthesizer: `opus`

## 推理力度

覆盖清单中的角色值可以在模型后面附带一个推理力度，例如 `opus @xhigh`。Claude Code 上的档位有：`low`、`medium`、`high`、`xhigh`、`max`。哪些档位可用取决于模型。不带 `@` 的值采用清单中的 `default effort` 行——它是一个档位或 `session`；若清单没有这一行，则取 `session`。`session` 不设置力度，派发方式与平常相同。读取模型前要先剥掉后缀：无论哪一档，`inherit-parent` 或 `auto` 仍然省略 `model`，而模型名则作为 `model` 传入。在 Claude Code 上，某一档位会从你原本要用的 `subagent_type` 选出对应的 effort agent：`pstack:poteto-agent` 会变成 `subagent_type: "pstack:poteto-agent-<level>"`；`general-purpose` 或未指定 `subagent_type` 则变成 `subagent_type: "pstack:effort-<level>"`。这些 effort agent 只设置 `effort`，因此你传入的模型仍然决定实际模型。在 Codex 上，把档位作为 `spawn_agent` 的 `reasoning_effort` 传入，其余指令照常。
