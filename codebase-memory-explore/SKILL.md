---
name: codebase-memory-explore
description: Answer structural codebase questions with codebase-memory-mcp graph queries instead of grep/glob file sweeps or explore/scout subagents. Covers finding functions/classes/routes, who calls X and what X calls, dead code, high fan-in/fan-out, change impact and blast radius, cross-service call paths, architecture overview, and index health/coverage — all via the `codebase-memory-mcp cli` subcommand from the shell. Use this BEFORE reaching for Grep, Glob, search tools, or spawning an exploration subagent whenever the repo may be indexed and the question is about code structure rather than literal text. Also use for scripts/CI/cron that need index checks, and whenever graph queries are needed but no MCP tools are mounted. Do NOT use for plain literal-text search or for in-session MCP tool calls (the codebase-memory skill covers those).
---

# Codebase Memory Explore — graph before grep

For structural questions about an indexed repository, query the code graph instead of grepping, globbing, or spawning an exploration subagent. A graph query returns exact symbols, files, and call chains in a few hundred tokens; a grep sweep over an unfamiliar repo burns tens of thousands and still misses callers hidden behind re-exports, interface implementations, and route registrations. Treat this as the default first move for "how does this codebase work" questions; fall back to text tools only for what the graph can't see.

**Graph answers these; grep answers literal text.** Error-message strings, config values, comments, docs, and anything in an unindexed directory still belong to grep/read.

Check the binary with `codebase-memory-mcp --version` (commonly `~/.local/bin/`).

## Question → query

| Question | Command |
|---|---|
| Which functions/classes match a name or concept? | `search_graph --query '...'` (BM25) or `--name-pattern '...'` |
| Who calls X? What does X call? | `trace_path --function-name X --direction both` |
| Is X dead code? | `search_graph --max-degree 0 --exclude-entry-points true` |
| Complexity hotspots (fan-in/out)? | `search_graph --min-degree 10 --relationship CALLS --direction outbound` |
| What do my uncommitted changes affect? | `detect_changes` (git diff → blast radius) |
| Project layout / entry points / deps? | `get_architecture --project <name>` |
| Is this file fully indexed? | `check_index_coverage --paths <file>` |
| Ad-hoc structural pattern? | `query_graph` (Cypher — always end with `LIMIT`) |

## Setup: is the repo indexed?

`--project` takes the derived project name from `list_projects` (`/home/smh/lsr` → `home-smh-lsr`), never the filesystem path:

```bash
codebase-memory-mcp cli list_projects
codebase-memory-mcp cli index_status --project home-smh-lsr
```

`index_status` reports node/edge counts, readiness, and `parse_partial` files — line ranges the indexer couldn't fully parse. Don't make exhaustive claims over those; fall back to reading the flagged ranges.

Not indexed yet, or stale after big changes:

```bash
codebase-memory-mcp cli index_repository --repo-path /abs/path/to/repo --mode fast --progress
```

`--mode`: `fast` (no similarity/semantic edges), `moderate`, `full`, `cross-repo-intelligence`. Long task — `--progress` shows progress. `--persistence true` writes a shareable artifact to `.codebase-memory/`.

## Passing arguments — always flags

```bash
codebase-memory-mcp cli <tool> --flag value --flag2 value2      # preferred
codebase-memory-mcp cli <tool> --args-file args.json
echo '{"project":"x"}' | codebase-memory-mcp cli <tool>          # piped stdin JSON
codebase-memory-mcp cli <tool> '{"project":"x"}'                # DEPRECATED — will be removed
```

Raw JSON positional args print a deprecation warning and will break in a future release — never write them into scripts. Flag names use dashes (`--name-pattern`). Array flags accept **repeated single values** (`--paths a.ts --paths b.ts`); passing a JSON array string as one flag value does NOT parse — use repeated flags or stdin JSON for arrays.

Every tool documents its flags via `cli <tool> --help` — but the listing can be incomplete: `get_code_snippet --help` shows only `--qualified-name`, while `--project` is also required. When a call fails with a "missing required argument" or "project not found" error, trust the error hint over the help listing.

## Reading output

- **Default**: human-readable tree/table with `total:`, `has_more:`, rank columns — good for eyeballing and grepping.
- **`--json`**: MCP envelope `{"content":[...],"structuredContent":{...},"isError":bool}` — for scripting, extract `jq '.structuredContent'` (note: `content[0].text` is human-readable text, not the payload).
- Diagnostics (`level=info ...`) go to **stderr**; stdout is clean. `2>/dev/null` in pipelines.
- Exit codes: `0` success, `1` tool error (missing/unknown project, bad args). Errors return `{"error":"...","hint":"..."}` — the hint names the fix.
- **Caution**: a successful coverage/status query exits 0 even when it reports problems. Branch on the JSON fields, never on the exit code alone.

## Query recipes

**Find symbols** (project name required):

```bash
codebase-memory-mcp cli search_graph --project home-smh-lsr --name-pattern '.*staging.*' --label Function
codebase-memory-mcp cli search_graph --project home-smh-lsr --query 'staging conflict' --detail ids   # BM25, camelCase-aware
```

BM25 mode (`--query`) ignores `--label` — post-filter with `grep ' Function '` or jq. `--detail ids` returns bare qualified names, cheapest for wide sweeps. Paginate with `--offset`/`--limit` while `has_more: true`.

**Read source** — BOTH flags required (qn embeds the project but `--project` is still mandatory in 0.10.8):

```bash
codebase-memory-mcp cli get_code_snippet --project home-smh-lsr \
  --qualified-name home-smh-lsr.src.lib.staging.evaluateStagingConflict
```

**Trace / impact:**

```bash
codebase-memory-mcp cli trace_path --project home-smh-lsr --function-name applyEditStaging --direction both --depth 3
codebase-memory-mcp cli detect_changes --project home-smh-lsr
```

`trace_path` needs exact names — `search_graph` first. `--direction outbound` misses cross-service callers; use `both`. `--mode cross_service` follows HTTP/async edges through Routes into other services.

**Coverage gates** (CI-friendly — judge by status fields, not exit code):

```bash
codebase-memory-mcp cli check_index_coverage --project home-smh-lsr --paths src/lib/staging.ts --json
```

Requires `--paths` or `--scopes` (`.` = repo root). Per-path verdicts: `status` ∈ `no_recorded_issue | partial | excluded`; `freshness` ∈ `metadata_match | not_tracked | missing`. Coverage entry kinds: `parse_partial` (with line ranges), `not_indexed_file`, `not_indexed_dir`. A nonexistent path comes back `no_recorded_issue + missing` — pre-validate existence locally if that matters. The signal is best-effort: clean ≠ proof of completeness.

**Raw Cypher:**

```bash
codebase-memory-mcp cli query_graph --project home-smh-lsr --query 'MATCH (f:Function) WHERE f.name =~ ".*staging.*" RETURN f.name LIMIT 20'
```

Always `LIMIT` — 100k row ceiling.

## Management

```bash
codebase-memory-mcp config list                 # keys: auto_index auto_index_limit auto_watch ui-lang ui_enabled ui_port
codebase-memory-mcp config get ui_port          # prints just the value
codebase-memory-mcp config set auto_index true
codebase-memory-mcp config reset
codebase-memory-mcp --ui=true --port=9749       # HTTP graph visualization (persisted)
codebase-memory-mcp install --dry-run           # register into 40+ client surfaces; preview first
codebase-memory-mcp update
```

## CLI vs MCP tools

Interactive session with MCP tools mounted → prefer MCP tools (see the codebase-memory skill). Prefer the CLI in scripts, CI/cron, shell loops over many queries, or when no MCP tools are available but the binary is.
