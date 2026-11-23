"""Validation runs (results/PREREG.md section 5). Sets thresholds; scores NO candidate and does NOT
compute de Vere vs Shakespeare. Writes results/validation/.

  5.1  de Vere target: leave-one-out on core poems (>=100 tokens), control decoys (a),
       same-venue Paradise decoys (b)  ->  theta (FPR <= 5%), theta1 (FPR <= 1%), recall, power
  5.2  Shakespeare target: control decoys -> theta_S; positive control (LOO sonnets + long poems);
       negative control: each control author as target (LOO + decoys from other authors) -> AUC

Usage: python src/score/validate.py
"""
import csv, json, sys, time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, mannwhitneyu
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C                      # noqa: E402
from features import Space              # noqa: E402
from gi import SEED, general_imposters, rng_for, centroid_ranks   # noqa: E402

OUT = C.ROOT / "results/validation/round2"
DECOYS_PER_AUTHOR, POS_SONNETS = 15, 30


class Runner:
    def __init__(self, texts):
        self.texts = texts
        self.spaces = {k: Space(k) for k in ("F1", "F2")}
        self.base = {}                           # author -> list of doc keys (no exclusions)
        self.docs = {}                           # doc key -> (author, tokens)
        groups = defaultdict(list)
        for t in texts:
            if t.role in ("target-oxford", "shakespeare", "control", "imposter"):
                groups[self.author_class(t)].append(t)
        self.groups = groups
        for a, ts in groups.items():
            self.base[a] = self.make_docs(a, ts, excluded=None)

    @staticmethod
    def author_class(t):
        return "pool" if t.role == "imposter" else t.author

    def make_docs(self, author, ts, excluded):
        keys = []
        for j, (_, vol, toks) in enumerate(C.chunk([t for t in ts if t.id != excluded], lambda t: author)):
            key = (author, excluded, vol, j)
            self.docs[key] = (author, toks)
            for sp in self.spaces.values():
                sp.row(key, toks)
            keys.append(key)
        return keys

    def docs_for(self, author, excluded=None):
        if excluded is None or excluded not in {t.id for t in self.groups[author]}:
            return self.base[author]
        cache_key = ("loo", author, excluded)
        if cache_key not in self.base:
            self.base[cache_key] = self.make_docs(author, self.groups[author], excluded)
        return self.base[cache_key]

    def score(self, test, target, kind):
        """GI score of test text against target author, open-set (test's own author removed from imposters)."""
        tkey = ("test", test.id)
        sp = self.spaces[kind]
        sp.row(tkey, test.tokens)
        own = self.author_class(test) if test.role in ("target-oxford", "shakespeare", "control", "imposter") else None
        tdocs = self.docs_for(target, excluded=test.id if own == target else None)
        imp = [k for a in self.groups if a != target and a != own for k in self.base[a]]
        ref = tdocs + imp
        R, v, _ = sp.build(ref, tkey)
        T, I = R[: len(tdocs)], R[len(tdocs):]
        s = general_imposters(v, T, I, rng_for(test.id, target, kind))
        top = centroid_ranks(v, R, [self.docs[k][0] for k in ref])[0]
        return s, top


def threshold(decoy_scores, fpr):
    d = np.asarray(decoy_scores)
    for s in sorted(set(np.round(np.append(d, 1.01), 2))):
        if np.mean(d >= s) <= fpr:
            return float(s)
    return 1.01


def ci(k, n):
    if n == 0:
        return (None, None)
    r = binomtest(k, n).proportion_ci(method="exact")
    return (round(r.low, 3), round(r.high, 3))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    texts = C.load()
    R = Runner(texts)
    byrole = defaultdict(list)
    for t in texts:
        byrole[t.role].append(t)
    controls = sorted({t.author for t in byrole["control"]})
    rng = np.random.default_rng(SEED)
    decoys = {}
    for a in controls:
        elig = sorted([t for t in byrole["control"] if t.author == a and t.n >= C.MIN_TEST], key=lambda t: t.id)
        pick = rng.choice(len(elig), min(DECOYS_PER_AUTHOR, len(elig)), replace=False)
        decoys[a] = [elig[i] for i in sorted(pick)]
    oxford_loo = [t for t in byrole["target-oxford"] if t.n >= C.MIN_TEST]
    venue = [t for t in byrole["venue-decoy"] if t.n >= C.MIN_TEST]
    son = sorted([t for t in byrole["shakespeare"] if t.id.startswith("shk-son") and t.n >= C.MIN_TEST], key=lambda t: t.id)
    pos = [son[i] for i in sorted(np.random.default_rng(SEED).choice(len(son), POS_SONNETS, replace=False))]
    pos += [t for t in byrole["shakespeare"] if t.id in ("shk-ven", "shk-luc", "shk-pt")]
    control_decoys = [t for a in controls for t in decoys[a]]

    rows = []
    def run(stage, target, tests, kind_label):
        for t in tests:
            for fs in ("F1", "F2"):
                s, top = R.score(t, target, fs)
                rows.append(dict(stage=stage, target=target, test_id=t.id, test_author=t.author, kind=kind_label,
                                 features=fs, score=s, n_tokens=t.n, nearest_centroid=top))

    run("S1", "Oxford", oxford_loo, "loo")
    run("S1", "Oxford", control_decoys, "decoy-control")
    run("S1", "Oxford", venue, "decoy-venue")
    print(f"stage 1 done ({time.time() - t0:.0f}s)")
    run("S2", "Shakespeare", pos, "loo")
    run("S2", "Shakespeare", control_decoys, "decoy-control")
    print(f"stage 2 controls done ({time.time() - t0:.0f}s)")
    for a in controls:
        run("NEG", a, decoys[a], "loo")
        run("NEG", a, [t for b in controls if b != a for t in decoys[b]], "decoy-control")
    print(f"negative controls done ({time.time() - t0:.0f}s)")

    with open(OUT / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    def sel(**kw):
        return [r["score"] for r in rows if all(r[k] == v for k, v in kw.items())]

    summary = {"seed": SEED, "n_texts": len(texts), "control_authors": controls,
               "decoys_per_author": {a: len(v) for a, v in decoys.items()}}
    for fs in ("F1", "F2"):
        loo = sel(stage="S1", kind="loo", features=fs)
        dc = sel(stage="S1", kind="decoy-control", features=fs)
        dv = sel(stage="S1", kind="decoy-venue", features=fs)
        th, th1 = threshold(dc + dv, 0.05), threshold(dc + dv, 0.01)
        k = sum(s >= th for s in loo); k1 = sum(s >= th1 for s in loo)
        s1 = dict(n_loo=len(loo), n_decoy_control=len(dc), n_decoy_venue=len(dv), theta=th, theta1=th1,
                  recall_theta=round(k / len(loo), 3), recall_theta_ci=ci(k, len(loo)),
                  recall_theta1=round(k1 / len(loo), 3), recall_theta1_ci=ci(k1, len(loo)),
                  auc_control=round(roc_auc_score([1] * len(loo) + [0] * len(dc), loo + dc), 3),
                  auc_venue=round(roc_auc_score([1] * len(loo) + [0] * len(dv), loo + dv), 3),
                  fpr_control_at_theta=round(float(np.mean(np.array(dc) >= th)), 3),
                  fpr_venue_at_theta=round(float(np.mean(np.array(dv) >= th)), 3),
                  underpowered=bool(k / len(loo) < 0.5))
        s1["venue_effect"] = bool(s1["fpr_venue_at_theta"] > 2 * max(s1["fpr_control_at_theta"], 1e-9))
        p = sel(stage="S2", kind="loo", features=fs)
        d2 = sel(stage="S2", kind="decoy-control", features=fs)
        ths = threshold(d2, 0.05)
        kp = sum(s >= ths for s in p)
        s2 = dict(theta_S=ths, n_pos=len(p), pos_rate=round(kp / len(p), 3), pos_ci=ci(kp, len(p)),
                  pos_pass=bool(kp / len(p) >= 0.6),
                  auc=round(roc_auc_score([1] * len(p) + [0] * len(d2), p + d2), 3))
        aucs = {}
        for a in controls:
            l = sel(stage="NEG", target=a, kind="loo", features=fs)
            d = sel(stage="NEG", target=a, kind="decoy-control", features=fs)
            aucs[a] = round(roc_auc_score([1] * len(l) + [0] * len(d), l + d), 3)
        neg = dict(auc_by_author=aucs, median_auc=round(float(np.median(list(aucs.values()))), 3))
        neg["pass"] = bool(neg["median_auc"] >= 0.75)
        summary[fs] = {"stage1": s1, "stage2_positive": s2, "negative_control": neg}
    summary["runtime_s"] = round(time.time() - t0)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({fs: summary[fs] for fs in ("F1", "F2")}, indent=1))


if __name__ == "__main__":
    main()
