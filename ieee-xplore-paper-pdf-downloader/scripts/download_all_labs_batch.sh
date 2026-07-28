#!/usr/bin/env bash
# Download the next batch of IEEE PDFs for every *-lab/docs/PAPERS.md in a repo.
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
STAGE_DIR="${STAGE_DIR:-/tmp/ieee-pdf-stage}"
MAX_PAPERS="${MAX_PAPERS:-10}"

exec "$SKILL_ROOT/scripts/run_python.sh" "$SKILL_ROOT/scripts/download_from_papers_md.py" \
  --repo-root "$REPO_ROOT" \
  --all-labs \
  --stage-dir "$STAGE_DIR" \
  --resume \
  --apply-each \
  --max-papers "$MAX_PAPERS" \
  "$@"
