#!/usr/bin/env bash
# Download calibration corpus PDFs from calibration/PAPERS.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENT_SKILLS_ROOT="$(cd "${SKILL_DIR}/../../.." && pwd)"
FETCH_SKILL="${FETCH_SKILL:-${AGENT_SKILLS_ROOT}/paper-acquisition/paper-pdf-fetch}"
PAPERS_MD="${SKILL_DIR}/calibration/PAPERS.md"

mkdir -p "${SKILL_DIR}/calibration/literature"

python3 "${FETCH_SKILL}/scripts/fetch_from_papers_md.py" \
  --repo-root "${AGENT_SKILLS_ROOT}" \
  --papers-md "${PAPERS_MD}" \
  --resume \
  "$@"

echo "Calibration PDFs: ${SKILL_DIR}/calibration/literature/<slug>/paper.pdf"
