# Project integration (strained-device-model)

Run corpus extraction on analyzed digests under **`paper/literature/`**:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL="$REPO_ROOT/.cursor/skills/ieee-literature-synthesize"
python3 "$SKILL/scripts/extract_corpus.py" "$REPO_ROOT/paper/literature"
python3 "$SKILL/scripts/aggregate_corpus.py" "$REPO_ROOT/paper/literature/_corpus/extracted.json"
```

Write synthesis report to `paper/literature/RESEARCH_ANALYSIS.md` or `docs/RESEARCH_ANALYSIS.md` as preferred.

Orchestrator: `ieee-literature-pipeline/SKILL.md`.
