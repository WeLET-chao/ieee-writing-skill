#!/usr/bin/env bash
# Load IEEE Xplore API keys for ieee-xplore-paper-search scripts.
SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$SKILL_ROOT/scripts/api_keys.sh" ]]; then
  # shellcheck source=/dev/null
  source "$SKILL_ROOT/scripts/api_keys.sh"
elif [[ -f "$SKILL_ROOT/scripts/api_keys.sh.example" ]]; then
  # shellcheck source=/dev/null
  source "$SKILL_ROOT/scripts/api_keys.sh.example"
fi

ENV_FILE="$SKILL_ROOT/scripts/env.local.sh"
if [[ -f "$ENV_FILE" ]]; then
  # Optional per-machine overrides (takes precedence over api_keys.sh).
  # shellcheck source=/dev/null
  source "$ENV_FILE"
fi

export IEEE_XPLORE_API_KEY="${IEEE_XPLORE_API_KEY:-}"
export IEEE_XPLORE_API_KEY_BACKUP="${IEEE_XPLORE_API_KEY_BACKUP:-}"
