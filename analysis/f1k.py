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
docs/next/design/glm52-f1k-cost-reduction.md (ASM-2205):
R = 3 derangement passes (the §R6 pre-registered degradation step 1, applied
up front), spot/pinning savings are ops-side and touch nothing statistical.

GEOMETRY (REVISION-6, the maintainer-approved powered geometry 2026-07-15,
ASM-2369; docs/next/design/asm-f1k-geometry-2369-2375.json): C = 96 concept
clusters, n = 1,573 test items (the prior 1,440 cap RAISED to 1,573),
pre-registered effect mu* = +4.09 pts, replication R-vector (1, 3, 1) for
K-1/K-2/K-3. This geometry clears the exact cluster-sign-flip JOINT power
>= 0.80 at ALL THREE rungs (the $0 blind askability screen's n=1440
geometry missed K-3 at 0.7955 — the registered pre-run return that
triggered the maintainer ruling). CO-PRIMARY (ASM-2370): K-1, K-2 AND K-3
are co-primary — the record VERDICT PASS requires all three joint passes
(pass_gate = k1 & k2 & k3); a K~d2 tie now DENIES the PASS and is reported
at equal prominence as the content-not-structure datum.

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
  * LADDER (§2.6, ASM-2029/2036; CO-PRIMARY per ASM-2370): K-1 = K vs b0;
    K-2 = K vs the per-item MEAN correctness over the R = 3 d1-drng
    derangement passes (dose-exact deflator, §R2); K-3 = K vs d2
    (plain-dictionary knull) — the kernel-vs-generic hard bar, CO-PRIMARY
    at the REVISION-6 geometry. K-seam = K vs d3-text, DESCRIPTIVE both
    directions, never a rung. Failing rung n caps the claim at rung n-1;
    pass_gate = k1 & k2 & k3. Cluster-BCa 95% CIs are REGISTERED OUTPUTS
    for all three rungs (/analysis/k1_ci95, k2_ci95, k3_ci95).
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
    1,573 items (the maintainer-approved REVISION-6 cap, ASM-2369; the
    design runs AT the cap); any other n (e.g. 520, or the superseded
    1,440) is rejected, not analyzed.
  * C EXACT (GPT-5.6 pre-run review-gate RUN-HOLD fix, 2026-07-15): the b0
    universe must span EXACTLY C_REGISTERED = 96 concept clusters (the
    frozen REVISION-6 geometry, ASM-2369). Previously a 97-cluster universe
    at n = 1,573 satisfied the >=-form power gate and could PASS; any
    cluster count != 96 is now rejected fail-closed (ERR_P2_ANALYSIS) —
    off-geometry data can NEVER receive a valid verdict, and the power gate
    itself is equality-form (n_clusters == 96 AND clusters-with-m>=8 == 96
    AND n == 1,573).
  * NO ARM SUPERSETS: every (arm, pass) may score ONLY items in the b0
    universe; any item outside it is rejected (mandatory-arm UNDER-coverage
    stays an INSTRUMENT-INVALID gate: /gates/completeness_valid).
  * STRICT-BOOLEAN SIDECAR VALIDITY (GPT-5.6 pre-run review-gate HOLD
    blocker-1 fix, 2026-07-16): every sidecar validity flag (manifest
    commits, guard byte-identity, template checks, dose attestations,
    replace.ran) accepts ONLY a JSON boolean — Python truthiness previously
    admitted the JSON STRING "false" as a passing attestation
    (guard.byte_identical="false" reached an official PASS, reproduced).
    A non-bool or false flag fails its gate CLOSED (INSTRUMENT-INVALID);
    a non-bool replace.ran is a shape defect (ERR_P2_ANALYSIS). AND guard
    COMPLETENESS: guard.n_items must equal the registered 60 (§2.5) —
    previously ignored, so byte_identical=true over 0 items gated valid;
    0 or any mismatch now resolves INCOMPLETE/INVALID, never PASS.
  * DEFAULT-DENY SIDECAR SCHEMA (GPT-5.6 pre-run review-gate HOLD round-3
    fix, 2026-07-16 — closes the whole fail-open CLASS, not hole-by-hole):
    the verdict can be PASS ONLY if EVERY mandatory sidecar block AND flag
    is PRESENT and STRICT-valid. validate_sidecar() enforces, BEFORE any
    gate or statistic runs: (a) the top-level key set is EXACTLY the
    mandatory-block whitelist {manifest, guard, template, dose, inference,
    replace, carriers, power, cost} (+ the optional b0_ceiling_threshold
    echo) — unknown keys REJECTED; (b) every mandatory block is a JSON
    OBJECT — missing / null / wrong-type blocks REJECTED (previously a
    deleted power/cost/carriers block was copied to the output unvalidated
    and PASSed, and a deleted replace block fail-opened .get("ran", False)
    into a "valid defer"); (c) every mandatory FIELD of every block is
    PRESENT — a missing attestation key is incomplete instrument data,
    REJECTED, never a default; (d) replace.ran is a strict JSON boolean —
    a valid defer REQUIRES the replace block present with ran === false;
    (e) the power block is pinned to the REGISTERED values: joint_power
    must equal the frozen ASM-2371 per-rung table {K-1: 0.8043,
    K-2: 0.8058, K-3: 0.8001} EXACTLY, rho_u == 0.10, mu* figure == 4.09,
    and the ASM-2376 mc_intersection sim block must be a NON-EMPTY object;
    (f) cost.usd_total is a number in [0, 155] (the ASM-2374 registered
    ceiling — a sidecar attesting spend above the cap is not a valid
    success record), instance_hours/prefills are non-negative numbers;
    (g) carriers.concepts == 96 with positive integer params/bytes/layers.
    Rejections are fail-closed ERR_P2_ANALYSIS (verdict-gen aborts, NO
    verdict is producible); present-but-false/non-bool attestation VALUES
    keep failing their gates CLOSED to INSTRUMENT-INVALID. Both channels
    are non-PASS; nothing missing can ever default to an attestation.
  * COMPLETE kot-f1k-record/1 DECLARATIVE SCHEMA (GPT-5.6 pre-run
    review-gate HOLD round-4 fix, 2026-07-16 — rounds 1..3b each validated
    ONE level and the next re-review found the NEXT level unvalidated;
    this closes the DEPTH CLASS): the ENTIRE run record — the kot-log/1
    line's consumed surface (RECORD_SCHEMA: config/metrics pinned to the
    registered protocol/engine/n=1,573/R=3; declared rows_emitted ==
    rows actually pinned; closed key sets; pseudonymous runner), the FULL
    interior of EVERY sidecar block (SIDECAR_SCHEMA: replace requires ALL
    of {ran strict-bool, delta_r_dev, n_ni, io_saving} with §R-REV4.3
    run/defer coherence (a RUN needs a numeric dev delta, an NI power
    requirement n_ni <= 1,573, io_saving > 0; a defer forbids a non-null
    io_saving); mc_exact_power requires its FULL registered interior
    {mu_star 4.09, n_sim 10000, seed 20260713, pass true, joint_power ==
    ASM-2371 EXACT}; mc_intersection must equal the registered ASM-2376
    content EXACTLY — {"bogus":1} rejected; cost is fully typed (integer
    prefills, hours bounded by the 900 h REG wall-clock cap) AND
    ledger-coherent (usd_total ~= usd_spent_prior + run_hours*rate,
    instance_hours ~= construction + sum(phase_seconds)/3600 — usd_total=0
    with positive metered time rejected; HOLD ROUND-5, 2026-07-16: the
    ledger must price ALL metered work — prefills >= 1, phase_seconds must
    carry ALL of {pilot, guard, test} with positive seconds (an
    empty/partial phase map is an unmetered ledger, rejected), and
    usd_spent_prior must cover construction_instance_hours * rate, so
    usd_total transitively prices construction + run hours — an
    under-reported/zero cost ledger never validates); carriers must satisfy the frozen
    kaec_format arithmetic — params_added == C*layers*D for an INTEGER D
    (the real-run D = 6144 binds at the generator-spec/driver seam) and
    table_bytes == the exact KAEC fp32 file size), and EVERY row
    (ROW_SCHEMA below) — is validated RECURSIVELY, default-deny at EVERY
    depth: unknown keys rejected at every object node
    (additionalProperties:false), required fields at every depth, a
    type/registered-pin/bound on every leaf. Channels unchanged:
    structural/type/pin defects => ERR_P2_ANALYSIS; present-but-invalid
    attestation VALUES (the gate-judged _ATTEST leaves) => their gates
    fail CLOSED (INSTRUMENT-INVALID). HOLD ROUND-5 (2026-07-16, round-4
    re-review residuals): the open-ended "any" schema kind is REMOVED —
    pins_observed (round-4: an open-key map of "any" values, so
    {"arbitrary":{"bogus":1}} validated) is now a typed CLOSED map
    (pin-name key pattern -> {observed[, expected]} sha256 pairs); the
    kot-log/1 CHAIN fields (schema_version, seq, prev_sha256, ts,
    experiment, runner) are REQUIRED on every record line, so an
    UNSTAMPED record — one that never went through log-append — can
    never validate.
  * BINARY correctness: row "correct" must equal 0 or 1 (bools and any
    non-binary value rejected). ROW SCHEMA (round-4): every row validated
    against the CLOSED ROW_SCHEMA — arm in the registered 7-arm enum (an
    UNKNOWN-ARM row was previously ignored silently; now rejected), pass a
    STRICT JSON integer in its per-arm range (1..3 for d1-drng, exactly 0
    otherwise; the prior int() coercion of strings is REMOVED — "0"
    rejects), item_id/cluster/pred_label/gold_label nonempty strings, tags
    from the registered vocabulary, no unknown keys.
  * IMMUTABLE thresholds: the ceiling threshold is the pinned constant; the
    sidecar cannot move it.
  * REPLACE coherence: REPLACE rows present iff sidecar replace.ran; when
    ran, REPLACE must score the full universe (no partial-NI).

INPUT CONTRACT (kot-log/1, HOLD round-3 fix 2026-07-16 — the OFFICIAL
verdict-gen seam): each eligible stdin record (event=="run",
phase=="final", exit=="ok") is a kot-log/1 run-record line whose
`artifacts` ARRAY carries EXACTLY ONE {path, sha256, role:"rows"} entry
(the per-item rows JSONL) and EXACTLY ONE {path, sha256, role:"sidecar"}
entry (the run sidecar JSON) — the D10-paired convention: verdict-gen
re-verifies both pins at consumption time and hands this analysis the
RECORD LINE (never a bare rows expansion, which would strand the sidecar).
The superseded artifacts-as-dict form {rows_path, rows_sha256, ...} is
REJECTED (it was never kot-log/1-conformant and could not flow through
log-append/verdict-gen). All eligible records must pin the SAME artifact
tuple. HOLD round-4: every eligible line is additionally validated against
the closed RECORD_SCHEMA (kot-f1k-record/1) — config pinned to
{protocol: f1k-main-campaign, engine: colibri, n_test_items: 1573,
r_drng_passes: 3}, metrics.rows_emitted == the rows ACTUALLY pinned,
metrics.n_test_items == 1573, exactly the 2-entry rows+sidecar artifact
pair, the kot-log/1 chain fields REQUIRED (HOLD round-5: an unstamped
record rejects; round-4 typed them only when present), pins_observed a
typed closed map when present, no unknown keys — and any stdin line that
is NOT an eligible final run line is REJECTED, never silently skipped.
Rows and sidecar are loaded from the pinned paths (relative paths
resolve against the repo root), sha256 re-verified, fail closed, strict
RFC 8259 parsing (NaN/Infinity refused — the same hooks verdict-gen
applies; two independent enforcements); the
analysis is a pure function of those bytes. ROWS (JSONL), one row per scored (item x arm x pass):
  {item_id, cluster, arm in {b0,d0,d1-drng,d2,d3-text,K,REPLACE},
   pass (int; 1..3 for d1-drng, else 0), correct 0/1 (STRICTLY binary),
   tags [subset of {sense-pair, multi-concept, option-trigger}],
   pred_label, gold_label}  — validated per row against the closed
   ROW_SCHEMA (round-4; no unknown keys, no string/coerced pass values)
SIDECAR (JSON): manifest flags (pre-spend (A), B0, 5, 7, 6 committed;
test-untouched), off-concept guard result {n_items — MUST equal the
registered 60, byte_identical}, scoring-template checks,
dose-exactness checks (R = 3 seeds vs the registered [101, 102, 103],
derangement fixed-point-free, layerwise norm-matched), inference {method
"signflip"|"bca", dev_sign_symmetry_pass} (the §R-REV4.1a dev-selected
choice, frozen at addendum (6)), replace {ran, delta_r_dev, n_ni,
io_saving_bytes_per_gated_token}, carriers {params_added, table_bytes,
concepts, layers}, power {rho_u, joint_mde_points_at_rho_u,
mc_exact_power, mc_intersection (the ASM-2376 shared-K joint-dependence
intersection sim block; carried verbatim into
/analysis/power_scope/intersection_all_three — the Frechet bounds are
COMPUTED in this script from mc_exact_power.joint_power, never narrated)},
cost {the FULL resume-safe-ledger emission surface (round-4): usd_total,
instance_hours, prefills (round-5: >= 1), usd_spent_prior,
construction_instance_hours, spot_rate_usd_per_hour, phase_seconds
(round-5: ALL of pilot+guard+test required, each positive),
expert_pinning {PIN, PIN_GB, semantics}, resume_safe_ledger,
d3_text_deferred — typed, bounded, and ledger-coherent per
SIDECAR_SCHEMA/validate_sidecar incl. the round-5 all-metered-work
pricing floor},
b0_ceiling_threshold (optional; MUST equal 0.95 if present). Every
validity FLAG above must be a JSON boolean literal — strings ("false",
"true"), ints, and null are NOT attestations (HOLD blocker-1, 2026-07-16).

MOCK SELF-TEST: `python3 analysis/f1k.py --selftest` (optional argv; the
stdin path takes no flags) builds three synthetic campaigns (planted +10-pt
K lift on the sign-flip branch; the SAME campaign on the BCa fallback
branch; exact null) plus a pinned-file round-trip, asserts the full
verdict-bearing output surface (including the co-primary K~d2-tie shape:
K-1 and K-2 fire, K-3 ties -> pass_gate FALSE; and the executable
intersection disclosure: computed Frechet bounds + carried ASM-2376 sim
block), and probes every hardened rejection (n != 1,573, 97-cluster and
95-cluster OFF-GEOMETRY universes at n = 1,573 — the RUN-HOLD exploit
shape, arm superset, non-binary correct, mutated ceiling threshold,
incoherent inference method, string replace.ran) PLUS the strict-bool /
guard-completeness gate probes (HOLD blocker-1 fix: string/int/null
attestations and guard.n_items 0/mismatch must fail their gates closed)
PLUS the kot-f1k-record/1 FULL-DEPTH DEFAULT-DENY sweep (HOLD round-4
fix, superseding the round-3 top-level sweep: EVERY required key at
EVERY depth popped, EVERY nested block at null/int/string, an unknown
key injected at EVERY object/map node — all DERIVED from the declarative
schema itself; the named round-3b probes: replace sub-fields +
run/defer coherence, the full mc_exact_power interior, mc_intersection
== ASM-2376 EXACTLY incl. {"bogus":1}, cost typing + ledger coherence
incl. usd_total=0-with-positive-hours and 1e308 hours and 0.5 prefills,
carriers C*layers*D / KAEC-size arithmetic; ROW-SCHEMA probes incl. an
UNKNOWN-ARM row and the string-"0" pass; RECORD-level probes incl.
rows_emitted count coherence — each fail-closed to non-PASS: structural
defects ERR_P2_ANALYSIS, value defects INSTRUMENT-INVALID; the
kot-log/1 FULL-record round-trip with the superseded dict form and a
rows-only record both rejected; the all-true/all-present fixture must
still PASS) PLUS the HOLD ROUND-5 residual-gap probes (2026-07-16:
pins_observed junk {"arbitrary":{"bogus":1}} / off-pattern key /
non-sha256 observed each REJECTED with a typed positive control still
loading byte-identically; each of the six kot-log/1 chain fields popped
=> the UNSTAMPED record REJECTED; cost.prefills = 0, an empty phase map,
a missing/zero-second phase, and construction-hours-unpriced
usd_spent_prior each REJECTED) PLUS the HOLD ROUND-6 final-static-review
probes (2026-07-16: every validity/provenance regex is fullmatch + \\Z —
never $, which matches before a terminal newline — trailing-newline
runner / ts / prev_sha256 / prereg_hash / pins_observed key / observed
sha and an embedded-newline runner each REJECTED; and BUDGET-HONESTY
SCALE FLOORS at the registered ASM-2374 campaign scale: the all-zero
ledger (prefills=1, 1 s phases, $0 totals — identity-coherent within
tolerance), the positive-hours/zero-dollars ledger, and the coherently
10x-under-reported ledger each REJECTED, with the full-scale corner
ledger (~$146 / 521.2 h / 19,444 prefills) the passing fixture).
Exits 0 on green.

Fail-closed exits: any pin/shape violation prints ERR_P2_ANALYSIS to stderr
and exits 1 (=> verdict-gen ERR_P2_ANALYSIS); nothing falls back.

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS.
"""

import hashlib
import json
import math
import random
import re
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
POWER_GATE_MIN_C = 96    # clusters with m >= 8 (REVISION-6 each-cluster
                         # gate at the maintainer-approved C=96, ASM-2369;
                         # supersedes the §R-REV2.2 C>=65 gate)
POWER_GATE_MIN_M = 8
C_REGISTERED = 96        # EXACT registered cluster count (REVISION-6 frozen
                         # geometry, ASM-2369; GPT-5.6 pre-run review-gate
                         # RUN-HOLD fix 2026-07-15): the frozen geometry is
                         # exactly C = 96 — a realized b0 universe spanning
                         # ANY other cluster count (97, 95, ...) is
                         # OUT-OF-GEOMETRY data and is REJECTED fail-closed
                         # (ERR_P2_ANALYSIS), never gated, never analyzed,
                         # never able to PASS
N_REGISTERED = 1573      # the design runs AT the maintainer-approved cap
                         # (ASM-2369, 2026-07-15; raises the prior 1440);
                         # any other realized n is REJECTED fail-closed
N_MAX = 1573             # hard cap (REVISION-6 geometry, ASM-2369)
GUARD_N_REGISTERED = 60  # off-concept guard cardinality (§2.5; REG design.
                         # n_planned.off_concept_guard_items; the frozen
                         # REVISION-6 eval build test/dev/guard = 1573/96/60,
                         # ASM-2377). GPT-5.6 pre-run review-gate HOLD
                         # blocker-1 fix (2026-07-16): guard.n_items was
                         # previously IGNORED — byte_identical over 0 items
                         # gated valid. The guard gate now REQUIRES the
                         # sidecar to attest byte-identity over EXACTLY this
                         # many items; n_items = 0 or any mismatch is
                         # INCOMPLETE instrument data => the gate fails
                         # closed (INSTRUMENT-INVALID/INCOMPLETE), never PASS
CEILING_B0 = 0.95        # ceiling-bound threshold (§2.7) — IMMUTABLE; a
                         # sidecar carrying a different value is rejected
INFERENCE_METHODS = ("signflip", "bca")  # §R-REV4.1a dev-selected choice
MANDATORY_ARMS = ("b0", "d0", "d1-drng", "d2", "K")  # ladder arms, never
                                                     # droppable (§R6)
RHO_U_REGISTERED = 0.10   # frozen planning rho_U (§R-REV3.1 item 3)
MU_STAR_POINTS = 4.09     # frozen joint-MDE / mu* figure (§R-REV5, ASM-2369)
USD_CAP_REGISTERED = 155.0  # REG budget.usd_cap (ASM-2374, REVISION-6): a
                            # sidecar attesting realized spend above the
                            # registered ceiling is NOT a valid success
                            # record — rejected fail-closed, never analyzed
REGISTERED_JOINT_POWER = {"K-1": 0.8043, "K-2": 0.8058, "K-3": 0.8001}
#   The frozen ASM-2371 per-rung exact joint-power table (MEASURED, seed
#   20260713, REVISION-6 geometry). HOLD round-3 fix: the sidecar power
#   block must carry EXACTLY these registered marginals — arbitrary
#   figures (0.9/0.9/0.9) previously flowed unvalidated into
#   /analysis/power_scope and the Frechet computation.

# =============================================================================
# kot-f1k-record/1 — the COMPLETE declarative run-record schema
# (HOLD round-4 fix, 2026-07-16).
#
# Rounds 1..3b each validated ONE level and the re-review found the NEXT
# level unvalidated (geometry; top-level truthiness; top-level default-deny;
# nested sidecar interiors + rows). This section closes the CLASS for good:
# the ENTIRE f1k run record — the kot-log/1 line's consumed surface, the
# FULL interior of EVERY sidecar block, and EVERY per-item row — is
# validated RECURSIVELY against the single declarative schema below,
# default-deny at EVERY depth: unknown keys are rejected at every object
# node (additionalProperties:false), required fields are enforced at every
# depth, and every leaf carries a type / registered-pin / bound. No field
# at any depth is unvalidated.
#
# TWO CHANNELS (unchanged discipline, blocker-1 + round-3 precedent):
#   * a STRUCTURAL/TYPE defect (missing key, unknown key, wrong type,
#     off-registered pin, incoherent ledger/geometry arithmetic) rejects
#     fail-closed ERR_P2_ANALYSIS — no verdict of any kind is producible;
#   * a PRESENT-but-invalid attestation VALUE — the leaves marked _ATTEST
#     below, each judged by _strict_true (or typed equality) at its named
#     gate — fails its gate CLOSED to the INSTRUMENT-INVALID verdict path.
# Both channels are non-PASS; nothing missing can ever default.
RECORD_SCHEMA_ID = "kot-f1k-record/1"

MC_N_SIM = 10000         # frozen MC procedure (§R-REV5; REG
                         # mc_exact_power_confirmation: N_sim = 10000)
KAEC_HEADER_BYTES = 16   # 'KAEC' magic + <iii> nc/nl/D (generator-spec
                         # kaec_format; f1k_driver.py kaec_read/kaec_write).
                         # The carriers coherence below derives D from
                         # params_added / (C*layers) and requires it be a
                         # positive INTEGER plus the EXACT KAEC file-size
                         # arithmetic — the REAL-run D = 6144 is bound at
                         # the generator-spec/driver seam (kaec_format:
                         # "D = 6144"; kaec_read of the actual spliced
                         # table), while the driver's $0 --mock stub engine
                         # lawfully runs the same pinned analysis at its
                         # own tiny D, so the analysis pins ARITHMETIC
                         # CONSISTENCY, not the hidden dim itself
KAEC_MAX_LAYERS = 128    # structural sanity bound on nl — A(iv) caps the
                         # candidate splice-layer set at the union of the
                         # pilot grid's layer sets (<= ALL MoE layers of the
                         # pinned model, far below 128); an nl above this is
                         # not a lawful KAEC subset of any frozen (5) choice
RUN_PHASES = ("pilot", "guard", "test")
#   the driver Ledger's exhaustive run-phase key set (f1k_driver.py
#   score-loop `phase=` call sites; construction time is carried separately
#   as construction_instance_hours) — an unknown phase key is unintelligible
SPOT_RATE_MAX = 10.0     # structural sanity bound on $/instance-hour: the
                         # registered pessimistic corner is $0.28/h spot
                         # i4i.2xlarge (REG budget_note; driver
                         # SPOT_RATE_DEFAULT); no lawful i4i rate approaches
                         # this — a rate above it is a ledger defect
WALL_CLOCK_CAP_HOURS = 900.0  # REG budget.wall_clock_cap_hours — bounds
                              # every hours figure (rejects 1e308-class junk)
COST_TOL_USD = 0.01      # ledger-arithmetic tolerance: usd_total is emitted
                         # round(.,4), hours round(.,6), phase seconds
                         # round(.,3) (f1k_driver.py build_sidecar) — a cent
                         # absorbs every rounding path. NOTE (HOLD round-6
                         # fix): a tolerance is a ROUNDING absorber, never a
                         # scale anchor — with every total near zero the
                         # identities held trivially (prefills=1, 1 s
                         # phases, $0 totals validated). The BUDGET-HONESTY
                         # SCALE FLOORS below reject that class.
HOURS_TOL = 0.001        # instance-hours coherence tolerance (same rounding)

# --- BUDGET-HONESTY SCALE FLOORS (HOLD round-6 fix, 2026-07-16, final
# --- static review defect-2). The REG budget_note (ASM-2374, successor of
# --- ASM-2283/ASM-2205) registers the mandatory campaign at the pessimistic
# --- corner (100 s/prefill / 1.20x pinning / $0.28/h spot i4i.2xlarge):
# --- 22,516 prefills -> 521.2 instance-h -> ~$146; +REPLACE ~$156 (> cap,
# --- so REPLACE runs only under a measured <=$155 projection). A completed
# --- 1,573-item campaign therefore has a REGISTERED work scale: a ledger
# --- whose totals sit an order of magnitude below it is UNDER-REPORTED —
# --- never a valid success record — regardless of internal arithmetic
# --- coherence. Floors, all enforced in the schema (structural, fail
# --- closed ERR_P2_ANALYSIS):
PREFILLS_MANDATORY_MIN = 11011   # = N_REGISTERED * 7: every mandatory
                                 # arm-pass (b0, d0, d1-drng x3, d2, K; §R6
                                 # arms never droppable, d3-text alone
                                 # deferrable) over every test item at
                                 # least once — the metered prefill COUNT
                                 # is a deterministic function of the
                                 # frozen design, not of throughput
                                 # [MEASURED arithmetic]
USD_TOTAL_MIN = 73.0             # half the ASM-2374 corner $146
                                 # [STIPULATED headroom: the corner is
                                 # worst-case throughput; halving admits up
                                 # to 2x better-than-corner realized
                                 # throughput while rejecting any >=2x
                                 # under-report — the review's 10x-too-low
                                 # ledger ($14.6) rejects with margin]
INSTANCE_HOURS_MIN = 260.6       # half the ASM-2374 corner 521.2 h
                                 # [STIPULATED, same rule]; the 900 h REG
                                 # wall-clock cap stays the upper bound

REGISTERED_MC_INTERSECTION = {
    # The frozen ASM-2376 shared-K joint-dependence intersection sim
    # (MEASURED, seed 20260713; poc/f1k-askability/
    # power_intersection_n1573.py -> reports/power-intersection-n1573.json;
    # REG n_planned assumption VERBATIM; byte-identical to the driver's
    # [R3-POWER] pin). HOLD round-4: the sidecar block must equal this
    # registered content EXACTLY — {"bogus": 1} (or any drifted value) is
    # rejected, never carried "verbatim" into the disclosure unverified.
    "lambda_grid": [0.0, 0.25, 0.5, 0.75, 1.0],
    "intersection_power_by_lambda": [0.5220, 0.5675, 0.6165, 0.6763,
                                     0.7984],
    "range_under_family": [0.5220, 0.7984],
    "at_lambda_0.5": 0.6165,
    "seed": SEED,
}
MC_INTERSECTION_SE_MAX = 0.005   # registered "MC-SE <= 0.005" (ASM-2376)
MC_INTERSECTION_SOURCE = ("poc/f1k-askability/reports/"
                          "power-intersection-n1573.json")

ARMS_REGISTERED = ("b0", "d0", "d1-drng", "d2", "d3-text", "K", "REPLACE")
#   the CLOSED §2.6/§R1.2 arm enum (ANA docstring ROWS contract) — a row
#   under any other arm label is off-protocol data, rejected fail-closed
TAGS_REGISTERED = ("sense-pair", "multi-concept", "option-trigger")

# HOLD round-6 fix (2026-07-16, final static review defect-1): every
# validity/provenance-bearing regex is anchored with \Z and applied via
# re.fullmatch — NEVER $. Python's $ matches BEFORE a terminal newline,
# so under the former re.match(...$) discipline "runner-1\n", a 64-hex
# value + "\n", and a trailing-newline timestamp/pin-key all satisfied
# the declared "strict" patterns, weakening the runner, ts, sha256
# (prev_sha256 / prereg_hash / artifacts / pins_observed) and
# pins_observed-key constraints. fullmatch requires the ENTIRE string to
# match, so no trailing- or embedded-newline value can validate.
RUNNER_RE = r"^(runner|auditor|coordinator|writer|redteam)-[0-9]+\Z"
HEX64_RE = r"^[0-9a-f]{64}\Z"
TS_RE = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z"


# ---- schema-node constructors (kept tiny so the literals below read as a
# ---- declaration, not code) -------------------------------------------------
def _c(value):
    """Leaf pinned EXACTLY to a registered JSON value (type-strict:
    True never equals 1; 4.09 matches 4.09 across int/float)."""
    return {"kind": "const", "value": value}


def _t(kind, **kw):
    d = {"kind": kind}
    d.update(kw)
    return d


def _obj(required, optional=None):
    """Closed JSON object: key set EXACTLY required+optional
    (additionalProperties:false), every required key present, recurse."""
    return {"kind": "object", "required": required,
            "optional": optional or {}}


_ATTEST = {"kind": "attest"}
#   a GATE-JUDGED attestation VALUE leaf (HOLD round-5 fix, 2026-07-16:
#   the former open-ended "any" kind — _ANY — is REMOVED from the schema
#   language; every remaining recursion-terminating leaf is one of THESE,
#   and each one is judged downstream at its named validity gate):
#   presence is structural (required at its depth), but the VALUE is
#   deliberately judged at its GATE via _strict_true / typed equality so
#   a present-but-false/non-bool attestation resolves INSTRUMENT-INVALID
#   (blocker-1 channel), never ERR_P2_ANALYSIS. This kind is NEVER lawful
#   on a provenance/cost-bearing node whose value no gate judges — those
#   carry a type/registered-pin/bound (e.g. pins_observed, which round-4
#   left as an open map of "any" values, is now a typed closed map).
_HEX64 = _t("string", pattern=HEX64_RE)

SIDECAR_SCHEMA = _obj(
    required={
        "manifest": _obj({
            "pre_spend_committed": _ATTEST,
            "b0_addendum_committed": _ATTEST,
            "entry5_committed": _ATTEST, "entry7_committed": _ATTEST,
            "entry6_committed": _ATTEST,
            "test_untouched_until_complete": _ATTEST}),
        "guard": _obj({"n_items": _ATTEST, "byte_identical": _ATTEST}),
        "template": _obj({"labels_single_token": _ATTEST,
                          "header_cue_labels_trigger_free": _ATTEST}),
        "dose": _obj({"r_seeds": _ATTEST,
                      "derangement_no_fixed_point": _ATTEST,
                      "norm_matched_within_tol": _ATTEST}),
        "inference": _obj({
            # method/dev_sign_symmetry_pass are SHAPE, not attestation:
            # structural (unchanged since the FIX-FIRST review)
            "method": _t("enum", values=list(INFERENCE_METHODS)),
            "dev_sign_symmetry_pass": _t("bool")}),
        "replace": _obj({
            # HOLD round-4 (round-3b item 1): ALL mandatory sub-fields
            # required — not just `ran` (delta_r_dev/n_ni/io_saving were
            # unvalidated interior). n_ni is the §R-REV4.3/ASM-2124 NI
            # POWER REQUIREMENT n_NI = delta_R*DEFF/SE_NI^2 (a rounded
            # NUMBER, not an item count); the RUN decision is licensed
            # iff n_NI <= the registered n = 1,573 — enforced as
            # conditional coherence with `ran` in validate_sidecar below.
            "ran": _t("bool"),
            "delta_r_dev": _t("number", nullable=True),
            "n_ni": _t("number", nullable=True, min=0),
            "io_saving_bytes_per_gated_token": _t("number", nullable=True,
                                                  min=0)}),
        "carriers": _obj({
            # round-3b item 5: measurements validated against the frozen
            # C=96 expectation (KAEC arithmetic in validate_sidecar) —
            # arbitrary integers rejected
            "params_added": _t("int", min=1),
            "table_bytes": _t("int", min=1),
            "concepts": _c(C_REGISTERED),
            "layers": _t("int", min=1, max=KAEC_MAX_LAYERS)}),
        "power": _obj({
            "rho_u": _c(RHO_U_REGISTERED),
            "joint_mde_points_at_rho_u": _c(MU_STAR_POINTS),
            "mc_exact_power": _obj({
                # round-3b item 2: the FULL interior required with the
                # registered values (§R-REV5/ASM-2371; driver [FIX-7] pins
                # the same five) — previously only joint_power was checked
                "mu_star": _c(MU_STAR_POINTS),
                "n_sim": _c(MC_N_SIM),
                "seed": _c(SEED),
                "pass": _c(True),
                "joint_power": _c(REGISTERED_JOINT_POWER)}),
            "mc_intersection": _obj(
                # round-3b item 3: EXACT ASM-2376 equality on every
                # registered key ({"bogus": 1} rejected); the two extra
                # disclosure keys the driver permits are typed/pinned when
                # present (default-deny: nothing else may appear)
                {k: _c(v)
                 for k, v in sorted(REGISTERED_MC_INTERSECTION.items())},
                optional={
                    "mc_se_max": _t("number", min_ex=0,
                                    max=MC_INTERSECTION_SE_MAX),
                    "source": _c(MC_INTERSECTION_SOURCE)})}),
        "cost": _obj({
            # round-3b item 4: typed AND coherent — the full [FIX-7]
            # resume-safe-ledger emission surface (f1k_driver.py
            # build_sidecar), every key required and bounded; the
            # usd/hours/rate ledger arithmetic is re-verified in
            # validate_sidecar (1e308 hours REJECTED by the wall-clock
            # cap; 0.5 prefills REJECTED by the int type). HOLD round-6
            # fix: the totals now carry the BUDGET-HONESTY SCALE FLOORS —
            # min=0 made zero/near-zero totals schema-legal, so a ledger
            # with prefills=1, 1 s phases and $0 everywhere satisfied
            # every coherence identity within tolerance and validated; a
            # real mandatory campaign is ~$146 / 521.2 metered hours
            # (ASM-2374 corner), so zero AND under-reported (e.g. 10x-low)
            # ledgers are both rejected at the schema.
            "usd_total": _t("number", min=USD_TOTAL_MIN,
                            max=USD_CAP_REGISTERED),
            "instance_hours": _t("number", min=INSTANCE_HOURS_MIN,
                                 max=WALL_CLOCK_CAP_HOURS),
            # HOLD round-5: positive — the campaign scored SOMETHING;
            # round-6: the metered prefill COUNT is deterministic under
            # the frozen design (>= n * 7 mandatory arm-passes), so an
            # under-counted ledger rejects (budget honesty: ASM-2374
            # prices the campaign BY its prefills)
            "prefills": _t("int", min=PREFILLS_MANDATORY_MIN),
            "usd_spent_prior": _t("number", min=0,
                                  max=USD_CAP_REGISTERED),
            # round-6: strictly positive — the campaign BUILT carriers
            # (metered construction work, ASM-2374); a zero-construction
            # ledger is under-reported, and the round-5 prior-spend floor
            # (usd_spent_prior >= construction * rate) then prices it
            "construction_instance_hours": _t("number", min_ex=0,
                                              max=WALL_CLOCK_CAP_HOURS),
            "spot_rate_usd_per_hour": _t("number", min_ex=0,
                                         max=SPOT_RATE_MAX),
            # HOLD round-5: the phase map must be COMPLETE — the round-4
            # typed map restricted UNKNOWN keys but required NONE, so an
            # empty/partial phase map (an unmetered ledger) validated.
            # Now every registered run phase (pilot, guard, test — the
            # driver Ledger's exhaustive key set) must be present with a
            # POSITIVE metered duration; closed object, so unknown phase
            # keys stay rejected.
            "phase_seconds": _obj({p: _t("number", min_ex=0)
                                   for p in RUN_PHASES}),
            "expert_pinning": _obj({
                "PIN": _c("1"),
                "PIN_GB": _t("number", min_ex=0),
                "semantics": _t("string", min_len=1)}),
            "resume_safe_ledger": _t("string", min_len=1),
            "d3_text_deferred": _t("bool")}),
    },
    optional={
        # optional echo of the pinned constant — MUST equal it (§2.7)
        "b0_ceiling_threshold": _c(CEILING_B0),
    },
)

ROW_SCHEMA = _obj({
    # round-3b item 6: the CLOSED row schema — every field required and
    # typed, the arm enum closed, `pass` a STRICT integer (string "0" and
    # any int() coercion path rejected; the d1-drng 1..R / else 0 range is
    # enforced in validate_rows), tags drawn from the registered vocabulary.
    "item_id": _t("string", min_len=1),
    "cluster": _t("string", min_len=1),
    "arm": _t("enum", values=list(ARMS_REGISTERED)),
    "pass": _t("int", min=0, max=R_DRNG),
    "correct": _t("enum", values=[0, 1]),   # type-strict: True/"1" rejected
    "tags": _t("array", items=_t("enum", values=list(TAGS_REGISTERED))),
    "pred_label": _t("string", min_len=1),
    "gold_label": _t("string", min_len=1),
})

RECORD_SCHEMA = _obj(
    required={
        # the kot-log/1 line as consumed at this seam — this schema
        # re-verifies the f1k-consumed surface, default-deny. REQUIRED
        # here: the f1k CONTENT (eligibility triple, config, metrics,
        # artifacts) AND — HOLD round-5 fix, 2026-07-16 — the kot-log/1
        # CHAIN fields (schema_version/seq/prev_sha256/ts/experiment/
        # runner): round-4 typed them only WHEN PRESENT, so an UNSTAMPED
        # record (never through log-append, the single write path)
        # validated. Provenance is validity-bearing: an unchained line is
        # not an official record. On the official path log-append stamps
        # these and verdict-gen's chain walk re-verifies them; the
        # driver's --mock supplementary direct shape-check stamps the
        # SAME sentinel fields before piping (mirroring, never bypassing,
        # the stamp — the REAL stamp is exercised by its official-seam
        # step).
        "schema_version": _c("kot-log/1"),
        "seq": _t("int", min=0),
        "prev_sha256": _HEX64,
        "ts": _t("string", pattern=TS_RE),
        "experiment": _c("f1k"),
        "runner": _t("string", pattern=RUNNER_RE),
        "event": _c("run"),
        "phase": _c("final"),
        "exit": _c("ok"),
        "prereg_hash": _HEX64,   # equality with the frozen index is
                                 # verdict-gen's step-3 eligibility check
        "config": _obj({
            # the driver's emit_run_record config, pinned (round-3b:
            # declared n coherence — n_test_items must be the registered
            # 1573 at BOTH declaration sites)
            "protocol": _c("f1k-main-campaign"),
            "engine": _c("colibri"),
            "n_test_items": _c(N_REGISTERED),
            "r_drng_passes": _c(R_DRNG)}),
        "metrics": _obj({
            # rows_emitted == the rows actually pinned is re-verified in
            # load_from_stdin (declared-vs-actual count coherence)
            "rows_emitted": _t("int", min=1),
            "n_test_items": _c(N_REGISTERED)}),
        "artifacts": _t("array", min_len=2, max_len=2,
                        items=_obj({"path": _t("string", min_len=1),
                                    "sha256": _HEX64,
                                    "role": _t("enum",
                                               values=["rows",
                                                       "sidecar"])})),
    },
    optional={
        # lawful kot-log/1 run-line extras, typed (default-deny otherwise)
        "config_sha256": _HEX64,
        # HOLD round-5 fix: round-4 left pins_observed an OPEN-KEY map of
        # "any" values, so {"arbitrary": {"bogus": 1}} validated on a
        # provenance-bearing node. Now: pin-name keys (strict pattern) ->
        # a CLOSED {observed[, expected]} sha256 pair — the only shape a
        # kot-log/1 pin observation lawfully takes (the f1k driver emits
        # no pins_observed at all, so anything else here is provenance
        # noise and rejects).
        "pins_observed": _t("map", key_pattern=r"^[a-z0-9][a-z0-9_.-]*\Z",
                            values=_obj({"observed": _HEX64},
                                        optional={"expected": _HEX64})),
        "cost": _obj({}, optional={"usd": _t("number", min=0),
                                   "gpu_hours": _t("number", min=0),
                                   "cumulative_usd": _t("number", min=0)}),
        "error": _t("string", nullable=True),
        "note": _t("string"),
        "supersedes": _t("array", min_len=1, items=_HEX64),
    },
)


def _json_eq(a, b):
    """Type-strict JSON equality for registered pins: a bool NEVER equals
    an int (True != 1, the truthiness lesson applied to equality), numbers
    compare numerically across int/float, containers recurse."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, dict):
        return (isinstance(b, dict) and set(a) == set(b)
                and all(_json_eq(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return (isinstance(b, list) and len(a) == len(b)
                and all(_json_eq(x, y) for x, y in zip(a, b)))
    return type(a) is type(b) and a == b


def _sv(val, node, where):
    """Recursive kot-f1k-record/1 validator — every violation is a
    STRUCTURAL defect: fail-closed ERR_P2_ANALYSIS, no verdict producible.
    (_ATTEST leaves return immediately: their VALUES are gate-judged —
    the INSTRUMENT-INVALID channel; the open-ended "any" kind is REMOVED,
    HOLD round-5 fix.)"""
    kind = node["kind"]
    if kind == "attest":
        return
    if node.get("nullable") and val is None:
        return
    if kind == "const":
        if not _json_eq(val, node["value"]):
            fail("%s %s: %r != the registered pinned value %r — "
                 "default-deny at every depth (HOLD round-4 fix)"
                 % (RECORD_SCHEMA_ID, where, val, node["value"]))
    elif kind == "enum":
        if not any(_json_eq(val, v) for v in node["values"]):
            fail("%s %s: %r not in the closed enum %s (HOLD round-4 fix)"
                 % (RECORD_SCHEMA_ID, where, val, node["values"]))
    elif kind == "bool":
        if not isinstance(val, bool):
            fail("%s %s: %r is not a JSON boolean (HOLD round-4 fix)"
                 % (RECORD_SCHEMA_ID, where, val))
    elif kind in ("int", "number"):
        ok = (isinstance(val, int) and not isinstance(val, bool)) \
            if kind == "int" else _num(val)
        if not ok:
            fail("%s %s: %r is not a JSON %s (HOLD round-4 fix: no "
                 "coercion of strings/bools/null, ever)"
                 % (RECORD_SCHEMA_ID, where, val, kind))
        if not math.isfinite(val):
            fail("%s %s: non-finite number %r" % (RECORD_SCHEMA_ID, where,
                                                  val))
        if "min" in node and val < node["min"]:
            fail("%s %s: %r < registered minimum %r"
                 % (RECORD_SCHEMA_ID, where, val, node["min"]))
        if "min_ex" in node and val <= node["min_ex"]:
            fail("%s %s: %r <= registered exclusive minimum %r"
                 % (RECORD_SCHEMA_ID, where, val, node["min_ex"]))
        if "max" in node and val > node["max"]:
            fail("%s %s: %r > registered maximum %r"
                 % (RECORD_SCHEMA_ID, where, val, node["max"]))
    elif kind == "string":
        if not isinstance(val, str):
            fail("%s %s: %r is not a JSON string" % (RECORD_SCHEMA_ID,
                                                     where, val))
        if len(val) < node.get("min_len", 0):
            fail("%s %s: string shorter than %d" % (RECORD_SCHEMA_ID,
                                                    where,
                                                    node["min_len"]))
        # fullmatch, never match: $-anchored re.match let "value\n"
        # through on every provenance pattern (HOLD round-6 fix)
        if "pattern" in node and not re.fullmatch(node["pattern"], val):
            fail("%s %s: %r does not match the registered pattern %s "
                 "(fullmatch — trailing/embedded newlines never validate, "
                 "HOLD round-6 fix)"
                 % (RECORD_SCHEMA_ID, where, val, node["pattern"]))
    elif kind == "object":
        if not isinstance(val, dict):
            fail("%s %s: missing-or-not-a-JSON-object (got %s) — every "
                 "registered block must be present as an object at its "
                 "depth (HOLD round-4 fix)"
                 % (RECORD_SCHEMA_ID, where, type(val).__name__))
        allowed = set(node["required"]) | set(node["optional"])
        unknown = sorted(set(val) - allowed)
        if unknown:
            fail("%s %s: keys outside the registered whitelist: %s — "
                 "additionalProperties:false at EVERY depth (HOLD round-4 "
                 "fix)" % (RECORD_SCHEMA_ID, where, unknown))
        missing = sorted(set(node["required"]) - set(val))
        if missing:
            fail("%s %s: mandatory field(s) %s missing — absence is "
                 "incomplete instrument data, never a default (HOLD "
                 "round-4 fix)" % (RECORD_SCHEMA_ID, where, missing))
        for k, sub in node["required"].items():
            _sv(val[k], sub, "%s.%s" % (where, k))
        for k, sub in node["optional"].items():
            if k in val:
                _sv(val[k], sub, "%s.%s" % (where, k))
    elif kind == "map":
        if not isinstance(val, dict):
            fail("%s %s: not a JSON object (got %s)"
                 % (RECORD_SCHEMA_ID, where, type(val).__name__))
        if node.get("keys") is not None:
            unknown = sorted(set(val) - set(node["keys"]))
            if unknown:
                fail("%s %s: keys outside the registered key set %s: %s "
                     "(HOLD round-4 fix)" % (RECORD_SCHEMA_ID, where,
                                             node["keys"], unknown))
        if node.get("key_pattern") is not None:
            for k in sorted(val):
                if not isinstance(k, str) \
                        or not re.fullmatch(node["key_pattern"], k):
                    fail("%s %s: map key %r off the registered key "
                         "pattern %s (HOLD round-5 fix; round-6: "
                         "fullmatch, so a trailing-newline key never "
                         "validates)"
                         % (RECORD_SCHEMA_ID, where, k,
                            node["key_pattern"]))
        for k, v in sorted(val.items()):
            _sv(v, node["values"], "%s.%s" % (where, k))
    elif kind == "array":
        if not isinstance(val, list):
            fail("%s %s: not a JSON array (got %s)"
                 % (RECORD_SCHEMA_ID, where, type(val).__name__))
        if len(val) < node.get("min_len", 0) \
                or len(val) > node.get("max_len", len(val)):
            fail("%s %s: array length %d outside [%s, %s]"
                 % (RECORD_SCHEMA_ID, where, len(val),
                    node.get("min_len", 0), node.get("max_len", "inf")))
        for i, v in enumerate(val):
            _sv(v, node["items"], "%s[%d]" % (where, i))
    else:  # pragma: no cover — a schema typo must never fail open
        fail("%s %s: UNKNOWN schema node kind %r (schema defect — fail "
             "closed)" % (RECORD_SCHEMA_ID, where, kind))

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


def _strict_true(x):
    """True ONLY for the JSON literal `true` (a real Python bool).

    GPT-5.6 pre-run review-gate HOLD blocker-1 fix (2026-07-16): the
    sidecar validity gates previously used Python truthiness, so the JSON
    STRING "false" (and any non-empty string / non-zero int) counted as a
    passing attestation — guard.byte_identical = "false" reproducibly
    reached an official PASS. Every sidecar validity flag now counts ONLY
    a real JSON boolean `true`; a string, int, null, missing key, or
    `false` fails its gate CLOSED to the INSTRUMENT-INVALID verdict path —
    the same fail-closed lesson as the exact-C geometry gate, applied to
    the sidecar-validity channel."""
    return x is True


def _num(x):
    """A real JSON number (bool excluded — JSON true/false are not numbers)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_sidecar(side):
    """FULL-DEPTH default-deny validation (HOLD round-4 fix, 2026-07-16;
    supersedes the round-3 hand-coded top-level whitelist).

    (1) The COMPLETE declarative kot-f1k-record/1 sidecar schema is
    validated RECURSIVELY: closed key set + required fields at EVERY
    depth, types/registered pins/bounds on every leaf (see SIDECAR_SCHEMA;
    every round-3b nested finding — replace sub-fields, the mc_exact_power
    interior, the exact ASM-2376 mc_intersection content, cost typing,
    carriers typing — rejects here). (2) CROSS-FIELD COHERENCE that a
    per-leaf schema cannot express is then enforced, equally fail-closed:

      * replace conditional (§R-REV4.3/ASM-2124): ran === true REQUIRES a
        numeric delta_r_dev, a numeric NI power requirement
        n_ni <= the registered n = 1,573 (the RUN rule: n_NI =
        delta_R*DEFF/SE_NI^2 must fit the test set) and io_saving > 0
        (the driver refuses a RUN without a positive measured saving);
        ran === false REQUIRES io_saving null (a run outcome cannot exist
        for a deferred arm; the PRE-test gate measurements delta_r_dev /
        n_ni may lawfully be present on a defer);
      * carriers vs the frozen expectation (round-3b item 5):
        params_added must equal C*layers*D for an INTEGER hidden dim D
        (divisibility by C*layers; the REAL-run D = 6144 is bound at the
        generator-spec/driver kaec seam) and table_bytes == the exact
        KAEC fp32 layout size 16 + 4*layers + 4*params_added — arbitrary
        integers rejected;
      * cost ledger arithmetic (round-3b item 4): with
        run_h = sum(phase_seconds)/3600,
        instance_hours ~= construction_instance_hours + run_h (HOURS_TOL)
        and usd_total ~= usd_spent_prior + run_h * spot_rate_usd_per_hour
        (COST_TOL_USD) — usd_total = 0 with positive metered run time is
        REJECTED, never a valid success record.

    Attestation VALUES (the gate-judged _ATTEST leaves) that are present
    but false / non-bool keep failing their gates CLOSED
    (INSTRUMENT-INVALID) via _strict_true — the two fail-closed channels
    together leave no missing / null / wrong-type / off-pin path to PASS.

    HOLD ROUND-5 (2026-07-16) additions to the cost ledger: prefills >= 1
    (schema), the COMPLETE positive pilot/guard/test phase map (schema),
    and ALL metered work priced — usd_spent_prior must cover the metered
    construction spend, so usd_total transitively prices
    (construction + run) hours; an under-reported/zero ledger is never a
    valid success record.

    HOLD ROUND-6 (2026-07-16, final static review defect-2): the round-5
    identities were purely RELATIVE — with prefills=1, 1 s phases, and
    zero totals everything agreed within the rounding tolerances, so an
    all-zero ledger validated. The schema now carries BUDGET-HONESTY
    SCALE FLOORS at the registered campaign scale (ASM-2374 corner ~$146
    / 521.2 h / 22,516 prefills; floors USD_TOTAL_MIN / INSTANCE_HOURS_MIN
    / PREFILLS_MANDATORY_MIN, construction_instance_hours > 0): the
    all-zero, positive-hours/zero-dollars, and coherently-10x-under-
    reported ledgers all reject; the $155 ASM-2374 ceiling is unchanged
    as the upper bound."""
    _sv(side, SIDECAR_SCHEMA, "sidecar")

    # --- replace conditional coherence (round-3b item 1) --------------------
    rep = side["replace"]
    if rep["ran"] is True:
        if not _num(rep["delta_r_dev"]):
            fail("%s sidecar.replace: ran=true with delta_r_dev %r — the "
                 "addendum-6 dev delta MUST be the measured number that "
                 "licensed the RUN (§R-REV4.3)"
                 % (RECORD_SCHEMA_ID, rep["delta_r_dev"]))
        if not _num(rep["n_ni"]) or rep["n_ni"] > N_REGISTERED:
            fail("%s sidecar.replace: ran=true with n_ni %r — the "
                 "§R-REV4.3/ASM-2124 RUN decision is licensed ONLY when "
                 "the NI power requirement n_NI is a measured number <= "
                 "the registered n = %d (n_NI > n_max mandates DEFER)"
                 % (RECORD_SCHEMA_ID, rep["n_ni"], N_REGISTERED))
        io = rep["io_saving_bytes_per_gated_token"]
        if not _num(io) or io <= 0:
            fail("%s sidecar.replace: ran=true with io_saving %r — the NI "
                 "endpoint requires a positive measured expert-byte saving "
                 "(§R1.2/ASM-2037; the driver refuses a RUN without one)"
                 % (RECORD_SCHEMA_ID, io))
    else:
        if rep["io_saving_bytes_per_gated_token"] is not None:
            fail("%s sidecar.replace: ran=false with a non-null io_saving "
                 "%r — a run outcome cannot exist for a deferred arm "
                 "(§R-REV4.3 PRE-test decision; the PRE-test gate "
                 "measurements delta_r_dev/n_ni may lawfully persist on a "
                 "defer)"
                 % (RECORD_SCHEMA_ID,
                    rep["io_saving_bytes_per_gated_token"]))

    # --- carriers vs the frozen expectation (round-3b item 5) ---------------
    car = side["carriers"]
    per_dim = C_REGISTERED * car["layers"]
    if car["params_added"] % per_dim != 0:
        fail("%s sidecar.carriers: params_added %r is not C*layers*D for "
             "any integer hidden dim D (not divisible by C*layers = "
             "%d*%d = %d) — the frozen kaec_format expectation "
             "(K[nc*nl*D]; ASM-2369 geometry); arbitrary integers are "
             "rejected (HOLD round-4 fix; the REAL-run D = 6144 is bound "
             "at the generator-spec/driver kaec seam)"
             % (RECORD_SCHEMA_ID, car["params_added"], C_REGISTERED,
                car["layers"], per_dim))
    want_bytes = KAEC_HEADER_BYTES + 4 * car["layers"] \
        + 4 * car["params_added"]
    if car["table_bytes"] != want_bytes:
        fail("%s sidecar.carriers: table_bytes %r != the exact KAEC fp32 "
             "layout size 16 + 4*nl + 4*nc*nl*D = %d (generator-spec "
             "kaec_format; f1k_driver.py kaec_write) — arbitrary integers "
             "are rejected (HOLD round-4 fix)"
             % (RECORD_SCHEMA_ID, car["table_bytes"], want_bytes))

    # --- cost ledger arithmetic (round-3b item 4) ---------------------------
    cost = side["cost"]
    run_h = sum(cost["phase_seconds"].values()) / 3600.0
    want_hours = cost["construction_instance_hours"] + run_h
    if abs(cost["instance_hours"] - want_hours) > HOURS_TOL:
        fail("%s sidecar.cost: instance_hours %r incoherent with "
             "construction_instance_hours + sum(phase_seconds)/3600 = %.6f "
             "(the [FIX-7] resume-safe ledger identity; tolerance %s) — "
             "an unmetered hours figure is not a valid success record "
             "(HOLD round-4 fix)"
             % (RECORD_SCHEMA_ID, cost["instance_hours"], want_hours,
                HOURS_TOL))
    want_usd = cost["usd_spent_prior"] \
        + run_h * cost["spot_rate_usd_per_hour"]
    if abs(cost["usd_total"] - want_usd) > COST_TOL_USD:
        fail("%s sidecar.cost: usd_total %r incoherent with "
             "usd_spent_prior + run_hours*rate = %.4f (tolerance $%s) — "
             "e.g. usd_total = 0 with positive metered run time can never "
             "be a valid success record (HOLD round-4 fix; REG budget_note "
             "meters the ledger)"
             % (RECORD_SCHEMA_ID, cost["usd_total"], want_usd,
                COST_TOL_USD))
    # --- ALL metered work priced (HOLD round-5 fix, 2026-07-16) --------------
    # The identities above alone never priced CONSTRUCTION: a ledger with
    # usd_spent_prior = 0 and POSITIVE construction_instance_hours still
    # satisfied usd_total ~= prior + run_h*rate near $0 — an
    # under-reported ledger validated (budget honesty broken).
    # Construction time is metered work on the same registered instance
    # (ASM-2374 prices the construction prefills at the same $/h corner;
    # the driver Ledger requires construction hours + prior spend as
    # explicit config, "never silent zeros"), so the prior-spend figure
    # must at least COVER it — usd_total then transitively covers
    # (construction_instance_hours + run_h) * rate: every metered hour
    # and every prefill-bearing phase is priced (prefills >= 1 and the
    # complete positive phase map are enforced by the schema above).
    prior_floor = cost["construction_instance_hours"] \
        * cost["spot_rate_usd_per_hour"]
    if cost["usd_spent_prior"] + COST_TOL_USD < prior_floor:
        fail("%s sidecar.cost: usd_spent_prior %r does not cover the "
             "metered construction spend construction_instance_hours * "
             "spot_rate = %.4f (tolerance $%s) — construction hours are "
             "metered work (ASM-2374; [FIX-7] ledger contract): an "
             "under-reported ledger (e.g. usd_total ~ 0 with positive "
             "construction hours) is never a valid success record (HOLD "
             "round-5 fix)"
             % (RECORD_SCHEMA_ID, cost["usd_spent_prior"], prior_floor,
                COST_TOL_USD))


def validate_rows(rows):
    """FULL row-schema validation (HOLD round-4 fix; round-3b item 6): every
    row against the closed ROW_SCHEMA (arm enum, strict-int pass, strictly
    binary correct, registered tag vocabulary, all fields required, no
    unknown keys) PLUS the per-arm pass-range coherence (1..R for d1-drng,
    exactly 0 otherwise). Structural — fail-closed ERR_P2_ANALYSIS."""
    if not rows:
        fail("%s rows: empty — no per-item rows, no analysis"
             % RECORD_SCHEMA_ID)
    for i, r in enumerate(rows):
        where = "row %d" % i
        _sv(r, ROW_SCHEMA, where)
        p = r["pass"]
        if r["arm"] == "d1-drng":
            if not 1 <= p <= R_DRNG:
                fail("%s %s: d1-drng pass %r outside the registered 1..%d "
                     "(§R2 dose-exact deflator)" % (RECORD_SCHEMA_ID, where,
                                                    p, R_DRNG))
        elif p != 0:
            fail("%s %s: arm %s carries pass %r — only d1-drng is "
                 "multi-pass (contract: pass 1..%d for d1-drng, else 0)"
                 % (RECORD_SCHEMA_ID, where, r["arm"], p, R_DRNG))


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
    a fractional or boolean correctness value is a scorer defect, not data.
    HOLD round-4: rows arrive here ONLY after validate_rows (full closed
    ROW_SCHEMA), so `pass` is read as the validated strict integer — the
    prior int() coercion of r.get("pass") is REMOVED (a string "0" or a
    missing key is now a structural rejection upstream, never coerced)."""
    byarm, clusters, tags, labels = {}, {}, {}, {}
    for r in rows:
        for k in ("item_id", "cluster", "arm", "correct"):
            if k not in r:
                fail("row missing %r: %s" % (k, json.dumps(r)[:200]))
        c = r["correct"]
        if isinstance(c, bool) or not (c == 0 or c == 1):
            fail("non-binary correct %r (must be 0 or 1): %s"
                 % (c, json.dumps(r)[:200]))
        arm, p, iid = r["arm"], r["pass"], r["item_id"]
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
    # FULL-DEPTH default-deny validation FIRST (HOLD round-3 fix, extended
    # to the COMPLETE kot-f1k-record/1 schema round-4): no gate, statistic,
    # or output copy runs on a structurally incomplete sidecar OR row set.
    validate_sidecar(side)
    validate_rows(rows)
    byarm, clusters, tags, labels = index_rows(rows)
    b0 = arm_items(byarm, "b0")
    karm = arm_items(byarm, "K")
    d0 = arm_items(byarm, "d0")
    d2 = arm_items(byarm, "d2")
    d3 = arm_items(byarm, "d3-text")
    drng = drng_mean(byarm)
    if not b0 or not karm:
        fail("mandatory arms b0/K missing from rows")
    # d3-text deferral coherence (HOLD round-4): the addendum-7 decision is
    # attested in cost.d3_text_deferred ([FIX-4]); the rows must agree —
    # d3-text rows present iff NOT deferred (like the REPLACE run/defer
    # coherence below, the decision is PRE-test and cannot drift silently).
    if bool(d3) == side["cost"]["d3_text_deferred"]:
        fail("d3-text coherence violated: rows %s but sidecar "
             "cost.d3_text_deferred=%r — the addendum-7 deferral decision "
             "is PRE-test (§R6; HOLD round-4 fix)"
             % ("present" if d3 else "absent",
                side["cost"]["d3_text_deferred"]))

    # --- HARDENED VALIDATION (codex FIX-FIRST review; fail-closed) ---------
    universe = set(b0)
    if len(universe) != N_REGISTERED:
        fail("registered n violated: b0 scores %d items but the frozen "
             "design runs AT the cap n = %d (§R-REV3.1 item 4) — any other "
             "realized n is rejected, never analyzed" % (len(universe),
                                                         N_REGISTERED))
    # GEOMETRY EXACT (GPT-5.6 pre-run review-gate RUN-HOLD fix, 2026-07-15):
    # the frozen REVISION-6 geometry is EXACTLY C = 96 clusters (ASM-2369).
    # Before this fix a 97-cluster universe at n = 1573 satisfied the >=-form
    # power gate and could reach pass_gate=true — OUT-OF-GEOMETRY data
    # receiving a valid PASS. Any realized cluster count != C_REGISTERED is
    # now REJECTED fail-closed here (ERR_P2_ANALYSIS), never gated, never
    # analyzed; an off-geometry run can NEVER PASS.
    realized_c = len({clusters[i] for i in universe})
    if realized_c != C_REGISTERED:
        fail("registered geometry violated: b0 test items span %d concept "
             "clusters but the frozen REVISION-6 geometry is EXACTLY C = %d "
             "(ASM-2369) — off-geometry data (97-cluster, 95-cluster, ... "
             "universes) is rejected fail-closed, never analyzed"
             % (realized_c, C_REGISTERED))
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
    # STRICT-BOOLEAN sidecar validity (GPT-5.6 pre-run review-gate HOLD
    # blocker-1 fix, 2026-07-16): every attestation below accepts ONLY the
    # JSON literal `true` via _strict_true (bool() truthiness previously
    # admitted the string "false" and produced an official PASS — the
    # reproduced spurious-PASS channel). Anything non-bool or false fails
    # the gate CLOSED (INSTRUMENT-INVALID), never a truthy PASS.
    man = side.get("manifest") or {}
    manifest_valid = all(_strict_true(man.get(k)) for k in (
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
    # Exact-geometry gate (RUN-HOLD fix): the hard rejection above already
    # guarantees n_clusters == C_REGISTERED and n_items == N_REGISTERED, so
    # this gate can only fail on an in-geometry ALLOCATION defect — some
    # registered cluster carrying m < 8 (c_ge8 == C_REGISTERED demands EVERY
    # cluster clear the m >= 8 floor). Equality throughout, never >=.
    power_gate = (n_clusters == C_REGISTERED
                  and c_ge8 == C_REGISTERED
                  and n_items == N_REGISTERED)

    # GUARD COMPLETENESS (HOLD blocker-1): the off-concept instrument must
    # attest byte-identity over EXACTLY the registered GUARD_N_REGISTERED
    # = 60 items (§2.5). n_items was previously ignored: n_items = 0 with
    # byte_identical = true gated valid — incomplete instrument data
    # reaching PASS. 0, any mismatch, or a non-integer count now fails the
    # gate closed (INCOMPLETE/INSTRUMENT-INVALID), never a PASS.
    guard = side.get("guard") or {}
    g_n = guard.get("n_items")
    guard_valid = (_strict_true(guard.get("byte_identical"))
                   and isinstance(g_n, int) and not isinstance(g_n, bool)
                   and g_n == GUARD_N_REGISTERED)

    tpl = side.get("template") or {}
    template_valid = all(_strict_true(tpl.get(k)) for k in (
        "labels_single_token", "header_cue_labels_trigger_free"))

    dose = side.get("dose") or {}
    # r_seeds must be the registered LIST exactly (typed: a non-list —
    # null/int/string — fails the gate closed, never raises; HOLD round-3
    # default-deny discipline on every attestation read).
    rs = dose.get("r_seeds")
    dose_valid = (isinstance(rs, list) and rs == DRNG_SEEDS
                  and _strict_true(dose.get("derangement_no_fixed_point"))
                  and _strict_true(dose.get("norm_matched_within_tol"))
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
    pass_gate = bool(k1_fire and k2_fire and k3_fire)  # CO-PRIMARY
    # discipline (ASM-2370, REVISION-6): the deciding four-condition
    # kernel-vs-generic test — a record PASS requires ALL THREE rungs
    # (seam works AND alignment matters AND kernel beats the matched
    # dictionary). A K~d2 tie DENIES the PASS and is reported at equal
    # prominence as the content-not-structure datum (ladder rung 2).

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
    rep_side = side["replace"]
    # validate_sidecar guarantees the replace block is PRESENT with ran a
    # strict JSON boolean (HOLD round-3 item 1: a valid defer REQUIRES the
    # block present with ran === false — .get("ran", False) previously
    # fail-opened a missing block/key into a "valid defer" and a PASS).
    ran_flag = rep_side["ran"]
    if bool(rep) != ran_flag:
        fail("REPLACE coherence violated: rows %s but sidecar replace.ran="
             "%r — the run/defer decision is PRE-test (§R-REV4.3)"
             % ("present" if rep else "absent", ran_flag))
    rep_ran = bool(rep) and ran_flag
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
    # CO-PRIMARY INTERSECTION disclosure — EXECUTABLE, not prose (GPT-5.6
    # pre-run review-gate RUN-HOLD defect-2 fix, 2026-07-15; ASM-2376): the
    # registered >= 0.80 power criterion is PER-RUNG (ASM-2371); the
    # probability that ALL THREE co-primary rungs fire simultaneously at
    # mu* is NOT bounded below by 0.80. The assumption-free Frechet bounds
    # max(0, 1 - sum_j(1-p_j)) <= P(all 3) <= min_j p_j are COMPUTED here
    # from the sidecar-carried per-rung powers; the shared-K
    # joint-dependence sim result (poc/f1k-askability/
    # power_intersection_n1573.py -> reports/power-intersection-n1573.json)
    # is carried from the sidecar power.mc_intersection block.
    jp = (power.get("mc_exact_power") or {}).get("joint_power") or {}
    rung_p = [jp.get(k) for k in ("K-1", "K-2", "K-3")]
    if all(isinstance(x, (int, float)) and not isinstance(x, bool)
           for x in rung_p):
        frechet = [round(max(0.0, 1.0 - sum(1.0 - x for x in rung_p)), 4),
                   round(min(rung_p), 4)]
    else:
        frechet = None
    power_scope = {
        "rho_u_planning": power.get("rho_u"),
        "joint_mde_points_at_rho_u": power.get("joint_mde_points_at_rho_u"),
        "mc_exact_power": power.get("mc_exact_power"),
        "intersection_all_three": {
            "not_separately_powered": True,
            "frechet_bounds_from_marginals": frechet,
            "mc_joint_dependence_sim": power.get("mc_intersection"),
            "wording": "P(K-1 AND K-2 AND K-3 all fire at mu*) is NOT >= "
                       "0.80 and is NOT separately powered: marginals alone "
                       "bound it only to the Frechet interval above; the "
                       "shared-K joint-dependence sim (ASM-2376, seed "
                       "20260713, marginals preserved exactly) measured it "
                       "across the full dependence grid. Consequence: "
                       "elevated INCONCLUSIVE (2-of-3) risk, NEVER a false "
                       "null — TOST/NULL rides only on K-1 and "
                       "ladder_rung_reached reports how far the evidence "
                       "got.",
        },
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
def _role_pin(art, role, what):
    """The record's single {path, sha256, role:<role>} artifacts entry
    (kot-log/1 array form, D10-paired convention — HOLD round-3 fix).
    Zero or duplicate entries for a role are unintelligible; fail closed."""
    ents = [a for a in art if isinstance(a, dict) and a.get("role") == role]
    if len(ents) != 1:
        fail("%s: artifacts must carry EXACTLY ONE role:%r entry "
             "(got %d) — the kot-log/1 D10-paired rows+sidecar convention "
             "(HOLD round-3 fix, 2026-07-16)" % (what, role, len(ents)))
    e = ents[0]
    if not isinstance(e.get("path"), str) or not e["path"] \
            or not isinstance(e.get("sha256"), str) or not e["sha256"]:
        fail("%s: role:%r artifacts entry lacks a string path/sha256: %r"
             % (what, role, e))
    return e["path"], e["sha256"]


def _refuse_constant(name):
    """json.loads parse_constant hook: NaN/Infinity/-Infinity are NOT JSON
    (RFC 8259 §6) — the same strictness verdict-gen applies at ITS pin
    verification; two independent enforcements of one contract."""
    raise ValueError("non-standard JSON constant %s" % name)


def _finite_float(s):
    v = float(s)
    if not math.isfinite(v):
        raise ValueError("numeric literal %s is non-finite" % s)
    return v


def _loads_strict(raw, what):
    try:
        return json.loads(raw if isinstance(raw, str)
                          else raw.decode("utf-8"),
                          parse_constant=_refuse_constant,
                          parse_float=_finite_float)
    except (ValueError, UnicodeDecodeError) as e:
        fail("%s is not strict RFC 8259 JSON: %s" % (what, e))


def load_from_stdin():
    eligible = []
    for i, line in enumerate(sys.stdin):
        line = line.strip()
        if not line:
            continue
        rec = _loads_strict(line, "stdin line %d" % i)
        if not isinstance(rec, dict) \
                or rec.get("event") != "run" or rec.get("phase") != "final" \
                or rec.get("exit") != "ok":
            # HOLD round-4 default-deny at the seam: verdict-gen feeds this
            # analysis ONLY eligible final run lines (f1k declares no D9
            # reuse) — anything else on stdin is unintelligible input,
            # never silently skipped.
            fail("stdin line %d is not an eligible f1k run record "
                 "(event/phase/exit) — the %s seam admits only "
                 "chain-verified final run lines (HOLD round-4 fix)"
                 % (i, RECORD_SCHEMA_ID))
        eligible.append(rec)
    if not eligible:
        fail("no eligible run records on stdin")
    pins = set()
    for rec in eligible:
        art = rec.get("artifacts")
        if not isinstance(art, list):
            fail("eligible record's artifacts is %s, not the kot-log/1 "
                 "ARRAY of {path, sha256, role} entries — the superseded "
                 "dict form never conformed to kot-log/1 and cannot flow "
                 "through log-append/verdict-gen (HOLD round-3 fix)"
                 % type(art).__name__)
        what = "run record seq %s" % rec.get("seq")
        rows_path, rows_sha = _role_pin(art, "rows", what)
        side_path, side_sha = _role_pin(art, "sidecar", what)
        pins.add((rows_path, rows_sha, side_path, side_sha))
    if len(pins) != 1:
        fail("eligible records pin DIFFERENT artifacts: %s" % sorted(pins))
    rows_path, rows_sha, side_path, side_sha = next(iter(pins))
    rows_raw = read_pinned(rows_path, rows_sha, "f1k rows")
    side_raw = read_pinned(side_path, side_sha, "f1k sidecar")
    rows = [_loads_strict(x, "pinned rows line")
            for x in rows_raw.decode("utf-8", "replace").splitlines()
            if x.strip()]
    side = _loads_strict(side_raw, "pinned sidecar")
    if not isinstance(side, dict):
        fail("sidecar is not a JSON object")
    # FULL kot-f1k-record/1 record-line validation + declared-vs-actual
    # row-count coherence (HOLD round-4 fix; round-3b item 6): every
    # eligible line is validated against the closed RECORD_SCHEMA (config
    # pinned to the registered protocol/engine/n/R; metrics typed), and
    # the DECLARED rows_emitted must equal the rows ACTUALLY pinned —
    # 1,573-item coherence then follows from the analyze() n/geometry
    # rejections over the same rows.
    for rec in eligible:
        what = "run record seq %s" % rec.get("seq")
        _sv(rec, RECORD_SCHEMA, what)
        declared = rec["metrics"]["rows_emitted"]
        if declared != len(rows):
            fail("%s %s: metrics.rows_emitted declares %d rows but the "
                 "pinned rows artifact carries %d — declared/actual count "
                 "coherence (HOLD round-4 fix)"
                 % (RECORD_SCHEMA_ID, what, declared, len(rows)))
    return rows, side


# ---------------------------------------------------------------------------
# MOCK self-test
# ---------------------------------------------------------------------------
def _mock_campaign(p_by_arm, rng, C=96, m=16, extra=37, shared_null=False):
    """shared_null=True plants an EXACT per-item null: one correctness draw
    shared by every arm/pass, so every paired diff is identically 0 (the
    TOST/NULL shape); otherwise arms draw independently at their p.
    Geometry mirrors REVISION-6 (ASM-2369): C=96 clusters, the first
    `extra`=37 clusters carry m+1=17 items and the rest m=16, so
    37*17 + 59*16 = 1,573 = N_REGISTERED exactly."""
    rows = []
    lab = "ABCD"
    for c in range(C):
        for j in range(m + (1 if c < extra else 0)):
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
        # KAEC-coherent (round-4): params = C*nl*D = 96*4*6144; file size =
        # 16-byte header + 4*nl layer ids + 4 bytes/param fp32 body
        "carriers": {"params_added": 96 * 4 * 6144,
                     "table_bytes": 16 + 4 * 4 + 4 * (96 * 4 * 6144),
                     "concepts": 96, "layers": 4},
        "power": {"rho_u": 0.10, "joint_mde_points_at_rho_u": 4.09,
                  "mc_exact_power": {"mu_star": 4.09, "n_sim": 10000,
                                     "joint_power": {"K-1": 0.8043,
                                                     "K-2": 0.8058,
                                                     "K-3": 0.8001},
                                     "seed": SEED, "pass": True},
                  # ASM-2376 (MEASURED, seed 20260713): the shared-K
                  # joint-dependence intersection sim, poc/f1k-askability/
                  # power_intersection_n1573.py — the executable successor
                  # of the withdrawn "~0.70-0.75" prose figure.
                  "mc_intersection": {
                      "lambda_grid": [0.0, 0.25, 0.5, 0.75, 1.0],
                      "intersection_power_by_lambda": [0.5220, 0.5675,
                                                       0.6165, 0.6763,
                                                       0.7984],
                      "range_under_family": [0.5220, 0.7984],
                      "at_lambda_0.5": 0.6165,
                      "mc_se_max": 0.005, "seed": SEED,
                      "source": "poc/f1k-askability/reports/"
                                "power-intersection-n1573.json"}},
        # the FULL [FIX-7] resume-safe-ledger emission surface at the
        # REGISTERED campaign scale (round-6: the fixture is the ASM-2374
        # corner ledger — the "correct full-scale ledger" positive
        # control for the budget-honesty floors): run_h = 1,620,360 s /
        # 3600 = 450.1 h; usd = 19.94 + 450.1*0.28 = 145.968 (<= the $155
        # cap); hours = 71.1 + 450.1 = 521.2; prior 19.94 >= construction
        # 71.1 h * 0.28 = 19.908 (round-5 floor); prefills = pilot 6,200
        # + guard 660 + test 1,573*8 = 19,444 (REG budget_note volumes)
        "cost": {"usd_total": 145.968, "instance_hours": 521.2,
                 "prefills": 19444, "usd_spent_prior": 19.94,
                 "construction_instance_hours": 71.1,
                 "spot_rate_usd_per_hour": 0.28,
                 "phase_seconds": {"pilot": 516600.0, "guard": 55000.0,
                                   "test": 1048760.0},
                 "expert_pinning": {"PIN": "1", "PIN_GB": 40.0,
                                    "semantics": "PIN=1 pins the hot "
                                    "expert working set resident; PIN_GB "
                                    "= pinned budget in GB."},
                 "resume_safe_ledger": "out/f1k-main/cost-ledger.json",
                 "d3_text_deferred": False},
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

    # Mock A — planted +10-pt K lift over b0/d0/drng AND d2 (all three
    # co-primary rungs fire); sign-flip branch (dev sign-symmetry passed)
    rng = random.Random(4242)
    rows_a = _mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                             "d2": 0.70, "d3-text": 0.71, "K": 0.80}, rng)
    out_a = analyze(rows_a, _mock_sidecar())
    g = out_a["gates"]
    a = out_a["analysis"]
    check(all(g.values()), "mock A: some gate failed: %s" % g)
    check(a["inference_method"] == "signflip", "mock A: method not signflip")
    check(a["k1_joint_pass"], "mock A: K-1 did not fire (lift=%s p=%s)"
          % (a["k1_lift_points"], a["k1_p"]))
    check(a["k2_joint_pass"], "mock A: K-2 did not fire")
    check(a["k3_joint_pass"], "mock A: K-3 did not fire")
    check(a["pass_gate"], "mock A: pass_gate false")
    check(not a["kill_fired"], "mock A: kill fired")
    check(not a["null_equiv"], "mock A: null_equiv true under planted lift")
    check(a["ladder_rung_reached"] == 3, "mock A: ladder != 3")
    check(a["n_items"] == 1573 and a["n_clusters"] == 96,
          "mock A: grid wrong (n=%s C=%s)" % (a["n_items"],
                                              a["n_clusters"]))
    # Executable intersection disclosure (RUN-HOLD defect-2 fix): the
    # Frechet bounds must be COMPUTED from the carried per-rung powers
    # (1 - (0.1957+0.1942+0.1999) = 0.4102; min = 0.8001) and the
    # joint-dependence sim block must be carried through.
    inter = a["power_scope"]["intersection_all_three"]
    check(inter["not_separately_powered"] is True,
          "mock A: intersection not flagged not_separately_powered")
    check(inter["frechet_bounds_from_marginals"] == [0.4102, 0.8001],
          "mock A: Frechet bounds wrong: %s"
          % inter["frechet_bounds_from_marginals"])
    check(isinstance(inter["mc_joint_dependence_sim"], dict)
          and inter["mc_joint_dependence_sim"]["range_under_family"]
          == [0.5220, 0.7984],
          "mock A: joint-dependence sim block not carried: %s"
          % inter["mc_joint_dependence_sim"])
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

    # Mock D — the co-primary K~d2 TIE shape (ASM-2370): K-1 and K-2 fire
    # (+10 pts over b0/drng) but d2 matches K exactly in expectation, so
    # K-3 must NOT fire and pass_gate must be FALSE (ladder caps at 2) —
    # the content-not-structure datum, no longer a PASS.
    rng = random.Random(1717)
    rows_d = _mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                             "d2": 0.80, "d3-text": 0.71, "K": 0.80}, rng)
    out_d = analyze(rows_d, _mock_sidecar())
    da = out_d["analysis"]
    check(da["k1_joint_pass"] and da["k2_joint_pass"],
          "mock D: K-1/K-2 did not fire under planted lift")
    check(not da["k3_joint_pass"], "mock D: K-3 fired on a planted K~d2 tie")
    check(not da["pass_gate"], "mock D: pass_gate TRUE on a K~d2 tie — the "
          "co-primary discipline (ASM-2370) is broken")
    check(da["ladder_rung_reached"] == 2, "mock D: ladder != 2 on the tie")

    # Hardened-validation probes — each must be REJECTED fail-closed
    rows_short = [r for r in rows_a if r["item_id"] != "it-000-00"]
    expect_reject(lambda: analyze(rows_short, _mock_sidecar()),
                  "n != 1573 (dropped item)")
    # OFF-GEOMETRY probes (GPT-5.6 RUN-HOLD defect-1 fix): a 97-cluster
    # universe AT n = 1573 previously satisfied the >=-form power gate
    # (c_ge8 = 97 >= 96) and could reach pass_gate=true. It must now be
    # REJECTED (ERR_P2_ANALYSIS), never gated, never a PASS. Relabel the
    # 10 items it-000-00..09 (all arms/passes, consistently) into a NEW
    # 97th cluster: n stays 1573, c-000 keeps 7 items, c-096 gets 10.
    rows_97 = [dict(r, cluster="c-096")
               if r["item_id"].startswith("it-000-0") else r
               for r in rows_a]
    check(len({r["cluster"] for r in rows_97}) == 97
          and len({r["item_id"] for r in rows_97}) == 1573,
          "97-cluster probe malformed")
    expect_reject(lambda: analyze(rows_97, _mock_sidecar()),
                  "97 clusters at n=1573 (off-geometry, the RUN-HOLD "
                  "exploit)")
    # ...and the under-count direction: merge c-095 into c-094 (95
    # clusters, n still 1573) — equally off-geometry, equally rejected.
    rows_95 = [dict(r, cluster="c-094") if r["cluster"] == "c-095" else r
               for r in rows_a]
    check(len({r["cluster"] for r in rows_95}) == 95,
          "95-cluster probe malformed")
    expect_reject(lambda: analyze(rows_95, _mock_sidecar()),
                  "95 clusters at n=1573 (off-geometry)")
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

    # STRICT-BOOL + GUARD-COMPLETENESS probes (GPT-5.6 pre-run review-gate
    # HOLD blocker-1 fix, 2026-07-16). The reproduced spurious-PASS
    # channel: the JSON STRING "false" is truthy in Python, so
    # guard.byte_identical="false" — and string attestations on EVERY
    # manifest/template/dose flag, with guard.n_items ignored entirely —
    # previously yielded all_gates=true, pass_gate=true, an official PASS.
    # Each probe below must now fail its gate CLOSED (gate false =>
    # INSTRUMENT-INVALID/INCOMPLETE at verdict time, never a truthy PASS);
    # mock A above asserts the valid all-true fixture still PASSES.
    def probe_gate(what, gate, mutate):
        s = _mock_sidecar()
        mutate(s)
        g = analyze(rows_a, s)["gates"]
        check(g[gate] is False,
              "strict-bool/guard probe %r left %s TRUE — the spurious-PASS "
              "channel is OPEN" % (what, gate))
        check(not all(g.values()),
              "strict-bool/guard probe %r: all_gates still true" % (what,))

    def _set(path, val):
        def m(s):
            node = s
            for p in path[:-1]:
                node = node[p]
            node[path[-1]] = val
        return m

    probe_gate('guard.byte_identical="false" (string)',
               "off_concept_guard_valid",
               _set(("guard", "byte_identical"), "false"))
    probe_gate('guard.byte_identical="true" (string, not JSON bool)',
               "off_concept_guard_valid",
               _set(("guard", "byte_identical"), "true"))
    probe_gate("guard.byte_identical=1 (int)",
               "off_concept_guard_valid",
               _set(("guard", "byte_identical"), 1))
    probe_gate("guard.n_items=0 (incomplete instrument)",
               "off_concept_guard_valid", _set(("guard", "n_items"), 0))
    probe_gate("guard.n_items=59 != registered 60",
               "off_concept_guard_valid", _set(("guard", "n_items"), 59))
    expect_reject(lambda: analyze(rows_a, (lambda s: (
        s["guard"].pop("n_items"), s)[1])(_mock_sidecar())),
        "guard.n_items missing (mandatory field — structural, "
        "round-3 default-deny)")
    probe_gate('guard.n_items="60" (string)',
               "off_concept_guard_valid", _set(("guard", "n_items"), "60"))

    def all_string_false(s):
        for k in s["manifest"]:
            s["manifest"][k] = "false"
        for k in s["template"]:
            s["template"][k] = "false"
        s["dose"]["derangement_no_fixed_point"] = "false"
        s["dose"]["norm_matched_within_tol"] = "false"
        s["guard"]["byte_identical"] = "false"
        s["guard"]["n_items"] = 0
    s_all = _mock_sidecar()
    all_string_false(s_all)
    g_all = analyze(rows_a, s_all)["gates"]
    for gate in ("freeze_manifest_valid", "scoring_template_valid",
                 "dose_exactness_valid", "off_concept_guard_valid"):
        check(g_all[gate] is False,
              "every-attestation-'false' probe left %s TRUE" % gate)
    check(not all(g_all.values()),
          "every-attestation-'false' probe: all_gates still true — the "
          "reviewer's reproduced spurious-PASS path is OPEN")
    probe_gate('manifest.entry6_committed="false" (string)',
               "freeze_manifest_valid",
               _set(("manifest", "entry6_committed"), "false"))
    probe_gate("manifest.pre_spend_committed=1 (int)",
               "freeze_manifest_valid",
               _set(("manifest", "pre_spend_committed"), 1))
    probe_gate("manifest.entry5_committed=None (null)",
               "freeze_manifest_valid",
               _set(("manifest", "entry5_committed"), None))
    probe_gate('template.labels_single_token="false" (string)',
               "scoring_template_valid",
               _set(("template", "labels_single_token"), "false"))
    probe_gate('dose.derangement_no_fixed_point="false" (string)',
               "dose_exactness_valid",
               _set(("dose", "derangement_no_fixed_point"), "false"))
    probe_gate('dose.norm_matched_within_tol="true" (string)',
               "dose_exactness_valid",
               _set(("dose", "norm_matched_within_tol"), "true"))
    side_repstr = _mock_sidecar()
    side_repstr["replace"]["ran"] = "false"
    expect_reject(lambda: analyze(rows_a, side_repstr),
                  'replace.ran="false" (string; strict-bool shape defect)')

    # ---- DEFAULT-DENY sweep (HOLD round-3 fix, 2026-07-16): EVERY
    # mandatory block and EVERY validity flag probed at missing / null /
    # int / string, each proving fail-closed to NON-PASS. Two channels:
    # structural defects (block missing/non-object, mandatory field
    # missing, replace.ran non-bool, off-registered power/cost/carriers)
    # REJECT fail-closed (ERR_P2_ANALYSIS — no verdict producible);
    # present-but-non-bool/false attestation VALUES fail their gates
    # CLOSED (INSTRUMENT-INVALID). Mock A above proves the all-true/
    # all-present fixture still PASSES.
    n_struct, n_gate = 0, 0

    def probe_struct(what, mutate):
        nonlocal n_struct
        s = _mock_sidecar()
        mutate(s)
        expect_reject(lambda: analyze(rows_a, s), what)
        n_struct += 1

    # (a) FULL-DEPTH schema sweep (HOLD round-4 fix, 2026-07-16): walk the
    # declarative kot-f1k-record/1 sidecar schema itself and prove, at
    # EVERY depth: every required key popped => reject; every nested block
    # replaced by null/int/string => reject; an unknown key injected into
    # EVERY object and typed-map node => reject. This is the executable
    # form of "required + additionalProperties:false at every depth" —
    # derived from the schema, so any future schema extension is swept
    # automatically (no hand-maintained probe list to fall behind).
    req_paths, obj_paths, map_paths = [], [], []

    def _walk(node, path):
        if node["kind"] == "object":
            obj_paths.append(path)
            for k, sub in sorted(node["required"].items()):
                req_paths.append(path + (k,))
                _walk(sub, path + (k,))
            for k, sub in sorted(node["optional"].items()):
                _walk(sub, path + (k,))
        elif node["kind"] == "map":
            map_paths.append(path)
    _walk(SIDECAR_SCHEMA, ())

    def _pop(path):
        def m(s):
            node = s
            for p in path[:-1]:
                node = node[p]
            node.pop(path[-1])
        return m

    for path in req_paths:
        probe_struct("required %s missing" % ".".join(path), _pop(path))
    for path in obj_paths:
        label = ".".join(path) or "<sidecar top level>"
        if path:
            for lab, val in (("null", None), ("int", 7),
                             ("string", "true")):
                probe_struct("block %s = %s (non-object)" % (label, lab),
                             _set(path, val))
        probe_struct("unknown key inside %s" % label,
                     _set(path + ("__not_registered__",), 1))
    for path in map_paths:
        probe_struct("unknown key inside typed map %s" % ".".join(path),
                     _set(path + ("__not_registered__",), 1.0))
    # (d) every strict-bool VALIDITY FLAG: null / int / string(false) /
    # string(true) => its gate fails CLOSED (INSTRUMENT-INVALID path)
    flag_gates = (
        [(("manifest", k), "freeze_manifest_valid")
         for k in sorted(SIDECAR_SCHEMA["required"]["manifest"]["required"])]
        + [(("guard", "byte_identical"), "off_concept_guard_valid")]
        + [(("template", k), "scoring_template_valid")
           for k in sorted(SIDECAR_SCHEMA["required"]["template"]["required"])]
        + [(("dose", "derangement_no_fixed_point"), "dose_exactness_valid"),
           (("dose", "norm_matched_within_tol"), "dose_exactness_valid")])
    for path, gate in flag_gates:
        for label, val in (("null", None), ("int", 1),
                           ('string "false"', "false"),
                           ('string "true"', "true")):
            probe_gate("%s = %s" % (".".join(path), label), gate,
                       _set(path, val))
            n_gate += 1
    # dose.r_seeds: typed list-equality — null/int/string fail the gate
    for label, val in (("null", None), ("int", 101),
                       ("string", "101,102,103")):
        probe_gate("dose.r_seeds = %s" % label, "dose_exactness_valid",
                   _set(("dose", "r_seeds"), val))
        n_gate += 1
    # (e) replace.ran + inference fields: null / int / string => reject
    for label, val in (("null", None), ("int", 1), ("string", "true")):
        probe_struct("replace.ran = %s" % label,
                     _set(("replace", "ran"), val))
        probe_struct("inference.dev_sign_symmetry_pass = %s" % label,
                     _set(("inference", "dev_sign_symmetry_pass"), val))
        probe_struct("inference.method = %s" % label,
                     _set(("inference", "method"), val))
    # (f) power block pinned EXACTLY to the registered frozen values —
    # round-4 extends the pin to the FULL mc_exact_power interior
    # (round-3b item 2) and the EXACT ASM-2376 mc_intersection content
    # (round-3b item 3)
    probe_struct("power.mc_exact_power.joint_power scalar 0.80 "
                 "(superseded form)",
                 _set(("power", "mc_exact_power", "joint_power"), 0.80))
    probe_struct("power marginals 0.9/0.9/0.9 (arbitrary, != ASM-2371)",
                 _set(("power", "mc_exact_power", "joint_power"),
                      {"K-1": 0.9, "K-2": 0.9, "K-3": 0.9}))
    probe_struct("power K-3 marginal missing",
                 _set(("power", "mc_exact_power", "joint_power"),
                      {"K-1": 0.8043, "K-2": 0.8058}))
    probe_struct("power.mc_exact_power.mu_star = 4.10 (!= frozen 4.09)",
                 _set(("power", "mc_exact_power", "mu_star"), 4.10))
    probe_struct("power.mc_exact_power.n_sim = 100 (!= frozen 10000)",
                 _set(("power", "mc_exact_power", "n_sim"), 100))
    probe_struct("power.mc_exact_power.seed = 42 (!= registered 20260713)",
                 _set(("power", "mc_exact_power", "seed"), 42))
    probe_struct('power.mc_exact_power.pass = "true" (string)',
                 _set(("power", "mc_exact_power", "pass"), "true"))
    probe_struct("power.mc_exact_power.pass = false (incoherent with the "
                 "frozen >=0.80 table)",
                 _set(("power", "mc_exact_power", "pass"), False))
    probe_struct("power.mc_exact_power.pass = 1 (int, not JSON bool)",
                 _set(("power", "mc_exact_power", "pass"), 1))
    probe_struct("power.mc_intersection = {} (empty — ASM-2376 block "
                 "stranded)", _set(("power", "mc_intersection"), {}))
    probe_struct('power.mc_intersection = {"bogus": 1} (the round-3b '
                 "reproduced exploit: non-empty passed the round-3 check)",
                 _set(("power", "mc_intersection"), {"bogus": 1}))
    probe_struct("power.mc_intersection.at_lambda_0.5 = 0.62 (drifted "
                 "from the registered 0.6165)",
                 _set(("power", "mc_intersection", "at_lambda_0.5"), 0.62))
    probe_struct("power.mc_intersection.intersection_power_by_lambda "
                 "drifted in one element",
                 _set(("power", "mc_intersection",
                       "intersection_power_by_lambda"),
                      [0.5220, 0.5675, 0.6165, 0.6763, 0.80]))
    probe_struct("power.mc_intersection.seed = 1 (!= registered)",
                 _set(("power", "mc_intersection", "seed"), 1))
    probe_struct("power.mc_intersection.mc_se_max = 0.006 (> registered "
                 "MC-SE ceiling 0.005)",
                 _set(("power", "mc_intersection", "mc_se_max"), 0.006))
    probe_struct("power.mc_intersection.source drifted",
                 _set(("power", "mc_intersection", "source"),
                      "reports/somewhere-else.json"))
    probe_struct("power.rho_u = 0.2 (off-registered)",
                 _set(("power", "rho_u"), 0.2))
    # (g) cost: typed AND ledger-coherent (round-3b item 4) — non-numeric,
    # non-integer, unbounded, or arithmetically incoherent spends are
    # never success records
    probe_struct('cost.usd_total = "0.0" (string)',
                 _set(("cost", "usd_total"), "0.0"))
    probe_struct("cost.usd_total = 155.01 (above the ASM-2374 ceiling)",
                 _set(("cost", "usd_total"), 155.01))
    probe_struct("cost.prefills = null",
                 _set(("cost", "prefills"), None))
    probe_struct("cost.prefills = 0.5 (fractional prefill count)",
                 _set(("cost", "prefills"), 0.5))
    probe_struct('cost.prefills = "12584" (string)',
                 _set(("cost", "prefills"), "12584"))
    probe_struct("cost.instance_hours = 1e308 (unbounded; > the 900 h "
                 "REG wall_clock_cap_hours)",
                 _set(("cost", "instance_hours"), 1e308))
    probe_struct("cost.usd_total = 0 with positive metered run time "
                 "(ledger-incoherent: the round-3b reproduced exploit)",
                 _set(("cost", "usd_total"), 0.0))
    probe_struct("cost.spot_rate_usd_per_hour = 0 (a free instance is "
                 "not a lawful metered rate)",
                 _set(("cost", "spot_rate_usd_per_hour"), 0))
    probe_struct("cost.instance_hours drifted from construction + "
                 "sum(phase_seconds)/3600 (400.0 clears the round-6 "
                 "scale floor, so ONLY the identity rejects it)",
                 _set(("cost", "instance_hours"), 400.0))
    probe_struct('cost.d3_text_deferred = "false" (string, not JSON bool)',
                 _set(("cost", "d3_text_deferred"), "false"))
    probe_struct('cost.expert_pinning.PIN = "0" (!= pinned "1")',
                 _set(("cost", "expert_pinning", "PIN"), "0"))
    probe_struct("cost.resume_safe_ledger = '' (empty path)",
                 _set(("cost", "resume_safe_ledger"), ""))
    probe_struct('cost.phase_seconds.test = "7200" (string seconds)',
                 _set(("cost", "phase_seconds", "test"), "7200"))
    # (g2) HOLD ROUND-5 cost-ledger COMPLETENESS probes (2026-07-16): the
    # round-4 equations ignored prefills, required no phase key, and never
    # priced construction hours — an incomplete/zero ledger validated.
    probe_struct("cost.prefills = 0 (zero metered prefills — an "
                 "under-reported ledger, round-5)",
                 _set(("cost", "prefills"), 0))
    probe_struct("cost.phase_seconds = {} (EMPTY phase map — previously "
                 "accepted: keys restricted but none required, round-5)",
                 _set(("cost", "phase_seconds"), {}))
    probe_struct("cost.phase_seconds missing 'test' (incomplete phase "
                 "map, round-5)", _pop(("cost", "phase_seconds", "test")))
    probe_struct("cost.phase_seconds.guard = 0.0 (zero-second metered "
                 "phase, round-5)",
                 _set(("cost", "phase_seconds", "guard"), 0.0))

    def _construction_unpriced(s):
        # usd_spent_prior zeroed with 71.1 metered construction hours;
        # usd_total kept IDENTITY-coherent (0 + 450.1 h * 0.28 = 126.028,
        # above the round-6 scale floor), so only the round-5
        # all-metered-work pricing floor can reject it
        s["cost"]["usd_spent_prior"] = 0.0
        s["cost"]["usd_total"] = 126.028
    probe_struct("cost.usd_spent_prior = 0 with positive "
                 "construction_instance_hours (construction hours "
                 "UNPRICED — accepted by the round-4 equations, round-5)",
                 _construction_unpriced)
    # (g3) HOLD ROUND-6 budget-honesty SCALE-FLOOR probes (2026-07-16,
    # final static review defect-2): the round-5 identities were purely
    # relative, so ledgers coherent at NEAR-ZERO scale validated. Each
    # probe below is a ledger the old code ACCEPTED; each must now be
    # REJECTED by the registered scale floors (ASM-2374 corner ~$146 /
    # 521.2 h / >= 11,011 mandatory prefills). The full-scale fixture
    # itself (mock A + the round-trip) is the positive control.
    def _ledger_all_zero(s):
        # the review's reproduced exploit VERBATIM: prefills=1, each
        # phase 1 s, rate 0.28, every total zero — run_h = 0.000833 h
        # was within HOURS_TOL of instance_hours = 0 and the expected
        # spend $0.000233 within COST_TOL_USD of usd_total = 0
        s["cost"].update({"usd_total": 0.0, "instance_hours": 0.0,
                          "prefills": 1, "usd_spent_prior": 0.0,
                          "construction_instance_hours": 0.0,
                          "phase_seconds": {"pilot": 1.0, "guard": 1.0,
                                            "test": 1.0}})
    probe_struct("all-zero/near-zero ledger (prefills=1, 1 s phases, "
                 "zero totals — identity-coherent within tolerance; the "
                 "round-6 reproduced exploit)", _ledger_all_zero)

    def _ledger_zero_dollars(s):
        # full-scale positive metered hours, zero dollars
        s["cost"].update({"usd_total": 0.0, "usd_spent_prior": 0.0})
    probe_struct("positive-hours/zero-dollars ledger (521.2 metered "
                 "hours, usd_total = 0, round-6)", _ledger_zero_dollars)

    def _ledger_10x_under(s):
        # EVERY figure coherently scaled to 1/10 of the registered
        # campaign (identities all hold; prefills > 0; construction
        # priced) — only the round-6 scale floors can reject it
        s["cost"].update({"usd_total": 14.5968, "instance_hours": 52.12,
                          "prefills": 1944, "usd_spent_prior": 1.994,
                          "construction_instance_hours": 7.11,
                          "phase_seconds": {"pilot": 51660.0,
                                            "guard": 5500.0,
                                            "test": 104876.0}})
    probe_struct("coherently 10x-under-reported ledger ($14.60 for the "
                 "1,573-item campaign — arithmetic green at 1/10 scale, "
                 "round-6)", _ledger_10x_under)
    # (h) carriers off the frozen expectation (round-3b item 5): arbitrary
    # integers rejected by the C*layers*D and exact-KAEC-size arithmetic
    probe_struct("carriers.concepts = 95 (!= frozen C = 96)",
                 _set(("carriers", "concepts"), 95))
    probe_struct('carriers.table_bytes = "big" (non-integer)',
                 _set(("carriers", "table_bytes"), "big"))
    probe_struct("carriers.params_added = 7 (arbitrary; != C*layers*D)",
                 _set(("carriers", "params_added"), 7))
    probe_struct("carriers.table_bytes = 9437184 (body-only figure; != "
                 "the exact KAEC file size 9437216)",
                 _set(("carriers", "table_bytes"), 9437184))
    probe_struct("carriers.layers = 0 (non-positive)",
                 _set(("carriers", "layers"), 0))
    probe_struct("carriers.layers = 5 incoherent with params_added for 4",
                 _set(("carriers", "layers"), 5))
    # positive control (driver --mock oracle): the stub engine's lawful
    # emission shapes must VALIDATE — the carriers bind is arithmetic
    # consistency (integer D, exact KAEC size), not the real-run 6144
    # (mock stub D = 8), and a RUN whose n_ni = 0.0 <= 1573 with a
    # positive io_saving is §R-REV4.3-coherent.
    s_stub = _mock_sidecar()
    s_stub["carriers"] = {"params_added": 96 * 1 * 8,
                          "table_bytes": 16 + 4 * 1 + 4 * (96 * 1 * 8),
                          "concepts": 96, "layers": 1}
    s_stub["replace"] = {"ran": True, "delta_r_dev": 0.0, "n_ni": 0.0,
                         "io_saving_bytes_per_gated_token": 8192.0}
    validate_sidecar(s_stub)   # must return, not exit
    # (j) replace conditional coherence (round-3b item 1): the run/defer
    # decision must agree with the sub-field values, both directions
    probe_struct("replace.ran = true with delta_r_dev null (no measured "
                 "dev delta can license a RUN)",
                 _set(("replace", "ran"), True))
    probe_struct("replace.ran = false with io_saving = 3.5 (run outcome "
                 "on a deferred arm)",
                 _set(("replace", "io_saving_bytes_per_gated_token"), 3.5))
    probe_struct('replace.delta_r_dev = "0.02" (string, not a number)',
                 _set(("replace", "delta_r_dev"), "0.02"))
    probe_struct('replace.n_ni = "812.3" (string, not a number)',
                 _set(("replace", "n_ni"), "812.3"))

    def _replace_run_overpowered(s):
        # a RUN attestation whose own NI power requirement exceeds the
        # registered n — the §R-REV4.3 rule mandates DEFER at n_NI > 1573
        s["replace"].update({"ran": True, "delta_r_dev": 0.061,
                             "n_ni": 2000.0,
                             "io_saving_bytes_per_gated_token": 8192.0})
    probe_struct("replace.ran = true with n_ni = 2000 > the registered "
                 "n = 1573 (RUN decision incoherent with §R-REV4.3)",
                 _replace_run_overpowered)

    # ---- ROW-SCHEMA probes (round-3b item 6): closed arm enum, strict-int
    # pass + per-arm range, all fields required, closed keys, registered
    # tag vocabulary — each a structural rejection, never coerced/ignored.
    n_rows_probes = 0

    def probe_rows(what, mutate_rows):
        nonlocal n_rows_probes
        rows = [dict(r) for r in rows_a]
        mutate_rows(rows)
        expect_reject(lambda: analyze(rows, _mock_sidecar()), what)
        n_rows_probes += 1

    probe_rows('arm "z9-unknown" row (closed arm enum: an UNKNOWN-ARM row '
               "was previously ignored silently)",
               lambda rows: rows.append(dict(rows[0], arm="z9-unknown")))
    probe_rows('pass = "0" (string; the prior int() coercion path is '
               "REMOVED)", lambda rows: rows[0].update({"pass": "0"}))
    probe_rows("pass = 1 on a single-pass arm (b0)",
               lambda rows: rows[0].update({"pass": 1}))
    probe_rows("pass = 0 on d1-drng (outside the registered 1..3)",
               lambda rows: next(r for r in rows
                                 if r["arm"] == "d1-drng")
               .update({"pass": 0}))
    probe_rows("pass = 4 on d1-drng (outside the registered 1..3)",
               lambda rows: next(r for r in rows
                                 if r["arm"] == "d1-drng")
               .update({"pass": 4}))
    probe_rows("gold_label missing (required row field)",
               lambda rows: rows[0].pop("gold_label"))
    probe_rows("tags missing (required row field)",
               lambda rows: rows[0].pop("tags"))
    probe_rows('unknown row key "raw" (closed row key set)',
               lambda rows: rows[0].update({"raw": "leak"}))
    probe_rows('tags = ["bogus-tag"] (outside the registered vocabulary)',
               lambda rows: rows[0].update({"tags": ["bogus-tag"]}))
    probe_rows("correct = true (JSON bool, not the strict 0/1)",
               lambda rows: rows[0].update({"correct": True}))
    probe_rows("item_id = 7 (non-string)",
               lambda rows: rows[0].update({"item_id": 7}))

    # Pinned-file round-trip (the REAL verdict-gen stdin seam) — round-4:
    # a FULL kot-log/1 record line, validated against RECORD_SCHEMA with
    # declared-vs-actual rows-count coherence, plus record-level probes.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rp = Path(td) / "rows.jsonl"
        sp = Path(td) / "sidecar.json"
        rp.write_text("\n".join(json.dumps(r) for r in rows_a) + "\n",
                      encoding="utf-8")
        sp.write_text(json.dumps(_mock_sidecar()), encoding="utf-8")
        arts = [{"path": str(rp), "sha256": sha256_bytes(rp.read_bytes()),
                 "role": "rows"},
                {"path": str(sp), "sha256": sha256_bytes(sp.read_bytes()),
                 "role": "sidecar"}]

        def _full_record(**over):
            rec = {"schema_version": "kot-log/1", "seq": 0,
                   "prev_sha256": "0" * 64,
                   "ts": "2026-07-16T00:00:00Z", "experiment": "f1k",
                   "event": "run", "phase": "final", "exit": "ok",
                   "runner": "runner-1", "prereg_hash": "f" * 64,
                   "config": {"protocol": "f1k-main-campaign",
                              "engine": "colibri",
                              "n_test_items": N_REGISTERED,
                              "r_drng_passes": R_DRNG},
                   "metrics": {"rows_emitted": len(rows_a),
                               "n_test_items": N_REGISTERED},
                   "artifacts": arts}
            rec.update(over)
            return rec

        old = sys.stdin

        def _stdin_run(recs):
            sys.stdin = io.StringIO("".join(json.dumps(r) + "\n"
                                            for r in recs))
            try:
                return load_from_stdin()
            finally:
                sys.stdin = old

        rows2, side2 = _stdin_run([_full_record()])
        out2 = analyze(rows2, side2)
        check(out2 == out_a, "pin round-trip output differs from in-memory")

        n_rec_probes = 0

        def probe_record(what, rec):
            nonlocal n_rec_probes
            expect_reject(lambda: _stdin_run([rec]), what)
            n_rec_probes += 1

        # the superseded artifacts-as-DICT form must be REJECTED (it never
        # conformed to kot-log/1; HOLD round-3 seam fix)
        probe_record("superseded artifacts-as-dict run record",
                     {"event": "run", "phase": "final", "exit": "ok",
                      "artifacts": {"rows_path": str(rp),
                                    "rows_sha256": arts[0]["sha256"],
                                    "sidecar_path": str(sp),
                                    "sidecar_sha256": arts[1]["sha256"]}})
        # a record lacking the role:"sidecar" pin (bare D10 rows-only
        # shape) must be REJECTED — the paired convention is mandatory
        probe_record("run record without a role:'sidecar' artifacts entry",
                     _full_record(artifacts=[arts[0]]))
        # round-4 RECORD_SCHEMA probes (round-3b item 6, record side)
        probe_record("metrics.rows_emitted != rows actually pinned "
                     "(declared/actual count coherence)",
                     _full_record(metrics={"rows_emitted": len(rows_a) - 1,
                                           "n_test_items": N_REGISTERED}))
        probe_record("config.n_test_items = 1440 (superseded declared n)",
                     _full_record(config={"protocol": "f1k-main-campaign",
                                          "engine": "colibri",
                                          "n_test_items": 1440,
                                          "r_drng_passes": R_DRNG}))
        probe_record("unknown config key (closed record config)",
                     _full_record(config={"protocol": "f1k-main-campaign",
                                          "engine": "colibri",
                                          "n_test_items": N_REGISTERED,
                                          "r_drng_passes": R_DRNG,
                                          "extra_knob": 1}))
        rec_nometrics = _full_record()
        del rec_nometrics["metrics"]
        probe_record("metrics block missing from the run record",
                     rec_nometrics)
        probe_record("non-pseudonymous runner identity",
                     _full_record(runner="jsmith"))
        probe_record("unknown top-level record key (default-deny)",
                     _full_record(bonus_field="looks official"))
        probe_record("a third artifacts entry (closed 2-entry pair)",
                     _full_record(artifacts=arts + [
                         {"path": str(rp), "sha256": arts[0]["sha256"],
                          "role": "rows"}]))
        probe_record("non-final phase line on stdin (strict seam: never "
                     "silently skipped)", _full_record(phase="exploratory"))
        # HOLD ROUND-5 record probes (2026-07-16): (i) an UNSTAMPED
        # record — each of the six kot-log/1 chain fields popped in turn
        # (round-4 typed them only WHEN PRESENT, so a record that never
        # went through log-append validated) — must REJECT;
        for cf in ("schema_version", "seq", "prev_sha256", "ts",
                   "experiment", "runner"):
            rec_uc = _full_record()
            del rec_uc[cf]
            probe_record("chain field %r missing (UNSTAMPED record — "
                         "provenance is validity-bearing, round-5)" % cf,
                         rec_uc)
        # (ii) pins_observed — round-4 left it an open-key map of "any"
        # values; the reviewer's exploit and its neighbours must REJECT
        probe_record('pins_observed={"arbitrary":{"bogus":1}} (the '
                     "round-4 open-map exploit)",
                     _full_record(pins_observed={"arbitrary":
                                                 {"bogus": 1}}))
        probe_record("pins_observed key off the pin-name pattern",
                     _full_record(pins_observed={"Not A Pin!":
                                                 {"observed": "a" * 64}}))
        probe_record("pins_observed .observed not a sha256",
                     _full_record(pins_observed={"analysis_script":
                                                 {"observed": "xyz"}}))
        # HOLD ROUND-6 record probes (2026-07-16, final static review
        # defect-1): trailing-newline bypass. Python's $ matches BEFORE a
        # terminal newline, so under re.match(...$) each value below
        # satisfied its declared "strict" pattern and VALIDATED. Every
        # validity/provenance regex is now fullmatch + \Z — each must
        # REJECT (the clean-value positive controls above/below prove
        # valid records still pass byte-identically).
        probe_record('runner = "runner-1\\n" (trailing newline, round-6)',
                     _full_record(runner="runner-1\n"))
        probe_record('ts = "...Z\\n" (trailing newline, round-6)',
                     _full_record(ts="2026-07-16T00:00:00Z\n"))
        probe_record("prev_sha256 = 64-hex + '\\n' (trailing newline, "
                     "round-6)", _full_record(prev_sha256="0" * 64 + "\n"))
        probe_record("prereg_hash = 64-hex + '\\n' (trailing newline, "
                     "round-6)", _full_record(prereg_hash="f" * 64 + "\n"))
        probe_record("pins_observed KEY with a trailing newline (round-6)",
                     _full_record(pins_observed={"analysis_script\n":
                                                 {"observed": "a" * 64}}))
        probe_record("pins_observed .observed = 64-hex + '\\n' (trailing "
                     "newline, round-6)",
                     _full_record(pins_observed={"analysis_script":
                                                 {"observed":
                                                  "a" * 64 + "\n"}}))
        probe_record('runner = "runner-1\\nrunner-2" (embedded newline, '
                     "round-6)", _full_record(runner="runner-1\nrunner-2"))
        # positive control: a LAWFULLY-typed pin observation still loads
        # and the analysis output is byte-identical
        rows5, side5 = _stdin_run([_full_record(
            pins_observed={"analysis_script": {"observed": "a" * 64,
                                               "expected": "a" * 64}})])
        check(analyze(rows5, side5) == out_a,
              "round-5 typed pins_observed positive control drifted the "
              "output")

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
          "ladder rung %d, all three CO-PRIMARY rungs fire) on the "
          "sign-flip branch AND on the implemented BCa fallback branch, "
          "K~d2 tie shape pass_gate-FALSE (ladder 2, ASM-2370), "
          "planted-null TOST NULL-bound, executable intersection "
          "disclosure (Frechet [0.4102, 0.8001] computed, ASM-2376 sim "
          "block carried), 9/9 hardened rejections fail-closed (n!=1573, "
          "97-cluster off-geometry, 95-cluster off-geometry, superset, "
          "non-binary, mutable ceiling, incoherent/missing inference, "
          "string replace.ran), 13/13 STRICT-BOOL + GUARD-COMPLETENESS "
          "gate probes fail-closed (HOLD blocker-1 fix 2026-07-16: "
          "string-'false'/'true'/int/null attestations on manifest/guard/"
          "template/dose REJECTED at their gates; guard.n_items 0 / 59 / "
          "missing / string REJECTED against the registered 60; the "
          "every-attestation-'false' reproduced spurious-PASS campaign "
          "now INSTRUMENT-INVALID; the all-true fixture still PASSES), "
          "kot-f1k-record/1 FULL-DEPTH DEFAULT-DENY sweep (HOLD round-4 "
          "fix 2026-07-16, superseding the round-3 top-level sweep) %d "
          "structural rejections (EVERY required key at EVERY depth "
          "popped; EVERY nested block x null/int/string; an unknown key "
          "injected at EVERY object/map node — all derived from the "
          "declarative schema itself; replace sub-fields + run/defer "
          "coherence; the FULL mc_exact_power interior pinned to the "
          "registered ASM-2371/§R-REV5 values; mc_intersection == the "
          "registered ASM-2376 content EXACTLY incl. the {'bogus':1} "
          "round-3b exploit; cost typed + ledger-coherent within the $155 "
          "ASM-2374 ceiling and the 900 h wall-clock cap incl. the "
          "usd_total=0-with-positive-hours exploit; carriers at the exact "
          "C*layers*D / KAEC-size expectation; HOLD ROUND-5 residual-gap "
          "closure 2026-07-16: the open-ended 'any' schema kind REMOVED — "
          "pins_observed now a typed CLOSED map, the {'arbitrary':"
          "{'bogus':1}} exploit + off-pattern keys + non-sha256 observed "
          "REJECTED with a typed positive control byte-identical; all six "
          "kot-log/1 chain fields REQUIRED — every UNSTAMPED-record pop "
          "REJECTED; cost-ledger completeness — prefills>=1, the COMPLETE "
          "positive pilot/guard/test phase map, and construction hours "
          "PRICED via the usd_spent_prior floor, the empty-phase-map / "
          "zero-prefill / construction-unpriced ledgers each REJECTED; "
          "HOLD ROUND-6 final-static-review closure 2026-07-16: "
          "BUDGET-HONESTY SCALE FLOORS at the registered ASM-2374 "
          "campaign scale (~$146 / 521.2 h / >= 11,011 mandatory "
          "prefills; construction hours strictly positive) — the "
          "all-zero (prefills=1 / 1 s phases / $0 totals, "
          "identity-coherent within tolerance), positive-hours/"
          "zero-dollars, and coherently-10x-under-reported ledgers each "
          "REJECTED with the full-scale corner ledger the passing "
          "fixture) "
          "+ %d value-level gate "
          "probes fail-closed, %d ROW-SCHEMA rejections (closed arm enum "
          "incl. an UNKNOWN-ARM row, strict-int pass incl. string-'0' "
          "with the int() coercion path REMOVED, per-arm pass range, "
          "required fields, closed keys, registered tags, bool correct), "
          "kot-log/1 FULL-record round-trip byte-stable + %d RECORD-level "
          "rejections (superseded dict form, rows-only record, "
          "declared-vs-actual rows_emitted coherence, n_test_items pin, "
          "closed config/metrics/top-level, pseudonymous runner, 2-entry "
          "artifact pair, strict-seam non-final line; ROUND-5: all six "
          "kot-log/1 chain fields popped in turn — the UNSTAMPED record "
          "rejects — and pins_observed junk/off-pattern-key/non-sha256 "
          "rejected with the typed positive control byte-identical; "
          "ROUND-6: every validity/provenance regex fullmatch+\\Z, never "
          "$ — trailing-newline runner/ts/prev_sha256/prereg_hash/"
          "pins_observed-key/pins_observed-sha and an embedded-newline "
          "runner each REJECTED, clean values still loading "
          "byte-identically), %d "
          "output fields "
          "present on both branches at the EXACT REVISION-6 geometry "
          "(C=96, n=1573)."
          % (out_a["analysis"]["ladder_rung_reached"], n_struct, n_gate,
             n_rows_probes, n_rec_probes, len(OUTPUT_FIELDS)))
    return 0


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    rows, side = load_from_stdin()
    out = analyze(rows, side)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
