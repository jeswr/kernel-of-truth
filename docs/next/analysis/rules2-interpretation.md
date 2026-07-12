# RULES-2 PASS — interpretation (Fable)

**Role: Fable INTERPRETATION agent, 2026-07-12. This document interprets the
completed and graded RULES-2 GPU campaign (train-time closure
internalisation) inside its frozen extrapolation envelope. It states NO
feasibility conclusion on either thesis — that synthesis belongs to the
cross-experiment feasibility node — and it modifies no mechanical verdict:
the readout below is the pinned `analysis/rules_2_go.py` output, and the
verdict artifact plus cross-model audit remain the owning roles' steps.**
Companion to `docs/next/analysis/rules1c-instrument-invalid-interpretation.md`
(the predecessor instrument post-mortem),
`docs/next/analysis/correctness-track-instrument-assessment.md` (the
five-instrument ledger), `docs/next/interpretations/deconf-b.md` (the
content-not-structure precedent), and `docs/next/feasibility-synthesis-v6.md`
§2 (the pre-result correctness-thesis state this campaign now updates).

Epistemic tags: **[MECHANICAL]** = the pinned-analysis output, reported
verbatim (recomputed this tick from the merged campaign bytes); **[MEASURED]**
= read directly from committed bytes (records, manifests, sibling artifacts)
this tick; **[DERIVED]** = follows from measured bytes by stated arithmetic,
wrong if the reading is; **[ASSESSMENT]** = this agent's judgment, one
model's opinion; **[EXTRAPOLATION]** = forward claim, never evidence;
**[UNRESOLVED]** = deliberately left to the owning role.

**Sources read at source this tick:** `registry/experiments/rules-2.json`
(status FROZEN, frozen sha `dde1b0d1…`); the pinned analysis
`analysis/rules_2_go.py` (sha `58b4831f…`) executed against
`poc/rules-2/results-incoming/campaign-20260712-195226/merged/`
(`results-rules2.json` sha `c904005a…`, outcome HARNESS-COMPLETE,
16,662 rows, `pins_verified: true`; `run-records-rules2.jsonl` sha
`e3981c8e…`) and `poc/rules-2/results/c8-result.json` (sha `674b424f…`);
`poc/rules-2/results/knull-analog-result.json` (sha `afcf09e8…`);
`poc/rules-2/asm-go-1847-1859.json` (ASM-1848..1852);
`registry/verdicts/f2b-transfer.json` and `registry/verdicts/deconf-b.json`
(both PASS); the four companion documents above.

---

## 0. The mechanical readout [MECHANICAL]

All four instrument gates valid — the rules lane's first fully green gate
vector:

| gate | value |
|---|---|
| pin_gate_valid (G1) | TRUE |
| c8_lookup_gate_valid (G2: 0/858 recovered ≤ 0.10 ceiling) | TRUE |
| headroom_valid (G3: B0 = 0.657 ≤ 0.85) | TRUE |
| repeat_byte_identical (G4) | TRUE |

Primary (B2 − B0 on S-out entailed cells, rung R1, 858 fresh-name items ×
3 FT seeds, two-stage FT-seed × item BCa bootstrap, B = 10,000, seed
20260712): point estimate **+0.343** (1.000 − 0.657), **LB95 = +0.3159**.
Registered band: PASS iff LB95 > SESOI 0.05. `primary_pass = TRUE`;
`kill_d_fired = FALSE`.

Per-arm S-out accuracy (R1 unless noted; chance floor 0.5, disclosed):

| arm | role | S-out acc | refusal correctness (100 control items) |
|---|---|---|---|
| B0 | plain host, no FT | 0.6573 | 0.000 |
| B1 | exposure control (stated + refusal only) | 0.0000 | 1.000 |
| **B2** | **treatment (stated + closure + refusal)** | **1.0000** | 0.007 |
| B3 | proof-augmented variant (descriptive) | 0.0000 | 0.883 |
| B5 | 1.7B no-FT comparator (R3) | 0.9277 | 0.030 |
| c1p | forced-flip deranged closure | 0.0000 | 0.883 |

FT-seed variance: range 0.000 in every fine-tuned arm; B2 = 1.000 at each
of seeds 0/1/2.

Holm step-down over {s1′, s2′, s4′} at family α = 0.05:
s1′ (deranged-closure recovery < 0.30): recovery UB95 = **−1.707**,
adjusted p = 0.0003, **rejected → s1p_pass = TRUE**.
s2′ (B2 − B1 > 0): LB95 = **1.000**, adjusted p = 0.0003, **rejected →
s2p_pass = TRUE**.
s4′ (degradation guard, intersection-union): stated-cell Δ = 0.000 but
refusal Δ = **−0.9933** vs the point-estimate-better reference (B1);
p = 0.995, **not rejected → s4p_pass = FALSE**,
`s4p_side_effect_flag = TRUE`.

Under the frozen `verdict_rules` this maps: INSTRUMENT-INVALID no (gates
green) → FAIL no (KILL-d not fired) → **PASS** (primary ∧ s1′ ∧ s2′). s4′
does not enter the PASS rule; its registered consequence is a cap on
deployment-shaped language (§1.4). The verdict artifact
(`registry/verdicts/rules-2.json`) and the cross-model audit are pending and
belong to the verdict-gen and auditor roles. [MECHANICAL; UNRESOLVED for the
artifact]

Descriptive spend: ~6.05 GPU-h ≈ $6.65 measured (A10G at the assumed
$1.1/h), 6.12 h wall, vs the $18 cap. Rungs executed: R1 (fine-tuned) and
R3 (eval-only comparator); the authorized R2 (360M) tier is **not** in this
campaign's merged results — one fine-tuned rung, `scale_language_max:
"none"`. [MEASURED]

---

## 1. What the PASS licenses [MEASURED / verdict-grade, at scope]

### 1.1 The licensed sentence

**Fine-tuning a small host on engine-derived entailments beats training on
stated facts — at this scope.** Precisely: LoRA fine-tuning SmolLM2-135M on
the certified engine's materialised closure (entity-form QA over the closed
kinship inventory) internalises the inference pattern to the resolution of
this instrument: out-of-world entailed accuracy 1.000 vs 0.657 for the plain
host (LB95 lift +0.316, > 6× the registered SESOI of 0.05), with no engine
at inference; the lift is closure-**content**-driven (s1′: the forced-flip
deranged closure at identical bulk collapses to 0.000, recovery UB95
−1.707 ≪ 0.30); it exceeds format/domain exposure (s2′: B2 − B1 LB95 =
1.000); and it is not reproducible by flat lookup over the training bytes
(c8: 0/858 S-out answers recovered, eval names token-disjoint from training
names). The pre-registered triangulation for "internalised the inference"
— S-out lift ∧ c8 non-reproduction ∧ c1p collapse — is met in full.
[MECHANICAL + MEASURED]

The claim carrier is S-out only. B2's S-mem = S-held = 1.000 are reported
separately and never pooled; S-mem is lookup-in-weights by frozen
assignment (ASM-1423), and S-held carries its disclosed cover-cell
string-recoverability caveat (ASM-1444). [MEASURED, frozen assignment]

### 1.2 First valid affirmative on the host-integration question

This is the **first non-instrument-invalid affirmative result the rules /
host-integration lane has produced** — after rules-1 (VOID, elicitation),
rules-1-b (superseded pre-GPU, form-dead), and rules-1-c
(INSTRUMENT-INVALID, verifier never engaged). It is *not* the correctness
track's first valid affirmative overall (f2b-transfer +0.2507 and DECONF-B
Δ_align +0.270, both PASS audit-CONFIRMED, precede it in the memory/checker
lane); it is the first time the engine's *output reaching a host* — here by
weight change — has been measured through a valid instrument, in either
direction. Synthesis v6 §2.3 pre-registered the reading discipline for
exactly this event ("a single valid affirmative result flips the ledger …
and re-opens the attribution chain"); executing that flip is the next
synthesis's job, not this document's. [MEASURED history; ASSESSMENT on
status; UNRESOLVED for the synthesis]

### 1.3 The arm anatomy behind the headline, honestly

- **B2 sits at ceiling.** 1.000 across all 2,574 S-out scorings and all
  three seeds. The instrument's measurable window above B0 was 0.343 wide
  and B2 consumed all of it; LB95 (+0.316) is within 0.027 of the
  saturation point. The obvious leak suspects are gated: lookup leakage by
  c8 (0/858, token-disjoint names, planted-exploiter teeth demonstrated in
  the blocking pilot's IP-2), content-independence by c1p, exposure by B1,
  and prompt-surface drift by the shared byte-identical prompt sha. What
  ceiling saturation still costs is *magnitude* language: "how much better"
  is truncated from above by this surface (§3.2). [MEASURED; DERIVED]
- **B1 collapsed to an always-refuser** (S-out 0.000; refusal correctness
  1.000): fine-tuned on stated facts + refusal only, it refuses entailed
  queries whose support facts are in its prompt — descriptively **worse
  than no fine-tuning at all** (B1 − B0 = −0.657). The s2′ pass is
  mechanically sound, but its magnitude (LB95 = 1.0) owes as much to the
  exposure control's refusal collapse as to B2's competence; the design's
  idealised "saw the format but not the inference" comparator behaviourally
  degenerated. This does not touch the primary, which is against B0.
  [MEASURED; ASSESSMENT]
- **c1p collapsed to 0.000**, as the content hypothesis requires. Its
  collapse mode is over-determined by construction: the forced flip is
  anti-correlated, so "learned the wrong mapping" and "content destroyed"
  both predict 0.0 — which is why the registered DESIGN-OPEN ASM-1806 (the
  pick-the-non-bridge shortcut cannot be fully separated from closure
  content by this control) **survives the PASS** and travels with the
  content claim. [MEASURED; frozen disclosure]
- **B3 (proof-augmented training) collapsed** (S-out 0.000, refusal-heavy
  at 0.883; B3 − B2 = −1.0, descriptive only per MD-R2-4). A plausible
  mechanism is train/eval surface mismatch — the why() proof block exists
  only in training prompts — but that is [ASSESSMENT]; the registered
  status is a descriptive negative for rationale-distillation scaffolding
  at this scale, nothing more.
- **B5 (1.7B, no fine-tune) reached 0.9277.** Descriptively, the fine-tuned
  135M (1.000) matches-or-exceeds a ~12.6×-parameter host on this closed
  surface at ~1/12.7 the per-query formula-FLOPs (8.78e10 vs 1.12e12) and
  ~1/8 the eval peak memory (874 MB vs 6.98 GB), for a one-off ~1.47 GPU-h
  / ~$1.61 LoRA cost plus 4.4 s CPU materialisation. No test is registered
  on B2 − B5; the efficiency ledger is a price table with **no direction
  presumed** (ASM-1429); the engine-at-inference price (5.3 µs/query) is a
  cross-campaign descriptive pointer and no break-even N* exists (B4
  struck). [MEASURED descriptives]

### 1.4 What s4′ failing means

The guard's stated-cell component is clean (Δ = 0.000: internalisation
training did not erode stated-fact accuracy). The refusal component breached
maximally: B2 correctly refuses **0.7%** of the 100 unanswerable control
items (vs its own training target — family-3 refusal data was in B2's
corpus — and vs B1's 1.000 reference). Two honest readings coexist. The
instrument reading: the frozen reference ("point-estimate-better of B0/B1")
selected a degenerate always-refuser, so the −0.993 delta partly reflects
the reference's pathology; B2 is no worse than the *base* host (B0 = 0.000)
at refusing. The substantive reading: after closure training the host
answers on virtually every unanswerable item — fail-closed behaviour did
not survive internalisation training, despite being trained. Under the
programme's honesty-first scoring direction (issue #18: wrong answers
penalised more than refusals), B2's control-cell behaviour is exactly the
failure mode that scoring exists to punish. The registered consequence
stands and is endorsed: **`s4p_side_effect_flag = TRUE` caps
deployment-shaped language** — nothing in this campaign licenses "a
fine-tuned small host can be fielded on this task", because fielding
requires the refusal behaviour this fine-tune destroyed. [MECHANICAL;
ASSESSMENT on the two readings]

---

## 2. The deflationary cap: content, not kernel structure [MEASURED, critical]

### 2.1 The knull analog closes the attribution question by construction

The mandatory sibling leg (rules-2-knull, $0 CPU, executed 2026-07-12,
artifact sha `afcf09e8…`; ASM-1849/1850) regenerated the entire rules-2
training corpus twice over the identical component set: once from the
kernel TBox, once from the knull **plain-dictionary** TBox. Result:
**fully surface-equivalent — 21,780/21,780 examples byte-equal** (family-2
closure cells 13,020/13,020 at fraction 1.0 across chain/cover/typing;
families 1+3 8,760/8,760; proof sidecars 0 divergent; identical exclusion
ledgers; kernel side anchored byte-equal to the pinned corpus
`c46aaa4e…`). The GPU knull arm is therefore conditional-vacuous and
prohibited (ASM-1851): its training bytes *are* B2's training bytes.

The consequence is not a caveat appended to the PASS; it is part of the
PASS's meaning, resolved before the campaign ran (ASM-1852, carried
verbatim in the frozen envelope): **on this closed inventory, the
plain-dictionary rules source derives the byte-identical training corpus,
so the measured lift is attributable to the entailment CONTENT the engine
materialised, and no rules-2 outcome — this PASS included — licenses
"kernel-specific value."** The claim ceiling is exactly: *engine-materialised
entailments, derivable from EITHER rules source on this closed inventory,
are internalisable by a small host.* The cap is two-sided: the byte-identity
neither validates nor indicts the kernel; it makes the kernel-vs-dictionary
question unaskable on this inventory. **RULES-2's PASS advances the
host-integration question and does not advance the kernel-SPECIFIC-value
question by any amount.** [MEASURED artifact; frozen cap]

### 2.2 The pattern this joins

This is now the fourth attribution probe to answer "content, not
structure," each at a different seam:

| probe | seam | deflationary observation |
|---|---|---|
| f2b-transfer (PASS, audit CONFIRMED) | in-context, verify-retry | +0.2507 lift carried by authored answer-bearing content |
| DECONF-B (PASS, audit CONFIRMED) | runtime store | GS-A projected store ≡ kernel arm, identity fraction 1.0; "alignment-specific, not kernel-specific" |
| CASC-0′ | prompt gloss | gloss ≡ plain at R2 |
| **rules-2-knull analog** | **training data** | **kernel-derived and dictionary-derived corpora byte-identical, 21,780/21,780** |

DECONF-B established that consuming the kernel *as a runtime object* adds
nothing over its projected answer store; the knull analog now establishes
that *deriving training data* from it adds nothing over a plain dictionary
— on inventories where both sources close to the same set. The mechanisms
differ (runtime identity vs derivation identity) but the surviving account
is uniform: **the measured value, wherever it has been measured, lives in
item-aligned, answer-bearing, engine-checkable content; no experiment has
yet detected value in the kernel's distinctive structure.** [MEASURED
verdicts + artifact; ASSESSMENT on the uniform account]

Where the question remains askable [EXTRAPOLATION, resolution path]: the
byte-identity is a fact about *this* closed kinship inventory, where a flat
dictionary already contains everything the kernel's structure contributes.
ASM-1851 pre-registers the re-activation condition: a fresh leg-1 artifact
showing corpus **divergence** — i.e., an inventory/domain rich enough that
kernel structure (e.g., UFO priors, cross-domain composition, the
large-scale kernel track's millions-of-concepts regime) derives entailments
a plain dictionary does not. Kernel-specific value must be sought where the
sources diverge; on inventories where they coincide, the question is closed
in the deflationary direction by construction.

---

## 3. Claim caps for the CORRECTNESS thesis

### 3.1 What this PASS does and does not license

**Does license** (verdict-grade, inside the frozen envelope):
1. Train-time internalisation of engine-materialised entailments by a 135M
   host, at this scope, with the s1′/s2′/c8 triangulation — the correctness
   thesis's host-integration slot has its first valid affirmative datum.
2. The engine's role as a **data product**: the certified closure
   (certificate 858/858 vs third-party gold) can be compiled into host
   weights that then answer fresh-name entailed queries without the engine
   at inference — on this inventory, at this form.
3. The instrument finding: the train-time channel instruments cleanly where
   three inference-time attempts could not (§4).

**Does not license:**
1. **Kernel-specific value** — capped permanently by the knull byte-identity
   (§2); the licensed subject is "engine-materialised entailments derivable
   from either rules source."
2. **Any scale claim** — one fine-tuned rung (R1); the R2 tier was
   authorized but not run; `scale_language_max = "none"`: not even a sign
   across scales.
3. **Any other question form, corpus, or domain** — entity form at the
   disclosed 0.5 chance floor only (the relation-word form is measured dead
   and nothing here rehabilitates it); this closed rule inventory, this
   kinship vertical, proof depth ≤ 4, corpus support-restricted to the
   3-name two-hop shape. "Internalised the inference" means *this closed
   inference pattern family, applied to fresh (token-disjoint) entities* —
   not inference in general.
4. **NL robustness** — gold-parse-only prompt-supplied facts; the l3a parse
   wall stands untouched.
5. **Other fine-tuning regimes** — LoRA at the pinned hyperparameters
   (r16/α32/lr2e-4/2 epochs, fp32) only.
6. **Deployment-shaped claims** — capped by `s4p_side_effect_flag` (§1.4):
   the fine-tune destroyed fail-closed refusal on unanswerables (0.007).
7. **Inference-time integration (verify-retry)** — struck as
   un-instrumentable at this operating point (ASM-1848); still unmeasured
   in both directions; this PASS answers a *different* question than
   rules-1 asked.
8. **Any feasibility conclusion** — explicitly outside this document's
   licence; the ledger update belongs to the next cross-experiment
   synthesis.

### 3.2 The SESOI / effect-size caveat

The registered decision band is a *paired-lift* criterion: PASS iff
LB95 > 0.05 absolute accuracy. The result clears it by more than a factor
of six (LB95 +0.316), so the PASS is not band-marginal. But two things
temper effect-size language. First, **ceiling truncation**: B2 saturated
the surface, so +0.343 is a *lower-bound-shaped* point estimate — the
instrument cannot say how much capability headroom remains above it, and
any "the effect is huge" reading generalised past this 2-option,
chance-0.5, closed-shape surface is uncapped extrapolation. Second, the
**surface's easiness is part of the effect**: at chance 0.5 with per-item
2-option anti-echo sets, a host that has internalised the (finite, closed)
mapping family can plausibly hit 1.000 without that implying comparable
lifts on open-vocabulary or deeper-chain surfaces. The honest magnitude
sentence is: *on this surface the effect is as large as the instrument can
measure; off this surface its size is unmeasured.* [DERIVED; ASSESSMENT]

### 3.3 Scope: single host, single corpus, single campaign

One base model fine-tuned (SmolLM2-135M @ pinned revision), one training
corpus (21,780 examples, one materialisation of one closure over one
inventory), one campaign (three FT seeds, zero seed variance — reassuring
for stability, but three seeds of one corpus is not a robustness
demonstration), one eval bank (858 S-out items from the strictly-eval-side
CLUTRR pin). Replication under corpus regeneration, another vertical, or
the 360M rung would each be a new record. [MEASURED scope; ASSESSMENT]

---

## 4. Why train-time succeeded where inference-time could not be instrumented

The rules host-lift lineage consumed three instruments without one valid
reading, each failing at a host-cooperation interface:

| iteration | failing interface | signature |
|---|---|---|
| rules-1 | elicitation (direction-unstated cue + menu) | all arms 0.000, oracle included; VOID |
| rules-1-b | task form (relation word, form-dead) | pilot A5 0/24; superseded pre-GPU |
| rules-1-c | verifier engagement (address-check defect atop the 2-option leak–vacuity dilemma) | attempts = 1 × 2,574, A3 ≡ c1; INSTRUMENT-INVALID |

rules-2 passed its gates on the first campaign, and the reason is
structural, not fortune. **The design removes the fragile cooperation
interface by construction.** An inference-time verify-retry instrument
needs a live, per-item, in-band dialogue between a 135M host and a
verifier: the host must propose parseably, the verifier must engage
non-vacuously without leaking the answer bit (jointly unsatisfiable at
n = 2, per the rules-1-c analysis), and the control arms must separate
feedback comprehension from resampling. Every one of those channels is a
place to die, and each iteration died at the first one not exercised at
the operating point. Train-time internalisation has none of them at
measurement time: the treatment is applied *offline* (a weight update from
a byte-pinned corpus the engine materialised once, deterministically), and
the measurement channel is the programme's most reliable primitive —
forced-choice string equality against the certified engine's gold. It is
the exact pattern the correctness-track assessment identified: every
experiment with a deterministic measurement channel has instrumented
cleanly (now six-for-six); every experiment requiring a runtime judgment
interface from the programme's smallest components has failed (still
zero-for-five on that side). rules-2 succeeded by moving the
host-integration question from the second class into the first.
[MEASURED history; ASSESSMENT]

Two further causes deserve explicit credit, because they are process, not
luck. First, the **blocking instrument pilot** (ASM-1830..1836's first
instance): every gate channel was exercised on real GPU at the operating
point before freeze — and it caught B4's verify-retry vacuity (IP-4,
attempts = 1 on all pilot rows), which was then *struck* rather than run,
converting what would have been a fourth decoy arm into a $0 design
decision. The c8 gate's teeth were likewise demonstrated (planted exploiter
fires, 55/60) rather than argued. Second, the **fail-closed pin discipline**
(hash-before-import, byte-identical prompt surfaces, shared-surface sha in
the results bytes) descends directly from the rules-1-c post-mortem's
finding that instruments fail at the first untested interface. The lane's
first valid reading arrived on the first design that tested every interface
it kept and deleted every interface it could not test. [MEASURED pilot
artifact + record; ASSESSMENT]

The honest converse: rules-2 does not vindicate the inference-time slot —
it *routes around* it. The verify-retry question (can a small host improve
its own answers under engine verification at inference?) remains
unmeasured in both directions, settled only as un-instrumentable at the
2-option operating point. If it ever matters independently, it needs the
rules-1-d design point (n ≥ 3 competitive distractors, k ≤ n−2, a
feedback-content control), which remains a paper design. [ASSESSMENT]

---

## 5. Residue and limitations of this reading

- The mechanical numbers were recomputed this tick by executing the pinned
  `rules_2_go.py` (sha-matched) against the merged campaign bytes; this
  document performed no independent row re-aggregation beyond that script,
  and the verdict artifact + audit are still pending [UNRESOLVED].
- B1/B3/c1p all collapsing to 0.000 S-out with high refusal is a
  *behavioural monoculture* worth one sentence of suspicion: three
  differently-trained arms found the same refusal attractor. Nothing in the
  gates is threatened by it (the arms' collapse directions are all
  design-consistent), but a replication where the exposure control retains
  some answering behaviour would make the s2′ magnitude more interpretable.
  [ASSESSMENT]
- The knull byte-identity is itself scope-bound: it was verified over this
  component set and TBox pair, deterministically. Any inventory change
  voids it and re-activates the GPU knull leg (ASM-1851). [MEASURED]
- Zero FT-seed variance at three seeds on a saturated arm carries little
  information about training stability off-ceiling. [DERIVED]
- Nothing here alters any frozen object, registers any assumption
  centrally (the companion ASM block is EMITTED for the coordinator), or
  issues any verdict; the assumption rows are
  `docs/next/analysis/asm-rules2interp-1930-1939.json` (ASM-1930..1939,
  owner writer-4).
