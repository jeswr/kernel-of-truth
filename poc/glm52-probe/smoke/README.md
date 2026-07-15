# GLM-5.2 colibri backend-feasibility SMOKE

> **EXPLORATORY infra — rigor relaxed vs a frozen experiment.** Builds and
> $0-validates the Stage-1 backend-feasibility smoke from
> `docs/next/design/glm52-expert-profiling-plan-sol-20260715.md`
> (§"Modal smoke test" + steps 2–3 of "First three coordinator-dispatchable
> steps"). Nothing here is a registry entry or a frozen mask; the coordinator
> reviews + commits. **The real 383.8 GB smoke is the coordinator's ≤$3 run
> (command below) — the build pass never staged the estate.**

## What the smoke answers

Can the full colibri int4 GLM-5.2 estate (383.8 GB, `mateogrgic/GLM-5.2-colibri-
int4-with-int8-mtp`, 19,456 routed cells) be staged, per-token router-traced, and
run on a genuinely non-AWS Modal worker within budget — and is local ephemeral-SSD
random-read bandwidth ≥1 GB/s (the one make-or-break the $0 audit could not settle;
`../stage1-feasibility-manifest.md` B3). Emits **GO-FULL-GLM52 / PROXY-ONLY /
OFFLINE-ONLY**.

## Files

| File | What |
|---|---|
| `rtrace.h` | READ-ONLY per-token MoE router-trace emitter (self-contained; inert unless `RTRACE=<file>`). Per-item reset, main/MTP disambiguation, top-k margin. |
| `rtrace-add-path.patch` | Unified diff vs pinned colibri `a78a06fc…d1250`: `moe()` gains a read-only emit + `pos_base`; adds `run_trace_score` (`TRACE_SCORE`) + `RTRACE` wiring; +1 Makefile dep. |
| `test_rtrace.c` | C unit tests for the emitter (per-item reset, top-k, main/MTP, byte-identity, io tag) + writes a real analyzer fixture. |
| `trace_schema.md` | The `kot-rtrace/1` schema + invariants. |
| `trace_analyze.py` | Integrity + go/no-go (all four verdict branches). Pure stdlib. |
| `smoke_driver.py` | In-container sequence: lscpu · arch self-test · 19 MB random-read iobench · 12 traced probes (+2 repeats) · analyzer · verdict. |
| `corpus/probes12.json` | 12 fixed teacher-forced probes (code/math/Chinese/JSON/prose/copy ×2) + tiny-oracle ids. |
| `build_apply.sh` | Host build: clone@pin → apply patch → build → inert-by-default proof → test_rtrace. `$0`. |
| `validate_local.sh` | The `$0` on-box validation (real emitter → real trace → analyzer; 4/4 verdicts). |
| `../../modal/modal_glm52_smoke.py` | The Modal wrapper: `plan` (dry-plan, $0) · `tiny` (~$0 real-oracle validation) · `main` (the ≤$3 full smoke). |

## Inert-by-default (MEASURED, on-box)

With `RTRACE` unset the engine holds `g_rt==NULL` and every trace call is a no-op.
Per-function objdump equivalence (pristine vs patched, address-normalised): only
`moe`, `layer_forward`, `main` differ — every other shared function byte-identical.

## Validation status (MEASURED 2026-07-15)

- **On-box `$0`** (`./validate_local.sh`): patched engine builds (gcc 11.5), 12/12
  C emitter unit tests pass, real emitter writes a 987-line GLM-5.2-shaped trace,
  analyzer returns GO / PROXY / OFFLINE / OFFLINE on the four fixtures — per-item
  reset + no-carry-over + top-k + main/MTP + byte-identity all enforced.
- **On Modal (image build)**: the patched engine builds remotely, `git apply` is
  clean, `test_rtrace` passes in the OCI image.
- **Dry-plan** (`modal run …::plan`): **cloud must be `oci`** — `gcp` rejects the
  900 GiB ephemeral ("Large disk requests are not supported for cloud provider
  'gcp'"); OCI accepts it. Config confirmed at $0, no container.
- **Tiny-oracle run** (`modal run …::tiny`): see the coordinator hand-off.

## Coordinator run commands

Source a **non-capped** account first (acct3/acct4 least-spent; acct1 capped —
`../stage1-feasibility-manifest.md` §1). Never print/commit the token.

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth
set -a; source ~/.config/kot/modal3.env; set +a         # or modal4.env
export COLIBRI_GIT_URL="https://github.com/JustVugg/colibri"

# 1) $0 dry-plan (already MEASURED-green on OCI)
poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py::plan

# 2) ~$0 tiny-oracle validation (real colibri, tiny GlmMoeDsa)
poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py::tiny

# 3) the real <=$3 smoke — OCI, 4 cores/64 GiB, 900 GiB ephemeral SSD, DRAFT=0
#    stages 383.8 GB (~10-30 min @ hf_transfer), then iobench + 12 traced probes.
poc/modal/.venv/bin/modal run poc/modal/modal_glm52_smoke.py
```

Stop-losses: `$25` in-runner ceiling + a 2 h smoke wall cap. The estate is staged
to **local ephemeral SSD**, never a `modal.Volume` (a network mount recreates the
failed 9p condition). The Function fails closed if its worker turns out to be AWS.
