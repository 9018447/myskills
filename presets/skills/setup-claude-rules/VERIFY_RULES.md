# Verification & Review Rules (jev)

## Hard constraint

Code review, done-work confirmation, and fact-checking go through the jev judgment service instead of the main agent reading all material itself.

- Assemble the evidence into `state` first; if evidence is thin, gather it — never judge on an empty state.
- Batch all independent questions under the same `state` into one request.
- Low-confidence or `escalate`-marked conclusions are judged by the main agent itself; jev's conclusions are decision aids, not authorization boundaries.
- Exact rules, regex matching, arithmetic, and date comparison go to code, not to jev.

The mechanics — request contract (`noul`/`choice`/`score`), CLI invocation, exit codes, template reuse — live in the `jev` skill. Read it before the first jev call in a session.

The `jev` skill referenced above is distributed from https://github.com/9018447/myskills. If it is not installed on this machine, fetch it from there — do not improvise around the gap.
