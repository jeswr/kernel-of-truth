#!/usr/bin/env python3
"""gen_mock_phrasings — MOCK-ONLY scaffold phrasings for the NLB harness.

QUARANTINE (docs/design-nl-boundary-l3a-parse-a5-nl.md sections 5.6, 9, 10.6):
these template phrasings are NON-BLIND scaffold English generated FROM the
gold queries. They exercise pipeline MECHANICS only (--mock), live under
poc/nlb-mock/ (never data/), are never shown to any authoring identity, and
can preview NOTHING about the primary. The real inputs are the blind-authored
held-out phrasing corpora (design doc section 5).

Deterministic: pure functions of the pinned eval + minted-urns files.
The malformed stratum is skipped (FK-NLB-5 — excluded from the NL leg).
"""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_ENT_PREFIX = "urn:kotw:v0:"


def load_urn2slug(root):
    m = {}
    for corpus in ("kernel-v0", "molecules-v0", "code-v0"):
        p = os.path.join(root, "data", corpus, "minted-urns.jsonl")
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    m[r["urn"]] = r["sourceId"]
    return m


def _ent(urn):
    return urn[len(_ENT_PREFIX):] if urn.startswith(_ENT_PREFIX) else urn


def _rel_word(urn, urn2slug):
    return urn2slug.get(urn, "UNMAPPABLE").replace("-", " ")


def _phrase_l3a(q, urn2slug):
    op = q.get("op")
    if op == "instance":
        return "is %s a %s" % (_ent(q.get("entity", "")),
                               _rel_word(q.get("concept", ""), urn2slug))
    r = _rel_word(q.get("rel", ""), urn2slug)
    e = _ent(q.get("subject", ""))
    inv = "inverse " if q.get("direction") == "inverse" else ""
    if op == "unique":
        return "who is the %s%s of %s" % (inv, r, e)
    if op == "lookup":
        return "list the %s%s of %s" % (inv, r, e)
    if op == "count":
        return "how many %s%s for %s" % (inv, r, e)
    return None


def _phrase_a5(q, urn2slug):
    op = q.get("op")
    if op == "instance-of":
        return "is %s a %s" % (_ent(q.get("entity", "")),
                               _rel_word(q.get("concept", ""), urn2slug))
    e = _ent(q.get("of", ""))
    return {
        "callers-of": "which functions call %s" % e,
        "callees-of": "which functions does %s call" % e,
        "imports-of": "which modules does %s import" % e,
        "imported-by": "which modules import %s" % e,
        "contains": "what does %s contain" % e,
        "contained-in": "what contains %s" % e,
        "where-defined": "where is %s defined" % e,
    }.get(op)


def generate(root, vertical):
    """-> (phrasings [{qid, text, mock}], included_qids set)."""
    eval_path = os.path.join(
        root, "data", "l3a-eval" if vertical == "l3a" else "a5-eval",
        "queries.jsonl")
    urn2slug = load_urn2slug(root)
    phrasings, skipped_covered = [], []
    with open(eval_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["family"] == "malformed":
                continue  # FK-NLB-5
            q = rec.get("query") or {}
            text = (_phrase_l3a(q, urn2slug) if vertical == "l3a"
                    else _phrase_a5(q, urn2slug))
            if text is None:
                if rec["class"] == "covered":
                    skipped_covered.append(rec["qid"])
                # non-templatable control: scaffold that must ERR_PARSE
                text = "untemplatable control query %s" % rec["qid"]
            phrasings.append({"qid": rec["qid"], "text": text, "mock": True})
    if skipped_covered:
        raise AssertionError(
            "mock generator missed covered templates: %s" % skipped_covered[:5])
    return phrasings


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=("l3a", "a5"))
    ap.add_argument("--root", default=_ROOT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    phr = generate(args.root, args.vertical)
    out = args.out or os.path.join(
        args.root, "poc", "nlb-mock", args.vertical, "phrasings.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for p in phr:
            f.write(json.dumps(p, sort_keys=True) + "\n")
    print("wrote %d mock phrasings -> %s" % (len(phr), out))


if __name__ == "__main__":
    main()
