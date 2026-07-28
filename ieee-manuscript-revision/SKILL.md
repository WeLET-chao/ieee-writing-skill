---
name: ieee-manuscript-revision
description: >-
  Orchestrates end-to-end IEEE manuscript revision for circuit, device,
  modeling, EDA, and measurement papers using ieee-manuscript-prose, figures,
  bib, layout, and final-review skills. Use when the user asks for a full paper
  polish, pre-submission revision pass, or IEEE guidelines review on paper/*.tex.
---

# IEEE Manuscript Revision (Orchestrator)

## Canonical source

Split across sub-skill `reference.md` files. See `guidelines-index.md` in this
folder for the full §-to-skill map.

## Purpose

Run a **ordered, topic-agnostic** revision pass on an existing IEEE LaTeX
manuscript. Default paths match this repository's `paper/` layout.

## Inputs

Required:

- Main TeX: `paper/0_main_ieee_conference.tex` (override if user specifies)
- Bibliography: `paper/reference.bib`
- Rules index: `guidelines-index.md` (this folder)

Optional:

- Plot scripts under `paper/scripts/`
- Target page count and venue name from user

## Sub-skills (read `SKILL.md` + `reference.md` before executing)

| Order | Skill | Rules | Workflow |
|-------|-------|-------|----------|
| 1 | Prose and claims | `ieee-manuscript-prose/reference.md` | `ieee-manuscript-prose/SKILL.md` |
| 2 | Figures and captions | `ieee-manuscript-figures/reference.md` | `ieee-manuscript-figures/SKILL.md` |
| 3 | Bibliography | `ieee-manuscript-bib/reference.md` | `ieee-manuscript-bib/SKILL.md` |
| 4 | Layout and compile | `ieee-manuscript-layout/reference.md` | `ieee-manuscript-layout/SKILL.md` |
| 5 | Final gate | `ieee-manuscript-final-review/reference.md` | `ieee-manuscript-final-review/SKILL.md` |

## Execution contract

Run stages **in order**. After each stage, note residual issues before continuing.

1. **Prose** — Claim map, abstract/intro/conclusion alignment (`ieee-manuscript-prose`).
2. **Figures** — Regenerate if needed; fix captions and results linkage.
3. **Bibliography** — Verify cited entries; conference `booktitle` acronyms;
   journal abbreviations only if chosen for layout (`ieee-manuscript-bib` §7).
4. **Layout** — Typography, floats, page-limit fixes; compile.
5. **Final review** — Visual PDF pass + checklist (`ieee-manuscript-final-review` §2).

If the user requests **review-only**, stop after stage 5 without further edits.

**After reviews:** use `ieee-manuscript-rebuttal` for the response letter (orthogonal to the polish pass above).

If a stage finds P0 blockers, fix them before downstream stages when feasible
(e.g., wrong figure undermines prose in stage 1).

## Templates

| Path | Purpose |
|------|---------|
| `templates/writing_plan.md` | Section/figure revision outline |

Installed into `paper/` by `ieee-manuscript-layout/scripts/init_paper_assets.sh --bootstrap-tex`.

## Scripts

Sub-skill scripts are listed in `../ARTIFACTS.md`. Typical full pass:

```bash
.cursor/skills/ieee-manuscript-layout/scripts/init_paper_assets.sh
# edit prose / figures / bib per sub-skills
.cursor/skills/ieee-manuscript-final-review/scripts/build_and_review.sh
```

## Default behavior

- **Execute revisions** unless the user asks for review-only.
- Keep diffs minimal and evidence-aligned.
- Do not invoke archived adder skills under `_archive/adder-design/`.

## Final deliverables

- Updated `paper/*.tex`, `paper/reference.bib`, `paper/figures/` as needed
- `paper/final_review.md` with readiness status and residual gaps
- Chat summary: page count, top 3 risks, next user action

## Invoke examples

- `@ieee-manuscript-revision` polish the IFETC draft
- `@ieee-manuscript-prose` only tighten Sec. III
- `@ieee-manuscript-bib` verify all cited entries
