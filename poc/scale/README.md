# poc/scale — SCALE-1 S0 first rung (10k pilot)

**Epistemic status: exploratory engineering pilot.** First increment of the
large-kernel SCALE-1 track (`docs/next/design/large-kernel-scale-track.md`,
stage S0 of §8). It qualifies machinery and measures design predictions at the
10k rung. It is **not** a pre-registered Phase-X harness, **not** an encoder
version change (the kot-enc-B/1 pin and goldens are untouched), and it issues
**no feasibility conclusion** (design §14: CORRECTNESS and EFFICIENCY remain
INCONCLUSIVE-PENDING).

## Pipeline (all deterministic + checkpointed; nice -n 10; 2 shared cores)

```bash
cd poc
npm run scale:ingest   -- --n 10000   # (1) top-frequency WordNet 3.1 subset
npm run scale:typing   -- --n 10000   # (2) CK-UFO sidecars + imported-vs-inferred split
npm run scale:vec      -- --n 10000   # (3) kot-enc-import/0-poc vectorisation (resumable chunks)
npm run scale:metrics  -- --n 10000   # (4) margins/RDM/storage/cost vs design predictions
npm run scale:vec:verify -- --n 10000 # determinism byte-check (chunk 0 of every store)
```

Run the **1k smoke first** (`--n 1000`) on a fresh box to confirm tractability.

## Stages

1. **ingest** — top-N synsets by summed SemCor `tag_cnt` from the pinned
   `index.sense` (source-provided frequency; disclosed bias: 1990s balanced
   corpus). Pure function of the pinned WordNet 3.1 extraction + N.
2. **typing** — design §4.1 cascade. WordNet asserts NO native UFO structure
   except the instance flag; everything else is pinned-rule inference
   ([STIPULATED] lexFile crosswalk + anchor closures) or `underdetermined`.
   The split is reported per field.
3. **vectorise** — `kot-enc-import/0-poc`: an exploratory instantiation of
   design §6.3 (SHA-256 Rademacher token atoms via the encoder's DetStream,
   one synchronous neighborhood round, sign-diagonal relation binding — zero
   FFTs). Stores: `canon8192` (canonical fp64 arithmetic, fp32 persisted),
   `proj512`/`proj576` (X4 Achlioptas JL, byte-identical stream labels to
   `poc/harness/x4.ts`), `native512`/`native576`, and `native512lex`
   (optional §6.2 lexical block probe). Construction B is NOT used here:
   AxiomsOnly records have no profile-1 AST and the import graph has cycles
   (design §6.1) — that is the point of the separate import vectoriser.
4. **metrics** — full O(n²) NN margin pass with per-pair structural
   classification (edge / shared-target / shared-lexFile vs disjoint) compared
   to the §6.5 `√(2·ln m / D)` Gaussian-crosstalk curve; duplicate censuses
   (structural token-multiset AND vector); X4 RDM-Spearman re-measure plus
   top-pair Spearman and NN recall@1/@10 decomposition; encode-cost and
   storage tables with 100k/1M [EXTRAPOLATION] rows.

Results land in `poc/scale/results/scale-s0-n<k>-report.{json,md}`;
intermediates and checkpoints under `poc/scale/out/n<k>/`.

ASM candidates for the coordinator are in `poc/scale/asm-1780-1789.json`
(free range checked against `registry/assumptions.jsonl`; this directory does
NOT write the registry itself).

## Next rung: S1 (100k) increment 1 — multi-source census (built 2026-07-13)

The first S1 increment is a **multi-source concept census + UFO-typing-yield
probe** over the local WordNet ∪ OBO ∪ SUMO shards — the cheapest measurement
that retires the two rung-gating S0 blockers before any 100k build:

```bash
cd poc
npm run scale:census   # reads data/{lexical-wn31,onto-obo,onto-sumo}; ~2.6 s, $0
```

Outputs `poc/scale/results/scale-s1-census.{json,md}`. It measures **yield, not
precision** (the §4.3 human audit is a later step). Design + staged plan:
`docs/next/design/scale-s1-multisource-census.md`. ASM candidates:
`poc/scale/asm-2050-2059.json` (ASM-2050..2055). Headline measured facts: the
union has >100k type-level headroom (retires §2.3 selection-rule exhaustion),
and OBO/SUMO give nonzero source-asserted-ontic (56.7%), identity-provider-
candidate (25.9%) and dependence-candidate (49.1%) yield where WordNet-only gave
0% (retires §2.1 as an evidential-path gap). Next cheap increments: load
per-ontology BFO bridges + SUMO↔WordNet mapping (step 2), add a Wikidata class
subset for domain balance (step 3) — both re-run this same script.
