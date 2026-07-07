# @jeswr/kernel-encoder

Kernel of Truth **encoder v0**: a deterministic, training-free
explication → vector encoder (construction B of
[`reports/deterministic-concept-vectors.md`](../reports/deterministic-concept-vectors.md) §7.3;
spec in [`docs/architecture.md`](../docs/architecture.md) §1), with the matching
decoder, a content-hash version pin, the profile-1 65-prime lexicon as data,
and a seeded synthetic-explication generator for the Phase-X property suites.

## What it does

- **Explication AST** (`kot-ast/1`): a typed JSON mirror of the profile-1
  explication grammar (concept-hash-design §4) — 65-prime lexicon with
  categories and chart indices, closed predicate valency frames, closed
  operator inventory with arities, three explication frames, indexed
  discourse referents with binding, substantive phrases, concept references
  by id. Caps enforced fail-closed: ≤32 clauses, ≤32 referents, depth ≤12.
- **Encoder** (`encodeExplication`): two-level TPR/VSA construction —
  - *within a clause*: exact binding over an exactly orthonormal
    Sylvester–Hadamard codebook (bit-partitioned XOR row indexing ⇒ every
    (slot, filler) pair is a unique orthogonal row; zero crosstalk);
  - *across clauses/depth*: unitary circular-convolution binding (HRR with
    unit-magnitude quarter-phase spectra, own radix-2 FFT) behind a
    deterministic spectral whitener, plus deterministic position
    permutations and superposition with pinned weighting parameters;
  - concept references bind the referenced concept's canonical vector
    (`encodeConceptSet` = memoised recursive encoding; cyclic references
    fail closed).
  - D configurable (power of two ≥ 8192; default 8192). No seeds anywhere:
    all derived structure comes from SHA-256 over fixed labels. Same input ⇒
    byte-identical `Float64Array` across runs and platforms.
- **Decoder** (`decodeExplication`): recursive unbinding + nearest-neighbour
  cleanup against a supplied kernel lexicon, matched filtering over the
  closed grammar, reconstruction peeling with a few global refinement
  passes; per-step confidence reported. Recovery is always *given the
  kernel* (codebook + lexicon are the cleanup memory).
- **Content hash** (`encoderContentHash`): sha-256 over the canonical
  serialisation of {schema version, algorithm version, D, codebook table,
  weighting params, derivation domain} — the pin required by
  poc-design Common rule 2.
- **Synthetics** (`generateExplication`, `mutateExplication`): explicit-seed
  deterministic generator over valid capped explications with controllable
  depth/clause-count, plus a validity-preserving single-edit mutator
  (operator flip / clause swap / referent-index change / filler
  substitution) for the X1 adversarial suite.

## Usage

```ts
import {
  encodeExplication, decodeExplication, encoderContentHash,
  generateExplication, mutateExplication,
} from '@jeswr/kernel-encoder';

const ast = generateExplication({ seed: 'demo', topClauses: 3, depth: 2 });
const v = encodeExplication(ast);            // Float64Array(8192), unit norm
const back = decodeExplication(v);           // { explication, ok, steps, minConfidence }
console.log(encoderContentHash());           // pinned encoder version
```

## Toy-native variant `kot-enc-Bq/1` (D ∈ {512, 576})

A SEPARATE pre-registration (own `ALGORITHM_VERSION_Q` + content-hash per D
via `encoderContentHashQ`) implementing architecture.md §1.3 dimension-policy
path (i): the kernel re-encoded natively at the host model's `d_model`
(512 = E1 toy, 576 = SmolLM2-135M) for the E1/E4 "structure-derived content
vs content-free at matched D" question — explicitly NOT the capacity story.

- Same AST → vector pipeline (`InternalEncoder` shared verbatim): whitened
  unitary circular convolution, position permutations, pinned weighting.
  D = 576 runs the convolution on a Bluestein chirp-z FFT (fft.ts).
- The exact Hadamard codebook needs 13 index bits (D ≥ 8192), so the variant
  substitutes a **quasi-orthogonal** deterministic codebook: independent
  Rademacher ±1/√D atoms per (slot, filler) from SHA-256 label
  `qatom/<D>/<slotId>/<fillerId>` — design decision, rejected alternatives,
  and what is lost (exact unbinding; zero crosstalk floor) documented in
  `src/codebookQ.ts`; coherence certified offline by `poc` `npm run cert:q`.
- Entry points: `encodeExplicationQ`, `encodeConceptSetQ`,
  `decodeExplicationQ` (decode is measurement-only at this D — see the
  ungated X2-q report). Non-pre-registered dimensions fail closed
  (`ERR_QUASI_DIMENSION`).
- Variant Phase-X: `npm run x0:q / x1:q / x2:q / x4:q / cert:q` in
  [`../poc`](../poc), goldens in `poc/fixtures/golden-vectors-q.json`.

## Determinism contract

- Float64 `+ − × ÷` and `Math.sqrt` are IEEE-754 exact; all superposition
  loops run in a pinned traversal order (part of `ALGORITHM_VERSION`).
- The only transcendentals are `Math.cos`/`Math.sin` in the FFT twiddles;
  Node/V8 implements them in portable software (fdlibm port), bit-identical
  across OS/CPU for a given engine. The committed X0 golden vectors are the
  operational cross-platform witness.

## Test

```sh
npm test   # builds + runs the node:test property suites
```

Phase-X harnesses (X0–X4, pre-registered in `docs/poc-design.md`) live in
[`../poc`](../poc).

MIT © Jesse Wright
