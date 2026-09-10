---
name: academic-paper-access
description: "Academic paper discovery and access workflows — search, navigate publisher restrictions, and guide users to institutional access"
---

# Academic Paper Access

Help users find and access academic papers, handle publisher anti-scraping measures, and provide alternative access routes.

## Trigger Conditions
User asks for:
- Latest papers from a specific journal/conference
- Papers from a particular year or venue
- Access to paywalled content (when they have institutional access)
- Literature search on a research topic

## Workflow

### 1. Understand the request
- **Target venue**: Journal name (e.g., "AIChE Journal"), conference (e.g., "NeurIPS"), or preprint server (arXiv)
- **Timeframe**: Latest issue, specific year, or date range
- **Access context**: User has institutional subscription? Open access preferred?

### 2. Search strategy (in order of preference)

#### For preprints/open access:
```bash
# arXiv API (no anti-scraping)
curl -s "https://export.arxiv.org/api/query?search_query=<query>&max_results=20&sortBy=submittedDate&sortOrder=descending"

# Google Scholar (may hit rate limits)
# Use browser_navigate to: https://scholar.google.com
```

#### For paywalled journals:
**DO NOT** attempt direct scraping of publisher sites (Wiley, Elsevier, Springer, ACS). They use:
- Cloudflare/ bot detection
- Session-based authentication
- Aggressive rate limiting

**Instead**, provide direct URLs and guide the user:
1. Give the journal homepage URL
2. Instruct user to connect to campus VPN/network
3. Point them to "Latest Issue" or "Current" sections
4. Mention they can download PDFs directly with institutional access

### 3. Common academic publisher URLs

See `references/publisher-urls.md` for comprehensive list of journal portals, preprint servers, and access tools.

### 4. Alternative access methods
- **Unpaywall** browser extension (legal open access versions)
- **Google Scholar** (shows "PDF" links to institutional copies)
- **ResearchGate** (authors sometimes upload copies)
- **Preprint servers** (arXiv, bioRxiv, chemRxiv) for early versions

## Pitfalls

❌ **Don't**: Attempt to scrape paywalled publisher sites directly
- Will hit Cloudflare/bot detection
- Browser tools often fail with these protections
- Vision analysis may fail due to access restrictions

✅ **Do**: Use APIs where available (arXiv, PubMed), provide direct URLs for institutional access

❌ **Don't**: Promise full-text access when user lacks subscription
- Be upfront: "This requires institutional access"

✅ **Do**: Suggest alternatives (preprints, author copies, interlibrary loan)

## Language considerations
- If user communicates in Chinese, respond in Chinese
- Maintain technical accuracy regardless of language
- Use platform-appropriate formatting (WeChat supports Markdown)

## Verification
After providing access guidance:
- Ask if user successfully accessed the content
- Offer to help search for specific topics/authors within the venue
- Suggest follow-up: literature review, citation analysis, etc.
