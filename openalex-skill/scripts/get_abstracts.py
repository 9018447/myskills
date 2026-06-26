#!/usr/bin/env python3
"""
Query OpenAlex API for abstracts of given DOIs and save to markdown.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

BASE_URL = "https://api.openalex.org"


def make_request(params):
    """Make a request to OpenAlex API."""
    url = f"{BASE_URL}/works?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "OpenAlex-Abstract-Extractor/1.0")

    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
        return None


def get_abstract_by_doi(doi):
    """Get abstract information for a given DOI."""
    params = {"filter": f"doi:{doi}", "per-page": 1}

    data = make_request(params)

    if data and data.get("results") and len(data["results"]) > 0:
        work = data["results"][0]

        # Extract abstract
        abstract = None
        if work.get("abstract_inverted_index"):
            # Reconstruct abstract from inverted index
            inv_index = work["abstract_inverted_index"]
            word_positions = {}
            for word, positions in inv_index.items():
                for pos in positions:
                    word_positions[pos] = word

            # Sort by position and join words
            sorted_words = [
                word_positions[pos] for pos in sorted(word_positions.keys())
            ]
            abstract = " ".join(sorted_words)

        # Safely extract venue information
        venue = ""
        primary_location = work.get("primary_location")
        if primary_location:
            source = primary_location.get("source")
            if source:
                venue = source.get("display_name", "")

        # Safely extract authors
        authors = []
        for author in work.get("authorships", []):
            author_info = author.get("author")
            if author_info:
                display_name = author_info.get("display_name", "")
                if display_name:
                    authors.append(display_name)

        return {
            "title": work.get("title", ""),
            "authors": authors,
            "year": work.get("publication_year", ""),
            "doi": work.get("doi", ""),
            "abstract": abstract,
            "type": work.get("type", ""),
            "venue": venue,
        }
    return None


def extract_dois_from_yaml(yaml_file):
    """Extract DOIs from a YAML file containing bibliography entries."""
    dois = []
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            # Load all documents from the YAML file (separated by ---)
            documents = yaml.safe_load_all(f)
            for doc in documents:
                if doc and isinstance(doc, dict) and "doi" in doc:
                    doi = doc["doi"]
                    if doi:  # Skip empty DOIs
                        dois.append(doi)
        print(f"Found {len(dois)} DOIs in {yaml_file}", file=sys.stderr)
        return dois
    except FileNotFoundError:
        print(f"Error: File '{yaml_file}' not found", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python get_abstracts.py <file.yaml>", file=sys.stderr)
        print("\nExample: python get_abstracts.py co2_capture.yaml", file=sys.stderr)
        sys.exit(1)

    yaml_file = sys.argv[1]

    # Check if file is a YAML file
    if not (yaml_file.endswith(".yaml") or yaml_file.endswith(".yml")):
        print("Error: Input file must be a YAML file (.yaml or .yml)", file=sys.stderr)
        sys.exit(1)

    # Extract DOIs from YAML file
    dois = extract_dois_from_yaml(yaml_file)

    if not dois:
        print("Error: No DOIs found in the YAML file", file=sys.stderr)
        sys.exit(1)

    # Results storage
    results_with_abstract = []  # Papers with abstracts
    skipped_items = []  # Papers without abstracts or not found

    # Query each DOI
    for i, doi in enumerate(dois, 1):
        print(f"Querying DOI {i}/{len(dois)}: {doi}", file=sys.stderr)
        result = get_abstract_by_doi(doi)

        if result and result["abstract"]:
            # Has abstract
            results_with_abstract.append(result)
            print(
                f"  ✓ Found with abstract: {result['title'][:50]}...", file=sys.stderr
            )
        elif result and not result["abstract"]:
            # Found but no abstract
            skipped_items.append(
                {
                    "doi": doi,
                    "title": result["title"],
                    "reason": "No abstract available",
                }
            )
            print(
                f"  ⊘ Found but no abstract: {result['title'][:50]}...", file=sys.stderr
            )
        else:
            # Not found
            skipped_items.append(
                {"doi": doi, "title": "Unknown", "reason": "DOI not found in OpenAlex"}
            )
            print("  ✗ Not found", file=sys.stderr)

        # Be nice to the API - rate limiting
        time.sleep(0.1)

    # Generate output filename base
    input_name = Path(yaml_file).stem
    abstracts_file = f"{input_name}_abstracts.md"
    skipped_file = f"{input_name}_skipped.md"

    # Write abstracts file
    with open(abstracts_file, "w", encoding="utf-8") as f:
        f.write("# References with Abstracts\n\n")
        f.write(f"*Generated from: {yaml_file}*\n\n")
        f.write(f"*Total papers with abstracts: {len(results_with_abstract)}*\n\n")
        f.write("---\n\n")

        for result in results_with_abstract:
            f.write(f"## {result['title']}\n\n")
            f.write(f"**Authors**: {', '.join(result['authors'])}\n\n")
            f.write(f"**Year**: {result['year']}\n\n")
            f.write(f"**DOI**: {result['doi']}\n\n")
            f.write(f"**Venue**: {result['venue']}\n\n")
            f.write(f"**Type**: {result['type']}\n\n")
            f.write(f"**Abstract**:\n\n{result['abstract']}\n\n")
            f.write("---\n\n")

    print(
        f"\n✓ Wrote {len(results_with_abstract)} abstracts to: {abstracts_file}",
        file=sys.stderr,
    )

    # Write skipped file
    with open(skipped_file, "w", encoding="utf-8") as f:
        f.write("# Skipped References\n\n")
        f.write(f"*Generated from: {yaml_file}*\n\n")
        f.write(f"*Total skipped items: {len(skipped_items)}*\n\n")
        f.write("---\n\n")

        for item in skipped_items:
            f.write(f"## {item['title']}\n\n")
            f.write(f"**DOI**: {item['doi']}\n\n")
            f.write(f"**Reason**: {item['reason']}\n\n")
            f.write("---\n\n")

    print(
        f"✓ Wrote {len(skipped_items)} skipped items to: {skipped_file}",
        file=sys.stderr,
    )

    # Summary
    print("\n=== Summary ===", file=sys.stderr)
    print(f"Total DOIs processed: {len(dois)}", file=sys.stderr)
    print(f"With abstracts: {len(results_with_abstract)}", file=sys.stderr)
    print(f"Skipped: {len(skipped_items)}", file=sys.stderr)


if __name__ == "__main__":
    main()
