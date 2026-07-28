---
name: ieee-manuscript-prose
description: >-
  Applies IEEE short-paper prose revision rules for circuit, device, modeling,
  EDA, and measurement manuscripts: claim scope, problem-mechanism-evidence
  chain, abstract/intro/conclusion alignment, objective methodology wording,
  semicolon avoidance, causal phrasing, and results tone. Use when polishing
  IEEE LaTeX text, revising abstract/introduction/conclusion, or improving
  figure-discussion paragraphs in paper/*.tex.
---

# IEEE Manuscript Prose Revision

## Canonical source

Read `reference.md` in this folder (local §1–§5). Section numbers are
**skill-local** only.

## Purpose

Revise manuscript **prose** so claims, structure, and tone meet IEEE short-paper
expectations. Topic-agnostic: circuits, devices, models, EDA flows, measurements.

## Inputs

Required (defaults for this repo; override when user specifies paths):

- `paper/0_main_ieee_conference.tex` (or user-provided `*.tex`)
- Supporting sections/includes referenced by the main file
- **Venue profile:** `ieee-venue-profiles` → apply `skills.ieee-manuscript-prose.overrides` (abstract style, narrative focus, run-in heads)

Recommended:

- `reference.md` (this skill)
- Compiled PDF for cross-checking quantitative anchors

## Execution workflow

1. **Extract claims** — List explicit novelty, performance, robustness, and scope
   statements from abstract, intro, results, and conclusion.
2. **Claim–evidence map** — Mark each claim as supported, partially supported,
   or unsupported by figures, tables, or cited prior work.
3. **Apply §2 scope tightening** — Replace universal wording (`always`, `optimal`,
   `fully solves`) with bounded phrases (`under the adopted setup`, `among the
   evaluated cases`, `for the demonstrated reference case`).
4. **Apply §3 structure**
   - Abstract: problem + method + strongest evidence; same numbers as body.
   - Introduction: motivation → gap → approach → contributions (not a figure list).
   - Conclusion: what was shown, what it enables, bounded forward look (not abstract copy).
5. **Apply §4 methodology tone** — State what is adopted, held fixed, measured,
   and compared; remove apology-style disclaimers.
5b. **Apply §4.0 novelty weight** — Emphasize true contributions; for classical
   or expected facts, use short objective narration and delete redundant
   “rather than a newly discovered …” / “we do not claim …” tags outside the
   one early scope statement.
5c. **Apply §4.0b claim density** — Absolute metrics + one headline relative
   claim; ban stacked `delay −x%, area −y%, and PDP −z%` (or equivalent) in one
   sentence; do not pair the same fact as both `%` and `×`.
5d. **Apply §4.0c caption formality** — Captions describe the figure/table; move
   “later confirmed in Table …” / “as expected …” process talk to the body.
5e. **Apply §4.0d future work** — At most one concrete next-step sentence
   (continue verification / extend evaluation); ban speculative “whether X widens”
   / “may favor at advanced nodes” / multi-paragraph unmeasured 7 nm claims.
5f. **Apply §4.0e equation references** — Use `In (\ref{...})` / `In
   (\ref{...})--(m)`; do not write `Eq.` / `Eqs.` before equation numbers.
6. **Apply §4.1 results tone** — Prefer `shows`/`presents`/`exhibits`/`indicating`;
   avoid informal `plots ... so ...` chains.
7. **Apply §4.2 punctuation** — Split semicolon-chained sentences; prefer periods,
   commas, `while`/`whereas` for contrast. **Do not use** em dashes (`---`) in
   body/caption/abstract prose; keep hyphens (`carry-bypass`) and en dashes
   (`8--128`, `Kogge--Stone`). If any body `---` remains, **report each hit to
   the user**.
8. **Apply §4.3 causal phrasing** — Vary openers (`To reveal ...`, `Although ...`,
   `Without modifying ...`, `A ... setup is evaluated using ...`); avoid stiff
   `For comparison`, `reports ... only`, `employs Table I`.
9. **Apply §5 results paragraphs** — Figure → behavior → mechanism → design
   implication → scope; explain why trends matter, not only what is visible.
10. **Re-read abstract vs results** — Every abstract number and superlative must
    appear and be justified in the body.

## Scripts

| Path | Purpose |
|------|---------|
| `scripts/scan_prose_patterns.sh` | Quick `rg` for `;`, `plots`, stiff `For`/`To` patterns |

## Default behavior

- **Execute edits** in the TeX source unless the user requests review-only.
- Keep notation, equation labels, and `\cite{}` keys stable unless fixing errors.
- Prefer minimal diffs: tighten sentences before deleting whole paragraphs.
- Do not remove technical content solely for length; defer page cuts to
  `ieee-manuscript-layout`.

## Output

Return a short summary:

```markdown
## Prose revisions
- [section]: [what changed and why]

## Residual risks
- [claim still weak / needs figure or experiment]

## Suggested next skill
- ieee-manuscript-figures | ieee-manuscript-bib | ieee-manuscript-layout
```

## Quick guardrails

| Avoid | Prefer |
|-------|--------|
| `We do not claim universal superiority` | Concrete comparability and fixed conditions |
| `These results are only preliminary` | Reference-case scope + future extraction targets |
| Semicolon chains in body/captions | Two short sentences |
| `For the evaluation, ... For comparison, ...` | Varied causal openers (`reference.md` §4.3) |
| Repository paths and script names in prose | Tool categories and reproducibility statement |
