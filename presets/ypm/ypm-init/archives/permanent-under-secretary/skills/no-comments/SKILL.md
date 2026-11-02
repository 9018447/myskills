---
name: no-comments
description: "常务次官在大臣指定范围内直接执行 Comment Sicko 注释检查，处理接受的发现，并提出约束编码方案。pstack no-comments 的 YPM 最小适配版。"
---

# No comments

Run Comment Sicko as a fresh inspection pass. Act on accepted findings.

Defer to Comment Sicko's fresh perspective.

## YPM execution boundary

Execute the scoped task directly; do not spawn agents. Read external Skills from their verified installation paths and follow their methods within this boundary. Any step requiring another agent goes back to the Minister for acpx dispatch. Report missing dependencies and their effect; do not claim a Skill ran when it did not. Existing Prime Minister decisions, ADRs, scope, and authorization remain in force.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Read [`references/comment-sicko.md`](references/comment-sicko.md) in full and run its prompt yourself in a fresh pass over the scope. Do not restate its rules. Preserve the inspection report and comment-only diff for step 2. This is the original no-subagent fallback applied to YPM’s execution boundary, not an independent-agent review. If a separate reviewer is required, return that requirement and evidence to the Minister for acpx dispatch; do not spawn one yourself.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, run `/how` or `/why` on their symbol. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert only that rejected inspection pass’s edits, preserve unrelated work, and rerun once with the failure named. Reject a second, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run `/architect` once for the accepted set and surrounding code. Stop at the sketch. Architect shapes. Step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The **ypm-principle-fix-root-causes** and **ypm-principle-redesign-from-first-principles** skills guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Use existing approval for the named encoding. If it is not already approved, return the offer to the Minister for interactive approval within the Prime Minister’s authority. Unattended and eval require pre-approval conveyed in the Minister’s brief. Do not infer approval from silence. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.

Source: pstack `skills/no-comments/SKILL.md`, blob `ca55cce41d85b90944f8f20853bfafbcb6a30a32`. See [LICENSE.pstack](LICENSE.pstack).
