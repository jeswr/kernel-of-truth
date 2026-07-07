# kernel-v0 — the explicated-concept corpus

54 concept explications in the `kot-ast/1` JSON AST (the typed mirror of the
profile-1 explication grammar, concept-hash-design.md §4), authored to exercise
the kernel encoder and the Phase-X experiment suites.

## What this is — and is not

**Research-grade, agent-authored against profile-1; NOT federation-endorsed;
adequacy unvalidated.** These explications exist to exercise the encoder and
experiments, not to claim NSM adequacy. Every record passes the encoder's
fail-closed grammar/valency/referent/caps gates (that bar is hard), but whether
any explication adequately captures its concept is a judgement no one has made:
no federation has endorsed these records, no NSM practitioner has reviewed
them, and the gist itself says adequacy is "social, not proven"
(concept-hash-design.md §1 claim 3). Known-weak explications say so in their
per-concept `notes` field (`KNOWN-WEAK:` prefix; ids listed in
`manifest.json#knownWeak`) rather than pretending polish.

Concept ids (`urn:kernel-v0:<slug>`) are **placeholder URNs**, not
content-address hashes — minting real `urn:concept:` identities is the
concept-hash pipeline's job, out of scope here.

## Contents

- `concepts/*.json` — one concept per file: `{id, label, status, pattern?,
  gloss, notes?, references, explication}`. The `explication` field is the
  kot-ast/1 record the encoder consumes; `references` lists the kernel-v0 ids
  whose canonical vectors the encoder binds for this record (recomputed and
  cross-checked by the harness).
- `manifest.json` — schema version, counts by frame, the reference-bearing
  subset, max reference depth, known-weak ids, and the encoder content-hash
  the corpus was validated against.
- `../validate.mjs` — the validation harness: per-concept
  `validateExplication`, a whole-corpus `encodeConceptSet` (reference DAG,
  cycles fail closed), vector sanity, manifest cross-checks. All 54 must pass.

## Shape

- **Frames:** 17 InstanceSchema, 16 WhenTrue, 21 RelationalSchema.
- **Walkthrough concepts** (translated from the gist): `event` (§3.3 record,
  verbatim), `archived` (§3.4 record, verbatim modulo two noted AST
  adaptations), `bookmark` (§3.4 pattern description), `kind` (§3.3 sketch —
  the gist marks the full record non-normative; ours is research-grade).
- **Reference structure:** 18 concepts reference other kernel-v0 concepts (the
  encoder binds the referenced vectors); the deepest chain is
  `condolence → grieving → death → event` (depth 3). No cycles.
- **Recurring authoring patterns** (from the gist): maker-coreference for
  ownership (§3.4), creation as `BECAUSE(cause: DO, effect: THERE-IS)` (§3.4),
  quote re-anchoring for first-person primes — IS-MINE/WANT on behalf of third
  parties (§4.6), kind-frame heads over concept refs for class membership
  (§4.3), bound-referent vs fresh-SP for same/some distinctions (§4.2).

## Validation

```sh
(cd encoder && npm install && npm run build)   # once
node data/validate.mjs                         # works from any cwd
```

Exit 0 iff every concept passes every gate and the whole corpus encodes.
