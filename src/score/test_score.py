"""Unit tests for the scoring code on synthetic data. Run: python -m pytest src/score"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C                                   # noqa: E402
from features import Space                           # noqa: E402
from gi import general_imposters, rng_for, cosine_dist   # noqa: E402
from validate import threshold                       # noqa: E402


def test_tokenize():
    assert C.tokenize("O'er the Hills, 1593 & co’s") == ["o'er", "the", "hills", "co's"]


def test_chunk_rules():
    t1 = C.Text("a", "X", "V1", "control", ["w"] * 450)   # 200 + 200 + 50 (dropped)
    t2 = C.Text("b", "X", "V2", "control", ["w"] * 130)   # single short piece kept (>=100)
    t3 = C.Text("c", "X", "V3", "control", ["w"] * 52)    # alone in volume, <100: nothing
    docs = C.chunk([t1, t2, t3], lambda t: t.author)
    assert [len(d[2]) for d in docs] == [200, 200, 130]
    assert {d[1] for d in docs} == {"V1", "V2"}


def test_chunks_do_not_cross_volumes():
    t1 = C.Text("a", "X", "V1", "control", ["a"] * 150)
    t2 = C.Text("b", "X", "V2", "control", ["b"] * 150)
    docs = C.chunk([t1, t2], lambda t: t.author)
    assert all(len(set(d[2])) == 1 for d in docs)


def synthetic_author(rng, probs, n_docs, length=200):
    words = np.array([f"w{i}" for i in range(len(probs))])
    return [list(rng.choice(words, length, p=probs)) for _ in range(n_docs)]


def test_general_imposters_separates_authors():
    rng = np.random.default_rng(0)
    V = 60
    pa = rng.dirichlet(np.ones(V) * 0.5); pb = rng.dirichlet(np.ones(V) * 0.5); pc = rng.dirichlet(np.ones(V) * 0.5)
    A = synthetic_author(rng, pa, 12); B = synthetic_author(rng, pb, 12); Cc = synthetic_author(rng, pc, 12)
    test_a = synthetic_author(rng, pa, 1)[0]; test_c = synthetic_author(rng, pc, 1)[0]
    sp = Space("F1"); sp.vocab = {}; import features; features.N_FEATURES["F1"] = 40
    keys = []
    for name, docs in (("A", A), ("B", B), ("C", Cc)):
        for j, d in enumerate(docs):
            sp.row((name, j), d); keys.append((name, j))
    sp.row("ta", test_a); sp.row("tc", test_c)
    # same author scores high
    ref = [k for k in keys if k[0] in ("A", "B", "C")]
    Rm, v, _ = sp.build(ref, "ta")
    isA = np.array([k[0] == "A" for k in ref])
    s_same = general_imposters(v, Rm[isA], Rm[~isA], rng_for("ta"))
    # open-set: author C's docs removed, test by C against target A should score low
    ref2 = [k for k in keys if k[0] in ("A", "B")]
    Rm2, v2, _ = sp.build(ref2, "tc")
    isA2 = np.array([k[0] == "A" for k in ref2])
    s_other = general_imposters(v2, Rm2[isA2], Rm2[~isA2], rng_for("tc"))
    features.N_FEATURES["F1"] = 150
    assert s_same >= 0.9
    assert s_other <= 0.6
    assert s_same > s_other


def test_gi_deterministic():
    rng_data = np.random.default_rng(1)
    v, T, I = rng_data.normal(size=20), rng_data.normal(size=(5, 20)), rng_data.normal(size=(30, 20))
    assert general_imposters(v, T, I, rng_for("x", "y")) == general_imposters(v, T, I, rng_for("x", "y"))


def test_balanced_sampling_removes_count_bias():
    # a random test vector: target and imposters are equally unrelated, so a balanced score sits near 0.5
    r = np.random.default_rng(3)
    T, I = r.normal(size=(10, 40)), r.normal(size=(2000, 40))
    scores = [general_imposters(r.normal(size=40), T, I, rng_for("bal", i)) for i in range(40)]
    assert 0.3 < float(np.mean(scores)) < 0.7


def test_cosine_dist():
    M = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    assert np.allclose(cosine_dist(np.array([1.0, 0.0]), M), [0.0, 1.0, 2.0])


def test_threshold():
    decoys = [0.0] * 90 + [0.5] * 5 + [0.9] * 4 + [1.0] * 1
    assert threshold(decoys, 0.05) == 0.9      # P(decoy >= 0.9) = 5%
    assert threshold(decoys, 0.01) == 1.0      # P(decoy >= 1.0) = 1%
    assert threshold([1.0] * 10, 0.05) == 1.01 # impossible: every decoy maxes out
