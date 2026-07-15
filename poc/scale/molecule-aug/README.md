# molecule-aug — reference-lexicon-augmented AST generation (strategy S5)

**DESIGN ONLY.** No prereg-freeze, no run, no commit, no encoder change. Every
choice is STIPULATED-not-MEASURED unless a measured artefact is cited by path.
Author: fable (lead designer); the coordinator owns all runs and all judging.

Tests whether letting the concept-def generator compose from a referenceable
concept lexicon (65 primes + `data/kernel-v0/` 54 + 31 authored bridge concepts)
reduces AST-lossiness vs the flat 65-prime baseline, on the same concepts, under
the `poc/scale/ast-pipeline/` blind cross-vendor judges.

**2026-07-15 — v2 revision (per the Sol readiness review + maintainer delegation):**
`DESIGN-v2.md` supersedes DESIGN.md §§2/6/7/8 — matched flat-E2-vs-mol-E2 primary
(McNemar, ITT) on **n=200 fresh frozen concepts**, single-candidate
**expanded-rendering** proxy judging (F1 gpt-5.6-sol annotator-proxy, F2 opus, F3
terra; no human judges available — all verdicts PROXY-PROVISIONAL, human re-judge of
the frozen artefacts is the upgrade path), proxy adjudication of all 31 bridges +
chains, prospective freeze. v1 Stage 2 will not run. Run commands: DESIGN-v2 §10;
run_s5.py v2 build spec: DESIGN-v2 §9.

| file | what |
|---|---|
| `DESIGN.md` | v1 design of record for lexicon/prompt/gate mechanics; §§2/6/7/8 superseded |
| `DESIGN-v2.md` | **the operative design + delegated PROCEED decision** (arms, n=200, judges, freeze, cost, claim scope, commands) |
| `judge-addendum-v2.md` | PRIMARY instrument: single-candidate, expanded-rendering fidelity addendum |
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
