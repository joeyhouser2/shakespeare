# Harvest plan: Stage 1 candidates (CLAUDE.md Phase 2)

Status: **Source A downloaded 2026-11-23** (11 TCP volumes, about 4.2 MB, all valid with matching STC; 10 public domain, 1 CC0). Verse is extracted; songbooks go through `src/extract/songbooks.py`. Sources B–G not started.

**Findings so far (printed outside evidence):**
- *Englands Parnassus* (1600) attributes two passages outside May's canon to Oxford: "Loue is a discord and a strange diuorce" (**E. O.**, 18 lines) and "What plague is greater then the griefe of minde?" (**E. of Ox.**, 6 lines). Both are recorded in `data/candidates/`.
- The 1578 *Paradise* already signs May No. 6 "E. O." (1576 has "M.B."), and signs Nos. 2 and 5 "E. Ox.". Added to the reference manifest notes.
- Songbooks: Dowland prints stanza 1 only as music underlay, which isn't reconstructed. 73 of 107 songs have clean later stanzas; 26 of those reach 100 words.

**Framing (locked PREREG):** Stage 1 is **underpowered**. Any candidate that reaches θ is an exploratory lead, reported with the expected number of false leads (0.05 × N) and the *Paradise* venue caveat. The real value of the harvest is **outside evidence**: printed or manuscript signatures, initials, headings, and co-occurrence with known Oxford poems. That is how the 1585 *Paradise* "E.Ox." and the *Phoenix Nest* "E. O." findings came about. Stylometry ranks nothing on its own.

## Access rules found (checked 2026-11-23)
- **Folger sites** (First-Line Index, CELM, EMMO): `robots.txt` disallows ClaudeBot, anthropic-ai and Claude-Web by name and sets `ai-train=no, use=reference`. **No automated access** from this project's AI tooling. These sources are searched by hand in a browser, and the results are recorded here.
- **EEBO-TCP** (GitHub release): public domain (Phase I) or CC0 (Phase II). No restrictions. Automated fetching with the existing script (2 s between requests, logged with checksums).
- **Digital Bodleian:** no AI block in `robots.txt`. It has a documented Data API (JSON-LD; search endpoint with `q`, `fq`, `rows`). Images are CC BY-NC 4.0, "for research and private use". Light API use is OK; images only for items we transcribe.
- **British Library catalogue** (interim, after the 2023 cyber-attack): catalogue text CC BY. No API, and many digitised items are currently unavailable. Manual.
- **TNA Discovery:** `robots.txt` has no AI-specific block. The API terms couldn't be read (403 to automated fetch). Check by hand before any API use. Low priority: it holds letters (prose), not verse candidates.
- **Perdita Project:** static HTML index (first lines of poetry by women compilers). Low relevance. Manual only if needed.

## Source A: EEBO-TCP printed miscellanies and songbooks (automated)
**Candidate rule.** A poem is a candidate if it is:
- unsigned, initialed (any initials), or signed "Ignoto", "Anomos" or "Incerto", or carries any Oxford-related signature or heading;
- at least 100 tokens, and English;
- not by a control author or Shakespeare, judged by signature;
- not already in the manifest as an Oxford poem.

**Already downloaded** (candidates can be selected now, with no new fetch):

| Volume | TCP | Notes |
|---|---|---|
| *Phoenix Nest* 1593 | A11254 | many unsigned items |
| *England's Helicon* 1600 | A16273 | "Ignoto" and unsigned items |
| *A Poetical Rapsody* 1602 | A19943 | "Anomos", "Ignoto", unsigned |
| *Brittons Bowre* 1591 | A16731 | almost all unsigned; Oxford items present |
| *Arbor of Amorous Devices* 1597 | A16729 | unsigned |
| *Paradise* 1585 | A21166 | poems not in 1576, plus changed signatures |
| *Paradise* 1576 | A21161 | unsigned items only (signed ones are decoys or controls) |

**Proposed new downloads (11 files, about 4.2 MB):**

| Volume | TCP | Bytes | Why |
|---|---|---|---|
| *A Gorgious Gallery of Gallant Inventions* 1578 | A10147 | 320,196 | major 1570s miscellany, many unsigned poems |
| *A Handefull of Pleasant Delites* 1584 | A10831 | 173,862 | ballad miscellany |
| *Paradise* 1578 | A21162 | 289,353 | second edition; signature changes |
| *Englands Parnassus* 1600 | A16884 | 1,400,341 | quotations attributed by name; check for Oxford attributions |
| *A Poetical Rapsodie* 1611 | A19945 | 607,644 | enlarged edition |
| Dowland, *First Booke of Songes* 1597 | A20689 | 164,461 | anonymous lyrics |
| Dowland, *Second Booke* 1600 | A20692 | 102,440 | anonymous lyrics |
| Dowland, *Third Booke* 1603 | A20693 | 102,442 | anonymous lyrics |
| R. Dowland, *Musicall Banquet* 1610 | A20696 | 73,999 | anthology of ayres |
| Dowland, *Pilgrimes Solace* 1612 | A20695 | 113,852 | anonymous lyrics |
| *Bel-vedére* 1600 | A16269 | 804,375 | unattributed single lines; low value, mainly for first-line matching |

Not in TCP: Byrd's *Psalmes, Sonets and Songs* (1588), which prints "If women could be fair" (Oxford possible No. III), and Cotgrave's *Wits Interpreter* (1655).

**Method issue to settle by amendment before scoring.** Some candidates come from the imposter-pool volumes (*Phoenix Nest*, *Helicon*, *Rapsody*). If they stayed in the pool, each would be compared against itself. When such a candidate is scored, its own text must be removed from the pool documents first (the same leave-one-out rule used for authors). This is an implementation detail of the locked design, but it gets written down as a PREREG amendment before any candidate is scored.

**Songbook texts** are often printed as music underlay with repeats (as with Mundy). Dowland's books usually print the full lyric separately; check that during extraction. Underlay-only texts are skipped rather than reconstructed, because reconstruction is editorial.

## Source B: Folger First-Line Index (manual, by the project owner)
At https://firstlines.folger.edu/, Advanced search:
1. **Author** = `Oxford`; **Author** = `Oxenford`; **Author** = `Vere`; keyword `"E. O."`. Record every hit: first line, attribution as given, source or shelfmark, and whether it's already in CELM or our manifest.
2. For each Stage 1 candidate that becomes a lead, look up its first line to find other witnesses and their attributions.

Save the results as `data/candidates/folger_firstlines_manual.csv`, with the columns: query, first_line, attribution, source, shelfmark, notes, date_searched.

## Source C: CELM (manual)
- The Oxford entries (OxE 1–49) are already in the manifest metadata.
- To add: search CELM for copies of Oxford poems listed under **other** authors, and for poems listed elsewhere with Oxford-related ascriptions ("E.O.", "Vere", "Oxford"). Example: the "I am not as I seme to bee" cross-reference to Essex (EsR 15). Record them in the same CSV format as Source B.

## Source D: Digital Bodleian (light API use)
- Check whether MS Rawl. poet. 85 (Oxford Nos. 8, 11, 12, 13, 15, I, III and more) and MS Tanner 306 (No. 10) are digitized. If they are, they become the transcription source for Nos. 10, 12 and 13 in original spelling (Phase 3, HTR plus a hand check), and for any unsigned poems near the Oxford group in Rawl. poet. 85. That manuscript is the single richest Oxford source.
- At most a few dozen API requests, 2 s apart; images only for the folios we transcribe.

## Source E: British Library (manual)
- **Harley MS 7392** is a verse miscellany with many Oxford items (CELM OxE 9, 20, 25, 32, 37, 42, 44, 46). Its unsigned poems near the signed Oxford ones are prime candidates. Check whether it's digitised. If it isn't, it needs a reading-room visit or an imaging order.
- **Harley MS 6910, Add. MS 22583:** same check.

## Sources F and G: TNA Discovery, Perdita (deferred)
- **TNA:** for Oxford's letters (Nelson's list of 77). Read the API terms by hand first.
- **Perdita:** only if a lead points to a woman compiler's manuscript.

## Outputs
- `data/candidates/manifest.csv`: one row per candidate. Columns: candidate_id, source (TCP id or shelfmark), poem_id/path, signature/heading as printed, why selected, tokens, already-known attribution (from Folger/CELM checks), notes. Same provenance columns as the reference manifest.
- Candidate texts go through the same extraction and normalization pipeline. Raw files stay untouched.
