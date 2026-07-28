# ieee-writing skill naming

All skills in this group use the prefix **`ieee-`** and a **phase** segment.

## Pattern

```text
ieee-<phase>-<role>
```

| Phase | Prefix | Purpose |
|-------|--------|---------|
| Literature | `ieee-literature-*` | Search, download handoff, per-paper digests, corpus synthesis |
| Manuscript | `ieee-manuscript-*` | Scoping, prose, figures, layout, bib, revision, venue-specific bootstrap |
| Venue | `ieee-venue-*` | Cross-phase venue contracts (profiles, calibration) |

**Exceptions (external, not in this repo):**

| Skill | Repo |
|-------|------|
| `paper-pdf-fetch` | `agent-skills/paper-pdf-fetch` |
| `analyze-research-paper` | `paper-pipeline` |

## Canonical skill slugs

### Literature (`ieee-literature-*`)

| Slug | Role |
|------|------|
| `ieee-literature-pipeline` | Orchestrator: search → fetch → analyze → synthesize |
| `ieee-literature-search` | IEEE Xplore search → `PAPERS.md` |
| `ieee-literature-synthesize` | Aggregate `analysis.md` → corpus report |

### Manuscript (`ieee-manuscript-*`)

| Slug | Role |
|------|------|
| `ieee-manuscript-scoping` | `writing_plan.md`, figure plan, TeX scaffold |
| `ieee-manuscript-journal-tcad` | TCAD journal split TeX bootstrap |
| `ieee-manuscript-conference` | Short IEEE conference TeX bootstrap |
| `ieee-manuscript-prose` | Claims, abstract, section prose |
| `ieee-manuscript-figures` | Figure generation and captions |
| `ieee-manuscript-layout` | Typography, floats, compile |
| `ieee-manuscript-bib` | `reference.bib` hygiene |
| `ieee-manuscript-revision` | Orchestrator: full revision pass |
| `ieee-manuscript-final-review` | Pre-submission compile + checklist |
| `ieee-manuscript-rebuttal` | Reviewer response letter / change log |

### Venue (`ieee-venue-*`)

| Slug | Role |
|------|------|
| `ieee-venue-profiles` | JSON profiles + five-pillar venue contract |

## Legacy names (removed)

| Old slug | New slug |
|----------|----------|
| `ieee-xplore-paper-search` | `ieee-literature-search` |
| `synthesize-paper-corpus` | `ieee-literature-synthesize` |
| `ieee-latex-layout` | `ieee-manuscript-layout` |
| `ieee-bib-hygiene` | `ieee-manuscript-bib` |
| `ieee-tcad-journal-manuscript` | `ieee-manuscript-journal-tcad` |
| `ieee-xplore-paper-pdf-downloader` | `paper-pdf-fetch` (external) |
| `ieee-csv-paper-pdf-downloader` | `paper-pdf-fetch` (external) |
