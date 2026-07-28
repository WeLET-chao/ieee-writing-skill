#!/usr/bin/env python3
"""List BibTeX keys cited in IEEE LaTeX source files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CITE_PATTERN = re.compile(r"\\cite[a-zA-Z*]*\{([^}]+)\}")


def extract_cited_keys(tex_paths: list[Path]) -> list[str]:
    """Return sorted unique citation keys from the given TeX files."""
    keys: set[str] = set()
    for path in tex_paths:
        text = path.read_text(encoding="utf-8")
        for match in CITE_PATTERN.finditer(text):
            for key in match.group(1).split(","):
                cleaned = key.strip()
                if cleaned:
                    keys.add(cleaned)
    return sorted(keys)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tex_files",
        nargs="*",
        type=Path,
        help="TeX files to scan (default: paper/0_main_ieee_conference.tex)",
    )
    parser.add_argument(
        "--bib",
        type=Path,
        default=None,
        help="Optional .bib file; report cited keys missing from bibliography",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parents[4]
    tex_files = args.tex_files or [repo_root / "paper" / "0_main_ieee_conference.tex"]
    tex_files = [p.resolve() for p in tex_files]

    cited = extract_cited_keys(tex_files)
    print("Cited keys:")
    for key in cited:
        print(f"  {key}")

    if args.bib is not None:
        bib_text = args.bib.read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
        missing = [k for k in cited if k not in bib_keys]
        if missing:
            print("\nMissing from bibliography:")
            for key in missing:
                print(f"  {key}")
            return 1
        print(f"\nAll {len(cited)} cited keys found in {args.bib}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
