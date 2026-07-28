---
name: ieee-manuscript-scoping
description: Analyzes a research repository (README, code, configs, literature digests) to produce a paper writing plan, figure or table asset plan, and IEEE LaTeX manuscript scaffold before drafting. Use when starting a paper from a repo, refreshing paper/writing_plan.md, or deciding what to simulate versus draw for figures. Runs user confirmation checkpoints for venue, narrative axis, and evidence boundaries.
---

# IEEE Manuscript Scoping

> **This repo:** read [PROJECT.md](PROJECT.md) — default paths under `paper/`.

**Phase B Step 0** — before `ieee-manuscript-prose` or full `ieee-manuscript-revision`.

Turn a **code + README + optional literature** repository into:

1. `paper/writing_plan.md` — outline, story line, contributions, section notes
2. `paper/figure_asset_plan.json` — each figure/table: claim, source type, repo path, status
3. `paper/<main>.tex` — IEEE scaffold with section shells, figure/table placeholders, comment stubs

Do **not** skip user confirmation when narrative choices are ambiguous (see §Checkpoints).

## TCAD journal branch

When `ieee-venue-profiles` resolves to **`ieee-tcad-journal`**:

- Set `main_tex` to **`0_main_ieee_trans.tex`** (not `main.tex`)
- Defer split section files to **`ieee-manuscript-journal-tcad`** (`init_tcad_journal.sh`)
- Record **narrative axis and evidence boundaries** in `writing_plan.md` (from scoping checkpoints — project-specific)
- Page targets: first draft **~8**, typical TCAD **10–12** (see `ieee-manuscript-journal-tcad` reference §2)

## Conference short-paper branch

When `ieee-venue-profiles` resolves to **`ieee-conference-short`** (or similar short conference profile):

- Bootstrap TeX via **`ieee-manuscript-conference`** → `ieee-manuscript-layout/scripts/init_paper_assets.sh --bootstrap-tex`
- Keep `main.tex` monolith; page budget from venue profile
- Defer layout trim to `ieee-manuscript-layout` after prose/figures stabilize

## Prerequisites

- Python 3.10+ (stdlib only; no venv required)
- Optional: Phase A literature (`paper/literature/*/analysis.md`) for gap / prior-art mapping
- Optional: existing `paper/writing_plan.md` (skill **merges** or refreshes; use `--refresh-plan` to replace). **Back up human edits to `paper/manual/` first** (see [PROJECT.md](PROJECT.md)).

## Workflow checklist

```
- [ ] Resolve venue profile (`ieee-venue-profiles`) → set `profile_id` in plan
- [ ] Scan repo inventory
- [ ] User checkpoints (venue, narrative, evidence, figure budget)
- [ ] Write scoping_decisions.json
- [ ] Generate writing_plan + figure_asset_plan + TeX scaffold
- [ ] Plan figure assets in `figure_asset_plan.json` only — **do not run plot commands here**
- [ ] Hand off plotting to **`ieee-manuscript-figures`** (mandatory for `needs_run` / `needs_design`)
- [ ] Hand off prose to `ieee-manuscript-prose`
```

## Step 1 — Scan repository

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL="$REPO_ROOT/.cursor/skills/ieee-manuscript-scoping"
python3 "$SKILL/scripts/scan_repo_for_paper.py" \
  --repo-root "$REPO_ROOT" \
  --out "$REPO_ROOT/paper/out/scoping/repo_inventory.json"
```

Read `repo_inventory.json` plus root `README.md`. See [reference.md](reference.md) §1 for field meanings.

## Step 2 — User checkpoints (mandatory when ambiguous)

Use **AskQuestion** or explicit chat before generating artifacts. Minimum topics:

| Topic | Why |
|-------|-----|
| **Venue & page limit** | Caps figure count and section depth |
| **Primary narrative axis** | Repo may support multiple papers (tool vs physics vs case study) |
| **Evidence boundary** | What metrics appear in body (e.g. ΔV_th only vs I_D curves) |
| **Figure/table budget** | Must-have vs optional; single- vs double-column |
| **Literature slugs** | Which `analysis.md` files anchor intro gap vs bib only |
| **Simulation defaults** | Which `configs/*.yaml` or scripts are canonical for Table I / Results |

Record answers in `paper/out/scoping/scoping_decisions.json` (copy from
[templates/scoping_decisions.example.json](templates/scoping_decisions.example.json)).

## Step 3 — Generate plans and TeX scaffold

```bash
python3 "$SKILL/scripts/scaffold_manuscript.py" \
  --repo-root "$REPO_ROOT" \
  --decisions "$REPO_ROOT/paper/out/scoping/scoping_decisions.json" \
  --inventory "$REPO_ROOT/paper/out/scoping/repo_inventory.json"
```

Defaults (override in `scoping_decisions.json`):

| Output | Path |
|--------|------|
| Writing plan | `paper/writing_plan.md` |
| Asset plan | `paper/figure_asset_plan.json` |
| TeX scaffold | `paper/main.tex` or project `main_tex` name |
| Decisions copy | `paper/out/scoping/scoping_decisions.json` |

Before `--refresh-plan` on a repo with a hand-maintained plan, copy artifacts to `paper/manual/` (not overwritten by this skill).

Flags:

- `--bootstrap-tex` — create TeX only if missing (default)
- `--force-tex` — overwrite existing main TeX (dangerous; confirm with user)
- `--refresh-plan` — replace `writing_plan.md` entirely

## Step 4 — Plan figure assets (no plotting in this skill)

`ieee-manuscript-scoping` **does not regenerate figures**. It only records what each figure needs in `figure_asset_plan.json`. **All plotting** — create/copy `paper/scripts/`, run simulation exports, `savefig` to `paper/figures/`, caption hygiene — is done in the next skill:

```text
@ieee-manuscript-figures  (read SKILL.md; inputs: figure_asset_plan.json + writing_plan.md)
```

Follow [reference.md](reference.md) §8 to fill `repo_path`, `status`, and `notes` for each row.

Summary:

| Inventory signal | Action |
|------------------|--------|
| `paper.scripts[]` lists `plot_*.py` | Set `repo_path` to that file; `status`: `exists` or `needs_run` |
| Only `configs/` + package CLI (`strain-spice`, etc.) | `repo_path`: canonical config + CLI; `status`: `needs_run`; add handoff to create `paper/scripts/` |
| `source_type: concept_diagram` and no script | `status`: `needs_design`; handoff to `ieee-manuscript-figures` |
| Plot script named in `tests/test_*figures*.py` but missing under `paper/scripts/` | Note in `notes`; offer to **copy from paper backup** or **scaffold new script** (user confirms) |

Record intended commands in `writing_plan.md` §Simulation and reproduction as **placeholders** for `ieee-manuscript-figures` to implement. That skill may create `paper/scripts/` from `generate_figures.template.py`, copy from `paper-backup/scripts/` (user confirms), or wrap `strain-spice run` — see `ieee-manuscript-figures/SKILL.md` steps 1–8.

## Step 5 — Agent completes the scaffold

After figure paths are resolved:

1. Fill **comment stubs** in TeX (`% SCOPE: ...`) using `writing_plan.md`
2. Wire `\cite{}` keys that exist in `paper/reference.bib` or mark `% TODO: bibkey`
3. Do **not** run `python paper/scripts/...` or plot commands in this skill
4. Do **not** run `ieee-manuscript-revision` until `ieee-manuscript-figures` and prose exist

## Handoff

| Next | Skill | When |
|------|-------|------|
| **Figures & plots** | `ieee-manuscript-figures` | **Always** after scoping when any asset is `needs_run` or `needs_design` |
| Draft section prose | `ieee-manuscript-prose` |
| Bootstrap layout only | `ieee-manuscript-layout` (`init_paper_assets.sh`) |
| Full polish | `ieee-manuscript-revision` |

## Source types (`figure_asset_plan.json`)

| `source_type` | Meaning |
|---------------|---------|
| `simulation` | Run repo script / SPICE / Python plot |
| `concept_diagram` | Architecture or flow (TikZ, draw.io, scripted diagram) |
| `literature_adapt` | Redraw or cite; do not `\includegraphics` vendor PDF extracts |
| `manual` | Photo, layout screenshot, external artwork |
| `table_from_config` | Parameters from YAML/JSON |

## Common failures

- **Skipping checkpoints** — agent picks wrong narrative (e.g. I_D plots when plan says ΔV_th only)
- **Empty literature** — intro gap invented; run `ieee-literature-pipeline` first or note in plan
- **Overwriting good TeX** — use `--bootstrap-tex` without `--force-tex` on mature repos
- **Repo paths in abstract** — scaffold uses placeholders; prose skill removes paths later
- **Missing `paper/scripts/`** — set `needs_design` / `needs_run` in asset plan and follow §8; do not skip figure script handoff

## Additional resources

- Scan field reference: [reference.md](reference.md)
- This repo paths: [PROJECT.md](PROJECT.md)
- Writing plan template: [templates/writing_plan.md](templates/writing_plan.md)
