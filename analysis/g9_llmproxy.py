#!/usr/bin/env python3
"""g9-llmproxy pinned analysis — STAND-IN blinded-review feasibility read
(registry/experiments/g9-llmproxy.json; design note poc/g9-llmproxy/design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; fully deterministic (counting + Wilson bounds — no
bootstrap, no PRNG).

WHAT THIS IS (and is not): the blinded HUMAN reviewer required by the FROZEN
g9 record (GATE-H) is unavailable; a pinned cross-vendor LLM (judge-r1p,
GPT-5.6-Sol) fills the g9.review role over the SAME 50 blinded sheets as a
clearly-labelled STAND-IN. The composite statistic here estimates
'GPT-5.x-family blind endorsement of the authored explications' — NOT the
blinded human review, which remains frozen, unconsumed, and solely
adjudicating for HS-A. The record's extrapolation envelope binds every
reading of these numbers verbatim.

COMPOSITE (prereg S2, verbatim): per-sheet composite pass = mechanical
legality (MEASURED 50/50 at g9.author,
data/authored-explication-set/validation/mechanical-summary.json) AND
substitutable=yes AND cross_translatable=yes; cannot-say counts AGAINST
composite pass (escape-as-disagreement, ASM-0554); no-label sheets leave the
denominator and are capped by the instrument gate. The runner assembles the
integer counts; this script never re-derives labels.

GATES (prereg S4; INSTRUMENT-INVALID, never FAIL/PASS):
  adjudication_valid: preflight_pass AND n_labelled >= 45/50 AND
                      n_nolabel <= 5 AND retest per-field agreement >= 0.80.
  probe_valid:        deranged-explication probe (substitutability leg only)
                      n_probe_labelled >= 45/50 AND false-endorsement
                      point-rate < 0.30. Probe Q-XT is REPORTED-ONLY: the
                      cross-translatability leg has NO content-scramble
                      control by construction (ASM-0523 disclosure).

PRIMARY (prereg S5): A_g9p = n_composite_pass_proxy / n_labelled; one-sided
95% Wilson bounds (z=1.645, the analysis/g9.py closed form verbatim);
margin_threshold = published DeepNSM-8B point 0.24 + 0.10 = 0.34 (the frozen
g9 bar verbatim; severity-comparability uncalibrated, ASM-0522).
Verdict path (record rules, first match wins): INSTRUMENT-INVALID on either
gate -> FAIL-analog iff wilson_ub < 0.34 -> PASS-analog iff wilson_lb >= 0.34
(the envelope caps ANY PASS at 'weak feasibility proxy') -> INCONCLUSIVE
catch-all (missing record => fields unset => fail closed).

Fixture: --selftest (constructed records; HAND-COMPUTED values in comments,
cross-checked against an independent quadratic-solve Wilson implementation
at staging, 2026-07-10).
"""
import json
import sys

Z = 1.645                       # one-sided 95%, the analysis/g9.py closed form
MARGIN_OVER_PUBLISHED = 0.10    # the frozen g9 margin verbatim
LABELLED_MIN = 45               # of 50
NOLABEL_MAX = 5
RETEST_AGREE_MIN = 0.80         # FAIL direction only (single judge)
PROBE_LABELLED_MIN = 45         # of 50
PROBE_FALSE_ENDORSE_BAR = 0.30  # point rule; >= 0.30 invalidates
ARM = "review-adjudication-instrument"


def wilson_bounds(p, n):
    if n <= 0:
        return 0.0, 1.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def analyze(records):
    out = {"gates": {}, "analysis": {}}
    a = out["analysis"]
    adj = None
    for r in records:
        if r["config"]["arm"] == ARM:
            if adj is not None:
                print("g9-llmproxy analysis: duplicate %s record" % ARM,
                      file=sys.stderr)
                sys.exit(1)
            adj = r["metrics"]
    if adj is None:
        return out  # fields unset => INCONCLUSIVE (fail closed)

    n_sheets = int(adj["n_sheets"])
    n_lab = int(adj["n_labelled"])
    n_nolab = int(adj["n_nolabel"])
    n_comp = int(adj["n_composite_pass_proxy"])
    preflight = bool(adj["preflight_pass"])
    a["n_sheets"] = n_sheets
    a["n_labelled"] = n_lab
    a["n_nolabel"] = n_nolab
    a["n_composite_pass_proxy"] = n_comp

    # ---- instrument gate: coverage + retest stability floor ------------------
    n_rt_fields = int(adj["n_retest_fields"])
    n_rt_agree = int(adj["n_retest_field_agree"])
    retest = (n_rt_agree / n_rt_fields) if n_rt_fields else 0.0  # fail closed
    a["retest_agreement"] = retest
    out["gates"]["adjudication_valid"] = (
        preflight and n_lab >= LABELLED_MIN and n_nolab <= NOLABEL_MAX
        and retest >= RETEST_AGREE_MIN - 1e-12)

    # ---- probe gate: deranged-explication false-endorsement (Q-SUB leg) -----
    n_probe_lab = int(adj["n_probe_labelled"])
    n_probe_fe = int(adj["n_probe_sub_yes"])
    fe_rate = (n_probe_fe / n_probe_lab) if n_probe_lab else 1.0  # fail closed
    a["probe_false_endorse_rate"] = fe_rate
    a["probe_xt_yes_rate"] = (int(adj["n_probe_xt_yes"]) / n_probe_lab
                              if n_probe_lab else 0.0)  # REPORTED-ONLY
    out["gates"]["probe_valid"] = (
        n_probe_lab >= PROBE_LABELLED_MIN
        and fe_rate < PROBE_FALSE_ENDORSE_BAR - 1e-12)

    # ---- the frozen-bar analog on the proxy composite rate ------------------
    rate = (n_comp / n_lab) if n_lab > 0 else 0.0
    lb, ub = wilson_bounds(rate, n_lab)
    thr = int(adj["deepnsm_published_point_x100"]) / 100.0 + MARGIN_OVER_PUBLISHED
    a["composite_rate_proxy"] = rate
    a["wilson_lb_proxy"] = lb
    a["wilson_ub_proxy"] = ub
    a["margin_threshold"] = thr
    a["clears_margin_proxy"] = lb >= thr
    a["below_margin_proxy"] = ub < thr

    # ---- per-leg diagnostics (REPORTED-ONLY; xt is the weakest leg) ----------
    a["sub_yes_rate"] = (int(adj["n_sub_yes"]) / n_lab) if n_lab else 0.0
    a["xt_yes_rate"] = (int(adj["n_xt_yes"]) / n_lab) if n_lab else 0.0
    return out


# --------------------------------------------------------------------------
def _rec(n_sheets=50, n_lab=48, n_nolab=2, n_comp=30, n_sub=33, n_xt=42,
         n_probe_lab=47, n_probe_fe=6, n_probe_xt=40,
         n_rt_fields=20, n_rt_agree=18, preflight=True, published_x100=24):
    return {"config": {"arm": ARM, "rung": "none", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_sheets": n_sheets, "n_labelled": n_lab,
                        "n_nolabel": n_nolab,
                        "n_composite_pass_proxy": n_comp,
                        "n_sub_yes": n_sub, "n_xt_yes": n_xt,
                        "n_probe_labelled": n_probe_lab,
                        "n_probe_sub_yes": n_probe_fe,
                        "n_probe_xt_yes": n_probe_xt,
                        "n_retest_fields": n_rt_fields,
                        "n_retest_field_agree": n_rt_agree,
                        "preflight_pass": preflight,
                        "deepnsm_published_point_x100": published_x100,
                        "labels_sha256": "0" * 64}}


def selftest():
    # PASS-analog branch — HAND (cross-checked, quadratic solve): 30/48 = .625;
    # z2 = 2.706025; Wilson LB = .50629, UB = .73037; threshold .24+.10 = .34;
    # LB .50629 >= .34 => clears. retest 18/20 = .90 >= .80; fe 6/47 = .12766 < .30
    out = analyze([_rec()])
    assert out["gates"]["adjudication_valid"] is True
    assert out["gates"]["probe_valid"] is True
    assert abs(out["analysis"]["composite_rate_proxy"] - 0.625) < 1e-12
    assert abs(out["analysis"]["wilson_lb_proxy"] - 0.50629) < 5e-4
    assert abs(out["analysis"]["wilson_ub_proxy"] - 0.73037) < 5e-4
    assert abs(out["analysis"]["margin_threshold"] - 0.34) < 1e-12
    assert out["analysis"]["clears_margin_proxy"] is True
    assert out["analysis"]["below_margin_proxy"] is False
    assert abs(out["analysis"]["sub_yes_rate"] - 33 / 48) < 1e-12
    assert abs(out["analysis"]["xt_yes_rate"] - 42 / 48) < 1e-12
    assert abs(out["analysis"]["probe_false_endorse_rate"] - 6 / 47) < 1e-12
    assert abs(out["analysis"]["probe_xt_yes_rate"] - 40 / 47) < 1e-12
    assert abs(out["analysis"]["retest_agreement"] - 0.90) < 1e-12

    # FAIL-analog branch — HAND: 8/48 = .16667; Wilson UB = .27237 < .34
    out = analyze([_rec(n_comp=8, n_sub=10, n_xt=20)])
    assert out["gates"]["adjudication_valid"] is True
    assert abs(out["analysis"]["wilson_ub_proxy"] - 0.27237) < 5e-4
    assert out["analysis"]["below_margin_proxy"] is True
    assert out["analysis"]["clears_margin_proxy"] is False

    # INSTRUMENT branches (each single-cause)
    out = analyze([_rec(n_lab=44, n_nolab=5, n_comp=28, n_sub=30, n_xt=40)])
    assert out["gates"]["adjudication_valid"] is False   # coverage 44 < 45
    out = analyze([_rec(n_lab=44, n_nolab=6, n_comp=28, n_sub=30, n_xt=40)])
    assert out["gates"]["adjudication_valid"] is False   # no-label 6 > 5
    out = analyze([_rec(n_rt_agree=15)])                 # 15/20 = .75 < .80
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(preflight=False)])
    assert out["gates"]["adjudication_valid"] is False
    # probe: 15/47 = .31915 >= .30 => probe_valid False
    out = analyze([_rec(n_probe_fe=15)])
    assert out["gates"]["probe_valid"] is False
    # probe point rule boundary IN: ceil — 14.1/47… use 47 lab, 15 fe above;
    # exact boundary: 141/470 impossible here; check coverage floor instead
    out = analyze([_rec(n_probe_lab=44, n_probe_fe=0, n_probe_xt=40)])
    assert out["gates"]["probe_valid"] is False          # 44 < 45

    # missing record => everything unset => INCONCLUSIVE downstream
    out = analyze([])
    assert out == {"gates": {}, "analysis": {}}
    print("g9-llmproxy selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    final = [r for r in records if r.get("phase") == "final"
             and r.get("experiment") == "g9-llmproxy"]
    print(json.dumps(analyze(final), sort_keys=True))
