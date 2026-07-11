# Round-1 architecture critique + synthesis — the recommended portfolio

> **Status: DESIGN document (critique + synthesis) for maintainer review and
> GPT-5.6 counter-review. NOTHING here is frozen, pre-registered, scheduled, or
> run; no registry record, verdict, audit, frozen object, or ASM entry is
> touched; no bead is created by this document (the coordinator beads §B.4
> after review). Proposed assumption entries live in §B.5 IN-DOC ONLY.**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
>
> **Revision 2 (2026-07-11), per the independent GPT-5.6 counter-review
> (`poc/gpt56-review/rev-archsynth-20260711b/last-message.json`, read in
> full):** P2's ceiling and P4's consumption test are de-overstated (neither is
> decisive as first written — P2 is conditional on the abstention-scoring
> freeze and calibration against human semantic gold; P4's bare pass licenses
> closed-inventory compression only, with transfer-shaped repairs added); P7 is
> reclassified as an ingestion/coverage FEEDER dependent on P1, not a peer
> architecture, and its census is costed as annotation work; a P1 G2
> system-seam test (gold-DSL→execution→renderer with per-stage oracle
> ablation + deterministic-template renderer baseline) is added before parser
> training; the W2-drop rationale is corrected (sealed evaluation prevents
> leakage, not amortisation); the M2 kill is restated as non-inferiority +
> Pareto; M3 gains equal-compute learned-expert controls; the portfolio is
> stratified (architectures vs substrate/diagnostics/feeders); a P6 G3
> learned-addressing step and the ambiguity-set executor arm are added.
> Deliverable of the round-1 cross-model architecture exchange: GPT-5.6
> (gpt-5.6-sol) proposed the candidate design space at
> `poc/gpt56-review/arch-propose-20260711/last-message.json` (read in full);
> this document is the chief architect's stress-test of every candidate and the
> synthesised portfolio recommendation.
>
> **Inputs read at source, in full:** the GPT-5.6 proposal (all nine candidates
> K1–K3 / W1–W3 / M1–M3, the capsule representation, cost profiles, falsifiers,
> and its ranked shortlist); `docs/next/programme-3-neurosymbolic-architecture.md`
> rev 2 (the programme + KOT-FAIR/2 measurement framework + H-* families + the
> G1–G5 gate ladder + K-P3v2); `docs/next/feasibility-synthesis.md` (the binding
> evidence); `docs/next/lit/PARSE.md`, `docs/next/lit/RAG.md`,
> `docs/next/lit/EVAL.md` (Phase-0 lit-reviews). Epistemic discipline: every
> load-bearing line carries [MEASURED|STIPULATED|EXTRAPOLATION] on the same
> logical line; every design CHOICE is [STIPULATED]; no EXTRAPOLATION is ever a
> premise. Lit claims are cited through the lit-reviews' own verified ledgers as
> [LIT: PARSE/RAG/EVAL §n] — the primary sources and their verification status
> live in those documents' sources.jsonl files, not here.

---

## 0. The frame I am judging against (the binding evidence, one screen)

- PREMISE: the deterministic engine is exact, fail-closed, µs-cheap, and ports
  across two verticals byte-identically — on its own closed-grammar,
  self-authored substrate only [MEASURED: registry/verdicts/l3a.json 600/600 +
  a5.json 855/855, audits CONFIRMED].
- PREMISE: every measured real-input crossing is negative — l3a-parse 47.6%
  retention (safe), a5-nl 41.6% retention AND the S2 dangerous-wrong kill fired
  (5.0% wrong-with-provenance via the deterministic ROLE_DIR table defect)
  [MEASURED: registry/verdicts/l3a-parse.json + a5-nl.json].
- PREMISE: coverage binds before reachability — 0/1,550 define-lane external
  census, g8 0/1,000 Mathlib, m0b 0.3542 on the friendliest corpus [MEASURED:
  registry/assessments/b-cov-define-lane.json; registry/verdicts/g8.json;
  ASM-0001 (m0b)].
- PREMISE: the one audited end-task SIGN is verifier-offload on FORMAL inputs —
  135M + kernel-verify-retry beats 1.7B-alone by +0.1507 at ~10% cost —
  alignment-confounded, de-confound unrun [MEASURED:
  registry/verdicts/f2b-replicate.json + assessments/f2b-replicate.json
  does_not_license].
- PREMISE: text-delivered grounding measured net-harmful; residual-stream
  delivery reached echo grade with integration unresolved (delivery ≠ use)
  [MEASURED: registry/assessments/nsk1-g2d.json + nsk1-bprime2.json,
  exploratory].
- PREMISE: cross-lingual capsule/compression evidence is a MEMBERSHIP UPPER
  BOUND (~18–42% @10k anchor) with the consumption channel and mint cost
  entirely unmeasured [MEASURED: registry/assessments/a-e2-census.json].
- RUBRIC: every candidate below is judged on five axes — soundness, NL-wall
  honesty, falsifier quality + tiny-scale feasibility, cost realism under
  KOT-SIZE/2 + KOT-COST/2, novelty vs known art — plus the two flag conditions
  the maintainer set: re-badged dead-end, and covered-slice-only (coverage too
  small to move the normalised index) [STIPULATED: this document's rubric].

**Overall verdict on the GPT-5.6 proposal before the per-candidate knives come
out:** its framing sentence — treat the symbolic stack as an *untrusted,
selectively invoked coprocessor*, not a universal replacement — is exactly what
the measured evidence licenses, and its portfolio discipline (G1 ceilings before
mechanism work; G2 oracle before NL training; never promote an oracle result)
restates ASM-0814/0817 correctly [STIPULATED: endorsement]. The proposal's
strength is that six of nine candidates carry genuinely cheap falsifiers and
none hides an outright gold parse — every natural-input candidate names the
parser inside the measured system. That is weaker than "none smuggles a solved
NL boundary": consistency/agreement checks (K2's inversion, K3's two-extractor
rule) do not by themselves establish semantic correctness, P7 contains no NL
query path at all, and an adapter-trained opaque ID (P4) can bake semantics
into its training data — each developed per-candidate below [STIPULATED:
honesty scoping, per the counter-review]. Its weaknesses, developed below:
(i) three candidates are engineering iterations or re-badges rather than new
bets (K1 substrate, W1 GraphRAG-adjacent, W2 materialized views); (ii) it
proposes the capsule representation but leaves its cheapest falsifier — the
one-token consumption test that would begin to price the a-e2 upper bound's
missing consumption leg — OUT of its run order entirely; (iii) NOTHING in the
proposal attacks the
coverage wall itself, which is the programme's single most likely killer
(K-P3v2(1)); (iv) several falsifiers have vacuity or power defects a prereg
would bounce; (v) two candidates' G1 arithmetic is wrong in its favour unless
computed on the normalised index scale [STIPULATED: the critique summary,
argued per-candidate in Part A].

---

# Part A — CRITIQUE, per candidate

Format per candidate: mechanism recap (one line) → the five axes → RULING.

## A.1 K1 — Proof-Carrying Relational Microkernel

*Typed Datalog-like clause store + indexed joins + four-valued answers
{proved, disproved, unknown, conflict} + minimal proof certificates replayed by
a tiny certificate VM.*

- **Soundness.** The mechanism is sound and largely already exists: the
  kot-axiom v0 engine IS a typed clause store with exact deterministic
  evaluation, fail-closed refusal, and provenance [MEASURED: l3a/a5 engine
  PASS]. K1's genuine deltas over the measured engine are (a) four-valued
  answers (the current engine effectively gives proved/refused; explicit
  `disproved` vs `unknown` vs `conflict` is a real upgrade), (b) the
  independently-replayable certificate VM, and (c) validity intervals. The
  hidden assumption is in the *interface* claim: "tiny replayable certificates
  are a better LM interface than passages" presumes the LM can consume a
  certificate — and the programme's only measurements of symbolic-content
  consumption are text-append NET-HARMFUL and residual-delivery echo-without-
  integration [MEASURED: nsk1-g2d/bprime2]. That claim is an unmeasured
  consumption-channel hypothesis, the same shape as the a-e2 gap
  [EXTRAPOLATION, flagged as such].
- **NL-wall honesty.** Honest by deferral: it adopts the two-tier NLB parser
  wholesale and routes uncertainty to `unknown`. It is not itself a boundary
  attack; it inherits P3-E-NLB-1 entirely.
- **Falsifier.** Gold-logical-form depth sweep 1–12 vs equal-information text
  prompting and generic Datalog. Cheap and buildable, but the *depth* half is
  near-certain to pass and therefore buys little information: the engine is
  exact at any depth [MEASURED: l3a/a5] and LM multi-hop decay is established
  art — a gold-parse depth win is the 2019 CLUTRR oracle-diagnostic result
  re-derived [LIT: EVAL §7, CLUTRR GNN-over-oracle-graphs]. The informative
  half is the OTHER comparator: **if generic Datalog matches K1 completely, the
  distinctive claim is dead** — that is attribution-collapse (K-P3v2(4))
  applied at G2, and to GPT-5.6's credit it names this kill itself.
- **Cost realism.** 5–100 MB store + µs–ms queries is consistent with measured
  engine timings [MEASURED: 5.29–7.82 µs/query]; "the parser is the expensive
  component" is honest. The "certificates replace long retrieved contexts"
  cost saving is contingent on the unmeasured consumption channel (above).
- **Novelty / likely failure.** Datalog + provenance semirings + certificate
  checking are known art; GPT-5.6 says so. Most likely failure: coverage —
  K1 is a whole-query architecture and the G1 Δ_max bound will bind at the
  measured near-zero external coverage [MEASURED: 0/1,550; EXTRAPOLATION that
  it binds — that is precisely what P3-D-POWER computes].
- **FLAGS: covered-slice-only.** Not a dead-end re-badge, but not a new bet
  either.
- **RULING [STIPULATED]:** ADOPT AS SUBSTRATE, NOT AS A BET. Fold K1's real
  deltas — four-valued answers, certificate VM, validity intervals — into the
  kernel engineering line as the v1 engine spec (an ALGORITHM_VERSION-class
  change when built). Do NOT spend a G2 experiment on the depth sweep as
  proposed; the generic-Datalog attribution cell survives as a mandatory
  control inside whichever M-level experiment first uses the engine. The
  certificate-as-LM-interface claim is re-routed to the capsule consumption
  falsifier (§B.2.1), where it is actually testable.

## A.2 K2 — Bidirectional Contract Compiler

*Every relation carries forward + inverse operators, role schema, paraphrase
families, metamorphic tests; a parse is accepted only if role binding is
consistent under inversion and contrastive transformation.*

- **Soundness.** This is the strongest kernel-level proposal because it aims at
  the programme's most dangerous MEASURED defect: the a5-nl ROLE_DIR flip that
  produced wrong-with-provenance at 5.0% [MEASURED: a5-nl.json]. Two soundness
  caveats. (i) **Self-consistency circularity:** if the inverse query is
  produced by the same defective mapping that produced the forward parse, a
  systematic direction confusion is *jointly consistent* — GPT-5.6 names this
  as its biggest risk but does not fix it. The fix is an independence
  requirement: the inverse must be derived DETERMINISTICALLY at the IR level
  (invert the typed operator, not the NL) — but note the scope of what that
  buys: deterministically inverting an already-wrong IR catches implementation
  inconsistency, NOT a parser that consistently mapped "A contains B" to the
  wrong relation. And "a structurally different channel" is by itself
  underspecified — a second parser or round-trip renderer can remain
  correlated with the first mapping. The NL-side check must therefore be one
  of two things: (a) explicit enumeration AND execution of the competing
  semantic parses (inverse/role alternatives), answering only on denotation
  agreement — the ambiguity-set executor arm, §B.2.5 — or (b) calibration
  against independent human semantic annotations [STIPULATED: design
  requirement carried into §B.1, sharpened per the counter-review]. (ii) The literature says
  confidence scores can fail exactly on consistent high-confidence inversions
  [LIT: PARSE §4 conformal caveat] — which is why contracts-as-independent-
  check is the right shape and confidence-thresholding alone is not; K2 has
  this right.
- **NL-wall honesty.** Honest — a genuine parser path with the contract layer
  as acceptance criterion, abstention on ambiguity. This is the anti-a5-nl
  architecture stated as a mechanism.
- **Falsifier.** Mostly right, one vacuity defect: "kill if S2 does not fall
  materially at matched ≥0.90 retention" is unevaluable if no threshold ever
  reaches 0.90 retention — which is exactly the possibility P3-E-NLB-1 exists
  to measure. Repair: the kill must be stated on the **risk–coverage curve** —
  contracts must strictly dominate confidence-only on the S2 (dangerous-wrong)
  dimension across a pre-registered coverage band, with per-frame
  both-orientation strata per the PARSE gate-instrument requirements
  [LIT: PARSE §8 P3-D-NLB requirements (1)–(7); STIPULATED repair]. The first
  step — repair the deterministic direction table — is already the a5
  assessment's named fix and costs ~nothing [MEASURED: a5-nl assessment's
  proposed deterministic repair].
- **Cost realism.** <20 MB + 2–4 µs-level executions per accepted query;
  honest, and honest that the parser dominates latency.
- **Novelty / likely failure.** Metamorphic testing + relational lenses +
  contrastive parsing are known; making inverse consistency a mandatory
  runtime safety contract measured on the risk–coverage curve is the
  programme-specific composition. Likely failure: the circularity in (i), or
  the checks converting correct answers into abstentions without separating
  inversions — both are measurable on the same experiment.
- **RULING [STIPULATED]:** KEEP — but it is not a standalone "kernel
  architecture"; it is the contract layer of the NL front-end. MERGE into the
  M1 front-end design (one architecture, §B.1.1) with the independence repair
  and the risk-coverage kill. Its falsifier rides inside P3-E-NLB-1 as a
  pre-registered arm (confidence-only vs confidence+contracts), which makes it
  nearly free.

## A.3 K3 — Abstract-Interpretation Claim Firewall

*Verify atomic claims inside candidate responses against abstract domains
(membership sets, intervals, reachability, type lattices, temporal
constraints); classify must-hold / may-hold / contradiction / out-of-domain;
reject only on contradiction.*

- **Soundness.** The coverage-ceiling argument — a response can contain
  kernel-checkable subclaims even when the whole task is not expressible — is
  the ONLY idea in the proposal that attacks the G1 wall from the mechanism
  side, and it is correct as far as it goes. Two soundness holes. (i) The
  "sound but incomplete" framing is sound only relative to the extracted
  predicate: the abstract check is exact w.r.t. what the claim extractor SAYS
  the span asserts, not w.r.t. what the span asserts — the NL boundary is
  recreated at claim granularity, and GPT-5.6 names this itself. The
  two-structurally-different-extractors agreement rule is a useful mitigation
  and must be mandatory for any rejection, not just "high-confidence" ones —
  but it is a MITIGATION, not a soundness guarantee: structurally different
  models can share systematic semantic errors, so agreement must additionally
  be CALIBRATED against human semantic gold and the joint
  false-rejection/false-agreement risk measured before any rejection is
  trusted [STIPULATED: hardening, strengthened per the counter-review]. (ii) **The firewall is asymmetric and its index
  arithmetic is easy to get wrong in its favour:** a contradiction-only
  firewall cannot ADD correct answers; it can only remove wrong ones (convert
  wrong→abstain) and improve calibration. On an accuracy-dominated
  KOT-AI-INDEX/2 cell its maximum gain is bounded by
  w_b · (share of baseline ERRORS that are covered-contradictions), computed
  on the NORMALISED scale — a far smaller quantity than "coverage of
  subclaims", and the EVAL review already ruled the raw-scale bound invalid
  under normalisation [LIT: EVAL §5.3; STIPULATED: the corrected G1 form for
  firewalls]. Where the firewall genuinely earns index movement is any
  abstention/calibration-scored component — which means its G1 depends on the
  P3-D-INDEX abstention-scoring decision, an open item [LIT: EVAL §8, open
  question 1; dependency flagged in §B.3].
- **NL-wall honesty.** Honest: neural extractor inside the measured system,
  oracle segmentation labelled as the G2 ceiling arm.
- **Falsifier.** The best in the whole proposal: 200 annotated responses,
  oracle-extractor maximum gain, kill at G1 if even perfect extraction cannot
  reach δ₁ — paper-and-annotation, no training, no GPU. Two defects. (a) n=200
  may not power a δ₁-margin LCB on the normalised scale; the annotation batch
  size must come out of the P3-D-POWER arithmetic, not be fixed at 200 a priori
  [STIPULATED; LIT: EVAL §5.3 uncertainty-propagation requirement]. (b) The
  ceiling is NOT decisive before the abstention-scoring rule freezes: the
  firewall's index gain depends on how abstention/calibration is scored
  (an open P3-D-INDEX item, §B.2.3), so pre-freeze the census reports
  SENSITIVITY BOUNDS under the candidate scoring rules — not a promote/kill
  verdict [STIPULATED: decisiveness correction per the counter-review].
- **Cost realism.** 10–200 MB + a tagging pass; "dearer than unconstrained
  generation, cheaper than multi-sample verifier search" is plausible; the
  50–150M tagger, if separate, is real bytes on KOT-SIZE/2 figure (1) — noted
  honestly.
- **Novelty / likely failure.** Abstract interpretation and claim-level
  factuality checking exist separately; the sound-but-deliberately-incomplete
  interpreter as a generation firewall with explicit `unverified` provenance
  is a genuine composition. Likely failure: claim-level coverage turns out no
  better than whole-query coverage (the same near-zero census), or the gain
  lands entirely in metrics the index scalar barely weights.
- **RULING [STIPULATED]:** KEEP AS A CONDITIONAL DIAGNOSTIC CENSUS, not (yet)
  a retained architecture. Run its paper falsifier FIRST among mechanism
  candidates — it is the cheapest test proposed by anyone and its census half
  is informative EVEN IF IT KILLS (it measures the claim-level coverage census
  the programme does not yet have) — with the corrected normalised-scale
  arithmetic, power-sized annotation, and sensitivity-banded (not decisive)
  reading until the abstention-scoring freeze. Promotion from diagnostic to
  architecture additionally requires the agreement-vs-human-gold calibration
  above [STIPULATED: reclassification per the counter-review].

## A.4 W1 — Bitemporal Provenance Hypergraph

*Typed n-ary hyperedges with source spans, extraction method, confidence
class, bitemporal validity, contradiction links; kernel axioms privileged but
challengeable; queries return subgraph + supporting spans.*

- **Soundness.** Internally coherent, and the evidence-span rule ("the graph
  may not become an unsupported answer key") is exactly the f2b answer-key
  lesson applied to store design [MEASURED: f2b-replicate does_not_license].
  But the mechanism stack (n-ary + bitemporal + contradiction links +
  provenance classes) multiplies authoring/extraction schema complexity at the
  precise point the programme is weakest: extraction quality is measured at
  proxy precision ~0.71 [MEASURED: m0a-llmproxy], and the flagship graph-RAG
  literature's own record is that construction cost and error dominate —
  "GraphRAG frequently underperforms vanilla RAG on many real-world tasks";
  neither paradigm uniformly dominates; no flagship paper publishes a complete
  build ledger [LIT: RAG §2–3].
- **NL-wall honesty.** Honest — hybrid retrieval proposes candidates, learned
  linker maps only those, uncertain linking falls back to passage RAG rather
  than inventing an address. Good fail-closed shape.
- **Falsifier.** The 10k-document source-parity two-arm build is the RIGHT
  comparison shape (it is the P3-D-RAGC matched control, verbatim) — but it is
  NOT cheap: an LLM-extracted hypergraph over 10k documents is a real
  construction spend with its own error analysis, and the RAG review says the
  equivalence rules for cross-representation controls have no published
  precedent and must be designed first [LIT: RAG §6 rules 1–5, §7.1]. As a
  first falsifier it is premature: it tests store-representation value before
  any mechanism has passed G2.
- **Cost realism.** 0.1–2 GB *including the source snapshot* — honest, and
  honestly notes build cost must be accounted. Under KOT-SIZE/2 figure (5)
  the construction ledger is where this candidate most plausibly dies
  [EXTRAPOLATION consistent with RAG §3].
- **Novelty / likely failure.** **FLAG: re-badge-adjacent.** Temporal KGs +
  provenance graphs + GraphRAG + KILT-style provenance scoring are all known;
  the joint typed-kernel/evidence design under strict source parity is a
  packaging novelty, not a mechanism novelty. Likely failure: construction
  error/cost dominates query-time benefit — GPT-5.6's own risk line, and the
  literature's modal outcome.
- **RULING [STIPULATED]:** DEFER — do not build in round 1. Salvage three
  pieces now: (i) the schema fields (bitemporal validity, contradiction links,
  provenance/confidence classes) become capsule fields (§B.2.1) so nothing is
  lost; (ii) the source-parity two-arm design is P3-D-RAGC's spec, which
  already exists as a bead; (iii) the structure-vs-passages question is owned
  by P3-E-GNN-1's size×depth sweep + the RAGC control — W1 re-enters at G3+
  only if some mechanism (M1/M2/M3/K3) has passed G2 and needs a world larger
  than the two verticals.

## A.5 W2 — Compiled Path-and-View World

*Mine recurrent relational query plans from training-only traffic; compile
frequent plans into materialized bitmaps/FSTs; generic slow path for the rest.*

- **Soundness.** The database logic is fine in the abstract and the accounting
  is honest. It fails on its premises in THIS programme, three ways.
  (i) **There is no traffic.** "Mine recurrent plans from training-only
  traffic" presupposes a deployed workload distribution; the programme's
  measured workloads are benchmark suites that are diverse by construction, so
  the mined-plan distribution would have to be stipulated into existence
  rather than measured. (Correction of this document's earlier draft, per the
  counter-review: the sealed evaluation does NOT structurally punish
  amortisation — it prevents leakage of evaluation items [LIT: EVAL §4,
  ASM-0812], and relation/operator families mined from training-only traffic
  could legitimately generalise to unseen sealed queries. The premise defect
  is the absence of any MEASURED reuse-heavy workload, not the fairness
  machinery.)
  (ii) **There is nothing to accelerate.** The generic "slow path" engine is
  already 5.29–7.82 µs/query on covered queries [MEASURED: l3a/a5]; compiled
  views buy near-constant time over an engine already at microseconds, at
  store sizes (10²–10³ records) where join fan-out cannot yet hurt. The p95
  claim is real only at graph scales the programme will not reach before R-3.
  (iii) GPT-5.6's own biggest-risk line — "benchmark queries are too diverse
  for view reuse, making this an overfit cache" — is, on the evidence, the
  expected outcome, not a tail risk.
- **NL-wall honesty.** Honest (view-template selection is grammar-constrained
  + contract-checked, fallback to RAG) — but moot given (i)–(iii).
- **Falsifier.** The equal-bytes CLUTRR-vs-views-vs-RAG sweep is cheap, but it
  answers a question whose premise (a reuse-heavy workload) has to be
  stipulated into existence to make the candidate winnable.
- **Cost realism.** 20–500 MB honest; build cost "significant but
  deterministic" honest.
- **Novelty / likely failure.** **FLAG: re-badge of known art** (materialized
  views, regular path queries, adaptive indexing) whose novelty claim is only
  the deployment context — and the deployment context is exactly what the
  programme cannot measure yet.
- **RULING [STIPULATED]:** DROP from round 1. Record one salvage: precomputed
  transitive closures / path automata over the closed relation set are a v1
  ENGINE implementation detail (subsumed by A.1's substrate ruling), not an
  architecture. W2 may be re-proposed at R-3+ if a deployed workload with
  measurable reuse ever exists.

## A.6 W3 — Counterfactual Evidence Mesh

*Store, per assertion, its structured near-miss competitors (inverse, negated,
argument-swapped, temporally-invalid, nearest-confusable); retrieval returns
candidate + competitors; kernel eliminates by exact constraint; answer only on
separation.*

- **Soundness.** Well-aimed: confusable-alternative errors ARE the measured
  dangerous class (ROLE_DIR argument swaps) [MEASURED: a5-nl]. One circularity:
  the contrast generator is "deterministic after schema assignment" — i.e. the
  counterfactuals are generated from the same direction/role tables whose
  defect caused a5-nl; a defective table generates defective contrast sets
  that are blind to exactly the real error. Mitigation is ordering: the
  deterministic ROLE_DIR repair and the K2 contract enumeration come FIRST,
  then meshes are generated from the repaired tables [STIPULATED ordering].
  GPT-5.6's own risk line (robust only to the generator's error taxonomy) is
  the same point made generally, and its named control — generic hard-negative
  training + cross-encoder reranker — is the correct one and must be kept.
- **NL-wall honesty.** Honest (answer only on retrieval-margin + contract
  separation; abstain or return alternatives otherwise).
- **Falsifier.** Good and cheap: add meshes only to the existing directional
  relations, evaluate adversarial argument swaps vs the hard-negative
  baseline. This is the SAME experimental substrate as the K2 falsifier and
  the NLB gate instrument's both-orientation strata [LIT: PARSE §8 req (3),
  (6)] — three birds, one harness.
- **Cost realism.** 1.5–4× assertion index as IDs+deltas: plausible; the
  rerank-over-4–16-alternatives step is honest added latency.
- **Novelty / likely failure.** Hard negatives are known; *executable*
  counterfactual neighbourhoods with provenance is a modest but real
  composition. Likely failure: synthetic contrast sets too easy → robustness
  theatre.
- **RULING [STIPULATED]:** KEEP-AS-MERGED. W3 is not a world-model; it is the
  materialised form of K2's contrastive alternatives. Merge K2+W3 into one
  contract-and-contrast layer inside the M1 front-end (§B.1.1); the mesh cell
  (mesh vs generic hard negatives) rides as an arm in the same P3-E-NLB-1
  experiment.

## A.7 M1 — Selective Canonicalizer–Executor–Renderer

*Two-tier NL→canonical-utterance→DSL parser (grammar-constrained, multi-
candidate, execution-aware selection, contracts), deterministic execution,
copy-constrained renderer (entity/value spans copied; only connective language
generated).*

- **Soundness.** This is the H-PS family (programme rev-2 §3.3a) made concrete,
  and it is the right #1: it attacks the only measured wall directly and every
  ingredient is the strongest-recipe item from the PARSE review (canonical
  utterances, fine-tuned 110–360M parser, grammar-constrained decode, inverse
  tests, split-source calibration, frozen threshold) [LIT: PARSE §2, §6, §8].
  Two soundness sharpenings. (i) **Execution-aware selection must not launder
  correctness:** a direction-flipped candidate executes perfectly; MBR-EXEC-
  style agreement can elect a consistently-wrong majority [LIT: PARSE §3
  MBR-EXEC caveat] — selection may prune invalid candidates but the S2 budget
  is carried by the contract layer + calibration, never by execution success
  [STIPULATED design law, restating PARSE §3/§5c]. (ii) **The renderer is a
  measured-risk component, not a formality:** the only measured attempt to
  have a host verbalise engine output was net-harmful [MEASURED: nsk1-g2d
  0.76→0.43 on append]; the copy-constrained renderer is GPT-5.6's genuinely
  novel contribution here and must carry its own endpoint (renderer corruption
  rate on checked results ≈ 0 at pre-registered n) inside the falsifier —
  GPT-5.6 names "renderer exactness"; make it a primary, not a note
  [STIPULATED].
- **NL-wall honesty.** This IS the wall attack; fully honest — it must clear
  ≥0.90 retention + S2 before any W1 attempt, stated verbatim in the proposal.
- **Falsifier.** Fine-tune a ≤220M parser on the two existing verticals with
  K>1 disjoint-source paraphrases; frozen threshold; joint retention/S2 read.
  This is P3-E-NLB-1, independently re-derived — convergent with the
  programme's own design, which raises confidence in the experiment's shape
  [STIPULATED]. It must inherit the full PARSE gate-instrument spec (S2
  definition, four-way data separation, per-frame strata, both-orientation
  tests, shift stress on the guarantee) [LIT: PARSE §8 requirements (1)–(7)].
  Cost: one parser fine-tune — inside the R-1 free-pool envelope.
- **Cost realism.** Shared 135–360M host + 5–50 MB adapters/grammar assets;
  2–8 short DSL candidates ≪ best-of-N NL chains; honest and plausible.
- **Novelty / likely failure.** PICARD/canonical-parsing/execution-guided
  decoding are known; the safety-critical composition (contracts + copy-
  renderer + frozen risk threshold at tiny scale) is the programme-specific
  novelty. Likely failure: systematic high-confidence direction errors defeat
  calibration — the named residue class [LIT: PARSE §5c] — which is exactly
  what the merged K2 contract layer exists to catch independently.
- **RULING [STIPULATED]:** KEEP as portfolio #1, merged with K2+W3 into ONE
  front-end architecture (§B.1.1). This is where the programme lives or dies
  (K-P3v2(2)), and the proposal's version is the strongest concrete design on
  the table.

## A.8 M2 — Symbolic Speculative Decoding

*Kernel compiles current formal state into allowed continuations / forbidden
claims; draft accepted in blocks while compatible; rollback + mask at
violation; uncovered spans decode normally, marked unverified.*

- **Soundness.** This is H-RULE-CD (engine-derived continuation sets delivered
  by masking — rev-2 §3.3's first-ordered placement) plus a real delta: block-
  speculative acceptance with rollback, which converts full-answer retry into
  in-flight repair. Three seams need naming. (i) **Mid-decode addressing is
  the NL boundary again:** deciding WHICH spans have a formal state is a
  selective-parser problem; a mask applied to a mis-addressed span
  manufactures a5-nl-class wrong-with-provenance INSIDE generation. GPT-5.6's
  rule — no symbolic masks when addressing is uncertain — is the right
  fail-closed law and must be a frozen design invariant, not a preference
  [STIPULATED]. (ii) **Distributional distortion:** rollback + local masking
  changes the sampling distribution; the prior lit review's local-vs-global
  mask divergence check on our tiny closed grammar applies verbatim before
  freeze [LIT: PARSE §4 P-GCD/GAD caveat + non-recommendation]. (iii) On
  code/tool grammars the formal state arises from syntax directly — that is
  the honest domain where this candidate is strongest, and it matches where
  the programme's evidence is strongest (formal inputs).
- **NL-wall honesty.** Honest: NLB-gated for general NL, syntax-grounded for
  code/tool. **FLAG: covered-slice-only** for its accuracy claims — on the
  real index it inherits the G1 coverage bound exactly like H-VL.
- **Falsifier.** Strong and cheap: on the existing formal slice, four-arm
  comparison (unrestricted / grammar-only / full-answer verify-retry / M2) at
  matched output tokens and resource vector. One repair: GPT-5.6's kill —
  "beats verify-retry on none of {error, tokens, p95}" — is too permissive as
  a survival rule, since "any improvement on any axis" can preserve a
  DOMINATED system (slightly fewer tokens with materially worse accuracy).
  Restate per the programme's own frontier discipline [rev-2 §4 G4 /
  ASM-0806 Pareto endpoint]: M2 survives only if accuracy AND S2 are
  non-inferior to verify-retry at pre-registered margins AND it materially
  improves ≥1 resource axis — equivalently, Pareto dominance over the full
  vector, never single-axis wins [STIPULATED: kill repair per the
  counter-review]. No training; extends the existing f2b harness; builds
  directly on the one audited SIGN [MEASURED: f2b-replicate]. Labelled
  oracle/formal-diagnostic, no W1 claim — correct.
- **Cost realism.** 1–20 MB integration; the CPU/GPU synchronisation risk is
  named honestly and is exactly what KOT-COST/2 (i) inter-token latency was
  built to price [STIPULATED: ASM-0810 vector applies].
- **Novelty / likely failure.** Grammar-constrained + speculative decoding are
  established; *semantic-state-dependent* speculative acceptance with proof
  provenance is a real seam novelty. Likely failure: throughput death by
  synchronisation, or the gain over external verify-retry being ~0 (the
  external loop is already cheap).
- **RULING [STIPULATED]:** KEEP as the concrete design of H-RULE-CD
  (P3-E-RULE-1's first placement), run on the formal slice after the
  K3 paper kill and the NLB arm are in flight. Its Pareto endpoint vs H-VL is
  already the rev-2 §3.3 endpoint — no new gate machinery needed.

## A.9 M3 — Routed Symbolic-Expert MoE

*Small transformer + router; tokens can invoke neural MLP, graph-query expert,
or deterministic rule expert consuming typed capsules and returning fixed-width
residual updates + certificate IDs; trained with proof-trace distillation +
sparsity penalty.*

- **Soundness.** The highest-upside bet and the one sitting directly on the
  programme's least resolved seam: the bridge from typed capsule to residual
  update is a learned encoder — the same channel class nsk1 measured at
  echo-grade delivery WITHOUT integration [MEASURED: nsk1-bprime2, R− rescue
  0/8]. GPT-5.6 names "the network ignores the expert" as the biggest risk and
  correctly matches it to the programme's delivery-without-use result. Two
  sharpenings. (i) The falsifier's endpoint must be CAUSAL-behavioural on
  held-out compositions (the rev-2 R4 mitigation), and the
  shuffled-certificate control it names is the right minimal derangement —
  keep both. (ii) Routing sparsity + "router may not invent symbolic
  addresses" is honest, but note the training-cost asymmetry: interface-
  present twins + proof curricula are a real training-spend multiplier that
  KOT-LIFE/1 must book (GPT-5.6 says training is dearer than inference —
  honest).
- **NL-wall honesty.** Honest and explicitly gated: candidate addresses come
  from the NLB parser/retriever; router confidence is declared NOT a
  substitute for NLB clearance; G2 gold capsules, G3 measures the addressing
  loss. This is ASM-0814 discipline verbatim.
- **Falsifier.** 10–30M twins at three widths on procedural D4, oracle
  capsules, plain vs text-evidence vs symbolic-expert arms, direction-of-
  effect read across widths. This IS the H-GU ≥3-point direction protocol
  [STIPULATED: ASM-0815 restated] with the MoE variant chosen from rev-2
  §3.5's variant list — well-formed, R-0-cheap, kill conditions correctly
  direction-based (flat-negative or shrinking-to-zero kills; growing promotes).
  One missing control, mandatory: the plain / text-evidence /
  shuffled-certificate arms do not isolate DETERMINISTIC SYMBOLIC EXPERTISE
  from extra parameters, privileged proof supervision, or conditional compute
  per se. Add two equal-compute controls — (a) a matched LEARNED neural expert
  (same router, same added params, same conditional-compute budget, no
  symbolic engine) and (b) a generic typed-store expert — so a symbolic-expert
  win is attributable to the symbolic content, not to capacity or routing
  [STIPULATED: control added per the counter-review].
- **Cost realism.** 5–30M router/bridge params, sparse activation ≈ dense-
  backbone average inference: plausible. The capsule tokenisation cost is
  unpriced — it depends on the capsule consumption format, which is unmeasured
  (§B.2.1 fixes the ordering).
- **Novelty / likely failure.** Tool-routing/MoE/NMN/differentiable logic are
  known; a certificate-carrying deterministic expert as conditional compute
  evaluated for scaling DIRECTION is a genuine composition. Likely failure:
  delivery-without-use, again.
- **RULING [STIPULATED]:** KEEP as the single high-upside training bet — it
  BECOMES the concrete design of P3-E-GU-1 (do not also run a generic H-GU
  arm in round 1; that would be two spends on one hypothesis). Sequence it
  AFTER the capsule consumption falsifier (§B.2.1) so the expert's input
  format is a measured object, not a guess, and last in the GPU queue per
  GPT-5.6's own ordering, which is correct.

## A.10 The Typed Evidence Capsule (cross-cutting representation)

- **Soundness.** One representation serving as kernel instruction, world node,
  retrieval unit, LM input, cache key, and audit unit is architecturally
  attractive and — critically — makes the §2.2(2) factorial controls cheap by
  construction (passages / triples / contract-less capsules / full capsules
  derived from one frozen snapshot). That is a real methodological asset.
  Risk: **premature unification** — freezing a ten-field schema before any
  mechanism has passed G2 invites schema lock-in and silent rework; the
  capsule should version like the encoder (content-hash pinned, version-bumped
  deliberately) [STIPULATED, consistent with the encoder-pin convention].
- **The missed trick (GPT-5.6's own best idea, left out of its run order):**
  the multilingual capsule-ID consumption test — map aliases to one ID,
  deliver a short code/learned token, measure task-accuracy non-inferiority —
  is EXACTLY the K-A3-shaped consumption measurement that the a-e2 census
  names as the missing leg of the compression evidence [MEASURED:
  a-e2-census.json — consumption channel entirely unmeasured]. It is cheap
  (adapters on existing 135M/360M hosts). Two scope corrections to what a pass
  means [STIPULATED: per the counter-review]. (i) **Memorization is itself a
  possible oracle:** an adapter-trained one-token ID can succeed by memorising
  a closed record→embedding lookup; that shows nothing about consuming unseen
  or versioned capsules, compositional capsule fields, proof certificates, or
  M3 expert residuals. A bare pass therefore licenses CLOSED-INVENTORY
  COMPRESSION evidence only; validating the input format M3 and K1's
  certificate-interface claim depend on requires the transfer-shaped arms of
  §B.2.1 (held-out identities, held-out field compositions, causal field
  perturbations, shuffled ID/content mappings). (ii) **"Matched information"
  is not automatic:** the ID's semantics reside in the adapter's training data
  and parameters, whose bytes and training cost MUST be charged to the
  capsule arm under KOT-SIZE/2 / KOT-LIFE/1. GPT-5.6 states the experiment and
  then never schedules it. Promoted, with these repairs, to the round-1 run
  order in §B.3 [STIPULATED].

## A.11 GPT-5.6's own run order — assessment

Its five-step order (K2+M1 → K3 ceiling → M2 vs verify-retry → W2 → M3+W1)
is 80% right. Corrections [STIPULATED]: (1) K3's paper ceiling is CHEAPER than
the K2+M1 fine-tune and informs a whole mechanism class — it goes first among
mechanism tests, alongside (not after) the NLB line, and both behind the ~$0
G1 Δ_max computations that gate everything (rev-2 §4 already orders this) —
though its reading stays sensitivity-banded, not decisive, until the
abstention scoring freezes (A.3, §B.3 step 2);
(2) W2 is dropped (A.5) — its slot goes to the capsule consumption falsifier
(A.10); (3) W1 is deferred out of round 1 entirely (A.4) — M3's oracle-capsule
twins do not need the hypergraph, they need capsules; (4) the closing
discipline paragraph ("if the NLB redesign fails its joint gate after the
registered cycles, the surviving programme is formal code/tool interfaces,
internal verification instruments, and compression diagnostics") is correct
and matches K-P3v2(2)/(5) — adopted as the shared expectation for the
negative branch [STIPULATED: endorsement].

---

# Part B — SYNTHESIS: the recommended portfolio

## B.1 The portfolio (keep / merge / drop), with what changed and why

| # | Portfolio entry | Built from | Status vs GPT-5.6 | What I changed |
|---|---|---|---|---|
| P1 | **CONTRACT-FRONT-END** — selective canonicalizer→DSL parser + bidirectional contracts + counterfactual contrast meshes + ambiguity-set executor + copy-constrained renderer | M1 + K2 + W3 (merged) | KEEP, merged | Inverse channel must be IR-level deterministic AND the NL-side check independent (ambiguity-set execution or human-annotation calibration — A.2 repair, §B.2.5); K2 kill restated on the risk-coverage curve; W3 meshes generated only from the REPAIRED direction tables; renderer corruption rate a primary endpoint (nsk1-g2d); NEW G2 system-seam test before parser training (gold DSL→execution→renderer, per-stage oracle ablation, deterministic-template renderer baseline — §B.3 step 3); full PARSE §8 gate-instrument spec inherited |
| P2 | **CLAIM-FIREWALL** — abstract-interpretation verification of atomic claims in responses | K3 | KEEP AS CONDITIONAL DIAGNOSTIC CENSUS (not yet an architecture) | G1 arithmetic corrected to normalised-scale error-bounded form (A.3); annotation n power-sized by P3-D-POWER; two-extractor agreement mandatory for ANY rejection AND calibrated vs human semantic gold (joint false-rejection risk measured) before promotion; ceiling reading sensitivity-banded, NOT decisive, until the P3-D-INDEX abstention-scoring freeze |
| P3 | **SYMBOLIC-SPECULATIVE-DECODE** — engine-derived continuation masks + block-accept/rollback, formal/code slice first | M2 (= H-RULE-CD concretised) | KEEP | Fail-closed no-mask-on-uncertain-address frozen as a design invariant; local-vs-global mask divergence check pre-freeze; kill restated as accuracy/S2 non-inferiority + material resource improvement (Pareto), never any-single-axis survival (A.8); scoped honestly as covered-slice/formal until NLB clears |
| P4 | **CAPSULE + CONSUMPTION TEST** — versioned typed-evidence-capsule schema (absorbing W1's bitemporal/contradiction/provenance fields) + the one-token/short-code consumption falsifier, transfer-repaired | Capsule section + A-E2's missing leg (my addition of the test to the run order) | ADDED to run order, as a representation+interface EXPERIMENT (not a peer architecture) | The schema is content-hash versioned, not frozen-forever; the test is REPAIRED against the memorization oracle: held-out capsule identities + held-out field compositions, causal field perturbations, shuffled ID/content mappings, full adapter/vocabulary/training-cost accounting charged to the capsule arm; a bare seen-inventory pass = closed-inventory compression evidence ONLY — the K1-interface/P6-format reading requires the transfer arms (A.10) |
| P5 | **VERIFIER-LOOP (standing)** — H-VL as already designed in rev-2 §3.1 | programme rev-2 (GPT-5.6's M2 comparator) | unchanged | No change; P3 (M2) is measured AGAINST it on Pareto frontiers per ASM-0815 — H-VL is the incumbent, not a new spend |
| P6 | **ROUTED SYMBOLIC EXPERT** — MoE twins with deterministic rule/graph experts over capsules, ≥3-width direction protocol | M3 (= the chosen H-GU variant) | KEEP, sequenced last | Becomes THE P3-E-GU-1 design (no parallel generic H-GU arm); blocked by P4's transfer result; causal-behavioural endpoint + shuffled-certificate control mandatory; PLUS equal-compute matched learned-expert and generic typed-store controls (A.9); explicit P6 G2→G3 edge — a learned-addressing degradation experiment (§B.3 step 9) is REQUIRED before any natural-input promotion |
| P7 | **DETERMINISTIC-EXTRACTION INGESTION FEEDER** — grow store coverage where extraction is structurally grounded (code, schemas, tables, structured data), scaling the measured a5 authoring route | **NEW — GPT-5.6 missed the coverage gap** (§B.2.2) | ADDED as an ingestion/coverage FEEDER, not a peer architecture | Feeds the G1 coverage wall — the top programme-kill risk no GPT-5.6 candidate addresses — but contains NO NL query path: every natural-query use depends on P1 (or a syntax-grounded tool API); semantic typing of NL labels in tables/schemas is NOT deterministic and needs per-source-class precision measurement; the κ census is costed annotation work, not ~$0 CPU (§B.2.2) |
| — | K1 microkernel | K1 | ADOPT AS SUBSTRATE | Four-valued answers + certificate VM + validity intervals → v1 engine spec; not an experiment bet; generic-Datalog attribution cell kept as a control |
| — | W1 hypergraph | W1 | DEFERRED | Schema fields → P4 capsules; comparison design → P3-D-RAGC; re-enters at G3+ only behind a G2-positive mechanism |
| — | W2 compiled views | W2 | DROPPED | No measured reuse-heavy workload; engine already µs (nothing to accelerate at round-1 scale); rationale corrected per A.5 — sealed eval prevents leakage, it does not defeat amortisation; salvage = engine implementation detail (A.5) |

- PORTFOLIO RULING (stratified — calling all seven a single "architecture
  portfolio" would obscure which entries can actually beat a resource-matched
  baseline [STIPULATED: stratification per the counter-review]):
  - **Architecture bets (can win a G4 W1 comparison):** P1 the
    programme-critical path (P3-E-NLB-1 + P3-D-PS made concrete); P3 measured
    against P5 on the formal/code slice; P6 the single late speculative
    training bet.
  - **Incumbent:** P5 (H-VL) — the comparator, not a new spend.
  - **Supporting work, NOT peer architectures:** P2 a conditional diagnostic
    census; P4 a representation + interface experiment; P7 an
    ingestion/coverage feeder (dependent on P1 for any natural use); K1
    substrate engineering.
  - P2 and P4 remain the two cheapest NEW tests, but neither is decisive as
    first written: P2's ceiling is sensitivity-banded until the
    abstention-scoring freeze, and P4's bare pass licenses closed-inventory
    compression only [STIPULATED: the round-1 portfolio choice].

## B.2 What GPT-5.6 missed (added by this synthesis)

### B.2.1 The capsule consumption falsifier, scheduled (P4) — transfer-repaired

Already argued at A.10. Shape [STIPULATED]: on the two existing verticals,
deliver the same record content to a 135M/360M host four ways —
(a) full text gloss, (b) capsule as structured text, (c) capsule as
short-code/single-token ID (adapter-trained), (d) no delivery — and measure
task accuracy + prefill tokens, with the adapter/vocabulary bytes and training
cost of arm (c) charged to it explicitly (the ID's semantics live in the
adapter, so (a) and (c) are NOT automatically matched information — A.10).
Repairs against the memorization oracle [STIPULATED: per the counter-review]:
mandatory arms for HELD-OUT capsule identities and HELD-OUT field
compositions, causal field perturbations (flip a field, the answer must
change), and shuffled ID/content-mapping controls. Reading discipline:
non-inferiority of (c) vs (a) on the SEEN inventory is evidence for
closed-inventory compression only; only the held-out/compositional arms speak
to the consumption channel that K1's certificate-interface claim and P6's
input format depend on; inferiority everywhere kills the one-token channel at
scope. Either way the a-e2 membership bound gains its first consumption-side
measurement. Cheap GPU (adapters, no pretraining); labelled oracle-diagnostic
(addresses are given, not parsed) [STIPULATED: ASM-0814 labelling applies].

### B.2.2 P7 — the Deterministic-Extraction Ingestion Feeder (the coverage input)

Every GPT-5.6 candidate treats the store as given; the programme's most likely
death is K-P3v2(1), coverage [MEASURED: 0/1,550 define-lane; g8 0/1,000].
The one authoring route that has ever scaled in this programme WITHOUT human
explication or LLM extraction is the a5 world layer: a typed world extracted
deterministically from code structure, supporting 855 covered queries with a
pure desugaring layer [MEASURED: registry/verdicts/a5.json — no-LLM-extracted
code world]. P7 generalises that measured precedent [EXTRAPOLATION, and the
falsifier below is what tests it]: build deterministic (non-LLM) extractors
for source classes whose structure carries the semantics — code (imports,
call/containment graphs, type signatures), schemas, tables/infoboxes,
configuration — and compile them into capsule stores, accepting that
unstructured prose stays uncovered. The strategic alignment is the point: the
domains where deterministic extraction works (code/tool/structured) are the
SAME domains where the NL boundary is most tractable (syntax-grounded, M2's
honest domain) and where the verifier-offload sign lives — the portfolio's
coverage, reachability, and mechanism levers concentrate on one slice instead
of diluting across all of NL [STIPULATED: the design rationale].

Three classification corrections [STIPULATED: per the counter-review]:

- **P7 is a feeder, not an NL architecture.** It may improve store coverage;
  it does not get an NL request INTO that store. It contains no NL query path:
  every natural-query use of a P7-built store depends on P1 clearing NLB, or
  on a syntax-grounded tool API. The dependency edge P7→P1 is explicit
  (ASM-0814 / rev-2's blocking rule applies to any natural-input use of P7
  output). It is the ingestion-side face of the coverage-growth feeder line,
  not an independent coverage-SOLVING architecture.
- **Deterministic extraction ≠ deterministic semantic typing.** Tables,
  infoboxes, configuration keys, and schemas routinely carry natural-language
  labels; extracting the structure deterministically does not make the
  semantic TYPE assignment of those labels deterministic. Per-source-class
  type-assignment precision must be measured on the blind sample, and
  source-class-specific lifecycle/build-effort accounting booked (KOT-LIFE/1).
- **The κ census is annotation work, not ~$0 CPU.** Judging whether the store
  captures an item's "decisive content" is human labelling that can itself
  drift into an oracle exercise; the census is therefore a COSTED annotation
  protocol (power-sized with P3-D-POWER, blind-sampled, with the
  authoring/build-effort census attached) — cheap relative to GPU work, but
  not free, and its extraction-precision leg is measured, not assumed.

- **Cheapest falsifier (feeds G1 for every store-dependent family):**
  pick one pinned external corpus per source class; measure κ (fraction of a
  target benchmark/suite's items whose decisive content the extractor
  captures) and extraction + type-assignment precision on a blind annotated
  sample; the deliverable is the Δ_max input P3-D-POWER needs, per source
  class. Kill per class if κ stays ~0 at acceptable precision — the same
  census shape that killed Lean minting cleanly [MEASURED: g8's census-shaped
  kill as the precedent].
- Relation to existing work: this is the same line as
  `docs/next/coverage-growth-ingestion-plan.md` (P7 extends the existing
  feeder, it does not found a new architecture family); costs book to
  KOT-LIFE/1 as store-construction per rev-2 §1.3a.

### B.2.3 The abstention-scoring dependency (a gate defect no candidate names)

P1, P2, and P5 are all SELECTIVE systems: they abstain by design. The index's
abstention scoring is an open P3-D-INDEX item [LIT: EVAL §8 open question 1 —
no chance-to-ceiling transform exists for abstention/calibration metrics].
Until it is registered, any G4 comparison of a selective architecture is
gameable in either direction (abstention as free error-avoidance, or abstention
as pure score loss). Recommendation: the P3-D-INDEX freeze must register the
abstention scoring rule BEFORE any selective candidate's G4 prereg freezes;
this is a new named dependency edge, not new machinery [STIPULATED].

### B.2.4 One negative-space note (no new spend)

The cascade/router idea (small model answers; escalate on kernel-check
failure) is conspicuously absent from GPT-5.6's list — correctly so: HE2
cascade-dominance is measured DEAD at scope [MEASURED: registry/verdicts/f2.json
HE2]. Recording the absence so nobody re-proposes it as "missed"
[STIPULATED: negative-space record].

### B.2.5 The ambiguity-set executor (added per the counter-review; rides in P1)

The counter-review's strongest addition, adopted as an arm of the P1 design
[STIPULATED: adoption]: produce a CALIBRATED SET of plausible DSL parses per
input — explicitly including the inverse/role alternatives that produced the
a5-nl ROLE_DIR failure [MEASURED: a5-nl.json] — execute ALL of them on the µs
engine, and answer only when their denotations agree; otherwise clarify or
abstain. This attacks the measured failure class WITHOUT assuming that
self-consistency of a single selected parse proves semantic correctness, and
it is the concrete form of A.2's independence repair (channel (a)): the
competing semantic parses are enumerated and executed, not re-derived by the
same mapping. It is cheap — the engine is µs-level [MEASURED: 5.29–7.82
µs/query], so executing 2–8 candidates costs ~nothing — and its endpoint is
the same risk–coverage curve as the other P1 arms: ambiguity-set agreement vs
confidence-only vs confidence+contracts vs mesh/hard-negative, all inside the
P3-E-NLB-1 harness (§B.3 step 4).

## B.3 The run order (cheapest-falsifier-first, mapped to G1–G5)

All rung/gate discipline per rev-2 §4; oracle-input stages labelled
`oracle-diagnostic`, licensing no W1 claim [STIPULATED: ASM-0814 applies
throughout]. "Gates" = which portfolio entries the step can kill or unblock.

| Step | Test | Gate | Cost class | Gates |
|---|---|---|---|---|
| 0 | **G1 prerequisite freeze + Δ_max computations** (P3-D-POWER): FIRST freeze the arithmetic's prerequisites — the R-1 suite, domain weights, normalisation constants, δ₁, and baseline accuracies; then the whole-query bound for P1/P3/P5 (on the NORMALISED scale: if `w_b` does not already fold in the chance-to-ceiling derivative and domain macro-weight, the whole-query formula needs the same normalisation as P2's — not only P2's); the corrected error-bounded firewall form for P2; P7's per-source-class κ census SCOPED and costed as an annotation protocol (§B.2.2), not assumed ~$0 | G1 | ~$0 CPU/paper + costed annotation | everything store-dependent; K-P3v2(1) input |
| 1 | **Deterministic ROLE_DIR repair** [MEASURED: a5-nl assessment's named fix] + exhaustive deterministic both-orientation table tests + directional-frame enumeration. NOTHING ELSE: the confidence-vs-contract and mesh-vs-hard-negative COMPARISONS need parser outputs (and possibly training) and move into step 4 — they are not a CPU-only step | pre-G3 instrument | ~$0, existing engine + CPU | P1 (its S2 leg); P3's mask-address safety |
| 2 | **P2 paper ceiling, sensitivity-banded**: power-sized annotation of atomic claims in real model answers; oracle-extractor max gain reported as BOUNDS under the candidate abstention-scoring rules — a promote/kill reading is BLOCKED until the P3-D-INDEX abstention scoring registers (§B.2.3) | G1 | annotation only | P2's census leg (its verdict waits on the scoring freeze) |
| 3 | **P1 G2 system-seam test (NEW, before any parser training)**: gold DSL/parse → execution → renderer on the two verticals, with SEPARATE oracle ablation of DSL serialization, execution, and rendering (a single aggregate gold-parse arm cannot localise correlated errors [LIT: PARSE §8 P3-D-ORACLE: stage-by-stage oracle ablation required]); includes the deterministic-TEMPLATE renderer baseline — on the closed typed grammar, templates may eliminate the symbolic→NL seam entirely, and the learned copy-constrained renderer survives only if it adds measured value at ~0 corruption | G2 `oracle-diagnostic` | ~$0–50, engine + CPU/small | P1's renderer + seam legs; the renderer-corruption primary |
| 4 | **P1 = P3-E-NLB-1**: ≤220M parser fine-tune, two verticals, K>1 disjoint-source phrasings, four-way data split, frozen threshold, joint ≥0.90 retention + S2 read; the contract, mesh-vs-hard-negative, AND ambiguity-set-executor arms (§B.2.5) ride here on one risk-coverage harness | G3-instrument | ≤~50 GPU-h (R-1 free pool) | EVERY natural-input store leg (ASM-0814); K-P3v2(2) |
| 5 | **P3 vs P5 (verify-retry)**: four-arm formal-slice comparison at matched resource vector (extends the f2b harness); no training, so it runs BEFORE or PARALLEL WITH step 4 — it directly tests the mechanism tied to the only positive sign; kill per the A.8 non-inferiority + Pareto rule | G2 `oracle-diagnostic` | ~$0–100, no training | P3; feeds the H-RULE-CD vs H-VL Pareto endpoint (ASM-0806) |
| 6 | **P4 repaired consumption/transfer test**: four-way delivery + held-out identities/compositions, causal field perturbations, shuffled-mapping controls, full adapter accounting (§B.2.1) | G2 `oracle-diagnostic` | cheap GPU (adapters) | P6's input format (via the TRANSFER arms); the a-e2 consumption leg; K1's interface claim (scoped) |
| 7 | **P2 real-extractor leg** (iff the step-2 ceiling survives its sensitivity band AND the abstention scoring has registered): contradiction precision vs a same-size learned NLI verifier + agreement calibration vs human semantic gold (A.3) | G3 | cheap-moderate | P2 promotion from diagnostic to architecture |
| 8 | **P6 = P3-E-GU-1 (G2)**: 10–30M twins × ≥3 widths, oracle capsules (format from step 6's transfer arms), plain/text/symbolic arms + matched learned-expert + generic typed-store controls (A.9), shuffled-certificate control, causal held-out endpoint | G2 `oracle-diagnostic`, R-0 | ~15–75 GPU-h | P6's G2; the interface-effect direction read (ASM-0815) |
| 9 | **P6 G3 learned-addressing degradation (NEW)**: replace gold capsule addresses with the NLB-gated learned addressing path and measure the G2 effect's survival — REQUIRED before any natural-input promotion of P6 (the portfolio's promised G2→G3 transition, previously missing from the run order) | G3 | cheap-moderate | P6's natural-input claim (ASM-0814); blocked by step 8 positive + step 4 clearing the vertical |
| 10 | **G4 first W1 attempt** for whichever of P1/P3/P5(/P2) survives, behind the full G4 block {P3-D-INDEX incl. abstention scoring, THREAT, BASE, FRONTIER, HW, RAGC, P3-E-CAL} and the resource-matched frontier freeze | G4, R-1→R-2 | the rung's main spend | the competitive thesis |

Steps 0–3 are runnable now in parallel (no GPU beyond small; G1/census work is
exempt from P3-E-CAL per rev-2 §4) — with ONE named exception that the earlier
draft stated inconsistently [corrected per the counter-review]: step 2's
promote/kill READING is freeze-dependent (§B.2.3); only its annotation and
sensitivity-band computation are runnable now. Steps 4–6 are the round-1 GPU
wave and fit the ARC/Modal free pool (step 5 needs no training and may lead).
Step 8 waits for step 6; step 9 waits for steps 8 and 4. Nothing at G4 runs
before the measurement framework freezes [STIPULATED: run-order decision,
consistent with ASM-0817].

**Dependency edges shown explicitly (per the counter-review and rev-2's
blocking rule):** P7→P1 (P7 output has no NL query path; any natural-input use
of a P7-built store is blocked by P3-E-NLB-1 or runs oracle-labelled), and
P6 G2→P6 G3 (steps 8→9: the oracle-capsule result licenses nothing
natural-input until the learned-addressing degradation is measured)
[STIPULATED].

**The three cheapest kills with the highest information, named:** (i) step 0's
Δ_max on the frozen R-1 suite — if <δ₁ for every store-dependent family it is
K-P3v2(1) and no mechanism result can save the competitiveness programme;
(ii) step 3's seam test — a deterministic-template renderer at ~0 corruption
plus a localised seam failure re-scopes P1 before its GPU spend; (iii) step
4's joint retention/S2 read — the first of the N=2 registered NLB redesign
cycles that K-P3v2(2)/(5) count. (Step 2's claim-ceiling is high-information
but NOT on this list: it is not decisive until the abstention scoring freezes)
[STIPULATED: the kill shortlist, revised].

## B.4 Bead mapping (existing + NEW for the coordinator to bd-create)

Existing design beads under epic `kernel-of-truth-s55r` and what they now
carry [STIPULATED: mapping only; no bead is created or modified here]:

| Existing bead | Round-1 assignment |
|---|---|
| P3-D-NLB | P1's gate instrument (unchanged scope); step 4 is its P3-E-NLB-1 |
| P3-D-PS | P1's architecture design — absorb M1 verbatim as the concrete design, + the renderer-corruption primary + the deterministic-template renderer baseline (step 3) |
| P3-D-ORACLE | now OWNS the step-3 P1 G2 system-seam test (per-stage oracle ablation of serialization/execution/rendering [LIT: PARSE §8]); its G2→G3 decomposition also attributes P1's contract-layer vs parser vs renderer losses |
| P3-D-RAGC | unchanged; inherits W1's source-parity two-arm design as its worked example |
| P3-D-FRONTIER | unchanged; A.11's endorsement of comparator discipline applies |
| P3-D-POWER | step 0 owner; MUST add the corrected firewall-form bound (A.3) and P7's κ census inputs |

NEW design beads to create (names/priorities proposed; blockers per rev-2 §5
conventions):

1. **P3-D-CONTRACT** [DESIGN, P0, blocked-by: P3-LR-PARSE (done)] — the K2+W3
   merged contract-and-contrast layer: deterministic ROLE_DIR repair spec,
   both-orientation frame enumeration, IR-level deterministic inversion + an
   INDEPENDENT NL-side check (ambiguity-set execution §B.2.5 or
   human-annotation calibration — A.2), mesh generation from repaired tables,
   risk-coverage kill shape. Feeds P3-E-NLB-1 arms (steps 1+4). Co-designs
   with P3-D-NLB/P3-D-PS.
2. **P3-D-FIREWALL** [DESIGN, P1, blocked-by: P3-D-POWER (co)] — K3/P2 as a
   conditional diagnostic census: the claim taxonomy, abstract domains,
   two-extractor agreement rule + its calibration against human semantic gold
   (joint false-rejection risk), the power-sized sensitivity-banded annotation
   protocol for step 2, and the step-7 extractor design.
3. **P3-D-CAP** [DESIGN, P1, blocked-by: none hard; co-input P3-LR-RAG] — the
   versioned typed-evidence-capsule schema (absorbing W1's bitemporal/
   contradiction/provenance fields) + the step-6 consumption/transfer
   falsifier design (held-out identities/compositions, causal perturbations,
   shuffled mappings, full adapter accounting — §B.2.1; prices the a-e2
   consumption leg at scope).
4. **P3-D-SSD** [DESIGN, P1, blocked-by: P3-LR-RULE] — M2 as the concrete
   H-RULE-CD design: formal-state compiler, block-accept/rollback semantics,
   no-mask-on-uncertain-address invariant, local-vs-global mask divergence
   check, the step-5 four-arm falsifier with the A.8 non-inferiority + Pareto
   kill. Feeds P3-E-RULE-1.
5. **P3-D-SYMX** [DESIGN, P2, blocked-by: P3-LR-TINY + P3-LR-NTP + P3-LR-FUSE
   + P3-D-CAP] — M3 as the concrete P3-E-GU-1 design: router/bridge spec,
   proof-trace curriculum, twin protocol, shuffled-certificate control +
   equal-compute matched learned-expert and generic typed-store controls
   (A.9), causal endpoint, AND the step-9 G3 learned-addressing degradation
   design (the G2→G3 edge).
6. **P3-D-DXW** [DESIGN, P1, blocked-by: none hard; co-input P3-LR-STORE] —
   P7 as an ingestion/coverage FEEDER (not an architecture): deterministic
   extractors per source class + the costed κ/precision annotation census
   (incl. type-assignment precision and build-effort accounting — §B.2.2);
   extends the coverage-growth ingestion plan; explicit P7→P1 dependency for
   any natural-input use; costs to KOT-LIFE/1.
7. **P3-D-ENGINE-V1** [DESIGN, P2, blocked-by: none] — K1's substrate deltas
   (four-valued answers, certificate VM, validity intervals) as a specified
   engine version change (ALGORITHM_VERSION bump + X0 golden regeneration +
   Phase-X re-run when built, per the standing encoder-pin convention).

Also for the coordinator's notes: record W2 as DROPPED-at-round-1 (rationale
A.5) and W1 as DEFERRED-behind-G2 (rationale A.4) so neither silently
reappears without new evidence [STIPULATED].

## B.5 Proposed assumption entries (IN-DOC ONLY — nothing written to the registry by this document; the coordinator assigns real ASM ids in the append-only register on adoption)

- **PROP-A (proposed stipulation):** the round-1 portfolio is P1–P7 of §B.1
  under the STRATIFIED reading: architecture bets = {P1; P3-vs-P5 with P5 the
  incumbent; P6 late}; supporting work = {P2 conditional diagnostic census,
  P4 representation+interface experiment, P7 ingestion feeder, K1 substrate};
  W2 dropped, W1 deferred; merge/drop/defer rulings of Part A. A scoping
  decision; confers no evidence on any candidate.
- **PROP-B (proposed stipulation):** selective-architecture G4 comparisons
  are BLOCKED on the P3-D-INDEX abstention-scoring registration (§B.2.3) — a
  new dependency edge strengthening ASM-0811/ASM-0817.
- **PROP-C (proposed extrapolation, never a premise):** deterministic
  extraction from structured sources can raise κ materially above the
  measured near-zero external coverage at acceptable precision (P7's bet);
  resolver = the P3-D-DXW census (§B.2.2).
- **PROP-D (proposed extrapolation, never a premise):** claim-level
  coverage exceeds whole-query coverage by enough to clear δ₁ on the
  normalised index for at least one benchmark family (P2's bet); resolver =
  the step-2 oracle ceiling's sensitivity band, read as promote/kill only
  after the P3-D-INDEX abstention-scoring registration (§B.2.3).

---

## Bottom line

Summary verdict [STIPULATED — the synthesis judgement; every constituent
fact is tagged where argued above]: the GPT-5.6 proposal is strong where the evidence is strong —
its front-end (M1+K2), its formal-slice decode integration (M2), and its
oracle-gated training bet (M3) are all adopted with repairs — and silent where
the programme is most likely to die: none of its nine candidates addresses the
coverage wall, and its own best cheap experiment (capsule consumption) was
left unscheduled; this synthesis adds both — P7 as an ingestion/coverage
FEEDER dependent on P1, and P4 as a transfer-repaired representation+interface
experiment whose bare pass licenses closed-inventory compression only — and
corrects two G1 arithmetic defects (firewall bound on the normalised scale;
K2 kill vacuity) that would otherwise have biased round 1 toward false hope.
Revision 2, per the independent counter-review, removed this document's OWN
false-hope residue: P2's ceiling and P4's consumption test are no longer
called decisive (the one waits on the abstention-scoring freeze and human-gold
calibration; the other on transfer arms), the P1 G2 system-seam test and the
P6 G3 learned-addressing step are now scheduled, and the portfolio is
stratified so that only P1, P3-vs-P5, and P6 are claimed as architecture bets.
The critical path remains exactly what the programme already knew it was: the
NL boundary (P1/step 4, K-P3v2(2)) — everything else is either upstream
paper-cheap (steps 0–3) or honestly labelled oracle-diagnostic until that
gate clears.

This document changes no frozen object, no verdict, no audit, no registry
entry, and no bead; its proposals become real only through maintainer review,
the GPT-5.6 counter-review, and the coordinator's bd-create.
