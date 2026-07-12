# kernel-v1 — Stage A (sense-split-first construction)

**Status: Stage-A subset ONLY (11 sense concepts over break/make/find/friend),
built 2026-07-12 per `docs/next/design/sense-split-first-construction.md`
(maintainer sense-split requirement ASM-1884; Stage-A GO ruling ASM-1909;
build assumption block `asm-stageA-1910-1929.json`, owner writer-4).**

A kernel concept is a **sense**, not a word. Every concept here carries a
`sense` block (senseTag, WN31 synset cluster, FrameNet frame, gloss quote —
all annotation, outside identity); every lemma has a `sense-index/` record
listing minted senses **and the full `excludedSenses` list** (R4 scope
closure: a concept claims its synset cluster, not the word).

- Minting: same identity function as kernel-v0 (`kot-ast/1` header + JCS +
  sha256 → `urn:kot:`), proven unchanged by re-minting the frozen v0 concepts
  (see `manifest.json .continuityChecks`). Alias URNs: `urn:kernel-v1:<lemma>.<senseTag>`.
- Gates (fail-closed, `build-kernel-v1-stageA.mjs`): R1 recount, R2 frame/LU
  licensing, G1 no-shared-identity, G2 no-unacknowledged-polysemy, R4 count
  checks, ERR_BREAK_NOT_EVENT (every break.* is an event), ERR_PI011_CLASS_REMINT
  (break.violate range can never anchor at material entity), ERR_ENCODER_PIN.
- Typing: `typing/ck-ufo-sidecar.jsonl` (per-sense ontic category, annotation)
  + `typing/soft-type-per-sense.jsonl` (30 rank-only, binding:false records).
- kernel-v0 is **frozen forever** and untouched; the four v0 word concepts are
  superseded for new consumers only (`manifest.json .supersedes`).
- Validation harness: V-A/V-B under `poc/sense-split-stageA/` (launch-ready,
  HELD — no judgments spent).

Rebuild: `node data/kernel-v1/build-kernel-v1-stageA.mjs` (deterministic;
regenerates manifest.json, minted-urns.jsonl, sense-index/).
