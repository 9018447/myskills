---
name: wos-researcher
description: >
  Web of Science research assistant for paper search, metadata extraction, PDF download, and citation export.
  Uses WoS internal API via Chrome DevTools for efficient, anti-detection browsing.
  Use this skill when the user wants to search academic papers, extract paper metadata, download PDFs,
  export citations to Zotero/RIS/BibTeX, or interact with Web of Science in any way.
---

# Web of Science Research Assistant

A comprehensive skill for interacting with Web of Science (WoS) through Chrome DevTools MCP.

## Quick Start

1. **Search papers**: `/wos-search deep learning --edition SSCI --sort citations`
2. **Get paper details**: `/wos-paper-detail WOS:000295471900004`
3. **Export to Zotero**: `/wos-export zotero`
4. **Navigate results**: `/wos-navigate-pages 2`
5. **Download PDF**: `/wos-download WOS:000295471900004`

## Core Workflow

```
Search → Browse Results → Paper Detail → Export/Download
   │           │              │              │
   └─ 1 call   └─ 1 call     └─ 2 calls    └─ 2-3 calls
      (API)        (API)         (nav+JS)      (nav+JS)
```

## Anti-Detection Rules

**Critical**: Every navigation must include:
```javascript
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

- Never use `wait_for` — use `evaluate_script` with internal polling
- Never use `take_screenshot` for data — use `evaluate_script` for structured JSON

## Operation Principles

1. **API First** — Use WoS internal API (`/api/wosnx/core/runQuerySearch`) via `evaluate_script`
2. **WoS ID as Key** — `WOS:000779183600001` links search → detail → export → download
3. **Minimum Calls** — Search/paginate: 1 call. Detail/export: 2 calls.

## Sub-Skills

| Skill | Purpose | Calls |
|-------|---------|-------|
| `wos-search` | Paper search with filters | 1 |
| `wos-paper-detail` | Full metadata extraction | 2 |
| `wos-navigate-pages` | Pagination | 1 |
| `wos-download` | PDF download | 3-4 |
| `wos-export` | Citation export | 2-3 |
| `wos-parse-results` | Internal parser | - |

## Detailed References

For comprehensive documentation, read these files as needed:

- **[API Reference](references/api-reference.md)** — Endpoints, request/response formats, SID extraction
- **[URL Patterns](references/url-patterns.md)** — All WoS URL patterns and database codes
- **[Troubleshooting](references/troubleshooting.md)** — Common issues and solutions

## Example: Complete Workflow

```bash
# 1. Search for papers
/wos-search value co-creation --edition SSCI --sort citations

# 2. View paper details
/wos-paper-detail WOS:000295471900004

# 3. Export to Zotero
/wos-export zotero

# 4. Download PDF
/wos-download WOS:000295471900004
```

## Prerequisites

1. Chrome DevTools MCP server running
2. Chrome browser logged into Web of Science
3. Python 3 (optional, for Zotero)
4. Zotero desktop (optional, for citation management)
