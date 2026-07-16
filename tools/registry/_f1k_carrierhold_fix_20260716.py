#!/usr/bin/env python3
"""One-shot CARRIER-PIPELINE HARDENING (pre-construction HOLD) fix pass
over registry/experiments/f1k.json.

The F1-K carrier-construction pipeline pre-construction review (2026-07-16)
returned HOLD: the d0 algorithm registration (kot-f1k-d0/1) and the .kaec
arithmetic were CONFIRMED sound, but the pipeline had real provenance/
determinism holes. All six are now CLOSED in the generator
poc/glm52-probe/f1k-harness/build_carriers.py + the (A)-time spec rows:

  (1) MOCK-vs-REAL CHECKPOINT CONTAMINATION (CRITICAL): checkpoints were
      accepted on seed+layer-list only, so a D=6144 MOCK checkpoint could
      silently seed a REAL construction and still report 4,608 passes.
      Now: every checkpoint + the construction report are BOUND to
      (mode=mock|real, manifest_sha256, tokenizer_sha256,
      engine_weights_sha256, dump_patch_sha256, construction_seed,
      layers); ANY field mismatch refuses fail-closed; a mode=mock
      artifact is categorically unusable in a mode=real construction;
      --mode real REQUIRES the three engine-side shas explicitly. The
      generator `selftest` PROVES the e2e refusal (subprocess, exit 2,
      no table written).
  (2) A(iv) LAYER IDS UNRESOLVED: construct accepted any ascending CLI
      list; verify compared only against a caller-supplied list. Now:
      A(iv) RESOLVED + PINNED = ALL 76 MoE layers of the pinned GLM-5.2
      config, ENGINE IDS 3..78 INCLUSIVE [MEASURED ASM-2342 R3;
      num_hidden_layers=78, first_k_dense_replace=3]; pilot realization
      L1=[40] / L2=[40,53,65,78] / L3=all [STIPULATED ASM-2406];
      construct --mode real and verify (mode=real report) fail closed on
      any other list.
  (3) MANIFEST VERIFIED BY COUNT+SEED ONLY: altered texts/spans with the
      same row count passed. Now: construct/verify re-derive the manifest
      FRESH from the (A) components, byte-for-byte line equality.
  (4) A-TIME DIGEST MISMATCH: the pinned cac24e18... digest predated the
      freeze-(A)-completion artifacts (construction-manifest.jsonl +
      generator-spec/README/manifest updates). Now: reconciled to the
      current digest covering them + the hardening spec rows — all $0
      (A)-time generator components, no realized table, no spend.
  (5) ENGINE PROVENANCE ECHO: KAE_SEED was exported but never verified.
      Now: kot-f1k-dump/1 REQUIRES the '[KAE-DUMP] armed: ... seed=' echo
      on stderr; construct verifies it per batch, fail-closed.
  (6) d0 REPRODUCIBILITY OVER-CLAIM: 'platform-independent byte-identical'
      relied on platform libm and verify checked 6 spots with tolerance.
      Now: claim RESCOPED to the pinned toolchain AND verify strengthened
      to a FULL cell-by-cell byte-exact (f32) re-derivation of the d0
      table (exact f64 reference norms recorded in norms.json).

Changing build_carriers.py changes its pinned sha256 (in harness_manifest
AND the A_pre_spend rider), and the (A)-time corpus edits change the
pinned directory digest — so this is the EIGHTH lawful pre-final
reset-refreeze (precedents: _f1k_runhold_fix_20260715.py through
_f1k_freezeA_fix_20260716.py; f1k is STILL not GNG-0-signed and
results-log/f1k.jsonl STILL does not exist). This script resets the record
to DRAFT and applies EXACTLY the deltas; prereg-freeze re-freezes under
the full lints. Build artifact, never part of the frozen record.
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
GENDIR = ROOT / "poc" / "glm52-probe" / "f1k-harness"
OLD_FROZEN = "c0d55aaf669fc9dc67f3f3c2a75d4dcb5e126e3d09c6f16192fa8bb454f7b139"
OLD_GEN_SHA = ("59bb8af035a3686c0244759633c1d62db5319dd71c05943e054"
               "cffcc6e1ce2c3")
OLD_ATIME_DIGEST = ("cac24e18c895c1903217ac9df1db7fec06385af016c1438654"
                    "419d60fd1d476b")
ANALYSIS_PIN = ("54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fc"
                "b75da9eea8eb")

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified an EIGHTH time (conjunctive)
gng0 = ROOT / "registry" / "gng0-signoff.json"
if gng0.exists():
    assert "f1k" not in (json.loads(gng0.read_text())
                         .get("frozen_records") or {}), "f1k GNG-0-signed"
assert not (ROOT / "results-log" / "f1k.jsonl").exists(), \
    "results-log/f1k.jsonl exists — reset-refreeze is UNLAWFUL"

# ---- current artifact digests (computed, never transcribed) -----------------
NEW_GEN_SHA = hashlib.sha256(
    (GENDIR / "build_carriers.py").read_bytes()).hexdigest()
assert NEW_GEN_SHA != OLD_GEN_SHA
NEW_ATIME_DIGEST = kc.corpus_hash(str(ROOT), "f1k-carriers-v1")
assert NEW_ATIME_DIGEST != OLD_ATIME_DIGEST
MAN_SHA = hashlib.sha256(
    (ROOT / "data" / "f1k-carriers-v1" / "generator" /
     "construction-manifest.jsonl").read_bytes()).hexdigest()
spec = json.loads((ROOT / "data" / "f1k-carriers-v1" / "generator" /
                   "generator-spec.json").read_text("utf-8"))
assert spec["candidate_splice_layers"].startswith("RESOLVED + PINNED")
# analysis script UNTOUCHED this round
got_ana = hashlib.sha256(
    (ROOT / "analysis" / "f1k.py").read_bytes()).hexdigest()
assert got_ana == ANALYSIS_PIN == rec["pins"]["analysis_script"]["sha256"]

# ---- reset to DRAFT (freeze re-stamps these) --------------------------------
rec["status"] = "DRAFT"
for k in ("frozen_at", "frozen_by", "frozen_sha256"):
    rec.pop(k, None)
idx = json.loads(IDX.read_text(encoding="utf-8"))
assert idx.pop("f1k", None) == OLD_FROZEN
kc.write_canonical_json(IDX, idx)

# ---- 1. harness_manifest: generator re-pin + ROUND-8 rider ------------------
hm = rec["pins"]["harness_manifest"]
assert hm.count(OLD_GEN_SHA) == 1
hm = hm.replace(OLD_GEN_SHA, NEW_GEN_SHA)
hm += (
    " CARRIER-PIPELINE HARDENING (2026-07-16, pre-construction provenance/"
    "determinism review HOLD; d0 registration + .kaec arithmetic CONFIRMED "
    "sound, untouched): build_carriers.py re-pinned at the sha above with "
    "(1) checkpoint/report PROVENANCE BINDING to (mode=mock|real, "
    "manifest_sha256, tokenizer_sha256, engine_weights_sha256, "
    "dump_patch_sha256, construction_seed, layers) — any field mismatch "
    "refuses fail-closed, a MOCK checkpoint is categorically UNUSABLE in a "
    "REAL construction, --mode real requires the three engine-side shas "
    "explicitly; (2) A(iv) ENFORCED — real-mode construct/verify refuse "
    "any layer list != the registered 76 MoE layers 3..78 [ASM-2342/"
    "ASM-2406]; (3) manifest CONTENT verified against a fresh (A)-spec "
    "re-derivation byte-for-byte (count+seed never sufficient); (4) the "
    "kot-f1k-dump/1 contract now REQUIRES the engine's '[KAE-DUMP] armed: "
    "... seed=<KAE_SEED>' stderr echo, captured + verified per dump batch; "
    "(5) verify re-derives the ENTIRE d0 table cell-by-cell with exact f32 "
    "equality on the pinned toolchain (exact f64 reference norms in "
    "norms.json), superseding the 6-spot rtol check, and the d0 claim is "
    "honestly scoped to the pinned toolchain (libm dependence disclosed). "
    "SELFTEST green 2026-07-16 ($0): 6/6 fail-closed probes — the "
    "mock-checkpoint-rejected-in-REAL-construction e2e refusal (exit 2, no "
    "table written), non-A(iv) layer list rejected in real mode, "
    "content-tampered manifest (same count+seed) rejected + positive "
    "control, engine echo seed-mismatch and echo-absent both rejected. "
    "Mock-acceptance RE-RUN green 2026-07-16 ($0): construct --mode mock "
    "at nc=96/D=6144 over the REAL (A)-time construction manifest "
    "(4,608 passes), all generator verify checks PASS incl. the FULL d0 "
    "byte-exact re-derivation and the binding/echo checks, and the "
    "untouched f1k_driver.py accepted the tables end-to-end "
    "(mock_e2e_carriers.py: pilot -> guard -> test -> pinned-analysis "
    "ingest exit 0, all gates true).")
rec["pins"]["harness_manifest"] = hm

# ---- 2. A_pre_spend: generator re-pin + d0 scope + hardening rider ----------
np_ = rec["design"]["n_planned"]
fm = np_["freeze_manifest"]
a = fm["A_pre_spend"]
assert a.count(OLD_GEN_SHA) == 1
a = a.replace(OLD_GEN_SHA, NEW_GEN_SHA)
old_scope = ("Isotropic on the sphere, platform-independent, "
             "stdlib-reproducible (build_carriers.py d0_direction; the "
             "generator's `verify` step spot-reconstructs the written "
             "table from this text).")
new_scope = ("Isotropic on the sphere, stdlib-implemented "
             "(build_carriers.py d0_direction). REPRODUCIBILITY SCOPE "
             "(carrier-pipeline hardening 2026-07-16; supersedes this "
             "rider's earlier 'platform-independent ... spot-reconstructs' "
             "phrasing, an over-claim): the SHA-256 stream/uniforms are "
             "platform-independent, but the Box-Muller transcendentals "
             "delegate to platform libm, so byte-identical reproduction is "
             "claimed ONLY ON THE PINNED TOOLCHAIN — the generator's "
             "`verify` step re-derives the ENTIRE written d0 table "
             "cell-by-cell from this text and requires exact f32 equality "
             "(exact f64 reference norms recorded in norms.json "
             "k_reference_norm_f64_hex); cross-platform agreement is "
             "expected to ~1 ulp per transcendental but NOT claimed "
             "byte-exact.")
assert a.count(old_scope) == 1
a = a.replace(old_scope, new_scope)
a += (
    " CARRIER-PIPELINE HARDENING (2026-07-16, pre-construction provenance/"
    "determinism review HOLD; bead kernel-of-truth-r03p; ASM-2406; latest "
    "revision governs on conflict): (1) A(iv) RESOLVED + PINNED — the "
    "exact candidate splice-layer set = ALL 76 MoE layers of the pinned "
    "GLM-5.2 config at ENGINE LAYER IDS 3..78 INCLUSIVE "
    "(num_hidden_layers=78, first_k_dense_replace=3; the committed "
    "routing-stats files span MoE layers 3-78 = 76 layers [MEASURED "
    "ASM-2342 R3]; DES SS2.3 L3 = ALL MoE layers forces the union "
    "regardless of L1/L2); pilot-grid realization L1=[40] (the DES's own "
    "'~ layer 40' mid-stack), L2=[40,53,65,78] (round(linspace(40,78,4)), "
    "mid-to-late), L3 = all 76 [STIPULATED]; ENFORCED fail-closed by "
    "build_carriers.py REGISTERED_SPLICE_LAYERS — `construct --mode real` "
    "and `verify` (on a mode=real report) REFUSE any other list. "
    "(2) CHECKPOINT PROVENANCE BINDING — every per-concept construction "
    "checkpoint and the construction report are BOUND to (mode=mock|real, "
    "manifest_sha256, tokenizer_sha256, engine_weights_sha256, "
    "dump_patch_sha256, construction_seed, layers); `construct` REFUSES "
    "fail-closed any checkpoint whose binding differs in ANY field; a "
    "mode=mock checkpoint is categorically UNUSABLE in a mode=real "
    "construction (generator `selftest` proves the refusal end-to-end: "
    "subprocess, exit 2, no table written); --mode real REQUIRES the "
    "pinned tokenizer-artifact sha, the pinned engine+weights sha, and "
    "the bring-up kot-f1k-dump/1 patch sha as explicit inputs. "
    "(3) MANIFEST CONTENT VERIFICATION — `construct` and `verify` "
    "re-derive the construction manifest FRESH from the (A) generator "
    "components and require byte-for-byte line equality (row count + "
    "seed alone are NEVER accepted; altered texts/spans reject). "
    "(4) ENGINE PROVENANCE ECHO — the kot-f1k-dump/1 contract now "
    "REQUIRES the engine to echo '[KAE-DUMP] armed: ... seed=<KAE_SEED>' "
    "on stderr; `construct` captures stderr and verifies the echoed seed "
    "== the registered 20260716 for EVERY dump batch, failing closed on "
    "absence or mismatch; the verified echo is recorded in every "
    "checkpoint and summarized in construction-report.json. "
    "(5) the (A)-time carrier-input directory digest RECONCILED (see "
    "pins.corpus_hashes[f1k-carriers-v1]): the earlier " + OLD_ATIME_DIGEST
    + " covered the pre-freeze-(A)-completion tree; the reconciled digest "
    + NEW_ATIME_DIGEST + " additionally covers the (A)-time "
    "construction-manifest.jsonl (4,608 rows, sha256 " + MAN_SHA + ") and "
    "the freeze-(A)-completion + hardening generator-spec/README/manifest "
    "rows — ALL $0 (A)-time generator components; no realized table, no "
    "spend, no model contact. Construction pass accounting (4,608 EXACT), "
    "pilot bound (<= 2,112), corner economics ($129.40 mandatory / "
    "$139.59 +REPLACE vs the UNCHANGED $155 cap), geometry, power table, "
    "kill criterion, envelope ALL UNCHANGED by this pass.")
fm["A_pre_spend"] = a

# ---- 3. corpus pin text: reconciled (A)-time digest -------------------------
ch = rec["pins"]["corpus_hashes"]
val = ch["f1k-carriers-v1"]
assert val.count(OLD_ATIME_DIGEST) == 1
val = val.replace(
    "are COMMITTED NOW at directory digest " + OLD_ATIME_DIGEST
    + " (ASM-2377)",
    "are COMMITTED NOW at directory digest " + NEW_ATIME_DIGEST
    + " (ASM-2377 as RECONCILED at the carrier-pipeline hardening "
    "refreeze 2026-07-16 [ASM-2406]: the superseded digest "
    + OLD_ATIME_DIGEST + " predated the freeze-(A) completion; the "
    "reconciled digest additionally covers the (A)-time "
    "construction-manifest.jsonl [4,608 rows, sha256 " + MAN_SHA + "] and "
    "the freeze-(A)-completion + carrier-HOLD hardening "
    "generator-spec/README/manifest rows incl. the A(iv) layer-id "
    "resolution — all $0 (A)-time generator components, no realized "
    "table, no spend)")
ch["f1k-carriers-v1"] = val

# ---- 4. title rider ----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 8 (2026-07-16, carrier-pipeline pre-construction "
    "provenance/determinism review; "
    "registry/corrections/f1k/1-prefreeze-correction.json amended): "
    "mode-bound checkpoints (mock-in-real contamination closed, "
    "selftest-proven), A(iv) splice layers RESOLVED (76 MoE layers 3..78) "
    "+ enforced, manifest fresh-derivation verification, engine KAE_SEED "
    "echo verified, d0 claim rescoped to the pinned toolchain with FULL "
    "byte-exact verify re-derivation, (A)-time digest reconciled. "
    "Geometry, power table, budget cap, kill criterion, envelope all "
    "unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]
assert rec["pins"]["analysis_script"]["sha256"] == ANALYSIS_PIN
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + carrier-pipeline hardening deltas "
      "applied;\n  generator sha %s -> %s\n  (A)-time digest %s -> %s"
      % (OLD_GEN_SHA[:12], NEW_GEN_SHA[:12],
         OLD_ATIME_DIGEST[:12], NEW_ATIME_DIGEST[:12]))
