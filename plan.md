# Project plan

Companion to CLAUDE.md (the brief). This file lays out the three stages and the order of work.
Last updated: 2026-11-22.

## Framing

Shakespeare is one comparison author among several. Hypotheses and thresholds are fixed in
results/PREREG.md before any candidate or comparison result is examined. The design must be
able to return "not a match" or "can't tell", and those outcomes get reported as readily as a match.

Prior work to replicate and engage with, not ignore: Elliott & Valenza (Claremont Shakespeare
Clinic) found de Vere's poems a poor match to Shakespeare on most of their tests.

## Stage 1 - Mine for more de Vere writings (CLAUDE.md phases 1-6)

### Reference corpus
- Poems: Steven May's canon (~16 secure, ~4 possible; ~600 lines total). Very small, so use methods suited to short texts.
- Letters: ~40-50 surviving, mostly Lansdowne MSS and Cecil Papers; many holograph.
  Alan Nelson's original-spelling transcriptions are the likely starting text (check terms of use).
  Tag each letter holograph vs secretary copy. Spelling analysis on holographs only.
- Controls: 10+ courtier poets (Sidney, Dyer, Ralegh, Vaux, Gascoigne, Breton, Greville, ...), balanced samples.

### Candidate sources
- CELM (Catalogue of English Literary Manuscripts) - Oxford entry lists manuscripts directly.
- May & Ringler, *Elizabethan Poetry: A Bibliography and First-line Index of English Verse, 1559-1603*.
- Folger Union First-Line Index; EMMO; Perdita Project.
- EEBO-TCP (Phase 1 is public domain) - printed miscellanies (Paradise of Dainty Devices, etc.).
- The National Archives Discovery; Cecil Papers; Lansdowne MSS; British Library.

### Scoring and validation
- Burrows' Delta and General Imposters on function words and character n-grams; rhyme and meter features layered on.
- Spelling habits from holograph letters only.
- Leave-one-out on known de Vere poems; decoys from control authors; precision/recall at the pre-set threshold.

## Stage 2 - Compare with Shakespeare

Design problems to handle:
1. Genre. Compare like with like: Shakespeare's non-dramatic verse (Sonnets, Venus and Adonis,
   Lucrece, A Lover's Complaint, The Phoenix and Turtle) plus songs from the plays. Folger Shakespeare texts are openly licensed.
2. Chronology. De Vere's verse is mostly 1570s-early 1580s; Shakespeare's 1590s+. Include control
   poets active in both periods (Ralegh, Breton, Greville, Daniel, Drayton) to measure drift over time alone.
3. Spelling. Printed Shakespeare reflects compositors; only Hand D (Sir Thomas More) and six
   signatures survive in his hand. No spelling test; vocabulary and verse features only.
4. Controls before the real test:
   - Positive: method assigns held-out Shakespeare poems to Shakespeare.
   - Negative: method separates known contemporaries (e.g. Sidney vs Dyer).
   - Then run de Vere vs Shakespeare as an open-set test where "neither" is an allowed answer.

New candidate texts from Stage 1 are scored against Shakespeare in the same framework.

## Stage 3 - Other candidate authors

Same pipeline, each candidate added as another author class.

| Candidate | Usable text | Testability |
|---|---|---|
| Marlowe | Plays + Hero and Leander | Good |
| Mary Sidney | Psalms, translations | Good for verse |
| Bacon | Mostly prose, little verse | Prose only, weak |
| Derby (William Stanley) | Almost nothing survives | Effectively untestable |
| Henry Neville | Letters only | Prose only, weak |

Record in PREREG.md that "insufficient text" is not "ruled out".

## Order of work
1. git init, .gitignore, conda env `devere`, folder layout. 
2. results/PREREG.md: hypotheses for all three stages, thresholds, controls. Lock before results.
3. data/reference/manifest.csv: May canon, letters (holograph/secretary), controls, Shakespeare poems.
4. Spelling normalization rules (keep original + normalized versions).
5. Per-source harvest plan: terms of use, rate limits. Ask before bulk downloading.
6. Build scoring pipeline; pass the controls before scoring any candidate.

Stage 2 can begin as soon as step 6 works; it needs only the reference corpus.

## Stage 2b: Shakespeare's handwriting vs de Vere's (added 2026-11-22)

**What survives in Shakespeare's hand**
- **Six signatures:** the Belott–Mountjoy deposition (1612), the Blackfriars Gatehouse conveyance and mortgage (1613), and three on the will (1616).
- **"Hand D" in *Sir Thomas More*:** British Library Harley MS 7368, ff. 8r–9r, about 147 lines in English secretary hand. The attribution to Shakespeare rests on palaeography (Thompson 1916), spelling, and style (Pollard et al. 1923; Jackson). Most scholars accept it, but it is an inference, not a documented fact.
- The BL images are on Shakespeare Documented (Folger) under a Public Domain Mark.

**What survives in de Vere's hand:** about 74 letters and memoranda entirely in his own hand (Nelson 2003, pp. 487–9). Almost all are in a clear **italic** hand.

**Why a letterform comparison won't work:** Hand D is secretary script; de Vere wrote italic. These are different writing systems, taught separately, with different letter shapes. Comparing them is like comparing print with cursive: neither likeness nor difference says much about who wrote them. CLAUDE.md also rules out automated handwriting judgments. Any hand comparison goes to a palaeographer, who would need an italic sample by Shakespeare (none exists) or a secretary sample by de Vere (if one turns up in his autograph letters, flag it).

**What we can do: compare spelling habits** (spelling analysis on holographs only, per CLAUDE.md)
1. **Hand D transcription in original spelling:** from Pollard et al., *Shakespeare's Hand in the Play of Sir Thomas More* (1923; public domain in the US, on Internet Archive as `shakespeareshand0000poll`), or Greg's Malone Society edition (1911). Check it against the BL images.
2. **De Vere holograph letters in original spelling:** needs a transcription source (see TODO.md, Oxford letters).
3. **Features:** spellings of common words (e.g. Hand D's "scilens"), doubling, final -e, -ie/-y, use of y for i, and so on, computed on original spelling only.
4. **Controls:** other holograph spellers of the period, such as Hands A, B and E in the same manuscript (Chettle, Heywood, Dekker), plus other courtiers' autograph letters. These test whether a de Vere/Hand D match is closer than chance.
5. **Limits to state up front:** Hand D is short, it's dramatic verse rather than letters, its authorship is inferred, and spelling habits change over a lifetime. Pre-register the comparison in PREREG before computing it.
