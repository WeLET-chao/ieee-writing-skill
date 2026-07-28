---
name: ieee-manuscript-figures
description: "Revises IEEE manuscript figures and captions for circuit, device, modeling, EDA, and measurement papers: claim-aligned plot types, axis/legend hygiene, caption takeaways, final figure paths under paper/figures/, and results discussion linked to plots. Use when editing figure scripts, regenerating plots, writing captions, or fixing figure-to-text mismatches."
---

# IEEE Manuscript Figures and Captions

## Canonical source

Read `reference.md` in this folder (local §1–§3). For results prose tone when
discussing figures, also read `ieee-manuscript-prose/reference.md` §4.1 and §5.

## Purpose

Ensure figures **test claims directly** and captions give reviewers an auditable
takeaway. Works with Python/Matlab/plot scripts or static assets.

## Inputs

- Manuscript: `paper/0_main_ieee_conference.tex` (or user path)
- Figure sources: `paper/figures/`, `paper/scripts/`, or user-specified plot code
- Config/data driving plots (YAML, CSV, simulation exports)
- **Venue profile:** `ieee-venue-profiles` → `min_figures`, `min_tables`, column span, concept diagram medium

## Execution workflow

1. **Claim-to-figure map** — For each figure, state which claim or comparison it
   supports; flag decorative-only diagrams.
2. **Figure type audit (§1)** — Prefer traces, baselines, ablations, sweeps,
   hysteresis/memory, error/residual, Pareto, or workflow diagrams when
   methodology-heavy.
3. **Plot hygiene**
   - Axis labels: symbol + units.
   - Consistent color mapping across related figures.
   - Readable legends; no axis collisions; legend not over markers.
   - Point labels: align by marker position in the axes (`ha=left` on the left
     side, `ha=right` on the right side) via `point_label_ha` so text stays
     inside the plot before visual QA.
   - Column-width survival: adjust canvas, line width, limits before LaTeX shrink.
4. **Data-plot correctness** — Common pitfalls:
   - Time-ordered quasi-static overlays (sort by x before plotting loops).
   - Staggered traces: disclose in caption or text.
   - Representative vs extracted parameters: match table/text provenance.
5. **Caption rewrite (§3)** — What is plotted, under what scope, main visual
   message; no full equation dump or invisible claims.
6. **Body linkage** — One tight paragraph per key figure: behavior, mechanism,
   bounded implication; use `ieee-manuscript-prose/reference.md` §4.1 tone.
7. **Asset path rule** — Commit finals under `paper/figures/`; avoid permanent
   `\includegraphics` paths to temp pipeline output.
8. **Regenerate** — Re-run plot scripts when code or data changed; record command
   in the summary.

## Scripts and templates

| Path | Purpose |
|------|---------|
| `scripts/plot_publication.py` | Canonical Matplotlib IEEE style (repo root shim re-exports this) |
| `templates/generate_figures.template.py` | Starter for new `paper/scripts/*.py` |

See `../ARTIFACTS.md` for commands.

## Build check

After figure or float edits:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
LAYOUT="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-layout)"
bash "$LAYOUT/scripts/build_paper.sh"
```

## Output

```markdown
## Figure revisions
- Fig. N: [plot/caption/text change]

## Regenerated assets
- [path]: [command used]

## Visual risks
- [readability / scaling / missing unit]

## Suggested next skill
- ieee-manuscript-layout | ieee-manuscript-final-review
```