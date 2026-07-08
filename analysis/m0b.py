#!/usr/bin/env python3
"""m0b pinned analysis — kernel-expressibility coverage + NICHE-SCOPE gate
(P1 §5 required gate; P3 §1.1 m0b.* / m0b.gate, RT-7b; P2 G-7).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (one or more records per coverage rung):
  metrics.coverage_rung        rung label ("kernel-v0" | "molecules-v0" | "wn31-aligned")
  metrics.n_tokens_sampled     content-word tokens sampled from the target task
                               family's text (planned 2000 at the primary rung)
  metrics.n_covered            tokens with a plausible profile-1 explication at
                               this rung
  metrics.spot_check_n         human spot-check sample size (GATE-H; planned 100)
  metrics.spot_check_agree     spot-check agreements with the machine judgment

PRIMARY RUNG (fixed at freeze): "molecules-v0" — the deepest authored kernel
content available at GNG-0; other rungs are reported in coverage_by_rung.

Output fields:
  /gates/instrument_valid    spot-check n >= 100 AND agreement >= 0.8 (pooled)
  /analysis/coverage_fraction, /analysis/coverage_wilson_lb, /analysis/coverage_wilson_ub
                             (primary rung)
  /analysis/coverage_by_rung  {rung: fraction}
  /analysis/coverage_rung     the primary rung label (restated in every verdict, P2 G-7)
  /analysis/n_tokens_sampled  (primary rung)

Verdict mapping (frozen record): PASS iff coverage_wilson_lb > 0.20 (clears the
pre-declared NICHE-SCOPE default threshold X = 20% of the target task family's
content-word mass — maintainer ratifies X at GNG-0); FAIL iff coverage_wilson_ub
<= 0.20 (the NICHE-SCOPE banner binds every later verdict template and any
frontier-pitch route must carry a coverage-growth cost line); else INCONCLUSIVE.

Fixture (--selftest, HAND-COMPUTED): 700/2000 covered -> 0.35;
Wilson lb (z=1.645) = 0.33267 (matches the freeze-lint value).
"""
import json
import sys

Z = 1.645
PRIMARY_RUNG = "molecules-v0"


def wilson_bounds(p, n):
    if n <= 0:
        return 0.0, 1.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def analyze(records):
    rungs, spot_n, spot_agree = {}, 0, 0
    for r in records:
        m = r["metrics"]
        s = rungs.setdefault(m["coverage_rung"], {"n": 0, "covered": 0})
        s["n"] += int(m["n_tokens_sampled"])
        s["covered"] += int(m["n_covered"])
        spot_n += int(m["spot_check_n"])
        spot_agree += int(m["spot_check_agree"])
    out = {"gates": {"instrument_valid": (spot_n >= 100
                                          and spot_agree / spot_n >= 0.8 if spot_n else False)},
           "analysis": {}}
    a = out["analysis"]
    if rungs:
        a["coverage_by_rung"] = {k: v["covered"] / v["n"] for k, v in sorted(rungs.items())
                                 if v["n"] > 0}
    if PRIMARY_RUNG in rungs and rungs[PRIMARY_RUNG]["n"] > 0:
        p = rungs[PRIMARY_RUNG]["covered"] / rungs[PRIMARY_RUNG]["n"]
        lb, ub = wilson_bounds(p, rungs[PRIMARY_RUNG]["n"])
        a.update({"coverage_fraction": p, "coverage_wilson_lb": lb,
                  "coverage_wilson_ub": ub, "coverage_rung": PRIMARY_RUNG,
                  "n_tokens_sampled": rungs[PRIMARY_RUNG]["n"]})
    return out


def selftest():
    recs = [{"metrics": {"coverage_rung": "molecules-v0", "n_tokens_sampled": 2000,
                         "n_covered": 700, "spot_check_n": 100, "spot_check_agree": 90}},
            {"metrics": {"coverage_rung": "kernel-v0", "n_tokens_sampled": 2000,
                         "n_covered": 300, "spot_check_n": 0, "spot_check_agree": 0}}]
    out = analyze(recs)
    a = out["analysis"]
    assert abs(a["coverage_fraction"] - 0.35) < 1e-12
    assert abs(a["coverage_wilson_lb"] - 0.33267) < 5e-5, a["coverage_wilson_lb"]
    assert abs(a["coverage_by_rung"]["kernel-v0"] - 0.15) < 1e-12
    assert a["coverage_rung"] == "molecules-v0"
    assert out["gates"]["instrument_valid"] is True
    print("m0b selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
