# Design + pre-registration spec — L3a: the kot-axiom/1 v0 rules-engine oracle

**Status:** design record + the prereg anchor for registry experiment `l3a`
(HL3a **engine leg**, gold parse). Author: Kern (Fable agent, runner-2), 2026-07-09.
**Binding constraints:** `docs/kernel-design-directives.md` (§1 native formalism,
§3 method, §5 strata, §6 honest stats); `docs/next/architecture-ladder.md` §5.1
(the L3a rung, maintainer-green-lit as the first programme-2 experiment);
`docs/design-constraint-layer.md` §3.3 (the kot-axiom/1 grammar this engine
implements). Epistemic tags per `docs/next/assumption-register.md`.

## 0. What this experiment is — and is not

L3a's full hypothesis (HL3a, architecture-ladder.md §5.1) has three stages:
NL parse → engine → cost comparison against LLM/RAG arms. **This record
pre-registers and runs ONLY the middle stage** — the per-stage instrument the
ladder's stage-indictment rule (§8 item 14) requires: *engine-with-gold-parse*.
Queries are posed directly in the closed query grammar (`kot-query/1`, §4); no
NL, no mapper, no LLM, no RAG arm. The LLM/RAG cost-ratio and NL-parse legs
register under successor ids gated on this verdict (§7).

- PREMISE: the kernel today has no machine-checkable constraint form and no
  world layer; this build is their first implementation.
  [MEASURED: docs/design-constraint-layer.md §1.4 audit, verified on-disk 2026-07-08]
- PREMISE: the closed constraint inventory {functional, cardinality,
  disjointWith, inverseOf, domain, range} checks in linear-ish local passes
  (strict subset of SHACL-core minus recursion — engineering fact, semantics
  native). [LIT-BACKED: W3C SHACL REC 2017 validation locality; carried via
  design-constraint-layer.md §3.3]
- PREMISE: explicit-lookup architectures win on factual queries at matched
  compute, motivating the rung at all.
  [LIT-BACKED: Memory Layers at Scale, arXiv:2412.09764; kNN-LM,
  arXiv:1911.00172; carried via architecture-ladder.md §5]
- The maintainer's worked case is the first covered eval item (q0001):
  *who gave birth to Elvis* ⇒ giving-birth is attributive of `mother` ⇒
  `mother` is functional cardinality-1 ⇒ `unique(mother, forward,
  elvis-presley)` ⇒ `gladys-presley`, with provenance + axiom license.

## 1. The four strata, instantiated

| Stratum | Artifact | Where |
|---|---|---|
| 1–2 profile + definitions | minted concept URNs (kernel-v0, molecules-v0) | `data/kernel-v0/`, `data/molecules-v0/` (untouched) |
| 3 endorsed axiom sidecar | 6 `kot-axiom/1` records | `data/axioms-v0/` |
| 4 world layer | 598 `kot-world/1` records | `data/world-v0/` |
| — query boundary | closed grammar `kot-query/1` + engine | `tools/axiom/kot_axiom.py` |

Concept identity is untouched: sidecar and world records only *reference*
URNs (directives §5; design-constraint-layer.md §3.5 sidecar decision).

## 2. kot-world/1 (stratum-4 record shape, v0)

```json
{"schema":"kot-world/1","id":"w00001","kind":"class",
 "entity":"urn:kotw:v0:elvis-presley","concept":"urn:kot:<man>",
 "provenance":{"source":"public-fact-agent-recalled"}}
{"schema":"kot-world/1","id":"w00002","kind":"relation",
 "relation":"urn:kot:<mother>","subject":"urn:kotw:v0:elvis-presley",
 "object":"urn:kotw:v0:gladys-presley","provenance":{"source":"..."}}
```

Entities are `urn:kotw:v0:*` — a deliberately separate identifier space so no
world fact can leak into definitional content-hashes. Every record carries
`provenance.source` (fail-closed at load). Relation assertions use the
*relation-concept URN* with a stipulated direction reading (ASM-0004):
`mother(child, mother)` — i.e. forward = child→mother, matching the
maintainer's `mother(Elvis)=Gladys` functional reading.

## 3. The stratum-3 axiom set (data/axioms-v0/)

| Record | Subject concept | Constraints | Litmus family |
|---|---|---|---|
| rel-mother.json | molecules-v0 `mother` | `functional`; `range` woman | mother = functional cardinality-1 (the worked case) |
| rel-father.json | molecules-v0 `father` | `functional`; `range` man | |
| class-man.json | molecules-v0 `man` | `disjointWith` woman | sex disjointness |
| class-bookmark.json | kernel-v0 `bookmark` | `cardinality` {path maker-of, inverse, min 1, max 1} | bookmark/maker exact-1 |
| rel-maker-of.json | kernel-v0 `maker-of` | `range` bookmark | |
| rel-part-of.json | kernel-v0 `part-of` | `inverseOf` has-part | inverse pair |

Honesty notes. (i) The full two-parents litmus axiom ("a human has exactly two
parents…") is **not** in this v0 set: no `human`/`person` concept is minted
today, and stating it on a sex-specific class would be wrong — recorded as a
successor authoring task, not smuggled. [MEASURED: no human/person record in
data/kernel-v0/minted-urns.jsonl or data/molecules-v0/minted-urns.jsonl,
checked 2026-07-09] (ii) `subClassOf` is in the kot-axiom/1 grammar but
unimplemented in engine v0; the engine REFUSES any record carrying it
(ERR_AXIOM_UNIMPLEMENTED — fail-closed, never partially honoured). (iii) These
axiom sets are contestable world modelling and therefore sidecar-endorsed, not
identity (design-constraint-layer.md §3.4–3.5).

## 4. kot-query/1 — the closed query grammar and its licensing semantics

Four operators, all answered by deterministic index lookups (no search, no
similarity step anywhere — the X3 cosine ban is trivially honoured):

| Op | Form | Answer licensed by |
|---|---|---|
| `unique` | {op, rel, direction, subject} | a `functional` axiom (forward) or an unqualified `cardinality min≥1 max=1` axiom whose subject class the entity is asserted — **uniqueness is never assumed from data** |
| `lookup` | {op, rel, direction, subject} | rel present in the axiom layer; returns the asserted set (≥1); NO completeness claim — empty ⇒ refusal |
| `count` | {op, rel, direction, subject, qualifier?} | an exact-cardinality axiom (min=max) matching (path, direction, qualifier) on an asserted class of the subject; asserted count must equal the licensed exact ("a gloss file cannot count parents", operationalised) |
| `instance` | {op, entity, concept} | true: asserted class record; false: ONLY via a `disjointWith` axiom against an asserted class (CWA: absence is never falsity) |

**Pre-registered validation order** (each step fail-closed with a named code):
1. shape/op/URN well-formedness → `ERR_BAD_QUERY`
2. term in the endorsed axiom layer → `ERR_TERM_UNLICENSED`
3. entity known to the world layer → `ERR_UNKNOWN_ENTITY`
4. conflict scan: the query's (entity, term) pair — or any supporting edge's
   far end — implicated in a store-validation violation → `ERR_CONFLICT`
   (violations are surfaced, never resolved; architecture-ladder.md §5 risk 4)
5. op-specific license → `ERR_UNLICENSED_UNIQUE` / `ERR_UNLICENSED_COUNT`
6. records → `ERR_NO_RECORD` / `ERR_COUNT_MISMATCH` / answer

Every answer carries `provenance` (world-record ids) and `license` (axiom
constraint refs, `<file>#<index>`). Store validation runs at load: functional,
cardinality-max, disjointness, range/domain violations; min-cardinality
shortfalls are incompleteness (refusals), not conflicts. inverseOf pairs are
canonicalised at load (lexicographically smaller URN; querying the partner
flips direction), so cross-name inconsistency is impossible by construction.

## 5. The pre-registered eval (registry id `l3a`)

### 5.1 Corpus and query set (pinned)

`data/world-v0/` (598 records, 324 entities: Presley anchor + 30 synthetic
families + bookmarks/makers + part-of pairs + 6 planted violations) and
`data/l3a-eval/` (900 queries: 600 covered / 300 control; strata pinned in the
manifest; generator RNG-free). Coverage of the covered slice is **by
construction** (queries authored against the records), so no m0b concept-
coverage gate applies; fact-coverage of real domains is exactly what this
experiment does NOT measure (§8).

Control strata: out-of-scope relation (friend/teacher — minted concepts NOT in
the axiom layer) 60; unknown entity 40; licensed-but-no-record 60; unlicensed
unique 40; unlicensed count 30; planted-conflict 20; instance-no-license 20;
malformed 30.

### 5.2 Scoring (pre-declared)

- covered exact: `status=answer ∧ value=expected ∧ provenance⊆world-ids ∧
  license≠∅` (engine arm).
- control correct: `status=refuse ∧ code = expected ERR_* code` (STRICT).
- Arms: engine; abstain-all (refuses everything); answer-all (never refuses,
  fabricates deterministically from the same indexes). The two trivial
  policies are the pre-declared baselines: neither can satisfy the
  conjunctive primary (abstain-all: covered=0; answer-all: refusal=0).

### 5.3 Endpoints, thresholds, kill (frozen in registry/experiments/l3a.json)

- **Primary:** one-sided Wilson 95% LB of engine covered-exact rate > 0.98
  (n=600). **Co-gate (secondary):** Wilson LB of control correct-refusal rate
  > 0.95 (n=300). FAIL if either UPPER bound ≤ its threshold. PASS requires
  the instrument-validity gate (arm presence, pinned strata counts, store
  counts, all-6 planted violations detected, provenance validity,
  byte-identical repeat) — else INSTRUMENT-INVALID / INCONCLUSIVE.
- Kill criterion (HL3a clause 1, engine/store indictment): verbatim in the
  frozen record.
- Cost: descriptive only — mean µs/query reported; **the ≥10³× cost-ratio
  claim of HL3a is NOT tested here** (needs LLM arms; successor).

### 5.4 Assumptions block (every premise tagged; register entries appended)

- [STIPULATED: ASM-0004] relation-direction/alias readings of molecule/kernel
  concept URNs as relations (mother = child→mother functional, etc.).
- [STIPULATED: ASM-0005] Presley anchor facts are agent-recalled public facts;
  eval correctness is against-records, so external accuracy is not load-bearing.
- [STIPULATED: ASM-0006] expected answers generated from construction tables by
  the same author as the engine (independent code path, residual circularity);
  the cross-vendor audit is the check.
- [MEASURED: docs/design-constraint-layer.md §1.4] no prior machine-checkable
  constraint form existed.
- [LIT-BACKED: arXiv:2412.09764; arXiv:1911.00172] explicit-lookup motivation
  (motivates the rung; does not enter the verdict function).

## 6. What a PASS means (and does not)

PASS = the kot-axiom/1 v0 engine + four-strata store is an adequate instrument:
exact, provenance-carrying answers on its covered slice and licensed refusals
on everything else, deterministically, at ~µs/query on shared CPU. It is an
instrument-adequacy and fail-closed-semantics verdict — the gold-parse stage
gate for the L3 family, and the constraint-layer engineering the programme
owes independently (E9's constraint-violation arm consumes this engine).

It does **not** show: NL robustness (no parser here), real-world fact
coverage, any LLM-relative accuracy or cost ratio, or scaling behaviour
(R0 — no host model; scale-free formalism property, same envelope class as
HS2–HS8).

## 7. Successors (register separately, gated on this verdict)

1. `l3a-cost` — LLM (R1–R3) + RAG arms on the same slice; the HL3a cost-ratio
   and differentiator kills (Tier 1, Modal).
2. `l3a-parse` — mapper/NL leg (mapper-parse vs gold-parse loss fraction).
3. Axiom authoring: mint `person`/`has-parent`, state the full two-parents
   litmus axiom, extend world-v0; FK-L3-2 population-route measurement.
4. `subClassOf` closure + engine v1 per G6-successor demand data.

## 8. Registered scope statement

Everything measured here is a property of THIS engine build, THIS axiom set,
THIS 598-record world layer and THIS 900-query closed-grammar eval. It
extrapolates to no NL behaviour, no other corpus, no fact-coverage claim, and
no LLM-comparative claim. (The m0b lesson, applied prospectively.)
