# Reference corpus

`manifest.csv` has one row per text (poem, letter or song). Every row must record its source, shelfmark, URL, license and access date.
Entries are added only after checking them against the cited source. Don't fill them in from memory.

| Column | Meaning |
|---|---|
| item_id | Stable ID, e.g. `oxf-p-01` (poem), `oxf-l-01` (letter), `sid-p-01`, `shk-son-018` |
| author | Name as used in the project (Oxford, Sidney, Shakespeare, ...) |
| role | `target` (de Vere), `control`, `comparison` (Shakespeare, Stage 3 candidates) |
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
