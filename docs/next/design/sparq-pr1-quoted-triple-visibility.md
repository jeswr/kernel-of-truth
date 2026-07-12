# sparq Wave-1 PR-1 — quoted-triple VISIBILITY in `sparq-vectors`

**Status:** DESIGN + patch sketch. NOT applied; NO fork PR opened (coordinator holds the PR
pending maintainer decision #22.4). This document is the implementation-ready design record for
the first upstream step of the full-UFO kernel programme (KUFO/1 Wave 1).

**Parent:** scratchpad `arch-synthesis.md` §2 PR-bundle table, row PR-1; expressibility verdict
`docs/next/arch/ufo-rdf12-expressibility.md` [ARCHITECTURE-VERDICT: YES-WITH-EXTENSION].
**Grounded against:** actual sparq code at `/tmp/sparq-clone/crates/sparq-vectors/src/`
(read 2026-07-12; line pins below re-verified, one drifted).
**Epistemic posture:** every expected lift is [EXTRAPOLATION]. This PR makes an axis
*measurable*; it claims **no** accuracy improvement. CORRECTNESS and EFFICIENCY of the programme
theses remain INCONCLUSIVE-PENDING. Assumptions are emitted inline as PROPOSED-ASM-1520..1539
(NOT yet written to assumptions.jsonl — coordinator ratifies).

---

## 1. Problem statement (verified code-state pins)

The `kge`/`structure` measurement stack in `sparq-vectors` is **structurally blind to RDF 1.2
quoted-triple terms**, and the NL grounding path renders them as an **empty string**. Verified
sites (all [MEASURED] — line numbers re-checked against the clone):

| # | Pin | What the code does today |
|---|-----|--------------------------|
| P1 | `train.rs:353` `fn is_entity` | matches only `TermParts::Iri{..} \| Blank(_)`. Used by `collect_positives` (train.rs:374) ⇒ any triple with a quoted-triple endpoint is dropped from positives; triple terms get **no entity row**, no gradient. |
| P2 | `eval.rs:116` `fn is_entity` (same body) | used by `Splits::split` (eval.rs:193) and `restrict_to_train` (eval.rs:970) ⇒ quoted-term edges are in no split, no filter set, no ranking pool. (`restrict_to_train`'s else-branch *keeps* them as "structural context" text — but the trainer then re-drops them via P1.) |
| P3 | `structure.rs:422` `fn is_entity` (same body; **arch pin said :409 — drifted by 13 lines**, :409 is `type_term()`) | used by `NegativeSampler::new` (structure.rs:319) ⇒ quoted terms never enter the corruption pool. |
| P4 | `grounding.rs:793` in `render_object` | `TermParts::Triple(_) => (String::new(), false)` — a grounded fact whose object is a quoted triple verbalises as the **empty string**. Silent data loss in every NL-string / subgraph-text grounding over RDF 1.2 data. A defect, not a behaviour. |
| P5 | `rewrite.rs:650` `term_to_ground` | maps `Term::Triple` (and blank nodes) to `None` ⇒ a `vec:` k-NN neighbour that is a triple term is silently dropped from the VALUES rows. |
| P6 | `eval.rs:301` `AblationCell::gufo_prior` | the dormant prior axis (hard-wired `false`) — the precedent this PR's flag wiring mirrors. |
| P7 | dict/core support exists | `sparq-core` interns triple terms content-addressed by component ids (`dict.rs` `Stored::Triple`), reconstructs nested terms with a depth cap, and the N-Triples/Turtle paths parse `<<( s p o )>>` + `rdf:reifies` (fingerprint.rs test :525-531 exercises exactly this). The blindness is **local to sparq-vectors**, not the engine. |

Consequence for the programme: UFO-KGE-1's "quoted-term visibility" arm cannot be run at all
until P1–P3 are widened, and any NL-grounding evidence over RDF 1.2 data is corrupted by P4.

---

## 2. Design invariants

- **I1 — Byte-stable baselines.** With the ablation flag OFF (the default, and the only default
  any existing constructor produces), every byte of trainer/eval behaviour is identical to
  pre-PR: same positives, same row assignment, same PRNG consumption, same splits, same
  metrics. OFF must reduce *structurally* (same match arms), not just numerically. Proof
  obligations in §7.
- **I2 — Attribution hygiene.** The flag changes only what the **trainer sees** (rows +
  positives + corruption pool). The eval **ranking pool and split membership stay
  scope-invariant**, so ON-vs-OFF paired deltas isolate the visibility effect rather than a
  changed query population (the CK-UFO representation-matched-null lesson, applied here).
- **I3 — Repo conventions preserved.** Opt-in features only (`structure`/`kge`, off by
  default); zero new dependencies; default build untouched; no benchmark numbers in committed
  code or docs; adoption of the prior is measurement-gated, never claimed (mirrors the
  `SamplingMode` / `WeightMode` precedents verbatim).
- **I4 — Bugfix vs ablation separation.** P4 (empty-string verbalisation) is a defect fix and
  ships **unflagged**; the visibility widening (P1–P3) is an ablation axis and ships
  **flagged-off**. The PR description calls both out separately.

---

## 3. The changes (patch sketch — NOT applied)

### 3.1 `structure.rs` — `TermScope` + `is_embeddable` (the b1 widening)

One definition, consumed by train/eval/sampler (they already depend on `crate::structure`
under the `kge` feature; the triplicated `is_entity` had no load-bearing rationale, unlike the
deliberately-local `splitmix64` copies):

```rust
/// Which term sorts participate in KGE entity space — the quoted-terms ablation switch.
/// `IriBlank` is the pre-existing behaviour and the DEFAULT: byte-identical baselines.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub enum TermScope {
    /// Named + blank nodes only (the ablation OFF baseline; reduces exactly to the old
    /// `is_entity` matcher).
    #[default]
    IriBlank,
    /// Also RDF 1.2 quoted-triple terms (`TermParts::Triple`) — the ablation ON arm.
    /// Literals stay out under both scopes.
    Embeddable,
}

/// Widened `is_entity`. Under `IriBlank` this is the identical match the three former
/// private `is_entity` copies performed — the structural byte-stability guarantee.
pub(crate) fn is_embeddable(graph: &Graph, id: Id, scope: TermScope) -> bool {
    match graph.dict.term_parts(id) {
        TermParts::Iri { .. } | TermParts::Blank(_) => true,
        TermParts::Triple(_) => scope == TermScope::Embeddable,
        _ => false,
    }
}
```

The three `is_entity` copies (P1–P3) are deleted; call sites take a `TermScope`.

### 3.2 `structure.rs` — `NegativeSampler`: scoped pools + sort-preserving corruption (b3)

```rust
pub struct NegativeSampler<'a> {
    constraints: &'a TypeConstraints,
    /// Atomic (IRI/blank) corruption pool — meaning unchanged.
    entities: Vec<Id>,
    /// Quoted-term pool — ALWAYS empty under `TermScope::IriBlank`.
    triple_terms: Vec<Id>,
    positives: FxHashSet<[Id; 3]>,
    mode: SamplingMode,
    scope: TermScope,
}

impl<'a> NegativeSampler<'a> {
    /// Existing signature preserved — delegates with the byte-stable default.
    pub fn new(graph, constraints, mode) -> Self {
        Self::new_scoped(graph, constraints, mode, TermScope::IriBlank)
    }
    pub fn new_scoped(graph, constraints, mode, scope) -> Self { /* pool build uses
        is_embeddable(graph, id, scope); ids landing in `triple_terms` iff
        TermParts::Triple; both pools sorted ascending as today */ }
}
```

**Position/sort-aware corruption** (the b3 item): in `sample`, the candidate pool is chosen by
the *sort of the term being replaced* — a quoted-term slot draws only from `triple_terms`, an
atomic slot only from `entities`. Rationale: replacing a quoted-triple object with an atomic
IRI yields a sort-trivial negative the model detects from term class alone, which pollutes the
training margin (standard type-of-negative hygiene, same spirit as Krompass type-constrained
negatives). Under `IriBlank` no positive can contain a triple term and `triple_terms` is empty,
so the draw loop, PRNG stream, and rejection sequence are **bit-identical** to today.
Type-constraint admissibility: quoted terms carry no `rdf:type`, so under `TypeConstrained`
mode a constrained side would reject them all; the quoted-term pool therefore **bypasses the
class filter** (statements have no class discipline until the PR-2 UFO prior reader exists —
documented in-code; PROPOSED-ASM-1526).

### 3.3 `train.rs` — `TrainConfig.term_scope` + scoped positive collection

```rust
pub struct TrainConfig {
    // ... existing fields ...
    /// Quoted-terms ablation switch (TermScope::IriBlank = byte-stable baseline).
    pub term_scope: TermScope,
}
// TrainConfig::small / small_with_model set term_scope: TermScope::default()  // IriBlank
```

- `collect_positives(graph, scope)` uses `is_embeddable(graph, id, scope)` for both endpoints.
  Under `Embeddable`, `(<reifier IRI>, rdf:reifies, <<(s p o)>>)` triples become positives and
  quoted terms get dense rows (id-sorted, as today).
- `train()` builds the sampler via `NegativeSampler::new_scoped(graph, constraints,
  config.sampling, config.term_scope)`.
- Nothing else in the SGD loop changes; the flag lives entirely in what is collected/sampled.

### 3.4 `eval.rs` — deliberately NOT widened at the split/pool level, plus a paired runner

**Design refinement over the arch sketch** (decision D1, §8): the arch row named `eval.rs:116`
as a widening site, but the deeper read shows `Splits` should stay **atomic by design**:

- Target relations are ordinary IRI–IRI edges under both scopes (a `rdf:reifies` triple never
  passes the both-endpoints check atomically — object is a quoted term — so splits are
  unchanged whether or not the flag exists).
- The **ranking pool stays atomic** in both arms, so filtered ranks are computed over the same
  candidate set and the paired ON−OFF delta isolates training-side visibility (invariant I2).
  Widening the pool would add quoted-term distractors to one arm's rankings — an incomparable
  measurement.

So `eval.rs:116` keeps its (now shared) `IriBlank` behaviour; the eval-side changes are:

1. `AblationCell` gains `pub quoted_terms: bool` (hard `false` in `run_ablation`, mirroring
   the dormant `gufo_prior` axis P6 — same wiring pattern, same honesty comment).
2. A **paired ON/OFF runner** mirroring `run_weight_ablation` (eval.rs:860) exactly:

```rust
pub struct QuotedAblation {
    pub off: CellStats,      // TermScope::IriBlank arm, aggregated over seeds
    pub on: CellStats,       // TermScope::Embeddable arm
    pub mrr: PairedDelta,    // per-seed MRR(on) − MRR(off), variance-reduced
    pub hits10: PairedDelta,
}
pub fn run_quoted_ablation(text, format, template: EvalConfig, seeds: &[u64])
    -> Result<QuotedAblation, String>
```

Per seed: one shared closure + `Splits` + `restrict_to_train` graph + `TypeConstraints`
(common random numbers, both arms); the arms differ ONLY in `tcfg.term_scope`. On a
quote-free graph the two arms are **byte-identical and the delta is exactly zero** — the
honest no-op, same property `run_weight_ablation` documents for provenance-free graphs, and
itself a byte-stability proof (§7, T-B).

Note (dilution, not bias): reifier-metadata IRI–IRI edges (e.g. `ex:assertedBy`) enter the
split as targets in **both** arms identically; they dilute the overall MRR but cannot bias the
paired delta. A per-relation metrics breakdown is deliberately out of PR-1 scope (kept small).

### 3.5 `grounding.rs:793` — the empty-string verbalisation bugfix (unflagged)

```rust
// BEFORE (the bug): a quoted-triple object verbalises as the empty string.
TermParts::Triple(_) => (String::new(), false),

// AFTER: reconstruct via the dict (handles nesting + inline children, depth-capped in
// sparq-core) and render in RDF 1.2 triple-term syntax.
TermParts::Triple(_) => (graph.dict.term(id).to_string(), false),
```

`Dict::term` already reconstructs nested `Term::Triple` values (dict.rs `reconstruct_triple`,
depth-capped), and oxrdf's `Display` renders the term syntax; if the vendored oxrdf `Display`
output is not the `<<( s p o )>>` form we want in NL text, fall back to a 6-line local
recursive formatter over `TermParts` with the same depth cap (verify at implementation —
PROPOSED-ASM-1536). Ships **unflagged** per invariant I4: the empty string is silent data
loss, not a contract; the KGE byte-stability surface (train/eval) never calls `render_object`.
Called out as its own commit + PR-description bullet.

### 3.6 `eval.rs` — the `synthetic_rdf12` slice

A generator mirroring the existing `synthetic_*_ttl` family (deterministic in `seed`, sized,
honest-by-construction, emitted as **N-Triples** because that path's RDF 1.2 quoted-term
support is already exercised by fingerprint.rs :525):

```rust
pub struct Rdf12Parts {
    /// IRI-only community-structured base graph (valid slice on its own).
    pub base: String,
    /// ONLY `stmtJ rdf:reifies <<( h p t )>>` lines — every triple has a quoted-term
    /// endpoint, i.e. INVISIBLE under TermScope::IriBlank (the byte-identity fixture).
    pub reifications: String,
    /// Reifier metadata: `stmtJ a ex:Statement ; ex:assertedBy ex:srcK` (IRI–IRI).
    pub metadata: String,
}
pub fn synthetic_rdf12_parts(n_entities: usize, seed: u64) -> Rdf12Parts;
pub fn synthetic_rdf12_ttl(n_entities: usize, seed: u64) -> String; // base+reifications+metadata
```

**Signal mechanism (stated honestly).** A shallow KGE treats a quoted term as an *opaque
node* — PR-1 buys structural visibility only, NOT compositional access to (s,p,o) content
(that is PR-4's b2 statement encoder, gated on the UFO-KGE-1 GO). What visibility adds is
real graph structure: sparq-core content-addresses triple terms, so two reifiers of the same
claim share one quoted-term node, and `src ←assertedBy− stmt −reifies→ tt ←reifies− stmt′
−assertedBy→ src′` paths connect sources through shared-claim hubs. The slice therefore:

- builds community-clustered base entities and claims (as `synthetic_relational_ttl` does);
- has sources assert overlapping claim sets within communities (multiple reifiers per quoted
  term — the hub structure), plus noise reifications and decoy sources with
  overlapping-but-uncorroborated claims (non-triviality guard, mirroring
  `gufo_slice_is_not_trivially_separable`);
- pre-registers the endpoint as filtered MRR/Hits@k on an ordinary IRI–IRI relation
  (`ex:corroborates`, src–src) that is *identically split in both arms* — the paired ON−OFF
  delta is the visibility effect.

Whether the hub structure lifts anything is exactly what UFO-KGE-1 measures
[EXTRAPOLATION — no lift promised; a standing synthetic-slice scope rider applies: a
schema-bearing synthetic win does not extrapolate to other corpora].

### 3.7 `rewrite.rs:650` — `vec:` VALUES triple-term bindings (secondary, conditional)

`term_to_ground` currently drops triple-term neighbours from VALUES rows. If the vendored
spargebra `GroundTerm` exposes a triple variant (RDF 1.2 / rdf-star feature — verify at
implementation), map it through; a quoted term with a stored vector is then a legal `vec:`
neighbour. If the variant is absent, this stays a **documented limitation** (doc-comment +
a counting `log`-style note), out of PR-1's behavioural scope. Either way blank-node drops are
untouched. Band S; PROPOSED-ASM-1531.

---

## 4. What PR-1 explicitly does NOT do

- No compositional statement encoder (learned or deterministic) — PR-4, gated on GO.
- No UFO prior reader / derived-disjointness mask — PR-2.
- No opacity-conformance tests in `sparq-reason` — PR-3 (but see T-9: PR-1 asserts closure
  *non-crash/non-interference* over quoted terms at the harness level as a smoke guard).
- No engine work (destructuring/construction, situation indexing) — PR-5, L-band, gated.
- No accuracy claim, no committed numbers, no adoption of the prior.

---

## 5. Tests to add

| ID | Where | Asserts |
|----|-------|---------|
| T-1 | structure.rs | `is_embeddable` scope matrix: IRI/blank true under both scopes; `Triple` true only under `Embeddable`; literals false under both. |
| T-2 | eval.rs (**load-bearing byte-identity**) | `run_ablation(base)` vs `run_ablation(base + reifications)` (from `synthetic_rdf12_parts`; appendix appended AFTER base so base dict ids are stable) under default scope: identical `Splits` (same `[Id;3]` vectors), **bit-equal** `entity_emb`/`rel_emb`/`epoch_loss`, equal `Metrics`. Proves invisible-stays-invisible. |
| T-3 | eval.rs | `run_quoted_ablation` on a **quote-free** graph: ON and OFF arms bit-equal, `mrr.mean == 0.0` exactly (the honest no-op, mirrors the weight-ablation property). |
| T-4 | train.rs | Under `Embeddable` on the rdf12 slice: quoted terms have entity rows; `rdf:reifies` positives counted; determinism (two runs bit-equal); loss decreases. |
| T-5 | structure.rs | Sort preservation: corrupting a quoted-term slot never emits an atomic entity and vice versa; sampler deterministic per (seed, scope); `new` (unscoped) still bit-reproduces pre-PR draws on a quoted-term-bearing graph. |
| T-6 | eval.rs | Split scope-invariance on the rdf12 slice: `Splits::split` output identical whether the graph carries reifications or not was covered by T-2; additionally ranking-pool atomicity — no quoted term in `splits.entities`. |
| T-7 | grounding.rs | `render_object` on a quoted-triple object returns non-empty `<<( … )>>`-shaped text; nested term depth-capped; a subgraph grounding over an RDF 1.2 fixture contains **no empty-object fact** (regression for P4). |
| T-8 | eval.rs | `synthetic_rdf12_parts` slice properties: deterministic in seed; ≥N reified statements with ≥2 reifiers sharing a quoted term (hub exists); decoy-source fraction ≥15% (non-separability guard); every `reifications` line has a quoted-term endpoint (T-2's precondition, asserted). |
| T-9 | eval.rs | RDFS closure over the rdf12 slice: `close_for_vectorise` succeeds, does not destructure or multiply quoted terms (entailed-triple count unaffected by the reification appendix) — the PR-3 non-interference smoke guard. |
| T-10 | rewrite.rs (conditional) | If `GroundTerm` supports triple terms: a triple-term neighbour survives into VALUES; else: doc-tested drop count. |
| T-11 | eval.rs | Presets audit: `TrainConfig::small*`, `EvalConfig::small` produce `TermScope::IriBlank`; `run_ablation` cells all report `quoted_terms == false`. |

---

## 6. Draft PR description (for the fork, when #22.4 clears)

> **Title:** vectors: RDF 1.2 quoted-triple visibility as an off-by-default ablation axis; fix
> empty-string verbalisation of quoted triples
>
> **What.** Three changes to the opt-in `structure`/`kge` measurement stack (default build
> untouched, zero new deps):
> 1. **Bugfix (unflagged):** `grounding::render_object` rendered a quoted-triple object as the
>    empty string, silently corrupting NL groundings over RDF 1.2 data. It now renders the
>    reconstructed `<<( s p o )>>` term (depth-capped via the existing dict reconstruction).
> 2. **`TermScope` ablation axis (default OFF, byte-stable):** the trainer/eval/sampler's
>    private `is_entity` copies excluded `TermParts::Triple`, so statement-level structure
>    (`rdf:reifies` edges, shared quoted-term nodes) was invisible to the embedding layer.
>    A single `is_embeddable(graph, id, scope)` replaces them; `TermScope::IriBlank` (the
>    default everywhere) reduces to the identical match — baselines are byte-identical, which
>    the new tests assert bit-for-bit. `TermScope::Embeddable` admits quoted terms to entity
>    space with sort-preserving negative corruption. Split membership and ranking pools stay
>    atomic under BOTH scopes, so paired ON/OFF deltas isolate the training-side effect.
> 3. **Measurement plumbing:** a `synthetic_rdf12` slice (deterministic, non-trivially
>    separable, honesty-guarded like the existing gUFO/relational slices) and
>    `run_quoted_ablation` (paired per-seed ON−OFF deltas, mirroring `run_weight_ablation`;
>    exact-zero delta on quote-free graphs).
>
> **Why (context).** This comes out of the Kern (Kernel-of-Truth) research programme, which is
> evaluating whether UFO-style ontological discipline — including statements-about-statements
> held without assertion — earns measurable lift in KGE link prediction on this stack. RDF 1.2
> reification is the data shape; today the vectors crate structurally cannot see it, so the
> question cannot even be asked. This PR follows the crate's own convention for such axes
> (`SamplingMode`, `WeightMode`, the dormant `gufo_prior` field): ship the switch OFF, adopt
> nothing without a measured, multi-seed, paired-delta result on the asymmetric model. **No
> benchmark numbers are included and no accuracy claim is made.**
>
> **Baseline safety.** `TermScope` defaults to the old behaviour in every constructor; the PR
> adds bit-equality regression tests (model bytes, splits, metrics) for (a) quoted-term-bearing
> graphs under the default scope and (b) the ON arm on quote-free graphs. Reviewer can also
> re-run the pinned-seed model-hash example (below) on the merge-base and this head — the
> hashes must match.
>
> *Review-timing footer per standing practice: no urgency; happy to split the bugfix into its
> own PR if preferred.*

---

## 7. Proving baseline byte-stability

Three independent layers:

1. **Structural argument (in-code):** `TermScope::IriBlank` reduces `is_embeddable` to the
   exact former match arms; every public constructor/preset defaults to it; the sampler's
   quoted pool is empty under it so PRNG draw sequences are unchanged; `Splits` is untouched.
   No float path, PRNG constant, or iteration order is modified when OFF.
2. **In-tree regression tests (single build):** T-2 (invisible additions change nothing,
   bit-equal model bytes) and T-3 (ON == OFF on quote-free graphs, exact-zero paired delta).
   These two bracket the change from both directions.
3. **Cross-commit hash pin (review procedure):** add `examples/kge_pin.rs` printing a SHA-256
   over the canonical little-endian bytes of `(epoch_loss, entity_emb, rel_emb,
   metrics-as-f64s)` for the three existing synthetic slices (gufo, relational, provenance —
   all quote-free) at pinned seeds `{1,2,3}`. Procedure: same box, same pinned toolchain;
   run on the merge-base commit and the PR head; `diff` of outputs must be empty; paste both
   hash blocks into the PR. (Float determinism across identical builds is already a crate
   invariant — `is_deterministic_for_fixed_config` et al.) Also `cargo test -p sparq-vectors
   --all-features` green on both commits.
   Audit checklist for the reviewer: `grep -n "fn is_entity" crates/sparq-vectors/src` returns
   nothing; every `is_embeddable` call site threads an explicit scope; `TermScope::Embeddable`
   is constructed only in `run_quoted_ablation` and tests.

---

## 8. Open decisions (for coordinator/maintainer)

- **D1 — eval pool scope (refines the arch row).** This design holds `Splits`/ranking pool
  atomic under both scopes (invariant I2) instead of widening `eval.rs:116` as the arch table
  sketched. Alternative (widen pool under ON) rejected: incomparable filtered ranks across
  arms. Recommend: adopt as designed.
- **D2 — one shared `is_embeddable` vs three parallel copies.** The crate deliberately
  duplicates `splitmix64`, but the `is_entity` triplication carries no such comment; train/eval
  already import from `crate::structure`. Recommend: single `pub(crate)` fn; fall back to three
  scoped copies only if the maintainer objects.
- **D3 — bugfix flagging.** Recommend unflagged (I4); offer the split-PR option in the footer.
- **D4 — `rdf:reifies` classification.** Not added to the `SCHEMA_PREDICATES` const (would be
  the one flag-off-visible change on malformed `rdf:reifies`-with-IRI-object data). Its triples
  are excluded from targets structurally (quoted-term object) under both scopes; revisit only
  if PR-2 needs it.

---

## 9. Effort bands

(S ≈ ≤1 agent-day, M ≈ 2–5 agent-days; assumes a dev already inside the crate — cold ×1.5–2.)

| Work item | Band |
|---|---|
| §3.1–3.3 `TermScope` + `is_embeddable` + sampler pools + `TrainConfig` wiring | **S** |
| §3.5 grounding verbalisation bugfix + T-7 | **S** (hours) |
| §3.4 + §3.6 `run_quoted_ablation` + `synthetic_rdf12_parts` + T-2/T-3/T-8/T-9 | **S–M** (1–2 days; the slice's honesty guards are the slow part) |
| §3.7 `vec:` VALUES triple terms (conditional on spargebra) | **S** |
| §7.3 cross-commit hash-pin example + both-commit run | **S** (hours) |
| **PR-1 total** | **≈ 2–4 agent-days** (matches the arch table's S + S–M band) |

---

## 10. PROPOSED-ASM-1520..1539 (emitted here only; NOT written to assumptions.jsonl)

| ASM | Statement | Basis / verify-when |
|---|---|---|
| PROPOSED-ASM-1520 | Code pins P1–P7 hold at the read clone; `structure.rs` `is_entity` is at :422, not :409 (arch pin drifted). Re-pin against the fork's merge-base before patching. | [MEASURED 2026-07-12] |
| PROPOSED-ASM-1521 | sparq-core parses RDF 1.2 quoted terms on both N-Triples and Turtle paths (NT proven by fingerprint.rs test; Turtle indicated by ttl/tests.rs `reifies` hits). Generator emits NT to stay on the proven path. | verify Turtle at implementation |
| PROPOSED-ASM-1522 | `Dict::term` reconstructs nested triple terms depth-capped; `TermParts::Triple([Id;3])` carries component ids — sufficient for both the verbalisation fix and any future destructuring. | [MEASURED: dict.rs] |
| PROPOSED-ASM-1523 | Byte-stability when OFF is structural: `IriBlank` reduces to the exact former matcher; no PRNG/float/iteration-order path changes. | design invariant I1; T-2/T-3 |
| PROPOSED-ASM-1524 | Appending statements to a serialisation leaves earlier terms' dict ids unchanged (parse-order interning) — the T-2 fixture's load-bearing premise. | verify with an id-stability assert inside T-2 |
| PROPOSED-ASM-1525 | Today, every triple with a quoted-term endpoint is excluded from positives, splits, filter set, and both pools (P1–P3 composition). | [MEASURED: code read §1] |
| PROPOSED-ASM-1526 | Sort-preserving corruption is the correct default for the ON arm and needs no separate flag in PR-1; quoted-term corruptions bypass the class filter (no statement typing exists until PR-2). | design choice; revisit at PR-2 |
| PROPOSED-ASM-1527 | Holding the ranking pool atomic in both arms is required for a comparable paired delta (I2). | design invariant; D1 |
| PROPOSED-ASM-1528 | Adding a field to `TrainConfig`/`AblationCell` (breaking struct literals) is acceptable for this research-grade opt-in crate; in-tree callers updated in-PR. | maintainer may prefer `Default` impls |
| PROPOSED-ASM-1529 | The empty-string verbalisation is a defect no consumer pins; the fix may ship unflagged (I4). | offer split-PR fallback (D3) |
| PROPOSED-ASM-1530 | `SCHEMA_PREDICATES` stays untouched; `rdf:reifies` needs no schema classification in PR-1 (structural exclusion suffices) (D4). | [MEASURED: split logic] |
| PROPOSED-ASM-1531 | The vendored spargebra `GroundTerm` may or may not expose a triple variant; §3.7 is conditional on it. | verify at implementation |
| PROPOSED-ASM-1532 | The rdf12 slice's hub mechanism (content-addressed shared quoted terms) is the only PR-1-visible signal path; compositional content stays opaque until PR-4. Synthetic-slice scope rider applies: no extrapolation off-corpus. | [EXTRAPOLATION posture] |
| PROPOSED-ASM-1533 | `sparq_reason::materialize` neither crashes on nor destructures quoted terms (closure non-interference). Smoke-guarded by T-9; semantics pinned properly in PR-3. | verify via T-9 |
| PROPOSED-ASM-1534 | PR posture: staged on the fork as a consolidated draft with the review-timing footer, ONLY after maintainer decision #22.4; nothing in this design opens a PR. | standing practice |
| PROPOSED-ASM-1535 | `run_weight_ablation`/`PairedDelta` is the accepted paired-harness precedent; `run_quoted_ablation` mirrors it exactly (incl. the exact-zero no-op property). | [MEASURED: eval.rs:860] |
| PROPOSED-ASM-1536 | oxrdf `Display` for `Term::Triple` renders acceptable term syntax for NL groundings; else a 6-line local formatter (depth-capped) replaces it. | verify at implementation |
| PROPOSED-ASM-1537 | Effort bands assume warm familiarity; ×1.5–2 cold. | estimate |
| PROPOSED-ASM-1538 | Cross-commit hash-pin proof requires the same box + pinned toolchain; per-build float determinism already crate-tested. | [MEASURED: determinism tests] |
| PROPOSED-ASM-1539 | PR-1 is necessary-not-sufficient for UFO-KGE-1; a completed PR-1 licenses running the visibility arm and nothing else — no thesis movement (CORRECTNESS/EFFICIENCY stay INCONCLUSIVE-PENDING). | programme posture |
