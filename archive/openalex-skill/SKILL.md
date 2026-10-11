---
name: openalex-api
description: Access the OpenAlex database to search for scholarly works, authors, institutions, and more. Use this skill when the user needs to find academic papers, research citations, author bibliographies, or institutional research output. It supports searching, filtering (by year, type, journal, etc.), and retrieving detailed metadata for entities. It also includes a crawler to scrape abstracts directly from DOI landing pages.
---

# OpenAlex API Skill

This skill allows querying the OpenAlex database of scholarly records. It uses a helper Python script to interact with the API.

## Usage

### 1. Searching & Listing (OpenAlex API)

Use the `list` command to search for entities (works, authors, institutions, etc.).

**Syntax:**
```bash
./scripts/openalex.py list <entity_type> [options]
```

**Common Entity Types:**
- `works` (Papers, articles, books)
- `authors` (Researchers)
- `institutions` (Universities, companies)
- `sources` (Journals, conferences)
- `concepts` (Topics)

**Options:**
- `--search "query"`: Full-text search.
- `--filter "attribute:value"`: Filter results (see [filters.md](references/filters.md)).
- `--limit N`: Number of results to return (default 5).

**Examples:**

*Search for papers about "machine learning" published in 2023:*
```bash
./scripts/openalex.py list works --search "machine learning" --filter "publication_year:2023" --limit 3
```

*Find an author by name:*
```bash
./scripts/openalex.py list authors --search "Yann LeCun"
```

### 2. Retrieving Single Entities (OpenAlex API)

Use the `get` command when you have a specific OpenAlex ID.

**Syntax:**
```bash
./scripts/openalex.py get --id <OpenAlex_ID>
```

**Example:**
```bash
./scripts/openalex.py get --id W2741809807
```

### 3. Scraping Abstracts (DOI Crawler)

Use the `scrape_abstracts.py` tool to extract abstracts directly from DOI landing pages (publisher sites). This is useful when the OpenAlex API data is missing the abstract or you need to verify content from the source.

**Syntax:**
```bash
./scripts/scrape_abstracts.py <doi1> <doi2> ...
# OR
./scripts/scrape_abstracts.py --file <path_to_doi_list_file>
```

**Example:**
```bash
./scripts/scrape_abstracts.py 10.1038/nature14539 10.1109/CVPR.2016.90
```

**Output:**
Returns a JSON object mapping DOIs to their extracted abstracts.

## Configuration

If the user provides an OpenAlex API Key, set it as an environment variable to get higher rate limits and faster response times.
```bash
export OPENALEX_API_KEY="your_key_here"
```

## Advanced Filtering

For detailed filter syntax and common attributes, see [references/filters.md](references/filters.md).
