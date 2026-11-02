---
name: principle-migrate-callers-then-delete-legacy-apis
description: "Apply when a new internal API exists but old callers remain and no external users need backward compat. Signals: leaving a shim or compat layer \"for now\", an old function still referenced after a refactor, breaking-change cleanup."
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

# Migrate Callers Then Delete Legacy APIs

- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details

**When this applies:**
- No external users depend on backward compatibility
- The project can absorb coordinated breaking changes
- The new API is part of a simplification or refactor initiative
