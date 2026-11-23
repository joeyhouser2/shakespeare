# Validation round 2 (2026-11-22): FAILED, final

The one change from round 1 is balanced imposter sampling: each iteration draws as many imposter documents as the target has. It was declared in PREREG before running; see `prereg_declared.sha256` (2026-11-23T03:49:29Z UTC) and `PREREG_as_declared.md`. Everything else is unchanged. **No candidate was scored, and de Vere was not scored against Shakespeare.**

## Results

| Check | F1 (decides) | F2 | Criterion | Outcome |
|---|---|---|---|---|
| Stage 1 θ / θ₁ (FPR ≤ 5% / 1%, 240 decoys) | 0.83 / 0.95 | 0.88 / 0.94 | – | |
| de Vere leave-one-out recall at θ (n = 11) | **0.09** (1/11; CI 0.00–0.41) | 0.09 | ≥ 0.50 | **underpowered** |
| de Vere vs control decoys, AUC | 0.62 | 0.49 | – | weak / chance |
| Same-venue (*Paradise*) decoys at θ | 13.5% vs 1.6% for controls | 5.8% vs 4.8% | ≤ 2× | **venue effect (F1)** |
| Stage 2 θ_S | 0.80 | 0.87 | – | |
| Shakespeare positive control at θ_S (n = 33) | **0.27** (CI 0.13–0.46) | 0.33 | ≥ 0.60 | **fail** |
| Shakespeare vs control decoys, AUC | 0.83 | 0.79 | – | |
| Negative control, median AUC (13 authors) | 0.85 | 0.88 | ≥ 0.75 | pass |
| Spearman (reference size, AUC), reported only | 0.51 (round 1: 0.50) | 0.53 | – | |

**De Vere's leave-one-out scores (F1):** No. 1 0.71; No. 2 0.87; No. 3 0.60; No. 4 0.50; No. 5 0.57; No. 7 0.25; No. 8 0.66; No. 9 0.54; No. 10 0.59; No. 11 0.77; No. 14 0.44. The control decoys average 0.51 (SD 0.19).

## Reading
- **Balanced sampling fixed the scale artefact.** A random text now scores about 0.5. It also improved the small control authors: Vaux 0.59 → 0.68, Edwards 0.66 → 0.76, and the median negative-control AUC rose from 0.81 to 0.85.
- **The correlation between reference size and accuracy did not fall** (ρ about 0.5). What remains looks like a genuine small-sample limit, not an artefact.
- **De Vere's held-out poems score only a little above unrelated poets.** With about 2,250 reference tokens and test poems of 100–300 tokens, the method cannot tell de Vere's poems apart from other poets' at a useful error rate.
- **Shakespeare:** held-out poems are distinguishable from controls on average (AUC 0.83). But at a 5% false-positive threshold only 27% are recovered, below the 60% criterion. Most test sonnets are only about 116 tokens long.
- **The *Paradise* venue effect persists in F1:** other 1576 *Paradise* poets reach θ at more than 8 times the control rate.

## Outcome under the pre-registered rules (round 2 final; no round 3)
- **Stage 1: UNDERPOWERED.** Any lead from candidate scoring is exploratory only, with no ranking claims. *Paradise*-derived similarity is a known confound.
- **Stage 2: INCONCLUSIVE** (positive control failed). The registered H2 test is not interpretable and is reported as such.
- **Thresholds recorded** (F1): θ = 0.83, θ₁ = 0.95, θ_S = 0.80.
