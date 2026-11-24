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

Candidate selection from the anthology volumes (unsigned or initialed items, at least 100 tokens) is still to do. Scoring waits for the PREREG amendment on removing candidates from the imposter pool.
