# Stage 1 candidates

Plan: `src/harvest/PLAN_candidates.md`. Under the locked PREREG, Stage 1 is **underpowered**: any candidate's stylometric score is an exploratory lead only. The evidence that counts is outside the text: signatures, headings, and where a poem sits in a book or manuscript.

- `tcp_sources.csv`: EEBO-TCP volumes used as candidate sources, with STC numbers, licence and access date. `src/harvest/fetch_tcp.py` reads it.
- `manifest.csv`: one row per candidate (source, locator, signature as printed, why selected, known attribution, provenance).
- `text/`: candidate texts in original spelling, as transcribed by TCP.

## Candidates so far (2026-11-23)
| ID | Source | Printed attribution | First line | Lines |
|---|---|---|---|---|
| cand-parnassus-01 | *Englands Parnassus* (1600), topic "Loue" | **E. O.** | "Loue is a discord and a strange diuorce," | 18 |
| cand-parnassus-02 | *Englands Parnassus* (1600), topic "Minde" | **E. of Ox.** | "What plague is greater then the griefe of minde?" | 6 |

Neither is in May's (1980) canon. *Englands Parnassus* attributions are known to be unreliable in places. **Next checks (manual):** May 1980, on why they were excluded; the Folger First-Line Index and CELM, for other witnesses and attributions.

## Anthology candidates (`src/harvest/select_candidates.py`, run 2026-11-23)
`selection_log.csv` records every poem considered, with its decision and the reason.

**Rules:**
- **Kept:** a poem whose attribution is absent, initials only, or a pseudonym.
- **Where the attribution comes from:** the printed signature; failing that, an author named in the heading as initials or a titled or capitalized name; failing that, the *Poetical Rapsody* section attribution.
- **Excluded:**
  - any poem where some copy, found by matching first lines across all 40 volumes plus the songbooks, names another author, or carries the initials of a control author, Shakespeare, a Davison or John Davies;
  - "Shep. Tonie" (Munday);
  - Oxford reference poems and their variants (fuzzy first-line match, or the listed variant *Helicon* "What Sheepheard can expresse" = No. 14).
- **Duplicates:** reprints merge into one candidate, using the earliest copy's text. Every copy and its signature is listed in `witnesses`.

**Result:** 716 candidates (including the two *Parnassus* rows), **467 scorable** (at least 100 tokens).

| Attribution class | Scorable | Too short |
|---|---|---|
| unsigned | 314 | 226 |
| initials (95 of them "A. W.", by *Rapsody* section) | 135 | 21 |
| pseudonym ("Ignoto" ×13, "ANOMOS", "Yloop", "Incerto") | 17 | 1 |
| Oxford-signed (*Englands Parnassus*) | 1 | 1 |

**By source (earliest copy):**
- *Poetical Rapsody*: 1611, 167; 1602, 114
- *Gorgious Gallery* 1578: 92
- *Phoenix Nest* 1593: 60
- *Brittons Bowre* 1591: 52
- *Arbor* 1597: 42
- *England's Helicon* 1600: 40
- *Handefull* 1584: 31
- *Paradise*: 1576, 24; 1585, 12; 1578, 7
- Dowland songbooks: 73 in total

**What scoring could give (locked PREREG):** Stage 1 is underpowered. At θ (5% FPR on decoys), about **0.05 × 467 ≈ 23 false leads** are expected by chance alone. Any score is therefore only a pointer for outside checks: other copies, signatures, manuscript context. A score is never evidence on its own.

**Before scoring:**
1. A PREREG amendment: remove a candidate's own text from the imposter pool when that candidate comes from a pool volume (*Phoenix Nest*, *Helicon*, 1602 *Rapsody*).
2. The manual Folger First-Line Index and CELM checks on the two Oxford-signed *Parnassus* passages.
