# P3-LR-SYS — Lifecycle cost, systems benchmarking, storage/I-O economics: decision-oriented literature review

> **Status: Phase-0 [LIT] deliverable of Programme-3 (bead kernel-of-truth-s55r.3).
> Nothing here is frozen, registered, or scheduled; no registry record, KB shard,
> or assumption entry is touched.** Author: Fable (chief-architect role),
> 2026-07-11.
> Parent: `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2,
> commit 1070c4c0) §1.3/§1.3a/§5, P3-LR-SYS row; the GPT-5.6 referee review is
> what put MLPerf + Sardana into the design as REVIEW-CITED-pending-verification.
> Spawns (recommendations only — the coordinator creates beads): **P3-D-HW,
> P3-D-LIFE, P3-D-INDEX (cost-rig co-input)** (§11).
> **Revised 2026-07-11 (same session)** per the independent GPT-5.6 maintainer
> review (`poc/gpt56-review/rev-SYS-20260711b`): MLPerf loop-semantics and
> early-stopping/duration corrected at the rules doc; Traeger run-count
> guidance corrected at the primary PDF; NVML energy-counter semantics and the
> Samsi venue upgraded to verified at source; storage-rent arithmetic,
> five-minute-rule scope, RAPL pool-scope, and the SmolLM2/Sardana
> characterisations corrected; a W1 energy-admissibility default is now
> proposed explicitly (§2). Living sources are commit-pinned in the ledger.
>
> **Tag convention** (the house discipline mapped onto a lit-review):
> `[LIT-BACKED: source, year]` = external empirical fact verified AT SOURCE this
> session (WebFetch/WebSearch on 2026-07-11; URL in §12 / SYS.sources.jsonl);
> `[MEASURED: ...]` = a programme verdict restated inside its own envelope, or a
> direct observation of this project's own hardware made this session;
> `[STIPULATED]` = a judgement or recommendation I make here; `[EXTRAPOLATION]`
> = a forward projection or arithmetic composition, never a premise. Anything
> not verifiable at source is marked **UNVERIFIED** inline, never silently
> carried.

---

## 0. Dedup: what already exists in-repo, and what this review adds

Surveyed before anything was added (the DEDUP-FIRST instruction):

- `kb/records/` (639 records, kot-lit-1 schema) — **architecture/mechanism
  records only** (seams, steering, constrained decoding, VSA). A grep for
  MLPerf/RAPL/NVML/energy/latency across the shard returns only incidental hits
  (energy-based models, HRR "energy"); there is NO systems-benchmarking,
  power-measurement, or lifecycle-economics record. Nothing below duplicates a
  KB record, and per governance nothing here is ingested — the staging file
  `docs/next/lit/SYS.sources.jsonl` is for the coordinator's central ingest.
- `docs/next/lit/{EVAL,RAG,PARSE}.md` (sibling Phase-0 deliverables) — EVAL
  covers index statistics and benchmark floors; it does not touch cost, power,
  or I/O. No overlap beyond the shared tag convention, which this review
  adopts.
- `docs/research-plan/06-resources.md` — already carries the in-house cost
  discipline this review must stay compatible with: latency/$ figures quoted in
  verdicts come from **pinned rigs** (line 86), per-RunSpec `worst_case_usd`
  refused above headroom, hourly cost-monitor, and the amortised
  `authoring_cost` line (~$0.10–0.50/concept planning figure). Inherited, not
  restated.
- Programme measured anchors this review calibrates against, each inside its
  own envelope: the deterministic engine answers covered queries at 5.29–7.82
  µs/query [MEASURED: registry/verdicts/l3a.json + a5.json engine timing]; the
  f2b system-level cost ratio vs the 1.7B host is 0.103 [MEASURED:
  registry/verdicts/f2b-replicate.json cost_ratio_vs_R3]; KOTK/2 columnar bytes
  beat compressed gloss text 6.7369× on one corpus, latency half UNDECIDED
  [MEASURED: registry/verdicts/f1.json].
- Local-hardware facts established THIS SESSION (they gate everything in §2–§4)
  [MEASURED: direct inspection of this box, 2026-07-11]: the dev box is a
  2-vCPU Intel Xeon Platinum 8259CL (virtualized EC2), 7 GiB RAM, ~50 GB NVMe
  EBS, **no GPU**, and **`/sys/class/powercap` does not exist** — RAPL is not
  exposed at all on this instance. Any energy protocol that assumes local RAPL
  is dead on arrival; CPU-side energy on this box is UNMEASURABLE by counter.

What is NEW here: MLPerf inference scenario/percentile/duration machinery in
operational detail; MLPerf Power's measurement boundary and why our counters
can never be "MLPerf-compliant"; RAPL and NVML pitfalls with magnitudes;
coordinated omission; goodput/TTFT/TPOT practice; warm/cold + startup
accounting practice; a repeatability protocol grounded in Hoefler–Belli,
Mytkowicz, and Traeger; storage/network price points for our actual compute
pool; and the at-source verification of Sardana et al. that §1.3a cited on
credit.

---

## 1. MLPerf Inference: the scenario + statistics machinery, operationalised

**What the standard actually is.** MLPerf Inference (Reddi et al., ISCA 2020)
prescribes rules "to ensure comparability across systems with wildly differing
architectures"; the first round produced 600+ reproducible measurements from 14
organizations [LIT-BACKED: arXiv:1911.02549, ISCA 2020]. The operational
content lives in the living rules document, verified directly [LIT-BACKED:
mlcommons/inference_policies inference_rules.adoc, fetched 2026-07-11]:

- **Four scenarios**, each a different load shape with a different metric —
  and, crucially, different query-issue semantics: *SingleStream* and
  *MultiStream* are **closed-loop** ("LoadGen sends next query as soon as SUT
  completes the previous query"; metrics = 90th- resp. 99th-percentile
  early-stopping latency estimate), *Server* is **open-loop** (LoadGen issues
  queries on a scheduled Poisson arrival process; metric = maximum Poisson
  throughput parameter sustainable under the latency bound), and *Offline*
  sends all samples at once (metric = throughput). Minimum run duration
  **600 seconds** in every scenario. So MLPerf itself uses closed-loop drivers
  where the claim is isolated per-query service time and an open-loop driver
  where the claim is latency under offered load — a distinction §5 builds on.
- **Query-count statistics are explicit, not vibes — but they are guidance,
  and duration always binds**: the rules' worked example computes that
  estimating a 90th percentile at 99% confidence with a 0.5% margin takes
  **23,886 inferences**, and the minimum-query table built on such numbers is
  offered as "a suggested starting point for how to set the minimum number of
  queries" — NOT a universal required sample size. The early-stopping
  criterion then allows runs with fewer processed queries to remain valid at
  the penalty of a slightly higher effective percentile, and it applies only
  ONCE THE MINIMUM RUN DURATION IS MET (its algorithm's step 1 begins "When
  the minimum run duration is met…") — early stopping relaxes query counts,
  never the 600-s duration [LIT-BACKED: inference_rules.adoc, scenarios table
  + early-stopping appendix]. Higher percentiles need correspondingly more
  queries — this is the reason programme-3 pinned p50/p95 rather than p99 for
  per-query latency (§1.3(f)), and it is the right call at our suite sizes
  [STIPULATED, arithmetic from the rules' own confidence machinery].
- **LLM serving constraints are TTFT/TPOT pairs per benchmark**, e.g.
  Llama3.1-8B summarization: TTFT 2000 ms / TPOT 100 ms (conversational) and
  500 ms / 30 ms (interactive); Llama2-70B: 2000/200 and 450/40; Mixtral-8x7B
  2000/200 [LIT-BACKED: inference_rules.adoc]. The percentile at which the LLM
  TTFT/TPOT constraints bind was not shown in the fetched excerpt —
  **UNVERIFIED** (commonly stated as 99th; do not repeat without checking the
  per-benchmark table at freeze time).
- **Caching rules** (directly relevant to our warm/cold accounting): caching
  queries, responses, or "values derived from activations" is prohibited; KV
  cache is allowed only when reused within the batch of queries; the trace may
  be pinned [LIT-BACKED: inference_rules.adoc]. MLPerf measures a warmed
  steady state — there is **no cold-start scenario in MLPerf at all**; our
  KOT-COST/2 clause (h) (warm AND cold both measured) is beyond-MLPerf and has
  to be designed by P3-D-HW, not copied (§6).
- **Scale gap, stated plainly**: the smallest LLM workload in the current
  suite is Llama3.1-8B (edge, summarization) [LIT-BACKED:
  inference_rules.adoc]; there is no MLPerf artifact at 100M–2B. What
  transfers to Programme-3 is the *machinery* — scenario definitions,
  percentile-with-confidence early stopping, minimum durations, seeded LoadGen
  trace generation, caching prohibitions — not any workload [STIPULATED].

DECISION for P3-D-HW [STIPULATED]: adopt (a) the SingleStream and Offline
scenarios as our two mandatory load shapes — SingleStream's closed-loop driver
yields isolated per-query **service-time** percentiles and every such figure
is labelled as such; Offline yields batch throughput — with a Server/Poisson
open-loop scenario MANDATORY for any latency-under-offered-load claim and
otherwise optional per rung under the pinned concurrency distribution already
required by KOT-COST/2(g); (b) the 600-second minimum-duration rule
unconditionally, with the early-stopping machinery used only to size/trim
query counts above that duration (never as a substitute for it); (c) a
query-count-per-percentile table computed from the same confidence machinery
at our n; (d) MLPerf's caching prohibitions as the default legality rule for
comparator arms (a comparator may not memoise the test trace — this closes a
gaming channel the threat model P3-D-THREAT should name).

## 2. MLPerf Power: what the methodology is, and what we can honestly claim

The power methodology was verified at the paper [LIT-BACKED: arXiv:2410.12032,
"MLPerf Power" (Tschand et al.), v2 2025]:

- **Full-system wall power is the tenet**: "a fundamental tenet of MLPerf
  Power is the emphasis on measuring full system power consumption" — via
  SPEC-certified external analyzers (e.g. Yokogawa WT310) driven through the
  PTDaemon, with a **range-fixing calibration run** before measurement runs, a
  minimum of **60 seconds of power samples**, energy computed by integrating
  power over the run window, and efficiency reported as Samples/Joule.
  Datacenter measurements include compute nodes + interconnect fabric; cooling
  and storage nodes are explicitly not yet covered. 1,841 reproducible
  measurements across 60 systems, µW→MW.
- The paper also kills two folk practices we must not reintroduce: TDP as a
  power proxy ("TDP only represents the thermal design limit, not the actual
  power usage") and cloud-granularity measurements that sweep in idle or
  unrelated nodes [LIT-BACKED: arXiv:2410.12032].

**The honest consequence for us** [STIPULATED, load-bearing]: we have no wall
meter and no PTDaemon on any pool platform surveyed so far — the local EC2 VM
and Modal containers are virtualized/containerized, and whether ARC offers a
bare-metal node with any power-measurement path is exactly the open survey
item §11 hands P3-D-HW (it is not settled either way here). **On the pool as
currently known, no Programme-3 energy figure can be labeled
MLPerf-Power-compliant.** What we CAN adopt is the
discipline around the number: fixed measurement boundary declared per figure,
calibration/ranging run, minimum measurement duration, whole-run integration
(already required by KOT-COST/2(d)), and Samples/Joule-style normalisation.
Our energy figures are **counter-based component estimates** (GPU via NVML
energy counters; CPU energy unavailable on the measured local box and
presumptively on other virtualized hosts pending the per-host survey, §3) and
must be
reported with that label, fail-closed: where no counter exists, the energy
cell of the resource vector is reported MISSING, never modeled from TDP or
utilisation [STIPULATED — this is the §1.3 no-silent-fallback convention
applied to the rig].

**Proposed W1 admissibility rule for energy (the review's blocking question,
answered)** [STIPULATED — proposed in-doc for the coordinator to carry into
`registry/assumptions.jsonl`; nothing is registered by this deliverable]: a
MISSING cell is honest reporting but does not by itself define how arms with
different or absent energy measurements participate in the binding W1
resource frontier. GPU-only NVML counters, CPU RAPL, and full-system wall
power are DIFFERENT measurement boundaries and are never directly comparable.
Therefore: (i) an energy **comparison** between arms is admissible only when
every compared arm carries a measurement at the SAME declared boundary, from
the same instrument class, on the same rig/session; (ii) no cross-boundary
conversion (e.g. GPU-counter → full-system) may be used unless a validated
conversion model with quantified error is itself pre-registered — none exists
today; (iii) consequently the energy component of the §1.3 resource vector is
**non-binding by default in W1**: it is always reported per arm with its
boundary label (or MISSING), and it becomes a binding frontier dimension only
on rigs where (i) holds for ALL compared arms. A MISSING or
boundary-mismatched cell excludes the energy dimension from that comparison
(disclosed in the verdict); it does not disqualify the arm. P3-D-HW inherits
this as its default and may strengthen it (e.g. by finding a same-boundary
path on ARC), never weaken it silently.

## 3. RAPL: pitfalls, and the measured fact that we don't have it

- **Accuracy when it exists**: the standard reference (Khan et al., "RAPL in
  Action", ACM TOMPECS 2018) finds RAPL readings highly correlated with plug
  power with negligible read overhead; accuracy improved generationally —
  Sandy Bridge-EP shows systematic errors while Haswell-EP correlates
  near-perfectly with external measurement (reported MAPE ~4.0% vs ~3.1%
  without the DRAM domain) [LIT-BACKED: TOMPECS 3(2) 2018, abstract + Aalto
  research-portal record; the MAPE split is carried from the portal summary,
  not re-derived from the paper body].
- **Operational pitfalls** [LIT-BACKED: Khan et al. 2018; V. Weaver's RAPL
  reference page]: (i) non-atomic register updates with unpredictable update
  timing — RAPL gives no timestamps, so short-interval deltas alias; (ii)
  32-bit energy counters that **wrap in ~60 s** at high power (energy unit
  ~15.3 µJ) — samplers must poll well inside the wrap period; (iii) socket
  granularity only — no per-process attribution; (iv) access regressions:
  unprivileged powercap sysfs reads were restricted in Linux 5.10 for security
  reasons, and the AMD RAPL-without-permission-checks driver was removed in
  5.13 — a root/perf-paranoid requirement is the practical default now.
- **The binding local fact, scoped precisely**: on this project's dev box
  `/sys/class/powercap` does not exist — the hypervisor does not expose RAPL
  at all [MEASURED: this box, 2026-07-11]. That measurement establishes THIS
  host only. Consequence: **CPU-side energy is unmeasurable by counter on the
  local box** [MEASURED]; for Modal and other cloud containers, absence is
  the expected default for unprivileged virtualized guests but is
  **UNVERIFIED until the P3-D-HW per-host survey probes each pool platform**
  — the survey, not this box, settles the pool-wide scope. KOT-COST/2(d)'s
  "RAPL on CPU" clause is conditional — it binds only if that survey finds a
  pool host that actually exposes it (an ARC bare-metal node, if one exists,
  is the only plausible candidate) [STIPULATED; P3-D-HW opening question].

## 4. NVML / nvidia-smi: the GPU counter is usable, but only integrated

- **The sampling hole, with magnitude**: Yang, Adámek & Armour ("Part-time
  Power Measurements: nvidia-smi's Lack of Attention", arXiv:2312.02741;
  70+ GPUs across every generation since Fermi) show that on **A100 and H100,
  only ~25% of runtime is sampled** for power — "during the other 75% of the
  time, the GPU can be using drastically different power" — and that applying
  their corrections against external meters reduces energy error by **35% on
  average and up to 65%** [LIT-BACKED: arXiv:2312.02741, 2024].
- Programme-3's KOT-COST/2(d) wording ("whole-run integration — not
  query-level spot reads") is therefore VERIFIED as the correct practice, not
  just caution [STIPULATED, resting on the LIT-BACKED line above]. Per-query
  energy at µs–ms scale is unmeasurable on NVML; energy must be measured over
  the whole 600-s-class run and divided by completed queries.
- **Prefer the cumulative energy counter over power polling**:
  `nvmlDeviceGetTotalEnergyConsumption` "[r]etrieves total energy consumption
  for this GPU in millijoules (mJ) since the driver was last reloaded", "[f]or
  Volta™ or newer fully supported devices" [LIT-BACKED: NVIDIA NVML API —
  existence/signature at the docs.nvidia.com device-queries page; units,
  reset-on-driver-reload semantics and architecture floor verified at
  NVIDIA's canonical `nvml.h` docstring, NVIDIA/go-nvml `gen/nvml/nvml.h` @
  commit 8b8585bd]. The remaining open item is narrower: actual availability
  and driver-reload/container semantics on each Modal GPU SKU — P3-D-HW
  confirms on the real rig before pinning.
- Precedent for LLM-inference energy benchmarking at multi-GPU scale exists
  (Samsi et al., "From Words to Watts": LLaMA-class models on V100/A100,
  sharded up to 32 GPUs, Alpaca + GSM8K) [LIT-BACKED: arXiv:2310.03003, 2023;
  venue IEEE HPEC 2023 verified this session — conference program listing +
  DOI 10.1109/HPEC58863.2023.10363447]. Useful as a shape
  precedent; its per-token numbers are for 7B+ models and do not transfer to
  our rungs.

## 5. Latency percentiles, throughput, TTFT/inter-token: measurement practice

- **Coordinated omission is the classic failure** of closed-loop load
  generators: when the system stalls, a closed-loop client stops issuing,
  silently deleting exactly the samples that carry the tail. Tene's wrk2
  documents a worked example where a 1.4 s server stall yields an uncorrected
  "p99 = 6.04 ms" vs a corrected 1.27 s — a ~200× understatement — and the
  fix: generate load on a constant schedule and measure latency **from the
  intended send time**, not the actual send time [LIT-BACKED: giltene/wrk2
  README]. Within MLPerf, **only the Server scenario embodies this open-loop
  discipline** (scheduled Poisson arrivals); SingleStream and MultiStream are
  deliberately closed-loop (§1) — legitimately so, because their claim is
  isolated per-query service time with no offered-load backlog, not latency
  under load [LIT-BACKED: inference_rules.adoc]. Coordinated omission is a
  failure mode of closed-loop measurement PRESENTED AS latency-under-load; it
  does not invalidate closed-loop service-time measurement as such.
  DECISION [STIPULATED]: any latency-under-offered-load or
  throughput-conditioned percentile claim must come from an open-loop driver
  — pinned, seeded arrival schedule, latency timestamped from INTENDED issue;
  a closed-loop next-query-on-completion driver is prohibited for those
  claims. A closed-loop SingleStream-style driver remains valid for isolated
  service-time percentiles, and every such figure is labelled "service-time
  (closed-loop, unloaded)" so the two claim types can never be conflated.
- **TTFT/TPOT as separate SLOs, and goodput**: DistServe (OSDI 2024) defines
  the now-standard decomposition — TTFT for prefill, TPOT (time per output
  token) for decode — and **goodput** = the maximum per-GPU request rate at
  which BOTH SLOs are met (they report 7.4× more requests or 12.6× tighter
  SLOs vs colocated baselines at >90% SLO attainment) [LIT-BACKED:
  arXiv:2401.09670, OSDI 2024]. Mean throughput alone hides the trade
  (prefill and decode interfere). For Programme-3: generative arms report
  TTFT and inter-token latency separately per KOT-COST/2(i); if a serving-rate
  claim is ever made, it must be a goodput-style claim (rate under a stated
  percentile SLO), never a bare tokens/s [STIPULATED].
- Note the asymmetry of our systems: the deterministic engine has no
  token stream (its whole answer arrives in µs), while comparator LLMs do.
  TTFT-vs-TPOT decomposition therefore mostly disciplines the *comparators*;
  for engine-bearing arms the end-to-end p50/p95 latency (KOT-COST/2(f)) is
  the binding figure, with parse/retrieval/engine/generation stage timing as
  diagnostics [STIPULATED].

## 6. Warm vs cold cache, startup, and index-load accounting

- The storage-benchmarking literature made cache-state disclosure a formal
  requirement long ago: Traeger et al.'s nine-year survey of **106 papers**
  (ACM Transactions on Storage, 2008) found chronic non-disclosure and set the
  guidelines — state whether caches are warm or cold; for cold-cache results
  actually clear the caches before EACH run (remount / purge / allocate-and-
  free memory); run "each test … several times to ensure accuracy", with the
  appropriate NUMBER of runs "determined" from "standard deviations or
  confidence levels" (they recommend 95% CIs with half-width below 5% of the
  mean, Student's t below 30 runs) — **no fixed run count is prescribed**;
  report the full system state. "At least ten times" was the AUTHORS' OWN
  Auto-pilot configuration for their example evaluation, not a guideline; and
  the survey found the majority of benchmarks did not even specify a run
  count, with per-conference MEDIAN run counts of 1–3 (SOSP 1, FAST 1, OSDI
  2, USENIX 3) [LIT-BACKED: ACM TOS 4(2) 2008, primary PDF re-read this
  session — §§3.3–3.4 (pp. 5:7–5:8), Fig. 1 + Table I (pp. 5:9–5:10),
  Auto-pilot config (p. 5:14); this corrects a misquote in the previous
  revision (a "≥10 runs" guideline and a "median 7 runs" statistic that was
  actually the median number of reported system parameters)].
- MLPerf, by contrast, standardises only the warmed steady state (§1) and
  prohibits response caching; **no public ML benchmark standardises cold-start
  + index-load accounting** — the closest formalisation is our own KOT-SIZE/2
  figure (4) (cold-start working set + total bytes read to first answer)
  [STIPULATED after search; carried as an absence-claim, i.e. no
  counter-example found this session, not a proven negative].
- DECISION for P3-D-HW [STIPULATED]: define three pinned states per arm —
  **COLD** (fresh container/process, page cache dropped
  (`echo 3 > drop_caches` where privileged, else fresh-VM/container),
  model+index load INCLUDED in the measured window; yields startup time and
  bytes-to-first-answer), **WARM** (steady state after a pinned warmup trace,
  MLPerf-style; yields the p50/p95/throughput figures), and **REPORT BOTH**,
  never a blend. The warmup trace and its length are pinned inputs; cold-run
  repetition count is CI-determined per Traeger's actual rule (repeat until
  the §7 rank-based CI half-width gate passes), with a stipulated minimum of
  10 — OUR configuration, echoing Traeger's own Auto-pilot practice rather
  than any literature-prescribed floor; cold-path variance is I/O-dominated,
  so expect the gate, not the minimum, to bind.
- Arithmetic floor worth pinning [EXTRAPOLATION, from verified baseline
  throughput]: an EBS gp3 volume's included baseline is 125 MB/s (§8), so
  every GB of model+index bytes costs ≥8 s of cold-start on baseline gp3
  before compute begins — cold-start economics are bytes economics, which is
  exactly why KOT-SIZE/2(4) and KOT-COST/2(h) must share one measurement.

## 7. Hardware repeatability: run-to-run and day-to-day variance control

- **The reporting canon** is Hoefler & Belli, "Scientific Benchmarking of
  Parallel Computing Systems" (SC15) — 12 rules, verified at the primary PDF
  this session. The ones that bind our rig [LIT-BACKED: SC15, 2015]:
  Rule 3/4 (arithmetic mean only for costs, harmonic for rates; avoid
  summarizing ratios — summarize costs/rates instead, geometric mean only as
  last resort); Rule 5 (report if measurements are deterministic; otherwise
  report confidence intervals); Rule 6 (do NOT assume normality without
  diagnostic checking); Rule 7 (compare nondeterministic data via
  non-overlapping CIs / ANOVA); Rule 8 (means/medians may be the wrong
  summary — worst-case-latency problems need percentiles); Rule 9 (document
  ALL varying factors and levels). For medians/percentiles they give the
  distribution-free rank-based CI (binomial ranks around n/2), which needs no
  normality assumption, and recommend CoV (s/x̄) as a consistency measure.
- **Measurement bias is real and large at our effect sizes**: Mytkowicz et
  al., "Producing Wrong Data Without Doing Anything Obviously Wrong!" (ASPLOS
  2009) showed UNIX environment size and link order alone shift measured
  performance by >10% (double-digit percent in cases), and prescribe
  randomizing the experimental setup across runs plus diverse workloads
  [LIT-BACKED: ASPLOS 2009, primary PDF]. Our W1 margins δ_k will plausibly be
  single-digit index points riding on cost measurements; a 10% systematic
  wobble in the cost denominator is disqualifying if uncontrolled
  [STIPULATED].
- **Cloud/day-to-day variance**: our pool is virtualized and shared (EC2 dev
  box with 2 shared cores; Modal serverless containers land on unknown hosts;
  ARC is a shared cluster). MLPerf Power's warning about cloud measurement
  granularity (§2) applies to timing too. DECISION for P3-D-HW [STIPULATED]:
  (a) same-host pairing — every S-vs-comparator cost comparison runs
  interleaved in the SAME session on the SAME container/node (A/B/A/B), never
  across days or hosts; (b) host fingerprint recorded per run (CPU model,
  GPU UUID, driver, clocks, container image hash) — the pinned-rig rule
  `06-resources.md:86` extended to identity; (c) per-session calibration
  probe: a fixed synthetic workload run at session start/end; sessions whose
  probe CoV exceeds a pinned gate (suggest 5% to start; calibrate in
  P3-E-CAL) are discarded fail-closed; (d) repetitions per cell driven by a
  pinned CI gate — rank-based nonparametric CIs per Hoefler Rule 6/8, run
  count increased until the half-width gate passes (Traeger's actual rule:
  the number of runs is determined from confidence levels) — with a
  stipulated minimum of 10 reps as our starting configuration, not a
  literature-backed floor; (e)
  environment pinned AND a randomized-dummy-env-var replicate per Mytkowicz to
  bound layout bias on CPU-side measurements.

## 8. Storage + network I/O economics

**Price points for OUR pool, verified 2026-07-11** (prices drift; these are
pins for Phase-1 modelling, to be refreshed at P3-D-LIFE freeze):

- **Modal** (the primary GPU home) [LIT-BACKED: modal.com/pricing]: H100
  $0.001097/s (≈$3.95/h); A100-80GB $0.000694/s (≈$2.50/h); A100-40GB
  $0.000583/s (≈$2.10/h); L40S ≈$1.95/h; A10 ≈$1.10/h; T4 ≈$0.59/h; L4
  ≈$0.80/h; CPU $0.0000131/core-s (≈$0.047/core-h); RAM $0.00000222/GiB-s
  (≈$0.008/GiB-h); Volumes $0.09/GiB-month with 1 TiB free; academic credits
  up to $10k (already in the §6 funding plan).
- **AWS (us-east-1)** [LIT-BACKED: aws.amazon.com pricing pages, partially
  extractable]: S3 GET $0.0004/1k requests, PUT $0.005/1k; first 100 GB/month
  of internet egress free account-wide; EBS gp3 $0.08/GB-month with 3,000 IOPS
  + 125 MB/s included, extra IOPS $0.005/IOPS-month, extra throughput
  $0.06/MBps-month (page labels these "regional example" rates); gp2
  $0.10/GB-month. S3 Standard per-GB storage price was NOT extractable from
  the JS pricing table this session — **UNVERIFIED** (commonly $0.023/GB-month
  first 50 TB; re-verify at P3-D-LIFE freeze).
- **What the prices say about our stores** [EXTRAPOLATION, arithmetic]: every
  store this programme has built is MB-scale (the entire kernel + indexes fit
  in tens of MB); at $0.08–0.09/GiB-month that is ~$0.001–0.01/month of
  storage *rent* — roughly **two to four orders of magnitude** below a single
  $1–4 GPU-hour (corrected from an earlier "five orders" overstatement) —
  and on Modal the marginal rent is plan-dependent and likely $0 outright,
  since 1 TiB/month of volume storage is included free. The conclusion
  (rent is negligible; bytes-in-motion are what cost) is unchanged; the
  magnitude now matches the arithmetic. The economically binding I/O
  quantities
  are (i) cold-start bytes (≥8 s/GB at gp3 baseline, §6), (ii) egress if a
  remote dependency exists (KOT-SIZE/2 figure (6) already forces remote bytes
  to count), and (iii) request costs only at 10⁹-query volumes (10⁹ S3 GETs =
  $400 — visible at exactly the largest KOT-LIFE/1 volume, hence worth a line
  in the amortisation table, not a design driver).
- **The memory-vs-storage residency question has a canonical economics tool**:
  the five-minute rule. Verified at the 30-year revisit (Appuswamy,
  Borovica-Gajic, Graefe, Ailamaki, ADMS@VLDB 2017, primary PDF): break-even
  residency interval = (pages/$ of RAM) ÷ (accesses/s/$ of storage device);
  2017 values — DRAM vs SATA SSD @4KB: ~7 min (down from 15 min in 2007);
  DRAM vs NVMe/3D-XPoint: ~40 s; DRAM vs HDD @4KB: the price ratio moved
  1,700→10,000 and the interval grew to hours (the literal five-minute rule
  survives only at 512KB HDD pages) [LIT-BACKED: adms-conf.org camera-ready,
  2017]. Consequence for us [STIPULATED — a hypothesis, not a settled
  conclusion]: on the 2017 break-even values, an index page accessed more
  than ~once/minute belongs in RAM, which for MB-scale stores SUGGESTS full
  RAM residency; but those break-evens are hardware- and price-generation-
  specific and do not account for cloud RAM billing (Modal meters RAM at
  ~$0.008/GiB-h), scale-to-zero container economics, capacity constraints,
  access skew, or opportunity cost. "Full RAM residency is economically
  optimal for our stores" is therefore a hypothesis KOT-LIFE/1 must evaluate
  under OUR pinned prices and access distributions. What survives
  unconditionally is the framing: the residency question is **who pays the
  warm RSS** — which KOT-COST/2(e) (peak accelerator memory AND host RSS)
  already charges to the arm — and the five-minute-rule machinery is the
  right tool for KOT-LIFE/1's RAM-rent-vs-storage-rent line.

## 9. Inference-volume-dependent sizing: Sardana et al., verified at source

The §1.3a REVIEW-CITED claim is now verified at source; its quantitative
results are stronger than the design assumed, and its stated limits (carried
below, not smoothed over) matter just as much [LIT-BACKED: arXiv:2401.00448,
ICML 2024, "Beyond Chinchilla-Optimal:
Accounting for Inference in Language Model Scaling Laws" (Sardana, Portes,
Doubov, Frankle), incl. v2 HTML full text]:

- **Method**: modify Chinchilla to minimise training+inference compute (and
  separately, real cost) for a target quality and lifetime inference demand.
- **Key worked numbers**: a 30B-Chinchilla-quality model with 10¹³ lifetime
  inference tokens is FLOP-optimally replaced by a **13.6B model trained on
  2.84× more data (−28% total FLOPs)**; in the real-cost analysis (1.5B
  requests), a **16B model on 3.35T tokens saves ~17% of $**. A 13B-quality
  model with 2T inference tokens → a 7B on more data, −17% FLOPs.
- **FLOPs ≠ dollars, quantified**: for Chinchilla-70B at 2T inference tokens,
  the compute-optimal-vs-cost-optimal gap is 1.3% in FLOPs but **36% in
  cost**, because inference runs at ~50× lower utilization than training
  (their accounting: ~1% MFU on output tokens vs ~50% MFU training). This is
  the single sharpest published warrant for programme-3's demotion of the
  neural-FLOP ledger to a non-binding diagnostic [STIPULATED reading; the
  numbers are LIT-BACKED].
- **Empirical leg**: 47 models, 150M–6B, trained at 10–10,000 tokens/param;
  loss does not plateau even at 10,000 tokens/param for the 150M model, and
  Chinchilla-fit-on-typical-ratios overestimates the value of extra tokens at
  extreme ratios (they refit α/β).
- **Sardana's own stated limits** (they bound how much §9 may claim): the
  real-cost analysis is a deliberately **simplified** dollar model (fixed
  utilisation assumptions; no maintenance/refresh, demand uncertainty, or
  financing structure), and the extreme-ratio scaling fits misbehave enough
  that the authors refit them; separately, the paper's quality axis is
  pretraining LOSS — transfer to a capability index like KOT-AI-INDEX is an
  assumption OUR design must carry explicitly, not a property of the paper
  [LIT-BACKED: arXiv:2401.00448 for the paper's own caveats; the
  transfer caveat STIPULATED]. Sardana licenses the qualitative proposition
  that expected inference demand changes optimal training size, plus its own
  worked numbers under its own assumptions — nothing stronger.
- **Practice at exactly our anchor scale**: SmolLM2-1.7B is explicitly
  "overtrain[ed] ... on ~11 trillion tokens" [LIT-BACKED: arXiv:2502.02737,
  2025], and SmolLM2-135M on 2T tokens [LIT-BACKED: HF model card,
  Apache-2.0]. That is ~6,500 and ~14,800 tokens/param — the 135M anchor sits
  BEYOND Sardana's swept range [EXTRAPOLATION, arithmetic]. Precision about
  what this establishes: overtraining is the DIRECTION Sardana prescribes
  under high lifetime inference demand, but "overtrained" is not
  "inference-optimal" — no specified target quality, workload, hardware,
  lifetime demand, or cost model makes SmolLM2 a solution to Sardana's
  optimisation, and HOW MUCH of the available train-longer-deploy-smaller
  gain these artifacts bank is unquantified. The claim this review needs is
  weaker and holds: our baseline frontier is built from inference-lean,
  deliberately overtrained artifacts rather than compute-optimal ones, so W1
  margins cannot be manufactured by comparing against compute-optimal
  strawmen [STIPULATED, load-bearing for P3-D-BASE/P3-D-LIFE].
- **Accounting consequence for KOT-LIFE/1** [STIPULATED]: the ledger's three
  pinned volumes (10³/10⁶/10⁹ queries) should be joined by Sardana-style
  crossover statements per claim — computed **per priced dimension, never on
  the vector**: a resource VECTOR has no crossover point unless its
  components are priced or constrained on a common scale, and this design
  deliberately refuses a universal exchange rate across human hours, GPU
  hours, latency, and energy (§1.3). So: report, separately for each
  dimension that has a defensible price (at minimum the $-denominated ones),
  the inference volume at which the measured per-query gap between S and
  each comparator repays any training/authoring cost difference — each line
  under stated billing-granularity/utilisation/horizon assumptions with
  sensitivity analysis (§11 P3-D-LIFE); dimensions without a price get no
  crossover claim, only their measured per-query gap. Dimension-drop arms
  inherit donor pretraining compute stated-not-netted (§1.3a); Sardana gives
  the principled reason this matters: the donor was already sized for
  someone's inference demand, not ours.

## 10. What beat matched baselines, under what accounting (the skeptical cut)

The bead's standing question, answered for the SYS scope [STIPULATED
synthesis; constituent figures LIT-BACKED / MEASURED as tagged]:

1. **Systems wins in this literature are accounting wins.** DistServe's 7.4×
   is a goodput win at fixed SLO and fixed hardware — same model, same
   accelerators, better scheduling; it never claims a FLOP reduction.
   Sardana's −17…−28% are compute-accounting results under an explicit
   inference-demand model — analytic + 47-model-empirical, no benchmark-arm
   comparison at all. Neither is a "smarter model" claim, and both would
   evaporate under the wrong ledger (mean throughput; FLOP-only cost). The
   Programme-3 analogue: our f2b cost_ratio 0.103 [MEASURED:
   f2b-replicate.json, formal inputs only] is credible precisely because it
   was measured on a pinned rig, and the §1.3 resource vector is what keeps
   any future such claim honest.
2. **Unmatched-compute smells specific to the SYS scope**: (i) energy from
   TDP or utilisation models (killed by MLPerf Power, §2); (ii)
   latency-under-load percentiles taken from closed-loop drivers
   (coordinated omission, §5 — understates
   comparator tails if OUR driver is open-loop and theirs closed, i.e. this
   pitfall can bias FOR us; symmetric drivers are mandatory); (iii)
   warm-vs-cold asymmetry — quoting S warm (engine resident) vs a comparator
   cold (model load included), closed by §6's both-states rule; (iv) storage
   rent quoted while cold-start bytes and egress are dropped (closed by
   KOT-SIZE/2 figures (4)/(6)); (v) comparing against compute-optimal rather
   than overtrained baselines (§9 — closed by using SmolLM2-class anchors).
3. **Nothing in the verified literature licenses a claim that any
   neurosymbolic/store-bearing system beats a matched neural baseline on the
   FULL resource vector** — the vector methodology itself (MLPerf + power +
   goodput + lifecycle) has simply not been applied to that comparison at
   100M–2B anywhere I could find this session [carried as an absence-claim
   after search, not a proven negative]. Programme-3's KOT-COST/2 + KOT-LIFE/1
   would be, to my knowledge, the first pre-registered instance at this scale
   — which is a reason to expect referee scrutiny of the rig, and to
   over-document it [EXTRAPOLATION].

## 11. Open questions for Phase-1, and the hand-off

**Settled by this review** (Phase-1 may consume without re-litigating):

- MLPerf scenario/percentile/duration/caching machinery verified and reduced
  to an adoptable subset, with the loop semantics stated correctly:
  SingleStream/MultiStream closed-loop, Server open-loop Poisson; 600-s
  duration unconditional, early stopping adjusts query counts only (§1); the
  LLM TTFT/TPOT constraint TABLE verified, its binding percentile UNVERIFIED
  (one item to close at P3-D-HW freeze).
- MLPerf-Power compliance is impossible on the pool as currently surveyed;
  counter-based estimates with declared boundaries + whole-run integration is
  the honest ceiling; and a W1 energy-admissibility default is PROPOSED —
  same-boundary-or-non-binding, no unvalidated boundary conversions (§2, for
  the coordinator/P3-D-HW to ratify).
- RAPL: absent on the dev box (measured); presumed-but-unverified absent on
  other virtualized hosts pending the per-host survey; pitfall list with
  magnitudes (§3). NVML: A100/H100 power-poll sampling hole verified at
  25%-of-runtime; whole-run integration/energy-counter practice verified as
  correct; `nvmlDeviceGetTotalEnergyConsumption` semantics verified at source
  (mJ since driver reload, Volta+) (§4).
- Coordinated omission + goodput discipline adopted; open-loop pinned-schedule
  driver mandatory for latency-under-offered-load claims, closed-loop
  service-time measurement retained and labelled (§5). Warm/cold/startup
  three-state protocol shaped (§6).
- A concrete repeatability protocol skeleton grounded in the literature's
  actual rules (CI-gated run counts with a stipulated ≥10 starting minimum,
  nonparametric CIs, no-normality, same-host A/B interleave, env
  randomization, calibration-probe gate) (§7).
- Sardana verified at source WITH its cost-vs-FLOP 36%-gap result AND its
  stated limits (simplified dollar model; extreme-ratio fit failures;
  loss-not-capability quality axis); SmolLM2 anchors confirmed as
  deliberately overtrained, inference-lean artifacts — NOT established as
  Sardana-optimal; the FLOP-diagnostic demotion is now
  literature-warranted, not just review-asserted (§9).
- Price pins for Modal/AWS captured; store rent shown negligible vs
  cold-start bytes + RSS rent; five-minute-rule framing adopted for
  KOT-LIFE/1 residency accounting (§8).

**Open questions each spawned design bead must answer:**

- **P3-D-HW** (hardware repeatability + warm/cold + startup/percentile
  protocol — the KOT-COST/2 rig's operating manual): (1) Ratify (or
  strengthen) the §2 energy-admissibility default — energy is non-binding in
  the W1 frontier unless every compared arm shares one declared measurement
  boundary on one rig; no unvalidated boundary conversion — and run the
  per-host energy survey it depends on: does ANY pool host expose RAPL or a
  wall-power path (ARC bare-metal?), or is GPU-counter-only the final scope?
  The survey also closes §3's open point that Modal-container RAPL absence is
  presumed, not measured. (2) Confirm `nvmlDeviceGetTotalEnergyConsumption`
  availability and driver-reload/container semantics on the actual Modal GPU
  SKUs (units and architecture floor are now verified at source, §4) and pin
  counter-vs-polling.
  (3) Set the calibration-probe workload, its CoV gate, and the
  discard-session rule; validate in P3-E-CAL. (4) Fix the query-count table
  per percentile at our suite sizes from the MLPerf confidence machinery; pin
  p50/p95 and BAN p99 below the supporting n. (5) Specify cache-drop
  mechanics per platform (drop_caches privilege on Modal? fresh-container
  semantics?) for the COLD state. (6) The Mytkowicz randomization set for
  CPU-side runs. (7) The pinned concurrency distribution for KOT-COST/2(g)
  and whether a Server/Poisson scenario is required before R-2.
- **P3-D-LIFE** (KOT-LIFE/1 amortisation model + logging hooks; co-blocked on
  P3-LR-STORE): (1) The ledger schema joining: donor pretraining (stated),
  tuning-compute audit trail, store authoring/parse/embed/index/review costs,
  measured per-query vector × {10³,10⁶,10⁹}, PLUS per-priced-dimension
  Sardana crossover lines (§9 — never a vector crossover). (2) Price-pin
  refresh discipline (prices verified here drift; pin at freeze with date +
  URL). (3) Whether energy enters the $ model at all given counter-only scope
  (recommend: report J, do not monetise — monetising component-estimate
  Joules launders precision). (4) Residency accounting: evaluate the §8
  full-RAM-residency HYPOTHESIS under our pinned prices (cloud RAM billing,
  scale-to-zero, access skew) and set the RSS-rent-vs-storage-rent line
  accordingly. (5) Egress/remote-dependency charging joint with
  KOT-SIZE/2(6). (6) The explicit assumption set every crossover line must
  state, with sensitivity analysis over each knob: billing granularity
  (per-second serverless vs reserved), utilisation/capacity assumptions,
  maintenance + hardware-refresh costs, workload mix and output-length
  distributions, and discount rate / time horizon — Sardana's own dollar
  model is stated-simplified (§9); ours must show its knobs rather than
  inherit that simplification silently.
- **P3-D-INDEX (cost-rig co-input)**: (1) The measurable-cell matrix — which
  of KOT-COST/2 (a)–(j) is measurable on which pool platform (local box: CPU-s
  /bytes/RSS/latency, NO energy; Modal: + accel time + NVML energy, NO wall
  power, NO CPU energy; ARC: survey pending) — so the calibration prereg
  (P3-E-CAL) declares MISSING cells fail-closed instead of discovering them.
  (2) The Samples/Joule-style normalisation and output-length control (j)
  interaction with the index's per-benchmark metrics. (3) Warm/cold as index
  co-variates: which figure the W1 admissibility check binds on (recommend:
  admissibility on BOTH, headline on warm, cold published — matches §1.4).

**What this review deliberately does NOT hand off**: no benchmark/index
content (P3-LR-EVAL owns it), no retrieval-index construction cost practice
(P3-LR-RAG/P3-LR-STORE own it), no store authoring economics (P3-LR-STORE).

## 12. Source count and verification ledger

20 external sources verified at their primary venue this session (the NVML
energy-counter semantics and the Samsi venue were upgraded from UNVERIFIED on
re-verification during the review-response pass; the Traeger entry was
corrected against the primary PDF), plus one direct local-hardware
measurement record; 5 items carried as UNVERIFIED inline (§1 LLM-constraint
percentile; §4 NVML availability/semantics on the actual Modal SKUs; §8 S3
Standard $/GB; and the two absence-claims §6/§10, which are
searches-without-counterexample, not verifications). Auditability discipline
adopted per review: living sources (MLPerf rules, wrk2 README, NVML header)
are pinned to commit hashes; partially-verified items are SPLIT into separate
ledger entries rather than hidden behind one boolean; entries carry
section/page locators where the source was read in the body rather than the
abstract. Full records: `docs/next/lit/SYS.sources.jsonl` (24 lines: 21
`verified:true` — 20 lit + 1 local measurement — and 3 `verified:false`).
