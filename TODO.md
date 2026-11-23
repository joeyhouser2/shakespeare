# TODO

Open tasks that need a person, library access, or a decision. Keep this list short and specific.

## Find original-spelling texts for de Vere poems

These are the gaps in the secure canon (May 1980). Original spelling matters because the spelling and character n-gram features are computed on it. Until these are found, the poems below are left out of those features or used only in the normalized layer.

### May No. 10, "Fain would I sing but fury makes me fret": modernized text only
- **What we have now:** Hannah 1870, pp. 144–5, with spelling modernized by the editor (`data/reference/text/edited/`).
- **Where the original is:**
  - Bodleian MS Tanner 306, Vol. I, f. 115v. Untitled; CELM OxE 3.
  - Same MS, f. 193r, subscribed "Earle of Oxenforde"; CELM OxE 4. This is Hannah's source ("p. 193").
- **Leads, roughly easiest first:**
  1. **Bliss's edition of Wood's *Athenae Oxonienses* / *Fasti*, vol. i, col. 177 (1813–20).** Hannah says Bliss printed the poem from the Tanner MS. Bliss may keep the manuscript spelling. It's public domain, so check Internet Archive or Google Books for a scan with OCR.
  2. **Grosart, *Miscellanies of the Fuller Worthies' Library*, vol. IV (1872).** Grosart usually keeps old spelling. HathiTrust has it (record 011225480 may be this volume) but blocks automated access, so open it in a browser.
  3. **Digital Bodleian:** search "Tanner 306". No facsimile was found on 2026-11-22. Tanner 306/2 is in an Adam Matthew subscription collection, which a university library may give access to.
  4. **May 1980 (*Studies in Philology* 77.5), No. 10,** or May 1991, p. 277. These are an old-spelling edition from the MS, but still in copyright, so use them only for checking.
- **Done when:** an original-spelling text is in `data/reference/text/`, the manifest row points to it, and its notes give the witness (f. 115v or f. 193r) and the transcription source.

### May No. 12, "Wing'de with desyre, I seeke to mount on hyghe": no text
- **Witness:** Bodleian MS Rawl. poet. 85, ff. 48v–49r. CELM OxE 31. No early print is known.
- **Leads:** Grosart 1872 (as above); Digital Bodleian; May 1980 No. 12 / May 1991 pp. 278–9 for checking.

### May No. 13, "Wheras the Harte at Tennysse playes and men to gaminge fall": no text
- **Witnesses:** Bodleian MS Rawl. poet. 85, f. 106r (CELM OxE 23), plus other MS copies (OxE 24–28). One copy is headed "by Sr E: D:", which is an attribution question to settle.
- **Print:** Cotgrave, *Wits Interpreter* (1655). Not in EEBO-TCP. Check EEBO page images or Wing C6371-73 for a later edition that might be in TCP.
- **Leads:** Grosart 1872; Digital Bodleian; May 1980 No. 13.

## Decisions needed
- **Hand D spelling comparison** (plan.md Stage 2b): get the Hand D transcription (Pollard 1923, public domain) and de Vere holograph letter transcriptions, then pre-register.

## Other open items
- **Check the Hannah No. 10 OCR text** against the page image (Internet Archive `courtlypoetsfro00wottgoog`, pp. 144–5).
- **Oxford letters:** only 2 are in so far. The full list (77 items) is in Nelson, *Monstrous Adversary* (2003), pp. 487–9. Nelson's old Berkeley site is offline.
- **Settle the attribution conflicts before locking PREREG:** May Nos. 5, 6, 13 and 15 (see `data/reference/text/README.md`).
