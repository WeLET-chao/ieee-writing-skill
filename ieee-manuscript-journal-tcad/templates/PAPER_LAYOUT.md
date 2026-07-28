# IEEE TCAD Journal `paper/` Layout

Initialize with:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
TCAD="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-journal-tcad)"

PAPER_DIR=paper \
  bash "$TCAD/scripts/init_tcad_journal.sh" --bootstrap-tex
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
├── SKILL_FEEDBACK.md           # Optional: lessons → promote to skill reference.md (consumer)
└── out/                        # Review outputs, not for submission
```

**Do not** maintain `main.tex` as a parallel journal entry point. Conference
`main.tex` is a different venue path (`ieee-manuscript-layout`); journal uses
`0_main_ieee_trans.tex` only.

## Build

```bash
PAPER_DIR=paper \
  bash "$TCAD/scripts/build_tcad_journal.sh"
```

Typography and float cleanup afterward: `ieee-manuscript-layout`.

## Conference vs journal entry

| Venue | Main TeX | Skill |
|-------|----------|-------|
| Short IEEE conference | `main.tex` | `ieee-manuscript-layout` `templates/main.tex` |
| IEEE TCAD journal | `0_main_ieee_trans.tex` + section files | `ieee-manuscript-journal-tcad` |

Do not maintain both as parallel sources of truth; migrate conference drafts into split journal files.

## Related skills

| Concern | Skill |
|---------|--------|
| TCAD structure, narrative, migration | `ieee-manuscript-journal-tcad` |
| Typography, float holes | `ieee-manuscript-layout` |
| Plot style | `ieee-manuscript-figures` |
| Bibliography hygiene | `ieee-manuscript-bib` |
| Prose and claims | `ieee-manuscript-prose` |
