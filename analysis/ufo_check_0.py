#!/usr/bin/env python3
"""ufo-check-0 pre-registered analysis (pure function over run records).

Design: docs/next/design/ufo-check-0.md §6 (endpoints, gates, kills).
Record: registry/experiments/ufo-check-0.json (kot-reg/2, ORACLE-DIAGNOSTIC).
ASMs: PROPOSED-ASM-1480..1493 (registered centrally at freeze).

Input: --run-records <run-records-ufo0.jsonl>, one row per item x arm x host
x seed: {item_id, family, gold, host in {r135, r360}, arm in {A0, AG, AU,
AD, AN}, seed, first_answer, rejected (0/1), retried (0/1), final_answer,
correct (0/1 exact three-way disposition vs engine-derived gold),
dangerous_wrong (0/1 per PROPOSED-ASM-1488), extracted_ok (0/1),
floor_uniform, floor_always_u, floor_cycle (per-item expected correctness of
the trivial retry policies, PROPOSED-ASM-1487), tokens_in, tokens_out,
rejection_msg_tokens, flops_formula, checker_us, scored (0/1; OOP probes 0)}
plus --sidecar <run-sidecar.json> with {fixtures_sha_run1, fixtures_sha_run2,
oop_probe_refusal_correctness, ad_coincidence_rate, gpu_hours, usd_total}.

Statistics: paired-item BCa bootstrap B=10000, PRNG seed 20260712, one-sided
alpha=0.05; Holm over {s1,s2,s3,s4,s5}; Wilson bounds for rate gates. Scored
135M rows only for every verdict-bearing quantity; r360 reports a SIGN only.
Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import argparse
import json
import math
import random

OUTPUT_FIELDS = [
    "/gates/fixtures_deterministic",
    "/gates/headroom_valid",
    "/gates/engagement_valid",
    "/gates/extraction_ok",
    "/gates/extraction_wilson_lb",
    "/gates/token_parity_valid",
    "/gates/token_parity_ratios",
    "/analysis/primary_lift_lb95",
    "/analysis/primary_pass",
    "/analysis/kill_u1_fired",
    "/analysis/kill_u2_fired",
    "/analysis/s1_content_over_bit_lb95",
    "/analysis/s1_pass",
    "/analysis/s2_vs_null_lb95",
    "/analysis/s2_pass",
    "/analysis/s3_deranged_recovery_ub95",
    "/analysis/s3_pass",
    "/analysis/s4_vs_gufo_lb95",
    "/analysis/s4_pass",
    "/analysis/s5_dangerous_wrong_increase_ub95",
    "/analysis/s5_pass",
    "/analysis/holm_order",
    "/analysis/acc_a0", "/analysis/acc_ag", "/analysis/acc_au",
    "/analysis/acc_ad", "/analysis/acc_an",
    "/analysis/dangerous_wrong_a0", "/analysis/dangerous_wrong_au",
    "/analysis/floor_max_trivial_au",
    "/analysis/acc_au_minus_a0_360m_sign",
    "/analysis/ad_coincidence_rate",
    "/analysis/oop_probe_refusal_correctness",
    "/analysis/per_family_breakdown",
    "/analysis/per_disposition_breakdown",
    "/analysis/rejection_rates",
    "/analysis/cost_ledger",
]

B = 10000
SEED = 20260712
ALPHA = 0.05
HOST = "r135"
DW_MARGIN = 0.02  # PROPOSED-ASM-1488
RECOVERY_BOUND = 0.30  # H-U3, rules-1/f2b bound verbatim
PARITY_BAND = 0.20  # PROPOSED-ASM-1484


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


def bca_lb(diffs, one_sided_alpha=ALPHA, b=B, seed=SEED):
    """One-sided BCa lower bound for the mean of paired diffs."""
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


def bca_ub(diffs):
    lb = bca_lb([-d for d in diffs])
    return None if lb is None else -lb


def scored(rows, host=HOST):
    return [r for r in rows if r.get("scored", 1) and r["host"] == host]


def per_item(rows, arm, key):
    """item_id -> seed-mean of key on scored rows for one arm."""
    acc = {}
    for r in rows:
        if r["arm"] != arm:
            continue
        acc.setdefault(r["item_id"], []).append(r[key])
    return {i: sum(v) / len(v) for i, v in acc.items()}


def paired(rows, arm_a, arm_b, key="correct", key_b=None):
    a = per_item(rows, arm_a, key)
    b = per_item(rows, arm_b, key_b or key)
    return [a[i] - b[i] for i in sorted(a) if i in b]


def mean_of(rows, arm, key="correct"):
    xs = [r[key] for r in rows if r["arm"] == arm]
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-records", required=True)
    ap.add_argument("--sidecar", required=True)
    args = ap.parse_args()
    rows = [json.loads(x) for x in open(args.run_records)]
    side = json.load(open(args.sidecar))
    s = scored(rows)

    # per-item max-trivial floor for AU (PROPOSED-ASM-1487): max over the
    # three analytic trivial retry policies, seed-mean per item.
    for r in rows:
        r["floor_max"] = max(r.get("floor_uniform", 0.0),
                             r.get("floor_always_u", 0.0),
                             r.get("floor_cycle", 0.0))

    # ---- gates (any failure => INSTRUMENT-INVALID) ----
    ex_ok = sum(r["extracted_ok"] for r in rows)
    ex_lb = wilson_lb(ex_ok, len(rows)) if rows else 0.0
    au_rej = mean_of(s, "AU", "rejected")
    msg_tok = {a: mean_of([r for r in s if r["rejected"]], a,
                          "rejection_msg_tokens")
               for a in ("AG", "AU", "AD", "AN")}
    parity = {a: (msg_tok[a] / msg_tok["AU"]
                  if msg_tok.get("AU") and msg_tok.get(a) is not None
                  else None)
              for a in ("AG", "AD", "AN")}
    gates = {
        "fixtures_deterministic": bool(
            side.get("fixtures_sha_run1")
            and side["fixtures_sha_run1"] == side.get("fixtures_sha_run2")),
        "headroom_valid": (mean_of(s, "A0") is not None
                           and mean_of(s, "A0") <= 0.85),
        "engagement_valid": (au_rej is not None
                             and 0.02 <= au_rej <= 0.98
                             and any(r["arm"] == "AU" and r["retried"]
                                     for r in s)),
        "extraction_ok": ex_lb >= 0.90,
        "extraction_wilson_lb": ex_lb,
        "token_parity_valid": all(
            v is not None and abs(v - 1.0) <= PARITY_BAND
            for v in parity.values()),
        "token_parity_ratios": parity,
    }

    # ---- primary + Holm secondaries ----
    primary = bca_lb(paired(s, "AU", "A0"))
    s1 = bca_lb(paired(s, "AU", "AU", key="correct", key_b="floor_max"))
    s2 = bca_lb(paired(s, "AU", "AN"))
    d_ad = paired(s, "AD", "A0")
    d_au = paired(s, "AU", "A0")
    s3_rec = None
    if d_ad and d_au:
        # conservative recovery ratio: UB(AD lift) / LB(AU lift), rules-1 form
        ub_ad = bca_ub(d_ad)
        lb_au = bca_lb(d_au)
        if ub_ad is not None and lb_au is not None and lb_au > 0:
            s3_rec = ub_ad / lb_au
    s4 = bca_lb(paired(s, "AU", "AG"))
    s5 = bca_ub(paired(s, "AU", "A0", key="dangerous_wrong"))

    r360 = scored(rows, host="r360")
    sign360 = None
    if r360:
        d = paired(r360, "AU", "A0")
        m = sum(d) / len(d) if d else None
        sign360 = None if m is None else (1 if m > 0 else (-1 if m < 0 else 0))

    def breakdown(field):
        out = {}
        for r in s:
            out.setdefault(r[field], {}).setdefault(r["arm"], []).append(
                r["correct"])
        return {k: {a: sum(v) / len(v) for a, v in arms.items()}
                for k, arms in sorted(out.items())}

    primary_pass = primary is not None and primary > 0
    s5_pass = s5 is not None and s5 < DW_MARGIN
    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_pass": primary_pass,
        "kill_u1_fired": primary is not None and primary <= 0,
        "kill_u2_fired": not s5_pass,
        "s1_content_over_bit_lb95": s1,
        "s1_pass": s1 is not None and s1 > 0,  # CLAIM CAP only, never verdict
        "s2_vs_null_lb95": s2,
        "s2_pass": s2 is not None and s2 > 0,
        "s3_deranged_recovery_ub95": s3_rec,
        "s3_pass": s3_rec is not None and s3_rec < RECOVERY_BOUND,
        "s4_vs_gufo_lb95": s4,
        "s4_pass": s4 is not None and s4 > 0,  # CLAIM CAP only, never verdict
        "s5_dangerous_wrong_increase_ub95": s5,
        "s5_pass": s5_pass,
        "holm_order": ["s1", "s2", "s3", "s4", "s5"],
        "acc_a0": mean_of(s, "A0"), "acc_ag": mean_of(s, "AG"),
        "acc_au": mean_of(s, "AU"), "acc_ad": mean_of(s, "AD"),
        "acc_an": mean_of(s, "AN"),
        "dangerous_wrong_a0": mean_of(s, "A0", "dangerous_wrong"),
        "dangerous_wrong_au": mean_of(s, "AU", "dangerous_wrong"),
        "floor_max_trivial_au": mean_of(s, "AU", "floor_max"),
        "acc_au_minus_a0_360m_sign": sign360,
        "ad_coincidence_rate": side.get("ad_coincidence_rate"),
        "oop_probe_refusal_correctness":
            side.get("oop_probe_refusal_correctness"),
        "per_family_breakdown": breakdown("family"),
        "per_disposition_breakdown": breakdown("gold"),
        "rejection_rates": {a: mean_of(s, a, "rejected")
                            for a in ("AG", "AU", "AD", "AN")},
        "cost_ledger": {  # DESCRIPTIVE only; no efficiency claim (design §6)
            "gpu_hours": side.get("gpu_hours"),
            "usd_total": side.get("usd_total"),
            "tokens_in_total": sum(r.get("tokens_in", 0) for r in rows),
            "tokens_out_total": sum(r.get("tokens_out", 0) for r in rows),
            "flops_formula_total": sum(r.get("flops_formula", 0)
                                       for r in rows),
            "checker_us_mean": (lambda xs: sum(xs) / len(xs) if xs else None)(
                [r.get("checker_us", 0) for r in rows
                 if r["arm"] != "A0"]),
            "usd_per_query": (side["usd_total"] / len(rows)
                              if side.get("usd_total") and rows else None),
        },
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
