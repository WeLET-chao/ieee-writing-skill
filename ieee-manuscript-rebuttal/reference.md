# IEEE Manuscript Rebuttal - Marked Manuscript Reference

## `\rev` macro

Tracked TeX must define (script injects if absent):

```latex
\usepackage{xcolor}
\newcommand{\rev}[1]{\textcolor{blue}{#1}}
```

Optional toggle for a clean build from the same file:

```latex
% \renewcommand{\rev}[1]{#1}  % uncomment for clean (no blue) PDF
```

Prefer a **separate** `main_tracked.tex` plus a clean `main.tex` rather than
shipping one file that reviewers must toggle.

## Sentence-level rules

1. Compare **submitted baseline** TeX to **revised** TeX.
2. If any token in a sentence differs, wrap the **entire revised sentence** in
   `\rev{...}`.
3. Brand-new sentences are fully blue.
4. Unchanged sentences stay black (even if nearby sentences changed).
5. Do not wrap one word, one `\cite{...}`, or a partial clause alone.

## What the marker should skip or handle carefully

| Region | Policy |
|--------|--------|
| `%` comment lines | Leave unchanged |
| `\begin{tabular}...\end{tabular}` and similar alignments | Do not sentence-split inside table rows |
| Figure/table `\caption{...}` | Wrap the **whole** caption in `\rev{...}` when caption text, float body (e.g. table cells), or any `\includegraphics` asset changed vs baseline (`--git-old` / `--old-asset-root`) |
| Display math `\[...\]` / `equation` | Leave structure; mark surrounding prose sentences |
| `\includegraphics` paths themselves | Leave unchanged; if the image file changed, mark the float caption |
| Title / author block | Mark only if the revision intentionally changed them |

## Why not default `latexdiff`

`latexdiff` is excellent for author review but usually emits **word-level**
color/`\DIFadd` markup. Many IEEE resubmit instructions want changes easy to
scan at **sentence** granularity. Use `latexdiff` only when the user asks for
that style explicitly; do not treat it as the default tracked deliverable of
this skill.

## Baseline selection

Prefer, in order:

1. User-named submitted PDF/TeX or git tag
2. Git commit recorded in the cover letter / decision email thread
3. `git show <commit>:main.tex` for the last submission on the branch

Record the baseline commit or path in `change_log.md`.

## Alignment evidence

In `reviewer_matrix.md`, optional column `tracked_cue` can quote the opening
words of the blue sentence so humans can search the PDF.

## Response-letter wording (uploadable DOCX/PDF)

| Do | Avoid |
|----|--------|
| Complete blue answers under each Question | “Known from the submitted manuscript / Still needed” in the final letter |
| Direct answers to **every sub-ask** in a multi-part comment | Pointing only to a section while leaving the *why* unanswered in the letter |
| Formal academic sentences | Note-like labels (`Contribution:`, `Die ladder:`) or “We retained …” |
| Varied thank-you openings, then the technical reply | One identical stock thank-you on every item |
| Standalone rewritten answers when Reviewer 2 repeats Reviewer 1 | “This comment overlaps Question X. See Response X.” / “also noted in Response …” |
| Claims restated from the tracked manuscript (same wording strength) | Escalating “dominated by …” into fake precision (`>99.9%`) or new mechanism numbers |
| “improved / optimized / redrawn for readability / updated” for figures | Leading with “regenerated” as the change claim |
| Quote revised manuscript sentences + embed key Fig./table evidence | Bare Response with no manuscript pointer |
| Preserve institutional letterhead, seal, Times, page breaks | Pandoc-from-Markdown that drops the template |
| Cover letter: short factual revision bullet list OK | Authors’ Responses opening laundry list / depth sermon |
| Short AE thank-you | AE process meta or naming ceremony |
| Short Authors’ Responses thank-you only | Prefacing with “Fig. N remains … / X unchanged / deferred for later” |
| Mention only edits that were actually made | Advertising unmodified items or optional future archives |
| Colon / comma / parentheses / hyphen `-` for ranges | Em dash `—` as a clause connector |
| Quotes with printed labels (“Table IX reports …”) | Placeholders (“Table reports …”, “the STA table”) |
| Table/Fig screenshots that include `TABLE N` / caption and IEEE-style body | Ad-hoc grids or caption-less crops that disagree with the tracked PDF |
| Short under-image pointer once the PNG already has the formal caption | Duplicating the full caption in two different styles |
| Response-only digests labeled as Section … summaries | Calling a non-float digest “Table N” |
| Selective adoption of LLM polish (tone + missing sub-answers) | Wholesale paste of an external “optimized” letter |

Scaffold inventory drafts are fine **internally**; convert them before portal upload.

## Triaging an external polish draft

When another model rewrites the cover letter / Responses:

1. Keep scaffold, blue color, page breaks, and evidence sync machinery.
2. Accept: formalization of note-like prose; explicit answers to named
   sub-questions; clearer contribution / verification-scope wording **already
   supported by the tracked PDF**.
3. Reject or rewrite: new physics or reliability claims; precision upgrades;
   em dashes; cross-ref stubs; long Authors’ Responses / AE preambles;
   Markdown dumps that abandon the institutional DOCX.
4. Target length: roughly half to two-thirds of a maximal LLM expansion.

## Sync checklist (quotes + screenshots)

Before regenerating the uploadable letter:

1. Build / open the **current** tracked PDF.
2. For each letter evidence block, search the PDF for the quoted opening words.
3. Confirm float numbers in lead-in, quote, and image caption agree
   (`aux` / PDF “TABLE VIII”, not a stale “Table VII”).
4. Re-render table PNGs **with** caption (`TABLE N` + caption text; blue if
   `\rev`); keep letter under-image text short.
5. If only prose numbers exist (no float), use a clearly titled summary image
   and say so in the letter caption.
