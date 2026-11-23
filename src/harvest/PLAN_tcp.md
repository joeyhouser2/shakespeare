# Harvest plan: EEBO-TCP

Status: **run 2026-11-22.** All 22 files downloaded. Each one parsed as XML, and every STC number in a TEI header matches the manifest. Checksums are in `data/reference/raw/tcp_fetch_log.csv`.

## What
22 TEI XML transcriptions: every `TCP Axxxxx` cited in `data/reference/manifest.csv`, plus A21166 (the 1585 *Paradise of Dainty Devices*), which we need to check which edition carries the E.O. poems.

| TCP ID | Work | Bytes |
|---|---|---|
| A01513 | Gascoigne, Hundreth Sundrie Flowres (1573) | 1,198,515 |
| A01514 | Gascoigne, Posies (1575) | 1,566,540 |
| A01909 | Googe, Eglogs, Epytaphes, and Sonettes (1563) | 202,146 |
| A02226 | Greville, Certaine Learned and Elegant Workes (1633) | 1,029,985 |
| A03742 | Tottel, Songes and Sonettes (1557) | 691,230 |
| A06170 | Lodge, Phillis (1593) | 138,398 |
| A11254 | The Phoenix Nest (1593) | 276,318 |
| A12226 | Sidney, Astrophel and Stella (1591) | 219,052 |
| A12229 | Sidney, Arcadia (1590) | 1,605,553 |
| A12772 | Spenser, Amoretti and Epithalamion (1595) | 169,088 |
| A12782 | Spenser, Shepheardes Calender (1579) | 327,350 |
| A14019 | Turberville, Epitaphes, Epigrams, Songs and Sonets (1567) | 489,599 |
| A14822 | Watson, Hekatompathia (1582) | 302,464 |
| A16273 | Englands Helicon (1600) | 418,290 |
| A16729 | Breton, Arbor of Amorous Deuises (1597) | 170,646 |
| A16731 | Brittons Bowre of Delights (1591) | 171,120 |
| A18734 | Churchyard, Chippes (1575) | 579,560 |
| A19816 | Daniel, Delia and Rosamond augmented (1594) | 309,224 |
| A19943 | A Poetical Rapsody (1602) | 445,923 |
| A20824 | Drayton, Ideas Mirrour (1594) | 97,794 |
| A21161 | Paradyse of Daynty Deuises (1576) | 290,045 |
| A21166 | Paradyse of Daynty Deuises (1585) | 300,633 |
| | **Total** | **≈11.0 MB** |

The sizes come from HTTP HEAD requests made on 2026-11-22. Nothing has been downloaded.

## Where from
`https://raw.githubusercontent.com/textcreationpartnership/<ID>/master/<ID>.xml`. This is the TCP's official GitHub release. We couldn't use quod.lib.umich.edu because it returns 403 to automated requests.

## Terms
- The 19 Phase I files on GitHub say they are "public domain as of 1 January 2015". The 3 Phase II files (A01514, A19943, A21161) carry a CC0 1.0 waiver. Either way they can be reused freely. The TCP asks that the source be credited.
- Page images are not covered. We don't download any.

## Rate and behaviour
- One request at a time, 2 seconds apart: 22 requests, under a minute in total.
- Generic User-Agent, with no personal details in it.
- Never overwrites a file. Each download's sha256, size, URL and UTC time are logged to `data/reference/raw/tcp_fetch_log.csv`.

## Storage
- The XML goes to `data/reference/raw/tcp/`, which is gitignored and can be re-fetched. The fetch log is committed.
- Cleaned text goes to a separate folder in the next step, so raw files are never edited.

## Run
```
python src/harvest/fetch_tcp.py        # dry run (default)
python src/harvest/fetch_tcp.py --go   # download
```

## Next step after download
Extract verse from the TEI (keeping line breaks), split collections into one manifest row per poem, and write original-spelling text files. The TEI header's STC and ESTC numbers get checked against the manifest.

## Not covered here
The Folger Shakespeare texts (noncommercial licence, separate plan), Bedingfield's *Cardanus Comforte* (1573; TCP ID not yet looked up), and manuscript-only items such as the Dyer, Ralegh and Essex poems.
