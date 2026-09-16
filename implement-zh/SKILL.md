---
name: implement
description: "基于 spec 或一组 tickets 实现工作内容。"
tags: [user]
disable-model-invocation: true
---

基于当前 Spec、ADR 和 Tickets 执行实现工作。

使用 `/acpx` 分发 Tickets。实现 Agent 必须由用户指定，可以在调用 Skill 时作为参数传入。

例如：

```text
/implement kimi
```

表示将所有 Tickets 按顺序依次分发给 `kimi`。

```text
/implement kimi 1-5 codex 6-7
```

表示 Tickets 1–5 分发给 `kimi`，Tickets 6–7 分发给 `codex`，依此类推。

如果用户没有指定 Agent，必须先询问用户，不得自行决定。

Tickets 原则上依次执行。每票单独使用 `/acpx` 开启新的 Agent 会话，一票一次，不要把多个 Tickets 堆进同一个会话，避免阻塞、上下文污染和上下文膨胀。

## 派发与等待

派发与收尾按 `/acpx` 的 **headless dispatch pattern** 执行（该节是派发机制的单一事实源）：

- 每票先写派发 prompt 到文件（包含下述 6 点告知事项），再后台启动 acpx，日志落到文件。
- **不阻塞轮询**：启动后结束当前回合，靠任务完成通知或日志里的 `[done] end_turn` 标记判断完成；查看进度用对日志文件的短非阻塞读取。
- 看到 `[done] end_turn` 后，若 acpx 包装进程仍存活，按记录的 PID 清掉（用 `ps -p <pid>` 确认，不用会自匹配的 `pgrep -f` 模式），然后才进入复核环节。

派发每个 Ticket 时，必须告诉实现 Agent：

1. 当前整个任务的目标和主要矛盾；
2. 当前 Ticket 在解决主要矛盾中的作用；
3. 使用 `/tdd` 原则完成实现，默认相关 Skills 已经配置；
4. 不要擅自扩大 Ticket 范围，不做与当前目标无关的过度设计；
5. Ticket 完成后使用 `/handoff-for-mattpocock` 建立 handoff 交接文档。
6. 不能再使用`/acpx`派发或者使用`subagent`工具派发

每票返回结果后，使用 `/open-code-review-delegate` 对实际修改进行 Review。

Review 发现的问题按照严重程度从 High 向下处理。凡是事实成立、属于当前 Ticket 范围的问题，都应修复；修复后重新测试，必要时重新 Review。

不要因为实现 Agent 声称“完成”、测试显示通过或 Review 没有报错，就直接认定 Ticket 正确。必须结合 Spec、ADR、代码、测试和实际运行结果进行独立判断。

整个 `/implement` Skill 必须以**毛泽东思想中的方法论原则**作为主要思维框架，但不要机械引用口号，也不要为了符合某种立场预设结论。

重点执行以下原则：

1. **实事求是。** 不要完全相信派发 Agent 的结果输出，也不要完全相信 `/open-code-review-delegate` 的规则判断。从 Spec、ADR、代码和实际运行结果出发，确认事实逻辑和事实结果。事实与描述不一致时，以实际证据为准。

2. **调查研究。** 遇到不确定问题时，先调查代码、测试、日志、历史设计和实际行为，不凭经验补全事实，不在证据不足时下结论。

3. **具体问题具体分析。** 不机械套用一般规则。每个 Ticket 都要结合当前代码状态、设计约束、上下游依赖和实际目标判断。

4. **矛盾分析法。** 始终从整个任务和全部 Tickets 的角度，分清主要矛盾和次要矛盾，判断当前真正限制任务推进的核心问题是什么。

5. **抓住主要矛盾。** 派发 Ticket 时必须向 Agent 说明整个任务当前的主要矛盾。Ticket 完成后必须再次检查：这一票的实际结果是否真正推动了主要矛盾的解决。如果没有，就不能因为代码增加、测试通过或架构变复杂而认定其具有实际价值。

6. **群众路线。** 从实际使用者和实际需求出发，再回到实际中验证。软件工程中优先解决真实用户问题，而不是从开发者视角追求架构复杂度；科研工作中区分“能够发表的技术细节”和“真正解决科学问题的核心贡献”。

始终保持：

```text
Ticket
→ /acpx 独立实现
→ /tdd
→ /handoff-for-mattpocock
→ /open-code-review-delegate
→ 修复问题
→ 独立事实复核
→ 下一 Ticket
```

一票一闭环。

所有 Tickets 完成后，再从整体 Spec 和 ADR 出发检查一次：局部 Tickets 全部完成，是否真的意味着整个任务已经完成。不得用“所有 Tickets 都是 completed”代替对最终实际结果的验证。

