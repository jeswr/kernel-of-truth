# Design + pre-registration spec — a5-llm: the engine-vs-LLM head-to-head on the a5 code-structure slice

**Status:** DESIGN-COMPLETE, maintainer-sign-off PENDING. This is the prereg
anchor for registry experiment `a5-llm` (DRAFT record
`registry/experiments/a5-llm.json`; idea `idea-code-worldlayer-cpg`,
successor 1 of `docs/design-a5-code-worldlayer-oracle.md` §7; unblocked by
the a5 PASS, cross-vendor audit CONFIRMED). **Not frozen. Do not run
`prereg-freeze` or spend before the maintainer signs off** (bead
kernel-of-truth-lbv; Fable/Opus split, docs/next/opus-execution-practices.md).
Author: Kern (Fable design agent), 2026-07-09.
**Binding constraints:** `docs/kernel-design-directives.md` (§1 native
formalism, §2 two value theses + full V, §4 don't-guess-test, §6 honest
stats); `docs/next/architecture-ladder.md` §5.1 (HL3a kill shapes) + §1
ladder-wide rules; `docs/next/resource-optimization-plan.md` (reuse
DEFERRED ⇒ FRESH runs only; pre-spend gate; reuse_overrides for the
deliberate engine re-run); f2b-replicate's absolute-non-inferiority /
verbatim-kill / envelope style mirrored throughout.

## 0. What this experiment is — and is not (HONEST SCOPE, registered)

The frozen a5 record measured the ENGINE leg only and explicitly licensed
**no engine-vs-LLM claim**: the arXiv:2505.12118 motivation ("LLMs perform
poorly on call-graph/AST static-structure tasks") entered a5 as LIT-BACKED
literature, never as a measurement. `a5-llm` is the pre-declared successor
that runs the LLM arms **on the identical pinned slice** (same corpus
hashes, same 977 queries, same strata) so that the head-to-head becomes
MEASURED — in either direction.

- This record CAN kill the differentiator: if a small LLM with the same
  facts rendered as text matches the engine's conjunctive accuracy, the L3
  code vertical's exactness edge is dead on this slice regardless of
  elegance (architecture-ladder §5 risk 3), and only the cost edge
  survives as a separate, separately-gated claim.
- This record can NOT establish: NL robustness (queries are rendered from
  the closed grammar by fixed templates, not authored by humans — `a5-nl`'s
  jurisdiction), anything about frontier or long-context models (pinned
  ladder is SmolLM2-Instruct 135M–1.7B), static-analysis ability of LLMs
  given raw source (no source-in-context arm — dropped with reason, §2.3),
  or representativeness of the 15-file corpus.

- PREMISE: the a5 engine leg is an adequate instrument on this slice
  (covered exact Wilson-LB 0.9968 above the 0.98 gate, control
  strict-refusal Wilson-LB 0.9783 above the 0.95 gate, 3/3 planted
  violations, byte-identical repeat, 7.82 µs/query).
  [MEASURED: registry/verdicts/a5.json — PASS, audit CONFIRMED; scope =
  that build + these pinned corpora]
- PREMISE: LLMs perform poorly on call-graph / AST static-structure
  tasks. [LIT-BACKED: arXiv:2505.12118 (2025/EMSE 2026), carried via
  reports/lit-structured-parsing-and-inner-symbolic.md §1.2 — this record
  RE-MEASURES that claim on this slice for the pinned small-model ladder;
  it stops being a premise and becomes the thing under test]
- PREMISE: the pinned SmolLM2-Instruct revisions predate the 2026-07-09
  snapshot corpus, so the direct arms are closed-book on these facts by
  construction. [STIPULATED: ASM-0014 — training-set membership is not
  directly verifiable; the dated-artifact argument (2024 checkpoints,
  2026 repo tooling) is strong but stipulated]
- PREMISE: the prompt pack, record→text renderer, and lenient extraction
  rules are a fair-to-the-LLM instrument; every leniency asymmetry runs
  in the LLM's favour (§3.4), making the engine-superiority claim
  conservative. [STIPULATED: ASM-0012, ASM-0013]

**X3 TRAP (restated per the idea-registry note):** concept and entity
identity everywhere is exact URN string match — the retrieval rule (§3.3)
is exact slug equality, never embedding or fuzzy similarity; there is no
kernel-space nearest-neighbour step anywhere in this design.

## 1. Decision value (why this rung, why now)

Two theses are on the line (directives §2), each with its own gate:

1. **Correctness/exactness differentiator** — the engine's conjunctive
   profile (exact covered answers AND licensed refusals) is claimed to be
   unmatchable by an LLM at these scales *even when the same facts are
   handed to it as text* (Law-2's kernel-as-text null, here in its
   strongest form: complete, exact retrieval + rendered axioms). If the
   best LLM arm matches it, the differentiator dies — a clean, publishable
   negative that re-scopes L3b's router premise before any L3b spend.
2. **Efficiency differentiator** — HL3a's ≥10³× cost claim
   (architecture-ladder §5.1) has never been measured against an actual
   LLM arm on this slice; a5 reported engine µs/query descriptively only.

Gate context: a5 PASS (audit CONFIRMED) unblocks this successor; it is
Tier-1, needs no training, and its verdict re-prices the L3 family
(l3a-cost is the same-shape sibling on the L3a slice, bead gv7).

## 2. Arms (all FRESH runs; reuse is DEFERRED programme-wide)

| Arm | Rungs | What it is | Status |
|---|---|---|---|
| `engine` | R0 | kot_axiom.py + kot_code.py, byte-identical to the a5 pins, full 977-query pass | fresh deliberate re-run ($0, CPU); `reuse_overrides` declared for the a5 collision; doubles as the engine-regression instrument gate (§5.4) |
| `abstain-all` | R0 | refuses every query | fresh re-run ($0); bracketing baseline continuity with a5 |
| `answer-all` | R0 | never refuses; fabricates deterministically from the same indexes | fresh re-run ($0); brackets the conjunction |
| `llm-direct` | R1, R2, R3 | pinned SmolLM2-Instruct answers the rendered query CLOSED-BOOK (no records in context) | fresh; measures the fabrication/refusal surface + scale sign |
| `llm-rag` | R1, R2, R3 | same prompt + CONTEXT block: the 5 axiom records + ALL world records exact-slug-matching the query's entities, rendered to pinned English templates | fresh; **the load-bearing Law-2 competitor** |

The LLM family for every comparative statistic is the exhaustive declared
set {llm-direct, llm-rag} × {R1, R2, R3} — six cells; "best-LLM" is a max
over this family (§5.2), never a hand-picked cell.

### 2.1 Model pins (pinned directly; already resolved by F2/f2b ops)

- R1 `HuggingFaceTB/SmolLM2-135M-Instruct@12fd25f77366fa6b3b4b768ec3050bf629380bac`
- R2 `HuggingFaceTB/SmolLM2-360M-Instruct@a10cc1512eabd3dde888204e902eca88bddb4951`
- R3 `HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a7173562077fd711b654946d38674`

Decode pins: greedy (do_sample=false, temperature 0), max_new_tokens 512,
context window 8192, chat template as shipped with the pinned revision.
Greedy decode makes every LLM cell deterministic given the pins; seeds
carry the registered placeholder [0] (a5 convention).

### 2.2 Why the RAG arm is built ORACLE-STRONG (and what that buys)

The retrieval rule (§3.3) is exact, complete, and deterministic: it hands
the model every record that can answer the query, plus the rendered axiom
sidecar. This deliberately UPPER-BOUNDS any deployable RAG (real retrievers
miss). If the engine beats even this arm, no weaker retrieval pipeline
rescues the LLM on this slice; if it does not, the differentiator kill is
earned against the strongest form of the null, not a strawman. RAG-arm
construction is therefore not a tunable — it is the Law-2 null in its
maximally charitable form.

### 2.3 Right-size: arms deliberately NOT run (each with its reason)

- **source-in-context** (raw Python files in the prompt): the 8k context
  cannot hold the cross-file call graph (snapshot is 255 KB across 15
  files); the arm would measure truncation policy, not static analysis.
  Named successor (long-context rungs), not a silent drop.
- **frontier-API arm** (GPT/Claude-class): un-pinnable revisions +
  external-API spend policy; successor candidate once the maintainer wants
  a frontier read; the envelope below explicitly does NOT cover frontier
  models.
- **NL-paraphrase robustness**: `a5-nl`'s jurisdiction.
- **sampling-seed sweeps**: greedy decode is deterministic; a seed sweep
  measures nothing here.
- **k-retrieval ladder**: retrieval is complete by construction (§3.3
  lint); a k-ladder would only degrade the null below its strongest form.

## 3. The LLM instrument (pinned at freeze; every choice below is part of the instrument identity)

### 3.1 Prompt pack (verbatim task preamble; few-shot on a TOY world only)

Fixed preamble (both LLM arms, all rungs):

> You are answering questions about the static structure of a fixed
> Python codebase. Entities are named by exact identifiers (URNs) like
> `urn:kotw:v0:code-fn-example--main`. Answer ONLY from what you know
> or from the CONTEXT records if provided. Reply with a single JSON
> object on one line: `{"answer": ["<identifier>", ...]}` for a list
> answer, `{"answer": true}` or `{"answer": false}` for a yes/no
> question, or `{"refuse": "<short reason>"}` if the question cannot be
> answered (unknown entity, no matching record, conflicting records, or
> a malformed question). Output nothing else.

Three fixed few-shot examples follow the preamble, authored over a
SYNTHETIC toy world (`urn:kotw:v0:code-fn-toy--*` identifiers, disjoint
from the corpus by construction — zero leakage): one list answer, one
boolean answer, one refusal. Any pre-freeze prompt iteration happens
against a 30-query toy-world probe set ONLY (never against a5-eval items);
the final prompt pack is emitted deterministically by the instrument and
its digest is recorded in every run record.

### 3.2 Query rendering (8 fixed templates, one per op)

callers-of → "Which functions call `<X>`?" · callees-of → "Which functions
does `<X>` call?" · where-defined → "In which single scope (module, class,
or function) is `<X>` defined?" · imports-of → "Which corpus modules does
module `<X>` import?" · imported-by → "Which corpus modules import module
`<X>`?" · contains → "Which constructs are lexically contained in `<X>`?"
· contained-in → "Which scopes lexically contain `<X>`?" · instance-of →
"Is `<E>` an instance of the concept `<C>`?"

Control queries in the `malformed` stratum (unknown/extra ops or fields)
have no template by construction; they are rendered as: "Answer this
structural query if it is well-formed, otherwise refuse: `<raw query
JSON>`". Disclosed: this stratum tests refusal on garbage, identically for
all arms.

### 3.3 RAG context construction (deterministic, exact, complete)

- **Axiom block (every rag prompt, pinned verbatim rendering of the 5
  code-axioms-v0 records):** functions/classes/modules are pairwise
  disjoint kinds as declared; every function and class is defined in
  exactly one scope; modules are not "defined in" a scope; calls relate
  functions; imports relate modules; containment is transitive with
  has-part as inverse.
- **Record retrieval:** all `code-world-v0` records whose subject or
  object URN string-equals any entity URN in the query (for instance-of:
  the entity and the concept). Exact string match only (X3-compliant).
  Rendering, one line per record, sorted by record id:
  class → "`<e>` is a `<python-module|python-function|python-class>`.";
  code-calls → "`<s>` calls `<o>`."; code-defines → "`<s>` defines
  `<o>`."; code-imports → "`<s>` imports `<o>`."; part-of → "`<s>` is
  lexically contained in `<o>`.". Planted-violation records render like
  any other (the conflict stratum NEEDS the model to see the conflict).
- **Empty retrieval** renders "CONTEXT: no records found for the entities
  in this question." (that is what honest RAG returns; it favours correct
  LLM refusals — pro-LLM, conservative for the superiority claim).
- **Completeness lint (build-time, mechanical, gate input):** for every
  covered query, the record set sufficient to derive the pre-authored
  expected answer must be a subset of the retrieved set;
  `/analysis/retrieval_completeness_violations` must equal 0 or the
  instrument is invalid (if any transitive-containment chain is not
  materialised per-pair in the store, the retrieval rule extends to the
  deterministic closure walk BEFORE freeze — fork FK-A5L-2).
- **Token budget:** prompts exceeding the 8192 context are truncated
  deterministically from the LONGEST context block tail, with the
  truncation count reported per cell; expected 0 (worst-case entity degree
  in an 889-record store fits comfortably).

### 3.4 Extraction + scoring (lenient-to-the-LLM; every asymmetry disclosed)

| Aspect | Engine (a5 rules, unchanged) | LLM arms (lenient) |
|---|---|---|
| covered exact | status=answer ∧ value=expected ∧ provenance⊆world-ids ∧ license≠∅ | extracted answer equals expected under normalisation: order-insensitive set equality; case-insensitive; whitespace-trimmed; full URN or terminal slug accepted; booleans accept true/false, yes/no |
| control correct | strict expected ERR_* code match | ANY well-formed refusal (JSON `refuse` field, or a pinned refusal-marker regex list: "cannot answer", "unknown", "no record", "not sure", "I don't know", refusal-shaped sentences) |
| provenance | required | not required |
| extraction | n/a (structured) | JSON-first parse; then pinned lenient regexes for answers and refusals; outputs matching neither = extraction failure (instrument event, §5.4, never a hypothesis event) |

Every asymmetry favours the LLM arms; the superiority claim is therefore
conservative. The exact normaliser and regex list are pinned inside
`tools/experiments/a5_llm_instrument.py` at freeze; changing any of them
after freeze is an instrument version change (correction record).

Per-query conjunctive correctness (the primary's unit), per arm: covered
query → covered-exact rule for that arm; control query → control-correct
rule for that arm. Extraction failures score 0 for the arm AND count
toward the extraction instrument gate.

### 3.5 Fairness disclosures (pre-registered, verbatim)

1. Control queries are scored refusal-expected for ALL arms (the a5
   pre-authored expectations); for 6/122 out-of-scope-concept controls an
   LLM could argue the question is answerable-in-spirit — disclosed;
   weight 0.6% of the eval, cannot move any gate.
2. The direct arms are closed-book by construction (ASM-0014): their
   expected covered-exact is ≈0 and their honest role is the
   fabrication/refusal surface + the scale sign, not a knowledge claim.
   The head-to-head headline is engine vs llm-rag.
3. Engine runs on 2 shared CPU cores; LLM cells run batched on a pinned
   Modal GPU class. Cost accounting per F0 §3.3/§3.4: engine CPU time
   metered at the pinned core rate; LLM at metered GPU-seconds × the
   pinned Modal rate; batching disclosed. Latency reported per-query
   p50/p95 both ways.

## 4. Cost accounting (F0 discipline)

- `usd_per_query(engine)` = measured ns/query × pinned CPU core rate (the
  f2b-replicate verifier-metering convention).
- `usd_per_query(llm cell)` = metered GPU wall-seconds for the cell ×
  pinned Modal GPU rate ÷ 977 (+ per-query token counts and FLOPs ≈
  2·N·tokens reported descriptively).
- `cost_ratio_min` = min over the six LLM cells of
  usd_per_query(cell) / usd_per_query(engine). The 10³ gate (§5.3) reads
  this minimum — the claim must hold against the CHEAPEST LLM cell.
- Planning constants (throughput, tokens/query) are dry-plan ESTIMATES
  only and are never emitted as measurements [STIPULATED, a5/f2b
  convention].

## 5. The pre-registered eval (registry id `a5-llm`)

### 5.1 Corpus + query set

Identical pins to a5, verbatim: `a5-eval` (977 = 855 covered / 122
control; strata as frozen in a5), `code-world-v0`, `code-axioms-v0`,
`code-v0`, `code-corpus-v0`, `kernel-v0` — corpus digests copied unchanged
into the record. No new corpus: prompts are emitted deterministically at
run time from pinned inputs by the pinned instrument, and the emitted
prompt-pack digest is recorded in every run record.

### 5.2 Primary endpoint (absolute, no denominator — the f2b-replicate lesson)

**effect_size = conj_acc(engine) − conj_acc(best-LLM)** over the 977
pinned queries, where best-LLM is the cell with the highest conjunctive
point estimate among the six-cell exhaustive family, restricted to cells
passing their extraction instrument gate (taking the max is conservative
for the engine; the family is exhaustive and declared, so no selection
laundering is possible). Paired per-query BCa bootstrap (B=10000, PRNG
seed 20260709), one-sided α=0.05.
**PASS-side reject iff the one-sided 95% lower bound > 0.10** (smallest
effect of interest: 0.10 absolute conjunctive-accuracy superiority).

Decidability/power: engine conjunctive point ≈ 0.996 (from a5's logged
counts, re-measured fresh here); at n=977 paired, the bootstrap CI
half-width is ≲0.03 for any plausible LLM accuracy, so the LB>0.10 /
UB≤0.10 pair is decidable across the whole plausible range (planning value
for best-LLM conj: 0.45–0.75; power ≈ 1 at those values; the design stays
decision-valid even at best-LLM = 0.85).

### 5.3 Co-gate + secondaries (ONE Holm family, membership pre-declared)

- **sec-cost-gate (verdict-bearing co-gate, not Holm):**
  `cost_ratio_min ≥ 10³` (HL3a's cost clause, measured; point estimate of
  a metered deterministic quantity). FAIL-side kill below 10³.
- **sec-separation-gate (INSTRUMENT gate, f2b-style, not a hypothesis
  test):** conj(llm-direct-R3) − conj(llm-direct-R1) ≥ 0.05 AND one-sided
  95% BCa LB > 0. On failure, the scale-trend secondary is
  INSTRUMENT-INVALID and leaves the Holm family BEFORE any p-value
  comparison; the absolute primary still reads.
- **Holm family F-secondary(a5-llm)** at α=0.05:
  1. `covered_superiority`: covered-exact(engine) − covered-exact(best-LLM
     cell) one-sided LB > 0.
  2. `refusal_superiority`: control-refusal(engine, strict) −
     control-refusal-any(best-LLM cell) one-sided LB > 0.
  3. `rag_lift_r3`: conj(llm-rag-R3) − conj(llm-direct-R3) one-sided
     LB > 0 (do handed facts rescue the LLM at the largest rung?).
  4. `scale_trend_rag` (CONDITIONAL on the separation gate):
     conj(llm-rag-R3) − conj(llm-rag-R1) one-sided LB > 0 — sign-only
     language, per the envelope.
  5. `fabrication_material`: fabrication rate (non-refusal answers on
     control queries) of the best-LLM cell, Wilson 95% LB > 0.30 — the
     anti-hallucination surface made quantitative.
- Descriptive (never Holm, never verdict-bearing): per-cell accuracy
  tables by stratum, latency ratios, FLOPs, token counts, truncation
  counts, abstain-all/answer-all brackets, direct-arm covered-exact
  (expected ≈0, closed-book).

### 5.4 Instrument gates (failures are instrument events, never hypothesis events)

`/gates/instrument_valid` requires ALL of:
1. **Pins/strata**: arm presence, 977-query strata counts equal to the a5
   manifest, corpus digests match the frozen record.
2. **Engine regression**: the fresh engine pass reproduces a5's logged
   per-query outcomes exactly (deterministic; byte-identical repeat also
   required) — `/analysis/engine_matches_a5 = 1`. A mismatch indicts the
   instrument (engine/store drift), not any hypothesis.
3. **Extraction gate per LLM cell** (P10 analogue): extraction-success
   (parseable answer or recognisable refusal) Wilson 95% LB ≥ 0.90 at
   n=977 for the cell. A failing cell is excluded from best-LLM selection
   and from Holm members referencing it (disclosed in the verdict);
   **record-level validity requires ≥1 llm-rag cell AND ≥1 llm-direct
   cell passing** — if every rag cell fails, the Law-2 competitor was not
   validly measured and the record is INSTRUMENT-INVALID.
4. **Retrieval completeness**: `/analysis/retrieval_completeness_violations = 0`.

### 5.5 Verdict rules (ordered, first-match-wins; mechanical)

1. INSTRUMENT-INVALID iff NOT `/gates/instrument_valid`.
2. FAIL iff `differentiator_within_kill` OR `cost_ratio_min ≤ 10³` OR
   primary one-sided 95% UB ≤ 0.10.
3. PASS iff primary one-sided 95% LB > 0.10 AND `cost_ratio_min > 10³`
   AND `engine_matches_a5 = 1`.
4. INCONCLUSIVE otherwise.

## 6. Kill criteria (verbatim; frozen into the record)

HA5-LLM kills (the architecture-ladder §5.1 third-kill, instantiated for
the code vertical, plus the HL3a cost clause): (a) DIFFERENTIATOR-KILL —
any extraction-gate-valid LLM cell (the exhaustive declared six-cell
family only; trivial baselines excluded) reaches conjunctive accuracy
within 0.05 (point estimate) of the engine's on the pinned 977-query
slice: the exactness differentiator is dead on this slice regardless of
cost, the record names the killing cell, and L3b's router premise must be
re-argued from cost alone; (b) COST-KILL — cost_ratio_min ≤ 10³ (usd/query,
F0 accounting): HL3a's ≥10³× cost clause is dead at this scale and the
efficiency thesis for the L3 code vertical reverts to unproven; (c)
primary one-sided 95% UB ≤ 0.10: the superiority margin is demonstrably
not met. Extraction-gate failures and engine-regression mismatches are
instrument events and can never fire a kill or a PASS.

## 7. What a PASS means (and does not)

PASS = on THIS pinned slice, with the same facts available as rendered
text to the strongest-form RAG null, pinned small LLMs (≤1.7B, one family)
fall short of the deterministic engine's conjunctive exact-answer +
licensed-refusal profile by >0.10 absolute, and the engine answers at
>10³× lower usd/query — the arXiv:2505.12118-motivated head-to-head, now
MEASURED, in the engine's favour, at these scales. It licenses the L3b
router premise AT these rungs and prices the anti-hallucination surface.

It does NOT show: anything about frontier or long-context models; NL
robustness (a5-nl); LLM static-analysis ability from raw source (no such
arm); other codebases/languages; kernel usefulness to any model's internal
computation; or that a weaker (deployable) RAG pipeline would do as well
as the oracle-strong null measured here.

## 8. Forks (directives §4 form)

**FK-A5L-1 — answer-format strictness.** (a) strict JSON-only extraction;
(b) lenient JSON+regex extraction (DEFAULT, pro-LLM). Why uncertain: small
instruct models drop JSON discipline unpredictably; strict extraction
would score format failures as wrong answers and could fake the
differentiator. Decided by: the toy-world probe pilot pre-freeze
(instrument engineering, never a5-eval items); the extraction instrument
gate (§5.4) is the in-run guard. Kill per option: extraction-success
Wilson-LB < 0.90 for the load-bearing cells.

**FK-A5L-2 — retrieval scope.** (a) exact subject/object slug match
(DEFAULT); (b) + deterministic transitive-closure walk for containment
chains. Why uncertain: whether the store materialises per-pair transitive
containment. Decided by: the build-time completeness lint (§3.3),
mechanically, before freeze; (b) activates only if the lint fails under
(a). Kill: none — this is instrument completeness, resolved pre-freeze.

## 9. Right-sized cost estimate (Tier 1)

- LLM cells: 6 × 977 = 5,862 prompts; mean ≈700 prompt + ≈60 decode
  tokens (max 512) ⇒ ≈4.5M tokens total, prefill-dominated, models ≤1.7B,
  batched greedy on one pinned Modal GPU: ≲2 GPU-h including model loads
  and the toy-probe smoke. Estimate **$3–8**; budget caps: usd_cap 25,
  gpu_hours_cap 4, wall_clock_cap_hours 24.
- Engine + trivial baselines + analysis: $0 (r0-local-cpu, nice -n 10,
  foreground gates).
- Pre-spend gate: `reuse-check.py check --record … --gate` WILL flag the
  engine/abstain-all/answer-all cells already logged by a5 at identical
  pins; the frozen record carries the `reuse_overrides` entry (deliberate
  fresh re-run; reuse-permission DEFERRED; $0 deterministic CPU; the fresh
  run IS the engine-regression instrument gate), which is the lawful
  response (resource-optimization-plan §3.6 path ii).

## 10. Successors (register separately; NOT this record)

1. `a5-llm-frontier` — frontier/long-context arms incl. source-in-context
   (the literal arXiv:2505.12118 task shape) — maintainer decision on
   external-API spend and pinning policy first.
2. `a5-nl` — NL/mapper parse leg (human-phrased code questions).
3. `l3a-cost` — same-shape sibling on the L3a litmus-family slice (bead
   gv7); shares this record's prompt/render/cost machinery (component
   reuse, not data reuse).

## 11. Registered scope statement (extrapolation envelope, verbatim-in-record)

Measured range: R1–R3 SmolLM2-Instruct pinned revisions (135M/360M/1.7B —
ONE model family, ONE vendor, 3 rungs ⇒ SIGN plus at most
direction+order-of-magnitude trend language, never a slope law); ONE
pinned 977-query closed-grammar eval authored against ONE extracted
889-record world layer from ONE 15-file Python snapshot; ONE prompt pack +
ONE deterministic exact-match retrieval rule + ONE lenient extraction
instrument (results are indexed to this instrument identity); greedy
decode only. Coverage disclosure: the covered slice is covered BY
CONSTRUCTION (queries authored against the extracted records) — every
accuracy statement is bounded to this slice and licenses no
representativeness claim for any other codebase, language, or query
distribution. The verdict extrapolates to NO frontier or long-context
model, NO deployable-RAG effectiveness claim (the null here is
oracle-strong by design), NO NL behaviour, NO static-analysis-from-source
claim, and licenses NO statement about kernel usefulness to any model's
internal computation. The closed-book direct arms measure fabrication/
refusal behaviour, not knowledge.

## 12. Assumptions block (register entries to be appended centrally)

- [STIPULATED: ASM-0012] the prompt pack, few-shot toy examples,
  record→text renderings, refusal-marker regexes, and answer normaliser
  are a stipulated pro-LLM-lenient instrument; every asymmetry runs in
  the LLM's favour; changing any of them is an instrument version change.
- [STIPULATED: ASM-0013] the record→English rendering + rendered axiom
  block is a faithful kernel-as-text (Law-2) form of the same content the
  engine consumes; the oracle-strong retrieval upper-bounds deployable RAG.
- [STIPULATED: ASM-0014] the pinned 2024 SmolLM2 checkpoint revisions
  predate the 2026-07-09 snapshot corpus; direct arms are closed-book on
  these facts (dated-artifact argument; training-set membership not
  directly verifiable).
- [MEASURED: registry/verdicts/a5.json] the engine leg is an adequate
  instrument on this slice (PASS, audit CONFIRMED; scope = that build +
  these corpora).
- [LIT-BACKED: arXiv:2505.12118] LLM weakness on code-structure tasks —
  motivates the rung AND is re-measured here at R1–R3; it does not enter
  the verdict function as a premise.
