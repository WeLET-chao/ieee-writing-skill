"""CLI for downloading one IEEE Xplore PDF by article number."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .ieee_pdf_downloader import download_ieee_pdf
except ImportError:  # pragma: no cover - direct script execution
    from ieee_pdf_downloader import download_ieee_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download one IEEE Xplore PDF by article number.")
    parser.add_argument("--article-number", required=True, help="IEEE article number, e.g. 11223063")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum download attempts")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_path = Path(args.output).resolve()
    if download_ieee_pdf(args.article_number.strip(), output_path, max_retries=args.max_retries):
        return 0
    print(f"[error] Failed to download article {args.article_number}.")
    print(f"[error] See {output_path.parent / 'ieee_download_errors.log'} for details.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
