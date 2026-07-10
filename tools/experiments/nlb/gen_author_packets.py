#!/usr/bin/env python3
"""gen_author_packets — deterministic author-packet generation for the blind
EVAL/PROBE phrasing build (design doc section 5; EVAL-BUILD-SPEC.md).

    python3 tools/experiments/nlb/gen_author_packets.py --vertical l3a \
        [--out-dir data/nlb-phrasings-l3a/packets]

Packets are the ONLY per-item context an authoring identity receives (plus
the pinned prompt file). Each packet line carries:
    {"qid", "shape", "rel_label"|"concept_label", "entity_label"[, "entity_label_2"]}
and deliberately does NOT carry: family name, covered/control class, expected
answer or refusal code, URNs, lexicon data, or any other item's data.

The shape id encodes the query's SEMANTICS (op + which side of the relation
the entity sits on), which the author must have to phrase the question
faithfully. The orientation mapping uses the same closed edge-convention
table as the front-end (nlb_frontend.ROLE_DIR) — world-edge semantics, not
answer knowledge.

Batching: EVAL packets are chunked (batch size 100, qid order) into
packets-eval-NNN.jsonl; ONE fresh authoring identity per batch, identities
disjoint from the DEV author and from each other. PROBE packets
(packets-probe.jsonl) are a deterministic largest-remainder stratified sample
of 60 covered qids (lexicographic within family) authored by a further
disjoint identity under the no-label prompt.
"""

import argparse
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, _HERE)

import nlb_frontend  # noqa: E402  (ROLE_DIR — the closed orientation table)

_ENT_PREFIX = "urn:kotw:v0:"
BATCH = 100

# shape glosses live in the pinned prompt files; ids only here
L3A_SHAPES = {("unique", "role"): "one-role", ("unique", "flip"): "one-holder",
              ("lookup", "role"): "all-role", ("lookup", "flip"): "all-holder",
              ("count", "role"): "count-role", ("count", "flip"): "count-holder"}


def ent_label(urn):
    return urn[len(_ENT_PREFIX):] if isinstance(urn, str) and \
        urn.startswith(_ENT_PREFIX) else str(urn)


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def urn2label(root):
    m = {}
    for corpus in ("kernel-v0", "molecules-v0", "code-v0"):
        for r in load_jsonl(os.path.join(root, "data", corpus,
                                         "minted-urns.jsonl")):
            m[r["urn"]] = r["sourceId"]
    return m


def packet(rec, u2l):
    q = rec.get("query") or {}
    op = q.get("op")
    if op in ("instance", "instance-of"):
        return {"qid": rec["qid"], "shape": "is-a",
                "concept_label": (u2l.get(q.get("concept")) or
                                  "unknown concept").replace("-", " "),
                "entity_label": ent_label(q.get("entity"))}
    if op in ("unique", "lookup", "count"):
        rel = q.get("rel")
        lab = u2l.get(rel)
        role_dir = nlb_frontend.ROLE_DIR.get(lab, "forward")
        side = "role" if q.get("direction") == role_dir else "flip"
        return {"qid": rec["qid"], "shape": L3A_SHAPES[(op, side)],
                "rel_label": (lab or "unknown relation").replace("-", " "),
                "entity_label": ent_label(q.get("subject"))}
    # a5 relational ops: the op id IS the shape id
    if op in nlb_frontend.A5_OPS:
        return {"qid": rec["qid"], "shape": op,
                "entity_label": ent_label(q.get("of"))}
    return None  # malformed and other unrenderable shapes are excluded


def probe_sample(included):
    """Deterministic largest-remainder stratified sample of 60 covered qids."""
    fams = {}
    for r in included:
        if r["class"] == "covered":
            fams.setdefault(r["family"], []).append(r["qid"])
    total = sum(len(v) for v in fams.values())
    quotas = {}
    rem = []
    used = 0
    for fam in sorted(fams):
        exact = 60.0 * len(fams[fam]) / total
        quotas[fam] = int(exact)
        used += int(exact)
        rem.append((-(exact - int(exact)), fam))
    for _frac, fam in sorted(rem)[:60 - used]:
        quotas[fam] += 1
    out = []
    for fam in sorted(fams):
        out.extend(sorted(fams[fam])[:quotas[fam]])
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=("l3a", "a5"))
    ap.add_argument("--root", default=_ROOT)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    root = args.root
    out_dir = args.out_dir or os.path.join(
        root, "data", "nlb-phrasings-%s" % args.vertical, "packets")
    ev = load_jsonl(os.path.join(
        root, "data", "l3a-eval" if args.vertical == "l3a" else "a5-eval",
        "queries.jsonl"))
    included = [r for r in ev if r["family"] != "malformed"]
    u2l = urn2label(root)
    packets = []
    for rec in included:
        p = packet(rec, u2l)
        if p is None:
            raise AssertionError("unrenderable included item %s" % rec["qid"])
        packets.append(p)
    os.makedirs(out_dir, exist_ok=True)
    manifest = {"schema": "nlb-packets-manifest/1", "vertical": args.vertical,
                "batch_size": BATCH, "eval_batches": [], "n_eval": len(packets)}
    for i in range(0, len(packets), BATCH):
        name = "packets-eval-%03d.jsonl" % (i // BATCH)
        path = os.path.join(out_dir, name)
        body = "".join(json.dumps(p, sort_keys=True) + "\n"
                       for p in packets[i:i + BATCH])
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        manifest["eval_batches"].append(
            {"file": name,
             "sha256": hashlib.sha256(body.encode()).hexdigest(),
             "n": len(packets[i:i + BATCH])})
    by_qid = {p["qid"]: p for p in packets}
    probe = [by_qid[q] for q in probe_sample(included)]
    ppath = os.path.join(out_dir, "packets-probe.jsonl")
    body = "".join(json.dumps(p, sort_keys=True) + "\n" for p in probe)
    with open(ppath, "w", encoding="utf-8") as f:
        f.write(body)
    manifest["probe"] = {"file": "packets-probe.jsonl",
                         "sha256": hashlib.sha256(body.encode()).hexdigest(),
                         "n": len(probe)}
    mpath = os.path.join(out_dir, "packets-manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"out_dir": out_dir, "n_eval": len(packets),
                      "n_probe": len(probe),
                      "batches": len(manifest["eval_batches"])}))


if __name__ == "__main__":
    main()
