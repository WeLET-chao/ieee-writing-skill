# IEEE LaTeX Typography and Layout

Topic-agnostic rules for IEEE short papers. Skill: `ieee-manuscript-layout`.

For semicolon and dash prose rules, also apply
`ieee-manuscript-prose/reference.md` §4.2.

## 1. IEEE LaTeX Typography

General typography rules:

- Use `~` for number-unit spacing, e.g., `5~s`, `0.5~mV`.
- Use `--` for ranges, e.g., `1--5`, `0.02--0.10~s`.
- Write percentages as `45.9\%`, with no space before `\%`.
- Keep notation stable across abstract, text, figures, and tables.
- Expand acronyms on first body mention.
- Avoid repository-local paths and script names in submission prose.

Punctuation rules:

- Avoid semicolons in body text and captions when a period or comma works.
- Prefer two short sentences over one semicolon-chained sentence.
- Use `while`, `whereas`, or `and` for contrast inside a single sentence when
  needed.
- See `ieee-manuscript-prose/reference.md` §4.2 for semicolon and em-dash rewrite patterns.
- **Do not use** em dashes (`---`) in body, caption, abstract, or conclusion prose. Prefer commas, periods, or parentheses.
- Allowed: hyphen compounds (`carry-bypass`), en dash ranges/names (`8--128`, `Kogge--Stone`), and comment rulers (`%-----`).
- After a layout/prose pass, if any non-comment `---` remains, **report every hit to the user**.
- Use hyphens for stacked modifiers and en-dashes for ranges or paired metrics
  such as `area--delay`.

Micro-unit rules:

```latex
\usepackage{textcomp}
```

Prefer:

```latex
10~\text{\textmu m}
\text{\textmu W}
```

over inconsistent mixtures of math-mode `$\mu$` and text units.

## 2. Float and Layout Rules

IEEE two-column layout is sensitive to float placement. A visually bad page is
often caused by float constraints, not by bad prose.

Important rules:

- Avoid overusing `[H]`. It pins figures/tables in place and can create large
  white holes in two-column papers.
- Use `[!t]` for figures/tables that can reasonably move to the top of a page.
- Use `figure*` only when a figure truly needs full page width.
- Check whether a full-width figure belongs logically to the section where it
  appears; otherwise it may float into an awkward page position.
- Do not fix layout by editing reference metadata.
- Do not shrink fonts below what the template reasonably supports unless the
  venue explicitly allows it.

For short IEEE papers, the practical workflow is:

1. Compile the PDF.
2. Render pages as images.
3. Inspect for blank regions, overlaps, unreadable figures, and broken reading
   order.
4. Adjust float placement before cutting technical content.

If the paper is at a hard page limit, prefer these fixes in order:

1. Remove redundant prose.
2. Merge repeated sentences.
3. Remove weak references.
4. Adjust float placement.
5. Reduce figure width only if readability remains acceptable.
6. As a last resort, reconsider whether the target page limit is realistic.

### Short captions and `tablenotes`

Keep `\caption{...}` short (object + metric family + comparison set). Move
column definitions, measurement conditions, and claim-scope notes to
`tablenotes` under `threeparttable` / `tabular`. Do not pack methodology into
the caption paragraph.

In `tablenotes`, use `\item` (not `\item[]`) so bullets render, put **one
sentence per `\item`**, and define metrics with **symbols and equations** (e.g.,
$\mathrm{Delay}=T_{\mathrm{clk}}-\mathrm{WNS}$ at $T_{\mathrm{clk}}=10~\mathrm{ns}$),
not colloquial prose (“Delay is … with …”). Use **column names** in metric
formulas (e.g., Power, Delay), not undefined symbols ($P$, $D$). Use `\times` for
multiplication in metric formulas, not `\cdot`. Do not add meta claim-scope lines (e.g., “primary claim is versus X”); scope belongs in the
body/abstract.

## 3. Build Commands

Useful commands (default paths for this repo):

```bash
cd paper
latexmk -pdf 0_main_ieee_conference.tex
pdfinfo 0_main_ieee_conference.pdf | rg '^Pages:'
```

Legacy manual sequence if `latexmk` is unavailable:

```bash
pdflatex -interaction=nonstopmode 0_main_ieee_conference.tex
bibtex 0_main_ieee_conference
pdflatex -interaction=nonstopmode 0_main_ieee_conference.tex
pdflatex -interaction=nonstopmode 0_main_ieee_conference.tex
```

After a successful build, `paper/.latexmkrc` removes intermediate files by
default and keeps the PDF.
