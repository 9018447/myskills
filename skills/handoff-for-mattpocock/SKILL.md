---
name: handoff-for-mattpocock
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Determine the current project root as follows:

1. If the current directory is inside a Jujutsu workspace, use `jj root`.
2. Otherwise, use the current working directory.

Build a project ID from the project root using:

`<parent-directory>--<project-directory>`

For example:

`/home/user/research/my-project`

becomes:

`research--my-project`

Save the handoff outside the workspace at:

`<temp>/agent-handoffs/<project-id>/handoff.md`

Use the operating system's temporary directory. Create the required directories if they do not already exist. Overwrite the previous handoff for the same project.

Include the absolute project root near the top of the handoff.

If the project is a Jujutsu workspace, include the current change ID when it can be obtained cheaply. Do not fail the handoff if Jujutsu metadata is unavailable.

After writing the handoff, update the project's `AGENTS.md` so future agents can discover it.

Manage exactly one handoff pointer section in `AGENTS.md` using these markers:

`<!-- handoff:start -->`

and

`<!-- handoff:end -->`

The managed section should contain:

* a short heading such as `## Active handoff`
* the absolute path to the generated handoff document
* a short instruction telling a fresh agent to read it when resuming interrupted work

If both markers already exist, replace only the content between them.

If the markers do not exist, append the managed section to `AGENTS.md`.

Do not modify any other content in `AGENTS.md`.

If `AGENTS.md` does not exist, create it containing only the managed handoff section.

Include a "suggested skills" section in the handoff document, naming which skills the next agent should invoke.

Do not duplicate content already captured in other artifacts such as specs, plans, ADRs, issues, commits, diffs, or documentation. Reference them by path or URL instead.

Redact sensitive information such as API keys, passwords, tokens, credentials, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the handoff accordingly.
