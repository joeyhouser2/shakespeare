"""Fetch EEBO-TCP TEI XML files listed in data/reference/manifest.csv and data/candidates/tcp_sources.csv.

Dry run by default: prints what would be fetched. Pass --go to download.
Never overwrites an existing file. Logs sha256, size, URL and date to
data/reference/raw/tcp_fetch_log.csv (committed; the XML itself is gitignored).

Usage (from the repo root):
    python src/harvest/fetch_tcp.py            # dry run
    python src/harvest/fetch_tcp.py --go       # download
"""
import argparse, csv, datetime, hashlib, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/reference/manifest.csv"
CANDIDATE_SOURCES = ROOT / "data/candidates/tcp_sources.csv"
OUT = ROOT / "data/reference/raw/tcp"
LOG = ROOT / "data/reference/raw/tcp_fetch_log.csv"
URL = "https://raw.githubusercontent.com/textcreationpartnership/{id}/master/{id}.xml"
EXTRA = ["A21166"]  # 1585 Paradise: check which edition carries the E.O. poems
DELAY_S = 2.0
UA = "devere-stylometry-research/0.1 (python-urllib)"


def licence_of(data):
    t = data.decode("utf-8", "replace")
    if "CC0" in t or "Creative Commons 0" in t:
        return "CC0 1.0 (EEBO-TCP Phase II waiver)"
    if "public domain as of 1 January 2015" in t:
        return "Public domain (EEBO-TCP Phase I, released 1 Jan 2015)"
    return "UNKNOWN - check header"


def wanted_ids():
    ids = set(EXTRA)
    with open(MANIFEST, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ids |= set(re.findall(r"TCP (A\d{5})", r["printed_source"]))
    if CANDIDATE_SOURCES.exists():
        with open(CANDIDATE_SOURCES, encoding="utf-8") as f:
            ids |= {r["tcp_id"] for r in csv.DictReader(f)}
    return sorted(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="actually download")
    args = ap.parse_args()

    ids = wanted_ids()
    todo = [i for i in ids if not (OUT / f"{i}.xml").exists()]
    print(f"{len(ids)} TCP ids in manifest; {len(todo)} not yet downloaded")
    if not args.go:
        for i in todo:
            print("would fetch", URL.format(id=i))
        print("dry run; pass --go to download")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    new_log = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if new_log:
            w.writerow(["tcp_id", "url", "bytes", "sha256", "fetched_utc", "licence"])
        for n, i in enumerate(todo, 1):
            url = URL.format(id=i)
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
            except Exception as e:  # keep going; report at end
                print(f"[{n}/{len(todo)}] {i} FAILED: {e}", file=sys.stderr)
                continue
            dest = OUT / f"{i}.xml"
            with open(dest, "xb") as f:  # 'x' refuses to overwrite
                f.write(data)
            w.writerow([i, url, len(data), hashlib.sha256(data).hexdigest(),
                        datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                        licence_of(data)])
            lf.flush()
            print(f"[{n}/{len(todo)}] {i} {len(data):,} bytes")
            time.sleep(DELAY_S)


if __name__ == "__main__":
    main()
