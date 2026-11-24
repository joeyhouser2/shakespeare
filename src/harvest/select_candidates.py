"""Select Stage 1 candidates from the candidate-source volumes (src/harvest/PLAN_candidates.md).

A poem is a candidate if, in every witness found:
  - its signature (or, failing that, an author named in its heading as initials or a titled name, or
    the Poetical Rapsody section attribution) is absent, initials only, a pseudonym, or Oxford-related
  - no witness names a non-Oxford author, and no witness carries initials of a control author
    or Shakespeare (KNOWN_INITIALS)
  - it is not an Oxford reference poem (fuzzy first-line match, ratio >= 0.8) and not a Shakespeare text
  - it is English and not commendatory/dramatic (same filters as src/extract/select_items.py)
Witnesses = all extracted poems (every TCP volume plus songbooks) whose first line matches
after folding spelling. One candidate per poem; earliest witness is the text used.
Candidates under 100 tokens are listed but marked scorable = 0.

Writes data/candidates/manifest.csv (keeps the hand-entered Englands Parnassus rows) and
data/candidates/selection_log.csv (every poem considered, with the decision and reason).

Usage: python src/harvest/select_candidates.py
"""
import csv, re, sys, unicodedata
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/score"))
sys.path.insert(0, str(ROOT / "src/extract"))
import corpus as C                                         # noqa: E402
from select_items import generic_exclusion, fold           # noqa: E402

SOURCES = ROOT / "data/candidates/tcp_sources.csv"
OUT = ROOT / "data/candidates/manifest.csv"
LOG = ROOT / "data/candidates/selection_log.csv"
SKIP_VOLUMES = {"A16884": "Englands Parnassus: quotations, Oxford items entered by hand",
                "A16269": "Bel-vedere: single unattributed lines, too short"}
SONGBOOKS = {"A20689", "A20692", "A20693", "A20695", "A20696"}
OXFORD_SIG = re.compile(r"(?i)\bE\.\s*O\b|E\.\s*Ox|Oxen|Oxf|\bVere\b|\bVeer\b|Lo\.?\s*Ox")
PSEUDONYM = re.compile(r"(?i)^(ignoto|anomos|incerto|incertus|yloop|ꝙ?\s*yloop|fortunatus infoelix|shep\.? tonie)\.?$")
# initials of control authors, Shakespeare and Stage 3 names: never candidates for Oxford
KNOWN_INITIALS = {"TL", "TW", "NB", "SED", "ED", "SPS", "PS", "SD", "WS", "MD", "GG", "GT", "BG", "TC", "RW", "LV", "ME",
                  "FK", "WH", "RH", "IH", "DS",   # Paradise poets resolved to names in other editions
                  "FD", "WD", "ID"}               # Davisons; John Davies (named "IOHN DAVIS" in the 1611 Rapsody)
# pseudonyms that resolve to known authors are treated like named signatures
KNOWN_PSEUDONYMS = re.compile(r"(?i)^shep\.? tonie\.?$")      # Anthony Munday (Englands Helicon)


def sig_class(sig):
    s = re.sub(r"\s+", " ", (sig or "")).strip().strip(".")
    s = re.sub(r"^(ꝙ|quod|finis)\s*", "", s, flags=re.I).strip()
    s = re.sub(r"\s*\(section\)$", "", s)
    if not s:
        return "unsigned", ""
    if OXFORD_SIG.search(s):
        return "oxford", s
    if KNOWN_PSEUDONYMS.match(s):
        return "named", s
    if PSEUDONYM.match(s):
        return "pseudonym", s
    letters = re.sub(r"[^A-Za-zƲ]", "", s.replace("Ʋ", "V"))
    if re.fullmatch(r"(?:[A-ZƲ]\.?\s*){1,3}", s.replace("Ʋ", "V")) or (len(letters) <= 3 and letters.isupper()):
        return ("known-initials" if letters.upper() in KNOWN_INITIALS else "initials"), s
    return "named", s


def key(first_line):
    return fold(first_line)[:28]


HEAD_BY = re.compile(r"(?:[Bb]y|made by|written by|set downe by)\s+((?:[A-Z]\.\s*){1,3}|(?:Sir|Master|M\.|Lord|Earle|Earl)\s+[A-Z][a-z]+|[A-Z]{3,}\s+[A-Z]{3,})")
# Poetical Rapsody: authorship is given per section (signature at section end), not per poem
RAPSODY_SECTIONS = {"sonnets, odes, elegies, and madrigalls": "Fra. Davison (section)",          # 1602
                    "sonets, odes, elegies and other poesies": "A. W. (section)",               # 1602
                    "sonnets, odes, elegies, madrigals, andepigrams": "Fra. Davison (section)",  # 1611 (TCP spacing)
                    "sonnets, odes, elegies, and other poesies": "A. W. (section)"}             # 1611
# witnesses of Oxford reference poems whose first line differs too much for the fuzzy match
OXFORD_VARIANTS = {"A16273_054": "oxf-p-14 ('What Sheepheard can expresse' = 'What cunning can express')"}


def rapsody_attributions(tcp):
    """Map first-line key -> section attribution for the Poetical Rapsody editions."""
    out = {}
    path = ROOT / f"data/reference/raw/tcp/{tcp}.xml"
    loc = lambda t: t.rsplit("}", 1)[-1] if isinstance(t, str) else ""
    txt = lambda e: re.sub(r"\s+", " ", "".join(e.itertext())).strip()
    body = next(e for e in ET.parse(path).getroot().iter() if loc(e.tag) == "body")
    for sec in (c for c in body if loc(c.tag) == "div"):
        head = next((txt(h) for h in sec if loc(h.tag) == "head"), "").lower().strip(" .")
        who = next((v for k, v in RAPSODY_SECTIONS.items() if head.startswith(k)), None)
        if not who:
            continue
        for l in (e for e in sec.iter() if loc(e.tag) == "l"):
            pass
        for d in (e for e in sec.iter() if loc(e.tag) == "div"):
            first = next((txt(l) for l in d.iter() if loc(l.tag) == "l"), "")
            if first:
                out.setdefault(key(first), who)
    return out


def effective_signature(p, section_attr):
    """Printed signature, else an author named in the heading, else a section attribution."""
    if p["signed"].strip():
        return p["signed"]
    m = HEAD_BY.search(p.get("head", ""))
    if m:
        return m.group(1)
    return section_attr.get((p["tcp_id"], key(p["first_line"])), "")


def is_oxford_poem(fl, oxford_lines):
    a = fold(fl)
    for o in oxford_lines:
        b = a[:len(o) + 3]
        if o and SequenceMatcher(None, o, b).ratio() >= 0.8:
            return True
    return False


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    vols = [r["tcp_id"] for r in csv.DictReader(open(SOURCES, encoding="utf-8"))]
    year = {r["tcp_id"]: r["year"] for r in csv.DictReader(open(SOURCES, encoding="utf-8"))}
    poems = list(csv.DictReader(open(ROOT / "data/reference/text/tcp_poems.csv", encoding="utf-8")))
    songs = [dict(poem_id=s["song_id"], tcp_id=s["tcp_id"], head=s["head"], signed="", first_line=s["first_clean_line"],
                  path=s["path"], div_path="song") for s in csv.DictReader(open(ROOT / "data/reference/text/songs/songs.csv", encoding="utf-8")) if s["path"]]
    allp = [p for p in poems if p["tcp_id"] not in SONGBOOKS] + songs
    man = list(csv.DictReader(open(ROOT / "data/reference/manifest.csv", encoding="utf-8")))
    oxford_lines = {fold(r["title_or_first_line"])[:40] for r in man if r["author"] == "Oxford" and r["genre"] == "lyric"}
    oxford_lines |= {fold(p["first_line"])[:40] for p in poems if p["path"] in {r["orig_text_path"] for r in man if r["author"] == "Oxford"}}
    section_attr = {}
    for t in ("A19943", "A19945"):
        for k_, v in rapsody_attributions(t).items():
            section_attr[(t, k_)] = v
    shk_paths = {r["orig_text_path"] for r in man if r["author"] == "Shakespeare"}
    witnesses = defaultdict(list)
    for p in allp:
        if p["first_line"]:
            witnesses[key(p["first_line"])].append(p)
    for k in witnesses:
        witnesses[k].sort(key=lambda p: (year.get(p["tcp_id"], "9999"), p["tcp_id"], p["poem_id"]))

    log, cands, done = [], [], set()
    for p in allp:
        if p["tcp_id"] not in vols:
            continue
        k = key(p["first_line"])
        def decide():
            if p["tcp_id"] in SKIP_VOLUMES:
                return "skip", SKIP_VOLUMES[p["tcp_id"]]
            if not p["first_line"] or not p["path"]:
                return "skip", "no text"
            if p["div_path"] != "song":
                why = generic_exclusion(p)
                if why:
                    return "skip", why
            if p["path"] in shk_paths:
                return "skip", "Shakespeare text"
            if p["poem_id"] in OXFORD_VARIANTS:
                return "skip", "Oxford reference poem variant: " + OXFORD_VARIANTS[p["poem_id"]]
            if is_oxford_poem(p["first_line"], oxford_lines):
                return "skip", "Oxford reference poem (manifest; fuzzy first-line match)"
            if k in done:
                return "dup", "other witness of a candidate already listed"
            classes = [sig_class(effective_signature(w, section_attr)) for w in witnesses[k]]
            bad = [s for c, s in classes if c in ("named", "known-initials")]
            if bad:
                return "skip", "a witness names another author: " + " | ".join(sorted(set(bad)))[:80]
            return "candidate", ""
        d, why = decide()
        tokens = len(C.tokenize((ROOT / ("data/reference/text/norm_ma/" + p["path"][len("data/reference/text/"):])).read_text(encoding="utf-8"))) if p["path"] else 0
        log.append(dict(poem_id=p["poem_id"], tcp_id=p["tcp_id"], signed=p["signed"], first_line=p["first_line"][:80],
                        tokens=tokens, decision=d, reason=why))
        if d != "candidate":
            continue
        done.add(k)
        ws = witnesses[k]
        best = ws[0] if ws[0]["tcp_id"] in vols else p
        cls = sorted({sig_class(effective_signature(w, section_attr))[0] for w in ws})
        main_cls = "oxford" if "oxford" in cls else ("pseudonym" if "pseudonym" in cls else ("initials" if "initials" in cls else "unsigned"))
        btok = len(C.tokenize((ROOT / ("data/reference/text/norm_ma/" + best["path"][len("data/reference/text/"):])).read_text(encoding="utf-8")))
        cands.append(dict(
            candidate_id=f"cand-{best['poem_id']}", source=f"TCP {best['tcp_id']} ({year.get(best['tcp_id'], '?')})",
            locator=f"{best['poem_id']}; head: {best['head'][:60]}", signature_as_printed=best["signed"], sig_class=main_cls,
            first_line=best["first_line"], n_lines="", n_tokens=btok,
            attribution_used=effective_signature(best, section_attr), scorable=int(btok >= C.MIN_TEST),
            witnesses=" ; ".join(f"{w['tcp_id']}:{w['poem_id']}:{w['signed'] or '-'}" for w in ws),
            why_selected=f"{main_cls}; no witness names another author",
            known_attribution="", orig_text_path=best["path"],
            url=f"https://github.com/textcreationpartnership/{best['tcp_id']}", license="EEBO-TCP (public domain / CC0)",
            access_date="2026-11-23", notes="songbook: stanza 1 (music underlay) missing" if best["div_path"] == "song" else ""))

    old = [r for r in csv.DictReader(open(OUT, encoding="utf-8"))] if OUT.exists() else []
    hand = [r for r in old if r["candidate_id"].startswith("cand-parnassus")]
    cols = list(cands[0].keys())
    for r in hand:
        r.setdefault("sig_class", "oxford"); r.setdefault("witnesses", ""); r.setdefault("n_tokens", "")
        r["n_tokens"] = r["n_tokens"] or str(len(C.tokenize((ROOT / r["orig_text_path"]).read_text(encoding="utf-8"))))
        r["scorable"] = int(int(r["n_tokens"]) >= C.MIN_TEST)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        w.writerows([{c: r.get(c, "") for c in cols} for r in hand]); w.writerows(cands)
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)

    from collections import Counter
    print("decisions:", Counter(r["decision"] for r in log))
    print("skip reasons:", Counter(r["reason"].split(":")[0] for r in log if r["decision"] == "skip").most_common(10))
    print("candidates:", len(cands) + len(hand), "| scorable:", sum(c["scorable"] for c in cands) + sum(int(r["scorable"]) for r in hand))
    print("by class:", Counter(c["sig_class"] for c in cands), "| by source:", Counter(c["source"] for c in cands))


if __name__ == "__main__":
    main()
