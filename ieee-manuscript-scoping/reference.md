# IEEE Manuscript Scoping — Reference

## §1 Repository inventory (`repo_inventory.json`)

Produced by `scripts/scan_repo_for_paper.py`.

| Field | Description |
|-------|-------------|
| `repo_root` | Absolute path scanned |
| `readme` | `{path, title_line, headings[], has_problem, has_innovation}` |
| `package` | PyPI name from `pyproject.toml` if present |
| `entry_points` | CLI commands (`[project.scripts]`) |
| `configs` | Relative paths to `configs/*.yaml`, `configs/*.yml`, `*.yaml` at repo root |
| `paper` | `{main_tex_candidates[], writing_plan, reference_bib, scripts[], figure_data_dirs[]}` |
| `literature` | `{papers_md, slugs[{slug, has_analysis, has_pdf}]}` |
| `tests` | Test file paths (signals reproducibility) |
| `src_top_level` | Top-level packages under `src/` |
| `plot_script_hints` | Paths inferred from README or `tests/test_*figure*.py` when missing from `paper.scripts[]` |

Use inventory to **ground** contributions and asset paths — do not invent scripts or configs not listed. If `plot_script_hints` is non-empty but `paper.scripts[]` is empty, apply §8 (copy or create).

## §2 Scoping decisions (`scoping_decisions.json`)

Agent-authored after user checkpoints. Schema: `templates/scoping_decisions.example.json`.

Required keys: `venue`, `page_limit`, `title`, `contributions`, `figures`, `tables`, `sections`, `main_tex`.

Optional: `literature_slugs`, `simulation_defaults`, `evidence_boundary`, `keywords`, `authors_placeholder`.

## §3 Figure asset plan (`figure_asset_plan.json`)

Array of objects:

```json
{
  "id": "Fig. 1",
  "file": "figures/fig1_architecture.pdf",
  "claim": "Wrapper dataflow from strain controls to ΔV_th",
  "source_type": "concept_diagram",
  "repo_path": "paper/scripts/plot_ifetc_figures.py",
  "status": "exists",
  "column_span": "single",
  "notes": ""
}
```

`status`: `exists` | `needs_run` | `needs_design` | `blocked`

## §4 Writing plan sections

Minimum headings in `paper/writing_plan.md`:

1. Target (venue, pages, main TeX)
2. Narrative (problem → gap → method → evidence → so what)
3. Contributions (numbered, aligned with intro)
4. Section outline (per-section bullets)
5. Figures and tables (table with claim + source + status)
6. Simulation / reproduction commands
7. Handoff checklist (prose, figures, bib, layout skills)

## §5 TeX scaffold conventions

Generated TeX includes:

- Preamble from `ieee-manuscript-layout/templates/main.tex` (subset)
- `\title`, `\author` placeholders
- `\begin{abstract}` / `IEEEkeywords` comment stubs
- One `\section{}` per `sections[]` in decisions
- Commented `\begin{figure}` blocks per figure asset
- `% SCOPE:` comments for agent fill-in
- `\bibliography{./IEEEabrv,./reference}` block

Section labels: `sec:introduction`, `sec:methodology`, `sec:results`, `sec:conclusion` when names match defaults; otherwise slugified.

## §6 Checkpoint question bank

When inventory shows multiple valid narratives, ask:

1. Which contribution is **first** in the abstract?
2. Are results **device-level**, **circuit-level**, or **workflow/tool**?
3. Maximum figure count for page limit?
4. Any result explicitly **out of scope** for this submission?
5. Reuse existing `writing_plan.md` bullets or replace?

## §7 Integration with literature pipeline

| Literature artifact | Scoping use |
|--------------------|-------------|
| `analysis.md` → Prior art / Innovations | Intro gap, related-work bullets |
| `analysis.md` → Limitations | Bounded claims in conclusion |
| `PAPERS.md` | Bib keys to cite in intro |
| `tables_manifest.json` | Do not embed vendor table PNGs in new paper |

Run `ieee-literature-pipeline` before scoping when intro gap depends on analyzed prior art.

## §8 Figure script resolution (mandatory after scaffold)

Use `repo_inventory.json` + README **Outputs** / **Quick start** sections. Every simulation or concept figure in `scoping_decisions.json` must have a resolvable `repo_path` and `status`.

### Decision tree

```
paper.scripts[] non-empty?
  yes → point repo_path at listed script; status exists | needs_run
  no  → package CLI or configs/*.yaml drive results?
          yes → repo_path = "<config> + <cli command>"; status needs_run
                handoff: CREATE paper/scripts/plot_<slug>.py (ieee-manuscript-figures template)
          no  → tests import plot module?
                  yes → note gap; COPY from backup OR CREATE (user confirms)
          no  → concept_diagram only → status needs_design (ieee-manuscript-figures)
```

### `repo_path` field conventions

| Pattern | Example |
|---------|---------|
| Plot script | `paper/scripts/plot_ifetc_figures.py` |
| Config + CLI | `configs/bsim4_nmos_dynamic.yaml + strain-spice run --config ...` |
| Package module | `src/strain_spice/report.py (export only; add paper/scripts wrapper)` |
| Concept | `paper/scripts/plot_architecture.py (to create)` |

### Create vs copy

| Situation | Default | User override |
|-----------|---------|---------------|
| Test sandbox / no `paper/scripts/` | **Create** from `ieee-manuscript-figures/templates/generate_figures.template.py` | Copy from `paper-backup/scripts/` if user wants parity with prior submission |
| Canonical repo with backup | **Copy** from latest `paper-backup-*/scripts/` after user confirms | Create fresh if refactoring plots |
| CLI already writes `figures/*.svg` under run dir | Document move/plot step in `paper/scripts/`; do not duplicate simulation logic in prose | |

### `writing_plan.md` must record

```bash
# Figure reproduction (fill after resolution)
python paper/scripts/plot_<slug>_figures.py
# and/or
strain-spice run --config configs/<canonical>.yaml
```

### Handoff to `ieee-manuscript-figures` (mandatory for all plotting)

**Scoping ends at planning.** Do not execute plot or simulation commands in `ieee-manuscript-scoping`.

Invoke `@ieee-manuscript-figures` with:

- `paper/figure_asset_plan.json`
- `paper/writing_plan.md`
- `paper/0_main_ieee_conference.tex` (or project main TeX)

That skill owns:

1. Create or restore `paper/scripts/plot_*.py` (`templates/generate_figures.template.py` or backup copy)
2. Run simulation / plot commands; export to `paper/figures/*.pdf`
3. Claim-to-figure map, axis/caption hygiene (`reference.md` §1–§3)
4. Record commands under `## Regenerated assets` in its output

Prose linkage to figures comes later in `ieee-manuscript-prose` (revision order: prose → figures per `ieee-manuscript-revision`, or figures first when only assets are missing — user may run figures skill immediately after scoping).
