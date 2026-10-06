---
name: gitnexus-exploring
description: "Use when the user asks how code works, wants to understand architecture, trace execution flows, or explore unfamiliar parts of the codebase. Examples: \"How does X work?\", \"What calls this function?\", \"Show me the auth flow\""
---

# Exploring Codebases with GitNexus

**Always use the CLI.** The GitNexus MCP server is often not mounted
(multiple sessions have hit `Server "gitnexus" not found`); every command below
works through plain Bash, so do not attempt MCP tools first. Run everything
from the repo root: `node .gitnexus/run.cjs <command>`. If `.gitnexus/run.cjs`
is missing, bootstrap with `bunx gitnexus@latest analyze` (npm 11 `npx` crashes).

## Bind the repository first

Multiple repositories are indexed on this machine (verified via `list`), so
**pass `--repo <name>` on every command that accepts it** — usually
`--repo .` for the repo you are in. Never rely on a default.

```
node .gitnexus/run.cjs list              # all indexed repos + stats
node .gitnexus/run.cjs status --repo .   # index freshness, indexed commit
```

Report the bound repository and index freshness alongside your explanation.
If `status` reports the index is stale (indexed commit ≠ HEAD), re-index:
`node .gitnexus/run.cjs analyze --index-only`.

## Workflow

```
1. node .gitnexus/run.cjs status --repo .            → bind repo, check staleness
2. node .gitnexus/run.cjs query "<concept>" --repo .  → find related execution flows
3. node .gitnexus/run.cjs context <symbol> --repo .   → 360° view: callers/callees/processes
4. node .gitnexus/run.cjs trace <from> <to> --repo .  → shortest call path between symbols
5. Read source files for implementation details
```

## Checklist

```
- [ ] status — bind repo; confirm index fresh (re-index if stale)
- [ ] query for the concept you want to understand
- [ ] Review returned processes (execution flows)
- [ ] context on key symbols for callers/callees
- [ ] trace when you need the path between two symbols
- [ ] Read source files for implementation details
- [ ] State the repository and index freshness with the explanation
```

## Commands

**query** — find execution flows related to a concept:

```bash
node .gitnexus/run.cjs query "payment processing" --repo .
# → Processes: CheckoutFlow, RefundFlow, ...
#   Symbols grouped by flow with file locations
# -l <n> caps results (default 5); --content inlines full symbol source
```

**context** — 360-degree view of a symbol:

```bash
node .gitnexus/run.cjs context processPayment --repo .
# → Incoming calls, outgoing calls, member processes
# -f <path> disambiguates common names; --content inlines full source
```

**trace** — shortest directed path between two symbols:

```bash
node .gitnexus/run.cjs trace checkoutHandler chargeStripe --repo .
```

If a query or context call returns nothing useful, fall back to text search
(grep) — an empty result can mean the symbol is not resolvable by the index,
not that it is unused.

## Example: "How does payment processing work?"

```bash
node .gitnexus/run.cjs status --repo .
#   → indexed 2026/10/5, commit d03a59f (= HEAD) — fresh
node .gitnexus/run.cjs query "payment processing" --repo .
#   → CheckoutFlow: processPayment → validateCard → chargeStripe
node .gitnexus/run.cjs context processPayment --repo .
#   → Incoming: checkoutHandler, webhookHandler
#   → Outgoing: validateCard, chargeStripe, saveTransaction
# then read src/payments/processor.ts for implementation details
# answer, noting: repository name + index freshness
```
