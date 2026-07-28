# IEEE literature search reference

## API endpoints

| Call | URL |
|------|-----|
| Article search | `https://ieeexploreapi.ieee.org/api/v1/search/articles` |
| Open-access full text | `https://ieeexploreapi.ieee.org/api/v1/document/{article_number}/full-text` (requires entitlement) |

Common parameters: `querytext`, `start_record`, `max_records`, `start_year`, `end_year`, `publication_title`, `doi`, `article_number`, `apikey`.

Register: https://developer.ieee.org/getting_started

## API keys in this skill

| File | Purpose |
|------|---------|
| `scripts/api_keys.sh` | **Primary store** — `IEEE_XPLORE_API_KEY` + `IEEE_XPLORE_API_KEY_BACKUP` |
| `scripts/env.sh` | Sources `api_keys.sh`, then optional `env.local.sh` overrides |
| `scripts/ieee_api.py` | Failover: primary → backup on HTTP 403 or 429 |

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
source "$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-literature-search)/scripts/env.sh"
```

See [PATH_MODE.md](../PATH_MODE.md).

## Canonical index layout

Default for ieee-writing consumers:

```text
paper/literature/
  PAPERS.md
  <slug>/
    paper.pdf
    analysis.md
```

Table columns: **Title | Authors | Year | Venue | Category | DOI | Analysis | PDF**

Category column: comma-separated tags (project-defined). Prefer stable, lowercase slugs (`device-modeling`, `level-shifter`, `prior-art`).

## Legacy layouts

Older lab repos used different roots. Map paths when porting:

| Legacy | Canonical |
|--------|-----------|
| `docs/PAPERS.md` | `paper/literature/PAPERS.md` |
| `papers/<slug>/paper.pdf` | `paper/literature/<slug>/paper.pdf` |
| `papers/<slug>/analysis.md` | `paper/literature/<slug>/analysis.md` |

Dedupe and import scripts accept any `--index` path; only the default docs assumed `docs/PAPERS.md`.

## Topic query presets

Copy into `--query` (boolean syntax per IEEE API docs). Add domain-specific blocks below as needed.

### Device / strain / TFT (example)

```text
("flexible electronics" OR "flexible TFT")
AND (strain OR mechanical)
AND ("threshold voltage" OR mobility)
```

### CAD / analog sizing (example)

```text
("analog circuit" OR "operational amplifier")
AND ("sizing" OR "design automation" OR reinforcement)
AND (TCAD OR "computer-aided design")
```

### Level shifter (example)

```text
("level shifter" OR "voltage level converter")
AND (ultra-low OR "sub-threshold" OR "wide range")
```

### Comparator-focused presets (legacy lab domain)

Use narrow queries (`dynamic comparator`, `SAR ADC offset calibration`) over bare `comparator`.

**Core comparator block:**

```text
("dynamic comparator" OR strongARM OR "latched comparator")
AND ("offset" OR kickback OR hysteresis OR metastability)
```

**SAR ADC calibration:**

```text
("SAR ADC" OR "successive approximation")
AND (comparator OR "decision circuit")
AND ("offset calibration" OR "auto-zero" OR kickback)
```

**Dual-comparator / TI-SAR:**

```text
("dual comparator" OR "dual-comparator")
AND ("SAR" OR "time-interleaved" OR "TI-ADC")
AND (offset OR alignment OR calibration)
```

**Flash threshold spread:**

```text
("flash ADC" OR "flash converter")
AND (comparator OR threshold)
AND (mismatch OR spread OR "bubble error")
```

**SerDes slicer (narrow):**

```text
(slicer OR comparator)
AND (SerDes OR "wireline" OR "PAM-4")
AND (offset OR calibration)
AND ("ADC-based" OR "SAR ADC")
```

## Category tags (example domains)

Project-defined — pick a small stable set per repo.

### Comparator / ADC lab (legacy)

| Tag | Use for |
|-----|---------|
| `comparator-calibration` | Offset trim, auto-zero, kickback cal, dual-comp alignment |
| `comparator-modeling` | Trip, delay, hysteresis, kickback characterization |
| `circuit-design` | Transistor comparator, strongARM, latched topology |
| `sar-adc` | SAR slice / bit trial context |
| `flash-adc` | Flash threshold / bubble / redundancy |
| `serdes-transceiver` | Slicer / ADC-based RX (when comparator is secondary) |
| `survey` | Tutorials and overview papers |

Other domains: reuse tags from **`analyze-research-paper`** `reference.md` or define in `PROJECT.md`.

## Venue filters (high signal)

Use `--publication-title` or add to query:

| Venue | `publication_title` value |
|-------|---------------------------|
| JSSC | `IEEE Journal of Solid-State Circuits` |
| TCAD | `IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems` |
| TCAS-I | `IEEE Transactions on Circuits and Systems I: Regular Papers` |
| TCAS-II | `IEEE Transactions on Circuits and Systems II: Express Briefs` |
| TED | `IEEE Transactions on Electron Devices` |
| SSCS Letters | `IEEE Solid-State Circuits Letters` |
| ISSCC | `IEEE International Solid-State Circuits Conference` |
| VLSI Symp. | `IEEE Symposium on VLSI Circuits` |

ISSCC/VLSI are conferences — also filter `content_type` in Xplore UI or add conference name to `querytext`.

## Manual search (no API)

1. https://ieeexplore.ieee.org/search/searchresult.jsp → **Advanced Search**
2. Search in **Abstract / Author Keywords** first
3. Filters: year, journals + conferences, open access (optional)
4. Select results → **Export** → BibTeX
5. Run `import_bibtex.py` on the export file

## Deduping rules

Treat as duplicate if any match:

- Same DOI (case-insensitive, strip `https://doi.org/`)
- Same IEEE article number in Xplore URL
- Normalized title (lowercase, remove punctuation, collapse whitespace) ≥ 90% similar to existing row

## Slug from title

```text
"A 112-134-Gb/s PAM4 Receiver Using ..." 
  → a-112-134-gb-s-pam4-receiver-using-...
```

Lowercase, replace non-alphanumeric with `-`, collapse repeated hyphens, trim length ~80 chars. Matches `search_ieee.py` `slugify_title()`.

## Open access and PDF download

- Metadata search via API: allowed with registered key.
- Paywalled PDF: use **`paper-pdf-fetch`** (IEEE → Sci-Hub → scansci cascade) or institutional access — not this skill.
- Open-access full text: API endpoint when metadata indicates OA; prefer **`paper-pdf-fetch`** for batch download from PAPERS.md.
- Do not use unauthorized scrapers or piracy sites.
