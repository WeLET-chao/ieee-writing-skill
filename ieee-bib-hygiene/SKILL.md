---
name: ieee-bib-hygiene
description: >-
  Verifies and cleans IEEE bibliography entries for circuit, device, modeling,
  EDA, and measurement papers: DOI/Crossref/PDF metadata checks, conference
  booktitle acronyms, optional journal abbreviation for layout,
  author/year/page consistency, and duplicate key removal. Use when editing
  reference.bib, fixing citations, or preparing submission-ready bibliographies.
---

# IEEE Bibliography Hygiene

## Canonical source

Read `reference.md` in this folder (local §1–§8). Section numbers are
**skill-local**; do not use legacy monolith §7.x from old guideline files.

## Purpose

Treat reference metadata as **technical content**. Never shorten or rewrite bib
fields only to save page space.

## Inputs

- `paper/reference.bib` (or user-specified `.bib`)
- Cited keys from manuscript `*.tex`
- Optional local PDFs: `paper/references/<bibkey>.pdf`
- **Venue profile:** `ieee-venue-profiles` → citation density, trim uncited for pages, journal abbrev policy

To fetch literature PDFs before verification, use **`ieee-literature-pipeline`**
(search/download into `paper/literature/`, then copy cited keys to `paper/references/`).

## Execution workflow

1. **List cited keys** — Only verify and edit entries that appear in `\cite{...}`.
2. **Authoritative check (§2)** — For each cited entry, confirm against DOI /
   Crossref, OpenAlex, or PDF title page. Do not invent metadata from memory.
3. **Fields to verify** — `title`, `author`, `journal` or `booktitle`, `year`,
   `volume`, `number`, `pages`, `month`, `doi`.
4. **Title rules (§3)** — Preserve official publisher casing and hyphenation;
   on Crossref vs PDF conflict, prefer PDF title page (conferences) or publisher
   page (journals).
5. **Conference booktitle (§4)** — Use acronyms only, e.g. `{IEEE IFETC}`,
   `{IEEE ISCAS}`, `{IEEE ESSDERC}`; no year, no `Proceedings of ...`.
6. **Author/year/pages (§5)** — Fix placeholder pages (`1-14`, `1-1`); brace
   surnames (`Yongfu {Li}`); `year` matches published record even if key differs.
7. **DOI and duplicates (§6)** — Add `doi` when available; sync duplicate keys;
   strip exporter noise (`keywords`, `ISSN`) unless needed.
8. **Journal names (§7)** — Full official titles are fine. Abbreviate only as an
   optional, file-consistent layout measure when references need space; or use
   `IEEEabrv.bib` at render time. Do not mix styles arbitrarily.
9. **Compile and inspect** — Build PDF and read the rendered reference list.

```bash
.cursor/skills/ieee-latex-layout/scripts/build_paper.sh
```

## Templates

| Path | Purpose |
|------|---------|
| `templates/reference.bib` | **Starter** `paper/reference.bib` (`IEEEexample:BSTcontrol` only) |
| `templates/entry_examples.bib` | Commented journal/conference entry patterns (reference only) |

Installed into `paper/` by:

```bash
.cursor/skills/ieee-latex-layout/scripts/init_paper_assets.sh --bootstrap-tex
```

When adding entries, copy field style from `entry_examples.bib`, then verify
metadata per `reference.md` §2.

## Scripts

| Path | Purpose |
|------|---------|
| `scripts/list_cited_keys.py` | List `\cite{}` keys; `--bib` checks missing entries |

```bash
python3 .cursor/skills/ieee-bib-hygiene/scripts/list_cited_keys.py \
  --bib paper/reference.bib
```

## Hard rules

- **Never** delete references or falsify metadata to fix page count.
- **Never** use Wikipedia or bare GitHub URLs in submission drafts unless
  explicitly temporary placeholders.
- One citation should not support unrelated claims in prose.

## Output

```markdown
## Bibliography changes
- [key]: [field corrected + source used]

## Unresolved entries
- [key]: [missing PDF/DOI; what was checked]

## Suggested next skill
- ieee-latex-layout | ieee-manuscript-final-review
```
