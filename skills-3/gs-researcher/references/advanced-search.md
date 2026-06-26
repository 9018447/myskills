# Advanced Search

Construct and execute a Google Scholar search using URL parameters based on the user's natural language description.

## Arguments

Natural language description of the search criteria, e.g.:
- "Search for Einstein's papers on relativity after 2020"
- "Find reviews about CRISPR in Nature"
- "Search for exact phrase 'machine learning' in title only"

## Step 1: Parse search criteria into URL parameters

Map the user's intent to Google Scholar URL parameters:

| Criteria | Parameter | Example |
|----------|-----------|---------|
| Keywords | `q` | `q=gastric+cancer` |
| Author | `as_sauthors` | `as_sauthors="Albert Einstein"` |
| Journal/Source | `as_publication` | `as_publication=Nature` |
| Start year | `as_ylo` | `as_ylo=2020` |
| End year | `as_yhi` | `as_yhi=2025` |
| Exact phrase | `as_epq` | `as_epq=machine+learning` |
| Any of these words (OR) | `as_oq` | `as_oq=immunotherapy+checkpoint` |
| Exclude words | `as_eq` | `as_eq=review` |
| Search scope | `as_occt` | `as_occt=title` (title only) / `as_occt=any` (anywhere) |
| Results per page | `num` | `num=10` (default) or `num=20` (max) |
| Language | `hl` | `hl=en` or `hl=zh-CN` |

**Construction examples:**
- "Einstein 2020 年以后在 Nature 上的论文" → `scholar?as_sauthors=Einstein&as_publication=Nature&as_ylo=2020&hl=en`
- "标题包含 CRISPR 的论文" → `scholar?q=CRISPR&as_occt=title&hl=en`
- "精确搜索 'deep learning' 排除 review" → `scholar?as_epq=deep+learning&as_eq=review&hl=en`
- "搜索 immunotherapy 或 checkpoint 相关论文" → `scholar?as_oq=immunotherapy+checkpoint&hl=en`

**Notes:**
- When `as_sauthors`, `as_publication`, etc. are used, `q` can be omitted or used for additional keywords
- Always include `hl=en` for consistent results
- Use `num=10` (default) to minimize CAPTCHA risk

## Step 2: Navigate

Use `mcp__chrome-devtools__navigate_page`:
- url: `https://scholar.google.com/scholar?{CONSTRUCTED_PARAMS}`

## Step 3: Extract results

Use the same extraction script as basic search (see [basic-search.md](basic-search.md)).

## Step 4: Report

Always show the constructed URL parameters so the user understands how the query was built.

## Notes

- Uses 2 tool calls: `navigate_page` + `evaluate_script`
- Google Scholar does NOT support publication type filtering (review, clinical trial, etc.) — use keywords instead
- Impact factor is not available in Google Scholar — use citation count as a proxy
- The key difference from basic search is URL parameter construction — this function translates natural language to Google Scholar query parameters
