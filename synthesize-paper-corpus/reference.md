# Corpus Synthesis Reference

## Purpose

Turn many structured paper digests into one corpus-level report:

- Problem themes
- Research directions
- Research opportunities
- Prior art by category

Scripts extract and aggregate mechanically. The agent synthesizes meaning.

## Input contract

Each digest is a markdown file discovered by the profile `input.glob`.

Compatible with `analyze-research-paper` output (`papers/<slug>/analysis.md`), but any repo can use the skill by supplying:

1. A profile JSON
2. Digests with level-2 `##` sections mapped in the profile

## Profile schema

Profiles live in `profiles/*.json`.

### Top-level keys

| Key | Required | Meaning |
|-----|----------|---------|
| `name` | yes | Profile identifier |
| `description` | no | Human-readable note |
| `input.glob` | yes | Digest glob relative to repo root |
| `input.index_file` | no | Optional index for cross-check (`docs/PAPERS.md`) |
| `bibliographic` | no | Title/year/venue extraction rules |
| `sections` | yes | Section aliases and requirements |
| `aggregation` | no | Grouping and validation settings |

### Bibliographic sources

| `source` | Behavior |
|----------|----------|
| `heading` | First `#` or `##` heading at configured level |
| `table` | Markdown table row `| Field | Value |` |

### Section parsers

| `parse` | Behavior |
|---------|----------|
| `category_block` | `Primary: \`tag\``, optional `Secondary`, `Note` |
| `comma_tags` | First comma-separated tag becomes primary |

### Aggregation settings

| Key | Default | Meaning |
|-----|---------|---------|
| `group_by` | `category.primary` | Mechanical grouping key |
| `min_theme_papers` | `2` | Agent should only promote themes seen in ≥N papers |
| `spot_check_count` | `5` | Random extraction fidelity checks |
| `min_section_chars` | `50` | Minimum required section length |
| `era_buckets` | `[2010,2015,2020,2023]` | Year bucket boundaries |

## Output artifacts

```
<repo>/
  _corpus/
    extracted.json     # per-paper structured fields
    aggregate.json     # counts, indexes, category summaries
  docs/
    RESEARCH_ANALYSIS.md  # agent-written report (recommended)
```

## Agent synthesis rules

### Problem themes

Read `problem_statement` and `motivation`. Name recurring themes in domain language. For each theme report:

- Approximate paper count
- Trend by era/year if visible
- 1–2 representative titles

Do not use hardcoded domain keyword lists unless the user provides them.

### Research directions

Synthesize from `motivation`, `limitations`, `contributions`, and `innovations`.

A direction is where the field is moving, not a list of individual paper titles.

### Research opportunities

Cluster bullets from `research_opportunity`.

- Deduplicate near-duplicates
- Rank by frequency and actionability
- Prefix inferred items with `Analysis:`

### Prior art by category

For each `category.primary` (or agent-inferred topic if categories are sparse):

- Summarize cited lineages from `prior_art`
- Use bold subheadings and named systems from the digests
- Never invent citations or paper titles not present in extracted data

### Corpus gaps

Report categories, eras, or topics with low coverage using `aggregate.json` counts.

## Validation contract

`validate_corpus.py` checks:

1. Required sections meet minimum length
2. Category coverage ≥80% when category parsing is enabled
3. Random spot-check: extracted prefix matches source digest
4. Optional synthesis grounding: report references multiple known slugs

Pass 5 (agent): re-read 2–3 papers per major category and confirm the written synthesis matches extracted facts.

## Custom profiles

Examples:

### ML papers with different headings

```json
{
  "name": "ml",
  "input": { "glob": "papers/*/analysis.md" },
  "sections": {
    "problem_statement": { "headings": ["Research question", "Problem statement"], "required": true },
    "prior_art": { "headings": ["Related work"], "required": true },
    "category": { "headings": ["Tags"], "parse": "comma_tags", "required": false }
  }
}
```

### Reviews outside `papers/`

```json
{
  "name": "reviews",
  "input": { "glob": "reviews/*/summary.md" },
  "sections": {
    "problem_statement": { "headings": ["Problem"], "required": true },
    "prior_art": { "headings": ["Related work"], "required": true }
  }
}
```

## Integration

```
analyze-research-paper  →  papers/<slug>/analysis.md
synthesize-paper-corpus →  docs/RESEARCH_ANALYSIS.md
```

Re-run extraction and aggregation whenever new digests are added.
