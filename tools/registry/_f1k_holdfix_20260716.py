#!/usr/bin/env python3
"""One-shot GPT-5.6 pre-run HOLD fix pass over registry/experiments/f1k.json.

The GPT-5.6 F1-K pre-run review-gate (post reset-refreeze, 2026-07-16)
returned HOLD on the refrozen record (frozen_sha256 77e7a6a8...). Blocker 1
(CRITICAL) required editing the pinned analysis/f1k.py (strict-JSON-boolean
sidecar validity + guard-completeness fail-closed hardening), which changes
its sha256 — and the frozen record pins that sha, so this is a second lawful
pre-final reset-refreeze (precedent: _f1k_runhold_fix_20260715.py; f1k is
STILL not GNG-0-signed and results-log/f1k.jsonl STILL does not exist).
This script resets the record to DRAFT and applies EXACTLY the HOLD-mandated
deltas; prereg-freeze re-freezes under the full lints. Build artifact, never
part of the frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the strict-bool/guard-completeness
     analysis/f1k.py (HOLD blocker-1 fix: JSON-STRING "false" truthiness
     spurious-PASS channel CLOSED; guard.n_items must equal the registered
     60; output_fields UNCHANGED, 50 pointers byte-identical).
  2. pins.harness_manifest selftest description updated to the HOLD
     strict-bool revision (9/9 hardened rejections + 14/14 strict-bool /
     guard-completeness gate probes).
  3. n_planned.statistics rider: sidecar validity flags are STRICT JSON
     booleans; guard cardinality gate.
  4. title rider. kill_criterion_verbatim and
     extrapolation_envelope_verbatim BYTE-IDENTICAL (asserted).
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
OLD_FROZEN = "77e7a6a865030197e231bbfff90960ef46060957f0ac9dbcc3f89f021d8a8278"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified (conjunctive conditions)
gng0 = ROOT / "registry" / "gng0-signoff.json"
if gng0.exists():
    assert "f1k" not in (json.loads(gng0.read_text())
                         .get("frozen_records") or {}), "f1k GNG-0-signed"
assert not (ROOT / "results-log" / "f1k.jsonl").exists(), \
    "results-log/f1k.jsonl exists — reset-refreeze is UNLAWFUL"

# ---- reset to DRAFT (freeze re-stamps these) --------------------------------
rec["status"] = "DRAFT"
for k in ("frozen_at", "frozen_by", "frozen_sha256"):
    rec.pop(k, None)
idx = json.loads(IDX.read_text(encoding="utf-8"))
assert idx.pop("f1k", None) == OLD_FROZEN
kc.write_canonical_json(IDX, idx)

# ---- 1. analysis pin ---------------------------------------------------------
new_sha = hashlib.sha256(
    (ROOT / "analysis" / "f1k.py").read_bytes()).hexdigest()
old_pin = rec["pins"]["analysis_script"]["sha256"]
assert old_pin == ("3478a6c020b421cc65cdb5fffee1e2ae"
                   "60049c700cd705fba1e3435a4f63fe80"), old_pin
rec["pins"]["analysis_script"]["sha256"] = new_sha
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

# ---- 2. harness_manifest selftest description --------------------------------
hm = rec["pins"]["harness_manifest"]
old_seg = ("Mock self-test green 2026-07-15 (RUN-HOLD-fix revision): "
           "`python3 analysis/f1k.py --selftest` at the EXACT C=96/n=1573 "
           "geometry")
new_seg = ("Mock self-test green 2026-07-16 (HOLD strict-bool revision): "
           "`python3 analysis/f1k.py --selftest` at the EXACT C=96/n=1573 "
           "geometry")
assert old_seg in hm
hm = hm.replace(old_seg, new_seg)
old_rej = ("8/8 hardened rejections fail-closed: n != 1573,")
new_rej = ("9/9 hardened rejections + 14/14 STRICT-BOOL/guard-completeness "
           "gate probes fail-closed (GPT-5.6 pre-run HOLD blocker-1 fix "
           "2026-07-16: string/int/null sidecar attestations — incl. the "
           "reproduced JSON-STRING \"false\" spurious-PASS channel — are "
           "REJECTED at their gates, never truthy-PASS; guard.n_items must "
           "equal the registered 60, 0/mismatch/missing = "
           "INCOMPLETE/INSTRUMENT-INVALID; a string replace.ran is a shape "
           "defect ERR_P2_ANALYSIS; the all-true fixture still PASSES): "
           "n != 1573,")
assert old_rej in hm
hm = hm.replace(old_rej, new_rej)
rec["pins"]["harness_manifest"] = hm

# ---- 3. statistics rider ------------------------------------------------------
np_ = rec["design"]["n_planned"]
np_["statistics"] += (
    " HOLD FIX (2026-07-16, GPT-5.6 pre-run review-gate, blocker 1): every "
    "sidecar VALIDITY FLAG (manifest commits, guard byte-identity, template "
    "checks, dose attestations, replace.ran) is validated as a STRICT JSON "
    "boolean — Python truthiness previously admitted the JSON STRING "
    "'false' as a passing attestation (guard.byte_identical='false' "
    "reproducibly reached an official PASS); a non-bool or false flag now "
    "fails its gate CLOSED (INSTRUMENT-INVALID, never truthy-PASS). AND "
    "guard COMPLETENESS: /gates/off_concept_guard_valid additionally "
    "requires guard.n_items == 60 (the registered off-concept guard "
    "cardinality) — previously ignored, so byte_identical=true over 0 "
    "items gated valid; 0 or any mismatch now resolves "
    "INCOMPLETE/INSTRUMENT-INVALID, never PASS. Selftest carries 14 "
    "strict-bool/guard-completeness gate probes + the string-replace.ran "
    "rejection.")

# ---- 4. title rider -----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 2 (2026-07-16, GPT-5.6 pre-run review-gate; "
    "registry/corrections/f1k/1-prefreeze-correction.json amended): "
    "sidecar validity flags STRICT JSON booleans (string-'false' "
    "spurious-PASS channel closed, reproduced+regression-probed) + guard "
    "cardinality gate (n_items == 60). Geometry, power table, budget, kill "
    "criterion, envelope all unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + HOLD strict-bool deltas applied; "
      "analysis sha %s -> %s" % (old_pin[:12], new_sha[:12]))
