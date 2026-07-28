#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_ROOT/.venv"

python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -r "$SKILL_ROOT/scripts/requirements.txt"

echo "Setup complete."
echo "Run scripts with: $SKILL_ROOT/scripts/run_python.sh"
