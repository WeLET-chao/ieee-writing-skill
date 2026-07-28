"""Batch download IEEE Xplore and ACM Digital Library PDFs from docs/PAPERS.md tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import parse_qs, unquote, urlparse

import requests

try:
    from .acm_pdf_downloader import (
        download_acm_pdf,
        extract_acm_doi_from_url,
        is_acm_dl_link,
        normalize_acm_doi,
    )
    from .arxiv_pdf_downloader import download_arxiv_pdf, extract_arxiv_id, is_arxiv_link
    from .ieee_pdf_downloader import (
        classify_download_failure,
        default_log_path_for_output,
        download_ieee_pdf,
        verify_pdf,
    )
except ImportError:  # pragma: no cover - direct script execution
    from acm_pdf_downloader import (
        download_acm_pdf,
        extract_acm_doi_from_url,
        is_acm_dl_link,
        normalize_acm_doi,
    )
    from arxiv_pdf_downloader import download_arxiv_pdf, extract_arxiv_id, is_arxiv_link
    from ieee_pdf_downloader import (
        classify_download_failure,
        default_log_path_for_output,
        download_ieee_pdf,
        verify_pdf,
    )


SKILL_ROOT = Path(__file__).resolve().parents[1]
LITERATURE_INDEX_REL = Path("paper/literature/PAPERS.md")
TABLE_HEADER = ["Title", "Authors", "Year", "Venue", "Category", "DOI", "Analysis", "PDF"]
TABLE_HEADER_NO_DOI = ["Title", "Authors", "Year", "Venue", "Category", "Analysis", "PDF"]
TABLE_HEADER_CALIBRATION = [
    "Title",
    "Authors",
    "Year",
    "Venue",
    "Profile",
    "Category",
    "DOI",
    "Analysis",
    "PDF",
]
SUPPORTED_TABLE_HEADERS = (TABLE_HEADER, TABLE_HEADER_NO_DOI, TABLE_HEADER_CALIBRATION)
PERMANENT_FAILURE_MARKERS = (
    "missing expected papers table header",
    "no IEEE Xplore link",
    "no IEEE/ACM PDF link",
    "missing source link",
)
SLUG_MAX_LENGTH = 80
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
INTER_PAPER_DELAY_SECONDS = 8
CONCURRENCY_COOLDOWN_SECONDS = 10
TERMINAL_STATUSES = frozenset({"downloaded", "duplicate", "existing", "applied", "skipped"})
SUCCESS_STATUSES = frozenset({"downloaded", "duplicate", "existing", "applied", "skipped"})


@dataclass
class PaperRecord:
    lab_name: str
    papers_md: str
    title: str
    title_slug: str
    doi: str
    doi_url: str
    pdf_label: str
    pdf_source_link: str
    article_number: Optional[str]
    staging_file: str
    target_file: str
    status: str = "pending"
    error: str = ""


@dataclass
class StatusSummary:
    total: int
    pending: int
    downloaded: int
    existing: int
    applied: int
    duplicate: int
    skipped: int
    failed: int
    complete: bool


def explicit_layout_from_text(document_text: str) -> bool:
    return (
        "papers/<slug>/analysis.md" in document_text
        or "papers/<slug>/paper.pdf" in document_text
        or "paper/literature/<slug>/paper.pdf" in document_text
    )


def slugify(text: str, max_length: int = SLUG_MAX_LENGTH) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower().replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        return "paper"
    return slug[:max_length].rstrip("-") or "paper"


def stable_short_suffix(*parts: str) -> str:
    payload = "||".join(part for part in parts if part) or "paper"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:8]


def append_stable_suffix(base_slug: str, suffix: str, max_length: int = SLUG_MAX_LENGTH) -> str:
    reserved = len(suffix) + 1
    trimmed_base = (base_slug or "paper")[: max_length - reserved].rstrip("-") or "paper"
    return f"{trimmed_base}-{suffix}"


def extract_markdown_link(cell: str) -> Tuple[str, str]:
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if not match:
        return cell.strip(), ""
    return match.group(1).strip(), match.group(2).strip()


def parse_markdown_row(line: str) -> List[str]:
    if not line.startswith("|"):
        return []
    return [part.strip() for part in line.strip().strip("|").split("|")]


def detect_table_header(line: str) -> Optional[List[str]]:
    columns = parse_markdown_row(line)
    if columns in SUPPORTED_TABLE_HEADERS:
        return columns
    return None


def is_ieee_xplore_link(url: str) -> bool:
    return "ieeexplore.ieee.org" in (url or "")


def is_downloadable_pdf_link(url: str) -> bool:
    return is_ieee_xplore_link(url) or is_acm_dl_link(url) or is_arxiv_link(url)


def is_permanent_failure(error: str) -> bool:
    lowered = (error or "").lower()
    return any(marker in lowered for marker in PERMANENT_FAILURE_MARKERS)


def resolve_local_pdf_path(papers_md_path: Path, link: str) -> Optional[Path]:
    if not link or is_downloadable_pdf_link(link):
        return None
    if link.startswith("http://") or link.startswith("https://"):
        return None
    base_dir = papers_md_path.parent
    return (base_dir / link).resolve()


def infer_lab_name(papers_md_path: Path, repo_root: Path) -> str:
    if is_literature_index(papers_md_path, repo_root):
        return ""
    lab_root = papers_md_path.parent.parent
    if lab_root == repo_root:
        return ""
    return lab_root.name


def is_literature_index(papers_md_path: Path, repo_root: Path) -> bool:
    """True when the index is this repo's paper/literature/PAPERS.md layout."""
    try:
        return papers_md_path.resolve() == (repo_root / LITERATURE_INDEX_REL).resolve()
    except OSError:
        return False


def is_calibration_index(papers_md_path: Path) -> bool:
    """True for ieee-venue-profiles/calibration/PAPERS.md style indices."""
    return papers_md_path.name == "PAPERS.md" and papers_md_path.parent.name == "calibration"


def resolve_repo_root(explicit_repo_root: Optional[str] = None) -> Path:
    """Resolve the circuit-work repo root from an explicit path or nearby markers."""
    if explicit_repo_root:
        return Path(explicit_repo_root).resolve()

    candidates: List[Path] = []
    for start in (Path.cwd().resolve(), SKILL_ROOT):
        current = start
        for _ in range(8):
            candidates.append(current)
            if current.parent == current:
                break
            current = current.parent

    for candidate in candidates:
        if (candidate / LITERATURE_INDEX_REL).is_file():
            return candidate
        if list(candidate.glob("*-lab/docs/PAPERS.md")):
            return candidate

    return Path.cwd().resolve()


def iter_papers_md_paths(
    all_labs: bool,
    explicit_paths: Sequence[str],
    repo_root: Path,
    lab_filters: Sequence[str],
) -> List[Path]:
    paths = [Path(path).resolve() for path in explicit_paths]
    if all_labs:
        paths.extend(sorted(repo_root.glob("*-lab/docs/PAPERS.md")))

    normalized_filters = {lab.strip() for lab in lab_filters if lab.strip()}
    deduped: List[Path] = []
    seen: Set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        if normalized_filters and infer_lab_name(path, repo_root) not in normalized_filters:
            continue
        seen.add(path)
        deduped.append(path)
    return deduped


def extract_doi_from_url(url: str) -> str:
    if not url:
        return ""

    parsed = urlparse(url)
    if "doi.org" in parsed.netloc:
        return unquote(parsed.path.lstrip("/"))
    if "searchresult.jsp" in parsed.path:
        query_text = parse_qs(parsed.query).get("queryText", [""])[0]
        return unquote(query_text)
    return ""


def extract_article_number_from_url(url: str) -> Optional[str]:
    if not url:
        return None

    document_match = re.search(r"/document/(\d+)", url)
    if document_match:
        return document_match.group(1)

    arnumber_match = re.search(r"arnumber=(\d+)", url)
    if arnumber_match:
        return arnumber_match.group(1)

    return None


def resolve_article_number(source_link: str, doi_url: str) -> Tuple[Optional[str], str]:
    direct_article_number = extract_article_number_from_url(source_link)
    if direct_article_number:
        return direct_article_number, ""

    if "searchresult.jsp" in source_link and doi_url:
        candidate_url = doi_url
    else:
        candidate_url = source_link or doi_url
    if not candidate_url:
        return None, "missing source link"

    try:
        response = requests.get(candidate_url, headers=REQUEST_HEADERS, timeout=30, allow_redirects=True)
    except requests.RequestException as exc:
        return None, f"failed to resolve article number: {exc}"

    for candidate in (response.url, response.text):
        article_number = extract_article_number_from_url(candidate)
        if article_number:
            return article_number, ""
        json_match = re.search(r'"articleNumber"\s*:\s*"?(?P<id>\d+)"?', candidate)
        if json_match:
            return json_match.group("id"), ""

    return None, f"unable to resolve article number from {candidate_url}"


def target_path_for_paper(
    repo_root: Path,
    lab_name: str,
    title_slug: str,
    explicit_layout: bool = False,
    *,
    literature_mode: bool = False,
    calibration_root: Optional[Path] = None,
) -> Path:
    if calibration_root is not None:
        return calibration_root / "literature" / title_slug / "paper.pdf"
    if literature_mode:
        return repo_root / "paper" / "literature" / title_slug / "paper.pdf"
    lab_root = repo_root / lab_name if lab_name else repo_root
    papers_dir = lab_root / "papers"
    if explicit_layout:
        return papers_dir / title_slug / "paper.pdf"
    return papers_dir / f"{title_slug}.pdf"


def staging_path_for_paper(stage_dir: Path, lab_name: str, title_slug: str, explicit_layout: bool = False) -> Path:
    stage_root = stage_dir / lab_name if lab_name else stage_dir
    if explicit_layout:
        return stage_root / title_slug / "paper.pdf"
    return stage_root / f"{title_slug}.pdf"


def finalize_record_paths(
    records: Sequence[PaperRecord],
    stage_dir: Path,
    repo_root: Path,
    explicit_layout: bool,
    *,
    literature_mode: bool = False,
    calibration_root: Optional[Path] = None,
) -> List[PaperRecord]:
    grouped: Dict[str, List[PaperRecord]] = {}
    for record in records:
        grouped.setdefault(record.target_file, []).append(record)

    finalized: List[PaperRecord] = []
    for collision_group in grouped.values():
        if len(collision_group) == 1:
            finalized.extend(collision_group)
            continue

        identity_groups: Dict[Tuple[str, str, str], List[PaperRecord]] = {}
        for record in collision_group:
            identity = (record.title, record.doi, record.pdf_source_link)
            identity_groups.setdefault(identity, []).append(record)

        unique_representatives: List[PaperRecord] = []
        for duplicates in identity_groups.values():
            leader = duplicates[0]
            unique_representatives.append(leader)
            for duplicate in duplicates[1:]:
                duplicate.status = "duplicate"
                duplicate.error = f"duplicate of {leader.title}"
                duplicate.staging_file = leader.staging_file
                duplicate.target_file = leader.target_file
                finalized.append(duplicate)

        if len(unique_representatives) == 1:
            finalized.append(unique_representatives[0])
            continue

        for record in unique_representatives:
            suffix = stable_short_suffix(record.doi, record.pdf_source_link, record.title)
            suffixed_slug = append_stable_suffix(record.title_slug, suffix)
            record.title_slug = suffixed_slug
            record.target_file = str(
                target_path_for_paper(
                    repo_root,
                    record.lab_name,
                    suffixed_slug,
                    explicit_layout=explicit_layout,
                    literature_mode=literature_mode,
                    calibration_root=calibration_root,
                )
            )
            record.staging_file = str(
                staging_path_for_paper(stage_dir, record.lab_name, suffixed_slug, explicit_layout=explicit_layout)
            )
            finalized.append(record)

    return finalized


def parse_papers_md(papers_md_path: Path, stage_dir: Path, repo_root: Path) -> List[PaperRecord]:
    document_text = papers_md_path.read_text(encoding="utf-8")
    lines = document_text.splitlines()
    header_index = None
    table_header: Optional[List[str]] = None
    literature_mode = is_literature_index(papers_md_path, repo_root)
    calibration_mode = is_calibration_index(papers_md_path)
    calibration_root = papers_md_path.parent if calibration_mode else None
    explicit_layout = explicit_layout_from_text(document_text) or literature_mode or calibration_mode

    for index, line in enumerate(lines):
        detected = detect_table_header(line)
        if detected is not None:
            header_index = index
            table_header = detected
            break
    if header_index is None or table_header is None:
        raise ValueError(f"missing expected papers table header in {papers_md_path}")

    records: List[PaperRecord] = []
    lab_name = infer_lab_name(papers_md_path, repo_root)
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            continue

        columns = parse_markdown_row(line)
        if len(columns) != len(table_header):
            continue

        title = columns[0].strip()
        if table_header == TABLE_HEADER_CALIBRATION:
            doi_label, doi_url = extract_markdown_link(columns[6])
            pdf_label, pdf_source_link = extract_markdown_link(columns[8])
        elif table_header == TABLE_HEADER:
            doi_label, doi_url = extract_markdown_link(columns[5])
            pdf_label, pdf_source_link = extract_markdown_link(columns[7])
        else:
            doi_label, doi_url = "", ""
            pdf_label, pdf_source_link = extract_markdown_link(columns[6])

        doi = extract_doi_from_url(doi_url) or doi_label
        title_slug = slugify(title)
        local_pdf_path = resolve_local_pdf_path(papers_md_path, pdf_source_link)
        if local_pdf_path is not None:
            target_path = local_pdf_path
            explicit_layout = True
        else:
            target_path = target_path_for_paper(
                repo_root,
                lab_name,
                title_slug,
                explicit_layout=explicit_layout,
                literature_mode=literature_mode,
                calibration_root=calibration_root,
            )
        stage_path = staging_path_for_paper(stage_dir, lab_name, title_slug, explicit_layout=explicit_layout)
        article_number = extract_article_number_from_url(pdf_source_link)

        record = PaperRecord(
            lab_name=lab_name,
            papers_md=str(papers_md_path),
            title=title,
            title_slug=title_slug,
            doi=doi,
            doi_url=doi_url,
            pdf_label=pdf_label,
            pdf_source_link=pdf_source_link,
            article_number=article_number,
            staging_file=str(stage_path),
            target_file=str(target_path),
        )
        if not is_downloadable_pdf_link(pdf_source_link):
            if target_pdf_is_valid(record):
                record.status = "existing"
                record.error = "local PDF already present"
            else:
                record.status = "skipped"
                record.error = "no IEEE/ACM PDF link"
        records.append(record)

    return finalize_record_paths(
        records,
        stage_dir,
        repo_root,
        explicit_layout,
        literature_mode=literature_mode,
        calibration_root=calibration_root,
    )


def record_identity_key(record: PaperRecord) -> str:
    return "||".join(
        [
            record.lab_name,
            record.doi,
            record.title,
            record.pdf_source_link,
            record.target_file,
        ]
    )


def target_pdf_is_valid(record: PaperRecord) -> bool:
    target_path = Path(record.target_file)
    if not target_path.exists() or target_path.stat().st_size == 0:
        return False
    article_number = record.article_number or record.doi or record.title_slug
    return verify_pdf(target_path, article_number)


def staging_pdf_is_valid(record: PaperRecord) -> bool:
    stage_path = Path(record.staging_file)
    if not stage_path.exists() or stage_path.stat().st_size == 0:
        return False
    article_number = record.article_number or record.doi or record.title_slug
    return verify_pdf(stage_path, article_number)


def mark_existing_records(records: Sequence[PaperRecord]) -> None:
    for record in records:
        if record.status != "pending":
            continue
        if target_pdf_is_valid(record):
            record.status = "existing"
            record.error = "already present in repo"
            continue
        if staging_pdf_is_valid(record):
            record.status = "downloaded"
            record.error = "valid staged PDF already present"


def load_manifest_records(stage_dir: Path) -> Dict[str, PaperRecord]:
    manifest_path = stage_dir / "manifest.json"
    if not manifest_path.exists():
        return {}

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored: Dict[str, PaperRecord] = {}
    for item in payload.get("records", []):
        record = PaperRecord(**item)
        restored[record_identity_key(record)] = record
    return restored


def merge_resume_status(records: Sequence[PaperRecord], stage_dir: Path) -> None:
    previous = load_manifest_records(stage_dir)
    for record in records:
        prior = previous.get(record_identity_key(record))
        if prior is None:
            continue
        if prior.status in {"existing", "applied", "duplicate", "skipped"}:
            record.status = prior.status
            record.error = prior.error
        elif prior.status == "downloaded" and staging_pdf_is_valid(record):
            record.status = prior.status
            record.error = prior.error
        elif prior.status == "failed" and is_permanent_failure(prior.error):
            record.status = "failed"
            record.error = prior.error
        elif prior.status == "failed":
            record.status = "pending"
            record.error = ""
        if prior.article_number and not record.article_number:
            record.article_number = prior.article_number


def limit_pending_records(records: Sequence[PaperRecord], max_papers: Optional[int]) -> List[PaperRecord]:
    if max_papers is None or max_papers <= 0:
        return list(records)

    limited: List[PaperRecord] = []
    pending_seen = 0
    for record in records:
        if record.status == "pending":
            if pending_seen >= max_papers:
                continue
            pending_seen += 1
        limited.append(record)
    return limited


def summarize_records(records: Sequence[PaperRecord]) -> StatusSummary:
    counts = {
        "pending": 0,
        "downloaded": 0,
        "existing": 0,
        "applied": 0,
        "duplicate": 0,
        "skipped": 0,
        "failed": 0,
    }
    for record in records:
        if record.status in counts:
            counts[record.status] += 1
        else:
            counts["failed"] += 1

    complete = counts["pending"] == 0 and counts["failed"] == 0
    return StatusSummary(
        total=len(records),
        pending=counts["pending"],
        downloaded=counts["downloaded"],
        existing=counts["existing"],
        applied=counts["applied"],
        duplicate=counts["duplicate"],
        skipped=counts["skipped"],
        failed=counts["failed"],
        complete=complete,
    )


def summarize_by_lab(records: Sequence[PaperRecord]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[PaperRecord]] = {}
    for record in records:
        grouped.setdefault(record.lab_name or ".", []).append(record)

    rows: List[Dict[str, object]] = []
    for lab_name in sorted(grouped):
        summary = summarize_records(grouped[lab_name])
        rows.append(
            {
                "lab": lab_name,
                "total": summary.total,
                "pending": summary.pending,
                "existing": summary.existing + summary.applied + summary.downloaded,
                "failed": summary.failed,
                "complete": summary.complete,
            }
        )
    return rows


def print_status_report(records: Sequence[PaperRecord], repo_root: Path) -> StatusSummary:
    summary = summarize_records(records)
    print(f"Repo root: {repo_root}")
    print(f"Total indexed papers: {summary.total}")
    print(f"Pending downloads: {summary.pending}")
    print(f"Already in repo: {summary.existing}")
    print(f"Staged/downloaded this run: {summary.downloaded}")
    print(f"Applied: {summary.applied}")
    print(f"Duplicates: {summary.duplicate}")
    print(f"Skipped (no IEEE link): {summary.skipped}")
    print(f"Failed: {summary.failed}")
    print(f"Complete: {summary.complete}")

    incomplete_labs = [row for row in summarize_by_lab(records) if not row["complete"]]
    print(f"Incomplete labs: {len(incomplete_labs)}")
    for row in incomplete_labs[:20]:
        print(
            f"  - {row['lab']}: pending={row['pending']} "
            f"have={row['existing']} failed={row['failed']} total={row['total']}"
        )
    if len(incomplete_labs) > 20:
        print(f"  ... and {len(incomplete_labs) - 20} more labs")

    payload = {
        "complete": summary.complete,
        "total": summary.total,
        "pending": summary.pending,
        "existing": summary.existing,
        "downloaded": summary.downloaded,
        "applied": summary.applied,
        "duplicate": summary.duplicate,
        "skipped": summary.skipped,
        "failed": summary.failed,
    }
    print(f"AGENT_IEEE_PDF_STATUS {json.dumps(payload, ensure_ascii=False)}")
    return summary


def ensure_stage_dir(stage_dir: Path) -> None:
    stage_dir.mkdir(parents=True, exist_ok=True)


def write_manifest(stage_dir: Path, repo_root: Path, records: Sequence[PaperRecord]) -> Path:
    manifest_path = stage_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "repo_root": str(repo_root),
                "records": [asdict(record) for record in records],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return manifest_path


def apply_single_record(record: PaperRecord) -> None:
    if record.status not in {"downloaded", "existing"}:
        return

    target_path = Path(record.target_file)
    if target_pdf_is_valid(record):
        record.status = "applied"
        record.error = "already present in repo"
        return

    stage_path = Path(record.staging_file)
    if record.status == "existing" and not stage_path.exists():
        record.status = "applied"
        return

    if not stage_path.exists():
        raise RuntimeError(f"missing staged file for apply: {stage_path}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        shutil.copy2(stage_path, temp_path)
        os.replace(temp_path, target_path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

    record.status = "applied"
    record.error = ""


def download_records(
    records: Sequence[PaperRecord],
    *,
    apply_each: bool = False,
    max_papers: Optional[int] = None,
) -> int:
    attempted = 0
    for index, record in enumerate(records, start=1):
        if record.status != "pending":
            continue
        if max_papers is not None and attempted >= max_papers:
            break

        attempted += 1
        print(f"[{index}/{len(records)}] {record.lab_name or '.'}: {record.title}")

        stage_path = Path(record.staging_file)
        log_path = default_log_path_for_output(stage_path)
        acm_doi = extract_acm_doi_from_url(record.pdf_source_link) or normalize_acm_doi(record.doi)
        arxiv_id = extract_arxiv_id(record.pdf_source_link)
        if is_arxiv_link(record.pdf_source_link) or arxiv_id:
            paper_id = arxiv_id or record.pdf_source_link
            result = download_arxiv_pdf(record.pdf_source_link or arxiv_id, output_path=stage_path, log_path=log_path)
            failure_label = f"download failed for arXiv ID {paper_id}"
            verify_id = arxiv_id or record.title_slug
        elif is_acm_dl_link(record.pdf_source_link) or acm_doi.startswith("10.1145/"):
            paper_id = acm_doi
            result = download_acm_pdf(
                record.pdf_source_link or acm_doi,
                output_path=stage_path,
                log_path=log_path,
            )
            failure_label = f"download failed for ACM DOI {paper_id}"
            verify_id = paper_id
        else:
            article_number = record.article_number
            if not article_number:
                article_number, error = resolve_article_number(record.pdf_source_link, record.doi_url)
                if error:
                    record.status = "failed"
                    record.error = error
                    print(f"  [error] {error}")
                    continue
                record.article_number = article_number
            paper_id = article_number
            result = download_ieee_pdf(article_number, output_path=stage_path, log_path=log_path)
            failure_label = f"download failed for article number {article_number}"
            verify_id = article_number
            failure_kind = classify_download_failure(article_number, log_path)
        if not result:
            record.status = "failed"
            record.error = failure_label
            if not is_acm_dl_link(record.pdf_source_link) and not acm_doi.startswith("10.1145/") and not is_arxiv_link(record.pdf_source_link):
                if failure_kind == "concurrency":
                    record.error += f" ({failure_kind})"
            print(f"  [error] {record.error}")
        elif not verify_pdf(stage_path, verify_id):
            record.status = "failed"
            record.error = f"downloaded PDF failed verification for {verify_id}"
            print(f"  [error] {record.error}")
        else:
            record.status = "downloaded"
            print(f"  [ok] staged to {record.staging_file}")
            if apply_each:
                apply_single_record(record)
                print(f"  [ok] applied to {record.target_file}")

        more_in_batch = max_papers is None or attempted < max_papers
        more_pending = any(item.status == "pending" for item in records)
        if more_in_batch and more_pending:
            print(f"  [info] Waiting {INTER_PAPER_DELAY_SECONDS} seconds before the next paper...")
            time.sleep(INTER_PAPER_DELAY_SECONDS)
            if record.status == "failed" and "(concurrency)" in record.error:
                print(f"  [info] Concurrency cooldown: {CONCURRENCY_COOLDOWN_SECONDS} seconds.")
                time.sleep(CONCURRENCY_COOLDOWN_SECONDS)

    return attempted


def preflight_apply(records: Sequence[PaperRecord]) -> None:
    failures = [record for record in records if record.status not in SUCCESS_STATUSES]
    if failures:
        raise RuntimeError("refusing to apply because not all staged downloads succeeded")

    for record in records:
        if record.status in {"duplicate", "existing", "applied"}:
            continue
        stage_path = Path(record.staging_file)
        if not stage_path.exists() and not target_pdf_is_valid(record):
            raise RuntimeError(f"missing staged file: {stage_path}")


def apply_records(records: Sequence[PaperRecord]) -> None:
    preflight_apply(records)
    temp_targets: List[Tuple[Path, Path]] = []
    try:
        for record in records:
            if record.status in {"duplicate", "existing", "applied"}:
                continue
            target_path = Path(record.target_file)
            stage_path = Path(record.staging_file)
            if target_pdf_is_valid(record):
                record.status = "applied"
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
            shutil.copy2(stage_path, temp_path)
            temp_targets.append((temp_path, target_path))
            record.status = "applied"

        for temp_path, target_path in temp_targets:
            os.replace(temp_path, target_path)
    except Exception:
        for temp_path, _ in temp_targets:
            if temp_path.exists():
                temp_path.unlink()
        raise


def collect_all_records(
    papers_md_paths: Sequence[Path],
    stage_dir: Path,
    repo_root: Path,
    *,
    resume: bool,
) -> List[PaperRecord]:
    all_records: List[PaperRecord] = []
    for papers_md_path in papers_md_paths:
        try:
            all_records.extend(parse_papers_md(papers_md_path, stage_dir, repo_root))
        except Exception as exc:
            all_records.append(
                PaperRecord(
                    lab_name=infer_lab_name(papers_md_path, repo_root),
                    papers_md=str(papers_md_path),
                    title="",
                    title_slug="",
                    doi="",
                    doi_url="",
                    pdf_label="",
                    pdf_source_link="",
                    article_number=None,
                    staging_file="",
                    target_file="",
                    status="failed",
                    error=str(exc),
                )
            )

    if resume:
        merge_resume_status(all_records, stage_dir)
    mark_existing_records(all_records)
    return all_records


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch download IEEE PDFs from docs/PAPERS.md files.")
    parser.add_argument("--papers-md", action="append", default=[], help="Path to a PAPERS.md file.")
    parser.add_argument("--all-labs", action="store_true", help="Process every */docs/PAPERS.md under the repo root.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Circuit-work repo root. Auto-detected from cwd when omitted.",
    )
    parser.add_argument(
        "--lab",
        action="append",
        default=[],
        help="Limit --all-labs to specific lab directory names (repeatable).",
    )
    parser.add_argument(
        "--stage-dir",
        default=str(Path("/tmp") / "ieee-pdf-stage"),
        help="Directory used for staged downloads and the manifest.",
    )
    parser.add_argument("--apply", action="store_true", help="Write validated staged PDFs into the repo papers/ tree.")
    parser.add_argument(
        "--apply-each",
        action="store_true",
        help="Apply each successful download immediately instead of waiting for a full batch.",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=None,
        help="Download at most N pending papers per run (for loop / batching).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse statuses from the stage manifest and skip already-downloaded targets.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Report pending/complete counts without downloading.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    repo_root = resolve_repo_root(args.repo_root)
    papers_md_paths = iter_papers_md_paths(args.all_labs, args.papers_md, repo_root, args.lab)
    if not papers_md_paths:
        parser.error("No PAPERS.md files specified. Use --papers-md, --all-labs, or --lab.")

    stage_dir = Path(args.stage_dir).resolve()
    ensure_stage_dir(stage_dir)

    all_records = collect_all_records(
        papers_md_paths,
        stage_dir,
        repo_root,
        resume=args.resume or args.status,
    )

    if args.status:
        print_status_report(all_records, repo_root)
        return 0 if summarize_records(all_records).complete else 2

    pending_before = summarize_records(all_records).pending
    if pending_before == 0:
        summary = print_status_report(all_records, repo_root)
        if args.apply:
            apply_records(all_records)
            print("Apply completed successfully.")
        return 0 if summary.complete else 2

    records_to_process = limit_pending_records(all_records, args.max_papers)
    attempted = download_records(
        records_to_process,
        apply_each=args.apply_each,
        max_papers=args.max_papers,
    )

    mark_existing_records(all_records)
    manifest_path = write_manifest(stage_dir, repo_root, all_records)
    summary = summarize_records(all_records)

    print(f"\nManifest written to: {manifest_path}")
    print(f"Repo root: {repo_root}")
    print(f"Attempted this run: {attempted}")
    print(f"Total records: {summary.total}")
    print(f"Pending: {summary.pending}")
    print(f"Already in repo: {summary.existing}")
    print(f"Downloaded (staged): {summary.downloaded}")
    print(f"Applied: {summary.applied}")
    print(f"Failures: {summary.failed}")
    print(f"Duplicates skipped: {summary.duplicate}")
    print(f"Skipped (no IEEE link): {summary.skipped}")
    print(f"Complete: {summary.complete}")
    print(f"AGENT_IEEE_PDF_STATUS {json.dumps(asdict(summary), ensure_ascii=False)}")

    if summary.failed:
        for record in [item for item in all_records if item.status == "failed"][:20]:
            print(f"- {record.lab_name or '.'}: {record.title} -> {record.error}")

    if args.apply and not args.apply_each:
        ready = [record for record in all_records if record.status == "downloaded"]
        if ready:
            apply_records(ready)
            mark_existing_records(all_records)
            write_manifest(stage_dir, repo_root, all_records)
            print(f"Applied {len(ready)} staged PDFs.")

    if summary.complete:
        return 0
    if summary.failed and attempted == 0:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
