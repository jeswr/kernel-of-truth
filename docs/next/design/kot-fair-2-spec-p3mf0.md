# KOT-FAIR/2 measurement + fair-comparison framework — REVISED DRAFT, Revision 1 (bead P3-MF-0)

> **STATUS: REVISED DRAFT — NOT FREEZE-READY; Part-B technical edits applied; Part C (correctness
> instrument) + re-review + Fable critique pending before any prereg-freeze; freeze also gated on the
> #57 a/b/c decision.** Revision 1 (2026-07-20, Programme-3 Phase-1, overflow-Fable lane) applies the
> **12 ordered Part-B reconciliation edits** from the freeze-readiness review
> ([kot-fair-2-review1-freeze-readiness.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md) — GPT-5.6 review reconciled against the 10 completed
> Phase-0 lit-reviews; verdict NOT-freeze-ready) to the 2026-07-19 GPT-5.6 draft. This CONCRETISES
> docs/next/programme-3-neurosymbolic-architecture.md §1-§2. All `[STIPULATED — coordinator/Fable to
> ratify]` values remain PROPOSED, not fixed. The review's **Part C (the correctness-instrument gap) is
> deliberately NOT applied** — it is a MAINTAINER/Fable strategic decision tied to the #57 a/b/c
> framework-adjudication crux; see "## Part C — correctness instrument — DEFERRED pending #57" below.
> NEXT: (1) re-review of this revision; (2) Fable adversarial critique; (3) the #57 decision + the
> Part-C correctness-instrument decision; (4) only then freeze via P3-D-INDEX (also needs P3-D-THREAT
> ratification). Do NOT treat as frozen. Itemised changes: "## Revision 1 — Part-B reconciliation
> edits applied". Source: poc/gpt56-review/p3mf0-kotfair-spec/ + review-1 Part-B fixes.

> **Tags:** four-tag scheme per programme discipline — `[MEASURED: ref]` observed fact with source;
> `[LIT-BACKED: ref]` literature-dependent choice with a resolvable backing; `[STIPULATED]` design
> choice awaiting ratification; `[EXTRAPOLATION]` forward claim beyond measurement (deliberately
> unused in this revision). The draft's `[SV]` source-verification markers are retained unchanged.

---

# KOT-FAIR/2 — measurement and fair-comparison framework

> **Status:** `KOT-FAIR/2-rc1` (REVISED DRAFT, Part-B edits applied), PROPOSAL for re-review and Fable critique. It is not frozen, preregistered, scheduled, or evidence. No Phase-2/G4/W1 work may freeze until every unresolved pin below is filled, the #57 a/b/c decision and the Part-C correctness-instrument decision land, P3-E-CAL is GREEN, and the resulting manifest is content-hashed.
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

(the energy component bound under the §3.1a boundary rules), and, for every preregistered comparator \(C\in F(B_k)\),

\[
LCB95(INDEX(S)-INDEX(C))>\delta_k,
\]

**and additionally** (Revision 1, per review Part-B edit #1) `[PROPOSED-PREREG-ROW-MF0-R1a]`: for every scalar-eligible domain \(d\) in the rung's frozen core-domain set and its preregistered **per-domain frontier comparator** \(C^{d}\) (the strongest admissible comparator on domain \(d\), pinned at roster closure),

\[
LCB95\left(D_d(S)-D_d(C^{d})\right)>-\delta_{NI},
\]

a simultaneous one-sided per-domain NON-INFERIORITY condition with preregistered margin \(\delta_{NI}\) (default `0.02`, §6.2), carried inside the same predeclared multiplicity family. **W1 is scalar superiority AND per-domain non-inferiority**: a system may not buy a large single-domain gain with regressions elsewhere and still pass. "No regression" means this frozen one-sided non-inferiority margin, not an impossible demand that every point estimate increase.

[LIT-BACKED: reports/lit-p3-eval.md §2, §7] This answers the construct-validity objection to any stand-alone scalar: the composite-index review returned a defensibility NULL for a bare scalar on this programme's suite. Consequently **the metric VECTOR (per-domain and per-benchmark scores, plus the mandatory refusal/coverage/risk columns) is the primary descriptive object of every KOT-FAIR/2 report**; the scalar exists for ranking inside the W1 decision rule and may never be quoted without the vector one link away.

**Framing discipline (add-capability, #57-pending) `[STIPULATED]`:** W1 defines the efficiency claim IF one is registered. Nothing in this framework asserts, presupposes, or requires that any governed architecture make — or win — a matched-resource efficiency claim; the governed family is crux-validated as ADD-CAPABILITY (see P3-D-THREAT Rev1 header discipline), and the primary endpoint framing for architecture claims awaits the #57 a/b/c decision plus the Part-C correctness-instrument decision (deferred; see the Part-C placeholder below).

The claim licensed is only:

> “S exceeds every pre-registered, reproducible open comparator and baseline family searched under budget \(B_k\) by at least \(\delta_k\) on KOT-AI-INDEX/2-vN, with no preregistered domain regression beyond \(\delta_{NI}\).”

It never licenses “better than all models of the same size and compute.”

The frozen threat register must map at least these channels to executable counters:

| Gaming channel | Mandatory counter |
|---|---|
| Padding, serialization shopping | One canonical packer for all arms |
| Moving functionality into the free base | Base image frozen before architecture work; arm-specific code/data always counted |
| Remote-store laundering | Remote snapshot bytes count; an unbounded dependency voids the smaller-deployment claim |
| Warm-cache-only reporting | Separate cold and warm results; both required |
| Output/batch/concurrency shopping | Frozen stop rules, maximum tokens, load shapes and arrival schedule |
| Symbolic work treated as zero | Whole-run CPU, I/O, latency and memory measurement + boundary-explicit energy (§3.1a) |
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
| D4 CLUTRR | EMNLP release archive SHA `b4029f68e555ba89dd5836d5f1d9049ca97fc54ed71ed880a5f5351f6c40228e`; clean systematic-generalisation bundle `data_089907f8`, test depths 2–10 | R0+ low-hop (depths 2–3, depth-stratified component, LCB floor-gated); R1+ full | 23-relation accuracy, depth-macro | 1/23 | 1.000 |
| D4 ProofWriter | Official ProofWriter OWA D0–D5 test sets, depth-macro, release/bytes pinned at freeze `[SV]` | R0+ shallow (D0–D1 depth-stratified, LCB floor-gated); R1+ full | True/False/Unknown accuracy | 1/3 | 1.000 |
| D4 FOLIO | FOLIO v0.0 validation, 204 rows; canonical SHA `6922c988ef10987bd6545568ee8e63e897af80994591fa20539767da58f8e3d1` | R2+ (moved per review edit #3; R1 only on a passing LCB floor census) | True/False/Unknown accuracy | 1/3 | 1.000 |
| D5 GSM8K | Official test, 1,319 rows; SHA `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14` | R2+ candidate (moved per review edit #3; below R2 only on a passing LCB floor census) | numeric exact match, 5-shot | 0 convention | 1.000 |
| D5 BBH | Original BIG-Bench Hard 23-task release, 3-shot direct prompting, no CoT `[SV]` | R3+ | per-task normalized accuracy | per item/task | 1.000 |
| D6 IFEval | Official Google IFEval release, prompt-level strict accuracy; release and canonical bytes pinned `[SV]` | R2+; R1 vector-only | strict prompt accuracy | 0 convention | 1.000 |
| D7 HumanEval | OpenAI HumanEval v1, 164 problems, pass@1, deterministic generation `[SV]` | R3+ | pass@1 | 0 convention | 1.000 |
| D7 LiveBench | Proposed release `2026-06`, exact tag and item digest required `[SV]` | R3+ | release-defined mechanical scores | per component | 1.000 |
| S sealed | Release-specific manifest produced under §5 | all W1 rungs | same domain metrics | same | same |

[STIPULATED — coordinator/Fable to ratify] The theoretical maximum `1.000` is used where no defensible human aggregate is already pinned. This removes reference-model drift at the cost of compressing scores for hard tasks. BLiMP alone uses the published human aggregate candidate `0.964`; its estimand and uncertainty require `[SV]`.

MMLU-cloze is excluded. RuleTaker is not separately scored as a headline component because ProofWriter is the selected successor; depth-stratified RuleTaker splits are R0/R1 continuity-diagnostic candidates alongside shallow ProofWriter, subject to the same LCB floor census. BBEH is excluded below R4 because of expected floor effects. `[SV]`

**Rung-membership rule (Revision 1, per review edit #3).** [LIT-BACKED: reports/lit-p3-eval.md §6] The rung columns above are the pre-calibration hypothesis: low-floor components — BLiMP, the EWoK domains that pass the floor census, low-hop CLUTRR, and shallow/depth-stratified ProofWriter–RuleTaker — anchor R0/R1; FOLIO and GSM8K sit at R2+ unless the rung-specific **LCB floor census** (§1.4) proves discrimination lower; MMLU-Pro and BBH remain R3+. Final per-rung membership is fixed by that census on each rung's anchor BEFORE any architecture output exists; a membership shift after census is an index VERSION change.

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

[LIT-BACKED: reports/lit-p3-eval.md §1] **Aggregation method citation and prohibition (Revision 1, per review edit #2).** This is the method of **HELM Capabilities (2025)**: mean of chance/ceiling-normalised scores under fixed macro-weights — the method HELM itself adopted after abandoning mean win rate. **Mean-win-rate aggregation is PROHIBITED** in every KOT-AI-INDEX/2 computation, headline or diagnostic: win-rate aggregates are unstable to comparator-set composition and reward rank inversions rather than calibrated margins. No index version may reintroduce win-rate aggregation without a full index VERSION change and re-review.

The sealed index is separate and never folded into the public frozen-suite scalar.

### 1.4 Floor, variance and saturation handling

[STIPULATED — coordinator/Fable to ratify]

- **LCB floor gate (Revision 1 — the prior UCB rule is WITHDRAWN as statistically backward)** `[PROPOSED-PREREG-ROW-MF0-R1b]`: before architecture results exist, a component is INCLUDED in a rung scalar only if, for that rung's anchor,
  `LCB95(raw_score − chance) > f`, with floor span `f = 0.02` `[STIPULATED — coordinator/Fable to ratify]`. Inclusion requires *demonstrated* discrimination above chance; a component whose estimate is at chance but whose interval is merely wide is excluded from the scalar (it remains in the vector). The withdrawn rule — exclude only when `UCB95(raw_score − chance) < 0.02` — admitted exactly such uncertain-at-chance components and is never used.
- Anchor by rung: R1 = 135M, R2 = 360M, R3 = 1.7B; the R0 anchor is pinned at P3-D-INDEX. The floor census runs per rung on that rung's anchor (§1.1 rung-membership rule).
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

### 1.6 Proxy-rung asymmetry — kill-not-certify (Revision 1, per review edit #4) `[PROPOSED-PREREG-ROW-MF0-R1c]`

[LIT-BACKED: reports/lit-p3-eval.md §5; reports/lit-p3-tiny.md §6] Tiny-model (R0/R1) results have historically predicted *failures* far more reliably than *successes*. The asymmetry is therefore wired in verbatim:

- **R0/R1 directional kills may terminate a family.** A pre-registered kill criterion failing at R0/R1 is a valid family/claim termination at its registered scope; no higher-rung run is owed to a killed hypothesis.
- **Positive R0/R1 margins are HYPOTHESES, never confirmations.** A positive margin at R0/R1 licenses only the registration of a higher-rung confirmation experiment; it is never W1 evidence at any higher rung, never quoted as a cross-rung win, and never extrapolated across rungs.
- **Byte-identical overlap across rungs.** Every benchmark that appears at more than one rung keeps its prompts, scorers, and formats byte-identical across rungs (`prompt_sha256`/`scorer_sha256` equality enforced by the manifest), so cross-rung movement measures the system, not harness drift.

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
- energy per the §3.1a boundary record: named component energies (CPU-package/DRAM RAPL, GPU-board NVML) and, where available, wall/system energy — never a component sum labelled as total;
- peak host RSS and peak accelerator memory, separately;
- end-to-end latency p50/p95;
- goodput under the frozen load shape;
- cold startup/index-load time;
- TTFT and inter-token latency for generative arms;
- input, retrieved and emitted token counts.

The primary W1 budget retains the four authority-defined components, with the energy component bound per §3.1a.

**Secondary anti-laundering ceilings (Revision 1 — the 3× rule is WITHDRAWN).** The prior rule — ceilings at three times the strongest fitting comparator's measured value — is withdrawn as endogenous and indefensible: the "strongest fitting comparator" is endogenous to model selection; a slow or I/O-heavy strongest comparator grants S a large allowance; a zero-use comparator yields an impossible zero ceiling; 3× has no construct, power, or systems basis; and no single factor fits CPU, I/O, TTFT and throughput at once. Instead `[STIPULATED — coordinator/Fable to ratify]` `[PROPOSED-PREREG-ROW-MF0-R1k]`, ONE of two branches is ratified:

1. CPU-seconds/query, accelerator-time/query, storage+network I/O bytes/query, TTFT and minimum goodput each receive a **metric-specific ABSOLUTE ceiling, preregistered before S is measured**, derived from the calibration anchors' measured values plus a per-metric deployment-rationale headroom stated in the prereg — never derived from S, and never from any comparator selected after S exists; or
2. the budget vector \(B_k\) is **extended** to include the relevant resource coordinates as explicit Pareto-budget components, under the same UCB95 admissibility rule as the four primary components.

Whichever branch is ratified, every coordinate remains co-reported even when non-binding, and exceeding any preregistered ceiling makes the arm inadmissible.

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

### 3.1a Energy boundary, measurement states, and the "total energy" prohibition (Revision 1, per review edit #5) `[PROPOSED-PREREG-ROW-MF0-R1d]`

[LIT-BACKED: reports/lit-p3-sys.md §Q7] RAPL package/DRAM plus NVML GPU-board energy is NOT system energy: disk, NIC, motherboard, PSU losses, remote compute, and (platform-dependent) portions of host power sit outside those counters. Implicit whole-system energy is therefore replaced by an explicit **boundary record** carried by every KOT-COST/2 energy figure:

```json
"energy": {
  "boundary": "wall | component",
  "components_measured": ["cpu_package_rapl", "dram_rapl", "gpu_board_nvml"],
  "components_unmeasured": ["disk", "nic", "motherboard", "psu_loss", "remote_compute"],
  "method": "...",
  "counter_availability": "...",
  "sampling_hz": 0,
  "wrap_handling": "...",
  "error_band_pct": null,
  "system_energy_status": "MEASURED-WALL | UNMEASURED"
}
```

Rules `[STIPULATED — coordinator/Fable to ratify]`:

- **Naming:** "total energy"/"system energy" may name ONLY a wall/IPMI/Redfish-class whole-node measurement (`system_energy_status = MEASURED-WALL`). A component sum is always named by its components ("CPU-package+DRAM RAPL + GPU-board NVML energy"); calling component energy "total energy" is PROHIBITED on every claim surface.
- **Two admissible paths for the binding W1 energy component:** either (a) obtain a common wall/system measurement for every arm on the pinned platform, or (b) AMEND the binding budget to **named component-energy coordinates** — max CPU-package+DRAM RAPL energy/query and max GPU-board NVML energy/query, each binding separately — with `system_energy_status = UNMEASURED` recorded and the amendment co-stated on every claim. There is no third, implicit path.
- **`UNPROVEN` rule:** an apparent energy win consistent with work moving from a measured component into an unmeasured domain (e.g. GPU compute → disk/NIC/host-I/O/remote CPU) is labelled `UNPROVEN`, not a win. The grader checks the co-reported CPU-seconds, storage/network bytes and latency vector for such a movement signature; a signature without a covering measurement blocks any energy-superiority wording.
- **Remote compute:** remote computation/API execution is forbidden for admissible arms unless fully metered inside the boundary record; snapshotting a remote corpus (§2.1) accounts for bytes, never for remote compute or energy.

### 3.2 Hardware pin

[STIPULATED — coordinator/Fable to ratify] Primary candidate: dedicated x86-64 host with one NVIDIA A10G 24 GB, fixed performance clocks, pinned driver/CUDA/container, accessible NVML energy or ≥20 Hz power sampling, and CPU package/DRAM RAPL. `[SV]`

The final hardware manifest must pin CPU model/microcode, RAM, NUMA, storage volume/type, GPU PCI/UUID class, driver, firmware, clocks, power limit, kernel, container digest and measurement-counter boundaries.

If neither a common wall/system boundary nor the complete named component set (CPU package/DRAM RAPL + GPU-board NVML) can be measured on one common platform for every arm, W1 is blocked rather than silently becoming energy-free; a partial component set never silently substitutes (§3.1a).

### 3.3 Load shapes

[STIPULATED — coordinator/Fable to ratify]

- `SingleStream`: concurrency 1, closed-loop, labelled “unloaded service time.”
- `Server`: open-loop Poisson arrivals from seed `20260719`; rate fixed before S is measured at `0.5 / anchor_warm_median_service_time`.
- `Offline`: batch size 8 or the largest batch fitting all arms, whichever is smaller.
- Each warm cell runs at least 600 seconds and at least 1,000 completed queries — a FLOOR, never the accounting denominator (see drop accounting below).
- Latency-under-load is measured from intended issue time. Closed-loop measurements cannot be presented as latency under offered load.
- **Goodput SLO (Revision 1, per review edit #6)** `[STIPULATED — coordinator/Fable to ratify]`: goodput counts only completed queries whose end-to-end latency meets the preregistered per-benchmark latency SLO; every SLO value is frozen before any arm is measured. [LIT-BACKED: reports/lit-p3-sys.md §Q2]
- **Timeout/drop accounting:** every load cell reports issued, completed, timed-out, dropped, and unfinished-at-cutoff counts. Timed-out and dropped queries remain denominator events (scored incorrect where scored; included in offered-load accounting); survivorship removal of timed-out queries is prohibited.
- **Queue/timeout policy:** the queue discipline, timeout values, and the treatment of unfinished requests at cell end are frozen per load shape before any arm is measured.
- **Intended-send drift:** intended-vs-actual issue-time drift is recorded per cell; drift beyond a preregistered bound invalidates the cell (the load generator, not the system under test, failed).
- **Workload mix:** the benchmark/query mix within each load cell is manifest-pinned before any arm is measured.
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

**Revision 1 additions (per review edit #6)** `[STIPULATED — coordinator/Fable to ratify]` `[PROPOSED-PREREG-ROW-MF0-R1e]`:

- **Rank-based CIs:** latency percentiles and all other order statistics receive distribution-free rank-based (binomial order-statistic) confidence intervals; mean-type metrics use the hierarchical bootstrap. Measurement resolution is assessed in each metric's OWN units; a percentage latency band is never numerically compared with an index margin. [LIT-BACKED: reports/lit-p3-sys.md §Q4]
- **Adaptive repetition count:** at least ten repetitions per cell remain the floor; the final \(N\) is chosen by a frozen rank-based CI-width stopping rule (target widths preregistered per metric, in that metric's units), evaluated blind to any cross-arm comparison. The stopping rule freezes before any arm is measured.
- **Every-arm repeatability gate:** the §3.5 bands and probe protocol gate EVERY W1 campaign arm and EVERY comparator measurement — not only the P3-E-CAL anchors. An arm or comparator whose measurement fails its bands is remeasured under the frozen discard/repeat rule or becomes inadmissible; a comparator lost this way is reported as such, never silently dropped from \(F(B_k)\).

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
    "build_mint": {
      "candidate_records": 0,
      "accepted_records": 0,
      "rejected_records": 0,
      "attrition_rate": null,
      "authoring_hours": 0,
      "parse_embed_index_cpu_hours": 0,
      "parse_embed_index_accelerator_hours": 0,
      "construction_bytes": 0
    },
    "review_provenance": {
      "review_hours": 0,
      "reviewers_per_record": null,
      "redundancy_policy": "...",
      "measured_quality_operating_point": null,
      "provenance_verification_hours": 0
    },
    "staleness_refresh": {
      "refresh_cadence_days": null,
      "staleness_detection_hours_per_cycle": null,
      "refresh_hours_per_cycle": null,
      "reindex_hours_per_cycle": null,
      "dependency_fanout_mean": null,
      "revalidation_hours_per_cycle": null,
      "rollback_events": 0
    },
    "uncertainty": {
      "human_time_distribution": "...",
      "hours_p50": null,
      "hours_p90": null
    }
  },
  "inference_ref": "kot-cost/2 record",
  "amortisation": {
    "grid": [
      {"queries": 1e3, "duration_days": null, "usd": null, "human_hours": 0, "joules": null},
      {"queries": 1e6, "duration_days": null, "usd": null, "human_hours": 0, "joules": null},
      {"queries": 1e9, "duration_days": null, "usd": null, "human_hours": 0, "joules": null}
    ]
  },
  "prices": [{
    "item": "...", "unit": "...", "value": 0,
    "currency": "USD", "as_of": "YYYY-MM-DD", "source": "..."
  }]
}
```

**Store-accounting subledgers (Revision 1, per review edit #7)** `[PROPOSED-PREREG-ROW-MF0-R1f]` [LIT-BACKED: reports/lit-p3-store.md §3, §4]: the single flat store object is replaced by three per-record-class subledgers — **build/mint** (including rejected-candidate attrition), **human-review/provenance** (including review redundancy and the measured quality operating point the review hours buy), and **staleness-refresh** (including staleness detection, dependency/entailment fan-out, revalidation, reindex, and rollback) — plus a human-time **uncertainty** block (distributions, not only totals). Refresh cost is NOT a function of query count alone; the amortisation rule is therefore, separately for every unit \(u\):

\[
TCO_u(q,t)=fixed_u+build_u+refresh_u(t,\dot q)+q\cdot inference_u,
\]

with \(t\) the deployment duration and \(\dot q\) the query rate: a continuously refreshed one-year deployment and a one-day burst of the same query count are no longer indistinguishable. The amortisation grid pins (query-volume, duration) PAIRS `[STIPULATED — coordinator/Fable to ratify]`.

**Matched refresh baseline:** store refresh TCO is measured AGAINST a matched external-context baseline — the matched-RAG comparator (§5.3 item 5) receiving the same fresh-evidence snapshot cadence and the same metered refresh/indexing budget — so refresh economics are always a comparison, never a solo figure. [LIT-BACKED: reports/lit-p3-store.md §5]

USD, human-hours and joules are never collapsed through a fabricated exchange rate. Dimension-drop arms state inherited donor pretraining; it is never netted out. Human and method-development accounting remains intrinsically gameable through unlogged prior work and failed experiments: metering is prospective from freeze, failed candidates are included, and this stays a standing limitation — KOT-LIFE remains non-binding and W1 is never described as overall lifecycle efficiency.

**Sardana quarantine (Revision 1, per review edit #12)** `[PROPOSED-PREREG-ROW-MF0-R1l]` [LIT-BACKED: reports/lit-p3-sys.md §Q6]: Sardana et al. ("Beyond Chinchilla-Optimal") enters KOT-LIFE/1 ONLY as qualitative context for inference-volume-dependent optimal sizing. The SYS review found conflicting dollar examples between the paper and secondary accounts; until a direct read of the PDF reconciles them, **no specific saving figure, model size, or token count from that line may be copied into any KOT-LIFE ledger, example, default, or amortisation constant.**

## 5. Anti-confound machinery

### 5.1 `kot-decon/1`

Inputs are every canonical text field in every store/build source and every benchmark question, choice, answer, rationale and available source page.

[STIPULATED — coordinator/Fable to ratify]

1. Normalize Unicode NFKC, lowercase, collapse whitespace, strip punctuation for matching.
2. Flag any shared word-level 8-gram.
3. Embed record/item text using `sentence-transformers/all-MiniLM-L6-v2`; revision and weights SHA must be pinned `[SV]`.
4. Flag cosine similarity `≥0.85`.
5. Human-review every flag. Unreviewed flags count as leakage.
6. Any confirmed leakage voids every W1 result using that store. **"Confirmed leakage" means benchmark-derived or answer-bearing leakage** — an index item, its paraphrase, its source page, or content authored/selected using benchmark error analysis. Literal overlap with an independently sourced fact that a benchmark happens to ask about is adjudicated; where independent sourcing is documented, it is a reported finding, not an automatic void (Revision 1, per review edit #11).
7. Every store record must carry source URI/hash, authoring session, date and author/build-agent identity.
8. Store authoring inputs, dev split, packer smoke set and benchmark suite are pairwise screened for disjointness.
9. **Layered validation (Revision 1, per review edit #11)** `[PROPOSED-PREREG-ROW-MF0-R1j]` [LIT-BACKED: reports/lit-p3-eval.md §4]:
   - threshold DEVELOPMENT and VALIDATION use disjoint planted sets; thresholds selected and evaluated on the same examples are invalid;
   - paraphrase positives come from at least two independent sources (distinct generators/authors);
   - recall and false-positive rates are reported with confidence bounds (Clopper–Pearson), never as bare points — 100 paraphrases cannot substantiate a 90% population recall claim with useful precision, and the gate wording must carry that bound;
   - flagged and near-threshold pairs receive perturbation-based robustness checks;
   - Min-K-style donor membership diagnostics run wherever donor logits are available;
   - screening covers derivation inputs and source pages, not only final record text.

Threshold calibration uses 100 verbatim inserts, 100 near-verbatim inserts with ≤10% token edits, 100 independently produced paraphrases and 1,000 same-domain negatives — split into disjoint development and held-out validation subsets per rule 9. Pass requires, on the HELD-OUT set: 100% verbatim recall, ≥99% near-verbatim recall, ≥90% paraphrase recall and ≤2% false-positive rate, each published with its confidence bound. Paraphrase misses remain a standing limitation; this gate certifies only gross-leak detection.

### 5.2 Sealed evaluation

[STIPULATED — coordinator/Fable to ratify]

- **Producer:** two-person evaluation-custodian team; neither may develop S, author its store, tune comparators, or see campaign error analysis.
- **Chronology:** architecture, stores, comparator configurations, prompts and analysis plan freeze first. The custodian then produces the release.
- **Size (POWERED, not fixed — Revision 1, per review edit #11):** the sealed-suite size is computed from a preregistered power analysis using the calibration covariance, the realized comparator count, the rare dangerous-wrong/rare-target rates, and the intended CI width for the sealed margin; 250 items per active domain, minimum four domains and 1,000 total items are a planning FLOOR, not the sizing rule. The power analysis and resulting size freeze before custodian production. Procedural domains use held-out generator families/rule compositions, not merely new seeds. [LIT-BACKED: reports/lit-p3-eval.md §4]
- **Fresh evidence:** where temporal facts are tested, all arms receive the same content-hashed evidence snapshot and identical metered refresh/indexing budget. Live search is enabled for all or none.
- **Cadence:** one release per W1 campaign; releases expire after 90 days and are never reused for another claim.
- **Access:** encrypted at rest; release manifest hash committed before execution; only the custodian-controlled evaluation runner receives plaintext; developing agents receive no item-level feedback before verdict.
- **After use:** publish items, scores and per-item outputs; mark the release burned. Any resulting learning requires the next claim to use a new release.
- **Gate:** for every \(C\in F(B_k)\),  
  `LCB95(INDEX_sealed(S) − INDEX_sealed(C)) > 0.01`, with the same FWER method. Additionally (Revision 1, per review edit #11), the frozen-to-sealed consistency condition is INFERENTIAL, not a point-estimate rule: with \(\Delta_{sealed}\) and \(\Delta_{public}\) the advantages against the strongest comparator, require one-sided **non-inferiority of the difference-in-differences**,  
  `LCB95(Δ_sealed − Δ_public) > −0.03` — a confidence bound on \(\Delta_{sealed}-\Delta_{public}\) under the §6.2 resampling, with the margin `[STIPULATED — coordinator/Fable to ratify]`.
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
5. **Matched generic RAG/tool use whenever S uses a store (COMPLETED, Revision 1, per review edit #9; detailed cells owned by P3-D-RAGC, consistent with P3-D-THREAT Rev1 §3.6)** `[PROPOSED-PREREG-ROW-MF0-R1h]` [LIT-BACKED: reports/lit-p3-rag.md §Q5]:
   - same source-evidence snapshot with **information parity certified across all three renderings — passages, triples, and typed records** (bidirectional proposition inventory; equal source snapshots do not guarantee equal information accessibility after derivation);
   - BOTH a shared BM25 cell AND a shared dense-retrieval cell with pinned model/index;
   - a separate native-retrieval cell so the conventional RAG system is not forced through a representation hostile to it;
   - retrieval recall and record/source provenance measured and reported per arm;
   - a position-shuffle sensitivity cell and a random-document control cell;
   - popularity-stratified reporting of retrieval-dependent results;
   - frozen context order per configuration;
   - a standard, widely used RAG harness at a pinned revision, not a bespoke one;
   - identical byte, build, retrieved-token, latency, tuning and query ledgers (KOT-SIZE/2, KOT-COST/2, KOT-LIFE/1) for every RAG cell.
6. Adaptive retrieval and task-appropriate adaptive test-time compute, including verifier-guided candidates when their build, bytes and inference costs fit.
7. **Compute-matched from-scratch twins via a FLOP-ledger specification (Revision 1, per review edit #8 — replaces the prior one-line "training-compute-matched twin"), whenever S trains from scratch** `[PROPOSED-PREREG-ROW-MF0-R1g]` [LIT-BACKED: reports/lit-p3-tiny.md §4, §7]:
   - a complete training FLOP ledger per arm: parameter count, interface/auxiliary tokens, sequence length, every training objective, last-layer/unembedding FLOPs, and any auxiliary execution (engine calls, verifiers, data machinery) — twins are matched on the LEDGER, never on parameter count or wall-clock alone;
   - same pretraining data and same data ORDER for twin and S wherever the architecture permits; deviations published;
   - IsoFLOP placement of the twin with the Porian et al. corrections (learning-rate/batch/warmup/last-layer corrections that reconcile the Kaplan-vs-Chinchilla exponent discrepancy), not naive scaling-law point reads;
   - paired training seeds (twin and S share the seed schedule; training seed enters the analysis as a random effect where the claim concerns a procedure);
   - a µP-parameterized width sweep at fixed depth for the twin's shape search, under the same tuning budget;
   - an optimizer/interface audit: Muon-class optimizer choices and interface-token asymmetries must be declared and either matched or charged to the ledger, with the **equal-tuning-budget fallback** when exact ledger matching is infeasible — both sides get the same total tuning compute under the frozen selection rule and the residual mismatch is published;
   - **released SmolLM2 anchors are PINNED COMPARATORS, never "compute-matched twins"** — their training compute is neither controlled by nor matched to this programme, and twin wording may never attach to them.

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

### 5.4 Factorial attribution controls and six-way attribution (RESTORED — Revision 1, per review edit #10; mandatory per parent §2.2)

The parent makes the factorial control design and six-way attribution MANDATORY for every W1 claim ([parent §2.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:469), [parent §2.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:525)); the rc0 draft omitted them entirely — a direct authority mismatch. This section is also the direct answer to the FUSE/RULE crux that component ablations and delivery probes do NOT establish structure causality: Deceive-KG/GTEval show semantics can be destroyed while downstream performance survives, and the RULE causal-evidence audit requires intervention-first evidence [LIT-BACKED: reports/lit-p3-fuse.md (controls/crux); reports/lit-p3-rule.md §3 (causal-evidence audit)].

**The detailed attribution design is the committed companion P3-D-THREAT Rev1** ([p3d-threat-factorial-controls.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md) — itself a REVISED PROPOSAL, not frozen; it is ratified jointly with this framework and gates P3-D-INDEX). KOT-FAIR/2 adopts it by reference and restores here the framework-level contract `[PROPOSED-PREREG-ROW-MF0-R1i]` `[STIPULATED — coordinator/Fable to ratify]`:

1. **Mandatory control families** (parent §2.2(2), all seven): (a) seed-pinned deranged store→item addressing `D`; (b) label permutation within records `P` — instantiated at the NL/schema binding seam with the joint equivariant-renaming positive control per THREAT Rev1 §3.2; (c) irrelevant-but-structurally-matched records `I`; (d) edge/relation shuffling for graph arms `G-edge`/`G-rel`/`G-adv`; (e) the aligned non-kernel typed store — split per THREAT Rev1 §3.5 into `T1`/`T2`/`T3` sub-factors with the executor factor kept separate; (f) the **matched generic-RAG/tool-use control** `R*` (§5.3 item 5 — both the same-host attribution cell and the strongest frontier RAG family); (g) the **kernel-as-text null** `X*` at matched token budget — **conditional per THREAT Rev1 §3.7**: a mandatory gate only when the registered claim names native/internal neural-symbolic integration, diagnostic otherwise. The default core conjunction is \(J_{core}=\{D,P,I,T^*,R^*\}\).
2. **Treatment-boundary law:** every control arm freezes a THREAT Rev1 §3.0 mutation-locus row (host-visible retrieval / entity-schema linking / formal request / authoritative store / engine results); a control supporting an engine-path claim must mutate the authoritative path *as consumed by the engine*; a declared-locus mismatch is `INSTRUMENT-INVALID` for that claim.
3. **Transformed-world validity gate:** every store-mutating control satisfies THREAT Rev1 §3.0b (licensed, conflict-valid, coverage-matched, recomputed-target). Destructive contrasts prove NECESSITY only; any structural-reasoning wording additionally requires the counterfactual-following GATE of THREAT Rev1 §3.4. Abstention triggered by transformation-induced conflict or coverage loss never counts as a pass.
4. **Six-way attribution ledger** (parent §2.3): every observed win is decomposed as far as the control cells allow across **kernel semantics / structured storage / retrieval / deterministic execution / retry-search / neural-symbolic integration**, as a contrast ledger with interactions reported — never six percentages forced to sum. Executor/retry/feedback cells use THREAT Rev1 §3.8's family-specific units and §3.9's feedback-information factor; H-GU-specific instantiations remain ▷ conditional on the H-GU API gate and are not preregistrable before it passes.
5. **Statistics:** the attribution family enters THREAT Rev1 §5.1's frozen two-stage gatekeeping procedure — stage 1: the W1 frontier + per-domain non-inferiority family (§0, §6.2); stage 2, only on a stage-1 pass: the attribution-control family — with simultaneous one-sided max-t bounds at family-wise \(\alpha=0.05\) within each stage and \(\delta_{attr,k}=\delta_k\) under the efficiency framing `[STIPULATED]`.
6. **W1 wiring** (parent W1 condition 4): the factorial controls must behave as pre-registered — derangement/permutation destroys any store-content-attributed component; the aligned-non-kernel and matched-RAG results are REPORTED as the attribution split, whatever they show. All controls run on both the public and sealed suites (THREAT Rev1 §5); a missing, inadmissible, or information-inequivalent required control yields `INSTRUMENT-INVALID`, never a caveat.

This section adds no control constructions beyond THREAT Rev1 and does not restate its treatment-boundary matrix, `G-*` gates, or `X*`-conditionality in different terms; any divergence between this section and a ratified THREAT is resolved in THREAT's favour and triggers a framework revision here.

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
- Form max-t simultaneous one-sided bounds across comparators. **The per-domain non-inferiority gates of §0 are BINDING and therefore always in the predeclared multiplicity family** (Revision 1, per review edit #1): the domain×frontier-comparator one-sided non-inferiority bounds enter the same max-t family or the frozen two-stage gatekeeping procedure of §5.4(5); they are never tested ad hoc. Additional domain-level superiority claims join the family only where registered.
- The sealed difference-in-differences condition (§5.2) is computed as a one-sided LCB on \(\Delta_{sealed}-\Delta_{public}\) under the same hierarchical resampling.
- No fallback multiplicity method may be selected after results. If max-t computation fails preregistered diagnostics, the verdict is instrument-invalid.
- Sample-size/power calculation uses the realized comparator count and calibration covariance before campaign freeze.
- Non-inferiority default margin is `−0.02` (this is the per-domain \(\delta_{NI}\) of §0); any other margin requires experiment-specific rationale.
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
- The full named component-energy set (CPU package/DRAM RAPL + GPU-board NVML) must be measurable on the common platform, with the §3.1a boundary record (including `system_energy_status`) emitted for every cell. A missing binding energy cell is FAIL. Wall/system measurement availability is probed and recorded; if absent, the W1 energy budget takes the amended component-energy form of §3.1a — never an unlabelled component sum.
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
4. LCB floor gate `f=.02` (`LCB95(score−chance)>f`, corrected direction, §1.4), variance exclusions `.05`, three-domain scalar minimum, and the frozen per-rung core-domain set required by the §0 non-inferiority condition.
5. `δ1–δ3=.02`, sealed margin `.01`, sealed difference-in-differences non-inferiority margin `.03` (inferential, §5.2), per-domain non-inferiority margin `δ_NI=.02` (§0).
6. Prompt shots, no-CoT rule, output limits and benchmark-specific scorers.
7. Canonical serialization choices, whole-file deduplication and zstd-19.
8. The actual base-image OCI digest and dependency lockfiles.
9. A10G hardware choice and availability of whole-system CPU/GPU energy counters. `[SV]`
10. Load shapes, 600-second/1,000-completed-query floor, goodput SLOs, queue/timeout policy, intended-send drift bounds, adaptive-repetition stopping widths (per metric, own units), and ±2/5/10% repeatability bands applied to every campaign arm and comparator (§3.3, §3.5).
11. Metric-specific absolute secondary resource ceilings — or the Pareto-extended \(B_k\) — preregistered before S is measured, replacing the withdrawn 3× rule (§3.1); plus the §3.1a energy-boundary decision (wall probe outcome or the amended component-energy budget wording). `[SV]`
12. Lifecycle amortisation grid — (query-volume, deployment-duration) pairs at \(10^3,10^6,10^9\) queries (§4) — and the KOT-LIFE subledger field definitions, quality operating-point metric, and matched external-context refresh baseline.
13. Decontamination 8-gram, MiniLM revision, cosine `.85`, the disjoint threshold-development/held-out validation split, CI reporting method, Min-K diagnostic availability, and planted-set thresholds (§5.1). `[SV]`
14. Sealed producer governance, the sealed-suite power analysis + 250/domain planning floor (§5.2), 90-day cadence and one-shot burn rule.
15. Frontier transform grid, 14-day nomination window, five challengers and `.01` regret gate.
16. 20,000 max-t hierarchical-bootstrap replicates and fixed seeds.
17. Calibration SD/SE/CI-stability thresholds and mock-seal requirements.
18. FLOP-ledger twin protocol constants: ledger field list, IsoFLOP/Porian correction recipe, µP width-sweep grid, paired-seed schedule, and the equal-tuning-budget fallback trigger (§5.3 item 7).
19. Matched-RAG completion cells: information-parity certificate method, pinned standard harness revision, position-shuffle/random-document/popularity-stratification recipes (§5.3 item 5; shared with P3-D-RAGC and P3-D-THREAT Rev1 §3.6).
20. Factorial-control constants (§5.4): adopted from P3-D-THREAT Rev1's own ratification list; THREAT and this framework are ratified jointly, and \(\delta_{attr,k}=\delta_k\) under the efficiency framing.

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

## Part C — correctness instrument — DEFERRED pending #57

**This section is deliberately a placeholder. The review's Part C is NOT applied in this revision, and the correctness instrument is NOT designed here.**

The review's Part C finds that KOT-FAIR/2 reports correctness columns (refusal, unconditional dangerous-wrong, selective risk, covered/uncovered — §1.2) but gives them no frozen definitions, challenge-set construction, statistical gates, or claim status: the framework can *report* a correctness signal but cannot *adjudicate* a correctness-value win ([review Part C](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:181)). Whether the correctness endpoint family becomes (a) a second success claim alongside W1, (b) a conjunctive W1 gate, or (c) a separate Pareto axis over correctness–coverage–cost is a **MAINTAINER/Fable strategic decision tied to the #57 a/b/c framework-adjudication crux**, and this revision does not pre-empt it — consistent with the review's own instruction that it "should not choose that re-weighting", and with P3-D-THREAT Rev1 §5.2, which carries the identical deferral.

Standing consequences until the decision lands `[STIPULATED]`:

- the §1.2 correctness columns remain mandatory DIAGNOSTIC vector columns with no claim status;
- KOT-FAIR/2 remains explicitly an efficiency framework in its binding W1 rule, and per the §0 framing discipline it does not force any architecture into that framing nor presuppose a matched-resource win;
- **this deferral is a named freeze blocker**: KOT-FAIR/2 CANNOT freeze with Part C unresolved (review freeze-requirement 8 — "add a claim-capable correctness instrument or explicitly scope it out" — is answered only by the #57 decision plus the resulting Part-C design or explicit scope-out).

## Revision 1 — Part-B reconciliation edits applied

Authoritative wording = the review's ["Part B — ordered reconciliation edits"](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md:155). All 12 applied; disposition per edit:

1. **W1 = scalar superiority AND per-domain non-inferiority; vector primary — ADOPTED.** §0 adds the simultaneous one-sided per-domain non-inferiority condition against the preregistered domain frontier (\(\delta_{NI}=0.02\) default, §6.2 multiplicity family), cites the construct-validity objection, and names the vector the primary descriptive object. (MF0-R1a)
2. **HELM Capabilities 2025 cited; mean-win-rate PROHIBITED — ADOPTED.** §1.3 keeps mean-of-normalised-scores and prohibits win-rate aggregation in every computation.
3. **Rung membership + LCB floor — ADOPTED.** §1.4 replaces the backward UCB exclusion with the `LCB95(score−chance)>f` inclusion gate; §1.1 moves FOLIO and GSM8K to R2+ (return only on a passing census), adds low-hop CLUTRR and shallow/depth-stratified ProofWriter–RuleTaker at R0/R1, keeps MMLU-Pro/BBH at R3+, and adds the per-rung floor-census rule. (MF0-R1b)
4. **Proxy-rung asymmetry — ADOPTED.** New §1.6: R0/R1 directional kills may terminate a family; positive margins are hypotheses requiring higher-rung confirmation; overlapping prompts/scorers/formats byte-identical across rungs. (MF0-R1c)
5. **Energy boundary — ADOPTED.** New §3.1a: explicit boundary records, `MEASURED-WALL`/`UNMEASURED` states, the `UNPROVEN` movement rule, the "total energy" naming prohibition, and the two admissible paths (wall measurement or an amended budget of named component-energy coordinates). §3.2 and §7.3 aligned. (MF0-R1d) *Additionally, folded into the same KOT-COST repair per review Part A / freeze-requirement 3: the endogenous 3× secondary ceilings are WITHDRAWN and replaced in §3.1 with preregistered metric-specific absolute ceilings or an explicitly Pareto-extended \(B_k\).* (MF0-R1k)
6. **Poisson design strengthened — ADOPTED.** §3.3 adds frozen goodput SLOs, issued/completed/timed-out/dropped/unfinished accounting, queue/timeout policy, intended-send drift bounds, and a frozen workload mix; §3.5 adds rank-based CIs (per-metric units), the adaptive repetition stopping rule, and the every-arm/every-comparator repeatability gate. (MF0-R1e)
7. **KOT-LIFE subledgers — ADOPTED.** §4 splits the store ledger into build/mint (with attrition), review/provenance (with redundancy + measured quality operating point), and staleness-refresh (with fan-out/revalidation/reindex/rollback) subledgers plus an uncertainty block; \(TCO(q)\) becomes \(TCO(q,t)\) with a (volume, duration) grid; refresh TCO is measured against the matched external-context baseline. (MF0-R1f)
8. **FLOP-ledger twin spec — ADOPTED.** §5.3 item 7: full FLOP ledger (params/interface tokens/seq length/objectives/last-layer/aux execution), same data + order, IsoFLOP with Porian corrections, paired seeds, µP width sweep at fixed depth, Muon/interface audit with equal-tuning-budget fallback; SmolLM anchors labelled pinned comparators, never twins. (MF0-R1g)
9. **Matched-RAG completion — ADOPTED.** §5.3 item 5: three-rendering information parity, BM25 + dense + native cells, retrieval recall/provenance, position shuffle, random-document control, popularity stratification, frozen context order, pinned standard harness, identical bytes/build/query ledgers — consistent with P3-D-THREAT Rev1 §3.6 / P3-D-RAGC ownership. (MF0-R1h)
10. **Factorial controls + six-way attribution RESTORED — ADOPTED.** New §5.4: all seven parent control families, the six-way contrast ledger, and the two-stage gatekeeping statistics — adopted **by reference to P3-D-THREAT Rev1** (treatment-boundary matrix §3.0, transformed-world validity + counterfactual-following gates §3.0b/§3.4, `T1/T2/T3` split §3.5, `X*` conditionality §3.7, family units §3.8, feedback factor §3.9), with the explicit rule that a ratified THREAT wins any divergence. Adopted-with-modification only in form: the review asked the section be restored in the framework; it is restored as a framework-level contract deferring construction detail to THREAT Rev1 rather than duplicating (and risking forking) its matrix — same normative content, one source of truth. (MF0-R1i)
11. **Decontamination layered + sealed suite powered + inferential gap rule — ADOPTED.** §5.1 rule 9 (disjoint dev/held-out sets, independent paraphrase sources, CIs on recall/FPR, perturbation checks, Min-K diagnostics, derivation-input/source-page screening) plus the benchmark-derived definition of confirmed leakage; §5.2 sizes the sealed suite by power analysis (250/domain demoted to a planning floor) and converts the `.03` gap to one-sided non-inferiority of the difference-in-differences with a CI. (MF0-R1j)
12. **Sardana quarantine — ADOPTED.** §4: qualitative context only; no dollar/model/token figure may enter KOT-LIFE until the direct PDF read reconciles the conflicting examples. (Noted: the rc0 draft contained no such figures; the rule now prevents their introduction.) (MF0-R1l)

No Part-B edit is rebutted. **Part C is NOT applied** (deferred placeholder above). Part-A observations not covered by the Part-B list (e.g. the Offline batch-shopping cell, construct-map freezing, base-image allowlisting, out-of-family calibration subject, per-rung calibration census scope) remain OPEN for the re-review and are not silently resolved here.

## PROPOSED prereg rows (labels only — nothing registered)

All rows are PROPOSED only — nothing is registered, frozen, or scheduled; no `ASM-<number>` ids are minted here (those are assigned at prereg-freeze). Labels are `MF0-`prefixed, disjoint from the sibling `THR-`/`R1`/`VL-R1`/`GU-R1` conventions.

- **PROPOSED-PREREG-ROW-MF0-R1a:** W1 = scalar LCB-margin superiority AND simultaneous per-domain one-sided non-inferiority (margin \(\delta_{NI}\)) against the preregistered domain frontier, in one predeclared multiplicity family; the metric vector is the primary descriptive object. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1b:** scalar inclusion floor = `LCB95(raw_score − chance) > f` on the rung anchor (demonstrated discrimination); the UCB exclusion rule is withdrawn; per-rung floor census before architecture outputs. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1c:** proxy-rung asymmetry — R0/R1 kills may terminate; positive R0/R1 margins are hypotheses only; byte-identical prompts/scorers/formats across rungs. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1d:** energy boundary law — first-class boundary records; `MEASURED-WALL`/`UNMEASURED`/`UNPROVEN` states; "total energy" reserved for wall-class measurement; wall measurement or amended named component-energy budget, no third path. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1e:** load/repeatability law — frozen goodput SLOs, full issued/completed/timed-out/dropped accounting, drift bounds, rank-based CIs in own units, adaptive-N stopping rule, repeatability gate on every campaign arm and comparator. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1f:** KOT-LIFE subledger law — build/mint, review/provenance, staleness-refresh subledgers + uncertainty; \(TCO(q,t)\); matched external-context refresh baseline. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1g:** twin law — from-scratch twins matched on a full FLOP ledger with IsoFLOP/Porian placement, paired seeds, µP sweep, optimizer/interface audit, equal-tuning-budget fallback; released anchors are pinned comparators, never twins. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1h:** matched-RAG completion law — three-rendering information parity, BM25+dense+native cells, recall/provenance, position-shuffle, random-document, popularity strata, frozen order, pinned standard harness, identical ledgers. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1i:** attribution law — the seven parent control families + six-way contrast ledger are mandatory for every W1 claim, instantiated per P3-D-THREAT Rev1 (boundary matrix, validity/following gates, `T`-split, `X*` conditionality, family units, feedback factor), under two-stage gatekept max-t statistics; ratified THREAT prevails on divergence. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1j:** decontamination/seal law — layered screening with disjoint dev/validation sets and CI-reported operating points; benchmark-derived definition of confirmed leakage; power-sized sealed suite; sealed consistency as one-sided non-inferiority of the difference-in-differences. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1k:** secondary-ceiling law — preregistered metric-specific absolute ceilings (anchor-derived, pre-S, with stated headroom) or an explicitly Pareto-extended \(B_k\); the 3×-strongest-comparator rule is withdrawn; all coordinates co-reported. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-MF0-R1l:** Sardana quarantine — qualitative context only; no specific saving/model/token figure enters KOT-LIFE before the direct-PDF reconciliation. `[STIPULATED]`

## MANDATORY self-check (Revision 1)

1. **All 12 Part-B edits applied?** YES — itemised above with section anchors: #1 §0/§6.2, #2 §1.3, #3 §1.1/§1.4, #4 §1.6, #5 §3.1a/§3.1/§3.2/§7.3, #6 §3.3/§3.5, #7 §4, #8 §5.3(7), #9 §5.3(5), #10 §5.4, #11 §5.1/§5.2, #12 §4.
2. **Floor rule now LCB-based?** YES — §1.4 requires `LCB95(raw_score − chance) > f` for scalar inclusion and explicitly withdraws the backward UCB exclusion rule.
3. **Energy boundary uses UNMEASURED/UNPROVEN with no "total energy" misnomer?** YES — §3.1a defines the boundary record, `system_energy_status ∈ {MEASURED-WALL, UNMEASURED}`, the `UNPROVEN` movement rule, and prohibits naming component sums "total energy"; §3.1, §3.2 and §7.3 use component-named energy language.
4. **3× endogenous ceilings replaced?** YES — §3.1 withdraws the 3× rule with the review's full rationale and substitutes preregistered metric-specific absolute ceilings or an explicitly Pareto-extended \(B_k\) (MF0-R1k), ratification-register item 11 updated.
5. **Factorial-control + six-way attribution section restored and consistent with P3-D-THREAT Rev1?** YES — §5.4 restores all seven parent §2.2 families and the parent §2.3 six-way ledger, adopts THREAT Rev1's §3.0 boundary matrix, §3.0b/§3.4 gates, `T`-split, `X*` conditionality, family units, feedback factor, and §5.1 gatekeeping by reference, and rules that a ratified THREAT prevails on any divergence — no contradiction of its treatment-boundary matrix, `G-*` gates, or `X*`-conditional structure introduced.
6. **Part C NOT designed?** YES — the "## Part C — correctness instrument — DEFERRED pending #57" section is a placeholder only: it states the gap, the a/b/c options, the deferral to the maintainer/#57, and the freeze-blocker status; no endpoint definitions, challenge sets, gates, or margins are designed; §1.2 correctness columns remain diagnostic.
7. **Every load-bearing claim tagged?** YES — new literature-dependent choices carry `[LIT-BACKED: reports/lit-p3-*.md §…]` with resolvable report/section backing; every new design choice carries `[STIPULATED]` (or `[STIPULATED — coordinator/Fable to ratify]`); no `[MEASURED]` misuse introduced (this revision adds no measured facts); `[EXTRAPOLATION]` deliberately unused; the draft's `[SV]` markers retained.
8. **No @handle/account strings?** YES — checked; none present in the revised file.
9. **No `ASM-<number>` ids minted?** YES — only `PROPOSED-PREREG-ROW-MF0-R1a…l` labels; the PROPOSED-rows section states ids are assigned at prereg-freeze.
10. **Nothing committed/registered/frozen/run?** YES — this file was edited in place only; no git operations, no registry/bead changes, no goldens, no schedules, no runs; the banner, status block, and Part-C section all state NOT freeze-ready with re-review + Fable critique + the #57/Part-C decisions pending.

No preregistration, bead, registry entry, or frozen object was created by this revision; this design file was edited in place only.