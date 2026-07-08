#!/usr/bin/env python3
"""g7 pinned analysis — HS7 apply-clause bulk-projection count (P1 §4 HS7 / G7).

Eligible run records on stdin; analysis-output JSON on stdout.
Deterministic counts over pinned corpora — no statistical test (P1 common rules).

Input metric contract (counts summed over eligible records):
  metrics.n_records_bulk        records in the bulk-scale projection
                                (kernel-v0 + molecules-v0 + wn31-aligned; planned >= 10^4)
  metrics.n_breached_either     records breaching EITHER a grammar cap OR >1.5x clause
                                growth when relational content is inlined (union count,
                                counted per record, not per breach)
  metrics.n_cap_violations      breakdown: cap violations (reporting only)
  metrics.n_growth_over_1p5x    breakdown: >1.5x clause growth (reporting only)

Output fields:
  /gates/instrument_valid    n_records_bulk >= 10000
  /analysis/breach_share     n_breached_either / n_records_bulk
  /analysis/cap_violation_share, /analysis/growth_share   (reporting)
  /analysis/n_records_bulk

Verdict mapping (frozen record): FAIL (apply-clauses / kot-ast/2 win) iff
breach_share > 0.10; PASS (defer; inlining stands) iff breach_share <= 0.10;
catch-all INCONCLUSIVE (unreachable when the gate is computable — deterministic).

Fixture (--selftest, HAND-COMPUTED): 800/10000 breached -> share 0.08 (defer side);
1500/10000 -> 0.15 (apply-clause side).
"""
import json
import sys


def analyze(records):
    tot = {k: 0 for k in ("n_records_bulk", "n_breached_either",
                          "n_cap_violations", "n_growth_over_1p5x")}
    for r in records:
        for k in tot:
            tot[k] += int(r["metrics"][k])
    out = {"gates": {"instrument_valid": tot["n_records_bulk"] >= 10000}, "analysis": {}}
    if tot["n_records_bulk"] > 0:
        n = tot["n_records_bulk"]
        out["analysis"] = {
            "breach_share": tot["n_breached_either"] / n,
            "cap_violation_share": tot["n_cap_violations"] / n,
            "growth_share": tot["n_growth_over_1p5x"] / n,
            "n_records_bulk": n,
        }
    return out


def selftest():
    out = analyze([{"metrics": {"n_records_bulk": 10000, "n_breached_either": 800,
                                "n_cap_violations": 500, "n_growth_over_1p5x": 400}}])
    assert abs(out["analysis"]["breach_share"] - 0.08) < 1e-12
    assert out["gates"]["instrument_valid"] is True
    out = analyze([{"metrics": {"n_records_bulk": 10000, "n_breached_either": 1500,
                                "n_cap_violations": 900, "n_growth_over_1p5x": 800}}])
    assert abs(out["analysis"]["breach_share"] - 0.15) < 1e-12
    print("g7 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
