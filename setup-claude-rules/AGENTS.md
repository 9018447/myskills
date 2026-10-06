## Tool Routing

Use specialized code search tools instead of shell `grep`/`find` or built-in `Grep`/`Glob`:

- File discovery: `rg --files`
- Content search: `zg` (default) · `zg --rg` (exact text / regex)
- Structural matching: `ast-grep`
- Symbols (definitions, references, types, call hierarchy): LSP
- Graph relations (call chains, dependencies, impact analysis, architecture): `GitNexus`

Escalate from cheap to expensive: `rg --files → zg → ast-grep / LSP → GitNexus`. After locating code, use `Read` on the exact source before concluding or editing.

The full routing policy, including tool boundaries and escalation flows, lives in `.claude/rules/code-search.md`.

## Division of Labor

Claude Code（主 agent）不做编码，只写文档、编排任务、把握全局。所有编码工作——修 bug、写测试、写新代码、重构——一律派发：零碎和单文件的改动由主 agent 用 aider-rs 的 `aider_task` MCP 工具快速派发（`files` 锁目标文件），跨文件改动用 `/acpx` 派发，完整实现流程由用户以 `/implement-zh` 启动。细则见 `.claude/rules/coding-principle.md`。
