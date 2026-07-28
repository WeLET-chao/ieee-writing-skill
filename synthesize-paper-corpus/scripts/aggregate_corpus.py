#!/usr/bin/env python3
"""Aggregate extracted corpus JSON into indexes and summary statistics."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from corpus_common import (
    bullet_items,
    era_label,
    load_profile,
    parse_year,
    prior_art_headings,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Aggregate extracted corpus JSON into summary indexes."
    )
    parser.add_argument(
        "extracted_json",
        type=Path,
        help="Path to extracted.json produced by extract_corpus.py",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="Profile JSON path for aggregation settings",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: sibling aggregate.json)",
    )
    return parser


def default_profile_path() -> Path:
    """Return the bundled default profile path."""
    return Path(__file__).resolve().parent.parent / "profiles" / "default.json"


def get_nested(record: dict[str, Any], dotted_key: str) -> Any:
    """Read a dotted key such as category.primary from a record."""
    value: Any = record
    for part in dotted_key.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def aggregate_corpus(extracted: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Build mechanical aggregates from extracted corpus data.

    Args:
        extracted: Output of extract_corpus.py.
        profile: Loaded profile dictionary.

    Returns:
        Aggregate payload with counts, indexes, and per-group summaries.
    """
    papers: list[dict[str, Any]] = extracted.get("papers", [])
    agg_settings = profile.get("aggregation", {})
    group_by = agg_settings.get("group_by", "category.primary")
    era_buckets = agg_settings.get("era_buckets", [2010, 2015, 2020, 2023])

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_year: Counter[str] = Counter()
    by_era: Counter[str] = Counter()
    prior_heading_counts: Counter[str] = Counter()
    opportunity_bullets: list[dict[str, str]] = []
    section_lengths: dict[str, list[int]] = defaultdict(list)
    category_primary_counts: Counter[str] = Counter()
    category_secondary_counts: Counter[str] = Counter()

    for paper in papers:
        category = paper.get("category") or {"primary": "uncategorized", "secondary": "", "note": ""}
        primary = category.get("primary") or "uncategorized"
        secondary = category.get("secondary") or ""
        by_category[primary].append(paper)
        category_primary_counts[primary] += 1
        if secondary:
            category_secondary_counts[secondary] += 1

        year_text = str(paper.get("year", ""))
        by_year[year_text] += 1
        by_era[era_label(parse_year(year_text), era_buckets)] += 1

        prior_text = paper.get("prior_art", "")
        for heading in prior_art_headings(prior_text):
            prior_heading_counts[heading] += 1

        for bullet in bullet_items(paper.get("research_opportunity", "")):
            opportunity_bullets.append(
                {
                    "slug": paper.get("slug", ""),
                    "year": year_text,
                    "text": bullet,
                }
            )

        for section_key, value in paper.items():
            if isinstance(value, str) and section_key not in {"path", "category_raw"}:
                section_lengths[section_key].append(len(value.strip()))

    category_summaries: dict[str, Any] = {}
    for category, group in sorted(by_category.items(), key=lambda item: (-len(item[1]), item[0])):
        category_summaries[category] = {
            "count": len(group),
            "papers": [
                {
                    "slug": item.get("slug", ""),
                    "title": item.get("title", ""),
                    "year": item.get("year", ""),
                }
                for item in group
            ],
            "sample_problem_statements": [
                item.get("problem_statement", "")[:240] for item in group[:3]
            ],
            "sample_prior_art_openers": [item.get("prior_art", "")[:240] for item in group[:3]],
            "opportunity_count": sum(
                len(bullet_items(item.get("research_opportunity", ""))) for item in group
            ),
        }

    return {
        "profile": extracted.get("profile", profile.get("name", "unknown")),
        "repo_root": extracted.get("repo_root", ""),
        "input_glob": extracted.get("input_glob", ""),
        "paper_count": len(papers),
        "group_by": group_by,
        "counts": {
            "by_primary_category": dict(category_primary_counts),
            "by_secondary_category": dict(category_secondary_counts),
            "by_year": dict(by_year),
            "by_era": dict(by_era),
        },
        "prior_art_heading_counts": dict(prior_heading_counts.most_common()),
        "opportunity_bullet_count": len(opportunity_bullets),
        "opportunity_bullets": opportunity_bullets,
        "section_length_stats": {
            key: {
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "avg": round(sum(values) / len(values), 1) if values else 0.0,
                "nonempty": sum(1 for value in values if value > 0),
            }
            for key, values in sorted(section_lengths.items())
        },
        "category_summaries": category_summaries,
    }


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    extracted_path = args.extracted_json.resolve()
    profile_path = args.profile or default_profile_path()
    out_path = args.out or extracted_path.parent / "aggregate.json"

    if not extracted_path.is_file():
        print(f"error: extracted JSON not found: {extracted_path}", file=sys.stderr)
        return 1
    if not profile_path.is_file():
        print(f"error: profile not found: {profile_path}", file=sys.stderr)
        return 1

    extracted = json.loads(extracted_path.read_text(encoding="utf-8"))
    profile = load_profile(profile_path)
    payload = aggregate_corpus(extracted, profile)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path} ({payload['paper_count']} papers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
