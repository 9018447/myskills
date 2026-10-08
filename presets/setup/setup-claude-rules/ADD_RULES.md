# Code Search & Navigation Rules

Use the following routing policy for repository search and code navigation. Prefer the most specialized tool for the task instead of defaulting to generic grep/find commands.

## Default routing

| Intent | Preferred tool |
|---|---|
| Find files by name, extension, or path | `rg --files` |
| Exact text, literal, regex, exhaustive content search | `zg --rg` |
| General code search with unclear naming | `jg` |
| Semantic / intent-based search | `jg` |
| Lexical / BM25 ranked search | `zg` |
| AST or syntax-structure matching | `ast-grep` |
| Definition / references / implementations | LSP |
| Symbol type / hover / document symbols | LSP |
| Call graph / dependency graph / multi-hop relations | `GitNexus` |
| Change impact / dependency impact analysis | `GitNexus` |
| Cross-symbol architectural exploration | `GitNexus` |

## Search policy

Use `jg` as the first stop for content search with uncertain wording. `jg "natural-language question" [root]` is a semantic source retriever backed by the Jev service (OpenRouter; verify with `jg doctor`, auth via `jg auth`). It needs no local index — it scans on demand and returns a relevant-file list with declaration locations (`file@start-end`) plus role hints; follow up with `Read` on the listed files. Retrieval order across tools: `jg → GitNexus → zg`, and prefer these over native `grep`/`find`/built-in `Grep`/`Glob` wherever one fits.

`zg` is the fallback content search when `jg` is unavailable (auth/quota/network) or when lexical/BM25 ranking over a local index is specifically what the task needs. It is semantic retrieval backed by an embedding index, so it also tolerates paraphrase. `zg --rg` is a separate exact-text engine, not a substitute for conceptual queries.

`zg` owns its repository index. If `zg status` reports the index missing or stale, rebuild with `zg index` instead of silently falling back to plain `rg` — a fresh semantic index is what `zg` queries depend on.

Use `zg --rg` when the query contains an exact identifier, string, error message, regex, or other pattern that requires exhaustive matching.

Use `rg --files` for file discovery. Do not use semantic search when only filenames or paths are needed.

Use `ast-grep` when the request depends on source-code structure rather than text, including function-call shapes, AST patterns, syntax-aware matching, or structural refactoring candidates.

Use LSP for precise compiler/language-server knowledge such as definitions, references, implementations, symbol lookup, types, hover information, and local call hierarchy.

Use `GitNexus` when the task requires graph-level reasoning across symbols, modules, or files, including multi-hop call chains, dependency relationships, architecture exploration, and change-impact analysis.

## Escalation strategy

For ambiguous code questions, start with:

`jg → LSP/GitNexus → zg --rg verification`

Typical flow:

`jg`
→ ask the question in natural language, get file list + declaration locations  
→ `LSP` for precise symbol navigation, or `GitNexus` for graph relationships  
→ `zg --rg` to verify exact source occurrences  
→ `Read` the relevant source ranges

For structural queries:

`ast-grep`
→ identify structural matches  
→ `LSP` or `GitNexus` when relationships must be expanded  
→ `Read` the final source

## GitNexus usage

GitNexus answers graph-level questions: call chains, execution flows, change impact, and architecture. **Always use the CLI, not the MCP server** — the server is often not mounted (sessions frequently hit `Server "gitnexus" not found`). Run from the repo root: `node .gitnexus/run.cjs <command> --repo .`, always passing `--repo .` (or the intended repo path); never rely on a default binding when multiple repos are indexed.

Before trusting a graph result, confirm the index is fresh with `node .gitnexus/run.cjs status --repo .`; if it reports stale (indexed commit ≠ HEAD), re-index with `node .gitnexus/run.cjs analyze --index-only` before continuing.

The index lives in the main checkout only (`.gitnexus/` is untracked, so it does not exist in linked worktrees — the runner fails there with `MODULE_NOT_FOUND`). When working in a git worktree or an agent-only branch, GitNexus is simply unavailable: fall back to `zg`/LSP for graph questions, and treat the recurring "index stale" notice as noise — commits on those branches never enter the graph, so neither chasing the notice nor re-indexing helps.

| Question | Command |
|---|---|
| Execution flows for a concept | `query "<concept>" --repo .` (`-l` caps results) |
| Callers / callees of a symbol | `context <symbol> --repo .` (`-f <path>` disambiguates common names) |
| Shortest call path between two symbols | `trace <from> <to> --repo .` |
| Change blast radius | `impact <symbol> -d upstream --repo .` |
| Pre-commit change impact | `detect-changes --scope all --repo .` |
| Custom call-chain trace | `cypher '<pattern>' --repo .` |

Expanding `impact -d upstream`: d=1 direct dependents **WILL BREAK** (review first), d=2 **LIKELY AFFECTED**, d=3 transitive. `impact`'s risk is the edit gate: warn on HIGH/CRITICAL, stop on UNKNOWN — an empty caller set is not LOW, it means the walk could not answer (property access, dynamic dispatch, cross-language calls). Confirm with `zg --rg` before treating a symbol as safe to change or delete.

An empty `query` / `context` / `impact` result does not mean the symbol is unused — the index may not resolve it. Fall back to `zg --rg` text search before concluding.

## Avoid redundant tools

Do not use built-in `Grep` or `Glob` when the equivalent search can be performed by this routing layer.

Avoid shell `grep`, `find`, `git grep`, or standalone `rg` for normal repository retrieval when the preferred tool above covers the task.

Exceptions are allowed when shell composition, filesystem metadata, scripting, or another capability unavailable through the search tools is specifically required.

Do not replace `Read` with search tools. Search tools locate code; `Read` retrieves the final source context.

## Tool boundaries

`rg --files` = file discovery  
`jg` = first-stop semantic retrieval, natural-language question → file list + declaration locations (no local index, needs auth)  
`zg` = fallback lexical + semantic repository retrieval (local embedding index)  
`zg --rg` = exhaustive exact text / regex search  
`ast-grep` = syntax and AST structure  
`LSP` = precise language-level symbol navigation  
`GitNexus` = graph relationships, architecture, and impact analysis  
`Read` = final source inspection

When several tools could answer the question, choose the narrowest specialized tool first. Escalate to more expensive graph or semantic operations only when they provide additional information.

## Compliance（迭代记录）

1. **2026-10-07 — 纠正路由倒退**：实际执行中观察到，agent 很少使用 `zg` 和 `GitNexus`，仍然退回 shell `grep`/`find`，`ast-grep` 更是从未用上。自本条起，上面的路由表按硬约束执行，不是偏好：

   - 内容搜索的第一选择必须是 `zg`（语义、概念、措辞不确定的查询）或 `zg --rg`（精确标识符、错误消息、正则）。shell `grep`、`find`、内置 `Grep`/`Glob` 只在两种情况下允许：路由表已声明的例外（shell 组合、文件系统元数据、脚本化需求），或所选路由工具不可用且当场说明原因。
   - `rg` 用于 `rg --files` 文件发现；内容层面的精确匹配走 `zg --rg`，不要用 `rg` 内容扫描替代。
   - 按语法结构找代码（调用形态、AST 模式、结构化重构候选）必须用 `ast-grep`，不要用文本匹配凑合。
   - 涉及调用链、依赖关系、多跳关系、变更影响面的问题必须用 `GitNexus`；它返回空结果时先用 `zg --rg` 复核再下结论，因为索引可能没有解析到该符号。

2. **2026-10-08 — jg 升为语义检索第一选择**：引入 `jg`（Jevgrep，Jev/OpenRouter 后端的语义源码检索 CLI，auth 已配置，`jg doctor` 可验证）。自本条起：

   - 措辞不确定的内容检索第一选择是 `jg "自然语言问题" [root]`；它返回相关文件清单 + 声明位置，随后 `Read` 精读。整条检索链为 `jg → GitNexus → zg`。
   - `zg` 降为 jg 不可用（auth/配额/网络）或明确需要本地索引 BM25 排序时的备选；`zg --rg` 的精确/穷举匹配职责不变。
   - 原生 `grep`/`find`、内置 `Grep`/`Glob` 的限制维持第 1 条不变：jg/zg/GitNexus 能覆盖时不得退回。
