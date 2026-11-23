# Folger Shakespeare (cross-check only)

These are modern-spelling texts of Shakespeare's Sonnets, *Venus and Adonis*, *Lucrece* and *The Phoenix and Turtle*, extracted from the Folger Shakespeare XML by `src/extract/folger_verse.py`.

**Source:** Folger Digital Texts, https://www.folger.edu/explore/shakespeares-works/download/ (XML; downloaded 2026-11-22). Checksums are in `data/reference/raw/folger_fetch_log.csv`.

**Licence:** CC BY-NC 3.0 (https://creativecommons.org/licenses/by-nc/3.0/). Credit Folger Digital Texts as the source. **Changes made:** the text is extracted from XML into plain text, one verse line per line; editorial apparatus and line numbers are dropped. Folger has no digital text of *A Lover's Complaint*.

**Use:** these texts are **not** the analysis texts. Stage 2 uses the first editions from EEBO-TCP (1609 *Sonnets* with *A Lover's Complaint*, 1593 *Venus*, 1594 *Lucrece*, *Phoenix and Turtle* from the 1611 reissue of *Love's Martyr*). Those are early prints in original spelling, the same kind of source as the controls, and they go through the same normalization. Folger is used to check those texts:
- **Line counts** match exactly: 154 sonnets (Sonnet 99 has 15 lines, Sonnet 126 has 12), *Venus* 1,194 lines, *Lucrece* 1,855, *Phoenix and Turtle* 67.
- **Sonnet first lines** all match (lowest similarity 0.92). The sonnets are mapped by position, because the 1609 Quarto's printed sonnet numbers contain misprints, which the TCP encoding copies.
- **Word-for-word agreement** between our normalized 1609 *Sonnets* and Folger averages **0.924** for the MorphAdorner layer and **0.820** for the rules layer. The remaining differences are partly Folger's editorial emendations ("their" → "thy", "then" → "than", "least" → "lest"), which we deliberately leave unapplied, and partly spellings left unchanged ("deare", "brest", "shew").
