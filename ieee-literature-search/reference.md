# IEEE Xplore search reference

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
source ~/.cursor/skills/ieee-literature-search/scripts/env.sh
```

## Comparator-focused querytext presets

Copy into `--query` (boolean syntax per IEEE API docs).

### Core comparator block

```text
("dynamic comparator" OR strongARM OR "latched comparator")
AND ("offset" OR kickback OR hysteresis OR metastability)
```

### SAR ADC calibration

```text
("SAR ADC" OR "successive approximation")
AND (comparator OR "decision circuit")
AND ("offset calibration" OR "auto-zero" OR kickback)
```

### Dual-comparator / TI-SAR

```text
("dual comparator" OR "dual-comparator")
AND ("SAR" OR "time-interleaved" OR "TI-ADC")
AND (offset OR alignment OR calibration)
```

### Flash threshold spread

```text
("flash ADC" OR "flash converter")
AND (comparator OR threshold)
AND (mismatch OR spread OR "bubble error")
```

### SerDes slicer (narrow)

```text
(slicer OR comparator)
AND (SerDes OR "wireline" OR "PAM-4")
AND (offset OR calibration)
AND ("ADC-based" OR "SAR ADC")
```

## Venue filters (high signal)

Use `--publication-title` or add to query:

| Venue | `publication_title` value |
|-------|---------------------------|
| JSSC | `IEEE Journal of Solid-State Circuits` |
| TCAS-I | `IEEE Transactions on Circuits and Systems I: Regular Papers` |
| TCAS-II | `IEEE Transactions on Circuits and Systems II: Express Briefs` |
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

Lowercase, replace non-alphanumeric with `-`, collapse repeated hyphens, trim length ~80 chars.

## Legal constraints

- Metadata search via API: allowed with registered key.
- Paywalled PDF download: **institutional access only** — user action.
- Open-access PDF: API full-text endpoint when metadata indicates OA.
- Do not use unauthorized scrapers or piracy sites.
