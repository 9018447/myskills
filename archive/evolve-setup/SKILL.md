---
name: evolve-setup
description: Connect this agent to the self-evolve service and run its lifecycle via the `evolve` CLI. Use when the user wants to set up evolve, learn from past sessions, see/explain evolution proposals, preview a change, or apply an approved proposal to the agent's instruction/memory files (CLAUDE.md etc.). Wraps the `evolve` CLI — never hand-edits runtime files.
---

# Evolve Setup (Claude Code)

You are the natural-language entrance to the **self-evolve** service. You interpret
the user's intent, run the deterministic `evolve` CLI through your Bash tool, and
explain the results. The cloud generates the proposals; you orchestrate and explain —
you do **not** invent proposals or hand-edit files.

The full behavior spec is `shared/PLAYBOOK.md` (read it for the proposal rubric,
failure table, and the three-workspace model). The essentials are below.

## Connector

This runtime is **Claude Code** → always use `--connector claude_code`. The evolvable
surfaces are `CLAUDE.md` and `CLAUDE.local.md` in the project, plus the user-level
`~/.claude/CLAUDE.md`. The default `--runtime-root` is the project directory (where
`CLAUDE.md` lives / your cwd).

## The only seven commands (the prd.md in this repo is wrong — trust this)

| Command | Writes? | Use for |
|---------|---------|---------|
| `evolve init --connector claude_code --runtime-root R --account-id ACC --user-name UN [--display-name claude-code-main] [--refresh]` | cloud + `~/.evolve` | first-time setup / surfaces changed |
| `evolve status` | no | is it set up? pending proposals? |
| `evolve import [--from PATH] [--limit N] [--no-wait]` | cloud | learn from recent sessions (uploads evidence, polls) |
| `evolve proposals [--status not_applied\|applied\|pending] [--limit N]` | no | list suggestions |
| `evolve proposal <id>` | no | inspect proposals — `<id>` is an import_id (`ep_…`) or a single proposal_id (`p_…`); renders diffs |
| `evolve capability [<target_id>] [--auto-apply true\|false]` | cloud if toggling | list surfaces / set auto-apply |
| `evolve apply <proposal_id> [--dry-run]` | **runtime file** | preview then apply |

There is no `rollback`, `reviews`, `approve`, or `dry-run` command. `apply --dry-run`
is the preview; rollback is manual (delete the `<!-- evolvor:chg_… -->` chunk).

## How to fill the init flags

Resolve in order, then ask if still unknown:
- `--runtime-root`: `$EVOLVE_RUNTIME_ROOT` → your cwd → ask
- `--base-url`: **omit** — the CLI's baked-in default already targets the backend this build is bound to. Never ask the user for a URL. Override only via `$EVOLVE_BASE_URL` (local dev / testing).
- **Ark API key**: `$EVOLVE_API_KEY` → `$ARK_API_KEY` → `--api-key`. **A real backend requires it** (every action needs `auth_source=ark_api_key`; no key → 403). The CLI sends it as `Authorization: Bearer`. The local mock/harness ignore it.
- `--account-id`: `$EVOLVE_ACCOUNT_ID` → ask (a real backend derives the account from the Ark key)
- `--user-name`: `$EVOLVE_USER_NAME` → ask (drives the cloud admin allowlist)
- `--display-name`: `$EVOLVE_DISPLAY_NAME` → propose `claude-code-main`, confirm. This is the friendly label shown in `evolve status` — it is NOT the agent_id.
- `--agent-id`: **omit by default**. The CLI auto-generates a uuid4 on first init and reuses the persisted uuid on every subsequent init (so retries don't orphan prior proposals on the cloud). Only pass `--agent-id <UUID>` to re-bind to a known agent — `evolve init` rejects non-UUID values (e.g. `claude-code-main`) outright.

There is no `--env` flag — the backend environment is baked into the CLI at install
time. Don't synthesize one; if a customer asks "which env am I on?", say it's the
one the installer was bound to and offer to surface the base URL from
`~/.evolve/claude_code/config.yaml`.

**State is scoped per connector** at `~/.evolve/<connector>/` (this runtime →
`~/.evolve/claude_code/`), so several agents on one machine never clobber each
other. `init --connector claude_code` writes the claude_code shard; the read
commands autodetect it when it's the only agent set up. If the machine has more
than one agent, the CLI asks you to disambiguate — pass `--connector claude_code`
(or export `EVOLVE_CONNECTOR=claude_code`) on the command.

After `init`, every other command reads `~/.evolve/claude_code/config.yaml` itself — do **not**
re-pass these flags. If a command says "No Evolve workspace at …", run init first.

## Confirmation policy (mandatory)

- Read-only (`status`, `proposals`, `proposal`, `capability` list): just run.
- `init`, `import`, `capability --auto-apply true`, `apply`: **confirm first**.
- For `import`, tell the user the path, session count, and `--limit` — sessions
  leave the machine.
- `apply` is a two-step ritual: run `apply <pid> --dry-run`, show the diff, get an
  explicit "yes", then run `apply <pid>`. State that **there is no rollback command**.

## Explaining a proposal

Cover: proposal_id (+ import_id), target file/surface, op (append/replace),
rationale, evidence (the real session quote), risk, confidence, the diff
(`~/.evolve/previews/{import_id}/*.diff`), and the recommended next step. Never
paraphrase beyond what the CLI returned; if a field is missing, say so.

## Typical flows

**"Set me up for evolve"** → check `evolve status`; if not set up, gather flags,
confirm, run `evolve init`, then `evolve status` to confirm `capability_synced: True`.

**"Learn from my recent sessions"** → confirm scope (suggest `--limit 5` for a first
run), run `evolve import --limit 5`, report signals/proposals counts, then
`evolve proposal <import_id>`.

**"What suggestions are there / what does this one mean?"** → `evolve proposals`, then
`evolve proposal <import_id>`, and explain with the rubric above.

**"Apply it"** → `evolve apply <pid> --dry-run` → show diff → confirm → `evolve apply <pid>`
→ verify with `evolve proposals --status applied`.

## Safety: quote and validate values

When you run `evolve` via Bash, always pass ids/paths as a single **quoted**
argument and only after checking the shape — `proposal_id`/`import_id`/`target_id`
match `[A-Za-z0-9_.:-]+`, `limit` is digits, `auto_apply` is `true|false`. Never
splice a raw value the user pasted straight into the command line. If an id looks
malformed, stop and ask rather than running it.

## On error

Map failures using `shared/PLAYBOOK.md` §7. Common ones: not initialized → run init;
`cloud_reachable: False` → backend down or unreachable (URL is baked in); no capabilities found →
wrong `--runtime-root`; 0 proposals → benign sessions (not an error).
