#!/usr/bin/env bash
# Quick grep pass for common IEEE prose issues (ieee-manuscript-prose/reference.md §4.1–§4.2).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
TEX_GLOB="${TEX_GLOB:-${REPO_ROOT}/paper/*.tex}"

echo "=== Semicolons in body (manual review) ==="
rg -n ';' ${TEX_GLOB} || true

echo
echo "=== Em dashes --- in non-comment TeX (must report / remove) ==="
# Ignore comment-only lines; still flag if --- appears before %.
rg -n '^[^%]*---' ${TEX_GLOB} || true

echo
echo "=== Informal figure verbs ==="
rg -n '\bplots\b|\bThus,\b|\bhides\b|\bforms a loop\b' ${TEX_GLOB} || true

echo
echo "=== Stiff For/To openers (sample) ==="
rg -n '^[[:space:]]*For (the|comparison)|^[[:space:]]*To (reveal|provide|execute)' ${TEX_GLOB} || true

echo
echo "Done. Rewrite hits using ieee-manuscript-prose/reference.md §4.1–§4.3."
