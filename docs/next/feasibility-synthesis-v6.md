# Cross-experiment feasibility synthesis v6 — after rules-1-c, the g2-import-v2 pilot stops, and scale S0

## Status, scope, and tags

- **Status:** synthesis update. This document supersedes `docs/next/feasibility-synthesis-v5.md` as the standing programme-level feasibility picture. It changes no frozen record, verdict, audit, result log, or registered assumption; assumption rows PROPOSED-ASM-1840..1846 are emitted alongside (`docs/next/asm-synthesis-v6-1840-1849.json`) for coordinator registration.
- **Scope:** both programme theses — **CORRECTNESS** and **EFFICIENCY** — after the rules-1-c INSTRUMENT-INVALID readout, the two g2-import-v2 Stage-P pilot stops, the correctness-track instrument assessment, the adoption of the blocking-pilot protocol (ASM-1830..1836, now in the register), the SCALE-1 S0 10k rung, and the launch of DDC T0 (in flight at write time).
- **Ownership:** this synthesis OWNS the synthesis-level conclusion. The verdicts stated here are programme-state verdicts (INCONCLUSIVE-PENDING where that is what the evidence supports); they are not experiment verdicts, which remain the property of the pinned verdict-gen chain, and not the maintainer's programme decision, which remains open issue #24 and the standing decision rights.
- **Riders:** every f2b/DECONF claim retains its self-authored, kernel-covered, oracle-addressed, scale-bounded riders; every g2-family gold-dependent claim remains PROVISIONAL-ON-LLM-PROXY until human reconciliation; the coverage disclosure (kernel-expressibility **0.3542 at rung molecules-v0**, one incomplete kernel-v0 instance, measured by m0b) applies wherever content claims are made.

Epistemic tags:

- **[MEASURED, VERDICT-GRADE]** — registered observation supporting a mechanical verdict, audit-confirmed where stated.
- **[MEASURED]** — read from committed bytes or pinned mechanical output; includes instrument facts from invalid runs (which license instrument findings only, never hypothesis findings).
- **[MEASURED-CERTIFICATE]** — the deterministic RULES-1 CPU certificate result; a passed precondition, not a programme verdict.
- **[PROVISIONAL-ON-LLM-PROXY]** — measured against proxy labels whose direction vs reconciled human judgment is unproven.
- **[IN-FLIGHT, UNGRADED]** — execution started, no licensed grade.
- **[BUILT, NOT RUN]** — instrument and materials exist; no non-mock result.
- **[PROVISIONAL]** — a stated reading that a named pending event can overturn.
- **[SUBJECTIVE]** — one model's weighed opinion, binding on nothing.
- **[INTERPRETIVE]** — this synthesis's composition of evidence.
- **[STIPULATED]** — frozen scope, registered rule, or adopted plan choice.
- **[EXTRAPOLATION]** — direction-only, never a premise.

---

## 0. Governing sentence

> **LOAD-BEARING:** The programme's measured positives are unchanged since v5 — an audit-confirmed authored-content lift on a 135M host (+0.25 f2b-transfer, +0.27 alignment-specific DECONF-B) and a passed CPU certificate of rules-machinery non-inertness (858/858 against third-party gold; entailed decisions irreproducible from stated bytes). What v6 adds is a sharpened *negative-space* diagnosis: every sharper affirmative question — kernel-specific runtime structure, engine-verify-retry host lift, typing soundness — is now known to be **uninstrumented rather than answered**, after three rules-lane instrument failures culminating in rules-1-c INSTRUMENT-INVALID and a g2 proxy-pair that stopped at AC1 0.6222 vs the 0.65 gate. EFFICIENCY still has **zero live data**; its first datum (DDC) is in flight. Both theses remain **INCONCLUSIVE-PENDING**. **[INTERPRETIVE composition of measured constituents]** [PROPOSED-ASM-1840/1841] [STIPULATED: ASM-1840]

---

## 1. What changed after v5

1. **rules-1-c landed and graded INSTRUMENT-INVALID.** `engagement_valid = FALSE`: every A3 row `attempts = 1`; A3 correctness-identical to the shuffled control c1 on all 2,574 item×seed cells. Proximate cause: a URN/word type mismatch at the verifier's address check made it abstain unconditionally; beneath it, a design-layer theorem — at a 2-option surface a non-leaking verifier is necessarily vacuous and an informative one necessarily decisive. `kill_b_fired` was computed but never reaches the verdict (rule-0 ordering); the engine-verify-retry claim is therefore **not killed — it has never been validly measured**. **[MEASURED/MECHANICAL, per `docs/next/analysis/rules1c-instrument-invalid-interpretation.md` §0–§1; frozen record `registry/experiments/rules-1-c.json`]** (Provenance note: the mechanical readout is reported verbatim in the interpretation document; no `registry/verdicts/rules-1-c.json` artifact was found at this read — the verdict-file commit is an outstanding runner/coordinator action and nothing below depends on more than the reported gate vector.)
2. **The campaign's instrument by-products are real and reusable.** The ENTITY form is the first rules-lane surface the pinned hosts demonstrably operate (A5 0.944, A7 1.000, A1 0.703 at chance 0.5); the "neutral" padding block is measurably non-neutral (+0.171 at the 135M — larger than the 0.05 SESOI); A7 = 1.000 is a rendering-competence datum, never an inference claim. **[MEASURED]**
3. **g2-import-v2 stopped at the pilot gate, twice, correctly.** Pilot #1: AC1 0.6909 ≥ 0.65 but a calibration-channel infrastructure failure (an MCP connector leak into 1/62 sessions). Pilot #2 (post-hardening): AC1 **0.6222 < 0.65** with **κ = 0.0000 exactly** — the judge pair agreed at precisely its independence rate; the full run was never launched. All prevalence-free known-answer channels were green in both pilots (hedge-calibration 12/12 semantic, flip 0/8, decisive 40/40 per judge). The gap is arithmetically one item at n=40, and the two pilots' run-to-run movement (2 items) equals the gate margin: a boundary-sitting instrument, refused certification exactly as designed. **[MEASURED; `docs/next/analysis/correctness-track-instrument-assessment.md` §0.1, §2.1]**
4. **The v2.2 bounded rubric attempt is in flight.** The v2.2 rubric and harness are built under a recorded pre-commitment (ASM-1825): AC1 ≥ 0.65 on the fresh Stage-P pilot → the $5–6 full run; a second AC1 failure → the proxy-pair instrument is retired for this record family and the two-human panel becomes the instrument. The first v2.2 pilot invocation (17:19Z today) aborted fail-closed at the pA judge preflight before any judged item — no pilot datum yet. **[MEASURED run directory `poc/ontology-import-g2-v2/runs/pilot-v22-20260712-171919/`; IN-FLIGHT]**
5. **The blocking-pilot protocol is registered.** ASM-1830..1836 are now in `registry/assumptions.jsonl`: no prereg-freeze without a recorded instrument pilot PASSED at the operating point (checks PC-1..PC-5), with an explicit override path. The rules-2 instrument pilot is the first instance. **[MEASURED register; STIPULATED rule]**
6. **SCALE-1 S0 (10k) measured.** §3 below. **[MEASURED]**
7. **DDC T0 is running.** Launch gates all green on the rerun (16:52Z); the A0 baseline cell for the 135M donor is computing at write time. This is the efficiency thesis's first-ever live execution. **[MEASURED run logs; IN-FLIGHT, UNGRADED]**

---

## 2. CORRECTNESS thesis

> **Synthesis verdict: INCONCLUSIVE-PENDING** — and the v6 refinement of that state: the gap between what is licensed and what is claimed-for is an **instrumentation gap before it is an evidence gap**. **[INTERPRETIVE]** [PROPOSED-ASM-1840]

### 2.1 Licensed [MEASURED, VERDICT-GRADE unless noted]

- **Authored-content lift, twice, audited.** f2b-transfer: +0.2507 on blind externally-adjudicated gold, endorsement 320/333 = 0.9610, all gates TRUE, PASS, audit CONFIRMED. DECONF-B: Δ_align +0.2697 (Holm-passed), bridge lift +0.285 (LB95 +0.255), PASS, audit CONFIRMED — with the licensed cap verbatim: the value is in the item-aligned, answer-bearing *content*; the kernel is one way to *author* such a key; **no kernel-specific runtime contribution is measured** (GS-A–kernel identity fraction 1.0). (`registry/verdicts/f2b-transfer.json`, `registry/verdicts/deconf-b.json`)
- **Rules machinery non-inertness at certificate scope.** RULES-1 CPU certificate: engine 858/858 vs third-party CLUTRR gold (Wilson-LB95 0.9955); stated-cell C_dec = 1.0 (1,716/1,716) vs entailed-cell C_dec = 0.0 (0/3,680 reproducible from stated bytes); refusal 100/100; counterfactual controls as predicted; SPARQ–twin agreement 1,207/1,207; <2 s, ~$0. **[MEASURED-CERTIFICATE]** The engine computes correct entailed decisions that flat lookup cannot. It does not connect that computation to any model.

### 2.2 Open — uninstrumented, NOT killed

- **Kernel-specific structure.** Every deconfound that asked answered "content, not structure" (identity 1.0; CASC-0′ gloss≡plain at R2; g2-import breadth control within noise). The designated honest decider — the knull rules-source ablation — has never run (its host-lift activation gate is unfulfillable on the rules-1-c branch). **[MEASURED verdicts; state PROVISIONAL]**
- **Engine-verify-retry host lift.** Three instruments consumed, zero valid readings: rules-1 VOID (elicitation; all arms 0.000 including the oracle arm), rules-1-b superseded pre-final-phase (form-dead surface, pilot A5 0/24), rules-1-c INSTRUMENT-INVALID (verifier never engaged, atop the 2-option leak–vacuity dilemma). At this operating point (135M host, depth-2 items, 3-name lexicons ⇒ 2-option surface) the claim **has no valid carrier in this design family** — closed independently by the leak–vacuity theorem, the exhaustion degeneracy (k=4 vs 2 options), and the abstaining shuffled control. The claim itself is unmeasured in both directions. **[MEASURED + DERIVED, per the rules-1-c interpretation; endorsement INTERPRETIVE]**
- **Typing soundness.** g2's adverse proxy bracket (33/84 = 0.3929 sound) is itself INSTRUMENT-INVALID (84 < 500); g2-import v1 INSTRUMENT-INVALID (κ_A3 = 0.286); the v2 successor has never launched its full run (two pilot stops, §1.3). The GO-shaped import signal (soundness roughly doubling, bracket-robust) exists **only under invalid instruments** and licenses nothing. **[MEASURED + PROVISIONAL-ON-LLM-PROXY]**

### 2.3 The diagnostic pattern, stated precisely

The correctness ledger is now five-for-five on one side and zero-for-five on the other: every experiment with a **deterministic or externally-adjudicated measurement channel** (string-equality acceptance, blind human-protocol adjudication, exact match vs third-party gold) instrumented cleanly and answered; every experiment requiring a **judgment interface the programme's smallest components must stably support** (a 135M host cooperating with an interactive verifier; a two-proxy judge pair agreeing on hedged compound semantics at prevalence ≈0.84) failed its instrument. The five failures failed at five *different* channels — the signature of a hard instrument neighbourhood, not of an untestable quantity. **[MEASURED ledger; ASSESSMENT endorsed from `correctness-track-instrument-assessment.md` §0–§1]**

The assessment's weighting of candidate explanations — **scale artifact 45% / design-space (testable another way) 40% / thesis genuinely hard to demonstrate 15%** — is adopted here as what it is: **[SUBJECTIVE]**, one model's explanatory-mass allocation, never a premise. What keeps the hard-thesis reading at minority weight is decisive for the verdict wording: neither sub-track has yet run a *valid* affirmative instrument even once, so "hard to demonstrate" cannot be distinguished from "never yet validly attempted" on the current record. The correct epistemic state for every affirmative correctness quantity is **UNMEASURED**, and the correct thesis verdict is **INCONCLUSIVE-PENDING**, not "adverse". **[INTERPRETIVE]**

What would move this verdict: a persistent deflationary/affirmative asymmetry *through valid instruments* (rules-2 with a passed blocking pilot; a human-gold g2) should promote the hard-thesis reading to primary; a single valid affirmative result flips the ledger from zero-for-five to one-for-six and re-opens the attribution chain (knull ablation next). **[STIPULATED reading discipline]**

---

## 3. EFFICIENCY thesis

> **Synthesis verdict: INCONCLUSIVE-PENDING — on zero live data.** No experiment whose primary endpoint is an efficiency quantity has ever produced a valid grade. **[INTERPRETIVE state; PROPOSED-ASM-1841]**

The honest ledger, in full:

- The one non-inferiority read ever taken came back not-shown: `noninferiority_vs_r3 = false` (135M + verifier vs 1.7B, f2b-transfer). **[MEASURED]** That is an absence of a demonstration, not an adverse verdict.
- CASC-0′ (static-medium shrinkage) is INSTRUMENT-INVALID (TTC mismatch 0.3537 > 0.30); no M2 verdict in either direction. **[MEASURED]**
- rules-1-c's verifier-offload leg (s3) is unevaluable under its INSTRUMENT-INVALID verdict. **[MEASURED]**
- The f2b/DECONF-B lift is an *offload-mechanism* observation (a small host converts retries into accuracy through a cheap deterministic acceptance interface) and a genuine input to efficiency thinking — but its experiments' endpoints were correctness endpoints; nothing about parity, shrinkage, or cost was licensed. **[MEASURED at scope; classification INTERPRETIVE]**
- Mint, review, routing, retry, maintenance, and coverage-adjusted economics: unpriced. **[MEASURED absence]**

**DDC is the first live efficiency measurement, and it is running now.** T0 (corpora pinning, token-parity gate I-3 green at ±10%, A0 baselines) is executing at write time **[IN-FLIGHT, UNGRADED]**; ddc0 (Stage-0 statistics, ~$5 cap) follows, then ddc1 (the arm campaign, ~$60 cap) gated on ddc0's admission result. The design tests whether **kernel-guided direction choice preserves more ability than magnitude/random pruning at equal size**, training-free, on SmolLM2-135M/360M BASE against public benchmarks, with mandatory shuffled-kernel and knull-render controls and one primary endpoint (Δ* > 0 at ρ = 0.75, the minimum of two correlated contrasts; TOST equivalence margin ±2 points). (`docs/next/design/DDC.md`)

What the first datum will and will not license — fixed now, before any number exists **[STIPULATED]**:

- **ddc0** licenses only whether kernel-aligned directions are *admitted* (survive the joint max-stat permutation family) — an instrument/admission fact gating ddc1's aligned arm; no ability, efficiency, or correctness claim in any direction.
- **ddc1**, if it runs and passes, licenses at most: *kernel-guided direction choice beats magnitude/random at matched sparsity on these two base checkpoints, these benchmarks, training-free* — **sign, not slope**; no model-replacement claim, no cost claim, no correctness claim, no extrapolation across model families.
- A TOST-equivalent ddc1 is the first valid *adverse* efficiency datum at this scope (kernel guidance adds nothing over magnitude at matched sparsity). A ddc0 non-admission stops the aligned arm and leaves efficiency at zero data *with a measured reason*.
- Under **every** ddc branch, EFFICIENCY remains short of a thesis verdict: parity/non-inferiority vs a larger host and lifecycle economics are separate, unaddressed legs.

---

## 4. SCALE — S0 (10k), and the standing backdrop

The deterministic import-vectoriser's **crosstalk model holds at scale** **[MEASURED]**: disjoint-pair σ within 3% of 1/√D at D ∈ {8192, 512, 576}; the √(2 ln m/D) max-spurious-cosine curve is a respected upper envelope at m = 10⁴; byte-determinism across independent recomputation; encode cost 39.3 ms/concept (≈10.9 CPU-h extrapolated at 1M — not the wall). Four measured blockers accompany it: **WordNet-only typing yields 0% identity/dependence coverage — the 0.95 UFO-typing gate is unreachable in principle on this source**; exact O(m²) cleanup dies between 100k and 1M (ANN + ≥0.99 recall gate mandatory); the SemCor selection rule exhausts at 27,210; duplicate structural mass (20.1% of records, worsening down the tail) — not crosstalk — is the binding margin constraint, so the S1 margin gate is uninterpretable without a pre-registered duplicate policy. (`docs/next/analysis/scale-s0-interpretation.md`; scoped to `kot-enc-import/*`, not construction B.)

The backdrop this leaves standing **[INTERPRETIVE]**: the programme's thesis-relevant demonstrations still live at **fewer than 100 concepts** (84 g2 slots; the closed kinship inventory; coverage 0.3542 at molecules-v0). S0 shows the *representational substrate* scales as designed and shows exactly which non-encoder machinery (multi-source typing, crosswalks, dedup policy, ANN) does not yet exist. That is a **barrier-not-result**: scale remains a rung on which no thesis quantity has yet been measured, and S0/S1 are machinery qualification by their own design (§14 discipline), never thesis evidence.

---

## 5. The clearest path to a defensible verdict — fewest experiments, in order

**[STIPULATED plan composition; each experiment's licences are its own record's, restated here without extension]** [PROPOSED-ASM-1845]

The serial spine is four experiments; everything else is background or authority-transfer. Gating decisions en route: the maintainer's **#24** host-integration slot decision; the **ASM-1825** pre-commitment on the g2 proxy pair; **ddc0's admission gate**; S1's pre-registration-before-vectorise rule.

1. **rules-2 REWORK-3 (train-time internalisation) — the one correctness host-integration experiment.** Validated instrument pilot at the operating point (the blocking-pilot exemplar) → freeze → GPU (~$14), pending #24. It removes the failed interface *by construction*: no inference-time host–verifier cooperation; the channel (weight change → forced-choice accuracy vs the certified engine's gold) is the most deterministic the lane has proposed. Two named design-opens (2-option derangement re-operationalisation; non-bridge-name shortcut audit) are exactly where a sixth instrument failure would occur and must clear the pilot's PC-3/PC-4 checks first.
   *Result map:* valid positive (B2−B0 with non-degenerate controls) → **GO at scope**: "engine-materialised entailments are internalisable by a small host" — kernel-specificity still pending the knull-closure analog (+~$4), which is the mandatory second half of any GO. Valid null/negative → **NO-GO for the train-time slot at this scope** — the first valid adverse host-integration datum the programme has ever had, and genuinely informative. Another instrument failure → still inconclusive, but the 15% hard-thesis weighting is promoted and the slot question returns to the maintainer with a materially worse prior. rules-1-d stays a paper design gated on a demonstrated nonzero rejection rate.
2. **g2 typing: one bounded v2.2 proxy attempt, then the human panel.** Per ASM-1825: v2.2 Stage-P pass (AC1 ≥ 0.65) → the $5–6 full v2.2 run (PROVISIONAL-ON-LLM-PROXY under any outcome); second failure → proxy pair retired. Either branch terminates the proxy iteration loop. The decisive spend is the **two-human blind adjudicated panel on the 84 slots** — the frozen envelope's sole adoption authority, immune to proxy-pair pathology, and cheap in the currently-cheap resource (human-hours).
   *Result map:* human A3 ≥ 34/84 (the quarantined bracket-robustness analysis says the primary would settle under every label construction) → **GO** for a bounded, advisory, non-binding soft-typing shard — never hard laws, never a thesis verdict. Human < 34/84 → **NO-GO at this scope**; hard Π stays demoted; the repair direction dies at this rendering. Humans *also* split on the residual items → still inconclusive on soundness but a finding in itself: the hedged soft-typing rendering, not the judges, resists crisp adjudication ⇒ redesign the rendering.
3. **DDC ddc0 → ddc1 — the efficiency thesis's first and second data.** Already in flight; result map in §3. This lane is gated on nothing external and should not wait on the rules lane.
4. **Scale S1 (100k)** under the de-risked plan (pre-registered selection rule + duplicate/differentia policy first; SCC fixture; multi-source typing portfolio with the stratified human audit — the single cheapest item that gives the 0.95 gate an estimator at all; ANN ≥ 0.99 recall gate).
   *Result map:* S1 clean → machinery qualified for the 1M rung where the only thesis-grade scale quantity (the SCALE-GROUND nested interaction) lives; **no GO/NO-GO on any thesis is available from S1 by design**. S1 gate failures → measured constraints, redesign, still inconclusive. S1 buys *runnability of the real experiment*, nothing else.

**What "defensible verdict" means at the end of this path [INTERPRETIVE]:** after (1)+(knull analog) and (2-human), CORRECTNESS has, for the first time, valid instruments over all three open quantities — at which point PASS/FAIL wording is licensed *at scope* and the remaining distance to a thesis verdict is scope (natural-input reach, coverage growth, generality beyond kinship), which is honestly a second campaign, not a hidden footnote. After (3), EFFICIENCY moves from zero data to one or two signed data; a thesis-grade efficiency verdict additionally needs the parity and economics legs neither DDC branch supplies. No shorter path exists on the current board that does not route through an instrument already known to be invalid.

---

## 6. What the programme can honestly claim today

**[INTERPRETIVE, composed only of licensed constituents; every sentence carries its source record's riders]** A deterministic rules engine over kernel-expressed worlds is exactly correct at its certified scope and computes entailed decisions that lookup over stated facts cannot reproduce (858/858 vs third-party gold; entailed-cell 0/3,680) — at ~$0. Kernel-authored, item-aligned content, checked through a thin deterministic acceptance interface, measurably lifts a 135M host on externally adjudicated gold, twice, audit-confirmed (+0.25, +0.27 alignment-specific) — and the same audited experiments show the value is carried by the content, with no kernel-specific runtime structure measured at that seam and no demonstration that the boosted 135M matches a 1.7B. Every sharper affirmative claim — kernel-specific structural value, engine-assisted host lift at inference time, soundness of the kernel's typing, repaired or not — is currently **unmeasured in both directions**, because no valid instrument has yet reached it: three rules-lane instruments failed at three different interfaces, and the typing line's proxy-judge instrument stopped, correctly, at its own stability gate. The efficiency thesis has produced no live datum yet; its first (training-free kernel-guided compression) is executing now. The vector substrate's crosstalk arithmetic holds at 10k concepts, while all thesis-relevant demonstrations remain below ~100 concepts at kernel coverage 0.35. Both theses are inconclusive-pending; the programme's next results are instrument-validated by a now-registered blocking-pilot protocol, and the fewest-experiments path to defensible scoped verdicts is four experiments deep.

---

## 7. Bottom line

**LOAD-BEARING:** CORRECTNESS remains **INCONCLUSIVE-PENDING**. Licensed: verdict-grade authored-content lift (f2b-transfer, DECONF-B; value in content, not kernel-specific runtime structure) and the RULES-1 certificate (machinery non-inert, exact at scope). Open and uninstrumented — not killed: kernel-specific structure (knull pending), engine-verify-retry lift (three instrument failures; no valid carrier at the current operating point), typing soundness (g2 proxy AC1 0.6222 vs 0.65; human panel pending). The gap is an instrumentation gap (weighting 45/40/15 scale/design/hard, [SUBJECTIVE]) before it is an evidence gap. [PROPOSED-ASM-1840, -1842, -1843] [STIPULATED: ASM-1840]

**LOAD-BEARING:** EFFICIENCY remains **INCONCLUSIVE-PENDING on zero live data.** No efficiency-endpoint experiment has ever validly graded; DDC T0 is in flight and ddc0/ddc1 will produce the first sign-level datum under fixed claim caps (sign not slope; no parity, cost, or correctness claim on any branch). [PROPOSED-ASM-1841] [STIPULATED: ASM-1840]

**LOAD-BEARING:** SCALE is a qualified substrate under a measured barrier: crosstalk arithmetic holds at 10k [MEASURED: docs/next/analysis/scale-s0-interpretation.md]; the UFO-typing gate is unreachable on WordNet alone; thesis-relevant results remain at <100 concepts. S0/S1 qualify machinery and can never, by design, yield a thesis verdict. [PROPOSED-ASM-1844] [STIPULATED: ASM-1840]

The fewest-experiments path: **rules-2 (pilot-validated, pending #24) + its knull analog; one bounded g2 v2.2 attempt then the two-human panel; ddc0 → ddc1; scale S1** — with GO/NO-GO/inconclusive wording fixed per branch in §5 before any result exists. [PROPOSED-ASM-1845; the expectation that this path suffices is EXTRAPOLATION, PROPOSED-ASM-1846]

---

## Epistemic register

- **MEASURED, verdict-grade:** f2b-transfer PASS (audit CONFIRMED): +0.2507, endorsement 320/333, noninferiority false. DECONF-B PASS (audit CONFIRMED): Δ_align +0.2697, bridge +0.285 (LB95 +0.255), GS-A–kernel identity 1.0.
- **MEASURED-CERTIFICATE:** RULES-1 CPU: 858/858 (Wilson-LB95 0.9955), stated/entailed C_dec 1.0/0.0, refusal 100/100, twin 1,207/1,207.
- **MEASURED (instrument facts, hypothesis-inert):** rules-1-c INSTRUMENT-INVALID (attempts=1 ×2,574; A3≡c1; ENTITY-form floors A5 0.944/A7 1.000/A1 0.703; padding +0.171); g2-import-v2 pilots AC1 0.6909 then 0.6222 (κ = 0.0000), pilot-stop held; g2 33/84 and g2-import v1 both INSTRUMENT-INVALID; CASC-0′ INSTRUMENT-INVALID; S0 crosstalk/blocker set.
- **PROVISIONAL-ON-LLM-PROXY:** every g2-family soundness number, adverse and GO-shaped alike.
- **IN-FLIGHT, UNGRADED:** DDC T0; the g2 v2.2 Stage-P attempt (first invocation aborted at preflight).
- **BUILT, NOT RUN:** rules-2 REWORK-3 (fail-closed behind ERR_PIN/ERR_FRAME_DRIFT, GPU held on #24); the knull ablations.
- **SUBJECTIVE:** the 45/40/15 instrument-failure weighting; every ranking in §5 beyond the recorded gating rules.
- **EXTRAPOLATION:** that the §5 path produces defensible scoped verdicts; every 100k/1M scale figure; any expectation about DDC's sign.

*Supersede this synthesis when any of the following lands: the rules-2 pilot/campaign, the g2 v2.2 pilot or human panel, ddc0/ddc1, the knull ablation, or the rules-1-c verdict artifact commit. Do not silently edit its evidence state.*
