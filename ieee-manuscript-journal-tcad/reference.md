# IEEE TCAD Journal Manuscript — Reference

Skill: `ieee-manuscript-journal-tcad`. Typography details remain in
`ieee-manuscript-layout/reference.md`.

## 1. LaTeX template

### Conference vs journal

| Item | IEEE conference (avoid for TCAD) | IEEE TCAD journal (use) |
|------|----------------------------------|-------------------------|
| Document class | `\documentclass[conference]{IEEEtran}` | `\documentclass[journal,twoside]{IEEEtran}` |
| Main file | `main.tex` monolith | `0_main_ieee_trans.tex` + numbered `\input{}` |
| Running header | none | `\markboth{IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN...}{Short title}` |
| Copyright | optional | `\IEEEpubid{...}` + `\IEEEoverridecommandlockouts` |
| Author block | short affiliation | `\thanks` with dates, funding, corresponding author |
| Bibliography | sometimes 7pt compressed | normal `IEEEtran` size |
| Biographies | none | `IEEEbiography` + `photos/` at end |

### Required preamble packages (CAD papers)

```latex
\usepackage[mediumspace,mediumqspace,Gray,squaren]{SIunits}
\usepackage[hang,center,tight]{subfigure}
\usepackage{float}
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{multirow}
\usepackage{textcomp}
\usepackage{textgreek}
\usepackage{algorithm}
\usepackage{algorithmic}
```

Use `algorithmic` **or** `algpseudocode`, not both (command conflict on TeX Live 2026).

### Document start

```latex
\begin{document}
\bstctlcite{IEEEexample:BSTcontrol}
\graphicspath{{./figures/}{./photos/}{./}}
```

### Algorithm environment

TCAD CAD papers expect at least one floating algorithm (flow, synthesis loop, or optimizer). Use `algorithm` + `algorithmic` with `\REQUIRE`/`\ENSURE` renamed to Input/Output.

## 2. Figures and layout

### Figure roles

| Role | Float | Width | Source |
|------|-------|-------|--------|
| CAD / architecture flow | `figure*` | `0.95\textwidth` | Vector PDF preferred |
| Gate-level / netlist example | `figure*` | `~18.5cm` or `\textwidth` | Export from EDA |
| Bar chart, ablation, sweep | `figure` | `9cm` or `\columnwidth` | `plot_publication.py` |
| Testbench + die photo | `figure` | `9cm` | Composite layout |
| FFT / spectrum | `figure` | `9cm` | Simulation export |

Optional: `[trim=..., clip]` on `\includegraphics` to crop export margins.

After the first intro figure in journal mode, `\IEEEpubidadjcol` may be needed to align the copyright block with the IEEE pub-id column.

### Table roles

| Table | Purpose |
|-------|---------|
| Setup / benchmark suite | Toolchain, runs, metrics, PDK — lets reviewers audit conditions |
| Results summary | Consolidates numbers also shown in figures |
| SOTA comparison (`table*`) | CAD capabilities vs cited baselines (fixed topology?, feedback loop?, sign-off scope?) |

Use `booktabs`, `multirow`, footnotes `^a` for simulation-only or estimated rows.

### Page budget

TCAD full papers are typically **~10--12 pages** in two-column journal format. A skeleton with only figures and outline prose often lands at **3--5 pages** — expand methodology and discussion, do not shrink bibliography to fake length.

**Milestones:**

| Stage | Pages | Action |
|-------|-------|--------|
| Skeleton | 3--5 | Add formulation, tables, RW section |
| First submittable draft | **~8** | Cost/failure tables, case metrics, RW as own section |
| TCAD typical | **10--12** | Deeper method, discussion, optional extra figures |

### Claim scope and deliverable wording

Narrative framing is **project-specific** — set it in `ieee-manuscript-scoping` checkpoints
and `ieee-manuscript-prose`, not in this skill.

Generic rules for TCAD CAD papers:

- **Title and contributions** must match the **actual automation endpoint** (e.g.,
  spec-to-schematic, spec-to-netlist, placement, timing closure) — do not imply
  silicon or layout sign-off unless the paper provides that evidence.
- If the paper uses terms such as “end-to-end” or “fully automated,” **define them once**
  in the abstract or introduction (what stages are in / out of scope).
- Use `ieee-manuscript-prose` for tone; avoid generic “flow” titles that understate
  or overstate the technical contribution.

Repeat scope limits in conclusion **Limitations**.

## 3. Section structure and narrative style

### Recommended file map

```
0_main_ieee_trans.tex
1_abstract_v1.tex       % abstract + IEEEkeywords
2_introduction_v1.tex   % intro, contributions, paper map
2b_related_work_v1.tex  % Related Work (recommended when draft >= 6 pages)
3_methodology_v1.tex    % proposed CAD flow / synthesis
4_results_v1.tex        % setup + experimental results
5_conclusion_v1.tex     % conclusion, discussion, limitations
```

For drafts under ~6 pages, Related Work may remain a `\subsection` inside
`2_introduction_v1.tex`. When expanding toward **8+ pages**, promote to
`2b_related_work_v1.tex` and `\input{}` from main.

### Section naming (CAD automation)

Prefer methodology language over circuit-only titles:

- **Good:** Proposed CAD Flow, Architecture Synthesis, Experimental Setup, Experimental Results, Conclusion and Discussion
- **Avoid for CAD primary story:** leading with “Circuit Implementation” unless the journal angle is circuit-heavy (TCAS-I)

### Introduction template

1. Application motivation (design cost, turnaround, complexity)
2. Why automation matters now
3. **Taxonomy** of prior work (2--3 classes with citations)
4. Gap: what prior classes do not do
5. This paper: approach in 3--5 sentences with **headline numbers**
6. Bulleted contributions
7. Related work subsection (optional if taxonomy is thin)
8. “The rest of this paper is organized as follows.”

### Abstract template (TCAD rhythm)

Use **short sentences** separated by `%` line breaks (optional). Include:

- problem statement
- gap in prior automation
- proposed method (3-stage flow, constraints, simulation-in-the-loop)
- **2--4 quantitative results** with same numbers as tables/figures
- explicit scope bound (what the flow does **not** include — e.g., layout, silicon, or unverified stages)

### Results narrative

Use bold run-in heads (not only `\subsection`):

```latex
\noindent\textbf{Behavioral ablation:}
...
\noindent\textbf{gm/ID sizing comparisons:}
```

Optional blocks when expanding toward **8+ pages** (use labels that match your experiments):

```latex
\noindent\textbf{Efficiency and cost analysis:}
\noindent\textbf{Failure-mode analysis:}
\noindent\textbf{Reproducibility:}
```

Each block: setup → figure/table reference → numeric takeaway with relative improvement.

### Number synchronization

Pick 3--5 **headline metrics** (e.g., pass-rate lift, runtime reduction, success-rate gap vs baseline). Repeat consistently in:

- abstract
- introduction (last paragraph before contributions)
- results text
- summary table
- conclusion

### CAD-specific content to include in methodology

- Formal spec vector and pass/fail predicates
- Template or constraint rules (what the generator cannot change)
- Fast proxy simulator or checker role (filter vs sign-off)
- Optimizer or sizing engine integration
- Reproducibility note (artifact manifest, scripts — in repo docs, not submission prose)

## 4. BibTeX

### Required controls

In `reference.bib`:

```bibtex
@IEEEtranBSTCTL{IEEEexample:BSTcontrol,
  CTLuse_forced_etal       = "yes",
  CTLmax_names_forced_etal = "3",
  CTLnames_show_etal       = "2"
}
```

In main TeX, before `\maketitle` content: `\bstctlcite{IEEEexample:BSTcontrol}`.

### Bibliography invocation

```latex
\bibliographystyle{IEEEtran}
\bibliography{./IEEEabrv,./reference}
```

### Citation strategy

| Section | Density | Purpose |
|---------|---------|---------|
| Introduction | high | Classify prior CAD, optimization, and learning-based EDA lines |
| Methodology | low–medium | Cite gm/ID, templates, simulators |
| Results | low | Cite baselines only when comparing in Table |
| Conclusion | none | |

Keep `ieee-manuscript-bib` DOI/month rules. Journal entries use braced full journal names: `journal="{IEEE Transactions on ...}"`.

### Comparison table citations

SOTA tables often use `\cite{key}` in column headers with `multirow`.

## 5. Directory and project layout

```
paper/                          # PAPER_DIR (name is conventional, not required)
├── 0_main_ieee_trans.tex
├── 1_abstract_v1.tex … 5_conclusion_v1.tex
├── reference.bib
├── IEEEabrv.bib
├── IEEEtran.cls
├── .latexmkrc
├── figures/              # submission PDFs/PNGs
├── scripts/              # regenerate figures
├── photos/               # IEEEbiography (optional)
├── references/           # local PDF library (optional)
├── literature/           # analyzed prior papers (optional)
├── writing_plan.md       # optional
└── out/                  # review artifacts, not for submission
```

Host projects may add artifact or reproducibility directories; those are **outside**
this skill's required layout.

### Build entry

- **Primary:** `MAIN_TEX=0_main_ieee_trans.tex`
- **Deprecated:** monolithic `main.tex` conference draft

### Skill boundaries

| Path | Role |
|------|------|
| `figures/` | Only `\includegraphics` targets |
| `scripts/` | Regenerate plots; may import `ieee-manuscript-figures` |
| `figure_data/` | Optional CSV/JSON intermediates |
| `out/` | Review artifacts, not for submission |
| `references/*.pdf` | Local PDF library for bib verification |

## Migration checklist (conference → TCAD)

1. Replace `\documentclass[conference]` with `[journal,twoside]`
2. Split sections into `1_`…`5_` files
3. Add TCAD front matter (`\markboth`, `\IEEEpubid`, author `\thanks`)
4. Convert flow diagram to `figure*`; add setup + summary tables
5. Add Algorithm 1 for automated flow
6. Expand abstract to quantitative multi-sentence form
7. Add intro taxonomy + paper organization paragraph
8. Restructure results with bold subheads
9. Remove bibliography font compression
10. Compile; if pages `< 6`, expand methodology and discussion before float trimming
