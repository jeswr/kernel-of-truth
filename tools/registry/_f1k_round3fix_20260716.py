#!/usr/bin/env python3
"""One-shot GPT-5.6 pre-run HOLD ROUND-3 fix pass over registry/experiments/f1k.json.

The round-2 re-review (2026-07-16) returned HOLD again: the strict-bool fix
was CONFIRMED real but INCOMPLETE (replace.ran fail-opened on a missing
block/key into a "valid defer"; deleted power/cost/carriers blocks were
copied to the output unvalidated and PASSed), and the official
driver-record -> verdict-gen -> analysis ingestion seam was structurally
impossible (the driver emitted artifacts as a DICT, not the kot-log/1
array). The fix edits the pinned analysis/f1k.py (DEFAULT-DENY sidecar
schema + the kot-log/1 artifacts-ARRAY rows+sidecar input contract), which
changes its sha256 — and the frozen record pins that sha, so this is a
THIRD lawful pre-final reset-refreeze (precedents:
_f1k_runhold_fix_20260715.py, _f1k_holdfix_20260716.py; f1k is STILL not
GNG-0-signed and results-log/f1k.jsonl STILL does not exist). This script
resets the record to DRAFT and applies EXACTLY the round-3 deltas;
prereg-freeze re-freezes under the full lints. Build artifact, never part
of the frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the default-deny analysis/f1k.py
     (round-3 fix: mandatory-block whitelist validated fail-closed before
     any statistic; replace.ran presence + strict bool; power pinned
     EXACTLY to the ASM-2371 marginals + non-empty ASM-2376 intersection
     block; cost numeric within the $155 ASM-2374 ceiling; carriers at the
     frozen C=96; kot-log/1 artifacts-ARRAY rows+sidecar input contract;
     output_fields UNCHANGED, 50 pointers byte-identical).
  2. pins.harness_manifest: analysis-invocation seam sentence updated to
     the kot-log/1 D10-paired rows+sidecar artifacts-ARRAY convention;
     selftest description updated to the round-3 default-deny revision.
  3. n_planned.statistics rider: default-deny sidecar schema.
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
OLD_FROZEN = "45e316e9925263e323090429e9d5f830dd5df71e1b5e68c19ffd57442b084235"

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
assert old_pin == ("e80c4190cd599ff8d003c2453fab8a6e"
                   "dc7dcc1029e796fe71d31c4acf8bf4e6"), old_pin
rec["pins"]["analysis_script"]["sha256"] = new_sha
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

# ---- 2. harness_manifest: seam sentence + selftest description ----------------
hm = rec["pins"]["harness_manifest"]
old_seam = ("Analysis invocation: verdict-gen pipes eligible results-log "
            "records to analysis/f1k.py on STDIN; records pin rows+sidecar "
            "artifacts (path+sha256), re-verified fail-closed.")
new_seam = ("Analysis invocation (HOLD round-3 seam fix, 2026-07-16): the "
            "run record is a kot-log/1 line whose artifacts ARRAY carries "
            "EXACTLY ONE {path, sha256, role:'rows'} entry (per-item rows "
            "JSONL) and EXACTLY ONE {path, sha256, role:'sidecar'} entry "
            "(run sidecar) — the D10-PAIRED convention: verdict-gen "
            "re-verifies BOTH pins fail-closed at consumption time and "
            "pipes the RECORD LINE (never a bare rows expansion, which "
            "would strand the sidecar) to analysis/f1k.py on STDIN; the "
            "analysis re-verifies both sha256 pins again before reading a "
            "byte (two independent enforcements). The pre-round-3 "
            "artifacts-as-DICT form never conformed to kot-log/1 (the "
            "official driver-record -> verdict-gen -> analysis round-trip "
            "was structurally impossible) and is REJECTED by the pinned "
            "analysis.")
assert old_seam in hm
hm = hm.replace(old_seam, new_seam)
old_seg = ("Mock self-test green 2026-07-16 (HOLD strict-bool revision): "
           "`python3 analysis/f1k.py --selftest` at the EXACT C=96/n=1573 "
           "geometry")
new_seg = ("Mock self-test green 2026-07-16 (HOLD round-3 default-deny "
           "revision): `python3 analysis/f1k.py --selftest` at the EXACT "
           "C=96/n=1573 geometry")
assert old_seg in hm
hm = hm.replace(old_seg, new_seg)
old_rej = ("9/9 hardened rejections + 14/14 STRICT-BOOL/guard-completeness "
           "gate probes fail-closed")
new_rej = ("9/9 hardened rejections + 13/13 STRICT-BOOL/guard-completeness "
           "gate probes + an 83-probe DEFAULT-DENY structural sweep (every "
           "mandatory sidecar block x missing/null/int/string, every "
           "mandatory field missing, unknown top-level key, replace.ran + "
           "inference null/int/string, power pinned EXACTLY to the "
           "ASM-2371 marginals with a non-empty ASM-2376 intersection "
           "block, cost numeric within the $155 ASM-2374 ceiling, carriers "
           "at the frozen C=96 — each ERR_P2_ANALYSIS) + 47 value-level "
           "gate probes + kot-log/1 artifacts-ARRAY round-trip (superseded "
           "dict form and rows-only record REJECTED) fail-closed")
assert old_rej in hm
hm = hm.replace(old_rej, new_rej)
rec["pins"]["harness_manifest"] = hm

# ---- 3. statistics rider ------------------------------------------------------
np_ = rec["design"]["n_planned"]
np_["statistics"] += (
    " HOLD ROUND-3 FIX (2026-07-16, GPT-5.6 pre-run review-gate round-2 "
    "re-review): the strict-bool fix was confirmed but INCOMPLETE — "
    "analysis-time validation now applies a single DEFAULT-DENY principle: "
    "the verdict can be PASS only if EVERY mandatory sidecar block "
    "{manifest, guard, template, dose, inference, replace, carriers, "
    "power, cost} AND every mandatory field is PRESENT and STRICT-valid, "
    "enforced by a closed whitelist BEFORE any gate or statistic runs. "
    "Previously replace.ran fail-opened on a missing replace block/key "
    "(.get('ran', False) read absence as a valid defer => PASS) and "
    "deleted power/cost/carriers blocks were copied to the output "
    "unvalidated (=> PASS with null disclosures). Now: missing/null/"
    "wrong-type blocks or fields, unknown top-level keys, a non-bool "
    "replace.ran, power marginals deviating from the registered ASM-2371 "
    "table (0.8043/0.8058/0.8001 EXACT) or an empty ASM-2376 intersection "
    "block, a non-numeric or above-ceiling ($155, ASM-2374) cost, or "
    "off-geometry carriers are ALL rejected fail-closed ERR_P2_ANALYSIS "
    "(no verdict producible); present-but-false/non-bool attestation "
    "values keep failing their gates CLOSED (INSTRUMENT-INVALID). INPUT "
    "SEAM: eligible records are kot-log/1 lines carrying the D10-paired "
    "artifacts ARRAY (exactly one role:'rows' + one role:'sidecar' entry); "
    "the superseded artifacts-dict form is rejected.")

# ---- 4. title rider -----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 3 (2026-07-16, GPT-5.6 pre-run review-gate round-2 "
    "re-review; registry/corrections/f1k/1-prefreeze-correction.json "
    "amended): DEFAULT-DENY sidecar schema (mandatory-block whitelist; "
    "replace.ran defer requires the block present with a strict-bool "
    "false; power/cost/carriers pinned to registered values) + the "
    "official kot-log/1 D10-paired rows+sidecar ingestion seam "
    "(artifacts ARRAY; driver-record -> verdict-gen -> analysis round-trip "
    "now real and tested). Geometry, power table, budget, kill criterion, "
    "envelope all unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + HOLD round-3 default-deny deltas applied; "
      "analysis sha %s -> %s" % (old_pin[:12], new_sha[:12]))
