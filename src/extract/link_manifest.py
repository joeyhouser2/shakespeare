"""Link manifest rows to extracted TCP poem texts.

- Oxford poems: find the TCP poem whose first line matches (after folding long s, u/v, i/j,
  case and punctuation) inside the expected TCP volume, and fill orig_text_path,
  line_count and word_count. The match must also start with the same first word.
- Single-author control collections: point orig_text_path at the TCP folder.
- Anthology rows (Vaux, Edwards, Breton, imposters) stay unlinked until items are
  filtered by signature.

Usage: python src/extract/link_manifest.py
"""
import csv, re, sys, unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAN = ROOT / "data/reference/manifest.csv"
IDX = ROOT / "data/reference/text/tcp_poems.csv"

# item_id -> (TCP volume to search, expected first-line text). First edition preferred.
OXFORD = {
    "oxf-p-02": ("A21161", "Even as the waxe doeth melt"),
    "oxf-p-03": ("A21161", "A Croune of Bayes shall that man weare"),
    "oxf-p-04": ("A21161", "Fraud is the front of Fortune past all recouerie"),
    "oxf-p-05": ("A21161", "I Am not as seme to bee"),
    "oxf-p-06": ("A21161", "If care or skill could conquere vaine desire"),
    "oxf-p-07": ("A21161", "My meanyng is to worke what wondes loue hath"),
    "oxf-p-08": ("A21161", "The liuely Larke did stretche her wyng"),
    "oxf-p-09": ("A21161", "The tricklyng teares that fales along my cheeks"),
    "oxf-p-11": ("A16731", "When wert thou born Desire"),
    "oxf-p-14": ("A11254", "What cunnnig can expresse"),
    "oxf-p-III": ("A16731", "If women would be faire and yet not fond"),
}
EXTRA_NOTES = {
    "oxf-p-04": "TCP 1576 text reads 'Fraud is the front of Fortune'; 1585 ed. (A21166) reads 'Fram'd in the front of forlorne hope' as May",
    "oxf-p-05": "1576 TCP signed 'E. O.'; 1585 ed. (A21166) signed 'E.Ox.' - weighs against the Essex cross-reference",
    "oxf-p-06": "1576 TCP signed 'M.B.'; 1585 ed. (A21166) signed 'E.O.' - attribution conflict in print",
    "oxf-p-07": "TCP 1576 reads 'what wondes loue hath wrought' (May: 'wonders')",
    "oxf-p-14": "Phoenix Nest TCP typo 'cunnnig'; Englands Helicon 1600 copy also extracted, signed 'Earle of Oxenford.'",
    "oxf-p-III": "Bowre 1591 copy unsigned and reads 'would be faire'",
}
SINGLE_AUTHOR = {"ctl-sid-as": "A12226", "ctl-sid-arc": "A12229", "ctl-gas-hsf": "A01513",
                 "ctl-gas-pos": "A01514", "ctl-goo": "A01909", "ctl-tur": "A14019", "ctl-chu": "A18734",
                 "ctl-gre": "A02226", "ctl-spe-sc": "A12782", "ctl-spe-am": "A12772", "ctl-wat": "A14822",
                 "ctl-dan": "A19816", "ctl-dra": "A20824", "ctl-lod": "A06170"}


def fold(s):
    s = unicodedata.normalize("NFKD", s).replace("ſ", "s").lower()
    s = re.sub(r"[^a-z ]", "", s).replace("vv", "w").replace("uu", "w").replace("v", "u").replace("j", "i")
    return re.sub(r"\s+", " ", s).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    idx = list(csv.DictReader(open(IDX, encoding="utf-8")))
    with open(MAN, encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)
    for r in rows:
        iid = r["item_id"]
        if iid in OXFORD:
            vol, fl = OXFORD[iid]
            target = fold(fl)
            cands = [p for p in idx if p["tcp_id"] == vol]
            score, best = max(((SequenceMatcher(None, target, fold(p["first_line"])[:len(target)]).ratio(), p)
                               for p in cands), key=lambda t: t[0])
            if score < 0.9 or fold(best["first_line"]).split()[0] != target.split()[0]:
                print(f"{iid}: NO CONFIDENT MATCH (best {score:.2f} {best['poem_id']})"); continue
            r["orig_text_path"] = best["path"]
            r["line_count"] = best["n_lines"]; r["word_count"] = best["n_words"]
            add = f"text: TCP {best['poem_id']} (signed '{best['signed']}', match {score:.2f})"
            if iid in EXTRA_NOTES:
                add += "; " + EXTRA_NOTES[iid]
            if "text: TCP" not in r["notes"]:
                r["notes"] = (r["notes"] + "; " + add).strip("; ")
            print(f"{iid}: {best['poem_id']} {score:.2f} signed={best['signed']!r} lines={best['n_lines']}")
        elif iid in SINGLE_AUTHOR:
            t = SINGLE_AUTHOR[iid]
            ps = [p for p in idx if p["tcp_id"] == t]
            r["orig_text_path"] = f"data/reference/text/orig/{t}/"
            r["line_count"] = str(sum(int(p["n_lines"]) for p in ps))
            r["word_count"] = str(sum(int(p["n_words"]) for p in ps))
    with open(MAN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
