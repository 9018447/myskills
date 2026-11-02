---
name: principle-laziness-protocol
description: "Apply when refactoring or tempted to add an abstraction, layer, wrapper, or signal threading. Signals: \"should I generalize this?\", a growing diff, new config or indirection, speculative flexibility, evaluating diff size."
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

# Laziness Protocol

- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
