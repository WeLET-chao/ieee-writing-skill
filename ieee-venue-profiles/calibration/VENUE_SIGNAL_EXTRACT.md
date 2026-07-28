# Venue signal extraction (per paper)

After `analyze-research-paper` completes, add `literature/<slug>/venue_signals.json` for profile calibration.

## Required fields

```json
{
  "profile_id": "ieee-tcad-journal",
  "source_slug": "paper-slug",
  "venue_from_pdf": "IEEE Trans. CAD",
  "year": 2024,
  "estimated_pages": 11,
  "latex_template": {
    "documentclass_guess": "IEEEtran journal",
    "split_sections": true,
    "has_markboth": true,
    "has_ieee_pubid": true,
    "bibliography_compact_guess": false
  },
  "figures_and_layout": {
    "figure_count": 8,
    "table_count": 3,
    "figure_star_count": 2,
    "algorithm_count": 1,
    "architecture_figure_full_width": true
  },
  "structure_and_narrative": {
    "section_titles": ["Introduction", "Background", "Proposed Method", "Experiments", "Conclusion"],
    "abstract_sentences": 10,
    "intro_has_taxonomy": true,
    "paper_organization_paragraph": true,
    "results_runin_heads": true,
    "narrative_focus_guess": "cad_methodology"
  },
  "bibliography": {
    "approx_reference_count": 45,
    "intro_citation_density": "high"
  },
  "agent_notes": "One paragraph: what this paper suggests for the profile."
}
```

## Map signals → profile pillars

| Signal | Profile pillar | Typical patch |
|--------|----------------|---------------|
| `split_sections` + `has_markboth` | `latex_template` | confirm journal split-file template |
| `figure_star_count` / `architecture_figure_full_width` | `figures_and_layout` | `figures.architecture_flow.environment` |
| `algorithm_count` median ≥ 1 | `figures_and_layout.algorithms` | `minimum_count` |
| `section_titles` cluster | `structure_and_narrative.sections` | rename / reorder section map |
| `abstract_sentences` median | `structure_and_narrative.abstract` | `sentence_count` range |
| `results_runin_heads` frequency | `structure_and_narrative.results` | `subsection_style` |
| `bibliography_compact_guess` | `latex_template.bibliography_in_main` | `compact_font_hack` |

Only patch when **≥3 papers** in the same `profile_id` agree, or one paper is an official IEEE template / widely cited exemplar.
