# SCALE-1 — Realistic Large-Kernel + Large-World Experiment Track

**Status:** strategic experiment design only.  
**Relationship to existing work:** additive to `rules-1-b`, `g2-import-v2`, DDC and RULES-2; it does not modify, delay, reinterpret or replace them.  
**Scope:** a staged kernel containing at least one million genuinely type-level concepts, a world containing tens to hundreds of millions of kernel-addressed facts, deterministic vectorisation, RULES-1-compatible inference, and the complete CK-UFO representational schema with a bounded UFO-SN3 executable projection.  
**Conclusion discipline:** this document makes **no feasibility conclusion** about CORRECTNESS or EFFICIENCY.

Epistemic tags:

- **[MEASURED]** — directly supported by repository artifacts or a stated local diagnostic.
- **[LIT-BACKED]** — supported by an official specification, source or programme page.
- **[DERIVED]** — arithmetic or direct consequence of measured facts.
- **[STIPULATED]** — proposed architecture, threshold, arm or sequencing decision.
- **[EXTRAPOLATION]** — cost or performance expectation to be measured; never a premise.
- **[OPEN]** — deliberately unresolved.

---

## 0. Governing question and non-negotiable scale standard

The track asks:

> Do the correctness or efficiency mechanisms already under investigation change when the kernel is large enough to cover a realistic long tail, the world is large enough to make retrieval and closure non-trivial, and the system must distinguish full UFO category, identity, modal, dependence, relator and event structure?

The scale hypothesis is neutral:

- **[STIPULATED]** Some gaps may be scale artifacts: coverage `0.3542`, natural-input reach, broad-workload competitiveness, DDC’s approximately 119-concept calibration set, and the small CLUTRR/world-v0 closure.
- **[STIPULATED]** Other gaps may worsen at scale: alignment quality, hard-typing errors, vector interference, closure blow-up, retrieval failures and lifecycle cost.
- **[STIPULATED]** The experiment must be capable of detecting either pattern.

A scale result is not licensed merely because a database contains millions of rows. A thesis-grade “million-concept” stage requires all of the following:

1. At least **1,000,000 deduplicated type-level concept clusters**, not named individuals and not duplicated source records.
2. Every counted concept has a content-addressed structural record, provenance, semantic-status field and full CK-UFO sidecar schema.
3. At least its broad ontic category is assigned with evidence; unresolved rigidity, identity or dependence fields remain explicitly `underdetermined`.
4. At least **10 million asserted world/TBox facts**, with a target of 100 million at the 1M stage.
5. Natural-input and structured-input benchmark legs.
6. Nested 10k, 100k and 1M stores selected without benchmark-label access.
7. At least 30% of the headline evaluation items must be **tail-exposed**: their licensed retrieval or proof must touch a concept absent from the 100k store.
8. The large store must be causally active in an experiment arm. Merely building or vectorising it is not enough.
9. Flat retrieval, shuffled mappings, shuffled rules and smaller nested kernels remain available as controls.
10. Build, update, closure, retrieval, model and human-review costs are reported separately.

Named entities belong in the world ABox. They do not count toward the million-concept headline. Taxa may count as biological Kinds, but a second “domain-balanced” count must exclude domination by a single taxonomy.

---

## 1. Starting point in the repository

### 1.1 Current semantic and ontology inventory

| Asset | Actual local scale | What it contributes | Current limitation |
|---|---:|---|---|
| Profile-1 encoder | 65 primes; 31 slots; 129 fillers | Deterministic explication encoding | Closed grammar; not a bulk-ontology encoder |
| kernel-v0 + molecules-v0 | approximately 108 authored records | High-assurance meaning anchors | Too small for broad coverage |
| WordNet 3.1 | **117,791 synsets; 269,960 axioms** | Broad lexical taxonomy and sense inventory | `AxiomsOnly`; no argument typing or NSM explications |
| OBO import | **96,192 records; 24,578 genus–differentia definitions** | Formal biology/anatomy/disease definitions | Current selection is under 100k; domain-skewed |
| SUMO | **3,705 terms; 15,595 KIF axioms** | Upper/mid ontology, typed relations and FOL content | SUMO↔WordNet mapping not loaded; most KIF exceeds current Horn profile |
| FrameNet | **1,221 frames; 2,070 relations; 11,428 frame elements** | Event/relationship valency scaffold | Not a definition or demonstrated selectional-restriction layer |
| world-v0 | **598 assertions over 324 entities** | Persistent world-layer fixture | Tiny and mostly synthetic |
| CLUTRR world | **5,090 facts** | Third-party relational task | Gold-parsed, closed kinship domain |
| RULES-1 certificate | 3,680 entailed cells; 1,207 SPARQ/twin cases | Proof-carrying non-stated closure | No large-world or natural-input result |

**[MEASURED]** The local WordNet bridge already places 39.49% of its synsets within five taxonomy hops of approximately 100 hand-authored anchors. That is useful proximity, not possession of an endorsed explication.

**[MEASURED]** OBO’s reference graph already contains non-trivial cycles, including an SCC of 1,142 terms. The current explication encoder’s DAG-only `encodeConceptSet` therefore cannot simply be run over the imported ontology.

### 1.2 Current vector construction

Construction B provides:

- exact Sylvester–Hadamard role/filler binding inside clauses — an atomic `(slot, filler)` filler costs one O(D) vector add with exactly-zero sibling crosstalk (measured `<1e-15` at `D=8192`; `encoder/src/codebook.ts:1-42`), no FFT;
- a 5-bit slot field (exactly 31 slots, saturated) and 8-bit filler field (129 of 255 IDs used);
- a hard minimum dimension of `D = 8192` (`MIN_D = 1<<13`; `D<8192` fails closed with `ERR_DIMENSION_TOO_SMALL`), because the exact level needs 5+8=13 index bits;
- whitened unitary circular convolution across structure, where **each structured (convolution-bound) child costs exactly two length-D FFTs** (`spread → fftReal → spectrumMultiply → ifftToReal`; `encoder/src/encoder.ts:114-118`), at O(D log₂D) with log₂8192 = 13;
- deterministic signed permutations and a fixed traversal order (SHA-256-seeded per label; `alphaStruct=1.0`, `notBoost=1.0` weights pinned by content hash);
- recursive concept references over a DAG (a reference binds the referenced concept's own canonical vector; cycles fail closed with `ERR_CYCLIC_CONCEPT_REF`);
- byte-identical Float64 output for a fixed AST and encoder pin (`ALGORITHM_VERSION='kot-enc-B/1'`).

**[MEASURED: encoder source, 2026-07-12]** The exact atoms are **not** hash-seeded — they are deterministic Hadamard rows by index (`popcount32`); SHA-256 seeds only the *structure* (tag spectra, permutations, whitener). There is therefore **no new-atom seeding collision from scaling**: concept count grows the number of records, not the atom codebook. A separate quasi-orthogonal encoder `kot-enc-Bq/1` (`encoderQ.ts`) does exist for `D ∈ {512, 576}` with SHA-256-seeded Rademacher `±1/√D` atoms (crosstalk floor `~1/√D`, exact unbinding lost); it is the projection/adapter path, not the canonical exact codebook.

The exact codebook covers at most 31 named slots and 129 named fillers. Arbitrary OBO, Wikidata, SUMO or FrameNet properties cannot be added without a new vectoriser/version.

A read-only local diagnostic using the shipped `encoder/dist` measured approximately:

- 758 shallow two-clause encodings/second;
- 102 depth-2, four-clause encodings/second;

on one CPU process. **[MEASURED, LOCAL DIAGNOSTIC; no persistent result artifact]** This suggests that ordinary explication encoding is not itself the dominant million-scale cost. Dense storage, graph-derived vectorisation, indexing and closure are larger risks.

---

## 2. Target architecture

### 2.1 Four separately versioned objects

**[STIPULATED]** Scale must not collapse meaning, ontology, world facts and vectors into one record.

1. **Concept record**

   Content-addressed source structure: source identifier, source version, semantic status and identity-bearing axioms.

2. **UFO bridge record**

   Separately content-addressed CK-UFO classification and warrant. It may evolve without silently re-minting the source concept.

3. **World assertion**

   An assertion over concept and entity identifiers, with source statement, world/situation, rank, qualifiers and provenance.

4. **Vector annotation**

   Keyed by:

   ```text
   (
     concept-record-hash,
     ufo-bridge-hash,
     vectoriser-content-hash,
     vector-profile,
     D,
     quantisation-profile
   )
   ```

A released snapshot manifest binds the four layers. A “canonical vector” is canonical only relative to this complete tuple.

### 2.2 Semantic-status ladder

Every concept receives exactly one primary status:

| Status | Meaning |
|---|---|
| `Prime` | One of the profile-1 semantic primes |
| `Molecule` | Endorsed reusable composition |
| `Explicated` | Authored and endorsed profile-1 explication |
| `PrimeAnchoredPartial` | Some clauses or relations are safely aligned to primes, but no complete explication is claimed |
| `LogicalDefinition` | Source supplies a machine-readable definition, such as OBO genus–differentia |
| `AxiomsOnly` | Structural source axioms without semantic-adequacy claim |
| `LexicalOnly` | Lemma/sense/gloss evidence without authoritative formal structure |

**[STIPULATED]** Automatic NSM paraphrase does not promote a record to `Explicated`. It remains a candidate annotation until reviewed.

### 2.3 Full CK-UFO sidecar

Every record carries the complete schema, even when some values are unknown:

```yaml
schema: ck-ufo-scale/1
concept: urn:...
source_record_hash: sha256:...

denotation_level:
  value: type | individual | relation | proposition | underdetermined
  status: source-asserted | rule-inferred | endorsed | underdetermined
  warrant: [...]

ontic_category:
  value: object | event | quality | mode | disposition | relator |
         proposition | social-object | region | underdetermined
  status: ...
  warrant: [...]

sortality:
  value: kind | subkind | role | phase | category | mixin |
         role-mixin | phase-mixin | non-sortal | underdetermined

rigidity:
  value: rigid | anti-rigid | semi-rigid | underdetermined

identity:
  provider: urn:... | underdetermined
  criterion:
    reference_ufo: ...
    executable_rule: ... | null
    status: ...

dependence:
  inheres_in: [...]
  existentially_depends_on: [...]
  externally_depends_on: [...]
  status: ...

relator_pattern: ... | not-applicable | underdetermined
event_pattern: ... | not-applicable | underdetermined
disposition_pattern: ... | not-applicable | underdetermined

reference_ufo_commitment: ...
executable_projection: [...]
reference_only_residue: [...]
provenance: ...
review: ...
```

“Full UFO expressivity” means the system can represent every field and preserve reference-only commitments. It does not mean that every imported concept receives a fabricated identity criterion or that unrestricted modal UFO becomes decidable.

---

## 3. Sourcing millions of grounded concepts

### 3.1 Source portfolio

| Source | Use in SCALE-1 | Grounding strength | Principal risk | License posture |
|---|---|---|---|---|
| **WordNet/OEWN** | Broad English sense backbone; hypernymy; common noun/verb coverage | Human lexical curation and graph structure | Sense ambiguity; no verb argument typing; not million-scale alone | Local Princeton WordNet is redistributable with notice; OEWN CC BY 4.0 is a possible cleaner successor |
| **Wikidata** | Primary broad class/property and world-fact source; full statements retain qualifiers and references | Source-linked structured assertions; large cross-domain graph | Many items are individuals; class hierarchy and constraints are uneven | Structured entity data is CC0; official weekly JSON/RDF dumps are available [Wikidata database download](https://www.wikidata.org/wiki/Wikidata%3ADatabase_download/en) |
| **DBpedia** | Cross-source agreement, ontology mappings and Wikipedia-derived comparator | Human-edited encyclopedia extraction | Redundant with Wikidata; extraction artifacts; ShareAlike/GFDL obligations | Keep as a separately licensed comparator shard; use current [DBpedia core releases](https://www.dbpedia.org/resources/latest-core/) |
| **OBO/BFO** | Primary formal-definition vertical; expand beyond the currently loaded 96,192 records, including full taxonomy and chemistry sources where licenses permit | Strong source axioms; 24,578 local genus–differentia definitions already available | Biology domination; imported stubs; ontology-specific licenses; cycles | Per-ontology manifest and attribution; current local shards are redistributable |
| **SUMO** | Upper/mid-level type anchor, argument candidates and FOL comparator | Richer formal commitments than taxonomy alone | Translation into the safe executable profile is unbuilt; only 48 local terms have narrow syntactic definitions | IEEE attribution; preserve KIF and route unsupported content out-of-profile |
| **FrameNet** | Event/relational concept inventory and valency structure | Human-curated frames, core/peripheral roles and mappings | Frame is not a definition; frame elements are not hard domain/range restrictions | CC BY 3.0 |
| **BabelNet** | Optional multilingual alignment and sense-coverage ceiling | Integrates 22.9M synsets and reports 7.3M concepts [BabelNet statistics](https://babelnet.org/statistics) | Inter-resource error propagation; API/index restrictions; cannot form a permissive public core | Research-only, non-commercial shard; adaptations have restricted redistribution [BabelNet license](https://babelnet.org/license) |
| **ConceptNet** | Optional commonsense soft-edge and natural-input candidate source | Broad multilingual community graph | Noisy, defeasible and heterogeneous; unsuitable for hard entailment | CC BY-SA 4.0; isolated advisory shard [ConceptNet](https://conceptnet.io/) |
| **schema.org** | Web-type scaffold and deliberately weak `domainIncludes`/`rangeIncludes` preferences | Widely deployed type vocabulary | Coarse and non-logical; ShareAlike | Isolated soft-typing shard under CC BY-SA 3.0 [schema.org terms](https://schema.org/docs/terms.html) |

### 3.2 Recommended combination by function

**Permissive public core**

- WordNet/OEWN;
- Wikidata structured data;
- currently loaded OBO/BFO/RO;
- expanded OBO ontologies whose licenses pass the shard review;
- SUMO with IEEE attribution;
- FrameNet 1.7.

**ShareAlike isolation**

- ConceptNet;
- schema.org;
- DBpedia releases with applicable ShareAlike/GFDL terms.

These may be evaluated through separately built shards, but their vectors, alignment files and derived records must not be merged into a permissively licensed release until legal review confirms the derivative-work boundary.

**Research-only isolation**

- BabelNet.

BabelNet may measure a multilingual and sense-alignment ceiling. It must not be counted toward the redistributable flagship kernel, and no derived vector artifact should be published outside its permitted audience without license review.

### 3.3 Grounding pipeline

The bulk pipeline is:

```text
source snapshot
  → source-specific lossless extraction
  → canonical source record
  → exact crosswalks and conservative alignment clusters
  → prime-anchor / logical-definition extraction where licensed
  → full CK-UFO candidate classification
  → hard/soft/reference-only regime split
  → deterministic vector bundle
  → world/TBox compilation
  → audit sample and snapshot freeze
```

Grounding is reported as a vector of evidence, not a single marketing label:

```text
source-grounded
formally-defined
prime-anchored
human-endorsed
UFO-category-resolved
identity-resolved
world-linked
natural-input-linked
```

A concept may be strong on one dimension and unresolved on another.

### 3.4 Prime decomposition at scale

**[STIPULATED]** Full NSM authoring is concentrated where its marginal value is greatest:

1. Existing primes, molecules and kernel-v0 remain the endorsed base.
2. Automatically safe prime correspondences are extracted only from approved patterns.
3. OBO logical definitions remain `LogicalDefinition`; they do not become NSM merely because genus and differentia can be rendered in English.
4. FrameNet Core elements supply valency candidates, not the explication body.
5. SUMO formulae remain KIF unless an authored translation exists.
6. Active authoring targets concepts with high benchmark reach, graph centrality, ambiguity, rule leverage or safety significance.
7. Suggested explications are permitted as review queues but never as authoritative compiler input.

A realistic target is therefore millions of typed and source-grounded records, tens of thousands of prime-anchored records, and a smaller high-assurance explicated nucleus. The exact tier counts are experimental outputs.

### 3.5 Deduplication and the headline count

Report four counts:

```text
raw source records
exactly crosswalked clusters
type-level clusters
fully resolved CK-UFO records
```

Only type-level clusters count toward the million-concept claim.

Exact external identifiers and endorsed `exactAlignment` links may merge clusters. Label similarity, embeddings and LLM judgments may propose merges but cannot perform them automatically. Uncertain alignments remain separate and are reported as possible duplicates.

---

## 4. Full-UFO typing at scale

### 4.1 Deterministic classification cascade

Each CK-UFO field is assigned through an ordered cascade:

1. **Explicit imported commitment:** native gUFO/BFO/UFO mapping or source axiom.
2. **Endorsed crosswalk:** reviewed mapping to an existing typed concept.
3. **Rule inference:** a pinned, proof-producing pattern over trusted source axioms.
4. **Soft candidate:** lexical, statistical or cross-resource evidence.
5. **Underdetermined:** default if the preceding evidence is insufficient.

Examples:

- FrameNet frames may become `Event` candidates, not automatically endorsed event Kinds.
- OBO classes under material-entity or process anchors may inherit object/event candidates.
- A WordNet noun synset is not automatically a UFO Kind merely because it is a noun.
- A relationally conditioned class may become a Role candidate only when its identity provider and dependence evidence are available.
- A temporally contingent intrinsic classification may become a Phase candidate.
- A Wikidata statement about employment may support an employment-relator representation, but a bare `employedBy` edge must not invent a relator or founding event.
- Source identifiers establish record identity, not metaphysical identity criteria.

### 4.2 Hard, soft and reference-only separation

| Regime | Permitted use |
|---|---|
| `owl-rl` | Endorsed structural closure |
| `horn-def` | Safe positive rules over existing terms |
| `ufo-modal` | Bounded world/situation reasoning |
| `validation` | Closed-scope integrity and witness checks |
| `policy` | Explicit local assumptions and advisory decisions |
| `stable-model` | Future closed-world/default cases after a separate gate |
| `fol-atp` | Reserved SUMO/FOL route |
| `proof-assistant` | Mathematics and higher-order content |
| `reference-only` | Preserved commitment not executable in the selected profile |

Imported selectional restrictions from SUMO, FrameNet, schema.org or ConceptNet remain soft unless separately endorsed. They must never silently compile into `rdfs:domain` or `rdfs:range`.

### 4.3 Typing-quality audit

At every stage:

- sample independently by source, inferred category, confidence and graph depth;
- oversample Role/Phase, relator, disposition and identity-provider assignments;
- measure hard-type precision separately from soft-candidate usefulness;
- measure `underdetermined` rather than treating it as an error;
- re-run known g2 over-constraint examples;
- perform source-ablation and rule-removal checks;
- publish disagreement and coverage, not just accepted precision.

A promotion gate should require the lower 95% confidence bound for **hard executable typings** to exceed a preregistered high-precision threshold, proposed as 0.95. Soft preferences receive no hard-entailment threshold because they are evaluated as rank/lint signals.

---

## 5. Large world and rules engine

### 5.1 World-store target

At the 1M stage:

```text
C: ≥1M type-level concept clusters
E: millions of named world entities, reported separately
A: ≥100M asserted facts
Q: quoted proposition dictionary
R: reifiers for worlds, attitudes, provenance, time and norms
D: derived facts or demand-closure cache
P: hash-consed proof DAG
```

The initial world sources are:

- Wikidata full statements for selected properties, retaining qualifiers, ranks and references;
- OBO/SUMO/FrameNet as TBox and bridge material;
- benchmark-specific temporary worlds;
- explicit source-aligned relations from independently licensed datasets.

Strings that fail concept/entity resolution remain raw staging data and do not count as kernel facts.

### 5.2 Persistent and temporary worlds

- **Persistent default world:** closure built or indexed offline; runtime lookup and demand completion.
- **Temporary prompt world:** per-query facts; semi-naive delta reasoning against the persistent TBox.
- **Situation/modal world:** explicit `holds`, `notHolds`, `existsAt`, `accessible` and `closedFor` records.

No fact crosses a world boundary without a rule that names the transition.

### 5.3 Full-UFO representation in the world

The world supports:

- rigid and anti-rigid membership across supplied accessible worlds;
- identity-provider and `sameContinuant` records;
- qualities and modes as dependent particulars;
- dispositions, triggers, activations and manifestations;
- events, participation and temporal parts;
- relators, mediated participants and qua-individuals;
- quoted beliefs, goals, commitments, claims and norms;
- explicit `UNDERDETERMINED` and `OUT-OF-PROFILE` results.

`owl:sameAs` is avoided for operational cross-situation identity unless true RDF denotational identity is intended.

### 5.4 Decidability versus tractability

**[LIT-BACKED/DERIVED]** The UFO-SN3 profile remains terminating and decidable at large data scale if it remains:

- finite;
- function-free;
- range-restricted;
- positive in the materialisation stratum;
- stratified only over explicitly finite, closed validation scopes;
- restricted to existing terms, aside from deterministic proposition-term construction;
- bounded by declared memory, derived-fact and wall-clock limits.

Fixed-ruleset data complexity remains polynomial. That does not guarantee acceptable runtime or closure size. Polynomial closure can still be operationally unusable.

Scale controls:

1. Semi-naive delta evaluation.
2. Six-way or equivalent SPO/POS/OSP indexing.
3. Rule-specific join plans and cardinality telemetry.
4. TBox/ABox and source/world partitioning.
5. Demand-driven or magic-set evaluation for query-local rules.
6. No global materialisation of soft preferences.
7. No fresh existential individuals.
8. Per-world and per-rule derived-fact budgets.
9. Hash-consed proof DAGs; full proofs materialised only for evaluated or requested conclusions.
10. Incremental invalidation by source snapshot and bounded graph radius.

Required systems metrics:

```text
asserted facts
derived facts
closure amplification
iterations to fixpoint
largest intermediate join
peak RSS
build wall time
incremental-update time
query p50/p95/p99
prompt-delta p50/p95/p99
proof bytes per licensed answer
budget refusals by rule and source
```

### 5.5 Quoted triples at scale

**[MEASURED: `docs/next/arch/sparq-estate-landscape.md`, 2026-07-12]** sparq-core already has a first-class RDF 1.2 term model: triple terms are a native dict kind (`Stored::Triple([Id;3])`, `intern_triple_ids`, hashed, spill/compaction-safe), with full RDF 1.2 Turtle/N-Triples grammar (`<<( s p o )>>`, `rdf:reifies` desugaring, 128-deep nesting) and SPARQL 1.2 wired end-to-end. **Opaque inference over quoted triples therefore works today with zero new code** — triple-term IDs flow through RDFS/OWL-RL/Datalog joins as opaque constants and `sameAs` correctly never substitutes inside them. What is missing for UFO-SN3 is (i) structural **decompose/construct** of triple terms inside the rule dialect (the Datalog grammar admits only IRI/literal/var; effort M), and (ii) a subject-position validity guard. Separately, the `sparq-vectors` KGE estate loads quoted triples but every embedding layer **drops** them (`is_entity()` matches only IRI/blank), and its gUFO/UFO prior is a hard-wired no-op placeholder — so the CK-UFO vector blocks of §6 are net-new work, not a toggle. This changes the stage sequence below from "build quoted-triple storage" to "add structural rule-level matching over storage that already exists."

Stage sequence:

1. **10k:** use explicit proposition nodes with `qtSubject`, `qtPredicate` and `qtObject`. Verify quotation non-assertion.
2. **100k:** add or adopt native triple-term decomposition/construction in `sparq-reason`; require text/compiled parity.
3. **1M:** run explicit-node and native-term representations on matched shards and require equivalent conclusions, non-assertion behavior and proof provenance.
4. **Millions:** use canonical proposition IDs shared by multiple reifiers; partition indexes by proposition content and world.

A quoted belief or norm must never become asserted merely because the reasoner indexes its components.

---

## 6. Deterministic vectorisation at scale

### 6.1 Preserve construction B; do not overload it

**[STIPULATED]** Construction B remains the canonical `NSM block` for `Prime`, `Molecule` and `Explicated` records. Its algorithm version and content hash do not change.

Bulk imports use a new, separately pinned `kot-enc-import/1` vectoriser. This is necessary because:

- the current exact codebook has a closed slot/filler inventory;
- most imported concepts have no profile-1 AST;
- imported ontology graphs contain cycles;
- arbitrary property identifiers cannot all receive mutually orthogonal Hadamard rows at `D=8192`.

### 6.2 Vector bundle

```text
V(c) =
  masked_fusion(
    NSM block,
    imported-structure block,
    UFO category/modal/identity/dependence blocks,
    evidence block,
    optional lexical block
  )
```

Missing, false and not-applicable are distinct masks.

Persisted representation:

- dense semantic/import block at `D=8192`, normally fp16;
- sparse CK-UFO feature record;
- cryptographic concept and bridge hashes;
- optional ANN projection;
- Float64 canonical vector regenerated on demand.

The full fused vector is deterministic but need not be stored for every profile.

### 6.3 Imported-structure vectoriser

A scalable candidate construction is:

1. Canonicalise each structural axiom as an ordered feature token.
2. Assign arbitrary relation and feature tokens deterministic signed sparse codes derived from SHA-256 labels.
3. Aggregate with integer counters or a deterministic CountSketch.
4. Use fixed synchronous neighborhood rounds:

   ```text
   h0(c) = local structural features
   h(t+1,c) = normalize(
       self_weight × h(t,c)
       + Σ relation-bound h(t,neighbor)
   )
   ```

5. Pin the number of rounds, relation weights, degree normalization and traversal order.
6. Sort source edges before aggregation or use integer commutative accumulators.
7. Treat SCCs normally through synchronous rounds; do not require a reference DAG.
8. Keep source-ID identity codes outside the semantic-similarity block.
9. Record discarded or unsupported axiom kinds; never skip them silently.

This preserves deterministic regeneration and bounded computation. It does not preserve construction B’s exact zero-crosstalk property, so its coherence and reconstruction behavior require separate measurement.

### 6.4 Dimension and storage

At `D=8192`:

| Concepts | fp64 dense block | fp32 | fp16 |
|---:|---:|---:|---:|
| 10k | 0.66 GB | 0.33 GB | 0.16 GB |
| 100k | 6.55 GB | 3.28 GB | 1.64 GB |
| 1M | 65.54 GB | 32.77 GB | 16.38 GB |
| 3M | 196.61 GB | 98.30 GB | 49.15 GB |
| 10M | 655.36 GB | 327.68 GB | 163.84 GB |

**[DERIVED]** Storing every CK-UFO block as another dense 8192-vector would multiply these values and is rejected. Sparse typed fields plus on-demand fusion preserve expressivity without that multiplication.

Dimension does not need to grow merely because `N` grows. However, cleanup against a million candidates, ANN recall, false-nearest-neighbor behavior and projection into host dimensions all become harder. These are empirical scale gates.

### 6.5 Canonicality and collision classes

Three distinct collision questions must be reported:

1. **Concept-hash collision**

   At 10 million records, the SHA-256 birthday probability is approximately \(4.3\times10^{-64}\). **[DERIVED under the random-oracle approximation]**

2. **Semantic-vector collision / margin decay**

   Two structurally indistinguishable `AxiomsOnly` records may legitimately receive the same semantic block. This is not a cryptographic identity collision. The quantitative scale risk is *margin decay*, not exact collision: pairwise crosstalk between independent D=8192 vectors is `~N(0, 1/D)` with `σ = 1/√8192 ≈ 0.0110`, and the expected **maximum** spurious cosine over `m` candidates grows as `√(2 ln m / D)` — `≈ 0.046` at `m=10⁴`, `≈ 0.058` at `m=10⁶`, `≈ 0.064` at `m=10⁷`. **[DERIVED, Gaussian-crosstalk approximation]** So the nearest-neighbour margin an honest concept must clear rises slowly but monotonically with `N`; whether real explication/import vectors keep a usable margin above that rising floor at 1M–10M is the empirical §12 margin-distribution gate, not a settled property.

3. **Quantisation or ANN collision**

   fp16, int8, product quantisation or an ANN index may merge neighborhoods or lose the correct concept. These are deployment errors, not failures of the canonical Float64 generator. Calibration point from the shipped X4 harness (`poc/harness/x4.ts`, seedless Achlioptas sign projection): on kernel-v0 (54 concepts, 2,475 adversarial pairs) the fp16 round-trip angular floor is `~0.000222 rad` while the minimum adversarial angle is `~0.00225 rad` — a `~10×` margin-to-floor ratio at small scale. **[MEASURED: `poc/results/x4-kernel-v0-report.md`]** That ratio is what must be re-measured, not assumed, on the million-vector corpus.

**Decoder-side scale cost (distinct from encode/collision).** Within-grammar decoding probes fixed closed candidate sets (~65 primes, 129 fillers, 32 referent indices) and is O(1) in kernel size. The **one** decode cost that grows with kernel size is the concept-reference cleanup: `conceptNN`/`conceptSignature` (`encoder`'s `decoder.ts:236-251`) run a **linear O(|lexicon|·D) scan over the entire supplied concept map at every SP-head and every structured slot**. At 1M concepts this is the decoder analogue of the retrieval problem and is the reason the exact-vs-ANN recall gate (≥0.99) governs both retrieval and decode. **[MEASURED: decoder source, 2026-07-12]**

The canonical-vector property survives if it is stated narrowly:

> The same concept record, UFO bridge, vectoriser pin and profile produce identical authoritative Float64 bytes.

It does not imply global injectivity, correct semantic similarity or exact recovery from a million-candidate ANN index.

Required tests:

- cross-platform golden vectors;
- duplicate semantic-block census;
- nearest-neighbor margin distribution by type/source;
- fp16/int8 angular error;
- exact-versus-ANN recall on at least 10k held-out queries;
- minimal-edit sensitivity;
- shuffled-source and shuffled-UFO controls;
- projection distortion for each `(8192, host-dimension)` pair. **[Pre-registered X4 pairs are 8192→512 and 8192→576; kernel-v0 RDM Spearman was 0.9718 (512) / 0.9706 (576) at 54 concepts — the open scale question is whether that RDM fidelity holds when the projected set is 10⁶ vectors rather than 54.]**

Canonical builds use pinned CPU arithmetic and traversal order. GPU vectorisation may produce derivative caches but cannot define authoritative bytes unless exact determinism is demonstrated.

### 6.6 Model integration

A million concept IDs should not become a million-token frozen LM vocabulary in the first scale experiment.

Use:

- kernel-side retrieval;
- top-k concept/proof injection;
- verify-retry;
- direct execution;
- an adapter-mediated side channel;
- fixed JL projections only in explicitly projected arms.

A learned map is an adapter arm, not the raw canonical-vector arm. All projection distortion is measured on the actual million-vector corpus.

---

## 7. Scale experiment portfolio

### 7.1 SCALE-SYS — vector, index and closure qualification

| Field | Design |
|---|---|
| **Question** | Can the pinned vector and rules profiles process nested 10k/100k/1M/multimillion stores within declared resource budgets while preserving exactness? |
| **Arms** | Construction-B NSM block; import vectoriser; fp64/fp16/int8 caches; exact/ANN retrieval; eager closure/demand closure; explicit/native quoted propositions |
| **Primary endpoints** | Deterministic rerun hash; exact-versus-ANN recall; closure equivalence; budget-refusal rate; build time; peak memory |
| **What scale unlocks** | Candidate cleanup, graph cycles, memory mapping, index construction, join amplification and update propagation are absent from the current small fixtures |
| **Claim scope** | Systems qualification only; no correctness or efficiency thesis result |

### 7.2 SCALE-GROUND — flagship “does grounding help a model?”

| Field | Design |
|---|---|
| **Question** | Does a million-concept typed kernel improve a host model on externally authored human-gold tasks over matched text and flat-graph retrieval? |
| **Benchmarks** | FOLIO; EntailmentBank + ARC; full ARC Easy/Challenge; add Natural Questions, HotpotQA or FEVER only after source/license verification |
| **Nested scale** | 10k → 100k → 1M using a benchmark-blind inclusion order |
| **A0** | Host only |
| **A1** | Host + matched BM25/dense RAG over the same source text |
| **A2** | Host + flat structured-fact retrieval, no UFO blocks and no rule execution |
| **A3** | Host + typed kernel retrieval, rules off |
| **A4** | A3 + proof-carrying closure and verify-retry |
| **A5** | Direct executor; LM renders only |
| **Controls** | Shuffled concept alignments; Sattolo-shuffled rules; matched random/decoy concepts; 100-concept core embedded in a million irrelevant records; UFO-block mask |
| **Primary endpoint** | Paired human-gold accuracy interaction: `(A4−A2 at 1M) − (A4−A2 at 10k)` |
| **Supporting endpoints** | Unconditional accuracy; accuracy on tail-exposed items; retrieval recall; dangerous false acceptance; unsupported rejection; abstention; proof validity; mapper retention; cost/query |
| **What scale unlocks** | Long-tail coverage, ambiguity, realistic distractors and causally used concepts that do not exist in the small kernel |

No “emergence” wording is licensed unless:

- the scale interaction passes its preregistered bound;
- at least 30% of items are tail-exposed;
- the gain survives matched flat retrieval and decoy-store controls;
- the relevant proofs or retrieved records actually touch tail concepts.

### 7.3 RULES-SCALE — RULES-1 at realistic closure size

| Field | Design |
|---|---|
| **Question** | Do RULES-1’s licensed derivations remain exact and useful when facts and irrelevant rule candidates are large? |
| **Benchmarks** | FOLIO engine-compatible subset; EntailmentBank T1/T2; ARC carrier; ProofWriter only as a synthetic diagnostic |
| **Arms** | Stated lookup; OWL-RL only; OWL-RL + Horn; bounded UFO-SN3; full stack with one module removed at a time |
| **Primary endpoint** | Four-valued disposition accuracy: `ENTAILED`, `CONTRADICTED`, `UNDERDETERMINED`, `OUT-OF-PROFILE` |
| **Mechanism endpoints** | Entailed-cell non-reproducibility from stated lookup; proof validity; rule-removal attribution; near-miss sensitivity |
| **Scale endpoints** | Closure amplification, largest join, p95 delta-closure latency, proof bytes and budget refusals |
| **What scale unlocks** | Tests whether polynomial closure remains operationally tractable and whether demand reasoning dominates eager materialisation |

### 7.4 UFO-SCALE — full-UFO value and tractability

| Field | Design |
|---|---|
| **Question** | Do modal, identity, relator, moment, disposition and event commitments change licensed decisions or retrieval at realistic graph scale? |
| **Arms** | gUFO taxonomy only; representation-matched null; bounded full-UFO checker; module removals; checker plus UFO-aware retrieval |
| **Endpoints** | Disposition accuracy; false acceptance; underdetermination calibration; family-level attribution; candidate reduction; reasoner latency |
| **Data** | Existing source-asserted ontology constraints plus independently reconciled full-UFO cases embedded into large background graphs |
| **What scale unlocks** | Relator incidence, cross-world identity ambiguity, modal witness retrieval and category-valid candidate pruning under millions of distractors |

No suitable large existing human-gold full-UFO benchmark is established by the reviewed repository material. This is the exception to the human-built-benchmark preference; its custom gold must therefore be independently authored and reconciled, never LLM-proxy headline gold.

### 7.5 OFFLOAD-SCALE — verifier offload with a real store

| Field | Design |
|---|---|
| **Question** | Does verifier offload retain value when the acceptance store is no longer an item-aligned answer key? |
| **Arms** | Small host; small host + oracle-addressed verifier; small host + retrieved flat store; small host + retrieved typed store; large host; self-consistency at matched cost |
| **Benchmarks** | FOLIO and ARC for rule/knowledge checking; GSM8K only with its arithmetic verifier, explicitly not RULES-1 |
| **Primary endpoint** | Small-host-plus-retrieved-verifier non-inferiority or superiority against the larger host at matched end-to-end cost |
| **Supporting endpoints** | Retrieval failures; retry count; verifier calls; false rejection; latency; store build/update cost |
| **What scale unlocks** | Separates genuine retrieval-and-verification value from the current item-aligned-key mechanism |

### 7.6 DDC-SCALE — DDC with a real kernel

DDC currently calibrates on approximately 119 primes/concepts/molecules, leaving its native geometry arm underdetermined at `n ≪ d`.

Scale extension:

- **A1-small:** current approximately 119-concept K-static corpus.
- **A1-10k, A1-100k, A1-1M:** nested concept-diverse calibration sets.
- **A2-geometry:** 10k–100k activation/vector pairs, eliminating the present `n≈119, d=576` rank bottleneck.
- **A3-closure:** calibration text or fixed sketches from large-world derived conclusions.
- **Controls:** matched generic text, plain dictionary, shuffled definitions, shuffled closure and source-stratified random concepts.

Run two distinct scale manipulations:

1. **Fixed token budget:** increasing concept diversity without increasing calibration bytes.
2. **Growing token budget:** measuring the compute–quality curve of fuller kernel exposure.

Primary endpoints remain DDC’s matched-compression public-benchmark retention on FOLIO, ARC and GSM8K through `poc/pubeval`. Additional endpoints are basis stability across source strata, layerwise direction admission, rare-domain retention and calibration compute.

What scale unlocks:

- covariance and alignment estimated from substantially more than 119 concepts;
- long-tail direction coverage;
- a real test of whether kernel geometry differs from generic or dictionary calibration;
- detection of whether a large kernel improves, washes out or destabilises the selected model subspace.

### 7.7 BROAD-SCALE — broad-workload competitiveness

Use existing human-built tasks wherever possible:

- FOLIO for deductive reasoning;
- EntailmentBank + ARC for human entailment trees and science QA;
- ARC Easy/Challenge as the immediate broad carrier already wired into `poc/pubeval`;
- GSM8K for verifier-offload only;
- a later natural-knowledge panel such as Natural Questions, HotpotQA and FEVER after licensing and release pinning.

Report:

- unconditional benchmark score;
- score on kernel-covered items;
- coverage itself;
- coverage-adjusted score;
- tail score by earliest nested tier;
- failure due to mapping, retrieval, rules, host or out-of-profile content.

A sub-100-concept kernel cannot compete on this endpoint because most benchmark concepts are necessarily absent. At 1M, lack of coverage can no longer be assumed from inventory size; it must be measured as reach and successful use.

---

## 8. Staging, costs and progression gates

All costs below are planning estimates, not measured commitments.

| Stage | Target | Dense vector storage | Compute estimate | Engineering estimate | Progression gate |
|---|---|---:|---:|---:|---|
| **S0 — 10k** | 10k concepts; 1M facts | 0.16 GB fp16 / 0.66 GB fp64 | 50–200 CPU-h; 5–20 GPU-h; approximately $25–150 cloud equivalent | 2–4 weeks | Deterministic extraction/vector bytes; complete license manifest; zero soft→hard leakage; SPARQ/twin exact on sampled closures |
| **S1 — 100k** | 100k concepts; 10M facts | 1.64 / 6.55 GB | 200–2,000 CPU-h; 25–150 GPU-h; approximately $200–1,000 | 4–8 additional weeks | Hard-typing audit passes; ANN recall gate; closure completes inside pinned memory/time budget; update and proof provenance work |
| **S2 — 1M** | ≥1M type clusters; target 100M facts | 16.38 / 65.54 GB | 2k–20k CPU-h; 200–1,000 GPU-h; approximately $2k–10k | 8–16 additional weeks | Genuine-scale criteria pass; ≥30% tail exposure; flagship nested-scale experiment completes without invalid instrumentation |
| **S3 — millions** | 3–10M type clusters; 0.3–1B facts | 49–164 GB fp16 / 197–655 GB fp64 | 20k–200k CPU-h; 1k–10k accelerator-h; grant-class equivalent $10k–100k | Multi-quarter | Only after S2 identifies a licensed reason to extend the scale slope or a failure mode whose asymptote remains unresolved |

Graph indexes, source snapshots, quoted propositions and proof caches add storage beyond the vector column. At S2, plan for hundreds of GB; at S3, plan for a multi-terabyte working estate.

### 8.1 Technical gates

**S0 → S1**

- all records reproduce byte-identically;
- every record has semantic status, source pin and license;
- all full-UFO fields are present, including explicit unknowns;
- no unendorsed selectional preference enters hard closure;
- vector and closure differential tests pass;
- quoted content never becomes asserted.

**S1 → S2**

- stratified hard-typing audit clears its preregistered precision bar;
- exact-versus-ANN recall is at least 0.99 on a held-out 10k-query audit, or the index is repaired;
- closure and query paths meet pinned budgets without silent truncation;
- the natural-input mapper has measured retention and dangerous-error rates;
- the 1M sourcing plan reaches one million type-level clusters without counting named entities or relying on BabelNet.

**S2 → S3**

- the 1M store is causally exercised;
- at least 30% of headline items are tail-exposed;
- scale interaction is estimable with adequate power;
- no unresolved instrumentation failure dominates the result;
- additional millions answer a named unresolved scale question.

A failed progression gate means pause, repair or stop for that route. It is not itself a programme feasibility conclusion.

---

## 9. Compute and infrastructure

### 9.1 Cheapest resources first

1. **Local/ordinary CPU**

   Extraction, hashing, validation, small vector builds and S0 closure. Current RULES-1 shows that the small certificate is CPU-cheap, but this does not price million-scale closure.

2. **Oxford ARC**

   Appropriate for CPU-heavy extraction, graph vectorisation, closure, memory-mapped indexing and moderate GPU evaluation. Oxford ARC provides central HPC/HTC CPU and GPU infrastructure to Oxford researchers and approved collaborators on Oxford-led projects [Oxford ARC](https://www.ox.ac.uk/research/support/data-computing/research-computing/advanced-research-computing).

3. **Modal for Academics**

   Best for bursty, inference-heavy benchmark arms and parallel DDC/model evaluation. The current programme advertises up to $10,000 in academic credits and access to H100/B200-class GPUs [Modal for Academics](https://modal.com/academics).

4. **Google TPU Research Cloud**

   Suitable for JAX/TPU-compatible model training or large batched inference, not TypeScript vectorisation or graph closure. TRC grants temporary free TPU quota on a rolling basis; ordinary GCP VMs and storage remain chargeable [TPU Research Cloud FAQ](https://sites.research.google/trc/faq/).

5. **UK AI Research Resource**

   Reserve for the 1M/multimillion host and training campaigns after S0/S1 supply credible scaling measurements. As of 12 July 2026, the AI Open Access call is open to UK-based researchers and AI developers and closes on 17 July 2026; it provides compute rather than cash and explicitly asks applicants to demonstrate prior GPU use and a need to scale [UKRI AIRR call](https://www.ukri.org/opportunity/airr-compute-opportunity-ai-open-access/). Isambard-AI is described as 5,448 GH200 superchips.

### 9.2 Workload placement

| Workload | Preferred resource |
|---|---|
| Source extraction, hashing, manifests | Local CPU / Oxford ARC |
| Graph vector construction | Oxford ARC CPU; GPU only after profiling |
| SPARQ closure and differential reasoning | Oxford ARC high-memory CPU |
| ANN build and retrieval benchmark | ARC CPU/GPU or Modal |
| SmolLM host and DDC evaluation | Modal |
| Larger host, RULES-2 or adapter training | Modal credits, AIRR or TPU-TRC depending framework |
| Multimillion graph + large-model joint runs | AIRR |

AIRR or TPU allocations should not be spent on extraction code that has not passed S0/S1 deterministic and licensing gates.

---

## 10. Cheapest decisive scale experiment

The cheapest experiment that genuinely tests the maintainer’s scale thesis is not the 10k or 100k stage. Those are engineering pilots.

**[STIPULATED]** The decisive first scale experiment is:

### SCALE-GROUND-1M

- **Kernel:** 1M deduplicated type-level concepts, drawn from WordNet, expanded OBO and a Wikidata class/property subset; SUMO and FrameNet as anchors.
- **World:** at least 10M asserted facts, with 100M as the target if the closure benchmark permits.
- **Vectors:** D=8192 fp16 store plus reproducible Float64 regeneration; sparse full-UFO sidecars; exact and ANN indexes.
- **Benchmarks:** FOLIO, EntailmentBank + ARC and full ARC Easy/Challenge.
- **Host:** one small model already supported by the existing harness.
- **Nested sizes:** 10k, 100k and 1M from the same frozen supersets.
- **Primary comparison:** typed retrieval + proof-carrying verify-retry versus matched flat structured retrieval at 1M, with the architecture-by-scale interaction as primary.
- **Controls:** host only, text RAG, rules off, shuffled mappings, shuffled rules, 100-concept core inside a million-record decoy store.
- **Primary endpoint:** paired human-gold accuracy interaction.
- **Required supporting gates:** tail exposure, retrieval recall, proof validity, dangerous false acceptance and end-to-end cost.
- **Compute:** inference-only; planning band approximately $500–3,000 after the data and systems pipeline exists. **[EXTRAPOLATION]**
- **Human/engineering cost:** approximately 6–12 weeks after the 100k stage, dominated by crosswalks, typing audits and reliable natural-input retrieval rather than GPU time. **[EXTRAPOLATION]**

Why this is decisive at the intended scope:

- it actually reaches one million type-level concepts;
- the large store must be used by benchmark proofs or retrieval;
- it compares against the best simple alternative using the same source content;
- it tests both structured mechanism and natural-input end-to-end behavior;
- its nested scale interaction can detect improvement, no change or degradation;
- it requires no model pretraining.

It does not decide whether multimillion-scale model training is useful; that belongs to later DDC/RULES-2 scale arms.

---

## 11. Genuine demonstration versus token gesture

### A genuine scale demonstration includes

- one million deduplicated type-level concepts;
- explicit separation of concepts and named entities;
- a broad count excluding single-taxonomy domination;
- full CK-UFO schema with unknowns preserved;
- millions of kernel-addressed facts;
- rules actually executed;
- natural-input and structured-input legs;
- human-built external gold where available;
- tail-exposed evaluation items;
- nested scale slopes;
- matched flat retrieval and text-RAG controls;
- rule, mapping, source and UFO-module ablations;
- build and lifecycle costs.

### A token scale gesture includes

- counting Wikidata people or places as concepts;
- counting duplicate source records before alignment;
- using BabelNet’s millions while publishing only aggregate claims against a non-redistributable shard;
- vectorising millions of records but evaluating the same 84 g2 slots;
- retrieving only the existing approximately 100 kernel concepts;
- placing a tiny useful kernel inside a million irrelevant decoys without a tail-exposure requirement;
- evaluating only oracle-addressed structured inputs;
- reporting polynomial decidability as practical tractability;
- treating unknown UFO identity or rigidity fields as resolved;
- compiling ConceptNet or FrameNet preferences as hard domain/range;
- omitting storage, indexing, update, mapping or review costs.

---

## 12. Principal failure modes and their decisive measurements

| Failure mode | Measurement |
|---|---|
| Semantic-vector collisions or poor margins | Duplicate-vector census; margin distribution; minimal-edit and cross-source tests |
| ANN loses canonical concepts | Exact-versus-ANN recall, stratified by type and source |
| fp16/int8 damages geometry | Angular error and downstream retrieval delta |
| Imported graph vectoriser loses meaningful structure | Held-out axiom reconstruction; shuffled-edge and relation-mask controls |
| Encoder cannot handle cycles | SCC fixtures and synchronous-round determinism tests |
| Closure explodes | Closure amplification, intermediate joins, peak memory, budget refusals |
| Quoted beliefs become asserted | Non-assertion conformance suite at every stage |
| Modal checks misuse absence | Open-versus-closed paired cases |
| `sameContinuant` merges incompatible records | Identity-rule counterexamples and module-removal tests |
| Typing quality decays with scale | Stratified human audit and g2-style hard-typing rerun |
| Source diversity hides domain domination | Per-source and domain-balanced counts/results |
| Natural mapper fails | Retention, abstention and dangerous-error metrics |
| Large kernel adds only retrieval bulk | Matched text/flat retrieval and decoy-store controls |
| Rule source is not kernel-specific | `knull` and imported-rule source ablations |
| Store helps only through answer-bearing leakage | Gold-leak audit; independently authored EntailmentBank store |
| DDC overfits a calibration corpus | Generic, dictionary, shuffled and nested-size controls |
| Licensing blocks redistribution | Shard-level license manifests and build-from-source recipes |
| Lifecycle economics dominate | Mint, review, rebuild, update, storage and query-cost ledger |

---

## 13. Relationship to active experiments

- **rules-1-b:** the small controlled host-lift experiment. **[MEASURED, 2026-07-12]** Its predecessor RULES-1's GPU campaign was VOIDED as a degenerate instrument (all 12,870 scored entailed rows `item_correct_ext=0` in every arm, including the 858/858-certified engine-direct arm, root-caused to a prompt-frame defect); rules-1-b is the FROZEN prompt-frame rebuild whose CPU pilot recovered the instrument (A7 20/24 clears the 0.30 floor) but whose **A5 GPU host-validity pilot FAILED the floor and its launch was refused fail-closed** — no rules-1-b verdict exists yet. SCALE-1 reuses its architecture only after a valid frozen host-lift result; it does not alter its arms and is not a workaround for the blocked GPU leg.
- **g2-import-v2:** the immediate soft-typing repair test on 84 slots (FROZEN; A0 33/84 baseline, A3 bar ≥34/84; instrument-repair after g2-import went INSTRUMENT-INVALID on judge-pair κ instability, now gated on Gwet AC1 ≥0.65). Its patterns may seed scale typing only after its own gate; SCALE-1 independently audits them at each source scale.
- **DDC:** the current ≈119-concept training-free dimension-collapse experiment (Phase-1 DESIGN; donors SmolLM2-135M `d=576` / 360M `d=960`). DDC-SCALE is a later real-kernel replication and scale-slope that removes the present `n≈119, d=576` rank bottleneck, not a redesign of the current record.
- **RULES-2:** the current train-time materialised-closure experiment (DRAFT; 21,780 engine-materialised examples; **launch gated on `registry/verdicts/rules-1-b.json = PASS`, currently blocked**). A 1M default-world RULES-2 arm is a later extension after large closure and retrieval are qualified.
- **UFO-SN3/CK-UFO:** supplies the full representational and bounded-execution profile (reference implementation + draft PR ENGINEERING-SHIPPED; `data/ufo-sn3-items-v0/` = 630 diagnostic items); SCALE-1 supplies the missing data-size and systems stress test.

---

## 14. Neutral closing statement

SCALE-1 is designed to distinguish three possibilities without presupposing any of them:

1. value increases because realistic coverage, ambiguity resolution, retrieval and rule composition become available only at scale;
2. results remain unchanged because the useful mechanism is local and scale-independent;
3. performance or economics degrade because grounding quality, vector cleanup, natural mapping or closure becomes harder faster than coverage grows.

The 10k and 100k stages qualify the machinery. The 1M nested flagship is the cheapest experiment that tests the scale thesis itself. The multimillion stage is justified only by a named unresolved scale question after that result.

**CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING; this design issues no feasibility conclusion.**