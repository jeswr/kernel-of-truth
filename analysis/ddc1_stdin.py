#!/usr/bin/env python3
"""ddc1 pre-registered analysis (pure function over per-item run records).
ddc1 pre-registered analysis — STDIN-CONFORMANT successor of analysis/ddc1.py
(verdict-gen-compatible input; IDENTICAL statistics). WHY: the CLI ddc1.py took
argparse-REQUIRED --items/--cells/--sidecar, but verdict-gen pipes eligible run
records as JSONL on STDIN with no argv (argparse exits 2 => ERR_P2_ANALYSIS;
/pins/analysis_script is un-amendable post-freeze). Same fix as ufo/rules/knull;
swap the DRAFT ddc1 pin to this successor BEFORE freeze. ONLY input acquisition
changed — load_inputs/validate and every statistic below are the exact CLI
functions (parity: mock stdout diff clean). Original CLI docstring follows.


Design: docs/next/design/DDC.md §3 (arms table), §4 (grid/matching), §5.1
(pinned pubeval instrument + informative-task filter), §5.2 (endpoint,
SESOI/TOST, power gate v3), §8 (gates I-1..I-6, S1->S2 promotion, verbatim
kill criteria), §11 (outcome map).
ASMs: ASM-1703 (primary endpoint Delta* = min(paired pooled-item retention
delta of A1 vs M1, and A1 vs mean-seed R1) at rho=0.75 on 135M; one-sided
95% task-stratified paired bootstrap 1e4 resamples; TOST = 90% percentile
CI inside (-3,+3) points; full-item cells rho in {0.9,0.75,0.5} only) and
ASM-1720 (joint power gate v3 — consumed here via the embedded
poc/ddc/power_sim_ddc1.py result; booleans recomputed from raw powers,
never trusted stored).

Inputs:
  --items items.jsonl — one row per scored item x cell:
    {task, item_id, rung in {r135,r360}, arm in {A0,A1,A2,A3,M1,M2,R1,C1,
     C2,C3}, rho in {0.9,0.75,0.5,0.3,0.15} (A0 rows carry rho=1.0),
     seed int (0 except R1: 0/1/2), correct 0/1 (acc_norm for MC, EM for
     gsm8k), subset 0/1 (1 = tail-cell deterministic subset scoring)}
  --cells cells.json — {"cells": [{rung, arm, rho, seed,
     gold_ppl_arc_easy, params_retained, energy_capture, present}...],
     "a0_gold_ppl": {"r135": float, "r360": float}}
  --sidecar sidecar.json — {filter_set: {r135: [...], r360: [...]},
     chance: {task: chance_acc}, i1_rotation_valid,
     i1_debug_iterations_used, i2_mechanics_valid, i3_corpus_parity_valid,
     i4_licenses_valid, per_item_emission_valid, power_sim_result
     (embedded poc/ddc/power_sim_ddc1.py output JSON), a2_ran, s2_ran,
     ddc0_verdict_ref, max_stat_outputs (opaque carry), usd_total,
     gpu_hours, expected_grid: {rung: [[arm, rho, n_seeds], ...]}}

Statistics (implemented, not narrated; global PRNG seed 20260712,
B=10000, deterministic per-statistic sub-seeds => byte-identical stdout
across reruns):
  * Pooled-item retention delta for (X vs Y) at a cell: pair items by
    (task, item_id) present in BOTH arms at that (rung, rho); delta_i =
    correct_X - correct_Y (R1 enters as the per-item mean over available
    seeds); statistic = 100 * mean_i(delta_i), in accuracy points.
    Delta* = min(delta(A1-M1), delta(A1-R1mean)).
  * Task-stratified paired bootstrap: resample items with replacement
    WITHIN task (task sizes fixed), recompute the full statistic; for
    Delta* BOTH contrasts are recomputed on the SAME resampled item
    multiset (the joint/min statistic, never independent legs). One-sided
    95% LB = 5th percentile of the B bootstrap statistics; TOST 90% CI =
    (5th, 95th) percentiles, equivalence iff both strictly inside
    (-3.0, +3.0) points (the ASM-1703 SESOI).
  * Bootstrap-inversion one-sided p per contrast =
    (1 + #{stat_b <= 0}) / (B + 1); Holm step-down over the §5.2
    registered secondary family (present members only). Full-item cells
    only — a subset row reaching any registered statistic is
    ERR_DDC1_SUBSET_IN_CLAIM, a hard error, never a gate.
  * Kills verbatim from §8; S1->S2 promotion rule verbatim from §8
    (primary holds OR any Holm-surviving secondary Delta* > 0 at
    rho >= 0.5 with A1 fluency inflation <= 1.5x).
  * Gate I-5 booleans are RECOMPUTED from the embedded simulation's raw
    powers (>= 0.9 both legs) AND config.q_ref == 0.25 AND not
    quick_mode (a --quick simulation can never gate).

Fail-closed exits: ERR_DDC1_IO (10), ERR_DDC1_MALFORMED (11),
ERR_DDC1_SUBSET_IN_CLAIM (12), ERR_DDC1_NO_PRIMARY_CELL (13).

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import hashlib
import json
import math
import os
import random
import shutil
import sys
import tempfile

OUTPUT_FIELDS = [
    "/gates/i1_rotation_valid",
    "/gates/i2_mechanics_valid",
    "/gates/i3_corpus_parity_valid",
    "/gates/i4_licenses_valid",
    "/gates/i5_power_valid",
    "/gates/i5_superiority_power",
    "/gates/i5_equivalence_power",
    "/gates/i5_least_favourable_c",
    "/gates/i5_infeasible_cells",
    "/gates/i6_energy_capture_min",
    "/gates/i6_flagged_cells",
    "/gates/per_item_emission_valid",
    "/gates/completeness_valid",
    "/analysis/delta_star_lb95",
    "/analysis/delta_star_point",
    "/analysis/primary_pass",
    "/analysis/delta_a1_m1_point",
    "/analysis/delta_a1_r1_point",
    "/analysis/macro_delta_star",
    "/analysis/measured_discordance",
    "/analysis/discordance_flags",
    "/analysis/holm_family_p",
    "/analysis/holm_adjusted_p",
    "/analysis/holm_survivors",
    "/analysis/secondary_delta_star_by_rho",
    "/analysis/kernel_specificity_ci",
    "/analysis/tost_ci90",
    "/analysis/tost_a1_c1_equiv",
    "/analysis/tost_a1_c2_equiv",
    "/analysis/null_a1_m1_r1_equiv",
    "/analysis/fluency_guard_ratios",
    "/analysis/fluency_breached_cells",
    "/analysis/retention_curves",
    "/analysis/chance_corrected_retention",
    "/analysis/kill_a_fired",
    "/analysis/kill_b_fired",
    "/analysis/kill_c_fired",
    "/analysis/kill_fired",
    "/analysis/a2_ran",
    "/analysis/a2_minus_a1_ci",
    "/analysis/a3_minus_a1_ci",
    "/analysis/max_stat_outputs_carried",
    "/analysis/s2_promotion_fired",
    "/analysis/s2_replication_sign",
    "/analysis/cost_ledger",
]

B = 10000
SEED = 20260712              # registered global PRNG seed (house convention)
SESOI = 3.0                  # +-3.0 pooled points, ASM-1703
FLUENCY_BOUND = 1.5          # §8 promotion rule / §11 fluency-guard row
DISCORDANCE_FLAG_Q = 0.25    # q_ref, ASM-1720 — measured q > q_ref flags
ENERGY_FLAG = 0.99           # gate I-6 tripwire
FULL_RHOS = (0.9, 0.75, 0.5)     # registered full-item cells, ASM-1703
SUBSET_RHOS = (0.3, 0.15)        # curve-only subset tail, ASM-1703
ITEM_RHOS = (0.9, 0.75, 0.5, 0.3, 0.15, 1.0)
ARMS = ("A0", "A1", "A2", "A3", "M1", "M2", "R1", "C1", "C2", "C3")
RUNGS = ("r135", "r360")
CHANCE_DEGENERATE = 0.05     # §5.2 chance-corrected denominator guard

ERR = {"ERR_DDC1_IO": 10, "ERR_DDC1_MALFORMED": 11,
       "ERR_DDC1_SUBSET_IN_CLAIM": 12, "ERR_DDC1_NO_PRIMARY_CELL": 13}


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(ERR[code])


def g(x):
    """Canonical short float key: 0.75 -> '0.75', 1.0 -> '1'."""
    return "%g" % x


def sub_rng(tag):
    """Deterministic sub-seeded PRNG per statistic (order-independent)."""
    sub = int(hashlib.sha256(("%d|%s" % (SEED, tag)).encode())
              .hexdigest()[:12], 16)
    return random.Random(sub)


def q_at(sorted_boots, p):
    """Nearest-rank percentile over the sorted bootstrap statistics."""
    idx = max(0, min(B - 1, int(math.ceil(p * B)) - 1))
    return sorted_boots[idx]


class PairBoot:
    """Task-stratified paired percentile bootstrap of one pooled paired
    delta (points scale). by_task: task -> list of per-item diffs."""

    def __init__(self, by_task, tag):
        self.by_task = {t: v for t, v in by_task.items() if v}
        self.tasks = sorted(self.by_task)
        self.n = sum(len(self.by_task[t]) for t in self.tasks)
        self.ok = self.n > 0
        if not self.ok:
            return
        self.point = 100.0 * sum(sum(self.by_task[t])
                                 for t in self.tasks) / self.n
        rng = sub_rng(tag)
        boots = []
        for _ in range(B):
            s = 0.0
            for t in self.tasks:
                v = self.by_task[t]
                s += sum(rng.choices(v, k=len(v)))
            boots.append(100.0 * s / self.n)
        self.boots = sorted(boots)

    def lb95(self):
        return q_at(self.boots, 0.05)

    def ci90(self):
        return [q_at(self.boots, 0.05), q_at(self.boots, 0.95)]

    def ci95(self):
        return [q_at(self.boots, 0.025), q_at(self.boots, 0.975)]

    def p_gt0(self):
        return (1 + sum(1 for x in self.boots if x <= 0)) / (B + 1)

    def tost(self):
        lo, hi = self.ci90()
        return lo > -SESOI and hi < SESOI


class JointBoot:
    """Task-stratified paired bootstrap of the JOINT min statistic
    Delta* = 100 * min(mean dAM, mean dAR); both contrasts recomputed on
    the SAME resampled item multiset. by_task: task -> [(dAM, dAR)]."""

    def __init__(self, by_task, tag):
        self.by_task = {t: v for t, v in by_task.items() if v}
        self.tasks = sorted(self.by_task)
        self.n = sum(len(self.by_task[t]) for t in self.tasks)
        self.ok = self.n > 0
        if not self.ok:
            return
        s_am = sum(d[0] for t in self.tasks for d in self.by_task[t])
        s_ar = sum(d[1] for t in self.tasks for d in self.by_task[t])
        self.point_am = 100.0 * s_am / self.n
        self.point_ar = 100.0 * s_ar / self.n
        self.point = min(self.point_am, self.point_ar)
        rng = sub_rng(tag)
        boots = []
        for _ in range(B):
            s_am = 0.0
            s_ar = 0.0
            for t in self.tasks:
                v = self.by_task[t]
                for d in rng.choices(v, k=len(v)):
                    s_am += d[0]
                    s_ar += d[1]
            boots.append(100.0 * min(s_am, s_ar) / self.n)
        self.boots = sorted(boots)

    def lb95(self):
        return q_at(self.boots, 0.05)

    def p_gt0(self):
        return (1 + sum(1 for x in self.boots if x <= 0)) / (B + 1)


def holm(p_raw):
    """Holm step-down adjusted p over the registered family."""
    items = sorted((p, k) for k, p in p_raw.items())
    m = len(items)
    adj, run = {}, 0.0
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = run
    return adj


# ---------------------------------------------------------------- loading

def load_inputs(args):
    try:
        with open(args.items) as f:
            lines = [ln for ln in f if ln.strip()]
        with open(args.cells) as f:
            cells_raw = f.read()
        with open(args.sidecar) as f:
            side_raw = f.read()
    except OSError as e:
        die("ERR_DDC1_IO", str(e))
    try:
        rows = [json.loads(ln) for ln in lines]
        cells = json.loads(cells_raw)
        side = json.loads(side_raw)
    except ValueError as e:
        die("ERR_DDC1_MALFORMED", "json parse: %s" % e)
    return rows, cells, side


def validate(rows, cells, side):
    row_keys = ("task", "item_id", "rung", "arm", "rho", "seed",
                "correct", "subset")
    for i, r in enumerate(rows):
        for k in row_keys:
            if k not in r:
                die("ERR_DDC1_MALFORMED",
                    "items row %d missing key %r" % (i, k))
        if r["rung"] not in RUNGS:
            die("ERR_DDC1_MALFORMED", "items row %d bad rung" % i)
        if r["arm"] not in ARMS:
            die("ERR_DDC1_MALFORMED", "items row %d bad arm" % i)
        if float(r["rho"]) not in ITEM_RHOS:
            die("ERR_DDC1_MALFORMED", "items row %d bad rho" % i)
        if r["correct"] not in (0, 1, 0.0, 1.0):
            die("ERR_DDC1_MALFORMED", "items row %d bad correct" % i)
        if r["subset"] not in (0, 1):
            die("ERR_DDC1_MALFORMED", "items row %d bad subset" % i)
    if not isinstance(cells, dict) or "cells" not in cells \
            or "a0_gold_ppl" not in cells:
        die("ERR_DDC1_MALFORMED", "cells.json missing cells/a0_gold_ppl")
    cell_keys = ("rung", "arm", "rho", "seed", "gold_ppl_arc_easy",
                 "params_retained", "energy_capture", "present")
    for i, c in enumerate(cells["cells"]):
        for k in cell_keys:
            if k not in c:
                die("ERR_DDC1_MALFORMED",
                    "cells entry %d missing key %r" % (i, k))
    side_keys = ("filter_set", "chance", "i1_rotation_valid",
                 "i1_debug_iterations_used", "i2_mechanics_valid",
                 "i3_corpus_parity_valid", "i4_licenses_valid",
                 "per_item_emission_valid", "power_sim_result", "a2_ran",
                 "s2_ran", "ddc0_verdict_ref", "max_stat_outputs",
                 "usd_total", "gpu_hours", "expected_grid")
    for k in side_keys:
        if k not in side:
            die("ERR_DDC1_MALFORMED", "sidecar missing key %r" % k)
    psr = side["power_sim_result"]
    for k in ("superiority_power_min_over_c", "equivalence_power",
              "least_favourable_c", "infeasible_cells", "config"):
        if not isinstance(psr, dict) or k not in psr:
            die("ERR_DDC1_MALFORMED", "power_sim_result missing %r" % k)
    if not isinstance(side["expected_grid"], dict):
        die("ERR_DDC1_MALFORMED", "expected_grid must map rung -> entries")
    if not isinstance(side["filter_set"], dict) \
            or "r135" not in side["filter_set"]:
        die("ERR_DDC1_MALFORMED", "filter_set missing r135")


# ------------------------------------------------------------- item maps

def guard_no_subset(rows):
    """A subset row reaching a registered statistic is a hard error
    (ASM-1703 cell-tier discipline), never a gate."""
    for r in rows:
        if r["subset"] != 0:
            die("ERR_DDC1_SUBSET_IN_CLAIM",
                "subset row in registered pool: %s/%s %s@rho%s"
                % (r["task"], r["item_id"], r["arm"], g(float(r["rho"]))))


def build_claim_maps(rows, filt):
    """Full-item registered pool: (rung, rho, arm) -> {(task,item): mean
    correct over seeds}; plus per-seed R1 maps (rung, rho, seed)."""
    claim = [r for r in rows
             if r["subset"] == 0
             and r["task"] in filt.get(r["rung"], [])
             and (float(r["rho"]) in FULL_RHOS
                  or (r["arm"] == "A0" and float(r["rho"]) == 1.0))]
    guard_no_subset(claim)
    acc = {}
    r1_seed = {}
    for r in claim:
        rho = float(r["rho"])
        k = (r["task"], r["item_id"])
        acc.setdefault((r["rung"], rho, r["arm"]), {}) \
           .setdefault(k, []).append(float(r["correct"]))
        if r["arm"] == "R1":
            r1_seed.setdefault((r["rung"], rho, int(r["seed"])), {})[k] = \
                float(r["correct"])
    maps = {ck: {k: sum(v) / len(v) for k, v in m.items()}
            for ck, m in acc.items()}
    return maps, r1_seed


def pair_by_task(mx, my):
    out = {}
    for k in sorted(set(mx) & set(my)):
        out.setdefault(k[0], []).append(mx[k] - my[k])
    return out


def joint_by_task(ma, mm, mr):
    out = {}
    for k in sorted(set(ma) & set(mm) & set(mr)):
        out.setdefault(k[0], []).append((ma[k] - mm[k], ma[k] - mr[k]))
    return out


def pooled_acc(m):
    return (sum(m.values()) / len(m)) if m else None


def discordance(mx, my):
    ks = sorted(set(mx) & set(my))
    if not ks:
        return None
    return sum(1 for k in ks if abs(mx[k] - my[k]) > 1e-9) / len(ks)


# ---------------------------------------------------------- completeness

def completeness(rows, cells, side):
    """Structural gate: every expected (arm, rho, seed) cell present in
    cells.json with >= 1 item row of the right tier; full-item per-task
    item counts equal across all arms/seeds of the same (rung, rho).
    Structural mismatch => False (gate), absent keys => ERR (validate)."""
    present = set()
    for c in cells["cells"]:
        if c.get("present"):
            present.add((c["rung"], c["arm"], float(c["rho"]),
                         int(c["seed"])))
    counts = {}
    for r in rows:
        key = (r["rung"], r["arm"], float(r["rho"]), int(r["seed"]),
               int(r["subset"]))
        tc = counts.setdefault(key, {})
        tc[r["task"]] = tc.get(r["task"], 0) + 1
    exp = side["expected_grid"]
    for rung in sorted(exp):
        for e in exp[rung]:
            if not (isinstance(e, (list, tuple)) and len(e) == 3):
                die("ERR_DDC1_MALFORMED", "bad expected_grid entry %r" % e)
            arm, rho, n_seeds = e[0], float(e[1]), int(e[2])
            tier = 1 if rho in SUBSET_RHOS else 0
            for seed in range(n_seeds):
                if (rung, arm, rho, seed) not in present:
                    return False
                if not counts.get((rung, arm, rho, seed, tier)):
                    return False
        by_rho = {}
        for e in exp[rung]:
            arm, rho, n_seeds = e[0], float(e[1]), int(e[2])
            if rho in FULL_RHOS:
                for seed in range(n_seeds):
                    by_rho.setdefault(rho, []).append((arm, seed))
        for rho in sorted(by_rho):
            ref = None
            for arm, seed in by_rho[rho]:
                tc = counts.get((rung, arm, rho, seed, 0), {})
                if ref is None:
                    ref = tc
                elif tc != ref:
                    return False
    return True


# ------------------------------------------------------------------ main

class _NS:
    def __init__(self, items, cells, sidecar):
        self.items = items
        self.cells = cells
        self.sidecar = sidecar


def _one_consistent(recs, key, code, what):
    """The single campaign-global metrics[key] carried (identically) by the
    eligible records; fail closed on absence or disagreement."""
    seen = {}
    for r in recs:
        m = r.get("metrics") or {}
        if key in m:
            seen[json.dumps(m[key], sort_keys=True)] = m[key]
    if not seen:
        die(code, "no eligible run record carries metrics.%s (%s)" % (key, what))
    if len(seen) != 1:
        die(code, "eligible run records carry %d distinct metrics.%s values — "
                  "refusing (fail closed)" % (len(seen), key))
    return next(iter(seen.values()))


def _stdin_inputs():
    """verdict-gen (P2 §3.1 step 5) pipes the ELIGIBLE results-log run records
    as JSONL on stdin with NO argv. The finalized campaign rides IN the records'
    metrics (poc/ddc collect-to-log, mirroring ufo-check-0): metrics.items (this
    record's per-item rows, concatenated across records in stdin order),
    metrics.cells (the campaign-global {cells, a0_gold_ppl} object) and
    metrics.sidecar (the campaign sidecar) — both identical in every record.
    Returns (items, cells, side) exactly as the CLI load_inputs would."""
    raw = sys.stdin.buffer.read().decode("utf-8")
    try:
        recs = [json.loads(x) for x in raw.splitlines() if x.strip()]
    except ValueError as e:
        die("ERR_DDC1_STDIN", "stdin is not JSONL: %s" % e)
    elig = [r for r in recs if r.get("event") == "run"
            and r.get("phase") == "final" and r.get("exit") == "ok"]
    if not elig:
        die("ERR_DDC1_NO_ELIGIBLE",
            "no eligible run records on stdin (the upstream completeness gate "
            "should have fired)")
    if any(r.get("reuse_provenance") for r in recs):
        die("ERR_DDC1_REUSE",
            "reused producer rows on stdin but ddc1 declares no reused_from "
            "block — refusing (fail closed)")
    items = []
    for r in elig:
        it = (r.get("metrics") or {}).get("items")
        if it is not None:
            if not isinstance(it, list):
                die("ERR_DDC1_MALFORMED", "metrics.items must be a list")
            items.extend(it)
    cells = _one_consistent(elig, "cells", "ERR_DDC1_NO_CELLS",
                            "the campaign {cells, a0_gold_ppl} aggregate")
    side = _one_consistent(elig, "sidecar", "ERR_DDC1_NO_SIDECAR",
                           "the campaign sidecar")
    return items, cells, side


def main():
    # ---- input acquisition (the ONLY departure from the CLI ddc1.py) ----
    # Reconstruct the three input files from the eligible records' metrics, then
    # load them through the SAME load_inputs validator, so every statistic below
    # is byte-identical to the CLI script (proven by a mock stdout diff).
    _items, _cells, _side = _stdin_inputs()
    _tmp = tempfile.mkdtemp(prefix="ddc1-stdin-")
    try:
        _ip = os.path.join(_tmp, "items.jsonl")
        _cp = os.path.join(_tmp, "cells.json")
        _sp = os.path.join(_tmp, "sidecar.json")
        with open(_ip, "w") as _f:
            for _row in _items:
                _f.write(json.dumps(_row) + "\n")
        with open(_cp, "w") as _f:
            json.dump(_cells, _f)
        with open(_sp, "w") as _f:
            json.dump(_side, _f)
        rows, cells, side = load_inputs(_NS(_ip, _cp, _sp))
    finally:
        shutil.rmtree(_tmp, ignore_errors=True)
    validate(rows, cells, side)

    filt = side["filter_set"]
    a2_ran = bool(side["a2_ran"])
    s2_ran = bool(side["s2_ran"])
    maps, r1_seed = build_claim_maps(rows, filt)

    def amap(rung, rho, arm):
        return maps.get((rung, rho, arm), {})

    # ---- pairwise contrast machinery (cached, deterministic tags) ----
    pair_arms = {"a1_m1": ("A1", "M1"), "a1_r1": ("A1", "R1"),
                 "a1_c1": ("A1", "C1"), "a1_c2": ("A1", "C2"),
                 "a1_c3": ("A1", "C3"), "a2_a1": ("A2", "A1"),
                 "a3_a1": ("A3", "A1")}
    pb_cache = {}

    def pb(name, rho, rung="r135"):
        key = (name, rho, rung)
        if key not in pb_cache:
            ax, ay = pair_arms[name]
            bt = pair_by_task(amap(rung, rho, ax), amap(rung, rho, ay))
            obj = PairBoot(bt, "pair|%s|%s|%s" % (name, rung, g(rho)))
            pb_cache[key] = obj if obj.ok else None
        return pb_cache[key]

    jb_cache = {}

    def jb(rho, rung="r135"):
        key = (rho, rung)
        if key not in jb_cache:
            bt = joint_by_task(amap(rung, rho, "A1"),
                               amap(rung, rho, "M1"),
                               amap(rung, rho, "R1"))
            obj = JointBoot(bt, "joint|%s|%s" % (rung, g(rho)))
            jb_cache[key] = obj if obj.ok else None
        return jb_cache[key]

    # ---- primary (ASM-1703): Delta* at rho=0.75, r135, full-item ----
    jb_primary = jb(0.75)
    pb_a1_m1 = pb("a1_m1", 0.75)
    pb_a1_r1 = pb("a1_r1", 0.75)
    if jb_primary is None or pb_a1_m1 is None or pb_a1_r1 is None:
        die("ERR_DDC1_NO_PRIMARY_CELL",
            "missing A1/M1/R1 paired items at rho=0.75 r135")
    delta_star_lb95 = jb_primary.lb95()
    primary_pass = delta_star_lb95 > 0

    # macro Delta*: min over contrasts of unweighted per-task mean delta
    def macro(pobj):
        ms = [100.0 * sum(v) / len(v) for t, v in
              sorted(pobj.by_task.items())]
        return sum(ms) / len(ms)
    macro_delta_star = min(macro(pb_a1_m1), macro(pb_a1_r1))

    # ---- Holm secondary family (§5.2; present members only) ----
    fam_p = {}
    for rho in (0.9, 0.5):
        o = jb(rho)
        if o is not None:
            fam_p["delta_star_rho%s" % g(rho)] = o.p_gt0()
    for name in ("a1_c1", "a1_c2", "a1_c3"):
        for rho in (0.75, 0.5):
            o = pb(name, rho)
            if o is not None:
                fam_p["%s_rho%s" % (name, g(rho))] = o.p_gt0()
    if a2_ran:
        for rho in (0.75, 0.5):
            o = pb("a2_a1", rho)
            if o is not None:
                fam_p["a2_a1_rho%s" % g(rho)] = o.p_gt0()
    for rho in (0.75, 0.5):
        o = pb("a3_a1", rho)
        if o is not None:
            fam_p["a3_a1_rho%s" % g(rho)] = o.p_gt0()
    jb_360 = jb(0.75, "r360") if s2_ran else None
    if s2_ran and jb_360 is not None:
        fam_p["primary_360m"] = jb_360.p_gt0()
    fam_adj = holm(fam_p)
    survivors = sorted(k for k in fam_adj if fam_adj[k] <= 0.05)

    secondary_by_rho = {}
    for rho in (0.9, 0.5):
        o = jb(rho)
        secondary_by_rho[g(rho)] = o.point if o is not None else None

    # ---- kernel-specificity CIs + TOST rows ----
    kspec_ci = {}
    for name in ("a1_c1", "a1_c2", "a1_c3"):
        for rho in (0.75, 0.5):
            o = pb(name, rho)
            if o is not None:
                kspec_ci["%s_rho%s" % (name, g(rho))] = o.ci95()
    tost_ci90 = {}
    for name in ("a1_m1", "a1_r1", "a1_c1", "a1_c2"):
        for rho in FULL_RHOS:
            o = pb(name, rho)
            if o is not None:
                tost_ci90["%s@rho%s" % (name, g(rho))] = o.ci90()

    def tost_equiv_dict(name):
        out = {}
        for rho in (0.75, 0.5):
            o = pb(name, rho)
            out["rho%s" % g(rho)] = o.tost() if o is not None else None
        return out
    tost_a1_c1 = tost_equiv_dict("a1_c1")
    tost_a1_c2 = tost_equiv_dict("a1_c2")

    # §11 NULL row: A1~M1~R1 (TOST) at ALL full-item rhos on r135
    null_equiv = True
    for name in ("a1_m1", "a1_r1"):
        for rho in FULL_RHOS:
            o = pb(name, rho)
            if o is None or not o.tost():
                null_equiv = False

    # ---- measured discordance at rho=0.75 r135 (flag q > q_ref) ----
    disc = {}
    a1_map = amap("r135", 0.75, "A1")
    for name in ("a1_m1", "a1_c1", "a1_c2", "a1_c3", "a3_a1") \
            + (("a2_a1",) if a2_ran else ()):
        ax, ay = pair_arms[name]
        d = discordance(amap("r135", 0.75, ax), amap("r135", 0.75, ay))
        if d is not None:
            disc[name] = d
    seeds_075 = sorted(s for (rg, rho, s) in r1_seed
                       if rg == "r135" and rho == 0.75)
    per_seed = [discordance(a1_map, r1_seed[("r135", 0.75, s)])
                for s in seeds_075]
    per_seed = [d for d in per_seed if d is not None]
    if per_seed:
        disc["a1_r1"] = sum(per_seed) / len(per_seed)
    disc_flags = sorted(k for k, v in disc.items()
                        if v > DISCORDANCE_FLAG_Q)

    # ---- retention (pooled acc / A0 pooled acc over the filter set) ----
    def retention(rung, rho, arm):
        a0 = pooled_acc(amap(rung, 1.0, "A0"))
        a = pooled_acc(amap(rung, rho, arm))
        if a0 is None or a is None or a0 == 0:
            return None
        return a / a0

    # kill (b) verbatim §8: strictly worse than BOTH controls at EVERY
    # full-item rho >= 0.5 on r135 (evaluable rhos only; none => False)
    kb_cells = []
    for rho in FULL_RHOS:
        ra1 = retention("r135", rho, "A1")
        rm1 = retention("r135", rho, "M1")
        rr1 = retention("r135", rho, "R1")  # per-item seed-mean pooled
        if None in (ra1, rm1, rr1):
            kb_cells = []
            break
        kb_cells.append(ra1 < rm1 and ra1 < rr1)
    kill_b = bool(kb_cells) and all(kb_cells)
    kill_a = (not bool(side["i1_rotation_valid"])
              and int(side["i1_debug_iterations_used"]) >= 1)
    kill_c = len(filt.get("r135", [])) == 0
    kill_fired = kill_a or kill_b or kill_c

    # ---- fluency guard (ARC-Easy gold_ppl, §5.1/ASM-1666) ----
    cell_idx = {}
    for c in cells["cells"]:
        if c.get("present"):
            cell_idx[(c["rung"], c["arm"], float(c["rho"]),
                      int(c["seed"]))] = c

    def gold_ppl(rung, arm, rho):
        if arm == "R1":
            vals = [c["gold_ppl_arc_easy"]
                    for (rg, a, rh, s), c in sorted(cell_idx.items())
                    if rg == rung and a == "R1" and rh == rho
                    and c["gold_ppl_arc_easy"] is not None]
            return (sum(vals) / len(vals)) if vals else None
        c = cell_idx.get((rung, arm, rho, 0))
        return c["gold_ppl_arc_easy"] if c else None

    fluency_ratios = {}
    fluency_breached = []
    for rho in FULL_RHOS:
        pa1 = gold_ppl("r135", "A1", rho)
        pm1 = gold_ppl("r135", "M1", rho)
        pr1 = gold_ppl("r135", "R1", rho)
        if None in (pa1, pm1, pr1) or min(pm1, pr1) <= 0:
            continue
        ratio = pa1 / min(pm1, pr1)
        fluency_ratios[g(rho)] = ratio
        if ratio > FLUENCY_BOUND:
            fluency_breached.append("A1@rho%s" % g(rho))
    fluency_breached = sorted(fluency_breached)

    # ---- retention curves (full-item + labelled subset tail) ----
    curves = {}
    subset_cells = []
    subset_rows = [r for r in rows
                   if r["subset"] == 1 and float(r["rho"]) in SUBSET_RHOS
                   and r["task"] in filt.get(r["rung"], [])]
    sub_acc = {}
    for r in subset_rows:
        sub_acc.setdefault((r["rung"], float(r["rho"]), r["arm"]),
                           []).append(float(r["correct"]))
    for rung in RUNGS:
        a0 = pooled_acc(amap(rung, 1.0, "A0"))
        if a0 is None or a0 == 0:
            continue
        cur = {"A0": {"1": 1.0}}
        for (rg, rho, arm) in sorted(maps):
            if rg != rung or arm == "A0":
                continue
            ret = retention(rung, rho, arm)
            if ret is not None:
                cur.setdefault(arm, {})[g(rho)] = ret
        for (rg, rho, arm) in sorted(sub_acc):
            if rg != rung:
                continue
            vals = sub_acc[(rg, rho, arm)]
            cur.setdefault(arm, {})[g(rho)] = (sum(vals) / len(vals)) / a0
            subset_cells.append("%s@%s@%s" % (arm, g(rho), rung))
        curves[rung] = cur
    retention_curves = {"curves": curves,
                        "subset_cells": sorted(subset_cells)}

    # ---- chance-corrected retention (per task, r135 full-item) ----
    chance = side["chance"]
    ccr = {}
    for task in sorted(filt.get("r135", [])):
        a0m = {k: v for k, v in amap("r135", 1.0, "A0").items()
               if k[0] == task}
        if not a0m:
            continue
        if task not in chance:
            die("ERR_DDC1_MALFORMED", "no chance level for task %r" % task)
        ch = float(chance[task])
        a0_acc = pooled_acc(a0m)
        if abs(a0_acc - ch) < CHANCE_DEGENERATE:
            ccr[task] = None  # degenerate denominator, disclosed (§5.2)
            continue
        ent = {}
        for (rg, rho, arm) in sorted(maps):
            if rg != "r135" or arm == "A0" or rho not in FULL_RHOS:
                continue
            tm = {k: v for k, v in maps[(rg, rho, arm)].items()
                  if k[0] == task}
            if tm:
                ent["%s@%s" % (arm, g(rho))] = \
                    (pooled_acc(tm) - ch) / (a0_acc - ch)
        ccr[task] = ent

    # ---- gate I-5 (recomputed from raw powers, ASM-1720) ----
    psr = side["power_sim_result"]
    sup = psr["superiority_power_min_over_c"]
    eqp = psr["equivalence_power"]
    qref_ok = psr.get("config", {}).get("q_ref") == 0.25
    i5_valid = (isinstance(sup, (int, float)) and sup >= 0.9
                and isinstance(eqp, (int, float)) and eqp >= 0.9
                and qref_ok and not psr.get("quick_mode", False))

    # ---- gate I-6 (energy-capture tripwire; flags, never blocks) ----
    caps = [(c["energy_capture"], key) for key, c in
            sorted(cell_idx.items()) if c["energy_capture"] is not None]
    i6_min = min(c for c, _ in caps) if caps else None
    i6_flagged = sorted("%s@%s@%s" % (arm, g(rho), rung)
                        for cap, (rung, arm, rho, seed) in caps
                        if cap < ENERGY_FLAG)

    # ---- A2/A3 minus A1 two-sided CIs ----
    def minus_a1_ci(name, arm):
        if not any(a == arm for (_rg, _rho, a) in maps):
            return None
        out = {}
        for rho in (0.75, 0.5):
            o = pb(name, rho)
            out["rho%s" % g(rho)] = o.ci95() if o is not None else None
        return out
    a2_ci = minus_a1_ci("a2_a1", "A2")
    a3_ci = minus_a1_ci("a3_a1", "A3")

    # ---- S1 -> S2 promotion (§8 verbatim) ----
    promotion = primary_pass
    for key, rho in (("delta_star_rho0.9", 0.9), ("delta_star_rho0.5",
                                                  0.5)):
        o = jb(rho)
        ratio = fluency_ratios.get(g(rho))
        if (key in survivors and o is not None and o.point > 0
                and ratio is not None and ratio <= FLUENCY_BOUND):
            promotion = True
    s2_sign = None
    if s2_ran and jb_360 is not None:
        s2_sign = 1 if jb_360.point > 0 else (-1 if jb_360.point < 0
                                              else 0)

    out = {
        "gates": {
            "i1_rotation_valid": bool(side["i1_rotation_valid"]),
            "i2_mechanics_valid": bool(side["i2_mechanics_valid"]),
            "i3_corpus_parity_valid": bool(side["i3_corpus_parity_valid"]),
            "i4_licenses_valid": bool(side["i4_licenses_valid"]),
            "i5_power_valid": i5_valid,
            "i5_superiority_power": sup,
            "i5_equivalence_power": eqp,
            "i5_least_favourable_c": psr["least_favourable_c"],
            "i5_infeasible_cells": psr["infeasible_cells"],
            "i6_energy_capture_min": i6_min,
            "i6_flagged_cells": i6_flagged,
            "per_item_emission_valid": bool(side["per_item_emission_valid"]),
            "completeness_valid": completeness(rows, cells, side),
        },
        "analysis": {
            "delta_star_lb95": delta_star_lb95,
            "delta_star_point": jb_primary.point,
            "primary_pass": primary_pass,
            "delta_a1_m1_point": pb_a1_m1.point,
            "delta_a1_r1_point": pb_a1_r1.point,
            "macro_delta_star": macro_delta_star,
            "measured_discordance": disc,
            "discordance_flags": disc_flags,
            "holm_family_p": fam_p,
            "holm_adjusted_p": fam_adj,
            "holm_survivors": survivors,
            "secondary_delta_star_by_rho": secondary_by_rho,
            "kernel_specificity_ci": kspec_ci,
            "tost_ci90": tost_ci90,
            "tost_a1_c1_equiv": tost_a1_c1,
            "tost_a1_c2_equiv": tost_a1_c2,
            "null_a1_m1_r1_equiv": null_equiv,
            "fluency_guard_ratios": fluency_ratios,
            "fluency_breached_cells": fluency_breached,
            "retention_curves": retention_curves,
            "chance_corrected_retention": ccr,
            "kill_a_fired": kill_a,
            "kill_b_fired": kill_b,
            "kill_c_fired": kill_c,
            "kill_fired": kill_fired,
            "a2_ran": a2_ran,
            "a2_minus_a1_ci": a2_ci,
            "a3_minus_a1_ci": a3_ci,
            "max_stat_outputs_carried": side["max_stat_outputs"],
            "s2_promotion_fired": promotion,
            "s2_replication_sign": s2_sign,
            "cost_ledger": {"usd_total": side["usd_total"],
                            "gpu_hours": side["gpu_hours"]},
        },
    }
    emitted = sorted("/%s/%s" % (top, k)
                     for top in ("gates", "analysis") for k in out[top])
    if emitted != sorted(OUTPUT_FIELDS):
        die("ERR_DDC1_MALFORMED",
            "output field set mismatch vs OUTPUT_FIELDS (internal)")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
