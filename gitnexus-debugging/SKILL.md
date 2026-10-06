---
name: gitnexus-debugging
description: "Use when the user is debugging a bug, tracing an error, or asking why something fails. Examples: \"Why is X failing?\", \"Where does this error come from?\", \"Trace this bug\""
---

# Debugging with GitNexus

**Always use the CLI.** The GitNexus MCP server is often not mounted
(multiple sessions have hit `Server "gitnexus" not found`); every command below
works through plain Bash. Run everything from the repo root:
`node .gitnexus/run.cjs <command>`. If `.gitnexus/run.cjs` is missing,
bootstrap with `bunx gitnexus@latest analyze`.

## Bind the repository first

A root cause traced in the wrong repository is a wrong root cause.

Multiple repositories are indexed on this machine (verified via `list`), so
**pass `--repo <name>` on every command** — usually `--repo .` for the repo
you are in. Never rely on a default. If you cannot tell which repository is
meant, stop and ask. This matters most for `cypher`, whose statement carries
no in-band hint of which database it ran against.

```
node .gitnexus/run.cjs list              # all indexed repos + stats
node .gitnexus/run.cjs status --repo .   # index freshness, indexed commit
```

A stale index describes the code from before your bug, so refresh before
trusting a trace: `node .gitnexus/run.cjs analyze --index-only`. State the
repository and index freshness with the diagnosis.

## Workflow

```
0. status --repo .                                     → bind repo, check staleness
1. query "<error or symptom>" --repo .                  → find related execution flows
2. context <suspect> --repo .                           → callers/callees/processes
3. trace <from> <to> --repo .                           → shortest call path
4. cypher "MATCH path..." --repo .                      → custom traces if needed
5. Read source files to confirm root cause
```

## Checklist

```
- [ ] Understand the symptom (error message, unexpected behavior)
- [ ] status — bind repo; confirm index fresh (re-index if stale)
- [ ] query for error text or related code
- [ ] Identify the suspect function from returned processes
- [ ] context to see callers and callees
- [ ] trace when you need the path between two symbols
- [ ] cypher for custom call chain traces if needed
- [ ] Read source files to confirm root cause
- [ ] State the repository and index freshness with the diagnosis
```

## Debugging Patterns

| Symptom              | GitNexus Approach                                          |
| -------------------- | ---------------------------------------------------------- |
| Error message        | `query` for error text → `context` on throw sites |
| Wrong return value   | `context` on the function → trace callees for data flow    |
| Intermittent failure | `context` → look for external calls, async deps            |
| Performance issue    | `context` → find symbols with many callers (hot paths)     |
| Recent regression    | `detect-changes --scope all --repo .` — what your changes affect |
| "How does A reach B?" | `trace` between the two symbols — shortest call chain in one call |

## Commands

**query** — find code related to error:

```bash
node .gitnexus/run.cjs query "payment validation error" --repo .
# → Processes: CheckoutFlow, ErrorHandling
#   Symbols: validatePayment, handlePaymentError, PaymentException
```

**context** — full context for a suspect:

```bash
node .gitnexus/run.cjs context validatePayment --repo .
# → Incoming calls: processCheckout, webhookHandler
#   Outgoing calls: verifyCard, fetchRates (external API!)
#   Processes: CheckoutFlow (step 3/7)
# -f <path> disambiguates common names
```

**trace** — shortest call chain between two symbols:

```bash
node .gitnexus/run.cjs trace processCheckout fetchRates --repo .
# → status: ok, hopCount: 3
#   hops: processCheckout → validatePayment → verifyCard → fetchRates
```

When no path exists, `trace` reports the furthest reachable node — exactly
where the chain breaks (dynamic dispatch, reflection, or an external boundary).

**cypher** — custom call chain traces:

```bash
node .gitnexus/run.cjs cypher 'MATCH path = (a)-[:CodeRelation {type: "CALLS"}*1..2]->(b:Function {name: "validatePayment"}) RETURN [n IN nodes(path) | n.name] AS chain' --repo .
```

## Example: "Payment endpoint returns 500 intermittently"

```bash
node .gitnexus/run.cjs status --repo .
#   → indexed commit = HEAD — fresh

node .gitnexus/run.cjs query "payment error handling" --repo .
#   → Symbols: validatePayment, handlePaymentError

node .gitnexus/run.cjs context validatePayment --repo .
#   → Outgoing calls: verifyCard, fetchRates (external API!)

# Root cause: fetchRates calls external API without proper timeout
# Report: Repository <name>  Index: current
```
