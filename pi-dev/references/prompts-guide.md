# Prompt Templates Guide

Quick reference for creating pi prompt templates.

## Location

- Global: `~/.pi/agent/prompts/*.md`
- Project: `.pi/prompts/*.md`

## Format

Frontmatter + markdown body:

```markdown
---
name: my-prompt
description: What this prompt does
---

# Instructions

Your specialized instructions here.
```

## Usage

Reference in code:
```typescript
pi.sendMessage({ role: "user", content: "Use prompt:my-prompt" });
```

Or via settings:
```json
{ "prompts": ["./my-prompt.md"] }
```

## Full Documentation

- **Complete prompt reference**: `references/docs/prompt-templates.md`
