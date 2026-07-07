# The sparq vectorisation estate — technical map & reusability assessment for the Kernel of Truth

**Scope.** Read-only survey of `/home/ec2-user/css/kernel/sparq` (crate `sparq-vectors`, plus
`sparq-canon`, `sparq-zk`, and the vector design records under `research/`), assessed against the
kernel programme's need: a **deterministic, training-free NSM-explication → vector encoder** with a
`(concept-hash → embedding)` table and a decode path back to consumable objects
(design doc: `/home/ec2-user/css/kernel/concept-gist/concept-hash-design.md`, esp. §3–§6, §9a).

**Method note (empirical honesty).** Every claim below is grounded in code as it exists on disk,
cited `file:line`. Where the sparq design docs *plan* something the code does not do, that is said
explicitly. One tasking correction up front: `crates/sparq-serve/src/canon.rs` is **not** RDFC
canonicalisation — it is SPARQL *query-text* cache-key canonicalisation (whitespace collapse +
optional variable alpha-renaming; `crates/sparq-serve/src/canon.rs:1-43`). RDFC-1.0 lives in the
standalone crate **`sparq-canon`** (`crates/sparq-canon/src/lib.rs:1-30`) and is consumed by
`sparq-zk` for commitments.

---

## 1. Deterministic vs trained: the exact split

`sparq-vectors` is architected so that **embeddings are normally produced out-of-process** and the
crate itself is a search/store/import surface (`crates/sparq-vectors/src/embed.rs:1-5`,
`src/structure.rs:10-17`). Almost everything *in-tree* is deterministic; the trained parts are
either external (remote embedding API) or an explicitly research-grade opt-in trainer.

### 1.1 Deterministic, training-free components (same input → same vector, no weights)

**(a) `HashEmbedder` — deterministic hashed text projection** (`src/embed.rs:26-102`).
Test-only by declaration, but fully deterministic and cross-platform: per token (word +
character-trigram over whitespace-normalised text), a 64-bit **FNV-1a** hash XOR a seed feeds a
**SplitMix64** stream that contributes ±1 to each of `dim` components; the accumulated vector is
L2-normalised (`embed.rs:41-72`, splitmix64 at `embed.rs:96-102`, default seed
`0x5354_5156_5645_4354` at `embed.rs:33`). Documented honestly: "It captures NO semantics ('car'
and 'automobile' are unrelated); do not ship it as a retrieval feature" (`embed.rs:21-25`).
Determinism is pinned by test (`embed.rs:679-687`). This is a signed random-projection over hashed
tokens — the exact trick reusable for hashing *concept-hash* terminals into fixed-width lanes.

**(b) The typed-literal encoders (structure-aware P1)** — pure functions keyed by datatype, "No
training, no graph state, no I/O" (`src/encode.rs:19-21`):

- **Datatype router** `route(datatype) -> Encoder` — exact dispatch on the datatype IRI alone:
  numeric family (incl. all derived integer subtypes) → `Numeric`, `xsd:boolean` → `Boolean`,
  date/dateTime/dateTimeStamp/gYear → `Date`, everything else (strings, langStrings, IRIs) →
  `Other`/text lane (`encode.rs:149-166`; enum and taxonomy blocks carry their own tags,
  `encode.rs:114-129`).
- **Order-preserving numeric encoder** (`NumericEncoder`, `encode.rs:250-333`): (1) fit an
  empirical per-predicate range from observed values (`fit`, `encode.rs:267-271`; `normalise`
  currently linear over `[min,max]` with clamping, `encode.rs:286-305`); (2) map the normalised
  scalar through a **strictly-monotone thermometer/cumulative code**: `dim[i] = clamp((u − i/d)·d,
  0, 1)` (`encode.rs:343-350`). The provable invariant: L2 distance between codes is globally
  monotone in value distance — "30 is nearer 31 than to 70, across the full range" — checked by the
  exported metamorphic property test `metamorphic_monotone` (`encode.rs:768-801`), which a periodic
  Fourier code would fail by design (`encode.rs:44-48`). Order-preservation is exact under **L2,
  not cosine** (`encode.rs:50-55`).
- **Boolean sign encoder**: one reserved ±1 dimension; `decode(slot) = slot >= 0.0` is an exact
  round-trip (`encode.rs:359-387`).
- **Date encoder**: temporal lexical → epoch-seconds scalar (`temporal_value`,
  `encode.rs:185-202`, XPath semantics via sparq-core `Timeline`, gYear handled directly) → the
  same thermometer lane (`encode.rs:400-429`).
- **Enum codebook** (`src/codebook.rs:39-133`): one-hot over a *closed* `sh:in`/`owl:oneOf` member
  set, width = members + 1, slot 0 reserved for the out-of-enum **invalid code**; membership is a
  **slot match, never a cosine threshold**; `encode`/`decode` round-trip every member
  (`codebook.rs:9-23, 123-133`).
- **QUDT unit normalisation** (`src/units.rs:103-208`): a curated affine table
  (`canonical = lexical·factor + offset`) to canonical SI per `QuantityKind`; unknown/compound
  units **fail closed** (`None`, never treated as dimensionless, `units.rs:180-200`); quantity
  kind is a routing slot so a length never shares a block with a mass (`units.rs:44-76, 173-178`).

**(c) The self-describing row layout — `SchemaHeader` / `.spqs`** (`encode.rs:532-709`). A node
vector is a **structured partitioned object**: contiguous, non-overlapping `Block`s each carrying
`(encoder tag, metric tag, offset, width, optional fusion weight)` (`encode.rs:469-513`).
Serialises to a deterministic little-endian byte string with magic `SPQS`, version 2
(`encode.rs:551-564, 629-644`); parsing is fail-closed (bad magic/version/tag/partition → `Err`,
`encode.rs:646-709`). The **metric-correctness guard** `check_euclidean` makes "cosine on a
non-Euclidean block" a detectable error, not silent corruption (`encode.rs:604-622`).

**(d) The taxonomy block (structure-aware P3)** (`src/taxonomy.rs`). `TaxonomyDag::build` extracts
the `rdfs:subClassOf` DAG from a (closed) graph with a **deterministic dense class order**
(sorted dict ids, `taxonomy.rs:95-133`), cycle-safe ancestor/depth computation
(`taxonomy.rs:157-209`). Two closed-form encoders:

- `EuclideanTaxonomyEncoder` (the default): `out[0]` = normalised depth; `out[1..]` = a **hashed
  ancestor bag** — each proper ancestor's stable class id hashes into one of `bag_dim` coordinates,
  then the bag lane is L2-normalised so distance reflects ancestry *overlap* not raw count
  (`taxonomy.rs:246-331`; width = `bag_dim + 1`, default `bag_dim = 16`).
- `HyperbolicTaxonomyEncoder`: a **closed-form, untrained** Poincaré-disc placement (radius from
  depth, angle hashed from class id — `taxonomy.rs:337-390`), tagged `Metric::NonEuclidean`. It
  exists so the **`GeometryGate`** has a real second arm: the gate *measures* average distortion
  `|d_embed/d_graph − 1|` of both geometries on the actual DAG and picks Euclidean unless
  hyperbolic strictly wins by a margin (default 5%) (`taxonomy.rs:405-520`). Adoption of
  non-Euclidean geometry is measurement-gated by construction.
- `DisjointnessOracle`: mines `owl:disjointWith` / `owl:AllDisjointClasses` / `owl:complementOf`,
  propagates through the materialised `subClassOf` closure, and provides train-time repulsion
  pairs plus a serve-time **answer-safe hard mask** (removes only *provably*-disjoint candidates)
  (`taxonomy.rs:527-560+`).

**(e) Graph fingerprint** (`src/fingerprint.rs`). Not a node vectoriser — a **staleness guard**
binding a `.spqv`/`.spqg` artifact to the graph generation it was built against. Three fields
(`dict_len`, `triple_count`, 64-bit `content_hash`); the content hash folds **per-term lexical
FxHash values in sorted (dict-id-order-independent) order**, with fixed-width writes so the value
is architecture-independent (wasm32 == native) and thread-count-independent
(`fingerprint.rs:16-53, 124-157, 228-274`); a golden value is pinned (`fingerprint.rs:631-658`).
Deliberately an integrity check, not a MAC (`fingerprint.rs:55-59`). The load-bearing caveat: the
store is **keyed by dict id**, and the fingerprint is blind to a pure id permutation, so a store is
valid only against the exact persisted graph generation (`Graph::save`/`Graph::open`, never a
re-parse) — a **term-keyed store is an acknowledged, unimplemented follow-up**
(`fingerprint.rs:61-90`, `src/store.rs:26-36`).

**(f) Deterministic preprocessing & sampling (P0)** (`src/structure.rs`).
`materialise_closure`/`close_for_vectorise` run the sparq-reason RDFS/OWL-RL closure *before*
vectorisation so entailed facts are real triples the encoders see (`structure.rs:98-122`);
`TypeConstraints::mine` reads declared+observed domain/range (`structure.rs:146-219`);
`NegativeSampler` draws corruptions from a SplitMix64 stream seeded per `(seed, triple, side)` —
"reproducible across runs and platforms" (`structure.rs:281-391`), with determinism pinned by test
(`structure.rs:564-574`).

**(g) Deterministic renderers/readers**: `verbalize` produces the exact template string
`"<label>. a <type>. <description>"` deterministically from the graph (`src/verbalize.rs:145-203,
233-281`); `shacl_priors`/`provenance` are read-only prior extractors (§4 below); `fuse_rrf`
/`fuse_scores` are pure rank-fusion arithmetic (`src/fuse.rs:1-25`).

### 1.2 Data-fitted (deterministic given pinned inputs, but corpus-dependent)

- `NumericEncoder::fit` / `DateEncoder::fit`: the normaliser depends on the **observed value set**
  per predicate (`encode.rs:258-271`). Same value + different fit corpus → different code. For a
  canonical kernel this means the fit breakpoints must themselves be pinned/content-addressed.
- `ScalarQuantizer` / `ProductQuantizer` (`src/quant.rs:1-52`): SQ per-dim ranges and PQ k-means
  codebooks are learned from the stored vectors (compression, not semantics).

### 1.3 Trained / external components

- **`RemoteEmbedder`** (`embed.rs:104-253`): an OpenAI-compatible `/v1/embeddings` client — the
  production text lane is an **external trained model**; the crate only validates the response
  (dim/finiteness/index, fail-closed, `embed.rs:401-453`). The `.spqv` header records **no model
  id, model version, or metric** — an acknowledged gap
  (`research/specs/vector-genai-estate-recon.md`, "Key missing provenance").
- **`train.rs`** (`kge` feature): a minimal CPU DistMult/ComplEx trainer, deterministically seeded
  (SplitMix64 init + negatives, `train.rs:44-50`), but explicitly "research-grade, not a
  production training subsystem", existing only "to produce embeddings to measure"
  (`train.rs:9-19`).
- **`eval.rs`** (`kge` feature): a filtered link-prediction harness (MRR/Hits@k, 2×2 closure ×
  type-negatives ablation, multi-seed, paired deltas) (`eval.rs:1-80`). **Checked as tasked: no
  benchmark numbers have been produced/committed since the design doc.** The module states "No
  numbers live in this file or any committed doc. The harness *computes* them at run time"
  (`eval.rs:73-80`); a repo grep finds no committed KGE ablation figures — only literature numbers
  quoted with sources in `research/genai-kg-embeddings-vectorindex.md:86-101`. The design record's
  posture stands: "No benchmark numbers appear anywhere in this document — none exist yet"
  (`research/structure-aware-vectorisation.md:8-12`).

**Bottom line for Q1.** The entire *literal/structural* lane stack — router, thermometer numeric,
boolean sign, date, enum codebook, unit normaliser, taxonomy ancestor-bag/depth, hashed
sign-projection text fallback, schema header, fingerprint, closure preprocessing — is
deterministic and training-free. The *relational/semantic* lane (what a node means beyond its
declared structure) is delegated to trained components (remote text embedder or the opt-in KGE
trainer). sparq's own design docs are candid that this split is deliberate
(`research/structure-aware-vectorisation.md:96-102`).

---

## 2. The decode direction: `grounding.rs`

`ground(graph, node, modality, cfg, introspection, store)` projects an **already-identified node**
into the object a consumer declared it needs (`src/grounding.rs:268-302`). Dispatch is by declared
`OutputType` → `Modality` (`grounding.rs:118-145`); ambiguous intent defaults to the exact,
re-checkable subgraph (`grounding.rs:47-51, 129-131`). Four modalities (`grounding.rs:99-187`):

1. **`Subgraph`** → `Vec<GroundFact>` — `(predicate IRI, rendered object, is_literal)` triples in
   a **stable, dict-id-independent order** (sorted by predicate then object,
   `grounding.rs:386-427`). Minimality is ABSTAT-style: restrict to the predicates of the node's
   *effective (most-specific) type's* characteristic set, mined from `sparq-introspect`, with
   `rdf:type` always kept; fail-open to all facts when no pattern matches
   (`grounding.rs:434-506`).
2. **`TypedSubVector`** → `{values: Vec<f32>, blocks: Vec<Encoder>}` — slices the node's stored
   `.spqv` row to only the requested encoder families using the `SchemaHeader` block spans
   (`grounding.rs:736-761`). This is the "return only the numeric lane / only the taxonomy lane"
   projection.
3. **`NlString`** → the deterministic `verbalize` passage, optionally extended with typed-value
   clauses (quantities, enum labels) under a char budget (`grounding.rs:310-349`).
4. **`TypedValue`** → exact typed slots: `Boolean(bool)`, `Number{value, datatype}`,
   `Quantity{value, unit}` (recognising the QUDT `qudt:numericValue`+`qudt:unit` shape,
   `grounding.rs:628-647`), `Enum{member, label}` — "each value is the literal's own value", never
   a cosine match (`grounding.rs:534-581`). Optional cross-unit reconciliation converts
   known-unit quantities to canonical SI, conservative on unknown/compound units
   (`grounding.rs:649-676`).

Completeness is **profile-relative by contract**: ground over a closure-materialised graph and the
result is complete relative to that entailment profile only — "No answer-completeness claim is
made" (`grounding.rs:31-45, 252-257`).

**Two honesty notes for the kernel.** (i) This is *node → object* projection, **not vector →
node inversion**. The vector→node step in sparq is ANN search (`nearest_term`) followed by
grounding, and — in the `neuro-symbolic` feature — a **propose-then-verify** pipeline where a
deductive gate (SHACL + OWL inconsistency check) rejects candidates fail-closed
(`src/lib.rs:54-61`). (ii) Per-block decode exists only where the encoder is exactly invertible:
`BooleanEncoder::decode` (`encode.rs:380-387`) and `Codebook::decode` (`codebook.rs:123-133`)
round-trip; the thermometer numeric code has **no implemented decoder** (an inverse is
mathematically straightforward — count saturated coordinates — but is not in the code).

---

## 3. Where a `(concept-hash → embedding)` table lands

The storage seam is exactly two files:

**`store.rs` — the `.spqv` table itself.** One f32 row per **dict term id (u32)**, one flat mmap
file: `magic "SPQV" | version=2 | dim u32 | count u64 | reserved | 24-byte graph fingerprint |
dense [count × dim] f32 | sorted (id u32, slot u32) index` (`src/store.rs:4-17`). Lookup is one
binary search plus a contiguous aligned slice (`store.rs:38-43`). Interfaces:
`create(path, dim)` → `put(id, &[f32])` → `with_fingerprint(graph)` → `finalize()`;
`open`/`open_from_bytes` for reads; `StreamingWriter` for O(1)-RAM builds (`store.rs:45-52,
163-226`); an optional delta sidecar (`.spqd`) for incremental add/remove/update behind the
`delta` feature (`store.rs:152-161`). The `SchemaHeader` travels as a sidecar byte string
(`encode.rs:538-543`).

**`import.rs` — the bring-your-own-embeddings bulk path.** `ImportSpec { spqv_path, dim, ids,
binding }` plus either a NumPy `.npy` (v1–v3, 2-D, C-order, `<f4`/`<f8`) or a headerless flat f32
dump; **row `i` of the matrix is stored for `ids[i]`** — the "row → dict-id contract"
(`src/import.rs:13-35, 100-110`). Validation is fail-closed before any proportional allocation;
the read is streaming (peak memory O(dim + index)) (`import.rs:37-59`). `ImportBinding::Graph`
binds the fingerprint (`import.rs:80-92`).

**How the kernel's table maps onto this.** A concept hash is a `urn:concept:<multibase>` URN —
an IRI. Interned into a sparq `Graph`, it gets a u32 dict id, and the whole estate (store, ANN,
filtered search, `vec:nearest`/`vec:search` SPARQL predicates, `src/lib.rs:110-123`) works
unchanged: build the graph of concept records, run the deterministic encoder out-of-process (or
in-process), and `import` the matrix against the interned ids. Two caveats:

1. **Id-keying vs hash-keying.** The `.spqv` is keyed by *mutable-generation* dict ids, with the
   staleness contract of §1.1(e). Concept hashes are immutable by construction, so the natural
   kernel key is the hash itself. sparq's own docs flag the term-keyed store as the right redesign
   (`fingerprint.rs:87-90`). Adapting `import.rs`'s row→id contract to a row→multihash contract
   (sorted multihash index instead of sorted u32 index) is a small format fork, not a rewrite.
2. **No model/encoder provenance in the header.** The concept-hash design (§9a) wants tables
   "keyed by model identifier + version" as signed annotations; `.spqv` records neither
   (`research/specs/vector-genai-estate-recon.md`). For a *deterministic* encoder this becomes an
   encoder-version + profile-hash field — which could live in the 12 reserved header bytes
   (`store.rs:11`) or the `SchemaHeader` sidecar.

---

## 4. Ontological structure as priors (`taxonomy.rs`, `shacl_priors.rs`) — applicability to explication trees

**`shacl_priors.rs`** (feature `structure-shacl`) reads a parsed SHACL shapes model read-only and
emits per-predicate priors (`src/shacl_priors.rs:11-35`): `sh:in` → an exact `Codebook`;
`sh:datatype` → a router-confirmed encoder family (mixed-family lists resolve to `Other`,
`shacl_priors.rs:216-232`); `sh:maxCount 1` **or** `owl:FunctionalProperty` (read from the data
graph, not the shapes — `shacl_priors.rs:234-254`) → `Cardinality::Functional` = **one
deterministic slot**, otherwise `Cardinality::Multi` = a **permutation-invariant pooled block**
(`shacl_priors.rs:49-60`). A predicate with no shape has no prior — fail-open, never a guess
(`shacl_priors.rs:33-35`).

**Applicability to NSM explication records — direct, with one gap:**

- The profile-1 grammar is *closed everywhere* (65-prime lexicon, closed role inventory, closed
  operator set with fixed arities, closed valency frames with req/opt slots, `refKind` enum,
  `semanticStatus` enum — concept-hash-design §4.1–§4.6). Every one of these is exactly the
  **closed-enum codebook** case: exact slot-match encoding with a reserved invalid code, no
  training, no recall loss. Prime category, chart index (bounded integer → thermometer), frame
  type, operator, role — all encode losslessly with the existing machinery.
- The **valency frames' req/opt slots** map onto the `Functional` cardinality prior: each role in a
  frame appears at most once, so each is "one deterministic slot" — the structured-row discipline
  fits explication clauses well.
- `TaxonomyDag` + `EuclideanTaxonomyEncoder` transfer directly to the concept **dependency DAG**
  (explications reference other hashes; axioms include `subClassOf`): a concept's hashed
  ancestor-bag over its transitive definitional dependencies plus a depth-from-primes lane is a
  deterministic "position in the concept hierarchy" block, computable at mint time. The
  `GeometryGate` gives a principled, measured way to decide whether that DAG warrants a hyperbolic
  block. The `DisjointnessOracle` applies as-is since `cdef:rel` includes `disjointWith`
  (concept-hash-design §5) — giving an answer-safe mask over provably-disjoint concepts.
- **The gap:** explications are **ordered clause lists** (≤32 clauses) with cross-clause referent
  binding (§4.2, §4.6). sparq's multi-valued prior is *permutation-invariant pooling* — exactly
  wrong for ordered clauses — and nothing in the estate encodes nesting or coreference. See §6.

---

## 5. The ZK estate: commitment scheme and domain separation

**Scheme** (`crates/sparq-zk`): per-named-graph commitments over **RDFC-1.0-canonicalised**
content. Pipeline (`sparq-zk/src/commit.rs:1-13`): canonicalise the graph (via `sparq-canon`,
W3C rdf-canon test-suite validated, `sparq-canon/src/lib.rs:18-27`) → encode each canonical triple
to a BN254 field-element leaf in canonical N-Quads order → `C(G)` = one **Poseidon2 sponge** over
the leaf sequence. Term encoding (`sparq-zk/src/encode.rs:1-33, 45-75`):

- `Enc_t(term) = Poseidon2(type_code, blake3(bytes))` — **Blake3 off-circuit, Poseidon2
  in-circuit**; 32-byte Blake3 digests map into the field by truncation to the low 31 bytes.
- **Domain separation, three layers:** (i) explicit **type codes** IRI=1 / Literal=2 / BlankNode=3
  as field-element separators inside `h_2` (`encode.rs:32-35`); (ii) literals hash their full
  canonical N-Triples token so datatype/langtag fold into the bytes (`encode.rs:19-22`, with a
  test pinning that `"1"`, `"1"^^xsd:integer`, `"1"@en` are distinct, `encode.rs:107-121`);
  (iii) the sponge's **length-bearing IV** gives per-leaf-count domain separation
  (`commit.rs:5-10`).
- **Blank nodes are graph-salted**: `Poseidon2(BlankNode_code, Poseidon2(salt_G,
  blake3(c14n_label)))`, salt drawn from the OS CSPRNG at ingest and recorded in the registry —
  closing cross-graph bnode correlation (`encode.rs:4-15`).
- The commitment **method is a closed enum** recorded as a `zk:scheme` IRI; unknown methods fail
  closed, and the estate is candid that nothing is externally audited and the `dual-leaf` variant
  downgrades an in-circuit invariant to issuer honesty (`commit.rs:20-95`).

**Could concept-hashing and ZK commitments share discipline? Yes — they already nearly do.** Both
pipelines rest on the same spine: extract a bounded record → validate fail-closed → RDFC-1.0
canonical N-Quads → hash with an explicit domain separator folded *inside* the digest. The
concept-hash design's profile header (`UTF8("urn:concept-def:1\n") ‖ canonical bytes`, §6 step 5)
plays the same role as sparq-zk's type codes and length-bearing IV: no payload can verify under the
wrong profile/shape. The differences are principled, not accidental: the kernel's records are
public and immutable, so it *rejects* ambiguous blank-node structure at the gate (duplicate-FDH
rule, trees only) where sparq-zk *salts* bnodes for cross-graph unlinkability; and the kernel uses
SHA-256/multihash for agility where sparq-zk uses Blake3→Poseidon2 for circuit efficiency. A future
"ZK-provable concept kernel" (prove a vector was derived from a committed explication) could reuse
`sparq-canon` verbatim and re-target the leaf hash from `sha2-256` to the
`Poseidon2(type_code, blake3(·))` composition without changing either design's canonicalisation or
domain-separation discipline. `sparq-canon` itself is the single most directly reusable artifact
here: it is exactly the RDFC-1.0-over-an-extracted-record engine the §6 minting algorithm needs,
including the fail-closed HNDQ work-limit posture (`sparq-canon/src/lib.rs:44-49`).

---

## 6. Verdict: reusable for the kernel

### Reusable as-is (deterministic, tested, drop-in)

1. **`sparq-canon`** — RDFC-1.0 canonicalisation, W3C-suite validated, with fail-closed handling
   of pathological inputs. The concept-hash minting pipeline (§6 of the design) can be built
   directly on it.
2. **The structured-row discipline**: `SchemaHeader`/`Block` with per-block encoder + metric tags,
   deterministic byte round-trip, fail-closed parse, and the metric-correctness guard
   (`encode.rs:532-709`). This *is* the record format for a partitioned concept vector.
3. **The exact closed-set encoders**: `Codebook` (one-hot + reserved invalid slot + decode
   round-trip) for primes/categories/roles/operators/frame-types/status; `BooleanEncoder`;
   thermometer `NumericEncoder` for bounded integers (chart index, restriction cardinalities,
   referent indices) — with the fit breakpoints pinned in the profile rather than data-fitted.
4. **`EuclideanTaxonomyEncoder` + `TaxonomyDag` + `GeometryGate` + `DisjointnessOracle`** over the
   concept dependency DAG (§4 above) — deterministic hierarchy position + measured-geometry
   decision + answer-safe disjointness masking.
5. **The hashing discipline**: FNV-1a/SplitMix64 seeded sign-projection (`HashEmbedder`) and the
   hashed ancestor-bag as the deterministic mechanism for folding *unbounded sets of
   content-addressed references* into fixed-width lanes; fixed-width, seedless, sorted-fold
   hashing per `fingerprint.rs` for artifact integrity.
6. **Storage + search estate**: `.spqv` store, `StreamingWriter`, `import.rs` bulk import,
   fingerprint binding, exact/HNSW/DiskANN search, filtered ANN, RRF fusion, and the
   `vec:nearest`/`vec:search` SPARQL surface — a complete serving layer for a
   `(concept → vector)` table once ids are minted.
7. **The verification patterns**: `metamorphic_monotone` as the property-test template for encoder
   invariants; `ground()`'s modality dispatcher and `propose-then-verify`'s fail-closed deductive
   gate as the decode-direction architecture.

### Adaptable (small, well-understood changes)

1. **Hash-keyed rows.** Swap the `.spqv` sorted `(u32 id → slot)` index for a sorted
   `(multihash → slot)` index, or accept the id-keyed store plus a persisted concept graph and
   its staleness contract. sparq already names the term-keyed redesign as a follow-up
   (`fingerprint.rs:87-90`).
2. **Encoder/profile provenance in the header** (reserved bytes or the `.spqs` sidecar) to satisfy
   the design's model-identifier-keyed table requirement (§9a) — trivially stronger here because
   the encoder is deterministic: the "model id" is a content hash of the encoder spec.
3. **Ordered composition.** Replace the `Multi → permutation-invariant pooling` rule with
   position-aware pooling for ordered clause lists (e.g. clause-index thermometer ⊗ clause lane),
   reusing existing lanes.
4. **Fit-free numeric normalisation.** Pin `NumericEncoder` breakpoints in the profile bundle
   (caps are already fixed constants — record size ≤ 65,536, clauses ≤ 32, referents ≤ 32) so the
   corpus-dependence of `fit` disappears.

### Missing entirely (the kernel must build these)

1. **A recursive, compositional tree encoder.** Nothing in sparq encodes *nested structure* —
   valency frames filled with sub-phrases, operator clauses over clauses, quote re-anchoring,
   referent binding — into a vector. sparq's deterministic lanes are per-node/per-literal features;
   its compositional/relational semantics are delegated to *trained* KGE or external text models.
   The kernel's core encoder — a deterministic fold over the explication tree (role-wise
   domain-separated binding/superposition, VSA-style, or any injective-enough composition
   operator) — has no counterpart in this estate. sparq contributes the ingredients (domain
   separation discipline, seeded projections, closed-slot codebooks) but not the operator.
2. **Coreference encoding.** Indexed discourse referents (`cdef:bind`/`cdef:ref`) have no analogue
   anywhere in sparq's encoders.
3. **Graded semantic similarity from deterministic codes.** The estate is honest that hash lanes
   carry no semantics (`embed.rs:21-25`). A deterministic kernel's neighbourhood structure will
   reflect *structural overlap of explications* (shared primes, shared ancestors, shared frames) —
   which is arguably the right notion for NSM, but is an untested hypothesis; no benchmark exists
   here or in sparq (eval harness present, zero committed numbers — §1.3).
4. **A non-Euclidean search kernel**, if the `GeometryGate` ever selects hyperbolic (sparq tags
   the block and refuses cosine on it, but ships no Poincaré ANN).
5. **Inverse decoders for the numeric lane** (thermometer → value) — feasible, unimplemented.

### One-line verdict

sparq supplies, tested and deterministic: the canonicaliser the concept-hash needs, the
partitioned-row format, the exact closed-set/numeric/taxonomy lane encoders, the hashing and
domain-separation discipline, and the full storage/ANN/decode serving layer — roughly the entire
*periphery* of a deterministic explication→vector encoder. What it does not supply is the *centre*:
a deterministic composition operator that turns a nested, referent-bound explication tree into one
vector, and any evidence about the semantic quality of purely deterministic neighbourhoods. That
operator — plus hash-keyed rows and pinned encoder profiles — is the kernel's genuinely novel work.
