"""General Imposters (Koppel & Winter 2014; Kestemont et al. 2016) with cosine distance
on z-scored features (Cosine Delta). results/PREREG.md 4.1.
"""
import zlib
import numpy as np

SEED = 20261122
ITERATIONS, FEATURE_FRAC = 100, 0.5
# Round 2 (PREREG 4.1): each iteration samples as many imposter docs as the target has docs.


def rng_for(*parts):
    """Deterministic generator per test, independent of run order."""
    return np.random.default_rng([SEED] + [zlib.crc32(str(p).encode()) for p in parts])


def cosine_dist(v, M):
    nv = np.linalg.norm(v)
    nm = np.linalg.norm(M, axis=1)
    denom = nv * nm
    denom[denom == 0] = 1e-12
    return 1.0 - (M @ v) / denom


def general_imposters(test, target, imposters, rng, iterations=ITERATIONS):
    """Share of iterations where test is closer to its nearest target doc than to its nearest imposter doc.
    Balanced: each iteration compares against as many imposter docs as there are target docs."""
    nf = test.shape[0]
    k_f = max(1, int(round(nf * FEATURE_FRAC)))
    k_i = min(target.shape[0], imposters.shape[0])
    wins = 0
    for _ in range(iterations):
        f = rng.choice(nf, k_f, replace=False)
        imp = imposters[rng.choice(imposters.shape[0], k_i, replace=False)][:, f]
        dt = cosine_dist(test[f], target[:, f]).min()
        di = cosine_dist(test[f], imp).min()
        wins += dt < di
    return wins / iterations


def centroid_ranks(test, docs, authors):
    """Closed-set Cosine Delta: authors ranked by distance from test to their centroid (PREREG 4.2)."""
    names = sorted(set(authors))
    a = np.array(authors)
    cents = np.vstack([docs[a == n].mean(axis=0) for n in names])
    d = cosine_dist(test, cents)
    return [names[i] for i in np.argsort(d)]
