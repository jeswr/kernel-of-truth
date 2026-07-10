#!/usr/bin/env python3
"""knull analysis — pinned endpoint computation for registry/experiments/knull.json
(design doc docs/design-knull-content-injection-ablation.md sections 3-4;
pre-freeze gate G-4).

Pure function of the run records (per-cell per-item 0/1 coverage vectors +
metered FLOPs) and the item metadata. Emits every /gates/* and /analysis/*
field the verdict rules consume. Stdlib + numpy (compute only; all randomness
comes from random.Random(SAP_SEED), stable across Python versions).

Statistics (all pre-declared; NO ratio is verdict-bearing except the bridge
SECONDARY, whose denominator is guaranteed away from zero by the bridge
instrument gate — the F2 degenerate-denominator lesson):

  lift(arm)   = mean_i [ seedmean(verify_i) - seedmean(alone_r1_i) ], paired
                by skeleton rank within the arm.
  D           = mean_i [ lift_i(kernel) - lift_i(best) ], best = the aligned
                non-NSM arm (plain|opaque) passing the difficulty gate with
                the larger point lift (pre-declared selection).
  PRIMARY     TOST at margin +/-MARGIN on D: equivalent iff the one-sided 95%
                BCa LB > -MARGIN and the one-sided 95% BCa UB < +MARGIN
                (B=10000, seed 20260710, skeleton-level resampling shared
                across every statistic). Superiority: LB > +MARGIN.
                Inferiority: UB < -MARGIN.
  GATES       bridge (kernel lift LB > +0.05); difficulty band per aligned
                arm (|d acc(alone-R1)| <= 0.15, seed-mean); extraction
                success Wilson-LB >= 0.90 per arm over all verify calls;
                FLOPs parity (each aligned verify arm's mean per-query FLOPs
                within +/-20% of the kernel verify arm).
  HOLM        family F-sec(knull), 2 members, bootstrap-inversion p-values:
                shuffled_low_recovery (recovery one-sided 95% BCa UB < 0.30)
                and f2b_form_positive (acc(verify R1) - acc(alone R3), kernel
                arm, one-sided 95% BCa LB > 0).
  DESCRIPTIVE per-type accuracies/lifts (never verdict-bearing).

Usage:
  python3 analysis/knull.py --records <run-records.jsonl> \
      --item-meta <item-meta.json> --out <analysis.json>
  python3 analysis/knull.py --selftest
"""

import argparse
import json
import math
import random
import sys

import numpy as np

SAP_SEED = 20260710
B = 10000
MARGIN = 0.05
DIFFICULTY_BAND = 0.15
BRIDGE_LIFT_MIN = 0.05
SHUF_RECOVERY_MAX = 0.30
EXTRACTION_WILSON_LB_MIN = 0.90
FLOPS_PARITY_BAND = 0.20
HOLM_ALPHA = 0.05
ARMS = ("kernel", "plain", "opaque")
ALIGNED = ("plain", "opaque")
Z95 = 1.6448536269514722


def wilson_lb(k, n, z=Z95):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def _norm_ppf(p):
    """Acklam's rational approximation (stdlib-only inverse normal CDF)."""
    if not 0.0 < p < 1.0:
        return float("-inf") if p <= 0.0 else float("inf")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


class Bootstrap:
    """ONE skeleton-level resampling plan (B x n indices from
    random.Random(SAP_SEED)) shared by every statistic — pre-declared so no
    statistic gets its own resampling luck. BCa bounds per Efron: bias
    correction from the bootstrap distribution, acceleration from the
    leave-one-out jackknife of the same statistic."""

    def __init__(self, n, b=B, seed=SAP_SEED):
        rng = random.Random(seed)
        self.n = n
        self.idx = np.array([[rng.randrange(n) for _ in range(n)]
                             for _ in range(b)], dtype=np.int32)
        self.b = b

    def _dist(self, stat_fn, vectors):
        """stat_fn maps a dict of resampled per-skeleton vectors -> float."""
        out = np.empty(self.b)
        chunk = 500
        for s in range(0, self.b, chunk):
            ix = self.idx[s:s + chunk]                      # (c, n)
            res = {k: v[ix] for k, v in vectors.items()}    # (c, n) each
            out[s:s + ix.shape[0]] = stat_fn(res, axis=1)
        return out

    def bca(self, stat_fn, vectors, alphas=(0.05, 0.95)):
        """BCa quantiles of stat_fn over the shared resampling plan.
        vectors: name -> np.array shape (n,). Contract for stat_fn(res, axis):
        axis=1  -> res values are (c, n) resample matrices; reduce by mean
                   over axis 1 before combining;
        axis=None -> res values are ALREADY per-index means; combine
                   elementwise with no reduction (jackknife/theta path)."""
        theta = float(np.asarray(stat_fn(
            {k: np.array([v.mean()]) for k, v in vectors.items()},
            axis=None)).reshape(-1)[0])
        boots = self._dist(stat_fn, vectors)
        prop = float(np.mean(boots < theta))
        prop = min(max(prop, 1.0 / (self.b + 1)), 1.0 - 1.0 / (self.b + 1))
        z0 = _norm_ppf(prop)
        # jackknife (leave-one-out) via totals: all statistics here are
        # functions of per-vector MEANS, so LOO means are computed in O(n)
        n = self.n
        loo = {}
        for k, v in vectors.items():
            tot = v.sum()
            loo[k] = (tot - v) / (n - 1)
        jack = stat_fn(loo, axis=None)
        jack = np.asarray(jack, dtype=float).reshape(-1)
        jm = jack.mean()
        num = ((jm - jack) ** 3).sum()
        den = 6.0 * (((jm - jack) ** 2).sum() ** 1.5)
        acc = num / den if den != 0 else 0.0
        out = {}
        for al in alphas:
            za = _norm_ppf(al)
            adj = z0 + (z0 + za) / max(1e-12, (1.0 - acc * (z0 + za)))
            q = _norm_cdf(adj)
            k = min(self.b - 1, max(0, int(q * self.b)))
            out[al] = float(np.sort(boots)[k])
        return theta, out, boots


def mean_stat(*names, coeffs=None):
    """stat = sum_j coeffs[j] * mean(vectors[names[j]]) (paired)."""
    coeffs = coeffs or [1.0] * len(names)

    def fn(res, axis):
        acc = None
        for name, cf in zip(names, coeffs):
            v = res[name]
            m = v.mean(axis=1) if axis == 1 else v   # axis=None: already means
            term = cf * m
            acc = term if acc is None else acc + term
        return acc
    return fn


def recovery_stat(res, axis):
    """(mean(shuf) - mean(alone)) / (mean(verify) - mean(alone)) — the bridge
    SECONDARY's ratio; only computed behind the bridge gate."""
    if axis == 1:
        s = res["shuf"].mean(axis=1)
        a = res["alone"].mean(axis=1)
        v = res["verify"].mean(axis=1)
    else:                                            # already per-index means
        s, a, v = res["shuf"], res["alone"], res["verify"]
    den = v - a
    den = np.where(np.abs(den) < 1e-9, np.nan, den)
    return (s - a) / den


def load_records(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def seedmean(cells):
    """cells: list of per-item 0/1 lists (one per seed) -> np.array (n,)."""
    m = np.array(cells, dtype=float)
    return m.mean(axis=0)


def analyse(records, item_meta):
    by = {}
    for r in records:
        key = (r["arm"], r["cell"], r["rung"])
        by.setdefault(key, []).append(r)
    for key in by:
        by[key].sort(key=lambda r: r["seed"])

    def covs(arm, cell, rung):
        rows = by.get((arm, cell, rung), [])
        if not rows:
            raise SystemExit("KNULL_SAP_ERR_MISSING_CELL: %s/%s/%s"
                             % (arm, cell, rung))
        return [r["cov"] for r in rows], rows

    n = len(by[("kernel", "model-alone", "R1")][0]["cov"])
    seeds = sorted(r["seed"] for r in by[("kernel", "model-alone", "R1")])

    alone_r1, alone_r3, verify, fl = {}, {}, {}, {}
    xt = {}
    for a in ARMS:
        c1, _ = covs(a, "model-alone", "R1")
        c3, _ = covs(a, "model-alone", "R3")
        cv, rows = covs(a, "verify-retry", "R1")
        alone_r1[a], alone_r3[a], verify[a] = map(seedmean, (c1, c3, cv))
        fl[a] = float(np.mean([r["flops_per_query"] for r in rows]))
        xt[a] = (sum(r.get("extraction_failures", 0) for r in rows),
                 sum(r.get("extraction_calls", len(r["cov"])) for r in rows))
    cs, _ = covs("kernel", "shuffled-verify-retry", "R1")
    shuf = seedmean(cs)

    boot = Bootstrap(n)
    out = {"gates": {}, "analysis": {}, "descriptive": {}}
    g, an = out["gates"], out["analysis"]
    an["n_skeletons"] = n
    an["n_seeds"] = len(seeds)

    # --- accuracies + per-arm lifts (paired, BCa)
    lifts = {}
    for a in ARMS:
        an["acc_alone_r1_%s" % a] = float(alone_r1[a].mean())
        an["acc_alone_r3_%s" % a] = float(alone_r3[a].mean())
        an["acc_verify_%s" % a] = float(verify[a].mean())
        lifts[a] = verify[a] - alone_r1[a]
        theta, q, _ = boot.bca(mean_stat("d"), {"d": lifts[a]})
        an["lift_%s" % a] = theta
        an["lift_%s_lb95_1s" % a] = q[0.05]
        an["lift_%s_ub95_1s" % a] = q[0.95]

    # --- instrument gates
    g["bridge_kernel_lift"] = bool(an["lift_kernel_lb95_1s"] > BRIDGE_LIFT_MIN)
    eligible = []
    for a in ALIGNED:
        ok = bool(abs(an["acc_alone_r1_%s" % a]
                      - an["acc_alone_r1_kernel"]) <= DIFFICULTY_BAND)
        g["difficulty_band_%s" % a] = ok
        if ok:
            eligible.append(a)
    g["any_aligned_arm_eligible"] = bool(eligible)
    ext_ok = True
    for a in ARMS:
        fails, calls = xt[a]
        lb = wilson_lb(calls - fails, calls) if calls else 0.0
        g["extraction_wilson_lb_%s" % a] = lb
        ext_ok = ext_ok and (lb >= EXTRACTION_WILSON_LB_MIN)
    g["extraction_ok"] = bool(ext_ok)
    par_ok = True
    for a in ALIGNED:
        ratio = fl[a] / fl["kernel"] if fl["kernel"] else float("nan")
        g["flops_ratio_%s" % a] = float(ratio)
        par_ok = par_ok and bool(abs(ratio - 1.0) <= FLOPS_PARITY_BAND)
    g["flops_parity"] = bool(par_ok)
    g["instrument_valid"] = bool(ext_ok and par_ok)

    # --- primary (only meaningful behind the gates; computed regardless so
    # --- the output document is total — verdict rules apply the gates)
    best = max(eligible, key=lambda a: an["lift_%s" % a]) if eligible else None
    an["best_aligned_arm"] = best or "NONE-ELIGIBLE"
    if best:
        d = lifts["kernel"] - lifts[best]
        theta, q, boots = boot.bca(mean_stat("d"), {"d": d})
        an["diff"], an["diff_lb95_1s"], an["diff_ub95_1s"] = theta, q[0.05], q[0.95]
        an["tost_equivalent"] = bool(q[0.05] > -MARGIN and q[0.95] < MARGIN)
        an["kernel_superior_beyond_margin"] = bool(q[0.05] > MARGIN)
        an["kernel_inferior_beyond_margin"] = bool(q[0.95] < -MARGIN)
    else:
        an["diff"] = an["diff_lb95_1s"] = an["diff_ub95_1s"] = None
        an["tost_equivalent"] = False
        an["kernel_superior_beyond_margin"] = False
        an["kernel_inferior_beyond_margin"] = False

    # --- Holm family F-sec(knull): 2 members, bootstrap-inversion p-values
    holm = {}
    vec = {"shuf": shuf, "alone": alone_r1["kernel"], "verify": verify["kernel"]}
    if g["bridge_kernel_lift"]:
        theta, q, boots = boot.bca(recovery_stat, vec)
        rec_ub = q[0.95]
        p_rec = float(np.mean(np.nan_to_num(boots, nan=np.inf)
                              >= SHUF_RECOVERY_MAX))
        holm["shuffled_recovery_fraction"] = theta
        holm["shuffled_recovery_ub95"] = rec_ub
    else:
        holm["shuffled_recovery_fraction"] = None
        holm["shuffled_recovery_ub95"] = None
        p_rec = 1.0
    theta_f, q_f, boots_f = boot.bca(
        mean_stat("v", "a", coeffs=[1.0, -1.0]),
        {"v": verify["kernel"], "a": alone_r3["kernel"]})
    p_form = float(np.mean(boots_f <= 0.0))
    holm["f2b_form_effect"] = theta_f
    holm["f2b_form_lb95_1s"] = q_f[0.05]
    ps = sorted([("shuffled_low_recovery", p_rec),
                 ("f2b_form_positive", p_form)], key=lambda t: t[1])
    passed, alive = {}, True
    for rank, (name, p) in enumerate(ps):
        thr = HOLM_ALPHA / (len(ps) - rank)
        ok = alive and (p < thr)
        passed[name] = ok
        holm["%s_p" % name] = p
        if not ok:
            alive = False
    holm["shuffled_low_recovery"] = bool(
        passed["shuffled_low_recovery"]
        and (holm["shuffled_recovery_ub95"] is not None
             and holm["shuffled_recovery_ub95"] < SHUF_RECOVERY_MAX))
    holm["f2b_form_positive"] = bool(passed["f2b_form_positive"]
                                     and q_f[0.05] > 0.0)
    an["holm"] = holm

    # --- descriptive per-type breakdown (never verdict-bearing)
    types = item_meta["kernel"]["types"][:n]
    per_type = {}
    for t in sorted(set(types)):
        mask = np.array([x == t for x in types])
        row = {"n": int(mask.sum())}
        for a in ARMS:
            acc_a = float(alone_r1[a][mask].mean())
            acc_v = float(verify[a][mask].mean())
            row[a] = {"acc_alone_r1": acc_a, "acc_verify": acc_v,
                      "lift": acc_v - acc_a,
                      "headroom_normalized_lift":
                          (acc_v - acc_a) / (1.0 - acc_a)
                          if acc_a < 1.0 else None}
        per_type[t] = row
    an["per_type_breakdown"] = per_type

    an["margin"] = MARGIN
    an["sap"] = {"B": B, "seed": SAP_SEED,
                 "resampling": "skeleton-level, ONE shared index plan",
                 "bounds": "BCa (bias-corrected accelerated), one-sided 95%"}
    return out


def selftest():
    """Planted-cov check through the FULL pipeline: five regimes classify to
    the verdict-relevant shapes. The planted arms are PAIRED (aligned arms
    derived from the kernel covs by small flips), mirroring the skeleton
    pairing the real design uses to keep se(D) small."""
    rng = random.Random(7)
    n, seeds = 800, (0, 1, 2)

    def cell(p):
        return [[1 if rng.random() < p else 0 for _ in range(n)]
                for _ in seeds]

    def flipped(cells, q):
        return [[(1 - x) if rng.random() < q else x for x in row]
                for row in cells]

    def records(p_lift_kernel, p_lift_best, difficulty_shift=0.0,
                shuf_rec=0.0):
        base = 0.40
        paired = abs(p_lift_kernel - p_lift_best) < 1e-9
        k_alone = cell(base)
        k_verify = cell(min(0.99, base + p_lift_kernel))
        recs = []
        for a, q in (("kernel", None), ("plain", 0.02), ("opaque", 0.03)):
            if a == "kernel":
                alone, verify = k_alone, k_verify
            elif difficulty_shift:
                alone = cell(base + difficulty_shift)
                verify = cell(min(0.99, base + difficulty_shift + p_lift_best))
            elif paired:                       # equivalence: paired flips
                alone, verify = flipped(k_alone, q), flipped(k_verify, q)
            else:                              # planted separation
                alone = flipped(k_alone, q)
                verify = cell(min(0.99, base + p_lift_best))
            for seed, cov in enumerate(alone):
                recs.append({"arm": a, "cell": "model-alone", "rung": "R1",
                             "seed": seed, "cov": cov,
                             "flops_per_query": 1e9})
            for seed, cov in enumerate(cell(min(0.99, base + 0.15))):
                recs.append({"arm": a, "cell": "model-alone", "rung": "R3",
                             "seed": seed, "cov": cov,
                             "flops_per_query": 3e9})
            for seed, cov in enumerate(verify):
                recs.append({"arm": a, "cell": "verify-retry", "rung": "R1",
                             "seed": seed, "cov": cov,
                             "flops_per_query": 1e9,
                             "extraction_failures": 0,
                             "extraction_calls": n})
        for seed, cov in enumerate(cell(base + shuf_rec * p_lift_kernel)):
            recs.append({"arm": "kernel", "cell": "shuffled-verify-retry",
                         "rung": "R1", "seed": seed, "cov": cov,
                         "flops_per_query": 1e9})
        return recs

    meta = {"kernel": {"types": (["def-match", "term-match", "claim-true",
                                  "claim-false"] * n)[:n]}}

    global B
    b_saved, B = B, 800

    r = analyse(records(0.25, 0.25), meta)
    assert r["analysis"]["tost_equivalent"], "equivalence regime failed"
    r = analyse(records(0.40, 0.15), meta)
    assert r["analysis"]["kernel_superior_beyond_margin"], "superiority failed"
    r = analyse(records(0.10, 0.40), meta)
    assert r["analysis"]["kernel_inferior_beyond_margin"], "inferiority failed"
    r = analyse(records(0.25, 0.25, difficulty_shift=0.5), meta)
    assert not r["gates"]["any_aligned_arm_eligible"], "difficulty gate failed"
    r = analyse(records(0.25, 0.25, shuf_rec=0.9), meta)
    assert not r["analysis"]["holm"]["shuffled_low_recovery"], \
        "shuffled bridge should fail at 90% recovery"
    B = b_saved
    print("analysis selftest OK: equivalence / superiority / inferiority / "
          "difficulty-gate / shuffled-bridge all classified correctly "
          "(planted covs, B=800)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records")
    ap.add_argument("--item-meta")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if not (args.records and args.item_meta and args.out):
        ap.error("--records, --item-meta and --out are required")
    records = load_records(args.records)
    with open(args.item_meta, encoding="utf-8") as f:
        item_meta = json.load(f)
    out = analyse(records, item_meta)
    if any(r.get("mock") for r in records):
        out["mock"] = True
        out["_note"] = ("MOCK input — mechanics check only, NEVER a "
                        "measurement")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    an, gg = out["analysis"], out["gates"]
    print("knull SAP: n=%d seeds=%d best=%s diff=%s [%s, %s] tost=%s "
          "sup=%s inf=%s gates(instr=%s bridge=%s eligible=%s)"
          % (an["n_skeletons"], an["n_seeds"], an["best_aligned_arm"],
             _r(an["diff"]), _r(an["diff_lb95_1s"]), _r(an["diff_ub95_1s"]),
             an["tost_equivalent"], an["kernel_superior_beyond_margin"],
             an["kernel_inferior_beyond_margin"], gg["instrument_valid"],
             gg["bridge_kernel_lift"], gg["any_aligned_arm_eligible"]))


def _r(x):
    return "None" if x is None else "%.4f" % x


if __name__ == "__main__":
    main()
