# How a concept becomes a vector — the definitive explainer

**Status:** explainer, 2026-07-08. Written for the maintainer: no ML/NLP background assumed, last
synced before the JSON representation existed, and asking how this relates to the earlier sparq
work. Everything here is grounded in code and reports in this repo (cited by path) — nothing is
aspirational unless explicitly marked *planned* or *not yet built*.

**Sources of truth:** `encoder/src/{lexicon,codebook,encoder,det}.ts` (the implementation),
`docs/architecture.md` §1 (the design record), `reports/deterministic-concept-vectors.md`
(the capacity mathematics), `reports/sparq-estate.md` (the sparq survey),
`poc/results/kernel-v0-phase-x-summary.md` and `poc/e*/results*/verdict-*.md` (the measurements).

---

## 0. The one-paragraph version

Every concept in the kernel is *defined* — written out as a small, machine-checkable definition
tree ("explication") over a closed vocabulary of ~65 semantic primes (NSM: I, YOU, SOMEONE,
HAPPEN, KNOW, WANT, GOOD, BIG, NOT, …). The encoder turns that tree into one fixed-length list of
8,192 numbers by pure, seedless arithmetic: the 65 primes and every other structural atom get
**fixed, mutually perpendicular starting vectors** (rows of a Hadamard matrix — no training, no
randomness); within a clause, "which role does this filler play" is stamped in by an exact
XOR-style binding; across clauses and nesting depth, sub-structures are folded in by a
norm-preserving circular convolution plus fixed position shuffles; a definition that *references*
another concept folds in that concept's own finished vector, recursively; and everything is added
up and scaled to length 1. Same definition in, byte-identical vector out, on any machine, forever
— that is the whole point. Quality is measured, not asserted: the Phase-X property suite shows
the geometry is robust (X1, X4 pass), decodable with one known gap (X2, 51/54), and **not** safe
for naive cosine similarity (X3 — a deep NOT barely moves the vector while inverting the meaning,
so cosine on kernel vectors is banned downstream).

---

## 1. What the encoder consumes: the JSON concept record

Since you last looked, the design moved from an RDF-first representation to a **JSON-first** one
(decision record: `docs/design-hash-input.md` — every validator, encoder and experiment computes
over the JSON ASTs, so identity is hashed over those same bytes; RDF is now a *projection* for
estate interop, never the hash input).

A concept is one JSON file in `data/kernel-v0/concepts/`:

```jsonc
{
  "id": "urn:kernel-v0:alive",       // working id; content-addressed URN minted separately
  "label": "alive",
  "status": "research-grade",
  "gloss": "this someone lives now; the body can move; this someone can feel something.",
  "notes": "KNOWN-WEAK: ...",         // honesty annotations, OUTSIDE identity
  "references": [],
  "explication": { ... }              // the typed AST — the ONLY thing the encoder sees
}
```

The `explication` (schema `kot-ast/1`, `encoder/src/ast.ts`) is a tree with a closed grammar:

- a **frame** (one of 3: `InstanceSchema`, `WhenTrue`, `RelationalSchema`);
- **referents** declared by index (1..32) with a kind (`SomeoneRef`, `SomethingRef`, `TimeRef`,
  `PlaceRef`, `ClauseRef`) — these are the "this someone / this thing" discourse variables that
  clauses can point back to (coreference);
- an ordered list of **clauses** (≤32), each either
  - a **pred clause**: a predicate prime (DO, HAPPEN, KNOW, FEEL, LIVE, …) plus a role→filler map
    drawn from a closed role inventory (agent, undergoer, experiencer, stimulus, … 13 core + 4
    adjuncts), constrained by per-predicate valency frames (`lexicon.ts PREDICATE_FRAMES`), or
  - an **op clause**: a logical operator (NOT, CAN, MAYBE, IF, BECAUSE, WHEN, LIKE, AFTER, BEFORE,
    VERY, MORE — closed set with fixed arities) over clause/entity arguments;
- fillers are primes, referent indices, **substantive phrases** (`sp`: determiner + quantifier +
  mods + head + optional restricting clause — "the same someone", "two big things"), quotes,
  temporal anchors, or **references to other concepts by id**.

Everything is closed and capped (≤32 clauses, ≤32 referents, depth ≤12 — `lexicon.ts CAPS`).
The caps are not conveniences: the capacity mathematics in §3 is *about* them.

**Identity** is separate from geometry: the concept's permanent name is
`urn:kot:<multibase-base32(sha-256)>` computed over the RFC-8785 (JCS) canonical JSON of the
explication identity payload with a profile-header prefix (`docs/design-hash-input.md`; minted
URNs in `data/kernel-v0/minted-urns.jsonl`). Two records with the same definition get the same
URN; edit one clause and you have a different concept. The hash gives exact identity and
zero similarity; the vector gives geometry. They are siblings, not rivals.

---

## 2. The vectorisation, step by step

The construction is called **construction B** (`docs/architecture.md` §1.2;
`reports/deterministic-concept-vectors.md` §7.3), implemented in `encoder/src/encoder.ts`
(`ALGORITHM_VERSION = 'kot-enc-B/1'`). It is a two-level scheme from the Vector Symbolic
Architecture / Tensor Product Representation literature (Smolensky 1990; Plate 1995): **exact
algebra within a clause, capacity-priced compression across clauses and depth**.

### 2.1 Level 0 — fixed starting vectors for every atom (no training, no seeds)

Pick D = 8192. The D×D **Sylvester-Hadamard matrix** H has entries
`H[i][j] = (−1)^popcount(i AND j)` — a purely combinatorial object, computable by anyone from
that one formula. Its rows, scaled by 1/√D, are **exactly orthonormal**: each has length 1, and
any two distinct rows are exactly perpendicular (dot product 0 in exact arithmetic; < 1e−15
observed in float64). No random number generator is involved anywhere.

Every atom in the closed grammar is assigned a row by a pinned table (`codebook.ts`):

- **rows 1–65: the 65 NSM primes, in chart order** (`lexicon.ts PRIMES`, chart v20 2022:
  I = row 1, YOU = 2, … NOT = 58, … LIKE~AS~WAY = 65). *These are the fixed base-unit vectors —
  the direct answer to your question in §4.*
- rows 66–76: the 11 operators; 77–79: the 3 frames; 80–84: the 5 referent kinds; 85–87:
  structural tags; 88–97: intensified mods (VERY+GOOD, …); 98–129: referent indices 1–32.

That is ~130 filler atoms (an 8-bit field, ids 1–255 available) and **31 slot names** (a 5-bit
field): the 17 roles plus structural slots (`det, quant, mod, head, of, restrictedBy, bind,
arg0, arg1, ctype, pred, op, frame, refdecl`).

### 2.2 Level 1 — within a clause: exact XOR binding of (role, filler)

To say "SOMEONE fills the *experiencer* role" (as opposed to the *agent* role) the encoder must
glue the role to the filler. For Hadamard rows this is exact and beautiful: the elementwise
(Hadamard) product of row *a* and row *b* is row *(a XOR b)* (times √D) — binding two codebook
vectors **never leaves the codebook**, unbinding is exact self-inverse, and crosstalk between
distinct bound pairs is exactly zero.

To guarantee that no two (slot, filler) pairs collide, the row index is a **disjoint bit-field**:
`index = (slotId << 8) | fillerId` — 5 slot bits, 8 filler bits, 13 bits total. Every pair gets
its own unique orthonormal row. **This is why D ≥ 2^13 = 8192 is the hard floor** (smaller D
fails closed, `ERR_DIMENSION_TOO_SMALL`).

A pred clause is then simply the *sum* of its bound atoms:

```
v(clause) = H[ctype ⊕ TAG:PRED] + H[pred ⊕ prime:P] + Σ_roles H[role ⊕ filler]   → normalise to length 1
```

Because all terms are exactly orthogonal, each component is perfectly recoverable: project onto
any candidate row and you get its coefficient exactly. Within a clause, nothing is approximate.

### 2.3 Level 2 — structured fillers and depth: unitary circular convolution

When a filler is not an atom but a whole sub-structure (an SP, an embedded clause, a referenced
concept's vector), you cannot XOR it — it is not a codebook row. Instead the encoder uses
**HRR circular-convolution binding** (Plate, IEEE TNN 1995): the sub-structure's vector `f` is
convolved with a fixed **slot tag** whose Fourier spectrum has unit magnitude everywhere
(quarter-phase ±1/±i entries drawn from a SHA-256 stream over the label `tag/<slot>` — public,
deterministic, exactly float-representable). Unit-magnitude spectra make the binding **unitary**:
it preserves lengths, is exactly invertible (correlate with the conjugate tag), and — critically
for our ≤12-deep trees — does not blow up or shrink with nesting depth (Plate §VIII-C).

One engineering subtlety, documented in `codebook.ts`: Walsh/Hadamard rows have *concentrated*
Fourier spectra, which would alias badly under convolution. So every structured filler is first
passed through a fixed **spectral whitener** W (a deterministic signed permutation) that makes it
spectrally flat. W is exactly unitary and exactly invertible; it is part of the pinned algorithm.

So: `bound = tag_slot ⊛ W(f)`, computed by FFT. Structured terms enter the sum with a pinned
weight `alphaStruct` (default 1.0 — an acknowledged free parameter, measured in X3).

### 2.4 Level 3 — clause order, referents, and the whole explication

- **Ordered clauses:** clause *i*'s vector is passed through a fixed position permutation π_i
  (derived from SHA-256 over the label `clause/i`) before superposition — so "clause 2 then
  clause 3" differs from "clause 3 then clause 2".
- **Referent declarations:** the kind atom (e.g. `refkind:SomeoneRef` bound under the `refdecl`
  slot) is passed through a per-index permutation ρ_n. (Permutation binding is used here because
  the (index × kind) product space would overflow the 13-bit exact-atom budget.)
- **The frame** enters as one bound atom.
- Everything is summed **in one pinned traversal order** (float addition is not associative, so
  the order is literally part of the algorithm) and normalised to unit length.

### 2.5 Level 4 — concept references: recursion over the concept DAG

If a definition references another concept (`{"kind":"concept","id":"urn:…"}`), the encoder binds
**that concept's own finished canonical vector** under the slot tag — it does *not* inline the
referenced definition. This is load-bearing twice over:

1. **Compositionality by construction:** `death`'s vector literally contains (a bound copy of)
   `die`'s vector. Change `die`'s definition and `death`'s vector changes — but then `die`'s
   content hash changes too, so identity and geometry move together.
2. **Capacity budget:** inlining definitions would explode the number of bound terms past what
   D can hold (§3). Reference-not-inline keeps every explication at s ≈ 100–200 bound terms.

`encodeConceptSet` (`encoder.ts`) resolves references memoised over the whole concept set in
deterministic (sorted) order; references must form a DAG — **cycles fail closed**
(`ERR_CYCLIC_CONCEPT_REF`; fixed-point encoding of mutually recursive definitions is explicitly
deferred). The kernel-v0 corpus (54 concepts) includes 18 reference-bearing concepts; all 18
decode exactly (phase-X summary).

### 2.6 Worked example: `alive`, symbolically

The real record `data/kernel-v0/concepts/alive.json`: frame `WhenTrue`; one referent
(index 1, `SomeoneRef`); three clauses — "this someone lives now", "the body can move",
"this someone can feel". Write `H[s⊕f]` for the Hadamard row of slot s bound to filler f,
`⊛` for whitened unitary convolution with a slot tag, `π_i`/`ρ_n` for the fixed permutations,
`N(·)` for normalise-to-unit-length.

**Clause 0 — `LIVE(undergoer: ref 1, time: NOW)`.** Four exact atoms, all mutually orthogonal:

```
c0 = N( H[ctype⊕TAG:PRED] + H[pred⊕LIVE] + H[undergoer⊕ref:1] + H[time⊕NOW] )
   —  each term’s coefficient is exactly 1/2 after normalisation; exact unbinding.
```

**Clause 1 — `CAN( MOVE(undergoer: SP[head BODY]) )`.** Built inside-out:

```
sp   = N( H[head⊕BODY] )                                    — the SP "the body" (one atom)
move = N( H[ctype⊕TAG:PRED] + H[pred⊕MOVE] + tag_undergoer ⊛ W(sp) )
c1   = N( H[ctype⊕TAG:OP] + H[op⊕CAN] + tag_arg0 ⊛ W(move) )
```

The SP is a *structured* filler, so it enters `move` by convolution, not XOR; the whole MOVE
clause is itself a structured argument of the CAN operator, so it enters `c1` by convolution
again — that is depth-2 nesting, and the unitary property is what keeps `c1` well-conditioned.

**Clause 2 — `CAN( FEEL(experiencer: ref 1) )`.** Same shape as c1.

**Assembly:**

```
v(alive) = N(  H[frame⊕WhenTrue]                    — the frame atom
             + ρ_1( H[refdecl⊕SomeoneRef] )         — referent 1’s declaration
             + π_0(c0) + π_1(c1) + π_2(c2) )        — position-permuted clauses
```

That `Float64Array(8192)`, unit length, is the canonical vector of `alive` — and if `alive` were
referenced by some other concept (say `kill` referencing `die` referencing `alive`), this exact
vector is what would be convolved into theirs.

**Decoding** runs the construction backwards: peel the frame and referent atoms (exact
projections), try each position permutation inverse, unbind slot tags by conjugate convolution +
un-whitening, and clean up each recovered fragment by nearest-neighbour against the known
codebook and concept lexicon. Decoding is always stated as *recoverable given the kernel* — the
cleanup lexicon is the kernel itself; a vector alone, without the codebook, is white noise by
design.

### 2.7 Why it is deterministic and training-free, and what D = 8192 buys

**Training-free:** there are no learned weights anywhere. The atom vectors are closed-form
Hadamard rows; the tags, permutations, and whitener are expanded from SHA-256 over *fixed,
versioned labels* (`det.ts`, domain `kot/enc/v1`) — public pseudo-randomness anyone can
recompute, not trained parameters and not even a seeded RNG in the usual sense.

**Deterministic to the byte:** IEEE-754 float64 `+ − × ÷ √` are exactly specified; SHA-256 is
bit-exact; the traversal/summation order is pinned; the single caveat (Math.sin/cos in the FFT)
is documented and guarded by X0 golden-vector fixtures (`poc/results/x0-report.md` — committed
reference vectors byte-compared on every run). The **encoder content-hash**
(`40e8c8ba4c3d…` for the current pin) covers {schema, algorithm, D, codebook table, weighting
parameters}; any change is a version bump plus deliberate golden regeneration. Every experiment
verdict in `poc/` records this pin.

**What D = 8192 buys, in three layers:**

1. **Exactness floor:** 2^13 rows are needed for the 5+8-bit disjoint (slot, filler) space —
   below 8192 the within-clause algebra cannot be exact at all.
2. **Capacity headroom:** the VSA capacity literature (`reports/deterministic-concept-vectors.md`
   §1.2, §7.2 — Plate 1995; Frady/Kleyko/Sommer 2018; Thomas/Dasgupta/Rosing JAIR 2021) prices
   robust storage at ~0.2–0.5 bits per dimension. A capped explication carries ~2–4 kbit of
   structure (s ≈ 100–200 bound terms × log2 of the lexicon), so D ≈ 8k–32k sits inside every
   published bound, with constants. The 32-clause cap is the load-bearing assumption — capacity
   is linear in D, so structures beyond ~D/2 bound terms *must* collide or lose decodability.
3. **Measured margins:** on the authored 54-concept corpus, the *hardest adversarial single edit*
   (change one atom anywhere in any explication) still moves the vector 0.00234 radians — 11×
   the fp16 representation floor (X1). Margins survive projection to 512 dims at 10× floor (X4).

---

## 3. What the Phase-X measurements say (the honest quality card)

Pre-registered property tests (`docs/poc-design.md` Phase X), run on both synthetic corpora and
the authored kernel-v0 corpus (`poc/results/kernel-v0-phase-x-summary.md`):

| suite | question | authored-corpus result | verdict |
|---|---|---|---|
| **X0** | byte-determinism | golden vectors byte-identical | pass |
| **X1** | do adversarial single edits (the closest possible different concept) stay distinguishable? | min angle 0.002342 rad over 2,475 edit-neighbours; 11.0× the fp16 floor (bar: >5×) | **SUCCESS** |
| **X2** | can the full definition be decoded back out of the vector, given the kernel? | **51/54 exact**; the 3 failures (afraid, angry, sad) drop optional SP slots / misorder a referent under deep quote+operator nesting; synthetics passed 720/720, i.e. the authored corpus found a real gap the synthetic grid missed | **FAIL** vs the 100% bar (known, tracked) |
| **X3** | does similarity track meaning? | **No** — 13/79 meaning-*inverting* edits sit closer than the nearest pair of genuinely distinct concepts (`afraid`↔`sad` cos 0.9933); median cosine of an inverting edit 0.8976 | documented pathology → **cosine similarity on kernel vectors is banned downstream** |
| **X4** | does the geometry survive projection from 8192 to model-sized dims? | RDM Spearman 0.9718 (→512) / 0.9706 (→576); min margin still ~10× fp16 floor | **SUCCESS** |

Read X3 carefully because it is the deepest honest limitation: the *provable* similarity of this
construction is **structural overlap** (how many bound terms two definitions share — Thomas et
al. Thm 9/15), not semantic similarity. One deep NOT changes ~1/s of the terms, so it moves the
vector ~1% while inverting the meaning. This is a theorem-level property of all
superposition-based encoders, not a bug to be patched quietly; mitigations (polarity-aware
weighting via the `notBoost` hook, canonicalisation above the encoder, using the *decoded
structure* rather than the raw metric) are design work in progress. Consumers get identity
(exact, via the hash), decodability (given the kernel), and margins — they do **not** get a
semantic distance function for free.

---

## 4. The maintainer's question, answered directly

> *"Is there a way of having fixed starting vectors from the base 65 units, from which everything
> else is derived, to similar-or-better quality than sparq?"*

**Yes — and that is precisely what is already built and measured.** The 65 primes own Hadamard
rows 1–65 (fixed forever by a table, not by training); every other vector in the kernel is
*derived* from those plus the structural atoms by the deterministic algebra of §2 — XOR binding
within clauses, unitary convolution across depth, recursive folding of referenced concepts'
vectors, superposition. There is no second source of content: change nothing but a definition and
only the affected vectors move; change nothing at all and every byte is reproducible from the
spec.

**On "similar-or-better quality than sparq"** the honest comparison has two halves:

1. **On the axis sparq never had, it is not a comparison — it is a first.** sparq's deterministic
   lanes encode *individual literals and node features*; sparq's own design delegates everything
   compositional or semantic to trained components (its remote text-embedding API, or the
   research-grade DistMult/ComplEx trainer). `reports/sparq-estate.md` §6 "Missing entirely",
   item 1, is explicit: *nothing in sparq encodes nested structure into a vector; the recursive
   composition operator has no counterpart in the estate*. Construction B **is** that missing
   centre. So for "what does this concept *mean*, deterministically" the kernel does not beat
   sparq's number — sparq has no number.
2. **On measurable quality, the card is §3:** margins an order of magnitude above the
   representation floor (X1, X4 — with the fully deterministic guarantee sparq's trained lane
   cannot offer even in principle), decode 51/54 with a named, reproducible gap (X2), and a
   documented similarity pathology with a ban attached (X3). And one result sparq never attempted:
   the derived vectors carry model-relevant *content* — in E5/E9 (§7), adapters trained on true
   kernel vectors transfer to unseen concepts at ~2.3× chance while semantics-scrambled but
   structurally identical vectors recover only ~8% of that effect. The content of the derivation,
   not just its format, is doing work.

The trade sparq did not have to make: kernel similarity is structural, so anything downstream
that wants "how alike are these meanings" must go through decode-and-compare or a mitigated
metric, never raw cosine.

---

## 5. sparq, explained, and exactly how the kernel differs

### 5.1 What sparq is (accessible version)

sparq (`/home/ec2-user/css/kernel/sparq`, Rust; survey: `reports/sparq-estate.md`) vectorises RDF
*data* — nodes and literals in a knowledge graph — for search. Its signature idea is the
**partitioned row**: a node's vector is a sequence of typed, non-overlapping blocks ("lanes"),
each with a declared encoder and metric, self-described by a `SchemaHeader` so that using the
wrong metric on a block is a detectable error. The deterministic lanes:

- **Thermometer numbers:** a value like 30 becomes a bar-chart-like code (dimensions fill up
  monotonically as the value grows) so that L2 distance provably preserves numeric order —
  30 is nearer 31 than 70, across the whole range.
- **Enum codebooks:** closed value sets (`sh:in`) get one-hot slots plus a reserved "invalid"
  slot; membership is a slot match, *never* a cosine threshold.
- **QUDT unit normalisation:** a curated affine table (`value_SI = lexical·factor + offset`)
  maps every known unit to canonical SI; unknown/compound units fail closed (never assumed
  dimensionless); the quantity kind routes to its own block so a length never shares a lane
  with a mass.
- **Taxonomy lane:** a class's position in the `subClassOf` DAG becomes depth + a hashed
  ancestor-bag, so ancestry overlap is measurable; a measured "geometry gate" decides whether a
  hyperbolic variant is warranted; a disjointness oracle gives provably-safe candidate masking.
- **SHACL priors** turn shape constraints into per-predicate encoder choices; boolean/date lanes,
  deterministic verbalisation, fail-closed parsing throughout.

Alongside these sits the **trained relational lane**: what a node means *beyond* its declared
structure is delegated to an external trained text embedder or an opt-in KGE (DistMult/ComplEx)
trainer — explicitly research-grade, with zero committed benchmark numbers.

### 5.2 The precise difference

sparq answers "*encode this literal/feature, deterministically*". The kernel answers "*encode
this **definition**, deterministically*" — a nested, referent-bound, operator-scoped tree over a
closed 65-prime basis, folded recursively into one vector, where referenced concepts contribute
their own canonical vectors. That **recursive tree-composition operator over a closed prime
basis** is the novel centre; sparq supplies roughly the entire periphery (the estate survey's
one-line verdict, verbatim: sparq supplies the canonicaliser, row format, lane encoders, hashing
discipline and serving layer — "what it does not supply is the centre").

### 5.3 Reuse vs build-new (the programme's actual plan)

**Reused / to reuse from sparq** (`reports/sparq-estate.md` §6):
the partitioned-row `SchemaHeader` discipline with per-block metric tags (adopted wholesale by
the planned physics lane, §6 below); the exact closed-set/thermometer/taxonomy encoders (with
fit breakpoints pinned instead of data-fitted); the `.spqv` vector store + ANN/search/SPARQL
serving layer (with a small format fork: hash-keyed rows instead of dict-id-keyed, plus encoder
provenance in the header); the fail-closed and domain-separation discipline; `sparq-canon`
(RDFC-1.0) wherever an RDF projection is minted — though programme-side identity is now JCS-JSON
(§1). **Built new (done):** construction B itself — the composition operator, coreference
encoding, ordered-clause encoding, the decoder, the whole Phase-X property harness. **Still to
build:** the physics dimension lane as a typed block (§6), polarity-aware similarity, thermometer
inverse decoders.

---

## 6. How QUDT (physics) and Lean/Metamath (mathematics) were grounded

The mandate admits non-NSM bases where NSM is dishonest (physical units, foundational maths).
Both sectors follow the same posture: exact, closed, capped substrates inside the kernel;
external ontologies as **bridges, never as identity or values**.

### 6.1 Physics: meaning as an integer vector in Z^7 (`docs/design-physics-sector.md`)

A physical quantity kind's semantic backbone is its **dimension-exponent vector over the seven SI
base dimensions [T, L, M, I, Θ, N, J]** — force = [−2,1,1,0,0,0,0]. Multiplying quantities *adds*
vectors; powers scale them; two quantities are compatible iff their vectors are equal. This is
exact integer linear algebra: the one kernel sector whose semantic geometry is a *theorem about
the domain* rather than a constructed claim. A **unit** is an exact affine map to SI
(`value_SI = lexical·scale + offset`, scale/offset exact rationals — "5/9" is a fraction, never a
float; floats are a validation error). The seven 2019-SI defining constants (c, h, e, k_B, …) are
exact by fiat and live in the kernel; every *measured* constant is a world-layer fact and stays
out. The v0 corpus (`data/physics-v0/`, 83 records) dimension-checks all 10 defining relations
(F = m·a … E_k = ½mv²) with BigInt arithmetic, and its checker demonstrably *rejects* (a flipped
exponent trips 5 independent gates).

**QUDT's role: bridge and cross-check only,** via the sanctioned `bridgesTo` pattern. QUDT is the
one external ontology whose canonical object *is* ours — its dimension-vector IRIs
(`qkdv:A0E0L1I0M0H0T-2D0`) are mechanically derivable from our exponent vectors, and the
validator recomputes and byte-compares every asserted bridge IRI. But QUDT has documented
conversion-factor errors (Keil & Schindler 2018), so **no numeric content is ever imported from
it** — every definitional number is re-derived from the SI Brochure; the bridge asserts "this
record ↔ that IRI", nothing more, and unverified bridges are marked `asserted-unverified`,
fail-closed.

**Where it hooks into the vector: a planned typed block, not yet built** (design §1.2; follow-up
bead filed). The dimension lane will be one `dim-exponent/1` block of a physics concept's vector
— per-component thermometer codes over the pinned exponent range with profile-pinned breakpoints
(sparq's `NumericEncoder` with the fit-free adaptation), metric tag **L2 only** (cosine is
undefined at the origin, where every dimensionless quantity sits — the metric tag is
load-bearing), bound alongside the relational/explication part exactly as construction B binds
clause lanes. Two honesty notes carried in the design: the dimension map is deliberately
non-injective (torque ≡ energy, entropy ≡ heat-capacity, … — 31 kinds → 27 vectors, 4 declared
collision classes), so the lane alone can never be identity — the *relational* part (τ = r×F vs
W = F·d) is what separates the collisions; and dimension-checking is necessary, never sufficient
(E = m·v² dimension-checks; the ½ is invisible).

### 6.2 Mathematics: Metamath carries identity; Lean is annotation-only

- **Profile-M** (`docs/design-math-sector.md`): the identity substrate for foundational maths is
  Metamath/MM0-*shaped* — many-sorted FOL over a Peano core, canonical de Bruijn binding (names
  never enter records; alpha-equivalence becomes syntactic identity), closed capped grammar. The
  decisive property: Metamath statements are **canonical, context-free token strings** — a
  statement's meaning is fully determined by its tokens, no elaboration layer, which is what a
  content-addressed hash needs. The concept-hash machinery applies unchanged; **construction B
  generalises to profile-M by a codebook swap + valency-table swap — specified, deliberately not
  yet built** (v0 corpus: 39 records in `data/math-v0/`; a bulk Metamath extraction, math-mm
  2,998 records, awaits minting).
- **Lean/Mathlib** (`docs/design-lean-route.md`): examined and *rejected as an identity layer*
  for a principled reason — Lean's identity is modulo definitional equality (two byte-different
  terms can be kernel-equal; the same source elaborates differently across versions), so there is
  **no honest byte-boundary to hash**. Hashing source is provenance, not identity; hashing kernel
  terms is simultaneously too fine and unstable; canonicalising modulo defeq would put a
  typechecker inside the mint gate. So Lean enters as **`lean-ref/1` annotation-layer records**,
  anchored on `(mathlibCommit, fullyQualifiedName)`, `status: "formal-reference"`, **minting no
  `urn:concept:`/`urn:kot:` ids** — 315k+ Mathlib declarations as bridge targets and mapper
  material, connected to profile-M hashes by `sameConceptAs`-style signed annotations.
- **Where maths hooks into the vector: nowhere yet.** Profile-M's encoder variant is a specified
  follow-up; Lean records, being annotation-only, never touch geometry at all. One deflationary
  survey finding worth keeping in view (`design-math-sector.md` §1.5): LMs do arithmetic via
  learned magnitude/Fourier features over digit tokens — a frozen vector for `addition`'s Peano
  recursion has *no mechanistic route* to improving `37+58`; what math records buy is reference
  fixity and checkability, not calculation skill.

---

## 7. The hook-in seam: where kernel vectors could meet an LLM/LCM

The architecture portfolio (`docs/architecture.md` §4) stages the bets; the E-series
(`poc/e*/`, all runs pinned to encoder `40e8c8ba…`) supplies the current evidence. Status per
seam, most- to least-supported:

### 7.1 The adapter route — A2 (**empirically supported at toy scale; the best seam**)

Keep the kernel outside the model; train a *small* learned map (adapter) from kernel space into
the model's embedding space; the kernel stays fixed and canonical, the adapter absorbs each
model's idiosyncratic geometry. Precedent: E-BERT, Frozen, GraphToken (report
`reports/fixed-vectors-in-llms.md` §2, §5).

- **E5 (PASS):** SmolLM2-135M + adapter; 24 held-out "nonce" concepts never seen in adapter
  training. True-kernel adapters hit 0.43–0.51 on 5-way slot-filling (chance 0.2); adapters
  trained on *shuffled* kernel vectors sit at chance. Mean advantage +0.285, exact permutation
  p < 1e-6, all 5 seeds. Kernel *content* transfers to unseen concepts through a learned bridge.
- **E9-defl (PASS, the control that makes E5 meaningful):** a "deflated" kernel — same structural
  statistics, semantics scrambled — recovers only **8.2%** of the true-kernel effect
  (+0.023 vs +0.285). The signal is the semantic content of the explications, not the mere
  existence of consistent structured codes.
- **E2 (primary criterion met, correlational):** kernel geometry adds explanatory power over
  word2vec/WordNet/gloss-overlap baselines in the internal representations of 3/3 model families
  (partial Spearman, p ≤ 0.0003), above frequency-matched random-set ceilings. The designed
  geometry is *detectably aligned* with learned geometries — necessary groundwork for any seam.

### 7.2 The embedding-table seam — A1 (**not supported so far**)

Freeze kernel vectors (JL-projected per X4) directly as token-embedding rows and pretrain around
them. This is the strong original hypothesis, and both its kill-chain experiments came back
negative-to-null: **E1 INCONCLUSIVE** (kernel-frozen did not beat shuffled-frozen at the
pre-registered look; TOST could not exclude the effect either; the trained arms did not even beat
the untrained step-0 baseline on the cloze instrument) and **E4 tier-2 NULL** (concept-emission
essentially at chance, 2/250 vs 0/250). This matches the literature's prediction (models train
fine around arbitrary frozen rows and construct interpretation downstream — the frozen-glyph
result; `reports/fixed-vectors-in-llms.md` §1): **fixing a vector fixes a symbol, not its
meaning.** The seam is not closed forever (E7 scale-slope is the pre-registered decisive test,
$2–10k, gated on maintainer sign-off), but nothing currently supports it.

### 7.3 The SAE label-space route — A6 (**one pass, one failed replication; open**)

Frontier labs extract millions of learned interpretable feature directions with sparse
autoencoders — per-model, unstable, unlabeled. The kernel is the exact complement: stable,
versioned, definitional. A6 proposes kernel geometry as a canonical *label/coordinate space* for
SAE features. **E8 PASSED on the first family pair** (GPT-2 ↔ Pythia-160M: kernel coordinates
predicted cross-model feature correspondence beyond shuffled and permutation nulls, ρ ≈ 0.39,
p = 1e-4, all secondaries surviving Holm) but **did NOT replicate on the third family**
(SmolLM2-135M: both new pairs NULL) — with a named conservative-direction confound (the SmolLM2
SAE is an MLP-output-site dictionary vs residual-stream for the passing pair). Honest status:
promising, unreplicated, needs a site-matched third family before any claim.

### 7.4 The external-verifier seam — A5 (**deployable mechanics, benefit unmeasured**)

No injection at all: the kernel sits beside the model as content-addressed reference + decoder +
verifier. The model's concept-level output is decoded against the kernel (X2's 51/54 is exactly
this machinery, with its known gap) and checked — and in the physics sector the checker is
*exact arithmetic*, not another model's opinion (a model emitting "energy in newtons" is caught
by integer-vector comparison). The delta over ordinary RAG-with-citations is pinned in
architecture.md §4 A5 (machine-checkable versioned definitions, O(1) equality, ZK-compatible
commitments); the experiment that would measure it (decode-verify vs vanilla RAG, poc-design E9
phase 2) is pre-registered and **not yet run**. Kernel-kNN similarity uses stay banned pending an
X3 mitigation.

### 7.5 The dimension seam (cross-cutting)

Kernel-native D = 8192+ vs model d_model of hundreds: every seam crosses this via either the
**fixed, published JL projection** (X4: Spearman 0.972, margins ~10× floor at 512) or a learned
projection — and a learned projection *is* A2 by definition; using one while claiming A1 silently
changes the hypothesis (architecture.md §1.3, pre-registered and enforced).

---

## 8. Summary card

| question | answer |
|---|---|
| Fixed starting vectors for the 65 primes? | Yes — Hadamard rows 1–65, pinned by table, no training (`codebook.ts`) |
| Everything else derived from them? | Yes — XOR binding within clauses, unitary convolution across depth, recursive concept references, superposition (`encoder.ts`) |
| Deterministic? | Byte-identical across platforms; SHA-256-derived structure only; X0 goldens guard the one FFT caveat |
| Why D = 8192? | 2^13 exact rows for the (slot,filler) space — hard floor; capacity math wants 8k–32k anyway |
| Better than sparq? | Different axis: sparq has no deterministic *meaning* encoder at all (its own survey says so); the kernel builds the missing centre and reuses sparq's periphery |
| Measured quality | X1 11× floor SUCCESS · X2 51/54 FAIL (known gap) · X3 pathology → cosine banned · X4 projection SUCCESS |
| QUDT | Bridge/cross-check only (`bridgesTo`, values never imported); dimension lane Z^7, exact; **encoder block planned, not built** |
| Lean / Metamath | Lean = annotation-only `lean-ref/1`, mints no ids (no honest hash boundary); Metamath-shaped profile-M carries math identity; encoder variant specified, not built |
| Best-supported LLM seam | A2 adapter (E5 PASS, E9-defl content-specific, E2 aligned); A6 SAE open (1 pass / 1 non-replication); A1 embedding-table unsupported (E1 inconclusive, E4 null); A5 verifier mechanics ready, benefit unmeasured |
