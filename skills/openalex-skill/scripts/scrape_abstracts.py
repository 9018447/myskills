#!/usr/bin/env python3
import urllib.request
import urllib.parse
import urllib.error
import re
import sys
import argparse
import html
import ssl
import time

# Regex patterns for common abstract meta tags
META_PATTERNS = [
    re.compile(r'<meta\s+name=["\']citation_abstract["\']\s+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta\s+name=["\']dc.description["\']\s+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
]

def clean_html(raw_html):
    """Remove HTML tags and decode entities."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext).strip()

def get_abstract(doi):
    """
    Fetches the abstract for a given DOI by following the DOI redirect
    and scraping meta tags from the landing page.
    """
    if doi.startswith("http"):
        url = doi
    else:
        url = f"https://doi.org/{doi}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    try:
        # Create a context that ignores SSL errors if necessary (use with caution, but helpful for scraping)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers=headers)
        
        # Follow redirects automatically (urllib does this by default)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            final_url = response.geturl()
            # Read content, decoding with utf-8, ignore errors
            content = response.read().decode('utf-8', errors='ignore')

            # Try each pattern
            for pattern in META_PATTERNS:
                match = pattern.search(content)
                if match:
                    raw_abstract = match.group(1)
                    # Basic validation: ignore if it's too short to be an abstract (e.g. "Home page")
                    if len(raw_abstract) > 50:
                        return clean_html(raw_abstract)
            
            # If no meta tag found, return None or a specific message
            return None

    except urllib.error.HTTPError as e:
        return f"Error: HTTP {e.code}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Scrape abstracts from DOI landing pages.")
    parser.add_argument("dois", nargs='*', help="List of DOIs to scrape")
    parser.add_argument("--file", help="File containing DOIs (one per line)")
    
    args = parser.parse_args()
    
    doi_list = args.dois
    if args.file:
        try:
            with open(args.file, 'r') as f:
                doi_list.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"Error: File {args.file} not found.", file=sys.stderr)
            sys.exit(1)

    if not doi_list:
        print("Usage: ./scrape_abstracts.py <doi1> <doi2> ... OR ./scrape_abstracts.py --file dois.txt")
        sys.exit(1)

    results = {}
    for doi in doi_list:
        # print(f"Fetching: {doi}...", file=sys.stderr)
        abstract = get_abstract(doi)
        if abstract:
             results[doi] = abstract
        else:
             results[doi] = "Abstract not found or extraction failed."
        # Be polite
        time.sleep(1)

    # Print results as JSON
    import json
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
