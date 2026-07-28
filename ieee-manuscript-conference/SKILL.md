---
name: ieee-manuscript-conference
description: >-
  Bootstraps short IEEE conference manuscripts (~2 pages): monolithic main.tex,
  figure/table budget, and init via ieee-manuscript-layout. Use when
  ieee-venue-profiles resolves to ieee-conference-short or the user targets
  IFETC-style two-page conference papers.
---

# IEEE Conference Short Manuscript

Venue contract: resolve **`ieee-conference-short`** in `ieee-venue-profiles` first.

This skill is the **conference counterpart** to `ieee-manuscript-journal-tcad`.

## When to use

- Target is a **short IEEE conference** paper (typically 2 pages)
- `paper/venue_profile.json` → `profile_id: ieee-conference-short`
- User asks for IFETC / 2-page / monolithic `main.tex` bootstrap

## Bootstrap

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
LAYOUT="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-layout)"

bash "$LAYOUT/scripts/init_paper_assets.sh" --bootstrap-tex
```

Produces `paper/main.tex`, `paper/reference.bib`, `paper/figures/`, revision templates.

## Workflow

```text
- [ ] ieee-venue-profiles → ieee-conference-short
- [ ] ieee-manuscript-scoping → writing_plan + figure_asset_plan
- [ ] This skill → init TeX scaffold
- [ ] ieee-manuscript-figures → generate figures per plan
- [ ] ieee-manuscript-prose → fill sections within page budget
- [ ] ieee-manuscript-layout → compile and trim to page limit
- [ ] ieee-manuscript-bib → verify citations
```

## Related skills

| Concern | Skill |
|---------|--------|
| Page budget, floats | `ieee-venue-profiles` profile + `ieee-manuscript-layout` |
| Outline | `ieee-manuscript-scoping` |
| Prose | `ieee-manuscript-prose` |
| Figures | `ieee-manuscript-figures` |
| Bib | `ieee-manuscript-bib` |
| Final gate | `ieee-manuscript-final-review` |
