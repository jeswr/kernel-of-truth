# P3-D-CASC — CASC/1: the cascade-naturalisation architecture (H-CN), developed from the maintainer's issue-#6 proposal

> **Status: [DESIGN] — maintainer-proposed architecture, developed by the chief
> architect as a candidate for the EFFICIENCY thesis. Nothing here is frozen,
> pre-registered, scheduled, or run; no verdict, audit, frozen object, or
> registry record is touched; no bead is created by this document. This
> document is written FOR the bidirectional design loop: it goes to GPT-5.6
> for external critique next, and every assumption is stated explicitly so the
> critique can attack it.** Author: Fable, chief-architect role
> (`kern/fable-designer`), 2026-07-11.
>
> **Provenance of the proposal:** the maintainer, on issue #6 (the knull
> authoring fork), verbatim: *"use the current kernel everywhere internally;
> and then apply the concision later on — much closer to the end in just a
> select set of layers; or in the decoder. Since the primary goal here is to
> substantially reduce the costs of larger language models that are expensive
> to run; one option might be to have Option A [the full structured kernel
> gloss] used in the primary language model that is doing harder tasks such as
> reasoning, and then to have a much smaller model sitting in front of it that
> is doing the 'naturalisation'. I think this means that all lines of work are
> also still very useful at this stage."* This document is the serious
> development of that proposal, not a critique of it; the critique round is
> GPT-5.6's.
>
> **Steering-note compliance, stated up front:** round-2 steering says STOP
> further design cycles because results, not designs, are the scarce resource
> [ref: docs/next/analysis/round2-steering.md §5]. This document is the named
> exception that note allows for: a MAINTAINER-directed architecture requires
> a developed design before it can be critiqued, beaded, or declined. It
> proposes exactly ONE cheap experiment (CASC-0, §6), defers both invasive
> variants without beads, and displaces no dispatched work.
>
> **Inputs read at source, in full:**
> `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) — §0
> constraints, §1.2–§1.4 KOT-SIZE/2 / KOT-COST/2 / W1, §2 KOT-FAIR/2, §3
> family taxonomy, §4 gate ladder; `docs/next/analysis/round2-steering.md`;
> `docs/next/interpretations/deconf-a1.md` (rev 3, the complete certificate);
> `docs/next/design/NLB.md` (rev 2); `docs/next/design/CODEVERT.md` (rev 2);
> `docs/next/design/RAGC.md` (rev 2); `docs/next/design/FRONT.md` (rev 2);
> `poc/codevert-g0/RESULT.md` (the G0 spike readout).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[STIPULATED: id]` = a design choice made here or inherited — every design
> CHOICE in this document is STIPULATED, never MEASURED; `[PROPOSED-ASM: id]`
> = a design choice pending coordinator registration; `[ESTIMATED]` = a
> planning number with no measurement behind it; `[DERIVED]` = an analytic
> computation made in this document from cited measured inputs, disclosed as
> such; `[EXTRAPOLATION: id]` = a registered forward projection, **never a
> premise**. New stipulations live in the fresh block **PROPOSED-ASM
> ASM-1070…ASM-1079** (registry high-water at authoring time ASM-1059;
> 1060–1069 left free for in-flight waves; the coordinator registers this
> block append-only at commit and rebases the ids if a concurrent wave has
> claimed them — this document performs no registry edit).

---

## 0. One-paragraph summary

The maintainer's proposal is read as a **cascade / two-tier architecture,
H-CN**: a large, expensive model does the hard reasoning entirely over the
full kernel-structured representation (the Option-A structured gloss — the
kernel's verbose, typed, canonical text form), and the natural-language
surface is produced (and consumed) by a much smaller, cheaper
**naturalisation model** at the boundary — or, in the invasive variants, by a
select set of late layers or a kernel-native decoder vocabulary. This
REFRAMES issue #12: the kernel is not an optional runtime add-on whose
structure must earn its keep at a checker (DECONF-A1 measured that structure
runtime-INERT at the F2 checker seam); it is the candidate **internal
language of the system**, valued as an authored, canonical, checkable medium
— exactly the reading DECONF-A1's answer-key deflation leaves standing. The
efficiency claim decomposes into five mechanisms (§3): only one is measured
anywhere (the checked-seam verify-retry shape, f2b, at its confounded formal
scope), one has a measured upper bound (minted-vocabulary prefill savings,
a-e2, consumption unmeasured), and the central one — that a canonical
disambiguated input lets a smaller reasoner match a bigger one — is pure
EXTRAPOLATION, with the one adjacent measurement (nsk1 text-delivered
grounding) NEGATIVE at its scope. The architecture makes the NL boundary
load-bearing TWICE (inbound parse, outbound render); the outbound direction —
rendering fidelity — is unmeasured programme-wide and is the genuinely new
quantity this design introduces. The cheapest decisive step is **CASC-0**
(§6): a G2-class, oracle-inbound, six-arm paired contrast on engine-derivable
composition tasks that prices the two unmeasured mechanisms for ≤ ~15 free
GPU-h + ≤ ~$25, with pre-registered kills that can close the family before
any instrument build. No cheap experiment can license the WIN — that remains
a G4 claim under KOT-FAIR/2, behind NLB, and this document does not pretend
otherwise [STIPULATED: ASM-1070; the ASM-1039 honesty rule adopted].

---

## 1. The proposal, interpreted — three seams, one primary

"Option A" in the maintainer's text is the **full structured kernel gloss**:
the kernel record's verbose typed text rendering (canonical labels, explicit
roles, explicit claims), as opposed to the concise naturalised surface a
reader wants. The proposal keeps Option A as the medium of computation and
moves the concision to the edge. Three distinct seam placements are
consistent with the maintainer's words; they are different architectures with
different costs and different evidence exposure, and the design names them
rather than blending them [STIPULATED: ASM-1070]:

| Variant | Seam | What it is | Invasiveness | Status in this design |
|---|---|---|---|---|
| **V-C2** two-model cascade | serialized text between models | small naturaliser (110–360M) at the boundary; large reasoner (R-3 anchor class and up) computes entirely in Option-A dialect; deterministic engine checks covered spans mid-loop | none (no weight surgery; prompting + fine-tuning only) | **PRIMARY** — developed in full below |
| **V-DEC** decoder-vocabulary seam | tokenizer/embedding surgery | the reasoner reads/writes a kernel-native minted vocabulary (one token per concept URN); a small decode layer expands to NL — the consumption channel the a-e2 census upper-bounds | medium (vocabulary + embedding surgery, training required) | NAMED, DEFERRED — no bead proposed; unlocks only if V-C2 shows a positive core effect |
| **V-LL** late-layer concision | internal layers | one model whose lower stack computes over structured tokens and whose "select set of late layers" performs naturalisation | highest (architecture surgery; the H-RULE-HL/H-DD class) | NAMED, DEFERRED — deep-internal placements are steering-dormant [ref: round2-steering §6] and every measured deep-internal channel is unresolved-at-best [MEASURED: nsk1 readings per programme §0] |

Why V-C2 is primary [STIPULATED: ASM-1070]: it is the only variant buildable
from measured components (the NLB-FE/1 front-end class, the µs engine, the
f2b loop shape, stock checkpoints); it needs no invariance derivations or
surgery; its failure localises at typed text seams (the programme's only seam
class with a measured green — the verify-retry accept seam
[MEASURED: registry/verdicts/f2b-replicate.json]); and it is exactly the
maintainer's "much smaller model sitting in front of it" sentence. The
seam-discipline lesson is inherited from CODEVERT rev 2 §2.1: serialized,
typed, executable interfaces; no residual-stream delivery
[STIPULATED: ASM-1070, adopting the CASK/CODEVERT seam ruling].

### 1.1 The internal medium: IR-soft with IR-hard islands

A load-bearing distinction the proposal needs and the one-line version hides
[STIPULATED: ASM-1071]:

- **IR-hard** — the closed kernel/world grammars (kot-query/1,
  kot-query-code/1, the typed record surface). Exactly checkable by the µs
  engine; fail-closed; but coverage-walled: kernel-expressibility 0.3542 on
  the friendliest measured corpus, 0/1,000 random Mathlib declarations,
  0/1,550 define-lane census, κ_q^indep 0.4361 on real Python repos
  [MEASURED: programme §0 restated; poc/codevert-g0/RESULT.md §1].
- **IR-soft** — the Option-A structured GLOSS: templated, typed, canonical
  text (explicit roles, canonical labels, one claim per clause), open
  vocabulary. Not coverage-walled — anything sayable is sayable in it — but
  only the spans that ground into IR-hard records/queries are engine-checkable.

- DECISION: the cascade's internal medium is **IR-soft everywhere, with
  IR-hard islands wherever content grounds into covered records** — the
  reasoner computes in the gloss dialect; every claim that parses into
  IR-hard is engine-checked (accept/reject/abstain, fail-closed); unparsed
  gloss is carried unchecked and MARKED unchecked in the intermediate form
  [STIPULATED: ASM-1071]. Rationale: an IR-hard-only medium is dead on
  arrival at measured coverage (a system that can only think about 35–44% of
  content is not a general reasoner); an IR-soft-only medium abandons the one
  measured green (checkability). The islands construction keeps the
  fail-closed property exactly where it is licensed and degrades to
  "canonical dialect, no check" elsewhere. Consequence, stated honestly: the
  checkable fraction of internal traffic is a coverage-class number and every
  benefit of mechanism M4 below scales with it.

---

## 2. The architecture, concrete (V-C2)

```
user NL question
   │
   ├─► F  NATURALISER-IN (110–360M; the NLB-FE/1 class, extended)
   │      NL → Option-A dialect: canonical entity labels, explicit
   │      roles/directions, one claim per clause; IR-hard contracts emitted
   │      for every span that parses; calibrated abstain/CLARIFY on low
   │      confidence (the NLB acceptance stack, inherited whole)
   │
   ├─► L  REASONER (large: R-3 anchor 1.7B within programme scale;
   │      the maintainer's target class is larger still — out-of-programme
   │      rungs are maintainer-gated per §4/§6 of the programme)
   │      computes ENTIRELY in the Option-A dialect: chain-of-reasoning,
   │      intermediate claims, final answer all emitted as structured gloss
   │      with IR-hard islands
   │         │
   │         └─► E  ENGINE (µs, measured 5.29–7.82 µs/query
   │             [MEASURED: registry/verdicts/l3a.json + a5.json]):
   │             every IR-hard island checked as emitted; reject → bounded
   │             retry of the enclosing step (the f2b loop shape, k pinned);
   │             uncheckable spans pass through marked unchecked
   │
   ├─► R  NATURALISER-OUT (110–360M): structured answer core → fluent,
   │      concise NL; carries provenance markers; must NOT introduce
   │      content absent from the core (the dangerous-render bound, §6)
   │
   └─► NL answer to the user
```

Model size classes [STIPULATED: ASM-1071]: F and R are the 110–360M class —
F literally IS NLB-FE/1 on its vertical (the same measured component,
ASM-0945's consumer obligations apply verbatim: exact passed content-hash,
grammar compatibility, own G3 leg); R is a new component with no programme
precedent (§3.4). L is the rung anchor of the consuming rung (R-3 = 1.7B for
any in-programme G4; the "substantially reduce the costs of larger models"
aspiration targets L in the 7B+ class, which is an out-of-programme rung and
stays an aspiration until a rung exists for it). F and R may share weights
(one model, two directions) — a T_k-metered tuning choice, not an assumption.

Everything is inside the measured system: F, R, E, the store, retries, and
CLARIFY turns are all bytes on KOT-SIZE/2 figure-(1) and cost on the
KOT-COST/2 vector; nothing is free [STIPULATED: ASM-0808/ASM-0810 applied].

### 2.1 Where this sits in the H-* taxonomy

H-CN is a COMPOSITION, not a new mechanism: F = H-PS's front-end (NLB-gated);
E-in-the-loop = H-VL productised at the reasoning-step grain instead of the
answer grain; R is new. It is registered as a family because its CLAIM is
new — that the composition beats a matched monolith at equal budget — and
because the maintainer directed it. Its gates are the standard ladder: G1 =
the routing-mass paper bound (§5.1), G2 = CASC-0 (§6, oracle-inbound), G3 =
the NLB-gated natural-input rerun, G4 = the full FRONT/RAGC frame
[STIPULATED: ASM-1072, adopting ASM-0817].

---

## 3. The cost model — five mechanisms, priced and tagged

Let c_L, c_S be per-token inference cost of reasoner and naturaliser (the
neural-FLOP diagnostic gives c_L/c_S ≈ params ratio: 1.7B/135M ≈ 12.6,
1.7B/360M ≈ 4.7 [DERIVED from the ASM-0810 formula sheet; REPORTED-never-
BINDING — every binding cost figure is the measured KOT-COST/2 vector]).
T_in, T_out = NL token counts; ρ_in = structured-dialect tokens per NL token
for the same content on the reasoner's tokenizer; γ = structured answer-core
tokens / naturalised answer tokens; r = verify-retry overhead fraction;
s = the share of workload routable through the structured path at all.

**The ledger (who pays, who saves):**

| # | Mechanism | Sign | Term | Epistemic status |
|---|---|---|---|---|
| M1 | dialect token-count delta on the reasoner's input | **likely a COST in V-C2**: Option-A gloss is verbose by design, ρ_in ≥ 1 on a stock tokenizer [ESTIMATED]; becomes a saving ONLY under V-DEC minted vocabulary | c_L·(ρ_in−1)·T_in | a-e2 gives the V-DEC ceiling: prefill-savings MEMBERSHIP UPPER BOUND 18.5–24.0% (Qwen2.5) / 33.4–41.7% (SmolLM2) at the 10k-concept anchor, consumption channel UNMEASURED [MEASURED: registry/assessments/a-e2-census.json, upper bound only] |
| M2 | **reasoner shrink**: canonical, disambiguated, role-explicit input + checked loop lets a smaller L' match L on the task | saving: (c_L−c_L')·(everything L does) — the dominant term if real | — | **EXTRAPOLATION, the load-bearing bet** [EXTRAPOLATION: ASM-1078]. Adjacent measurements: f2b's 135M+loop beat 1.7B-alone at cost 0.103, formal inputs, alignment-confounded [MEASURED: registry/verdicts/f2b-replicate.json + assessments does_not_license]; nsk1 text-appended kernel grounding NET-HARMFUL at its scope (0.76→0.43, 0/24 rescues) [MEASURED: registry/assessments/nsk1-g2d.json, exploratory] — the one direct "give the model kernel text" read is NEGATIVE |
| M3 | **short-core decoding**: L emits the compact structured core (γ<1), R expands to fluent NL at c_S | saving on output: c_L·T_out·(1−γ) − c_S·T_out ⇒ ratio γ + c_S/c_L | worked point [ESTIMATED]: γ=0.3, c_S/c_L=0.08 → output-side cost ×0.38 | γ is UNMEASURED; note the direction: for family/world answer shapes the kernel gloss is often LONGER than a naturalised answer — M3 is real only where the naturalised surface carries fluency padding the core omits |
| M4 | **checked-seam accuracy per cost**: engine accept/reject converts cheap retries into accuracy on covered islands (accuracy bought at symbolic µs instead of neural tokens) | effective: fewer L-tokens per correct answer | engine 5.29–7.82 µs/query; f2b system cost ratio 0.103 with +0.1507 lift [MEASURED, at formal/self-authored/oracle-addressed scope; DECONF-A1: the mechanism is aligned-answer-key + retry, not kernel runtime structure] | MEASURED at its narrow scope; scales with island coverage (§1.1) |
| M5 | canonicalisation → cache/dedup: identical semantic queries collapse to identical dialect strings; prefix/KV cache hit rates rise | minor saving, workload-dependent | — | [ESTIMATED]; real in serving practice, never decisive; measured only under the KOT-COST/2 warm/cold protocol |

**The composed cost identity** (per routed item; the algebra is
diagnostic-class, never binding) [DERIVED]:

```
cost(CASC) = c_S·(T_in + ρ_in·T_in)              # F: read NL, write dialect
           + c_L'·(ρ_in·T_in + γ·T_out·(1+r))    # L': read dialect, write core, retries
           + ε_E                                  # engine: µs-class, measured ≈ free
           + c_S·(γ·T_out + T_out)               # R: read core, write NL
cost(MONO) = c_L·(T_in + T_out)
```

With the worked planning point (all [ESTIMATED]): L=1.7B, L'=360M, S=135M,
ρ_in=1.4, γ=0.3, r=0.3, T_in=T_out — cost(CASC)/cost(MONO) ≈ 0.25. The
entire plausibility of that number rests on M2 (L'=360M sufficing where
L=1.7B was needed); set L'=L and the ratio is ≈ 1.14 — **without the
reasoner shrink the cascade is a net cost INCREASE in V-C2**, because M1 is
adverse and M3+M5 are small. That is the honest shape of the bet: M4 is
measured-but-narrow, M2 is the thesis, everything else is trim
[STIPULATED: ASM-1073 — this framing is binding on any CASC prereg: no
cost-saving claim may be attributed to the architecture without naming which
mechanism carried it and citing its measured status].

### 3.1 The accuracy identity — the boundary tax, quantified

The cascade pays the NL boundary TWICE. End-to-end accuracy on routed items
factorises (to first order, ignoring rescue correlations) [DERIVED]:

```
acc(CASC) ≈ ret_F × acc_L'(dialect) × fid_R
```

where ret_F = inbound retention (NLB's gate quantity), acc_L'(dialect) = the
reasoner's task accuracy over the dialect, fid_R = **rendering fidelity**
(P(NL surface preserves the core | core correct)) — the outbound seam
quantity, UNMEASURED programme-wide. Consequences:

- At today's measured front-ends (ret_F 0.42–0.48
  [MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json]) the cascade is
  DEAD on real natural input regardless of every other mechanism. H-CN is
  therefore hard-gated on NLB clearing 0.90, which is itself an unresolved
  projection [EXTRAPOLATION: ASM-0906, inherited].
- Even at gate-clearing values (ret_F=0.90, fid_R=0.95) the boundary tax is
  ≈ 14.5% multiplicative: **M2's accuracy-per-cost gain must exceed a
  ~14.5% accuracy handicap before the cascade breaks even with a monolith
  that pays no boundary tax at all** [DERIVED; planning-grade]. This single
  line is the strongest a-priori argument AGAINST the architecture and any
  prereg must display it.
- fid_R has a safety dimension the programme has never measured: a fluent
  renderer that asserts content absent from the core is the outbound
  analogue of a5-nl's S2 wrong-with-provenance. The **dangerous-render
  bound** (UB95 < 0.02, mirroring G-NLB clause 2) is introduced here as the
  rear seam's gate quantity [PROPOSED-ASM: ASM-1074].

### 3.2 What DECONF-A1 does to this design — the issue-#12 reframe, stated exactly

DECONF-A1 (complete certificate, C_dec = 1.0 over 40,576/40,576) measured
that at the pinned F2 checker seam the kernel's structural fields are
runtime-INERT: the store functioned as an aligned deterministic answer key
and nothing else, at R-1/135M scope [MEASURED:
docs/next/interpretations/deconf-a1.md §0–§1, exploratory pre-registration].
Read against H-CN:

- It does NOT contradict the cascade: A1 quantifies over the CHECKER's
  information diet, not over what a reasoner does with a structured medium.
  The cascade never claims the checker consumes structure; its checker is
  the same answer-key-consuming engine A1 certified.
- It FITS the cascade's value story: if the kernel's runtime value is "one
  way to author an aligned, canonical, checkable representation", then the
  natural home for that value is as the system's internal representation —
  which is precisely the maintainer's proposal. H-CN relocates the kernel
  from "runtime add-on that must beat a null at a checker" to "the medium
  reasoning happens in, plus the authoring discipline that makes the
  medium's statements alignable to answer keys".
- It does NOT support the cascade either: whether a reasoner is BETTER-PER-
  COST in that medium is exactly the M2 extrapolation, and A1 is silent on
  it. The reframe of issue #12 is therefore a reframe, **not an answer**:
  under H-CN the kernel cannot be "optional" (it is the internal language),
  but the live question mutates into "does the internal language need to be
  KERNEL-structured, or does any typed canonical dialect do?" — which is the
  knull-v2 channel, now MORE decisive rather than less (§4), and CASC-0
  carries a dialect arm for exactly this (§6, arm A5)
  [STIPULATED: ASM-1075].

### 3.3 The maintainer's "all lines still useful" claim, made concrete

| Existing line | Role inside H-CN | Measured status it brings |
|---|---|---|
| kernel authoring / mint (A-F0 line) | defines the Option-A dialect + the IR-hard record base the engine checks against | authoring economics unmeasured; f2b-transfer stage-1 endorsed the covered-slice membership gold (A=0.9610 LB 0.9395 FINAL) [MEASURED: interpretations/f2b-transfer-stage1.md, restated] |
| f2b / H-VL | the E-in-the-loop mechanism (M4), generalised from answer-grain to step-grain | the only audited efficiency sign (+0.1507 at 0.103 cost), aligned-answer-key mechanism, formal scope [MEASURED] |
| NLB / H-PS | F IS NLB-FE/1 + the H-PS generalisation; G-NLB is the cascade's front-door gate unchanged | both measured crossings FAILED (0.476 / 0.416 + S2 kill) — the cascade's binding constraint [MEASURED] |
| knull / naturalisation line | (a) the dialect-attribution control (kernel gloss vs plain typed dialect); (b) R's training/eval material — the scholarly-prose bar lives at R | plain-arm quality ruling still open; becomes the "which internal language" decider [ref: issue #6] |
| CODEVERT / code vertical | the friendliest first vertical for a full cascade instance: extractor+engine = the IR-hard substrate; UNKNOWN-INCOMPLETE semantics inherited | G0: forward/lexical families κ≈0.72 pooled, store 6.05 MB, µs queries, 82 MB RSS — symbolic side ≈ free; inverse families 0.00 (walled) [MEASURED: poc/codevert-g0/RESULT.md] |
| a-e2 minting census | V-DEC's ceiling: the minted-vocabulary consumption channel is exactly the deferred decoder-seam variant | membership upper bound 18.5–41.7% prefill, consumption unmeasured [MEASURED: upper bound only] |
| RAGC / FRONT | supply the G4 comparators and controls verbatim: MONO+TTC is FRONT §2.4/C4; the tool arm is RAGC GR-C/TOOL-NL; derangement is house | designed, registered |
| ORACLE / KOT-DECOMP | the three-stage pipeline is a decomposition-native object: F / L' / E / R stage counters per KOT-DECOMP | designed |

Lines H-CN does NOT rescue, said plainly so the "all lines useful" sentence
is not overread: H-DD, deep-internal H-RULE placements, broad general-NL GNN
fusion, and the general-index oracle census remain steering-dormant; nothing
here re-opens them [STIPULATED: ASM-1072; ref: round2-steering §6].

---

## 4. Relation to knull-v2 and the attribution ladder

Under H-CN the attribution question has three rungs, and existing
instruments already own two of them [STIPULATED: ASM-1075]:

1. **Structured-medium vs free NL** (does ANY canonical typed dialect beat
   natural text as the reasoner's medium at matched budgets?) — new; CASC-0
   arms A3-vs-A2 and A5-vs-A2 price it.
2. **Kernel dialect vs plain dialect** (does kernel-grade authoring of the
   dialect add anything over knull-grade plain typed text?) — the knull-v2
   channel, inherited; CASC-0 arm A5 is its cascade instantiation. The
   deflationary prior is stated honestly: every measured contrast so far
   (DECONF-A1; the a5 structural caveat; the CODEVERT kernel-free-win
   analysis) points to ≈0 here, and a ≈0 result would leave H-CN alive as a
   GENERIC structured-cascade architecture while killing its kernel-content
   attribution — a legitimate outcome the prereg must name in advance.
3. **Checked vs unchecked medium** (does the engine loop carry the effect?)
   — the f2b/DECONF question at step grain; CASC-0 arm A4 isolates it.

---

## 5. Gates

### 5.1 G1 — the routing-mass paper bound (~$0, run first)

The cascade's workload-level cost saving is bounded on paper before any GPU
spend [STIPULATED: ASM-1072, the ASM-0817 G1 discipline applied to a COST
claim]: with s = share of traffic routable through the structured path,
m = per-item cost ratio on routed items, and o = the naturaliser/router
overhead paid by UNROUTED items falling back to the monolith,

```
saving_max = s·(1−m) − (1−s)·o
```

Illustrative bound from measured inputs [DERIVED, planning-grade — the
inputs are corpus-indexed and extrapolate to no other corpus]: s at the
friendliest measured values 0.35–0.44 [MEASURED: m0b 0.3542; codevert-g0
κ_q^indep 0.4361], m at the f2b measured 0.103 (its narrow scope), o ≈ 0.1
→ saving_max ≈ 0.26–0.34 of workload cost. Two readings: (a) even under
generous routing the cascade is a ~⅓-cost story, not an order-of-magnitude
story, UNTIL coverage grows — the maintainer's cost goal binds through the
coverage wall like everything else; (b) the bound is computable per vertical
from census numbers already paid for, so a vertical where it comes out below
the prereg's δ is killed on paper. G1 for the code vertical additionally
inherits G0's family structure: only the forward/lexical families (κ≈0.72)
are routable; inverse/exhaustive families contribute s≈0
[MEASURED: codevert-g0 §1].

### 5.2 G2 = CASC-0 (§6) · G3 = natural-input rerun behind G-NLB · G4 = full frame

G3 re-runs the surviving CASC-0 contrast with F inside the measured system
on blind natural phrasings, per vertical, only after G-NLB clears that
vertical (ASM-0814/ASM-0945 verbatim — H-CN's F has the same output space as
NLB's gate instrument on the QA verticals, but its G3 leg is still owed on
its own distribution). G4 is the W1 attempt under the full KOT-FAIR/2 frame:
FRONT-built comparators at the rung anchor's B_k (note the RAGC §2.2
arithmetic consequence: a store+naturaliser-bearing system at rung k
necessarily runs a sub-anchor reasoner — the cascade is NATIVELY this shape,
which is a point in its favour: it is the first family whose design
PRESUPPOSES the sub-anchor arithmetic instead of colliding with it), MONO+TTC
and TOOL arms mandatory, sealed eval, lifecycle ledger including R's and F's
training and the dialect-authoring hours [STIPULATED: ASM-1072].

---

## 6. CASC-0 — the single cheapest decisive experiment

**Honesty first, inheriting ASM-1039's rule verbatim: no cheap experiment
can deliver the matched-budget WIN — that is a G4 claim under the full
framework. CASC-0 is the cheapest experiment that is DECISIVE about whether
the win is possible: it prices the two mechanisms no registry record
touches (M2 reasoning-over-structure; fid_R rendering fidelity) and carries
pre-registered kills that close the family at scope for ≤ ~15 free GPU-h**
[STIPULATED: ASM-1076].

**Class:** G2, `oracle-diagnostic` on the inbound seam (gold dialect inputs;
F is NOT exercised — its price is already the subject of NLB and is composed
analytically afterwards). NO W1 claim, NO real-input claim, per ASM-0814.
Everything self-authored/kernel-covered riders ride verbatim.

**Task corpus** [STIPULATED: ASM-1076]: reasoning items, not lookups — the
maintainer's proposal is specifically about the model "doing harder tasks
such as reasoning", and single-hop membership QA is already f2b's measured
ground. A seed-pinned procedural generator composes depth-2–4 relation
chains over covered kernel-world records (CLUTRR-shaped, the programme's D4
diagnostic class), with engine-derivable gold by construction, held-out
compositions and depths, plus blind NL phrasings of each item (parents'
blind protocol, one author source, K=1 at pilot grade — screen, not gate).
n ≈ 300–500 base items × arms; power sized by the pinned analysis script at
freeze, not here. Item-generation circularity (items rendered from kernel
records) is disclosed as the standing rider and partially countered by the
generator's held-out compositions.

**Arms** (paired, same items throughout; all decoding/token/stop discipline
pinned; KOT-COST/2 vector measured per arm on the pinned rig):

| Arm | System | What it prices |
|---|---|---|
| A1 MONO-L | 1.7B, NL in → NL out | the monolith floor |
| A2 MONO-L+TTC | 1.7B + FRONT §2.4-grade adaptive test-time compute, total measured cost = A3's | **the strong generic baseline — the arm that kills "the saving is just more compute"**; anti-weak-control rules (RAGC §2.4) apply: harness defaults, logged tuning, published build log |
| A3 CASC-full | gold Option-A dialect → 360M reasoner + engine verify-retry on IR-hard islands (k pinned) → structured core → 135M renderer → NL out | the cascade core (M2+M3+M4 composed) |
| A4 CASC-noverify | A3 minus the engine | isolates M2/M3 from M4 (the f2b-redux discriminator: if A3≈A4≈A2 the "structure" adds nothing beyond the known loop) |
| A5 CASC-plain-dialect | A3 with the knull-grade plain typed dialect, matched content/tokens | dialect attribution (§4 rung 2); expected-direction disclosure: ≈A3 under the deflationary prior |
| A6 CASC-deranged | A3 with seed-pinned deranged store/keys | house control; expected collapse to abstention/errors |

Co-reported floor: MONO-S (360M alone, NL in/out) — contextualises whether
A3's core is doing anything its bare reasoner would not.

**Endpoints** [STIPULATED: ASM-1076; statistics per programme §2.5 —
hierarchical cluster bootstrap over items preserving paired predictions,
Holm across the named contrasts, exact CP for the rare-event render leg]:

1. **Primary (efficiency shape):** paired LCB95(acc_e2e(A3) − acc_e2e(A2)) > 0
   at measured cost(A3) ≤ cost(A1), acc scored on the NL SURFACE by a pinned
   mechanical answer-extraction contract against engine gold (format-blind;
   any judge fallback is a pinned temp-0 protocol named at freeze — a Fable
   ops-amendment names the judge, per standing practice). The renderer's
   failures COUNT AGAINST the cascade — the anti-l3a/a5 rule applied to the
   output side for the first time.
2. **Co-primary (the new instrument):** fid_R = P(surface correct | core
   correct) with LB95 ≥ 0.90 (planning bar, maintainer-adjustable at
   freeze), AND dangerous-render rate (surface asserts content absent from
   the core, mechanically diffed against the core's claim set) UB95 < 0.02
   [PROPOSED-ASM: ASM-1074].
3. **Secondaries:** Δ(A3−A4) (checked-loop share); Δ(A3−A5) (dialect share,
   TOST/NI at a pinned margin — a within-band result kills kernel-dialect
   attribution at this scope, feeding the knull/issue-#12 ruling); A6
   collapse check; the full KOT-COST/2 vector per arm including TTFT and
   p95 (the cascade's serial-latency tax measured, not assumed away); γ and
   ρ_in measured as realised token ratios (converting two [ESTIMATED]
   ledger entries into numbers).

**Pre-registered kills** [STIPULATED: ASM-1076]:

- **K1 (core kill):** LCB95(acc(A3) − acc(A2)) ≤ 0 at matched cost AND
  point acc(A3) < acc(A1) → the structured core buys nothing a generic
  TTC monolith doesn't; H-CN killed at scope (V-DEC/V-LL do not unlock).
- **K2 (rear-seam kill):** fid_R point < 0.85 OR dangerous-render LB95 ≥
  0.02 → the outbound boundary is a second NL wall; H-CN blocked pending a
  renderer redesign cycle, and the §3.1 algebra is re-published with the
  measured fid_R so the e2e ceiling is explicit.
- **K3 (attribution kill, non-fatal to the family):** Δ(A3−A5) inside the
  NI band → kernel-dialect attribution dead at scope; H-CN continues, if at
  all, as a generic structured-cascade comparator and the kernel-content
  claim routes entirely to knull-v2/A-F0.

**Cost** [ESTIMATED]: ≤ ~10–15 GPU-h free pool (dominated by A2's TTC arm at
1.7B), ≤ ~$25 API-class judge/authoring, zero annotation hours (procedural
gold; the blind phrasings are authoring-class spend of the parents' scale).
CPU/engine legs run on the local box under standing nice/checkpoint
discipline.

**Top failure modes of CASC-0 itself, with counters** [STIPULATED: ASM-1076]:
(i) self-authored circularity flatters A3 — countered partially by held-out
compositions + the A5 dialect arm; rider rides regardless. (ii) A2
under-tuned — the anti-weak-control machinery is mandatory, and an A3 "win"
over a weak A2 is void. (iii) format/verbosity bias in surface scoring —
mechanical extraction contract, pinned max-tokens on every arm, cost
co-normalised per emitted token. (iv) oracle-inbound flattery — disclosed in
every readout; the e2e projection acc ≈ ret_F × core × fid_R is published
beside the result with ret_F from the NLB line, tagged EXTRAPOLATION until
G3 runs it. (v) fid_R measured on a renderer nobody has tuned — a floor
read, not a ceiling; K2 therefore blocks rather than kills.

**Promotion:** CASC-0 pass → G3 (natural-input, per vertical, behind G-NLB)
→ G4 under the full frame. The code vertical joins at G3 via CODEVERT's
forward-family substrate once its own G1/G2 line resolves (choosing among
G0's three defensible-universe options is the coordinator/maintainer design
decision G0 already names [MEASURED: codevert-g0 §5.3]).

---

## 7. Honest risks — where the cascade likely does NOT help

1. **The saving may be moved, not removed.** F and R are real bytes, real
   latency, real training and authoring cost, real failure modes; the
   KOT-SIZE/2 + KOT-COST/2 + KOT-LIFE/1 ledgers charge all of it. The
   worked identity (§3) shows V-C2 is net-NEGATIVE without M2; a critique
   that says "you shrank the reasoner and paid for it in the naturaliser +
   boundary error" is answered only by the measured A3-vs-A2 contrast at
   matched TOTAL cost — never by the ledger's algebra.
2. **Structured input may hurt the reasoner.** The one adjacent measurement
   (nsk1 text-delivered grounding) is NEGATIVE at its scope; stock
   checkpoints are NL-trained and the dialect is out-of-distribution;
   dialect fine-tuning of L' costs metered T_k that the baseline symmetric
   tuning rule matches on A2's side [STIPULATED: ASM-0852 applied].
3. **The coverage wall binds the cost goal.** §5.1's bound: at measured
   routing shares the cascade is a ~⅓-cost architecture at best on the
   friendliest corpora, and the maintainer's order-of-magnitude ambition
   requires coverage growth that no measured line yet delivers (0/1,550
   define-lane; inverse code families 0.00). Where s is small the
   naturaliser is pure overhead on 1−s of traffic.
4. **Open-ended generation is out of scope.** Where the naturalised surface
   IS the content (essays, long explanations, style-bearing text), γ→1 and
   M3 vanishes; the renderer would need the full content anyway. H-CN's
   claim surface is QA/reasoning/agentic-tool shapes with compact answer
   cores — this is disclosed as a workload restriction on every claim.
5. **Below the reasoning floor the middle tier is unnecessary.** For
   single-hop covered lookups the engine (or plain RAG) alone is cheaper
   than any cascade — a three-tier system that "wins" on lookup items has
   manufactured its win by refusing the cheaper two-tier comparator; the
   MONO-S floor and the RAGC arms exist to catch exactly this.
6. **Latency.** Three serial stages worsen TTFT and p95 by construction;
   interactive workloads may reject the architecture even at a FLOP saving.
   Measured, reported, and part of B_k admissibility — not waivable.
7. **How a false win would most likely be manufactured** (threat-model
   entries for the eventual prereg, each with its §6 counter): covered-only
   or kernel-rendered-only evaluation (rider + held-out compositions);
   long-NL baseline vs short-core cascade scoring asymmetry (output-length
   control); naturaliser costs off-ledger (KOT-SIZE/COST/LIFE charge them);
   judge preference for canonical phrasing (mechanical extraction first);
   weak TTC baseline (anti-weak-control); alignment-confound redux — a
   CASC win without A5/A6 controls attributes to "kernel structure" what
   DECONF-A1 has already shown can live in an aligned answer key
   (controls mandatory) [STIPULATED: ASM-1077].
8. **The strategic risk is dilution, not falsity.** H-CN composes three
   lines that each have their own gate; if it becomes the umbrella under
   which those gates blur ("it's all one architecture now"), the programme
   loses its kill discipline. Counter: H-CN adds NO new licence to any
   component line — NLB still gates, knull-v2 still decides content,
   CODEVERT still owns its census floors; H-CN's own claims live only at
   its own gates [STIPULATED: ASM-1072].

---

## 8. Epistemic register

- **MEASURED (restated strictly in-envelope):** f2b-replicate lift/cost
  (+0.1507, 0.103) and its does_not_license scope; DECONF-A1 complete
  certificate (C_dec = 1.0, 40,576/40,576; runtime-structure inert at the
  pinned R-1 checker scope); l3a-parse/a5-nl retentions and the S2 kill;
  nsk1-g2d net-harm and nsk1-bprime2 echo-grade delivery (exploratory);
  m0b 0.3542 / g8 0/1,000 / define-lane 0/1,550 coverage walls;
  codevert-g0 κ_q^indep 0.4361, family split (forward ≈0.72, inverse 0.00),
  store/latency/RSS figures; a-e2 membership UPPER BOUND 18.5–41.7%;
  engine 5.29–7.82 µs; f2b-transfer stage-1 endorsement (A=0.9610 LB 0.9395).
- **STIPULATED / PROPOSED-ASM (this document's design choices; coordinator
  registers at commit, append-only):** ASM-1070 (H-CN framing, three
  variants, V-C2 primary, no-cheap-win honesty); ASM-1071 (IR-soft medium
  with IR-hard islands; component classes; F := NLB-FE/1 with ASM-0945
  obligations); ASM-1072 (gate mapping G1-routing-bound/G2-CASC-0/G3-NLB-
  gated/G4-full-frame; no dormant line re-opened; no new licence to
  component lines); ASM-1073 (mechanism-named cost attribution rule);
  ASM-1074 (rendering fidelity fid_R + dangerous-render bound as the rear
  seam's gate quantities); ASM-1075 (the issue-#12 reframe semantics + the
  three-rung attribution ladder); ASM-1076 (CASC-0 design: arms, endpoints,
  kills, oracle-diagnostic class); ASM-1077 (false-win threat entries);
  inherited in force: ASM-0808, ASM-0810, ASM-0812, ASM-0814, ASM-0817,
  ASM-0852, ASM-0945, ASM-1039's honesty rule.
- **EXTRAPOLATION (registered, never premises):** ASM-1078 — M2, the
  reasoner-shrink bet (a smaller reasoner over canonical checked dialect
  matches a larger one over NL at task grade); resolver: CASC-0 A3-vs-A2
  then G3/G4. ASM-1079 — that gate-clearing boundary values (ret_F ≥ 0.90,
  fid_R ≥ 0.95) are jointly achievable at the 110–360M class; resolvers:
  P3-E-NLB-1 and CASC-0 endpoint 2. The e2e projection composed from them
  is published only as the product of tagged quantities, never as a number
  of its own.
- **ESTIMATED (planning only, converted to measurements by CASC-0 where
  possible):** ρ_in, γ, r, o, c_S/c_L worked points; all §6 costs.
- **DERIVED (this document's analytic computations from measured inputs,
  disclosed):** the cost identity and worked ratios (§3); the boundary-tax
  arithmetic (§3.1); the G1 routing-mass bound and its 0.26–0.34
  illustrative range (§5.1).

**Self-check gate (mandatory, performed before hand-off):** every design
choice above is tagged STIPULATED or PROPOSED-ASM, never MEASURED; every
forward expectation is EXTRAPOLATION or ESTIMATED and none is used as a
premise; every MEASURED figure names its artifact and stays inside its
envelope (upper bounds called upper bounds; exploratory called exploratory;
scopes R-1/corpus-indexed where they are); no registry/verdict/frozen object
is edited; no account handles appear; the PROPOSED-ASM block is disjoint
from the observed high-water mark and its registration is explicitly
delegated to the coordinator at commit.

This document changes no frozen object, no verdict, no audit, and no
registry entry; it proposes one bead-able experiment (CASC-0) and defers two
variants without beads. Next step per the standing loop: GPT-5.6 external
critique (bidirectional design), then coordinator synthesis, then the
maintainer's routing.
