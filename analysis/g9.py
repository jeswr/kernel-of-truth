#!/usr/bin/env python3
"""g9 pinned analysis — HS-A authoring capability gate (P1 §4 HS-A / G9).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (counts summed over eligible records):
  metrics.n_explications        machine-authored explications scored (planned >= 50)
  metrics.n_composite_pass      explications passing the composite validator bar
                                (legality + substitutability + cross-translatability,
                                Baartmans et al. metric definitions reused as-is)
  metrics.blinded_review_done   1 iff the blinded human review stage completed
  metrics.deepnsm_published_point_x100
                                DeepNSM-8B published composite point estimate x100
                                (integer to keep the raw log integer-clean; 24 = 0.24)

Output fields:
  /gates/instrument_valid      blinded_review_done AND n_explications >= 50
  /analysis/composite_rate, /analysis/wilson_lb, /analysis/wilson_ub
  /analysis/margin_threshold   published point + 0.10 (the pre-defined margin)
  /analysis/clears_margin      bool: wilson_lb >= margin_threshold
  /analysis/below_margin       bool: wilson_ub <  margin_threshold
  /analysis/n_explications

Verdict mapping (frozen record): PASS iff clears_margin; FAIL iff below_margin;
else INCONCLUSIVE. Detectable alternative at n=50 (P8 §1.6, printed per the
decidability lint): reliable clearance of 0.34 needs true rate >~ 0.54; the
frozen wilson_gate declares expected_rate 0.60.

Fixture (--selftest, HAND-COMPUTED): 35/50 pass -> rate 0.70;
Wilson lb (z=1.645) = 0.58539; threshold 0.24+0.10=0.34 -> clears.
"""
import json
import sys

Z = 1.645


def wilson_bounds(p, n):
    if n <= 0:
        return 0.0, 1.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def analyze(records):
    tot = {"n_explications": 0, "n_composite_pass": 0}
    review_done, published = False, None
    for r in records:
        m = r["metrics"]
        tot["n_explications"] += int(m["n_explications"])
        tot["n_composite_pass"] += int(m["n_composite_pass"])
        review_done = review_done or bool(m["blinded_review_done"])
        published = int(m["deepnsm_published_point_x100"]) / 100.0
    out = {"gates": {"instrument_valid": review_done and tot["n_explications"] >= 50},
           "analysis": {}}
    if tot["n_explications"] > 0 and published is not None:
        rate = tot["n_composite_pass"] / tot["n_explications"]
        lb, ub = wilson_bounds(rate, tot["n_explications"])
        thr = published + 0.10
        out["analysis"] = {
            "composite_rate": rate, "wilson_lb": lb, "wilson_ub": ub,
            "margin_threshold": thr,
            "clears_margin": lb >= thr, "below_margin": ub < thr,
            "n_explications": tot["n_explications"],
        }
    return out


def selftest():
    recs = [{"metrics": {"n_explications": 50, "n_composite_pass": 35,
                         "blinded_review_done": 1, "deepnsm_published_point_x100": 24}}]
    out = analyze(recs)
    a = out["analysis"]
    assert abs(a["composite_rate"] - 0.70) < 1e-12
    assert abs(a["wilson_lb"] - 0.58539) < 5e-5, a["wilson_lb"]   # HAND-COMPUTED
    assert abs(a["margin_threshold"] - 0.34) < 1e-12
    assert a["clears_margin"] is True and a["below_margin"] is False
    assert out["gates"]["instrument_valid"] is True
    print("g9 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
