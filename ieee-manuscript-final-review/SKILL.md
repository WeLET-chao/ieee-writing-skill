---
name: ieee-manuscript-final-review
description: >-
  Runs pre-submission final review for IEEE manuscripts on circuit, device,
  modeling, EDA, and measurement topics: compile PDF, visual page inspection,
  final checklist, unresolved references, and P0/P1 blocker summary. Use when
  asking if a paper is submission-ready or before uploading to a conference
  portal.
---

# IEEE Manuscript Final Review

## Canonical source

Read `reference.md` in this folder (local §1 visual review, §2 final checklist).

## Purpose

Gate submission readiness with a **repeatable compile + visual + checklist**
pass. Topic-agnostic.

## Inputs

- `paper/0_main_ieee_conference.tex`
- `paper/reference.bib`
- `paper/figures/`
- Target page count (user-specified; default 2 for this repo's IFETC draft)

## Execution workflow

### 1. Compile

```bash
.cursor/skills/ieee-manuscript-final-review/scripts/build_and_review.sh
```

Or separately: `ieee-latex-layout/scripts/build_paper.sh` then
`ieee-manuscript-final-review/scripts/render_pdf_pages.sh`.

Treat LaTeX exit status as necessary but not sufficient.

### 2. Visual PDF review (reference.md §1)

Rasterize pages for inspection:

```bash
.cursor/skills/ieee-manuscript-final-review/scripts/render_pdf_pages.sh
```

Check:

- page count vs target
- unresolved references or citations
- overfull boxes, text overlap
- figure and legend readability
- caption proximity
- table scaling
- last-page column balance
- reference spill
- float order and unexplained white holes

### 3. Final checklist (reference.md §2)

Work through every item in `reference.md` §2.
Mark pass/fail; failed items become P0 or P1.

### 4. Route fixes

| Failure type | Skill |
|--------------|-------|
| Claim scope, prose tone | `ieee-manuscript-prose` |
| Caption, plot, figure path | `ieee-manuscript-figures` |
| Bib metadata | `ieee-bib-hygiene` |
| Float holes, units, page count | `ieee-latex-layout` |

### 5. Optional external visual QA

If the user has Gemini CLI and wants deeper figure/layout critique, they may
run a manual visual review workflow. Archived adder-specific automation lives
at `.cursor/skills/_archive/adder-design/pdf-visual-qa-gemini/`.

## Output artifact

Save to `paper/final_review.md` (or user path):

```markdown
## Submission readiness
- Status: ready | needs revision
- Page count: N / target T

## Checklist
- [x] item ...
- [ ] item ... → P0/P1

## Visual review
- [page/issue]

## P0 blockers
- ...

## P1 improvements
- ...

## Commands run
- ...
```

Provide a short inline summary in chat; treat `final_review.md` as canonical.
