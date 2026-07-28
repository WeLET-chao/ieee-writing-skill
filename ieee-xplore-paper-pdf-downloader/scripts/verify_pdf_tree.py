"""Verify that every PDF in a directory tree is readable."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Tuple

try:
    from .ieee_pdf_downloader import verify_pdf
except ImportError:  # pragma: no cover - direct script execution
    from ieee_pdf_downloader import verify_pdf


def scan_pdfs(root_dir: Path, max_depth: int | None = None) -> Tuple[int, int, int]:
    """Walk a directory tree and validate every PDF file."""
    total_files = 0
    valid_count = 0
    invalid_count = 0

    root_dir = root_dir.resolve()
    for current_dir, dirs, files in os.walk(root_dir):
        current_path = Path(current_dir)
        current_depth = len(current_path.relative_to(root_dir).parts)
        if max_depth is not None and current_depth >= max_depth:
            dirs.clear()

        for filename in files:
            if not filename.lower().endswith(".pdf"):
                continue
            total_files += 1
            file_path = current_path / filename
            relative_path = file_path.relative_to(root_dir)
            print(f"[info] Verifying {relative_path}")
            if verify_pdf(file_path, str(relative_path)):
                valid_count += 1
                print(f"  [ok] Valid PDF")
            else:
                invalid_count += 1
                print(f"  [error] Invalid PDF")

    return total_files, valid_count, invalid_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify every PDF in a directory tree.")
    parser.add_argument("root_dir", help="Root directory to scan")
    parser.add_argument("--depth", type=int, help="Maximum directory depth to scan")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    total_files, valid_count, invalid_count = scan_pdfs(Path(args.root_dir), args.depth)
    print("\nVerification summary:")
    print(f"Total files: {total_files}")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    return 1 if invalid_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
