#!/usr/bin/env bash
# Resolve absolute path to an ieee-writing skill directory.
#
# Usage:
#   SKILL="$(bash ieee-writing/scripts/skill_root.sh ieee-literature-search)"
#   bash "$SKILL/scripts/setup.sh"
#
# Override: export SKILL_ROOT=/path/to/skill  (must contain SKILL.md)
# Prefer:   export AGENT_SKILLS=/path/to/agent-skills meta repo
set -euo pipefail

name="${1:?usage: skill_root.sh <skill-name>}"

if [[ -n "${SKILL_ROOT:-}" ]]; then
  echo "$SKILL_ROOT"
  exit 0
fi

candidates=()

if [[ -n "${AGENT_SKILLS:-}" ]]; then
  candidates+=("$AGENT_SKILLS/ieee-writing/$name")
fi

if [[ -d "${HOME}/.agents/skills/$name" ]]; then
  candidates+=("${HOME}/.agents/skills/$name")
fi

repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -n "$repo" ]]; then
  candidates+=("$repo/ieee-writing/$name" "$repo/.cursor/skills/$name")
fi

ieee_writing_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
candidates+=("$ieee_writing_root/$name")

for c in "${candidates[@]}"; do
  if [[ -d "$c" && -f "$c/SKILL.md" ]]; then
    echo "$c"
    exit 0
  fi
done

echo "skill_root: cannot resolve $name (set AGENT_SKILLS or SKILL_ROOT)" >&2
exit 1
