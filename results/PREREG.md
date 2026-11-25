# Pre-registration

Status: **LOCKED 2026-11-23.** Validation is complete (round 2 final, failed; outcome registered below). From here on, changes go only in Amendments. The judgement calls marked **[accepted]** were confirmed by the project owner on 2026-11-22.

**Locking procedure:**
1. ~~Settle the review items~~ (done 2026-11-22).
2. Implement `src/score/` and its tests.
3. Run **only** the validation in section 5. Thresholds are set there.
4. Write the resulting threshold values into section 4.
5. Commit with the message "Lock PREREG" and record the hash below.

No candidate (section 2.6) and no Stage 2 de Vere-vs-Shakespeare score is computed before the lock. After locking, changes go in the Amendments section with date and reason; the original text is not edited.

- Locked on: 2026-11-23
- Lock commit: `1f8c0898708cf5649bdc5fdd8e9085c63a0f57ba` ("Lock PREREG"; hash recorded in the following commit). Check with `git diff 1f8c089 -- results/PREREG.md`: only this line and Amendments may differ.
- Random seed for every sampling step: **20261122**

Corpus measurements behind the choices below (tokens in the MorphAdorner layer, counted 2026-11-22): de Vere secure poems 52–297 tokens each, about 2,600 in total; Shakespeare non-dramatic verse about 45,000 (sonnets median 116); control authors from about 600 (Dyer) to about 56,000 (Gascoigne). Only sizes were examined, not scores.

---

## 1. Questions and hypotheses

### Stage 1: undiscovered de Vere writings
- **Q1:** Do any harvested anonymous, initialed or disputed items score as de Vere's at a rate higher than decoys do?
- **H1 (null):** The number of candidates at or above the de Vere threshold θ is no greater than expected from the decoy false-positive rate (FPR × number of candidates).
- Every candidate at or above θ is a **lead**, not an attribution. Each needs outside evidence (hand, provenance, dating, scribal note).

### Stage 2: de Vere vs Shakespeare
- **Q2:** In an open-set General Imposters test with Shakespeare's non-dramatic verse as the target, do de Vere's poems score as Shakespeare's more than poems by period control poets do?
- **Statistic:** each author's mean GI score (Shakespeare as target) over that author's test poems.
- **H2a (de Vere closer than controls)** is supported only if **both** hold:
  - (i) de Vere's mean is higher than every control author's mean;
  - (ii) a one-sided Mann–Whitney test of de Vere's poem scores against pooled control-poem scores gives p < 0.05.
- **H2b (de Vere no closer than controls)** is supported if de Vere's mean is at or below the median of the control-author means.
- Anything in between is **inconclusive**. So is any outcome where a section 5 control fails.
- All three outcomes are reported with the same prominence.
- **Chronology (secondary):** the same comparison is repeated against early-printed controls (first printed 1557–1582) and late-printed controls (1590–1602) separately (section 2.3). It is descriptive only, with no separate hypothesis.

### Stage 3: other candidate authors
- Same design as Stage 2, with each candidate author as the target or as the tested author. It gets its own amendment, with that author's corpus, before any Stage 3 score is computed.
- Candidates below the author minimum (section 3.4) are reported as **untestable**, not as excluded or refuted.

---

## 2. Corpora (all listed in `data/reference/manifest.csv` and `data/reference/text/items.csv`)

### 2.1 De Vere reference set
- **Core reference set (12 poems), [accepted]:** May (1980) secure Nos. 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 14, 16. These have no contrary contemporary attribution.
  - **No. 5 is included.** Both *Paradise* editions sign it "E. O." / "E.Ox."; only CELM cross-references a manuscript copy to Essex.
  - **No. 10** is a modernized text (Hannah 1870). It's used in normalized layers only.
  - **No. 16** is an editorial reconstruction from the Mundy part-book. The lineation is editorial, which doesn't matter for lexical features.
- **Contested canon (scored as test items, not used for training or threshold-setting):**
  - No. 6: signed "M.B." in the 1576 *Paradise*.
  - No. 15: printed unsigned within Watson's *Tears of Fancie*.
- **Possible poems (scored as candidates):** No. III. Nos. I and IV have no text yet.
- **Excluded:** No. II (assigned to Dyer by CELM). Nos. 12 and 13 have no text.
- **Letters:** the 1573 Bedingfield letter is prose and in printed spelling. It's excluded from verse scoring and from spelling-habit features.

### 2.2 Shakespeare (Stage 2 target)
- **Target documents:** Sonnets 1–154, *Venus and Adonis*, *Lucrece*, *The Phoenix and Turtle*, from first editions (EEBO-TCP), with the same normalization as the controls.
- ***A Lover's Complaint*** (authorship debated) is excluded from the target. It's scored separately as a descriptive test item.
- **Songs from the plays:** not included, [accepted]. They're a different genre and setting, would have to be extracted from different early prints, and the corpus is already large.

### 2.3 Control authors
- Selection rules are in `src/extract/select_items.py`; per-poem decisions are in `items.csv`.
- **Author classes** (at least 2,000 tokens, section 3.4), grouped by first printing:
  - **Early (1557–1582):** Googe (1563), Turberville (1567), Gascoigne (1575), Churchyard (1575), Vaux and Edwards (*Paradise* 1576), Spenser *Shepheardes Calender* (1579), Watson (1582).
  - **Late (1590–1602):** Sidney (1590–91), Lodge (1593), Daniel (1594), Drayton (1594), Spenser *Amoretti* (1595).
  - **Greville** (written c. 1577–1600s, printed 1633): counted in neither chronology group, included in the main analysis.
  - **Spenser** is one author class for the main analysis, but each work goes in its own chronology group.
- **Below the minimum:** Dyer (about 600 tokens) and Breton (about 1,400) go into the imposter pool only.
- **No text yet:** Ralegh and Essex.

### 2.4 Imposter pool
- *Phoenix Nest* (1593), *England's Helicon* (1600) and *A Poetical Rapsody* (1602). Items signed by Oxford, Shakespeare ("W. S." included), Marlowe or Mary Sidney are removed, along with anything matching an Oxford first line.
- Dyer and Breton items are added (section 2.3).

### 2.5 Same-venue decoys
- Poems in the 1576 *Paradise of Dainty Devices* signed by authors other than E. O., Vaux and Edwards (e.g. F. K., W. H., D. S., E. S., R. Hill, Jasper Heywood).
- They belong to no reference set, so they test whether the method responds to the volume or printer rather than to the author.
- Any poem linked to an Oxford manifest row is excluded. In practice that is contested No. 6, signed "M.B." in 1576.

### 2.6 Candidates (Stage 1)
- Not yet harvested. Harvest is a separate step (CLAUDE.md Phase 2). Candidate texts are normalized with the same pipeline.
- Candidates are scored only after the lock.

### 2.7 Exclusions decided before analysis
- Texts under 100 tokens are not scored as test items (section 3.3), though they can sit in reference documents.
- Latin, Italian and Spanish pieces, commendatory verse by others, plays, and prose are excluded (`items.csv`).
- Duplicate witnesses are excluded: Gascoigne 1573 (the 1575 *Posies* is used), and the 1585 *Paradise* (the 1576 edition is used).

---

## 3. Features and text handling

### 3.1 Spelling layers
- **Lexical and character features:** the MorphAdorner layer (`text/norm_ma/`).
- **Metre:** the rules layer (`text/norm/`).
- **Holograph spelling-habit features only:** original spelling.
- Modernized-source texts (Hannah No. 10; Folger) are never used in the original layer.
- Normalizer: MorphAdorner 2.0.1 over VARD2, decided 2026-11-22. Details in `data/reference/NORMALIZATION.md`.

### 3.2 Tokenization
Text is lowercased. Tokens are runs of letters, with internal apostrophes kept ("o'er"). Punctuation and numerals are dropped. No stemming or lemmatization.

### 3.3 Units
- **Test items:** whole poems of **at least 100 tokens**, not chunked. Longer poems are tested whole; features are relative frequencies, so length is normalized.
- **Reference documents:** for each author, that author's selected texts in corpus order, joined and cut into consecutive **200-token documents** [accepted]. Chunks don't cross volume boundaries. The last piece of a volume is kept if it has at least 100 tokens and dropped otherwise. So a text under 100 tokens that is alone in its volume adds nothing; in practice that is de Vere No. 16, at 52 tokens. The 200-token length matches the typical test poem (de Vere median about 200).
- **Leave-one-out:** whenever a poem is the test item, it is removed **before** its author's reference documents are built, so no test text appears in any reference document.

### 3.4 Author minimum
An author can be a target or a tested author class only with **at least 2,000 tokens** of reference text. Below that, the author goes into the imposter pool only. With 12 core poems (about 2,250 tokens), de Vere is just above the minimum. That's a stated limitation.

### 3.5 Feature sets
- **F1, primary:** the 150 most frequent words, ranked over the reference documents of the current run (test item excluded). Values are relative frequencies, z-scored with the reference documents' means and standard deviations.
- **F2, secondary:** the 300 most frequent character 3-grams, including word-boundary spaces, built and scaled the same way.
- **Metre and rhyme:** descriptive only, reported alongside the scores. Not used in any decision. The texts are too short and too varied in form.
- Proper names are not removed, [accepted]. Removing them needs a name list that doesn't exist yet. Name-driven similarity gets checked when leads are reviewed.

---

## 4. Methods and thresholds

### 4.1 Primary: General Imposters (Koppel & Winter 2014; Kestemont et al. 2016)
- **Distance:** cosine distance on z-scored F1 vectors (Cosine Delta; Smith & Aldridge 2011; Evert et al. 2017).
- **Iterations:** 100. In each one, sample 50% of the features and **as many imposter documents as the target has reference documents** (after any leave-one-out removal), without replacement. *(Changed for validation round 2; round 1 sampled 50% of all imposter documents. See Validation history.)*
- **Score:** the share of iterations in which the test item is closer to its nearest target-author document than to its nearest imposter document. Range 0–1.
- **Imposter set:** all reference documents from authors other than the target, plus the imposter pool.
  - **Open-set rule:** when the test item's own author is one of those, that author's documents are removed from the imposter set for that test. This simulates an author the method has never seen and is the harder, more realistic case.
- **Repeat for F2.** F2 results are secondary and reported in parallel. Decisions use F1.

### 4.2 Secondary: Cosine Delta nearest author (closed set)
Rank each test item's distance to every author's centroid (mean z-scored vector). Descriptive only.

### 4.3 Thresholds (set in section 5, before any candidate is scored)
- **θ (lead):** the smallest GI score at which the false-positive rate on the Stage 1 decoys (section 5.1) is **at most 5%**.
- **θ₁ (strong lead):** the same at **at most 1%**.
- **θ_S (Stage 2 assignment to Shakespeare):** the smallest GI score at which the false-positive rate on control-author poems tested against the Shakespeare target is at most 5%. It's used only for the positive control and for reporting assignment rates.
- **Values** (validation round 2, F1): **θ = 0.83, θ₁ = 0.95, θ_S = 0.80.** (F2, secondary: θ = 0.88, θ₁ = 0.94, θ_S = 0.87.)

### 4.4 Multiple testing (Stage 1)
With N candidates, about 0.05 × N false leads are expected at θ. The report always gives this expected number next to the observed count of leads. Ranking is by score, and no lead is called significant on its own.

---

## 5. Validation (run before the lock; all results reported)

### 5.1 Stage 1: de Vere as target
- **Recall:** leave-one-out over the 11 core poems of at least 100 tokens (No. 16 is too short to test). Report recall at θ and θ₁, with exact binomial 95% confidence intervals.
- **Decoys:**
  - (a) Up to 15 poems of at least 100 tokens per control author class (13 authors), sampled with the fixed seed and tested open-set.
  - (b) All same-venue *Paradise* decoys of at least 100 tokens (section 2.5).
  - FPR, ROC and AUC are reported for (a), (b) and the two combined. θ and θ₁ are set on the combined decoys.
- **Power criterion, [accepted]:** if leave-one-out recall at θ is below **0.50**, Stage 1 is declared **underpowered**. Leads would then be reported as exploratory only, with no ranking claims.

### 5.2 Stage 2 controls (any failure makes Stage 2 inconclusive)
- **Positive control:** leave-one-out on 30 sonnets of at least 100 tokens (fixed-seed sample) plus each of *Venus*, *Lucrece* and *Phoenix and Turtle*, tested against the Shakespeare target with that text removed. **Pass:** at least 60% score at or above θ_S.
- **Negative control:** each control author class in turn is the target, with leave-one-out on up to 15 of its poems and its own open-set decoys from the other authors. **Pass:** the median AUC across authors is **at least 0.75**.
- **Same-venue check:** the *Paradise* decoys' scores against the de Vere target are compared with control decoys. If same-venue decoys reach θ at more than twice the control-decoy rate, a printer/venue effect is reported as a caveat on Stage 1.

---

## 6. Reporting
- Every test run is reported, including null and inconclusive results, with full score tables. Precision and recall are reported at the pre-set thresholds.
- Limits stated up front:
  - de Vere's small and short canon (about 2,250 core tokens; only 11 poems testable)
  - genre mismatch (Shakespeare's sonnets and narrative poems against de Vere's lyrics)
  - a 20–30-year gap in date
  - normalizer effects
  - authorship evidence that rests on printers' attributions
- Prior work to engage: Elliott & Valenza (Claremont Shakespeare Clinic).
- Stylometric hits are leads; attribution needs outside evidence.
- **Not covered by this registration:** holograph spelling-habit analyses and the Hand D comparison (plan.md Stage 2b). Each gets its own amendment before anything is computed.

## 7. Software
- A Python implementation goes in `src/score/`, with unit tests (synthetic data where the right answer is known). R `stylo` is not used, so results don't depend on two implementations.
- Python and library versions are recorded in `results/environment.txt` at the lock.

## Validation history (before lock)
- **Round 1, 2026-11-22: failed.** de Vere leave-one-out recall at θ was 0/11 (F1). The Shakespeare positive control was 21% against a 60% criterion. The negative control passed (median AUC 0.81). Diagnosis: the GI nearest-neighbour score is biased by the target's document count (11 for de Vere against about 1,250 sampled imposters), and the 1576 *Paradise* shows a venue effect. Full results, all kept: `results/validation/round1/`. The thresholds from this round are not adopted.
- **Round 2, declared 2026-11-22 before running:**
  - **The one change** is balanced imposter sampling (section 4.1). Each iteration draws as many imposter documents as the target has reference documents, so the nearest-neighbour comparison is between equal-sized sets.
  - **Rationale:** the round 1 score was confounded with the target's document count. The change was chosen to remove that bias, not tuned to any author's score.
  - **Unchanged:** features, distance, iterations, feature fraction, open-set rule, decoy samples, seed, and every pass/fail criterion in section 5.
  - **Additional report (not a criterion):** the Spearman correlation between target reference size and negative-control AUC, compared with round 1 (ρ = 0.50).
  - **Round 2 is final.** If any section 5 criterion fails, PREREG is locked with that outcome (Stage 1 underpowered and/or Stage 2 inconclusive). There is no round 3.
- **Round 2, run 2026-11-22: failed (final).**
  - de Vere leave-one-out recall at θ: 1/11 (AUC 0.62).
  - Shakespeare positive control: 27% against the 60% criterion (AUC 0.83).
  - Negative control: passed (median AUC 0.85).
  - *Paradise* venue effect: present in F1.
  - Details: `results/validation/round2/VALIDATION.md`.

## Registered outcome of validation (binding at lock)
- **Stage 1 is UNDERPOWERED.** Candidates may still be scored after the lock, but every lead is exploratory, reported with the expected false-lead count (section 4.4) and the *Paradise* venue caveat, and given no ranking claim.
- **Stage 2 is INCONCLUSIVE** under this design, because the positive control failed. The H2 statistic may be computed and reported for completeness, labelled inconclusive. It must not be described as support for H2a or H2b.
- **Any new analysis needs its own amendment, declared before it is computed.** Examples: aggregating all de Vere poems into one sample, adding more de Vere text (letters, Nos. 12–13), or a different method. Its results are reported as new, not as a rescue of this design.

## Amendments

### Amendment 1: scoring Stage 1 candidates (2026-11-23; declared before any candidate is scored)
**Why:** the locked design (sections 2.6, 4.3, 4.4) says candidates are scored after the lock, but it doesn't say how to handle candidates whose text also sits in the imposter pool, or candidates that were used as validation decoys. Nothing below changes the method, features, thresholds or the registered outcome (Stage 1 underpowered).

**A1.1 Candidate set.**
- The set is `data/candidates/manifest.csv` as committed together with this amendment (selection rules in `src/harvest/select_candidates.py`; full decision log in `data/candidates/selection_log.csv`).
- Only candidates with at least 100 tokens (`scorable = 1`) are scored: 467 of 716. The rest are listed, not scored. That includes *Englands Parnassus* "What plague is greater…" (E. of Ox., 51 tokens).
- Songbook candidates are scored on their plain-verse stanzas only (stanza 1 missing) and flagged as such.

**A1.2 Self-match exclusion.**
- Before a candidate is scored, every copy of it (all `witnesses`, matched by first line) is removed from the reference and imposter texts. The affected author's or pool's documents are then rebuilt, exactly as for leave-one-out.
- This matters for the 159 scorable candidates with a copy in an imposter-pool volume (*Phoenix Nest*, *England's Helicon*, 1602 *Rapsody*).
- Imposter set: all reference documents from authors other than Oxford, plus the pool (section 4.1). The open-set rule doesn't apply, because the candidate's author is unknown.

**A1.3 Validation decoys.**
- 13 scorable candidates (initialed poems in the 1576 *Paradise*) were same-venue decoys in validation round 2, and their scores helped set θ.
- They are scored and listed, but reported separately and **excluded from the H1 count**. That gives **N = 454** for H1.

**A1.4 Scoring and labels.**
- Each candidate is scored with F1 (which decides) and F2 (reported in parallel), with the round 2 method: balanced GI, seed 20261122, per-test generator keyed on the candidate id.
- **Lead** = F1 score ≥ θ = 0.83. **Strong lead** = F1 score ≥ θ₁ = 0.95.
- The nearest-centroid author (section 4.2) is reported for each candidate.

**A1.5 Test of H1.**
- One-sided exact binomial test of the number of leads among the N = 454, against the chance rate measured on the round 2 decoys at θ: **p₀ = 0.0417** (10/240), so about 18.9 leads are expected by chance.
- Strong leads are reported the same way against p₀ = 0.0083 (2/240), so about 3.8 expected.
- α = 0.05.
- **Stated in advance:** the candidates come from the same anthologies and decades as de Vere's printed poems, whereas the decoys are mostly from single-author control books. So an excess of leads may reflect shared period, venue or printing conventions rather than de Vere's authorship (see the *Paradise* venue effect in validation). A significant result would therefore *not* be read as evidence that the pool contains de Vere poems. A non-significant result means the stylometric screen found nothing beyond chance.

**A1.6 Reporting.**
- All 467 scores are published.
- Leads are listed by score, each with: every copy and its signature, source volume and date, whether it comes from a *Paradise* edition (venue caveat), its nearest-centroid author, and a pointer to the outside checks needed (other copies in the Folger First-Line Index or CELM, manuscript context).
- No lead is called an attribution. Stage 1 stays labelled **underpowered**.
- Output goes to `results/stage1/`.

### Amendment 2: pooled de Vere sample vs Shakespeare (2026-11-25; declared before anything for it is computed)
**Why:** the registered Stage 2 design (sections 1, 4, 5.2) works at the level of single poems and was declared **inconclusive**. Its positive control failed, because texts of 100–300 tokens carry too little author signal. This is a **new, separately registered analysis**, not a rescue of that design. Its result is reported as new, and the Stage 2 outcome above stays **inconclusive**. Larger samples are the standard remedy for weak signal in short texts, and de Vere's whole core canon is just large enough for one sample.

**A2.1 Question.**
- **Q2-pooled:** treating de Vere's core poems as one sample, is it closer to Shakespeare's non-dramatic verse than equal-sized samples from the period control poets are?

**A2.2 Samples (all from the MorphAdorner layer, tokenized as in section 3.2).**
- **Sample size:** S = **2,200 tokens** for every sample. De Vere's core is 2,246 tokens.
- **De Vere:** one sample. The 12 core poems (section 2.1) are joined in May order and cut to the first 2,200 tokens.
- **Control authors:** B = **100** random samples per author. Each sample is built from whole poems in random order until S is reached, then cut to S. A poem longer than the remaining need contributes a contiguous random window of the needed length.
- **Comparison set (used for the decision):** control authors with at least 2S = 4,400 tokens, so each can give two or more independent samples. That's 11 authors: Daniel, Drayton, Lodge, Watson, Googe, Greville, Spenser, Sidney, Churchyard, Turberville, Gascoigne.
  - Vaux and Edwards (about 2,800 tokens each) are sampled and reported, but **excluded from the decision**, because their 100 samples would overlap almost completely.
- **Shakespeare:** B = 100 samples, drawn the same way from the Stage 2 target texts (Sonnets, *Venus*, *Lucrece*, *Phoenix and Turtle*). *A Lover's Complaint* is scored separately and described only.
- **Random seed:** 20261122. Each author's sampling has its own generator, keyed on the author name.

**A2.3 Features and distance.**
- **F1 (decides):** the 150 most frequent words over all tokens of the comparison set, Shakespeare and de Vere. Values are relative frequencies, z-scored with the mean and SD across all control and Shakespeare samples in the run.
- **F2 (reported in parallel):** 300 most frequent character 3-grams, built and scaled the same way.
- **Shakespeare profile:** the mean z-vector of the 100 Shakespeare samples.
- **D(x):** the cosine distance from sample x to the Shakespeare profile (Cosine Delta).

**A2.4 Validation (computed first; if either check fails, the pooled analysis is reported as inconclusive).**
Each split-half run uses a separate profile and sample set:
- Every comparison author and Shakespeare is split in two halves by alternating poems in corpus order. For Shakespeare, *Venus* goes to half A and *Lucrece* plus *Phoenix and Turtle* to half B.
- Profiles are built from samples of one half, test samples from the other, and then the halves are swapped. Each run uses 100 samples per half.

**V1, Shakespeare positive control:**
- Held-out Shakespeare samples (D to the opposite-half Shakespeare profile) are compared with comparison-author samples (D to the same profile).
- **Pass** requires both:
  - AUC ≥ **0.90** (Shakespeare scored as nearer than controls);
  - the median held-out Shakespeare D is lower than every comparison author's median D.

**V2, author signal at 2,200 tokens:**
- Each held-out sample is assigned to the nearest profile among the 12 split-half profiles (11 comparison authors plus Shakespeare).
- **Pass:** macro-averaged accuracy of at least **0.80**.

**V3, de Vere self-recognition:** cannot be tested, because one sample can't be split. Stated as a limitation.

**A2.5 Decision rule (main run, all texts).**
- Let m_c be the median D over author c's 100 samples, for each comparison author c, and let P be the pooled distribution of all comparison-author samples' D.
- **H2a-pooled (de Vere closer to Shakespeare than the controls)** is supported only if **both** hold:
  - D(de Vere) < min over c of m_c;
  - D(de Vere) < the 5th percentile of P.
- **H2b-pooled (de Vere no closer than the controls)** is supported if D(de Vere) ≥ the median of {m_c}.
- Anything in between is **inconclusive**. A failed V1 or V2 makes the whole analysis inconclusive.
- All outcomes are reported with equal prominence.

**A2.6 Descriptive only (no decisions):**
- F2 results.
- D for Vaux, Edwards and *A Lover's Complaint*.
- De Vere's rank among the 100 × 11 control samples.
- A chronology split: early comparison authors (Googe, Turberville, Gascoigne, Churchyard, Watson) against late ones (Sidney, Lodge, Daniel, Drayton). Spenser and Greville go in neither group.
- A de Vere jackknife: 12 leave-one-poem-out samples of 1,900–2,200 tokens each, reported with their lengths. These are shorter than S, so they're not compared formally.

**A2.7 Caveats stated before computing:**
- There is only one de Vere sample, so there's no estimate of its own variability.
- De Vere's sample mixes several printers and decades (seven poems come from the 1576 *Paradise*), while control samples mostly come from single books.
- The genres differ: Shakespeare's sonnets and narrative poems against de Vere's mixed lyrics.
- Shakespeare's printed poems date from 1593–1609 and de Vere's mostly from 1573–1593.
- A result in either direction is weak evidence. H2a-pooled would not show common authorship.
- Prior work to engage: Elliott & Valenza.

**A2.8 Implementation and output.**
- Code: `src/score/pooled.py`, with unit tests for the sampling rules.
- Output: `results/stage2_pooled/`.
- Order: validation is computed and written out **before** the main run. The main run is a separate command, so the validation result can be checked first.
