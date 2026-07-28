---
name: ieee-manuscript-rebuttal
description: >-
  Structures IEEE manuscript reviewer responses: point-by-point rebuttal letter,
  change log mapped to TeX diffs, and optional revision pass hooks. Use when the
  user receives reviewer comments and needs a response letter or revision plan
  before resubmitting.
---

# IEEE Manuscript Rebuttal

Use after review comments arrive and before a full `ieee-manuscript-revision` pass.

## Inputs

- Reviewer PDF or pasted comments
- Current manuscript: `paper/*.tex`, `paper/reference.bib`
- Optional: `paper/writing_plan.md` for claim map

## Outputs

```text
paper/rebuttal/response.md          # point-by-point letter
paper/rebuttal/change_log.md        # what changed in TeX/figures/bib
paper/rebuttal/reviewer_matrix.md   # comment ID → status → evidence
```

## Workflow

```text
- [ ] Parse reviewer comments into numbered items (R1-C1, R2-C3, …)
- [ ] Classify each: accept / partial / decline-with-evidence
- [ ] Map each item to manuscript location (section, figure, equation)
- [ ] Draft response.md (polite, specific, cites figure/table/line where possible)
- [ ] List required TeX/bib/figure edits in change_log.md
- [ ] Run ieee-manuscript-revision on changed sections only
- [ ] ieee-manuscript-final-review before resubmission
```

## Response style

- One block per reviewer comment; quote or paraphrase the comment first
- State the change made, or why no change (with evidence / scope limit)
- Do not promise results not supported by simulations or literature

## Related skills

| Step | Skill |
|------|--------|
| Full revision after rebuttal plan | `ieee-manuscript-revision` |
| Prose fixes | `ieee-manuscript-prose` |
| New figures for reviewer requests | `ieee-manuscript-figures` |
| Bib updates | `ieee-manuscript-bib` |
| Resubmission check | `ieee-manuscript-final-review` |
