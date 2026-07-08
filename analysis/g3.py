#!/usr/bin/env python3
"""g3 pinned analysis — HS3 semantics-pin annotation study (P1 §4 HS3 / G3; P8 §1.6).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (counts summed over eligible records):
  metrics.n_judgments               instance judgments (~20 concepts x ~10 instances,
                                    planned 200)
  metrics.n_necessity_violations    judged violations of the necessary-conditions pin
  metrics.n_sufficiency_violations  judged violations of the sufficiency (equivalence) pin
  metrics.annot_both_yes/_both_no/_a_yes_b_no/_a_no_b_yes
                                    2x2 dual-annotation table on the necessity judgments

Output fields:
  /gates/instrument_valid          kappa >= 0.4 AND n_judgments >= 200
  /analysis/necessity_rate, /analysis/necessity_wilson_lb, /analysis/necessity_wilson_ub
  /analysis/sufficiency_rate, /analysis/sufficiency_wilson_lb, /analysis/sufficiency_wilson_ub
  /analysis/sufficiency_equivalence_survives   bool (suff. ub <= 0.10) — secondary
  /analysis/kappa, /analysis/n_judgments

Verdict mapping (frozen record; the P1 HS3 two-decision Wilson rule — no TOST,
P8 §1.5 row 5): PASS (necessary-conditions pin survives) iff necessity_wilson_ub
<= 0.10; FAIL (defeasible-script stands; HS2 auto-resolves sidecar-only) iff
necessity_wilson_lb > 0.10; else INCONCLUSIVE (buys more annotations, never a verdict).

Bounds on a violation RATE p over n: two-sided-style score bounds at z=1.645
(one-sided 95% each side), same closed form as the freeze lint.

Fixture (--selftest, HAND-COMPUTED): 12/200 violations -> rate 0.06;
Wilson ub = (centre+spread)/(1+z2/n) with z=1.645: 0.09393 (< 0.10 -> survives);
30/200 -> rate 0.15, lb = 0.11315 (> 0.10 -> kill side decidable).
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
    tot = {k: 0 for k in ("n_judgments", "n_necessity_violations",
                          "n_sufficiency_violations", "annot_both_yes",
                          "annot_both_no", "annot_a_yes_b_no", "annot_a_no_b_yes")}
    for r in records:
        m = r["metrics"]
        for k in tot:
            tot[k] += int(m[k])
    kap = kappa_2x2(tot["annot_both_yes"], tot["annot_both_no"],
                    tot["annot_a_yes_b_no"], tot["annot_a_no_b_yes"])
    out = {"gates": {"instrument_valid": kap >= 0.4 and tot["n_judgments"] >= 200},
           "analysis": {"kappa": kap, "n_judgments": tot["n_judgments"]}}
    n = tot["n_judgments"]
    if n > 0:
        for name, k in (("necessity", "n_necessity_violations"),
                        ("sufficiency", "n_sufficiency_violations")):
            rate = tot[k] / n
            lb, ub = wilson_bounds(rate, n)
            out["analysis"]["%s_rate" % name] = rate
            out["analysis"]["%s_wilson_lb" % name] = lb
            out["analysis"]["%s_wilson_ub" % name] = ub
        out["analysis"]["sufficiency_equivalence_survives"] = (
            out["analysis"]["sufficiency_wilson_ub"] <= 0.10)
    return out


def selftest():
    base = {"n_judgments": 200, "n_necessity_violations": 12,
            "n_sufficiency_violations": 30, "annot_both_yes": 20,
            "annot_both_no": 170, "annot_a_yes_b_no": 5, "annot_a_no_b_yes": 5}
    out = analyze([{"metrics": base}])
    a = out["analysis"]
    assert abs(a["necessity_rate"] - 0.06) < 1e-12
    assert abs(a["necessity_wilson_ub"] - 0.09393) < 5e-5, a["necessity_wilson_ub"]
    assert a["necessity_wilson_ub"] <= 0.10        # survives side decidable
    assert abs(a["sufficiency_rate"] - 0.15) < 1e-12
    assert abs(a["sufficiency_wilson_lb"] - 0.11315) < 5e-5, a["sufficiency_wilson_lb"]
    assert a["sufficiency_wilson_lb"] > 0.10       # kill side decidable
    assert a["sufficiency_equivalence_survives"] is False
    assert out["gates"]["instrument_valid"] is True
    print("g3 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
