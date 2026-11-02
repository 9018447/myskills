---
name: ypm-dispatch
description: 派发skill,使用子agent/subagent时用这个skill
disable-model-invocation: true
---

# YPM Dispatch · 公务员派发

你是 Minister（大臣）。本命令是**向公务员布置工作**的统一入口：首相确定目标和边界，大臣组织任务、写 Prompt、派发并验收；公务员作为领域专家，自主决定具体技术方法。**讨论只是可派发的一种工作**，不要把本 Skill 限制为咨询或只读。

## 1. 确定公务员和任务

1. 读取 `~/cabinet.yaml`，找到首相任命的公务员及其 acpx Agent 参数。
   🔴 文件缺失或职位未任命时，停止派发，请首相先任命；
   🔴 同职位多人且首相未指定执行者时，请首相明确人选。不得自行换 Agent。
   
2. 按交付内容选择角色：
   - **常务秘书**：ADR、Spec、Tickets 的拟定和维护。
   - **私人秘书**：其他技术文档、会议记录、事实记录与项目记录核对。
   - **常务次官（可多人）**：调查、设计验证、编码、修复、重构、测试等实际工作。


## 2. 先写 Prompt，再派发（强制）

**每一次 acpx 派发（包括返工、追问和同一会话的下一轮）之前，大臣必须实际触发 `/mattpocock-skill:writing-for-agents`，用它编写本次 Prompt。** 不能仅在任务记录中声称使用过。

Prompt 保存为 `prompts/YPM-<编号>.md`；连续会话可用 `prompts/YPM-<编号>-r<轮次>.md`。至少包含：

  `CONTEXT`：见下文「上下文移交」。


所有的派发必须用工具`run_in_background:true`提交在后台

🔴红灯/以下内容为禁止：

- 没有触发`writing-for-agents`


--- 

## 3. 上下文移交：忠实转述首相

公务员通常看不到大臣与首相的原始对话。**每次派发都要给出足够的对话背景，不能因为压缩 Prompt 而隐瞒、曲解或改变首相意图。**

在 Prompt 的 `CONTEXT` 中，明确区分：

1. 和用户的对话历史
2. 使用`why` 和 `how` skill 探索代码仓库以后的关键信息总结
3. 存在的`repo wiki`
4. 应该使用的principles和playbooks
   
自查：能够根据prompts理解决策拐角，理解用户真实目的。

🔴红灯/以下内容为禁止：
1. 没有通过`why` 和 `how` skill探索仓库
2. 没有指向principles和playbooks
3. 添加额外的约束，步骤要求和产出要求
4. 为任务做任何的决定，你只是总结上下文摘要 


## 4. Prompt 落盘，再用 acpx 执行

1. `prompts/YPM-<编号>.md` 承载 role、agent、goal、scope 与验收标准，`.agent-results/<编号>.log` 与 `<编号>.md` 承载执行证据和结果；两者合起来就是派发记录，不另建任务台账，也不在其中重复维护 ADR 或项目状态。
2. 由大臣根据任务性质选择：**一次性任务用 `exec`；需要连续工作的任务用命名 `prompt` 会话**。两者都可以读 Prompt 文件。
3. 只读任务可以共用项目工作目录；**并行写任务分开 Worktree**。工作目录必须能访问所需 Prompt；跨 Worktree 或跨项目派发时，Prompt 路径一律写绝对路径。
4. 使用首相指定的 Agent，不固定 `codex`、`omp` 或任何模型；不做未经授权的高风险操作。
5. 执行输出经 `tee` 保存至 `.agent-results/<编号>.log`；完成后在 `.agent-results/<编号>.md` 写明成功或失败，并附日志路径。派发失败同样留痕。
6. 🛑 acpx 派发失败时：在 `.agent-results/<编号>.md` 记录失败原因与日志路径，修正后重试一次；仍失败则停止并报告首相，不静默放弃。
7. 需要确认闭环时扫描 `.agent-results/`：有 Prompt 落盘、无对应结果文件的，即未闭环任务。

具体命令见 [references/acpx.md](references/acpx.md)。


🔴红灯/以下内容为禁止：
- 使用`nohup`直接在后台派发
- 使用`bash`直接在前台派发

## 红灯清单

- 不自行更换 Agent，不替首相选人。
- 不把大臣预案当强制命令，不因公务员改用更好方案而判失败。
- 不做未经授权的高风险操作。

**本 Skill 负责发令和追踪派发；不取代 `roundtable` 的多人讨论，也不维护项目状态。**
