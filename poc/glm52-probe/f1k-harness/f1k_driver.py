#!/usr/bin/env python3
"""f1k_driver.py — F1-K SINGLE-INSTANCE run driver (colibri C engine + KaE patch).

BUILD + MOCK-VALIDATE pass only: this file implements the FROZEN F1-K protocol
exactly; it launches no instance, downloads no model, writes no registry entry,
takes no git action, and spends $0. The coordinator owns the spot-instance
launch, sharding orchestration, collection, and go/no-go, and reviews this
driver against the frozen protocol before any real run.

REVISION-2 of this driver — the codex correctness review
(poc/gpt56-review/f1k-driver/out/last-message.json, verdict FIX-FIRST)
found launch-blocking deviations from the frozen protocol. Every blocker is
fixed in this file; each fix site carries a [FIX-n] anchor comment (n = the
blocker number in the coordinator instruction) and the --mock self-check
prints the realized line number of every anchor:

  [FIX-1] SCORER stdout parsed ROBUSTLY: the real colibri prints startup
          banners to stdout BEFORE the KAE_SCORE results (patch hunks at
          glm.c printf "== GLM C engine ..." / "loaded in ..."); result
          lines are now LOCATED by strict shape validation against the
          item's label-token ids (pred index in range, pred token == the
          label id it indexes, exactly K logits) — never "line 1". The
          frozen tie information + all K label logits are LOGGED per item
          (label-logits.<phase>.jsonl), and the engine's lowest-index
          tie-break is re-asserted from the logged logits.
  [FIX-2] KaE FAIL-CLOSED: engine stderr is CAPTURED per invocation; every
          KAE=1 invocation requires the POSITIVE "[KAE] ADD-path armed"
          signal with matching (concepts, splice layers, g) BEFORE the
          first scored item is accepted, and any KaE-disabled marker
          aborts the run — a spliced arm can never silently score as b0.
          Span concept-ids are pre-validated against the carrier header so
          kae_bind_spans() cannot fail silently (the engine already emits
          "ERR item" for out-of-range ids, which is fatal here; malloc-
          failure is the only residual bind path and it leaves spans empty
          for THAT item only — excluded by the pre-validation + the armed
          signal + the off-concept guard's byte-identity instrument).
  [FIX-3] Conditional REPLACE per the frozen gate (§R-REV4.3/ASM-2124 +
          REG sec-replace-ni): dev delta_R = REPLACE-vs-ADD discordance is
          MEASURED on dev-96 at the frozen (L,g) whenever the engine
          supports REPLACE; n_NI = delta_R*DEFF/SE_NI^2; RUN iff
          n_NI <= n_max (= N_TEST, 1573 since [R6-1]); a stubbed REPLACE
          engine (byte-identical to b0) is
          DETECTED and fails closed; the decision drives EXECUTION (guard
          + test schedule the REPLACE pass; sidecar replace.ran is real).
  [FIX-4] The affordability d3-text deferral (§R6 step 3) is honored in
          EXECUTION: addendum-7 records d3_text_deferred and the test
          schedule derives from it — never projection-only.
  [FIX-5] Expert pinning ENFORCED + RECORDED (as corrected by the
          ASM-2513 PIN=<stats-file> fix, 2026-07-18): engine env must
          carry PIN=<bring-up-derived hot-expert stats-file> and
          PIN_GB>0 (frozen semantics glm52-followup-experiment.md
          §7.1:638-639; cost lever 2 glm52-f1k-cost-reduction.md /
          ASM-2205); the stats-file is validated + content-hashed FROM
          BYTES, engine arming is verified from the pin banner/counters
          (never trusted from the flag), and hash + PIN_GB + realized
          experts_pinned enter the resume-safe ledger, the sidecar, and
          the [R10-4] resume-auth binding. The legacy literal PIN="1"
          is REFUSED (it was never engine semantics and could only emit
          a false pinning attestation).
  [FIX-6] PILOT: dev-96 is scored AFTER the (L,g) freeze and all dev
          inputs (delta-hat, sign-symmetry, placebo, delta_R) come from
          dev-96; frozen g = MULTIPLIER x MEAN NATIVE EXPERT WEIGHT
          (§2.3 grid); FULL panel validation (seed 11, d0 seed 7, {2,1,1}
          family partition, carrier identities vs the arm tables, per-
          (c,l) norm matching, derangement reconstruction); the committed
          (5)/(7)/(6) flags + pilot-gate artifacts are ENFORCED before any
          test spend; the pilot dev subset is the freeze-manifest (A)
          committed id list, not a driver-invented rule.
  [FIX-7] FROZEN CONSTANTS exact: z0.80 = 0.842 (design verbatim);
          n = N_TEST EXACTLY (1573 since [R6-1]; never
          min(cap, ceil(n_req))); the power block
          is fully validated (rho_u == 0.10, N_sim == 10000, mu* == 4.09,
          seed, MC pass threshold + coherence); the cost/elapsed ledger is
          RESUME-SAFE (cost-ledger.json accumulates across invocations and
          phases, includes pilot + construction, survives interruption).

REVISION-3 of this driver — the GPT-5.6 pre-run review-gate (post
reset-refreeze, 2026-07-16) returned HOLD blocker 2: the driver was still
on the SUPERSEDED pre-REVISION-6 geometry and could not run the frozen
96/1573 record. Every alignment site carries an [R6-n] anchor:

  [R6-1] N_TEST = 1573 EXACT (REG design.n_planned.n_test_items/n_max,
         ASM-2369; the superseded 1440 cap is REJECTED by the pinned
         analysis).
  [R6-2] EQUALITY-form power gate: n_clusters == 96 AND
         clusters-with-m>=8 == 96 AND n == 1573 — byte-matches
         analysis/f1k.py's /gates/power_gate_valid; the cached >=-form
         (C >= 65) gate is REMOVED (a 97-cluster universe must FAIL here
         exactly as the analysis hard-rejects it).
  [R6-3] USD_CAP = $155 (REG budget.usd_cap, ASM-2374, successor of the
         $149 ceiling) + the worst-case $ RECOMPUTED for 96/1573 at the
         ASM-2205 pessimistic corner (WORST_CASE block below). [FREEZE-A
         2026-07-16] envelopes amended at the freeze-(A) completion
         refreeze: construction = 4,608 dump passes EXACT (96x16x3 — the
         3,072 figure under-counted d2's with-dictionary passes), pilot
         <= 2,112 DETERMINISTIC (grid 1,728 + dev-96 3x96 + conditional
         REPLACE dev pass 96; supersedes the ~6,200 planning bound):
         mandatory campaign $129.40 <= $155; +REPLACE $139.59 <= $155 at
         the corner — REPLACE STILL runs ONLY if its §R-REV4.3 NI gate
         says RUN and the measured (7) projection keeps the ledger <= cap
         (the pre-registered ASM-2374 resolution — never a silent raise).
  [R6-4] power.mc_exact_power.joint_power is the REVISION-6 PER-RUNG dict
         {"K-1","K-2","K-3"} (each numeric in [0,1]; coherence
         pass == all three >= 0.80, the ASM-2371 per-rung criterion);
         power.mc_intersection (the ASM-2376 joint-dependence sim block)
         is REQUIRED and carried verbatim into the sidecar. The superseded
         scalar joint_power is REJECTED. DELTA_R_RUN_MAX re-derived
         (~0.0397 at n_max = 1573).
  [R6-5] mock fixtures realize the FROZEN geometry (96 clusters, 37x17 +
         59x16 = 1573 test items; dev 96; guard 60) and the mock campaign
         round-trips the FIXED strict-bool analysis end-to-end.

REVISION-4 of this driver — the GPT-5.6 round-2 re-review (2026-07-16)
returned HOLD: attestation laundering, an unpinned power block, no
realized-cost stop, and a structurally impossible official ingestion seam.
Every fix site carries an [R3-*] anchor:

  [R3-ATTEST] NO bool() coercion anywhere on the attestation surface: the
          driver previously emitted bool(<config value>) so an upstream
          JSON STRING "false" (truthy) became an emitted `true` and the
          analysis PASSed. Emission goes through attest_bool (a non-bool
          FAILS the run, ERR_F1K_ATTEST — `true` is never fabricated);
          every gate/report READ uses strict `is True`.
  [R3-POWER] the sidecar power block is pinned EXACTLY to the frozen
          registered values: ASM-2371 marginals 0.8043/0.8058/0.8001 and
          the ASM-2376 intersection sim block (non-empty, values pinned);
          any deviation fails closed (the pinned analysis independently
          enforces the same equality).
  [R3-COST] realized-ledger ceiling ENFORCED (REG budget.usd_cap $155,
          ASM-2374) at ledger init/resume, at EVERY accumulation, and at
          sidecar emission — exceeding it STOPS the run fail-closed with
          NO success record (previously only the pre-test projection was
          checked).
  [R3-SEAM] the run record is kot-log/1-CONFORMANT (artifacts ARRAY with
          the D10-paired role:"rows" + role:"sidecar" entries,
          prereg_hash, config/metrics) and the mock drives the REAL
          official path — log-append -> verdict-gen -> pinned analysis ->
          verdict — in a sandboxed repo root, on BOTH a PASS-eligible
          fixture (PASS-PENDING-AUDIT) and an attacker-consistent
          tampered fixture (INSTRUMENT-INVALID). The previous mock's
          direct analysis call is retained only as a supplementary shape
          check and labeled as such.

  INPUT SEAMS (review §1/§2/§3): the eval manifest, carrier tables, and
  trigger map are verified against their kot-corpus-hash/1 pins and the
  frozen record's pins.corpus_hashes; guard/dev/test id-list hashes are
  verified against the freeze-manifest (A) commits; eval/carrier paths
  must be CONTAINED in the pinned corpus dirs. The real f1k-eval-v1 /
  f1k-carriers-v1 / f1k-trigger-map-v1 corpora are ABSENT
  (PINNED-AT-INPUTS) and are a SEPARATE build: a real (non-mock) run
  FAILS CLOSED until the ops amendment pins them — this driver NEVER
  fabricates them (mock fixtures are generated only under --mock and are
  labeled MOCK throughout).

FROZEN PROTOCOL SOURCES (every constant below cites one of these; there are
NO invented thresholds):
  [REG]   registry/experiments/f1k.json          (frozen-review-clean record)
  [DES]   docs/next/design/glm52-followup-experiment.md
          §2 (F1-K) as amended by §R (REVISION-1) .. §R-REV5 (REVISION-5);
          the latest revision governs on conflict
  [ANA]   analysis/f1k.py                        (pinned analysis; this
          driver's rows/sidecar output MUST match what it reads)
  [COST]  docs/next/design/glm52-f1k-cost-reduction.md (spot i4i.2xlarge +
          expert-pinning + R=3 levers; ASM-2205) — the CEILING itself is
          now the REVISION-6 $155 (REG budget.usd_cap, ASM-2374,
          successor of the doc's $149) [R6-3]
  [PATCH] poc/glm52-probe/kae-patch-draft/ (KaE ADD splice + §R1.1 scorer:
          KAE / KAE_CARRIER / KAE_G / KAE_MODE / KAE_SCORE interface)
  [CACHE] docs/next/design/glm52-expert-cache.md (FREEZE-READY; optional
          XCACHE seam — pass-through only here; the pilot may run cache-off;
          the off-concept guard ALWAYS runs cache-off, ASM-2306)

WHAT THE DRIVER DOES
  --phase pilot : the (L,g) selection over the 4-member FAMILY-BLIND carrier
                  panel on the freeze-committed 48-item stratified dev subset
                  (selection statistic = EQUAL FAMILY-LEVEL weight mean
                  [DES §R-REV3.2 / ASM-2113], tie-break fewer spliced layers
                  then lower g [DES §R4]); then the POST-FREEZE dev-96 passes
                  (b0, K, d0-family, and REPLACE when the engine supports it)
                  that yield delta-hat, the sign-symmetry inputs, the placebo
                  alarm, and the REPLACE-vs-ADD delta_R; then the bring-up
                  affordability / power / placebo / semantics gates; emits the
                  addendum-(5) and addendum-(7) pure-function artifacts and
                  the addendum-(6) INPUT record [DES §R-REV2.4/§R-REV4.2].
  --phase guard : the 60-item off-concept byte-identity guard [DES §2.5]:
                  every spliced arm's engine output (REPLACE included when
                  scheduled) must be byte-identical to b0 (gate never fires);
                  any mismatch VOIDS [REG kill_criterion_verbatim]. XCACHE
                  forced off [CACHE ASM-2306].
  --phase test  : the main campaign: items x arms x passes, ONE
                  candidate-independent label-logit prefill per unit
                  [DES §R1.1], per-item checkpoint/resume (spot interruption
                  just resumes [COST]), rows + sidecar in analysis/f1k.py's
                  EXACT schema, plus the verdict-gen run-record line. Runs
                  ONLY after the (A)/(B0)/(5)/(7)/(6) commits and the pilot
                  gate artifacts are verified [DES §R-REV4.2 / ASM-2123].
  --mock        : runs the ENTIRE wiring (pilot -> guard -> test with a
                  forced interrupt + resume -> sidecar -> analysis/f1k.py
                  ingest) against the deterministic stub mock_colibri.py.
                  $0; validates schema and protocol conformance only — a
                  mock outcome is NOT a feasibility result.

Fail-closed discipline: every violated precondition raises DriverError with
an ERR_F1K_* code and exits 2; nothing falls back silently (house rule:
"No silent fallbacks; fail closed with ERR_* codes").
"""

import argparse
import array
import fcntl
import hashlib
import json
import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # repo root (kernel-of-truth/)

# ---------------------------------------------------------------------------
# FROZEN-PROTOCOL CONSTANTS — each cites its source; changing any of these is
# a protocol change requiring a new freeze, never a driver edit.
# ---------------------------------------------------------------------------
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
#   [REG pins.model_revisions.colibri-base-commit]
KAE_PATCH_SHA256 = ("11f8b45884878111480192ee086c92b22ac"
                    "aa1aaf3238b2d46c47f952e9dd9cb")
#   [REG pins.harness_manifest] — the gate-0 KaE ADD patch; the authoritative
#   pin is enforced fail-closed by bringup.sh before build/apply.

ARMS_MAIN = ("b0", "d0", "d1-drng", "d2", "d3-text", "K")
#   [REG design.independent_vars arm levels, minus conditional REPLACE;
#    REG arms_mandatory_baselines]
ARM_REPLACE = "REPLACE"
#   [REG design.independent_vars level 7: conditional, run/defer decided
#    PRE-test by the §R-REV4.3 NI power gate — see replace_gate below]
SPLICED_ARMS = ("d0", "d1-drng", "d2", "K")     # arms that arm KAE=1, mode 0
#   [DES §2.6 arm table: b0 = no splice; d3-text = prompt text, no splice;
#    REPLACE = KAE=1 with KAE_MODE=1, handled explicitly]
R_DRNG = 3
#   [REG arms_mandatory_baselines d1-drng: R = 3 passes (SSR6 degradation
#    step 1 pre-applied per maintainer reduced-cost GO #28); ANA R_DRNG]
DRNG_SEEDS = (101, 102, 103)
#   [REG design.seeds; ANA DRNG_SEEDS — dose gate fails closed on mismatch]
N_TEST = 1573
#   [R6-1] [REG design.n_planned.n_test_items / n_max = 1573 EXACT
#    (REVISION-6 powered geometry, ASM-2369: the maintainer-approved raise
#    of the SUPERSEDED 1440 cap, 2026-07-15): F1-K runs AT the cap
#    (§R-REV3.1 item 4); ANA N_REGISTERED — any other realized n REJECTED]
DEV_N = 96
#   [REG design.n_planned.dev_split_items; DES §R3.2 dev split expanded to 96]
GUARD_N = 60
#   [REG design.n_planned.off_concept_guard_items; DES §2.5 off-concept guard]
C_REGISTERED = 96
POWER_GATE_MIN_M = 8
#   [R6-2] [REG design.n_planned.power_gate (REVISION-6/RUN-HOLD equality
#    form, ASM-2369): EXACTLY 96 concept clusters, EACH with >= 8 test
#    items, at EXACTLY n = 1573 — matches ANA C_REGISTERED and the
#    equality-form /gates/power_gate_valid; SUPERSEDES the §R-REV2.2
#    C>=65 >=-form gate (ASM-2271)]
USD_CAP = 155.0
#   [R6-3] [REG budget.usd_cap = 155; ASM-2374 REVISION-6 ceiling,
#    successor of the $149 ASM-2283/ASM-2205 ceiling — see WORST_CASE_*
#    below for the recomputed 96/1573 worst-case arithmetic]
WALL_CLOCK_CAP_HOURS = 900.0
#   [REG budget wall-clock cap, ASM-2374 — the REV-B addendum-(7)
#    projection tests instance-hours against this cap too]
RESERVE_USD_ADD7 = 8.0
#   [REV-B ASM-2516; F1K-BRINGUP-GATE-FIX.md SSA2/SSB] the plan-SS8 $8
#   staging/overhead + ~5% preemption-rework reserve, charged AGAINST the
#   caps in the addendum-(7) projection (usd + 8 <= 155 AND hours + 8/rate
#   <= 900, at central AND +1SE) — the SAME reserve rule as the bring-up
#   gate (ASM-2515): ONE projection model + ONE reserve rule at BOTH
#   seams. The FULL $8 is kept even though part of the overhead is
#   already inside usd_spent_prior by pilot time [STIPULATED,
#   conservative-only].
ADD7_KAPPA_BOUNDS = (0.5, 2.0)
#   [REV-B ASM-2516, STIPULATED] admissible realized/model-predicted pilot
#   throughput ratio; outside -> the frozen gate model does not transfer
#   to the realized campaign -> ERR_F1K_AFFORD (maintainer surface).
#   Enforced only for a REAL gate artifact (the $0 mock's stub timings
#   carry no meaningful level; a mock artifact never licenses anything).
SPOT_RATE_DEFAULT = 0.28
#   [COST: $0.28/h spot i4i.2xlarge, the pessimistic corner of $0.20-0.28]
PILOT_DEV_SUBSET_N = 48
#   [REG design.n_planned.pilot: "48-item stratified dev subset"]
PILOT_KDRNG_SEED = 11
PILOT_D0_SEED = 7
#   [REG freeze_manifest A(vii): pilot-panel derangement seed 11, d0 table
#    seed 7 — disjoint from main seeds 101,102,103]
PERM_B = 10000
ALPHA = 0.05
#   [DES §R3.1: 10,000 resamples, one-sided alpha = 0.05; ANA B/ALPHA]
PERM_SEED = 20260713
#   [ANA SEED — the registered global PRNG seed; the pilot placebo check
#    reuses it with its own deterministic sub-seed string]
SE_TARGET = 0.012
#   [DES §R3.2: design target SE <= 1.2 accuracy points (fraction 0.012)]
RHO_U = 0.10
#   [DES §R-REV3.1 item 3: frozen conservative planning rho_U = 0.10]
Z80 = 0.842   # [FIX-7] EXACT design value
#   [DES §R3.2 VERBATIM: "z_0.80 = 0.842"; §R-REV2.4 entry-6 rule: delta-hat
#    at its one-sided 80%-upper-bound estimator. NOT 0.8416: the frozen
#    record fixes the 3-decimal constant and every downstream figure
#    (2.487 = 1.645 + 0.842, MDE = 3 + 0.842*SE) uses it.]
SE_NI = 0.008
#   [DES §R-REV2.1/ASM-2044: REPLACE-NI design target SE_NI <= 0.80 pts
#    (fraction 0.008); n_NI = delta_R * DEFF / SE_NI^2 = delta_R*DEFF/0.000064]
DELTA_R_RUN_MAX = 0.0397
#   [R6-4] [DES §R-REV4.3 / ASM-2124 rule AT the REVISION-6 geometry:
#    REPLACE runs only if n_NI = delta_R*DEFF/SE_NI^2 <= n_max = 1573; at
#    planned m = 1573/96 (DEFF = 1 + (m-1)*rho_U = 2.5385) that is
#    delta_R <= 1573*0.008^2/2.5385 ~= 0.0397 (was ~0.038 at the
#    superseded 1440 geometry) — the n_NI rule is PRIMARY, this figure is
#    the descriptive equivalent only]
MU_STAR_POINTS = 4.09
MC_N_SIM = 10000
MC_PASS_MIN = 0.80
MC_SEED = PERM_SEED
REGISTERED_JOINT_POWER = {"K-1": 0.8043, "K-2": 0.8058, "K-3": 0.8001}
#   [R3-POWER] the frozen ASM-2371 per-rung exact joint-power table
#   (MEASURED, seed 20260713, REVISION-6 geometry; REG
#   mc_exact_power_confirmation VERBATIM). HOLD round-3 item 5: the driver
#   previously accepted ARBITRARY marginals (0.9/0.9/0.9) and an EMPTY
#   mc_intersection {} — the power block is now pinned EXACTLY to these
#   registered values; any deviation fails closed (the pinned analysis
#   enforces the same equality independently).
REGISTERED_MC_INTERSECTION = {
    "lambda_grid": [0.0, 0.25, 0.5, 0.75, 1.0],
    "intersection_power_by_lambda": [0.5220, 0.5675, 0.6165, 0.6763,
                                     0.7984],
    "range_under_family": [0.5220, 0.7984],
    "at_lambda_0.5": 0.6165,
    "seed": PERM_SEED,
}
#   [R3-POWER] the frozen ASM-2376 shared-K joint-dependence intersection
#   sim (MEASURED; poc/f1k-askability/power_intersection_n1573.py ->
#   reports/power-intersection-n1573.json; REG n_planned assumption
#   VERBATIM). The sidecar block must carry EXACTLY these values on the
#   required keys (extra disclosure keys like mc_se_max/source permitted);
#   an empty or deviating block fails closed — never carried "verbatim"
#   into the disclosure unverified.
#   [FIX-7] [DES §R-REV5 / REG design.n_planned.mc_exact_power_confirmation:
#    frozen pre-spend Monte-Carlo of the EXACT sign-flip joint power at
#    mu* = +4.09 pts, N_sim = 10000, pass iff >= 0.80, procedure + seed =
#    freeze-manifest (A) entries]
G_MULTIPLIERS = (0.5, 1.0, 2.0)
#   [FIX-6] [DES §2.3 grid VERBATIM: "blend grid g in {0.5, 1.0, 2.0} x mean
#    native expert weight" — the grid values are MULTIPLIERS; the realized
#    KAE_G is multiplier x the bring-up-measured mean native expert weight]
CEILING_B0 = 0.95
#   [DES §2.7; ANA CEILING_B0 — echoed into the sidecar, never moved]
NORM_MATCH_RTOL = 2e-3
#   [DES §R2 reference-norm rule tolerance for the fp32-stored tables; the
#    dose gate proper re-checks from the B0 addendum metadata]
DEGRADATION_ORDER = (
    "R 5->3 (PRE-APPLIED per maintainer reduced-cost GO #28)",
    "defer REPLACE (independently gated by its own NI power gate, "
    "§R-REV4.3; affordability step per §R6)",
    "defer d3-text (K-seam question deferred, ladder rungs intact)",
    "STOP and return to the maintainer with the measured projection",
)
#   [DES §R6 pre-registered degradation order; n never cut below n_required,
#    no ladder arm (b0, d0, d1-drng, d2, K) ever dropped]

# [R6-3] WORST-CASE $ RECOMPUTED for the REVISION-6 96/1573 geometry, per
# the ASM-2374 derivation at the ASM-2205 pessimistic corner (100 s/prefill
# raw engine throughput / 1.20x expert-pinning speedup / $0.28/h spot
# i4i.2xlarge), envelopes as AMENDED at the freeze-(A) completion refreeze
# (2026-07-16 [FREEZE-A]; REG scoring_passes/budget_note riders):
#   construction = 96 x 16 x 3 = 4,608 dump passes EXACT (WITHOUT shared
#     between K and d2; the superseded 3,072 figure counted K's two
#     variants only and under-counted d2's §2.6 "same construction"
#     with-dictionary passes — build_carriers.py is the deterministic
#     counter);
#   pilot <= 2,112 DETERMINISTIC (this driver's own frozen-grid
#     arithmetic: 9 configs x 4 panel members x 48 dev = 1,728, + dev-96
#     post-freeze passes b0/K/d0 = 288, + the conditional dev-96 REPLACE
#     pass 96; supersedes the ~6,200 pre-driver planning bound).
# Mandatory campaign (no REPLACE): 12,584 main + 4,608 construction +
# 2,112 pilot + 660 guard = 19,964 prefills -> 462.1 h -> $129.40 <= the
# $155 cap. WITH the conditional REPLACE arm (+1,573): 21,537 -> 498.5 h
# -> $139.59, ALSO <= the cap at this corner — REPLACE nevertheless runs
# ONLY if its §R-REV4.3 NI gate says RUN AND the bring-up-MEASURED (7)
# projection keeps the total ledger <= $155 (the pre-registered ASM-2374
# resolution; never a silent cap raise), else DEFERRED (its registered
# modal expectation) by the §R6 step-2 degradation implemented below.
WORST_S_PER_PREFILL = 100.0 / 1.20      # ASM-2205 corner, pinning lever
WORST_PREFILLS_MAIN = 8 * N_TEST        # 12,584: b0,d0,3x d1-drng,d2,d3,K
WORST_PREFILLS_CONSTRUCTION = 4608      # EXACT [FREEZE-A: 96*16*3]
WORST_PREFILLS_PILOT = 2112             # deterministic <= [FREEZE-A]
WORST_PREFILLS_GUARD = 660              # <= bound [ASM-2374]
WORST_PREFILLS_REPLACE = N_TEST         # the conditional arm


def worst_case_usd(replace=False):
    """[R6-3] Deterministic worst-case $ at the ASM-2374 pessimistic
    corner; the mandatory-campaign figure MUST clear USD_CAP (asserted
    fail-closed in load_config) — exceeding it is a STOP-and-return, never
    a silent ceiling raise."""
    pf = (WORST_PREFILLS_MAIN + WORST_PREFILLS_CONSTRUCTION
          + WORST_PREFILLS_PILOT + WORST_PREFILLS_GUARD
          + (WORST_PREFILLS_REPLACE if replace else 0))
    return pf * WORST_S_PER_PREFILL / 3600.0 * SPOT_RATE_DEFAULT


ANALYSIS_SCRIPT = ROOT / "analysis" / "f1k.py"     # [REG pins.analysis_script]
REGISTRY_RECORD = ROOT / "registry" / "experiments" / "f1k.json"
CORPUS_NAMES = ("f1k-eval-v1", "f1k-carriers-v1", "f1k-trigger-map-v1")
#   [REG pins.corpus_hashes — all three currently PINNED-AT-INPUTS: a
#    SEPARATE build; this driver verifies, never creates]

# [R9-PROV] Carrier-construction provenance gate constants (carrier
# RE-REVIEW item 8, 2026-07-16): the driver previously checked ONLY the
# carrier-dir digest + path containment at ingest, never the construction
# report's mode / D / layers / bindings — so a mode=mock D=6144 table set
# with 8 non-pinned layers was accepted END-TO-END for what claimed to be
# a real campaign. These are the REGISTERED values the driver now enforces
# fail-closed BEFORE ingesting carriers for a REAL campaign (sources:
# build_carriers.py module docstring + the frozen record riders).
REGISTERED_SPLICE_LAYERS = list(range(3, 78))
#   the A(iv) candidate splice union: the 75 DRAFT=0-reachable MoE layers
#   of the pinned GLM-5.2 config, ENGINE IDS 3..77 INCLUSIVE [MEASURED
#   probe M4 75/3/77 + PER-PROTOCOL DRAFT=0; ASM-2504 amending ASM-2342/
#   ASM-2406; REG A_pre_spend layer-geometry re-freeze rider 2026-07-17]
D_REGISTERED = 6144           # [generator-spec kaec_format "D = 6144"]
REGISTERED_CONSTRUCTION_SEED = 20260716
#   [REG freeze_manifest A(vii), freeze-(A) completion refreeze]
CONSTRUCTION_MANIFEST = (ROOT / "data" / "f1k-carriers-v1" / "generator" /
                         "construction-manifest.jsonl")
#   the (A)-time deterministic construction manifest the binding pins
CONSTRUCTION_BINDING_FIELDS = (
    "mode", "manifest_sha256", "tokenizer_sha256", "engine_weights_sha256",
    "dump_patch_sha256", "construction_seed", "layers")
#   [build_carriers.py BINDING_FIELDS — carrier-HOLD fix 1]
CONSTRUCTION_ECHO_RE = re.compile(
    r"^\[KAE-DUMP\] armed:.*?\bseed=([0-9-]+)", re.M)
#   [kot-f1k-dump/1 REQUIRED provenance echo — carrier-HOLD fix 5]
PROVENANCE_ARTIFACT_KEYS = {
    # config.carrier_provenance.<key> (a REAL-run artifact path) -> the
    # binding field its sha256 must DERIVE to (re-review item 8: derived
    # from the actual artifact bytes and compared, never accepted as a
    # caller assertion of mere 64-hex syntax)
    "tokenizer_artifact": "tokenizer_sha256",
    "engine_weights_artifact": "engine_weights_sha256",
    "dump_patch_artifact": "dump_patch_sha256",
}

# [R10] Carrier re-review CONTENT-AUTHENTICATION constants (2026-07-16,
# round-10; the metadata gates above were confirmed sound — these close the
# CONTENT-integrity holes).
MOCK_STACK_SCRIPTS = ("mock_colibri_dump.py", "mock_tokenizer.py",
                      "mock_colibri.py")
#   [R10-1] the repo's $0 mock stack. A REAL construction/report can NEVER
#   be satisfied by a mock table: any real-claiming binding whose
#   provenance shas match the digest of a repo mock script (i.e. a
#   relabeled mock construction, or a config that names a mock script as
#   the pinned artifact) is refused fail-closed.
NONDEGEN_MIN_STD_OVER_RMS = 1e-3
NONDEGEN_MIN_NONZERO_FRAC = 1.0 / 1024.0
#   [R10-2] non-degeneracy floors for carrier-table vectors (STIPULATED;
#   see ASM ledger, round-10 rider). A REAL §2.4 mean-difference carrier is
#   a dense difference of hidden-state means: component std ~ component rms
#   (mean component ~ 0) and essentially every component nonzero. The
#   floors sit ORDERS OF MAGNITUDE below any real carrier and exist only
#   to kill degenerate bodies: all-zero, constant/near-constant, and
#   below-min-variance vectors (the round-10 exploit: correctly-SHAPED
#   all-zero mode-real tables passed the provenance gate end-to-end).
ROWS_AUTH_DOMAIN = "kot-f1k-rows-auth/1"
#   [R10-4] campaign checkpoint/resume authentication: rows.jsonl resume
#   state is content-hashed (running sha256 over the exact row lines under
#   this domain) and BOUND to the current run's pinned inputs (carrier
#   table + construction report + engine files + eval manifest + phase);
#   a resume whose hash/bindings do not match is refused, so resume can
#   never skip real execution or inject foreign rows.


def vector_degeneracy(v):
    """[R10-2] Non-degeneracy check for one (concept, layer) carrier
    vector. Returns None when the vector is non-degenerate, else a short
    reason string. Enforced classes (the round-10 review's list): all-zero,
    near-constant, below-min-variance, plus a trivially-sparse floor.
    C-speed on lists/tuples/array('f'): count() + math.hypot(*v) + sum()."""
    n = len(v)
    if n == 0:
        return "empty vector"
    nz = n - v.count(0.0)
    if nz == 0:
        return "all-zero"
    if nz < NONDEGEN_MIN_NONZERO_FRAC * n:
        return ("only %d/%d components nonzero (< the 1/1024 floor)"
                % (nz, n))
    norm = math.hypot(*v)
    if norm == 0.0 or not math.isfinite(norm):
        return "zero/non-finite norm"
    mean = sum(v) / n
    rms = norm / math.sqrt(n)
    var = max(norm * norm / n - mean * mean, 0.0)
    if math.sqrt(var) < NONDEGEN_MIN_STD_OVER_RMS * rms:
        return ("near-constant: component std %.3g < %g x rms %.3g "
                "(min-variance floor)"
                % (math.sqrt(var), NONDEGEN_MIN_STD_OVER_RMS, rms))
    return None


def mock_stack_shas():
    """[R10-1] Current digests of the repo mock stack (recomputed at every
    call — editing a mock changes its digest, which only ever WIDENS what a
    stale relabeled binding fails against)."""
    out = {}
    for name in MOCK_STACK_SCRIPTS:
        p = HERE / name
        if p.is_file():
            out[sha256_file(p)] = name
    return out

# instrumentation counters surfaced by the --mock self-check
BANNERS_SKIPPED = {"n": 0}
ENGAGEMENT_CHECKS = {"n": 0}
TIES_LOGGED = {"n": 0}


class DriverError(SystemExit):
    def __init__(self, code, msg):
        print("%s: %s" % (code, msg), file=sys.stderr)
        super().__init__(2)


def fail(code, msg):
    raise DriverError(code, msg)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def attest_bool(value, what):
    """[R3-ATTEST] STRICT attestation emission (HOLD round-3 item 4 — the
    attestation-laundering fix). The driver previously bool()-coerced
    manifest/template/guard/dose values before emitting, so an upstream
    JSON STRING "false" (truthy in Python) was emitted as the JSON boolean
    `true` and the analysis PASSed — the driver itself laundered a failing
    attestation into a passing one. RULE: the driver NEVER coerces; every
    emitted validity flag must ALREADY be a genuine JSON boolean derived
    from a strict check of the real underlying condition. A non-bool here
    means the underlying value is not a valid measurement/commitment —
    the RUN fails closed; `true` is never fabricated. Truthiness is banned
    on the whole attestation surface (reads use `is True`, emission uses
    this function)."""
    if not isinstance(value, bool):
        fail("ERR_F1K_ATTEST",
             "%s is %r (%s), not a JSON boolean — attestations are never "
             "coerced (bool() truthiness previously laundered the string "
             "\"false\" into an emitted true => spurious PASS); the run "
             "fails closed until the underlying value is a genuine strict "
             "boolean [HOLD round-3 item 4]"
             % (what, value, type(value).__name__))
    return value


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")


# ---------------------------------------------------------------------------
# KAEC carrier files (the engine's KAE_CARRIER format [PATCH kae.h]):
#   [4]="KAEC" | i32 nc | i32 nl | i32 D | i32 layer_id[nl] | f32 K[nc*nl*D]
# ---------------------------------------------------------------------------
def kaec_header(path):
    try:
        with open(path, "rb") as f:
            raw = f.read(16)
    except OSError as e:
        fail("ERR_F1K_CARRIER", "cannot read carrier %s: %s" % (path, e))
    if len(raw) < 16 or raw[:4] != b"KAEC":
        fail("ERR_F1K_CARRIER", "bad KAEC magic/short header: %s" % path)
    nc, nl, D = struct.unpack_from("<iii", raw, 4)
    if nc <= 0 or nl <= 0 or D <= 0:
        fail("ERR_F1K_CARRIER", "non-positive dims in %s" % path)
    return {"nc": nc, "nl": nl, "D": D}


def kaec_read(path):
    with open(path, "rb") as f:
        raw = f.read()
    if len(raw) < 16 or raw[:4] != b"KAEC":
        fail("ERR_F1K_CARRIER", "bad KAEC magic/short header: %s" % path)
    nc, nl, D = struct.unpack_from("<iii", raw, 4)
    if nc <= 0 or nl <= 0 or D <= 0:
        fail("ERR_F1K_CARRIER", "non-positive dims in %s" % path)
    layers = list(struct.unpack_from("<%di" % nl, raw, 16))
    body_off = 16 + 4 * nl
    want = nc * nl * D
    vals = struct.unpack_from("<%df" % want, raw, body_off)
    if len(raw) != body_off + 4 * want:
        fail("ERR_F1K_CARRIER", "trailing/short carrier body: %s" % path)
    return {"nc": nc, "nl": nl, "D": D, "layers": layers, "vals": list(vals)}


def kaec_write(path, nc, layers, D, vals):
    nl = len(layers)
    if len(vals) != nc * nl * D:
        fail("ERR_F1K_CARRIER", "kaec_write size mismatch")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"KAEC")
        f.write(struct.pack("<iii", nc, nl, D))
        f.write(struct.pack("<%di" % nl, *layers))
        f.write(struct.pack("<%df" % len(vals), *vals))


def kaec_subset(master, layers, out_path):
    """Derive the KAEC file for a splice-layer subset — a PURE FUNCTION of
    the (B0)-committed master table [DES §R-REV3.3: realized tables enter
    as pure functions of frozen rules; subsetting selects slots, it never
    creates content]. Fails closed if a requested layer is absent."""
    m = kaec_read(master)
    slots = []
    for lay in layers:
        if lay not in m["layers"]:
            fail("ERR_F1K_CARRIER",
                 "frozen layer %d absent from master %s (candidate splice-"
                 "layer union must cover every pilot layer set, freeze-"
                 "manifest A(iv))" % (lay, master))
        slots.append(m["layers"].index(lay))
    nc, nl, D = m["nc"], m["nl"], m["D"]
    vals = []
    for c in range(nc):
        for s in slots:
            base = (c * nl + s) * D
            vals.extend(m["vals"][base:base + D])
    kaec_write(out_path, nc, list(layers), D, vals)
    return out_path


def _kaec_vec(m, c, slot):
    base = (c * m["nl"] + slot) * m["D"]
    return m["vals"][base:base + m["D"]]


def _vnorm(v):
    return math.sqrt(sum(x * x for x in v))


# ---------------------------------------------------------------------------
# Registered statistics helpers — MIRRORS of the pinned analysis/f1k.py
# machinery (cluster_diffs + one-sided cluster sign-flip, §R3.1), used ONLY
# for the pilot-n placebo alarm and dev descriptives; the verdict-bearing
# statistics run exclusively in the pinned analysis/f1k.py.
# ---------------------------------------------------------------------------
def cluster_diffs(xa, xb, clusters):
    shared = sorted(set(xa) & set(xb))
    acc = {}
    for i in shared:
        acc.setdefault(clusters[i], []).append(xa[i] - xb[i])
    return [sum(v) / len(v) for _, v in sorted(acc.items())]


def signflip_p(dcs, name, b=PERM_B):
    """One-sided cluster sign-flip permutation p for H1: mean_c D_c > 0,
    add-one corrected [DES §R3.1; ANA signflip]. Deterministic sub-seed."""
    C = len(dcs)
    if C == 0:
        return None, None
    t_obs = sum(dcs) / C
    rng = random.Random("%d|%s" % (PERM_SEED, name))
    ge = 0
    for _ in range(b):
        t = sum(d if rng.random() < 0.5 else -d for d in dcs) / C
        if t >= t_obs:
            ge += 1
    return 100.0 * t_obs, (1 + ge) / (b + 1)


# ---------------------------------------------------------------------------
# Config + input-pin verification (fail-closed)
# ---------------------------------------------------------------------------
def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        fail("ERR_F1K_CONFIG", "cannot load config %s: %s" % (path, e))
    for k in ("engine", "eval_manifest", "carriers", "corpora", "cost",
              "power", "replace"):
        if k not in cfg:
            fail("ERR_F1K_CONFIG", "config missing %r" % k)
    rep = cfg.get("replace") or {}
    if "ran" in rep:
        # [FIX-3] replace.ran is an OUTPUT of the frozen §R-REV4.3 gate
        # (computed at pilot addendum (6)), never a config input.
        fail("ERR_F1K_REPLACE",
             "config.replace.ran is not an input: the REPLACE RUN/DEFER "
             "decision is the frozen NI power gate (dev delta_R on dev-96, "
             "n_NI = delta_R*DEFF/SE_NI^2 <= %d, §R-REV4.3/ASM-2124) "
             "computed at pilot addendum (6) — remove the key" % N_TEST)
    if not isinstance(rep.get("engine_supported"), bool):
        fail("ERR_F1K_REPLACE",
             "config.replace.engine_supported must be an explicit bool: "
             "the gate-0 patch stubs REPLACE (KAE_MODE=1 inert [PATCH "
             "kae.h]); TRUE requires a reviewed REPLACE-capable engine")
    env = (cfg.get("engine") or {}).get("env") or {}
    for k in env:
        if str(k).startswith("KAE"):
            fail("ERR_F1K_CONFIG",
                 "engine.env may not carry KAE* keys (%r): the driver owns "
                 "the KAE seam per arm — a config override would be a "
                 "silent arm change" % k)
    validate_pinning(cfg)
    validate_power(cfg)
    # [R6-3] worst-case $ sanity, fail-closed: the RECOMPUTED 96/1573
    # mandatory-campaign worst case must clear the approved ceiling —
    # exceeding it is a STOP-and-return-to-maintainer, never a silent
    # ceiling raise (ASM-2374).
    wc = worst_case_usd(replace=False)
    if wc > USD_CAP:
        fail("ERR_F1K_COST",
             "recomputed worst-case $%.2f for the MANDATORY 96/1573 "
             "campaign EXCEEDS the approved $%.0f ceiling (ASM-2374) — "
             "STOP and return to the maintainer; the cap is never raised "
             "silently" % (wc, USD_CAP))
    return cfg


PIN_BASENAME_RE = re.compile(r"(?!1\Z)[A-Za-z0-9._+-]{1,255}")
# [v2, review #3] VERBATIM mirror of the PINNED analysis schema's
# expert_pinning.PIN pattern (analysis/f1k.py §2a:
# r"^(?!1\Z)[A-Za-z0-9._+-]{1,255}\Z", applied via re.fullmatch — the
# schema side is the AUTHORITATIVE copy; this driver-side constant must
# stay textually identical to it, checked by the §1i pin_badname probe).
# Enforced at CONFIG LOAD so a basename the pinned schema would reject
# can never run first and be rejected only AFTER spend.


def validate_pinning(cfg):
    """[FIX-5]+[ASM-2513] ENFORCE + RECORD expert pinning [COST lever 2 /
    ASM-2205: 'expert-pinning + warm page-cache, priced conservatively at
    1.20x'; bringup.sh step 6: configured via the engine's PIN= / PIN_GB
    env]. FROZEN SEMANTICS (glm52-followup-experiment.md §7.1:638-639):
    PIN=<stats-file> — the hot-expert pin list — with PIN_GB fixed at
    bring-up from measured free RAM and recorded in the manifest; the
    engine loads the pinned hot set FROM a stats file
    (glm52-kernel-integration-northstar.md:92 "pin[layer] ... loadable
    from a stats file PIN=stats.txt"). The pre-fix literal PIN=="1" was
    NEVER the frozen (or engine) semantics: the engine would treat it as
    a stats-file path named '1', pin nothing, and the ledger would still
    attest pinning — the false pinning attestation this fix closes
    (F1K-AFFORDABILITY-DECISION.md §3/§5.1). Optional pass-through is
    still not enough: an unpinned run silently voids the $155 ceiling
    arithmetic [R6-3/ASM-2374]. The stats-file is validated (exists,
    non-empty UTF-8, M4-measured '<layer> <expert> <count>' int-triple
    lines — poc/gcp/probe-results/accum20.stats; format re-verified at
    bring-up per ASM-1971) and its content sha256 is DERIVED FROM BYTES
    and recorded in ledger + sidecar + the [R10-4] resume-auth binding,
    so the metered speedup resolves ASM-2205 against a NAMED, HASHED
    pin. Engine-side arming is separately verified fail-closed from the
    pin banner/counters (check_pin_engagement). NOTE: the M4 dev-item
    pin (pin_50gb.stats, 6802cc97...) does NOT transfer — the campaign
    pin is the LICENSED BRING-UP-DERIVED pin, run for the WHOLE
    campaign [REV-C/REV-E: the F1K-CONSTRUCTION-PLAN.md §5.4
    full-corpus re-derivation is WITHDRAWN — structurally impossible
    through the sha-pinned builder; DEFERRED behind bead
    kernel-of-truth-8cpm; this driver refuses a campaign pin whose sha
    differs from the gate artifact's]; this function accepts whatever
    bring-up-produced stats-file the config names and pins its hash."""
    env = (cfg.get("engine") or {}).get("env") or {}
    pin = env.get("PIN")
    pin_gb = env.get("PIN_GB")
    if pin is None or str(pin).strip() in ("", "0", "1"):
        fail("ERR_F1K_PINNING",
             "engine.env.PIN must be the PATH of the bring-up-derived "
             "hot-expert stats-file (frozen semantics PIN=<stats-file>, "
             "glm52-followup-experiment.md §7.1:638; the legacy literal "
             "\"1\" is REFUSED — it was never engine semantics and could "
             "only emit a false pinning attestation [ASM-2513]. The $155 "
             "ceiling prices the 1.20x pinning lever; COST item 2 / "
             "ASM-2205/ASM-2374; got %r)" % (pin,))
    ap = os.path.abspath(str(pin))
    if not PIN_BASENAME_RE.fullmatch(os.path.basename(ap)):
        fail("ERR_F1K_PINNING",
             "engine.env.PIN basename %r violates the PINNED ledger "
             "schema's rule [A-Za-z0-9._+-]{1,255} excluding \"1\" "
             "(analysis/f1k.py cost.expert_pinning.PIN) — enforced HERE "
             "at config load so a run can never spend first and be "
             "schema-rejected after [ASM-2513 v2 review #3]"
             % (os.path.basename(ap),))
    try:
        raw = Path(ap).read_bytes()
    except OSError as e:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is not readable (%s) — a pin "
             "that cannot be loaded would leave the run UNPINNED while "
             "the ledger attests pinned [ASM-2513]" % (ap, e))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is not UTF-8 text (%s) — not "
             "an engine stats file [ASM-2513]" % (ap, e))
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is EMPTY — pins nothing "
             "[ASM-2513]" % ap)
    for i, ln in enumerate(lines):
        parts = ln.split()
        if len(parts) != 3 or not all(p.isascii() and p.isdigit()
                                      for p in parts):
            # [v2, review #2] ASCII digits ONLY: bare str.isdigit()
            # admits Unicode digit codepoints — int() silently ACCEPTS
            # some (Arabic-Indic '٣' -> 3) and CRASHES on others
            # (superscript '²' -> ValueError) [MEASURED, python3
            # 2026-07-18]; neither is the M4-measured ASCII format.
            fail("ERR_F1K_PINNING",
                 "engine.env.PIN stats-file %s line %d is not the "
                 "M4-measured '<layer> <expert> <count>' non-negative "
                 "ASCII int triple (%r) — malformed pin lists are "
                 "refused, never silently skipped [ASM-1971 fetch-grade "
                 "rider: format re-verified at bring-up; a semantic "
                 "surprise halts for a protocol amendment BEFORE data "
                 "collection]" % (ap, i + 1, ln[:80]))
    try:
        gb = float(pin_gb)
    except (TypeError, ValueError):
        gb = -1.0
    if not 0.0 < gb < float("inf"):
        # [v2, review #2] FINITE positive only: float('nan') <= 0 is
        # False and float('inf') > 0 is True [MEASURED, python3
        # 2026-07-18], so the v1 `gb <= 0` check let NaN/inf through to
        # fail only at the post-spawn banner-budget comparison — i.e.
        # AFTER spend. NaN fails every comparison here; inf fails the
        # upper bound; both are refused at config load.
        fail("ERR_F1K_PINNING",
             "engine.env.PIN_GB must be a FINITE positive GB budget "
             "(got %r; NaN/inf REFUSED — a non-finite budget can never "
             "coherently match an engine banner and must fail BEFORE "
             "spend) — fixed at bring-up from measured free RAM and "
             "recorded [DES §7.1:639; COST item 2; ASM-2513 v2]"
             % (pin_gb,))
    env["PIN"] = ap          # engine receives the resolved absolute path
    return {"PIN": os.path.basename(ap),
            "pin_file_sha256": hashlib.sha256(raw).hexdigest(),
            "pin_file_lines": len(lines),
            "PIN_GB": gb,
            "pin_scope": "shared-all-arms",
            "semantics": "PIN=<stats-file> pins the hot expert working "
                         "set resident (top experts by count under the "
                         "PIN_GB budget); PIN_GB fixed at bring-up from "
                         "measured free RAM [DES §7.1:638-639]. One "
                         "shared bring-up-derived pin across all arms, "
                         "recorded as such (matched-budget discipline; "
                         "F1K-CONSTRUCTION-PLAN.md §5 item 6 minimum "
                         "realization). The 1.20x-pessimistic throughput "
                         "lever of the $155 ceiling [glm52-f1k-cost-"
                         "reduction.md item 2 / ASM-2205; REVISION-6 cap "
                         "ASM-2374]; realized speedup resolves ASM-2205 "
                         "from the metered ledger; engine arming "
                         "verified from the pin banner/counters "
                         "[ASM-2513]."}


def attested_pinning(ledger):
    """[ASM-2513] The expert_pinning record is emitted ONLY once engine
    arming was POSITIVELY verified this run (check_pin_engagement
    recorded experts_pinned from the pin banner/counters). A sidecar
    attesting pinning without an engine attestation would re-open the
    false-attestation channel this fix closes — fail closed instead."""
    ep = dict(ledger.d.get("expert_pinning") or {})
    n = ep.get("experts_pinned")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        fail("ERR_F1K_PINNING",
             "emission without a verified engine pin attestation "
             "(expert_pinning.experts_pinned=%r) — the pin banner/"
             "counters were never positively verified this run; a "
             "pinning attestation is never emitted on trust [ASM-2513]"
             % (n,))
    return ep


def validate_power(cfg):
    """[FIX-7] Frozen power block validated EXACTLY, not just present
    [DES §R-REV5 / REG mc_exact_power_confirmation]: rho_U == 0.10,
    mu* == 4.09 pts, N_sim == 10000, the registered seed, and the >= 0.80
    pass threshold (coherence enforced). A below-threshold MC is a
    REPORTING-fidelity outcome (the sim replaces the headline joint-MDE),
    never a spend lever — so it is validated for coherence, not gated."""
    p = cfg.get("power") or {}
    if p.get("rho_u") != RHO_U:
        fail("ERR_F1K_POWER", "power.rho_u %r != frozen planning rho_U %s "
             "[DES §R-REV3.1 item 3]" % (p.get("rho_u"), RHO_U))
    if p.get("joint_mde_points_at_rho_u") != MU_STAR_POINTS:
        fail("ERR_F1K_POWER",
             "power.joint_mde_points_at_rho_u %r != frozen %s "
             "[DES §R-REV4.1(b)/§R-REV5: joint-MDE at rho_U=0.10]"
             % (p.get("joint_mde_points_at_rho_u"), MU_STAR_POINTS))
    mc = p.get("mc_exact_power") or {}
    if mc.get("mu_star") != MU_STAR_POINTS:
        fail("ERR_F1K_POWER", "mc_exact_power.mu_star %r != frozen %s"
             % (mc.get("mu_star"), MU_STAR_POINTS))
    if mc.get("n_sim") != MC_N_SIM:
        fail("ERR_F1K_POWER", "mc_exact_power.n_sim %r != frozen %d "
             "[DES §R-REV5]" % (mc.get("n_sim"), MC_N_SIM))
    if mc.get("seed") != MC_SEED:
        fail("ERR_F1K_POWER", "mc_exact_power.seed %r != registered %d "
             "(freeze-manifest (A) MC procedure + seed)"
             % (mc.get("seed"), MC_SEED))
    # [R6-4] REVISION-6 record: joint_power is the PER-RUNG dict of the
    # frozen co-primary power table {"K-1","K-2","K-3"} (ASM-2369/2371;
    # the committed 0.8043/0.8058/0.8001) — the pinned analysis computes
    # the ASM-2376 Frechet intersection bounds from EXACTLY these three
    # numbers, so the superseded scalar form is REJECTED, and coherence is
    # the PER-RUNG >= 0.80 criterion (pass iff ALL THREE clear it).
    jp = mc.get("joint_power")
    if not isinstance(jp, dict) or sorted(jp) != ["K-1", "K-2", "K-3"]:
        fail("ERR_F1K_POWER",
             "mc_exact_power.joint_power must be the REVISION-6 per-rung "
             "dict over exactly {'K-1','K-2','K-3'} (ASM-2371 co-primary "
             "power table; the superseded scalar form is rejected; got %r)"
             % (jp,))
    # [R3-POWER] HOLD round-3 item 5: the power block is pinned to the
    # FROZEN REGISTERED values EXACTLY — the prior numeric-in-[0,1] range
    # check accepted arbitrary marginals (0.9/0.9/0.9) into the sidecar
    # and the registered disclosure. Any deviation from the ASM-2371
    # table fails closed; the pinned analysis enforces the same equality.
    if jp != REGISTERED_JOINT_POWER:
        fail("ERR_F1K_POWER",
             "mc_exact_power.joint_power %r != the REGISTERED ASM-2371 "
             "per-rung table %s — the frozen power block is pinned "
             "EXACTLY; arbitrary marginals are never emitted [HOLD "
             "round-3 item 5]" % (jp, REGISTERED_JOINT_POWER))
    if not isinstance(mc.get("pass"), bool):
        fail("ERR_F1K_POWER", "mc_exact_power.pass must be a bool")
    if mc["pass"] != all(jp[r] >= MC_PASS_MIN
                         for r in ("K-1", "K-2", "K-3")):
        fail("ERR_F1K_POWER",
             "mc_exact_power incoherent: pass=%r with per-rung powers %s "
             "vs the frozen PER-RUNG >= %s criterion (ASM-2371; ALL THREE "
             "co-primary rungs must clear it) [DES §R-REV5]"
             % (mc["pass"], jp, MC_PASS_MIN))
    # [R6-4]/[R3-POWER] the ASM-2376 shared-K joint-dependence intersection
    # sim block is part of the registered sidecar power contract (carried
    # into /analysis/power_scope/intersection_all_three by the pinned
    # analysis — the executable successor of the withdrawn prose figure).
    # HOLD round-3 item 5: an EMPTY dict previously satisfied the
    # isinstance check — the block must now carry the registered ASM-2376
    # values EXACTLY on every required key; deviation/absence fails closed.
    inter = p.get("mc_intersection")
    if not isinstance(inter, dict) or not inter:
        fail("ERR_F1K_POWER",
             "power.mc_intersection must be the NON-EMPTY ASM-2376 shared-K "
             "joint-dependence intersection sim block (got %r) [HOLD "
             "round-3 item 5]" % (inter,))
    for k, want in sorted(REGISTERED_MC_INTERSECTION.items()):
        if inter.get(k) != want:
            fail("ERR_F1K_POWER",
                 "power.mc_intersection[%r] = %r != the REGISTERED "
                 "ASM-2376 value %r (poc/f1k-askability/reports/"
                 "power-intersection-n1573.json; pinned EXACTLY, never "
                 "carried unverified) [HOLD round-3 item 5]"
                 % (k, inter.get(k), want))
    return p


def kot_corpus_hash(dirpath):
    """kot-corpus-hash/1 over an arbitrary corpus dir — byte-identical to
    the reference implementation tools/registry/corpus-pin.py
    [REG pins.corpus_hashes._recipe]."""
    base = Path(dirpath)
    if not base.is_dir():
        fail("ERR_F1K_CORPUS", "corpus dir missing: %s" % dirpath)
    lines = []
    for dp, dns, fns in os.walk(str(base)):
        dns.sort()
        for name in fns:
            full = os.path.join(dp, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, str(base)).replace(os.sep, "/")
            lines.append((rel.encode("utf-8"), sha256_file(full)))
    if not lines:
        fail("ERR_F1K_CORPUS", "corpus dir has no regular files: %s"
             % dirpath)
    lines.sort(key=lambda t: t[0])
    payload = b"".join(d.encode("ascii") + b"  " + r + b"\n"
                       for r, d in lines)
    return hashlib.sha256(payload).hexdigest()


def _contained(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def verify_corpus_pins(cfg, mock):
    """Input seams (review §1/§2/§3): verify the eval manifest, carrier
    tables, and trigger map against the frozen record's corpus pins
    [REG pins.corpus_hashes, recipe kot-corpus-hash/1] BEFORE any scoring.
    The absent real corpora are a SEPARATE build (PINNED-AT-INPUTS): a real
    run fails closed until the ops amendment pins them; this driver never
    fabricates them. Mock fixtures verify against their own config-declared
    hashes and are labeled MOCK."""
    try:
        reg = json.loads(REGISTRY_RECORD.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail("ERR_F1K_CORPUS", "cannot read frozen record %s: %s"
             % (REGISTRY_RECORD, e))
    pins = (reg.get("pins") or {}).get("corpus_hashes") or {}
    corp = cfg.get("corpora") or {}
    out = {}
    for name in CORPUS_NAMES:
        ent = corp.get(name) or {}
        cdir = ent.get("dir")
        want = ent.get("expected_kot_corpus_hash")
        if not cdir or not want:
            fail("ERR_F1K_CORPUS",
                 "config.corpora[%r] must carry dir + "
                 "expected_kot_corpus_hash" % name)
        got = kot_corpus_hash(cdir)
        if got != want:
            fail("ERR_F1K_CORPUS",
                 "%s kot-corpus-hash %s != config-expected %s — the inputs "
                 "are not the pinned corpus" % (name, got, want))
        pinned = pins.get(name)
        placeholder = isinstance(pinned, str) and \
            pinned.startswith("PINNED-AT-INPUTS")
        if placeholder:
            if not mock:
                fail("ERR_F1K_CORPUS",
                     "%s is still PINNED-AT-INPUTS in the frozen record — "
                     "the real corpus is a SEPARATE build; NO real scoring "
                     "until the ops amendment pins it (this driver never "
                     "fabricates input corpora)" % name)
            out[name] = {"kot_corpus_hash": got,
                         "registry": "PINNED-AT-INPUTS placeholder "
                                     "(MOCK fixtures only)"}
        elif got != pinned:
            # [R6-5] the reset-refrozen record carries REAL digests for
            # f1k-eval-v1 / f1k-trigger-map-v1 (ASM-2377). MOCK fixtures
            # are SHAPED synthetics and legitimately diverge — disclosed,
            # never silently passed off as the pinned corpus; a REAL run
            # fails closed on this mismatch exactly as before.
            if not mock:
                fail("ERR_F1K_CORPUS",
                     "%s kot-corpus-hash %s != frozen record pin %s"
                     % (name, got, pinned))
            out[name] = {"kot_corpus_hash": got,
                         "registry": "MOCK fixture DIVERGES from the REAL "
                                     "frozen pin %s... (mock-only "
                                     "disclosure; a real run fails closed "
                                     "on this mismatch)" % pinned[:12]}
        else:
            out[name] = {"kot_corpus_hash": got, "registry": "MATCH"}
    # path containment: the scored bytes must be COVERED by the pins
    evdir = corp["f1k-eval-v1"]["dir"]
    if not _contained(cfg["eval_manifest"], evdir):
        fail("ERR_F1K_CORPUS",
             "eval_manifest %s is outside the pinned f1k-eval-v1 dir %s "
             "(review §2: arbitrary config paths rejected)"
             % (cfg["eval_manifest"], evdir))
    cadir = corp["f1k-carriers-v1"]["dir"]
    carrier_paths = []
    cars = cfg.get("carriers") or {}
    for arm in ("K", "d0", "d2"):
        carrier_paths.append(((cars.get(arm) or {}).get("path"), arm))
    for s, ent in sorted((cars.get("d1-drng") or {}).items()):
        carrier_paths.append((ent.get("path"), "d1-drng/%s" % s))
    for mid, ent in sorted((((cfg.get("pilot") or {}).get("panel") or {})
                            .get("members") or {}).items()):
        carrier_paths.append((ent.get("path"), "panel/%s" % mid))
    for p, what in carrier_paths:
        if not p:
            fail("ERR_F1K_CORPUS", "carrier path missing for %s" % what)
        if not _contained(p, cadir):
            fail("ERR_F1K_CORPUS",
                 "carrier %s (%s) is outside the pinned f1k-carriers-v1 "
                 "dir %s" % (what, p, cadir))
    return out


def _kaec_header_layers(path):
    """KAEC header incl. the layer-id list (16 + 4*nl bytes; cheap —
    never loads the body)."""
    try:
        with open(path, "rb") as f:
            raw = f.read(16)
            if len(raw) < 16 or raw[:4] != b"KAEC":
                fail("ERR_F1K_CARRIERPROV",
                     "bad KAEC magic/short header: %s" % path)
            nc, nl, D = struct.unpack_from("<iii", raw, 4)
            if nc <= 0 or nl <= 0 or D <= 0:
                fail("ERR_F1K_CARRIERPROV",
                     "non-positive KAEC dims in %s" % path)
            lay = f.read(4 * nl)
            if len(lay) != 4 * nl:
                fail("ERR_F1K_CARRIERPROV",
                     "short KAEC layer-id block in %s" % path)
            layers = list(struct.unpack("<%di" % nl, lay))
    except OSError as e:
        fail("ERR_F1K_CARRIERPROV", "cannot read carrier %s: %s"
             % (path, e))
    return nc, nl, D, layers


def _configured_carrier_paths(cfg):
    """Every carrier table the run config points the engine at (main arms
    + d1-drng seeds + pilot panel members) — the exact set the KAE seam
    splices."""
    cars = cfg.get("carriers") or {}
    paths = []
    for arm in ("K", "d0", "d2"):
        paths.append(((cars.get(arm) or {}).get("path"), arm))
    for s, ent in sorted((cars.get("d1-drng") or {}).items()):
        paths.append((ent.get("path"), "d1-drng/%s" % s))
    for mid, ent in sorted((((cfg.get("pilot") or {}).get("panel") or {})
                            .get("members") or {}).items()):
        paths.append((ent.get("path"), "panel/%s" % mid))
    return paths


def kaec_nondegeneracy_scan(path, what):
    """[R10-2] FULL-coverage non-degeneracy scan of a KAEC carrier table:
    EVERY (concept, layer) vector must pass vector_degeneracy (all-zero /
    near-constant / below-min-variance / trivially-sparse bodies are
    refused). Streams the body cell-by-cell (never holds a full 179 MB
    real table in Python floats); array('f') gives C-speed count/min/max
    and hypot/sum. KAEC bodies are little-endian f32 [PATCH kae.h];
    byteswap on a big-endian host keeps the arithmetic identical."""
    with open(path, "rb") as f:
        hdr = f.read(16)
        if len(hdr) < 16 or hdr[:4] != b"KAEC":
            fail("ERR_F1K_CARRIERPROV",
                 "carrier %s (%s): bad KAEC header at non-degeneracy scan"
                 % (what, path))
        nc, nl, D = struct.unpack_from("<iii", hdr, 4)
        f.seek(16 + 4 * nl)
        for c in range(nc):
            for li in range(nl):
                buf = f.read(4 * D)
                if len(buf) != 4 * D:
                    fail("ERR_F1K_CARRIERPROV",
                         "carrier %s (%s): short body at cell (c=%d, li=%d)"
                         % (what, path, c, li))
                a = array.array("f")
                a.frombytes(buf)
                if sys.byteorder != "little":
                    a.byteswap()
                reason = vector_degeneracy(a)
                if reason:
                    fail("ERR_F1K_CARRIERPROV",
                         "carrier %s (%s): DEGENERATE vector at (concept=%d"
                         ", layer_index=%d): %s — a real §2.4 mean-"
                         "difference carrier is non-degenerate; degenerate "
                         "mode-real bodies are never ingested "
                         "([R10-2] carrier re-review content gap 2)"
                         % (what, Path(path).name, c, li, reason))


def verify_carrier_construction(cfg, mock):
    """[R9-PROV] The driver<->generator PROVENANCE seam (carrier RE-REVIEW
    item 8, 2026-07-16). verify_corpus_pins checks the carrier-DIR digest
    and path containment, but NEVER looked inside the generator's
    construction-report — so mode=mock D=6144 tables with 8 non-pinned
    layers were ingested end-to-end with every gate green. Now, BEFORE any
    carrier is spliced for a REAL campaign, the driver enforces
    fail-closed (ERR_F1K_CARRIERPROV):

      * construction-report.json present next to the K master table, with
        the full carrier-HOLD-fix-1 provenance binding;
      * report + binding mode == "real" (a mode=mock construction can
        NEVER feed a real campaign);
      * layers == the REGISTERED A(iv) splice union (75 MoE layers 3..77
        [ASM-2342/ASM-2406]), D == 6144, nc == C_REGISTERED == 96,
        construction_seed == the registered 20260716 [REG A(vii)];
      * binding.manifest_sha256 == sha256 of the COMMITTED (A)-time
        construction manifest (re-derived here, never trusted);
      * the engine provenance-echo summary re-verified (expected seed,
        one verified batch per concept, sample line re-parsed);
      * the three engine-side provenance shas DERIVED from the actual
        artifacts named by config.carrier_provenance.{tokenizer_artifact,
        engine_weights_artifact, dump_patch_artifact} and compared to the
        binding — a caller assertion of mere 64-hex syntax is never
        accepted (re-review item 8);
      * every configured carrier table byte-witnessed against the report:
        sha256 + size + KAEC header geometry (nc/nl/D/layer ids) + the
        exact KAEC fp32 size arithmetic.

    In MOCK runs (the $0 wiring validation): driver-fabricated stub
    fixtures carry no construction report — DISCLOSED, never passed off
    as generator output; when a generator report IS present (the
    mock_e2e_carriers acceptance fixture) its binding/table witness
    checks run identically, with mode=mock disclosed.

    Returns (disclosure, pins_observed): the disclosure is written to the
    outdir as carrier-provenance.json, and pins_observed is carried on
    the kot-log/1 run record (the typed {observed[, expected]} sha256 map
    — the record-level witness channel; the sidecar schema is CLOSED
    [ANA SIDECAR_SCHEMA default-deny], so the run record, which
    verdict-gen re-verifies, is where mode+bindings are witnessed)."""
    cars = cfg.get("carriers") or {}
    kpath = Path((cars.get("K") or {}).get("path") or "")
    rep_path = kpath.parent / "construction-report.json"
    pins = {}
    if not rep_path.is_file():
        if not mock:
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: construction-report.json is ABSENT next "
                 "to the K master table (%s) — carriers without the "
                 "generator's bound construction report are NEVER ingested "
                 "for a real run (re-review item 8)" % rep_path)
        if kpath.is_file():
            pins["f1k-carriers-v1.k-true"] = {
                "observed": sha256_file(kpath)}
        return ({"mode": "MOCK-FIXTURE (driver-fabricated stub tables; no "
                         "construction report — mock only, disclosed)",
                 "construction_report": None}, pins)
    try:
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail("ERR_F1K_CARRIERPROV",
             "cannot read construction report %s: %s" % (rep_path, e))
    binding = rep.get("binding")
    if not isinstance(binding, dict) or \
            any(k not in binding for k in CONSTRUCTION_BINDING_FIELDS):
        fail("ERR_F1K_CARRIERPROV",
             "construction report %s carries no complete provenance "
             "binding %s (carrier-HOLD fix 1 shape) — unbound carrier "
             "artifacts are never ingested" % (rep_path,
                                               CONSTRUCTION_BINDING_FIELDS))
    mode = binding.get("mode")
    if mode not in ("mock", "real") or rep.get("mode") != mode:
        fail("ERR_F1K_CARRIERPROV",
             "construction report mode %r / binding mode %r incoherent — "
             "refusing" % (rep.get("mode"), mode))
    if not mock:
        if mode != "real":
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: the construction report is a mode=%s "
                 "artifact — a mock construction can NEVER feed a real "
                 "campaign (re-review item 8; generator binding, "
                 "carrier-HOLD fix 1)" % mode)
        if binding.get("construction_seed") != REGISTERED_CONSTRUCTION_SEED \
                or rep.get("construction_seed") != \
                REGISTERED_CONSTRUCTION_SEED:
            fail("ERR_F1K_CARRIERPROV",
                 "construction_seed %r/%r != the registered %d "
                 "[REG A(vii)]" % (binding.get("construction_seed"),
                                   rep.get("construction_seed"),
                                   REGISTERED_CONSTRUCTION_SEED))
        if binding.get("layers") != REGISTERED_SPLICE_LAYERS or \
                rep.get("layers") != REGISTERED_SPLICE_LAYERS:
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: construction layers != the REGISTERED "
                 "A(iv) splice union (75 MoE layers %d..%d [ASM-2504]); "
                 "got %r... — wrong-layer tables are never ingested "
                 "(re-review item 8)"
                 % (REGISTERED_SPLICE_LAYERS[0],
                    REGISTERED_SPLICE_LAYERS[-1],
                    (binding.get("layers") or [])[:8]))
        if rep.get("D") != D_REGISTERED:
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: construction D %r != the frozen "
                 "kaec_format D = %d" % (rep.get("D"), D_REGISTERED))
        if rep.get("nc") != C_REGISTERED:
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: construction nc %r != C_REGISTERED = %d"
                 % (rep.get("nc"), C_REGISTERED))
        if not CONSTRUCTION_MANIFEST.is_file():
            fail("ERR_F1K_CARRIERPROV",
                 "the committed (A)-time construction manifest %s is "
                 "ABSENT — the binding's manifest pin cannot be "
                 "re-derived" % CONSTRUCTION_MANIFEST)
        man_sha = sha256_file(CONSTRUCTION_MANIFEST)
        if binding.get("manifest_sha256") != man_sha:
            fail("ERR_F1K_CARRIERPROV",
                 "binding manifest_sha256 %r != the committed (A)-time "
                 "construction manifest's %s — the carriers were not "
                 "built from the frozen manifest"
                 % (binding.get("manifest_sha256"), man_sha))
        echo = rep.get("engine_provenance_echo") or {}
        m = CONSTRUCTION_ECHO_RE.search(str(echo.get("sample") or ""))
        if echo.get("expected_seed") != REGISTERED_CONSTRUCTION_SEED or \
                echo.get("verified_batches") != C_REGISTERED or \
                not m or m.group(1) != str(REGISTERED_CONSTRUCTION_SEED):
            fail("ERR_F1K_CARRIERPROV",
                 "engine provenance-echo summary invalid (%r) — expected "
                 "seed %d, %d verified batches, and a parseable "
                 "'[KAE-DUMP] armed: ... seed=' sample (carrier-HOLD "
                 "fix 5 witness)" % (echo, REGISTERED_CONSTRUCTION_SEED,
                                     C_REGISTERED))
        pa = cfg.get("carrier_provenance") or {}
        for akey in sorted(PROVENANCE_ARTIFACT_KEYS):
            bfield = PROVENANCE_ARTIFACT_KEYS[akey]
            apath = pa.get(akey)
            if not apath or not Path(apath).is_file():
                fail("ERR_F1K_CARRIERPROV",
                     "REAL campaign: config.carrier_provenance.%s must "
                     "name the actual pinned artifact file (got %r) — "
                     "the %s is DERIVED from its bytes, never accepted "
                     "as a bare 64-hex assertion (re-review item 8)"
                     % (akey, apath, bfield))
            derived = sha256_file(apath)
            if derived != binding.get(bfield):
                fail("ERR_F1K_CARRIERPROV",
                     "binding %s %r != sha256(%s) = %s — the asserted "
                     "provenance pin is not the artifact's actual digest "
                     "(re-review item 8)"
                     % (bfield, binding.get(bfield), apath, derived))
            pins["carrier-%s" % akey.replace("_", "-")] = {
                "observed": derived, "expected": binding[bfield]}
        # ---- [R10-1] a REAL construction can NEVER be backed by the repo
        # mock stack: if any binding provenance sha (== the artifact-derived
        # digest checked above) matches a repo mock script's current bytes,
        # the "real" report is a relabeled mock construction (or the config
        # names a mock script as the pinned artifact) — refused fail-closed.
        mstack = mock_stack_shas()
        for bfield in ("tokenizer_sha256", "engine_weights_sha256",
                       "dump_patch_sha256"):
            hit = mstack.get(binding.get(bfield))
            if hit:
                fail("ERR_F1K_CARRIERPROV",
                     "REAL campaign: binding %s equals the digest of the "
                     "repo mock stack script %s — a real construction/"
                     "report can NEVER be satisfied by a mock table/"
                     "toolchain (relabeled mock construction refused; "
                     "[R10-1] carrier re-review content gap 1)"
                     % (bfield, hit))
        # ---- [R10-3] checkpoint-content witness: the generator now binds
        # a content hash (sha256 over the exact f64 vector bytes) of every
        # per-concept construction checkpoint into the report; a real
        # report without the full 96-entry witness list predates (or
        # strips) content authentication and is refused.
        cks = rep.get("checkpoint_content_sha256")
        if not (isinstance(cks, list) and len(cks) == C_REGISTERED
                and all(isinstance(x, str)
                        and re.fullmatch(r"[0-9a-f]{64}", x)
                        for x in cks)):
            fail("ERR_F1K_CARRIERPROV",
                 "REAL campaign: construction report carries no complete "
                 "checkpoint_content_sha256 witness (need %d x 64-hex; "
                 "got %r) — checkpoint vector contents must be content-"
                 "authenticated ([R10-3] carrier re-review content gap 3)"
                 % (C_REGISTERED,
                    (len(cks) if isinstance(cks, list) else type(cks))))
    # ---- table byte-witness (BOTH modes): every configured carrier must
    # be pinned by the report and match by sha256 + size + KAEC header
    # geometry + the exact fp32 size arithmetic --------------------------
    tables = rep.get("tables") or {}
    rep_layers = rep.get("layers")
    rep_D, rep_nc = rep.get("D"), rep.get("nc")
    checked = {}
    for p, what in _configured_carrier_paths(cfg):
        if not p:
            fail("ERR_F1K_CARRIERPROV",
                 "carrier path missing for %s" % what)
        rp = str(Path(p).resolve())
        if rp in checked:
            continue
        name = Path(p).name
        ent = tables.get(name)
        if not isinstance(ent, dict):
            fail("ERR_F1K_CARRIERPROV",
                 "carrier %s (%s) is not pinned by the construction "
                 "report's tables block — unwitnessed table refused"
                 % (what, name))
        size = os.path.getsize(p)
        got_sha = sha256_file(p)
        if ent.get("sha256") != got_sha or ent.get("bytes") != size:
            fail("ERR_F1K_CARRIERPROV",
                 "carrier %s (%s): bytes on disk (sha %s, %d B) != the "
                 "construction report's pin (sha %r, %r B) — the table "
                 "is not the constructed artifact"
                 % (what, name, got_sha, size, ent.get("sha256"),
                    ent.get("bytes")))
        nc_, nl_, D_, layers_ = _kaec_header_layers(p)
        if (nc_, D_, layers_) != (rep_nc, rep_D, rep_layers) or \
                nl_ != len(rep_layers or []):
            fail("ERR_F1K_CARRIERPROV",
                 "carrier %s (%s): KAEC header (nc=%d, nl=%d, D=%d, "
                 "layers=%r...) != the construction report's geometry "
                 "(nc=%r, D=%r, layers=%r...)"
                 % (what, name, nc_, nl_, D_, layers_[:8], rep_nc, rep_D,
                    (rep_layers or [])[:8]))
        if size != 16 + 4 * nl_ + 4 * nc_ * nl_ * D_:
            fail("ERR_F1K_CARRIERPROV",
                 "carrier %s (%s): file size %d != the exact KAEC fp32 "
                 "layout 16 + 4*nl + 4*nc*nl*D = %d"
                 % (what, name, size,
                    16 + 4 * nl_ + 4 * nc_ * nl_ * D_))
        if not mock:
            # [R10-2] REAL campaigns: full-coverage non-degeneracy — an
            # all-zero/constant/min-variance-floor body with a perfectly
            # coherent report is still never spliced.
            kaec_nondegeneracy_scan(p, what)
        checked[rp] = name
    rep_sha = sha256_file(rep_path)
    pins["carrier-construction-report.mode-%s" % mode] = {
        "observed": rep_sha}
    man_pin = {"observed": binding["manifest_sha256"]}
    if CONSTRUCTION_MANIFEST.is_file():
        man_pin["expected"] = sha256_file(CONSTRUCTION_MANIFEST)
    pins["carrier-construction-manifest"] = man_pin
    if kpath.is_file():
        pins["f1k-carriers-v1.k-true"] = {"observed": sha256_file(kpath)}
    disclosure = {
        "mode": mode,
        "construction_report": str(rep_path),
        "construction_report_sha256": rep_sha,
        "binding": binding,
        "tables_byte_witnessed": sorted(checked.values()),
        "registered_splice_layers_enforced": (not mock),
        "nondegeneracy_enforced": (not mock),
        "gate": "[R9-PROV] carrier re-review item 8 (2026-07-16): "
                "mode/D/layers/bindings verified fail-closed before "
                "ingest; provenance shas artifact-derived; tables "
                "byte-witnessed against the report. [R10] content "
                "authentication (2026-07-16 round-10): real bindings "
                "denylisted against the repo mock-stack digests; "
                "checkpoint_content_sha256 witness required; every "
                "witnessed table non-degeneracy-scanned full-coverage "
                "(all-zero/near-constant/min-variance bodies refused)",
    }
    return disclosure, pins


def verify_id_lists(cfg, items):
    """Freeze-manifest (A): guard/dev/test id-list hashes [REG
    harness_manifest '(A) ... guard/dev/test id-list hashes']. Hash =
    sha256 over '\\n'.join(sorted ids) + '\\n'."""
    want = (cfg.get("freeze") or {}).get("id_list_hashes") or {}
    for split in ("test", "dev", "guard"):
        ids = sorted(it["item_id"] for it in items[split])
        got = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
        if want.get(split) != got:
            fail("ERR_F1K_EVAL",
                 "%s id-list hash %s != freeze-manifest (A) commit %r "
                 "(the eval split is not the frozen id list)"
                 % (split, got, want.get(split)))
    return True


def load_eval_manifest(path):
    items = {"test": [], "dev": [], "guard": []}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                it = json.loads(line)
                for k in ("item_id", "split", "cluster", "gold_index",
                          "labels", "label_token_ids", "template_tokens",
                          "spans"):
                    if k not in it:
                        fail("ERR_F1K_EVAL",
                             "eval item missing %r: %s" % (k, line[:120]))
                if it["split"] not in items:
                    fail("ERR_F1K_EVAL", "bad split %r" % it["split"])
                if len(it["spans"]) != len(it["template_tokens"]):
                    fail("ERR_F1K_EVAL",
                         "spans/template length mismatch: %s" % it["item_id"])
                if len(it["labels"]) != len(it["label_token_ids"]):
                    fail("ERR_F1K_EVAL",
                         "labels/label_token_ids mismatch: %s" % it["item_id"])
                items[it["split"]].append(it)
    except (OSError, json.JSONDecodeError) as e:
        fail("ERR_F1K_EVAL", "cannot load eval manifest %s: %s" % (path, e))
    # frozen sizes [REG design.n_planned]
    if len(items["test"]) != N_TEST:
        fail("ERR_F1K_EVAL", "test split has %d items; the frozen design "
             "runs AT the cap n = %d (§R-REV3.1 item 4)"
             % (len(items["test"]), N_TEST))
    if len(items["dev"]) != DEV_N:
        fail("ERR_F1K_EVAL", "dev split has %d items != registered %d"
             % (len(items["dev"]), DEV_N))
    if len(items["guard"]) != GUARD_N:
        fail("ERR_F1K_EVAL", "guard split has %d items != registered %d"
             % (len(items["guard"]), GUARD_N))
    for it in items["guard"]:
        if any(s >= 0 for s in it["spans"]):
            fail("ERR_F1K_EVAL",
                 "guard item %s carries a gated span — the off-concept "
                 "guard must never fire the gate (§2.5)" % it["item_id"])
    for it in items["test"] + items["dev"]:
        if "d3_template_tokens" not in it:
            fail("ERR_F1K_EVAL",
                 "item %s lacks d3_template_tokens (the frozen d3-text "
                 "prompt-seam rendering, §2.6 arm d3-text)" % it["item_id"])
    return items


def check_power_gate(test_items):
    """[R6-2] [REG design.n_planned.power_gate / ASM-2369, RUN-HOLD
    EQUALITY form]: EXACTLY C_REGISTERED = 96 clusters, EACH with >= 8
    test items, at EXACTLY n = N_TEST = 1573 — byte-matches the pinned
    analysis/f1k.py /gates/power_gate_valid (n_clusters == 96 AND
    clusters-with-m>=8 == 96 AND n == 1573; never >=: a 97-cluster
    universe must FAIL here exactly as the analysis hard-rejects it).
    A shortfall is a PRE-RUN RETURN to the maintainer, never a run."""
    sizes = {}
    for it in test_items:
        sizes[it["cluster"]] = sizes.get(it["cluster"], 0) + 1
    c_ok = sum(1 for v in sizes.values() if v >= POWER_GATE_MIN_M)
    ok = (len(sizes) == C_REGISTERED and c_ok == C_REGISTERED
          and len(test_items) == N_TEST)
    return {"n_items": len(test_items), "n_clusters": len(sizes),
            "clusters_with_m_ge_8": c_ok,
            "gate": "n_clusters==%d AND clusters-with-m>=%d==%d AND n==%d "
                    "(EQUALITY form, ASM-2369 / RUN-HOLD fix; matches "
                    "analysis/f1k.py)"
                    % (C_REGISTERED, POWER_GATE_MIN_M, C_REGISTERED,
                       N_TEST),
            "pass": ok}


def validate_dose(carriers_cfg):
    """Dose-exactness preconditions [DES §R2 / REG sec-k2 endpoint]: the
    registered seeds EXACTLY [101,102,103], each derangement fixed-point-free,
    layerwise norm-matched (from the B0 pure-function addendum metadata).
    analysis/f1k.py re-gates this from the sidecar; the driver fails closed
    EARLY so no spend happens on a mis-dosed arm."""
    d1 = carriers_cfg.get("d1-drng") or {}
    seeds = sorted(int(s) for s in d1.keys())
    if seeds != list(DRNG_SEEDS):
        fail("ERR_F1K_DOSE", "d1-drng seeds %s != registered %s "
             "(f1k.json design.seeds)" % (seeds, list(DRNG_SEEDS)))
    for s in DRNG_SEEDS:
        meta = d1[str(s)].get("meta") or {}
        der = meta.get("derangement")
        if not isinstance(der, list) or sorted(der) != list(range(len(der))):
            fail("ERR_F1K_DOSE", "seed %d: derangement missing or not a "
                 "permutation (B0 addendum metadata required)" % s)
        if any(der[i] == i for i in range(len(der))):
            fail("ERR_F1K_DOSE", "seed %d: derangement has a fixed point "
                 "(§R2: no concept keeps its own carrier)" % s)
        if meta.get("layerwise_norm_matched") is not True:
            # [R3-ATTEST] strict `is True`: a truthy STRING here previously
            # laundered into the emitted dose attestation below
            fail("ERR_F1K_DOSE", "seed %d: layerwise_norm_matched is %r, "
                 "not the strict boolean true — the B0 addendum must attest "
                 "it as a genuine JSON boolean (§R2 rescale to "
                 "||v^K_{c,l}||; HOLD round-3 item 4)"
                 % (s, meta.get("layerwise_norm_matched")))
    # the emitted dose attestations are literal booleans PROVEN by the
    # strict checks above (derangement re-verified element-wise, norm
    # matching attested `is True`) — never coerced from config values
    return {"r_seeds": list(DRNG_SEEDS),
            "derangement_no_fixed_point": True,
            "norm_matched_within_tol": True}


SPEND_START_NAME = "spend-start.jsonl"


def write_spend_start(ledger, phase, arm, pass_no):
    """[ASM-2513 v4, round-3 #2] Durable SPEND-START sentinel: appended
    + fsynced (file AND directory entry) to the ledger's outdir BEFORE
    every metered engine Popen. Semantics: an engine spawn was
    ATTEMPTED under this outdir's ledger basis — so a hard interruption
    in the spawn-to-first-checkpoint window (child spent; only
    manifests/logs persisted) can never be followed by a silent
    fresh-ledger re-init (§1e predicate includes this file). Presence,
    not content, drives the predicate; the recorded line (phase/arm/
    pass + pin/cost basis) is forensics for the recovery decision.
    Fails closed: no spawn without a durable sentinel."""
    sp = ledger.path.parent / SPEND_START_NAME
    line = json.dumps({
        "event": "engine-spawn-attempt",
        "phase": phase, "arm": arm, "pass": pass_no,
        "ledger_basis": dict(
            {"pin_file_sha256":
                 ledger.d["expert_pinning"]["pin_file_sha256"],
             "PIN_GB": ledger.d["expert_pinning"]["PIN_GB"]},
            **{k: ledger.d[k] for k in ledger.COST_KEYS})},
        sort_keys=True)
    try:
        with open(sp, "a", encoding="utf-8") as sf:
            sf.write(line + "\n")
            sf.flush()
            os.fsync(sf.fileno())
        dfd = os.open(str(ledger.path.parent), os.O_RDONLY)
        try:
            os.fsync(dfd)      # the DIRENT too: a crash must not lose
        finally:               # a freshly created sentinel [MEASURED:
            os.close(dfd)      # file+dir fsync demo, this box
    except OSError as e:       # 2026-07-18]
        fail("ERR_F1K_COST",
             "cannot durably record the SPEND-START sentinel %s (%s) — "
             "an engine spawn without a durable spend mark would re-open "
             "the spawn-to-checkpoint crash window; no spawn without it "
             "[ASM-2513 v4 round-3 #2]" % (sp, e))


# ---------------------------------------------------------------------------
# Resume-safe cost/elapsed ledger
# ---------------------------------------------------------------------------
class Ledger:
    """[FIX-7] RESUME-SAFE cost/elapsed ledger [COST; REG budget_note: the
    ceiling resolves from the METERED spend recorded in the run's cost
    ledger]. Accumulates per-phase seconds + prefills in
    <outdir>/cost-ledger.json (atomic replace), so timing survives spot
    interruption and spans pilot + guard + test; construction hours,
    prior metered spend AND the prior spend's instance-hours are
    REQUIRED config inputs, never silent zeros."""

    COST_KEYS = ("spot_rate_usd_per_hour", "usd_spent_prior",
                 "prior_instance_hours", "construction_instance_hours")
    #   [REV-D 1d] prior_instance_hours (gate config-cost --prior-hours:
    #   failed construction sessions + metered pre-construction) is
    #   REQUIRED — dollars in usd_spent_prior may never travel without
    #   their hours, or failed-session time vanishes from the 900 h
    #   projection basis (round-3 verdict 1d). SCOPE: it feeds the
    #   addendum-(7) cap basis (add7_hours_basis) ONLY; the SIDECAR
    #   surface is UNCHANGED — the FROZEN pinned analysis enforces
    #   cost.instance_hours == construction + sum(phase_seconds)/3600
    #   (registered identity), so instance_hours() below stays as
    #   registered and prior hours enter the PRE-SPEND projection cap
    #   (cap-conservative), never the frozen ledger identity.

    def __init__(self, outdir, cfg):
        cost = cfg.get("cost") or {}
        for k in self.COST_KEYS:
            if k not in cost:
                fail("ERR_F1K_COST",
                     "config.cost.%s is REQUIRED (no silent zero prior "
                     "spend / construction time — review §9; REG "
                     "budget_note meters the ledger)" % k)
        base = {k: float(cost[k]) for k in self.COST_KEYS}
        for k in self.COST_KEYS:
            # [REV-E 3] finiteness defense-in-depth (round-4 verdict 4;
            # the landed PIN_GB defect class): a hand-edited NaN/inf in
            # a required cost key (Python json.loads accepts the bare
            # NaN literal [MEASURED]) poisons every downstream cap
            # comparison — nan > 900 is False, so an over-hours
            # campaign becomes GO. The gate's config-cost refuses
            # non-finite inputs at the parse; the Ledger refuses them
            # at init REGARDLESS of who wrote the config.
            if not math.isfinite(base[k]) or base[k] < 0 or (
                    k == "spot_rate_usd_per_hour" and base[k] <= 0):
                fail("ERR_F1K_COST",
                     "config.cost.%s = %r is not a finite %s number — "
                     "NaN/inf/contract-violating basis values fail "
                     "OPEN through cap comparisons; refused at Ledger "
                     "init [REV-E]"
                     % (k, cost[k],
                        "positive" if k == "spot_rate_usd_per_hour"
                        else "nonnegative"))
        base.update({"phase_seconds": {}, "prefills": {},
                     "expert_pinning": validate_pinning(cfg)})
        self.path = Path(outdir) / "cost-ledger.json"
        if self.path.exists():
            try:
                self.d = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                fail("ERR_F1K_COST", "corrupt cost ledger %s: %s"
                     % (self.path, e))
            for k in self.COST_KEYS:
                if float(self.d.get(k, -1)) != base[k]:
                    fail("ERR_F1K_COST",
                         "resume with a CHANGED cost basis: ledger %s=%r "
                         "vs config %r — amend the ledger deliberately, "
                         "never silently" % (k, self.d.get(k), base[k]))
            # [ASM-2513] resume: the realized engine attestation
            # (experts_pinned) carries over ONLY under the SAME pin
            # file AND the SAME PIN_GB; a changed pin OR budget at
            # resume is refused here — this ledger is the ONLY state
            # spanning pilot+guard+test, so this comparison (not the
            # per-phase [R10-4] bindings, which carry `phase` and never
            # compare across it) is what closes the phase-boundary
            # swap [v2, review #5]. A campaign never silently swaps
            # its pin or its budget mid-run.
            prev = self.d.get("expert_pinning") or {}
            if prev.get("pin_file_sha256") not in (
                    None, base["expert_pinning"]["pin_file_sha256"]):
                fail("ERR_F1K_PINNING",
                     "resume with a CHANGED pin stats-file: ledger "
                     "pin_file_sha256=%r vs config-derived %r — amend "
                     "the ledger deliberately, never silently "
                     "[ASM-2513/R10-4]"
                     % (prev.get("pin_file_sha256"),
                        base["expert_pinning"]["pin_file_sha256"]))
            if prev.get("PIN_GB") is not None and \
                    float(prev["PIN_GB"]) != \
                    base["expert_pinning"]["PIN_GB"]:
                fail("ERR_F1K_PINNING",
                     "resume with a CHANGED PIN_GB: ledger %r vs "
                     "config-derived %r — PIN_GB is fixed ONCE at "
                     "bring-up (DES §7.1:639) and may not drift at a "
                     "phase boundary (pilot/guard/test share THIS "
                     "ledger; the per-phase [R10-4] bindings cannot "
                     "see across it) [ASM-2513 v2 review #5]"
                     % (prev.get("PIN_GB"),
                        base["expert_pinning"]["PIN_GB"]))
            self.d["expert_pinning"] = base["expert_pinning"]
            if isinstance(prev.get("experts_pinned"), int) \
                    and not isinstance(prev.get("experts_pinned"), bool):
                self.d["expert_pinning"]["experts_pinned"] = \
                    prev["experts_pinned"]
        else:
            # [ASM-2513 v3, re-review #3] MISSING-LEDGER fail-closed:
            # this ledger is the ONLY state spanning pilot+guard+test
            # (§1e first hunk), so its ABSENCE while campaign evidence
            # exists means the cross-phase pin/budget comparison basis
            # was lost or deleted — re-initializing would let a changed
            # PIN_GB/pin enter guard/test uncompared. Refuse with the
            # recovery path named; a fresh ledger is legal ONLY on a
            # virgin outdir.
            # [v4, round-3 #2] the SPEND-START sentinel leads the
            # predicate: it is fsynced BEFORE every metered engine
            # spawn (§1d2), so even a hard interruption in the
            # spawn-to-first-checkpoint window — which persists only
            # manifests/logs, none of the seven artifact paths below —
            # leaves it behind; spend can never have occurred here
            # without it. NOT "any outdir artifact":
            # carrier-provenance.json legitimately precedes fresh-
            # ledger construction and is excluded.
            ev = [Path(outdir) / SPEND_START_NAME]     # [v4]
            ev += [Path(outdir) / "pilot" / q for q in
                   ("pilot-rows.jsonl", "pilot-gates.json",
                    "addendum-5-frozen-lg.json", "addendum-6-inputs.json",
                    "addendum-7-affordability.json")]
            ev.append(Path(outdir) / "test" / "rows.jsonl")
            found = [str(q) for q in ev if q.exists()]
            found += [str(q) for q in
                      sorted((Path(outdir) / "guard").glob("raw.*.jsonl"))]
            if found:
                fail("ERR_F1K_COST",
                     "cost-ledger.json is MISSING but campaign evidence "
                     "(SPEND-START sentinel and/or artifacts/"
                     "checkpoints) exists under %s (%s%s) — a "
                     "fresh ledger here would re-initialize the "
                     "cross-phase pin/budget basis silently. RECOVERY: "
                     "restore the atomic-replace-persisted "
                     "cost-ledger.json from the interrupted run, or "
                     "obtain a maintainer-authorized reset that "
                     "ARCHIVES the listed evidence first "
                     "[ASM-2513 v3 re-review #3 / v4 round-3 #2]"
                     % (outdir, "; ".join(found[:3]),
                        ", ..." if len(found) > 3 else ""))
            self.d = base
            self._write()
        # [R3-COST] a resumed/prior-spend ledger already over the ceiling
        # stops HERE — before a single new prefill
        self.enforce_cap("ledger init/resume")

    def _write(self):
        tmp = self.path.with_suffix(".json.tmp")
        write_json(tmp, self.d)
        os.replace(str(tmp), str(self.path))

    def add(self, phase, seconds, prefills):
        if seconds <= 0 and prefills <= 0:
            return
        ps = self.d["phase_seconds"]
        ps[phase] = ps.get(phase, 0.0) + float(seconds)
        pf = self.d["prefills"]
        pf[phase] = pf.get(phase, 0) + int(prefills)
        self._write()
        # [R3-COST] realized-cost stop AT ACCUMULATION (HOLD round-3 item
        # 6): the pre-test PROJECTION gate alone never re-checked the
        # ledger as real spend accrued — a slower-than-projected campaign
        # could meter past $155 and still emit a success record. Every
        # accumulation now enforces the registered ceiling; the spend is
        # RECORDED first (the ledger stays truthful), then the run STOPS.
        self.enforce_cap("accumulation (phase %s)" % phase)

    def enforce_cap(self, where):
        """[R3-COST] Fail-closed realized-ledger ceiling (REG budget.usd_cap
        = $155, ASM-2374): called at every accumulation AND at sidecar
        emission. Exceeding the cap STOPS the run (exit 2) — no success
        sidecar/run-record is ever emitted; the STOP is a
        return-to-maintainer, never a silent overrun."""
        usd = self.usd_total()
        if usd > USD_CAP:
            fail("ERR_F1K_COST_STOP",
                 "REALIZED ledger $%.2f EXCEEDS the registered $%.0f "
                 "ceiling at %s (ASM-2374) — STOP; no success record is "
                 "emitted; return to the maintainer with the metered "
                 "ledger %s [HOLD round-3 item 6]"
                 % (usd, USD_CAP, where, self.path))

    def phase_seconds(self, phase):
        return float(self.d["phase_seconds"].get(phase, 0.0))

    def phase_prefills(self, phase):
        return int(self.d["prefills"].get(phase, 0))

    def total_prefills(self):
        return sum(int(v) for v in self.d["prefills"].values())

    def run_hours(self):
        return sum(float(v) for v in self.d["phase_seconds"].values()) \
            / 3600.0

    def instance_hours(self):
        return self.d["construction_instance_hours"] + self.run_hours()

    def usd_total(self):
        return self.d["usd_spent_prior"] \
            + self.run_hours() * self.d["spot_rate_usd_per_hour"]


# ---------------------------------------------------------------------------
# Engine invocation (the §R1.1 scorer, one prefill per unit)
# ---------------------------------------------------------------------------
def manifest_line(item, arm):
    """One KAE_SCORE manifest line [PATCH run_kae_score]:
    T K t_0..t_{T-1} l_0..l_{K-1} s_0..s_{T-1}. The template is byte-identical
    across arms EXCEPT d3-text (kernel explication prepended as PROMPT TEXT,
    no splice [DES §2.6]); spans are the item's FROZEN sidecar, identical
    across arms and passes [DES §R1.1/§R-REV2.1]."""
    if arm == "d3-text":
        toks = item["d3_template_tokens"]
        spans = [-1] * len(toks)      # no splice arm: gate must not fire
    else:
        toks = item["template_tokens"]
        spans = item["spans"]
    K = len(item["label_token_ids"])
    parts = [str(len(toks)), str(K)]
    parts += [str(t) for t in toks]
    parts += [str(t) for t in item["label_token_ids"]]
    parts += [str(s) for s in spans]
    return " ".join(parts)


def arm_env(cfg, arm, seed, workdir, frozen, cache_off=False):
    """Environment for one (arm, pass) engine invocation. Splice arms set
    KAE=1 + the arm's carrier (subset to the frozen L) + KAE_G=frozen g
    [DES §R4: the frozen (L,g) applied IDENTICALLY to every spliced arm].
    REPLACE = the K carrier with KAE_MODE=1 [PATCH; §2.5]. Expert-pinning
    env is ENFORCED [FIX-5]; XCACHE is a clean pass-through seam [CACHE],
    forced OFF for the guard [CACHE ASM-2306]."""
    env = dict(os.environ)
    for k in list(env):
        if k.startswith("KAE") or k.startswith("XCACHE") \
                or k.startswith("MOCK"):
            del env[k]
    env.update({k: str(v) for k, v in
                (cfg["engine"].get("env") or {}).items() if v is not None})
    if cache_off:
        for k in list(env):
            if k.startswith("XCACHE"):
                del env[k]           # guard: no serve, no populate (ASM-2306)
    if arm in SPLICED_ARMS or arm == ARM_REPLACE:
        if arm == "d1-drng":
            master = cfg["carriers"]["d1-drng"][str(seed)]["path"]
            tag = "d1-drng-%d" % seed
        elif arm == ARM_REPLACE:
            # [FIX-3] REPLACE scores the SAME K carrier at the frozen (L,g),
            # with the engine's REPLACE mode armed [PATCH KAE_MODE].
            master = cfg["carriers"]["K"]["path"]
            tag = "K"
        else:
            master = cfg["carriers"][arm]["path"]
            tag = arm
        sub = os.path.join(workdir, "carriers-frozenL",
                           "%s.L-%s.kaec" % (tag,
                                             "-".join(map(str,
                                                          frozen["layers"]))))
        if not os.path.exists(sub):
            kaec_subset(master, frozen["layers"], sub)
        env["KAE"] = "1"
        env["KAE_CARRIER"] = sub
        env["KAE_G"] = repr(float(frozen["g"]))
        env["KAE_MODE"] = "1" if arm == ARM_REPLACE else "0"
        #   [PATCH: mode 0 = ADD; mode 1 = REPLACE — stubbed at gate 0,
        #    which run_scoring_pass's engagement + the pilot stub check
        #    refuse to score silently]
    else:
        env["KAE"] = "0"             # b0 / d3-text: unmodified engine
    return env


def parse_result_line(line, item):
    """[FIX-1] Locate a KAE_SCORE RESULT line by its frozen shape [PATCH
    run_kae_score: '<pred_label_index> <pred_token_id> <logit_l0> ..
    <logit_lK-1>'] validated against THIS item's label-token ids — the real
    engine prints startup banners to stdout first, so 'first line = result'
    is wrong. Returns (pred_idx, pred_tok, logits) or None (non-result)."""
    parts = line.split()
    K = len(item["label_token_ids"])
    if len(parts) != 2 + K:
        return None
    try:
        pred_idx = int(parts[0])
        pred_tok = int(parts[1])
        logits = [float(x) for x in parts[2:]]
    except ValueError:
        return None
    if not (0 <= pred_idx < K):
        return None
    if pred_tok != item["label_token_ids"][pred_idx]:
        return None
    return pred_idx, pred_tok, logits


KAE_ARMED_RE = re.compile(
    r"\[KAE\] ADD-path armed[^:]*: (\d+) concepts, (\d+) splice layers, "
    r"g=([0-9.eE+\-]+)")
#   [PATCH glm.c: fprintf(stderr, "[KAE] ADD-path armed (DRAFT/gate-0): %d
#    concepts, %d splice layers, g=%.3f; ...")]
KAE_DISABLED_MARKERS = (
    "KaE DISABLED", "[KAE] load failed", "[KAE] cannot open",
    "[KAE] bad carrier", "[KAE] short carrier", "[KAE] non-positive",
    "[KAE] carrier D=", "[KAE] nl=", "[KAE] alloc", "[KAE] splice layer",
    "[KAE] KAE=1 requires",
)
#   [PATCH kae.h/glm.c failure messages — ANY of these means the splice is
#    not armed and the run would silently score b0]
MAX_BANNER_LINES = 200


def check_kae_engagement(stderr_path, env, where):
    """[FIX-2] POSITIVE KaE-engagement verification from the captured engine
    stderr. A spliced (KAE=1) invocation REQUIRES the armed banner with
    matching (concepts, splice layers, g) and NO disabled marker; a
    baseline (KAE=0) invocation must NOT report an armed splice. Called
    BEFORE the first scored item is accepted (the armed/failed banner is
    emitted at engine load, ahead of any KAE_SCORE output) and re-checked
    at pass completion — a K/d0/d1/d2/REPLACE arm can never silently score
    as b0 [review blocker 2; DES §2.6 arm integrity]."""
    ENGAGEMENT_CHECKS["n"] += 1
    try:
        text = Path(stderr_path).read_text(encoding="utf-8",
                                           errors="replace")
    except OSError:
        text = ""
    armed = KAE_ARMED_RE.search(text)
    disabled = [m for m in KAE_DISABLED_MARKERS if m in text]
    if env.get("KAE") == "1":
        if disabled:
            fail("ERR_F1K_KAE_ENGAGE",
                 "%s: KaE reported DISABLED (%s) on a spliced arm — the "
                 "engine would silently run unmodified (b0); ABORTED "
                 "before scoring, item quarantined in-place (nothing "
                 "recorded). Fix the carrier/engine seam and resume."
                 % (where, disabled))
        if not armed:
            fail("ERR_F1K_KAE_ENGAGE",
                 "%s: no positive '[KAE] ADD-path armed' signal on engine "
                 "stderr for a spliced arm (stderr: %s) — fail closed; a "
                 "spliced arm must VERIFIABLY engage before any item is "
                 "scored" % (where, stderr_path))
        nc_rep, nl_rep = int(armed.group(1)), int(armed.group(2))
        g_rep = float(armed.group(3))
        hdr = kaec_header(env["KAE_CARRIER"])
        g_exp = float(env["KAE_G"])
        if nc_rep != hdr["nc"] or nl_rep != hdr["nl"]:
            fail("ERR_F1K_KAE_ENGAGE",
                 "%s: engine armed with (%d concepts, %d layers) != the "
                 "arm's carrier (%d, %d) — wrong table spliced"
                 % (where, nc_rep, nl_rep, hdr["nc"], hdr["nl"]))
        if abs(g_rep - g_exp) > 5.01e-4:   # engine prints g at %.3f
            fail("ERR_F1K_KAE_ENGAGE",
                 "%s: engine armed with g=%s != frozen g=%s"
                 % (where, g_rep, g_exp))
    else:
        if armed:
            fail("ERR_F1K_KAE_ENGAGE",
                 "%s: baseline (KAE=0) invocation reports an ARMED splice "
                 "— arm contamination, fail closed" % where)


PIN_ARMED_RE = re.compile(
    r"\[PIN\] hot-expert store armed: pinned (\d+) experts?, "
    r"([0-9.]+) GiB \(budget ([0-9.]+) GiB\) from (\S+)")
#   [MOCK mock_colibri.py pin banner. The REAL colibri pin-report wording
#    is FETCH-GRADE (ASM-1971) — re-verified from the checkout at the
#    bring-up knob-semantics re-verification (DES §7.1: "any semantic
#    surprise ... halts the run for a protocol amendment BEFORE data
#    collection, never after"). This driver is NOT sha-pinned (frozen
#    record: "f1k_driver.py, not sha-pinned here"), so aligning this
#    regex to the verified real banner is a recorded run-log amendment,
#    not a re-freeze; the PINNED analysis carries only the pin-file HASH
#    + counters, never the banner format — deliberately, so bring-up
#    format alignment cannot touch the frozen surface.]
PIN_DISABLED_MARKERS = (
    "[PIN] cannot open", "[PIN] malformed", "[PIN] no experts",
    "pinning DISABLED",
)
PIN_CHECKS = {"n": 0}


def check_pin_engagement(stderr_file, stderr_path, banner_text, env,
                         where, ledger=None, *, stderr_start):
    """[ASM-2513] POSITIVE pin-engagement verification: PIN=<stats-file>
    in the env REQUIRES a pin-armed banner (on captured stderr or the
    pre-result stdout banners) whose COUNTERS confirm a hot store
    actually loaded — verify, never trust the env flag [F4/
    F1K-AFFORDABILITY-DECISION.md §3; CONSTRUCTION-PLAN §5]. Mirrors
    [FIX-2]: called BEFORE the first scored item is accepted. Coherence:
    1 <= experts_pinned <= pin-file lines; the banner's used GiB is
    strictly positive; the banner's budget equals the validated PIN_GB
    (1% tolerance); the banner's source file is the validated pin file;
    the file bytes still hash to the ledger's pin_file_sha256 (no
    mid-run swap). Realized experts_pinned is recorded in the
    resume-safe ledger (and thence the sidecar via attested_pinning).
    [v2, review #2 — SECURITY] `stderr_start` is the BYTE OFFSET of the
    stderr log captured by run_scoring_pass AFTER opening the log and
    BEFORE spawning the engine: the log has a DETERMINISTIC filename
    and is opened in APPEND mode, so after an interruption it still
    holds a PRIOR invocation's armed banner — v1's whole-file scan let
    that stale banner authorize a NEW process that never armed (a false
    attestation, the exact channel this fix closes). Only the slice
    [stderr_start:] — bytes this invocation's engine wrote — plus this
    invocation's freshly collected stdout banners may satisfy the
    check. A log shorter than stderr_start (truncated under us) is
    refused outright.
    [v3, re-review #1 — SECURITY] The evidence is DESCRIPTOR-BOUND:
    `stderr_file` is the very file object whose descriptor the child
    inherited (Popen(stderr=errf) dups it), and the slice is read with
    os.fstat + os.pread ON THAT DESCRIPTOR — a rotation/replacement of
    the PATHNAME between spawn and check cannot substitute evidence
    (the v2 by-name Path.read_bytes() re-open could: a replacement of
    length >= stderr_start carrying a stale banner after the offset
    passed the short-file guard). `stderr_path` is retained for error
    messages ONLY. `stderr_start` is a REQUIRED keyword-only argument
    (the permissive =0 default is REMOVED): no call site can silently
    fall back to whole-file semantics. Concurrent-ownership honesty
    [best-effort, tagged]: §1d holds a non-blocking exclusive flock on
    the log descriptor for the whole invocation, which REFUSES a
    second cooperating driver instance on the same path (the realistic
    double-resume race, incl. same-inode openers); an UNCOOPERATIVE
    same-box writer appending a forged banner to the same inode is
    invisible to advisory locking — that residue is outside the threat
    model (such a writer could equally forge the pin file itself
    before hashing) and is named here, not hidden."""
    if not env.get("PIN"):
        fail("ERR_F1K_PINNING",
             "%s: engine env carries NO PIN at engagement time — "
             "pinning is MANDATORY (validate_pinning already passed at "
             "config load, so a missing PIN here means the env was "
             "corrupted between load and spawn); the engagement check "
             "is never silently skipped [ASM-2513 v2 review #2]" % where)
    PIN_CHECKS["n"] += 1
    # [v3, re-review #1] fstat + pread on the RETAINED descriptor —
    # never a by-name re-open (see docstring; requires the §1d "a+"
    # open mode: os.pread on a write-only "a" descriptor raises EBADF
    # [MEASURED, this box 2026-07-18])
    st = os.fstat(stderr_file.fileno())
    if stderr_start > st.st_size:
        fail("ERR_F1K_PINNING",
             "%s: stderr log %s (%d bytes at the retained descriptor) "
             "is SHORTER than the pre-spawn offset %d — the log was "
             "truncated under this invocation; no banner in it is "
             "attributable [ASM-2513 v2 review #2 / v3 re-review #1]"
             % (where, stderr_path, st.st_size, stderr_start))
    # ONLY the current invocation's slice of the SAME file object the
    # child wrote to — never a prior run's banner, never a pathname
    # decoy's bytes
    raw_slice = os.pread(stderr_file.fileno(),
                         st.st_size - stderr_start, stderr_start)
    text = raw_slice.decode("utf-8", errors="replace")
    text = text + "\n" + (banner_text or "")
    disabled = [m for m in PIN_DISABLED_MARKERS if m in text]
    if disabled:
        fail("ERR_F1K_PINNING",
             "%s: engine reported pinning DISABLED (%s) with PIN=%s — "
             "the run would stream UNPINNED while the ledger attests "
             "pinned (voids the ASM-2205/ASM-2374 $155 lever); fail "
             "closed [ASM-2513]" % (where, disabled, env.get("PIN")))
    m = PIN_ARMED_RE.search(text)
    if not m:
        fail("ERR_F1K_PINNING",
             "%s: no positive pin-armed banner for PIN=%s (stderr: %s) "
             "— a hot store was never verifiably loaded; a pinning "
             "attestation is never emitted on trust [ASM-2513]"
             % (where, env.get("PIN"), stderr_path))
    n_pinned, gb_used = int(m.group(1)), float(m.group(2))
    gb_budget, src = float(m.group(3)), m.group(4)
    if not gb_used > 0.0:
        # [v2, review #2] a banner attesting 0.000 GiB resident pinned
        # NOTHING regardless of its expert count — refuse (NaN also
        # fails this comparison)
        fail("ERR_F1K_PINNING",
             "%s: engine pin banner reports %.3f GiB used — a hot "
             "store holding zero bytes resident is not a pinned store; "
             "a pinning attestation is never emitted for it "
             "[ASM-2513 v2]" % (where, gb_used))
    rec = validate_pinning({"engine": {"env": dict(env)}})
    if src != rec["PIN"]:
        fail("ERR_F1K_PINNING",
             "%s: engine pinned from %r != the validated stats-file %r "
             "— wrong pin loaded [ASM-2513]" % (where, src, rec["PIN"]))
    if not 1 <= n_pinned <= rec["pin_file_lines"]:
        fail("ERR_F1K_PINNING",
             "%s: engine reports %d pinned experts vs a stats-file "
             "listing %d — incoherent counters (a zero or over-listed "
             "pin is not a verified hot store) [ASM-2513]"
             % (where, n_pinned, rec["pin_file_lines"]))
    if abs(gb_budget - rec["PIN_GB"]) > 0.01 * max(1.0, rec["PIN_GB"]) \
            or gb_used > gb_budget * 1.01:
        fail("ERR_F1K_PINNING",
             "%s: engine pin budget %.3f GiB / used %.3f GiB vs the "
             "validated PIN_GB=%.3f — budget mismatch (matched-budget "
             "discipline DES §7.1) [ASM-2513]"
             % (where, gb_budget, gb_used, rec["PIN_GB"]))
    if ledger is not None:
        lp = ledger.d["expert_pinning"].get("pin_file_sha256")
        if lp != rec["pin_file_sha256"]:
            fail("ERR_F1K_PINNING",
                 "%s: pin stats-file content hash %s != the ledger's "
                 "%s — the pin file changed MID-RUN; a campaign never "
                 "silently swaps its pin [ASM-2513/R10-4]"
                 % (where, rec["pin_file_sha256"], lp))
        ledger.d["expert_pinning"]["experts_pinned"] = n_pinned
        ledger._write()


def run_scoring_pass(cfg, items, arm, pass_no, seed, env, out_rows_path,
                     done_keys, ledger=None, mock_gold_dir=None,
                     phase="test", interrupt_state=None, store_raw=False,
                     auth=None):
    """Score `items` under one (arm, pass): ONE engine process, ONE prefill
    per item [DES §R1.1], streaming per-item checkpoint appends (a spot
    interruption resumes at item granularity [COST lever 1]). `auth` is the
    RowsAuth from read_ckpt_authed [R10-4]: every appended row line is
    absorbed + persisted in lockstep, so the checkpoint stays resumable
    ONLY by the run that produced it.
    Returns (n_scored, raw_output_lines_by_item_id)."""
    pending = [it for it in items
               if (arm, pass_no, it["item_id"]) not in done_keys]
    raw = {}
    if not pending:
        return 0, raw
    workdir = Path(out_rows_path).parent
    mdir = workdir / "manifests"
    mdir.mkdir(parents=True, exist_ok=True)
    mpath = mdir / ("%s.%s.pass%d.kae_score" % (phase, arm, pass_no))
    with open(mpath, "w", encoding="utf-8") as f:
        for it in pending:
            f.write(manifest_line(it, arm) + "\n")
    where = "%s/%s pass %d" % (phase, arm, pass_no)
    if env.get("KAE") == "1":
        # [FIX-2] span pre-validation against the carrier header: an
        # out-of-range concept id would make the engine print "ERR item"
        # (fatal below) and kae_bind_spans() reject — neither may be
        # reachable from frozen inputs; validate BEFORE spending.
        hdr = kaec_header(env["KAE_CARRIER"])
        for it in pending:
            bad = [s for s in it["spans"] if s >= hdr["nc"]]
            if bad:
                fail("ERR_F1K_SPANS",
                     "%s: item %s carries concept id(s) %s >= carrier "
                     "nc=%d — frozen spans must index the frozen table "
                     "(kae_bind_spans would reject; never scored silently)"
                     % (where, it["item_id"], bad[:4], hdr["nc"]))
    env = dict(env)
    env["KAE_SCORE"] = str(mpath)
    if mock_gold_dir is not None:
        gp = Path(mock_gold_dir) / (mpath.name + ".gold")
        with open(gp, "w") as f:
            f.write("\n".join(str(it["gold_index"]) for it in pending) + "\n")
        env["MOCK_GOLD"] = str(gp)
    argv = list(cfg["engine"].get("argv") or [])
    if not argv:
        fail("ERR_F1K_ENGINE", "engine.argv missing (colibri binary + args)")
    sdir = workdir / "stderr"
    sdir.mkdir(parents=True, exist_ok=True)
    stderr_path = sdir / ("%s.%s.pass%d.log" % (phase, arm, pass_no))
    errf = open(stderr_path, "a+", encoding="utf-8")
    # [ASM-2513 v3, re-review #1] "a+" (O_RDWR|O_APPEND), not "a":
    # check_pin_engagement reads its evidence back through THIS
    # descriptor (os.pread — which raises EBADF on a write-only "a"
    # fd [MEASURED, this box 2026-07-18]); append semantics for the
    # child are unchanged.
    try:
        fcntl.flock(errf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fail("ERR_F1K_PINNING",
             "%s/%s pass %d: stderr log %s is flock-held by ANOTHER "
             "LIVE invocation — concurrent ownership of the evidence "
             "log is REFUSED (the double-resume race); wait for or "
             "stop the other driver [ASM-2513 v3 re-review #1; "
             "advisory lock = cooperating-writer guarantee ONLY — "
             "honesty note in §1c docstring]"
             % (phase, arm, pass_no, stderr_path))
    # [ASM-2513 v2, review #2 / v3 re-review #1] pre-spawn BYTE
    # offset: the log filename is DETERMINISTIC and the file is opened
    # in APPEND mode, so after an interruption a PRIOR invocation's
    # armed banner is still in the file. Captured after open (which
    # creates the file) and BEFORE Popen — the engine's first byte
    # lands at exactly this offset — so check_pin_engagement can only
    # be satisfied by evidence THIS invocation's engine produced.
    # (v3: os.fstat on the DESCRIPTOR, not os.path.getsize(name) —
    # getsize re-binds to the pathname, the exact channel re-review #1
    # closes; not errf.tell(): text-mode tell() is an opaque cookie,
    # not a byte offset. The driver itself never writes to errf; the
    # flock above spans the child's lifetime because Popen dups this
    # fd — child and driver share ONE open file description.)
    err_start = os.fstat(errf.fileno()).st_size
    # [FIX-1] per-item label-logit + frozen-tie log (design DV: "tie-break
    # lowest label index, ties logged" [REG dependent_vars item_correct]).
    llog = open(workdir / ("label-logits.%s.jsonl" % phase), "a",
                encoding="utf-8")
    if ledger is not None:
        # [ASM-2513 v4, round-3 #2] durable SPEND-START sentinel,
        # fsynced BEFORE Popen: from the spawn onward the child can
        # SPEND before ANY of the seven §1e artifact/checkpoint paths
        # exists (the selected-rows checkpoint opens only at :1755) —
        # a hard interruption in that window previously left only
        # manifests (:1702) and logs (:1733/:1736), none of them
        # predicate sentinels, so a subsequently missing
        # cost-ledger.json fresh-inited silently. Now every METERED
        # spawn (ledger is not None — every campaign pass call site
        # carries ledger=ledger: :2123/:2180/:2676/:2741/:2745/
        # :2749/:2755; only unmetered mock/probe spawns pass None and
        # have no ledger basis to protect) is preceded by a durable
        # mark the §1e missing-ledger predicate includes. The helper
        # fails closed on OSError: no spawn without a durable sentinel.
        write_spend_start(ledger, phase, arm, pass_no)
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE,
                            stderr=errf, text=True)
    n = 0
    first_seen = False
    banners_here, banners_txt = 0, []
    t_last = time.monotonic()
    pend_prefills = 0

    def ledger_flush():
        nonlocal t_last, pend_prefills
        if ledger is not None:
            now = time.monotonic()
            ledger.add(phase, now - t_last, pend_prefills)
            t_last = now
            pend_prefills = 0

    try:
        with open(out_rows_path, "a", encoding="utf-8") as rf:
            for it in pending:
                parsed = None
                line = ""
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        fail("ERR_F1K_ENGINE",
                             "engine ended early at %s item %s"
                             % (where, it["item_id"]))
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("ERR"):
                        fail("ERR_F1K_ENGINE",
                             "engine rejected item %s (%s) — frozen items "
                             "must never fail; this is a harness/pin defect"
                             % (it["item_id"], line))
                    parsed = parse_result_line(line, it)   # [FIX-1]
                    if parsed is not None:
                        break
                    # non-result stdout: startup banners are legal ONLY
                    # before the first result line [FIX-1]
                    if first_seen:
                        fail("ERR_F1K_ENGINE",
                             "%s: unexpected non-result stdout line AFTER "
                             "scoring began: %r" % (where, line[:160]))
                    banners_here += 1
                    banners_txt.append(line)     # [ASM-2513] pin banner
                    #   may legally ride the pre-result stdout banners
                    BANNERS_SKIPPED["n"] += 1
                    if banners_here > MAX_BANNER_LINES:
                        fail("ERR_F1K_ENGINE",
                             "%s: >%d non-result stdout lines before the "
                             "first KAE_SCORE result — not a scoring engine"
                             % (where, MAX_BANNER_LINES))
                if not first_seen:
                    first_seen = True
                    errf.flush()
                    check_kae_engagement(stderr_path, env, where)  # [FIX-2]
                    check_pin_engagement(errf, stderr_path,        # [ASM-
                                         "\n".join(banners_txt),   #  2513]
                                         env, where, ledger=ledger,
                                         stderr_start=err_start)   # [v3 #1]
                pred_idx, pred_tok, logits = parsed
                # [FIX-1] frozen tie information: re-assert the engine's
                # deterministic lowest-index tie-break [PATCH
                # kae_argmax_label strict >; REG dependent_vars] and LOG.
                mx = max(logits)
                tie_idx = [i for i, v in enumerate(logits) if v == mx]
                if pred_idx != tie_idx[0]:
                    fail("ERR_F1K_SCORER",
                         "%s item %s: engine pred index %d != frozen "
                         "lowest-index argmax %d over the logged label "
                         "logits — scorer readout defect"
                         % (where, it["item_id"], pred_idx, tie_idx[0]))
                if len(tie_idx) > 1:
                    TIES_LOGGED["n"] += 1
                llog.write(json.dumps({
                    "phase": phase, "arm": arm, "pass": pass_no,
                    "item_id": it["item_id"],
                    "pred_index": pred_idx, "pred_token_id": pred_tok,
                    "label_logits": logits,
                    "tie": len(tie_idx) > 1,
                    "tie_label_indices": tie_idx if len(tie_idx) > 1 else [],
                }, sort_keys=True) + "\n")
                llog.flush()
                raw[it["item_id"]] = line
                row = {
                    "item_id": it["item_id"],
                    "cluster": it["cluster"],
                    "arm": arm,
                    "pass": pass_no,
                    "correct": int(pred_idx == it["gold_index"]),
                    "pred_label": it["labels"][pred_idx],
                    "gold_label": it["labels"][it["gold_index"]],
                    "tags": it.get("tags") or [],
                }
                if store_raw:
                    # guard/dev raw persistence: byte-identity + stub
                    # comparisons survive a resume
                    row["raw"] = line
                row_line = json.dumps(row, sort_keys=True)
                rf.write(row_line + "\n")
                rf.flush()
                os.fsync(rf.fileno())
                if auth is not None:
                    # [R10-4] auth state updated in lockstep (rows first,
                    # then auth: a kill between the two leaves at most one
                    # uncovered trailing row, which resume DROPS+re-scores)
                    auth.absorb(row_line)
                    auth.write()
                done_keys.add((arm, pass_no, it["item_id"]))
                n += 1
                pend_prefills += 1
                if n % 25 == 0:
                    ledger_flush()             # [FIX-7] survives a kill -9
                if interrupt_state is not None:
                    interrupt_state["count"] += 1
                    if interrupt_state["count"] >= interrupt_state["after"]:
                        raise MockInterrupt()
        errf.flush()
        check_kae_engagement(stderr_path, env, where)   # [FIX-2] re-assert
    finally:
        ledger_flush()
        try:
            proc.stdout.close()
        except OSError:
            pass
        proc.terminate()
        proc.wait()
        errf.close()
        llog.close()
    return n, raw


class MockInterrupt(Exception):
    """Simulated spot interruption (mock resume validation only)."""


def read_ckpt(rows_path):
    """Resume state = the rows file itself; tolerate a torn final line
    (interrupted mid-write), never a torn middle line."""
    done, rows = set(), []
    p = Path(rows_path)
    if not p.exists():
        return done, rows
    lines = p.read_text(encoding="utf-8").splitlines()
    good = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                break                      # torn tail from an interruption
            fail("ERR_F1K_CKPT", "corrupt checkpoint row mid-file: %s"
                 % line[:120])
        key = (r["arm"], r["pass"], r["item_id"])
        if key in done:
            fail("ERR_F1K_CKPT", "duplicate checkpoint row %s" % (key,))
        done.add(key)
        good.append(line)
        rows.append(r)
    p.write_text("\n".join(good) + ("\n" if good else ""), encoding="utf-8")
    return done, rows


# ---------------------------------------------------------------------------
# [R10-4] Campaign checkpoint/resume AUTHENTICATION (carrier re-review
# content gap 4, 2026-07-16). read_ckpt alone treated ANY well-formed
# rows.jsonl as completed work, so a pre-fabricated/foreign rows file could
# bypass carrier/engine execution entirely (phase_test would score nothing
# and emit a sidecar over rows no engine produced). Now every scoring
# checkpoint file carries a sidecar auth state (<rows>.auth.json):
#   binding     the CURRENT run's pinned inputs (carrier K table +
#               construction report + engine argv/file digests + eval
#               manifest + phase) — a resume under different inputs is a
#               FOREIGN run and is refused;
#   rows_sha256 a running content hash (sha256, domain kot-f1k-rows-auth/1)
#               over the exact row lines the driver itself wrote, updated
#               in lockstep with every fsync'd row append;
#   n_rows      the number of rows the hash covers.
# On resume the stored binding must EQUAL the recomputed current binding
# and the hash of the first n_rows lines must EQUAL rows_sha256; rows
# beyond n_rows (a tail the auth state never covered — at most the torn
# write of an interruption) are DROPPED and re-scored, never trusted.
# Rows present with NO auth state = unauthenticated resume, refused.
# ---------------------------------------------------------------------------
def rows_auth_path(rows_path):
    return Path(str(rows_path) + ".auth.json")


def campaign_resume_binding(cfg, phase):
    """The pinned-input binding [R10-4] a resume must match. Pure function
    of the loaded config + on-disk pinned artifacts; deterministic across
    invocations of the same run."""
    b = {"domain": ROWS_AUTH_DOMAIN, "phase": str(phase)}
    kpath = Path(((cfg.get("carriers") or {}).get("K") or {})
                 .get("path") or "")
    if kpath.is_file():
        b["k_table_sha256"] = sha256_file(kpath)
    rep = kpath.parent / "construction-report.json"
    if rep.is_file():
        b["construction_report_sha256"] = sha256_file(rep)
    evp = cfg.get("eval_manifest")
    if evp and Path(evp).is_file():
        b["eval_manifest_sha256"] = sha256_file(evp)
    argv = [str(a) for a in ((cfg.get("engine") or {}).get("argv") or [])]
    b["engine_argv"] = argv
    b["engine_file_sha256"] = {a: sha256_file(a) for a in argv
                               if Path(a).is_file()}
    # [ASM-2513 / R10-4 extension; F1K-CONSTRUCTION-PLAN.md §5 item 5]:
    # the pin identity is a pinned input of the run — every resume (and
    # any future multi-VM shard) re-derives the pin-file hash FROM BYTES
    # via validate_pinning and must MATCH the auth state, so a swapped
    # pin can never silently resume; mismatch fails closed exactly like
    # a foreign engine (ERR_F1K_RESUME binding mismatch).
    ep = validate_pinning(cfg)
    b["pin_file_sha256"] = ep["pin_file_sha256"]
    b["pin_gb"] = ep["PIN_GB"]
    return b


class RowsAuth:
    """Running rows-content authenticator [R10-4]; absorb() every row line
    the driver writes, write() persists atomically in lockstep."""

    def __init__(self, rows_path, binding):
        self.path = rows_auth_path(rows_path)
        self.binding = binding
        self.h = hashlib.sha256((ROWS_AUTH_DOMAIN + "\n").encode("utf-8"))
        self.n = 0

    def absorb(self, line):
        self.h.update(line.encode("utf-8") + b"\n")
        self.n += 1

    def write(self):
        tmp = Path(str(self.path) + ".tmp")
        tmp.write_text(json.dumps(
            {"binding": self.binding, "n_rows": self.n,
             "rows_sha256": self.h.hexdigest()}, sort_keys=True) + "\n",
            encoding="utf-8")
        tmp.rename(self.path)


def read_ckpt_authed(rows_path, binding):
    """read_ckpt + [R10-4] authentication. Returns (done, rows, auth); the
    returned RowsAuth is primed with the authenticated content and MUST be
    handed to run_scoring_pass so new rows stay covered."""
    read_ckpt(rows_path)              # torn-tail repair + duplicate check
    p = Path(rows_path)
    lines = [ln for ln in (p.read_text(encoding="utf-8").splitlines()
                           if p.exists() else []) if ln.strip()]
    ap = rows_auth_path(rows_path)
    auth = RowsAuth(rows_path, binding)
    if lines and not ap.exists():
        fail("ERR_F1K_RESUME",
             "%s carries %d completed row(s) but NO auth state (%s) — an "
             "unauthenticated resume could skip carrier/engine execution "
             "entirely; refusing fail-closed. Delete the foreign rows "
             "file (re-scoring is checkpoint-cheap) or restore the auth "
             "state written by the run that produced it "
             "([R10-4] carrier re-review content gap 4)"
             % (rows_path, len(lines), ap))
    if ap.exists():
        try:
            st = json.loads(ap.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fail("ERR_F1K_RESUME",
                 "cannot read resume auth state %s: %s — refusing an "
                 "unauthenticated resume [R10-4]" % (ap, e))
        if st.get("binding") != binding:
            got, want = st.get("binding") or {}, binding
            diff = sorted(k for k in set(got) | set(want)
                          if got.get(k) != want.get(k))
            fail("ERR_F1K_RESUME",
                 "%s was produced under DIFFERENT pinned inputs than this "
                 "run (binding mismatch on %s) — rows from a foreign run "
                 "are never resumed into this one [R10-4]"
                 % (rows_path, ", ".join(diff) or "(shape)"))
        n = st.get("n_rows")
        if not isinstance(n, int) or isinstance(n, bool) or n < 0 \
                or n > len(lines):
            fail("ERR_F1K_RESUME",
                 "resume auth state %s covers n_rows=%r but %s carries "
                 "only %d row(s) — the auth state does not describe this "
                 "file; refusing [R10-4]" % (ap, n, rows_path, len(lines)))
        for ln in lines[:n]:
            auth.absorb(ln)
        if auth.h.hexdigest() != st.get("rows_sha256"):
            fail("ERR_F1K_RESUME",
                 "%s content hash %s != the auth state's rows_sha256 %r "
                 "over the first %d row(s) — the completed-rows content "
                 "was tampered with/replaced; a resume can never inject "
                 "rows the engine did not produce [R10-4]"
                 % (rows_path, auth.h.hexdigest(),
                    st.get("rows_sha256"), n))
        if n < len(lines):
            print("[R10-4] %s: dropping %d unauthenticated trailing "
                  "row(s) beyond the auth-covered %d (torn/injected tail "
                  "— re-scored, never trusted)"
                  % (rows_path, len(lines) - n, n))
            p.write_text("\n".join(lines[:n]) + ("\n" if n else ""),
                         encoding="utf-8")
            lines = lines[:n]
    done, rows = set(), []
    for ln in lines:
        r = json.loads(ln)
        done.add((r["arm"], r["pass"], r["item_id"]))
        rows.append(r)
    auth.write()
    return done, rows, auth


# ---------------------------------------------------------------------------
# PHASES
# ---------------------------------------------------------------------------
def load_frozen_lg(cfg, outdir):
    frozen = cfg.get("frozen_lg")
    if frozen is None:
        add5 = Path(outdir) / "pilot" / "addendum-5-frozen-lg.json"
        if add5.exists():
            frozen = json.loads(add5.read_text())["frozen"]
    if not frozen or "layers" not in frozen or "g" not in frozen:
        fail("ERR_F1K_FREEZE",
             "no frozen (L,g): run --phase pilot first (addendum (5) is a "
             "deterministic argmax of the pilot output, §R-REV2.4) or supply "
             "config.frozen_lg from the committed addendum")
    return frozen


def main_arm_passes(d3_deferred=False, replace_run=False):
    """The frozen main-arm pass list [REG design.n_planned.scoring_passes:
    b0, d0, d1-drng x3, d2, d3-text, K = 8 passes, +1 conditional REPLACE].
    [FIX-4] d3-text is EXCLUDED when the §R6 step-3 affordability deferral
    fired (execution honors the deferral, not just the projection).
    [FIX-3] REPLACE is INCLUDED when the §R-REV4.3 NI gate decided RUN."""
    passes = []
    for arm in ARMS_MAIN:
        if arm == "d3-text" and d3_deferred:
            continue
        if arm == "d1-drng":
            for i, s in enumerate(DRNG_SEEDS, start=1):
                passes.append((arm, i, s))
        else:
            passes.append((arm, 0, None))
    if replace_run:
        passes.append((ARM_REPLACE, 0, None))
    return passes


def read_replace_decision(outdir):
    """The committed REPLACE RUN/DEFER decision from pilot addendum (6)
    [FIX-3]. Guard/test phases derive their schedule from it."""
    p = Path(outdir) / "pilot" / "addendum-6-inputs.json"
    if not p.exists():
        fail("ERR_F1K_ORDER",
             "pilot addendum (6) inputs missing (%s): run --phase pilot "
             "first — the REPLACE run/defer gate is decided there "
             "(§R-REV4.3)" % p)
    rg = (json.loads(p.read_text(encoding="utf-8"))
          .get("replace_gate")) or {}
    if rg.get("decision") not in ("RUN", "DEFER"):
        fail("ERR_F1K_REPLACE", "addendum-6 replace_gate.decision %r not in "
             "RUN/DEFER" % (rg.get("decision"),))
    return rg


def read_d3_deferral(outdir):
    """[FIX-4] The committed d3-text deferral flag from addendum (7)."""
    p = Path(outdir) / "pilot" / "addendum-7-affordability.json"
    if not p.exists():
        fail("ERR_F1K_ORDER",
             "pilot addendum (7) missing (%s): run --phase pilot first" % p)
    # [R3-ATTEST] strict read: a malformed/tampered addendum never coerces
    return attest_bool(json.loads(p.read_text(encoding="utf-8"))
                       .get("d3_text_deferred"),
                       "addendum-7 d3_text_deferred")


def phase_guard(cfg, ev, outdir, frozen, replace_run, ledger,
                mock_gold_dir=None):
    """Off-concept byte-identity guard [DES §2.5; REG kill_criterion: any
    mismatch VOIDS the run]. Every spliced arm at the frozen (L,g) on the
    60 guard items — REPLACE included when scheduled [FIX-3] — engine
    output lines must equal b0's byte-for-byte (the gate never fires, so
    the splice must be a no-op). d3-text is excluded: it has no splice and
    a different (frozen) prompt. XCACHE forced OFF in both directions
    [CACHE ASM-2306]."""
    gdir = Path(outdir) / "guard"
    gdir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    passes = main_arm_passes(d3_deferred=True, replace_run=replace_run)
    gbind = campaign_resume_binding(cfg, "guard")     # [R10-4]
    for arm, pass_no, seed in passes:
        env = arm_env(cfg, arm, seed, str(gdir), frozen, cache_off=True)
        raw_path = gdir / ("raw.%s.pass%d.jsonl" % (arm, pass_no))
        # resume-safe per pass; [R10-4] authenticated (a fabricated raw
        # file would otherwise skip the byte-identity instrument itself)
        done, _, auth = read_ckpt_authed(raw_path, gbind)
        run_scoring_pass(
            cfg, ev["guard"], arm, pass_no, seed, env, raw_path, done,
            ledger=ledger, mock_gold_dir=mock_gold_dir, phase="guard",
            store_raw=True, auth=auth)
        # rebuild the FULL raw map from the checkpoint file (resume-safe)
        _, rows = read_ckpt(raw_path)
        if len(rows) != GUARD_N:
            fail("ERR_F1K_GUARD", "guard pass %s/%d scored %d/%d items"
                 % (arm, pass_no, len(rows), GUARD_N))
        outputs[(arm, pass_no)] = {r["item_id"]: r["raw"] for r in rows}
    base = outputs[("b0", 0)]
    mismatches = []
    for (arm, pass_no), rawmap in outputs.items():
        if arm == "b0":
            continue
        for iid, line in rawmap.items():
            if base.get(iid) != line:
                mismatches.append({"item_id": iid, "arm": arm,
                                   "pass": pass_no})
    report = {
        "n_items": GUARD_N,
        "passes_compared": ["%s/pass%d" % (a, p) for a, p, _ in passes
                            if a != "b0"],
        "byte_identical": not mismatches,
        "mismatches": mismatches,
        "xcache": "forced OFF both directions (no serve, no populate) "
                  "[glm52-expert-cache.md ASM-2306]",
        "rule": "any mismatch VOIDS the run (INSTRUMENT-INVALID), "
                "f1k.json kill_criterion_verbatim / design §2.5",
    }
    write_json(gdir / "guard-report.json", report)
    if mismatches:
        fail("ERR_F1K_GUARD", "off-concept byte-identity VIOLATED on %d "
             "(item, arm) pairs — run VOID; see %s"
             % (len(mismatches), gdir / "guard-report.json"))
    print("guard: %d items x %d spliced passes byte-identical to b0 -> OK"
          % (GUARD_N, len(passes) - 1))
    return report


def phase_test(cfg, ev, outdir, frozen, passes, ledger, mock_gold_dir=None,
               interrupt_state=None):
    """The main campaign: items x arms x passes, one §R1.1 prefill per unit,
    per-item checkpoint/resume. The pass list is COMMITTED (from the pilot
    addenda: d3 deferral [FIX-4] + REPLACE decision [FIX-3]). Emits rows in
    analysis/f1k.py's EXACT row schema [ANA docstring 'ROWS (JSONL)']."""
    tdir = Path(outdir) / "test"
    tdir.mkdir(parents=True, exist_ok=True)
    rows_path = tdir / "rows.jsonl"
    # [R10-4] authenticated resume: completed rows are consumed ONLY when
    # their content hash + pinned-input binding match this run
    done, _, auth = read_ckpt_authed(rows_path,
                                     campaign_resume_binding(cfg, "test"))
    n_new = 0
    expected = N_TEST * len(passes)
    for arm, pass_no, seed in passes:
        env = arm_env(cfg, arm, seed, str(tdir), frozen)
        n, _ = run_scoring_pass(cfg, ev["test"], arm, pass_no, seed, env,
                                rows_path, done, ledger=ledger,
                                mock_gold_dir=mock_gold_dir, phase="test",
                                interrupt_state=interrupt_state, auth=auth)
        n_new += n
        print("test: arm=%s pass=%d scored %d new (total done %d/%d)"
              % (arm, pass_no, n, len(done), expected))
    if len(done) != expected:
        fail("ERR_F1K_TEST", "campaign incomplete or off-schedule: %d/%d "
             "units for the committed pass list %s"
             % (len(done), expected, [(a, p) for a, p, _ in passes]))
    return rows_path, n_new


# ---- KOT-ADD7-SHARED-BEGIN ------------------------------------------------
# [REV-C F5i, F1K-BRINGUP-GATE-FIX.md SSC] ONE projection-model
# implementation, byte-identical in poc/gcp/f1k_bringup_gate.py and
# poc/glm52-probe/f1k-harness/f1k_driver.py. Each copy is verified at
# runtime: block sha256 == the in-file ADD7_SRC_SHA256 constant AND (at
# consumption) == the licensed gate artifact's model_bundle.add7_src_sha256
# — drift in EITHER copy is a refusal, never a silent second
# implementation. Semantics (frozen, fix memo SS2.6): piecewise-linear in T
# over isotonic knots; below the min knot central/hi are CONSTANT
# (cap-conservative) and the lo band extrapolates floored at
# floor_frac*s(minknot); above the max sampled knot: Add7RangeError
# (extrapolation above the frozen sample is FORBIDDEN — the campaign max-T
# text is in the sample by construction).
class Add7RangeError(ValueError):
    """T above the max sampled knot — never extrapolated."""


def add7_interp(knots, sfield, t, below="const", floor_frac=0.35):
    ts = [k["T"] for k in knots]
    ss = [k[sfield] for k in knots]
    if t > ts[-1] + 1e-9:
        raise Add7RangeError(
            "T=%.0f above max sampled knot %.0f" % (t, ts[-1]))
    if t <= ts[0]:
        if below == "const" or len(ts) < 2:
            return ss[0]
        slope = (ss[1] - ss[0]) / max(1e-9, ts[1] - ts[0])
        return max(floor_frac * ss[0], ss[0] - slope * (ts[0] - t))
    for i in range(len(ts) - 1):
        if t <= ts[i + 1]:
            frac = (t - ts[i]) / max(1e-9, ts[i + 1] - ts[i])
            return ss[i] + frac * (ss[i + 1] - ss[i])
    return ss[-1]


def add7_block_sha256(path):
    """sha256 over the exact lines BETWEEN the shared-block markers
    (marker lines excluded); None when the markers are absent/ambiguous."""
    lines = open(path, encoding="utf-8").read().split("\n")
    beg = [i for i, l in enumerate(lines)
           if l.startswith("# ---- KOT-ADD7-SHARED-BEGIN")]
    end = [i for i, l in enumerate(lines)
           if l.startswith("# ---- KOT-ADD7-SHARED-END")]
    if len(beg) != 1 or len(end) != 1 or end[0] <= beg[0]:
        return None
    body = "\n".join(lines[beg[0] + 1:end[0]])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
# ---- KOT-ADD7-SHARED-END --------------------------------------------------


ADD7_SRC_SHA256 = "9d3e1bc76f8506d99a29b0465af2c063b32ba8d726e7ec2c6a65e3c596260353"
#   [REV-C F5i] frozen sha256 of the KOT-ADD7-SHARED block body (both
#   copies must hash to THIS value; the gate refuses to emit an artifact
#   from a drifted copy, and this driver refuses to consume one).
ADD7_GATE_SCHEMA = "kot-f1k-bringup-gate/2"
#   [REV-C F5ii] the ONLY consumable gate-artifact schema: /2 adds the
#   REQUIRED model_bundle binding (add7_src_sha256 + tokens_full_sha256).


def add7_hours_basis(led_d, pilot_s):
    """[REV-D 1d] the addendum-(7) 900 h projection's realized-hours
    basis: PRIOR instance hours (failed construction sessions + metered
    pre-construction — gate config-cost --prior-hours) + licensed
    construction hours + realized pilot hours. Module level so the $0
    mock exercises the SAME basis phase_pilot uses. NOT the sidecar
    identity: the frozen analysis pins cost.instance_hours ==
    construction + sum(phase_seconds)/3600; prior hours enter the
    pre-spend cap projection only (cap-conservative)."""
    return (float(led_d["prior_instance_hours"])
            + float(led_d["construction_instance_hours"])
            + pilot_s / 3600.0)


def add7_cap_breach(p4, rate):
    """[REV-C] reserve-inclusive cap test at central AND +1SE (module
    level so the $0 mock exercises the degradation boundary with the
    SAME predicate phase_pilot uses)."""
    u_c, u_hi, h_c, h_hi = p4
    reserve_h = RESERVE_USD_ADD7 / rate
    return (u_c + RESERVE_USD_ADD7 > USD_CAP
            or u_hi + RESERVE_USD_ADD7 > USD_CAP
            or h_c + reserve_h > WALL_CLOCK_CAP_HOURS
            or h_hi + reserve_h > WALL_CLOCK_CAP_HOURS)


class Add7Model:
    """[REV-B GAP-3b / gate-fix review #1; ASM-2516 / REV-C ASM-2517] The
    FROZEN bring-up gate projection model (kot-f1k-bringup-gate/2,
    model-bundle-BOUND) consumed at the
    pilot->main seam — ONE projection model, stated once (ASM-2514/2515),
    used by BOTH seams. Inputs (config.affordability, REQUIRED for a real
    campaign, every path sha-verified fail-closed):
      tokens_full_path/_sha256   the gate run's tokens-full.jsonl sidecar
                                 (per-item T for every frozen text; its
                                 sha is recorded in bringup-gate.json)
      gate_artifact_path/_sha256 the GREEN bringup-gate.json (isotonic
                                 knots + cont addend + SE rule)
    The seam RE-LEVELS the frozen s_hat(T) SHAPE by kappa = realized pilot
    s/prefill DIVIDED BY the model-predicted pilot blend (prefill-weighted
    over the pilot population), then sums PER ITEM over the remaining
    main/guard prefills at their measured token counts — never one blended
    average times a prefill count (v3-review finding 3 lineage). kappa
    outside ADD7_KAPPA_BOUNDS on a REAL artifact -> fail-closed (model
    does not transfer). Below the min knot: CONSTANT (cap-conservative);
    above the max knot: fail-closed (the campaign max-T text was sampled
    by construction). Mirrors f1k_bringup_gate.project exactly."""

    def __init__(self, cfg):
        blk = cfg.get("affordability") or {}
        for k in ("tokens_full_path", "tokens_full_sha256",
                  "gate_artifact_path", "gate_artifact_sha256"):
            if not blk.get(k):
                fail("ERR_F1K_AFFORD",
                     "config.affordability.%s is REQUIRED [REV-B "
                     "ASM-2516]: the addendum-(7) projection consumes the "
                     "FROZEN bring-up gate model + per-item token counts "
                     "— no silent fallback to a blended average" % k)
        for pk, sk in (("tokens_full_path", "tokens_full_sha256"),
                       ("gate_artifact_path", "gate_artifact_sha256")):
            got = sha256_file(blk[pk])
            if got != blk[sk]:
                fail("ERR_F1K_AFFORD",
                     "affordability input %s sha %s != declared %s — the "
                     "seam never consumes unverified model inputs"
                     % (blk[pk], got, blk[sk]))
        art = json.loads(Path(blk["gate_artifact_path"])
                         .read_text(encoding="utf-8"))
        self.mock = (art.get("tokenizer") or {}).get("mode") != "REAL"
        if self.mock and blk.get("_allow_mock") is not True:
            fail("ERR_F1K_AFFORD",
                 "gate artifact tokenizer mode is not REAL and "
                 "_allow_mock is unset — a mock gate model never enters "
                 "a real campaign projection")
        # ---- [REV-C F5ii] the WHOLE bundle must be the LICENSED one —
        # a self-consistent config pointing at non-licensed bytes is
        # refused on the ARTIFACT-recorded identities, never trusted:
        if art.get("schema") != ADD7_GATE_SCHEMA:
            fail("ERR_F1K_AFFORD",
                 "gate artifact schema %r != %s — only a /2 model-bundle-"
                 "bound artifact is consumable [REV-C]"
                 % (art.get("schema"), ADD7_GATE_SCHEMA))
        if art.get("verdict") != "GREEN":
            fail("ERR_F1K_AFFORD",
                 "gate artifact verdict %r — a non-GREEN gate never "
                 "drives the pilot->main projection [REV-C]"
                 % art.get("verdict"))
        mb = art.get("model_bundle") or {}
        if mb.get("tokens_full_sha256") != blk["tokens_full_sha256"]:
            fail("ERR_F1K_AFFORD",
                 "config-declared sidecar sha %r != the ARTIFACT-recorded "
                 "model_bundle.tokens_full_sha256 %r — the config binds "
                 "whatever the ARTIFACT licensed, not what it declares "
                 "about itself [REV-C F5ii]"
                 % (blk["tokens_full_sha256"][:16],
                    (mb.get("tokens_full_sha256") or "")[:16]))
        own = add7_block_sha256(__file__)
        if own != ADD7_SRC_SHA256 or mb.get("add7_src_sha256") != own:
            fail("ERR_F1K_AFFORD",
                 "shared-model identity broken (own block %r, frozen %s, "
                 "artifact %r) — ONE model implementation, sha-verified; "
                 "a drifted copy never projects [REV-C F5i]"
                 % (own and own[:16], ADD7_SRC_SHA256[:16],
                    (mb.get("add7_src_sha256") or "")[:16]))
        rate_cfg = float((cfg.get("cost") or {})
                         .get("spot_rate_usd_per_hour", -1.0))
        rate_art = float((art.get("rate") or {}).get("usd_per_hour", -2.0))
        if rate_cfg != rate_art:
            fail("ERR_F1K_AFFORD",
                 "config cost rate %r != the gate artifact's licensed "
                 "rate %r — the projection was licensed AT that rate; a "
                 "different campaign rate is a different license "
                 "[REV-C F5ii]" % (rate_cfg, rate_art))
        if not self.mock:
            cur_pin = validate_pinning(cfg)
            if (art.get("pin") or {}).get("pin_file_sha256") \
                    != cur_pin["pin_file_sha256"]:
                fail("ERR_F1K_PINNING",
                     "campaign pin sha %r != the gate artifact's licensed "
                     "pin %r — REV-C runs the LICENSED bring-up pin for "
                     "the whole campaign (full-corpus re-derivation is "
                     "DEFERRED, no rebind path exists); a different pin "
                     "is a different license"
                     % (cur_pin["pin_file_sha256"][:16],
                        ((art.get("pin") or {})
                         .get("pin_file_sha256") or "")[:16]))
        self.knots = sorted(art["model"]["knots_isotonic"],
                            key=lambda k: k["T"])
        if not self.knots:
            fail("ERR_F1K_AFFORD", "gate artifact carries no knots")
        self.cont = art["model"]["cont_tokens_addend"]
        self.art_sha = blk["gate_artifact_sha256"]
        self.kappa_weighting = None    # set by kappa() [REV-C F5iv]
        # [REV-D 2] COUNT-PRESERVING sidecar load: rows are consumed as
        # a dict, so a duplicate key (with a conflicting T) would
        # silently overwrite and still pass a set-equality "bijection"
        # (round-3 verdict 2). ANY duplicate key refuses — the licensed
        # sidecar is duplicate-free by construction.
        self.tp = {}
        dup = set()
        for ln in open(blk["tokens_full_path"], encoding="utf-8"):
            if ln.strip():
                e = json.loads(ln)
                if e["key"] in self.tp:
                    dup.add(e["key"])
                self.tp[e["key"]] = e["T"] + self.cont
        if dup:
            fail("ERR_F1K_AFFORD",
                 "gate tokens sidecar carries %d DUPLICATE key(s) (e.g. "
                 "%s) — duplicate rows would silently overwrite the "
                 "per-item T; refused, never collapsed [REV-D 2]"
                 % (len(dup), sorted(dup)[:3]))

    def verify_corpus(self, ev):
        """[REV-C F5ii corpus identity, driver-verifiable form; REV-D 2
        COUNT-PRESERVING] the licensed sidecar must cover EXACTLY this
        campaign's eval items: the {pilot, main-tmpl, main-d3, guard}
        key sets are a bijection with the loaded ev splits. STRICTNESS
        [REV-D]: duplicates are refused on BOTH sides BEFORE the set
        comparison — the sidecar rows at load (__init__) and the eval
        inventory here — because sets silently collapse duplicates, so
        set equality alone is not a bijection (byte-identity of the
        corpora stays enforced gate-side via corpus_sha256 and
        driver-side via the landed verify_corpus_pins; this check binds
        the TWO records to the SAME item universe)."""
        want_l = []
        for it in ev["dev"]:
            want_l.append("pilot:%s" % it["item_id"])
        for it in ev["test"]:
            want_l.append("main-tmpl:%s" % it["item_id"])
            want_l.append("main-d3:%s" % it["item_id"])
        for it in ev["guard"]:
            want_l.append("guard:%s" % it["item_id"])
        seen = set()
        edup = set()
        for k in want_l:
            (edup if k in seen else seen).add(k)
        if edup:
            fail("ERR_F1K_AFFORD",
                 "eval item inventory carries %d DUPLICATE id(s) (e.g. "
                 "%s) — a set-equality check would silently collapse "
                 "them; refused [REV-D 2]"
                 % (len(edup), sorted(edup)[:3]))
        want = set(want_l)
        have = {k for k in self.tp
                if k.split(":", 1)[0] in ("pilot", "main-tmpl", "main-d3",
                                          "guard")}
        if want != have:
            fail("ERR_F1K_AFFORD",
                 "gate sidecar item universe != this campaign's eval "
                 "items (%d missing, %d foreign; e.g. %s) — the licensed "
                 "bundle projects a DIFFERENT corpus [REV-C F5ii]"
                 % (len(want - have), len(have - want),
                    sorted(want.symmetric_difference(have))[:3]))

    def _interp(self, t, field):
        # [REV-C F5i] delegate to the SHARED implementation (KOT-ADD7-
        # SHARED block) — the driver keeps only its error surface.
        try:
            return add7_interp(self.knots, field, t, below="const")
        except Add7RangeError:
            fail("ERR_F1K_AFFORD",
                 "T=%.0f above the max sampled knot %.0f — extrapolation "
                 "above the frozen sample is FORBIDDEN (the campaign "
                 "max-T text is in the sample by construction)"
                 % (t, self.knots[-1]["T"]))

    def s_hat(self, t, hi=False):
        if hi:
            return self._interp(t, "s") + self._interp(t, "se")
        return self._interp(t, "s")

    def tp_of(self, key):
        if key not in self.tp:
            fail("ERR_F1K_AFFORD",
                 "no token count for %r in the gate tokens-full sidecar "
                 "— the per-item projection never guesses a length" % key)
        return self.tp[key]

    def kappa(self, realized_s_per_prefill, ev, pass_rows):
        """[REV-C F5iv] kappa = realized pilot s/prefill / model-predicted
        pilot blend, where the prediction is PREFILL-WEIGHTED over the
        REALIZED pilot pass structure: each scored pilot row (grid passes
        over the 48-item tuning subset, f1k_driver phase_pilot section 1,
        + the full-dev-96 passes, section 3 — read back from the pilot
        rows checkpoint) contributes one weight to its item. The REV-B
        unweighted 96-item mean mislabeled the blend (grid traffic
        weights the subset ~heavily); the realized-row weighting matches
        the numerator's ledger basis (same scored prefills) exactly, and
        stays exact under resume/REPLACE-support variation."""
        dev_ids = {it["item_id"] for it in ev["dev"]}
        w = {}
        for r in pass_rows:
            iid = r.get("item_id")
            if iid in dev_ids:
                w[iid] = w.get(iid, 0) + 1
        if not w:
            fail("ERR_F1K_AFFORD", "no pilot rows to calibrate kappa — "
                 "the prefill-weighted blend needs the realized pass "
                 "structure, never a guessed inventory [REV-C F5iv]")
        num = sum(n * self.s_hat(self.tp_of("pilot:%s" % iid))
                  for iid, n in w.items())
        den = sum(w.values())
        if den == 0 or num <= 0:
            fail("ERR_F1K_AFFORD", "no pilot entries to calibrate kappa")
        self.kappa_weighting = {
            "rule": "prefill-weighted over the REALIZED pilot pass rows "
                    "(grid passes weight the 48-item subset) [REV-C "
                    "F5iv]",
            "n_pass_rows": den, "distinct_items": len(w),
            "weight_min": min(w.values()), "weight_max": max(w.values())}
        k = realized_s_per_prefill / (num / den)
        if not self.mock and not (ADD7_KAPPA_BOUNDS[0] <= k
                                  <= ADD7_KAPPA_BOUNDS[1]):
            fail("ERR_F1K_AFFORD",
                 "kappa %.4f outside %s — the frozen gate model does not "
                 "transfer to the realized pilot throughput; maintainer "
                 "surface, never a silent projection [REV-B ASM-2516]"
                 % (k, list(ADD7_KAPPA_BOUNDS)))
        return k

    def remaining_seconds(self, ev, d3_def, rep, kappa, hi=False):
        """Per-item seconds for the REMAINING main + guard prefills."""
        passes = main_arm_passes(d3_def, rep)
        n_tmpl = sum(1 for a, _, _ in passes if a != "d3-text")
        n_d3 = sum(1 for a, _, _ in passes if a == "d3-text")
        n_guard = len(main_arm_passes(True, rep))
        tot = 0.0
        for it in ev["test"]:
            tot += n_tmpl * self.s_hat(
                self.tp_of("main-tmpl:%s" % it["item_id"]), hi)
            if n_d3:
                tot += n_d3 * self.s_hat(
                    self.tp_of("main-d3:%s" % it["item_id"]), hi)
        for it in ev["guard"]:
            tot += n_guard * self.s_hat(
                self.tp_of("guard:%s" % it["item_id"]), hi)
        return tot * kappa


def check_addendum_pinning(add7, cfg):
    """[ASM-2513 v3, re-review #3] The pilot addendum-7 is the THIRD
    cross-phase pin state (beside the cost ledger and the per-phase
    [R10-4] bindings): it records expert_pinning at PILOT time and is
    consumed at PRE-TEST time, so it must be compared, not trusted.
    A mismatch = the pilot ran under a different pin stats-file or a
    different matched-budget condition (DES §7.1) — no test spend."""
    ep = (add7.get("expert_pinning") or {})
    cur = validate_pinning(cfg)
    if ep.get("pin_file_sha256") != cur["pin_file_sha256"]:
        fail("ERR_F1K_PINNING",
             "pre-test: addendum-7 expert_pinning.pin_file_sha256=%r "
             "vs the current config's %s — the pilot ran under a "
             "DIFFERENT pin stats-file; a swapped pin never enters "
             "test [ASM-2513 v3 re-review #3]"
             % (ep.get("pin_file_sha256"), cur["pin_file_sha256"]))
    try:
        agb = float(ep.get("PIN_GB"))
    except (TypeError, ValueError):
        agb = float("nan")     # NaN != x for all x -> refused below
    if agb != cur["PIN_GB"]:
        fail("ERR_F1K_PINNING",
             "pre-test: addendum-7 expert_pinning.PIN_GB=%r vs the "
             "current config's %r — PIN_GB is fixed ONCE at bring-up "
             "(DES §7.1:639); a pilot/test budget divergence is a "
             "DIFFERENT matched-budget condition, refused "
             "[ASM-2513 v3 re-review #3]"
             % (ep.get("PIN_GB"), cur["PIN_GB"]))


def enforce_pretest_commits(cfg, outdir):
    """[FIX-6] PRE-TEST enforcement [DES §R-REV4.2 / ASM-2123: the test set
    stays untouched until (A),(B0),(5),(7),(6) are ALL committed; bring-up
    (7) and power freeze (6) are strictly PRE-test]. The coordinator-
    committed flags must ALL be true AND the pilot gate artifacts must
    exist and PASS before a single test prefill."""
    man = ((cfg.get("freeze") or {}).get("manifest_flags")) or {}
    need = ("pre_spend_committed", "b0_addendum_committed",
            "entry5_committed", "entry7_committed", "entry6_committed",
            "test_untouched_until_complete")
    for k in need:
        if man.get(k) is not True:
            # [R3-ATTEST] strict `is True`: a truthy string ("false"/"yes")
            # previously passed this check AND was bool()-laundered to true
            # in the sidecar — both channels now fail closed
            fail("ERR_F1K_FREEZE",
                 "freeze.manifest_flags.%s is %r, not the strict boolean "
                 "true — no test spend until (A),(B0),(5),(7),(6) are ALL "
                 "coordinator-committed as genuine JSON booleans "
                 "(§R-REV4.2/ASM-2123; HOLD round-3 item 4)"
                 % (k, man.get(k)))
    pdir = Path(outdir) / "pilot"
    arts = {}
    for fname in ("addendum-5-frozen-lg.json", "addendum-6-inputs.json",
                  "addendum-7-affordability.json", "pilot-gates.json"):
        p = pdir / fname
        if not p.exists():
            fail("ERR_F1K_FREEZE",
                 "pilot artifact %s missing — the (5)/(6)/(7) pure-function "
                 "addenda + gate record must exist BEFORE test spend "
                 "(§R-REV2.4/§R-REV4.2)" % p)
        arts[fname] = json.loads(p.read_text(encoding="utf-8"))
    gates = arts["pilot-gates.json"]
    for gname in ("power_gate", "placebo_gate_pilot_n",
                  "affordability_gate", "semantics_gate"):
        # [R3-ATTEST] strict `is True` on every persisted gate read
        if (gates.get(gname) or {}).get("pass") is not True:
            fail("ERR_F1K_FREEZE",
                 "pilot gate %r did not PASS as a strict boolean (%s) — no "
                 "test spend (§R-REV4.2 pre-test gates; HOLD round-3 "
                 "item 4)" % (gname, gates.get(gname)))
    add7 = arts["addendum-7-affordability.json"]
    if add7.get("affordable") is not True:
        fail("ERR_F1K_AFFORD", "addendum (7) affordable is %r, not the "
             "strict boolean true — no test spend (§R6; HOLD round-3 "
             "item 4)" % (add7.get("affordable"),))
    d3_deferred = attest_bool(add7.get("d3_text_deferred"),
                              "addendum-7 d3_text_deferred")
    check_addendum_pinning(add7, cfg)     # [ASM-2513 v3 re-review #3]
    rg = (arts["addendum-6-inputs.json"].get("replace_gate")) or {}
    if rg.get("decision") not in ("RUN", "DEFER"):
        fail("ERR_F1K_REPLACE", "addendum-6 replace_gate.decision %r invalid"
             % (rg.get("decision"),))
    replace_run = rg["decision"] == "RUN"
    if replace_run:
        if not (cfg.get("replace") or {}).get("engine_supported"):
            fail("ERR_F1K_REPLACE",
                 "replace gate committed RUN but the engine is not "
                 "REPLACE-capable — protocol conflict, return to the "
                 "coordinator")
        io = (cfg.get("replace") or {}).get(
            "io_saving_bytes_per_gated_token")
        if not isinstance(io, (int, float)) or isinstance(io, bool) \
                or io <= 0:
            fail("ERR_F1K_REPLACE",
                 "REPLACE runs but measured expert-byte saving is %r — the "
                 "NI endpoint requires io_saving > 0 [REG sec-replace-ni]"
                 % (io,))
    return d3_deferred, replace_run, rg


def build_sidecar(cfg, outdir, guard_report, dose, ledger, d3_deferred,
                  replace_gate, replace_run):
    """Sidecar in analysis/f1k.py's EXACT schema [ANA docstring 'SIDECAR'].
    Every field is either a coordinator-committed freeze artifact (copied
    verbatim, fail-closed if absent) or a driver measurement."""
    man = (cfg.get("freeze") or {}).get("manifest_flags")
    need = ("pre_spend_committed", "b0_addendum_committed", "entry5_committed",
            "entry7_committed", "entry6_committed",
            "test_untouched_until_complete")
    if not man or not all(k in man for k in need):
        fail("ERR_F1K_FREEZE", "freeze.manifest_flags must carry all of %s "
             "(the (A)/(B0)/(5)/(7)/(6) commit states, §R-REV4.2 — "
             "coordinator-committed, never inferred)" % (need,))
    tpl = cfg.get("template_checks")
    if not tpl or not all(k in tpl for k in
                          ("labels_single_token",
                           "header_cue_labels_trigger_free")):
        fail("ERR_F1K_FREEZE", "template_checks missing (frozen at (A): "
             "single-token labels + trigger-free header/cue/labels, "
             "§R1.1/§R-REV2.1)")
    inf = cfg.get("inference")
    if not inf or inf.get("method") not in ("signflip", "bca") or \
            not isinstance(inf.get("dev_sign_symmetry_pass"), bool):
        fail("ERR_F1K_FREEZE", "inference {method: signflip|bca, "
             "dev_sign_symmetry_pass: bool} is mandatory — the §R-REV4.1a "
             "dev-selected choice frozen at addendum (6); analysis/f1k.py "
             "enforces coherence fail-closed")
    power = validate_power(cfg)                          # [FIX-7]
    # carriers block from the frozen-L K table actually spliced
    frozen = load_frozen_lg(cfg, outdir)
    ksub = Path(outdir) / "test" / "carriers-frozenL" / (
        "K.L-%s.kaec" % "-".join(map(str, frozen["layers"])))
    if not ksub.exists():
        kaec_subset(cfg["carriers"]["K"]["path"], frozen["layers"],
                    str(ksub))
    km = kaec_read(str(ksub))
    io_saving = (cfg.get("replace") or {}).get(
        "io_saving_bytes_per_gated_token") if replace_run else None
    # [R3-ATTEST] HOLD round-3 item 4 (attestation laundering CLOSED): every
    # validity flag below goes through attest_bool — NO bool() coercion
    # anywhere on the emission surface. bool() previously turned an
    # upstream JSON STRING "false" (truthy) into an emitted JSON `true`,
    # so a failing attestation reached the analysis as a passing one and
    # the campaign PASSed officially. Now a non-bool upstream value FAILS
    # THE RUN (ERR_F1K_ATTEST) before any sidecar byte is written; `true`
    # is only ever emitted when the underlying strict check produced the
    # genuine boolean true.
    side = {
        "manifest": {k: attest_bool(man[k], "freeze.manifest_flags.%s" % k)
                     for k in need},
        "guard": {"n_items": guard_report["n_items"],
                  "byte_identical": attest_bool(
                      guard_report["byte_identical"],
                      "guard-report byte_identical")},
        "template": {k: attest_bool(tpl[k], "template_checks.%s" % k)
                     for k in ("labels_single_token",
                               "header_cue_labels_trigger_free")},
        "dose": dose,
        "inference": {"method": inf["method"],
                      "dev_sign_symmetry_pass": attest_bool(
                          inf["dev_sign_symmetry_pass"],
                          "inference.dev_sign_symmetry_pass")},
        "replace": {"ran": attest_bool(replace_run,           # [FIX-3]
                                       "replace_run decision"),
                    "delta_r_dev": replace_gate.get("delta_r_dev"),
                    "n_ni": replace_gate.get("n_ni"),
                    "io_saving_bytes_per_gated_token": io_saving},
        "carriers": {"params_added": km["nc"] * km["nl"] * km["D"],
                     "table_bytes": os.path.getsize(str(ksub)),
                     "concepts": km["nc"],
                     "layers": km["nl"]},
        "power": power,
        "cost": {                                             # [FIX-7]
            "usd_total": round(ledger.usd_total(), 4),
            "instance_hours": round(ledger.instance_hours(), 6),
            "prefills": ledger.total_prefills(),
            "usd_spent_prior": ledger.d["usd_spent_prior"],
            "construction_instance_hours":
                ledger.d["construction_instance_hours"],
            "spot_rate_usd_per_hour":
                ledger.d["spot_rate_usd_per_hour"],
            "phase_seconds": {k: round(v, 3) for k, v in
                              ledger.d["phase_seconds"].items()},
            "expert_pinning": attested_pinning(ledger),  # [FIX-5+ASM-2513]
            "resume_safe_ledger": str(ledger.path),
            "d3_text_deferred": attest_bool(d3_deferred,      # [FIX-4]
                                            "d3_text_deferred")},
        "b0_ceiling_threshold": CEILING_B0,   # echo of the pinned constant
    }
    # [R3-COST] realized-cost stop AT EMISSION (HOLD round-3 item 6): the
    # metered ledger is re-checked against the $155 ceiling as the final
    # act before the success sidecar exists — an over-ceiling campaign can
    # never emit a success record (the accumulation-time stop in
    # Ledger.add is the first line; this is the second, independent one).
    ledger.enforce_cap("sidecar emission")
    spath = Path(outdir) / "test" / "sidecar.json"
    write_json(spath, side)
    return spath


def _repo_rel(path):
    """Repo-relative POSIX path for a run artifact. kot-log/1 artifact
    paths resolve against the repo root (verdict-gen joins them to --root;
    the pinned analysis resolves them against its own repo root), so an
    artifact OUTSIDE the repo could never be consumed through the official
    seam — fail closed, never emit an absolute/escaping path."""
    try:
        rel = Path(path).resolve().relative_to(ROOT)
    except ValueError:
        fail("ERR_F1K_RECORD",
             "artifact %s is outside the repo root %s — kot-log/1 artifact "
             "paths are repo-relative; keep --outdir inside the repo so "
             "the official verdict-gen seam can consume the record"
             % (path, ROOT))
    return rel.as_posix()


def emit_run_record(outdir, rows_path, sidecar_path, pins_observed=None):
    """[R3-SEAM] The kot-log/1-conformant run-record BODY (HOLD round-3
    item 7). The pre-round-3 driver emitted `artifacts` as a DICT
    {rows_path, ...} with none of the chained fields — schema-invalid for
    log-append, so the OFFICIAL driver-record -> verdict-gen -> analysis
    round-trip was structurally impossible and had never been tested (the
    mock called the analysis directly). Now: event=run, phase=final,
    exit=ok, prereg_hash = the CURRENT frozen_sha256 from
    registry/frozen-index.json (verdict-gen eligibility), config/metrics
    (raw counts only, P2 §2.4), and the D10-PAIRED artifacts ARRAY —
    exactly one {path, sha256, role:"rows"} entry and one
    {path, sha256, role:"sidecar"} entry, repo-relative. log-append stamps
    seq/prev_sha256/ts/runner/schema_version; the coordinator appends this
    body via log-append (the single write path), then verdict-gen verifies
    both pins and pipes the record line to the pinned analysis.

    [R9-PROV] pins_observed (carrier re-review item 8, 2026-07-16): the
    carrier-construction provenance witness from
    verify_carrier_construction — the typed kot-f1k-record/1
    {observed[, expected]} sha256 map (the sidecar schema is CLOSED, so
    the RECORD is the lawful channel that witnesses the construction
    mode + bindings; the key carrier-construction-report.mode-<mode>
    names the mode, its value pins the report bytes that bind it)."""
    idx_path = ROOT / "registry" / "frozen-index.json"
    try:
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail("ERR_F1K_RECORD", "cannot read %s: %s" % (idx_path, e))
    if "f1k" not in idx:
        fail("ERR_F1K_RECORD",
             "f1k absent from registry/frozen-index.json — no run record "
             "without a frozen prereg (G-1)")
    n_rows = sum(1 for line in
                 Path(rows_path).read_text(encoding="utf-8").splitlines()
                 if line.strip())
    rec = {
        "event": "run", "phase": "final", "exit": "ok",
        "prereg_hash": idx["f1k"],
        "config": {
            "protocol": "f1k-main-campaign",
            "engine": "colibri",
            "n_test_items": N_TEST,
            "r_drng_passes": R_DRNG,
        },
        "metrics": {
            "rows_emitted": n_rows,
            "n_test_items": N_TEST,
        },
        "artifacts": [
            {"path": _repo_rel(rows_path),
             "sha256": sha256_file(rows_path), "role": "rows"},
            {"path": _repo_rel(sidecar_path),
             "sha256": sha256_file(sidecar_path), "role": "sidecar"},
        ],
    }
    if pins_observed:
        rec["pins_observed"] = pins_observed     # [R9-PROV] typed witness
    rpath = Path(outdir) / "test" / "run-record.jsonl"
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rpath


# ---------------------------------------------------------------------------
# PILOT (phase producing the (5)/(7) addenda + the (6) inputs)
# ---------------------------------------------------------------------------
def pilot_dev_subset(cfg, dev_items):
    """[FIX-6] The 48-item stratified dev subset [REG design.n_planned.pilot]
    is the freeze-manifest (A) COMMITTED id list (config.pilot.
    dev_subset_ids) — the deterministic selection rule lives in (A), the
    driver only validates it (48 unique dev ids, at most one per cluster =
    stratified), never invents one (review §9: the earlier round-robin rule
    was unspecified by f1k.json/design and is REMOVED)."""
    ids = (cfg.get("pilot") or {}).get("dev_subset_ids")
    if not isinstance(ids, list) or len(ids) != PILOT_DEV_SUBSET_N \
            or len(set(ids)) != PILOT_DEV_SUBSET_N:
        fail("ERR_F1K_PILOT",
             "pilot.dev_subset_ids must be exactly %d unique dev item ids "
             "(the freeze-manifest (A) committed stratified subset)"
             % PILOT_DEV_SUBSET_N)
    by_id = {it["item_id"]: it for it in dev_items}
    missing = [i for i in ids if i not in by_id]
    if missing:
        fail("ERR_F1K_PILOT", "pilot dev-subset ids not in the dev split: %s"
             % missing[:5])
    subset = [by_id[i] for i in ids]
    per_cluster = {}
    for it in subset:
        per_cluster[it["cluster"]] = per_cluster.get(it["cluster"], 0) + 1
    over = {c: n for c, n in per_cluster.items() if n > 1}
    if over:
        fail("ERR_F1K_PILOT",
             "pilot dev subset is not stratified (clusters with >1 item: "
             "%s) [REG design.n_planned.pilot: 'stratified dev subset']"
             % sorted(over.items())[:5])
    return sorted(subset, key=lambda x: (x["cluster"], x["item_id"]))


def validate_panel(cfg):
    """[FIX-6] FULL family-blind panel validation [DES §R-REV2.3/§R-REV3.2;
    REG design.n_planned.pilot; REG freeze_manifest A(vii)] — not just
    '4 members / 3 families':
      * the {2,1,1} FAMILY PARTITION with the 2-member family = the K
        family {K-true, K-derangement};
      * pilot-panel derangement seed 11 and d0 table seed 7;
      * CARRIER IDENTITIES: K-true == the main K table, the d0 member ==
        the main d0 table, the d2 member == the main d2 table (byte shas);
      * per-(c,l) NORM MATCHING of every member to the K reference norm
        (§R2 rescale rule);
      * the K-derangement member RECONSTRUCTS as the declared fixed-point-
        free permutation of the K table, norm-rescaled (pure-function
        check of the B0 addendum, §R-REV3.3)."""
    pil = cfg.get("pilot") or {}
    panel = pil.get("panel") or {}
    members = panel.get("members") or {}
    families = panel.get("families") or {}
    if len(members) != 4 or len(families) != 3:
        fail("ERR_F1K_PILOT", "panel must be 4 members in 3 families "
             "(§R-REV2.3/§R-REV3.2)")
    sizes = sorted(len(v) for v in families.values())
    if sizes != [1, 1, 2]:
        fail("ERR_F1K_PILOT",
             "family partition %s != the frozen {2,1,1} (K family supplies "
             "2 members, d2 and d0 one each; §R-REV3.2 equal FAMILY-level "
             "weight)" % sizes)
    all_ids = sorted(x for v in families.values() for x in v)
    if all_ids != sorted(members):
        fail("ERR_F1K_PILOT", "families do not partition the member set")
    k_true = panel.get("k_true_member")
    placebo_fam = panel.get("placebo_family")
    if k_true not in members or placebo_fam not in families:
        fail("ERR_F1K_PILOT", "panel.k_true_member and panel.placebo_family "
             "must name a member / family")
    kfams = [f for f, v in families.items() if k_true in v]
    if len(kfams) != 1 or len(families[kfams[0]]) != 2:
        fail("ERR_F1K_PILOT",
             "the K family must be the 2-member family {K-true, "
             "K-derangement(seed %d)} containing k_true_member"
             % PILOT_KDRNG_SEED)
    kfam = kfams[0]
    if placebo_fam == kfam or len(families[placebo_fam]) != 1:
        fail("ERR_F1K_PILOT", "placebo (d0) family must be a 1-member "
             "family distinct from the K family")
    kdrng_id = [x for x in families[kfam] if x != k_true][0]
    d0_id = families[placebo_fam][0]
    d2fam = [f for f in families if f not in (kfam, placebo_fam)][0]
    d2_id = families[d2fam][0]
    # carrier identities (byte-level)
    idents = (("k_true", k_true, cfg["carriers"]["K"]["path"]),
              ("d0", d0_id, cfg["carriers"]["d0"]["path"]),
              ("d2", d2_id, cfg["carriers"]["d2"]["path"]))
    for what, mid, arm_path in idents:
        if sha256_file(members[mid]["path"]) != sha256_file(arm_path):
            fail("ERR_F1K_PILOT",
                 "panel %s member %s carrier != the main-arm table %s "
                 "(carrier IDENTITY, freeze-manifest (A)/(B0))"
                 % (what, mid, arm_path))
    # seeds [REG freeze_manifest A(vii)]
    kd_meta = members[kdrng_id].get("meta") or {}
    if int(kd_meta.get("seed", -10 ** 9)) != PILOT_KDRNG_SEED:
        fail("ERR_F1K_PILOT",
             "K-derangement member seed %r != frozen pilot-panel seed %d"
             % (kd_meta.get("seed"), PILOT_KDRNG_SEED))
    d0_meta = members[d0_id].get("meta") or {}
    if int(d0_meta.get("seed", -10 ** 9)) != PILOT_D0_SEED:
        fail("ERR_F1K_PILOT", "d0 member seed %r != frozen d0 table seed %d"
             % (d0_meta.get("seed"), PILOT_D0_SEED))
    der = kd_meta.get("derangement")
    if not isinstance(der, list) or sorted(der) != list(range(len(der))):
        fail("ERR_F1K_PILOT", "K-derangement member lacks a valid "
             "derangement permutation in its (B0) metadata")
    if any(der[i] == i for i in range(len(der))):
        fail("ERR_F1K_PILOT", "pilot derangement has a fixed point (§R2)")
    # geometry + norm matching + derangement reconstruction
    K = kaec_read(cfg["carriers"]["K"]["path"])
    if len(der) != K["nc"]:
        fail("ERR_F1K_PILOT", "derangement length %d != nc %d"
             % (len(der), K["nc"]))
    knorm = {}
    for c in range(K["nc"]):
        for s in range(K["nl"]):
            knorm[(c, s)] = _vnorm(_kaec_vec(K, c, s))
    for mid in (kdrng_id, d0_id, d2_id):
        m = kaec_read(members[mid]["path"])
        if (m["nc"], m["nl"], m["D"], m["layers"]) != \
                (K["nc"], K["nl"], K["D"], K["layers"]):
            fail("ERR_F1K_PILOT", "panel member %s geometry differs from "
                 "the K table" % mid)
        for c in range(K["nc"]):
            for s in range(K["nl"]):
                nk = knorm[(c, s)]
                nm = _vnorm(_kaec_vec(m, c, s))
                if abs(nm - nk) > NORM_MATCH_RTOL * max(nk, 1e-9):
                    fail("ERR_F1K_PILOT",
                         "panel member %s NOT norm-matched at (c=%d, "
                         "slot=%d): ||v||=%.6g vs K reference %.6g (§R2 "
                         "'all rescaled to the reference norm')"
                         % (mid, c, s, nm, nk))
    mdr = kaec_read(members[kdrng_id]["path"])
    for c in range(K["nc"]):
        for s in range(K["nl"]):
            src = _kaec_vec(K, der[c], s)
            nk = knorm[(c, s)]
            nsrc = knorm[(der[c], s)]
            scale = nk / max(nsrc, 1e-12)
            got = _kaec_vec(mdr, c, s)
            tol = NORM_MATCH_RTOL * max(nk, 1e-9)
            if any(abs(g - x * scale) > tol for g, x in zip(got, src)):
                fail("ERR_F1K_PILOT",
                     "K-derangement member does not reconstruct as the "
                     "declared seed-%d permutation of the K table at "
                     "(c=%d, slot=%d) — pure-function (B0) check failed"
                     % (PILOT_KDRNG_SEED, c, s))
    return {"k_family": kfam, "k_true_member": k_true,
            "k_derangement_member": kdrng_id, "k_derangement_seed":
                PILOT_KDRNG_SEED,
            "d0_member": d0_id, "d0_seed": PILOT_D0_SEED,
            "d2_member": d2_id, "family_partition": "{2,1,1}",
            "carrier_identities_verified": True,
            "norm_matched_within_rtol": NORM_MATCH_RTOL,
            "derangement_reconstructed": True}


def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
    pdir = Path(outdir) / "pilot"
    pdir.mkdir(parents=True, exist_ok=True)
    validate_power(cfg)                     # [FIX-7] before any pilot spend
    pil = cfg.get("pilot")
    if not pil:
        fail("ERR_F1K_PILOT", "config.pilot missing (grid + family-blind "
             "panel, freeze-manifest (A) rule for entry 5)")
    layer_sets = pil["layer_sets"]          # {"L1": [...], ...} [DES §2.3]
    if len(layer_sets) != 3:
        fail("ERR_F1K_PILOT", "pilot grid must be 3 layer sets "
             "(f1k.json design.n_planned.pilot)")
    # [FIX-6] the grid's g values are MULTIPLIERS of the bring-up-measured
    # mean native expert weight [DES §2.3 VERBATIM: "blend grid g in
    # {0.5, 1.0, 2.0} x mean native expert weight"] — never raw KAE_G.
    mults = [float(x) for x in (pil.get("g_multipliers") or [])]
    if mults != list(G_MULTIPLIERS):
        fail("ERR_F1K_PILOT",
             "pilot.g_multipliers %s != the frozen grid %s "
             "[DES §2.3]" % (mults, list(G_MULTIPLIERS)))
    w_bar = pil.get("mean_native_expert_weight")
    if not isinstance(w_bar, (int, float)) or isinstance(w_bar, bool) \
            or w_bar <= 0:
        fail("ERR_F1K_PILOT",
             "pilot.mean_native_expert_weight must be a positive measured "
             "value (bring-up measurement, committed with the (A)/(B0) "
             "artifacts) — frozen g = multiplier x mean native expert "
             "weight [DES §2.3]")
    w_bar = float(w_bar)
    # colibri knob-semantics re-verification (ASM-1971; §R-REV4.2 step 3
    # runs it alongside the pilot; addendum (7) is the SEMANTIC gate too)
    sem = cfg.get("semantics_reverification") or {}
    # [R3-ATTEST] strict: performed must be the genuine boolean true (a
    # truthy string previously counted AND was bool()-laundered into the
    # (7) artifact); evidence_path must be a real on-disk path
    sem_ok = (sem.get("performed") is True
              and isinstance(sem.get("evidence_path"), str)
              and Path(sem["evidence_path"]).exists())
    panel_facts = validate_panel(cfg)       # [FIX-6]
    panel = pil["panel"]
    members = panel["members"]
    families = panel["families"]
    subset = pilot_dev_subset(cfg, ev["dev"])

    # ---- 1. score the grid over the UNLABELED panel (48-item subset) ------
    rows_path = pdir / "pilot-rows.jsonl"
    # [R10-4] authenticated resume (pilot rows feed the (5)/(6)/(7)
    # addenda — fabricated rows must never select (L,g) or pass gates)
    done, _, auth = read_ckpt_authed(rows_path,
                                     campaign_resume_binding(cfg, "pilot"))
    configs = []
    for ls_id in sorted(layer_sets):
        for mult in mults:
            configs.append(("%s|gx=%.4g" % (ls_id, mult), ls_id, mult))
    for cfg_id, ls_id, mult in configs:
        g_eff = mult * w_bar                # [FIX-6] realized KAE_G
        for mem_id in sorted(members):
            arm_tag = "panel:%s:%s" % (cfg_id, mem_id)
            frozen_c = {"layers": layer_sets[ls_id], "g": g_eff}
            # splice with the member's carrier subset to this layer set
            # (file named from the master table, a pure derivation; the
            # SELECTION statistic below sees only blind member/family ids)
            mbase = Path(members[mem_id]["path"]).stem
            sub = pdir / "carriers" / ("%s.%s.kaec" % (mbase, ls_id))
            if not sub.exists():
                kaec_subset(members[mem_id]["path"], layer_sets[ls_id],
                            str(sub))
            env = arm_env(cfg, "b0", None, str(pdir), frozen_c)  # base env
            env["KAE"] = "1"
            env["KAE_CARRIER"] = str(sub)
            env["KAE_G"] = repr(g_eff)
            env["KAE_MODE"] = "0"
            run_scoring_pass(cfg, subset, arm_tag, 0, None, env,
                             rows_path, done, ledger=ledger,
                             mock_gold_dir=mock_gold_dir, phase="pilot",
                             auth=auth)
    _, rows = read_ckpt(rows_path)
    acc = {}
    for r in rows:
        acc.setdefault(r["arm"], {})[r["item_id"]] = r["correct"]

    # ---- 2. the BLIND selection statistic (equal FAMILY-level weight) -----
    # S(L,g) = (1/3) * sum over families of mean(member dev accuracy)
    # [DES §R-REV3.2 / ASM-2113]; the panel ids and family partition carry
    # no treatment label. Tie-break: fewer spliced layers, then lower g
    # [DES §R4].
    s_table = {}
    per_member = {}
    for cfg_id, ls_id, mult in configs:
        fam_means = []
        for fam in sorted(families):
            vals = []
            for mem_id in families[fam]:
                a = acc.get("panel:%s:%s" % (cfg_id, mem_id), {})
                if len(a) != PILOT_DEV_SUBSET_N:
                    fail("ERR_F1K_PILOT", "incomplete panel scoring for "
                         "%s/%s" % (cfg_id, mem_id))
                v = sum(a.values()) / len(a)
                vals.append(v)
                per_member["%s|%s" % (cfg_id, mem_id)] = v
            fam_means.append(sum(vals) / len(vals))
        s_table[cfg_id] = sum(fam_means) / len(fam_means)
    best = sorted(
        configs,
        key=lambda c: (-s_table[c[0]], len(layer_sets[c[1]]), c[2]))[0]
    best_id, best_ls, best_mult = best
    frozen = {"layer_set_id": best_ls, "layers": layer_sets[best_ls],
              "g_multiplier": best_mult,
              "mean_native_expert_weight": w_bar,
              "g": best_mult * w_bar}       # [FIX-6] mult x w-bar, recorded
    add5 = {
        "addendum": "(5) frozen (L,g)",
        "rule": "deterministic argmax of S(L,g) = equal-family-weight mean "
                "dev accuracy over the 4-member unlabeled panel; tie-break "
                "fewer spliced layers then lower g; realized g = "
                "grid MULTIPLIER x mean native expert weight "
                "[glm52-followup-experiment.md §2.3/§R4/§R-REV2.3/"
                "§R-REV3.2; f1k.json design.n_planned.pilot]",
        "s_table": {k: round(v, 6) for k, v in sorted(s_table.items())},
        "per_member_dev_accuracy_UNBLINDED_AFTER_FREEZE":
            {k: round(v, 6) for k, v in sorted(per_member.items())},
        "panel_validation": panel_facts,
        "frozen": frozen,
    }
    write_json(pdir / "addendum-5-frozen-lg.json", add5)
    print("pilot: frozen (L,g) = (%s, gx=%.4g -> g=%.6g), S=%.4f"
          % (best_ls, best_mult, frozen["g"], s_table[best_id]))

    # ---- 3. POST-FREEZE dev-96 passes [FIX-6]: the frozen design computes
    #         delta-hat / sign-symmetry / placebo / delta_R "after the §R4
    #         pilot freezes (L,g) ... on dev-96" [DES §R3.2 dev-measured
    #         inputs; §R-REV4.2 step 3], NOT on the 48-item tuning subset. --
    dev96 = sorted(ev["dev"], key=lambda x: (x["cluster"], x["item_id"]))
    replace_supported = (cfg.get("replace") or {}) \
        .get("engine_supported") is True    # [R3-ATTEST] strict (load_config
    #                                         already enforces a real bool)
    env = arm_env(cfg, "b0", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:b0", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot", store_raw=True, auth=auth)
    env = arm_env(cfg, "K", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:K", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot", store_raw=True, auth=auth)
    env = arm_env(cfg, "d0", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:d0", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot", auth=auth)
    if replace_supported:
        # [FIX-3]/[FIX-6] measure REPLACE-vs-ADD dev discordance
        env = arm_env(cfg, ARM_REPLACE, None, str(pdir), frozen)
        run_scoring_pass(cfg, dev96, "dev96:REPLACE", 0, None, env,
                         rows_path, done, ledger=ledger,
                         mock_gold_dir=mock_gold_dir, phase="pilot",
                         store_raw=True, auth=auth)
    _, rows = read_ckpt(rows_path)
    acc, raws = {}, {}
    for r in rows:
        acc.setdefault(r["arm"], {})[r["item_id"]] = r["correct"]
        if "raw" in r:
            raws.setdefault(r["arm"], {})[r["item_id"]] = r["raw"]
    for tag in ["dev96:b0", "dev96:K", "dev96:d0"] + \
            (["dev96:REPLACE"] if replace_supported else []):
        if len(acc.get(tag, {})) != DEV_N:
            fail("ERR_F1K_PILOT", "post-freeze pass %s scored %d/%d dev "
                 "items" % (tag, len(acc.get(tag, {})), DEV_N))
    clusters96 = {it["item_id"]: it["cluster"] for it in dev96}
    b0_acc = acc["dev96:b0"]
    k_acc = acc["dev96:K"]
    d0_acc = acc["dev96:d0"]

    # placebo gate at pilot n (dev-96): one-sided cluster sign-flip,
    # d0-family member vs b0, p < 0.05 alarms at ANY magnitude [ASM-2273:
    # no +3 floor; the registered run-voiding gate is the analysis-time one
    # — this pilot check is the same rule applied early so no test spend
    # follows a noisy instrument].
    dcs = cluster_diffs(d0_acc, b0_acc, clusters96)
    d0_lift, d0_p = signflip_p(dcs, "pilot_placebo_d0_vs_b0")
    placebo_ok = (d0_p is not None and d0_p >= ALPHA)

    # dev delta-hat (K vs b0 discordance on dev-96) at its one-sided 80%
    # upper bound [DES §R3.2: "delta-hat = discordance rate between b0 and
    # the frozen-config panel arms on dev-96, taken at its one-sided 80%
    # upper confidence bound"; §R-REV2.4 entry-6 rule; z0.80 = 0.842 EXACT]
    shared = sorted(set(k_acc) & set(b0_acc))
    disc = sum(1 for i in shared if k_acc[i] != b0_acc[i])
    delta_hat = disc / len(shared)
    delta_u = min(1.0, delta_hat + Z80 * math.sqrt(           # [FIX-7]
        max(delta_hat * (1 - delta_hat), 1e-12) / len(shared)))
    # n_required at rho_U [DES §R-REV2.2: SE^2 = delta * DEFF / n,
    # DEFF = 1 + (m-1) rho; planned test geometry m = n/C from the frozen
    # eval manifest]
    test_pg = check_power_gate(ev["test"])
    m_planned = test_pg["n_items"] / max(test_pg["n_clusters"], 1)
    deff = 1 + (m_planned - 1) * RHO_U
    n_required = delta_u * deff / (SE_TARGET ** 2)
    # [FIX-7]/[R6-1] n = 1573 EXACTLY [REG design.n_planned.n_test_items:
    # F1-K runs AT the cap (§R-REV3.1 item 4; REVISION-6/ASM-2369); ANA
    # N_REGISTERED rejects any other realized n]. Never
    # min(cap, ceil(n_required)): the frozen n is the cap itself;
    # n_required is recorded, and a measured n_required below the cap is
    # DISCLOSED as an anomaly against §R-REV3.1 item 4 (running at the cap
    # only adds power — n is never reduced).
    n_run = N_TEST
    n_req_note = None
    if math.ceil(n_required) < N_TEST:
        n_req_note = ("ANOMALY vs §R-REV3.1 item 4 (dev-measured "
                      "n_required %.0f < the cap %d): the frozen protocol "
                      "still runs AT n = %d exactly; disclosed, not a "
                      "spend lever" % (n_required, N_TEST, N_TEST))
    dsym = cluster_diffs(k_acc, b0_acc, clusters96)

    # ---- 3b. REPLACE run/defer gate [FIX-3] [DES §R-REV4.3/ASM-2124; REG
    #          sec-replace-ni: run/defer decided PRE-test] -------------------
    if replace_supported:
        gated_ids = [it["item_id"] for it in dev96
                     if any(s >= 0 for s in it["spans"])]
        rep_raw = raws.get("dev96:REPLACE", {})
        b0_raw = raws.get("dev96:b0", {})
        if gated_ids and all(rep_raw.get(i) == b0_raw.get(i)
                             for i in gated_ids):
            # [FIX-3] REPLACE-engine STUB DETECTION: the gate-0 patch keeps
            # KAE_MODE=1 inert, so a stubbed engine scores b0 byte-for-byte
            # on every gated item — that is NOT a measured REPLACE arm.
            fail("ERR_F1K_REPLACE",
                 "config claims a REPLACE-capable engine but the dev-96 "
                 "REPLACE pass is byte-identical to b0 on ALL %d gated "
                 "items — the REPLACE splice did not engage (gate-0 stub "
                 "behaviour); delta_R is NOT measured on an unspliced "
                 "model" % len(gated_ids))
        rep_acc = acc["dev96:REPLACE"]
        shared_r = sorted(set(rep_acc) & set(k_acc))
        delta_r = sum(1 for i in shared_r
                      if rep_acc[i] != k_acc[i]) / len(shared_r)
        n_ni = delta_r * deff / (SE_NI ** 2)
        decision = "RUN" if n_ni <= N_TEST else "DEFER"
        reason = ("dev delta_R=%.4f -> n_NI=%.0f %s n_max=%d "
                  "[§R-REV4.3/ASM-2124 at the REVISION-6 geometry: RUN "
                  "only if n_NI <= %d, i.e. delta_R <= ~%.4f at "
                  "rho_U=%.2f]"
                  % (delta_r, n_ni, "<=" if decision == "RUN" else ">",
                     N_TEST, N_TEST, DELTA_R_RUN_MAX, RHO_U))
    else:
        delta_r, n_ni = None, None
        decision = "DEFER"
        reason = ("engine is not REPLACE-capable: the gate-0 patch "
                  "implements REPLACE as a documented no-op stub "
                  "(KAE_MODE=1 keeps the ADD splice inert [PATCH kae.h]), "
                  "so dev delta_R is not measurable ON THIS ENGINE; "
                  "deferral is recorded EXPLICITLY for the coordinator's "
                  "(6) commit (the modal expectation, §R-REV4.3/ASM-2124) "
                  "— a reviewed REPLACE-capable engine patch is required "
                  "before the gate can admit RUN")
    replace_gate = {"delta_r_dev": None if delta_r is None
                    else round(delta_r, 6),
                    "n_ni": None if n_ni is None else round(n_ni, 1),
                    "se_ni_target_fraction": SE_NI,
                    "deff_at_planned_m": round(deff, 4),
                    "engine_supported": replace_supported,
                    "decision": decision, "reason": reason}

    # ---- 4. bring-up affordability gate (addendum (7)) --------------------
    # [FIX-7] resume-safe timing: the ledger's accumulated pilot seconds/
    # prefills, never a per-invocation stopwatch.
    # [REV-B GAP-3b, F1K-BRINGUP-GATE-FIX.md SSB / ASM-2516] PER-ITEM
    # token-aware + RESERVE-INCLUSIVE: the FROZEN bring-up gate model
    # s_hat(T) (ASM-2514/2515), re-levelled by the realized pilot
    # throughput (kappa), summed per item over the remaining main/guard
    # prefills at their measured token counts, and tested against BOTH
    # caps (+$8 / +8/rate hours) at central AND +1SE — never one blended
    # average times a prefill count (the v3-review finding-3 failure
    # mode), and never reserve-blind. ONE projection model at both seams.
    pilot_s = ledger.phase_seconds("pilot")
    pilot_pf = ledger.phase_prefills("pilot")
    s_per_prefill = pilot_s / max(pilot_pf, 1)
    rate = ledger.d["spot_rate_usd_per_hour"]
    prior = ledger.d["usd_spent_prior"]
    a7m = Add7Model(cfg)
    a7m.verify_corpus(ev)          # [REV-C F5ii] same item universe
    _, k_rows = read_ckpt(rows_path)
    kappa = a7m.kappa(s_per_prefill, ev, k_rows)   # [REV-C F5iv]
    reserve_h = RESERVE_USD_ADD7 / rate
    base_h = add7_hours_basis(ledger.d, pilot_s)   # [REV-D 1d] incl.
    #   prior_instance_hours — failed-session hours never vanish from
    #   the 900 h cap basis (the SAME module-level helper the mock
    #   exercises)
    steps_taken = [DEGRADATION_ORDER[0]]
    d3_deferred = False
    replace_candidate = (decision == "RUN")

    def projection(d3_def, rep):
        """(usd_c, usd_hi, hours_c, hours_hi): prior + realized pilot +
        the PER-ITEM projected remainder (central / +1SE knots)."""
        sec_c = a7m.remaining_seconds(ev, d3_def, rep, kappa)
        sec_hi = a7m.remaining_seconds(ev, d3_def, rep, kappa, hi=True)
        return (prior + (pilot_s + sec_c) / 3600.0 * rate,
                prior + (pilot_s + sec_hi) / 3600.0 * rate,
                base_h + sec_c / 3600.0,
                base_h + sec_hi / 3600.0)

    def cap_breach(p4):
        # [REV-C] the module-level predicate — ONE reserve rule, also
        # exercised at the degradation boundary by the $0 mock.
        return add7_cap_breach(p4, rate)

    proj4 = projection(d3_deferred, replace_candidate)
    if cap_breach(proj4) and replace_candidate:
        # §R6 step 2: defer REPLACE (overrides an NI-gate RUN — recorded)
        steps_taken.append(DEGRADATION_ORDER[1])
        replace_candidate = False
        decision = "DEFER"
        replace_gate["decision"] = "DEFER"
        replace_gate["reason"] += (" | OVERRIDDEN to DEFER by the §R6 "
                                   "step-2 affordability degradation")
        proj4 = projection(d3_deferred, replace_candidate)
    elif not replace_candidate:
        steps_taken.append(DEGRADATION_ORDER[1] +
                           " [already deferred by the NI gate]")
    if cap_breach(proj4):
        # [FIX-4] step 3: defer d3-text — recorded AND honored in execution
        steps_taken.append(DEGRADATION_ORDER[2])
        d3_deferred = True
        proj4 = projection(d3_deferred, replace_candidate)
    affordable = not cap_breach(proj4)
    proj = proj4[0]      # central usd (legacy field/message basis)
    add7 = {
        "addendum": "(7) bring-up s/prefill + affordability/semantic "
                    "PRE-test gate [§R-REV4.2 step 5]",
        "measured_s_per_prefill": round(s_per_prefill, 6),
        "pilot_prefills": pilot_pf,
        "pilot_wall_hours": round(pilot_s / 3600.0, 6),
        "spot_rate_usd_per_hour": rate,
        "usd_spent_prior": prior,
        "prior_instance_hours":                          # [REV-D 1d]
            ledger.d["prior_instance_hours"],
        "construction_instance_hours":
            ledger.d["construction_instance_hours"],
        "expert_pinning": attested_pinning(ledger),      # [FIX-5+ASM-2513]
        "projected_total_usd": round(proj, 2),
        "usd_cap": USD_CAP,
        "projection_rev_b": {                            # [REV-B ASM-2516]
            "model": "kot-f1k-bringup-gate/2 frozen knots (gate artifact "
                     "sha %s) re-levelled by kappa; per-item over "
                     "remaining main/guard prefills; ONE model at both "
                     "seams" % a7m.art_sha[:16],
            "kappa_realized_over_predicted": round(kappa, 4),
            "kappa_bounds": list(ADD7_KAPPA_BOUNDS),
            "kappa_weighting": a7m.kappa_weighting,   # [REV-C F5iv]
            "usd_total": {"central": round(proj4[0], 2),
                          "hi": round(proj4[1], 2)},
            "instance_hours": {"central": round(proj4[2], 1),
                               "hi": round(proj4[3], 1)},
            "reserve": {"usd": RESERVE_USD_ADD7,
                        "hours_at_rate": round(reserve_h, 2),
                        "rule": "caps reserve-inclusive at central AND "
                                "+1SE; same rule as the bring-up gate "
                                "(ASM-2515)"},
            "wall_clock_cap_hours": WALL_CLOCK_CAP_HOURS,
            "per_average_RETIRED_usd": round(
                prior + pilot_s / 3600.0 * rate
                + (N_TEST * len(main_arm_passes(d3_deferred,
                                                replace_candidate))
                   + GUARD_N * len(main_arm_passes(True,
                                                   replace_candidate)))
                * s_per_prefill / 3600.0 * rate, 2)},
        "degradation_order": list(DEGRADATION_ORDER),
        "degradation_steps_applied": steps_taken,
        "d3_text_deferred": d3_deferred,                      # [FIX-4]
        "replace_pass_in_projection": replace_candidate,
        "semantics_reverification": {
            # [R3-ATTEST] emitted ONLY when already a strict bool (sem_ok
            # gates the run below, so a non-bool never reaches emission)
            "performed": sem.get("performed")
            if isinstance(sem.get("performed"), bool) else False,
            "evidence_path": sem.get("evidence_path"),
            "pass": sem_ok,
            "rule": "colibri knob-semantics re-verified on the fetched "
                    "snapshot (ASM-1971; §R-REV4.2 step 3/5: the (7) gate "
                    "is the affordability/SEMANTIC gate)"},
        "affordable": affordable,
        "note": "cap = validated reduced ceiling [glm52-f1k-cost-reduction"
                ".md/ASM-2205]; if the projection still exceeds the cap "
                "after step 3, the run STOPS and returns to the maintainer "
                "(n is never cut below n_required; no ladder arm dropped, "
                "§R6)",
    }
    write_json(pdir / "addendum-7-affordability.json", add7)

    # ---- 5. addendum (6) INPUTS -------------------------------------------
    add6_inputs = {
        "addendum": "(6) power freeze + dev-selected inference method + "
                    "RUN/DEFER gates — INPUTS ONLY (the commit is the "
                    "coordinator's; the method choice is frozen PRE-test "
                    "from the dev sign-symmetry check, §R-REV4.1a, and "
                    "enters the run config as "
                    "inference.{method,dev_sign_symmetry_pass})",
        "dev_split_used": "dev-96 POST-FREEZE at the frozen (L,g) "
                          "[DES §R3.2; review blocker 6 fix]",
        "delta_hat_dev96": round(delta_hat, 6),
        "delta_hat_dev96_upper80": round(delta_u, 6),
        "z80": Z80,                                           # [FIX-7]
        "rho_u_planning": RHO_U,
        "deff_at_planned_m": round(deff, 4),
        "n_required": round(n_required, 1),
        "n_run": n_run,
        "n_run_rule": "n = %d EXACTLY [f1k.json design.n_planned"
                      ".n_test_items; analysis/f1k.py N_REGISTERED rejects "
                      "any other realized n]" % N_TEST,
        "n_required_note": n_req_note,
        "n_cap": N_TEST,
        "dev96_cluster_diffs_K_vs_b0": [round(d, 6) for d in dsym],
        "dev_sign_symmetry_note":
            "the pass/fail CHECK PROCEDURE is a freeze-manifest (A) entry "
            "committed by the coordinator; this driver reports the dev-96 "
            "cluster-difference distribution verbatim and NEVER decides "
            "the method itself [f1k.json harness_manifest: sidecar MUST "
            "carry inference {method, dev_sign_symmetry_pass}]",
        "replace_gate": replace_gate,                         # [FIX-3]
    }
    write_json(pdir / "addendum-6-inputs.json", add6_inputs)

    # ---- 6. gates summary (fail-closed pre-run returns) --------------------
    gates = {
        "power_gate": test_pg,
        "placebo_gate_pilot_n": {
            "dev_split": "dev-96 post-freeze",
            "d0_lift_points": None if d0_lift is None else round(d0_lift, 4),
            "d0_p": None if d0_p is None else round(d0_p, 6),
            "rule": "one-sided cluster sign-flip p < 0.05 at ANY magnitude "
                    "alarms [ASM-2273 no +3 floor]; the registered VOID "
                    "gate re-runs in analysis/f1k.py on the test rows",
            "pass": placebo_ok},
        "affordability_gate": {"pass": affordable,
                               "projected_total_usd": round(proj, 2),
                               "projected_total_usd_hi": round(proj4[1], 2),
                               "projected_hours": round(proj4[2], 1),
                               "projected_hours_hi": round(proj4[3], 1),
                               "reserve_usd": RESERVE_USD_ADD7,
                               "rule": "reserve-inclusive caps at central "
                                       "AND +1SE [REV-B ASM-2516]",
                               "usd_cap": USD_CAP},
        "semantics_gate": {"pass": sem_ok,
                           "rule": "ASM-1971 colibri knob-semantics "
                                   "re-verification attested + evidence "
                                   "on disk (§R-REV4.2 step 3)"},
    }
    write_json(pdir / "pilot-gates.json", gates)
    if not test_pg["pass"]:
        fail("ERR_F1K_POWER_GATE",
             "power gate FAILED (%s) — F1-K does not run; return to the "
             "maintainer with the coverage-vs-power shortfall "
             "[f1k.json design.n_planned.power_gate]" % test_pg)
    if not placebo_ok:
        fail("ERR_F1K_PLACEBO",
             "pilot placebo alarm: d0-family beats b0 at p=%.4g < 0.05 — "
             "instrument measures noise sensitivity; STOP for coordinator "
             "review before any test spend [ASM-2273 / design §2.6]" % d0_p)
    if not sem_ok:
        fail("ERR_F1K_SEMANTICS",
             "colibri knob-semantics re-verification not attested "
             "(semantics_reverification.performed + evidence_path on "
             "disk) — the (7) semantic gate fails closed (ASM-1971 / "
             "§R-REV4.2)")
    if not affordable:
        fail("ERR_F1K_AFFORD",
             "addendum-(7) RESERVE-INCLUSIVE per-item projection breaches "
             "a cap after the full degradation order (central $%.2f / +1SE "
             "$%.2f vs $%.0f-$%.0f-reserve; %.1f / %.1f h vs %.0f h - "
             "%.1f h reserve) — STOP and return to the maintainer "
             "[§R6/§R-REV4.2; REV-B ASM-2516]"
             % (proj4[0], proj4[1], USD_CAP, RESERVE_USD_ADD7,
                proj4[2], proj4[3], WALL_CLOCK_CAP_HOURS, reserve_h))
    print("pilot: gates -> power OK, placebo OK (p=%.3f), semantics OK, "
          "affordability OK ($%.2f <= $%.0f); REPLACE %s"
          % (d0_p, proj, USD_CAP, decision))
    return frozen


# ---------------------------------------------------------------------------
# MOCK fixtures + end-to-end mock validation
# ---------------------------------------------------------------------------
def _hashf(*parts):
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def seeded_derangement(n, seed):
    """Fixed-point-free permutation from a registered seed [DES §R2].
    MOCK-ONLY generator: the real derangement realization is a (B0)
    pure-function artifact of the frozen (A) generator."""
    rng = random.Random(seed)
    while True:
        p = list(range(n))
        rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


def gen_mock_fixtures(outdir):
    """Synthetic f1k-eval-v1 / f1k-carriers-v1 / f1k-trigger-map-v1 SHAPED
    fixtures (MOCK ONLY; the real pins are coordinator-committed corpus
    pins [REG pins.corpus_hashes] produced by a SEPARATE build — this
    driver never fabricates them for a real run). [R6-5] Geometry mirrors
    the FROZEN REVISION-6 record (ASM-2369): 96 clusters, the first 37
    carrying 17 test items and the remaining 59 carrying 16 (37*17 +
    59*16 = 1573 = N_TEST exactly; every m >= 8, satisfying the
    EQUALITY-form 96/1573 gate AND the pinned analysis's hard geometry
    rejection), 96 dev (one per cluster), 60 guard. Corpus dirs mirror
    data/<corpus>/ so the kot-corpus-hash/1 verification path is
    exercised end-to-end."""
    fx = Path(outdir) / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    eval_dir = fx / "data" / "f1k-eval-v1"
    cdir = fx / "data" / "f1k-carriers-v1"
    tdir = fx / "data" / "f1k-trigger-map-v1"
    for d in (eval_dir, cdir, tdir):
        d.mkdir(parents=True, exist_ok=True)
    C, EXTRA = C_REGISTERED, 37          # [R6-5] 37x17 + 59x16 = 1573
    labels = ["A", "B", "C", "D"]
    label_ids = [65, 66, 67, 68]
    ev_path = eval_dir / "mock-eval-v1.jsonl"
    split_ids = {"test": [], "dev": [], "guard": []}
    with open(ev_path, "w", encoding="utf-8") as f:
        def emit(iid, split, cluster, cid_for_span):
            T = 24
            toks = [int(_hashf("tok", iid, t) * 5000) + 10 for t in range(T)]
            gold = int(_hashf("gold", iid) * 4)
            spans = [-1] * T
            if cid_for_span is not None:
                spans[5] = cid_for_span
                spans[6] = cid_for_span
            d3 = [9000 + (cid_for_span or 0), 9001, 9002] + toks
            it = {"item_id": iid, "split": split, "cluster": cluster,
                  "gold_index": gold, "labels": labels,
                  "label_token_ids": label_ids, "template_tokens": toks,
                  "spans": spans, "d3_template_tokens": d3,
                  "tags": (["sense-pair"] if cluster.endswith("00") or
                           cluster.endswith("01") else [])}
            f.write(json.dumps(it, sort_keys=True) + "\n")
            split_ids[split].append(iid)
        for c in range(C):
            for j in range(17 if c < EXTRA else 16):    # [R6-5] n = 1573
                emit("it-%03d-%02d" % (c, j), "test", "c-%03d" % c, c)
        dev_i = 0
        for c in range(C):
            emit("dev-%03d-0" % c, "dev", "c-%03d" % c, c)
            dev_i += 1
        c = 0
        while dev_i < DEV_N:
            emit("dev-%03d-1" % c, "dev", "c-%03d" % c, c)
            dev_i += 1
            c += 1
        for gidx in range(GUARD_N):
            emit("guard-%02d" % gidx, "guard", "g-%02d" % gidx, None)
    id_hashes = {s: hashlib.sha256(("\n".join(sorted(ids)) + "\n")
                                   .encode()).hexdigest()
                 for s, ids in split_ids.items()}

    # mock trigger map (SHAPED placeholder — never the real map)
    write_json(tdir / "mock-trigger-map.json",
               {"_mock": True,
                "note": "MOCK phrase->concept trigger map fixture; the "
                        "real f1k-trigger-map-v1 is a separate "
                        "PINNED-AT-INPUTS build",
                "gate_precedence": ["longest-match", "lowest-concept-id"],
                "triggers": {"c-%03d" % c: ["mock-phrase-%d" % c]
                             for c in range(C)}})

    # carriers: master tables over the candidate splice-layer UNION
    # [freeze-manifest A(iv)]; nc = 72 concepts; small D for the mock.
    D = 8
    union = [1, 2, 3, 5, 7, 8, 9, 11]
    nc = C

    def kvec(tag, c, li):
        return [2.0 * _hashf("vec", tag, c, li, d) - 1.0 for d in range(D)]

    def norm(v):
        return math.sqrt(sum(x * x for x in v)) or 1.0

    kvals = {}
    for c in range(nc):
        for li, lay in enumerate(union):
            kvals[(c, li)] = kvec("K", c, li)

    def flat(table):
        out = []
        for c in range(nc):
            for li in range(len(union)):
                out.extend(table[(c, li)])
        return out

    kaec_write(cdir / "k-true.kaec", nc, union, D, flat(kvals))

    def rescaled(tag_or_map):
        """Reference-norm rule [DES §R2]: every carrier rescaled per (c,l)
        to ||v^K_{c,l}||."""
        t = {}
        for c in range(nc):
            for li in range(len(union)):
                if isinstance(tag_or_map, str):
                    v = kvec(tag_or_map, c, li)
                else:
                    v = kvals[(tag_or_map[c], li)]
                s = norm(kvals[(c, li)]) / norm(v)
                t[(c, li)] = [x * s for x in v]
        return t

    carriers = {"K": {"path": str(cdir / "k-true.kaec")},
                "d0": {"path": str(cdir / "d0-seed7.kaec"),
                       "meta": {"seed": PILOT_D0_SEED}},
                "d2": {"path": str(cdir / "d2-dict.kaec")},
                "d1-drng": {}}
    kaec_write(cdir / "d0-seed7.kaec", nc, union, D,
               flat(rescaled("d0-%d" % PILOT_D0_SEED)))
    kaec_write(cdir / "d2-dict.kaec", nc, union, D, flat(rescaled("d2")))
    for s in DRNG_SEEDS:
        der = seeded_derangement(nc, s)
        p = cdir / ("d1-drng-%d.kaec" % s)
        kaec_write(p, nc, union, D, flat(rescaled(der)))
        carriers["d1-drng"][str(s)] = {
            "path": str(p),
            "meta": {"seed": s, "derangement": der,
                     "layerwise_norm_matched": True}}
    pder = seeded_derangement(nc, PILOT_KDRNG_SEED)
    kaec_write(cdir / "k-drng-11.kaec", nc, union, D, flat(rescaled(pder)))

    # semantics re-verification MOCK attestation (ASM-1971)
    semlog = fx / "mock-semantics-reverification.log"
    semlog.write_text("MOCK colibri knob-semantics re-verification "
                      "attestation (ASM-1971): stub engine, $0. The REAL "
                      "attestation is produced on the bring-up'd instance "
                      "alongside the pilot (design §R-REV4.2 step 3).\n",
                      encoding="utf-8")

    # [ASM-2513] deterministic MOCK hot-expert stats-file: the $0 oracle
    # exercises the accept+hash+verify+record path with a SHAPED mock
    # pin (M4-measured '<layer> <expert> <count>' triples — accum20.stats
    # format), NEVER the real GCS-resident dev pin (pin_50gb.stats
    # 6802cc97..., which in any case does NOT transfer: the campaign
    # pin is the licensed bring-up-derived pin, run for the WHOLE
    # campaign [REV-C/REV-E — the §5.4 full-corpus re-derivation is
    # WITHDRAWN/deferred, bead kernel-of-truth-8cpm]). Deterministic
    # literals — seeded by nothing, like every fixture here.
    pin_path = fx / "mock-pin.stats"
    pin_path.write_text(
        "".join("%d %d %d\n" % (3 + (i % 12), i, 4096 - 17 * i)
                for i in range(128)),
        encoding="utf-8")

    # [REV-B ASM-2516] mock bring-up gate MODEL + tokens-full sidecar: the
    # addendum-(7) pilot->main seam consumes the SAME frozen model as the
    # bring-up gate — the $0 oracle exercises the sha-verify + per-item +
    # reserve-inclusive path end-to-end. SHAPED mock (tokenizer mode MOCK,
    # _allow_mock; NEVER a license input): knot s-level ~stub scale, kappa
    # unbounded under mock (a real artifact enforces ADD7_KAPPA_BOUNDS).
    tokens_path = fx / "mock-tokens-full.jsonl"

    def _mock_t(key):
        # [REV-C F5v] deterministic HETEROGENEOUS per-item T in [16, 52]
        # (Tp = T+8 <= 60 stays under the mock max knot 64): the REV-B
        # uniform T=24 traversed the per-item code without proving
        # per-item projection — distinct T per item does.
        return 16 + int(hashlib.sha256(key.encode("utf-8"))
                        .hexdigest()[:4], 16) % 37

    with open(tokens_path, "w", encoding="utf-8") as f:
        for iid in split_ids["test"]:
            t = _mock_t("main-tmpl:%s" % iid)
            f.write(json.dumps({"key": "main-tmpl:%s" % iid,
                                "pop": "main-tmpl", "m": 7, "W": t,
                                "T": t}) + "\n")
            f.write(json.dumps({"key": "main-d3:%s" % iid,
                                "pop": "main-d3", "m": 1, "W": t + 3,
                                "T": t + 3}) + "\n")
        for iid in split_ids["dev"]:
            t = _mock_t("pilot:%s" % iid)
            f.write(json.dumps({"key": "pilot:%s" % iid, "pop": "pilot",
                                "m": 22, "W": t, "T": t}) + "\n")
        for iid in split_ids["guard"]:
            t = _mock_t("guard:%s" % iid)
            f.write(json.dumps({"key": "guard:%s" % iid, "pop": "guard",
                                "m": 11, "W": t, "T": t}) + "\n")
    gate_art_path = fx / "mock-bringup-gate.json"
    write_json(gate_art_path, {
        "schema": "kot-f1k-bringup-gate/2", "_mock": True,
        "verdict": "GREEN",
        "tokenizer": {"mode": "MOCK", "sha256": None},
        "model": {"knots_isotonic": [
            {"stratum": "bin0", "T": 16.0, "s": 0.02,
             "se": 0.002, "n": 4},
            {"stratum": "max", "T": 64.0, "s": 0.03,
             "se": 0.003, "n": 1}],
            "cont_tokens_addend": 8},
        # [REV-C F5ii] the /2 model-bundle binding, mock-shaped: the
        # sidecar sha is the REAL sha of the fixture sidecar and the
        # shared-model sha is THE frozen constant — so the driver's
        # binding checks run for real even on the $0 path.
        "model_bundle": {"add7_src_sha256": ADD7_SRC_SHA256,
                         "tokens_full_sha256": sha256_file(tokens_path)},
        "rate": {"usd_per_hour": SPOT_RATE_DEFAULT},
        "pin": {"pin_file_sha256": None, "pin_gb": 48.0,
                "regime": "pinned-bringup", "note": "MOCK artifact"}})

    cfg = {
        "engine": {
            "argv": [sys.executable, str(HERE / "mock_colibri.py")],
            "env": {"MOCK_SALT": "f1k-mock-v1",
                    # [FIX-5]+[ASM-2513] pinning ENFORCED even in the
                    # mock so the SAME validate+hash+verify path runs:
                    # PIN = the mock stats-file above (frozen semantics
                    # PIN=<stats-file> — never the legacy literal "1");
                    # PIN_GB = mock placeholder in the M4-measured
                    # 40-50 GB pinnable-headroom band (m4.json
                    # h_pin_by_G; the REAL value is fixed at bring-up
                    # from measured free RAM, DES §7.1:639)
                    "PIN": str(pin_path), "PIN_GB": "48"},
            "note": "MOCK stub — a real run points argv at the patched "
                    "colibri glm binary + snapshot args"},
        "eval_manifest": str(ev_path),
        "corpora": {
            "f1k-eval-v1": {
                "dir": str(eval_dir),
                "expected_kot_corpus_hash": kot_corpus_hash(eval_dir),
                "provenance": "MOCK fixtures (SHAPED only; real corpus is "
                              "a separate PINNED-AT-INPUTS build)"},
            "f1k-carriers-v1": {
                "dir": str(cdir),
                "expected_kot_corpus_hash": kot_corpus_hash(cdir),
                "provenance": "MOCK fixtures"},
            "f1k-trigger-map-v1": {
                "dir": str(tdir),
                "expected_kot_corpus_hash": kot_corpus_hash(tdir),
                "provenance": "MOCK fixtures"},
        },
        "carriers": carriers,
        "pilot": {
            "layer_sets": {"L1": [5], "L2": [2, 5, 8, 11],
                           "L3": [1, 3, 5, 7, 9, 11]},
            # [FIX-6] multipliers + the bring-up-measured mean native
            # expert weight (mock value)
            "g_multipliers": [0.5, 1.0, 2.0],
            "mean_native_expert_weight": 0.35,
            "dev_subset_ids": ["dev-%03d-0" % c for c in range(
                PILOT_DEV_SUBSET_N)],
            "panel": {
                "members": {
                    "panel-0": {"path": str(cdir / "k-true.kaec")},
                    "panel-1": {"path": str(cdir / "k-drng-11.kaec"),
                                "meta": {"seed": PILOT_KDRNG_SEED,
                                         "derangement": pder}},
                    "panel-2": {"path": str(cdir / "d2-dict.kaec")},
                    "panel-3": {"path": str(cdir / "d0-seed7.kaec"),
                                "meta": {"seed": PILOT_D0_SEED}}},
                "families": {"fam-a": ["panel-0", "panel-1"],
                             "fam-b": ["panel-2"],
                             "fam-c": ["panel-3"]},
                "k_true_member": "panel-0",
                "placebo_family": "fam-c"}},
        "freeze": {
            "manifest_flags": {
                "pre_spend_committed": True, "b0_addendum_committed": True,
                "entry5_committed": True, "entry7_committed": True,
                "entry6_committed": True,
                "test_untouched_until_complete": True,
                "_note": "MOCK: real values are coordinator commit states"},
            "id_list_hashes": id_hashes},
        "template_checks": {"labels_single_token": True,
                            "header_cue_labels_trigger_free": True},
        "inference": {"method": "signflip", "dev_sign_symmetry_pass": True},
        "replace": {
            # [FIX-3] the MOCK engine implements REPLACE (KAE_MODE=1 with a
            # distinct effect) so the conditional path is exercised
            # end-to-end; the REAL gate-0 engine sets this FALSE (stub).
            "engine_supported": True,
            "io_saving_bytes_per_gated_token": 8192.0,
            "note": "MOCK: io saving is a placeholder measured value"},
        "semantics_reverification": {
            "performed": True, "evidence_path": str(semlog),
            "note": "MOCK attestation (ASM-1971)"},
        "power": {"rho_u": RHO_U, "joint_mde_points_at_rho_u": 4.09,
                  # [R6-4] the REGISTERED per-rung co-primary power table
                  # (ASM-2371, frozen record verbatim — real values, not
                  # mock inventions) + the ASM-2376 intersection sim block
                  # (poc/f1k-askability/power_intersection_n1573.py)
                  "mc_exact_power": {"mu_star": 4.09, "n_sim": 10000,
                                     "joint_power": {"K-1": 0.8043,
                                                     "K-2": 0.8058,
                                                     "K-3": 0.8001},
                                     "seed": PERM_SEED, "pass": True},
                  "mc_intersection": {
                      "lambda_grid": [0.0, 0.25, 0.5, 0.75, 1.0],
                      "intersection_power_by_lambda": [0.5220, 0.5675,
                                                       0.6165, 0.6763,
                                                       0.7984],
                      "range_under_family": [0.5220, 0.7984],
                      "at_lambda_0.5": 0.6165,
                      "mc_se_max": 0.005, "seed": PERM_SEED,
                      "source": "poc/f1k-askability/reports/"
                                "power-intersection-n1573.json"}},
        # [R6-4]-style REAL registered figures, not mock inventions
        # (HOLD round-6, 2026-07-16): the pinned analysis now enforces
        # BUDGET-HONESTY SCALE FLOORS (a real mandatory campaign is
        # ~$146 / 521.2 metered hours at the ASM-2374 corner — a
        # zero/under-reported ledger is never a valid success record),
        # so the $0 mock's cost CONFIG carries the ASM-2374
        # planning-scale prior-spend/construction figures; the mock's
        # own metered run seconds/prefills accrue on top exactly as a
        # real run's would. Still $0 REAL spend — these are ledger
        # fixture values, disclosed here, exercising the same emission
        # surface the real run uses.
        "cost": {"spot_rate_usd_per_hour": SPOT_RATE_DEFAULT,
                 "usd_spent_prior": 146.0,
                 # [REV-D 1d] REQUIRED prior-hours key. 0.0 IS the
                 # registered corner figure, not an invention: the
                 # ASM-2374 corner's $146 usd_spent_prior is the PRICED
                 # construction time (521.2 h x $0.28 = $145.94) — no
                 # failed-session/pre-construction hours exist in the
                 # registered planning corner. The nonzero path (prior
                 # hours flip a 900 h STOP) is probed below against the
                 # SAME add7_hours_basis/add7_cap_breach helpers.
                 "prior_instance_hours": 0.0,
                 "construction_instance_hours": 521.2},
        # [REV-B ASM-2516] the addendum-(7) seam's REQUIRED model inputs
        # (sha-verified fail-closed; a REAL campaign points these at the
        # landed gate run's artifacts, shas from bringup-gate.json)
        "affordability": {
            "tokens_full_path": str(tokens_path),
            "tokens_full_sha256": sha256_file(tokens_path),
            "gate_artifact_path": str(gate_art_path),
            "gate_artifact_sha256": sha256_file(gate_art_path),
            "_allow_mock": True},
    }
    cfg_path = fx / "mock-config.json"
    write_json(cfg_path, cfg)
    return cfg_path


def run_analysis(run_record_path):
    """DIRECT pure-function ingest of the run record by the PINNED
    analysis/f1k.py on stdin. NOTE [R3-SEAM]: this is a SUPPLEMENTARY
    shape check only — it bypasses log-append/verdict-gen and proves
    nothing about the official path; the REAL seam (log-append ->
    verdict-gen -> analysis -> verdict) is exercised by
    run_official_seam below (HOLD round-3 item 7: the pre-round-3 mock
    had ONLY this direct call, so the driver had never been tested
    through the official path — and could not be, since its record was
    not kot-log/1-conformant).

    HOLD ROUND-5 (2026-07-16): the pinned analysis now REQUIRES the
    kot-log/1 chain fields on every record line (an UNSTAMPED record —
    one that never went through log-append, the single write path — must
    never validate), so this supplementary check stamps the SAME sentinel
    fields log-append would stamp (schema_version / seq 0 / zero
    prev_sha256 / fixed mock ts / experiment / runner-1) onto a COPY of
    the body before piping — mirroring the stamp, never bypassing it; the
    REAL stamp + chain walk are still exercised end-to-end by
    run_official_seam. The emitted run-record BODY on disk stays
    bare (log-append owns the real stamp)."""
    if not ANALYSIS_SCRIPT.exists():
        fail("ERR_F1K_ANALYSIS", "pinned analysis missing: %s"
             % ANALYSIS_SCRIPT)
    body = json.loads(Path(run_record_path).read_text(encoding="utf-8"))
    stamped = dict(body)
    stamped.update({"schema_version": "kot-log/1", "seq": 0,
                    "prev_sha256": "0" * 64,
                    "ts": "2026-07-16T00:00:00Z",
                    "experiment": "f1k", "runner": "runner-1"})
    proc = subprocess.run([sys.executable, str(ANALYSIS_SCRIPT)],
                          input=json.dumps(stamped, sort_keys=True) + "\n",
                          capture_output=True, text=True)
    return proc


def run_official_seam(outdir, tag, rec_path, tamper=None):
    """[R3-SEAM] Drive the REAL official ingestion path end-to-end in an
    ISOLATED sandbox repo root:

        driver run-record BODY -> tools/registry/log-append.py (the single
        write path: kot-log/1 schema validation, chain stamping, raw-
        metrics rule) -> tools/registry/verdict-gen.py (frozen-record hash
        check, eligibility, D10-PAIRED rows+sidecar pin verification,
        pinned-analysis execution, frozen verdict_rules) ->
        registry/verdicts/f1k.json

    Sandboxed because a REAL results-log/f1k.jsonl line is a lawful-window
    event (the RT-5 cutoff witness) that a $0 mock must never create. The
    sandbox carries byte-identical copies of the frozen record, frozen
    index, schemas, and the pinned analysis, plus the mock rows/sidecar at
    their exact repo-relative paths — verdict-gen's own hash checks then
    hold or fail exactly as they would on the real repo. `tamper(side)`
    mutates the sandbox sidecar JSON and re-pins its sha in the record
    body (an attacker-consistent tamper: every sha check stays green, the
    VERDICT must still refuse). Returns the verdict object."""
    sb = Path(outdir) / ("seam-" + tag)
    shutil.rmtree(str(sb), ignore_errors=True)
    (sb / "registry" / "experiments").mkdir(parents=True)
    (sb / "analysis").mkdir(parents=True)
    shutil.copytree(str(ROOT / "registry" / "schema"),
                    str(sb / "registry" / "schema"))
    for rel in ("registry/experiments/f1k.json", "registry/frozen-index.json",
                "analysis/f1k.py"):
        shutil.copy2(str(ROOT / rel), str(sb / rel))
    body = json.loads(Path(rec_path).read_text(encoding="utf-8"))
    for ent in body["artifacts"]:
        dst = sb / ent["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(ROOT / ent["path"]), str(dst))
    if tamper is not None:
        side_ent = [a for a in body["artifacts"]
                    if a["role"] == "sidecar"][0]
        sp = sb / side_ent["path"]
        side = json.loads(sp.read_text(encoding="utf-8"))
        tamper(side)
        write_json(sp, side)
        side_ent["sha256"] = sha256_file(sp)   # attacker-consistent re-pin
    tools = ROOT / "tools" / "registry"
    p = subprocess.run(
        [sys.executable, str(tools / "log-append.py"), "--experiment",
         "f1k", "--agent-id", "runner-1", "--record", "-", "--root",
         str(sb)],
        input=json.dumps(body, sort_keys=True), capture_output=True,
        text=True)
    if p.returncode != 0:
        fail("ERR_F1K_SEAM", "official seam (%s): log-append REFUSED the "
             "driver record: %s" % (tag, p.stderr.strip()[:600]))
    p = subprocess.run(
        [sys.executable, str(tools / "verdict-gen.py"), "--experiment",
         "f1k", "--agent-id", "coordinator-1", "--root", str(sb),
         "--computed-at", "2026-07-16T00:00:00Z"],
        capture_output=True, text=True)
    if p.returncode != 0:
        fail("ERR_F1K_SEAM", "official seam (%s): verdict-gen failed: %s"
             % (tag, p.stderr.strip()[:600]))
    vpath = sb / "registry" / "verdicts" / "f1k.json"
    return json.loads(vpath.read_text(encoding="utf-8"))


def fix_line_refs():
    """Realized line numbers of every [FIX-n] anchor in THIS file — printed
    by the --mock self-check so the coordinator's re-review can jump to
    each fix site."""
    refs = {}
    for i, line in enumerate(
            Path(__file__).read_text(encoding="utf-8").splitlines(), 1):
        for m in re.finditer(r"\[FIX-(\d)\]", line):
            refs.setdefault(m.group(1), []).append(i)
    return {k: v for k, v in sorted(refs.items())}


def mock_main(args):
    outdir = Path(args.outdir or (HERE / "mock-out")).resolve()
    # deterministic mock: start from a clean slate (stale checkpoints from
    # an earlier protocol revision must never satisfy the new schedule)
    for sub in ("pilot", "guard", "test", "fixtures", "mock-gold",
                "seam-official", "seam-tampered", "cost-stop-probe",
                "cost-stop-probe-init", "carrier-prov-probes",
                "resume-auth-probes"):
        shutil.rmtree(str(outdir / sub), ignore_errors=True)
    try:
        (outdir / "cost-ledger.json").unlink()
    except OSError:
        pass
    try:
        # [ASM-2513 v4] the clean slate removes the SPEND-START
        # sentinel WITH the ledger it guards — the deterministic $0
        # oracle re-runs from scratch by design; one of exactly two
        # lawful removals (the other: the maintainer-authorized
        # archiving reset, §1e recovery text). The REAL campaign path
        # never deletes it.
        (outdir / SPEND_START_NAME).unlink()
    except OSError:
        pass
    outdir.mkdir(parents=True, exist_ok=True)
    print("== F1-K MOCK end-to-end validation ($0; stub engine; NOT a "
          "feasibility result) ==")
    cfg_path = gen_mock_fixtures(outdir)
    cfg = load_config(cfg_path)
    corpus_pins = verify_corpus_pins(cfg, mock=True)
    # [R9-PROV] carrier-construction provenance gate — mock fixtures carry
    # no construction report (DISCLOSED, mock-only); the witness pins that
    # DO exist (the K table bytes) still ride the run record so the
    # official seam exercises the pins_observed emission surface.
    carrier_prov, carrier_pins = verify_carrier_construction(cfg,
                                                             mock=True)
    write_json(outdir / "carrier-provenance.json", carrier_prov)
    ev = load_eval_manifest(cfg["eval_manifest"])
    verify_id_lists(cfg, ev)
    ledger = Ledger(outdir, cfg)
    gold_dir = outdir / "mock-gold"
    gold_dir.mkdir(exist_ok=True)

    # 1. pilot: (L,g) selection + dev-96 post-freeze + gates + addenda
    frozen = phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=gold_dir)

    # 1b. negative probe: KaE fail-closed [FIX-2] — fault-inject a carrier
    # load failure into the stub and assert the driver ABORTS before any
    # spliced item is scored as baseline.
    print("probe: fault-injecting a KaE load failure — the next "
          "ERR_F1K_KAE_ENGAGE line is EXPECTED")
    probe_dir = outdir / "pilot" / "kae-failclosed-probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    probe_env = arm_env(cfg, "K", None, str(probe_dir), frozen)
    probe_env["MOCK_KAE_FORCE_LOAD_FAIL"] = "1"
    kae_failclosed = False
    try:
        run_scoring_pass(cfg, ev["guard"][:1], "probe:K", 0, None,
                         probe_env, probe_dir / "rows.jsonl", set(),
                         mock_gold_dir=gold_dir, phase="probe")
    except SystemExit as e:
        kae_failclosed = (e.code == 2)
    probe_rows = (probe_dir / "rows.jsonl")
    kae_failclosed = kae_failclosed and (
        not probe_rows.exists() or not probe_rows.read_text().strip())

    # committed decisions drive EXECUTION [FIX-3]/[FIX-4]
    d3_deferred, replace_run, replace_gate = \
        enforce_pretest_commits(cfg, outdir)
    passes = main_arm_passes(d3_deferred, replace_run)

    # 2. guard: byte-identity (REPLACE included when scheduled)
    guard_report = phase_guard(cfg, ev, outdir, frozen, replace_run,
                               ledger, mock_gold_dir=gold_dir)

    # 3. dose validation (would run before ANY spliced spend in a real run)
    dose = validate_dose(cfg["carriers"])

    # 4. test campaign with a FORCED interruption + resume (spot-interruption
    #    checkpoint validation [COST lever 1])
    interrupted = False
    try:
        phase_test(cfg, ev, outdir, frozen, passes, ledger,
                   mock_gold_dir=gold_dir,
                   interrupt_state={"count": 0, "after": 2000})
    except MockInterrupt:
        interrupted = True
        print("test: simulated spot interruption after 2000 units -> "
              "resuming from per-item checkpoint")
    if not interrupted:
        fail("ERR_F1K_MOCK", "forced interruption did not fire — resume "
             "path not exercised")
    rows_path, n_resumed = phase_test(cfg, ev, outdir, frozen, passes,
                                      ledger, mock_gold_dir=gold_dir)
    done, rows = read_ckpt(rows_path)
    expected_units = N_TEST * len(passes)
    assert len(done) == expected_units, "unit count"

    # 5. sidecar + run record + pinned analysis ingest
    sidecar_path = build_sidecar(cfg, outdir, guard_report, dose, ledger,
                                 d3_deferred, replace_gate, replace_run)
    rec_path = emit_run_record(outdir, rows_path, sidecar_path,
                               pins_observed=carrier_pins)  # [R9-PROV]
    proc = run_analysis(rec_path)
    ok = proc.returncode == 0
    verdict_bits = {}
    gates_all = False
    if ok:
        out = json.loads(proc.stdout)
        a, g = out["analysis"], out["gates"]
        gates_all = all(g.values())
        verdict_bits = {
            "gates_all_true": gates_all,
            "inference_method": a["inference_method"],
            "k1_lift_points": a["k1_lift_points"], "k1_p": a["k1_p"],
            "k1_joint_pass": a["k1_joint_pass"],
            "k2_joint_pass": a["k2_joint_pass"],
            "pass_gate": a["pass_gate"],
            "ladder_rung_reached": a["ladder_rung_reached"],
            "kill_fired": a["kill_fired"], "null_equiv": a["null_equiv"],
            "replace_ran": a["replace_ran"],
        }
        write_json(outdir / "test" / "analysis-output.json", out)

    # 5b. [R3-ATTEST]/[R3-POWER]/[R3-COST] fail-closed probes (each prints
    # an EXPECTED ERR_F1K_* line) — the round-3 laundering/pinning/cost
    # classes, each proven CLOSED against the live code paths.
    import copy as _copy

    def expect_stop(thunk):
        try:
            thunk()
        except SystemExit as e:
            return e.code == 2
        return False

    print("probe: round-3 fail-closed probes — the next ERR_F1K_* lines "
          "are EXPECTED")
    side_sha_before = sha256_file(sidecar_path)
    cfg_bad = _copy.deepcopy(cfg)
    cfg_bad["freeze"]["manifest_flags"]["entry6_committed"] = "false"
    launder_emit_closed = expect_stop(
        lambda: build_sidecar(cfg_bad, outdir, guard_report, dose, ledger,
                              d3_deferred, replace_gate, replace_run))
    launder_gate_closed = expect_stop(
        lambda: enforce_pretest_commits(cfg_bad, outdir))
    cfg_bad2 = _copy.deepcopy(cfg)
    cfg_bad2["template_checks"]["labels_single_token"] = "true"
    launder_tpl_closed = expect_stop(
        lambda: build_sidecar(cfg_bad2, outdir, guard_report, dose, ledger,
                              d3_deferred, replace_gate, replace_run))
    cfg_bad3 = _copy.deepcopy(cfg)
    cfg_bad3["carriers"]["d1-drng"]["101"]["meta"][
        "layerwise_norm_matched"] = "true"
    launder_dose_closed = expect_stop(
        lambda: validate_dose(cfg_bad3["carriers"]))
    launder_closed = (launder_emit_closed and launder_gate_closed
                      and launder_tpl_closed and launder_dose_closed
                      and sha256_file(sidecar_path) == side_sha_before)

    cfg_pow = _copy.deepcopy(cfg)
    cfg_pow["power"]["mc_exact_power"]["joint_power"] = {
        "K-1": 0.9, "K-2": 0.9, "K-3": 0.9}
    power_pin_closed = expect_stop(lambda: validate_power(cfg_pow))
    cfg_pow2 = _copy.deepcopy(cfg)
    cfg_pow2["power"]["mc_intersection"] = {}
    power_inter_closed = expect_stop(lambda: validate_power(cfg_pow2))

    cfg_cost = _copy.deepcopy(cfg)
    cfg_cost["cost"]["usd_spent_prior"] = 154.9
    led2 = Ledger(outdir / "cost-stop-probe", cfg_cost)  # 154.9 <= cap: OK
    cost_stop_closed = expect_stop(lambda: led2.add("test", 4 * 3600.0,
                                                    100))
    led2_disk = json.loads((outdir / "cost-stop-probe" /
                            "cost-ledger.json").read_text(encoding="utf-8"))
    cost_stop_closed = (cost_stop_closed
                        and led2_disk["phase_seconds"].get("test", 0) > 0)
    cfg_cost2 = _copy.deepcopy(cfg)
    cfg_cost2["cost"]["usd_spent_prior"] = 156.0
    cost_init_closed = expect_stop(
        lambda: Ledger(outdir / "cost-stop-probe-init", cfg_cost2))

    # 5b2. [R9-PROV] carrier-construction provenance-gate probes (carrier
    # re-review item 8, 2026-07-16) — the mock-D=6144-carriers-ingested-
    # for-real exploit class, each proven CLOSED against the live gate,
    # plus a VALID real-mode fixture positive control (sparse tables:
    # correct KAEC headers + exact fp32 sizes + report-pinned shas, $0).
    print("probe: [R9-PROV] carrier-provenance fail-closed probes — the "
          "next ERR_F1K_CARRIERPROV lines are EXPECTED")
    prov_root = outdir / "carrier-prov-probes"
    prov_root.mkdir(parents=True, exist_ok=True)
    prov_arts = {}
    for k, payload in (("tokenizer_artifact", b"mock-pinned-tokenizer"),
                       ("engine_weights_artifact",
                        b"mock-pinned-engine-weights"),
                       ("dump_patch_artifact", b"mock-pinned-dump-patch")):
        p = prov_root / (k + ".bin")
        p.write_bytes(payload)
        prov_arts[k] = p
    prov_man_sha = sha256_file(CONSTRUCTION_MANIFEST) \
        if CONSTRUCTION_MANIFEST.is_file() else "0" * 64

    # [R10-2] a cheap NON-DEGENERATE per-(c,l) body pattern: zero-mean,
    # std/rms == 1, 16/6144 nonzero (>= the 1/1024 floor) — written sparse
    # (16 f32 at each cell start), so the fixture stays $0-sized on disk
    # while every cell passes the full-coverage non-degeneracy scan.
    NONDEGEN_CELL_PATTERN = struct.pack(
        "<16f", *[v for v in (1.0, -1.0, 0.5, -0.5, 0.25, -0.25, 2.0, -2.0,
                              0.75, -0.75, 1.5, -1.5, 0.125, -0.125,
                              3.0, -3.0)])

    def _prov_fixture(tag, mode="real", layers=None, D=D_REGISTERED,
                      tables=True, degenerate=False, prov_paths=None,
                      content_witness=True):
        d = prov_root / tag
        shutil.rmtree(str(d), ignore_errors=True)
        d.mkdir(parents=True)
        lay = list(REGISTERED_SPLICE_LAYERS if layers is None else layers)
        nl = len(lay)
        arts = prov_paths if prov_paths is not None else prov_arts
        binding = {
            "mode": mode, "manifest_sha256": prov_man_sha,
            "tokenizer_sha256":
                sha256_file(arts["tokenizer_artifact"]),
            "engine_weights_sha256":
                sha256_file(arts["engine_weights_artifact"]),
            "dump_patch_sha256":
                sha256_file(arts["dump_patch_artifact"]),
            "construction_seed": REGISTERED_CONSTRUCTION_SEED,
            "layers": lay}
        names = ["k-true.kaec", "d0-seed7.kaec", "d2-dict.kaec"] + \
                ["d1-drng-%d.kaec" % s for s in DRNG_SEEDS]
        tbl = {}
        if tables:
            hdr = b"KAEC" + struct.pack("<iii", C_REGISTERED, nl, D) + \
                struct.pack("<%di" % nl, *lay)
            size = 16 + 4 * nl + 4 * C_REGISTERED * nl * D
            sha_common = None
            for nm in names:
                p = d / nm
                with open(p, "wb") as f:
                    f.write(hdr)
                    f.truncate(size)        # sparse fp32 body ($0)
                    if not degenerate:      # [R10-2] non-degenerate cells
                        for c in range(C_REGISTERED):
                            for li in range(nl):
                                f.seek(16 + 4 * nl
                                       + 4 * (c * nl + li) * D)
                                f.write(NONDEGEN_CELL_PATTERN)
                if sha_common is None:
                    sha_common = sha256_file(p)
                tbl[nm] = {"sha256": sha_common, "bytes": size}
        rep = {
            "mode": mode, "binding": binding,
            "construction_seed": REGISTERED_CONSTRUCTION_SEED,
            "layers": lay, "D": D, "nc": C_REGISTERED,
            "engine_provenance_echo": {
                "expected_seed": REGISTERED_CONSTRUCTION_SEED,
                "verified_batches": C_REGISTERED,
                "sample": "[KAE-DUMP] armed: %d layers, D=%d, seed=%d"
                          % (nl, D, REGISTERED_CONSTRUCTION_SEED)},
            "tables": tbl}
        if content_witness:
            # [R10-3] shape-valid checkpoint-content witness (probe pins)
            rep["checkpoint_content_sha256"] = [
                hashlib.sha256(b"prov-probe-ckpt-%d" % c).hexdigest()
                for c in range(C_REGISTERED)]
        write_json(d / "construction-report.json", rep)
        return {"carriers": {
                    "K": {"path": str(d / "k-true.kaec")},
                    "d0": {"path": str(d / "d0-seed7.kaec")},
                    "d2": {"path": str(d / "d2-dict.kaec")},
                    "d1-drng": {str(s):
                                {"path": str(d / ("d1-drng-%d.kaec" % s))}
                                for s in DRNG_SEEDS}},
                "carrier_provenance": {k: str(v)
                                       for k, v in arts.items()}}

    cfg_prov_ok = _prov_fixture("valid-real")
    prov_pos, prov_pos_pins = verify_carrier_construction(cfg_prov_ok,
                                                          mock=False)
    prov_pos_ok = (prov_pos["mode"] == "real"
                   and "carrier-construction-report.mode-real"
                   in prov_pos_pins
                   and len(prov_pos["tables_byte_witnessed"]) == 6)
    prov_none = {"carriers": {"K": {"path": str(prov_root / "no-report" /
                                                "k-true.kaec")}}}
    prov_c1 = expect_stop(
        lambda: verify_carrier_construction(prov_none, mock=False))
    prov_c2 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("mode-mock", mode="mock", tables=False), mock=False))
    prov_c3 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("wrong-layers", layers=[1, 2, 3, 5, 7, 8, 9, 11],
                      tables=False), mock=False))
    prov_c4 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("wrong-D", D=8, tables=False), mock=False))
    cfg_bad_art = _copy.deepcopy(cfg_prov_ok)
    bad_art = prov_root / "wrong-tokenizer.bin"
    bad_art.write_bytes(b"NOT-the-pinned-tokenizer")
    cfg_bad_art["carrier_provenance"]["tokenizer_artifact"] = str(bad_art)
    prov_c5 = expect_stop(
        lambda: verify_carrier_construction(cfg_bad_art, mock=False))
    cfg_tamper = _prov_fixture("tampered-table")
    with open(cfg_tamper["carriers"]["d2"]["path"], "ab") as f:
        f.write(b"\x00")                    # byte-tamper vs the report pin
    prov_c6 = expect_stop(
        lambda: verify_carrier_construction(cfg_tamper, mock=False))
    # [R10-2] the round-10 exploit: a correctly-SHAPED, report-coherent,
    # mode=real table set whose bodies are ALL-ZERO must be REFUSED by the
    # full-coverage non-degeneracy scan (this exact fixture shape WAS the
    # round-9 positive control and passed end-to-end).
    prov_c7 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("all-zero-real", degenerate=True), mock=False))
    # [R10-1] a relabeled mock construction: binding provenance shas ==
    # the repo mock stack's own digests (artifact-derived, so the item-8
    # derivation check PASSES) must be REFUSED by the mock-stack denylist
    # — a real report can never be satisfied by a mock toolchain.
    prov_c8 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("mock-stack-relabel", prov_paths={
            "tokenizer_artifact": HERE / "mock_tokenizer.py",
            "engine_weights_artifact": HERE / "mock_colibri_dump.py",
            "dump_patch_artifact": HERE / "mock_colibri_dump.py"}),
        mock=False))
    # [R10-3] a real report WITHOUT the checkpoint-content witness list
    # (pre-round-10 shape) is REFUSED.
    prov_c9 = expect_stop(lambda: verify_carrier_construction(
        _prov_fixture("no-content-witness", content_witness=False),
        mock=False))
    prov_closed = (prov_c1 and prov_c2 and prov_c3 and prov_c4
                   and prov_c5 and prov_c6 and prov_c7 and prov_c8
                   and prov_c9)

    # 5b3. [R10-4] campaign resume-authentication probes (carrier
    # re-review content gap 4, 2026-07-16) — the rows.jsonl-bypass exploit
    # class: a resume state that is foreign, tampered, unauthenticated, or
    # carries injected rows must never satisfy (or leak rows into) the
    # campaign; the genuine state must still resume cleanly.
    print("probe: [R10-4] resume-auth fail-closed probes — the next "
          "ERR_F1K_RESUME lines are EXPECTED")
    ra_root = outdir / "resume-auth-probes"
    ra_root.mkdir(parents=True, exist_ok=True)
    tbind = campaign_resume_binding(cfg, "test")

    def _ra_fixture(tag, mutate=None, drop_auth=False):
        d = ra_root / tag
        d.mkdir(parents=True, exist_ok=True)
        rp = d / "rows.jsonl"
        shutil.copy2(rows_path, rp)
        if not drop_auth:
            shutil.copy2(rows_auth_path(rows_path), rows_auth_path(rp))
        if mutate:
            mutate(rp)
        return rp

    ra_pos_done, _, _ = read_ckpt_authed(_ra_fixture("ok"), tbind)
    ra_pos = len(ra_pos_done) == expected_units    # positive control

    def _ra_flip(rp):                   # tamper one completed row
        lines = rp.read_text(encoding="utf-8").splitlines()
        r = json.loads(lines[7])
        r["correct"] = 1 - r["correct"]
        lines[7] = json.dumps(r, sort_keys=True)
        rp.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ra_tamper = expect_stop(
        lambda: read_ckpt_authed(_ra_fixture("tamper", _ra_flip), tbind))
    ra_noauth = expect_stop(
        lambda: read_ckpt_authed(_ra_fixture("noauth", drop_auth=True),
                                 tbind))
    fbind = json.loads(json.dumps(tbind))          # foreign-run binding
    fbind["engine_file_sha256"] = {"other-engine": "0" * 64}
    ra_foreign = expect_stop(
        lambda: read_ckpt_authed(_ra_fixture("foreign"), fbind))

    def _ra_inject(rp):                 # append a row no engine produced
        forged = {"arm": "K", "pass": 9, "item_id": "forged-item",
                  "cluster": "zz", "correct": 1, "pred_label": "a",
                  "gold_label": "a", "tags": []}
        with open(rp, "a", encoding="utf-8") as f:
            f.write(json.dumps(forged, sort_keys=True) + "\n")

    ra_inj_done, _, _ = read_ckpt_authed(_ra_fixture("inject", _ra_inject),
                                         tbind)
    ra_inject = (len(ra_inj_done) == expected_units
                 and ("K", 9, "forged-item") not in ra_inj_done)
    ra_closed = (ra_pos and ra_tamper and ra_noauth and ra_foreign
                 and ra_inject)

    # 5b4. [ASM-2513, v4 probe set] pinning fail-closed probes — the
    # false-attestation exploit class: the legacy literal "1", a missing
    # stats-file, a malformed stats-file, a schema-illegal basename, a
    # non-ASCII "digit" triple, a non-finite PIN_GB, an engine that
    # never armed the hot store, a PRIOR invocation's stale armed banner
    # riding the append-mode log, a ROTATED/REPLACED log pathname
    # carrying a planted banner [v3], a mid-run pin-file/ledger-hash
    # mismatch, a PIN_GB swap at the cross-phase ledger seam, a MISSING
    # ledger beside existing campaign artifacts [v3], a MISSING ledger
    # beside ONLY the SPEND-START sentinel (the spawn-to-checkpoint
    # crash window) [v4], an addendum-7 pin/budget mismatch at pre-test
    # consumption [v3], and a resume under a swapped pin must ALL
    # refuse — while a VIRGIN outdir (no sentinel, no artifacts) must
    # still fresh-init [v4, positive probe] and a same-basis ledger+
    # sentinel pair must still RESUME cleanly [v5, positive probe].
    print("probe: [ASM-2513] pinning fail-closed probes — the next "
          "ERR_F1K_PINNING lines are EXPECTED")
    # [v2] the validated mock pin file, FROM the loaded config (the
    # gen_mock_fixtures local `pin_path` is not in scope at this
    # insertion point) — validate_pinning already resolved it absolute
    pin_path = Path(cfg["engine"]["env"]["PIN"])

    def _pin_cfg(val, gb=None):
        c = _copy.deepcopy(cfg)
        c["engine"]["env"]["PIN"] = val
        if gb is not None:
            c["engine"]["env"]["PIN_GB"] = gb
        return c

    pin_legacy = expect_stop(lambda: validate_pinning(_pin_cfg("1")))
    pin_missing = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(outdir / "fixtures" / "no-such.stats"))))
    badp = outdir / "fixtures" / "malformed-pin.stats"
    badp.write_text("3 0 not-an-int\n", encoding="utf-8")
    pin_malformed = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badp))))
    # [v2, review #3] basename the PINNED schema would reject (space is
    # outside [A-Za-z0-9._+-]) — must fail AT CONFIG LOAD, before spend,
    # even though the file itself is valid and readable
    badn = outdir / "fixtures" / "bad name.stats"
    badn.write_text("3 0 7\n", encoding="utf-8")
    pin_badname = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badn))))
    # [v2, review #2] Unicode-digit triple: '٣'.isdigit() is True and
    # int('٣') == 3 [MEASURED], so v1 would have hashed+accepted a
    # non-ASCII pin list the engine cannot parse
    badu = outdir / "fixtures" / "nonascii-pin.stats"
    badu.write_text("٣ 0 7\n", encoding="utf-8")   # Arabic-Indic 3
    pin_nonascii = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badu))))
    # [v2, review #2] non-finite PIN_GB: NaN slides past `gb <= 0`
    pin_nangb = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(pin_path), gb="nan")))
    pin_infgb = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(pin_path), gb="inf")))
    print("probe: fault-injecting a pin load failure — the next "
          "ERR_F1K_PINNING line is EXPECTED")
    pprobe_dir = outdir / "pilot" / "pin-failclosed-probe"
    pprobe_dir.mkdir(parents=True, exist_ok=True)
    penv = arm_env(cfg, "b0", None, str(pprobe_dir), frozen)
    penv["MOCK_PIN_FORCE_LOAD_FAIL"] = "1"
    pin_unarmed = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, penv,
        pprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    pin_rows = pprobe_dir / "rows.jsonl"
    pin_unarmed = pin_unarmed and (
        not pin_rows.exists() or not pin_rows.read_text().strip())
    # [v2, review #2 — SECURITY] STALE-BANNER-RESUME probe: pre-seed the
    # DETERMINISTIC append-mode stderr log with a byte-perfect armed
    # banner from a "prior invocation", then run an engine that stays
    # SILENT about its pin (MOCK_PIN_SILENT=1). v1's whole-file scan
    # would have gone GREEN on the stale banner — a newly UNPINNED
    # process authorized by a prior run's attestation; v2's pre-spawn
    # offset slice must see NO banner and refuse with zero rows scored.
    print("probe: stale-banner resume — the next ERR_F1K_PINNING line "
          "is EXPECTED (a prior run's banner must authorize NOTHING)")
    sprobe_dir = outdir / "pilot" / "pin-staleban-probe"
    (sprobe_dir / "stderr").mkdir(parents=True, exist_ok=True)
    stale_log = sprobe_dir / "stderr" / "probe.probe:b0.pass0.log"
    stale_log.write_text(
        "[PIN] hot-expert store armed: pinned 128 experts, 2.210 GiB "
        "(budget 48.00 GiB) from mock-pin.stats\n", encoding="utf-8")
    senv = arm_env(cfg, "b0", None, str(sprobe_dir), frozen)
    senv["MOCK_PIN_SILENT"] = "1"
    pin_stale = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, senv,
        sprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    stale_rows = sprobe_dir / "rows.jsonl"
    pin_stale = pin_stale and (
        not stale_rows.exists() or not stale_rows.read_text().strip())
    # [v3, re-review #1] LOG-ROTATION/REPLACEMENT probe: pre-seed the
    # deterministic log (so the pre-spawn offset > 0), then run an
    # engine that is SILENT on its real (fd-inherited) stderr but
    # plants a decoy AT THE PATHNAME — pad bytes >= the offset + a
    # stale armed banner (MOCK_PIN_ROTATE_LOG/_PAD, §1h). The decoy
    # passes the v2 short-file guard and carries a valid banner after
    # the offset, so a NAME-based read goes GREEN on it [MEASURED:
    # decoy-rotation demo, this box 2026-07-18]; the v3 descriptor-
    # bound read sees NO banner on the true file object -> RED, zero
    # rows.
    print("probe: log rotation/replacement swap — the next "
          "ERR_F1K_PINNING line is EXPECTED (a pathname decoy must "
          "authorize NOTHING)")
    rprobe_dir = outdir / "pilot" / "pin-rotate-probe"
    (rprobe_dir / "stderr").mkdir(parents=True, exist_ok=True)
    rot_log = rprobe_dir / "stderr" / "probe.probe:b0.pass0.log"
    rot_log.write_text("prior invocation noise\n", encoding="utf-8")
    renv = arm_env(cfg, "b0", None, str(rprobe_dir), frozen)
    renv["MOCK_PIN_ROTATE_LOG"] = str(rot_log)
    renv["MOCK_PIN_ROTATE_PAD"] = str(rot_log.stat().st_size)
    pin_rotate = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, renv,
        rprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    rot_rows = rprobe_dir / "rows.jsonl"
    pin_rotate = (pin_rotate
                  and (not rot_rows.exists()
                       or not rot_rows.read_text().strip())
                  and b"[PIN] hot-expert store armed"
                  in rot_log.read_bytes())
    #   ^ third conjunct: the decoy really IS at the pathname (the bait
    #     was live) — ONLY the descriptor-bound read refused it
    # [v2, review #6 probe (a)] EXPECTED-HASH mismatch: the ledger's
    # pin_file_sha256 no longer matches the file BYTES (the file grew
    # after ledger init = a mid-run swap) — check_pin_engagement must
    # re-derive from bytes and go RED, zero rows scored.
    print("probe: ledger pin-hash vs file-bytes mismatch — the next "
          "ERR_F1K_PINNING line is EXPECTED")
    hprobe_dir = outdir / "pilot" / "pin-hashswap-probe"
    hprobe_dir.mkdir(parents=True, exist_ok=True)
    pin2 = outdir / "fixtures" / "hashswap-pin.stats"
    pin2.write_text(pin_path.read_text(encoding="utf-8"),
                    encoding="utf-8")
    hcfg = _pin_cfg(str(pin2))
    hled = Ledger(str(hprobe_dir), hcfg)     # hashes pin2 AS IT IS NOW
    with open(pin2, "a", encoding="utf-8") as pf:
        pf.write("3 999 1\n")                # ...then the bytes change
    henv = arm_env(hcfg, "b0", None, str(hprobe_dir), frozen)
    pin_hashswap = expect_stop(lambda: run_scoring_pass(
        hcfg, ev["guard"][:1], "probe:b0", 0, None, henv,
        hprobe_dir / "rows.jsonl", set(), ledger=hled,
        mock_gold_dir=gold_dir, phase="probe"))
    hs_rows = hprobe_dir / "rows.jsonl"
    pin_hashswap = pin_hashswap and (
        not hs_rows.exists() or not hs_rows.read_text().strip())
    # [v2, review #5] PIN_GB swap at the CROSS-PHASE ledger seam: a
    # ledger written under PIN_GB=48 must refuse a re-init (= a phase
    # boundary or resume) whose config carries a different budget.
    print("probe: cross-phase PIN_GB swap — the next ERR_F1K_PINNING "
          "line is EXPECTED")
    gprobe_dir = outdir / "pilot" / "pin-gbswap-probe"
    gprobe_dir.mkdir(parents=True, exist_ok=True)
    Ledger(str(gprobe_dir), cfg)             # ledger under PIN_GB=48
    gb_ledgerswap = expect_stop(
        lambda: Ledger(str(gprobe_dir), _pin_cfg(str(pin_path),
                                                 gb="32")))
    # [v3, re-review #3] MISSING-LEDGER phase-transition probe:
    # campaign evidence exists (a pilot artifact) but cost-ledger.json
    # does NOT — Ledger init must REFUSE to re-initialize (the
    # cross-phase comparison basis is gone; §1e second hunk), naming
    # the recovery path.
    print("probe: missing ledger beside campaign artifacts — the next "
          "ERR_F1K_COST line is EXPECTED")
    mprobe_dir = outdir / "pilot" / "pin-noledger-probe"
    (mprobe_dir / "pilot").mkdir(parents=True, exist_ok=True)
    (mprobe_dir / "pilot" / "pilot-gates.json").write_text(
        "{}", encoding="utf-8")            # evidence present, no ledger
    pin_noledger = expect_stop(lambda: Ledger(str(mprobe_dir), cfg))
    # [v4, round-3 #2] SPAWN-TO-CHECKPOINT CRASH-WINDOW probe: a spawn
    # was attempted (sentinel written, exactly as run_scoring_pass does
    # BEFORE Popen) but the run was interrupted before ANY of the seven
    # artifact/checkpoint paths existed, and cost-ledger.json was then
    # lost — the ONLY evidence is the sentinel. v3's predicate saw
    # nothing here and fresh-inited silently; v4 must refuse.
    print("probe: SPEND-START sentinel beside a missing ledger (spawn-"
          "to-checkpoint crash window) — the next ERR_F1K_COST line is "
          "EXPECTED")
    wprobe_dir = outdir / "pilot" / "pin-spendstart-probe"
    wprobe_dir.mkdir(parents=True, exist_ok=True)
    write_spend_start(Ledger(str(wprobe_dir), cfg), "probe", "b0", 0)
    # [v5, round-4 #1] NORMAL-RESUME positive assertion, BEFORE the
    # unlink: while ledger AND sentinel COEXIST (exactly the state an
    # ordinary interrupted run leaves behind), a SAME-config
    # Ledger(...) is a lawful resume and must PROCEED — a wrong
    # fail-closed here dies loudly (not wrapped in expect_stop), the
    # positive-probe signal, as pin_virgin — reporting the SAME basis:
    # the config-derived pin sha + PIN_GB carried through the §1e
    # resume comparison (exact equality; §1e semantics). With
    # pin_virgin and the post-unlink crash assertion below, this
    # sequence now distinguishes all THREE states: virgin /
    # normal-resume / crash-window.
    wexp = validate_pinning(cfg)
    wres = Ledger(str(wprobe_dir), cfg)          # must NOT stop
    pin_spendresume = (
        (wprobe_dir / "cost-ledger.json").exists()      # the state
        and (wprobe_dir / SPEND_START_NAME).exists()    # under test
        #   really held: ledger + sentinel COEXIST at resume time ^
        and wres.d["expert_pinning"]["pin_file_sha256"]
        == wexp["pin_file_sha256"]
        and float(wres.d["expert_pinning"]["PIN_GB"]) == wexp["PIN_GB"])
    (wprobe_dir / "cost-ledger.json").unlink()   # ...then the ledger is
    #   lost; NO artifact/checkpoint path exists in this outdir
    pin_spendstart = expect_stop(lambda: Ledger(str(wprobe_dir), cfg))
    pin_spendstart = pin_spendstart and \
        (wprobe_dir / SPEND_START_NAME).exists()
    #   ^ second conjunct: the sentinel really IS the only evidence
    #     present — the refusal came from it, not from an artifact
    # [v4, round-3 #2] VIRGIN-OUTDIR fresh-start PRESERVED (positive
    # probe, per the round-3 prescription): no sentinel, no artifacts
    # -> Ledger init must PROCEED (not raise) and persist a fresh
    # ledger. A wrong fail-closed here dies loudly (not wrapped in
    # expect_stop) — the correct signal for a positive probe.
    vprobe_dir = outdir / "pilot" / "pin-virgin-probe"
    vprobe_dir.mkdir(parents=True, exist_ok=True)
    Ledger(str(vprobe_dir), cfg)                 # must NOT stop
    pin_virgin = (vprobe_dir / "cost-ledger.json").exists() and \
        not (vprobe_dir / SPEND_START_NAME).exists()
    # [v3, re-review #3] ADDENDUM-MISMATCH probes: a pilot addendum
    # whose recorded pin sha (or PIN_GB) differs from the CURRENT
    # config must refuse at pre-test consumption (§1e2 helper, exact
    # equality semantics of the ledger seam).
    print("probe: addendum-7 pin/budget mismatch — the next TWO "
          "ERR_F1K_PINNING lines are EXPECTED")
    cur_ep = validate_pinning(cfg)
    pin_addsha = expect_stop(lambda: check_addendum_pinning(
        {"expert_pinning": {"pin_file_sha256": "e" * 64,
                            "PIN_GB": cur_ep["PIN_GB"]}}, cfg))
    pin_addgb = expect_stop(lambda: check_addendum_pinning(
        {"expert_pinning": {"pin_file_sha256": cur_ep["pin_file_sha256"],
                            "PIN_GB": 32.0}}, cfg))
    # [R10-4] pin-swap resume: a binding whose pin-file hash differs is
    # a FOREIGN run — refused like any other binding mismatch.
    pswap = json.loads(json.dumps(tbind))
    pswap["pin_file_sha256"] = "f" * 64
    ra_pinswap = expect_stop(
        lambda: read_ckpt_authed(_ra_fixture("pin-swap"), pswap))
    pin_closed = (pin_legacy and pin_missing and pin_malformed
                  and pin_badname and pin_nonascii and pin_nangb
                  and pin_infgb and pin_unarmed and pin_stale
                  and pin_rotate and pin_hashswap and gb_ledgerswap
                  and pin_noledger and pin_spendstart
                  and pin_spendresume and pin_virgin
                  and pin_addsha and pin_addgb and ra_pinswap)

    # 5c. [R3-SEAM] the OFFICIAL round-trip, both fixtures: the driver's
    # kot-log/1 record through the REAL log-append -> verdict-gen ->
    # pinned-analysis path (sandboxed repo root; see run_official_seam).
    verdict_good = run_official_seam(outdir, "official", rec_path)
    paired = (verdict_good.get("inputs") or {}).get(
        "paired_artifacts_verified") or []
    seam_pass = (verdict_good.get("verdict") == "PASS-PENDING-AUDIT"
                 and len(paired) == 1
                 and paired[0]["rows"]["rows"] == expected_units)

    def _tamper(side):
        side["guard"]["n_items"] = 0    # incomplete guard instrument
    verdict_bad = run_official_seam(outdir, "tampered", rec_path,
                                    tamper=_tamper)
    seam_tamper = verdict_bad.get("verdict") == "INSTRUMENT-INVALID"

    add6 = json.loads((outdir / "pilot" / "addendum-6-inputs.json")
                      .read_text(encoding="utf-8"))
    add5 = json.loads((outdir / "pilot" / "addendum-5-frozen-lg.json")
                      .read_text(encoding="utf-8"))
    led = json.loads((outdir / "cost-ledger.json")
                     .read_text(encoding="utf-8"))
    llog_pilot = outdir / "pilot" / "label-logits.pilot.jsonl"
    llog_test = outdir / "test" / "label-logits.test.jsonl"
    dev96_rows = [r for r in
                  read_ckpt(outdir / "pilot" / "pilot-rows.jsonl")[1]
                  if r["arm"] == "dev96:b0"]
    pg = json.loads((outdir / "pilot" / "pilot-gates.json")
                    .read_text(encoding="utf-8"))["power_gate"]   # [R6-2]
    refs = fix_line_refs()

    def ref(n):
        return "f1k_driver.py:%s" % ",".join(map(str, refs.get(str(n), [])))

    # ---- [REV-C F5] shared-model / bundle-binding / kappa / boundary ----
    print("probe: [REV-C] Add7Model bundle tamper probes — the next "
          "ERR_F1K_AFFORD lines are EXPECTED")
    a7_art = json.loads((outdir / "pilot" /
                         "addendum-7-affordability.json")
                        .read_text(encoding="utf-8"))
    prb = a7_art.get("projection_rev_b") or {}
    kw = prb.get("kappa_weighting") or {}
    t_vals = [json.loads(l)["T"] for l in
              open(cfg["affordability"]["tokens_full_path"],
                   encoding="utf-8") if l.strip()]
    het_ok = len(set(t_vals)) >= 10
    kw_ok = (kw.get("distinct_items") == DEV_N
             and kw.get("n_pass_rows", 0) > DEV_N
             and kw.get("weight_max", 0) > kw.get("weight_min", 0))
    gate_copy = HERE.parents[1] / "gcp" / "f1k_bringup_gate.py"
    own_a7 = add7_block_sha256(__file__)
    shared_ok = (own_a7 == ADD7_SRC_SHA256
                 and add7_block_sha256(gate_copy) == own_a7)
    tam_tok = outdir / "fixtures" / "tokens-tampered.jsonl"
    tam_tok.write_bytes(Path(cfg["affordability"]["tokens_full_path"])
                        .read_bytes() + b"\n")
    cfg_t = json.loads(json.dumps(cfg))
    cfg_t["affordability"]["tokens_full_path"] = str(tam_tok)
    try:
        Add7Model(cfg_t)
        tamper_closed = False
    except DriverError:
        tamper_closed = True
    cfg_t2 = json.loads(json.dumps(cfg))
    cfg_t2["affordability"]["tokens_full_path"] = str(tam_tok)
    cfg_t2["affordability"]["tokens_full_sha256"] = sha256_file(tam_tok)
    try:
        Add7Model(cfg_t2)
        bundle_closed = False
    except DriverError:
        bundle_closed = True
    a7p = Add7Model(cfg)
    a7p.verify_corpus(ev)
    rate_p = float(cfg["cost"]["spot_rate_usd_per_hour"])

    def _p4(d3d, rep, kap):
        sc = a7p.remaining_seconds(ev, d3d, rep, kap)
        sh = a7p.remaining_seconds(ev, d3d, rep, kap, hi=True)
        return (sc / 3600.0 * rate_p, sh / 3600.0 * rate_p,
                sc / 3600.0, sh / 3600.0)

    kap_b = ((USD_CAP - RESERVE_USD_ADD7 - 1.0) * 3600.0 / rate_p
             / a7p.remaining_seconds(ev, True, False, 1.0, hi=True))
    boundary_ok = (add7_cap_breach(_p4(False, True, kap_b), rate_p)
                   and not add7_cap_breach(_p4(True, False, kap_b),
                                           rate_p))

    # ---- [REV-D] strict-bijection + realized-hours probes ----
    print("probe: [REV-D] bijection/prior-hours probes — the next "
          "ERR_F1K_AFFORD / ERR_F1K_COST lines are EXPECTED")
    # (2) a DUPLICATE sidecar key with a CONFLICTING T, re-pinned
    # attacker-consistent through the whole bundle (config shas AND the
    # artifact-recorded model_bundle sha all agree on the duplicated
    # bytes) — only the count-preserving load refuses it; the old
    # set-equality "bijection" passed it silently.
    dup_lines = [l for l in
                 open(cfg["affordability"]["tokens_full_path"],
                      encoding="utf-8") if l.strip()]
    dup_row = json.loads(dup_lines[0])
    dup_row["T"] = dup_row["T"] + 7          # conflicting duplicate T
    dup_tok = outdir / "fixtures" / "tokens-dup.jsonl"
    dup_tok.write_text("".join(dup_lines) + json.dumps(dup_row) + "\n",
                       encoding="utf-8")
    art_dup = json.loads(
        Path(cfg["affordability"]["gate_artifact_path"])
        .read_text(encoding="utf-8"))
    art_dup["model_bundle"]["tokens_full_sha256"] = sha256_file(dup_tok)
    art_dup_p = outdir / "fixtures" / "gate-art-dup.json"
    write_json(art_dup_p, art_dup)
    cfg_dup = json.loads(json.dumps(cfg))
    cfg_dup["affordability"].update({
        "tokens_full_path": str(dup_tok),
        "tokens_full_sha256": sha256_file(dup_tok),
        "gate_artifact_path": str(art_dup_p),
        "gate_artifact_sha256": sha256_file(art_dup_p)})
    try:
        Add7Model(cfg_dup)
        dup_closed = False
    except DriverError:
        dup_closed = True
    # (2b) a DUPLICATE eval item id — set equality would collapse it.
    ev_dup = {"dev": ev["dev"], "test": list(ev["test"]) + [ev["test"][0]],
              "guard": ev["guard"]}
    try:
        a7p.verify_corpus(ev_dup)
        evdup_closed = False
    except DriverError:
        evdup_closed = True
    # (1d) prior_instance_hours REQUIRED (missing key -> fail-closed) ...
    cfg_nh = json.loads(json.dumps(cfg))
    del cfg_nh["cost"]["prior_instance_hours"]
    try:
        Ledger(outdir / "fixtures" / "led-nh", cfg_nh)
        nh_closed = False
    except DriverError:
        nh_closed = True
    # (3) [REV-E] a HAND-EDITED NaN in a required cost key: the bare
    # NaN literal round-trips through Python json [MEASURED], so a
    # nan-poisoned ledger basis is representable on disk — the Ledger
    # finiteness assert refuses it at init, whoever wrote it.
    cfg_nan = json.loads(json.dumps(cfg))
    cfg_nan["cost"]["prior_instance_hours"] = float("nan")
    try:
        Ledger(outdir / "fixtures" / "led-nan", cfg_nan)
        nan_closed = False
    except DriverError:
        nan_closed = True
    # ... and THREADED: prior hours alone flip the 900 h reserve-
    # inclusive cap through the SAME add7_hours_basis + add7_cap_breach
    # phase_pilot uses (521.2 construction + 380 prior + reserve > 900;
    # identical projection sans prior clears).
    led_ph = dict(led)
    led_ph["prior_instance_hours"] = 380.0
    bh_ph = add7_hours_basis(led_ph, 0.0)
    bh_0 = add7_hours_basis(led, 0.0)
    ph_flip = (add7_cap_breach((80.0, 80.0, bh_ph, bh_ph), rate_p)
               and not add7_cap_breach((80.0, 80.0, bh_0, bh_0), rate_p))

    print("\n== MOCK SELF-CHECK (codex FIX-FIRST launch blockers 1-7) ==")
    checks = [
        ("[1] SCORER: robust stdout parse — %d banner line(s) skipped "
         "before results (mock emits real-engine banners), result lines "
         "located by shape validation, label logits + frozen ties LOGGED "
         "(%s, %s; %d tie(s)) [%s]"
         % (BANNERS_SKIPPED["n"], llog_pilot.name, llog_test.name,
            TIES_LOGGED["n"], ref(1)),
         BANNERS_SKIPPED["n"] > 0 and llog_pilot.exists()
         and llog_test.exists()),
        ("[2] KaE FAIL-CLOSED: %d positive engagement checks (armed banner "
         "+ nc/nl/g match per spliced invocation); fault-injected load "
         "failure ABORTED with no row scored as baseline [%s]"
         % (ENGAGEMENT_CHECKS["n"], ref(2)),
         ENGAGEMENT_CHECKS["n"] > 0 and kae_failclosed),
        ("[3] conditional REPLACE per the frozen gate: dev-96 delta_R=%s "
         "-> n_NI=%s -> decision=%s; executed=%s (rows %s); stub "
         "detection armed [%s]"
         % (replace_gate.get("delta_r_dev"), replace_gate.get("n_ni"),
            replace_gate.get("decision"), replace_run,
            "present" if any(r["arm"] == "REPLACE" for r in rows)
            else "absent", ref(3)),
         (replace_gate.get("decision") in ("RUN", "DEFER"))
         and (replace_run == any(r["arm"] == "REPLACE" for r in rows))
         and replace_gate.get("delta_r_dev") is not None),
        ("[4] d3-text deferral honored in EXECUTION: schedule derives from "
         "addendum-7 d3_text_deferred=%s (passes=%d; deferral pure-check: "
         "main_arm_passes(True) drops d3-text) [%s]"
         % (d3_deferred, len(passes), ref(4)),
         (("d3-text", 0, None) in main_arm_passes(False)) and
         (("d3-text", 0, None) not in main_arm_passes(True)) and
         ((("d3-text", 0, None) in passes) == (not d3_deferred))),
        ("[5] expert pinning ENFORCED + RECORDED (ASM-2513 "
         "PIN=<stats-file>): PIN=%s sha256=%.12s... PIN_GB=%s "
         "experts_pinned=%s (%d engine pin verifications, descriptor-"
         "bound evidence) in ledger + sidecar cost.expert_pinning; "
         "legacy \"1\" / missing / malformed / bad-basename / "
         "non-ASCII-digits / non-finite-PIN_GB / unarmed-engine / "
         "STALE-BANNER-RESUME / LOG-ROTATION-SWAP / ledger-hash-"
         "vs-bytes / cross-phase-PIN_GB-swap / MISSING-LEDGER-REINIT / "
         "SPEND-START-CRASH-WINDOW / ADDENDUM-PIN-MISMATCH / "
         "pin-swap-resume ALL "
         "REFUSED (ERR_F1K_PINNING / ERR_F1K_COST); virgin-outdir "
         "fresh init AND same-basis ledger+sentinel NORMAL-RESUME "
         "PRESERVED; spend-start sentinel written by every "
         "metered spawn [%s]"
         % (led["expert_pinning"]["PIN"],
            led["expert_pinning"]["pin_file_sha256"],
            led["expert_pinning"]["PIN_GB"],
            led["expert_pinning"].get("experts_pinned"),
            PIN_CHECKS["n"], ref(5)),
         led.get("expert_pinning", {}).get("PIN") == "mock-pin.stats"
         and len(led["expert_pinning"].get("pin_file_sha256", "")) == 64
         and led["expert_pinning"].get("experts_pinned") == 128
         and PIN_CHECKS["n"] > 0 and pin_closed
         and (outdir / SPEND_START_NAME).exists()),
        #   ^ [v4] final conjunct: the mock campaign's own metered
        #     spawns really wrote the sentinel at the outdir root —
        #     the pre-Popen write is proven on the REAL code path,
        #     not only by the direct-call probe
        ("[6] PILOT: dev-96 scored post-freeze (%d dev96:b0 rows); frozen "
         "g = %.4g x %.4g = %.6g (multiplier x mean native expert "
         "weight); FULL panel validation (seed 11 / d0 seed 7 / {2,1,1} / "
         "identities / norms / derangement reconstruction); (5)/(7)/(6) "
         "flags + gate artifacts enforced pre-test [%s]"
         % (len(dev96_rows), add5["frozen"]["g_multiplier"],
            add5["frozen"]["mean_native_expert_weight"],
            add5["frozen"]["g"], ref(6)),
         len(dev96_rows) == DEV_N
         and add5["frozen"]["g"] == add5["frozen"]["g_multiplier"]
         * add5["frozen"]["mean_native_expert_weight"]
         and add5["panel_validation"]["derangement_reconstructed"]),
        ("[7] frozen constants: z0.80=%s EXACT; n_run=%s EXACT (=1573, "
         "REVISION-6); power block validated (rho_u/N_sim/mu*/seed/"
         "per-rung threshold); ledger resume-safe with pilot+construction "
         "(%s) [%s]"
         % (Z80, add6["n_run"], sorted(led["phase_seconds"]), ref(7)),
         Z80 == 0.842 and add6["n_run"] == N_TEST and N_TEST == 1573
         and "pilot" in led["phase_seconds"]
         and "construction_instance_hours" in led),
        ("[R6] REVISION-6 alignment: EQUALITY-form power gate PASS "
         "(realized %d clusters / %d with m>=8 / n=%d); per-rung "
         "joint_power dict K-1/K-2/K-3 + ASM-2376 intersection block in "
         "the sidecar; worst-case $ at the ASM-2374 pessimistic corner "
         "with the [FREEZE-A] amended envelopes (construction 4,608 "
         "EXACT, pilot <= 2,112 deterministic): mandatory campaign $%.2f "
         "<= cap $%.0f; +REPLACE $%.2f <= cap at the corner (REPLACE "
         "still runs ONLY if its NI gate says RUN and the measured (7) "
         "projection keeps the ledger <= cap — ASM-2374, never a silent "
         "raise)"
         % (pg["n_clusters"], pg["clusters_with_m_ge_8"], pg["n_items"],
            worst_case_usd(False), USD_CAP, worst_case_usd(True)),
         pg["pass"] is True and pg["n_clusters"] == C_REGISTERED
         and pg["n_items"] == N_TEST
         and worst_case_usd(False) <= USD_CAP
         and worst_case_usd(True) <= USD_CAP),
        ("input seams: kot-corpus-hash/1 verified for %s (registry "
         "placeholders + REAL pins honored: mock fixtures disclosed as "
         "DIVERGING, real runs fail closed on any mismatch); id-list "
         "hashes verified; eval/carrier paths contained; NO fabricated "
         "real corpora (fixtures labeled MOCK)"
         % ", ".join(sorted(corpus_pins)),
         len(corpus_pins) == 3),
        ("mock run executed end-to-end (pilot -> KaE probe -> guard -> "
         "test interrupt+resume -> sidecar -> analysis)", True),
        ("analysis/f1k.py ingested the mock output (exit %d, gates all "
         "true: %s)" % (proc.returncode, gates_all), ok and gates_all),
        ("checkpoint/resume validated (forced interruption after 2000 "
         "units; resumed %d units; %d/%d total, no duplicates)"
         % (n_resumed, len(done), expected_units),
         len(done) == expected_units),
        ("guard byte-identity asserted (60 items x spliced passes == b0, "
         "REPLACE included when scheduled: %s)"
         % ("yes" if replace_run else "n/a"),
         guard_report["byte_identical"] is True),   # [R3-ATTEST] strict
        ("dose-exactness pre-validated (seeds %s, fixed-point-free, "
         "norm-matched)" % (list(DRNG_SEEDS),), True),
        ("[R3-ATTEST] attestation laundering CLOSED: string-'false' "
         "manifest flag => build_sidecar FAILS (ERR_F1K_ATTEST, no "
         "coercion, sidecar bytes untouched) AND enforce_pretest_commits "
         "refuses (`is True` reads); string-'true' template check and B0 "
         "dose attestation equally refused — bool() is gone from the "
         "whole attestation surface", launder_closed),
        ("[R3-POWER] power block pinned EXACTLY: 0.9/0.9/0.9 marginals "
         "REJECTED against the registered ASM-2371 table "
         "0.8043/0.8058/0.8001; empty mc_intersection {} REJECTED "
         "(ASM-2376 block required, values pinned)",
         power_pin_closed and power_inter_closed),
        ("[R3-COST] realized-cost stop: accumulation past $155 STOPPED "
         "fail-closed (spend recorded, run halted, NO success record); "
         "over-cap ledger at init/resume STOPPED; the same enforce_cap "
         "runs at sidecar emission", cost_stop_closed and cost_init_closed),
        ("[R9-PROV] carrier-construction provenance gate (re-review "
         "item 8): REAL-mode ingest REFUSES (a) carriers without a "
         "construction report, (b) a mode=mock report — the D=6144 "
         "mock-carrier exploit, (c) non-A(iv) layers [1,2,3,5,7,8,9,11], "
         "(d) D=8, (e) an asserted provenance sha != the DERIVED artifact "
         "digest, (f) a byte-tampered table vs the report pin; a VALID "
         "real-mode fixture (nc=96, D=6144, layers 3..77, artifact-"
         "derived shas, 6 byte-witnessed NON-DEGENERATE tables) PASSES; "
         "mock fixtures DISCLOSED (%.24s); pins_observed (%d pin(s)) "
         "carried on the kot-log/1 record through the OFFICIAL seam"
         % (carrier_prov["mode"], len(carrier_pins)),
         prov_closed and prov_pos_ok and bool(carrier_pins)
         and "pins_observed" in json.loads(
             Path(rec_path).read_text(encoding="utf-8"))),
        ("[R10-1/2/3] carrier CONTENT authentication (re-review round-10): "
         "REAL-mode ingest REFUSES (g) a correctly-shaped ALL-ZERO "
         "mode=real table set (full-coverage non-degeneracy per (c,l) "
         "cell: all-zero/near-constant/min-variance-floor bodies "
         "rejected), (h) a RELABELED mock construction whose artifact-"
         "derived provenance shas equal the repo mock-stack digests (a "
         "real report can never be satisfied by a mock toolchain), (i) a "
         "real report WITHOUT the 96-entry checkpoint_content_sha256 "
         "witness; the same fixture with non-degenerate bodies + witness "
         "PASSES (positive control above)",
         prov_c7 and prov_c8 and prov_c9 and prov_pos_ok),
        ("[R10-4] campaign resume AUTHENTICATION: rows.jsonl resume state "
         "content-hashed (%s) + bound to the run's pinned inputs; probes: "
         "tampered row REFUSED, rows-without-auth REFUSED, foreign-"
         "binding (different engine) REFUSED, INJECTED trailing row "
         "DROPPED never resumed; the genuine authenticated state resumes "
         "%d/%d units cleanly (the live campaign above ALSO resumed "
         "through the auth path after the forced interruption)"
         % (ROWS_AUTH_DOMAIN, len(ra_pos_done), expected_units),
         ra_closed),
        ("[R3-SEAM] OFFICIAL round-trip (sandboxed real path): kot-log/1 "
         "driver record -> log-append (chain, schema) -> verdict-gen "
         "(D10-paired rows+sidecar pins verified, %d rows) -> pinned "
         "analysis -> verdict %r (PASS fired, audit pending)"
         % (paired[0]["rows"]["rows"] if paired else -1,
            verdict_good.get("verdict")), seam_pass),
        ("[R3-SEAM] TAMPERED fixture through the same official path "
         "(guard.n_items=0, sha re-pinned attacker-consistent, every "
         "hash check green) -> verdict %r" % (verdict_bad.get("verdict"),),
         seam_tamper),
        ("[REV-C F5] ONE bound projection model: shared-block sha "
         "verified in BOTH copies (%s...); /2 artifact + model_bundle "
         "consumed; heterogeneous per-item T proven (%d distinct T over "
         "%d sidecar items); kappa PREFILL-WEIGHTED over the realized "
         "pilot pass rows (%d rows / %d items, weights %d..%d — grid "
         "passes weight the 48-item subset); TAMPERED sidecar bytes "
         "REFUSED; SELF-CONSISTENT-but-unlicensed bundle REFUSED "
         "(artifact-recorded sha wins); sidecar item universe == this "
         "campaign's eval items (verify_corpus)"
         % (ADD7_SRC_SHA256[:12], len(set(t_vals)), len(t_vals),
            kw.get("n_pass_rows", -1), kw.get("distinct_items", -1),
            kw.get("weight_min", -1), kw.get("weight_max", -1)),
         shared_ok and het_ok and kw_ok and tamper_closed
         and bundle_closed),
        ("[REV-C R6-BOUNDARY] degradation ladder exercised AT the "
         "reserve-inclusive boundary (planted kappa %.4f): the full "
         "arm-set BREACHES, REPLACE-defer + d3-defer CLEARS — the SSR6 "
         "order recovers a GREEN through the SAME add7_cap_breach "
         "predicate phase_pilot uses" % kap_b, boundary_ok),
        ("[REV-D 2] STRICT corpus bijection (count-preserving): a "
         "DUPLICATE sidecar key with a conflicting T REFUSED even when "
         "re-pinned attacker-consistent through the whole bundle (the "
         "old set-equality check passed it); a DUPLICATE eval item id "
         "REFUSED before the set comparison",
         dup_closed and evdup_closed),
        ("[REV-D 1d] realized-hours accounting: cost.prior_instance_"
         "hours REQUIRED (missing key fail-closed at Ledger init) and "
         "THREADED into the SAME add7_hours_basis/add7_cap_breach the "
         "pilot->main gate uses — 380 prior h alone flip the 900 h "
         "reserve-inclusive cap (%.1f h breaches, %.1f h clears); "
         "addendum-7 records prior_instance_hours=%s; SIDECAR surface "
         "unchanged (frozen-analysis identity instance_hours == "
         "construction + run re-validated by THIS mock's analysis pass)"
         % (bh_ph, bh_0, a7_art.get("prior_instance_hours")),
         nh_closed and ph_flip
         and a7_art.get("prior_instance_hours") == 0.0),
        ("[REV-E 3] cost-key FINITENESS: a hand-edited NaN in "
         "cost.prior_instance_hours (bare-NaN JSON parses [MEASURED]) "
         "REFUSED at Ledger init — nan > 900 is False at every cap, a "
         "NaN basis was a fail-open GO (the PIN_GB defect class, "
         "round-4 verdict 4)", nan_closed),
        ("governance: engine referred to only as 'colibri'; $0; no "
         "instance, no model download, no git, no registry write "
         "(official-seam runs are SANDBOXED repo copies — no real "
         "results-log/f1k.jsonl line exists)", True),
    ]
    for msg, okc in checks:
        print("  [%s] %s" % ("PASS" if okc else "FAIL", msg))
    print("  [FIX-n] anchor line map: %s" % json.dumps(refs))
    if verdict_bits:
        print("  analysis verdict surface (MOCK planted-lift shape, "
              "NOT evidence): %s" % json.dumps(verdict_bits, sort_keys=True))
    if not ok:
        print("  analysis stderr: %s" % proc.stderr.strip()[:800])
        fail("ERR_F1K_MOCK", "pinned analysis rejected the mock output")
    if not all(c for _, c in checks):
        fail("ERR_F1K_MOCK", "a mock self-check failed")
    print("MOCK VALIDATION PASS (wiring only; no feasibility conclusion).")
    return 0


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", help="run config JSON (coordinator-supplied)")
    ap.add_argument("--phase", choices=["pilot", "guard", "test"],
                    help="which frozen-protocol phase to run")
    ap.add_argument("--outdir", help="output/checkpoint directory")
    ap.add_argument("--mock", action="store_true",
                    help="run the ENTIRE wiring against the stub engine "
                         "($0 end-to-end validation)")
    args = ap.parse_args()
    if args.mock:
        return mock_main(args)
    if not args.config or not args.phase or not args.outdir:
        ap.error("--config, --phase and --outdir are required "
                 "(or use --mock)")
    cfg = load_config(args.config)
    verify_corpus_pins(cfg, mock=False)     # input seams, fail closed
    # [R9-PROV] carrier-construction provenance gate (re-review item 8):
    # mode=real + D/layers/seed/bindings verified BEFORE any carrier is
    # ingested; provenance shas artifact-derived; disclosure written to
    # the outdir, witness pins carried on the run record.
    carrier_prov, carrier_pins = verify_carrier_construction(cfg,
                                                             mock=False)
    write_json(Path(args.outdir) / "carrier-provenance.json", carrier_prov)
    ev = load_eval_manifest(cfg["eval_manifest"])
    verify_id_lists(cfg, ev)
    ledger = Ledger(args.outdir, cfg)       # [FIX-7] resume-safe
    if args.phase == "pilot":
        phase_pilot(cfg, ev, args.outdir, ledger)
        return 0
    frozen = load_frozen_lg(cfg, args.outdir)
    dose = validate_dose(cfg["carriers"])
    if args.phase == "guard":
        rg = read_replace_decision(args.outdir)
        phase_guard(cfg, ev, args.outdir, frozen,
                    rg["decision"] == "RUN", ledger)
        return 0
    # test phase: (5)/(7)/(6) commits + pilot gates + guard must all hold
    # BEFORE any test prefill [FIX-6] [DES §R-REV4.2/ASM-2123]
    d3_deferred, replace_run, replace_gate = \
        enforce_pretest_commits(cfg, args.outdir)
    grep = Path(args.outdir) / "guard" / "guard-report.json"
    if not grep.exists():
        fail("ERR_F1K_ORDER", "run --phase guard before --phase test "
             "(the byte-identity guard is a run-voiding instrument check, "
             "§2.5)")
    guard_report = json.loads(grep.read_text(encoding="utf-8"))
    # [R3-ATTEST] strict `is True`: a persisted report tampered to the
    # STRING "false" previously passed this truthy read
    if guard_report.get("byte_identical") is not True:
        fail("ERR_F1K_GUARD", "guard report byte_identical is %r, not the "
             "strict boolean true — run VOID (HOLD round-3 item 4)"
             % (guard_report.get("byte_identical"),))
    if replace_run and \
            "REPLACE/pass0" not in (guard_report.get("passes_compared")
                                    or []):
        fail("ERR_F1K_GUARD", "REPLACE is scheduled but the guard did not "
             "cover it — re-run --phase guard (§2.5 applies to every "
             "spliced arm)")
    passes = main_arm_passes(d3_deferred, replace_run)
    rows_path, _ = phase_test(cfg, ev, args.outdir, frozen, passes, ledger)
    sidecar_path = build_sidecar(cfg, args.outdir, guard_report, dose,
                                 ledger, d3_deferred, replace_gate,
                                 replace_run)
    rec_path = emit_run_record(args.outdir, rows_path, sidecar_path,
                               pins_observed=carrier_pins)  # [R9-PROV]
    print("test campaign complete: rows=%s sidecar=%s run-record=%s\n"
          "NEXT (coordinator): verdict-gen pipes the run record to the "
          "PINNED analysis/f1k.py on stdin; this driver never grades."
          % (rows_path, sidecar_path, rec_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
