"""Fetch a single IEEE record by DOI using the Metadata API."""

from __future__ import annotations

import argparse
import json
import os
import sys

from ieee_api import get_with_key_failover, load_api_keys
from search_ieee import normalize_article, to_markdown_row


def fetch_by_doi(doi: str) -> dict[str, str]:
    """Return normalized record for one DOI."""
    response = get_with_key_failover({"doi": doi, "max_records": 1})
    articles = response.json().get("articles") or []
    if not articles:
        msg = f"No IEEE record found for DOI {doi}"
        raise ValueError(msg)
    return normalize_article(articles[0])


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Fetch one IEEE Xplore record by DOI.")
    parser.add_argument("--doi", required=True, help="Paper DOI, e.g. 10.1109/LSSC.2020.3007580")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--category", default="circuit-design")
    args = parser.parse_args()

    if not load_api_keys():
        print("Error: No IEEE API keys configured.", file=sys.stderr)
        return 1

    record = fetch_by_doi(args.doi.strip())
    if args.format == "markdown":
        print(to_markdown_row(record, args.category))
    else:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
