## Tool Routing

Use specialized code search tools instead of shell `grep`/`find` or built-in `Grep`/`Glob`:

- File discovery: `rg --files`
- Content search: `zg` (semantic default — embedding model, tolerates paraphrase) · `zg --rg` (exact text / regex) · `zg` index missing/stale → rebuild with `zg index`, don't degrade to rg
- Structural matching: `ast-grep`
- Symbols (definitions, references, types, call hierarchy): LSP
- Graph relations (call chains, dependencies, impact analysis, architecture): `GitNexus`

Escalate from cheap to expensive: `rg --files → zg → ast-grep / LSP → GitNexus`. After locating code, use `Read` on the exact source before concluding or editing.

The full routing policy, including tool boundaries and escalation flows, lives in `.claude/rules/code-search.md`.

## Division of Labor

Claude Code（主 agent）只写文档、编排任务、把握全局。编码工作：零碎和单文件的改动由主 agent 自己直接完成，跨文件改动用 `/acpx` 派发，完整实现流程由用户以 `/implement-zh` 启动。细则见 `.claude/rules/coding-principle.md`。
