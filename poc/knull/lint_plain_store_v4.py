#!/usr/bin/env python3
"""knull-v2 Option-B -- G-1 plain-store lint driver for the FRAME-VARIATION v4 store.

Runs the pinned v1 linter contract (poc/knull/lint_plain_store.py, imported
as a library, byte-untouched) over poc/knull/inputs-v4/plain-authored.json,
with the TWO relaxations of the maintainer's Option-B ruling (2026-07-11,
maintainer decision issue 6; design note docs/next/design/
knull-optionb-analysis.md, PROPOSED-ASM-1080):

  L-3 word band     DROPPED for this store (KNULL_LINT_L3_WORDBAND findings
                    are reported as DISCLOSED relaxations, never violations;
                    the FLOP-parity role of L-3 moves to the plain-padded
                    secondary arm + the token-count sensitivity read).
  L-4 segments      RELAXED from >=2 to >=1 admissible claim segment (the
                    floor the claim-item contract of build-dqa/build-dqar
                    actually needs). KNULL_LINT_L4_SEGMENTS findings are
                    re-checked against the >=1 floor: <1 admissible segment
                    is a violation (code KNULL_LINT_L4B_MIN1SEG), 1 segment
                    is a disclosed relaxation.

Every OTHER check of the pinned contract stays enforced fail-closed:
D-1 disclosure, L-1 completeness, L-2 LC1 own-label (full label AND
headword), L-5 uniqueness, R-1 no-verbatim-NSM (both directions),
R-2 register (ratio >= 0.25 + per-segment non-NSM content), R-3 own-gloss
Jaccard < 0.5, R-4 hygiene (ASCII, no double quotes, no account strings).

Usage:
  python3 poc/knull/lint_plain_store_v4.py [--report]

Exit 0 iff zero ENFORCED findings. --report writes
inputs-v4/g1-lint-report.json with per-item rows plus the relaxation
disclosure table.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORED_V4 = os.path.join(HERE, "inputs-v4", "plain-authored.json")

sys.path.insert(0, HERE)
import lint_plain_store as lps  # noqa: E402  (pinned v1 contract, library use)

RELAXED_CODES = ("KNULL_LINT_L3_WORDBAND", "KNULL_LINT_L4_SEGMENTS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    with open(AUTHORED_V4, encoding="utf-8") as f:
        authored = json.load(f)
    concepts = lps.load_concepts()
    by_label = {c["label"]: c for c in concepts}
    findings = []
    ratios = lps.lint(authored, concepts, findings)

    enforced, relaxed = [], []
    for code, msg in findings:
        (relaxed if code in RELAXED_CODES else enforced).append((code, msg))

    # L-4' floor: >=1 admissible claim segment (fail-closed; the claim-item
    # contract needs at least one segment per store gloss in every arm).
    rows = []
    for lab in sorted(authored.get("definitions", {})):
        d = authored["definitions"][lab]
        c = by_label.get(lab)
        if c is None:
            continue
        segs = lps.segments(d)
        if len(segs) < 1:
            enforced.append(("KNULL_LINT_L4B_MIN1SEG",
                             "%s: 0 admissible claim segments (floor 1)" % lab))
        wc, wn = len(c["gloss"].split()), len(d.split())
        rows.append({"label": lab, "nsm_words": wc, "words": wn,
                     "word_ratio_vs_nsm": round(wn / float(wc), 3) if wc else None,
                     "in_v1_band": bool(wc * (1 - lps.WORDBAND_FRAC) <= wn
                                        <= max(wc * (1 + lps.WORDBAND_FRAC),
                                               wc + 8)),
                     "n_segments": len(segs),
                     "jaccard_vs_own_gloss": round(
                         lps.jaccard(lps.tokens(d), lps.tokens(c["gloss"])), 3),
                     "register_ratio": ratios.get(lab)})

    if enforced:
        for code, msg in enforced:
            sys.stderr.write("FAIL %s: %s\n" % (code, msg))
        sys.stderr.write("lint_plain_store_v4: %d enforced violation(s) "
                         "(plus %d disclosed L-3/L-4 relaxations)\n"
                         % (len(enforced), len(relaxed)))
        sys.exit(1)

    if args.report:
        vals = sorted(v for v in ratios.values() if v is not None)
        wr = sorted(r["word_ratio_vs_nsm"] for r in rows)
        report = {
            "store": "poc/knull/inputs-v4/plain-authored.json",
            "contract": ("pinned v1 G-1 (lint_plain_store.py) MINUS L-3 "
                         "(dropped) and L-4 (relaxed to >=1 admissible "
                         "segment) per the Option-B ruling; see "
                         "docs/next/design/knull-optionb-analysis.md"),
            "checks_enforced": ["D-1", "L-1", "L-2", "L-4b(>=1 segment)",
                                "L-5", "R-1", "R-2", "R-3", "R-4"],
            "checks_relaxed_disclosed": ["L-3 (word band)",
                                         "L-4 (>=2 segments)"],
            "n_definitions": len(ratios),
            "n_l3_out_of_v1_band": sum(1 for r in rows if not r["in_v1_band"]),
            "n_single_segment": sum(1 for r in rows if r["n_segments"] == 1),
            "word_ratio_vs_nsm_median": wr[len(wr) // 2] if wr else None,
            "word_ratio_vs_nsm_min": wr[0] if wr else None,
            "word_ratio_vs_nsm_max": wr[-1] if wr else None,
            "register_ratio_min_observed": vals[0] if vals else None,
            "register_ratio_median": vals[len(vals) // 2] if vals else None,
            "register_ratio_threshold": lps.REGISTER_RATIO_MIN,
            "rows": rows,
        }
        opath = os.path.join(HERE, "inputs-v4", "g1-lint-report.json")
        with open(opath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, sort_keys=True)
            f.write("\n")
        print(json.dumps({k: v for k, v in report.items() if k != "rows"},
                         indent=1, sort_keys=True))
        print("report -> %s" % opath)
    print("lint_plain_store_v4: PASS (108 Option-B v4 definitions; enforced "
          "checks green; %d disclosed L-3/L-4 relaxations)" % len(relaxed))


if __name__ == "__main__":
    main()
