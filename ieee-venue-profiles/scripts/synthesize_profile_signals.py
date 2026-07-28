#!/usr/bin/env python3
"""Aggregate venue_signals.json files into a profile patch report."""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
LITERATURE = SKILL_DIR / "calibration" / "literature"
OUT = SKILL_DIR / "calibration" / "_corpus" / "profile_synthesis_report.md"


def load_signals() -> list[dict]:
    rows: list[dict] = []
    if not LITERATURE.is_dir():
        return rows
    for path in sorted(LITERATURE.glob("*/venue_signals.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_path"] = str(path.relative_to(SKILL_DIR))
        rows.append(payload)
    return rows


def median_int(values: list[int]) -> int | None:
    if not values:
        return None
    return int(round(statistics.median(values)))


def main() -> int:
    signals = load_signals()
    by_profile: dict[str, list[dict]] = defaultdict(list)
    for s in signals:
        by_profile[s.get("profile_id", "unknown")].append(s)

    lines: list[str] = ["# Venue profile synthesis report", ""]
    if not signals:
        lines.append("No `calibration/literature/*/venue_signals.json` files found.")
        lines.append("Complete analyze + VENUE_SIGNAL_EXTRACT.md step first.")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote {OUT} (empty)")
        return 0

    lines.append(f"Papers with signals: **{len(signals)}**")
    lines.append("")

    for pid, group in sorted(by_profile.items()):
        lines.append(f"## {pid} (n={len(group)})")
        pages = [g["estimated_pages"] for g in group if g.get("estimated_pages")]
        figs = [g.get("figures_and_layout", {}).get("figure_count") for g in group]
        figs = [f for f in figs if isinstance(f, int)]
        tabs = [g.get("figures_and_layout", {}).get("table_count") for g in group]
        tabs = [t for t in tabs if isinstance(t, int)]
        algs = [g.get("figures_and_layout", {}).get("algorithm_count") for g in group]
        algs = [a for a in algs if isinstance(a, int)]
        abss = [g.get("structure_and_narrative", {}).get("abstract_sentences") for g in group]
        abss = [a for a in abss if isinstance(a, int)]

        mp = median_int(pages)
        mf = median_int(figs)
        mt = median_int(tabs)
        ma = median_int(algs)
        mabs = median_int(abss)

        if mp is not None:
            lines.append(f"- Median pages: **{mp}**")
        if mf is not None:
            lines.append(f"- Median figures: **{mf}**")
        if mt is not None:
            lines.append(f"- Median tables: **{mt}**")
        if ma is not None:
            lines.append(f"- Median algorithms: **{ma}**")
        if mabs is not None:
            lines.append(f"- Median abstract sentences: **{mabs}**")

        titles: list[str] = []
        for g in group:
            titles.extend(g.get("structure_and_narrative", {}).get("section_titles") or [])
        common = Counter(titles).most_common(8)
        if common:
            lines.append("- Common section titles: " + ", ".join(f"`{t}` ({c})" for t, c in common))

        runin = sum(
            1
            for g in group
            if g.get("structure_and_narrative", {}).get("results_runin_heads")
        )
        if group:
            lines.append(f"- Results run-in heads: **{runin}/{len(group)}** papers")

        lines.append("")
        lines.append("### Suggested profile patches (review before applying)")
        if mp is not None:
            lines.append(
                f"- `figures_and_layout.page.typical_min` / `typical_max`: consider `{max(1, mp - 2)}`–`{mp + 2}`"
            )
        if mf is not None:
            lines.append(f"- `figures_and_layout.figures.minimum_count`: consider `{max(1, mf - 1)}`")
        if mt is not None:
            lines.append(f"- `figures_and_layout.tables.minimum_count`: consider `{max(0, mt)}`")
        if ma is not None and ma >= 1:
            lines.append(f"- `figures_and_layout.algorithms.minimum_count`: consider `{ma}`")
        if mabs is not None:
            lo, hi = max(4, mabs - 2), mabs + 2
            lines.append(f"- `structure_and_narrative.abstract.sentence_count`: consider `[{lo}, {hi}]`")
        if runin >= max(2, len(group) // 2):
            lines.append("- `structure_and_narrative.results.subsection_style`: keep `bold_runin_heads`")

        lines.append("")
        lines.append("### Sources")
        for g in group:
            slug = g.get("source_slug", "?")
            notes = g.get("agent_notes", "")
            lines.append(f"- `{slug}`: {notes[:200]}{'…' if len(notes) > 200 else ''}")
        lines.append("")

    lines.append("## Next step")
    lines.append("Edit `profiles/<profile_id>.json` per pillar; require ≥3 agreeing papers or one official exemplar.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
