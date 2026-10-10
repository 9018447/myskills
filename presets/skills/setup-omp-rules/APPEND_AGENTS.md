## Tool Routing

Use specialized search tools instead of shell `find`/`grep`/`rg`.

- File discovery: `glob`; content search first stop: `jg`; second tier: `zg` / `ast-grep` / `GitNexus` / `xd://lsp`; unknown owner: `find` first; literal/regex: `grep`; shell `rg` last — state the reason on the spot.
- Web fetch: `read`; JS-rendered pages: `browser`; otherwise meta-search/meta-fetch/meta-ask, batched in `eval` so raw output stays out of context.

@{{CTX}}/code-search.md

## Division of Labor

omp (the main agent) writes documents, orchestrates tasks, and holds the global picture. Route cross-file work, signature changes, design choices, and unknown-cause bugs through plan mode with `task` dispatch (read-only `scout` first); contained single-file changes with an obvious test are done directly. Delete this section to turn the standing routing off.

@{{CTX}}/coding-labor.md

## Verification

For code review, done-work confirmation, and fact-checking, use the jev judgment service instead of reading everything yourself: assemble evidence into `state`, batch independent questions into one request, and judge low-confidence or escalated conclusions yourself. jev's conclusions are decision aids, not authorization boundaries; exact rules and arithmetic go to code.

@{{CTX}}/verification.md

## Work Principles

Universal work principles: subtract before you add, test behavior not implementation, accept only with evidence (prove-it-works), fix root causes not symptoms, after two failures of the same fix re-examine the shared premise, encode lessons in structure not memory. Context is a budget — batch tool chains in one `eval` script.

@{{CTX}}/work-principles.md

Missing skills: the skills referenced in these sections come from https://github.com/9018447/myskills — if one is not installed on this machine, fetch it from there.
