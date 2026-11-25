# Hand D spelling comparison: corpus

Rules are binding in `results/PREREG.md`, Amendment 3. This file says how to add texts.

## Status (2026-11-25)
Nothing collected yet. `manifest.csv` has only its header.

## Folders
| Path | Contents | In git? |
|---|---|---|
| `raw/` | Downloaded pages and scans, never edited | No |
| `text/<doc_id>.txt` | One cleaned original-spelling document per file, line breaks kept | No (source terms) |
| `manifest.csv` | One row per document, with the text file's sha256 | Yes |
| `standard_forms.csv` | Spelling → standard word; made by `spelling.py vocab` | Yes |

## Sources to fetch
| Source | Use | Terms | Approx. size |
|---|---|---|---|
| Internet Archive `bookofsirthomasm00brituoft` (Greg, Malone Society 1911), `_djvu.txt` and PDF | Hand D | Marked NOT_IN_COPYRIGHT there (US); Greg died 1959, so check status outside the US | 0.27 MB text, 9.4 MB PDF |
| Internet Archive `shakespeareshand00polluoft` (Pollard et al. 1923) | Hand D, second transcript | Published 1923 | 0.47 MB text, 10.9 MB PDF |
| Wayback Machine copy of `socrates.berkeley.edu/~ahnelson/oxlets.html` and linked pages | de Vere | Cite with acknowledgement. Reposting a substantial part of any letter needs the holding institution's permission | 44 personal and 18 tin-mining letter pages indexed, plus memoranda; likely under 2 MB (estimate) |
| bessofhardwick.org XML batch | Controls | Individual, non-commercial use only (as summarised by search; read the site's page before use) | not checked |
| Malone Society play manuscripts; *Henslowe Papers* (1907); EMMO | Controls | Not checked | not checked |

The controls are the bottleneck: the decision rule needs at least 10 eligible writers to run, and at least 19 before "de Vere is closer" can be concluded.

## Text file conventions
- Original spelling and line breaks. No modernizing, no silent expansion.
- Put **square brackets** round anything the editor supplied, expanded (including italic expansions) or marked doubtful: `lett[er]`, `p[ar]ish`. Illegible letters: `[.]`. The whole word is then skipped.
- Only the named writer's words. Leave out addresses or endorsements in other hands, speech prefixes, and editorial notes.
- Proofread Hand D line by line against the British Library images; OCR of a diplomatic transcript is unreliable.

## Manifest columns
`doc_id, writer, role (query|oxford|control), hand (must be holograph), genre, date, language, source, repository, shelfmark, url, license, access_date, path, sha256, include (1|0), notes`

Use writer `Oxford` with role `oxford` for de Vere, and `HandD` with role `query` for Hand D.

## Commands
`python src/score/spelling.py vocab`, then check every row of `standard_forms.csv` (set `checked` to 1), then `freeze`, commit, `validate`, commit, `main`.
