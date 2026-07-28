# IEEE TCAD Journal `paper/` Layout

Initialize with:

```bash
PAPER_DIR=paper \
  .skills/ieee-tcad-journal-manuscript/scripts/init_tcad_journal.sh --bootstrap-tex
```

`PAPER_DIR` is the **consumer manuscript root** (any path the user chooses;
default `<repo>/paper/`). This skill does not assume a fixed folder name.

## Directory tree

```
paper/                          # or paper_writing/ — set PAPER_DIR
├── 0_main_ieee_trans.tex       # Journal main file (preamble + \input)
├── 1_abstract_v1.tex
├── 2_introduction_v1.tex
├── 2b_related_work_v1.tex      # Optional: own \section{Related Work} (draft >= 6 pp)
├── 3_methodology_v1.tex
├── 4_results_v1.tex
├── 5_conclusion_v1.tex
├── reference.bib
├── IEEEabrv.bib
├── IEEEtran.cls
├── .latexmkrc
├── figures/                    # Submission \includegraphics targets
├── scripts/                    # Figure regeneration
├── photos/                     # IEEEbiography portraits
├── references/                 # Local PDF library (optional)
├── literature/                 # Analyzed prior papers (optional)
├── artifacts/                  # Optional: manifest + synced experiment outputs (consumer)
├── writing_plan.md             # Outline (optional)
├── drafting_goal.md            # Optional: tracks + user decisions (consumer)
├── SKILL_FEEDBACK.md           # Optional: lessons → .skills/ promotion (consumer)
└── out/                        # Review outputs, not for submission
```

**Do not** maintain `main.tex` as a parallel journal entry point. Conference
`main.tex` is a different venue path (`ieee-latex-layout`); journal uses
`0_main_ieee_trans.tex` only.

## Build

```bash
PAPER_DIR=paper \
  .skills/ieee-tcad-journal-manuscript/scripts/build_tcad_journal.sh
```

Typography and float cleanup afterward: `ieee-latex-layout`.

## Conference vs journal entry

| Venue | Main TeX | Skill |
|-------|----------|-------|
| Short IEEE conference | `main.tex` | `ieee-latex-layout` `templates/main.tex` |
| IEEE TCAD journal | `0_main_ieee_trans.tex` + section files | `ieee-tcad-journal-manuscript` |

Do not maintain both as parallel sources of truth; migrate conference drafts into split journal files.

## Related skills

| Concern | Skill |
|---------|--------|
| TCAD structure, narrative, migration | `ieee-tcad-journal-manuscript` |
| Typography, float holes | `ieee-latex-layout` |
| Plot style | `ieee-manuscript-figures` |
| Bibliography hygiene | `ieee-bib-hygiene` |
| Prose and claims | `ieee-manuscript-prose` |
