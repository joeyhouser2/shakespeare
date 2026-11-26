"""Pooled-sample analysis: de Vere vs Shakespeare (results/PREREG.md, Amendment 2).

    python src/score/pooled.py validate   # A2.4 split-half validation only -> results/stage2_pooled/validation.json
    python src/score/pooled.py main       # A2.5/A2.6 main run; refuses to run without validation.json

Implementation choices fixed before any result was computed:
  - Validation: V1 and V2 are judged on BOTH half-swap runs pooled (200 held-out samples per
    author); each run is also reported separately.
  - Feature list: the 150 MFW (300 char 3-grams for F2) over all tokens of the texts in the run.
    Validation runs use the comparison authors + Shakespeare (de Vere takes no part in validation);
    the main run adds de Vere's core poems, as A2.3 states.
  - z-scaling: mean/SD over all control + Shakespeare samples in the run (de Vere/LC/jackknife excluded).
  - Jackknife samples: remaining 11 poems in May order, cut to at most S tokens.
"""
import json, sys, zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C                       # noqa: E402
from features import units               # noqa: E402

SEED, S, B = 20261122, 2200, 100
N_FEAT = {"F1": 150, "F2": 300}
COMPARISON = ["Daniel", "Drayton", "Lodge", "Watson", "Googe", "Greville", "Spenser", "Sidney",
              "Churchyard", "Turberville", "Gascoigne"]
SMALL = ["Vaux", "Edwards"]
EARLY = ["Googe", "Turberville", "Gascoigne", "Churchyard", "Watson"]
LATE = ["Sidney", "Lodge", "Daniel", "Drayton"]
OUT = C.ROOT / "results/stage2_pooled"


def rng_for(*parts):
    return np.random.default_rng([SEED] + [zlib.crc32(str(p).encode()) for p in parts])


def draw_sample(texts, size, rng):
    """Whole poems in random order until `size` tokens; a poem longer than the remaining need
    contributes a contiguous random window of exactly that need (A2.2)."""
    if sum(len(t) for t in texts) < size:
        raise ValueError("not enough text for one sample")
    out = []
    for i in rng.permutation(len(texts)):
        need = size - len(out)
        toks = texts[i]
        if len(toks) <= need:
            out.extend(toks)
        else:
            start = int(rng.integers(0, len(toks) - need + 1))
            out.extend(toks[start:start + need])
        if len(out) == size:
            break
    return out


def split_halves(author, texts):
    """Alternating poems in corpus order; Shakespeare: Venus -> A, Lucrece + Phoenix -> B (A2.4)."""
    if author == "Shakespeare":
        son = [t for t in texts if t.id.startswith("shk-son")]
        A = [t for t in son[0::2]] + [t for t in texts if t.id == "shk-ven"]
        Bh = [t for t in son[1::2]] + [t for t in texts if t.id in ("shk-luc", "shk-pt")]
        return A, Bh
    return texts[0::2], texts[1::2]


class Space:
    def __init__(self, kind, token_lists):
        c = Counter()
        for toks in token_lists:
            c.update(units(toks, kind))
        self.kind = kind
        self.feats = [u for u, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:N_FEAT[kind]]]
        self.index = {u: i for i, u in enumerate(self.feats)}

    def vec(self, toks):
        us = units(toks, self.kind)
        v = np.zeros(len(self.feats))
        for u in us:
            j = self.index.get(u)
            if j is not None:
                v[j] += 1
        return v / max(1, len(us))


def cosine_dist(a, M):
    M = np.atleast_2d(M)
    return 1 - (M @ a) / (np.linalg.norm(M, axis=1) * np.linalg.norm(a) + 1e-12)


def zscaler(rows):
    X = np.vstack(rows)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd[sd == 0] = 1.0
    return lambda v: (v - mu) / sd


def load_groups():
    texts = C.load()
    g = defaultdict(list)
    for t in texts:
        if t.role == "control" and t.author in COMPARISON + SMALL:
            g[t.author].append(t)
        elif t.role == "shakespeare":
            g["Shakespeare"].append(t)
        elif t.role == "target-oxford":
            g["Oxford"].append(t)
        elif t.role == "shakespeare-extra":
            g["LC"].append(t)
    order = {i: k for k, i in enumerate(C.OXFORD_CORE)}
    g["Oxford"].sort(key=lambda t: order[t.id])
    return g


def validate():
    g = load_groups()
    authors = COMPARISON + ["Shakespeare"]
    halves = {a: split_halves(a, g[a]) for a in authors}
    for a, (h1, h2) in halves.items():
        for h in (h1, h2):
            if sum(t.n for t in h) < S:
                raise SystemExit(f"{a}: a half has fewer than {S} tokens")
    res = {"S": S, "B": B, "runs": {}}
    pooled = {fs: {"d_shk": [], "d_ctrl": [], "med": defaultdict(list), "correct": defaultdict(list)} for fs in N_FEAT}
    for run, (pi, ti) in (("A_profile_B_test", (0, 1)), ("B_profile_A_test", (1, 0))):
        prof_s = {a: [draw_sample([t.tokens for t in halves[a][pi]], S, rng_for("val", run, "profile", a, b)) for b in range(B)] for a in authors}
        test_s = {a: [draw_sample([t.tokens for t in halves[a][ti]], S, rng_for("val", run, "test", a, b)) for b in range(B)] for a in authors}
        res["runs"][run] = {}
        for fs in N_FEAT:
            sp = Space(fs, [t.tokens for a in authors for t in g[a]])
            P = {a: [sp.vec(x) for x in prof_s[a]] for a in authors}
            T = {a: [sp.vec(x) for x in test_s[a]] for a in authors}
            z = zscaler([v for a in authors for v in P[a] + T[a]])
            prof = {a: np.mean([z(v) for v in P[a]], axis=0) for a in authors}
            names = list(prof)
            PM = np.vstack([prof[a] for a in names])
            d_shk = [float(cosine_dist(z(v), prof["Shakespeare"])[0]) for v in T["Shakespeare"]]
            d_ctrl, med, acc = [], {}, {}
            for a in authors:
                ds = [float(cosine_dist(z(v), prof["Shakespeare"])[0]) for v in T[a]]
                med[a] = float(np.median(ds))
                if a != "Shakespeare":
                    d_ctrl += ds
                pred = [names[int(np.argmin(cosine_dist(z(v), PM)))] for v in T[a]]
                acc[a] = float(np.mean([p == a for p in pred]))
                pooled[fs]["med"][a] += ds
                pooled[fs]["correct"][a] += [p == a for p in pred]
            pooled[fs]["d_shk"] += d_shk; pooled[fs]["d_ctrl"] += d_ctrl
            auc = roc_auc_score([1] * len(d_shk) + [0] * len(d_ctrl), [-d for d in d_shk + d_ctrl])
            res["runs"][run][fs] = dict(V1_auc=round(auc, 3), V1_median_shk=round(med["Shakespeare"], 4),
                                        V1_min_ctrl_median=round(min(m for a, m in med.items() if a != "Shakespeare"), 4),
                                        V2_acc_by_author={a: round(x, 3) for a, x in acc.items()},
                                        V2_macro=round(float(np.mean(list(acc.values()))), 3))
        print(f"{run} done")
    res["pooled"] = {}
    for fs in N_FEAT:
        p = pooled[fs]
        auc = roc_auc_score([1] * len(p["d_shk"]) + [0] * len(p["d_ctrl"]), [-d for d in p["d_shk"] + p["d_ctrl"]])
        meds = {a: float(np.median(v)) for a, v in p["med"].items()}
        accs = {a: float(np.mean(v)) for a, v in p["correct"].items()}
        v1 = bool(auc >= 0.90 and meds["Shakespeare"] < min(m for a, m in meds.items() if a != "Shakespeare"))
        v2 = bool(np.mean(list(accs.values())) >= 0.80)
        res["pooled"][fs] = dict(V1_auc=round(auc, 3), V1_median_shk=round(meds["Shakespeare"], 4),
                                 V1_ctrl_medians={a: round(m, 4) for a, m in meds.items() if a != "Shakespeare"},
                                 V1_pass=v1, V2_acc_by_author={a: round(x, 3) for a, x in accs.items()},
                                 V2_macro=round(float(np.mean(list(accs.values()))), 3), V2_pass=v2)
    res["decision_features"] = "F1"
    res["validation_pass"] = bool(res["pooled"]["F1"]["V1_pass"] and res["pooled"]["F1"]["V2_pass"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "validation.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps(res["pooled"], indent=1)); print("VALIDATION PASS (F1):", res["validation_pass"])


def main_run():
    vfile = OUT / "validation.json"
    if not vfile.exists():
        raise SystemExit("Run `pooled.py validate` first (Amendment 2: validation before the main run).")
    val = json.loads(vfile.read_text(encoding="utf-8"))
    g = load_groups()
    samples = {a: [draw_sample([t.tokens for t in g[a]], S, rng_for("main", a, b)) for b in range(B)]
               for a in COMPARISON + SMALL + ["Shakespeare"]}
    dv_all = [tok for t in g["Oxford"] for tok in t.tokens]
    devere = dv_all[:S]
    lc = [tok for t in g["LC"] for tok in t.tokens][:S]
    jack = {t.id: [tok for u in g["Oxford"] if u.id != t.id for tok in u.tokens][:S] for t in g["Oxford"]}
    out = {"validation_pass": val["validation_pass"], "devere_tokens": len(devere)}
    for fs in N_FEAT:
        sp = Space(fs, [t.tokens for a in COMPARISON + ["Shakespeare"] for t in g[a]] + [dv_all])
        V = {a: [sp.vec(x) for x in xs] for a, xs in samples.items()}
        z = zscaler([v for a in COMPARISON + ["Shakespeare"] for v in V[a]])
        prof = np.mean([z(v) for v in V["Shakespeare"]], axis=0)
        D = lambda toks: float(cosine_dist(z(sp.vec(toks)), prof)[0])
        Dc = {a: [float(cosine_dist(z(v), prof)[0]) for v in V[a]] for a in COMPARISON + SMALL}
        m = {a: float(np.median(Dc[a])) for a in COMPARISON}
        Ppool = [d for a in COMPARISON for d in Dc[a]]
        d_dv = D(devere)
        h2a = bool(d_dv < min(m.values()) and d_dv < np.percentile(Ppool, 5))
        h2b = bool(d_dv >= np.median(list(m.values())))
        out[fs] = dict(D_devere=round(d_dv, 4), comparison_medians={a: round(x, 4) for a, x in m.items()},
                       min_comparison_median=round(min(m.values()), 4), median_of_medians=round(float(np.median(list(m.values()))), 4),
                       p5_pooled=round(float(np.percentile(Ppool, 5)), 4),
                       devere_rank_among_control_samples=int(sum(d < d_dv for d in Ppool)) + 1, n_control_samples=len(Ppool),
                       shakespeare_sample_median=round(float(np.median([float(cosine_dist(z(v), prof)[0]) for v in V["Shakespeare"]])), 4),
                       small_author_medians={a: round(float(np.median(Dc[a])), 4) for a in SMALL},
                       D_lovers_complaint=round(D(lc), 4),
                       early_median=round(float(np.median([d for a in EARLY for d in Dc[a]])), 4),
                       late_median=round(float(np.median([d for a in LATE for d in Dc[a]])), 4),
                       jackknife={k: dict(D=round(D(v), 4), tokens=len(v)) for k, v in jack.items()},
                       H2a_pooled=h2a, H2b_pooled=h2b)
    f1 = out["F1"]
    out["outcome"] = ("INCONCLUSIVE (validation failed)" if not val["validation_pass"] else
                      "H2a-pooled supported" if f1["H2a_pooled"] else "H2b-pooled supported" if f1["H2b_pooled"] else "INCONCLUSIVE")
    (OUT / "main.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "validate":
        validate()
    elif cmd == "main":
        main_run()
    else:
        raise SystemExit(__doc__)
