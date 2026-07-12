#!/usr/bin/env python3
"""Fetch + sha-pin the poc/pubeval benchmark data (stdlib only, no torch).

Pattern: poc/nsk1/build_clutrr_corpus.py corpus-build discipline — consume
only *released structured columns*, fail closed on format assertions, and pin
content hashes in a manifest (pin-on-first-fetch: the first successful fetch
writes data/manifest.json; every later fetch re-verifies sha256 of files on
disk and FAILS CLOSED on drift, ERR_DATA_DRIFT).

Sources ([search 2026-07-12] per the survey; licenses in benchmarks.LICENSES):
  ARC         : Hugging Face datasets-server rows API (plain JSON pages —
                avoids the parquet/pyarrow dependency the pinned image lacks)
  FOLIO       : raw JSONL from github.com/Yale-LILY/FOLIO data/v0.0 (MIT) —
                the paper authors' own release channel. Switched from the HF
                mirror (yale-nlp/FOLIO) 2026-07-12 T0 ops: that repo is
                GATED (auto click-through) and the box token has not accepted
                the terms; programmatically accepting a gate under the
                account's identity was ruled out. The GitHub v0.0 release
                carries 204 validation / 1004 train rows (the HF mirror lists
                203 validation) — counts pinned per-file below; the row
                schema (premises list / conclusion / label incl. 'Unknown')
                normalises through benchmarks._folio_norm unchanged.
  GSM8K       : raw JSONL from github.com/openai/grade-school-math (MIT)

Usage:
  python3 poc/pubeval/fetch_data.py            # fetch everything missing
  python3 poc/pubeval/fetch_data.py --verify   # verify pins only, no network
  python3 poc/pubeval/fetch_data.py --only arc_easy,arc_challenge,gsm8k
      # filename-prefix filter — added 2026-07-12 because yale-nlp/FOLIO is
      # GATED on the HF datasets-server (401 without an accepted-terms
      # token); lets the ungated sets pin without it. Pins are per-file, so
      # partial fetches stay fail-closed on later drift.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
MANIFEST = os.path.join(DATA_DIR, "manifest.json")

DS_API = "https://datasets-server.huggingface.co/rows"
GSM_RAW = ("https://raw.githubusercontent.com/openai/grade-school-math/"
           "master/grade_school_math/data/%s.jsonl")

# (filename, kind, spec). Row-count floors are fail-closed sanity assertions
# against silently-truncated fetches (public sizes per the survey §2.1/§3).
FOLIO_RAW = ("https://raw.githubusercontent.com/Yale-LILY/FOLIO/main/"
             "data/v0.0/folio-%s.jsonl")

SOURCES = [
    ("folio_validation.jsonl", "url",
     {"url": FOLIO_RAW % "validation", "min_rows": 150}),
    ("folio_train.jsonl", "url",
     {"url": FOLIO_RAW % "train", "min_rows": 800}),
    ("arc_easy_test.jsonl", "hf",
     {"dataset": "allenai/ai2_arc", "config": "ARC-Easy",
      "split": "test", "min_rows": 2000}),
    ("arc_easy_train.jsonl", "hf",
     {"dataset": "allenai/ai2_arc", "config": "ARC-Easy",
      "split": "train", "min_rows": 2000}),
    ("arc_challenge_test.jsonl", "hf",
     {"dataset": "allenai/ai2_arc", "config": "ARC-Challenge",
      "split": "test", "min_rows": 1000}),
    ("arc_challenge_train.jsonl", "hf",
     {"dataset": "allenai/ai2_arc", "config": "ARC-Challenge",
      "split": "train", "min_rows": 1000}),
    ("gsm8k_test.jsonl", "url", {"url": GSM_RAW % "test", "min_rows": 1300}),
    ("gsm8k_train.jsonl", "url", {"url": GSM_RAW % "train", "min_rows": 7000}),
]

PAGE = 100  # datasets-server max rows per request


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _get(url, retries=4):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "kot-pubeval-fetch/1 (research; stdlib urllib)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 ** i)
    raise SystemExit("ERR_FETCH: %s: %s" % (url, last))


def fetch_hf_rows(dataset, config, split):
    """Page through the datasets-server rows API; return raw row dicts."""
    rows, offset, total = [], 0, None
    while total is None or offset < total:
        url = ("%s?dataset=%s&config=%s&split=%s&offset=%d&length=%d"
               % (DS_API, urllib.request.quote(dataset, safe=""),
                  urllib.request.quote(config, safe=""), split, offset, PAGE))
        j = json.loads(_get(url))
        if "rows" not in j:
            raise SystemExit("ERR_FETCH: unexpected datasets-server reply for "
                             "%s/%s/%s at offset %d: %s"
                             % (dataset, config, split, offset,
                                str(j)[:300]))
        total = j.get("num_rows_total", 0)
        batch = [r["row"] for r in j["rows"]]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
        print("  %s/%s/%s: %d/%s rows" % (dataset, config, split, offset, total))
    return rows


def fetch_one(name, kind, spec):
    dest = os.path.join(DATA_DIR, name)
    if kind == "hf":
        rows = fetch_hf_rows(spec["dataset"], spec["config"], spec["split"])
        body = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                       for r in rows)
    else:
        body = _get(spec["url"]).decode("utf-8")
        rows = [ln for ln in body.splitlines() if ln.strip()]
    n = len(rows)
    if n < spec["min_rows"]:
        raise SystemExit("ERR_FETCH_TRUNCATED: %s has %d rows < floor %d"
                         % (name, n, spec["min_rows"]))
    with open(dest, "w", encoding="utf-8") as f:
        f.write(body)
    return {"sha256": sha256_file(dest), "rows": n,
            "source": spec.get("url") or ("hf-datasets-server:%s/%s/%s"
                                          % (spec["dataset"], spec["config"],
                                             spec["split"])),
            "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def main():
    verify_only = "--verify" in sys.argv
    sources = SOURCES
    if "--only" in sys.argv:
        want = [w.strip() for w in
                sys.argv[sys.argv.index("--only") + 1].split(",") if w.strip()]
        sources = [s for s in SOURCES
                   if any(s[0].startswith(w) for w in want)]
        if not sources:
            raise SystemExit("ERR_ONLY_EMPTY: --only %r matches no source"
                             % want)
    os.makedirs(DATA_DIR, exist_ok=True)
    man = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as f:
            man = json.load(f)

    changed = False
    for name, kind, spec in sources:
        dest = os.path.join(DATA_DIR, name)
        if os.path.exists(dest):
            sha = sha256_file(dest)
            if name in man and man[name]["sha256"] != sha:
                raise SystemExit(
                    "ERR_DATA_DRIFT: %s sha %s != pinned %s — refuse to "
                    "proceed; delete data/ deliberately to re-pin"
                    % (name, sha[:12], man[name]["sha256"][:12]))
            if name not in man:
                raise SystemExit("ERR_DATA_UNPINNED: %s exists but is not in "
                                 "the manifest — delete it or re-pin "
                                 "deliberately" % name)
            print("ok  %s (%d rows, %s)" % (name, man[name]["rows"], sha[:12]))
            continue
        if verify_only:
            print("missing  %s (verify-only, skipping fetch)" % name)
            continue
        print("fetching %s ..." % name)
        man[name] = fetch_one(name, kind, spec)
        changed = True
        print("pinned  %s (%d rows, %s)"
              % (name, man[name]["rows"], man[name]["sha256"][:12]))

    if changed:
        with open(MANIFEST, "w") as f:
            json.dump(man, f, indent=2, sort_keys=True)
            f.write("\n")
        print("wrote %s" % MANIFEST)

    # LICENSE-NOTICE next to the data (corpus-build discipline).
    notice = os.path.join(DATA_DIR, "LICENSE-NOTICE.md")
    if not os.path.exists(notice) and not verify_only and changed:
        with open(notice, "w") as f:
            f.write(
                "# poc/pubeval data — license notice\n\n"
                "Fetched benchmark data; NOT authored by this project.\n\n"
                "- FOLIO: MIT (Yale-LILY/FOLIO, arXiv:2209.00840) "
                "[search 2026-07-12]\n"
                "- ARC (Easy/Challenge): CC BY-SA 4.0 (AI2) "
                "[search 2026-07-12]\n"
                "- GSM8K: MIT (openai/grade-school-math) "
                "[search 2026-07-12]\n\n"
                "Re-verify each license at source before any frozen use "
                "(survey riders, PROPOSED-ASM-1590..1596).\n")
        print("wrote %s" % notice)


if __name__ == "__main__":
    main()
