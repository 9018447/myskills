---
name: skillsgate-helper
description: Use the skillsgate CLI to manage the user's AI-agent skills library — install, remove, list, update, scan, and publish skills. Use when the user asks to add/remove/update a skill, sync skills across agents, browse what's installed, or publish a skill.
---

# SkillsGate Helper

The user manages their skills library with **SkillsGate**
(https://skillsgate.ai). Skills are markdown files named `SKILL.md`.

- Global (canonical) store: `~/.agents/skills/<skill-name>/SKILL.md`
- Project-local installs: `.agents/skills/` in the project root
- Installs are symlinked into each agent's skills directory
  (e.g. `~/.cursor/skills/`, `~/.claude/skills/`); `.skill-lock.json` tracks them.

Always prefer the CLI over editing files or symlinks by hand, so the lock
file and agent links stay consistent.

## Commands

```bash
skillsgate list [-g]            # show installed skills (-g = global scope)
skillsgate add <source>         # install: @user/skill, owner/repo, owner/repo@skill, GitHub URL, or local path
skillsgate remove [name]        # uninstall a skill
skillsgate update [name]        # check and apply updates (no name = all)
skillsgate sync                 # sync skills from node_modules
skillsgate scan <source>        # security-scan a skill before installing
skillsgate publish [path]       # publish a local skill to the SkillsGate catalog
```

Useful flags: `-g/--global`, `-y/--yes` (skip prompts), `-a/--agent <id>`
(target specific agents), `--all`, `--copy` (copy instead of symlink).

## Common workflows

- **Install a skill**: `skillsgate add <source> -g -y`. For untrusted
  sources, run `skillsgate scan <source>` first and report the result.
- **Create a new skill**: make `~/.agents/skills/<name>/SKILL.md` with
  frontmatter (`name`, `description`) — the CLI has no scaffold command.
- **Check what's installed**: `skillsgate list -g` (global) or
  `skillsgate list` (current project).
- **Keep skills fresh**: `skillsgate update`.
- **Publish the user's own skill**: ensure the `SKILL.md` is valid, then
  `skillsgate publish <path>` (requires `skillsgate login` first).

If `skillsgate` is not on PATH, fall back to `npx skillsgate <command>`.
