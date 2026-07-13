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
          n_NI <= 1440; a stubbed REPLACE engine (byte-identical to b0) is
          DETECTED and fails closed; the decision drives EXECUTION (guard
          + test schedule the REPLACE pass; sidecar replace.ran is real).
  [FIX-4] The affordability d3-text deferral (§R6 step 3) is honored in
          EXECUTION: addendum-7 records d3_text_deferred and the test
          schedule derives from it — never projection-only.
  [FIX-5] Expert pinning ENFORCED + RECORDED: engine env must carry PIN=1
          and PIN_GB>0 (glm52-f1k-cost-reduction.md lever 2); realized
          pinning semantics enter the resume-safe ledger and the sidecar.
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
          n = 1440 EXACTLY (never min(1440, ceil(n_req))); the power block
          is fully validated (rho_u == 0.10, N_sim == 10000, mu* == 4.09,
          seed, MC pass threshold + coherence); the cost/elapsed ledger is
          RESUME-SAFE (cost-ledger.json accumulates across invocations and
          phases, includes pilot + construction, survives interruption).

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
  [COST]  docs/next/design/glm52-f1k-cost-reduction.md  ($149 ceiling,
          spot i4i.2xlarge + expert-pinning + R=3; ASM-2205)
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
N_TEST = 1440
#   [REG design.n_planned.n_test_items / n_max: F1-K runs AT the cap
#    (§R-REV3.1 item 4); ANA N_REGISTERED — any other n is REJECTED]
DEV_N = 96
#   [REG design.n_planned.dev_split_items; DES §R3.2 dev split expanded to 96]
GUARD_N = 60
#   [REG design.n_planned.off_concept_guard_items; DES §2.5 off-concept guard]
POWER_GATE_MIN_C = 65
POWER_GATE_MIN_M = 8
#   [REG design.n_planned.power_gate: >= 65 clusters EACH with >= 8 test
#    items (each-cluster reading, ASM-2271); ANA POWER_GATE_MIN_C/M]
USD_CAP = 149.0
#   [REG budget.usd_cap; COST validated reduced ceiling, ASM-2205]
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
DELTA_R_RUN_MAX = 0.038
#   [DES §R-REV4.3 / ASM-2124: REPLACE runs only if dev delta_R <= ~0.038,
#    i.e. n_NI <= n_max = 1440 at rho_U = 0.10 — the n_NI rule is primary]
MU_STAR_POINTS = 4.09
MC_N_SIM = 10000
MC_PASS_MIN = 0.80
MC_SEED = PERM_SEED
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

ANALYSIS_SCRIPT = ROOT / "analysis" / "f1k.py"     # [REG pins.analysis_script]
REGISTRY_RECORD = ROOT / "registry" / "experiments" / "f1k.json"
CORPUS_NAMES = ("f1k-eval-v1", "f1k-carriers-v1", "f1k-trigger-map-v1")
#   [REG pins.corpus_hashes — all three currently PINNED-AT-INPUTS: a
#    SEPARATE build; this driver verifies, never creates]

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
             "n_NI = delta_R*DEFF/SE_NI^2 <= 1440, §R-REV4.3/ASM-2124) "
             "computed at pilot addendum (6) — remove the key")
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
    return cfg


def validate_pinning(cfg):
    """[FIX-5] ENFORCE + RECORD expert pinning [COST lever 2 / ASM-2205:
    'expert-pinning + warm page-cache, priced conservatively at 1.20x';
    bringup.sh step 6: configured via the engine's PIN= / PIN_GB env].
    Optional pass-through is not enough: an unpinned run silently voids the
    $149 ceiling arithmetic. Realized values are recorded in the ledger and
    sidecar so the metered speedup resolves ASM-2205."""
    env = (cfg.get("engine") or {}).get("env") or {}
    pin = env.get("PIN")
    pin_gb = env.get("PIN_GB")
    if str(pin) != "1":
        fail("ERR_F1K_PINNING",
             "engine.env.PIN must be \"1\" (expert pinning ENFORCED — the "
             "$149 ceiling prices the 1.20x pinning lever; COST item 2 / "
             "ASM-2205; got %r)" % (pin,))
    try:
        gb = float(pin_gb)
    except (TypeError, ValueError):
        gb = -1.0
    if gb <= 0:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN_GB must be a positive GB budget (got %r) — "
             "realized pinning semantics are a recorded cost-model input "
             "[COST item 2]" % (pin_gb,))
    return {"PIN": "1", "PIN_GB": gb,
            "semantics": "PIN=1 pins the hot expert working set resident; "
                         "PIN_GB = pinned budget in GB. The 1.20x-"
                         "pessimistic throughput lever of the $149 ceiling "
                         "[glm52-f1k-cost-reduction.md item 2 / ASM-2205]; "
                         "realized speedup resolves ASM-2205 from the "
                         "metered ledger."}


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
    jp = mc.get("joint_power")
    if not isinstance(jp, (int, float)) or isinstance(jp, bool):
        fail("ERR_F1K_POWER", "mc_exact_power.joint_power must be numeric "
             "(got %r)" % (jp,))
    if not isinstance(mc.get("pass"), bool):
        fail("ERR_F1K_POWER", "mc_exact_power.pass must be a bool")
    if mc["pass"] != (jp >= MC_PASS_MIN):
        fail("ERR_F1K_POWER",
             "mc_exact_power incoherent: pass=%r with joint_power=%s vs "
             "the frozen >= %s threshold [DES §R-REV5]"
             % (mc["pass"], jp, MC_PASS_MIN))
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
        else:
            if got != pinned:
                fail("ERR_F1K_CORPUS",
                     "%s kot-corpus-hash %s != frozen record pin %s"
                     % (name, got, pinned))
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
    """[REG design.n_planned.power_gate / ASM-2271]: >= 65 clusters EACH with
    >= 8 test items, n == 1440. A shortfall is a PRE-RUN RETURN to the
    maintainer, never a run."""
    sizes = {}
    for it in test_items:
        sizes[it["cluster"]] = sizes.get(it["cluster"], 0) + 1
    c_ok = sum(1 for v in sizes.values() if v >= POWER_GATE_MIN_M)
    ok = (c_ok >= POWER_GATE_MIN_C and len(test_items) == N_TEST)
    return {"n_items": len(test_items), "n_clusters": len(sizes),
            "clusters_with_m_ge_8": c_ok,
            "gate": "C>=%d each with m>=%d and n==%d (ASM-2271)"
                    % (POWER_GATE_MIN_C, POWER_GATE_MIN_M, N_TEST),
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
        if not meta.get("layerwise_norm_matched"):
            fail("ERR_F1K_DOSE", "seed %d: layerwise_norm_matched not "
                 "attested by the B0 addendum (§R2 rescale to ||v^K_{c,l}||)"
                 % s)
    return {"r_seeds": list(DRNG_SEEDS),
            "derangement_no_fixed_point": True,
            "norm_matched_within_tol": True}


# ---------------------------------------------------------------------------
# Resume-safe cost/elapsed ledger
# ---------------------------------------------------------------------------
class Ledger:
    """[FIX-7] RESUME-SAFE cost/elapsed ledger [COST; REG budget_note: the
    ceiling resolves from the METERED spend recorded in the run's cost
    ledger]. Accumulates per-phase seconds + prefills in
    <outdir>/cost-ledger.json (atomic replace), so timing survives spot
    interruption and spans pilot + guard + test; construction hours and
    prior metered spend are REQUIRED config inputs, never silent zeros."""

    COST_KEYS = ("spot_rate_usd_per_hour", "usd_spent_prior",
                 "construction_instance_hours")

    def __init__(self, outdir, cfg):
        cost = cfg.get("cost") or {}
        for k in self.COST_KEYS:
            if k not in cost:
                fail("ERR_F1K_COST",
                     "config.cost.%s is REQUIRED (no silent zero prior "
                     "spend / construction time — review §9; REG "
                     "budget_note meters the ledger)" % k)
        base = {k: float(cost[k]) for k in self.COST_KEYS}
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
            self.d["expert_pinning"] = base["expert_pinning"]
        else:
            self.d = base
            self._write()

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


def run_scoring_pass(cfg, items, arm, pass_no, seed, env, out_rows_path,
                     done_keys, ledger=None, mock_gold_dir=None,
                     phase="test", interrupt_state=None, store_raw=False):
    """Score `items` under one (arm, pass): ONE engine process, ONE prefill
    per item [DES §R1.1], streaming per-item checkpoint appends (a spot
    interruption resumes at item granularity [COST lever 1]).
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
    errf = open(stderr_path, "a", encoding="utf-8")
    # [FIX-1] per-item label-logit + frozen-tie log (design DV: "tie-break
    # lowest label index, ties logged" [REG dependent_vars item_correct]).
    llog = open(workdir / ("label-logits.%s.jsonl" % phase), "a",
                encoding="utf-8")
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE,
                            stderr=errf, text=True)
    n = 0
    first_seen = False
    banners_here = 0
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
                rf.write(json.dumps(row, sort_keys=True) + "\n")
                rf.flush()
                os.fsync(rf.fileno())
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
    return bool(json.loads(p.read_text(encoding="utf-8"))
                .get("d3_text_deferred"))


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
    for arm, pass_no, seed in passes:
        env = arm_env(cfg, arm, seed, str(gdir), frozen, cache_off=True)
        raw_path = gdir / ("raw.%s.pass%d.jsonl" % (arm, pass_no))
        done, _ = read_ckpt(raw_path)      # resume-safe per pass
        run_scoring_pass(
            cfg, ev["guard"], arm, pass_no, seed, env, raw_path, done,
            ledger=ledger, mock_gold_dir=mock_gold_dir, phase="guard",
            store_raw=True)
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
    done, _ = read_ckpt(rows_path)
    n_new = 0
    expected = N_TEST * len(passes)
    for arm, pass_no, seed in passes:
        env = arm_env(cfg, arm, seed, str(tdir), frozen)
        n, _ = run_scoring_pass(cfg, ev["test"], arm, pass_no, seed, env,
                                rows_path, done, ledger=ledger,
                                mock_gold_dir=mock_gold_dir, phase="test",
                                interrupt_state=interrupt_state)
        n_new += n
        print("test: arm=%s pass=%d scored %d new (total done %d/%d)"
              % (arm, pass_no, n, len(done), expected))
    if len(done) != expected:
        fail("ERR_F1K_TEST", "campaign incomplete or off-schedule: %d/%d "
             "units for the committed pass list %s"
             % (len(done), expected, [(a, p) for a, p, _ in passes]))
    return rows_path, n_new


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
        if not man.get(k):
            fail("ERR_F1K_FREEZE",
                 "freeze.manifest_flags.%s is not TRUE — no test spend "
                 "until (A),(B0),(5),(7),(6) are ALL coordinator-committed "
                 "(§R-REV4.2/ASM-2123)" % k)
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
        if not (gates.get(gname) or {}).get("pass"):
            fail("ERR_F1K_FREEZE",
                 "pilot gate %r did not PASS (%s) — no test spend "
                 "(§R-REV4.2 pre-test gates)" % (gname, gates.get(gname)))
    add7 = arts["addendum-7-affordability.json"]
    if not add7.get("affordable"):
        fail("ERR_F1K_AFFORD", "addendum (7) projection not affordable — "
             "no test spend (§R6)")
    d3_deferred = bool(add7.get("d3_text_deferred"))
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
    side = {
        "manifest": {k: bool(man[k]) for k in need},
        "guard": {"n_items": guard_report["n_items"],
                  "byte_identical": bool(guard_report["byte_identical"])},
        "template": {"labels_single_token": bool(
                         tpl["labels_single_token"]),
                     "header_cue_labels_trigger_free": bool(
                         tpl["header_cue_labels_trigger_free"])},
        "dose": dose,
        "inference": {"method": inf["method"],
                      "dev_sign_symmetry_pass":
                          bool(inf["dev_sign_symmetry_pass"])},
        "replace": {"ran": bool(replace_run),                 # [FIX-3]
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
            "expert_pinning": ledger.d["expert_pinning"],     # [FIX-5]
            "resume_safe_ledger": str(ledger.path),
            "d3_text_deferred": bool(d3_deferred)},           # [FIX-4]
        "b0_ceiling_threshold": CEILING_B0,   # echo of the pinned constant
    }
    spath = Path(outdir) / "test" / "sidecar.json"
    write_json(spath, side)
    return spath


def emit_run_record(outdir, rows_path, sidecar_path):
    """The verdict-gen stdin record [ANA 'INPUT CONTRACT']: event=run,
    phase=final, exit=ok, artifacts pinned by path+sha256."""
    rec = {"event": "run", "phase": "final", "exit": "ok",
           "experiment": "f1k",
           "artifacts": {
               "rows_path": str(Path(rows_path).resolve()),
               "rows_sha256": sha256_file(rows_path),
               "sidecar_path": str(Path(sidecar_path).resolve()),
               "sidecar_sha256": sha256_file(sidecar_path)}}
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
    sem_ok = bool(sem.get("performed")) and bool(sem.get("evidence_path")) \
        and Path(str(sem.get("evidence_path"))).exists()
    panel_facts = validate_panel(cfg)       # [FIX-6]
    panel = pil["panel"]
    members = panel["members"]
    families = panel["families"]
    subset = pilot_dev_subset(cfg, ev["dev"])

    # ---- 1. score the grid over the UNLABELED panel (48-item subset) ------
    rows_path = pdir / "pilot-rows.jsonl"
    done, _ = read_ckpt(rows_path)
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
                             mock_gold_dir=mock_gold_dir, phase="pilot")
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
    replace_supported = bool((cfg.get("replace") or {})
                             .get("engine_supported"))
    env = arm_env(cfg, "b0", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:b0", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot", store_raw=True)
    env = arm_env(cfg, "K", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:K", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot", store_raw=True)
    env = arm_env(cfg, "d0", None, str(pdir), frozen)
    run_scoring_pass(cfg, dev96, "dev96:d0", 0, None, env, rows_path, done,
                     ledger=ledger, mock_gold_dir=mock_gold_dir,
                     phase="pilot")
    if replace_supported:
        # [FIX-3]/[FIX-6] measure REPLACE-vs-ADD dev discordance
        env = arm_env(cfg, ARM_REPLACE, None, str(pdir), frozen)
        run_scoring_pass(cfg, dev96, "dev96:REPLACE", 0, None, env,
                         rows_path, done, ledger=ledger,
                         mock_gold_dir=mock_gold_dir, phase="pilot",
                         store_raw=True)
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
    # [FIX-7] n = 1440 EXACTLY [REG design.n_planned.n_test_items: F1-K
    # runs AT the cap (§R-REV3.1 item 4); ANA N_REGISTERED rejects any
    # other realized n]. Never min(1440, ceil(n_required)): the frozen n is
    # the cap itself; n_required is recorded, and a measured n_required
    # below the cap is DISCLOSED as an anomaly against §R-REV3.1 item 4
    # (running at the cap only adds power — n is never reduced).
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
                  "[§R-REV4.3/ASM-2124: RUN only if n_NI <= 1440, i.e. "
                  "delta_R <= ~%.3f at rho_U=%.2f]"
                  % (delta_r, n_ni, "<=" if decision == "RUN" else ">",
                     N_TEST, DELTA_R_RUN_MAX, RHO_U))
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
    pilot_s = ledger.phase_seconds("pilot")
    pilot_pf = ledger.phase_prefills("pilot")
    s_per_prefill = pilot_s / max(pilot_pf, 1)
    rate = ledger.d["spot_rate_usd_per_hour"]
    prior = ledger.d["usd_spent_prior"]
    steps_taken = [DEGRADATION_ORDER[0]]
    d3_deferred = False
    replace_candidate = (decision == "RUN")

    def projection(d3_def, rep):
        n_main = N_TEST * len(main_arm_passes(d3_def, rep))
        n_guard = GUARD_N * len(main_arm_passes(True, rep))
        return prior + pilot_s / 3600.0 * rate \
            + (n_main + n_guard) * s_per_prefill / 3600.0 * rate

    proj = projection(d3_deferred, replace_candidate)
    if proj > USD_CAP and replace_candidate:
        # §R6 step 2: defer REPLACE (overrides an NI-gate RUN — recorded)
        steps_taken.append(DEGRADATION_ORDER[1])
        replace_candidate = False
        decision = "DEFER"
        replace_gate["decision"] = "DEFER"
        replace_gate["reason"] += (" | OVERRIDDEN to DEFER by the §R6 "
                                   "step-2 affordability degradation")
        proj = projection(d3_deferred, replace_candidate)
    elif not replace_candidate:
        steps_taken.append(DEGRADATION_ORDER[1] +
                           " [already deferred by the NI gate]")
    if proj > USD_CAP:
        # [FIX-4] step 3: defer d3-text — recorded AND honored in execution
        steps_taken.append(DEGRADATION_ORDER[2])
        d3_deferred = True
        proj = projection(d3_deferred, replace_candidate)
    affordable = proj <= USD_CAP
    add7 = {
        "addendum": "(7) bring-up s/prefill + affordability/semantic "
                    "PRE-test gate [§R-REV4.2 step 5]",
        "measured_s_per_prefill": round(s_per_prefill, 6),
        "pilot_prefills": pilot_pf,
        "pilot_wall_hours": round(pilot_s / 3600.0, 6),
        "spot_rate_usd_per_hour": rate,
        "usd_spent_prior": prior,
        "construction_instance_hours":
            ledger.d["construction_instance_hours"],
        "expert_pinning": ledger.d["expert_pinning"],         # [FIX-5]
        "projected_total_usd": round(proj, 2),
        "usd_cap": USD_CAP,
        "degradation_order": list(DEGRADATION_ORDER),
        "degradation_steps_applied": steps_taken,
        "d3_text_deferred": d3_deferred,                      # [FIX-4]
        "replace_pass_in_projection": replace_candidate,
        "semantics_reverification": {
            "performed": bool(sem.get("performed")),
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
             "bring-up projection $%.2f exceeds the $%.0f ceiling after the "
             "full degradation order — STOP and return to the maintainer "
             "[§R6/§R-REV4.2]" % (proj, USD_CAP))
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
    driver never fabricates them for a real run). Geometry: 72 clusters x
    20 = 1440 test items (satisfies n==1440 and the C>=65/m>=8 gate),
    96 dev, 60 guard. Corpus dirs mirror data/<corpus>/ so the
    kot-corpus-hash/1 verification path is exercised end-to-end."""
    fx = Path(outdir) / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    eval_dir = fx / "data" / "f1k-eval-v1"
    cdir = fx / "data" / "f1k-carriers-v1"
    tdir = fx / "data" / "f1k-trigger-map-v1"
    for d in (eval_dir, cdir, tdir):
        d.mkdir(parents=True, exist_ok=True)
    C, M = 72, 20
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
            for j in range(M):
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

    cfg = {
        "engine": {
            "argv": [sys.executable, str(HERE / "mock_colibri.py")],
            "env": {"MOCK_SALT": "f1k-mock-v1",
                    # [FIX-5] pinning ENFORCED even in the mock so the same
                    # validation path runs (values are mock placeholders)
                    "PIN": "1", "PIN_GB": "96"},
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
                  "mc_exact_power": {"mu_star": 4.09, "n_sim": 10000,
                                     "joint_power": 0.81,
                                     "seed": PERM_SEED, "pass": True}},
        "cost": {"spot_rate_usd_per_hour": SPOT_RATE_DEFAULT,
                 "usd_spent_prior": 0.0,
                 "construction_instance_hours": 0.0},
    }
    cfg_path = fx / "mock-config.json"
    write_json(cfg_path, cfg)
    return cfg_path


def run_analysis(run_record_path):
    """Pipe the run record to the PINNED analysis/f1k.py on stdin (the
    verdict-gen contract [ANA 'INPUT CONTRACT'])."""
    if not ANALYSIS_SCRIPT.exists():
        fail("ERR_F1K_ANALYSIS", "pinned analysis missing: %s"
             % ANALYSIS_SCRIPT)
    rec = Path(run_record_path).read_text(encoding="utf-8")
    proc = subprocess.run([sys.executable, str(ANALYSIS_SCRIPT)],
                          input=rec, capture_output=True, text=True)
    return proc


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
    for sub in ("pilot", "guard", "test", "fixtures", "mock-gold"):
        shutil.rmtree(str(outdir / sub), ignore_errors=True)
    try:
        (outdir / "cost-ledger.json").unlink()
    except OSError:
        pass
    outdir.mkdir(parents=True, exist_ok=True)
    print("== F1-K MOCK end-to-end validation ($0; stub engine; NOT a "
          "feasibility result) ==")
    cfg_path = gen_mock_fixtures(outdir)
    cfg = load_config(cfg_path)
    corpus_pins = verify_corpus_pins(cfg, mock=True)
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
    rec_path = emit_run_record(outdir, rows_path, sidecar_path)
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
    refs = fix_line_refs()

    def ref(n):
        return "f1k_driver.py:%s" % ",".join(map(str, refs.get(str(n), [])))

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
        ("[5] expert pinning ENFORCED + RECORDED: PIN=1 PIN_GB=%s in "
         "ledger + sidecar cost.expert_pinning [%s]"
         % (led["expert_pinning"]["PIN_GB"], ref(5)),
         led.get("expert_pinning", {}).get("PIN") == "1"),
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
        ("[7] frozen constants: z0.80=%s EXACT; n_run=%s EXACT (=1440); "
         "power block validated (rho_u/N_sim/mu*/seed/threshold); ledger "
         "resume-safe with pilot+construction (%s) [%s]"
         % (Z80, add6["n_run"], sorted(led["phase_seconds"]), ref(7)),
         Z80 == 0.842 and add6["n_run"] == N_TEST
         and "pilot" in led["phase_seconds"]
         and "construction_instance_hours" in led),
        ("input seams: kot-corpus-hash/1 verified for %s (registry "
         "placeholders honored: mock-only); id-list hashes verified; "
         "eval/carrier paths contained; NO fabricated real corpora "
         "(fixtures labeled MOCK)" % ", ".join(sorted(corpus_pins)),
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
         bool(guard_report["byte_identical"])),
        ("dose-exactness pre-validated (seeds %s, fixed-point-free, "
         "norm-matched)" % (list(DRNG_SEEDS),), True),
        ("governance: engine referred to only as 'colibri'; $0; no "
         "instance, no model download, no git, no registry write", True),
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
    if not guard_report.get("byte_identical"):
        fail("ERR_F1K_GUARD", "guard report shows a byte-identity mismatch "
             "— run VOID")
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
    rec_path = emit_run_record(args.outdir, rows_path, sidecar_path)
    print("test campaign complete: rows=%s sidecar=%s run-record=%s\n"
          "NEXT (coordinator): verdict-gen pipes the run record to the "
          "PINNED analysis/f1k.py on stdin; this driver never grades."
          % (rows_path, sidecar_path, rec_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
