#!/usr/bin/env python3
"""f2b-transfer-llmproxy pinned analysis — STAGE-1-ONLY stand-in feasibility
read (registry/experiments/f2b-transfer-llmproxy.json; design note
poc/f2b-transfer/llmproxy-design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; fully deterministic (counting + Wilson bounds — no
bootstrap, no PRNG).

WHAT THIS IS (and is not): the human judge-1 required by the FROZEN
f2b-transfer §4 protocol is unavailable; a pinned cross-vendor LLM
(GPT-5.6-Sol) fills the judge-1 ROLE under the identical blind rendering as a
clearly-labelled STAND-IN. The endorsement statistic here estimates
'GPT-5.x-family endorsement of the kernel's content' — NOT the human-anchored
external gold of f2b-transfer, which remains frozen, unconsumed, and solely
adjudicating for H-TRANSFER vs H-CIRC. The extrapolation envelope of the
record binds every reading of these numbers verbatim.

SINGLE-JUDGE-FAMILY TREATMENT (the correlation honesty rule): judge-1p
(GPT-5.6) and the diagnostic judge-2 (GPT-5.5, reused from the in-flight
f2b-transfer instrument run) are same-vendor, adjacent-generation models.
They are NOT a two-judge panel in the f2b-transfer §4 sense; concordance
between them is expected under family correlation and carries ZERO validation
weight. Therefore:
  - the primary endorsement A_1p is computed from judge-1p's labels ALONE
    (escape tokens NONE / 'cannot say' count as DISAGREEMENT; no-label items
    leave the denominator and are capped by the instrument gate);
  - raw judge-1p/judge-2 agreement is a gate only in its FAIL direction
    (< 0.80 => the single-family instrument is unstable => INSTRUMENT-INVALID);
    its pass direction validates nothing;
  - A_j2 and the concordant-panel analog A_panel are REPORTED-ONLY
    diagnostics (never verdict-bearing).

PROBE GATE (the judge-level content-scramble control): 60 deranged-gloss
def-match probes (data/d-adj-t-llmproxy/deranged-probe.jsonl) in which the
own-gloss is deranged out, so a content-competent judge must answer NONE.
false-endorsement point-rate >= 0.30, or probe coverage < 54/60, or a failed
preflight => /gates/probe_valid false => INSTRUMENT-INVALID (style-driven
endorsement of NSM-shaped text would fabricate a proxy-PASS under H-CIRC;
this gate exists so it cannot).

Verdict path (mirrors the frozen record's rules; first match wins):
  1 INSTRUMENT-INVALID on either gate -> 2 FAIL on the kill-(d) analog
  (Wilson one-sided 95% LB of A_1p < 0.70) -> 3 PASS (LB >= 0.70; the
  envelope caps a PASS at 'weak feasibility proxy') -> 4 INCONCLUSIVE
  catch-all (missing record => fields unset => fail closed).

Fixture: --selftest (constructed records; HAND-COMPUTED values in comments).
"""
import json
import sys

Z_ONE_SIDED = 1.645
ENDORSEMENT_BAR = 0.70   # kill-(d) analog: Wilson one-sided 95% LB < 0.70
JUDGE_AGREE_MIN = 0.80   # single-family stability gate (FAIL direction only)
LABELLED_MIN = 300       # of 360 (mirrors frozen G-adj n_adjudicated >= 300)
NOLABEL_MAX = 18         # 5% of 360 (judge-2 spec §6 abort bar, reused)
PROBE_FALSE_ENDORSE_BAR = 0.30  # point rule (house kill-(b) style)
PROBE_LABELLED_MIN = 54  # 90% of 60
ARM_ADJ = "adjudication-instrument"


def wilson_lb(p, n, z=Z_ONE_SIDED):
    if n <= 0:
        return 0.0
    p = min(max(p, 0.0), 1.0)
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def analyze(records):
    out = {"gates": {}, "analysis": {}}
    a = out["analysis"]
    adj = None
    for r in records:
        if r["config"]["arm"] == ARM_ADJ:
            if adj is not None:
                print("f2b-transfer-llmproxy analysis: duplicate "
                      "adjudication-instrument record", file=sys.stderr)
                sys.exit(1)
            adj = r["metrics"]
    if adj is None:
        return out  # fields unset => INCONCLUSIVE (fail closed)

    n_items = int(adj["n_items"])
    n_lab = int(adj["n_labelled_j1p"])
    n_nolab = int(adj["n_nolabel_j1p"])
    n_agree = int(adj["n_agree_j1p"])
    n_escape = int(adj["n_escape_j1p"])
    jp_both = int(adj["judge_pairs_both_labelled"])
    jp_eq = int(adj["judge_pairs_token_equal"])
    preflight = bool(adj["preflight_pass"])
    a["n_items"] = n_items
    a["n_labelled_j1p"] = n_lab
    a["n_nolabel_j1p"] = n_nolab
    a["n_escape_j1p"] = n_escape

    # ---- instrument gate: judge-1p coverage + single-family stability -------
    agree_raw = (jp_eq / jp_both) if jp_both else 0.0
    a["judge_pair_agreement_raw"] = agree_raw
    out["gates"]["adjudication_valid"] = (
        preflight and n_lab >= LABELLED_MIN and n_nolab <= NOLABEL_MAX
        and agree_raw >= JUDGE_AGREE_MIN - 1e-12)

    # ---- probe gate: deranged-gloss false-endorsement (escape function) -----
    n_probe_lab = int(adj["n_probe_labelled"])
    n_probe_fe = int(adj["n_probe_false_endorse"])
    fe_rate = (n_probe_fe / n_probe_lab) if n_probe_lab else 1.0  # fail closed
    a["probe_false_endorse_rate"] = fe_rate
    a["probe_none_rate"] = (int(adj["n_probe_none"]) / n_probe_lab
                            if n_probe_lab else 0.0)
    a["probe_deranged_pick_rate"] = (int(adj["n_probe_deranged_pick"])
                                     / n_probe_lab if n_probe_lab else 0.0)
    out["gates"]["probe_valid"] = (
        n_probe_lab >= PROBE_LABELLED_MIN
        and fe_rate < PROBE_FALSE_ENDORSE_BAR - 1e-12)

    # ---- the kill-(d) analog on judge-1p's labels ALONE ---------------------
    # A_1p: escape tokens count as DISAGREEMENT (a judge that cannot endorse
    # the kernel's content is evidence, never an instrument event); no-label
    # items leave the denominator (instrument events, capped by the gate).
    A = (n_agree / n_lab) if n_lab > 0 else 0.0
    a["external_endorsement_proxy"] = A
    a["external_endorsement_proxy_lb"] = wilson_lb(A, n_lab)
    a["stage1_endorsement_fail"] = (a["external_endorsement_proxy_lb"]
                                    < ENDORSEMENT_BAR)
    a["endorsement_pass"] = not a["stage1_endorsement_fail"]

    # ---- reported-only diagnostics (never verdict-bearing) ------------------
    n_lab_j2 = int(adj["n_labelled_j2"])
    a["a_j2"] = (int(adj["n_agree_j2"]) / n_lab_j2) if n_lab_j2 else 0.0
    pr = int(adj["panel_resolved"])
    a["a_panel_concordant"] = (int(adj["panel_agree_membership"]) / pr
                               if pr else 0.0)
    a["panel_unresolved_fraction"] = (1.0 - pr / jp_both) if jp_both else 1.0
    return out


# --------------------------------------------------------------------------
def _rec(n_items=360, n_lab=350, n_nolab=10, n_agree=315, n_escape=20,
         jp_both=330, jp_eq=300, n_lab_j2=355, n_agree_j2=300,
         panel_res=300, panel_agree=280, n_probe_lab=60, n_probe_fe=6,
         n_probe_none=52, n_probe_dp=4, preflight=True):
    return {"config": {"arm": ARM_ADJ, "rung": "none", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_items": n_items, "n_labelled_j1p": n_lab,
                        "n_nolabel_j1p": n_nolab, "n_agree_j1p": n_agree,
                        "n_escape_j1p": n_escape,
                        "judge_pairs_both_labelled": jp_both,
                        "judge_pairs_token_equal": jp_eq,
                        "n_labelled_j2": n_lab_j2, "n_agree_j2": n_agree_j2,
                        "panel_resolved": panel_res,
                        "panel_agree_membership": panel_agree,
                        "n_probe_labelled": n_probe_lab,
                        "n_probe_false_endorse": n_probe_fe,
                        "n_probe_none": n_probe_none,
                        "n_probe_deranged_pick": n_probe_dp,
                        "preflight_pass": preflight,
                        "labels_sha256": "0" * 64}}


def selftest():
    # PASS branch — HAND: A = 315/350 = 0.9; Wilson LB one-sided 95%:
    # z2 = 2.706025; centre = .9 + 2.706025/700 = .9038660;
    # spread = 1.645*sqrt(.9*.1/350 + 2.706025/490000)
    #        = 1.645*sqrt(.000262665) = .0266605;
    # LB = (.9038660-.0266605)/(1+2.706025/350) = .8772055/1.0077315 = .87048
    # agree_raw = 300/330 = .90909 >= .80; fe_rate = 6/60 = .10 < .30
    out = analyze([_rec()])
    assert out["gates"]["adjudication_valid"] is True
    assert out["gates"]["probe_valid"] is True
    assert abs(out["analysis"]["external_endorsement_proxy"] - 0.9) < 1e-12
    assert abs(out["analysis"]["external_endorsement_proxy_lb"] - 0.87048) < 5e-4
    assert out["analysis"]["stage1_endorsement_fail"] is False
    assert out["analysis"]["endorsement_pass"] is True
    # diagnostics — HAND: a_j2 = 300/355 = .84507; a_panel = 280/300 = .93333;
    # unresolved = 1 - 300/330 = .09091
    assert abs(out["analysis"]["a_j2"] - 300 / 355) < 1e-12
    assert abs(out["analysis"]["a_panel_concordant"] - 280 / 300) < 1e-12
    assert abs(out["analysis"]["panel_unresolved_fraction"] - 1 + 300 / 330) < 1e-12

    # FAIL branch — HAND: A = 252/350 = .72; centre = .72 + .0038660 = .7238660;
    # spread = 1.645*sqrt(.72*.28/350 + .0000055225) = 1.645*sqrt(.000581522)
    #        = .0396688; LB = .6841972/1.0077315 = .67895 < .70 => kill fires
    out = analyze([_rec(n_agree=252)])
    assert out["gates"]["adjudication_valid"] is True
    assert abs(out["analysis"]["external_endorsement_proxy_lb"] - 0.67895) < 5e-4
    assert out["analysis"]["stage1_endorsement_fail"] is True

    # INSTRUMENT branches
    # stability: 250/330 = .75758 < .80 => adjudication_valid False
    out = analyze([_rec(jp_eq=250)])
    assert out["gates"]["adjudication_valid"] is False
    # coverage: n_lab 290 < 300 => False (n_nolab kept within cap)
    out = analyze([_rec(n_lab=290, n_nolab=18, n_agree=260)])
    assert out["gates"]["adjudication_valid"] is False
    # no-label cap: 19 > 18 => False
    out = analyze([_rec(n_lab=341, n_nolab=19)])
    assert out["gates"]["adjudication_valid"] is False
    # preflight fail-closed
    out = analyze([_rec(preflight=False)])
    assert out["gates"]["adjudication_valid"] is False
    # probe: 18/60 = .30 >= .30 => probe_valid False (point rule, boundary IN)
    out = analyze([_rec(n_probe_fe=18)])
    assert out["gates"]["probe_valid"] is False
    # probe coverage: 53 < 54 => False even at fe 0
    out = analyze([_rec(n_probe_lab=53, n_probe_fe=0, n_probe_none=50)])
    assert out["gates"]["probe_valid"] is False

    # missing record => everything unset => INCONCLUSIVE downstream
    out = analyze([])
    assert out == {"gates": {}, "analysis": {}}
    print("f2b-transfer-llmproxy selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    final = [r for r in records if r.get("phase") == "final"
             and r.get("experiment") == "f2b-transfer-llmproxy"]
    print(json.dumps(analyze(final), sort_keys=True))
