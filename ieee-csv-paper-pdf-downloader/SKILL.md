---
name: ieee-csv-paper-pdf-downloader
description: >-
  Download and validate IEEE Xplore PDFs from an IEEE export CSV containing
  "PDF Link", "Document Title", and "Publication Year" columns. Use when the
  user has an IEEE Xplore CSV export instead of docs/PAPERS.md or article-number
  JSON, and the current environment already has legitimate IEEE Xplore access.
---

# IEEE CSV Paper PDF Downloader

Download PDFs from IEEE Xplore CSV exports such as `export2026.06.10-05.09.50.csv`.
This skill follows the same principle as `download_papers.ps1`: extract the
article number from the CSV `PDF Link`, visit the IEEE document page to establish
a session, then request the stamp PDF URL and validate the downloaded file.

## Use When

- The input is an IEEE Xplore export CSV, not `docs/PAPERS.md`.
- The CSV has columns like `Document Title`, `Publication Year`, `DOI`, and `PDF Link`.
- PDFs should be grouped into folders by year or another CSV column.

Do not use this skill to bypass access controls. If IEEE returns HTML, login,
paywall, or concurrency pages instead of PDFs, report the failure and stop or
retry later.

## Quick Start

Dry-run first:

```bash
SKILL=.skills/ieee-csv-paper-pdf-downloader
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_ieee_csv.py" \
  --csv export2026.06.10-05.09.50.csv \
  --output-root /tmp/ieee-csv-papers \
  --dry-run \
  --max-papers 5
```

Download a small batch:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_ieee_csv.py" \
  --csv export2026.06.10-05.09.50.csv \
  --output-root paper_writing/ieee_csv_papers \
  --max-papers 5 \
  --delay-seconds 4
```

## Main Script

`scripts/download_from_ieee_csv.py`

Important options:

| Option | Purpose |
|--------|---------|
| `--csv PATH` | IEEE export CSV path. |
| `--output-root DIR` | Root folder for downloaded PDFs. |
| `--group-by COLUMN` | CSV column used for subfolders; default `Publication Year`. |
| `--pdf-link-column COLUMN` | Column containing IEEE PDF/document links; default `PDF Link`. |
| `--title-column COLUMN` | Column used for filenames; default `Document Title`. |
| `--max-papers N` | Limit attempted downloads for safe batching. |
| `--delay-seconds N` | Delay between downloads. |
| `--dry-run` | Print planned downloads without writing PDFs. |

Outputs:

- PDFs under `<output-root>/<group>/<year>_<slug>.pdf`.
- `download_log_<timestamp>.txt` summary.
- `ieee_csv_download_errors.log` with failure details.
- `AGENT_IEEE_CSV_PDF_STATUS {...}` JSON for batch automation.

## Implementation Notes

Article-number extraction:

1. Match `/document/<id>` in `PDF Link`.
2. Match `arnumber=<id>` in `PDF Link`.
3. Rows without an article number are skipped.

Download URL:

```text
https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=<id>&ref=
```

The script validates that the response is a real PDF and, when `pypdf` is
installed, parses the first page before marking a download successful.
