#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_ROOT/.venv"

if [[ -x "$VENV/bin/python" ]]; then
  exec "$VENV/bin/python" "$@"
fi

exec python3 "$@"
