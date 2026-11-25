"""Spelling normalization layer. Rules and rationale: data/reference/NORMALIZATION.md.

Reads every original-layer text under data/reference/text/{orig,special,edited}/ and writes
the normalized version to data/reference/text/norm/<same relative path>. Keeps line breaks,
case and punctuation. Logs rule counts per file to text/norm/normalize_log.csv, then fills norm_text_path in the manifest.

Usage: python src/normalize/normalize.py
"""
import csv, re, sys, unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT = ROOT / "data/reference/text"
SOURCES = ["orig", "special", "edited", "songs"]
NORM = TEXT / "norm"

VOWELS = "aeiouyAEIOUY"
SUPERSCRIPT_WORDS = {"yᵉ": "the", "yᵗ": "that", "yᵘ": "thou", "wᵗ": "with", "wᶜ": "which",
                     "Yᵉ": "The", "Yᵗ": "That", "Yᵘ": "Thou", "Wᵗ": "With", "Wᶜ": "Which"}
MODIFIERS = "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"
UNMOD = dict(zip(MODIFIERS, "abcdefghijklmnoprstuvwxyz0123456789"))
RV_STEMS = ("serue", "deserue", "preserue", "obserue", "reserue", "conserue", "carue", "starue",
            "swerue", "curue", "nerue", "solue", "resolue", "dissolue", "absolue", "delue", "twelue",
            "selue", "halue", "salue", "calue", "shelue", "wolue", "silue")
LEXICON = {
    "mee": "me", "hee": "he", "shee": "she", "wee": "we", "yee": "ye",
    "goe": "go", "soe": "so", "noe": "no", "doo": "do", "dooth": "doth",
    "beene": "been", "beyng": "being", "beinge": "being",
    "onely": "only", "onlie": "only", "verie": "very", "anie": "any", "manie": "many", "eche": "each",
    "thei": "they", "theyr": "their", "theyre": "their", "thier": "their", "thyne": "thine", "myne": "mine",
    "wyth": "with", "whiche": "which", "suche": "such", "muche": "much", "yf": "if", "hir": "her", "owne": "own",
    "shal": "shall", "wyll": "will", "wil": "will", "al": "all", "untill": "until", "tyll": "till",
    "ys": "is", "hys": "his", "thys": "this", "wher": "where", "whan": "when", "ther": "there",
    "sayd": "said", "sayde": "said", "saide": "said",
}
THAT_NEXT = set("""i he she it we they you ye thou which who as may might hath haue have had is was are were
there shall will doth did can could would should his her my thy our their no not so from fro when if
comes came cometh commeth ment meant""".split())
ANIMAL_CONTEXT = {"bee": "be", "doe": "do"}          # keep after these words (the insect / the deer)
ANIMAL_PREV = {"the", "a", "an", "busy", "busie", "humble"}
WORD = re.compile(r"[^\W\d_]+(?:[̄][^\W\d_]*)*|[^\W\d_]*\^.", re.UNICODE)


def match_case(src, repl):
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[:1].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


def fix_word(w, log):
    """Rules 3, 7, 8 on a single word (after typographic rules)."""
    # 3. drop caps: FRaud -> Fraud (two caps then lowercase); a doubled initial (TThy) loses one
    if re.fullmatch(r"([A-Z])\1[a-z].*", w):
        w = w[1:]; log["dropcap"] += 1
    elif re.fullmatch(r"[A-Z]{2}[a-z].*", w):
        w = w[0] + w[1:].lower(); log["dropcap"] += 1
    # 7a. initial v + consonant -> u
    if len(w) > 1 and w[0] in "vV" and w[1].lower() not in "aeiouy":
        w = ("u" if w[0] == "v" else "U") + w[1:]; log["v>u"] += 1
    # 7b. medial u between vowels -> v
    chars = list(w)
    for i in range(1, len(chars) - 1):
        if chars[i] in "uU" and chars[i - 1] in VOWELS and chars[i + 1] in VOWELS:
            # 'qu' + vowel and doubled vowels like 'uu' are not touched (uu handled earlier)
            if chars[i - 1] in "qQ":
                continue
            chars[i] = "v" if chars[i] == "u" else "V"; log["u>v"] += 1
    w = "".join(chars)
    # 7c. r/l + ue stems
    lw = w.lower()
    for stem in RV_STEMS:
        k = lw.find(stem)
        if k >= 0:
            j = k + len(stem) - 2           # position of the 'u'
            w = w[:j] + ("v" if w[j] == "u" else "V") + w[j + 1:]; log["stem u>v"] += 1
            break
    # 8. initial i + vowel -> j (not the word "I")
    if len(w) > 1 and w[0] in "iI" and w[1].lower() in "aeiou":
        w = ("j" if w[0] == "i" else "J") + w[1:]; log["i>j"] += 1
    return w


def normalize_line(line, log, prev_word):
    s = unicodedata.normalize("NFC", line).replace("\xa0", " ")
    # 2. letter forms
    s = s.replace("ſ", "s").replace("Ʋ", "V").replace("é", "e").replace("É", "E")  # é marks long e in some prints
    s, n = re.subn(r"VV|UU", "W", s); log["VV>W"] += n
    s, n = re.subn(r"vv|uu", "w", s); log["vv>w"] += n
    # 4. superscript abbreviations
    for k, v in SUPERSCRIPT_WORDS.items():
        s, n = re.subn(rf"(?<![^\W\d_]){k}(?![^\W\d_])", v, s); log["superscript"] += n
    def illegible_sup(m):
        # superscript letter illegible: "that" before a pronoun/verb/function word, else "the"
        y, space, following = m.group(1), m.group(2), m.group(3) or ""
        nxt = re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", following).lower().replace("ſ", "s"))
        that = nxt in THAT_NEXT or nxt.endswith(("eth", "ed"))
        log["y^• guessed 'that'" if that else "y^• guessed 'the'"] += 1
        word = "that" if that else "the"
        return (word if y == "y" else word.capitalize()) + space + following
    s = re.sub(r"(?<![^\W\d_])([yY])\^•(\s*)([^\W\d_]*)", illegible_sup, s)
    s, n = re.subn(r"wᵗ", "with", s); log["superscript"] += n      # forthwᵗ
    s = re.sub(r"\^(.)", r"\1", s)
    s = "".join(UNMOD.get(c, c) for c in s)
    # 5. abbreviation stroke over a vowel (NFC may have precomposed it: ō -> o + U+0304)
    s = "".join(unicodedata.normalize("NFD", c) if c in "āēīōūĀĒĪŌŪ" else c for c in s)
    def macron(m):
        nxt = m.group(2)
        return m.group(1) + ("m" if nxt and nxt.lower() in "bpm" else "n") + (nxt or "")
    s, n = re.subn(r"([aeiouAEIOU])̄(\w?)", macron, s); log["macron"] += n
    s = s.replace("̄", "")
    # 6. symbols
    s, n = re.subn(r"&\s*c\b\.?", "etc.", s); log["&c"] += n
    s, n = re.subn(r"&", "and", s); log["&"] += n
    s = s.replace("ꝙ", "").replace("ꝰ", "us").replace("ꝑ", "per").replace("ꝓ", "pro")
    # 3, 7, 8, 9 word by word
    out, last = [], 0
    for m in re.finditer(r"[^\W\d_]+", s):
        w = fix_word(m.group(0), log)
        lw = w.lower()
        if lw in LEXICON:
            w = match_case(w, LEXICON[lw]); log["lexicon"] += 1
        elif lw in ANIMAL_CONTEXT and (prev_word or "").lower() not in ANIMAL_PREV:
            w = match_case(w, ANIMAL_CONTEXT[lw]); log["bee/doe>be/do"] += 1
        out.append(s[last:m.start()]); out.append(w); last = m.end()
        prev_word = w
    out.append(s[last:])
    return "".join(out), prev_word


def normalize_text(text, log=None):
    log = log if log is not None else Counter()
    prev, lines = None, []
    for line in text.split("\n"):
        nl, prev = normalize_line(line, log, prev)
        lines.append(nl)
    return "\n".join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows, total, n = [], Counter(), 0
    for src in SOURCES:
        for p in sorted((TEXT / src).rglob("*.txt")):
            rel = p.relative_to(TEXT)
            log = Counter()
            out = NORM / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(normalize_text(p.read_text(encoding="utf-8"), log), encoding="utf-8")
            rows.append({"path": rel.as_posix(), **log}); total.update(log); n += 1
    keys = sorted({k for r in rows for k in r if k != "path"})
    with open(NORM / "normalize_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path"] + keys, restval=0); w.writeheader(); w.writerows(rows)
    print(f"{n} files normalized -> {NORM.relative_to(ROOT)}")
    # candidate texts entered by hand (data/candidates/text) -> data/candidates/norm
    cdir, cnorm = ROOT / "data/candidates/text", ROOT / "data/candidates/norm"
    if cdir.exists():
        cnorm.mkdir(parents=True, exist_ok=True)
        for p in sorted(cdir.glob("*.txt")):
            (cnorm / p.name).write_text(normalize_text(p.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"{len(list(cdir.glob('*.txt')))} candidate files normalized -> data/candidates/norm")
    link_manifest()
    for k, v in total.most_common():
        print(f"  {k:22} {v}")


def norm_path(orig_path):
    """data/reference/text/<layer>/x -> data/reference/text/norm/<layer>/x (works for folders too)."""
    pre = "data/reference/text/"
    return pre + "norm/" + orig_path[len(pre):] if orig_path.startswith(pre) else ""


def link_manifest():
    man = ROOT / "data/reference/manifest.csv"
    with open(man, encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)
    k = 0
    for r in rows:
        np_ = norm_path(r["orig_text_path"]) if r["orig_text_path"] else ""
        if np_ and (ROOT / np_).exists():
            r["norm_text_path"] = np_; k += 1
    with open(man, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"manifest: norm_text_path set on {k} rows")


if __name__ == "__main__":
    main()
