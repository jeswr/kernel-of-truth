#!/usr/bin/env python3
"""One-shot CARRIER RE-REVIEW residual-hole fix pass over
registry/experiments/f1k.json (2026-07-16, NINTH lawful pre-final
reset-refreeze).

The F1-K carrier re-review (2026-07-16) CONFIRMED the round-8 critical
fixes (mock/real checkpoint binding, manifest re-derivation, d0 full
re-derivation, A-time digest) but returned HOLD on three residual
provenance holes + one stale doc. All are now CLOSED in the generator
poc/glm52-probe/f1k-harness/build_carriers.py + the (unpinned) run driver
f1k_driver.py + the harness README:

  (2) VERIFY WAS MODE-BLIND: `verify` enforced the A(iv) layer set only
      when the report itself claimed mode=real, and --expect-mode was
      OPTIONAL — so a plain `verify` PASSED D=6144 mock carriers with 8
      non-pinned layers [1,2,3,5,7,8,9,11]. Now: --expect-mode is
      REQUIRED (argparse + an in-band fail-closed check for programmatic
      callers), the binding mode must EQUAL it, and any report claiming
      OR expected real is UNCONDITIONALLY held to the registered A(iv)
      union 3..78.
  (5) CACHED-RESUME ECHO BYPASS: a cached per-concept checkpoint
      incremented echo_verified and accepted the stored echo VERBATIM,
      so a binding-matching checkpoint with no echo (or seed=999) was
      accepted on resume. Now: on cached resume the stored engine_echo
      is RE-PARSED and its seed re-verified == the registered 20260716
      (the SAME check a fresh batch gets); missing/unparseable/
      mismatched => reject. ADDITIONALLY the cached content (D == 6144,
      n_passes == 48, v_k/v_d2 shape + finiteness) is schema/integrity-
      checked, never consumed verbatim.
  (8) DRIVER<->ANALYSIS SEAM DID NOT GATE THE CONSTRUCTION: the driver
      checked only the carrier-dir digest + path containment, never the
      construction-report mode / D / layers / bindings — so mock D=6144
      carriers with wrong layers were accepted END-TO-END with all gates
      true. Now (driver [R9-PROV], the pinned analysis/f1k.py BYTE-
      IDENTICAL at its pin): before ingesting carriers for a REAL
      campaign the driver verifies construction-report mode == real,
      D == 6144, nc == 96, layers == the registered 3..78, seed ==
      20260716, binding.manifest_sha256 == the COMMITTED (A)-time
      manifest re-derived fresh, the echo summary re-parsed, the three
      engine-side provenance shas DERIVED from the actual artifacts
      named by config.carrier_provenance and compared (never accepted as
      caller assertions of mere 64-hex syntax — the generator's
      `construct --mode real` now equally requires --*-artifact paths
      and derives+compares), and every configured table byte-witnessed
      against the report (sha256 + size + KAEC header geometry + exact
      fp32 size arithmetic); the disclosure lands in
      carrier-provenance.json and the typed pins_observed witness map
      rides the kot-log/1 run record (the sidecar schema is CLOSED
      default-deny, so the RECORD — which verdict-gen re-verifies and
      the pinned analysis schema-validates — is the lawful witness
      channel for mode+bindings).
  (doc) poc/glm52-probe/f1k-harness/README.md rewritten from the
      superseded n=1440/$149/C>=65 protocol to the current REVISION-6 +
      freeze-(A)-completion figures: n=1573 / C=96 EQUALITY gate /
      $129.40 mandatory ($139.59 +REPLACE) vs the $155 cap / layers
      3..78 / construction 4,608 EXACT / pilot <= 2,112.

Changing build_carriers.py changes its pinned sha256 (harness_manifest AND
the A_pre_spend rider) — so this is the NINTH lawful pre-final
reset-refreeze (precedents: _f1k_runhold_fix_20260715.py through
_f1k_carrierhold_fix_20260716.py; f1k is STILL not GNG-0-signed and
results-log/f1k.jsonl STILL does not exist). The (A)-time carrier-input
directory digest is UNCHANGED this pass (no data/f1k-carriers-v1 edit).
This script resets the record to DRAFT and applies EXACTLY the deltas;
prereg-freeze re-freezes under the full lints. Build artifact, never part
of the frozen record.
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
OLD_FROZEN = "064c9a906b7d40c23ed7f6c2e410f268990d4037e6fe15d5a63fccef1f1acbac"
OLD_GEN_SHA = ("c4b6f2089857b22416f9c110bd72378267d3886c4195ed178a771ca4"
               "3bb38c47")
ANALYSIS_PIN = ("54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fc"
                "b75da9eea8eb")

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a NINTH time (conjunctive)
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
# (A)-time digest UNCHANGED this pass — no data/f1k-carriers-v1 edit
ATIME_DIGEST = kc.corpus_hash(str(ROOT), "f1k-carriers-v1")
assert ATIME_DIGEST in rec["pins"]["corpus_hashes"]["f1k-carriers-v1"], \
    "(A)-time digest drifted — this pass must not touch the corpus"
# analysis script UNTOUCHED this round (asserted byte-identical)
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

# ---- 1. harness_manifest: generator re-pin + ROUND-9 rider ------------------
hm = rec["pins"]["harness_manifest"]
assert hm.count(OLD_GEN_SHA) == 1
hm = hm.replace(OLD_GEN_SHA, NEW_GEN_SHA)
hm += (
    " CARRIER RE-REVIEW RESIDUAL-HOLE CLOSURE (2026-07-16, ninth lawful "
    "pass; round-8 critical fixes CONFIRMED by the re-review, untouched): "
    "build_carriers.py re-pinned at the sha above with (2) `verify` "
    "--expect-mode REQUIRED (never mode-blind; binding mode must EQUAL "
    "it; a report claiming OR expected real is UNCONDITIONALLY held to "
    "the registered A(iv) union 3..78 — a D=6144 mock table set with 8 "
    "non-pinned layers can no longer pass any verify a real consumer "
    "relies on); (5) CACHED-RESUME checkpoints re-verified like fresh "
    "batches — the stored engine_echo is RE-PARSED and its seed "
    "re-verified == the registered 20260716, and the cached content "
    "(D == 6144, n_passes == 48, v_k/v_d2 shape + finiteness) is "
    "schema/integrity-checked, never consumed verbatim; (8) REAL "
    "provenance shas DERIVED from the actual artifacts — `construct "
    "--mode real` now REQUIRES --tokenizer-artifact/--engine-weights-"
    "artifact/--dump-patch-artifact and each asserted --*-sha must EQUAL "
    "the artifact's derived digest (64-hex syntax alone never accepted). "
    "The RUN DRIVER (f1k_driver.py, not sha-pinned here) gained the "
    "matching [R9-PROV] carrier-construction provenance gate: before "
    "ingesting carriers for a REAL campaign it verifies construction-"
    "report mode == real, D == 6144, nc == 96, layers == 3..78, seed == "
    "20260716, the binding's manifest sha against a fresh re-hash of the "
    "COMMITTED (A)-time manifest, artifact-DERIVED provenance shas via "
    "config.carrier_provenance, and byte-witnesses every configured "
    "table against the report (sha256 + size + KAEC header + exact fp32 "
    "arithmetic), failing closed ERR_F1K_CARRIERPROV on any mismatch; "
    "the disclosure is written to carrier-provenance.json and the typed "
    "pins_observed witness map rides the kot-log/1 run record (the "
    "sidecar schema is CLOSED default-deny — the record, re-verified by "
    "verdict-gen and schema-validated by the PINNED analysis, is the "
    "lawful witness channel; analysis/f1k.py BYTE-IDENTICAL at its pin "
    "this pass). SELFTEST green 2026-07-16 ($0): 11/11 fail-closed "
    "probes (the 6 round-8 probes + asserted-sha != derived-artifact "
    "rejected, cached-resume echo seed=999 rejected, cached-resume echo "
    "ABSENT rejected, cached content D=8 rejected, mode-blind verify "
    "refused). Mock-acceptance RE-RUN green 2026-07-16 ($0): construct "
    "--mode mock resumed from all 96 round-8 checkpoints (every cached "
    "echo re-parsed + content-checked), generator verify 52/52 PASS "
    "incl. the FULL d0 byte-exact re-derivation; verify --expect-mode "
    "real on the same mock set FAILS CLOSED (exit 2); driver --mock "
    "green end-to-end incl. the [R9-PROV] probe battery (no-report / "
    "mode=mock / wrong-layers / wrong-D / underived-sha / byte-tampered-"
    "table each REFUSED for real ingest; a VALID real-mode fixture "
    "PASSES; pins_observed accepted through the OFFICIAL log-append -> "
    "verdict-gen -> pinned-analysis seam); mock_e2e_carriers.py "
    "DRIVER-ACCEPTANCE PASS with the SAME mock D=6144 tables REFUSED by "
    "the REAL-mode gate. Harness README rewritten from the superseded "
    "n=1440/$149 runbook to the REVISION-6 n=1573 / C=96 / $129.40-vs-"
    "$155 / layers-3..78 protocol. Geometry, power table, budget cap, "
    "kill criterion, envelope ALL UNCHANGED by this pass.")
rec["pins"]["harness_manifest"] = hm

# ---- 2. A_pre_spend: generator re-pin + round-9 rider -----------------------
np_ = rec["design"]["n_planned"]
fm = np_["freeze_manifest"]
a = fm["A_pre_spend"]
assert a.count(OLD_GEN_SHA) == 1
a = a.replace(OLD_GEN_SHA, NEW_GEN_SHA)
a += (
    " CARRIER RE-REVIEW RESIDUAL-HOLE CLOSURE (2026-07-16, ninth lawful "
    "pass; latest revision governs on conflict): (i) the generator's "
    "`verify` is never mode-blind — --expect-mode REQUIRED, binding mode "
    "must equal it, and a report claiming OR expected real is "
    "UNCONDITIONALLY held to the A(iv) union 3..78; (ii) cached-resume "
    "checkpoints are held to the SAME kot-f1k-dump/1 echo requirement as "
    "fresh batches (stored echo re-parsed, seed re-verified == 20260716) "
    "and their content (D == 6144, n_passes == 48, v_k/v_d2 shape + "
    "finiteness) is integrity-checked, never consumed verbatim; (iii) "
    "REAL construction provenance shas are DERIVED from the actual "
    "artifacts (--tokenizer-artifact/--engine-weights-artifact/"
    "--dump-patch-artifact REQUIRED with --mode real; asserted pin must "
    "equal the derived digest); (iv) the RUN DRIVER enforces the "
    "[R9-PROV] carrier-construction provenance gate at REAL ingest "
    "(construction-report mode/D=6144/nc=96/layers 3..78/seed 20260716/"
    "fresh manifest re-hash/artifact-derived shas/per-table byte "
    "witness, fail-closed ERR_F1K_CARRIERPROV) and witnesses "
    "mode+bindings on the kot-log/1 run record via the typed "
    "pins_observed map. The pinned analysis, all seeds, the pass "
    "accounting (4,608 EXACT construction / <= 2,112 pilot), corner "
    "economics ($129.40 mandatory / $139.59 +REPLACE vs the UNCHANGED "
    "$155 cap), geometry, power table, kill criterion and envelope are "
    "ALL UNCHANGED by this pass; the (A)-time carrier-input directory "
    "digest is UNCHANGED (no data/f1k-carriers-v1 edit).")
fm["A_pre_spend"] = a

# ---- 3. title rider ----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 9 (2026-07-16, carrier re-review residual-hole "
    "closure; registry/corrections/f1k/1-prefreeze-correction.json "
    "amended): mode-blind verify banned (--expect-mode REQUIRED + "
    "unconditional A(iv) for real), cached-resume engine-echo "
    "re-verification + cached-content integrity, artifact-DERIVED real "
    "provenance shas, and the driver-side [R9-PROV] construction-report "
    "ingest gate (mode/D/layers/bindings verified fail-closed; witness "
    "pins on the run record); harness README updated to the n=1573/C=96/"
    "$129.40-vs-$155/layers-3..78 protocol. Analysis pin, geometry, "
    "power table, budget cap, kill criterion, envelope all unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]
assert rec["pins"]["analysis_script"]["sha256"] == ANALYSIS_PIN
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + carrier re-review residual-hole deltas "
      "applied;\n  generator sha %s -> %s\n  (A)-time digest UNCHANGED %s"
      % (OLD_GEN_SHA[:12], NEW_GEN_SHA[:12], ATIME_DIGEST[:12]))
