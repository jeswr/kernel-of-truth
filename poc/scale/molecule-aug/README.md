# molecule-aug — reference-lexicon-augmented AST generation (strategy S5)

**DESIGN ONLY.** No prereg-freeze, no run, no commit, no encoder change. Every
choice is STIPULATED-not-MEASURED unless a measured artefact is cited by path.
Author: fable (lead designer); the coordinator owns all runs and all judging.

Tests whether letting the concept-def generator compose from a referenceable
concept lexicon (65 primes + `data/kernel-v0/` 54 + 31 authored bridge concepts)
reduces AST-lossiness vs the flat 65-prime baseline, on the same concepts, under
the `poc/scale/ast-pipeline/` blind cross-vendor judges.

| file | what |
|---|---|
| `DESIGN.md` | the experiment: arms, lexicon, endpoint, stats, cost, ALGORITHM_VERSION analysis |
| `lexicon/PLAN.md` | the 31 bridge words (mined from consensus-100 lossy notes), authoring order, briefs, gates |
| `ref-addendum.md` | generation-prompt delta (composed with the unmodified base prompt at gen time) |
| `judge-addendum.md` | judge-prompt delta (reference semantics; applied to ALL candidates in a run) |
| `validate-record-ref.mjs` | S5 mechanical gate: pinned gate + lexicon-resolved `encodeConceptSet` (smoke-tested) |
| `mine_lossy.py` | reproduces the lossy-note mining evidence (§3.1 of DESIGN.md) |
| `lexicon/records/*.json` | **BUILT** — the 31 bridge records, all gate-green (13 faithful / 18 lossy self-flags); provenance in `lexicon/AUTHORING.md` |
| `lexicon/build_manifest.mjs` | **BUILT** — 85-id manifest + `lexiconSetHash` + encoder-pin check + eval-slug anti-leakage gate + `listing.txt` |
| `lexicon/manifest.json`, `lexicon/listing.txt` | **BUILT** — pinned lexicon snapshot + the 85-line prompt listing (regenerate only via build_manifest) |
| `run_s5.py` | **BUILT** — compose/sample/gen/prep/judge/score/dryrun/selftest driver (offline selftest green, 16/16) |
| `s5-prompt.md`, `s5-judge-prompt.md`, `compose-manifest.json` | **BUILT** — composed prompts + hash pins (from `run_s5.py compose`) |

**Delta vs DESIGN §8's command sketch (disclosed):** S5 judging runs as
`run_s5.py judge --stage N --judge A|B|T --i-am-the-coordinator`, NOT via
`../ast-pipeline/run_pipeline.py judge`. Reason: §6 requires the composed
reference-aware judge prompt for ALL candidates in the S5 pool, and
`run_pipeline.py judge` reads its own `judge_prompt.md`/`judge-inputs/`;
running from here reuses the identical `judge_one` code path (imported) while
leaving every ast-pipeline harness file untouched.

Before any generation run: maintainer spot-check of ≥5 bridge records
(stipulated pick: money, law, status, sex, art — see `lexicon/AUTHORING.md`).
Frozen paths (`concept-def-prompt.md`, `define_concept.py`,
`validate-record.mjs`, `judge_prompt.md`, `encoder/`) are NOT modified.
Maintainer sign-off required before any FULL-tier (molecule-prose vector,
ALGORITHM_VERSION-bump) work — see DESIGN.md §9.
