#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_ROOT/.venv"

python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q requests bibtexparser

ENV_LOCAL="$SKILL_ROOT/scripts/env.local.sh"
if [[ ! -f "$ENV_LOCAL" ]]; then
  cat > "$ENV_LOCAL" <<'EOF'
# Optional overrides for IEEE API keys.
# Defaults live in scripts/api_keys.sh (primary + backup failover).
#
# export IEEE_XPLORE_API_KEY='your-primary-key'
# export IEEE_XPLORE_API_KEY_BACKUP='your-backup-key'
EOF
  echo "Created $ENV_LOCAL (optional overrides)."
fi

chmod 600 "$SKILL_ROOT/scripts/api_keys.sh" 2>/dev/null || true

echo "Setup complete."
echo "API keys: scripts/api_keys.sh (primary + backup)"
echo "Activate: source $SKILL_ROOT/scripts/env.sh"
