#!/usr/bin/env python3
"""Download IEEE Xplore PDFs from an IEEE export CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class CsvPaper:
    index: int
    title: str
    year: str
    group: str
    article_number: str
    pdf_link: str
    output_path: Path


def sanitize_filename(text: str, max_len: int = 80) -> str:
    if not text or not text.strip():
        return "unknown"
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return (slug[:max_len].rstrip("-") or "unknown")


def extract_article_number(link: str) -> str:
    if not link:
        return ""
    match = re.search(r"/document/(\d+)", link)
    if match:
        return match.group(1)
    match = re.search(r"arnumber=(\d+)", link)
    if match:
        return match.group(1)
    return ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_columns(rows: list[dict[str, str]], columns: Iterable[str]) -> None:
    if not rows:
        raise ValueError("CSV contains no rows")
    available = set(rows[0].keys())
    missing = [column for column in columns if column not in available]
    if missing:
        raise ValueError(f"CSV missing required columns: {', '.join(missing)}")


def iter_papers(
    rows: list[dict[str, str]],
    output_root: Path,
    title_column: str,
    year_column: str,
    group_by: str,
    pdf_link_column: str,
) -> tuple[list[CsvPaper], int]:
    papers: list[CsvPaper] = []
    skipped_no_article = 0
    for index, row in enumerate(rows, start=1):
        pdf_link = (row.get(pdf_link_column) or "").strip()
        article_number = extract_article_number(pdf_link)
        if not article_number:
            skipped_no_article += 1
            continue

        title = (row.get(title_column) or "Untitled Paper").strip()
        year = (row.get(year_column) or "NoYear").strip() or "NoYear"
        group_value = (row.get(group_by) or "Unknown").strip() or "Unknown"
        group_slug = sanitize_filename(group_value, 40)
        title_slug = sanitize_filename(title)
        output_path = output_root / group_slug / f"{year}_{title_slug}.pdf"
        papers.append(
            CsvPaper(
                index=index,
                title=title,
                year=year,
                group=group_value,
                article_number=article_number,
                pdf_link=pdf_link,
                output_path=output_path,
            )
        )
    return papers, skipped_no_article


def response_is_concurrency_block(response: requests.Response) -> bool:
    final_url = response.url or ""
    content_type = response.headers.get("content-type", "")
    if response.status_code == 418 or "reason=concurrency" in final_url:
        return True
    if content_type.startswith("text/html") and "reason=concurrency" in response.text:
        return True
    return False


def verify_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            prefix = handle.read(5)
            if prefix != b"%PDF-":
                return False
            handle.seek(0)
            if PdfReader is not None:
                reader = PdfReader(handle)
                if not reader.pages:
                    return False
                reader.pages[0].extract_text()
            return True
    except Exception:
        return False


def download_one(paper: CsvPaper, log_path: Path, timeout: int = 60) -> tuple[bool, str]:
    paper.output_path.parent.mkdir(parents=True, exist_ok=True)
    if paper.output_path.exists() and verify_pdf(paper.output_path):
        return True, "existing"

    doc_url = f"https://ieeexplore.ieee.org/document/{paper.article_number}"
    pdf_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={paper.article_number}&ref="

    session = requests.Session()
    try:
        doc_response = session.get(doc_url, headers=BROWSER_HEADERS, timeout=30, allow_redirects=True)
        if response_is_concurrency_block(doc_response):
            return False, "IEEE concurrency block on document page"

        headers = dict(BROWSER_HEADERS)
        headers["Referer"] = doc_url
        response = session.get(pdf_url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return False, f"request failed: {exc}"

    if response_is_concurrency_block(response):
        return False, "IEEE concurrency block on PDF request"

    content_type = response.headers.get("content-type", "")
    if response.status_code != 200 or not content_type.startswith("application/pdf"):
        message = (
            f"download failed: status={response.status_code}, "
            f"content_type={content_type}, final_url={response.url}"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"[{paper.article_number}] {message}\n")
        return False, message

    temp_path = paper.output_path.with_suffix(paper.output_path.suffix + ".tmp")
    temp_path.write_bytes(response.content)
    if not verify_pdf(temp_path):
        temp_path.unlink(missing_ok=True)
        message = "downloaded file failed PDF validation"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"[{paper.article_number}] {message}\n")
        return False, message

    temp_path.replace(paper.output_path)
    return True, "downloaded"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="IEEE Xplore export CSV")
    parser.add_argument("--output-root", required=True, help="Root directory for downloaded PDFs")
    parser.add_argument("--group-by", default="Publication Year", help="CSV column used for subfolders")
    parser.add_argument("--title-column", default="Document Title", help="CSV column used for filename slugs")
    parser.add_argument("--year-column", default="Publication Year", help="CSV column used for filename year prefix")
    parser.add_argument("--pdf-link-column", default="PDF Link", help="CSV column containing IEEE PDF/document links")
    parser.add_argument("--max-papers", type=int, default=0, help="Attempt at most N papers; 0 means all")
    parser.add_argument("--delay-seconds", type=float, default=4.0, help="Delay between downloads")
    parser.add_argument("--dry-run", action="store_true", help="Print planned downloads without writing PDFs")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    csv_path = Path(args.csv).resolve()
    output_root = Path(args.output_root).resolve()
    rows = read_csv(csv_path)
    require_columns(rows, [args.title_column, args.year_column, args.group_by, args.pdf_link_column])

    papers, skipped_no_article = iter_papers(
        rows,
        output_root,
        args.title_column,
        args.year_column,
        args.group_by,
        args.pdf_link_column,
    )
    selected = papers[: args.max_papers] if args.max_papers else papers

    print("=== IEEE CSV PDF Downloader ===")
    print(f"CSV: {csv_path}")
    print(f"Output root: {output_root}")
    print(f"Rows: {len(rows)} | with article number: {len(papers)} | skipped no article: {skipped_no_article}")
    print(f"Attempting: {len(selected)}")
    if args.dry_run:
        print("DRY RUN -- no files will be downloaded")

    downloaded = existing = failed = 0
    log_path = output_root / "ieee_csv_download_errors.log"
    for pos, paper in enumerate(selected, start=1):
        print(f"[{pos}/{len(selected)}] {paper.article_number} {paper.title[:90]}")
        print(f"  -> {paper.output_path}")
        if args.dry_run:
            continue

        ok, status = download_one(paper, log_path)
        if ok and status == "existing":
            existing += 1
            print("  [skip] existing valid PDF")
        elif ok:
            downloaded += 1
            size_kb = paper.output_path.stat().st_size / 1024
            print(f"  [ok] {size_kb:.1f} KB")
        else:
            failed += 1
            print(f"  [failed] {status}")

        if pos < len(selected) and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)

    if not args.dry_run:
        output_root.mkdir(parents=True, exist_ok=True)
        summary_path = output_root / f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        summary_path.write_text(
            "\n".join(
                [
                    "IEEE CSV PDF Download Log",
                    "==========================",
                    f"Date: {datetime.now().isoformat(timespec='seconds')}",
                    f"CSV: {csv_path}",
                    f"Output root: {output_root}",
                    f"Rows: {len(rows)}",
                    f"Attempted: {len(selected)}",
                    f"Downloaded: {downloaded}",
                    f"Existing: {existing}",
                    f"Skipped no article number: {skipped_no_article}",
                    f"Failed: {failed}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print(f"Log: {summary_path}")

    status = {
        "total_rows": len(rows),
        "with_article_number": len(papers),
        "attempted": len(selected),
        "downloaded": downloaded,
        "existing": existing,
        "skipped_no_article": skipped_no_article,
        "failed": failed,
        "dry_run": bool(args.dry_run),
        "complete_for_selected_batch": failed == 0,
    }
    print("AGENT_IEEE_CSV_PDF_STATUS " + json.dumps(status, ensure_ascii=False, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
