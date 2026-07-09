# Design + pre-registration spec — A5: the code world-layer + code-structure oracle

**Status:** design record + the prereg anchor for registry experiment `a5`
(idea `idea-code-worldlayer-cpg`, docs/next/idea-registry.md §4.1 NOW-list
item 5; **HA5 engine leg**, deterministic extraction, gold-op queries).
Author: Kern (Fable agent, runner-3), 2026-07-09.
**Binding constraints:** `docs/kernel-design-directives.md` (§1 native
formalism, §3 method, §5 strata, §6 honest stats);
`docs/design-l3a-rules-engine-oracle.md` (the kot-axiom/1 v0 engine +
kot-query/1 grammar this vertical builds ON, UNCHANGED — L3a PASS is the
gate that green-lit this fast-follow); `docs/design-constraint-layer.md`
§3.3 (kot-axiom/1 grammar). Epistemic tags per
`docs/next/assumption-register.md`.

## 0. What this experiment is — and is not (HONEST SCOPE, registered)

A5 extends the L3a rules-engine oracle to a CODE vertical: a deterministic,
CODE-based (no LLM anywhere) extractor populates a stratum-4 world layer from
a pinned Python snapshot corpus, and a closed code-structure query grammar
(`kot-query-code/1`) is answered by the UNCHANGED kot-axiom/1 v0 engine via
pure desugaring. **This record tests the ENGINE's correctness on
deterministically-extracted code structure — nothing else.**

- PREMISE: the kot-axiom/1 v0 engine + four-strata store is an adequate
  instrument on its covered slice with licensed refusals elsewhere.
  [MEASURED: registry/verdicts/l3a.json — l3a PASS, audit CONFIRMED; scope =
  that engine build, extended here only by data and a desugaring layer]
- PREMISE: LLMs perform poorly on call-graph / AST / data-flow static-analysis
  tasks, and pretraining on such tasks does not transfer to better code
  intelligence. [LIT-BACKED: arXiv:2505.12118 (2025/EMSE 2026), established;
  carried via reports/lit-structured-parsing-and-inner-symbolic.md §1.2]
  **This motivates the rung and is NOT re-measured here: this $0 record has NO
  LLM arm, and its verdict licenses NO head-to-head engine-vs-LLM claim.**
- PREMISE: serialized-AST/deep-static-analysis INPUT injection at LLM scale is
  parity, so the living seat for deterministic code structure is an external
  engine/world-layer, not the encoder input. [LIT-BACKED: arXiv:2602.06671
  (2026) + arXiv:2505.12118; the X1 non-adoption boundary,
  reports/lit-structured-parsing-and-inner-symbolic.md §1.2]
- PREMISE: the construct->concept mapping table (six minted code-v0 concepts +
  reused kernel-v0 part-of/has-part for containment) is a stipulated modelling
  choice with exact content-hash identity. [STIPULATED: ASM-0007]

In code, the Law-3 engine seat is already held by compilers/static analysers;
the kernel's marginal value exercised here is canonical concept IDENTITY
across domains (the part-of reuse), not re-doing static analysis.

**X3 TRAP (binding, restated at freeze per the idea-registry note):** concept
identity everywhere in this vertical is by EXACT content-hash URN — the
extractor's construct->concept table, the axiom layer, and the query layer's
op->relation table are all exact `sourceId -> minted URN` lookups from the
minted-urns files. NO kernel-space nearest-neighbour, NO similarity step,
anywhere.

## 1. The four strata, instantiated for code

| Stratum | Artifact | Where |
|---|---|---|
| 1–2 profile + definitions | minted concept URNs: 6 new (code-v0, `kot-code-construct/1` structural definitions — NOT NSM explications, ASM-0007) + reused kernel-v0 `part-of`/`has-part` | `data/code-v0/` (minted 2026-07-09, canonical mint tool), `data/kernel-v0/` (untouched) |
| 3 endorsed axiom sidecar | 5 `kot-axiom/1` records | `data/code-axioms-v0/` |
| 4 world layer | 889 `kot-world/1` records (879 extracted + 10 planted, flagged by provenance) | `data/code-world-v0/` |
| — query boundary | closed grammar `kot-query-code/1` desugaring to `kot-query/1`; engine UNCHANGED | `tools/axiom/kot_code.py` (layer), `tools/axiom/kot_axiom.py` (v0 engine, byte-identical to the l3a pin) |

Source corpus: `data/code-corpus-v0/src/` — a pinned SNAPSHOT of 15 Python
files copied from this repo's own tooling (registry tools, the axiom engine,
two instruments, two analysis scripts) on 2026-07-09; the snapshot, not the
live files, is what the extractor reads and the corpus pin hashes.
Extractor: `kot-code-extract/1` (`tools/axiom/gen_a5_corpora.py`), CPython
stdlib `ast`, RNG-free, fail-closed slug collisions; version + script sha are
recorded in every run record (`config.extractor_version`,
`config.extractor_sha256`) and the corpus digests are frozen in the record.

## 2. The construct -> concept mapping (ASM-0007, exact-hash, closed)

| Extracted construct | Record | Concept (exact minted URN by sourceId) |
|---|---|---|
| source file | `kind:class` | code-v0 `python-module` |
| ast.FunctionDef / AsyncFunctionDef | `kind:class` | code-v0 `python-function` |
| ast.ClassDef | `kind:class` | code-v0 `python-class` |
| resolved call, caller -> callee | `kind:relation` | code-v0 `code-calls` |
| immediate-child definition, scope -> construct | `kind:relation` | code-v0 `code-defines` |
| corpus-internal import, module -> module | `kind:relation` | code-v0 `code-imports` |
| transitive lexical containment, construct -> enclosing scope | `kind:relation` | kernel-v0 `part-of` (inverseOf `has-part`) |

Extraction is CONSERVATIVE static assertion (exact-name call resolution only;
extra-corpus imports and unresolvable calls assert NOTHING); soundness w.r.t.
Python runtime semantics is not claimed and not load-bearing — the verdict
scores against the records. [STIPULATED: ASM-0009]

Entities are `urn:kotw:v0:code-*` — the same deliberately separate identifier
space as world-v0, so no world fact can leak into definitional content-hashes.
Every record carries `provenance.source` (extractor version + file:line, or
the planted-violation flag).

## 3. The stratum-3 axiom set (data/code-axioms-v0/)

| Record | Subject concept | Constraints | Licenses |
|---|---|---|---|
| class-python-function.json | python-function | disjointWith module, disjointWith class; cardinality {path defines, inverse, min 1, max 1} | instance-false; where-defined uniqueness |
| class-python-class.json | python-class | disjointWith module; cardinality {path defines, inverse, min 1, max 1} | instance-false; where-defined uniqueness |
| rel-code-calls.json | code-calls | domain function; range function | callers-of / callees-of lookups |
| rel-code-imports.json | code-imports | domain module; range module | imports-of / imported-by lookups |
| rel-part-of.json | part-of | inverseOf has-part | contains / contained-in lookups |

Honesty notes. (i) `defines` carries no domain/range: its domain is a UNION
(module-or-class-or-function scope) the v0 grammar cannot express — left
unstated rather than mis-stated; it is licensed through the cardinality
constraints. (ii) A def nested under if/try is NOT an immediate child: it gets
class + containment records but no defines edge (count reported by the
generator; 0 in this corpus). (iii) These axiom sets are contestable world
modelling and therefore sidecar-endorsed, not identity.

## 4. kot-query-code/1 — the closed code-structure grammar

Eight named operators, each a PURE DESUGARING to one core kot-query/1 query
(design-l3a §4); the engine's pre-registered validation order and named
refusal codes apply unchanged downstream of the desugar step:

| Op | Form | Desugars to |
|---|---|---|
| `callers-of` | {op, of} | lookup(code-calls, inverse, of) |
| `callees-of` | {op, of} | lookup(code-calls, forward, of) |
| `where-defined` | {op, of} | unique(code-defines, inverse, of) — uniqueness axiom-licensed, never assumed |
| `imports-of` | {op, of} | lookup(code-imports, forward, of) |
| `imported-by` | {op, of} | lookup(code-imports, inverse, of) |
| `contains` | {op, of} | lookup(part-of, inverse, of) |
| `contained-in` | {op, of} | lookup(part-of, forward, of) |
| `instance-of` | {op, entity, concept} | instance(entity, concept) |

Fail-closed boundary: the grammar is CLOSED. Unknown ops — including the
semantic/static-analysis asks the grammar deliberately does not cover
(type-of, data-flow-of, docstring-of, ...) — missing/extra fields, and
non-string arguments refuse `ERR_BAD_QUERY` at the desugar step; raw core
kot-query/1 ops are not exposed through this layer. Everything admitted then
passes the engine's chain: term licensing -> entity existence -> conflict ->
op license -> records (`ERR_TERM_UNLICENSED`, `ERR_UNKNOWN_ENTITY`,
`ERR_CONFLICT`, `ERR_UNLICENSED_UNIQUE`, `ERR_NO_RECORD`). Every answer
carries `provenance` (world-record ids) and `license` (axiom constraint refs).

## 5. The pre-registered eval (registry id `a5`)

### 5.1 Corpus and query set (pinned)

`data/code-world-v0/` (889 records: 879 extracted from the 15-file snapshot —
216 constructs, 201 defines, 292 containment, 10 imports, 160 calls — plus 10
planted records realising exactly 3 pre-declared violations: 1
VIOLATION_DISJOINT, 1 VIOLATION_CARD_MAX, 1 VIOLATION_RANGE) and
`data/a5-eval/` (977 queries: 855 covered / 122 control; strata pinned in the
manifest; generator RNG-free, byte-identical on re-run). Coverage of the
covered slice is **by construction** (queries authored against the extracted
records), so no m0b concept-coverage gate applies; code-corpus
representativeness of real codebases is exactly what this experiment does NOT
measure (§8).

Covered strata: callers-of 74, callees-of 73, where-defined 201, imports-of 9,
imported-by 2, contains 41, contained-in 201, instance-true 216,
instance-false-disjoint 38. Control strata: no-record 56 (callers 15,
callees 15, imports 6, imported-by 10, contains 10), unknown-entity 24,
unlicensed-unique 15 (where-defined on modules), out-of-scope-concept 6
(minted kernel concepts not in the code axiom layer), planted-conflict 5,
malformed/out-of-scope-op 16.

### 5.2 Scoring (pre-declared, identical shape to l3a §5.2)

- covered exact: `status=answer ∧ value=expected ∧ provenance⊆world-ids ∧
  license≠∅` (engine arm).
- control correct: `status=refuse ∧ code = expected ERR_* code` (STRICT).
- Arms: engine; abstain-all (refuses everything); answer-all (never refuses,
  fabricates deterministically from the same indexes). Neither trivial policy
  can satisfy the conjunctive primary (abstain-all: covered=0; answer-all:
  refusal=0). LLM/RAG arms are a successor (§7), NOT this record.

### 5.3 Endpoints, thresholds, kill (frozen in registry/experiments/a5.json)

- **Primary:** one-sided Wilson 95% LB of engine covered-exact rate > 0.98
  (n=855). **Co-gate (secondary):** Wilson LB of control correct-refusal rate
  > 0.95 (n=122). FAIL if either UPPER bound ≤ its threshold. PASS requires
  the instrument-validity gate (arm presence, pinned strata counts, store
  counts, all-3 planted violations detected, provenance validity,
  byte-identical repeat) — else INSTRUMENT-INVALID / INCONCLUSIVE.
- Kill criterion (HA5, clause-1 analog of HL3a): verbatim in the frozen
  record — engine/store/extraction-mapping indicted if either gate's upper
  bound is at or below threshold.
- Cost: descriptive only — mean µs/query reported; **no cost-ratio claim and
  no LLM-comparative claim of any kind is tested here** (successor `a5-llm`).

### 5.4 Assumptions block (every premise tagged; register entries appended)

- [STIPULATED: ASM-0007] the construct->concept mapping table (six code-v0
  structural-definition concepts + kernel part-of reuse), exact-hash identity.
- [STIPULATED: ASM-0008] expected answers generated from construction tables
  by the same author as the engine (independent code path, residual
  circularity); the cross-vendor audit is the check.
- [STIPULATED: ASM-0009] extraction is conservative static assertion;
  runtime-semantics soundness is not load-bearing (against-records scoring).
- [MEASURED: registry/verdicts/l3a.json] the underlying v0 engine passed its
  gold-parse gate (audit CONFIRMED), scope = that build + those corpora.
- [LIT-BACKED: arXiv:2505.12118; arXiv:2602.06671] motivation for the code
  vertical and for the world-layer (not input-injection) seat; motivates the
  rung, does NOT enter the verdict function, and is NOT re-measured here.

## 6. What a PASS means (and does not)

PASS = the kot-axiom/1 v0 engine, fed a deterministically-extracted code
world layer through the kot-query-code/1 desugaring, is an adequate
instrument: exact, provenance-carrying answers on its covered code-structure
slice and licensed refusals on everything else, deterministically, at ~µs/query
on shared CPU. It is an instrument-adequacy and fail-closed-semantics verdict
for the CODE VERTICAL of the L3 family — the world-layer population route
FK-L3-2(a) demonstrated end-to-end (extract -> stratum-4 records -> licensed
answers).

It does **not** show: that LLMs fail these queries (LIT-BACKED motivation,
arXiv:2505.12118, no LLM arm here — **no head-to-head win is claimed**), NL
robustness (no parser here), extraction soundness w.r.t. runtime semantics
(ASM-0009), representativeness of the 15-file corpus, any cost ratio, or any
scaling behaviour (R0 — no host model).

## 7. Successors (register separately, gated on this verdict)

1. `a5-llm` — LLM arms on the same slice (the arXiv:2505.12118-motivated
   head-to-head; only THAT record could license an engine-vs-LLM claim).
2. `a5-nl` — NL/mapper parse leg (natural-language code questions -> grammar).
3. Extraction scale-up: tree-sitter/multi-language, larger pinned snapshots;
   NSM-explicated code concepts per the idea-A sub-programme (ASM-0007 lapse).
4. Cross-audit: the a5 audit must re-derive a sample of expected answers
   independently from the snapshot sources (ASM-0008 revisit condition).

## 8. Registered scope statement

Everything measured here is a property of THIS engine build + desugaring
layer, THIS 5-record axiom set, THIS 889-record world layer extracted by THIS
extractor version from THIS pinned 15-file snapshot, and THIS 977-query
closed-grammar eval. It extrapolates to no other codebase or language, no NL
behaviour, no extraction-soundness claim, no LLM-comparative claim (absence
of an LLM arm is a design fact of this record), and licenses no statement
about kernel usefulness to any model. (The m0b lesson, applied prospectively.)
