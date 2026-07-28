#!/usr/bin/env python3
"""Resolve an IEEE venue profile into an agent-readable briefing (schema v2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
PROFILES_DIR = SKILL_DIR / "profiles"

PILLARS = [
    ("latex_template", "1. LaTeX template"),
    ("figures_and_layout", "2. Figures and layout"),
    ("structure_and_narrative", "3. Structure and narrative"),
    ("bibliography", "4. BibTeX"),
    ("project_layout", "5. Project layout"),
]


def load_profile(profile_id: str) -> dict:
    path = PROFILES_DIR / f"{profile_id}.json"
    if not path.is_file():
        raise SystemExit(f"Unknown profile: {profile_id} (missing {path})")
    profile = json.loads(path.read_text(encoding="utf-8"))
    if profile.get("schema_version") != "2":
        raise SystemExit(f"Profile {profile_id} uses unsupported schema_version")
    return profile


def list_profiles() -> list[str]:
    return sorted(
        p.stem
        for p in PROFILES_DIR.glob("*.json")
        if not p.stem.startswith("_")
    )


def _lines_for_value(key: str, val: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    lines: list[str] = []
    if isinstance(val, dict):
        if not val:
            lines.append(f"{prefix}- `{key}`: {{}}")
            return lines
        if indent == 0:
            lines.append(f"{prefix}**{key}**")
        else:
            lines.append(f"{prefix}- `{key}`:")
        for k, v in val.items():
            lines.extend(_lines_for_value(k, v, indent + 1 if indent == 0 else indent + 1))
        return lines
    if isinstance(val, list):
        if not val:
            lines.append(f"{prefix}- `{key}`: []")
            return lines
        if all(isinstance(x, str) for x in val):
            lines.append(f"{prefix}- `{key}`: {', '.join(val)}")
        else:
            lines.append(f"{prefix}- `{key}`:")
            for item in val:
                if isinstance(item, dict):
                    summary = ", ".join(f"{k}={v!r}" for k, v in list(item.items())[:4])
                    lines.append(f"{prefix}  - {summary}")
                else:
                    lines.append(f"{prefix}  - {item}")
        return lines
    lines.append(f"{prefix}- `{key}`: {json.dumps(val, ensure_ascii=False)}")
    return lines


def format_section(block: dict) -> list[str]:
    lines: list[str] = []
    notes = block.pop("notes", None)
    for key, val in block.items():
        lines.extend(_lines_for_value(key, val, indent=0))
    if notes:
        lines.append("")
        for note in notes:
            lines.append(f"- *{note}*")
    return lines


def format_briefing(profile: dict) -> str:
    lines: list[str] = []
    pid = profile["profile_id"]
    lines.append(f"# Venue profile: {pid}")
    lines.append(f"- **Venue:** {profile.get('venue_name', '')}")
    lines.append(f"- **Schema:** v{profile.get('schema_version', '?')}")
    if profile.get("aliases"):
        lines.append(f"- **Aliases:** {', '.join(profile['aliases'])}")
    lines.append("")

    for key, title in PILLARS:
        block = profile.get(key, {})
        if not block:
            continue
        lines.append(f"## {title}")
        block_copy = json.loads(json.dumps(block))
        lines.extend(format_section(block_copy))
        lines.append("")

    exec_skills = profile.get("execution_skills", {})
    if exec_skills:
        lines.append("## Execution skills (secondary)")
        lines.append("Apply pillar content above; invoke these skills for implementation:")
        for pillar, skills in exec_skills.items():
            lines.append(f"- `{pillar}` → {', '.join(skills)}")
        lines.append("")

    checklist = profile.get("checklist", [])
    if checklist:
        lines.append("## Checklist")
        for item in checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile_id", nargs="?", help="Profile id, e.g. ieee-tcad-journal")
    parser.add_argument("--list", action="store_true", help="List available profile ids")
    parser.add_argument("--json", action="store_true", help="Print raw profile JSON")
    args = parser.parse_args()

    if args.list:
        for pid in list_profiles():
            print(pid)
        return

    if not args.profile_id:
        parser.error("profile_id required unless --list")

    profile = load_profile(args.profile_id)
    if args.json:
        json.dump(profile, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return

    sys.stdout.write(format_briefing(profile))


if __name__ == "__main__":
    main()
