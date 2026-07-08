#!/usr/bin/env python3
"""g2 pinned analysis — HS2 Π read-out soundness (P1 §4 HS2 / G2; P8 §1.6 worked case).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (counts are summed over eligible records):
  metrics.n_gold                    gold subsumption judgments scored (planned 500)
  metrics.n_derived_correct         Π-derived subsumptions judged correct (precision hits)
  metrics.annot_both_yes/_both_no/_a_yes_b_no/_a_no_b_yes
                                    2x2 dual-annotation agreement table (pre-adjudication)
  metrics.litmus_promise_recovered  1 iff Π recovers `promise [= words` (NF1 check)
  metrics.partition_axioms_recovered  count of partition-side axioms Π recovered
                                    (MUST be 0: the read-out/residue split)
  metrics.sidecar_conflicts         count of Π outputs conflicting with endorsed
                                    sidecar axioms on kernel-v0 (deterministic check)

Output fields:
  /gates/instrument_valid   Cohen's kappa >= 0.4 AND n_gold >= 500
  /analysis/precision, /analysis/wilson_lb, /analysis/wilson_ub  (one-sided 95%, z=1.645)
  /analysis/kappa
  /analysis/litmus_promise_recovered  bool
  /analysis/partition_residue_ok      bool (no partition-side axiom recovered)
  /analysis/sidecar_conflict          bool (any conflict)
  /analysis/n_gold

Verdict mapping (frozen record): PASS requires wilson_lb > 0.9 AND litmus AND
residue-ok AND no conflict; FAIL fires on wilson_ub <= 0.9 (decidably below the
gate) OR any sidecar conflict; else INCONCLUSIVE (the P8 §1.6 pre-computed
not-well-decidable band ~(0.86, 0.94) true precision).

Fixture (--selftest, HAND-COMPUTED):
  470/500 -> precision 0.94; Wilson lb (z=1.645) = 0.92005 (matches the freeze lint's
  closed form); kappa for table (40,50,5,5): po=0.90, pe=0.505, kappa=0.39/0.495=0.79798.
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


def kappa_2x2(n11, n00, n10, n01):
    n = n11 + n00 + n10 + n01
    if n == 0:
        return 0.0
    po = (n11 + n00) / n
    a_yes, b_yes = (n11 + n10) / n, (n11 + n01) / n
    pe = a_yes * b_yes + (1 - a_yes) * (1 - b_yes)
    return 0.0 if pe == 1.0 else (po - pe) / (1 - pe)


def analyze(records):
    tot = {k: 0 for k in ("n_gold", "n_derived_correct", "annot_both_yes",
                          "annot_both_no", "annot_a_yes_b_no", "annot_a_no_b_yes",
                          "partition_axioms_recovered", "sidecar_conflicts")}
    litmus = False
    for r in records:
        m = r["metrics"]
        for k in tot:
            tot[k] += int(m[k])
        litmus = litmus or bool(m["litmus_promise_recovered"])

    kap = kappa_2x2(tot["annot_both_yes"], tot["annot_both_no"],
                    tot["annot_a_yes_b_no"], tot["annot_a_no_b_yes"])
    instrument_valid = kap >= 0.4 and tot["n_gold"] >= 500
    out = {"gates": {"instrument_valid": instrument_valid},
           "analysis": {"kappa": kap, "n_gold": tot["n_gold"]}}
    if tot["n_gold"] > 0:
        p = tot["n_derived_correct"] / tot["n_gold"]
        lb, ub = wilson_bounds(p, tot["n_gold"])
        out["analysis"].update({
            "precision": p, "wilson_lb": lb, "wilson_ub": ub,
            "litmus_promise_recovered": litmus,
            "partition_residue_ok": tot["partition_axioms_recovered"] == 0,
            "sidecar_conflict": tot["sidecar_conflicts"] > 0,
        })
    return out


def selftest():
    recs = [{"metrics": {"n_gold": 500, "n_derived_correct": 470,
                         "annot_both_yes": 40, "annot_both_no": 50,
                         "annot_a_yes_b_no": 5, "annot_a_no_b_yes": 5,
                         "litmus_promise_recovered": 1,
                         "partition_axioms_recovered": 0, "sidecar_conflicts": 0}}]
    out = analyze(recs)
    a = out["analysis"]
    assert abs(a["precision"] - 0.94) < 1e-12
    assert abs(a["wilson_lb"] - 0.92005) < 5e-5, a["wilson_lb"]   # HAND-COMPUTED
    assert abs(a["kappa"] - 0.79798) < 5e-5, a["kappa"]           # HAND-COMPUTED
    assert out["gates"]["instrument_valid"] is True
    assert a["partition_residue_ok"] and not a["sidecar_conflict"]
    # kappa below 0.4 trips the instrument gate
    bad = [{"metrics": dict(recs[0]["metrics"], annot_both_yes=25, annot_both_no=25,
                            annot_a_yes_b_no=25, annot_a_no_b_yes=25)}]
    assert analyze(bad)["gates"]["instrument_valid"] is False
    print("g2 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
