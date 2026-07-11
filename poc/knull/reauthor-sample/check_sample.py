#!/usr/bin/env python3
"""knull re-authored-sample checker (docs/next/knull-plain-arm-quality.md).

Verifies that the 12 re-authored plain-dictionary definitions in
plain-reauthored-sample.json satisfy the FULL G-1 plain-store contract
(lint_plain_store.py checks D-1, L-1..L-5, R-1..R-4) when substituted into
the authored store, i.e. that the re-authoring to the maintainer's
lexicographic standard preserves every constraint the token-budget /
alignment matching of the frozen knull record rests on.

Method: load poc/knull/inputs/plain-authored.json, substitute the 12 sample
definitions, run the linter's lint() function over the patched store against
the 108 covered concepts. Exit 0 iff zero findings. Also prints the per-item
word counts vs the L-3 band and writes check-report.json.

$0, CPU-only, read-only on all frozen inputs.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KNULL = os.path.dirname(HERE)
sys.path.insert(0, KNULL)

import lint_plain_store as lps  # noqa: E402


def main():
    with open(os.path.join(KNULL, "inputs", "plain-authored.json"),
              encoding="utf-8") as f:
        authored = json.load(f)
    with open(os.path.join(HERE, "plain-reauthored-sample.json"),
              encoding="utf-8") as f:
        sample = json.load(f)

    patched = dict(authored)
    patched["definitions"] = dict(authored["definitions"])
    for lab, d in sample["definitions"].items():
        if lab not in patched["definitions"]:
            print("FAIL ERR_SAMPLE_LABEL: %r not a covered concept" % lab)
            sys.exit(1)
        patched["definitions"][lab] = d

    concepts = lps.load_concepts()
    by_label = {c["label"]: c for c in concepts}

    findings = []
    lps.lint(patched, concepts, findings)
    # Findings on the 96 untouched entries would predate the sample; report
    # them separately (expected: none - the committed store is linter-green).
    sample_labels = set(sample["definitions"])
    sample_findings = [(c, m) for c, m in findings
                       if any(m.startswith(l + ":") or (l in m)
                              for l in sample_labels)]

    rows = []
    for lab in sorted(sample["definitions"]):
        d = sample["definitions"][lab]
        wc = len(by_label[lab]["gloss"].split())
        wn = len(d.split())
        lo = wc * (1 - lps.WORDBAND_FRAC)
        hi = max(wc * (1 + lps.WORDBAND_FRAC), wc + 8)
        segs = lps.segments(d)
        rows.append({"label": lab, "nsm_words": wc, "sample_words": wn,
                     "band": [round(lo, 1), round(hi, 1)],
                     "in_band": lo <= wn <= hi, "n_segments": len(segs),
                     "jaccard_vs_own_gloss": round(
                         lps.jaccard(lps.tokens(d),
                                     lps.tokens(by_label[lab]["gloss"])), 3)})
        print("%-40s nsm=%2d sample=%2d band=[%.1f, %.1f] segs=%d %s"
              % (lab, wc, wn, lo, hi, len(segs),
                 "OK" if lo <= wn <= hi else "OUT-OF-BAND"))

    report = {"n_sample": len(sample["definitions"]),
              "lint_findings_total": len(findings),
              "lint_findings": ["%s: %s" % (c, m) for c, m in findings],
              "rows": rows}
    with open(os.path.join(HERE, "check-report.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")

    if findings:
        for c, m in findings:
            print("FAIL %s: %s" % (c, m))
        print("check_sample: %d violation(s)" % len(findings))
        sys.exit(1)
    print("check_sample: PASS (12 re-authored definitions satisfy the full "
          "G-1 contract inside the patched store)")


if __name__ == "__main__":
    main()
