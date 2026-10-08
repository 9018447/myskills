# pstack 本地副本改动记录

本目录是 pstack-claude 的本地副本，为适配「主 agent 编排 + acpx 派发」工作流做的改动记录在这里。上游原文以 pstack-claude 包为准。

## 2026-10-XX 派发化改造

poteto-mode：

- 实现阶段的派发链定为 grilling → /split-tickets → /acpxtodo → /open-code-review-delegate，playbook 里的实现步骤经此链交接，主会话不直接写生产代码。
- Subagents 节改为 Delegation：代码实现代理一律走 acpx 派发（omp/kimi/codex/dsh，herdr 承载，日志落盘），不再用内置 Agent 工具；保留「主 agent 拥有产出、新工作用新代理、废弃代理先停、独立评审门不放过」的纪律内核。
- Models / Reasoning effort 两节删除：角色→模型覆盖路线废弃，代理选择只看 /acpxtodo 路由表与 /acpx 能力对照表（setup-pstack 的模型覆盖表降为可选）。
- Non-negotiables 增两条触发：实现类任务走派发链；判定类检查（复审分诊、完工确认、事实核对）走 jev。中文输出对齐说人话规则。swarm/arena/interrogate 多代理面板改并发 herdr pane 或降级单次顺序执行。
- 删除 autopilot-full、autopilot-stack、orchestrate 三个子代理舰队 playbook（与派发工作流不适配），babysit、multi-phase-plan、shipping、opening-a-pr 及 references 中的相关引用同步清理。

其余技能：show-me-your-work、deslop、setup-pstack 的适配与全量 subagent→acpx 审计随本批次进行（见各自改动）。
