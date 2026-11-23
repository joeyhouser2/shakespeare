"""Tests for the normalization rules (data/reference/NORMALIZATION.md). Run: python -m pytest src/normalize"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize_text as n  # noqa: E402


def test_long_s_and_w():
    assert n("ſweete") == "sweete"
    assert n("VVHat cunnnig") == "What cunnnig"
    assert n("UUhat knot") == "What knot"


def test_accent_e():
    assert n("thée mée sée") == "thee me see"
    assert n("it shall bée so") == "it shall be so"


def test_drop_cap():
    assert n("FRaud is the front") == "Fraud is the front"
    assert n("THe liuely Larke") == "The lively Larke"
    assert n("TThy guift") == "Thy guift"


def test_superscripts():
    assert n("yᵗ on yᵉ earth") == "that on the earth"
    assert n("wᵗ teares") == "with teares"
    assert n("ye howling hounds") == "ye howling hounds"  # real pronoun untouched
    assert n("y^• way") == "the way"
    assert n("y^• they") == "that they"
    assert n("y^• hath") == "that hath"
    assert n("Y^• face") == "The face"


def test_macron():
    assert n("cōmaund") == "commaund"
    assert n("thē") == "then"


def test_symbols():
    assert n("sprites & powers") == "sprites and powers"
    assert n("Os rabidum &c.") == "Os rabidum etc."


def test_u_v():
    assert n("loue euer haue giue") == "love ever have give"
    assert n("vnto vp vse") == "unto up use"
    assert n("true queene vertue") == "true queene vertue"  # u after consonant, qu, initial v+vowel
    assert n("serue deserue") == "serve deserve"
    assert n("very vaine") == "very vaine"


def test_i_j():
    assert n("ioy Ioue iust") == "joy Jove just"
    assert n("I am in it") == "I am in it"


def test_lexicon_and_case():
    assert n("Mee thinkes hee") == "Me thinkes he"
    assert n("hir owne") == "her own"


def test_bee_doe_context():
    assert n("Then doeth the Bee") == "Then doeth the Bee"
    assert n("it shall bee so") == "it shall be so"
    assert n("I doe not") == "I do not"


def test_line_breaks_kept():
    assert n("a\nb\n\nc") == "a\nb\n\nc"
