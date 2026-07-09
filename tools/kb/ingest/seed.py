#!/usr/bin/env python3
"""Seed the lit-KB ingest queue from the programme's own verified lit reports
(N-C §4.2 "Bootstrap corpus"): every arXiv id / DOI cited across reports/*.md
is a known-relevant paper. Fetches metadata (arXiv API for arXiv ids —
authoritative abstracts; OpenAlex for DOIs + citation-count enrichment) and
appends kot-lit-queue/1 lines to kb/queue/candidates.jsonl.

Queue entries are CANDIDATES awaiting (next-phase) Haiku triage+extraction —
they are not records and carry no evidence status.

Usage: python3 tools/kb/ingest/seed.py [--reports-glob "reports/*.md"] [--dry-run]
"""

import argparse
import datetime
import glob
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, ".."))
import kb_common as K  # noqa: E402
import clients  # noqa: E402
import prescore as PS  # noqa: E402

ARXIV_CITE_RE = re.compile(r"(?:arXiv[:.]\s?|arxiv\.org/(?:abs|pdf)/)([0-9]{4}\.[0-9]{4,5})", re.IGNORECASE)
DOI_CITE_RE = re.compile(r"\b(10\.[0-9]{4,9}/[-._;()/:A-Za-z0-9]*[A-Za-z0-9])")


def extract_ids(paths):
    """-> ({arxiv ids}, {dois}, {id: [source files]})."""
    arxivs, dois, provenance = set(), set(), {}
    for path in sorted(paths):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(path, K.REPO_ROOT)
        for m in ARXIV_CITE_RE.finditer(text):
            aid = m.group(1)
            arxivs.add(aid)
            provenance.setdefault("arxiv:" + aid, set()).add(rel)
        for m in DOI_CITE_RE.finditer(text):
            cid = K.canonical_paper_id(doi=m.group(1))
            if cid is None:
                continue
            if cid.startswith("arxiv:"):
                arxivs.add(cid.split(":", 1)[1])
            else:
                dois.add(cid.split(":", 1)[1])
            provenance.setdefault(cid, set()).add(rel)
    return arxivs, dois, provenance


def existing_queue_ids():
    return {row["id"] for row in K.read_jsonl(K.QUEUE_PATH)}


def make_entry(meta, source, terms, today):
    cid = K.canonical_paper_id(arxiv=meta.get("arxiv"), doi=meta.get("doi"))
    if cid is None and meta.get("openalex"):
        cid = "url:openalex-" + meta["openalex"].lower()
    if cid is None:
        return None
    score, matched = PS.prescore(meta.get("title"), meta.get("abstract"), terms)
    cc = meta.get("citation_count")
    if cc and "as_of" not in cc:
        cc = dict(cc, as_of=today)
    return {
        "schema_version": "kot-lit-queue/1",
        "id": cid,
        "source": source,
        "title": meta.get("title") or "",
        "authors": meta.get("authors") or [],
        "year": meta.get("year"),
        "venue": meta.get("venue"),
        "doi": meta.get("doi"),
        "arxiv": meta.get("arxiv"),
        "openalex": meta.get("openalex"),
        "s2": meta.get("s2"),
        "abstract": meta.get("abstract"),
        "citation_count": cc,
        "prescore": score,
        "prescore_terms": matched,
        "status": "queued",
        "queued_at": today,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports-glob", default="reports/*.md")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = glob.glob(os.path.join(K.REPO_ROOT, args.reports_glob))
    arxivs, dois, provenance = extract_ids(paths)
    print("seed: %d arXiv ids + %d DOIs cited across %d files" % (len(arxivs), len(dois), len(paths)))

    terms = PS.load_terms()
    today = datetime.date.today().isoformat()
    known = existing_queue_ids()
    entries = {}

    # arXiv metadata (authoritative title/abstract)
    for meta in clients.arxiv_batch(sorted(arxivs)):
        src_files = sorted(provenance.get("arxiv:" + meta["arxiv"], []))
        entry = make_entry(meta, "seed:" + ";".join(src_files) if src_files else "seed:reports", terms, today)
        if entry and entry["id"] not in known:
            entries[entry["id"]] = entry

    # OpenAlex enrichment for the arXiv set (citation counts) — batched by DataCite DOI
    arxiv_dois = ["10.48550/arxiv." + a for a in sorted(arxivs)]
    try:
        for w in clients.openalex_by_dois(arxiv_dois):
            meta = clients.openalex_work_to_meta(w)
            cid = K.canonical_paper_id(arxiv=meta.get("arxiv"), doi=meta.get("doi"))
            if cid in entries:
                cc = meta.get("citation_count")
                entries[cid]["citation_count"] = dict(cc, as_of=today) if cc else None
                entries[cid]["openalex"] = meta.get("openalex")
                if not entries[cid]["venue"]:
                    entries[cid]["venue"] = meta.get("venue")
    except K.KotError as e:
        print("seed: OpenAlex enrichment degraded (%s) — continuing without citation counts" % e, file=sys.stderr)

    # non-arXiv DOIs via OpenAlex
    try:
        for w in clients.openalex_by_dois(sorted(dois)):
            meta = clients.openalex_work_to_meta(w)
            src_files = sorted(provenance.get(K.canonical_paper_id(doi=meta.get("doi")) or "", []))
            entry = make_entry(meta, "seed:" + ";".join(src_files) if src_files else "seed:reports", terms, today)
            if entry and entry["id"] not in known and entry["id"] not in entries:
                entries[entry["id"]] = entry
    except K.KotError as e:
        print("seed: OpenAlex DOI fetch degraded (%s)" % e, file=sys.stderr)

    print("seed: %d new queue entries (%d already queued)" % (len(entries), len(known)))
    if args.dry_run:
        return 0
    for entry in sorted(entries.values(), key=lambda e: e["id"]):
        K.append_jsonl(K.QUEUE_PATH, entry)
    print("seed: appended to %s" % os.path.relpath(K.QUEUE_PATH, K.REPO_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
