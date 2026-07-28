# ieee-writing skills

Canonical repository: [WeLET-chao/ieee-writing-skill](https://github.com/WeLET-chao/ieee-writing-skill).  
In [agent-skills](https://github.com/WeLET-chao/agent-skills), this group is mounted as the `ieee-writing/` git submodule.

This group supports IEEE-style manuscript workflows from literature discovery to draft generation, revision, and submission readiness checks.

## Table of contents

- [Workflow phases](#workflow-phases)
- [Skill map](#skill-map)
- [Quick start](#quick-start)
- [Environment setup](#environment-setup)
- [Working assumptions](#working-assumptions)

## Workflow phases

1. Literature collection and digesting
2. Manuscript scoping and drafting
3. Iterative revision and final review

## Skill map

### Literature phase

- `ieee-literature-pipeline` (orchestrator)
- `ieee-xplore-paper-search`
- `paper-pdf-fetch` (submodule in agent-skills)
- `analyze-research-paper` (from `paper-pipeline`)
- `synthesize-paper-corpus` (optional)

### Drafting and structure phase

- `ieee-venue-profiles`
- `ieee-manuscript-scoping`
- `ieee-tcad-journal-manuscript` (journal path)
- `ieee-manuscript-prose`
- `ieee-manuscript-figures`
- `ieee-latex-layout`
- `ieee-bib-hygiene`

### Revision phase

- `ieee-manuscript-revision` (orchestrator)
- `ieee-manuscript-final-review`

## Quick start

For literature-oriented workflows, start from the orchestrator:

```bash
# Skill is consumed by the agent through ~/.agents/skills
# Primary entrypoint for end-to-end literature flow:
ieee-literature-pipeline
```

For drafting, set venue constraints first:

```bash
ieee-venue-profiles
ieee-manuscript-scoping
```

## Environment setup

Most skills in this group are markdown and shell workflows and do **not** ship a Python venv.

Skills that need a local `.venv` (gitignored; not in the repo):

| Skill | Setup |
|-------|--------|
| `ieee-xplore-paper-search` | `bash scripts/setup.sh` |

PDF download uses [paper-pdf-fetch](../paper-pdf-fetch/SKILL.md) (`bash paper-pdf-fetch/scripts/setup.sh` from agent-skills root).

Literature analysis depends on [paper-pipeline `analyze-research-paper`](../paper-pipeline/README.md#environment-setup); set up that skill's venv separately.

`setup.sh` uses `python3 -m venv` + `pip`. To use uv instead:

```bash
SKILL=/path/to/agent-skills/ieee-writing/ieee-xplore-paper-search
uv venv --python 3.10 "$SKILL/.venv"
uv pip install --python "$SKILL/.venv/bin/python" requests bibtexparser
```

## Working assumptions

- Most skills assume a `paper/` workspace layout and IEEE-focused conventions.
- Run `ieee-venue-profiles` early so downstream prose, figure, and layout skills receive the same venue constraints.
