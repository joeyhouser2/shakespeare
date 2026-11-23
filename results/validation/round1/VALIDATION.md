# Validation round 1 (2026-11-22): FAILED as designed

The method is the one in PREREG sections 3–5 as drafted (GI, cosine distance, 100 iterations, 50% of features, 50% of imposters, open-set). The code is `src/score/` at the commit that adds this folder. **No candidate was scored, and de Vere was not scored against Shakespeare.**

## Results (F1 = 150 most frequent words; F2 = character 3-grams)

| Check | F1 | F2 | Criterion | Outcome |
|---|---|---|---|---|
| Stage 1 θ (FPR ≤ 5%, 240 decoys) | 0.11 | 0.07 | – | |
| de Vere leave-one-out recall at θ (n = 11) | **0.00** (CI 0–0.29) | 0.27 (0.06–0.61) | ≥ 0.50 | **underpowered** |
| de Vere vs control decoys, AUC | 0.54 | 0.56 | – | about chance |
| Same-venue (*Paradise*) decoys at θ | 9.6% vs 2.7% for controls | 9.6% vs 3.2% | ≤ 2× control rate | **venue effect** |
| Stage 2 θ_S (FPR ≤ 5%) | 0.49 | 0.59 | – | |
| Shakespeare positive control at θ_S (n = 33) | **0.21** (CI 0.09–0.39) | 0.33 (0.18–0.52) | ≥ 0.60 | **fail** |
| Shakespeare vs control decoys, AUC | 0.81 | 0.77 | – | |
| Negative control, median AUC (13 authors) | 0.81 | 0.84 | ≥ 0.75 | pass |

## Diagnosis
- **De Vere's held-out poems almost never win a GI round.** Their scores were 0.00–0.08. Only 1 of 11 had de Vere as its nearest author centroid.
- **AUC rises with the target's reference size** (Spearman ρ = 0.50 across 14 authors). The three smallest (de Vere at 2,246 tokens, Vaux 2,802, Edwards 2,835) are the three worst (AUC 0.54–0.66).
- **Structural cause:** the GI score compares the test text's *nearest* target document with its *nearest* imposter document. De Vere has 11 reference documents; each iteration samples about 1,250 imposter documents. The minimum distance over 1,250 random texts is almost always smaller than over 11, almost regardless of style. So the score as implemented largely measures the target's document count. The same imbalance, milder (about 200 target documents), explains the failed Shakespeare positive control, given AUC 0.81.
- **Venue effect:** other poets in the 1576 *Paradise* score closer to de Vere than control poets do. Shared printer, date and anthology conventions are a confound for any *Paradise*-heavy reference set. Seven of de Vere's 12 core poems come from that volume.

## Status
Under the drafted rules, Stage 1 would be **underpowered** (leads exploratory only) and Stage 2 **inconclusive** (positive control failed). The thresholds above are recorded but not adopted. Whether to lock with these outcomes or run one documented redesign is the project owner's decision. See PREREG "Validation history".
