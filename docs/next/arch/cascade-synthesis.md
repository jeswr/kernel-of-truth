# P3-D-CASC-SYN — Synthesis: CASC/1 × GPT-5.6 critique — one honest recommendation

> **Status: [SYNTHESIS] — adjudication of the bidirectional design loop on the
> cascade-naturalisation architecture (H-CN). Inputs: the CASC/1 proposal
> (`docs/next/arch/cascade-naturalisation.md`, the maintainer's issue-#6 idea
> developed by the chief architect) and the GPT-5.6 external critique
> (`poc/gpt56-review/cascade-critique-20260711/last-message.json`). Nothing
> here is frozen, pre-registered, scheduled, or run; no verdict, audit, frozen
> object, or registry record is touched; no bead is created. §5 is a labelled
> OPINION/recommendation for the coordinator to surface to the maintainer —
> it is NOT a thesis conclusion.** Author: Fable, architecture-synthesis role,
> 2026-07-11.
>
> **Verification performed for this synthesis:** the critique's cost
> arithmetic was independently recomputed from CASC/1's own §3 identity
> (results in §4); the f2b-transfer citation was verified at source
> (`registry/verdicts/f2b-transfer.json`: `/analysis/effect_size` = +0.2507,
> `/analysis/holm/noninferiority_vs_r3` = **false**, audit state PENDING).
> The critique is arithmetically and factually correct on every checkable
> claim examined.
>
> Tag convention as in CASC/1: [MEASURED: ref] / [STIPULATED] / [ESTIMATED] /
> [DERIVED] / [EXTRAPOLATION] / and here additionally **[ADJUDICATION]** (this
> document's ruling on a critique point) and **[OPINION]** (the recommendation).

---

## 0. Verdict at a glance

The critique is substantially **upheld**. Its three core points are accepted:
(1) the M2 evidence register in CASC/1 understated adverse adjacent evidence —
the measured balance on M2 is not balanced, it leans negative; (2) CASC-0 as
designed cannot identify M2 and can manufacture an oracle-structured win — it
is a screen, not a decider; (3) the worked cost ratios were wrong (≈0.34×,
≈1.04×, verified) and "net-negative without M2" is not algebraically general —
the break-even INEQUALITY (§4) replaces the categorical claim. One critique
point is accepted only in part (the outbound fid_R seam is kept, but split and
deferred, §1.5).

**Recommendation in one line [OPINION]:** REDESIGN, don't shelve and don't
build — keep H-CN registered as a hypothesis, drop CASC-0, and run **CASC-0′**
(§3), a ≤15 GPU-h factorial M2 isolator whose single job is to measure the
sign of the size×medium interaction. Nothing else in the family (renderer
instrument, V-DEC, G3/G4 planning, beads) proceeds until that sign is known.

---

## 1. Adjudication of the critique, point by point

### 1.1 The M2 evidence register — ACCEPTED in full [ADJUDICATION]

The critique's decomposition is correct and CASC/1's register must be
rewritten to match it:

- **f2b supports M4, not M2.** f2b-replicate's +0.1507 at 0.103 cost is a
  cheap-verify/retry effect against an aligned deterministic answer key
  [MEASURED: registry/verdicts/f2b-replicate.json, does_not_license scope].
  It shows nothing about a small model *reasoning better in* a structured
  medium, which is what M2 asserts. CASC/1 cited it in the M2 ledger row as
  "adjacent"; the adjacency runs to M4 only.
- **DECONF-A1 sharpens this the wrong way for M2.** The effect survives with
  only the projected answer key; kernel runtime structure is INERT at the
  pinned F2 checker seam (C_dec = 1.0, 40,576/40,576) [MEASURED:
  docs/next/interpretations/deconf-a1.md]. So the one audited efficiency sign
  in the programme is *known* not to run through structure consumption.
- **f2b-transfer is the sharpest omission.** Verified at source for this
  synthesis: `noninferiority_vs_r3` = **false** (Holm secondary), alongside a
  real +0.2507 external-gold lift over the 135M host alone; audit PENDING
  [MEASURED: registry/verdicts/f2b-transfer.json, pass-pending-audit].
  Whatever the authoring/verdict race that kept this out of CASC/1's register
  (the verdict is stamped 18:47Z on the same day), the consequence stands:
  **the closest honest-gold measurement gave the "small + checking matches
  large" headline a live test and did NOT establish it.** That is not a
  refutation of H-CN — there was no internal structured medium in that
  experiment — but it is direct negative evidence against the exact premise
  M2 generalises.
- **nsk1 points the wrong way.** 0.76→0.43, 0/24 rescues, exploratory
  [MEASURED: registry/assessments/nsk1-g2d.json] is the only "supply kernel
  text to the model" measurement in the programme, and it is net-harmful at
  its scope.

**Corrected register, binding on all downstream CASC documents
[STIPULATED, this synthesis]:** *M2 is untested directly; the verifier
mechanism (M4) has a positive measured prior at narrow scope; the honest-gold
size comparison (f2b-transfer noninferiority, pending audit) and the closest
text-delivery measurement (nsk1) are both adverse; kernel-specific attribution
carries a strongly deflationary prior (DECONF-A1, the a5 structural caveat,
CODEVERT's kernel-free reading).* The phrase "the measured balance is roughly
balanced" and any equivalent framing is withdrawn.

### 1.2 CASC-0 is not decisive — ACCEPTED in full [ADJUDICATION]

Three independent defects, each sufficient:

1. **Confounded central contrast.** A3−A2 varies model scale, input
   representation, oracle canonicalisation, checking, output allocation, and
   rendering simultaneously. A4 removes checking only. No arm combination in
   the design identifies the size×medium interaction that *is* M2. A
   pre-registered "win" on this contrast would attribute to the architecture
   an effect that could live entirely in oracle-canonicalised inputs plus the
   already-measured M4 loop — an oracle-structured win without any reasoner
   shrinkage shown.
2. **Arithmetically infeasible cost contract.** A2 is defined as 1.7B+TTC at
   cost equal to A3, while the primary requires cost(A3) ≤ cost(A1) (one
   1.7B pass). Since cost(A2) ≥ cost(A1) by construction, the constraints
   coexist only at equality with ~zero TTC budget: the "strong generic
   baseline" self-destructs. [DERIVED, confirming the critique.]
3. **The central new instrument can't fail meaningfully.** fid_R is measured
   on an untuned renderer and K2 "blocks rather than kills" — an experiment
   whose novel component's bad result is pre-declared a floor-read cannot be
   called decisive. Additionally the procedural covered-record corpus is
   close to the ideal environment for the structured arm (held-out
   compositions control memorisation, not representation advantage).

CASC/1's own honesty machinery (ASM-1039 rule, the §7 threat list) named
several of these risks and then under-weighted them. Ruling: **CASC-0 as
specified in CASC/1 §6 is withdrawn as "decisive"; had it run unchanged it
would have been quarantined as a screen.** Replacement in §3.

### 1.3 Cost arithmetic — ACCEPTED, independently verified [ADJUDICATION]

Recomputed from CASC/1's own identity and worked point (L=1.7B, L′=360M,
S=135M, ρ_in=1.4, γ=0.3, r=0.3, T_in=T_out): **cost(CASC)/cost(MONO) = 0.336**
(not 0.25) with the shrink, and **1.042** (not 1.14) without it [DERIVED,
this synthesis; script re-run 2026-07-11]. Both of CASC/1's numbers were
wrong, in opposite directions. Two consequences, one against CASC/1 and one
mildly for it:

- Against: the with-shrink upside was overstated by ~35% relative.
- For: the no-shrink downside was overstated too — at the worked point the
  cascade without M2 is ≈ cost-*neutral* (+4%), not clearly net-negative.
  "Net-negative without M2" is therefore false as a categorical claim; with a
  sufficiently short core (γ small) M3 alone can carry a small saving.

The correct statement — and the only one any future CASC document may make —
is the break-even inequality of §4: **without M2 the cascade is at best a
trim; the maintainer's "substantially reduce the costs of larger models" goal
requires M2 specifically.** M2 remains the load-bearing bet for the *goal*;
it is no longer claimed load-bearing for bare break-even. Also accepted: the
parameter-ratio cost diagnostic is not a wall-clock/energy model across three
serial poorly-batched models; no planning saving is quotable before the
KOT-COST/2 vector is measured; ρ_in and γ convert to MEASURED in CASC-0′.

### 1.4 The boundary-tax identity — ACCEPTED [ADJUDICATION]

`ret_F × acc_core × fid_R` assumes conditional independence and ignores
off-path rescues and correlated failures; NLB's retention is retained covered
exactness for a *closed grammar and execution endpoint*, and NLB's own
compatibility rule denies transfer to CASC's open-vocabulary IR-soft output
space. Rulings: the "≈14.5% tax" is demoted to a planning scenario, never a
derived handicap; "F literally IS NLB-FE/1" is withdrawn in favour of "F is
an NLB-FE/1-CLASS component owing its own G3 leg on its own distribution";
"dead regardless of every other mechanism" is softened to "hard-gated on a
front end no measured instrument currently provides" — which preserves the
practically identical planning consequence (G3 stays behind G-NLB) without
the invalid identity. The qualitative point survives intact: the cascade pays
the NL boundary twice and the outbound direction is unmeasured programme-wide.

### 1.5 The outbound fid_R seam — ACCEPTED IN PART [ADJUDICATION]

The critique itself calls the outbound seam one of the design's best
contributions; kept. Accepted: mechanical claim-set diffing only works for
IR-hard islands; IR-soft prose needs semantic adjudication; the dangerous-
render rate must be measured unconditionally AND stratified by core
correctness (including deliberately incomplete/erroneous cores — the
deployment-relevant hallucination case `fid_R | core correct` misses); the
K2 band (co-primary LB ≥ 0.90 / kill < 0.85; UB < 0.02 / kill LB ≥ 0.02)
leaves an inconclusive region and must be closed at freeze. Ruling: the rear
seam becomes a **separate, later instrument** with the critique's five split
endpoints adopted verbatim, built only if CASC-0′ returns a positive M2 sign.
There is no reason to price a renderer for an architecture whose core bet may
die first — and removing the renderer from the M2 probe removes a confound.

### 1.6 Unification and the issue-#12 reframe — ACCEPTED [ADJUDICATION]

"All lines still useful" is downgraded from convergence to adjacency:
f2b/NLB/CODEVERT/knull are **adjacent components and controls with unmeasured
transfer assumptions**, not joint evidence for CASC. Step-grain verification
assumes intermediate claims are extractable, addressable, correct-keyed and
engine-checkable — none measured. And the issue-#12 reframe is a rename, not
an answer: declaring the kernel "the internal language" resolves optionality
by architecture choice, not empirical necessity; DECONF-A1 does not support
kernel-as-internal-language and if anything strengthens the generic-dialect
null. The live question — kernel dialect vs plain canonical dialect after
authoring and consumption costs — stays with knull-v2 and is carried in
CASC-0′ as a factor level, with the deflationary prior stated.

---

## 2. (a) Is CASC worth pursuing at all?

**Position [OPINION, with reasoning]: pursue exactly one step further — the
cheap M2 probe — and nothing else.** Neither of the two clean alternatives is
right:

- *Shelve outright?* Would be justified if probing M2 were expensive. It is
  not: the redesigned probe (§3) fits the same ≤15 GPU-h envelope the flawed
  CASC-0 claimed, uses only in-programme rungs (135M–1.7B), and its negative
  result closes the family at scope with pre-registered kills. Shelving
  without running it converts "adverse adjacent evidence" into "never
  measured", which is worse epistemics at zero savings. The proposal is also
  maintainer-directed: it deserves a measured answer, not a prior-only
  decline.
- *Pursue the architecture?* Indefensible on the corrected register (§1.1):
  the dominant mechanism has zero direct support, two adverse adjacent
  measurements, and one adverse pending-audit honest-gold test. Every
  downstream artifact (renderer instrument, V-DEC surgery, G3/G4 frames,
  FRONT comparator builds) is dead spend if M2's sign is negative.

So the family's status is: **speculative-until-the-M2-probe-reports, with the
probe now specified, cheap, and decisive at scope.** If CASC-0′ kills M2, the
family is shelved; V-DEC/V-LL do not unlock (a prefill-side saving without
reasoner shrinkage is the a-e2 upper bound of 18.5–41.7%, consumption
unmeasured — a trim, not the maintainer's goal); the kernel-as-internal-
language framing of issue #12 reverts to the knull-v2 channel.

---

## 3. (b) CASC-0′ — the redesigned minimal decisive M2 probe

**The critique's single most important fix, adopted with amendments
[STIPULATED, this synthesis]:** replace the six-arm cascade contrast with a
**factorial M2 isolator** that measures the size×medium interaction directly,
scored on the structured core BEFORE any renderer.

**Class:** G2 `oracle-diagnostic`, gold-dialect inbound (F not exercised;
composed analytically after, tagged EXTRAPOLATION), no W1/real-input claim,
ASM-0814 riders verbatim. Renderer and fid_R: **excluded** — separate later
instrument (§1.5).

**Factors and cells:**

| Factor | Levels |
|---|---|
| model size | 360M, 1.7B (in-programme rungs; sign-not-slope envelope) |
| medium | content-matched NL · Option-A kernel gloss · plain typed dialect (knull-grade) |
| verifier | off · on (structured mediums only — NL has no IR-hard islands) |

Cells: 2×3 base + 2×2 verifier-on = 10, plus one control cell (below). Same
paired item set throughout; content matched across mediums with per-medium
token counts measured (ρ_in becomes MEASURED); NL phrasings produced by the
same pinned protocol as the dialect renderings so the NL cells are not
disadvantaged by authoring quality; decoding/stop/max-tokens pinned per cell;
KOT-COST/2 vector measured per cell. Tuning symmetry (ASM-0852): all cells
stock, OR dialect-tuning matched by metered T_k on the NL side — decided and
budgeted at freeze; if tuning pushes the run over the envelope, the run is
re-labelled an *informative screen* in the prereg itself (the critique's
closing rule, adopted verbatim).

**Corpus:** the CLUTRR-shaped depth-2–4 engine-derivable generator from
CASC/1 §6, held-out compositions and depths, seed-pinned, self-authored/
covered rider disclosed. n ≈ 300–500 base items; power sized by the pinned
analysis script at freeze.

**The corrected cost-matched control (fixes the infeasible A2):** the
"just-more-compute" deflator lives at the SMALL scale, where cost-matching is
feasible: one cell of **360M-NL + TTC** with total measured cost matched to
the 360M-structured(+verifier) cell's measured total (retries included). The
old contract (1.7B+TTC at a sub-1.7B-pass budget) is arithmetically
impossible and is dropped; a 1.7B-NL+TTC reference MAY be co-reported at its
own cost, never as a matched baseline.

**Endpoints** (hierarchical cluster bootstrap over items preserving pairing;
Holm across the two structured mediums):

1. **Primary — the M2 sign:**
   `LCB95[ (acc(360M, medium) − acc(360M, NL)) − (acc(1.7B, medium) − acc(1.7B, NL)) ] > 0`
   for at least one structured medium. M2 *requires* a positive size×medium
   interaction — a small-model gain that the large model doesn't share — not
   merely a structured arm beating an incomparable NL system.
2. **Co-primary — practical shrink:** non-inferiority (pinned margin at
   freeze) of acc(360M, best structured medium, verifier on) vs
   acc(1.7B, NL), at measured cost strictly below the 1.7B-NL cell's. This
   is the honest successor to f2b-transfer's failed `noninferiority_vs_r3`,
   now WITH an internal structured medium — the exact thing that test lacked.
3. **Secondaries:** verifier main effect and verifier×size interaction (M4 at
   step grain); kernel-gloss vs plain-dialect TOST at pinned margin
   (attribution rung 2; deflationary prior disclosed); the 360M-NL+TTC
   deflator contrast; realised ρ_in, γ, r per cell (converting the §4
   inequality's inputs to MEASURED); deranged-store control on one
   verifier-on cell (house).

**Pre-registered kills:**

- **K1′ (M2 kill):** primary interaction LCB95 ≤ 0 for BOTH structured
  mediums AND co-primary NI fails → M2 dead at scope; **H-CN shelved;
  V-DEC/V-LL do not unlock**; the cost goal reverts to the a-e2 trim bound.
- **K2′ (compute-deflator kill):** 360M-structured within the pinned band of
  cost-matched 360M-NL+TTC → the medium effect is purchased compute; treated
  as K1′.
- **K3′ (attribution kill, non-fatal):** kernel-gloss ≈ plain-dialect within
  TOST band → kernel-content attribution dead at scope; any surviving family
  continues as a GENERIC structured cascade and the kernel claim routes to
  knull-v2/A-F0.

**Cost [ESTIMATED]:** ≤ ~15 GPU-h free pool + ≤ ~$25 — the removal of the
renderer and of the 1.7B TTC arm pays for the extra factorial cells; models
≤ 1.7B throughout; engine legs on the local box under standing
nice/checkpoint discipline. Re-estimated at freeze if tuning is included.

**What a pass licenses:** only that the M2 sign exists at oracle-inbound,
covered-corpus, ≤1.7B scope — the gate to build the renderer instrument and
plan G3 behind G-NLB. It licenses no W1 claim, no cost headline, no
kernel-attribution claim (that is K3′'s separate reading).

---

## 4. (c) The corrected cost model — the break-even inequality

Per routed item, normalised by c_L·T_in, with σ = c_S/c_L, λ = c_L′/c_L
(shrink factor; λ=1 = no shrink), ρ = ρ_in, γ = core/NL output ratio,
r = retry overhead, τ = T_out/T_in [DERIVED, replaces CASC/1 §3's worked
claims]:

```
cost(CASC)/cost(MONO) = [ σ(1+ρ) + λ(ρ + τγ(1+r)) + τσ(1+γ) ] / (1+τ)   (+ε_E ≈ 0)

Break-even  ⇔  λ ≤ λ* ≡ [ (1+τ) − σ(1+ρ) − τσ(1+γ) ] / [ ρ + τγ(1+r) ]
```

Verified worked values (τ=1, ρ=1.4, γ=0.3, r=0.3, σ=135/1700):

| quantity | CASC/1 claimed | correct |
|---|---|---|
| ratio at λ=360/1700 | ≈0.25 | **0.336** |
| ratio at λ=1 (no shrink) | ≈1.14 | **1.042** |
| λ* at the worked point | — | **0.953** |

Sensitivity of λ* [DERIVED]: γ=1 (no core compression) → λ* ≈ 0.61;
ρ=2, γ=1 → λ* ≈ 0.49. Readings, binding on any CASC prereg [STIPULATED]:

1. "Net-negative without M2" is **withdrawn** as categorical. At the worked
   point the no-shrink cascade is ≈ cost-neutral (+4%); with small measured γ
   it can carry a small M3 saving with λ=1.
2. What survives, stated as the inequality: the cascade's saving is
   monotone in λ below λ*; **without M2 (λ≈1) the achievable saving is a
   trim; the maintainer's substantial-cost-reduction goal requires λ ≪ λ***,
   i.e. requires M2. Whether M2 is needed for *any* saving depends on the
   measured (ρ_in, γ, r) — which CASC-0′ measures.
3. All of this is diagnostic-class parameter-ratio algebra: not wall-clock,
   not energy, not serving cost across three serial poorly-batched models
   with constrained decoding, loading, and KV traffic. No planning saving is
   quotable; the KOT-COST/2 vector measured per cell is the only binding
   figure.
4. The G1 routing-mass bound survives in form but its illustrative 0.26–0.34
   range is withdrawn (it multiplied cross-corpus routing shares by f2b's
   own-scope 0.103 — the critique's DROP item, accepted). G1 is recomputed
   per vertical from that vertical's own census numbers only.

---

## 5. (d) Recommendation to the maintainer — labelled OPINION

**[OPINION — Fable synthesis role. This is a recommendation about research
routing, not a thesis conclusion; every empirical statement above carries its
own tag and this section adds no new evidence.]**

**Recommendation: REDESIGN-THEN-DECIDE.** Specifically:

1. **Keep** H-CN registered as a maintainer-directed hypothesis. The idea is
   coherent, correctly identifies where kernel value would have to live after
   DECONF-A1 (an authored canonical checkable medium, not runtime structure
   at a checker), and its variant separation, lifecycle accounting, and
   outbound-safety seam are genuine contributions worth retaining regardless
   of outcome.
2. **Do not build** any part of the architecture now — no renderer, no
   V-DEC, no G3/G4 preparation, no family bead. The load-bearing bet (M2:
   structured canonical input lets a smaller reasoner match a larger one) has
   no direct support, and the three nearest measurements lean against it:
   f2b's effect is verify/retry-with-answer-key, not medium (DECONF-A1
   certified structure inert); f2b-transfer's honest-gold noninferiority vs
   the 1.7B anchor came back FALSE (pending audit); nsk1's text-delivered
   kernel grounding was net-harmful (0.76→0.43). Presenting M2 as an open
   coin-flip would misstate the record.
3. **Drop CASC-0 as specified** — it cannot identify M2 (confounded central
   contrast, infeasible A2 cost contract, untuned-renderer co-primary that
   blocks rather than kills) and a win from it would be an oracle-structured
   artifact.
4. **The single cheapest experiment that moves M2's probability is CASC-0′
   (§3):** a ≤15 GPU-h, ≤$25, in-programme (135M–1.7B) factorial — size
   {360M, 1.7B} × medium {matched NL, kernel gloss, plain dialect} ×
   verifier {off, on} — scored on the structured core before any renderer,
   with the M2 sign defined as a positive size×medium interaction, a
   cost-matched small-model TTC deflator, and pre-registered kills that
   shelve the family (without unlocking V-DEC/V-LL) if the sign is absent.
   Positive → build the renderer instrument and proceed to G3 behind G-NLB.
   Negative → shelve H-CN at scope; the cost goal reverts to the measured
   a-e2 prefill trim (18.5–41.7% upper bound, consumption unmeasured), and
   issue #12 stays with knull-v2.

Honest framing for the maintainer in one sentence: *your cascade is the right
shape for the value DECONF-A1 left standing, but its one decisive premise is
currently unmeasured-with-adverse-neighbours, and fifteen GPU-hours of
factorial measurement — not architecture-building — is what its probability
responds to next.*

---

## 6. Epistemic register of this synthesis

- **MEASURED (verified at source for this document):** f2b-transfer verdict
  — effect_size +0.2507, noninferiority_vs_r3 FALSE, audit PENDING, envelope
  verbatim on file [registry/verdicts/f2b-transfer.json]. All other MEASURED
  figures are restated from CASC/1 §8 strictly within their envelopes and
  were not re-verified here except as noted.
- **DERIVED (recomputed here, script run 2026-07-11):** cost ratios 0.336 /
  1.042; λ* = 0.953 (worked point), 0.61 (γ=1), 0.49 (ρ=2, γ=1); the
  break-even inequality of §4.
- **ADJUDICATION (this document's rulings):** §1.1–§1.6 — critique upheld in
  full on M2 register, CASC-0 non-decisiveness, cost arithmetic, boundary
  identity, unification downgrade; upheld in part on fid_R (seam kept, split
  and deferred).
- **STIPULATED (design choices made here, coordinator to register with the
  CASC block):** the corrected M2 register wording (§1.1); withdrawal of
  CASC-0-as-decisive (§1.2); the §4 inequality-publication rule superseding
  ASM-1073's categorical clause; CASC-0′'s factors, endpoints, kills, and
  the small-scale cost-matched deflator (§3); rear-seam deferral with the
  critique's five split endpoints (§1.5).
- **EXTRAPOLATION (unchanged, never premises):** ASM-1078 (M2) — resolver
  now CASC-0′ primary; ASM-1079 (joint boundary values) — resolver
  unchanged, composition demoted to conditional form per §1.4.
- **OPINION:** §5 only, labelled.

This document changes no frozen object, no verdict, no audit, no registry
entry; it proposes one redesigned bead-able experiment (CASC-0′) and routes
everything else behind its result. Next step per the standing loop:
coordinator surfaces §5 to the maintainer for routing.
