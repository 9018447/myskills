---
name: deslop
description: Remove AI-generated code slop and clean up code style
---

# Remove AI code slop

Check the diff against main and remove AI-generated slop introduced in the branch.

## Focus Areas

- Extra comments that are unnecessary or inconsistent with local style
- Defensive checks or try/catch blocks that are abnormal for trusted code paths
- Casts to `any` used only to bypass type issues
- Deeply nested code that should be simplified with early returns
- Other patterns inconsistent with the file and surrounding codebase

## Chinese-output style

For Chinese text (docs, comments, agent-facing prompts), additionally check the host's plain-language rules:

- AI-flavored filler and terms standing in for explanations ("triggered the fallback" without saying what the fallback is)
- Vague references ("it / this / this setup" whose target the paragraph does not name)
- Telegraphic compression (dropped subjects, dropped cause-effect steps)
- Verdicts without reasons, or a paragraph that stops making sense when read on its own

## Guardrails

- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
- Keep the final summary concise (1-3 sentences).
