# Project integration (strained-device-model)

| Generic skill default | This repo |
|----------------------|-----------|
| `*-lab/docs/PAPERS.md` | **`paper/literature/PAPERS.md`** |
| `papers/<slug>/paper.pdf` | **`paper/literature/<slug>/paper.pdf`** |

The downloader detects `paper/literature/PAPERS.md` when `--repo-root` points at this repository.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL="$REPO_ROOT/.cursor/skills/ieee-xplore-paper-pdf-downloader"
"$SKILL/scripts/run_python.sh" "$SKILL/scripts/download_from_papers_md.py" \
  --repo-root "$REPO_ROOT" \
  --papers-md "$REPO_ROOT/paper/literature/PAPERS.md" \
  --stage-dir /tmp/ieee-pdf-stage \
  --apply
```

For **cited** bibliography PDFs, copy or symlink to `paper/references/<bibkey>.pdf` (`ieee-bib-hygiene`).

Orchestrator: `ieee-literature-pipeline/SKILL.md`.
