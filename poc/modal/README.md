# poc/modal — E-series on Modal serverless GPU (quota-free fallback)

AWS GPU quota for the E2 launch is stuck in an escalation queue
(bead `kernel-of-truth-wve`). Modal (modal.com) is the fallback transport:
serverless GPUs, per-second billing, **no quota**. Same runners, same inputs
as the AWS path (`poc/gpu/`) — **two transports, one analysis**.

Built + validated token-free 2026-07-07 (bead `kernel-of-truth-0oj`); the
moment a token exists, E2 is one command.

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
   sidecar redacts anything credential-shaped (`modal_common.redact_env`).

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

## Byte-identity vs the AWS path

The wrapper subprocesses the runner and ships its output as **opaque bytes**
— it never rewrites `results-e2.json` / `verdict-e2.md`. Same runner bytes +
same input bytes (manifest-enforced) + the runner's fixed seed ⇒ the verdict
JSON round-trips byte-identical to what the AWS path would produce; the
runner's own `date` field is the only per-invocation difference, on any
transport. (Unit-tested: `test_cross_transport_determinism`.) Two runner-side
caveats apply to ANY cross-transport comparison, not to this wrapper: real
(non-mock) extraction depends on torch/cuda kernels, so bit-level float
identity across different GPU/driver/torch versions is not guaranteed by
torch itself — which is why the image is PINNED here while the AWS path
resolves "newest DLAMI" at launch.

Transport provenance is SIDECAR-only, mirroring how the AWS pull path leaves
`nvidia-smi` + logs next to the results instead of editing them:

| file | contents |
|---|---|
| `provenance-modal.json` | GPU requested + `nvidia-smi` seen, staged sha256 manifest (runner, requirements, every input), numpy/torch/transformers versions, redacted `MODAL_*` ids, runner rc, timestamps; the coordinator merge adds modal client version + hydrated image object id |
| `kot-e2-run.log` | full runner stdout/stderr (same name as the AWS path) |
| `RUNNER_EXIT` | `rc=N` (same format as the AWS path) |

A failed run still returns partials + logs + rc (diagnosable trace), then the
entrypoint exits non-zero — collect-e2.sh failure-trace parity.

## Cost / free-credit coverage (Modal Starter includes ~$30/month of compute; verify at modal.com/pricing)

| run | GPU time | est. cost | covered by one month's $30? |
|---|---|---|---|
| E2 `--mock` smoke | ~1–2 min T4 | ~$0.02 | yes (~0.1%) |
| **E2 full** | ~45–75 min T4 (≈$0.59/h) + CPU/mem | **~$0.60–1.00** | **yes (~3%)** |
| E1 full grid (once ported, bead `af7`) | ~17 A10G-h (≈$1.10/h) parallel + ~4 h CPU build | ~$22–27 | marginal — most of one month |
| E4 chained (once ported) | ~3–5 A10G-h | ~$4–6 | yes, if E1 spread across months |

E1's ~20 h serial grid becomes ~4–5 h wall via `starmap` fan-out (25 parallel
train jobs; the serial CPU data build dominates — bead `kernel-of-truth-0r1`).
GPU-seconds ≈ unchanged; only wall-clock shrinks. Modal has no spot market:
T4 costs ~2–3× AWS spot per hour, but E2 is ~$1 either way and quota-free.

## Files

- `modal_e2.py` — the E2 app: T4/A10G function pair wrapping the unchanged
  runner, HF cache Volume, 4 h timeout (AWS failsafe parity), results-incoming
  unpack + provenance merge. One `local_entrypoint`, flags `--gpu/--mock`.
- `modal_common.py` — stdlib-only transport helpers (manifest, run, package,
  unpack, redact, provenance); unit-testable without modal, reused verbatim
  inside the container.
- `modal_e1e4.py` — **SCAFFOLD** (raises `NotImplementedError` everywhere):
  fixes the E1+E4 function/Volume/parallelism shape (`kot-e1-work` Volume,
  15-way sweep + 25-way grid + 35-way evals via `starmap`). Full port: bead
  `kernel-of-truth-af7`.
- `requirements.txt` — pinned modal client (venv-only; never system python).
- `requirements-image.txt` — pinned container env (numpy/torch/transformers);
  the pins + recorded image id make the environment reproducible, unlike the
  AWS "newest DLAMI at launch" resolution.
- `validate.sh` / `test_modal_port.py` — the token-free gate (below).
- `.venv/` — gitignored; recreated by `validate.sh`.

## Validation status (2026-07-07, this box, ZERO authenticated Modal calls)

`bash poc/modal/validate.sh` green: 17/17 unit tests (Modal stubbed) including
a full wrapper round-trip against the real `e2_runner.py --mock` (staging
assertion → subprocess → package → unpack → provenance merge → OUTCOME echo,
byte-identity + determinism checks); tokenless `import modal_e2` against the
real pinned client (modal 1.2.6, python 3.9 — app/image/volume construction
is lazy); `modal run modal_e2.py --help` resolves the entrypoint + flags.
Client py3.9 vs image py3.11 is deliberate; call args/returns are plain
dict/str/bytes for cross-version safety.

## Coexistence with the AWS path

`poc/gpu/` remains the primary transport once quota lands (spot is cheaper);
this directory is the quota-free fallback. Both run the SAME committed runner
against the SAME committed inputs and land results in the same
`results-incoming/` review flow — a Modal verdict and an AWS verdict are
directly comparable, and either one satisfies the E2 campaign. Nothing in
`poc/e2/` was modified for this port.
