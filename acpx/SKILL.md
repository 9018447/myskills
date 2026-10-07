---
name: acpx
description: Use acpx as a headless ACP CLI for agent-to-agent communication, including installed-agent inspection, prompt/exec/sessions workflows, session scoping, queueing, permissions, output formats, system-prompt overrides, multi-agent flows authored with defineFlow/decision/decisionEdge. Dispatch chain for implementation work: omp / kimi -> dsh (fallback). zcode is retired (headless model creation broken, 2026-10-06); claude is not a dispatch target.
---

# acpx

Use `acpx` when another coding agent should inspect, implement, review, test, or reason about work in a repository.

`acpx` is a headless ACP client. Prefer it over PTY/terminal scraping when the target agent supports ACP.

## Headless dispatch pattern (scripted / orchestrator use)

When an orchestrator agent dispatches work to acpx, follow this pattern — the two failure modes it prevents are blocking waits and zombie wrappers:

0. **Dispatch through a herdr pane when the session runs inside herdr (`HERDR_ENV=1`)**; the harness's own background Bash (`run_in_background: true`) is the fallback when herdr is unavailable. Pane dispatch runs the task in a real terminal the user can `herdr session attach` into, and completion notification is bridged by wrapping `pane wait-output` in a background Bash:

1. **Write the prompt to a file** and pass it with `-f`; never inline long prompts into shell quoting.

1b. **Every dispatch goes into a dispatch tab named by ADR.** One tab per ADR of the work being dispatched (fallback: the feature slug when the work has no ADR), max **8 panes** per tab. Check first whether a tab with that label already exists and reuse it instead of creating a new one; when it already holds 8 panes, open the next tab of the series (`<adr>-2`, `<adr>-3`, …). Create:

   ```bash
   herdr tab create --cwd "$PWD" --label "<adr-slug>" --no-focus
   ```

   Read `tab_id` / `root_pane.pane_id` from the response; never guess IDs. `--cwd "$PWD"`, `--label`, `--no-focus` are mandatory. Reuse `herdr tab list` (or the equivalent listing) to find an existing dispatch tab before creating one.

   **Re-dispatch: verify the pane still exists first.** A pane dies with the agent session that ran in it — after a run finishes, the old pane-id is gone and dispatching into it fails with `pane_not_found` (2026-10-06: cost one wasted dispatch round). Before re-dispatch, `herdr pane get <pane-id>` (or `herdr pane list`); when gone, reuse the tab from `herdr tab list` or recreate the tab, and take the fresh pane-id.

   **Parallel dispatch into one working tree: file sets must not intersect.** When several tasks run concurrently in the same checkout, the files each task is allowed to modify must be disjoint; intersecting sets cause in-flight edits from one task to break another's test runs (2026-10-06: two tickets both touching `agent/src/bridge.jl` — one reported a `UndefVarError` caused by the other's half-finished edit). Intersecting file sets → serialize the dispatches, or give each task its own git worktree.
2. **Launch with a log file and an explicit idle TTL so the wrapper exits on its own.** Primary form (herdr pane from the dispatch tab; output tee'd to the log so both the pane and the file have it):

   ```bash
   herdr pane run <pane-id> "acpx --cwd <repo> --approve-all --ttl 60 --timeout 3600 <agent> exec -f prompt.md 2>&1 | tee .agent-results/<agentname>-<label>.log"
   ```

   Fallback form (no herdr — Bash `run_in_background: true` carries the completion notification):

   ```bash
   acpx --cwd <repo> --approve-all --ttl 60 --timeout 3600 <agent> exec -f prompt.md > .agent-results/<agentname>-<label>.log 2>&1
   ```

   Logs go to `.agent-results/` (relative to the launch directory), not `/tmp/` — create the directory if it is missing: `mkdir -p .agent-results`.

   `--timeout` caps one prompt's wait; `--ttl` governs idle shutdown after completion. Both are needed — one does not imply the other.

   **A process detached with `nohup ... &` from an ordinary foreground Bash command is NOT tracked: no completion notification will ever arrive.**

   **The harness's own background time limit kills tracked tasks too** (2026-10-01: a healthy dsh ticket dispatch was killed at the ~30-min default, log ended `[done] cancelled`). The implement-zh rule "no `--timeout`" does not cover this. Always pass an explicit `timeout` on the `run_in_background` launch (max 7200000 ms = 2 h); for expected >2 h work use a tmux detached session plus a waiter instead.

   **The two dispatch forms are mutually exclusive.** The `acpx <agent> exec -f prompt.md` form is for built-in agents only. Overlay agents dispatched via `acpx --agent '<command>' exec -f prompt.md` must NOT also carry a positional agent name before `exec` — writing `--agent 'dsh --profile acp' ... dsh exec -f ...` shifts parsing and fails with `error: unknown option '-f'`.

4. **Verify within ~1 minute of launch that the task actually started** (the log reaches `session/new` / `session/set_config_option` with no apply error, and is advancing). For the herdr form, arm the completion callback the same way the fallback gets one — wrap `pane wait-output` in a background Bash so its exit wakes the session:

   ```bash
   herdr pane wait-output <pane-id> --match "end_turn" --timeout 3600000  # via run_in_background: true
   ```

   The match string must not appear in the dispatched command text, or the shell's echo of that command triggers `wait-output` instantly (fake completion). Pick a marker that exists only in real output (`[done] end_turn` qualifies as long as the command text itself does not contain it). On timeout, `pane read` first to see actual state — never blindly re-dispatch.
5. **Do not block-poll.** End the turn; act when the completion notification arrives (tracked background task, or its waiter), or the user pings. To check interim progress, `tail` the log file in a short non-blocking call.
6. **Turn completion = the `[done] end_turn` marker** at the end of the log. That marker, not the background task's exit status, is the completion criterion: the acpx wrapper process can linger after the turn ends even past its TTL.
7. **Reap the wrapper by PID.** Record the launcher PID (or find it once with `pgrep -af` when nothing else matches); when the marker is present and the process lives, `kill <pid>`. Never verify with `pgrep -f <pattern>` whose pattern appears in your own check command — it self-matches and reports a dead task as alive; confirm with `ps -p <pid>`.
6. Read the delivered result from the tail of the log; `--format quiet` when only the final answer line is needed.

## Core usage

### One-shot task

Use `exec` when the task does not need conversational state:

```bash
acpx <agent> exec '<prompt>'
```

Example:

```bash
acpx codex exec 'review the current changes'
```

### Codex proxy

When dispatching to `codex` and network access needs to go through a proxy, set the proxy env vars on the acpx launch (port `7890`):

```bash
HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890 acpx codex exec '<prompt>'
```

Scope the vars to the single command as above — do not export them in the shell. When the task is done (or if the dispatch was persistent), clear them so later work is unaffected:

```bash
unset HTTP_PROXY HTTPS_PROXY
```

### Persistent session

Use a named session when follow-up context matters:

```bash
acpx <agent> sessions ensure -s <name>
acpx <agent> -s <name> '<prompt>'
```

Sessions are scoped by agent, working directory, and optional session name.

Use a new session for logically independent work. Do not reuse one session across unrelated tickets.

### Parallel / non-blocking work

Independent tasks should use different named sessions.

If a session is already busy and the caller should not wait:

```bash
acpx <agent> -s <name> --no-wait '<prompt>'
```

Do not send concurrent independent tasks into the same session.

## Agent selection

**派发候补链（2026-10-06 定案）**：实现类工作首选 `omp`（overlay，`--agent 'omp acp'`）或内置 `kimi`；不可用时降级 `dsh`（`--agent 'dsh --profile acp'`）。**zcode 已退役**（3.14.4 headless 选模型必败，不再排障）；**`claude` 不作派发目标**。

Common built-in agents include:

```text
codex
gemini
kimi
qwen
cursor
copilot
droid
opencode
pi
```

**A bare agent name the user gives means the built-in `acpx <name>` form.** Do not
map a bare name onto an overlay/bridge command from this file — if the user says
"pi", dispatch `acpx pi ...`, never `--agent 'omp acp'`. Overlays below are only
for commands the user names explicitly as such. Verify a bare name is built-in
with `acpx --help` before dispatching; if it is not listed, ask the user rather
than substituting a lookalike overlay.

For another ACP-compatible command, use:

```bash
acpx --agent '<command>' exec '<prompt>'
```

For DeepSeek Harness:

```bash
acpx --agent 'dsh --profile acp' exec '<prompt>'
```

For Oh My Pi (omp) — 候补链首选之一（代码票、零碎编码默认可用，不必等用户点名）：

```bash
acpx --agent 'omp acp' exec '<prompt>'
```

`omp acp` is omp's native stdio ACP mode. Requires `omp` on `PATH` — `command -v omp` 不在时直接降级 kimi，不要尝试安装或修 omp。

Do not assume every adapter supports every ACP capability.

## Working directory

Use `--cwd` when the agent must operate on a specific repository or worktree:

```bash
acpx --cwd <path> <agent> exec '<prompt>'
```

Always make the intended working directory explicit when dispatching work across multiple repositories or worktrees.

## Permissions

Default to normal read approval behavior.

For trusted autonomous implementation:

```bash
--approve-all
```

For review-only work:

```bash
--deny-all
```

Use a permission policy when finer control is required.

Do not grant broader permissions than the task needs.

## Output

Human-readable output is the default.

For scripts and orchestration:

```bash
--format json --json-strict
```

For only the final answer:

```bash
--format quiet
```

Prefer structured output when another program will consume the result.

## Model/config

When supported by the adapter:

```bash
acpx --model <model> <agent> exec '<prompt>'
acpx <agent> set model <model>
acpx <agent> set reasoning_effort <level>
```

Adapter capabilities differ. If a model, mode, or configuration is rejected, inspect the agent's advertised capabilities instead of guessing.

### Provider/model verification (2026-09-26 定案)

The adapter's configured default provider/model is **not** proof of what actually served the run — an adapter may ignore its settings default and fall back to another provider family (2026-09-26: dsh's settings pinned `arkcli-coding-plan`, runtime billed the DeepSeek official endpoint). When the billing endpoint matters:

- Verify the actual provider from **runtime evidence** (provider console usage, session records) — never from config files alone.
- To pin one, pass the model id **exactly as the ACP agent advertises it**. 2026-09-26 (dsh): advertised `modelId` strings are JSON-array literals like `["arkcli-coding-plan","deepseek-v4-1-flash"]`, and acpx matches `--model` by exact string equality — both `provider/model-id` and bare ids fail with a self-contradictory "did not advertise" error whose printed "available list" is actually each raw modelId and *does* contain the requested model. Read the failing error literally and pass one entry verbatim: `acpx --model '["arkcli-coding-plan","deepseek-v4-1-flash"]' ...`. Success signal: the log shows `session/set_config_option` instead of the apply error.
- Confirm the pin took effect with a cheap probe dispatch before routing real work through it.

## Operational rules

1. Use `exec` for isolated tasks and persistent sessions only when context must continue.
2. Use one session per independent task or ticket.
3. Use separate sessions for parallel work.
4. Prefer `--no-wait` when dispatch should not block.
5. Specify `--cwd` when repository/worktree identity matters.
6. Prefer structured output for automation.
7. Use the minimum permissions required.
8. Do not assume adapter-specific features are universal.
9. For unfamiliar or advanced commands, consult `acpx --help` or the upstream acpx documentation instead of relying on this skill as a complete CLI reference.
10. Verify a dispatch actually started within the first minute — the log must reach `session/new` / `session/set_config_option` with no apply error — using a `run_in_background` until-loop watcher (`until grep -qE 'session/new \(ok\)|Cannot apply|error' <log>; do sleep 3; done`). Chained `sleep N && tail` compounds are blocked by the harness.

## Multi-agent flows

Use `acpx flow run` only when the workflow genuinely requires persistent multi-step routing, branching, or coordination between several agents.

For simple ticket dispatch, prefer ordinary independent `acpx` invocations instead of building a flow.

