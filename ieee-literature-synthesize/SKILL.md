---
name: ieee-literature-synthesize
description: "Aggregates structured paper digests (e.g. papers/*/analysis.md) into a corpus-level synthesis: problem themes, research directions, opportunities, and prior-art maps by category. Domain-agnostic via JSON profiles. Use when summarizing a paper library, building a research roadmap, identifying gaps, or comparing prior art across many analyzed papers."
---

# IEEE Literature Synthesize

> **This repo:** read [PROJECT.md](PROJECT.md) — corpus root `paper/literature/`.

Turn many structured digests into one research landscape report.

**Principle:** scripts extract and count; the agent names themes and writes the synthesis.

**Do not declare done after Pass 2.** Passes 4–5 (agent synthesis + verification) are mandatory.

## Quick start

Paths: [PATH_MODE.md](../PATH_MODE.md).

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-synthesize)"
REPO=/path/to/repo

python3 "$SKILL/scripts/extract_corpus.py" "$REPO"
python3 "$SKILL/scripts/aggregate_corpus.py" "$REPO/_corpus/extracted.json"
python3 "$SKILL/scripts/validate_corpus.py" "$REPO"
```

Then read `_corpus/aggregate.json`, sample papers per category, and write the report from [templates/corpus-synthesis.md](templates/corpus-synthesis.md).

Default profile: [profiles/default.json](profiles/default.json) — compatible with `analyze-research-paper`.

## Workflow checklist

```
- [ ] Pass 0 — Discover corpus (glob, count, optional index cross-check)
- [ ] Pass 1 — extract_corpus.py → _corpus/extracted.json
- [ ] Pass 2 — aggregate_corpus.py → _corpus/aggregate.json
- [ ] Pass 3 — validate_corpus.py exit 0
- [ ] Pass 4 — Agent synthesis → docs/RESEARCH_ANALYSIS.md (or user path)
- [ ] Pass 5 — Agent re-read 2–3 papers/category; fix synthesis; re-validate
```

### Pass 0 — Discover

1. Identify repo root and profile (`default` or user-provided).
2. Count digest files:

```bash
python3 "$SKILL/scripts/extract_corpus.py" "$REPO" --profile "$SKILL/profiles/default.json"
```

3. Optional: compare count against `docs/PAPERS.md` or profile `input.index_file`.

### Pass 1 — Extract

```bash
python3 "$SKILL/scripts/extract_corpus.py" "$REPO" \
  --profile "$SKILL/profiles/default.json" \
  --out "$REPO/_corpus/extracted.json"
```

Writes per-paper structured fields defined by the profile. See [reference.md](reference.md) for schema.

### Pass 2 — Aggregate

```bash
python3 "$SKILL/scripts/aggregate_corpus.py" "$REPO/_corpus/extracted.json" \
  --profile "$SKILL/profiles/default.json" \
  --out "$REPO/_corpus/aggregate.json"
```

Produces mechanical indexes only:

- counts by category, year, era
- prior-art bold-heading frequencies
- opportunity bullet inventory
- per-category sample snippets

### Pass 3 — Validate extraction

```bash
python3 "$SKILL/scripts/validate_corpus.py" "$REPO" \
  --extracted "$REPO/_corpus/extracted.json" \
  --profile "$SKILL/profiles/default.json"
```

After synthesis exists:

```bash
python3 "$SKILL/scripts/validate_corpus.py" "$REPO" \
  --synthesis "$REPO/docs/RESEARCH_ANALYSIS.md"
```

### Pass 4 — Agent synthesis (required)

Read `aggregate.json` and write the report using [templates/corpus-synthesis.md](templates/corpus-synthesis.md).

Produce these sections:

| Section | Source fields | Agent task |
|---------|---------------|------------|
| Executive summary | all | 1-paragraph landscape |
| Problem themes | `problem_statement`, `motivation` | Name recurring themes with counts |
| Research directions | `motivation`, `limitations`, `contributions` | Field-level movement, not paper list |
| Opportunities | `research_opportunity` | Cluster, rank, dedupe; mark `Analysis:` |
| Prior art by category | `prior_art`, `category` | Lineage per primary category |
| Corpus gaps | `aggregate.json` counts | Sparse categories/eras/topics |

**Rules:**

- Ground every theme in ≥2 papers unless the corpus has fewer than 2 total.
- Do not invent citations; prior-art names must come from extracted `prior_art`.
- Distinguish author claims (`contributions`) from agent inference (`Analysis:`).
- Use domain language from the papers, not hardcoded vocabulary from this skill.

### Pass 5 — Accuracy verification (required)

For each major category in `aggregate.json`:

1. Re-read 2–3 source `analysis.md` files.
2. Confirm problem themes, prior-art lineages, and opportunities match the digests.
3. Fix synthesis errors.
4. Re-run `validate_corpus.py --synthesis` if a report file exists.

## Profiles

| Profile | Use when |
|---------|----------|
| [default.json](profiles/default.json) | `analyze-research-paper` digests |
| [minimal.json](profiles/minimal.json) | Only problem + prior art + opportunities |

Custom profile:

```bash
python3 "$SKILL/scripts/extract_corpus.py" "$REPO" --profile /path/to/custom.json
```

Copy `default.json` and change `input.glob` or section `headings` for other domains. Full schema: [reference.md](reference.md).

## Output layout

```
<repo>/
  _corpus/
    extracted.json
    aggregate.json
  docs/
    RESEARCH_ANALYSIS.md    # recommended final report
```

`_corpus/` is generated data; add to `.gitignore` if the repo should not commit intermediates.

## Pairing with analyze-research-paper

```
analyze-research-paper (per PDF)  →  papers/<slug>/analysis.md
ieee-literature-synthesize (batch)   →  docs/RESEARCH_ANALYSIS.md
```

Re-run synthesis when new digests land.

## Common failures

| Symptom | Fix |
|---------|-----|
| 0 files extracted | Check `input.glob` in profile |
| Required section errors | Add missing `##` headings or relax profile `required` |
| Low category coverage | Fill `Category of work` or switch to `comma_tags` parser |
| Spot-check mismatch | Re-run extraction; inspect non-UTF-8 or nonstandard headings |
| Thin synthesis | Read more source digests; do not infer from titles alone |

## Additional resources

- Profile schema and agent rules: [reference.md](reference.md)
- Report template: [templates/corpus-synthesis.md](templates/corpus-synthesis.md)