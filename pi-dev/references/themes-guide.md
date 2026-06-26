# Themes Guide

Quick reference for creating pi themes.

## Theme Location

- Global: `~/.pi/agent/themes/*.json`
- Project: `.pi/themes/*.json`

## Theme Format

```json
{
  "$schema": "https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json",
  "name": "my-theme",
  "vars": {
    "primary": "#00aaff",
    "secondary": 242
  },
  "colors": {
    "accent": "primary",
    "border": "primary",
    "success": "#00ff00",
    "error": "#ff0000",
    "warning": "#ffff00",
    "text": "",
    "muted": "secondary",
    "dim": 240,
    "selectedBg": "#2d2d30",
    "userMessageBg": "#2d2d30",
    "mdHeading": "#ffaa00",
    "mdLink": "primary",
    "mdCode": "#00ffff",
    "syntaxKeyword": "primary",
    "syntaxFunction": "#00aaff",
    "syntaxString": "#00ff00"
  }
}
```

## Color Values

- Hex: `#00aaff`
- ANSI 256: `242`
- Reference var: `"primary"`
- Empty string `""`: inherits terminal default

## Activation

Select via `/settings` or set `"theme": "my-theme"` in settings.json.

**Hot reload**: Editing the active theme file reloads it automatically.

## Full Documentation

- **Complete theme reference**: `references/docs/themes.md`
