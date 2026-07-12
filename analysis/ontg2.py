#!/usr/bin/env python3
"""ontg2.py -- pinned analysis for ONT-TYPE-G2/1 (registry g2-import).

Pure function: stdin JSON {"metrics": {...}} -> stdout JSON
{"gates": {...}, "analysis": {...}}. No file IO, no RNG, no clock.
Implements docs/next/design/ontology-import-plan.md sections 7.3-7.8:

  primary gate   : a3_yes >= 34 on the fixed 84-slot denominator
                   (strict improvement over the frozen A0 baseline
                   33/84 = 0.392857; point-estimate engineering gate)
  secondary gate : a2_yes >= 34 (GO-BFO-SUMO without FrameNet)
  instrument     : kappa >= 0.40 per new arm; each judge decisive on
                   >= 90% of real items per arm (0.90 is the highest
                   RT-4-decidable bar at n=84: Wilson LB at the measured
                   ~0.98 decisive rate is 0.936); deranged-probe
                   false-satisfaction <= 0.30 per judge per arm; pins ok
  informativeness: >= 67/84 A3 non-vacuous AND >= 34/42 R3 non-vacuous
                   AND zero hard operational laws emitted
  reporting      : Wilson 95% intervals, exact McNemar vs A0 (paired,
                   judge-pA labels, vacuity-zeroed), R1/R3/R4 slices,
                   pair-union / pair-concordant brackets -- all
                   REPORTED, never verdict-bearing (plan section 7.5).

Vacuity-zeroing is applied UPSTREAM (assemble): the yes-counts arriving
here are already scored counts (yes AND non-vacuous). kappa is computed
on the RAW judge labels (instrument stability, not scoring).
Every mathematical choice cites its plan anchor. Fail closed on any
missing metric (ERR_ONTG2_METRIC).
"""
import json
import math
import sys

BASELINE_YES = 33          # frozen g2 primary readout (plan section 7.5)
N_ITEMS = 84
GATE_YES = 34              # strict improvement gate: >= 34/84
KAPPA_MIN = 0.40           # plan section 7.6
DECISIVE_MIN = 0.90    # RT-4 powered at n=84 (Wilson LB 0.936 at rate 0.98)
FALSE_SAT_MAX = 0.30
NONVAC_MIN = 67            # plan section 7.6 informativeness guard
NONVAC_R3_MIN = 34

ARMS = ("a1", "a2", "a3")


def wilson(k, n, z=1.96):
    """Two-sided Wilson 95% interval (plan section 7.8)."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return ((centre - spread) / (1 + z2 / n),
            (centre + spread) / (1 + z2 / n))


def kappa(t):
    """Cohen's kappa from a 2x2 yes/no table (instrument stability only)."""
    n = t["both_yes"] + t["both_no"] + t["a_yes_b_no"] + t["a_no_b_yes"]
    if n == 0:
        return None
    po = (t["both_yes"] + t["both_no"]) / n
    pa_yes = (t["both_yes"] + t["a_yes_b_no"]) / n
    pb_yes = (t["both_yes"] + t["a_no_b_yes"]) / n
    pe = pa_yes * pb_yes + (1 - pa_yes) * (1 - pb_yes)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def mcnemar_exact(b, c):
    """Exact two-sided McNemar p over the discordant pairs (plan 7.8):
    p = min(1, 2 * P(X <= min(b,c))), X ~ Binomial(b+c, 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    tail = sum(math.comb(n, k) for k in range(0, m + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def need(m, key):
    if key not in m:
        sys.stderr.write("ERR_ONTG2_METRIC: missing %r\n" % key)
        sys.exit(2)
    return m[key]


def run(metrics):
    m = metrics
    if need(m, "n_items") != N_ITEMS:
        sys.stderr.write("ERR_ONTG2_METRIC: n_items != 84\n")
        sys.exit(2)
    if need(m, "baseline_yes") != BASELINE_YES:
        sys.stderr.write("ERR_ONTG2_METRIC: baseline_yes != 33 (frozen A0)\n")
        sys.exit(2)

    analysis = {"n_items": N_ITEMS, "baseline_yes": BASELINE_YES,
                "baseline_precision": BASELINE_YES / N_ITEMS}
    kappas, decisives, false_sats = {}, [], []
    for arm in ARMS:
        a = need(m, arm)
        ys = need(a, "yes_pA_scored")
        analysis["%s_yes" % arm] = ys
        analysis["%s_yes_pB" % arm] = need(a, "yes_pB_scored")
        analysis["%s_precision" % arm] = ys / N_ITEMS
        lo, hi = wilson(ys, N_ITEMS)
        analysis["%s_wilson_lb" % arm] = lo
        analysis["%s_wilson_ub" % arm] = hi
        k = kappa(need(a, "agreement_raw"))
        kappas[arm] = k
        analysis["kappa_%s" % arm] = k
        for pk in ("pA", "pB"):
            decisives.append(need(a, "decisive_%s" % pk) / N_ITEMS)
            pr = need(a, "probe_%s" % pk)
            fs = (pr["n_false_sat"] / pr["n_labelled"]
                  if pr["n_labelled"] else 1.0)
            false_sats.append(fs)
        analysis["%s_nonvacuous" % arm] = need(a, "nonvacuous")
        analysis["%s_nonvacuous_r3" % arm] = need(a, "nonvacuous_r3")
        analysis["%s_pair_union_yes" % arm] = need(a, "pair_union_yes")
        analysis["%s_pair_concordant_yes" % arm] = need(
            a, "pair_concordant_yes")
        for rl in ("r1", "r3", "r4"):
            analysis["%s_%s_yes" % (arm, rl)] = need(a, "%s_yes" % rl)
    for arm in ("a2", "a3"):
        b = need(m, "mcnemar_%s_b" % arm)
        c = need(m, "mcnemar_%s_c" % arm)
        analysis["mcnemar_%s_b" % arm] = b
        analysis["mcnemar_%s_c" % arm] = c
        analysis["mcnemar_%s_p" % arm] = mcnemar_exact(b, c)
        analysis["delta_%s" % arm] = (analysis["%s_yes" % arm]
                                      - BASELINE_YES) / N_ITEMS

    analysis["decisive_min_fraction"] = min(decisives)
    analysis["probe_false_sat_max"] = max(false_sats)
    analysis["forbidden_effects_ok"] = bool(need(m, "forbidden_effects_ok"))

    instrument_valid = (
        bool(need(m, "pins_ok"))
        and all(k is not None and k >= KAPPA_MIN for k in kappas.values())
        and min(decisives) >= DECISIVE_MIN
        and max(false_sats) <= FALSE_SAT_MAX)
    informative_valid = (
        analysis["a3_nonvacuous"] >= NONVAC_MIN
        and analysis["a3_nonvacuous_r3"] >= NONVAC_R3_MIN
        and analysis["forbidden_effects_ok"])

    primary_pass = analysis["a3_yes"] >= GATE_YES
    a2_pass = analysis["a2_yes"] >= GATE_YES
    analysis["primary_pass"] = primary_pass
    analysis["a2_pass"] = a2_pass
    analysis["go_combined"] = primary_pass
    analysis["go_bfo_sumo_only"] = (not primary_pass) and a2_pass
    analysis["no_go"] = not (primary_pass or a2_pass)
    # A1 can never authorize adoption (plan section 7.2) -- reported only:
    analysis["a1_pass_reported_only"] = analysis["a1_yes"] >= GATE_YES
    analysis["rider"] = (
        "PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; "
        "point-estimate engineering gate, not statistical superiority; "
        "soft non-binding typing only -- never hard laws; no feasibility "
        "conclusion")
    return {"gates": {"instrument_valid": instrument_valid,
                      "informative_valid": informative_valid},
            "analysis": analysis}


def _mock_metrics(a3_yes=40, a2_yes=35, a1_yes=20):
    def arm(y):
        return {"yes_pA_scored": y, "yes_pB_scored": max(0, y - 3),
                "agreement_raw": {"both_yes": y, "both_no": 84 - y - 4,
                                  "a_yes_b_no": 3, "a_no_b_yes": 1},
                "decisive_pA": 84, "decisive_pB": 83,
                "probe_pA": {"n_labelled": 20, "n_false_sat": 1},
                "probe_pB": {"n_labelled": 20, "n_false_sat": 2},
                "nonvacuous": 83, "nonvacuous_r3": 42,
                "pair_union_yes": y + 4, "pair_concordant_yes": y - 2,
                "r1_yes": 5, "r3_yes": y - 15, "r4_yes": 10}
    return {"n_items": 84, "baseline_yes": 33, "pins_ok": True,
            "forbidden_effects_ok": True,
            "a1": arm(a1_yes), "a2": arm(a2_yes), "a3": arm(a3_yes),
            "mcnemar_a2_b": 6, "mcnemar_a2_c": 8,
            "mcnemar_a3_b": 5, "mcnemar_a3_c": 12}


def selftest():
    out = run(_mock_metrics())
    a = out["analysis"]
    assert out["gates"]["instrument_valid"] is True
    assert out["gates"]["informative_valid"] is True
    assert a["primary_pass"] is True and a["go_combined"] is True
    assert abs(a["delta_a3"] - 7 / 84) < 1e-12
    assert 0.36 < a["a3_precision"] < 0.55
    lo, hi = a["a3_wilson_lb"], a["a3_wilson_ub"]
    assert lo < 40 / 84 < hi
    out2 = run(_mock_metrics(a3_yes=30, a2_yes=28))
    assert out2["analysis"]["no_go"] is True
    out3 = run(_mock_metrics(a3_yes=30, a2_yes=35))
    assert out3["analysis"]["go_bfo_sumo_only"] is True
    # McNemar sanity: b=c symmetric -> p ~ 1; extreme split -> small p
    assert mcnemar_exact(5, 5) > 0.99
    assert mcnemar_exact(0, 15) < 0.001
    # kappa sanity: perfect agreement -> 1
    assert kappa({"both_yes": 40, "both_no": 44,
                  "a_yes_b_no": 0, "a_no_b_yes": 0}) == 1.0
    print("ontg2 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    payload = json.load(sys.stdin)
    print(json.dumps(run(payload["metrics"]), indent=1, sort_keys=True))
