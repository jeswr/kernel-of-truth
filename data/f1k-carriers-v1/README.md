# f1k-carriers-v1 — carrier GENERATOR components (PRE-SPEND; NOT the B0 pin)

Target pin: `registry/experiments/f1k.json` `f1k-carriers-v1` ("realized
carrier tables for every arm (K, 3 derangements, d0, d2) + raw and rescaled
norms — the B0 pure-function addendum (SSR-REV3.3); kot-corpus-hash/1
pinned AFTER construction, BEFORE the pilot"). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — 2026-07-13 designer-23 data-construction pass ($0).

**The realized tables CANNOT exist in this pass, by the frozen ordering
itself:** they are mean differences of GLM-5.2 forward-pass hidden states
(DES §2.4) — i.e. construction SPEND — and the record orders them as the
(B0) addendum committed after construction. This directory therefore holds
ONLY the deterministic, model-independent generator components, so that at
construction time every arm's table is a pure function of frozen rules:

- `generator/derangements.json` — the REGISTERED seeds (pilot 11; main
  101/102/103 = `design.seeds`) realized as fixed-point-free permutations
  over the 49 carrier slots (the concepts present in the frozen test/dev
  spans, SSR2), via the run driver's algorithm (OP-7).
- `generator/carrier-index-map.json` — carrier slot ↔ kernel concept map
  (the KAEC concept-major axis; eval spans use these slots).
- `generator/concept-texts.jsonl` — per concept: the kernel explication
  text (kernel-v0 `gloss`, hashed) for K/d3-text, and the plain-dictionary
  text (aligned WN3.1 synset gloss, hashed) for d2 — freeze-(A)(ii).
- `generator/construction-contexts.jsonl` — OP-8 DRAFT: m = 16 verbatim
  WordNet-authored contexts per concept, checked disjoint from every eval
  item (DES §2.4).
- `generator/generator-spec.json` — the §2.4/§R2 formulas + protocol, with
  every model-dependent input explicitly marked BLOCKED.

**Still missing for (A)/(B0), never invented here:** the construction seed
VALUE (named at freeze_manifest A(vii), no value registered anywhere); the
d0 direction-generation algorithm; the exact candidate splice-layer ids
(model config, bring-up); the mean native expert weight for the g grid;
and the realized tables + raw/rescaled norms themselves. The
kot-corpus-hash/1 digest of this directory at THIS pass is NOT the B0 pin.
