---
name: wos-researcher
description: Web of Science research assistant. Coordinates search, detail extraction, pagination, PDF download, and export to Zotero/RIS/BibTeX/Excel. Use when working with Web of Science for literature research, paper metadata extraction, citation analysis, or building reference libraries.
---

# Web of Science Research Assistant

Comprehensive research assistant for Web of Science (WoS) — the premier scientific citation database. Coordinates search, paper detail extraction, pagination, PDF download, and export to Zotero/RIS/BibTeX/Excel.

## Core Capabilities

1. **Search** — Search by topic, author, title, DOI, journal, or advanced WoS query with edition filtering and sorting
2. **Browse Results** — Navigate pages of search results (API-based for efficiency)
3. **Paper Details** — Extract full metadata including abstract, keywords, JIF, JCR quartile
4. **PDF Download** — Download full text via publisher links
5. **Export** — Export to Zotero (direct push), RIS, BibTeX, or Excel

## Quick Start

### Basic Search Workflow

User provides search terms:
1. Build API request with query parameters (see [search.md](references/search.md))
2. Execute via `evaluate_script` with `fetch` to WoS internal API (1 tool call)
3. Display results table with WoS IDs
4. User picks a paper → navigate to full record → extract details (see [paper-detail.md](references/paper-detail.md))
5. User wants PDF → follow publisher link (see [download.md](references/download.md))
6. User wants to save → export to Zotero or file (see [export.md](references/export.md))

### Pagination

To navigate to page N of results:
- Re-run search API with `retrieve.first` offset (see [navigation.md](references/navigation.md))
- Page 2 = first:51, Page 3 = first:101, etc. (50 records per page)

## Anti-Detection Best Practices

Every `navigate_page` call must include:
```javascript
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

**Never use `wait_for`** — always use `evaluate_script` with internal polling loops.

**Never use `take_screenshot` for data extraction** — use `evaluate_script` for structured JSON.

## Operation Principles

1. **API First, DOM Fallback** — Use `evaluate_script` with `fetch` to WoS internal API (`/api/wosnx/core/runQuerySearch`). Only fall back to URL navigation + DOM scraping when API is unavailable.

2. **WoS Accession Number as Global Key** — `WOS:000779183600001` links search → detail → export → download.

3. **Minimum Tool Calls** — Search/navigate use **1 tool call** (API via `evaluate_script`). Detail/export use 2 calls (navigate + evaluate_script).

4. **No wait_for** — Use `evaluate_script` with internal `for` loops for waiting.

5. **No take_screenshot for data** — Use `evaluate_script` to return structured JSON.

6. **SID from Performance Entries** — Extract session ID via `performance.getEntriesByType('resource')` for API calls.

## Language

Respond in the same language the user uses. For Chinese keywords in SCI/SSCI searches, translate to English (e.g., "价值共创" → "value co-creation") and inform the user.

## Detailed Reference Documentation

For implementation details, consult these reference files:

### Core Workflows
- **[search.md](references/search.md)** — Search workflows, API request building, parameter reference (database, editions, sort, field mapping), URL-based fallback
- **[paper-detail.md](references/paper-detail.md)** — Full record extraction steps, CSS selectors, JIF/JCR extraction, result presentation
- **[navigation.md](references/navigation.md)** — Pagination workflows (URL and API-based approaches)
- **[download.md](references/download.md)** — PDF download workflows, publisher link handling, access limitation troubleshooting
- **[export.md](references/export.md)** — Zotero push (preferred) and file export via UI, script features

### Internal Reference
- **[parsing.md](references/parsing.md)** — Internal reference for API response parsing and DOM scraping fallback (used by other workflows)
- **[wos-dom.md](references/wos-dom.md)** — Complete DOM & URL reference: CSS selectors, URL patterns, field tags, internal API endpoints

## Common User Tasks

| Task | Command/Action | Reference |
|------|----------------|-----------|
| Search by topic | "Search WoS for deep learning" | [search.md](references/search.md) |
| Search by author | "Find papers by Hinton" | [search.md](references/search.md) |
| Get paper details | "Show details for WOS:000779183600001" | [paper-detail.md](references/paper-detail.md) |
| Download PDF | "Download PDF for WOS:000779183600001" | [download.md](references/download.md) |
| Export to Zotero | "Export to Zotero" | [export.md](references/export.md) |
| Export to RIS | "Export to RIS file" | [export.md](references/export.md) |
| Next page | "Show page 2" or "Next page" | [navigation.md](references/navigation.md) |

## API Quick Reference

### Search/Paginate API (preferred)

- **Endpoint**: `POST /api/wosnx/core/runQuerySearch?SID={SID}`
- **Response**: NDJSON — parse `searchInfo` (total count) and `records` (paper data)
- **Editions**: `WOS.SCI`, `WOS.SSCI`, `WOS.CPCI-S`, `WOS.CPCI-SSH`
- **Sort**: `relevance`, `times-cited-descending`, `date-descending`, `date-ascending`, `usage-count-last-180-days-descending`
- **Pagination**: Set `retrieve.first` (1-based offset). Page 2 = first:51, Page 3 = first:101

### queryJson Format

```json
[
  {"rowBoolean":null,"rowField":"TS","rowText":"deep learning"},
  {"rowBoolean":"AND","rowField":"AU","rowText":"Hinton"},
  {"rowBoolean":"AND","rowField":"PY","rowText":"2020-2025"}
]
```

First row: `rowBoolean` is always `null`. Subsequent rows: `AND`, `OR`, or `NOT`.

### Field Tags (for queryJson rowField)

| Tag | Field |
|-----|-------|
| TS | Topic (title + abstract + keywords) |
| TI | Title |
| AU | Author |
| DO | DOI |
| SO | Publication Titles |
| PY | Year Published |
| ALL | All Fields |

See [wos-dom.md](references/wos-dom.md) for complete field tag reference.

## Troubleshooting

### SID Lost (API returns `no_session`)

After navigating to an external publisher site, WoS performance entries are cleared. Recover by:

1. Navigate to any WoS page (e.g., `/wos/woscc/basic-search`) to re-establish session
2. Then retry the API call

Or use URL-based fallback (see [search.md](references/search.md)).

### PDF Download Fails

- **Login required**: Publisher requires authentication. Try via institutional VPN/WebVPN.
- **Paywall**: Paper requires subscription.
- **Cross-origin**: The `a.download` trick only works on same-origin pages.

See [download.md](references/download.md) for detailed troubleshooting.

### Zotero Push Fails

- **Zotero not running**: Start Zotero desktop application
- **Connection refused**: Zotero must be running on localhost:23119

See [export.md](references/export.md) for script usage.

## Bundled Resources

### Scripts
- **[scripts/push_to_zotero.py](scripts/push_to_zotero.py)** — Push WoS records to Zotero via HTTP API

### References
All reference files in `references/` contain detailed implementation guides loaded on demand.
