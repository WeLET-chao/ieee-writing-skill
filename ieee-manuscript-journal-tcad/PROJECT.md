# ieee-manuscript-journal-tcad — PMIC consumer example

Host repo: **PMIC** (`paper_writing/` as `PAPER_DIR`).

> **Note:** Narrative choices below are **PMIC-specific**. They belong here and in
> `paper_writing/drafting_goal.md`, not in the generic skill `SKILL.md` / `reference.md`.

## Paths

| Generic skill default | PMIC |
|----------------------|------|
| `paper/` | `paper_writing/` |
| `writing_plan.md` | `paper_writing/writing_plan.md` |
| Evidence (optional) | `paper_writing/artifacts/manifest.yaml`, `thesis_repro/` |
| Skill feedback | `paper_writing/SKILL_FEEDBACK.md`, `drafting_goal.md` |
| Venue | `paper_writing/venue_profile.json` → `ieee-tcad-journal` |

## Narrative choices (PMIC user decisions — not generic TCAD defaults)

- **Title framing:** agentic end-to-end spec-to-netlist (PMIC LDO automation story)
- **Scope:** verified netlist via Spectre; not layout/silicon
- **Main TeX:** `0_main_ieee_trans.tex` + `2b_related_work_v1.tex`

## Build

```bash
bash paper_writing/scripts/build_paper.sh
```

## Feedback into this skill

When PMIC writing surfaces a reusable TCAD pattern:

1. Log in `paper_writing/SKILL_FEEDBACK.md`
2. Promote to `ieee-manuscript-journal-tcad/reference.md` or `SKILL.md` in the canonical skill repo
3. Keep hurricane paths, manifest slugs, and thesis tables in PMIC only

See `paper_writing/SKILL_FEEDBACK.md` for promoted vs pending items.
