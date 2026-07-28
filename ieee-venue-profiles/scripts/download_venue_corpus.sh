#!/usr/bin/env bash
# Download calibration corpus PDFs from calibration/PAPERS.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PMIC_ROOT="$(cd "${SKILL_DIR}/../.." && pwd)"
DOWNLOAD_SKILL="${PMIC_ROOT}/.skills/ieee-xplore-paper-pdf-downloader"
PAPERS_MD="${SKILL_DIR}/calibration/PAPERS.md"
STAGE_DIR="${STAGE_DIR:-/tmp/ieee-venue-profile-pdf-stage}"
MAX_PAPERS="${MAX_PAPERS:-15}"

mkdir -p "${SKILL_DIR}/calibration/literature"

ARGS=(
  --repo-root "${PMIC_ROOT}"
  --papers-md "${PAPERS_MD}"
  --stage-dir "${STAGE_DIR}"
  --max-papers "${MAX_PAPERS}"
  --apply-each
)

if [[ "${RESUME:-1}" == "1" ]]; then
  ARGS+=(--resume)
fi

"${DOWNLOAD_SKILL}/scripts/run_python.sh" \
  "${DOWNLOAD_SKILL}/scripts/download_from_papers_md.py" \
  "${ARGS[@]}" \
  "$@"

echo "Calibration PDFs: ${SKILL_DIR}/calibration/literature/<slug>/paper.pdf"
