"""Extract the Folger Shakespeare XML (modern-spelling edition) for use as a cross-check.

Folger XML marks each verse line with <milestone unit="line"/> followed by <w>/<c>/<pc> tokens.
Sonnets are <div2 n="1".."154">; the other poems are one text each.

Output: data/reference/text/folger/<Work>_<nnn>.txt  (one per sonnet; Ven/Luc/PhT one file each)
        data/reference/text/folger/folger_poems.csv  index: id, work, n, first_line, n_lines, path
Licence: Folger Digital Texts, CC BY-NC 3.0 (credit Folger Digital Texts, link the licence, note changes).

Usage: python src/extract/folger_verse.py
"""
import csv, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/reference/raw/folger"
OUT = ROOT / "data/reference/text/folger"
WORKS = ["Son", "Ven", "Luc", "PhT"]


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def lines_of(el):
    lines, cur = [], None
    for e in el.iter():
        t = local(e.tag)
        if t == "milestone" and e.get("unit") == "line":
            if cur is not None:
                lines.append("".join(cur).strip())
            cur = []
        elif t in ("w", "c", "pc") and cur is not None:
            cur.append(e.text or "")
    if cur:
        lines.append("".join(cur).strip())
    return [l for l in lines if l]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for w in WORKS:
        xml = next(p for p in RAW.rglob(f"{w}.xml") if "MACOSX" not in str(p))
        root = ET.parse(xml).getroot()
        body = next(e for e in root.iter() if local(e.tag) == "body")
        units = [(int(d.get("n")), d) for d in body.iter() if local(d.tag) == "div2" and d.get("n", "").isdigit()] if w == "Son" else [(1, body)]
        for n, el in units:
            ls = lines_of(el)
            pid = f"{w}_{n:03d}"
            path = OUT / f"{pid}.txt"
            path.write_text("\n".join(ls) + "\n", encoding="utf-8")
            rows.append(dict(id=pid, work=w, n=n, first_line=ls[0] if ls else "", n_lines=len(ls),
                             path=path.relative_to(ROOT).as_posix()))
        print(w, len(units), "units")
    with open(OUT / "folger_poems.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)


if __name__ == "__main__":
    main()
