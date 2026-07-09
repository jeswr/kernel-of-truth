#!/usr/bin/env python3
"""f2b-transfer pinned analysis — ground-truth-independence test of the
verifier-offload lift (registry/experiments/f2b-transfer.json; design note
poc/f2b-transfer/design.md).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; deterministic (PRNG seed 20260710, B=10000 BCa paired
item bootstrap; float64 end-to-end, no pre-rounding — P8 C-7).

WHAT THIS EXPERIMENT SEPARATES (the f2b-replicate residual): on d-qa/d-qa-r
the gold answers were DEFINED by the same string-equality the kernel verifier
checks, so verifier acceptance == gold BY CONSTRUCTION (definitional
circularity). Here every scored item carries an EXTERNAL gold label produced
by blind judges who never see the kernel, membership status, or provenance
(data/d-adj-t; protocol frozen in the design note). Acceptance and gold can
now disagree; whether verify-retry still lifts accuracy against EXTERNAL gold
is exactly the real-content-vs-circularity fork.

TWO-STAGE STRUCTURE (both stages are final-phase run records of THIS id):
  Stage 1 (adjudication instrument, $0 GPU): the arm="adjudication-instrument"
    record carries the blind-adjudication summary. Its gates and the
    external-endorsement statistic are computable from that record ALONE, so
    the stage-1 kill (external_endorsement_lb < 0.70 => FAIL) can fire before
    any GPU spend. Stage-1-passed-but-no-arm-cells yields INCOMPLETE-DATA
    (fields for later rules are left unset — fail closed, never a verdict).
  Stage 2 (GPU arms): model-alone R1/R3, kernel-verify-retry R1 k=4,
    shuffled-kernel-verify-retry R1 k=4 (load-bearing carry-over),
    gloss-self-verify-retry R1 k=4; every cell dual-scored:
      item_correct_ext — against the EXTERNAL adjudicated gold (all endpoints)
      item_correct_mem — against membership gold (descriptive contrast only)

ENGAGEMENT GATE (the RT-7a fix made structural): the F2 external secondary
was vacuous because ext_vector() bypassed the pipeline; the f2b-replicate fix
ran the pipeline but d-ext items are not kernel-checkable, so the verifier
abstained on 100% and the verify/alone external vectors were byte-identical
(MEASURED, results-log/f2b-replicate.jsonl). This analysis therefore refuses
to read the primary unless the verifier demonstrably ENGAGED:
  decidable_fraction >= 0.95, attempt-0 rejection rate in [0.05, 0.95], and
  at least one final answer that differs from attempt 0 — else
  /gates/engagement_valid = false => INSTRUMENT-INVALID, never FAIL/PASS.

Endpoints (absolute style, NO denominators anywhere in the verdict path):
  PRIMARY  effect_size = acc_ext(135M+kernel-verify, fixed pre-registered
           k=4) - acc_ext(135M-alone); reject iff one-sided 95% BCa lower
           bound of the paired difference > 0 (superiority at margin 0).
  Holm family F-secondary(f2b-t), membership pre-declared here:
           beats_gloss_self_verify, shuffled_low_recovery, plus — ONLY when
           the external-gold separation gate holds — noninferiority_vs_r3.
           Conditional membership is itself the pre-declaration; the gate is
           a deterministic function of the alone arms only and is decided
           BEFORE any p-value comparison.
  Dual-scoring contrast (lift_mem - lift_ext), transfer_ratio, seed-sign,
           cost_ratio_vs_R3: reported with CIs, never Holm-tested, never
           verdict-bearing.

Output fields — the frozen record's pins.analysis_script.output_fields.
Missing arms/cells leave fields unresolvable and the verdict INCOMPLETE-DATA
(fail closed at verdict-gen step 7); nothing is imputed.

Fixture: --selftest (constructed cells; HAND-COMPUTED point values in
comments at each assert).
"""
import json
import math
import sys
from statistics import NormalDist

SEED = 20260710
B_PRODUCTION = 10000
ALPHA = 0.05
Z_ONE_SIDED = 1.645
ENDORSEMENT_BAR = 0.70      # stage-1 kill (d): Wilson one-sided 95% LB < 0.70
JUDGE_AGREE_MIN = 0.80      # adjudication instrument gate (raw two-judge)
UNRESOLVED_MAX = 0.15       # adjudication instrument gate (post-tie-break)
ADJUDICATED_MIN = 300       # adjudication instrument gate (planned 360)
DECIDABLE_MIN = 0.95        # engagement gate (RT-7a fix)
REJECT_RATE_LO = 0.05       # engagement gate: verifier must sometimes reject
REJECT_RATE_HI = 0.95       # ... and sometimes accept
HEADROOM_MAX = 0.85         # acc_ext(R1-alone) above this => no measurable lift
SEPARATION_MIN_EXT = 0.05   # external-gold separation gate (R3 vs R1 alone)
RECOVERY_BAR = 0.30         # carry-over kill clause (b) + secondary bar
TOST_MARGIN_H = 0.2         # P8 section 1.5 paired-proportion margin
IFACE_FAIL_BOUND = 0.10     # P10 extraction gate (unchanged from f2b-replicate)
ND = NormalDist()

ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_SHUF = "shuffled-kernel-verify-retry"
ARM_SELFV = "gloss-self-verify-retry"
ARM_IFACE = "extraction-instrument"
ARM_ADJ = "adjudication-instrument"
RETRY_K = 4                 # the single pre-registered retry budget (no sweep)


def wilson_lb(p, n, z=Z_ONE_SIDED):
    if n <= 0:
        return 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def cohens_h(p1, p2):
    clamp = lambda p: min(max(p, 0.0), 1.0)
    return 2 * math.asin(math.sqrt(clamp(p1))) - 2 * math.asin(math.sqrt(clamp(p2)))


class Cells:
    """(arm, rung, k) -> per-item accuracy vectors (mean over seeds), one per
    scoring rule (ext = external adjudicated gold; mem = membership gold),
    plus flops, per-seed ext vectors, the adjudication record and the
    engagement sums for the RT-7a gate."""

    def __init__(self, records):
        ext, mem = {}, {}
        self.flops = {}
        self.iface = {}
        self.adj = None
        self.by_seed_ext = {}
        self.engagement = {"n_items": 0, "n_decidable": 0,
                           "n_attempt0_rejected": 0,
                           "n_final_differs_attempt0": 0, "cells": 0,
                           "cells_with_block": 0}
        for r in records:
            cfg, m = r["config"], r["metrics"]
            arm, rung = cfg["arm"], cfg["rung"]
            if arm == ARM_IFACE:
                s = self.iface.setdefault(rung, {"n": 0, "fail": 0})
                s["n"] += int(m["n_labelled"])
                s["fail"] += int(m["n_extraction_failures"])
                continue
            if arm == ARM_ADJ:
                if self.adj is not None:
                    print("f2b-transfer analysis: duplicate adjudication-"
                          "instrument record", file=sys.stderr)
                    sys.exit(1)
                self.adj = m
                continue
            key = (arm, rung, int(cfg.get("retry_budget", 0) or 0))
            ext.setdefault(key, []).append([int(x) for x in m["item_correct_ext"]])
            mem.setdefault(key, []).append([int(x) for x in m["item_correct_mem"]])
            self.by_seed_ext.setdefault(key, {})[cfg.get("seed", 0)] = [
                int(x) for x in m["item_correct_ext"]]
            fl = m.get("metric_vector", {}).get("inference_compute",
                                                {}).get("flops_per_query")
            if fl is not None:
                self.flops.setdefault(key, []).append(float(fl))
            if arm == ARM_VERIFY:
                self.engagement["cells"] += 1
                eng = m.get("verifier_engagement")
                if eng is not None:
                    self.engagement["cells_with_block"] += 1
                    for f in ("n_items", "n_decidable", "n_attempt0_rejected",
                              "n_final_differs_attempt0"):
                        self.engagement[f] += int(eng[f])
        self.items_ext, self.items_mem = {}, {}
        for store, out in ((ext, self.items_ext), (mem, self.items_mem)):
            for key, seed_vecs in store.items():
                n = len(seed_vecs[0])
                if any(len(v) != n for v in seed_vecs):
                    print("f2b-transfer analysis: item-vector length mismatch "
                          "in cell %r" % (key,), file=sys.stderr)
                    sys.exit(1)
                out[key] = [sum(v[i] for v in seed_vecs) / len(seed_vecs)
                            for i in range(n)]

    def vec(self, arm, rung="R1", k=0, scoring="ext"):
        store = self.items_ext if scoring == "ext" else self.items_mem
        return store.get((arm, rung, k))

    def mean_flops(self, arm, rung="R1", k=0):
        v = self.flops.get((arm, rung, k))
        return sum(v) / len(v) if v else None


def acc_of(vec, idx=None):
    if idx is None:
        return sum(vec) / len(vec)
    return sum(vec[i] for i in idx) / len(idx)


def bca_bounds(theta_hat, thetas, jack, levels):
    """BCa bounds at the given lower-tail levels (item jackknife)."""
    if not thetas:
        return [None] * len(levels)
    b = len(thetas)
    below = sum(1 for t in thetas if t < theta_hat)
    z0 = ND.inv_cdf(min(max(below / b, 1.0 / (b + 1)), b / (b + 1.0)))
    jack = [j for j in jack if j is not None]
    if len(jack) >= 2:
        jbar = sum(jack) / len(jack)
        num = sum((jbar - j) ** 3 for j in jack)
        den = 6.0 * (sum((jbar - j) ** 2 for j in jack) ** 1.5)
        a = 0.0 if den == 0 else num / den
    else:
        a = 0.0
    out = []
    srt = sorted(thetas)
    for lv in levels:
        z = ND.inv_cdf(lv)
        adj = ND.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        pos = min(max(int(adj * b), 0), b - 1)
        out.append(srt[pos])
    return out


def one_sided_p(boot, null=0.0):
    """Bootstrap one-sided p: share of resampled statistics <= the null."""
    b = len(boot)
    if b == 0:
        return 1.0
    return (1 + sum(1 for d in boot if d <= null)) / (b + 1)


def holm(pvals, alpha=ALPHA):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    reject = [False] * len(pvals)
    m = len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            reject[i] = True
        else:
            break
    return reject


def analyze(records, B=B_PRODUCTION):
    import random
    rng = random.Random(SEED)
    cells = Cells(records)
    out = {"gates": {}, "analysis": {"holm": {}}}
    a = out["analysis"]

    # ---- STAGE 1: adjudication instrument + external-endorsement kill -------
    # Computable from the adjudication-instrument record ALONE, so the frozen
    # verdict rules 1-2 can fire before any GPU spend. No adjudication record
    # => these fields stay unset => INCOMPLETE-DATA (fail closed).
    if cells.adj is not None:
        adj = cells.adj
        n_adj = int(adj["n_adjudicated"])
        n_unres = int(adj["n_unresolved_disagreement"])
        n_agree = int(adj["n_agree_membership"])
        jp_total = int(adj["judge_pairs_total"])
        jp_conc = int(adj["judge_pairs_concordant"])
        a["n_adjudicated"] = n_adj
        a["n_unresolved_disagreement"] = n_unres
        a["n_undecided"] = int(adj["n_undecided"])
        a["n_ext_labelled"] = int(adj["n_ext_labelled"])
        judge_agree = (jp_conc / jp_total) if jp_total else 0.0
        a["judge_pair_agreement"] = judge_agree
        out["gates"]["adjudication_valid"] = (
            n_adj >= ADJUDICATED_MIN
            and n_unres <= UNRESOLVED_MAX * n_adj + 1e-12
            and judge_agree >= JUDGE_AGREE_MIN - 1e-12)
        # Endorsement A: agreement between blind external gold and membership
        # gold over every RESOLVED adjudication; concordant "cannot-say" counts
        # as NON-agreement (a judge who cannot endorse the kernel's content is
        # evidence, not an instrument event). Unresolved judge disagreements
        # (quality events, capped by the gate above) leave the denominator.
        denom = n_adj - n_unres
        A = (n_agree / denom) if denom > 0 else 0.0
        a["external_endorsement"] = A
        a["external_endorsement_lb"] = wilson_lb(A, denom)
        a["stage1_endorsement_fail"] = a["external_endorsement_lb"] < ENDORSEMENT_BAR

    # ---- STAGE 2 presence check ---------------------------------------------
    a1 = cells.vec(ARM_ALONE, "R1")
    a3 = cells.vec(ARM_ALONE, "R3")
    v = cells.vec(ARM_VERIFY, k=RETRY_K)
    sh = cells.vec(ARM_SHUF, k=RETRY_K)
    gl = cells.vec(ARM_SELFV, k=RETRY_K)
    if any(x is None for x in (a1, a3, v, sh, gl)):
        return out  # stage-1-only (or missing arms): INCOMPLETE-DATA downstream

    # ---- P10 extraction-failure instrument gate (verifier host rung R1) -----
    st = cells.iface.get("R1")
    out["gates"]["instrument_valid"] = bool(
        st and st["n"] >= 300
        and wilson_lb(st["fail"] / st["n"], st["n"]) <= IFACE_FAIL_BOUND)

    # ---- engagement gate (RT-7a fix made structural) -------------------------
    eng = cells.engagement
    if eng["cells"] and eng["cells_with_block"] == eng["cells"] and eng["n_items"]:
        dec_frac = eng["n_decidable"] / eng["n_items"]
        rej_rate = eng["n_attempt0_rejected"] / eng["n_items"]
        a["engagement_decidable_fraction"] = dec_frac
        a["engagement_attempt0_reject_rate"] = rej_rate
        a["engagement_final_differs_attempt0"] = eng["n_final_differs_attempt0"]
        out["gates"]["engagement_valid"] = (
            dec_frac >= DECIDABLE_MIN - 1e-12
            and REJECT_RATE_LO - 1e-12 <= rej_rate <= REJECT_RATE_HI + 1e-12
            and eng["n_final_differs_attempt0"] >= 1)
    else:
        # a verify cell without its engagement block is a runner defect:
        # the gate exists precisely so this can never silently read as data
        a["engagement_decidable_fraction"] = None
        a["engagement_attempt0_reject_rate"] = None
        a["engagement_final_differs_attempt0"] = None
        out["gates"]["engagement_valid"] = False

    n = len(a1)
    a["n_eval_items"] = n
    v_mem = cells.vec(ARM_VERIFY, k=RETRY_K, scoring="mem")
    a1_mem = cells.vec(ARM_ALONE, "R1", scoring="mem")

    def stats_for(idx=None):
        acc1 = acc_of(a1, idx)
        acc3 = acc_of(a3, idx)
        accv = acc_of(v, idx)
        accs = acc_of(sh, idx)
        accg = acc_of(gl, idx)
        delta = accv - acc1                       # PRIMARY (external gold)
        d3 = accv - acc3                          # non-inferiority vs R3
        sep = acc3 - acc1                         # external-gold separation
        rec = ((accs - acc1) / delta) if delta > 1e-12 else None
        lift_mem = (acc_of(v_mem, idx) - acc_of(a1_mem, idx))
        return {"acc1": acc1, "acc3": acc3, "accv": accv, "accs": accs,
                "accg": accg, "delta": delta, "d3": d3, "sep": sep,
                "rec": rec, "lift_mem": lift_mem,
                "dual": lift_mem - delta, "d_gloss": accv - accg}

    pt = stats_for()
    a["acc_ext_alone_r1"] = pt["acc1"]
    a["acc_ext_alone_r3"] = pt["acc3"]
    a["acc_ext_verify_k4"] = pt["accv"]
    a["acc_ext_shuffled_k4"] = pt["accs"]
    a["acc_ext_gloss_k4"] = pt["accg"]
    a["acc_mem_alone_r1"] = acc_of(a1_mem)
    a["acc_mem_verify_k4"] = acc_of(v_mem)
    a["effect_size"] = pt["delta"]
    a["delta_vs_r3"] = pt["d3"]
    a["separation_gap"] = pt["sep"]
    a["lift_mem"] = pt["lift_mem"]
    a["dual_scoring_gap"] = pt["dual"]
    a["transfer_ratio"] = (pt["delta"] / pt["lift_mem"]
                           if pt["lift_mem"] > 1e-12 else None)
    a["shuffled_recovery_fraction"] = pt["rec"]

    # ---- headroom gate (external gold) ---------------------------------------
    out["gates"]["headroom_valid"] = pt["acc1"] <= HEADROOM_MAX + 1e-12

    # ---- kill clause (c) point machinery: commodity verification -------------
    v_flops = cells.mean_flops(ARM_VERIFY, k=RETRY_K)
    g_flops = cells.mean_flops(ARM_SELFV, k=RETRY_K)
    lift_v = pt["accv"] - pt["acc1"]
    lift_g = pt["accg"] - pt["acc1"]
    a["competitor_closes_asmuch"] = bool(
        lift_g >= lift_v - 1e-12
        and (g_flops is not None and v_flops is not None
             and g_flops <= v_flops * (1 + 1e-9)))
    S_flops = cells.mean_flops(ARM_ALONE, "R3")
    a["cost_ratio_vs_R3"] = (v_flops / S_flops
                             if (v_flops is not None and S_flops) else None)

    # ---- paired item bootstrap ------------------------------------------------
    boot = {"delta": [], "d3": [], "sep": [], "rec": [], "dual": [],
            "d_gloss": []}
    rec_invalid = 0
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        s = stats_for(idx)
        boot["delta"].append(s["delta"])
        boot["d3"].append(s["d3"])
        boot["sep"].append(s["sep"])
        boot["dual"].append(s["dual"])
        boot["d_gloss"].append(s["d_gloss"])
        if s["rec"] is not None:
            boot["rec"].append(s["rec"])
        else:
            rec_invalid += 1
    a["recovery_defined_fraction"] = (B - rec_invalid) / B if B else None

    # ---- item jackknife for BCa acceleration ----------------------------------
    jack = {"delta": [], "d3": [], "sep": [], "rec": []}
    idx_all = list(range(n))
    for i in range(n):
        idx = idx_all[:i] + idx_all[i + 1:]
        s = stats_for(idx)
        jack["delta"].append(s["delta"])
        jack["d3"].append(s["d3"])
        jack["sep"].append(s["sep"])
        jack["rec"].append(s["rec"])

    # ---- external-gold separation gate (instrument; pre-declared) -------------
    (sep_lb,) = bca_bounds(pt["sep"], boot["sep"], jack["sep"], [ALPHA])
    a["separation_lower_onesided95"] = sep_lb
    sep_valid = (pt["sep"] >= SEPARATION_MIN_EXT - 1e-12
                 and sep_lb is not None and sep_lb > 0.0)
    out["gates"]["separation_valid"] = sep_valid

    # ---- PRIMARY: absolute superiority over R1-alone on external gold --------
    d_lo95, d_lo, d_hi95 = bca_bounds(pt["delta"], boot["delta"], jack["delta"],
                                      [0.025, ALPHA, 0.975])
    a["effect_ci_low"], a["effect_ci_high"] = d_lo95, d_hi95
    a["primary_lower_onesided95"] = d_lo
    a["primary_reject"] = (d_lo is not None) and (d_lo > 0.0)
    a["primary_p"] = one_sided_p(boot["delta"], 0.0)

    # ---- non-inferiority vs R3-alone on external gold (conditional Holm) -----
    (d3_lo,) = bca_bounds(pt["d3"], boot["d3"], jack["d3"], [ALPHA])
    a["delta_vs_r3_lower_onesided95"] = d3_lo
    p_d3 = one_sided_p(boot["d3"], 0.0)

    # ---- shuffled-recovery secondary + carry-over kill (b) --------------------
    if pt["rec"] is not None and boot["rec"]:
        (r_ub,) = bca_bounds(pt["rec"], boot["rec"], jack["rec"], [1 - ALPHA])
        a["shuffled_recovery_ub95"] = r_ub
        br = len(boot["rec"])
        p_rec = (1 + sum(1 for r in boot["rec"] if r >= RECOVERY_BAR)) / (br + 1)
        rec_established = (a["recovery_defined_fraction"] is not None
                           and a["recovery_defined_fraction"] >= 0.5)
        if not rec_established:
            p_rec = 1.0  # cannot claim low recovery when the ratio rarely exists
        a["shuffled_recovers_geq_30"] = pt["rec"] >= RECOVERY_BAR
    else:
        a["shuffled_recovery_ub95"] = None
        p_rec = 1.0
        # no measurable lift => nothing for the shuffled arm to "recover";
        # kill (a) owns the dead-primary case
        a["shuffled_recovers_geq_30"] = False

    # ---- dual-scoring contrast (descriptive; never Holm, never verdict) ------
    ds = sorted(boot["dual"])
    a["dual_scoring_gap_ci_low"] = ds[max(0, int(0.025 * len(ds)) - 1)]
    a["dual_scoring_gap_ci_high"] = ds[min(len(ds) - 1, int(0.975 * len(ds)))]

    # ---- ONE Holm family (pre-declared conditional membership) ---------------
    sec = [("beats_gloss_self_verify", one_sided_p(boot["d_gloss"])),
           ("shuffled_low_recovery", p_rec)]
    if sep_valid:
        sec.append(("noninferiority_vs_r3", p_d3))
    rejects = holm([p for _, p in sec])
    for (name, p), rej in zip(sec, rejects):
        a["holm"][name] = bool(rej)
        a["holm"][name + "_p"] = p
    if "noninferiority_vs_r3" not in a["holm"]:
        # gate-invalid: the secondary is INSTRUMENT-INVALID (excluded from
        # Holm before any p comparison), reported as non-reject
        a["holm"]["noninferiority_vs_r3"] = False
        a["holm"]["noninferiority_vs_r3_p"] = p_d3

    # ---- TOST equivalence vs R1-alone at margin h=0.2 (NULL branch) ----------
    hs = []
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        hs.append(cohens_h(acc_of(v, idx), acc_of(a1, idx)))
    hs.sort()
    lo = hs[max(0, int(0.05 * len(hs)) - 1)]
    hi = hs[min(len(hs) - 1, int(0.95 * len(hs)))]
    a["tost_equivalence_pass"] = -TOST_MARGIN_H < lo and hi < TOST_MARGIN_H

    # ---- seed robustness (C-4: >= ceil(0.8*n_seeds) same-direction lift) -----
    v_seeds = cells.by_seed_ext.get((ARM_VERIFY, "R1", RETRY_K), {})
    a_seeds = cells.by_seed_ext.get((ARM_ALONE, "R1", 0), {})
    common = sorted(set(v_seeds) & set(a_seeds))
    if common:
        pos = sum(1 for s in common if acc_of(v_seeds[s]) > acc_of(a_seeds[s]))
        a["seed_sign_consistent"] = pos >= math.ceil(0.8 * len(common))
    else:
        a["seed_sign_consistent"] = False
    return out


# --------------------------------------------------------------------------
def _adj(n_adj=360, n_unres=20, n_und=25, n_agree=300, jp=360, jp_conc=330,
         n_lab=315, n_eval=250):
    return {"config": {"arm": ARM_ADJ, "rung": "R1", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_adjudicated": n_adj,
                        "n_unresolved_disagreement": n_unres,
                        "n_undecided": n_und, "n_agree_membership": n_agree,
                        "judge_pairs_total": jp,
                        "judge_pairs_concordant": jp_conc,
                        "n_ext_labelled": n_lab, "n_eval_items": n_eval,
                        "labels_sha256": "0" * 64}}


def _mk(arm, rung, ext_n, mem_n=None, n=200, k=0, seed=0, flops=1e11,
        eng=None):
    m = {"item_correct_ext": [1] * ext_n + [0] * (n - ext_n),
         "item_correct_mem": [1] * (mem_n if mem_n is not None else ext_n)
                             + [0] * (n - (mem_n if mem_n is not None else ext_n)),
         "metric_vector": {"inference_compute": {"flops_per_query": flops}}}
    if eng is not None:
        m["verifier_engagement"] = eng
    return {"config": {"arm": arm, "rung": rung, "retry_budget": k,
                       "escalation_budget": 0, "seed": seed}, "metrics": m}


def _iface(rung="R1", n=300, fails=15):
    return {"config": {"arm": ARM_IFACE, "rung": rung, "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_labelled": n, "n_extraction_failures": fails}}


ENG_OK = {"n_items": 200, "n_decidable": 198, "n_attempt0_rejected": 90,
          "n_final_differs_attempt0": 60}


def selftest():
    # prefix-structured vectors => hand-computable statistics
    recs = [
        _adj(),                                             # A = 300/340
        _mk(ARM_ALONE, "R1", 100),                          # ext 0.5 / mem 0.5
        _mk(ARM_ALONE, "R3", 140, flops=4e11),              # ext 0.7
        _mk(ARM_VERIFY, "R1", 130, mem_n=150, k=4,
            flops=2e11, eng=ENG_OK),                        # ext 0.65 / mem 0.75
        _mk(ARM_SHUF, "R1", 104, k=4, flops=2e11),          # ext 0.52
        _mk(ARM_SELFV, "R1", 110, k=4, flops=2e11),         # ext 0.55
        _iface(),                                           # 15/300 lb .0326<=.1
    ]
    out = analyze(recs, B=800)
    a = out["analysis"]
    g = out["gates"]
    # stage 1 — HAND: A = 300/(360-20) = 0.882353; Wilson LB > 0.70
    assert g["adjudication_valid"] is True    # 360>=300; 20<=54; 330/360=.9167>=.8
    assert abs(a["external_endorsement"] - 300.0 / 340.0) < 1e-12
    assert a["external_endorsement_lb"] > ENDORSEMENT_BAR
    assert a["stage1_endorsement_fail"] is False
    # stage 2 gates
    assert g["instrument_valid"] is True
    assert g["engagement_valid"] is True      # .99>= .95; .45 in [.05,.95]; 60>=1
    assert g["headroom_valid"] is True        # 0.5 <= 0.85
    assert g["separation_valid"] is True      # sep .2 >= .05, lb > 0
    assert abs(a["separation_gap"] - 0.2) < 1e-12       # HAND: 0.7-0.5
    assert abs(a["effect_size"] - 0.15) < 1e-12         # HAND: 0.65-0.5
    assert a["primary_reject"] is True and a["primary_p"] < 0.05
    assert abs(a["delta_vs_r3"] - (-0.05)) < 1e-12      # HAND: 0.65-0.7
    assert a["holm"]["noninferiority_vs_r3"] is False   # d3 < 0 cannot reject
    assert abs(a["lift_mem"] - 0.25) < 1e-12            # HAND: 0.75-0.5
    assert abs(a["dual_scoring_gap"] - 0.10) < 1e-12    # HAND: 0.25-0.15
    assert abs(a["transfer_ratio"] - 0.6) < 1e-12       # HAND: 0.15/0.25
    assert abs(a["shuffled_recovery_fraction"] - 0.02 / 0.15) < 1e-12
    assert a["shuffled_recovers_geq_30"] is False       # HAND: 0.1333 < 0.30
    assert a["holm"]["shuffled_low_recovery"] is True
    assert a["holm"]["beats_gloss_self_verify"] is True  # 0.65 vs 0.55, paired
    assert a["competitor_closes_asmuch"] is False        # gloss lift .05 < .15
    assert abs(a["cost_ratio_vs_R3"] - 0.5) < 1e-12      # HAND: 2e11/4e11
    assert a["tost_equivalence_pass"] is False           # h(.65,.5) ~ .305 > .2
    assert a["seed_sign_consistent"] is True

    # stage-1-only branch: adjudication fields resolve, stage-2 fields absent
    out1 = analyze([_adj()], B=100)
    assert out1["gates"]["adjudication_valid"] is True
    assert out1["analysis"]["stage1_endorsement_fail"] is False
    assert "instrument_valid" not in out1["gates"]       # => INCOMPLETE-DATA
    assert "primary_reject" not in out1["analysis"]

    # stage-1 kill branch — HAND: A = 200/340 = 0.588, LB < 0.70 => FAIL fires
    out2 = analyze([_adj(n_agree=200)], B=100)
    assert out2["analysis"]["stage1_endorsement_fail"] is True

    # adjudication-instrument-invalid branch — HAND: 250/360 = 0.694 < 0.80
    out3 = analyze([_adj(jp_conc=250)], B=100)
    assert out3["gates"]["adjudication_valid"] is False

    # engagement-degenerate branch (the F2/f2b-replicate vacuity signature:
    # verifier never rejects => verify == alone byte-identical): gate must
    # fail as INSTRUMENT-INVALID, never read as a hypothesis outcome
    eng_vac = {"n_items": 200, "n_decidable": 198, "n_attempt0_rejected": 0,
               "n_final_differs_attempt0": 0}
    recs_vac = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_vac += [_mk(ARM_VERIFY, "R1", 100, k=4, flops=2e11, eng=eng_vac)]
    out4 = analyze(recs_vac, B=200)
    assert out4["gates"]["engagement_valid"] is False    # reject rate 0 < .05

    # missing-engagement-block branch: runner defect => gate false
    recs_nb = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_nb += [_mk(ARM_VERIFY, "R1", 130, k=4, flops=2e11)]
    out5 = analyze(recs_nb, B=200)
    assert out5["gates"]["engagement_valid"] is False

    # kill-(b) branch: shuffled recovers the whole external-gold lift
    recs_kill = [r for r in recs if r["config"]["arm"] != ARM_SHUF]
    recs_kill += [_mk(ARM_SHUF, "R1", 128, k=4, flops=2e11)]  # rec=.14/.15=0.9333
    out6 = analyze(recs_kill, B=400)
    assert abs(out6["analysis"]["shuffled_recovery_fraction"] - 0.14 / 0.15) < 1e-12
    assert out6["analysis"]["shuffled_recovers_geq_30"] is True
    assert out6["analysis"]["holm"]["shuffled_low_recovery"] is False

    # dead-primary branch: verify == alone on external gold
    flat = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    flat += [_mk(ARM_VERIFY, "R1", 100, mem_n=150, k=4, flops=2e11, eng=ENG_OK)]
    out7 = analyze(flat, B=400)
    a7 = out7["analysis"]
    assert a7["primary_reject"] is False                 # delta = 0
    assert a7["shuffled_recovery_fraction"] is None      # lift <= 0: undefined
    assert a7["shuffled_recovers_geq_30"] is False       # kill (a) owns this case
    assert a7["holm"]["shuffled_low_recovery"] is False

    # separation-gate-failure branch: R3-alone == R1-alone on external gold =>
    # the non-inferiority secondary leaves the Holm family; primary still reads
    nosep = [r for r in recs if not (r["config"]["arm"] == ARM_ALONE
                                     and r["config"]["rung"] == "R3")]
    nosep += [_mk(ARM_ALONE, "R3", 100, flops=4e11)]
    out8 = analyze(nosep, B=400)
    a8 = out8["analysis"]
    assert out8["gates"]["separation_valid"] is False
    assert a8["holm"]["noninferiority_vs_r3"] is False
    assert a8["primary_reject"] is True                  # delta = 0.15 unaffected

    # headroom branch: saturated R1-alone => INSTRUMENT-INVALID, not a verdict
    sat = [r for r in recs if not (r["config"]["arm"] == ARM_ALONE
                                   and r["config"]["rung"] == "R1")]
    sat += [_mk(ARM_ALONE, "R1", 180)]                   # acc_ext .9 > .85
    out9 = analyze(sat, B=200)
    assert out9["gates"]["headroom_valid"] is False
    print("f2b-transfer selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records, B=B_PRODUCTION), sort_keys=True))
