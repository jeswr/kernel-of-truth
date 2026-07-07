# poc/modal — E-series on Modal serverless GPU (quota-free fallback)

AWS GPU quota for the E-series launches is stuck in an escalation queue
(bead `kernel-of-truth-wve`). Modal (modal.com) is the fallback transport:
serverless GPUs, per-second billing, **no quota**. Same runners, same inputs
as the AWS path (`poc/gpu/`) — **two transports, one analysis**.

- **E2** built + validated token-free 2026-07-07 (bead `kernel-of-truth-0oj`).
- **E1 grid + chained E4** built + validated token-free 2026-07-07 (bead
  `kernel-of-truth-af7`). The moment a token exists, each is one command.

## One-time setup (~3 min, coordinator-driven)

1. Create a Modal account at <https://modal.com> (GitHub sign-in works).
2. Pair this box (the client venv is already pinned; recreate any time with
   `bash poc/modal/validate.sh`):

   ```bash
   cd poc/modal
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # if absent
   .venv/bin/modal token new     # prints a pairing URL; coordinator opens it
   ```

   The token lands in `~/.modal.toml` — outside the repo. Nothing under
   `poc/modal/` reads, stores, or logs token material, and the provenance
   sidecars redact anything credential-shaped (`modal_common.redact_env`).

## Run E2

```bash
.venv/bin/modal run poc/modal/modal_e2.py --mock       # transport smoke, ~1 min GPU, ~pennies
.venv/bin/modal run poc/modal/modal_e2.py              # full pre-registered E2 (T4)
.venv/bin/modal run poc/modal/modal_e2.py --gpu a10g   # optional faster GPU
```

What happens: a pinned image (`requirements-image.txt`, python 3.11) is built
once and cached; `poc/e2/runner/e2_runner.py` + `poc/e2/inputs/` are staged
byte-for-byte (sha256 manifest asserted **inside** the container — a mismatch
fails closed, `ERR_STAGING_MISMATCH`); the unchanged runner executes with
`--device cuda`; the results directory returns as bytes and lands in
`poc/e2/results-incoming/<UTC stamp>-modal/` with the results JSON parse +
`OUTCOME:` echo of `poc/gpu/collect-e2.sh`. **Not auto-committed** — the
coordinator reviews and commits deliberately, exactly like the AWS pull path.
HF model downloads persist in Modal Volume `kot-hf-cache`, so only the first
run pays download time.

## Run E1 (+E4 chain)

```bash
.venv/bin/python poc/modal/modal_e1e4.py --dry-plan    # call graph + GPU-h + $ — NO token
.venv/bin/modal run poc/modal/modal_e1e4.py --mock     # tiny both-stage transport smoke, ~$0.10-0.50
.venv/bin/modal run poc/modal/modal_e1e4.py            # full pre-registered E1 grid + E4 chain (A10G)
.venv/bin/modal run poc/modal/modal_e1e4.py --skip-e4  # E1 only
.venv/bin/modal run poc/modal/modal_e1e4.py --gpu t4   # T4 flavour — see deviation 6 below
```

Pipeline (each stage subprocesses the UNCHANGED poc/e1 / poc/e4 script with
the argv of `poc/e1/run_all.sh full` / `poc/e4/runner/run_e4.sh full` — the
argv, LR-selection rule, E4 pin gate and mock corpus are **parsed out of the
staged driver bytes**, never reimplemented; see `modal_e1e4_lib.py`):

1. `fetch_corpus` (CPU): TinyStories-train → Volume `kot-e1-work`
   (sha-recorded, idempotent skip-if-verified).
2. `build_data` (CPU): parity-gated mapper port, 5 paired seeds, p=0.5 seeded
   substitution, uint16 shards. Idempotent via a stamp keyed on
   (argv, corpus sha, staged-manifest digest). Serial today (~4 h — the
   wall-clock bottleneck; bead `kernel-of-truth-0r1` parallelises it).
3. `lr_sweep` ×15 via `starmap` (5 arms × 3 LRs, seed 0, half budget), then
   `select_lrs` — the Common-rule-5 barrier — executes **run_all.sh's own**
   best-of-sweep-by-val-loss snippet; `lr-selection.json` ships with results.
4. `train_arm_seed` ×25 via `starmap`: full-budget runs, checkpoints at
   step-0/50%/100% on the Volume, frozen-row bit-identity asserted by the
   unchanged trainer in-container (a violation crashes that run).
5. `eval_ckpt` ×35 via `starmap` (incl. step-0 circularity baselines), then
   `stats_verdict`: pre-registered statistics; criteria quoted verbatim by
   the unchanged `stats_e1.py`.
6. E4 chain on the SAME Volume (exactly like `launch-e1-pull.sh --with-e4`):
   GLOSS-HASH + holdout-manifest pins asserted **in-container, fail closed**
   (`ERR_GLOSS_PIN` / `ERR_TABLES_PIN`, using run_e4.sh's own gate snippet),
   `e4_build_emission`, `e4_finetune` ×15, `e4_eval` ×15 (1,054-way
   candidate-restricted), `e4_stats` (manifest criteria quoted verbatim).

Results land in `poc/e1/results-incoming/<UTC stamp>-modal/` with the AWS
pull-path layout: `verdict-e1.{json,md}`, `lr-selection(-full).json`,
`data-meta-full.json`, `eval-*.json`, `kot-e1-run.log`, `RUNNER_EXIT`
(`rc=N e4_rc=M`, tpl format), E4 under `e4/`, plus per-run provenance
sidecars under `provenance/` and train summaries under `summaries/`
(additive — checkpoints stay on the Volume). The entrypoint echoes the
`VERDICT:` lines like `collect-e1.sh`. **Not auto-committed.** On failure it
salvages logs/provenance/partials into `<stamp>-modal-FAILED/`
(collect-e1.sh failure-trace parity), and a re-run RESUMES: completed stages
are stamped on the Volume and skipped when argv + staged bytes are unchanged.
After the campaign: `modal volume delete kot-e1-work` (~13 GB of shards +
checkpoints otherwise keeps billing storage).

### E1+E4 dry-plan (2026-07-07, real pinned client, zero Modal calls)

```
stage               kind   calls  est min/call  timeout min
fetch_corpus        cpu        1          20.0           35
build_data          cpu        1         220.0          335
lr_sweep            gpu       15          14.0           26
select_lrs          cpu        1           2.0            8
train_arm_seed      gpu       25          28.0           47
eval_ckpt           gpu       35           3.0            9
stats_verdict       cpu        1           5.0           12
e4_build_emission   cpu        1          15.0           27
e4_finetune         gpu       15           5.0           12
e4_eval             gpu       15           4.0           11
e4_stats            cpu        1           5.0           12

totals: 19.2 A10G-h (parallel; wall ~5.3 h — serial AWS path is ~20-23 h)
estimate: ~$24 GPU + ~$5 CPU/mem = ~$29;  worst case (every GPU call runs to
its sized timeout): ~$41 — vs the AWS 42 h on-demand failsafe cap ~$42
```

Per-call estimates are the poc/gpu/README.md E1 cost-table rows (g5.xlarge =
1× A10G, the same GPU); timeouts = estimate ×1.5 (the +50% margin) + 5 min
container overhead. The earlier ~$26–33 estimate **stands**: ~$29 expected on
A10G (T4: ~47.9 T4-h, ~$38 — slower AND more expensive here, see deviation 6).

## Byte-identity vs the AWS path (and honest deviations)

The wrappers subprocess the runners and ship their output as **opaque
bytes** — never rewriting results. For E2 (same runner bytes + same input
bytes + fixed seed) the verdict JSON round-trips byte-identical across
transports up to the runner's own `date` field (unit-tested).

For E1/E4 the same discipline holds at the transport layer, with these
**deviations from the AWS serial path**, in decreasing order of relevance:

1. **Parallel, not serial.** Run order is immaterial by construction (Common
   rule 1: shards/story order/substitution draws/batch schedule are functions
   of the seed index only — SHA-256 DetStream labels, hardware-independent);
   the only cross-run data flow, Common rule 5's LR selection, is an explicit
   barrier executed with run_all.sh's own snippet. Trainer argv is asserted
   (tests) to be arm-invariant apart from `--arm` and to match run_all.sh
   token-for-token, so the paired-seed batch-schedule guarantee carries over
   unchanged.
2. **Pinned env vs "newest DLAMI at launch".** numpy/torch pins in
   `requirements-image.txt` + recorded image id make the Modal env
   reproducible. Consequence for ANY cross-transport comparison: training
   float trajectories are not bit-reproducible across different
   GPU/driver/torch versions (torch makes no such promise) — but everything
   pre-registered as exact IS exact on both paths: shards/schedules
   (DetStream), frozen-row bit-identity (asserted per run, in-container),
   paired-seed base init (torch.Generator per seed). `CUBLAS_WORKSPACE_CONFIG
   =:4096:8` is set as on the AWS box.
3. **Corpus fetch**: a Modal function downloads TinyStories-train to the
   Volume (sha256 recorded in `corpus-meta.json` + `data-meta-full.json`).
   Same URL, and — like the AWS boot script — no pre-registered content pin.
4. **Mock corpus**: `--mock` uses run_e4.sh's own synthetic gloss-free
   corpus generator (network-free) instead of poc/e1's TinyStories-valid
   smoke slice; otherwise the mock mirrors `run_all.sh mock` /
   `run_e4.sh mock` (fixed LR via run_all.sh's own heredoc, mock tables,
   `--smoke` build, mock-labelled verdicts) and additionally runs BOTH
   suites' own `check_smoke.py` in-flow.
5. **E4 chained by default** (`--skip-e4` to opt out); the AWS launcher is
   E1-only with `--with-e4` opt-in.
6. **T4 flavour caveat**: `train_e1.py` uses bf16 autocast, which is not
   hardware-accelerated on T4 (sm_75). The T4 path runs the unchanged
   trainer but slower (×2.5 timeouts) and off the g5/A10G hardware baseline —
   A10G is the default and the like-for-like transport.
7. Cosmetics: no `nice` (dedicated containers), no `DONE` marker (no scp
   collection), per-stage logs concatenated into `kot-e1-run.log` /
   `e4/kot-e4-run.log` instead of one tee'd stream, and E1 train summaries
   shipped under `summaries/` (additive).

Transport provenance is SIDECAR-only, mirroring how the AWS pull path leaves
`nvidia-smi` + logs next to the results instead of editing them:

| file | contents |
|---|---|
| `provenance-modal.json` | coordinator record: gpu requested, staged sha256 manifest (every script + input), modal client + hydrated image id, timestamps |
| `provenance/<runid>.json` | per-run sidecars: stage, argv, gpu seen (`nvidia-smi`), numpy/torch versions, redacted `MODAL_*` ids, rc, timestamps, the same staged manifest |
| `kot-e1-run.log`, `e4/kot-e4-run.log` | full per-stage stdout/stderr (AWS log-name parity) |
| `RUNNER_EXIT` | `rc=N e4_rc=M` (user-data-e1-pull.sh.tpl format) |

## Cost / free-credit coverage (Modal Starter includes ~$30/month of compute; verify at modal.com/pricing)

| run | GPU time | est. cost | covered by one month's $30? |
|---|---|---|---|
| E2 `--mock` smoke | ~1–2 min T4 | ~$0.02 | yes (~0.1%) |
| **E2 full** | ~45–75 min T4 (≈$0.59/h) + CPU/mem | **~$0.60–1.00** | **yes (~3%)** |
| E1+E4 `--mock` smoke | minutes of container time | ~$0.10–0.50 | yes |
| **E1 grid + E4 chain (full)** | ~19.2 A10G-h (≈$1.10/h) parallel + ~4.5 h CPU | **~$29 (cap ~$41)** | marginal — most of one month |
| E1 only (`--skip-e4`) | ~17.5 A10G-h + CPU | ~$26 | marginal |

E1's ~20 h serial grid becomes ~5-6 h wall via `starmap` fan-out; GPU-seconds
≈ unchanged, only wall-clock shrinks (the serial CPU data build now dominates
— bead `kernel-of-truth-0r1`). Modal has no spot market: A10G costs ~2-3× AWS
spot per hour, so `poc/gpu/` stays primary once quota lands.

## Files

- `modal_e2.py` — the E2 app: T4/A10G function pair wrapping the unchanged
  runner, HF cache Volume, 4 h timeout (AWS failsafe parity), results-incoming
  unpack + provenance merge. One `local_entrypoint`, flags `--gpu/--mock`.
- `modal_e1e4.py` — the E1+E4 app: 11 stages (6 CPU + 5 GPU in A10G/T4
  flavours) over Volume `kot-e1-work`, 15/25/35/15/15-way `starmap` fan-outs,
  in-container staging + pin gates, idempotent stamps, salvage-on-failure.
  Flags `--gpu/--mock/--skip-e4/--dry-plan/--out-root`; `--dry-plan` also
  works token-free via `python3 modal_e1e4.py --dry-plan`.
- `modal_common.py` — stdlib-only transport helpers (manifest, run, package,
  unpack, redact, provenance); unit-testable without modal, reused verbatim
  inside the containers.
- `modal_e1e4_lib.py` — stdlib-only E1/E4 helpers: staged-file list, tree
  manifest, run_all.sh / run_e4.sh bash-array + heredoc parsers (the drivers
  stay the single source of truth for argv/rules), cost table, plan builder.
- `requirements.txt` — pinned modal client (venv-only; never system python).
- `requirements-image.txt` — pinned container env (numpy/torch/transformers);
  the pins + recorded image id make the environment reproducible, unlike the
  AWS "newest DLAMI at launch" resolution.
- `validate.sh` / `test_modal_port.py` / `test_modal_e1e4.py` — the
  token-free gate (below).
- `.venv/` — gitignored; recreated by `validate.sh`.

## Validation status (2026-07-07, this box, ZERO authenticated Modal calls)

`bash poc/modal/validate.sh` green:

- **E2 suite** 15/15 (Modal stubbed) incl. the full wrapper round-trip
  against the real `e2_runner.py --mock` (byte-identity + determinism).
- **E1+E4 suite** 38/38 (Modal stubbed) — wiring/timeouts vs the cost table,
  staged-file completeness, driver fidelity (bash arrays + heredocs parsed
  from the committed run_all.sh / run_e4.sh, trainer-argv arm-invariance),
  fail-closed gates (staging manifest, GLOSS-HASH, tables pin, missing-ckpt),
  dry-plan with zero calls, RUNNER_EXIT format — plus, under
  `validate.sh --mock-e2e` (disposable torch venv, poc/e1 house practice):
  the tiny-config CPU mock of BOTH stages end-to-end through the wrapper
  (`main(mock=True)`: mock corpus → build → fixed-LR selection via
  run_all.sh's own snippet → 5 arms × 2 seeds → 14 evals → stats + e1
  check_smoke → E4 pin gates → build → 3×2 fine-tunes → evals → stats + e4
  check_smoke → results bundle), proving frozen-row bit-identity assertions
  still fire through the wrapper (incl. a negative control: a corrupted
  checkpoint makes poc/e1's own check_smoke exit 1), paired-seed base-init
  bit-identity across arms, schedule determinism via poc/e1's own
  `batches()`/DetStream, results-incoming byte identity, stamp-resume, and
  the sweep+selection path against wrapper-produced summaries.
- **Tokenless imports** of both apps against the real pinned client
  (modal 1.2.6, python 3.9 — construction is lazy) + `modal run --help`
  entrypoint resolution + `--dry-plan` under the real client.

Client py3.9 vs image py3.11 is deliberate; call args/returns are plain
dict/str/bytes for cross-version safety.

## Coexistence with the AWS path

`poc/gpu/` remains the primary transport once quota lands (spot is cheaper);
this directory is the quota-free fallback. Both run the SAME committed
runners against the SAME committed inputs and land results in the same
`results-incoming/` review flow — a Modal verdict and an AWS verdict are
directly comparable, and either one satisfies the E-series campaigns.
Nothing in `poc/e1/`, `poc/e2/` or `poc/e4/` was modified for these ports.
