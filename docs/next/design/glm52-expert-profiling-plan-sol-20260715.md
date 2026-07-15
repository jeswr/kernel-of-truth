## Executive verdict

[ASSESSMENT] Full GLM-5.2 profiling is technically plausible on a non-AWS Modal worker using the existing colibri int4 estate and CPU expert streaming. It does not require a GPU. It is not yet operationally proven because colibri requires fast local NVMe-like random reads; a mounted network volume would recreate the failed 9p condition. The make-or-break experiment is therefore a capped `<$3` Modal smoke test using local ephemeral SSD.

[ASSESSMENT] The preferred path is:

1. `$0` inventory, corpus, instrumentation, and backend audit.
2. Modal Function forced onto GCP or OCI, 4 physical cores, 64 GiB RAM, 600 GiB ephemeral SSD.
3. Stage the public preconverted 370 GB colibri int4 estate directly onto ephemeral storage, benchmark it, then run 12 traced prefills.
4. Proceed to a 480-item GLM-5.2 profiling wave only if throughput, trace integrity, and projected cost pass.

If this fails, the best methodology proxy is trained GLM-4.7-Flash: approximately 30B total/3B active, 47 layers, 64 routed experts, top-4, and the same broad sigmoid/no-auxiliary MoE router family. It is useful for building and validating the profiling/replacement machinery, but its expert identities and specialisations cannot be transferred to GLM-5.2. The tiny 0.8B GLM-5.2-shaped checkpoint is suitable only for instrumentation tests because it was trained on a toy corpus. [GLM-4.7-Flash architecture](https://huggingface.co/docs/transformers/model_doc/glm4_moe_lite), [tiny GLM-5.2-shaped checkpoint](https://huggingface.co/inference-optimization/GLM-5.2-0.8B-A0.8B).

---

## Stage 1 — Backend-feasibility gate

### What

Determine whether the full colibri int4 GLM-5.2 estate can be staged, instrumented, and run on a genuinely non-AWS worker within available credits. Do this before expanding the corpus or designing expensive ablations.

Also resolve what “all experts” means in the weight estate. The committed traces expose 76 layer indices, 3–78, each with 256 expert IDs: 19,456 addressable cells. Current colibri documentation describes 21,504 stored routed experts when the MTP estate is included. [MEASURED] These counts must be reconciled rather than silently treating the traced 19,456 cells as the complete disk inventory. The inventory should distinguish:

- Main-model experts: ordinary generation layers.
- MTP-only experts.
- Stored expert tensors not reachable in the selected `DRAFT=0` execution mode.
- Shared experts, which are not part of the routed-expert replacement population.
- Any converter/container duplication.

### Method

#### 1. `$0` static audit

Produce a machine-readable expert ledger from config and safetensors/container metadata, without reading 370 GB of tensor payload:

`execution_site, main_or_mtp, layer, expert_id, tensor_names, shard, byte_offset/size, dtype, weight_hash_if_available, reachable_mode`

Audit the three accounts for:

- Current credit balance and expiry.
- Ability to force a non-AWS physical cloud.
- Maximum local ephemeral disk.
- CPU architecture and AVX2 availability.
- RAM limit.
- maximum job duration;
- storage and transfer charges.
- Whether custom C code can be compiled and patched.

#### 2. Modal smoke test — preferred

Use a standard Modal Function, not a higher-priced interactive Sandbox:

- `cloud="gcp"` or `cloud="oci"`; fail closed if scheduling reports AWS.
- 4 physical CPU cores.
- 64 GiB RAM.
- 600 GiB ephemeral SSD.
- 24-hour timeout.
- Colibri pinned first to the repository’s existing commit; port only the trace patch needed here.
- Download the existing preconverted int4 estate directly into ephemeral storage. Do not run colibri against a Modal Volume mount.
- Hash the model manifest after staging.
- Run `lscpu`, the colibri architecture self-test, and its 19 MB random-read benchmark.
- Run 12 short teacher-forced probes spanning code, math, Chinese, JSON, prose, and copy.
- Emit direct per-item/per-token traces; verify that no result is session-cumulative.

Modal’s default ephemeral quota is 512 GiB and can be raised to 3 TiB; Functions may run for up to 24 hours. Standard Function pricing is currently approximately $0.0472 per physical-core-hour and $0.0080 per GiB-hour. Thus 4 cores plus 64 GiB is about `$0.70/hour` before any location premium; budget `$1.05–1.23/hour` if a 1.5–1.75× provider/location premium applies. Persistent Volume storage would add roughly `$33–36/month` for the estate, so omit it from the smoke and first profiling wave. [Modal resource limits](https://modal.com/docs/guide/resources), [timeouts](https://modal.com/docs/guide/timeouts), [pricing](https://modal.com/pricing).

[ESTIMATE] Staging, benchmarking, and 12 probes should cost `<$3`. The existing 100-second-per-prefill planning assumption would put a 480-item wave at about 13.3 compute hours, or roughly `$9–17` depending on placement premium, plus staging.

#### 3. Measured go/no-go criteria

Declare `GO-FULL-GLM52` only if all of the following hold:

- The model manifest and expert ledger reconcile every stored expert tensor with an execution site or an explicit unreachable designation.
- AVX2/OpenMP tests pass.
- At least 400 GB remains free after staging and temporary download files are removed.
- Parallel 19 MB random reads from ephemeral storage reach at least 1 GB/s. This is the approximate disk regime in which colibri reports 0.05–0.1 cold tok/s; network/9p mounts are forbidden. [Colibri requirements and measured disk regime](https://github.com/JustVugg/colibri).
- RSS stays below 60 GiB.
- Twelve of twelve probes complete.
- Router traces contain exactly the expected top-k selections per main-model token/layer, with valid scores and no cumulative carry-over.
- Repeating two probes gives byte-identical trace decisions under the frozen deterministic settings.
- Measured throughput projects the 480-item Stage 2 wave below 20 hours and below a `$25` stop-loss.

If disk bandwidth misses the threshold, trace integrity fails, or the cost projection exceeds the actual credit cap, declare `NO-GO-FULL-GLM52` and do not scale the run.

### Other backend options

| Backend | Feasibility assessment | Cost/constraint |
|---|---|---|
| Modal | Best full-model candidate. Adequate disk quota, configurable CPU/RAM, custom build, provider selection. Local-disk performance remains unmeasured. | `<$3` smoke; roughly `$9–17` per 480 prefills under the current 100 s estimate. |
| Lightning | Technically possible only if an existing plan exposes ≥64 GiB RAM and ≥500 GB fast local disk. Free and Pro persistent-storage limits are 50 GB and 200 GB; the 2 TB tier is materially more expensive. | Storage is the blocker at cheap tiers. Drive storage above the free allowance is $0.10/GB/month. [Lightning pricing](https://lightning.ai/pricing), [billing](https://lightning.ai/docs/overview/faq/billing). |
| Anyscale | A head-only Google Cloud cluster with local NVMe can support the workload, but setup and platform overhead add no value to a single-process C engine. Serverless Google Cloud and custom storage can require support enablement. | Use only if suitable Anyscale and Google Cloud credits already exist. [Anyscale local storage](https://docs.anyscale.com/storage/local), [cloud options](https://docs.anyscale.com/clouds). |
| CPU-only existing data | Immediately available for offline routing analysis, but cannot reveal expert outputs or support causal replacement tests. | `$0`; useful only as a prior and dry run. |
| GLM-4.7-Flash proxy | Best trained proxy if full GLM fails. Instrument standard inference on one L4/A10-class GPU, preferably int4. Similar MoE family but different model, scale, layers, expert count, and top-k. | [ESTIMATE] 3–10 L4 hours, about `$2.40–8` GPU cost on Modal, plus CPU/RAM. |
| Tiny GLM-5.2 proxy | Preserves the broad code path and DSA architecture shape, but has only eight experts and toy-corpus specialisation. | `$0–2`; instrumentation/unit tests only. |

### Existing public cost-saving opportunity

A current colibri “Expert Atlas” effort proposes exactly the category-by-category `.coli_usage` differencing approach and intends to publish raw activation spectra. Import those raw diffs if they appear, but only after checking model hash, tokenizer, prompt bytes, execution mode, and whether data are per-item rather than category-aggregated. They can provide free cross-validation, not causal evidence. [GLM-5.2 Expert Atlas proposal](https://github.com/JustVugg/colibri/issues/175).

### Decision gate

- `GO-FULL-GLM52`: continue Stages 2–5 on full colibri GLM-5.2.
- `PROXY-ONLY`: run Stages 2–5 on GLM-4.7-Flash to validate methodology, while marking every expert conclusion proxy-scoped.
- `OFFLINE-ONLY`: if neither backend works, produce only the inventory and routing-prior atlas. This does not satisfy the original GLM-5.2 characterisation goal.

---

## Stage 2 — Expert enumeration and activation profiling

### What

Create a complete row for every stored routed expert, while allowing honest labels such as `unseen`, `rare`, `generalist`, `polysemantic`, and `unresolved`. “Enumerate all” must not become “invent a speciality for all.”

Primary output:

`expert_atlas.parquet` plus a compact JSON index, keyed by `(execution_site, layer, expert_id)`.

Each row should eventually contain:

- Main/MTP status and weight location.
- Total routed tokens and weighted routing mass.
- Fraction of tokens selecting it.
- Router-rank and router-margin distributions.
- Domain, operation, language, format, and token-role enrichments.
- Top activation-max contexts.
- Co-activation community.
- Local contribution statistics.
- Causal ablation statistics where collected.
- Hierarchical expertise label and confidence.
- Candidate deterministic module, replaceability score, and evidence level.

### Probe corpus

Use a 480-item Wave A:

- 12 macrodomains.
- Four subdomains or operations per macro-domain.
- Five base items per cell: 240 base items.
- One controlled counterpart per item: 480 total.

Recommended macrodomains:

1. Code and program transformation.
2. Arithmetic, algebra, geometry, and probability.
3. Formal logic and symbolic manipulation.
4. Factual/entity-relation completion.
5. Science and technical exposition.
6. Legal and financial language.
7. Narrative and general prose.
8. Multilingual content, with English and Chinese mandatory.
9. JSON, XML, CSV, Markdown, tables, and whitespace.
10. Copy, repetition, induction, and long-range reference.
11. Tool/function schemas and closed-class choices.
12. Dialogue, instructions, classification, and short-form answers.

Give every item orthogonal labels rather than one exclusive topic:

`semantic_domain, operation, language, surface_format, prompt_or_target, token_role, answer_type, template_family`

Controlled counterparts should vary one axis at a time: same semantics/different format, same surface/different sense, translation pairs, changed numbers with the same wording, code versus prose descriptions, or valid versus near-valid structured output.

Use fixed teacher-forced targets for the primary matrix. Free generation adds a confound because different model outputs expose different future routing. Naturalistic generation can be a secondary corpus after the teacher-forced map is stable. Split by template family, never by individual token, into discovery/dev/held-out sets.

### Required colibri trace

Instrument at the router before batch-union or disk caching:

- Item ID, token position, input versus target token.
- Execution site and layer.
- Selected expert IDs.
- Pre-normalisation router score, normalised weight, and rank.
- Top-k/top-(k+1) margin.
- Expert contribution norm and total MoE-output norm.
- Cache tier and bytes loaded as systems fields, kept separate from routing.
- Frozen mode flags.

Log all 256 router scores only for a fixed 1/16 sample of token-layer positions; selected experts and margins suffice on the full corpus.

Maintain a small per-expert reservoir of routed examples. Eight fp16 input/output pairs per expert would be roughly 4 GB for 19,456 expert cells and is feasible; begin with four and expand only for shortlisted experts.

Freeze:

- `DRAFT=0` for the main-model atlas.
- Sampling off.
- Fixed prompt template/tokenizer.
- Fixed single-token versus batched-prefill mode.
- No adaptive expert pinning that could alter execution.
- A separate MTP sweep if MTP expert characterisation is required.

### Activation matrix

For expert cell \(e=(\ell,i)\) and domain \(d\), compute:

\[
M_{e,d} =
\frac{\sum_{t\in d} 1[e\in TopK(t)]\,w_e(t)}
{\sum_{t\in d}\sum_{j\in TopK(t)} w_j(t)}
\]

Normalize within layer, then report:

- Raw selected-token fraction.
- Weighted routing mass.
- Smoothed log enrichment relative to the expert’s layer-specific base rate.
- Bootstrap confidence interval, resampling prompt families.
- Conditional matrices by language, operation, and surface format.
- Co-activation mutual information and expert communities.

Do not compare raw counts across layers without normalization: every token visits every MoE layer, and layer-specific routing distributions differ.

### What existing artifacts already establish

- [MEASURED] The corrected committed data recover 23 independent fingerprints by first-differencing. They contain 15,850 ever-active cells; 2,027 cells appear in every recovered fingerprint and carry 41.78% of the clean mass. Concept-shaped routing remains real at permutation \(p=0.0001\). [Contamination correction](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/CONTAMINATION-NOTE.md:1).
- [MEASURED] The original 24 STATS files are session-cumulative. `f000` cannot be recovered, so they cannot be treated as 24 independent fingerprints.
- [MEASURED] R4 finds a substantial same-prompt routing oracle, about 19.8% relative miss-mass reduction, but only 2.6% for the thin kernel-conditioned map versus global-hot. This says more prompt-level structure exists than the eight-concept map captures; it is not a functional label for individual experts. [R4 replay](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/r4/r4-replay.md:1).
- [MEASURED] LOOKA produced `0/0`, so it currently provides no routing-predictability evidence.
- [MEASURED] TOPK provides system-level expert-load counters and the preliminary speed lever: 8→4 was about 1.9× and 8→2 about 2.5× in one confounded sweep. It does not say what any expert does. [Probe log](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/results/probe-main.log:1).
- STATS can supply aggregate category affinity after correct differencing. It lacks token identity, router score, expert output, and causal information.

### Coverage and decision gate

After Wave A:

- Trace invariants must pass on 100% of items.
- At least 95% of observed routing mass must belong to experts with ≥100 routed events.
- A stable label requires ≥100 events across ≥20 prompt families; otherwise mark the cell rare/unresolved.
- Discovery-versus-held-out domain matrices should have Spearman correlation ≥0.8 at the layer level.
- Top-domain identity should reproduce in at least 70% of prompt-family bootstraps.
- Inventory coverage must report both expert-cell coverage and routed-mass coverage.

If mass coverage passes but many rare cells remain unseen, retain them as enumerated/unresolved rather than spending disproportionately to force activations. Add targeted prompts only for rare experts with high router scores or high projected system value.

[ESTIMATE] Wave A costs roughly `$9–17` on full Modal GLM-5.2. A second held-out 480-item wave is another `$9–17`. Corpus construction and all post-processing are `$0` local work.

---

## Stage 3 — Specialisation characterisation

### What

Infer what each expert contributes, not merely what inputs route to it. Router affinity is evidence about the gate; it is not by itself evidence about the expert function.

Use four independent evidence channels.

### 1. Activation-max contexts and controlled contrasts

For each expert, retain the highest normalized router-score examples after correcting for the layer base rate. Present short surrounding contexts, token role, and labels.

Use minimal pairs to distinguish:

- Semantic versus lexical triggers.
- Format versus content.
- Language versus topic.
- Position or punctuation effects.
- Number presence versus arithmetic operation.
- Copy structure versus repeated vocabulary.

An expert whose apparent “finance” affinity disappears when lexical tokens are controlled should receive a lexical/closed-class label, not a finance-reasoning label.

### 2. Local functional signatures

From the per-expert reservoirs:

- Input and output norms.
- Cosine between weighted expert contribution and the total MoE output.
- Sensitivity to matched input changes.
- Output clustering across domains.
- Similarity to other experts in the same layer.
- Whether the expert behaves like a near-duplicate of another expert.

Recapture full hidden/input-output pairs only for shortlisted experts; scalar and compact sketches suffice for the all-expert census.

### 3. Causal ablation and output-logit attribution

Exact individual ablation of all 19,000-plus cells is infeasible. Use a two-tier design:

- All experts receive routing and local-contribution evidence.
- A stratified shortlist of approximately 32 experts receives exact causal tests: high-specialisation, high-load, format/copy/arithmetic candidates, apparent generalists, and negative controls.

For each shortlisted expert:

1. Baseline forward.
2. Contribution ablation: leave router weights unchanged but replace that expert’s contribution with zero.
3. Route-around ablation: exclude it and renormalize remaining selected experts.
4. For later replacement candidates, module-swap forward.

Measure paired change in:

- Target-token NLL.
- Gold-token logit margin.
- Next-token KL divergence.
- Exact task correctness.
- Downstream effects by domain and token role.

Use 16–32 activation-max items plus matched off-domain controls per expert. Measure at final logits rather than relying on an intermediate “logit lens.”

Balanced multi-expert knockouts may screen larger groups, but they are not substitutes for the single-expert causal tests because interaction effects are expected.

### 4. Weight-structure signatures

Stream through the int4 estate once and compute:

- Per-matrix and per-channel norms/scales.
- Randomized low-rank spectral sketches.
- Effective-rank proxy.
- Quantization saturation.
- Router-vector similarity.
- Expert-to-expert weight-sketch similarity within each layer.
- Nearest-neighbour or duplicate clusters.

These signatures are weak semantic evidence, but useful for identifying redundancy, outliers, and groups likely to admit the same replacement.

### Expertise label and confidence

Use hierarchical, multi-label output:

`primary_area`, `secondary_areas`, `operation`, `surface_trigger`, `generalist/polysemantic/unresolved`

A concrete confidence score is:

\[
C_e = 0.25\,Coverage +
      0.25\,SplitStability +
      0.25\,EvidenceAgreement +
      0.25\,LabelMargin
\]

Each component is scaled to \([0,1]\):

- `Coverage`: routed events and prompt-family diversity.
- `SplitStability`: held-out and bootstrap reproducibility.
- `EvidenceAgreement`: agreement among routing, activation maxima, local output, and causal ablation.
- `LabelMargin`: separation of the first and second labels.

Report the conservative bootstrap lower bound:

- High confidence: lower bound ≥0.80.
- Medium: 0.50–0.80.
- Low: <0.50.
- Unresolved: insufficient coverage or contradictory channels.

A speciality label should normally require held-out enrichment whose lower confidence bound is above zero and at least one functional channel pointing in the same direction. Otherwise publish the routing association explicitly as such.

### Decision gate

Proceed to replaceability scoring only for an expert or expert cohort when:

- The label is at least medium-confidence.
- It reproduces on held-out prompt families.
- Causal harm is either narrow and interpretable or demonstrably redundant.
- The apparent function is not solely a lexical artifact unless the proposed replacement is itself lexical.
- The cohort is coherent enough that one deterministic module could plausibly handle it.

[ESTIMATE] Matrix analysis, context extraction, and weight summaries are `$0` after traces are downloaded. A 32-expert causal wave of roughly 1,000–2,000 additional prefills is about `$20–55` in full-model CPU credits. No GPU is required.

---

## Stage 4 — Deterministic replaceability analysis

### Plausible candidate classes

| Expert pattern | Natural deterministic replacement | Kernel/sparq fit |
|---|---|---|
| JSON/XML/CSV delimiters, whitespace, Markdown structure | DFA/grammar, schema-driven emitter, parser | No; plain deterministic module |
| Exact arithmetic, unit conversion, date calculation | Parser plus integer/rational/unit evaluator | Usually no; sparq is relevant only when semantic unit/type knowledge matters |
| Copy, repetition, induction, recent-span continuation | Rolling hash, suffix/prefix index, KV pointer, deterministic n-gram | No |
| Closed-class selections, enum/schema fields, tool names | Trie/table/rule router | No |
| Entity/relation lookup with stable semantic keys | Versioned key-value or relation store | Kernel/sparq is natural when concept identity, provenance, typing, or inference is part of the task |
| Sparse taxonomic or rule-based reasoning | Deterministic reasoner | Kernel/sparq is natural |
| Code syntax or schema validation | Parser/type/schema checker | Usually plain deterministic |
| Broad prose, nuanced translation, open-ended synthesis, distributed reasoning | No credible deterministic substitute at this stage | Learned/diffuse; do not prototype |

A domain-enriched expert is not automatically replaceable. For example, a “math” expert may implement distributed representation transformations rather than arithmetic. Conversely, a low-entropy punctuation expert may be trivially predictable yet causally essential to the residual computation. Both routing and causal evidence are required.

### Replaceability score

Score each expert–module pair, not just each expert:

\[
R_{e,m} = 100 \times Q_{0.10}
\left[
0.20G + 0.30F + 0.20C + 0.15S + 0.15I
\right]
\]

where \(Q_{0.10}\) is the prompt-family bootstrap tenth percentile:

- `G — Gateability`: can a cheap deterministic trigger decide when the module should act?
- `F — Fidelity`: how closely does the module swap preserve expert-local output or, preferably, final logits and correctness?
- `C — Causal containment`: is the expert’s measured importance concentrated on the module’s covered operation?
- `S — Stability`: does the characterization survive phrasing, language, seed, and held-out templates?
- `I — Noninterference/redundancy`: is off-domain behaviour unchanged, and can remaining experts absorb uncovered cases?

Evidence caps prevent routing-only candidates from receiving misleading scores:

- Level 0 — routing affinity only: maximum score 30.
- Level 1 — routing plus local input/output tests: maximum 55.
- Level 2 — exact causal ablation on dev items: maximum 80.
- Level 3 — locked held-out module-swap validation: maximum 100.

Keep system value separate:

\[
Priority_{e,m} =
(R_{e,m}/100)\times
MeasuredBytesSaved_{e}\times
ActivationRate_e
\]

This prevents a highly replaceable but almost-unused expert from displacing a slightly harder cohort with real I/O value.

### Cohorts, not only individual cells

A single expert cell is unlikely to remove enough total GLM-5.2 I/O to matter. Form module-specific cohorts across layers, while preserving the per-cell evidence. A cohort advances only if:

- Every included cell has Level-2 evidence.
- Cohort score lower bound is ≥70.
- The proposed trigger is deterministic and held-out.
- Measured trace replay projects a meaningful byte/load reduction, provisionally ≥3% on the target workload.
- Off-target activation is low or the module has a reliable fail-open path to the native expert.

### Decision gate

- `PROTOTYPE`: Level-2 score lower bound ≥70 and projected ≥3% target-workload expert-I/O reduction.
- `CHARACTERISE-MORE`: score 50–70 or uncertainty dominates.
- `DO-NOT-REPLACE`: diffuse causal effects, poor gateability, broad off-domain harm, or no credible deterministic module.
- `DROP-CANDIDATE`: low causal importance and high redundancy; test removal separately from replacement.

Stage 4 is `$0` analysis.

---

## Stage 5 — Replacement prototyping and validation

### Replacement seams

Implement three distinct seams and report which one is being tested:

1. **Literal MoE substitution:** keyed by `(execution_site, layer, expert_id)`. When the expert is selected, skip its disk load and matmul and ask a deterministic module for a 6,144-dimensional contribution. Kernel-derived content carriers or exact copy/pointer transformations are plausible here.

2. **Route-around plus deterministic sidecar:** mask the expert cohort, let remaining experts handle the residual computation, and perform the narrow operation through a deterministic evaluator or lookup sidecar. Suitable for arithmetic, schema fields, or closed-class tasks.

3. **Task-span bypass:** a deterministic module emits an exact span without running the native experts for that span. Suitable for fully forced formatting, exact arithmetic answers, or verbatim copy. A grammar that still executes the full GLM forward does not count as expert replacement; native expert loads must actually disappear.

Every path must fail open to the unmodified native model when its trigger is not certain.

### First prototypes

Select from data rather than preordaining the winner, but predeclare these module families:

- Format/structured-output cohort → parser/DFA/template emitter.
- Arithmetic cohort → expression parser plus exact evaluator.
- Copy/induction cohort → rolling-hash or suffix-index pointer.
- Semantic lookup/rule cohort → kernel/sparq carrier or reasoner.

Start with at most two cohorts. The native colibri implementation should expose:

- Native expert arm.
- Drop-only arm.
- Deterministic replacement arm.
- Compute-matched uniform TOPK control.
- Wrong-table or deranged-key control for any content-bearing lookup module.

### Matched-quality endpoint

Use a joint quality gate, not “no significant difference”:

- Target exact accuracy: paired non-inferiority, with the dev-selected margin capped at one absolute percentage point.
- Off-target exact accuracy: same one-point cap.
- Teacher-forced NLL: upper 95% confidence bound on replacement-minus-native ≤0.02 nats/token.
- No preregistered domain subgroup may regress by more than two points.
- Deterministic parser/evaluator unit corpus must be 100% correct before model evaluation.
- Structured-output candidates must not increase invalid-output rate.

The pilot estimates discordance and determines the required paired sample size before test freeze. If the available credits cannot power the selected margin, report `UNDERPOWERED` and do not call the replacement quality-neutral.

### Systems endpoint

Run randomized blocked repetitions under two regimes:

- Cold/local-SSD cache.
- Fixed warm/pinned cache.

Freeze prompt bytes, output length, `DRAFT=0`, thread count, and CPU placement. Report:

- Expert loads/token.
- Expert bytes read/token.
- Expert-matmul time.
- Module time.
- Prefill and decode wall time.
- Trigger rate.
- End-to-end speed at matched quality.

A replacement passes only if the quality gate passes and the lower confidence bound on end-to-end speed improvement is positive. Cache-specific speedups must not be generalized to other regimes.

### Pre-registration discipline

Before touching held-out data, hash and freeze:

- Model/container and colibri commits.
- Expert cohort.
- Trigger and fail-open rule.
- Module implementation and data tables.
- Corpus item IDs and template-family split.
- Primary and secondary endpoints.
- Quality margins and power calculation.
- Baselines and controls.
- Cache regimes and run order.
- Cost and wall-clock stop-loss.
- Missing-data and interruption handling.
- Exact positive, negative, underpowered, and instrument-invalid wording.

Candidate selection and threshold tuning occur on discovery/dev only. The held-out set is evaluated once. A failed candidate remains in the atlas at equal prominence; it is not replaced post hoc by a nearby expert or easier subgroup.

[ESTIMATE] A single 300-target/300-off-target campaign with native, drop, replacement, and uniform controls is approximately 2,400 prefills. At 100 seconds each this is about 67 instance-hours, roughly `$40–82` depending on Modal placement and measured throughput. Smaller pilot campaigns should precede this. No GPU is required on the full colibri path.

---

## Cost summary

| Work | `$0` work | Paid work |
|---|---|---|
| Stage 1 | Account/resource audit, exact expert inventory, container and patch design | Modal smoke `<$3`; optional persistent model storage `$33–36/month` |
| Stage 2 | Corpus, schema, trace parser, analysis dry run on existing fingerprints | Full GLM Wave A `$9–17`; held-out expansion another `$9–17` |
| Stage 3 | Activation matrix, labels, weight summaries after traces exist | Causal shortlist roughly `$20–55` CPU |
| Stage 4 | Replaceability scoring and cohort selection | None |
| Stage 5 | Preregistration, deterministic module/unit tests | Roughly `$40–82` CPU per powered full-model cohort |
| Proxy fallback | Tiny-checkpoint instrumentation can be nearly `$0` | GLM-4.7-Flash: approximately `$2.40–8` of L4 GPU time for a profiling build-out |

[ASSESSMENT] No stage intrinsically needs a GPU if the Modal colibri path passes. GPU credits are only a fallback for the smaller trained proxy.

---

## Relationship to `glm-edrop-0`

This work should run alongside and extend `glm-edrop-0`, not silently supersede it.

`glm-edrop-0` asks whether kernel-guided candidate masks preserve quality better than uniform TOPK and other mask controls at matched expert compute. It does not identify expert function or build deterministic substitutes. Its uniform TOPK arm remains the required kernel-free baseline. [Existing design](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-expert-drop.md:231), [registry record](/home/ec2-user/css/kernel/kernel-of-truth/registry/experiments/glm-edrop-0.json:1).

The new atlas contributes:

- Correct per-item/per-token traces instead of cumulative STATS.
- A reconciled all-expert inventory.
- Stable domain/operation labels.
- Causal evidence for particular expert cells.
- Candidate-specific deterministic modules.
- Better frequency/topic/redundancy masks for a future `glm-edrop-1`.
- Replacement arms that test quality-neutral speed, not just expert removal.

Before `glm-edrop-0` freezes, it still needs its documented v2→v3 contamination amendment. Do not alter a frozen `glm-edrop-0` mask using new atlas results. If the atlas arrives after freeze, treat it as successor evidence and retain `glm-edrop-0` unchanged. Replacement validation should reuse its DROP sidecar, load counters, item-level scoring, and uniform-TOPK control wherever possible.

---

## First three coordinator-dispatchable steps

1. **`$0` expert/backend audit.** Build the exact stored-expert ledger, inspect actual Modal/Lightning/Anyscale balances and limits, and emit a one-page feasibility manifest with the Modal GCP/OCI configuration and `$25` Wave-A stop-loss.

2. **Trace patch plus tiny-model validation.** Add direct per-token router records, scores, contribution norms, execution-site identity, and per-expert reservoirs. Prove on the tiny GLM-5.2-shaped checkpoint that traces reset per item, top-k invariants hold, and main versus MTP experts are disambiguated.

3. **Freeze Wave-A corpus, then run the `<$3` Modal smoke.** Materialize the 480-item labelled/matched corpus and analysis schema at `$0`; only then stage full colibri int4 onto ephemeral SSD and execute the 12-probe backend gate. The measured disk and prefill results decide whether the coordinator dispatches the full 480-item wave.