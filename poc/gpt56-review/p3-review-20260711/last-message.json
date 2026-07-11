## Overall judgement

The programme is intellectually serious, unusually candid about its weak evidence base, and worth continuing—but the current design should be revised before it is frozen or converted into experiment beads.

The architecture literature reviews can begin now. The measurement framework, dependency graph, and several falsifiers should be redesigned first. As written, a W1 “win” could be statistically real yet still depend on resource-band gaming, a narrow and correlated benchmark index, unmatched lifecycle investment, or an inadequately strong neural/RAG baseline.

## 1. Measurement and fair comparison

### What is strong

The framework in [§1–2](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:96>) gets several important things right:

- It measures the whole deployed system, not just neural parameters.
- It freezes stores and indices and includes them in the artifact.
- It evaluates natural benchmark inputs rather than hand-formalized versions.
- It requires own-harness baselines, full score vectors, abstention reporting, decontamination, and aligned-store controls.
- It separates the competitive system claim from kernel-specific attribution.
- It proposes calibration on neural models before using the instrument.

Those are substantive strengths, not cosmetic safeguards.

### The ±10% matching rule is gameable

Bilateral ±10% bands are not the right primary comparison. They permit:

- Padding an artifact to enter a more favorable model band.
- Avoiding a strong model just outside the band.
- Having no credible comparator in the intersection of size and compute bands.
- Calling a system competitive when a smaller or cheaper neural system already dominates it.

Replace bands with a resource-constrained frontier:

> At resource budget `(maximum deployment bytes, maximum latency/energy/memory)`, compare S against the best neural or neural-retrieval system that fits within every budget.

The comparator should be allowed to be smaller or cheaper, not merely within ±10%. Report interpolation or a staircase envelope across neural Pareto points. W1 should mean that S lies significantly above the best baseline capability frontier, not that it won a favorable neighborhood.

The claim should also be narrowed from “all other models” to “all pre-registered, reproducible open comparators and baseline families searched under the specified budget.” The literal universal claim is not testable.

### “Same compute” is underspecified and partly mislabeled

KOT-COST/1’s neural-FLOP ledger assigns symbolic work zero. That can be a useful diagnostic—“neural FLOPs”—but it is not a compute ledger. A system performing substantial CPU search, retrieval, decompression, or I/O can appear compute-matched there by definition.

Use a resource vector:

- accelerator time and estimated operations;
- CPU-seconds;
- bytes read from storage and network;
- energy;
- peak GPU memory and host RSS;
- end-to-end latency;
- throughput under a fixed concurrency distribution.

W1 currently mentions wall-clock and memory but omits the energy constraint even though energy is supposedly part of KOT-COST/1. That inconsistency must be fixed.

Measure both warm- and cold-cache behavior, startup/index-load time, p50/p95 latency, throughput, time to first token, and inter-token latency. Output length must be controlled or cost normalized appropriately. MLPerf uses explicit latency, throughput, compliance, and full-system power methodology for exactly these reasons; the programme should borrow that measurement discipline rather than relying on query-level `nvidia-smi` readings alone. [MLPerf inference methodology](https://mlcommons.org/benchmarks/inference-datacenter/), [MLPerf power measurement](https://docs.mlcommons.org/inference/power/).

### Deployment size is useful, but not sufficient

Raw on-disk bytes are a defensible requested metric, provided packaging is canonical. Otherwise serialization format, padding, duplicate metadata, compression settings, and what gets moved into the “common base image” are gaming surfaces.

Report at least:

1. Canonically packed, minimally sufficient artifact bytes.
2. Compressed distribution bytes.
3. Warm resident RAM/VRAM.
4. Cold-start working set and bytes read.
5. Index/store construction size and cost.
6. Any remote service, cache, or corpus dependency.

Freeze the common base image before architecture development. Otherwise custom functionality can migrate into the supposedly free base.

Most importantly, add a lifecycle ledger. The current design explicitly compares deployment efficiency, not equal total compute. That is legitimate, but it must be named accurately. Report:

- donor pretraining provenance where known;
- architecture fine-tuning and hyperparameter-search compute;
- store authoring, parsing, embedding, indexing, and human-review costs;
- total cost amortized at several deployment volumes, such as \(10^3, 10^6,\) and \(10^9\) queries.

Training longer to obtain a smaller model is a real deployment strategy, and optimal model size depends on expected inference volume. [Sardana et al., “Beyond Chinchilla-Optimal”](https://proceedings.mlr.press/v235/sardana24a.html).

### Baselines need strengthening

The strongest missing control is:

> Same corpus, same retriever/index, same resource budgets, but a conventional neural RAG or tool-use architecture.

The aligned-non-kernel store does not replace this. The programme must distinguish:

- kernel semantics;
- structured storage;
- retrieval;
- deterministic execution;
- retry/search;
- specialized neural-symbolic integration.

Baseline optimization should include quantization, structured pruning, distillation, retrieval, and compute-optimal sampling or verification. Best-of-\(k\) self-consistency alone is too weak: adaptive test-time compute can substantially outperform naive best-of-\(N\). [ICLR 2025 test-time-compute study](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html).

Equal numbers of hyperparameter configurations are also not sufficient symmetry because configurations differ greatly in cost. Match total tuning compute and use fixed selection rules.

### Decontamination is necessary but cannot certify fairness

N-gram and embedding overlap screening can catch gross answer-key leakage, but not:

- benchmark source knowledge encoded as rules or abstractions;
- selective store authoring based on benchmark error analysis;
- paraphrases below the threshold;
- benchmark contamination in donor weights;
- repeated researcher adaptation to the frozen test suite.

Add a sealed evaluation component produced after architecture and store freeze, preferably by an independent party or procedural generator. For store-based systems, include temporally fresh facts or independently held-out domains.

Use a factorial control design: content type × retrieval architecture × executor. Derangement alone is weak because it changes alignment and often retrieval behavior simultaneously. Include label permutation, irrelevant-but-structurally-matched records, edge shuffling, and matched generic RAG.

### Statistical specification needs correction

W1 should require the lower confidence bound on the difference to exceed the practical margin:

\[
LCB_{95}(INDEX(S)-INDEX(B)) > \delta_k
\]

A point estimate above \(\delta_k\) plus an LCB merely above zero does not establish the margin.

Because S is tested against multiple baselines, use simultaneous confidence bounds or family-wise error control. Bootstrap hierarchically across benchmark families and items, preserving paired predictions.

“TOST non-inferiority” is technically incorrect. TOST is normally an equivalence procedure with two one-sided tests. A non-inferiority claim uses the appropriate single one-sided test or confidence bound against the non-inferiority margin.

## The AI index

The current nine-task suite is reasonable for SmolLM2 harness calibration. It is not adequate as the headline “AI-capability index.”

Seven components are closely related multiple-choice commonsense or factual tasks. An unweighted macro-average therefore overweights that construct while underrepresenting:

- language modeling and linguistic competence;
- instruction following;
- natural-language generation;
- compositional and relational generalization;
- logical reasoning;
- calibration and selective prediction;
- multilingual performance;
- coding below R-3;
- robustness under distribution shift.

The raw average also combines binary, four-way, five-way, and open-ended tasks with different chance floors and variances. Normalize scores relative to chance and a pinned ceiling, then macro-average first within capability domains and only then across domains. Publish both the domain vector and the scalar.

MMLU-cloze is particularly problematic: the repository itself notes inconsistent MMLU variants across SmolLM2 sizes. It should not be silently treated as a stable cross-rung component.

Recommended structure:

- **R-0:** held-out language-model loss plus BabyLM-style BLiMP/EWoK linguistic evaluation; small procedural relational and rule-reasoning suites.
- **R-1/R-2 general capability:** a reduced set from HellaSwag, ARC-Challenge, PIQA, WinoGrande, MMLU, GSM8K, plus instruction following where above floor.
- **Neurosymbolic diagnostics:** CLUTRR, ProofWriter/RuleTaker, FOLIO or similar, with held-out rules, relation compositions, proof depths, and lexical paraphrases. CLUTRR explicitly evaluates systematic relational generalization and includes natural-language graph construction, making it especially relevant. [CLUTRR paper](https://arxiv.org/abs/1908.06177).
- **R-3+:** MMLU-Pro, BBH or BBEH where discriminative, IFEval, code, and a frozen release of LiveBench or another recent objective benchmark.
- **Contamination-resistant secondary:** a sealed or periodically refreshed suite. LiveBench is useful because it refreshes questions and uses objective scoring, though its changing nature means each release must be versioned rather than folded silently into a fixed index. [LiveBench](https://github.com/livebench/livebench).

HELM’s multi-scenario, multi-metric structure is a better conceptual model than a flat accuracy average. [Stanford HELM](https://nlp.stanford.edu/helm/vhelm/). The Open LLM Leaderboard v2 suite is suitable at larger scales but the document is right that much of it may floor out at tiny scales. [Official benchmark descriptions](https://huggingface.co/docs/leaderboards/main/open_llm_leaderboard/about).

Keep the current suite as “SmolLM2 continuity index,” not as the sole capability index.

## 2. Architecture bets

### Verifier loop

This is the best-motivated family because it has the only measured system-level positive shape. The proposed index-level falsifier is sensible, provided it compares against:

- compute-optimal neural sampling;
- a learned neural verifier;
- generic structured RAG;
- grammar/constrained decoding;
- the same verifier with a non-kernel store.

Run a coverage upper-bound calculation first:

\[
\Delta_{\text{maximum index}} \leq \sum_b w_b \kappa_b
(1-\text{baseline accuracy on covered items})
\]

If even perfect covered-item correction cannot reach \(\delta\), kill the index-mover claim without GPU work.

### GNN fusion

The hypothesis is plausible, particularly for relational composition and systematic generalization. But “GNN ≤ text serialization” at R-0/R-1 does not kill the entire family. Text is often superior for tiny graphs, while graph encoders may become useful only as graph size and reasoning depth grow.

Controls should include:

- same retrieved nodes with no edges;
- shuffled edges and relation labels;
- MLP/DeepSets/Transformer encoders with the same inputs;
- text serialization at equal information and resource budgets;
- held-out relation compositions and proof depths;
- oracle graph versus NL-extracted graph.

Separate four stages: retrieval, graph construction, graph encoding, and LM use. A positive delivery probe is insufficient; require causal behavioral improvement.

### Rule placement

The cheap-first order CD → KV → adapters/activations → hidden layer is sensible. Several claims need tightening:

- Constrained decoding does not itself perform inference; it enforces an output language unless the external engine has already derived the valid continuation set.
- Attention weights are not adequate provenance evidence. KV provenance requires causal ablation, intervention, or executor traces.
- A dedicated concept bottleneck is not strongly interpretable merely because its units are named. Provenance must be causally validated.
- Cost parity with the external loop should not be the only endpoint. An internal mechanism might be worthwhile if it improves accuracy, coverage, or latency variance. Compare Pareto frontiers.

A promising missing design is explicit NL-to-program synthesis: parse into a small executable DSL, execute deterministically, and generate from the checked result with calibrated abstention. That attacks the actual boundary problem more directly than hoping rule knowledge emerges in a hidden layer.

### Ground-up training

A matched twin is correct, but one R-0 failure should not imply failure at R-2. Interfaces may require enough model capacity to become usable. Run at least three small widths or token budgets and test the direction of scaling.

The most promising training variants missing are:

- distillation from symbolic proof traces;
- verifier-guided training rather than verifier-only retry;
- synthetic curriculum over increasing rule depth and paraphrase diversity;
- learned routing so the symbolic path is activated selectively;
- conditional-compute or MoE designs with a symbolic expert.

### Dimension drop

This is currently the weakest technical component.

An arbitrary per-layer orthogonal rotation is not generally function-preserving through elementwise nonlinearities, normalization, residual connections, attention head structure, and tied embeddings merely because adjacent linear maps are adjusted. Some restricted residual-stream basis changes can be absorbed, but the exact invariance group must be derived for the chosen architecture.

SAE features are typically overcomplete and non-orthogonal; matching them to concepts does not produce a removable orthogonal coordinate block.

Also, dropping 80% of hidden width does not imply a 5× smaller dense transformer. Major matrices scale approximately quadratically with width, so the reduction could be much larger—while embeddings and other components scale differently. Conversely, “dropping 80% of dimensions” could mean rank or parameter pruning, in which case 5× needs an explicit parameterization.

Before the five-arm full experiment, add a cheaper causal gate:

1. Identify a purported concept subspace.
2. Ablate or patch it on concept-relevant and irrelevant tasks.
3. Test stability across layers, prompts, and donors.
4. Show that store reinjection specifically restores the lost behavior.
5. Only then attempt structural width pruning and distillation.

Compare against the strongest retrained structured-pruning and knowledge-distillation baselines, not pruning without recovery training.

## 3. Scaling ladder and cost approach

The cheap-first intent is good, but the ladder should be reorganized around information-gaining gates:

1. **Coverage ceiling:** Can perfect oracle use move the index by \(\delta\)?
2. **Oracle interface:** With gold parses/subgraphs, does the architecture help?
3. **Boundary degradation:** How much survives realistic NL mapping?
4. **Full system:** Does it beat the resource-constrained baseline frontier?
5. **Scaling:** Does the margin improve across at least two sizes?

This kills failures earlier and localizes them. Presently, an architecture can fail because the graph encoder is bad, retrieval is bad, or NL parsing is bad, with no clean diagnosis.

Do not require every experiment, including NLB, to wait for index calibration. NLB and coverage work can proceed independently. Conversely, every store-touching natural-input experiment—not only H-VL—must explicitly depend on NLB or be labeled an oracle/formal diagnostic.

There is also a W2 inconsistency: P3-E-SCALE-2 promises a Pareto sweep, while §4 says W2 begins only after W1. Make the R-2 sweep conditional on W1, or label earlier compression curves diagnostic rather than W2.

## 4. Work breakdown

The broad literature-first structure is good, but add or expand these reviews:

- RAG, structured retrieval, knowledge graphs, and tool-using neural baselines.
- Semantic parsing, program synthesis, grammar induction, uncertainty, and selective prediction.
- Neural theorem proving, differentiable logic, neural algorithmic reasoning, and proof-trace distillation.
- Causal representation analysis and the exact invariances of transformer model surgery.
- Lifecycle cost, systems benchmarking, storage/I/O, and MLPerf-style measurement.
- Benchmark contamination, sealed evaluation, composite-index statistics, and proxy-rung validity.
- Store authoring, maintenance, provenance, and knowledge-update economics.

Missing design tasks include:

- a formal resource/baseline threat model;
- a neural frontier-builder that optimizes baselines under each budget;
- a coverage × maximum-gain power analysis;
- an independent sealed benchmark;
- a matched generic-RAG control;
- oracle-to-NL error decomposition;
- hardware repeatability and cold/warm-cache protocols;
- lifecycle cost amortization.

P3-D-NLB should itself depend on a semantic-parsing/selective-prediction review. The current “no blocker” status risks repeating the already-measured parser failure without first reconsidering the approach.

## 5. Honesty and programme risks

The document is commendably honest about the current evidence. It accurately carries forward the central result from [feasibility synthesis §0–2](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/feasibility-synthesis.md:33>): exact machinery inside a closed grammar, but 47.6% and 41.6% retention across the two NL boundaries, one with dangerous wrong answers, plus extremely low external coverage.

However, it overstates one conclusion in §7.3: the comparison has not yet been shown capable of being “made fair.” It has been made auditable in several respects, but unresolved training-data contamination, lifecycle cost, baseline search, and artifact-band gaming remain.

The natural-language failure is acknowledged rhetorically but not fully encoded in dependencies. GNN retrieval, KV rules, constrained decoding, and H-DD store reinjection all need query-to-symbol grounding. NLB must gate all natural-input store use, or experiments must explicitly use oracle inputs and make no W1 claim.

The programme-level kill is too soft and too subjective. “Analysts attribute misses to fundamentals rather than instrument failure” leaves a wide escape hatch. Pre-register quantitative kills:

- perfect-oracle coverage cannot reach \(\delta\);
- NLB fails safety or minimum precision/recall after a fixed number of redesigns;
- no family exceeds the neural/RAG frontier at R-1 and R-2;
- gains disappear against matched generic stores;
- integration gains do not survive natural input;
- total lifecycle costs are dominated at all plausible deployment volumes.

If none passes W1 at R-2, the default should be terminate the competitiveness programme, with a new proposal required to restart—not an open-ended maintainer fork.

## Ranked concerns

1. **The comparison frontier is wrong.** ±10% size/compute bands are gameable and do not establish dominance over resource-constrained neural and RAG alternatives.
2. **The headline index is too narrow and statistically ill-formed.** It overweights correlated legacy multiple-choice benchmarks and averages incomparable raw scores.
3. **The NL/coverage wall is not enforced in the experiment dependencies.** Several architectures can reach Phase 2 without demonstrating usable query-to-symbol grounding.
4. **H-DD contains unsupported and partly incorrect model-surgery assumptions.** Rotation invariance, semantic axis alignment, store replacement, and the 80%→5× relation all need reformulation.
5. **The baseline and accounting scope is incomplete.** Generic RAG/tool use, optimized test-time compute, store construction, training, and lifecycle economics are not adequately matched.

## Factual or technical errors

- TOST is described as a non-inferiority test; non-inferiority normally uses one one-sided test or CI, while TOST establishes equivalence.
- A point estimate above \(\delta\) with an LCB above zero does not establish a margin-\(\delta\) win.
- Arbitrary per-layer orthogonal rotation is not generally function-preserving in a transformer.
- SAE features do not normally form an orthogonal removable basis.
- Dropping 80% of hidden dimensions does not generically equal a 5× size reduction.
- Attention weights do not provide reliable causal provenance.
- A neural-FLOP ledger in which symbolic computation is zero is not a total-compute measure.
- Constrained decoding is not rule inference unless an executor has already computed the constraints.

## Recommendation

Proceed with the literature reviews, especially evaluation, RAG baselines, semantic parsing, and compression/model surgery. Do not freeze KOT-FAIR/1, bead the current Phase-2 graph, or treat W1 as publication-ready until the resource-frontier comparison, index, lifecycle ledger, sealed evaluation, and NLB dependencies are revised.

The programme is promising enough to investigate, but not methodologically sound enough to execute as currently specified.