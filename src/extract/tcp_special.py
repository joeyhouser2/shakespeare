"""One-off extractions from TCP files that the verse extractor can't handle.

1. Oxford's prose letter to Thomas Bedingfield, prefixed to Cardanus Comforte (1573, TCP A17947):
   the front-matter <div> whose <signed> contains "Oxenford". Paragraphs joined, original spelling.
2. "Were I a king" from John Mundy, Songs and Psalmes (1594, TCP A07912), song XXVI.
   The print is musical underlay with repeats ("ij.", repeated phrases), so the six verse lines are
   an EDITORIAL reconstruction from the SVPERIVS part: repeats removed, lineation by rhyme,
   spelling as printed in that part. See RECONSTRUCTED below; check it against the TCP text.

Output: data/reference/text/special/  (separate from the automatic extraction in text/orig/)
Usage: python src/extract/tcp_special.py
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/reference/raw/tcp"
OUT = ROOT / "data/reference/text/special"


SUP = dict(zip("abcdefghijklmnoprstuvwxyz0123456789", "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"))


def superscript(s):
    """Superscript letters as Unicode modifier letters (yᵉ, yᵗ, wᵗ); anything else as ^x (e.g. y^• = illegible)."""
    return "".join(SUP.get(c, c if c.isspace() else "^" + c) for c in s)


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def flat(el):
    parts = []
    def walk(e):
        t = local(e.tag)
        if t in ("note", "pb", "figure"):
            pass
        elif t == "gap":
            d = next((x.text for x in e if local(x.tag) == "desc" and x.text), "〈?〉")
            parts.append(d.strip())
        elif t == "g" and e.get("ref") == "char:EOLhyphen":
            parts.append("\u0000")
        elif t == "hi" and e.get("rend") == "sup" and e is not el:
            parts.append(superscript(flat(e)))
        else:
            parts.append(e.text or "")
            for c in e:
                walk(c)
        if e is not el:
            parts.append(e.tail or "")
    walk(el)
    s = re.sub(r"\s*\u0000\s*", "", "".join(parts))
    return re.sub(r"\s+", " ", s).strip()


def bedingfield_letter():
    root = ET.parse(RAW / "A17947.xml").getroot()
    for div in root.iter():
        if local(div.tag) != "div":
            continue
        signed = [flat(s) for s in div.iter() if local(s.tag) == "signed"]
        if any("Oxenford" in s for s in signed) and any(local(p.tag) == "p" for p in div.iter()):
            paras = [flat(p) for p in div.iter() if local(p.tag) == "p"]
            opener = [flat(o) for o in div if local(o.tag) in ("head", "opener")]
            text = "\n\n".join(opener + paras + signed) + "\n"
            (OUT / "A17947_oxford_letter.txt").write_text(text, encoding="utf-8")
            return len(" ".join(paras).split())
    raise SystemExit("Oxford letter not found in A17947")


# Editorial reconstruction from Mundy 1594 song XXVI, SVPERIVS part (repeats removed).
RECONSTRUCTED = """WEre I a king, I might commaund content,
were I obscure, vnknowne should bee my cares,
and were I dead, no thoughts should mee torment,
nor words, nor wrongs, nor loues, nor hopes, nor feares,
a doubtfull choice of three things one to craue,
a kingdome, or a cottage, or a graue.
"""


def mundy():
    raw = (RAW / "A07912.xml").read_text(encoding="utf-8")
    m = re.search(r'<div n="27" type="song">(.*?)</div>', raw, re.S)
    if not m or "SVPERIVS" not in m.group(1) or "commaund content" not in m.group(1):
        raise SystemExit("Mundy song XXVI SVPERIVS not where expected; recheck before using reconstruction")
    # every word of the reconstruction must occur in the printed part
    part = re.sub(r"<[^>]+>", " ", m.group(1)).lower()
    missing = [w for w in re.findall(r"[a-zſ]+", RECONSTRUCTED.lower()) if w not in part]
    if missing:
        raise SystemExit(f"reconstruction words not in source part: {missing}")
    (OUT / "A07912_026_were_i_a_king_EDITORIAL.txt").write_text(RECONSTRUCTED, encoding="utf-8")
    return len(RECONSTRUCTED.split())


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("Bedingfield letter words:", bedingfield_letter())
    print("Mundy reconstruction words:", mundy())
