---
name: ieee-manuscript-layout
description: >-
  Fixes IEEE LaTeX typography, float placement, and page-limit layout for
  circuit, device, modeling, EDA, and measurement manuscripts: number-unit
  spacing, ranges, textcomp micro-units, semicolon/dash hygiene, float
  specifiers, and ordered page-reduction steps. Use when the PDF is over page
  limit, has float holes, or needs IEEEtran typesetting cleanup.
---

# IEEE LaTeX Layout and Typography

## Canonical source

Read `reference.md` in this folder (local §1–§3). Visual checklist:
`ieee-manuscript-final-review/reference.md` §1–§2.

## Purpose

Fix **compiled PDF layout** and IEEE typography without damaging technical
content or bibliography integrity.

For **IEEE TCAD journal** document structure (split TeX, section narrative,
tables/algorithms, conference→journal migration), use
`ieee-manuscript-journal-tcad` first; then apply this skill for typography and
float cleanup.

**Always resolve the active venue profile** (`ieee-venue-profiles`) before
layout work — defaults in this skill assume short conference unless overridden.

## Inputs

- `paper/0_main_ieee_conference.tex` and includes
- `paper/.latexmkrc` (intermediate cleanup)
- Target page count from user or venue (this repo: 2-page IFETC conference)

## Typography pass (§1)

- Number–unit: `5~s`, `0.5~mV`
- Ranges: `1--5`, `0.02--0.10~s` (en dash)
- Percentages: `45.9\%` (no space before `\%`)
- Micro-units: `\usepackage{textcomp}` and `\text{\textmu m}`, `\text{\textmu W}`
- Notation consistent across abstract, text, figures, tables
- Acronyms expanded on first body mention
- No repo-local paths in submission prose
- **Do not use** em dashes (`---`) in body/caption/abstract prose; rewrite with commas, periods, or parentheses (`ieee-manuscript-prose/reference.md` §4.2). Hyphens (`carry-bypass`) and en dashes (`8--128`, `Kogge--Stone`) remain allowed.
- If any body `---` remains after the pass, **report each occurrence to the user** (do not silently leave them).
- Avoid semicolon chains (`ieee-manuscript-prose/reference.md` §4.2)

## Float pass (§2)

- Reduce `[H]` usage; prefer `[!t]` for two-column floats
- Use `figure*` only when full width is required
- Check section affinity for wide floats
- **Do not** fix layout by editing reference metadata
- **Table captions:** keep short (what the table is). Move definitions, parameter
  settings, metric formulas, and claim-scope notes into `\begin{tablenotes}...`
  under `threeparttable` (or an equivalent short note block). Do not paste
  methodology paragraphs into `\caption{...}`.

## Page-limit reduction order (§2)

When over the target page count, apply in order:

1. Remove redundant prose (coordinate with `ieee-manuscript-prose`)
2. Merge repeated sentences
3. Remove weak uncited references (`ieee-manuscript-bib`)
4. Adjust float placement and order
5. Reduce figure width only if readability remains acceptable
6. Last resort: reassess whether the page target is realistic

## Scripts and templates

| Path | Purpose |
|------|---------|
| `templates/PAPER_LAYOUT.md` | **`paper/` folder conventions** |
| `templates/main.tex` | IEEE conference preamble + section skeleton |
| `templates/IEEEtran.cls` | IEEE class (sync to `paper/` via init script) |
| `templates/IEEEabrv.bib` | Abbreviated journal strings |
| `templates/.latexmkrc` | Build PDF + remove intermediates on success |
| `scripts/init_paper_assets.sh` | Create `paper/` tree + install templates |
| `scripts/build_paper.sh` | `latexmk -pdf` + page count |

Starter `reference.bib`: `ieee-manuscript-bib/templates/reference.bib`

Initialize a new paper tree:

```bash
.cursor/skills/ieee-manuscript-layout/scripts/init_paper_assets.sh --bootstrap-tex
```

## Build workflow

```bash
.cursor/skills/ieee-manuscript-layout/scripts/build_paper.sh
```

## Output

```markdown
## Layout changes
- [file]: [float/typography/page fix]

## Page count
- Before: N | After: M | Target: T

## Residual layout risks
- [hole / overlap / unreadable figure]

## Suggested next skill
- ieee-manuscript-final-review
```
