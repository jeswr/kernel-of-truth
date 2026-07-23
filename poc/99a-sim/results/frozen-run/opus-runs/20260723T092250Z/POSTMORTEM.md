# 99a frozen full-grid v1 run — POST-MORTEM (OPUS experiment-runner)

Run: app `ap-SEsbGWFqXseXM7lADUiHHS`, launched 20260723T092250Z, driver pid 2240987.
Status: **LOST** — no `grid-results.json` written; ~71 completed cells lost.

## 1. Death cause — DEFINITIVE (not box OOM)

The driver crashed at **15:06:47Z** (5h44m in) with, from `grid-run/driver.log`:

```
grpclib.exceptions.GRPCError: (<Status.FAILED_PRECONDITION: 9>,
  'workspace ac-eD1aaY3npNEubBCLiCaVHF is disabled', None)
```
in `parallel_map.pump_inputs -> MapStartOrContinue`. On a subsequent compute
attempt the workspace now returns `RESOURCE_EXHAUSTED: 'Workspace
ac-eD1aaY3npNEubBCLiCaVHF has exceeded its spend limit'`.

Root cause: **the Modal workspace hit its configured SPEND LIMIT**, which disabled
the workspace server-side mid-run, failing the map gRPC stream and crashing the
driver. NOT a box OOM: driver RSS ~86 MB; `free -m` showed ~432 MB free / ~3.3 GB
available; no OOM-kill in dmesg. The box was never the constraint.

## 2. Results unrecoverable — CONFIRMED

`grid-results.json` ABSENT; `grid-run/cells/` has 0 files; driver + app gone
(app `stopped`, 0 tasks). The v1 driver used `run_cell_job.map(..., order_outputs=True)`,
which holds ALL completed-but-not-yet-yielded results in the LIVE client's reorder
buffer, blocked on cell 0 (which never got a preemption-free R=40k run in 5h44m).
When the client crashed, the ephemeral app died and the buffer was lost. There is
no Modal-side retained map output and no reconstructable call-IDs for an ephemeral
`app.run()`. Unrecoverable.

Contributing factor: 100 preemptible `cpu=1` containers -> heavy CPU-preemption
churn (e.g. an 11-container mass-preemption/retry burst at 14:22Z) -> ~2.4x
slowdown vs the box/warm bench + retry restarts -> the run trended toward ~500
core-h / a 6h tail, and pushed the workspace over its spend limit.

## 3. Sunk cost

Accumulated ~**386 core-hours** at death (guard integral, 15:06:47Z). At Modal CPU
$0.135-0.192/core-h + memory ≈ **$58-88**. The workspace hitting its spend limit
is the billing-side confirmation that the run reached the workspace's Modal spend
cap. Exact $ is on the `jmwright-045` / workspace `ac-eD1aaY3npNEubBCLiCaVHF`
dashboard (account-owner view).

## 4. Monitoring defect (noted)

The `grid_guard.py` DID correctly detect driver death (fired 15:06:47Z, reason
`DRIVER-DIED`, tasks history [43,40], core-h ~386). But the harness relay monitor
`bzpkamp3b` (which watched for the guard's "GUARD FIRED" string) FAILED (exit 1)
and did not re-invoke me — a relay defect (poller-watches-wrong-signal). Future
monitors should watch the durable artifact + process liveness directly.

## 5. Fix — v2 harness (`results/frozen-run/kot_99a_grid_v2.py`) — total-loss-proof

- **order_outputs eliminated**: single container runs cells with an in-container
  process Pool (BLAS threads pinned to 1/worker), results streamed as completed.
- **Durable per-cell writes** to a Modal Volume `kot-99a-grid-vol`, keyed by
  config_index, **committed after EVERY cell**; **collection DECOUPLED** (a
  separate `collect` reads the Volume) so a client/app death never loses cells.
- **Resumable**: (re)launch reads the Volume, skips written cells, runs only the
  remainder -> a preemption/spend-pause just resumes.
- **Churn-free**: ONE `cpu=32` container (dedicated cores at ~bench rate) instead
  of 100 preemptible `cpu=1` containers.

**Local harness-logic validation: GREEN** (box, `test_v2_logic.py`) — durable
per-cell writes + decoupled collect + resume-skip all correct, INCLUDING partial-
loss recovery (deleted one cell file -> only that cell recomputed, the other
stayed skipped). This is the exact v1 failure mode, now fixed.

**Pinned-image tiny green validation on Modal: BLOCKED** on the workspace spend
limit (RESOURCE_EXHAUSTED). Volume `kot-99a-grid-vol` was created (metadata op
works); function execution is refused until the spend limit is raised/reset.

## 6. Recommended re-run config (cheap-correct path; NOT launched — awaiting go)

- Harness: `kot_99a_grid_v2.py`, single `cpu=32` container, in-Pool 30 workers,
  durable Volume + resume, timeout 6h.
- Projected: ~**108.7 core-hours** at bench rate (churn-free) -> **~$15-25**
  (Modal CPU + memory), **~3.5-4.5h** wall-clock. Resumable, so any interruption
  just continues from the Volume (no re-spend on completed cells).
- Pre-run fail-closed gate re-verification (unchanged): pins (6), estimator wiring
  (R11a exact-REML A+B), B2 fixture (R12a), S8 hash, determinism, small-slice.

**Blocked on: (a) maintainer raising/resetting the Modal workspace spend limit
(workspace `ac-eD1aaY3npNEubBCLiCaVHF`), or an alternative compute workspace; and
(b) the coordinator's launch go.** No re-run launched.
