---
name: principle-exhaust-the-design-space
description: "Apply when facing a UI interaction or architecture choice with no precedent in the codebase, or one whose quality depends on feel. Signals: \"how should this work?\", novel component, no existing pattern to copy, picking between approaches."
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

# Exhaust the Design Space

When a decision has no precedent in the codebase, you cannot reason to the right answer from the code alone. Choose the shape by building the candidates and looking at them, not by arguing about them in the abstract.

**Why:** A novel interaction or architecture choice has properties you can only see once it exists. Committing to the first idea you can imagine locks in a design picked from a single sample of a space you never looked at.

**Pattern:**
- Name the decision and the two or three genuinely different ways to make it. Variations on one idea count as one candidate, not several.
- Build each as a throwaway, minimal prototype: enough to feel it, not to ship it. Plan to delete the code.
- Put the working candidates side by side and compare them against what actually matters for this decision.
- Commit to one, then remove the losers.

It also applies to product design decisions where user experience depends on feel, not logic. A feel cannot be argued into being; you learn it only by seeing the options next to each other.

Distinct from [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md), which rebuilds one existing design around a new requirement. This explores a space where no design exists yet.
