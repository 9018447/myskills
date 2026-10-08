---
name: gitnexus-refactoring
description: "Use when the user wants to rename, extract, split, move, or restructure code safely. Examples: \"Rename this function\", \"Extract this into a module\", \"Refactor this class\", \"Move this to a separate file\""
---

# Refactoring with GitNexus

**Use the CLI for analysis; there is no CLI `rename`.** The GitNexus MCP
server is often not mounted (multiple sessions have hit
`Server "gitnexus" not found`), and `rename` exists only as an MCP tool — if
the server is not mounted, do the rename by hand (see *Manual rename* below).
All analysis commands below work through plain Bash from the repo root:
`node .gitnexus/run.cjs <command>`. If `.gitnexus/run.cjs` is missing,
bootstrap with `bunx gitnexus@latest analyze`.

## Bind the repository first

Refactoring writes to disk, so binding identity here is a safety gate, not
bookkeeping.

Multiple repositories are indexed on this machine (verified via `list`), so
**pass `--repo <name>` on every command** — usually `--repo .` for the repo
you are in. Never rely on a default. If you cannot tell which repository is
meant, stop and ask.

`--repo .` means the current checkout; pass the intended repository path
instead when you are not standing in it. A wrong-checkout diff reports zero
changed symbols, which reads as a verified refactor when it is nothing of the
sort. Confirm the diffed checkout is the one you edited.

```
node .gitnexus/run.cjs list              # all indexed repos + stats
node .gitnexus/run.cjs status --repo .   # index freshness, indexed commit
```

A stale index maps old symbols, so re-index before planning:
`node .gitnexus/run.cjs analyze --index-only`.

## Workflow

```
0. status --repo .                                → bind repo, check staleness
1. impact "X" -d upstream --repo .                 → map all dependents
2. query "X" --repo .                              → find execution flows involving X
3. context X --repo .                              → see all incoming/outgoing refs
4. Plan update order: interfaces → implementations → callers → tests
5. Apply edits (CLI rename does not exist — manual or MCP)
6. detect-changes --scope all --repo .             → verify affected scope
7. Run tests for affected processes
```

## Checklists

### Rename Symbol

```
- [ ] status --repo . — bind repo; confirm index fresh
- [ ] impact "oldName" -d upstream --repo . — map all callers
- [ ] context oldName --repo . — see all incoming/outgoing refs
- [ ] MCP rename with dry_run: true if server is mounted; review previewed
      file paths are in the bound repository before applying
- [ ] Otherwise: manual edit — never find-and-replace blindly; query/grep
      for string/dynamic references the index cannot see
- [ ] detect-changes --scope all --repo . — verify only expected files changed
- [ ] Run tests for affected processes
```

### Extract Module

```
- [ ] status --repo . — bind repo; confirm index fresh
- [ ] context <target> --repo . — see all incoming/outgoing refs
- [ ] impact "<target>" -d upstream --repo . — find all external callers
- [ ] Define new module interface
- [ ] Extract code, update imports
- [ ] detect-changes --scope all --repo . — verify affected scope
- [ ] Run tests for affected processes
```

### Split Function/Service

```
- [ ] status --repo . — bind repo; confirm index fresh
- [ ] context <target> --repo . — understand all callees
- [ ] Group callees by responsibility
- [ ] impact "<target>" -d upstream --repo . — map callers to update
- [ ] Create new functions/services
- [ ] Update callers
- [ ] detect-changes --scope all --repo . — verify affected scope
- [ ] Run tests for affected processes
```

## Commands

**impact** — map all dependents first:

```bash
node .gitnexus/run.cjs impact validateUser -d upstream --repo .
# → d=1: loginHandler, apiMiddleware, testUtils
#   Affected Processes: LoginFlow, TokenRefresh
```

**context** — see all incoming/outgoing refs:

```bash
node .gitnexus/run.cjs context validateUser --repo .
# -f <path> disambiguates common names
```

**detect-changes** — verify your changes after refactoring (alias
`detect_changes`):

```bash
node .gitnexus/run.cjs detect-changes --scope all --repo .
# → Changed: 8 files, 12 symbols
#   Affected processes: LoginFlow, TokenRefresh
#   Risk: MEDIUM
```

`partial: true` (a graph query failed) or `truncated: true` (the changed-symbol
listing was capped) means the result is short of the truth: a short or empty
list is not proof that only the expected files changed. Re-run it rather than
treat the refactor as verified.

A wrong-checkout zero carries neither flag and is indistinguishable from a
clean verification, so confirm the diffed checkout is the one you edited.

**cypher** — custom reference queries:

```bash
node .gitnexus/run.cjs cypher 'MATCH (caller)-[:CodeRelation {type: "CALLS"}]->(f:Function {name: "validateUser"}) RETURN caller.name, caller.filePath ORDER BY caller.filePath' --repo .
```

## Manual rename (no MCP `rename` available)

The CLI has no `rename` command. Without the MCP server:

1. `impact "oldName" -d upstream --repo .` and `context oldName --repo .` —
   enumerate every caller and reference the graph can see.
2. grep for string/dynamic references the index cannot see (property access,
   dispatch tables, serialization names, docs).
3. Edit each site by hand; update interfaces → implementations → callers → tests.
4. `detect-changes --scope all --repo .` — verify only expected files changed.
5. Run tests for affected processes.

## Risk Rules

| Risk Factor         | Mitigation                                |
| ------------------- | ----------------------------------------- |
| Many callers (>5)   | Work interface → implementation → caller → test; verify with detect-changes |
| Cross-area refs     | detect-changes after to verify scope      |
| String/dynamic refs | query + grep to find them                 |
| External/public API | Version and deprecate properly            |
| Same name in another indexed repo | Bind `--repo`; verify diffed checkout before concluding |
