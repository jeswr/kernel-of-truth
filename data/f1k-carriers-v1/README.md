# f1k-carriers-v1 — carrier GENERATOR components (96 slots; PRE-SPEND; NOT the B0 pin)

Target pin: `registry/experiments/f1k.json` `f1k-carriers-v1` ("realized
carrier tables for every arm (K, 3 derangements, d0, d2) + raw and rescaled
norms — the B0 pure-function addendum (SSR-REV3.3); kot-corpus-hash/1
pinned AFTER construction, BEFORE the pilot"). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — 2026-07-15 fable REVISION-6 data-construction pass ($0).
**supersedes the 2026-07-13 designer-23 kernel-v0-only pass (49 clusters, n=1440) — REVISION-6 frozen geometry C=96 / n_test=1573, maintainer-approved 2026-07-15.**

**STILL NOT THE B0 PIN.** The realized tables are mean differences of
GLM-5.2 forward-pass hidden states (DES §2.4) — construction SPEND — and the
frozen ordering commits them as the (B0) addendum after construction. This
directory now holds the **96-slot (A)-time deterministic generator
components** at the REVISION-6 geometry, so that at construction time every
arm's table is a pure function of frozen rules:

- `generator/derangements.json` — the REGISTERED seeds (pilot 11; main
  101/102/103 = `design.seeds`) realized as fixed-point-free permutations
  over the **96 carrier slots** (the frozen selected concepts, slot =
  askability rank - 1), via the run driver's algorithm (OP-7).
- `generator/carrier-index-map.json` — carrier slot ↔ concept map in
  selection-rank order (the KAEC concept-major axis; eval spans use these
  slots).
- `generator/concept-texts.jsonl` — 96 rows: the kernel explication text
  (K/d3-text) and the plain-dictionary text (d2), VERIFIED BYTE-IDENTICAL at
  build to the certified pinned pair corpus
  `data/f1k-contrast-v1/<rank>-<slug>/{kernel.txt,dictionary.txt}`
  (kernel.ast.json also re-verified) — freeze-(A)(ii).
- `generator/construction-contexts.jsonl` — OP-8 DRAFT: m = 16 verbatim
  WordNet-authored contexts per concept (1,536 rows), checked disjoint from
  every eval item (DES §2.4).
- `generator/generator-spec.json` — the §2.4/§R2 formulas + protocol, with
  every model-dependent input explicitly marked BLOCKED.

**Still missing for (A)/(B0), never invented here:** the construction seed
VALUE (named at freeze_manifest A(vii), no value registered anywhere); the
d0 direction-generation algorithm; the exact candidate splice-layer ids
(model config, bring-up); the mean native expert weight for the g grid;
and the realized tables + raw/rescaled norms themselves. The
kot-corpus-hash/1 digest of this directory at THIS pass is NOT the B0 pin.
