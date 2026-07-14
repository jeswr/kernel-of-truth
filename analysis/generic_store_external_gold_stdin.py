#!/usr/bin/env python3
"""generic-store-external-gold pinned analysis — STDIN-CONFORMANT from the
start (verdict-gen-compatible; NO argparse-required flags — the CLI-only pin
defect that killed knull/ufo-check-0 registration is not repeated here).

DESIGN: docs/next/design/generic-store-external-gold.md
DRAFT — this file is scaffolding for coordinator review; it is NOT frozen and
NOT pinned in any registry record yet.

THE QUESTION (from the knull dual-model reconcile,
docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md, Divergence 1):
f2b-transfer (PASS, +0.2507) showed the KERNEL store's verify-retry lift
survives BLIND external gold-label-independent adjudication; knull-v2 (NULL,
PASS-GENERIC) showed the store content is generic (plain/opaque matched the
kernel on SELF-AUTHORED membership gold, lifts 0.2477 / 0.2357 vs 0.2397).
Neither frozen record tests whether a PLAIN/OPAQUE (generic, non-kernel)
store's verify-retry lift ALSO survives the SAME blind EXTERNAL gold. This
experiment does. YES (the plain/generic store's external-gold lift clears the
same bar) => content-attribution is fully dead on this line even under
independent gold. NO (it does not) => a real content signal reappears exactly
where knull could not see it.

VERDICT-GEN CONTRACT (tools/registry/verdict-gen.py step 5, confirmed): the
eligible run records (event=="run", phase=="final", exit=="ok", chain-verified,
prereg-hash-matched) are piped as JSONL on STDIN with NO argv; analysis-output
JSON is read from STDOUT. This script reads stdin, filters eligible, and is a
PURE FUNCTION of the eligible set. Every per-cell record carries its own item
vectors in metrics (item_correct_ext / item_correct_mem) — the f2b_transfer.py
pattern — so no separate materialised campaign file or metrics.rows carrying is
required.

TWO STAGES, TWO STORES (all are final-phase run records of THIS id):
  Stage 1 (adjudication instruments, $0 GPU):
    arm="adjudication-instrument-plain"   -> the PRIMARY stage-1 kill (d):
        plain external endorsement A_plain (blind judges endorse the PLAIN
        store's own-gloss slot on the plain-rendered surfaces). Wilson LB
        < 0.70 => FAIL before any GPU (plain content fails blind external
        adjudication => the H-KC route: kernel content is distinctive).
    arm="adjudication-instrument-opaque"  -> REPORTED negative control:
        opaque external endorsement A_opaque. Forecast: near option-chance =>
        opaque_stage1_fail true. This is an INSTRUMENT-VALIDITY datum (external
        gold is not a rubber stamp — it can detect non-content); it does NOT
        enter the verdict rules.
  Stage 2 (GPU, PLAIN store; opaque stage 2 only if opaque survives stage 1 —
    a coordinator decision, not pre-committed here):
    model-alone R1/R3, plain-verify-retry R1 k=4 (THE deflator arm),
    shuffled-plain-verify-retry R1 k=4 (LOAD-BEARING content-vs-structure
    control), plain-gloss-self-verify-retry R1 k=4 (RT-2 commodity control).
    Every cell dual-scored:
      item_correct_ext — against the PLAIN external adjudicated gold
                         (data/d-adj-t-plain; all endpoints)
      item_correct_mem — against plain membership gold (descriptive contrast)

PRIMARY (absolute, no denominator, external gold): effect_size =
  acc_ext(plain-verify, k=4) - acc_ext(R1-alone); reject iff one-sided 95% BCa
  LB > 0 (superiority at margin 0). SESOI Cohen's h = 0.2 (TOST NULL branch).
  This is EXACTLY the f2b-transfer primary bar, now applied to the generic
  store — "does the generic arm's external-gold lift clear the same bar".

THE DEFLATOR (reported, not verdict-bearing — the cross-experiment caveat):
  kernel_content_premium_ext = KERNEL_EXT_LIFT_REF - plain_ext_lift, where
  KERNEL_EXT_LIFT_REF = 0.25066666666666704 is the FROZEN f2b-transfer primary
  (registry/verdicts/f2b-transfer.json). Reported with the plain-arm bootstrap
  CI on plain_ext_lift, plus tost_equiv_to_kernel_ref (|premium| within ±0.05).
  When the primary clears the bar AND the premium straddles 0, the deflation is
  licensed: the NSM kernel adds no external-gold premium over a generic plain
  store. The kernel reference is a fixed constant from a frozen verdict, NOT
  co-resampled — so this is a diagnostic, never a Holm member (the primary +
  shuffled control carry the verdict-bearing deflation).

ENGAGEMENT / EXTRACTION GATES (INSTRUMENT-INVALID on failure, never FAIL/PASS):
  engagement (RT-7a fix, summed over plain-verify cells): decidable_fraction
  >= 0.95, attempt-0 rejection rate in [0.05, 0.95], >= 1 final != attempt-0.
  extraction (knull-style in-run, store-appropriate — the pinned d-xif set is
  kernel-rendered and cannot measure the plain surfaces): pooled Wilson-LB of
  extraction success over the plain-verify verify calls >= 0.90.
  headroom: acc_ext(R1-alone) <= 0.85 (a saturated baseline measures no lift).

Fixture: --selftest (constructed cells; HAND-COMPUTED point values asserted).
"""
import json
import math
import sys
from statistics import NormalDist

SEED = 20260713
B_PRODUCTION = 10000
ALPHA = 0.05
Z_ONE_SIDED = 1.645
ENDORSEMENT_BAR = 0.70       # stage-1 kill (d) on the PLAIN store
JUDGE_AGREE_MIN = 0.80       # adjudication instrument gate (raw two-judge)
UNRESOLVED_MAX = 0.15        # adjudication instrument gate (post-tie-break)
ADJUDICATED_MIN = 300        # adjudication instrument gate (planned 360)
DECIDABLE_MIN = 0.95         # engagement gate (RT-7a fix)
REJECT_RATE_LO = 0.05        # engagement gate: verifier must sometimes reject
REJECT_RATE_HI = 0.95        # ... and sometimes accept
HEADROOM_MAX = 0.85          # acc_ext(R1-alone) above this => no measurable lift
SEPARATION_MIN_EXT = 0.05    # external-gold separation gate (R3 vs R1 alone)
RECOVERY_BAR = 0.30          # carry-over kill clause (b) + secondary bar
TOST_MARGIN_H = 0.2          # P8 §1.5 paired-proportion margin (vs R1-alone)
EXTRACTION_FAIL_BOUND = 0.10 # in-run extraction gate (failure Wilson-LB <= 0.10)
PREMIUM_EQUIV_MARGIN = 0.05  # deflator diagnostic: |premium| within this margin
# FROZEN reference — the f2b-transfer PASS primary (kernel-verify external-gold
# lift over R1-alone), registry/verdicts/f2b-transfer.json endpoint "primary".
KERNEL_EXT_LIFT_REF = 0.25066666666666704
ND = NormalDist()

ARM_ALONE = "model-alone"
ARM_VERIFY = "plain-verify-retry"
ARM_SHUF = "shuffled-plain-verify-retry"
ARM_SELFV = "plain-gloss-self-verify-retry"
ARM_ADJ_PLAIN = "adjudication-instrument-plain"
ARM_ADJ_OPAQUE = "adjudication-instrument-opaque"
RETRY_K = 4                  # the single pre-registered retry budget (no sweep)

OUTPUT_FIELDS = [
    "/gates/adjudication_valid",
    "/gates/extraction_valid",
    "/gates/extraction_wilson_lb",
    "/gates/engagement_valid",
    "/gates/headroom_valid",
    "/gates/separation_valid",
    "/analysis/n_adjudicated",
    "/analysis/n_unresolved_disagreement",
    "/analysis/n_undecided",
    "/analysis/n_ext_labelled",
    "/analysis/judge_pair_agreement",
    "/analysis/external_endorsement",
    "/analysis/external_endorsement_lb",
    "/analysis/stage1_endorsement_fail",
    "/analysis/opaque_external_endorsement",
    "/analysis/opaque_external_endorsement_lb",
    "/analysis/opaque_stage1_fail",
    "/analysis/opaque_adjudication_valid",
    "/analysis/n_eval_items",
    "/analysis/engagement_decidable_fraction",
    "/analysis/engagement_attempt0_reject_rate",
    "/analysis/engagement_final_differs_attempt0",
    "/analysis/acc_ext_alone_r1",
    "/analysis/acc_ext_alone_r3",
    "/analysis/acc_ext_verify_k4",
    "/analysis/acc_ext_shuffled_k4",
    "/analysis/acc_ext_gloss_k4",
    "/analysis/acc_mem_alone_r1",
    "/analysis/acc_mem_verify_k4",
    "/analysis/effect_size",
    "/analysis/effect_ci_low",
    "/analysis/effect_ci_high",
    "/analysis/primary_lower_onesided95",
    "/analysis/primary_reject",
    "/analysis/primary_p",
    "/analysis/delta_vs_r3",
    "/analysis/delta_vs_r3_lower_onesided95",
    "/analysis/separation_gap",
    "/analysis/separation_lower_onesided95",
    "/analysis/lift_mem",
    "/analysis/dual_scoring_gap",
    "/analysis/dual_scoring_gap_ci_low",
    "/analysis/dual_scoring_gap_ci_high",
    "/analysis/transfer_ratio",
    "/analysis/plain_ext_lift",
    "/analysis/kernel_ext_lift_ref",
    "/analysis/kernel_content_premium_ext",
    "/analysis/kernel_content_premium_ci_low",
    "/analysis/kernel_content_premium_ci_high",
    "/analysis/tost_equiv_to_kernel_ref",
    "/analysis/shuffled_recovery_fraction",
    "/analysis/shuffled_recovery_ub95",
    "/analysis/shuffled_recovers_geq_30",
    "/analysis/recovery_defined_fraction",
    "/analysis/competitor_closes_asmuch",
    "/analysis/cost_ratio_vs_R3",
    "/analysis/tost_equivalence_pass",
    "/analysis/seed_sign_consistent",
    "/analysis/holm/beats_gloss_self_verify",
    "/analysis/holm/beats_gloss_self_verify_p",
    "/analysis/holm/shuffled_low_recovery",
    "/analysis/holm/shuffled_low_recovery_p",
    "/analysis/holm/noninferiority_vs_r3",
    "/analysis/holm/noninferiority_vs_r3_p",
]


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
    scoring rule (ext = plain external adjudicated gold; mem = plain membership
    gold), plus flops, the TWO adjudication records (plain primary + opaque
    control), the engagement sums (plain-verify cells) and the in-run
    extraction counters (plain-verify verify calls)."""

    def __init__(self, records):
        ext, mem = {}, {}
        self.flops = {}
        self.adj_plain = None
        self.adj_opaque = None
        self.by_seed_ext = {}
        self.engagement = {"n_items": 0, "n_decidable": 0,
                           "n_attempt0_rejected": 0,
                           "n_final_differs_attempt0": 0, "cells": 0,
                           "cells_with_block": 0}
        self.extraction = {"calls": 0, "failures": 0, "cells": 0,
                           "cells_with_block": 0}
        for r in records:
            cfg, m = r["config"], r["metrics"]
            arm, rung = cfg["arm"], cfg["rung"]
            if arm == ARM_ADJ_PLAIN:
                if self.adj_plain is not None:
                    print("gsx analysis: duplicate plain adjudication record",
                          file=sys.stderr)
                    sys.exit(1)
                self.adj_plain = m
                continue
            if arm == ARM_ADJ_OPAQUE:
                if self.adj_opaque is not None:
                    print("gsx analysis: duplicate opaque adjudication record",
                          file=sys.stderr)
                    sys.exit(1)
                self.adj_opaque = m
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
                self.extraction["cells"] += 1
                if ("n_verify_calls" in m) and ("n_extraction_failures" in m):
                    self.extraction["cells_with_block"] += 1
                    self.extraction["calls"] += int(m["n_verify_calls"])
                    self.extraction["failures"] += int(m["n_extraction_failures"])
        self.items_ext, self.items_mem = {}, {}
        for store, out in ((ext, self.items_ext), (mem, self.items_mem)):
            for key, seed_vecs in store.items():
                n = len(seed_vecs[0])
                if any(len(v) != n for v in seed_vecs):
                    print("gsx analysis: item-vector length mismatch in cell %r"
                          % (key,), file=sys.stderr)
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


def _adj_gates(adj):
    """Adjudication-instrument gate + endorsement statistic from ONE
    adjudication record's metrics (the f2b-transfer stage-1 machinery)."""
    n_adj = int(adj["n_adjudicated"])
    n_unres = int(adj["n_unresolved_disagreement"])
    n_agree = int(adj["n_agree_membership"])
    jp_total = int(adj["judge_pairs_total"])
    jp_conc = int(adj["judge_pairs_concordant"])
    judge_agree = (jp_conc / jp_total) if jp_total else 0.0
    valid = (n_adj >= ADJUDICATED_MIN
             and n_unres <= UNRESOLVED_MAX * n_adj + 1e-12
             and judge_agree >= JUDGE_AGREE_MIN - 1e-12)
    denom = n_adj - n_unres
    A = (n_agree / denom) if denom > 0 else 0.0
    lb = wilson_lb(A, denom)
    return {"n_adjudicated": n_adj, "n_unresolved_disagreement": n_unres,
            "n_undecided": int(adj["n_undecided"]),
            "n_ext_labelled": int(adj["n_ext_labelled"]),
            "judge_pair_agreement": judge_agree, "adjudication_valid": valid,
            "external_endorsement": A, "external_endorsement_lb": lb,
            "stage1_fail": lb < ENDORSEMENT_BAR}


def analyze(records, B=B_PRODUCTION):
    import random
    rng = random.Random(SEED)
    cells = Cells(records)
    out = {"gates": {}, "analysis": {"holm": {}}}
    a = out["analysis"]

    # ---- STAGE 1: plain endorsement (primary kill d) + opaque control -------
    if cells.adj_plain is not None:
        g = _adj_gates(cells.adj_plain)
        a["n_adjudicated"] = g["n_adjudicated"]
        a["n_unresolved_disagreement"] = g["n_unresolved_disagreement"]
        a["n_undecided"] = g["n_undecided"]
        a["n_ext_labelled"] = g["n_ext_labelled"]
        a["judge_pair_agreement"] = g["judge_pair_agreement"]
        out["gates"]["adjudication_valid"] = g["adjudication_valid"]
        a["external_endorsement"] = g["external_endorsement"]
        a["external_endorsement_lb"] = g["external_endorsement_lb"]
        a["stage1_endorsement_fail"] = g["stage1_fail"]
    if cells.adj_opaque is not None:
        go = _adj_gates(cells.adj_opaque)
        # REPORTED negative control only — never in the verdict rules.
        a["opaque_external_endorsement"] = go["external_endorsement"]
        a["opaque_external_endorsement_lb"] = go["external_endorsement_lb"]
        a["opaque_stage1_fail"] = go["stage1_fail"]
        a["opaque_adjudication_valid"] = go["adjudication_valid"]

    # ---- STAGE 2 presence check ---------------------------------------------
    a1 = cells.vec(ARM_ALONE, "R1")
    a3 = cells.vec(ARM_ALONE, "R3")
    v = cells.vec(ARM_VERIFY, k=RETRY_K)
    sh = cells.vec(ARM_SHUF, k=RETRY_K)
    gl = cells.vec(ARM_SELFV, k=RETRY_K)
    if any(x is None for x in (a1, a3, v, sh, gl)):
        return out  # stage-1-only (or missing arms): INCOMPLETE-DATA downstream

    # ---- in-run extraction-failure instrument gate (plain-verify calls) ------
    ex = cells.extraction
    if ex["cells"] and ex["cells_with_block"] == ex["cells"] and ex["calls"]:
        ex_fail_rate = ex["failures"] / ex["calls"]
        ex_success_lb = wilson_lb(1.0 - ex_fail_rate, ex["calls"])
        a_ext_lb = ex_success_lb
        out["gates"]["extraction_valid"] = ex_success_lb >= (1.0 - EXTRACTION_FAIL_BOUND) - 1e-12
    else:
        a_ext_lb = None
        out["gates"]["extraction_valid"] = False
    out["gates"]["extraction_wilson_lb"] = a_ext_lb

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
        delta = accv - acc1                       # PRIMARY (plain external gold)
        d3 = accv - acc3                          # non-inferiority vs R3
        sep = acc3 - acc1                         # external-gold separation
        rec = ((accs - acc1) / delta) if delta > 1e-12 else None
        lift_mem = (acc_of(v_mem, idx) - acc_of(a1_mem, idx))
        premium = KERNEL_EXT_LIFT_REF - delta     # deflator (kernel ref fixed)
        return {"acc1": acc1, "acc3": acc3, "accv": accv, "accs": accs,
                "accg": accg, "delta": delta, "d3": d3, "sep": sep,
                "rec": rec, "lift_mem": lift_mem,
                "dual": lift_mem - delta, "d_gloss": accv - accg,
                "premium": premium}

    pt = stats_for()
    a["acc_ext_alone_r1"] = pt["acc1"]
    a["acc_ext_alone_r3"] = pt["acc3"]
    a["acc_ext_verify_k4"] = pt["accv"]
    a["acc_ext_shuffled_k4"] = pt["accs"]
    a["acc_ext_gloss_k4"] = pt["accg"]
    a["acc_mem_alone_r1"] = acc_of(a1_mem)
    a["acc_mem_verify_k4"] = acc_of(v_mem)
    a["effect_size"] = pt["delta"]
    a["plain_ext_lift"] = pt["delta"]
    a["delta_vs_r3"] = pt["d3"]
    a["separation_gap"] = pt["sep"]
    a["lift_mem"] = pt["lift_mem"]
    a["dual_scoring_gap"] = pt["dual"]
    a["transfer_ratio"] = (pt["delta"] / pt["lift_mem"]
                           if pt["lift_mem"] > 1e-12 else None)
    a["shuffled_recovery_fraction"] = pt["rec"]
    a["kernel_ext_lift_ref"] = KERNEL_EXT_LIFT_REF
    a["kernel_content_premium_ext"] = pt["premium"]

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
            "d_gloss": [], "premium": []}
    rec_invalid = 0
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        s = stats_for(idx)
        boot["delta"].append(s["delta"])
        boot["d3"].append(s["d3"])
        boot["sep"].append(s["sep"])
        boot["dual"].append(s["dual"])
        boot["d_gloss"].append(s["d_gloss"])
        boot["premium"].append(s["premium"])
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

    # ---- PRIMARY: absolute superiority over R1-alone on plain external gold ---
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
            p_rec = 1.0
        a["shuffled_recovers_geq_30"] = pt["rec"] >= RECOVERY_BAR
    else:
        a["shuffled_recovery_ub95"] = None
        p_rec = 1.0
        a["shuffled_recovers_geq_30"] = False

    # ---- dual-scoring contrast (descriptive; never Holm, never verdict) ------
    ds = sorted(boot["dual"])
    a["dual_scoring_gap_ci_low"] = ds[max(0, int(0.025 * len(ds)) - 1)]
    a["dual_scoring_gap_ci_high"] = ds[min(len(ds) - 1, int(0.975 * len(ds)))]

    # ---- THE DEFLATOR: kernel-content premium (descriptive, kernel ref fixed)-
    pm = sorted(boot["premium"])
    a["kernel_content_premium_ci_low"] = pm[max(0, int(0.025 * len(pm)) - 1)]
    a["kernel_content_premium_ci_high"] = pm[min(len(pm) - 1, int(0.975 * len(pm)))]
    # equivalence of the plain lift to the FROZEN kernel lift: |premium| within
    # ±0.05 with both 95% CI ends inside the margin (a TOST on the premium; the
    # kernel ref is a constant so only the plain lift is resampled).
    a["tost_equiv_to_kernel_ref"] = bool(
        a["kernel_content_premium_ci_low"] > -PREMIUM_EQUIV_MARGIN
        and a["kernel_content_premium_ci_high"] < PREMIUM_EQUIV_MARGIN)

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
def _adj(arm, n_adj=360, n_unres=20, n_und=25, n_agree=300, jp=360,
         jp_conc=330, n_lab=315):
    return {"config": {"arm": arm, "rung": "R1", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_adjudicated": n_adj,
                        "n_unresolved_disagreement": n_unres,
                        "n_undecided": n_und, "n_agree_membership": n_agree,
                        "judge_pairs_total": jp,
                        "judge_pairs_concordant": jp_conc,
                        "n_ext_labelled": n_lab,
                        "labels_sha256": "0" * 64}}


def _mk(arm, rung, ext_n, mem_n=None, n=200, k=0, seed=0, flops=1e11,
        eng=None, verify_calls=None, extraction_failures=None):
    m = {"item_correct_ext": [1] * ext_n + [0] * (n - ext_n),
         "item_correct_mem": [1] * (mem_n if mem_n is not None else ext_n)
                             + [0] * (n - (mem_n if mem_n is not None else ext_n)),
         "metric_vector": {"inference_compute": {"flops_per_query": flops}}}
    if eng is not None:
        m["verifier_engagement"] = eng
    if verify_calls is not None:
        m["n_verify_calls"] = verify_calls
        m["n_extraction_failures"] = extraction_failures
    return {"config": {"arm": arm, "rung": rung, "retry_budget": k,
                       "escalation_budget": 0, "seed": seed}, "metrics": m}


ENG_OK = {"n_items": 200, "n_decidable": 198, "n_attempt0_rejected": 90,
          "n_final_differs_attempt0": 60}


def selftest():
    # prefix-structured vectors => hand-computable statistics. Plain arm mirrors
    # the f2b-transfer selftest numbers so the port is provably faithful.
    recs = [
        _adj(ARM_ADJ_PLAIN),                                 # A_plain=300/340
        _adj(ARM_ADJ_OPAQUE, n_agree=110, jp_conc=330),      # A_opaque=110/340
        _mk(ARM_ALONE, "R1", 100),                           # ext 0.5 / mem 0.5
        _mk(ARM_ALONE, "R3", 140, flops=4e11),               # ext 0.7
        _mk(ARM_VERIFY, "R1", 130, mem_n=150, k=4, flops=2e11,
            eng=ENG_OK, verify_calls=600, extraction_failures=18),  # ext .65 / mem .75
        _mk(ARM_SHUF, "R1", 104, k=4, flops=2e11),           # ext 0.52
        _mk(ARM_SELFV, "R1", 110, k=4, flops=2e11),          # ext 0.55
    ]
    out = analyze(recs, B=800)
    a = out["analysis"]
    g = out["gates"]
    # stage 1 (plain) — HAND: A = 300/(360-20)=0.882353; Wilson LB > 0.70
    assert g["adjudication_valid"] is True
    assert abs(a["external_endorsement"] - 300.0 / 340.0) < 1e-12
    assert a["external_endorsement_lb"] > ENDORSEMENT_BAR
    assert a["stage1_endorsement_fail"] is False
    # opaque control — HAND: A = 110/340 = 0.3235; LB < 0.70 => opaque fails
    assert abs(a["opaque_external_endorsement"] - 110.0 / 340.0) < 1e-12
    assert a["opaque_stage1_fail"] is True
    assert a["opaque_adjudication_valid"] is True
    # stage-2 gates
    # extraction: 18/600 fail => success 0.97; Wilson LB (one-sided) > 0.90
    assert g["extraction_valid"] is True
    assert g["extraction_wilson_lb"] > 0.90
    assert g["engagement_valid"] is True      # .99>=.95; .45 in [.05,.95]; 60>=1
    assert g["headroom_valid"] is True        # 0.5 <= 0.85
    assert g["separation_valid"] is True      # sep .2 >= .05, lb > 0
    assert abs(a["separation_gap"] - 0.2) < 1e-12       # HAND: 0.7-0.5
    assert abs(a["effect_size"] - 0.15) < 1e-12         # HAND: 0.65-0.5
    assert abs(a["plain_ext_lift"] - 0.15) < 1e-12
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
    # deflator — HAND: premium = 0.250667 - 0.15 = 0.100667 (kernel > plain here)
    assert abs(a["kernel_content_premium_ext"] - (KERNEL_EXT_LIFT_REF - 0.15)) < 1e-12
    assert a["tost_equiv_to_kernel_ref"] is False        # premium ~0.10 outside ±0.05

    # deflation branch — plain lift == kernel ref => premium ~ 0, equiv true.
    # HAND: build plain-verify at ext 0.750667 so delta ≈ 0.250667 == kernel ref.
    # Use integer prefixes on n=1000 for resolution: alone .500, verify .751.
    defl = [
        _adj(ARM_ADJ_PLAIN),
        _mk(ARM_ALONE, "R1", 500, n=1000),
        _mk(ARM_ALONE, "R3", 700, n=1000, flops=4e11),
        _mk(ARM_VERIFY, "R1", 751, mem_n=760, n=1000, k=4, flops=2e11,
            eng={"n_items": 1000, "n_decidable": 990, "n_attempt0_rejected": 450,
                 "n_final_differs_attempt0": 300},
            verify_calls=3000, extraction_failures=60),
        _mk(ARM_SHUF, "R1", 520, n=1000, k=4, flops=2e11),
        _mk(ARM_SELFV, "R1", 560, n=1000, k=4, flops=2e11),
    ]
    outd = analyze(defl, B=400)
    ad = outd["analysis"]
    # delta = 0.751-0.500 = 0.251; premium = 0.250667-0.251 = -0.000333 ~ 0
    assert abs(ad["kernel_content_premium_ext"] - (KERNEL_EXT_LIFT_REF - 0.251)) < 1e-12
    assert ad["primary_reject"] is True
    assert ad["tost_equiv_to_kernel_ref"] is True        # premium CI within ±0.05

    # stage-1-only branch: adjudication fields resolve, stage-2 fields absent
    out1 = analyze([_adj(ARM_ADJ_PLAIN)], B=100)
    assert out1["gates"]["adjudication_valid"] is True
    assert out1["analysis"]["stage1_endorsement_fail"] is False
    assert "extraction_valid" not in out1["gates"]       # => INCOMPLETE-DATA
    assert "primary_reject" not in out1["analysis"]

    # plain stage-1 kill branch — HAND: A = 200/340 = 0.588, LB < 0.70 => FAIL
    out2 = analyze([_adj(ARM_ADJ_PLAIN, n_agree=200)], B=100)
    assert out2["analysis"]["stage1_endorsement_fail"] is True

    # plain adjudication-instrument-invalid — HAND: 250/360 = 0.694 < 0.80
    out3 = analyze([_adj(ARM_ADJ_PLAIN, jp_conc=250)], B=100)
    assert out3["gates"]["adjudication_valid"] is False

    # engagement-degenerate branch (verifier never rejects => verify == alone):
    eng_vac = {"n_items": 200, "n_decidable": 198, "n_attempt0_rejected": 0,
               "n_final_differs_attempt0": 0}
    recs_vac = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_vac += [_mk(ARM_VERIFY, "R1", 100, k=4, flops=2e11, eng=eng_vac,
                     verify_calls=600, extraction_failures=18)]
    out4 = analyze(recs_vac, B=200)
    assert out4["gates"]["engagement_valid"] is False    # reject rate 0 < .05

    # missing-engagement-block branch: runner defect => gate false
    recs_nb = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_nb += [_mk(ARM_VERIFY, "R1", 130, k=4, flops=2e11,
                    verify_calls=600, extraction_failures=18)]
    out5 = analyze(recs_nb, B=200)
    assert out5["gates"]["engagement_valid"] is False

    # missing-extraction-block branch: gate false (fail closed)
    recs_ne = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_ne += [_mk(ARM_VERIFY, "R1", 130, mem_n=150, k=4, flops=2e11, eng=ENG_OK)]
    out5b = analyze(recs_ne, B=200)
    assert out5b["gates"]["extraction_valid"] is False

    # high-extraction-failure branch: 120/600 = 0.20 fail => gate false
    recs_xf = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    recs_xf += [_mk(ARM_VERIFY, "R1", 130, mem_n=150, k=4, flops=2e11, eng=ENG_OK,
                    verify_calls=600, extraction_failures=120)]
    out5c = analyze(recs_xf, B=200)
    assert out5c["gates"]["extraction_valid"] is False

    # kill-(b) branch: shuffled recovers the whole external-gold lift
    recs_kill = [r for r in recs if r["config"]["arm"] != ARM_SHUF]
    recs_kill += [_mk(ARM_SHUF, "R1", 128, k=4, flops=2e11)]  # rec=.14/.15=0.9333
    out6 = analyze(recs_kill, B=400)
    assert abs(out6["analysis"]["shuffled_recovery_fraction"] - 0.14 / 0.15) < 1e-12
    assert out6["analysis"]["shuffled_recovers_geq_30"] is True
    assert out6["analysis"]["holm"]["shuffled_low_recovery"] is False

    # dead-primary branch: plain-verify == alone on external gold (kill a)
    flat = [r for r in recs if r["config"]["arm"] != ARM_VERIFY]
    flat += [_mk(ARM_VERIFY, "R1", 100, mem_n=150, k=4, flops=2e11, eng=ENG_OK,
                 verify_calls=600, extraction_failures=18)]
    out7 = analyze(flat, B=400)
    a7 = out7["analysis"]
    assert a7["primary_reject"] is False                 # delta = 0
    assert a7["shuffled_recovery_fraction"] is None      # lift <= 0: undefined
    assert a7["shuffled_recovers_geq_30"] is False       # kill (a) owns this case

    # separation-gate-failure branch: R3-alone == R1-alone => R3 secondary leaves
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
    print("generic-store-external-gold selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records, B=B_PRODUCTION), sort_keys=True))
