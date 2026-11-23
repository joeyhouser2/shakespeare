# Extracted texts

Generated from the raw EEBO-TCP XML by `src/extract/tcp_verse.py`, then linked to the manifest by `src/extract/link_manifest.py`. Don't edit these files by hand: change the script and rerun it. The raw XML in `data/reference/raw/tcp/` is never modified.

- `orig/<TCP>/<TCP>_<nnn>.txt`: one poem per file, in original spelling, one verse line per line, with a blank line between stanzas.
- `tcp_poems.csv`: one row per extracted poem. Columns: `poem_id`, `tcp_id`, `div_path` (TEI div types), `head` (heading), `signed` (signature, e.g. `E. O.`), `first_line`, `n_lines`, `n_words`, `n_gaps`, `split`, `path`.

Run on 2026-11-22: **2,714 poems from 25 volumes.**

## How poems are split
1. Each leaf TEI `div` that contains verse is a candidate poem.
2. Inside that `div`, a new poem starts at any `<head>` that follows verse. Sonnet sequences encode each sonnet this way.
3. A new poem also starts where a stanza opens with a TCP drop-cap word (e.g. "VVHat", "FRaud") after verse. These are flagged `split=dropcap` (132 poems). This catches unmarked poems inside one `div`. In the *Phoenix Nest*, for example, "Alas my hart" and Oxford's "What cunning can express" were run together, and the "E. O." signature belongs to the second.
   - "VV" or "UU" alone is just W and doesn't count. The *Epithalamion* is excluded from this rule because every stanza opens with a drop cap.

## Known imperfections
- **Over-splitting:** the *Anacreontics* at the end of the *Amoretti* (A12772) come out as 5 pieces. Some dialogue poems split at internal headings. 30 pieces are under 4 lines long, so set a minimum length when sampling.
- **Gaps:** 698 poems contain TCP gap placeholders, about 3,400 in total, almost all single illegible letters (`•`). Words stay whole, but the letter is unknown. `n_gaps` counts them.
- **Spelling:** long s (ſ), u/v, i/j and abbreviation strokes are kept as printed. Superscript letters are written as Unicode modifier letters ("yᵉ" = the, "yᵗ" = that, "wᵗ" = with), so they stay distinct from the real word "ye". An illegible superscript appears as "y^•".
- **Normalized layers:** `norm_ma/` (MorphAdorner pass, used for cross-author features) and `norm/` (rules only, used for metre) both mirror `orig/`, `special/` and `edited/` with the same file names. It's made by `src/normalize/normalize.py` under the rules in `../NORMALIZATION.md`. `items.csv` has a `norm_path` column, and the manifest has `norm_text_path`.

## De Vere texts linked (secure canon)
14 of the 16 secure poems have text, about 2,620 words. 13 come from early prints; No. 10 is a modernized 19th-century edited text (see `edited/README.md`).

| May No. | Source | TCP poem | Signature in this print |
|---|---|---|---|
| 1 | *Cardanus Comforte*, 1573 (A17947) | A17947_001 | headed "The Earle of Oxenforde to the Reader" |
| 2–9 | *Paradise of Dainty Devices*, 1576 (A21161) | see manifest | "E. O." on seven; No. 6 "M.B." |
| 11 | *Brittons Bowre*, 1591 (A16731) | A16731_040 | "E. of Ox." |
| 14 | *Phoenix Nest*, 1593 (A11254) | A11254_048 | "E. O." |
| 15 | *Tears of Fancie*, 1593 (A14826) | A14826_053 (Sonnet LX) | unsigned, in a sequence by T. W. (Watson) |
| 16 | Mundy, *Songs and Psalmes*, 1594 (A07912) | `special/` (editorial) | music book |
| 10 | Hannah 1870, from MS Tanner 306 p. 193 | `edited/` (**modernized spelling**) | MS: "Earl of Oxenford" |

Possible No. III is also linked, from the *Bowre* (unsigned there).

**Prose:** Oxford's letter to Bedingfield, printed before *Cardanus Comforte* (1573) and signed "E. Oxenford.", is in `special/A17947_oxford_letter.txt` (about 1,000 words). It's in print, so the spelling is the typesetter's, not his. Use it for vocabulary, not spelling.

**`special/`** holds texts made by `src/extract/tcp_special.py` rather than the automatic extractor. The Mundy text is an **editorial reconstruction**: the print is the words set under the music, with repeats ("ij.", repeated phrases). I took the top voice part (SVPERIVS), removed the repeats and set the lines by rhyme. The script checks that every word appears in the printed part. Keep in mind that the line breaks are editorial.

Attribution conflicts from the prints:
- **No. 5:** signed "E.Ox." in the 1585 *Paradise*. That weighs against CELM's cross-reference to Essex.
- **No. 6:** signed "M.B." in 1576 and "E.O." in 1585.
- **No. 15:** printed unsigned inside Watson's *Tears of Fancie*. The attribution to Oxford rests on the manuscript subscription in Rawl. poet. 85.
- **No. 4:** the 1576 text reads "Fraud is the front of Fortune"; the 1585 text reads "Fram'd in the front of forlorne hope".

Still without text (both in Bodleian MS Rawl. poet. 85):
- **No. 12:** ff. 48v–49r.
- **No. 13:** f. 106r. Its only print, Cotgrave's *Wits Interpreter* (1655), is not in EEBO-TCP.

Neither is in Hannah (1870). Grosart (1872) has them, but online it's only in Internet Archive's lending-only 1970 reprint and on HathiTrust, which blocks automated access. Someone needs to read Grosart in a browser or library, or look at the manuscript itself.

**Caution:** a manifest `orig_text_path` under `edited/` points to a modernized text. Its notes say "MODERNIZED". Feature code must leave these out of anything computed on original spelling.

## Control and imposter selection (`items.csv`)
`src/extract/select_items.py` decides which extracted poems count as each control author's own, and which go into the imposter pool. Every poem it considers gets a row with `include` (1/0) and the reason, so the choices can be audited. The rules are in the script's header. In short:
- **Single-author books:** only the author's own sections count. That leaves out commendatory verse by others, plays, errata, Latin/Italian mottoes, and poems signed by someone else.
- ***Astrophel* 1591:** Daniel's 28 sonnets ("S. D.") and the cantos by other poets are left out of Sidney.
- **Greville:** *Caelica* only. The verse treatises and play choruses are a different genre.
- **Gascoigne:** the 1575 *Posies* only. The 1573 *Flowres* is an earlier version of the same poems.
- **Anthologies:** assigned by printed signature only.
  - Vaux and Edwards: 1576 *Paradise*.
  - Breton and Dyer ("S. E. D."): *England's Helicon*.
  - The *Bowre* and *Arbor* carry no Breton signatures, so they aren't used.
- **Imposter pool:** everything in the *Phoenix Nest*, *England's Helicon* and *A Poetical Rapsody*, except items signed by Oxford, Shakespeare ("W. Shakespeare", plus the ambiguous "W. S."), Marlowe or Mary Sidney, and anything matching an Oxford first line.

Kept, by author (words):

| Author | Poems | Words | | Author | Poems | Words |
|---|---|---|---|---|---|---|
| Gascoigne | 143 | 56,288 | | Watson | 94 | 15,759 |
| Turberville | 164 | 45,693 | | Lodge | 46 | 12,721 |
| Churchyard | 36 | 45,080 | | Drayton | 62 | 8,394 |
| Sidney | 189 | 33,678 | | Daniel | 56 | 6,462 |
| Spenser | 117 | 30,028 | | Edwards | 10 | 2,832 |
| Greville | 110 | 18,741 | | Vaux | 13 | 2,802 |
| Googe | 43 | 17,157 | | Breton | 7 | 1,381 |
| | | | | Dyer | 5 | 606 |
| **Imposter pool** | 419 | 86,705 | | | | |

**Sizes are very uneven:** Gascoigne has about 56k words; Dyer about 600, Breton about 1,400. The scoring step must sample equal-sized chunks per author (PREREG section 3). Authors with too little text should be dropped as classes or kept only in the imposter pool. **Decide that before scoring.**

**Still without text:** Ralegh and Essex. Neither has a single-author print, and the anthology signatures aren't reliable for them.
