"""Unit tests for the spelling comparison on synthetic data only. Run: python -m pytest src/score"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spelling as S                                 # noqa: E402


def test_tokenize_folds_transcriber_conventions():
    assert S.tokenize_line("Loue, ioy and ſilence; yᵉ o'er-much") == ["loue", "ioy", "and", "silence", "ye", "oer", "much"]
    assert S.tokenize_line("love joy") == ["loue", "ioy"]


def test_tokenize_drops_editorial_and_damaged_words():
    assert S.tokenize_line("a lett[er] [two words] b <x>y cō 1593 w^• end") == ["a", "b", "end"]
    with pytest.raises(ValueError):
        S.tokenize_line("broken [bracket")


def test_to_pairs_excludes_and_rejects_unknown():
    forms = {"mee": "me", "x": None}
    assert S.to_pairs([["mee", "x"], ["mee"]], forms) == [("me", "mee", 0), ("me", "mee", 1)]
    with pytest.raises(KeyError):
        S.to_pairs([["unknown"]], forms)


def test_profile_sample_size_and_shortfall():
    docs = [[1] * 30, [2] * 30]
    assert len(S.profile_sample(docs, 45, np.random.default_rng(0))) == 45
    with pytest.raises(ValueError):
        S.profile_sample(docs, 61, np.random.default_rng(0))


def test_holdout_keeps_documents_apart():
    docs = [[i] * 20 for i in range(5)]
    held, rest = S.holdout_split(docs, 30, 40, np.random.default_rng(0))
    assert len(held) == 30
    assert not set(held) & {t for d in rest for t in d}
    assert S.holdout_split([[1] * 100], 10, 10, np.random.default_rng(0)) is None


WORDS = [f"w{i}" for i in range(20)]


def writer(rng, habit, n_docs=8, length=100):
    """habit[i] = probability this writer spells word i with a final e. Tokens: (standard, spelling, line)."""
    docs = []
    for _ in range(n_docs):
        d = []
        for j in range(length):
            i = int(rng.integers(len(WORDS)))
            d.append((WORDS[i], WORDS[i] + ("e" if rng.random() < habit[i] else ""), j // 10))
        docs.append(d)
    return docs


def synthetic():
    rng = np.random.default_rng(1)
    habits = {w: rng.beta(0.5, 0.5, len(WORDS)) for w in [S.OXFORD, "A", "B", "C"]}
    return rng, habits, {w: writer(rng, h) for w, h in habits.items()}


def test_true_writer_ranks_first_and_bootstrap_is_confident():
    rng, habits, corpus = synthetic()
    query = writer(rng, habits["B"], n_docs=1, length=200)[0]
    writers, M, info = S.log_ratios(corpus, query, 400, 10, ("test",))
    assert S.rank_of(writers, M.mean(axis=1), "B") == 1
    assert S.bootstrap_share(writers, M, info, "B", np.random.default_rng(0), n=200) > 0.95
    assert S.bootstrap_share(writers, M, info, "A", np.random.default_rng(0), n=200) < 0.05


def test_words_with_one_spelling_are_not_informative():
    corpus = {S.OXFORD: [[("the", "the", 0)] * 10], "A": [[("the", "the", 0)] * 10]}
    _, M, info = S.log_ratios(corpus, [("the", "the", 0)], 5, 2, ("t",))
    assert info == [] and M.shape == (2, 0)


def test_validation_passes_with_distinct_habits_and_fails_without():
    _, _, corpus = synthetic()
    good = S.validate(corpus, 150, size=400, trials=5, draws=3)
    assert good["pass"]
    rng = np.random.default_rng(2)
    same = np.full(len(WORDS), 0.5)
    bad = S.validate({w: writer(rng, same) for w in corpus}, 150, size=400, trials=10, draws=3)
    assert not bad["pass"]


def test_rank_ties_count_against_target():
    assert S.rank_of(["a", "b"], np.array([1.0, 1.0]), "a") == 2


def test_decision_rule():
    assert S.decide(9, 500, 1, 1.0).startswith("inconclusive (too little")
    assert S.decide(25, 199, 1, 1.0).startswith("inconclusive (too little")
    assert S.decide(19, 500, 1, 0.95).startswith("H3a")
    assert S.decide(18, 500, 1, 1.0) == "inconclusive"          # too few controls to claim 'closer'
    assert S.decide(25, 500, 1, 0.94) == "inconclusive"
    assert S.decide(20, 500, 11, 0.0) == "inconclusive"         # exact middle of 21 writers
    assert S.decide(20, 500, 12, 0.0).startswith("H3b")
    assert S.decide(11, 500, 7, 0.0).startswith("H3b")          # 12 writers, bottom half starts at rank 7
    assert S.decide(11, 500, 6, 0.0) == "inconclusive"


def test_spelling_variables():
    toks = [("silence", "scilens", 0), ("me", "mee", 0), ("city", "citie", 0), ("man", "manne", 0)]
    r = S.variable_rates(toks)
    assert r["sc_for_s"] == (1, 1)
    assert r["final_y_as_ie"] == (1, 1)
    assert r["doubled_e_or_o"][0] == 1
    assert r["added_final_e"][0] == 1
    assert S.variable_distance(r, r) == (None, 0)               # too few opportunities to compare
    many = S.variable_rates(toks * 5)
    assert S.variable_distance(many, many)[0] == 0
