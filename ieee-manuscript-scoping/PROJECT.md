# Project integration (strained-device-model)

| Generic default | This repo |
|-----------------|-----------|
| `paper/main.tex` | **`paper/0_main_ieee_conference.tex`** |
| Literature | `paper/literature/` |
| Figure scripts | `paper/scripts/plot_ifetc_figures.py` |
| Configs | `configs/bsim4_nmos_dynamic.yaml`, `configs/transient_profiles_ngspice.yaml` |

## Example scoping run

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
AGENT_SKILLS="${AGENT_SKILLS:-$REPO_ROOT}"
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-scoping)"
mkdir -p "$REPO_ROOT/paper/out/scoping"

python3 "$SKILL/scripts/scan_repo_for_paper.py" \
  --repo-root "$REPO_ROOT" \
  --out "$REPO_ROOT/paper/out/scoping/repo_inventory.json"

# Agent fills scoping_decisions.json after user checkpoints, then:
python3 "$SKILL/scripts/scaffold_manuscript.py" \
  --repo-root "$REPO_ROOT" \
  --decisions "$REPO_ROOT/paper/out/scoping/scoping_decisions.json" \
  --inventory "$REPO_ROOT/paper/out/scoping/repo_inventory.json"
```

Set `"main_tex": "0_main_ieee_conference.tex"` in `scoping_decisions.json`.
Use `--bootstrap-tex` only for a **new** manuscript; this repo already has a full draft.

## Backups and test sandbox (this repo)

| Path | Role |
|------|------|
| `../strained-device-model-paper-backup-20260612/` | **Full `paper/`** snapshot |
| `../strained-device-model-scoping-test/` | Test repo; human manuscript stripped |
| `paper/manual/` | Quick copies of key hand-edited files |

Recreate test sandbox:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
SKILL="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-scoping)"
bash "$SKILL/scripts/prepare_scoping_test_repo.sh"
```

Before `--refresh-plan` on the canonical repo, refresh the full `paper/` backup first.

## Canonical figure script (copy source)

When scoping test sandbox lacks `paper/scripts/`, user may confirm copy from backup:

```bash
cp ../strained-device-model-paper-backup-20260612/scripts/plot_ifetc_figures.py \
   paper/scripts/
```

Otherwise **create** per scoping skill §8:

```bash
AGENT_SKILLS="${AGENT_SKILLS:-$(git rev-parse --show-toplevel)}"
FIGURES="$(bash "$AGENT_SKILLS/ieee-writing/scripts/skill_root.sh" ieee-manuscript-figures)"
mkdir -p paper/scripts
cp "$FIGURES/templates/generate_figures.template.py" \
   paper/scripts/plot_ifetc_figures.py
```

## Narrative anchors (from README)

- Device-agnostic strain wrapper + direction-aware map (Liu TNANO 2022)
- Dynamic extensions: bandwidth, rate, hysteresis, profile library
- BSIM4 reference case study; ngspice / Spectre workflow

Orchestrator: `ieee-manuscript-scoping/SKILL.md` (Phase B Step 0).
