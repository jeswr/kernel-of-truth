# f2b-replicate — Opus run-log (PHASE 2: real A100 run)

- UTC stamp: `20260709T110510Z` (`date -u +%Y%m%dT%H%M%SZ`)
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-4`
- Task: RUN the right-sized, FROZEN f2b-replicate on a single A100-40GB
  (detached), per the advisor right-sized design. Phase 1 (right-size +
  reset-correct-refreeze + dry-plan + mock smoke) was completed by `runner-3`
  in `poc/f2b/opus-runs/20260709T104212Z/`; this log covers the real run only.
- Opus-execution practices: this log is a committed BACKUP for a Fable agent to
  audit later (practice 1); the single reproducible launcher is
  `poc/f2/run-f2b-replicate.sh` (practice 2); ledger row in
  `registry/audit-status.jsonl` (practice 3); NO interpretation / NO verdict-gen
  / NO conclusive analysis by Opus (practice 4).

## Pre-launch gate re-verification (this session, all $0)

Independently re-verified before spending any GPU:

1. Current harness file shas (unchanged from Phase-1 log):
   ```
   b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666  poc/f2b/runner/f2b_runner.py
   da1fe9dddd9cbddc13143a7f7931ae3f0ced2548df8e36042244ee043fcb61f9  poc/f2b/inputs/f2b-manifest.json
   c2fc2b3a50458e7353c7b687e0a5ea9820c2be0517c93831e76422de1555575d  poc/modal/modal_f2b.py
   14bbc66840e1f2d7d57aeda22e52c69b5a1d99820562980d46b16f22541219a4  poc/f2b/smoke/check_mock.py
   3209b4b0f94d6fbb07ccd63048ce4603e7def0605b50749bef6bd718c799e0d1  poc/f2/run-f2b-replicate.sh
   711ac322573be939a03f60aa39ef9bb05b775336c6474d634e43ed20f57e8426  analysis/f2b_replicate.py
   ```
2. Recomputed harness_manifest (offline, 158 files):
   `cffd61049bd6f6a08adf1dbe6ee3a2aa7dd3d032c630de10060edfbca5431d9c`
   == frozen record `pins.harness_manifest` (NO drift since freeze).
3. `poc/f2/run-f2b-replicate.sh --dry-plan` -> gate 1 OK (FROZEN,
   frozen_sha256 `21d401777d2b11bca98b0528a58ebb23e774e4d7e4bee5434a746be76a66771d`
   == frozen-index), registry-check PASS. Cost plan (A100): 19 cells, 3 seeds,
   250 fresh d-qa-r covered items + 500-item external slice; 0.38 h point /
   0.76 h worst; $0.80 / $1.60; all caps OK (usd_cap $60, gpu_hours_cap 24 h,
   Tier-1 cap $80). <1 h => Phase-2 launch gate satisfied.
4. `poc/f2b/smoke/check_mock.py` -> F2B-REPLICATE MOCK SMOKE: ALL CHECKS PASSED
   ($0, CPU): 7 arm levels x 14 records, all 50 output_fields resolve,
   separation gate (sep=0.312, delta=0.156) + P10 gate PASS, best_k=4,
   gold-oracle field null (arm dropped), both safety bounds self-terminate.

## Inputs (paths + shas)

- Frozen record: `registry/experiments/f2b-replicate.json`
  frozen_sha256 `21d401777d2b11bca98b0528a58ebb23e774e4d7e4bee5434a746be76a66771d`.
- pins.harness_manifest `cffd61049bd6f6a08adf1dbe6ee3a2aa7dd3d032c630de10060edfbca5431d9c`.
- pins.analysis_script `analysis/f2b_replicate.py` sha256
  `711ac322573be939a03f60aa39ef9bb05b775336c6474d634e43ed20f57e8426`.
- Models: SmolLM2-135M @12fd25f77366, SmolLM2-1.7B @31b70e2e869a,
  Skywork PRM 1.5B @98d69606595e.
- Corpora (kot-corpus-hash/1): d-qa `ad756a7e...`, d-qa-r `0d548bf1...`,
  d-xif `8c9aded6...`, d-ext `0c5306bb...`, kernel-v0 `8209cada...`,
  molecules-v0 `69f0c8a3...`.

## Reproducible launch command (the ONE script)

```
KOT_TIER1_GO=1 poc/f2/run-f2b-replicate.sh --run
# which execs: poc/modal/.venv/bin/modal run poc/modal/modal_f2b.py --gpu a100
```
Launched detached via `setsid`, stdout/stderr -> `launch.log` in this dir.
Maintainer Tier-1 go is authorised by Jesse's Opus-execution authorization
(Tier-0 + F2 $80 authorised); dry-plan worst case $1.60 << $80 Tier-1 cap.

## Run timeline (appended as it runs)

- `20260709T110558Z` LAUNCH: `KOT_TIER1_GO=1 poc/f2/run-f2b-replicate.sh --run`
  detached via `setsid` (real pid 364210, PPID 1 = detached session). Launcher
  gate 1 OK (FROZEN sha `21d40177...`, harness pin `cffd6104...`, models
  SmolLM2-1.7B@31b70e2e869a / SmolLM2-135M@12fd25f77366 / PRM@98d69606595e),
  registry-check PASS. Modal wrapper printed staged-bytes sha `cffd6104...`
  (== frozen pin; in-container assert also fails closed on drift). Runner
  started: `mode=FULL device=cuda items=1000 fresh covered (d-qa-r)`,
  shuffled-verifier permutation `seed=20260709 sha=05af8f50b134` (matches smoke).
  Full launch stdout: `launch.log` in this dir.

- `20260709T114229Z` RUN COMPLETE — OUTCOME `HARNESS-COMPLETE`, runner rc=0.
  Container: started `2026-07-09T11:06:11Z`, finished `2026-07-09T11:42:29Z`
  (wallClockHours 0.604 ≈ 36.2 min runner wall-clock). GPU seen: NVIDIA
  A100-SXM4-40GB (40960 MiB) — matches --gpu a100. No ERR_STAGING_MISMATCH;
  `coordinator.local_manifest_matched: true` and the coordinator-printed
  staged-bytes sha `cffd6104...` == frozen `pins.harness_manifest` => the
  in-container staged-bytes assert held against the NEW harness_manifest.
  20 run-record bodies, 3 seeds, all `exit: ok`.

### Per-cell timings (from launch.log; ESTIMATES are never these — these are real elapsed)
```
model-alone R1 s0 75.5s | s1 74.7s | s2 74.8s
model-alone R3 s0 56.9s | s1 56.9s | s2 56.9s
kernel-verify-retry  R1 k4 s0 116.7s | s1 112.7s | s2 113.5s
shuffled-verify      R1 k4 s0 126.5s | s1 124.9s | s2 125.0s
kernel-as-text       R1     s0  74.2s
gloss-self-verify    R1 k4 s0 168.5s | s1 168.0s | s2 168.0s
prm-verifier         R1     s0 ~ s2  ~105.7-105.8s each
extraction-instrument R1    s0   0.1s (CPU)
iface gate: 500 labelled, 0 extraction failures
```

### Outputs (declared; NOT auto-committed)
- Results dir `poc/f2b/results-incoming/20260709-114229-modal/`:
  - `run-records-f2b.jsonl` sha256 `dd98ccebaebd6a44d9dbe69e251a75978456c3f6ffd2ce99b534ead5c78ee570`
  - `results-f2b.json`      sha256 `8c01f2c974891955ff3d0a06358311641cdf37d2c61ec824fd818f655f2aec7c`
  - `provenance-modal.json` sha256 `9cd93e41cf2963126b7d680acea5e5045c796117fc3787db5f539c309172e330`
  - `shuffle-map.json`      sha256 `173b351d16352d581e67fa69495b135283e37a92b6ec2a5254985a93a9c63676`
- Modal app run: https://modal.com/apps/jmwright-045/main/ap-I4Fuaz9RZtGLDcymmH4H6L

### Appended to results-log (log-append, agent runner-4, phase:final)
20 records appended seq 0..19 to `results-log/f2b-replicate.jsonl`
(prereg_hash `21d40177...` == frozen index; each append chain-verified,
config_sha256 auto-stamped; NO derived stats in any metric body).
results-log file sha256 after append: `a3becf11498f2f5b8824d2ce9b52ede262065d0a036bea1f211b03e6a1d5817d`.
(These result records are NOT git-committed by this Opus run.)

### MECHANICAL numbers (pure means / raw counts — NOT a verdict, NOT an interpretation)
- acc(model-alone R1, SmolLM2-135M) = 0.4920  (seed-averaged per-item mean over 250 covered items x 3 seeds)
- acc(model-alone R3, SmolLM2-1.7B) = 0.6000  (same)
- separation gap acc(R3)-acc(R1) = 0.1080  (pre-declared instrument point-threshold >= 0.10; the BCa one-sided lower-bound component is a pure function computed by the pinned analysis/f2b_replicate.py — NOT computed here)
- extraction instrument: n_labelled=500, n_extraction_failures=0, n_extraction_errors=0 (Wilson-LB computed by the pinned analysis)

### Cost (mechanical estimate)
Runner GPU wall-clock 0.604 h on one A100 x Modal A100 list $2.10/h ≈ $1.27
(image was cache-warm; below dry-plan worst $1.60 and far below usd_cap $60 /
Tier-1 cap $80). Actual Modal billing per the app-run link.

### DEFERRED (Opus-execution practice 4 — NOT done here)
- verdict-gen: NOT run (analysis/f2b_replicate.py -> verdict-gen ->
  registry/verdicts/f2b-replicate.json) — deferred.
- Codex/GPT-5.5 cross-vendor audit: PENDING.
- FABLE interpretive assessment (kill-chain read, separation-gate CI,
  EXTRAPOLATION->MEASURED, kot-assess): PENDING. NO Opus conclusion written.
- git commit of results: NOT performed by this run (per instruction).

### Note (unrelated to f2b)
`registry-check.py` reports 6 PRE-EXISTING KB-shard pin violations
(kb/chunks, kb/embeddings, kb/manifest.json — governance-wiring-3 artifacts),
independent of the f2b log chain (which log-append chain-verified on every
append). Left untouched (out of scope).
