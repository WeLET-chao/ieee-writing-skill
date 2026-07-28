"""Search IEEE Xplore Metadata API and emit JSON or PAPERS.md rows."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any
from urllib.parse import quote

from ieee_api import get_with_key_failover, load_api_keys


def slugify_title(title: str, max_len: int = 80) -> str:
    """Convert a paper title to a filesystem slug."""
    text = title.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len].rstrip("-")


def format_authors(authors: list[dict[str, Any]] | None) -> str:
    """Format author list as 'First Author et al.' when multiple."""
    if not authors:
        return "—"
    names = [a.get("preferred_name") or a.get("full_name") or "" for a in authors]
    names = [n.strip() for n in names if n.strip()]
    if not names:
        return "—"
    if len(names) == 1:
        return names[0]
    return f"{names[0]} et al."


def normalize_article(raw: dict[str, Any]) -> dict[str, str]:
    """Map IEEE API article record to index fields."""
    title = (raw.get("title") or raw.get("article_title") or "").strip()
    doi = (raw.get("doi") or "").strip()
    article_number = str(raw.get("article_number") or raw.get("arnumber") or "")
    year = str(raw.get("publication_year") or raw.get("publication_date", "")[:4] or "")
    venue = (raw.get("publication_title") or raw.get("publisher") or "—").strip()
    xplore_url = f"https://ieeexplore.ieee.org/document/{article_number}" if article_number else ""
    if doi and not doi.startswith("http"):
        doi_url = f"https://doi.org/{doi}"
    else:
        doi_url = doi
    return {
        "title": title,
        "authors": format_authors(raw.get("authors", {}).get("authors")),
        "year": year or "—",
        "venue": venue,
        "doi": doi,
        "doi_url": doi_url,
        "article_number": article_number,
        "xplore_url": xplore_url,
        "slug": slugify_title(title) if title else "",
        "is_open_access": str(raw.get("is_open_access", False)).lower(),
    }


def search_ieee(
    query: str,
    *,
    start_year: int | None = None,
    end_year: int | None = None,
    publication_title: str | None = None,
    max_records: int = 25,
    start_record: int = 1,
) -> list[dict[str, str]]:
    """Query IEEE Xplore Metadata API and return normalized records."""
    params: dict[str, str | int] = {
        "querytext": query,
        "max_records": max_records,
        "start_record": start_record,
    }
    if start_year is not None:
        params["start_year"] = start_year
    if end_year is not None:
        params["end_year"] = end_year
    if publication_title:
        params["publication_title"] = publication_title

    response = get_with_key_failover(params)
    payload = response.json()
    articles = payload.get("articles") or []
    return [normalize_article(a) for a in articles]


def to_markdown_row(record: dict[str, str], category: str) -> str:
    """Format one PAPERS.md table row for a pending download."""
    doi_cell = "—"
    if record.get("doi"):
        short = record["doi"]
        url = record.get("doi_url") or f"https://doi.org/{short}"
        doi_cell = f"[{short}]({url})"
    pdf_cell = "—"
    if record.get("xplore_url"):
        pdf_cell = f"[IEEE Xplore]({record['xplore_url']})"
    return (
        f"| {record['title']} | {record['authors']} | {record['year']} | "
        f"{record['venue']} | {category} | {doi_cell} | — | {pdf_cell} |"
    )


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Search IEEE Xplore Metadata API.")
    parser.add_argument("--query", required=True, help="Boolean querytext string.")
    parser.add_argument("--start-year", type=int, default=None)
    parser.add_argument("--end-year", type=int, default=None)
    parser.add_argument("--publication-title", default=None)
    parser.add_argument("--max-records", type=int, default=25)
    parser.add_argument("--start-record", type=int, default=1)
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--category",
        default="circuit-design",
        help="Category tag(s) for markdown rows (comma-separated).",
    )
    parser.add_argument("--output", default=None, help="Write output to file instead of stdout.")
    args = parser.parse_args()

    if not load_api_keys():
        print(
            "Error: No IEEE API keys configured.\n"
            "Add IEEE_XPLORE_API_KEY (and optional IEEE_XPLORE_API_KEY_BACKUP) to "
            "scripts/env.local.sh, or use import_bibtex.py on a manual Xplore export.",
            file=sys.stderr,
        )
        return 1

    records = search_ieee(
        args.query,
        start_year=args.start_year,
        end_year=args.end_year,
        publication_title=args.publication_title,
        max_records=args.max_records,
        start_record=args.start_record,
    )

    if args.format == "json":
        text = json.dumps(records, indent=2, ensure_ascii=False)
    else:
        lines = [to_markdown_row(r, args.category) for r in records]
        text = "\n".join(lines) + ("\n" if lines else "")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
