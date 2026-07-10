#!/usr/bin/env python3
"""m0a-llmproxy pinned analysis — STAND-IN mapper measurement
(registry/experiments/m0a-llmproxy.json; design note
poc/m0a-llmproxy/design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; fully deterministic (counting + closed forms + an exact
Clopper-Pearson bisection — no bootstrap, no PRNG).

WHAT THIS IS (and is not): the M0a pre-registration (docs/poc-design.md Phase
M) names HUMAN annotation; a pinned blind cross-vendor LLM (judge-m1p,
GPT-5.6-Sol) judges the SAME 300 pinned annotation-sample items under
kernel-naive per-stratum rendering. The resulting P/R REPLACE the 2026-07-07
non-blind agent-judged provisionals as the programme's PROVISIONAL numbers
(upgrading blindness + author-family independence ONLY) and remain WEAK-PROXY
pending the human pass, which stays the sole gold standard. The record's
extrapolation envelope binds every reading verbatim.

NO KILL BAR BY DESIGN (prereg S6): M0a is a MEASUREMENT; the proxy cannot
invent a pass/fail bar on P/R. Verdict path (record rules, first match wins):
INSTRUMENT-INVALID iff either gate fails -> PASS iff both gates hold (PASS
means EXACTLY 'a valid blind-LLM proxy measurement of the M0a quantities
exists', never a mapper-quality endorsement) -> INCONCLUSIVE catch-all
(missing record => fields unset => fail closed). This script emits NO
FAIL-shaped field on the P/R values.

ESTIMATOR (prereg S5; mapper/m0/compute-pr.py sha 5858b116… reimplemented
VERBATIM with proxy labels, denominators restricted to labelled items,
ASM-0542): stratum-population-weighted precision (strict: unclear counted
incorrect; lenient: correct) over concept+prime; recall = correct-mapped mass
/ (correct-mapped mass + abstain-miss mass + none-miss mass);
recall_lower_bound95 = recall at the none-miss rate's exact one-sided 95%
Clopper-Pearson UPPER bound over the observed none-stratum sample (the
pre-existing thin-coverage discipline carried over UNCHANGED; the published
k=0 closed form 1 - 0.05**(1/n) is the k=0 special case of the bisection
here, asserted in the selftest). Populations pinned from
mapper/m0/results/m0a-report.json (sha c424be2d…).

GATES (prereg S4; INSTRUMENT-INVALID, never FAIL):
  adjudication_valid: preflight_pass AND n_labelled >= 285/300 AND >= 90 per
                      100-item stratum AND >= 45 per 50-item stratum AND
                      retest agreement >= 0.80.
  probe_valid:        deranged-gloss probe n_probe_labelled >= 36/40 AND
                      false-endorsement ('correct') point-rate < 0.30.

DIAGNOSTIC (REPORTED-ONLY, never gated, never validation): per-stratum raw
agreement of proxy labels with the pinned 2026-07-07 non-blind agent labels
(mapper/m0/agent-judgments.jsonl sha 6f291b69…) — a blindness+judge-family
JOINT delta, unattributable within this design (ASM-0543).

Fixture: --selftest (constructed records; HAND-COMPUTED values in comments,
cross-checked against independent recomputation at staging, 2026-07-10).
"""
import json
import math
import sys

# Stratum token populations, pinned VERBATIM from the published
# mapper/m0/results/m0a-report.json sampling block (sha c424be2d…).
POP = {"concept": 117563, "prime": 504500, "abstain": 181388, "none": 2958417}
MAPPED_POP = POP["concept"] + POP["prime"]

LABELLED_TOTAL_MIN = 285          # of 300
STRATUM_FLOORS = {"concept": 90, "prime": 90, "abstain": 45, "none": 45}
RETEST_AGREE_MIN = 0.80           # FAIL direction only (single judge)
PROBE_LABELLED_MIN = 36           # of 40
PROBE_FALSE_ENDORSE_BAR = 0.30    # point rule; >= 0.30 invalidates
CP_ALPHA = 0.05                   # one-sided 95% Clopper-Pearson upper
ARM = "mapper-annotation-instrument"
STRATA = ("concept", "prime", "abstain", "none")


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i)
               for i in range(k + 1))


def cp_upper(k, n, alpha=CP_ALPHA):
    """Exact one-sided Clopper-Pearson upper bound: the p at which
    P(X <= k | n, p) = alpha (monotone decreasing in p; bisection to ~1e-15).
    k = 0 reduces to the published closed form 1 - alpha**(1/n)."""
    if n <= 0:
        return 1.0  # fail closed
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def analyze(records):
    out = {"gates": {}, "analysis": {}}
    a = out["analysis"]
    adj = None
    for r in records:
        if r["config"]["arm"] == ARM:
            if adj is not None:
                print("m0a-llmproxy analysis: duplicate %s record" % ARM,
                      file=sys.stderr)
                sys.exit(1)
            adj = r["metrics"]
    if adj is None:
        return out  # fields unset => INCONCLUSIVE (fail closed)

    n_items = int(adj["n_items"])
    lab = {s: int(adj["n_labelled_%s" % s]) for s in STRATA}
    n_lab = sum(lab.values())
    preflight = bool(adj["preflight_pass"])
    a["n_items"] = n_items
    a["n_labelled"] = n_lab
    a["n_labelled_by_stratum"] = dict(lab)

    # ---- instrument gate: coverage floors + retest stability floor -----------
    n_rt_cmp = int(adj["n_retest_compared"])
    n_rt_agr = int(adj["n_retest_agree"])
    retest = (n_rt_agr / n_rt_cmp) if n_rt_cmp else 0.0  # fail closed
    a["retest_agreement"] = retest
    out["gates"]["adjudication_valid"] = (
        preflight and n_lab >= LABELLED_TOTAL_MIN
        and all(lab[s] >= STRATUM_FLOORS[s] for s in STRATA)
        and retest >= RETEST_AGREE_MIN - 1e-12)

    # ---- probe gate: deranged-gloss false-endorsement ------------------------
    n_probe_lab = int(adj["n_probe_labelled"])
    n_probe_fe = int(adj["n_probe_false_endorse"])
    fe_rate = (n_probe_fe / n_probe_lab) if n_probe_lab else 1.0  # fail closed
    a["probe_false_endorse_rate"] = fe_rate
    out["gates"]["probe_valid"] = (
        n_probe_lab >= PROBE_LABELLED_MIN
        and fe_rate < PROBE_FALSE_ENDORSE_BAR - 1e-12)

    # ---- the published estimator, proxy-labelled (compute-pr.py verbatim) ----
    # precision per stratum over LABELLED items; strict: unclear incorrect.
    p_strict, p_lenient = {}, {}
    for s in ("concept", "prime"):
        n_s = lab[s]
        n_c = int(adj["n_correct_%s" % s])
        n_u = int(adj["n_unclear_%s" % s])
        p_strict[s] = (n_c / n_s) if n_s else 0.0
        p_lenient[s] = ((n_c + n_u) / n_s) if n_s else 0.0

    def wprec(p):
        return (p["concept"] * POP["concept"] + p["prime"] * POP["prime"]) / MAPPED_POP

    ws, wl = wprec(p_strict), wprec(p_lenient)
    a["precision_strict_proxy"] = ws
    a["precision_lenient_proxy"] = wl
    a["precision_by_stratum_strict"] = dict(p_strict)

    abstain_miss = (int(adj["n_candidate_correct_abstain"]) / lab["abstain"]
                    if lab["abstain"] else 0.0)
    none_miss = (int(adj["n_should_map_none"]) / lab["none"]
                 if lab["none"] else 0.0)
    none_upper95 = cp_upper(int(adj["n_should_map_none"]), lab["none"])
    a["abstain_miss_rate"] = abstain_miss
    a["none_miss_rate"] = none_miss
    a["none_miss_upper95"] = none_upper95

    def recall(prec, none_rate):
        tp = prec * MAPPED_POP
        missed = abstain_miss * POP["abstain"] + none_rate * POP["none"]
        return tp / (tp + missed) if (tp + missed) > 0 else 0.0

    a["recall_strict_proxy"] = recall(ws, none_miss)
    a["recall_lenient_proxy"] = recall(wl, none_miss)
    a["recall_lower_bound95"] = recall(ws, none_upper95)

    # ---- reported-only diagnostic: agreement with the non-blind agent labels -
    agree = {}
    for s in STRATA:
        n_cmp = int(adj["n_agent_compared_%s" % s])
        agree[s] = (int(adj["n_agent_agree_%s" % s]) / n_cmp) if n_cmp else 0.0
    a["agent_agreement_by_stratum"] = agree
    return out


# --------------------------------------------------------------------------
def _rec(n_items=300, lab_c=100, lab_p=100, lab_a=50, lab_n=50,
         cor_c=80, unc_c=10, cor_p=85, unc_p=5, cand_a=10, smap_n=0,
         n_probe_lab=38, n_probe_fe=5, n_rt_cmp=30, n_rt_agr=27,
         ag_cmp=(100, 100, 50, 50), ag_agr=(90, 88, 45, 50), preflight=True):
    m = {"n_items": n_items,
         "n_labelled_concept": lab_c, "n_labelled_prime": lab_p,
         "n_labelled_abstain": lab_a, "n_labelled_none": lab_n,
         "n_correct_concept": cor_c, "n_unclear_concept": unc_c,
         "n_correct_prime": cor_p, "n_unclear_prime": unc_p,
         "n_candidate_correct_abstain": cand_a, "n_should_map_none": smap_n,
         "n_probe_labelled": n_probe_lab, "n_probe_false_endorse": n_probe_fe,
         "n_retest_compared": n_rt_cmp, "n_retest_agree": n_rt_agr,
         "preflight_pass": preflight, "labels_sha256": "0" * 64}
    for s, c, g in zip(STRATA, ag_cmp, ag_agr):
        m["n_agent_compared_%s" % s] = c
        m["n_agent_agree_%s" % s] = g
    return {"config": {"arm": ARM, "rung": "none", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0}, "metrics": m}


def selftest():
    # Measurement branch — HAND (cross-checked at staging):
    # p_strict = {concept .80, prime .85};
    # wprec_strict = (.80*117563 + .85*504500)/622063 = 522875.4/622063
    #              = .8405506 (rounded .84055)
    # p_lenient = {.90, .90} => wprec_lenient = .90
    # abstain_miss = 10/50 = .2; none_miss = 0/50 = 0;
    # none_upper95 = 1 - .05**(1/50) = .0581551 (k=0 closed form)
    # recall_strict = .8405506*622063 / (.8405506*622063 + .2*181388)
    #               = 522875.4/559153.0 = .9351204
    # recall_lenient = 559856.7/596134.3 = .9391453
    # recall_lb95 = 522875.4/(522875.4 + 36277.6 + .0581551*2958417)
    #             = 522875.4/731200.5 = .7150922
    out = analyze([_rec()])
    assert out["gates"]["adjudication_valid"] is True
    assert out["gates"]["probe_valid"] is True
    a = out["analysis"]
    assert a["n_labelled"] == 300
    assert abs(a["precision_strict_proxy"] - 0.84055) < 5e-5
    assert abs(a["precision_lenient_proxy"] - 0.90) < 1e-12
    assert abs(a["precision_by_stratum_strict"]["concept"] - 0.80) < 1e-12
    assert abs(a["abstain_miss_rate"] - 0.20) < 1e-12
    assert abs(a["none_miss_rate"] - 0.0) < 1e-12
    assert abs(a["none_miss_upper95"] - (1 - 0.05 ** (1 / 50))) < 1e-9
    assert abs(a["recall_strict_proxy"] - 0.93512) < 5e-5
    assert abs(a["recall_lenient_proxy"] - 0.93915) < 5e-5
    assert abs(a["recall_lower_bound95"] - 0.71509) < 5e-5
    assert abs(a["probe_false_endorse_rate"] - 5 / 38) < 1e-12
    assert abs(a["retest_agreement"] - 0.90) < 1e-12
    assert abs(a["agent_agreement_by_stratum"]["prime"] - 0.88) < 1e-12
    # NO kill bar: no FAIL-shaped field may exist on the P/R values.
    assert not any("fail" in k or "pass" in k for k in a)

    # Clopper-Pearson bisection is the EXACT bound: at k=3, n=50 the returned
    # p satisfies P(X<=3 | 50, p) = 0.05 (HAND: p = .1478372).
    p3 = cp_upper(3, 50)
    assert abs(p3 - 0.14784) < 5e-5
    assert abs(binom_cdf(3, 50, p3) - 0.05) < 1e-9
    # nonzero none-miss propagates: k=2/50 => none_miss=.04, upper95 > .04
    out = analyze([_rec(smap_n=2)])
    assert abs(out["analysis"]["none_miss_rate"] - 0.04) < 1e-12
    assert out["analysis"]["none_miss_upper95"] > 0.04

    # INSTRUMENT branches (each single-cause)
    out = analyze([_rec(lab_c=89, cor_c=71, unc_c=9)])   # stratum floor 89 < 90
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(lab_a=44, cand_a=9)])            # 50-stratum floor 44 < 45
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(lab_c=95, lab_p=95, lab_a=47, lab_n=47,
                        cor_c=76, unc_c=9, cor_p=80, unc_p=5, cand_a=9)])
    assert out["gates"]["adjudication_valid"] is False   # total 284 < 285
    out = analyze([_rec(n_rt_agr=23)])                   # 23/30 = .7667 < .80
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(preflight=False)])
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(n_probe_fe=12)])                 # 12/38 = .3158 >= .30
    assert out["gates"]["probe_valid"] is False
    out = analyze([_rec(n_probe_lab=35, n_probe_fe=0)])  # coverage 35 < 36
    assert out["gates"]["probe_valid"] is False
    # probe point rule boundary IN: 12/40 = .30 exactly => invalid
    out = analyze([_rec(n_probe_lab=40, n_probe_fe=12)])
    assert out["gates"]["probe_valid"] is False

    # missing record => everything unset => INCONCLUSIVE downstream
    out = analyze([])
    assert out == {"gates": {}, "analysis": {}}
    print("m0a-llmproxy selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    final = [r for r in records if r.get("phase") == "final"
             and r.get("experiment") == "m0a-llmproxy"]
    print(json.dumps(analyze(final), sort_keys=True))
