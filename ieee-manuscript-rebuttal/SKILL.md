---
name: ieee-manuscript-rebuttal
description: "Structures IEEE manuscript reviewer responses: point-by-point rebuttal letter (institutional DOCX/PDF with blue answers, varied thank-yous, standalone replies, revised quotes/figures), change log mapped to TeX diffs, sentence-level blue marked manuscript (tracked PDF), and resubmission checklist. Core principle: know what to say and what not to say. Answer every sub-ask in formal prose; positive scope framing; audit out internal meta notes (float-status asides, figure-styling inventories, ranking disclaimers). Lock claims to the tracked manuscript; cover-letter revision bullets OK, Authors’ Responses/AE openings stay short. Triage LLM polish drafts selectively. Sync quotes/screenshots to the current tracked PDF. Avoid em dashes as connectors. Use when drafting a response letter, revision plan, or blue track-changes PDF before resubmitting."
---

# IEEE Manuscript Rebuttal

Use after review comments arrive. Orthogonal to a full `ieee-manuscript-revision`
polish pass: this skill owns the **reviewer loop** and the **marked manuscript**,
not general prose/figure polish.

**Core principle: know what to say and what not to say.** A rebuttal is not a
status dump. Every sentence should either (a) answer the reviewer’s ask or
(b) point to a real manuscript change with evidence. Extra honesty about
unchanged figures, deferred archives, portal process, or “we will also …”
invites chase. Silence on non-asks is professional, not evasive.

Read [reference.md](reference.md) for `\rev` conventions, markup rules, and the
say / don’t-say table.

## Inputs

- Reviewer PDF or pasted comments
- Current manuscript TeX (e.g. `paper/*.tex` or project `main.tex`)
- Bibliography as cited by the manuscript
- **Revision baseline** for the marked PDF: git commit / tag of the submitted
  manuscript, or an explicit old `.tex` path (ask if unclear)

## Outputs

```text
paper/rebuttal/response.md              # point-by-point letter
paper/rebuttal/change_log.md            # what changed in TeX/figures/bib
paper/rebuttal/reviewer_matrix.md       # comment ID → status → evidence
paper/rebuttal/main_tracked.tex         # sentence-level \rev{...} markup
paper/rebuttal/main_tracked.pdf         # blue marked PDF for resubmission
```

Paths may sit next to the manuscript if the project is not under `paper/`
(e.g. `reviewer-comments/` + `main_tracked.pdf` beside `main.tex`). Prefer a
single `rebuttal/` (or `reviewer-comments/tracked/`) folder and record it in
`change_log.md`.

## Workflow

```text
- [ ] Parse reviewer comments into numbered items (R1-C1, R2-C3, …)
- [ ] Classify each: accept / partial / decline-with-evidence
- [ ] Map each item to manuscript location (section, figure, equation, table)
- [ ] Draft response.md (polite, specific; cite fig/table/section)
- [ ] List required TeX/bib/figure edits in change_log.md
- [ ] Apply manuscript edits (optionally via ieee-manuscript-revision on
      changed sections only)
- [ ] Build marked manuscript (sentence-level blue) vs revision baseline
- [ ] Align response ↔ change_log ↔ blue sentences (every promised change
      must be findable)
- [ ] Sync letter quotes + Table/Fig screenshots (with captions) to current
      tracked PDF float numbers/wording
- [ ] ieee-manuscript-final-review on the clean manuscript before resubmit
- [ ] Resubmit package checklist (below)
```

## Marked manuscript (required for many IEEE journal resubmits)

Journals often ask for Track Changes or equivalent highlighting. For LaTeX:

1. **Color:** revised / new text in **blue** via `\rev{...}` → `\textcolor{blue}{...}`.
2. **Granularity:** mark **whole sentences**, not individual words. If one word
   in a sentence changed, wrap the **entire sentence**.
3. **Deletions:** do not rely on red strikethrough word salad; omit deleted
   sentences from the marked PDF (clean new prose in blue where replaced).
4. **Do not** use default `latexdiff` word-level CFONT markup as the deliverable
   unless the user explicitly wants that style. Prefer
   `scripts/mark_revision_sentences.py`.
5. Ship **both** a clean PDF (no blue) and a tracked PDF when the venue asks
   for highlighted changes.

### Build tracked TeX/PDF

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
REB="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-rebuttal)"

# old = submitted baseline; new = revised working tree
# Always pass --git-old (or --old-asset-root) with --asset-root so only
# actually changed figure binaries blue their captions. --asset-root alone
# no longer spuriously marks every float (missing baseline is skipped).
python3 "$REB/scripts/mark_revision_sentences.py" \
  --old path/to/submitted/main.tex \
  --new path/to/revised/main.tex \
  --out path/to/rebuttal/main_tracked.tex \
  --asset-root path/to/revised \
  --git-repo path/to/revised \
  --git-old <submitted-commit>

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=path/to/rebuttal path/to/rebuttal/main_tracked.tex
```

From a git baseline (example):

```bash
git show <submitted-commit>:main.tex > /tmp/main_submitted.tex
python3 "$REB/scripts/mark_revision_sentences.py" \
  --old /tmp/main_submitted.tex --new main.tex --out rebuttal/main_tracked.tex \
  --asset-root . --git-repo . --git-old <submitted-commit>
```

The script injects `\usepackage{xcolor}` and `\newcommand{\rev}[1]{\textcolor{blue}{#1}}`
when missing. See [reference.md](reference.md).

## Response style

### What to say / what not to say (primary filter)

Before drafting each Response, ask: *Did the reviewer ask this?* If no, omit it.

| Say | Do not say |
|-----|------------|
| Direct answer to the asked point | Unrelated extra context “for completeness” |
| What you **changed** (section / fig / table) + short evidence | What you **did not** change (“Fig. N remains…”, “X unchanged”) |
| Scoped decline **only when declining that ask**, with evidence | Deferred / optional / “archived for later” / “Incomplete X omitted” volunteer notes |
| Short AE thank-you; address AE comments that actually exist | Process narration (“no AE comments”, “we will mention the paper ID”) |
| Authors’ Responses: one thank-you sentence | Opening laundry list of improved vs untouched figures / blue-markup sermon |
| Standalone rewrite when R2 repeats R1 | “See Response X” / overlap stubs |
| Claims supported by sim / measurement / literature | Promises you cannot back in this revision |

Team-internal drafts may track Known / Still needed / deferred items.
**Uploadable letter and cover letter must not leak that inventory.**

### Multi-part comments: answer in the letter, prove in the manuscript

Reviewers often pack several sub-asks into one numbered item (physics *why*,
metric tables, verification scope, corner cases). Treat each sub-ask as
mandatory in the **Response body**, not only as a pointer to a section:

- Name the sub-ask briefly, then give a **direct technical answer** in formal
  academic prose (complete sentences).
- Follow with the manuscript change + quote / screenshot evidence as usual.
- Prefer about **50-70%** of a verbose LLM rewrite: enough to feel answered,
  short enough to stay evidence-locked.

Do **not** invent mechanism numbers, percentages, tool versions, or bend /
field claims that are absent from the tracked manuscript. If the paper says
“dominated by cell leakage,” do not escalate to “>99.9%” in the letter unless
that figure is computed and reported. Qualitative *why* is fine when it
restates mechanisms already in the paper (e.g. resistive-load pull-ups, local
decode timing, channel quantization).

### Formal prose (not internal notes)

Uploadable Responses must read as letter prose, not lab notes:

| Prefer | Avoid |
|--------|--------|
| “The contribution of this work is the G3SC overlay: …” | `Contribution:` / `Die ladder:` / `Same-library flat check:` labels |
| “We expanded Section … / clarified …” | “We retained …” / “Fig. N remains …” (process inventory) |
| Standalone rewrite when R2 repeats R1 | “As also noted in Response 1.5 …” |
| Positive scope: what was verified and why it suffices | Stacked “we do not claim X / no measured Y” closers |
| “Redrawn Figs. 3 and 5 for legibility” | Figure-styling inventories (label size, violet/orange, “color split”, junction markup) |
| “Summary of the … numbers reported in Section …” | Parenthetical float-status asides (`not a separate manuscript float`) |
| Outcome-led comparison (“PlaceRAM yields DRC-clean macros”) | Ranking-disclaimer stacks (`not used to rank density or fmax`) |
| “same-library flat RTL comparison / section” | Lab labels (`context experiment`, `shared-compiler context only`) |

When limiting scope, lead with the completed evidence and the study’s role
(e.g. “PDK-backed post-route STA across liberty corners is the appropriate
evidence level for this compiler study”). Prefer that framing over ending on
what was *not* measured, unless the reviewer explicitly demanded a decline.

### Pre-upload letter hygiene audit

Before regenerating the final DOCX/PDF, search the letter text for **team-internal
scaffolding** that must never ship. Typical leaks:

| Leak pattern | Why it fails | Fix |
|--------------|--------------|-----|
| `(not a separate manuscript float)` / `response-only digest` / `supporting Response N` | Process note for authors, not reviewers | Point to the section/table that owns the numbers; keep the image, drop the aside |
| Figure edit inventories (fonts, colors, straightened wires) | Reviewer asked for readability, not a changelog of drawing ops | One short “redrawn for legibility” + show the figure |
| `context experiment` / `context only` / `not an alternate proposed flow` | Defensive lab framing | State the comparison purpose and the positive outcome |
| `not used to rank …` / `not a density or fmax ranking` | Sounds like arguing with the ask | End on what the comparison establishes |
| `we do not claim …` / `no measured …` closers | Negative scope dump | Positive evidence-level sentence |
| Stale quotes vs tracked PDF (e.g. “cell leakage” after body moved to “static cell power”) | Letter/manuscript drift | Re-copy quotes after every TeX edit |

`(blue text)` markers that point to the tracked PDF are fine when the venue
uses blue revision markup. Keep those; remove only author-process asides.

### Manuscript body ≠ rebuttal meta-talk

Revised **manuscript** prose must also stay reader-facing. Do **not** paste
rebuttal scaffolding into `main.tex`:

| Prefer in the paper | Avoid in the paper |
|---------------------|--------------------|
| “To evaluate X against Y, we …” | “To answer the request for …” / “as the reviewer asked …” |
| Objective comparison + measured outcome | Defensive inventories (“this is not a ranking…”, “context experiment only”) as the thesis |
| Mechanism sentences that close multi-part asks (FO4→period gap; resistor-bias vs $I_{\mathrm{off}}$) | Leaving those *why* answers only in the letter |
| Stable cross-PDK wording (“evaluated at post-PlaceRAM placement”) | Lab shorthand in Abstract/Conclusion (`sky130NAND remains PlaceRAM pre-PnR`) |

Keep scoped disclaimers short and technical (e.g. flat dies are non-clean
outlines). Put process caveats in the letter if needed, not as manuscript
meta-talk.

### Cover letter vs Authors’ Responses preamble

- **Cover letter (to EIC):** a short numbered list of what this revision
  changed is appropriate (contribution clarity, new table/section, redrawn
  figures). Keep it factual and aligned with the tracked PDF.
- **Authors’ Responses opening:** one thank-you sentence only. Do **not**
  paste the cover-letter laundry list or a “significantly improved depth”
  sermon there.
- **AE block:** short thank-you; address only comments that exist. No process
  meta (“please check attachments”).

### Using LLM polish drafts

External “optimized rebuttal” drafts are useful for tone and for surfacing
unanswered sub-asks. Do **not** paste them wholesale into the DOCX:

1. Diff against the current letter and the tracked manuscript.
2. Adopt formalization + missing sub-answers that the paper already supports.
3. Reject new physics, bend/reliability claims, false precision, em dashes,
   cross-ref stubs, and long Authors’ Responses / AE preambles.
4. Keep the institutional scaffold, blue Responses, and quote/screenshot sync
   workflow; only rewrite Response/cover text.

### Per-item mechanics

- One block per reviewer comment; quote or paraphrase the comment first
- Thank first (vary openings), then answer every sub-ask in that comment
- State the change made, or why no change (with evidence / scope limit)
- Point to a concrete location (section / figure / table) and, when useful,
  that the sentence appears in blue in the tracked PDF
- **Punctuation:** do **not** use em dashes (`—`) as clause connectors in the
  letter. Prefer a colon, comma, parentheses, or a new sentence. Ordinary
  hyphens (`-`) are fine for compounds and numeric ranges (e.g. `MT1-MT2`,
  `7-10%`).

## Response letter production (DOCX / PDF)

Many IEEE journals want a **point-by-point letter** with institutional letterhead,
not a Markdown dump. Prefer editing the venue/author **DOCX template** (cover
letter + responses) and exporting PDF; do not rebuild from scratch with pandoc
unless no template exists.

### Hard rules (from JFLEX-style resubmits)

1. **Final letter ≠ Known/Still needed scaffolding.** Early inventory drafts may
   use “Known from the submitted manuscript / Still needed,” but the uploaded
   response must be complete answers only.
2. **Author replies in blue** (Times New Roman, ~10 pt), matching manuscript
   revision color: each `Response N.N` body **and** the short thank-you that
   answers a reviewer’s overall preamble (“We thank you for your time in
   reviewing… Below are our point-by-point responses”). Questions and the
   reviewer’s quoted comments stay black.
3. **Thank the reviewer first**, then answer. Vary the opening across items
   (do not reuse one stock sentence). Template patterns:
   - “Thank you for your valuable comment. We agree that …”
   - “Thank you for this constructive suggestion. …”
   - “We appreciate this helpful feedback. …”
   - “We thank the reviewer for this insightful comment on ….”
   - “We sincerely thank the reviewer for highlighting ….”
4. **No cross-ref stubs.** Never write “This comment overlaps Question X. See
   Response X.” Even if content overlaps, rewrite a **standalone** answer
   (slightly rephrased), optionally re-attach the same figure/table excerpt.
5. **Show manuscript evidence under each accept/partial item**, after the blue
   Response:
   - Lead-in: “We have revised Section … / improved Fig. … / added Table N as
     follows:” (name the **current** section title and float number)
   - Short **quoted** revised sentence(s) in blue (italic optional) - copy from
     the latest tracked PDF, not from an earlier draft placeholder
   - Embed the **revised figure** and/or a **table excerpt** when that is the
     evidence (see “Quotes and float screenshots” below)
6. **Figure/table wording.** Prefer *improved*, *optimized*, *redrawn for
   readability*, *updated*, *clarified* - **not** “regenerated” as the main
   claim of what changed for the reviewer.
7. **Page breaks.** Keep cover letter on its own page; start “Author’s Responses
   …” on a new page; start “Reviewer #2:” (and later reviewers) on a new page.
   Preserve template letterhead/seal. Do not insert duplicate page breaks that
   create blank pages.
8. **Cover letter tense.** Say the revision **is prepared** / **addresses**
   concerns, not that evidence is “still required” or the team is “still
   preparing,” once the response is final. A short factual bullet list of
   revision highlights is fine on the cover letter only.
9. **Apply the say / don’t-say filter (above) to every paragraph.** Common
   leaks to delete before upload: “Fig. N remains…”, “archived for later”,
   Authors’ Responses figure laundry lists, AE process meta, cross-ref stubs,
   note-like `Contribution:` labels, em dashes, and precision/claims not in
   the tracked manuscript.

### Quotes and float screenshots (sync to tracked PDF)

Letter evidence drifts when the manuscript is revised after the first DOCX fill.
Treat the **current** `main_tracked.pdf` (or venue equivalent) as the source of
truth every time the letter is regenerated.

**Quoted prose**

- Resolve `\ref{tab:…}` / `\ref{fig:…}` to the **printed** labels (Table VIII,
  Fig. 5, subsection D, …) before pasting into the letter.
- Never leave placeholders such as “Table reports …” or “the STA table”.
- Lead-ins should name the same float/section the quote uses
  (e.g. “subsection D (Macro Power) and Table IX”).
- After any TeX edit that adds/removes floats, re-diff every letter quote
  against the new PDF text.

**Table / figure screenshots**

- Prefer a crop or re-render that matches the **manuscript** look (IEEE
  horizontal rules, math for `$f_{\max}$` / `$\times$`, blue caption text if
  the tracked float is blue) - not an ad-hoc Word/Excel grid from an early
  inventory.
- **Include the float caption in the image**: `TABLE N` / `FIG. N` plus the
  caption sentence. Under the image in the letter, keep only a short pointer
  (“Revised Table IX from the manuscript.”) so the formal caption is not
  duplicated in two styles.
- If the letter needs a **response-only summary** of prose numbers that are
  not a manuscript float (e.g. a die-ladder digest), label the image caption
  clearly as a summary of Section …, not as “Table N”.
- Re-export PNG assets whenever the float body, caption, or table number
  changes; then refill the DOCX.

### Preferred build path

```text
1. Copy institutional scaffold DOCX (letterhead + Question blocks)
2. Replace Known/Still needed with blue Response + thank-you + evidence
3. Sync quotes to current tracked PDF (real Table/Fig numbers + wording)
4. Re-render/crop Fig./Table screenshots WITH captions; insert after each item
5. Export PDF via LibreOffice/Word; verify: no Known/Still needed,
   no “overlaps … See Response”, no “Fig./X remains unchanged” volunteering,
   no float-status / figure-styling / ranking-disclaimer internal asides,
   short Authors’ Responses thank-you only, no blank pages, blue responses,
   no stale “Table reports …” placeholders, screenshots match tracked floats
```

Record the scaffold path, asset-render command, and export command in
`change_log.md`.

## Response ↔ manuscript alignment (hard rule)

For each `accept` / `partial` item in `reviewer_matrix.md`:

- `change_log.md` names the files/sections touched
- The clean manuscript contains the substance of the change
- The tracked PDF shows the corresponding **sentence(s)** in blue
- Letter **quotes**, **float numbers**, and **screenshots** match that same
  tracked PDF build (not an older asset folder)

Fail the task if the letter claims a change that is not in the manuscript, or
if evidence images/quotes lag the current tracked PDF.

## Resubmit checklist

```text
- [ ] Clean manuscript PDF (no revision color)
- [ ] Tracked / blue manuscript PDF (sentence-level)
- [ ] Point-by-point response letter (PDF or DOCX as venue requires)
- [ ] Letter quotes use printed Table/Fig/section labels from tracked PDF
- [ ] Table/figure screenshots include captions and match manuscript formatting
- [ ] Pre-upload hygiene audit passed (no float-status / styling / ranking asides)
- [ ] Cover letter / Author Comments cites original manuscript ID
- [ ] change_log.md and reviewer_matrix.md retained for the team
- [ ] Final review / compile clean on the submission TeX
```

## Related skills

| Step | Skill |
|------|--------|
| Full revision polish after plan | `ieee-manuscript-revision` |
| Prose fixes | `ieee-manuscript-prose` |
| New figures for reviewer requests | `ieee-manuscript-figures` |
| Bib updates | `ieee-manuscript-bib` |
| Resubmission check | `ieee-manuscript-final-review` |
| Venue contract | `ieee-venue-profiles` |

## Templates

| Path | Purpose |
|------|---------|
| `templates/response.md` | Point-by-point letter skeleton |
| `templates/change_log.md` | Edit inventory |
| `templates/reviewer_matrix.md` | Comment tracking table |

## Invoke examples

- `@ieee-manuscript-rebuttal` draft the IEEE-XXXX-2026 response letter and matrix
- `@ieee-manuscript-rebuttal` build sentence-level blue `main_tracked.pdf` vs `HEAD`
- `@ieee-manuscript-rebuttal` check response claims against the tracked PDF
- `@ieee-manuscript-rebuttal` re-sync letter Table/Fig screenshots and quotes to `main_tracked.pdf`
