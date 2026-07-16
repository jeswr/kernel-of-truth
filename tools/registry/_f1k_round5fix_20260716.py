#!/usr/bin/env python3
"""One-shot GPT-5.6 pre-run HOLD ROUND-5 fix pass over registry/experiments/f1k.json.

The round-4 re-review (read-only codex, 2026-07-16) returned HOLD and
confirmed the round-4 declarative-schema architecture sound, but found
FOUR residual open/untyped nodes on validity/provenance/cost-bearing
paths of kot-f1k-record/1, all now CLOSED in analysis/f1k.py:

  (a) record.pins_observed was an OPEN-KEY map of "any" values
      ({"arbitrary": {"bogus": 1}} validated) -> now a typed CLOSED map
      (strict pin-name key pattern -> {observed[, expected]} sha256
      pairs); the open-ended "any" schema kind is REMOVED entirely (the
      gate-judged attestation leaves are now the explicit "attest" kind).
  (b) the kot-log/1 CHAIN fields (schema_version, seq, prev_sha256, ts,
      experiment, runner) were typed only WHEN PRESENT -> now REQUIRED:
      an UNSTAMPED record (never through log-append) can never validate.
      The driver's --mock supplementary direct shape-check now stamps the
      same sentinel fields before piping (f1k_driver.py run_analysis);
      the REAL stamp stays exercised by its official-seam step.
  (c) cost.phase_seconds restricted unknown keys but REQUIRED none (an
      empty/partial phase map — an unmetered ledger — validated) -> now
      ALL of {pilot, guard, test} required, each with positive seconds.
  (d) the cost-ledger equations ignored prefills and never priced
      construction hours (prefills=0 / phase_seconds={} / usd_total~0
      with positive construction hours validated) -> prefills >= 1 and
      usd_spent_prior must cover construction_instance_hours*spot_rate,
      so usd_total ~= prior + run_hours*rate transitively prices ALL
      metered work; an under-reported ledger never validates.

That edit changes the pinned analysis sha256 — and the frozen record pins
that sha — so this is a FIFTH lawful pre-final reset-refreeze
(precedents: _f1k_runhold_fix_20260715.py, _f1k_holdfix_20260716.py,
_f1k_round3fix_20260716.py, _f1k_round4fix_20260716.py; f1k is STILL not
GNG-0-signed and results-log/f1k.jsonl STILL does not exist). This script
resets the record to DRAFT and applies EXACTLY the round-5 deltas;
prereg-freeze re-freezes under the full lints. Build artifact, never part
of the frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the round-5 analysis/f1k.py
     (output_fields UNCHANGED, 50 pointers byte-identical).
  2. pins.harness_manifest: selftest description -> the round-5 revision
     (170-probe structural sweep, 19 record-level rejections, the
     residual-gap closures named).
  3. n_planned.statistics rider: the round-5 residual-gap closure.
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
OLD_FROZEN = "d4d58cb6355838996a5abe885b3db53a6f3301e9101b6585af5ab5b91f9b9da5"
OLD_PIN = "8d05201fac553a45840a365dc3b438f3735f50cb54a6b4214c507da7e589365e"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a FIFTH time (conjunctive conditions)
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
assert rec["pins"]["analysis_script"]["sha256"] == OLD_PIN
assert new_sha != OLD_PIN
rec["pins"]["analysis_script"]["sha256"] = new_sha
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

# ---- 2. harness_manifest: selftest description -> round-5 --------------------
hm = rec["pins"]["harness_manifest"]
old_head = ("Mock self-test green 2026-07-16 (HOLD round-4 "
            "kot-f1k-record/1 full-depth revision)")
new_head = ("Mock self-test green 2026-07-16 (HOLD round-5 residual-gap "
            "revision of the round-4 kot-f1k-record/1 full-depth schema)")
assert old_head in hm
hm = hm.replace(old_head, new_head)
old_sweep = "a 159-probe kot-f1k-record/1 FULL-DEPTH default-deny structural sweep"
new_sweep = "a 170-probe kot-f1k-record/1 FULL-DEPTH default-deny structural sweep"
assert old_sweep in hm
hm = hm.replace(old_sweep, new_sweep)
old_tail = ("each ERR_P2_ANALYSIS; plus a driver-emission positive "
            "control: the --mock stub shapes validate)")
new_tail = ("each ERR_P2_ANALYSIS; plus a driver-emission positive "
            "control: the --mock stub shapes validate; ROUND-5 "
            "residual-gap closure 2026-07-16: the open-ended 'any' "
            "schema kind REMOVED — pins_observed now a typed CLOSED map "
            "with a strict pin-name key pattern and {observed[, "
            "expected]} sha256 values, the {'arbitrary':{'bogus':1}} "
            "exploit rejected; all six kot-log/1 chain fields REQUIRED "
            "so an UNSTAMPED record rejects; cost-ledger completeness — "
            "prefills >= 1, the COMPLETE positive pilot/guard/test "
            "phase map, and construction hours PRICED via the "
            "usd_spent_prior >= construction_instance_hours*spot_rate "
            "floor, so the empty-phase-map / zero-prefill / "
            "construction-unpriced ledgers each reject)")
assert old_tail in hm
hm = hm.replace(old_tail, new_tail)
old_rec = ("with 10 RECORD-level rejections (superseded dict form, "
           "rows-only record, declared-vs-actual metrics.rows_emitted "
           "count coherence, config n_test_items pin, closed "
           "config/metrics/top-level key sets, pseudonymous runner, "
           "exact 2-entry artifact pair, strict-seam non-final line) "
           "fail-closed")
new_rec = ("with 19 RECORD-level rejections (superseded dict form, "
           "rows-only record, declared-vs-actual metrics.rows_emitted "
           "count coherence, config n_test_items pin, closed "
           "config/metrics/top-level key sets, pseudonymous runner, "
           "exact 2-entry artifact pair, strict-seam non-final line; "
           "ROUND-5: all six kot-log/1 chain fields popped in turn — "
           "the unstamped record rejects — and pins_observed junk/"
           "off-pattern-key/non-sha256 rejected with a typed positive "
           "control loading byte-identically) fail-closed")
assert old_rec in hm
hm = hm.replace(old_rec, new_rec)
rec["pins"]["harness_manifest"] = hm

# ---- 3. statistics rider ------------------------------------------------------
np_ = rec["design"]["n_planned"]
np_["statistics"] += (
    " HOLD ROUND-5 FIX (2026-07-16, GPT-5.6 pre-run review-gate round-4 "
    "re-review): the four residual open/untyped kot-f1k-record/1 nodes on "
    "validity/provenance/cost-bearing paths are CLOSED — (a) the "
    "open-ended 'any' schema kind is REMOVED (the gate-judged attestation "
    "leaves are the explicit 'attest' kind, each judged at its named gate "
    "on the INSTRUMENT-INVALID channel); record.pins_observed (previously "
    "an open-key map of 'any' values, so {'arbitrary':{'bogus':1}} "
    "validated) is now a typed CLOSED map — strict pin-name key pattern "
    "-> {observed[, expected]} sha256 pairs; (b) the kot-log/1 chain "
    "fields (schema_version, seq, prev_sha256, ts, experiment, runner) "
    "are REQUIRED on every record line, so an UNSTAMPED record — one that "
    "never went through log-append, the single write path — can never "
    "validate (the driver's $0 --mock supplementary direct shape-check "
    "now stamps the same sentinel fields before piping; its "
    "official-seam step still exercises the REAL log-append stamp + "
    "verdict-gen chain walk end-to-end); (c) cost.phase_seconds must "
    "carry ALL of {pilot, guard, test} with positive seconds — an "
    "empty/partial phase map (an unmetered ledger) rejects; previously "
    "unknown keys were restricted but none required; (d) the cost ledger "
    "must price ALL metered work: prefills >= 1 and usd_spent_prior must "
    "cover construction_instance_hours * spot_rate_usd_per_hour (cent "
    "tolerance; construction time is metered work at the registered "
    "ASM-2374 corner), so usd_total ~= usd_spent_prior + run_hours*rate "
    "transitively prices construction + run hours — the prefills=0, "
    "phase_seconds={}, and usd_total~0-with-positive-construction-hours "
    "ledgers all reject (budget honesty: an under-reported ledger must "
    "not validate). Channels unchanged: structural/type/pin defects => "
    "ERR_P2_ANALYSIS (no verdict producible); present-but-invalid "
    "attestation VALUES keep failing their gates CLOSED "
    "(INSTRUMENT-INVALID). The selftest carries a rejection probe for "
    "EACH gap (170-probe structural sweep; 19 record-level rejections "
    "incl. the six unstamped chain-field pops and the pins_observed "
    "exploit; cost-completeness probes) and the all-true/all-present "
    "fixture plus a typed pins_observed positive control still PASS "
    "byte-identically.")

# ---- 4. title rider -----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 5 (2026-07-16, GPT-5.6 pre-run review-gate round-4 "
    "re-review; registry/corrections/f1k/1-prefreeze-correction.json "
    "amended): residual open/untyped schema nodes closed — pins_observed "
    "a typed CLOSED map, kot-log/1 chain fields REQUIRED (unstamped "
    "records reject), complete positive phase map + all-metered-work "
    "cost pricing. Geometry, power table, budget, kill criterion, "
    "envelope all unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + HOLD round-5 residual-gap deltas "
      "applied; analysis sha %s -> %s" % (OLD_PIN[:12], new_sha[:12]))
