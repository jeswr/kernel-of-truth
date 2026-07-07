# poc/e4 — E4 emission-test DATA prep

Prep for **E4 — emission / unseen-concept decode** (docs/poc-design.md E4
rev 2, MAJOR 6/7, BLOCKER 3, panel O7; bead `kernel-of-truth-73u`): the
1,054-concept vocabulary, kernel/control vector tables at d_model = 512,
the independently authored gloss set with its pre-published hash, the
two-tier holdout + compositional-split pre-registration, and the builder
that emits gloss→concept-token shards in poc/e1's format. The fine-tune/eval
runner that consumes all of this lives in `runner/` (bead
`kernel-of-truth-hkp`; see "Runner" below).

## Layout

| path | what |
|---|---|
| `harness/synthVocab.ts` | 1,000 seeded synthetic capped explications (generator = encoder synth v2; seed scheme documented in-file); gate-validated, dedup'd |
| `harness/vectorTables.ts` | all 1,054 concepts encoded at Bq@512 (pin `3492799e…`, FAIL CLOSED) → `inputs/vectors/kernel-d512.f32` + 5 seeded random tables + 5 shuffled derangements in the manifest |
| `harness/realizer.ts` | the gloss AUTHOR: AST-meaning → naturalistic English, 5 style profiles (register/syntax/lexis), total over the grammar |
| `harness/glosses.ts` | drives the realizer, enforces the gloss discipline mechanically, emits `inputs/glosses.jsonl` + `GLOSS-HASH.txt` + `inputs/gloss-report.json` |
| `harness/holdout.ts` | tier-1/tier-2 seeded selection, compositional split, statistical spec → `inputs/holdout-manifest.json` (THE pre-registration artifact) |
| `pipeline/build_emission.py` | gloss→concept shards in e1's uint16 format against a real e1 `vocab.json`; leakage gates fail closed |
| `smoke/` | CPU end-to-end data smoke (mock corpus → real e1 vocab builder → emission builder → independent assertions); evidence in `results/` |
| `test/e4prep.test.ts` | artifact gates: pin, AST validity/determinism, table hashes/norms/derangements, gloss disjointness + n-gram + distinctness + hash, manifest consistency |
| `runner/` | the E4 experiment runner: emission fine-tune of the E1 kernel-frozen model (3 arms, E1 freezing discipline), 1,054-way candidate-restricted eval, pre-registered stats + verdict, mock smoke (see "Runner" below) |

```bash
cd poc/e4 && npm install && npm test        # verify committed artifacts
npm run inputs                              # regenerate artifacts (DELIBERATE only — changes GLOSS-HASH)
bash smoke/run_smoke.sh                     # CPU data-pipeline smoke
# real data build (GPU box), against the E1 run's actual vocab.json:
python3 pipeline/build_emission.py --e1-vocab <e1out>/vocab.json --out <e4out>
```

## Design decisions bound to the pre-registration

- **Vocabulary (panel O7):** 54 authored kernel-v0 concepts + 1,000 synthetic
  explications = **1,054**. Synthetics are PURE PRIME structures (no
  conceptRef pool): referencing authored concepts would import
  corpus-attested surface forms into "zero-exposure" targets. Seed scheme:
  `e4/synth/<i>` (+ documented retry salt), sizes from `e4/size/<i>`
  (topClauses 1–4, depth 1–5).
- **Encoder pin (Common rule 2, path (i)):** kot-enc-Bq/1 @ D=512, hash
  `3492799e…` — same pin as poc/e1; generation fails closed on mismatch;
  every artifact is stamped. No decode-dependent claim runs on the Bq path.
- **Controls (Common rule 4):** shuffled = seeded derangements of the
  concept↔vector assignment (5 seeds, no fixed points, redraws recorded);
  random-frozen = N(0, 0.02²) i.i.d. per element, 5 seeds, Box-Muller over
  DetStream. Scale policy identical to e1 (`frozenScale` at load).
- **Two tiers (MAJOR 7):** tier-1 = 211 concepts (20%, stratified 11
  authored / 200 synthetic) held out of emission SUPERVISION; tier-2 = 10
  synthetic concepts with ZERO occurrences in any training text (emission
  builder asserts this on the emitted uint16 streams). Tier-2 is synthetic
  by construction so the E1 corpus is untouched.
- **Exposure lines:** "tokens still seen in corpus" is implemented for ALL
  tier-1 members via meaning-free carrier lines — emitted for train AND
  tier-1 concepts at the SAME per-concept count (20), so exposure carries no
  information about holdout status. Authored tier-1 members additionally
  have real E1-corpus exposure; the manifest records the classes.
- **Statistics (BLOCKER 3):** candidate set = the 1,054 concept tokens;
  chance top-1 = 1/1054 ≈ 0.095%, top-10 = 10/1054 ≈ 0.95% (the "10/|C|" in
  the spec). Primary: tier-2 top-1, kernel vs **shuffled-kernel** (the
  empirical chance floor), one-sided exact paired sign-flip permutation over
  5 paired seeds, α = 0.05; Fisher exact on pooled items is a Holm-corrected
  secondary. A control-floor check (shuffled inside the binomial CI of
  1/|C|) is pre-registered: a "positive" with a hot control is INVALID, not
  a result.
- **Compositional split:** feature set = frame + depth-1 clause skeletons of
  every clause node; a held-out concept "shares structure" iff all its
  features are attested in the train concepts' union (103 shared / 118
  novel). Reported descriptively per subset. **Positioning:** Palatucci
  et al. 2009 ("Zero-shot learning with semantic output codes") and Frome
  et al. 2013 (DeViSE) established zero-shot decode through label
  embeddings; both use LEARNED/distributional codes. E4's codes are
  training-free compositional explication encodings, and the novel-structure
  subset asks specifically whether emission generalises along the
  COMPOSITION of the code space — the part the classic setups do not test.
- **Emission format:** `<gloss tokens> ⟦emit⟧ <concept token> <eos>`
  (uint16, e1 conventions); eval items end at `⟦emit⟧`, scored over
  candidate ids only. The E1 vocab is extended (never modified): `⟦emit⟧` +
  1,000 synthetic `⟦c:e4-…⟧` rows appended; e1 code and inputs untouched.

## Gloss discipline (MAJOR 6) — what was done

1. **≥5 naturalistic paraphrases per concept** (exactly 5 × 1,054 = 5,270),
   generated from the MEANING of the explication AST by `realizer.ts` — 5
   style profiles varying register, syntax (adjunct fronting, clause-order
   flips where meaning-safe, direct vs re-anchored indirect thought quotes)
   and lexical choice (seeded).
2. **Target-lexicon disjointness, mechanical:** every gloss is run through
   the LIVE compiled mapper (`mapText`); any token mapping to the gloss's own
   target concept (abstentions count as hits) forces a seeded rewrite with
   the target's surface lemmas banned. First-pass collision rate: **5/5270 =
   0.09%** overall, **5/270 = 1.85%** over authored-concept glosses (all
   five were `part-of`, whose natural realization used "a part of…"; zero
   for synthetics, which have no mapper surfaces). Re-verified in tests.
   *Pre-registered interpretation:* disjointness is per-TARGET; full
   disjointness from the whole lexicon is impossible in naturalistic English
   (the prime exponents are "good/want/know/say/…").
3. **Independence from the deterministic renderings:** no gloss shares a
   contiguous run of more than 7 words with its concept's kernel-v0 `gloss`
   field (9 redraws needed; worst surviving run = 7 words). Gloss text is
   never used on the corpus side, and glosses were generated from the AST,
   not from e1's cloze frames or any encoder/decoder rendering.
4. **Hash before training:** `GLOSS-HASH.txt` (sha-256 of `glosses.jsonl`)
   is committed with this prep, BEFORE any training run exists;
   `build_emission.py` refuses to build from a gloss file with any other
   hash.

### Independent authorship — honesty notes (pre-registered caveats)

- The "independent author" is the E4 data-prep agent (Claude Fable 5,
  2026-07-07): the paraphrase rules in `realizer.ts` are its authorship,
  recorded there. This buys *procedural* independence — the gloss text is
  provably not derived from the explication renderings (n-gram gate), not
  copied from kernel-v0 glosses, and lexicon-disjoint at the target — but it
  does NOT buy what a genuinely second author would: the SAME agent lineage
  designed the encoder's grammar, the kernel-v0 explications and these
  paraphrase rules, so systematic stylistic/structural correlations between
  explication shape and gloss shape (clause order above all: glosses follow
  the AST's clause sequence) survive all mechanical gates.
- Consequence, stated before any run: a model could partially solve emission
  from CLAUSE-STRUCTURE regularities of the realizer rather than from kernel
  vector content. The kernel-vs-shuffled contrast is immune to this as a
  *confound* (both arms see identical glosses) — it can only inflate both
  arms equally — but it caps the external-validity claim: E4 tests decoding
  of frozen kernel content from realizer-English, not from free human
  English. A human-authored gloss sample for a subset of concepts is filed
  as a follow-up quality audit and would directly measure this gap.
- Present-tense normalization: the realizer renders temporal operators in
  the present ("dies earlier"); slightly stilted, uniform across arms.
- Degenerate synthetic ASTs (single minimal clause) yield legitimately tiny
  glosses ("I happen."); they make some synthetic targets near-ambiguous —
  equal for both arms, reported via the eval item metadata.

## Smoke status (mechanics only, committed evidence in `results/`)

Mock 60-story corpus → **real** `poc/e1/pipeline/build_data.py` (read-only)
built a schema-true 423-token vocab → `build_emission.py --smoke 30`
(2 seeds) → `check_smoke.py`: emission/exposure sequence shapes, tier-2
absence, no held-out token after `⟦emit⟧`, seed invariance of the emission
multiset, tier-2 eval coverage (10 × 5), vector-table sha/norm/derangement
verification — **PASS**. The 14% gloss-OOV rate is an artifact of the tiny
mock vocab; the real E1 vocab (8k over TinyStories) is expected to be far
lower — measured and recorded in `meta.json` at real build time.

## What the data prep does NOT do

- No model training or evaluation, no GPU use, no claims (that is
  `runner/`'s job, below).
- No modification to `encoder/`, `mapper/`, `data/kernel-v0`, `poc/e1`,
  `poc/e2`, `poc/gpu`, `docs/`, `reports/`.
- The tier-1 "seen in corpus" property for SYNTHETIC tier-1 members rests
  entirely on the exposure-line mechanism (they cannot occur in TinyStories);
  analyses must stratify authored vs synthetic tier-1 if corpus exposure
  matters to the question being asked.

## Runner (`runner/` — bead kernel-of-truth-hkp)

Consumes an E1 trainer work dir (READ-ONLY: `$E1_WORK/data` +
`$E1_WORK/ckpts`, poc/e1's own output layout) plus the committed prep
artifacts above (never regenerated) and runs the pre-registered E4 protocol
end-to-end:

```bash
bash runner/run_e4.sh mock     # CPU end-to-end machinery check (see below)
# full run: chained after the E1 grid on the SAME GPU box —
poc/gpu/launch-e1-pull.sh --with-e4        # one boot, E1 grid then E4
# or standalone on a box that already has /opt/e1work:
E1_WORK=/opt/e1work bash runner/run_e4.sh full
```

Pipeline: fail-closed pins (sha-256 of `inputs/glosses.jsonl` vs
`GLOSS-HASH.txt` AND the holdout manifest; `vector-tables-manifest.json` vs
the manifest's recorded sha — re-verified downstream by `build_emission.py`
and per-`.f32`-file by the fine-tuner) → `pipeline/build_emission.py`
against the REAL E1 `vocab.json` (the measured gloss OOV rate is copied into
results as `e4-data-meta-<mode>.json`) → `finetune_e4.py` (3 arms x paired
seeds) → `eval_e4.py` → `stats_e4.py` (verdict JSON + md quoting the
manifest's `statistics` strings verbatim).

Design decisions bound to the pre-registration (`finetune_e4.py` header has
the full statement):

- **Base model:** the E1 `kernel-frozen` **100pct** checkpoint of the SAME
  seed (Common rule 1 pairing), for ALL THREE arms — that is the manifest's
  "E1 kernel-frozen model + ..." arm definitions.
- **Vocab surgery:** V→V+1001 per `e4-vocab.json` (EMIT + 1000 synthetic
  rows appended); everything else copied bit-exact; appended rows init
  N(0, 0.02²) from a seed-paired arm-independent generator; then the 1,054
  concept rows are set per arm from the tables (kernel/shuffled ×
  `frozenScale` at load per the manifest `scalePolicy`; random raw) and
  FROZEN with poc/e1's full discipline (wd-exclusion, grad-zero
  optimizer-state masking from step 0, bit-identity assertion at every
  check; violation crashes the run).
- **Kernel arm continuity:** the 54 authored rows are KEPT from the E1
  checkpoint and the table-derived rows are asserted bit-equal to them
  (fail closed; `--authored-row-tol` relaxes to a RECORDED deviation).
- **Shuffled arm consequence (stated before any full run):** the manifest's
  derangement spans all 1,054 ids, so the 54 authored rows are ALSO deranged
  — the shuffled model's authored rows differ from the rows the E1 base was
  trained around. Identical glosses, content-free assignment: that is what
  makes it the EMPIRICAL chance floor; the control-floor validity check
  guards the readout.
- **Fine-tune budget/LR (runner-level, arm-symmetric):** fixed 10M tokens,
  lr 1e-4, batch 64 @ seq 256, identical across arms — arms differ only in
  frozen-row CONTENT, so this cannot confound the kernel-vs-shuffled
  contrast. Recorded in every summary json.
- **Stats:** exactly the manifest `statistics` block — 1,054-way candidate
  restriction, tier-2 top-1 primary (one-sided exact paired sign-flip,
  reused READ-ONLY from `poc/e1/eval/stats_e1.py`), tier-2 top-10 +
  tier-1 top-1/top-10 Holm secondaries, per-seed one-sided Fisher exact on
  pooled items (Holm over seeds), compositional shared/novel splits
  descriptive only, exact-binomial control-floor validity check (a
  "positive" with a hot control is emitted as INVALID), MAJOR 16 advance
  rule quoted in the verdict.

### Runner mock-smoke status (mechanics only, committed evidence in `results/`)

`run_e4.sh mock` (2026-07-07, CPU, niced, disposable venv): generated a mock
E1 checkpoint pair with poc/e1's OWN trainer (tiny d=64 config, 2 seeds,
mock corpus — poc/e1 code untouched), built the emission shards with the
real builder (`--smoke 30`, gloss pin verified, OOV 14% = known mock-vocab
artifact), fine-tuned 3 arms x 2 seeds under the freezing mask, evaluated,
and emitted `results/verdict-e4-mock.{json,md}` (MOCK-labelled). Independent
assertions (`runner/check_smoke.py`, `results/runner-smoke-log.txt`): 6,324
frozen-row bit-identity comparisons — all 1,054 frozen rows equal the
table-recomputed expectations bit-exactly through emission fine-tuning, the
kernel arm's 54 authored rows bit-identical to the E1 checkpoint through the
vocab surgery AND the fine-tune, EMIT + non-frozen rows actually trained,
tier-2 eval coverage complete — **PASS**.
