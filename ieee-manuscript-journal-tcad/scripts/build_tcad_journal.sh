#!/usr/bin/env bash
# Build IEEE TCAD journal manuscript (0_main_ieee_trans.tex) with latexmk.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../.." && pwd)"
PAPER_DIR="${PAPER_DIR:-${REPO_ROOT}/paper}"
MAIN_TEX="${MAIN_TEX:-0_main_ieee_trans.tex}"
PDF_NAME="${MAIN_TEX%.tex}.pdf"

if [[ ! -f "${PAPER_DIR}/${MAIN_TEX}" ]]; then
  echo "Missing ${PAPER_DIR}/${MAIN_TEX}" >&2
  echo "Run: PAPER_DIR=<dir> ${SCRIPT_DIR}/init_tcad_journal.sh --bootstrap-tex" >&2
  exit 1
fi

cd "${PAPER_DIR}"
latexmk -pdf "${MAIN_TEX}"

if command -v pdfinfo >/dev/null 2>&1; then
  pdfinfo "${PDF_NAME}" | rg '^Pages:' || true
fi

echo "Built: ${PAPER_DIR}/${PDF_NAME}"
