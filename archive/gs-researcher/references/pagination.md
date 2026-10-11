# Page Navigation

Navigate search result pages. Requires context from a previous search call.

## Arguments

Can be:
- `next` — go to next page
- `previous` — go to previous page
- `page N` — go to page N

## Prerequisites

Requires context from a previous search:
- `currentUrl`: the current Google Scholar search URL
- `page`: current page number (1-based)

## Steps

### 1. Calculate new URL

Google Scholar uses `start` parameter for pagination (0-indexed, increments of 10):
- Page 1: `start=0` (or omitted)
- Page 2: `start=10`
- Page 3: `start=20`

Based on arguments:
- `next`: newStart = currentStart + 10
- `previous`: newStart = max(0, currentStart - 10)
- `page N`: newStart = (N - 1) * 10

Modify the `start` parameter in the current search URL. If `start` doesn't exist in the URL, append `&start={newStart}`.

### 2. Navigate

Use `mcp__chrome-devtools__navigate_page` with the updated URL.

### 3. Extract results

Use the same extraction script as basic search (see [basic-search.md](basic-search.md)), but update the result numbering to start from `NEW_START + 1`.

### 4. Report

```
Page {page} for "{query}" ({total}):

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy}
   Data-CID: {dataCid}
...

{hasNext ? "More results available — ask me for the next page." : "No more results."}
```

## Notes

- Uses 2 tool calls: `navigate_page` + `evaluate_script`
- Google Scholar shows 10 results per page by default
- `start` parameter controls pagination offset
