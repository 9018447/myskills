---
name: principle-guard-the-context-window
description: "Apply when context is filling up on a long run. Signals: large outputs, reading big or long files repeatedly, fan-out planning, \"context almost full\", compression kicking in."
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

# Guard the Context Window

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

**Pattern:**
- **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.
