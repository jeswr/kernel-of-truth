# Cross-experiment feasibility synthesis v3 — where both theses actually stand

- **Author:** Fable (synthesis agent), 2026-07-11 (evening wave). This is the CAPSTONE
  refresh the round-2 steering note scheduled ("cross-experiment feasibility-synthesis
  refresh once G0 + stage-2 land" [ref: docs/next/analysis/round2-steering.md §Next-wave]).
  It SUPERSEDES `docs/next/feasibility-synthesis.md` (2026-07-11 morning edition), whose
  governing sentence is now stale in one load-bearing respect (§0). This document changes
  NO frozen record, NO verdict object, NO registry line, NO registered assumption; it runs
  no experiment and performs no git/bd/kb operation. Neither thesis conclusion is mine to
  declare: this document states the evidenced STATE and the critical path, and stops there.
- **What landed since the morning capstone** (each read at source, in full, with its
  epistemic status carried on every use):
  1. `docs/next/interpretations/f2b-transfer-stage2.md` — stage-2 **PASS**, now
     **audit-CONFIRMED** [MEASURED: registry/audit-status.jsonl f2b-transfer line, Gate-A
     cross-vendor audit `registry/audits/f2b-transfer/1-gate-a-codex.json`, result CONFIRM,
     auditor GPT-5.6/codex, endpoint recompute ok]. NOTE a mechanical inconsistency for the
     coordinator: `registry/verdicts/f2b-transfer.json` still carries `audit.state = PENDING`
     while the audit-status ledger and the audit artifact record CONFIRMED — the verdict
     object's audit field needs the mechanical update; nothing in this synthesis depends on
     which file is authoritative because both the ledger and the artifact agree on CONFIRM.
  2. `docs/next/interpretations/f2b-transfer-stage1.md` — stage-1 FINAL post-judge-3
     endorsement [MEASURED: A = 320/333 = 0.9610, Wilson LB 0.9395, human-anchored].
  3. `docs/next/interpretations/deconf-a1.md` (rev-4, complete certificate) — C_dec = 1.0
     exactly, 40,576/40,576 [MEASURED, **EXPLORATORY pre-registration**; the §3.1(c)
     replay component is a disclosed answer-superset SUBSTITUTE resting on an unmeasured
     code-level confluence argument — that disclosure rides every citation here].
  4. `docs/next/interpretations/codevert-g0.md` — κ_q^indep = 0.4361 [0.3610, 0.5364]
     [MEASURED, **non-scored spike, off the pinned G1 pool** — a verdict INPUT, never a
     G1 verdict].
  5. `docs/next/analysis/g3-result.md` + `docs/next/interpretations/g3-llmproxy-v3.md` —
     human Pass-A g3: hybrid necessity 46/200 = 0.230, Wilson LB 0.1848 > 0.10, FAIL-side
     [**PROVISIONAL** — human q1 × LLM-proxy q2 hybrid; human Pass B NOT DONE and is the
     sole adjudicator]; human-vs-GPT-5.6 q1 agreement κ = 0.7561 [MEASURED]; the frozen
     llmproxy-v3 FAIL-analog (concordant 36/195, LB 0.1433) [MEASURED, weak proxy per
     ASM-0550].
  6. `docs/next/analysis/coverage-census.md` — D3 upper-sieve κ = 0.6665; general-index
     ceiling under the sound lane 0.9860 [MEASURED κ + COMPUTED BOUND under a provisional
     pin; STILL-INCOMPLETE for any kill].
  7. `docs/next/analysis/round2-steering.md` [OPINION/steering, dual-model convergent].
  8. `docs/next/arch/cascade-naturalisation.md` (CASC/1, H-CN) [**DESIGN** — maintainer-
     proposed, developed, UNFROZEN; GPT-5.6 critique IN FLIGHT].
- **In flight, to be folded when they land** [STIPULATED: deferral discipline per
  ASM-0761's precedent]: (i) human g3 **Pass B** (and A2) — converts every PROVISIONAL g3
  quantity to MEASURED and alone licenses the real g3 verdict; (ii) **g2** (Π read-out
  soundness vs human gold, g3-gated); (iii) the **GPT-5.6 critique of CASC/1**; (iv) DECONF
  registration (external review → freeze → registered re-run) and the stage-2-runner-vs-A1
  pin comparison the stage-2 interpretation asks for. None of these is load-bearing enough
  to defer this synthesis, and none can *reverse* a standing INCONCLUSIVE (there is no
  FEASIBLE/NOT-FEASIBLE call to reverse); each resolves or sharpens a leg named below.
- **Epistemic discipline:** every load-bearing line carries its `[TAG]`. **MEASURED**
  restates a measured/computed fact strictly inside its own envelope, never recomputed;
  **PROVISIONAL** marks the g3 hybrid quantities (human q1 × proxy q2, Pass B owed);
  **STIPULATED** marks frozen text, registered rulings, and framing adopted verbatim;
  **DERIVED** marks this document's own rule-application from MEASURED facts;
  **INTERPRETIVE** marks this document's composition of measured results, never a fact of
  any record; **EXTRAPOLATION** is direction-only and load-bearing for nothing.
  Cross-experiment readings are EXTRAPOLATION by house law and are never premises.

---

## 0. The governing sentence, revised — one word of it changed, and it matters

The morning capstone's governing sentence was: *"Across the entire registry there are ZERO
audited end-task wins over the kernel-as-text null that are attributable to the kernel's
content"* — and its own maintenance discipline (via the stage-2 interpretation §7) pre-named
the condition under which it would go stale: Gate-A audit confirmation. That condition has
now been met [MEASURED: audit-status.jsonl, Gate-A CONFIRM]. The revised governing sentence,
worded per the stage-2 interpretation's §5 attribution requirement [STIPULATED, adopted
verbatim]:

> LOAD-BEARING: [MEASURED: registry/verdicts/f2b-transfer.json] the registry now contains **ONE audited end-task win on blind,
> ground-truth-independent external gold** — a 135M host + deterministic verify-retry over
> the kernel-authored store gains **+0.2507 absolute** over the same host alone, the lift
> is **content-specific** (seed-pinned shuffled arm recovers <30% at the one-sided 95%
> upper bound) and **better-than-commodity** (beats gloss self-verify at matched budget and
> FLOPs), scored against gold fixed by blind dual-judge adjudication the kernel never
> defined [MEASURED: registry/verdicts/f2b-transfer.json + Gate-A audit CONFIRM]. The win
> is attributable to the **kernel-AUTHORED aligned answer key** — NOT shown to require
> kernel-grade authoring (knull-v2/Δ_align unrun), NOT an efficiency headline
> (`noninferiority_vs_r3` FALSE: the 135M+verify arm was not shown to match 1.7B-alone on
> external gold), and scoped to ≤1.7B hosts, kernel-rendered templated definitional QA over
> the 108 covered concepts, k = 4, THIS gold standard [STIPULATED: the frozen extrapolation
> envelope, binding].

Everything else in the morning capstone's boundary picture SURVIVES VERBATIM: every
MEASURED crossing into real or natural INPUT still either FAILs or is INCONCLUSIVE
(l3a-parse 47.6% FAIL-safe; a5-nl 41.6% FAIL-dangerous with the S2 kill fired; g8 0/1000;
nsk1 INCONCLUSIVE) [MEASURED: each index-bound to its own verdict; the conjunction is
EXTRAPOLATION per ASM-0762, direction-only]. Stage-1/stage-2 crossed a different boundary —
**who fixes the gold**, not **what input reaches the system** — and one axis turning
positive while the other stays negative is the single most important structural fact of the
current evidence [INTERPRETIVE, following the stage-1 interpretation's axis contrast].

The honest one-line state: **the reachability-wall-on-coverage-wall stands; behind it, on
the covered, kernel-rendered slice, the content is now externally endorsed AND externally
load-bearing — and the programme's central question has mutated from "is the lift real?"
to "who must author what carries it, at what cost, and can anything reach it from natural
input?"** [INTERPRETIVE; each constituent cited below.]

---

## 1. The evidence wave, item by item, each in its own envelope

### 1.1 f2b-transfer stage 1 + stage 2 — the F2 line's circularity confound is discharged

- Stage 1 [MEASURED, FINAL]: blind external endorsement of the kernel's membership gold at
  A = 320/333 = 0.9610 (Wilson LB 0.9395 against the 0.70 kill bar; worst-case counterfactual
  over the 27 permanently-unresolved items 0.889/LB≈0.859). Human-anchored: every resolved
  label IS the kernel-naive human judge-1's, admitted by GPT-5.5 concordance or the
  conservative issue-#9 judge-3 rule. Caveats riding every citation [STIPULATED]:
  abstention-heavy unresolved set; judges 2/3 one model family.
- Stage 2 [MEASURED, PASS, audit-CONFIRMED]: primary +0.2507 on that external gold
  (BCa LB > 0, B = 10000); `shuffled_low_recovery` TRUE; `beats_gloss_self_verify` TRUE;
  **`noninferiority_vs_r3` FALSE** under a VALID separation gate; dual-scoring gap 0.0053
  (the external-gold lift and the membership-gold lift are the same lift to within half a
  point — the H-CIRC signature is not merely below threshold, it is absent); all instrument
  gates VALID; 3/3 seeds sign-consistent.
- What this adjudicates [DERIVED: the frozen H-CIRC disjunction applied to the two measured
  outcomes]: both of H-CIRC's registered falsification routes failed to fire. At this
  instance/rung/slice/gold, the definitional-circularity reading of the F2 lift is
  disconfirmed; the lift is real semantic contact.
- The honest unit of citation [STIPULATED: stage-2 interp rec. 4]: **"+0.2507 over itself;
  not shown to match 1.7B."** Splitting the pair overstates.
- What it does NOT touch [STIPULATED: envelope]: NL input (none appears anywhere in the
  design), coverage beyond 0.3542, question-style ecological validity (the verifier is
  MEASURED unable to engage public-benchmark surfaces — byte-identical verify/alone d-ext),
  PRM comparisons, scale beyond sign, other retry budgets, other gold standards.

### 1.2 DECONF-A1 — the runtime structure is inert; the value must live in the authored key

[MEASURED, EXPLORATORY pre-registration; the §3.1(c) replay component is a disclosed
answer-superset SUBSTITUTE whose soundness rests on an unmeasured code-level confluence
argument — discount to exactly that extent and no further.] C_dec = 1.0 exactly over
40,576/40,576 distinct decision cells (grid ∪ replay-substitute ∪ init-order), triage
NO-OBJECT, at R-1/135M pinned scope. Reading [STIPULATED: DECONF §3.2, extensional-decision
form only]: the kernel's structural fields (explication trees, primes, vectors, engine
hooks) change no runtime decision on the measured closure; every decision is extensionally
computable from the projected four-column label/gloss/claims answer key alone. NOT a
read-set proof; NOT a claim that kernel-authored content is generic (GS-A's strings ARE the
kernel's strings); NOT extendable beyond R-1/135M.

### 1.3 The composition — the two results bracket the mechanism, and it is clean

[INTERPRETIVE, adopted from the stage-2 interpretation §5; each input MEASURED as cited.]
A1 bounds the mechanism from ABOVE (nothing more than the projected answer key is consumed
at runtime); the shuffled control bounds it from BELOW (nothing less than the item-ALIGNED
key suffices — same bytes, same topology, same cost, wrong alignment → lift collapses);
stages 1+2 certify the remaining channel (the aligned key's content is externally true,
A = 0.961, and externally load-bearing, +0.2507). The story that survives all three results
simultaneously:

> **The kernel's runtime value is the item-aligned, externally-true, deterministic answer
> key it AUTHORS; the runtime channel that consumes it is thin and structurally generic;
> the lift is a property of verify-retry against that authored key.**

Attribution stops at "kernel-AUTHORED": nothing yet shows kernel-GRADE authoring is
necessary — that is knull-v2's authored-content channel and DECONF Stage B's Δ_align
contrast, both unrun [STIPULATED, carried verbatim].

### 1.4 g3 — the specific semantic pins are provisionally not-necessary, and this COMPOSES

- The frozen llmproxy-v3 verdict [MEASURED, weak proxy]: FAIL-analog, concordant necessity
  violations 36/195 = 0.1846 (LB 0.1433 > 0.10), instrument VALID. Response executed:
  Π-hardening paused, maintainer escalated, scoped to the proxy id.
- The human Pass-A hybrid [PROVISIONAL — human q1 authority × GPT-5.6 q2 stand-in; Pass B
  NOT DONE and is the sole adjudicator]: necessity 46/200 = 0.230, Wilson LB 0.1848 > 0.10 —
  the FAIL row matches, direction INVARIANT across two cross-family q2 sources, the
  decisive-only mapping, the pure-proxy leg, and the frozen proxy verdict. Sufficiency in
  the INCONCLUSIVE band.
- The proxy is now partially validated against the human [MEASURED]: human-vs-GPT-5.6 q1
  κ = 0.7561 (substantial band; validates only the q1 face — no human q2 exists yet).
- If Pass B confirms, the frozen consequence [STIPULATED: kill_criterion_verbatim] is:
  **defeasible-script stands, Π is lint, HS2 auto-resolves sidecar-only** — the kernel's
  clause-wise necessary-condition scripts, read literally, are NOT necessary for
  ordinary-usage truth on this slice.
- The composition with 1.1–1.3 [INTERPRETIVE, direction-only — never a premise]: this does
  NOT contradict the stage-1 endorsement; it refines the grain. Whole explications are
  externally endorsed as TRUE (0.961, whole-item grain); the clause-wise conditions are
  provisionally NOT individually NECESSARY (0.230 violation rate, clause grain). Content
  true-as-authored, pins defeasible-not-load-bearing: exactly the shape the
  aligned-answer-key reading predicts — the value is in the authored true content, not in a
  hardened clause-level semantic apparatus. A confirmed g3 FAIL would *converge with*, not
  undermine, the DECONF deflation. (Symmetric honesty: the instrument cannot distinguish
  script over-specification from common-mode LLM literalism even in the hybrid — the human
  q2 of Pass B is what removes that; and a Pass-B REVERSAL would break this convergence and
  must be folded if it lands.)

### 1.5 CODEVERT G0 — the strongest kernel-free vertical does not clear as designed

[MEASURED, non-scored spike, off-pool.] κ_q^indep = 0.4361 [0.3610, 0.5364] against the 0.5
G1 planning floor; package-source slice CI entirely below floor. The shortfall is
STRUCTURAL and annotation-proof: unrestricted '*' unknown call edges (22–869 per repo,
inherent to real Python under PY-STAT/1) zero callers-of (0/3,783) and instance-of (0/503)
on ALL six repos under the §2.2 repo-wide completeness precondition. The forward/lexical
subset clears at κ ≈ 0.72 (contains/contained-in exact at 1.00) and the instrument itself
validated (~$0, one bug caught and fixed on the pre-registered path). The asymmetric
summary [DERIVED, adopted]: **G0 killed a claim and validated a tool in the same run.**
The full-8-family product is measured-infeasible on this evidence (subject to the weak
chance the pinned G1 pool is atypically decorator-free [EXTRAPOLATION, conditional]); the
live choice is re-scope (forward/lexical subset; UNKNOWN-INCOMPLETE-as-answer; PY-STAT/2)
or drop — a maintainer design decision that re-enters the external review gate. The G1
annotation hours (candidate #1 in the steering's portfolio) must NOT be spent on the
full-8-family design [STIPULATED: G0 interp implication, endorsed].

### 1.6 Coverage census — the general index is demoted by measurement

[MEASURED κ + COMPUTED BOUND under a provisional pin.] The D3 upper-sieve census reads
κ = 0.6665 pooled (1033/1550) where the mapper-parse lane read 0/1550 — the cheap
kill-sound lane does NOT confirm the mapper zero, dissolving the free D3 domain kill as an
unconditional kill, and the sound-lane general-index ceiling comes out at Δ_max simUCB95 =
0.9860 ≫ δ_k = 0.03. Completing this census lane RAISED the ceiling. Read with the round-2
steering's "drop/dormant" call [OPINION]: the general index is demoted-by-measurement — no
cheap kill exists, the suite is not even fully enumerated (D1/D2/D5/D6 carry weight with
zero benchmarks), and the only defined tightening lane (the oracle census) is human-priced.
The coverage walls themselves stand unmoved [MEASURED: m0b 0.3542; g8 0/1000; define-lane
0/1550 on its own instrument; G0's inverse-family zeros].

### 1.7 The cascade reframe — CASC/1 as the unifying frame, and what it is not

[DESIGN, unfrozen; critique in flight; nothing here is evidence.] The maintainer's issue-#6
proposal, developed as H-CN: the kernel as the system's **internal representation** — a
large reasoner computes in the Option-A structured gloss (IR-soft with IR-hard checkable
islands), small naturalisers at both NL boundaries, the µs engine checking covered spans
mid-loop. Its significance for this synthesis is architectural coherence, not evidence:
it is the one frame in which every landed result keeps a role — DECONF's inert-structure
finding fits (the checker consumes the answer key; the cascade never claimed otherwise);
the stage-2 win is M4 (checked-seam accuracy-per-cost) measured at its narrow scope;
G0's forward/lexical subset is the routable substrate; NLB's FAILs are the binding front
gate; knull-v2 becomes the "which internal language" decider. Its own design document is
honest that the load-bearing bet (M2, reasoner-shrink over canonical dialect) is pure
EXTRAPOLATION with the one adjacent measurement (nsk1 text-delivered grounding) NEGATIVE
at scope, that the architecture is net-COST without M2, and that the double NL boundary
imposes a ~14.5% multiplicative accuracy tax at even gate-clearing seam values [DERIVED
there, planning-grade]. Under H-CN, issue #12 ("is the kernel becoming optional?") is
REFRAMED, not answered: the kernel cannot be optional if it is the internal language — but
the live question becomes *"does the internal language need to be KERNEL-structured, or
does any typed canonical dialect do?"*, which routes to exactly the same attribution
experiments (knull-v2/Δ_align; CASC-0 arm A5) [STIPULATED: ASM-1075 framing].

---

## 2. CORRECTNESS thesis — the evidenced state

> **STATE (not a verdict): INCONCLUSIVE-PENDING, unchanged as a call — but its internal
> geography has changed materially.** The thesis now has its first ground-truth-independent
> content positive (whole-item grain, covered slice) sitting beside an unmoved wall of
> input-boundary negatives and a provisional clause-grain necessity FAIL. SCOPE: kernel-v0/
> molecules-v0, ≤1.7B hosts, two verticals, the pinned front-end, the self-authored covered
> slice.

**MEASURED-positive:**
- The instrument: sound, fail-closed, µs, byte-identical across two verticals — l3a 600/600,
  a5 855/855, cross-vendor CONFIRMED [MEASURED; instrument-only, formalism-not-NSM-semantics].
- Content endorsement, whole-item grain: A = 0.9610 (LB 0.9395), blind, human-anchored, on
  the covered kernel-rendered slice [MEASURED: stage 1].
- Content load-bearing on external gold: +0.2507 with both controls, audit-CONFIRMED
  [MEASURED: stage 2] — evidence that what the kernel says about its covered concepts is
  true enough, by a standard it did not define, to lift a host against that same standard.
- Adjudication-instrument adequacy: truthstyle-2x2 PASS (style-robust at margin 0.10)
  [MEASURED, instrument-only].

**MEASURED-negative:**
- Every INPUT-boundary crossing: l3a-parse 47.6% FAIL (safe); a5-nl 41.6% FAIL (DANGEROUS,
  S2 kill fired); g8 0/1000; nsk1 text-channel net-harmful, internal channel unresolved
  [MEASURED, each in its envelope; conjunction EXTRAPOLATION].
- Coverage: 0.3542 (m0b, friendliest corpus, one incomplete instance); define-lane 0/1550
  on its instrument; G0 inverse-family zeros on real Python [MEASURED].
- Authoring capability, proxy grain: g9-llmproxy FAIL-analog (0.18 vs 0.34 bar) [MEASURED,
  weak proxy].

**PROVISIONAL-negative:**
- Clause-grain necessity: g3 hybrid 0.230 (LB 0.1848 > 0.10), FAIL-side, direction-invariant
  across four mappings; proxy q1 validated against the human at κ 0.756; human Pass B is the
  sole adjudicator [PROVISIONAL].

**UNMEASURED:**
- g2 (Π read-out soundness vs human gold) — the semantics core, still the decisive dark leg.
- Any NL-reaching parser (FK-NLB-3 class) clearing 0.90 retention + the S2 gate.
- The surface-realization layer (NSM gloss → scholarly English) — named, unbuilt, ungated.
- Human g9 (GATE-H authoring adjudication); human M0a.

**The shape, honestly** [INTERPRETIVE]: the correctness evidence is consolidating around a
*content* claim and away from a *semantic-apparatus* claim. What is externally validated is
that the kernel's authored records are TRUE of their concepts (stage 1) and USEFUL as a
checking authority (stage 2) — on the slice it covers, when addressed formally. What is
provisionally failing is the stronger claim that the kernel's clause-level necessary-
condition machinery is semantically load-bearing (g3), and what was already measured-inert
is that machinery's runtime consumption (DECONF-A1). If Pass B confirms, the defensible
correctness thesis contracts to: *a training-free engine over externally-endorsed authored
content, exact where covered, fail-closed off it, with defeasible (lint-grade) rather than
necessary clause semantics* — which is weaker than the founding ambition and stronger than
anything the programme could claim a week ago.

**Single most decisive remaining experiment (correctness):** **complete the human g3
(Pass B, then A2) and let it gate g2.** It is nearly free (one annotator pass), it converts
the largest PROVISIONAL in the registry to MEASURED, it adjudicates HS3 and fixes whether
Π is semantics or lint — i.e., it decides the *shape* of any future correctness claim — and
it prices the LLM-proxy instrument's q2 face for every downstream leg for free. (The
NL-reaching parser remains the *deployment*-decisive experiment, but it gates reachability,
not the thesis's content core; and it is a build, not a readout.) [DERIVED: ranking by
verdict-movement per hour under the steering's portfolio discipline; the maintainer's call.]

---

## 3. EFFICIENCY thesis — the evidenced state

> **STATE (not a verdict): INCONCLUSIVE-PENDING, unchanged as a call — with the mechanism
> leg now MEASURED-positive on honest gold and the headline leg MEASURED-not-established.**
> SCOPE: ≤1.7B hosts, kernel-rendered covered slice, k = 4, this gold standard.

**MEASURED-positive:**
- The verifier-offload MECHANISM on external gold: +0.2507 (135M+verify−135M-alone), engaged
  (gate proven), content-specific (shuffled <30% recovery), better-than-commodity (beats
  matched-budget gloss self-verify), audit-CONFIRMED [MEASURED: stage 2].
- The earlier membership-gold sign: f2b-replicate +0.1507 over 1.7B-alone at cost 0.103,
  audit-CONFIRMED — now understood, via DECONF-A1, as an aligned-answer-key property
  [MEASURED + STIPULATED reading].
- The byte premise: f1 6.74× [MEASURED, retainer-only]. The engine's µs cost [MEASURED].

**MEASURED-negative / not-established:**
- **`noninferiority_vs_r3` FALSE** [MEASURED: stage 2]: the headline "135M + kernel matches
  1.7B" had its pre-registered opportunity on honest gold under a valid separation gate and
  did not clear it (a failure to establish, not a measured shortfall). The membership-gold
  above-R3 reading does not carry to external gold on this corpus [EXTRAPOLATION contrast,
  direction-only].
- The compute-matched f2 primary FAILED; HE2 cascade-dominance dead at scope [MEASURED].
- The deterministic verifier measurably cannot engage public-benchmark surfaces
  (byte-identical d-ext vectors) [MEASURED].
- For any real deployment the line inherits the NL-boundary FAILs [MEASURED, composed
  direction-only].

**MEASURED-deflationary (attribution):**
- DECONF-A1: runtime structure inert; the lift's mechanism is verify-retry against the
  aligned authored key, kernel structure contributing nothing at the checker seam
  [MEASURED, exploratory, R-1 scope].

**UNMEASURED — the three open legs, unchanged in identity, raised in leverage:**
- **Attribution:** does the aligned key need kernel-GRADE authoring? knull-v2
  authored-content arm / DECONF Stage B Δ_align — unrun (plain-arm quality ruling open).
- **Mint cost:** A-F0, frozen, key-gated unrun.
- **Consumption:** A-E2's K-A3/K-A4 channel (the 18.5–41.7% figure remains a membership
  UPPER BOUND, never achievable savings) [MEASURED-exploratory, upper bound only].
- The cascade's M2 (reasoner-shrink over canonical dialect) — pure EXTRAPOLATION, priced by
  CASC-0 if/when frozen; γ, ρ_in, fid_R all unmeasured.

**The shape, honestly** [INTERPRETIVE]: the efficiency thesis has bifurcated. Its
*mechanism* form — "a small host plus a cheap deterministic verifier over an authored
aligned store gains real accuracy per cost on covered content" — is now measured, real, and
audit-confirmed at scope. Its *headline* form — "the small system replaces the big model" —
failed its first honest test at this rung pair, and its *economic* form (authoring cost vs
delivered value) is entirely unpriced. A thesis that gained one leg, failed to establish a
second, and holds three unmeasured cannot lawfully move [DERIVED: the capstone verdict
discipline applied, per the stage-2 interpretation].

**Single most decisive remaining experiment (efficiency):** **the attribution contrast —
knull-v2's authored-content arm / DECONF Stage B's Δ_align** (kernel-authored aligned key
vs independently-authored plain/generic aligned key, matched alignment and budget). Every
other reading now hangs on it: if generic authoring reproduces the lift, the efficiency
story is "aligned answer keys + retry" and the kernel's residual value is pushed entirely
onto authoring economics (A-F0) and the cascade's unmeasured M2; if it does not, the
kernel-content attribution is finally licensed and the +0.2507 becomes a kernel result
rather than an authored-store result. It is also the experiment the stage-2 interpretation
itself names as carrying more verdict-leverage per dollar than any replication
[STIPULATED, endorsed]. Precondition: the plain-arm quality ruling (ASM-0700 line), so the
control cannot confound one-sidedly.

---

## 4. Does the evidence point toward "small model + aligned authored store/checker"?

[INTERPRETIVE + EXTRAPOLATION throughout this section; direction-only; never a premise.]

Yes — directionally, and more strongly than at round 2. Every result of this wave is
CONSISTENT with that reading and none contradicts it:

- Stage 2 measured the small-model+store/checker system doing real, externally-scored work
  (the reading's affirmative half) while failing to match the big model (bounding its
  headline).
- DECONF-A1 located the runtime mechanism in the aligned authored key, not in kernel
  structure (the reading's deflationary half, from above).
- The shuffled control located it in ALIGNMENT specifically (from below).
- g3 provisionally removes the clause-grain semantic-pin apparatus from the load-bearing
  path — leaving authored true content, which is exactly what "aligned authored store"
  names.
- G0 shows even the kernel-free vertical succeeds only in its forward/lexical
  (store-like, provable) fragment — the success mode everywhere is *typed aligned stores
  with honest incompleteness*, not deep semantics.
- The cascade design gives the reading an architectural future in which the store/dialect
  is the internal medium rather than a runtime add-on.

But the reading is NOT adjudicated, and this document does not declare it. Three things
separate "points toward" from "established": (i) the attribution contrast is unrun —
"aligned authored store" vs "aligned KERNEL store" is precisely the open Δ_align question;
(ii) whether the store's authoring must be kernel-disciplined to be externally TRUE at
0.961 is untested (blind endorsement was measured for kernel-authored content only — no
generic-authored arm has ever faced the same judges); (iii) the whole reading currently
lives behind the NL wall — a store/checker no natural input can address is an internal
instrument whatever its alignment. The round-2 steering's decision B stands verbatim: if
"small model + aligned authored store/checker" is the programme's emerging success story,
it should be **decided, not drifted into** — and the deciding experiments are exactly the
critical path above (knull-v2/Δ_align; g3 Pass B → g2; then NLB) [OPINION adopted from
round2-steering; the decision is the maintainer's].

---

## 5. The critical path, consolidated

In verdict-leverage order, with blockers [DERIVED: portfolio ranking; maintainer-gated]:

1. **g3 human Pass B** (cheap; converts PROVISIONAL→MEASURED; gates g2; decides the shape
   of the correctness claim; prices the proxy's q2 face).
2. **knull-v2 plain-arm ruling → the authored-content/Δ_align attribution run** (the
   efficiency decider; ~$0–250 class).
3. **g2** (Π-soundness vs human gold; the correctness semantics core; behind 1).
4. **The CODEVERT re-scope decision** (maintainer; before ANY G1 annotation hour; options
   (a)/(b)/(c)/(d) per the G0 interpretation — the full-8-family G1 spend is not
   justifiable on current evidence).
5. **CASC-0** (if the in-flight critique survives review and the maintainer freezes it:
   ≤15 free GPU-h; prices M2 and fid_R, the two mechanisms no record touches).
6. **A-F0** (mint economics; key-gated) and the A-E2 consumption channel — the pricing legs
   any eventual efficiency verdict needs.
7. Mechanical hygiene now owed: update `registry/verdicts/f2b-transfer.json` audit field to
   CONFIRMED with the audit path; apply the §7 capstone delta of the stage-2 interpretation
   (done here, v3); run the stage-2-runner-vs-A1 pin comparison; register DECONF.

The binding constraint has CHANGED since the morning capstone: it is no longer "human
annotation everywhere" — the f2b-transfer line discharged its human dependency entirely and
read out. The remaining binding constraints are **one annotator pass (g3 Pass B), one
quality ruling (knull plain arm), one maintainer design decision (CODEVERT re-scope), and
one API key (A-F0)** [DERIVED from the ledger states cited above].

---

## 6. Bottom line

LOAD-BEARING: [STIPULATED: ASM-1240] Neither thesis is dead; neither is established; neither moves off
INCONCLUSIVE-PENDING on this wave — and this synthesis declares nothing beyond that state.
What the wave changed is the *content* of the pending question. CORRECTNESS now reads:
instrument exact and confirmed; authored content externally endorsed (0.961) and externally
load-bearing (+0.2507, audit-confirmed) on the covered rendered slice; clause-grain
necessity provisionally failing; every natural-input crossing still negative; semantics
core (g2) unrun. EFFICIENCY now reads: mechanism measured-positive on honest gold;
headline (match-the-1.7B) measured-not-established; attribution, mint-cost, and consumption
unmeasured; runtime structure measured-inert. The accumulated evidence points, direction-
only, at a narrower and more conventional success story — **a small model plus an aligned,
authored, externally-true store and a deterministic checker, with the kernel as one
measured way to author that store and possibly (per the cascade reframe) as the system's
internal language** — and the experiments that would convert that pointer into a programme
verdict are few, cheap, named, and mostly waiting on one annotator pass, one control
rewrite, and one design decision [INTERPRETIVE; every constituent MEASURED/PROVISIONAL/
STIPULATED as cited above; g2 and the CASC/1 critique fold in when they land].

---

## Epistemic register (what this synthesis relied on)

- **MEASURED, never widened, never recomputed:** stage-2 verdict figures (+0.2507;
  shuffled_low_recovery TRUE; beats_gloss_self_verify TRUE; noninferiority_vs_r3 FALSE;
  dual_scoring_gap 0.0053; gates VALID) from registry/verdicts/f2b-transfer.json via its
  interpretation; the Gate-A audit CONFIRM from registry/audit-status.jsonl +
  registry/audits/f2b-transfer/1-gate-a-codex.json (result field read at source);
  stage-1 FINAL (A = 0.9610, LB 0.9395) and its caveat enumerations; DECONF-A1
  (C_dec = 1.0, 40,576/40,576, exploratory, substitution disclosure); codevert-g0
  (κ 0.4361 [0.3610, 0.5364]; family split 1.00/0.72/0.00; 0/3,783 and 0/503); the g3
  llmproxy-v3 verdict (0.1846, LB 0.1433) and the human-vs-proxy κ 0.7561; the coverage
  census (sieve κ 0.6665; ceiling 0.9860 as COMPUTED BOUND); every morning-capstone figure
  restated (l3a/a5/l3a-parse/a5-nl/g8/nsk1/f2/f2b-replicate/f1/a-e2/m0b), each inside its
  own envelope.
- **PROVISIONAL:** every g3 hybrid quantity (necessity 0.230, LB 0.1848; sufficiency band) —
  human q1 × proxy q2; human Pass B is the sole adjudicator and its outcome binds this
  document's §1.4/§2 readings.
- **STIPULATED, adopted verbatim:** the stage-2 extrapolation envelope and its
  one-confound-removed clause; the §5 attribution wording ("kernel-AUTHORED", necessity
  unresolved); the honest-citation pairing rule (+0.2507 / noninferiority FALSE together);
  the DECONF §3.2 extensional reading and its riders; the g3 kill-criterion consequence
  text; ASM-0550 weak-proxy law; ASM-0762's conjunction-is-extrapolation law; the G0
  implication block; the CASC/1 ASM-1070–1079 framings (design-only).
- **DERIVED (this document's rule-application, disclosed):** the §0 governing-sentence
  revision (the morning capstone's own maintenance discipline applied on audit
  confirmation); the §2/§3 MEASURED/UNMEASURED ledgers; the §5 critical-path ranking and
  binding-constraint restatement; the verdict-object-vs-ledger audit-field inconsistency
  flag.
- **INTERPRETIVE (this document's, never a fact of any record):** the §1.3 bracketing
  composition (adopted from the stage-2 interpretation and endorsed); the §1.4 grain
  refinement (endorsed-true / pins-not-necessary); the §2/§3 "shape" paragraphs; §4 in its
  entirety.
- **EXTRAPOLATION/OPINION (direction-only, load-bearing for nothing):** every
  cross-experiment conjunction; the G0 pinned-pool prediction; the membership-vs-external
  R3 contrast; the "small model + aligned authored store" pointer; all steering-note
  material.

*This synthesis changes no frozen object, no verdict, no audit, no log, and no registered
assumption. It supersedes docs/next/feasibility-synthesis.md as the standing capstone and
is itself to be superseded — not edited — when g2, the human g3 Pass B, or the CASC/1
critique lands, or if the stage-2 audit state is ever revised.*
