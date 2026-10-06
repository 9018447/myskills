---
name: gitnexus-guide
description: "Use when the user asks about GitNexus itself — available tools, how to query the knowledge graph, MCP resources, graph schema, or workflow reference. Examples: \"What GitNexus tools are available?\", \"How do I use GitNexus?\""
---

# GitNexus Guide

Quick reference for the GitNexus CLI commands, the knowledge graph schema, and
which capabilities are CLI vs MCP-only.

**Always use the CLI.** The GitNexus MCP server is often not mounted
(multiple sessions have hit `Server "gitnexus" not found`). Run commands from
the repo root: `node .gitnexus/run.cjs <command>`. If `.gitnexus/run.cjs` is
missing, bootstrap with `bunx gitnexus@latest analyze`.

## Always Start Here

For any task involving code understanding, debugging, impact analysis, or refactoring:

1. **Check index freshness**: `node .gitnexus/run.cjs status --repo .` — stale
   (indexed commit ≠ HEAD) → re-index with `analyze --index-only`
2. **Match your task to a skill below** and **read that skill file**
3. **Follow the skill's workflow and checklist**

## Skills

| Task                                         | Skill to read       |
| -------------------------------------------- | ------------------- |
| Understand architecture / "How does X work?" | `gitnexus-exploring`         |
| Blast radius / "What breaks if I change X?"  | `gitnexus-impact-analysis`   |
| Trace bugs / "Why is X failing?"             | `gitnexus-debugging`         |
| Rename / extract / split / refactor          | `gitnexus-refactoring`       |
| Tools, schema, CLI vs MCP reference          | `gitnexus-guide` (this file) |
| Index, status, clean, wiki CLI commands      | `gitnexus-cli`               |

## CLI Commands (primary path)

Multiple repositories are indexed on this machine — **pass `--repo <name>` on
every command** (usually `--repo .`).

| Command | What it gives you |
| ------- | ----------------- |
| `list`  | All indexed repos + stats (files, symbols, edges, clusters, processes) |
| `status -r .` | Index freshness, indexed commit for the current repo |
| `query "<concept>" -r .` | Execution flows related to a concept, symbols grouped by flow |
| `context <symbol> -r .` | 360° symbol view: callers, callees, member processes |
| `impact "<symbol>" -d upstream -r .` | Blast radius at depth 1/2/3 with confidence |
| `trace <from> <to> -r .` | Shortest call path between two symbols |
| `detect-changes --scope all -r .` | Map git diff hunks to indexed symbols + affected flows |
| `cypher "<query>" -r .` | Raw graph queries |
| `check -r .` | Graph invariant checks (e.g. circular imports) |
| `analyze [--index-only] [path]` | (Re-)index the repo |
| `wiki [path]` | Generate a repo wiki from the graph |
| `clean` | Delete the current repo's index |

Shared disambiguation flags on `query`/`context`/`impact`: `-f <path>` (file
path for common names), `-u <uid>` (zero-ambiguity), `--include-tests`,
`-l <n>` (result cap). `detect-changes` scopes: `unstaged` (default),
`staged`, `all`, `compare --base-ref main`.

## MCP-Only Capabilities

These exist only as MCP tools — usable when the server is mounted, otherwise
substitute the manual equivalent:

| MCP tool | Manual substitute |
| -------- | ----------------- |
| `rename` | `impact` + `context` to enumerate refs, grep for dynamic refs, edit by hand — see `gitnexus-refactoring` |
| `explain` (taint findings) | Needs `analyze --pdg` index; review source manually |
| `pdg_query` (CDG / reaching-def) | Needs `analyze --pdg` index; queryable edges are also reachable via `cypher` |
| `route_map`, `shape_check`, `api_impact`, `tool_map` | No CLI equivalent — grep routes/handlers |
| `group_list`, `group_sync` | Edit `group.yaml` directly, then re-index members |
| `list_repos` (paginated) | `list` (prints everything) |

## Graph Schema

**Nodes:** File, Folder, Function, Class, Interface, Method, CodeElement, Community, Process, Route, Tool, plus language-specific types (Struct, Enum, Trait, Impl, Namespace, Module, …) and BasicBlock (`--pdg` indexes only).
**Edges (via CodeRelation.type):** CALLS, IMPORTS, EXTENDS, IMPLEMENTS, DEFINES, CONTAINS, MEMBER_OF, HAS_METHOD, HAS_PROPERTY, ACCESSES, METHOD_OVERRIDES, METHOD_IMPLEMENTS, STEP_IN_PROCESS, HANDLES_ROUTE, FETCHES, HANDLES_TOOL, ENTRY_POINT_OF, WRAPS, QUERIES, INJECTS, plus `--pdg`-only types (CFG, REACHING_DEF, TAINTED, SANITIZES, TAINT_PATH, CDG — zero rows on a default index).

Read the schema before writing Cypher (MCP resource
`gitnexus://repo/{name}/schema`); the node/edge lists above cover the common
cases.

```bash
node .gitnexus/run.cjs cypher 'MATCH (caller)-[:CodeRelation {type: "CALLS"}]->(f:Function {name: "myFunc"}) RETURN caller.name, caller.filePath' --repo .
```
