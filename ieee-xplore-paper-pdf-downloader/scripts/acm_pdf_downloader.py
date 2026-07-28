"""ACM Digital Library PDF download helpers."""

from __future__ import annotations

import re
import shutil
import time
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse

import requests

try:
    from .ieee_pdf_downloader import (
        REQUEST_TIMEOUT_SECONDS,
        RETRY_WAIT_SECONDS,
        build_error_logger,
        check_existing_pdf,
        default_log_path_for_output,
        log_error,
        verify_pdf,
    )
except ImportError:  # pragma: no cover - direct script execution
    from ieee_pdf_downloader import (
        REQUEST_TIMEOUT_SECONDS,
        RETRY_WAIT_SECONDS,
        build_error_logger,
        check_existing_pdf,
        default_log_path_for_output,
        log_error,
        verify_pdf,
    )

ACM_DOI_PATTERN = re.compile(r"10\.1145/\S+", re.IGNORECASE)


def is_acm_dl_link(url: str) -> bool:
    return "dl.acm.org" in (url or "")


def normalize_acm_doi(doi: str) -> str:
    cleaned = (doi or "").strip()
    if cleaned.lower().startswith("doi:"):
        cleaned = cleaned[4:].strip()
    return cleaned


def extract_acm_doi_from_url(url: str) -> str:
    if not url:
        return ""

    parsed = urlparse(url)
    if "doi.org" in parsed.netloc:
        candidate = unquote(parsed.path.lstrip("/"))
        if ACM_DOI_PATTERN.fullmatch(candidate):
            return candidate

    if not is_acm_dl_link(url):
        return ""

    path = unquote(parsed.path)
    for prefix in ("/doi/pdf/", "/doi/epdf/", "/doi/abs/", "/doi/"):
        if prefix in path:
            candidate = path.split(prefix, 1)[1].split("?")[0].strip("/")
            if ACM_DOI_PATTERN.fullmatch(candidate):
                return candidate
    match = ACM_DOI_PATTERN.search(path)
    return match.group(0) if match else ""


def build_acm_pdf_url(doi: str) -> str:
    return f"https://dl.acm.org/doi/pdf/{normalize_acm_doi(doi)}"


def response_indicates_acm_block(response: requests.Response) -> bool:
    content_type = response.headers.get("content-type", "")
    if response.status_code in {403, 429} and content_type.startswith("text/html"):
        lowered = response.text.lower()
        if "cloudflare" in lowered or "challenge" in lowered or "access denied" in lowered:
            return True
    return False


def download_acm_pdf(
    doi_or_url: str,
    output_path: str | Path,
    max_retries: int = 3,
    log_path: str | Path | None = None,
) -> bool:
    """Download and verify one ACM Digital Library PDF."""
    doi = extract_acm_doi_from_url(doi_or_url) or normalize_acm_doi(doi_or_url)
    if not doi or not ACM_DOI_PATTERN.fullmatch(doi):
        return False

    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = Path(log_path).resolve() if log_path else default_log_path_for_output(output_path).resolve()
    logger = build_error_logger(log_path)

    if check_existing_pdf(output_path, doi, logger):
        return True

    request_url = build_acm_pdf_url(doi)
    headers = {
        "Connection": "keep-alive",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
        "Referer": f"https://dl.acm.org/doi/{doi}",
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
            log_error(logger, f"[Paper ID: {doi}] Request failed: {exc}")
            if attempt < max_retries - 1:
                continue
            return False

        if response_indicates_acm_block(response):
            log_error(
                logger,
                (
                    f"[Paper ID: {doi}] ACM_ACCESS_BLOCK "
                    f"ACM returned an access block page: status={response.status_code}, final_url={response.url}"
                ),
            )
            if attempt < max_retries - 1:
                print("[warn] ACM returned an access block page, retrying...")
                continue
            return False

        content_type = response.headers.get("content-type", "")
        is_pdf = content_type.startswith("application/pdf") or response.content[:5] == b"%PDF-"
        if response.status_code != 200 or not is_pdf:
            if attempt < max_retries - 1:
                print(f"[warn] Download failed with status={response.status_code}, retrying...")
                continue
            log_error(
                logger,
                (
                    f"[Paper ID: {doi}] Download failed: status={response.status_code}, "
                    f"content_type={content_type}, final_url={response.url}"
                ),
            )
            return False

        temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        try:
            temp_path.write_bytes(response.content)
        except OSError as exc:
            log_error(logger, f"[Paper ID: {doi}] Failed to write temp file {temp_path}: {exc}")
            if temp_path.exists():
                temp_path.unlink()
            if attempt < max_retries - 1:
                continue
            return False

        if temp_path.stat().st_size == 0 or not verify_pdf(temp_path, doi, logger):
            if temp_path.exists():
                temp_path.unlink()
            if attempt < max_retries - 1:
                print("[warn] Downloaded file failed validation, retrying...")
                continue
            log_error(logger, f"[Paper ID: {doi}] Downloaded PDF failed validation: {output_path}")
            return False

        shutil.move(temp_path, output_path)
        print(f"[info] Downloaded and verified PDF: {output_path}")
        return True

    return False
