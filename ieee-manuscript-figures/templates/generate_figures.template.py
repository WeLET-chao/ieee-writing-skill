#!/usr/bin/env python3
"""Template for IEEE paper figure scripts.

Copy to ``paper/scripts/generate_figures.py`` and adapt data paths.
Import the shared style module from this skill (or repo-root shim).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = REPO_ROOT / ".cursor/skills/ieee-manuscript-figures/scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from plot_publication import (  # noqa: E402
    PALETTE,
    apply_publication_style,
    figsize_publication,
    point_label_ha,
    savefig_publication,
)

PAPER_DIR = REPO_ROOT / "paper"
FIGURES_DIR = PAPER_DIR / "figures"


def main() -> None:
    """Generate publication figures under paper/figures/."""
    apply_publication_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Example skeleton — replace with project data and plot functions.
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize_publication())
    ax.plot([0, 1], [0, 1], color=PALETTE["blue"], label="example")
    ax.set_xlabel("x [unit]")
    ax.set_ylabel("y [unit]")
    # Annotated markers: pick ha from relative x so labels stay inside the axes.
    # ax.text(x, y, "name", ha=point_label_ha(x, *ax.get_xlim()), va="bottom")
    ax.legend()
    savefig_publication(fig, FIGURES_DIR / "fig_example.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
