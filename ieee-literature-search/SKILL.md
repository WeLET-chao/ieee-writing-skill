---
name: ieee-literature-search
description: "Search IEEE Xplore for papers on a topic, dedupe against paper/literature/PAPERS.md, and append index rows with DOI / Xplore links for PDF download. Use when the user asks to find IEEE papers, build a reading list, search Xplore for device/modeling/EDA topics, or populate PAPERS.md before analysis."
---

# IEEE Literature Search

> **Paths:** [PATH_MODE.md](../PATH_MODE.md) · consumer example [PROJECT.md](PROJECT.md)

Search IEEE Xplore and append rows to **`paper/literature/PAPERS.md`**. **Do not paywall-bypass.** When PDFs are unavailable, link **DOI** and **IEEE Xplore** so **`paper-pdf-fetch`** or institutional access can fetch them.

Orchestrator: **`ieee-literature-pipeline`**.

## Layout (canonical)

| Path | Role |
|------|------|
| `paper/literature/PAPERS.md` | Literature index table |
| `paper/literature/<slug>/` | Per-paper folder (PDF + digest) |
| `paper/literature/<slug>/paper.pdf` | Downloaded PDF |
| `paper/literature/<slug>/analysis.md` | After **`analyze-research-paper`** |

Legacy `docs/PAPERS.md` / `papers/<slug>/` layouts: [reference.md § Legacy layouts](reference.md#legacy-layouts).

## Downstream

1. **This skill** — search, dedupe, append pending rows
2. **`paper-pdf-fetch`** — download into `paper/literature/<slug>/paper.pdf`
3. **`analyze-research-paper`** — write `analysis.md`, update PAPERS.md Analysis/PDF columns

## Prerequisites

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-search)"
bash "$SKILL/scripts/setup.sh"
```

IEEE Xplore Metadata API key (recommended): register at https://developer.ieee.org/, copy `scripts/api_keys.sh.example` → `scripts/api_keys.sh`. `scripts/env.sh` loads primary + backup keys (failover on 403/429). Without a key, use manual BibTeX export — [reference.md](reference.md).

## Workflow

```
- [ ] Clarify topic, year range, venues, max results
- [ ] Search (API, BibTeX import, or single DOI/record)
- [ ] Dedupe vs paper/literature/PAPERS.md (DOI + normalized title)
- [ ] Assign category tags (comma-separated; see reference.md)
- [ ] Append rows (newest year first)
- [ ] Optional: mkdir paper/literature/<slug>/ for each pending paper
- [ ] Hand off to paper-pdf-fetch or list DOIs still needing download
```

### Step 1 — Build the query

Read [reference.md](reference.md) for boolean `querytext` presets, venue filters, and domain-specific examples.

| Parameter | Example |
|-----------|---------|
| `querytext` | `("flexible electronics" AND strain AND TFT)` |
| `start_year` / `end_year` | `2018` – `2026` |
| `publication_title` | `IEEE Transactions on Electron Devices` (optional) |
| `max_records` | default `25`, cap `200` |

### Step 2 — Run search

Set `SKILL` once per shell session:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
AGENT_SKILLS="${AGENT_SKILLS:-$REPO_ROOT}"
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-search)"
PAPERS_MD="$REPO_ROOT/paper/literature/PAPERS.md"
source "$SKILL/scripts/env.sh"

# JSON for dedupe pipeline
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/search_ieee.py" \
  --query '("level shifter" AND low power)' \
  --start-year 2015 --max-records 30 \
  --output /tmp/ieee_hits.json

# Markdown rows ready to paste
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/search_ieee.py" \
  --query '("BSIM" AND strain AND modeling)' \
  --start-year 2018 --format markdown \
  --category 'device-modeling, compact-model'
```

**Manual export (no API key):** Xplore Advanced Search → Export BibTeX → `import_bibtex.py`.

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/import_bibtex.py" \
  export.bib --format markdown --category 'prior-art'
```

**Single record (DOI or Xplore URL):**

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/fetch_record.py" \
  --doi 10.1109/TCAD.2024.3435692 --format markdown
```

### Step 3 — Dedupe before append

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/dedupe_papers.py" \
  --index "$PAPERS_MD" \
  --candidates /tmp/ieee_hits.json
```

Report how many candidates were skipped (duplicate DOI or fuzzy title match).

### Step 4 — Update PAPERS.md

Row template: [templates/PAPERS-pending-row.md](templates/PAPERS-pending-row.md).

**Pending download** (no local PDF):

```markdown
| Title | Authors | Year | Venue | Category | DOI | Analysis | PDF |
|-------|---------|------|-------|----------|-----|----------|-----|
| RoSE-Opt: Robust and Efficient Analog Circuit Parameter Optimization ... | W. Cao et al. | 2025 | IEEE TCAD | cad, analog-sizing | [10.1109/TCAD.2024.3435692](https://doi.org/10.1109/TCAD.2024.3435692) | — | [IEEE Xplore](https://ieeexplore.ieee.org/document/10614385) |
```

Rules:

- Sort by **year descending** (newest first).
- Insert new rows **above** any `<!-- Add new rows` comment.
- **Analysis:** `—` until **`analyze-research-paper`** completes.
- **PDF:** `[IEEE Xplore](url)` until `paper/literature/<slug>/paper.pdf` exists.
- After download → update PDF column to `[pdf](<slug>/paper.pdf)` (relative to `paper/literature/`).

**Analyzed paper:**

```markdown
| ... | [10.1109/...](https://doi.org/...) | [analysis](<slug>/analysis.md) | [pdf](<slug>/paper.pdf) |
```

### Step 5 — Optional scaffold

```bash
SLUG=rose-opt-robust-and-efficient-analog-circuit-parameter-optimization
mkdir -p "$REPO_ROOT/paper/literature/$SLUG"
# paper-pdf-fetch or user drops paper.pdf here
```

Slug rules: lowercase, ASCII hyphens — same as **`analyze-research-paper`** ([reference.md § Slug](reference.md#slug-from-title)).

## Handoff

**Download** (batch from PAPERS.md):

```bash
SKILL=paper-pdf-fetch   # or resolve via AGENT_SKILLS/paper-pdf-fetch
python3 "$SKILL/scripts/fetch_from_papers_md.py" \
  --repo-root "$REPO_ROOT" \
  --papers-md "$PAPERS_MD" \
  --resume
```

**Analyze** one PDF:

```bash
ANALYZE="$AGENT_SKILLS/paper-pipeline/analyze-research-paper"
bash "$ANALYZE/scripts/analyze_paper_batch.sh" \
  "$REPO_ROOT/paper/literature/$SLUG/paper.pdf" \
  "$REPO_ROOT/paper/literature"
```

Then update the PAPERS.md row Analysis and PDF columns.

## Output checklist

Tell the user:

1. Query used and hit count (after dedupe)
2. Path to updated `paper/literature/PAPERS.md`
3. DOIs still needing download (`https://doi.org/...` links)
4. Suggested priority (venue, relevance)
5. Whether API key was used or manual path was taken

## Additional resources

- API, queries, categories, legacy paths: [reference.md](reference.md)
- Pending row template: [templates/PAPERS-pending-row.md](templates/PAPERS-pending-row.md)