#!/usr/bin/env bash
# Initialize IEEE TCAD journal manuscript layout (split TeX + journal template).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LAYOUT_SKILL="$(cd "${SKILL_DIR}/../ieee-manuscript-layout" && pwd)"
BIB_SKILL="$(cd "${SKILL_DIR}/../ieee-manuscript-bib/templates" && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../.." && pwd)"
PAPER_DIR="${PAPER_DIR:-${REPO_ROOT}/paper}"
TEMPLATE_DIR="${SKILL_DIR}/templates"
BOOTSTRAP_TEX=0

usage() {
  cat <<'EOF'
Usage: init_tcad_journal.sh [--bootstrap-tex]

  Default: create paper/ subdirs + install IEEEtran.cls, IEEEabrv.bib, .latexmkrc.

  --bootstrap-tex: install 0_main_ieee_trans.tex and 1_abstract_v1.tex … 5_conclusion_v1.tex
                   plus starter reference.bib when missing.

Environment:
  PAPER_DIR   Manuscript root (default: <repo>/paper)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bootstrap-tex) BOOTSTRAP_TEX=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

mkdir -p \
  "${PAPER_DIR}/figures" \
  "${PAPER_DIR}/photos" \
  "${PAPER_DIR}/references" \
  "${PAPER_DIR}/scripts" \
  "${PAPER_DIR}/figure_data" \
  "${PAPER_DIR}/out/pdf_pages"

copy_if_missing() {
  local src="$1"
  local dst="$2"
  if [[ -f "${dst}" ]]; then
    echo "keep existing: ${dst}"
  else
    cp "${src}" "${dst}"
    echo "installed: ${dst}"
  fi
}

copy_if_missing "${LAYOUT_SKILL}/templates/IEEEtran.cls" "${PAPER_DIR}/IEEEtran.cls"
copy_if_missing "${LAYOUT_SKILL}/templates/IEEEabrv.bib" "${PAPER_DIR}/IEEEabrv.bib"
copy_if_missing "${LAYOUT_SKILL}/templates/.latexmkrc" "${PAPER_DIR}/.latexmkrc"

if [[ "${BOOTSTRAP_TEX}" -eq 1 ]]; then
  copy_if_missing "${TEMPLATE_DIR}/0_main_ieee_trans.tex" "${PAPER_DIR}/0_main_ieee_trans.tex"
  for n in 1_abstract_v1 2_introduction_v1 3_methodology_v1 4_results_v1 5_conclusion_v1; do
    copy_if_missing "${TEMPLATE_DIR}/${n}.tex" "${PAPER_DIR}/${n}.tex"
  done
  copy_if_missing "${BIB_SKILL}/reference.bib" "${PAPER_DIR}/reference.bib"
fi

echo "TCAD journal layout ready under ${PAPER_DIR}"
echo "See ${TEMPLATE_DIR}/PAPER_LAYOUT.md and skill reference.md"
