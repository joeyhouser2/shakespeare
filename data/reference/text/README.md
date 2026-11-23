# Extracted texts

Generated from the raw EEBO-TCP XML by `src/extract/tcp_verse.py`, then linked to the manifest by `src/extract/link_manifest.py`. Don't edit these files by hand: change the script and rerun it. The raw XML in `data/reference/raw/tcp/` is never modified.

- `orig/<TCP>/<TCP>_<nnn>.txt`: one poem per file, in original spelling, one verse line per line, with a blank line between stanzas.
- `tcp_poems.csv`: one row per extracted poem. Columns: `poem_id`, `tcp_id`, `div_path` (TEI div types), `head` (heading), `signed` (signature, e.g. `E. O.`), `first_line`, `n_lines`, `n_words`, `n_gaps`, `split`, `path`.

Run on 2026-11-22: **2,651 poems from 22 volumes.**

## How poems are split
1. Each leaf TEI `div` that contains verse is a candidate poem.
2. Inside that `div`, a new poem starts at any `<head>` that follows verse. Sonnet sequences encode each sonnet this way.
3. A new poem also starts where a stanza opens with a TCP drop-cap word (e.g. "VVHat", "FRaud") after verse. These are flagged `split=dropcap` (132 poems). This catches unmarked poems inside one `div`. In the *Phoenix Nest*, for example, "Alas my hart" and Oxford's "What cunning can express" were run together, and the "E. O." signature belongs to the second.
   - "VV" or "UU" alone is just W and doesn't count. The *Epithalamion* is excluded from this rule because every stanza opens with a drop cap.

## Known imperfections
- **Over-splitting:** the *Anacreontics* at the end of the *Amoretti* (A12772) come out as 5 pieces. Some dialogue poems split at internal headings. 30 pieces are under 4 lines long, so set a minimum length when sampling.
- **Gaps:** 698 poems contain TCP gap placeholders, about 3,400 in total, almost all single illegible letters (`•`). Words stay whole, but the letter is unknown. `n_gaps` counts them.
- **Spelling:** long s (ſ), u/v, i/j and superscript abbreviations ("yt") are kept as printed. Normalization is a separate layer and isn't built yet.

## De Vere texts linked (secure canon)
10 of the 16 secure poems have text, about 2,060 words:
- **1576 *Paradise of Dainty Devices* (A21161):** Nos. 2–9.
- ***Brittons Bowre* 1591 (A16731):** No. 11.
- ***Phoenix Nest* 1593 (A11254):** No. 14.
- Possible No. III is also linked, from the *Bowre*.

Signature findings from the prints:
- 1576 *Paradise*: seven poems are signed "E. O.". No. 6 ("If care or skill") is signed "M.B." there, but "E.O." in the 1585 edition.
- No. 5 ("I am not as I seem to be") is signed "E.Ox." in 1585. That weighs against CELM's cross-reference to Essex.
- No. 4 reads "Fraud is the front of Fortune" in the 1576 TCP text and "Fram'd in the front of forlorne hope" in 1585.

Still without text:
- **No. 1:** Cardanus Comforte, 1573.
- **No. 13:** Wits Interpreter, 1655, plus manuscripts.
- **No. 15:** Tears of Fancie, 1593.
- **No. 16:** Mundy, 1595.
- **Nos. 10 and 12:** manuscript only.

The four prints may be in EEBO-TCP. Look them up before transcribing from manuscript.
