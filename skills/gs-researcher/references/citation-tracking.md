# Citation Tracking (Cited By)

Find all papers that cite a given paper. Uses Google Scholar's `cites` parameter with the paper's cluster ID (data-cid).

## Arguments

Can be:
- A `data-cid` from a previous search result (e.g., `TFS2GgoGiNUJ`)
- A paper title (will search first to find the data-cid)

## Steps

### Step 1: Resolve data-cid

**If argument is a data-cid** (alphanumeric string, no spaces): use it directly.

**If argument is a title or description**: first search to find the data-cid:
1. Use basic search with the title as keywords
2. Match the target paper in results by title similarity
3. Extract its `dataCid`

### Step 2: Navigate to "Cited by" page

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://scholar.google.com/scholar?cites={DATA_CID}&hl=en&num=10`

Replace `{DATA_CID}` with the resolved cluster ID.

### Step 3: Extract citing papers

Use the same extraction script as basic search (see [basic-search.md](basic-search.md)).

### Step 4: Report

```
Papers citing [{original paper title}] (data-cid: {DATA_CID}):
{total}

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy}
   Data-CID: {dataCid}
...
```

## Follow-up

- **See more citing papers**: use pagination (works on cited-by pages too)
- **Export citing papers**: use export function with the data-cid(s)
- **Recursive citation tracking**: apply citation tracking on any of the citing papers

## Notes

- Uses 2-3 tool calls: optional search + `navigate_page` + `evaluate_script`
- The `cites` parameter uses the cluster ID (data-cid), NOT a DOI or paper ID
- Cited-by pages support the same pagination as regular search (`start` parameter)
- Citation count on Google Scholar is typically higher than PubMed because it includes non-PubMed sources (books, theses, preprints, etc.)
