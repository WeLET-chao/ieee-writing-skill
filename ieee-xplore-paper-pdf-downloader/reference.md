# IEEE Xplore PDF downloader reference

## Runtime assumption

This skill assumes the user's environment already has working IEEE Xplore access. The scripts do not bootstrap browser sessions, scrape alternate sites, or bypass access controls.

## Supported `PAPERS.md` layouts

The downloader supports both index layouts used by the related paper skills.

### Flat PDF layout

Downloaded PDFs are applied to:

```text
papers/<slug>.pdf
```

### Nested analysis layout

Downloaded PDFs are applied to:

```text
papers/<slug>/paper.pdf
```

The parser infers the nested layout when `docs/PAPERS.md` mentions `papers/<slug>/paper.pdf` or `papers/<slug>/analysis.md`.

## `PAPERS.md` table requirements

Expected header:

```markdown
| Title | Authors | Year | Venue | Category | DOI | Analysis | PDF |
```

The downloader reads:

- `DOI` column for DOI resolution
- `PDF` column for an IEEE Xplore `document/<article_number>` link or an IEEE search-result link

## Article-number resolution

Resolution order:

1. Extract `document/<id>` directly from the PDF cell link
2. Extract `arnumber=<id>` from the PDF cell link
3. If the PDF cell points to an IEEE search-result page and a DOI exists, resolve the DOI URL first
4. Otherwise request the PDF or DOI link and search the final URL or page text for `articleNumber`

## Concurrency-limit behavior

IEEE sometimes returns an HTML page or redirect indicating a concurrency block. The downloader detects these cases by:

- `reason=concurrency` in the final URL or response body
- HTTP `418`
- HTML responses that include the concurrency marker

Behavior:

- mark the failure with `IEEE_CONCURRENCY_BLOCK` in the log
- retry up to the configured retry count
- add an extra cooldown between papers after a concurrency failure

## Staging and apply model

`download_from_papers_md.py` uses a two-phase flow:

1. Download and validate each PDF into `--stage-dir`
2. Write `manifest.json`
3. If `--apply` is set and there are no failures, copy staged files into the repo `papers/` tree

This prevents partial writes into the target repo when some downloads fail.

## JSON input expectations

`download_from_article_json.py` expects JSON files whose top-level value is a list. Each item should contain:

```json
{
  "articleNumber": 11223063
}
```

Files without `articleNumber` are counted as failures and reported in the summary.

## Logs

The scripts write `ieee_download_errors.log` next to staged PDFs or next to the target output directory. These logs are runtime artifacts and are ignored by git.

## Repo root detection

`download_from_papers_md.py` resolves the circuit-work root by:

1. `--repo-root` when provided
2. Otherwise walking upward from the current working directory and the skill directory until it finds `*-lab/docs/PAPERS.md`

## Resume and batching

`manifest.json` under `--stage-dir` stores per-paper status (`pending`, `downloaded`, `existing`, `applied`, `failed`, `duplicate`).

- `--resume` merges prior manifest statuses before each run
- Existing valid PDFs under `*-lab/papers/` are marked `existing` and skipped
- `--max-papers N` limits how many pending rows are attempted per invocation
- `--apply-each` copies each successful download into the repo without waiting for the full corpus

Each run prints `AGENT_IEEE_PDF_STATUS {...}` for `/loop` automation. Exit code `2` means pending papers remain.

## Stable CLI surface

```bash
download_from_papers_md.py --repo-root PATH --papers-md PATH [--papers-md PATH ...] [--stage-dir PATH] [--apply]
download_from_papers_md.py --repo-root PATH --all-labs [--lab NAME ...] [--stage-dir PATH] [--resume] [--max-papers N] [--apply-each] [--status]
download_all_labs_batch.sh   # REPO_ROOT, STAGE_DIR, MAX_PAPERS env vars
download_from_article_json.py --article-info-dir DIR --pdf-base-dir DIR
download_ieee_pdf.py --article-number ID --output PATH [--max-retries N]
verify_pdf_tree.py ROOT_DIR [--depth N]
```
