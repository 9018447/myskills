## Tool Routing

Use specialized code search tools instead of shell `grep`/`find` or built-in `Grep`/`Glob`:

- File discovery: `rg --files`
- Content search: `jg` (semantic first stop — natural-language question, returns file list + declaration locations; verify with `jg doctor`) · `zg` (fallback, local embedding index) · `zg --rg` (exact text / regex) · `zg` index missing/stale → rebuild with `zg index`, don't degrade to rg
- Structural matching: `ast-grep`
- Symbols (definitions, references, types, call hierarchy): LSP
- Graph relations (call chains, dependencies, impact analysis, architecture): `GitNexus`

Escalate from cheap to expensive: `rg --files → zg → ast-grep / LSP → GitNexus`. After locating code, use `Read` on the exact source before concluding or editing.

本节是硬约束，不是建议。已观察到的倒退：实际工作中很少用 `zg` 和 `GitNexus`，仍然退回 shell `grep`/`find`，`ast-grep` 几乎从未使用。内容搜索默认 `zg`，精确匹配 `zg --rg`，结构匹配 `ast-grep`，调用链与影响面 `GitNexus`；`grep`/`find` 只在路由层声明的例外情形或路由工具不可用（需当场说明）时才出现。细则见 `.claude/rules/code-search.md`。

The full routing policy, including tool boundaries and escalation flows, lives in `.claude/rules/code-search.md`.

## Division of Labor

Claude Code（主 agent）只写文档、编排任务、把握全局。编码工作：零碎和单文件的改动由主 agent 自己直接完成，跨文件改动用 `/acpx` 派发，完整实现流程由用户以 `/acpxtodo` 启动。细则见 `.claude/rules/coding-principle.md`。

## Verification

代码复审、完成工作确认、事实确认，尽可能用 jev 判定服务而非自己逐一去看：把已知事实整理成 state，把问题整理成一批类型化判定（真/假、选项、分级）一次提交，按带置信度的结论行动。低置信度或 escalate 的问题自己判；jev 结论是判定辅助，不是授权边界；精确规则和算术用代码。细则见 `.claude/rules/verification.md`。
