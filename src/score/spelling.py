"""Hand D spelling comparison (results/PREREG.md, Amendment 3; plan.md Stage 2b).

Run in this order. Each step refuses to run until the one before it is done.

    python src/score/spelling.py vocab      # build/extend the blind standard-form table; token counts only
    python src/score/spelling.py freeze     # hash corpus, table and code (then commit)
    python src/score/spelling.py validate   # V1 and V2; Hand D is not scored
    python src/score/spelling.py main       # score Hand D, only if validation passed
"""
import csv, datetime, hashlib, json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/hand_d"
OUT = ROOT / "results/stage2b_spelling"
MANIFEST, FORMS = DATA / "manifest.csv", DATA / "standard_forms.csv"
FREEZE = OUT / "corpus_freeze.sha256"

SEED = 20261122
P = 2000                 # profile sample, usable tokens per writer
DRAWS = 200              # profile draws, main run
TRIALS, TRIAL_DRAWS = 50, 20
ALPHA, BETA = 1.0, 0.5
MIN_INFORMATIVE = 200
MIN_CONTROLS, MIN_CONTROLS_CLOSER = 10, 19
PASS_TOP1 = 0.70
BOOTSTRAPS, CLOSER_SHARE = 1000, 0.95
MIN_OPPORTUNITIES = 5
OXFORD = "Oxford"

BRACKETS = re.compile(r"\[[^\[\]]*\]|\{[^{}]*\}|<[^<>]*>")


# ---------------------------------------------------------------- text handling
def tokenize_line(line):
    """Usable original-spelling tokens of one line (A3.4)."""
    s = BRACKETS.sub("•", line)
    if re.search(r"[\[\]{}<>]", s):
        raise ValueError(f"unbalanced editorial bracket: {line!r}")
    out = []
    for chunk in s.split():
        d = unicodedata.normalize("NFKD", chunk)        # long s -> s, superscripts -> base letters
        if "•" in chunk or "^" in d or any(c.isdigit() for c in d) or "̄" in d or "̃" in d:
            continue                                    # supplied, illegible, numeral or abbreviation stroke
        d = "".join(c for c in d if not unicodedata.combining(c) and c not in "'’")
        d = d.lower().replace("v", "u").replace("j", "i")
        out.extend(re.findall(r"[^\W\d_]+", d))
    return out


def load_forms(path):
    """spelling -> standard word; excluded spellings map to None."""
    forms = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r["exclude"] == "1":
            forms[r["spelling"]] = None
        elif r["standard"].strip():
            forms[r["spelling"]] = r["standard"].strip()
    return forms


def to_pairs(lines, forms):
    """[(standard, spelling, line_no)] for one document. Unknown spellings are an error."""
    pairs = []
    for n, toks in enumerate(lines):
        for sp in toks:
            if sp not in forms:
                raise KeyError(f"spelling not in standard-form table: {sp!r}")
            if forms[sp] is not None:
                pairs.append((forms[sp], sp, n))
    return pairs


# ---------------------------------------------------------------- scoring
def rng_for(*key):
    h = hashlib.sha256("|".join(map(str, (SEED,) + key)).encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


def profile_sample(docs, size, rng):
    """Whole documents in random order until `size`; the last one gives a contiguous window."""
    got = []
    for i in rng.permutation(len(docs)):
        need = size - len(got)
        if need <= 0:
            break
        d = docs[i]
        if len(d) > need:
            start = int(rng.integers(0, len(d) - need + 1))
            d = d[start:start + need]
        got.extend(d)
    if len(got) < size:
        raise ValueError("writer has less text than the profile size")
    return got


def variant_counts(corpus, query):
    """Number of distinct spellings of each standard word anywhere in the corpus and query."""
    seen = {}
    for docs in corpus.values():
        for d in docs:
            for std, sp, *_ in d:
                seen.setdefault(std, set()).add(sp)
    for std, sp, *_ in query:
        seen.setdefault(std, set()).add(sp)
    return {k: len(v) for k, v in seen.items()}


def log_ratios(corpus, query, size, draws, key):
    """matrix [writer, informative query token] of mean log P_writer / P_background (A3.5)."""
    writers = sorted(corpus)
    variants = variant_counts(corpus, query)
    info = [t for t in query if variants[t[0]] >= 2]
    M = np.zeros((len(writers), len(info)))
    rngs = {w: rng_for(*key, w) for w in writers}
    for _ in range(draws):
        pair, word, bg_pair, bg_word = {}, {}, Counter(), Counter()
        for w in writers:
            s = profile_sample(corpus[w], size, rngs[w])
            pair[w] = Counter((t[0], t[1]) for t in s)
            word[w] = Counter(t[0] for t in s)
            bg_pair.update(pair[w]); bg_word.update(word[w])
        B = np.array([(bg_pair[(t[0], t[1])] + BETA) / (bg_word[t[0]] + BETA * variants[t[0]]) for t in info])
        for i, w in enumerate(writers):
            c = np.array([pair[w][(t[0], t[1])] for t in info], dtype=float)
            n = np.array([word[w][t[0]] for t in info], dtype=float)
            M[i] += np.log((c + ALPHA * B) / (n + ALPHA) / B)
    return writers, M / draws, info


def rank_of(writers, scores, target):
    """1 = highest. Ties count against the target."""
    t = scores[writers.index(target)]
    return 1 + sum(1 for w, s in zip(writers, scores) if w != target and s >= t)


def bootstrap_share(writers, M, info, target, rng, n=BOOTSTRAPS):
    """Share of line-resampled queries in which the target beats every other writer."""
    lines = sorted({t[2] for t in info})
    by_line = {ln: [j for j, t in enumerate(info) if t[2] == ln] for ln in lines}
    sums = np.array([M[:, by_line[ln]].sum(axis=1) for ln in lines]).T     # [writer, line]
    counts = np.array([len(by_line[ln]) for ln in lines])
    ti, wins = writers.index(target), 0
    for _ in range(n):
        pick = rng.integers(0, len(lines), len(lines))
        s = sums[:, pick].sum(axis=1) / counts[pick].sum()
        wins += s[ti] > np.delete(s, ti).max()
    return wins / n


# ---------------------------------------------------------------- validation
def holdout_split(docs, held_size, profile_size, rng, tries=100):
    """(held-out tokens, remaining documents), split by whole documents; None if impossible."""
    if len(docs) < 2:
        return None
    for _ in range(tries):
        order = rng.permutation(len(docs))
        held, k = [], 0
        while k < len(order) and len(held) < held_size:
            held.extend(docs[order[k]]); k += 1
        rest = [docs[i] for i in order[k:]]
        if len(held) >= held_size and sum(map(len, rest)) >= profile_size:
            return held[:held_size], rest
    return None


def eligible(corpus, held_size, size=P):
    return {w: d for w, d in corpus.items() if holdout_split(d, held_size, size, rng_for("eligible", w)) is not None}


def validate(corpus, held_size, size=P, trials=TRIALS, draws=TRIAL_DRAWS):
    per_writer = {}
    for w in sorted(corpus):
        rng, hits, ranks, mistaken = rng_for("validate", w), 0, [], Counter()
        for k in range(trials):
            held, rest = holdout_split(corpus[w], held_size, size, rng, tries=10000)
            trial = dict(corpus); trial[w] = rest
            writers, M, _ = log_ratios(trial, held, size, draws, ("validate", w, k))
            scores = M.mean(axis=1)
            r = rank_of(writers, scores, w)
            hits += r == 1; ranks.append(r)
            if r != 1:
                mistaken[max((x for x in writers if x != w), key=lambda x: scores[writers.index(x)])] += 1
        per_writer[w] = {"top1": hits / trials, "median_rank": float(np.median(ranks)),
                         "mistaken_for": dict(mistaken.most_common())}   # check for clustering by source
    macro = float(np.mean([v["top1"] for v in per_writer.values()]))
    v2 = per_writer[OXFORD]["top1"]
    return {"V1_macro_top1": macro, "V1_pass": macro >= PASS_TOP1, "V2_oxford_top1": v2,
            "V2_pass": v2 >= PASS_TOP1, "pass": macro >= PASS_TOP1 and v2 >= PASS_TOP1, "writers": per_writer}


def decide(n_controls, n_informative, rank, share):
    """A3.7."""
    if n_controls < MIN_CONTROLS or n_informative < MIN_INFORMATIVE:
        return "inconclusive (too little data)"
    if n_controls >= MIN_CONTROLS_CLOSER and rank == 1 and share >= CLOSER_SHARE:
        return "H3a: de Vere closer than controls"
    if rank > (n_controls + 2) / 2:                 # below the middle of n_controls + 1 writers
        return "H3b: de Vere no closer than controls"
    return "inconclusive"


# ---------------------------------------------------------------- secondary: spelling variables
def _doubles(w):
    return len(re.findall(r"([b-df-hj-np-tv-xz])\1", w))


VARIABLES = {   # name: (opportunity(standard), realised(spelling, standard))
    "added_final_e": (lambda s: not s.endswith("e"), lambda p, s: p in (s + "e", s + s[-1] + "e")),
    "final_y_as_ie": (lambda s: len(s) > 1 and s.endswith("y"), lambda p, s: p.endswith("ie")),
    "i_as_y": (lambda s: "i" in s[:-1], lambda p, s: p.count("y") > s.count("y")),
    "extra_doubled_consonant": (lambda s: True, lambda p, s: _doubles(p) > _doubles(s)),
    "reduced_doubled_consonant": (lambda s: _doubles(s) > 0, lambda p, s: _doubles(p) < _doubles(s)),
    "doubled_e_or_o": (lambda s: "e" in s or "o" in s,
                       lambda p, s: p.count("ee") + p.count("oo") > s.count("ee") + s.count("oo")),
    "ea_as_ee": (lambda s: "ea" in s, lambda p, s: p.count("ea") < s.count("ea") and p.count("ee") > s.count("ee")),
    "sc_for_s": (lambda s: re.match(r"s[aeiouy]", s) is not None, lambda p, s: p.startswith("sc")),
}


def variable_rates(tokens):
    out = {}
    for name, (opp, real) in VARIABLES.items():
        o = [(t[1], t[0]) for t in tokens if opp(t[0])]
        out[name] = (sum(bool(real(p, s)) for p, s in o), len(o))
    return out


def variable_distance(a, b):
    d = [abs(a[v][0] / a[v][1] - b[v][0] / b[v][1]) for v in VARIABLES
         if a[v][1] >= MIN_OPPORTUNITIES and b[v][1] >= MIN_OPPORTUNITIES]
    return (float(np.mean(d)), len(d)) if d else (None, 0)


# ---------------------------------------------------------------- files and commands
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_rows():
    rows = [r for r in csv.DictReader(open(MANIFEST, encoding="utf-8")) if r["include"] == "1"]
    if not rows:
        sys.exit("No included documents in data/hand_d/manifest.csv. Add texts first (data/hand_d/README.md).")
    for r in rows:
        f = ROOT / r["path"]
        if not f.is_file():
            sys.exit(f"{r['doc_id']}: missing text file {r['path']}")
        if r["hand"] != "holograph":
            sys.exit(f"{r['doc_id']}: only holograph documents may be included (hand={r['hand']!r})")
        if r["role"] not in ("query", "oxford", "control"):
            sys.exit(f"{r['doc_id']}: unknown role {r['role']!r}")
        if (r["role"] == "oxford") != (r["writer"] == OXFORD):
            sys.exit(f"{r['doc_id']}: role 'oxford' and writer '{OXFORD}' must go together")
    return rows


def read_lines(row):
    return [tokenize_line(x) for x in (ROOT / row["path"]).read_text(encoding="utf-8").splitlines()]


def cmd_vocab():
    sys.path.insert(0, str(ROOT / "src/normalize"))
    from normalize import normalize_text
    if FREEZE.exists():
        sys.exit("Corpus is frozen; the table can't change.")
    rows = manifest_rows()
    vocab, counts = set(), Counter()
    for r in rows:
        for line in read_lines(r):
            vocab.update(line); counts[r["writer"]] += len(line)
    old = {r["spelling"]: r for r in csv.DictReader(open(FORMS, encoding="utf-8"))} if FORMS.exists() else {}
    with open(FORMS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["spelling", "standard", "exclude", "checked"])
        w.writeheader()
        for sp in sorted(vocab | set(old)):            # alphabetical, no writer labels
            if sp in old:
                w.writerow(old[sp])
            else:
                guess = "".join(tokenize_line(normalize_text(sp)[0]))
                w.writerow({"spelling": sp, "standard": guess, "exclude": "0", "checked": "0"})
    print("usable tokens per writer (before exclusions):")
    for name, n in counts.most_common():
        print(f"  {name}: {n}")


def cmd_freeze():
    if FREEZE.exists():
        sys.exit(f"{FREEZE} already exists.")
    rows = manifest_rows()
    for r in rows:
        if sha(ROOT / r["path"]) != r["sha256"]:
            sys.exit(f"{r['doc_id']}: sha256 in manifest doesn't match the file")
    table = list(csv.DictReader(open(FORMS, encoding="utf-8")))
    unchecked = [t["spelling"] for t in table if t["checked"] != "1"]
    if unchecked:
        sys.exit(f"{len(unchecked)} spellings not yet checked, e.g. {unchecked[:10]}")
    forms = load_forms(FORMS)
    for r in rows:
        to_pairs(read_lines(r), forms)                 # every spelling covered
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = [MANIFEST, FORMS, Path(__file__).resolve()]
    FREEZE.write_text(f"Corpus frozen {now}, before validation\n" +
                      "".join(f"{sha(p)} *{p.relative_to(ROOT).as_posix()}\n" for p in files), encoding="utf-8")
    print(f"Frozen. Commit {FREEZE.relative_to(ROOT)} with the manifest and table before validating.")


def load_frozen():
    if not FREEZE.exists():
        sys.exit("Run 'freeze' first.")
    for line in FREEZE.read_text(encoding="utf-8").splitlines()[1:]:
        digest, name = line.split(" *")
        if sha(ROOT / name) != digest:
            sys.exit(f"{name} changed after the freeze.")
    forms, corpus, query, offset = load_forms(FORMS), {}, [], 0
    for r in manifest_rows():
        if sha(ROOT / r["path"]) != r["sha256"]:
            sys.exit(f"{r['doc_id']}: text changed after the freeze.")
        pairs = to_pairs(read_lines(r), forms)
        if r["role"] == "query":
            query += [(s, p, n + offset) for s, p, n in pairs]
            offset += 100000                           # keep line numbers distinct across pages
        elif pairs:
            corpus.setdefault(r["writer"], []).append(pairs)
    if not query or OXFORD not in corpus:
        sys.exit("Need both a query (Hand D) and Oxford documents.")
    return corpus, query


def write_once(path, obj):
    if path.exists():
        sys.exit(f"{path} already exists; results are never overwritten.")
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def cmd_validate():
    if (OUT / "validation.json").exists():
        sys.exit("validation.json already exists.")
    corpus, query = load_frozen()
    held = len(query)                                  # only the length of Hand D is used
    use = eligible(corpus, held)
    dropped = sorted(set(corpus) - set(use))
    n_controls = len(use) - (OXFORD in use)
    if OXFORD not in use or n_controls < MIN_CONTROLS:
        res = {"pass": False, "reason": "de Vere or too few control writers eligible", "n_controls": n_controls}
    else:
        res = validate(use, held)
    res.update({"held_out_size": held, "n_controls": n_controls, "ineligible": dropped})
    write_once(OUT / "validation.json", res)
    print(json.dumps(res, indent=2))


def cmd_main():
    v = OUT / "validation.json"
    if not v.exists():
        sys.exit("Run 'validate' first.")
    if not json.loads(v.read_text(encoding="utf-8"))["pass"]:
        sys.exit("Validation failed: the comparison is inconclusive and Hand D is not scored (A3.6).")
    if (OUT / "main.json").exists():
        sys.exit("main.json already exists.")
    corpus, query = load_frozen()
    use = eligible(corpus, len(query))
    writers, M, info = log_ratios(use, query, P, DRAWS, ("main",))
    scores = M.mean(axis=1)
    rank = rank_of(writers, scores, OXFORD)
    share = bootstrap_share(writers, M, info, OXFORD, rng_for("bootstrap"))
    res = {"n_controls": len(writers) - 1, "query_tokens": len(query), "informative_tokens": len(info),
           "oxford_rank": rank, "oxford_bootstrap_share": share,
           "outcome": decide(len(writers) - 1, len(info), rank, share)}
    qr = variable_rates(query)
    with open(OUT / "scores.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["writer", "llr_score", "variable_distance", "variables_compared"])
        for i in np.argsort(-scores):
            toks = [t for d in use[writers[i]] for t in d]
            w.writerow([writers[i], f"{scores[i]:.5f}", *variable_distance(qr, variable_rates(toks))])
    write_once(OUT / "main.json", res)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    cmds = {"vocab": cmd_vocab, "freeze": cmd_freeze, "validate": cmd_validate, "main": cmd_main}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]]()
