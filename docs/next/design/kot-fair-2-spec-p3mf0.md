# KOT-FAIR/2 measurement + fair-comparison framework — GPT-5.6 DRAFT (bead P3-MF-0)

> **STATUS: UNREVIEWED GPT-5.6 DRAFT — NOT FROZEN.** Produced 2026-07-19 (Programme-3 Phase-0, overflow-Fable
> lane, Fable capped). This CONCRETISES docs/next/programme-3-neurosymbolic-architecture.md §1-§2. All
> `[STIPULATED — coordinator/Fable to ratify]` values are PROPOSED, not fixed. NEXT: (1) coordinator review
> gate; (2) RECONCILE with the two framework-gating lit-reviews landed same day — reports/lit-p3-eval.md
> (HELM-2025 citation; composite-index-defensibility NULL → candidate W1 = scalar-LCB AND per-domain
> no-regression; OLLv2 floors ≤500M → R-0/R-1 low-floor benchmarks; proxy-rung kill-not-certify) and
> reports/lit-p3-sys.md (energy-boundary-as-first-class; repeatability-as-gate; Sardana $-figure divergence);
> (3) Fable adversarial critique; (4) freeze via P3-D-INDEX (also needs P3-D-THREAT). Do NOT treat as frozen.
> Source: poc/gpt56-review/p3mf0-kotfair-spec/.

---

# KOT-FAIR/2 — measurement and fair-comparison framework

> **Status:** `KOT-FAIR/2-rc0`, PROPOSAL for coordinator review and Fable critique. It is not frozen, preregistered, scheduled, or evidence. No Phase-2/G4/W1 work may freeze until every unresolved pin below is filled, P3-E-CAL is GREEN, and the resulting manifest is content-hashed.
>
> **Authority:** Programme-3 [§1.1–§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:222) and [§2.0–§2.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:445).
>
> `[SV]` means source/licence/release verification is required before freeze.  
> `[STIPULATED — coordinator/Fable to ratify]` marks a proposed value not already fixed by the authority.

## 0. Governing claim and threat model

The W1 claim remains verbatim in substance: at rung \(R_k\), S must fit every component of the preregistered budget

\[
B_k=(\text{max packed bytes},\text{max p95 latency},
\text{max energy/query},\text{max peak accelerator memory and host RSS})
\]

and, for every preregistered comparator \(C\in F(B_k)\),

\[
LCB95(INDEX(S)-INDEX(C))>\delta_k.
\]

The claim licensed is only:

> “S exceeds every pre-registered, reproducible open comparator and baseline family searched under budget \(B_k\) by at least \(\delta_k\) on KOT-AI-INDEX/2-vN.”

It never licenses “better than all models of the same size and compute.”

The frozen threat register must map at least these channels to executable counters:

| Gaming channel | Mandatory counter |
|---|---|
| Padding, serialization shopping | One canonical packer for all arms |
| Moving functionality into the free base | Base image frozen before architecture work; arm-specific code/data always counted |
| Remote-store laundering | Remote snapshot bytes count; an unbounded dependency voids the smaller-deployment claim |
| Warm-cache-only reporting | Separate cold and warm results; both required |
| Output/batch/concurrency shopping | Frozen stop rules, maximum tokens, load shapes and arrival schedule |
| Symbolic work treated as zero | Whole-system CPU, I/O, latency, memory and energy measurement |
| Suite/domain shopping | Versioned benchmark manifest, equal fixed macro weights |
| Abstention gaming | Abstentions score incorrect; coverage/risk reported separately |
| Answer-key encoding | Decontamination hard gate plus post-freeze sealed evaluation |
| Unequal tuning | Per-arm CPU-hour and accelerator-hour caps, fixed dev-selection rule |
| Comparator dodging | Closed roster, public nomination window, search log, independent challenger gate |
| Oracle formalisation | Natural benchmark text only; oracle diagnostics cannot enter W1 |

## 1. KOT-AI-INDEX/2

### 1.1 Proposed benchmark manifest

Every final manifest row must contain:

```text
benchmark_id, domain, source_uri, upstream_commit_or_release,
config, split, row_count, canonical_item_sha256, licence,
prompt_sha256, scorer_sha256, metric, chance, ceiling,
rungs, scalar_or_vector_only
```

A release name without `canonical_item_sha256` is not a frozen pin.

| Domain/component | Proposed immutable release and scored split | Rungs | Metric | Chance \(c\) | Ceiling \(u\) |
|---|---|---:|---|---:|---:|
| D1 TinyStories held-out loss | Existing programme TinyStories validation corpus; full existing corpus digest must be copied into the index manifest | R0+ | token NLL, vector-only | n/a | n/a |
| D1 BLiMP | Official BLiMP 1.0, all 67 paradigms × 1,000 minimal pairs `[SV]` | R0+ | forced-choice sentence log-prob accuracy | .50 | .964 `[SV]` |
| D1 EWoK | EWoK-core 1.0, all 4,374 items `[SV]` | R0+ | minimal-pair accuracy | .50 | 1.000 |
| D2 HellaSwag | `Rowan/hellaswag`, validation, 10,042 items, release 1.1.0 `[SV]` | R1+ | normalized option log-prob accuracy | .25 | 1.000 |
| D2 PIQA | `ybisk/piqa`, validation, release 1.1.0 `[SV]` | R1+ | option log-prob accuracy | .50 | 1.000 |
| D2 WinoGrande | `allenai/winogrande`, `winogrande_xl/dev`, release 1.1.0 `[SV]` | R1+ | option log-prob accuracy | .50 | 1.000 |
| D3 ARC-Easy | `allenai/ai2_arc`, `ARC-Easy/test`, 2,376 rows; canonical JSONL SHA `09ab01ecb7493f88ebe45f4183360b102937d3879f566216e62f4ddeececdf56` | R1+ | option log-prob accuracy | .25 | 1.000 |
| D3 ARC-Challenge | `allenai/ai2_arc`, `ARC-Challenge/test`, 1,172 rows; SHA `86ccaace4cd159b5c02b6b3339ebe8a7022a54f1b488e433c060b3bc38ac1f63` | R1+ | option log-prob accuracy | .25 | 1.000 |
| D3 OpenBookQA | `allenai/openbookqa@388097ea7776314e93a529163e0fea805b8a6454`, `main/test`, 500 rows | R1+ | option log-prob accuracy | .25 | 1.000 |
| D3 MMLU-Pro | `TIGER-Lab/MMLU-Pro`, official test release current at freeze `[SV]` | R3+ | per-category 5-shot accuracy | .10 | 1.000 |
| D4 PR-KOT/1 | Programme-owned generator v1; 10,000 four-choice items, seeds `2026071900–2026071999`, balanced across held-out rules, compositions, depths and paraphrase families | R0+ | accuracy; split-family macro | .25 | 1.000 |
| D4 CLUTRR | EMNLP release archive SHA `b4029f68e555ba89dd5836d5f1d9049ca97fc54ed71ed880a5f5351f6c40228e`; clean systematic-generalisation bundle `data_089907f8`, test depths 2–10 | R1+ | 23-relation accuracy, depth-macro | 1/23 | 1.000 |
| D4 ProofWriter | Official ProofWriter OWA D0–D5 test sets, depth-macro, release/bytes pinned at freeze `[SV]` | R1+ | True/False/Unknown accuracy | 1/3 | 1.000 |
| D4 FOLIO | FOLIO v0.0 validation, 204 rows; canonical SHA `6922c988ef10987bd6545568ee8e63e897af80994591fa20539767da58f8e3d1` | R1+ | True/False/Unknown accuracy | 1/3 | 1.000 |
| D5 GSM8K | Official test, 1,319 rows; SHA `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14` | R1+ candidate | numeric exact match, 5-shot | 0 convention | 1.000 |
| D5 BBH | Original BIG-Bench Hard 23-task release, 3-shot direct prompting, no CoT `[SV]` | R3+ | per-task normalized accuracy | per item/task | 1.000 |
| D6 IFEval | Official Google IFEval release, prompt-level strict accuracy; release and canonical bytes pinned `[SV]` | R2+; R1 vector-only | strict prompt accuracy | 0 convention | 1.000 |
| D7 HumanEval | OpenAI HumanEval v1, 164 problems, pass@1, deterministic generation `[SV]` | R3+ | pass@1 | 0 convention | 1.000 |
| D7 LiveBench | Proposed release `2026-06`, exact tag and item digest required `[SV]` | R3+ | release-defined mechanical scores | per component | 1.000 |
| S sealed | Release-specific manifest produced under §5 | all W1 rungs | same domain metrics | same | same |

[STIPULATED — coordinator/Fable to ratify] The theoretical maximum `1.000` is used where no defensible human aggregate is already pinned. This removes reference-model drift at the cost of compressing scores for hard tasks. BLiMP alone uses the published human aggregate candidate `0.964`; its estimand and uncertainty require `[SV]`.

MMLU-cloze is excluded. RuleTaker is not separately scored because ProofWriter is the selected successor; it may remain a vector-only continuity diagnostic. BBEH is excluded below R4 because of expected floor effects. `[SV]`

### 1.2 Prompt and scoring pins

[STIPULATED — coordinator/Fable to ratify]

- MC/minimal-pair tasks: zero-shot option log likelihood, length-normalized where the benchmark convention requires it; no CoT.
- ARC/OpenBookQA: zero-shot in the headline index. Any five-shot continuity run is separate.
- ProofWriter/FOLIO/CLUTRR: one fixed natural-language instruction and answer menu; no gold parses or addresses.
- GSM8K: five fixed demonstrations selected by hashed ID; greedy generation; `max_new_tokens=512`; numeric canonicalizer frozen.
- IFEval: native prompt, greedy generation, `max_new_tokens=512`, prompt-level strict score primary.
- BBH: three fixed demonstrations, direct answer, no CoT.
- HumanEval: greedy pass@1, temperature 0, one sample, official execution sandbox and timeout pinned.
- All abstentions, parse failures and malformed outputs score incorrect. Refusal rate, unconditional dangerous-wrong rate, selective risk, covered/uncovered results and output length remain mandatory vector columns.

### 1.3 Normalisation and aggregation

For every scalar-eligible accuracy component \(b\), use the authority’s formula:

\[
\tilde{s}_b=\frac{s_b-c_b}{u_b-c_b}.
\]

[STIPULATED — coordinator/Fable to ratify] Publish both raw \(\tilde{s}_b\) and the scalar contribution

\[
s_b^*=\min(1,\max(0,\tilde{s}_b)).
\]

For each domain \(d\),

\[
D_d=\frac{1}{|B_d|}\sum_{b\in B_d}s_b^*,
\qquad
INDEX_R=\frac{1}{|D_R|}\sum_{d\in D_R}D_d.
\]

Weights are equal across included benchmarks within a domain and equal across included domains. Subtasks/depths are first macro-averaged within their benchmark. No inverse-variance, item-count, coverage, or architecture-dependent weighting is permitted.

The sealed index is separate and never folded into the public frozen-suite scalar.

### 1.4 Floor, variance and saturation handling

[STIPULATED — coordinator/Fable to ratify]

- Before architecture results exist, a component is excluded from a rung scalar if, for that rung’s anchor,  
  `UCB95(raw_score − chance) < 0.02`. It remains in the vector.
- Anchor by rung: R1 = 135M, R2 = 360M, R3 = 1.7B.
- A component also becomes vector-only if its normalized bootstrap SE exceeds `0.05`, or if any calibration anchor clips at the upper ceiling.
- Missing model output is incorrect. Missing benchmark items are not imputed; any scorer loss above `0.1%` of expected items invalidates the component.
- Benchmark size does not change its weight. Its larger or smaller uncertainty is exposed through per-benchmark CIs.
- Index values and comparisons are rung/version-specific. Scalars from different rungs or index versions are never directly compared.

### 1.5 When a scalar is defensible

A scalar may be reported only when all are true:

1. At least three capability domains remain scalar-eligible.
2. P3-E-CAL is GREEN for this exact manifest, prompts, scorers and harness.
3. Every scalar component passed the floor, variance and saturation rules.
4. No domain or benchmark was removed after architecture outputs were observed.
5. The complete domain and per-benchmark vectors are published one link away.
6. The scalar is used only within the same rung/version.
7. Refusal, covered/uncovered and dangerous-wrong columns are present.

Consequently, R0 is vector-first and diagnostic unless at least three valid domains are added by a later version; it cannot carry W1 under this proposal.

## 2. KOT-SIZE/2

### 2.1 Canonical packer: `kot-pack/2`

The arm manifest must enumerate every serving dependency:

- neural weights, embeddings and output heads;
- tokenizer, vocabulary, chat template and generation configuration;
- adapters, routers, GNNs, verifiers, reward models and selectors;
- kernel/world stores, rules, schemas and provenance required at inference;
- dense/sparse/graph indices and retrieval metadata;
- executors, binaries, shared libraries and arm-specific code absent from the base;
- prompt templates and tool schemas;
- any cache prepopulated before evaluation.

Excluded from figure 1 only: logs, benchmark outputs, development-only tests and build inputs not present in the serving artifact.

Canonicalisation is deterministic:

1. UTF-8/NFC paths, bytewise path order; no symlinks or device nodes.
2. JSON uses RFC 8785 canonical JSON; text uses UTF-8/LF; tensors use safetensors with lexicographically sorted keys and declared stored dtype.
3. Opaque serving indices are counted byte-for-byte as built.
4. Whole-file SHA-256 deduplication is allowed within an arm only.
5. UID/GID/time/mode metadata are normalized and excluded from payload bytes.
6. Figure 1 is canonical-manifest bytes plus unique canonical payload bytes.
7. Figure 2 is the concatenated canonical stream compressed using `zstd --ultra -19 --threads=1`; zstd binary/version is pinned.
8. Packing twice must produce identical manifest and stream hashes.
9. An unpacked artifact on the base image must boot and answer a frozen smoke suite using no undeclared file, cache, corpus, network endpoint or environment secret.

The pack record contains:

```json
{
  "schema": "kot-size/2",
  "system_id": "...",
  "artifact_sha256": "...",
  "base_oci_digest": "sha256:...",
  "packer_sha256": "...",
  "figure_1_canonical_payload_bytes": 0,
  "figure_2_zstd19_bytes": 0,
  "figure_3_warm": {"peak_host_rss": 0, "peak_vram": 0},
  "figure_4_cold": {
    "startup_seconds": 0,
    "peak_working_set_bytes": 0,
    "storage_bytes_to_first_answer": 0,
    "network_bytes_to_first_answer": 0
  },
  "figure_5_construction": {
    "source_bytes": 0,
    "peak_intermediate_bytes": 0,
    "cpu_hours": 0,
    "accelerator_hours": 0,
    "human_hours": 0,
    "usd": 0
  },
  "figure_6_remote": {
    "dependencies": [],
    "snapshot_canonical_bytes": 0,
    "bytes_per_query": 0
  }
}
```

A remote corpus/API must be snapshotted and counted. If the reachable byte extent cannot be bounded and packed, the arm is ineligible for a smaller-deployment claim.

### 2.2 Frozen base image

[STIPULATED — coordinator/Fable to ratify] Proposed selector:

```text
nvidia/cuda:12.4.1-runtime-ubuntu22.04@sha256:<RATIFICATION-DIGEST>
```

The final base record must also pin the Dockerfile SHA, OCI manifest digest, architecture, CUDA runtime, Python and generic library lockfile. The placeholder is an intentional freeze blocker: KOT-FAIR/2 cannot freeze until replaced with a real OCI digest produced before architecture development.

The base may contain only generic components available identically to all arms. Kernel engines, stores, indices, model runtimes used only by one family, custom CUDA extensions and architecture-specific code count as arm bytes.

## 3. KOT-COST/2

### 3.1 Resource vector

Per query and per suite, record:

- accelerator kernel time and estimated accelerator operations;
- process and child CPU-seconds;
- storage bytes read and written;
- network bytes sent and received;
- whole-run CPU, DRAM and accelerator energy where measurable;
- peak host RSS and peak accelerator memory, separately;
- end-to-end latency p50/p95;
- goodput under the frozen load shape;
- cold startup/index-load time;
- TTFT and inter-token latency for generative arms;
- input, retrieved and emitted token counts.

The primary W1 budget retains the four authority-defined components. [STIPULATED — coordinator/Fable to ratify] CPU-seconds, accelerator-time, I/O, TTFT and throughput additionally receive hard preregistered anti-laundering ceilings of three times the strongest fitting comparator’s measured value. Exceeding any one makes the arm inadmissible.

The neural-FLOP diagnostic is always reported and never binding:

\[
F_{\text{neural}} =
2P_{\text{active}}(T_{\text{in}}+T_{\text{out}})
+4Ld\left[
\frac{T_{\text{in}}(T_{\text{in}}+1)}2+
T_{\text{out}}T_{\text{in}}+
\frac{T_{\text{out}}(T_{\text{out}}+1)}2
\right].
\]

`P_active` counts active neural parameters per token; \(L,d\) are transformer layers and model width. MoE uses active, not total, experts. Formula inputs and omissions are published.

### 3.2 Hardware pin

[STIPULATED — coordinator/Fable to ratify] Primary candidate: dedicated x86-64 host with one NVIDIA A10G 24 GB, fixed performance clocks, pinned driver/CUDA/container, accessible NVML energy or ≥20 Hz power sampling, and CPU package/DRAM RAPL. `[SV]`

The final hardware manifest must pin CPU model/microcode, RAM, NUMA, storage volume/type, GPU PCI/UUID class, driver, firmware, clocks, power limit, kernel, container digest and measurement-counter boundaries.

If CPU plus GPU energy cannot be measured on one common platform for every arm, W1 is blocked rather than silently becoming energy-free.

### 3.3 Load shapes

[STIPULATED — coordinator/Fable to ratify]

- `SingleStream`: concurrency 1, closed-loop, labelled “unloaded service time.”
- `Server`: open-loop Poisson arrivals from seed `20260719`; rate fixed before S is measured at `0.5 / anchor_warm_median_service_time`.
- `Offline`: batch size 8 or the largest batch fitting all arms, whichever is smaller.
- Each warm cell runs at least 600 seconds and at least 1,000 completed queries.
- Latency-under-load is measured from intended issue time. Closed-loop measurements cannot be presented as latency under offered load.
- No cross-query response, activation or prompt memoisation; KV reuse is limited to a single query/batch.
- Prompt, maximum output length, stop strings and context/retrieval-token cap are frozen per benchmark.

### 3.4 Cold and warm protocol

**Cold:** reboot at the start of each day; fresh process/container; page cache dropped where supported; no model/index/cache loaded; measurement begins before process start and ends after the first valid answer. Ten cold repetitions per arm, resetting process and caches each time.

**Warm:** run the frozen 128-query warmup trace twice; discard warmup; then run the load shape. Ten repetitions per arm. Arms are A/B/A/B interleaved on the same host/session.

Cold and warm results are separate. W1 admissibility is checked in both states.

### 3.5 P3-D-HW repeatability

Run on at least three days separated by at least 24 hours, with at least two full host reboots. Run a fixed synthetic calibration probe before and after every session.

[STIPULATED — coordinator/Fable to ratify] Pass bands:

| Measure | Warm day/reboot band | Cold day/reboot band | Within-session requirement |
|---|---:|---:|---:|
| p50/p95 latency, CPU-s, accelerator-time, energy/query | each day median within ±5% of grand median | ±10% | CoV ≤5% |
| Throughput/goodput | ±5% | n/a | CoV ≤5% |
| Peak RSS/VRAM | ±2% | ±2% | no run >2% from session median |
| Storage/network bytes | exact for a fixed trace | exact | 0% unexplained drift |
| Output/item counts | exact | exact | 0% drift |

A session whose start/end probe differs by more than 5% is discarded in full. Failures are not selectively rerun; the failure and discard are logged.

## 4. KOT-LIFE/1

Every S and comparator publishes one ledger:

```json
{
  "schema": "kot-life/1",
  "system_id": "...",
  "artifact_sha256": "...",
  "donors": [{
    "model_revision": "...",
    "pretraining_tokens": null,
    "pretraining_accelerator_hours": null,
    "provenance": "...",
    "contamination_status": "known|unknown"
  }],
  "architecture_work": {
    "human_hours": 0,
    "cpu_hours": 0,
    "accelerator_hours": 0,
    "usd": 0
  },
  "tuning_search": {
    "cpu_hours": 0,
    "accelerator_hours": 0,
    "candidates_evaluated": 0,
    "selection_rule_sha256": "...",
    "dev_split_sha256": "..."
  },
  "store": {
    "source_snapshot_sha256": "...",
    "candidate_records": 0,
    "accepted_records": 0,
    "authoring_hours": 0,
    "review_hours": 0,
    "provenance_verification_hours": 0,
    "parse_embed_index_cpu_hours": 0,
    "parse_embed_index_accelerator_hours": 0,
    "refresh_cadence_days": null,
    "refresh_hours_per_cycle": null,
    "reindex_hours_per_cycle": null,
    "construction_bytes": 0
  },
  "inference_ref": "kot-cost/2 record",
  "amortisation": {
    "q1e3":  {"usd": null, "human_hours": 0, "joules": null},
    "q1e6":  {"usd": null, "human_hours": 0, "joules": null},
    "q1e9":  {"usd": null, "human_hours": 0, "joules": null}
  },
  "prices": [{
    "item": "...", "unit": "...", "value": 0,
    "currency": "USD", "as_of": "YYYY-MM-DD", "source": "..."
  }]
}
```

The amortisation rule is, separately for every unit \(u\):

\[
TCO_u(q)=fixed_u+build_u+refresh_u(q)+q\cdot inference_u.
\]

USD, human-hours and joules are never collapsed through a fabricated exchange rate. Dimension-drop arms state inherited donor pretraining; it is never netted out.

## 5. Anti-confound machinery

### 5.1 `kot-decon/1`

Inputs are every canonical text field in every store/build source and every benchmark question, choice, answer, rationale and available source page.

[STIPULATED — coordinator/Fable to ratify]

1. Normalize Unicode NFKC, lowercase, collapse whitespace, strip punctuation for matching.
2. Flag any shared word-level 8-gram.
3. Embed record/item text using `sentence-transformers/all-MiniLM-L6-v2`; revision and weights SHA must be pinned `[SV]`.
4. Flag cosine similarity `≥0.85`.
5. Human-review every flag. Unreviewed flags count as leakage.
6. Any confirmed leakage voids every W1 result using that store.
7. Every store record must carry source URI/hash, authoring session, date and author/build-agent identity.
8. Store authoring inputs, dev split, packer smoke set and benchmark suite are pairwise screened for disjointness.

Threshold calibration uses 100 verbatim inserts, 100 near-verbatim inserts with ≤10% token edits, 100 independently produced paraphrases and 1,000 same-domain negatives. Pass requires 100% verbatim recall, ≥99% near-verbatim recall, ≥90% paraphrase recall and ≤2% false-positive rate. Paraphrase misses remain a standing limitation; this gate certifies only gross-leak detection.

### 5.2 Sealed evaluation

[STIPULATED — coordinator/Fable to ratify]

- **Producer:** two-person evaluation-custodian team; neither may develop S, author its store, tune comparators, or see campaign error analysis.
- **Chronology:** architecture, stores, comparator configurations, prompts and analysis plan freeze first. The custodian then produces the release.
- **Size:** 250 items per active domain, minimum four domains and 1,000 total items. Procedural domains use held-out generator families/rule compositions, not merely new seeds.
- **Fresh evidence:** where temporal facts are tested, all arms receive the same content-hashed evidence snapshot and identical metered refresh/indexing budget. Live search is enabled for all or none.
- **Cadence:** one release per W1 campaign; releases expire after 90 days and are never reused for another claim.
- **Access:** encrypted at rest; release manifest hash committed before execution; only the custodian-controlled evaluation runner receives plaintext; developing agents receive no item-level feedback before verdict.
- **After use:** publish items, scores and per-item outputs; mark the release burned. Any resulting learning requires the next claim to use a new release.
- **Gate:** for every \(C\in F(B_k)\),  
  `LCB95(INDEX_sealed(S) − INDEX_sealed(C)) > 0.01`, with the same FWER method; additionally, the sealed advantage against the strongest comparator may not fall more than `0.03` below the frozen-suite advantage. `[STIPULATED — coordinator/Fable to ratify]`
- Any custody violation, pre-freeze exposure, asymmetric evidence refresh or failed gap gate voids W1.

### 5.3 Frontier builder and comparator pinning

Per rung, derive the primary budget from the measured bf16 anchor before S is measured:

- R1: SmolLM2-135M-Instruct.
- R2: SmolLM2-360M-Instruct.
- R3: SmolLM2-1.7B-Instruct.

The required source-family search includes:

1. All eligible open pure-neural donors nominated before roster closure.
2. Quantisation grid: unquantized, Q8_0, Q5_K_M, Q4_K_M, Q3_K_M and one pinned AWQ/GPTQ int4 implementation.
3. Structured pruning fractions 12.5%, 25% and 50% with recovery inside the tuning budget.
4. Distillation where affordable.
5. Matched generic RAG/tool use whenever S uses a store:
   - same source-evidence snapshot;
   - shared BM25 and one shared dense-retrieval cell;
   - identical byte, retrieved-token, latency and tuning budgets;
   - separate native-retrieval cell so the conventional RAG system is not forced to use a hostile representation.
6. Adaptive retrieval and task-appropriate adaptive test-time compute, including verifier-guided candidates when their build, bytes and inference costs fit.
7. A training-compute-matched plain twin whenever S trains from scratch.

Search proceeds by enumeration, byte screening, a fixed 10% dev mini-suite, successive halving, metered tuning, full dev measurement, admissibility filtering and content-hash freeze. Selection maximizes dev index subject to the complete resource constraints.

Tuning symmetry is componentwise:

```text
CPU-hours(C) ≤ registered CPU cap
accelerator-hours(C) ≤ registered accelerator cap
```

The same caps and selection rule apply to every family, including S. Equal configuration counts are not sufficient.

Comparator roster closure occurs 14 days before W1 prereg freeze. Maintainers, reviewers and external nominators may submit candidates before closure. The builder must measure them or publish a mechanical refusal reason. Five independently nominated blinded challenger configurations are then run once; if the builder’s best dev index is more than `0.01` below the best challenger, the frontier is invalid and must be rebuilt. `[STIPULATED — coordinator/Fable to ratify]`

Every comparator freezes:

```text
model/weights/tokenizer revisions
quantisation/pruning/distillation recipes
store/corpus/index hashes
retriever and verifier hashes
prompt/decoding/TTC configuration
tuning ledger
size and cost records
per-item dev outputs
```

Membership in \(F(B_k)\) uses resource UCB95, not point estimates. An arm whose UCB crosses a budget boundary is inadmissible.

## 6. Statistics

### 6.1 Programme-3 §2.5, wired in verbatim

> 1. **Margin wins:** a margin-δ superiority claim requires  
>    `LCB95(INDEX(S) − INDEX(B)) > δ` — the lower confidence bound itself clears  
>    the margin. A point estimate above δ with an LCB merely > 0 is NOT a margin  
>    win and is never reported as one.
> 2. **Multiplicity:** S is tested against multiple comparators (and multiple  
>    domains): use simultaneous confidence bounds / family-wise error control  
>    across the pre-registered comparator set; the FWER procedure is pinned in the  
>    analysis plan at freeze.
> 3. **Resampling:** hierarchical bootstrap across benchmark families and items,  
>    preserving paired predictions (same items, per-system outputs paired).
> 4. **Non-inferiority vs equivalence:** a "retains capability" claim is  
>    NON-INFERIORITY and uses a single one-sided test / one-sided CI against the  
>    pre-registered non-inferiority margin. TOST (two one-sided tests) is an  
>    EQUIVALENCE procedure and is reserved for genuine equivalence claims. All  
>    revision-1 uses of "TOST" for retention claims (the H-DD central claim  
>    included) are corrected accordingly.
> 5. One primary endpoint per experiment; kill criteria verbatim in the prereg;  
>    verdicts generated by the mechanical grader and cross-vendor audited, per  
>    standing practice.

### 6.2 Concrete analysis plan

[STIPULATED — coordinator/Fable to ratify]

- `δ1 = δ2 = δ3 = 0.02` normalized index units. R0 has no W1 scalar.
- One primary endpoint: the minimum simultaneous margin over all comparators,
  \(\min_C LCB95(INDEX(S)-INDEX(C))\).
- 20,000 hierarchical bootstrap replicates, seed `20260719`.
- At each replicate, resample benchmark families within domain, then items within benchmark; all S/comparator predictions for an item travel together. Domain weights remain fixed.
- Form max-t simultaneous one-sided bounds across comparators; include domains in that family only where domain-level claims are made.
- No fallback multiplicity method may be selected after results. If max-t computation fails preregistered diagnostics, the verdict is instrument-invalid.
- Sample-size/power calculation uses the realized comparator count and calibration covariance before campaign freeze.
- Non-inferiority default margin is `−0.02`; any other margin requires experiment-specific rationale.
- Mechanical grader consumes only frozen per-item rows and emits PASS/FAIL/INSTRUMENT-INVALID.
- Cross-vendor audit checks 100% of rule evaluation and a seeded 10% item sample; unresolved audit disagreement blocks the verdict.

The prereg must fill:

```text
index/harness/suite/scorer hashes
S and F(B_k) artifact hashes
primary estimand and δ
secondary domain claims
budget vector and resource ceilings
sample sizes, seeds and prompts
hierarchical bootstrap levels
FWER procedure and diagnostics
floor/exclusion list
missing/malformed/abstention handling
sealed release custody reference
decontamination record
kill text
grader and audit pins
```

## 7. P3-E-CAL calibration-report protocol

This calibration judges pure-neural systems only. No kernel, store, retrieval, parser, symbolic engine or oracle input is permitted.

### 7.1 Subjects

- `HuggingFaceTB/SmolLM2-135M-Instruct@12fd25f77366fa6b3b4b768ec3050bf629380bac`
- `HuggingFaceTB/SmolLM2-360M-Instruct@a10cc1512eabd3dde888204e902eca88bddb4951`
- `HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a7173562077fd711b654946d38674`

### 7.2 Exact run

1. Materialize and hash every proposed dataset and scorer.
2. Hash-partition each benchmark by item ID: 20% `CAL-FLOOR`, 80% `CAL-ORDER`.
3. On `CAL-FLOOR`, apply the §1.4 floor and saturation rules without inspecting ordering results. Freeze `INDEX_COMMON` as the surviving R1 component set.
4. Run all three models on the identical `CAL-ORDER` items and prompts.
5. Repeat the complete harness five times per model across the three P3-D-HW days. Deterministic option-logprob outputs should be byte-identical; generated-task score variability is measured.
6. Run KOT-SMOL-CONT/1 as a separate harness-fidelity diagnostic.
7. Canonically pack each model twice; run its minimal-sufficiency smoke test.
8. Execute ten warm and ten cold cost repetitions per model per day under all mandatory load shapes.
9. Produce two mock sealed releases under each applicable production recipe and run all three anchors without developer access.
10. Calibrate `kot-decon/1` on the planted-positive/negative set; this does not introduce a store into model evaluation.
11. Emit KOT-SIZE/2, KOT-COST/2 and KOT-LIFE/1 records for all three models.

### 7.3 GREEN criteria

All are conjunctive:

**Primary endpoint — known-order separation**

\[
LCB95(INDEX_{COMMON}(360M)-INDEX_{COMMON}(135M))>0
\]

and

\[
LCB95(INDEX_{COMMON}(1.7B)-INDEX_{COMMON}(360M))>0,
\]

using simultaneous one-sided 95% bounds across the two adjacent comparisons. Point estimates must also satisfy `1.7B > 360M > 135M`.

**Index variance**

- Across the five identical harness runs, `SD(INDEX_COMMON) ≤ 0.005` for every model.
- No domain score has run-to-run SD above `0.010`.
- Hierarchical-bootstrap SE of each model’s index is at most `0.015`.
- Recomputing the 20,000-replicate CI with seed `20260720` may move either adjacent LCB by at most `0.002`.
- No scalar component may saturate at 1.0.
- At least three domains must survive the floor rule.

**Harness anchoring**

- Every genuinely variant-matched KOT-SMOL-CONT/1 cell must be within ±2.0 percentage points of its published SmolLM2 card cell.
- A cell lacking a matching published prompt/model variant is labelled “no anchor,” not failed or substituted.

**Size**

- Two independent packs of each model produce identical manifest/stream SHA-256.
- The packed artifact boots from the frozen base and passes every smoke query.
- Canonical figure-1 bytes must satisfy `135M < 360M < 1.7B`; violation is a packer diagnosis, not a capability result.

**Cost and hardware**

- Every warm metric, memory metric, byte counter and cold metric passes the bands in §3.5 on every model.
- At least three days and two reboots are represented.
- No more than one session may be discarded; any discarded session is repeated once under a rule fixed before results.
- CPU and GPU energy boundaries must both be measurable. A missing binding energy cell is FAIL.
- All completed-query, token and output hashes are exact for deterministic traces.

**Sealed machinery**

- Both mock releases preserve the point ordering `1.7B > 360M > 135M`.
- Spearman rank correlation with frozen-suite model ordering is exactly 1.0.
- Absolute frozen-to-mock index shift is at most `0.03` per model after the difficulty-matching procedure.

**Decontamination**

- The planted-set recall/false-positive thresholds in §5.1 pass.
- Every flagged pair is adjudicated.

### 7.4 FAIL rule

Any failed primary comparison, variance bound, hardware-repeatability band, missing binding energy measurement, pack determinism check, sealed ordering check or decontamination gate makes P3-E-CAL RED.

RED means:

- KOT-FAIR/2 does not freeze.
- No neurosymbolic system may be scored for W1.
- No Phase-2/G4 architecture prereg may cite the instrument.
- The failure must be localized to index membership/normalisation, harness, hardware rig, packing, seal production or screener; repair requires a new RC version and a complete calibration rerun.

A GREEN report licenses only “the instrument separates and repeatedly measures this pure-neural anchor triple.” It licenses no architecture or efficiency conclusion.

## Ratification register

The following proposed values require coordinator/Fable ratification:

1. Dataset semantic releases, full upstream commits, licences and canonical byte hashes not already present locally—especially BLiMP, EWoK, PIQA, WinoGrande, ProofWriter, IFEval, MMLU-Pro, BBH, HumanEval and LiveBench. `[SV]`
2. PR-KOT/1 generator semantics, item count, four-choice format and seed range.
3. BLiMP ceiling `.964`; theoretical ceiling `1.000` elsewhere; scalar clipping.
4. Floor span `.02`, variance exclusions `.05`, three-domain scalar minimum.
5. `δ1–δ3=.02`, sealed margin `.01`, sealed-gap band `.03`, non-inferiority margin `.02`.
6. Prompt shots, no-CoT rule, output limits and benchmark-specific scorers.
7. Canonical serialization choices, whole-file deduplication and zstd-19.
8. The actual base-image OCI digest and dependency lockfiles.
9. A10G hardware choice and availability of whole-system CPU/GPU energy counters. `[SV]`
10. Load shapes, 600-second/1,000-query minimum, repetitions and ±2/5/10% repeatability bands.
11. Hard secondary resource ceilings at three times the strongest comparator.
12. Lifecycle amortisation volumes \(10^3,10^6,10^9\).
13. Decontamination 8-gram, MiniLM revision, cosine `.85` and planted-set thresholds. `[SV]`
14. Sealed producer governance, 250 items/domain, 90-day cadence and one-shot burn rule.
15. Frontier transform grid, 14-day nomination window, five challengers and `.01` regret gate.
16. 20,000 max-t hierarchical-bootstrap replicates and fixed seeds.
17. Calibration SD/SE/CI-stability thresholds and mock-seal requirements.

## Residual gameability and standing limitations

- Closed or incompletely disclosed neural training corpora cannot be audited for contamination.
- Rules or abstractions may encode benchmark knowledge without triggering lexical or embedding screening.
- A custodian can leak a sealed release; access controls reduce but cannot prove independence.
- Generator-based sealed tasks remain related to their generator family even when rules are held out.
- Equal source snapshots do not guarantee equal information accessibility after passages, triples and typed records are derived.
- The party building S still helps build its opponents; search disclosure and challengers cannot prove frontier completeness.
- Anchor-derived budgets and equal domain weights are normative and can favor particular profiles.
- The scalar can conceal regressions despite mandatory vectors.
- Perfect-score ceilings compress hard-task movement and the BLiMP human ceiling may saturate.
- Hardware counters have measurement boundaries; RAPL/NVML do not equal whole-facility energy.
- Cold-cache behavior on a dedicated rig may not transfer to production storage/network systems.
- Human authoring and review hours vary in quality and cannot be converted fairly into accelerator-hours.
- A remote service’s reachable corpus may be difficult to bound.
- The SmolLM2 size ordering is a strong same-family calibration expectation, not a law that larger models always score higher.

No repository file, bead, preregistration, or frozen object was created; this is the requested inline review proposal.