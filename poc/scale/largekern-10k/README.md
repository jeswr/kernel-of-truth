# largekern-10k — WordNet-10k drafting pipeline, MOCK-FIRST build ($0)

Pre-freeze build artifact for the GPT-5.6 WordNet-10k drafting pilot, built
exactly per the reviewed GO-TO-FREEZE spec
`docs/next/design/gpt56-draft-pipeline-large-kernel.md` (revision **r5**).
Built by designer-20 (pipeline-code ASMs) for coordinator review; operated by
runner-1 (kb-pipeline-runner) in any real run.

**NOTHING here spends money or touches a network.** The GPT-5.6 drafter and
the OpenAI Batch backend are MOCKS (`pipeline/mock_drafter.py`,
`pipeline/mock_batch.py`). The real run happens only after the coordinator's
prereg-freeze (spec §10.6 P7), with the store re-rooted at
`data/kernel-v1-draft/` and the mock seams replaced (ASM-2496 lists every
deliberate mock divergence).

**Adversarial-review finding — CLOSED (2026-07-16).** The MAJOR finding that
the mock interleaved per-request errors into a single `output_file_id` (no
`error_file_id`), so the orchestrator's §10.4 provider-retry / PROVIDER_FAILED
accounting would silently never fire on the real run (leaving `SUBMITTED`
ledger rows that break §10.3 terminal accounting), is fixed: `mock_batch.py`
now routes per-request failures/expiry to a separate `error_file_id` and
whole-batch validation failures to `status="failed"` (no files, `errors[]`),
and `orchestrator.py` merges both files + the `failed` status into the §10.4
path, failing closed (`ERR_UNACCOUNTED_REQUEST`) on any un-accounted
`custom_id`. Modelled + tested end-to-end (ASM-2496 (h)); mock-green now
implies real-green for the error path.

## Layout / components (spec section per module)

| file | spec | what |
|---|---|---|
| `pipeline/common.py` | — | pinned values (frame hash ASM-2493, $500 cap, R=2, §5.2 prices), hash conventions (ASM-2497) |
| `pipeline/frame_sample.py` | §1, §9.3, P1 | frame recompute + `ERR_FRAME_HASH` fail-closed, denylist `ERR_FROZEN_OVERLAP`, seeded stratified 10k draw (ASM-2498), sample manifest |
| `pipeline/prompt.py` | §2.2, §3, §5.3 | scholarly drafting prompt (4 invariant prefix blocks, `cachePrefixHash`; exemplar block = P2 placeholder), deterministic Batch request bytes, versionHash/idempotencyKey |
| `pipeline/ledger.py` | §6.1, §10.2 | SQLite WAL ledger: atomic row claim, job outbox committed BEFORE create, `BEGIN IMMEDIATE` worst-case reservation (`ERR_BUDGET_RESERVE`), settlement release, terminal accounting, passive JSONL export |
| `pipeline/mock_batch.py` | §6, §10.4, P5 | mock Batch backend (create/list/retrieve/`output_bytes`/`error_bytes`, `after`/`has_more` pagination); per-request failures/expiry split to a separate `error_file_id`, whole-batch validation failure → `status="failed"` + `errors[]`; crash/pagination/validation injection hooks |
| `pipeline/mock_drafter.py` | §2.3, §10.4 | mock GPT-5.6: deterministic drafts + pinned failure mix (invalid AST, gloss lint, malformed, abstention, provider transients) |
| `pipeline/validate_shard.mjs` | §4.1, §7.1 | REUSED encoder loop: `validateExplication` + `ERR_REF_OUTSIDE_CATALOG` closure + `encodeConceptSet(opts.concepts)` sanity, B=1,000 shards, P4a instrumented |
| `pipeline/accept.py` | §2, §4.1, §8, §9 | gloss lints + leakage, immutable ModelDrafted minting (kernel-v1-draft/1, §8 provenance incl. `requestId`), quarantine, §9.2 consumer gate (JSONL-aware) |
| `pipeline/orchestrator.py` | §6 r5, §7, §10 | jobKey = sha256(wave ‖ attempt ‖ sorted member keys)[:24], exhaustive-pagination sweeper (`ERR_RECONCILE_UNVERIFIED` fail-closed), settle merges output+error files & the `failed` status into the §10.4 provider-retry/PROVIDER_FAILED path (`ERR_UNACCOUNTED_REQUEST` fail-closed), repair waves ≤ R=2, kill ladder, P4a/P4b gates |
| `pipeline/run_e2e.py` | §10.3, P7 | the green $0 end-to-end mock incl. mid-run crash-recovery demo and endpoint computation |
| `tests/test_pipeline.py` | P5, P8, §10.2, §10.4 | 25 tests: both SIGKILL crash windows, r5 negative listing cases, jobKey collision case, budget atomicity, family/status fail paths, acceptance routing, and the error-file cases (per-request 500 → PROVIDER_FAILED, transient expiry → recovered, whole-batch `failed` → all-member retry, `ERR_UNACCOUNTED_REQUEST` guard) |

Reused, not reimplemented: `poc/plainv5/{invoke_seat,check_family_disjoint,family-map.json}`
(P8 machinery, a4f65edd), `encoder/dist` (validator/encoder loop),
`tools/registry/kot_common` (hashing, account lint, Wilson LB).

## Check commands

```bash
cd poc/scale/largekern-10k
python3 pipeline/frame_sample.py                       # component 1 (frame+sample)
python3 pipeline/prompt.py                             # component 2 (determinism probe)
nice -n 10 python3 -m unittest tests.test_pipeline -v  # P5/P8/budget/gates/error-file (25 tests)
nice -n 10 python3 pipeline/run_e2e.py --n 10000 --fresh   # full green mock (~2.5 min)
```

Latest full-run artifacts (2026-07-16, this box): `out/e2e-report.json`
(GREEN; terminal accounting 9,521 accepted + 453 quarantined + 26
provider_failed = 10,000; spend $182.62 mock-settled under the $500 cap;
α_LB 0.951, κ 0.864, $/accepted $0.0192; crash-adopt with zero duplicate
submissions), `out/p4a-benchmark.json` (224 rec/s, 205 MiB RSS,
representative B=1,000), `out/p4b-sizes.json`, `out/sample-manifest.json`.

## ASMs

ASM-2496 (mock conventions), ASM-2497 (hash byte-serialization), ASM-2498
(sampling mechanics) — companion file
`asm-largekern-mockbuild-2496-2498.json`, rows appended to
`registry/assumptions.jsonl` (working tree; coordinator commits).

## Known pre-freeze gaps (deliberate; blocking items live in the spec's P-list)

- P2 exemplar review not run: prefix block 3 is a labelled placeholder; the
  re-freeze changes `cachePrefixHash` deliberately.
- P3 micro-pilot, P6 preflight (real prices/tokenizer/API key) and P7
  maintainer cap/$c re-confirmation are real-run-side, untouched here.
- §10.3 endpoint 4 (human pass-rate) is N/A in the mock and blocks any real
  PROCEED.
- Interface wrinkle for the coordinator: the pinned
  `check_family_disjoint.check_status_eligibility` reads per-file `.json`
  records keyed on `status`; kernel-v1-draft records are JSONL shards keyed
  on `semanticStatus`. `accept.check_status_eligibility_jsonl` applies the
  identical fail-closed semantics to the shard format; reconciling the two
  (tool flag or record field) is a follow-up decision — the pinned tool was
  NOT modified by this build.
