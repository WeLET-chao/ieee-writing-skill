---
name: ieee-venue-profiles
description: "Resolves venue-specific manuscript contracts for IEEE conferences and journals across five pillars: LaTeX template, figures/layout, structure/narrative, BibTeX, and project layout. Loads JSON profiles (TCAD, short conference, TCAS-I). Use when the target venue changes or before scoping, drafting, or revision — not only for per-skill layout tweaks."
---

# IEEE Venue Profiles

## Core idea

A **venue profile** is the full manuscript contract for a conference or journal,
organized by **five pillars** (not by downstream skill name):

| # | Pillar | What it governs |
|---|--------|-----------------|
| 1 | `latex_template` | documentclass, main/section TeX, front matter, preamble, bib in main |
| 2 | `figures_and_layout` | page budget, floats, figure*/table* roles, algorithms, plot widths |
| 3 | `structure_and_narrative` | section map, abstract/intro/results rhythm, taxonomy, metric sync |
| 4 | `bibliography` | bib files, BST control, citation density, trim policy |
| 5 | `project_layout` | PAPER_DIR tree, init/build scripts, scoping artifacts |

**Base skills** (`ieee-manuscript-layout`, `ieee-manuscript-prose`, …) implement mechanics.
**Profiles** state what this venue requires in each pillar.
`execution_skills` at the bottom of each profile only says *which skill to run* — it is not the primary schema.

## When to use

- Target venue selected or changed (TCAD, IFETC 2-page, TCAS-I, …)
- Before scoping, bootstrap, draft expansion, or revision pass
- User asks how this journal differs from a conference structurally

## Quick start

Paths: [PATH_MODE.md](../PATH_MODE.md). Resolve skill root:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
VENUE="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-venue-profiles)"

python3 "$VENUE/scripts/resolve_venue_profile.py" --list
python3 "$VENUE/scripts/resolve_venue_profile.py" ieee-tcad-journal

# Consumer repo pointer (any PAPER_DIR):
# { "profile_id": "ieee-tcad-journal" }
```

## Workflow

1. Set `paper/venue_profile.json` → `profile_id`
2. Run `resolve_venue_profile.py <id>` — read **all five pillars**
3. Bootstrap from `project_layout.init` / `latex_template.template_skill`
4. Draft and revise **against pillar fields**, not generic skill defaults
5. Use `execution_skills` only to pick which skill to invoke per pillar

## Shipped profiles

| `profile_id` | Venue |
|--------------|-------|
| `ieee-tcad-journal` | IEEE TCAD |
| `ieee-conference-short` | ~2-page IEEE conference |
| `ieee-tcas-i-journal` | IEEE TCAS-I |

Copy `profiles/_template.json` for new venues.

## Pillar → skill mapping (execution only)

| Pillar | Typical skills |
|--------|----------------|
| LaTeX template | `ieee-manuscript-journal-tcad` or `ieee-manuscript-layout` |
| Figures and layout | `ieee-manuscript-figures`, `ieee-manuscript-layout` |
| Structure and narrative | `ieee-manuscript-journal-tcad`, `ieee-manuscript-prose` |
| BibTeX | `ieee-manuscript-bib` |
| Project layout | `ieee-manuscript-journal-tcad`, `ieee-manuscript-scoping` |

## Maintenance

Lessons from a host-repo manuscript → update the **profile pillar fields** (or structure skill templates). Do not embed consumer paths in profiles.

## Profile calibration (IEEE corpus)

Refine profiles from recent venue papers. **Discovery:** web search or Xplore browse → `calibration/PAPERS.md`. **PDFs:** `download_venue_corpus.sh` on campus. **Tune profiles:** analyze → `venue_signals.json` → `synthesize_profile_signals.py`.

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
VENUE="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-venue-profiles)"
bash "$VENUE/scripts/download_venue_corpus.sh"
```

Full workflow: [calibration/PROFILE_CALIBRATION.md](calibration/PROFILE_CALIBRATION.md)

## Resources

- Schema and pillar field catalog: [reference.md](reference.md)
- Example consumer pointer: [templates/venue_profile.example.json](templates/venue_profile.example.json)