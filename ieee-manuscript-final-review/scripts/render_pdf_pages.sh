#!/usr/bin/env bash
# Rasterize compiled PDF pages for visual review (reference.md §1).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
PAPER_DIR="${PAPER_DIR:-${REPO_ROOT}/paper}"
MAIN_TEX="${MAIN_TEX:-0_main_ieee_conference.tex}"
PDF_NAME="${MAIN_TEX%.tex}.pdf"
PDF_PATH="${PAPER_DIR}/${PDF_NAME}"
OUT_DIR="${OUT_DIR:-${PAPER_DIR}/out/pdf_pages}"
DPI="${DPI:-180}"

if [[ ! -f "${PDF_PATH}" ]]; then
  echo "Missing PDF: ${PDF_PATH}" >&2
  echo "Run ieee-manuscript-layout/scripts/build_paper.sh first." >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
pdftoppm -png -r "${DPI}" "${PDF_PATH}" "${OUT_DIR}/page"

echo "Rendered pages under ${OUT_DIR}/page-*.png"
