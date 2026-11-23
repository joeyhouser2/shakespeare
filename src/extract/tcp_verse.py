"""Extract verse from EEBO-TCP TEI files into one original-spelling text file per poem.

A "poem" is a leaf <div> (one with no child <div>) that contains verse lines (<l>),
split further wherever a <head> follows verse (sonnet sequences encode each sonnet that way),
or a stanza after verse opens with a TCP drop-cap word ("VVHat", "FRaud"); such splits are flagged split=dropcap.
Raw XML in data/reference/raw/tcp is read only, never modified.

Output:
  data/reference/text/orig/<TCP>/<TCP>_<nnn>.txt   one verse line per line, blank line between stanzas
  data/reference/text/tcp_poems.csv                index: heading, signature, first line, counts, path

Text rules (original-spelling layer; see data/reference/NORMALIZATION.md for the normalized layer):
  - characters kept exactly as TCP gives them (long s, u/v, i/j, abbreviation marks, superscripts as Unicode modifier letters: "yᵗ", "yᵉ"; unmappable as "^x")
  - TCP's soft line wraps inside an <l> collapsed to single spaces
  - end-of-line hyphen glyphs (char:EOLhyphen) removed so the word joins up
  - <gap> (illegible/missing) becomes TCP's placeholder ("•" per letter, "〈◊〉" per word; "〈?〉" if none) and is counted
  - <note>, <speaker>, <figure>, <pb>, <head>, <trailer>, <closer> excluded from the verse text
    (heading and signature are stored in the index instead)

Usage: python src/extract/tcp_verse.py
"""
import csv, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/reference/raw/tcp"
OUT = ROOT / "data/reference/text/orig"
INDEX = ROOT / "data/reference/text/tcp_poems.csv"

SKIP = {"note", "speaker", "figure", "pb", "head", "trailer", "closer", "signed", "label", "milestone", "fw"}
GAP = "〈?〉"
DROPCAP = re.compile(r"^((VV|UU)[A-Z]|(?!VV|UU)[A-Z][A-Z])[a-zſ']")  # VV/UU alone = W
NO_DROPCAP_SPLIT = {"epithalamium"}  # single long poems whose stanzas each open with a drop cap


SUP = dict(zip("abcdefghijklmnoprstuvwxyz0123456789", "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"))


def superscript(s):
    """Superscript letters as Unicode modifier letters (yᵉ, yᵗ, wᵗ); anything else as ^x (e.g. y^• = illegible)."""
    return "".join(SUP.get(c, c if c.isspace() else "^" + c) for c in s)


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def text_of(el, counter):
    """Flatten an element to text, applying the rules above."""
    parts = []
    def walk(e):
        t = local(e.tag)
        if t in SKIP and e is not el:
            pass
        elif t == "gap":
            # TCP's own placeholder: "•" per illegible letter, "〈◊〉" per word; keeps damaged words whole
            desc = next((d.text for d in e if local(d.tag) == "desc" and d.text), None)
            parts.append(desc.strip() if desc else GAP); counter["gaps"] += 1
        elif t == "g" and e.get("ref") == "char:EOLhyphen":
            parts.append("\u0000")  # join marker, removed with surrounding whitespace
        elif t == "hi" and e.get("rend") == "sup" and e is not el:
            parts.append(superscript(text_of(e, counter)))
        else:
            if e.text:
                parts.append(e.text)
            for c in e:
                walk(c)
        if e.tail and e is not el:
            parts.append(e.tail)
    walk(el)
    s = "".join(parts)
    s = re.sub(r"\s*\u0000\s*", "", s)
    return re.sub(r"\s+", " ", s).strip()


def plain(el):
    return text_of(el, {"gaps": 0}) if el is not None else ""


def leaf_divs(body):
    for d in body.iter():
        if local(d.tag) == "div" and not any(local(c.tag) == "div" for c in d):
            if any(local(x.tag) == "l" for x in d.iter()):
                yield d


def units(div):
    """Split a leaf div into poems. Walk in document order; a <head> that comes after
    verse lines starts a new poem (sonnet sequences put each sonnet's head inside one div).
    Lines are grouped into stanzas by their nearest <lg>. <signed> attaches to the current poem."""
    parent = {c: p for p in div.iter() for c in p}
    out = []
    def new():
        return {"head": "", "signed": [], "groups": [], "cur": [], "key": None, "gaps": {"gaps": 0}, "split": ""}
    u = new()
    def flush(u):
        if u["cur"]:
            u["groups"].append(u["cur"]); u["cur"] = []
    for el in div.iter():
        t = local(el.tag)
        if t not in ("l", "head", "signed"):
            continue
        p, key, skip = parent.get(el), None, False
        while p is not None and p is not div:
            if local(p.tag) in SKIP and not (t == "signed" and local(p.tag) in ("closer", "trailer")):
                skip = True
            if key is None and local(p.tag) == "lg":
                key = id(p)
            p = parent.get(p)
        if skip:
            continue
        if t == "head":
            if u["groups"] or u["cur"]:
                flush(u); out.append(u); u = new()
            u["head"] = (u["head"] + " " + plain(el)).strip()
        elif t == "signed":
            u["signed"].append(plain(el))
        else:
            line = text_of(el, u["gaps"])
            if key != u["key"]:
                flush(u)
                # TCP types a poem's decorated initial as two capitals ("VVHat", "FRaud").
                # A stanza opening that way after verse = an unmarked new poem in the same div.
                if u["groups"] and DROPCAP.match(line) and div.get("type") not in NO_DROPCAP_SPLIT:
                    out.append(u); u = new(); u["split"] = "dropcap"
            u["key"] = key
            if line:
                u["cur"].append(line)
    flush(u)
    out.append(u)
    return [x for x in out if x["groups"]]


def div_path(div, parent):
    bits, d = [], div
    while d is not None and local(d.tag) == "div":
        bits.append(f'{d.get("type", "?")}{":" + d.get("n") if d.get("n") else ""}')
        d = parent.get(d)
    return "/".join(reversed(bits))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for xml in sorted(RAW.glob("A*.xml")):
        tcp = xml.stem
        root = ET.parse(xml).getroot()
        text_el = next((e for e in root.iter() if local(e.tag) == "text"), None)
        parent = {c: p for p in text_el.iter() for c in p}
        outdir = OUT / tcp
        outdir.mkdir(parents=True, exist_ok=True)
        n = 0
        for div in leaf_divs(text_el):
            for u in units(div):
                groups = u["groups"]
                lines = [l for g in groups for l in g]
                n += 1
                pid = f"{tcp}_{n:03d}"
                path = outdir / f"{pid}.txt"
                path.write_text("\n\n".join("\n".join(g) for g in groups) + "\n", encoding="utf-8")
                rows.append(dict(
                    poem_id=pid, tcp_id=tcp, div_path=div_path(div, parent),
                    head=u["head"], signed=" | ".join(u["signed"]), first_line=lines[0],
                    n_lines=len(lines), n_words=sum(len(l.split()) for l in lines),
                    n_gaps=u["gaps"]["gaps"], split=u["split"], path=path.relative_to(ROOT).as_posix()))
        print(f"{tcp}: {n} poems")
    with open(INDEX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} poems -> {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
