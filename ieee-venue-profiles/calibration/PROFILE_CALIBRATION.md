# Profile calibration from IEEE Xplore corpus

Empirically refine `profiles/*.json` using recent representative papers per venue.

See [PATH_MODE.md](../PATH_MODE.md) for skill path variables.

## Prerequisites

```bash
AGENT_SKILLS=/path/to/agent-skills
IEEE_WRITING="$AGENT_SKILLS/ieee-writing"

bash "$IEEE_WRITING/ieee-literature-search/scripts/setup.sh"
bash "$AGENT_SKILLS/paper-pdf-fetch/scripts/setup.sh"
bash "$AGENT_SKILLS/paper-pipeline/analyze-research-paper/scripts/setup.sh"
```

## Phase 1 — Discover papers (pick one)

**Recommended: Web search + manual rows** — no API key, no BibTeX export required.

1. For each `profile_id` in `venue_targets.json`, web-search or browse IEEE Xplore.
2. Pick **10–20 representative** papers per profile (recent 3–5 years).
3. Append rows to `calibration/PAPERS.md` with Title, DOI, PDF link, and Profile.
4. Optional: add DOI to `reference.bib` via `ieee-manuscript-bib` later.

### Option B — IEEE Metadata API (batch automation, optional)

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
CALIBRATION_YEARS_BACK=5 \
  python3 "$IEEE_WRITING/ieee-venue-profiles/scripts/run_venue_calibration_search.py"
```

Outputs: `calibration/PAPERS.md`, `calibration/_corpus/search_results.json`.

### Option C — BibTeX import (no API)

Export from IEEE Xplore → `ieee-literature-search/scripts/import_bibtex.py` → append to `PAPERS.md`.

## Phase 2 — Download

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
export AGENT_SKILLS_ROOT="$AGENT_SKILLS"
bash "$IEEE_WRITING/ieee-venue-profiles/scripts/download_venue_corpus.sh"
```

PDFs land in `calibration/literature/<slug>/paper.pdf`.

## Phase 3 — Analyze

```bash
SKILL="$AGENT_SKILLS/paper-pipeline/analyze-research-paper"
CORPUS="$IEEE_WRITING/ieee-venue-profiles/calibration/literature"

for pdf in "$CORPUS"/*/paper.pdf; do
  bash "$SKILL/scripts/analyze_paper_batch.sh" "$pdf" "$CORPUS"
done
```

Update `PAPERS.md` analysis column when each `analysis.md` exists.

## Phase 4 — Venue signals

For each analyzed paper, read PDF + `analysis.md` and write `venue_signals.json` per `VENUE_SIGNAL_EXTRACT.md`.

## Phase 5 — Synthesize → patch profiles

```bash
python3 "$IEEE_WRITING/ieee-venue-profiles/scripts/synthesize_profile_signals.py"
```

Agent then edits `profiles/<profile_id>.json` and runs:

```bash
python3 "$IEEE_WRITING/ieee-venue-profiles/scripts/resolve_venue_profile.py" <id>
```

## Phase 6 — Validate

- [ ] `resolve_venue_profile.py` reads cleanly
- [ ] Patches cite ≥3 papers or one official exemplar
- [ ] `checklist` in profile matches synthesis
