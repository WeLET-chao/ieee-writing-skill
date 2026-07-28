#!/usr/bin/env bash
# Create a scoping-test sandbox: full repo copy with human paper artifacts stripped.
# Usage: prepare_scoping_test_repo.sh [source_repo] [dest_repo]
set -euo pipefail

SRC="$(readlink -f "${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}")"
DEST="$(readlink -f "${2:-$(dirname "$SRC")/strained-device-model-scoping-test}")"
BACKUP_ROOT="$(dirname "$SRC")/strained-device-model-paper-backup-$(date +%Y%m%d)"

echo "Source: $SRC"
echo "Test sandbox: $DEST"
echo "Paper backup: $BACKUP_ROOT"

if [[ -d "$SRC/paper" ]]; then
  rm -rf "$BACKUP_ROOT"
  cp -a "$SRC/paper" "$BACKUP_ROOT"
  echo "Backed up paper/ -> $BACKUP_ROOT"
fi

rm -rf "$DEST"
rsync -a \
  --exclude='.git' \
  --exclude='**/.venv' \
  --exclude='**/__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.egg-info' \
  "$SRC/" "$DEST/"

PAPER="$DEST/paper"
rm -f "$PAPER/writing_plan.md" "$PAPER/figure_asset_plan.json" \
  "$PAPER/0_main_ieee_conference.tex" "$PAPER/0_main_ieee_conference.pdf" \
  "$PAPER/figure1_architecture_prompt.md" "$PAPER/TFT_Strain_Model.zip"
rm -rf "$PAPER/manual" "$PAPER/out" "$PAPER/figures" "$PAPER/scripts" "$PAPER/figure_data" "$PAPER/docs"
mkdir -p "$PAPER/figures" "$PAPER/out/scoping"

for slug in "$PAPER/literature"/*/; do
  [[ -d "$slug" ]] || continue
  find "$slug" -mindepth 1 -maxdepth 1 ! -name 'paper.pdf' -exec rm -rf {} +
done

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$SKILL_ROOT/../ieee-manuscript-bib/templates/reference.bib" ]]; then
  cp "$SKILL_ROOT/../ieee-manuscript-bib/templates/reference.bib" "$PAPER/reference.bib"
fi

echo "Scoping test repo ready: $DEST"
