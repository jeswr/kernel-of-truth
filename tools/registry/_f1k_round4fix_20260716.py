#!/usr/bin/env python3
"""One-shot GPT-5.6 pre-run HOLD ROUND-4 fix pass over registry/experiments/f1k.json.

The round-3 re-review (2026-07-16) returned HOLD a fourth time: each prior
round validated ONE level and the next re-review found the NEXT level
unvalidated (round 1 geometry; round 2 top-level truthiness + guard; round 3
top-level default-deny; round 3b NESTED sidecar interiors + the ROW schema +
missing paired-sidecar tests). The round-4 fix STOPS patching levels and
adopts a COMPLETE DECLARATIVE SCHEMA — kot-f1k-record/1 — for the ENTIRE
f1k run record, validated RECURSIVELY in analysis/f1k.py, default-deny
(unknown keys rejected + required fields enforced at EVERY depth, a
type/registered-pin/bound on every leaf). That edit changes the pinned
analysis sha256 — and the frozen record pins that sha — so this is a FOURTH
lawful pre-final reset-refreeze (precedents: _f1k_runhold_fix_20260715.py,
_f1k_holdfix_20260716.py, _f1k_round3fix_20260716.py; f1k is STILL not
GNG-0-signed and results-log/f1k.jsonl STILL does not exist). This script
resets the record to DRAFT and applies EXACTLY the round-4 deltas;
prereg-freeze re-freezes under the full lints. Build artifact, never part
of the frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the kot-f1k-record/1 analysis/f1k.py
     (full-depth declarative schema: replace ALL-sub-fields + run/defer
     coherence; the FULL mc_exact_power interior pinned; mc_intersection ==
     the registered ASM-2376 content EXACTLY; cost fully typed + ledger-
     coherent; carriers at the exact C*layers*D / KAEC-size expectation;
     the CLOSED row schema with strict-int pass; RECORD_SCHEMA over the
     kot-log/1 line incl. declared-vs-actual rows-count coherence;
     output_fields UNCHANGED, 50 pointers byte-identical).
  2. pins.harness_manifest: selftest description updated to the round-4
     full-depth revision (counts + the schema-derived sweep).
  3. n_planned.statistics rider: the kot-f1k-record/1 full-record schema.
  4. title rider. kill_criterion_verbatim and
     extrapolation_envelope_verbatim BYTE-IDENTICAL (asserted).

INTRA-PASS CORRECTION (2026-07-16, before any round-4 review): the first
application of this pass over-pinned two leaves against the REAL emission
surface — replace.n_ni was typed int and pinned == 1573, but n_ni is the
§R-REV4.3/ASM-2124 NI POWER REQUIREMENT (a rounded NUMBER; the RUN rule is
n_NI <= 1573), and carriers were pinned to D = 6144, which the driver's $0
--mock stub engine (lawful D = 8) cannot satisfy — both caught by running
`f1k_driver.py --mock` against the new schema (the mock's official-seam
step failed exactly there). The analysis now types n_ni as a number with
the <= 1573 RUN-coherence and binds carriers by INTEGER-D divisibility +
the exact KAEC file-size arithmetic (the real-run D = 6144 binds at the
generator-spec/driver seam). A second intermediate application then over-required the kot-log/1
chain fields on the record line (the mock's lawful bare-body direct
shape-check cannot carry them — log-append stamps them; they are now
typed WHEN PRESENT). This script therefore NORMALIZES from the round-3
frozen state or EITHER superseded intermediate round-4 freeze (e2022a...,
a7f971...), then applies the FINAL deltas — no intermediate freeze was
ever posted, reviewed, or committed.
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
OLD_FROZEN = "cf19b52a5361d0f3939385ac4c516d4341bd9408bae20e63085df340ae5e624b"
# superseded intra-pass intermediate freezes (never posted/reviewed/
# committed): the first application (n_ni/D over-pins), then the second
# (record chain-fields required, which the driver --mock's lawful bare-body
# direct shape-check cannot carry — presence is log-append's stamp)
INTERMEDIATE_FROZENS = (
    "e2022a5241c688c040121f3c0f73b23fb0ae95895faefa0a35a64a5df3c3a436",
    "a7f971b1373aed5aabea300e5d0bde78992992ed40e10b7d9cc33cb7c4952e30",
)
OLD_PIN = "5b5801664bb3653a50f7fdd1e5cebbf868d15c310813e6f8b8b5dc9548bbc7cc"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and \
    rec["frozen_sha256"] in (OLD_FROZEN,) + INTERMEDIATE_FROZENS
STARTING = rec["frozen_sha256"]
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a FOURTH time (conjunctive conditions)
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
assert idx.pop("f1k", None) == STARTING
kc.write_canonical_json(IDX, idx)

# ---- normalize a superseded intermediate round-4 application ----------------
if STARTING in INTERMEDIATE_FROZENS:
    i = rec["design"]["n_planned"]["statistics"].find(
        " HOLD ROUND-4 FIX (2026-07-16")
    assert i > 0
    rec["design"]["n_planned"]["statistics"] = \
        rec["design"]["n_planned"]["statistics"][:i]
    i = rec["title"].find(" HOLD REFREEZE 4 (2026-07-16")
    assert i > 0
    rec["title"] = rec["title"][:i]
    rec["pins"]["analysis_script"]["sha256"] = OLD_PIN
    # hm reversal happens below by matching on the round-4 strings first

# ---- 1. analysis pin ---------------------------------------------------------
new_sha = hashlib.sha256(
    (ROOT / "analysis" / "f1k.py").read_bytes()).hexdigest()
assert rec["pins"]["analysis_script"]["sha256"] == OLD_PIN
assert new_sha != OLD_PIN
rec["pins"]["analysis_script"]["sha256"] = new_sha
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

# ---- 2. harness_manifest: selftest description -> round-4 --------------------
hm = rec["pins"]["harness_manifest"]
old_seg = ("Mock self-test green 2026-07-16 (HOLD round-3 default-deny "
           "revision): `python3 analysis/f1k.py --selftest` at the EXACT "
           "C=96/n=1573 geometry")
new_seg = ("Mock self-test green 2026-07-16 (HOLD round-4 kot-f1k-record/1 "
           "full-depth revision): `python3 analysis/f1k.py --selftest` at "
           "the EXACT C=96/n=1573 geometry")
# the superseded intermediate application's selftest sentence (differs from
# the final new_rej only in the n_ni / D=6144 over-pins) — reversed first
INTERMEDIATE_REJ = (
    "9/9 hardened rejections + 13/13 STRICT-BOOL/guard-completeness "
    "gate probes + a 159-probe kot-f1k-record/1 FULL-DEPTH "
    "default-deny structural sweep DERIVED FROM THE DECLARATIVE "
    "SCHEMA ITSELF (every required key at EVERY depth popped; every "
    "nested block x null/int/string; an unknown key injected at "
    "EVERY object/map node; replace ALL-sub-fields + run/defer "
    "coherence; the FULL mc_exact_power interior pinned to the "
    "registered {mu*=4.09, n_sim=10000, seed=20260713, pass=true, "
    "ASM-2371 marginals}; mc_intersection == the registered "
    "ASM-2376 content EXACTLY, {'bogus':1} rejected; cost fully "
    "typed — integer prefills, hours bounded by the 900 h wall-"
    "clock cap — AND ledger-coherent (usd_total ~= usd_spent_prior "
    "+ run_hours*rate; usd_total=0 with positive metered time "
    "rejected) within the $155 ASM-2374 ceiling; carriers at the "
    "exact C*layers*D / KAEC-file-size expectation, D=6144 per the "
    "frozen generator-spec — each ERR_P2_ANALYSIS) + 47 value-level "
    "gate probes + 11 CLOSED-ROW-SCHEMA rejections (arm enum incl. "
    "an UNKNOWN-ARM row; pass a STRICT JSON integer in its per-arm "
    "range, the int() string-coercion path REMOVED; required "
    "fields; closed keys; registered tags) + a kot-log/1 "
    "FULL-record round-trip with 10 RECORD-level rejections "
    "(superseded dict form, rows-only record, declared-vs-actual "
    "metrics.rows_emitted count coherence, config n_test_items pin, "
    "closed config/metrics/top-level key sets, pseudonymous runner, "
    "exact 2-entry artifact pair, strict-seam non-final line) "
    "fail-closed")
if STARTING in INTERMEDIATE_FROZENS:
    assert new_seg in hm
    hm = hm.replace(new_seg, old_seg)
assert old_seg in hm
hm = hm.replace(old_seg, new_seg)
old_rej = ("9/9 hardened rejections + 13/13 STRICT-BOOL/guard-completeness "
           "gate probes + an 83-probe DEFAULT-DENY structural sweep (every "
           "mandatory sidecar block x missing/null/int/string, every "
           "mandatory field missing, unknown top-level key, replace.ran + "
           "inference null/int/string, power pinned EXACTLY to the "
           "ASM-2371 marginals with a non-empty ASM-2376 intersection "
           "block, cost numeric within the $155 ASM-2374 ceiling, carriers "
           "at the frozen C=96 — each ERR_P2_ANALYSIS) + 47 value-level "
           "gate probes + kot-log/1 artifacts-ARRAY round-trip (superseded "
           "dict form and rows-only record REJECTED) fail-closed")
new_rej = ("9/9 hardened rejections + 13/13 STRICT-BOOL/guard-completeness "
           "gate probes + a 159-probe kot-f1k-record/1 FULL-DEPTH "
           "default-deny structural sweep DERIVED FROM THE DECLARATIVE "
           "SCHEMA ITSELF (every required key at EVERY depth popped; every "
           "nested block x null/int/string; an unknown key injected at "
           "EVERY object/map node; replace ALL-sub-fields + §R-REV4.3 "
           "run/defer coherence — a RUN needs a numeric dev delta, an NI "
           "power requirement n_ni <= 1573 and io_saving > 0, a defer "
           "forbids a non-null io_saving; the FULL mc_exact_power interior "
           "pinned to the registered {mu*=4.09, n_sim=10000, "
           "seed=20260713, pass=true, ASM-2371 marginals}; "
           "mc_intersection == the registered ASM-2376 content EXACTLY, "
           "{'bogus':1} rejected; cost fully typed — integer prefills, "
           "hours bounded by the 900 h wall-clock cap — AND "
           "ledger-coherent (usd_total ~= usd_spent_prior + "
           "run_hours*rate; usd_total=0 with positive metered time "
           "rejected) within the $155 ASM-2374 ceiling; carriers bound by "
           "the frozen kaec_format arithmetic — params_added == "
           "C*layers*D for an INTEGER D (the real-run D=6144 binds at the "
           "generator-spec/driver seam) and table_bytes == the exact KAEC "
           "fp32 file size — each ERR_P2_ANALYSIS; plus a driver-emission "
           "positive control: the --mock stub shapes validate) + 47 "
           "value-level gate probes + 11 CLOSED-ROW-SCHEMA rejections "
           "(arm enum incl. an UNKNOWN-ARM row; pass a STRICT JSON "
           "integer in its per-arm range, the int() string-coercion path "
           "REMOVED; required fields; closed keys; registered tags) + a "
           "kot-log/1 FULL-record round-trip with 10 RECORD-level "
           "rejections (superseded dict form, rows-only record, "
           "declared-vs-actual metrics.rows_emitted count coherence, "
           "config n_test_items pin, closed config/metrics/top-level key "
           "sets, pseudonymous runner, exact 2-entry artifact pair, "
           "strict-seam non-final line) fail-closed")
if STARTING in INTERMEDIATE_FROZENS:
    # reverse whichever intermediate selftest sentence is present
    if INTERMEDIATE_REJ in hm:
        hm = hm.replace(INTERMEDIATE_REJ, old_rej)
    elif new_rej in hm:
        hm = hm.replace(new_rej, old_rej)
assert old_rej in hm
hm = hm.replace(old_rej, new_rej)
rec["pins"]["harness_manifest"] = hm

# ---- 3. statistics rider ------------------------------------------------------
np_ = rec["design"]["n_planned"]
np_["statistics"] += (
    " HOLD ROUND-4 FIX (2026-07-16, GPT-5.6 pre-run review-gate round-3 "
    "re-review): rounds 1..3b each validated one level and the next "
    "re-review found the NEXT level unvalidated — analysis-time validation "
    "now applies the COMPLETE DECLARATIVE kot-f1k-record/1 SCHEMA to the "
    "ENTIRE run record, recursively, default-deny at EVERY depth "
    "(additionalProperties:false + required fields at every object node; a "
    "type/registered-pin/bound on every leaf), so no field at any depth is "
    "unvalidated: (a) SIDECAR interiors — replace requires ALL of {ran "
    "strict-bool, delta_r_dev, n_ni, io_saving} with §R-REV4.3/ASM-2124 "
    "run/defer coherence (ran=true needs a numeric dev delta, an NI power "
    "requirement n_ni <= the registered n = 1573 — the RUN rule n_NI = "
    "delta_R*DEFF/SE_NI^2 <= n_max — and io_saving > 0; ran=false forbids "
    "a non-null io_saving, while the PRE-test gate measurements "
    "delta_r_dev/n_ni may lawfully persist on a defer); mc_exact_power "
    "requires its FULL "
    "registered interior {mu_star 4.09, n_sim 10000, seed 20260713, pass "
    "true, joint_power == the ASM-2371 table} EXACTLY; mc_intersection "
    "must equal the registered ASM-2376 content EXACTLY (a non-empty but "
    "bogus block is rejected); cost is fully typed (integer prefills; "
    "hours bounded by the registered 900 h wall-clock cap; rate positive) "
    "AND ledger-coherent (usd_total ~= usd_spent_prior + run_hours*rate "
    "and instance_hours ~= construction + sum(phase_seconds)/3600, cent/"
    "millihour tolerances — usd_total = 0 with positive metered time can "
    "never be a valid success record) within the $155 ASM-2374 ceiling; "
    "carriers bound by the frozen kaec_format arithmetic — params_added "
    "== C*layers*D for an INTEGER hidden dim D (the real-run D = 6144 "
    "binds at the generator-spec/driver kaec seam; the driver's $0 --mock "
    "stub lawfully runs the same pinned analysis at its own D) and "
    "table_bytes == the exact KAEC fp32 file size; (b) ROWS — every row "
    "validated against the CLOSED "
    "row schema: arm in the registered 7-arm enum (an UNKNOWN-ARM row was "
    "previously ignored silently), pass a STRICT JSON integer in its "
    "per-arm range (string '0' rejected; the int() coercion path REMOVED), "
    "strictly binary correct, registered tag vocabulary, all fields "
    "required, no unknown keys; (c) the RECORD LINE — config pinned to "
    "{protocol f1k-main-campaign, engine colibri, n_test_items 1573, "
    "r_drng_passes 3}, metrics.rows_emitted == the rows ACTUALLY pinned "
    "(declared-vs-actual count coherence), closed key sets, pseudonymous "
    "runner, exactly the 2-entry rows+sidecar artifact pair, and any "
    "stdin line that is not an eligible final run line is REJECTED rather "
    "than silently skipped. Channels unchanged: structural/type/pin "
    "defects => ERR_P2_ANALYSIS (no verdict producible); present-but-"
    "invalid attestation VALUES keep failing their gates CLOSED "
    "(INSTRUMENT-INVALID). The registry suites now carry an executing "
    "PAIRED-SIDECAR test class (success + missing/drifted/malformed/"
    "ambiguous/orphan sidecar, the rows-dup guard on paired records, the "
    "kot-log/1 non-run scope guard for role:'sidecar', and the rows-only/"
    "unmarked preservation controls) — 135/135 direct-suite tests, zero "
    "skips in a writable environment.")

# ---- 4. title rider -----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 4 (2026-07-16, GPT-5.6 pre-run review-gate round-3 "
    "re-review; registry/corrections/f1k/1-prefreeze-correction.json "
    "amended): COMPLETE declarative kot-f1k-record/1 schema — the ENTIRE "
    "run record (sidecar interiors incl. replace/mc_exact_power/"
    "mc_intersection/cost/carriers, the CLOSED row schema, the record "
    "line + rows-count coherence) validated recursively, default-deny at "
    "EVERY depth; paired-sidecar registry tests added (135/135, zero "
    "skips). Geometry, power table, budget, kill criterion, envelope all "
    "unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + HOLD round-4 kot-f1k-record/1 deltas "
      "applied; analysis sha %s -> %s" % (OLD_PIN[:12], new_sha[:12]))
