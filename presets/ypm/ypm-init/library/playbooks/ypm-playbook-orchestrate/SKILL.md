---
name: ypm-playbook-orchestrate
description: "长期、多任务、多公务员协调；YPM 改编自 pstack orchestrate Playbook。"
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

### Orchestrate

**You own the program, never the code. Author briefs, drain the queue, keep the frontier green, decide.** For a whole project handed to one standing coordinator chat: multi-day, many stacked PRs, dozens to hundreds of subagents, the human checking in twice a day instead of every five minutes. One task driven to a predicate is Autonomous run. One ambitious run needing a bespoke workflow is figure-it-out. Route here when the work outlives any single agent. Work one agent could finish inside the session's budget is not a program.

Ceremony must scale with the program. On cheap near-identical units, collapse it as each section directs.

Three rules carry the rest.

- Completions are queue events, not interrupts.
- Every spawn and every resume carries the standing orders verbatim.
- The brief is the product. A vague brief fails quietly, because a worker cannot ask you a question.

#### Roles and placement

- **Coordinator (the Minister).** Frame the program, author briefs with `writing-for-agents`, collect reports, own the Prime Minister’s report, and make delegated judgments. Do not author business code. Conflicted merges, chain rebases, and code changes are tasks for appointed civil servants. A clean mechanical integration may be done by the Minister within authorization. All dispatches, replacements, and watcher assignments go through `ypm-dispatch` and acpx. Scan `prompts/` and `.agent-results/` at drain points to reconcile dispatches; no pstack orchestration runtime is required.
- **Track responsibility.** Keep tracks as groups of assignments managed by the Minister, not another Agent rank. A civil servant may own a broad track and report its units, blockers, and aggregated evidence, but cannot dispatch workers or verifiers. The Minister refills a rolling window only as fast as reports can be reviewed. Do not pay for nested orientation or wait on hidden children.
- **Worker / verifier.** Use a Prime-Minister-appointed civil servant through acpx in a suitable local or explicitly configured remote worktree. Use the environment that actually has the required runtime, simulator, authentication, or scoped session records. Inline necessary context or point at accessible repository paths. Prefer fewer, broader assignments and one writer per worktree or branch. The verifier must be independent of the author; use a different model family only when such an appointment is available, never invent an appointment.

Dispatch depth is Minister to civil servant. Name track boundaries per project; build, landing, and verification are common cuts, not required Agent layers. Do not create a hard-coded swarm hierarchy.

#### Store layout

Keep authoritative assignment and verification facts in the dispatch prompts under `prompts/` and the per-task result files under `.agent-results/`. Do not keep a project state file: mode, ADR pointer, work frontier, and derived conclusions are read from ADR indexes, tickets, PRs, and those records at read time. Prompts, logs, and evidence may live under `.ypm/` or the project’s existing artifact paths. Every fact has one designated writer; aggregate at read time. The following upstream record roles are fields or references in those existing records, not new TSV/JSON databases.

- `standing_orders` records the numbered constraints or points to the existing authoritative rules. Paste the applicable orders into every dispatch and resume. When a correction repeats, update its structural source before acting.
- `overview` references the durable PR and issue history. Append facts, never rewrite the history on each event.
- `assignments` has one row per unit, with id, track, status, branch, PR, head SHA, and prompt path. Update the existing `.agent-results/<id>.md` result.
- `merge_frontier` is derived from actual PR bases, current head SHAs, and merge state, with a generation number.
- `verification` holds per-PR, per-head verdicts and evidence in the assignment record.
- `completion_events` holds completion pointers; `gates` records Prime Minister decisions still required. No unanswered gate implies approval.
- `decisions` references the experiment or decision trail. A task-local scientific TSV may remain an evidence artifact, never a competing assignment database.
- `status` is a report derived from assignment and verification facts at each drain, never a second manually synchronized database.

#### The brief

Your prompts to agents are your only product, and a sloppy brief compounds into slop across the whole tree. Every spawn carries all of it. A field you cannot fill is a unit you have not scoped yet.

```
GOAL         one sentence, the outcome, executable by a stranger with no chat access
SCOPE        paths this unit may write; paths it may not; its exclusive worktree or branch
CONTEXT      pointers to files and PRs; upstream reports pasted in full when this unit
             depends on them, because workers cannot see siblings
ACCEPTANCE   checkable criteria, one per line
VERIFY       exact commands or the control-skill path, plus known gotchas
TIMEBOX      rough cap on runtime; on expiry, return partial findings and stop rather than run on
FORBIDDEN    no PR retargets or merges, no rebase, no force-push, no fixes outside scope,
             plus unit-specific bans
REPORT       status, branch, head SHA, PRs, verdict, what you actually ran, deviations,
             suggested follow-ups
STANDING     <preferences.md pasted verbatim>
```

Size the brief to the unit. A one-command unit gets the template collapsed to a paragraph that still names goal, scope, the verify command, and the report shape. A 4KB scaffold around a two-line edit costs more to write and obey than the edit. Local spawns may reference the standing-orders file by store path. Verbatim paste is for cloud spawns and every resume.

A track brief adds its boundary and unit list, the Minister’s dispatch window, the drain protocol, and the rollup format. Civil servants report unit name, status, PR, head SHA, verdict, one-line finding, track status, and frontier delta. They do not create further Agents.

A dependency is a context relay, not just ordering. Undeclared upstream context makes the worker guess. Missing fields are a refuse-to-spawn condition. Audit one sampled assignment brief per track per wave, concurrently with the wave it samples, never as a gate in front of it. A failing brief stops that track and fixes the track brief and Minister’s dispatch instructions, not just the worker, because brief quality decays late in a run. Never resume-chain a brief. Respawn fresh with consolidated scope.

#### Steps

1. **Frame.** State the done predicate as something countable ("all 126 units merged, each ledger-verified `unit-test-verified` or better"). Quantify scope: units, rough effort, expected stacks, and the wall-clock budget. If one agent could finish inside that budget, stop here and run Autonomous run instead. Collapsing must not depend on another document being present. It means do the work directly in this session, plain workers where they help, verification inline, landing as you go, and none of the store, register, or pilot machinery below. Schedule landing against the budget. By roughly 70% of it, stop spawning and land what is verified. Name the tracks per project. A contested decomposition or one-way door goes through the arena skill before the pilot. Present the framing once. Reversible prep proceeds without waiting.
2. **Initialize records.** Reconcile `prompts/` and `.agent-results/`, establish standing orders before dispatch, and derive the merge frontier from actual PR metadata. Keep an evidence trail without installing `orch.ts`, another orchestration database, or a project state file.
3. **Pilot.** Push one unit through the whole path: brief, worker, verification, stack entry, ledger row, merge. The pilot exists to falsify the brief template, the verify recipe, and the unit size while that costs one agent instead of fifty. Fix the contract from pilot evidence before any fan-out. Scale the pilot to the unit. On programs of near-identical cheap units, the first unit is the pilot, run as a normal unit with its verify command inline, and fan-out starts the moment it lands. The dedicated pilot pipeline (separate verifier agent, audit gate) is for expensive or novel unit shapes, not for clone-units where a serialized pilot has nothing to falsify.
4. **Scale.** Spawn a rolling window of workers up to the in-flight cap, refilling as children finish. Blocking batches pay the slowest child of every batch. Keep track aggregation under the Minister; no sub-coordinator Agent layer. Recompute ready work after each drain. Relay upstream reports into downstream briefs. Keep sibling communication upward only. The sampled brief audit runs alongside the wave it samples and stops the next refill on failure, not the current one.
5. **Drain.** Run the queue discipline below at every drain point.
6. **Land.** Landing is continuous, never a terminal phase. Integration starts with the first verified unit and runs alongside the remaining waves. On heavy repos the stacker is a standing role from wave one, integrating as units verify. On repos where local git is cheap, the coordinator lands verified units itself per Roles. Keep the frontier green before upper-stack work. Stack safety governs. Advance the derived merge frontier only on merge or reported new head SHAs.
7. **Close.** Drain the final inbox, reconcile every spawned agent to a terminal row (done, abandoned, zombie-reconciled), confirm the predicate on the real artifact, confirm every landed PR has a verdict for its current head SHA, audit the trail per show-me-your-work including its cross-model review, encode recurring corrections into standing orders or the brief template. Leave the store intact. It is the postmortem.

#### Queue and drain

- On a completion notification, run a completion-pointer update to the existing `.agent-results/<id>.md` result and return to what you were doing. Never deep-review inline. A completion that needs review becomes a verifier unit. Never review a diff inside a drain.
- Drain in batches at four points: the end of a critical section, a track rollup, a frontier watcher wake (arm it via the loop skill, with a long heartbeat fallback), and before a human report. Begin each batch with a snapshot of unprocessed completion pointers. Arrivals during a drain wait for the next one.
- Critical sections you finish first: authoring a brief, a stack operation, a conflict decision, writing a gate, updating ledger or frontier.
- Each drain classifies every pointer (landed, needs-verify, failed, zombie, noise), writes the resulting rows in the existing assignment and verification entries, derives the status summary, then spawns the next wave in one message.
- Account for every spawned child at its track's rollup: arrived, respawned, or its scope explicitly absorbed. Silently redoing a missing child's work hides both the wasted spend and the coverage gap its result existed to close.
- A drain turn ends with the three lines from the derived assignment summary: counts against the states, what changed, gates open. Detail lives in the derived status report. The full reply contract applies at checkpoints and close.

#### Stack safety

- The frontier is a computed object, never narrative. Recompute the derived merge frontier after every merge and stack mutation: ordered PR list, branch names, head SHAs, a generation number, the lowest unmerged PR. The command walks the PR base chain through the checkout's current branch, so chain order and PR states come from the forge. It uses `gh` by default. Pass `--forge origin` when the program resolved the forge to Origin. Head SHAs come from local branch refs, so resolve it from the stacker's clone. A branch with no PR errors rather than guessing.
- Exactly one stacker per stack may mutate topology (chain rebases, force-pushes, base retargets, merges), serialized within its stack. Record the holder in the standing orders. Run chain rebases where resources and access actually suffice; avoid exhausting the coordinator machine.
- Workers never rebase and never retarget or merge PRs. Babysitters follow `../ypm-playbook-babysit/SKILL.md`, one per stack, scoped to one immutable frontier generation. They report conflicts to the stacker rather than rebasing.
- PR closes and retargets go through the stacker only. Closing a base PR orphans every chain above it. Merges and stack surgery are units with briefs like any other.
- One retro watcher follows merged PRs for reverts, post-merge CI breaks, and orphaned follow-ups.

#### Verification

Scale verification to the unit. When VERIFY is a single cheap command, the worker runs it and reports the output, and the coordinator spot-checks receipts. A dedicated verifier agent (on a different model family than the worker) is for units whose verification is expensive, judgment-laden, or high-blast-radius. A verifier agent whose entire product would be rerunning one command is ceremony, not verification.

Write verification rows in the existing assignment record and check the current PR and head SHA against each row. Key each verdict by PR number plus head SHA. Preserve the verdict vocabulary `live-ui-verified | unit-test-verified | type-check-only | verifier-blocked | verifier-failed`. Green CI is an input, not a verdict. Behavioral work needs better than type-check-only. Blocked is not pass; failed needs a fix assignment. An independent verifier overrides self-report on the same key. A new head invalidates the row unless the Shipping patch-id evidence explicitly carries it. Re-verify drift rather than relying on memory.

A unit is not done until its output is externalized the moment it lands, never batched to the end of the run. A worker pushes its branch, a verifier writes its ledger row, receipts land in the store. Work that exists only on one VM when that VM dies was never done.

#### Liveness and failure

- Never resume an agent to check on it. A resume restarts an idle agent. Probe read-only: the ledger, assignment records, `gh`, pushed branches, the actual acpx session or process status. Transcript mtime is not liveness.
- A silent death gets a synthetic postmortem row in the inbox (unit, failure mode, last evidence, options). Replan on evidence as it arrives. Never wait for full quiescence.
- Retry by mode: cap-hit or oom, respawn with smaller scope. Network-drop, retry as-is. Tool-error, retry on a different model. Unknown, retry once. Two retries, then abandon the unit and replan around it.
- A zombie that returns hours late reconciles against the current frontier and ledger before anything is accepted. Salvage unique findings through a fresh unit, never a blind merge.
- When continued spawning would produce garbage tree-wide (bad upstream output, broken acceptance, dead infra), write a stop line at the top of the standing orders, let in-flight work finish, fix the cause, clear it.
- Bound your own infra retries the same way you bound a child's. After a few consecutive tool aborts, stop retrying. Write a terminal handoff to durable state (what is done, where it lives, the exact command to resume) and end the run.
- After a coordinator restart, read standing orders and current task records, probe the actual acpx sessions and processes, and derive the frontier from branches and PRs. Do not assume a process survived or died merely because the coordinator restarted. Reattach only when supported and proven live. Otherwise the Minister dispatches a replacement with the stored brief and current evidence. Do not steal a record lock without proving its holder has stopped.

#### Escalation

Reaches the human, batched into the status page rather than per item: irreversible actions (force-push to shared branches, deploys, deletions, closing someone else's PR), genuine product or preference calls no experiment settles, a standing order that contradicts observed reality, a program-level dead end that survived a replan. Park each as a the assignment’s gates field entry before asking, and route work around it.

Never reaches the human: frontier nudges, rebase mechanics, retries, CI flake triage, review-thread triage, format fixes, scope the brief already forbids (refuse and continue), and "should I keep going". When in doubt, act and log.

Mid-run discoveries fix only what blocks the frontier. Everything else parks in follow-ups. At this fan-out a small scope leak multiplies into PRs nobody asked for.

**Reply:** at checkpoints and close: the predicate and the count against it from assignment records and verification records, tracks and what each landed, the frontier (PR list plus SHAs), verdicts summary, what was abandoned and why, gates awaiting the human (the only asks), the store path, and the trail path. Numbers from the tables, not narrative. Include PR links.
