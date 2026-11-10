# Scripts and templates index

Shell entry points for ieee-writing skills. Resolve paths with [PATH_MODE.md](PATH_MODE.md) or:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
ROOT="$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh"
SKILL="$(bash "$ROOT" ieee-literature-search)"   # example
```

## Literature (`ieee-literature-*`)

| Skill | Script | Purpose |
|-------|--------|---------|
| `ieee-literature-search` | `scripts/setup.sh` | Create `.venv` |
| | `scripts/search_ieee.py` | Xplore Metadata API search |
| | `scripts/import_bibtex.py` | Parse manual BibTeX export |
| | `scripts/fetch_record.py` | Single DOI / record URL |
| | `scripts/dedupe_papers.py` | Dedupe vs `PAPERS.md` |
| `ieee-literature-synthesize` | `scripts/extract_corpus.py` | Per-paper field extract |
| | `scripts/aggregate_corpus.py` | Corpus counts / indexes |
| | `scripts/validate_corpus.py` | Schema + synthesis checks |

## Venue (`ieee-venue-*`)

| Skill | Script | Purpose |
|-------|--------|---------|
| `ieee-venue-profiles` | `scripts/resolve_venue_profile.py` | Load / list JSON profiles |
| | `scripts/download_venue_corpus.sh` | Calibration PDF download |
| | `scripts/run_venue_calibration_search.py` | Batch Xplore search for calibration |
| | `scripts/synthesize_profile_signals.py` | Merge `venue_signals.json` |

## Manuscript (`ieee-manuscript-*`)

| Skill | Script | Purpose |
|-------|--------|---------|
| `ieee-manuscript-scoping` | `scripts/scan_repo_for_paper.py` | Repo inventory JSON |
| | `scripts/scaffold_manuscript.py` | `writing_plan` + TeX scaffold |
| | `scripts/prepare_scoping_test_repo.sh` | Local test fixture |
| `ieee-manuscript-layout` | `scripts/init_paper_assets.sh` | Bootstrap `paper/` tree |
| | `scripts/build_paper.sh` | `latexmk` build + page count |
| `ieee-manuscript-journal-tcad` | `scripts/init_tcad_journal.sh` | TCAD split TeX bootstrap |
| | `scripts/build_tcad_journal.sh` | TCAD build wrapper |
| `ieee-manuscript-bib` | `scripts/list_cited_keys.py` | Cited keys vs `.bib` |
| `ieee-manuscript-figures` | `scripts/plot_publication.py` | Matplotlib style helper |
| `ieee-manuscript-prose` | `scripts/scan_prose_patterns.sh` | Prose pattern grep |
| `ieee-manuscript-final-review` | `scripts/build_and_review.sh` | Build + review bundle |
| | `scripts/render_pdf_pages.sh` | Rasterize PDF pages |
| `ieee-manuscript-rebuttal` | `scripts/mark_revision_sentences.py` | Sentence-level blue `\rev{...}` tracked TeX |

Orchestrators (`ieee-literature-pipeline`, `ieee-manuscript-revision`) invoke the scripts above via sub-skills — see each `SKILL.md`.
