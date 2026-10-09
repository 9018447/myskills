# Code Search & Navigation Rules

Use the most specialized tool for the task instead of defaulting to shell `grep`/`find` or built-in `Grep`/`Glob`. This file is the routing layer only — tool mechanics live in the skills: `jevgrep` (jg), the `gitnexus-*` family (GitNexus).

## Default routing

| Intent | Preferred tool |
| --- | --- |
| Find files by name, extension, or path | `rg --files` |
| Content search, wording or location unknown | `jg` (jevgrep) |
| Lexical / BM25 ranked search over a local index | `zg` |
| Exact text, literal, regex, exhaustive matching | `zg --rg` |
| AST / syntax-structure matching | `ast-grep` |
| Definitions / references / types / hover / call hierarchy | LSP |
| Call graph / dependency graph / multi-hop / impact analysis | `GitNexus` |

## Retrieval order (hard rule)

Content retrieval escalates in one fixed order:

**`jg` → `zg` / `ast-grep` / `GitNexus` / LSP → `rg`**

1. **`jg` (jevgrep) is the first stop** for content search: a natural-language question returns a relevant-file list with declaration locations. Follow up with `Read` on the listed ranges.
2. **Second tier: `zg`, `ast-grep`, `GitNexus`, LSP.** `zg` when `jg` is unavailable (auth/quota/network) or a local index is exactly what is needed — if its index is stale, rebuild it rather than degrade to plain `rg`; `zg --rg` for exact/exhaustive matching; `ast-grep` for source-structure questions; LSP for symbol navigation; `GitNexus` for graph-level questions. Usage details: the `jevgrep` and `gitnexus-*` skills.
3. **`rg` (and shell `grep`/`find`, built-in `Grep`/`Glob`) come last.** Legitimate uses: file discovery (`rg --files`), shell composition / filesystem metadata / scripting the tools above cannot do, or when the routing tools are unavailable — state the reason on the spot. Do not fall back out of habit.

## Escalation flows

Ambiguous code question: `jg` (file list + locations) → `LSP` / `GitNexus` (relationships) → `zg --rg` (verify exact occurrences) → `Read` the source ranges.

Structural query: `ast-grep` → `LSP` / `GitNexus` (expand relationships) → `Read` the final source.

## Web retrieval

| Intent | Preferred tool |
| --- | --- |
| Web search | `WebSearch`; unavailable or poor results → `meta-search` (metaso) |
| Fetch page content | `WebFetch`; blocked (anti-crawl, JS-rendered, WeChat articles) → `meta-fetch` (metaso reader) |
| Quick networked answer / second opinion | `meta-ask` (metaso chat) |

Meta skills run their work as `curl` and return long raw output (result JSON, full article text, SSE stream) — **always trigger them through context-mode**, never as a bare Bash call: run the skill's curl inside `ctx_batch_execute` (with `queries` so matched sections come back inline) or `ctx_execute`, so the raw output is indexed and only the matched windows enter the conversation. For plain page fetches, prefer `ctx_fetch_and_index` outright — it caches and indexes without any curl.

## Avoid redundant tools

Do not use built-in `Grep` or `Glob` when the equivalent search is covered by this routing layer. Do not replace `Read` with search tools — search locates code; `Read` retrieves the final source.

## Tool boundaries

`rg --files` = file discovery · `jg` = first-stop semantic retrieval · `zg` = fallback lexical + semantic index · `zg --rg` = exhaustive exact text / regex · `ast-grep` = syntax and AST structure · LSP = precise language-level symbol navigation · `GitNexus` = graph relationships, architecture, impact · `Read` = final source inspection.

## GitNexus in git worktrees

A git worktree has no `.gitnexus/` folder (the index is not tracked by git), so the relative launcher `node .gitnexus/run.cjs` fails there. That does not make GitNexus unusable in a worktree (tested 2026-10-09):

- Invoke the launcher by its absolute path in the main checkout and point `--repo` at the main checkout's absolute path: `node <main-checkout>/.gitnexus/run.cjs impact|query|trace|context <target> --repo <main-checkout>`.
- The graph answers as of the **indexed commit of the main checkout**: merged code is in the graph; the worktree's uncommitted or new code is not, and the index may lag `main`. Before editing, verify graph-derived facts against the worktree source with `Read`.
- Do not degrade to shell `grep`/`find` just because you are in a worktree — the routing layer above still applies, with the `--repo` workaround for GitNexus.

## Missing skills

The skills referenced above (`jevgrep`) are distributed from https://github.com/9018447/myskills. If one is not installed on this machine, fetch it from that repo — do not improvise around the gap. GitNexus itself is the CLI (`node .gitnexus/run.cjs`), not a skill; nothing to fetch for it.
