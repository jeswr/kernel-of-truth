#!/usr/bin/env python3
"""deconf-b pinned analysis — the aligned-generic-store deconfound, Stage B
(DRAFT registry record registry/experiments/deconf-b.json; freeze-ready spec
docs/next/design/deconf-stageb-spec.md; DECONF.md rev-B §5.2/§6 verbatim).

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; deterministic (PRNG seed 20260711, B=10000 paired
item-level BCa bootstrap over seed-averaged per-item means; float64
end-to-end, no pre-rounding).

WHAT THIS EXPERIMENT SEPARATES: A1 measured the pinned checker extensionally
equal to its urn-keyed answer-key projection (GS-A bit-identical to the kernel
arm at the pins); stage-2 measured the lift on blind external gold. Stage B
asks whether the ALIGNMENT (the item-aligned deterministic answer key) is the
load-bearing ingredient, or whether a generic lexical store (BM25 precursor)
with a generic menu acceptance signal (self-consistency, RAGC frozen-menu
item (i)) at matched budget through the identical retry topology reproduces
the lift too.

  PRIMARY  delta_align = acc_ext(gsa-verify-retry) - acc_ext(gr-d-lite),
           paired item-level on the shared 333-item x 5-seed grid
           (PROPOSED-ASM-1013/1100). Branches (DECONF §5.2 verbatim):
           - COLLAPSE (verdict NULL = ATTRIBUTION-COLLAPSE-AT-SCOPE): TOST —
             the 90% BCa CI of delta_align lies entirely inside
             (-0.05, +0.05);
           - ALIGNMENT-SPECIFIC (verdict PASS): the primary's Holm-ADJUSTED
             one-sided p vs the null delta <= +0.05 clears alpha = 0.05
             (PROPOSED-ASM-1107; unadjusted LCB95 + Holm-floor LCB
             co-reported);
           - neither: INCONCLUSIVE-UNDERPOWERED (verdict INCONCLUSIVE) —
             no attribution sentence in either direction.
  HOLM     ONE family, four named one-sided contrasts (PROPOSED-ASM-1107):
           {delta_align > 0.05; bridge lift (gsa - alone) > 0.05;
            gr-d-lite - gr-a-lite > 0; gsa-verify-retry - gr-a-lite > 0}.
  GATES    (INSTRUMENT-INVALID-at-B, never FAIL/PASS/NULL): P10 extraction;
           RT-7a engagement on the gsa-verify-retry cells; headroom
           acc_ext(model-alone) <= 0.85; bridge gate — one-sided 95% BCa LB
           of (gsa - alone) > +0.05 (no reproduced lift => nothing to
           attribute; a bridge failure against the landed stage-2 result is
           a flagged inconsistency to investigate, ASM-0964).
  DESCRIPTIVE ONLY (never Holm, never verdict-bearing): recovery_rag =
           (grd - alone)/(gsa - alone); dual-scored acc_mem; hit@j +
           zero-hit retrieval disclosures; the §2.2 GR-D-lite calibration
           table; per-type breakdown; GS-A<->kernel identity diagnostic when
           the PROPOSED-ASM-1105 fallback arm ran.

VERDICT-NAME MAPPING (pinned; the kot-reg/2 enum is canonical): PASS ==
ALIGNMENT-SPECIFIC (+ rider); NULL == ATTRIBUTION-COLLAPSE-AT-SCOPE (+ rider;
the K-P3v2(4) input at this scope, equal prominence); INCONCLUSIVE ==
INCONCLUSIVE-UNDERPOWERED (+ rider); INSTRUMENT-INVALID ==
INSTRUMENT-INVALID-at-B. RIDER on every verdict sentence, verbatim
(ASM-1017): self-authored items, kernel-covered slice, oracle-addressed
store; external adjudication removes membership-gold circularity, not
item-generation or store-addressing circularity.

Missing arms/cells leave fields unresolvable and the verdict INCOMPLETE-DATA
(fail closed at verdict-gen step 7); nothing is imputed.

Fixture: --selftest (constructed cells; hand-computed values in comments).
"""
import json
import math
import sys
from statistics import NormalDist

SEED = 20260711
B_PRODUCTION = 10000
ALPHA = 0.05
DELTA_SUP = 0.05            # superiority margin (PROPOSED-ASM-1013)
DELTA_EQ = 0.05             # TOST equivalence margin (PROPOSED-ASM-1013)
BRIDGE_MIN = 0.05           # bridge gate: LB95(gsa - alone) must exceed this
HOLM_FLOOR = ALPHA / 4.0    # worst-case floor the power sizing used (§1.3)
DECIDABLE_MIN = 0.95
REJECT_RATE_LO = 0.05
REJECT_RATE_HI = 0.95
HEADROOM_MAX = 0.85
IFACE_FAIL_BOUND = 0.10
Z_ONE_SIDED = 1.645
ND = NormalDist()

ARM_ALONE = "model-alone"
ARM_GSA = "gsa-verify-retry"
ARM_GRA = "gr-a-lite"
ARM_GRD = "gr-d-lite"
ARM_KERNEL = "kernel-verify-retry"
ARM_IFACE = "extraction-instrument"
ARM_EVALMAN = "eval-manifest"
RETRY_K = 4


def wilson_lb(p, n, z=Z_ONE_SIDED):
    if n <= 0:
        return 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


class Cells:
    """(arm, rung, k) -> per-item seed-averaged accuracy vectors (ext + mem),
    plus per-seed ext vectors, the P10 sums, the RT-7a engagement sums (from
    gsa-verify-retry cells), the GR-D-lite calibration sums, the retrieval
    aggregate and the eval-manifest provenance record."""

    def __init__(self, records):
        ext, mem = {}, {}
        self.iface = {}
        self.evalman = None
        self.by_seed_ext = {}
        self.engagement = {"n_items": 0, "n_decidable": 0,
                           "n_attempt0_rejected": 0,
                           "n_final_differs_attempt0": 0, "cells": 0,
                           "cells_with_block": 0}
        self.calib = None
        self.retrieval = None
        for r in records:
            cfg, m = r["config"], r["metrics"]
            arm, rung = cfg["arm"], cfg["rung"]
            if arm == ARM_IFACE:
                s = self.iface.setdefault(rung, {"n": 0, "fail": 0})
                s["n"] += int(m["n_labelled"])
                s["fail"] += int(m["n_extraction_failures"])
                continue
            if arm == ARM_EVALMAN:
                if self.evalman is not None:
                    print("deconf-b analysis: duplicate eval-manifest record",
                          file=sys.stderr)
                    sys.exit(1)
                self.evalman = m
                continue
            key = (arm, rung, int(cfg.get("retry_budget", 0) or 0))
            ext.setdefault(key, []).append([int(x) for x in m["item_correct_ext"]])
            mem.setdefault(key, []).append([int(x) for x in m["item_correct_mem"]])
            self.by_seed_ext.setdefault(key, {})[cfg.get("seed", 0)] = [
                int(x) for x in m["item_correct_ext"]]
            if arm == ARM_GSA:
                self.engagement["cells"] += 1
                eng = m.get("verifier_engagement")
                if eng is not None:
                    self.engagement["cells_with_block"] += 1
                    for f in ("n_items", "n_decidable", "n_attempt0_rejected",
                              "n_final_differs_attempt0"):
                        self.engagement[f] += int(eng[f])
            if arm == ARM_GRD:
                cal = m.get("grd_calibration")
                if cal is not None:
                    if self.calib is None:
                        self.calib = {"n_items": 0, "n_accepted": 0,
                                      "n_exhausted": 0, "n_generations": 0,
                                      "accept_attempt_hist": None,
                                      "agree_hist": None, "cells": 0}
                    c = self.calib
                    c["cells"] += 1
                    for f in ("n_items", "n_accepted", "n_exhausted",
                              "n_generations"):
                        c[f] += int(cal[f])
                    for hf in ("accept_attempt_hist", "agree_hist"):
                        if c[hf] is None:
                            c[hf] = [0] * len(cal[hf])
                        c[hf] = [a + int(b) for a, b in zip(c[hf], cal[hf])]
                if self.retrieval is None:
                    self.retrieval = m.get("retrieval_summary")
        self.grd_cells = sum(1 for k in ext if k[0] == ARM_GRD)
        self.items_ext, self.items_mem = {}, {}
        for store, out in ((ext, self.items_ext), (mem, self.items_mem)):
            for key, seed_vecs in store.items():
                n = len(seed_vecs[0])
                if any(len(v) != n for v in seed_vecs):
                    print("deconf-b analysis: item-vector length mismatch in "
                          "cell %r" % (key,), file=sys.stderr)
                    sys.exit(1)
                out[key] = [sum(v[i] for v in seed_vecs) / len(seed_vecs)
                            for i in range(n)]
        self.n_seeds = {key: len(v) for key, v in self.by_seed_ext.items()}

    def vec(self, arm, rung="R1", k=0, scoring="ext"):
        store = self.items_ext if scoring == "ext" else self.items_mem
        return store.get((arm, rung, k))


def acc_of(vec, idx=None):
    if idx is None:
        return sum(vec) / len(vec)
    return sum(vec[i] for i in idx) / len(idx)


def bca_bounds(theta_hat, thetas, jack, levels):
    """BCa bounds at the given lower-tail levels (item jackknife). Verbatim
    machinery from the pinned analysis/f2b_transfer.py (RAGC §8.4 shape)."""
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
    """Bootstrap one-sided p vs H0: theta <= null (share of resampled
    statistics <= the null, add-one smoothed)."""
    b = len(boot)
    if b == 0:
        return 1.0
    return (1 + sum(1 for d in boot if d <= null)) / (b + 1)


def holm_adjusted(pvals):
    """Holm step-down ADJUSTED p-values (monotone, capped at 1). The primary's
    verdict branch fires on its adjusted p (PROPOSED-ASM-1107)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def analyze(records, B=B_PRODUCTION):
    import random
    rng = random.Random(SEED)
    cells = Cells(records)
    out = {"gates": {}, "analysis": {"holm": {}}}
    a = out["analysis"]

    al = cells.vec(ARM_ALONE, "R1")
    gs = cells.vec(ARM_GSA, k=RETRY_K)
    ra = cells.vec(ARM_GRA)
    rd = cells.vec(ARM_GRD, k=RETRY_K)
    kv = cells.vec(ARM_KERNEL, k=RETRY_K)  # PROPOSED-ASM-1105 fallback only
    a["kernel_arm_present"] = kv is not None
    if any(x is None for x in (al, gs, ra, rd)):
        return out  # missing arms: INCOMPLETE-DATA downstream (fail closed)

    n = len(al)
    a["n_eval_items"] = n
    a["n_seeds"] = cells.n_seeds.get((ARM_GSA, "R1", RETRY_K))
    if cells.evalman is not None:
        a["eval_item_ids_sha256"] = cells.evalman.get("eval_item_ids_sha256")

    # ---- P10 extraction-failure instrument gate (R1) --------------------------
    st = cells.iface.get("R1")
    out["gates"]["instrument_valid"] = bool(
        st and st["n"] >= 300
        and wilson_lb(st["fail"] / st["n"], st["n"]) <= IFACE_FAIL_BOUND)

    # ---- engagement gate (RT-7a, over the gsa-verify-retry cells) -------------
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

    al_mem = cells.vec(ARM_ALONE, "R1", scoring="mem")
    gs_mem = cells.vec(ARM_GSA, k=RETRY_K, scoring="mem")

    def stats_for(idx=None):
        acc_al = acc_of(al, idx)
        acc_gs = acc_of(gs, idx)
        acc_ra = acc_of(ra, idx)
        acc_rd = acc_of(rd, idx)
        bridge = acc_gs - acc_al                 # bridge gate + Holm member
        delta = acc_gs - acc_rd                  # PRIMARY delta_align
        loop = acc_rd - acc_ra                   # loop pricing (Holm member)
        key = acc_gs - acc_ra                    # key vs retrieval (Holm member)
        rec = ((acc_rd - acc_al) / bridge) if bridge > 1e-12 else None
        return {"acc_al": acc_al, "acc_gs": acc_gs, "acc_ra": acc_ra,
                "acc_rd": acc_rd, "bridge": bridge, "delta": delta,
                "loop": loop, "key": key, "rec": rec}

    pt = stats_for()
    a["acc_ext_alone_r1"] = pt["acc_al"]
    a["acc_ext_gsa_verify_k4"] = pt["acc_gs"]
    a["acc_ext_gra_lite"] = pt["acc_ra"]
    a["acc_ext_grd_lite"] = pt["acc_rd"]
    a["acc_ext_kernel_verify_k4"] = acc_of(kv) if kv is not None else None
    a["acc_mem_alone_r1"] = acc_of(al_mem)
    a["acc_mem_gsa_verify_k4"] = acc_of(gs_mem)
    a["bridge_lift"] = pt["bridge"]
    a["delta_align"] = pt["delta"]
    a["grd_minus_gra"] = pt["loop"]
    a["gsa_minus_gra"] = pt["key"]
    a["recovery_rag"] = pt["rec"]  # DESCRIPTIVE ONLY (PROPOSED-ASM-1013)

    # ---- headroom gate ---------------------------------------------------------
    out["gates"]["headroom_valid"] = pt["acc_al"] <= HEADROOM_MAX + 1e-12

    # ---- paired item bootstrap (B=10000, PRNG seed 20260711) -------------------
    boot = {"bridge": [], "delta": [], "loop": [], "key": [], "rec": []}
    rec_invalid = 0
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        s = stats_for(idx)
        for f in ("bridge", "delta", "loop", "key"):
            boot[f].append(s[f])
        if s["rec"] is not None:
            boot["rec"].append(s["rec"])
        else:
            rec_invalid += 1
    a["recovery_defined_fraction"] = (B - rec_invalid) / B if B else None

    # ---- item jackknife for BCa acceleration -----------------------------------
    jack = {"bridge": [], "delta": [], "loop": [], "key": []}
    idx_all = list(range(n))
    for i in range(n):
        idx = idx_all[:i] + idx_all[i + 1:]
        s = stats_for(idx)
        for f in jack:
            jack[f].append(s[f])

    # ---- bridge gate (one-sided 95% BCa LB must clear +0.05) -------------------
    (bridge_lb,) = bca_bounds(pt["bridge"], boot["bridge"], jack["bridge"],
                              [ALPHA])
    a["bridge_lift_lower_onesided95"] = bridge_lb
    out["gates"]["bridge_valid"] = bridge_lb is not None and bridge_lb > BRIDGE_MIN

    # ---- PRIMARY delta_align: bounds + TOST + Holm-adjusted decision ----------
    d_tost_lo, d_lo95, d_holm_floor_lo, d_tost_hi = bca_bounds(
        pt["delta"], boot["delta"], jack["delta"],
        [ALPHA, ALPHA, HOLM_FLOOR, 1 - ALPHA])
    a["delta_align_ci90_low"] = d_tost_lo
    a["delta_align_ci90_high"] = d_tost_hi
    a["delta_align_lower_onesided95"] = d_lo95
    a["delta_align_lower_holm_floor"] = d_holm_floor_lo

    p_delta = one_sided_p(boot["delta"], DELTA_SUP)
    p_bridge = one_sided_p(boot["bridge"], DELTA_SUP)
    p_loop = one_sided_p(boot["loop"], 0.0)
    p_key = one_sided_p(boot["key"], 0.0)
    a["delta_align_p"] = p_delta

    # ONE Holm family, four named one-sided contrasts (PROPOSED-ASM-1107)
    names = ["delta_align", "bridge_lift", "grd_minus_gra", "gsa_minus_gra"]
    raw = [p_delta, p_bridge, p_loop, p_key]
    adj = holm_adjusted(raw)
    for name, p_raw, p_adj in zip(names, raw, adj):
        a["holm"][name] = bool(p_adj <= ALPHA)
        a["holm"][name + "_p"] = p_raw
        a["holm"][name + "_p_adjusted"] = p_adj
    a["delta_align_p_holm"] = adj[0]

    # ---- verdict branches (DECONF §5.2 verbatim; mapping in the docstring) ----
    tost = (d_tost_lo is not None and d_tost_hi is not None
            and -DELTA_EQ < d_tost_lo and d_tost_hi < DELTA_EQ)
    superiority = adj[0] <= ALPHA
    a["tost_equivalence_pass"] = tost                # NULL  = COLLAPSE (+rider)
    a["superiority_pass"] = superiority              # PASS  = ALIGNMENT-SPECIFIC
    a["inconclusive_underpowered"] = not (tost or superiority)

    # ---- descriptive co-reports (never verdict-bearing) ------------------------
    cal = cells.calib
    if cal and cal["n_items"]:
        a["grd_acceptance_rate"] = cal["n_accepted"] / cal["n_items"]
        a["grd_exhaustion_rate"] = cal["n_exhausted"] / cal["n_items"]
        a["grd_accept_attempt_hist"] = cal["accept_attempt_hist"]
        a["grd_agree_hist"] = cal["agree_hist"]
        a["grd_generations_total"] = cal["n_generations"]
    else:
        a["grd_acceptance_rate"] = None
        a["grd_exhaustion_rate"] = None
        a["grd_accept_attempt_hist"] = None
        a["grd_agree_hist"] = None
        a["grd_generations_total"] = None
    r = cells.retrieval
    if r:
        a["retrieval_zero_hit_count"] = r["zero_hit_count"]
        a["retrieval_hit_at_j_rate"] = r["hit_at_j_count"] / max(1, r["n_items"])
        a["retrieval_mean_selected_docs"] = r["mean_selected_docs"]
        a["retrieval_mean_context_tokens"] = r["mean_context_tokens"]
    else:
        a["retrieval_zero_hit_count"] = None
        a["retrieval_hit_at_j_rate"] = None
        a["retrieval_mean_selected_docs"] = None
        a["retrieval_mean_context_tokens"] = None

    # GS-A<->kernel identity diagnostic (only when the fallback arm ran):
    # fraction of (item, seed) ext-correctness bits identical across the two
    # arms — expected 1.0 under the A1 certificate; cross-container numeric
    # nondeterminism can break it (read as diagnostic, never endpoint).
    if kv is not None:
        g_seeds = cells.by_seed_ext.get((ARM_GSA, "R1", RETRY_K), {})
        k_seeds = cells.by_seed_ext.get((ARM_KERNEL, "R1", RETRY_K), {})
        common = sorted(set(g_seeds) & set(k_seeds))
        tot = same = 0
        for s in common:
            for x, y in zip(g_seeds[s], k_seeds[s]):
                tot += 1
                same += int(x == y)
        a["gsa_kernel_identity_fraction"] = (same / tot) if tot else None
    else:
        a["gsa_kernel_identity_fraction"] = None

    # bridge seed-sign robustness (descriptive)
    g_seeds = cells.by_seed_ext.get((ARM_GSA, "R1", RETRY_K), {})
    a_seeds = cells.by_seed_ext.get((ARM_ALONE, "R1", 0), {})
    common = sorted(set(g_seeds) & set(a_seeds))
    if common:
        pos = sum(1 for s in common if acc_of(g_seeds[s]) > acc_of(a_seeds[s]))
        a["seed_sign_consistent_bridge"] = pos >= math.ceil(0.8 * len(common))
    else:
        a["seed_sign_consistent_bridge"] = None

    # per-type breakdown (descriptive only)
    if cells.evalman is not None and "item_types" in cells.evalman:
        types = cells.evalman["item_types"]
        if len(types) == n:
            per = {}
            for ty in sorted(set(types)):
                idx = [i for i, t in enumerate(types) if t == ty]
                per[ty] = {"n": len(idx),
                           "acc_ext_alone": acc_of(al, idx),
                           "acc_ext_gsa": acc_of(gs, idx),
                           "acc_ext_gra": acc_of(ra, idx),
                           "acc_ext_grd": acc_of(rd, idx)}
            a["per_type"] = per
    return out


OUTPUT_FIELDS = [
    "/gates/instrument_valid", "/gates/engagement_valid",
    "/gates/headroom_valid", "/gates/bridge_valid",
    "/analysis/n_eval_items", "/analysis/n_seeds",
    "/analysis/eval_item_ids_sha256", "/analysis/kernel_arm_present",
    "/analysis/acc_ext_alone_r1", "/analysis/acc_ext_gsa_verify_k4",
    "/analysis/acc_ext_gra_lite", "/analysis/acc_ext_grd_lite",
    "/analysis/acc_ext_kernel_verify_k4",
    "/analysis/acc_mem_alone_r1", "/analysis/acc_mem_gsa_verify_k4",
    "/analysis/engagement_decidable_fraction",
    "/analysis/engagement_attempt0_reject_rate",
    "/analysis/engagement_final_differs_attempt0",
    "/analysis/bridge_lift", "/analysis/bridge_lift_lower_onesided95",
    "/analysis/delta_align", "/analysis/delta_align_ci90_low",
    "/analysis/delta_align_ci90_high",
    "/analysis/delta_align_lower_onesided95",
    "/analysis/delta_align_lower_holm_floor",
    "/analysis/delta_align_p", "/analysis/delta_align_p_holm",
    "/analysis/grd_minus_gra", "/analysis/gsa_minus_gra",
    "/analysis/holm/delta_align", "/analysis/holm/delta_align_p",
    "/analysis/holm/delta_align_p_adjusted",
    "/analysis/holm/bridge_lift", "/analysis/holm/bridge_lift_p",
    "/analysis/holm/bridge_lift_p_adjusted",
    "/analysis/holm/grd_minus_gra", "/analysis/holm/grd_minus_gra_p",
    "/analysis/holm/grd_minus_gra_p_adjusted",
    "/analysis/holm/gsa_minus_gra", "/analysis/holm/gsa_minus_gra_p",
    "/analysis/holm/gsa_minus_gra_p_adjusted",
    "/analysis/tost_equivalence_pass", "/analysis/superiority_pass",
    "/analysis/inconclusive_underpowered",
    "/analysis/recovery_rag", "/analysis/recovery_defined_fraction",
    "/analysis/grd_acceptance_rate", "/analysis/grd_exhaustion_rate",
    "/analysis/grd_accept_attempt_hist", "/analysis/grd_agree_hist",
    "/analysis/grd_generations_total",
    "/analysis/retrieval_zero_hit_count", "/analysis/retrieval_hit_at_j_rate",
    "/analysis/retrieval_mean_selected_docs",
    "/analysis/retrieval_mean_context_tokens",
    "/analysis/gsa_kernel_identity_fraction",
    "/analysis/seed_sign_consistent_bridge", "/analysis/per_type",
]


def _mk_record(arm, k, seed, ext, mem, extra=None):
    m = {"item_correct_ext": ext, "item_correct_mem": mem}
    if extra:
        m.update(extra)
    return {"event": "run", "phase": "final", "exit": "ok",
            "config": {"arm": arm, "rung": "R1", "retry_budget": k,
                       "escalation_budget": 0, "seed": seed},
            "metrics": m}


def selftest():
    """Constructed cells; hand-computed values asserted."""
    n = 8
    # alone: 2/8 = 0.25; gsa: 6/8 = 0.75; gra: 3/8 = 0.375; grd: 4/8 = 0.5
    alone = [1, 1, 0, 0, 0, 0, 0, 0]
    gsa = [1, 1, 1, 1, 1, 1, 0, 0]
    gra = [1, 1, 1, 0, 0, 0, 0, 0]
    grd = [1, 1, 1, 1, 0, 0, 0, 0]
    eng = {"n_items": n, "n_decidable": n, "n_attempt0_rejected": 4,
           "n_final_differs_attempt0": 3}
    cal = {"n_items": n, "n_accepted": 6, "n_exhausted": 2,
           "accept_attempt_hist": [4, 1, 1, 0, 0],
           "agree_hist": [1, 1, 2, 12], "n_generations": 8 * 8}
    recs = []
    for seed in (0, 1):
        recs.append(_mk_record(ARM_ALONE, 0, seed, alone, alone))
        recs.append(_mk_record(ARM_GSA, 4, seed, gsa, gsa,
                               {"verifier_engagement": eng}))
        recs.append(_mk_record(ARM_GRA, 0, seed, gra, gra))
        recs.append(_mk_record(ARM_GRD, 4, seed, grd, grd,
                               {"grd_calibration": cal,
                                "retrieval_summary": {
                                    "n_items": n, "zero_hit_count": 1,
                                    "hit_at_j_count": 6,
                                    "mean_selected_docs": 5.0,
                                    "mean_context_tokens": 400.0}}))
    recs.append({"event": "run", "phase": "final", "exit": "ok",
                 "config": {"arm": ARM_IFACE, "rung": "R1", "retry_budget": 0,
                            "escalation_budget": 0, "seed": 0},
                 "metrics": {"n_labelled": 400, "n_extraction_failures": 4,
                             "n_extraction_errors": 0}})
    recs.append({"event": "run", "phase": "final", "exit": "ok",
                 "config": {"arm": ARM_EVALMAN, "rung": "R1",
                            "retry_budget": 0, "escalation_budget": 0,
                            "seed": 0},
                 "metrics": {"eval_item_ids_sha256": "t" * 64,
                             "item_types": ["def-match"] * 4 + ["claim-true"] * 4}})
    out = analyze(recs, B=500)
    a = out["analysis"]
    assert abs(a["acc_ext_alone_r1"] - 0.25) < 1e-12
    assert abs(a["acc_ext_gsa_verify_k4"] - 0.75) < 1e-12
    assert abs(a["delta_align"] - 0.25) < 1e-12          # 0.75 - 0.50
    assert abs(a["bridge_lift"] - 0.50) < 1e-12          # 0.75 - 0.25
    assert abs(a["grd_minus_gra"] - 0.125) < 1e-12       # 0.50 - 0.375
    assert abs(a["gsa_minus_gra"] - 0.375) < 1e-12       # 0.75 - 0.375
    assert abs(a["recovery_rag"] - 0.5) < 1e-12          # 0.25 / 0.50
    assert out["gates"]["headroom_valid"] is True
    assert out["gates"]["engagement_valid"] is True      # 1.0 dec, 0.5 rej, 3>0
    assert out["gates"]["instrument_valid"] is True      # fail 1%, LB<10% @400
    assert abs(a["grd_acceptance_rate"] - 0.75) < 1e-12  # 6/8
    assert a["kernel_arm_present"] is False
    assert a["gsa_kernel_identity_fraction"] is None
    # Holm adjusted-p monotonicity sanity
    ps = [a["holm"][k + "_p_adjusted"] for k in
          ("delta_align", "bridge_lift", "grd_minus_gra", "gsa_minus_gra")]
    assert all(0.0 < p <= 1.0 for p in ps)
    # verdict branches are mutually exclusive by construction
    assert not (a["tost_equivalence_pass"] and a["superiority_pass"])
    # holm_adjusted hand-check: [0.01, 0.04, 0.03, 0.5] ->
    #   sorted .01,.03,.04,.5; adj = 4*.01=.04, max(.04,3*.03)=.09,
    #   max(.09,2*.04)=.09, max(.09,1*.5)=.5  (order restored below)
    got = holm_adjusted([0.01, 0.04, 0.03, 0.5])
    want = [0.04, 0.09, 0.09, 0.5]
    assert all(abs(g - w) < 1e-12 for g, w in zip(got, want)), got
    print("deconf-b analysis selftest OK", file=sys.stderr)


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    records = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("event") == "run" and r.get("exit") == "ok":
            records.append(r)
    out = analyze(records)
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
