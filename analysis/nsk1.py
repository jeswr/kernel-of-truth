#!/usr/bin/env python3
"""nsk1 analysis — pinned endpoint computation for registry/experiments/nsk1.json
(DRAFT; design docs/design-neurosym-kernel-internals.md).

Pure function of the row log. Emits /gates/* and /analysis/* fields the verdict
rules consume. Stdlib only; every statistic is pre-declared:

  PRIMARY  /analysis/delta_primary        = acc(internal) - acc(external-text)
           on the covered stratum, PAIRED by item; one-sided 95% BCa bootstrap
           bounds (B=2000, seed 13). ABSOLUTE difference — never a ratio
           (the F2 degenerate-denominator lesson).
  TOST     /analysis/tost_equivalent      = 90% BCa CI inside +/-0.02.
  SPEC     /analysis/spec_delta_abs       = acc(internal) - acc(shuffled),
           paired, absolute (semantics-specificity; KILL if LB <= 0 while the
           primary passes).
  STAGE 0  /gates/stage0_rescuable_wilson_lb over swept failures vs the
           pre-declared floor 0.15 (one-sided Wilson 95%).
  GATES    extraction-failure Wilson-UB (covered, loop arms), mapper-abstention
           rate on covered, false-fire Wilson-UB on uncovered controls,
           headroom (text-only covered accuracy in [0.05, 0.85]).
"""
import argparse
import json
import math
import random
import sys

Z95 = 1.6448536269514722


def wilson_lb(k, n, z=Z95):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def wilson_ub(k, n, z=Z95):
    if n == 0:
        return 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + r) / d


def bca_bounds(pairs, seed=13, B=2000, alphas=(0.05, 0.95, 0.10, 0.90)):
    """BCa bootstrap bounds for the mean of paired differences.
    pairs: list of per-item differences (di = xi - yi, values in {-1,0,1})."""
    n = len(pairs)
    if n == 0:
        return {a: 0.0 for a in alphas}
    rng = random.Random(seed)
    theta = sum(pairs) / n
    boots = []
    for _ in range(B):
        s = 0
        for _ in range(n):
            s += pairs[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    # bias correction
    prop = sum(1 for b in boots if b < theta) / B
    prop = min(max(prop, 1.0 / (B + 1)), 1 - 1.0 / (B + 1))
    z0 = _norm_ppf(prop)
    # acceleration via jackknife
    tot = sum(pairs)
    jack = [(tot - p) / (n - 1) for p in pairs] if n > 1 else [theta]
    jm = sum(jack) / len(jack)
    num = sum((jm - j) ** 3 for j in jack)
    den = 6.0 * (sum((jm - j) ** 2 for j in jack) ** 1.5)
    a = num / den if den != 0 else 0.0
    out = {}
    for al in alphas:
        za = _norm_ppf(al)
        adj = z0 + (z0 + za) / max(1e-12, (1 - a * (z0 + za)))
        q = _norm_cdf(adj)
        idx = min(B - 1, max(0, int(q * B)))
        out[al] = boots[idx]
    return out


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_ppf(p):
    # Acklam rational approximation (sufficient for bootstrap index selection)
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
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    with open(args.rows) as f:
        for l in f:
            if l.strip():
                rows.append(json.loads(l))

    s0 = [r for r in rows if r["stage"] == 0 and r["arm"] == "backpatch-sweep"]
    s1 = [r for r in rows if r["stage"] == 1]
    by = {}
    for r in s1:
        by.setdefault((r["arm"], r["stratum"]), {})[r["item_id"]] = r

    def acc(arm, stratum="covered"):
        d = by.get((arm, stratum), {})
        if not d:
            return 0.0, 0
        k = sum(1 for r in d.values() if r["correct"])
        return k / len(d), len(d)

    def paired_diffs(arm_a, arm_b, stratum="covered"):
        da, db = by.get((arm_a, stratum), {}), by.get((arm_b, stratum), {})
        ids = sorted(set(da) & set(db))
        return [int(da[i]["correct"]) - int(db[i]["correct"]) for i in ids]

    # ---- stage 0 gate ----
    n_res = sum(1 for r in s0 if r.get("rescued"))
    s0_lb = wilson_lb(n_res, len(s0))

    # ---- primary + secondaries ----
    dp = paired_diffs("internal", "external-text")
    bb = bca_bounds(dp)
    delta = (sum(dp) / len(dp)) if dp else 0.0
    tost = (bb[0.10] > -0.02) and (bb[0.90] < 0.02)

    ds = paired_diffs("internal", "shuffled")
    bs = bca_bounds(ds, seed=17)
    dt = paired_diffs("internal", "text-only")
    bt = bca_bounds(dt, seed=19)
    de = paired_diffs("external-text", "text-only")
    be = bca_bounds(de, seed=23)

    # ---- instrument gates ----
    loop_arms = ("internal", "shuffled", "random-dir", "noop-hook", "external-text")
    cov_loop = [r for r in s1 if r["stratum"] == "covered" and r["arm"] in loop_arms]
    n_extract_fail = sum(1 for r in cov_loop if not r["extraction_ok"])
    extract_ub = wilson_ub(n_extract_fail, len(cov_loop))
    cov_int = [r for r in s1 if r["stratum"] == "covered" and r["arm"] == "internal"]
    abstain_rate = (sum(1 for r in cov_int if r["abstained"]) / len(cov_int)) if cov_int else 1.0
    unc = [r for r in s1 if r["stratum"] == "uncovered" and r["arm"] in
           ("internal", "shuffled", "random-dir")]
    n_falsefire = sum(1 for r in unc if r["fired"])
    falsefire_ub = wilson_ub(n_falsefire, len(unc))
    acc_text, n_text = acc("text-only")
    headroom_ok = (0.05 <= acc_text <= 0.85) and n_text >= 500

    # NOTE: the Stage-0 rescuable floor is deliberately NOT part of
    # instrument_valid — falling below the floor is the pre-declared FAMILY
    # KILL (verdict FAIL via its own rule), not an instrument failure.
    instrument_valid = (extract_ub <= 0.30 and
                        abstain_rate <= 0.20 and falsefire_ub <= 0.05 and
                        headroom_ok)

    out = {
        "gates": {
            "instrument_valid": bool(instrument_valid),
            "stage0_rescuable_wilson_lb": s0_lb,
            "stage0_n_swept": len(s0),
            "extraction_failure_wilson_ub": extract_ub,
            "mapper_abstention_rate_covered": abstain_rate,
            "headroom_ok": bool(headroom_ok),
        },
        "analysis": {
            "acc_internal": acc("internal")[0],
            "acc_external_text": acc("external-text")[0],
            "acc_text_only": acc_text,
            "acc_kernel_as_text": acc("kernel-as-text")[0],
            "acc_shuffled": acc("shuffled")[0],
            "acc_random_dir": acc("random-dir")[0],
            "acc_noop_hook": acc("noop-hook")[0],
            "n_covered_paired": len(dp),
            "delta_primary": delta,
            "delta_primary_bca_lb": bb[0.05],
            "delta_primary_bca_ub": bb[0.95],
            "delta_primary_bca_lb90": bb[0.10],
            "delta_primary_bca_ub90": bb[0.90],
            "tost_equivalent": bool(tost),
            "spec_delta_abs": (sum(ds) / len(ds)) if ds else 0.0,
            "spec_delta_abs_lb": bs[0.05],
            "loop_vs_textonly_delta": (sum(dt) / len(dt)) if dt else 0.0,
            "loop_vs_textonly_lb": bt[0.05],
            "external_vs_textonly_delta": (sum(de) / len(de)) if de else 0.0,
            "external_vs_textonly_lb": be[0.05],
            "falsefire_wilson_ub": falsefire_ub,
            "mean_extra_tokens_internal": _mean_tokens(s1, "internal"),
            "mean_extra_tokens_external": _mean_tokens(s1, "external-text"),
        },
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("analysis written: %s" % args.out)
    return 0


def _mean_tokens(s1, arm):
    xs = [r["extra_tokens"] for r in s1 if r["arm"] == arm and
          r["stratum"] == "covered"]
    return (sum(xs) / len(xs)) if xs else 0.0


if __name__ == "__main__":
    sys.exit(main())
