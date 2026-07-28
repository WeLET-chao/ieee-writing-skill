---
name: ieee-xplore-paper-pdf-downloader
description: >-
  Download IEEE Xplore PDFs referenced from docs/PAPERS.md or article-number JSON
  exports, stage and validate them, then optionally apply them into papers/.
  Supports all *-lab repos, resume, batching, and status reporting for long-running
  /loop downloads. Use after ieee-xplore-paper-search and before analyze-research-paper
  when the user's environment already has working IEEE Xplore access.
---

# IEEE Xplore Paper PDF Downloader

> **This repo:** read [PROJECT.md](PROJECT.md) — downloads to `paper/literature/<slug>/paper.pdf`.

Download IEEE Xplore PDFs in bulk for literature-review repos. This skill assumes the user's runtime environment already has working IEEE Xplore access. If access fails, report the failed papers and stop; do not attempt workarounds.

Primary workflow: `*-lab/docs/PAPERS.md` -> staged PDFs -> optional `--apply` into `papers/` -> handoff to [analyze-research-paper](../analyze-research-paper/SKILL.md).

## Prerequisites

```bash
bash ~/.cursor/skills/ieee-xplore-paper-pdf-downloader/scripts/setup.sh
```

Use the skill venv wrapper when the venv is not activated:

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-pdf-downloader
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" --help
```

When the skill lives inside a repo at `.cursor/skills/ieee-xplore-paper-pdf-downloader`, prefer that copy and pass `--repo-root` explicitly.

## Workflow

Copy and track:

```text
- [ ] Confirm the repo already has working IEEE Xplore access in this environment
- [ ] Identify the target *-lab/docs/PAPERS.md file(s) or use --all-labs
- [ ] Run --status to see pending counts across labs
- [ ] Run batched downloads with --resume --apply-each --max-papers N
- [ ] Re-run /loop until AGENT_IEEE_PDF_STATUS reports complete=true
- [ ] Hand off downloaded papers to analyze-research-paper
```

## Primary flow - single lab `docs/PAPERS.md`

Use this after [ieee-xplore-paper-search](../ieee-xplore-paper-search/SKILL.md) has appended pending rows with DOI and IEEE Xplore links.

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-pdf-downloader
REPO=/path/to/circuit-work

"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO" \
  --papers-md "$REPO/cdac-lab/docs/PAPERS.md" \
  --stage-dir /tmp/ieee-pdf-stage
```

Stage-only mode downloads and validates PDFs under the stage directory, then writes `manifest.json`. It does not modify the target repo.

When every staged record succeeds:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO" \
  --papers-md "$REPO/cdac-lab/docs/PAPERS.md" \
  --stage-dir /tmp/ieee-pdf-stage \
  --apply
```

`--apply` copies validated staged files into the target repo `papers/` layout.

## All labs under one repo

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-pdf-downloader
REPO=/path/to/circuit-work

# Status only — no downloads
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO" \
  --all-labs \
  --stage-dir /tmp/ieee-pdf-stage \
  --resume \
  --status

# Next batch (recommended for large corpora)
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO" \
  --all-labs \
  --stage-dir /tmp/ieee-pdf-stage \
  --resume \
  --apply-each \
  --max-papers 10
```

`--all-labs` scans every `*-lab/docs/PAPERS.md` under `--repo-root`.

Convenience wrapper:

```bash
REPO=/path/to/circuit-work MAX_PAPERS=10 \
  bash "$SKILL/scripts/download_all_labs_batch.sh"
```

### New flags for long-running downloads

| Flag | Purpose |
|------|---------|
| `--repo-root PATH` | Circuit-work root (auto-detected from cwd when omitted) |
| `--lab NAME` | Limit `--all-labs` to one or more lab directories (repeatable) |
| `--resume` | Reuse `manifest.json` statuses and skip PDFs already in `papers/` |
| `--max-papers N` | Download at most N pending papers per invocation |
| `--apply-each` | Copy each successful download into the repo immediately |
| `--status` | Print per-lab pending/complete summary; emits `AGENT_IEEE_PDF_STATUS` JSON |

Exit codes:

- `0` — all papers complete (or `--status` with nothing pending)
- `2` — batch ran but papers remain pending (continue the loop)
- `1` — hard failure in the current batch

## Loop until all PDFs are downloaded

Use dynamic `/loop` pacing for large corpora (tens of thousands of papers). Run one batch immediately, then re-arm a heartbeat until `complete=true`.

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-pdf-downloader
REPO=/path/to/circuit-work
STAGE=/tmp/ieee-pdf-stage-circuit-work

"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO" \
  --all-labs \
  --stage-dir "$STAGE" \
  --resume \
  --apply-each \
  --max-papers 10
```

On each wake:

1. Parse the latest `AGENT_IEEE_PDF_STATUS {"complete":...}` line from the prior run.
2. If `complete` is true, stop the loop and report success.
3. Otherwise rerun the same batch command.
4. If concurrency failures appear in `ieee_download_errors.log`, increase the fallback heartbeat delay.

Suggested fallback heartbeat when IEEE throttles: **5–15 minutes** between batches (each paper already waits 8 s internally).

## Secondary flow - article-number JSON exports

Use this when you already have JSON files containing `articleNumber` entries.

```bash
SKILL=~/.cursor/skills/ieee-xplore-paper-pdf-downloader

"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_article_json.py" \
  --article-info-dir /path/to/articleInfo \
  --pdf-base-dir /path/to/PDF
```

The script preserves the JSON directory tree and writes PDFs under `<pdf-base-dir>/<relative-json-dir>/<json-stem>/`.

## One-off debugging and validation

Download one paper:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_ieee_pdf.py" \
  --article-number 11223063 \
  --output /tmp/11223063.pdf
```

Verify a PDF tree:

```bash
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/verify_pdf_tree.py" \
  /path/to/papers --depth 3
```

## Failure handling

- Treat inaccessible IEEE content as a normal failure mode.
- Do not bulk `--apply` when any record in that batch failed; prefer `--apply-each` for incremental progress.
- When IEEE returns a concurrency block page, the scripts retry and record the failure marker in the log.
- Review the per-run `ieee_download_errors.log` file written beside staged or output PDFs.
- Failed rows stay in `manifest.json`; a later `--resume` run retries only pending items.

## Handoff to analysis

After PDFs land under `*-lab/papers/`, run [analyze-research-paper](../analyze-research-paper/SKILL.md) on the downloaded PDFs.

Typical sequence:

1. Search and append pending rows with [ieee-xplore-paper-search](../ieee-xplore-paper-search/SKILL.md)
2. Download PDFs with this skill (batched `/loop` for full corpora)
3. Generate `analysis.md` with [analyze-research-paper](../analyze-research-paper/SKILL.md)

## Additional resources

- Behavior details and layouts: [reference.md](reference.md)
- Stable CLI entrypoints: `scripts/download_from_papers_md.py`, `scripts/download_all_labs_batch.sh`, `scripts/download_from_article_json.py`, `scripts/download_ieee_pdf.py`, `scripts/verify_pdf_tree.py`
