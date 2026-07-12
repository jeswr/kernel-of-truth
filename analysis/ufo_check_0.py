#!/usr/bin/env python3
"""ufo-check-0 pre-registered analysis (pure function over run records).

Design: docs/next/design/ufo-check-0.md §6 (endpoints, gates, kills).
Record: registry/experiments/ufo-check-0.json (kot-reg/2, ORACLE-DIAGNOSTIC).
ASMs: PROPOSED-ASM-1480..1495 (registered centrally at freeze).

Input: --run-records <run-records-ufo0.jsonl>, one row per item x arm x host
x seed: {item_id, family, gold, host in {r135, r360}, arm in {A0, AG, AU,
AD, AN}, seed, first_answer, rejected (0/1), retried (0/1), final_answer,
correct (0/1 exact three-way disposition vs engine-derived gold),
dangerous_wrong (0/1 per PROPOSED-ASM-1488), extracted_ok (0/1),
floor_uniform, floor_always_u, floor_cycle (per-item analytic trivial retry
policy expectations, PROPOSED-ASM-1487), tokens_in, tokens_out,
rejection_msg_tokens, flops_formula, checker_us, scored (0/1; OOP probes 0)}
plus --sidecar <run-sidecar.json> with {fixtures_sha_run1, fixtures_sha_run2,
expected: {hosts, arms, seeds, n_items, n_scored, all_item_ids_sha256,
scored_item_ids_sha256}, oop_probe_refusal_correctness, ad_coincidence_rate,
ad_coincidence_ok, an_representation_match, an_nondegenerate,
rejection_message_clean, gpu_hours, usd_total}.

Statistics (review fix 2 — implemented, not narrated): paired-item BCa
bootstrap B=10000, PRNG seed 20260712, one-sided alpha=0.05; bootstrap-
INVERSION p-values for every secondary (the smallest alpha at which the
registered one-sided BCa decision rule fires — for s3 this inverts the
registered conservative ratio rule UB_a(lift AD)/LB_a(lift AU) < 0.30 by
bisection over a); HOLM step-down over {s1..s5} (adjusted p <= 0.05 is the
operative pass for every secondary); Wilson bounds for rate gates. The
primary is standalone (exactly one primary endpoint): decision = LB95 > 0,
its inversion p reported. Scored 135M rows only for every verdict-bearing
quantity; r360 reports a SIGN only.

Completeness gate (review fix 6): the exact item x arm x host x seed
factorial with the fixed 600-item scored set is TERMINALLY gated — missing,
duplicate, or unbalanced rows are INSTRUMENT-INVALID, never silently
accepted.

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import argparse
import hashlib
import json
import math
import random

OUTPUT_FIELDS = [
    "/gates/fixtures_deterministic",
    "/gates/completeness_valid",
    "/gates/headroom_valid",
    "/gates/engagement_valid",
    "/gates/extraction_ok",
    "/gates/extraction_wilson_lb",
    "/gates/token_parity_valid",
    "/gates/token_parity_ratios",
    "/gates/an_representation_match",
    "/gates/an_nondegenerate",
    "/gates/ad_coincidence_ok",
    "/gates/rejection_message_clean",
    "/analysis/primary_lift_lb95",
    "/analysis/primary_p",
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
    "/analysis/p_values",
    "/analysis/holm_adjusted_p",
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
    "/analysis/retry_rates",
    "/analysis/cost_ledger",
]

B = 10000
SEED = 20260712
ALPHA = 0.05
HOST = "r135"
DW_MARGIN = 0.02       # PROPOSED-ASM-1488
RECOVERY_BOUND = 0.30  # H-U3, rules-1/f2b bound verbatim
PARITY_BAND = 0.20     # PROPOSED-ASM-1484
ARMS = ("A0", "AG", "AU", "AD", "AN")
P_FLOOR = 1.0 / (B + 1)


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


class Boot:
    """Cached BCa machinery for the mean of one paired diff vector:
    bootstrap draws are computed ONCE (B=10000, deterministic sub-seed from
    the registered PRNG seed + a stable tag), then bounds at ARBITRARY alpha
    and the CI-inversion p-value are pure lookups — this is what lets the s3
    ratio rule be inverted by bisection without re-resampling."""

    def __init__(self, diffs, tag):
        self.n = len(diffs)
        if self.n == 0:
            self.ok = False
            return
        self.ok = True
        sub = int(hashlib.sha256(("%d|%s" % (SEED, tag)).encode())
                  .hexdigest()[:12], 16)
        rng = random.Random(sub)
        self.theta = sum(diffs) / self.n
        self.boots = sorted(sum(rng.choices(diffs, k=self.n)) / self.n
                            for _ in range(B))
        prop = sum(1 for x in self.boots if x < self.theta) / B
        self.z0 = _norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
        if self.n > 1:
            s = sum(diffs)
            jack = [(s - d) / (self.n - 1) for d in diffs]
        else:
            jack = [self.theta]
        jm = sum(jack) / len(jack)
        num = sum((jm - j) ** 3 for j in jack)
        den = 6 * (sum((jm - j) ** 2 for j in jack) ** 1.5) or 1e-12
        self.a = num / den

    def lb(self, alpha=ALPHA):
        """One-sided BCa LOWER bound at level alpha."""
        if not self.ok:
            return None
        zq = _norm_ppf(min(max(alpha, 1e-9), 1 - 1e-9))
        den = 1 - self.a * (self.z0 + zq)
        if den <= 0:
            return self.boots[0]
        adj = _norm_cdf(self.z0 + (self.z0 + zq) / den)
        idx = min(max(int(adj * B), 0), B - 1)
        return self.boots[idx]

    def p_gt0(self):
        """Bootstrap-inversion one-sided p for H1: mean > 0 — the smallest
        alpha at which lb(alpha) > 0 (BCa CI inversion, closed form)."""
        if not self.ok:
            return None
        g = sum(1 for x in self.boots if x <= 0) / B
        if g <= 0:
            return P_FLOOR
        if g >= 1:
            return 1.0
        w = _norm_ppf(g) - self.z0
        den = 1 + self.a * w
        if den <= 0:
            return 1.0
        p = _norm_cdf(w / den - self.z0)
        return min(max(p, P_FLOOR), 1.0)


def boot_ub(diffs, tag):
    """UPPER-bound machinery via negation (matches the registered
    conservative-ratio convention: UB(x) = -LB(-x))."""
    return Boot([-d for d in diffs], tag + "|neg")


def scored(rows, host=HOST):
    return [r for r in rows if r.get("scored", 1) and r["host"] == host]


def per_item(rows, arm, key):
    """item_id -> seed-mean of key on the given rows for one arm."""
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


def holm(p_raw):
    """Holm step-down adjusted p-values over the named family."""
    items = sorted(((p if p is not None else 1.0), k)
                   for k, p in p_raw.items())
    m = len(items)
    adj, run = {}, 0.0
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = run
    order = [k for _p, k in items]
    return adj, order


def completeness(rows, side):
    """TERMINAL completeness gate (review fix 6): exact factorial, no
    duplicates, identical item set per cell, fixed scored set."""
    exp = side.get("expected") or {}
    hosts = exp.get("hosts") or []
    arms = exp.get("arms") or []
    seeds = exp.get("seeds") or []
    n_items = exp.get("n_items")
    n_scored_exp = exp.get("n_scored")
    if not (hosts and arms and seeds and n_items and n_scored_exp):
        return False
    keys = [(r["item_id"], r["arm"], r["host"], r["seed"]) for r in rows]
    if len(keys) != len(set(keys)):
        return False  # duplicate rows
    if len(rows) != n_items * len(arms) * len(hosts) * len(seeds):
        return False
    cells = {}
    for r in rows:
        cells.setdefault((r["arm"], r["host"], r["seed"]),
                         []).append(r)
    if len(cells) != len(arms) * len(hosts) * len(seeds):
        return False
    for (arm, host, seed), cr in sorted(cells.items()):
        if arm not in arms or host not in hosts or seed not in seeds:
            return False
        ids = sorted(r["item_id"] for r in cr)
        if len(ids) != n_items:
            return False
        sha = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
        if sha != exp.get("all_item_ids_sha256"):
            return False
        sids = sorted(r["item_id"] for r in cr if r.get("scored", 1))
        if len(sids) != n_scored_exp:
            return False
        ssha = hashlib.sha256("\n".join(sids).encode("utf-8")).hexdigest()
        if ssha != exp.get("scored_item_ids_sha256"):
            return False
    return True


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
        "completeness_valid": completeness(rows, side),
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
        # MEASURED fixture-side gates (review fix 4), carried by the runner
        # from fixtures-meta.json and re-verified in-run:
        "an_representation_match": bool(side.get("an_representation_match")),
        "an_nondegenerate": bool(side.get("an_nondegenerate")),
        "ad_coincidence_ok": bool(side.get("ad_coincidence_ok")),
        "rejection_message_clean": bool(side.get("rejection_message_clean")),
    }

    # ---- primary (standalone) + Holm secondaries (review fix 2) ----
    b_primary = Boot(paired(s, "AU", "A0"), "primary")
    primary = b_primary.lb()
    primary_p = b_primary.p_gt0()

    b_s1 = Boot(paired(s, "AU", "AU", key="correct", key_b="floor_max"),
                "s1")
    b_s2 = Boot(paired(s, "AU", "AN"), "s2")
    b_s4 = Boot(paired(s, "AU", "AG"), "s4")
    b_s5 = Boot([DW_MARGIN - d
                 for d in paired(s, "AU", "A0", key="dangerous_wrong")],
                "s5")  # H1: dw increase < margin <=> mean(margin - d) > 0

    d_ad = paired(s, "AD", "A0")
    d_au = paired(s, "AU", "A0")
    b_ad_ub = boot_ub(d_ad, "s3ad")
    b_au_lb = Boot(d_au, "s3au")

    def s3_fires(alpha):
        """The registered conservative ratio rule at level alpha:
        UB_a(lift AD) / LB_a(lift AU) < 0.30 with LB_a(lift AU) > 0."""
        if not (b_ad_ub.ok and b_au_lb.ok):
            return False
        lb_au = b_au_lb.lb(alpha)
        if lb_au is None or lb_au <= 0:
            return False
        ub_ad = -b_ad_ub.lb(alpha)
        return (ub_ad / lb_au) < RECOVERY_BOUND

    # registered 95% statistic (reported)
    s3_rec = None
    if b_ad_ub.ok and b_au_lb.ok:
        lb_au95 = b_au_lb.lb(ALPHA)
        if lb_au95 is not None and lb_au95 > 0:
            s3_rec = (-b_ad_ub.lb(ALPHA)) / lb_au95
    # bootstrap-inversion p for s3: smallest alpha at which the registered
    # rule fires (monotone in alpha; bisection).
    if s3_fires(0.4999):
        lo, hi = P_FLOOR, 0.4999
        if s3_fires(lo):
            s3_p = lo
        else:
            for _ in range(50):
                mid = (lo + hi) / 2
                if s3_fires(mid):
                    hi = mid
                else:
                    lo = mid
            s3_p = hi
    else:
        s3_p = 1.0

    p_raw = {"s1": b_s1.p_gt0(), "s2": b_s2.p_gt0(), "s3": s3_p,
             "s4": b_s4.p_gt0(), "s5": b_s5.p_gt0()}
    p_adj, holm_order = holm(p_raw)
    passes = {k: (p_adj[k] is not None and p_adj[k] <= ALPHA)
              for k in p_raw}

    s1 = b_s1.lb()
    s2 = b_s2.lb()
    s4 = b_s4.lb()
    s5 = (DW_MARGIN - b_s5.lb()) if b_s5.ok and b_s5.lb() is not None \
        else None  # back-transform: UB95 of the dw increase

    r360 = scored(rows, host="r360")
    sign360 = None
    if r360:
        d = paired(r360, "AU", "A0")
        m = sum(d) / len(d) if d else None
        sign360 = None if m is None else (1 if m > 0 else (-1 if m < 0
                                                           else 0))

    def breakdown(field):
        out = {}
        for r in s:
            out.setdefault(r[field], {}).setdefault(r["arm"], []).append(
                r["correct"])
        return {k: {a: sum(v) / len(v) for a, v in arms.items()}
                for k, arms in sorted(out.items())}

    primary_pass = primary is not None and primary > 0
    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_p": primary_p,
        "primary_pass": primary_pass,
        "kill_u1_fired": primary is None or primary <= 0,
        "kill_u2_fired": not passes["s5"],
        "s1_content_over_bit_lb95": s1,
        "s1_pass": passes["s1"],  # CLAIM CAP only, never verdict-bearing
        "s2_vs_null_lb95": s2,
        "s2_pass": passes["s2"],
        "s3_deranged_recovery_ub95": s3_rec,
        "s3_pass": passes["s3"],
        "s4_vs_gufo_lb95": s4,
        "s4_pass": passes["s4"],  # CLAIM CAP only, never verdict-bearing
        "s5_dangerous_wrong_increase_ub95": s5,
        "s5_pass": passes["s5"],
        "p_values": p_raw,
        "holm_adjusted_p": p_adj,
        "holm_order": holm_order,
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
        "retry_rates": {a: mean_of(s, a, "retried")
                        for a in ("AG", "AU", "AD", "AN")},
        "cost_ledger": {  # DESCRIPTIVE only; no efficiency claim (design §6)
            "gpu_hours": side.get("gpu_hours"),
            "usd_total": side.get("usd_total"),
            "tokens_in_total": sum(r.get("tokens_in", 0) for r in rows),
            "tokens_out_total": sum(r.get("tokens_out", 0) for r in rows),
            "flops_formula_total": sum(r.get("flops_formula", 0)
                                       for r in rows),
            "checker_us_mean": (lambda xs: sum(xs) / len(xs) if xs
                                else None)(
                [r.get("checker_us", 0) for r in rows
                 if r["arm"] != "A0"]),
            "usd_per_query": (side["usd_total"] / len(rows)
                              if side.get("usd_total") and rows else None),
        },
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
