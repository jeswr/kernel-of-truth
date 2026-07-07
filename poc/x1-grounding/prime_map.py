#!/usr/bin/env python3
"""
X1-grounding stage 2 (PREREG §5.1): the FROZEN prime->node table, verified
mechanically against the built vocabulary. This stage may only REMOVE rows
that fail vocab lookup (discrepancies reported); it never adds or remaps.

Runs BEFORE strata (no-peeking, PREREG §7): it does vocabulary lookup only,
touches no graph structure, prints no stratum membership.
"""
import argparse
import gzip
import json
import os

import x1g_lib as L

# --- FROZEN §5.1 table (transcribed from encoder/src/lexicon.ts PRIMES) ------
# Each row: (prime name, chartIndex, target node, senseRiskNote|None).
EVALUABLE = [
    ("SOMEONE", 3, "someone", None),
    ("SOMETHING~THING", 4, "thing", None),
    ("PEOPLE", 5, "people", None),
    ("BODY", 6, "body", None),
    ("KIND", 7, "kind", "WN 'kind': sort/type vs kind-hearted; word-form match (T3)"),
    ("PART", 8, "part", None),
    ("THE-SAME", 10, "same", "hand adjudication: the determiner is semantically empty"),
    ("OTHER~ELSE~ANOTHER", 11, "other", None),
    ("ONE", 12, "one", None),
    ("TWO", 13, "two", None),
    ("SOME", 14, "some", None),
    ("ALL", 15, "all", None),
    ("MUCH~MANY", 16, "much", None),
    ("LITTLE~FEW", 17, "little", None),
    ("GOOD", 18, "good", None),
    ("BAD", 19, "bad", None),
    ("BIG", 20, "big", None),
    ("SMALL", 21, "small", None),
    ("THINK", 22, "think", None),
    ("KNOW", 23, "know", None),
    ("WANT", 24, "want", None),
    ("FEEL", 26, "feel", None),
    ("SEE", 27, "see", None),
    ("HEAR", 28, "hear", None),
    ("SAY", 29, "say", None),
    ("WORDS", 30, "word", "frozen target 'word' via Morphy (PREREG §5.1)"),
    ("TRUE", 31, "true", "WN 'true' senses may skew from prime meaning (T3)"),
    ("DO", 32, "do", None),
    ("HAPPEN", 33, "happen", None),
    ("MOVE", 34, "move", None),
    ("LIVE", 39, "live", None),
    ("DIE", 40, "die", None),
    ("WHEN~TIME", 41, "time", None),
    ("NOW", 42, "now", None),
    ("BEFORE", 43, "before", None),
    ("AFTER", 44, "after", None),
    ("MOMENT", 48, "moment", None),
    ("WHERE~PLACE", 49, "place", None),
    ("HERE", 50, "here", None),
    ("ABOVE", 51, "above", None),
    ("BELOW", 52, "below", None),
    ("FAR", 53, "far", None),
    ("NEAR", 54, "near", None),
    ("SIDE", 55, "side", None),
    ("INSIDE", 56, "inside", None),
    ("TOUCH", 57, "touch", None),
    ("NOT", 58, "not", None),
    ("MAYBE", 59, "maybe", None),
    ("VERY", 63, "very", None),
    ("MORE", 64, "more", None),
    ("LIKE~AS~WAY", 65, "like", "WN 'like' verb/prep senses may skew (T3)"),
]

EXCLUDED = [
    ("YOU", "no WordNet entry (closed-class)"),
    ("THIS", "no WordNet entry (closed-class)"),
    ("BECAUSE", "no WordNet entry (closed-class)"),
    ("IF", "no WordNet entry (closed-class)"),
    ("DON'T-WANT", "negation compound; no single-word exponent"),
    ("BE-SOMEWHERE", "copular / multi-word construction"),
    ("THERE-IS", "copular / multi-word construction"),
    ("BE-SPEC", "copular / multi-word construction"),
    ("IS-MINE", "copular / multi-word construction"),
    ("A-LONG-TIME", "multi-word duration exponent"),
    ("A-SHORT-TIME", "multi-word duration exponent"),
    ("FOR-SOME-TIME", "multi-word duration exponent"),
    ("I", "WN 'i' = letter/iodine/numeral; homograph exclusion"),
    ("CAN", "WN 'can' = container/preserve; modal absent; homograph exclusion"),
]

COVERAGE_MIN = 45  # PREREG §5.1 coverage gate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default=os.path.join(L.HERE, "graph.json.gz"))
    ap.add_argument("--out", default=os.path.join(L.HERE, "primes-mapping.json"))
    args = ap.parse_args()

    with gzip.open(args.graph, "rt") as f:
        graph = json.loads(f.read())
    nodes = graph["nodes"]
    node_id = {lem: i for i, lem in enumerate(nodes)}
    vocab = set(nodes)

    rows = []
    removed = []
    for name, ci, target, note in EVALUABLE:
        if target in vocab:
            rows.append({
                "prime": name,
                "chartIndex": ci,
                "node": target,
                "nodeId": node_id[target],
                "senseRiskNote": note,
            })
        else:
            removed.append({"prime": name, "chartIndex": ci, "node": target,
                            "reason": "target node absent from built vocabulary"})

    count = len(rows)
    gate = "OK" if count >= COVERAGE_MIN else "INCONCLUSIVE-BY-COVERAGE"

    out = {
        "schema": "x1g-primes-mapping/1",
        "inputsSha256": graph.get("inputsSha256", {}),
        "evaluableCount": count,
        "coverageGate": gate,
        "coverageMin": COVERAGE_MIN,
        "evaluable": sorted(rows, key=lambda r: r["chartIndex"]),
        "removedByVerification": removed,
        "excluded": [{"prime": p, "reason": r} for p, r in EXCLUDED],
        "excludedCount": len(EXCLUDED),
    }
    L.dump_json_pretty(out, args.out)
    print("prime_map: evaluable=%d gate=%s removed=%d" % (
        count, gate, len(removed)))
    if removed:
        for r in removed:
            print("  REMOVED:", r["prime"], "->", r["node"])


if __name__ == "__main__":
    main()
