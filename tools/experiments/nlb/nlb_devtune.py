#!/usr/bin/env python3
"""nlb_devtune — DEV-set frame-finalisation runner (pre-freeze tooling).

    python3 tools/experiments/nlb/nlb_devtune.py --vertical l3a [--receipt]

Parses data/nlb-phrasings-<v>/dev.jsonl through the front-end with a
gazetteer built from the pinned world-store entities PLUS the fresh DEV-only
entities (data/nlb-phrasings-<v>/dev-entities.jsonl — never part of any
scored arm's gazetteer). Reports, per the design doc section 5.3 protocol:

  - dev abstention (front-end parse-failure) rate — the G4 quantity;
  - parse-stage breakdown;
  - intent-match among reach=expect-parse items (op+rel/concept+direction
    equal to the intent, with the registered part-of mirror equivalence);
  - any WRONG-DIRECTION or WRONG-SLOT parse among expect-parse items
    (must be 0 before pinning: those are the S2-shaped hazards).

DEV items are over FRESH identities disjoint from every scored eval item and
are never scored in the final analysis (ASM-0145); this tool is how the frame
layer is tuned, and its receipt is committed alongside the DEV corpus.
"""

import argparse
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "axiom"))
sys.path.insert(0, _HERE)

import kot_axiom  # noqa: E402
import kot_code  # noqa: E402
import nlb_frontend  # noqa: E402

MIRROR = {"has-part": ("part-of", {"forward": "inverse", "inverse": "forward"})}


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def label2urn(root):
    m = {}
    for corpus in ("kernel-v0", "molecules-v0", "code-v0"):
        p = os.path.join(root, "data", corpus, "minted-urns.jsonl")
        for r in load_jsonl(p):
            m[r["sourceId"]] = r["urn"]
    return m


def intent_query(intent, l2u, vertical):
    if vertical == "l3a":
        if intent["op"] == "instance":
            return {"op": "instance", "entity": intent["entity"],
                    "concept": l2u[intent["concept_label"]]}
        return {"op": intent["op"], "rel": l2u[intent["rel_label"]],
                "direction": intent["direction"], "subject": intent["entity"]}
    if intent["op"] == "instance-of":
        return {"op": "instance-of", "entity": intent["entity"],
                "concept": l2u[intent["concept_label"]]}
    return {"op": intent["op"], "of": intent["entity"]}


def matches(parsed, rec, l2u, vertical):
    want = intent_query(rec["intent"], l2u, vertical)
    if parsed == want:
        return True
    if (rec.get("mirror_ok") or rec["intent"].get("mirror_ok")) \
            and vertical == "l3a":
        lab = rec["intent"].get("rel_label")
        if lab in MIRROR:
            mlab, flip = MIRROR[lab]
            mw = dict(want)
            mw["rel"] = l2u[mlab]
            mw["direction"] = flip[want["direction"]]
            if parsed == mw:
                return True
    return False


def run(root, vertical):
    base = os.path.join(root, "data", "nlb-phrasings-%s" % vertical)
    dev = load_jsonl(os.path.join(base, "dev.jsonl"))
    dev_ents = [r["urn"] for r in
                load_jsonl(os.path.join(base, "dev-entities.jsonl"))]
    if vertical == "l3a":
        axioms, world = kot_axiom.load_corpora(root)
        engine = kot_axiom.Engine(axioms, world)
    else:
        engine = kot_code.build_code_oracle(root).engine
    gaz_ents = sorted(set(engine.entities) | set(dev_ents))
    parses = nlb_frontend.parse_all(
        [{"qid": r["qid"], "text": r["text"]} for r in dev],
        vertical, gaz_ents, root=root)
    l2u = label2urn(root)
    m = {"dev_n": len(dev), "parse_refused": 0, "stage_breakdown": {},
         "expect_parse_n": 0, "expect_parse_parsed": 0,
         "expect_parse_intent_match": 0, "wrong_slot_parses": [],
         "refused_qids": [], "by_reach": {}}
    for rec in dev:
        p = parses[rec["qid"]]
        reach = rec["intent"].get("reach", "expect-parse")
        br = m["by_reach"].setdefault(reach, {"n": 0, "parsed": 0})
        br["n"] += 1
        if p["status"] == "refuse":
            m["parse_refused"] += 1
            st = p.get("stage", "unknown")
            m["stage_breakdown"][st] = m["stage_breakdown"].get(st, 0) + 1
            m["refused_qids"].append(rec["qid"])
        else:
            br["parsed"] += 1
        if reach == "expect-parse":
            m["expect_parse_n"] += 1
            if p["status"] == "parse":
                m["expect_parse_parsed"] += 1
                if matches(p["query"], rec, l2u, vertical):
                    m["expect_parse_intent_match"] += 1
                else:
                    m["wrong_slot_parses"].append(
                        {"qid": rec["qid"], "got": p["query"]})
    m["dev_abstention_rate"] = m["parse_refused"] / float(len(dev))
    return m


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=("l3a", "a5"))
    ap.add_argument("--root", default=_ROOT)
    ap.add_argument("--receipt", action="store_true",
                    help="write dev-tune-receipt.json next to the corpus")
    args = ap.parse_args()
    m = run(args.root, args.vertical)
    print(json.dumps(m, indent=1, sort_keys=True))
    if args.receipt:
        base = os.path.join(args.root, "data",
                            "nlb-phrasings-%s" % args.vertical)
        receipt = {
            "schema": "nlb-devtune-receipt/1",
            "vertical": args.vertical,
            "metrics": {k: v for k, v in m.items()
                        if k not in ("refused_qids", "wrong_slot_parses")},
            "refused_qids": m["refused_qids"],
            "wrong_slot_parses": m["wrong_slot_parses"],
            "pins": {
                "dev.jsonl": file_sha256(os.path.join(base, "dev.jsonl")),
                "dev-entities.jsonl": file_sha256(
                    os.path.join(base, "dev-entities.jsonl")),
                "nlb_frontend.py": file_sha256(
                    os.path.join(_HERE, "nlb_frontend.py")),
                "nlb_map.mjs": file_sha256(
                    os.path.join(_HERE, "nlb_map.mjs")),
            },
            "note": ("frame finalisation ran against DEV only (design doc "
                     "5.3); DEV identities are fresh and disjoint from every "
                     "scored eval item (ASM-0145)"),
        }
        rp = os.path.join(base, "dev-tune-receipt.json")
        with open(rp, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=1, sort_keys=True)
            f.write("\n")
        print("receipt -> %s" % rp)
    gate = m["dev_abstention_rate"] <= 0.20
    hazards = len(m["wrong_slot_parses"]) == 0
    print("G4 dev_abstention_rate=%.4f (<=0.20: %s); wrong-slot hazards: %d"
          % (m["dev_abstention_rate"], gate, len(m["wrong_slot_parses"])))
    sys.exit(0 if (gate and hazards) else 1)


if __name__ == "__main__":
    main()
