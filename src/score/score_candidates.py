"""Score Stage 1 candidates (results/PREREG.md, Amendment 1). Writes results/stage1/.

A1.1  scorable candidates from data/candidates/manifest.csv (>= 100 tokens)
A1.2  every witness of the candidate is removed from reference/imposter texts before scoring
A1.3  candidates that were validation decoys are scored but excluded from the H1 count
A1.4  balanced GI (round 2 method), F1 decides; lead >= 0.83, strong lead >= 0.95
A1.5  one-sided exact binomial test: leads among N vs p0 = 0.0417 (strong: 0.0083)
A1.6  all scores published; leads listed with witnesses and caveats; no attributions

Usage: python src/score/score_candidates.py
"""
import csv, json, re, sys, time
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C                                  # noqa: E402
from features import Space                          # noqa: E402
from gi import general_imposters, rng_for, centroid_ranks   # noqa: E402

OUT = C.ROOT / "results/stage1"
THETA, THETA1 = 0.83, 0.95
P0, P0_STRONG = 10 / 240, 2 / 240
REF_ROLES = ("target-oxford", "shakespeare", "control", "imposter")


def norm_ma_path(p):
    if p.startswith("data/reference/text/"):
        return C.ROOT / ("data/reference/text/norm_ma/" + p[len("data/reference/text/"):])
    if p.startswith("data/candidates/text/"):
        return C.ROOT / ("data/candidates/norm_ma/" + p[len("data/candidates/text/"):])
    raise ValueError(p)


class Scorer:
    def __init__(self, texts):
        self.groups = {}
        for t in texts:
            if t.role in REF_ROLES:
                self.groups.setdefault("pool" if t.role == "imposter" else t.author, []).append(t)
        self.spaces = {k: Space(k) for k in ("F1", "F2")}
        self.cache, self.docs_author = {}, {}

    def docs(self, author, excluded):
        ex = frozenset(t.id for t in self.groups[author] if t.id in excluded)
        ck = (author, ex)
        if ck not in self.cache:
            keys = []
            for j, (_, vol, toks) in enumerate(C.chunk([t for t in self.groups[author] if t.id not in ex], lambda t: author)):
                key = (author, ex, vol, j)
                for sp in self.spaces.values():
                    sp.row(key, toks)
                self.docs_author[key] = author
                keys.append(key)
            self.cache[ck] = keys
        return self.cache[ck], bool(ex)

    def score(self, cid, tokens, excluded):
        tkey = ("cand", cid)
        tdocs, _ = self.docs("Oxford", excluded)
        imp, removed = [], []
        for a in self.groups:
            if a == "Oxford":
                continue
            ks, hit = self.docs(a, excluded)
            imp += ks
            if hit:
                removed.append(a)
        out = {}
        for fs, sp in self.spaces.items():
            sp.row(tkey, tokens)
            R, v, _ = sp.build(tdocs + imp, tkey)
            out[fs] = general_imposters(v, R[: len(tdocs)], R[len(tdocs):], rng_for(cid, "Oxford", fs))
            if fs == "F1":
                out["nearest"] = centroid_ranks(v, R, [self.docs_author[k] for k in tdocs + imp])[0]
        out["removed_from"] = ";".join(removed)
        return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    texts = C.load()
    S = Scorer(texts)
    venue_ids = {r["test_id"] for r in csv.DictReader(open(C.ROOT / "results/validation/round2/scores.csv", encoding="utf-8"))
                 if r["stage"] == "S1" and r["kind"] == "decoy-venue"}
    cands = [r for r in csv.DictReader(open(C.ROOT / "data/candidates/manifest.csv", encoding="utf-8")) if r["scorable"] == "1"]
    rows = []
    for r in cands:
        wit = {w.split(":")[1] for w in r["witnesses"].split(" ; ") if w.count(":") >= 2}
        own = r["candidate_id"].replace("cand-", "")
        excluded = wit | {own}
        tokens = C.tokenize(norm_ma_path(r["orig_text_path"]).read_text(encoding="utf-8"))
        s = S.score(r["candidate_id"], tokens, excluded)
        rows.append(dict(candidate_id=r["candidate_id"], source=r["source"], sig_class=r["sig_class"],
                         attribution=r.get("attribution_used") or r["signature_as_printed"], n_tokens=len(tokens),
                         F1=s["F1"], F2=s["F2"], nearest_author=s["nearest"],
                         lead=int(s["F1"] >= THETA), strong_lead=int(s["F1"] >= THETA1),
                         validation_decoy=int(bool(excluded & venue_ids)),
                         paradise=int(bool(re.search(r"A2116[12]|A21166", r["witnesses"] + r["source"]))),
                         songbook=int("song" in r["candidate_id"]), self_match_removed_from=s["removed_from"],
                         first_line=r["first_line"], witnesses=r["witnesses"]))
    rows.sort(key=lambda x: -x["F1"])
    with open(OUT / "candidate_scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    h1 = [x for x in rows if not x["validation_decoy"]]
    N, k, k1 = len(h1), sum(x["lead"] for x in h1), sum(x["strong_lead"] for x in h1)
    bt, bt1 = binomtest(k, N, P0, alternative="greater"), binomtest(k1, N, P0_STRONG, alternative="greater")
    summary = dict(n_scored=len(rows), N_h1=N, leads=k, expected_leads=round(N * P0, 1), p_leads=round(bt.pvalue, 4),
                   strong_leads=k1, expected_strong=round(N * P0_STRONG, 1), p_strong=round(bt1.pvalue, 4),
                   decoy_overlap_scored=sum(x["validation_decoy"] for x in rows),
                   decoy_overlap_leads=sum(x["lead"] for x in rows if x["validation_decoy"]),
                   self_match_exclusions=sum(bool(x["self_match_removed_from"]) for x in rows),
                   leads_from_paradise=sum(x["lead"] for x in h1 if x["paradise"]),
                   leads_by_source=Counter(x["source"] for x in h1 if x["lead"]),
                   leads_by_class=Counter(x["sig_class"] for x in h1 if x["lead"]),
                   nearest_author_of_leads=Counter(x["nearest_author"] for x in h1 if x["lead"]),
                   F1_mean=round(float(np.mean([x["F1"] for x in h1])), 3), runtime_s=round(time.time() - t0))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
