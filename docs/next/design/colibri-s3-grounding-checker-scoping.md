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
> commit, per design-agent governance. The next consumer is the cross-vendor review
> gate, then the experiment-designer pipeline.

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
  work is trie intersection. At current kernel scale (≤108 concepts, hundreds of
  facts) this is microseconds and cannot be the bottleneck; at the large-kernel
  scale the token-mask-caching literature says the same engineering is near-zero
  overhead in serving stacks [LIT-claimed, UNVERIFIED-THIS-PASS: XGrammar,
  arXiv:2411.15100, per docs/next/lit/PARSE.sources.jsonl `verified:false` —
  engineering pointer only, non-load-bearing].
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

## 2. Where the kernel is load-bearing by design

### 2.1 The contentless-without-kernel argument (mechanistic, not asserted)

The mechanism's operative object is the admissible set. That set is *computed from
kernel records and from nothing else*: the vocabulary closure is the stratum-2
inventory; the veto semantics are the stratum-3 axiom sidecar evaluated by the pinned
CWA procedure; the grounded set is the stratum-4 closure under the certified rules
engine. Remove the kernel and the mechanism does not degrade — it **vanishes**: an
empty record set compiles to either an all-admitting mask (P-consistent, no
constraints to violate) or an all-blocking mask (P-strict, nothing derivable). This is
categorically different from S1, where the kernel supplies at most a *ranking* that
competes with kernel-free saliency (modal outcome a tie, per the design menu
[MEASURED-as-record: moe-expert-replacement-design-menu.md §2]), and from S2, where a
drafter must be a generative model and the kernel is not one (steer Rank-3 argument).
Here the kernel content **is the program** the deterministic engine runs.

### 2.2 The Law-3 seat

This is the engine seat of the winning topology (neural proposer ↔ formal language ↔
deterministic external engine that owns correctness): the model proposes token
continuations; `kot-axiom/1` + the record closure are the formal language; the
validate/closure engine owns the admissibility verdict. Every verified capability win
in the injection survey is on the symbol side of exactly this seam [LIT-BACKED:
reports/lit-llm-injection-priorart.md §6-§7; Logic-LM/AlphaGeometry template]. The
kernel's strongest seat per the programme's own laws is the engine seat — S3 is that
seat implemented at the sampler.

### 2.3 Mapping onto the four-condition discriminator

The v9 crux requires (i) validated instrument, (ii) powered pre-registered margin,
(iii) kernel-vs-matched-generic by construction, (iv) non-degenerate,
structure-sensitive contrast [MEASURED-as-record: feasibility-synthesis-v9 §5]. The
S3 design can hit all four *by construction*: (i) deterministic, judge-free scoring
(the engine itself scores groundedness; answers scored against engine-certified gold)
— no LLM-proxy validity leg; (ii)/(iv) §4-§5 below; (iii) the format-only-grammar arm
G gives a matched-generic mechanism control and the kernel-as-text arm T gives the
matched-content channel control. No prior programme instrument had all four available
this cheaply; that — not optimism about the number — is the design-level case for S3.

### 2.4 The honest deflators, faced

- **Content-interchangeability (knull-v2).** The T arm may capture nearly all the
  value: models are good at copying constraints from context, and the programme has
  already measured that authoritative content helps regardless of authorship
  [MEASURED: knull-v2]. This is exactly why T is the binding opponent (Law 2) and why
  the kill criterion (§4.3) is written against T, not against a bare baseline.
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

### 3.1 The capability claim under test

On closed-world tasks whose answers lie in the kernel's covered slice, compiling
kernel facts into a hard sampler admissibility mask **adds correctness beyond
supplying the identical facts as prompt text** — by structurally eliminating the
fabrication error class inside constrained spans (P-strict) or the
kernel-contradicted error class (P-consistent), while leaving selection to the model.

### 3.2 Candidate task families (designer picks the primary; FORK-S3-B)

- **T-A: engine-derived entailment QA.** Items whose gold answers are certified by
  the rules engine over the stratum-4 closure (the 858-entailment machinery and the
  item-builder discipline: `docs/next/design/item-builder-v5-contract.md`,
  `generic-store-external-gold.md`). Deterministic external gold; no judge.
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

### 3.3 Primary endpoint — one, and it must be non-tautological

Binding endpoint rule [STIPULATED, and structurally so — proposed for registration at commit]: under P-strict, groundedness/well-formedness inside constrained spans is
**true by construction** — those quantities carry zero information about value and are
forbidden as primary endpoints. The primary endpoint
must be a quantity the mask does not mechanically control: **answer correctness under
honesty-first scoring** on items where the admissible set is certifiably non-singleton
(§5.2), i.e. where the model still has a real selection problem and can still be
wrong.

PROPOSED-PREREG-ROW-S3-01 (estimand + primary endpoint): mean paired difference in
honesty-scored per-item correctness (correct +1; abstain 0; wrong −2 — weights per the
maintainer's programme-wide honesty-first scoring policy [STIPULATED: exact negative
weight in −2..−5 is a designer/maintainer choice]) between arm M (mask) and arm T
(kernel-as-text), over the covered item universe, cluster-balanced over concepts,
deterministic scoring against engine-certified gold. One-sided superiority at a
pre-registered margin δ (anchor: +3.0-point floor for continuity with F1-K's SEOI
[STIPULATED]).

Secondary endpoints (reported, never promoted): grounded-precision of emitted
assertions (informative only under P-consistent — by-construction 1.0 under P-strict);
abstention rate; wrong-answer rate specifically (the honesty-scoring tail);
constrained-span well-formedness in the T/B arms (where it is not by-construction);
full metric vector V incl. mask-side engine compute, prompt-token deltas, tok/s with
and without mask, forced-span draft acceptance (§1.5).

### 3.4 Coverage rider (binding)

Every claim is indexed to the covered slice: coverage 0.3542 molecules-v0 on ONE
pinned corpus [MEASURED: m0b], α_point 0.24 on the WordNet-10k draw [MEASURED: v9 §7],
≤108-concept kernel instance (or the kernel-v1 successor inventory if the F1-K
eligibility machinery lands first — reuse its gates, `f1k-large-kernel-rebuild.md`
§1). A PASS licenses "on kernel-covered closed-world items, the compiled checker beats
the same facts as text" — nothing about uncovered workloads, and no
"natural-coverage" narration.

---

## 4. THE PRICED FALSIFIER (the carried caveat, discharged)

### 4.1 Arms

PROPOSED-PREREG-ROW-S3-02 (arms; all at matched decoding params, matched model,
matched item set, paired):

| Arm | Context text | Sampler mask | What it isolates |
|---|---|---|---|
| **M** (mechanism) | kernel facts as text (same rendering as T) | compiled kernel mask (Level A+B) | the checker mechanism, additive over the same information |
| **T** (kernel-as-text null — the binding opponent) | kernel facts as text | none | Law-2 control: value of *having* the facts |
| **G** (format-only grammar) | kernel facts as text | task grammar with OPEN terminal sets (no kernel enumeration, no axiom veto) | format-forcing / entropy-reduction / span-structure benefit without kernel content |
| **D** (deranged-kernel mask) | kernel facts as text | mask compiled from a type-preserving derangement of the record/axiom set (objects permuted within relation; dose-exact constraint counts) | structure-sensitivity of the instrument (condition (iv)) |
| **B** (text-only null) | no kernel facts | none | the programme's mandatory second null; floors the item set |
| M0 (secondary) | no kernel facts | compiled kernel mask | channel-substitution reading (can the mask replace the text channel); secondary only |

Design rationale, tagged: M-vs-T holds the information channel fixed and varies only
the mechanism — the cleanest attribution of "the checker beats its own content as
text" [STIPULATED]. The mandatory programme controls (two nulls + scramble) map to
T, B, and D respectively; G supplies the matched-generic mechanism for condition
(iii).

### 4.2 Matched-resource accounting

PROPOSED-PREREG-ROW-S3-03: F0-style accounting (design-efficiency-track.md standard).
M and T are token-identical on the prompt side by construction (same rendered facts);
M's extra resource is compile + per-step engine work — measured and reported in V,
with the honest note that it is engine CPU, not model FLOPs. B's shorter prompt is
reported as a token credit, not "free." No arm's win may be narrated without its
resource row. The efficiency co-benefit (forced-span drafting) is reported under M
only if the identical mechanism runs in all its comparisons.

### 4.3 Kill criteria

PROPOSED-CRIT-S3-KILL-1 (**the home-claim falsifier — verbatim candidate**): *if arm M
does not strictly beat arm T on the primary endpoint at the pre-registered margin
(one-sided, δ = +3.0 points, cluster-balanced), the claim "the kernel's home is the
output/logits seam" FAILS its pricing: the S3 seam reverts to unproven, "home" status
is not banked anywhere in programme narration, and the seam ranking of the 2026-07-21
steer must be re-argued from scratch rather than carried.* A T≈M tie is a genuine
deflation, not a near-miss: it would say the facts, not the mechanism, carry the value
— the knull-v2 pattern recurring at this seam.

PROPOSED-CRIT-S3-KILL-2 (instrument validity): *if arm D is within the margin of arm M
on the primary endpoint (deranged content, same-shape mask, no collapse), the
instrument is not measuring grounding — INSTRUMENT-INVALID; no value conclusion in
either direction may be drawn from any arm.* Expected behaviour: D collapses toward
floor on covered items (under P-strict it forcibly excludes gold).

PROPOSED-CRIT-S3-KILL-3 (kernel-content attribution): *if arm G recovers ≥ the
pre-registered fraction (designer sets; anchor ½) of the M−T difference, the win is
format/structure-forcing, not kernel content — the result is reported as a
constrained-decoding win with the kernel NOT load-bearing, and the kernel-specific
claim fails even if KILL-1 passes.*

PROPOSED-PREREG-ROW-S3-06 (negative-direction licensing, learned from the K-3 gap): a
pre-registered futility/equivalence rule ships **in the initial freeze** (e.g. TOST at
±δ on M−T), so a null is a *licensed* negative, not INCONCLUSIVE — the v9 lesson that
a directional-only registration cannot produce a licensed NO-GO
[MEASURED-as-record: v9 §7 "What a defensible verdict requires"].

### 4.4 Gate before spend

PROPOSED-CRIT-S3-GATE-0 (pilot gates, cheapest-decisive-first): (a) mask machinery
end-to-end on a tiny REAL model (never mock-only — the mocks-calibrate-plumbing-not-
semantics lesson [MEASURED-as-record: programme memory/largekern]), including measured
dead-end rate ≈ 0 and per-token overhead; (b) admissible-set non-degeneracy
certification (§5.2) pre-spend; (c) pilot n≈50 items across ≥10 concepts completing
with sane abstention/wrong distributions in ALL arms. Failure of any gate = fix or
stop; no powered spend.

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

### 5.2 Non-degeneracy certification (condition (iv), pre-spend)

PROPOSED-PREREG-ROW-S3-05: for every item, the certified admissible set at the
decision slot has cardinality ≥ k_min (anchor: median ≥ 4, minimum ≥ 2
[STIPULATED]) so the mask cannot mechanically force gold; certification is a
deterministic pre-spend artifact (the ASM-2372 distinctness-certification pattern from
the F1-K freeze, reused as a pattern — no new ASM minted here). Items failing the
check are excluded before randomisation.

### 5.3 Power and clustering

PROPOSED-PREREG-ROW-S3-04 (sketch, designer to finalise): paired M-vs-T on the same
items. For a paired binary read at δ = 3.0 points with plausible discordance ~10–15%,
n ≈ 900–1,500 items gives ~80% power one-sided (McNemar-style back-of-envelope
[STIPULATED sketch — the designer runs the real calculation on pilot discordance]);
anchor n = 1,440 for continuity with F1-K's scale. **Clustering is the known trap:**
if the estimand is cluster-balanced over concepts, effective power rides on concept
count, and the programme has measured a C=8 design at power 0.119 [MEASURED: F1-K
power record via the colibri steer]. With a ≤108-concept inventory (and the F1-K
askability knife-edge showing eligible-inventory can gate a campaign
[MEASURED-as-record: programme memory, ~116 authored kernels]), the designer must
either (a) power at the item level with concept as a variance component and disclose
it, or (b) certify C ≥ the powered cluster count before freeze. This is a freeze
blocker, not a footnote.

### 5.4 Cost

[STIPULATED estimates] Harness build: agentic time, ~$0 model spend beyond smoke
tests. Pilot (GATE-0): ~$5–15. Powered run on the portable host: 6 arms × ~1,440
items × ~0.5k tokens ≈ 4–5M generated tokens on a small model ≈ **~$30–80** GPU/API
depending on host — the F1-K-campaign price class, decisively cheaper than any S1
probe requiring the 370GB estate. colibri/GLM-5.2 deployment replication is a
separate, later line item (box re-provision + wiring; not needed for the verdict).

### 5.5 Honest expectation

[EXTRAPOLATION — flagged, premise of nothing, resolution path = this experiment]:
modal outcome by my read: M beats B clearly; M-vs-T is genuinely uncertain — the
literature says constraints help most where the model is weakest at compliance
(few-shot/small models [LIT-BACKED: arXiv:2305.13971; arXiv:2104.08768]) and the
programme's own content-interchangeability result warns that text may already capture
most of the value [MEASURED: knull-v2]. A T≈M tie on a strong-compliance host with a
licensed equivalence read is a fully reportable negative that would price the "home"
claim honestly — that is the point of running it. Do not size the expectation off
Logic-LM's +39.2% (§2.4).

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
- Portability beyond colibri entirely (llama.cpp grammars, HF logits processors,
  vLLM structured output) means the *scientific* result is host-independent; colibri
  is one deployment target, and its symbol anchors (`gr_admissible`, `gr_feed`,
  `schema_to_gbnf`) survive its own refactor while line numbers do not
  [MEASURED: recon caveats].

---

## 7. Open design forks and maintainer questions

**FORK-S3-A — admissibility policy: P-strict vs P-consistent.** Why uncertain:
P-strict maximises the kernel's load-bearing role but narrows the model's job to
selection (and risks degeneracy if item construction slips); P-consistent is the
deployment-honest checker semantics but its veto fires only on contradicted
assertions, so its effect size rides on how often unconstrained models emit
kernel-contradicted content (unmeasured). Deciding experiment: run BOTH as sub-arms of
M on the same items (marginal cost ~1 extra arm); kill criterion per policy = its own
KILL-1 against T. Recommendation [STIPULATED]: do not choose — the fork is cheap to
measure and the answer is itself programme knowledge (which semantics the kernel's
value lives in).

**FORK-S3-B — primary task family (T-A entailment QA vs T-B contradiction-avoidance).**
Why uncertain: T-A has the cleanest gold but P-consistent may rarely bind on it; T-B
probes the veto directly but needs careful distractor construction. Deciding
experiment: pilot both at n≈50; freeze the one with the better-behaved discordance and
non-degeneracy profile; carry the other as secondary. Kill criterion: a family whose
pilot shows median admissible-set cardinality < 2 or ceiling-level T-arm accuracy
(> 0.95) is dropped as unpowerable.

**Maintainer questions (must be answered before the designer freezes):**
1. Host choice (§5.1): portable-first (recommendation [STIPULATED]: yes — verdict
   needs no colibri box) with colibri replication deferred?
2. Honesty-scoring negative weight within −2..−5 (§3.3) — programme-wide policy call.
3. Whether a licensed K-3-style asymmetry is acceptable here or the TOST rule
   (ROW-S3-06) is mandatory at first freeze (recommendation [STIPULATED]: mandatory —
   this experiment exists to *price* a claim, and pricing requires a licensed
   negative).
4. Inventory: run on the current ≤108-concept instance now, or wait for kernel-v1
   eligibility output (§5.3 clustering interacts with this; recommendation
   [STIPULATED]: gate the freeze on the certified cluster count, not on a calendar).

---

## 8. Label index (for the experiment-designer)

- PROPOSED-PREREG-ROW-S3-01 — estimand + primary endpoint (honesty-scored paired M−T)
- PROPOSED-PREREG-ROW-S3-02 — arms M / T / G / D / B (+ M0 secondary)
- PROPOSED-PREREG-ROW-S3-03 — matched-resource (F0) accounting
- PROPOSED-PREREG-ROW-S3-04 — n/power/cluster plan (freeze blocker on cluster count)
- PROPOSED-PREREG-ROW-S3-05 — admissible-set non-degeneracy certification, pre-spend
- PROPOSED-PREREG-ROW-S3-06 — pre-registered futility/equivalence (licensed negative)
- PROPOSED-CRIT-S3-KILL-1 — M must strictly beat T or the "home" claim fails
- PROPOSED-CRIT-S3-KILL-2 — deranged-mask insensitivity ⇒ INSTRUMENT-INVALID
- PROPOSED-CRIT-S3-KILL-3 — format-only grammar recovers the win ⇒ kernel not load-bearing
- PROPOSED-CRIT-S3-GATE-0 — pilot gates (real-model smoke, dead-end rate, non-degeneracy)
- FORK-S3-A — P-strict vs P-consistent (both run; per-policy pricing)
- FORK-S3-B — primary task family (pilot-decided)

---

## 9. MANDATORY SELF-CHECK

1. **Kernel load-bearing role stated mechanistically, not asserted:** PASS — §2.1
   derives it from what the admissible set is computed *from* (strata 2/3/4 records +
   pinned validate/closure), with the vanishing argument (empty kernel ⇒ no mechanism)
   and the explicit contrast with S1/S2 where the kernel is substitutable.
2. **Priced falsifier vs kernel-as-text fully specified with a kill criterion:** PASS
   — arm T defined (same facts, same rendering, no mask), M-vs-T paired primary
   endpoint (ROW-S3-01), matched accounting (ROW-S3-03), verbatim kill criterion
   PROPOSED-CRIT-S3-KILL-1 including the consequence (home status not banked; steer
   ranking re-argued), plus a licensed-negative rule (ROW-S3-06).
3. **Shuffled/deranged-kernel control present:** PASS — arm D (type-preserving,
   dose-exact derangement) with its own criterion (KILL-2), plus the format-only arm G
   (KILL-3) exceeding the minimum control requirement.
4. **Epistemic tags on every load-bearing claim:** PASS — checked by section; MEASURED
   claims carry verdict/report paths with scope restated (m0b 0.3542 corpus-indexed;
   α_point 0.24 with CI; colibri facts cited to the recon with line-ref caveat);
   LIT-BACKED claims carry arXiv ids + the verifying repo report; design choices are
   tagged STIPULATED; the two EXTRAPOLATIONs (§2.4 ledger-escape prediction, §5.5
   expectation) are flagged, carry resolution paths, and are premises of nothing.
5. **No ASM-<number> ids minted:** PASS — only PROPOSED-PREREG-ROW-S3-* /
   PROPOSED-CRIT-S3-* / FORK-S3-* labels; the two references to existing registered
   assumptions (the F1-K certification-pattern and carrier-validity rows) are
   citations of already-registered entries, and §5.2 states explicitly that no new ASM
   is minted.
6. **No handle/account strings:** PASS — none present (verified by grep for
   at-sign-prefixed tokens; the only match was this self-check item before it was
   rephrased).
7. **Nothing committed/registered/frozen/run:** PASS — this file is written to the
   design directory only; no git action, no registry write, no freeze, no execution;
   status header states the same.
