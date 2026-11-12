#!/usr/bin/env python3
"""Mark revised LaTeX sentences in blue for IEEE resubmission track PDFs.

Compares a submitted baseline TeX file to a revised TeX file. Any sentence that
is not an exact match (after whitespace normalization) in the baseline is
wrapped with \\rev{...}. Unchanged sentences stay unmarked.

This deliberately marks whole sentences (not word-level diffs). Prefer this
over default latexdiff CFONT markup for journal "highlight changes" PDFs.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ABBREV_PROTECT = [
    (re.compile(r"\b(Fig|Figs|Eq|Eqs|Sec|Secs|Tab|Tabs|Ref|Refs|No|Nos|Vol|Vols|"
                r"et al|i\.e|e\.g|vs|etc|Dr|Mr|Mrs|Prof)\."),
     lambda m: m.group(0).replace(".", "\0")),
]

REV_USEPACKAGE = r"\usepackage{xcolor}"
REV_NEWCOMMAND = r"\newcommand{\rev}[1]{\textcolor{blue}{#1}}"


def _protect_abbreviations(text: str) -> str:
    out = text
    for rx, repl in ABBREV_PROTECT:
        out = rx.sub(repl, out)
    return out


def _unprotect_abbreviations(text: str) -> str:
    return text.replace("\0", ".")


def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def split_sentences(paragraph: str) -> list[str]:
    """Split a prose paragraph into sentences; keep LaTeX macros intact."""
    if not paragraph.strip():
        return []
    protected = _protect_abbreviations(paragraph)
    # Split on .?! followed by whitespace or end, not after \0-protected abbrev dots.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\$])", protected)
    out: list[str] = []
    for p in parts:
        p = _unprotect_abbreviations(p.strip())
        if p:
            out.append(p)
    if not out and paragraph.strip():
        out.append(paragraph.strip())
    return out


def is_structural_line(line: str) -> bool:
    s = line.lstrip()
    if not s or s.startswith("%"):
        return True
    # Whole-line TeX structure / floats - do not sentence-split these lines alone.
    # Note: \\item with trailing prose is handled separately (not structural).
    starters = (
        "\\documentclass",
        "\\usepackage",
        "\\begin{",
        "\\end{",
        "\\section",
        "\\subsection",
        "\\subsubsection",
        "\\paragraph",
        "\\caption",
        "\\label",
        "\\includegraphics",
        "\\bibliography",
        "\\bibliographystyle",
        "\\maketitle",
        "\\IEEEoverride",
        "\\thanks",
        "\\author",
        "\\title",
        "\\centering",
        "\\hline",
        "\\multicolumn",
        "\\renewcommand",
        "\\newcommand",
        "\\setcounter",
        "\\newlength",
        "\\setlength",
        "\\addtolength",
        "\\arraystretch",
        "\\vspace",
        "\\hspace",
        "\\noindent",
        "\\tiny",
        "\\scriptsize",
        "\\footnotesize",
        "\\small",
        "\\normalsize",
        "\\large",
        "\\Large",
    )
    # Bare \\item / \\item[...] with no trailing prose on this line.
    if s == "\\item" or re.fullmatch(r"\\item\[[^\]]*\]\s*", s):
        return True
    return any(s.startswith(x) for x in starters)


def item_prose_prefix(line: str) -> tuple[str, str] | None:
    """If line is ``\\item prose...``, return (\"\\\\item \", prose)."""
    s = line.lstrip()
    m = re.match(r"(\\item\s+)(.+)$", s)
    if not m:
        return None
    return m.group(1), m.group(2)


def is_markable_prose(sentence: str) -> bool:
    """Skip pure TeX commands / table knobs; keep real prose sentences."""
    s = sentence.strip()
    if len(_normalize_ws(s)) < 12:
        return False
    # Mostly a single control sequence with arguments, no prose letters outside.
    if re.fullmatch(r"\\[a-zA-Z]+\*?(\{[^}]*\}|\[[^\]]*\])*", s):
        return False
    letters = sum(c.isalpha() for c in s)
    backslashes = s.count("\\")
    if letters < 8:
        return False
    # Heavy-macro lines with almost no words
    words = re.findall(r"[A-Za-z]{3,}", s)
    if len(words) < 2 and backslashes >= 1:
        return False
    return True


def extract_sentences_from_tex(tex: str) -> set[str]:
    """Collect normalized sentences from non-structural prose lines."""
    found: set[str] = set()
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        para = " ".join(x.strip() for x in buf if x.strip())
        buf = []
        for sent in split_sentences(para):
            if not is_markable_prose(sent):
                continue
            found.add(_normalize_ws(sent))

    for line in tex.splitlines():
        ip = item_prose_prefix(line)
        if ip is not None:
            flush()
            _, prose = ip
            for sent in split_sentences(prose):
                if is_markable_prose(sent):
                    found.add(_normalize_ws(sent))
            continue
        if is_structural_line(line):
            flush()
            continue
        if not line.strip():
            flush()
            continue
        buf.append(line)
    flush()
    return found


def wrap_rev(sentence: str) -> str:
    # Avoid double-wrapping
    if sentence.lstrip().startswith("\\rev{"):
        return sentence
    return f"\\rev{{{sentence}}}"


def mark_paragraph(paragraph: str, baseline: set[str]) -> str:
    sents = split_sentences(paragraph)
    if not sents:
        return paragraph
    marked: list[str] = []
    for sent in sents:
        norm = _normalize_ws(sent)
        if (not is_markable_prose(sent)) or norm in baseline:
            marked.append(sent)
        else:
            marked.append(wrap_rev(sent))
    # Rejoin with space; original paragraph may have been multi-line
    return " ".join(marked)


SKIP_ENVS = (
    "tabular",
    "tabular*",
    "tabularx",
    "array",
    "eqnarray",
    "align",
    "align*",
    "equation",
    "equation*",
    "IEEEeqnarray",
    "verbatim",
    "lstlisting",
    "tikzpicture",
)


def transform_tex(old_tex: str, new_tex: str) -> str:
    baseline = extract_sentences_from_tex(old_tex)
    lines = new_tex.splitlines(keepends=True)
    out: list[str] = []
    buf: list[str] = []
    skip_depth = 0
    i = 0

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        raw = "".join(buf)
        # Preserve trailing newline pattern
        ends_nl = raw.endswith("\n")
        body = raw[:-1] if ends_nl and raw.endswith("\n") else raw
        # Multi-line paragraph as single prose block
        para = " ".join(line.strip() for line in body.splitlines() if line.strip())
        if para:
            marked = mark_paragraph(para, baseline)
            out.append(marked + ("\n" if ends_nl else ""))
        else:
            out.append(raw)
        buf = []

    begin_re = re.compile(r"\\begin\{([^}]+)\}")
    end_re = re.compile(r"\\end\{([^}]+)\}")

    while i < len(lines):
        line = lines[i]
        raw_line = line.rstrip("\n")

        # Pass through multi-line \\caption{...} intact (mark_captions wraps later).
        if r"\caption" in raw_line and skip_depth == 0:
            flush()
            chunk = [line]
            # Brace depth from this line onward until caption arg closes.
            brace = 0
            started = False
            for ch in raw_line:
                if ch == "{":
                    brace += 1
                    started = True
                elif ch == "}":
                    brace -= 1
            i += 1
            while started and brace > 0 and i < len(lines):
                chunk.append(lines[i])
                for ch in lines[i]:
                    if ch == "{":
                        brace += 1
                    elif ch == "}":
                        brace -= 1
                i += 1
            out.extend(chunk)
            continue

        # Track skip environments (do not mark table/math rows as prose).
        for m in begin_re.finditer(raw_line):
            if m.group(1) in SKIP_ENVS:
                skip_depth += 1
        if skip_depth > 0:
            flush()
            out.append(line)
            for m in end_re.finditer(raw_line):
                if m.group(1) in SKIP_ENVS and skip_depth > 0:
                    skip_depth -= 1
            i += 1
            continue

        ip = item_prose_prefix(raw_line)
        if ip is not None:
            flush()
            prefix, prose = ip
            marked_prose = mark_paragraph(prose, baseline)
            nl = "\n" if line.endswith("\n") else ""
            # keep original indent
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f"{indent}{prefix}{marked_prose}{nl}")
            i += 1
            continue
        if is_structural_line(raw_line) or not raw_line.strip():
            flush()
            out.append(line)
            i += 1
            continue
        buf.append(line)
        i += 1
    flush()
    return "".join(out)


def ensure_rev_macro(tex: str) -> str:
    if re.search(r"\\newcommand\{\\rev\}", tex) or re.search(
        r"\\renewcommand\{\\rev\}", tex
    ):
        # Still ensure xcolor
        if "xcolor" not in tex:
            tex = tex.replace(
                "\\documentclass",
                "\\documentclass",
                1,
            )
            tex = re.sub(
                r"(\\documentclass(?:\[[^\]]*\])?\{[^}]+\})",
                r"\1\n" + REV_USEPACKAGE + "\n",
                tex,
                count=1,
            )
        return tex

    inject = REV_USEPACKAGE + "\n" + REV_NEWCOMMAND + "\n"
    if re.search(r"\\usepackage\{xcolor\}", tex) or re.search(
        r"\\usepackage\[[^\]]*\]\{xcolor\}", tex
    ):
        inject = REV_NEWCOMMAND + "\n"
        tex = re.sub(
            r"(\\usepackage(?:\[[^\]]*\])?\{xcolor\})",
            r"\1\n" + REV_NEWCOMMAND,
            tex,
            count=1,
        )
        return tex

    m = re.search(r"(\\documentclass(?:\[[^\]]*\])?\{[^}]+\})", tex)
    if not m:
        return inject + tex
    return tex[: m.end()] + "\n" + inject + tex[m.end() :]


def _brace_arg_span(tex: str, open_brace: int) -> tuple[int, int] | None:
    """Return [inner_start, inner_end) for {...} starting at open_brace."""
    if open_brace >= len(tex) or tex[open_brace] != "{":
        return None
    depth = 0
    p = open_brace
    while p < len(tex):
        ch = tex[p]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return open_brace + 1, p
        p += 1
    return None


def _caption_bodies(tex: str) -> list[str]:
    """Extract \\caption arguments with simple brace matching."""
    bodies: list[str] = []
    i = 0
    while True:
        j = tex.find("\\caption", i)
        if j < 0:
            break
        k = tex.find("{", j)
        if k < 0:
            break
        span = _brace_arg_span(tex, k)
        if not span:
            break
        bodies.append(tex[span[0] : span[1]])
        i = span[1] + 1
    return bodies


def _strip_caption_from_block(block: str) -> str:
    j = block.find("\\caption")
    if j < 0:
        return _normalize_ws(block)
    k = block.find("{", j)
    if k < 0:
        return _normalize_ws(block)
    span = _brace_arg_span(block, k)
    if not span:
        return _normalize_ws(block)
    return _normalize_ws(block[:j] + block[span[1] + 1 :])


def _iter_floats(tex: str) -> list[dict]:
    """Parse figure/table floats with label, caption, graphics, body key."""
    floats: list[dict] = []
    for m in re.finditer(
        r"\\begin\{(figure\*?|table\*?)\}(.*?)\\end\{\1\}",
        tex,
        re.S,
    ):
        kind, block = m.group(1), m.group(2)
        cap_body = None
        cap_m = re.search(r"\\caption\s*\{", block)
        if cap_m:
            k = block.find("{", cap_m.start())
            span = _brace_arg_span(block, k) if k >= 0 else None
            if span:
                cap_body = block[span[0] : span[1]]
        lab_m = re.search(r"\\label\{([^}]+)\}", block)
        label = lab_m.group(1) if lab_m else None
        figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", block)
        floats.append(
            {
                "kind": kind,
                "label": label,
                "caption": cap_body,
                "figs": figs,
                "body_key": _strip_caption_from_block(block),
            }
        )
    return floats


def _file_digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_blob_digest(repo: Path, rev: str, rel: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", f"{rev}:{rel}"],
            check=False,
            capture_output=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return hashlib.sha256(proc.stdout).hexdigest()


def _assets_changed(
    figs: list[str],
    *,
    new_root: Path | None,
    old_root: Path | None,
    git_repo: Path | None,
    git_old: str | None,
) -> bool:
    """Return True only when both baseline and revised digests exist and differ.

    If the baseline asset cannot be read (no ``old_root`` / ``git-old`` blob),
    skip that file rather than treating a missing baseline as a change. Otherwise
    ``--asset-root`` alone spuriously blues every figure caption.
    """
    if not figs:
        return False
    for rel in figs:
        new_dig = _file_digest(new_root / rel) if new_root else None
        old_dig = None
        if old_root is not None:
            old_dig = _file_digest(old_root / rel)
        if old_dig is None and git_repo is not None and git_old:
            old_dig = _git_blob_digest(git_repo, git_old, rel)
        if new_dig is None or old_dig is None:
            continue
        if new_dig != old_dig:
            return True
    return False


def captions_to_mark(
    old_tex: str,
    new_tex: str,
    *,
    new_root: Path | None = None,
    old_root: Path | None = None,
    git_repo: Path | None = None,
    git_old: str | None = None,
) -> set[str]:
    """Return normalized caption bodies in new_tex that should be \\rev-wrapped.

    Mark when caption text changed, float body (table/figure TeX) changed, or
    any \\includegraphics asset differs vs baseline (old-asset-root or git).
    """
    old_floats = _iter_floats(old_tex)
    new_floats = _iter_floats(new_tex)
    old_by_label = {f["label"]: f for f in old_floats if f["label"]}
    mark_bodies: set[str] = set()

    for idx, nf in enumerate(new_floats):
        if not nf["caption"]:
            continue
        of = old_by_label.get(nf["label"]) if nf["label"] else None
        if of is None and idx < len(old_floats):
            # Fallback: same ordinal when labels missing/renamed.
            of = old_floats[idx]

        need = False
        if of is None:
            need = True
        else:
            if _normalize_ws(nf["caption"]) != _normalize_ws(of["caption"] or ""):
                need = True
            elif nf["body_key"] != of["body_key"]:
                need = True
            elif _assets_changed(
                nf["figs"],
                new_root=new_root,
                old_root=old_root,
                git_repo=git_repo,
                git_old=git_old,
            ):
                need = True
        if need:
            mark_bodies.add(_normalize_ws(nf["caption"]))

    # Also mark lone caption-text changes not tied to a parseable float match.
    old_caps = {_normalize_ws(b) for b in _caption_bodies(old_tex)}
    for body in _caption_bodies(new_tex):
        nb = _normalize_ws(body)
        if nb not in old_caps:
            mark_bodies.add(nb)
    return mark_bodies


def apply_caption_marks(tex: str, to_mark: set[str]) -> str:
    """Wrap \\caption bodies whose normalized text is in to_mark."""
    out: list[str] = []
    i = 0
    while True:
        j = tex.find("\\caption", i)
        if j < 0:
            out.append(tex[i:])
            break
        out.append(tex[i:j])
        k = tex.find("{", j)
        if k < 0:
            out.append(tex[j:])
            break
        span = _brace_arg_span(tex, k)
        if not span:
            out.append(tex[j:])
            break
        body = tex[span[0] : span[1]]
        if _normalize_ws(body) in to_mark and not body.lstrip().startswith("\\rev{"):
            out.append("\\caption{\\rev{" + body + "}}")
        else:
            out.append(tex[j : span[1] + 1])
        i = span[1] + 1
    return "".join(out)


def mark_captions(
    old_tex: str,
    new_tex: str,
    *,
    new_root: Path | None = None,
    old_root: Path | None = None,
    git_repo: Path | None = None,
    git_old: str | None = None,
    decision_tex: str | None = None,
) -> str:
    """Wrap float captions in \\rev when the float or its assets changed.

    ``decision_tex`` should be the clean revised manuscript (no \\rev yet) so
    float/body matching is stable; marks are then applied onto ``new_tex``
    (which may already have sentence-level \\rev).
    """
    to_mark = captions_to_mark(
        old_tex,
        decision_tex if decision_tex is not None else new_tex,
        new_root=new_root,
        old_root=old_root,
        git_repo=git_repo,
        git_old=git_old,
    )
    return apply_caption_marks(new_tex, to_mark)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old", required=True, type=Path, help="Submitted baseline .tex")
    ap.add_argument("--new", required=True, type=Path, help="Revised .tex")
    ap.add_argument("--out", required=True, type=Path, help="Output tracked .tex")
    ap.add_argument(
        "--asset-root",
        type=Path,
        default=None,
        help="Root for revised \\includegraphics paths (default: parent of --new)",
    )
    ap.add_argument(
        "--old-asset-root",
        type=Path,
        default=None,
        help="Root for baseline figure/table assets (optional)",
    )
    ap.add_argument(
        "--git-repo",
        type=Path,
        default=None,
        help="Git repo used to read baseline assets via --git-old",
    )
    ap.add_argument(
        "--git-old",
        type=str,
        default=None,
        help="Git revision for baseline assets (e.g. submitted commit)",
    )
    args = ap.parse_args()

    old_tex = args.old.read_text(encoding="utf-8")
    new_tex = args.new.read_text(encoding="utf-8")
    new_root = args.asset_root or args.new.parent
    git_repo = args.git_repo
    if git_repo is None and args.git_old:
        git_repo = new_root

    marked = transform_tex(old_tex, new_tex)
    marked = mark_captions(
        old_tex,
        marked,
        new_root=new_root,
        old_root=args.old_asset_root,
        git_repo=git_repo,
        git_old=args.git_old,
        decision_tex=new_tex,
    )
    marked = ensure_rev_macro(marked)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(marked, encoding="utf-8")

    base = extract_sentences_from_tex(old_tex)
    new_sents = extract_sentences_from_tex(new_tex)
    changed = sorted(s for s in new_sents if s not in base)
    cap_n = sum(
        1
        for b in _caption_bodies(marked)
        if b.lstrip().startswith("\\rev{")
    )
    print(
        f"wrote {args.out}  "
        f"(baseline_sentences={len(base)} revised={len(new_sents)} "
        f"marked≈{len(changed)} captions_rev={cap_n})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
