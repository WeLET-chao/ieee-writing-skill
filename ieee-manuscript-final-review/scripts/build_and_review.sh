#!/usr/bin/env bash
# Compile PDF, print page count, and rasterize pages for final review.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LAYOUT_SCRIPTS="$(cd "${SKILL_ROOT}/../ieee-manuscript-layout/scripts" && pwd)"

"${LAYOUT_SCRIPTS}/build_paper.sh"
"${SCRIPT_DIR}/render_pdf_pages.sh"

echo "Next: run ieee-manuscript-final-review checklist (reference.md §2)."
