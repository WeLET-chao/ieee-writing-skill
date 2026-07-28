# References and Bibliography Hygiene

Topic-agnostic rules for IEEE short papers. Skill: `ieee-bib-hygiene`.

**Templates:** `templates/reference.bib` (starter for `paper/`), `templates/entry_examples.bib`
(journal/conference field patterns). Install starter via
`ieee-latex-layout/scripts/init_paper_assets.sh --bootstrap-tex`.

## 1. Principles

Reference metadata is technical content, not layout filler.

Do not change reference titles, authors, journal/conference names, years, pages,
or volume information simply to save space. If a bibliography is too long:

- remove unnecessary references,
- merge weak citation groups,
- shorten prose around citations,
- improve float placement,
- optionally switch journal names to a **consistent abbreviated style** (§7),
- or accept an additional page if the venue allows it.

Preferred reference sources:

- peer-reviewed journals and conferences,
- standard textbooks,
- official tool or model documentation,
- canonical process/design-kit/model papers.

Avoid relying on Wikipedia, unsourced web pages, or bare GitHub links in a
submission draft unless they are temporary placeholders.

Citation placement should make the role of each reference clear. Do not make
one citation support unrelated claims.

## 2. Verify Metadata Against Authoritative Sources

Before finalizing `paper/reference.bib`, verify every **cited** entry against at
least one authoritative source:

1. DOI / Crossref record,
2. OpenAlex or publisher page,
3. local PDF first page in `paper/references/` when available.

Do not rewrite titles, author names, pages, volume, issue, year, or conference
names from memory, from another agent's summary, or to make entries look more
uniform. If metadata was changed without permission, restore the official
record.

Minimum fields to check for each cited entry:

- `title`
- `author`
- `journal` or `booktitle`
- `year`
- `volume`, `number` when applicable
- `pages`
- `month` when known
- `doi` when available

Common errors to catch:

- wrong first-author given name,
- placeholder pages such as `1-1` or `1-14` for published journal articles,
- missing `volume` or `issue`,
- conference `booktitle` copied from Crossref as `Proceedings of the Nth ...`,
- title capitalization or hyphenation drift,
- duplicate keys for the same paper with inconsistent metadata.

## 3. Title Formatting Rules

Use the official publisher title unless the venue explicitly requires a local
house style. In practice, IEEE records usually imply these conventions:

- preserve official acronym casing, e.g., `VCO-Based`, `LTPS-TFT`, `IGZO-TFT-PDK`,
- use `With` / `Using` rather than lowercased function words when that matches
  the official title,
- use hyphenated compound modifiers, e.g., `Thin-Film`, `N-Type-Only`,
- do not append editorial suffixes such as `[TFT based]` unless they appear on
  the official title page.

Examples of title corrections:

- `Generalized Rapid TFT Modeling ... with Thin Film Transistors`
  -> `Generalized Rapid TFT Modeling ... With Thin-Film Transistors`
- `A 10.23-bit ENOB ... VCO-based ADC with ...`
  -> `A 10.23-Bit ENOB ... VCO-Based ADC With ...`
- `Flexible semiconductor devices: fingerprint sensor ... [TFT based]`
  -> `Flexible Semiconductor Devices: Fingerprint Sensor and Electrophoretic Display on Plastic`

When Crossref and the PDF disagree, prefer the PDF title page for conference
papers and the publisher/journal landing page for journal articles.

## 4. Conference `booktitle` Format

Use the standard conference acronym, without year, proceedings numbering, or
redundant full conference titles.

Preferred IEEE conference format:

```bibtex
booktitle = "{IEEE ISCAS}",
booktitle = "{IEEE IFETC}",
booktitle = "{IEEE A-SSCC}",
booktitle = "{IEEE ISSCC}",
booktitle = "{IEEE ESSDERC}",
booktitle = "{IEEE ESSCIRC}",
booktitle = "{IEEE CICC}",
booktitle = "{IEEE BioCAS}",
booktitle = "{IEEE NEWCAS}",
booktitle = "{IEEE IRPS}",
```

Do **not** use forms such as:

- `Proceedings of the 34th European Solid-State Device Research Conference (ESSDERC)`
- `IEEE International Symposium on Circuits and Systems (ISCAS)`
- `Proc. IEEE Symposium on VLSI Circuits`
- any `booktitle` containing the publication year

For non-IEEE conferences, use the conventional acronym directly:

```bibtex
booktitle = "{DATE}",
booktitle = "{OECC}",
booktitle = "{SBCCI}",
booktitle = "{VDAT}",
```

Do not add an `IEEE` prefix unless the event is actually IEEE-sponsored.

## 5. Author, Year, and Page Consistency

Author lists must match the official record, including:

- given-name spelling,
- missing `and` between authors,
- consistent brace protection for surnames, e.g., `Yongfu {Li}`.

Year should reflect the official publication record. If the BibTeX key says
`Lou_2024_TFT` but the journal issue is dated 2025, keep the key if needed for
stable citations, but set the `year` field to the published year unless the
venue requires online-publication year.

Replace placeholder page ranges with the final published range, for example:

- journal article: `3524-3537`, not `1-14`
- dataset/descriptor article: `27-32`, not `1-7`
- express brief: `359-363`, not `1-5`

## 6. DOI, Abstract, and Duplicate Entries

Add `doi = {...}` to cited entries whenever a DOI exists.

Optional `abstract` fields are allowed for internal bibliography maintenance, but
only when copied from the official paper or publisher record. If added:

- convert LaTeX to plain text,
- do not paraphrase or summarize unless clearly marked as internal notes,
- do not let abstract insertion become an excuse to alter the title or venue.

Avoid duplicate BibTeX keys for the same paper. If legacy aliases must remain,
ensure title, authors, venue, pages, year, and DOI stay identical across keys.

Remove exporter noise when it is not needed for BibTeX, such as:

- `keywords = {...}` copied from IEEE Xplore,
- `ISSN = {...}`,
- malformed author lists copied directly from metadata dumps.

## 7. IEEE Journal Names (Full Title vs Abbreviation)

**Full official journal titles are valid** and are often the safest default when
metadata is verified against the publisher record, for example:

```bibtex
journal = "{IEEE Transactions on Electron Devices}",
journal = "{IEEE Journal of Solid-State Circuits}",
```

**Abbreviated forms are optional**, not required. Use them only as a deliberate,
**consistent** layout-compression choice when references spill or a hard page
limit leaves no better fix (after prose cuts and float adjustments). Do not
abbreviate journal names merely to make entries look more uniform.

When abbreviating, pick **one style for the whole file** and apply it
consistently. Common compact IEEE forms include:

```bibtex
journal = "{IEEE JSSC}",
journal = "{IEEE TCAS-I}",
journal = "{IEEE TCAS-II}",
journal = "{IEEE TED}",
journal = "{IEEE JFLEX}",
```

Alternatively, keep full titles in `reference.bib` and rely on `IEEEabrv.bib`
with `\bibliography{./IEEEabrv,./reference}` so BibTeX expands abbreviations at
render time—without editing verified `journal` fields by hand.

Within a chosen style, avoid awkward hybrids in the same file:

- mixing full `IEEE Transactions on ...` titles with hand-abbreviated fragments,
- `IEEE TCAS-II Exp. Briefs` when `IEEE TCAS-II` suffices,
- inconsistent word-by-word fragments such as `IEEE J. Flexible Electron.` next to
  `IEEE JSSC`.

Non-IEEE journals may keep publisher-standard full names or their conventional
abbreviations, e.g. `Analog Integrated Circuits and Signal Processing`.

## 8. Bibliography Maintenance Workflow

Recommended workflow for this repository:

1. collect PDFs into `paper/references/` using the BibTeX key as filename,
2. verify cited entries in `paper/reference.bib`,
3. compile from `paper/` with:

```bash
cd paper
latexmk -pdf 0_main_ieee_conference.tex
```

4. inspect the rendered references in the PDF,
5. let `paper/.latexmkrc` remove intermediate files after a successful build.

If a reference is cited in `paper/0_main_ieee_conference.tex`, treat it as
high priority for full metadata verification even if a PDF is not yet available.
