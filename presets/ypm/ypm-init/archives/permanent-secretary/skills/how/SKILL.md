---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

## YPM shared execution policy

This is one shared Skill for the Minister and all three civil-service roles. Keep the same investigation, evidence standards, and output contract for every role.

- The Minister may dispatch the roles below only through `ypm-dispatch` and acpx, using the Agent appointments and actual CLI parameters in `~/cabinet.yaml`. Before each dispatch, invoke the installed `writing-for-agents` Skill and save a concrete prompt to `prompts/` as the dispatch record. Do not select an Agent or model yourself; ask the Prime Minister when an appointment is missing. Independent parallel tasks need separate worktrees; readers may share immutable evidence but must not race on shared records.
- A civil servant performs the named analytical roles directly as separate passes within the assigned scope. Do not spawn or delegate. Keep each pass's findings separate before synthesis. If independent agents are required, return the role briefs to the Minister for acpx dispatch; never call sequential passes an independent review.
- Discover the tools and MCP access actually available in the executing Agent. Read-only investigation means no mutations, not a tool mode that removes needed MCP access. Missing access is a reported coverage gap, never an invented search result.
- Keep Prime Minister decisions, current ADRs, scope, and authorization. Civil servants return findings to the Minister; the Minister reports to the Prime Minister. Extra mutations, external messages, and wider access are not authorized by an investigation.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Use one explainer role that explores and explains in one pass under the shared execution policy, built from `references/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

**YPM execution.** Apply the shared execution policy above: the Minister dispatches through acpx; civil servants perform separate passes or return an independence requirement to the Minister.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Use one explorer role per angle under the shared execution policy, each with `references/explorer-prompt.md` and its angle filled in.

## 3. Synthesize (complex only)

Once all explorer passes have returned, use one explainer role with `references/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.

