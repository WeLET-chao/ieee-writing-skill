---
name: ieee-literature-pipeline
description: "Orchestrates IEEE literature search, PDF download, per-paper analysis, and optional corpus synthesis for this repository. Uses paper/literature/PAPERS.md and integrates with ieee-manuscript-bib and ieee-manuscript-prose. Use when building a reading list, downloading Xplore PDFs, analyzing prior art, or synthesizing related-work themes before writing the manuscript."
---

# IEEE Literature Pipeline (this repo)

## Paths (project-specific)

| Path | Role |
|------|------|
| `paper/literature/PAPERS.md` | Literature index table |
| `paper/literature/<slug>/paper.pdf` | Downloaded PDF |
| `paper/literature/<slug>/analysis.md` | Structured digest |
| `paper/references/<bibkey>.pdf` | Cited-entry PDFs for bib verification |

Skill root (repo-local):

```bash
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PAPERS_MD="$REPO_ROOT/paper/literature/PAPERS.md"
```

See [PATH_MODE.md](../PATH_MODE.md) for symlink and consumer-embedded paths.

## Sub-skills

| Step | Skill | Setup |
|------|-------|-------|
| 1 Search | `ieee-literature-search` | `bash "$REPO_ROOT/ieee-writing/ieee-literature-search/scripts/setup.sh"` |
| 2 Download | `paper-pdf-fetch` (unified: IEEE → Sci-Hub → scansci) | `bash paper-pdf-fetch/scripts/setup.sh` |
| 3 Analyze | `analyze-research-paper` | `bash "$REPO_ROOT/paper-pipeline/analyze-research-paper/scripts/setup.sh"` |
| 4 Synthesize | `ieee-literature-synthesize` | (uses repo `_corpus/`; no venv required for extract) |

Copy `ieee-literature-search/scripts/api_keys.sh.example` → `api_keys.sh` before search.

## Typical commands

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
AGENT_SKILLS="${AGENT_SKILLS:-$REPO_ROOT}"

# Search → append rows to PAPERS.md (example)
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-search)"
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/search_ieee.py" \
  --query '("flexible electronics" AND strain AND TFT)' \
  --start-year 2018 --max-records 20 --format markdown

# Download pending PDFs into paper/literature/<slug>/
SKILL=paper-pdf-fetch
python3 "$SKILL/scripts/fetch_from_papers_md.py" \
  --repo-root "$REPO_ROOT" \
  --papers-md "$REPO_ROOT/paper/literature/PAPERS.md" \
  --resume

# Analyze one PDF
SKILL="$REPO_ROOT/paper-pipeline/analyze-research-paper"
bash "$SKILL/scripts/analyze_paper_batch.sh" \
  "$REPO_ROOT/paper/literature/<slug>/paper.pdf" \
  "$REPO_ROOT/paper/literature"

# Corpus synthesis (after many analysis.md files exist)
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-synthesize)"
python3 "$SKILL/scripts/extract_corpus.py" "$REPO_ROOT/paper/literature"
```

## Handoff to manuscript skills

- New citations → add verified entries to `paper/reference.bib` (`ieee-manuscript-bib`)
- Intro / related work → `ieee-manuscript-prose`
- Figures from analyzed papers → do not `\includegraphics` vendor extracts; regenerate for claims

## Notes

- Step 2 uses **`paper-pdf-fetch`** — single skill with auto-cascade backends and CSV/JSON/PAPERS.md inputs.
- In this repository, canonical paths are `ieee-writing/` and `paper-pipeline/` under repo root.
- Each skill's `scripts/setup.sh` creates a local `.venv` inside that skill folder (gitignored).