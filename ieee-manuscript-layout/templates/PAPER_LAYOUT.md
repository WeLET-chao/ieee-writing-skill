# IEEE `paper/` Folder Layout

Topic-agnostic layout for circuit, device, modeling, EDA, and measurement
manuscripts. Initialize with:

```bash
.cursor/skills/ieee-manuscript-layout/scripts/init_paper_assets.sh
```

Optional fresh `main.tex` + starter `reference.bib`:

```bash
.cursor/skills/ieee-manuscript-layout/scripts/init_paper_assets.sh --bootstrap-tex
```

## Directory tree

```
paper/
├── main.tex                    # Primary manuscript (or project-specific name)
├── reference.bib               # From ieee-manuscript-bib/templates/reference.bib
├── IEEEtran.cls                # From skill templates/
├── IEEEabrv.bib                # Abbreviated journal strings
├── .latexmkrc                  # latexmk PDF + cleanup intermediates
├── figures/                    # Final plot exports for \includegraphics
├── references/                 # Local PDFs keyed by BibTeX key (optional)
├── scripts/                    # Project figure/data scripts
│   └── generate_figures.py     # Copy from ieee-manuscript-figures template
├── figure_data/                # Optional: simulation exports, CSV, netlists
├── out/                        # Generated review artifacts (not for submission)
│   └── pdf_pages/              # Rasterized pages from final-review script
├── writing_plan.md             # Optional: outline / figure-table plan (skill output)
└── manual/                     # Human-maintained backups (not overwritten by skills)
```

## Path conventions

| Path | Role |
|------|------|
| `figures/*.pdf` | **Submission figures** — `\graphicspath{{./figures/}}` |
| `scripts/*.py` | Regenerate figures; import `plot_publication` style |
| `figure_data/` | Intermediate simulation/plot inputs (repo-specific) |
| `references/<key>.pdf` | Bib metadata verification (`ieee-manuscript-bib/reference.md` §8) |
| `out/` | Build/review outputs; do not cite in manuscript |

## Main TeX naming

| Venue | Main file | Skill |
|-------|-----------|-------|
| IEEE conference (short) | `main.tex` or `0_main_ieee_conference.tex` | `templates/main.tex` |
| IEEE TCAD / journal | `0_main_ieee_trans.tex` + `1_abstract_v1.tex` … | `ieee-manuscript-journal-tcad` |

Journal split-file conventions and migration checklist:
`../ieee-manuscript-journal-tcad/templates/PAPER_LAYOUT.md`.

Set `MAIN_TEX` when building:

```bash
MAIN_TEX=0_main_ieee_trans.tex \
  .cursor/skills/ieee-manuscript-layout/scripts/build_paper.sh
```

## Related skills

| Concern | Skill |
|---------|-------|
| Preamble, floats, compile | `ieee-manuscript-layout` |
| Figure style, captions | `ieee-manuscript-figures` |
| `reference.bib` hygiene | `ieee-manuscript-bib` |
| Prose / outline | `ieee-manuscript-prose`, `writing_plan.md` |
