#!/usr/bin/env python3
"""f1k pre-registered analysis (stdin-conformant; verdict-gen P2 §3.1 step 5
invokes this with the ELIGIBLE results-log run records as JSONL on STDIN and
no argv — the rules_2_go_stdin.py / engine_inference_stdin.py contract).

Experiment: F1-K Kernel-as-Expert ADD path on GLM-5.2 (colibri C engine,
i4i instance). Design: docs/next/design/glm52-followup-experiment.md §2
(F1-K), as amended by §R (REVISION-1) through §R-REV5 (REVISION-5); where a
revision conflicts with §§1-10, the latest revision governs. Companion
record: registry/experiments/f1k.json. Cost approach: the maintainer's
reduced-cost GO (issue #28): R = 3 derangement passes (the §R6 pre-registered
degradation step 1, applied up front), spot/pinning savings are ops-side and
touch nothing statistical.

REGISTERED STATISTICS (implemented, not narrated):
  * Unit of inference = the concept CLUSTER (§R3.1/§R-REV4.1a). For a paired
    contrast (X vs Y): per-item d_i = correct_X(i) - correct_Y(i), per-cluster
    D_c = mean_{i in c} d_i, statistic T = mean_c D_c, reported in accuracy
    points (100*T).
  * PRIMARY TEST = one-sided cluster-level sign-flip permutation test:
    reference set = B random draws from the 2^C sign patterns, add-one
    corrected p = (1 + #{T_b >= T_obs}) / (B + 1), B = 10,000, deterministic
    per-contrast PRNG sub-seeds (global SEED below) => byte-identical stdout
    across reruns. Type-I exact under cluster sign-symmetry, for ANY
    within-cluster ICC (§R-REV4.1a; ASM-2122).
  * LICENSING RULE (joint, §R-REV3.1/§R-REV4.1): a ladder rung is licensed
    iff observed lift >= +3.0 accuracy points AND permutation p < 0.05. The
    Gaussian joint-MDE numbers are PLANNING approximations only (§R-REV5 /
    ASM-2130); they never enter this script's decisions.
  * LADDER (§2.6, ASM-2029/2036): K-1 = K vs b0; K-2 = K vs the per-item MEAN
    correctness over the R = 3 d1-drng derangement passes (dose-exact
    deflator, §R2); K-3 = K vs d2 (plain-dictionary knull). K-seam = K vs
    d3-text, DESCRIPTIVE both directions, never a rung. Failing rung n caps
    the claim at rung n-1.
  * d0 placebo (run-voiding, §2.6): d0 vs b0 one-sided sign-flip p < 0.05
    voids the instrument (NO +3 floor — noise sensitivity at any magnitude
    voids; conservative sharpening registered in the f1k record).
  * NULL (TOST at the +/-3.0-pt SESOI): cluster-level BCa 90% CI of the K-1
    statistic strictly inside (-3.0, +3.0), and NOT ceiling-bound.
  * KILL (harm direction): K-1 observed lift <= -3.0 points AND
    harm-direction sign-flip p < 0.05.
  * REPLACE non-inferiority (conditional arm, §R1.2/ASM-2037/2044/2124):
    cluster-level BCa one-sided 95% LB of (REPLACE - K) > -2.0 points AND
    measured expert-byte saving > 0; run/defer decided PRE-test (sidecar).
  * Ceiling-bound wording (§2.7): b0 accuracy > 0.95 on the subset =>
    /analysis/ceiling_bound true; a non-fire is then scoped "ceiling-bound at
    this subset", never a null (null_equiv is forced false).

INPUT CONTRACT: each eligible stdin record (event=="run", phase=="final",
exit=="ok") must carry artifacts.rows_path/rows_sha256 and
artifacts.sidecar_path/sidecar_sha256; all eligible records must pin the
SAME artifact tuple. Rows and sidecar are loaded from the pinned paths,
sha256 re-verified, fail closed; the analysis is a pure function of those
bytes. ROWS (JSONL), one row per scored (item x arm x pass):
  {item_id, cluster, arm in {b0,d0,d1-drng,d2,d3-text,K,REPLACE},
   pass (int; 1..3 for d1-drng, else 0), correct 0/1,
   tags [subset of {sense-pair, multi-concept, option-trigger}],
   pred_label, gold_label}
SIDECAR (JSON): manifest flags (pre-spend (A), B0, 5, 7, 6 committed;
test-untouched), off-concept guard result, scoring-template checks,
dose-exactness checks (R = 3 seeds vs the registered [101, 102, 103],
derangement fixed-point-free, layerwise norm-matched), replace
{ran, delta_r_dev, n_ni, io_saving_bytes_per_gated_token}, carriers
{params_added, table_bytes, concepts, layers}, power {rho_u,
joint_mde_points_at_rho_u, mc_exact_power}, cost {usd_total,
instance_hours, prefills}, b0_ceiling_threshold.

MOCK SELF-TEST: `python3 analysis/f1k.py --selftest` (optional argv; the
stdin path takes no flags) builds two synthetic campaigns (planted +10-pt
K lift; exact null) plus a pinned-file round-trip and asserts the full
verdict-bearing output surface. Exits 0 on green.

Fail-closed exits: any pin/shape violation prints ERR_P2_ANALYSIS to stderr
and exits 1 (=> verdict-gen ERR_P2_ANALYSIS); nothing falls back.

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Pre-registered constants (changing any is a design change requiring a
# --- new freeze; sources cited per line) ---
SEED = 20260713          # global PRNG seed (this freeze)
B = 10000                # sign-flip draws AND bootstrap resamples (§R3.1)
ALPHA = 0.05             # one-sided (§R3.1)
FLOOR_PTS = 3.0          # licensing effect floor, accuracy points (§2.7)
TOST_CI = 0.90           # NULL equivalence CI (two-sided 90%, §R1.2-style)
NI_MARGIN_PTS = 2.0      # REPLACE non-inferiority margin (§R1.2 / ASM-2037)
R_DRNG = 3               # derangement passes (R 5->3: §R6 degradation step 1,
                         # pre-applied per the maintainer's reduced-cost GO,
                         # issue #28; rank check granularity note below)
DRNG_SEEDS = [101, 102, 103]   # registered main-run derangement seeds
POWER_GATE_MIN_C = 65    # clusters with m >= 8 (§R-REV2.2 power gate)
POWER_GATE_MIN_M = 8
N_MAX = 1440             # hard cap (§R3.2 / §R-REV3.1 item 4)
CEILING_B0 = 0.95        # ceiling-bound threshold (§2.7)
MANDATORY_ARMS = ("b0", "d0", "d1-drng", "d2", "K")  # ladder arms, never
                                                     # droppable (§R6)

OUTPUT_FIELDS = [
    "/gates/freeze_manifest_valid",
    "/gates/power_gate_valid",
    "/gates/placebo_gate_valid",
    "/gates/off_concept_guard_valid",
    "/gates/scoring_template_valid",
    "/gates/dose_exactness_valid",
    "/gates/completeness_valid",
    "/analysis/n_items",
    "/analysis/n_clusters",
    "/analysis/clusters_with_m_ge_8",
    "/analysis/m_per_cluster_mean",
    "/analysis/b0_accuracy",
    "/analysis/ceiling_bound",
    "/analysis/k1_lift_points",
    "/analysis/k1_p",
    "/analysis/k1_ci95",
    "/analysis/k1_joint_pass",
    "/analysis/k2_lift_points",
    "/analysis/k2_p",
    "/analysis/k2_joint_pass",
    "/analysis/k2_rank_of_k",
    "/analysis/k3_lift_points",
    "/analysis/k3_p",
    "/analysis/k3_joint_pass",
    "/analysis/kseam_delta_points",
    "/analysis/d0_lift_points",
    "/analysis/d0_p",
    "/analysis/ladder_rung_reached",
    "/analysis/pass_gate",
    "/analysis/tost_ci90",
    "/analysis/null_equiv",
    "/analysis/kill_fired",
    "/analysis/replace_ran",
    "/analysis/replace_ni_lb95",
    "/analysis/replace_ni_pass",
    "/analysis/replace_io_saving",
    "/analysis/deflator_comparison",
    "/analysis/flip_matrix",
    "/analysis/position_bias",
    "/analysis/subgroups",
    "/analysis/power_scope",
    "/analysis/accuracy",
    "/analysis/params",
    "/analysis/memory",
    "/analysis/inference_compute",
    "/analysis/training_compute",
    "/analysis/cost_ledger",
]


def fail(msg):
    print("ERR_P2_ANALYSIS: %s" % msg, file=sys.stderr)
    sys.exit(1)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pinned(path, want_sha, what):
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / path
    try:
        raw = full.read_bytes()
    except OSError as e:
        fail("%s: cannot read pinned %s: %s" % (what, path, e))
    got = sha256_bytes(raw)
    if got != want_sha:
        fail("%s: %s sha256 %s != pinned %s" % (what, path, got, want_sha))
    return raw


# ---------------------------------------------------------------------------
# Data marshalling (fail-closed)
# ---------------------------------------------------------------------------
def index_rows(rows):
    """rows -> {arm: {pass: {item_id: correct}}}; plus item->cluster map and
    item->tags. Duplicate (arm, pass, item) rows are a harness bug."""
    byarm, clusters, tags, labels = {}, {}, {}, {}
    for r in rows:
        for k in ("item_id", "cluster", "arm", "correct"):
            if k not in r:
                fail("row missing %r: %s" % (k, json.dumps(r)[:200]))
        arm, p, iid = r["arm"], int(r.get("pass", 0) or 0), r["item_id"]
        d = byarm.setdefault(arm, {}).setdefault(p, {})
        if iid in d:
            fail("duplicate row (arm=%s pass=%d item=%s)" % (arm, p, iid))
        d[iid] = float(r["correct"])
        prev = clusters.setdefault(iid, r["cluster"])
        if prev != r["cluster"]:
            fail("item %s carries two clusters (%s, %s)" % (iid, prev,
                                                            r["cluster"]))
        tags.setdefault(iid, set()).update(r.get("tags") or [])
        if r.get("pred_label") is not None:
            labels.setdefault(arm, []).append(
                (r.get("pred_label"), r.get("gold_label")))
    return byarm, clusters, tags, labels


def arm_items(byarm, arm, p=0):
    return byarm.get(arm, {}).get(p, {})


def drng_mean(byarm):
    """Per-item MEAN correctness over the R registered derangement passes
    (§R2 rung-K-2 control). Requires ALL R passes per item (fail closed)."""
    passes = byarm.get("d1-drng", {})
    if sorted(passes) != list(range(1, R_DRNG + 1)):
        return None
    items = set(passes[1])
    for p in range(2, R_DRNG + 1):
        items &= set(passes[p])
    return {i: sum(passes[p][i] for p in range(1, R_DRNG + 1)) / R_DRNG
            for i in items}


# ---------------------------------------------------------------------------
# Registered statistics
# ---------------------------------------------------------------------------
def cluster_diffs(xa, xb, clusters):
    """Paired per-item diffs -> sorted list of cluster means D_c (fractions).
    Pairing over the shared item set; clusters with zero shared items drop."""
    shared = sorted(set(xa) & set(xb))
    acc = {}
    for i in shared:
        acc.setdefault(clusters[i], []).append(xa[i] - xb[i])
    return [sum(v) / len(v) for _, v in sorted(acc.items())], len(shared)


def signflip(dcs, name, b=B):
    """One-sided cluster sign-flip permutation test of T = mean_c D_c > 0.
    Returns (T_points, p). Add-one corrected over b random sign patterns
    (§R3.1; identity counted via the correction)."""
    C = len(dcs)
    if C == 0:
        return None, None
    t_obs = sum(dcs) / C
    rng = random.Random("%d|%s" % (SEED, name))
    ge = 0
    for _ in range(b):
        t = sum(d if rng.random() < 0.5 else -d for d in dcs) / C
        if t >= t_obs:
            ge += 1
    return 100.0 * t_obs, (1 + ge) / (b + 1)


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


class ClusterBCa:
    """BCa bootstrap of T = mean_c D_c, resampling CLUSTERS with
    replacement (§R1.2 / §R-REV4.1a fallback machinery; used here for the
    TOST CI and the REPLACE-NI lower bound). Deterministic sub-seeded."""

    def __init__(self, dcs, name, b=B):
        self.n = len(dcs)
        if self.n == 0:
            self.theta = None
            return
        self.theta = sum(dcs) / self.n
        rng = random.Random("%d|bca|%s" % (SEED, name))
        boots = []
        for _ in range(b):
            tot = 0.0
            for _j in range(self.n):
                tot += dcs[rng.randrange(self.n)]
            boots.append(tot / self.n)
        self.boots = sorted(boots)
        self.b = b
        self.degenerate = (self.boots[0] == self.boots[-1])
        prop = sum(1 for x in self.boots if x < self.theta) / b
        self.z0 = _norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
        if self.n > 1:
            jack = [(sum(dcs) - x) / (self.n - 1) for x in dcs]
        else:
            jack = [self.theta]
        jm = sum(jack) / len(jack)
        num = sum((jm - j) ** 3 for j in jack)
        den = 6 * (sum((jm - j) ** 2 for j in jack) ** 1.5) or 1e-12
        self.a = num / den

    def _q(self, alpha):
        if self.degenerate:
            return self.theta
        zq = _norm_ppf(alpha)
        adj = _norm_cdf(self.z0 + (self.z0 + zq)
                        / (1 - self.a * (self.z0 + zq)))
        idx = min(max(int(adj * self.b), 0), self.b - 1)
        return self.boots[idx]

    def lb(self, alpha=ALPHA):
        return None if self.theta is None else self._q(alpha)

    def ub(self, alpha=ALPHA):
        return None if self.theta is None else self._q(1 - alpha)


# ---------------------------------------------------------------------------
# The pure analysis function (rows + sidecar bytes -> output dict)
# ---------------------------------------------------------------------------
def analyze(rows, side):
    byarm, clusters, tags, labels = index_rows(rows)
    b0 = arm_items(byarm, "b0")
    karm = arm_items(byarm, "K")
    d0 = arm_items(byarm, "d0")
    d2 = arm_items(byarm, "d2")
    d3 = arm_items(byarm, "d3-text")
    drng = drng_mean(byarm)
    if not b0 or not karm:
        fail("mandatory arms b0/K missing from rows")

    # --- gates -------------------------------------------------------------
    man = side.get("manifest") or {}
    manifest_valid = all(bool(man.get(k)) for k in (
        "pre_spend_committed", "b0_addendum_committed", "entry5_committed",
        "entry7_committed", "entry6_committed",
        "test_untouched_until_complete"))

    csizes = {}
    for i in b0:
        csizes[clusters[i]] = csizes.get(clusters[i], 0) + 1
    n_items = len(b0)
    n_clusters = len(csizes)
    c_ge8 = sum(1 for v in csizes.values() if v >= POWER_GATE_MIN_M)
    m_mean = (n_items / n_clusters) if n_clusters else None
    power_gate = (c_ge8 >= POWER_GATE_MIN_C and n_items <= N_MAX)

    guard = side.get("guard") or {}
    guard_valid = bool(guard.get("byte_identical"))

    tpl = side.get("template") or {}
    template_valid = all(bool(tpl.get(k)) for k in (
        "labels_single_token", "header_cue_labels_trigger_free"))

    dose = side.get("dose") or {}
    dose_valid = (list(dose.get("r_seeds") or []) == DRNG_SEEDS
                  and bool(dose.get("derangement_no_fixed_point"))
                  and bool(dose.get("norm_matched_within_tol"))
                  and drng is not None)

    # placebo: d0 vs b0 one-sided sign-flip; p < 0.05 VOIDS (no +3 floor)
    d0_dcs, _ = cluster_diffs(d0, b0, clusters)
    d0_lift, d0_p = signflip(d0_dcs, "d0_vs_b0")
    placebo_valid = (d0_p is not None and d0_p >= ALPHA)

    # completeness: every mandatory arm scores every b0 test item
    complete = True
    for arm in MANDATORY_ARMS:
        if arm == "d1-drng":
            complete &= (drng is not None and set(b0) <= set(drng))
        else:
            complete &= set(b0) <= set(arm_items(byarm, arm))

    gates = {
        "freeze_manifest_valid": bool(manifest_valid),
        "power_gate_valid": bool(power_gate),
        "placebo_gate_valid": bool(placebo_valid),
        "off_concept_guard_valid": bool(guard_valid),
        "scoring_template_valid": bool(template_valid),
        "dose_exactness_valid": bool(dose_valid),
        "completeness_valid": bool(complete),
    }

    # --- ladder ------------------------------------------------------------
    def rung(xa, xb, name):
        dcs, _ = cluster_diffs(xa, xb, clusters)
        lift, p = signflip(dcs, name)
        fired = (lift is not None and p is not None
                 and lift >= FLOOR_PTS and p < ALPHA)
        return dcs, lift, p, bool(fired)

    k1_dcs, k1_lift, k1_p, k1_fire = rung(karm, b0, "k1_K_vs_b0")
    if drng is not None:
        _, k2_lift, k2_p, k2_fire = rung(karm, drng, "k2_K_vs_drngmean")
    else:
        k2_lift = k2_p = None
        k2_fire = False
    _, k3_lift, k3_p, k3_fire = rung(karm, d2, "k3_K_vs_d2") if d2 else \
        (None, None, None, False)

    # K-seam descriptive (never a rung)
    if d3:
        ks_dcs, _ = cluster_diffs(karm, d3, clusters)
        kseam = 100.0 * sum(ks_dcs) / len(ks_dcs) if ks_dcs else None
    else:
        kseam = None

    ladder = 0
    if k1_fire:
        ladder = 1
        if k2_fire:
            ladder = 2
            if k3_fire:
                ladder = 3
    pass_gate = bool(k1_fire and k2_fire)  # deflator discipline (ASM-2029):
    # a PASS licenses "kernel-aligned content helps", never "any content
    # helps"; K-3 elevates wording only (kernel-vs-dictionary), not verdict.

    # --- NULL (TOST) + kill + ceiling ---------------------------------------
    b0_acc = sum(b0.values()) / len(b0)
    ceiling = b0_acc > float(side.get("b0_ceiling_threshold", CEILING_B0))
    bca = ClusterBCa([100.0 * d for d in k1_dcs], "k1_tost")
    a2 = (1 - TOST_CI) / 2
    tost = ([bca.lb(a2), bca.ub(a2)] if bca.theta is not None else None)
    null_equiv = bool(tost is not None and tost[0] is not None
                      and -FLOOR_PTS < tost[0] and tost[1] < FLOOR_PTS
                      and not ceiling)
    harm_lift, harm_p = signflip([-d for d in k1_dcs], "k1_harm")
    kill = bool(k1_lift is not None and k1_lift <= -FLOOR_PTS
                and harm_p is not None and harm_p < ALPHA)

    # --- REPLACE non-inferiority (conditional) -------------------------------
    rep = arm_items(byarm, "REPLACE")
    rep_side = side.get("replace") or {}
    rep_ran = bool(rep) and bool(rep_side.get("ran"))
    if rep_ran:
        rdcs, _ = cluster_diffs(rep, karm, clusters)
        rlb = ClusterBCa([100.0 * d for d in rdcs], "replace_ni").lb(ALPHA)
        io = rep_side.get("io_saving_bytes_per_gated_token")
        rep_pass = bool(rlb is not None and rlb > -NI_MARGIN_PTS
                        and io is not None and io > 0)
    else:
        rlb, io, rep_pass = None, None, False

    # --- descriptives --------------------------------------------------------
    def acc_of(d):
        return (sum(d.values()) / len(d)) if d else None

    passes = byarm.get("d1-drng", {})
    per_pass = {("pass%d" % p): acc_of(passes.get(p) or {})
                for p in range(1, R_DRNG + 1)}
    k_acc = acc_of(karm)
    ranked = sorted([v for v in per_pass.values() if v is not None]
                    + ([k_acc] if k_acc is not None else []), reverse=True)
    k_rank = (1 + ranked.index(k_acc)) if k_acc in ranked else None
    deflator_comparison = {
        "k_accuracy": k_acc,
        "drng_per_pass_accuracy": per_pass,
        "d2_accuracy": acc_of(d2),
        "d0_accuracy": acc_of(d0),
        "b0_accuracy": b0_acc,
        "k_rank_note": "descriptive ONLY: K's rank among {K} + the R=%d "
                       "derangement passes; best-of-%d nominal %.3f — the "
                       "R 5->3 reduction (§R6 step 1, maintainer reduced-cost "
                       "GO) coarsens this check, disclosed" % (
                           R_DRNG, R_DRNG + 1, 1.0 / (R_DRNG + 1)),
    }

    shared_k1 = sorted(set(karm) & set(b0))
    flip = {
        "corrections": sum(1 for i in shared_k1
                           if karm[i] > b0[i]),
        "regressions": sum(1 for i in shared_k1
                           if karm[i] < b0[i]),
        "unchanged": sum(1 for i in shared_k1 if karm[i] == b0[i]),
    }
    position_bias = {}
    for arm, pairs in sorted(labels.items()):
        dist = {}
        for pred, _gold in pairs:
            dist[str(pred)] = dist.get(str(pred), 0) + 1
        position_bias[arm] = dist
    subgroups = {}
    for tag in ("sense-pair", "multi-concept", "option-trigger"):
        ids = [i for i in shared_k1 if tag in tags.get(i, ())]
        if ids:
            subgroups[tag] = {
                "n": len(ids),
                "k1_lift_points": 100.0 * (sum(karm[i] - b0[i]
                                               for i in ids) / len(ids)),
                "note": "descriptive subgroup (§2.7/§R-REV2.1), never an "
                        "endpoint"}

    power = side.get("power") or {}
    power_scope = {
        "rho_u_planning": power.get("rho_u"),
        "joint_mde_points_at_rho_u": power.get("joint_mde_points_at_rho_u"),
        "mc_exact_power": power.get("mc_exact_power"),
        "wording": "PLANNING APPROXIMATION (Gaussian large-sample) per "
                   "§R-REV5/ASM-2130 — the licensing decision uses ONLY the "
                   "exact sign-flip p and the +3-pt floor; a non-fire is "
                   "scoped 'powered to resolve >= the joint MDE at rho_U', "
                   "never a clean null at +3.",
    }

    car = side.get("carriers") or {}
    cost = side.get("cost") or {}
    out = {"gates": gates, "analysis": {
        "n_items": n_items,
        "n_clusters": n_clusters,
        "clusters_with_m_ge_8": c_ge8,
        "m_per_cluster_mean": m_mean,
        "b0_accuracy": b0_acc,
        "ceiling_bound": bool(ceiling),
        "k1_lift_points": k1_lift, "k1_p": k1_p,
        "k1_ci95": ([bca.lb(0.025), bca.ub(0.025)]
                    if bca.theta is not None else None),
        "k1_joint_pass": k1_fire,
        "k2_lift_points": k2_lift, "k2_p": k2_p, "k2_joint_pass": k2_fire,
        "k2_rank_of_k": k_rank,
        "k3_lift_points": k3_lift, "k3_p": k3_p, "k3_joint_pass": k3_fire,
        "kseam_delta_points": kseam,
        "d0_lift_points": d0_lift, "d0_p": d0_p,
        "ladder_rung_reached": ladder,
        "pass_gate": pass_gate,
        "tost_ci90": tost,
        "null_equiv": null_equiv,
        "kill_fired": kill,
        "replace_ran": rep_ran,
        "replace_ni_lb95": rlb,
        "replace_ni_pass": rep_pass,
        "replace_io_saving": io,
        "deflator_comparison": deflator_comparison,
        "flip_matrix": flip,
        "position_bias": position_bias,
        "subgroups": subgroups,
        "power_scope": power_scope,
        "accuracy": k_acc,
        "params": {
            "host_params_unchanged": True,
            "carrier_params_added": car.get("params_added"),
            "note": "training-free splice; native experts intact (ADD)"},
        "memory": {"carrier_table_bytes": car.get("table_bytes"),
                   "concepts": car.get("concepts"),
                   "layers": car.get("layers")},
        "inference_compute": {
            "prefills_total": cost.get("prefills"),
            "replace_io_saving_bytes_per_gated_token": io,
            "note": "one prefill per item per arm (§R1.1); ADD adds one "
                    "axpy per gated (token, layer) — no expert load change"},
        "training_compute": {
            "flops": 0,
            "note": "identically ZERO by construction — forward passes + "
                    "mean-difference arithmetic only (§2.4)"},
        "cost_ledger": {"usd_total": cost.get("usd_total"),
                        "instance_hours": cost.get("instance_hours"),
                        "prefills": cost.get("prefills")},
    }}
    return out


# ---------------------------------------------------------------------------
# Input acquisition (verdict-gen stdin contract)
# ---------------------------------------------------------------------------
def load_from_stdin():
    eligible = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            fail("stdin line is not JSON")
        if rec.get("event") == "run" and rec.get("phase") == "final" \
                and rec.get("exit") == "ok":
            eligible.append(rec)
    if not eligible:
        fail("no eligible run records on stdin")
    pins = set()
    for rec in eligible:
        art = rec.get("artifacts") or {}
        for k in ("rows_path", "rows_sha256", "sidecar_path",
                  "sidecar_sha256"):
            if not art.get(k):
                fail("eligible record lacks artifacts.%s" % k)
        pins.add((art["rows_path"], art["rows_sha256"],
                  art["sidecar_path"], art["sidecar_sha256"]))
    if len(pins) != 1:
        fail("eligible records pin DIFFERENT artifacts: %s" % sorted(pins))
    rows_path, rows_sha, side_path, side_sha = next(iter(pins))
    rows_raw = read_pinned(rows_path, rows_sha, "f1k rows")
    side_raw = read_pinned(side_path, side_sha, "f1k sidecar")
    try:
        rows = [json.loads(x) for x in rows_raw.decode("utf-8").splitlines()
                if x.strip()]
        side = json.loads(side_raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        fail("pinned artifact is malformed: %s" % e)
    if not isinstance(side, dict):
        fail("sidecar is not a JSON object")
    return rows, side


# ---------------------------------------------------------------------------
# MOCK self-test
# ---------------------------------------------------------------------------
def _mock_campaign(p_by_arm, rng, C=72, m=20, shared_null=False):
    """shared_null=True plants an EXACT per-item null: one correctness draw
    shared by every arm/pass, so every paired diff is identically 0 (the
    TOST/NULL shape); otherwise arms draw independently at their p."""
    rows = []
    lab = "ABCD"
    for c in range(C):
        for j in range(m):
            iid = "it-%03d-%02d" % (c, j)
            gold = lab[rng.randrange(4)]
            base = rng.random()
            for arm, p in p_by_arm.items():
                if arm == "d1-drng":
                    for pss in range(1, R_DRNG + 1):
                        ok = (1 if base < p else 0) if shared_null else \
                            (1 if rng.random() < p else 0)
                        rows.append({"item_id": iid,
                                     "cluster": "c-%03d" % c,
                                     "arm": arm, "pass": pss, "correct": ok,
                                     "pred_label": gold if ok else
                                     lab[(lab.index(gold) + 1) % 4],
                                     "gold_label": gold, "tags": []})
                else:
                    ok = (1 if base < p else 0) if shared_null else \
                        (1 if rng.random() < p else 0)
                    rows.append({"item_id": iid, "cluster": "c-%03d" % c,
                                 "arm": arm, "pass": 0, "correct": ok,
                                 "pred_label": gold if ok else
                                 lab[(lab.index(gold) + 1) % 4],
                                 "gold_label": gold,
                                 "tags": (["sense-pair"] if c < 4 else [])})
    return rows


def _mock_sidecar():
    return {
        "manifest": {"pre_spend_committed": True,
                     "b0_addendum_committed": True,
                     "entry5_committed": True, "entry7_committed": True,
                     "entry6_committed": True,
                     "test_untouched_until_complete": True},
        "guard": {"n_items": 60, "byte_identical": True},
        "template": {"labels_single_token": True,
                     "header_cue_labels_trigger_free": True},
        "dose": {"r_seeds": DRNG_SEEDS, "derangement_no_fixed_point": True,
                 "norm_matched_within_tol": True},
        "replace": {"ran": False, "delta_r_dev": None, "n_ni": None,
                    "io_saving_bytes_per_gated_token": None},
        "carriers": {"params_added": 96 * 4 * 6144, "table_bytes": 9437184,
                     "concepts": 96, "layers": 4},
        "power": {"rho_u": 0.10, "joint_mde_points_at_rho_u": 4.09,
                  "mc_exact_power": {"mu_star": 4.09, "n_sim": 10000,
                                     "joint_power": 0.81, "seed": SEED,
                                     "pass": True}},
        "cost": {"usd_total": 0.0, "instance_hours": 0.0, "prefills": 11520},
        "b0_ceiling_threshold": CEILING_B0,
    }


def selftest():
    def check(cond, msg):
        if not cond:
            print("MOCK-SELFTEST FAIL: %s" % msg, file=sys.stderr)
            sys.exit(1)

    # Mock A — planted +10-pt K lift over b0/d0/drng; d2 close (+2 pts)
    rng = random.Random(4242)
    rows_a = _mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                             "d2": 0.78, "d3-text": 0.71, "K": 0.80}, rng)
    out_a = analyze(rows_a, _mock_sidecar())
    g = out_a["gates"]
    a = out_a["analysis"]
    check(all(g.values()), "mock A: some gate failed: %s" % g)
    check(a["k1_joint_pass"], "mock A: K-1 did not fire (lift=%s p=%s)"
          % (a["k1_lift_points"], a["k1_p"]))
    check(a["k2_joint_pass"], "mock A: K-2 did not fire")
    check(a["pass_gate"], "mock A: pass_gate false")
    check(not a["kill_fired"], "mock A: kill fired")
    check(not a["null_equiv"], "mock A: null_equiv true under planted lift")
    check(a["ladder_rung_reached"] >= 2, "mock A: ladder < 2")
    check(a["n_items"] == 1440 and a["n_clusters"] == 72,
          "mock A: grid wrong")

    # Mock B — exact per-item null: every arm shares each item's draw
    rng = random.Random(2424)
    rows_b = _mock_campaign({k: 0.75 for k in
                             ("b0", "d0", "d1-drng", "d2", "d3-text", "K")},
                            rng, shared_null=True)
    out_b = analyze(rows_b, _mock_sidecar())
    bnl = out_b["analysis"]
    check(not bnl["pass_gate"], "mock B: pass_gate true under null")
    check(not bnl["kill_fired"], "mock B: kill fired under null")
    check(bnl["null_equiv"], "mock B: TOST did not certify the planted "
          "null (ci90=%s)" % bnl["tost_ci90"])

    # Pinned-file round-trip (exercises the stdin/pin path end-to-end)
    import io
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rp = Path(td) / "rows.jsonl"
        sp = Path(td) / "sidecar.json"
        rp.write_text("\n".join(json.dumps(r) for r in rows_a) + "\n",
                      encoding="utf-8")
        sp.write_text(json.dumps(_mock_sidecar()), encoding="utf-8")
        rec = {"event": "run", "phase": "final", "exit": "ok",
               "artifacts": {"rows_path": str(rp),
                             "rows_sha256": sha256_bytes(rp.read_bytes()),
                             "sidecar_path": str(sp),
                             "sidecar_sha256": sha256_bytes(sp.read_bytes())}}
        old = sys.stdin
        sys.stdin = io.StringIO(json.dumps(rec) + "\n")
        try:
            rows2, side2 = load_from_stdin()
        finally:
            sys.stdin = old
        out2 = analyze(rows2, side2)
        check(out2 == out_a, "pin round-trip output differs from in-memory")

    # Output-surface completeness: every OUTPUT_FIELDS pointer resolves
    for ptr in OUTPUT_FIELDS:
        node = out_a
        for part in ptr.strip("/").split("/"):
            check(isinstance(node, dict) and part in node,
                  "output field %s missing" % ptr)
            node = node[part]
    print("MOCK-SELFTEST PASS: planted-lift verdict shape (PASS-bound, "
          "ladder rung %d), planted-null TOST NULL-bound, pin round-trip "
          "byte-stable, %d output fields present."
          % (out_a["analysis"]["ladder_rung_reached"], len(OUTPUT_FIELDS)))
    return 0


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    rows, side = load_from_stdin()
    out = analyze(rows, side)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
