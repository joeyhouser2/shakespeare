# Pooled de Vere sample vs Shakespeare: main result (Amendment 2), 2026-11-26

**Registered outcome: H2b-pooled SUPPORTED. De Vere's pooled sample is no closer to Shakespeare's non-dramatic verse than the period control poets are.** Both feature sets agree.

Run: `python src/score/pooled.py main` (seed 20261122). Full output: `main.json`.
- Design: PREREG Amendment 2 (hashed 2026-11-25T21:30:10Z; committed and pushed as `6d44cb3` before any code).
- Validation: passed first (`VALIDATION.md`; V1 AUC 0.984, V2 accuracy 0.966).
- The Stage 2 single-poem outcome stays **inconclusive**. This is a separate analysis.

## Decision (F1: 150 MFW, Cosine Delta to the Shakespeare profile; lower = closer)
| Quantity | Value |
|---|---|
| **D(de Vere)**, 12 core poems as one 2,200-token sample | **1.133** |
| Nearest comparison author's median (Sidney) | 0.916 |
| Median of the 11 comparison-author medians | 1.029 |
| 5th percentile of all 1,100 comparison samples | 0.876 |
| De Vere's rank among 1,100 comparison samples (1 = nearest) | **868**: further than about 79% of control samples |
| Shakespeare's own samples, median D to his profile (reference) | 0.380 |

- **H2a-pooled** (D < 0.916 and D < 0.876): **not met.**
- **H2b-pooled** (D ≥ 1.029): **met.**

**F2 (300 character 3-grams, reported in parallel):** D(de Vere) = 1.089 against a median of medians of 1.030; rank 711 of 1,100. Same outcome.

## Descriptive results (A2.6, no decisions)
**Comparison authors' median D (F1), nearest first:**

| Author | Median D | | Author | Median D |
|---|---|---|---|---|
| Sidney | 0.916 | | Gascoigne | 1.065 |
| Greville | 0.963 | | Turberville | 1.073 |
| Watson | 0.991 | | Drayton | 1.077 |
| Lodge | 1.000 | | Googe | 1.130 |
| Daniel | 1.020 | | Churchyard | 1.207 |
| Spenser | 1.029 | | | |

- **De Vere (1.133)** sits between Googe and Churchyard.
- **Chronology:** early-printed comparison authors (1560s–82) have a median of 1.099; late-printed (1590s) a median of 1.009. De Vere (1.133) falls with the early group, close to Vaux (1.114) and Edwards (1.096), his *Paradise* companions.
- **Jackknife** (12 leave-one-poem-out samples, 1,949–2,194 tokens): D ranges from **1.095 to 1.132**. No single poem drives the result; every jackknife sample is beyond the median of medians.
- ***A Lover's Complaint*** (2,200 tokens; authorship debated): D = 0.969. That's inside the control range and nowhere near Shakespeare's own samples (median 0.38). It's one sample in a different genre (complaint), so this is descriptive only.

## Interpretation and limits (as registered in A2.7)
- On function-word and character-n-gram evidence, de Vere's surviving verse doesn't resemble Shakespeare's non-dramatic verse more than other Elizabethan poets' verse does. It sits among the 1560s–70s courtier and miscellany poets, which is where its printing history places it.
- **What this doesn't show:**
  - It doesn't disprove any authorship theory. Style can change over 20–30 years, the genres differ (lyrics vs sonnets and narrative poems), and there's only one de Vere sample, which couldn't be validated (V3).
  - The chronological gradient means period alone could produce this distance. That isn't evidence about authorship either way.
  - The split-half validation was within books, so cross-book comparisons are less certain.
- **What it adds:** under a pre-registered design whose checks passed, the result points the same way as Elliott & Valenza's earlier finding that de Vere's poems match Shakespeare poorly. "Not a match" is a reportable result (CLAUDE.md).
