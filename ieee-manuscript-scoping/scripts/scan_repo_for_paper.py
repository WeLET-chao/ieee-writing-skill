#!/usr/bin/env python3
"""Scan a research repository for manuscript scoping inputs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _read_text_head(path: Path, max_chars: int = 8000) -> str:
    """Read the start of a text file safely."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""


def _markdown_headings(text: str) -> list[str]:
    """Extract level-2 markdown headings from README text."""
    headings: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def _pyproject_package(repo_root: Path) -> dict[str, Any]:
    """Parse minimal metadata from pyproject.toml."""
    path = repo_root / "pyproject.toml"
    if not path.is_file():
        return {}
    text = _read_text_head(path, 12000)
    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    scripts: list[str] = []
    in_scripts = False
    for line in text.splitlines():
        if line.strip() == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts and line.startswith("["):
            break
        if in_scripts:
            m = re.match(r'^(\S+)\s*=', line)
            if m:
                scripts.append(m.group(1))
    return {
        "name": name_match.group(1) if name_match else "",
        "scripts": scripts,
    }


def _collect_configs(repo_root: Path) -> list[str]:
    """List YAML config paths relevant to simulations."""
    patterns = ["configs/*.yaml", "configs/*.yml", "*.yaml"]
    found: list[str] = []
    for pattern in patterns:
        for path in sorted(repo_root.glob(pattern)):
            if path.is_file():
                rel = path.relative_to(repo_root).as_posix()
                if rel not in found:
                    found.append(rel)
    return found


def _collect_paper_assets(paper_dir: Path) -> dict[str, Any]:
    """Inventory files under paper/."""
    if not paper_dir.is_dir():
        return {
            "exists": False,
            "main_tex_candidates": [],
            "writing_plan": "",
            "reference_bib": "",
            "scripts": [],
            "figure_data_dirs": [],
        }
    tex_files = sorted(p.name for p in paper_dir.glob("*.tex"))
    scripts = sorted(
        p.relative_to(paper_dir).as_posix()
        for p in paper_dir.glob("scripts/*")
        if p.is_file()
    )
    figure_data = sorted(
        p.relative_to(paper_dir).as_posix()
        for p in paper_dir.glob("figure_data/*")
        if p.is_dir()
    )
    writing_plan = "writing_plan.md" if (paper_dir / "writing_plan.md").is_file() else ""
    reference_bib = "reference.bib" if (paper_dir / "reference.bib").is_file() else ""
    return {
        "exists": True,
        "main_tex_candidates": tex_files,
        "writing_plan": writing_plan,
        "reference_bib": reference_bib,
        "scripts": scripts,
        "figure_data_dirs": figure_data,
    }


def _collect_literature(literature_dir: Path) -> dict[str, Any]:
    """Inventory literature slugs and analysis artifacts."""
    if not literature_dir.is_dir():
        return {"papers_md": "", "slugs": []}
    papers_md = "PAPERS.md" if (literature_dir / "PAPERS.md").is_file() else ""
    slugs: list[dict[str, Any]] = []
    for child in sorted(literature_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        slugs.append(
            {
                "slug": child.name,
                "has_analysis": (child / "analysis.md").is_file(),
                "has_pdf": (child / "paper.pdf").is_file(),
            }
        )
    return {"papers_md": papers_md, "slugs": slugs}


def scan_repo(repo_root: Path) -> dict[str, Any]:
    """Build a JSON-serializable inventory for manuscript scoping.

    Args:
        repo_root: Repository root containing README and optional paper/.

    Returns:
        Inventory dict written by the CLI.
    """
    readme_path = repo_root / "README.md"
    readme_text = _read_text_head(readme_path) if readme_path.is_file() else ""
    title_line = ""
    for line in readme_text.splitlines():
        if line.startswith("# "):
            title_line = line[2:].strip()
            break
    headings = _markdown_headings(readme_text)
    lower = readme_text.lower()
    package = _pyproject_package(repo_root)
    src_dir = repo_root / "src"
    src_top = sorted(p.name for p in src_dir.iterdir() if p.is_dir()) if src_dir.is_dir() else []
    tests_dir = repo_root / "tests"
    tests = (
        sorted(p.relative_to(repo_root).as_posix() for p in tests_dir.rglob("test_*.py"))
        if tests_dir.is_dir()
        else []
    )
    plot_script_hints: list[str] = []
    for test_path in tests_dir.rglob("test_*figure*.py") if tests_dir.is_dir() else []:
        text = _read_text_head(test_path, 4000)
        for match in re.finditer(r"paper[/\\]scripts[/\\]([a-zA-Z0-9_]+\.py)", text):
            hint = f"paper/scripts/{match.group(1)}"
            if hint not in plot_script_hints:
                plot_script_hints.append(hint)
    readme_plot_refs = re.findall(
        r"(paper/scripts/[a-zA-Z0-9_]+\.py)",
        readme_text,
    )
    for ref in readme_plot_refs:
        if ref not in plot_script_hints:
            plot_script_hints.append(ref)
    return {
        "repo_root": str(repo_root.resolve()),
        "readme": {
            "path": "README.md" if readme_path.is_file() else "",
            "title_line": title_line,
            "headings": headings,
            "has_problem": "problem" in lower,
            "has_innovation": "innovation" in lower or "contribut" in lower,
        },
        "package": package,
        "configs": _collect_configs(repo_root),
        "paper": _collect_paper_assets(repo_root / "paper"),
        "literature": _collect_literature(repo_root / "paper" / "literature"),
        "tests": tests[:40],
        "plot_script_hints": plot_script_hints,
        "src_top_level": src_top,
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON path")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir():
        print(f"ERROR: not a directory: {repo_root}")
        return 1

    inventory = scan_repo(repo_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    print(
        f"  readme headings: {len(inventory['readme']['headings'])}, "
        f"configs: {len(inventory['configs'])}, "
        f"literature slugs: {len(inventory['literature']['slugs'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
