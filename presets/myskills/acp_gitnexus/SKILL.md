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
2. **派发**：默认**一次派发覆盖全部票据**；票面工作总量超出一个会话能可靠完成的量时，按票据边界分两次派发（先派发无阻塞的前批），不得拆碎到一票一派。派发前记录当前 `HEAD` 和 `git status --short` 作为基线。headless 细节（pane 验证、watcher、完成判据、候补链）见 `/acpx` 与 `/acpxtodo`，不在此重复。
3. **核验与评审**：执行者完成后，编排者抽查关键 diff、每票验收标准、执行者声称的验证结果——自述与盘上证据冲突时以盘上证据为准。然后按 `/jev-code-review` 评审本次闭环的全部 commit。有修复经新派发回到执行者，复评受影响部分，不创建空 commit。

## 派发 Prompt 模板

```markdown
# 任务：<一句话目标，含当前主要矛盾>

## 规范与票据

- 规范：<spec 路径>
- 票据：<tickets 目录或编号范围>，按阻塞边顺序执行。
- 范围以规范和票面为准，不扩大范围，不做无关重构和过度设计。

## 执行流程

逐票执行，每票：/gitnexus-plan 出计划 → 图谱事实不足用 /gitnexus-exploring 补齐
→ 按 /gitnexus-work 纪律实现（impact 前置、最小改动、跑 verification_commands）
→ 一票一提交，commit message 标明票号。

## 禁止事项

- 不派发 subagent，不再次使用 /acpx；
- 不跑 code-review（评审由编排者在你提交后做）；
- 规范、票据与代码现状发生实质冲突时停下报告，不自行改写设计。

## 完成判据

每票验收标准逐条满足并有证据（测试名、命令输出、文件路径）；
每票恰好一个 commit；结尾列出票号 → commit → 验收证据对照表。
```

提示词中的文件路径必须先在盘上验证存在（ls/grep）；验证不了就让执行者自行定位，不断言未验证的路径。
