#!/usr/bin/env python3
"""f2b-replicate pinned analysis — fresh-item replication of the F2
verifier-offload signal with oracle-structure controls (architecture-advisor
frozen design; registry/experiments/f2b-replicate.json).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; deterministic (PRNG seed 20260709, B=10000 BCa paired
item bootstrap; float64 end-to-end, no pre-rounding — P8 C-7).

WHAT CHANGED vs analysis/f2.py AND WHY (each change closes a named F2 failure):
  1. PRIMARY HAS NO DENOMINATOR (fixes the degenerate-ratio failure that
     killed F2): one-sided absolute non-inferiority at margin 0 —
     acc(135M + kernel-verify, best k in {1,2,4} reselected inside EVERY
     resample) >= acc(1.7B-alone); reject iff the one-sided 95% BCa lower
     bound of the paired accuracy difference is >= 0.
  2. SEPARATION GATE (instrument, pre-declared): acc(R3-alone) −
     acc(R1-alone) >= 0.10 (5-seed mean) AND one-sided 95% lower CI > 0,
     else the RATIO secondaries are INSTRUMENT-INVALID (dropped from the
     Holm family; the absolute primary still reads).
  3. SHUFFLED-VERIFY CONTROL (load-bearing): recovery = (acc_shuffled −
     acc_alone) / (acc_verify − acc_alone), each arm's best k reselected
     in-resample. Secondary passes iff the one-sided 95% upper bound of
     recovery < 0.30; KILL (advisor clause b) fires iff the point estimate
     >= 0.30 — then the lift is retry-against-any-oracle STRUCTURE, not
     kernel CONTENT, and the kernel-specific claim dies at any accuracy.
  4. GOLD-ORACLE CEILING (diagnostic, reported not killed, NON-DEPLOYABLE):
     acc(gold-oracle-retry, best k) − acc(verify, best k) with a percentile
     CI; never contributes to any verdict.

Estimand family (P8 sections 1.2/1.7 discipline): accuracies are mean
per-item kernel-covered accuracy (seed-averaged item vectors); best retry
budget k in {1,2,4} selected on accuracy (tie -> smaller k) INSIDE every
bootstrap resample and every jackknife replicate, so selection uncertainty
is inside every CI.

Holm family F-secondary(f2b) — ONE family, membership pre-declared here:
  beats_text_null, beats_gloss_self_verify, prm_beaten,
  shuffled_low_recovery, and — ONLY when the separation gate holds —
  gap_r1r3_gt_half, gap_r1r3_gt_one. Conditional membership is itself the
  pre-declaration; a failed gate removes the two ratio members BEFORE any
  p-value is compared (it can never be decided post hoc: the gate is a
  deterministic function of the alone-arm cells only).

Output fields — the frozen record's pins.analysis_script.output_fields.
Missing arms/cells make fields unresolvable and the verdict INCOMPLETE-DATA
(fail closed at verdict-gen step 7); nothing is imputed.

Fixture: --selftest (constructed cells; HAND-COMPUTED point values in
comments at each assert).
"""
import json
import math
import sys
from statistics import NormalDist

SEED = 20260709
B_PRODUCTION = 10000
ALPHA = 0.05
Z_ONE_SIDED = 1.645
SEPARATION_MIN = 0.10       # pre-declared separation gate
RECOVERY_BAR = 0.30         # advisor kill clause (b) + secondary bar
GAP_BAR_HALF = 0.5
GAP_BAR_ONE = 1.0
TOST_MARGIN_H = 0.2         # P8 section 1.5 paired-proportion margin
IFACE_FAIL_BOUND = 0.10     # P10 extraction gate
ND = NormalDist()

ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_SHUF = "shuffled-kernel-verify-retry"
ARM_SELFV = "gloss-self-verify-retry"
ARM_PRM = "prm-verifier"
ARM_TEXT = "kernel-as-text"
ARM_GOLD = "gold-oracle-retry"
ARM_IFACE = "extraction-instrument"
RETRY_KS = (1, 2, 4)


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
    """(arm, rung, k) -> per-item accuracy vector (mean over seeds) + flops."""

    def __init__(self, records):
        acc = {}
        self.flops = {}
        self.iface = {}
        self.by_seed = {}
        for r in records:
            cfg, m = r["config"], r["metrics"]
            arm, rung = cfg["arm"], cfg["rung"]
            if arm == ARM_IFACE:
                s = self.iface.setdefault(rung, {"n": 0, "fail": 0})
                s["n"] += int(m["n_labelled"])
                s["fail"] += int(m["n_extraction_failures"])
                continue
            key = (arm, rung, int(cfg.get("retry_budget", 0) or 0))
            acc.setdefault(key, []).append([int(x) for x in m["item_correct"]])
            self.by_seed.setdefault(key, {})[cfg.get("seed", 0)] = [
                int(x) for x in m["item_correct"]]
            fl = m.get("metric_vector", {}).get("inference_compute",
                                                {}).get("flops_per_query")
            if fl is not None:
                self.flops.setdefault(key, []).append(float(fl))
        self.items = {}
        for key, seed_vecs in acc.items():
            n = len(seed_vecs[0])
            if any(len(v) != n for v in seed_vecs):
                print("f2b-analysis: item-vector length mismatch in cell %r"
                      % (key,), file=sys.stderr)
                sys.exit(1)
            self.items[key] = [sum(v[i] for v in seed_vecs) / len(seed_vecs)
                               for i in range(n)]

    def vec(self, arm, rung="R1", k=0):
        return self.items.get((arm, rung, k))

    def mean_flops(self, arm, rung="R1", k=0):
        v = self.flops.get((arm, rung, k))
        return sum(v) / len(v) if v else None


def acc_of(vec, idx=None):
    if idx is None:
        return sum(vec) / len(vec)
    return sum(vec[i] for i in idx) / len(idx)


def best_k_acc(cells, arm, idx=None):
    """Accuracy-max retry-budget selection, tie -> smaller k (fewer FLOPs)."""
    best, best_acc = None, -1.0
    for k in RETRY_KS:
        v = cells.vec(arm, k=k)
        if v is None:
            continue
        a = acc_of(v, idx)
        if a > best_acc + 1e-15:
            best, best_acc = k, a
    return best, best_acc


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

    # --- P10 extraction-failure instrument gate (verifier host rungs) --------
    verify_rungs = {rung for (arm, rung, _k) in cells.items if arm == ARM_VERIFY}
    iface_ok = bool(verify_rungs)
    for rung in verify_rungs:
        st = cells.iface.get(rung)
        if not st or st["n"] < 300:
            iface_ok = False
            break
        if wilson_lb(st["fail"] / st["n"], st["n"]) > IFACE_FAIL_BOUND:
            iface_ok = False
            break
    out["gates"]["instrument_valid"] = iface_ok

    a1_vec = cells.vec(ARM_ALONE, "R1")
    a3_vec = cells.vec(ARM_ALONE, "R3")
    k_point, _ = best_k_acc(cells, ARM_VERIFY)
    if a1_vec is None or a3_vec is None or k_point is None:
        return out  # unresolvable pointers => INCOMPLETE-DATA downstream

    n = len(a1_vec)
    a["n_items"] = n

    def stats_for(idx=None):
        """All point statistics on an index multiset (None = full sample).
        Best-k reselected here — i.e. inside every resample/jackknife."""
        acc1 = acc_of(a1_vec, idx)
        acc3 = acc_of(a3_vec, idx)
        _kv, accv = best_k_acc(cells, ARM_VERIFY, idx)
        _ks, accs = best_k_acc(cells, ARM_SHUF, idx)
        _kg, accg = best_k_acc(cells, ARM_SELFV, idx)
        _ko, acco = best_k_acc(cells, ARM_GOLD, idx)
        sep = acc3 - acc1
        delta = accv - acc3
        gap = ((accv - acc1) / sep) if abs(sep) > 1e-12 else None
        lift = accv - acc1
        rec = ((accs - acc1) / lift) if (accs >= 0 and lift > 1e-12) else None
        return {"acc1": acc1, "acc3": acc3, "accv": accv, "accs": accs,
                "accg": accg, "acco": acco, "sep": sep, "delta": delta,
                "gap": gap, "rec": rec}

    pt = stats_for()
    a["acc_alone_r1"] = pt["acc1"]
    a["acc_alone_r3"] = pt["acc3"]
    a["acc_verify_bestk"] = pt["accv"]
    a["acc_shuffled_bestk"] = pt["accs"] if pt["accs"] >= 0 else None
    a["acc_gloss_self_verify_bestk"] = pt["accg"] if pt["accg"] >= 0 else None
    a["gold_oracle_acc_bestk"] = pt["acco"] if pt["acco"] >= 0 else None
    a["best_retry_budget"] = k_point
    a["separation_gap"] = pt["sep"]
    a["effect_size"] = pt["delta"]           # PRIMARY: acc_verify - acc_R3alone
    a["gap_closed_fraction_r1r3"] = pt["gap"]
    a["shuffled_recovery_fraction"] = pt["rec"]
    prm_vec = cells.vec(ARM_PRM)
    text_vec = cells.vec(ARM_TEXT)
    a["acc_prm"] = acc_of(prm_vec) if prm_vec is not None else None
    a["acc_text_null"] = acc_of(text_vec) if text_vec is not None else None

    # kill clause (c) point machinery (advisor): does gloss-self-verify or the
    # PRM close as much lift at <= matched FLOPs? (F0 ledger, point estimates;
    # the text null is included as the weakest competitor for completeness)
    v_flops = cells.mean_flops(ARM_VERIFY, k=k_point)
    lift_v = pt["accv"] - pt["acc1"]
    closes = False
    kg_point, _ = best_k_acc(cells, ARM_SELFV)
    for arm, kk in ((ARM_SELFV, kg_point or 0), (ARM_PRM, 0), (ARM_TEXT, 0)):
        vec = cells.vec(arm, k=kk)
        if vec is None:
            continue
        lift_c = acc_of(vec) - pt["acc1"]
        fl_c = cells.mean_flops(arm, k=kk)
        if lift_c >= lift_v - 1e-12 and (fl_c is not None and v_flops is not None
                                         and fl_c <= v_flops * (1 + 1e-9)):
            closes = True
    a["competitor_closes_asmuch"] = closes

    S_flops = cells.mean_flops(ARM_ALONE, "R3")
    a["cost_ratio_vs_R3"] = (v_flops / S_flops
                             if (v_flops is not None and S_flops) else None)

    # --- paired item bootstrap (best-k reselected inside every resample) -----
    boot = {"sep": [], "delta": [], "gap": [], "rec": [], "gold_gap": [],
            "d_text": [], "d_gloss": [], "d_prm": []}
    rec_invalid = 0
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        s = stats_for(idx)
        boot["sep"].append(s["sep"])
        boot["delta"].append(s["delta"])
        if s["gap"] is not None:
            boot["gap"].append(s["gap"])
        if s["rec"] is not None:
            boot["rec"].append(s["rec"])
        else:
            rec_invalid += 1
        if s["acco"] >= 0:
            boot["gold_gap"].append(s["acco"] - s["accv"])
        if text_vec is not None:
            boot["d_text"].append(s["accv"] - acc_of(text_vec, idx))
        if s["accg"] >= 0:
            boot["d_gloss"].append(s["accv"] - s["accg"])
        if prm_vec is not None:
            boot["d_prm"].append(s["accv"] - acc_of(prm_vec, idx))
    a["recovery_defined_fraction"] = (B - rec_invalid) / B if B else None

    # --- item jackknife for BCa acceleration ---------------------------------
    jack = {"sep": [], "delta": [], "gap": [], "rec": []}
    idx_all = list(range(n))
    for i in range(n):
        idx = idx_all[:i] + idx_all[i + 1:]
        s = stats_for(idx)
        jack["sep"].append(s["sep"])
        jack["delta"].append(s["delta"])
        jack["gap"].append(s["gap"])
        jack["rec"].append(s["rec"])

    # --- separation gate (instrument; pre-declared) --------------------------
    (sep_lb,) = bca_bounds(pt["sep"], boot["sep"], jack["sep"], [ALPHA])
    a["separation_lower_onesided95"] = sep_lb
    sep_valid = (pt["sep"] >= SEPARATION_MIN - 1e-12
                 and sep_lb is not None and sep_lb > 0.0)
    out["gates"]["separation_valid"] = sep_valid
    a["ratio_secondaries_valid"] = sep_valid

    # --- PRIMARY: absolute non-inferiority at margin 0 -----------------------
    d_lo95, d_lo, d_hi, d_hi95 = bca_bounds(pt["delta"], boot["delta"],
                                            jack["delta"],
                                            [0.025, ALPHA, 1 - ALPHA, 0.975])
    a["effect_ci_low"], a["effect_ci_high"] = d_lo95, d_hi95
    a["primary_lower_onesided95"] = d_lo
    a["primary_reject"] = (d_lo is not None) and (d_lo >= 0.0)
    a["primary_p"] = one_sided_p(boot["delta"], 0.0)

    # --- ratio secondary machinery (gap_closed R1->R3) -----------------------
    if pt["gap"] is not None and boot["gap"]:
        g_lo95, g_lo, g_hi95 = bca_bounds(pt["gap"], boot["gap"], jack["gap"],
                                          [0.025, ALPHA, 0.975])
        a["gap_ci_low"], a["gap_ci_high"] = g_lo95, g_hi95
        a["gap_lower_onesided95"] = g_lo
        p_gap_half = one_sided_p(boot["gap"], GAP_BAR_HALF)
        p_gap_one = one_sided_p(boot["gap"], GAP_BAR_ONE)
    else:
        a["gap_ci_low"] = a["gap_ci_high"] = a["gap_lower_onesided95"] = None
        p_gap_half = p_gap_one = None

    # --- shuffled-recovery secondary + kill (advisor clause b) ---------------
    if pt["rec"] is not None and boot["rec"]:
        (r_ub,) = bca_bounds(pt["rec"], boot["rec"], jack["rec"], [1 - ALPHA])
        a["shuffled_recovery_ub95"] = r_ub
        # p for H0: recovery >= 0.30 (upper-tail analogue of one_sided_p)
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
        # kill (a) handles the dead primary
        a["shuffled_recovers_geq_30"] = False

    # --- gold-oracle ceiling (diagnostic, reported not killed) ---------------
    if boot["gold_gap"] and pt["acco"] >= 0:
        gg = sorted(boot["gold_gap"])
        a["gold_oracle_gap"] = pt["acco"] - pt["accv"]
        a["gold_oracle_gap_ci_low"] = gg[max(0, int(0.025 * len(gg)) - 1)]
        a["gold_oracle_gap_ci_high"] = gg[min(len(gg) - 1, int(0.975 * len(gg)))]
    else:
        a["gold_oracle_gap"] = None
        a["gold_oracle_gap_ci_low"] = a["gold_oracle_gap_ci_high"] = None

    # --- ONE Holm family (pre-declared conditional membership) ---------------
    sec = []
    if boot["d_text"]:
        sec.append(("beats_text_null", one_sided_p(boot["d_text"])))
    if boot["d_gloss"]:
        sec.append(("beats_gloss_self_verify", one_sided_p(boot["d_gloss"])))
    if boot["d_prm"]:
        sec.append(("prm_beaten", one_sided_p(boot["d_prm"])))
    sec.append(("shuffled_low_recovery", p_rec))
    if sep_valid and p_gap_half is not None:
        sec.append(("gap_r1r3_gt_half", p_gap_half))
        sec.append(("gap_r1r3_gt_one", p_gap_one))
    rejects = holm([p for _, p in sec])
    for (name, p), rej in zip(sec, rejects):
        a["holm"][name] = bool(rej)
        a["holm"][name + "_p"] = p
    for name, p in (("gap_r1r3_gt_half", p_gap_half),
                    ("gap_r1r3_gt_one", p_gap_one)):
        if name not in a["holm"]:
            # gate-invalid or denominator-degenerate: the ratio secondary is
            # INSTRUMENT-INVALID (excluded from Holm), reported as non-reject
            a["holm"][name] = False
            a["holm"][name + "_p"] = p
    a["beats_text_null"] = a["holm"].get("beats_text_null", False)
    a["beats_gloss_self_verify"] = a["holm"].get("beats_gloss_self_verify", False)

    # --- TOST equivalence vs R3-alone at margin h=0.2 (NULL branch) ----------
    v_vec = cells.vec(ARM_VERIFY, k=k_point)
    if v_vec is not None:
        hs = []
        for _ in range(B):
            idx = [rng.randrange(n) for _ in range(n)]
            hs.append(cohens_h(acc_of(v_vec, idx), acc_of(a3_vec, idx)))
        hs.sort()
        lo = hs[max(0, int(0.05 * len(hs)) - 1)]
        hi = hs[min(len(hs) - 1, int(0.95 * len(hs)))]
        a["tost_equivalence_pass"] = -TOST_MARGIN_H < lo and hi < TOST_MARGIN_H
    else:
        a["tost_equivalence_pass"] = False

    # --- seed robustness (C-4: >=4/5 seeds same-direction verifier lift) -----
    v_seeds = cells.by_seed.get((ARM_VERIFY, "R1", k_point), {})
    a_seeds = cells.by_seed.get((ARM_ALONE, "R1", 0), {})
    common = sorted(set(v_seeds) & set(a_seeds))
    if common:
        pos = sum(1 for s in common if acc_of(v_seeds[s]) > acc_of(a_seeds[s]))
        a["seed_sign_consistent"] = pos >= math.ceil(0.8 * len(common))
    else:
        a["seed_sign_consistent"] = False
    return out


# --------------------------------------------------------------------------
def _mk(arm, rung, correct_n, n=200, k=0, seed=0, flops=1e11):
    m = {"item_correct": [1] * correct_n + [0] * (n - correct_n),
         "metric_vector": {"inference_compute": {"flops_per_query": flops}}}
    return {"config": {"arm": arm, "rung": rung, "retry_budget": k,
                       "escalation_budget": 0, "seed": seed}, "metrics": m}


def _iface(rung="R1", n=300, fails=15):
    return {"config": {"arm": ARM_IFACE, "rung": rung, "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0},
            "metrics": {"n_labelled": n, "n_extraction_failures": fails}}


def selftest():
    # prefix-structured vectors => hand-computable statistics
    recs = [
        _mk(ARM_ALONE, "R1", 100),                       # acc1 = 0.5
        _mk(ARM_ALONE, "R3", 140, flops=4e11),           # acc3 = 0.7
        _mk(ARM_VERIFY, "R1", 150, k=1, flops=2e11),     # accv = 0.75 (best k=1)
        _mk(ARM_VERIFY, "R1", 148, k=2, flops=2.5e11),
        _mk(ARM_VERIFY, "R1", 149, k=4, flops=3e11),
        _mk(ARM_SHUF, "R1", 106, k=1, flops=2e11),       # accs = 0.53 (best k=1)
        _mk(ARM_SHUF, "R1", 105, k=2, flops=2.5e11),
        _mk(ARM_SHUF, "R1", 104, k=4, flops=3e11),
        _mk(ARM_SELFV, "R1", 120, k=1, flops=2e11),      # accg = 0.6
        _mk(ARM_SELFV, "R1", 118, k=2, flops=2.5e11),
        _mk(ARM_SELFV, "R1", 116, k=4, flops=3e11),
        _mk(ARM_GOLD, "R1", 190, k=1, flops=2e11),       # acco = 0.95
        _mk(ARM_GOLD, "R1", 188, k=2, flops=2.5e11),
        _mk(ARM_GOLD, "R1", 188, k=4, flops=3e11),
        _mk(ARM_PRM, "R1", 130, flops=2e11),             # 0.65
        _mk(ARM_TEXT, "R1", 110, flops=1.2e11),          # 0.55
        _iface(),                                        # 15/300 lb=0.0326<=0.1
    ]
    out = analyze(recs, B=800)
    a = out["analysis"]
    assert out["gates"]["instrument_valid"] is True
    assert out["gates"]["separation_valid"] is True     # sep 0.2 >= 0.1, lb > 0
    assert abs(a["separation_gap"] - 0.2) < 1e-12       # HAND: 0.7-0.5
    assert abs(a["effect_size"] - 0.05) < 1e-12         # HAND: 0.75-0.7
    assert a["best_retry_budget"] == 1
    assert a["primary_reject"] is True and a["primary_p"] < 0.05
    assert abs(a["gap_closed_fraction_r1r3"] - 1.25) < 1e-12  # HAND: .25/.20
    assert abs(a["shuffled_recovery_fraction"] - 0.12) < 1e-12  # HAND: .03/.25
    assert a["shuffled_recovers_geq_30"] is False
    assert abs(a["gold_oracle_gap"] - 0.2) < 1e-12      # HAND: 0.95-0.75
    assert abs(a["cost_ratio_vs_R3"] - 0.5) < 1e-12     # HAND: 2e11/4e11
    assert a["competitor_closes_asmuch"] is False
    assert a["holm"]["beats_text_null"] and a["holm"]["beats_gloss_self_verify"]
    assert a["holm"]["prm_beaten"] and a["holm"]["shuffled_low_recovery"]
    assert a["holm"]["gap_r1r3_gt_half"] and a["holm"]["gap_r1r3_gt_one"]
    assert a["seed_sign_consistent"] is True

    # kill-(b) branch: shuffled recovers the whole lift => kill bool fires
    recs_kill = [r for r in recs if r["config"]["arm"] != ARM_SHUF]
    recs_kill += [_mk(ARM_SHUF, "R1", 148, k=1, flops=2e11)]  # rec = .24/.25 = 0.96
    out_k = analyze(recs_kill, B=400)
    ak = out_k["analysis"]
    assert abs(ak["shuffled_recovery_fraction"] - 0.96) < 1e-12  # HAND
    assert ak["shuffled_recovers_geq_30"] is True
    assert ak["holm"]["shuffled_low_recovery"] is False

    # dead-primary branch: verify == alone-R1 => no lift, no recovery ratio
    flat = [r for r in recs if r["config"]["arm"] not in (ARM_VERIFY,)]
    flat += [_mk(ARM_VERIFY, "R1", 100, k=1, flops=2e11)]
    out2 = analyze(flat, B=400)
    a2 = out2["analysis"]
    assert a2["primary_reject"] is False                # delta = -0.2
    assert a2["gap_closed_fraction_r1r3"] == 0.0        # HAND: 0/0.2
    assert a2["shuffled_recovery_fraction"] is None     # lift <= 0: undefined
    assert a2["shuffled_recovers_geq_30"] is False      # kill (a) owns this case
    assert a2["holm"]["shuffled_low_recovery"] is False

    # separation-gate-failure branch: R3-alone == R1-alone => ratio secondaries
    # INSTRUMENT-INVALID (dropped from Holm), absolute primary still reads
    nosep = [r for r in recs if not (r["config"]["arm"] == ARM_ALONE
                                     and r["config"]["rung"] == "R3")]
    nosep += [_mk(ARM_ALONE, "R3", 100, flops=4e11)]
    out3 = analyze(nosep, B=400)
    a3 = out3["analysis"]
    assert out3["gates"]["separation_valid"] is False
    assert a3["ratio_secondaries_valid"] is False
    assert a3["gap_closed_fraction_r1r3"] is None       # degenerate denominator
    assert a3["holm"]["gap_r1r3_gt_half"] is False
    assert a3["primary_reject"] is True                 # delta = 0.75-0.5 = 0.25
    print("f2b-replicate selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records, B=B_PRODUCTION), sort_keys=True))
