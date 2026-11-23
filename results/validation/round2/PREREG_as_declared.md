# Pre-registration

Status: **DRAFT, not locked.** Drafted 2026-11-22. The judgement calls marked **[accepted]** were confirmed by the project owner on 2026-11-22.

**Locking procedure:**
1. ~~Settle the review items~~ (done 2026-11-22).
2. Implement `src/score/` and its tests.
3. Run **only** the validation in section 5. Thresholds are set there.
4. Write the resulting threshold values into section 4.
5. Commit with the message "Lock PREREG" and record the hash below.

No candidate (section 2.6) and no Stage 2 de Vere-vs-Shakespeare score is computed before the lock. After locking, changes go in the Amendments section with date and reason; the original text is not edited.

- Locked on: TBD
- Lock commit: TBD
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
- **Values** (filled in after validation, before the lock): θ = TBD, θ₁ = TBD, θ_S = TBD.

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

## Amendments
(none)
