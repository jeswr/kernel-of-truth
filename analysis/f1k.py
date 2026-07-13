#!/usr/bin/env python3
"""f1k pre-registered analysis (stdin-conformant; verdict-gen P2 §3.1 step 5
invokes this with the ELIGIBLE results-log run records as JSONL on STDIN and
no argv — the rules_2_go_stdin.py / engine_inference_stdin.py contract).

Experiment: F1-K Kernel-as-Expert ADD path on GLM-5.2 (colibri C engine,
i4i instance). Design: docs/next/design/glm52-followup-experiment.md §2
(F1-K), as amended by §R (REVISION-1) through §R-REV5 (REVISION-5); where a
revision conflicts with §§1-10, the latest revision governs. Companion
record: registry/experiments/f1k.json. Cost approach: the maintainer's
reduced-cost GO (issue #28) as validated by
docs/next/design/glm52-f1k-cost-reduction.md (ASM-2205, $149 ceiling):
R = 3 derangement passes (the §R6 pre-registered degradation step 1, applied
up front), spot/pinning savings are ops-side and touch nothing statistical.

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
  * K-2 EXACTNESS BASIS (explicit, per the codex FIX-FIRST review
    2026-07-13): the K-2 sign-flip (K vs the per-item derangement MEAN) is
    exact ONLY under the EXPLICIT cluster sign-symmetry assumption on
    D_c = mean_c(K - mean_R(d1-drng)) registered as ASM-2280. Four-arm
    carrier exchangeability alone does NOT deliver it — the review's
    counterexample (an exchangeable null in which exactly 3 of the 4 carrier
    assignments score an item correct) rejects at ~6.28%, not 5%, at C = 72.
    The registered remedy when sign-symmetry cannot be trusted is the
    dev-selected BCa fallback below; the K-1 basis (ASM-2122) is unchanged.
  * DEV-SELECTED INFERENCE METHOD + BCa FALLBACK BRANCH (IMPLEMENTED,
    §R-REV4.1a): the choice between the sign-flip test and the cluster
    (concept-block) BCa bootstrap is frozen PRE-TEST at freeze-manifest
    addendum (6) from the dev-split sign-symmetry check — never from test
    data — and carried in the sidecar as
    inference = {method: "signflip"|"bca", dev_sign_symmetry_pass: bool}
    (coherence enforced fail-closed: method == "signflip" iff the dev check
    passed). Under "bca" EVERY directional contrast (K-1, K-2, K-3, d0
    placebo, harm/kill) takes p = the cluster-BCa CI-inversion one-sided p
    (p < a  <=>  BCa one-sided lower bound at level a clears 0, by
    construction), same +3.0-pt joint rule. The method used is reported at
    /analysis/inference_method.
  * LICENSING RULE (joint, §R-REV3.1/§R-REV4.1): a ladder rung is licensed
    iff observed lift >= +3.0 accuracy points AND p < 0.05 (p per the
    dev-selected method above). The Gaussian joint-MDE numbers are PLANNING
    approximations only (§R-REV5 / ASM-2130); they never enter this
    script's decisions.
  * LADDER (§2.6, ASM-2029/2036): K-1 = K vs b0; K-2 = K vs the per-item MEAN
    correctness over the R = 3 d1-drng derangement passes (dose-exact
    deflator, §R2); K-3 = K vs d2 (plain-dictionary knull). K-seam = K vs
    d3-text, DESCRIPTIVE both directions, never a rung. Failing rung n caps
    the claim at rung n-1. Cluster-BCa 95% CIs are REGISTERED OUTPUTS for
    all three rungs (/analysis/k1_ci95, k2_ci95, k3_ci95).
  * d0 placebo (run-voiding, §2.6): d0 vs b0 one-sided p < 0.05 voids the
    instrument (NO +3 floor — noise sensitivity at any magnitude voids;
    conservative sharpening registered in the f1k record, ASM-2273).
  * NULL (TOST at the +/-3.0-pt SESOI): cluster-level BCa 90% CI of the K-1
    statistic strictly inside (-3.0, +3.0), and NOT ceiling-bound.
  * KILL (harm direction): K-1 observed lift <= -3.0 points AND
    harm-direction p < 0.05 (dev-selected method).
  * REPLACE non-inferiority (conditional arm, §R1.2/ASM-2037/2044/2124):
    cluster-level BCa one-sided 95% LB of (REPLACE - K) > -2.0 points AND
    measured expert-byte saving > 0; run/defer decided PRE-test (sidecar).
  * Ceiling-bound wording (§2.7): b0 accuracy > 0.95 on the subset =>
    /analysis/ceiling_bound true; a non-fire is then scoped "ceiling-bound at
    this subset", never a null (null_equiv is forced false). The 0.95
    threshold is IMMUTABLE (CEILING_B0 below): a sidecar carrying any other
    b0_ceiling_threshold is rejected fail-closed.

HARDENED VALIDATION (codex FIX-FIRST review 2026-07-13; all fail-closed
ERR_P2_ANALYSIS, never gates):
  * n EXACT: the b0 test-item universe must contain EXACTLY N_REGISTERED =
    1,440 items (the design runs AT the cap, §R-REV3.1 item 4); any other n
    (e.g. 520) is rejected, not analyzed.
  * NO ARM SUPERSETS: every (arm, pass) may score ONLY items in the b0
    universe; any item outside it is rejected (mandatory-arm UNDER-coverage
    stays an INSTRUMENT-INVALID gate: /gates/completeness_valid).
  * BINARY correctness: row "correct" must equal 0 or 1 (bools and any
    non-binary value rejected).
  * IMMUTABLE thresholds: the ceiling threshold is the pinned constant; the
    sidecar cannot move it.
  * REPLACE coherence: REPLACE rows present iff sidecar replace.ran; when
    ran, REPLACE must score the full universe (no partial-NI).

INPUT CONTRACT: each eligible stdin record (event=="run", phase=="final",
exit=="ok") must carry artifacts.rows_path/rows_sha256 and
artifacts.sidecar_path/sidecar_sha256; all eligible records must pin the
SAME artifact tuple. Rows and sidecar are loaded from the pinned paths,
sha256 re-verified, fail closed; the analysis is a pure function of those
bytes. ROWS (JSONL), one row per scored (item x arm x pass):
  {item_id, cluster, arm in {b0,d0,d1-drng,d2,d3-text,K,REPLACE},
   pass (int; 1..3 for d1-drng, else 0), correct 0/1 (STRICTLY binary),
   tags [subset of {sense-pair, multi-concept, option-trigger}],
   pred_label, gold_label}
SIDECAR (JSON): manifest flags (pre-spend (A), B0, 5, 7, 6 committed;
test-untouched), off-concept guard result, scoring-template checks,
dose-exactness checks (R = 3 seeds vs the registered [101, 102, 103],
derangement fixed-point-free, layerwise norm-matched), inference {method
"signflip"|"bca", dev_sign_symmetry_pass} (the §R-REV4.1a dev-selected
choice, frozen at addendum (6)), replace {ran, delta_r_dev, n_ni,
io_saving_bytes_per_gated_token}, carriers {params_added, table_bytes,
concepts, layers}, power {rho_u, joint_mde_points_at_rho_u,
mc_exact_power}, cost {usd_total, instance_hours, prefills},
b0_ceiling_threshold (optional; MUST equal 0.95 if present).

MOCK SELF-TEST: `python3 analysis/f1k.py --selftest` (optional argv; the
stdin path takes no flags) builds three synthetic campaigns (planted +10-pt
K lift on the sign-flip branch; the SAME campaign on the BCa fallback
branch; exact null) plus a pinned-file round-trip, asserts the full
verdict-bearing output surface, and probes every hardened rejection
(n != 1,440, arm superset, non-binary correct, mutated ceiling threshold,
incoherent inference method). Exits 0 on green.

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
N_REGISTERED = 1440      # the design runs AT the cap (§R-REV3.1 item 4);
                         # any other realized n is REJECTED fail-closed
N_MAX = 1440             # hard cap (§R3.2 / §R-REV3.1 item 4)
CEILING_B0 = 0.95        # ceiling-bound threshold (§2.7) — IMMUTABLE; a
                         # sidecar carrying a different value is rejected
INFERENCE_METHODS = ("signflip", "bca")  # §R-REV4.1a dev-selected choice
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
    "/analysis/inference_method",
    "/analysis/k1_lift_points",
    "/analysis/k1_p",
    "/analysis/k1_ci95",
    "/analysis/k1_joint_pass",
    "/analysis/k2_lift_points",
    "/analysis/k2_p",
    "/analysis/k2_ci95",
    "/analysis/k2_joint_pass",
    "/analysis/k2_rank_of_k",
    "/analysis/k3_lift_points",
    "/analysis/k3_p",
    "/analysis/k3_ci95",
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
    item->tags. Duplicate (arm, pass, item) rows are a harness bug.
    HARDENED: "correct" must be STRICTLY binary (0 or 1; bools rejected) —
    a fractional or boolean correctness value is a scorer defect, not data."""
    byarm, clusters, tags, labels = {}, {}, {}, {}
    for r in rows:
        for k in ("item_id", "cluster", "arm", "correct"):
            if k not in r:
                fail("row missing %r: %s" % (k, json.dumps(r)[:200]))
        c = r["correct"]
        if isinstance(c, bool) or not (c == 0 or c == 1):
            fail("non-binary correct %r (must be 0 or 1): %s"
                 % (c, json.dumps(r)[:200]))
        arm, p, iid = r["arm"], int(r.get("pass", 0) or 0), r["item_id"]
        d = byarm.setdefault(arm, {}).setdefault(p, {})
        if iid in d:
            fail("duplicate row (arm=%s pass=%d item=%s)" % (arm, p, iid))
        d[iid] = int(c)
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
    (§R3.1; identity counted via the correction). Exact ONLY under the
    registered cluster sign-symmetry null: ASM-2122 grounds it for K-1;
    K-2 additionally requires the EXPLICIT ASM-2280 assumption (four-arm
    exchangeability alone is insufficient — see the module docstring)."""
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
    replacement (§R1.2 / §R-REV4.1a fallback machinery; carries the rung
    95% CIs, the TOST CI, the REPLACE-NI lower bound, AND — when the
    dev-selected method is 'bca' — the fallback-branch one-sided p via CI
    inversion). Deterministic sub-seeded."""

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

    def p_one_sided(self):
        """CI-inversion one-sided p for H1: T > 0 — the smallest alpha at
        which the BCa lower bound clears 0, so p < a <=> lb(a) > 0 by
        construction (the §R-REV4.1a fallback branch's p). Deterministic
        bisection over the same _q the CIs use; add-one floored at
        1/(B+1), capped at 1."""
        if self.theta is None:
            return None
        floor = 1.0 / (self.b + 1)
        if self.degenerate:
            return floor if self.theta > 0 else 1.0
        lo, hi = floor, 1.0 - 1e-12
        if self._q(lo) > 0:
            return floor
        if self._q(hi) <= 0:
            return 1.0
        for _ in range(60):          # lb(lo) <= 0 < lb(hi) invariant
            mid = (lo + hi) / 2
            if self._q(mid) > 0:
                hi = mid
            else:
                lo = mid
        return max(floor, min(1.0, hi))


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

    # --- HARDENED VALIDATION (codex FIX-FIRST review; fail-closed) ---------
    universe = set(b0)
    if len(universe) != N_REGISTERED:
        fail("registered n violated: b0 scores %d items but the frozen "
             "design runs AT the cap n = %d (§R-REV3.1 item 4) — any other "
             "realized n is rejected, never analyzed" % (len(universe),
                                                         N_REGISTERED))
    for arm in sorted(byarm):
        for p in sorted(byarm[arm]):
            extra = sorted(set(byarm[arm][p]) - universe)
            if extra:
                fail("arm %s pass %d scores %d item(s) OUTSIDE the "
                     "registered b0 test set (arm supersets rejected): %s"
                     % (arm, p, len(extra), extra[:5]))

    # Immutable decision threshold: the sidecar may echo the pinned ceiling
    # but can NEVER move it (§2.7; mutable-threshold rejection).
    if "b0_ceiling_threshold" in side \
            and side["b0_ceiling_threshold"] != CEILING_B0:
        fail("sidecar b0_ceiling_threshold %r != pinned CEILING_B0 %s — "
             "decision thresholds are immutable at freeze"
             % (side["b0_ceiling_threshold"], CEILING_B0))

    # Dev-selected inference method (§R-REV4.1a): frozen at addendum (6)
    # from the dev sign-symmetry check, coherence enforced fail-closed.
    inf = side.get("inference") or {}
    method = inf.get("method")
    if method not in INFERENCE_METHODS:
        fail("sidecar inference.method %r not in %s (the §R-REV4.1a "
             "dev-selected sign-flip-vs-BCa choice, frozen at addendum (6), "
             "is mandatory)" % (method, list(INFERENCE_METHODS)))
    sym = inf.get("dev_sign_symmetry_pass")
    if not isinstance(sym, bool):
        fail("sidecar inference.dev_sign_symmetry_pass must be a bool "
             "(got %r)" % (sym,))
    if (method == "signflip") != sym:
        fail("sidecar inference incoherent: method=%r with "
             "dev_sign_symmetry_pass=%r — sign-flip is licensed iff the dev "
             "sign-symmetry check PASSED; otherwise the BCa fallback branch "
             "governs (§R-REV4.1a)" % (method, sym))

    # --- registered directional inference (both branches implemented) ------
    def contrast(xa, xb, name, want_bca):
        """T = mean_c D_c with H1: T > 0. p per the dev-selected method:
        'signflip' = exact cluster sign-flip permutation p (valid under the
        registered sign-symmetry null: ASM-2122 for K-1, the EXPLICIT
        ASM-2280 assumption for K-2); 'bca' = the cluster-BCa CI-inversion
        one-sided p (the §R-REV4.1a fallback branch), applied uniformly to
        every directional contrast. want_bca additionally computes the
        registered 95% CI even on the sign-flip branch."""
        dcs, _ = cluster_diffs(xa, xb, clusters)
        if not dcs:
            return {"dcs": [], "lift": None, "p": None, "ci95": None,
                    "bca": None}
        lift = 100.0 * sum(dcs) / len(dcs)
        bca = None
        if want_bca or method == "bca":
            bca = ClusterBCa([100.0 * d for d in dcs], name)
        if method == "bca":
            p = bca.p_one_sided()
        else:
            _, p = signflip(dcs, name)
        return {"dcs": dcs, "lift": lift, "p": p,
                "ci95": ([bca.lb(0.025), bca.ub(0.025)] if bca else None),
                "bca": bca}

    def fired(c):
        return bool(c["lift"] is not None and c["p"] is not None
                    and c["lift"] >= FLOOR_PTS and c["p"] < ALPHA)

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
    power_gate = (c_ge8 >= POWER_GATE_MIN_C and n_items == N_REGISTERED)

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

    # placebo: d0 vs b0 one-sided; p < 0.05 VOIDS (no +3 floor, ASM-2273)
    c_d0 = contrast(d0, b0, "d0_vs_b0", want_bca=False)
    d0_lift, d0_p = c_d0["lift"], c_d0["p"]
    placebo_valid = (d0_p is not None and d0_p >= ALPHA)

    # completeness: every mandatory arm scores EXACTLY the b0 test universe
    # (supersets already hard-rejected above; missing coverage gates here)
    complete = True
    for arm in MANDATORY_ARMS:
        if arm == "d1-drng":
            complete = complete and (drng is not None
                                     and set(drng) == universe)
        else:
            complete = complete and set(arm_items(byarm, arm)) == universe

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
    k1 = contrast(karm, b0, "k1_K_vs_b0", want_bca=True)
    k1_fire = fired(k1)
    if drng is not None:
        k2 = contrast(karm, drng, "k2_K_vs_drngmean", want_bca=True)
    else:
        k2 = {"lift": None, "p": None, "ci95": None}
    k2_fire = fired(k2) if drng is not None else False
    if d2:
        k3 = contrast(karm, d2, "k3_K_vs_d2", want_bca=True)
        k3_fire = fired(k3)
    else:
        k3 = {"lift": None, "p": None, "ci95": None}
        k3_fire = False

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
    ceiling = b0_acc > CEILING_B0     # pinned constant, never sidecar-movable
    bca = k1["bca"]
    a2 = (1 - TOST_CI) / 2
    tost = ([bca.lb(a2), bca.ub(a2)] if bca is not None
            and bca.theta is not None else None)
    null_equiv = bool(tost is not None and tost[0] is not None
                      and -FLOOR_PTS < tost[0] and tost[1] < FLOOR_PTS
                      and not ceiling)
    harm = contrast(b0, karm, "k1_harm", want_bca=False)  # T' = b0 - K
    kill = bool(k1["lift"] is not None and k1["lift"] <= -FLOOR_PTS
                and harm["p"] is not None and harm["p"] < ALPHA)

    # --- REPLACE non-inferiority (conditional) -------------------------------
    rep = arm_items(byarm, "REPLACE")
    rep_side = side.get("replace") or {}
    if bool(rep) != bool(rep_side.get("ran")):
        fail("REPLACE coherence violated: rows %s but sidecar replace.ran="
             "%r — the run/defer decision is PRE-test (§R-REV4.3)"
             % ("present" if rep else "absent", rep_side.get("ran")))
    rep_ran = bool(rep) and bool(rep_side.get("ran"))
    if rep_ran and set(rep) != universe:
        fail("REPLACE ran but scores %d/%d registered items — partial-NI is "
             "rejected (§R1.2)" % (len(rep), len(universe)))
    if rep_ran:
        c_rni = contrast(rep, karm, "replace_ni", want_bca=True)
        rlb = c_rni["bca"].lb(ALPHA) if c_rni["bca"] is not None else None
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
                   "dev-selected exact-test p (sign-flip, or the BCa "
                   "fallback branch) and the +3-pt floor; a non-fire is "
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
        "inference_method": method,
        "k1_lift_points": k1["lift"], "k1_p": k1["p"],
        "k1_ci95": k1["ci95"],
        "k1_joint_pass": k1_fire,
        "k2_lift_points": k2["lift"], "k2_p": k2["p"],
        "k2_ci95": k2["ci95"],
        "k2_joint_pass": k2_fire,
        "k2_rank_of_k": k_rank,
        "k3_lift_points": k3["lift"], "k3_p": k3["p"],
        "k3_ci95": k3["ci95"],
        "k3_joint_pass": k3_fire,
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


def _mock_sidecar(method="signflip"):
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
        "inference": {"method": method,
                      "dev_sign_symmetry_pass": method == "signflip"},
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
    import contextlib
    import io

    def check(cond, msg):
        if not cond:
            print("MOCK-SELFTEST FAIL: %s" % msg, file=sys.stderr)
            sys.exit(1)

    def expect_reject(thunk, what):
        """Every hardened validation must exit fail-closed (never return)."""
        sink = io.StringIO()
        try:
            with contextlib.redirect_stderr(sink):
                thunk()
        except SystemExit as e:
            check(e.code == 1, "%s: rejected but exit code %r" % (what,
                                                                  e.code))
            check("ERR_P2_ANALYSIS" in sink.getvalue(),
                  "%s: rejection did not print ERR_P2_ANALYSIS" % what)
            return
        check(False, "%s: expected fail-closed rejection, got a result"
              % what)

    # Mock A — planted +10-pt K lift over b0/d0/drng; d2 close (+2 pts);
    # sign-flip branch (dev sign-symmetry check passed)
    rng = random.Random(4242)
    rows_a = _mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                             "d2": 0.78, "d3-text": 0.71, "K": 0.80}, rng)
    out_a = analyze(rows_a, _mock_sidecar())
    g = out_a["gates"]
    a = out_a["analysis"]
    check(all(g.values()), "mock A: some gate failed: %s" % g)
    check(a["inference_method"] == "signflip", "mock A: method not signflip")
    check(a["k1_joint_pass"], "mock A: K-1 did not fire (lift=%s p=%s)"
          % (a["k1_lift_points"], a["k1_p"]))
    check(a["k2_joint_pass"], "mock A: K-2 did not fire")
    check(a["pass_gate"], "mock A: pass_gate false")
    check(not a["kill_fired"], "mock A: kill fired")
    check(not a["null_equiv"], "mock A: null_equiv true under planted lift")
    check(a["ladder_rung_reached"] >= 2, "mock A: ladder < 2")
    check(a["n_items"] == 1440 and a["n_clusters"] == 72,
          "mock A: grid wrong")
    for key in ("k1_ci95", "k2_ci95", "k3_ci95"):
        ci = a[key]
        check(isinstance(ci, list) and len(ci) == 2 and ci[0] is not None
              and ci[0] <= ci[1], "mock A: %s malformed: %s" % (key, ci))
    check(a["k2_ci95"][0] > 0, "mock A: K-2 BCa 95%% CI LB not > 0 under "
          "planted lift: %s" % a["k2_ci95"])

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

    # Mock C — the SAME planted-lift campaign on the dev-selected BCa
    # FALLBACK branch (dev sign-symmetry check failed): the implemented
    # §R-REV4.1a machinery must reach the same PASS shape.
    out_c = analyze(rows_a, _mock_sidecar(method="bca"))
    cga, ca = out_c["gates"], out_c["analysis"]
    check(all(cga.values()), "mock C: some gate failed: %s" % cga)
    check(ca["inference_method"] == "bca", "mock C: method not bca")
    check(ca["k1_p"] is not None and ca["k1_p"] < ALPHA,
          "mock C: BCa-branch k1_p not significant: %s" % ca["k1_p"])
    check(ca["k1_joint_pass"] and ca["k2_joint_pass"] and ca["pass_gate"],
          "mock C: BCa fallback branch did not reach the PASS shape")
    check(not ca["kill_fired"] and not ca["null_equiv"],
          "mock C: kill/null fired under planted lift on the BCa branch")

    # Hardened-validation probes — each must be REJECTED fail-closed
    rows_short = [r for r in rows_a if r["item_id"] != "it-000-00"]
    expect_reject(lambda: analyze(rows_short, _mock_sidecar()),
                  "n != 1440 (dropped item)")
    rows_super = rows_a + [{"item_id": "it-extra-99", "cluster": "c-000",
                            "arm": "K", "pass": 0, "correct": 1,
                            "pred_label": "A", "gold_label": "A",
                            "tags": []}]
    expect_reject(lambda: analyze(rows_super, _mock_sidecar()),
                  "arm item superset")
    rows_frac = [dict(r) for r in rows_a]
    rows_frac[0]["correct"] = 0.5
    expect_reject(lambda: analyze(rows_frac, _mock_sidecar()),
                  "non-binary correct")
    side_ceil = _mock_sidecar()
    side_ceil["b0_ceiling_threshold"] = 0.99
    expect_reject(lambda: analyze(rows_a, side_ceil),
                  "mutated ceiling threshold")
    side_inc = _mock_sidecar()
    side_inc["inference"] = {"method": "bca", "dev_sign_symmetry_pass": True}
    expect_reject(lambda: analyze(rows_a, side_inc),
                  "incoherent inference method")
    side_nom = _mock_sidecar()
    del side_nom["inference"]
    expect_reject(lambda: analyze(rows_a, side_nom),
                  "missing inference block")

    # Pinned-file round-trip (exercises the stdin/pin path end-to-end)
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
    # on BOTH branches
    for branch, out in (("signflip", out_a), ("bca", out_c)):
        for ptr in OUTPUT_FIELDS:
            node = out
            for part in ptr.strip("/").split("/"):
                check(isinstance(node, dict) and part in node,
                      "output field %s missing on %s branch" % (ptr, branch))
                node = node[part]
    print("MOCK-SELFTEST PASS: planted-lift verdict shape (PASS-bound, "
          "ladder rung %d) on the sign-flip branch AND on the implemented "
          "BCa fallback branch, planted-null TOST NULL-bound, 6/6 hardened "
          "rejections fail-closed (n!=1440, superset, non-binary, mutable "
          "ceiling, incoherent/missing inference), pin round-trip "
          "byte-stable, %d output fields present on both branches."
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
