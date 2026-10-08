## Tool Routing

Use specialized code search tools instead of shell `grep`/`find` or built-in `Grep`/`Glob`.

- File discovery: `rg --files`
- Content search, first stop: `jg` (jevgrep — natural-language question → relevant-file list + declaration locations; auth `jg auth`, health `jg doctor`)
- Second tier: `zg` (fallback local index; `zg --rg` for exact/exhaustive text; missing/stale index → rebuild with `zg index`) · `ast-grep` (structure) · `GitNexus` (call chains, dependencies, impact) · LSP (symbols)
- Last resort: `rg` / `grep` — only for declared exceptions (shell composition, filesystem metadata, scripting) or when the tools above cannot cover the task; state the reason on the spot.

Retrieval order: `jg → zg / ast-grep / GitNexus → rg`. After locating code, `Read` the exact source before concluding or editing. Full policy: `.claude/rules/code-search.md`.

## Division of Labor

Claude Code (the main agent) writes documents, orchestrates tasks, and holds the global picture. Coding: trivial and single-file changes are done by the main agent directly; cross-file implementation always enters through `/poteto-mode` — the dispatch chain and the single-agent vs concurrent choice live inside that skill, and the main agent never codes across files itself. Details: `.claude/rules/coding-principle.md`.

## Verification

For code review, done-work confirmation, and fact-checking, use the jev judgment service (the `jev` skill) instead of reading everything yourself: assemble evidence into `state`, batch independent questions into one request, and judge low-confidence or escalated conclusions yourself. jev's conclusions are decision aids, not authorization boundaries; exact rules and arithmetic go to code. Details: `.claude/rules/verification.md`.

## Work Principles

Universal work principles: subtract before you add, test behavior not implementation, accept only with evidence (prove-it-works), fix root causes not symptoms, after two failures of the same fix re-examine the shared premise, encode lessons in structure not memory. Details: `.claude/rules/work-principles.md`.
