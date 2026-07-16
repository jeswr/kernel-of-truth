#!/usr/bin/env python3
"""One-shot RUN-HOLD fix pass over registry/experiments/f1k.json.

GPT-5.6 pre-run review-gate RUN-HOLD (2026-07-15) on the FROZEN f1k record
(frozen_sha256 4541966640b3...). Lawful pre-final reset-refreeze (precedent:
registry/corrections/rules-2/1-prefreeze-correction.json — f1k is NOT
GNG-0-signed and results-log/f1k.jsonl does not exist): this script resets
the record to DRAFT and applies EXACTLY the review-mandated deltas; the
coordinator-facing correction record documents them; prereg-freeze re-freezes
under the full lints. Build artifact, never part of the frozen record.

Deltas:
  1. pins.analysis_script.sha256 -> the fixed analysis/f1k.py (exact-C=96
     fail-closed geometry rejection + executable intersection disclosure +
     8/8 hardened-rejection selftest incl. the 97/95-cluster probes).
  2. Intersection assumption: the unsupported '~0.70-0.75' prose figure is
     WITHDRAWN, replaced by the MEASURED ASM-2376 sim + Frechet bounds.
  3. pins.corpus_hashes: f1k-trigger-map-v1 + f1k-eval-v1 resolved to REAL
     kot-corpus-hash/1 digests (96-concept REVISION-6 rebuilds);
     f1k-carriers-v1 placeholder rewritten to carry the committed 96-slot
     (A)-time generator digest, realized tables still lawfully B0.
  4. Law-1 assumption updated: the scoped amendment is now an explicit
     registry event (registry/governance/law-1/1-kae-scoped-amendment.json,
     ASM-2378), binding on the coordinator's landing commit.
  5. Coherence text: power_gate exact-form, statistics C-exact sentence,
     sec-power-scope endpoint intersection disclosure, harness_manifest
     selftest description, mc_exact_power_confirmation intersection rider,
     title rider. kill_criterion_verbatim and
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
OLD_FROZEN = "4541966640b391e50824765955447bcef103f94241e32b70e76a5c7f77e18079"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# ---- reset to DRAFT (pre-final reset-refreeze; freeze re-stamps these) -----
rec["status"] = "DRAFT"
for k in ("frozen_at", "frozen_by", "frozen_sha256"):
    rec.pop(k, None)
idx = json.loads(IDX.read_text(encoding="utf-8"))
assert idx.pop("f1k", None) == OLD_FROZEN
kc.write_canonical_json(IDX, idx)

# ---- 1. analysis pin --------------------------------------------------------
new_sha = hashlib.sha256(
    (ROOT / "analysis" / "f1k.py").read_bytes()).hexdigest()
rec["pins"]["analysis_script"]["sha256"] = new_sha

# ---- 2. intersection assumption (withdraw the prose figure) -----------------
np_ = rec["design"]["n_planned"]
hit = 0
for a in np_["assumptions"]:
    if a["claim"].startswith("CO-PRIMARY INTERSECTION DISCLOSURE"):
        a["claim"] = (
            "CO-PRIMARY INTERSECTION DISCLOSURE (GPT-5.6 pre-run review-gate "
            "RUN-HOLD defect-2 fix, 2026-07-15; the prior '~0.70-0.75' prose "
            "figure is WITHDRAWN as unsupported): the registered "
            "maintainer-approved power criterion is PER-RUNG joint power >= "
            "0.80 at each of K-1/K-2/K-3 (ASM-2371, unchanged). The "
            "probability that ALL THREE co-primary rungs fire simultaneously "
            "at mu* = +4.09 pts is NOT bounded below by 0.80 and is NOT "
            "separately powered: assumption-free the ASM-2371 marginals "
            "(0.8043/0.8058/0.8001) give only the Frechet interval "
            "[0.4102, 0.8001]; the MEASURED shared-K joint-dependence sim "
            "(ASM-2376; poc/f1k-askability/power_intersection_n1573.py -> "
            "reports/power-intersection-n1573.json, seed 20260713, "
            "registered marginal law preserved exactly, lambda grid "
            "{0,0.25,0.5,0.75,1}) bounds it to [0.5220, 0.7984] under the "
            "family, 0.6165 at the equal-arm-variance point lambda=0.5, "
            "MC-SE <= 0.005. Consequence stated pre-freeze: an elevated "
            "INCONCLUSIVE risk (e.g. 2 of 3 rungs fire), NEVER a false null "
            "- TOST/NULL rides only on K-1, every non-fire is scoped by the "
            "~4.06-4.09-pt MDE wording, and the disclosure is EXECUTABLE at "
            "/analysis/power_scope/intersection_all_three (Frechet bounds "
            "computed by analysis/f1k.py from the sidecar-carried per-rung "
            "powers; sim block carried verbatim), and ladder_rung_reached "
            "reports exactly how far the evidence got")
        a["tag"] = "MEASURED"
        hit += 1
    if a["claim"].startswith("MAINTAINER GATE 0"):
        a["claim"] = (
            "MAINTAINER GATE 0 (Law-1 scoped amendment + the KaE patch) and "
            "GATE 1 (plan + ceilings) are GO'd on the reduced-cost approach "
            "per kernel-of-truth #28; the Law-1 amendment IS NOW an explicit "
            "registry event (RUN-HOLD item-3 resolution, 2026-07-15): "
            "registry/governance/law-1/1-kae-scoped-amendment.json + "
            "ASM-2378 register the scoped amendment verbatim ('kernel-"
            "derived content vectors may enter model activations ONLY "
            "within the KaE track, only via the registered splice, deflator "
            "ladder mandatory'), authorized by the GATE-0 GO, binding on "
            "the coordinator's landing commit; no run starts before that "
            "commit exists (ASM-2025 satisfied by that event)")
        hit += 1
assert hit == 2, hit

# ---- 3. corpus pins ---------------------------------------------------------
pins = rec["pins"]["corpus_hashes"]
for name in ("f1k-trigger-map-v1", "f1k-eval-v1"):
    assert pins[name].startswith(kc.PINNED_AT_INPUTS_PREFIX)
    pins[name] = kc.corpus_hash(str(ROOT), name)
gen_digest = kc.corpus_hash(str(ROOT), "f1k-carriers-v1")
pins["f1k-carriers-v1"] = (
    "PINNED-AT-INPUTS:realized carrier tables for every arm (K, 3 "
    "derangements, d0, d2) + raw and rescaled norms — the B0 pure-function "
    "addendum (SSR-REV3.3); kot-corpus-hash/1 over data/f1k-carriers-v1/ "
    "pinned after construction, before the pilot. The (A)-time 96-slot "
    "GENERATOR components (REVISION-6 rebuild 2026-07-15: derangements for "
    "seeds 11/101/102/103 over 96 slots, carrier-index map ranks 1..96, "
    "concept-texts byte-identical to data/f1k-contrast-v1, 96x16 "
    "construction contexts, generator-spec) are COMMITTED NOW at directory "
    "digest " + gen_digest + " (ASM-2377); the B0 completion adds ONLY the "
    "realized tables/norms on top of these frozen rules")

# ---- 4./5. coherence text ---------------------------------------------------
np_["power_gate"] = (
    "HARD and EXACT (REVISION-6 gate as hardened by the RUN-HOLD fix "
    "2026-07-15): EXACTLY 96 concept clusters, EACH with >= 8 test items, "
    "at EXACTLY n = 1573, computed from the realized b0 test rows over the "
    "frozen askability-screen selection (ranks 1..96; realized allocation "
    "m_min 10, m_mean 16.3854, m_max 18); analysis/f1k.py REJECTS any "
    "realized cluster count != 96 or n != 1573 fail-closed "
    "(ERR_P2_ANALYSIS - off-geometry data can never PASS), and "
    "/gates/power_gate_valid is equality-form (n_clusters == 96 AND "
    "clusters-with-m>=8 == 96 AND n == 1573). Below the allocation floor "
    "F1-K does NOT run and returns to the maintainer with the measured "
    "coverage-vs-power shortfall")
np_["statistics"] += (
    " RUN-HOLD FIX (2026-07-15, GPT-5.6 pre-run review-gate): analysis-time "
    "validation additionally rejects fail-closed ANY realized cluster count "
    "!= the exact C = 96 (the >=-form gate previously admitted a 97-cluster "
    "universe at n = 1573 to a valid PASS - demonstrated and closed; "
    "selftest carries 97-cluster and 95-cluster rejection probes), and the "
    "co-primary intersection power disclosure is EXECUTABLE at "
    "/analysis/power_scope/intersection_all_three (Frechet bounds computed "
    "from the sidecar marginals + the ASM-2376 joint-dependence sim block).")
np_["mc_exact_power_confirmation"] += (
    " INTERSECTION (ASM-2376, MEASURED, RUN-HOLD defect-2 fix): P(all three "
    "rungs fire) at mu* is Frechet-bounded [0.4102, 0.8001] by the "
    "marginals and MEASURED [0.5220, 0.7984] under the shared-K "
    "joint-dependence family (0.6165 at lambda=0.5; "
    "poc/f1k-askability/reports/power-intersection-n1573.json); NOT "
    "separately powered to >= 0.80 - elevated INCONCLUSIVE risk, never a "
    "false null; the per-rung >= 0.80 criterion is unchanged.")
for ep in rec["endpoints"]:
    if ep["id"] == "sec-power-scope":
        ep["test"] += (
            " INTERSECTION DISCLOSURE (RUN-HOLD defect-2 fix, ASM-2376): "
            "/analysis/power_scope/intersection_all_three carries the "
            "COMPUTED Frechet bounds [0.4102, 0.8001] and the MEASURED "
            "shared-K joint-dependence sim [0.5220, 0.7984] (0.6165 at "
            "lambda=0.5) - the all-three-rungs full-PASS probability is not "
            "separately powered; the withdrawn '~0.70-0.75' figure never "
            "re-enters any wording.")
rec["pins"]["harness_manifest"] = rec["pins"]["harness_manifest"].replace(
    "Mock self-test green 2026-07-15 (REVISION-6 revision): `python3 "
    "analysis/f1k.py --selftest` at the C=96/n=1573 geometry (planted "
    "+10-pt lift -> PASS shape with ALL THREE co-primary rungs firing, on "
    "BOTH the sign-flip branch and the implemented BCa fallback branch; "
    "planted K~d2 TIE -> pass_gate FALSE, ladder 2, the ASM-2370 "
    "discipline; exact per-item null -> TOST NULL shape; 6/6 hardened "
    "rejections fail-closed: n != 1573, arm superset, non-binary "
    "correctness, mutated ceiling threshold, incoherent/missing inference "
    "method; pin round-trip byte-stable; 50/50 output fields present on "
    "both branches).",
    "Mock self-test green 2026-07-15 (RUN-HOLD-fix revision): `python3 "
    "analysis/f1k.py --selftest` at the EXACT C=96/n=1573 geometry (planted "
    "+10-pt lift -> PASS shape with ALL THREE co-primary rungs firing, on "
    "BOTH the sign-flip branch and the implemented BCa fallback branch; "
    "planted K~d2 TIE -> pass_gate FALSE, ladder 2, the ASM-2370 "
    "discipline; exact per-item null -> TOST NULL shape; executable "
    "intersection disclosure asserted (Frechet [0.4102, 0.8001] computed, "
    "ASM-2376 sim block carried); 8/8 hardened rejections fail-closed: "
    "n != 1573, 97-cluster off-geometry at n=1573 (the review-gate exploit "
    "shape, previously a valid PASS on the superseded script - regression-"
    "proven), 95-cluster off-geometry, arm superset, non-binary "
    "correctness, mutated ceiling threshold, incoherent/missing inference "
    "method; pin round-trip byte-stable; 50/50 output fields present on "
    "both branches).")
assert "RUN-HOLD-fix revision" in rec["pins"]["harness_manifest"]
rec["title"] += (
    " RUN-HOLD REFREEZE (2026-07-15, GPT-5.6 pre-run review-gate; "
    "registry/corrections/f1k/1-prefreeze-correction.json): exact-C=96 "
    "fail-closed geometry (off-geometry data can never PASS), executable "
    "intersection-power disclosure (ASM-2376: Frechet [0.4102, 0.8001], "
    "shared-K sim [0.5220, 0.7984]; '~0.70-0.75' withdrawn), 96-concept "
    "(A) input pins resolved (trigger-map + eval REAL digests; carriers "
    "generator digest carried, B0 completion unchanged), Law-1 scoped "
    "amendment registered (ASM-2378). Power table and PROXY-PROVISIONAL "
    "validity scope unchanged.")

# ---- invariants -------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + RUN-HOLD deltas applied; analysis sha %s; "
      "trigger-map %s; eval %s; carriers-generator %s"
      % (new_sha[:12], pins["f1k-trigger-map-v1"][:12],
         pins["f1k-eval-v1"][:12], gen_digest[:12]))
