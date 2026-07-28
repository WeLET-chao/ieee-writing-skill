#!/usr/bin/env bash
# Build the IEEE manuscript PDF with latexmk and print page count.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
PAPER_DIR="${PAPER_DIR:-${REPO_ROOT}/paper}"
MAIN_TEX="${MAIN_TEX:-0_main_ieee_conference.tex}"
PDF_NAME="${MAIN_TEX%.tex}.pdf"

cd "${PAPER_DIR}"
latexmk -pdf "${MAIN_TEX}"

if command -v pdfinfo >/dev/null 2>&1; then
  pdfinfo "${PDF_NAME}" | rg '^Pages:' || true
fi

echo "Built: ${PAPER_DIR}/${PDF_NAME}"
