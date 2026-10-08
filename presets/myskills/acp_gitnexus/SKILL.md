---
name: acp_gitnexus
description: "中等任务的快速闭环：/gitnexus-plan 出计划，经 /acpx 派发实现（worker 按 /gitnexus-work 纪律执行），/jev-code-review 收盘。长程复杂任务仍用 /acpxtodo 一票一闭环。"
tags: [user]
disable-model-invocation: true
---

以 gitnexus 图谱为事实来源的中等任务实现流程。实现一律经 `/acpx` 派发，编排者不亲手改代码。

## 适用边界

任务能用一份 gitnexus 计划覆盖、无需拆票时用本技能。出现以下任一信号改用 `/acpxtodo`（先 `/split-tickets` 拆票）：

- 交付需要多个可独立验证的垂直切片；
- 含时长不可控的真实运行（运行票必须单拆）；
- 计划阶段发现影响面波及全库的机械性变更（走 expand-contract 拆票）。

## 固定闭环

```text
任务确认 → /gitnexus-plan 出计划 → /acpx 派发实现 → /jev-code-review 评审 → 修复复评 → git commit
```

1. **计划**：编排者运行 `/gitnexus-plan`，产出计划文档（含 §11 implementation_context pack：files_to_modify、tests、verification_commands、avoid）。图谱事实不足或索引过期时先用 `/gitnexus-exploring` 补齐，不凭经验补全。计划阶段暴露任务实际大于中等规模 → 停下升级到 `/acpxtodo`，不硬塞。
2. **派发**：派发前记录当前 `HEAD` 和 `git status --short` 作为基线（拿不到就显式记"status 未知"并补一次真实 status）。按下方模板写派发 Prompt 落盘，经 `/acpx` 派发；headless 细节（pane 验证、watcher、完成判据、候补链）见 `/acpx` 与 `/acpxtodo`，不在此重复。worker 按 `/gitnexus-work` 纪律执行，但**不提交 git**——提交权在编排者，评审通过后才 commit。
3. **评审**：worker 完成后按 `/jev-code-review` 评审本任务 diff。有修复才复评受影响部分、才有第二次 commit，不创建空 commit。
4. **提交**：评审通过后编排者 `git commit`。纯文档 / 纯 markdown 改动可豁免评审轮，但豁免须在 commit message 显式声明。

自述与盘上证据冲突时以盘上证据为准；worker 声称完成不代替验收，至少抽查关键 diff 与其声称的验证结果。

## 派发 Prompt 模板

```markdown
# 任务：<一句话目标，含当前主要矛盾>

## 计划

按 <计划文档路径> 执行，先读 §11 implementation_context pack。
其中范围边界、avoid、pdg_constraints 是硬约束；acceptance_criteria 是验收标准。

## 执行纪律（按 /gitnexus-work）

- 每个符号编辑前跑 impact（direction: "upstream"），d=1 依赖全部入账；
  HIGH/CRITICAL 风险先报告再动；
- 最小改动，遵守计划范围，不做无关重构和过度设计；
- 计划 tests[] 场景落成真实测试，行为变化必须有验证；
- 跑计划里的 verification_commands；改动经构建产物生效的先重建再验证。

## 禁止事项

- 不提交 git；
- 不再次使用 /acpx 或 subagent 向下派发；
- 不跑 code-review（评审由编排者在提交前做）；
- 计划与代码现状发生实质冲突时停下报告，不自行改写设计。

## 完成判据

verification_commands 全绿，且 acceptance_criteria 逐条满足；
在结尾逐条列出每条验收标准对应的证据（测试名、命令输出、文件路径）。
```

提示词中的文件路径必须先在盘上验证存在（ls/grep）；验证不了就让 worker 自行定位，不断言未验证的路径。
