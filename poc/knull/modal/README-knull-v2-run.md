# knull-v2 campaign — coordinator launch sequence

The verdict-bearing GPU run of the **FROZEN** record
`registry/experiments/knull-v2.json` (frozen 2026-07-13T15:09:36Z, in
`registry/frozen-index.json`). Built + mock-validated at $0 by the designer
harness role; **the coordinator owns every step below that spends or
launches.** The designer identity that built the record never runs, grades,
or audits it (run != audit).

## What runs

| piece | file |
|---|---|
| campaign runner (verdict-bearing records) | `poc/knull/runner/knull_runner_v2.py` |
| Modal transport (A100-40GB, f2b image) | `poc/knull/modal/modal_knull_run.py` |
| slice merge (account fan → canonical records) | `poc/knull/runner/merge_knull_slices.py` |
| pinned SAP the records feed | `analysis/knull_v3.py` (record `pins.analysis_script`, sha `54528cd4…`) |

36 GPU cells (knull-v2.json): 4 arms × alone-R1 + {kernel,plain,opaque} ×
alone-R3 (**plain-padded excluded, ASM-1086**) + 4 arms ×
verify-retry-R1(k=4) + kernel shuffled-verify-retry-R1 (derangement seed
20260710, f2b bridge verbatim), seeds {0,1,2}, n=1000 rank-prefix paired
skeletons per arm. Arms differ ONLY in records_root + item file (the pinned
f2b machinery is imported byte-identical at sha `b62c3a72…`, fail-closed).
The runner emits RAW records only — the verdict belongs to
`analysis/knull_v3.py` + verdict-gen.

Fail-closed pins the runner re-verifies **in-container before touching a
model** (`KNULL2_ERR_*`): record FROZEN + indexed; SAP sha; f2b-machinery
sha; all 4 item-file shas; every per-file store sha (3×108 files; kernel
records re-verified per item at load); prompt-token sidecar sha
(`d9312f19…`); n frozen at 1000; skeleton pairing + type-mix identity
across arms; model revisions from `pins.model_revisions`.

## 0. $0 local validation (already run green; re-runnable any time)

```bash
# full 36-cell mock (StubLM, CPU, no torch) + SAP ingest
python3 poc/knull/runner/knull_runner_v2.py --mock --out-dir /tmp/knull2-mock \
    --checkpoint-dir /tmp/knull2-ckpt --items 60
python3 analysis/knull_v3.py --records /tmp/knull2-mock/run-records.jsonl \
    --item-meta /tmp/knull2-mock/item-meta.json --out /tmp/knull2-mock/analysis-mock.json
```

Validated 2026-07-13: 36/36 cells; SAP rc=0; **all 68 frozen
`output_fields` pointers resolve**; the ONLY false gate on mock is
`/gates/flops_parity` — exactly the record's disclosed stipulated mock
artifact (StubLM token proxy; carries no information about the real gate,
which resolves via the run-time HFLM-metered F0 ledger, ASM-1088).
Per-item checkpoint/resume validated (mid-cell kill → identical cov/acc on
resume); 4-way arm fan + merge validated byte-identical to the single run.

```bash
# cost plan vs the frozen caps ($0)
python3 poc/knull/runner/knull_runner_v2.py --dry-plan
# staged-bytes sha for the run log ($0, no modal import)
python3 poc/knull/modal/modal_knull_run.py --print-manifest
```

## 1. Transport smoke (~pennies, CPU container, loudly MOCK)

```bash
source ~/.config/kot/modal.env
poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_run.py --mock
```

Results land in `poc/knull/results-incoming/<stamp>-modal-knull2-mock-…/`
with provenance sidecars. Confirm `RUNNER_EXIT` is `rc=0` and the mock
records ingest exactly as in step 0.

## 2. Launch gates (before any GPU cell)

1. `registry/experiments/knull-v2.json` status FROZEN + in the frozen index
   (the runner also refuses otherwise) — **holds already**.
2. Maintainer Tier-1 sign-off per `runner_constraints.gate` ("GPU spend
   REQUIRES maintainer sign-off + prereg-freeze").
3. Record the `--print-manifest` sha in the campaign run-log (the
   re-pin-at-campaign-start step the record's harness_manifest anticipates).
   Do not edit any staged byte mid-campaign.

## 3. The campaign — how the four arms fan

One slice per Modal account (disjoint by construction; the merge
fail-closes unless the union is exactly the frozen 36-cell plan). 4
concurrent jobs ≤ the record's `concurrency_cap` 5.

| account env | `--arms` | cells | worst-case est.* |
|---|---|---|---|
| `~/.config/kot/modal.env`  | `kernel`       | 12 (incl. shuffled bridge) | ~0.73 GPU-h |
| `~/.config/kot/modal2.env` | `plain`        | 9  | ~0.32 GPU-h |
| `~/.config/kot/modal3.env` | `plain-padded` | 6 (ASM-1086) | ~0.25 GPU-h |
| `~/.config/kot/modal4.env` | `opaque`       | 9  | ~0.52 GPU-h |

\* from `--dry-plan` (pinned A100 planning table, 2.0× overhead); the
record's own planning estimate is 4–6 GPU-h / $15–30 total — planning
numbers, never measurements.

```bash
TAG="knull-v2-$(date -u +%Y%m%d)"   # ONE tag for the whole campaign
CAMP="poc/knull/results-incoming/$TAG"; mkdir -p "$CAMP"
i=0
for arm in kernel plain plain-padded opaque; do
  i=$((i+1)); envf=~/.config/kot/modal$( [ $i -eq 1 ] || echo $i ).env
  ( set -a; . "$envf"; set +a
    exec nohup setsid poc/modal/.venv/bin/modal run \
      poc/knull/modal/modal_knull_run.py \
      --confirm-spend --arms "$arm" --tag "$TAG" --out-root "$CAMP" \
  ) > "$CAMP/slice-$arm.launch.log" 2>&1 &
done
tail -f "$CAMP"/slice-*.launch.log
```

`nohup+setsid` per the standing bd memory (E5 lesson). **HYGIENE:** a
killed client does NOT stop the remote task — `modal app stop ap-<id>`
under THAT account's env (grep `ap-` from its launch log).

Serial fallback (one account, still well under caps): run the same command
four times, or once with the default `--arms` (all four, ~1.8 GPU-h
worst-case).

### $60 cap accounting

- `budget` block (knull-v2.json): `usd_cap 60`, `gpu_hours_cap 8`,
  `wall_clock_cap_hours 24`; Tier-1 `tier_cap_usd 60`.
- Hard ceiling: 8 GPU-h × pinned $2.10/h (F0 table) = $16.80; even at
  Modal's current A100 list (~$2.50–4/h) the 8 GPU-h ceiling stays ≤ $32
  ≪ $60. Dry-plan worst case: **1.82 GPU-h ≈ $3.82** (whole campaign).
- Enforcement in-run: `--max-hours` (default 8 = gpu_hours_cap) aborts
  checkpointed between cells; per-cell CellGuard timeout 7200 s; Modal
  function timeout 12 h ≪ wall cap 24 h.
- Track actual spend on each account's Modal dashboard; a resumed slice
  recomputes $~0 (per-item checkpoints on the `kot-knull-v2-ckpt` volume,
  committed every 120 s).

### Crash / preemption

Relaunch the SAME command (same `--tag`, same `--arms`): finished cells
re-emit from checkpoint without touching a model; a part-done cell resumes
at its first missing item. Cov is deterministic per item (greedy attempt-0;
seeded generator for retries), so resumed cells are identical to
uninterrupted ones — validated in mock.

## 4. Collect → merge → analysis

Each slice unpacks to `$CAMP/<stamp>-modal-knull2-<arm>/` (check
`RUNNER_EXIT` = `rc=0` in each).

```bash
python3 poc/knull/runner/merge_knull_slices.py \
    --slices "$CAMP"/*-modal-knull2-kernel "$CAMP"/*-modal-knull2-plain \
             "$CAMP"/*-modal-knull2-plainpadded "$CAMP"/*-modal-knull2-opaque \
    --out-dir "$CAMP/merged"
python3 analysis/knull_v3.py --records "$CAMP/merged/run-records.jsonl" \
    --item-meta "$CAMP/merged/item-meta.json" --out "$CAMP/merged/analysis.json"
```

Then hand off: verdict-gen + the cross-vendor audit grade the analysis
document against the record's `verdict_rules`
(INSTRUMENT-INVALID / NULL / PASS / FAIL / INCONCLUSIVE — the runner and
this transport never conclude). Nothing is auto-committed — review and
commit deliberately.
