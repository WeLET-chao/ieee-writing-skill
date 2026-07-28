---
name: ieee-tcad-journal-manuscript
description: >-
  Bootstraps and drafts IEEE TCAD-style journal manuscripts for CAD/EDA papers:
  journal IEEEtran split TeX, figure/table conventions, section narrative
  rhythm, BibTeX, and paper/ folder layout. Use when targeting IEEE TCAD,
  migrating from IEEE conference to journal format, or structuring
  simulation-in-the-loop / design-automation journal papers (not short conference
  drafts). Independent of any specific consumer repo folder.
---

# IEEE TCAD Journal Manuscript

## Scope

This skill covers **venue-level manuscript architecture** for IEEE Transactions on
Computer-Aided Design (TCAD) and similar IEEE **journal** CAD papers.

It complements (does not replace):

| Concern | Skill |
|---------|--------|
| Typography, float holes, page trimming | `ieee-latex-layout` |
| Matplotlib figure style | `ieee-manuscript-figures` |
| `reference.bib` hygiene | `ieee-bib-hygiene` |
| Prose tone, claim bounds | `ieee-manuscript-prose` |
| Outline / figure-table plan | `ieee-manuscript-scoping` |

Templates live in this skill (`templates/`). The consumer manuscript directory
(`PAPER_DIR`, default `paper/`) is chosen by the user — not part of this skill.

**Venue parameters** for all five manuscript pillars live in
`ieee-venue-profiles` — resolve `ieee-tcad-journal` (or active `profile_id`) before
drafting. This skill supplies **TeX templates and init scripts** when
`latex_template.template_skill` points here.

## When to use

- User says **TCAD**, **IEEE journal**, or **migrate conference → journal**
- Paper narrative is **CAD methodology** (flow, algorithms, reproducible artifacts), not a 2-page conference abstract
- Draft is too short, lacks tables/algorithms, or uses `\documentclass[conference]`

## Quick start

Initialize a TCAD journal tree:

```bash
PAPER_DIR=paper \
  .skills/ieee-tcad-journal-manuscript/scripts/init_tcad_journal.sh --bootstrap-tex
```

Build (after figures exist):

```bash
PAPER_DIR=paper \
  .skills/ieee-tcad-journal-manuscript/scripts/build_tcad_journal.sh
```

`PAPER_DIR` defaults to `<repo>/paper/` when unset.

## Workflow

Copy this checklist:

```
TCAD journal pass:
- [ ] 1. Template: journal,twoside + split files + TCAD front matter
- [ ] 2. Figures/tables: figure* flow, setup table, results table, algorithm
- [ ] 3. Narrative: intro taxonomy, paper map, bold result blocks, number sync
- [ ] 4. BibTeX: BST control, IEEEabrv, cite density in intro
- [ ] 5. Layout: figures/scripts/bib paths per PAPER_LAYOUT.md
- [ ] 6. Compile + page count (milestone **~8**; typical TCAD **10–12**; expand if <6)
```

### 1. LaTeX template

- Use `\documentclass[journal,twoside]{IEEEtran}` — **not** `conference`
- Main file: `0_main_ieee_trans.tex`; body via `\input{1_abstract_v1.tex}` …
- Include `\markboth`, `\IEEEpubid`, `\bstctlcite`, full author `\thanks`
- Preamble: `SIunits`, `algorithm`+`algorithmic`, `threeparttable`, `multirow`, `textcomp`, `textgreek` — see `templates/0_main_ieee_trans.tex`
- **Do not** use conference 7pt bibliography shrink hack

Details: [reference.md](reference.md) §1

### 2. Figures and layout

- Architecture / CAD flow → `figure*` at `0.95\textwidth`
- Bar charts, sweeps → single-column `width=9cm` or `\columnwidth`
- Every results claim needs a **table and/or figure**; prefer `table*` for SOTA comparison
- At least one **Algorithm** for the automated flow
- Data figures: `ieee-manuscript-figures` `plot_publication.py`
- Concept diagrams: vector PDF (not matplotlib-only) for submission quality

Details: [reference.md](reference.md) §2

### 3. Section structure and narrative

Default section map for CAD automation:

| Section file | Content |
|--------------|---------|
| `2_introduction_v1.tex` | Problem, prior-work **taxonomy**, contributions, paper map |
| `2b_related_work_v1.tex` | **Related Work** (own `\section{}` when draft ≥6 pages) |
| `3_methodology_v1.tex` | Problem formulation, flow, algorithms, implementation |
| `4_results_v1.tex` | Experimental setup, results with `\textbf{Block:}` subheads |
| `5_conclusion_v1.tex` | Conclusion and Discussion + Limitations |

Narrative rules: abstract numbers = body = tables; one-sentence-per-line `%` breaks optional; repeat headline metrics in intro and conclusion.

Details: [reference.md](reference.md) §3

### 4. BibTeX

- Keep `@IEEEtranBSTCTL{IEEEexample:BSTcontrol}` in `reference.bib`
- `\bibliography{./IEEEabrv,./reference}` — no font compression
- Intro carries **dense** citations classifying prior work; results cite evidence sources only when needed
- Comparison tables may use `\cite{key}` in column headers

Details: [reference.md](reference.md) §4

### 5. Directory layout

See [templates/PAPER_LAYOUT.md](templates/PAPER_LAYOUT.md).

Required: `figures/`, `scripts/`, `reference.bib`, `IEEEabrv.bib`, `.latexmkrc`  
Optional (host project): `literature/`, `writing_plan.md`, `photos/`, reproducibility or artifact dirs

## Migration: conference → journal

1. Run `init_tcad_journal.sh --bootstrap-tex` if split files missing
2. Move prose from monolithic `main.tex` into numbered `\input` files
3. Change `figure` → `figure*` for flow diagram; add Table I (setup) + Table II (summary)
4. Expand abstract to 8–12 short sentences with quantitative anchors
5. Add Algorithm 1; add `\markboth` / `\IEEEpubid`
6. Run `ieee-latex-layout` typography pass **after** content expansion

## Output

When applying this skill, report:

```markdown
## TCAD journal changes
- [file]: [template | figure | narrative | bib | layout]

## Page count
- Before: N | After: M | Target: 10--12

## Gaps vs TCAD bar
- [missing table | thin methodology | RW density | ...]

## Next skill
- ieee-manuscript-prose | ieee-latex-layout | ieee-manuscript-figures
```

## Additional resources

- Full rules: [reference.md](reference.md)
- Folder tree: [templates/PAPER_LAYOUT.md](templates/PAPER_LAYOUT.md)

## Skill maintenance

Consumer manuscripts may surface reusable TCAD patterns (tables, section splits,
checklists). **Promote only venue-generic patterns** into this skill's templates and
`reference.md`.

**Keep in the consumer repo** (see host `PROJECT.md` if present):

- Project narrative choices (e.g., LLM/agent framing, domain-specific scope terms)
- Evidence manifests, synced experiment trees, domain repo paths
- `SKILL_FEEDBACK.md` / `drafting_goal.md` with **User Decisions**

**Promotion criteria:** the pattern applies to TCAD CAD papers broadly (structure,
page budget, tables, RW split, reproducibility blocks) — not one paper's story.

Host-specific examples: [PROJECT.md](PROJECT.md) (PMIC and others as added).
