# P3-LR-SYS — Lifecycle cost, systems benchmarking, storage/I-O economics

**Bead:** P3-LR-SYS (Programme-3, Phase-0 [LIT]).
**Deliverable path:** `reports/lit-p3-sys.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is
frozen, registered, or scheduled; no registry record / ASM / KB shard is touched.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §1.2
(KOT-SIZE/2), §1.3 (KOT-COST/2), §1.3a (KOT-LIFE/1), §5 P3-LR-SYS row.
**Feeds:** P3-D-HW (cost-rig operating manual), P3-D-LIFE (lifecycle ledger),
P3-D-INDEX (cost-rig co-input) inside the KOT-FAIR/2 freeze.

> **Relationship to `docs/next/lit/SYS.md`.** A prior, thorough SYS review exists
> (Fable, 2026-07-11, bead …s55r.3, with a source ledger `SYS.sources.jsonl`).
> This report is an **independent re-verification pass at the requested
> `reports/` path**, not a replacement. Where I re-fetched a source this session
> I say so and flag any divergence from the 07-11 extract; where I did not, I
> cite the 07-11 verification and mark it as such. The one material divergence I
> found (Sardana's real-cost worked numbers) is flagged in Q6 and the citation
> table — treat it as a WebFetch numeric-extraction reliability caution, not a
> factual dispute.

## Epistemic tag convention
- `[established]` — external empirical/methodological fact confirmed at a primary
  source. `[claimed]` — asserted in a source but not independently corroborated,
  or a single-source figure. `[speculative]` — my forward inference / design
  judgement.
- Provenance suffix: `[search: <date>]` = verified via WebSearch/WebFetch this
  session (2026-07-19) unless another date given; `[memory]` = from the parent
  doc or in-repo verdicts, not re-checked at source; `[prior-verified: 2026-07-11]`
  = verified at source by the 07-11 SYS.md, cited here without re-fetch.
- `[UNVERIFIED]` marks anything I could not confirm at source this session
  (usually because the fetcher returned binary/truncated content).

---

## Q1. MLPerf inference scenarios + power methodology in operational detail

### Findings — scenarios (LoadGen semantics)
`[established][search: 2026-07-19]` MLCommons MLPerf-Inference defines **four
scenarios** with distinct query-issue semantics (verified against the live
`inference_rules.adoc`, master branch):
- **SingleStream** — **closed-loop**: LoadGen issues the next query as soon as
  the system-under-test (SUT) completes the previous one; 1 sample/query; reports
  the **90th-percentile early-stopping latency** estimate. This measures isolated
  *service time*.
- **MultiStream** — **closed-loop**: like SingleStream but 8 samples/query;
  reports the **99th-percentile early-stopping latency**.
- **Server** — **open-loop**: LoadGen issues queries on a **Poisson** arrival
  schedule; reports the **maximum Poisson throughput** sustainable under a
  per-benchmark latency bound.
- **Offline** — batch: all samples issued at once (min 24,576 samples in one
  query); reports **throughput**.

`[established][search: 2026-07-19]` **Minimum run duration is 600 s** for
SingleStream/Server/MultiStream. The **early-stopping criterion** lets a run with
relatively few processed queries be valid by widening the percentile confidence
adjustment once the SUT clearly exceeds the latency threshold — it operates
**after** the 600 s minimum is met and **does not replace it**. (This corrects a
common misreading; the 23,886-query figure is a *worked example*, not a universal
required sample size — `[prior-verified: 2026-07-11]`, consistent with my read.)

`[established][search: 2026-07-19]` **Caching rules:** caching queries, responses,
or intermediate/derived results **across queries is prohibited**; **KV-cache is
allowed only as in the reference model and only within a query** (not across);
caching values derived from input-tensor *shapes* is allowed.

`[established][search: 2026-07-19]` **LLM latency constraints** are given as
TTFT/TPOT pairs and bind at (essentially) the **99th percentile**: Llama3.1-8B
2000/100 ms (conversational) and 500/30 ms (interactive); Llama2-70B 2000/200 and
450/40; Llama3.1-405B 6000/175 and 4500/80. The exact per-benchmark binding
percentile should be re-confirmed at the P3-D-HW freeze (see Open Questions).

### Findings — power methodology
`[established][search: 2026-07-19]` MLPerf Power (Tschand et al., "MLPerf Power:
… Microwatts to Megawatts", arXiv 2410.12032v2):
- **Full-system wall power is the fundamental tenet** — measure the whole system,
  not a component.
- **Instrumentation is tier-dependent:** edge → a **SPEC-certified analyzer
  (e.g. Yokogawa WT310) driven by SPEC PTDaemon**; datacenter → IPMI/RedFish
  telemetry; tiny → external current/voltage-waveform capture.
- **Boundary:** compute + interconnect are *in*; **cooling and storage nodes are
  explicitly excluded** ("future work").
- **Calibration:** a *range-fixing* run finds max current/voltage; subsequent runs
  use fixed analyzer ranges for accuracy.
- **Duration/energy:** **≥60 s of power data**; if the workload is shorter it is
  **run in a loop**; energy = **integral of power samples over the run window**,
  summed across components — *not* query-level spot reads.
- **Metric:** (samples/s)/W = **samples/joule** (throughput), or 1/joules
  (latency benchmarks).
- **Stated pitfalls:** **TDP is a thermal limit, not a power proxy**; cloud
  facilities that meter only at PDU level cannot isolate a node; measuring an
  isolated component misses the dynamic interplay.

### What we can actually implement (operational)
`[speculative]` **Scenarios: mostly implementable.** SingleStream (isolated
p50/p95 service time) and Offline (throughput) are directly reproducible with our
own LoadGen-equivalent on the CPU box and free GPUs. Server requires a
**genuine open-loop Poisson generator** (see Q3 — coordinated omission);
implementable but must not be faked with a closed-loop client.
`[speculative]` **Power: the discipline is implementable, the instrument is not.**
We cannot attach a SPEC-certified external analyzer to a free-cloud GPU or a
virtualized CPU box, and MLPerf's own datacenter path assumes IPMI/RedFish
telemetry we do not control. We therefore **inherit the MLPerf *discipline*
(whole-run integration, ≥60 s / loop-short-workloads, joules/query + samples/joule,
report the boundary) on RAPL/NVML counters** and treat the gap as a
**capability limitation, not a fundamental one** — see Q7 and the honest-risk
section.

**Implications.** *KOT-COST/2 rig:* adopt LoadGen-style scenario separation
(closed-loop for service-time percentiles; open-loop Poisson for
throughput-under-bound). *P3-D-HW:* pin the ≥600 s (or loop-to-≥60 s for energy)
duration and the early-stopping-after-minimum rule; forbid cross-query caching in
the harness exactly as MLPerf does. *KOT-COST/2 energy:* whole-run integration is
mandated; **the measurement boundary must be reported as a first-class field**
because ours will not be full-system.

---

## Q2. Latency-percentile / throughput / TTFT measurement practice

### Findings
`[established][search: 2026-07-19]` **Coordinated omission** (Gil Tene, wrk2
README, verified): closed-loop load generators *coordinate with the server* — when
the SUT stalls, the client waits and simply **fails to issue (and therefore fails
to measure) the requests that would have seen the high latency**. Worked example:
a **1.4 s stall** yields an uncorrected **p99 of 6.04 ms** vs a corrected
**p99 of 1.27 s — ~200×**. Fix: a **constant-throughput (open-loop) schedule**
with latency measured from the **intended** send time, not the actual send time.
**Scope note (important):** this is a failure of *closed-loop latency-under-load*
measurement; closed-loop measurement of *isolated service time* (MLPerf
SingleStream-style, one query at a time) is **not** invalidated by it.

`[established][memory / prior-verified: 2026-07-11]` **TTFT vs TPOT are separate
SLOs** for generative serving (DistServe, OSDI 2024): time-to-first-token
(prefill-bound) and time-per-output-token (decode-bound) behave differently, and
"goodput" is the max request rate meeting **both** — colocating prefill and decode
can cost 7.4× throughput or 12.6× SLO tightness. This is an accounting/scheduling
distinction, not a FLOP distinction.

### Implications
- *KOT-COST/2 (f)(g)(i):* measure **p50/p95 service time with a closed-loop
  single-query harness**; measure **throughput-under-latency-bound with an
  open-loop Poisson generator** — using a closed-loop client for the throughput
  number would import coordinated omission and silently inflate apparent capacity
  (a live gaming surface for any arm that has occasional long stalls, e.g. a
  verifier-retry loop). For generative arms report **TTFT and inter-token latency
  separately**, never a single blended latency.
- *P3-D-HW:* percentiles must be reported with **rank-based, distribution-free
  confidence intervals** (Hoefler R8; Q5), and the load generator must record
  intended-vs-actual send times so coordinated omission is detectable.

---

## Q3. Warm vs cold cache + startup / model-load accounting

### Findings
`[established][search: 2026-07-19]` MLPerf prohibits cross-query response/result
caching but allows within-query KV-cache; it requires the **cache state to be
disclosed**. `[established][memory / prior-verified: 2026-07-11]` File-system
benchmarking practice (Traeger et al., "A Nine Year Study…", ACM ToS 2008):
**disclose cache state; clear caches before *each* cold run** (remount / purge /
allocate-and-free); report full system state. `[memory]` The parent doc already
splits this: KOT-COST/2(h) requires **warm and cold both, including
startup/index-load time**; KOT-SIZE/2 figure-(4) = **cold-start working set +
total bytes read to first answer**.

### Implications (attribution rule)
`[speculative]` Concrete protocol P3-D-HW should adopt:
- **Cold** := fresh process/container, model + index **not resident**, OS page
  cache dropped (`echo 3 > /proc/sys/vm/drop_caches` or remount, per Traeger),
  measured once per definition-of-cold. Record **model-load + index-load time**
  and **bytes-read-to-first-answer** here.
- **Warm** := steady state after W pinned warmup queries (W pinned per benchmark),
  caches populated.
- **Attribution:** model/index-load cost belongs to the **cold** number only and
  is then **amortized in KOT-LIFE/1 over 10³ / 10⁶ / 10⁹ queries** — a one-time
  load that dominates at 10³ queries is negligible at 10⁹. Reporting only the
  warm number would let a heavy-startup arm hide its load cost; reporting only
  cold would over-penalize a high-volume deployment. **Both, plus the amortization
  curve, is the honest form.** This directly feeds the Sardana framing (Q6):
  optimal size and the load/inference balance depend on deployment volume.

---

## Q4. Hardware repeatability (run-to-run, day-to-day variance control)

### Findings
`[established][search: 2026-07-19]` **Measurement bias is large and unpredictable**
(Mytkowicz et al., "Producing Wrong Data Without Doing Anything Obviously Wrong!",
ASPLOS 2009, verified): **UNIX environment size and link order *alone* shift
measured performance by ~double-digit % (order 20%)** — with no code change.
Biases arise from memory/cache alignment and are not predictable per-benchmark;
remedies are **(i) randomize the experimental setup across runs, (ii) use many
diverse workloads/setups, (iii) causal analysis** to separate a real effect from
an artifact.
`[established][memory / prior-verified: 2026-07-11]` **Hoefler & Belli**,
"Scientific Benchmarking of Parallel Computing Systems" (SC15) — twelve rules;
the statistically load-bearing ones (R3 arithmetic mean for costs / harmonic for
rates; R4 never average ratios, geometric mean only as a last resort; R5 report
CIs for nondeterministic data; R6 don't assume normality; R7 compare via
non-overlapping CIs / ANOVA; R8 percentiles for worst-case/tail; R9 document all
varying factors) — R3/R4 independently corroborated this session `[search:
2026-07-19]`; rank-based distribution-free CIs for medians/percentiles.
`[established][memory / prior-verified: 2026-07-11]` **Traeger:** the **number of
runs is chosen from the observed standard deviation / target CI** (e.g. 95% CI
half-width < 5% of the mean; Student's t below ~30 runs), **not a fixed count**.
`[MEASURED]` Our current box is a **2-shared-vCPU virtualized EC2** (§ CLAUDE.md /
prior verdict) — noisy-neighbour and only 2 cores make variance control the
binding difficulty, not a formality.

### Implications
- *P3-D-HW must pin the environment* (CPU governor = performance / frequency
  pinned, turbo disabled or fixed, thread affinity pinned, background load niced
  and quiesced, fixed env block or *deliberately randomized* per Mytkowicz), and
  **characterize day-to-day variance** with a repeated pinned **calibration
  workload** (this is exactly what P3-E-CAL is for).
- Report **median + distribution-free (rank-based) 95% CI**, choose N so the CI
  half-width meets a target, use **harmonic mean for throughput / arithmetic for
  latency** (R3), **never average ratios** (R4).
- A **repeatability band must gate admissibility**: if day-to-day median drift on
  the calibration workload exceeds the win margin δ_k, the instrument cannot
  resolve the claimed effect and **W1 is not claimable at that rung**. Proposed
  band numbers are in the recommendations, marked [STIPULATED].

---

## Q5. Storage + network I/O economics

### Findings
`[established][memory / prior-verified: 2026-07-11]` **Five-minute rule, thirty
years later** (Appuswamy et al., ADMS@VLDB 2017 / CACM 2019): break-even residency
interval = **(pages-per-\$ of RAM) / (accesses-per-second-per-\$ of the device)**;
at 4 KB pages in 2017, DRAM↔SATA-SSD ≈ **~7 min** (was 15 min in 2007),
DRAM↔NVMe/3D-XPoint ≈ **~40 s**, DRAM↔HDD grew to **hours** (the literal
five-minute rule survives only near 512 KB HDD pages). **Scope limit stated by the
authors:** these break-evens are hardware/price-generation-specific and **do not
cover cloud RAM billing, scale-to-zero, capacity constraints, access skew, or
opportunity cost** — so residency-optimality for *our* stores is a hypothesis for
KOT-LIFE/1, not a licensed conclusion. *(PDF did not re-parse this session —
[UNVERIFIED] at source on 2026-07-19; carried from the 07-11 primary-PDF read.)*
`[established][memory]` KOT-SIZE/2 already treats I/O as first-class: figure-(4)
**total bytes read to first answer**, figure-(6) **remote service/cache/corpus
bytes count** (a remote dependency cannot claim a smaller deployment). KOT-COST/2
(c) counts **bytes read from storage and network** per query.

### Implications
- *KOT-COST/2:* record **bytes-read (storage) and bytes-transferred (network)
  per query** as measured columns, not as a footnote — this is the column in
  which an arm that "offloads to a cheap CPU index / remote store" must show up
  even when its FLOP and energy columns look small (see honest risk).
- *KOT-SIZE/2:* index/store **construction size + construction cost** (figure-(5))
  feed KOT-LIFE/1; the five-minute-rule framing tells us *where a store should
  live* (RAM vs SSD vs remote) is a **cost decision to log, not a free choice** —
  but the paper does **not** license a specific placement for our workload; that
  is a KOT-LIFE hypothesis.
- *KOT-LIFE/1:* the residency/placement decision and its \$ consequence at
  10³/10⁶/10⁹ query volumes is a ledger line, and any **remote store's egress /
  request cost** must be amortized there.

---

## Q6. Inference-volume-dependent optimal sizing — Sardana et al. (VERIFIED AT SOURCE)

### Verification
`[established][search: 2026-07-19]` **Sardana, Portes, Doubov, Frankle, "Beyond
Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws",
ICML 2024, arXiv 2401.00448.** Verified at the arXiv abstract **and** the v2 HTML
full text this session.

### What it establishes
`[established][search: 2026-07-19]`
- **Core result:** modifying Chinchilla scaling to include inference cost changes
  the compute-/cost-optimal `(params, pretraining-tokens)` pair; under **large
  inference demand you should train models *smaller and longer* than
  Chinchilla-optimal**.
- **Empirical:** they trained **47 models** and find **quality (pretraining loss)
  keeps improving out to ~10,000 tokens/param**, well past the Chinchilla ~20.
- **FLOP-optimal ≠ dollar-optimal:** for a Chinchilla-70B at 2 T inference tokens
  the FLOP-optimal deviation is only **+1.3% FLOPs** but the **dollar** gap is
  **~36%**, because inference *output* generation runs at **~1% MFU** vs training
  at **~50% MFU** — the pure-FLOP ledger cannot see this.

`[claimed][search: 2026-07-19]` **Worked numbers (full-text HTML read this
session):** 13B→7B saves 1.7×10²² FLOPs (~17%) at 2 T inference tokens;
30B-quality at 10¹³ inference tokens → **13.6B on 2.84× Chinchilla data, −28%
FLOPs**; real-cost examples 30B @1.5B requests → **8.58B params / 12.1 T tokens,
−58% \$** and 70B @35.1B requests → **21.5B / 27 T tokens, −54% \$**.
**⚠ DISCREPANCY:** the 07-11 SYS.md recorded the 1.5B-request real-cost example as
**16B on 3.35 T tokens, ~17% \$ saving** — materially different from my full-text
fetch's 8.58B/12.1 T/58%. I could not reconcile these two WebFetch extractions
without the PDF's exact table. **Treat all specific Sardana \$-figures as
[claimed] pending a direct-PDF read at the P3-D-LIFE freeze.** The *qualitative*
result and the FLOP-vs-dollar / MFU point are robust across both reads and the
abstract.

### Stated limitations (carry these — they bound what it licenses)
`[established][search: 2026-07-19]`
- MFU and cost-per-FLOP are **assumed independent of model size, config, and
  sequence length**; latency requirements are set aside.
- **Quality is measured as pretraining loss, not a downstream capability index** —
  and the authors note that smaller equal-loss models may in practice have
  **higher** demand (lower latency). So it says nothing directly about a
  capability-index frontier like KOT-AI-INDEX/2.
- Scaling-law fits **misbehave at extreme token/param ratios** (they had to refit);
  47 models → **wide confidence intervals**.
- The dollar model is **explicitly simplified**: fixed utilization, **no
  maintenance / refresh / demand-uncertainty**.

### What it does / does not license here
`[speculative]` **Licenses:** the KOT-LIFE/1 framing — amortize total cost at
**10³/10⁶/10⁹ queries** because optimal size genuinely depends on inference
volume; and it makes **"train longer to deploy smaller"** a legitimate,
name-it-don't-net-it deployment strategy (dimension-drop / donor-inheritance arms).
**Does NOT license:** any "our kernel is Sardana-optimal" claim; any transfer of
its \$ figures to a capability index (its axis is loss); or extrapolation into the
**extreme-ratio regime our reference models already sit in** — SmolLM2-135M is
~14,800 tokens/param and SmolLM2-1.7B ~11 T tokens, both **beyond Sardana's fitted
range** `[established][memory / prior-verified: 2026-07-11]`. In the ledger,
Sardana is **context, not a premise**.

---

## Q7. Energy measurement (RAPL / NVML) — the practical pitfalls

### RAPL (CPU)
`[established][search: 2026-07-19]` (Weaver RAPL reference page, verified):
- Domains **package / PP0(cores) / PP1(uncore-GPU) / DRAM / PSys(platform)** —
  **per-socket only, no per-core or per-process** attribution.
- **Coverage gap:** RAPL sees **CPU package (+ DRAM domain) only** — **not disk,
  NIC, fans, PSU losses, or the rest of the board**. RAPL energy ≠ system energy.
- **Counter wraparound:** energy unit ≈ **15.3 µJ**; the 32-bit counter can
  **overflow in ~60 s** at sustained high power → **must poll within the wrap
  window**.
- **Permissions:** unprivileged `powercap` sysfs reads were **restricted in Linux
  5.10** (power side-channel); the no-permission-check **AMD RAPL driver was
  removed in 5.13** → need root / a configured `perf_event_paranoid`.
`[MEASURED][prior-verified: 2026-07-11]` **Our current CPU box exposes no RAPL at
all** — `/sys/class/powercap` is absent on the 2-vCPU virtualized EC2 host, so
**CPU energy is uncountable by counter on this host.** Must be re-checked per rig
host (Modal containers etc.).

### NVML (GPU)
`[established][search: 2026-07-19]` `nvmlDeviceGetTotalEnergyConsumption` returns
**energy in millijoules since the driver was last reloaded**, supported on
**Volta or newer** (else `NVML_ERROR_NOT_SUPPORTED`); `nvmlDeviceGetPowerUsage`
returns power in milliwatts. Boundary = **GPU board only** (excludes host CPU,
DRAM, cooling, PSU).
`[established][search: 2026-07-19]` **The sensor is duty-cycled** (Yang, Adamek,
Armour, "Part-time Power Measurements: nvidia-smi's Lack of Attention", 2024,
verified): on **A100 and H100 only ~25% of runtime is actually sampled for
power**; external-meter correction cuts energy error by **~35% on average, up to
65%**; 70+ GPUs across all generations since Fermi surveyed.
`[established][search: 2026-07-19]` **Best practice** (ML.ENERGY blog, verified):
prefer the **accumulated energy counter** (two calls + one subtraction) over
integrating instantaneous power polls — polling itself burns energy and adds
integration artifacts. **Caveat I add:** the counter does **not** fix the
underlying duty-cycled-sensor problem Yang documents, and there is a known
"off by a factor" community report on the counter — so an **error band is still
required**, and per-SKU reset/availability must be probed.

### Implications (this is the sharpest one for W1)
`[speculative]` Energy **binds W1 admissibility** (parent §1.4), yet our energy
numbers are **boundary-limited and architecture-dependently biased**:
- **Report the boundary as a field** (RAPL = pkg+DRAM; NVML = GPU board; neither =
  system). Never sum component counters and call it "system energy" — on free
  cloud, **system energy is UNMEASURED** and should be labelled so.
- **Prefer whole-run counter integration** (NVML energy-counter delta; RAPL with
  wrap-safe <60 s polling), per MLPerf discipline and ML.ENERGY.
- **Probe each rig SKU** for counter availability + well-defined reset **before
  pinning** the rig; attach a **Yang-scale error band** (assume order-of the
  reported 25%-sampling error unless externally validated).
- Because our present CPU box has **no RAPL**, either (i) select a rig host that
  exposes RAPL/IPMI, or (ii) declare CPU energy **unmeasured** on that host and
  fall back to the neural-FLOP diagnostic + CPU-seconds + bytes-read as the
  honest proxies (never as a binding energy claim).

---

## (a) Concrete measurement-rig recommendations for P3-D-HW / P3-D-INDEX

All band numbers below are **[STIPULATED]** starting points for the coordinator/
Fable to ratify at the P3-D-HW freeze — chosen to be defensible given the sources,
not derived from a power calc on our specific hardware.

**R1 — Host pinning (P3-D-HW).** Fixed instance type + content-hashed base image
(this is also KOT-SIZE/2's frozen base image); CPU governor = `performance`,
turbo/boost disabled or frequency pinned; `taskset`/`numactl` affinity pinned;
background quiesced. Per Mytkowicz, **either fix the entire env block or
deliberately randomize it across runs** (and say which) — do not leave env size /
link order uncontrolled.

**R2 — Scenario harness (KOT-COST/2).** Closed-loop single-query harness for
**p50/p95 service-time latency**; a **true open-loop Poisson generator** for
**throughput-under-latency-bound** (records intended-vs-actual send time so
coordinated omission is detectable and reportable); **TTFT + inter-token latency
reported separately** for generative arms. Forbid cross-query caching exactly as
MLPerf does; disclose warm/cold cache state on every number.

**R3 — Duration.** ≥600 s per measured condition where feasible; for energy,
**loop short workloads to ≥60 s** and integrate power/energy over the whole window
(no spot reads). Early-stopping only *after* the minimum duration.

**R4 — Warm/cold protocol.** Cold = fresh process + dropped page cache + non-resident
model/index; capture load time and bytes-to-first-answer here. Warm = post-W
warmup. **Attribute load cost to cold; amortize in KOT-LIFE/1 across
10³/10⁶/10⁹ queries.**

**R5 — Statistics.** Report **median + distribution-free (rank-based) 95% CI**;
choose N so CI half-width ≤ 5% of median (Traeger); arithmetic mean for latencies,
harmonic for throughput (Hoefler R3); **never average ratios** (R4); percentiles
for tails (R8); document every varying factor (R9).

**R6 — Repeatability band [STIPULATED]** (P3-D-HW admissibility gate, calibrated
on the P3-E-CAL workload, to be tightened once real variance is observed):
- within-day CoV ≤ **5%** for latency-percentile metrics; ≤ **10%** for energy
  (counter noise) and for throughput on the 2-core box;
- day-to-day **median drift ≤ 5%** on the pinned calibration workload, over
  **≥ 3 measurement days** for any headline W1 number;
- **admissibility rule:** if the day-to-day band on a metric **exceeds δ_k** for
  that rung, the instrument cannot resolve the effect → **that metric cannot carry
  a W1 claim at that rung** (it is reported with the band and flagged).

**R7 — Energy reporting (KOT-COST/2 (d)).** Per-boundary, whole-run integration,
wrap-safe; per-SKU counter probe before pinning; explicit **measurement-boundary
field** + **error band**; "system energy" labelled **UNMEASURED** where only
component counters exist. Co-report the **neural-FLOP diagnostic + CPU-seconds +
bytes-read** so offloaded work is visible in *some* measured column.

**R8 — Size counting (KOT-SIZE/2, for P3-D-INDEX).** Figure-(1) canonical packed
bytes primary; count everything beyond the frozen base image; **report warm
resident RAM/VRAM (figure-3)** so an on-disk-small / RAM-huge arm is visible;
**remote bytes count** (figure-6). Index/store construction size + cost
(figure-5) → KOT-LIFE/1.

**R9 — KOT-LIFE/1 ledger fields (P3-D-LIFE).** Donor pretraining compute
(inherited, stated, never netted out) + fine-tune/HP-search compute (hours + \$,
the tuning-symmetry audit trail) + store authoring/parse/embed/index/human-review
(hours + \$) + **amortized TCO at 10³/10⁶/10⁹ queries** from measured
energy+latency + a **measurement-boundary & energy-error-band disclosure field** +
a **Sardana-framing note** (optimal size vs demand as context, not license) +
**remote-store egress/request cost** line.

## (b) Open questions
1. **Can we get any full-system wall-power on any rig** (a host with IPMI/RedFish,
   or a metered outlet)? If not, energy is boundary-limited *everywhere* — decide
   at P3-D-HW whether energy stays a **binding** W1 component or is demoted to
   **reported-with-band** (a live W1-admissibility design choice, since parent
   §1.4 currently makes energy bind).
2. **Exact MLPerf LLM binding percentile** per benchmark (I saw ~99% on master;
   confirm at freeze).
3. **Which free-GPU SKU**, and does it support `nvmlDeviceGetTotalEnergyConsumption`
   with well-defined reset **inside a container** (Modal etc.)? Needs a probe.
4. **Reconcile the Sardana \$-figures** (58% vs 17%) from the PDF tables before any
   KOT-LIFE amortization cites a specific number.
5. **The frozen base image contents** — does it, or a chosen rig host, resolve the
   RAPL-absence problem (CPU energy uncountable on the present box)?
6. **δ_k vs the repeatability band** — the band numbers in R6 are stipulated; they
   must be re-derived from P3-E-CAL's observed variance and checked against each
   rung's δ_k.

## (c) The honest risk — how our cost/size measurement could be gamed or be non-reproducible
`[speculative]` **The single sharpest risk is the energy measurement boundary.**
RAPL sees only CPU-package+DRAM (and nothing on our current box), NVML sees only
the GPU board, and even where a counter exists the underlying sensor is
duty-cycled (~25% on A100/H100, up to 65% correctable error). **An arm that shifts
work into an unmeasured domain — CPU/disk/NIC energy, a remote index, decompression
on a host with no RAPL — can look energy-cheap purely because its consumption
falls where the counters do not look.** The counter boundary *is* the gaming
surface, and it directly threatens a W1 energy-admissibility claim. The only
principled counter (full-system wall power, the MLPerf tenet) is exactly what we
cannot instrument on free cloud. **Honest mitigation, not a fix:** (i) report the
boundary explicitly and label system energy UNMEASURED where it is; (ii) co-report
bytes-read + CPU-seconds + neural-FLOP diagnostic so an offload shows up in *some*
measured column even when it hides from joules; (iii) treat any energy advantage
that lives entirely in an unmeasured domain as **UNPROVEN, not won**.
Secondary risks: **repeatability** — on a 2-shared-core noisy-neighbour box,
Mytkowicz-scale (~20%) measurement bias and day-to-day drift can exceed δ_k, so an
unenforced repeatability band would let measurement noise masquerade as a win
(→ R6 gate); **size** — the frozen-base-image and canonical-packer rules close the
main channels, but a generous base image and warm-RAM-vs-disk asymmetry remain
residual surfaces (→ R8 figure-3).

---

## Citation-verification table
| # | Source (short) | URL | What it anchors | Status (2026-07-19) |
|---|---|---|---|---|
| 1 | MLPerf Inference rules (`inference_rules.adoc`) | github.com/mlcommons/inference_policies (master) | 4 scenarios, 600 s, early-stop, caching, LLM TTFT/TPOT | **VERIFIED AT SOURCE this session** (master; pin a commit at P3-D-HW) |
| 2 | MLPerf Power (Tschand et al. 2410.12032v2) | arxiv.org/html/2410.12032v2 | full-system power, PTDaemon/Yokogawa, ≥60 s+loop, samples/joule, boundary excl. cooling/storage, TDP pitfall | **VERIFIED AT SOURCE this session** |
| 3 | Sardana et al. "Beyond Chinchilla-Optimal" (2401.00448) | arxiv.org/abs/2401.00448 + /html/…v2 | inference-aware optimal sizing; FLOP-vs-\$; limitations | **VERIFIED AT SOURCE this session** — qualitative + limits solid; **\$-figures [claimed], numeric discrepancy vs 07-11 flagged (Q6)** |
| 4 | wrk2 / Coordinated Omission (Tene) | github.com/giltene/wrk2 README | closed-loop CO, 1.4 s→200× p99, open-loop fix | **VERIFIED AT SOURCE this session** |
| 5 | Yang et al. "Part-time Power Measurements" (2312.02741) | arxiv.org/abs/2312.02741 | ~25% sampling A100/H100; 35%/65% error | **VERIFIED AT SOURCE this session** |
| 6 | Weaver RAPL reference page | web.eece.maine.edu/~vweaver/projects/rapl/ | domains, ~15.3 µJ, ~60 s wrap, 5.10/5.13 perms, per-socket | **VERIFIED AT SOURCE this session** |
| 7 | NVML `nvmlDeviceGetTotalEnergyConsumption` | docs.nvidia.com NVML ref + go-nvml/pynvml mirrors | mJ since driver reload; Volta+; NOT_SUPPORTED | **VERIFIED (semantics) this session** via NVIDIA docs + bindings; NVIDIA docs page + raw nvml.h truncated in-fetcher |
| 8 | ML.ENERGY GPU-energy best practices | ml.energy/blog/…/measuring-gpu-energy-best-practices/ | prefer energy counter over polling | **VERIFIED AT SOURCE this session** (does not cover per-process/idle attribution) |
| 9 | Mytkowicz et al. ASPLOS 2009 | users.cs.northwestern.edu/~robby/…/mytkowicz-wrong-data.pdf | env/link-order ~20% bias; randomize+causal | **VERIFIED AT SOURCE this session** |
| 10 | Hoefler & Belli SC15 (twelve rules) | htor.inf.ethz.ch/…/hoefler-scientific-benchmarking.pdf | R3/R4/R5/R6/R7/R8/R9 | **R3/R4 corroborated via search this session**; full PDF **[UNVERIFIED]** in-fetcher (binary); rule set `[prior-verified: 2026-07-11]` |
| 11 | Traeger et al. ToS 2008 (FS benchmarking) | fsl.cs.stonybrook.edu/docs/fsbench/fsbench.pdf | clear caches per cold run; N from stddev/CI | `[prior-verified: 2026-07-11]`, not re-fetched this session |
| 12 | Appuswamy et al. "Five-minute rule 30y" | adms-conf.org/2017/…/5minute-rule.pdf | break-even residency; scope excludes cloud billing | **PDF did not parse this session — [UNVERIFIED] at source 2026-07-19**; `[prior-verified: 2026-07-11]` |
| 13 | DistServe OSDI 2024 (2401.09670) | arxiv.org/abs/2401.09670 | TTFT vs TPOT separate SLOs | `[prior-verified: 2026-07-11]`, not re-fetched |
| 14 | SmolLM2 (2502.02737) + 135M card | arxiv.org/abs/2502.02737 | ~11 T tokens / ~14,800 t·param⁻¹ beyond Sardana range | `[prior-verified: 2026-07-11]`, not re-fetched |
| 15 | Local box no-RAPL | file:///sys/class/powercap | CPU energy uncountable on present host | `[MEASURED][prior-verified: 2026-07-11]` |

*Fetcher caveat:* three primary PDFs (Hoefler, five-minute-rule) and two large
raw headers/HTML (NVIDIA docs page, raw `nvml.h`) returned binary/truncated
content to the summarizing fetcher; where a claim depended on one, I either
corroborated it by an independent search this session or explicitly carried the
07-11 primary-source verification and marked it. No load-bearing MLPerf, Sardana,
RAPL, NVML-semantics, coordinated-omission, or Mytkowicz claim rests on an
unverified fetch.
