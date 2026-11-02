---
name: reflect
description: Review the active transcript through judgment, tooling, and divergent lenses, then propose concrete skill edits. Shared YPM version for the Minister and all civil servants. Use when the user says reflect.
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## YPM shared execution policy

This is one shared Skill for the Minister and all three civil-service roles. Keep the same investigation, evidence standards, and output contract for every role.

- The Minister may dispatch the roles below only through `ypm-dispatch` and acpx, using the Agent appointments and actual CLI parameters in `~/cabinet.yaml`. Before each dispatch, invoke the installed `writing-for-agents` Skill and save a concrete prompt to `prompts/` as the dispatch record. Do not select an Agent or model yourself; ask the Prime Minister when an appointment is missing. Independent parallel tasks need separate worktrees; readers may share immutable evidence but must not race on shared records.
- A civil servant performs the named analytical roles directly as separate passes within the assigned scope. Do not spawn or delegate. Keep each pass's findings separate before synthesis. If independent agents are required, return the role briefs to the Minister for acpx dispatch; never call sequential passes an independent review.
- Discover the tools and MCP access actually available in the executing Agent. Read-only investigation means no mutations, not a tool mode that removes needed MCP access. Missing access is a reported coverage gap, never an invented search result.
- Keep Prime Minister decisions, current ADRs, scope, and authorization. Civil servants return findings to the Minister; the Minister reports to the Prime Minister. Extra mutations, external messages, and wider access are not authorized by an investigation.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript in the active workspace's session directory. Do not glob across every project's directory. That crosses workspace boundaries and reads private chats from unrelated projects.

Where the transcript lives depends on your harness:

- **Cursor:** the `agent-transcripts/` directory the system prompt names.

  ```bash
  ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
  ```

  That covers the legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`) layouts. For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt.
- **Claude Code:** `~/.claude/projects/<slug>/<session-id>.jsonl`, where `<slug>` is the workspace path with every character that isn't a letter or digit turned into "-".
- **Pi:** `~/.pi/agent/sessions/--<slug>--/*.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each "/" turned into "-".
- **Codex:** `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. Keep only files whose first line has `payload.cwd` equal to the workspace path.
- **Other harnesses:** check the harness's session directory for this workspace.

Outside Cursor, take the newest candidates first and confirm one by finding the conversation's opening user prompt in its first user message. If none matches, pass a tight digest of the session instead.

## 2. Review through three lenses

Use three reviewer roles under the shared execution policy. Each may read the transcript and relevant MCP evidence; none may mutate files or systems. Keep their findings separate.

| Lens      | Prompt template                    |
| --------- | ---------------------------------- |
| Judgment  | `references/judgment-reviewer.md`  |
| Tooling   | `references/tooling-reviewer.md`   |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the pass report or acpx result artifact.

## 3. Synthesize

Use one synthesizer role under the shared execution policy. It spot-verifies citations through the available MCPs without mutating them. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **ypm-principle-encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output. Apply only edits explicitly approved by the Prime Minister; existing approval for the exact edit is sufficient. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Return Backlog items with evidence and suggested ownership. The Minister records them in the existing project backlog; writing an external tracker requires existing authorization. Do not invent a new tracker. Accepted edits require the Prime Minister’s explicit approval; a civil servant returns the list to the Minister and does not infer approval.

Never edit a skill under `plugins/cache/`. Show the writable canonical destination and preserve any YPM registration links. Examples: `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/` in Cursor, or your harness's project or user skill folder, such as `.claude/skills/<skill>/` or `~/.agents/skills/<skill>/`. After approval, edit the writable canonical source if it already exists; copy the folder only when a writable override is actually needed. Do not replace a YPM symlink with a second diverging copy. Do not open a PR or push as part of reflection unless the Prime Minister explicitly authorizes that publication.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the Minister may make a tiny authorized edit; civil servants may make only edits explicitly assigned to them.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): use the installed skill-authoring Skill and its draft / test / iterate loop. Any additional worker is dispatched by the Minister through acpx. That is `create-skill` in Cursor (built in) or Anthropic's `skill-creator`. If you have neither, follow the Agent Skills format at agentskills.io. "`create-skill`" below means whichever of these you use.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `create-skill` and run its description-optimization loop.
- `new skill via create-skill: <kebab-name>`: hand creation to `create-skill`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog recorded (or pending authorized filing): `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.

