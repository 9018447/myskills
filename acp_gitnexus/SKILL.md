---
name: acp_gitnexus
description: "中等任务的快速闭环：编排者用 /to-spec + /split-tickets 写规范和票据，执行者经 /acpx 一次派发内跑完 /gitnexus-plan → /gitnexus-exploring → /gitnexus-work，一票一提交，编排者 /jev-code-review 收盘。长程复杂任务仍用 /acpxtodo。"
tags: [user]
disable-model-invocation: true
---

中等任务的快速闭环。与 `/acpxtodo` 的分工差异：gitnexus 流水线（计划/探索/执行）全部下放给执行者在一个派发会话内完成，编排者不逐票陪跑。

## 分工

- **编排者**：`/to-spec` 写规范、`/split-tickets` 拆票、派发、事实核验、`/jev-code-review` 评审、修复复评。不亲手实现。
- **执行者**（经 `/acpx` 派发）：一个会话内按 `/gitnexus-plan` → `/gitnexus-exploring`（图谱事实不足时）→ `/gitnexus-work` 完成票据实现，一票一提交。

## 固定闭环

```text
/to-spec 写规范 → /split-tickets 拆票 → 用户确认票面 → /acpx 派发（尽可能一次）
→ 执行者逐票实现、一票一提交 → 编排者核验 → /jev-code-review → 修复复评
```

1. **规范与拆票**：编排者先 `/to-spec` 再 `/split-tickets`，票面含验收标准与阻塞边，交用户确认后才派发。拆票时暴露任务实际为长程复杂任务（多切片强依赖、时长不可控的真实运行）→ 改用 `/acpxtodo`。
2. **派发**：默认**一次派发覆盖全部票据**；票面工作总量超出一个会话能可靠完成的量时，按票据边界分两次派发（先派发无阻塞的前批），不得拆碎到一票一派。派发位置默认**主检出而非票级 worktree**：`.gitnexus/` 索引不进 git，worktree 里相对调用 `node .gitnexus/run.cjs` 会失败，且图谱只覆盖主检出已索引提交（执行者新写的代码不在图里，索引可能落后 main）——本技能的 GitNexus 流水线在主检出才完整生效。执行者确需 worktree 时，编排者在 prompt 里写明 GitNexus 的 worktree 用法（2026-10-09 实测）：用主检出绝对路径调启动器并 `--repo <主检出>`（`node <主检出>/.gitnexus/run.cjs query|impact|trace <目标> --repo <主检出>`），图谱结论编辑前用 Read 对照 worktree 源码核实，不裸 grep。派发前记录当前 `HEAD` 和 `git status --short` 作为基线。headless 细节（pane 验证、watcher、完成判据、候补链）见 `/acpx` 与 `/acpxtodo`，不在此重复。
3. **核验与评审**：执行者完成后，编排者抽查关键 diff、每票验收标准、执行者声称的验证结果——自述与盘上证据冲突时以盘上证据为准。然后按 `/jev-code-review` 评审本次闭环的全部 commit。评审口径固定：本快速闭环用 `/jev-code-review`（轻、快）；`/acpxtodo` 长程任务用 `/open-code-review-delegate`（逐文件、覆盖强制），不混用。有修复经新派发回到执行者，复评受影响部分，不创建空 commit。
4. **决策日志**：执行者按 show-me-your-work 约定把决策记入 `.scratch/<feature>/decisions.tsv`（每票 `start`/`dispatch`/`close` 必记，列式与语义见 `/show-me-your-work`）；编排者收盘核验时抽查日志，票号对不上的 commit 退回补记。

## 派发 Prompt 模板

```markdown
# 任务：<一句话目标，含当前主要矛盾>

## 规范与票据

- 规范：<spec 路径>
- 票据：<tickets 目录或编号范围>，按阻塞边顺序执行。
- 范围以规范和票面为准，不扩大范围，不做无关重构和过度设计。

## 执行流程

- 执行位置：主检出（编排者已在 prompt 里确认过 `.gitnexus` 索引在位；若编排者改派 worktree，GitNexus 用法：`node <主检出>/.gitnexus/run.cjs query|impact|trace <目标> --repo <主检出>`，图谱只覆盖主检出已索引提交，结论编辑前用 Read 对照 worktree 源码核实，不要裸 grep）。
- 逐票执行，每票：/gitnexus-plan 出计划 → 图谱事实不足用 /gitnexus-exploring 和/jev-grep 补齐
→ 按 /gitnexus-work 纪律实现（impact 前置、最小改动、跑 verification_commands）
→ 一票一提交，commit message 标明票号。
- 工作原则注入：每票开始时按票面类型注入对应原则，映射规则与全类型必含项（test-behavior-not-implementation、prove-it-works、minimize-reader-load）见 `/acpxtodo` 派发 prompt 第 11 条，不在此重复。
- 输出文风：对用户的说明性文字对齐说人话规则（中文场景），见 `/acpxtodo` 派发 prompt 第 12 条。
- 决策日志：每票在 `.scratch/<feature>/decisions.tsv` 记 `start`/`dispatch`/`close` 行。

## 禁止事项

- 不派发 subagent，不再次使用 /acpx；
- 不跑 code-review（评审由编排者在你提交后做）；
- 规范、票据与代码现状发生实质冲突时停下报告，不自行改写设计。

## 完成判据

每票验收标准逐条满足并有证据（测试名、命令输出、文件路径）；
每票恰好一个 commit；决策日志每票有 start/dispatch/close 行；
结尾列出票号 → commit → 验收证据对照表。
```

提示词中的文件路径必须先在盘上验证存在（ls/grep）；验证不了就让执行者自行定位，不断言未验证的路径。
