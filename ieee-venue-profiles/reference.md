# IEEE Venue Profiles — Reference (schema v2)

Skill: `ieee-venue-profiles`.

Profiles are the **primary contract**. Skills are **executors** referenced in
`execution_skills`.

## 1. Profile top level

```json
{
  "profile_id": "string",
  "schema_version": "2",
  "venue_name": "string",
  "aliases": ["string"],
  "latex_template": { },
  "figures_and_layout": { },
  "structure_and_narrative": { },
  "bibliography": { },
  "project_layout": { },
  "checklist": ["string"],
  "execution_skills": { }
}
```

## 2. Pillar 1 — `latex_template`

| Field | Purpose |
|-------|---------|
| `documentclass` | `conference` vs `journal,twoside` |
| `main_tex` | Entry file |
| `section_inputs` | Split `\input{}` list; empty if monolithic |
| `monolithic` | `true` for single `main.tex` |
| `template_skill` | Skill supplying TeX templates |
| `front_matter` | `markboth`, `ieee_pubid`, `bstctlcite`, `author_thanks`, biographies |
| `preamble` | `packages_required`, `package_conflicts` |
| `bibliography_in_main` | style, files, `compact_font_hack` |
| `notes` | Venue-specific TeX remarks |

**Conference vs TCAD (examples)**

| | conference-short | tcad-journal |
|--|------------------|--------------|
| documentclass | conference | journal,twoside |
| main | `main.tex` monolith | `0_main_ieee_trans.tex` + 5 inputs |
| front matter | minimal | markboth + IEEEpubid |
| bib compact hack | allowed | forbidden |

## 3. Pillar 2 — `figures_and_layout`

| Field | Purpose |
|-------|---------|
| `page` | typical_min/max, hard_limit, expand_if_below, when_over_limit |
| `floats` | default_specifier, textfloatsep_tight |
| `figures` | architecture_flow spec, data_plots spec, minimum_count |
| `tables` | setup, results_summary, sota_comparison, minimum_count |
| `algorithms` | minimum_count, environment |
| `notes` | |

**This pillar is more than min figure count** — it defines float environments,
widths, media (vector vs matplotlib), table roles, and page strategy.

## 4. Pillar 3 — `structure_and_narrative`

| Field | Purpose |
|-------|---------|
| `sections` | File map and what each file must contain |
| `abstract` | structure, sentence_count, must_include, metric_sync |
| `introduction` | taxonomy, contributions format, related_work placement, closing |
| `methodology` | preferred section title, must_include |
| `results` | setup separate?, subsection_style, example_heads, each_block pattern |
| `conclusion` | title, limitations, metric repetition |
| `writing_rhythm` | sentence-per-line comments, headline_metric_in, narrative_focus |
| `notes` | |

**Writing rhythm** lives here — not in `ieee-latex-layout`.

## 5. Pillar 4 — `bibliography`

| Field | Purpose |
|-------|---------|
| `bib_files` | `reference.bib`, `IEEEabrv.bib` |
| `bst_control_entry` | IEEEtran BST control key |
| `bibliography_command` | LaTeX invocation |
| `citation_policy` | density per section, comparison table cites |
| `maintenance_policy` | trim uncited, abbrev journals, shrink bib font |
| `notes` | |

## 6. Pillar 5 — `project_layout`

| Field | Purpose |
|-------|---------|
| `root_variable` | `PAPER_DIR` |
| `default_root_name` | conventional folder name (`paper`) |
| `active_profile_file` | `venue_profile.json` in consumer root |
| `required_paths` / `optional_paths` | Directory contract |
| `init` / `build` | scripts and main_tex |
| `scoping_outputs` | writing_plan, figure_asset_plan |
| `notes` | Host-specific dirs stay outside profile |

## 7. `execution_skills` (secondary)

Maps each pillar to skills for implementation. Agents read pillars first;
invoke skills second.

## 8. Resolution order

1. `PAPER_DIR/venue_profile.json` → `profile_id`
2. Else `IEEE_VENUE_PROFILE` env
3. Else user-stated venue → match `aliases`
4. `resolve_venue_profile.py <id>` → five-pillar briefing
5. Work pillar by pillar; call skills listed in `execution_skills`

## 9. Adding a venue

1. Copy `profiles/_template.json`
2. Fill **all five pillars** — do not only set page_limit and min_figures
3. If `latex_template` or `structure_and_narrative` needs new TeX skeleton → extend `ieee-tcad-journal-manuscript` templates or add a new structure skill
4. Validate: `resolve_venue_profile.py <id>`

## 10. Relationship to structure skills

| Artifact | Role |
|----------|------|
| **Venue profile** | What this journal requires (5 pillars) |
| **Structure skill** (e.g. `ieee-tcad-journal-manuscript`) | Reusable TeX templates + init scripts when split journal skeleton is shared |
| **Base skills** | Timeless rules; apply with profile context |

TCAD and TCAS-I may share the same structure skill but differ in pillars 2–3.
