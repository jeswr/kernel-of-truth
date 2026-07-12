#!/usr/bin/env python3
"""rules-2 pre-registered analysis, GO revision (pure function over run
records) — the SUCCESSOR of analysis/rules_2.py (sha 782bc9eb...), which was
pinned in the pre-GO DRAFT and in the blocking-pilot artifact and is retained
UNEDITED as history (never edit a pinned script; PROPOSED-ASM-1853).

GO finalisation (maintainer issue #24 decision (C), 2026-07-12; design doc
Appendix C; PROPOSED-ASM-1847..1859): the B4 engine-at-inference comparator
arm and the s3' gap-closure leg are STRUCK. The blocking instrument pilot
(PILOT-PASS-WITH-FLAGS, poc/rules-2/results-incoming/20260712-165344-
instrpilot) measured the imported rules-1-c A3 verify-retry channel VACUOUS
at the 2-option entity operating point (IP-4: attempts=1 everywhere,
PROPOSED-ASM-1818 confirming PROPOSED-ASM-1808) — the verify-retry question
is settled UN-INSTRUMENTABLE at 2-option scale and B4 rows would be
attempt-0 decoys. Consequences implemented here:

  * s3' is REMOVED from the secondary family: Holm runs over
    {s1', s2', s4'} (m=3 when all evaluable). No --rules1-primary-lb input.
  * All B4 / cell='entailed2' (common 2-option gap) surfaces are gone: the
    runner no longer emits them; this script no longer reads them.
  * The engine-at-inference price column is carried DESCRIPTIVELY from the
    landed rules-1-c campaign ledger (cross-campaign, disclosed pointer —
    never recomputed here); B5 (R3 no-fine-tune) remains the in-campaign
    efficiency comparator. NO break-even N* is computed (its B4 leg died
    with the arm); NO direction presumed (PROPOSED-ASM-1429).
  * The train-time internalisation primary (B2 - B0) and the s1'/s2'/s4'
    machinery are UNCHANGED from the superseded script (statistics verbatim:
    two-stage FT-seed x item BCa bootstrap, B=10000, PRNG seed 20260712,
    SESOI 0.05 band, REAL Holm step-down).

The kernel-vs-plain-dictionary attribution question (ASM-1138 claim cap)
is NOT answered by this campaign's arms: it is carried by the MANDATORY
sibling campaign registry/experiments/rules-2-knull.json (knull-sourced
closure; $0 CPU byte-equivalence leg first — PROPOSED-ASM-1849..1852).

Input:
  --run-records  run-records-rules2.jsonl rows {item_id, arm, rung, seed,
                 cell in {entailed, control, s_mem, s_held, stated,
                 refusal_train, timeout}, item_correct_ext, refused,
                 attempts, tokens_in, flops_formula, engine_us?}
  --results      results-rules2.json (pins_verified, repeat_shas,
                 training_ledger, eval_ledger, usd table, c8_gate echo)
  --c8           poc/rules-2/results/c8-result.json (the G2 artifact)

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
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
    "/analysis/primary_band",
    "/analysis/kill_d_fired",
    "/analysis/s1p_shuffled_recovery_ub95",
    "/analysis/s1p_pass",
    "/analysis/s2p_exposure_lb95",
    "/analysis/s2p_pass",
    "/analysis/s4p_stated_delta",
    "/analysis/s4p_refusal_delta",
    "/analysis/s4p_side_effect_flag",
    "/analysis/s4p_pass",
    "/analysis/holm_order",
    "/analysis/holm",
    "/analysis/acc_b0_sout", "/analysis/acc_b1_sout",
    "/analysis/acc_b2_sout", "/analysis/acc_b3_sout",
    "/analysis/acc_b5_sout",
    "/analysis/acc_c1p_sout",
    "/analysis/strata_profile",
    "/analysis/rung_sign_descriptive",
    "/analysis/refusal_correctness_control",
    "/analysis/b3_minus_b2_descriptive",
    "/analysis/ft_seed_variance",
    "/analysis/efficiency_ledger",
    "/analysis/accuracy", "/analysis/params", "/analysis/memory",
    "/analysis/inference_compute", "/analysis/training_compute",
]

B = 10000
SEED = 20260712
ALPHA = 0.05
SESOI = 0.05          # registered smallest_effect_of_interest (primary):
                      # PASS iff LB95 > SESOI; KILL-d iff LB95 <= 0;
                      # 0 < LB95 <= SESOI => INCONCLUSIVE band (review fix 3)
GUARD_MARGIN = 0.05   # s4' degradation guard margin (ASM-1430)
S1_RECOVERY_UB = 0.30  # s1' ceiling (ASM-1426, estate H-STRUCT verbatim)
HOLM_ORDER = ["s1p", "s2p", "s4p"]  # registered family (s3' STRUCK,
                                    # issue #24 (C) + PROPOSED-ASM-1848)


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


# ---------------------------------------------------------------------------
# Paired per-item x per-FT-seed data collection (fail-closed grid)
# ---------------------------------------------------------------------------
def collect(rows, arm, cell, rung="R1", key="item_correct_ext"):
    """{item_id: {seed: value}} for one (arm, cell, rung). Duplicate rows for
    the same (item, seed) collapse to their mean (there are none by
    construction; the repeat pass is scored emit=False)."""
    acc = {}
    for r in rows:
        if r["arm"] == arm and r["cell"] == cell and r.get("rung") == rung:
            acc.setdefault(r["item_id"], {}).setdefault(
                r["seed"], []).append(r[key])
    return {i: {s: sum(v) / len(v) for s, v in bs.items()}
            for i, bs in acc.items()}


def _grid(d, what):
    """Fail-closed complete seed grid: every item carries the same seed set
    (a ragged grid is a harness bug, never silently averaged over)."""
    if not d:
        return [], []
    seeds = sorted(next(iter(d.values())))
    for i, bs in d.items():
        if sorted(bs) != seeds:
            raise SystemExit("ERR_SEED_GRID: %s item %s has seeds %s != %s"
                             % (what, i, sorted(bs), seeds))
    return sorted(d), seeds


class BootContrast:
    """Two-stage paired bootstrap of mean(seed-mean(a) - seed-mean(b)) over
    shared items (review fix 3): each replicate resamples the FT-seed axis
    per arm (cluster bootstrap, independent between arms — a seed label is
    a distinct training run, not a pairing key) and then the item axis.
    BCa: z0 from the two-stage bootstrap distribution; acceleration from
    the item-level jackknife of seed-mean diffs (disclosed approximation)."""

    def __init__(self, da, db, name, b=B):
        items_a, seeds_a = _grid(da, name + "/a")
        items_b, seeds_b = _grid(db, name + "/b")
        self.items = sorted(set(items_a) & set(items_b))
        self.n = len(self.items)
        self.name = name
        if self.n == 0:
            self.theta = None
            return
        A = [[da[i][s] for s in seeds_a] for i in self.items]
        Bm = [[db[i][s] for s in seeds_b] for i in self.items]
        ka, kb = len(seeds_a), len(seeds_b)
        d = [sum(A[i]) / ka - sum(Bm[i]) / kb for i in range(self.n)]
        self.theta = sum(d) / self.n
        rng = random.Random("%d|%s" % (SEED, name))
        n = self.n
        boots = []
        for _ in range(b):
            sa = ([rng.randrange(ka) for _ in range(ka)] if ka > 1
                  else [0])
            sb = ([rng.randrange(kb) for _ in range(kb)] if kb > 1
                  else [0])
            tot = 0.0
            for _j in range(n):
                i = rng.randrange(n)
                tot += (sum(A[i][s] for s in sa) / len(sa)
                        - sum(Bm[i][s] for s in sb) / len(sb))
            boots.append(tot / n)
        self.boots = sorted(boots)
        self.b = b
        # degenerate distribution (every paired diff identical => zero
        # bootstrap variance): the BCa z0 estimate is undefined there; the
        # statistic is known exactly and lb/ub/p short-circuit on theta.
        self.degenerate = (self.boots[0] == self.boots[-1]
                           and min(d) == max(d))
        prop = sum(1 for x in self.boots if x < self.theta) / b
        self.z0 = _norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
        jack = ([(sum(d) - x) / (n - 1) for x in d] if n > 1
                else [self.theta])
        jm = sum(jack) / len(jack)
        num = sum((jm - j) ** 3 for j in jack)
        den = 6 * (sum((jm - j) ** 2 for j in jack) ** 1.5) or 1e-12
        self.a = num / den

    def lb(self, alpha=ALPHA):
        """One-sided BCa lower bound at level alpha."""
        if self.theta is None:
            return None
        if self.degenerate:
            return self.theta
        zq = _norm_ppf(alpha)
        adj = _norm_cdf(self.z0 + (self.z0 + zq)
                        / (1 - self.a * (self.z0 + zq)))
        idx = min(max(int(adj * self.b), 0), self.b - 1)
        return self.boots[idx]

    def ub(self, alpha=ALPHA):
        if self.theta is None:
            return None
        if self.degenerate:
            return self.theta
        zq = _norm_ppf(1 - alpha)
        adj = _norm_cdf(self.z0 + (self.z0 + zq)
                        / (1 - self.a * (self.z0 + zq)))
        idx = min(max(int(adj * self.b), 0), self.b - 1)
        return self.boots[idx]

    def p_greater(self, h0):
        """One-sided p-value for H0: theta <= h0 vs H1: theta > h0, by BCa
        inversion (the alpha at which the BCa lower bound crosses h0), so
        p <= alpha <=> lb(alpha) > h0 up to grid resolution."""
        if self.theta is None:
            return None
        lo, hi = 1.0 / (self.b + 1), 1 - 1.0 / (self.b + 1)
        if self.degenerate:
            return lo if self.theta > h0 else 1.0
        q = min(max(sum(1 for x in self.boots if x <= h0) / self.b, lo), hi)
        adj_z = _norm_ppf(q)
        u = (adj_z - self.z0) / (1 + self.a * (adj_z - self.z0))
        return min(max(_norm_cdf(u - self.z0), lo), 1.0)


class BootRatio:
    """Joint two-stage bootstrap of the s1' recovery ratio
    (c1p - B0)/(B2 - B0) on shared items: one item resample per replicate
    (shared numerator/denominator), FT seeds resampled independently per
    arm. Replicates with a non-positive B2 lift count CONSERVATIVELY as
    recovery >= the ceiling (+inf)."""

    def __init__(self, dc1, db2, db0, name, b=B):
        _grid(dc1, name + "/c1p")
        _grid(db2, name + "/b2")
        _grid(db0, name + "/b0")
        self.items = sorted(set(dc1) & set(db2) & set(db0))
        self.n = len(self.items)
        if self.n == 0:
            self.theta = None
            return
        s_c1 = sorted(next(iter(dc1.values())))
        s_b2 = sorted(next(iter(db2.values())))
        s_b0 = sorted(next(iter(db0.values())))
        C = [[dc1[i][s] for s in s_c1] for i in self.items]
        A = [[db2[i][s] for s in s_b2] for i in self.items]
        Z = [[db0[i][s] for s in s_b0] for i in self.items]
        kc, ka, kz = len(s_c1), len(s_b2), len(s_b0)
        l2 = sum(sum(A[i]) / ka - sum(Z[i]) / kz
                 for i in range(self.n)) / self.n
        l1 = sum(sum(C[i]) / kc - sum(Z[i]) / kz
                 for i in range(self.n)) / self.n
        self.lift_b2, self.lift_c1p = l2, l1
        self.theta = (l1 / l2) if l2 > 0 else None
        rng = random.Random("%d|%s" % (SEED, name))
        n = self.n
        ratios = []
        for _ in range(b):
            sc = [rng.randrange(kc) for _ in range(kc)] if kc > 1 else [0]
            sa = [rng.randrange(ka) for _ in range(ka)] if ka > 1 else [0]
            sz = [rng.randrange(kz) for _ in range(kz)] if kz > 1 else [0]
            t1 = t2 = 0.0
            for _j in range(n):
                i = rng.randrange(n)
                z = sum(Z[i][s] for s in sz) / len(sz)
                t2 += sum(A[i][s] for s in sa) / len(sa) - z
                t1 += sum(C[i][s] for s in sc) / len(sc) - z
            ratios.append((t1 / n) / (t2 / n) if t2 > 0
                          else float("inf"))
        self.ratios = sorted(ratios)
        self.b = b

    def ub(self, alpha=ALPHA):
        """Percentile upper bound (BCa is undefined at the +inf conservative
        replicates; percentile keeps them counted against the test)."""
        if self.theta is None and not getattr(self, "ratios", None):
            return None
        idx = min(max(int((1 - alpha) * self.b), 0), self.b - 1)
        u = self.ratios[idx]
        return None if math.isinf(u) else u

    def p_below(self, ceiling):
        """One-sided p for H0: recovery >= ceiling vs H1: recovery <
        ceiling; +inf replicates (undefined denominator) count for H0."""
        if not getattr(self, "ratios", None):
            return None
        lo = 1.0 / (self.b + 1)
        return min(max(sum(1 for r in self.ratios if r >= ceiling)
                       / self.b, lo), 1.0)


def holm_stepdown(pvals, alpha=ALPHA):
    """REAL Holm step-down (review fix 3). pvals: {name: p or None}; None
    (unevaluable) is excluded and the family size m adjusts. Returns the
    full machinery: order, assigned per-rank alphas alpha/(m-rank),
    Holm-adjusted p-values (monotone max-cummax), and step-down
    rejections."""
    evald = {k: v for k, v in pvals.items() if v is not None}
    m = len(evald)
    order = sorted(evald, key=lambda k: (evald[k], k))
    adjusted, reject, assigned = {}, {}, {}
    running, still = 0.0, True
    for rank, k in enumerate(order):
        a_k = alpha / (m - rank)
        assigned[k] = a_k
        running = max(running, min(1.0, (m - rank) * evald[k]))
        adjusted[k] = running
        rej = still and evald[k] <= a_k
        if not rej:
            still = False
        reject[k] = rej
    return {"family_size": m, "alpha": alpha, "order_by_p": order,
            "raw_p": evald, "assigned_alpha": assigned,
            "holm_adjusted_p": adjusted, "reject": reject,
            "excluded_unevaluable": sorted(k for k, v in pvals.items()
                                           if v is None)}


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


# ---------------------------------------------------------------------------
# Efficiency ledger (review fix 4): per-arm/rung price table, NO direction
# presumed (PROPOSED-ASM-1429). B4 struck (issue #24 (C)): the
# engine-at-inference price column is a DESCRIPTIVE cross-campaign pointer
# to the landed rules-1-c ledger, never recomputed here; no break-even N*.
# ---------------------------------------------------------------------------
def build_efficiency_ledger(rows, res):
    gpu_class = res.get("gpu_class_assumed_for_usd")
    usd_rate = (res.get("usd_per_hour_table") or {}).get(gpu_class)
    tl = res.get("training_ledger", {}) or {}
    el = res.get("eval_ledger", {}) or {}
    mode = res.get("mode")

    def keyparts(k):  # "arm/rung/seed=N" or "arm/rung/ft_seed=N"
        p = k.split("/")
        return p[0], p[1]

    per = {}

    def slot(arm, rung):
        return per.setdefault("%s/%s" % (arm, rung), {
            "train": None, "eval": None, "sout_per_query": None})

    # training side (per arm/rung, summed over FT seeds)
    tr_group = {}
    for k, v in tl.items():
        arm, rung = keyparts(k)
        tr_group.setdefault((arm, rung), []).append(v)
    for (arm, rung), vs in sorted(tr_group.items()):
        wall = sum(v.get("wall_seconds", 0) or 0 for v in vs)
        slot(arm, rung)["train"] = {
            "runs": len(vs),
            "gpu_hours": wall / 3600.0,
            "usd": (wall / 3600.0 * usd_rate) if usd_rate else None,
            "tokens_seen_total": sum(v.get("tokens_seen", 0) or 0
                                     for v in vs),
            "flops_formula_total": sum(v.get("flops_formula_train", 0) or 0
                                       for v in vs),
            "peak_mem_bytes_max": max(
                (v.get("peak_mem_bytes") for v in vs
                 if v.get("peak_mem_bytes") is not None), default=None),
            "mem_instrument": next((v.get("mem_instrument") for v in vs
                                    if v.get("mem_instrument")), None),
            "mode": vs[0].get("mode", mode)}

    # eval side (per arm/rung)
    ev_group = {}
    for k, v in el.items():
        arm, rung = keyparts(k)
        ev_group.setdefault((arm, rung), []).append(v)

    def eval_block(vs):
        wall = sum(v.get("wall_seconds", 0) or 0 for v in vs)
        return {
            "cells": len(vs),
            "gpu_hours": wall / 3600.0,
            "usd": (wall / 3600.0 * usd_rate) if usd_rate else None,
            "peak_mem_bytes_max": max(
                (v.get("peak_mem_bytes") for v in vs
                 if v.get("peak_mem_bytes") is not None), default=None),
            "mem_instrument": next((v.get("mem_instrument") for v in vs
                                    if v.get("mem_instrument")), None)}

    # row-derived per-query metrics on the identical S-out covered slice
    def rowstats(arm, rung, cell):
        rs = [r for r in rows if r["arm"] == arm and r.get("rung") == rung
              and r["cell"] == cell]
        if not rs:
            return None
        n = len(rs)
        eng = [r["engine_us"] for r in rs if r.get("engine_us") is not None]
        return {
            "n_query_scorings": n,
            "mean_attempts": sum(r.get("attempts", 0) for r in rs) / n,
            "mean_tokens_in": sum(r.get("tokens_in", 0) for r in rs) / n,
            "mean_flops_formula": sum(r.get("flops_formula", 0.0)
                                      for r in rs) / n,
            "tokens_in_total": sum(r.get("tokens_in", 0) for r in rs),
            "flops_formula_total": sum(r.get("flops_formula", 0.0)
                                       for r in rs),
            "mean_engine_us": (sum(eng) / len(eng)) if eng else None,
            "engine_us_total": sum(eng) if eng else None}

    arms_rungs = sorted({(r["arm"], r.get("rung")) for r in rows
                         if r["cell"] == "entailed"})
    for arm, rung in arms_rungs:
        s = slot(arm, rung)
        if (arm, rung) in ev_group:
            s["eval"] = eval_block(ev_group[(arm, rung)])
        st = rowstats(arm, rung, "entailed")
        if st is not None:
            ev = s.get("eval")
            usd_q = None
            if ev and ev.get("usd") is not None and st["n_query_scorings"]:
                # flops-share attribution of the arm's eval USD to S-out
                tot = sum(r.get("flops_formula", 0.0) for r in rows
                          if r["arm"] == arm and r.get("rung") == rung)
                share = (st["flops_formula_total"] / tot) if tot else None
                if share is not None:
                    usd_q = ev["usd"] * share / st["n_query_scorings"]
            st["usd_per_query_flops_share"] = usd_q
            s["sout_per_query"] = st

    consts = res.get("efficiency_constants", {}) or {}
    engine_descriptive = {
        "status": "DESCRIPTIVE, CROSS-CAMPAIGN (B4 struck — issue #24 "
                  "decision (C) + blocking-pilot IP-4, PROPOSED-ASM-1848)",
        "source": "the landed rules-1-c campaign efficiency ledger "
                  "(poc/rules-1/results-incoming/20260712-142704-"
                  "rules1b-parallel; campaign graded INSTRUMENT-INVALID — "
                  "its price rows are wall-clock/compute measurements and "
                  "remain citable as prices, never as hypothesis evidence)",
        "engine_us_per_query_class":
            consts.get("engine_us_per_query_class"),
        "note": "PROPOSED-ASM-1429/1848: NO direction presumed and NO "
                "break-even N* computed — the in-campaign engine-at-"
                "inference comparator (B4) was struck as vacuous, so any "
                "engine-vs-train-slot price comparison is cross-campaign "
                "and disclosed as such; B5 (R3 no-fine-tune) is the "
                "in-campaign efficiency comparator."}

    return {
        "mode": mode,
        "gpu_class": gpu_class,
        "usd_per_gpu_hour": usd_rate,
        "per_arm_rung": per,
        "engine_at_inference_descriptive": engine_descriptive,
        "constants": consts,
        "materialisation_one_off_cpu_seconds":
            consts.get("materialisation_cpu_seconds_measured"),
        "usd_attribution_note": "eval USD per arm/rung = measured cell wall "
                                "hours x the assumed GPU list rate; per-"
                                "query USD on the main surface uses flops-"
                                "share attribution (disclosed formula).",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-records", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--c8", required=True)
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
        # (REWORK-3 re-derivation at chance 0.5, PROPOSED-ASM-1805: expected
        # plain-host floor ~0.70 on the entity form; 0.85 keeps >= 3x SESOI
        # of headroom below the ceiling)
        "headroom_valid": (acc(rows, "B0", rung="R1") is not None and
                           acc(rows, "B0", rung="R1") <= 0.85),
        # G4 repeat gate (ASM-1439): every arm's S-out repeat byte-identical
        "repeat_byte_identical": bool(repeat) and all(
            v.get("byte_identical") for v in repeat.values()),
    }

    ent = lambda arm: collect(rows, arm, "entailed", "R1")

    # PRIMARY (ASM-1424 + review fix 3): B2 - B0 on S-out entailed, seed+item
    # bootstrap; registered SESOI 0.05 decision band.
    bc_primary = BootContrast(ent("B2"), ent("B0"), "primary_b2_b0")
    primary = bc_primary.lb(ALPHA)
    primary_pass = primary is not None and primary > SESOI
    kill_d = primary is not None and primary <= 0
    primary_band = (None if primary is None else
                    "pass_lb_above_sesoi" if primary_pass else
                    "kill_lb_at_or_below_zero" if kill_d else
                    "inconclusive_lb_in_(0,sesoi]")

    # Secondaries: bootstrap machinery + one-sided p-values for REAL Holm
    # (family {s1', s2', s4'} — s3' STRUCK, issue #24 (C)/PROPOSED-ASM-1848)
    bc_s2 = BootContrast(ent("B2"), ent("B1"), "s2p_b2_b1")
    br_s1 = BootRatio(ent("c1p"), ent("B2"), ent("B0"), "s1p_ratio")

    # s4' components (ASM-1430): B2 vs the point-estimate-better of B0/B1
    # (reference fixed at the point estimate, disclosed), paired items;
    # strata are first-FT-seed only (ASM-1457) so the seed axis there is
    # degenerate and the bootstrap is item-level.
    def guard_contrast(cell, key, name):
        d2 = collect(rows, "B2", cell, "R1", key=key)
        d0 = collect(rows, "B0", cell, "R1", key=key)
        d1 = collect(rows, "B1", cell, "R1", key=key)
        cand = {}
        for tag, d in (("B0", d0), ("B1", d1)):
            vals = [v for bs in d.values() for v in bs.values()]
            if vals:
                cand[tag] = sum(vals) / len(vals)
        if not cand or not d2:
            return None, None
        ref = max(cand, key=lambda t: (cand[t], t))
        bc = BootContrast(d2, d0 if ref == "B0" else d1,
                          "%s_vs_%s" % (name, ref))
        return bc, ref

    bc_s4_st, s4_st_ref = guard_contrast("stated", "item_correct_ext",
                                         "s4p_stated")
    bc_s4_rf, s4_rf_ref = guard_contrast("control", "refused", "s4p_refusal")
    s4_st = bc_s4_st.theta if bc_s4_st else None
    s4_rf = bc_s4_rf.theta if bc_s4_rf else None
    s4_side_effect = any(d is not None and d < -GUARD_MARGIN
                         for d in (s4_st, s4_rf))

    # one-sided p-values (H1 directions: s1' recovery < 0.30; s2' diff > 0;
    # s4' both deltas > -margin, intersection-union)
    p_s1 = br_s1.p_below(S1_RECOVERY_UB)
    p_s2 = bc_s2.p_greater(0.0) if bc_s2.theta is not None else None
    p4_parts = [bc.p_greater(-GUARD_MARGIN)
                for bc in (bc_s4_st, bc_s4_rf)
                if bc is not None and bc.theta is not None]
    p_s4 = max(p4_parts) if len(p4_parts) == 2 else None

    holm = holm_stepdown({"s1p": p_s1, "s2p": p_s2, "s4p": p_s4})
    # Bounds at each test's Holm-ASSIGNED alpha (the adjusted-CI companion)
    holm_bounds = {}
    for k, a_k in holm["assigned_alpha"].items():
        if k == "s1p":
            holm_bounds[k] = {"recovery_ub_at_assigned_alpha":
                              br_s1.ub(a_k)}
        elif k == "s2p":
            holm_bounds[k] = {"lb_at_assigned_alpha": bc_s2.lb(a_k)}
        elif k == "s4p":
            holm_bounds[k] = {
                "stated_lb_at_assigned_alpha":
                    bc_s4_st.lb(a_k) if bc_s4_st else None,
                "refusal_lb_at_assigned_alpha":
                    bc_s4_rf.lb(a_k) if bc_s4_rf else None}
    holm["bounds_at_assigned_alpha"] = holm_bounds
    holm["construction"] = (
        "review fix 3 + GO revision: one-sided bootstrap p-values (BCa "
        "inversion; percentile for the s1' ratio with conservative +inf "
        "replicates), two-stage FT-seed (cluster) x item resampling, B=%d, "
        "PRNG seed %d; Holm step-down at family alpha %.2f over "
        "{s1p, s2p, s4p} (s3' STRUCK with the B4 arm — issue #24 decision "
        "(C) + blocking-pilot IP-4, PROPOSED-ASM-1848); s4' is an "
        "intersection-union test (p = max of the two component ps)."
        % (B, SEED, ALPHA))

    s1p_rec_ub95 = br_s1.ub(ALPHA)
    s1p_pass = bool(holm["reject"].get("s1p"))
    s2p_pass = bool(holm["reject"].get("s2p"))
    s4p_pass = bool(holm["reject"].get("s4p")) and not s4_side_effect

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

    ledger = build_efficiency_ledger(rows, res)
    train_flops = sum(v.get("flops_formula_train", 0) or 0
                      for v in res.get("training_ledger", {}).values())
    per_ar = ledger["per_arm_rung"]

    def _train_field(k, f):
        t = (per_ar.get(k, {}) or {}).get("train")
        return t.get(f) if t else None

    bc_b3 = BootContrast(ent("B3"), ent("B2"), "b3_minus_b2")

    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_pass": primary_pass,
        "primary_band": {
            "value": primary_band,
            "sesoi": SESOI,
            "rule": "review fix 3 / registered SESOI: PASS iff LB95 > "
                    "0.05; KILL-d iff LB95 <= 0; 0 < LB95 <= 0.05 is "
                    "INCONCLUSIVE (neither pass nor kill)"},
        "kill_d_fired": kill_d,
        "s1p_shuffled_recovery_ub95": s1p_rec_ub95,
        "s1p_pass": s1p_pass,
        "s2p_exposure_lb95": bc_s2.lb(ALPHA),
        "s2p_pass": s2p_pass,
        "s4p_stated_delta": s4_st,
        "s4p_refusal_delta": s4_rf,
        "s4p_side_effect_flag": s4_side_effect,
        "s4p_pass": s4p_pass,
        "s4p_reference_arms": {"stated": s4_st_ref, "refusal": s4_rf_ref},
        "holm_order": HOLM_ORDER,
        "holm": holm,
        "acc_b0_sout": acc(rows, "B0", rung="R1"),
        "acc_b1_sout": acc(rows, "B1", rung="R1"),
        "acc_b2_sout": acc(rows, "B2", rung="R1"),
        "acc_b3_sout": acc(rows, "B3", rung="R1"),
        "acc_b5_sout": acc(rows, "B5", rung="R3"),
        "acc_c1p_sout": acc(rows, "c1p", rung="R1"),
        "strata_profile": strata_profile,
        "rung_sign_descriptive": {
            "values": rung_sign,
            "note": "two rungs license a SIGN, not a slope (ASM-1433); the "
                    "frozen envelope presumes NO direction, so the record's "
                    "scale_language_max is 'none'"},
        "refusal_correctness_control": {
            a: refusal_rate(rows, a) for a in
            ("B0", "B1", "B2", "B3", "B5", "c1p")},
        "b3_minus_b2_descriptive": bc_b3.lb(ALPHA),
        "ft_seed_variance": seed_var,
        "efficiency_ledger": ledger,
        "accuracy": acc(rows, "B2", rung="R1"),
        "params": 135_000_000,
        "memory": {
            "per_arm_rung_train_peak_bytes": {
                k: _train_field(k, "peak_mem_bytes_max")
                for k in sorted(per_ar)},
            "per_arm_rung_eval_peak_bytes": {
                k: ((per_ar[k].get("eval") or {}).get("peak_mem_bytes_max"))
                for k in sorted(per_ar)},
            "instrument_note": "review fix 4: measured per cell — CUDA "
                               "allocator peak (reset per cell) on GPU; "
                               "process peak RSS (monotone high-water "
                               "mark, named per entry) on CPU/mock",
            "claim_carrier_b2_r1_train_peak_bytes":
                _train_field("B2/R1", "peak_mem_bytes_max")},
        "inference_compute": {
            "total_flops_formula_all_rows": (lambda xs: sum(xs) if xs
                                             else None)(
                [r.get("flops_formula", 0) for r in rows]),
            "b2_r1_sout_mean_flops_per_query":
                ((per_ar.get("B2/R1", {}) or {}).get("sout_per_query")
                 or {}).get("mean_flops_formula"),
            "engine_at_inference_descriptive":
                ledger.get("engine_at_inference_descriptive"),
            "detail": "per-arm/rung breakdown in /analysis/"
                      "efficiency_ledger (review fix 4; B4 struck — "
                      "issue #24 (C))"},
        "training_compute": {
            "total_flops_formula": train_flops,
            "per_arm_rung": {
                k: {f: _train_field(k, f) for f in
                    ("gpu_hours", "usd", "tokens_seen_total",
                     "flops_formula_total", "peak_mem_bytes_max")}
                for k in sorted(per_ar) if _train_field(k, "gpu_hours")
                is not None},
            "one_off_materialisation_cpu_seconds":
                ledger.get("materialisation_one_off_cpu_seconds")},
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
