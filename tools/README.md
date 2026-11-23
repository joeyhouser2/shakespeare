# External tools

Tool folders under `tools/` are gitignored. This file records how to rebuild them.

## MorphAdorner 2.0.1 (Northwestern University)
- **Download:** https://morphadorner.northwestern.edu/morphadorner/download/morphadorner-2.0.1.zip (fetched 2026-11-22; 87,853,764 bytes).
  - sha256 `2d5f74c1d6b00252a2e13eb390f1d111cfb475518b53302495ad2819a3be2bb7`
- **Install:** unzip into `tools/morphadorner/` (zip kept in `tools/morphadorner_dl/`).
- **Licence:** NCSA-style open source, © 2006–2013 Northwestern University. Some bundled components have their own licences (see the MorphAdorner licence page). We use only the Early Modern English spelling data and tagger.
- **Runtime:** Java 1.6 or later. Tested with Java 8 (1.8.0_461). Called directly from `src/normalize/morphadorner_layer.py`, not through the bundled `.bat` scripts.
- **Data files used:** `emelexicon.lex`, `emetransmat.mat`, `emesuffixlexicon.lex`, `ememergedspellingpairs.tab`, `standardspellings.txt`, `spellingsbywordclass.txt`, with `emeplaintext.properties`.
