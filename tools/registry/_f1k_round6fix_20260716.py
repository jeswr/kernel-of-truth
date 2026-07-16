#!/usr/bin/env python3
"""One-shot HOLD ROUND-6 (final static review) fix pass over
registry/experiments/f1k.json.

The F1-K final static review (2026-07-16) CONFIRMED provenance consistency
(schema architecture, driver, geometry, intersection, seam, provenance
chain all sound) but found TWO residual static-validation defects in the
pinned analysis/f1k.py, both now CLOSED as a CLASS:

  (1) REGEX ANCHOR — trailing-newline bypass: every "strict" pattern on a
      validity/provenance-bearing field (RUNNER_RE, HEX64_RE, TS_RE, the
      pins_observed key pattern) was applied via re.match(...$); Python $
      matches BEFORE a terminal newline, so "runner-1\\n", 64-hex+"\\n",
      a trailing-newline timestamp and a trailing-newline pin key all
      validated. Now: every such regex is anchored \\Z and applied via
      re.fullmatch (both _sv call sites — string `pattern` and map
      `key_pattern`); NO regex on a validity/provenance field uses $.
  (2) BUDGET-HONESTY GAP — a zero/under-reported cost ledger validated:
      the ledger identities were purely RELATIVE (tolerances $0.01 /
      0.001 h), so prefills=1 + 1 s phases + all-zero totals was
      arithmetically coherent and schema-legal (mins were 0). Now: the
      schema carries SCALE FLOORS at the registered ASM-2374 campaign
      scale (corner: 22,516 prefills -> 521.2 instance-h -> ~$146) —
      usd_total >= 73.0 and instance_hours >= 260.6 (STIPULATED at half
      the corner: admits up to 2x better-than-corner realized throughput,
      rejects any >=2x under-report), prefills >= 11,011 (= 1573 * 7
      mandatory arm-passes, a deterministic COUNT under the frozen
      design), construction_instance_hours strictly positive. The $155
      ceiling and the round-4/5 identities are unchanged as upper
      bound/coherence. The --selftest fixture ledger is now the
      full-scale corner ledger; the driver's $0 --mock cost CONFIG
      carries the same planning-scale prior/construction figures
      ([R6-4]-style real registered figures) so the emission-surface
      oracle still runs end-to-end green at $0 real spend.

That edit changes the pinned analysis sha256 — and the frozen record pins
that sha — so this is a SIXTH lawful pre-final reset-refreeze
(precedents: _f1k_runhold_fix_20260715.py, _f1k_holdfix_20260716.py,
_f1k_round3fix_20260716.py, _f1k_round4fix_20260716.py,
_f1k_round5fix_20260716.py; f1k is STILL not GNG-0-signed and
results-log/f1k.jsonl STILL does not exist). This script resets the
record to DRAFT and applies EXACTLY the round-6 deltas; prereg-freeze
re-freezes under the full lints. Build artifact, never part of the
frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the round-6 analysis/f1k.py
     (output_fields UNCHANGED, 50 pointers byte-identical).
  2. pins.harness_manifest: selftest description -> the round-6 revision
     (173-probe structural sweep, 26 record-level rejections, the
     regex-anchor + budget-honesty closures named).
  3. n_planned.statistics rider: the round-6 closure.
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
OLD_FROZEN = "5fba4acbe6a91d0821ead78ac5b0beb10a09cbe53bf7dd812c552fd9070a2245"
OLD_PIN = "55eafe349be250ded20c404c1bbee4abce8cbdc5be47889ff3bc7b10c3d97306"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a SIXTH time (conjunctive conditions)
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

# ---- 2. harness_manifest: selftest description -> round-6 --------------------
hm = rec["pins"]["harness_manifest"]
old_head = ("Mock self-test green 2026-07-16 (HOLD round-5 residual-gap "
            "revision of the round-4 kot-f1k-record/1 full-depth schema)")
new_head = ("Mock self-test green 2026-07-16 (HOLD round-6 "
            "final-static-review revision of the round-5 kot-f1k-record/1 "
            "full-depth schema)")
assert old_head in hm
hm = hm.replace(old_head, new_head)
old_sweep = ("a 170-probe kot-f1k-record/1 FULL-DEPTH default-deny "
             "structural sweep")
new_sweep = ("a 173-probe kot-f1k-record/1 FULL-DEPTH default-deny "
             "structural sweep")
assert old_sweep in hm
hm = hm.replace(old_sweep, new_sweep)
old_ledger = ("cost-ledger completeness — prefills >= 1, the COMPLETE "
              "positive pilot/guard/test phase map, and construction "
              "hours PRICED via the usd_spent_prior >= "
              "construction_instance_hours*spot_rate floor, so the "
              "empty-phase-map / zero-prefill / construction-unpriced "
              "ledgers each reject)")
new_ledger = ("cost-ledger completeness — prefills >= 1, the COMPLETE "
              "positive pilot/guard/test phase map, and construction "
              "hours PRICED via the usd_spent_prior >= "
              "construction_instance_hours*spot_rate floor, so the "
              "empty-phase-map / zero-prefill / construction-unpriced "
              "ledgers each reject; ROUND-6 final-static-review closure "
              "2026-07-16: BUDGET-HONESTY SCALE FLOORS at the registered "
              "ASM-2374 campaign scale — usd_total >= $73 and "
              "instance_hours >= 260.6 h (half the ~$146 / 521.2 h "
              "corner), prefills >= 11,011 (= 1573*7 mandatory "
              "arm-passes), construction hours strictly positive — so "
              "the all-zero (prefills=1 / 1 s phases / $0 totals, "
              "identity-coherent within tolerance), positive-hours/"
              "zero-dollars, and coherently-10x-under-reported ledgers "
              "each reject while the full-scale corner ledger passes)")
assert old_ledger in hm
hm = hm.replace(old_ledger, new_ledger)
old_rec = ("with 19 RECORD-level rejections (superseded dict form, "
           "rows-only record, declared-vs-actual metrics.rows_emitted "
           "count coherence, config n_test_items pin, closed "
           "config/metrics/top-level key sets, pseudonymous runner, "
           "exact 2-entry artifact pair, strict-seam non-final line; "
           "ROUND-5: all six kot-log/1 chain fields popped in turn — "
           "the unstamped record rejects — and pins_observed junk/"
           "off-pattern-key/non-sha256 rejected with a typed positive "
           "control loading byte-identically) fail-closed")
new_rec = ("with 26 RECORD-level rejections (superseded dict form, "
           "rows-only record, declared-vs-actual metrics.rows_emitted "
           "count coherence, config n_test_items pin, closed "
           "config/metrics/top-level key sets, pseudonymous runner, "
           "exact 2-entry artifact pair, strict-seam non-final line; "
           "ROUND-5: all six kot-log/1 chain fields popped in turn — "
           "the unstamped record rejects — and pins_observed junk/"
           "off-pattern-key/non-sha256 rejected with a typed positive "
           "control loading byte-identically; ROUND-6: every validity/"
           "provenance regex re.fullmatch + \\\\Z anchored, NEVER $ — "
           "Python $ matches before a terminal newline — so "
           "trailing-newline runner/ts/prev_sha256/prereg_hash/"
           "pins_observed-key/pins_observed-sha values and an "
           "embedded-newline runner each reject, clean values loading "
           "byte-identically) fail-closed")
assert old_rec in hm
hm = hm.replace(old_rec, new_rec)
rec["pins"]["harness_manifest"] = hm

# ---- 3. statistics rider ------------------------------------------------------
np_ = rec["design"]["n_planned"]
np_["statistics"] += (
    " HOLD ROUND-6 FIX (2026-07-16, F1-K final static review): the two "
    "residual static-validation defects are CLOSED as a CLASS — (1) "
    "REGEX ANCHORS: every validity/provenance-bearing pattern in "
    "kot-f1k-record/1 (runner, ts, all sha256 fields incl. prev_sha256/"
    "prereg_hash/artifacts/pins_observed values, the pins_observed key "
    "pattern) is now \\\\Z-anchored and applied via re.fullmatch at BOTH "
    "validator call sites; the former re.match(...$) discipline let "
    "trailing-newline values validate because Python $ matches before a "
    "terminal newline. NO regex on a validity/provenance field uses $. "
    "(2) BUDGET-HONESTY SCALE FLOORS: the ledger identities were purely "
    "relative, so a zero/near-zero ledger (prefills=1, 1 s phases, $0 "
    "totals) was coherent within the rounding tolerances and its zero "
    "totals were schema-legal; the schema now requires usd_total >= "
    "$73.0 and instance_hours >= 260.6 h (STIPULATED at half the "
    "ASM-2374 pessimistic-corner ~$146 / 521.2 h mandatory-campaign "
    "figures: admits up to 2x better-than-corner realized throughput, "
    "rejects any >=2x under-report), prefills >= 11,011 (= 1573 * 7 "
    "mandatory arm-passes — a deterministic count under the frozen "
    "design [MEASURED arithmetic]), and construction_instance_hours "
    "strictly positive; the $155 ASM-2374 ceiling and the round-4/5 "
    "coherence identities are unchanged. The selftest carries a "
    "rejection probe for EACH bypass (trailing-newline runner/ts/"
    "prev_sha256/prereg_hash/pins_observed key+sha, embedded-newline "
    "runner; the all-zero, positive-hours/zero-dollars, and coherently "
    "10x-under-reported ledgers) and the clean/full-scale fixtures "
    "still PASS byte-identically; the driver's $0 --mock cost CONFIG "
    "carries the ASM-2374 planning-scale prior/construction figures so "
    "the emission-surface oracle stays green end-to-end.")

# ---- 4. title rider -----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 6 (2026-07-16, F1-K final static review; "
    "registry/corrections/f1k/1-prefreeze-correction.json amended): "
    "validity/provenance regexes fullmatch+\\\\Z (trailing-newline bypass "
    "closed), budget-honesty scale floors on the cost ledger "
    "(zero/under-reported ledgers reject). Geometry, power table, "
    "budget cap, kill criterion, envelope all unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + HOLD round-6 final-static-review deltas "
      "applied; analysis sha %s -> %s" % (OLD_PIN[:12], new_sha[:12]))
