# Stage 1 results: candidate screen (2026-11-24)

**Status: Stage 1 is UNDERPOWERED** (locked PREREG; validation round 2 recall 1/11). Every score below is an exploratory pointer for outside checks. **None is an attribution.**

Method: PREREG sections 3–4 plus Amendment 1, which was committed (`ee4448a`, pushed) and hashed (`amendment1_declared.sha256`) before scoring. Code: `src/score/score_candidates.py`. Every score: `candidate_scores.csv`. Summary: `summary.json`.

## Test of H1 (Amendment 1, A1.5)
| | Observed | Expected by chance | One-sided binomial p |
|---|---|---|---|
| Leads (F1 ≥ θ = 0.83), N = 454 | **18** | 18.9 (p₀ = 0.0417) | **0.62** |
| Strong leads (F1 ≥ θ₁ = 0.95) | **2** | 3.8 (p₀ = 0.0083) | **0.89** |

**H1 (null) is not rejected.** The number of de Vere-like candidates is exactly what decoys produce by chance, so the stylometric screen found no excess of de Vere-like poems in the printed anthologies. Given validation, a non-significant result was the expected outcome. It does **not** show that the anthologies contain no de Vere poems; the method can't detect them at this sample size.

## Other facts
- **467 candidates scored.** 13 of them were validation decoys and are excluded from H1; 4 of those 13 reached θ, which is roughly their own decoy rate.
- **Self-match exclusion** (A1.2) applied to 162 candidates.
- **Mean F1 score** of the H1 candidates: 0.525, about the same as the control decoys in validation (0.51).
- **The one scorable Oxford-signed candidate,** *Englands Parnassus* "Loue is a discord and a strange diuorce" (E. O.), scores **F1 0.35** (rank 372 of 467; nearest author Turberville). That's not a lead. Because the method can't recognize de Vere's own canon poems (validation), this low score is **not** evidence against the printed attribution either.
- **Limitation found while reviewing leads:** cross-edition merging by first line missed two pairs whose spelling differs ("Like to a(n) Hermit(e) poore…"; "I Rage in restlesse youth/ruthe…"). Merged, the leads are about 16 distinct poems against about 19 expected, which changes nothing. A fuzzier first-line merge would fix it in future runs.

## Leads (F1 ≥ 0.83), H1 set, by score
These are pointers for outside checks only. "Nearest" is the closest author centroid (closed set). Flags: P = from a *Paradise* edition (venue caveat); 2× = a second copy is listed separately (merging limitation).

| # | Candidate | Source | Attribution in print | F1 | F2 | Nearest | First line |
|---|---|---|---|---|---|---|---|
| 1 | A10147_009 | *Gorgious Gallery* 1578 | – | 0.96 | 0.79 | Edwards | IN doubtful dreading thoughts, as I gan call to mind |
| 2 | A19943_092 | *Poetical Rapsody* 1602 | A. W. (section) | 0.95 | 0.94 | Oxford | AS soone may water wipe me drie |
| 3 | A11254_059 | *Phoenix Nest* 1593 | – | 0.91 | 0.54 | Oxford | WHat else is hell, but losse of blisfull heauen? |
| 4 | A21161_078 | *Paradise* 1576 (P) | – | 0.91 | 0.84 | Vaux | LO heare the man that must of loue complaine |
| 5 | A19943_087 | *Poetical Rapsody* 1602 | A. W. (section) | 0.90 | 0.69 | Oxford | SOme men, they say, are Poets borne by kinde |
| 6 | A10147_016 | *Gorgious Gallery* 1578 | – | 0.89 | 0.67 | Oxford | SInce neede ye will mee singe, giue eare vnto the same |
| 7 | A10147_013 | *Gorgious Gallery* 1578 | – | 0.87 | 0.80 | Oxford | THe glyttering showes of Floras dames |
| 8 | A10147_032 | *Gorgious Gallery* 1578 | – | 0.87 | 0.86 | Oxford | IF only sight suffise, my hart to loose or binde |
| 9 | A19945_307 | *Poetical Rapsody* 1611 | – | 0.87 | 0.49 | pool | Her face, her tongue, her wit, so faire, so sweete |
| 10 | A21166_099 | *Paradise* 1585 (P, 2×) | Yloop | 0.87 | 0.73 | Vaux | I Rage in restlesse youth, and ruines rule my dayes |
| 11 | A10147_048 | *Gorgious Gallery* 1578 | – | 0.86 | 0.44 | Vaux | I Spake when I ment not, in speeding to gayne |
| 12 | A11254_055 | *Phoenix Nest* 1593 (2×) | – | 0.86 | 0.94 | Oxford | LIke to a Hermite poore in place obscure |
| 13 | A16273_083 | *England's Helicon* 1600 | M. F G. | 0.86 | 0.67 | pool | LOues Queene long wayting for her true-Loue |
| 14 | A10831_023 | *Handefull* 1584 | – | 0.85 | 0.64 | Watson | THe famous Prince of Macedon |
| 15 | A20696_song_004 | Dowland, *Musicall Banquet* 1610 | – | 0.85 | 0.53 | Edwards | Leaue a wretch in whom all woe (stanza 2+) |
| 16 | A16731_010 | *Brittons Bowre* 1591 (2×) | – | 0.84 | 0.94 | Oxford | LIke to an Hermit poore in place obscure |
| 17 | A19943_110 | *Poetical Rapsody* 1602 | A. W. (section) | 0.84 | 0.69 | Oxford | The summer Sun that scalds the ground with heate |
| 18 | A19945_333 | *Poetical Rapsody* 1611 | – | 0.83 | 0.37 | pool | DEarling of these, of future times the glory |

Leads among the validation-decoy candidates (not counted): A21161_063 (M.H., 0.91), A21161_020 (M. T., 0.87), A21161_099 (Yloop, 0.85), A21161_038 (E. S., 0.83).

## How to read the leads (Phase 6 triage, manual)
- About 19 of 454 candidates would reach θ by chance. **Some or all of these 18 are false leads**, and the method can't say which.
- Outside evidence decides. For each lead: look up its first line in the Folger First-Line Index and CELM for other copies and attributions, and check manuscript context and dating.
  - Several leads are well-known anthology poems that later sources attribute to other writers. "Like to a Hermit poor…" is often associated with Ralegh, for example. Those attributions need checking in CELM and the First-Line Index, not assuming either way.
- Two patterns don't count as evidence. Leads cluster in the 1570s anthologies (*Gorgious Gallery* has 5; the *Paradise* editions 2), and several have Vaux or Edwards as nearest author. Both are consistent with the period and venue confound found in validation.
- Ralegh and Essex, the two control authors without text yet, would be the first alternative authors to test once their corpora exist.
