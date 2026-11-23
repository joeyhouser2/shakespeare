# Reference corpus

`manifest.csv` has one row per text (poem, letter or song). Every row must record its source, shelfmark, URL, license and access date.
Entries are added only after checking them against the cited source. Don't fill them in from memory.

| Column | Meaning |
|---|---|
| item_id | Stable ID, e.g. `oxf-p-01` (poem), `oxf-l-01` (letter), `sid-p-01`, `shk-son-018` |
| author | Name as used in the project (Oxford, Sidney, Shakespeare, ...) |
| role | `target` (de Vere), `control` (author classes), `comparison` (Shakespeare, Stage 3 candidates), `imposter` (mixed anthologies used only as the General Imposters pool) |
| genre | `lyric`, `sonnet`, `narrative-verse`, `song`, `letter` |
| title_or_first_line | First line in original spelling if untitled |
| canon_status | `secure`, `possible`, `disputed` |
| canon_source | Authority for attribution, e.g. `May 1991 Poem I` |
| witness_type | `manuscript` or `print` |
| hand | `holograph`, `secretary`, `scribal`, `print`, `unknown`. Spelling features use `holograph` only |
| date_est | Year or range, e.g. `1576` or `1572-1580` |
| repository / shelfmark / folio | Where the witness lives, e.g. `British Library`, `Lansdowne MS 19`, `f. 181` |
| printed_source | Edition or print the text was taken from |
| url | IIIF or catalogue link |
| license | Terms for the text/images used |
| access_date | YYYY-MM-DD |
| orig_text_path / norm_text_path | Paths to original-spelling and normalized text files |
| word_count / line_count | Computed from the original-spelling file by script |
| notes | Anything else (variants, attribution doubts) |

## Spelling layers
Every text has an original-spelling version and a normalized version. The rules are in `NORMALIZATION.md`.

## Sources used (accessed 2026-11-22)
- De Vere canon: CELM, Edward de Vere entry (https://celm.folger.edu/authors/oxfordedwarddevereearlof.html), which follows May 1980 (*Studies in Philology* 77.5) and gives MS witnesses and May numbers. CELM states no reuse licence, so we use it for metadata only.
- May numbers 1, 5, 7 and 14 and their print-only sources come from the Shakespeare Oxford Fellowship "Twenty Poems" list (https://shakespeareoxfordfellowship.org/twenty-poems-de-vere). This is a secondary, advocacy source, used only to fill gaps CELM leaves. **Check these against May 1980 itself.**
- Shakespeare: Folger Shakespeare downloads, free for noncommercial use.
- Controls: EEBO-TCP. TCP IDs, STC numbers and imprints were read from the TCP catalogue CSV (github.com/textcreationpartnership/Texts) and each text's TEI header. Phase I transcriptions are public domain (released 1 January 2015) and Phase II transcriptions carry a CC0 1.0 waiver, per each file's TEI header. Page images are not covered.

## Open issues
- **Letters:** only one row so far (Lansdowne 33 f. 13r, holograph per Petti/CELM). The full list is Nelson, *Monstrous Adversary* (2003) pp. 487-9: 77 letters and memoranda, most autograph. Nelson's old Berkeley site is offline, so we need the book or library access.
- **Attribution flags:** May No. 5 (CELM cross-references it to Essex), No. 6 (the print is subscribed "M. B."), No. 13 (one copy is credited to "Sr E: D:"). Settle these before locking PREREG.
- May No. II goes to Dyer (per CELM), so it's out of the de Vere set. Nos. I, III and IV are "possible": held out of training and scored as candidates.
- **Text:** available for 14 of 16 secure de Vere poems: 13 from EEBO-TCP prints, plus No. 10 from Hannah 1870 in modernized spelling. The 1573 Bedingfield letter is also in. Text is also extracted for all single-author control collections. See `text/README.md`. The anthology rows (Vaux, Edwards, Breton, imposters) still need items filtered by signature.
- **Controls:** 22 rows covering 17 authors, plus 3 anthologies as the imposter pool. Each row is one whole collection. Poem-level items live in `text/tcp_poems.csv`, linked by TCP ID, rather than as manifest rows.
  - Dyer, Ralegh and Essex have no single-author print, so their poem lists have to be built from CELM or modern editions.
  - In the anthologies (Tottel, Paradise, Bowre, Arbor), use only items signed by the author or securely his. The Bowre and Arbor also contain Oxford items, so keep those out of the control set.
  - Sidney's *Certain Sonnets* (1598 folio, STC 22541) and the 1592 *Delia* have no TCP text. We use the 1594 *Delia* instead.
  - Check that the E.O. poems are actually in the 1576 *Paradise* TCP text (A21161), not only in later editions.
  - Balance sample sizes when sampling (PREREG section 3). Collections differ a lot in length.
- **Shakespeare songs from the plays:** not added yet.
