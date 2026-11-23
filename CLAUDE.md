# De Vere Manuscript Search

Goal: find digitized texts (letters, verse, anonymous or initialed items) that may be by
Edward de Vere, 17th Earl of Oxford (1550-1604) but are not currently attributed to him,
using a small securely attributed reference set plus controls.

This file is the project brief. Read it first in any Claude Code session.

## Ground rules
- A stylometric hit is a LEAD, not an attribution. Needs outside evidence (hand, provenance, scribal note, dating).
- Small reference corpus (a couple dozen poems plus letters), so expect weak signal. Report uncertainty honestly.
- Set the false-positive threshold BEFORE looking at candidate results. Log it in results/PREREG.md.
- Keep raw images/transcripts, cleaned text, and results in separate folders. Never overwrite raw data.
- Record source, shelfmark, URL, license, and access date for every item.
- Stage 1 target is de Vere's own corpus. Later stages compare him (and other candidates) with
  Shakespeare, but Shakespeare is one comparison author among several, not a conclusion to prove.
  Hypotheses and thresholds go in results/PREREG.md before looking; "not a match" is a reportable result.
- See plan.md for the three-stage plan and order of work.

## Folder layout
- data/reference/    securely attributed de Vere poems and letters, plus control authors
- data/candidates/   harvested candidate items (anonymous, "E.O.", "Oxenford", disputed)
- data/transcripts/  HTR output (Transkribus or similar) and manual corrections
- src/               scripts
- results/           scores, plots, ranked leads, PREREG.md

## Phase 1: Reference set
1. Securely attributed de Vere poems (canon per Steven May, "The Elizabethan Courtier Poets"; verify against the text).
2. His letters. Tag each as holograph (his own hand) or secretary copy. Spelling analysis only on holographs.
3. Controls: other courtier poets of the period (Sidney, Dyer, Raleigh, Vaux, Gascoigne, etc.). Roughly 10+ authors, balanced sample sizes where possible.
4. Normalize spelling carefully: keep one original-spelling version and one normalized version. Document the rules.

## Phase 2: Harvest candidates
Search for "Oxenford", "Oxford", "E.O.", "Earl of Oxenford" and anonymous items in:
- Folger Union First-Line Index of English Verse
- Early Modern Manuscripts Online (Folger) and the Perdita Project
- EEBO-TCP (printed miscellanies and anthologies, e.g. Paradise of Dainty Devices)
- The National Archives (Discovery catalogue), Cecil Papers, Lansdowne MSS, British Library
- Flag items that are anonymous, initialed, or disputed. Keep catalog IDs.
Check each source's terms of use before bulk downloading.

## Phase 3: Get text
- Page images via library IIIF links where offered.
- HTR with Transkribus (or similar); hand-check a sample and report character error rate.
- Keep line breaks; they matter for verse features.

## Phase 4: Score candidates
- Features: character n-grams, function-word frequencies, rhyme scheme, meter, spelling habits (holographs).
- Methods suited to short texts: Burrows' Delta, General Imposters method. R package `stylo` and Python both work.
- Handwriting: refer shortlisted holographs to a paleographer. Do not judge hands automatically.

## Phase 5: Validate
- Leave-one-out on known de Vere poems.
- Blind tests with decoys from control authors.
- Report precision/recall at the pre-set threshold.

## Phase 6: Triage
- Rank leads. For each: provenance, dating, scribal notes, other candidate authors.
- Write up findings with limits stated. Share data and code.

## Suggested first session (do these in order)
1. Initialize git in this folder and add a .gitignore for data/transcripts raw images and large files.
2. Create results/PREREG.md with the planned methods and threshold placeholders.
3. Build the reference corpus: list every securely attributed poem/letter with source, in data/reference/manifest.csv.
4. Draft a harvest script plan per source (what it queries, rate limits, terms of use). Ask before bulk downloading.

## Environment notes
- Windows machine; Python available via Anaconda. Prefer a project venv or conda env named devere.
- Open this folder in Claude Code (run `claude` from Documents/GitHub/devere-manuscript-search).
