---
name: gs-researcher
description: Google Scholar Research Assistant - comprehensive academic literature search, citation tracking, and Zotero export. Use proactively when the user needs to search Google Scholar, find papers, track citations, get full-text access, or manage references. Supports basic keyword search, advanced filtered search (author, journal, date range), citation chain tracking, full-text link resolution (PDF, DOI, Sci-Hub), page navigation, and batch export to Zotero.
---

# Google Scholar Research Assistant

Research assistant for academic literature via Google Scholar. Operates Chrome DevTools to scrape DOM data—Google Scholar has no public API.

## Quick Start

See [references/](references/) for detailed function documentation:

- **Basic search** — [basic-search.md](references/basic-search.md)
- **Advanced search** — [advanced-search.md](references/advanced-search.md)
- **Citation tracking** — [citation-tracking.md](references/citation-tracking.md)
- **Full-text access** — [fulltext.md](references/fulltext.md)
- **Page navigation** — [pagination.md](references/pagination.md)
- **Export to Zotero** — [export.md](references/export.md)

## Prerequisites

### Chrome DevTools Setup

1. Use `mcp__chrome-devtools__list_pages` to find open Chrome tabs
2. Use `mcp__chrome-devtools__select_page` to select a Google Scholar tab (URL contains `scholar.google.com`)
3. If no Google Scholar tab exists, use `mcp__chrome-devtools__new_page` to open `https://scholar.google.com/`

### DOM Scraping Strategy

All data extraction uses `evaluate_script` with CSS selectors:

| Selector | Purpose |
|----------|---------|
| `#gs_res_ccl .gs_r.gs_or.gs_scl` | Result items |
| `.gs_rt a` | Title + link |
| `.gs_a` | Authors, journal, year |
| `.gs_rs` | Abstract snippet |
| `.gs_fl a[href*="cites"]` | "Cited by N" link |
| `.gs_ggs a` | Full-text PDF/HTML link |
| `data-cid` attribute | Cluster ID (primary key) |
| `#gs_captcha_ccl` | CAPTCHA detection |

## Core Workflows

### 1. Literature Search

```
User: "搜索关于 CRISPR 的论文"
→ Execute basic search
→ Present results with title, authors, journal, year, citation count
```

### 2. Advanced Search

```
User: "搜索 2020 年以后 Nature 上关于 cancer 的论文"
→ Execute advanced search → construct URL with as_publication=Nature&as_ylo=2020&q=cancer
→ Present results
```

### 3. Citation Tracking

```
User: "谁引用了这篇论文"
→ Execute citation tracking with dataCid from previous results
→ Present citing papers
```

### 4. Full-Text Access

```
User: "帮我找这篇论文的全文"
→ Resolve full-text links: direct PDF, DOI, Sci-Hub, publisher page
→ Present options, open preferred link on request
```

### 5. Export to Zotero

```
User: "把搜索结果保存到 Zotero"
→ Execute export with dataCid(s) (batch supported)
→ Report success
```

### 6. Combined Workflow

```
User: "搜索最新的 gastric cancer 论文，找出引用最高的，帮我存到 Zotero"
→ Advanced search "gastric cancer" (sort by relevance, recent years)
→ Identify highest-cited paper
→ Export to Zotero
```

## Output Format

### Search Results

```
Searched Google Scholar for "{keyword}": {total}

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy} | [Full text]({fullTextUrl})
   Data-CID: {dataCid}

2. ...
```

### Citation Tracking

```
Papers citing [{title}] (data-cid: {cid}):
{total}

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy}

2. ...
```

### Full-Text Links

```
## Full Text Links — {title}

**Authors:** {authors} | {journalYear}

**Direct Full Text:**
- [PDF] https://example.com/paper.pdf

**Publisher Page:**
- https://publisher.com/article

**DOI:**
- https://doi.org/10.xxxx/xxxx

**Sci-Hub:**
- https://sci-hub.ru/10.xxxx/xxxx
```

## CAPTCHA Handling

Google Scholar aggressively detects automated access. When any function returns `{error: 'captcha'}`:

1. **Stop all operations immediately**
2. **Tell the user**: "Google Scholar is requesting CAPTCHA verification. Please complete the verification in your browser, then tell me to continue."
3. **Wait for user confirmation** before retrying
4. **Do NOT** retry automatically — this will make things worse

## Behavioral Rules

1. **DOM scraping only** — No API available. All extraction via `evaluate_script` + CSS selectors
2. **`data-cid` is the key** — Track and use cluster IDs for all cross-referencing between functions
3. **Always show citation count** — This is Google Scholar's key advantage over PubMed
4. **Handle CAPTCHA gracefully** — Stop and ask user to verify manually
5. **Match user's language** — Chinese query → Chinese response. English query → English response
6. **Pace operations** — Wait between requests. Never make rapid successive page loads
7. **Navigate for visual context** — Always `navigate_page` so the user can see the Google Scholar page in their browser
8. **Highlight full-text links** — When a paper has a free PDF/HTML link, always mention it

## Common Patterns

### Result Numbering

Results should be numbered starting from 1, but when using pagination, continue the numbering from where the previous page left off (e.g., page 2 results start at 11, page 3 at 21).

### Data-CID Tracking

The `data-cid` (cluster ID) is the unique identifier for papers in Google Scholar. Always preserve and report this value — it's used for:
- Citation tracking (`cites={dataCid}`)
- Export to Zotero
- Cross-referencing between functions

### Full-Text Link Prioritization

When presenting full-text options, use this priority:
1. Direct PDF/HTML (usually free, from `.gs_ggs a`)
2. DOI link (may require subscription)
3. Sci-Hub (fallback)
4. Publisher page
