# Stage 1 — Backend-feasibility manifest (GLM-5.2 expert profiling)

> **$0 audit, no GPU, no payload download.** Produced by the coordinator's
> feasibility-runner against the Stage-1 spec in
> `docs/next/design/glm52-expert-profiling-plan-sol-20260715.md`
> ("Backend-feasibility gate" + step 1 of "First three coordinator-dispatchable steps").
> Method: Modal CLI/SDK introspection (no Function launched, $0), HF Hub
> metadata only (config + safetensors **headers** via HTTP range reads — no
> multi-GB shard payload fetched), and reconciliation against the committed
> traces / colibri docs. **Uncommitted — the coordinator commits after review.**
> Machine-readable ledger written alongside: `expert_ledger.csv` (76 rows),
> `expert_ledger_summary.json`.
>
> Tags: **[MEASURED]** = observed this pass from an authoritative source;
> **[ESTIMATE]** = projected/derived; **[REPORTED]** = taken from a prior note
> or external doc, not independently confirmable here.

---

## 1. Modal / cloud account audit

### 1a. Per-account status

Env files `~/.config/kot/modal.env` (acct1), `modal2/3/4.env` (chmod 600; tokens
never printed or written anywhere in this pass). Probed with the pinned client
`poc/modal/.venv/bin/modal` **v1.2.6**. **Credit balance is not exposed by the
Modal CLI or SDK** — it is dashboard-only — so per-account headroom below is
`UNKNOWN-from-CLI`; the actionable signal is token validity + workspace
distinctness + the prior cap report.

| Acct | Env file | Token | Auth (`modal app list`) | Workspace signal | Credit headroom | Notes |
|---|---|---|---|---|---|---|
| acct1 | `modal.env` | `MODAL_TOKEN_ID` only (**no SECRET**) | [MEASURED] OK (falls back to `~/.modal.toml` token) | app list empty | **spend limit REACHED** [REPORTED] | env incomplete; effectively uses the local toml profile `jmwright-045`. Treat as **capped — do not dispatch.** |
| acct2 | `modal2.env` | ID+SECRET | [MEASURED] OK | [MEASURED] sees `ap-SVY8ZBZjVzZB3XhvS1rKm7` (kot-nsk1-r3 bridge, *stopped*, created 2026-07-15 02:23 UTC) | UNKNOWN-from-CLI | live/known-good; recently used. |
| acct3 | `modal3.env` | ID+SECRET | [MEASURED] OK | app list empty | UNKNOWN-from-CLI | valid token, no recent apps → likely least-spent. |
| acct4 | `modal4.env` | ID+SECRET | [MEASURED] OK | app list empty | UNKNOWN-from-CLI | valid token, no recent apps → likely least-spent. |

Caveats: `modal profile current` returns `jmwright-045` under **all four** env
tokens — this is the local `~/.modal.toml` active-profile *name*, echoed
regardless of the env token, **not** a per-token workspace identity. That
acct2's `app list` shows an app the others don't [MEASURED] indicates the
tokens do **not** all resolve to one shared view (consistent with distinct
accounts/workspaces, or at minimum acct2 distinct). Confirm true workspace +
credit for each on the Modal web dashboard before dispatch.

### 1b. Platform capabilities (apply to any funded account) [MEASURED unless noted]

| Capability | Finding | Source |
|---|---|---|
| Force **non-AWS** cloud | **YES** — `cloud=` accepts `aws, gcp, oci, auto` | SDK source `modal/app.py:721` (docstring), Oracle case-study confirms Modal runs on OCI |
| Region pin | `region=` supported; adds a pricing multiplier; "contact sales" for granular regions | Modal region-selection docs |
| Max ephemeral SSD | default **512 GiB**, raisable to **3.0 TiB** (`ephemeral_disk`) | Modal resources docs |
| CPU | physical cores via `cpu=` (float); soft limit = request + 16 cores; `cpu=4.0` trivially allowed | Modal resources docs |
| RAM | `memory=` (MiB), request/limit tuple supported; 64 GiB well within limits | Modal resources docs |
| Max job duration | up to **24 h** per Function | Modal timeouts docs [REPORTED via plan] |
| Custom C build (colibri `setup.sh`, gcc+OpenMP, AVX2) | **YES** — Modal images run arbitrary `apt_install`/`run_commands`/dockerfile at build time; C compiled at image build | SDK image API (not yet exercised for colibri → [ESTIMATE] it builds clean) |
| SDK params exist | `cpu, memory, ephemeral_disk, timeout, cloud, region, gpu, image, block_network` all present | `inspect.signature(modal.App.function)` [MEASURED] |

**Which account(s) can host a non-AWS CPU Function with ≥600 GB ephemeral SSD:**
the capability is platform-wide (not account-gated). Among the four, **acct3 or
acct4** are the recommended primary host (valid tokens, no recent spend → likely
fullest credit), **acct2** as backup (valid, known-good, but partly used).
**acct1 is excluded (capped).** Final choice pending dashboard credit check.

### 1c. Recommended non-AWS backend config

```python
@app.function(
    cloud="gcp",           # or "oci"; assert placement != aws at runtime (fail closed)
    region=None,           # let scheduler pick within cloud; pin only if a cheap region is confirmed
    cpu=4.0,               # 4 physical cores
    memory=65536,          # 64 GiB (colibri needs only >=16 GiB; headroom for RSS<60 GiB gate)
    ephemeral_disk=921600, # ~900 GiB  <-- NOT 600 GiB; see blocker B2
    timeout=24*3600,       # 24 h
    # NO modal.Volume mount for the model (network mount recreates the failed 9p condition)
)
```

**Cost** [ESTIMATE, prices per plan's Modal-pricing citation, not re-fetched]:
base = 4×$0.0472 + 64×$0.0080 = **$0.70/core-set-hour**; with a 1.5–1.75×
provider/location premium ≈ **$1.05–1.23/hr**. Smoke (stage 383.8 GB + benchmark
+ 12 probes ≈ 1–2 h wall) ≈ **$1.5–2.5 < $3**. A 480-item Wave A at the plan's
100 s/prefill ≈ 13.3 compute-h ≈ **$9–17**.

**Stop-losses (hard):** smoke — kill at **$3** or **2 h** wall, whichever first.
**Wave-A — $25 stop-loss** (kill the wave and do not scale if projected or actual
spend crosses $25; the go/no-go also requires the 480-item projection to land
< 20 h and < $25 before dispatch).

---

## 2. Reconciled expert ledger — 19,456 vs 21,504 **RESOLVED** [MEASURED]

Built **without any payload download**: HF `list_repo_files` + `config.json` +
HTTP range-reads of the safetensors **headers** of all 144 shards (there is **no
`model.safetensors.index.json`** in the repo — the shard→tensor map exists only
in each shard header, which this pass parsed directly).

**Estate:** `mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp` — 150 files,
**383.76 GB** total (357.4 GiB) [MEASURED from LFS sizes]: 141 main shards
`out-00000..00140` (373.8 GB) + 3 MTP shards `out-mtp-00000..00002` (9.96 GB) +
config/tokenizer (20 MB). Base = `zai-org/GLM-5.2-FP8`; `config.json`:
`num_hidden_layers=78`, `first_k_dense_replace=3`, `n_routed_experts=256`,
`n_shared_experts=1`, `num_experts_per_tok=8`, `num_nextn_predict_layers=1`,
`scoring_func=sigmoid`, `topk_method=noaux_tc`, `hidden_size=6144`.

### The stored routed-expert population (authoritative, from headers)

| execution_site | main_or_mtp | layers | layers×256 | routed cells | reachable_mode (DRAFT=0 main atlas) |
|---|---|---|---|---|---|
| main_model | main | sparse layers **3–77** (75 layers) | 75×256 | **19,200** | routed / replaceable |
| mtp_head | mtp | layer **78** (1 layer) | 1×256 | **256** | routed **MTP-only** — speculative; **excluded at DRAFT=0**, separate sweep needed |
| **TOTAL** | | | | **19,456** | = the committed trace's 76 layers (3–78) × 256 |

Each routed cell stores exactly 6 tensors: `{gate_proj, up_proj, down_proj} ×
{.weight (packed), .weight.qs (F32 scale)}`. Not part of the routed-replacement
population: **76 shared_experts** (1 per MoE layer 3–78), **76 routers**
(`gate.weight` + `gate.e_score_correction_bias`), **3 dense MLP layers** (0–2, no
experts). Per-layer detail in `expert_ledger.csv`.

### Reconciliation of the count discrepancy

- **[MEASURED] Disk truth = 19,456**, byte-for-byte identical to the trace's
  19,456 addressable cells. There is **no hidden "stored-but-unreachable"
  routed-expert population** in this estate, and **no converter/container
  duplication** of experts (each cell appears once).
- **[MEASURED] The colibri "21,504" is a documentation error, not a real
  population.** Colibri's own headline says *"21,504 routed experts (75 MoE
  layers × 256 experts + the MTP head …)"* — but that parenthetical formula
  evaluates to 75×256 + 256 = **19,456**. Colibri's Brain-page and the Expert
  Atlas issue #175 both use **19,456**. 21,504 (= 84×256) is not reproducible
  from any GLM-5.2 config field (78 layers, 75 sparse, 1 MTP) and appears to be
  a stale/miscopied number in one colibri doc. The 2,048-cell gap (=8×256) has
  **no backing tensors** on disk.
- **Nothing is "missing" for reconciliation** — it is complete from metadata.
  A payload-level pass is **not required** to settle the count. It *would* only
  be needed to (optionally) materialize per-expert byte-offsets / weight hashes
  (already available cheaply from the same headers) or to verify the container
  format nuance below.

**Container-format note** [MEASURED]: `config.json.quantization_config` reads
`fp8/e4m3` (inherited from the FP8 base), while the repo is colibri **int4** with
per-row `.qs` scales; the README states the **MTP heads are int8** (required —
int4 MTP heads have ~0% acceptance, "useless"). This does not affect the count
reconciliation but means: (a) MTP characterization is a distinct int8 / DRAFT≥1
sweep, and (b) any weight-structure signatures (Stage 3.4) must read colibri's
int4 packing, not the fp8 config claim.

### Free cross-validation [MEASURED]

colibri **Expert Atlas** issue #175 (github.com/JustVugg/colibri/issues/175) is
**real, open, active** (opened 2026-07-14 by ZacharyZcR). It does exactly the
`.coli_usage` snapshot-differencing profiling over 19,456 experts, and plans to
publish **raw diffs + an aggregated `experts.json` atlas**. Scope is small
(10 categories × 3 prompts × 64 tokens) and **category-aggregated** on a 6×5090
GPU rig — i.e. routing-affinity only, **not per-item and not causal**. Import
the raw diffs when published **as cross-validation only**, after checking model
hash, tokenizer, prompt bytes, and execution mode (per the plan's caveat).

---

## 3. Recommendation on the `<$3` backend smoke: **GO (conditional)**

Not `NEEDS-PAYLOAD-PASS` — the expert reconciliation is already complete from
metadata, so the smoke has no inventory blocker. Every $0 precondition now
passes:

- ✅ Non-AWS backend feasible (`cloud=gcp|oci` MEASURED).
- ✅ ≥600 GB ephemeral feasible (max 3.0 TiB; **set ≥900 GiB — see B2**).
- ✅ Expert ledger reconciled (19,456; no hidden/duplicate experts).
- ✅ Model present & sized on HF (383.8 GB, direct-to-ephemeral staging).
- ✅ colibri C/OpenMP/AVX2 build possible in a Modal image.

**The smoke is worth running** — its sole remaining purpose is to measure the
**one genuinely unmeasured make-or-break**: local **ephemeral-SSD random-read
bandwidth ≥1 GB/s** for colibri's 19 MB/expert reads (the 9p network-mount
regime that gave 0.01 tok/s is explicitly avoided by using local ephemeral SSD,
not a Volume), plus trace-integrity and throughput→cost projection.

**GO is conditional on two gates the coordinator must clear first:**
1. Pick a **non-capped** account (acct3/acct4 preferred, acct2 backup) with
   **dashboard-confirmed credit ≥ $25** (covers smoke + Wave-A headroom). acct1
   is capped — excluded.
2. Set `ephemeral_disk ≥ 900 GiB` (not the plan's 600 GiB — B2).

If neither acct2/3/4 has ≥$3 confirmed credit, the smoke is **NO-GO until
funded** (the fallback is `PROXY-ONLY` on GLM-4.7-Flash to build the machinery,
per the plan — but that does not characterize GLM-5.2 experts).

---

## 4. Blockers

- **B1 [HARD, external] — Credit visibility.** Modal exposes no CLI/SDK credit
  balance; must confirm ≥$25 on acct2/3/4 via the web dashboard before dispatch.
  acct1 is reported capped. Cannot be closed from this box.
- **B2 [CONFIG FIX] — 600 GiB ephemeral contradicts the plan's own go/no-go.**
  MEASURED payload is 383.8 GB; the gate "≥400 GB free after staging" needs
  ≥784 GB → **the plan's 600 GiB (≈644 GB → only 260 GB free) FAILS its own
  gate.** Raise `ephemeral_disk` to **≥900 GiB** (≈582 GB free) or 1024 GiB.
  Also set `HF_HUB_ENABLE_HF_TRANSFER=1` and download straight to the ephemeral
  path with `--local-dir` (no blob-cache symlink duplication) to avoid a
  transient ~2× (768 GB) disk spike.
- **B3 [THE EXPERIMENT] — colibri local-SSD random-read bandwidth is unproven.**
  Modal ephemeral is local NVMe (not 9p), so ≥1 GB/s is *plausible* but
  unmeasured — this is precisely what the smoke tests; treat as the primary
  make-or-break, not a pre-cleared assumption.
- **B4 [SCOPE] — MTP layer 78 (256 cells) is int8 / DRAFT≥1-only.** It is
  excluded from the DRAFT=0 main-model atlas and requires a separate speculative
  sweep if MTP characterization is wanted. Keep it enumerated-but-unreached in
  the ledger, do not conflate with the 19,200 main cells.
- **B5 [PLACEMENT] — non-AWS fail-closed.** Modal schedules across providers;
  the Function must assert its actual placement is not AWS at runtime and abort
  if it is (the plan's "fail closed if scheduling reports AWS").

---
*Artifacts written this pass (uncommitted): `stage1-feasibility-manifest.md`,
`expert_ledger.csv`, `expert_ledger_summary.json` in `poc/glm52-probe/`.*
