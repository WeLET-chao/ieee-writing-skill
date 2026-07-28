#!/usr/bin/env python3
"""Extract structured fields from paper digest files into corpus JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from corpus_common import (
    extract_bibliographic,
    extract_sections,
    load_profile,
    read_markdown,
    resolve_glob,
    slug_from_path,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract structured fields from paper digests using a profile."
    )
    parser.add_argument("repo_root", type=Path, help="Repository root directory")
    parser.add_argument(
        "--profile",
        type=Path,
        default=None,
        help="Profile JSON path (default: profiles/default.json next to this script)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: <repo>/_corpus/extracted.json)",
    )
    return parser


def default_profile_path() -> Path:
    """Return the bundled default profile path."""
    return Path(__file__).resolve().parent.parent / "profiles" / "default.json"


def extract_corpus(repo_root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    """Extract all configured fields from the corpus.

    Args:
        repo_root: Repository root.
        profile: Loaded profile dictionary.

    Returns:
        Extraction payload with metadata and per-paper records.
    """
    glob_pattern = profile["input"]["glob"]
    paths = resolve_glob(repo_root, glob_pattern)
    section_specs = profile["sections"]
    bibliographic = profile.get("bibliographic", {})

    papers: list[dict[str, Any]] = []
    for path in paths:
        content = read_markdown(path)
        record: dict[str, Any] = {
            "slug": slug_from_path(path, repo_root),
            "path": str(path.relative_to(repo_root)),
        }
        record.update(extract_bibliographic(content, bibliographic))
        record.update(extract_sections(content, section_specs))
        papers.append(record)

    return {
        "profile": profile.get("name", "unknown"),
        "repo_root": str(repo_root),
        "input_glob": glob_pattern,
        "paper_count": len(papers),
        "papers": papers,
    }


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    profile_path = args.profile or default_profile_path()
    out_path = args.out or (repo_root / "_corpus" / "extracted.json")

    if not repo_root.is_dir():
        print(f"error: repo root not found: {repo_root}", file=sys.stderr)
        return 1
    if not profile_path.is_file():
        print(f"error: profile not found: {profile_path}", file=sys.stderr)
        return 1

    profile = load_profile(profile_path)
    payload = extract_corpus(repo_root, profile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path} ({payload['paper_count']} papers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
