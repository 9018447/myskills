---
name: implement
description: "基于 spec 或一组 tickets 实现工作内容。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。

## Agent 分发

使用 `/acpx` 逐票分发。实现 Agent 由用户指定，可作为参数传入：

```text
/implement kimi
/implement kimi 1-5 codex 6-7
```

第一种表示全部 Tickets 依次交给 `kimi`；第二种表示 Tickets 1–5 给 `kimi`，6–7 给 `codex`。

Agent 选择规则：

1. 用户明确指定 → 使用用户指定；
2. 用户未指定，但票面标注 `含 N 次真实运行` 或预计真实运行总时长 ≥20 分钟 → 默认 `claude`；
3. 其他情况用户未指定 → 必须询问，不得自行选择。

当前 Agent 只有在额度耗尽、不可用、启动/执行失败时才进入候补链。代码有 bug、测试失败或 Review 发现问题不属于 Agent 不可用，应继续本票修复。

候补链：

```text
08:00–18:00：kimi → claude
18:00–08:00：zcode → claude → dsh
```

调用 `zcode` 或 `dsh` 前必须查询当前真实时间，不得依赖上下文时间推断。

如果运行预算超过当前执行环境允许的上限，停止并报告，不得擅自拆 Ticket 或无限增大 timeout。

## 一票一闭环

Tickets 原则上依次执行。每个 Ticket 单独开启一个新的 `/acpx` 会话，不得多票共用一个会话。

当前 Ticket 未完成闭环，不得派发下一 Ticket。

派发前记录当前 `HEAD` 和 `git status --short`，用于区分本票改动与已有未提交内容。不得顺手提交无关改动。

派发 Prompt 必须告诉实现 Agent：

1. 整个任务的目标和当前主要矛盾；
2. 当前 Ticket 对解决主要矛盾的作用；
3. 遵守当前 Spec、ADR 和 Ticket 范围；
4. 使用 `/tdd` 完成实现；
5. 不扩大范围，不做无关重构和过度设计；
6. 完成后使用 `/handoff-for-mattpocock`；
7. 不得再次使用 `/acpx` 或 `subagent` 向下派发。

如果 Spec、ADR、Ticket 存在无法解释的实质冲突，停止本票并报告，不得自行改写设计。

## Headless 派发

按 `/acpx` headless dispatch pattern 执行：

* 派发 Prompt 写入文件后后台启动，日志写入文件；
* `--timeout` 按 Ticket 运行预算设置；
* 不阻塞轮询，只通过任务完成通知或日志中的 `[done] end_turn` 判断结束；
* 查看进度仅短暂读取日志；
* `[done] end_turn` 后若包装进程仍存在，用已记录 PID 经 `ps -p <pid>` 确认后清理，不用 `pgrep -f`。

任务中断后续作时，先审计盘上现状，保留符合 Ticket 的已有成果，再补完剩余验收，不得默认推倒重来。handoff 中记录中断和续作事实。

## 固定闭环

每票严格按以下顺序：

```text
Ticket
→ /acpx 独立实现
→ /tdd
→ Agent 跑绿本票要求的检查
→ /handoff-for-mattpocock
→ git commit
→ /open-code-review-delegate
→ 独立事实核验
→ 修复有效问题
→ 定向测试
→ git commit（有修复时）
→ 必要时复审
→ 下一 Ticket
```

Agent 交付后直接提交第一次 commit，不在 commit 前插入额外实现步骤。

Review 中凡是事实成立且属于当前 Ticket 范围的问题都应修复；范围外问题记录但不顺手扩展本票。

修复后重新验证受影响部分。有修复才提交第二次 commit，不创建空 commit。

## 事实核验

不要因为实现 Agent 声称完成、测试通过或 Review 无报错，就直接认定 Ticket 正确。

至少抽查：

```text
关键 diff
Ticket 验收项
Agent 声称的关键测试/运行结果
```

必要时检查 Spec、ADR、日志、测试、生成物和 handoff。自述与盘上证据冲突时，以盘上证据为准。

实现 Agent 负责把 `pnpm run check` 或项目等价检查跑绿。编排者默认不重复跑完整 check；只有结果可疑、发生修复、缺少验收证据或 Ticket 明确要求时才定向复跑。

## 方法论

整个 `/implement` 以毛泽东思想的方法论原则指导执行，但落实为具体工程行为：

* **实事求是**：以 Spec、ADR、代码、测试、日志和实际运行结果为准，不迷信 Agent 或 Review 的文字结论。
* **调查研究**：事实不清先查代码、日志、测试和历史设计，不凭经验补全。
* **具体问题具体分析**：结合当前 Ticket、代码状态和实际约束判断，不机械套模板。
* **抓主要矛盾**：每票都要明确它解决什么核心瓶颈；不能推动主要矛盾的工作不要因为“更完整”而增加。
* **实践检验**：正确性最终由测试和真实运行验证，优先采用成本最低但有判别力的实验。
* **从实际需求出发**：以真实目标而不是代码量、复杂架构或形式完整性判断价值。

## 最终验收

全部 Tickets 完成后，再从整体 Spec 和 ADR 检查一次：

```text
局部 Tickets 全部完成
≠
整个任务一定完成
```

必须确认各 Ticket 组合后真正实现了整体目标、接口闭合且最终实际路径成立。不得用 `completed` 状态代替最终事实验证。
