# ieee-writing skills

Canonical repository: [WeLET-chao/ieee-writing-skill](https://github.com/WeLET-chao/ieee-writing-skill).  
In [agent-skills](https://github.com/WeLET-chao/agent-skills), this group is mounted as the `ieee-writing/` git submodule.

IEEE-style manuscript workflows: literature → scoping → drafting → revision → submission.

**Naming:** `ieee-literature-*`, `ieee-manuscript-*`, `ieee-venue-*` — see [NAMING.md](NAMING.md).  
**Paths:** [PATH_MODE.md](PATH_MODE.md) · script index [ARTIFACTS.md](ARTIFACTS.md).

## End-to-end flow

```text
┌─ Literature (Phase A) ─────────────────────────────────────────────┐
│ ieee-literature-pipeline                                           │
│   → ieee-literature-search → paper-pdf-fetch → analyze-research  │
│   → (optional) ieee-literature-synthesize                          │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Drafting (Phase B) ─────────────────────────────────────────────┐
│ ieee-venue-profiles                                                │
│   → ieee-manuscript-scoping                                        │
│   → ieee-manuscript-journal-tcad  OR  ieee-manuscript-conference   │
│   → ieee-manuscript-prose / figures / layout / bib                 │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Revision (Phase C) ──────────────────────────────────────────────┐
│ ieee-manuscript-revision → final-review                            │
│ ieee-manuscript-rebuttal (after reviews)                           │
└────────────────────────────────────────────────────────────────────┘
```

External skills: `paper-pdf-fetch`, `analyze-research-paper` (see PATH_MODE.md).

## Skill map

### Literature (`ieee-literature-*`)

| Skill | Role |
|-------|------|
| `ieee-literature-pipeline` | Orchestrator |
| `ieee-literature-search` | Xplore search → PAPERS.md |
| `ieee-literature-synthesize` | Corpus-level synthesis (optional) |

### Manuscript (`ieee-manuscript-*`)

| Skill | Role |
|-------|------|
| `ieee-manuscript-scoping` | Writing plan + figure plan + scaffold |
| `ieee-manuscript-journal-tcad` | TCAD journal TeX bootstrap |
| `ieee-manuscript-conference` | Short conference TeX bootstrap |
| `ieee-manuscript-prose` | Prose and claims |
| `ieee-manuscript-figures` | Figures and captions |
| `ieee-manuscript-layout` | Layout, compile, page trim |
| `ieee-manuscript-bib` | Bibliography hygiene |
| `ieee-manuscript-revision` | Full revision orchestrator |
| `ieee-manuscript-final-review` | Pre-submission gate |
| `ieee-manuscript-rebuttal` | Reviewer response letter |

### Venue (`ieee-venue-*`)

| Skill | Role |
|-------|------|
| `ieee-venue-profiles` | Venue JSON profiles + calibration |

## Quick start

Literature:

```bash
ieee-literature-pipeline
```

New manuscript:

```bash
ieee-venue-profiles → ieee-manuscript-scoping → ieee-manuscript-conference  # or journal-tcad
```

Revision:

```bash
ieee-manuscript-revision
```

## Environment setup

| Skill | Setup |
|-------|--------|
| `ieee-literature-search` | `bash scripts/setup.sh` |
| `paper-pdf-fetch` | `bash paper-pdf-fetch/scripts/setup.sh` (agent-skills root) |
| `analyze-research-paper` | see `paper-pipeline` README |

Most other skills are markdown/shell workflows without a shared venv.

## Working assumptions

- Default workspace: `paper/` layout under a consumer git repo.
- Run `ieee-venue-profiles` early so downstream skills share venue constraints.
