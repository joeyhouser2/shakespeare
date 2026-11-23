"""Load the analysis corpus and build reference documents (results/PREREG.md sections 2-3).

Every text is read from the MorphAdorner layer (data/reference/text/norm_ma/).
"""
import csv, re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT = "data/reference/text/"
CHUNK, MIN_LAST, MIN_TEST, AUTHOR_MIN = 200, 100, 100, 2000

OXFORD_CORE = ["oxf-p-01", "oxf-p-02", "oxf-p-03", "oxf-p-04", "oxf-p-05", "oxf-p-07", "oxf-p-08",
               "oxf-p-09", "oxf-p-10", "oxf-p-11", "oxf-p-14", "oxf-p-16"]
OXFORD_CONTESTED = ["oxf-p-06", "oxf-p-15"]
OXFORD_POSSIBLE = ["oxf-p-III"]
SHAKESPEARE_EXCLUDED_FROM_TARGET = {"shk-lc"}
PARADISE = "A21161"
PARADISE_REFERENCE_SIG = re.compile(r"E\.\s*O|Vaux|Ʋ|^L\.\s*V|Edward", re.I)

TOKEN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*")


def tokenize(text):
    return TOKEN.findall(text.lower().replace("’", "'"))


@dataclass
class Text:
    id: str
    author: str
    volume: str
    role: str                      # target-oxford | contested | possible | control | imposter | shakespeare | shakespeare-extra | venue-decoy
    tokens: list = field(repr=False)

    @property
    def n(self):
        return len(self.tokens)


def norm_ma(path):
    return ROOT / (TEXT + "norm_ma/" + path[len(TEXT):])


def volume_of(path):
    m = re.search(r"/orig/(A\d{5})/", path)
    return m.group(1) if m else Path(path).stem      # special/edited texts are their own volume


def load():
    texts = []
    man = list(csv.DictReader(open(ROOT / "data/reference/manifest.csv", encoding="utf-8")))
    byid = {r["item_id"]: r for r in man}
    for ids, role in ((OXFORD_CORE, "target-oxford"), (OXFORD_CONTESTED, "contested"), (OXFORD_POSSIBLE, "possible")):
        for i in ids:
            p = byid[i]["orig_text_path"]
            texts.append(Text(i, "Oxford", volume_of(p), role, tokenize(norm_ma(p).read_text(encoding="utf-8"))))
    for r in man:
        if r["author"] == "Shakespeare" and r["orig_text_path"]:
            role = "shakespeare-extra" if r["item_id"] in SHAKESPEARE_EXCLUDED_FROM_TARGET else "shakespeare"
            texts.append(Text(r["item_id"], "Shakespeare", volume_of(r["orig_text_path"]), role,
                              tokenize(norm_ma(r["orig_text_path"]).read_text(encoding="utf-8"))))
    items = [r for r in csv.DictReader(open(ROOT / "data/reference/text/items.csv", encoding="utf-8")) if r["include"] == "1"]
    for r in items:
        texts.append(Text(r["poem_id"], r["author"] if r["role"] == "control" else "pool", r["tcp_id"], r["role"],
                          tokenize(norm_ma(r["path"]).read_text(encoding="utf-8"))))
    # authors below the minimum go to the imposter pool (PREREG 3.4)
    size = defaultdict(int)
    for t in texts:
        if t.role == "control":
            size[t.author] += t.n
    for t in texts:
        if t.role == "control" and size[t.author] < AUTHOR_MIN:
            t.role = "imposter"
    # same-venue decoys: Paradise 1576 poems signed by other authors (PREREG 2.5)
    # (any poem linked to an Oxford manifest row, e.g. contested No. 6 signed "M.B.", is never a decoy)
    oxford_paths = {r["orig_text_path"] for r in man if r["author"] == "Oxford" and r["orig_text_path"]}
    for r in csv.DictReader(open(ROOT / "data/reference/text/tcp_poems.csv", encoding="utf-8")):
        if r["path"] in oxford_paths:
            continue
        if r["tcp_id"] == PARADISE and r["signed"].strip() and not PARADISE_REFERENCE_SIG.search(r["signed"]):
            texts.append(Text(r["poem_id"], "venue:" + re.sub(r"\W+", "", r["signed"])[:12], PARADISE, "venue-decoy",
                              tokenize(norm_ma(r["path"]).read_text(encoding="utf-8"))))
    return texts


def chunk(texts, author_key):
    """Cut texts (in corpus order) into CHUNK-token documents per (author_key, volume).
    The last piece of each volume is kept if it has at least MIN_LAST tokens."""
    groups, order = defaultdict(list), []
    for t in texts:
        k = (author_key(t), t.volume)
        if k not in groups:
            order.append(k)
        groups[k].extend(t.tokens)
    docs = []
    for k in order:
        toks = groups[k]
        for i in range(0, len(toks), CHUNK):
            piece = toks[i:i + CHUNK]
            if len(piece) == CHUNK or len(piece) >= MIN_LAST:
                docs.append((k[0], k[1], piece))
    return docs
