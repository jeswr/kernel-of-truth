#!/usr/bin/env python3
"""Watchlist discovery sweep (N-C §4.2 `discover`): run every kb/sources.json
watchlist against OpenAlex search (+ arXiv search side channel), dedupe against
the queue, append new kot-lit-queue/1 candidates.

Usage: python3 tools/kb/ingest/discover.py [--watchlist NAME] [--pages 2] [--dry-run]
"""

import argparse
import datetime
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, ".."))
import kb_common as K  # noqa: E402
import clients  # noqa: E402
import prescore as PS  # noqa: E402
from seed import existing_queue_ids, make_entry  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watchlist", default=None, help="run only this watchlist")
    ap.add_argument("--pages", type=int, default=2, help="OpenAlex pages of 50 per watchlist")
    ap.add_argument("--arxiv-max", type=int, default=40, help="arXiv search results per watchlist")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(K.SOURCES_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)
    terms = PS.load_terms()
    today = datetime.date.today().isoformat()
    known = existing_queue_ids()
    total_new = 0

    for wl in sources.get("watchlists", []):
        if args.watchlist and wl["name"] != args.watchlist:
            continue
        entries = {}
        source_tag = "watchlist:" + wl["name"]
        try:
            for w in clients.openalex_search(wl["openalex_search"], from_year=wl.get("from_year"), pages=args.pages):
                meta = clients.openalex_work_to_meta(w)
                entry = make_entry(meta, source_tag, terms, today)
                if entry and entry["id"] not in known and entry["id"] not in entries:
                    entries[entry["id"]] = entry
        except K.KotError as e:
            print("discover[%s]: OpenAlex degraded (%s)" % (wl["name"], e), file=sys.stderr)
        if wl.get("arxiv_query"):
            try:
                for meta in clients.arxiv_search(wl["arxiv_query"], max_results=args.arxiv_max):
                    entry = make_entry(meta, source_tag, terms, today)
                    if entry and entry["id"] not in known and entry["id"] not in entries:
                        entries[entry["id"]] = entry
            except K.KotError as e:
                print("discover[%s]: arXiv degraded (%s)" % (wl["name"], e), file=sys.stderr)
        print("discover[%s]: %d new candidates" % (wl["name"], len(entries)))
        if not args.dry_run:
            for entry in sorted(entries.values(), key=lambda e: e["id"]):
                K.append_jsonl(K.QUEUE_PATH, entry)
        known.update(entries)
        total_new += len(entries)

    print("discover: %d new candidates total" % total_new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
