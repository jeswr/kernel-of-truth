#!/usr/bin/env python3
"""ontg2v2.py -- pinned analysis for ONT-TYPE-G2/1-v2 (registry g2-import-v2).

Pure function: stdin JSON {"metrics": {...}} -> stdout JSON
{"gates": {...}, "analysis": {...}}. No file IO, no RNG, no clock.
Fork of the audited analysis/ontg2.py (sha 5cca4b5c...) implementing
docs/next/design/g2-import-v2-repair.md sections 4-6 on top of
docs/next/design/ontology-import-plan.md sections 7.3-7.8:

  primary gate   : a3_yes >= 34 on the fixed 84-slot denominator
                   (strict improvement over the frozen A0 baseline
                   33/84; point-estimate engineering gate; plan 7.5)
  PILOT gate     : Stage P (design sections 4 + 11, kappa-paradox
                   redesign 2026-07-12): hedge-calibration 12/12 across
                   judges AND pilot Gwet AC1_A3 >= 0.65 over the
                   both-decisive pair table of the 40 pinned stratified
                   real A3 items (Cohen kappa, PABAK, raw table, p_pos/
                   p_neg specific agreement and the marginal-matched
                   independence-ceiling AC1 all co-reported, never gate
                   substitutes; kappa is NEVER gated -- at the measured
                   v2 operating prevalence pi ~ 0.83 it collapses for
                   accurate judges with independent errors, design 11.1)
                   AND decisive >= 36/40 per judge AND pilot hedge-flip
                   false-satisfaction <= 0.25 per judge (2/8 on the
                   doubled 8-probe pilot block). ANY failure
                   => pilot_valid false => instrument_valid false
                   (INSTRUMENT-INVALID, pilot channel; never FAIL/PASS)
  instrument     : pilot_valid AND Gwet AC1 >= 0.65 per arm (kappa
                   co-reported only, design 11.3) AND each judge
                   decisive on >= 90% of real items per arm (RT-4 at
                   n=84) AND deranged-probe false-sat <= 0.30 per judge
                   per arm AND hedge-flip probe false-sat <= 0.30 per
                   judge per hedged arm (A2, A3) AND pins ok; the
                   prevalence-FREE known-answer channels (calibration +
                   deranged + hedge-flip probes) are load-bearing
                   instrument evidence on an equal footing with AC1
                   (design 11.3: at high prevalence ANY pair-agreement
                   coefficient discriminates weakly)
  separation     : sep_A3 := (a3_yes >= a1_yes) AND (a3_r3_yes >=
                   a1_r3_yes + 5); sep_A2 analogous (design section 5);
                   verdict wiring: go_combined := primary_pass AND
                   sep_a3_pass; go_bfo_sumo_only := a2_pass AND
                   sep_a2_pass AND NOT go_combined; breadth_confound :=
                   (primary_pass OR a2_pass) AND NOT (go_combined OR
                   go_bfo_sumo_only)  [FAIL as NO-GO-BREADTH-CONFOUND];
                   no_go := NOT (primary_pass OR a2_pass)
  informativeness: >= 67/84 A3 non-vacuous AND >= 34/42 R3 non-vacuous
                   AND zero hard operational laws emitted (plan 7.6)
  reporting      : Wilson 95%, exact McNemar vs A0 AND A3-vs-A1
                   (overall + R3 slice), raw agreement tables per arm,
                   pilot block, R1/R3/R4 slices, pair brackets -- all
                   REPORTED, never verdict-bearing (plan 7.5).

Vacuity-zeroing is applied UPSTREAM (assemble); AC1/kappa/PABAK are
computed on RAW judge labels over both-decisive pairs (instrument
stability, not scoring); kappa: pe == 1 implies po == 1 and kappa :=
1.0 (v1 convention kept, co-reported only); AC1: pe_gamma = 2*pi*(1-pi)
<= 0.5 so the denominator is never 0 for n > 0 (Gwet 2008; design
11.2). PILOT-ONLY mode (metrics.pilot_only
true) is accepted ONLY when the pilot gate fails: it emits the full
declared field set with null full-run fields and instrument_valid
false, so the frozen verdict_rules fire INSTRUMENT-INVALID on rule 0.
Every mathematical choice cites its anchor. Fail closed on any missing
metric (ERR_ONTG2V2_METRIC).
"""
import json
import math
import sys

BASELINE_YES = 33          # frozen g2 primary readout (plan section 7.5)
N_ITEMS = 84
GATE_YES = 34              # strict improvement gate: >= 34/84
# AC1_MIN (design section 11.3, kappa-paradox redesign 2026-07-12):
# Gwet AC1 >= 0.65 per arm and at the pilot. Justification quadrangle:
# (i) above the marginal-matched independence-ceiling AC1 at the
# MEASURED v2 operating marginals (0.587 at pA 35/40, pB 31/40) -- any
# threshold <= 0.60 is passable by independent judges >= 46% of the
# time at n=40; (ii) strictly tighter than the retired kappa gate's own
# carried-over stringency (kappa >= 0.40 at the v1 A3 marginals <=> po
# >= 0.7299 <=> AC1 = 0.51); (iii) between measured-broken v1 A3
# (0.417 at n=84; 0.529 on the matched 40) and measured-healthy
# unhedged A1 (0.744); (iv) at the pilot marginals it demands raw
# agreement >= 31/40 -- strictly beating the item-matched v1 subset
# (30/40): the repair must repair. kappa is co-reported, never gated.
AC1_MIN = 0.65
DECISIVE_MIN = 0.90    # RT-4 powered at n=84 (Wilson LB 0.936 at rate 0.98)
FALSE_SAT_MAX = 0.30       # deranged AND hedge-flip families (section 3b)
NONVAC_MIN = 67            # plan section 7.6 informativeness guard
NONVAC_R3_MIN = 34
SEP_R3_MARGIN = 5          # design section 5: half the v1-measured +10 edge
PILOT_N = 40               # design section 4 (review-repaired: 40, not 20)
PILOT_CAL_MIN = 12         # 6 hedge-calibration items x 2 judges
PILOT_AC1_MIN = AC1_MIN    # the prevalence-robust gate at the operating point
PILOT_DECISIVE_MIN = 36    # 0.90 of 40, per judge
PILOT_HF_FS_MAX = 0.25     # <= 2/8 hedge-flip false-sat per judge (design 11.4)

ARMS = ("a1", "a2", "a3")
HEDGED_ARMS = ("a2", "a3")

RIDER = (
    "PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; "
    "point-estimate engineering gate, not statistical superiority; "
    "soft non-binding typing only -- never hard laws; no feasibility "
    "conclusion")

FULL_NULL_FIELDS = None    # filled by _declared_analysis_fields()


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
    """Cohen's kappa from a 2x2 yes/no table -- CO-REPORTED ONLY, never
    gated (design section 11: at the measured v2 operating prevalence
    pi ~ 0.83, kappa collapses toward 0 for accurate judges with
    independent errors -- the Feinstein-Cicchetti prevalence paradox).
    Identical to the audited v1 implementation (comparability, design
    section 6): pe == 1 is reachable only with po == 1 -> kappa := 1.0."""
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


def agree_stats(t):
    """Prevalence-robust agreement panel from a 2x2 yes/no pair table
    (design section 11.2, kappa-paradox redesign 2026-07-12). Returns
    {ac1, pabak, p_pos, p_neg, ac1_indep} or None on an empty table.
      ac1       Gwet's AC1 (Gwet 2008): pe_gamma = 2*pi*(1-pi) with pi
                the mean yes-marginal; pe_gamma <= 0.5, so the
                denominator is never 0 for n > 0 -- no degenerate case.
                THE GATED QUANTITY (AC1_MIN).
      pabak     Brennan-Prediger / PABAK = 2*po - 1 (uniform-chance
                correction; prevalence-free rescaled raw agreement).
      p_pos     positive specific agreement 2a/(2a+b+c)
      p_neg     negative specific agreement 2d/(2d+b+c) (None if the
                denominator is 0) -- the Cicchetti-Feinstein companion
                pair; p_neg is where the v2 pilot's residual
                disagreement concentrates (design 11.1).
      ac1_indep the marginal-matched INDEPENDENCE CEILING: the AC1 an
                independent judge pair with these exact marginals
                attains in expectation. Mandatory disclosure next to
                every gated AC1 (design 11.3)."""
    a, d = t["both_yes"], t["both_no"]
    b, c = t["a_yes_b_no"], t["a_no_b_yes"]
    n = a + b + c + d
    if n == 0:
        return None
    po = (a + d) / n
    pa_yes = (a + b) / n
    pb_yes = (a + c) / n
    pi = (pa_yes + pb_yes) / 2.0
    pe_g = 2.0 * pi * (1.0 - pi)
    po_ind = pa_yes * pb_yes + (1 - pa_yes) * (1 - pb_yes)
    return {"ac1": (po - pe_g) / (1.0 - pe_g),
            "pabak": 2.0 * po - 1.0,
            "p_pos": (2.0 * a / (2 * a + b + c)) if (2 * a + b + c) else None,
            "p_neg": (2.0 * d / (2 * d + b + c)) if (2 * d + b + c) else None,
            "ac1_indep": (po_ind - pe_g) / (1.0 - pe_g)}


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
        sys.stderr.write("ERR_ONTG2V2_METRIC: missing %r\n" % key)
        sys.exit(2)
    return m[key]


def _fs(pr):
    """Probe false-satisfaction, fail-closed on zero labelled probes."""
    return (pr["n_false_sat"] / pr["n_labelled"] if pr["n_labelled"] else 1.0)


def pilot_block(m):
    """The Stage-P pilot block (design sections 4 + 11, kappa-paradox
    redesign): prevalence-robust Gwet AC1 gate at the operating point;
    kappa/PABAK/p_pos/p_neg/independence-ceiling AC1 and the agreement
    table co-reported, never gate substitutes."""
    p = need(m, "pilot")
    if need(p, "n_items") != PILOT_N:
        sys.stderr.write("ERR_ONTG2V2_METRIC: pilot n_items != %d\n" % PILOT_N)
        sys.exit(2)
    t = need(p, "table")
    k = kappa(t)
    g = agree_stats(t)
    cal = need(p, "cal_correct")
    dec_min = min(need(p, "decisive_pA"), need(p, "decisive_pB"))
    hf_max = max(_fs(need(p, "hedgeflip_pA")), _fs(need(p, "hedgeflip_pB")))
    valid = (cal >= PILOT_CAL_MIN
             and g is not None and g["ac1"] >= PILOT_AC1_MIN
             and dec_min >= PILOT_DECISIVE_MIN
             and hf_max <= PILOT_HF_FS_MAX)
    fields = {
        "pilot_n_items": PILOT_N,
        "pilot_ac1_a3": g["ac1"] if g else None,
        "pilot_pabak_a3": g["pabak"] if g else None,
        "pilot_p_pos": g["p_pos"] if g else None,
        "pilot_p_neg": g["p_neg"] if g else None,
        "pilot_ac1_indep": g["ac1_indep"] if g else None,
        "pilot_kappa_a3": k,
        "pilot_agreement": t["both_yes"] + t["both_no"],
        "pilot_both_yes": t["both_yes"],
        "pilot_both_no": t["both_no"],
        "pilot_a_yes_b_no": t["a_yes_b_no"],
        "pilot_a_no_b_yes": t["a_no_b_yes"],
        "pilot_cal_correct": cal,
        "pilot_decisive_min": dec_min,
        "pilot_hedgeflip_false_sat_max": hf_max,
    }
    return valid, fields


def run(metrics):
    m = metrics
    if need(m, "n_items") != N_ITEMS:
        sys.stderr.write("ERR_ONTG2V2_METRIC: n_items != 84\n")
        sys.exit(2)
    if need(m, "baseline_yes") != BASELINE_YES:
        sys.stderr.write("ERR_ONTG2V2_METRIC: baseline_yes != 33 (frozen A0)\n")
        sys.exit(2)

    pilot_valid, pfields = pilot_block(m)

    if m.get("pilot_only"):
        # Accepted ONLY on a failed pilot: the record's designed early stop
        # (design section 4). A passed pilot with no full-run metrics is an
        # incomplete run, never analysable (fail closed).
        if pilot_valid:
            sys.stderr.write("ERR_ONTG2V2_METRIC: pilot_only with a PASSING "
                             "pilot gate -- incomplete full run, refusing\n")
            sys.exit(2)
        analysis = {f: None for f in FULL_NULL_FIELDS}
        analysis.update({"n_items": N_ITEMS, "baseline_yes": BASELINE_YES,
                         "baseline_precision": BASELINE_YES / N_ITEMS,
                         "rider": RIDER})
        analysis.update(pfields)
        return {"gates": {"pilot_valid": False,
                          "instrument_valid": False,
                          "informative_valid": False},
                "analysis": analysis}

    analysis = {"n_items": N_ITEMS, "baseline_yes": BASELINE_YES,
                "baseline_precision": BASELINE_YES / N_ITEMS}
    analysis.update(pfields)
    ac1s, decisives, false_sats, hf_sats = {}, [], [], []
    for arm in ARMS:
        a = need(m, arm)
        ys = need(a, "yes_pA_scored")
        analysis["%s_yes" % arm] = ys
        analysis["%s_yes_pB" % arm] = need(a, "yes_pB_scored")
        analysis["%s_precision" % arm] = ys / N_ITEMS
        lo, hi = wilson(ys, N_ITEMS)
        analysis["%s_wilson_lb" % arm] = lo
        analysis["%s_wilson_ub" % arm] = hi
        t = need(a, "agreement_raw")
        g = agree_stats(t)
        ac1s[arm] = g["ac1"] if g else None
        analysis["ac1_%s" % arm] = g["ac1"] if g else None
        analysis["pabak_%s" % arm] = g["pabak"] if g else None
        analysis["p_pos_%s" % arm] = g["p_pos"] if g else None
        analysis["p_neg_%s" % arm] = g["p_neg"] if g else None
        analysis["ac1_indep_%s" % arm] = g["ac1_indep"] if g else None
        # kappa CO-REPORTED for cross-record continuity with g2/g2-import;
        # never gated (design section 11: prevalence paradox)
        analysis["kappa_%s" % arm] = kappa(t)
        # raw agreement co-reported so no coefficient ever floats free of
        # its base rates (design sections 6 + 11)
        analysis["agreement_raw_%s" % arm] = t["both_yes"] + t["both_no"]
        for pk in ("pA", "pB"):
            decisives.append(need(a, "decisive_%s" % pk) / N_ITEMS)
            false_sats.append(_fs(need(a, "probe_%s" % pk)))
            if arm in HEDGED_ARMS:
                hf_sats.append(_fs(need(a, "hedgeflip_%s" % pk)))
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
    # paired A3-vs-A1 (overall + R3 slice) -- co-reported, never
    # verdict-bearing (design section 5)
    for tag in ("a3_vs_a1", "a3_vs_a1_r3"):
        b = need(m, "mcnemar_%s_b" % tag)
        c = need(m, "mcnemar_%s_c" % tag)
        analysis["mcnemar_%s_b" % tag] = b
        analysis["mcnemar_%s_c" % tag] = c
        analysis["mcnemar_%s_p" % tag] = mcnemar_exact(b, c)

    analysis["decisive_min_fraction"] = min(decisives)
    analysis["probe_false_sat_max"] = max(false_sats)
    analysis["hedgeflip_false_sat_max"] = max(hf_sats)
    analysis["forbidden_effects_ok"] = bool(need(m, "forbidden_effects_ok"))

    instrument_valid = (
        bool(need(m, "pins_ok"))
        and pilot_valid
        and all(g is not None and g >= AC1_MIN for g in ac1s.values())
        and min(decisives) >= DECISIVE_MIN
        and max(false_sats) <= FALSE_SAT_MAX
        and max(hf_sats) <= FALSE_SAT_MAX)
    informative_valid = (
        analysis["a3_nonvacuous"] >= NONVAC_MIN
        and analysis["a3_nonvacuous_r3"] >= NONVAC_R3_MIN
        and analysis["forbidden_effects_ok"])

    primary_pass = analysis["a3_yes"] >= GATE_YES
    a2_pass = analysis["a2_yes"] >= GATE_YES
    sep_a3 = (analysis["a3_yes"] >= analysis["a1_yes"]
              and analysis["a3_r3_yes"] >= analysis["a1_r3_yes"]
              + SEP_R3_MARGIN)
    sep_a2 = (analysis["a2_yes"] >= analysis["a1_yes"]
              and analysis["a2_r3_yes"] >= analysis["a1_r3_yes"]
              + SEP_R3_MARGIN)
    analysis["primary_pass"] = primary_pass
    analysis["a2_pass"] = a2_pass
    analysis["sep_a3_pass"] = sep_a3
    analysis["sep_a2_pass"] = sep_a2
    analysis["go_combined"] = primary_pass and sep_a3
    analysis["go_bfo_sumo_only"] = (a2_pass and sep_a2
                                    and not analysis["go_combined"])
    analysis["no_go"] = not (primary_pass or a2_pass)
    # NO-GO-BREADTH-CONFOUND (design section 5): a 34/84-clearing arm whose
    # separation gate fails -- FAIL, source-specific shard not licensed.
    analysis["breadth_confound"] = ((primary_pass or a2_pass)
                                    and not (analysis["go_combined"]
                                             or analysis["go_bfo_sumo_only"]))
    # A1 can never authorize adoption (plan section 7.2) -- reported only:
    analysis["a1_pass_reported_only"] = analysis["a1_yes"] >= GATE_YES
    analysis["rider"] = RIDER
    return {"gates": {"pilot_valid": pilot_valid,
                      "instrument_valid": instrument_valid,
                      "informative_valid": informative_valid},
            "analysis": analysis}


def _declared_analysis_fields():
    """Every /analysis/* field of the full-run document (the record's
    pins.analysis_script.output_fields, minus the three /gates/*). Used to
    null-fill the PILOT-ONLY document so the field set is byte-stable."""
    out = ["n_items", "baseline_yes", "baseline_precision",
           "decisive_min_fraction", "probe_false_sat_max",
           "hedgeflip_false_sat_max", "forbidden_effects_ok",
           "delta_a2", "delta_a3", "primary_pass", "a2_pass",
           "sep_a3_pass", "sep_a2_pass", "go_combined", "go_bfo_sumo_only",
           "no_go", "breadth_confound", "a1_pass_reported_only", "rider",
           "pilot_n_items", "pilot_ac1_a3", "pilot_pabak_a3", "pilot_p_pos",
           "pilot_p_neg", "pilot_ac1_indep", "pilot_kappa_a3",
           "pilot_agreement",
           "pilot_both_yes", "pilot_both_no", "pilot_a_yes_b_no",
           "pilot_a_no_b_yes", "pilot_cal_correct", "pilot_decisive_min",
           "pilot_hedgeflip_false_sat_max"]
    for arm in ARMS:
        out += ["%s_yes" % arm, "%s_yes_pB" % arm, "%s_precision" % arm,
                "%s_wilson_lb" % arm, "%s_wilson_ub" % arm,
                "ac1_%s" % arm, "pabak_%s" % arm, "p_pos_%s" % arm,
                "p_neg_%s" % arm, "ac1_indep_%s" % arm,
                "kappa_%s" % arm, "agreement_raw_%s" % arm,
                "%s_nonvacuous" % arm, "%s_nonvacuous_r3" % arm,
                "%s_pair_union_yes" % arm, "%s_pair_concordant_yes" % arm,
                "%s_r1_yes" % arm, "%s_r3_yes" % arm, "%s_r4_yes" % arm]
    for tag in ("a2", "a3", "a3_vs_a1", "a3_vs_a1_r3"):
        out += ["mcnemar_%s_b" % tag, "mcnemar_%s_c" % tag,
                "mcnemar_%s_p" % tag]
    return sorted(set(out))


FULL_NULL_FIELDS = _declared_analysis_fields()


def _mock_pilot(ac1_good=True, cal=12, dec=(40, 40), hf=(0, 0)):
    if ac1_good:
        # AC1 0.8165 (and kappa 0.7059 co-reported)
        t = {"both_yes": 24, "both_no": 12, "a_yes_b_no": 2, "a_no_b_yes": 2}
    else:
        # AC1 -0.2244 (anti-correlated pair; kappa -0.2913)
        t = {"both_yes": 12, "both_no": 2, "a_yes_b_no": 14,
             "a_no_b_yes": 12}
    return {"n_items": 40, "cal_correct": cal, "table": t,
            "decisive_pA": dec[0], "decisive_pB": dec[1],
            "hedgeflip_pA": {"n_labelled": 8, "n_false_sat": hf[0]},
            "hedgeflip_pB": {"n_labelled": 8, "n_false_sat": hf[1]}}


def _mock_metrics(a3_yes=54, a2_yes=45, a1_yes=27, a1_r3=10, a2_r3=20,
                  a3_r3=25, pilot=None):
    def arm(y, r3, hedged):
        d = {"yes_pA_scored": y, "yes_pB_scored": max(0, y - 3),
             "agreement_raw": {"both_yes": y, "both_no": 84 - y - 4,
                               "a_yes_b_no": 3, "a_no_b_yes": 1},
             "decisive_pA": 84, "decisive_pB": 83,
             "probe_pA": {"n_labelled": 20, "n_false_sat": 1},
             "probe_pB": {"n_labelled": 20, "n_false_sat": 2},
             "nonvacuous": 83, "nonvacuous_r3": 42,
             "pair_union_yes": y + 4, "pair_concordant_yes": y - 2,
             "r1_yes": 4, "r3_yes": r3, "r4_yes": y - r3 - 4}
        if hedged:
            d["hedgeflip_pA"] = {"n_labelled": 10, "n_false_sat": 1}
            d["hedgeflip_pB"] = {"n_labelled": 10, "n_false_sat": 2}
        return d
    return {"n_items": 84, "baseline_yes": 33, "pins_ok": True,
            "forbidden_effects_ok": True,
            "pilot": pilot or _mock_pilot(),
            "a1": arm(a1_yes, a1_r3, False), "a2": arm(a2_yes, a2_r3, True),
            "a3": arm(a3_yes, a3_r3, True),
            "mcnemar_a2_b": 6, "mcnemar_a2_c": 8,
            "mcnemar_a3_b": 5, "mcnemar_a3_c": 12,
            "mcnemar_a3_vs_a1_b": 4, "mcnemar_a3_vs_a1_c": 9,
            "mcnemar_a3_vs_a1_r3_b": 2, "mcnemar_a3_vs_a1_r3_c": 8}


def selftest():
    # GO path: primary + separation both clear
    out = run(_mock_metrics())
    a = out["analysis"]
    assert out["gates"]["pilot_valid"] is True
    assert out["gates"]["instrument_valid"] is True
    assert out["gates"]["informative_valid"] is True
    assert a["primary_pass"] and a["sep_a3_pass"] and a["go_combined"]
    assert not a["breadth_confound"] and not a["no_go"]
    assert abs(a["delta_a3"] - 21 / 84) < 1e-12
    assert a["a3_wilson_lb"] < 54 / 84 < a["a3_wilson_ub"]
    good_t = {"both_yes": 24, "both_no": 12, "a_yes_b_no": 2,
              "a_no_b_yes": 2}
    assert abs(a["pilot_kappa_a3"] - kappa(good_t)) < 1e-12
    assert abs(a["pilot_ac1_a3"] - agree_stats(good_t)["ac1"]) < 1e-12
    assert a["pilot_ac1_a3"] >= 0.65 and a["pilot_agreement"] == 36
    assert a["pilot_ac1_indep"] < a["pilot_ac1_a3"]
    # NO-GO path
    out2 = run(_mock_metrics(a3_yes=25, a2_yes=20, a3_r3=10, a2_r3=8))
    assert out2["analysis"]["no_go"] is True
    assert not out2["analysis"]["breadth_confound"]
    # BREADTH-CONFOUND path: a3 clears 34 but a1 matches it (sep fails)
    out3 = run(_mock_metrics(a3_yes=50, a2_yes=25, a1_yes=57, a1_r3=22,
                             a3_r3=21, a2_r3=8))
    a3d = out3["analysis"]
    assert a3d["primary_pass"] and not a3d["sep_a3_pass"]
    assert a3d["breadth_confound"] is True and not a3d["no_go"]
    assert not a3d["go_combined"] and not a3d["go_bfo_sumo_only"]
    # GO-BFO-SUMO fallback: a3 fails 34, a2 clears with separation
    out4 = run(_mock_metrics(a3_yes=30, a2_yes=45, a3_r3=12))
    assert out4["analysis"]["go_bfo_sumo_only"] is True
    # PILOT FAIL: AC1 collapse => instrument_valid false
    out5 = run(_mock_metrics(pilot=_mock_pilot(ac1_good=False)))
    assert out5["gates"]["pilot_valid"] is False
    assert out5["gates"]["instrument_valid"] is False
    # PILOT-ONLY document (the designed early stop)
    out6 = run({"n_items": 84, "baseline_yes": 33, "pilot_only": True,
                "pilot": _mock_pilot(ac1_good=False)})
    assert out6["gates"]["instrument_valid"] is False
    assert out6["analysis"]["a3_yes"] is None
    assert out6["analysis"]["pilot_ac1_a3"] is not None
    assert out6["analysis"]["pilot_kappa_a3"] is not None
    # pilot gate breaks on each channel independently
    for bad in (_mock_pilot(cal=11), _mock_pilot(dec=(35, 40)),
                _mock_pilot(hf=(3, 0))):
        assert run(_mock_metrics(pilot=bad))["gates"]["pilot_valid"] is False
    # hedge-flip 2/8 = 0.25 passes exactly at the bound
    assert run(_mock_metrics(
        pilot=_mock_pilot(hf=(2, 0))))["gates"]["pilot_valid"] is True
    # hedge-flip full-run channel breaks instrument
    mm = _mock_metrics()
    mm["a3"]["hedgeflip_pA"] = {"n_labelled": 10, "n_false_sat": 4}
    assert run(mm)["gates"]["instrument_valid"] is False
    # AC1 full-run channel breaks instrument: the 2026-07-12 exploratory
    # pilot shape scaled to n=84 (po 0.702 at pi 0.827 -> AC1 0.583 < 0.65
    # while kappa would read -0.02: the exact paradox operating point)
    mm2 = _mock_metrics()
    mm2["a3"]["agreement_raw"] = {"both_yes": 57, "both_no": 2,
                                  "a_yes_b_no": 17, "a_no_b_yes": 8}
    out7 = run(mm2)
    assert out7["gates"]["instrument_valid"] is False
    assert out7["analysis"]["ac1_a3"] < 0.65
    # McNemar + kappa sanity (v1-identical implementations)
    assert mcnemar_exact(5, 5) > 0.99
    assert mcnemar_exact(0, 15) < 0.001
    assert kappa({"both_yes": 40, "both_no": 44,
                  "a_yes_b_no": 0, "a_no_b_yes": 0}) == 1.0
    # agreement-panel sanity against the measured tables (design 11.1-11.2):
    # v2 exploratory pilot (27,1,8,4): kappa -0.0213 vs AC1 0.5782 -- and the
    # pair sits BELOW its own independence ceiling 0.5873 (the honest read)
    g = agree_stats({"both_yes": 27, "both_no": 1,
                     "a_yes_b_no": 8, "a_no_b_yes": 4})
    assert abs(g["ac1"] - 0.5782) < 5e-4 and abs(g["pabak"] - 0.40) < 1e-12
    assert abs(g["ac1_indep"] - 0.5873) < 5e-4 and g["ac1"] < g["ac1_indep"]
    assert abs(kappa({"both_yes": 27, "both_no": 1, "a_yes_b_no": 8,
                      "a_no_b_yes": 4}) - (-0.0213)) < 5e-4
    # v1 A3 84-item table (42,15,16,11): AC1 0.4173, p_neg 0.5263
    g2 = agree_stats({"both_yes": 42, "both_no": 15,
                      "a_yes_b_no": 16, "a_no_b_yes": 11})
    assert abs(g2["ac1"] - 0.4173) < 5e-4 and abs(g2["p_neg"] - 0.5263) < 5e-4
    print("ontg2v2 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    payload = json.load(sys.stdin)
    print(json.dumps(run(payload["metrics"]), indent=1, sort_keys=True))
