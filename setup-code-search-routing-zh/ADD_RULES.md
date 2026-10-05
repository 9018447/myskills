# Code Search & Navigation Rules

Use the following routing policy for repository search and code navigation. Prefer the most specialized tool for the task instead of defaulting to generic grep/find commands.

## Default routing

| Intent | Preferred tool |
|---|---|
| Find files by name, extension, or path | `rg --files` |
| Exact text, literal, regex, exhaustive content search | `zg --rg` |
| General code search with unclear naming | `zg` |
| Semantic / intent-based search | `zg` |
| Lexical / BM25 ranked search | `zg` |
| AST or syntax-structure matching | `ast-grep` |
| Definition / references / implementations | LSP |
| Symbol type / hover / document symbols | LSP |
| Call graph / dependency graph / multi-hop relations | `GitNexus` |
| Change impact / dependency impact analysis | `GitNexus` |
| Cross-symbol architectural exploration | `GitNexus` |

## Search policy

Use `zg` as the default repository content search engine.

Use `zg --rg` when the query contains an exact identifier, string, error message, regex, or other pattern that requires exhaustive matching.

Use `rg --files` for file discovery. Do not use semantic search when only filenames or paths are needed.

Use `ast-grep` when the request depends on source-code structure rather than text, including function-call shapes, AST patterns, syntax-aware matching, or structural refactoring candidates.

Use LSP for precise compiler/language-server knowledge such as definitions, references, implementations, symbol lookup, types, hover information, and local call hierarchy.

Use `GitNexus` when the task requires graph-level reasoning across symbols, modules, or files, including multi-hop call chains, dependency relationships, architecture exploration, and change-impact analysis.

## Escalation strategy

For ambiguous code questions, start with:

`zg → LSP/GitNexus → zg --rg verification`

Typical flow:

`zg`
→ locate likely files and symbols  
→ `LSP` for precise symbol navigation, or `GitNexus` for graph relationships  
→ `zg --rg` to verify exact source occurrences  
→ `Read` the relevant source ranges

For structural queries:

`ast-grep`
→ identify structural matches  
→ `LSP` or `GitNexus` when relationships must be expanded  
→ `Read` the final source

## Avoid redundant tools

Do not use built-in `Grep` or `Glob` when the equivalent search can be performed by this routing layer.

Avoid shell `grep`, `find`, `git grep`, or standalone `rg` for normal repository retrieval when the preferred tool above covers the task.

Exceptions are allowed when shell composition, filesystem metadata, scripting, or another capability unavailable through the search tools is specifically required.

Do not replace `Read` with search tools. Search tools locate code; `Read` retrieves the final source context.

## Tool boundaries

`rg --files` = file discovery  
`zg` = default lexical + semantic repository retrieval  
`zg --rg` = exhaustive exact text / regex search  
`ast-grep` = syntax and AST structure  
`LSP` = precise language-level symbol navigation  
`GitNexus` = graph relationships, architecture, and impact analysis  
`Read` = final source inspection

When several tools could answer the question, choose the narrowest specialized tool first. Escalate to more expensive graph or semantic operations only when they provide additional information.
