#!/usr/bin/env python3
"""rules-2 pre-registered analysis (pure function over run records).

Design: docs/next/design/rules-2-train-time.md SS2.4 (endpoints and decision
rules; PROPOSED-ASM-1423..1430, 1436, 1439) + the RULES-2 build block
PROPOSED-ASM-1440..1459. Statistics discipline verbatim from the frozen
rules-1 lineage (analysis/rules_1.py): paired item BCa bootstrap B=10000,
one-sided alpha=0.05; Holm over the secondary family {s1', s2', s3', s4'};
PRNG seed 20260712 (this experiment's published seed).

Input:
  --run-records  run-records-rules2.jsonl rows {item_id, arm, rung, seed,
                 cell in {entailed, control, s_mem, s_held, stated,
                 refusal_train, timeout}, item_correct_ext, refused, ...}
  --results      results-rules2.json (pins_verified, repeat_shas,
                 training_ledger, c8_gate echo)
  --c8           poc/rules-2/results/c8-result.json (the G2 artifact)
  --rules1-primary-lb  rules-1 A3-A1 primary LB95 if that campaign has a
                 verdict (s3' is CONDITIONAL on it being > 0; absent or
                 <= 0 => s3' unevaluable: null, never a fail — ASM-1428)

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
Primary endpoint (ASM-1424): B2 - B0 on S-out entailed cells (rung R1) vs
the pinned third-party CLUTRR gold; KILL-d fires on LB <= 0. The primary is
computed on the per-item per-seed-mean paired statistic — never a
best-of-seeds selection (ASM-1439).
"""

import argparse
import json
import math
import random

OUTPUT_FIELDS = [
    "/gates/pin_gate_valid",
    "/gates/c8_lookup_gate_valid",
    "/gates/headroom_valid",
    "/gates/repeat_byte_identical",
    "/analysis/primary_lift_lb95",
    "/analysis/primary_pass",
    "/analysis/kill_d_fired",
    "/analysis/s1p_shuffled_recovery_ub95",
    "/analysis/s1p_pass",
    "/analysis/s2p_exposure_lb95",
    "/analysis/s2p_pass",
    "/analysis/s3p_gap_ni_lb95",
    "/analysis/s3p_pass",
    "/analysis/s3p_evaluable",
    "/analysis/s4p_stated_delta",
    "/analysis/s4p_refusal_delta",
    "/analysis/s4p_side_effect_flag",
    "/analysis/s4p_pass",
    "/analysis/holm_order",
    "/analysis/acc_b0_sout", "/analysis/acc_b1_sout",
    "/analysis/acc_b2_sout", "/analysis/acc_b3_sout",
    "/analysis/acc_b4_sout", "/analysis/acc_b5_sout",
    "/analysis/acc_c1p_sout",
    "/analysis/strata_profile",
    "/analysis/rung_sign_descriptive",
    "/analysis/refusal_correctness_control",
    "/analysis/gap_fraction_descriptive",
    "/analysis/b3_minus_b2_descriptive",
    "/analysis/ft_seed_variance",
    "/analysis/efficiency_ledger",
    "/analysis/accuracy", "/analysis/params", "/analysis/memory",
    "/analysis/inference_compute", "/analysis/training_compute",
]

B = 10000
SEED = 20260712
ALPHA = 0.05
NI_MARGIN = 0.05      # s3' absolute noninferiority margin (ASM-1428)
GUARD_MARGIN = 0.05   # s4' degradation guard margin (ASM-1430)
S1_RECOVERY_UB = 0.30  # s1' ceiling (ASM-1426, estate H-STRUCT verbatim)


def wilson_lb(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    ph = k / n
    return ((ph + z * z / (2 * n)) - z * math.sqrt(
        ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_ppf(p, lo=-10.0, hi=10.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def paired_diffs(rows, arm_a, arm_b, cell="entailed", rung="R1",
                 key="item_correct_ext"):
    """Per-item seed-mean difference arm_a - arm_b (ASM-1439 pairing)."""
    acc = {}
    for r in rows:
        if r["cell"] != cell or r["arm"] not in (arm_a, arm_b) \
                or r.get("rung") != rung:
            continue
        acc.setdefault(r["item_id"], {}).setdefault(r["arm"], []).append(
            r[key])
    diffs = []
    for _item, byarm in sorted(acc.items()):
        if arm_a in byarm and arm_b in byarm:
            diffs.append(sum(byarm[arm_a]) / len(byarm[arm_a]) -
                         sum(byarm[arm_b]) / len(byarm[arm_b]))
    return diffs


def bca_lb(diffs, one_sided_alpha=ALPHA, b=B, seed=SEED):
    """One-sided BCa lower bound for the mean of paired diffs (verbatim
    construction from the frozen analysis/rules_1.py lineage)."""
    n = len(diffs)
    if n == 0:
        return None
    rng = random.Random(seed)
    theta = sum(diffs) / n
    boots = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(b))
    prop = sum(1 for x in boots if x < theta) / b
    z0 = _norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
    jack = [(sum(diffs) - d) / (n - 1) for d in diffs] if n > 1 else [theta]
    jm = sum(jack) / len(jack)
    num = sum((jm - j) ** 3 for j in jack)
    den = 6 * (sum((jm - j) ** 2 for j in jack) ** 1.5) or 1e-12
    a = num / den
    zq = _norm_ppf(one_sided_alpha)
    adj = _norm_cdf(z0 + (z0 + zq) / (1 - a * (z0 + zq)))
    idx = min(max(int(adj * b), 0), b - 1)
    return boots[idx]


def acc(rows, arm, cell="entailed", rung=None):
    xs = [r["item_correct_ext"] for r in rows
          if r["arm"] == arm and r["cell"] == cell
          and (rung is None or r.get("rung") == rung)]
    return sum(xs) / len(xs) if xs else None


def refusal_rate(rows, arm, cell="control", rung=None):
    xs = [r["refused"] for r in rows
          if r["arm"] == arm and r["cell"] == cell
          and (rung is None or r.get("rung") == rung)]
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-records", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--c8", required=True)
    ap.add_argument("--rules1-primary-lb", type=float, default=None)
    args = ap.parse_args()
    rows = [json.loads(x) for x in open(args.run_records)]
    res = json.load(open(args.results))
    c8 = json.load(open(args.c8))

    repeat = res.get("repeat_shas", {})
    gates = {
        # G1 pin gate (ASM-1437): runner-verified byte-exact pins + the
        # rules-1 certificate SUCCESS flags carried in the results bytes
        "pin_gate_valid": bool(
            res.get("pins_verified") and
            res["certificate_precondition"]["success_asm_1131"] and
            res["certificate_precondition"]["gates_asm_1163_all_pass"] and
            not res["certificate_precondition"]["kill_a_fired"]),
        # G2 c8 lookup gate (ASM-1427): S-out not lookup-recoverable
        "c8_lookup_gate_valid": bool(
            c8["gate"]["gate_pass"] and
            c8["gate"]["sout_recovered_acc"] <= c8["gate"]["ceiling"]),
        # G3 headroom gate: saturated floor cannot measure a lift
        "headroom_valid": (acc(rows, "B0", rung="R1") is not None and
                           acc(rows, "B0", rung="R1") <= 0.85),
        # G4 repeat gate (ASM-1439): every arm's S-out repeat byte-identical
        "repeat_byte_identical": bool(repeat) and all(
            v.get("byte_identical") for v in repeat.values()),
    }

    primary = bca_lb(paired_diffs(rows, "B2", "B0"))
    s2p = bca_lb(paired_diffs(rows, "B2", "B1"))
    # s1' recovery: UB(c1p lift) / LB(B2 lift), conservative construction
    # verbatim from the rules-1 s1 lineage
    s1p_rec = None
    d_c1 = paired_diffs(rows, "c1p", "B0")
    d_b2 = paired_diffs(rows, "B2", "B0")
    if d_c1 and d_b2:
        ub_c1 = -bca_lb([-d for d in d_c1])
        lb_b2 = bca_lb(d_b2)
        s1p_rec = (ub_c1 / lb_b2) if lb_b2 and lb_b2 > 0 else None
    # s3' noninferiority B2 vs B4, margin 0.05, CONDITIONAL (ASM-1428)
    s3p_eval = args.rules1_primary_lb is not None \
        and args.rules1_primary_lb > 0
    s3p = bca_lb(paired_diffs(rows, "B2", "B4")) if s3p_eval else None
    # s4' degradation guard (ASM-1430): stated + refusal within 0.05 of the
    # better of B0/B1
    st_b2 = acc(rows, "B2", cell="stated", rung="R1")
    st_ref = max(x for x in (acc(rows, "B0", cell="stated", rung="R1"),
                             acc(rows, "B1", cell="stated", rung="R1"))
                 if x is not None) if any(
        x is not None for x in (acc(rows, "B0", cell="stated", rung="R1"),
                                acc(rows, "B1", cell="stated", rung="R1"))) \
        else None
    rf_b2 = refusal_rate(rows, "B2", rung="R1")
    rf_ref = max(x for x in (refusal_rate(rows, "B0", rung="R1"),
                             refusal_rate(rows, "B1", rung="R1"))
                 if x is not None) if any(
        x is not None for x in (refusal_rate(rows, "B0", rung="R1"),
                                refusal_rate(rows, "B1", rung="R1"))) \
        else None
    s4_st = (st_b2 - st_ref) if None not in (st_b2, st_ref) else None
    s4_rf = (rf_b2 - rf_ref) if None not in (rf_b2, rf_ref) else None
    s4_side_effect = any(d is not None and d < -GUARD_MARGIN
                         for d in (s4_st, s4_rf))
    s4_pass = (s4_st is not None and s4_rf is not None
               and not s4_side_effect)

    strata_profile = {}
    for arm in ("B0", "B1", "B2", "B3", "c1p"):
        strata_profile[arm] = {
            "s_mem": acc(rows, arm, cell="s_mem", rung="R1"),
            "s_held": acc(rows, arm, cell="s_held", rung="R1"),
            "s_out": acc(rows, arm, cell="entailed", rung="R1"),
            "note": "reported separately, NEVER pooled (ASM-1436); only "
                    "s_out carries the internalisation claim (ASM-1423)"}
    rung_sign = {a: {"R1": acc(rows, a, rung="R1"),
                     "R2": acc(rows, a, rung="R2")}
                 for a in ("B0", "B1", "B2")}
    b2b0 = paired_diffs(rows, "B2", "B0")
    b4b0 = paired_diffs(rows, "B4", "B0")
    gap_fraction = None
    if b2b0 and b4b0:
        m2 = sum(b2b0) / len(b2b0)
        m4 = sum(b4b0) / len(b4b0)
        gap_fraction = (m2 / m4) if m4 else None
    seed_var = {}
    for arm in ("B1", "B2", "B3", "c1p"):
        per_seed = {}
        for r in rows:
            if r["arm"] == arm and r["cell"] == "entailed" \
                    and r.get("rung") == "R1":
                per_seed.setdefault(r["seed"], []).append(
                    r["item_correct_ext"])
        accs = {s: sum(v) / len(v) for s, v in sorted(per_seed.items())}
        if accs:
            seed_var[arm] = {"per_seed": accs,
                             "range": max(accs.values()) - min(accs.values())}

    ledger = {
        "training": res.get("training_ledger", {}),
        "constants": res.get("efficiency_constants", {}),
        "note": "PROPOSED-ASM-1429: descriptive price table; NO direction "
                "presumed — the engine's marginal compute is microseconds "
                "on CPU and the ledger may show it cheaper at any realistic "
                "N, in which case the train slot's efficiency case rests on "
                "the k=4->k=1 resample reduction and dependency removal "
                "only.",
    }
    train_flops = sum(v.get("flops_formula_train", 0) or 0
                      for v in res.get("training_ledger", {}).values())

    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_pass": primary is not None and primary > 0,
        "kill_d_fired": primary is not None and primary <= 0,
        "s1p_shuffled_recovery_ub95": s1p_rec,
        "s1p_pass": s1p_rec is not None and s1p_rec < S1_RECOVERY_UB,
        "s2p_exposure_lb95": s2p,
        "s2p_pass": s2p is not None and s2p > 0,
        "s3p_gap_ni_lb95": s3p,
        "s3p_pass": (None if not s3p_eval
                     else (s3p is not None and s3p > -NI_MARGIN)),
        "s3p_evaluable": s3p_eval,
        "s4p_stated_delta": s4_st,
        "s4p_refusal_delta": s4_rf,
        "s4p_side_effect_flag": s4_side_effect,
        "s4p_pass": s4_pass,
        "holm_order": ["s1p", "s2p", "s3p", "s4p"],
        "acc_b0_sout": acc(rows, "B0", rung="R1"),
        "acc_b1_sout": acc(rows, "B1", rung="R1"),
        "acc_b2_sout": acc(rows, "B2", rung="R1"),
        "acc_b3_sout": acc(rows, "B3", rung="R1"),
        "acc_b4_sout": acc(rows, "B4", rung="R1"),
        "acc_b5_sout": acc(rows, "B5", rung="R3"),
        "acc_c1p_sout": acc(rows, "c1p", rung="R1"),
        "strata_profile": strata_profile,
        "rung_sign_descriptive": {
            "values": rung_sign,
            "note": "two rungs license a SIGN, not a slope (ASM-1433)"},
        "refusal_correctness_control": {
            a: refusal_rate(rows, a) for a in
            ("B0", "B1", "B2", "B3", "B4", "B5", "c1p")},
        "gap_fraction_descriptive": gap_fraction,
        "b3_minus_b2_descriptive": bca_lb(paired_diffs(rows, "B3", "B2")),
        "ft_seed_variance": seed_var,
        "efficiency_ledger": ledger,
        "accuracy": acc(rows, "B2", rung="R1"),
        "params": 135_000_000,
        "memory": None,
        "inference_compute": (lambda xs: sum(xs) if xs else None)(
            [r.get("flops_formula", 0) for r in rows]),
        "training_compute": train_flops,
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
