---
name: ieee-xplore-paper-search
description: >-
  Search IEEE Xplore for papers on a topic, dedupe against docs/PAPERS.md,
  and append index rows with DOI / Xplore links for manual PDF download.
  Use when the user asks to find IEEE papers, build a reading list, search
  Xplore for device/modeling/EDA topics, or populate PAPERS.md before analysis.
---

# IEEE Xplore Paper Search

> **This repo:** read [PROJECT.md](PROJECT.md) — index at `paper/literature/PAPERS.md`.

Discover papers on IEEE Xplore and append rows to `docs/PAPERS.md` (legacy *-lab layout) or **`paper/literature/PAPERS.md`** in this repo. **Do not paywall-bypass.** When PDFs are unavailable, link **DOI** and **IEEE Xplore** so the downloader or the user can fetch them through the environment's existing IEEE access.

Downstream flow:

1. Search and append pending rows with this skill
2. Download PDFs with [paper-pdf-fetch](../../paper-pdf-fetch/SKILL.md)
3. Analyze papers with [analyze-research-paper](../../paper-pipeline/analyze-research-paper/SKILL.md) after `paper.pdf` exists

## Prerequisites

```bash
bash ~/.cursor/skills/ieee-xplore-paper-search/scripts/setup.sh
```

Optional but recommended — IEEE Xplore Metadata API key (free registration):

1. Register at https://developer.ieee.org/
2. API keys are stored in **`scripts/api_keys.sh`** (primary + backup). `scripts/env.sh` loads them automatically.
   Optional overrides: `scripts/env.local.sh`.
   Scripts try **primary first**, then **backup** on HTTP 403 (inactive) or 429 (rate limit).

Without a key, use **manual export** (BibTeX/CSV from Xplore) or **WebFetch** on individual record pages — see [reference.md](reference.md).

## Workflow

Copy and track:

```
- [ ] Clarify topic, year range, venues, max results
- [ ] Search (API script, BibTeX import, or record URLs)
- [ ] Dedupe vs existing docs/PAPERS.md (DOI + normalized title)
- [ ] Assign categories (comparator-lab or serdes-lab tags)
- [ ] Append rows to docs/PAPERS.md (newest year first)
- [ ] Optional: scaffold papers/<slug>/ stub for each pending paper
- [ ] Hand off pending rows to paper-pdf-fetch or tell the user which DOIs still need manual download
```

### Step 1 — Build the query

Read topic presets in [reference.md](reference.md). For comparator-lab, prefer narrow queries (`dynamic comparator`, `SAR ADC offset calibration`, `dual comparator TI-SAR`) over bare `comparator`.

Translate user intent into:

| Parameter | Example |
|-----------|---------|
| `querytext` | `("dynamic comparator" OR strongARM) AND ("offset calibration" OR kickback)` |
| `start_year` / `end_year` | `2015` – `2026` |
| `publication_title` | `IEEE Journal of Solid-State Circuits` (optional filter) |
| `max_records` | default `25`, cap `200` |

### Step 2 — Run search

**Preferred (API):**

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-search
source "$SKILL/scripts/env.sh"   # loads IEEE_XPLORE_API_KEY if set

"$SKILL/scripts/run_python.sh" "$SKILL/scripts/search_ieee.py" \
  --query '("SAR ADC" AND comparator AND calibration)' \
  --start-year 2015 --max-records 30 \
  --output /tmp/ieee_hits.json

# Markdown rows ready to paste (includes DOI column)
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/search_ieee.py" \
  --query '("dual comparator" AND "time-interleaved")' \
  --start-year 2018 --format markdown \
  --category 'comparator-calibration, circuit-design'
```

**Manual export (no API key):**

1. Run Advanced Search on https://ieeexplore.ieee.org/
2. Export → BibTeX or CSV
3. Parse with:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/import_bibtex.py" \
  export.bib --format markdown --category 'comparator-calibration'
```

**Single record (DOI or Xplore URL known):**

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/fetch_record.py" \
  --doi 10.1109/LSSC.2020.3007580 --format markdown
```

### Step 3 — Dedupe before append

Before editing `docs/PAPERS.md`:

```bash
REPO=/path/to/comparator-lab   # or serdes-lab
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/dedupe_papers.py" \
  --index "$REPO/docs/PAPERS.md" \
  --candidates /tmp/ieee_hits.json
```

Skip rows already indexed (matching DOI or fuzzy title). Report skipped count to the user.

### Step 4 — Update docs/PAPERS.md

Index file: **`docs/PAPERS.md`** (legacy: `papers/PAPERS.md`).

**Pending download** (no local PDF yet) — extend the serdes-lab table with a **DOI** column:

```markdown
| Title | Authors | Year | Venue | Category | DOI | Analysis | PDF |
|-------|---------|------|-------|----------|-----|----------|-----|
| A 112-134-Gb/s PAM4 Receiver Using a 36-Way Dual-Comparator TI-SAR ADC in 7-nm FinFET | Pedro Wilson de Abreu Farias Neto et al. | 2020 | IEEE Solid-State Circuits Letters | comparator-calibration, circuit-design | [10.1109/LSSC.2020.3007580](https://doi.org/10.1109/LSSC.2020.3007580) | — | [IEEE Xplore](https://ieeexplore.ieee.org/document/9123456) |
```

Rules:

- Sort by **year descending** (newest first).
- Insert new rows **above** the `<!-- Add new rows` comment.
- **Analysis:** `—` until [analyze-research-paper](../../paper-pipeline/analyze-research-paper/SKILL.md) completes.
- **PDF:** `[IEEE Xplore](url)` or `[doi](https://doi.org/...)` when no `papers/<slug>/paper.pdf`.
- After the user downloads PDF → save as `papers/<slug>/paper.pdf` → run analyze skill → replace `—` with analysis/pdf links.

**Analyzed paper** (existing serdes-lab style — DOI optional in table, required in `analysis.md`):

```markdown
| ... | [10.1109/...](https://doi.org/10.1109/...) | [analysis](../papers/slug/analysis.md) | [pdf](../papers/slug/paper.pdf) |
```

### Step 5 — Optional scaffold

For each pending paper, create slug directory only (no fake analysis):

```bash
SLUG=a-112134-gb-s-pam4-receiver-using-a-36-way-dual-comparator-ti-sar-adc-in-7-nm-finfet
mkdir -p "$REPO/papers/$SLUG"
# User drops paper.pdf here after manual download
```

Slug rules: lowercase, ASCII hyphens, strip punctuation — same as analyze-research-paper.

### Step 6 — Open-access PDF (only when allowed)

If API metadata marks `is_open_access: true`, try:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_open_access.py" \
  --article-number 9123456 --out "$REPO/papers/$SLUG/paper.pdf"
```

If download fails or paper is not open access, **stop** and leave DOI/Xplore links for [paper-pdf-fetch](../../paper-pdf-fetch/SKILL.md) or manual fetch. Never scrape paywalled PDFs.

## Handoff to analysis

When the user adds `papers/<slug>/paper.pdf` or the PDF downloader skill applies it:

```bash
REPO=/path/to/agent-skills
SKILL="$REPO/paper-pipeline/analyze-research-paper"
bash "$SKILL/scripts/analyze_paper_batch.sh" \
  /path/to/repo/papers/slug/paper.pdf /path/to/repo/papers
```

Then update the PAPERS.md row: replace `—` / Xplore link in PDF column with `[pdf](../papers/slug/paper.pdf)`.

## Output checklist

Tell the user:

1. Query used and hit count (after dedupe)
2. Path to updated `docs/PAPERS.md`
3. List of DOIs needing manual download (with `https://doi.org/...` links)
4. Suggested priority order (venue, relevance to stated topic)
5. Whether `IEEE_XPLORE_API_KEY` was used or manual path was taken

## Categories (comparator-lab)

| Tag | Use for |
|-----|---------|
| `comparator-calibration` | Offset trim, auto-zero, kickback cal, dual-comp alignment |
| `comparator-modeling` | Trip, delay, hysteresis, kickback characterization |
| `circuit-design` | Transistor comparator, strongARM, latched topology |
| `sar-adc` | SAR slice / bit trial context |
| `flash-adc` | Flash threshold / bubble / redundancy |
| `serdes-transceiver` | Slicer / ADC-based RX (when comparator is secondary) |
| `survey` | Tutorials and overview papers |

Serdes-lab repos may use existing tags from analyze-research-paper `reference.md`.

## Additional resources

- Query templates and venue filters: [reference.md](reference.md)
- Row template: [templates/PAPERS-pending-row.md](templates/PAPERS-pending-row.md)
