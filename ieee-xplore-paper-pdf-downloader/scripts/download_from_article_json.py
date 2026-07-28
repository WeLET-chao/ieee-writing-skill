"""Batch download IEEE PDFs from JSON files containing article numbers."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import List, Sequence, Tuple

try:
    from .ieee_pdf_downloader import default_log_path_for_output, download_ieee_pdf, verify_pdf
except ImportError:  # pragma: no cover - direct script execution
    from ieee_pdf_downloader import default_log_path_for_output, download_ieee_pdf, verify_pdf


INTER_PAPER_DELAY_SECONDS = 5


def get_json_files(directory: Path) -> List[Tuple[Path, Path]]:
    """Return every JSON file with its path relative to the input directory."""
    return [(path, path.parent.relative_to(directory)) for path in sorted(directory.rglob("*.json"))]


def create_output_directory(base_output_dir: Path, relative_path: Path, json_filename: str) -> Path:
    """Mirror the JSON directory structure under the output base directory."""
    output_dir = base_output_dir / relative_path / json_filename
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def download_papers_from_json(json_file_path: Path, output_dir: Path) -> Tuple[int, int, List[str]]:
    """Download every paper referenced by articleNumber in one JSON file."""
    data = json.loads(json_file_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print(f"[warn] JSON content is not a list, skipping: {json_file_path}")
        return 0, 0, []

    success_count = 0
    failed_count = 0
    failed_papers: List[str] = []
    total_papers = len(data)

    for index, paper in enumerate(data, start=1):
        article_number = paper.get("articleNumber")
        if article_number is None:
            failed_count += 1
            failed_papers.append(f"record {index}: missing articleNumber")
            print(f"[warn] Missing articleNumber in record {index} of {json_file_path}")
            continue

        article_number = str(article_number)
        output_path = output_dir / f"{article_number}.pdf"
        log_path = default_log_path_for_output(output_path)
        print(f"[{index}/{total_papers}] {article_number}")

        if output_path.exists() and verify_pdf(output_path, article_number):
            print(f"  [info] Existing PDF is valid, skipping: {output_path}")
            success_count += 1
            continue

        if download_ieee_pdf(article_number, output_path=output_path, log_path=log_path):
            success_count += 1
            print(f"  [ok] Saved to {output_path}")
        else:
            failed_count += 1
            failed_papers.append(article_number)
            print(f"  [error] Failed to download {article_number}")

        if index < total_papers:
            print(f"  [info] Waiting {INTER_PAPER_DELAY_SECONDS} seconds before the next paper...")
            time.sleep(INTER_PAPER_DELAY_SECONDS)

    return success_count, failed_count, failed_papers


def batch_download_from_json(article_info_dir: Path, pdf_base_dir: Path) -> int:
    """Process all JSON files below one directory tree."""
    article_info_dir = article_info_dir.resolve()
    pdf_base_dir = pdf_base_dir.resolve()
    pdf_base_dir.mkdir(parents=True, exist_ok=True)

    json_files = get_json_files(article_info_dir)
    print(f"[info] Found {len(json_files)} JSON files under {article_info_dir}")

    total_success = 0
    total_failed = 0
    all_failed_papers: List[Tuple[str, str]] = []

    for file_index, (json_file_path, relative_path) in enumerate(json_files, start=1):
        json_stem = json_file_path.stem
        output_dir = create_output_directory(pdf_base_dir, relative_path, json_stem)
        print(f"\n[info] File {file_index}/{len(json_files)}: {json_file_path}")
        print(f"[info] Output directory: {output_dir}")

        success, failed, failed_list = download_papers_from_json(json_file_path, output_dir)
        total_success += success
        total_failed += failed
        for paper_id in failed_list:
            all_failed_papers.append((json_stem, paper_id))

    print("\nDownload summary:")
    print(f"JSON files processed: {len(json_files)}")
    print(f"Successful downloads: {total_success}")
    print(f"Failed downloads: {total_failed}")

    if all_failed_papers:
        print("\nFailures:")
        for json_stem, paper_id in all_failed_papers:
            print(f"- {json_stem}: {paper_id}")
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch download IEEE PDFs from JSON article lists.")
    parser.add_argument("--article-info-dir", required=True, help="Directory containing JSON article lists")
    parser.add_argument("--pdf-base-dir", required=True, help="Base directory for downloaded PDFs")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return batch_download_from_json(Path(args.article_info_dir), Path(args.pdf_base_dir))


if __name__ == "__main__":
    raise SystemExit(main())
