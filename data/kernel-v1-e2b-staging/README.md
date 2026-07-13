# kernel-v1-e2b-staging — E2b inventory-extension STAGING corpus

**Status: STAGING ONLY (pre-adoption). 22 sense concepts over 10 lemmas
(add / bring / conduct / cry / fight / leave / produce / run / shape / sing),
authored 2026-07-13 for the ENGINE-INF E2b design
(`docs/next/design/engine-inference-under-typing.md` §E2b; maintainer-approved
issue #29; assumption block
`poc/engine-inference/asm-e2b-2250-2259.json`).**

This directory is an experiment-scoped **extension CANDIDATE** for kernel-v1
Stage A. It is NOT part of kernel-v1: `data/kernel-v1/` and its frozen
surface proof are untouched; no encoder file, ALGORITHM_VERSION, or X0 golden
changes here (the build asserts the encoder pin READ-only against kernel-v0's
frozen value). Adoption into the confirmatory instrument is a maintainer
decision that follows the #29 anomaly-gold construct sign-off.

- **Scope is mechanical:** the minted lemmas and synsets are exactly the
  output of the pinned E2b-SEL selection rule
  (`poc/engine-inference/e2b-inventory-extension/e2b_select_lemmas.py` →
  `e2b-selection.json`); the build fails closed if the concept set drifts
  from the selection (SCOPE gate). Per lemma: every VN-restricted synset
  passing the frequency filter, plus the within-lemma sortal-contrast sense.
  The explication CONTENT is authored (research-grade, profile-1), like
  Stage A — a disclosed authoring act, not a mechanical output.
- **A concept is a sense, not a word** (ASM-1884). Every concept carries a
  `sense` block; every lemma has a `sense-index/` record with the FULL
  `excludedSenses` closure (R4/R5: nothing silently dropped).
- **Every verb sense is an EVENT**: `typing/ck-ufo-sidecar.jsonl` assigns
  `ontic_category: "event"` to all 22 concepts — the Stage-A
  "a breakage, in any sense, is an event" maintainer clause, generalized and
  enforced by the build.
- **Identity minting is deferred**: ids here are alias URNs
  (`urn:kernel-v1e2b:<lemma>.<senseTag>`). `urn:kot:` identity hashes are
  minted by the adoption build (the Stage-A path, coordinator custody).
  Every explication already passes the encoder's `validateExplication` and
  one `encodeConceptSet` pass (ENC gate), so adoption is a re-mint, not a
  re-authoring.
- **FrameNet licensing deferred**: `framenetFrame` is null pending the
  adoption build's R2 frame-licensing gate (the break.interrupt null
  precedent).
- **Holdout custody**: none of these lemmas has ever been extracted into any
  seen frame (they are outside Stage-A, outside the PC-6 decoys, and outside
  the kernel-v0 panel — enforced by E2b-SEL filter F1), so every cell they
  will generate in the E2b re-extraction is fresh by construction; outcomes
  are unknown at freeze.

Build/verify: `node build-e2b-staging.mjs` (fail-closed gates: ENC, SCOPE,
G1/G2, R1 recount, ONTIC event rule). No feasibility conclusion is stated or
implied by anything in this directory.
