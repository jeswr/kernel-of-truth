# g8 — Opus run-log (frozen design → run → mechanical verdict → cross-vendor audit)

- UTC stamp: `20260710T054838Z`
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-9` (RUN + mechanical
  verdict only; NO interpretation — `fable_interpretive_assessed` stays pending).
- Experiment: `g8` — "Lean-minting viability: fragment gate, verified LLM locale,
  round-trip fixed point (HS8 / NF3)".
- Frozen record `registry/experiments/g8.json`
  frozen_sha256 `a3c4510113513525c8e5aaff4f7a0f27c2ee6edaed9463c3b0e25d8da3b2b41c`
  (== `registry/frozen-index.json[g8]`; registry-check frozen-drift OK).
- Pinned analysis `analysis/g8.py` sha256
  `e5769612fc072faf38e7155abf13f3d7e76515036a5fe29dde2a4cbd9dc03674`
  (== `pins.analysis_script.sha256`; `--selftest` OK this session).
- Instrument `tools/experiments/g8_instrument.py` sha256
  `f051d4fc640b4f2d505887204ae7d572e655572dbc096904c4f8b2b10d2e8138`;
  `tools/experiments/g8_fragment.py` sha256
  `f7ecc10c7f8afd4fd31b3d6758e80ca457e708301f77ff422463263516fb5635`.

## Step 1 — Ops amendment (pre-unblinding, pre-run; frozen record UNTOUCHED)

The frozen record pre-declares `pins.corpus_hashes.mathlib-1000-sample =
PINNED-AT-INPUTS:...` — a placeholder lawfully filled by a pre-run ops amendment
(P2 P-9; prereg-freeze exempts placeholders). Wrote
`registry/amendments/g8/1-pin-mathlib-1000-sample.json` (kind `ops`, seq 1):
single `replace` at `/pins/corpus_hashes/mathlib-1000-sample` →
`9c2a3a888b98593d999adb65c7a32cba0cdbf092bcdb5f2b9c738e4cff2a80c2`
(= `tools/registry/corpus-pin.py mathlib-1000-sample`, the kot-corpus-hash/1 digest
of `data/mathlib-1000-sample/`). Verified via verdict-gen's own overlay
(`apply_amendment_overlay`): amendment [1] applies, resolves the placeholder to the
real digest, the raw frozen file + its `frozen_sha256` are byte-untouched, and the
amended effective-record hash is
`a2b46a0e9dbddc1dd8c47cffada119e56a51a8484507d75e53180589af8b3bd2`.
`registry-check.py`: 0 g8-scoped FAILs; the `WARN corpus-pins: g8/mathlib-1000-sample
is a PINNED-AT-INPUTS placeholder` is the raw-record lint (registry-check reads the
frozen file, not the overlay) and persists by design — matching the
f2b-transfer-llmproxy precedent; the amendment is the authoritative resolver and is
applied by verdict-gen + independently re-derived by the cross-vendor audit.

## Step 2 — Host LLM served (R0 record pins NO host model → pinned in RUN CONFIG)

Served **Qwen/Qwen2.5-7B-Instruct** (Apache-2.0, ungated) behind an
OpenAI-compatible endpoint on Modal via vLLM 0.7.3 (`poc/modal/modal_g8_vllm.py`;
debian_slim + `vllm==0.7.3`, `transformers==4.48.3` pin — the default newer
transformers breaks the Qwen2 tokenizer; A10G 24GB, `--max-model-len 8192`, bearer
auth via the `VLLM_API_KEY` Modal secret so the key never enters the server's logged
args). Pinned in the run config:
- model `Qwen/Qwen2.5-7B-Instruct`
- revision `a09a35458c702b33eeacc393d103063234e8bc28`
- decode `temperature 0`, `max_tokens 300`

Endpoint verified end-to-end before the run: `/v1/models` → 200 (correct model at the
pinned revision); a temp-0 `/v1/chat/completions` smoke returned the requested JSON;
an unauthenticated request returned 401. GPU wall-clock ≈ 10 min across the build /
crashed-first-attempt / successful serve; cost ≈ $0.20 (recorded 0.30 / 0.25 GPU-h,
conservative; budget cap $5). App + secret torn down after the run.

## Step 3 — Run sequence (per the g8-instrument handoff)

1. `--emit-prompts` → `prompt-pack.jsonl` (39 targets; pack_sha256
   `3d45629951c018674909a10ea22135e02503a4219de991d7cd25bc70e16e4699`).
2. `--call-llm` (temp 0) over the 39 prompts → `llm-raw.jsonl` (header pack_sha256
   matches; model + decode pinned; **39/39 ok, 0 transport errors, 0 null outputs**).
   raw_file_sha256 `065a2242b7e7af77416ec2b2729a8ce45dffd8d9f9ebbafdda64af6c701bca3f`.
3. `--fetch-candidates` (pre-downloaded doc-gen4 index
   `declaration-data.bmp` sha256 `ea533afe…`, moved to scratch after use — its bytes
   are pinned by sha in the run record + `fetched/fetch-log.json`) → `fetched/`
   (archive + fetch-log). **fetched mathlib_commit
   `e3b73828b03c9961c9b33aa95f1d2dc0dca82028` == the pinned sample's commit** (no
   cross-page commit mismatch — fails closed otherwise); 17 names resolved from live
   doc-gen4, 114 candidate names unindexed (LLM-proposed names absent from Mathlib —
   correctly unresolvable).
4. `--run --sample data/mathlib-1000-sample/records.jsonl --raw llm-raw.jsonl
   --candidates fetched/archive.jsonl,data/mathlib-1000-sample/records.jsonl,
   data/math-lean-sample/records.jsonl --details details.jsonl` → the 8-count metrics
   block (RAW only; 0 internal parser errors; gate reject reasons sum to exactly
   1000). sample_file_sha256
   `35650ba58be5e4862b6cad0d12f1d0f3b2548939ac2a658e0d8d09d239040d9b`.
5. `log-append.py` phase:`final` → `results-log/g8.jsonl` seq 0 (run, exit ok,
   prereg_hash == frozen hash, runner runner-9). config = instrument/fragment/analysis
   shas + model+revision+decode pins + hardware + coverage_requirement restatement
   (m0b census, P2 G-7, not a new measurement); pins_observed re-verifies the analysis
   sha + all four reproducible corpus pins + the amendment-resolved
   mathlib-1000-sample digest.
6. `verdict-gen.py` (mechanical, pure function) → `registry/verdicts/g8.json`;
   appended the `unblind` line seq 1. amendments_applied [1]; eligible_runs 1;
   analysis_output_sha256 `6670c0164b6241d1f05fab66327fecb327c12d45a16a76c5aa6a9d5793b85645`.
7. `report-gen.py` → `reports/auto/g8/verdict-g8.md`; `reuse-check.py build` (producer
   R-1) refreshed `registry/artifact-ledger.jsonl`.

## MECHANICAL numbers (RAW counts / pure-function gates — NOT an interpretation)

Eight-count metrics block (seq 0):

| count | value |
|---|---|
| n_mathlib_decls | 1000 |
| n_in_fragment | 0 |
| n_location_targets | 39 |
| n_location_top5 | 5 |
| n_roundtrip | 33 |
| n_roundtrip_fixed | 33 |
| n_llm_candidates | 139 |
| n_f_verified | 7 |

Pinned analysis (`analysis/g8.py`) output:
- `/gates/instrument_valid` = true (n_mathlib_decls ≥ 1000 AND n_location_targets ≥ 39)
- fragment_rate 0.0; **fragment_wilson_lb 0.0, fragment_wilson_ub 0.0026987**
- location_rate 0.128205; location_wilson_lb 0.063819, location_wilson_ub 0.240837
- roundtrip_holds true (33/33)
- f_verification_rate 0.0503597 (7/139)

Frozen verdict_rules evaluated top-down (pure function):
- rule 0 INSTRUMENT-INVALID: instrument_valid true → does not fire.
- rule 1 FAIL: `fragment_wilson_ub ≤ 0.01` (0.0027 ≤ 0.01) TRUE **and** the OR also
  holds (`location_wilson_ub ≤ 0.80`, 0.2408 ≤ 0.80) → **FIRES**. f_verification_rate
  0.0504 ≥ 0.01, so the near-zero-F-verification kill did NOT fire; the FAIL is on the
  fragment + location bounds.

**MECHANICAL VERDICT: FAIL** (fired_rule_index 1). Kill-criterion mapping (verbatim in
the frozen record): "below either bound ⇒ Metamath-only identity stands, Lean stays
annotation-only." Interpretation is FABLE's, NOT written here.

## Step 4 — Cross-vendor GATE-A audit (Codex/GPT-5.5; run != audit)

`codex exec -s read-only -c model_reasoning_effort=high --output-schema … --json`
(codex-cli 0.142.5, gpt-5.5, sandbox read-only, session
`019f4aa3-848f-7290-b5b0-32074684b8f2`; smoke session
`019f4aa3-3c9e-7641-9198-6a81c8e06847` returned KOT-AUDIT-SMOKE-OK). Auditor
`auditor-5` (independent: not a runner in the log). Independently recomputed the
frozen hash (a3c45101…), the amendment overlay + amended-record hash (a2b46a0e…), the
JSONL hash chain, all five corpus pins (incl. the amendment-resolved
mathlib-1000-sample), the analysis sha, re-ran the pinned analysis over seq 0 only,
reproduced `analysis-output.json`, and evaluated the verdict_rules to fired_rule_index
1 = FAIL. **Result CONFIRM** (all 13 checks ok, failing_step null,
matches_verdict_object true). Record:
`registry/audits/g8/1-gate-a-codex.json` (kot-audit/1, outcome CONFIRMED).
verdict_object_audited_sha256 `63f5a6946723272462fcb0da399c0d0229bc35d1576d822a3dfde11fc8fa9538`.
Verdict stays FAIL / audit N/A (the audit gate's PASS→PASS upgrade is inapplicable to
a FAIL; the CONFIRM cross-vendor-certifies the mechanical FAIL).

## Provenance / integrity gates (this session)

- g8 instrument `--selftest` OK; `analysis/g8.py --selftest` OK; `--mock` end-to-end
  green (all checks true) — same-day green before the real run.
- reuse-check `--gate` (pre-spend): exit 0, 0 blocking, 1 unlogged cell.
- registry-check: g8 chain (2 records), frozen-drift g8, four reproducible g8
  corpus-pins, account-lint (experiment/verdict/amendment/audit/log) all GREEN. The
  mathlib-1000-sample WARN is the by-design raw-record placeholder lint (see Step 1).
  Repo-wide FAILs present are kb-sync-deferred: `ERR_KB_INTERNAL_STALE` for
  `internal_g8.json` (this run — kb-sync-internal deferred to the coordinator per the
  handoff) and `ERR_KB_INTERNAL_EDITED` for `internal_doc-design-neurosym-kernel-
  internals.json` (a concurrent session's file, out of scope for g8).

## DEFERRED (NOT done here — no Opus conclusion, no kb-sync, no git)

- FABLE interpretive assessment: kill-chain read (what n_in_fragment 0/1000 and the
  location/round-trip/F-verification numbers MEAN for HS8/NF3), any
  EXTRAPOLATION→MEASURED promotion, kot-assess. `fable_interpretive_assessed: pending`.
- `tools/kb/kb-sync-internal` (regenerate `internal_g8.json`) — coordinator.
- git add/commit/push — coordinator (branch index is coordinator-owned).
