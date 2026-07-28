# IEEE Manuscript Revision — Topic Index

Each skill owns a **self-contained** `reference.md` numbered from §1 within that
skill. Do **not** use legacy monolith section numbers (old §7, §13, etc.) in new
projects—they only appear below for migration lookup.

## Where to find rules

| Topic | Skill | Local sections |
|-------|-------|----------------|
| **Venue profiles (overrides)** | `ieee-venue-profiles` | SKILL.md, `profiles/*.json`, reference.md §3 |
| Core writing principle | `ieee-manuscript-prose` | §1 |
| Claim scope and evidence | `ieee-manuscript-prose` | §2 |
| Abstract, intro, conclusion | `ieee-manuscript-prose` | §3 |
| Methodology wording | `ieee-manuscript-prose` | §4 |
| Results prose tone | `ieee-manuscript-prose` | §4.1, §5 |
| Semicolon avoidance | `ieee-manuscript-prose` | §4.2 |
| Causal phrasing | `ieee-manuscript-prose` | §4.3 |
| Figures | `ieee-manuscript-figures` | §1 |
| Tables | `ieee-manuscript-figures` | §2 |
| Captions | `ieee-manuscript-figures` | §3 |
| Bibliography hygiene | `ieee-manuscript-bib` | §1–§8 |
| LaTeX typography | `ieee-manuscript-layout` | §1 |
| Float and layout | `ieee-manuscript-layout` | §2 |
| Build commands | `ieee-manuscript-layout` | §3 |
| Visual PDF review | `ieee-manuscript-final-review` | §1 |
| Final checklist | `ieee-manuscript-final-review` | §2 |

## Cross-skill references

When one skill points to another, use the **skill path + local section**, for
example:

- `ieee-manuscript-prose/reference.md` §4.1 (not “guidelines §4.1”)
- `ieee-manuscript-bib/reference.md` §7 (not “guidelines §7.6”)

## Legacy monolith map (deprecated)

For repos that still mention the old single-file numbering:

| Legacy § | Now |
|----------|-----|
| 1–4, 11 | `ieee-manuscript-prose/reference.md` §1–§5 |
| 5, 6, 10 | `ieee-manuscript-figures/reference.md` §1–§3 |
| 7 | `ieee-manuscript-bib/reference.md` §1–§8 |
| 8, 9 | `ieee-manuscript-layout/reference.md` §1–§2 |
| 12, 13 | `ieee-manuscript-final-review/reference.md` §1–§2 |

Root `IEEE_MANUSCRIPT_REVISION_GUIDELINES.md` is a pointer only, not the
canonical numbered source.

## Orchestrator

Full ordered pass: `ieee-manuscript-revision/SKILL.md`
