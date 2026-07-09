#!/usr/bin/env python3
"""a5 pinned analysis — HA5 engine leg (code world-layer + code-structure
oracle, deterministic extraction, gold-op queries).

Eligible run records on stdin (one JSON per line); analysis-output JSON on
stdout. Derived statistics live HERE and nowhere else (P2 G-4).

Input contract (tools/experiments/a5_instrument.py raw metrics), one final
record per arm in {engine, abstain-all, answer-all}; the LAST record per arm
wins (supersession is verdict-gen's job; this is a tie-break for re-runs):
  metrics.n_covered / n_covered_exact            covered slice, exact answers
  metrics.n_control / n_control_refused_correct_code / n_control_refused_any
  metrics.store.{n_axiom_records,n_world_records,n_violations}
  metrics.provenance_all_valid, metrics.deterministic_repeat_identical
  metrics.engine_total_ns, metrics.n_queries

Primary endpoint (frozen record): one-sided Wilson 95% LOWER bound (z=1.645,
same formula as tools/registry/kot_common.py) on the ENGINE arm's covered
exact-answer rate; co-gate on the control correct-refusal Wilson LB.
UPPER bounds feed the FAIL rule (UB at/below threshold = decisive failure).

Instrument-validity gate (all raw, pre-declared):
  engine + both trivial-policy baseline arms present; n_covered == 855 and
  n_control == 122 (the pinned a5-eval strata); store counts match the pinned
  corpus manifests (5 axiom records, 889 world records, exactly the 3 planted
  violations detected); every engine answer carried valid provenance+license;
  the doubled eval pass was byte-identical (determinism).

Fixture (--selftest, HAND-COMPUTED): 855/855 covered & 122/122 control ->
rates 1.0; covered LB = (1 + z^2/2n - z*(z^2/4n^2)^0.5)/(1 + z^2/n) with
n=855, z=1.645: z^2=2.706025, z^2/2n=0.0015824..., z*(z/2n)=0.0015824...,
so LB = 1/(1+0.0031649...) = 0.996845...; 851/855 -> rate 0.99532,
LB ~ 0.99034 (> 0.98); 838/855 -> rate 0.98012, LB ~ 0.97031 (< 0.98; the
point estimate sits ~ON the threshold, so its lower bound must fall below).
"""
import json
import sys

Z = 1.645  # one-sided 95%, matches kot_common.wilson_lower_bound

PLANNED_COVERED = 855
PLANNED_CONTROL = 122
PLANNED_AXIOM_RECORDS = 5
PLANNED_WORLD_RECORDS = 889
PLANTED_VIOLATIONS = 3


def wilson(p, n, upper=False):
    if n <= 0:
        return 1.0 if upper else 0.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre + spread if upper else centre - spread) / (1 + z2 / n)


def analyze(records):
    by_arm = {}
    for r in records:
        by_arm[r.get("config", {}).get("arm")] = r  # last per arm wins
    eng = by_arm.get("engine")
    ab = by_arm.get("abstain-all")
    aa = by_arm.get("answer-all")

    out = {"gates": {"instrument_valid": False}, "analysis": {}}
    if eng is None:
        return out
    m = eng["metrics"]
    store = m.get("store", {})
    out["gates"]["instrument_valid"] = bool(
        ab is not None and aa is not None
        and m.get("n_covered") == PLANNED_COVERED
        and m.get("n_control") == PLANNED_CONTROL
        and store.get("n_axiom_records") == PLANNED_AXIOM_RECORDS
        and store.get("n_world_records") == PLANNED_WORLD_RECORDS
        and store.get("n_violations") == PLANTED_VIOLATIONS
        and m.get("provenance_all_valid") is True
        and m.get("deterministic_repeat_identical") is True
    )

    nc, ne = m.get("n_covered", 0), m.get("n_covered_exact", 0)
    ng, nr = m.get("n_control", 0), m.get("n_control_refused_correct_code", 0)
    cov = ne / nc if nc else 0.0
    ctl = nr / ng if ng else 0.0
    a = out["analysis"]
    a["n_covered"] = nc
    a["n_control"] = ng
    a["covered_exact_rate"] = cov
    a["covered_exact_wilson_lb"] = wilson(cov, nc)
    a["covered_exact_wilson_ub"] = wilson(cov, nc, upper=True)
    a["control_refusal_rate"] = ctl
    a["control_refusal_wilson_lb"] = wilson(ctl, ng)
    a["control_refusal_wilson_ub"] = wilson(ctl, ng, upper=True)
    a["store_violations_detected"] = store.get("n_violations", 0)
    if m.get("n_queries"):
        a["engine_mean_us_per_query"] = m.get("engine_total_ns", 0) / m["n_queries"] / 1000.0
    else:
        a["engine_mean_us_per_query"] = 0.0

    def rate(rec, num, den):
        if rec is None:
            return 0.0
        mm = rec["metrics"]
        return (mm.get(num, 0) / mm.get(den, 1)) if mm.get(den) else 0.0

    a["baseline_abstain_covered_exact_rate"] = rate(ab, "n_covered_exact", "n_covered")
    a["baseline_abstain_control_refused_any_rate"] = rate(ab, "n_control_refused_any", "n_control")
    a["baseline_answerall_covered_exact_rate"] = rate(aa, "n_covered_exact", "n_covered")
    a["baseline_answerall_control_refused_any_rate"] = rate(aa, "n_control_refused_any", "n_control")
    return out


def _rec(arm, **kw):
    m = {"n_covered": 855, "n_covered_exact": 855, "n_control": 122,
         "n_control_refused_correct_code": 122, "n_control_refused_any": 122,
         "store": {"n_axiom_records": 5, "n_world_records": 889, "n_violations": 3},
         "provenance_all_valid": True, "deterministic_repeat_identical": True,
         "engine_total_ns": 5400000, "n_queries": 977}
    m.update(kw)
    return {"config": {"arm": arm}, "metrics": m}


def selftest():
    recs = [_rec("engine"), _rec("abstain-all", n_covered_exact=0),
            _rec("answer-all", n_control_refused_any=0,
                 n_control_refused_correct_code=0)]
    out = analyze(recs)
    assert out["gates"]["instrument_valid"] is True
    a = out["analysis"]
    assert abs(a["covered_exact_rate"] - 1.0) < 1e-12
    assert abs(a["covered_exact_wilson_lb"] - 0.996845) < 1e-4, a["covered_exact_wilson_lb"]
    assert a["covered_exact_wilson_ub"] >= 1.0 - 1e-9
    assert a["control_refusal_wilson_lb"] > 0.95, a["control_refusal_wilson_lb"]
    assert abs(a["baseline_abstain_covered_exact_rate"]) < 1e-12
    assert abs(a["baseline_answerall_control_refused_any_rate"]) < 1e-12
    # 851/855 -> LB above the 0.98 threshold; 838/855 (rate ~= threshold) -> below
    hi = analyze([_rec("engine", n_covered_exact=851), recs[1], recs[2]])
    lo = analyze([_rec("engine", n_covered_exact=838), recs[1], recs[2]])
    assert hi["analysis"]["covered_exact_wilson_lb"] > 0.98, hi["analysis"]
    assert lo["analysis"]["covered_exact_wilson_lb"] < 0.98, lo["analysis"]
    # broken instrument: missing baseline arm
    bad = analyze([_rec("engine")])
    assert bad["gates"]["instrument_valid"] is False
    print("a5 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
