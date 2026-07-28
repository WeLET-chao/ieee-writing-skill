# Writing Plan

Generated or refreshed by `ieee-manuscript-scoping`. Update as the manuscript evolves.

## Target

- **Venue:**
- **Page limit:**
- **Main TeX:** `paper/main.tex`
- **Title:**

## Narrative (problem → gap → method → evidence → so what)

1. **Problem:**
2. **Gap in prior work:**
3. **Proposed method:**
4. **Strongest evidence (numbers):**
5. **So what:**

## Contributions

1.
2.
3.

## Evidence boundary

<!-- What is in scope vs explicitly omitted (metrics, plots, device types). -->

## Section outline

### Introduction

-

### Methodology

-

### Results

-

### Conclusion

-

## Figures and tables

| ID | File | Claim | Source type | Repo path | Status |
|----|------|-------|-------------|-----------|--------|
| Fig. 1 | | | | | |
| Table I | | | | | |

## Simulation and reproduction

<!-- ieee-manuscript-scoping §8: list exact commands after figure script resolution -->

```bash
# Simulation (if applicable):
# strain-spice run --config configs/...

# Paper figures (create paper/scripts/plot_*.py from ieee-manuscript-figures template, or copy from paper backup):
# python paper/scripts/plot_<slug>_figures.py
```

## Literature slugs used

<!-- paper/literature/<slug>/analysis.md -->

## Handoff

- [ ] **`ieee-manuscript-figures`** — plot scripts + `paper/figures/` (`figure_asset_plan.json`)
- [ ] `ieee-manuscript-prose` — fill TeX comment stubs
- [ ] `ieee-bib-hygiene` — verify cite keys
- [ ] `ieee-latex-layout` — compile
- [ ] `ieee-manuscript-revision` — full polish
