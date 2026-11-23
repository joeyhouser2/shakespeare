"""Feature spaces (results/PREREG.md 3.5): most frequent words (F1) and character 3-grams (F2).

Features are ranked over the reference documents of the current run only (test item excluded),
then relative frequencies are z-scored with the reference documents' means and SDs.
"""
from collections import Counter
import numpy as np
from scipy import sparse

N_FEATURES = {"F1": 150, "F2": 300}


def units(tokens, kind):
    if kind == "F1":
        return tokens
    s = " " + " ".join(tokens) + " "
    return [s[i:i + 3] for i in range(len(s) - 2)]


class Space:
    """Caches each document's sparse count row so runs can be assembled cheaply."""

    def __init__(self, kind):
        self.kind, self.vocab, self.cache = kind, {}, {}

    def row(self, key, tokens):
        if key not in self.cache:
            c = Counter(units(tokens, self.kind))
            idx = [self.vocab.setdefault(u, len(self.vocab)) for u in c]
            self.cache[key] = (np.array(idx, dtype=np.int64), np.array(list(c.values()), dtype=np.float64), sum(c.values()))
        return self.cache[key]

    def matrix(self, keys):
        rows = [self.cache[k] for k in keys]
        ind = np.concatenate([r[0] for r in rows]) if rows else np.zeros(0, dtype=np.int64)
        dat = np.concatenate([r[1] for r in rows]) if rows else np.zeros(0)
        ptr = np.cumsum([0] + [len(r[0]) for r in rows])
        tot = np.array([r[2] for r in rows], dtype=np.float64)
        return sparse.csr_matrix((dat, ind, ptr), shape=(len(rows), len(self.vocab))), tot

    def build(self, ref_keys, test_key):
        """Return z-scored dense matrices (ref, test) over the top-N features of the reference docs."""
        R, rtot = self.matrix(ref_keys)
        T, ttot = self.matrix([test_key])
        R.resize(R.shape[0], len(self.vocab)); T.resize(1, len(self.vocab))
        colsum = np.asarray(R.sum(axis=0)).ravel()
        n = N_FEATURES[self.kind]
        inv = {i: u for u, i in self.vocab.items()}
        # top-N by frequency, ties broken alphabetically for determinism
        cand = np.argsort(-colsum, kind="stable")[: n * 3]
        cand = sorted(cand, key=lambda i: (-colsum[i], inv[i]))[:n]
        cand = np.array(cand)
        Rf = R[:, cand].toarray() / rtot[:, None]
        Tf = T[:, cand].toarray() / ttot[:, None]
        mu, sd = Rf.mean(axis=0), Rf.std(axis=0)
        sd[sd == 0] = 1.0
        return (Rf - mu) / sd, ((Tf - mu) / sd)[0], [inv[i] for i in cand]
