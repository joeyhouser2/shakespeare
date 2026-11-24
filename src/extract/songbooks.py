"""Extract lyric texts from songbooks (Dowland 1597-1612) in EEBO-TCP.

Songbooks print the first stanza only as music underlay (broken by repeats, hyphenated
syllables and <gap reason="music"> marks) and the remaining stanzas as plain verse.
Rule: within each song <div>, keep only <lg> stanzas none of whose lines contain a music gap.
The underlay stanza is NOT reconstructed (editorial), so stanza 1 is usually missing; each
output row records that. Songs with no clean stanza are listed with n_lines = 0 and no file.

The general extractor (tcp_verse.py) output for these volumes is not used for candidates.

Output: data/reference/text/songs/<TCP>/<TCP>_song_<nnn>.txt and data/reference/text/songs/songs.csv
Usage: python src/extract/songbooks.py
"""
import csv, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tcp_verse import text_of, local   # noqa: E402  (same text rules as the main extractor)

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/reference/raw/tcp"
OUT = ROOT / "data/reference/text/songs"
SONGBOOKS = ["A20689", "A20692", "A20693", "A20695", "A20696"]


def has_music_gap(el):
    return any(local(g.tag) == "gap" and g.get("reason") == "music" for g in el.iter())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for tcp in SONGBOOKS:
        root = ET.parse(RAW / f"{tcp}.xml").getroot()
        text_el = next(e for e in root.iter() if local(e.tag) == "text")
        songs = [d for d in text_el.iter() if local(d.tag) == "div" and d.get("type") == "song"]
        (OUT / tcp).mkdir(parents=True, exist_ok=True)
        kept = 0
        for k, song in enumerate(songs, 1):
            head = next((text_of(h, {"gaps": 0}) for h in song if local(h.tag) == "head"), "")
            stanzas, seen = [], set()
            for lg in song.iter():
                if local(lg.tag) != "lg" or has_music_gap(lg):
                    continue
                if any(local(c.tag) == "lg" for c in lg):      # only innermost stanzas
                    continue
                lines = [text_of(l, {"gaps": 0}) for l in lg.iter() if local(l.tag) == "l"]
                lines = [l for l in lines if l]
                key = tuple(lines)
                if lines and key not in seen:
                    seen.add(key); stanzas.append(lines)
            sid = f"{tcp}_song_{k:03d}"
            path = ""
            if stanzas:
                p = OUT / tcp / f"{sid}.txt"
                p.write_text("\n\n".join("\n".join(s) for s in stanzas) + "\n", encoding="utf-8")
                path = p.relative_to(ROOT).as_posix(); kept += 1
            n_lines = sum(len(s) for s in stanzas)
            rows.append(dict(song_id=sid, tcp_id=tcp, n=song.get("n", ""), head=head,
                             first_clean_line=stanzas[0][0] if stanzas else "", n_stanzas=len(stanzas),
                             n_lines=n_lines, n_words=sum(len(l.split()) for s in stanzas for l in s),
                             note="stanza 1 (music underlay) not reconstructed", path=path))
        print(f"{tcp}: {len(songs)} songs, {kept} with clean stanzas")
    with open(OUT / "songs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
