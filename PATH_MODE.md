# Path mode for ieee-writing skills

Pick **one** installation mode and keep paths consistent across orchestrators and scripts.

## Modes

| Mode | Skill root example | When |
|------|-------------------|------|
| **agent-skills canonical** | `$REPO/ieee-writing/ieee-literature-search` | Working inside `agent-skills` meta repo |
| **Symlink** | `~/.agents/skills/ieee-literature-search` | Skills linked via `bootstrap_links.sh` |
| **Consumer embedded** | `$REPO/.cursor/skills/ieee-literature-search` | Skills copied/symlinked into a paper project |

Cross-group skills (same rules):

| Skill | agent-skills path |
|-------|-------------------|
| `paper-pdf-fetch` | `$REPO/paper-pdf-fetch` |
| `analyze-research-paper` | `$REPO/paper-pipeline/analyze-research-paper` |

## Recommended variables

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"   # consumer paper repo
AGENT_SKILLS=/path/to/agent-skills             # meta repo root when not the consumer

# ieee-writing skill (pick one):
SKILL="$AGENT_SKILLS/ieee-writing/ieee-literature-search"
# or
SKILL="$HOME/.agents/skills/ieee-literature-search"
# or
SKILL="$REPO_ROOT/.cursor/skills/ieee-literature-search"
```

## Orchestrator defaults

- `ieee-literature-pipeline` — examples use **agent-skills canonical** (`ieee-writing/...`, `paper-pipeline/...`, `paper-pdf-fetch`)
- `ieee-manuscript-revision` — examples use **consumer embedded** (`.cursor/skills/...`); override with `$SKILL` as above

## Do not mix

Avoid hardcoding project-specific paths like `PMIC/.skills/` in shared skill docs. Use `$REPO_ROOT`, `$AGENT_SKILLS`, or `$SKILL` variables.
