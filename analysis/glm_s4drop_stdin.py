#!/usr/bin/env python3
"""glm_s4drop_stdin.py — pinned analysis for glm-s4drop-0 (GLM-5.2 Stage-4
expert-drop efficiency: COMPOSITE causal+atlas mask vs matched-removed-I/O
frequency-blind mask).

Invocation (verdict-gen step 5): kot-s4row/3 rows as JSONL on STDIN, NO argv;
emits ONE JSON object {"gates": {...}, "analysis": {...}} on stdout. All
derived statistics live here and nowhere else (G-4). `--selftest` runs the
green mock (synthetic fixtures for every decision branch + fail-closed
rejections + adversarial-replay gates + byte-determinism); touches no real
data.

ESTIMAND (cross-model review 2026-07-16, finding A; option (b) adopted,
ASM-2397): the primary contrast compares the Stage-4 COMPOSITE mask s4-semd
(22 causally-validated cells + the UNVALIDATED atlas rare/unseen cost-weighted
extension) against the deployable concept-free ascending-frequency blind mask
s4-bldf-d at matched removed I/O. It does NOT isolate causal evidence per se
(the composite consumes ~2 orders of magnitude more routing evidence than the
blind arm's 3,072-token telemetry); every licensed sentence names the
composite, never "causal evidence beats frequency". Option (a) — restricting
to the 22 causal cells — was REJECTED as physically undoseable: those cells
carry ~0.1% of decode miss-I/O (full-scale mock estimate, STIPULATED), so an
(a)-design fires kill trigger 2 by construction, a verdict fixed in advance.

Row schema kot-s4row/3 (produced by the runner; carried as a D10 role:"rows"
artifact on the chained log; v2->v3 = re-review round-3 items 2/3: replay rows
gain a MANDATORY per-prompt trajectory digest, item rows gain a MANDATORY
validated n_target_toks, meta gains replay_reference.digests):
  {"kind":"meta", "phase":"construction"|"final", ...}   exactly one;
      runner-verified gate booleans, telemetry summary, masks audit (from
      masks_manifest.json), LIVE cost ledger (realized_usd + REGISTERED
      phase-boundary checkpoints), seeds, pins (sha256s of every consumed
      input), degradation-ladder disclosure (dropped_arms), and — final phase
      — replay_reference.digests: {prompt_id -> sha256 over the exact forced
      token-id sequence of the pinned s4-b0 reference trajectory} (ASM-2401).
  {"kind":"item","arm":A,"item_id":I,"family":F,"nll_per_tok":x,
   "n_target_toks":n}
      one per (quality arm x suite item); family must equal the PINNED
      id->family mapping below (review finding B3); n_target_toks is REQUIRED
      and validated (positive int) at ingestion (re-review item 3, ASM-2402).
  {"kind":"decode","arm":A,"prompt_id":P,"pass_idx":1|2,"new_tokens":n,
   "wall_s":s,"miss_bytes":b,"match_tokens_vs_b0":m}
      free-running T-eval decode, TWICE per arm in seeded interleaved blocks
      (tok/s + descriptive match-rate ONLY — never the dose gate).
  {"kind":"replay","arm":A,"prompt_id":P,"forced_tokens":n,"miss_bytes":b,
   "traj_sha256":h}
      COMMON-TOKEN replay (review finding A3): every throughput arm teacher-
      forces the SAME pinned reference trajectories (s4-b0 pass-1 greedy
      continuations, sha256-pinned in meta.pins.reference_trajectories).
      traj_sha256 = sha256 over the exact forced TOKEN-ID SEQUENCE the arm
      replayed; io_match GATES on digest IDENTITY against the pinned
      reference digests (re-review item 2, ASM-2401) — equal token COUNTS
      with different sequences VOID io_match. ALL realized-dose gates run on
      replay rows.

phase="construction" (review finding B5): a meta-only stream (zero item /
decode / replay rows) taken at the pre-spend point — kill trigger 2
(construction dose < 2%) and the [2%, 8%) dose-band stop are computable from
telemetry+masks alone, BEFORE any quality item or $5 of ledger exists. A
construction stream whose projected dose is >= 8% and uncapped REFUSES to
emit a verdict (ERR_S4A_PHASE): the campaign must proceed, not grade itself.

Decision rule (review finding D1 — no spurious KILL at the SESOI): KILL
trigger 1 is now the one-sided 95% UPPER bound < SESOI (+0.05): the data
must AFFIRM the absence of any effect as large as the SESOI. A true-SESOI
effect now resolves KILL with prob ~5% (was ~36.6% under the old lb<=0
rule); lb<=0 with upper bound >= SESOI is INCONCLUSIVE (underpowered region,
reported at its resolution), never a kill.

Round-3 re-review (2026-07-16, items 2/3/5; ASM-2401/2402/2403): io_match is
mechanically common-token (trajectory digests) and recomputes projected
matching from the audit fields; liveness carries a registered MEANINGFUL
variance floor (an effectively inert primary pair is INSTRUMENT-INVALID,
never a KILL on lb~0); the [2%,8%) dose band and realized/projected dose
coherence are enforced in FINAL mode too (ERR_S4A_DOSE_BAND /
ERR_S4A_DOSE_INCOHERENT); the cost ledger must carry the REGISTERED
phase-boundary checkpoint sequence, not merely >= N monotone rows.

Fail-closed: any malformed stream exits nonzero with a named ERR_S4A_* code —
no partial output. Every constant is REGISTERED here and in the frozen record
(STIPULATED: ASM-2386/2387/2395/2396/2397/2398/2399/2400/2401/2402/2403;
ASM-2389 is formally SUPERSEDED by ASM-2399).
"""
from __future__ import annotations
import hashlib, json, math, sys

SCHEMA = "kot-s4row/3"
QUALITY_ARMS = ("s4-b0", "s4-sem16", "s4-remap16", "s4-semd", "s4-bldf-d",
                "s4-bldr-d-r1", "s4-bldr-d-r2", "s4-bldr-d-r3")
PRIMARY_ARMS = ("s4-semd", "s4-bldf-d")   # the ONLY arms the primary needs
THROUGHPUT_ARMS = ("s4-b0", "s4-sem16", "s4-semd", "s4-bldf-d")
RANDBLIND = ("s4-bldr-d-r1", "s4-bldr-d-r2", "s4-bldr-d-r3")
DROPPABLE_ARMS = frozenset(("s4-bldr-d-r2", "s4-bldr-d-r3"))  # ladder rung 3 ONLY
N_SUITE = 300
EXPECTED_IDS = frozenset("s4q-%04d" % i for i in range(N_SUITE))
MAX_INCOMPLETE = 5            # per SECONDARY arm; the primary pair allows ZERO missing
N_TEVAL = 8
EXPECTED_TEVAL_IDS = frozenset("s4d-e%02d" % i for i in range(N_TEVAL))
TEVAL_TOKEN_BUDGETS = (96, 64)  # registered budget + ladder rung 2; ONE common
                                # value across every decode/replay row
                                # (skeptic-5 R2 finding 4: rows bind to the
                                # pinned T-eval corpus, not any 8 prompt ids)
N_PASSES = 2                  # free-running T-eval decoded twice per arm
SESOI_NATS = 0.05             # smallest selective effect of interest (primary)
TOST_MARGIN = 0.05            # registered equivalence margin (90% CI inside +-margin)
NONINF_MARGIN = 0.05          # joint-16 non-inferiority margin vs s4-b0 (upper bound)
IO_MIN_FRAC = 0.02            # kill trigger 2: achievable semantic dose below this
DOSE_BAND_LO, DOSE_BAND_HI = 0.02, 0.08   # [lo, hi) at construction => pre-spend STOP
PASS_DOSE_FRAC = 0.08         # PASS requires at least this REALIZED (replay) dose
MATCH_TOL_PROJ = 0.02         # projected blind-vs-sem removed-I/O tolerance —
                              # RECOMPUTED from the audit's removed_frac +
                              # removed_bytes_per_tok fields, never trusted
                              # from the supplied match_rel_err (re-review
                              # item 2, ASM-2401)
MATCH_AUDIT_COH = 0.005       # |supplied match_rel_err - recomputed byte-basis
                              # rel err| audit self-consistency bound: a
                              # contradictory audit VOIDS io_match (ASM-2401;
                              # builder emits the byte-basis figure,
                              # build_masks.py arms_audit)
REAL_DOSE_TOL = 0.05          # realized REMOVED-dose semd-vs-bldf rel. tol. (was 0.25; review A3)
REAL_PROJ_COH_TOL = 0.15      # realized-vs-projected semd dose coherence: the
                              # replay dose may not EXCEED the projected dose
                              # by more than 3x the stipulated transfer sigma
                              # sigma_rel 0.05 (ASM-2399); breach is REFUSED
                              # fail-closed, never graded (re-review item 5,
                              # ASM-2403). Shortfall is lawful and handled by
                              # the 8% floor (tie-at-sub-floor-dose =>
                              # INCONCLUSIVE) down to the 2% band floor.
WINSOR_NATS = 2.0             # per-item delta winsorization bound (all quality contrasts)
TOKPS_MIN_GAIN = 0.03         # PASS tok/s clause: pooled gain >= this AND >0 in each pass
LIVENESS_MIN_DISTINCT = 50    # per primary arm: distinct NLL values over the 300 items
LIVENESS_MAX_ZERO_FRAC = 0.10 # fraction of EXACTLY-zero primary deltas tolerated
LIVENESS_MIN_STDEV = 1e-3     # nats/tok: registered MEANINGFUL variance floor
                              # (re-review item 3, ASM-2402) for each primary
                              # arm's NLLs and for the primary deltas — a
                              # mathematically-positive but effectively inert
                              # spread (e.g. 1e-12 jitter) is a dead
                              # instrument (INSTRUMENT-INVALID), never a KILL
                              # on lb~0; real per-item spread is ~0.1-0.3
                              # (planning sigma, ASM-2396), >= 100x this floor
BOOT_B = 10000
BOOT_SEED = 20260806
BLIND_SEEDS = {"s4-bldr-d-r1": 20260803, "s4-bldr-d-r2": 20260804,
               "s4-bldr-d-r3": 20260805}
TEL_MIN_TOKENS = 2000
COST_CAP_USD = 40.0
COST_CAP_WALL_H = 36.0
COST_FLOOR_USD = 5.0          # ledger scale floor at FULL campaign scale (final phase)
COST_FLOOR_CONSTRUCTION = 0.5 # ledger floor at the construction point (telemetry+masks)
# REGISTERED phase-boundary checkpoint sequences (re-review item 5, ASM-2403;
# supersedes the count-only >=12/>=2 rule, review D3): labels must be DISTINCT,
# drawn from the registered sequence IN REGISTERED ORDER; a quality checkpoint
# may be absent ONLY for a lawfully ladder-dropped arm ({r2, r3}). Duplicate /
# placeholder / off-registry labels VOID the ledger gate.
CKPT_SEQ_CONSTRUCTION = ("telemetry", "masks")
CKPT_SEQ_FINAL = (("telemetry", "masks", "bring-up")
                  + tuple("quality-%s" % a for a in QUALITY_ARMS)
                  + ("t-eval", "replay"))
# Pins the meta MUST carry as 64-hex digests (fail-closed at consumption;
# review finding C2). reference_trajectories is final-phase only.
PIN_KEYS_CONSTRUCTION = ("telemetry", "masks_manifest", "s4_table_patch",
                         "weights", "runner_script", "staged_bytes_manifest")
PIN_KEYS_FINAL = PIN_KEYS_CONSTRUCTION + ("reference_trajectories",)

# PINNED id->family mapping (review finding B3): the committed suite
# data/glm-s4drop-quality-suite-v1/items.json (corpus sha
# 4723f7c40d4fa377a8dbc80213476afa4cb50a986b4898340cf5b5ff81dad11e) assigns
# ids s4q-0000..0299 in 30 contiguous blocks of 10, one per template family,
# in exactly this generator order (poc/glm52-probe/stage4/gen_suite.py).
# Runner-supplied family labels are CHECKED against this mapping; a
# collapsed / relabelled family set FAILS the family gate.
PINNED_FAMILIES = (
    "add4", "mul2x2", "word_sub",                       # arithmetic
    "fn_eval", "str_len", "list_index",                 # code
    "col_sum", "col_get", "tsv_to_csv",                 # format_csv
    "json_value", "xml_value", "json_first_key",        # format_xml_json
    "zh_verbatim", "zh_to_en", "en_verbatim",           # copy_zh
    "element_symbol", "planet_fact", "organ_fact",      # science
    "simple_interest", "fx_convert", "term_recall",     # legal_fin
    "de_word", "fr_word", "es_word",                    # multiling
    "capital", "next_day", "next_month",                # general
    "idiom", "opposite", "coref",                       # prose
)
assert len(PINNED_FAMILIES) == 30 and len(set(PINNED_FAMILIES)) == 30


def pinned_family(item_id: str) -> str:
    return PINNED_FAMILIES[int(item_id.split("-")[1]) // 10]


OUTPUT_FIELDS = [
    "/gates/pins_valid", "/gates/pins_present_valid", "/gates/telemetry_valid",
    "/gates/suite_disjoint_valid", "/gates/mask_construction_valid",
    "/gates/family_valid", "/gates/quality_liveness_valid",
    "/gates/io_match_valid", "/gates/decode_config_valid",
    "/gates/inertness_valid", "/gates/completeness_valid", "/gates/seeds_valid",
    "/gates/cost_ledger_valid", "/gates/all_valid",
    "/analysis/phase", "/analysis/construction_stop",
    "/analysis/n_items", "/analysis/n_primary_complete", "/analysis/n_families",
    "/analysis/incomplete_by_arm", "/analysis/dropped_arms",
    "/analysis/secondary_n_items", "/analysis/telemetry_tier",
    "/analysis/primary_delta_nats", "/analysis/primary_delta_raw_nats",
    "/analysis/n_winsorized", "/analysis/primary_ci95",
    "/analysis/primary_lb95", "/analysis/primary_ub95",
    "/analysis/primary_joint_pass",
    "/analysis/tost90_ci", "/analysis/tost_equiv_at_margin",
    "/analysis/liveness",
    "/analysis/dose_target_frac", "/analysis/dose_achieved_frac",
    "/analysis/dose_achieved_realized",
    "/analysis/dose_capped", "/analysis/removed_io_bytes_per_tok",
    "/analysis/io_match_rel_err_projected", "/analysis/io_match_rel_err_realized",
    "/analysis/joint16_delta_nats", "/analysis/joint16_ci95",
    "/analysis/joint16_upper95", "/analysis/joint16_noninferior",
    "/analysis/randblind_delta_nats", "/analysis/randblind_ci95",
    "/analysis/randblind_n_realizations",
    "/analysis/remap16_delta_nats", "/analysis/remap16_ci95",
    "/analysis/arm_mean_nll", "/analysis/tokps", "/analysis/missbytes_per_tok",
    "/analysis/replay_missbytes_per_tok",
    "/analysis/tokps_gain_semd_vs_b0", "/analysis/tokps_gain_by_pass",
    "/analysis/decode_match_rate",
    "/analysis/mask_cell_counts",
    "/analysis/kill_fired", "/analysis/kill_reason", "/analysis/pass_gate",
    "/analysis/power_scope", "/analysis/full_verdict_power",
    "/analysis/accuracy", "/analysis/params", "/analysis/memory",
    "/analysis/inference_compute", "/analysis/training_compute",
    "/analysis/cost_ledger",
]

POWER_SCOPE = (
    "cluster resolution (ASM-2396/2399): 30 pinned template families are the "
    "independence unit; planning within-family sigma 0.30, between-family tau "
    "0.10 (both STIPULATED) => se(T) ~ 0.025; joint VALIDATE MDE_80 ~ 0.071 "
    "nats/tok. Decision boundaries under the REVISED kill rule (upper95 < "
    "SESOI; review finding D1): at true +0.10 validate ~ 0.977 / kill ~ 1e-4; "
    "at the +0.05 SESOI kill ~ 0.05 / validate ~ 0.50 / inconclusive ~ 0.45 "
    "(a true-SESOI effect can no longer be spuriously killed); at true 0 "
    "kill ~ 0.64 / validate ~ 0.02 / inconclusive ~ 0.34. A non-demonstration "
    "is scoped 'not demonstrated at this resolution', never 'no effect'; the "
    "honest power lever is more template families, not more items per family. "
    "The pre-review iid figure (MDE ~ 0.043) is RETIRED as stale."
)
FULL_VERDICT_POWER = (
    "FULL-VERDICT power (review finding D2 + skeptic-5 R2 finding 2; every "
    "non-quality clause carries a STIPULATED noise model, ASM-2399): (1) "
    "quality joint pass at true +0.10: ~0.977 (cluster se 0.025); (2) "
    "realized-dose clause (replay-based dose >= 0.08 given projected 0.098): "
    "projection->realized transfer error stipulated sigma_rel 0.05 per arm "
    "(common-token replay removes trajectory noise; residual = T-build->"
    "T-eval distribution shift) => P ~ 0.9999; (3) io_match 5%-of-dose gate: "
    "between-arm transfer errors are stipulated correlated rho 0.9 (common "
    "forced trajectory, matched rare tails) => sd(rel diff) ~ 0.022, "
    "P(io_match) ~ 0.975 - SENSITIVITY DISCLOSED: at rho 0.5 P falls to "
    "~0.68 and an io_match miss is a VOID (coordinator rerun under void "
    "budget 1), never a verdict; (4) two-pass tok/s clause at true gain "
    "+0.08: per-pass gain se stipulated 0.02 => P ~ 0.99. Design-point "
    "FULL-VERDICT validate ~ 0.94; at true tok/s gain +0.04 the tok/s "
    "clause alone falls to ~0.7 and the full verdict to ~0.66 (disclosed: "
    "the tok/s clause is the weakest link). KILL trigger 1 additionally "
    "requires realized dose >= 0.08 (skeptic-5 R2 finding 1): a quality tie "
    "observed at a sub-floor dose is INCONCLUSIVE - the lever question was "
    "not asked at lever scale."
)


def die(code: str, msg: str):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def is_hex64(x) -> bool:
    """A real digest: 64 lowercase hex chars, not a degenerate placeholder
    (all-identical characters, e.g. '0'*64) — review finding C2."""
    return (isinstance(x, str) and len(x) == 64
            and all(c in "0123456789abcdef" for c in x) and len(set(x)) > 1)


# ------------------------------------------------------------------ bootstrap
def boot_indices(seed: int, b: int, n: int):
    """SHA-256 DRBG resample indices: replicate b, draw j -> index in [0,n)."""
    for rep in range(b):
        out, ctr = [], 0
        while len(out) < n:
            d = hashlib.sha256(("glm-s4drop-0:boot:%d:%d:%d" % (seed, rep, ctr)).encode()).digest()
            for k in range(0, 32, 4):
                if len(out) >= n:
                    break
                out.append(int.from_bytes(d[k:k + 4], "big") % n)
            ctr += 1
        yield out


def wins(x: float) -> float:
    """Registered per-item delta winsorization (ASM-2396): a single broken
    1-3-token-target item cannot dominate the mean or the CI tails."""
    return max(-WINSOR_NATS, min(WINSOR_NATS, x))


def boot_ci(cluster_deltas, seed, b=BOOT_B):
    """CLUSTER percentile bootstrap of the mean (skeptic-4 finding 3): the
    suite's 10-near-clone template families are the independence unit, so
    replicates resample FAMILIES with replacement and keep all their item
    deltas. cluster_deltas: list of lists (one inner list per family, already
    winsorized). Returns the observed pooled mean and the 2.5/5/95/97.5
    percentiles of the resampled pooled-mean distribution."""
    C = len(cluster_deltas)
    flat = [x for cl in cluster_deltas for x in cl]
    means = []
    for idx in boot_indices(seed, b, C):
        s, m = 0.0, 0
        for j in idx:
            for x in cluster_deltas[j]:
                s += x
                m += 1
        means.append(s / m)
    means.sort()

    def pct(p):
        k = p * (len(means) - 1)
        lo = int(math.floor(k)); hi = int(math.ceil(k))
        return means[lo] + (means[hi] - means[lo]) * (k - lo)
    return {"mean": sum(flat) / len(flat), "p2_5": pct(0.025), "p5": pct(0.05),
            "p95": pct(0.95), "p97_5": pct(0.975)}


# ------------------------------------------------------------------ ingestion
def read_rows(stream):
    meta, items, decodes, replays = None, [], [], []
    n_lines = 0
    for line in stream:
        line = line.strip()
        if not line:
            continue
        n_lines += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            die("ERR_S4A_PARSE", "line %d unparseable: %s" % (n_lines, e))
        kind = row.get("kind")
        if kind == "meta":
            if row.get("schema") != SCHEMA:
                die("ERR_S4A_SCHEMA", "meta schema %r != %s" % (row.get("schema"), SCHEMA))
            if row.get("phase") not in ("construction", "final"):
                die("ERR_S4A_PHASE", "meta phase %r not in construction/final" % row.get("phase"))
            if meta is not None:
                die("ERR_S4A_META_DUP", "more than one meta row")
            meta = row
        elif kind == "item":
            if row.get("arm") not in QUALITY_ARMS:
                die("ERR_S4A_ARM", "unknown quality arm %r" % row.get("arm"))
            if not isinstance(row.get("item_id"), str):
                die("ERR_S4A_ITEM", "item row without string item_id")
            if row["item_id"] not in EXPECTED_IDS:
                die("ERR_S4A_ITEM_ID", "item id %r is not a pinned suite id" % row["item_id"])
            if not isinstance(row.get("family"), str) or not row["family"]:
                die("ERR_S4A_FAMILY", "item %s/%s carries no template family"
                    % (row.get("arm"), row.get("item_id")))
            if not is_num(row.get("nll_per_tok")) or row["nll_per_tok"] < 0:
                die("ERR_S4A_ITEM", "item %s/%s: nll_per_tok invalid"
                    % (row.get("arm"), row.get("item_id")))
            # re-review item 3 (ASM-2402): n_target_toks is REQUIRED and
            # type-validated on EVERY item row — a stream missing it is a
            # broken instrument, never a silent PASS.
            ntt = row.get("n_target_toks")
            if not isinstance(ntt, int) or isinstance(ntt, bool) or ntt <= 0:
                die("ERR_S4A_ITEM", "item %s/%s: n_target_toks absent/invalid "
                    "(positive int required)" % (row.get("arm"), row.get("item_id")))
            items.append(row)
        elif kind == "decode":
            if row.get("arm") not in THROUGHPUT_ARMS:
                die("ERR_S4A_ARM", "unknown throughput arm %r" % row.get("arm"))
            if row.get("pass_idx") not in (1, 2):
                die("ERR_S4A_DECODE", "decode %s/%s: pass_idx must be 1 or 2"
                    % (row.get("arm"), row.get("prompt_id")))
            for k in ("new_tokens", "wall_s", "miss_bytes", "match_tokens_vs_b0"):
                if not is_num(row.get(k)) or row[k] < 0:
                    die("ERR_S4A_DECODE", "decode %s/%s: %s invalid"
                        % (row.get("arm"), row.get("prompt_id"), k))
            decodes.append(row)
        elif kind == "replay":
            if row.get("arm") not in THROUGHPUT_ARMS:
                die("ERR_S4A_ARM", "unknown replay arm %r" % row.get("arm"))
            for k in ("forced_tokens", "miss_bytes"):
                if not is_num(row.get(k)) or row[k] < 0:
                    die("ERR_S4A_REPLAY", "replay %s/%s: %s invalid"
                        % (row.get("arm"), row.get("prompt_id"), k))
            if row["forced_tokens"] <= 0:
                die("ERR_S4A_REPLAY", "replay %s/%s: forced_tokens must be positive"
                    % (row.get("arm"), row.get("prompt_id")))
            # re-review item 2 (ASM-2401): every replay row MUST carry the
            # trajectory digest (sha256 over the exact forced token-id
            # sequence); a count-only row cannot prove common-token replay.
            if not is_hex64(row.get("traj_sha256")):
                die("ERR_S4A_REPLAY", "replay %s/%s: traj_sha256 absent/invalid "
                    "(64-hex trajectory digest required)"
                    % (row.get("arm"), row.get("prompt_id")))
            replays.append(row)
        else:
            die("ERR_S4A_KIND", "unknown row kind %r" % kind)
    if meta is None:
        die("ERR_S4A_META", "no meta row on stdin")
    if meta["phase"] == "construction":
        if items or decodes or replays:
            die("ERR_S4A_PHASE", "construction phase must carry ZERO item/decode/replay "
                "rows (got %d/%d/%d)" % (len(items), len(decodes), len(replays)))
    else:
        if not items:
            die("ERR_S4A_EMPTY", "no item rows on stdin")
    return meta, items, decodes, replays


# ---------------------------------------------------------------- gate helpers
def gate_pins_present(meta, phase):
    pins = meta.get("pins") or {}
    keys = PIN_KEYS_CONSTRUCTION if phase == "construction" else PIN_KEYS_FINAL
    return all(is_hex64(pins.get(k)) for k in keys)


def gate_cost(meta, phase, dropped=frozenset()):
    """LIVE hard-cap ledger (review finding D3): realized dollars enforced
    DURING the run via monotone per-phase checkpoints, every one <= cap;
    the final figure must equal the last checkpoint. Scale floors per the
    F1-K round-6 lesson (a $0 ledger at campaign scale is dishonest).
    Re-review item 5 (ASM-2403): the checkpoints must be the REGISTERED
    phase-boundary sequence — distinct labels, in registered order, one per
    registered boundary; a quality checkpoint may be absent ONLY for a
    lawfully ladder-dropped arm. Duplicate/placeholder checkpoint trails
    ('x' x 13) are rejected."""
    cost = meta.get("cost") or {}
    if not (is_num(cost.get("realized_usd")) and is_num(cost.get("wall_h"))):
        return False
    usd, wall = cost["realized_usd"], cost["wall_h"]
    cps = cost.get("checkpoints")
    if not isinstance(cps, list):
        return False
    labels, last = [], 0.0
    for cp in cps:
        if not (isinstance(cp, dict) and isinstance(cp.get("label"), str)
                and is_num(cp.get("usd")) and cp["usd"] >= last
                and cp["usd"] <= COST_CAP_USD):
            return False
        last = cp["usd"]
        labels.append(cp["label"])
    seq = CKPT_SEQ_CONSTRUCTION if phase == "construction" else CKPT_SEQ_FINAL
    if len(set(labels)) != len(labels):
        return False                      # duplicate checkpoints
    if labels != [l for l in seq if l in set(labels)]:
        return False                      # off-registry label or out of registered order
    missing = set(seq) - set(labels)
    if not missing <= {"quality-%s" % a for a in dropped}:
        return False                      # a registered boundary was skipped
    if abs(last - usd) > 1e-9:
        return False
    floor = COST_FLOOR_CONSTRUCTION if phase == "construction" else COST_FLOOR_USD
    return floor <= usd <= COST_CAP_USD and 0.0 < wall <= COST_CAP_WALL_H


def dose_from_masks(meta):
    masks = meta.get("masks") or {}
    arms_audit = masks.get("arms") or {}
    semd_audit = arms_audit.get("s4-semd") or {}
    dose = semd_audit.get("removed_frac")
    dose = float(dose) if is_num(dose) else 0.0
    ck = masks.get("construction_kill") or (masks.get("audit") or {}).get("construction_kill")
    capped = bool(masks.get("dose_capped")) or bool((ck or {}).get("fired"))
    target = masks.get("dose_frac_target")
    target = float(target) if is_num(target) else 0.10
    return dose, capped, target, semd_audit, arms_audit


def null_analysis(overrides):
    """Every declared /analysis field, null-shaped; construction phase fills
    only what telemetry+masks license."""
    base = {
        "phase": None, "construction_stop": None,
        "n_items": None, "n_primary_complete": None, "n_families": None,
        "incomplete_by_arm": None, "dropped_arms": None,
        "secondary_n_items": None, "telemetry_tier": None,
        "primary_delta_nats": None, "primary_delta_raw_nats": None,
        "n_winsorized": None, "primary_ci95": None,
        "primary_lb95": None, "primary_ub95": None, "primary_joint_pass": None,
        "tost90_ci": None, "tost_equiv_at_margin": None,
        "liveness": None,
        "dose_target_frac": None, "dose_achieved_frac": None,
        "dose_achieved_realized": None, "dose_capped": None,
        "removed_io_bytes_per_tok": None,
        "io_match_rel_err_projected": None, "io_match_rel_err_realized": None,
        "joint16_delta_nats": None, "joint16_ci95": None,
        "joint16_upper95": None, "joint16_noninferior": None,
        "randblind_delta_nats": None, "randblind_ci95": None,
        "randblind_n_realizations": None,
        "remap16_delta_nats": None, "remap16_ci95": None,
        "arm_mean_nll": None, "tokps": None, "missbytes_per_tok": None,
        "replay_missbytes_per_tok": None,
        "tokps_gain_semd_vs_b0": None, "tokps_gain_by_pass": None,
        "decode_match_rate": None, "mask_cell_counts": None,
        "kill_fired": False, "kill_reason": "", "pass_gate": False,
        "power_scope": POWER_SCOPE, "full_verdict_power": FULL_VERDICT_POWER,
        "accuracy": None, "params": None, "memory": None,
        "inference_compute": None, "training_compute": None,
        "cost_ledger": None,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------- construction
def compute_construction(meta):
    """Pre-spend verdict point (review finding B5): kill trigger 2 and the
    dose-band stop from telemetry+masks ALONE. Gates that need run data are
    scoped out (recorded as True with the scope disclosed in /analysis/phase);
    PASS is unreachable here by construction (primary_joint_pass is null)."""
    g_in = meta.get("gates") or {}

    def rg(name):
        v = g_in.get(name)
        return v if isinstance(v, bool) else False

    tel = meta.get("telemetry") or {}
    seeds = meta.get("seeds") or {}
    dose, capped, target, semd_audit, arms_audit = dose_from_masks(meta)

    gates = {
        "pins_valid": rg("pins_valid"),
        "pins_present_valid": gate_pins_present(meta, "construction"),
        "telemetry_valid": (tel.get("tier") in ("M", "P")
                            and is_num(tel.get("total_expert_miss_bytes_per_tok"))
                            and tel.get("total_expert_miss_bytes_per_tok", 0) > 0
                            and isinstance(tel.get("decode_tokens"), int)
                            and tel.get("decode_tokens", 0) >= TEL_MIN_TOKENS),
        "mask_construction_valid": rg("mask_construction_valid"),
        "seeds_valid": (seeds.get("bootstrap") == BOOT_SEED
                        and all((arms_audit.get(a) or {}).get("seed") == s
                                for a, s in BLIND_SEEDS.items()
                                if a in arms_audit)),
        "cost_ledger_valid": gate_cost(meta, "construction"),
        # scoped out at the pre-spend point (no run data exists yet):
        "suite_disjoint_valid": True, "family_valid": True,
        "quality_liveness_valid": True, "io_match_valid": True,
        "decode_config_valid": True, "inertness_valid": True,
        "completeness_valid": True,
    }
    gates["all_valid"] = all(gates.values())

    kill, kill_reason, stop = False, "", None
    if dose >= DOSE_BAND_HI:
        die("ERR_S4A_PHASE", "construction-phase verdict refused: projected dose %.4f "
            ">= %.2f — the campaign must PROCEED, not grade itself pre-spend"
            % (dose, DOSE_BAND_HI))
    if dose < DOSE_BAND_LO and not capped:
        # skeptic-5 R2 finding 3: the pinned builder cannot emit a sub-2%
        # dose without dose_capped; an uncapped sub-band dose is incoherent
        # input, never a silent "proceed".
        die("ERR_S4A_DOSE_INCOHERENT", "projected dose %.4f < %.2f with dose_capped "
            "false — the pinned builder cannot produce this; refusing" % (dose, DOSE_BAND_LO))
    if gates["all_valid"] and capped and dose < IO_MIN_FRAC:
        kill = True
        stop = "kill-dose"
        kill_reason = ("dose-capped at construction: achievable semantic removed-I/O "
                       "%.4f < IO_MIN_FRAC %.2f (tier %s) — no physically meaningful "
                       "drop dose exists at current causal+rare-tail coverage; "
                       "computed from telemetry+masks alone at the pre-spend point"
                       % (dose, IO_MIN_FRAC, tel.get("tier")))
    elif DOSE_BAND_LO <= dose < DOSE_BAND_HI:
        stop = "dose-band-stop"

    analysis = null_analysis({
        "phase": "construction",
        "construction_stop": stop,
        "telemetry_tier": tel.get("tier"),
        "dose_target_frac": target,
        "dose_achieved_frac": dose,
        "dose_capped": capped,
        "removed_io_bytes_per_tok": semd_audit.get("removed_bytes_per_tok"),
        "mask_cell_counts": {a: (arms_audit.get(a) or {}).get("cells")
                             for a in QUALITY_ARMS if a != "s4-b0"},
        "kill_fired": kill, "kill_reason": kill_reason,
        "pass_gate": False,
        "cost_ledger": {"realized_usd": (meta.get("cost") or {}).get("realized_usd"),
                        "wall_h": (meta.get("cost") or {}).get("wall_h"),
                        "n_checkpoints": len((meta.get("cost") or {}).get("checkpoints") or []),
                        "usd_cap": COST_CAP_USD, "wall_cap_h": COST_CAP_WALL_H},
    })
    return {"gates": gates, "analysis": analysis}


# --------------------------------------------------------------------- final
def compute_final(meta, items, decodes, replays):
    # ---------------- degradation-ladder disclosure -------------------------
    dropped = (meta.get("degradation") or {}).get("dropped_arms") or []
    dropped_ok = (isinstance(dropped, list)
                  and all(a in DROPPABLE_ARMS for a in dropped))
    dropped_set = set(dropped) if dropped_ok else set()
    expected_arms = [a for a in QUALITY_ARMS if a not in dropped_set]

    # ---------------- per-item table, families, completeness ----------------
    table = {}
    family_ok = True
    for r in items:
        key = (r["item_id"], r["arm"])
        if key in table:
            die("ERR_S4A_ITEM_DUP", "duplicate item row %s/%s" % key)
        table[key] = float(r["nll_per_tok"])
        # PINNED family check (review finding B3): runner labels must match
        # the committed suite bytes exactly.
        if r["family"] != pinned_family(r["item_id"]):
            family_ok = False
    ids = sorted({r["item_id"] for r in items})
    # PRIMARY completeness is PAIR-ONLY and ZERO-MISSING (review finding B2):
    # secondary/random-arm missingness can no longer move the primary set.
    primary_complete = [i for i in sorted(EXPECTED_IDS)
                        if all((i, a) in table for a in PRIMARY_ARMS)]
    incomplete_by_arm = {a: sum(1 for i in EXPECTED_IDS if (i, a) not in table)
                         for a in expected_arms}
    rows_for_dropped = any(r["arm"] in dropped_set for r in items)
    completeness = (dropped_ok and not rows_for_dropped
                    and len(primary_complete) == N_SUITE
                    and all(incomplete_by_arm[a] <= MAX_INCOMPLETE
                            for a in expected_arms if a not in PRIMARY_ARMS)
                    and all(incomplete_by_arm[a] == 0 for a in PRIMARY_ARMS))
    if not primary_complete:
        die("ERR_S4A_EMPTY", "no suite item carries both primary arms (%s)"
            % ", ".join(PRIMARY_ARMS))
    families = sorted({pinned_family(i) for i in primary_complete})
    fam_items = {f: [i for i in primary_complete if pinned_family(i) == f]
                 for f in families}
    family_gate = (family_ok
                   and len(families) == 30
                   and all(len(fam_items[f]) == 10 for f in families))

    # ---------------- liveness (review finding B1 + re-review item 3) -------
    # A broken/inert/rounded readout must be INSTRUMENT-INVALID, never a KILL:
    # a real tie has continuous per-item noise; all-equal or heavily-rounded
    # NLLs (or identically-zero deltas) mark a dead instrument. Re-review
    # item 3 (ASM-2402): "positive variance" is not enough — a mathematically
    # positive but effectively inert spread (1e-12 jitter) passed liveness
    # and fired KILL with T=0; the floor is now the registered MEANINGFUL
    # LIVENESS_MIN_STDEV on each primary arm AND on the primary deltas.
    liveness_diag = {}
    live_ok = True
    for a in PRIMARY_ARMS:
        vals = [table[(i, a)] for i in primary_complete if (i, a) in table]
        n_distinct = len(set(vals))
        mean_a = sum(vals) / len(vals) if vals else 0.0
        var_a = (sum((v - mean_a) ** 2 for v in vals) / len(vals)) if vals else 0.0
        liveness_diag[a] = {"n_distinct": n_distinct, "stdev": math.sqrt(var_a)}
        if n_distinct < LIVENESS_MIN_DISTINCT or var_a < LIVENESS_MIN_STDEV ** 2:
            live_ok = False
    deltas_raw = [table[(i, "s4-bldf-d")] - table[(i, "s4-semd")]
                  for i in primary_complete]
    zero_frac = (sum(1 for d in deltas_raw if d == 0.0) / len(deltas_raw))
    mean_d = sum(deltas_raw) / len(deltas_raw)
    var_d = sum((d - mean_d) ** 2 for d in deltas_raw) / len(deltas_raw)
    liveness_diag["primary_delta"] = {"zero_frac": zero_frac,
                                      "stdev": math.sqrt(var_d)}
    if var_d < LIVENESS_MIN_STDEV ** 2 or zero_frac > LIVENESS_MAX_ZERO_FRAC:
        live_ok = False

    # ---------------- runner-verified gate booleans -------------------------
    g_in = meta.get("gates") or {}

    def rg(name):
        v = g_in.get(name)
        return v if isinstance(v, bool) else False   # missing => False (fail closed)

    tel = meta.get("telemetry") or {}
    seeds = meta.get("seeds") or {}
    dose_achieved, dose_capped, dose_target, semd_audit, arms_audit = dose_from_masks(meta)

    gates = {}
    gates["pins_valid"] = rg("pins_valid")
    gates["pins_present_valid"] = gate_pins_present(meta, "final")
    gates["suite_disjoint_valid"] = rg("suite_disjoint_valid")
    gates["mask_construction_valid"] = rg("mask_construction_valid")
    gates["inertness_valid"] = rg("inertness_valid")
    gates["family_valid"] = family_gate
    gates["quality_liveness_valid"] = live_ok
    gates["telemetry_valid"] = (tel.get("tier") in ("M", "P")
                                and is_num(tel.get("total_expert_miss_bytes_per_tok"))
                                and tel.get("total_expert_miss_bytes_per_tok", 0) > 0
                                and isinstance(tel.get("decode_tokens"), int)
                                and tel.get("decode_tokens", 0) >= TEL_MIN_TOKENS)
    gates["seeds_valid"] = (seeds.get("bootstrap") == BOOT_SEED
                            and all((arms_audit.get(a) or {}).get("seed") == s
                                    for a, s in BLIND_SEEDS.items()
                                    if a not in dropped_set))
    gates["completeness_valid"] = completeness
    gates["cost_ledger_valid"] = gate_cost(meta, "final", dropped_set)

    # projected matching (re-review item 2, ASM-2401): every present blind arm
    # within MATCH_TOL_PROJ of s4-semd, RECOMPUTED from the audit's own
    # removed_frac + removed_bytes_per_tok fields — the supplied match_rel_err
    # is never trusted as the gate quantity, only checked for self-consistency
    # against the byte-basis recompute (a contradictory audit VOIDS io_match).
    semd_frac = semd_audit.get("removed_frac")
    semd_bpt = semd_audit.get("removed_bytes_per_tok")
    proj_base_ok = (is_num(semd_frac) and semd_frac > 0
                    and is_num(semd_bpt) and semd_bpt > 0)
    proj_errs = []
    proj_ok = proj_base_ok
    for a in ("s4-bldf-d",) + RANDBLIND:
        if a in dropped_set:
            continue
        aud = arms_audit.get(a) or {}
        fr, bp, sup = (aud.get("removed_frac"), aud.get("removed_bytes_per_tok"),
                       aud.get("match_rel_err"))
        if not (proj_base_ok and is_num(fr) and is_num(bp) and is_num(sup)):
            proj_errs.append(1.0)
            proj_ok = False
            continue
        rec_f = abs(fr - semd_frac) / semd_frac      # fraction-basis recompute
        rec_b = abs(bp - semd_bpt) / semd_bpt        # byte-basis recompute
        rec = max(rec_f, rec_b)
        proj_errs.append(rec)
        if rec > MATCH_TOL_PROJ or abs(sup - rec_b) > MATCH_AUDIT_COH:
            proj_ok = False

    # free-running T-eval decode: tok/s + descriptive match-rate ONLY
    def decode_tot(rows, field):
        return sum(r[field] for r in rows)
    mb, tokps, match_rate, tokps_pass = {}, {}, {}, {}
    decode_shape_ok = True
    # ONE common token budget binds every decode/replay row to the pinned
    # corpus schedule (skeptic-5 R2 finding 4): 96 registered, 64 ladder rung 2.
    budgets = ({r["new_tokens"] for r in decodes}
               | {r["forced_tokens"] for r in replays})
    if len(budgets) != 1 or not budgets.issubset(set(TEVAL_TOKEN_BUDGETS)):
        decode_shape_ok = False
    for a in THROUGHPUT_ARMS:
        rows = [r for r in decodes if r["arm"] == a]
        keys = sorted((r["prompt_id"], r["pass_idx"]) for r in rows)
        pids = sorted({r["prompt_id"] for r in rows})
        want = sorted((pid, p) for pid in pids for p in (1, 2))
        if (len(rows) != N_TEVAL * N_PASSES or set(pids) != EXPECTED_TEVAL_IDS
                or keys != want):
            decode_shape_ok = False
            continue
        nt = decode_tot(rows, "new_tokens"); ws = decode_tot(rows, "wall_s")
        if nt <= 0 or ws <= 0:
            decode_shape_ok = False
            continue
        mb[a] = decode_tot(rows, "miss_bytes") / nt
        tokps[a] = nt / ws
        match_rate[a] = decode_tot(rows, "match_tokens_vs_b0") / nt
        per_pass = {}
        for p in (1, 2):
            pr = [r for r in rows if r["pass_idx"] == p]
            ntp = sum(r["new_tokens"] for r in pr); wsp = sum(r["wall_s"] for r in pr)
            per_pass[p] = (ntp / wsp) if (ntp > 0 and wsp > 0) else None
        tokps_pass[a] = per_pass
    gates["decode_config_valid"] = bool(rg("decode_config_valid") and decode_shape_ok)

    # COMMON-TOKEN replay (review finding A3 + re-review item 2, ASM-2401):
    # the GATED realized-dose currency. Same forced trajectory for every arm
    # => miss-byte differences are attributable to the mask alone; tolerance
    # tightened to 5% of the dose (was 25%). Commonality is proven by
    # TRAJECTORY-DIGEST IDENTITY against the pinned s4-b0 reference digests
    # (meta.replay_reference.digests, whose source file is pinned in
    # meta.pins.reference_trajectories) — equal token COUNTS over different
    # forced sequences VOID io_match; the count check is kept as a cheap
    # coherence cross-check only.
    ref_digests = (meta.get("replay_reference") or {}).get("digests") or {}
    ref_ok = (set(ref_digests) == set(EXPECTED_TEVAL_IDS)
              and all(is_hex64(v) for v in ref_digests.values()))
    replay_mb = {}
    replay_ok = ref_ok
    replay_by_arm = {a: [r for r in replays if r["arm"] == a] for a in THROUGHPUT_ARMS}
    if len(budgets) != 1 or not budgets.issubset(set(TEVAL_TOKEN_BUDGETS)):
        replay_ok = False
    for a in THROUGHPUT_ARMS:
        rows = replay_by_arm[a]
        pids = sorted({r["prompt_id"] for r in rows})
        if len(rows) != N_TEVAL or set(pids) != EXPECTED_TEVAL_IDS:
            replay_ok = False
            continue
        if ref_ok and any(r["traj_sha256"] != ref_digests.get(r["prompt_id"])
                          for r in rows):
            replay_ok = False            # divergent forced sequence: not common-token
            continue
        ft = decode_tot(rows, "forced_tokens")
        if ft <= 0:
            replay_ok = False
            continue
        replay_mb[a] = decode_tot(rows, "miss_bytes") / ft
    if replay_ok:
        # coherence cross-check: forced token counts must also agree per prompt
        ft_of = {(r["arm"], r["prompt_id"]): r["forced_tokens"] for r in replays}
        pids = sorted({r["prompt_id"] for r in replays})
        for pid in pids:
            counts = {ft_of.get((a, pid)) for a in THROUGHPUT_ARMS}
            if len(counts) != 1 or None in counts:
                replay_ok = False
                break
    rr = {}
    if replay_ok and replay_mb.get("s4-b0", 0) > 0:
        for a in THROUGHPUT_ARMS:
            rr[a] = (replay_mb["s4-b0"] - replay_mb[a]) / replay_mb["s4-b0"]
    if replay_ok and rr.get("s4-semd", 0) > 0:
        real_err = abs(rr["s4-bldf-d"] - rr["s4-semd"]) / rr["s4-semd"]
    else:
        real_err = 1.0
        replay_ok = False
    gates["io_match_valid"] = bool(proj_ok and replay_ok and real_err <= REAL_DOSE_TOL)
    gates["all_valid"] = all(gates.values())

    # ---------------- contrasts (winsorized, family-clustered) --------------
    def clusters_for(id_set, delta_fn):
        fams = sorted({pinned_family(i) for i in id_set})
        return [[wins(delta_fn(i)) for i in id_set if pinned_family(i) == f]
                for f in fams]

    # PRIMARY: blind-frequency minus semantic-composite at matched removed I/O.
    prim = lambda i: table[(i, "s4-bldf-d")] - table[(i, "s4-semd")]
    raw = [prim(i) for i in primary_complete]
    n_winsorized = sum(1 for x in raw if abs(x) > WINSOR_NATS)
    T_raw = sum(raw) / len(raw)
    ci_p = boot_ci(clusters_for(primary_complete, prim), BOOT_SEED)
    T = ci_p["mean"]
    lb95 = ci_p["p5"]            # one-sided 95% lower confidence bound
    ub95 = ci_p["p95"]           # one-sided 95% upper confidence bound (kill rule)
    primary_joint = bool(lb95 > 0 and T >= SESOI_NATS)
    tost_equiv = bool(-TOST_MARGIN < ci_p["p5"] and ci_p["p95"] < TOST_MARGIN)

    # secondaries: each on its OWN pairwise-complete id set (review B2)
    secondary_n = {}

    def pairwise_ci(arm_hi, arm_lo, salt):
        id_set = [i for i in sorted(EXPECTED_IDS)
                  if (i, arm_hi) in table and (i, arm_lo) in table]
        secondary_n["%s-vs-%s" % (arm_hi, arm_lo)] = len(id_set)
        if not id_set:
            return None
        return boot_ci(clusters_for(id_set, lambda i: table[(i, arm_hi)] - table[(i, arm_lo)]),
                       BOOT_SEED + salt)

    ci16 = pairwise_ci("s4-sem16", "s4-b0", 1)
    joint16_noninf = bool(ci16 and ci16["p95"] < NONINF_MARGIN)
    ci_rm = pairwise_ci("s4-remap16", "s4-sem16", 3)

    rb_present = [a for a in RANDBLIND if a not in dropped_set]
    rb_ids = [i for i in sorted(EXPECTED_IDS)
              if (i, "s4-semd") in table and all((i, a) in table for a in rb_present)]
    secondary_n["randblind-vs-s4-semd"] = len(rb_ids)
    ci_rb = None
    if rb_present and rb_ids:
        ci_rb = boot_ci(clusters_for(
            rb_ids, lambda i: sum(table[(i, a)] for a in rb_present) / len(rb_present)
            - table[(i, "s4-semd")]), BOOT_SEED + 2)

    arm_mean = {a: (sum(table[(i, a)] for i in primary_complete if (i, a) in table)
                    / max(1, sum(1 for i in primary_complete if (i, a) in table)))
                for a in expected_arms}

    # ---------------- kill / pass (revised decision rule, review D1) --------
    if dose_achieved < DOSE_BAND_LO and not dose_capped:
        # skeptic-5 R2 finding 3 (final-phase mirror): the pinned builder
        # cannot emit a sub-2% dose without dose_capped.
        die("ERR_S4A_DOSE_INCOHERENT", "projected dose %.4f < %.2f with dose_capped "
            "false — the pinned builder cannot produce this; refusing"
            % (dose_achieved, DOSE_BAND_LO))
    # Re-review item 5 (ASM-2403): the [2%, 8%) dose band is enforced in FINAL
    # mode too — the registered protocol STOPS pre-spend inside the band, so a
    # final stream carrying an in-band projected dose bypassed the stop and is
    # protocol-violating input, REFUSED fail-closed (never graded).
    if DOSE_BAND_LO <= dose_achieved < DOSE_BAND_HI:
        die("ERR_S4A_DOSE_BAND", "final-phase projected dose %.4f lies inside the "
            "registered [%.2f, %.2f) pre-spend stop band — the construction stop "
            "cannot be bypassed; refusing" % (dose_achieved, DOSE_BAND_LO, DOSE_BAND_HI))
    dose_realized = rr.get("s4-semd")
    # Re-review item 5 (ASM-2403): realized/projected coherence. At a lawful
    # (>= 8%) projected dose, the realized replay dose may not EXCEED the
    # projection by more than REAL_PROJ_COH_TOL (3x the stipulated transfer
    # sigma_rel 0.05, ASM-2399) and may not collapse below the 2% band floor:
    # either combination means the masks audit and the replay counters
    # contradict each other — an instrument lie, refused, never graded.
    # (Shortfall down to 2% stays lawful: it is handled by the 8% PASS/KILL
    # floor as INCONCLUSIVE — the tie-at-sub-floor-dose branch.)
    if replay_ok and is_num(dose_realized) and dose_achieved >= DOSE_BAND_HI:
        if dose_realized > dose_achieved * (1.0 + REAL_PROJ_COH_TOL):
            die("ERR_S4A_DOSE_INCOHERENT", "realized replay dose %.4f exceeds the "
                "projected dose %.4f by more than the registered coherence "
                "tolerance %.2f — masks audit and replay counters contradict; "
                "refusing" % (dose_realized, dose_achieved, REAL_PROJ_COH_TOL))
        if dose_realized < DOSE_BAND_LO:
            die("ERR_S4A_DOSE_INCOHERENT", "realized replay dose %.4f collapsed "
                "below the %.2f band floor at projected %.4f — catastrophic "
                "projection->replay transfer failure; refusing"
                % (dose_realized, DOSE_BAND_LO, dose_achieved))
    kill_reason = ""
    kill = False
    if gates["all_valid"]:
        if dose_capped and dose_achieved < IO_MIN_FRAC:
            kill, kill_reason = True, ("dose-capped: achievable semantic removed-I/O "
                                       "%.4f < IO_MIN_FRAC %.2f — no physically "
                                       "meaningful drop dose exists at current causal+"
                                       "rare-tail coverage" % (dose_achieved, IO_MIN_FRAC))
        elif ub95 < SESOI_NATS:
            # skeptic-5 R2 finding 1: kill-1 carries the SAME dose floor as
            # PASS — a quality tie observed at a sub-floor realized dose is
            # INCONCLUSIVE (the lever question was not asked at lever scale),
            # never a terminal FAIL; lower doses shrink deltas monotonically,
            # so an unfloored ub-kill would be a spurious-kill gradient.
            if is_num(dose_realized) and dose_realized >= PASS_DOSE_FRAC:
                kill, kill_reason = True, ("primary one-sided 95%% upper bound %.4f < "
                                           "SESOI %.2f at realized dose %.4f >= %.2f: "
                                           "the data affirm there is NO composite-mask "
                                           "selective advantage as large as the "
                                           "registered SESOI over the matched-removed-"
                                           "I/O frequency-blind mask at lever-scale "
                                           "dose" % (ub95, SESOI_NATS, dose_realized,
                                                     PASS_DOSE_FRAC))

    tok_gain, gain_by_pass = None, {}
    if is_num(tokps.get("s4-semd")) and is_num(tokps.get("s4-b0")) and tokps["s4-b0"] > 0:
        tok_gain = tokps["s4-semd"] / tokps["s4-b0"] - 1.0
        for p in (1, 2):
            a = (tokps_pass.get("s4-semd") or {}).get(p)
            b = (tokps_pass.get("s4-b0") or {}).get(p)
            gain_by_pass[str(p)] = (a / b - 1.0) if (is_num(a) and is_num(b) and b > 0) else None
    tok_clause = bool(tok_gain is not None and tok_gain >= TOKPS_MIN_GAIN
                      and all(is_num(g) and g > 0 for g in gain_by_pass.values())
                      and len(gain_by_pass) == 2)
    pass_gate = bool(gates["all_valid"] and primary_joint
                     and is_num(dose_realized) and dose_realized >= PASS_DOSE_FRAC
                     and tok_clause)

    cost = meta.get("cost") or {}
    analysis = null_analysis({
        "phase": "final", "construction_stop": None,
        "n_items": len(ids), "n_primary_complete": len(primary_complete),
        "n_families": len(families),
        "incomplete_by_arm": incomplete_by_arm,
        "dropped_arms": sorted(dropped_set) if dropped_ok else dropped,
        "secondary_n_items": secondary_n,
        "telemetry_tier": tel.get("tier"),
        "primary_delta_nats": T,
        "primary_delta_raw_nats": T_raw,
        "n_winsorized": n_winsorized,
        "primary_ci95": [ci_p["p2_5"], ci_p["p97_5"]],
        "primary_lb95": lb95, "primary_ub95": ub95,
        "primary_joint_pass": primary_joint,
        "tost90_ci": [ci_p["p5"], ci_p["p95"]],
        "tost_equiv_at_margin": tost_equiv,
        "liveness": liveness_diag,
        "dose_target_frac": dose_target,
        "dose_achieved_frac": dose_achieved,
        "dose_achieved_realized": dose_realized,
        "dose_capped": dose_capped,
        "removed_io_bytes_per_tok": semd_audit.get("removed_bytes_per_tok"),
        "io_match_rel_err_projected": max(proj_errs) if proj_errs else None,
        "io_match_rel_err_realized": real_err,
        "joint16_delta_nats": ci16["mean"] if ci16 else None,
        "joint16_ci95": [ci16["p2_5"], ci16["p97_5"]] if ci16 else None,
        "joint16_upper95": ci16["p95"] if ci16 else None,
        "joint16_noninferior": joint16_noninf,
        "randblind_delta_nats": ci_rb["mean"] if ci_rb else None,
        "randblind_ci95": [ci_rb["p2_5"], ci_rb["p97_5"]] if ci_rb else None,
        "randblind_n_realizations": len(rb_present),
        "remap16_delta_nats": ci_rm["mean"] if ci_rm else None,
        "remap16_ci95": [ci_rm["p2_5"], ci_rm["p97_5"]] if ci_rm else None,
        "arm_mean_nll": arm_mean,
        "tokps": tokps, "missbytes_per_tok": mb,
        "replay_missbytes_per_tok": replay_mb,
        "tokps_gain_semd_vs_b0": tok_gain,
        "tokps_gain_by_pass": gain_by_pass,
        "decode_match_rate": match_rate,
        "mask_cell_counts": {a: (arms_audit.get(a) or {}).get("cells")
                             for a in QUALITY_ARMS if a != "s4-b0"},
        "kill_fired": kill, "kill_reason": kill_reason,
        "pass_gate": pass_gate,
        "accuracy": {"definition": "quality endpoint is teacher-forced mean NLL/target-token "
                                    "on the pinned 300-item suite (lower better); no "
                                    "correctness/accuracy claim is licensed by this record",
                     "arm_mean_nll": arm_mean},
        "params": {"added": 0, "note": "drop/remap select among native experts; nothing is "
                                        "trained or written"},
        "memory": {"mask_cells": {a: (arms_audit.get(a) or {}).get("cells")
                                  for a in QUALITY_ARMS if a != "s4-b0"},
                   "note": "mask tables are KB-scale sidecars; no shard-size or "
                           "page-cache-pool claim attaches"},
        "inference_compute": {"quality_prefills": len(items),
                              "decode_tokens_teval": int(sum(r["new_tokens"] for r in decodes)),
                              "replay_tokens_teval": int(sum(r["forced_tokens"] for r in replays)),
                              "telemetry_decode_tokens": tel.get("decode_tokens")},
        "training_compute": {"flops": 0, "note": "identically zero by construction"},
        "cost_ledger": {"realized_usd": cost.get("realized_usd"), "wall_h": cost.get("wall_h"),
                        "n_checkpoints": len(cost.get("checkpoints") or []),
                        "usd_cap": COST_CAP_USD, "wall_cap_h": COST_CAP_WALL_H},
    })
    return {"gates": gates, "analysis": analysis}


def compute(meta, items, decodes, replays):
    if meta["phase"] == "construction":
        return compute_construction(meta)
    return compute_final(meta, items, decodes, replays)


def emit(out):
    sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


# ------------------------------------------------------------------ selftest
def _hex(tag):
    return hashlib.sha256(("s4mock-pin:%s" % tag).encode()).hexdigest()


def _pins(final=True):
    keys = PIN_KEYS_FINAL if final else PIN_KEYS_CONSTRUCTION
    return {k: _hex(k) for k in keys}


def _checkpoints(final=True):
    if not final:
        return [{"label": "telemetry", "usd": 2.4}, {"label": "masks", "usd": 3.1}]
    labels = (["telemetry", "masks", "bring-up"]
              + ["quality-%s" % a for a in QUALITY_ARMS]
              + ["t-eval", "replay"])
    return [{"label": lab, "usd": round(16.2 * (i + 1) / len(labels), 4)}
            for i, lab in enumerate(labels)]


def _fixture(scenario: str):
    """Synthetic kot-s4row/2 stream for one decision branch. Deterministic
    (SHA-256 noise only). Cost figures carry the REGISTERED planning-scale
    values (realized_usd 16.2 / wall_h 14.1) so the ledger scale floor stays
    green on a $0 mock (F1-K round-6 lesson)."""
    def noise(tag, i, scale):
        r = int(hashlib.sha256(("s4mock:%s:%s:%d" % (scenario, tag, i)).encode()).hexdigest(), 16)
        return ((r % 20001) - 10000) / 10000.0 * scale

    construction = scenario in ("kill-dose", "band-stop")
    gates = {"pins_valid": True, "suite_disjoint_valid": True,
             "mask_construction_valid": True, "decode_config_valid": True,
             "inertness_valid": True}
    dose_capped, dose_frac = False, 0.098
    if scenario == "kill-dose":
        dose_capped, dose_frac = True, 0.015
    if scenario == "band-stop":
        dose_capped, dose_frac = True, 0.05
    if scenario == "void-gate":
        gates["inertness_valid"] = False
    arms_audit = {
        "s4-sem16": {"cells": 16, "removed_bytes_per_tok": 2.3e6, "removed_frac": 0.0007},
        "s4-remap16": {"cells": 16, "removed_bytes_per_tok": 2.3e6, "removed_frac": 0.0007,
                        "swaps": 9},
        "s4-semd": {"cells": 509, "removed_bytes_per_tok": 3.19e8, "removed_frac": dose_frac,
                     "tier0_used": 16, "tier1_used": 6},
        "s4-bldf-d": {"cells": 9920, "removed_bytes_per_tok": 3.13e8,
                       "removed_frac": dose_frac * 0.99, "match_rel_err": 0.0199},
        "s4-bldr-d-r1": {"cells": 765, "removed_bytes_per_tok": 3.13e8,
                          "removed_frac": dose_frac * 0.99, "match_rel_err": 0.018, "seed": 20260803},
        "s4-bldr-d-r2": {"cells": 780, "removed_bytes_per_tok": 3.13e8,
                          "removed_frac": dose_frac * 0.99, "match_rel_err": 0.0199, "seed": 20260804},
        "s4-bldr-d-r3": {"cells": 766, "removed_bytes_per_tok": 3.13e8,
                          "removed_frac": dose_frac * 0.99, "match_rel_err": 0.0186, "seed": 20260805},
    }
    meta = {"kind": "meta", "schema": SCHEMA,
            "phase": "construction" if construction else "final",
            "gates": gates,
            "pins": _pins(final=not construction),
            "telemetry": {"tier": "M", "total_expert_miss_bytes_per_tok": 3.26e9,
                          "decode_tokens": 3072},
            "masks": {"dose_frac_target": 0.10, "dose_capped": dose_capped,
                      "construction_kill": ({"fired": True, "reason": "dose-zero",
                                              "achieved_frac": 0.0}
                                             if scenario == "kill-dose" and dose_frac == 0.0
                                             else None),
                      "arms": arms_audit},
            "degradation": {"dropped_arms": []},
            "cost": ({"realized_usd": 3.1, "wall_h": 1.6,
                      "checkpoints": _checkpoints(final=False)}
                     if construction else
                     {"realized_usd": 16.2, "wall_h": 14.1,
                      "checkpoints": _checkpoints(final=True)}),
            "seeds": {"bootstrap": BOOT_SEED}}
    if not construction:
        # pinned per-prompt reference-trajectory digests (ASM-2401)
        meta["replay_reference"] = {"digests": {"s4d-e%02d" % p: _hex("traj:%02d" % p)
                                                for p in range(N_TEVAL)}}
    rows = [meta]
    if construction:
        return rows
    # per-branch true effects (nats/tok)
    eff = {"pass": 0.09, "kill-ub": 0.0, "inconclusive": 0.045,
           "lb0-notkill": 0.04, "void-gate": 0.09, "tost": 0.0,
           "tie-lowdose": 0.0, "tost-lowdose": 0.0}[scenario]
    sd = {"tost": 0.02, "tost-lowdose": 0.02, "lb0-notkill": 0.5}.get(scenario, 0.15)
    for i in range(N_SUITE):
        iid = "s4q-%04d" % i
        base = 1.4 + abs(noise("base", i, 0.5))
        arm_nll = {
            "s4-b0": base,
            "s4-sem16": base + 0.004 + noise("s16", i, 0.02),
            "s4-remap16": base + 0.006 + noise("r16", i, 0.02),
            "s4-semd": base + 0.11 + noise("semd", i, sd),
            "s4-bldf-d": base + 0.11 + eff + noise("bldf", i, sd),
            "s4-bldr-d-r1": base + 0.12 + eff + noise("rb1", i, sd),
            "s4-bldr-d-r2": base + 0.12 + eff + noise("rb2", i, sd),
            "s4-bldr-d-r3": base + 0.12 + eff + noise("rb3", i, sd),
        }
        fam = pinned_family(iid)   # pinned 30-family mapping
        for a, v in arm_nll.items():
            rows.append({"kind": "item", "arm": a, "item_id": iid, "family": fam,
                         "nll_per_tok": max(0.01, v), "n_target_toks": 6})
    tokps = {"s4-b0": 0.20, "s4-sem16": 0.201, "s4-semd": 0.226, "s4-bldf-d": 0.224}
    mbt = {"s4-b0": 3.26e9, "s4-sem16": 3.25e9, "s4-semd": 2.94e9, "s4-bldf-d": 2.945e9}
    mbt_replay = dict(mbt)
    if scenario in ("tie-lowdose", "tost-lowdose"):
        # realized replay dose lands at ~6% (below the 8% floor) while the
        # arms stay matched: a quality tie here must be INCONCLUSIVE — and a
        # TOST equivalence here must NOT coincide with a kill (TOST is
        # dose-independent; kill trigger 1 carries the 8% floor; ASM-2403).
        mbt_replay["s4-semd"] = 3.0644e9
        mbt_replay["s4-bldf-d"] = 3.0654e9
    for a in THROUGHPUT_ARMS:
        for pi in (1, 2):
            speed = tokps[a] * (1.0 + (0.01 if pi == 2 else -0.01))
            for p in range(N_TEVAL):
                nt = 96
                rows.append({"kind": "decode", "arm": a, "prompt_id": "s4d-e%02d" % p,
                             "pass_idx": pi, "new_tokens": nt, "wall_s": nt / speed,
                             "miss_bytes": int(mbt[a] * nt),
                             "match_tokens_vs_b0": nt if a == "s4-b0" else int(nt * 0.93)})
        # COMMON-TOKEN replay rows: same forced trajectory (same digest) per arm
        for p in range(N_TEVAL):
            rows.append({"kind": "replay", "arm": a, "prompt_id": "s4d-e%02d" % p,
                         "forced_tokens": 96, "miss_bytes": int(mbt_replay[a] * 96),
                         "traj_sha256": _hex("traj:%02d" % p)})
    return rows


def _run_rows(rows):
    meta = [r for r in rows if r.get("kind") == "meta"]
    items = [r for r in rows if r.get("kind") == "item"]
    decodes = [r for r in rows if r.get("kind") == "decode"]
    replays = [r for r in rows if r.get("kind") == "replay"]
    return compute(meta[0], items, decodes, replays)


def selftest():
    import subprocess
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    outs = {}
    for scenario in ("pass", "kill-ub", "kill-dose", "band-stop", "void-gate",
                     "inconclusive", "lb0-notkill", "tost", "tie-lowdose",
                     "tost-lowdose"):
        outs[scenario] = _run_rows(_fixture(scenario))

    o = outs["pass"]
    ck("pass: gates all valid", o["gates"]["all_valid"])
    ck("pass: joint pass", o["analysis"]["primary_joint_pass"])
    ck("pass: pass_gate true", o["analysis"]["pass_gate"])
    ck("pass: not killed", not o["analysis"]["kill_fired"])
    ck("pass: liveness diagnostics live", o["gates"]["quality_liveness_valid"]
       and o["analysis"]["liveness"]["s4-semd"]["n_distinct"] >= LIVENESS_MIN_DISTINCT)
    o = outs["kill-ub"]
    ck("kill-ub: killed on upper bound", o["analysis"]["kill_fired"]
       and "upper bound" in o["analysis"]["kill_reason"])
    ck("kill-ub: no pass", not o["analysis"]["pass_gate"])
    o = outs["kill-dose"]
    ck("kill-dose: CONSTRUCTION-phase kill from telemetry+masks alone",
       o["analysis"]["phase"] == "construction" and o["analysis"]["kill_fired"]
       and "dose-capped" in o["analysis"]["kill_reason"]
       and o["analysis"]["construction_stop"] == "kill-dose")
    ck("kill-dose: cheap pre-spend ledger accepted", o["gates"]["cost_ledger_valid"])
    o = outs["band-stop"]
    ck("band-stop: [2%,8%) => pre-spend stop, not a kill",
       o["analysis"]["construction_stop"] == "dose-band-stop"
       and not o["analysis"]["kill_fired"] and not o["analysis"]["pass_gate"])
    o = outs["void-gate"]
    ck("void: gates invalid", not o["gates"]["all_valid"])
    ck("void: not killed (instrument, not outcome)", not o["analysis"]["kill_fired"])
    ck("void: no pass", not o["analysis"]["pass_gate"])
    o = outs["inconclusive"]
    ck("inconclusive: under SESOI, upper bound above it", o["analysis"]["primary_ub95"] >= SESOI_NATS
       and not o["analysis"]["primary_joint_pass"] and not o["analysis"]["kill_fired"]
       and not o["analysis"]["pass_gate"])
    o = outs["lb0-notkill"]
    ck("lb<=0 with ub>=SESOI is INCONCLUSIVE, never a kill (review D1)",
       o["analysis"]["primary_lb95"] <= 0 and o["analysis"]["primary_ub95"] >= SESOI_NATS
       and not o["analysis"]["kill_fired"] and not o["analysis"]["pass_gate"])
    o = outs["tost"]
    ck("tost: equivalence at margin", o["analysis"]["tost_equiv_at_margin"])
    ck("tost: killed (ub < SESOI affirms the pre-named null)", o["analysis"]["kill_fired"])
    o = outs["tie-lowdose"]
    ck("quality tie at sub-floor realized dose is INCONCLUSIVE, not a kill (skeptic-5 f1)",
       o["gates"]["all_valid"] and o["analysis"]["primary_ub95"] < SESOI_NATS
       and o["analysis"]["dose_achieved_realized"] < PASS_DOSE_FRAC
       and not o["analysis"]["kill_fired"] and not o["analysis"]["pass_gate"])
    o = outs["tost-lowdose"]
    ck("TOST does NOT coincide with kill at sub-floor dose (dose-independent TOST, "
       "8%-floored kill; re-review item 5)",
       o["gates"]["all_valid"] and o["analysis"]["tost_equiv_at_margin"]
       and o["analysis"]["dose_achieved_realized"] < PASS_DOSE_FRAC
       and not o["analysis"]["kill_fired"] and not o["analysis"]["pass_gate"])

    # every declared output field present in every branch (incl. construction)
    def has_ptr(out, ptr):
        node = out
        for part in ptr.strip("/").split("/"):
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return True
    for scenario, o in outs.items():
        ck("fields complete: %s" % scenario, all(has_ptr(o, p) for p in OUTPUT_FIELDS))

    # byte-determinism
    a = json.dumps(_run_rows(_fixture("pass")), sort_keys=True)
    b = json.dumps(_run_rows(_fixture("pass")), sort_keys=True)
    ck("byte-deterministic recompute", a == b)

    # ---------------- adversarial replays (cross-model review 2026-07-16):
    # each of these previously produced a PASS/KILL and must now be gated ----
    T_ref = outs["pass"]["analysis"]["primary_delta_nats"]

    # (B1) inert readout: all-equal NLLs => INSTRUMENT-INVALID, never a kill
    rows = _fixture("kill-ub")
    for r in rows:
        if r.get("kind") == "item":
            r["nll_per_tok"] = 1.5
    o = _run_rows(rows)
    ck("inert all-equal NLLs => liveness gate, NOT a kill",
       not o["gates"]["quality_liveness_valid"] and not o["gates"]["all_valid"]
       and not o["analysis"]["kill_fired"])
    # (B1) rounded readout: 1-decimal NLLs => liveness gate
    rows = _fixture("kill-ub")
    for r in rows:
        if r.get("kind") == "item":
            r["nll_per_tok"] = round(r["nll_per_tok"], 1)
    o = _run_rows(rows)
    ck("rounded (1dp) NLLs => liveness gate, NOT a kill",
       not o["gates"]["quality_liveness_valid"] and not o["analysis"]["kill_fired"])
    # (B2) dropping 5 SECONDARY rows cannot move the primary
    rows = _fixture("pass")
    drop_ids = {"s4q-%04d" % i for i in range(5)}
    rows = [r for r in rows if not (r.get("kind") == "item" and r.get("arm") == "s4-bldr-d-r1"
                                    and r.get("item_id") in drop_ids)]
    o = _run_rows(rows)
    ck("secondary-arm missingness leaves the primary IDENTICAL and gates valid",
       o["analysis"]["primary_delta_nats"] == T_ref and o["gates"]["completeness_valid"])
    # (B2) a missing PRIMARY-arm row voids completeness (zero-missing rule)
    rows = _fixture("pass")
    rows = [r for r in rows if not (r.get("kind") == "item" and r.get("arm") == "s4-semd"
                                    and r.get("item_id") == "s4q-0000")]
    ck("one missing primary-pair row voids completeness",
       not _run_rows(rows)["gates"]["completeness_valid"])
    # (B3) collapsed family labels => family gate FAILS (was: silent PASS)
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "item":
            r["family"] = "add4"
    o = _run_rows(rows)
    ck("collapsed one-family labels FAIL the family gate",
       not o["gates"]["family_valid"] and not o["gates"]["all_valid"])
    # (A3) blind removing ~25% more I/O than semd => io_match FAILS at 5%
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "replay" and r.get("arm") == "s4-bldf-d":
            r["miss_bytes"] = int(2.86e9 * r["forced_tokens"])   # rr ~ 0.123 vs semd 0.098
    o = _run_rows(rows)
    ck("24.9%-of-dose realized mismatch now VOIDS io_match (5% gate)",
       not o["gates"]["io_match_valid"] and o["analysis"]["io_match_rel_err_realized"] > REAL_DOSE_TOL)
    # (A3) divergent forced trajectories => replay invalid
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "replay" and r.get("arm") == "s4-semd" \
                and r.get("prompt_id") == "s4d-e00":
            r["forced_tokens"] = 80
    ck("non-common replay trajectories void io_match",
       not _run_rows(rows)["gates"]["io_match_valid"])
    # (skeptic-5 f4) rows must bind to the pinned T-eval corpus
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "decode" and r.get("prompt_id") == "s4d-e00" \
                and r.get("arm") == "s4-b0":
            r["prompt_id"] = "s4d-x00"
    ck("off-corpus decode prompt id voids decode_config",
       not _run_rows(rows)["gates"]["decode_config_valid"])
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "replay" and r.get("prompt_id") == "s4d-e07":
            r["prompt_id"] = "s4d-x07"
    ck("off-corpus replay prompt id voids io_match",
       not _run_rows(rows)["gates"]["io_match_valid"])
    rows = _fixture("pass")
    for r in rows:
        if r.get("kind") == "decode":
            r["new_tokens"] = 50
        elif r.get("kind") == "replay":
            r["forced_tokens"] = 50
    o = _run_rows(rows)
    ck("off-schedule token budget (50) voids decode_config and io_match",
       not o["gates"]["decode_config_valid"] and not o["gates"]["io_match_valid"])
    rows = _fixture("pass")
    for r in rows:   # ladder rung 2: uniform 64-token budget stays lawful
        if r.get("kind") == "decode":
            r["wall_s"] = r["wall_s"] * 64.0 / 96.0
            r["miss_bytes"] = int(r["miss_bytes"] * 64.0 / 96.0)
            r["match_tokens_vs_b0"] = 64 if r["arm"] == "s4-b0" else int(64 * 0.93)
            r["new_tokens"] = 64
        elif r.get("kind") == "replay":
            r["miss_bytes"] = int(r["miss_bytes"] * 64.0 / 96.0)
            r["forced_tokens"] = 64
    o = _run_rows(rows)
    ck("ladder rung-2 64-token budget stays lawful", o["gates"]["decode_config_valid"]
       and o["gates"]["io_match_valid"] and o["gates"]["all_valid"])
    # (C2) placeholder / missing pins => pins_present gate
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0]["pins"]["weights"] = "0" * 64
    ck("placeholder weights digest fails pins_present", not _run_rows(rows)["gates"]["pins_present_valid"])
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0]["pins"].pop("runner_script")
    ck("missing runner_script pin fails pins_present", not _run_rows(rows)["gates"]["pins_present_valid"])
    # (D3) live-ledger shape: no checkpoints / non-monotone / mid-run breach
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0]["cost"]["checkpoints"] = []
    ck("missing live checkpoints fail the ledger gate", not _run_rows(rows)["gates"]["cost_ledger_valid"])
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["cost"]["checkpoints"][5]["usd"] = 41.0
    ck("mid-run cap breach fails the ledger gate", not _run_rows(rows)["gates"]["cost_ledger_valid"])
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0]["cost"]["realized_usd"] = 0.0
    ck("ledger scale floor gates out a $0 ledger", not _run_rows(rows)["gates"]["cost_ledger_valid"])
    # (D3) registered ladder: dropping r2/r3 keeps the primary + gates intact
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["degradation"]["dropped_arms"] = ["s4-bldr-d-r2", "s4-bldr-d-r3"]
    rows = [r for r in rows if not (r.get("kind") == "item"
                                    and r.get("arm") in ("s4-bldr-d-r2", "s4-bldr-d-r3"))]
    o = _run_rows(rows)
    ck("ladder drop of r2/r3 is analysis-compatible (primary identical, gates valid)",
       o["analysis"]["primary_delta_nats"] == T_ref and o["gates"]["all_valid"]
       and o["analysis"]["randblind_n_realizations"] == 1)
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["degradation"]["dropped_arms"] = ["s4-bldf-d"]
    ck("dropping a PRIMARY arm is never lawful", not _run_rows(rows)["gates"]["completeness_valid"])
    # seeds + completeness legacy shapes
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0]["seeds"]["bootstrap"] = 1
    ck("wrong bootstrap seed gates out", not _run_rows(rows)["gates"]["seeds_valid"])
    rows = _fixture("pass")
    drop_ids = {"s4q-%04d" % i for i in range(7)}
    rows = [r for r in rows if not (r.get("kind") == "item" and r.get("arm") == "s4-sem16"
                                    and r.get("item_id") in drop_ids)]
    ck("secondary arm >5 incomplete (not ladder-dropped) voids completeness",
       not _run_rows(rows)["gates"]["completeness_valid"])
    rows = _fixture("pass")
    rows = [r for r in rows if not (r.get("kind") == "decode" and r.get("arm") == "s4-bldf-d"
                                    and r.get("prompt_id") == "s4d-e00"
                                    and r.get("pass_idx") == 1)]
    ck("missing decode row voids decode_config", not _run_rows(rows)["gates"]["decode_config_valid"])
    rows = _fixture("pass")
    for r in rows:   # one catastrophic item: winsorization must count + cap it
        if (r.get("kind") == "item" and r.get("arm") == "s4-bldf-d"
                and r.get("item_id") == "s4q-0007"):
            r["nll_per_tok"] = 40.0
    o = _run_rows(rows)
    ck("winsorization counts and caps a catastrophic item",
       o["analysis"]["n_winsorized"] == 1
       and o["analysis"]["primary_delta_raw_nats"] > o["analysis"]["primary_delta_nats"])
    rows = _fixture("pass")
    for r in rows:   # kill a single pass's tok/s gain: PASS clause must fail
        if (r.get("kind") == "decode" and r.get("arm") == "s4-semd"
                and r.get("pass_idx") == 2):
            r["wall_s"] = r["new_tokens"] / 0.19
    o = _run_rows(rows)
    ck("one negative-pass tok/s gain blocks pass_gate", not o["analysis"]["pass_gate"]
       and not o["analysis"]["kill_fired"])

    # ---------------- round-3 re-review adversarial replays (items 2/3/5):
    # each previously produced a spurious PASS/KILL and must now be gated ----
    # (item 2) equal-token-count DIVERGENT forced sequence: same count (96),
    # different trajectory digest => io_match VOID (was: PASSed on count)
    rows = _fixture("pass")
    for r in rows:
        if (r.get("kind") == "replay" and r.get("arm") == "s4-semd"
                and r.get("prompt_id") == "s4d-e00"):
            r["traj_sha256"] = _hex("evil-divergent-sequence")   # forced_tokens stays 96
    o = _run_rows(rows)
    ck("equal-length divergent trajectory (digest mismatch) VOIDS io_match",
       not o["gates"]["io_match_valid"] and not o["analysis"]["pass_gate"]
       and not o["analysis"]["kill_fired"])
    # (item 2) missing pinned reference digest map => io_match fail-closed
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0])); rows[0].pop("replay_reference")
    ck("missing replay_reference digest map voids io_match",
       not _run_rows(rows)["gates"]["io_match_valid"])
    # (item 2) contradictory projected audit: fields say blind 0.05 vs SEM-D
    # 0.098 (49% mismatch) while supplied match_rel_err claims 1% — the
    # RECOMPUTE must win (was: trusted supplied value => PASS)
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    aud = rows[0]["masks"]["arms"]["s4-bldf-d"]
    aud["removed_frac"] = 0.05
    aud["removed_bytes_per_tok"] = 1.628e8
    aud["match_rel_err"] = 0.01
    o = _run_rows(rows)
    ck("contradictory projected audit (0.05 vs 0.098, claimed 1%) FAILS io_match",
       not o["gates"]["io_match_valid"]
       and o["analysis"]["io_match_rel_err_projected"] > MATCH_TOL_PROJ)
    # (item 2) audit self-consistency: matched fields but a match_rel_err
    # incoherent with them (under-reported) is a lying audit => VOID
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["masks"]["arms"]["s4-bldf-d"]["match_rel_err"] = 0.0001
    ck("match_rel_err incoherent with the audit's own fields voids io_match",
       not _run_rows(rows)["gates"]["io_match_valid"])
    # (item 3) near-zero-variance primary pair (1e-12-scale jitter, >=50
    # distinct values): liveness FLOOR => INSTRUMENT-INVALID, never a KILL
    # on lb~0 (was: mathematically positive variance passed liveness)
    rows = _fixture("kill-ub")
    for r in rows:
        if r.get("kind") == "item":
            r["nll_per_tok"] = 1.5 + (r["nll_per_tok"] % 7e-4) * 1e-9
    o = _run_rows(rows)
    ck("near-zero-variance jitter => liveness floor (INSTRUMENT-INVALID), NOT a kill",
       not o["gates"]["quality_liveness_valid"] and not o["gates"]["all_valid"]
       and not o["analysis"]["kill_fired"]
       and o["analysis"]["liveness"]["s4-semd"]["n_distinct"] >= LIVENESS_MIN_DISTINCT)
    # (item 5) ledger: 13 duplicate placeholder checkpoints at $16.20 => VOID
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    for cp in rows[0]["cost"]["checkpoints"]:
        cp["label"] = "x"
    ck("duplicate placeholder ('x' x 13) checkpoints fail the ledger gate",
       not _run_rows(rows)["gates"]["cost_ledger_valid"])
    # (item 5) registered order is binding
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    cps = rows[0]["cost"]["checkpoints"]
    cps[0]["label"], cps[1]["label"] = cps[1]["label"], cps[0]["label"]
    ck("out-of-registered-order checkpoints fail the ledger gate",
       not _run_rows(rows)["gates"]["cost_ledger_valid"])
    # (item 5) a skipped registered boundary fails
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["cost"]["checkpoints"] = [cp for cp in rows[0]["cost"]["checkpoints"]
                                      if cp["label"] != "bring-up"]
    ck("skipped registered boundary (bring-up) fails the ledger gate",
       not _run_rows(rows)["gates"]["cost_ledger_valid"])
    # (item 5) a droppable arm's checkpoint may be absent ONLY when dropped
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["cost"]["checkpoints"] = [cp for cp in rows[0]["cost"]["checkpoints"]
                                      if cp["label"] != "quality-s4-bldr-d-r2"]
    ck("missing r2 checkpoint WITHOUT a declared drop fails the ledger gate",
       not _run_rows(rows)["gates"]["cost_ledger_valid"])
    rows = _fixture("pass")
    rows[0] = json.loads(json.dumps(rows[0]))
    rows[0]["degradation"]["dropped_arms"] = ["s4-bldr-d-r2", "s4-bldr-d-r3"]
    rows[0]["cost"]["checkpoints"] = [
        cp for cp in rows[0]["cost"]["checkpoints"]
        if cp["label"] not in ("quality-s4-bldr-d-r2", "quality-s4-bldr-d-r3")]
    rows = [r for r in rows if not (r.get("kind") == "item"
                                    and r.get("arm") in ("s4-bldr-d-r2", "s4-bldr-d-r3"))]
    o = _run_rows(rows)
    ck("ladder drop with absent dropped-arm checkpoints stays lawful",
       o["gates"]["cost_ledger_valid"] and o["gates"]["all_valid"])

    # fail-closed rejections via subprocess (stdin path, no argv)
    def expect_fail(mutator, code):
        rows = _fixture("pass")
        rows = mutator(rows)
        payload = "\n".join(json.dumps(r) for r in rows) + "\n"
        r = subprocess.run([sys.executable, __file__], input=payload,
                           capture_output=True, text=True)
        return r.returncode != 0 and code in r.stderr

    ck("rejects empty stdin", subprocess.run([sys.executable, __file__], input="",
       capture_output=True, text=True).returncode != 0)
    ck("rejects no meta", expect_fail(lambda rs: [r for r in rs if r.get("kind") != "meta"],
                                      "ERR_S4A_META"))
    ck("rejects dup meta", expect_fail(lambda rs: rs + [rs[0]], "ERR_S4A_META_DUP"))
    ck("rejects missing phase", expect_fail(
        lambda rs: [dict((k, v) for k, v in r.items() if k != "phase")
                    if r.get("kind") == "meta" else r for r in rs], "ERR_S4A_PHASE"))
    ck("rejects construction stream carrying rows", expect_fail(
        lambda rs: [dict(r, phase="construction") if r.get("kind") == "meta" else r
                    for r in rs], "ERR_S4A_PHASE"))
    ck("construction refuses to grade a healthy dose (>=8%)", expect_fail(
        lambda rs: [dict(r, phase="construction") for r in rs if r.get("kind") == "meta"],
        "ERR_S4A_PHASE"))
    ck("rejects unknown arm", expect_fail(
        lambda rs: rs + [{"kind": "item", "arm": "s4-nope", "item_id": "s4q-0000",
                          "nll_per_tok": 1.0, "n_target_toks": 5}], "ERR_S4A_ARM"))
    ck("rejects NaN nll", expect_fail(
        lambda rs: rs + [{"kind": "item", "arm": "s4-b0", "item_id": "s4q-0000",
                          "family": "add4", "nll_per_tok": float("nan"),
                          "n_target_toks": 5}], "ERR_S4A_ITEM"))
    ck("rejects non-suite item id", expect_fail(
        lambda rs: rs + [{"kind": "item", "arm": "s4-b0", "item_id": "s4q-9999",
                          "family": "add4", "nll_per_tok": 1.0, "n_target_toks": 5}],
        "ERR_S4A_ITEM_ID"))
    ck("rejects family-less item", expect_fail(
        lambda rs: [dict((k, v) for k, v in r.items() if k != "family")
                    if r.get("kind") == "item" and r.get("item_id") == "s4q-0001"
                    and r.get("arm") == "s4-b0" else r for r in rs], "ERR_S4A_FAMILY"))
    ck("rejects duplicate item row", expect_fail(
        lambda rs: rs + [next(r for r in rs if r.get("kind") == "item")], "ERR_S4A_ITEM_DUP"))
    ck("rejects bad meta schema", expect_fail(
        lambda rs: [dict(r, schema="x") if r.get("kind") == "meta" else r for r in rs],
        "ERR_S4A_SCHEMA"))
    ck("rejects unknown kind", expect_fail(lambda rs: rs + [{"kind": "wat"}], "ERR_S4A_KIND"))
    ck("rejects malformed replay row", expect_fail(
        lambda rs: rs + [{"kind": "replay", "arm": "s4-b0", "prompt_id": "s4d-e00",
                          "forced_tokens": 0, "miss_bytes": 1}], "ERR_S4A_REPLAY"))
    # round-3 item 3: n_target_toks REQUIRED + validated on every item row
    ck("stripping n_target_toks from ALL item rows is refused", expect_fail(
        lambda rs: [dict((k, v) for k, v in r.items() if k != "n_target_toks")
                    if r.get("kind") == "item" else r for r in rs], "ERR_S4A_ITEM"))
    ck("non-int n_target_toks refused", expect_fail(
        lambda rs: [dict(r, n_target_toks=6.5)
                    if (r.get("kind") == "item" and r.get("item_id") == "s4q-0000"
                        and r.get("arm") == "s4-b0") else r for r in rs], "ERR_S4A_ITEM"))
    ck("zero n_target_toks refused", expect_fail(
        lambda rs: [dict(r, n_target_toks=0)
                    if (r.get("kind") == "item" and r.get("item_id") == "s4q-0001"
                        and r.get("arm") == "s4-semd") else r for r in rs], "ERR_S4A_ITEM"))
    # round-3 item 2: a replay row without its trajectory digest is malformed
    ck("replay row without traj_sha256 refused", expect_fail(
        lambda rs: [dict((k, v) for k, v in r.items() if k != "traj_sha256")
                    if (r.get("kind") == "replay" and r.get("arm") == "s4-b0"
                        and r.get("prompt_id") == "s4d-e00") else r for r in rs],
        "ERR_S4A_REPLAY"))
    # round-3 item 5: FINAL stream with an in-band projected dose is REFUSED —
    # this is the review's projected-0.05 / realized-0.098 replay that PASSed

    def mut_final_band(rs):
        rs[0] = json.loads(json.dumps(rs[0]))
        arms = rs[0]["masks"]["arms"]
        arms["s4-semd"]["removed_frac"] = 0.05
        for a in ("s4-bldf-d", "s4-bldr-d-r1", "s4-bldr-d-r2", "s4-bldr-d-r3"):
            arms[a]["removed_frac"] = 0.05 * 0.99
        return rs
    ck("final stream with in-band projected dose (0.05) refused (band bypass)",
       expect_fail(mut_final_band, "ERR_S4A_DOSE_BAND"))
    # round-3 item 5: realized replay dose incoherent with the projection

    def mut_realized_excess(rs):
        for r in rs:
            if r.get("kind") == "replay" and r.get("arm") == "s4-semd":
                r["miss_bytes"] = int(2.8362e9 * r["forced_tokens"])   # rr ~ 0.130
        return rs
    ck("realized dose 0.130 at projected 0.098 refused (coherence, > 1.15x)",
       expect_fail(mut_realized_excess, "ERR_S4A_DOSE_INCOHERENT"))

    def mut_realized_collapse(rs):
        for r in rs:
            if r.get("kind") == "replay" and r.get("arm") == "s4-semd":
                r["miss_bytes"] = int(3.2111e9 * r["forced_tokens"])   # rr ~ 0.015
        return rs
    ck("realized dose collapsed to 1.5% at projected 9.8% refused",
       expect_fail(mut_realized_collapse, "ERR_S4A_DOSE_INCOHERENT"))
    # skeptic-5 f3: an uncapped sub-2% dose is incoherent input, both phases
    rows_c = _fixture("kill-dose")
    rows_c[0] = json.loads(json.dumps(rows_c[0])); rows_c[0]["masks"]["dose_capped"] = False
    payload = "\n".join(json.dumps(r) for r in rows_c) + "\n"
    r = subprocess.run([sys.executable, __file__], input=payload,
                       capture_output=True, text=True)
    ck("uncapped sub-2% construction dose refused (incoherent)",
       r.returncode != 0 and "ERR_S4A_DOSE_INCOHERENT" in r.stderr)

    def mut_final_incoherent(rs):
        rs[0] = json.loads(json.dumps(rs[0]))
        rs[0]["masks"]["dose_capped"] = False
        rs[0]["masks"]["arms"]["s4-semd"]["removed_frac"] = 0.015
        return rs
    ck("uncapped sub-2% final-phase dose refused (incoherent)",
       expect_fail(mut_final_incoherent, "ERR_S4A_DOSE_INCOHERENT"))

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    if failed:
        print("selftest: %d/%d FAILED" % (len(failed), len(checks)))
        sys.exit(1)
    print("selftest: %d/%d PASS (%d output fields on every branch)"
          % (len(checks), len(checks), len(OUTPUT_FIELDS)))


def main():
    if "--selftest" in sys.argv[1:]:
        selftest()
        return
    if sys.argv[1:]:
        die("ERR_S4A_ARGS", "no argv accepted (rows on stdin); only --selftest is recognized")
    meta, items, decodes, replays = read_rows(sys.stdin)
    emit(compute(meta, items, decodes, replays))


if __name__ == "__main__":
    main()
