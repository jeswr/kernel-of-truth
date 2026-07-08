#!/usr/bin/env python3
"""g6 pinned analysis — HS6 AND-under-operator static count (P1 §4 HS6 / G6).

Eligible run records on stdin; analysis-output JSON on stdout.
Deterministic counts over pinned corpora — no statistical test (P1 common rules).

Input metric contract (counts summed over eligible records):
  metrics.n_axioms                       working axiom set size (G4 set + kernel-v0 +
                                         molecules-v0 projections; planned >= 20)
  metrics.n_need_and_under_operator      axioms requiring AND under an operator
  metrics.n_need_and_sidecar_expressible of those, how many are sidecar-expressible

Output fields:
  /gates/instrument_valid      n_axioms >= 20
  /analysis/and_share          n_need / n_axioms
  /analysis/all_sidecar_expressible  bool
  /analysis/n_axioms

Verdict mapping (frozen record): PASS (∃-conjunctive fragment stays) iff
and_share < 0.20 AND all_sidecar_expressible; FAIL (extend grammar) iff
and_share >= 0.20 AND NOT all_sidecar_expressible; else INCONCLUSIVE.

Fixture (--selftest, HAND-COMPUTED): 3/20 need AND, all 3 expressible
-> share 0.15, PASS side; 5/20 with 3 expressible -> share 0.25, not-all.
"""
import json
import sys


def analyze(records):
    tot = {k: 0 for k in ("n_axioms", "n_need_and_under_operator",
                          "n_need_and_sidecar_expressible")}
    for r in records:
        for k in tot:
            tot[k] += int(r["metrics"][k])
    out = {"gates": {"instrument_valid": tot["n_axioms"] >= 20}, "analysis": {}}
    if tot["n_axioms"] > 0:
        out["analysis"] = {
            "and_share": tot["n_need_and_under_operator"] / tot["n_axioms"],
            "all_sidecar_expressible": (tot["n_need_and_sidecar_expressible"]
                                        == tot["n_need_and_under_operator"]),
            "n_axioms": tot["n_axioms"],
        }
    return out


def selftest():
    out = analyze([{"metrics": {"n_axioms": 20, "n_need_and_under_operator": 3,
                                "n_need_and_sidecar_expressible": 3}}])
    assert abs(out["analysis"]["and_share"] - 0.15) < 1e-12
    assert out["analysis"]["all_sidecar_expressible"] is True
    assert out["gates"]["instrument_valid"] is True
    out = analyze([{"metrics": {"n_axioms": 20, "n_need_and_under_operator": 5,
                                "n_need_and_sidecar_expressible": 3}}])
    assert abs(out["analysis"]["and_share"] - 0.25) < 1e-12
    assert out["analysis"]["all_sidecar_expressible"] is False
    print("g6 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
