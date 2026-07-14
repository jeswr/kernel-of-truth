#!/usr/bin/env python3
"""glm-edrop-0 pre-registered analysis (stdin-conformant; verdict-gen P2 §3.1
step 5 invokes this with the ELIGIBLE results-log run records as JSONL on
STDIN and NO argv — the analysis/f1k.py / rules_2_go_stdin.py contract; the
CLI-only-pin defect that stranded knull/ufo/ddc verdict registration is not
repeatable here: load_from_stdin() is the only data path).

Experiment: GLM-DROP (B1b) — kernel-guided GLM-5.2 expert-drop at matched
experts-per-token. Design: docs/next/design/glm52-expert-drop.md (R0..R4;
latest revision governs on conflict), sha256
f1c8d0f603f7b92ab7e36527912fbda2f4740f5f3c6a9d43dfcbe71307b45a1c as read at
record-draft time. Companion record: registry/experiments/glm-edrop-0.json
(DRAFT). ASMs: ASM-2230..2239 (R0), ASM-2290..2293 (R1), ASM-2340..2352
(R2, as R3/R4-amended; centrally registered).

REGISTERED STATISTICS (design §5.2, implemented, not narrated):
  * Unit of inference = the trace concept ANALYSIS CLUSTER, C = 8 exactly
    (ASM-2340). For a paired contrast (X vs Y): per-item
    d_i = correct_X(i) - correct_Y(i); per-cluster D_c = mean_{i in c} d_i;
    statistic T = mean_c D_c, reported in accuracy points (100*T). The
    item-weighted accuracy deltas are DESCRIPTIVE only.
  * PRIMARY TEST = EXACT one-sided cluster sign-flip ENUMERATION: ALL
    2^8 = 256 sign vectors s in {+-1}^8, p = #{s : T(s) >= T_obs} / 256
    (identity included, so p >= 1/256). NO Monte-Carlo resampling — the R1
    10,000-draw test is superseded (§5.2 [R2]). "Reject iff p <= 0.05"
    operates at effective size 12/256 ~ 0.0469 (conservative, disclosed).
  * LICENSING RULE (joint, §5.2): a contrast is licensed iff enumeration
    p <= 0.05 AND observed T >= +3.0 accuracy points. The +3 floor binds on
    the CLUSTER-BALANCED statistic, never the item-weighted delta.
  * EXCHANGEABILITY BASIS + FALLBACK (imported from F1-K, ASM-2122 /
    §R-REV4.1a, carried verbatim by §5.2 [R2]): if the dev-split
    sign-symmetry check fails, the pre-registered fallback is the cluster
    (concept-block) BCa bootstrap of T (B = 10,000, one-sided p by CI
    inversion, identical +3-pt joint rule). The choice is frozen PRE-test at
    prereg-freeze on the DEV check and carried in the sidecar as
    inference = {method: "enumeration"|"bca", dev_sign_symmetry_pass: bool};
    coherence enforced fail-closed (method == "enumeration" iff the dev
    check passed). Bootstrap randomness uses the house SHA-256 DRBG over
    fixed labels (encoder-pin discipline; zero PRNG library dependencies).
  * DECISION LADDER (§5.3, both directions pre-worded):
      D0 (deficit check): T(b0-full vs u-topk) <= 3.0 points => FLOOR-BOUND:
        no guided-vs-uniform contrast is licensed; everything below is
        reported descriptively with status NOT-LICENSED-FLOOR-BOUND.
      D1 (guided vs uniform): T(m-kern vs u-topk) under the joint rule,
        matched loads verified (§4.1).
      D2 (kernel-specificity, ASM-2293): THREE separate named legs, EACH
        under the joint rule: (a) m-kern vs m-freq; (b) m-kern vs m-emb;
        (c) m-kern vs the per-item MEAN over the R = 3 m-drng realizations
        on the non-excluded subset (m-kern restricted to the same items).
        D2 passes only if ALL THREE pass — never a best-of comparator.
      D2 FAIL vs UNINFORMATIVE are DISTINCT (§5.3 [R2]): a leg voided by
        the Jaccard gate (mean > 0.95), a load-gate VOID, or the m-drng
        exclusion bound (> 10% of eligible n) is UNINFORMATIVE; a clean leg
        that misses the joint rule is FAIL-TO-DEMONSTRATE. Aggregation
        (implementation choice, disclosed for the pre-freeze skeptic): any
        CLEAN leg missing => D2 = FAIL-TO-DEMONSTRATE (a clean miss is
        decisive); else any voided leg => UNINFORMATIVE; else PASS.
      PASS GATE: not floor-bound AND D1 joint AND D2 == PASS. This licenses
        ONLY the §5.3 row-1 sentence; a non-demonstration NEVER licenses
        equivalence/sufficiency/"added nothing" wording (§5.3 [R2]).
      KILL (harm direction; record-level operationalisation — the design
        doc words no kill; flagged for the freeze-gate review): T(u-topk vs
        m-kern) >= +3.0 AND harm-direction p <= 0.05 with both arms
        load-valid — kernel guidance actively HARMS vs the free uniform
        knob at matched loads.
  * LOAD GATE (§4.1 + §3.1 item 6): ARM-LEVEL MEAN realized
    experts-loaded/token within +-5% of u-topk's mean on identical items,
    per masked arm; violation VOIDs that arm's contrasts (never
    reinterpreted). b0-full is the TOPK=8 retention reference and is exempt.
    Realized loads/token is the ONLY systems endpoint (ASM-2348);
    everything else efficiency-shaped is descriptive.
  * EQUIVALENCE DISCIPLINE (§5.3 [R2]): this script computes NO TOST and
    emits NO equivalence field; no outcome licenses "X adds nothing".

HARDENED VALIDATION (all fail-closed ERR_P2_ANALYSIS, never gates):
  * STRICTLY binary correctness (bools rejected); duplicate rows rejected;
    unknown arms rejected; realization coherence (1..3 for m-drng, 0
    otherwise) enforced.
  * NO ARM SUPERSETS: every (arm, realization) scores ONLY items in the
    b0-full universe.
  * The b0-full universe must equal the frozen eligible set: count == the
    sidecar manifest n AND sha256 over the sorted id list == the manifest
    eligible_ids_sha256 (the §5.1 sequenced-after-F1-K-freeze pin, echoed
    by the freeze manifest).
  * IMMUTABLE thresholds: floor 3.0 / alpha 0.05 / Jaccard 0.95 / load
    tolerance 0.05 are pinned constants; a sidecar carrying different
    values is rejected.
  * loads_per_token required on every row, finite and > 0.
  * Pinned repo-byte constants: the universal-core hash and the
    concept->cluster table hash (design §2.1 [R3]) must be echoed exactly.

INPUT CONTRACT: each eligible stdin record (event=="run", phase=="final",
exit=="ok") must carry artifacts.rows_path/rows_sha256 and
artifacts.sidecar_path/sidecar_sha256; all eligible records must pin the
SAME artifact tuple. Rows and sidecar are loaded from the pinned paths,
sha256 re-verified, fail closed; the analysis is a pure function of those
bytes. ROWS (JSONL), one row per scored (item x arm x realization):
  {item_id, cluster (int 0..7 per the frozen §2.1 table order),
   arm in {b0-full, u-topk, m-freq, m-emb, m-kern, m-drng},
   realization (int; 1..3 for m-drng, else 0), correct 0/1 (STRICTLY
   binary), loads_per_token (number > 0; the engine counter)}
SIDECAR (JSON):
  manifest {core_sha256, concept_table_sha256, eligible_ids_sha256, n,
    m_c (list of 8 ints, cluster order 0..7), exclusion_count (from the
    1440 test pool), mask_table_sha256 {m-freq, m-emb, m-kern, m-drng-1,
    m-drng-2, m-drng-3 -> 64-hex}, prereg_frozen_before_f1k_test_outcomes
    (bool; or firewalled true per §6.1 step 5), drop_table_patch_approved,
    r4_replay_landed, power_rerun_committed, encoder_weights_sha256_pinned
    (bools)}
  seeds {drng: [20260721, 20260722, 20260723], kmeans: 20260724,
    pilot_bootstrap: 20260725, blocks: 20260726, spotset: 20260727,
    powersim: 20260728}  (must equal the §3.1 item 8 registry EXACTLY)
  k_star (int in {4, 3, 2, 1}; the §4.2 pilot-selected operating point)
  pilot {dev_deficit_points_at_k_star, eligible_dev_n,
    continuous_sign_agrees (bool; §4.2 fail-closed surfacing)}
  cold_warm {byte_identical: bool}   (§4.3 correctness-regime check)
  isolation {seal_recorded, f1k_terminated, fresh_pid, env_echo_verified,
    namespaces_distinct, firewall_ok: bools}   (§6.1 steps 1-6)
  dose {all_masked_exactly_64_per_layer, same_core_all_masked,
    cardinality_matched: bools}   (§3 dose invariant, manifest-verified)
  jaccard {"m-kern|m-freq", "m-kern|m-emb", "m-kern|m-drng": floats}
    (§3.1 item 5 mean-J statistics; m-drng pooled over 3 realizations)
  drng {excluded_item_ids: [ids], impossible_strata_count: int} (§3.1 item 4)
  footprint {union_gb_per_arm: {...}}  (descriptive, §5.1 [R2])
  masks {table_bytes_per_arm: {...}}   (descriptive)
  inference {method: "enumeration"|"bca", dev_sign_symmetry_pass: bool}
  power {simulated_mde_true_points_planning, joint_power_at_true_3_planning,
    rerun_at_realized: {...}}   (§5.2 pinned simulation + freeze re-run)
  cost {usd_total, instance_hours, prefills}
  floor_points / alpha / jaccard_max / load_tolerance (optional echoes;
    MUST equal 3.0 / 0.05 / 0.95 / 0.05 if present)

MOCK SELF-TEST: `python3 analysis/glm_edrop_0_stdin.py --selftest` (optional
argv; the stdin path takes no flags) drives EVERY verdict branch on
synthetic rows: PASS shape (planted D1+D2 advantage, both inference
branches), FAIL shape (planted harm => kill), floor-bound D0 shape,
not-demonstrated D1 shape, D2 FAIL-TO-DEMONSTRATE shape, D2 UNINFORMATIVE
(Jaccard) shape, load-VOID shape, INSTRUMENT-INVALID gate shape, plus the
hardened fail-closed rejections and a pinned-file stdin round-trip, and
asserts the full output surface on both branches. Exits 0 on green.

Fail-closed exits: any pin/shape violation prints ERR_P2_ANALYSIS to stderr
and exits 1 (=> verdict-gen ERR_P2_ANALYSIS); nothing falls back.

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Pre-registered constants (changing any is a design change requiring a
# --- new freeze; sources cited per line; design = glm52-expert-drop.md) ---
FLOOR_PTS = 3.0            # joint-rule effect floor, accuracy points (§5.2)
ALPHA = 0.05               # one-sided; effective 12/256 ~ 0.0469 (§5.2 [R2])
C_REGISTERED = 8           # analysis clusters, exactly (ASM-2340; §5.2)
N_MIN = 300                # coverage gate floor (§5.1 [R2], MD-6)
TEST_POOL = 1440           # F1-K test pool cap (§5.1)
EXCL_MAX_FRAC = 0.20       # eligibility exclusions <= 20% of pool (§5.1)
M_C_MIN = 10               # per-cluster floor (§5.1)
DRNG_EXCL_MAX_FRAC = 0.10  # m-drng impossible-strata bound (§3.1 item 4)
JACCARD_MAX = 0.95         # non-distinctness gate (§3.1 item 5)
LOAD_TOL = 0.05            # +-5% arm-mean load gate (§4.1, §3.1 item 6)
R_DRNG = 3                 # preregistered derangement realizations (§3.1)
B_BOOT = 10000             # BCa resamples (fallback branch; F1-K discipline)
K_STAR_LEVELS = (4, 3, 2, 1)   # §4.2 (TOPP branch REMOVED, §3.1 item 7)
UNIFORM_ARMS = ("b0-full", "u-topk")
MASKED_ARMS = ("m-freq", "m-emb", "m-kern", "m-drng")
ARMS = UNIFORM_ARMS + MASKED_ARMS
MASK_TABLE_IDS = ("m-freq", "m-emb", "m-kern",
                  "m-drng-1", "m-drng-2", "m-drng-3")  # §6.3 [R4] closed set
INFERENCE_METHODS = ("enumeration", "bca")
# Repo-byte pins MATERIALIZED at design R3 (§2.1; MEASURED there, echoed
# here as immutable constants — the freeze manifest re-verifies the same):
CORE_SHA = "632bcd182ae8a716b3f8843d640d43772f9ddfac6880d12ac531cf974cd3f18f"
CONCEPT_TABLE_SHA = ("10cb109d651727d89bbb575ae39690e1cb"
                     "4a0081dd373a9eec139986e7ac5e38")
# §3.1 item 8 seed registry (exact echo required; disjoint from F1-K's):
SEED_REGISTRY = {
    "drng": [20260721, 20260722, 20260723],
    "kmeans": 20260724,
    "pilot_bootstrap": 20260725,
    "blocks": 20260726,
    "spotset": 20260727,
    "powersim": 20260728,
}

OUTPUT_FIELDS = [
    "/gates/freeze_manifest_valid",
    "/gates/coverage_valid",
    "/gates/seeds_valid",
    "/gates/dose_exactness_valid",
    "/gates/cold_warm_byte_identical",
    "/gates/isolation_protocol_valid",
    "/gates/completeness_valid",
    "/analysis/n_items",
    "/analysis/n_clusters",
    "/analysis/m_per_cluster",
    "/analysis/k_star",
    "/analysis/inference_method",
    "/analysis/floor_bound",
    "/analysis/d0_deficit_points",
    "/analysis/d1_lift_points",
    "/analysis/d1_p",
    "/analysis/d1_ci95",
    "/analysis/d1_joint_pass",
    "/analysis/d1_status",
    "/analysis/d2a_lift_points",
    "/analysis/d2a_p",
    "/analysis/d2a_joint_pass",
    "/analysis/d2a_status",
    "/analysis/d2b_lift_points",
    "/analysis/d2b_p",
    "/analysis/d2b_joint_pass",
    "/analysis/d2b_status",
    "/analysis/d2c_lift_points",
    "/analysis/d2c_p",
    "/analysis/d2c_joint_pass",
    "/analysis/d2c_status",
    "/analysis/d2_status",
    "/analysis/pass_gate",
    "/analysis/kill_fired",
    "/analysis/jaccard_gate",
    "/analysis/load_match",
    "/analysis/drng_exclusions",
    "/analysis/arm_accuracies",
    "/analysis/item_weighted_deltas",
    "/analysis/loads_per_token",
    "/analysis/mask_union_footprint",
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


def is_hex64(s):
    return (isinstance(s, str) and len(s) == 64
            and all(c in "0123456789abcdef" for c in s))


# ---------------------------------------------------------------------------
# House DRBG (design §3.1 item 8 primitive, reused for the BCa fallback's
# resampling: SHA-256 over fixed ASCII labels + a decimal counter, zero PRNG
# library dependencies — the encoder pin's own discipline. Analysis streams
# are namespaced "glm-edrop-0:bca:<contrast>" so they can never collide with
# any run-time stream of the design's registry.)
# ---------------------------------------------------------------------------
class DRBG:
    def __init__(self, label):
        self.label = label
        self.t = 0

    def _u64(self):
        h = hashlib.sha256(
            ("glm-edrop-0:%s:%d" % (self.label, self.t)).encode("ascii")
        ).digest()
        self.t += 1
        return int.from_bytes(h[:8], "big")

    def randrange(self, k):
        lim = (1 << 64) - ((1 << 64) % k)
        while True:
            v = self._u64()
            if v < lim:
                return v % k


# ---------------------------------------------------------------------------
# Data marshalling (fail-closed)
# ---------------------------------------------------------------------------
def index_rows(rows):
    """rows -> {arm: {realization: {item_id: correct}}} + item->cluster map
    + per-arm loads lists. STRICTLY binary correctness; duplicate rows,
    unknown arms, incoherent realizations, bad clusters, and missing/
    non-positive loads_per_token are all rejected fail-closed."""
    byarm, clusters, loads = {}, {}, {}
    for r in rows:
        for k in ("item_id", "cluster", "arm", "realization", "correct",
                  "loads_per_token"):
            if k not in r:
                fail("row missing %r: %s" % (k, json.dumps(r)[:200]))
        arm = r["arm"]
        if arm not in ARMS:
            fail("unknown arm %r (closed set %s)" % (arm, list(ARMS)))
        c = r["correct"]
        if isinstance(c, bool) or not (c == 0 or c == 1):
            fail("non-binary correct %r (must be 0 or 1): %s"
                 % (c, json.dumps(r)[:200]))
        cl = r["cluster"]
        if isinstance(cl, bool) or not isinstance(cl, int) \
                or not (0 <= cl < C_REGISTERED):
            fail("cluster %r not an int in [0, %d)" % (cl, C_REGISTERED))
        rz = r["realization"]
        if isinstance(rz, bool) or not isinstance(rz, int):
            fail("realization %r not an int" % (rz,))
        if arm == "m-drng":
            if not (1 <= rz <= R_DRNG):
                fail("m-drng realization %r outside 1..%d" % (rz, R_DRNG))
        elif rz != 0:
            fail("arm %s carries realization %r (must be 0)" % (arm, rz))
        lpt = r["loads_per_token"]
        if isinstance(lpt, bool) or not isinstance(lpt, (int, float)) \
                or not math.isfinite(lpt) or lpt <= 0:
            fail("loads_per_token %r not a finite positive number" % (lpt,))
        iid = r["item_id"]
        d = byarm.setdefault(arm, {}).setdefault(rz, {})
        if iid in d:
            fail("duplicate row (arm=%s realization=%d item=%s)"
                 % (arm, rz, iid))
        d[iid] = int(c)
        prev = clusters.setdefault(iid, cl)
        if prev != cl:
            fail("item %s carries two clusters (%s, %s)" % (iid, prev, cl))
        loads.setdefault(arm, []).append(float(lpt))
    return byarm, clusters, loads


def arm_items(byarm, arm, rz=0):
    return byarm.get(arm, {}).get(rz, {})


def drng_mean(byarm, restricted):
    """Per-item MEAN correctness over the R = 3 m-drng realizations on the
    non-excluded (restricted) item set (§5.3 D2 leg c). Fail-closed if any
    realization is missing or off-set (completeness gate also sees this)."""
    passes = byarm.get("m-drng", {})
    if sorted(passes) != list(range(1, R_DRNG + 1)):
        return None
    for rz in range(1, R_DRNG + 1):
        if set(passes[rz]) != restricted:
            return None
    return {i: sum(passes[rz][i] for rz in range(1, R_DRNG + 1)) / R_DRNG
            for i in sorted(restricted)}


# ---------------------------------------------------------------------------
# Registered statistics (§5.2)
# ---------------------------------------------------------------------------
def cluster_diffs(xa, xb, clusters):
    """Paired per-item diffs -> list of cluster means D_c (fractions) in
    ascending cluster index, plus the set of clusters present."""
    shared = sorted(set(xa) & set(xb))
    acc = {}
    for i in shared:
        acc.setdefault(clusters[i], []).append(xa[i] - xb[i])
    present = sorted(acc)
    return [sum(acc[c]) / len(acc[c]) for c in present], set(present)


def enum_signflip(dcs):
    """EXACT one-sided cluster sign-flip enumeration (§5.2 [R2]): all 2^C
    sign vectors, p = #{s : T(s) >= T_obs} / 2^C, identity included.
    Returns (T_points, p, ge_count). Deterministic; no randomness."""
    C = len(dcs)
    t_obs = sum(dcs) / C
    total = 1 << C
    ge = 0
    for bits in range(total):
        s = 0.0
        for i in range(C):
            s += -dcs[i] if (bits >> i) & 1 else dcs[i]
        if s / C >= t_obs:
            ge += 1
    return 100.0 * t_obs, ge / total, ge


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
    """BCa bootstrap of T = mean_c D_c resampling CLUSTERS with replacement
    (the imported F1-K §R-REV4.1a fallback machinery; carries the 95% CI on
    the primary contrast and — when the dev-selected method is 'bca' — the
    fallback-branch one-sided p via CI inversion). Randomness = the house
    SHA-256 DRBG, deterministic by contrast label."""

    def __init__(self, dcs, name, b=B_BOOT):
        self.n = len(dcs)
        if self.n == 0:
            self.theta = None
            return
        self.theta = sum(dcs) / self.n
        rng = DRBG("bca:%s" % name)
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
        """CI-inversion one-sided p for H1: T > 0 (p < a <=> lb(a) > 0)."""
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
        for _ in range(60):
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
    byarm, clusters, loads = index_rows(rows)
    b0 = arm_items(byarm, "b0-full")
    utopk = arm_items(byarm, "u-topk")
    if not b0 or not utopk:
        fail("mandatory arms b0-full/u-topk missing from rows")
    universe = set(b0)

    # --- immutable-threshold echoes (mutable-threshold rejection) ----------
    for key, pinned in (("floor_points", FLOOR_PTS), ("alpha", ALPHA),
                        ("jaccard_max", JACCARD_MAX),
                        ("load_tolerance", LOAD_TOL)):
        if key in side and side[key] != pinned:
            fail("sidecar %s %r != pinned %s — decision thresholds are "
                 "immutable at freeze" % (key, side[key], pinned))

    # --- manifest identity (fail-closed hard checks + gate) ----------------
    man = side.get("manifest") or {}
    n_man = man.get("n")
    if not isinstance(n_man, int) or n_man <= 0:
        fail("manifest.n %r not a positive int" % (n_man,))
    if len(universe) != n_man:
        fail("b0-full scores %d items but the freeze manifest pins n = %d "
             "(the §5.1 sequenced pin) — any other realized n is rejected, "
             "never analyzed" % (len(universe), n_man))
    ids_sha = sha256_bytes(
        ("\n".join(sorted(universe)) + "\n").encode("utf-8"))
    if man.get("eligible_ids_sha256") != ids_sha:
        fail("eligible-set identity: sha256 over the sorted scored id list "
             "%s != manifest eligible_ids_sha256 %r"
             % (ids_sha, man.get("eligible_ids_sha256")))
    for arm in sorted(byarm):
        for rz in sorted(byarm[arm]):
            extra = sorted(set(byarm[arm][rz]) - universe)
            if extra:
                fail("arm %s realization %d scores %d item(s) OUTSIDE the "
                     "frozen eligible set (supersets rejected): %s"
                     % (arm, rz, len(extra), extra[:5]))

    k_star = side.get("k_star")
    if k_star not in K_STAR_LEVELS:
        fail("k_star %r not in the frozen escalation set %s (§4.2; TOPP "
             "removed §3.1 item 7)" % (k_star, list(K_STAR_LEVELS)))

    inf = side.get("inference") or {}
    method = inf.get("method")
    if method not in INFERENCE_METHODS:
        fail("sidecar inference.method %r not in %s (the §5.2 dev-selected "
             "enumeration-vs-BCa choice, frozen at prereg-freeze, is "
             "mandatory)" % (method, list(INFERENCE_METHODS)))
    sym = inf.get("dev_sign_symmetry_pass")
    if not isinstance(sym, bool):
        fail("sidecar inference.dev_sign_symmetry_pass must be a bool "
             "(got %r)" % (sym,))
    if (method == "enumeration") != sym:
        fail("sidecar inference incoherent: method=%r with "
             "dev_sign_symmetry_pass=%r — enumeration is licensed iff the "
             "dev sign-symmetry check PASSED; otherwise the BCa fallback "
             "governs (§5.2 [R2])" % (method, sym))

    # --- gates --------------------------------------------------------------
    mask_shas = man.get("mask_table_sha256") or {}
    manifest_valid = (
        man.get("core_sha256") == CORE_SHA
        and man.get("concept_table_sha256") == CONCEPT_TABLE_SHA
        and sorted(mask_shas) == sorted(MASK_TABLE_IDS)
        and all(is_hex64(mask_shas[a]) for a in mask_shas)
        and all(bool(man.get(k)) for k in (
            "prereg_frozen_before_f1k_test_outcomes",
            "drop_table_patch_approved",
            "r4_replay_landed",
            "power_rerun_committed",
            "encoder_weights_sha256_pinned")))

    csizes = {}
    for i in universe:
        csizes[clusters[i]] = csizes.get(clusters[i], 0) + 1
    n_items = len(universe)
    realized_mc = [csizes.get(c, 0) for c in range(C_REGISTERED)]
    excl = man.get("exclusion_count")
    coverage_valid = (
        n_items >= N_MIN
        and isinstance(excl, int) and 0 <= excl <= EXCL_MAX_FRAC * TEST_POOL
        and sorted(csizes) == list(range(C_REGISTERED))
        and all(m >= M_C_MIN for m in realized_mc)
        and list(man.get("m_c") or []) == realized_mc)

    seeds_valid = (side.get("seeds") == SEED_REGISTRY)

    dose = side.get("dose") or {}
    dose_valid = all(bool(dose.get(k)) for k in (
        "all_masked_exactly_64_per_layer", "same_core_all_masked",
        "cardinality_matched"))

    cw = side.get("cold_warm") or {}
    cold_warm_valid = bool(cw.get("byte_identical"))

    iso = side.get("isolation") or {}
    isolation_valid = all(bool(iso.get(k)) for k in (
        "seal_recorded", "f1k_terminated", "fresh_pid",
        "env_echo_verified", "namespaces_distinct", "firewall_ok"))

    drng_side = side.get("drng") or {}
    excluded = set(drng_side.get("excluded_item_ids") or [])
    if not excluded <= universe:
        fail("drng.excluded_item_ids contains ids outside the eligible set")
    restricted = universe - excluded
    drng = drng_mean(byarm, restricted)

    complete = True
    for arm in ("b0-full", "u-topk", "m-freq", "m-emb", "m-kern"):
        complete = complete and set(arm_items(byarm, arm)) == universe \
            and sorted(byarm.get(arm, {})) == [0]
    complete = complete and drng is not None

    gates = {
        "freeze_manifest_valid": bool(manifest_valid),
        "coverage_valid": bool(coverage_valid),
        "seeds_valid": bool(seeds_valid),
        "dose_exactness_valid": bool(dose_valid),
        "cold_warm_byte_identical": bool(cold_warm_valid),
        "isolation_protocol_valid": bool(isolation_valid),
        "completeness_valid": bool(complete),
    }

    # --- load gate (§4.1; VOIDs contrasts, never reinterpreted) ------------
    def mean_loads(arm):
        v = loads.get(arm) or []
        return (sum(v) / len(v)) if v else None

    ref = mean_loads("u-topk")
    load_ratio, arm_void = {}, {}
    for arm in MASKED_ARMS:
        m = mean_loads(arm)
        ratio = (m / ref) if (m is not None and ref) else None
        load_ratio[arm] = ratio
        arm_void[arm] = not (ratio is not None
                             and abs(ratio - 1.0) <= LOAD_TOL)
    load_match = {
        "u_topk_mean": ref,
        "b0_full_mean": mean_loads("b0-full"),
        "masked_arm_ratio_vs_u_topk": load_ratio,
        "tolerance": LOAD_TOL,
        "voided_arms": sorted(a for a in MASKED_ARMS if arm_void[a]),
        "note": "arm-level MEAN realized experts-loaded/token vs u-topk on "
                "identical items (§4.1, §3.1 item 6); violation VOIDs the "
                "arm's contrasts — never reinterpreted; b0-full (TOPK=8 "
                "reference) is exempt",
    }

    # --- registered directional inference (both branches implemented) ------
    def contrast(xa, xb, name):
        dcs, present = cluster_diffs(xa, xb, clusters)
        if len(present) != C_REGISTERED:
            return {"lift": None, "p": None, "ci95": None, "bca": None,
                    "cluster_loss": True}
        lift_pts = 100.0 * sum(dcs) / len(dcs)
        bca = ClusterBCa([100.0 * d for d in dcs], name)
        if method == "bca":
            p = bca.p_one_sided()
        else:
            _, p, _ = enum_signflip(dcs)
        return {"lift": lift_pts, "p": p,
                "ci95": [bca.lb(0.025), bca.ub(0.025)], "bca": bca,
                "cluster_loss": False}

    def joint(c):
        return bool(c["lift"] is not None and c["p"] is not None
                    and c["lift"] >= FLOOR_PTS and c["p"] <= ALPHA)

    # --- D0: deficit check (plain threshold on observed T, §5.3) ------------
    c_d0 = contrast(b0, utopk, "d0_deficit")
    if c_d0["cluster_loss"]:
        fail("D0 contrast lost an analysis cluster — the C = 8 basis is "
             "broken (coverage gate should have caught this)")
    d0_deficit = c_d0["lift"]
    floor_bound = bool(d0_deficit is not None and d0_deficit <= FLOOR_PTS)

    kern = arm_items(byarm, "m-kern")
    freq = arm_items(byarm, "m-freq")
    emb = arm_items(byarm, "m-emb")

    # --- D1: guided vs uniform ----------------------------------------------
    if arm_void["m-kern"]:
        d1 = {"lift": None, "p": None, "ci95": None}
        d1_pass, d1_status = False, "VOID-LOAD"
    else:
        d1 = contrast(kern, utopk, "d1_kern_vs_utopk")
        d1_pass = joint(d1) and not floor_bound
        d1_status = ("NOT-LICENSED-FLOOR-BOUND" if floor_bound else "TESTED")

    # --- KILL (harm direction; both arms load-valid) -------------------------
    if arm_void["m-kern"]:
        kill = False
    else:
        harm = contrast(utopk, kern, "kill_harm")
        kill = joint(harm)

    # --- D2: three named legs (ASM-2293), FAIL vs UNINFORMATIVE distinct ----
    jac = side.get("jaccard") or {}

    def leg(xa, xb, name, deflator_arm, jac_key):
        j = jac.get(jac_key)
        if arm_void["m-kern"] or arm_void[deflator_arm]:
            return {"lift": None, "p": None, "pass": False,
                    "status": "UNINFORMATIVE-LOAD-VOID"}
        if not isinstance(j, (int, float)) or not math.isfinite(j):
            fail("sidecar jaccard[%r] %r not a finite number (§3.1 item 5 "
                 "gate statistic is mandatory)" % (jac_key, j))
        if j > JACCARD_MAX:
            return {"lift": None, "p": None, "pass": False,
                    "status": "UNINFORMATIVE-JACCARD"}
        c = contrast(xa, xb, name)
        if c["cluster_loss"]:
            return {"lift": None, "p": None, "pass": False,
                    "status": "UNINFORMATIVE-CLUSTER-LOSS"}
        ok = joint(c)
        return {"lift": c["lift"], "p": c["p"], "pass": ok,
                "status": "PASS" if ok else "FAIL-TO-DEMONSTRATE"}

    d2a = leg(kern, freq, "d2a_kern_vs_freq", "m-freq", "m-kern|m-freq")
    d2b = leg(kern, emb, "d2b_kern_vs_emb", "m-emb", "m-kern|m-emb")

    drng_excl_ok = (len(excluded) <= DRNG_EXCL_MAX_FRAC * n_items)
    if not drng_excl_ok:
        d2c = {"lift": None, "p": None, "pass": False,
               "status": "UNINFORMATIVE-EXCLUSION"}
    else:
        kern_restricted = {i: kern[i] for i in restricted if i in kern}
        d2c = leg(kern_restricted, drng or {}, "d2c_kern_vs_drngmean",
                  "m-drng", "m-kern|m-drng")

    legs = (d2a, d2b, d2c)
    if floor_bound:
        d2_status = "NOT-LICENSED-FLOOR-BOUND"
    elif any(l["status"] == "FAIL-TO-DEMONSTRATE" for l in legs):
        # a CLEAN miss is decisive regardless of another leg's void
        d2_status = "FAIL-TO-DEMONSTRATE"
    elif any(l["status"].startswith("UNINFORMATIVE") for l in legs):
        d2_status = "UNINFORMATIVE"
    else:
        d2_status = "PASS"

    pass_gate = bool((not floor_bound) and d1_pass and d2_status == "PASS")

    # --- descriptives ---------------------------------------------------------
    def acc_of(d):
        return (sum(d.values()) / len(d)) if d else None

    arm_acc = {a: acc_of(arm_items(byarm, a))
               for a in ("b0-full", "u-topk", "m-freq", "m-emb", "m-kern")}
    arm_acc["m-drng-per-realization"] = {
        ("realization%d" % rz): acc_of(byarm.get("m-drng", {}).get(rz) or {})
        for rz in range(1, R_DRNG + 1)}
    b0_acc = arm_acc["b0-full"]
    deltas = {a: (100.0 * (arm_acc[a] - b0_acc)
                  if arm_acc[a] is not None and b0_acc is not None else None)
              for a in ("u-topk", "m-freq", "m-emb", "m-kern")}

    power = side.get("power") or {}
    power_scope = {
        "simulated_mde_true_points_planning":
            power.get("simulated_mde_true_points_planning"),
        "joint_power_at_true_3_planning":
            power.get("joint_power_at_true_3_planning"),
        "rerun_at_realized": power.get("rerun_at_realized"),
        "wording": "pinned planning simulation (§5.2 [R3]): MDE_true ~ 16 "
                   "pts at the n = 300 planning point under the exact "
                   "256-flip joint rule, refreshed at freeze at realized "
                   "(n, m_c); any non-demonstration is scoped 'powered to "
                   "resolve >= MDE_true pts at C = 8 cluster coverage', "
                   "never 'no effect', and NEVER an equivalence claim "
                   "(§5.3 [R2])",
    }

    masks = side.get("masks") or {}
    foot = side.get("footprint") or {}
    cost = side.get("cost") or {}
    out = {"gates": gates, "analysis": {
        "n_items": n_items,
        "n_clusters": len(csizes),
        "m_per_cluster": realized_mc,
        "k_star": k_star,
        "inference_method": method,
        "floor_bound": floor_bound,
        "d0_deficit_points": d0_deficit,
        "d1_lift_points": d1["lift"], "d1_p": d1["p"],
        "d1_ci95": d1.get("ci95"),
        "d1_joint_pass": bool(d1_pass),
        "d1_status": d1_status,
        "d2a_lift_points": d2a["lift"], "d2a_p": d2a["p"],
        "d2a_joint_pass": bool(d2a["pass"]), "d2a_status": d2a["status"],
        "d2b_lift_points": d2b["lift"], "d2b_p": d2b["p"],
        "d2b_joint_pass": bool(d2b["pass"]), "d2b_status": d2b["status"],
        "d2c_lift_points": d2c["lift"], "d2c_p": d2c["p"],
        "d2c_joint_pass": bool(d2c["pass"]), "d2c_status": d2c["status"],
        "d2_status": d2_status,
        "pass_gate": pass_gate,
        "kill_fired": bool(kill),
        "jaccard_gate": {"pair_means": {k: jac.get(k) for k in (
            "m-kern|m-freq", "m-kern|m-emb", "m-kern|m-drng")},
            "threshold": JACCARD_MAX,
            "note": "mean J(i, layer) per §3.1 item 5; > threshold renders "
                    "the leg UNINFORMATIVE, never a tie"},
        "load_match": load_match,
        "drng_exclusions": {
            "excluded_count": len(excluded),
            "impossible_strata_count":
                drng_side.get("impossible_strata_count"),
            "bound_frac": DRNG_EXCL_MAX_FRAC,
            "within_bound": bool(drng_excl_ok)},
        "arm_accuracies": arm_acc,
        "item_weighted_deltas": {
            "vs_b0_full_points": deltas,
            "note": "DESCRIPTIVE only (§5.2 [R2]): licensing rides the "
                    "cluster-balanced T, never the item-weighted delta; "
                    "disclosed whenever the two disagree in magnitude"},
        "loads_per_token": {
            "per_arm_mean": {a: (sum(v) / len(v) if v else None)
                             for a, v in sorted(loads.items())},
            "note": "realized experts-loaded/token — the ONLY systems "
                    "endpoint (ASM-2348); arm-level tok/s comparisons are "
                    "DECLINED by design (§4.3 [R2])"},
        "mask_union_footprint": {
            "union_gb_per_arm": foot.get("union_gb_per_arm"),
            "note": "measured per-mask union footprint (§5.1 [R2: "
                    "ASM-2351]); NO shard-size or page-cache-pool claim "
                    "attaches to this experiment"},
        "power_scope": power_scope,
        "accuracy": arm_acc["m-kern"],
        "params": {
            "host_params_unchanged": True,
            "params_added": 0,
            "note": "routing-mask selection among native experts only; "
                    "nothing writes activations or weights (§6.3)"},
        "memory": {
            "mask_table_bytes_per_arm": masks.get("table_bytes_per_arm"),
            "note": "immutable item-ID->mask table sidecars (§6.3 [R4]); "
                    "union routed-expert footprint reported above"},
        "inference_compute": {
            "prefills_total": cost.get("prefills"),
            "experts_loaded_per_token_by_arm": {
                a: (sum(v) / len(v) if v else None)
                for a, v in sorted(loads.items())},
            "note": "one prefill per item per arm (§5.1); the compute "
                    "lever IS the endpoint: fewer experts loaded/token at "
                    "matched k*"},
        "training_compute": {
            "flops": 0,
            "note": "identically ZERO by construction — offline CPU mask "
                    "construction from committed fingerprints only (§2.1)"},
        "cost_ledger": {"usd_total": cost.get("usd_total"),
                        "instance_hours": cost.get("instance_hours"),
                        "prefills": cost.get("prefills"),
                        "note": "resolved ONLY against "
                                "glm-drop/cost-ledger.json (ASM-2350), "
                                "never against quality metrics"},
    }}
    return out


# ---------------------------------------------------------------------------
# Input acquisition (verdict-gen stdin contract — NO argv on this path)
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
    rows_raw = read_pinned(rows_path, rows_sha, "glm-edrop-0 rows")
    side_raw = read_pinned(side_path, side_sha, "glm-edrop-0 sidecar")
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
# MOCK self-test — drives every verdict branch on synthetic rows
# ---------------------------------------------------------------------------
def _mock_rows(p_by_arm, tag, C=8, m=40):
    """Deterministic synthetic campaign via the house DRBG (no library
    PRNG): n = C*m items across the 8 analysis clusters; independent
    per-(item, arm[, realization]) correctness at the planted rates;
    loads_per_token planted at the matched level (u-topk and every masked
    arm ~606; b0-full ~1825)."""
    rng = DRBG("selftest:%s" % tag)

    def bern(p):
        return 1 if rng.randrange(10 ** 6) < int(p * 10 ** 6) else 0

    rows = []
    for c in range(C):
        for j in range(m):
            iid = "it-%03d-%02d" % (c, j)
            for arm, p in p_by_arm.items():
                lpt = 1825.1 if arm == "b0-full" else 606.3
                if arm == "m-drng":
                    for rz in range(1, R_DRNG + 1):
                        rows.append({"item_id": iid, "cluster": c,
                                     "arm": arm, "realization": rz,
                                     "correct": bern(p),
                                     "loads_per_token": lpt})
                else:
                    rows.append({"item_id": iid, "cluster": c, "arm": arm,
                                 "realization": 0, "correct": bern(p),
                                 "loads_per_token": lpt})
    return rows


def _mock_sidecar(rows, method="enumeration"):
    ids = sorted({r["item_id"] for r in rows if r["arm"] == "b0-full"})
    mc = {}
    for r in rows:
        if r["arm"] == "b0-full":
            mc[r["cluster"]] = mc.get(r["cluster"], 0) + 1
    return {
        "manifest": {
            "core_sha256": CORE_SHA,
            "concept_table_sha256": CONCEPT_TABLE_SHA,
            "eligible_ids_sha256": sha256_bytes(
                ("\n".join(ids) + "\n").encode("utf-8")),
            "n": len(ids),
            "m_c": [mc.get(c, 0) for c in range(C_REGISTERED)],
            "exclusion_count": 200,
            "mask_table_sha256": {a: "ab" * 32 for a in MASK_TABLE_IDS},
            "prereg_frozen_before_f1k_test_outcomes": True,
            "drop_table_patch_approved": True,
            "r4_replay_landed": True,
            "power_rerun_committed": True,
            "encoder_weights_sha256_pinned": True,
        },
        "seeds": {k: (list(v) if isinstance(v, list) else v)
                  for k, v in SEED_REGISTRY.items()},
        "k_star": 2,
        "pilot": {"dev_deficit_points_at_k_star": 8.3,
                  "eligible_dev_n": 61, "continuous_sign_agrees": True},
        "cold_warm": {"byte_identical": True},
        "isolation": {"seal_recorded": True, "f1k_terminated": True,
                      "fresh_pid": True, "env_echo_verified": True,
                      "namespaces_distinct": True, "firewall_ok": True},
        "dose": {"all_masked_exactly_64_per_layer": True,
                 "same_core_all_masked": True, "cardinality_matched": True},
        "jaccard": {"m-kern|m-freq": 0.71, "m-kern|m-emb": 0.74,
                    "m-kern|m-drng": 0.69},
        "drng": {"excluded_item_ids": [], "impossible_strata_count": 0},
        "footprint": {"union_gb_per_arm": {"m-kern": 118.0}},
        "masks": {"table_bytes_per_arm": {a: 2500000
                                          for a in MASK_TABLE_IDS}},
        "inference": {"method": method,
                      "dev_sign_symmetry_pass": method == "enumeration"},
        "power": {"simulated_mde_true_points_planning": 16.0,
                  "joint_power_at_true_3_planning": 0.119,
                  "rerun_at_realized": None},
        "cost": {"usd_total": 0.0, "instance_hours": 0.0, "prefills": 2930},
        "floor_points": FLOOR_PTS,
    }


def selftest():
    import contextlib
    import io

    def check(cond, msg):
        if not cond:
            print("MOCK-SELFTEST FAIL: %s" % msg, file=sys.stderr)
            sys.exit(1)

    def expect_reject(thunk, what):
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

    # A — PASS shape: real deficit regime (b0 .85 vs u-topk .60), m-kern
    # recovers (.84), deflators do not (.62-.66), enumeration branch.
    P_A = {"b0-full": 0.85, "u-topk": 0.60, "m-freq": 0.64, "m-emb": 0.66,
           "m-kern": 0.84, "m-drng": 0.62}
    rows_a = _mock_rows(P_A, "A")
    out_a = analyze(rows_a, _mock_sidecar(rows_a))
    g, a = out_a["gates"], out_a["analysis"]
    check(all(g.values()), "A: some gate failed: %s" % g)
    check(a["inference_method"] == "enumeration", "A: method wrong")
    check(not a["floor_bound"], "A: floor-bound under planted deficit "
          "(d0=%s)" % a["d0_deficit_points"])
    check(a["d1_joint_pass"], "A: D1 did not fire (lift=%s p=%s)"
          % (a["d1_lift_points"], a["d1_p"]))
    check(a["d2_status"] == "PASS" and a["d2a_joint_pass"]
          and a["d2b_joint_pass"] and a["d2c_joint_pass"],
          "A: D2 not PASS: %s" % a["d2_status"])
    check(a["pass_gate"] and not a["kill_fired"], "A: verdict shape wrong")
    check(a["n_items"] == 320 and a["n_clusters"] == 8, "A: grid wrong")
    ci = a["d1_ci95"]
    check(isinstance(ci, list) and len(ci) == 2 and ci[0] is not None
          and ci[0] <= ci[1], "A: d1_ci95 malformed: %s" % ci)

    # F — the SAME campaign on the BCa fallback branch: same PASS shape.
    out_f = analyze(rows_a, _mock_sidecar(rows_a, method="bca"))
    fa = out_f["analysis"]
    check(fa["inference_method"] == "bca", "F: method wrong")
    check(fa["d1_p"] is not None and fa["d1_p"] <= ALPHA,
          "F: BCa-branch d1_p not significant: %s" % fa["d1_p"])
    check(fa["pass_gate"] and fa["d2_status"] == "PASS",
          "F: BCa fallback did not reach the PASS shape")

    # B — not-demonstrated D1: deficit regime but m-kern == u-topk.
    P_B = dict(P_A, **{"m-kern": 0.60, "m-freq": 0.60, "m-emb": 0.60})
    rows_b = _mock_rows(P_B, "B")
    out_b = analyze(rows_b, _mock_sidecar(rows_b))
    ba = out_b["analysis"]
    check(not ba["floor_bound"], "B: floor-bound unexpectedly")
    check(not ba["d1_joint_pass"] and not ba["pass_gate"],
          "B: D1 fired under planted null")
    check(not ba["kill_fired"], "B: kill fired under planted null")

    # C — FAIL shape: kernel guidance actively harms (m-kern .40 vs .60).
    P_C = dict(P_A, **{"m-kern": 0.40})
    rows_c = _mock_rows(P_C, "C")
    out_c = analyze(rows_c, _mock_sidecar(rows_c))
    ca = out_c["analysis"]
    check(ca["kill_fired"], "C: kill did not fire under planted harm")
    check(not ca["pass_gate"], "C: pass_gate true under harm")

    # D — floor-bound D0: uniform truncation costs nothing (u-topk ~ b0).
    P_D = dict(P_A, **{"u-topk": 0.84, "m-kern": 0.85})
    rows_d = _mock_rows(P_D, "D")
    out_d = analyze(rows_d, _mock_sidecar(rows_d))
    da = out_d["analysis"]
    check(da["floor_bound"], "D: not floor-bound (d0=%s)"
          % da["d0_deficit_points"])
    check(da["d1_status"] == "NOT-LICENSED-FLOOR-BOUND"
          and da["d2_status"] == "NOT-LICENSED-FLOOR-BOUND"
          and not da["pass_gate"], "D: floor-bound did not de-license")

    # E — D2 UNINFORMATIVE: Jaccard gate fires on m-kern|m-emb.
    side_e = _mock_sidecar(rows_a)
    side_e["jaccard"]["m-kern|m-emb"] = 0.97
    out_e = analyze(rows_a, side_e)
    ea = out_e["analysis"]
    check(ea["d2b_status"] == "UNINFORMATIVE-JACCARD"
          and ea["d2_status"] == "UNINFORMATIVE" and not ea["pass_gate"],
          "E: Jaccard void did not yield UNINFORMATIVE (d2=%s)"
          % ea["d2_status"])

    # E2 — a CLEAN leg miss is decisive over another leg's void.
    P_E2 = dict(P_A, **{"m-freq": 0.84})     # leg (a) cleanly ties
    rows_e2 = _mock_rows(P_E2, "E2")
    side_e2 = _mock_sidecar(rows_e2)
    side_e2["jaccard"]["m-kern|m-emb"] = 0.97   # leg (b) void
    out_e2 = analyze(rows_e2, side_e2)
    check(out_e2["analysis"]["d2_status"] == "FAIL-TO-DEMONSTRATE",
          "E2: clean miss not decisive: %s"
          % out_e2["analysis"]["d2_status"])

    # G — load-gate VOID: m-kern loads off by > 5% => D1 VOID-LOAD.
    rows_g = [dict(r) for r in rows_a]
    for r in rows_g:
        if r["arm"] == "m-kern":
            r["loads_per_token"] = 700.0
    out_g = analyze(rows_g, _mock_sidecar(rows_g))
    ga = out_g["analysis"]
    check(ga["d1_status"] == "VOID-LOAD" and not ga["pass_gate"]
          and "m-kern" in ga["load_match"]["voided_arms"]
          and ga["d2_status"] == "UNINFORMATIVE",
          "G: load void shape wrong (%s/%s)" % (ga["d1_status"],
                                                ga["d2_status"]))

    # H — INSTRUMENT-INVALID gate shape: isolation protocol violated.
    side_h = _mock_sidecar(rows_a)
    side_h["isolation"]["env_echo_verified"] = False
    out_h = analyze(rows_a, side_h)
    check(not out_h["gates"]["isolation_protocol_valid"],
          "H: isolation gate did not fail")

    # H2 — drng exclusions over the 10% bound => leg (c) UNINFORMATIVE.
    side_h2 = _mock_sidecar(rows_a)
    excl_ids = sorted({r["item_id"] for r in rows_a})[:40]   # 12.5% of 320
    side_h2["drng"]["excluded_item_ids"] = excl_ids
    rows_h2 = [r for r in rows_a
               if not (r["arm"] == "m-drng" and r["item_id"] in excl_ids)]
    out_h2 = analyze(rows_h2, side_h2)
    check(out_h2["analysis"]["d2c_status"] == "UNINFORMATIVE-EXCLUSION",
          "H2: exclusion bound did not void leg (c): %s"
          % out_h2["analysis"]["d2c_status"])

    # Hardened-validation probes — each must be REJECTED fail-closed.
    side_ok = _mock_sidecar(rows_a)
    rows_frac = [dict(r) for r in rows_a]
    rows_frac[0]["correct"] = 0.5
    expect_reject(lambda: analyze(rows_frac, side_ok), "non-binary correct")
    rows_super = rows_a + [{"item_id": "it-extra-99", "cluster": 0,
                            "arm": "m-kern", "realization": 0, "correct": 1,
                            "loads_per_token": 606.3}]
    expect_reject(lambda: analyze(rows_super, side_ok), "arm superset")
    rows_short = [r for r in rows_a if r["item_id"] != "it-000-00"]
    expect_reject(lambda: analyze(rows_short, side_ok),
                  "n != manifest n (dropped item)")
    side_seed = _mock_sidecar(rows_a)
    side_seed["seeds"] = dict(SEED_REGISTRY, drng=[101, 102, 103])
    out_seed = analyze(rows_a, side_seed)
    check(not out_seed["gates"]["seeds_valid"],
          "unregistered seeds did not fail the seeds gate")
    side_floor = _mock_sidecar(rows_a)
    side_floor["floor_points"] = 2.0
    expect_reject(lambda: analyze(rows_a, side_floor),
                  "mutated floor threshold")
    side_inc = _mock_sidecar(rows_a)
    side_inc["inference"] = {"method": "bca", "dev_sign_symmetry_pass": True}
    expect_reject(lambda: analyze(rows_a, side_inc),
                  "incoherent inference method")
    side_noinf = _mock_sidecar(rows_a)
    del side_noinf["inference"]
    expect_reject(lambda: analyze(rows_a, side_noinf),
                  "missing inference block")
    side_ids = _mock_sidecar(rows_a)
    side_ids["manifest"]["eligible_ids_sha256"] = "00" * 32
    expect_reject(lambda: analyze(rows_a, side_ids),
                  "eligible-id-list hash mismatch")
    side_k = _mock_sidecar(rows_a)
    side_k["k_star"] = 6
    expect_reject(lambda: analyze(rows_a, side_k), "k_star off-grid")
    rows_noload = [dict(r) for r in rows_a]
    del rows_noload[0]["loads_per_token"]
    expect_reject(lambda: analyze(rows_noload, side_ok),
                  "missing loads_per_token")
    rows_badrz = [dict(r) for r in rows_a]
    for r in rows_badrz:
        if r["arm"] == "u-topk" and r["item_id"] == "it-000-00":
            r["realization"] = 1
    expect_reject(lambda: analyze(rows_badrz, side_ok),
                  "realization on a non-drng arm")

    # Pinned-file round-trip (exercises the stdin/pin path end-to-end).
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rp = Path(td) / "rows.jsonl"
        sp = Path(td) / "sidecar.json"
        rp.write_text("\n".join(json.dumps(r) for r in rows_a) + "\n",
                      encoding="utf-8")
        sp.write_text(json.dumps(_mock_sidecar(rows_a)), encoding="utf-8")
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

    # Output-surface completeness on BOTH branches.
    for branch, out in (("enumeration", out_a), ("bca", out_f)):
        for ptr in OUTPUT_FIELDS:
            node = out
            for part in ptr.strip("/").split("/"):
                check(isinstance(node, dict) and part in node,
                      "output field %s missing on %s branch" % (ptr, branch))
                node = node[part]

    print("MOCK-SELFTEST PASS: PASS shape on the enumeration AND the "
          "implemented BCa fallback branch; not-demonstrated-D1, "
          "planted-harm KILL, floor-bound D0, D2 UNINFORMATIVE (Jaccard), "
          "clean-miss-decisive, load-VOID, gate-failure, and "
          "exclusion-bound shapes all reached; 11/11 hardened rejections "
          "fail-closed; pin round-trip byte-stable; %d output fields "
          "present on both branches." % len(OUTPUT_FIELDS))
    return 0


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    rows, side = load_from_stdin()
    out = analyze(rows, side)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
