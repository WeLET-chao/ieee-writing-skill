#!/usr/bin/env python3
"""Search IEEE Xplore for venue-profile calibration papers and update PAPERS.md."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = SKILL_DIR / "calibration"
TARGETS_PATH = CALIBRATION_DIR / "venue_targets.json"
PAPERS_MD = CALIBRATION_DIR / "PAPERS.md"
CORPUS_DIR = CALIBRATION_DIR / "_corpus"
SEARCH_SKILL = SKILL_DIR.parent / "ieee-literature-search"
SEARCH_SCRIPT = SEARCH_SKILL / "scripts" / "search_ieee.py"
RUN_PYTHON = SEARCH_SKILL / "scripts" / "run_python.sh"


def load_targets() -> dict:
    return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))


def years_back(config: dict) -> tuple[int, int]:
    back = int(__import__("os").environ.get("CALIBRATION_YEARS_BACK", config["year_window"]["default_years_back"]))
    end = int(__import__("os").environ.get("CALIBRATION_END_YEAR", config["year_window"]["end_year"]))
    return end - back + 1, end


def run_search(query: str, start_year: int, end_year: int, publication_title: str | None, max_records: int) -> list[dict]:
    cmd = [
        str(RUN_PYTHON),
        str(SEARCH_SCRIPT),
        "--query",
        query,
        "--start-year",
        str(start_year),
        "--end-year",
        str(end_year),
        "--max-records",
        str(max_records),
        "--format",
        "json",
    ]
    if publication_title:
        cmd.extend(["--publication-title", publication_title])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"Search failed (exit {proc.returncode}). Configure IEEE_XPLORE_API_KEY or use manual BibTeX import.")
    return json.loads(proc.stdout or "[]")


def post_filter(records: list[dict], target: dict) -> list[dict]:
    pf = target.get("post_filter")
    if not pf:
        return records
    needles = [n.lower() for n in pf.get("venue_contains_any", [])]
    if not needles:
        return records
    out = []
    for r in records:
        venue = (r.get("venue") or "").lower()
        if any(n in venue for n in needles):
            out.append(r)
    return out


def to_row(record: dict, profile_id: str, category: str) -> str:
    doi = record.get("doi") or ""
    doi_cell = "—"
    if doi:
        url = record.get("doi_url") or f"https://doi.org/{doi}"
        doi_cell = f"[{doi}]({url})"
    pdf_cell = "—"
    if record.get("xplore_url"):
        pdf_cell = f"[IEEE Xplore]({record['xplore_url']})"
    title = record.get("title", "—")
    return (
        f"| {title} | {record.get('authors', '—')} | {record.get('year', '—')} | "
        f"{record.get('venue', '—')} | {profile_id} | {category} | {doi_cell} | — | {pdf_cell} |"
    )


def existing_dois(papers_md: Path) -> set[str]:
    text = papers_md.read_text(encoding="utf-8") if papers_md.is_file() else ""
    return set(re.findall(r"10\.\d{4,}/[^\s\]|]+", text))


def insert_rows(papers_md: Path, rows: list[str]) -> None:
    if not rows:
        return
    text = papers_md.read_text(encoding="utf-8")
    marker = "<!-- Add new rows above this line"
    block = "\n".join(rows) + "\n"
    if marker in text:
        text = text.replace(marker, block + marker, 1)
    else:
        text = text.rstrip() + "\n" + block
    papers_md.write_text(text, encoding="utf-8")


def main() -> int:
    if not RUN_PYTHON.is_file():
        raise SystemExit(f"Missing search skill: {RUN_PYTHON}")

    config = load_targets()
    start_year, end_year = years_back(config)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    (CALIBRATION_DIR / "literature").mkdir(parents=True, exist_ok=True)

    all_results: dict[str, list[dict]] = {}
    new_rows: list[str] = []
    seen = existing_dois(PAPERS_MD)

    for target in config["targets"]:
        pid = target["profile_id"]
        print(f"Searching {pid} ({start_year}–{end_year}) …", file=sys.stderr)
        records = run_search(
            target["query"],
            start_year,
            end_year,
            target.get("publication_title"),
            int(target.get("max_records", 20)),
        )
        records = post_filter(records, target)
        all_results[pid] = records
        category = target.get("category", "venue-calibration")
        for r in records:
            doi = r.get("doi") or ""
            if doi and doi in seen:
                continue
            if doi:
                seen.add(doi)
            new_rows.append(to_row(r, pid, category))

    out_json = CORPUS_DIR / "search_results.json"
    out_json.write_text(
        json.dumps(
            {
                "generated": datetime.now().isoformat(timespec="seconds"),
                "year_range": [start_year, end_year],
                "by_profile": all_results,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    insert_rows(PAPERS_MD, new_rows)
    print(f"Wrote {out_json}")
    print(f"Appended {len(new_rows)} rows to {PAPERS_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
