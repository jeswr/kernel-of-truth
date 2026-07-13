#!/usr/bin/env python3
"""knull-v2 Option-B analysis — STDIN-CONFORMANT successor of
analysis/knull_v3.py (identical statistics, verdict-gen-compatible input).

WHY THIS FILE EXISTS (interface-defect fix, NOT a design change): the original
pinned script analysis/knull_v3.py (sha256 54528cd42485effd8a08c6472b7f1f1bff
6074ad1b62cf24604b9a8dbedfa181) took argparse-REQUIRED flags
(--records/--item-meta/--out) and read those files, while tools/registry/
verdict-gen.py step 5 (§3.1) invokes the pinned analysis with the ELIGIBLE
results-log run records as JSONL on STDIN and NO argv — so the automated
verdict path could never execute the pin (argparse ap.error exits 2 =>
ERR_P2_ANALYSIS, and /pins/analysis_script is DESIGN_SCOPE, un-amendable
post-freeze). This is the SAME defect class resolved for ufo-check-0
(analysis/ufo_check_0_stdin.py), rules-1-c (analysis/rules_1c_stdin.py) and
rules-2 (analysis/rules_2_go_stdin.py); the successor is swapped in on the
DRAFT record BEFORE re-freeze. Every constant, gate expression, class, helper
(Bootstrap/BCa, mean_stat, recovery_stat, spearman, seedmean, analyse,
selftest) and the output serialization below is carried BYTE-IDENTICAL from
knull_v3.py — this file was produced by copying knull_v3.py and rewriting ONLY
this docstring and main()'s input acquisition. Parity was proven by running
the CLI original over merged/run-records.jsonl + merged/item-meta.json and
diffing its analysis.json bytes against this adapter's stdout (identical;
analysis.tost_equivalent==True in both).

INPUT CONTRACT (verdict-gen P2 §3.1 step 5): eligible run records as JSONL on
stdin — event=="run", phase=="final", exit=="ok", chain-verified,
prereg-hash-matched by verdict-gen. knull-v2's run is already merged, but the
36 SAP CELL records live under poc/knull/results-incoming/ (results staging,
not a durable pinned artifact); rather than baking a ROWS_PATH/ROWS_SHA256
constant into this frozen script (the rules-1-c style), the SAP run records and
the item metadata are CARRIED IN the log records (the ufo-check-0 style): each
eligible record's `metrics.rows` is the list of SAP cell records it witnesses
(arm/cell/rung/seed/cov/flops_per_query/… — the exact knull_v3.py record
schema) and `metrics.sidecar` is the item-meta document (kernel.types,
kernel.prompt_tokens, plain.prompt_tokens; opaque/plain-padded are carried too,
faithful to the merged file). The analysis is a PURE FUNCTION OF THE ELIGIBLE
SET: analyse() groups by (arm,cell,rung) and SORTS each group by seed, so the
reconstructed record list is order-invariant — every statistic is byte-stable
regardless of stdin order (no float-reduction-order hazard). Exactly one
consistent metrics.sidecar must be present. Any absence/inconsistency fails
closed (exit 1 => verdict-gen ERR_P2_ANALYSIS); nothing falls back or is
imputed.

Everything below main()'s input acquisition is verbatim from
analysis/knull_v3.py — see that file's docstring for the design record
(ARMS/PRIMARY/SUPERIORITY/GATES/DESCRIPTIVE/ITEM-META, ASM-1081/1083/1084/
1085/1086; the padded-cell scope trip-wire and the token-meta fail-closed
contract are TERMINAL).

Pure function of the run records + item metadata; stdlib + numpy; all
randomness from random.Random(SAP_SEED). $0, CPU-only.

Usage (verdict-gen path — the reason this file exists):
  <eligible run records as JSONL> | python3 analysis/knull_v3_stdin.py
Self-check (unchanged planted-cov selftest; never invoked by verdict-gen):
  python3 analysis/knull_v3_stdin.py --selftest
Output: canonical-ordered JSON on stdout (json.dumps(out, indent=1,
sort_keys=True) — byte-identical to knull_v3.py's --out file).
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
ARMS = ("kernel", "plain", "plain-padded", "opaque")
ALIGNED = ("plain", "plain-padded", "opaque")
MATCHED = ("plain-padded", "opaque")          # token-matched arms (ASM-1085)
R3_ARMS = ("kernel", "plain", "opaque")       # padded excluded (ASM-1086)
PADDED_CELLS = {("model-alone", "R1"), ("verify-retry", "R1")}  # ASM-1086
Z95 = 1.6448536269514722


def sfx(arm):
    """Output-field suffix for an arm name ('plain-padded' -> 'plain_padded',
    matching the section 4.6 field list)."""
    return arm.replace("-", "_")


# The full section-4.6 output-field list (pins.analysis_script.output_fields
# for the B-4 record delta). The selftest verifies every pointer resolves in
# the emitted document (freeze constraint 2, checked at build).
OUTPUT_FIELDS = [
    "/gates/bridge_kernel_lift",
    "/gates/difficulty_band_plain",
    "/gates/difficulty_band_plain_padded",
    "/gates/difficulty_band_opaque",
    "/gates/any_aligned_arm_eligible",
    "/gates/length_guard_available",
    "/gates/extraction_wilson_lb_kernel",
    "/gates/extraction_wilson_lb_plain",
    "/gates/extraction_wilson_lb_plain_padded",
    "/gates/extraction_wilson_lb_opaque",
    "/gates/extraction_ok",
    "/gates/flops_ratio_plain",
    "/gates/flops_ratio_plain_padded",
    "/gates/flops_ratio_opaque",
    "/gates/flops_parity",
    "/gates/instrument_valid",
    "/analysis/n_skeletons",
    "/analysis/n_seeds",
    "/analysis/acc_alone_r1_kernel",
    "/analysis/acc_alone_r1_plain",
    "/analysis/acc_alone_r1_plain_padded",
    "/analysis/acc_alone_r1_opaque",
    "/analysis/acc_alone_r3_kernel",
    "/analysis/acc_alone_r3_plain",
    "/analysis/acc_alone_r3_opaque",
    "/analysis/acc_verify_kernel",
    "/analysis/acc_verify_plain",
    "/analysis/acc_verify_plain_padded",
    "/analysis/acc_verify_opaque",
    "/analysis/lift_kernel",
    "/analysis/lift_kernel_lb95_1s",
    "/analysis/lift_kernel_ub95_1s",
    "/analysis/lift_plain",
    "/analysis/lift_plain_lb95_1s",
    "/analysis/lift_plain_ub95_1s",
    "/analysis/lift_plain_padded",
    "/analysis/lift_plain_padded_lb95_1s",
    "/analysis/lift_plain_padded_ub95_1s",
    "/analysis/lift_opaque",
    "/analysis/lift_opaque_lb95_1s",
    "/analysis/lift_opaque_ub95_1s",
    "/analysis/best_aligned_arm",
    "/analysis/diff",
    "/analysis/diff_lb95_1s",
    "/analysis/diff_ub95_1s",
    "/analysis/tost_equivalent",
    "/analysis/kernel_superior_beyond_margin",
    "/analysis/kernel_inferior_beyond_margin",
    "/analysis/best_matched_arm",
    "/analysis/diff_matched",
    "/analysis/diff_matched_lb95_1s",
    "/analysis/diff_matched_ub95_1s",
    "/analysis/length_effect",
    "/analysis/length_effect_lb95",
    "/analysis/length_effect_ub95",
    "/analysis/length_sensitivity",
    "/analysis/holm",
    "/analysis/per_type_breakdown",
    "/analysis/margin",
    "/analysis/sap",
]


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
    leave-one-out jackknife of the same statistic. (VERBATIM from the pinned
    analysis/knull.py.)"""

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


def _ranks(v):
    """Average ranks with tie handling (deterministic mergesort order)."""
    v = np.asarray(v, dtype=float)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(len(v))
    sv = v[order]
    base = np.arange(1.0, len(v) + 1)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = base[i:j + 1].mean()
        i = j + 1
    return ranks


def spearman(x, y):
    """Spearman rank correlation (average-rank ties); None if either input
    is constant (degenerate — disclosed, the read is DESCRIPTIVE only)."""
    rx, ry = _ranks(x), _ranks(y)
    if rx.std() == 0.0 or ry.std() == 0.0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


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

    # ASM-1086 fail-closed cell scope: the plain-padded arm runs alone-R1 +
    # verify-retry-R1 ONLY; any other plain-padded cell means an off-plan run.
    for (arm, cell, rung) in by:
        if arm == "plain-padded" and (cell, rung) not in PADDED_CELLS:
            raise SystemExit("KNULL_SAP_ERR_PADDED_CELL_SCOPE: unexpected "
                             "plain-padded cell %s/%s (ASM-1086 restricts "
                             "the padded arm to alone-R1 + verify-retry-R1)"
                             % (cell, rung))

    def covs(arm, cell, rung):
        rows = by.get((arm, cell, rung), [])
        if not rows:
            raise SystemExit("KNULL_SAP_ERR_MISSING_CELL: %s/%s/%s"
                             % (arm, cell, rung))
        return [r["cov"] for r in rows], rows

    n = len(by[("kernel", "model-alone", "R1")][0]["cov"])
    seeds = sorted(r["seed"] for r in by[("kernel", "model-alone", "R1")])

    # item_meta contract (fail-closed): types (v1-carried) + prompt tokens
    # for the kernel and plain arms (the ASM-1081 descriptive covariate read;
    # MEASURED source = the B-2 G-3 sidecar poc/knull/inputs-v4/
    # prompt-tokens.json, skeleton-rank order).
    try:
        types = item_meta["kernel"]["types"][:n]
        tok_kernel = np.array(item_meta["kernel"]["prompt_tokens"][:n],
                              dtype=float)
        tok_plain = np.array(item_meta["plain"]["prompt_tokens"][:n],
                             dtype=float)
    except (KeyError, TypeError):
        raise SystemExit("KNULL_SAP_ERR_TOKEN_META: item_meta must carry "
                         "kernel.types, kernel.prompt_tokens and "
                         "plain.prompt_tokens (see poc/knull/inputs-v4/"
                         "prompt-tokens.json)")
    if len(types) < n or len(tok_kernel) < n or len(tok_plain) < n:
        raise SystemExit("KNULL_SAP_ERR_TOKEN_META: item_meta arrays shorter "
                         "than n_skeletons (%d)" % n)

    alone_r1, alone_r3, verify, fl = {}, {}, {}, {}
    xt = {}
    for a in ARMS:
        c1, _ = covs(a, "model-alone", "R1")
        cv, rows = covs(a, "verify-retry", "R1")
        alone_r1[a], verify[a] = seedmean(c1), seedmean(cv)
        if a in R3_ARMS:                               # ASM-1086: no padded R3
            c3, _ = covs(a, "model-alone", "R3")
            alone_r3[a] = seedmean(c3)
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
        an["acc_alone_r1_%s" % sfx(a)] = float(alone_r1[a].mean())
        if a in R3_ARMS:
            an["acc_alone_r3_%s" % sfx(a)] = float(alone_r3[a].mean())
        an["acc_verify_%s" % sfx(a)] = float(verify[a].mean())
        lifts[a] = verify[a] - alone_r1[a]
        theta, q, _ = boot.bca(mean_stat("d"), {"d": lifts[a]})
        an["lift_%s" % sfx(a)] = theta
        an["lift_%s_lb95_1s" % sfx(a)] = q[0.05]
        an["lift_%s_ub95_1s" % sfx(a)] = q[0.95]

    # --- instrument gates
    g["bridge_kernel_lift"] = bool(an["lift_kernel_lb95_1s"] > BRIDGE_LIFT_MIN)
    eligible = []
    for a in ALIGNED:
        ok = bool(abs(an["acc_alone_r1_%s" % sfx(a)]
                      - an["acc_alone_r1_kernel"]) <= DIFFICULTY_BAND)
        g["difficulty_band_%s" % sfx(a)] = ok
        if ok:
            eligible.append(a)
    g["any_aligned_arm_eligible"] = bool(eligible)
    # ASM-1083: the length guard needs an eligible TOKEN-MATCHED arm
    eligible_matched = [a for a in MATCHED if g["difficulty_band_%s" % sfx(a)]]
    g["length_guard_available"] = bool(eligible_matched)
    ext_ok = True
    for a in ARMS:
        fails, calls = xt[a]
        lb = wilson_lb(calls - fails, calls) if calls else 0.0
        g["extraction_wilson_lb_%s" % sfx(a)] = lb
        ext_ok = ext_ok and (lb >= EXTRACTION_WILSON_LB_MIN)
    g["extraction_ok"] = bool(ext_ok)
    # ASM-1085: parity BINDS the token-matched arms only; the plain ratio is
    # metered and reported DESCRIPTIVE (exempt by design).
    par_ok = True
    for a in ALIGNED:
        ratio = fl[a] / fl["kernel"] if fl["kernel"] else float("nan")
        g["flops_ratio_%s" % sfx(a)] = float(ratio)
        if a in MATCHED:
            par_ok = par_ok and bool(abs(ratio - 1.0) <= FLOPS_PARITY_BAND)
    g["flops_parity"] = bool(par_ok)
    g["instrument_valid"] = bool(ext_ok and par_ok)

    # --- primary D_full (only meaningful behind the gates; computed
    # --- regardless so the output document is total — verdict rules apply
    # --- the gates)
    best = max(eligible, key=lambda a: an["lift_%s" % sfx(a)]) \
        if eligible else None
    an["best_aligned_arm"] = best or "NONE-ELIGIBLE"
    if best:
        d = lifts["kernel"] - lifts[best]
        theta, q, _ = boot.bca(mean_stat("d"), {"d": d})
        an["diff"], an["diff_lb95_1s"], an["diff_ub95_1s"] = \
            theta, q[0.05], q[0.95]
        an["tost_equivalent"] = bool(q[0.05] > -MARGIN and q[0.95] < MARGIN)
        an["kernel_inferior_beyond_margin"] = bool(q[0.95] < -MARGIN)
        d_full_superior = bool(q[0.05] > MARGIN)
    else:
        an["diff"] = an["diff_lb95_1s"] = an["diff_ub95_1s"] = None
        an["tost_equivalent"] = False
        an["kernel_inferior_beyond_margin"] = False
        d_full_superior = False

    # --- ASM-1083 length guard: D_matched vs the eligible token-matched arm
    # --- with the larger point lift; superiority = IUT conjunction; forced
    # --- false when /gates/length_guard_available is false.
    if eligible_matched:
        bm = max(eligible_matched, key=lambda a: an["lift_%s" % sfx(a)])
        an["best_matched_arm"] = bm
        dm = lifts["kernel"] - lifts[bm]
        theta, q, _ = boot.bca(mean_stat("d"), {"d": dm})
        an["diff_matched"] = theta
        an["diff_matched_lb95_1s"] = q[0.05]
        an["diff_matched_ub95_1s"] = q[0.95]
        d_matched_superior = bool(q[0.05] > MARGIN)
    else:
        an["best_matched_arm"] = "NONE-ELIGIBLE"
        an["diff_matched"] = None
        an["diff_matched_lb95_1s"] = an["diff_matched_ub95_1s"] = None
        d_matched_superior = False
    an["kernel_superior_beyond_margin"] = bool(
        g["length_guard_available"] and d_full_superior and d_matched_superior)

    # --- section 4.5 descriptive reads (outside the Holm family, never
    # --- verdict-bearing)
    le = lifts["plain-padded"] - lifts["plain"]
    theta, q, _ = boot.bca(mean_stat("d"), {"d": le},
                           alphas=(0.025, 0.975))
    an["length_effect"] = theta
    an["length_effect_lb95"] = q[0.025]
    an["length_effect_ub95"] = q[0.975]
    dt = tok_kernel - tok_plain
    an["length_sensitivity"] = spearman(lifts["kernel"] - lifts["plain"], dt)

    # --- Holm family F-sec(knull): 2 members, bootstrap-inversion p-values
    # --- (UNCHANGED from v1; the IUT does not resize the family, ASM-1083)
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
                 "bounds": "BCa (bias-corrected accelerated), one-sided 95% "
                           "(length_effect: two-sided 95%)",
                 "design": ("knull-v2 Option-B four-arm; superiority = "
                            "ASM-1083 IUT [LB95_1s(D_full) > +0.05] AND "
                            "[LB95_1s(D_matched) > +0.05], forced false "
                            "when length_guard_available is false")}
    return out


def resolve_pointer(out, ptr):
    """Resolve a /gates|/analysis JSON pointer against the output document
    (KeyError if absent) — the constraint-2 field check."""
    node = out
    for part in ptr.lstrip("/").split("/"):
        node = node[part]
    return node


def selftest():
    """Planted-cov check through the FULL four-arm pipeline: the v1 regimes
    (equivalence / superiority / inferiority / difficulty-gate / shuffled-
    bridge) plus the Option-B ones — the ASM-1083 length-guard bite (a
    kernel win over the concise plain arm alone must NOT read as
    superiority when no token-matched arm is eligible), the padded-cell
    scope trip-wire, and the sign of the section-4.5 length_effect read.
    Also verifies every OUTPUT_FIELDS pointer resolves in the emitted
    document (freeze constraint 2). Planted arms are PAIRED (aligned arms
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

    def records(pk, arm_lift, shift_arms=(), shuf_rec=0.0):
        base = 0.40
        k_alone = cell(base)
        k_verify = cell(min(0.99, base + pk))
        flip_q = {"plain": 0.02, "plain-padded": 0.025, "opaque": 0.03}
        recs = []
        for a in ARMS:
            if a == "kernel":
                alone, verify = k_alone, k_verify
            elif a in shift_arms:
                alone = cell(base + 0.5)
                verify = cell(min(0.99, base + 0.5 + arm_lift[a]))
            elif abs(arm_lift[a] - pk) < 1e-9:  # equivalence: paired flips
                alone = flipped(k_alone, flip_q[a])
                verify = flipped(k_verify, flip_q[a])
            else:                               # planted separation
                alone = flipped(k_alone, flip_q[a])
                verify = cell(min(0.99, base + arm_lift[a]))
            for seed, cov in enumerate(alone):
                recs.append({"arm": a, "cell": "model-alone", "rung": "R1",
                             "seed": seed, "cov": cov,
                             "flops_per_query": 1e9})
            if a in R3_ARMS:                    # ASM-1086: no padded R3 cell
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
        for seed, cov in enumerate(cell(base + shuf_rec * pk)):
            recs.append({"arm": "kernel", "cell": "shuffled-verify-retry",
                         "rung": "R1", "seed": seed, "cov": cov,
                         "flops_per_query": 1e9})
        return recs

    meta = {"kernel": {"types": (["def-match", "term-match", "claim-true",
                                  "claim-false"] * n)[:n],
                       "prompt_tokens": [110 + (i % 7) for i in range(n)]},
            "plain": {"prompt_tokens": [69 + (i % 5) for i in range(n)]}}

    def L(pl, pp, po):
        return {"plain": pl, "plain-padded": pp, "opaque": po}

    global B
    b_saved, B = B, 800

    r = analyse(records(0.25, L(0.25, 0.25, 0.25)), meta)
    assert r["analysis"]["tost_equivalent"], "equivalence regime failed"
    assert r["gates"]["length_guard_available"], "guard availability failed"
    for ptr in OUTPUT_FIELDS:                    # freeze constraint 2
        resolve_pointer(r, ptr)
    ls = r["analysis"]["length_sensitivity"]
    assert ls is None or -1.0 <= ls <= 1.0, "length_sensitivity out of range"

    r = analyse(records(0.40, L(0.15, 0.15, 0.15)), meta)
    assert r["analysis"]["kernel_superior_beyond_margin"], "superiority failed"
    assert r["analysis"]["best_matched_arm"] in MATCHED, "best_matched wrong"
    assert r["analysis"]["diff_matched_lb95_1s"] > MARGIN, "IUT clause 2 failed"

    r = analyse(records(0.10, L(0.40, 0.40, 0.40)), meta)
    assert r["analysis"]["kernel_inferior_beyond_margin"], "inferiority failed"

    r = analyse(records(0.25, L(0.25, 0.25, 0.25), shift_arms=ALIGNED), meta)
    assert not r["gates"]["any_aligned_arm_eligible"], "difficulty gate failed"
    assert not r["gates"]["length_guard_available"], "guard should be gone"
    assert not r["analysis"]["kernel_superior_beyond_margin"]

    # ASM-1083 bite: kernel beats the concise plain arm beyond margin, but
    # NO token-matched arm is eligible -> superiority FORCED false.
    r = analyse(records(0.40, L(0.15, 0.15, 0.15),
                        shift_arms=("plain-padded", "opaque")), meta)
    assert r["analysis"]["diff_lb95_1s"] > MARGIN, \
        "regime should show a raw kernel win vs plain"
    assert not r["gates"]["length_guard_available"], "guard should be gone"
    assert not r["analysis"]["kernel_superior_beyond_margin"], \
        "length guard failed to force superiority false"
    assert r["analysis"]["best_matched_arm"] == "NONE-ELIGIBLE"

    r = analyse(records(0.25, L(0.25, 0.25, 0.25), shuf_rec=0.9), meta)
    assert not r["analysis"]["holm"]["shuffled_low_recovery"], \
        "shuffled bridge should fail at 90% recovery"

    # section 4.5: pure token-budget effect at fixed content, planted sign
    r = analyse(records(0.25, L(0.10, 0.22, 0.10)), meta)
    assert r["analysis"]["length_effect"] > 0.05, "length_effect sign failed"

    # ASM-1086 trip-wire: an off-plan plain-padded cell fails closed
    bad = records(0.25, L(0.25, 0.25, 0.25))
    bad.append({"arm": "plain-padded", "cell": "model-alone", "rung": "R3",
                "seed": 0, "cov": [0] * n, "flops_per_query": 3e9})
    try:
        analyse(bad, meta)
        raise AssertionError("padded-cell scope trip-wire failed to fire")
    except SystemExit as e:
        assert "KNULL_SAP_ERR_PADDED_CELL_SCOPE" in str(e)

    # token-meta contract fails closed
    try:
        analyse(records(0.25, L(0.25, 0.25, 0.25)),
                {"kernel": {"types": meta["kernel"]["types"]}})
        raise AssertionError("token-meta trip-wire failed to fire")
    except SystemExit as e:
        assert "KNULL_SAP_ERR_TOKEN_META" in str(e)

    B = b_saved
    print("analysis selftest OK: equivalence / superiority(IUT) / "
          "inferiority / difficulty-gate / LENGTH-GUARD-FORCED-FALSE / "
          "shuffled-bridge / length-effect-sign / padded-cell-scope / "
          "token-meta all classified correctly; every section-4.6 "
          "output-field pointer resolves (planted covs, B=800)")


def _fail(code, msg):
    """Fail-closed stderr + exit 1 (verdict-gen maps any non-zero exit to
    ERR_P2_ANALYSIS)."""
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def main():
    # The unchanged planted-cov selftest stays reachable for a $0 self-check
    # (never invoked by verdict-gen, which passes NO argv and pipes stdin).
    if "--selftest" in sys.argv[1:]:
        selftest()
        return

    # ---- input acquisition (the ONLY departure from knull_v3.py) ----
    # verdict-gen pipes the ELIGIBLE run records as JSONL on stdin; the SAP
    # cell records and the item-meta ride IN those records (metrics.rows /
    # metrics.sidecar) — see this module's INPUT CONTRACT docstring.
    stdin_raw = sys.stdin.buffer.read().decode("utf-8")
    try:
        log_records = [json.loads(x) for x in stdin_raw.splitlines()
                       if x.strip()]
    except json.JSONDecodeError as e:
        _fail("KNULL_SAP_ERR_STDIN", "stdin is not JSONL: %s" % e)
    eligible = [r for r in log_records
                if r.get("event") == "run" and r.get("phase") == "final"
                and r.get("exit") == "ok"]
    if not eligible:
        _fail("KNULL_SAP_ERR_NO_ELIGIBLE",
              "no eligible run records on stdin (verdict-gen pipes eligible "
              "rows; the completeness gate should have fired upstream)")
    # knull-v2 freezes no reused_from block — any reuse-provenance row is a
    # contract violation (fail closed, matching the sibling stdin successors).
    if any(r.get("reuse_provenance") for r in log_records):
        _fail("KNULL_SAP_ERR_REUSE",
              "reused producer rows on stdin but knull-v2 freezes no "
              "reused_from block — refusing (fail closed)")
    # Reconstruct the SAP run records + item-meta as a PURE FUNCTION of the
    # eligible set (analyse() re-groups by (arm,cell,rung) and sorts by seed,
    # so record order is irrelevant; stdin order is preserved anyway).
    records = []
    sidecars = []
    for r in eligible:
        m = r.get("metrics") or {}
        rr = m.get("rows")
        if rr is not None:
            if not isinstance(rr, list):
                _fail("KNULL_SAP_ERR_ROWS",
                      "eligible run record seq=%r metrics.rows is not a list"
                      % r.get("seq"))
            records.extend(rr)
        sc = m.get("sidecar")
        if sc is not None:
            sidecars.append(sc)
    if not records:
        _fail("KNULL_SAP_ERR_NO_ROWS",
              "no SAP cell records carried in eligible run records' "
              "metrics.rows")
    if not sidecars:
        _fail("KNULL_SAP_ERR_NO_SIDECAR",
              "no metrics.sidecar (item-meta) carried in any eligible run "
              "record")
    # exactly one consistent item-meta sidecar (fail closed on disagreement)
    canon = {json.dumps(sc, sort_keys=True) for sc in sidecars}
    if len(canon) != 1:
        _fail("KNULL_SAP_ERR_SIDECAR_CONFLICT",
              "eligible run records carry %d distinct item-meta sidecars — "
              "refusing (fail closed)" % len(canon))
    item_meta = sidecars[0]
    # ---- everything below is verbatim from analysis/knull_v3.py main() ----
    out = analyse(records, item_meta)
    if any(r.get("mock") for r in records):
        out["mock"] = True
        out["_note"] = ("MOCK input — mechanics check only, NEVER a "
                        "measurement")
    print(json.dumps(out, indent=1, sort_keys=True))


def _r(x):
    return "None" if x is None else "%.4f" % x


if __name__ == "__main__":
    main()
