# Spelling normalization

Every text exists in two layers:

| Layer | Folder | Used for |
|---|---|---|
| Original spelling | `text/orig/`, `text/special/` | Spelling-habit features (holographs only), checking against sources |
| Normalized, rules | `text/norm/` (same relative paths) | Metre and syllable features (keeps syncopated spellings such as "lingring"); input to the next layer |
| Normalized, MorphAdorner | `text/norm_ma/` (same relative paths) | Function words, character n-grams, vocabulary: anything compared across authors and printers |

The normalized layer is made only by `src/normalize/normalize.py`. Never edit it by hand: change a rule here and in the script, then rerun.

## Why normalize
Early printed spelling mostly reflects the typesetter, not the author. The same word appears as "loue", "love", "lovve". Without normalization, function-word counts and character n-grams would partly measure printing houses and decades rather than authors. That matters most for the Stage 2 comparison: de Vere is in 1570s prints, Shakespeare in a modern-spelling edition.

## Aim and limits
**Aim:** make function words and common spellings comparable across texts. Change only what can be changed without guessing.

**Not done on purpose:**
- **Content words** are left as printed beyond the typographic rules: "hart", "beautie", "doubled consonants", final -e. A full modernizer would need a dictionary and context.
- **Ambiguous forms** are left alone: "then" (also = "than"), "to"/"too", "of"/"off", "ye" (a real pronoun).

Content-word spelling is handled by a second pass with MorphAdorner (below), so this layer can stay conservative.

## Rules, applied in this order
1. **Unicode:** NFC; non-breaking space → space.
2. **Typographic letter forms:** ſ → s; Ʋ → V; é → e (some prints mark a long e this way: "thée", "bée"); "VV"/"vv" → W/w and "UU"/"uu" → W/w (TCP types w as two v's or two u's).
3. **Drop caps:** a word typed with two capitals then lowercase ("FRaud", "THe") → one capital ("Fraud", "The").
4. **Superscript abbreviations** (encoded as Unicode modifier letters in the original layer): yᵉ → the, yᵗ → that, yᵘ → thou, wᵗ → with, wᶜ → which. "y^•" (superscript illegible; 61 cases, 20 of them in texts used for analysis, 1 in Oxford material) → "that" if the next word is a pronoun, verb, or function word, or ends in -eth/-ed ("y^• they" → "that they"); otherwise "the" ("y^• earth" → "the earth"). Both guesses are counted in the log. Any other superscript has its marker dropped.
5. **Abbreviation stroke** (combining macron, U+0304, over a vowel): → that vowel + "m" before b/p/m, otherwise + "n". "cōmaund" → "commaund", "thē" → "then". The "them"/"then" ambiguity is not resolved.
6. **Symbols:** "&c" → "etc"; "&" → "and"; ꝙ (quod) removed; ꝰ → "us"; ꝑ → "per"; ꝓ → "pro".
7. **u/v by position:**
   - A word-initial v before a consonant → u ("vnto" → "unto", "vp" → "up", "vse" → "use").
   - A u between vowels inside a word → v ("loue" → "love", "euer" → "ever", "haue" → "have"). y counts as a vowel.
   - Listed stems where u follows r/l before e → v: serue, deserue, preserue, obserue, reserue, conserue, carue, starue, swerue, curue, nerue, solue, resolue, dissolue, absolue, delue, twelue, selue(s), halue, salue, calue, shelue, wolue(s), silue(r) ("serue" → "serve").
8. **i/j by position:** a word-initial I/i followed by a vowel → J/j ("ioy" → "joy", "Ioue" → "Jove", "iust" → "just"). The single word "I" is untouched.
9. **Lexical variants:** whole words, case kept. Only forms with one reading:
   - mee, hee, shee, wee, yee → me, he, she, we, ye
   - doe, goe, soe, noe, doo, dooth → do, go, so, no, do, doth
   - beene, beyng, beinge → been, being
   - onely, onlie, verie, anie, manie, eche → only, very, any, many, each
   - thei, theyr, theyre, thier, thyne, myne → they, their, their, their, thine, mine
   - wyth, whiche, suche, muche, yf, hir, owne → with, which, such, much, if, her, own
   - shal, wyll, wil, al, untill, tyll → shall, will, will, all, until, till
   - ys, hys, thys, wher, whan, ther → is, his, this, where, when, there
   - sayd, sayde, saide → said

   **"bee"** → "be" unless the previous word is "the", "a", "an", "busy" or "humble" (the insect: de Vere No. 2 has "the Bee"). **"doe"** follows the same rule (the deer).

## Checks
- `src/normalize/test_normalize.py` has a test for each rule, including the cases where the rule must *not* fire ("ye howling hounds", "the Bee", "true", "I am").
- `text/norm/normalize_log.csv` counts how often each rule fired per file, so unusual texts stand out.

## Texts that are already modernized
The Folger Shakespeare and Hannah 1870 (de Vere No. 10) are in modern spelling. They go through the same rules, which change almost nothing. They should only ever be compared with other texts in the normalized layer, never the original-spelling one.


## Layer 2: MorphAdorner (`text/norm_ma/`)
`src/normalize/morphadorner_layer.py` runs MorphAdorner 2.0.1's Early Modern English standardizer on the rules layer. It then puts the standard spellings back onto our lines, because MorphAdorner drops line breaks; all 814,088 tokens realign. Part-of-speech tags and lemmas are saved in `text/adorned/*.tsv`. That folder is gitignored and can be regenerated in about 90 seconds. Tool details are in `tools/README.md`.

**MorphAdorner's output is not taken as a whole.** On first review it was modernizing grammar and guessing from context, which would erase authorship markers and introduce errors:
- doth → does (2,845 times), ye → you (445), whilst → while
- an → and (528, mostly the article), fall → fallen (494), sight → sighed (460), sound → found, deare → deer, 'tis → this

So a change is accepted only if all of these hold (see `accept()` in the script):
1. The input is a real variant spelling (not in MorphAdorner's standard-spelling list), **or** the two forms differ only in orthography: final -e, doubled letters, y/i, final -ie/-y (beare → bear, sonne → son, fayre → fair).
2. Neither form is a protected grammar or word-choice marker: doth/does, hath/has, ye/you, the thou-forms and -st verbs, whilst/while, amongst/among, betwixt/between, 'tis, o/oh, an/and, then/than, to/too, of/off.
3. It doesn't modernize an -eth/-est ending.
4. It doesn't add an apostrophe (no possessives guessed).
5. The first letter is the same, and the length changes by at most 3.
6. The input isn't an elision ending in an apostrophe (t', th'). Those are kept as printed for the metre.
7. The pair isn't on the hand-reviewed reject list (past→passed, mans→men, faine→feign, borne→born, lose→loose, heer→her, divers→diverse, …).

**Result (2026-11-22):** 104,236 changes accepted (12,155 distinct pairs) and 28,384 rejected (2,053 distinct). Both lists are saved for review: `text/norm_ma/changes.csv` and `text/norm_ma/rejected.csv`.

**Known limits:**
- Some spellings stay unstandardized where the input is itself a standard word (e.g. hart → heart is rejected, because "hart" is a real word).
- Context-chosen standards accepted through the spelling-shape rule (e.g. weare → wear, where "were" was sometimes meant) can still be wrong now and then.
- Review the top of `changes.csv` again whenever the corpus changes.
