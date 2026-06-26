# Settings Guide

Quick reference for configuring pi.

## Settings Files

| Scope | Path |
|-------|------|
| Global | `~/.pi/agent/settings.json` |
| Project | `.pi/settings.json` |

## Key Settings

```json
{
  "defaultProvider": "anthropic",
  "defaultModel": "claude-sonnet-4-20250514",
  "defaultThinkingLevel": "medium",
  "theme": "dark",
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  },
  "retry": {
    "enabled": true,
    "maxRetries": 3,
    "baseDelayMs": 2000
  }
}
```

## Common Configuration Tasks

| Task | Setting |
|------|---------|
| Change model | `defaultModel` |
| Adjust thinking | `defaultThinkingLevel` / `thinkingBudgets` |
| Custom theme | `theme` |
| Disable compaction | `compaction.enabled: false` |
| Add skills paths | `skills: ["~/.claude/skills"]` |
| Custom commands | `commands: [...]` |

## Full Documentation

- **Complete settings reference**: `references/docs/settings.md`
- **Keybindings**: `references/docs/keybindings.md`
- **Models**: `references/docs/models.md`
