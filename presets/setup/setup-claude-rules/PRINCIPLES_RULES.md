# Work Principles (distilled from the pstack principle-* series)

## Hard constraints

Apply these principles item by item. Scenario-specific injection during dispatch is handled by acpxtodo's mapping table (per-ticket-type scenario entries); this file is the universal subset and applies to all work.

- **minimize-reader-load** — code, comments, and docs are written for the next reader. Plain names, full paths, no skipped steps; if a reader still has to ask "so what does this actually mean", it is not finished.
- **subtract-before-you-add** — first ask whether deleting code solves the problem, then adding. Every added abstraction, config option, or defensive branch must name the old burden it removes in exchange.
- **test-behavior-not-implementation** — tests assert behavior (input → output, observable side effects), not implementation details (internal call order, private structure). Refactoring the implementation must not turn a good test suite red.
- **prove-it-works** — done means evidence: test output, run results, verifiable pointers, not "should be fine". When a claim conflicts with what is on disk, disk wins.
- **fix-root-causes** — for bugs, keep asking why until the root cause before acting; patching over symptoms schedules the same bug for delivery to the future.
- **attack-the-premise** — after two consecutive failures of the same kind of fix, stop and examine the shared assumption; do not try a third time. If three attempts circle the same premise, the premise is what is wrong.
- **foundational-thinking** — before acting, ask what the question is really asking; writing straight onto the first formulation often bakes a wrong premise into the code.
- **type-system-discipline** — constraints that types/structures can guard (illegal states unrepresentable) are not guarded by comments and conventions. `any` and type bypasses downgrade a constraint to a verbal promise.
- **encode-lessons-in-structure** — encode lessons into structure (check scripts, tighter types, rule files), not into memory. A lesson that depends on someone remembering it next time was never learned.
- **outcome-oriented-execution** — accept by resulting state, not by actions performed. "Ran the command" is not a result; "the command's output is on disk and correctly shaped" is.
- **guard-the-context-window** — context is a budget. Spill long output to disk and take summaries, read only the relevant sections, retrieve instead of bulk-reading; the attention saved goes to judgment.
