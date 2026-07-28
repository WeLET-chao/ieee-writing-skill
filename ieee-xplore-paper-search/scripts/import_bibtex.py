"""Import BibTeX exported from IEEE Xplore into PAPERS.md rows or JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

import bibtexparser
from bibtexparser.bparser import BibTexParser

from search_ieee import normalize_article, slugify_title, to_markdown_row


def bib_entry_to_raw(entry: dict[str, Any]) -> dict[str, Any]:
    """Convert BibTeX entry to pseudo-IEEE API shape for normalize_article."""
    title = (entry.get("title") or "").strip("{} ")
    doi = (entry.get("doi") or "").strip()
    year = (entry.get("year") or entry.get("date") or "")[:4]
    venue = (entry.get("journal") or entry.get("booktitle") or entry.get("publisher") or "")
    authors_raw = entry.get("author") or ""
    author_names = [a.strip() for a in authors_raw.replace("\n", " and ").split(" and ") if a.strip()]
    authors = [{"preferred_name": name} for name in author_names]
    url = entry.get("url") or ""
    article_number = ""
    match = re.search(r"/document/(\d+)", url)
    if match:
        article_number = match.group(1)
    return {
        "title": title,
        "doi": doi,
        "publication_year": year,
        "publication_title": venue.strip("{} "),
        "article_number": article_number,
        "authors": {"authors": authors},
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Parse IEEE Xplore BibTeX export.")
    parser.add_argument("bibtex_file", help="Path to exported .bib file.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--category", default="circuit-design")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    parser_obj = BibTexParser(common_strings=True)
    with open(args.bibtex_file, encoding="utf-8") as handle:
        library = bibtexparser.load(handle, parser=parser_obj)

    records = [normalize_article(bib_entry_to_raw(entry)) for entry in library.entries]
    records = [r for r in records if r.get("title")]

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
    print(f"Imported {len(records)} entries.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
