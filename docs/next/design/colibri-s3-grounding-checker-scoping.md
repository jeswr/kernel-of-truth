# S3 grounding-checker — design-scoping (kernel facts → closed-world admissibility at the sampler)

> **Status: DESIGN-SCOPING ONLY.** Not a pre-registration, not frozen, nothing here is
> registered, committed, or run by its author. Authored by the architecture-advisor role
> (Fable) on coordinator request following the dual-model colibri steer
> (`docs/next/design/colibri-s1-seam-steer-2026-07-21.md`) and the maintainer's
> elevation of S3 to the top kernel-leverage seam (issue #60). The carried caveat that
> this document exists to discharge *in design form*: **the checker claim needs its own
> priced falsifier vs a kernel-as-text control before "the kernel's home is the output
> seam" is banked** — migrate the test, not the optimism. All proposed pre-registration
> content carries `PROPOSED-PREREG-ROW-S3-*` / `PROPOSED-CRIT-S3-*` labels for the
> experiment-designer; no ASM ids are minted here — the [STIPULATED] design choices
> below are proposed assumption rows the coordinator registers with the landing
> commit, per design-agent governance. **This is Revision 3:** the Rev1
> cross-vendor GPT-5.6 review returned NEEDS-REVISION (dispositions §9, applied in
> Rev2); the Rev2 delta-check returned NEW-DEFECT (three C-KERN defects, the first
> load-bearing; dispositions §10, applied here). The next consumer is the
> delta-check re-check, then the experiment-designer pipeline.

---

## 0. Load-bearing premises of this design

PREMISE: colibri's S3 seam has structural primitives only and no grounding hook — GBNF engine `c/grammar.h` with `gr_admissible` (byte-class mask, `grammar.h:333`) and `gr_forced` (`:349`), wired via `GRAMMAR=` at `grammar_setup()` (`glm.c:4228`), JSON-Schema→GBNF `schema_to_gbnf()` (`c/schema_gbnf.h:220`) via `SCHEMA=`; grammar is currently **draft-only** (`grammar_draft()`, guaranteed-accepted), never a hard sampler constraint; `grounding`→0, `checker`→0 hits in code [MEASURED: reports/colibri-recon-2026-07-21.md §S3; line refs against `glm.c` HEAD `153e6f4c`, symbols are the durable anchors].

PREMISE: both blind design reads ranked S3 first among the three colibri seams, for the same three measured reasons — regime-independent (survives full RAM residency, unlike S1/S2 [MEASURED: colibri #472 via recon]), model-agnostic (grammar/sampler machinery survives the Kimi-K3/DeepSeek-V4 pivot; expert atlases do not), and net-new/unowned [MEASURED-as-record: docs/next/design/colibri-s1-seam-steer-2026-07-21.md §"Where the two models AGREE"].

PREMISE: the strongest published analogue for engine-owned output correctness is the neural-author/deterministic-engine topology — Logic-LM +39.2% over standard prompting, +18.4% over CoT on five logical-reasoning datasets [LIT-BACKED: arXiv:2305.12295 (2023); verified reports/lit-llm-injection-priorart.md §6; figures re-verified at the primary page 2026-07-11 per docs/next/lit/RULE.md].

PREMISE: incremental constraint checking during decoding measurably removes an error class at matched model and compute — PICARD cut Spider-dev execution errors 12%→2% on a fine-tuned T5 by rejecting inadmissible tokens mid-decode [LIT-BACKED: arXiv:2109.05093 (2021); verified reports/lit-structured-parsing-and-inner-symbolic.md 2026-07-09]; grammar-constrained decoding without finetuning substantially outperforms unconstrained LMs on structured tasks [LIT-BACKED: arXiv:2305.13971 (2023); docs/next/lit/PARSE.sources.jsonl, verified].

PREMISE: the kernel-specific-structure correctness thesis has never been validly measured at power under the programme's four conditions (validated instrument; powered pre-registered margin; kernel-vs-matched-generic; non-degenerate structure-sensitive contrast), and the content thesis is bounded by content-interchangeability — authoritative content helps, but the content need not be kernel-authored [MEASURED: registry/verdicts/knull-v2.json; synthesis docs/next/feasibility-synthesis-v9.md §5, §7].

PREMISE: every existing thesis demonstration sits at ≤108 concepts; kernel coverage is 0.3542 at molecules-v0 on ONE pinned corpus [MEASURED: registry/verdicts/m0b.json — corpus-indexed, extrapolates to no other corpus] and exploratory α_point = 0.24 (two-sided Wilson-95 [0.1150, 0.4343]) on the representative WordNet-10k draw [MEASURED: per feasibility-synthesis-v9 §7]. Any S3 claim is bounded by the covered slice.

PREMISE: the programme's runtime-judgment-interface ledger is 0-for-5 [MEASURED: programme record, feasibility-synthesis v6 §2.3, carried in v9] — the honest prior against any new runtime mechanism is adverse, and this document must not argue around it, only design past it (§2.4).

STIPULATED: this document treats the S3 checker as a **correctness-thesis** experiment first (the add-capability shape the Programme-3 Phase-0 sweeps located as the kernel's defensible value — no matched-resource efficiency win was found on any audited pathway [LIT-BACKED: reports/lit-p3-{fuse,rule,ntp,parse}.md, direction-only]); any speed co-benefit (forced-span drafting, §1.5) is reported in the metric vector but is not the claim.

---

## 1. The seam, precisely

### 1.1 What exists and what is net-new

colibri ships a GBNF grammar engine whose runtime interface is exactly an
admissibility oracle over next bytes/tokens: `gr_admissible` answers "which
continuations does the grammar admit from this automaton state," `gr_forced` answers
"is the continuation unique," and `gr_feed(t)` (`glm.c:4269`) advances the state at
the emit site. Today that oracle is consumed only by `grammar_draft()` — grammar-forced
*drafts*, lossless because the target model verifies them — and never constrains the
sampler [MEASURED: recon §S3]. The recon identifies three net-new insertion points:

1. **Sampler hard mask** — intersect the sampler's candidate set with
   `gr_admissible` before sampling: tokens outside the admissible set get logit −∞.
   This is the true hard-constraint semantics and the mechanism under test here.
2. **Post-sample veto** at `gr_feed(t)` — rejection-sample: if the sampled token is
   inadmissible, resample. Cheaper wiring, equivalent in the limit, slower and
   messier at low admissible mass. Fallback implementation only.
3. **Server-side validate-and-retry** in `openai_server.py` — no logits access;
   whole-output validation + regeneration. This is a deployment variant, not the S3
   mechanism claim, and is excluded from the estimand. [STIPULATED design choice:
   the experiment tests insertion point (1), with (2) as an implementation fallback
   producing identical accept/reject decisions.]

### 1.2 The compile pipeline: kernel records → admissibility predicate

The kernel supplies three strata of machine-checkable content (strata discipline per
`docs/design-dl-from-nsm-and-lean-reconstruction.md`; axiom grammar per
`docs/design-constraint-layer.md` §3.3):

- **Stratum 2 (definitions):** the minted concept inventory — URNs, labels, and
  relational-concept signatures. Supplies the closed *symbol vocabulary*.
- **Stratum 3 (endorsed laws, `kot-axiom/1` sidecar):** `subClassOf`, `disjointWith`,
  `domain`, `range`, `inverseOf`, `functional`, `cardinality` — a closed constraint
  inventory with pinned CWA validation semantics
  (`validate(recordSet, axiomSet) → {conformant | violations[]}`), linear-ish local
  checks over a materialised closure, no search
  [MEASURED-as-design-record: design-constraint-layer.md §3.3; complexity claim is the
  doc's own, for a strict subset of SHACL-core minus recursion].
- **Stratum 4 (world layer):** the closed, declared set of asserted facts, plus the
  deterministic rules engine's entailment closure over them — exactly correct at
  certified scope (858/858 entailments; 0/3,680 false positives, ~$0)
  [MEASURED: registry/verdicts/rules-1-c.json as synthesised in feasibility-synthesis-v9 §8].

The compile is two-level, and the distinction is load-bearing for honesty about what
is guaranteed:

**Level A — vocabulary/structural closure (statically compilable to GBNF).**
A deterministic compiler (the `schema_to_gbnf()` pattern, kernel-fed) emits a task
grammar whose *terminal productions are enumerated from the kernel instance*: concept
labels/URNs from stratum 2, relation names from the relational-concept signatures,
entity constants from the stratum-4 record set. Any output inside a constrained span
is then well-formed **and references only kernel-known symbols** — closed-world at the
vocabulary level. This level alone is expressible in colibri's existing GBNF engine
with zero engine changes beyond the sampler wiring.

**Level B — record/axiom admissibility (stateful, beyond a static grammar).**
The incremental checker tracks the partially-emitted assertion. At the span boundary
where subject `s` and relation `r` are fixed and the object slot opens, the checker
computes the admissible object set and intersects the token mask with the trie of its
tokenisations. Two admissibility policies exist, and choosing between them is a real
design fork (FORK-S3-A, §7):

- **P-strict (grounded-only):** `o` is admissible iff `(s,r,o)` is in the pinned
  entailment closure of the record set. The model cannot emit a non-derivable
  assertion inside a constrained span — fabrication is structurally impossible there;
  the model's remaining job is *selection* among derivable facts and everything
  outside the constrained spans.
- **P-consistent (contradiction-veto):** `o` is admissible iff
  `validate(recordSet ∪ {(s,r,o)}, axiomSet)` returns no violations — blocks only
  assertions the kernel *contradicts* (disjointness, domain/range, cardinality,
  functionality), and permits unknown-but-consistent assertions, preserving model
  knowledge outside kernel coverage. The weaker, wider, more deployment-honest
  semantics.

STIPULATED: the admissibility predicate is evaluated by the existing deterministic
engine over the pinned closure — the verifier stays outside the vector and outside the
model, per the verifier-not-in-the-vector rule (design-constraint-layer.md §4) and the
X3 cosine ban. No similarity computation appears anywhere in the mask path.

### 1.3 Per-token evaluation without wrecking generation

- **Cost shape.** Admissible sets are computed once per span-entry (one batched
  `validate()` per `(s,r)` context), cached, and compiled to a token trie; per-token
  work is trie intersection. That this is microsecond-scale at current kernel scale
  (≤108 concepts, hundreds of facts) is an unmeasured engineering forecast
  [EXTRAPOLATION — premise of nothing; resolution path: the measured per-token
  overhead gate in PROPOSED-CRIT-S3-GATE-0]; at the large-kernel scale the
  token-mask-caching literature says the same engineering is near-zero overhead in
  serving stacks [LIT-claimed, UNVERIFIED-THIS-PASS: XGrammar, arXiv:2411.15100, per
  docs/next/lit/PARSE.sources.jsonl `verified:false` — engineering pointer only,
  non-load-bearing].
- **Dead-end safety.** The automaton must only admit prefixes that have at least one
  admissible completion (completability check at mask-build time — the PICARD lesson);
  GBNF's automaton construction gives this for Level A; Level B tries are built from
  complete admissible objects, so completability holds by construction.
- **Scope of the mask.** [STIPULATED design choice] The mask applies **only inside
  declared assertion/answer spans** of a structured output format; reasoning prose
  outside those spans is unconstrained (think-then-constrained-answer). This
  preserves generation quality where the mask has nothing to say and confines the
  mechanism to where its semantics are defined.
- **Distributional caveat, carried honestly.** Locally-masked constrained decoding is
  biased sampling relative to the true grammar-conditioned distribution over the
  constraint classes studied; the published result does *not* show local masking is
  unsafe in general [LIT-BACKED: arXiv:2606.01926 (2026), scope caveat verbatim from
  the verified source record]. The design's response is empirical, not argumentative:
  the falsifier arms (§4) price the whole mechanism, bias included.
- **Draft/MTP contract.** The measured hazard class: changing what fires differently
  in draft vs verify zeroes MTP acceptance (56%→0% datum) [MEASURED: recon §S1-gap].
  The mask therefore must be applied identically to draft proposals and verify-side
  sampling. colibri's own `grammar_draft()` is the shipped consistent pattern; a
  hard sampler mask sharing the same automaton state satisfies the contract by
  construction. [STIPULATED: experiment runs DRAFT=0 primary to keep the estimand
  clean; an MTP-on acceptance check rides as a secondary observation.]

### 1.4 What the checker does NOT do

Binding scope rule for every claim in this document [STIPULATED scope, proposed for registration at commit]: this mechanism guarantees **structural and enumerated consistency inside constrained spans — never general factual truth of free prose** (concurring with the GPT-5.6 steer's own caveat in
colibri-s1-seam-steer-2026-07-21.md §2.1). Unconstrained prose grounding would need a
semantic checker beyond this design. Every claim in §3 is scoped accordingly; any
narration of this design as "hallucination elimination" simpliciter is over-claim.

### 1.5 Efficiency co-benefit (reported, not claimed)

Where `gr_forced` finds singleton admissible sets, forced spans can be emitted through
the existing guaranteed-accepted draft path — the checker's constraints become free
speculative tokens. This is measured and reported in the metric vector V (inference
compute) but is explicitly not the value claim (§0 last premise).

---

## 2. What is load-bearing at this seam — the store by design, the kernel only by measurement

### 2.1 What the seam supports — and the two-claim split (Rev2 central correction)

The mechanism's causal chain is `source → admissible set A(s,r,prefix) → token
mask`. Once compiled, the sampler sees only A: any source producing the same
admissible sets — a relational database, a knowledge graph, a JSON-Schema with
enums, a plain typed ontology, a retrieval allowlist — yields an **identical output
distribution**, and the source's provenance is erased at compile time. Rev1's
version of this section argued "empty kernel ⇒ no mechanism" and concluded the
kernel content is the program; the cross-vendor review is right that this proves
only that the mechanism needs *a* populated typed store, not *this* kernel
[design interpretation, corrected in Rev2]. The programme has already measured this
pattern once: an aligned non-kernel store was value-equivalent to the kernel on a
related checking seam [MEASURED: registry/verdicts/knull-v2.json]. The thesis
therefore splits, and the halves are tested by different contrasts:

- **C-MECH (mechanism claim):** a closed-world admissibility mask at the logits
  seam beats the same facts as text (and beats format-only constraint). Tested by
  M_K vs T and M_K vs G (§4).
- **C-KERN (kernel-specific-MASK claim, Rev3):** at matched context, a mask
  compiled from the KERNEL beats the identical mechanism compiled from the
  strongest matched non-kernel typed store. Tested ONLY by the §4.1 crossed cells
  — the mask-source main effect at held-fixed context (KILL-3). A full-package
  swap (text and mask together — Rev2's M_K−M_N) cannot carry it: that bundled
  contrast identifies the kernel source *package*, not the mask at the sampler
  seam (Rev3 correction; the package contrast is demoted to a secondary
  source-stack reading).

What remains true mechanistically: within this seam the *store* is load-bearing by
design — the admissible sets are computed from store records and from nothing else
(stratum-2 vocabulary closure; stratum-3 axiom sidecar under the pinned CWA
procedure; stratum-4 closure under the certified rules engine) — which is
categorically different from S1, where the kernel supplies a substitutable ranking
(modal outcome a tie [MEASURED-as-record: moe-expert-replacement-design-menu.md
§2]), and from S2, where a drafter must be a generative model (steer Rank-3
argument). But "store load-bearing" licenses only C-MECH. The structural
concession, stated up front: the kernel's differentiators (NSM grounding,
deterministic vectors, hash identity, strata governance) live *outside* the
admissibility predicate; the kernel can differ from a matched store at this seam
only where its records or closure make **different admissibility predictions**
(e.g. engine-derived entailments an asserted-only store lacks, or axiom vetoes a
plain schema does not express). PROPOSED-CRIT-S3-PRECERT-1 (§4.3) certifies that
such differences exist on the frozen item universe before C-KERN is registered.
Rev3 qualifications: a PRECERT failure at a nonzero ρ_min means C-KERN is **not
identifiable/powerable under this planned design** — strict unidentifiability
holds only in the limiting case where the two compiled sets are literally
identical; and the narrowed headline "structured-store admissibility is
load-bearing" is licensed ONLY by a subsequent C-MECH PASS — a failed PRECERT
alone establishes nothing.

### 2.2 The Law-3 seat

This is the engine seat of the winning topology (neural proposer ↔ formal language ↔
deterministic external engine that owns correctness): the model proposes token
continuations; `kot-axiom/1` + the record closure are the formal language; the
validate/closure engine owns the admissibility verdict. Every verified capability win
in the injection survey is on the symbol side of exactly this seam [LIT-BACKED:
reports/lit-llm-injection-priorart.md §6-§7; Logic-LM/AlphaGeometry template]. The
kernel's strongest seat per the programme's own laws is the engine seat — S3 is that
seat implemented at the sampler. Rev2/Rev3 discipline: Law 3 licenses the engine
seat for a deterministic store *generally* — which store earns the seat is the
C-KERN question, and only the crossed mask-source contrast answers it (§4.1).

### 2.3 Mapping onto the four-condition discriminator

The v9 crux requires (i) validated instrument, (ii) powered pre-registered margin,
(iii) kernel-vs-matched-generic by construction, (iv) non-degenerate,
structure-sensitive contrast [MEASURED-as-record: feasibility-synthesis-v9 §5]. Rev1
claimed the design "can hit all four by construction"; the review is right that this
was untagged and too strong — deterministic scoring validates neither the answer key
nor the item semantics nor source fidelity. Rev2 statement [STIPULATED design
intent]: the design *addresses* each condition through an explicit validation gate,
none of it free — (i) instrument validity = store-independent gold (§3.2–§3.3) plus
the GATE-0 artifact/implementation gates (§4.3–§4.4); deterministic scoring removes
only the LLM-judge validity leg; (ii) the simulation-based power plan (§5.3); (iii)
kernel-vs-matched-generic = the crossed arm-N cells and only those (Rev3: the
mask-source main effect at held-fixed context) — neither T (varies the channel,
not the source) nor G (removes semantic constraints rather than replacing their
source; Rev1's "matched generic" label for G is withdrawn) is that control;
(iv) the effective non-degeneracy certification (§5.2) plus the policy-specific
derangement gates (§4.3). The design-level case for S3 is that these gates are
cheap here, not that anything comes by construction.

### 2.4 The honest deflators, faced

- **Content-interchangeability (knull-v2).** The T arm may capture nearly all the
  value: models are good at copying constraints from context, and the programme has
  already measured that authoritative content helps regardless of authorship
  [MEASURED: knull-v2]. This is exactly why T is C-MECH's binding opponent (Law 2)
  — and why Rev2/Rev3 extend the same lesson to the compiled channel: an aligned
  non-kernel store may compile to an equally good mask, so C-KERN gets its own
  binding opponent, the crossed arm-N cells of §4.1 (the knull pattern
  re-instantiated at the mask seam, with the mask isolated from the text).
- **0-for-5 runtime-judgment ledger** [MEASURED: v6 §2.3 via v9]. Distinguishing
  feature, stated precisely and not as an excuse: the five failures were *judgment*
  interfaces — the kernel asked to out-judge a model or a generic control at runtime
  on open semantics. The S3 checker makes no judgment: it evaluates a closed, decidable
  predicate over declared records, i.e. the seam where the programme's instruments
  have actually worked (deterministic engine 858/858; deterministic scoring channels
  keep working while proxy-judged channels failed twice, v9 §7b). Whether that
  distinction buys a measured win is exactly what the falsifier decides —
  [EXTRAPOLATION — premise of nothing]: the distinction predicts S3 escapes the 0-for-5
  pattern; resolution path = this experiment.
- **The Logic-LM transfer caveat, kept.** +39.2% is a text-seam, solver-in-loop,
  formalizable-benchmark number; its transfer to sampler-masked generation is
  unmeasured [LIT-BACKED figure; transfer status per the cross-read's own warning].
  It licenses direction and design, never an expectation of magnitude.

---

## 3. The value proposition + estimand

### 3.1 The claims under test — split (Rev2)

**C-MECH (mechanism claim, confirmatory):** on closed-world tasks whose answers lie
in the store's covered slice, compiling the store's facts into a hard sampler
admissibility mask adds correctness beyond supplying the identical facts as prompt
text (M_K > T) AND beyond format-only constraint (M_K > G) — by structurally
eliminating the fabrication error class inside constrained spans (P-strict, the
confirmatory primary per FORK-S3-A), while leaving selection to the model.

**C-KERN (kernel-specific-MASK claim, registered only if PRECERT-1 certifies
different predictions; Rev3 estimand):** holding context fixed, a KERNEL-compiled
mask beats the identical mechanism compiled from the strongest matched non-kernel
typed store. Confirmatory estimand = the MASK-SOURCE MAIN EFFECT over the crossed
cells {kernel-text, N-text} × {kernel-mask, N-mask} (§4.1), scored against gold
independent of both stores, with both simple effects and the context×mask
interaction co-reported. Rev2's full-package contrast (M_K − M_NN: text and mask
swapped together) is a BUNDLED intervention — it identifies the value of the
complete kernel source package, not the mask at the sampler seam — and is demoted
to a secondary "kernel-source-stack" reading in package language only. Without the
crossed contrast the seam cannot attribute mask-specific value to the kernel at
all (§2.1); if PRECERT-1 fails, C-KERN is conceded not identifiable/powerable
under this design (§4.3), and the narrowed headline "structured-store
admissibility is load-bearing" is licensed only by a subsequent C-MECH PASS.

### 3.2 Candidate task families (designer picks the primary; FORK-S3-B)

- **T-A: closed-world QA with store-independent gold.** Items about an external
  domain that BOTH stores (kernel and the arm-N store) represent, with gold sourced
  and adjudicated independently of both (the external-gold discipline:
  `generic-store-external-gold.md`, `docs/next/design/item-builder-v5-contract.md`).
  Rev2 correction: Rev1's formulation ("engine-derived entailment QA" — gold
  certified by the rules engine over the kernel's own closure) is the programme's
  known oracle-favourable construction — a store scored against gold derived from
  itself measures answer-key adherence, not independent correctness, and would bias
  the K-vs-N mask contrasts by construction. Engine certification remains a *consistency check* on
  item construction; it is never the gold source. Where store-independent gold is
  unattainable for an item family, that family's endpoint is renamed **closed-world
  store conformance** and cannot carry the correctness headline.
- **T-B: contradiction-avoidance slot-fill.** Generation items with a constrained
  slot where distractors are type-inadmissible under the axiom sidecar
  (disjointWith / domain / range / cardinality violations) — the direct probe of
  P-consistent's veto semantics.
- **T-C: tool-argument validity.** Kernel-enumerated IDs/arguments in tool calls —
  the deployment-shaped variant (colibri's live unowned defect class: tool-output
  validation #401, reasoning loops #455 [MEASURED: recon §S3-gap]). Engineering
  relevance high; scientific cleanliness lower (task surface less controlled).
  [STIPULATED recommendation: T-A primary, T-B co-primary or secondary, T-C
  demonstration-only.]

### 3.3 Primary endpoint — one, non-tautological, KOT-HON/1-conformant (Rev2)

Binding endpoint rule [STIPULATED, and structurally so — proposed for registration at commit]: under P-strict, groundedness/well-formedness inside constrained spans is
**true by construction** — those quantities carry zero information about value and are
forbidden as primary endpoints. The primary endpoint
must be a quantity the mask does not mechanically control: **answer correctness under
the programme's honesty-first asymmetric-utility score** on items certified
effectively non-degenerate (§5.2), i.e. where the model retains a real selection
problem and can still be wrong.

PROPOSED-PREREG-ROW-S3-01 (estimand + primary endpoint, Rev2): the primary endpoint
is the paired difference in KOT-HON/1 utility S_λ
(`docs/next/design/honesty-first-scoring.md` §1: +1 correct; 0 explicit fail-closed
abstention; −λ wrong; abstentions stay in the denominator) between arms, over the
covered item universe, concept-clustered, scored against store-independent gold
(§3.2) by arm-blind deterministic extraction. Rev1's "designer picks a weight in
−2..−5" is withdrawn — it permitted endpoint tuning. The KOT-HON/1 safeguards are
pinned verbatim:

- **λ pinned BEFORE any pilot outcome exists:** λ = 3 (the band default) absent a
  declared task harm ratio [STIPULATED, per the KOT-HON/1 default rule]; changing λ
  after any readout is endpoint-shopping under the registered discipline.
- **Mandatory sensitivity co-report:** S_2 and S_5 beside every pinned S_3 readout.
- **Full co-report vector, never the scalar alone:** answer rate a,
  precision-on-answered p, abstention rate (reasoned vs reasonless split),
  wrong-rate W/N, raw recall r.
- **Degenerate-abstention guard:** a pre-registered answer-rate co-floor per arm
  plus the full risk–coverage curve — the score must not be gameable by abstaining
  on hard items, in any arm.

**Margin semantics, pinned (Rev2 — Rev1's wording permitted two readings):** the
licensing rule is the F1-K convention [MEASURED-as-record:
registry/experiments/f1k.json `analysis_plan_ref` — observed lift ≥ floor AND
test-vs-zero p < 0.05], NOT a test of Δ > floor: a contrast fires iff (a) the
pre-registered cluster-level test against ZERO fires (§5.3) AND (b) the observed Δ
meets the registered floor (anchor δ_floor = +0.03 on the S_λ scale [STIPULATED
anchor; designer re-derives from pilot utility variance]). Disclosed property of
this convention: an effect exactly at the floor fires ~50% of the time. Equivalence
is licensed separately (ROW-S3-06) by TOST at a registered ±δ_eq, powered on its
own (§5.3).

**Region disjointness (Rev3 — the Rev2 regions could overlap when δ_eq > δ_floor,
e.g. Δ = 0.04, CI [0.01, 0.049], δ_eq = 0.05 licenses both PASS and equivalence):**
at freeze, (a) **δ_eq < δ_floor is a hard constraint** — a TOST-licensed
equivalence (CI ⊂ (−δ_eq, +δ_eq), hence observed Δ < δ_eq) then can never co-fire
with superiority (observed Δ ≥ δ_floor > δ_eq); and (b) outcomes are evaluated in
the FIXED ORDER superiority → harm → equivalence, taking the first licensed
outcome, so no result ever licenses two outcomes even at the region boundaries.
This applies identically to the KILL-1 (C-MECH) and KILL-3 (C-KERN) trees.

PROPOSED-PREREG-ROW-S3-08 (matched-arms protocol, Rev2): identical across ALL arms
— explicit abstention availability (every arm's response format, including every
masked arm's grammar, admits the fail-closed abstention production; under P-strict
the abstention non-terminal is always admissible), response-grammar instructions,
stopping rules, token budgets, decoding parameters, seed handling, and arm-blind
answer extraction + scoring. Any asymmetry here is a validity defect, not a design
freedom.

Secondary endpoints (reported, never promoted): grounded-precision of emitted
assertions (informative only under P-consistent — by-construction 1.0 under
P-strict); constrained-span well-formedness in the T/B arms (where it is not
by-construction); full metric vector V incl. mask-side engine compute, prompt-token
deltas, tok/s with and without mask, forced-span draft acceptance (§1.5).

### 3.4 Coverage rider (binding)

Every claim is indexed to the covered slice: coverage 0.3542 molecules-v0 on ONE
pinned corpus [MEASURED: m0b], α_point 0.24 on the WordNet-10k draw [MEASURED: v9 §7],
≤108-concept kernel instance (or the kernel-v1 successor inventory if the F1-K
eligibility machinery lands first — reuse its gates, `f1k-large-kernel-rebuild.md`
§1). A C-MECH PASS licenses "on covered closed-world items, the compiled
admissibility checker beats the same facts as text"; a C-KERN PASS additionally
licenses kernel-MASK-source specificity only on the certified disagreement surface
(PRECERT-1) — nothing about uncovered workloads, and no "natural-coverage"
narration.

---

## 4. THE PRICED FALSIFIER (the carried caveat, discharged)

### 4.1 Arms

PROPOSED-PREREG-ROW-S3-02 (arms, Rev3; all at matched decoding params, matched
model, matched item set, paired; matched-arms protocol per ROW-S3-08). The C-KERN
cells form a crossed 2×2: {context source: kernel-text, N-text} × {mask source:
kernel-mask, N-mask}.

| Arm | Context text | Sampler mask | What it isolates |
|---|---|---|---|
| **M_K** (kernel mechanism; 2×2 cell (K-text, K-mask)) | kernel facts as text (same rendering as T) | kernel-compiled mask (Level A+B) | the checker mechanism, additive over the same information (C-MECH, with T and G); one cell of the C-KERN 2×2 |
| **X_KN** (crossed cell, Rev3 — confirmatory) | kernel facts as text | N-store-compiled mask (identical compiler/checker; ROW-S3-07) | mask-source simple effect at kernel context |
| **X_NK** (crossed cell, Rev3 — confirmatory) | N-store facts as text (same rendering discipline) | kernel-compiled mask | mask-source simple effect at N context |
| **M_NN** (full N-package; Rev2's "M_N") | N-store facts as text | N-store-compiled mask | completes the 2×2; the full-package swap M_K vs M_NN is a SECONDARY source-stack reading only |
| **T** (kernel-as-text null — C-MECH's binding opponent) | kernel facts as text | none | Law-2 control: value of *having* the facts |
| **G** (format-only grammar) | kernel facts as text | task grammar with OPEN terminal sets (no store enumeration, no axiom veto) | format-forcing / entropy-reduction / span-structure benefit. NOT a matched-generic-source control: it removes semantic constraints rather than replacing their source |
| **D^policy** (seeded deranged-store masks) | kernel facts as text | masks compiled from MULTIPLE seeded, policy-specific derangements certified at the KILL-2 Stage-1 artifact gate | implementation/manipulation validity (P-strict); certified-property validity (P-consistent) — never grounding evidence by itself |
| **B** (text-only null) | no store facts | none | the programme's mandatory second null; floors the item set |
| T_N (optional secondary) | N-store facts as text | none | context-source effect; the N-package text null |
| M0_K / M0_N (optional secondary) | none | compiled mask only | channel-substitution decomposition (mask without text) |

Design rationale, tagged [STIPULATED]: M_K-vs-T holds the information channel fixed
and varies only the mechanism (C-MECH). For C-KERN, Rev3 adopts the CROSSED design
(delta-check option (a)): Rev2's M_K-vs-M_N was a BUNDLED intervention — both the
context text and the mask were swapped together, so it identified the kernel source
package, never the mask at the seam. The confirmatory estimand is now the
mask-source MAIN effect over {M_K, X_KN, X_NK, M_NN} — the mean of the two simple
effects, each holding context fixed — with both simple effects and the context×mask
interaction co-reported (a large interaction means the mask's value is
congruence-dependent; it is disclosed, never averaged away silently). The
full-package contrast M_K vs M_NN survives only as a secondary source-stack
reading. The mandatory programme controls (two nulls + scramble) map to T, B, and
D^policy; condition (iii) is carried by the crossed cells alone. Cost: +2
confirmatory cells over Rev2 (§5.4); the crossed-vs-narrowed choice is flagged as
maintainer question 7.

### 4.2 Matched-resource accounting

PROPOSED-PREREG-ROW-S3-03: F0-style accounting (design-efficiency-track.md standard).
M_K and T are token-identical on the prompt side by construction (same rendered
facts); a masked arm's extra resource is compile + per-step engine work — measured
and reported in V, with the honest note that it is engine CPU, not model FLOPs. B's
shorter prompt is reported as a token credit, not "free." No arm's win may be
narrated without its resource row. The efficiency co-benefit (forced-span drafting)
is reported under M_K only if the identical mechanism runs in all its comparisons.

PROPOSED-PREREG-ROW-S3-07 (arm-N matching manifest, Rev3): the non-kernel store is
matched to the kernel on — coverage of the frozen item universe (certified
per-item); admissible-set size distribution at decision slots (reported; any
mismatch disclosed and bounded); store bytes; authoring budget (the scholarly
authoring standard applies to BOTH stores at matched hours/spend — an impoverished
strawman N-store voids C-KERN); **matched SEMANTIC EXPRESSIVITY (Rev3 — matching
size and budget without matching expressive power makes disagreement, and a kernel
win, too easy):** a typed relation inventory of matched breadth, the same
constraint/axiom families available to both stores (the `kot-axiom/1` construct
classes or typed-store equivalents), the same closure/entailment capability (the
deterministic closure engine runs over the N-store's records exactly as over the
kernel's — an asserted-only opponent against a closure-bearing kernel is
structurally weaker and disallowed), and the same source-quality gates;
compiler/checker code paths (byte-identical machinery, different input records);
and runtime accounting (same V columns). Candidate opponent, reframed (Rev3):
**plain-v5-natural or stronger**
(`docs/next/design/plain-v5-natural-store-contract.md` — the repo's STRONG
generic-definition store contract, the designed successor to knull-v2's
deliberately-degenerate token-matched generic), extended with typed facts and
constraints under the matched-expressivity requirement above. knull-v2 itself is
cited only as the measured precedent for source-interchangeability
[MEASURED: registry/verdicts/knull-v2.json, related checking seam] — it is NOT the
opponent. The N-store choice remains a maintainer-ratified design decision (§7
question 5).

### 4.3 Kill / decision criteria (Rev2 — three-outcome trees, conjunctions, pre-certification)

**PROPOSED-CRIT-S3-PRECERT-1 (different-predictions pre-certification, before
C-KERN may be registered — Rev3-qualified):** on the frozen item universe, compute
both compiled admissibility predicates offline and certify the disagreement rate
ρ_KN — the fraction of decision slots where A_K ≠ A_N, with the direction split
reported (K-only-admits / N-only-admits / both-differ) — against a registered
ρ_min. Rev3 qualifications: (i) failure at a nonzero ρ_min means C-KERN is **not
identifiable/powerable under THIS planned design** — it is strict
unidentifiability only in the limiting case where the two compiled sets are
literally identical; (ii) on failure the experiment proceeds on C-MECH alone, and
the narrowed headline "structured-store admissibility is load-bearing" may be
claimed ONLY IF C-MECH subsequently PASSES — a failed PRECERT alone establishes
nothing; both qualifications are stated in the readout. This certification is a $0
offline artifact computation, run before any powered spend.

**PROPOSED-CRIT-S3-KILL-1 (C-MECH decision tree — replaces Rev1's conflated
rule):** the mechanism claim requires the CONJUNCTION: Δ(M_K − T) fires AND
Δ(M_K − G) fires (licensing rule per ROW-S3-01: test-vs-zero + observed floor,
cluster-level per §5.3). Rev1's single-margin rule and its "fraction of M−T
recovered by G" test are both withdrawn (the latter is an unstable ratio of noisy
differences). Outcomes — Rev3: evaluated in the fixed order superiority → harm →
equivalence, first licensed outcome taken, with δ_eq < δ_floor at freeze so the
regions are disjoint (§3.3):

- **PASS:** both conjuncts fire → C-MECH banked (scoped: this host, this item
  universe, the §3.4 coverage rider).
- **Licensed equivalence-or-harm:** the registered TOST at ±δ_eq concludes
  equivalence on Δ(M_K − T), or the harm test fires (upper confidence bound of
  Δ(M_K − T) < 0) → the "kernel's home is the output/logits seam" claim FAILS its
  pricing at this seam; ONLY in this branch may the readout say the facts, not the
  mechanism, carry the value.
- **INCONCLUSIVE:** neither superiority nor equivalence/harm is licensed →
  home-status remains UNBANKED and the 2026-07-21 steer's seam ranking may not be
  carried forward as evidence — but no attribution narration in either direction is
  licensed. Rev1's wording ("if M does not strictly beat T … the claim fails")
  conflated this branch with falsification; corrected.

**PROPOSED-CRIT-S3-KILL-2 (derangement gates — policy-specific, two stages;
replaces Rev1's "D must collapse"):**

- *Stage 1 — artifact gate (offline, $0, no model):* for each of ≥3 seeded,
  policy-specific derangements, certify: mask-disagreement rate vs the true mask;
  gold-exclusion rate (P-strict construction) or contradiction-flip rate
  (P-consistent construction); nonempty completability at every decision slot;
  cardinality matching to the true mask; and closure size / internal consistency of
  the deranged store. A derangement failing certification is discarded and
  re-seeded; if no certifiable derangement exists, kernel-content attribution
  (C-KERN and any D-based validity statement) is INSTRUMENT-INVALID — but a
  separately valid C-MECH result is NOT erased.
- *Stage 2 — implementation gate (model-side, conditional on Stage 1):* outputs
  under D^policy obey the deranged mask (the mask demonstrably controls decoding;
  the scoring pipeline does not leak gold). Under P-strict, D-collapse on
  gold-excluding derangements is mechanically forced and is therefore ONLY an
  implementation/manipulation check — never evidence of grounding or
  kernel-specificity. Under P-consistent, no generic collapse is required or
  predicted; the gate checks only the behavioural signature of the certified
  Stage-1 properties (e.g. contradiction-flip items move as the deranged axioms
  dictate).

**PROPOSED-CRIT-S3-KILL-3 (C-KERN decision tree — Rev3 estimand):** requires
PRECERT-1 certified. The confirmatory contrast is the MASK-SOURCE MAIN EFFECT over
the crossed cells:

> Δ_mask = ½ · [ (S(M_K) − S(X_KN)) + (S(X_NK) − S(M_NN)) ]

— each simple effect holds context fixed and swaps only the mask source; both
simple effects and the context×mask interaction are co-reported (a large
interaction means the mask's value is congruence-dependent and is disclosed, not
averaged away). The three-outcome structure applies to Δ_mask with the same fixed
evaluation order and the same δ_eq < δ_floor disjointness constraint (§3.3):
**PASS** → kernel-specific MASK value at this seam, scoped to the certified
disagreement surface; **licensed equivalence** → the kernel mask is
source-interchangeable at this seam (the knull outcome, reported at equal
prominence — the modal expectation, §5.5); **INCONCLUSIVE** → no
kernel-attribution narration in either direction. The full-package contrast
S(M_K) − S(M_NN) is reported as a SECONDARY "kernel-source-stack" reading, in
source-package language only — never in mask-at-the-seam language.

PROPOSED-PREREG-ROW-S3-06 (negative-direction licensing, learned from the K-3 gap):
registered TOST equivalence margins ±δ_eq for BOTH primary contrasts (Δ(M_K−T) and
the C-KERN mask-source main effect Δ_mask), each powered separately (§5.3), each
with δ_eq < δ_floor (Rev3 disjointness) — a null must be licensable, not
INCONCLUSIVE-by-default [MEASURED-as-record: v9 §7 "What a defensible verdict
requires"].

### 4.4 Gate before spend

PROPOSED-CRIT-S3-GATE-0 (pilot gates, cheapest-decisive-first, Rev2-expanded): (a)
mask machinery end-to-end on a tiny REAL model (never mock-only — the
mocks-calibrate-plumbing-not-semantics lesson [MEASURED-as-record: programme
memory/largekern]), including measured dead-end rate ≈ 0, measured per-token mask
overhead, and the abstention production verified admissible in every masked arm;
(b) effective non-degeneracy certification (§5.2) pre-spend; (c) PRECERT-1
different-predictions certification plus the KILL-2 Stage-1 derangement artifact
gate (both $0, offline); (d) pilot n≈50 items across ≥10 concepts completing with
sane abstention/wrong distributions in ALL arms, feeding the §5.3 power
simulation; (e) measured $/paired-item at bring-up, from which the powered-phase
cost ceiling is frozen (§5.4). Failure of any gate = fix or stop; no powered
spend.

---

## 5. Measurement + cost sketch

### 5.1 Instrument and reuse

Harness = kernel compiler (records → GBNF + tries) + the existing validate/closure
engine + a host with logits access. Two host options (open question, §7): (i)
**portable harness** — small open-weights model (1–8B class) with a logits-processor
hook (llama.cpp GBNF / HF processor), CPU-or-cheap-GPU; (ii) **colibri/GLM-5.2** —
requires re-provisioning (probe box terminated [MEASURED: programme memory]) and the
net-new sampler wiring in `glm.c`. The correctness claim needs (i) only; (ii) buys
deployment realism later. Item machinery, eligibility gates, and deterministic-scoring
discipline are reused from the F1-K/gsx0 estate (item-builder-v5, external-gold
store).

### 5.2 EFFECTIVE non-degeneracy certification (condition (iv), pre-spend — Rev2)

PROPOSED-PREREG-ROW-S3-05 (Rev2 — cardinality alone is insufficient: two admissible
objects may both be valid answers, one may be the only *plausible* one, or the mask
may force gold before the decision slot). For every item, certify offline:
(a) ≥ 1 admissible gold answer, AND every independently-valid alternative answer is
in the gold set (no false "wrong" scoring of valid variants); (b) ≥ 1 admissible
competitor that is independently certified INCORRECT for the item (a real way to be
wrong inside the mask); (c) a prefix-forcing audit through the automaton — no
earlier forced span or singleton prefix determines gold before the decision slot;
(d) plausibility and token-length matching controls between gold and competitors
(the mask must not select on surface artifacts). Cardinality floors (anchor: median
≥ 4, min ≥ 2 [STIPULATED]) remain as a coarse screen only. Certification is a
deterministic pre-spend artifact (the ASM-2372 distinctness-certification pattern
from the F1-K freeze, reused as a pattern — no new ASM minted here). Items failing
any check are excluded before randomisation. **Rev3 freeze note:** effective
non-degeneracy is certified SEPARATELY for the kernel-compiled and the
N-store-compiled masks on the COMMON item set — the crossed cells decode under
both masks, and an item non-degenerate under one mask may be degenerate under the
other; only items passing under BOTH masks enter the crossed cells.

### 5.3 Power and clustering (Rev2 — the Rev1 item-level sketch is withdrawn)

PROPOSED-PREREG-ROW-S3-04 (Rev2): the endpoint is a paired ASYMMETRIC-UTILITY
difference with abstentions (three-valued per item, λ-weighted) — not paired binary
correctness — so McNemar is the wrong variance model and Rev1's n ≈ 900–1,500
back-of-envelope is withdrawn. The Rev2 plan: (a) the GATE-0 pilot estimates the
paired utility-difference distribution per contrast, including abstention-transition
rates (answer→abstain and abstain→answer under masking are real, utility-moving
events); (b) power is computed by SIMULATION of the COMPLETE licensing rule
(test-vs-zero + observed floor; the C-MECH conjunction across M_K−T and M_K−G; the
C-KERN mask-source main effect over the 2×2 cells including its interaction
co-report; the separate equivalence TOSTs with δ_eq < δ_floor) under the actual
concept count C, unequal per-concept
item counts m_c, pilot-estimated abstention transitions, the declared
primary/secondary policy hierarchy, and cluster covariance; (c) the frozen
inference procedure is a concept-level sign-flip or cluster bootstrap (or a
justified hierarchical model) — house rules, no new statistics; (d) superiority AND
equivalence are powered separately (equivalence at ±δ_eq is typically the MORE
demanding target); (e) the freeze reports the 80%-powered effect size per contrast,
never n alone. Calibration anchors: the registered F1-K geometry required C = 96
clusters and n = 1,573 items for ~80% per-rung power at μ* = +4.09 pts, with +3.0
as the licensing floor only — an effect exactly at the floor fires ~50% of the time
[MEASURED-as-record: registry/experiments/f1k.json `analysis_plan_ref`,
REVISION-6]. (Correction of a Rev1 error: Rev1 cited "C=8 → power 0.119" as the
F1-K power record; that figure is the E-GLM/GLM-DROP cluster-power record via the
colibri steer, not F1-K — re-attributed here.) **The cluster-count limit persists
regardless of item count:** more items on the same concepts do not add independent
clusters; with a ≤108-concept eligible inventory (and the F1-K askability
knife-edge showing eligible-inventory can gate a campaign [MEASURED-as-record:
programme memory, ~116 authored kernels]), the designer must either power the
concept-level design honestly at the achievable C or gate the freeze on inventory
growth. Freeze blocker, not a footnote.

### 5.4 Cost (Rev2 — re-tagged)

[EXTRAPOLATION — a LOWER-BOUND planning forecast, premise of nothing; resolution
path: the measured $/paired-item at GATE-0(e), from which the powered-phase ceiling
is frozen]: harness build ≈ agentic time; pilot ~$5–15; the powered run was
Rev1-estimated at ~$30–80. That figure omits, at minimum: long-prompt prefill at
scale (facts-as-text rides in most arms), the Rev2/Rev3-added crossed cells
(X_KN, X_NK, M_NN — the Rev3 crossed design costs +2 confirmatory cells over
Rev2's single M_N, roughly +25–40% powered-phase inference, itself an
[EXTRAPOLATION] within this forecast), the optional T_N / M0 cells, the multi-seed
D^policy arms, the P-consistent secondary study, the multiplicity of the declared
hierarchy, and audit/replication passes — the true powered-phase cost is strictly
above it. If the measured $/paired-item makes the crossed design bust the
envelope, the registered fallback is delta-check option (b) — narrow C-KERN to the
full-package source-stack claim — taken ONLY by maintainer decision (§7 question
7), because it changes what the experiment can claim, not just what it costs. Feasibility caveat: ordinary hosted completion APIs do NOT
expose a per-step dynamic-logits hook; Level-B dynamic tries require local
inference (llama.cpp / HF logits-processor / vLLM structured output) or engine
integration, and static-grammar API endpoints cannot express them. The
powered-phase budget is frozen from the measured bring-up number, not from this
paragraph. colibri/GLM-5.2 deployment replication remains a separate, later line
item (box re-provision + wiring; not needed for the verdict).

### 5.5 Honest expectation

[EXTRAPOLATION — flagged, premise of nothing, resolution path = this experiment]:
modal outcome by my read: M_K beats B clearly; C-MECH (M_K vs T and G) is genuinely
uncertain — the literature says constraints help most where the model is weakest at
compliance (few-shot/small models [LIT-BACKED: arXiv:2305.13971; arXiv:2104.08768])
and the programme's own content-interchangeability result warns that text may
already capture most of the value [MEASURED: knull-v2]. **C-KERN's modal outcome is a licensed
equivalence (mask-source main effect Δ_mask ≈ 0)** — the knull pattern
re-instantiated at the mask seam — and the design treats that outcome as a
first-class, fully reportable result at equal prominence, not as a failure of the
experiment. A licensed C-MECH
equivalence would price the "home" claim honestly; that is the point of running it.
Do not size any expectation off Logic-LM's +39.2% (§2.4).

---

## 6. Model-agnostic framing (why this survives the pivot)

- The mechanism's host requirements are exactly: a tokenizer, per-step logits access,
  and a place to intersect a mask — properties of every autoregressive LM. colibri's
  grammar engine is already model-independent machinery; expert atlases, routing
  fingerprints, and MoE placement (S1/S2 assets) are per-model artifacts that the
  Kimi-K3/DeepSeek-V4 pivot [MEASURED: recon, maintainer roadmap #406/#430]
  invalidates per-model. The compiled kernel mask re-targets by re-running the
  compiler against a new tokenizer — a build step, not a research program.
- Regime-independence: the correctness value does not depend on the disk-streaming
  regime that gates S1/S2 value [MEASURED: colibri #472 via recon].
- Portability beyond colibri (llama.cpp grammars, HF logits processors, vLLM
  structured output) — Rev2 correction: this licenses **portable implementation**
  (an engineering fact about the mechanism), NOT cross-host generalisation of the
  measured treatment effect. Model instruction-compliance, tokenizer granularity
  against the trie structure, and baseline strength are plausible effect modifiers;
  a single-host result licenses that host, and any cross-host claim is
  [EXTRAPOLATION — resolution path: replication on a second host] under the
  programme's envelope discipline. colibri is one deployment target; its symbol
  anchors (`gr_admissible`, `gr_feed`, `schema_to_gbnf`) survive its own refactor
  while line numbers do not [MEASURED: recon caveats].

---

## 7. Open design forks and maintainer questions

**FORK-S3-A — admissibility policy: RESOLVED-WITH-HIERARCHY (Rev2).** Rev1
recommended running P-strict and P-consistent as symmetric confirmatory sub-arms;
the review is right that they are not symmetric — they target different error
classes (P-strict guarantees derivability-from-the-closed-world, not truth, and can
reject true-but-absent facts; P-consistent guarantees only no-detected-violation
and admits arbitrary unknowns), need different item construction, and create
multiplicity. Rev2 resolution [STIPULATED recommendation]: **P-strict is the
confirmatory primary** (the narrow closed-world mechanism claim, under §3.2's
store-independent gold and §5.2's effective non-degeneracy); **P-consistent is a
separately-powered secondary "contradiction-veto" deployment study** with its own
exposure gate (measured first, on pilot data: the rate at which UNCONSTRAINED
outputs contain store-contradicted assertions — if exposure ≈ 0 the veto cannot
show value and the secondary study is descoped), its own D construction
(contradiction-flip derangements, §4.3), and its own items. Multiplicity is handled
by declared hierarchy (primary family = P-strict contrasts only), specified before
outcomes. The alternative — P-consistent as primary IF deployment usefulness is the
maintainer's real question — is a maintainer call (question 6 below), and taking it
means withdrawing the grounding/correctness-guarantee framing from the headline.

**FORK-S3-B — primary task family (T-A closed-world QA vs T-B contradiction-avoidance).**
Why uncertain: T-A has the cleanest gold but P-consistent may rarely bind on it; T-B
probes the veto directly but needs careful distractor construction. Deciding
experiment: pilot both at n≈50; freeze the one with the better-behaved discordance and
non-degeneracy profile; carry the other as secondary. Kill criterion: a family whose
pilot shows median admissible-set cardinality < 2 or ceiling-level T-arm accuracy
(> 0.95) is dropped as unpowerable.

**Maintainer questions (must be answered before the designer freezes):**
1. Host choice (§5.1): portable-first (recommendation [STIPULATED]: yes — verdict
   needs no colibri box; note §5.4's logits-hook constraint rules out plain hosted
   completion APIs) with colibri replication deferred?
2. KOT-HON/1 λ: confirm the band default λ = 3, or declare a task harm ratio that
   moves it within [2, 5] (§3.3; Rev2 removed the designer's freedom to pick).
3. Whether a licensed K-3-style asymmetry is acceptable here or the TOST rule
   (ROW-S3-06) is mandatory at first freeze (recommendation [STIPULATED]: mandatory —
   this experiment exists to *price* a claim, and pricing requires a licensed
   negative).
4. Inventory: run on the current ≤108-concept instance now, or wait for kernel-v1
   eligibility output (§5.3 clustering interacts with this; recommendation
   [STIPULATED]: gate the freeze on the certified cluster count, not on a calendar).
5. Arm-N store choice (ROW-S3-07, Rev3-reframed): ratify the matched non-kernel
   typed store (candidate [STIPULATED]: **plain-v5-natural or stronger** —
   `docs/next/design/plain-v5-natural-store-contract.md` — extended with typed
   facts/constraints under the matched-expressivity requirement, at matched
   authoring budget). This choice is load-bearing for what C-KERN means; an
   under-expressive opponent makes a kernel win vacuous.
6. Primary policy: P-strict-primary as recommended (FORK-S3-A), or P-consistent
   primary with the correctness-guarantee framing withdrawn (deployment-first
   reading)?
7. C-KERN design shape (Rev3): fund the CROSSED design (option (a), +2
   confirmatory cells, ~+25–40% powered-phase inference [EXTRAPOLATION within the
   §5.4 forecast] — the recommendation [STIPULATED], because only it identifies
   the mask-at-the-seam claim, which is the scientifically valuable one), or fall
   back to option (b) — the cheaper full-package contrast — accepting that C-KERN
   is then renamed a "kernel-source-stack" claim with ALL mask-at-the-seam
   language dropped?

---

## 8. Label index (for the experiment-designer)

- PROPOSED-PREREG-ROW-S3-01 — estimand + primary endpoint (KOT-HON/1 S_λ, λ = 3
  pinned pre-pilot, S_2/S_5 + co-report vector + answer-rate co-floor; margin
  semantics = observed floor + test-vs-zero, the registered F1-K convention;
  Rev3: δ_eq < δ_floor + fixed evaluation order = disjoint outcome regions)
- PROPOSED-PREREG-ROW-S3-02 — arms M_K / X_KN / X_NK / M_NN / T / G / D^policy / B
  (+ T_N, M0_K, M0_N optional secondary); the C-KERN cells form a crossed 2×2
  {context source} × {mask source}
- PROPOSED-PREREG-ROW-S3-03 — matched-resource (F0) accounting
- PROPOSED-PREREG-ROW-S3-04 — simulation-based power of the complete licensing
  rule incl. the 2×2 mask-source main effect; concept-level inference;
  superiority + equivalence powered separately; 80%-powered effect reported
  (freeze blocker on cluster count)
- PROPOSED-PREREG-ROW-S3-05 — EFFECTIVE non-degeneracy certification, pre-spend
  (admissible gold + certified-incorrect competitor + prefix-forcing audit +
  plausibility/length controls); Rev3: certified SEPARATELY under the K and N
  masks on the common item set
- PROPOSED-PREREG-ROW-S3-06 — registered TOST equivalence margins for BOTH primary
  contrasts (Δ(M_K−T), Δ_mask), each with δ_eq < δ_floor (licensed negative,
  disjoint regions)
- PROPOSED-PREREG-ROW-S3-07 — arm-N matching manifest (coverage, admissible-set
  sizes, bytes, authoring budget, byte-identical machinery, runtime accounting,
  and Rev3 matched SEMANTIC EXPRESSIVITY: relation inventory, axiom families,
  closure/entailment capability, source-quality gates; opponent =
  plain-v5-natural or stronger)
- PROPOSED-PREREG-ROW-S3-08 — matched-arms protocol (abstention availability,
  instructions, stopping rules, budgets, seeds, arm-blind extraction/scoring)
- PROPOSED-CRIT-S3-PRECERT-1 — different-predictions pre-certification (ρ_KN);
  Rev3: failure = not-identifiable-under-THIS-design (not theoretical
  unidentifiability, except literal set identity), and the narrowed headline
  additionally requires a C-MECH PASS
- PROPOSED-CRIT-S3-KILL-1 — C-MECH three-outcome tree (conjunction M_K>T AND
  M_K>G / licensed equivalence-or-harm / INCONCLUSIVE; ordered evaluation,
  disjoint regions)
- PROPOSED-CRIT-S3-KILL-2 — derangement gates: Stage-1 artifact + Stage-2
  implementation, policy-specific, multi-seed
- PROPOSED-CRIT-S3-KILL-3 — C-KERN three-outcome tree on the MASK-SOURCE MAIN
  EFFECT Δ_mask over the 2×2 (simple effects + interaction co-reported; package
  swap demoted to a secondary source-stack reading; ordered evaluation, disjoint
  regions)
- PROPOSED-CRIT-S3-GATE-0 — pilot gates (real-model smoke, overhead, effective
  non-degeneracy under both masks, PRECERT-1 + D artifact gate, $/paired-item
  ceiling)
- FORK-S3-A — RESOLVED-WITH-HIERARCHY: P-strict confirmatory primary;
  P-consistent separately-powered secondary with exposure gate
- FORK-S3-B — primary task family (pilot-decided; store-independent gold binding)

---

## 9. Revision 2 — cross-vendor review corrections applied

The cross-vendor GPT-5.6 review of Rev1 returned NEEDS-REVISION: one central
finding and six supporting. Dispositions:

| # | Finding (compressed) | Disposition | Where |
|---|---|---|---|
| 1 | `source → A → mask` erases kernel provenance: Rev1 could attribute value to the mechanism only, never the kernel; the empty-kernel argument proves "a store," not "this kernel"; G is not a matched-generic control | **ADOPTED (central).** Thesis split C-MECH / C-KERN; arm M_N added (identical machinery, matched non-kernel store, ROW-S3-07 manifest); kernel-specific contrast = M_K − M_N against store-independent gold; PRECERT-1 different-predictions certification with an explicit concession path; G relabelled | §2.1, §3.1, §4.1–§4.3 |
| 2 | Falsifier bundles effects; KILL-1 conflated unbanked with falsified; margin ambiguous; arm protocol unmatched | **ADOPTED.** Conjunction M_K>T AND M_K>G for C-MECH; three-outcome trees (PASS / licensed equivalence-or-harm / INCONCLUSIVE); G-fraction rule withdrawn; margin = observed floor + test-vs-zero (the registered F1-K convention, cited); matched-arms protocol ROW-S3-08 | §3.3, §4.3 |
| 3 | Endpoint missing KOT-HON/1 safeguards; designer-pickable λ; non-degeneracy insufficient; engine-derived gold oracle-favourable | **ADOPTED.** KOT-HON/1 pinned (λ = 3 default pre-pilot, S_2/S_5, co-report vector, answer-rate co-floor / risk–coverage); effective non-degeneracy (admissible gold + certified-incorrect competitor + prefix-forcing audit + plausibility/length controls); store-independent gold or the endpoint renames to closed-world store conformance | §3.2, §3.3, §5.2 |
| 4 | D-collapse mechanically forced under P-strict, not implied under P-consistent; needs policy-specific two-gate structure | **ADOPTED.** Stage-1 offline artifact gate (multi-seed, certified properties) + Stage-2 implementation gate; D never grounding evidence by itself; failed Stage-1 invalidates kernel-content attribution without erasing a valid C-MECH result | §4.1, §4.3 |
| 5 | Power sketch wrong variance model; cluster limit persists; cost under-tagged; API logits-hook feasibility | **ADOPTED.** McNemar sketch withdrawn; simulation-based power of the complete licensing rule; F1-K anchor corrected to the registered C = 96 / n = 1,573 / μ* = +4.09 geometry [MEASURED-as-record: registry/experiments/f1k.json]; Rev1's "C=8 → 0.119" citation re-attributed to the E-GLM/GLM-DROP record (a Rev1 mis-attribution found while applying this fix); cost re-tagged [EXTRAPOLATION] lower bound with omissions listed; $/paired-item measured at bring-up freezes the ceiling; dynamic-logits-hook constraint stated | §5.3, §5.4 |
| 6 | P-strict / P-consistent are not symmetric confirmatory sub-arms | **ADOPTED.** FORK-S3-A resolved-with-hierarchy: P-strict confirmatory primary; P-consistent separately-powered secondary with exposure gate + own D construction; declared hierarchy for multiplicity; the P-consistent-primary alternative surfaced as maintainer question 6 | §7 |
| 7 | Epistemic hygiene: untagged / over-strong claims (§2.1 conclusion, §2.3 "by construction," microseconds forecast, cost as STIPULATED, host-independence) | **ADOPTED.** All five retagged or rewritten; Rev1's self-check item 4 is recorded as FAILED in §10 | §1.3, §2.1, §2.3, §5.4, §6 |

No finding is rebutted. One nuance noted without disagreement: the review's
observation that M−T bundles three effects (format enforcement / vocabulary
restriction / record-axiom semantic restriction) is fully separable only with
further arms (e.g. a Level-A-only mask); Rev2 carries the conjunction
M_K>T AND M_K>G as the registered claim boundary and leaves finer mechanism
decomposition to a follow-on design rather than adding arms to this one
[STIPULATED scoping choice].

---

## 10. Revision 3 — delta-check corrections applied

The GPT-5.6 delta-check of Rev2 returned NEW-DEFECT: three defects in the new
C-KERN design (item 1 load-bearing), plus two PRECERT-1 qualifications and one
freeze note. Everything else was confirmed substantively resolved and is left
undisturbed. Dispositions:

| # | Defect (compressed) | Disposition | Where |
|---|---|---|---|
| 1 | **(Load-bearing)** M_K−M_N was a BUNDLED intervention — text AND mask both swapped — so the confirmatory C-KERN estimand identified the kernel source *package*, never the mask at the sampler seam; demoting M0_K−M0_N to secondary did not repair it | **ADOPTED — option (a), the CROSSED design.** C-KERN confirmatory estimand = the mask-source MAIN EFFECT over the 2×2 {kernel-text, N-text} × {kernel-mask, N-mask} (cells M_K, X_KN, X_NK, M_NN; simple effects + context×mask interaction co-reported); the full-package contrast M_K vs M_NN is demoted to a secondary "kernel-source-stack" reading in package language only. Cost: +2 confirmatory cells (~+25–40% powered-phase inference [EXTRAPOLATION]); the crossed-vs-narrowed fallback (option (b), with C-KERN renamed and all mask-at-the-seam language dropped) is surfaced as maintainer question 7 | §2.1, §3.1, §4.1, §4.3 (KILL-3), §5.4, §7 |
| 2 | Arm-N opponent under-matched (size/budget matching without matched semantic expressivity makes a kernel win too easy) and mis-framed (knull-v2-lineage named instead of the repo's strong successor) | **ADOPTED.** ROW-S3-07 now requires matched SEMANTIC EXPRESSIVITY — relation-inventory breadth, the same axiom families, the same closure/entailment capability (the closure engine runs over the N-store's records too; asserted-only opponents disallowed), source-quality gates — and the candidate opponent is reframed to **plain-v5-natural or stronger** (`docs/next/design/plain-v5-natural-store-contract.md`), with knull-v2 cited only as the measured interchangeability precedent; maintainer question 5 reframed accordingly | §4.2, §7 |
| 3 | The three-outcome regions could OVERLAP (unconstrained δ_eq > δ_floor lets one result license both PASS and equivalence) | **ADOPTED.** Freeze constraint δ_eq < δ_floor (making TOST-equivalence and observed-floor superiority mutually exclusive) PLUS fixed evaluation order superiority → harm → equivalence, first licensed outcome taken; applied identically to KILL-1 and KILL-3 | §3.3, §4.3 |
| + | PRECERT-1 qualifications: (i) nonzero-ρ_min failure = not-identifiable-under-THIS-design, not theoretical unidentifiability (except literal set identity); (ii) the narrowed headline needs a subsequent C-MECH PASS — failed PRECERT alone establishes nothing | **ADOPTED** verbatim into PRECERT-1 and §2.1/§3.1 | §2.1, §3.1, §4.3 |
| + | Freeze note: non-degeneracy certified separately for the K and N masks on the common item set | **ADOPTED** into ROW-S3-05 and GATE-0 | §5.2, §8 |

No item is rebutted. One consequence made explicit rather than left implicit: with
the crossed design, KILL-3's licensing now rides on Δ_mask, so ROW-S3-06's
equivalence margins and the §5.3 power simulation were updated to the same
estimand — a licensing rule and a power target must name the same quantity.

---

## 11. MANDATORY SELF-CHECK (Rev3 re-run — prior revisions' results honestly reported)

Honest record of prior self-checks: **Rev1 item 4 FAILED** (six tagging/attribution
defects, itemised later in this paragraph). **Rev2 items
1–2 were PASS-as-worded but WRONG in substance:** they endorsed M_K−M_N as "holds
the mechanism fixed and varies only the source," which was false as a
mask-isolation claim — both text and mask varied (the delta-check's load-bearing
finding). Rev1's other recorded defects: untagged §2.1 conclusion, untagged §2.3
over-claim, §1.3 forecast stated as fact, §5.4 forecasts tagged [STIPULATED],
untagged §6 host-independence extrapolation, and the §5.3 "C=8 → power 0.119"
citation mis-attributed to F1-K instead of E-GLM/GLM-DROP — all corrected in Rev2
and left corrected here. Rev3 re-run:

1. **Kernel's load-bearing role stated mechanistically, not asserted:** PASS —
   §2.1 states what the seam supports (the STORE is load-bearing; C-MECH) and why
   kernel-MASK-specificity (C-KERN) is carried only by the crossed mask-source
   contrast on a certified different-predictions surface; the Rev2 bundled-estimand
   error is corrected, not papered over.
2. **Priced falsifier vs kernel-as-text fully specified with a kill criterion:**
   PASS — arm T, conjunction licensing (KILL-1) with equivalence/harm branch and
   Rev3 disjoint regions; the kernel-specific falsifier now correctly isolates the
   mask (crossed cells, KILL-3 on Δ_mask, PRECERT-1 with both Rev3
   qualifications).
3. **Shuffled/deranged-kernel control present:** PASS — D^policy unchanged from
   Rev2 (multi-seed, two-gate, policy-specific, evidential scope stated).
4. **Epistemic tags on every load-bearing claim:** PASS — Rev3 added claims are
   tagged ([STIPULATED] design choices incl. the crossed-design adoption;
   [EXTRAPOLATION] on the +25–40% cost delta inside the §5.4 forecast; MEASURED
   citations unchanged); the Rev2 substantive mis-statement (mechanism-fixed
   wording) is corrected in place and recorded here.
5. **No ASM-<number> ids minted:** PASS — labels remain
   PROPOSED-PREREG-ROW-S3-01..08, PROPOSED-CRIT-S3-{PRECERT-1, KILL-1..3, GATE-0},
   FORK-S3-A/B; the single existing-ASM reference (§5.2 pattern citation) is a
   citation only.
6. **No handle/account strings:** PASS — grep for at-sign-prefixed tokens returns
   zero matches.
7. **Nothing committed/registered/frozen/run:** PASS — Rev3 edited in place in the
   design directory; no git action, no registry write, no freeze, no execution;
   the status header states the same.
