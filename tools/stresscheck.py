# /// script
# requires-python = ">=3.10"
# ///
"""Cross-check every stress mark in parts/ against the OpenRussian dictionary CSVs.

Usage: python3 -I tools/stresscheck.py <dir with nouns.csv verbs.csv adjectives.csv others.csv> [path filters...]

The CSVs come from https://github.com/Badestrand/russian-dictionary (stress shown as ' after the
vowel). A flagged word is not necessarily wrong: the dictionary has gaps and lists one variant
where the norm allows two. Review the output by hand.
"""
import collections
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)
ROOT = Path(__file__).resolve().parent.parent
AC = "́"
VOW = "аеёиоуыэюя"
NONFORM = {"bare", "gender", "partner", "aspect", "animate", "indeclinable", "sg_only", "pl_only"}


def load(dictdir):
    known = collections.defaultdict(set)

    def add(form):
        for tok in re.split(r"[\s,;/()]+", form):
            tok = tok.strip().lower()
            if not tok or not re.fullmatch(r"[а-яё'\-]+", tok):
                continue
            for part in tok.split("-"):
                bare = part.replace("'", "")
                if sum(c in VOW for c in bare) < 2:
                    continue
                if "'" in part:
                    pos = part.index("'") - 1
                elif "ё" in part:
                    pos = part.index("ё")
                else:
                    continue
                known[bare.replace("ё", "е")].add(pos)

    for f in Path(dictdir).glob("*.csv"):
        with open(f, encoding="utf-8", newline="") as fh:
            r = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
            hdr = next(r)
            skip = {i for i, h in enumerate(hdr) if h.startswith("translations") or h in NONFORM}
            for row in r:
                for i, cell in enumerate(row):
                    if i not in skip and cell:
                        add(cell)
    return known


def main():
    known = load(sys.argv[1])
    only = sys.argv[2:]
    word = re.compile(r"[А-Яа-яЁё́]+")
    flags = collections.defaultdict(list)
    unknown = set()
    n = 0
    for f in sorted((ROOT / "parts").rglob("*.md")):
        if only and not any(o in str(f) for o in only):
            continue
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            line = re.sub(r"\[\[ns:.*?\]\]", "", line).replace("*", "")
            for m in word.finditer(line):
                w = m.group(0).lower()
                if AC in w:
                    pos = w.index(AC) - 1
                    bare = w.replace(AC, "")
                elif "ё" in w and sum(c in VOW for c in w) >= 2:
                    pos = w.index("ё")
                    bare = w
                else:
                    continue
                n += 1
                key = bare.replace("ё", "е")
                if key not in known:
                    unknown.add(bare)
                    continue
                if pos not in known[key]:
                    flags[(w, tuple(sorted(known[key])))].append(f"{f.parent.name[:2]}-{f.name[:2]}:{ln}")
    print(f"checked {n} stressed tokens; {len(flags)} flagged forms; {len(unknown)} forms not in dictionary")
    for (w, exp), locs in sorted(flags.items()):
        key = w.replace(AC, "")
        alts = ", ".join(key[: p + 1] + AC + key[p + 1 :] if key[p] != "ё" else key for p in exp)
        print(f"{w}  (dict: {alts})  x{len(locs)}  {' '.join(locs[:4])}")


if __name__ == "__main__":
    main()
