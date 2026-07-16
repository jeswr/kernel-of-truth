#!/usr/bin/env python3
"""One-shot REVISION-6 amendment of registry/experiments/f1k.json (DRAFT).

Applies the maintainer-approved powered geometry (2026-07-15): C=96, n=1573,
mu*=+4.09 pts, R=(1,3,1); K-3 co-primary; $155 cap; new pins. Companion ASMs
ASM-2369..2375 (docs/next/design/asm-f1k-geometry-2369-2375.json). Idempotent
in effect (sets fields to final values); run once by designer-32. Deleted or
kept as a build artifact — never part of the frozen record.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kot_common as kc

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "registry" / "experiments" / "f1k.json"

NEW_ANALYSIS_SHA = "9d01468e99c61d71fd47235614795ea3bb976e3ea184e96899d4dd11b86286a7"
CONTRAST_PIN = "c6eb82944ed15827d15aae59e7e522693b1a9917cd914086e8514778a47fb78d"
KV1_PIN = "f2c8472778bc95f92c09b95f845b8d32e383b980d62cb9e801693cd8066a6fd1"

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "DRAFT"

# ---- budget (ASM-2374, successor of ASM-2283) ------------------------------
rec["budget"]["usd_cap"] = 155

# ---- analysis plan anchor: REVISION-6 rider --------------------------------
rec["analysis_plan_ref"]["anchor"] += (
    " — all as amended by REVISION-6 (the maintainer-approved powered "
    "geometry 2026-07-15, ASM-2369..2375, "
    "docs/next/design/asm-f1k-geometry-2369-2375.json): C=96, n=1573, "
    "mu*=+4.09 pts, R=(1,3,1), K-1/K-2/K-3 CO-PRIMARY "
    "(pass_gate = k1 AND k2 AND k3); latest revision governs on conflict")

d = rec["design"]
np_ = d["n_planned"]

# ---- n_planned geometry ----------------------------------------------------
np_["n_max"] = 1573
np_["n_test_items"] = (
    "n = EXACTLY 1573 (REVISION-6/ASM-2369: the maintainer-approved raise of "
    "the prior 1440 cap, 2026-07-15, after the $0 blind askability screen "
    "returned the registered PRE-RUN RETURN at n=1440 — K-3 joint power "
    "0.7955 < 0.80; the geometry was re-powered, the bar untouched). The "
    "design runs AT the cap; analysis/f1k.py rejects any other realized n "
    "fail-closed.")
np_["power_gate"] = (
    "HARD (REVISION-6 each-cluster gate, ASM-2369, successor of ASM-2271): "
    ">= 96 concept clusters EACH with >= 8 test items at EXACTLY n = 1573, "
    "computed from the realized b0 test rows over the frozen askability-"
    "screen selection (ranks 1..96; realized allocation m_min 10, m_mean "
    "16.3854, m_max 18); below it F1-K does NOT run and returns to the "
    "maintainer with the measured coverage-vs-power shortfall")
np_["mc_exact_power_confirmation"] = (
    "SSR-REV5 EXECUTED PRE-SPEND at the frozen geometry (MEASURED, "
    "ASM-2371; poc/f1k-askability/power_n1573.py -> "
    "reports/power-report-n1573.json, 2026-07-15, $0/blind/deterministic): "
    "exact cluster-sign-flip JOINT power at mu* = +4.09 pts, seed 20260713, "
    "N_sim = 10000, B = 10000 add-one, delta = rho_U = 0.10, fire iff "
    "p < 0.05 AND T >= 0.03 — K-1 (R=1) 0.8043 / K-2 (R=3) 0.8058 / K-3 "
    "(R=1) 0.8001, MC-SE ~0.004, 80%-power MDEs 4.072/4.063/4.090 pts; all "
    "three co-primary rungs >= 0.80. DISCLOSED: K-3 clears by 0.0001 at "
    "MC-SE 0.0040 (knife-edge; the frozen-seed point estimate governs, and "
    "any K-3 non-fire is scoped by the +4.09-pt MDE wording, never read as "
    "a clean null at +3). Re-executed unchanged at addendum (6) as a "
    "reporting-fidelity check into the sidecar -> /analysis/power_scope; "
    "never a spend lever.")
np_["scoring_passes"] = (
    "1 prefill per item per arm; main arms = b0, d0, d1-drng x3, d2, "
    "d3-text, K = 8 passes x 1573 = 12584 prefills (+1 conditional REPLACE "
    "pass = 1573 more, run only if dev delta_R <= ~0.038 per SSR-REV4.3 AND "
    "the ASM-2374 ledger projection keeps total <= $155); + construction "
    "<= 3072 + pilot ~6200 + guard <= 660")
np_["budget_note"] = (
    "usd_cap = 155 is the REVISION-6 maintainer-approved ceiling "
    "(2026-07-15, ASM-2374, SUCCESSOR of ASM-2283/ASM-2205's $149 at "
    "n=1440): at the ASM-2205 pessimistic corner (100 s/prefill / 1.20 "
    "pinning / $0.28/h spot i4i.2xlarge) the 8-pass main volume gives "
    "22516 prefills -> 521 instance-h -> $146; WITH the conditional "
    "REPLACE pass 24089 prefills -> 558 h -> ~$156, marginally above the "
    "cap at that corner — so REPLACE runs ONLY if the bring-up-measured "
    "projection keeps the total ledger <= $155, else DEFERRED (its modal "
    "expectation; SSR-REV4.3 PRE-test decision). Approval-memo planning "
    "figure ~555 instance-h, 0 GPU-h; EC2 instance compute only, "
    "storage/tax/transfer separately accounted. If pinning yields < 1.20x "
    "or spot exceeds $0.28/h, the SSR6 degradation order governs and the "
    "ceiling re-derives from measured throughput at the bring-up "
    "affordability gate. Reductions may never cut n below 1573 or drop a "
    "ladder arm (SSR6 as amended by ASM-2369).")
np_["statistics"] += (
    " REVISION-6 (ASM-2369/2370): all constants above unchanged except the "
    "geometry — C = 96 clusters, n = 1573 exact — and the verdict "
    "conjunction: /analysis/pass_gate = k1_joint_pass AND k2_joint_pass "
    "AND k3_joint_pass (K-3 co-primary).")
np_["assumptions"] += [
    {"claim": "REVISION-6 geometry is the maintainer-approved powered "
              "geometry (2026-07-15): C=96, n=1573, mu*=+4.09 pts, "
              "R=(1,3,1) — registered ASM-2369 (successor of ASM-2271), "
              "docs/next/design/asm-f1k-geometry-2369-2375.json; the "
              "askability screen's n=1440 NOT-ASKABLE-AT-SCALE verdict is "
              "the recorded trigger, not overridden by the designer",
     "tag": "STIPULATED"},
    {"claim": "K-1/K-2/K-3 are CO-PRIMARY (ASM-2370): PASS requires all "
              "three joint passes; a K~d2 tie denies the PASS and is "
              "reported at equal prominence (content-not-structure). The "
              "kot-reg/1 single-primary lint is satisfied structurally: "
              "role:primary stays on K-1 (SESOI carrier); the conjunction "
              "lives in /analysis/pass_gate",
     "tag": "STIPULATED"},
    {"claim": "Frozen-geometry exact joint power (ASM-2371, MEASURED, seed "
              "20260713): K-1 0.8043 / K-2 0.8058 / K-3 0.8001 at mu* = "
              "+4.09 pts — all >= 0.80; K-3 is a disclosed knife-edge "
              "(clears by 0.0001 at MC-SE 0.0040)",
     "tag": "MEASURED"},
    {"claim": "Pre-spend structure-question-askable deflator gate SATISFIED "
              "(ASM-2372): $0 gold-label/model-outcome-blind screen, "
              "redacted-input hash 4f7cf1c6a5b5e92655581ba901ea35ce3c6781e3"
              "f5279a7b4181b2d4bafc0359 frozen before screening; 96/96 "
              "concepts contrast-CERTIFIED (condition iv): hashes differ, "
              "NLD >= 0.20 (min 0.387), prompt-hash-diff rate 1.00, "
              "outside-payload diff 0",
     "tag": "MEASURED"},
    {"claim": "CONDITION-I VALIDITY BAR (ASM-2373, open EXTRAPOLATION, "
              "resolution = human fidelity pass over the 96 pinned "
              "explication texts): the explications are PROXY/UNVALIDATED "
              "instruments (kernel-v0 explicator-authored, kernel-v1 "
              "pipeline-minted; mechanical + LLM-proxy validation only, NO "
              "human fidelity pass) — any F1-K PASS is PROXY-PROVISIONAL: "
              "it licenses 'these 96 kernel-record texts as carriers beat "
              "matched dictionary glosses at this model/box', NOT "
              "'validated NSM explications beat dictionaries'",
     "tag": "EXTRAPOLATION"},
    {"claim": "Explication + dictionary texts pinned PRE-SPEND as "
              "data/f1k-contrast-v1 (ASM-2375; freeze-manifest (A) item "
              "(ii) completed now, not deferred): kot-corpus-hash/1 " +
              CONTRAST_PIN + "; kernel-v1 source corpus pinned " + KV1_PIN +
              "; K/d3-text construction MUST read kernel.txt and d2 MUST "
              "read dictionary.txt from this pin",
     "tag": "STIPULATED"},
]

# ---- arms: d2 wording now cites the pin + co-primary -----------------------
arms = d["arms_mandatory_baselines"]
for i, a in enumerate(arms):
    if a.startswith("d2 plain-dictionary"):
        arms[i] = ("d2 plain-dictionary definitions of the SAME concepts "
                   "(the knull proper, rung K-3 — CO-PRIMARY per ASM-2370), "
                   "texts pinned pre-spend at data/f1k-contrast-v1/"
                   "<rank>-<slug>/dictionary.txt (ASM-2375), same "
                   "construction, norm-rescaled to the K reference")

# ---- endpoints -------------------------------------------------------------
for ep in rec["endpoints"]:
    if ep["id"] == "primary-k1-add-lift":
        ep["test"] = ep["test"].replace(
            "The record VERDICT PASS additionally requires rung K-2 "
            "(/analysis/pass_gate = k1_joint_pass AND k2_joint_pass) "
            "— the mandatory deflator discipline (ASM-2029/2036; "
            "ASM-2271).",
            "The record VERDICT PASS additionally requires rungs K-2 AND "
            "K-3 (/analysis/pass_gate = k1_joint_pass AND k2_joint_pass "
            "AND k3_joint_pass) — the mandatory deflator discipline "
            "elevated to the CO-PRIMARY four-condition form "
            "(ASM-2029/2036; ASM-2369/2370, REVISION-6).")
        assert "CO-PRIMARY four-condition" in ep["test"]
    if ep["id"] == "sec-k2-dose-exact-deflator":
        ep["test"] = ("CO-PRIMARY rung (ASM-2370; schema role stays "
                      "'secondary' — the kot-reg/1 single-primary slot "
                      "is K-1's — but the record VERDICT requires this "
                      "rung). " + ep["test"])
    if ep["id"] == "sec-k3-knull":
        ep["test"] = (
            "CO-PRIMARY rung (REVISION-6, ASM-2370; schema role stays "
            "'secondary' — the kot-reg/1 single-primary slot is K-1's "
            "— but the record VERDICT requires this rung): rung K-3, "
            "the kernel-vs-generic hard bar of the deciding four-condition "
            "test — K vs d2 plain-dictionary carriers (matched texts "
            "pinned at data/f1k-contrast-v1, condition-iv contrast "
            "certified: NLD >= 0.20, min 0.387), same joint rule (exact "
            "cluster sign-flip p < 0.05 AND lift >= +3.0 pts), joint power "
            "0.8001 at mu* = +4.09 pts (ASM-2371, disclosed knife-edge). A "
            "K~d2 tie — still the modal expectation on the "
            "four-deflation record — now DENIES the record PASS "
            "(pass_gate false, ladder caps at 2) and is reported at equal "
            "prominence in the pre-adopted content-not-structure wording. "
            "Cluster-BCa 95% CI reported at /analysis/k3_ci95; the same "
            "dev-selected sign-flip-vs-BCa method governs "
            "(/analysis/inference_method). Any PASS through this rung is "
            "PROXY-PROVISIONAL per ASM-2373 (explications are an "
            "unvalidated-instrument proxy pending human fidelity "
            "validation).")
    if ep["id"] == "sec-power-scope":
        ep["test"] = (
            "Realized (C, m) joint-MDE at rho_U = 0.10 + the frozen "
            "pre-spend Monte-Carlo EXACT-test joint power (SSR-REV5; "
            "MEASURED at the REVISION-6 geometry: K-1 0.8043 / K-2 0.8058 "
            "/ K-3 0.8001 at mu* = +4.09 pts, ASM-2371) carried from the "
            "sidecar; any non-fire is scoped 'powered to resolve >= [joint "
            "MDE ~4.06-4.09] pts at rho_U = 0.10', never a clean null at "
            "+3.")

# ---- hypotheses ------------------------------------------------------------
hyp = rec["hypotheses"]
for i, h in enumerate(hyp):
    if h.startswith("H-K3"):
        hyp[i] = (
            "H-K3 (kernel-specific, the hard bar; CO-PRIMARY per "
            "REVISION-6/ASM-2370): K beats the plain-dictionary d2 knull "
            "(matched texts pinned at data/f1k-contrast-v1; NLD >= 0.20 "
            "certified) at the same joint rule (rung K-3), joint power "
            "0.8001 at mu* = +4.09 pts. On the four-deflation record a "
            "K~d2 tie remains the MODAL expectation and is reported at "
            "equal prominence in the content-not-structure wording — "
            "but under REVISION-6 a tie DENIES the record PASS (ladder "
            "caps at 2): K-3 now moves the verdict, not just the wording. "
            "A K-3 PASS is PROXY-PROVISIONAL pending human fidelity "
            "validation of the explication instrument (ASM-2373).")
    if h.startswith("H0/NULL"):
        hyp[i] = h.replace(
            "a rung-2/3 null is the next content-not-structure datum.",
            "a rung-2/3 null is the next content-not-structure datum (and "
            "under REVISION-6 a rung-3 null/tie denies the PASS).")

# ---- kill criterion: pre-run return geometry -------------------------------
rec["kill_criterion_verbatim"] = rec["kill_criterion_verbatim"].replace(
    "PRE-RUN RETURNS (F1-K does not start): power gate < 65 clusters with "
    "m >= 8 within n_max = 1440 (SSR-REV2.2 — the scale gate biting, "
    "not a lever failure);",
    "PRE-RUN RETURNS (F1-K does not start): power gate < 96 clusters EACH "
    "with m >= 8 at exactly n = 1573 (REVISION-6/ASM-2369, successor of "
    "the SSR-REV2.2 C>=65@1440 gate that ALREADY FIRED once: the 2026-07-15 "
    "askability screen returned NOT-ASKABLE-AT-SCALE at n=1440, K-3 power "
    "0.7955, and the maintainer re-powered the geometry — the scale "
    "gate biting, not a lever failure);")
assert "REVISION-6/ASM-2369" in rec["kill_criterion_verbatim"]

# ---- envelope: geometry + validity bar --------------------------------------
rec["extrapolation_envelope_verbatim"] = rec[
    "extrapolation_envelope_verbatim"].replace(
    "the mechanically filtered known-concept QA subset (composition "
    "reported verbatim; internal-relative numbers, never "
    "leaderboard-comparable);",
    "the mechanically filtered known-concept QA subset at the REVISION-6 "
    "frozen geometry — the 96 askability-screen concepts (45 "
    "kernel-v0 + 51 kernel-v1) and exactly 1573 test items (composition "
    "reported verbatim; internal-relative numbers, never "
    "leaderboard-comparable);")
rec["extrapolation_envelope_verbatim"] += (
    " VALIDITY BAR (condition i, ASM-2373 — binding on every "
    "citation): the 96 explications are a PROXY instrument — "
    "explicator-authored (kernel-v0) or pipeline-minted (kernel-v1) texts "
    "validated mechanically and by LLM proxy only, with NO human fidelity "
    "validation of explication-to-concept faithfulness — so ANY PASS "
    "of this record is PROXY-PROVISIONAL: it licenses 'these 96 "
    "kernel-record texts, spliced as carriers, beat matched dictionary "
    "glosses on concept-covered QA at this model and box', and does NOT "
    "license 'validated NSM explications beat dictionaries' until the "
    "human fidelity pass over the pinned data/f1k-contrast-v1 texts "
    "confirms the instrument; every scoreboard citation of a PASS carries "
    "the PROXY-PROVISIONAL label verbatim.")

# ---- pins -------------------------------------------------------------------
p = rec["pins"]
p["analysis_script"]["sha256"] = NEW_ANALYSIS_SHA
p["corpus_hashes"]["f1k-contrast-v1"] = CONTRAST_PIN
p["corpus_hashes"]["kernel-v1"] = KV1_PIN
p["harness_manifest"] = p["harness_manifest"].replace(
    "Mock self-test green 2026-07-13 (codex-review-hardened revision): "
    "`python3 analysis/f1k.py --selftest` (planted +10-pt lift -> PASS "
    "shape on BOTH the sign-flip branch and the implemented BCa fallback "
    "branch; exact per-item null -> TOST NULL shape; 6/6 hardened "
    "rejections fail-closed: n != 1440, arm superset, non-binary "
    "correctness, mutated ceiling threshold, incoherent/missing inference "
    "method; pin round-trip byte-stable; 50/50 output fields present on "
    "both branches).",
    "Mock self-test green 2026-07-15 (REVISION-6 revision): `python3 "
    "analysis/f1k.py --selftest` at the C=96/n=1573 geometry (planted "
    "+10-pt lift -> PASS shape with ALL THREE co-primary rungs firing, on "
    "BOTH the sign-flip branch and the implemented BCa fallback branch; "
    "planted K~d2 TIE -> pass_gate FALSE, ladder 2, the ASM-2370 "
    "discipline; exact per-item null -> TOST NULL shape; 6/6 hardened "
    "rejections fail-closed: n != 1573, arm superset, non-binary "
    "correctness, mutated ceiling threshold, incoherent/missing inference "
    "method; pin round-trip byte-stable; 50/50 output fields present on "
    "both branches).")
assert "REVISION-6 revision" in p["harness_manifest"]

# ---- title ------------------------------------------------------------------
rec["title"] += (
    " REVISION-6 (maintainer-approved powered geometry, 2026-07-15; "
    "ASM-2369..2375, docs/next/design/asm-f1k-geometry-2369-2375.json): "
    "C=96 concepts (the frozen askability-screen selection, redacted-input "
    "hash 4f7cf1c6), n=1573 exact (cap raised from 1440 after the "
    "registered pre-run power return), mu*=+4.09 pts, R=(1,3,1); "
    "K-1/K-2/K-3 CO-PRIMARY (a K~d2 tie denies PASS); exact joint power "
    "MEASURED 0.8043/0.8058/0.8001 at seed 20260713; texts pinned "
    "data/f1k-contrast-v1; $155 cap; any PASS is PROXY-PROVISIONAL "
    "pending human fidelity validation of the explication instrument "
    "(ASM-2373).")

kc.write_canonical_json(REC, rec)
print("f1k.json REVISION-6 amendment written")
