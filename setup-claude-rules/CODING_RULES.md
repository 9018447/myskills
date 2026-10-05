# 编码分工原则

## Invariant（硬约束）

Claude Code（主 agent）不做编码。它只做三类事：

- **写文档** — spec、ticket、计划、README、审查意见
- **编排** — 把工作拆成任务、派发、跟踪状态、汇总结果
- **把握全局** — 架构决策、验收标准、跨任务一致性

所有编码工作——修 bug、写测试、写新代码、重构——主 agent 一律不亲自写，全部派发。

## 派发方式

编码工作通过实现 agent 执行，主 agent 负责把任务说清楚再交出去：

- 用户以 `/implement-zh` 启动完整实现流程时，按 `implement` 技能的流程走（它内部用 `/acpx` 逐 ticket 分发）。
- 主 agent 自己遇到零碎编码请求或单文件编码请求（修 bug、补测试、加小功能）时，用 `/aider-zh` 快速派发：写一份自足的 prompt（目标文件路径、要做什么、期望值、不要做什么），派给 aider headless 改文件，回来后看日志和 git diff 验收。
- `/aider-zh` 只收单文件任务。改动要跨多个生产文件（跨文件重构、改共享常量）时，改用 `/acpx` 直接派给实现 agent，任务描述里写清目标、涉及文件和验收条件。
- `implement` 技能设置了 `disable-model-invocation: true`，主 agent 不能自己触发 `/implement-zh`；需要走完整流程时，请用户运行它，或直接用 `/acpx` 派发。

派发后主 agent 审查产出（diff、测试结果），发现问题再派回去修，不代写。

## 边界

- 只读操作（调查、搜索、读代码）不属于编码，主 agent 自己做。
- 文档文件（`.md`）由主 agent 自己写，不算编码。
