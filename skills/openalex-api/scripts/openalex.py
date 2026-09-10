#!/usr/bin/env python3
import urllib.request
import urllib.parse
import urllib.error
import json
import argparse
import os
import sys

BASE_URL = "https://api.openalex.org"

def get_api_key():
    return os.environ.get("OPENALEX_API_KEY")

def make_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    
    query_params = {}
    if params:
        query_params.update(params)
    
    api_key = get_api_key()
    if api_key:
        query_params['api_key'] = api_key
    else:
        # Polite pool usage
        query_params['mailto'] = 'gemini-cli-agent@google.com' 

    if query_params:
        url += "?" + urllib.parse.urlencode(query_params)

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Gemini-CLI-OpenAlex-Skill/1.0')

    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode()
            print(f"Details: {err_body}", file=sys.stderr)
        except:
            pass
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
        sys.exit(1)

def command_get(args):
    entity_id = args.id
    if not entity_id:
        print("Error: --id is required for 'get' command", file=sys.stderr)
        sys.exit(1)
    
    # Clean ID if it's a full URL
    if entity_id.startswith("https://openalex.org/"):
        entity_id = entity_id.replace("https://openalex.org/", "")
        
    data = make_request(entity_id)
    print(json.dumps(data, indent=2))

def command_list(args):
    endpoint = args.entity_type
    params = {
        'per_page': args.limit,
    }
    
    if args.search:
        params['search'] = args.search
    
    if args.filter:
        params['filter'] = args.filter

    data = make_request(endpoint, params)
    
    if 'results' in data:
        print(json.dumps(data['results'], indent=2))
        print(f"\n--- Meta ---\nCount: {data['meta']['count']}")
    else:
        # Some endpoints might behave differently, but standard lists have 'results'
        print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Interact with OpenAlex API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Get single entity
    get_parser = subparsers.add_parser("get", help="Get a single entity by ID")
    get_parser.add_argument("--id", required=True, help="OpenAlex ID (e.g., W2741809807)")

    # List/Search entities
    list_parser = subparsers.add_parser("list", help="List or search entities")
    list_parser.add_argument("entity_type", choices=["works", "authors", "institutions", "venues", "concepts", "publishers", "funders"], help="Type of entity to search")
    list_parser.add_argument("--search", help="Full-text search query")
    list_parser.add_argument("--filter", help="Filter string (e.g., 'type:article,from_publication_date:2020-01-01')")
    list_parser.add_argument("--limit", type=int, default=5, help="Number of results to return (default: 5)")

    args = parser.parse_args()

    if args.command == "get":
        command_get(args)
    elif args.command == "list":
        command_list(args)

if __name__ == "__main__":
    main()
