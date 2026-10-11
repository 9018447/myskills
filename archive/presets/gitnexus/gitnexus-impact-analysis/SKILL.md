---
name: gitnexus-impact-analysis
description: "Use when the user wants to know what will break if they change something, or needs safety analysis before editing code. Examples: \"Is it safe to change X?\", \"What depends on this?\", \"What will break?\""
---

# Impact Analysis with GitNexus

**Always use the CLI.** The GitNexus MCP server is often not mounted
(multiple sessions have hit `Server "gitnexus" not found`); every command below
works through plain Bash. Run everything from the repo root:
`node .gitnexus/run.cjs <command>`. If `.gitnexus/run.cjs` is missing,
bootstrap with `bunx gitnexus@latest analyze`.

## Bind the repository first

Impact analysis is the gate that authorizes an edit, so it must answer for the
repository you are about to edit.

Multiple repositories are indexed on this machine (verified via `list`), so
**pass `--repo <name>` on every command** — usually `--repo .` for the repo
you are in. Never rely on a default. If you cannot tell which repository is
meant, stop and ask — every result below an ambiguous identity inherits the
ambiguity.

`--repo .` means the current checkout; pass the intended repository path
instead when you are not standing in it. A wrong-checkout diff reports zero
changed symbols — a false clean check. Confirm the checkout you edited is the
checkout that was diffed.

State the bound identity with your risk report:

```
Repository: <name> (<path>)   Index: <commit>, <n> behind HEAD
```

## Workflow

```
0. node .gitnexus/run.cjs status --repo .                      → bind repo, check staleness
1. node .gitnexus/run.cjs impact "X" -d upstream --repo .       → find dependents
2. node .gitnexus/run.cjs detect-changes --scope all --repo .   → pre-commit check (step 3 below)
3. Assess risk and report to user, echoing repo/index identity
```

> If the index is stale (indexed commit ≠ HEAD) → re-index:
> `node .gitnexus/run.cjs analyze --index-only`.

## Checklist

```
- [ ] status — bind repo; confirm index fresh (re-index if stale)
- [ ] impact -d upstream to find dependents
- [ ] Review d=1 items first (these WILL BREAK)
- [ ] Check high-confidence (>0.8) dependencies
- [ ] detect-changes --scope all for pre-commit check
- [ ] Confirm the checkout you edited is the checkout that was diffed
- [ ] Assess risk level and report, stating repo/index identity
```

## Understanding Output

| Depth | Risk Level       | Meaning                  |
| ----- | ---------------- | ------------------------ |
| d=1   | **WILL BREAK**   | Direct callers/importers |
| d=2   | LIKELY AFFECTED  | Indirect dependencies    |
| d=3   | MAY NEED TESTING | Transitive effects       |

## Risk Assessment

| Affected                       | Risk     |
| ------------------------------ | -------- |
| <5 symbols, few processes      | LOW      |
| 5-15 symbols, 2-5 processes    | MEDIUM   |
| >15 symbols or many processes  | HIGH     |
| Critical path (auth, payments) | CRITICAL |
| **Zero callers found**         | **UNKNOWN** |

`UNKNOWN` is not a low rung on this scale — it means the walk could not answer.
An empty caller set is equally consistent with "genuinely unused" and "the
callers are not resolvable by the index" (plain-object property access, dynamic
dispatch, cross-language calls), so few-callers ⇒ LOW does **not** apply.
Confirm with a text search (grep) before treating the symbol as safe to change
or delete.

`risk` is the edit gate: warn on HIGH/CRITICAL and stop on UNKNOWN until the
uncertainty is resolved. Never waive the edit gate.

## Commands

**impact** — the primary command for symbol blast radius:

```bash
node .gitnexus/run.cjs impact validateUser -d upstream --repo .
# → d=1 (WILL BREAK): loginHandler, apiMiddleware
#   d=2 (LIKELY AFFECTED): authRouter, sessionManager
# -f <path> disambiguates common names; --depth <n> caps traversal (default 3);
# --include-tests passes through test-file symbols (off by default)
```

**detect-changes** — git-diff based impact analysis (alias `detect_changes`):

```bash
node .gitnexus/run.cjs detect-changes --scope all --repo .
# → Changed: 5 symbols in 3 files
#   Affected: LoginFlow, TokenRefresh, APIMiddlewarePipeline
#   Risk: MEDIUM
# --scope staged|unstaged|all|compare; --base-ref main for compare
```

`partial: true` (a graph query failed) or `truncated: true` (the changed-symbol
listing was capped) means the result is short of the truth, and reads like
`UNKNOWN` above: a zero there means unseen, not unaffected. Re-run it rather
than tick the pre-commit check.

A wrong-checkout zero carries neither flag and is shape-identical to a genuine
clean result, so confirm the checkout you edited is the one that was diffed
before treating an empty change set as a passed check.

## Example: "What breaks if I change validateUser?"

```bash
node .gitnexus/run.cjs status --repo .
#   → indexed commit = HEAD — fresh

node .gitnexus/run.cjs impact validateUser -d upstream --repo .
#   → d=1: loginHandler, apiMiddleware (WILL BREAK)
#   → d=2: authRouter, sessionManager (LIKELY AFFECTED)

# Risk: 2 direct callers = MEDIUM
# Report: Repository <name> (<path>)  Index: current
```
