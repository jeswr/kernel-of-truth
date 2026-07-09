#!/usr/bin/env python3
"""f2b EXPLORATORY re-analysis — gap_closed(R1=135M, R3=1.7B) from logged F2 data.

PHASE: exploratory (P2 P-10 / G-13 quarantine; GR-7: computed outside the
pinned analysis/f2.py script => uncitable as confirmatory, can never flip the
F2 verdict). The (R1,R3) rung pairing was NOT in the frozen HE1 pair set
{(R1,R2),(R2,R3)}; this is a post-hoc estimand over already-unblinded data.

Purely statistical: reads results-log/f2.jsonl (already-logged greedy-decoded
outputs; no new model calls), reuses the pinned machinery from analysis/f2.py
verbatim — seed-averaged per-item vectors, best retry-budget k in {1,2,4}
reselected INSIDE every bootstrap resample (P8 s1.7 selection-inside-CI),
BCa from the item jackknife, B=10000, PRNG seed 20260708, stdlib only.

Usage:  python3 poc/f2/f2b_exploratory.py < results-log/f2.jsonl
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "analysis"))
import f2  # the pinned F2 analysis module (machinery reuse only)

B = f2.B_PRODUCTION  # 10000
SEED = f2.SEED       # 20260708
GAP_BAR = f2.GAP_BAR  # 0.5


def bca_ci(theta_hat, thetas, jack):
    lo95, lo90, hi90, hi95 = f2.bca_bounds(theta_hat, thetas, jack,
                                           [0.025, 0.05, 0.95, 0.975])
    return lo95, lo90, hi90, hi95


def main():
    records = [json.loads(l) for l in sys.stdin if l.strip()]
    records = [r for r in records if r.get("config")]
    cells = f2.Cells(records)
    rng = random.Random(SEED)
    out = {"phase": "exploratory",
           "estimand": "gap_closed(R1,R3) — post-hoc pairing, NOT pre-registered"}

    a1 = cells.vec(f2.ARM_ALONE, "R1")
    a2 = cells.vec(f2.ARM_ALONE, "R2")
    a3 = cells.vec(f2.ARM_ALONE, "R3")
    n = len(a1)
    idx_all = list(range(n))

    # --- point estimates --------------------------------------------------
    k13, acc_v = f2.best_k(cells, f2.ARM_VERIFY, "R1")
    sv_k, acc_sv = f2.best_k(cells, f2.ARM_SELFV, "R1")
    acc_prm = f2.acc_of(cells.vec(f2.ARM_PRM, "R1"))
    gap13, _ = f2.gap_fraction(cells, "R1", "R3", "R1")
    out["acc"] = {"alone_R1_135M": f2.acc_of(a1),
                  "alone_R2_360M": f2.acc_of(a2),
                  "alone_R3_1p7B": f2.acc_of(a3),
                  "verify_R1_bestk": acc_v,
                  "gloss_self_verify_R1_bestk": acc_sv,
                  "prm_R1": acc_prm}
    out["best_retry_budget_verify"] = k13
    out["best_retry_budget_gloss"] = sv_k
    out["gap_closed_R1R3"] = gap13
    denom = f2.acc_of(a3) - f2.acc_of(a1)
    out["gap_closed_R1R3_gloss_arm"] = (acc_sv - f2.acc_of(a1)) / denom
    out["gap_closed_R1R3_prm_arm"] = (acc_prm - f2.acc_of(a1)) / denom

    v_fl = cells.mean_flops(f2.ARM_VERIFY, "R1", k=k13)
    r3_fl = cells.mean_flops(f2.ARM_ALONE, "R3")
    r2_fl = cells.mean_flops(f2.ARM_ALONE, "R2")
    out["cost_ratio_vs_R3"] = (v_fl / r3_fl) if (v_fl and r3_fl) else None
    out["cost_ratio_vs_R2"] = (v_fl / r2_fl) if (v_fl and r2_fl) else None

    # --- paired bootstrap (items; best-k reselected per resample) ---------
    boot_gap, boot_acc = [], {k: [] for k in out["acc"]}
    diffs_sv, diffs_prm = [], []
    sv_vec = cells.vec(f2.ARM_SELFV, "R1", k=sv_k)
    prm_vec = cells.vec(f2.ARM_PRM, "R1")
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        g, _k = f2.gap_fraction(cells, "R1", "R3", "R1", idx)
        if g is not None:
            boot_gap.append(g)
        _kb, avb = f2.best_k(cells, f2.ARM_VERIFY, "R1", idx)
        boot_acc["alone_R1_135M"].append(f2.acc_of(a1, idx))
        boot_acc["alone_R2_360M"].append(f2.acc_of(a2, idx))
        boot_acc["alone_R3_1p7B"].append(f2.acc_of(a3, idx))
        boot_acc["verify_R1_bestk"].append(avb)
        boot_acc["gloss_self_verify_R1_bestk"].append(f2.acc_of(sv_vec, idx))
        boot_acc["prm_R1"].append(f2.acc_of(prm_vec, idx))
        diffs_sv.append(avb - f2.acc_of(sv_vec, idx))
        diffs_prm.append(avb - f2.acc_of(prm_vec, idx))

    # --- jackknives + BCa CIs ---------------------------------------------
    jack_gap = []
    for i in range(n):
        idx = idx_all[:i] + idx_all[i + 1:]
        g, _ = f2.gap_fraction(cells, "R1", "R3", "R1", idx)
        jack_gap.append(g if g is not None else gap13)
    lo95, lo90, hi90, hi95 = bca_ci(gap13, boot_gap, jack_gap)
    out["gap_closed_R1R3_ci95"] = [lo95, hi95]
    out["gap_closed_R1R3_onesided95_lower"] = lo90
    out["gap_clears_half_bar"] = lo90 > GAP_BAR
    out["p_gap_gt_half"] = f2.one_sided_p(boot_gap, GAP_BAR)
    out["p_gap_gt_zero"] = f2.one_sided_p(boot_gap, 0.0)
    out["p_gap_gt_one"] = f2.one_sided_p(boot_gap, 1.0)

    vecs = {"alone_R1_135M": a1, "alone_R2_360M": a2, "alone_R3_1p7B": a3,
            "gloss_self_verify_R1_bestk": sv_vec, "prm_R1": prm_vec}
    out["acc_ci95"] = {}
    for name, th in out["acc"].items():
        if name == "verify_R1_bestk":
            jk = []
            for i in range(n):
                idx = idx_all[:i] + idx_all[i + 1:]
                jk.append(f2.best_k(cells, f2.ARM_VERIFY, "R1", idx)[1])
        else:
            v = vecs[name]
            jk = [f2.acc_of(v, idx_all[:i] + idx_all[i + 1:]) for i in range(n)]
        l95, _, _, h95 = bca_ci(th, boot_acc[name], jk)
        out["acc_ci95"][name] = [l95, h95]

    out["p_beats_gloss_self_verify"] = f2.one_sided_p(diffs_sv)
    out["p_beats_prm"] = f2.one_sided_p(diffs_prm)
    out["n_items"] = n
    out["B"] = B
    out["seed"] = SEED
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
