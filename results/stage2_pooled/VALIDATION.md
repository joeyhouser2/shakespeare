# Pooled-sample validation (Amendment 2, A2.4), 2026-11-25: PASSED

Run: `python src/score/pooled.py validate`. Results in `validation.json`. The run took 39 s and used seed 20261122. **The main de Vere-vs-Shakespeare run has NOT been computed.** It is a separate command (`pooled.py main`).

The design was declared in PREREG Amendment 2, hashed at 2026-11-25T21:30:10Z, committed as `6d44cb3` and pushed before this code was written. Implementation choices the amendment left open were fixed in the `pooled.py` docstring before the run:
- V1 and V2 are judged on both half-swaps pooled together, and each run is also reported separately.
- Validation runs choose their features from the comparison authors plus Shakespeare only.

## Results (both runs pooled: 200 held-out 2,200-token samples per author)

| Check | F1: 150 MFW (decides) | F2: 300 char 3-grams | Criterion | Outcome |
|---|---|---|---|---|
| V1 AUC, held-out Shakespeare vs comparison authors | **0.984** | 0.976 | ≥ 0.90 | pass |
| V1 median D, Shakespeare vs nearest control median | 0.538 vs 0.919 (Sidney) | 0.555 vs 0.928 (Sidney) | lower than every control | pass |
| V2 macro accuracy, nearest of 12 profiles | **0.966** | 0.942 | ≥ 0.80 | pass |

V2 accuracy by author (F1):

| Author | Accuracy | | Author | Accuracy |
|---|---|---|---|---|
| Daniel | 1.00 | | Spenser | 0.875 |
| Drayton | 1.00 | | Sidney | 0.965 |
| Lodge | 0.90 | | Churchyard | 0.995 |
| Watson | 1.00 | | Turberville | 1.00 |
| Googe | 1.00 | | Gascoigne | 0.925 |
| Greville | 1.00 | | Shakespeare | 0.935 |

Comparison authors' median D to the held-out Shakespeare profile (F1): Sidney 0.92, Watson 0.98, Greville 0.98, Lodge 1.00, Daniel 1.02, Spenser 1.04, Drayton 1.07, Gascoigne 1.09, Turberville 1.09, Googe 1.11, Churchyard 1.19. In the 1590s or later is nearer; the 1560s–70s are further. That's the expected chronological gradient.

## Reading
- At 2,200 tokens, this feature set carries a strong author signal. Held-out Shakespeare samples are nearly perfectly separated from the controls. That contrasts with single poems (round 2 AUC 0.83, 27% recall).
- **The validation is likely optimistic for the main question.** Each split puts alternating poems from the same books into the two halves, so it tests recognition within a work or volume. De Vere's single sample has to be compared across books, printers and decades, and it can't be validated at all (V3). Topic and character names shared within a sequence (e.g. Daniel's *Delia*) may inflate V2.
- **The chronological gradient is a confound to keep in mind.** Control authors printed in the 1590s sit nearer to Shakespeare than the 1560s–70s authors do. De Vere's poems were mostly printed 1573–93, so period alone predicts an intermediate distance, regardless of authorship. The registered decision rule compares de Vere with **all** comparison authors, early and late; the early/late split is reported descriptively (A2.6).

## Status
Validation passed, so the main run is permitted under Amendment 2. Its decision rule is fixed (A2.5), and the result will be reported whichever way it falls.
