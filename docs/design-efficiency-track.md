# Efficiency track (F-series) — does the kernel make models SMALLER or CHEAPER at matched-or-better accuracy?

**Status:** design / pre-registration draft, 2026-07-08. New track, complementary to `poc-design.md`'s E-series: E1–E9 measure *geometry and correctness*; none measures FLOPs, params, or memory. This track exists because the maintainer's directive makes throughput-of-truth an explicit priority: test whether the kernel reduces {model size, inference compute, training compute, memory} while holding or improving {accuracy/correctness}.
**Author:** G1-EFF (Claude Fable 5 design agent), for @jeswr. Coordination: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683).
**Honesty contract:** as in `architecture.md` — claims tagged **[established]** / **[claimed]** / **[open]**; the literature prior is stated *against* the thesis where that is what the record says. Programme rule inherited verbatim: **do not guess which design wins where confidence is low — decide it by experiment, with pre-registered kill criteria.**
**Builds on:** `reports/lit-llm-injection-priorart.md` (Laws 1–3, the text-null mandate, LCM/CALM, InstructRetro absorption, ToolkenGPT), `docs/architecture.md` (A1–A6, §1.3 dimension problem), `docs/poc-design.md` (Common rules, E-series), `docs/design-compact-kernel-serialization-v2.md` (KOTK/2 measured bytes), `reports/deterministic-concept-vectors.md` (capacity arithmetic), `poc/e5` + `poc/e9` verdicts (the one PASSed injection instrument this track can reuse).

---

## 0. Executive summary

1. Six falsifiable mechanisms (M1–M6, §2) exhaust the plausible causal routes from "definitional, training-free, content-addressed concept representations" to "fewer params / fewer FLOPs / fewer bytes at matched accuracy". Each gets a causal story, the literature evidence for and against, and a kill criterion.
2. One measurement standard (F0, §3) governs every run: dual iso-accuracy/iso-compute discipline, Pareto-frontier reporting, explicit FLOP and byte accounting **including all kernel machinery** (encoder, adapter, verifier, store, retrieval), measured latency and $/query on pinned hardware.
3. Seven experiments (F1–F7, §4) instantiate the mechanisms, each with the mandatory metric vector (accuracy, params, memory ledger, inference FLOPs/latency/$, training FLOPs/steps-to-target), the five mandatory baselines where applicable (RAG-over-text, distillation, quantization/pruning, smaller-model-alone, kernel-as-text null), and a model-scale ladder.
4. Cheapest-decisive-first (§6): **F1** (KOTK memory-offload accounting; ~$0, this box) settles the *byte* premise of the memory story immediately; **F2** (verifier-offload on definitional QA, SmolLM2 135M/360M/1.7B, reusing the E5/E9 Modal harness; ~$10–40) is the cheapest experiment that touches the **full** metric vector and can kill or support the efficiency thesis proper.
5. The honest prior (§1) is asymmetric: the *verifier-side* mechanisms (M1/M5/M6) have live literature support (test-time compute substitutes for parameters; ToolkenGPT-shaped vocabulary extension; our own E5 PASS); the *dense-I/O and in-weights* mechanisms (M2-output, M3) are where the field's evidence says fixed-semantic structure historically loses. The track is designed so the cheap experiments discriminate exactly along that line.

---

## 1. Honest prior — what the record says before we spend a dollar

### 1.1 The field's bar for "efficiency" claims

Any claim of the form *smaller-model + kernel ≥ bigger-model* competes against four industrial-strength alternatives, each with published, large, cheap wins. These are not straw baselines; they are the reason most "external knowledge makes models smaller" papers do not matter:

| Alternative | Representative result | What it costs | Tag |
|---|---|---|---|
| **RAG / retrieval over text** | Atlas 11B beats PaLM 540B on knowledge tasks; RETRO 7.5B ≈ 25× larger models on the Pile (lit-llm-injection §3) | a text index + retriever; no model change | [established] |
| **Quantization** | 4-bit weight quantization (GPTQ arXiv:2210.17323, AWQ arXiv:2306.00978) ≈ 4× memory cut at near-parity | one-off calibration, minutes–hours | [established] |
| **Distillation / pruning** | Minitron (arXiv:2407.14679): pruned+distilled small models at up to ~40× fewer training tokens than from-scratch; DistilBERT-line ~40% smaller at ~97% capability | teacher inference + short training | [established] |
| **Smaller-model-alone + test-time compute** | Compute-optimal test-time scaling: small models beat ≫larger ones on verifiable tasks (Snell et al. arXiv:2408.03314; Liu et al. arXiv:2502.06703 — 1B > 405B on MATH-500 with a PRM; 0.5B > GPT-4o) | a verifier (usually a *trained* PRM) + extra sampling | [established on verifiable domains] |

Consequence: **an efficiency result that beats "no kernel" but not this table is not a result.** Every F-experiment carries the relevant subset as arms, plus the programme's own deflationary null.

### 1.2 The kernel-as-text null is mandatory everywhere

`lit-llm-injection-priorart.md` Law 2 [our synthesis over established results]: as models strengthen, the *text* interface to external knowledge improves automatically, while the *vector* interface keeps paying capability-independent tolls (trained adapter, ~62–73% fidelity ceiling à la xRAG, distribution matching). The null hypothesis in every F-experiment is therefore **the same kernel content rendered as Minimal-English text** (hash-pinned, in context or in the training data), not "no kernel". If kernel *vectors/machinery* cannot beat kernel *text* on the cost-accuracy frontier, the efficiency thesis reduces to "curated definitions help", which is neither novel nor architectural.

### 1.3 Where fixed-semantic concept I/O historically lost

- **LCM/SONAR** [established]: concept-space autoregression into a frozen semantic space did not surpass same-size token LLMs; third-party scaling exponents ~0.49–0.57 vs ~0.79 for token LMs (SONAR-LLM, arXiv:2508.05305) [claimed]. **CALM** (arXiv:2510.27688) [claimed] recovers the concept-level efficiency win *by abandoning the fixed semantic space* for a learned autoencoder latent. Verdict carried from the lit report: the scaling penalty attaches to *fixed semantic geometry as a prediction target*, not to concept-level step compression per se.
- **KEPLM injection** [established]: died of scaling + retrieval; probes showed little injected knowledge integrated; stronger hosts need it less.
- **Frozen embeddings** [established]: models train around them; mismatched frozen embeddings can cost 5–10× convergence; semantic initialisation washes out (the direct threat to M3).
- **InstructRetro** [established]: even *successful* external apparatus is absorbed into weights and becomes removable — which kills "permanent residence" claims but, note carefully, **supports** training-compute claims: scaffolding that is absorbed still saved the steps (§2 M3).

### 1.4 Where the thesis is most vs least likely to survive (pre-registered prior)

**Most likely** (in order): **M1/M5** verifier-offload/verifier-gated decoding on *kernel-covered, correctness-sensitive* slices — the substitution "test-time verification for parameters" is established; the kernel's marginal claim is a *deterministic, training-free, exactly-scoped* verifier instead of a trained PRM. **M6** amortized concept-vocabulary onboarding — E5 PASSed exactly this shape at toy scale (+28.5 pp over shuffled on unseen nonce concepts; E9-defl: content-specific, deflation recovers only ~8%). **M4** external-store byte arithmetic — externalising knowledge is established (Atlas); the kernel-specific edge over a compressed text store is small in bytes (§4 F1: ~3.3×) and must come from verifiability, not bytes.
**Least likely:** **M2-output** (predicting into kernel space — the LCM-shaped cell; pre-declared expected-fail, budgeted only as a cheap falsification), and **M3 at scale** (C2 is "[mostly contradicted]" in `architecture.md`; the surviving question is narrow: *content-bearing* scaffolding on *concept-heavy* distributions, where E1's 50%-token-checkpoint criterion is already the toy-scale gate).
**Global bound:** M0b's kernel-expressibility coverage number bounds every mechanism — efficiency wins can only occur on the covered token/task mass. A 5% coverage number caps the deployable win at roughly that slice; this is reported unvarnished in every verdict.

---

## 2. Mechanisms as hypotheses (M1–M6)

Format: causal story → falsifiable statement → strongest evidence for / against → kill criterion (operationalised in §4).

### M1 — Verifier-offload → smaller model
**Causal story.** Small models' errors on definitional/terminological content are disproportionately *detectable* errors when a deterministic verifier holds the ground-truth explications: decode the model's claim about a kernel-covered concept, check it against the canonical record (hash-level identity, structural consistency), reject/repair/retry on failure. Correctness is bought with cheap deterministic compute instead of parameters — the efficiency corollary of the endorsed A5 verifier track.
**Hypothesis.** ∃ task family T (kernel-covered, correctness-sensitive) and scales (s < S) such that model_s + kernel-verifier ≥ model_S alone on accuracy, at strictly lower total inference FLOPs, $ and memory.
**For:** test-time compute substitutes for params [established, §1.1 row 4]; the kernel verifier is training-free and O(lookup+decode) vs a PRM's per-token forward; the AlphaGeometry/Logic-LM topology (neural proposer + deterministic engine owns correctness) is the one verified capability win in the entire survey (lit report Law 3).
**Against:** PRM-based results live on *math/code* where verification is total; kernel coverage is partial (M0b), and the verifier checks *consistency with definitions*, not task truth — the accuracy lift may be small outside pure-definitional tasks. Retry loops multiply FLOPs; the win must survive expected-cost accounting.
**Kill:** F2 (§4.2).

### M2 — Dense concept I/O → fewer inference FLOPs (+ smaller KV cache)
**Causal story.** A concept vector carries a whole explication; injecting it as ~1 soft token replaces the N-token textual definition. Prefill FLOPs scale ~2·N_params·T and the attention term ~T²; KV bytes scale ~T. Cutting definitional context length K× cuts those terms proportionally at fixed model size.
**Split — this mechanism has a survivable half and a doomed half, pre-registered as such:**
- **M2-input** (xRAG/KBLaM-shaped, A2-mediated): kernel vectors enter through a small trained adapter as compressed *input* context. Live: xRAG/KBLaM show real dense-injection wins with quantified fidelity loss [established]; the kernel variant swaps their *trained* compressor for a *training-free canonical* vector + per-model adapter (already PASSed as an instrument in E5).
- **M2-output** (LCM-shaped): the model *predicts into* kernel space. Contradicted at scale on current evidence (§1.3); kept only as a cheap falsification with the field's default (fail) as the expected outcome. E3's guard is inherited: per-token metrics are descriptive only — the per-token metric wins by arithmetic and proves nothing.
**Hypothesis (input form).** At matched accuracy on tasks requiring in-context definitions, kernel-vector injection reaches the same accuracy at ≤1/2 the prompt FLOPs and KV bytes of full-text definitions, and is not matched by (a) truncated/summarised text at the same token budget or (b) an xRAG-style *trained* compressor at the same training budget.
**Kill:** F3 (§4.3).

### M3 — Grounded scaffolding → sample-efficient training
**Causal story.** Kernel structure (frozen content-bearing rows; explication-annotated data) gives the optimiser a consistent, compositional target for concept meanings, so concept-heavy distributions are learned in fewer tokens/steps → fewer training FLOPs to target accuracy. **The InstructRetro absorption finding is confronted head-on by re-scoping the claim:** we do not claim the kernel *remains* load-bearing in the weights (rows 12–13 of the lit synthesis say it will not); we claim only that the scaffold *saved steps on the way*. Absorption is compatible with — indeed the mechanism of — a training-compute win. What absorption *does* kill is any story requiring the kernel at inference time after such training; that story belongs to M4, not M3.
**Hypothesis.** On a concept-heavy distribution, kernel-scaffolded training (vector arm: frozen kernel rows; data arm: interleaved explication text) reaches the target-accuracy checkpoint at ≤0.8× the baseline token/FLOP budget, and the vector arm is not matched by the data arm (else the win is curriculum, not architecture).
**For:** E1's pre-registered 50%-checkpoint criterion is exactly this at toy scale; retrieval-augmented pretraining did improve sample quality before absorption (InstructRetro) [established].
**Against:** C2 "[mostly contradicted]"; frozen mismatched embeddings can *slow* convergence 5–10×; semantic init washes out; arXiv:2507.04886 predicts the null [established].
**Kill:** F6 (§4.6).

### M4 — Content-addressed external store → memory/param offload
**Causal story.** LMs store ~2 bits of extractable factual knowledge per parameter (Allen-Zhu & Li, arXiv:2404.05405 [established at their scales]) — i.e. ~16 fp16 weight-bytes, ~4 int8 bytes, per knowledge-byte. KOTK/2 stores a definitional record at the entropy floor: **2.90 B/record** measured on 117,791 wn31 records, 7.1–8.8 B/record on richer haiku-tier explications (`design-compact-kernel-serialization-v2.md`). Offloading definitional knowledge to the store lets a smaller model match a larger one's knowledge coverage: params buy skill, the store holds facts (the Atlas framing), with the kernel adding content-addressed identity + verifiability that a text store lacks.
**The honest arithmetic up front (from measured repo numbers):** the kernel's byte edge over its own deflation — the same records as zstd-19 identity-JCS text — is 9.58 → 2.90 B/record ≈ **3.3×**, not orders of magnitude. Orders of magnitude only appear vs *in-weights* storage (~8× vs fp16 at the Allen-Zhu density, before extraction-reliability differences) and vs *uncompressed* text (236×). So M4's kernel-specific claim must rest on {verifiability, O(1) identity, updateability} at *comparable* bytes to text-RAG — the byte story alone cannot carry it. Stated now so no verdict oversells it.
**Hypothesis.** small-model + kernel-store retrieval sits strictly outside the accuracy-vs-total-bytes Pareto frontier of {larger model alone, int4-quantized larger model, byte-matched text-RAG} on kernel-covered knowledge tasks.
**Kill:** F5 (§4.5); byte premise checked for ~$0 in F1 (§4.1).

### M5 — Verifier-gated cheaper decoding / cascade routing
**Causal story.** Deterministic error detection substitutes for statistical error suppression. Today correctness on risky outputs is bought with expensive decoding: self-consistency-N (N× FLOPs), best-of-N + judge, or simply a bigger model. A kernel verifier that *certifies* kernel-covered outputs enables: (i) greedy decoding where sampling was needed, (ii) cascade routing — run the small model, escalate to the large model only on verifier failure, (iii) draft-acceptance in speculative-style pipelines. Expected cost = c_small + p_escalate·c_large + c_verify; the win exists iff the verifier's false-accept rate is low and p_escalate ≪ 1 on real traffic. This is M1's deployment form; it is separated because its baseline is different — **the model's own calibration** (logprob-threshold cascades, FrugalGPT-style), which is free.
**Hypothesis.** On kernel-covered tasks, a kernel-verifier-gated cascade strictly dominates a logprob-gated cascade (matched escalation budget) on the accuracy-vs-expected-FLOPs frontier.
**For:** speculative decoding shows verify-don't-generate buys 2–3× wall-clock at *identical* outputs (Leviathan et al., arXiv:2211.17192) [established] — the template that cheap verification of cheap drafts is a real efficiency primitive.
**Against:** logprob calibration is a strong free baseline; kernel verification covers only the covered slice; per-step verification may interact badly with decoding (latency stalls).
**Kill:** F2b arm of F2 (§4.2).

### M6 — Amortized concept vocabulary → cheap domain adaptation (training-compute cut)
**Causal story.** E5 established [at toy scale, one model] that a single trained adapter maps *unseen* kernel vectors into usable soft tokens (+28.5 pp over shuffled; content-specific per E9-defl). If the adapter amortizes, adding a new domain's concepts costs **zero marginal training** — mint explications, encode (CPU, deterministic), inject — versus per-domain LoRA finetuning or per-token embedding training (ToolkenGPT trains every toolken). Training compute for domain adaptation drops from O(finetune) to O(authoring).
**Hypothesis.** For a new terminology domain, frozen-kernel-vectors + already-trained adapter reaches ≥90% of LoRA-finetune accuracy on domain-concept usage at ≤10% of its adaptation FLOPs, and beats in-context text definitions at matched inference cost.
**For:** E5/E9 PASS (the only injection cell with a measured kernel-content win anywhere in the programme); ToolkenGPT precedent that frozen hosts accept new functional symbols [established].
**Against:** in-context definitions are the killer null — a strong host may use 30 tokens of text as well as one injected vector, at zero training and only modest context cost; E5 never ran this arm.
**Kill:** F4 (§4.4).

**Not admitted as mechanisms** (considered, rejected as non-causal or duplicative): "kernel improves data quality" (that is data curation, tested inside M3's data arm); "hash-dedup of KV cache across requests" (an engineering optimisation orthogonal to the kernel's content — noted as a deployment bonus in F3's memory ledger, not a hypothesis); "kernel as tokenizer replacement" (strictly worse-supported than M2 and dominated by BLT-style learned units per the lit report).

---

## 3. Measurement methodology (F0 — the accounting standard)

Built once, versioned in-repo (`poc/f0/`), used by every F-run. Airtight-ness principle: **every number is either measured on pinned hardware or computed from a formula stated here, and every arm's total includes its own machinery.**

### 3.1 Comparison disciplines
Two pre-registered disciplines; every claim names which one it used:
- **Iso-accuracy:** fix the accuracy target (baseline's measured mean; candidate must fall inside the baseline's 95% CI or above), compare full cost vectors at that target. Cost-to-accuracy is found by sweeping the candidate's budget knob (model size, retrieval depth, retry count, token budget) — the sweep grid is pre-registered, no post-hoc knob-fitting.
- **Iso-compute:** fix total FLOPs/query (or training FLOPs), including kernel machinery, compare accuracy.
A mechanism claim is **strong** iff it wins under both; a single-discipline win is reported as qualified. Rationale: iso-accuracy alone rewards moving along a flat region; iso-compute alone rewards accuracy at absurd budgets.

### 3.2 Pareto-frontier reporting
Per experiment, four frontiers, all arms on all of them: accuracy vs (i) inference FLOPs/query, (ii) params (N_total and N_active), (iii) peak memory (total-system bytes, §3.4), (iv) training FLOPs-to-target (training experiments only). **A mechanism "wins" only if it places a point strictly outside the convex hull of ALL baseline points on the relevant frontier** — beating one baseline while sitting inside another baseline's hull is a null. Frontiers ship as data (CSV) + plot per run.

### 3.3 FLOP accounting
- **LM inference:** FLOPs ≈ 2·N_active·T_total + 2·L·T²·d_attn per sequence (the quadratic term is *mandatory* — M2's claim lives exactly there; omitting it flatters long-context baselines). Prefill and decode accounted separately; T measured per arm with that arm's own tokenizer.
- **LM training:** FLOPs ≈ 6·N·tokens to the target checkpoint (Kaplan/Chinchilla convention), plus any teacher inference (distillation arms: 2·N_teacher·tokens — distillation is NOT free and its teacher cost is on its ledger, stated because this is where distillation comparisons are usually rigged in either direction).
- **Kernel machinery enters as follows, none of it waived:**
  - *Encoder* (explication→vector): one-time, CPU; measured seconds/vector at D=8192; amortized over the declared query volume Q (both amortized and unamortized reported; Q pre-registered per experiment, default 10⁶ queries).
  - *Adapter:* 2·N_adapter FLOPs per injected concept token, on the per-query ledger.
  - *Verifier (decode-verify):* dominated by nearest-neighbour cleanup ≈ |lexicon|·D MACs per cleanup step (~1.6 GFLOP/step at 10⁵ concepts, D=8192 — same order as tens of forward tokens of a 135M model, so it is **counted, not hand-waved**); ANN indexing may reduce it, in which case the index memory goes on the ledger (§3.4). Hash lookups and structural checks metered as measured CPU-time and converted at the hardware's FLOP/s only for the aggregate figure; reported separately as wall-clock too.
  - *Retrieval:* index probe cost per query (measured), embedding cost if the query must be embedded.
  - *Cascade/retry:* expected FLOPs = Σ p(path)·FLOPs(path), with p(path) measured on the eval distribution, not assumed.
- Cross-check rule: formula-FLOPs vs measured wall-clock×(pinned hardware FLOP/s×measured MFU) must agree within 2×, else the run is flagged and the discrepancy explained before any verdict.

### 3.4 Memory ledger (peak, measured + decomposed)
Headline = **total-system peak bytes** (prevents hiding the store): weights (by dtype) + KV cache (2·L·T·n_kv·d_head·bytes, at the eval's actual max T and batch) + adapter + activations peak (measured) + **kernel store bytes (KOTK/2, measured)** + materialized vector cache (fp16 D·4bytes... fp16 = 2·D bytes/concept; 16 kB/concept at D=8192, 1 kB at d=512 — whether vectors are stored or re-derived on demand is an arm-level choice whose compute/memory trade F1 measures) + retrieval/ANN index + text corpus for RAG arms (compressed, as served). Measured via device memory profiler (torch.cuda.max_memory_allocated + RSS), not estimated, with the formula decomposition reconciled against the measurement.

### 3.5 Latency and $/query
Pinned hardware configs (from poc-design Hardware, extended): T4 g4dn.xlarge ($0.53/hr on-demand) and A10G g5.xlarge ($1.01/hr); training-scale runs on A100-40GB with the rate pinned in the run manifest. Report batch-1 p50/p95 latency AND max-throughput tokens/s (latency-bound and throughput-bound deployments differ; verifier/cascade overheads hit them differently — a CPU-side verifier can hide under GPU decode in throughput mode but not in batch-1 latency). $/query = measured wall-clock × pinned $/hr, both modes. CPU-side kernel work priced at the same node's CPU (it rides along free unless it becomes the bottleneck — measured, not assumed).

### 3.6 Fairness rules (anti-apples-to-oranges)
1. Same eval items, same prompts (modulo the arm's declared representation), same scoring across arms; scorers are non-LLM rubrics or leak-checked judges (E5 discipline).
2. **Equal tuning budget:** every arm gets the same HPO budget under the poc-design Common-rule-5 selection protocol; no arm is tuned harder than its baselines.
3. The **kernel-as-text null** (§1.2) is present in every experiment; where a structural deflation is meaningful, the E9-defl scrambled-structure arm too.
4. Quantization symmetry: if any arm is quantized, the comparison includes quantized versions of both sides.
5. Token asymmetry honesty: arms with different tokenizers/vocabularies report both their own token counts and normalized bytes-of-input; FLOPs always computed per-arm.
6. Statistics inherited from poc-design Common rules: ≥5 paired seeds for trained conditions, single pre-registered primary endpoint per experiment, Holm-corrected secondaries, paired permutation tests, TOST (d=0.5 default) required to declare a null; negative results are first-class.
7. Scale claims only from the ladder (§5): a single-rung result licenses nothing about scale; every verdict carries its rung.
8. Coverage disclosure: every verdict restates M0b's kernel-expressibility number and the evaluated slice's relation to it.

---

## 4. Experiments F1–F7

Common metric vector **V** (mandatory in every F-report, per maintainer directive): **accuracy/correctness** (task primary + kernel-covered-slice), **params** (N_total, N_active, N_trained), **memory** (§3.4 ledger, total-system peak headline), **inference compute** (FLOPs/query per §3.3, p50/p95 latency, $/query), **training compute** (FLOPs/steps/tokens-to-target, wall-clock, $; "n/a" only for pure-inference experiments with no trained component beyond a pinned, already-costed adapter).

### F1 — Memory-offload accounting study (M4 byte premise; ~$0, this box, CPU)
**Question.** What does a knowledge-byte cost in each medium, measured — and what does serving it cost?
**Design.** No model training. On this box: (i) assemble the byte ledger per knowledge record across media: KOTK/2 pack (measured: 2.90 B/rec wn31; 7.1–8.8 B/rec haiku-tier), zstd-19 identity-JCS text (measured: 9.58 B/rec), zstd'd plain-gloss text (to be measured — the RAG-over-text store as actually served), materialized fp16 vectors at D=8192 and d=512, and the in-weights equivalent via the Allen-Zhu 2-bit/param density (~8 fp16-bytes... 16 weight-bits per 2 knowledge-bits ⇒ 8× fp16, 4× int8, 2× int4 overhead per knowledge-bit) [computed, clearly labelled as resting on Allen-Zhu's scales]; (ii) measure retrieval latency + peak RSS for hash-lookup and record-decode from the KOTK/2 pack vs a zstd text store vs a naive JSONL store, at 10³/10⁵ record scale; (iii) measure the derive-vectors-on-demand vs cache-vectors compute/memory trade (encoder seconds/vector vs 16 kB/concept).
**Metric vector V:** accuracy n/a (no model); everything else measured.
**Baselines & why:** compressed-text store (the deflationary medium — the kernel must state its edge over it in bytes AND capabilities); uncompressed JSONL (the honest "what we'd naively ship").
**Kill criterion (byte premise):** if KOTK/2 fails to beat the best *general-purpose-compressed text store of the same records* by ≥2× bytes at ≤2× retrieval latency, the memory-offload pitch drops the byte claim entirely and M4 proceeds (if at all) on verifiability alone. (Current evidence says ~3.3× vs identity-JCS+zstd — expected pass, but glosses-only text may compress tighter; measure it.)
**Scale axis:** store scale (10³→10⁵→extrapolated 10⁶ records), not model scale.
**Cost:** ~0 GPU; days of niced CPU at most.

### F2 — Verifier-offload on definitional QA (M1 primary; M5 cascade as F2b; first GPU spend, ~$10–40)
**Task.** Definitional/terminological QA built from kernel v0 + wn31-backed records: (a) E5-style slot-filling and forced-choice usage items on kernel-covered concepts; (b) consistency items where the model's answer entails a definitional claim the verifier can check (decode→hash/structural check against the canonical record). TinyStories-clean-domain discipline inherited: this is a *favourable-case* slice by construction, stated as such.
**Arms (inference-only; SmolLM2-instruct family, harness-proven):**
1. 135M alone; 2. 360M alone; 3. 1.7B alone (the "larger model" targets);
4. 135M + kernel-verifier loop (verify → reject → resample/repair, max-k retries, k∈{1,2,4} pre-registered sweep);
5. 135M + kernel-as-TEXT (Minimal-English explication in context, no verifier) — the Law-2 null;
6. 135M + RAG-over-text (BM25/embedding retrieval over the gloss corpus) — the industrial null;
7. 135M + self-consistency-N at FLOPs matched to arm 4 — "spend the same extra compute without the kernel";
8. (F2b) cascade 135M→1.7B gated by kernel verifier vs gated by logprob threshold, escalation budget matched;
9. int4-quantized 360M (quantization null: maybe the cheap way to "a smaller model" is just quantizing the bigger one).
**Why these baselines:** 2/3 define the gap to close; 5 is mandatory (§1.2); 6 is the winner of the injection literature; 7 isolates "verification" from "more compute"; 8's logprob gate isolates "deterministic verification" from "any confidence signal"; 9 is the practitioner's alternative.
**Primary endpoint (pre-registered):** kernel-covered-slice accuracy of arm 4 vs arm 2 (does 135M+verifier reach 360M?) under iso-accuracy discipline, with full V reported; paired bootstrap over items, α=0.05.
**Kill criterion:** M1 is dead at this scale if (a) arm 4 closes <50% of the (135M→360M) accuracy gap at its best pre-registered retry budget, OR (b) arm 5 (text null) or arm 7 (matched-compute sampling) closes as much gap at ≤ the same FLOPs/query, OR (c) closing the gap costs ≥ the FLOPs/query of running 360M directly. F2b/M5 is dead if the verifier-gated cascade does not strictly dominate the logprob-gated cascade on the accuracy-vs-expected-FLOPs frontier. Nulls require TOST.
**Scale ladder:** repeat the (s, S) pair at (360M, 1.7B); if both rungs show the same sign, F7 adds (1.7B, 7B-class). Pre-registered scale question: does the closable gap fraction grow or shrink with S?
**Cost:** inference-only on T4/A10G via the existing Modal harness; ~$10–40.

### F3 — Dense concept input vs text (M2-input; ~$50–150)
**Task.** QA/consistency items whose prompts require d in-context definitions (d∈{4,16,64}) — long-glossary regime where the T and T² terms bite. Toy-clean domain first (kernel v0 concepts), wn31-backed second.
**Arms (SmolLM2-360M host, A2 adapter per E5 protocol, frozen kernel vectors, JL-projected path with X4 distortion reported):**
1. full text definitions in context; 2. kernel vectors via adapter, 1 soft token/concept; 3. kernel-as-text *compressed by an LLM summarizer* to match arm 2's token budget (matched-token text null); 4. truncated text at matched tokens (cheap matched-token null); 5. xRAG-style *trained* compressor at the same adapter-training budget (isolates "canonical training-free" from "dense injection works"); 6. shuffled-kernel vectors (assignment null, E5 discipline); 7. no definitions (floor).
**Primary endpoint:** accuracy at matched *prompt FLOPs + KV bytes* (iso-compute), arm 2 vs arms 3/4; secondary: iso-accuracy prompt-FLOP ratio vs arm 1.
**Kill criterion:** M2-input dead at this scale if arm 2 fails to beat both matched-budget text arms (3 AND 4) at d≥16, or if arm 5 matches arm 2 (then dense injection works but the kernel's training-free canonicality adds nothing measurable to *efficiency* — any residual claim moves to governance). Adapter training FLOPs are amortized per §3.3; if amortized adapter cost exceeds the per-query savings at Q=10⁶, the win is declared uneconomic regardless of accuracy.
**M2-output rider (cheap falsification, pre-declared expected-fail):** one small run — loss-vs-compute slope for next-concept prediction into frozen kernel space vs next-token prediction, E3's task and guards, 5-15M models; kill (expected): concept-space slope worse, consistent with LCM/SONAR-LLM. Budgeted ≤$20; a surprise survival re-opens the question at the next rung, nothing more.
**KV/memory note:** arm 2's ledger books the KV savings AND the adapter+vector-cache bytes; the deployment bonus (definitions cached once by content-address across requests) is reported descriptively.
**Scale ladder:** 135M → 360M → 1.7B hosts (does the dense-input win shrink as the host gets better at using text? — Law 2 predicts yes; measure the slope).

### F4 — Amortized vocabulary onboarding vs LoRA (M6; ~$20–60)
**Design.** Extend the E5 instrument with cost accounting and the missing nulls. Domain = a held-out concept tier (≥50 new concepts with explications + glosses, disjoint from adapter training).
**Arms:** 1. frozen kernel vectors + *already-trained* adapter (zero marginal training — E5 arm, now costed); 2. LoRA finetune on domain glosses (the industrial domain-adaptation baseline, matched data); 3. per-concept trained embeddings, ToolkenGPT protocol (isolates "canonical vector" from "trained new symbol"); 4. in-context text definitions, no training (the null most likely to win); 5. shuffled-kernel (assignment null).
**Primary endpoint:** domain-concept usage accuracy (E5 rubric) per unit *adaptation FLOPs* (iso-accuracy: FLOPs to reach 90% of arm 2's accuracy).
**Kill criterion:** M6 dead if arm 1 < 90% of arm 2's accuracy at every point, or if arm 4 ≥ arm 1 at matched inference FLOPs/query (in-context text makes onboarding free too — then the adapter path has no marginal value), or if arm 3 ≈ arm 1 only when arm 3's per-concept training is included (i.e. canonical vectors save nothing).
**Scale ladder:** SmolLM2 135M/360M/1.7B; pre-registered question: E5's effect was measured at 135M only — does the text null overtake vector injection as host scale grows (Law 2 direction)?

### F5 — Knowledge-offload: store vs weights (M4 full test; ~$200–800)
**Design.** The accuracy leg of M4. Controlled knowledge corpus (wn31-backed relational/definitional facts, coverage known by construction), small LMs trained/continued-pretrained with and without retrieval access to the kernel store; eval = knowledge tasks over covered facts + a held-out generalisation slice.
**Arms:** 1. Pythia-style model_S trained on corpus (in-weights, the knowledge lives in params); 2. model_s (≈S/2.5) + kernel-store retrieval (records decoded to text or injected via F3's adapter, whichever won F3 — fork 1 feeds in here); 3. model_s + byte-matched text-RAG (same knowledge as compressed glosses, store bytes equalized to arm 2's ledger); 4. int4-quantized model_S (quantization null: 4× memory for free); 5. model_s alone (floor); 6. distilled model_s from model_S teacher (distillation null; teacher FLOPs on its ledger).
**Primary endpoint:** accuracy vs **total-system peak bytes** frontier (§3.2 iii); secondary: accuracy vs params; inference FLOPs/query with retrieval costed.
**Kill criterion:** M4-kernel dead if arm 2 fails to place outside the hull of arms {3,4,6} on the accuracy-vs-total-bytes frontier — i.e. if byte-matched text-RAG, or simply quantizing/distilling the bigger model, matches the kernel store. (Arm 2 beating arm 1/5 alone re-establishes Atlas/RETRO, which is not ours to claim and is reported as such.) Verifiability side-benefits are logged but cannot rescue an efficiency null — they belong to E9/A5.
**Scale ladder:** train at 70M/160M (Pythia configs, from scratch on the controlled corpus — feasible: 6·N·tokens at ≤2B tokens ≈ low-hundreds of A100-hours worst case, budget-gated); 410M rung only if 160M is positive.

### F6 — Tokens-to-target with kernel scaffolding (M3; ~$50–150 toy, ladder gated)
**Design.** E1's sample-efficiency criterion, promoted to a full-accounting efficiency experiment with the missing text-scaffold arm. Concept-heavy corpus (TinyStories + concept augmentation per E1 AMENDMENT A1; 52-concept evaluated set).
**Arms (5 paired seeds each, E1 Common rules):** 1. kernel-frozen rows (E1 arm); 2. shuffled-kernel-frozen (E1 null); 3. trainable (E1 baseline); 4. **explication-text-interleaved data, trainable embeddings** (the kernel-as-text-in-training-data null — the arm the lit report demanded); 5. kernel-init-trainable (washout probe).
**Primary endpoint:** training FLOPs (=6·N·tokens) to the pre-registered target accuracy on E1's concept-cloze endpoint; the E1 single-look rule (arm-1@50%-tokens vs arm-2@100%) carries over as the headline test.
**Kill criterion:** M3-vector dead if arm 1 fails the ≤0.8× tokens-to-target bound vs arm 3 (TOST), or if arm 4 matches arm 1 (win is data curriculum, not architecture — arm 4 surviving alone is still a publishable data result, filed under M3-data, but it retires the architectural claim). Absorption is NOT a kill: post-training removal of kernel apparatus at eval time is run descriptively (InstructRetro protocol) and informs M4 vs M3 (fork 2), not this verdict.
**Scale ladder:** 5–15M (E1 scale) → Pythia-70M config → 160M, matched token budgets; this ladder merges into E7's 15M/160M/~1B plan (shared compute, one budget sign-off). Frozen-embedding convergence penalties are documented at ≥100M [established], so **the 160M rung is the smallest decisive rung for M3** — toy-scale wins are necessary but not sufficient.

### F7 — Efficiency scale-slope (gate-kept, ~$2–10k, merges with E7)
**Design.** For every mechanism alive after F1–F6: re-measure its efficiency delta at three rungs (inference mechanisms: SmolLM2 135M/360M/1.7B + one Qwen2.5 rung 3B for family replication; training mechanisms: 15M/160M/~1B per E7). Pre-registered question per mechanism: is Δ(cost saved at iso-accuracy) growing, flat, or shrinking in model scale?
**Kill criterion (frontier relevance):** a mechanism whose Δ shrinks monotonically across all three rungs and extrapolates below practical significance (pre-registered per mechanism; default: <10% cost saving at iso-accuracy) at 7B is declared **toy-only**: honest for the prospectus, dead for a frontier pitch. Not started without maintainer budget sign-off (same governance as E7).

---

## 5. Scale ladder (concrete recommendation)

**Inference-side mechanisms (M1, M2-input, M5, M6): SmolLM2 135M / 360M / 1.7B** (arXiv:2502.02737; instruct variants; already the programme's proven Modal harness models) as the primary ladder, with **Qwen2.5 0.5B / 1.5B / 3B** as the replication family (different tokenizer/data lineage — guards against SmolLM2-specific artifacts). Rationale: verifier-offload needs *gaps to close between adjacent rungs*, and the 135M→360M→1.7B spacing (~2.7×/4.7×) gives large, cheaply measurable accuracy gaps on knowledge tasks. **Smallest decisive rung: the (135M, 360M) pair** — if the kernel cannot lift 135M toward 360M on its own favourable-case slice, no larger rung will be kinder (Law 2 runs the wrong way).

**Training-side mechanisms (M3, M4): Pythia 70M / 160M / 410M configs** (arXiv:2304.01373; revision-pinned suite, public data order, deduped variants — the standard controlled-training lineage), trained from scratch on the track's controlled corpora at matched token budgets; 1B/1.4B only inside the F7/E7 gate. **Smallest decisive rung: 160M** — below it, frozen-embedding penalties and retrieval-baseline dynamics are not yet representative (documented convergence effects at ≥100M), so 5–15M results gate spending but decide nothing.

**Slope discipline:** every mechanism is measured at ≥3 rungs before any scale adjective ("appears/vanishes/grows") is used; two rungs license only a sign, one rung licenses nothing (§3.6 rule 7).

---

## 6. Cheapest-decisive-first ordering

| # | Exp | Mechanism | Cost | What it can decide |
|---|---|---|---|---|
| 1 | **F1** | M4 byte premise | ~$0 (this box) | kills/retains the memory-offload *byte* story; publishes the honest 3.3×-not-1000× number either way |
| 2 | **F2** | M1 + M5 | ~$10–40 | **the single cheapest kill-or-support of the efficiency thesis proper** — full metric vector, reuses E5/E9 harness, targets the best-supported mechanism |
| 3 | F4 | M6 | ~$20–60 | extends the programme's only PASSed injection instrument into a costed adaptation claim |
| 4 | F3 | M2-input (+output rider) | ~$50–170 | decides fork 1; retires or promotes dense I/O for efficiency |
| 5 | F6 | M3 | ~$50–150 toy | training-compute claim at toy scale; gates the 160M rung |
| 6 | F5 | M4 full | ~$200–800 | store-vs-weights accuracy leg; only worth running if F1 passes and F3's injection path is settled |
| 7 | F7 | all survivors | ~$2–10k | scale slopes; maintainer gate, merged with E7 |

Rationale for the F1→F2 order: F1 is near-free but touches only bytes — it cannot support the thesis, only trim it. F2 is the cheapest experiment whose PASS would be *evidence for* "kernel cuts cost at matched accuracy" and whose clean kill (text-null or matched-compute-sampling parity) would gut M1 and M5 simultaneously — the two mechanisms with the best prior. If F2 dies cleanly at both rungs, the surviving efficiency programme is M6+M4-verifiability, which is a much smaller pitch, and the maintainer should know that for ~$40.

---

## 7. Design forks exposed

**Fork 1 — Concept-I/O-as-shorter-sequence vs verifier-offload-keeps-token-I/O.**
Options: (A) invest in the dense-input stack (A2 adapters, soft tokens, KV savings — M2); (B) keep token I/O untouched and put the kernel entirely at the interface (verify/route/cascade — M1/M5).
Why uncertain: xRAG/KBLaM prove dense input wins exist with trained bridges [established]; E5 proves the kernel's training-free variant transfers at toy scale; but Law 2 predicts text catches up as hosts strengthen, and every A1-adjacent cell in the literature is empty.
Deciding experiment: F3 vs F2 on the same task family and budget (both produce accuracy-vs-FLOPs frontiers; directly comparable by §3.2).
Kill: if F3's arm 2 is dominated by F2's cascade at matched accuracy, drop dense I/O from the efficiency track (it may survive elsewhere on latency-specific grounds only if measured so).

**Fork 2 — External-store (runtime dependency) vs in-weights (scaffold-then-absorb).**
Options: (A) M4 — knowledge stays in the kernel store forever, models stay small, store is updateable, verifiable, and on the memory ledger; (B) M3 — kernel scaffolding accelerates training, is absorbed (InstructRetro-style), apparatus removed at deployment; zero runtime cost, zero runtime benefit.
Why uncertain: InstructRetro says absorption happens and costs nothing at inference [established]; but absorption forfeits updateability and verifiability, and Allen-Zhu density says in-weights knowledge is byte-expensive; the crossover depends on query volume and update rate — unmeasured.
Deciding experiment: F5 arm 2 vs F6 arm 1 at the 160M rung, compared at matched *total lifecycle FLOPs* (training + Q·inference, Q swept over 10⁴–10⁸) — F0's amortization machinery exists precisely for this.
Kill: store dies if scaffold-then-discard dominates at all realistic Q; scaffold dies on F6's tokens-to-target TOST.

**Fork 3 — Deterministic kernel verifier vs trained verifier (PRM).**
Options: (A) kernel decode-verify — training-free, exactly scoped, cheap, narrow; (B) small trained PRM — broad, costs training + per-token inference.
Why uncertain: the entire test-time-scaling literature runs on trained PRMs; nobody has measured whether a deterministic definitional verifier buys comparable routing/accuracy signal on the slice it covers.
Deciding experiment: add a tiny-PRM arm (reuse an off-the-shelf small reward model) to F2 at matched inference FLOPs.
Kill: if the generic PRM matches the kernel verifier *on kernel-covered content*, the kernel's efficiency contribution collapses into commodity verification — determinism/provenance revert to governance claims (A5/E9 territory), and M1/M5 lose their kernel-specificity.

**Fork 4 — Kernel-structured store vs hash-pinned text store (the M4-internal deflation).**
Options: (A) KOTK/2 records + optional vectors; (B) the same content as hash-pinned Minimal-English text (E9-rev-3's deflationary architecture).
Why uncertain: measured byte gap is only ~3.3×; text needs no decoder and feeds RAG directly; the structured store's edge is machine-checkable identity + verifier compatibility — value that only shows up when a verifier consumes it.
Deciding experiment: F5 arms 2 vs 3 (byte-matched), plus F2 arm 4 re-run with a text-diff-based checker replacing the structural verifier (can plain text verification match structural verification?).
Kill: text-store parity on both ⇒ the kernel's efficiency contribution is a compression format, not an architecture; keep KOTK/2 as engineering, retire the M4 architectural claim.

**Fork 5 — Where verification runs: post-hoc retry vs in-decode gating.**
Options: (A) generate → verify → resample (simple, batchable, k× cost on failures); (B) step-level constrained/gated decoding (catches errors early, but stalls decode and needs incremental verification).
Why uncertain: pure engineering trade at small scale, but it determines M5's latency profile (batch-1 vs throughput, §3.5) and hence the $/query verdict.
Deciding experiment: F2's retry-budget sweep (k∈{1,2,4}) vs one in-decode gating arm, latency measured both modes.
Kill: none (both can lose to the logprob cascade — that kill lives in F2b); this fork only picks the surviving implementation.

---

## 8. What a full-track sweep licenses — and does not

A clean positive sweep at the toy/small rungs licenses exactly: *"at ≤1.7B scale, on kernel-covered correctness-sensitive slices, kernel verification (and, if F3/F4 survive, dense concept input and amortized vocabulary onboarding) buys measured {X% params / Y% FLOPs / Z bytes} at matched accuracy against the strongest cheap alternatives, including the kernel's own text rendering."* It does **not** license: frontier-scale claims (F7 is the only currency there), open-domain claims (coverage-bounded by M0b), or any restatement of the strong A1 thesis (this track never touches "the model adopts kernel meaning" — E-series owns that). Per the E-series discipline, all nulls ship with the same prominence as passes, and every externally quoted number carries its rung, its coverage bound, and its comparison discipline.

## 9. Citation index (new to this track; repo reports carry the rest)

| Topic | Work | ID |
|---|---|---|
| Test-time compute vs params | Snell et al. | arXiv:2408.03314 |
| 1B>405B with PRM-guided TTS | Liu et al. | arXiv:2502.06703 |
| Knowledge capacity ~2 bits/param | Allen-Zhu & Li | arXiv:2404.05405 |
| Speculative decoding 2–3× | Leviathan et al. | arXiv:2211.17192 |
| 4-bit quantization near-parity | GPTQ; AWQ | arXiv:2210.17323; arXiv:2306.00978 |
| Pruning+distillation, ~40× fewer tokens | Minitron | arXiv:2407.14679 |
| Small-model suites (ladder) | Pythia; SmolLM2 | arXiv:2304.01373; arXiv:2502.02737 |
| RAG/memory/absorption/LCM/CALM/ToolkenGPT | see `reports/lit-llm-injection-priorart.md` §10 | — |
| Store bytes (measured) | KOTK/2 decision record | `docs/design-compact-kernel-serialization-v2.md` |
| Capacity arithmetic | DCV report §7 | `reports/deterministic-concept-vectors.md` |
