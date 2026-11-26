"""Tests for the pooled-sample rules (PREREG Amendment 2). Run: python -m pytest src/score"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pooled import draw_sample, rng_for, split_halves   # noqa: E402
import corpus as C                                      # noqa: E402


def test_sample_exact_length_and_whole_poems():
    poems = [[f"a{i}"] * 300 for i in range(10)]
    s = draw_sample(poems, 1000, rng_for("t"))
    assert len(s) == 1000
    # first three poems whole (300 each), last a 100-token window of one poem
    words = [w for w in dict.fromkeys(s)]
    assert len(words) == 4


def test_long_poem_contributes_contiguous_window():
    poem = [f"w{i}" for i in range(5000)]
    s = draw_sample([poem], 2200, rng_for("long"))
    start = int(s[0][1:])
    assert s == [f"w{i}" for i in range(start, start + 2200)]


def test_deterministic():
    poems = [[f"p{i}_{j}" for j in range(150)] for i in range(40)]
    assert draw_sample(poems, 2200, rng_for("x", 1)) == draw_sample(poems, 2200, rng_for("x", 1))
    assert draw_sample(poems, 2200, rng_for("x", 1)) != draw_sample(poems, 2200, rng_for("x", 2))


def test_insufficient_text_raises():
    with pytest.raises(ValueError):
        draw_sample([["a"] * 100], 2200, rng_for("short"))


def test_split_halves_alternate_and_shakespeare_rule():
    ts = [C.Text(f"t{i}", "X", "V", "control", ["w"]) for i in range(5)]
    a, b = split_halves("X", ts)
    assert [t.id for t in a] == ["t0", "t2", "t4"] and [t.id for t in b] == ["t1", "t3"]
    shk = [C.Text(f"shk-son-{i:03d}", "Shakespeare", "V", "shakespeare", ["w"]) for i in range(1, 5)]
    shk += [C.Text(i, "Shakespeare", "V", "shakespeare", ["w"]) for i in ("shk-ven", "shk-luc", "shk-pt")]
    A, Bh = split_halves("Shakespeare", shk)
    assert "shk-ven" in [t.id for t in A] and {"shk-luc", "shk-pt"} <= {t.id for t in Bh}
    assert {t.id for t in A} & {t.id for t in Bh} == set()
