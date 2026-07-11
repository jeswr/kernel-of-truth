# P3-D-NLB — NLB/1: the real-parser re-entry (FK-NLB-3)

> **Status: Phase-1 [DESIGN] deliverable of Programme-3, revision 2. Revision 2
> applies every named correction of the GPT-5.6 external review
> (`poc/gpt56-review/rev-dNLB-20260711b/last-message.json`): the ambiguity-set
> executor is repaired to evidence-gated semantics, the primary acceptance arm
> is frozen at design time, the rare-event statistics are replaced with exact
> cluster-valid bounds and an enumerated multiplicity family, the data
> separation becomes five-role, τ selection becomes fixed-sequence
> risk-controlled testing, NLB-0 is demoted to a non-decisive per-vertical
> screen, the PASS license is narrowed with consumer obligations, the corpus
> arithmetic is corrected, and the missing implementation/accounting pins are
> registered. Nothing here is frozen, pre-registered, scheduled, or run; no
> verdict, audit, frozen object, or existing registry record is touched.
> Revision 1 registered ASM-0900…ASM-0906; revision 2 REGISTERS its corrective
> stipulations as ASM-0940…ASM-0947 in `registry/assumptions.jsonl`
> (append-only; 0948–0949 remain free; where a rev-2 clause supersedes a rev-1
> clause the rev-2 ASM says so and both stay visible in the register). No
> git/bd/kb-sync is run by this bead.**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
> Bead: `kernel-of-truth-s55r.13` (P3-D-NLB). Parent epic: `kernel-of-truth-s55r`.
> Blocked-by (satisfied): P3-LR-PARSE (`docs/next/lit/PARSE.md`, 2026-07-11).
> Deliverable named by programme rev-2 §5: *"The NL front-end redesign that targets
> 0.90 retention + S2 fail-closed per vertical, with calibrated abstention; the
> gate instrument ASM-0814 points at."* Spawns: **P3-E-NLB-1** (via the NLB-0
> go/no-go pilot, §7).
>
> **Inputs read at source, in full:**
> `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) — §0 constraints,
> §1.1 NL-input integrity, §3.3a H-PS, §4 gate ladder + sequencing exemptions,
> §5 the P3-D-NLB row, §7.1 K-P3v2(2)/(5); `docs/next/feasibility-synthesis.md` —
> the binding walls (§0–§1, §5); `docs/next/arch/round1-critique-synthesis.md` —
> P1 (M1+K2+W3 merged), §B.2.5 ambiguity-set executor, §B.3 run order;
> `docs/next/lit/PARSE.md` — the whole review, esp. §5 per-class judgements and
> §8's gate-instrument requirements (1)–(7); `registry/verdicts/{l3a-parse,a5-nl}.json`
> + `reports/auto/{l3a-parse,a5-nl}/analysis-output.json` (figures below quoted
> from these) + `registry/assessments/{l3a-parse,a5-nl,l3a-parse-recoverability}.json`;
> `docs/design-nl-boundary-l3a-parse-a5-nl.md` (the parent instrument design:
> FK-NLB forks, blind phrasing protocol, boundary arithmetic);
> `docs/next/design/ORACLE.md` (KOT-DECOMP/1 — the stage-attribution consumer);
> revision 2 additionally: `poc/gpt56-review/rev-dNLB-20260711b/last-message.json`
> (the external review this revision answers, read in full).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a registry
> verdict/assessment restated strictly inside its envelope; `[LIT-BACKED: ref]` =
> an external fact verified at source by a completed Phase-0 lit review, cited
> through that review; `[STIPULATED: ASM-id]` = a design choice registered here;
> `[EXTRAPOLATION: ASM-id]` = a registered forward projection, never a premise.

---

## 0. One-paragraph summary

Both measured crossings of natural language into the deterministic engine FAILED —
l3a-parse retained 47.6% of gold-parse covered exactness (safe: mis-parses died as
refusals), a5-nl retained 41.6% AND fired the S2 dangerous-wrong kill (5.0%
wrong-with-provenance via the deterministic ROLE_DIR direction-table defect)
[MEASURED: registry/verdicts/l3a-parse.json + registry/verdicts/a5-nl.json]. Those
FAILs were produced by a verbatim-lexicon, no-learning front-end whose paraphrase
stratum scored 0/261; the PARSE lit-review judges the dominant failure classes
capability-limited (leading hypothesis, empirically unresolved at our gate) and
names the strongest matched-accounting recipe: fine-tuned small parser +
grammar-constrained decoding + lexicon/trie resources + calibrated abstention with
a frozen risk-coverage operating point [LIT-BACKED: docs/next/lit/PARSE.md §0, §5,
§8]. This document designs that re-entry as **NLB/1**: a two-tier front-end
(NLB-FE/1, §3 — repaired deterministic µs fast path + learned ≤360M fallback under
exact grammar masks + contracts + EVIDENCE-GATED ambiguity-set acceptance + one
frozen abstention threshold, with the full stack frozen at design time as the
single primary gate arm), the exact per-vertical success gate (**G-NLB**, §4 —
retention LB95 ≥ 0.90 jointly with unconditional dangerous-wrong UB95 < 0.02 under
exact cluster-valid rare-event bounds, plus directional-stratum near-zero rules
and creditable abstention), the gate corpus (**NLB-EVAL/1**, §5 — K=3 blind
phrasings per query from disjoint author sources, five-role data separation,
both-orientation and perturbation strata, a rubric-governed ambiguity annotation),
the threshold-freeze and risk-control protocol (§6 — fixed-sequence monotone
testing on a dedicated selection split), and the cheapest informative screen
(**NLB-0**, §7 — a ~$25 + ≤5-GPU-h two-leg per-vertical pilot on the
already-paid-for legacy corpora that screens go/no-go BEFORE the instrument build
and before any registered redesign cycle is burned; explicitly non-decisive).
Everything natural-input and store-touching in Programme-3 waits behind
this gate or runs oracle-labelled [STIPULATED: ASM-0814, applied; ASM-0900];
a PASS is a prerequisite for consumers, never a transferable certificate
[STIPULATED: ASM-0945].

---

## 1. What NLB is, what it gates, and what it can never license

- DECISION: NLB/1 is the shared **gate instrument**, not an architecture family:
  P3-E-NLB-1 clearing G-NLB on a vertical unblocks every natural-input
  store-addressed leg on THAT vertical (H-VL NL legs, H-GNN NL-extracted
  subgraphs, H-RULE KV/CD firing from NL, H-DD store reinjection on NL tasks,
  H-PS's front-end); the only alternative anywhere remains `oracle-diagnostic`
  labelling with no W1 or real-input claim [STIPULATED: ASM-0814 restated;
  ASM-0900].
- DECISION: the front-end is INSIDE any measured system that later makes an index
  claim — its bytes under KOT-SIZE/2, its latency/energy under KOT-COST/2, its
  training and authoring costs under KOT-LIFE/1; no arm ever receives
  hand-formalised inputs [STIPULATED: ASM-0808 restated; ASM-0900].
- DECISION: P3-E-NLB-1 itself makes NO index claim and is exempt from P3-E-CAL
  and the G4 block (the programme's sequencing exemption); it runs as early as
  its corpus exists [STIPULATED: ASM-0817 restated; ASM-0900].
- LOAD-BEARING: a G-NLB PASS licenses exactly "the closed grammar is reachable
  from blind natural phrasings at ≥0.90 retention with the S2 bound holding, on
  this vertical, for this front-end pin and this phrasing protocol" — never
  usefulness, never index movement, never coverage growth; those live behind G1
  (Δ_max) and G4, which are other beads' gates [STIPULATED: ASM-0900].
- LOAD-BEARING: the PASS is a **prerequisite, not a transferable certificate**.
  What it tested is backward-authored blind paraphrases of a closed parent
  grammar over a registered lexicon — not naturally occurring traffic — and
  that limitation is disclosed verbatim on any PASS. Every consumer unblocked
  under ASM-0814 owes three things: (a) it ships the EXACT passed front-end
  content-hash unmodified (any change to weights/masks/tries/tables/calibrator/τ
  voids the pass for it); (b) its NL input surface must be the tested closed
  grammar — a consumer with a different output space or input distribution
  (H-GNN subgraph extraction, H-RULE addressing, H-DD reinjection,
  benchmark-facing H-PS) does not inherit the pass and needs its own clearance
  or a registered compatibility argument; (c) its G3 evidence must include a
  task-originated NL leg on its own input distribution — the NLB PASS unblocks
  RUNNING that leg, never substitutes for it [STIPULATED: ASM-0945].

Failure is a first-class outcome: K-P3v2(2) kills the competitiveness programme
if P3-E-NLB-1 and its redesigns fail the joint gate on BOTH verticals after N=2
pre-registered redesign cycles beyond the first attempt, and K-P3v2(5) counts the
same cycles for G2→G3 non-survival [STIPULATED: ASM-0818 restated]. §7.4 makes
"cycle" mechanical so the kill cannot be gamed in either direction
[STIPULATED: ASM-0904].

---

## 2. The measured failure this design must beat (restated exactly)

All figures below from the verdicts' own analysis outputs
[MEASURED: reports/auto/l3a-parse/analysis-output.json +
reports/auto/a5-nl/analysis-output.json, restated within their envelopes]:

| quantity | l3a-parse (family/world) | a5-nl (code) |
|---|---|---|
| retained covered exactness | 251/527 = 0.4763 (UB .5121) — FAIL vs 0.90 | 356/855 = 0.4164 (UB .4443) — FAIL |
| S2 unconditional wrong-with-provenance | 8/527 = 0.0152 (LB .0086) — kill did NOT fire | 43/855 = 0.0503 (**LB .0394 ≥ 0.02 — KILL FIRED**) |
| label-verbatim stratum | 259/339 = 0.764 | 287/441 = 0.651 |
| paraphrase stratum | **0/261 = 0.000** | 69/414 = 0.167 |
| stage breakdown | frame-miss 228, mapper-abstain 48, gazetteer-miss 40, frame-ambiguous 41 | frame-miss 468, gazetteer-miss 24 |
| dangerous class mechanism | — | deterministic ROLE_DIR table flips "what contains X" vs "what X contains" into a valid-but-wrong operation (contained-in 24, where-defined 18) |
| control fail-closed (S1) | 0.896 (Holm S1 FAIL) | 104/106 = 0.981 (S1 PASS) |
| front-end cost | 266.8 µs/query | 249.8 µs/query |
| synonym probe (no-label phrasings) | 0/60 parse | 0/60 parse |

Three design-driving readings:

- PREMISE: the retention loss is dominated by the paraphrase/lexical gap
  (frame-miss + the 0/261 paraphrase stratum) and entity linking — the two
  classes the field repairs most reliably with learned components; nothing
  zero-learning clears 0.85+ under held-out phrasing anywhere in the reviewed
  record [MEASURED: the stage breakdowns above; LIT-BACKED:
  docs/next/lit/PARSE.md §2 load-bearing close + §5a/b].
- PREMISE: the dangerous class was NOT a learned-model hallucination — it was a
  hand-coded deterministic direction-table defect, with a targeted deterministic
  repair (fail closed on ambiguous orientation) already named by the a5
  assessment as the priority route [MEASURED: registry/assessments/a5-nl.json,
  questions_opened `a5-nl-frame-direction-repair`].
- PREMISE: checked execution cannot catch that class — a direction-flipped query
  is valid-and-wrong and executes perfectly — and self-consistency-style
  confidence scores can fail on exactly the consistent confident inversion, so
  the S2 budget must be carried by layered independent checks, with the
  threshold as the residual control only [LIT-BACKED: docs/next/lit/PARSE.md §3
  limit (mbr-exec-2022) + §4 conformal caveat (conformal-abstention-2024) + §5c
  design law].

Instrument lessons inherited (not re-litigated): the shape-ambiguous families
(unique-maker, made-lookup) stay carved out of scoring per FK-NLB-10/ASM-0420;
the recoverability audit exists because a phrasing corpus that humans cannot
parse manufactures kills — strict recovery measured 43/60 = 0.717 on the l3a DEV
audit before the carve-out [MEASURED:
registry/assessments/l3a-parse-recoverability.json].

---

## 3. NLB-FE/1 — the two-tier front-end (the thing under test)

- DECISION: the front-end is a **parser+abstention SYSTEM** with the
  deterministic engine as sole answer authority and the parser as an untrusted
  proposer; the fail-closed invariants of ASM-0900(3) are frozen design law: no
  surface answer except from an engine execution of an ACCEPTED parse; failure
  at any stage → ABSTAIN or CLARIFY, never a guess [STIPULATED: ASM-0900].

```
NL phrasing
   │
   ├─► TIER-0 (deterministic, ~µs): repaired a1-hybrid
   │      trie/template exact match + gazetteer + REPAIRED frame layer
   │      • accept only exact template+lexicon hits → kot-query IR
   │      • ambiguous orientation / any miss → fall through (never guess)
   │
   ├─► TIER-1 (learned, ~ms, ≤360M): fine-tuned parser
   │      primary: joint intent(family)+slot(entity,role/direction) head
   │      secondary arm: seq2seq → DSL under EXACT grammar mask
   │      • trie-constrained entity emission (registered lexicon only)
   │      • emits IR candidates + confidence score
   │
   ├─► ACCEPTANCE (contract-and-contrast layer, deterministic + µs engine):
   │      grammar/type validity → IR-level deterministic operator inversion
   │      check → EVIDENCE-GATED ambiguity-set execution (build the set of
   │      parses the surface cannot distinguish; singleton → answer it;
   │      else run all members on the µs engine and answer only on
   │      denotation agreement, otherwise CLARIFY)
   │      → frozen threshold τ on the calibrated score
   │
   ├─► ACCEPTED → engine executes → answer WITH provenance
   └─► else → ABSTAIN (or CLARIFY, returning the competing readings)
```

### 3.1 Tier-0 — the repaired deterministic fast path

- DECISION: Tier-0 is the measured a1-hybrid mapper (mapper/src lexicon +
  lemmatizer + gazetteer + closed frame layer) with two changes and NO
  broadening of its acceptance: (i) the **deterministic ROLE_DIR repair** — the
  frame layer's direction table is rebuilt with an explicit per-frame
  orientation inventory, exhaustive both-orientation unit tests over every
  directional frame × surface pattern, and a fail-closed rule: any phrasing
  whose orientation cues are absent or conflicting yields NO Tier-0 parse
  (fall through), never a defaulted direction; (ii) template/trie matching
  stays exact-match-only, so Tier-0's acceptance set is enumerable and
  auditable offline. Tier-0 exists for cost (µs vs ms on the verbatim/templated
  stratum that measured 65–76% parseable) and for safety (its accepted parses
  are table-verified, not model-scored) [STIPULATED: ASM-0900; ASM-0905(4);
  the repair is the a5 assessment's named route — MEASURED:
  registry/assessments/a5-nl.json].

### 3.2 Tier-1 — the learned fallback

- DECISION: primary parser class = **joint intent+slot** at 110–360M (frame
  classification + gazetteer-constrained slot filling + an explicit
  directional-role classification head), because kot-query/1 (7 in-scope
  families) and kot-query-code/1 are closed grammars of few shape-recoverable
  families over registered lexicons — structurally an intent+slot task, not
  open text-to-SQL; the secondary arm on the same harness = seq2seq generation
  of the DSL under grammar-constrained decoding [STIPULATED: ASM-0905;
  difficulty prior per LIT-BACKED: docs/next/lit/PARSE.md §2].
- DECISION: any constrained decoder in a scored arm must first pass an **exact
  local-vs-global mask equivalence check on the full closed grammar** (the
  grammar is tiny; the check is cheap and exhaustive at the automaton level),
  with any divergence quantified and pinned before freeze — local masking
  fidelity is checked, never assumed [STIPULATED: ASM-0905(3); caveat per
  LIT-BACKED: docs/next/lit/PARSE.md §4 P-GCD/GAD].
- DECISION: entity/slot emission is trie-constrained to the registered
  gazetteer (GENRE shape): the parser can only name entities that exist; unseen
  surface forms route to a deterministic post-mapping or abstain
  [STIPULATED: ASM-0905; recipe per LIT-BACKED: docs/next/lit/PARSE.md §5b].
- Model shortlist (pinned at prereg, tuning-compute logged per ASM-0812): a
  ~110M encoder (BERT-class intent+slot) vs SmolLM2-135M / 360M
  (decoder seq2seq+mask). Rationale for the range: the review's proven recipe
  band is 110M–3B; the programme's cheap rung is R-1; the 100M–2B build
  directive is satisfied at its bottom end where the falsifier is cheapest
  [STIPULATED: ASM-0905].

Implementation-defining pins (rev-2; the review's buildability gaps closed)
[STIPULATED: ASM-0947]:

- DECISION: **IR** = the parents' kot-query/1 / kot-query-code/1 DSLs,
  unchanged — NLB introduces no new IR [STIPULATED: ASM-0947(1)].
- DECISION: **mask interface + formal equivalence.** The decoder mask is
  computed on the PRODUCT AUTOMATON (DSL grammar automaton × tokenizer
  transducer × entity trie × per-family type constraints). "Exact
  local-vs-global mask equivalence" MEANS: at every reachable product state,
  the locally admitted token set equals the set of tokens extendable to at
  least one complete valid parse. The check runs exhaustively over the product
  automaton (feasible: the grammar is tiny); grammar-automaton equivalence
  alone is insufficient and is not accepted [STIPULATED: ASM-0947(2)].
- DECISION: **candidate-set construction** — intent+slot arm: top-M frame
  hypotheses × type-checked slot bindings (M pinned at prereg); seq2seq arm:
  masked beam of pinned width; both emit complete IR candidates with scores
  [STIPULATED: ASM-0947(3)].
- DECISION: **confidence aggregation** — one pinned scalar per candidate from
  a pinned function class (calibrated product of intent and slot posteriors,
  or length-normalized sequence log-prob); class chosen on DEV, pinned at
  freeze [STIPULATED: ASM-0947(4)].
- DECISION: **entity linking, fully specified** (the named dominant measured
  failure class): mention detection = longest-match trie scan over the
  lemmatized surface; the alias table is built deterministically at
  artifact-build time from the registered gazetteer by enumerated generators
  (case / lemma / separator variants) and hash-pinned in the manifest; a
  surface form mapping to >1 URN is a COLLISION and enters the ambiguity set
  (CLARIFY path), never a silent pick; the "deterministic post-mapping" for
  unseen surface forms MEANS lemmatization + alias-table lookup ONLY — no
  fuzzy/edit-distance matching in any scored arm; no match → the candidate
  dies (abstain if none survives) [STIPULATED: ASM-0947(5)].
- DECISION: **training recipe** — synthetic TRAIN generated by a hash-pinned
  grammar-recombination script over fresh identities with a registered seed;
  target sizes pinned at prereg (order 10⁴–10⁵ phrasing-IR pairs per
  vertical); recipe, seed, and realized size enter the frozen record
  [STIPULATED: ASM-0947(6)].

### 3.3 The acceptance layer (contract-and-contrast)

Adopted from the round-1 synthesis P1 merge (M1+K2+W3); rev-2 repairs the
executor semantics and freezes the primary arm [STIPULATED: ASM-0940]:

1. **Grammar/type validity** — free, by construction of the mask/IR.
2. **IR-level deterministic inversion** — invert the typed operator
   deterministically at the IR level and check binding consistency; this
   catches implementation inconsistency, and explicitly does NOT catch a parser
   that consistently maps to the wrong relation (scope stated per the round-1
   A.2 repair).
3. **Evidence-gated ambiguity-set execution** (rev-2 repair — the rev-1
   "always include the inverse" rule is REJECTED as logically wrong: on
   genuinely directional queries the correct and inverse denotations normally
   differ, so it abstains exactly where direction matters, and accidental
   agreement never identifies the correct direction; it could alone make 0.90
   retention unreachable [the external review's ranked concern 1]). The
   AMBIGUITY SET is the set of complete valid parses the front-end cannot
   distinguish on surface evidence, built deterministically: the pinned
   per-frame orientation-cue inventory decides each directional frame — cues
   present and consistent select ONE orientation (the inverse is NOT added);
   cues absent or conflicting add BOTH orientations; Tier-1 adds any candidate
   within a pinned score band of the top candidate and any competing entity
   binding from a true trie collision. Execution rule: |set| = 1 → answer that
   parse (subject to contracts + τ); |set| > 1 → execute ALL members on the µs
   engine (2–8 executions ≈ free at 5.29–7.82 µs/query engine cost
   [MEASURED: registry/verdicts/l3a.json + a5.json engine timing]) and answer
   only if every denotation agrees (direction immaterial on that item);
   otherwise CLARIFY with the competing readings attached
   [STIPULATED: ASM-0940(1)/(2)].
4. **Frozen threshold τ** on the calibrated confidence score (§6) — the
   residual control.

- DECISION: **the primary gate arm is frozen NOW, at design time** — the gate
  system is the full stack (repaired Tier-0 + Tier-1 + grammar/type validity +
  IR-inversion contract + evidence-gated ambiguity-set + frozen τ). The
  ablation arms (confidence-only; confidence+contracts; Tier-0-only as the
  measured deterministic baseline) are DIAGNOSTIC CO-REPORTS computed on the
  same run — which acceptance layer dominates the S2 dimension of the
  risk-coverage curve remains a deliverable — but they are never candidates
  for selection on EVAL; no arm choice ever touches EVAL (the rev-1 ambiguity
  between "mandatory layer" and "experimental arm" is resolved: mandatory in
  the gate system, compared only diagnostically) [STIPULATED: ASM-0940(3)].

### 3.4 Cost and size envelope (rev-2: executable, measured in-gate)

- DECISION: **executable resource ceiling**, pinned at prereg-freeze and
  MEASURED during G-NLB as an instrument-validity leg (exceeding it fails the
  attempt, not a footnote): packed front-end artifact ≤ 1.0 GB; Tier-1 warm
  batch-1 CPU latency p95 ≤ 500 ms and p99 ≤ 2000 ms per query on the pinned
  reference CPU; cold start ≤ 60 s. "ms-class" projections are not budgets
  [STIPULATED: ASM-0946(1)].
- DECISION: **canonical packed-artifact manifest** — one content-hash over
  parser weights, tokenizer, runtime + version, grammar masks, entity tries +
  alias tables, Tier-0 template/lexicon/frame tables, calibrator, τ, and
  config; this hash IS the front-end pin of §5(4)
  [STIPULATED: ASM-0946(2)].
- DECISION: **measured during G-NLB, reported in the verdict, not deferred to
  consumers**: warm and cold batch-1 latency (CPU, and GPU if used), Tier-1
  fall-through rate, peak RSS (and VRAM if used), energy estimate, and tail
  latencies [STIPULATED: ASM-0946(3)].
- Tier-0 measured 250–267 µs/query PRE-repair [MEASURED:
  frontend_mean_us_per_query in both analysis outputs] — a prior only; the
  repaired implementation's timing is RE-MEASURED and never inherits the
  parents' figures [STIPULATED: ASM-0946(3)]. The two-tier shape exists so the
  µs path absorbs the templated mass; the blended cost is workload-dependent
  and additionally reported per KOT-COST/2 in any consuming system
  [STIPULATED: ASM-0900].
- Parser weights (~0.2–0.7 GB fp16 at 110–360M, less quantised), grammar masks,
  tries, and calibrator are all bytes on KOT-SIZE/2 figure (1) of whatever
  system ships them; nothing here is "free" [STIPULATED: ASM-0900; ASM-0810
  applies].
- DECISION: KOT-LIFE/1 logs the TOTAL search/tuning cost across every tried
  parser, score class, and acceptance arm — not just the survivor
  [STIPULATED: ASM-0946(4); ASM-0812 applies].
- DECISION: an **API-hosted parser is a remote dependency** and is ineligible
  as NLB-FE/1 or any gate arm (its bytes and latency cannot be pinned under
  KOT-SIZE/2 + KOT-COST/2); the `a5-nl-llm-successor` branch requires its own
  registered accounting stipulation before any gate use
  [STIPULATED: ASM-0946(5)].

---

## 4. G-NLB — the exact success gate (verbatim, per vertical)

DECISION: **G-NLB (verbatim)** [STIPULATED: ASM-0901] with the statistics
clause superseded [STIPULATED: ASM-0941]; the system under this gate is the
frozen primary arm of §3.3 — the full acceptance stack — and no other arm
[STIPULATED: ASM-0940]. P3-E-NLB-1 PASSES on a vertical iff ALL of:

1. **Retention:** retained covered exactness — engine-exact answers on covered
   scored items under blind NL phrasing, over the gold-parse ceiling of the
   same items (gold replication is exact by construction on both verticals) —
   has one-sided 95% lower confidence bound ≥ 0.90. FAIL fires when the upper
   bound < 0.90; between the two = INCONCLUSIVE (the parent instruments'
   three-way shape, retained).
2. **S2 safety bound, defined precisely:** S2 = **unconditional**
   P(answered ∧ wrong) over covered scored items. Gate leg: UB95 < 0.02.
   Kill leg: LB95 ≥ 0.02 (fires the dangerous-wrong kill exactly as a5-nl's
   did). The **selective risk** P(wrong | answered) is a mandatory co-report —
   the two notions diverge exactly when coverage drops — but the binding bound
   is unconditional because clause 1 already punishes over-abstention (an
   abstain-all policy scores retention 0).
3. **Directional-stratum safety:** every directional frame × orientation
   stratum with pre-registered minimum support carries a near-zero
   wrong-with-provenance allowance; the exact integer stratum boundary is
   pinned at freeze from the exact-bound arithmetic — a zero-wrong allowance
   certifies UB95 < r only when the stratum holds ≥ ln(0.05)/ln(1−r) clusters
   (e.g. 59 for r = 0.05), so minimum support per stratum is derived, not
   guessed [STIPULATED: ASM-0941(3)]. An aggregate pass with a failing
   directional stratum is a FAIL — systematic inversion cannot hide in an
   average.
4. **Creditable abstention:** items independently annotated
   ambiguous/unanswerable BEFORE scoring are scored correct on ABSTAIN/CLARIFY
   and wrong on any answer; they sit outside the retention denominator and
   inside the safety accounting.
5. **Controls:** the S1 control fail-closed leg (out-of-scope/control phrasings
   must die as acceptable refusals) rides in the same Holm family as S2, per
   the parent instruments.
6. **Statistics (rev-2 — exact, cluster-valid, non-adaptive)** [STIPULATED:
   ASM-0941]: rare-event legs never use a bootstrap. The S2 gate/kill legs,
   the S1 control leg, and every directional-stratum allowance use the
   one-sided exact Clopper–Pearson bound on the CLUSTER-COLLAPSED indicator
   (a base-query cluster fails iff ANY of its K=3 phrasings is
   answered-and-wrong): the phrasing-level rate never exceeds the cluster
   any-wrong rate, so the collapsed CP UB95 is a valid conservative UB95 on
   the phrasing-level unconditional risk, and it is never degenerate at zero
   observed events (0 wrong in m clusters → UB95 = 1 − 0.05^(1/m), the
   rule-of-three shape). The pre-registered cluster bootstrap (pinned B, seed,
   method) is retained ONLY for the retention interval — a non-rare
   proportion — with the exact CP bound on the cluster-collapsed all-correct
   indicator co-reported; where the two disagree on gate crossing, the
   conservative one binds. NO adaptive selection touches EVAL: τ is frozen on
   CAL-B before EVAL exists (§6), the primary arm is frozen at design time
   (§3.3), endpoints and strata are enumerated at freeze; the per-vertical
   Holm family is EXACTLY {retention leg, S2 gate leg, S1 control leg,
   directional-stratum intersection leg}; the two verticals are separate
   registered claims, never pooled. Every integer PASS/FAIL/kill boundary is
   derived by analytic inversion of the exact bounds (never by resampling)
   and pinned in the frozen record before any scored run, per the l3a-parse
   boundary-pinning precedent. The Wilson z=1.645/1.96 forms remain for K=1
   diagnostics only.

Per-vertical independence: family/world and code gate separately; a PASS on one
vertical unblocks ASM-0814 legs on that vertical only [STIPULATED: ASM-0901].

What a PASS licenses — and does not — is fixed by §1's LOAD-BEARING scope line
[STIPULATED: ASM-0900]. What a FAIL means: one registered redesign cycle is
consumed (§7.4); two consumed cycles beyond the first attempt with both
verticals still failing fires K-P3v2(2) [STIPULATED: ASM-0818 restated].

Relation to KOT-DECOMP/1: the scored run exports the per-stage counters the
oracle-decomposition protocol consumes (frame/intent selection, role/direction
binding, entity linking, DSL serialization, execution — rendering is out of
NLB's scope and stays with P3-D-PS/P3-D-ORACLE), so a FAIL localises to a named
stage without a second campaign [STIPULATED: ASM-0821 interface, adopted].

---

## 5. NLB-EVAL/1 — the gate corpus (per vertical)

DECISION: the corpus protocol, all clauses binding [STIPULATED: ASM-0902],
with separation, arithmetic, and annotation superseded [STIPULATED: ASM-0942]:

1. **Base items:** the frozen covered scored query sets of the parents — l3a
   527 over the 7 in-scope families (children-lookup, count-maker,
   instance-false-disjoint, instance-true, part-lookup, unique-father,
   unique-mother; shape-ambiguous families stay carved out per FK-NLB-10) and
   a5 855 (call-graph + containment/definition families) — plus matched control
   sets (270 / 106 shapes as parented).
2. **Phrasings: K=3 per query, blind, fresh-identity protocol** — upgrading the
   parents' K=1, which was below field practice [LIT-BACKED:
   docs/next/lit/PARSE.md §6.5]. Authoring context per packet contains only
   what the parents' blind protocol allowed; all parent corpus lints apply
   (one-phrasing-per-qid → now three, no `urn:`, no answer leakage, UTF-8,
   dedup, no mock-template bytes).
3. **Five-role separation with DISJOINT SOURCES** (rev-2 — the rev-1 four-way
   scheme gave DEV double duty, model selection AND calibrator training,
   violating the cited four-role requirement; each role now has one job)
   [STIPULATED: ASM-0942(1)]:
   - **TRAIN** — synthetic only: grammar-recombination paraphrase augmentation
     (CSL-style) + canonical-utterance templates over FRESH identities; never
     an eval query, never a blind corpus, never an eval author source
     [LIT-BACKED: docs/next/lit/PARSE.md §4 use-(i) + §6.1].
   - **DEV** — designer-authored fresh-identity phrasings: model selection
     ONLY; never scored, never used to fit the score.
   - **CAL-A** — author-source S1, a pre-registered ~20% split of covered
     queries, K=3: calibrator/score training only.
   - **CAL-B** — author-source S1, a DISJOINT ~20% split, K=3: threshold
     selection only (§6); never touched by score training.
   - **EVAL** — DISJOINT author-source S2 (different model family or human
     authors) over the remaining ~60%, K=3, authored AFTER the front-end pin:
     the single scored set.
4. **Freeze ordering, hash-witnessed:** train + pin parser weights and grammar
   mask → author CAL-A/CAL-B → train calibrator (CAL-A) → select and freeze τ
   (CAL-B) → pin the full front-end content-hash (the §3.4 manifest: weights +
   tokenizer + runtime + masks + tries + alias tables + Tier-0 tables +
   calibrator + τ) → author EVAL blind → single scored run. This generalises
   the parents' pin-before-authoring discipline to a learned front-end
   [STIPULATED: ASM-0942(1); ASM-0946(2)].
5. **Adversarial strata inside EVAL:**
   - **both orientations of every directional frame**, minimum support per
     orientation per source pinned at freeze (the §4(3) strata);
   - a **perturbation suite** (synonym substitution / structural rewrite /
     typo-noise), per-perturbation worst-case reported, Dr.Spider-shaped
     [LIT-BACKED: docs/next/lit/PARSE.md §6.5];
   - an **independent ambiguity/answerability annotation pass** before scoring
     (feeds §4(4)), rubric-governed (rev-2): a pinned written rubric authored
     before any annotation; ≥3 independent annotators (or 2 + a standing
     adjudicator) blind to system outputs; chance-corrected agreement
     (Krippendorff α) reported with a pinned floor of 0.6, below which the
     rubric is repaired and annotation redone; majority + adjudication fixes
     the label; annotated-ambiguous items are CAPPED at 10% of EVAL items per
     vertical (beyond the cap the corpus is repaired), and retention is
     co-reported with the annotated items retained in the denominator, so
     hard-item exclusion cannot silently inflate retention
     [STIPULATED: ASM-0942(3)]; the descriptive no-label synonym probe
     retained, never gated.
6. **Instrument validity:** the recoverability audit gates every authored set —
   ≥95% strict recovery of the intended parse from the phrasing alone by an
   independent auditor, else the CORPUS is repaired (the parents' lesson: 43/60
   pre-carve-out) [MEASURED: registry/assessments/l3a-parse-recoverability.json;
   STIPULATED: ASM-0902(6)].
7. **Legacy corpora are diagnostic-only forever** — their outcomes are public
   in the parent verdicts; no successor gate scores on them, no parser trains
   on them [STIPULATED: ASM-0902(7)].

Sizes and power (corrected arithmetic, binding; exact boundaries pinned at
freeze) [STIPULATED: ASM-0942(2)]: covered scored phrasings at K=3 are
527×3 = 1,581 (l3a) + 855×3 = 2,565 (a5) = **4,146**; matched controls add
270×3 + 106×3 = **1,128**; total **5,274** phrasings BEFORE directional-support
and perturbation strata top-ups (the rev-1 "≈4,700" figure and the
"~1,800-phrasing instrument" note in ASM-0904 are superseded). EVAL-side scored
phrasings: ≈316 queries × 3 ≈ 948 (l3a) and ≈513 × 3 ≈ 1,539 (a5). Under the
§4(6) cluster-collapsed exact bounds the operative n is the CLUSTER count
(≈316 / ≈513): e.g. at m = 316 clusters, a zero-wrong S2 read gives
UB95 ≈ 0.0094 and the exact integer error budgets follow by analytic inversion
of the CP bound — computed and pinned by the pinned analysis script at freeze,
never quoted from here; no G-NLB prereg may cite boundaries before that
computation exists [STIPULATED: ASM-0941(3); consistent with the ASM-0864
sizing discipline].

Cost of the corpus: ~5,300 blind phrasings + strata top-ups + audits across
both verticals — an authoring/API spend of the parents' class (~$30–80), no GPU
[STIPULATED: ASM-0902; ASM-0942(2); parent cost precedent in
docs/design-nl-boundary-l3a-parse-a5-nl.md §5].

---

## 6. The frozen risk-coverage abstention threshold

DECISION: the threshold protocol [STIPULATED: ASM-0903], selection mechanics
superseded [STIPULATED: ASM-0943]:

1. **Selection (rev-2 — fixed-sequence monotone risk-controlled testing; the
   rev-1 "largest acceptable threshold by pointwise bounds" reading is
   rejected as post-selection):** τ is chosen ONCE, on CAL-B only. The
   threshold grid is pinned in advance; candidates are traversed from most
   conservative (lowest coverage) to least; each candidate's unconditional
   dangerous-wrong risk is tested with the exact cluster-collapsed
   Clopper–Pearson UB at δ = 0.05 against the 0.02 budget; traversal stops at
   the FIRST failure and the last passing τ is frozen into the front-end
   content-hash before any EVAL phrasing exists. Validity: fixed-sequence
   testing spends no multiplicity — each test is reached only if every more
   conservative candidate passed — so the frozen τ carries a valid 95%
   risk certificate on the CAL distribution without uniform bounds or
   confidence sequences (the RCPS/learn-then-test shape)
   [STIPULATED: ASM-0943]. The literature-standard instrument shape stays:
   report the whole risk-coverage curve + AUACC, then freeze one operating
   point [LIT-BACKED: docs/next/lit/PARSE.md §4 selective-prediction frame].
2. **Score classes (pinned at freeze, one chosen):** raw parser
   sequence/label probability; a trained calibrator — fitted on CAL-A only,
   never on CAL-B (calibrators beat raw softmax under shift in the reviewed
   record); a conformal nonconformity score with high-probability risk
   control [LIT-BACKED: docs/next/lit/PARSE.md §4; STIPULATED: ASM-0943].
3. **Shift stress is a pre-registered secondary:** the CAL-source-vs-EVAL-source
   risk delta at frozen τ is the measured validity of the guarantee under
   phrasing-source shift — exchangeability does not hold across sources by
   construction, so the CAL guarantee is never quoted as an EVAL-distribution
   guarantee; EVAL measures its degradation [STIPULATED: ASM-0903(3);
   caveat per LIT-BACKED: docs/next/lit/PARSE.md §4 exchangeability +
   kamath-2020 shift line].
4. **Inversion separation is a pre-registered secondary:** AUROC + score
   distributions of the chosen score on direction-flipped-wrong vs correct
   parses over the both-orientation strata — measuring, not assuming, whether
   the score separates the one class where confidence is known to fail
   (consistent confident inversion). The S2 budget for that class is carried by
   the Tier-0 repair and the acceptance layer; the threshold is the residual
   control only [STIPULATED: ASM-0903(4); LIT-BACKED:
   docs/next/lit/PARSE.md §4 conformal caveat + §5c].

---

## 7. NLB-0 — the per-vertical go/no-go screen (explicitly non-decisive)

The full instrument (~5,300 blind phrasings, a fine-tune, a frozen threshold, a
registered attempt) is cheap by programme standards but NOT free, and a frozen
P3-E-NLB-1 FAIL consumes one of the N=2 registered redesign cycles. NLB-0 is the
design-phase pilot that spends ~$25 + ≤5 free-pool GPU-h to screen the two
independent failure budgets FIRST, on corpora that are already paid for
[STIPULATED: ASM-0904; ASM-0944]. Rev-2 states its epistemic status plainly:
NLB-0 is a SCREEN, not a decisive experiment — the legacy corpora are public
and influenced this design, K=1, and the acceptance layer is absent in the
pilot; a pilot number is neither a floor nor a ceiling for the full system,
and no conservatism claim is made [STIPULATED: ASM-0944(1)].

### 7.1 NLB-0-A — the safety leg (~$0, CPU, ~2 agent-days)

Implement the deterministic ROLE_DIR frame-layer repair (fail closed on
ambiguous orientation) + exhaustive both-orientation table tests + the
per-vertical directional-frame inventory; re-run the committed legacy a5-nl
phrasing corpus through the repaired Tier-0 as a **labelled diagnostic** (the
corpus outcomes are public in the verdict; this is disclosed post-outcome
analysis, never a gate) [STIPULATED: ASM-0904(2); the repair route is
MEASURED: registry/assessments/a5-nl.json questions_opened].

- **Proceed condition:** point dangerous-wrong ≤ 4/855 with retention not below
  the measured 0.416 − 0.02.
- **No-go meaning:** if the dangerous class survives a deterministic repair at
  its own source, the design's S2 budget claim fails before any learning enters
  — redesign at the design level; nothing registered is burned.
- **Scope limit (disclosed on every artifact):** NLB-0-A exercises the
  repaired Tier-0 ONLY and establishes NOTHING about Tier-1 safety — a learned
  fallback that dominates novel paraphrases can introduce new inversions,
  which are controlled only by the acceptance layer and the G-NLB directional
  strata at the gate itself [STIPULATED: ASM-0944(3)].

### 7.2 NLB-0-B — the retention-headroom leg (≤5 GPU-h free pool + ≤ ~$25 API)

Train the Tier-1 pilot parser on TRAIN/DEV material ONLY (synthetic
grammar-recombination paraphrases + canonical templates + designer DEV over
fresh identities; the blind corpora are never trained on); freeze a pilot
operating point in advance; evaluate ONCE on the legacy K=1 blind corpora
(527 + 855) as a labelled diagnostic [STIPULATED: ASM-0904(3)].

- **GO condition (PER VERTICAL — rev-2; the rev-1 both-vertical rule is
  rejected as contradicting per-vertical gating and the at-least-one-vertical
  projection):** each vertical screens independently; GO on a vertical =
  pilot retention point ≥ 0.80 at a pre-frozen operating point with
  dangerous-wrong point ≤ 0.01 on that vertical's legacy corpus (plus, on the
  a5 vertical, the §7.1 A-leg proceed condition). A vertical failing the
  screen routes THAT vertical to design revision or the escalated branches;
  the other vertical proceeds to its instrument build
  [STIPULATED: ASM-0944(2)].
- **Reading discipline:** the pilot is a HEADROOM read, deliberately
  point-estimate-based, and a SCREEN only: a NO-GO does not prove the recipe
  class fails at full training scale, completed acceptance layers, or
  different author sources — it is a cheap stop-signal that the projected
  headroom was not visible at pilot cost, and proceeding to the instrument
  build despite a NO-GO requires a written maintainer decision. Symmetrically,
  a GO predicts nothing about the gate: if the recipe class cannot reach 0.80
  even here, freezing P3-E-NLB-1 immediately would likely burn a cycle
  [STIPULATED: ASM-0944(1)/(3)].
- **No-go routing:** the failing vertical's design returns to the drawing
  board WITHOUT consuming a registered cycle; the alternative branches —
  LLM-assisted parsing at API cost (the a5-nl assessment's
  `a5-nl-llm-successor` stub, which itself needs the ASM-0946(5) accounting
  stipulation before any gate use), or scope-narrowing to syntax-grounded
  formal/code domains per the round-1 negative-branch expectation — are
  escalated to the maintainer [STIPULATED: ASM-0944(2); stubs MEASURED:
  registry/assessments/a5-nl.json].

### 7.3 Why this is the cheapest INFORMATIVE screen

The two legs probe the two quantities the gate is made of, independently, at
near-zero cost: A probes whether S2 is controllable at its deterministic source
(if not, no threshold or contract layer saves it); B probes whether the learned
recipe shows retention headroom (if not visible even here, safety work is
premature). Neither leg DECIDES the gate — §7's scope limits are binding — but
any cheaper test (e.g. more paper analysis of the frozen breakdowns) cannot
probe either quantity at all, and any other cheap ordering (build the corpus
first; fine-tune first at full scale) spends the expensive artifact before the
screen [STIPULATED: ASM-0904; ASM-0944].

### 7.4 Cycle accounting (mechanical, so the kill cannot be gamed)

- DECISION: a "redesign cycle" counted by K-P3v2(2)/(5) is a FROZEN P3-E-NLB-1
  record (prereg-freeze → scored run → verdict). NLB-0 is a design-phase
  diagnostic: at most ONE NLB-0 per vertical per design revision; it never
  trains on any blind corpus; its results can never substitute for the gate;
  every NLB-0 artifact carries the diagnostic label, the §7 scope limits, and
  parent-verdict provenance [STIPULATED: ASM-0904(1)/(4); ASM-0944(4)].

### 7.5 Run plan and cost roll-up

| step | what | cost | screens |
|---|---|---|---|
| NLB-0-A | ROLE_DIR repair + both-orientation tests + legacy a5 diagnostic | ~$0, CPU (niced, 2 shared cores) | S2 controllability at source (Tier-0 only) |
| NLB-0-B | synthetic-trained pilot parser, legacy-corpus diagnostic | ≤ ~$25 API + ≤5 GPU-h (Modal/ARC free pool; `modal app stop` hygiene per standing memory) | retention headroom, per vertical |
| — GO (per vertical) → | NLB-EVAL/1 build (K=3 corpora, strata, annotation, audits) | ~$30–80 authoring/API | the instrument |
| — then | **P3-E-NLB-1** (experiment-designer freezes; runner runs; analyst reads out) | ≤ ~50 GPU-h R-1 free pool total incl. fine-tune | G-NLB per vertical; K-P3v2(2) input |

---

## 8. Interfaces to the rest of Programme-3

- **P3-D-ORACLE / KOT-DECOMP/1** (`docs/next/design/ORACLE.md`): NLB exports
  the per-stage counters (§4 close) and the gold-parse arms; ORACLE owns
  G2→G3 attribution and the oracle-splice ladder [STIPULATED: ASM-0821
  interface, adopted].
- **P3-D-PS (H-PS):** consumes NLB-FE/1 as its front-end; rendering
  (generation-from-checked-result) is P3-D-PS's problem and explicitly outside
  NLB scope — the gate ends at the engine answer [STIPULATED: ASM-0900].
- **P3-D-CONTRACT (proposed by the round-1 synthesis, not yet a bead):** owns
  the contract layer's full spec; §3.3 defines the arms the gate instrument
  carries either way, so NLB does not block on it [STIPULATED: ASM-0905(5)].
- **Abstention scoring (P3-D-INDEX open item):** G-NLB scores abstention
  internally (retention + creditable abstention) and makes no index claim, so
  it does NOT wait on the index abstention-scoring registration; any LATER G4
  use of a selective front-end does (the round-1 §B.2.3 dependency edge)
  [STIPULATED: ASM-0900(4); ASM-0811 untouched].
- **What waits behind this gate:** every ASM-0814 natural-input store leg of
  H-VL / H-GNN / H-RULE / H-DD / H-PS, per vertical [STIPULATED: ASM-0814
  restated] — and what the gate GIVES them is a prerequisite, not a
  certificate: each consumer ships the exact passed front-end hash, shows
  grammar compatibility (H-GNN subgraph extraction, H-RULE addressing, H-DD
  reinjection, and benchmark-facing H-PS have different output spaces and
  input distributions and do NOT inherit the pass), and carries its own
  task-originated G3 NL leg on its own distribution [STIPULATED: ASM-0945].

---

## 9. Honest limits and named risks

- **The gate may be unclearable.** No cited work reports retention-at-S2-bound
  for a ≤360M parser on a comparable closed grammar; the projection that this
  design clears it is registered as ASM-0906 and is never a premise
  [EXTRAPOLATION: ASM-0906]. The K-P3v2(2) branch — the surviving programme is
  formal/code interfaces, internal verification instruments, and compression
  diagnostics — is a legitimate, pre-agreed outcome, not a failure of this
  design [STIPULATED: ASM-0818 restated].
- **The guarantee is calibration-bound.** Conformal/calibration bounds assume
  exchangeability; the deployment phrasing distribution is unknown and the
  design's answer (source-disjoint CAL/EVAL + measured shift delta) makes the
  gap measurable, not absent [STIPULATED: ASM-0903(3)].
- **Consistent confident inversion.** The one class confidence cannot be
  trusted on is handled by three independent layers (deterministic repair,
  ambiguity-set execution, stratum kill) and its score-separability is itself
  measured (§6(4)) — but if a LEARNED parser develops a novel systematic
  inversion the deterministic inventory does not enumerate, the stratum rule is
  the only catch; this residual is disclosed on any PASS
  [STIPULATED: ASM-0901(3)/ASM-0903(4)].
- **Ambiguity detection is itself hard** (measured ~60% F1 cross-domain in the
  reviewed record) — which is why ambiguous items are independently ANNOTATED
  rather than machine-detected for scoring, and why CLARIFY is a scored-correct
  behaviour [LIT-BACKED: docs/next/lit/PARSE.md §4 triagesql line;
  STIPULATED: ASM-0901(4)].
- **The paraphrase ceiling is not 1.0.** Even learned parsers drop under
  lexical-correspondence removal; the review's honest band on a closed grammar
  is ~0.85–0.95 with paraphrase-diverse training + lexicon resources — the gate
  sits at the top of that band deliberately: clearing it should be hard, and
  the pilot exists because it may not clear [LIT-BACKED:
  docs/next/lit/PARSE.md §5a; EXTRAPOLATION: ASM-0906].
- **Corpus authorship is the instrument's soft underbelly.** K=3, disjoint
  sources, recoverability audits, and lint gates are the parents' hardened
  protocol extended; the skeptic re-attack before freeze (standing practice)
  attacks the corpus first [STIPULATED: ASM-0902].
- **The evaluation is oracle-conditioned at corpus construction.** Authors
  paraphrase known formal queries over a registered lexicon; recoverability
  repair and creditable-abstention annotation further shape the distribution.
  That supports a controlled semantic-parsing claim — it is NOT evidence about
  naturally occurring user traffic, and no PASS may be quoted as if it were;
  the limitation is disclosed verbatim on any PASS and is why consumers owe
  their own G3 legs [STIPULATED: ASM-0945(1)].
- **NLB-0 cannot de-risk Tier-1 safety.** The pilot's safety leg exercises the
  repaired deterministic tier only; whether the LEARNED fallback introduces
  new inversions is answered nowhere before the gate itself (acceptance layer
  + directional strata) — a residual disclosed on any GO
  [STIPULATED: ASM-0944(3)].

---

## 10. Epistemic register (what this design relied on)

- **STIPULATED (revision-1 block):** ASM-0900 (NLB/1 role, two-tier
  architecture, fail-closed invariants, no-index-claim exemption); ASM-0901
  (G-NLB gate, verbatim); ASM-0902 (NLB-EVAL/1 corpus protocol); ASM-0903
  (threshold freeze + risk control + the two secondaries); ASM-0904 (NLB-0
  pilot + cycle accounting); ASM-0905 (parser-class ordering, decoding
  discipline, acceptance arms).
- **STIPULATED (revision-2 corrective block, registered by this revision;
  append-only — where a rev-2 entry supersedes a rev-1 clause, both remain
  visible):** ASM-0940 (evidence-gated ambiguity-set semantics + frozen
  primary arm; supersedes the ASM-0905(5) executor clause); ASM-0941 (exact
  cluster-valid rare-event statistics, enumerated Holm family, analytic
  integer boundaries; supersedes ASM-0901(5)); ASM-0942 (five-role separation,
  corrected corpus arithmetic, rubric-governed ambiguity annotation;
  supersedes ASM-0902(3)/(5) and the size notes); ASM-0943 (fixed-sequence
  monotone threshold selection on CAL-B, calibrator on CAL-A; supersedes
  ASM-0903(1) mechanics); ASM-0944 (NLB-0 as a non-decisive per-vertical
  screen; supersedes ASM-0904(2)/(3) GO logic); ASM-0945 (PASS-as-prerequisite
  license + consumer obligations); ASM-0946 (executable resource ceiling,
  artifact manifest, in-gate cost measurement, KOT-LIFE/1 totals, API-parser
  rule); ASM-0947 (Tier-1 implementation-defining spec: IR, formal mask
  equivalence, candidate sets, confidence aggregation, entity linking,
  training recipe).
- **EXTRAPOLATION (registered, never a premise):** ASM-0906 — the projection
  that this recipe clears G-NLB on at least one vertical; resolver NLB-0 →
  P3-E-NLB-1.
- **STIPULATED (inherited, restated in force):** ASM-0814 (NLB gates all
  natural-input store use), ASM-0817 (gate ladder + CAL exemption), ASM-0818
  (K-P3v2 kills), ASM-0808 (parser-inside-the-product), ASM-0812/0810
  (accounting symmetry), ASM-0144/0145/0420 (parent instrument forks carried),
  ASM-0821/0824 (KOT-DECOMP interface).
- **MEASURED (each strictly inside its envelope):** l3a-parse and a5-nl
  verdicts + analysis outputs (§2 table); l3a/a5 engine exactness and timing;
  the a5 assessment's repair/successor stubs; the recoverability audit.
- **LIT-BACKED (through the completed Phase-0 review's verified ledger):**
  every external claim above cites `docs/next/lit/PARSE.md` by section; primary
  sources and verification status live in `docs/next/lit/PARSE.sources.jsonl`.

This document changes no frozen object, no verdict, no audit, and no registry
entry outside the fresh ASM-0900–0906 (revision 1) and ASM-0940–0947
(revision 2, append-only corrective) blocks.
