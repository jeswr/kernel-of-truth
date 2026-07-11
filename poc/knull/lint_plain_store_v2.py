#!/usr/bin/env python3
"""knull-v2 — G-1 plain-store lint driver for the RE-AUTHORED store.

Runs the FULL pinned v1 linter contract (poc/knull/lint_plain_store.py,
imported as a library, byte-untouched: checks D-1, L-1..L-5, R-1..R-4)
over the v2 authored store poc/knull/inputs-v2/plain-authored.json.
The v1 linter file itself is a frozen-knull pinned artifact and keeps
reading the v1 store when invoked directly; this driver is the v2 entry
point (fresh v2 path, the g3-llmproxy-v2 custody pattern).

Usage:
  python3 poc/knull/lint_plain_store_v2.py [--report]

Exit 0 iff zero findings. --report additionally prints the per-check
summary JSON (same fields as the v1 --report) plus the per-item word-band
table, and writes inputs-v2/g1-lint-report.json.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORED_V2 = os.path.join(HERE, "inputs-v2", "plain-authored.json")

sys.path.insert(0, HERE)
import lint_plain_store as lps  # noqa: E402  (pinned v1 contract, library use)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    with open(AUTHORED_V2, encoding="utf-8") as f:
        authored = json.load(f)
    concepts = lps.load_concepts()
    by_label = {c["label"]: c for c in concepts}
    findings = []
    ratios = lps.lint(authored, concepts, findings)

    rows = []
    for lab in sorted(authored["definitions"]):
        d = authored["definitions"][lab]
        c = by_label.get(lab)
        if c is None:
            continue
        wc, wn = len(c["gloss"].split()), len(d.split())
        lo = wc * (1 - lps.WORDBAND_FRAC)
        hi = max(wc * (1 + lps.WORDBAND_FRAC), wc + 8)
        segs = lps.segments(d)
        rows.append({"label": lab, "nsm_words": wc, "words": wn,
                     "band": [round(lo, 1), round(hi, 1)],
                     "in_band": bool(lo <= wn <= hi),
                     "n_segments": len(segs),
                     "jaccard_vs_own_gloss": round(
                         lps.jaccard(lps.tokens(d),
                                     lps.tokens(c["gloss"])), 3),
                     "register_ratio": ratios.get(lab)})

    if findings:
        for code, msg in findings:
            sys.stderr.write("FAIL %s: %s\n" % (code, msg))
        sys.stderr.write("lint_plain_store_v2: %d violation(s)\n"
                         % len(findings))
        sys.exit(1)

    if args.report:
        vals = sorted(v for v in ratios.values() if v is not None)
        report = {
            "store": "poc/knull/inputs-v2/plain-authored.json",
            "checks": ["D-1", "L-1", "L-2", "L-3", "L-4", "L-5",
                       "R-1", "R-2", "R-3", "R-4"],
            "n_definitions": len(ratios),
            "register_ratio_min_observed": vals[0] if vals else None,
            "register_ratio_median": vals[len(vals) // 2] if vals else None,
            "register_ratio_threshold": lps.REGISTER_RATIO_MIN,
            "rows": rows,
        }
        opath = os.path.join(HERE, "inputs-v2", "g1-lint-report.json")
        with open(opath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, sort_keys=True)
            f.write("\n")
        print(json.dumps({k: v for k, v in report.items() if k != "rows"},
                         indent=1, sort_keys=True))
        print("report -> %s" % opath)
    print("lint_plain_store_v2: PASS (108 re-authored definitions, "
          "all v1 G-1 checks green)")


if __name__ == "__main__":
    main()
