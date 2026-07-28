# Figures, Tables, and Captions

Topic-agnostic rules for IEEE short papers. Skill: `ieee-manuscript-figures`.

For results **prose tone** when discussing figures, also apply
`ieee-manuscript-prose/reference.md` §4.1 and §5.

## 1. Figures

Figures should test or clarify claims directly. Architecture diagrams are useful
only when they explain a method that later figures evaluate.

High-value figure types:

- architecture or flow diagram with correct signal/data order,
- representative transient trace,
- measured/simulated comparison against a baseline,
- ablation plot,
- parameter or sensitivity sweep,
- hysteresis or memory-behavior plot,
- error distribution or residual plot,
- Pareto-style trade-off plot,
- reproducibility or workflow diagram when the paper is methodology-heavy.

Figure requirements:

- Axis labels must include symbols and units.
- Legends must be readable and not collide with axes **or data markers**.
- Color mapping should remain consistent across related figures.
- Captions should state the takeaway and scope, not repeat the whole method.
- If profiles or amplitudes are staggered for visibility, say so in text or
  caption.
- Generated figures should be stored under the paper's `figures/` directory,
  not permanently included from temporary output paths.

### Point-label alignment (prevent overflow before visual QA)

For scatter / Pareto / annotated marker plots, choose horizontal alignment from
the marker's **relative x position inside the axes**, not from a fixed
`ha="left"` for every label:

| Marker location in x-span | Prefer `ha=` | Why |
|---------------------------|--------------|-----|
| Left third of the plot | `left` | Label grows **into** the axes (rightward) |
| Right third of the plot | `right` | Label grows **into** the axes (leftward) |
| Middle third | `center` (or local override) | Avoids favoring one spine |

Use the same idea on y when labels sit near the top/bottom spine (`va="top"`
near the top edge, `va="bottom"` near the bottom edge).

Place the text anchor at the marker's data `x` (same abscissa), then set `ha`
as above. Do **not** offset long labels further outward past the spine.

Prefer the shared helper `point_label_ha(x, x_min, x_max)` from
`scripts/plot_publication.py` after axis limits are known. Apply this at
**plot generation time** so Gemini / PDF visual QA is not the first filter for
labels clipped by the axes box.

Also place legends in empty regions (often upper-right when left-side points are
dense); never leave a legend on top of markers.

For IEEE short papers, prefer figures that can survive column-width scaling.
If a figure needs fine curve separation, adjust canvas size, line width, legend
placement, and axis limits before shrinking it in LaTeX.

### Matplotlib Publication Style

Use `scripts/plot_publication.py` as the single source of truth for generated
Matplotlib figures. New paper-specific plotting scripts should import
`PALETTE`, `figsize_publication()`, `apply_publication_style()`, and
`savefig_publication()` rather than redefining style constants.

Current canonical style constraints:

- Default export DPI: `180`.
- Single-panel canvas: `1600 x 900 px`; use `figsize_publication()` for
  proportional multi-panel layouts.
- Palette: black, blue, red, purple, green, and orange, with stable semantic
  aliases in `PALETTE`.
- Font family: Arial first, then DejaVu Sans / sans-serif fallbacks.
- Font weight: bold for labels, titles, and tick text.
- Default font size: `18 pt` for axes labels, ticks, legends, and titles.
- Default line width: `3.0`; default marker size: `12.0`.
- Axis spine width: `3.0`.
- Default grid: dashed, `linewidth=0.5`, `alpha=0.6`.
- Figure titles inside axes should normally be omitted at export time; use the
  manuscript caption and body text for context.
- Point labels: use `point_label_ha(...)` (see above) rather than hard-coding
  `ha="left"` for every annotated marker.

For PASS/FAIL matrices, use the helper heatmap convention in
`plot_publication.py`: red for failure, green for pass, and a discrete patch
legend rather than a continuous colorbar.

## 2. Tables

Tables should let reviewers audit conditions quickly.

High-value table types:

- evaluation parameter table,
- baseline comparison table,
- ablation summary,
- measurement setup table,
- model-parameter provenance table,
- reproducibility table,
- threats-to-validity table when space allows.

Table requirements:

- Use consistent precision.
- Include units in headers or entries.
- Avoid excessive `N/A`; split the table if needed.
- State parameter provenance clearly.
- Distinguish literature-based parameters from representative settings or
  assumed demonstration values.

A table can create a false impression that every listed value is literature
extracted. Add a short provenance sentence after the table when needed.

## 3. Caption Rules

Captions should be concise and takeaway-oriented.

Good captions include:

- what is plotted,
- under what scope or condition,
- the main visual message.

Avoid captions that:

- restate all equations,
- include excessive implementation detail,
- make claims not visible in the figure,
- hide important caveats from the main text.

Example pattern:

```latex
\caption{Representative transient strain modes and dynamic
$\Delta V_{\mathrm{th}}$ responses.}
```

Then use the body text to explain why the behavior matters.
