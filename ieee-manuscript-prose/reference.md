# Prose and Claims Revision Rules

Topic-agnostic rules for circuit, device, modeling, EDA, and measurement IEEE
short papers. Skill: `ieee-manuscript-prose`.

## 1. Core Writing Principle

Every major claim should follow a clear problem--mechanism--evidence chain:

1. State the design, modeling, measurement, or system problem.
2. Explain the mechanism or method that addresses it.
3. Show evidence under declared conditions.

Avoid presenting a paper as a list of figures, scripts, or implementation
details. A reviewer should be able to answer:

- What problem matters?
- Why are existing methods insufficient?
- What is the proposed technical idea?
- What evidence supports the claim?
- What is the exact scope of the claim?

## 2. Claim Scope and Evidence Alignment

Use bounded, auditable language.

Prefer:

- `under the adopted setup`
- `among the evaluated cases`
- `within the measured sweep`
- `for the demonstrated reference case`
- `before device-specific extraction is available`

Avoid unsupported universal wording:

- `always`
- `optimal`
- `fully solves`
- `general for all circuits`
- `guarantees robustness`

A claim is ready only when its scope matches the actual data. If a paper
evaluates one reference device, do not imply complete system-level validation.
If a paper evaluates one process corner, do not imply PVT-wide robustness. If a
paper demonstrates a model wrapper, distinguish model capability from extracted
device physics.

## 3. Abstract, Introduction, and Conclusion

### Abstract

The abstract should mirror the actual results section.

Checklist:

- Include the problem, method, and strongest evidence.
- Use the same quantitative anchors as the body.
- Do not introduce numbers that do not appear later.
- Do not overstate beyond the demonstrated setup.
- Keep method details short; reserve implementation specifics for the body.

### Introduction

A strong IEEE introduction usually moves in this order:

1. Application or technology motivation.
2. Why current practice is insufficient.
3. Specific technical gap.
4. Proposed approach.
5. Contributions and evidence.

Citation logic should be specific, not decorative. Separate citations by role:

- application background,
- device/process/platform evidence,
- prior modeling or design methodology,
- relevant circuit/system demonstrations.

Avoid citation piles where all references appear to support the same broad
sentence.

### Conclusion

The conclusion should do more than repeat the abstract. It should summarize:

- what was proposed,
- what was demonstrated,
- what the result enables,
- what scope remains bounded.

For short papers, one compact paragraph is acceptable, but it should still
include a forward-looking design or methodology implication when supported by
the evidence.

## 4. Methodology Wording

Prefer objective methodology statements over apology-style disclaimers.

Avoid:

```latex
We do not claim that the method is universally superior.
```

Prefer:

```latex
The comparison uses identical test conditions, model cards, input profiles,
and metric extraction scripts across all evaluated cases.
```

Avoid:

```latex
These results are only preliminary.
```

Prefer:

```latex
The experiment is used as a reference-case evaluation; device-specific dynamic
parameters remain future extraction targets.
```

The key is to state what is adopted, held fixed, measured, and compared.

### 4.0 Emphasize Novelty; Narrate the Ordinary

Allocate rhetorical weight by importance:

- **If a point is a true contribution or innovation**, state it explicitly and
  give it prominence (contribution bullets, abstract headline claim, results
  takeaway). Do not bury it in hedged clauses.
- **If a point is classical, expected, or routine**, narrate it objectively in
  one short clause with a citation when needed. Do **not** append defensive
  anti-claims that restate what the work is *not*.

Avoid repeating throughout results/DSE text:

```latex
..., which we report as a flow-level confirmation rather than a newly
discovered optimum.
..., rather than a contradiction of lookahead theory.
..., rather than as a new addition algebra.
HGGCBA does not claim a new carry algebra.
```

Prefer:

```latex
The selected \texttt{BLOCK\_SIZE}=16 coincides with the classical carry-skip
heuristic $m\approx\sqrt{N}$ for $N=256$~\cite{...}.
Grouped CLA with \texttt{GROUP\_SIZE}=4 and a linear inter-group carry chain
remains only moderately faster than RCA, as expected from its $O(N/4)$
organization.
```

Put novelty/scope framing **once**, early (introduction or contributions). In
later sections, report measurements and classical agreements without re-arguing
what is not claimed.

### 4.0b Quantitative Claim Density (General)

Prefer **absolute metrics once** plus **one** headline relative claim. Do not
stack parallel percentage deltas for every column in the same sentence.

Avoid:

```latex
... versus CSLA at 3.82~ns, 6561~\text{\textmu m\textsuperscript{2}}, and 11.69~fJ:
delay $-$26.7\%, area $-$3.8\%, and PDP $-$45.9\% (1.85$\times$ lower PDP).
```

Prefer (pick one relative form; do not also quote the complementary \%):

```latex
... achieves 1.99~ns delay, 6312~\text{\textmu m\textsuperscript{2}} core area, and
4.22~fJ PDP, i.e., 2.39$\times$ lower PDP than CSLA.
```

Rules of thumb:

- Abstract / contribution bullet / conclusion: same absolute anchors + **one**
  relative form (prefer a factor such as `2.39$\times$ lower PDP`, or a single
  percentage—not both).
- Results may give a second relative axis only when it is a **different
  comparison** (e.g., area vs prefix after PDP vs CSLA), not a third percentage
  on the same baseline.
- Do not append incidental scaling percentages (e.g., `+37.9\%` when width
  doubles) unless that percentage is the claim under discussion.

### 4.0c Caption Formality (General)

Captions state **what is shown**. Keep process narrative and cross-float
validation in the body.

Avoid colloquial / process language in captions:

```latex
% Weak
... selects BLOCK_SIZE=16, later confirmed in Table~I.
... as expected from their shorter logic depth.
```

Prefer:

```latex
% Stronger
... The U-shaped PDP curve identifies \texttt{BLOCK\_SIZE}=16 as the minimum.
... parallel-prefix baselines remain faster.
```

### 4.0d Future Work (not speculative outlook)

Conclusions may add **one** short future-work sentence when follow-on
verification is planned (e.g., other nodes, corners, or workloads). Do **not**
assert unmeasured gains, and do **not** float uncertain expectations such as
“whether the advantage widens” or “may further favor … at advanced nodes.”

Avoid long speculative paragraphs that claim exponential resistance scaling,
“strict” RC dominance, or that benefits “will amplify at 7~nm” without data.

Prefer a concrete next-step commitment:

```latex
Future work will continue post-route verification at more advanced technology
nodes.
```

Pattern: planned verification / extension → not an open-ended prediction about
unmeasured PPA. Keep mechanism arguments in Results; do not re-argue them in
the future-work line.

Domain-specific physical evidence (e.g., OpenROAD wirelength for adder
interconnect claims) lives in repo skills such as
`idea-adders/.cursor/skills/adder-idea-pipeline` and
`manuscript-eval-improvement`, not here.

### 4.0e Equation Cross-References (General)

Refer to numbered equations inline; do **not** prefix with `Eq.` or `Eqs.`

Avoid:

```latex
Eqs.~(\ref{eq:blockcarry})--(7) make the relationship explicit.
From Eq.~(5), carry-out is generated ...
```

Prefer:

```latex
In (\ref{eq:blockcarry}), carry-out is generated inside the block or propagated
from the prior block carry.
In (\ref{eq:blockcarry})--(7), the relationship to classical carry-skip is
explicit.
```

Use `In (n)` / `In (n)--(m)` at the start of the sentence (or clause) and state
the meaning immediately after the reference.

### 4.1 Prose Tone for Figure and Results Discussion

IEEE body text should read like measured technical reporting, not informal figure
commentary. This is especially important in short papers, where Results paragraphs
carry much of the evidence chain.

Preferred figure-opening verbs:

- `shows`
- `presents`
- `illustrates`
- `compares`

Avoid in formal body text unless space is extremely tight:

- `plots`
- `draws`
- `clarifies` when the figure itself is doing the explaining

Preferred comparative phrasing:

- `as a function of`
- `under a 5~s sinusoidal profile`
- `at equal applied strain`
- `the quasi-static reference (dashed)`
- `the dynamic trajectory`
- `exhibits a closed hysteresis loop`
- `indicating distinct loading and unloading responses`
- `does not capture`
- `whereas` / `In contrast,`

Avoid conversational cause-effect connectors and vague nouns:

- `..., so loading and recovery differ ...`
- `forms a loop`
- `the dynamic path`
- `hides waveform dependence`
- `clarify waveform dependence`
- `because its ramp has a weak rate term`

Before/after example from a recent revision:

```latex
% Weak
Fig.~3 plots $\Delta V_{\mathrm{th}}$ versus strain for the 5~s sine profile.
The dynamic path forms a loop, so loading and recovery differ at the same strain,
whereas the dashed quasi-static map is single-valued.

% Stronger
Fig.~3 shows $\Delta V_{\mathrm{th}}$ as a function of $\epsilon_S$ under a
5~s sinusoidal profile.
The dynamic trajectory exhibits a closed hysteresis loop, indicating distinct
loading and unloading responses at equal applied strain, whereas the
quasi-static reference (dashed) remains single-valued.
```

Additional patterns that usually improve IEEE tone:

```latex
% Weak
Staggered sub-percent peaks clarify waveform dependence: drift remains smooth
because its ramp has a weak rate term.

% Stronger
Staggered sub-percent peak amplitudes highlight waveform dependence: the drift
profile remains smooth owing to its limited ramp-induced rate contribution.
```

```latex
% Weak
Thus, a quasi-static strain map hides waveform dependence and load/unload memory.

% Stronger
Accordingly, the quasi-static strain map does not capture waveform dependence or
load/unload memory in the wrapper state.
```

Practical review order for prose tone:

1. Search for `;`, `plots`, `so `, `Thus,`, `because`, `hides`, `clarify`, and
   `forms a`.
2. Rewrite figure-opening sentences with `shows` or `presents`.
3. Replace vague curve nouns (`path`, `map`) with `trajectory`, `reference`, or
   `response` when discussing plotted behavior.
4. Split semicolon-chained clauses into separate sentences when possible.
5. Keep captions concise; move mechanism and implication to the body text.
5b. Keep **table** captions short; put parameter settings, metric definitions,
   and claim-scope notes in `tablenotes`, not in the caption paragraph.
6. Recompile and confirm page count after tone edits.

### 4.2 Avoid Semicolon-Chained Sentences and Em Dashes

In IEEE conference prose, semicolons often make sentences read like lab notes or
spoken commentary. Prefer short independent sentences joined by periods, or a
single sentence with `while`, `whereas`, or `and` when the relation is clear.

**Em dashes (`---`):** Do **not** use LaTeX em dashes in body text, captions,
abstracts, or conclusions. There is no default exception for “occasional”
narrative dashes. Rewrite with commas, periods, or parentheses.

**Allowed dash-like tokens (not em dashes):**

- Hyphen `-` for compound terms (`carry-bypass`, `ripple-carry`, `place-and-route`)
- En dash `--` for ranges (`8--128`), name compounds (`Kogge--Stone`), and
  compound adjectives (`power--delay`, `area--delay`)
- Comment-only rulers (`%-----...`)

**Mandatory report:** After editing or reviewing TeX, scan non-comment lines for
`---`. If any remain, report every line and a short snippet to the user before
finishing; do not silently leave them.

Default rewrite strategy:

1. Replace `clause A; clause B` with two sentences: `Clause A. Clause B.`
2. In captions, replace semicolons inside parentheses with commas or a second
   short sentence.
3. Reserve semicolons only when the venue style explicitly favors them.
4. Replace `text---aside---` / `claim---detail` with commas, parentheses, or
   `i.e.,` / `namely` phrasing.

Before/after examples from a recent revision:

```latex
% Weak
The wrapper inserts a strain engine ... without modifying core model equations;
the engine is emitted as embedded SPICE or Verilog-A for ngspice and Spectre flows.

% Stronger
The wrapper inserts a strain engine ... without modifying core model equations.
The engine is emitted as embedded SPICE or Verilog-A for ngspice and Spectre flows.
```

```latex
% Weak
Fig.~2 presents representative modes ... responses; staggered sub-percent peaks
highlight waveform dependence, while abrupt and pulse inputs induce ...

% Stronger
Fig.~2 presents representative modes ... responses.
Staggered sub-percent peaks highlight waveform dependence, while abrupt and pulse
inputs induce ...
```

```latex
% Weak (caption)
... sinusoidal loading (arrows indicate trajectory direction;
$\tau_{\mathrm{load}}/\tau_{\mathrm{unload}}$ in Table~I).

% Stronger (caption)
... sinusoidal loading (arrows indicate trajectory direction, with
$\tau_{\mathrm{load}}/\tau_{\mathrm{unload}}$ in Table~I).
```

When bounding representative parameters, state scope once and pivot to the
mechanism contrast instead of repeating defensive negatives:

```latex
% Weak (redundant scope defense)
... dynamic settings are representative rather than extracted.
Although not silicon-fitted, the representative settings contrast with ...

% Stronger (single scope statement)
For the BSIM4 reference evaluation, the parameters in Table~I are adopted.
Static terms follow [Liu_2022_TFT], while representative dynamic settings
contrast with the quasi-static map, which exhibits no mechanical delay or branch
dependence by construction.
```

### 4.3 Goal-Oriented and Causal Phrasing

In methodology and results prose, explain why a setup, simplification, figure, or
parameter choice appears before stating what was done. The goal is causal flow,
not a repeated `For ...` template.

Vary the sentence pattern across the paragraph:

- purpose first: `To reveal waveform-dependent behavior, Fig.~2 surveys ...`
- mechanism with embedded purpose: `... are encoded as control voltages that
  drive the strain engine`
- contrastive scope: `Although both pathways are available, the BSIM4 case study
  emphasizes ... to highlight ...`
- evaluation setup without `For the evaluation`: `A BSIM4 NMOS reference setup
  is evaluated using the parameters summarized in Table~I`
- consequence: `These results indicate that ... so the profile library is used
  as ...`

Useful opener families:

| Intent | Example patterns |
|--------|------------------|
| enable a flow | `In SPICE transient analysis, ... are encoded as ...` |
| preserve compatibility | `Without modifying core model equations, ...` |
| support tools | `... is emitted as ... to support ngspice and Spectre flows` |
| focus a case study | `... emphasizes ... to highlight ...` |
| expose a limitation | `... are chosen to expose the structural limitation of ...` |
| visual contrast | `To provide a direct visual contrast with ..., Fig.~3 plots ...` |
| survey behavior | `To reveal ..., Fig.~2 surveys ...` |

Prefer active focus statements over stiff disclaimers:

```latex
% Weak
The wrapper supports both $\Delta V_{\mathrm{th}}$ and $\Delta\mu$ modulation.
The BSIM4 case study reports $\Delta V_{\mathrm{th}}$ only.

% Stronger
Although both $\Delta V_{\mathrm{th}}$ and $\Delta\mu$ pathways are available,
the BSIM4 case study emphasizes $\Delta V_{\mathrm{th}}$ tracking to highlight
the dynamic strain-to-threshold response.
```

Replace checklist-style architecture prose with purpose plus mechanism:

```latex
% Weak
For the BSIM4 reference evaluation, the parameters in Table~I are adopted.
For comparison, Fig.~3 shows ...

% Stronger
A BSIM4 NMOS reference setup is evaluated using the parameters summarized in
Table~I.
To provide a direct visual contrast with the single-valued quasi-static map,
Fig.~3 plots $\Delta V_{\mathrm{th}}$ against $\epsilon_S$ ...
```

Guardrails for short IEEE papers:

- Do not start every sentence with `For` or `To`; vary with `In ...`, `Without
  ...`, `Although ...`, `These results indicate that ...`, and embedded
  `to ...` purpose clauses.
- Avoid brochure-like chains such as `To execute ... To accommodate ... To
  evaluate ... Finally, to ...` in a single paragraph.
- Prefer `emphasizes`, `is evaluated using`, `are chosen to expose`, or
  `provides a direct visual contrast` over `reports ... only`, `For comparison`,
  or `employs Table I`.

## 5. Results Section

Results should connect plots to design meaning.

A strong result paragraph often follows this shape:

1. Identify the figure or table.
2. State the observed behavior.
3. Explain the mechanism.
4. State the design implication.
5. Bound the scope.

Use the prose-tone rules in §4.1 when opening figure discussions. In
particular, prefer `shows`/`presents`, `as a function of`, `exhibits`,
`indicating`, and `does not capture` over informal wording such as `plots`,
`forms a loop`, `so ... differ`, or `hides`.

Avoid saying only what the reader can already see in the plot. Explain why the
trend matters for circuits, systems, modeling, verification, calibration, or
reliability.

When using representative settings, say so. Do not imply extracted physical
constants unless extraction was actually performed.
