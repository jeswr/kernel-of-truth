# Canonical hash-input form for kernel minting (coordinator decision, 2026-07-07)

**Status:** decided for programme-side minting; **held open for PSS input** on the estate-interop question before any cross-estate identity claims. Implements design-review change 2 (`notes/panel-kernel-design-review.md`), which blocks bulk minting (bead arq) until this exists.

## Decision

Programme-side concept identity is computed over **UTF-8 NFC + RFC 8785 (JCS) canonical JSON** of the record's *identity payload* — the same JSON ASTs every validator, encoder, and experiment in this repo actually computes over — hashed per the concept-hash design's multihash/multibase conventions with a profile-header-in-digest (`kot-<profile>/<version>\n` prefix, mirroring gist §6's in-band profile discipline). The RDF serialisation becomes a **projection**: derivable from the JSON record, published for estate interop, never the hash input on the programme side.

Identity payload = the record minus its annotation block (labels, glosses, notes, provenance-of-extraction stay outside identity, matching gist §3's D1 boundary exactly). Reference URNs inside payloads follow the gist's reference discipline; cyclic-SCC handling adopts the gist §6 ordering-key algorithm unchanged (it is serialisation-agnostic).

## Why (the review's argument, accepted)

1. Every artifact that *computes* — validators, encoder, Phase-X, E-series pins, all six bulk extractors — operates on the JSON ASTs. Hashing a different serialisation than the one computed over reintroduces the exact validator/decoder-disagreement class of bug the corpus X2 failure exposed, at the identity layer, where it would be unrecoverable.
2. The RDF path's complexity is self-inflicted for our purposes: rdf:List spines, bnode-tree discipline, the duplicate-FDH gate, and a prototype with nine recorded deviations exist to make *RDF graphs* canonicalise safely — a problem we do not have when the native form is a tree with deterministic key order. JCS is a small, testable spec.
3. Nothing semantic is lost: the D1 boundary, semantic-status ladder, caps, profile-header discipline, SCC handling, and multihash agility all carry over unchanged. This is a change of *bytes*, not of model.

## What this does NOT decide (PSS's turf, explicitly reserved)

The concept-hash design (gist) remains the estate's RDF-native identity scheme with a working prototype. Two paths forward, PSS to weigh in on #1683:
- **(a) Dual-hash bridge:** programme records carry both `kot` (JCS) URNs and, where an RDF projection is minted through `@jeswr/concept-hash`, the gist URN — linked by `sameDefinitionAs` annotations (mechanically checkable, the gist §8 device).
- **(b) Convergence:** the gist adopts a JSON-native profile variant (its §8 permissionless-profile mechanism makes this a new bundle, not a breaking change).

Until resolved, programme URNs use the `urn:kot:` namespace (never `urn:concept:`) so no cross-scheme collision is possible.

## Consequences

- Unblocks bulk minting (arq): real content-addressed ids for math-mm (2,998), physics-qudt (3,070), lexical-wn31 (117,791), onto-* (in flight), haiku-tier (gated) — a minting pass per corpus, JCS + sha2-256, manifest-recorded.
- The snapshot-pack distribution (bead 6j5) packs JCS bytes; verification = re-canonicalise + compare, no RDF toolchain required by consumers.
- Encoder/experiment pins are untouched (they never depended on record identity bytes).
