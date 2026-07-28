"""Shared IEEE Xplore PDF download and validation helpers."""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Optional

import requests

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - setup.sh installs this dependency
    PdfReader = None


REQUEST_TIMEOUT_SECONDS = 30
CONCURRENCY_ERROR_MARKER = "IEEE_CONCURRENCY_BLOCK"
RETRY_WAIT_SECONDS = (10, 8)


def response_indicates_concurrency_block(response: requests.Response) -> bool:
    """Return True when IEEE responds with a concurrency limit page."""
    final_url = response.url or ""
    content_type = response.headers.get("content-type", "")
    if "reason=concurrency" in final_url:
        return True
    if response.status_code == 418:
        return True
    if content_type.startswith("text/html") and "reason=concurrency" in response.text:
        return True
    return False


def build_error_logger(log_path: Path) -> logging.Logger:
    """Create or reuse a file logger for one log path."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger_name = f"ieee_downloader.{log_path.resolve()}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.ERROR)
    if logger.handlers:
        return logger

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


def flush_logger(logger: logging.Logger) -> None:
    """Flush every handler attached to the logger."""
    for handler in logger.handlers:
        handler.flush()


def log_error(logger: logging.Logger, message: str) -> None:
    """Write one error line and flush immediately."""
    logger.error(message)
    flush_logger(logger)


def default_log_path_for_output(output_path: Path) -> Path:
    """Place runtime logs beside the requested output file."""
    return output_path.parent / "ieee_download_errors.log"


def verify_pdf(file_path: Path, paper_id: str, logger: Optional[logging.Logger] = None) -> bool:
    """Validate that a PDF exists, is non-empty, and can be parsed."""
    try:
        with file_path.open("rb") as handle:
            if PdfReader is None:
                return handle.read(5) == b"%PDF-"

            pdf = PdfReader(handle)
            if not pdf.pages:
                raise ValueError("PDF has no pages")
            pdf.pages[0].extract_text()
            return True
    except Exception as exc:  # pragma: no cover - depends on malformed PDFs
        if logger is not None:
            log_error(logger, f"[Paper ID: {paper_id}] PDF verification failed: {exc}")
        return False


def check_existing_pdf(file_path: Path, paper_id: str, logger: logging.Logger) -> bool:
    """Skip downloads when a valid PDF already exists."""
    if not file_path.exists():
        return False
    if file_path.stat().st_size == 0:
        print(f"[warn] Existing file is empty, re-downloading: {file_path}")
        return False
    if verify_pdf(file_path, paper_id, logger):
        print(f"[info] Existing file is valid, skipping download: {file_path}")
        return True
    print(f"[warn] Existing file failed validation, re-downloading: {file_path}")
    return False


def classify_download_failure(paper_id: str, log_path: Path) -> str:
    """Inspect the tail of the error log for a known failure class."""
    if not log_path.exists():
        return ""
    lines = log_path.read_text(encoding="utf-8").splitlines()[-50:]
    matches = [line for line in lines if f"[Paper ID: {paper_id}]" in line]
    if not matches:
        return ""
    if CONCURRENCY_ERROR_MARKER in matches[-1]:
        return "concurrency"
    return ""


def download_ieee_pdf(
    article_number: str,
    output_path: str | Path,
    max_retries: int = 3,
    log_path: str | Path | None = None,
) -> bool:
    """Download and verify one IEEE Xplore PDF."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = Path(log_path).resolve() if log_path else default_log_path_for_output(output_path).resolve()
    logger = build_error_logger(log_path)

    if check_existing_pdf(output_path, article_number, logger):
        return True

    request_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={article_number}&ref="
    headers = {
        "Connection": "keep-alive",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Referer": f"https://ieeexplore.ieee.org/document/{article_number}",
    }

    for attempt in range(max_retries):
        if attempt > 0:
            wait_seconds = RETRY_WAIT_SECONDS[min(attempt - 1, len(RETRY_WAIT_SECONDS) - 1)]
            print(f"[info] Retry {attempt + 1}/{max_retries} after waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)

        try:
            response = requests.get(
                request_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
                allow_redirects=True,
            )
        except requests.RequestException as exc:
            log_error(logger, f"[Paper ID: {article_number}] Request failed: {exc}")
            if attempt < max_retries - 1:
                continue
            return False

        if response_indicates_concurrency_block(response):
            log_error(
                logger,
                (
                    f"[Paper ID: {article_number}] {CONCURRENCY_ERROR_MARKER} "
                    f"IEEE returned a concurrency block page: status={response.status_code}, final_url={response.url}"
                ),
            )
            if attempt < max_retries - 1:
                print("[warn] IEEE returned a concurrency block page, retrying...")
                continue
            return False

        content_type = response.headers.get("content-type", "")
        if response.status_code != 200 or not content_type.startswith("application/pdf"):
            if attempt < max_retries - 1:
                print(f"[warn] Download failed with status={response.status_code}, retrying...")
                continue
            log_error(
                logger,
                (
                    f"[Paper ID: {article_number}] Download failed: status={response.status_code}, "
                    f"content_type={content_type}, final_url={response.url}"
                ),
            )
            return False

        temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        try:
            temp_path.write_bytes(response.content)
        except OSError as exc:
            log_error(logger, f"[Paper ID: {article_number}] Failed to write temp file {temp_path}: {exc}")
            if temp_path.exists():
                temp_path.unlink()
            if attempt < max_retries - 1:
                continue
            return False

        if temp_path.stat().st_size == 0 or not verify_pdf(temp_path, article_number, logger):
            if temp_path.exists():
                temp_path.unlink()
            if attempt < max_retries - 1:
                print("[warn] Downloaded file failed validation, retrying...")
                continue
            log_error(logger, f"[Paper ID: {article_number}] Downloaded PDF failed validation: {output_path}")
            return False

        shutil.move(temp_path, output_path)
        print(f"[info] Downloaded and verified PDF: {output_path}")
        return True

    return False
