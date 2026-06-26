# Skills Guide

Quick reference for creating pi skills.

## Skill Structure

```
my-skill/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Helper scripts (optional)
└── references/           # Detailed docs (optional)
```

## SKILL.md Format

```markdown
---
name: my-skill
description: |
  What this skill does and when to use it.
  Be specific about use cases.
---

# My Skill

## When to Use
Describe trigger conditions.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Common mistake to avoid

## Verification
How to verify success.
```

## Locations

- Global: `~/.pi/agent/skills/` or `~/.agents/skills/`
- Project: `.pi/skills/` or `.agents/skills/`
- Direct `.md` files are discovered in `~/.pi/agent/skills/` and `.pi/skills/`
- Directories with `SKILL.md` are discovered recursively everywhere

## Commands

```bash
/skill:name          # Load and execute skill
/skill:name args     # Load with arguments
```

Enable skill commands in settings:
```json
{ "enableSkillCommands": true }
```

## Full Documentation

- **Complete skills reference**: `references/docs/skills.md`
- **Examples in this skill**: See `SKILL.md` in this directory as a live example
