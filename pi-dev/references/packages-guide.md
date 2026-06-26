# Packages Guide

Quick reference for creating pi packages.

## Package Structure

```
my-pi-package/
├── package.json          # npm package + pi manifest
├── index.ts              # Extension entry (optional)
├── skills/               # Skills (optional)
├── themes/               # Themes (optional)
└── prompts/              # Prompt templates (optional)
```

## package.json Pi Manifest

```json
{
  "name": "my-pi-package",
  "pi": {
    "extensions": ["index.ts"],
    "skills": ["skills/"],
    "themes": ["themes/"],
    "prompts": ["prompts/"]
  }
}
```

Or use `pi.` prefixed keys:
```json
{
  "pi.extensions": ["index.ts"],
  "pi.skills": ["skills/"]
}
```

## Installation

```bash
pi --install /path/to/package
# or from npm
pi --install my-pi-package
```

## Full Documentation

- **Complete packages reference**: `references/docs/packages.md`
