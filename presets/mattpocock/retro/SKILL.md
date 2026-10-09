---
name: retro
description: "对一次编码会话进行回顾复盘（retrospective）。"
disable-model-invocation: true
---

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

## Steps

1. Call the Skill tool with `writing-for-agents` for the writing style guide. 

2. Read the primary sources for the session the user specifies. This may mean searching through session logs on this machine. If the user doesn't specify a session, default to the current one.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? Linting, typing, tests, filesystem linters? Read the repo's own check command first (its `package.json`/build-tool `lint`/`check` scripts, its CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook and no CI job running its lint/typecheck/test command) is itself a finding: an un-linted repo is a standing missed opportunity, not a neutral default. _Use when_ the agent made a mistake an automated check could have caught, or the repo has no guardrail at all.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop: a custom rule in the repo's own linter, a new pre-commit hook, or a new CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style," anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? Is there any custom tooling (CLI's, MCP's) that is particularly token-inefficient? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.

4. 对每条结论做**归因判定**（见下节）：确定它应由哪个技能承载，以及它是通用规则还是仅本次适用。

5. Present these candidates to the user, in order of severity.

## 归因判定

呈现结论前，每条改进先经过一次 jev 归因判定，不凭主会话印象挑技能：

1. **提取已用技能清单**：从会话日志里机械提取本次实际调用过的每个技能（Skill 工具的调用记录），并标注触发方式——用户手动调起，还是模型自主触发。这份清单就是判定器的候选池；不枚举全仓库技能，判定器只做归因。
2. **jev 判定**：把「本次事故的具体证据 + 已用技能清单（带触发方式）+ 结论草稿」组装成 state，一次请求批量问两个独立问题：
   - choice：这个结论应由哪个技能承载？选项 = 已用技能清单 + 显式的"无归属"。判定标准写进问题："无归属"是正当结论而不是判定失败，没有充分证据时不硬选一个。
   - 是否通用：这个结论是通用规则，还是仅本次适用？
   低置信度或 escalate 的结论由主 agent 自己复核——jev 是决策辅助，不是授权边界。
3. **无归属分流**：判为无归属的结论，用事故关键词对 myskills 的技能描述跑一次 zg 定向检索（索引未覆盖或过期先 `zg index` 重建，不静默降级到 rg），把两种成因分开：
   - **搜到现成技能**：该技能存在但本次没被触发。修复落在它的 description 触发条件上，用本次事故的真实问法作为触发测试，改完验证这个问法能命中。
   - **没搜到**：库里确实没有技能管这件事，落档走"记忆或新建技能"层。
   触发方式为手动调起的技能，若其覆盖范围本应包含本次事故，归因时优先怀疑它的 description 没拦住该拦的活。

## 落档优先级

每条反思结论按这个顺序找落点，前一层装得下就不落到后一层。每条结论必须写成「触发条件 → 行为」的形式：触发条件写明未来什么样的会话会命中它，写不出的结论只是本次问题的点状补丁，不落档。

1. **已有技能迭代** —— 归因判定选中某个技能的（改流程、加检查步骤、补触发条件），先迭代那个技能的 SKILL.md；判为"有但没触发"的，改的是那个技能的 description 触发条件。
2. **CLAUDE.md / AGENTS.md** —— 不属于任何技能、但每轮会话都该生效的导航指针或硬约束，落到对应的 steering 文件。
3. **记忆或新建技能** —— 前两层都装不下的行为约定，最后才写入记忆（无技能指引时的行为约束），或确有复用价值时新建技能。

## Reference

### Implementation vs Review

Remember that all work goes through two stages: implementation and review. The implementation agent has the most **context pressure**. They are responsible for exploration, writing code, and debugging failures.

The review agent has the least context pressure - it receives a diff, so no exploration needed. It often does not need to write code or debug.

This means that the review agent should be responsible for imposing coding standards, not the implementation agent.

### Files

You have access to several files in the repo:

- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. They should be used incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: this file is read during review, not implementation. Add **navigation pointers** to docs folders if the standards file gets more than 1,000 lines long.
- Docs: use docs as references files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into
