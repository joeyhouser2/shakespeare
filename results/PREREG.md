# Pre-registration

Status: **DRAFT - not locked.** Fill every `TBD`, then lock by committing with the message
"Lock PREREG" and recording the commit hash below. After locking, changes go in the
Amendments section with date and reason; the original text is not edited.

- Locked on: TBD
- Lock commit: TBD

## 1. Questions and hypotheses

### Stage 1 - de Vere candidates
- Q1: Do any harvested anonymous, initialed or disputed items score closer to de Vere's secure canon than to the control authors?
- H1 (null): No candidate exceeds the de Vere threshold (section 4) beyond the rate expected from decoys.

### Stage 2 - de Vere vs Shakespeare
- Q2: In an open-set test on non-dramatic verse, are de Vere's secure poems assigned to Shakespeare more often than the poems of period-matched control poets?
- H2a: de Vere poems assigned to Shakespeare at a rate above the control-poet rate.
- H2b: de Vere poems assigned to Shakespeare at or below the control-poet rate.
- Both outcomes are reported. A result is "inconclusive" if the controls in section 5 fail.
- Chronology handling: TBD (e.g. compare de Vere with 1570s-80s and 1590s-1600s halves of cross-period control poets).

### Stage 3 - other candidates
- Same test as Q2 for each candidate in the testability table (plan.md).
- Candidates below the minimum text size (section 3) are reported as **untestable**, not excluded.

## 2. Corpora
- De Vere reference: May canon, secure poems only for the main test; "possible" poems held out and scored as candidates. Letters: holograph only for spelling features.
- Controls (manifest role `control`). Courtier poets contemporary with Oxford: Sidney, Gascoigne, Googe, Turberville, Vaux, Edwards, Breton, Churchyard, Ralegh, Dyer, Essex, Greville. Cross-period and 1590s poets for the chronology check: Spenser (1579 and 1595), Watson, Daniel, Drayton, Lodge. Item selection rules in src/extract/select_items.py; kept word counts in data/reference/text/README.md (range ~600 words for Dyer to ~56k for Gascoigne). Minimum words per author class for inclusion: TBD. Ralegh and Essex currently have no text.
- Imposter pool (manifest role `imposter`): Phoenix Nest, Englands Helicon, Poetical Rapsody, with any items by test authors removed.
- Shakespeare: Sonnets, Venus and Adonis, Lucrece, A Lover's Complaint, The Phoenix and Turtle, songs from plays. Edition: Folger Shakespeare. TBD confirm.
- Exclusions decided before analysis: TBD

## 3. Features and text handling
- Spelling: original and normalized versions; rule-based normalization defined in data/reference/NORMALIZATION.md (src/normalize/normalize.py, tested). Function words, character n-grams and vocabulary are computed on the MorphAdorner layer (text/norm_ma, filtered as documented); metre/syllable features on the rules layer (text/norm); original spelling only for holograph spelling-habit features. Modernized-source texts (Folger Shakespeare, Hannah 1870 de Vere No. 10) are used only in normalized layers. Normalizer choice made 2026-11-22 (MorphAdorner 2.0.1 over VARD2).
- Feature sets: most-frequent-word lists (size TBD), character n-grams (n = TBD), rhyme/meter features (TBD).
- Minimum text size for a scored sample: TBD words.
- Sampling: TBD (whole poems vs fixed-length chunks; chunk size).

## 4. Methods and thresholds
- Primary: General Imposters (parameters TBD: iterations, feature sampling ratio, imposter pool).
- Secondary: Burrows' Delta (variant TBD).
- Decision threshold for "lead": Imposters score >= TBD.
- Target false-positive rate on decoys: <= TBD %.
- Threshold chosen from validation (section 5) only, before any candidate is scored.

## 5. Validation (must pass before real tests)
- Leave-one-out on de Vere secure poems: report recall at threshold.
- Decoys: TBD number of control-author poems hidden among candidates; report false-positive rate.
- Positive control (Stage 2): held-out Shakespeare poems assigned to Shakespeare at >= TBD %.
- Negative control (Stage 2): known contemporaries (e.g. Sidney vs Dyer) separated at >= TBD %.
- If a control fails, the dependent test is reported as inconclusive.

## 6. Reporting
- Report precision/recall at the pre-set threshold, full score tables, and all tests run (including null results).
- Prior work to engage: Elliott & Valenza (Claremont Shakespeare Clinic).
- Stylometric hits are leads; attribution needs outside evidence (hand, provenance, dating).

## Amendments
(none)
