"""Shared utilities for synthesize-paper-corpus scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
BOLD_HEADING_RE = re.compile(r"\*\*([^*]+)\*\*")
BULLET_RE = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)


def load_profile(profile_path: Path) -> dict[str, Any]:
    """Load a JSON profile describing corpus input and section mapping.

    Args:
        profile_path: Path to a profile JSON file.

    Returns:
        Parsed profile dictionary.

    Raises:
        FileNotFoundError: If the profile does not exist.
        json.JSONDecodeError: If the profile is not valid JSON.
    """
    return json.loads(profile_path.read_text(encoding="utf-8"))


def resolve_glob(repo_root: Path, glob_pattern: str) -> list[Path]:
    """Resolve analysis digest files under a repository root.

    Args:
        repo_root: Repository root directory.
        glob_pattern: Glob relative to repo_root (e.g. papers/*/analysis.md).

    Returns:
        Sorted list of matching file paths.
    """
    return sorted(repo_root.glob(glob_pattern))


def read_markdown(path: Path) -> str:
    """Read a UTF-8 markdown digest.

    Args:
        path: Markdown file path.

    Returns:
        File contents as a string.
    """
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(text: str) -> str:
    """Remove HTML comments from markdown text."""
    return HTML_COMMENT_RE.sub("", text).strip()


def extract_title(content: str, level: int = 1) -> str:
    """Extract the first level-N markdown heading as title."""
    if level == 1:
        match = TITLE_RE.search(content)
        return match.group(1).strip() if match else "Unknown"
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", re.MULTILINE)
    match = pattern.search(content)
    return match.group(1).strip() if match else "Unknown"


def extract_table_field(content: str, field_name: str) -> str:
    """Extract a bibliographic table cell by field name."""
    for match in TABLE_ROW_RE.finditer(content):
        key = match.group(1).strip()
        if key.lower() == field_name.lower():
            return match.group(2).strip()
    return ""


def section_map(content: str) -> dict[str, str]:
    """Map level-2 headings to their body text."""
    matches = list(HEADING_RE.finditer(content))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections[heading] = strip_comments(content[start:end])
    return sections


def extract_section(sections: dict[str, str], heading_aliases: list[str]) -> str:
    """Return the first matching section body for a list of heading aliases."""
    alias_map = {alias.lower(): alias for alias in heading_aliases}
    for heading, body in sections.items():
        if heading.lower() in alias_map:
            return body.strip()
    return ""


def parse_category_block(text: str) -> dict[str, str]:
    """Parse Primary/Secondary/Note category block used by analyze-research-paper."""
    primary = re.search(r"Primary:\s*`([^`]+)`", text)
    secondary = re.search(r"Secondary:\s*`([^`]+)`", text)
    note = re.search(r"^Note:\s*(.+)$", text, re.MULTILINE)
    return {
        "primary": primary.group(1).strip() if primary else "uncategorized",
        "secondary": secondary.group(1).strip() if secondary else "",
        "note": note.group(1).strip() if note else "",
    }


def parse_comma_tags(text: str) -> dict[str, str]:
    """Parse comma-separated tags into a synthetic primary category."""
    tags = [tag.strip().strip("`") for tag in re.split(r"[,\n]", text) if tag.strip()]
    primary = tags[0] if tags else "uncategorized"
    secondary = ", ".join(tags[1:]) if len(tags) > 1 else ""
    return {"primary": primary, "secondary": secondary, "note": ""}


def parse_category(text: str, parse_mode: str) -> dict[str, str]:
    """Parse a category section using the configured parse mode."""
    if parse_mode == "comma_tags":
        return parse_comma_tags(text)
    return parse_category_block(text)


def extract_bibliographic(content: str, bibliographic: dict[str, Any]) -> dict[str, str]:
    """Extract bibliographic metadata defined by a profile."""
    result: dict[str, str] = {}
    for field_name, spec in bibliographic.items():
        source = spec.get("source", "table")
        if source == "heading":
            result[field_name] = extract_title(content, spec.get("level", 1))
        elif source == "table":
            result[field_name] = extract_table_field(content, spec.get("field", field_name))
        else:
            result[field_name] = ""
    return result


def extract_sections(content: str, section_specs: dict[str, Any]) -> dict[str, Any]:
    """Extract all configured sections from a digest."""
    heading_sections = section_map(content)
    extracted: dict[str, Any] = {}
    for section_key, spec in section_specs.items():
        headings = spec.get("headings", [])
        body = extract_section(heading_sections, headings)
        extracted[section_key] = body
        if spec.get("parse") in {"category_block", "comma_tags"}:
            extracted["category"] = parse_category(body, spec["parse"])
            extracted["category_raw"] = body
    return extracted


def bullet_items(text: str) -> list[str]:
    """Return markdown bullet items from a section body."""
    return [match.group(1).strip() for match in BULLET_RE.finditer(text)]


def prior_art_headings(text: str) -> list[str]:
    """Extract bold prior-art subheadings from a section."""
    return [match.group(1).strip() for match in BOLD_HEADING_RE.finditer(text)]


def slug_from_path(path: Path, repo_root: Path) -> str:
    """Derive a paper slug from a digest path."""
    relative = path.relative_to(repo_root)
    parts = relative.parts
    if len(parts) >= 2:
        return parts[-2]
    return path.stem


def parse_year(year_text: str) -> int | None:
    """Parse a publication year from free text."""
    match = re.search(r"(19|20)\d{2}", year_text)
    return int(match.group(0)) if match else None


def era_label(year: int | None, buckets: list[int]) -> str:
    """Assign a year to an era bucket label."""
    if year is None:
        return "unknown"
    sorted_buckets = sorted(buckets)
    if year < sorted_buckets[0]:
        return f"≤{sorted_buckets[0]}"
    for index in range(len(sorted_buckets) - 1):
        low = sorted_buckets[index]
        high = sorted_buckets[index + 1]
        if low <= year < high:
            return f"{low}-{high - 1}"
    return f"{sorted_buckets[-1]}+"
