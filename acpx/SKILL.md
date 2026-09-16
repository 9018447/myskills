---
name: acpx
description: Use acpx as a headless ACP CLI for agent-to-agent communication, including installed-agent inspection, prompt/exec/sessions workflows, session scoping, queueing, permissions, output formats, system-prompt overrides, multi-agent flows authored with defineFlow/decision/decisionEdge, and DeepSeek Harness (dsh), ZCode (zcode-acp bridge), and Oh My Pi (omp) ACP support via the raw agent escape hatch.
---

# acpx

Use `acpx` when another coding agent should inspect, implement, review, test, or reason about work in a repository.

`acpx` is a headless ACP client. Prefer it over PTY/terminal scraping when the target agent supports ACP.

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

Common built-in agents include:

```text
codex
claude
gemini
kimi
qwen
cursor
copilot
droid
opencode
```

For another ACP-compatible command, use:

```bash
acpx --agent '<command>' exec '<prompt>'
```

For DeepSeek Harness:

```bash
acpx --agent 'dsh --profile acp' exec '<prompt>'
```

For ZCode (via the `zcode-acp` bridge):

```bash
acpx --agent 'zcode-acp-server' exec '<prompt>'
```

ZCode drives the real `zcode app-server`. The `zcode` CLI must be discoverable; if it is only bundled inside the desktop app, set `ZCODE_BIN` to its `zcode.cjs` entry (e.g. `ZCODE_BIN=/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs`). Credentials live in `~/.zcode/v2/config.json`; no API key is passed on the acpx side.

For Oh My Pi (omp):

```bash
acpx --agent 'omp acp' exec '<prompt>'
```

`omp acp` is omp's native stdio ACP mode. Requires `omp` on `PATH`.

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

## Multi-agent flows

Use `acpx flow run` only when the workflow genuinely requires persistent multi-step routing, branching, or coordination between several agents.

For simple ticket dispatch, prefer ordinary independent `acpx` invocations instead of building a flow.

