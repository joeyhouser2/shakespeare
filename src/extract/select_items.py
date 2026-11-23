"""Decide which extracted poems count as each author's own (controls, imposter pool).

Reads data/reference/text/tcp_poems.csv and writes data/reference/text/items.csv:
one row per poem in a relevant volume, with author class, role, include (1/0) and the reason.
Every exclusion is recorded, so the choices can be audited and changed here.

Rules (all decided before any scoring):
  - Each control collection lists the top-level TEI div types that hold the author's own verse.
  - Commendatory verse, plays, errata, Latin/Italian pieces (by function-word counts), and poems signed by someone
    else are excluded.
  - Anthologies: items are assigned by printed signature only.
  - Imposter pool: everything in the three anthologies except items signed by the target
    (Oxford), Shakespeare, or Stage 3 candidates, or matching an Oxford first line.
  - Duplicate witnesses: Gascoigne's 1573 Flowres is skipped in favour of his revised 1575 Posies.
  - Breton: the Bowre (1591) and Arbor (1597) carry no Breton signatures, and Breton disowned
    the Bowre, so Breton comes only from items signed "N. Breton." in Englands Helicon.

Usage: python src/extract/select_items.py
"""
import csv, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDX = ROOT / "data/reference/text/tcp_poems.csv"
MAN = ROOT / "data/reference/manifest.csv"
OUT = ROOT / "data/reference/text/items.csv"

# manifest item -> (TCP id, author class, allowed top-level div types or None for all)
COLLECTIONS = {
    "ctl-sid-as":  ("A12226", "Sidney", {"poem", "sonnets"}),       # excludes S. D. sonnets and 'cantos' by others
    "ctl-sid-arc": ("A12229", "Sidney", None),
    "ctl-gas-pos": ("A01514", "Gascoigne", {"poems", "poem", "fable", "argument"}),
    "ctl-goo":     ("A01909", "Googe", {"poem", "eclogue", "epitaph"}),
    "ctl-tur":     ("A14019", "Turberville", {"poem", "epilogue"}),
    "ctl-chu":     ("A18734", "Churchyard", None),
    "ctl-gre":     ("A02226", "Greville", {"sonnet_sequence"}),     # Caelica only; treatises and choruses differ in genre
    "ctl-spe-sc":  ("A12782", "Spenser", {"month"}),
    "ctl-spe-am":  ("A12772", "Spenser", {"sonnets", "epithalamium"}),
    "ctl-wat":     ("A14822", "Watson", {"part"}),
    "ctl-dan":     ("A19816", "Daniel", {"sonnet_sequence", "ode"}),
    "ctl-dra":     ("A20824", "Drayton", {"poem"}),
    "ctl-lod":     ("A06170", "Lodge", None),
}
SKIPPED_COLLECTIONS = {
    "ctl-gas-hsf": "duplicate witness: 1573 Flowres revised as 1575 Posies (ctl-gas-pos)",
    "ctl-bre-bow": "no Breton signatures; Breton disowned the Bowre; contains Oxford items",
    "ctl-bre-arb": "no Breton signatures; mixed authorship",
    "ctl-vau-tot": "Tottel prints Vaux unsigned among 'uncertain auctours'; needs a scholarly attribution list",
}
# anthology signature rules: (TCP id, author class, manifest item, regex on signature)
SIGNED = [
    ("A21161", "Vaux", "ctl-vau-par", r"^L\.\s*(V|Ʋ)"),
    ("A21161", "Edwards", "ctl-edw-par", r"^M[.,]?\s*Edward"),
    ("A16273", "Breton", "ctl-bre-hel", r"^N\.\s*Breton"),
    ("A16273", "Dyer", "ctl-dye", r"^S\.\s*E\.\s*D\.?$"),
]
IMPOSTER_VOLS = {"A11254": "imp-phx", "A16273": "imp-hel", "A19943": "imp-rap"}
# signatures that must never enter the imposter pool (target, comparison, Stage 3 candidates, ambiguous initials)
NOT_IMPOSTER = r"E\.\s*O\.|Ox|W\.\s*S\.|Shake|Marlo|Mary Count|Counte(s|ſ)(s|ſ)e of Pem"
EXCLUDE_DIVS = {"encomium", "encomia", "play", "act", "errata", "title_page", "dedication",
                "author_to_book", "argument_of_play", "dramatis_personae", "colophon"}
COMMENDATORY_HEAD = re.compile(r"(?i)to the author|in (the )?commendation|in praise of the author")
EN_FUNCTION = set("the and of to in that is my i a his her with not but for as be thy thou which me so all when by this".split())
FOREIGN_FUNCTION = set("et est quod non sit que nec quam te tu vt ut cum ad sed il che di per mi la las de del e chj ch amor".split())


def fold(s):
    s = unicodedata.normalize("NFKD", s).replace("ſ", "s").lower()
    s = re.sub(r"[^a-z ]", "", s).replace("vv", "w").replace("uu", "w").replace("v", "u").replace("j", "i")
    return re.sub(r"\s+", " ", s).strip()


def not_english(path):
    """Latin/Italian piece: English function words rare AND outnumbered by Latin/Italian ones."""
    words = re.findall(r"[a-zſèàò]+", (ROOT / path).read_text(encoding="utf-8").lower().replace("ſ", "s"))
    en = sum(w in EN_FUNCTION for w in words)
    fo = sum(w in FOREIGN_FUNCTION for w in words)
    return en / max(1, len(words)) < 0.12 and fo >= en


def generic_exclusion(p, author=None):
    top = p["div_path"].split("/")[0].split(":")[0]
    if top in EXCLUDE_DIVS:
        return f"div type '{top}'"
    if COMMENDATORY_HEAD.search(p["head"]):
        return "commendatory heading"
    if not_english(p["path"]):
        return "not English (Latin/Italian function words outnumber English)"
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    idx = list(csv.DictReader(open(IDX, encoding="utf-8")))
    oxford_first = [fold(r["title_or_first_line"])[:25] for r in csv.DictReader(open(MAN, encoding="utf-8"))
                    if r["author"] == "Oxford" and r["genre"] == "lyric"]
    rows = []
    def add(p, author, role, item, include, reason):
        rows.append(dict(poem_id=p["poem_id"], tcp_id=p["tcp_id"], author=author, role=role,
                         manifest_item=item, include=int(include), reason=reason,
                         n_lines=p["n_lines"], n_words=p["n_words"], signed=p["signed"],
                         first_line=p["first_line"], path=p["path"],
                         norm_path=p["path"].replace("data/reference/text/", "data/reference/text/norm/", 1)))

    for item, (tcp, author, allowed) in COLLECTIONS.items():
        for p in (x for x in idx if x["tcp_id"] == tcp):
            top = p["div_path"].split("/")[0].split(":")[0]
            why = generic_exclusion(p)
            if not why and allowed is not None and top not in allowed:
                why = f"div type '{top}' not in author's own sections"
            if not why and p["signed"] and author.lower()[:4] not in fold(p["signed"]) and re.search(
                    r"(?i)^(done by|[A-Z]\.\s*[A-Z][a-z]+\.?$)|Twine|Bucke|Acheley|Downhal|Roydon|Peele|Gorbo|Yeluert|Kinw", p["signed"]):
                why = f"signed by someone else: {p['signed']}"
            add(p, author, "control", item, why is None, why or "author's own section")

    for tcp, author, item, rx in SIGNED:
        for p in (x for x in idx if x["tcp_id"] == tcp):
            if re.search(rx, p["signed"].strip()):
                why = generic_exclusion(p)
                add(p, author, "control", item, why is None, why or f"signed '{p['signed']}'")

    for tcp, item in IMPOSTER_VOLS.items():
        for p in (x for x in idx if x["tcp_id"] == tcp):
            why = generic_exclusion(p)
            if not why and re.search(NOT_IMPOSTER, p["signed"]):
                why = f"signature excluded from pool: {p['signed']}"
            if not why and any(fold(p["first_line"]).startswith(f[:20]) for f in oxford_first):
                why = "matches an Oxford first line"
            add(p, "various", "imposter", item, why is None, why or "anthology item")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    from collections import defaultdict
    tot = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        k = (r["role"], r["author"])
        tot[k][0] += 1
        if r["include"]:
            tot[k][1] += 1; tot[k][2] += int(r["n_words"])
    print(f"{'role':9} {'author':12} {'seen':>5} {'kept':>5} {'words':>7}")
    for (role, a), (n, k, wds) in sorted(tot.items()):
        print(f"{role:9} {a:12} {n:5} {k:5} {wds:7}")
    for item, why in SKIPPED_COLLECTIONS.items():
        print(f"skipped {item}: {why}")


if __name__ == "__main__":
    main()
