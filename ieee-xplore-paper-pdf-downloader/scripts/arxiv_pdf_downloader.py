"""arXiv open-access PDF download helpers."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

try:
    from .ieee_pdf_downloader import (
        REQUEST_TIMEOUT_SECONDS,
        build_error_logger,
        check_existing_pdf,
        default_log_path_for_output,
        log_error,
        verify_pdf,
    )
except ImportError:  # pragma: no cover - direct script execution
    from ieee_pdf_downloader import (
        REQUEST_TIMEOUT_SECONDS,
        build_error_logger,
        check_existing_pdf,
        default_log_path_for_output,
        log_error,
        verify_pdf,
    )

ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")


def is_arxiv_link(url: str) -> bool:
    return "arxiv.org" in (url or "")


def extract_arxiv_id(url_or_id: str) -> str:
    if not url_or_id:
        return ""
    text = url_or_id.strip()
    if ARXIV_ID_PATTERN.fullmatch(text):
        return text.split("v", 1)[0]
    parsed = urlparse(text)
    if "arxiv.org" not in parsed.netloc:
        match = ARXIV_ID_PATTERN.search(text)
        return match.group(1) if match else ""
    path = parsed.path.strip("/")
    if path.startswith("pdf/"):
        candidate = path.split("/", 1)[1]
    elif path.startswith("abs/"):
        candidate = path.split("/", 1)[1]
    else:
        candidate = path.split("/")[-1]
    match = ARXIV_ID_PATTERN.search(candidate)
    return match.group(1) if match else ""


def build_arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def download_arxiv_pdf(
    url_or_id: str,
    output_path: str | Path,
    log_path: str | Path | None = None,
) -> bool:
    """Download and verify one arXiv PDF."""
    arxiv_id = extract_arxiv_id(url_or_id)
    if not arxiv_id:
        return False

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = Path(log_path).resolve() if log_path else default_log_path_for_output(output_path).resolve()
    logger = build_error_logger(log_path)

    if check_existing_pdf(output_path, arxiv_id, logger):
        return True

    request_url = build_arxiv_pdf_url(arxiv_id)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
    }

    try:
        response = requests.get(
            request_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        log_error(logger, f"[Paper ID: {arxiv_id}] Request failed: {exc}")
        return False

    content_type = response.headers.get("content-type", "")
    is_pdf = content_type.startswith("application/pdf") or response.content[:5] == b"%PDF-"
    if response.status_code != 200 or not is_pdf:
        log_error(
            logger,
            (
                f"[Paper ID: {arxiv_id}] Download failed: status={response.status_code}, "
                f"content_type={content_type}, final_url={response.url}"
            ),
        )
        return False

    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        temp_path.write_bytes(response.content)
    except OSError as exc:
        log_error(logger, f"[Paper ID: {arxiv_id}] Failed to write temp file {temp_path}: {exc}")
        if temp_path.exists():
            temp_path.unlink()
        return False

    if temp_path.stat().st_size == 0 or not verify_pdf(temp_path, arxiv_id, logger):
        if temp_path.exists():
            temp_path.unlink()
        log_error(logger, f"[Paper ID: {arxiv_id}] Downloaded PDF failed validation: {output_path}")
        return False

    shutil.move(temp_path, output_path)
    print(f"[info] Downloaded and verified PDF: {output_path}")
    return True
