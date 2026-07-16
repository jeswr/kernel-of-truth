#!/usr/bin/env python3
"""One-shot FREEZE-(A) COMPLETION fix pass over
registry/experiments/f1k.json (bead kernel-of-truth-hh2d).

The Opus experiment-runner's lawful pre-spend FAIL-CLOSED stop
(2026-07-16T09:23Z, poc/glm52-probe/f1k-harness/opus-runs/20260716T092312Z)
found freeze-manifest (A) (SSR-REV4.2) INCOMPLETE: three Fable-owned
design/definitional artifacts were not frozen —

  (1) the A(vii) CONSTRUCTION SEED had a name but NO VALUE anywhere in the
      frozen record (generator-spec /construction_seed: "NOT REGISTERED");
  (2) the d0 DIRECTION-GENERATION ALGORITHM (the mandatory placebo's
      random directions; load-bearing via the placebo voiding gate) was
      unregistered;
  (3) the CARRIER-CONSTRUCTION GENERATOR — the runnable software doing
      GLM-5.2 forward passes -> §2.4 mean difference -> the K/d0/d2/
      derangement .kaec master tables — did not exist as code.

This pass registers (1) construction seed = 20260716, (2) the kot-f1k-d0/1
algorithm VERBATIM, and (3) pins the authored generator
poc/glm52-probe/f1k-harness/build_carriers.py by sha256; it ALSO corrects
the construction pass accounting the generator made explicit (d2's §2.6
"same construction" needs its own WITH-dictionary passes: construction =
96 x 16 x 3 = 4,608 EXACT, not 3,072) and tightens the pilot envelope to
the driver's deterministic arithmetic (<= 2,112, superseding the ~6,200
planning bound), keeping the ASM-2374-corner mandatory campaign at $129.40
<= the UNCHANGED $155 cap (+REPLACE $139.59; REPLACE still gated on its
§R-REV4.3 NI gate + the measured (7) projection). ASM-2404/ASM-2405.

That changes frozen-record text — a SEVENTH lawful pre-final reset-refreeze
(precedents: _f1k_runhold_fix_20260715.py, _f1k_holdfix_20260716.py,
_f1k_round3fix_20260716.py, _f1k_round4fix_20260716.py,
_f1k_round5fix_20260716.py, _f1k_round6fix_20260716.py; f1k is STILL not
GNG-0-signed and results-log/f1k.jsonl STILL does not exist; no spend, no
unblind). This script resets the record to DRAFT and applies EXACTLY the
freeze-(A) completion deltas; prereg-freeze re-freezes under the full
lints. Build artifact, never part of the frozen record.

Deltas:
  1. design.n_planned.freeze_manifest.A_pre_spend rider: seed value + d0
     algorithm verbatim + generator pin + pass-accounting correction.
  2. design.n_planned.scoring_passes rider (envelope arithmetic).
  3. design.n_planned.budget_note rider (amended corner figures).
  4. design.arms_mandatory_baselines d0 entry rider (algorithm pointer).
  5. pins.harness_manifest rider (generator sha; driver worst-case
     constants amended; mock-acceptance evidence).
  6. title rider. kill_criterion_verbatim, extrapolation_envelope_verbatim,
     budget.usd_cap, analysis pin all BYTE-IDENTICAL (asserted).
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kot_common as kc

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "registry" / "experiments" / "f1k.json"
IDX = ROOT / "registry" / "frozen-index.json"
OLD_FROZEN = "974f403176216f3221b12583b70816880d357d5ae58e0f1d7d3b0642d6106987"
ANALYSIS_PIN = \
    "54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb"
GENERATOR = ROOT / "poc" / "glm52-probe" / "f1k-harness" / \
    "build_carriers.py"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a SEVENTH time (conjunctive)
gng0 = ROOT / "registry" / "gng0-signoff.json"
if gng0.exists():
    assert "f1k" not in (json.loads(gng0.read_text())
                         .get("frozen_records") or {}), "f1k GNG-0-signed"
assert not (ROOT / "results-log" / "f1k.jsonl").exists(), \
    "results-log/f1k.jsonl exists — reset-refreeze is UNLAWFUL"

gen_sha = hashlib.sha256(GENERATOR.read_bytes()).hexdigest()

# ---- reset to DRAFT (freeze re-stamps these) --------------------------------
rec["status"] = "DRAFT"
for k in ("frozen_at", "frozen_by", "frozen_sha256"):
    rec.pop(k, None)
idx = json.loads(IDX.read_text(encoding="utf-8"))
assert idx.pop("f1k", None) == OLD_FROZEN
kc.write_canonical_json(IDX, idx)

# ---- 1. A_pre_spend rider ---------------------------------------------------
np_ = rec["design"]["n_planned"]
fm = np_["freeze_manifest"]
assert "construction; pilot-panel derangement 11; d0 table 7" \
    in fm["A_pre_spend"]
fm["A_pre_spend"] += (
    " FREEZE-(A) COMPLETION (2026-07-16, bead kernel-of-truth-hh2d; the "
    "Opus runner's lawful pre-spend fail-closed stop found three unfrozen "
    "Fable-owned (A) artifacts; ASM-2404/ASM-2405): (1) the A(vii) "
    "CONSTRUCTION SEED VALUE = 20260716. The SS2.4 construction "
    "arithmetic is sampling-free (forward passes + means) and its only "
    "PRNG uses are the separately-registered d0/derangement seeds; the "
    "construction seed's registered role is DETERMINISM PROVENANCE — "
    "stamped into the (A)-time construction manifest "
    "(data/f1k-carriers-v1/generator/construction-manifest.jsonl), "
    "exported as KAE_SEED to every construction engine invocation, and "
    "carried into the B0 addendum; any construction artifact carrying a "
    "different value fails closed. (2) the d0 DIRECTION-GENERATION "
    "ALGORITHM (the mandatory placebo carrier's random directions; "
    "load-bearing via the placebo voiding gate), REGISTERED VERBATIM as "
    "kot-f1k-d0/1 at seed 7 [A(vii) 'd0 table 7']: for carrier slot c and "
    "splice-layer id l, digest_j = SHA-256(utf8('kot-f1k-d0/1|seed=7|"
    "slot=<c>|layer=<l>|blk=<j>')) for j = 0,1,2,...; each digest yields "
    "4 uniforms (consecutive 8-byte big-endian blocks / 2^64); "
    "Box-Muller, BOTH branches per uniform pair (r = sqrt(-2 ln(1-u1)); "
    "z = r cos(2 pi u2), r sin(2 pi u2)), IEEE-754 float64; the first "
    "D = 6144 normals in stream order form z; direction = z / ||z||_2; "
    "the d0 table entry at (c,l) = ||v^K_{c,l}|| * direction (the SSR2 "
    "reference-norm rule; g applies AFTER rescaling); f32 cast only at "
    "table write. Isotropic on the sphere, platform-independent, "
    "stdlib-reproducible (build_carriers.py d0_direction; the generator's "
    "`verify` step spot-reconstructs the written table from this text). "
    "(3) the CARRIER-CONSTRUCTION GENERATOR (the runnable SS2.4 "
    "software): poc/glm52-probe/f1k-harness/build_carriers.py sha256 "
    + gen_sha +
    " — subcommands manifest [(A)-time, $0: the deterministic 96x16x3 "
    "construction manifest with OP-4/SSR4-rule gated char-spans; the "
    "WITHOUT sequence SHARED between the K and d2 mean differences] -> "
    "construct [the construction spend: kot-f1k-tok/1 tokenizer contract "
    "(the pinned GLM-5.2 tokenizer wrapped at bring-up, ASM-1971), "
    "kot-f1k-dump/1 engine hidden-state dump contract (per-line SUMS of "
    "the moe()-input hidden state over gated positions per candidate "
    "splice layer — the DES SS2.8 item-3 dump mode, implemented at "
    "bring-up as a CONSTRUCTION-ONLY patch on top of the pinned gate-0 "
    "engine; every SCORING phase runs the binary built from the pinned "
    "patch alone), registered float64 mean-difference arithmetic "
    "(per-line mean = sum/gated_count; per (concept,variant,layer) "
    "sequential accumulation in context order / m; v = WITH - WITHOUT; "
    "f32 only at kaec_write), per-concept checkpointed] -> verify [$0: "
    "KAEC geometry nc=96/D=6144, the pinned analysis's carriers "
    "arithmetic params_added == C*layers*D and table_bytes == 16 + "
    "4*layers + 4*params_added, per-(c,l) norm matching within the "
    "driver rtol, seed-derangement reconstruction identity, d0 "
    "spot-reconstruction]. CONSTRUCTION PASS ACCOUNTING CORRECTED "
    "(ASM-2405): d2 is built by the same construction with substituted "
    "content (SS2.6) and therefore needs its own WITH-dictionary passes; "
    "construction = 96 x 16 x 3 = 4,608 forward passes EXACT (the prior "
    "3,072 counted K's two variants only); pilot tightened to the "
    "driver's deterministic arithmetic <= 2,112 (1,728 grid + 288 dev-96 "
    "b0/K/d0 + 96 conditional REPLACE dev pass; supersedes the ~6,200 "
    "planning bound); amended ASM-2205-corner worst case: mandatory "
    "19,964 prefills -> 462.1 h -> $129.40 <= the UNCHANGED $155 cap; "
    "+REPLACE 21,537 -> 498.5 h -> $139.59 <= $155 (REPLACE still runs "
    "ONLY under its SSR-REV4.3 NI gate + the measured (7) projection <= "
    "$155). MOCK EVIDENCE [$0]: the generator green-ran end-to-end "
    "against the mock dump engine + mock tokenizer at the FULL frozen "
    "geometry (nc=96, D=6144, 4,608 passes) and f1k_driver.py (protocol "
    "logic untouched; worst-case envelope constants amended to this "
    "correction) accepted its tables through pilot -> guard -> test -> "
    "pinned-analysis ingest, exit 0 (mock_e2e_carriers.py; regenerable "
    "mock-out/ evidence).")

# ---- 2. scoring_passes rider --------------------------------------------------
assert "+ construction <= 3072 + pilot ~6200" in np_["scoring_passes"]
np_["scoring_passes"] += (
    " FREEZE-(A) COMPLETION CORRECTION (2026-07-16, ASM-2405; latest "
    "revision governs): construction = 96x16x3 = 4608 dump passes EXACT "
    "(WITHOUT shared between K and d2; the 3072 figure under-counted "
    "d2's with-dictionary passes); pilot <= 2112 DETERMINISTIC (1728 "
    "grid + 288 dev-96 + 96 conditional REPLACE dev pass); guard <= 660 "
    "unchanged; mandatory total 19964 prefills.")

# ---- 3. budget_note rider ------------------------------------------------------
assert "22516 prefills -> 521 instance-h -> $146" in np_["budget_note"]
np_["budget_note"] += (
    " FREEZE-(A) COMPLETION (2026-07-16, ASM-2405): with the corrected "
    "construction accounting (4608 EXACT) and the deterministic pilot "
    "bound (<= 2112), the same pessimistic corner gives mandatory 19964 "
    "prefills -> 462.1 h -> $129.40 <= $155, and +REPLACE 21537 -> "
    "498.5 h -> $139.59 <= $155; the $155 cap, the SSR6 degradation "
    "order, and the REPLACE run-only-under-measured-projection rule are "
    "all UNCHANGED. The analysis's round-6 budget-honesty floors "
    "(usd_total >= $73, instance_hours >= 260.6 h, prefills >= 11011) "
    "are UNCHANGED and remain below the amended corner (the admitted "
    "better-than-corner throughput band narrows from 2.0x to ~1.77x; "
    "disclosed, analysis untouched).")

# ---- 4. d0 arm rider -----------------------------------------------------------
arms = rec["design"]["arms_mandatory_baselines"]
d0_idx = [i for i, a in enumerate(arms)
          if a.startswith("d0 norm-matched random carrier")]
assert len(d0_idx) == 1
arms[d0_idx[0]] += (
    " [FREEZE-(A) COMPLETION 2026-07-16: direction-generation algorithm "
    "registered VERBATIM as kot-f1k-d0/1 (seed 7) in "
    "design.n_planned.freeze_manifest.A_pre_spend; ASM-2404]")

# ---- 5. harness_manifest rider -------------------------------------------------
rec["pins"]["harness_manifest"] += (
    " FREEZE-(A) COMPLETION (2026-07-16): carrier-construction generator "
    "poc/glm52-probe/f1k-harness/build_carriers.py sha256 " + gen_sha +
    " (manifest/construct/verify; kot-f1k-tok/1 + kot-f1k-dump/1 "
    "contracts in its docstring; construction seed 20260716; d0 = "
    "kot-f1k-d0/1 seed 7; construction = 4608 passes EXACT). Driver "
    "worst-case envelope constants amended to the ASM-2405 accounting "
    "(WORST_PREFILLS_CONSTRUCTION 3072 -> 4608 EXACT, WORST_PREFILLS_"
    "PILOT 6200 -> 2112 deterministic; mandatory corner $129.40, "
    "+REPLACE $139.59, cap $155 unchanged; the mock self-check now "
    "asserts BOTH <= cap). Generator mock-acceptance green 2026-07-16 "
    "($0): build_carriers.py construct against the mock dump engine + "
    "mock tokenizer (mock_colibri_dump.py / mock_tokenizer.py, MOCK "
    "ONLY, unpinned) over the REAL (A)-time construction manifest at "
    "nc=96 / D=6144; its 7 arm tables passed the generator verify "
    "binds (KAEC geometry, analysis carriers arithmetic, norm matching, "
    "derangement reconstruction, d0 reconstruction) AND the driver "
    "end-to-end (mock_e2e_carriers.py: pilot validate_panel -> guard -> "
    "test -> pinned-analysis ingest exit 0, all gates true).")

# ---- 6. title rider -------------------------------------------------------------
rec["title"] += (
    " FREEZE-(A) COMPLETION REFREEZE 7 (2026-07-16, bead "
    "kernel-of-truth-hh2d; registry/corrections/f1k/"
    "1-prefreeze-correction.json amended): construction seed 20260716 + "
    "d0 kot-f1k-d0/1 algorithm registered; carrier-construction "
    "generator build_carriers.py authored + sha-pinned; construction "
    "pass accounting corrected (4608 EXACT) and pilot bound made "
    "deterministic (<= 2112) — corner $129.40/$139.59 vs the unchanged "
    "$155 cap. Geometry, power table, kill criterion, envelope, "
    "analysis pin all unchanged.")

# ---- invariants -----------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert rec["pins"]["analysis_script"]["sha256"] == ANALYSIS_PIN
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + FREEZE-(A) completion deltas applied; "
      "generator pin %s..." % gen_sha[:16])
