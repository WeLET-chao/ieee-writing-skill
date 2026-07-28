# Profile calibration from IEEE Xplore corpus

Empirically refine `profiles/*.json` using recent representative papers per venue.

## Prerequisites

```bash
# Search skill (optional — only for API/BibTeX batch paths)
bash PMIC/.skills/ieee-xplore-paper-search/scripts/setup.sh

# Downloader (paper-pdf-fetch in agent-skills)
bash /path/to/agent-skills/paper-pdf-fetch/scripts/setup.sh

# Analyze skill
bash PMIC/.skills/analyze-research-paper/scripts/setup.sh
```

## Phase 1 — Discover papers (pick one)

**Recommended: Web search + manual rows** — no API key, no BibTeX export required.

1. For each `profile_id` in `venue_targets.json`, web-search or browse IEEE Xplore, e.g.:
   - `ieee-tcad-journal`: site:ieeexplore.ieee.org TCAD analog design automation 2024
   - `ieee-tcas-i-journal`: site:ieeexplore.ieee.org TCAS-I LDO amplifier 2023..2025
   - `ieee-conference-short`: ICCAD DAC analog LLM CAD 2024
2. Pick **10–20 representative** papers per profile (recent 3–5 years).
3. Append rows to `calibration/PAPERS.md` with **Title, DOI, PDF link** (`IEEE Xplore` or `ACM DL` for `10.1145/*` ICCAD/DAC papers), and **Profile**.
4. Optional: add DOI to `reference.bib` via `ieee-bib-hygiene` later.

Web search is enough for **discovery**. It does not download PDFs.

### Option B — IEEE Metadata API (batch automation, optional)

Only if `api_keys.sh` keys are **activated** on developer.ieee.org:

```bash
cd PMIC
CALIBRATION_YEARS_BACK=5 \
  python3 .skills/ieee-venue-profiles/scripts/run_venue_calibration_search.py
```

Outputs: `calibration/PAPERS.md`, `calibration/_corpus/search_results.json`.

### Option C — BibTeX import (no API)

Export from IEEE Xplore Advanced Search → `import_bibtex.py` → append to `PAPERS.md`.

## Phase 2 — Download

Requires working IEEE Xplore access in this environment. ICCAD/DAC papers with `10.1145/*` DOIs may use **ACM Digital Library** PDF links; if automated ACM download is blocked (Cloudflare), use the publisher **arXiv** open PDF for the same paper.

```bash
cd PMIC
.skills/ieee-venue-profiles/scripts/download_venue_corpus.sh
# Optional: MAX_PAPERS=10 per batch, re-run with --resume
```

PDFs land in `calibration/literature/<slug>/paper.pdf`.

## Phase 3 — Analyze

```bash
SKILL=PMIC/.skills/analyze-research-paper
CORPUS=PMIC/.skills/ieee-venue-profiles/calibration/literature

for pdf in "$CORPUS"/*/paper.pdf; do
  bash "$SKILL/scripts/analyze_paper_batch.sh" "$pdf" "$CORPUS"
done
```

Update `PAPERS.md` analysis column when each `analysis.md` exists.

## Phase 4 — Venue signals

For each analyzed paper, agent reads PDF + `analysis.md` and writes `venue_signals.json` per `VENUE_SIGNAL_EXTRACT.md`.

Focus on the target's `calibration_focus` fields in `venue_targets.json`.

## Phase 5 — Synthesize → patch profiles

```bash
python3 PMIC/.skills/ieee-venue-profiles/scripts/synthesize_profile_signals.py
```

Produces `calibration/_corpus/profile_synthesis_report.md` with:

- per-profile medians (pages, figures, tables, abstract sentences)
- suggested JSON patches per pillar
- outliers to ignore

Agent then edits `profiles/<profile_id>.json` and runs:

```bash
python3 .skills/ieee-venue-profiles/scripts/resolve_venue_profile.py <id>
```

## Phase 6 — Validate

- [ ] `resolve_venue_profile.py` reads cleanly
- [ ] Patches cite ≥3 papers or one official exemplar
- [ ] `checklist` in profile matches synthesis
- [ ] Host manuscript (`PAPER_DIR`) unchanged unless user opts in

## Maintenance

| Event | Action |
|-------|--------|
| New target venue | Add `venue_targets.json` entry + empty profile from `_template.json` |
| IEEE changes template | Re-run phases 1–5 for that `profile_id` only |
| paper_writing lesson | Update profile pillar field + note source slug in `agent_notes` |

Corpus stays under `ieee-venue-profiles/calibration/` — independent of consumer repos.
