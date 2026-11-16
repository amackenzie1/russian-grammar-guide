# /// script
# requires-python = ">=3.10"
# ///
"""Lint section files: stress marks, block syntax, cross-reference ids.

Usage: uv run tools/lint.py [paths...]   (default: parts/)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACUTE = "́"
VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
# A run of Cyrillic letters / acutes, with any hyphens attached (so "-ого" and "при-" are seen whole).
WORD = re.compile(r"-?[А-Яа-яЁё́]+(?:-[А-Яа-яЁё́]+)*-?")
KINDS = {"ex", "vocab", "dialogue", "note", "warn", "aside", "summary", "cursive", "keyboard", "figure"}
UNMARKED = {"cursive", "keyboard"}  # shown as real-world text, without stress marks
NS = re.compile(r"\[\[ns:(.*?)\]\]", re.S)
LINK = re.compile(r"\]\(#(s-\d\d-\d\d)\)")


def section_ids():
    ids = set()
    for d in sorted((ROOT / "parts").iterdir()):
        if d.is_dir():
            for f in sorted(d.glob("*.md")):
                ids.add(f"s-{d.name[:2]}-{f.name[:2]}")
    return ids


def check_word(w):
    """Return a problem string or None for one hyphen-free Cyrillic chunk."""
    n_vowels = sum(1 for c in w if c in VOWELS)
    n_marks = w.count(ACUTE)
    has_yo = "ё" in w or "Ё" in w
    if n_marks > 1:
        return "two stress marks"
    if n_marks == 1:
        i = w.index(ACUTE)
        if i == 0 or w[i - 1] not in VOWELS:
            return "stress mark not after a vowel"
        if w[i - 1] in "ёЁ":
            return "stress mark on ё"
        if n_vowels == 1:
            return "stress mark on one-syllable word"
        if has_yo:
            return "both ё and a stress mark"
        return None
    if n_vowels >= 2 and not has_yo:
        return "no stress mark"
    return None


def lint_file(path, ids):
    problems = []
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or not lines[0].startswith("# "):
        problems.append((1, "first line must be '# Title'"))
    open_block = None
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith(":::"):
            if s == ":::":
                if open_block is None:
                    problems.append((n, "':::' closes nothing"))
                open_block = None
            else:
                kind = s[3:].split()[0]
                if open_block is not None:
                    problems.append((n, f"block '{kind}' opened inside unclosed '{open_block[0]}' (line {open_block[1]})"))
                if kind not in KINDS:
                    problems.append((n, f"unknown block kind '{kind}'"))
                open_block = (kind, n)
            continue
        if open_block and open_block[0] in ("ex", "vocab", "dialogue") and s:
            parts = s.split(" | ")
            if len(parts) < 2 or len(parts) > 3:
                problems.append((n, f"'{open_block[0]}' line needs 2-3 fields separated by ' | '"))
        if n > 1 and re.match(r"#\s", line):
            problems.append((n, "only one '# ' title per file; use ## / ###"))
        if open_block and open_block[0] == "keyboard":
            continue
        if "<" in line and re.search(r"</?[a-zA-Z][^>]*>", line):
            problems.append((n, "raw HTML is not allowed"))
        for m in LINK.finditer(line):
            if m.group(1) not in ids:
                problems.append((n, f"link target {m.group(1)} does not exist (yet)"))
        # drop emphasis markers so кни́г**ами** is read as one word
        if open_block and open_block[0] in UNMARKED:
            continue
        checked = NS.sub("", line).replace("*", "")
        for m in WORD.finditer(checked):
            tok = m.group(0)
            chunks = tok.strip("-").split("-")
            # bare affixes such as "-ого" or "при-" need no stress mark
            if (tok.startswith("-") or tok.endswith("-")) and len(chunks) == 1:
                continue
            for chunk in chunks:
                p = check_word(chunk)
                if p:
                    problems.append((n, f"{p}: {chunk}"))
    if open_block is not None:
        problems.append((open_block[1], f"block '{open_block[0]}' never closed"))
    return problems, len(re.findall(r"\S+", text))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or [ROOT / "parts"]
    files = []
    for t in targets:
        t = t if t.is_absolute() else (Path.cwd() / t)
        files += sorted(t.rglob("*.md")) if t.is_dir() else [t]
    ids = section_ids()
    total = 0
    words = 0
    for f in files:
        problems, wc = lint_file(f, ids)
        words += wc
        rel = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
        print(f"{rel}: {wc} words, {len(problems)} problem(s)")
        for n, p in problems:
            print(f"  line {n}: {p}")
        total += len(problems)
    print(f"\n{len(files)} file(s), {words} words, {total} problem(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
