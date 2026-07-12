#!/usr/bin/env python3
"""rules-2 pre-registered analysis, GO revision — STDIN-CONFORMANT successor
of analysis/rules_2_go.py (identical statistics, verdict-gen-compatible
input).

WHY THIS FILE EXISTS (interface-defect fix, NOT a design change): the
original pinned script analysis/rules_2_go.py (sha256 58b4831f1b742ff934c2
8db2016c0fd284f2a0adfce1f4cf093d794c75639a54) took argparse-REQUIRED flags
(--run-records/--results/--c8), while tools/registry/verdict-gen.py step 5
invokes the pinned analysis with the ELIGIBLE results-log run records as
JSONL on STDIN and NO argv — so the automated verdict path could never
execute the pin (argparse exits 2 => ERR_P2_ANALYSIS). This is the SAME
defect class the rules-1-c record carried (resolved by analysis/
rules_1c_stdin.py + registry/corrections/rules-1-c/2-prefreeze-correction
.json); this successor is swapped in by the same lawful pre-final
reset-refreeze mechanism (docs/next/opus-execution-practices.md 'Scope
note'; registry/corrections/rules-2/1-prefreeze-correction.json): rules-2
has NO run record of any phase in its results-log at correction time (the
file does not exist) and is NOT GNG-0-signed. Every statistic, constant,
gate expression and the output serialization below is carried
BYTE-IDENTICAL from rules_2_go.py; only input acquisition changed. Parity
was proven by running both scripts over the same 16,662 merged campaign
rows and diffing stdout bytes (see the correction record).

INPUT CONTRACT (verdict-gen P2 §3.1 step 5): eligible run records as JSONL
on stdin — event=="run", phase=="final", exit=="ok", chain-verified,
prereg-hash-matched by verdict-gen. Each eligible record's `artifacts`
must pin the campaign per-item row file (ROWS_PATH/ROWS_SHA256 below);
this script loads the per-item rows from that PINNED path (sha256
re-verified, fail closed) and consumes ONLY rows whose (arm, rung, seed)
cell is witnessed by an eligible stdin record — the analysis stays a pure
function of the eligible set. The campaign results carrier (pins_verified,
certificate precondition, repeat shas, ledgers) and the c8 G2-gate
artifact are read from their PINNED paths, sha256 re-verified. Any
mismatch/absence fails closed (exit 1 => verdict-gen ERR_P2_ANALYSIS);
nothing falls back.

Everything below this docstring other than main()'s input acquisition is
verbatim from analysis/rules_2_go.py — see that file's docstring for the
design record (GO revision: B4/s3'/entailed2 struck per maintainer issue
#24 decision (C) + blocking-pilot IP-4; Holm family {s1p, s2p, s4p};
engine-at-inference price column descriptive cross-campaign only).

Statistics: two-stage FT-seed x item paired BCa bootstrap B=10000, PRNG
seed 20260712, one-sided alpha=0.05; registered SESOI 0.05 decision band
on the primary; REAL Holm step-down over {s1p, s2p, s4p}; s4' is an
intersection-union test with the point-estimate side-effect flag.
"""

import hashlib
import json
import math
import random
import sys

# Pinned inputs (pinned transitively via THIS script's sha256 in
# pins.analysis_script — a byte change here is an encoder-of-record change
# and requires a new freeze). The rows/results shas equal the merged
# campaign pair produced by poc/rules-2/merge_shards.py (campaign
# campaign-20260712-195226); the c8 sha equals the frozen record's
# pins.artifact_hashes["c8-result(...)"] carrier 674b424f....
ROWS_PATH = ("poc/rules-2/results-incoming/campaign-20260712-195226/"
             "merged/run-records-rules2.jsonl")
ROWS_SHA256 = "e3981c8e2d12c7e773118c40c42cb014df76dea05477c06a67f89295469da59a"
RESULTS_PATH = ("poc/rules-2/results-incoming/campaign-20260712-195226/"
                "merged/results-rules2.json")
RESULTS_SHA256 = "c904005a0f8040362a4ad26a7e2aa61413688814284ddfae5db8bfd0c3c39264"
C8_PATH = "poc/rules-2/results/c8-result.json"
C8_SHA256 = "674b424f913d397c757ddf263d9abf8fbc10f54d986b75e3ff3bb768e8d7c598"

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


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def read_pinned(path, want_sha, what):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        fail("ERR_RULES2_PIN_IO", "%s: cannot read pinned %s: %s"
             % (what, path, e))
    got = hashlib.sha256(raw).hexdigest()
    if got != want_sha:
        fail("ERR_RULES2_PIN_DRIFT", "%s: %s sha256 %s != pinned %s"
             % (what, path, got, want_sha))
    return raw


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
    # ---- input acquisition (the ONLY departure from rules_2_go.py) ----
    stdin_raw = sys.stdin.buffer.read().decode("utf-8")
    try:
        records = [json.loads(x) for x in stdin_raw.splitlines() if x.strip()]
    except json.JSONDecodeError as e:
        fail("ERR_RULES2_STDIN", "stdin is not JSONL: %s" % e)
    # Defensive re-filter of verdict-gen's own eligibility (P2 §3.1 step 3);
    # reuse-provenance rows (D9) are refused — rules-2 declares no
    # reused_from block, so any such row is a contract violation.
    eligible = [r for r in records
                if r.get("event") == "run" and r.get("phase") == "final"
                and r.get("exit") == "ok"]
    if not eligible:
        fail("ERR_RULES2_NO_ELIGIBLE",
             "no eligible run records on stdin (verdict-gen pipes eligible "
             "rows; the completeness gate should have fired upstream)")
    if any(r.get("reuse_provenance") for r in records):
        fail("ERR_RULES2_REUSE",
             "reused producer rows on stdin but rules-2 freezes no "
             "reused_from block — refusing (fail closed)")
    cells = set()
    for r in eligible:
        arts = r.get("artifacts") or []
        if not any(a.get("path") == ROWS_PATH and a.get("sha256") == ROWS_SHA256
                   for a in arts):
            fail("ERR_RULES2_ARTIFACT",
                 "eligible run record seq=%r does not pin the campaign row "
                 "artifact %s@%s…" % (r.get("seq"), ROWS_PATH, ROWS_SHA256[:12]))
        cfg = r.get("config") or {}
        missing = [k for k in ("arm", "rung", "seed") if k not in cfg]
        if missing:
            fail("ERR_RULES2_CONFIG",
                 "eligible run record seq=%r config missing %s"
                 % (r.get("seq"), ", ".join(missing)))
        cells.add((cfg["arm"], cfg["rung"], cfg["seed"]))

    rows_raw = read_pinned(ROWS_PATH, ROWS_SHA256, "campaign rows")
    rows_all = [json.loads(x) for x in rows_raw.decode("utf-8").splitlines()
                if x.strip()]
    # Only rows whose (arm, rung, seed) cell is witnessed by an eligible
    # stdin record enter the analysis — excluded log rows drop their cells.
    rows = [r for r in rows_all if (r["arm"], r["rung"], r["seed"]) in cells]
    if not rows:
        fail("ERR_RULES2_NO_ROWS",
             "no pinned campaign rows match the eligible cells %s"
             % sorted(cells))
    res = json.loads(read_pinned(RESULTS_PATH, RESULTS_SHA256,
                                 "campaign results carrier"))
    c8 = json.loads(read_pinned(C8_PATH, C8_SHA256, "c8 G2-gate artifact"))
    # ---- everything below is verbatim from analysis/rules_2_go.py ----

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
