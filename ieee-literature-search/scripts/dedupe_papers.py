"""Dedupe candidate papers against an existing docs/PAPERS.md index."""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


def normalize_title(title: str) -> str:
    """Normalize title for fuzzy comparison."""
    text = title.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def extract_dois_from_index(index_text: str) -> set[str]:
    """Extract DOIs from markdown links in PAPERS.md."""
    dois: set[str] = set()
    for match in re.finditer(r"doi\.org/([^\s\)\]]+)", index_text, flags=re.IGNORECASE):
        dois.add(match.group(1).lower().rstrip(").,"))
    for match in re.finditer(r"10\.\d{4,}/[^\s\|\]\)]+", index_text):
        dois.add(match.group(0).lower().rstrip(").,"))
    return dois


def extract_titles_from_index(index_text: str) -> list[str]:
    """Extract first-column titles from markdown table rows."""
    titles: list[str] = []
    for line in index_text.splitlines():
        if not line.startswith("|") or line.startswith("| Title") or line.startswith("|-"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and not cells[0].startswith("*"):
            titles.append(cells[0])
    return titles


def extract_xplore_ids(index_text: str) -> set[str]:
    """Extract IEEE document numbers from Xplore URLs."""
    ids: set[str] = set()
    for match in re.finditer(r"ieeexplore\.ieee\.org/document/(\d+)", index_text):
        ids.add(match.group(1))
    return ids


def is_duplicate(
    record: dict[str, Any],
    existing_dois: set[str],
    existing_titles: list[str],
    existing_xplore_ids: set[str],
    *,
    title_threshold: float = 0.9,
) -> tuple[bool, str]:
    """Return whether record duplicates index content and why."""
    doi = (record.get("doi") or "").lower().strip()
    if doi and doi in existing_dois:
        return True, f"DOI {doi}"

    article_number = str(record.get("article_number") or "")
    if article_number and article_number in existing_xplore_ids:
        return True, f"Xplore {article_number}"

    title = record.get("title") or ""
    norm = normalize_title(title)
    for existing in existing_titles:
        if SequenceMatcher(None, norm, normalize_title(existing)).ratio() >= title_threshold:
            return True, f"title ~ {existing[:60]}"
    return False, ""


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Filter candidates not already in PAPERS.md.")
    parser.add_argument("--index", required=True, type=Path, help="Path to docs/PAPERS.md")
    parser.add_argument(
        "--candidates",
        required=True,
        type=Path,
        help="JSON file from search_ieee.py",
    )
    parser.add_argument("--output", type=Path, default=None, help="Write filtered JSON here.")
    args = parser.parse_args()

    index_text = args.index.read_text(encoding="utf-8")
    existing_dois = extract_dois_from_index(index_text)
    existing_titles = extract_titles_from_index(index_text)
    existing_xplore_ids = extract_xplore_ids(index_text)

    candidates: list[dict[str, Any]] = json.loads(args.candidates.read_text(encoding="utf-8"))
    kept: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for record in candidates:
        dup, reason = is_duplicate(
            record, existing_dois, existing_titles, existing_xplore_ids
        )
        if dup:
            skipped.append({"title": record.get("title", ""), "reason": reason})
        else:
            kept.append(record)

    print(f"Candidates: {len(candidates)} | New: {len(kept)} | Skipped: {len(skipped)}")
    for item in skipped:
        print(f"  skip: {item['reason']} — {item['title'][:70]}")

    payload = json.dumps(kept, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
