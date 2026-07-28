# Visual PDF Review and Final Checklist

Topic-agnostic rules for IEEE short papers. Skill: `ieee-manuscript-final-review`.

## 1. Visual and PDF Review

Before calling a paper ready, perform a visual review of the compiled PDF.

Check:

- page count,
- unresolved references or citations,
- overfull boxes,
- text overlap,
- figure readability,
- caption proximity,
- legend readability,
- table scaling,
- last-page column balance,
- whether references spill unexpectedly,
- whether float order is acceptable for the paper length.

Useful commands:

```bash
cd paper
latexmk -pdf 0_main_ieee_conference.tex
pdfinfo 0_main_ieee_conference.pdf | rg '^Pages:'
pdftoppm -png -r 180 0_main_ieee_conference.pdf /tmp/page
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

Do not rely only on LaTeX exit status. A PDF can compile successfully and still
have poor layout.

## 2. Final Revision Checklist

- [ ] Abstract claims appear in the results section.
- [ ] Introduction citations are grouped by purpose.
- [ ] Contribution statements are specific and evidence-backed.
- [ ] Each figure has readable axes, units, legends, and caption.
- [ ] Each table has units, precision consistency, and provenance when needed.
- [ ] Claims are bounded to demonstrated evidence.
- [ ] Figure-discussion prose follows `ieee-manuscript-prose/reference.md` §4.1
      (`shows`/`presents`, no informal `plots ... so ...` chains).
- [ ] Body text and captions avoid semicolon-chained sentences
      (`ieee-manuscript-prose/reference.md` §4.2).
- [ ] Methodology and results use goal-oriented phrasing where helpful
      (`ieee-manuscript-prose/reference.md` §4.3), without stiff
      `reports ... only` disclaimers.
- [ ] Reference metadata is official and unchanged for layout purposes.
- [ ] Cited `paper/reference.bib` entries were checked against DOI/Crossref,
      OpenAlex, or local PDF title pages.
- [ ] Conference `booktitle` fields use standard acronyms such as `IEEE ISCAS`,
      `IEEE IFETC`, and `IEEE ESSDERC`, without year or `Proceedings of ...`
      wording.
- [ ] Titles, authors, pages, volume, issue, year, and DOI match official records.
- [ ] Journal names are consistent (full titles **or** abbreviations per
      `ieee-bib-hygiene/reference.md` §7); abbreviation is optional layout only.
- [ ] Duplicate BibTeX keys for the same paper are absent or fully synchronized.
- [ ] No repository-local paths remain in manuscript prose.
- [ ] Number-unit, range, percentage, and notation formatting are consistent.
- [ ] PDF page count matches the target.
- [ ] Rendered PDF pages have no large unexplained holes or overlaps.
- [ ] The final PDF was checked visually after the last LaTeX change.
