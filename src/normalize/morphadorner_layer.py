"""Second normalization pass with MorphAdorner (Northwestern, v2.0.1, Early Modern English data).

Input:  the rule-based layer, data/reference/text/norm/**.txt (typographic forms, abbreviations,
        u/v, i/j already handled; see data/reference/NORMALIZATION.md).
Output: data/reference/text/norm_ma/<same path>.txt  standardized spelling, line breaks kept
        data/reference/text/adorned/<same path>.tsv  MorphAdorner token table:
            token, spelling, NUPOS part of speech, standard spelling, lemma, end-of-sentence
        data/reference/text/norm_ma/changes.csv     every (spelling -> standard) change with counts

MorphAdorner drops line breaks, so its standard spellings are re-aligned onto our lines by
walking each line and matching MorphAdorner's surface tokens in order. Words that cannot be
aligned are left unchanged and counted.

Only plain spelling changes are accepted; see accept() for the filter. Accepted changes go to
norm_ma/changes.csv, rejected ones to norm_ma/rejected.csv, for review.

Requires Java and MorphAdorner unpacked in tools/morphadorner (see tools/README.md).
Usage: python src/normalize/morphadorner_layer.py
"""
import csv, re, shutil, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/morphadorner"
NORM = ROOT / "data/reference/text/norm"
OUT = ROOT / "data/reference/text/norm_ma"
ADORN = ROOT / "data/reference/text/adorned"
# (input, output, token tables): reference texts, then hand-entered candidate texts
LAYERS = [(NORM, OUT, ADORN),
          (ROOT / "data/candidates/norm", ROOT / "data/candidates/norm_ma", ROOT / "data/candidates/adorned")]
BATCH = 300

# MorphAdorner modernizes grammar as well as spelling and guesses from context, which erases
# stylometric markers (doth/does, ye/you, whilst/while) and makes errors (fall->fallen,
# sight->sighed, an->and). So a change is ACCEPTED only if all of these hold:
#   1. EITHER the input word is not in MorphAdorner's standard-spelling list (a real variant spelling)
#      OR the two forms differ only orthographically (same skeleton(): final -e, doubled letters,
#      y/i, final -ie/-y), e.g. beare->bear, sonne->son, fayre->fair
#   2. neither form is a protected grammatical/lexical marker
#   3. it doesn't turn an -eth/-est verb ending into a modern one
#   4. it doesn't add an apostrophe (beauties -> beauty's guesses a possessive)
#   5. same first letter (ignoring case) and length change of at most 3
#   6. the input is not an elision ending in an apostrophe (t', th'): kept as printed for metre
#   7. not in OVERRIDES (reviewed and rejected by hand)
PROTECTED = set("""doth does dooth hath has ye you thou thee thy thine whilst while whiles amongst among
betwixt between mought might ere oft often tis twas twere o oh an and then than art wert wast
shalt wilt canst couldst wouldst shouldst didst hast dost to too of off""".split())
OVERRIDES = {
    ("past", "passed"), ("mans", "men"), ("faine", "feign"), ("somers", "some"), ("fre", "from"),
    ("borne", "born"),     # 'borne' (carried) is a distinct modern word
    ("lose", "loose"), ("doe", "do"), ("bee", "be"),
    ("heer", "her"), ("tong", "tonge"), ("divers", "diverse"),   # reviewed 2026-11-22   # real words; rule layer already handles doe/bee by context
}


def skeleton(w):
    w = w.lower()
    w = re.sub(r"ie$", "y", w)
    w = w.replace("y", "i")
    w = re.sub(r"e$", "", w)
    return re.sub(r"(.)\1+", r"\1", w)


STANDARD = set()


def accept(sp, std):
    a, b = sp.lower(), std.lower()
    if a == b or not b:
        return False
    if a in STANDARD and skeleton(a) != skeleton(b):
        return False
    if a.endswith("'"):
        return False
    if a in PROTECTED or b in PROTECTED:
        return False
    if a.endswith(("eth", "est")) and not b.endswith(("eth", "est")):
        return False
    if "'" in b and "'" not in a:
        return False
    if a[:1] != b[:1] or abs(len(a) - len(b)) > 3:
        return False
    return (a, b) not in OVERRIDES


def run_batch(files, workdir):
    """Copy files to a flat staging dir, run MorphAdorner, return {original path: tsv text}."""
    inp, out = workdir / "in", workdir / "out"
    for d in (inp, out):
        shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    names = {}
    for i, f in enumerate(files):
        n = f"f{i:05d}.txt"
        shutil.copyfile(f, inp / n); names[n] = f
    cp = ";".join(str(TOOL / p) for p in ("bin", "dist/*", "lib/*"))
    cmd = ["java", "-Xmx3072m", "-Xss1m", "-cp", cp, "edu.northwestern.at.morphadorner.MorphAdorner",
           "-p", str(TOOL / "emeplaintext.properties"), "-l", str(TOOL / "data/emelexicon.lex"),
           "-t", str(TOOL / "data/emetransmat.mat"), "-u", str(TOOL / "data/emesuffixlexicon.lex"),
           "-a", str(TOOL / "data/ememergedspellingpairs.tab"), "-s", str(TOOL / "data/standardspellings.txt"),
           "-w", str(TOOL / "data/spellingsbywordclass.txt"), "-o", str(out)] + sorted(str(p) for p in inp.glob("*.txt"))
    r = subprocess.run(cmd, cwd=TOOL, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(r.stdout[-2000:] + r.stderr[-2000:])
    res = {}
    for n, f in names.items():
        o = out / n
        if not o.exists():
            raise SystemExit(f"MorphAdorner wrote no output for {f}")
        res[f] = o.read_text(encoding="utf-8")
    return res


def realign(text, tsv, changes, rejected, stats):
    """Put MorphAdorner standard spellings back into the original lines."""
    toks = []
    for row in tsv.splitlines():
        parts = row.split("\t")
        if len(parts) >= 4:
            toks.append((parts[1], parts[3]))
    out_lines, k = [], 0
    for line in text.split("\n"):
        i, buf = 0, []
        while i < len(line):
            if line[i].isspace():
                buf.append(line[i]); i += 1; continue
            if k < len(toks) and toks[k][0] and line.startswith(toks[k][0], i):
                sp, std = toks[k]
                if std and std.lower() != sp.lower():
                    ok = accept(sp, std)
                    (changes if ok else rejected)[(sp.lower(), std.lower())] += 1
                    buf.append(std if ok else sp)
                else:
                    buf.append(sp)
                i += len(sp); k += 1
            else:
                # resync: skip MorphAdorner tokens that don't start here (rare), else copy one char
                look = next((j for j in range(k, min(k + 4, len(toks))) if toks[j][0] and line.startswith(toks[j][0], i)), None)
                if look is not None:
                    stats["skipped tokens"] += look - k; k = look; continue
                buf.append(line[i]); i += 1; stats["unaligned chars"] += 1
        out_lines.append("".join(buf))
    stats["tokens"] += len(toks)
    if k < len(toks):
        stats["unused tokens"] += len(toks) - k
    return "\n".join(out_lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    STANDARD.update(l.strip().lower() for l in (TOOL / "data/standardspellings.txt").read_text(encoding="utf-8", errors="replace").splitlines() if l.strip())
    changes, rejected, stats = Counter(), Counter(), Counter()
    with tempfile.TemporaryDirectory() as td:
        for src, out, adorn in LAYERS:
            if not src.exists():
                continue
            files = sorted(p for p in src.rglob("*.txt"))
            for b in range(0, len(files), BATCH):
                chunk = files[b:b + BATCH]
                res = run_batch(chunk, Path(td))
                for f, tsv in res.items():
                    rel = f.relative_to(src)
                    (adorn / rel).with_suffix(".tsv").parent.mkdir(parents=True, exist_ok=True)
                    (adorn / rel).with_suffix(".tsv").write_text(tsv, encoding="utf-8")
                    (out / rel).parent.mkdir(parents=True, exist_ok=True)
                    (out / rel).write_text(realign(f.read_text(encoding="utf-8"), tsv, changes, rejected, stats), encoding="utf-8")
                print(f"  {src.relative_to(ROOT)}: {min(b + BATCH, len(files))}/{len(files)} files")
    with open(OUT / "changes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["spelling", "standard", "count"])
        for (a, s), c in changes.most_common():
            w.writerow([a, s, c])
    with open(OUT / "rejected.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["spelling", "morphadorner_standard", "count"])
        for (a, s_), c in rejected.most_common():
            w.writerow([a, s_, c])
    print(dict(stats))
    print(f"accepted {sum(changes.values())} changes ({len(changes)} distinct); rejected {sum(rejected.values())} ({len(rejected)} distinct)")


if __name__ == "__main__":
    main()
