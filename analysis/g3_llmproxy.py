#!/usr/bin/env python3
"""g3-llmproxy pinned analysis — STAND-IN semantics-pin annotation read
(registry/experiments/g3-llmproxy.json; design note poc/g3-llmproxy/design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; fully deterministic (counting + Wilson bounds + the
analysis/g3.py kappa closed form — no bootstrap, no PRNG).

WHAT THIS IS (and is not): the two independent blinded HUMAN annotators the
FROZEN g3 record requires (GATE-H) are unsourced; a pinned cross-family LLM
pair (judge-pA GPT-5.6-Sol; judge-pB Claude Haiku 4.5) fills the g3.annotate
role over the SAME 200 pinned instances under the frozen two-pass protocol.
The violation rates here ARE two LLMs' blind judgments — NOT native-speaker
human competence (the HS3 estimand). g3 remains FROZEN, unconsumed, solely
adjudicating; only the human g3 can trigger HS2 auto-resolution / g5 pruning
/ Pi demotion. The record's extrapolation envelope binds every reading.

DERIVED VIOLATIONS (frozen rule verbatim, annotation-protocol.md): necessity
violation iff q1 = yes AND q2 = no; sufficiency violation iff q1 = no AND
q2 = yes. An instance is DECISIVE for a judge iff its q1 AND q2 are both in
{yes, no}; DUAL-DECISIVE iff decisive for both judges. cannot-say is neither
violation nor satisfaction (ASM-0533/ASM-0554); no-label leaves denominators.

TWO-SIDED BRACKET (prereg S4/S6, ASM-0531 — the human record's combination
rule stays unconsumed): over dual-decisive instances,
  concordant rate = both judges derive the violation (the FAIL-analog side);
  union rate      = either judge derives it        (the PASS-analog side).
Wilson bounds z = 1.645 (the analysis/g3.py closed form verbatim) over
n_dual_decisive. Verdict path (record rules, first match wins):
INSTRUMENT-INVALID on either gate -> FAIL-analog iff concordant necessity
Wilson LB > 0.10 (/analysis/proxy_fail) -> PASS-analog iff union necessity
Wilson UB <= 0.10 (/analysis/proxy_pass; the envelope caps ANY PASS at 'weak
feasibility proxy') -> INCONCLUSIVE catch-all (missing record => fields
unset => fail closed). Each verdict direction clears under the combination
rule LEAST favourable to it.

GATES (prereg S4/S5; INSTRUMENT-INVALID, never FAIL/PASS):
  adjudication_valid: preflight_pass AND n_dual_decisive >= 170/200 AND
                      per judge per pass cannot-say <= 5% AND no-label <= 5%
                      AND kappa_pair >= 0.4 (the frozen g3 kappa rule carried
                      over as judge-pair instability, never FAIL).
  probe_valid:        probe-B (mismatched-conditions control), PER JUDGE:
                      coverage >= 27/30 AND false-satisfaction (q2=yes where
                      'no' is correct by construction) point-rate < 0.30.

SECONDARY: same bracket on sufficiency (union UB <= 0.10 =>
sufficiency_equivalence_survives_proxy); per-judge rates; escape rates; the
pass-B failing-cid histogram (diagnostic only — the beginnings of the failure
taxonomy the human round will need).

Fixture: --selftest (constructed records; HAND-COMPUTED values in comments —
the 12/200 and 30/200 Wilson constants are the analysis/g3.py fixture values
verbatim; kappa cross-checked by hand at staging, 2026-07-10).
"""
import json
import sys

Z = 1.645                    # one-sided 95% each side, analysis/g3.py verbatim
BAR = 0.10                   # the frozen g3 10% bar verbatim
KAPPA_MIN = 0.4              # frozen g3 rule carried over (instrument only)
DUAL_DECISIVE_MIN = 170      # of 200
ESCAPE_MAX = 0.05            # per judge per pass (protocol ~5%, mechanical)
NOLABEL_MAX = 0.05           # per judge per pass
PROBE_LABELLED_MIN = 27      # of 30, per judge
PROBE_FALSE_SAT_BAR = 0.30   # point rule; >= 0.30 invalidates
ARM = "instance-annotation-instrument"
JUDGES = ("judge-pA", "judge-pB")


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
    out = {"gates": {}, "analysis": {}}
    a = out["analysis"]
    adj = None
    for r in records:
        if r["config"]["arm"] == ARM:
            if adj is not None:
                print("g3-llmproxy analysis: duplicate %s record" % ARM,
                      file=sys.stderr)
                sys.exit(1)
            adj = r["metrics"]
    if adj is None:
        return out  # fields unset => INCONCLUSIVE (fail closed)

    n_inst = int(adj["n_instances"])
    n_dual = int(adj["n_dual_decisive"])
    preflight = bool(adj["preflight_pass"])
    a["n_instances"] = n_inst
    a["n_dual_decisive"] = n_dual

    # ---- kappa on the per-instance necessity indicator (dual-decisive 2x2) --
    nb, nn = int(adj["n_nec_both"]), int(adj["n_nec_neither"])
    na, nb2 = int(adj["n_nec_a_only"]), int(adj["n_nec_b_only"])
    if nb + nn + na + nb2 != n_dual:
        print("g3-llmproxy analysis: necessity 2x2 does not sum to "
              "n_dual_decisive", file=sys.stderr)
        sys.exit(1)
    kap = kappa_2x2(nb, nn, na, nb2)
    a["kappa_pair"] = kap

    # ---- bracket counts must be consistent with the 2x2 ---------------------
    n_conc = int(adj["n_necessity_concordant"])
    n_union = int(adj["n_necessity_union"])
    if n_conc != nb or n_union != nb + na + nb2:
        print("g3-llmproxy analysis: bracket counts inconsistent with the "
              "necessity 2x2", file=sys.stderr)
        sys.exit(1)

    # ---- escape / no-label / coverage gate ----------------------------------
    escape_ok = True
    escapes = {}
    for j, tag in (("judge-pA", "a"), ("judge-pB", "b")):
        row = {}
        for pas, ptag in (("pass_a", "1"), ("pass_b", "2")):
            cs = int(adj["n_cannot_say_%s%s" % (tag, ptag)])
            nl = int(adj["n_nolabel_%s%s" % (tag, ptag)])
            cs_rate = (cs / n_inst) if n_inst else 1.0
            nl_rate = (nl / n_inst) if n_inst else 1.0
            row["%s_cannot_say" % pas] = cs_rate
            row["%s_nolabel" % pas] = nl_rate
            if cs_rate > ESCAPE_MAX + 1e-12 or nl_rate > NOLABEL_MAX + 1e-12:
                escape_ok = False
        escapes[j] = row
    a["escape_rates"] = escapes
    out["gates"]["adjudication_valid"] = (
        preflight and n_dual >= DUAL_DECISIVE_MIN and escape_ok
        and kap >= KAPPA_MIN - 1e-12)

    # ---- probe-B gate, per judge ---------------------------------------------
    probe_rates, probe_ok = {}, True
    for j, tag in (("judge-pA", "a"), ("judge-pB", "b")):
        n_lab = int(adj["n_probe_labelled_%s" % tag])
        n_fs = int(adj["n_probe_false_sat_%s" % tag])
        rate = (n_fs / n_lab) if n_lab else 1.0  # fail closed
        probe_rates[j] = rate
        if n_lab < PROBE_LABELLED_MIN or rate >= PROBE_FALSE_SAT_BAR - 1e-12:
            probe_ok = False
    a["probe_false_satisfaction_rates"] = probe_rates
    out["gates"]["probe_valid"] = probe_ok

    # ---- the two-sided bracket on necessity and sufficiency ------------------
    for name, conc_k, union_k in (
            ("necessity", "n_necessity_concordant", "n_necessity_union"),
            ("sufficiency", "n_sufficiency_concordant", "n_sufficiency_union")):
        for rule, key in (("concordant", conc_k), ("union", union_k)):
            k = int(adj[key])
            rate = (k / n_dual) if n_dual else 0.0
            lb, ub = wilson_bounds(rate, n_dual)
            a["%s_rate_%s" % (name, rule)] = rate
            a["%s_%s_wilson_lb" % (name, rule)] = lb
            a["%s_%s_wilson_ub" % (name, rule)] = ub
    a["sufficiency_equivalence_survives_proxy"] = (
        a["sufficiency_union_wilson_ub"] <= BAR)
    a["proxy_fail"] = a["necessity_concordant_wilson_lb"] > BAR
    a["proxy_pass"] = a["necessity_union_wilson_ub"] <= BAR

    # ---- reported-only per-judge diagnostics ---------------------------------
    a["per_judge_necessity_rates"] = {
        j: (int(adj["n_necessity_%s" % t]) / n_dual) if n_dual else 0.0
        for j, t in (("judge-pA", "a"), ("judge-pB", "b"))}
    a["per_judge_sufficiency_rates"] = {
        j: (int(adj["n_sufficiency_%s" % t]) / n_dual) if n_dual else 0.0
        for j, t in (("judge-pA", "a"), ("judge-pB", "b"))}
    hist = adj["failing_cid_histogram"]
    a["failing_cid_histogram"] = {str(k): int(v) for k, v in sorted(hist.items())}
    return out


# --------------------------------------------------------------------------
def _rec(n_inst=200, n_dual=200, nec_both=5, nec_a=3, nec_b=4,
         suf_conc=2, suf_union=6, cs=(4, 6, 3, 5), nl=(2, 3, 1, 2),
         probe=(29, 3, 28, 4), nec_j=(8, 9), suf_j=(4, 5),
         hist=None, preflight=True):
    nec_neither = n_dual - nec_both - nec_a - nec_b
    m = {"n_instances": n_inst, "n_dual_decisive": n_dual,
         "n_nec_both": nec_both, "n_nec_neither": nec_neither,
         "n_nec_a_only": nec_a, "n_nec_b_only": nec_b,
         "n_necessity_concordant": nec_both,
         "n_necessity_union": nec_both + nec_a + nec_b,
         "n_sufficiency_concordant": suf_conc,
         "n_sufficiency_union": suf_union,
         "n_cannot_say_a1": cs[0], "n_cannot_say_a2": cs[1],
         "n_cannot_say_b1": cs[2], "n_cannot_say_b2": cs[3],
         "n_nolabel_a1": nl[0], "n_nolabel_a2": nl[1],
         "n_nolabel_b1": nl[2], "n_nolabel_b2": nl[3],
         "n_probe_labelled_a": probe[0], "n_probe_false_sat_a": probe[1],
         "n_probe_labelled_b": probe[2], "n_probe_false_sat_b": probe[3],
         "n_necessity_a": nec_j[0], "n_necessity_b": nec_j[1],
         "n_sufficiency_a": suf_j[0], "n_sufficiency_b": suf_j[1],
         "failing_cid_histogram": hist if hist is not None
         else {"c1": 4, "c3": 9},
         "preflight_pass": preflight, "labels_sha256": "0" * 64}
    return {"config": {"arm": ARM, "rung": "none", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0}, "metrics": m}


def selftest():
    # PASS-analog branch — HAND (the analysis/g3.py fixture constants
    # verbatim): union = 5+3+4 = 12 of 200 -> rate .06, Wilson UB = .09393
    # <= .10 => proxy_pass; concordant 5/200 -> LB .01222 (not > .10).
    # kappa 2x2 (5,188,3,4): po = 193/200 = .965; a_yes = 8/200 = .04;
    # b_yes = 9/200 = .045; pe = .04*.045 + .96*.955 = .9186;
    # kappa = (.965-.9186)/(1-.9186) = .0464/.0814 = .57003 >= .4.
    # escapes max 6/200 = .03 <= .05; probes 3/29 = .1034, 4/28 = .1429 < .30
    out = analyze([_rec()])
    assert out["gates"]["adjudication_valid"] is True
    assert out["gates"]["probe_valid"] is True
    a = out["analysis"]
    assert a["n_dual_decisive"] == 200
    assert abs(a["necessity_rate_union"] - 0.06) < 1e-12
    assert abs(a["necessity_union_wilson_ub"] - 0.09393) < 5e-5
    assert a["proxy_pass"] is True and a["proxy_fail"] is False
    assert abs(a["necessity_concordant_wilson_lb"] - 0.01222) < 5e-5
    assert abs(a["kappa_pair"] - 0.57003) < 5e-5
    assert abs(a["per_judge_necessity_rates"]["judge-pA"] - 0.04) < 1e-12
    assert abs(a["escape_rates"]["judge-pB"]["pass_b_cannot_say"] - 0.025) < 1e-12
    assert a["failing_cid_histogram"] == {"c1": 4, "c3": 9}
    # sufficiency secondary — HAND: union 6/200 -> UB (rate .03) < .10
    assert a["sufficiency_equivalence_survives_proxy"] is True

    # FAIL-analog branch — HAND (g3.py fixture verbatim): concordant 30/200
    # -> rate .15, Wilson LB = .11315 > .10 => proxy_fail. union 45/200 ->
    # rate .225. 2x2 (30, 155, 7, 8): po = .925; a_yes = .185; b_yes = .19;
    # pe = .185*.19 + .815*.81 = .69530; kappa = .22970/.30470 = .75386
    out = analyze([_rec(nec_both=30, nec_a=7, nec_b=8,
                        nec_j=(37, 38), suf_conc=2, suf_union=8)])
    a = out["analysis"]
    assert out["gates"]["adjudication_valid"] is True
    assert abs(a["necessity_concordant_wilson_lb"] - 0.11315) < 5e-5
    assert a["proxy_fail"] is True and a["proxy_pass"] is False
    assert abs(a["necessity_rate_union"] - 0.225) < 1e-12
    assert abs(a["kappa_pair"] - 0.75386) < 5e-5

    # INSTRUMENT branches (each single-cause)
    out = analyze([_rec(n_dual=169, nec_both=4, nec_a=3, nec_b=4)])
    assert out["gates"]["adjudication_valid"] is False   # dual 169 < 170
    out = analyze([_rec(cs=(11, 6, 3, 5))])              # 11/200 = .055 > .05
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(nl=(2, 11, 1, 2))])              # no-label 11 > 10
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(preflight=False)])
    assert out["gates"]["adjudication_valid"] is False
    # kappa floor: 2x2 (1,183,8,8): po = .92; a_yes = .045; b_yes = .045;
    # pe = .045^2 + .955^2 = .914050; kappa = .00595/.085950 = .06923 < .4
    out = analyze([_rec(nec_both=1, nec_a=8, nec_b=8)])
    assert abs(out["analysis"]["kappa_pair"] - 0.06923) < 5e-5
    assert out["gates"]["adjudication_valid"] is False
    # probe: judge-pB 9/30 = .30 exactly => invalid (point rule boundary IN)
    out = analyze([_rec(probe=(29, 3, 30, 9))])
    assert out["gates"]["probe_valid"] is False
    out = analyze([_rec(probe=(26, 0, 28, 4))])          # coverage 26 < 27
    assert out["gates"]["probe_valid"] is False

    # cannot-say boundary IN: 10/200 = .05 exactly is allowed
    out = analyze([_rec(cs=(10, 6, 3, 5))])
    assert out["gates"]["adjudication_valid"] is True

    # missing record => everything unset => INCONCLUSIVE downstream
    out = analyze([])
    assert out == {"gates": {}, "analysis": {}}
    print("g3-llmproxy selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    final = [r for r in records if r.get("phase") == "final"
             and r.get("experiment") == "g3-llmproxy"]
    print(json.dumps(analyze(final), sort_keys=True))
