---
description: Nudge shell find/grep/rg toward omp search tools
condition: '(^|[;&|(\s])(sudo\s+)?(find|grep|rg)\b'
scope: ['tool:bash']
interruptMode: never
---

Shell find/grep/rg is the last resort: prefer `glob` / `grep` / `find` and the `jg → zg/ast-grep/GitNexus/LSP` routing (see `.omp/context/code-search.md`). Batch a chain of related calls in one `eval` script so intermediate results stay out of context.
