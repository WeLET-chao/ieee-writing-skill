#!/usr/bin/env bash
# Initialize paper/ folder layout and copy IEEE LaTeX templates when missing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../../.." && pwd)"
REVISION_TEMPLATES="$(cd "${SKILL_DIR}/../ieee-manuscript-revision/templates" && pwd)"
BIB_TEMPLATES="$(cd "${SKILL_DIR}/../ieee-manuscript-bib/templates" && pwd)"
PAPER_DIR="${PAPER_DIR:-${REPO_ROOT}/paper}"
TEMPLATE_DIR="${SKILL_DIR}/templates"
BOOTSTRAP_TEX=0

usage() {
  cat <<'EOF'
Usage: init_paper_assets.sh [--bootstrap-tex]

  Default: create paper/ subdirs + install IEEEtran.cls, IEEEabrv.bib, .latexmkrc
            when missing.

  --bootstrap-tex: also install main.tex, reference.bib, writing_plan.md when missing.
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

copy_if_missing "${TEMPLATE_DIR}/IEEEtran.cls" "${PAPER_DIR}/IEEEtran.cls"
copy_if_missing "${TEMPLATE_DIR}/IEEEabrv.bib" "${PAPER_DIR}/IEEEabrv.bib"
copy_if_missing "${TEMPLATE_DIR}/.latexmkrc" "${PAPER_DIR}/.latexmkrc"

if [[ "${BOOTSTRAP_TEX}" -eq 1 ]]; then
  copy_if_missing "${TEMPLATE_DIR}/main.tex" "${PAPER_DIR}/main.tex"
  copy_if_missing "${BIB_TEMPLATES}/reference.bib" "${PAPER_DIR}/reference.bib"
  if [[ -f "${REVISION_TEMPLATES}/writing_plan.md" ]]; then
    copy_if_missing "${REVISION_TEMPLATES}/writing_plan.md" "${PAPER_DIR}/writing_plan.md"
  fi
  FIG_TEMPLATE="$(cd "${SKILL_DIR}/../ieee-manuscript-figures/templates" && pwd)/generate_figures.template.py"
  if [[ -f "${FIG_TEMPLATE}" ]]; then
    copy_if_missing "${FIG_TEMPLATE}" "${PAPER_DIR}/scripts/generate_figures.py"
  fi
fi

echo "Paper layout ready under ${PAPER_DIR}"
echo "See ${TEMPLATE_DIR}/PAPER_LAYOUT.md for directory conventions."
