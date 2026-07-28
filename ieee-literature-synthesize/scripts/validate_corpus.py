#!/usr/bin/env python3
"""Validate extracted corpus data and optional synthesis grounding."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

from corpus_common import (
    extract_section,
    load_profile,
    read_markdown,
    section_map,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Validate corpus extraction and synthesis.")
    parser.add_argument("repo_root", type=Path, help="Repository root directory")
    parser.add_argument(
        "--extracted",
        type=Path,
        default=None,
        help="Path to extracted.json (default: <repo>/_corpus/extracted.json)",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="Profile JSON path",
    )
    parser.add_argument(
        "--synthesis",
        type=Path,
        default=None,
        help="Optional synthesis markdown to validate for slug grounding",
    )
    parser.add_argument(
        "--spot-check",
        type=int,
        default=None,
        help="Number of random papers to spot-check (default: profile setting)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for spot-check sampling",
    )
    return parser


def default_profile_path() -> Path:
    """Return the bundled default profile path."""
    return Path(__file__).resolve().parent.parent / "profiles" / "default.json"


def validate_required_sections(
    papers: list[dict[str, Any]],
    section_specs: dict[str, Any],
    min_chars: int,
) -> list[str]:
    """Validate required sections and minimum content length."""
    errors: list[str] = []
    for paper in papers:
        slug = paper.get("slug", "<unknown>")
        for section_key, spec in section_specs.items():
            if not spec.get("required", False):
                continue
            value = paper.get(section_key, "")
            if not isinstance(value, str) or len(value.strip()) < min_chars:
                errors.append(
                    f"{slug}: required section '{section_key}' missing or shorter than {min_chars} chars"
                )
    return errors


def validate_categories(
    papers: list[dict[str, Any]],
    require_category: bool,
    min_coverage: float,
) -> list[str]:
    """Validate category coverage when categories are expected."""
    errors: list[str] = []
    if not require_category:
        return errors

    categorized = 0
    for paper in papers:
        category = paper.get("category") or {}
        primary = category.get("primary", "uncategorized")
        if primary and primary != "uncategorized":
            categorized += 1

    coverage = categorized / len(papers) if papers else 0.0
    if coverage < min_coverage:
        errors.append(
            f"category coverage {coverage:.1%} below minimum {min_coverage:.1%}"
        )
    return errors


def spot_check_extraction(
    repo_root: Path,
    papers: list[dict[str, Any]],
    section_specs: dict[str, Any],
    sample_size: int,
    seed: int,
) -> list[str]:
    """Compare extracted text prefixes against source digests."""
    errors: list[str] = []
    if not papers or sample_size <= 0:
        return errors

    random.seed(seed)
    sample = random.sample(papers, min(sample_size, len(papers)))
    for paper in sample:
        rel_path = paper.get("path")
        if not rel_path:
            errors.append(f"{paper.get('slug', '<unknown>')}: missing path for spot-check")
            continue
        source_path = repo_root / rel_path
        if not source_path.is_file():
            errors.append(f"{paper.get('slug', '<unknown>')}: source digest not found at {rel_path}")
            continue

        content = read_markdown(source_path)
        sections = section_map(content)
        for section_key, spec in section_specs.items():
            if not spec.get("required", False):
                continue
            headings = spec.get("headings", [])
            source_body = extract_section(sections, headings)
            extracted_body = str(paper.get(section_key, ""))
            if source_body[:80].strip() != extracted_body[:80].strip():
                errors.append(
                    f"{paper.get('slug', '<unknown>')}: spot-check mismatch in section '{section_key}'"
                )
                break
    return errors


def validate_synthesis_grounding(synthesis_path: Path, papers: list[dict[str, Any]]) -> list[str]:
    """Ensure synthesis markdown references at least some known paper slugs."""
    errors: list[str] = []
    if not synthesis_path.is_file():
        return [f"synthesis file not found: {synthesis_path}"]

    text = synthesis_path.read_text(encoding="utf-8", errors="replace")
    slugs = [paper.get("slug", "") for paper in papers if paper.get("slug")]
    referenced = [slug for slug in slugs if slug and slug in text]
    if len(referenced) < max(3, min(10, len(slugs) // 10)):
        errors.append(
            "synthesis references too few paper slugs; ground themes in source index or inline slug mentions"
        )

    if re.search(r"\bAnalysis:\b", text) is None and "analysis:" not in text.lower():
        errors.append("synthesis should mark agent-inferred items with 'Analysis:' when applicable")

    return errors


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    profile_path = args.profile or default_profile_path()
    extracted_path = args.extracted or (repo_root / "_corpus" / "extracted.json")

    if not repo_root.is_dir():
        print(f"error: repo root not found: {repo_root}", file=sys.stderr)
        return 1
    if not extracted_path.is_file():
        print(f"error: extracted JSON not found: {extracted_path}", file=sys.stderr)
        return 1
    if not profile_path.is_file():
        print(f"error: profile not found: {profile_path}", file=sys.stderr)
        return 1

    profile = load_profile(profile_path)
    extracted = json.loads(extracted_path.read_text(encoding="utf-8"))
    papers = extracted.get("papers", [])
    section_specs = profile.get("sections", {})
    agg_settings = profile.get("aggregation", {})
    min_chars = int(agg_settings.get("min_section_chars", 50))
    spot_check_count = args.spot_check or int(agg_settings.get("spot_check_count", 5))
    require_category = any(
        spec.get("parse") in {"category_block", "comma_tags"}
        for spec in section_specs.values()
    )

    errors: list[str] = []
    errors.extend(validate_required_sections(papers, section_specs, min_chars))
    errors.extend(validate_categories(papers, require_category, min_coverage=0.8))
    errors.extend(
        spot_check_extraction(
            repo_root=repo_root,
            papers=papers,
            section_specs=section_specs,
            sample_size=spot_check_count,
            seed=args.seed,
        )
    )
    if args.synthesis is not None:
        errors.extend(validate_synthesis_grounding(args.synthesis, papers))

    if errors:
        print("validate_corpus.py: FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "validate_corpus.py: OK "
        f"({len(papers)} papers, spot-check={spot_check_count}, profile={profile.get('name', 'unknown')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
