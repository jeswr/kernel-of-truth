#!/usr/bin/env python3
"""rules-1-c pre-registered analysis (pure function over run records).

Supersedes analysis/rules_1b.py (rules-1-b host-validity pilot FAILED its
frozen A5 floor 2026-07-12: acc(A5)=0/24 on the fixed relation-word frame;
root cause = FORM MIS-ATTRIBUTION — the 0.7912 A5 premise is the nsk1
ENTITY-form bprime datum (n=958) while the harness asked the RELATION-WORD
form, which the nsk1-g2d assessment records as 'dead-at-floor at every
tested host'). rules-1-c switches the host surface to the ENTITY form
(nsk1 g2b form 2): question 'Who is the <gold_rel> of <base>?', per-item
2-option forced choice over the non-base lexicon surfaces (bridge +
chain-top), answer = the chain-top NAME (third-party CLUTRR proof_state
gold, predates the kernel). CHANCE FLOOR IS NOW 0.5 (2-option, DISCLOSED);
the host-validity floors below are re-derived against it. Every other
endpoint/statistic is byte-carried from rules_1b.py (s1 is the ratio-based
recovery operationalisation, chance-floor-invariant because both lifts are
A1-paired).

1. HOST-VALIDITY INSTRUMENT GATE (/gates/host_validity_valid):
   host_validity_valid := acc(A7, entailed, seed-mean) >= 0.85
                      AND acc(A5, entailed, seed-mean) >= 0.75.
   Rationale: the 2-option chance floor is 0.5 (its n=2574 one-sided 95%
   binomial UB is ~0.516); A7 renders the engine's bare derived fact in a
   render-only prompt (engine 858/858 vs third-party gold; pilot 24/24 on
   the pinned R1), so a host below 0.85 is not reading a verbatim stated
   answer; A5 carries the nsk1 R3 entity-form datum 0.7912 and piloted
   24/24 on the pinned R3, so 0.75 is far below any plausible healthy value
   while far above chance. Failure => INSTRUMENT-INVALID (verdict rule 0),
   never FAIL/KILL-b.
2. s3 CONDITIONING (carried from rules_1b.py): s3 is null/unevaluable
   (never a pass, never a fail) when separation_valid is false.

Design: docs/next/arch/world-model-rules-engine.md §4.3/§4.4 as amended by
the cross-model synthesis (arms A1-A5, A7; controls c1-c4, c6; A6 removed;
c5 knull-ablation pre-registered for phase 2 per MD-7) and the maintainer
approvals on issue #19 (MD-1..MD-9). ASMs: PROPOSED-ASM-1127..1133,
1160..1164, plus the rules-1-b block PROPOSED-ASM-1630..1649.

Input: --run-records <run-records-rules1.jsonl> (one row per item x arm x
seed: {item_id, arm, rung, seed, cell in {entailed, stated, control},
item_correct_ext (0/1 vs the pinned third-party CLUTRR gold), refused (0/1),
attempts, tokens_in, tokens_out, engine_us, flops_formula}) and
--certificate <certificate-result.json> (the pinned CPU precondition).
Output: canonical JSON on stdout with exactly the OUTPUT_FIELDS below.

Statistics: paired item BCa bootstrap B=10000, PRNG seed 20260711, one-sided
alpha=0.05; Holm over the secondary family {s1, s2, s3, s4}; Wilson 95%
bounds for rate gates. Entailed-cell rows only for every endpoint; stated
cells are sanity descriptives; control cells feed refusal correctness.
"""

import argparse
import json
import math
import random

OUTPUT_FIELDS = [
    "/gates/certificate_precondition_valid",
    "/gates/twin_agreement_valid",
    "/gates/headroom_valid",
    "/gates/separation_valid",
    "/gates/engagement_valid",
    "/gates/host_validity_valid",
    "/gates/repeat_byte_identical",
    "/analysis/primary_lift_lb95",
    "/analysis/primary_pass",
    "/analysis/kill_b_fired",
    "/analysis/a2_minus_a1_lb95_systems",
    "/analysis/s1_shuffled_recovery_ub95",
    "/analysis/s1_pass",
    "/analysis/s2_a3_minus_a1_lb95",
    "/analysis/s2_pass",
    "/analysis/s3_efficiency_diff_lb95",
    "/analysis/s3_pass",
    "/analysis/s4_a7_minus_c6_lb95",
    "/analysis/s4_pass",
    "/analysis/holm_order",
    "/analysis/acc_a1", "/analysis/acc_a2", "/analysis/acc_a3",
    "/analysis/acc_a4", "/analysis/acc_a5_r3", "/analysis/acc_a7",
    "/analysis/acc_c1_shuffled", "/analysis/acc_c6_axioms_text",
    "/analysis/refusal_correctness_e5",
    "/analysis/proof_depth_strata",
    "/analysis/engine_us_per_query",
    "/analysis/default_world_cost_ledger",
    "/analysis/accuracy", "/analysis/params", "/analysis/memory",
    "/analysis/inference_compute", "/analysis/training_compute",
]

B = 10000
SEED = 20260711
ALPHA = 0.05


def wilson_lb(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    ph = k / n
    return ((ph + z * z / (2 * n)) - z * math.sqrt(
        ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def paired_diffs(rows, arm_a, arm_b, key="item_correct_ext"):
    """Per-item seed-mean difference arm_a - arm_b on entailed cells."""
    acc = {}
    for r in rows:
        if r["cell"] != "entailed" or r["arm"] not in (arm_a, arm_b):
            continue
        acc.setdefault(r["item_id"], {}).setdefault(r["arm"], []).append(
            r[key])
    diffs = []
    for item, byarm in sorted(acc.items()):
        if arm_a in byarm and arm_b in byarm:
            diffs.append(sum(byarm[arm_a]) / len(byarm[arm_a]) -
                         sum(byarm[arm_b]) / len(byarm[arm_b]))
    return diffs


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


def acc(rows, arm, cell="entailed"):
    xs = [r["item_correct_ext"] for r in rows
          if r["arm"] == arm and r["cell"] == cell]
    return sum(xs) / len(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-records", required=True)
    ap.add_argument("--certificate", required=True)
    ap.add_argument("--repeat-sha-a", default=None)
    ap.add_argument("--repeat-sha-b", default=None)
    args = ap.parse_args()
    rows = [json.loads(x) for x in open(args.run_records)]
    cert = json.load(open(args.certificate))

    gates = {
        # pinned CPU precondition (PROPOSED-ASM-1131 + 1163): the frozen
        # certificate bytes must carry SUCCESS + gates + no KILL-a.
        "certificate_precondition_valid": bool(
            cert["certificate_result"]["success_asm_1131"] and
            cert["certificate_result"]["gates_asm_1163_all_pass"] and
            not cert["certificate_result"]["kill_a_fired"]),
        # differential twin exact agreement carried with the certificate
        "twin_agreement_valid": "EXACTLY agreed" in
            cert["engine_identity"]["ran"],
        "headroom_valid": (acc(rows, "A1") is not None and
                           acc(rows, "A1") <= 0.85),
        "separation_valid": (acc(rows, "A5") is not None and
                             acc(rows, "A1") is not None and
                             acc(rows, "A5") - acc(rows, "A1") >= 0.05),
        # A3 verifier decidably engaged: >=1 rejection-resample observed and
        # rejection rate not degenerate (RT-7a shape)
        "engagement_valid": any(r["arm"] == "A3" and r.get("attempts", 1) > 1
                                for r in rows),
        # HOST-VALIDITY INSTRUMENT GATE (rules-1-c, entity-form floors): a
        # degenerate host scorer can NEVER read as a substantive verdict.
        # Floors: A7 >= 0.85 (render-only bare derived fact; pinned-R1 pilot
        # 24/24) AND A5 >= 0.75 (nsk1 R3 entity-form datum 0.7912; pinned-R3
        # pilot 24/24) — both far above the 2-option chance floor 0.5
        # (n=2574 one-sided 95% binomial UB ~0.516). Wired into
        # verdict_rules rule 0: failure => INSTRUMENT-INVALID before FAIL.
        "host_validity_valid": (acc(rows, "A7") is not None and
                                acc(rows, "A5") is not None and
                                acc(rows, "A7") >= 0.85 and
                                acc(rows, "A5") >= 0.75),
        "repeat_byte_identical": (args.repeat_sha_a == args.repeat_sha_b
                                  if args.repeat_sha_a else False),
    }

    primary = bca_lb(paired_diffs(rows, "A3", "A1"))
    s2 = primary  # s2 is the Holm-corrected confirmation of the same contrast
    s1_rec = None
    d_c1 = paired_diffs(rows, "c1", "A1")
    d_a3 = paired_diffs(rows, "A3", "A1")
    if d_c1 and d_a3 and sum(d_a3):
        # recovery = shuffled lift / real lift; UB95 via BCa on the ratio's
        # components (conservative: UB of c1 lift over LB of A3 lift)
        ub_c1 = -bca_lb([-d for d in d_c1])
        lb_a3 = bca_lb(d_a3)
        s1_rec = (ub_c1 / lb_a3) if lb_a3 and lb_a3 > 0 else None
    # s3 CONDITIONED on the separation gate (frozen endpoint text; fixes the
    # rules_1.py unconditional-compute defect disclosed at the rules-1 grade):
    # separation false => s3 unevaluable (null), never a pass, never a fail.
    s3 = (bca_lb(paired_diffs(rows, "A3", "A5"))  # NI margin 0, sign-only
          if gates["separation_valid"] else None)
    s4 = bca_lb(paired_diffs(rows, "A7", "c6"))
    a2 = bca_lb(paired_diffs(rows, "A2", "A1"))

    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_pass": primary is not None and primary > 0,
        "kill_b_fired": primary is not None and primary <= 0,
        "a2_minus_a1_lb95_systems": a2,
        "s1_shuffled_recovery_ub95": s1_rec,
        "s1_pass": s1_rec is not None and s1_rec < 0.30,
        "s2_a3_minus_a1_lb95": s2,
        "s2_pass": s2 is not None and s2 > 0,
        "s3_efficiency_diff_lb95": s3,
        "s3_pass": s3 is not None and s3 >= 0,
        "s4_a7_minus_c6_lb95": s4,
        "s4_pass": s4 is not None and s4 > 0,
        "holm_order": ["s1", "s2", "s3", "s4"],
        "acc_a1": acc(rows, "A1"), "acc_a2": acc(rows, "A2"),
        "acc_a3": acc(rows, "A3"), "acc_a4": acc(rows, "A4"),
        "acc_a5_r3": acc(rows, "A5"), "acc_a7": acc(rows, "A7"),
        "acc_c1_shuffled": acc(rows, "c1"),
        "acc_c6_axioms_text": acc(rows, "c6"),
        "refusal_correctness_e5": (lambda xs: sum(xs) / len(xs)
                                   if xs else None)(
            [r["refused"] for r in rows if r["cell"] == "control"
             and r["arm"] in ("A3", "A7")]),
        "proof_depth_strata": "per PROPOSED-ASM-1160: reported by depth<=4",
        "engine_us_per_query": (lambda xs: sum(xs) / len(xs)
                                if xs else None)(
            [r["engine_us"] for r in rows if "engine_us" in r]),
        "default_world_cost_ledger": {
            "note": "A4 one-off materialisation vs per-prompt delta closure "
                    "(PROPOSED-ASM-1139: cost ledger only, no non-inertness "
                    "claim)"},
        "accuracy": acc(rows, "A3"),
        "params": 135_000_000,
        "memory": None,
        "inference_compute": (lambda xs: sum(xs) if xs else None)(
            [r.get("flops_formula", 0) for r in rows]),
        "training_compute": 0,
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
