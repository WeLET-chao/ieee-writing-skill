"""Shared Matplotlib publication style for IEEE two-column paper figures.

All ``ideaX/scripts/*`` plotting entrypoints should import from this module so
font sizes, dpi, palette, and grids stay consistent across ideas.

Normative references:

- ``.cursor/skills/ieee-manuscript-figures/reference.md`` §1 (figure rules)
- ``.cursor/skills/ieee-manuscript-figures/SKILL.md`` (asset layout workflow)

Palette (fixed black + five MATLAB-style primaries, RGB in ``[0,1]``):

- Blue ``[0, 0, 1]``, Red ``[1, 0, 0]``, Green ``[0, 128/255, 0]``,
  Purple ``[112/255, 48/255, 160/255]``, Orange ``[234/255, 112/255, 13/255]``.

Canvas default (single axes): **1600×900 px** at ``DEFAULT_DPI`` (MATLAB-style
logical size; doubled from an 800×450 baseline for clearer included PNGs). Use
``figsize_publication(nrows, ncols)`` so multi-panel figures scale
proportionally (each subplot cell ≈ one default tile).

Scripts run as ``python ideaX/scripts/foo.py`` from the repository root add::

    import sys
    from pathlib import Path

    _ROOT = Path(__file__).resolve().parents[2]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

    from scripts.plot_publication import PALETTE, apply_publication_style

"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Optional, Sequence, Union

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Patch

DEFAULT_DPI: Final[int] = 180

# Single-panel pixel canvas (MATLAB-style ``figure`` width/height).
FIG_WIDTH_PX: Final[int] = 1600
FIG_HEIGHT_PX: Final[int] = 900

GRID_KWARGS: Final[dict[str, Any]] = {
    "linestyle": "--",
    "linewidth": 0.5,
    "alpha": 0.6,
}

# Fixed black + five primaries (Blue, Red, Green, Purple, Orange). Semantic keys
# map baselines to stable slots; ``orange`` is the fifth distinct series color.
PALETTE: Final[dict[str, str]] = {
    "abba": "#000000",
    "rca": "#0000FF",
    "cska": "#FF0000",
    "carry_select": "#7030A0",
    "brent_kung": "#008000",
    "orange": "#EA700D",
    "black": "#000000",
    "blue": "#0000FF",
    "red": "#FF0000",
    "purple": "#7030A0",
    "green": "#008000",
}


def figsize_publication(
    nrows: int = 1,
    ncols: int = 1,
    *,
    width_px: Optional[int] = None,
    height_px: Optional[int] = None,
    dpi: int = DEFAULT_DPI,
) -> tuple[float, float]:
    """Return figure ``figsize`` in inches for the standard pixel canvas at ``dpi``.

    One subplot tile defaults to ``FIG_WIDTH_PX`` × ``FIG_HEIGHT_PX`` pixels
    (1600×900). A grid uses ``ncols`` tiles horizontally and ``nrows`` vertically,
    matching MATLAB-style proportional scaling for ``subplot`` layouts.

    Args:
        nrows: Number of subplot rows (minimum 1).
        ncols: Number of subplot columns (minimum 1).
        width_px: Override width of **one** tile in pixels (default ``FIG_WIDTH_PX``).
        height_px: Override height of **one** tile in pixels (default ``FIG_HEIGHT_PX``).
        dpi: Dots per inch used when saving (must match ``savefig_publication``).

    Returns:
        ``(width_in, height_in)`` tuple suitable for ``plt.subplots(figsize=...)``.
    """
    w_tile = FIG_WIDTH_PX if width_px is None else width_px
    h_tile = FIG_HEIGHT_PX if height_px is None else height_px
    cols = max(int(ncols), 1)
    rows = max(int(nrows), 1)
    return (w_tile * cols / dpi, h_tile * rows / dpi)


def apply_publication_style(**overrides: Any) -> None:
    """Update Matplotlib rcParams (Arial, bold 18 pt axes, thick lines/markers).

    Default line width **3** and marker size **12** match MATLAB ``LineWidth`` /
    ``MarkerSize``. Axis spines use linewidth **3**; tick labels are bold **18** pt.

    Callers should still set **xlim** / **ylim** explicitly per dataset so ranges
    are data-appropriate.

    Args:
        **overrides: Optional rcParams merged last (for isolated experiments).
    """
    base: dict[str, Any] = {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Bitstream Vera Sans", "sans-serif"],
        "font.size": 18,
        "font.weight": "bold",
        "axes.titlesize": 18,
        "axes.titleweight": "bold",
        "axes.labelsize": 18,
        "axes.labelweight": "bold",
        "axes.linewidth": 3.0,
        "xtick.labelsize": 18,
        "ytick.labelsize": 18,
        "legend.fontsize": 18,
        "lines.linewidth": 3.0,
        "lines.markersize": 12.0,
    }
    base.update(overrides)
    plt.rcParams.update(base)


def axes_grid(ax: Axes, **kwargs: Any) -> None:
    """Apply the repository default dashed grid to one axes."""
    merged = {**GRID_KWARGS, **kwargs}
    ax.grid(True, **merged)


def point_label_ha(
    x: float,
    x_min: float,
    x_max: float,
    *,
    left_frac: float = 1.0 / 3.0,
    right_frac: float = 2.0 / 3.0,
) -> str:
    """Choose Matplotlib text ``ha`` from a marker's relative x position.

    Generation-time hygiene: keep point labels inside the axes so visual QA does
    not have to catch overflow after export.

    Rule of thumb (data coordinates over the plotted x-span):

    - Marker in the **left** third → ``\"left\"`` (text grows rightward into the plot).
    - Marker in the **right** third → ``\"right\"`` (text grows leftward into the plot).
    - Otherwise → ``\"center\"``.

    Args:
        x: Marker abscissa in data coordinates.
        x_min: Left edge of the relevant x-span (usually ``ax.get_xlim()[0]`` after
            limits are set, or ``min(xs)`` of the plotted series).
        x_max: Right edge of the relevant x-span.
        left_frac: Upper bound of the left band as a fraction of the span.
        right_frac: Lower bound of the right band as a fraction of the span.

    Returns:
        One of ``\"left\"``, ``\"center\"``, or ``\"right\"`` for ``ax.text(..., ha=...)``.
    """
    span = float(x_max) - float(x_min)
    if span <= 0.0:
        return "left"
    t = (float(x) - float(x_min)) / span
    if t <= left_frac:
        return "left"
    if t >= right_frac:
        return "right"
    return "center"


def pass_fail_codes(
    values: np.ndarray,
    *,
    pass_mask: Optional[np.ndarray] = None,
    zero_atol: float = 0.0,
) -> np.ndarray:
    """Return float array with ``0.0`` (FAIL) / ``1.0`` (PASS) for discrete red/green maps.

    When ``pass_mask`` is provided, it must broadcast to ``values.shape``; ``True`` means PASS.
    Otherwise PASS is ``np.isclose(values, 0.0, atol=max(zero_atol, 0.0), rtol=0.0)``.

    Args:
        values: Raw metric grid (for example mismatch counts or mismatch rates).
        pass_mask: Optional explicit boolean PASS mask.
        zero_atol: Absolute tolerance when inferring zero from floating-point ``values``.

    Returns:
        Array of shape ``values.shape`` with entries ``0.0`` or ``1.0`` (``float`` dtype).
    """
    if pass_mask is not None:
        mask = np.asarray(pass_mask, dtype=bool)
    else:
        mask = np.isclose(np.asarray(values, dtype=float), 0.0, atol=max(float(zero_atol), 0.0), rtol=0.0)
    return np.where(mask, 1.0, 0.0)


def draw_pass_fail_heatmap(
    ax: Axes,
    values: np.ndarray,
    *,
    x_tick_labels: Sequence[str],
    y_tick_labels: Sequence[str],
    xlabel: str,
    ylabel: str,
    title: str,
    show_title: bool = True,
    pass_mask: Optional[np.ndarray] = None,
    zero_atol: float = 0.0,
    overlay_text: Optional[np.ndarray] = None,
    overlay_color: str = "#ffffff",
    overlay_fontsize: int = 14,
    legend_title: str = "Functional result",
    pass_label: str = "PASS (0 mismatches)",
    fail_label: str = "FAIL (>0 mismatches)",
    legend_bbox: tuple[float, float] = (1.02, 1.0),
    show_legend: bool = True,
) -> None:
    """Draw a binary PASS/FAIL heatmap (STA-style) on ``ax``.

    Uses ``ListedColormap([PALETTE['red'], PALETTE['green']])`` with ``vmin=0``,
    ``vmax=1`` so FAIL codes map to red and PASS codes map to green. Adds a
    patch legend (no continuous colorbar) consistent with core-adders STA
    closure heatmaps.

    Important policy:
        For sweep/verification matrices where *all* points pass, callers should
        skip figure generation entirely and express the all-pass result in
        manuscript text/table instead of exporting a dedicated heatmap.

    Args:
        ax: Target axes.
        values: Numeric grid (same semantics as ``pass_fail_codes``).
        x_tick_labels: Tick labels for columns (left-to-right).
        y_tick_labels: Tick labels for rows (top-to-bottom; ``imshow`` origin is upper).
        xlabel: X axis label text.
        ylabel: Y axis label text.
        title: Axes title text.
        pass_mask: Optional explicit PASS mask; see ``pass_fail_codes``.
        zero_atol: Zero tolerance for inferred PASS; see ``pass_fail_codes``.
        overlay_text: Optional string array same shape as ``values`` for per-cell text.
        overlay_color: Text color for overlays.
        overlay_fontsize: Font size for overlays.
        legend_title: Legend title string.
        pass_label: Legend label for PASS (code ``1``).
        fail_label: Legend label for FAIL (code ``0``).
        legend_bbox: ``bbox_to_anchor`` for the legend (axes fraction).
    """
    arr = np.asarray(values, dtype=float)
    codes = pass_fail_codes(arr, pass_mask=pass_mask, zero_atol=zero_atol)
    cmap = ListedColormap([PALETTE["red"], PALETTE["green"]])
    ax.imshow(codes, cmap=cmap, vmin=0.0, vmax=1.0, interpolation="nearest", aspect="auto")
    ax.set_xticks(np.arange(len(x_tick_labels)))
    ax.set_xticklabels(list(x_tick_labels))
    ax.set_yticks(np.arange(len(y_tick_labels)))
    ax.set_yticklabels(list(y_tick_labels))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if show_title:
        ax.set_title(title)
    if overlay_text is not None:
        text_arr = np.asarray(overlay_text)
        if text_arr.shape != arr.shape:
            raise ValueError("overlay_text must match values shape")
        for row in range(arr.shape[0]):
            for col in range(arr.shape[1]):
                ax.text(
                    col,
                    row,
                    str(text_arr[row, col]),
                    ha="center",
                    va="center",
                    color=overlay_color,
                    fontsize=overlay_fontsize,
                )
    if show_legend:
        ax.legend(
            handles=[
                Patch(facecolor=PALETTE["green"], edgecolor="none", label=pass_label),
                Patch(facecolor=PALETTE["red"], edgecolor="none", label=fail_label),
            ],
            title=legend_title,
            loc="upper left",
            bbox_to_anchor=legend_bbox,
            frameon=False,
        )


def style_colorbar(
    colorbar: Any,
    *,
    label: str | None = None,
    label_fontsize: int = 18,
    tick_labelsize: int = 18,
) -> None:
    """Improve heatmap colorbar tick and label sizing for included PNGs."""
    colorbar.ax.tick_params(labelsize=tick_labelsize)
    if label is not None:
        colorbar.set_label(label, fontsize=label_fontsize)


def savefig_publication(
    fig: Figure,
    path: Union[str, Path],
    *,
    dpi: int = DEFAULT_DPI,
    strip_titles: bool = True,
    **kwargs: Any,
) -> None:
    """Save figure at the repository standard DPI.

    By default, subplot titles are removed before export because figure context
    should be expressed in paper captions rather than duplicated inside images.
    """
    if strip_titles:
        for axis in fig.axes:
            axis.set_title("")
    fig.savefig(path, dpi=dpi, **kwargs)
