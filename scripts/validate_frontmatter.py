#!/usr/bin/env python3
"""Validate SKILL.md frontmatter for Cursor compatibility (single-line description)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

IEEE_WRITING = Path(__file__).resolve().parents[1]


def validate_skill_md(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    if text.startswith("\ufeff"):
        errors.append("BOM before opening ---")
        text = text.lstrip("\ufeff")

    if not text.startswith("---"):
        errors.append("file must start with ---")
        return errors

    if not re.match(r"^---\n(.*?)\n---", text, re.DOTALL):
        errors.append("missing YAML frontmatter delimited by --- (Cursor regex)")

    lines = text.splitlines()
    delim = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if len(delim) < 2:
        errors.append(f"expected 2 --- delimiters, found {len(delim)}")
        return errors

    fm_text = "\n".join(lines[1 : delim[1]])
    if "description: >-" in fm_text or "description: |" in fm_text:
        errors.append("use single-line quoted description (not >- or | blocks)")

    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        errors.append(f"invalid YAML: {exc}")
        return errors

    if not isinstance(data, dict):
        errors.append("frontmatter must be a mapping")
        return errors

    for key in ("name", "description"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"missing or empty field: {key}")

    return errors


def main() -> int:
    skill_paths = sorted(IEEE_WRITING.glob("*/SKILL.md"))
    failed = False
    for path in skill_paths:
        errors = validate_skill_md(path)
        if errors:
            failed = True
            print(f"{path.relative_to(IEEE_WRITING)}:")
            for err in errors:
                print(f"  - {err}")
    if failed:
        return 1
    print(f"OK: {len(skill_paths)} SKILL.md files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
