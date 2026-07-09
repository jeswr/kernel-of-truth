# Prior Art, Line 4: Deterministic Structure-Parsing at the Model Boundary (Code & Structured Data) + Symbolic Inference Between Layers

**Kernel of Truth programme — literature review, Line 4.**
Author: Kern (Claude Fable 5, literature-researcher role). Date: 2026-07-09.
**Purpose:** prior-art + idea-mining pass feeding the architecture-advisor's idea+permutation
registry (`docs/next/idea-registry.md`, in construction). Two maintainer threads:
**(A)** deterministic structured-data → concept parsing built into an LLM's encoder/decoder,
for code + structured formats; **(B)** symbolic inference *between* layers
(decode hidden state → concepts → symbolic inference → re-encode → next layer).

**Epistemic contract.** Every load-bearing claim carries BOTH tag families:
[established]/[claimed]/[speculative] (report convention) and
MEASURED / LIT-BACKED (arXiv id + year) / STIPULATED / EXTRAPOLATION (directives
convention); live web checks are marked **[search]** (verified 2026-07-09), training-memory
items **[memory]**. KB/lit records are recall infrastructure, NOT evidence; nothing here
amends any registry entry; no [claimed]/[speculative] item may become a prereg premise
without source-verification at freeze time. Companions: `reports/lit-llm-injection-priorart.md`
(L3 laws), `docs/next/arch-survey.md` (N0), `docs/next/architecture-ladder.md` (N1-A).

---

## 0. One-paragraph verdicts

**Thread A.** Deterministic structure-parsing has been injected into neural code models at
three loci with sharply different fates. (i) *Encoder-side, small pretrained models*
(110M–770M): real but modest wins — GraphCodeBERT's data-flow attention, StructCoder's
AST+DFG encoder/decoder, AST-T5's AST-aware spans each buy ~1–3 points over their
structure-blind twins [established]. (ii) *Input-side at LLM scale*: mostly washes out —
serialized ASTs reach only parity with raw code for an 8B LLM, deep static-analysis
signals neither live in the models nor transfer in, while *shallow* deterministic facts
added to prompts still buy ~2 BLEU [established, mixed]. What survives at 1B–8B scale is
structure-aware *objectives* (AST-FIM) and *compiler-IR grounding* (IRCoder), not
structure-aware input encodings. (iii) *Decoder-side*: the unambiguous wins. Incremental
parsing / grammar masks / type systems as deterministic decode-time filters transform
outputs — execution errors 12%→2% (PICARD), 96% syntax-error reduction (SynCode),
compilation errors halved + repair +37% relative (type-constrained decoding, PLDI 2025) —
at near-zero overhead (XGrammar) [established]. The two priced caveats: greedy
grammar-masking distorts the LM's distribution (GAD), and format restriction taxes
reasoning unless reasoning and formatting are decoupled (Format-Tax line). Net law for
our programme: **deterministic parsing pays at the decoder and in external engines; it
pays on the encoder side only below LLM scale or through training-time grounding — the
same interface-locality + absorption pattern as L3.**

**Thread B.** The literal decode→concepts→symbolic-inference→re-encode→next-layer cell is
nearly empty: one direct occupant (a 2025 trained VSA-bridge system, single-group,
spectacular numbers on narrow rule-following tasks, unreplicated [claimed]), plus a
strong sibling *outside* LLMs (IBM's NVSA: perception → vector-symbolic algebra →
probabilistic abduction, measured SOTA on RAVEN with two-orders-of-magnitude cheaper
reasoning [established]). What IS mature is the instrument layer the loop needs:
training-free read/write access to mid-network state — Patchscopes (decode hidden states
via the model itself), function/steering vectors (extract from the model's own
activations, re-inject, causal effects), inference-time intervention (TruthfulQA
32.5%→65.1%), and back-patching (up to 66% of failed 2-hop queries rescued by moving a
late hidden state to an earlier layer) [established]. Trained latent-reasoning loops
(Coconut, recurrent-depth) show the residual stream can carry multi-step reasoning, but
all require training the host and trade away inspectability [established]. Feasibility
for our training-free, cosine-banned kernel: a composed loop — model-native decode
(patchscope/text) → mapper-exact concept identification → kot-axiom engine → feedback as
text, steering vector, or back-patch — is buildable from established parts; the
composition itself is unmeasured EXTRAPOLATION, and every concept-identification step
must be exact-match on decoded text, never kernel-space nearest-neighbour (X3).

---

## 1. THREAD A — deterministic structured-data parsing at the model boundary

### 1.1 Structure-aware encoders: the small-model record (2019–2023)

The pre-LLM generation established that deterministic parse structure, injected into the
*encoder* (or as auxiliary objectives), reliably buys a few points at BERT/T5 scale:

- **GraphCodeBERT** (Guo et al., ICLR 2021, arXiv:2009.08366) **[search] [established]
  LIT-BACKED**: adds the deterministic *data-flow graph* (where-a-value-comes-from) to a
  CodeBERT-class encoder via graph-guided masked attention + two structure-aware
  pretraining tasks (edge prediction, variable alignment). SOTA at its scale on code
  search, clone detection, translation, refinement; ablations attribute the gain to the
  data-flow machinery (code-search gain significant at p<0.01). The paradigm case of
  "deterministic semantic structure into the encoder works" — at 125M parameters.
- **StructCoder** (Tipirneni et al., TKDD 2024, arXiv:2206.05239) **[search]
  [established] LIT-BACKED**: first structure-aware *decoder* line — encoder consumes
  AST + DFG; decoder is trained with auxiliary AST-path and data-flow prediction tasks
  (AST-path prediction 94% acc; DFG-edge prediction 94.7 AP at 0.8% positive prevalence).
  SOTA on CodeXGLUE translation and text-to-code at T5 scale. Note the mechanism:
  structure enters as *training signal*, not as an inference-time deterministic pass.
- **AST-T5** (Gong et al., 2024, arXiv:2401.03003) **[search] [established] LIT-BACKED**:
  AST-aware segmentation + AST-aware span corruption, no architecture change; +2 EM
  Bugs2Fix, +3 EM Java–C# transpilation over CodeT5 at matched size. Deliberately
  parser-at-training-time-only — inference is plain text.
- **TreeGen** (Sun et al., AAAI 2020, arXiv:1911.09983) **[memory] [established]**:
  grammar-rule-sequence decoder (generates AST construction actions, not tokens); the
  strongest of the grammar-action line (TranX, Yin & Neubig 2018, arXiv:1810.02720
  **[memory]**; Abstract Syntax Networks 2017 **[memory]**) — syntactic validity by
  construction, SOTA on small text-to-code sets of the era. This line was *absorbed* by
  scale: no frontier code model generates AST actions; token decoding + post-hoc
  constraints won.
- **Code property graphs** (Yamaguchi et al., IEEE S&P 2014) **[memory] [established]**:
  the canonical deterministic code→graph representation (AST ∪ CFG ∪ PDG in one graph;
  industrialised in Joern). Consumed by GNN-era vulnerability detectors (Devign, NeurIPS
  2019, arXiv:1909.03496 **[memory]**). Modern relevance for us is *not* as a model
  input but as a deterministic extraction source (→ §1.5, world-layer route).

**§1.1 verdict.** At sub-LLM scale, with-vs-without is measured and positive but small
(single-digit points), and the wins concentrate on code-to-code tasks where the output
is itself structured. Every mechanism that worked passes structure through *trained*
components (attention masks learned around the graph, auxiliary losses) — consistent
with L3's interface-locality law; none feeds a foreign structural encoding raw.

### 1.2 What happens at LLM scale: objectives survive, input encodings wash out

The 2024–2026 record splits cleanly by locus:

- **Structure-aware objectives survive.** **AST-FIM** (arXiv:2506.00204, 2025) **[search]
  [established] LIT-BACKED**: tree-sitter-based AST-aware fill-in-the-middle masking at
  1B and 8B scale, language-agnostic, up to +5 points over random-character FIM on
  infilling/code-editing benchmarks. **IRCoder** (Paul et al., ACL 2024, arXiv:2403.03894)
  **[search] [established] LIT-BACKED**: continued pretraining of 1.1B–7.3B code LMs on
  ~4M source↔compiler-IR pairs (SLTrans); "sizeable and consistent" gains including
  **prompt robustness**, multilingual completion, and understanding. The deterministic
  artifact (compiler IR — a canonical, language-shared semantic form) improves the model
  by being *trained through*, exactly the F6-scaffolding shape.
- **Input-side AST serialization: parity, not gains.** Direct with-vs-without at 8B:
  serialized-AST input for LLaMA-3.1-8B code summarization achieves quality *parity*
  with raw code — the measured benefit is shorter inputs/faster training, not accuracy
  (arXiv:2602.06671, 2026) **[search] [established] LIT-BACKED**. The authors' reading:
  LLMs already extract the structure from raw text; explicit ASTs helped
  encoder-decoder-era models, not LLMs.
- **Deep static analysis: not inside, and doesn't transfer in.** "Do Code LLMs Do Static
  Analysis?" (arXiv:2505.12118, 2025/EMSE 2026) **[search] [established] LIT-BACKED**:
  across GPT-4o/Gemini/CodeLlama/Jam, LLMs perform poorly on call-graph/AST/data-flow
  tasks, and pretraining on static-analysis tasks does **not** generalize to better code
  intelligence (nor vice versa). Related: LLMs are poor at *generating* data-flow graphs
  and ICL does not fix it **[search] [claimed]**.
- **Shallow deterministic facts in prompts still pay.** Automatic Semantic Augmentation
  of prompts (Ahmed et al., 2023/ICSE 2024, arXiv:2304.06815) **[search] [established]
  LIT-BACKED**: adding tagged, deterministically-derived facts (parameter/variable names,
  return expressions, simple pre/post-conditions, basic control/data flow) to
  summarization prompts gains ~2 BLEU across settings. The facts are cheap, exact, and
  rendered as *text* — Law 2-compatible.
- **Structured-format sensitivity (the structured-data analog of Brittlebench).** Tables:
  LLMs answer differently when the same table is serialized as Markdown/HTML/JSON
  (arXiv:2412.17189, 2024) **[search] [claimed]**. Agentic/SQL tasks across 11 models × 4
  formats: aggregate accuracy format-insensitive but per-model swings −7.7%…+2.7%, with
  capability dominating format ("Notation Matters", arXiv:2605.29676, 2026) **[search]
  [claimed]**. So input canonicalisation of structured data is motivated for *variance*,
  with the honest caution that the aggregate-accuracy effect may be small — mirror of the
  N-C3/L1a design and its strong null.

**§1.2 verdict.** The 2602.06671 parity result + 2505.12118 no-transfer result together
bound the encoder-side ambition: at LLM scale, handing the model a deterministic parse of
what it can already read is mostly redundant (absorption, again). The living input-side
cells are (a) *shallow-fact augmentation as text* and (b) *training-time grounding on
canonical forms* (IR/AST objectives) — both of which have kernel analogues (L1a
annotate-arm; F6/N-C2).

### 1.3 Grammar-, semantics-, and type-constrained decoding: the decoder-side wins

This is where deterministic parsing is *load-bearing in production* today:

- **PICARD** (Scholak et al., EMNLP 2021, arXiv:2109.05093) **[search] [established]
  LIT-BACKED**: incremental parser rejects inadmissible tokens during beam search;
  fine-tuned T5-3B goes from passable to SOTA on Spider/CoSQL; execution-error rate on
  Spider dev 12% → 2%.
- **Synchromesh** (Poesia et al., ICLR 2022, arXiv:2201.11227) **[search] [established]
  LIT-BACKED**: Constrained Semantic Decoding enforces syntax, scope, typing, and
  contextual logic for GPT-3/Codex on SQL/Vega-Lite/SMCalFlow, "effectively preventing
  run-time errors"; complementary to retrieval-side Target Similarity Tuning.
- **SynCode** (arXiv:2403.01632, 2024) **[search] [established] LIT-BACKED**: general CFG
  masking; removes 96.07% of syntax errors in generated Python/Go.
- **XGrammar** (arXiv:2411.15100, 2024) + **XGrammar-2** (arXiv:2601.04426, 2026)
  **[search] [established] LIT-BACKED**: adaptive token-mask caching + pushdown automata
  → up to 100× lower constraint overhead; near-zero-overhead structured generation in
  serving stacks. Constrained decoding is now effectively *free* at inference.
- **Type-constrained decoding** (Mündler et al., PLDI 2025, arXiv:2504.09246) **[search]
  [established] LIT-BACKED**: prefix automata + type inference enforce well-typedness
  (formalised on a simply-typed core, extended to TypeScript); compilation errors more
  than halved and functional correctness up on HumanEval/MBPP synthesis, translation,
  and repair, across families incl. >30B open-weight models; repair +37% relative. The
  strongest evidence that *semantic-level* deterministic constraints (beyond syntax)
  still pay at modern scale.
- **The two priced caveats.** (i) *Distribution distortion*: greedy grammar-masking
  produces grammatical-but-low-quality outputs whose likelihoods diverge from the LM's
  distribution; Grammar-Aligned Decoding/ASAp corrects toward the true
  grammar-conditioned distribution at extra sampling cost (NeurIPS 2024,
  arXiv:2405.21047) **[search] [established] LIT-BACKED**. (ii) *Format tax*: format
  restriction degrades reasoning (Tam et al., arXiv:2408.02442, 2024) **[search]
  [established]**; the 2026 follow-ups find the tax is real across open-weight models but
  largely recoverable by **decoupling reasoning from formatting** (freeform reasoning
  first, constrained re-encoding second, or extended thinking) ("The Format Tax",
  arXiv:2604.03616 **[search] [claimed]**) and argue residual failures track model
  capacity, not format per se ("Capacity, Not Format", arXiv:2606.09410 **[search]
  [claimed]**). Adjacent engineering: draft-conditioned constrained decoding
  (arXiv:2603.03305, 2026) **[search] [claimed]** implements exactly this two-stage shape.
- **Constrained emission of canonical identifiers.** GENRE (De Cao et al., ICLR 2021,
  arXiv:2010.00904) **[memory] [established]**: entity retrieval by constrained beam
  search over a prefix trie of entity *names* — the model never memorises IDs; decoding
  is confined to the registered name set and a deterministic name→ID map finishes the
  job. Directly relevant to the E4 emission null: hash-emission failed as a
  *training* target; trie-constrained *name* emission + exact mapping needs no training.

**§1.3 verdict.** Deterministic parsing injected at the **decoder** is the single most
successful "deterministic structure meets LLM" mechanism in the literature: measured,
large, cheap, and scale-robust — because it operates on the model's *output space*
(where validity is checkable) rather than asking the network to internalise foreign
structure. For the kernel this maps 1:1 onto P10-record emission, the L1b output leg,
L3c engine-in-decode, and the L3a closed query grammar.

### 1.4 The with-vs-without benchmark set

For any prereg in this thread, the measurement surfaces already exist:

- **Generation:** HumanEval (arXiv:2107.03374) / MBPP (arXiv:2108.07732) + EvalPlus
  test-strengthening (arXiv:2305.01210) **[memory]**; BigCodeBench (arXiv:2406.15877),
  LiveCodeBench (arXiv:2403.07974, contamination-controlled) **[memory]**.
- **Understanding/execution:** CRUXEval — 800 Python functions, input/output prediction;
  GPT-4 67%/63% pass@1 vs Code Llama 34B 47%/44% (arXiv:2401.03065, 2024) **[search]
  [established]**; CRUXEval-X multilingual **[search]**.
- **Multi-task legacy:** CodeXGLUE (arXiv:2102.04664) **[memory]** — where the §1.1
  small-model deltas live.
- **Repo-scale:** SWE-bench (arXiv:2310.06770) **[memory]** — where deterministic
  repo-structure (call graphs, imports) plausibly matters most and is least measured.
- **Robustness (the code Brittlebench):** ReCode (arXiv:2212.10264, ACL 2023) **[search]
  [established]** — 30+ semantics-preserving perturbations over docstrings, names,
  syntax, format; models most sensitive to syntax-class perturbations; MBPP harder than
  HumanEval under perturbation. This is the natural primary surface for a code/structured
  input canonicaliser (L1a-code), exactly as Brittlebench is for NL.
- **Text-to-SQL:** Spider (arXiv:1809.08887), BIRD (arXiv:2305.03111) **[memory]** — the
  historical home of constrained-decoding deltas.
- **Structured-data QA:** the table-serialization sensitivity sets of §1.2
  (arXiv:2412.17189; arXiv:2605.29676) **[search]**.

### 1.5 Kernel connections (incl. the Lean pipeline) — the honest mapping

- **The Lean precedent, stated at its true strength.** The programme's math route is a
  deterministic extractor over Mathlib (annotation-layer `lean-ref/1` records; sample of
  70 records, 0/70 parse errors on manual review — MEASURED, `docs/design-lean-route.md`
  2026-07-07; identity grounded in Metamath, not Lean, per `design-math-sector.md`). That
  is a *deterministic-front-end + canonical-record* pattern, proven at
  feasibility-sample scale — NOT an end-task win. Thread A says this pattern generalises
  to code with even better tooling (tree-sitter, compilers, type systems are the
  best-industrialised deterministic parsers in existence).
- **The occupied-seat caution (design-critical).** In the code domain, the Law-3
  deterministic-engine seat is **already occupied by incumbents**: compilers,
  type-checkers, test runners, static analysers. The measured wins of §1.3 belong to
  *those* engines. The kernel cannot out-compile a compiler; its marginal value in code
  must be at the **concept/semantic layer the incumbents don't own** — canonical
  cross-language concept identity (IRCoder's win hints this is real value), API/contract
  semantics as kernel records, NL↔code concept mapping — or in domains *without* an
  incumbent engine (which is exactly the NL/kot-axiom case F2/L3a already target).
  STIPULATED design opinion.
- **Where the with-vs-without experiment is genuinely open**: (i) deterministic
  canonicalisation of *input* code/tables against ReCode/table-sensitivity suites
  (variance endpoint — same shape as N-C3, nobody has run the deterministic arm);
  (ii) grammar/type-constrained emission of *kernel records* (P10) — engineering with
  established literature behind every component; (iii) canonical concept annotations on
  code (shallow-fact augmentation shape, 2304.06815) with kernel-versioned rather than
  ad-hoc facts.

---

## 2. THREAD B — symbolic inference between layers

### 2.1 The decode→symbolic→re-encode cell: occupants and near-occupants

- **The one direct occupant.** "Improving Rule-based Reasoning in LLMs via Neurosymbolic
  Representations" (arXiv:2502.01657, 2025) **[search] [claimed] LIT-BACKED (single
  group, unreplicated)**: trained encoder/decoder networks map an LLM hidden state (layer
  17 chosen by encoding-RMSE) into a **vector-symbolic (VSA) space**; structured values
  are extracted by querying the VSA vector; a *predefined rule-based function* computes
  the answer symbolically; the result is re-encoded and linearly merged 50–50 with the
  original hidden state at the intervention layer. Claims: 88.6% lower cross-entropy and
  ~15.4× more problems solved vs CoT prompting and LoRA on arithmetic/rule-following
  tasks, with no degradation elsewhere. Read with care: narrow task family, trained
  bridge both ways (Law-1-compliant but not training-free), single-group. This is
  nonetheless the closest existing system to the maintainer's Thread-B sketch, and its
  *shape* (exact symbolic compute on decoded structure, then re-injection) is precedent
  that mid-network symbolic offload is at least implementable.
- **The strong sibling outside LLMs.** **NVSA** (Hersche et al., Nature MI 2023,
  arXiv:2203.04571) **[search] [established] LIT-BACKED**: neural perception front-end +
  vector-symbolic algebra back-end doing probabilistic abduction over distributed
  representations; 87.7%/88.1% on RAVEN/I-RAVEN (then-record), with the VSA reasoning
  **two orders of magnitude faster** than explicit symbolic search — because rule
  evaluation happens *in the algebra* (binding/unbinding/bundling) rather than by
  enumeration. Successor **ARLC** (arXiv:2401.16024) learns abductive rules in the same
  algebra **[search] [claimed]**. Directly relevant to us: the kernel *is* a TPR/HRR
  algebra (construction B), so NVSA-style in-algebra rule evaluation is a candidate
  *implementation strategy for the kot-axiom engine itself* (L3a) — with one hard trap:
  VSA pipelines end in a **cleanup memory** that is a nearest-neighbour similarity
  lookup, which for kernel vectors is X3-banned; any kernel adoption must replace
  cleanup-by-similarity with exact content-hash lookup or a polarity-aware variant.
- **The grounding cautionary tale.** SATNet (differentiable MAXSAT layer, ICML 2019,
  arXiv:1905.12149 **[memory]**) claimed visual-Sudoku end-to-end; the NeurIPS 2020
  re-analysis showed **label leakage** — without leaked intermediate symbol labels,
  visual SATNet drops to 0%: the differentiable-logic layer never solved symbol
  grounding **[search] [established]**; partial fixes exist ("Techniques for Symbol
  Grounding with SATNet", NeurIPS 2021, arXiv:2106.11072 **[search] [claimed]**). Lesson
  for any between-layers symbolic module: the *interface* (do hidden states actually
  decode to the symbols the engine consumes?) is the failure point, and it must be
  instrumented (our P10 extraction-failure gate + E9-defl scramble discipline are the
  right controls). Same family: neurosymbolic reasoning-shortcut leakage
  (arXiv:2507.11357, carried from N0).
- **In-network differentiable logic at layer-scale** (DeepProbLog/Scallop/LTN/semantic
  loss) — surveyed in N0 §2.1 (NS-2/NS-3), unchanged this pass: real frameworks, module
  scale, never demonstrated as an *interleaved LLM layer* at generation time. The
  natural kernel uses remain external-engine (F2/L3a) and training-signal (N-C2).

### 2.2 The instrument layer: training-free read/write on mid-network state

Everything in this subsection is established, mostly training-free, and is what makes a
kernel inter-layer loop *implementable without touching the host's weights*:

- **Reading (decode-to-text).** **Patchscopes** (Ghandeharioun et al., ICML 2024,
  arXiv:2401.06102) **[search] [established] LIT-BACKED**: patch a hidden representation
  into a crafted inspection prompt and let the model itself verbalise what it encodes;
  subsumes logit-lens-style projection **[memory: nostalgebraist 2020]** and tuned lens
  (arXiv:2303.08112 **[memory]**); beats probing baselines on attribute extraction
  *without training examples*, works in early layers, and a stronger model can decode a
  weaker model's states. SelfIE (arXiv:2403.10949) **[memory] [claimed]** is the same
  idea framed as self-interpretation. This is the training-free "decode hidden state →
  inspectable text" primitive; our mapper + P10 extraction can then produce *exact*
  concept records from that text (no kernel-space similarity anywhere — X3-compliant).
- **Writing (model-native vectors, no training).** **Function vectors** (Todd et al.,
  ICLR 2024, arXiv:2310.15213) **[search] [established] LIT-BACKED**: a small set of
  attention heads carries a compact task representation; summing their outputs yields a
  vector that, added at middle layers, causally *triggers the task* in zero-shot
  contexts. Extraction = causal mediation over the model's own activations; injection =
  vector addition. Siblings: task vectors (arXiv:2310.15916 **[memory]**), in-context
  vectors (arXiv:2311.06668 **[memory]**), activation addition (arXiv:2308.10248
  **[memory]**), contrastive activation addition (arXiv:2312.06681 **[memory]**),
  representation engineering (arXiv:2310.01405 **[memory]**) — all [established] as a
  family: cheap, training-free, causally effective, moderate precision.
- **Targeted correctness effects.** **ITI** (Li et al., NeurIPS 2023, arXiv:2306.03341)
  **[search] [established] LIT-BACKED**: shifting activations along probe-found truthful
  directions in a few heads lifts Alpaca TruthfulQA 32.5% → 65.1% with a few hundred
  examples. The 2026 steering literature adds calibration-aware and transferable
  variants (e.g. CORAL, arXiv:2602.06022 **[search] [claimed]**) and — the honest
  counterweight — reliability audits showing steering-intervention evaluations are often
  fragile (arXiv:2410.17245 **[search] [claimed]**).
- **Layer-timing intervention.** **Back-patching** (Biran et al., EMNLP 2024,
  arXiv:2406.12775, "Hopping Too Late") **[search] [established] LIT-BACKED**: in 2-hop
  factual queries the bridge entity resolves in early-middle layers and the second hop
  begins too late to use it; patching a *later-layer* hidden state back into an
  *earlier* layer rescues up to 66% of failed cases (some back-patch exists that fixes
  the answer). This is a measured existence proof that **re-entering computed state at
  an earlier layer adds capability the frozen forward pass lacks** — the closest
  training-free relative of "symbolic inference between layers", using the model's own
  states (no foreign coordinates, Law-1-clean).
- **Concept-subspace editing.** LEACE (arXiv:2306.03819) / concept-whitening lineage —
  already tabulated with epistemic tags in `docs/next/kernel-introduction-schedule.md`
  (N1-S); carried, not re-argued. The S0 pilot's MEASURED warning binds here too: naive
  Procrustes-fit/cosine alignment metrics are inflated under the null; any
  "hidden-state↔kernel alignment" endpoint must use Gram-RSA-class relational statistics
  against null bands.

### 2.3 Latent-loop architectures and residual-stream reasoning (the trained end)

- **Coconut** (Hao et al., 2024, arXiv:2412.06769) **[search] [established]
  LIT-BACKED**: feed the last hidden state back as the next input embedding — reasoning
  steps in latent space with no decoded text; trained via curriculum; beats CoT on
  search-heavy logical tasks with fewer tokens, and encodes *parallel* candidate paths
  (breadth-first-like) per follow-up analysis; theory: "Reasoning by Superposition"
  (arXiv:2505.12514, 2025) **[search] [claimed]**. Survey of the (large, fast-moving)
  latent-CoT space: arXiv:2505.16782 **[search]**.
- **Recurrent-depth / looped transformers** (Geiping et al. 2025, arXiv:2502.05171
  **[memory: id; [search]-confirmed line]**; looped-transformer reasoning, Saunshi et
  al. 2025 **[search, id unverified]**): scale test-time compute by iterating a latent
  block; a 3.5B recurrent-depth model improves reasoning by looping. [established as a
  line].
- **Reading for our programme.** These prove the *capacity* claim — the residual stream
  can host multi-step, even parallel, reasoning without emitting tokens — and
  simultaneously the *cost* claim: every member trains the host, and the latent steps
  resist inspection (faithfulness concerns carried from L3 §4). For a training-free
  kernel these are **non-adoption boundary conditions**, with one architectural reading
  worth logging: Coconut's loop (hidden state → [something] → next input embedding) is
  topologically identical to the maintainer's Thread-B sketch with the symbolic engine
  replaced by identity. The kernel proposal = Coconut's wiring + a deterministic engine
  in the loop + no training — nobody has run that cell. EXTRAPOLATION.
- **Native latent multi-hop evidence** (why an inter-layer engine has something to work
  with): latent 2-hop reasoning exists but is unreliable and layer-timing-limited
  (arXiv:2402.16837 **[memory]**; arXiv:2406.12775 **[search]**); grokked transformers
  can implicitly reason (arXiv:2405.15071 **[memory]**). [established, mixed].

### 2.4 Feasibility verdict for the training-free, cosine-banned kernel

**The buildable loop (all parts established, composition unmeasured):**
(1) at a chosen layer/position, *read* state via patchscope decode (training-free) →
(2) mapper-exact concept identification on the decoded text (deterministic; abstains
out-of-lexicon; NO kernel-space kNN — X3 respected by construction) →
(3) kot-axiom engine computes/checks (deterministic, CPU, the L3a artifact) →
(4) *write back* one of: (a) text into the continuing context (weakest, safest — this
degenerates to L0/F2-with-early-exit); (b) a model-native steering/function vector
selected by exact concept-hash from a per-model cached dictionary (write-strength
medium); (c) a back-patch of a corrected/earlier-resolved state (strongest, riskiest).
Cost tier: 1–2 (inference-only, open-weights hosts, forward hooks); no training beyond
optional cached vector extraction, which is itself training-free causal-mediation
arithmetic. EXTRAPOLATION — flagged, not a premise.

**The five honest hazards:** (i) *extraction validity* — patchscope decodes are
themselves model behaviour, not ground truth (Faithful-Patchscopes documents bias in
hidden-state readouts, arXiv:2602.00300 **[search] [claimed]**); the P10
extraction-failure gate must cover step (1)+(2) jointly. (ii) *SATNet lesson* — if the
engine's inputs don't actually correspond to what the state encodes, the loop
manufactures confident nonsense; scramble/shuffled-kernel controls are mandatory.
(iii) *steering reliability* — the write-back channel's evaluation fragility is
documented (arXiv:2410.17245). (iv) *Law 2* — the same engine output delivered as plain
text at the model's *input* (i.e., F2's existing loop) is the null; the inter-layer
version must beat it at matched budget, and the only prior (2502.01657) never ran that
control. (v) *absorption* — any win is efficiency/auditability, not permanent residence.

**Maturity summary.** Instruments: mature. Trained bridges at depth: one unreplicated
occupant. Training-free composed loop with a deterministic engine: **empty, motivated
cell** — the genuinely new experiment Thread B licenses, at Tier-1–2 cost, sitting
between L0 (external verifier) and L2 (in-network layers) on the N1-A ladder.

---

## 3. Additional architectural ideas surfaced (beyond the two threads)

1. **Two-stage decouple as standing P10 discipline** — freeform reasoning → constrained
   re-encode recovers most of the format tax (arXiv:2604.03616; arXiv:2603.03305)
   **[search] [claimed]**: every kernel experiment that demands record output should
   carry a decoupled-emission arm, or the format tax will be misattributed to the kernel.
2. **Semantic-aware iterative decoding** (ITERGEN-class backtracking generation, grammar
   + semantic checks driving re-generation of spans, OpenReview 2024/25 **[search, id
   unverified] [claimed]**): a middle rung between L1b record-decode and L3c
   engine-in-decode — the engine *rejects mid-generation* and forces local backtrack.
3. **Kernel-canonical facts as prompt augmentation for code** (the 2304.06815 shape with
   versioned kernel records instead of ad-hoc facts) — cheapest Thread-A idea that is
   also Law-2-honest (facts enter as text; the kernel's delta is canonicality/versioning,
   measured against the same facts unversioned).
4. **IR-style paired-corpus grounding** (IRCoder shape): text ↔ canonical kernel-record
   pairs as a continued-pretraining corpus for small hosts — the concrete corpus recipe
   F6/N-C2 was missing; measured precedent at 1.1B–7.3B.
5. **VSA-algebra engine internals for kot-axiom** (NVSA shape, §2.1) — an
   *implementation* idea for L3a (speed), not a new seam; conditional on X3-safe cleanup.

---

## 4. Registry-ready idea entries

(Format per the architecture-advisor's registry: idea / slot / mechanism / epistemic tag
/ feasibility {cost tier, dependency-readiness} / key citation. Tags describe the
*evidence for the mechanism*, not for kernel benefit — kernel benefit is EXTRAPOLATION
in every row until a verdict exists.)

| # | Idea | Architecture+part slot | Mechanism | Epistemic tag | Feasibility | Key citation(s) |
|---|---|---|---|---|---|---|
| A1 | Structured-input canonicaliser for code/tables (L1a extended beyond NL) | L1a preprocessor (out-of-network); N-C3 sibling | tree-sitter/format parsers → one canonical surface form (format, identifiers, table serialization); endpoint = variance under ReCode/table-perturbation at accuracy non-inferiority | LIT-BACKED motivation (brittleness measured); kernel arm EXTRAPOLATION | Tier 1–2; HIGH readiness (parsers off-shelf, mapper exists, ReCode public) | arXiv:2212.10264 (2022); arXiv:2412.17189 (2024); arXiv:2605.29676 (2026) |
| A2 | Grammar+type-constrained P10-record emission with two-stage decoupling | P10 interface; L1b output leg; F2/E9 emission path; L3a query grammar | compile kot-record/kot-axiom grammars to XGrammar-class masks; freeform-reason-then-constrained-encode; kills extraction-failure risk at ~zero overhead | LIT-BACKED components (all measured); composition EXTRAPOLATION | Tier 1; HIGH readiness (XGrammar/SynCode OSS; P10 grammar exists) | arXiv:2109.05093 (2021); arXiv:2504.09246 (2025); arXiv:2411.15100 (2024); arXiv:2604.03616 (2026); arXiv:2405.21047 (2024, distortion caveat) |
| A3 | Trie-constrained concept-NAME emission + deterministic name→hash map (GENRE shape) | A1-emission seam replacement; E4's rescue; L3b router output | prefix-trie over registered lexicon constrains decoding; hashes never enter the model; exact post-map | LIT-BACKED mechanism; kernel use EXTRAPOLATION | Tier 1–2; HIGH readiness (lexicon exists) | arXiv:2010.00904 (2021) |
| A4 | Kernel-record paired-corpus grounding (IRCoder shape) for small hosts | F6 scaffolding / N-C2 arm (training-time) | continued pretraining on text↔canonical-record pairs; endpoints incl. prompt robustness (IRCoder's measured gain) | LIT-BACKED precedent at 1.1B–7.3B; kernel transfer EXTRAPOLATION | Tier 3; MEDIUM readiness (needs corpus build + training budget; POST-F2 gate) | arXiv:2403.03894 (2024); arXiv:2506.00204 (2025) |
| A5 | Code-domain world layer by deterministic CPG/call-graph extraction feeding the L3a engine | L3a/L3b engine, code vertical; FK-L3-2 route (a) | Joern/tree-sitter extraction → world-layer records; engine answers structure queries LLMs measurably fail at; division-of-labour claim | LIT-BACKED gap (LLMs poor at static analysis); engine-answer mechanism MEASURED-adjacent (deterministic tooling); kernel delta EXTRAPOLATION | Tier 0–1; HIGH readiness (CPU only) | arXiv:2505.12118 (2025); Yamaguchi et al. S&P 2014 [memory] |
| A6 | Kernel-canonical shallow facts as prompt augmentation (text, versioned) | L1a annotate-arm variant; Law-2-native | deterministic shallow facts rendered as text (the only input-side cell that still pays at LLM scale), kernel delta = canonical identity/versioning vs same facts ad-hoc | LIT-BACKED (+~2 BLEU precedent) ; kernel delta EXTRAPOLATION | Tier 1; HIGH readiness | arXiv:2304.06815 (2023) |
| B1 | Training-free inter-layer loop: patchscope-decode → mapper-exact concepts → kot-axiom engine → feedback (text / cached steering vector / back-patch) | NEW seam between L0 and L2 on the N1-A ladder ("L1.5 inner-verifier"); composes with F2 | all-established parts, §2.4; X3-safe by exact-match concept ID; nulls = F2-external loop at matched budget + shuffled-kernel + scramble | components LIT-BACKED; composition EXTRAPOLATION (empty cell) | Tier 1–2; MEDIUM readiness (needs forward-hook harness on open weights; engine = L3a artifact) | arXiv:2401.06102 (2024); arXiv:2406.12775 (2024); arXiv:2306.03341 (2023); caveat arXiv:2602.00300 (2026) |
| B2 | Kernel-keyed steering dictionary: concept-hash → per-model model-native function/steering vector (extracted once, cached, exact-hash addressed) | A2-adjacent injection channel WITHOUT trained adapter; write-channel of B1 | function-vector extraction by causal mediation over the model's own activations; injection = activation addition; kernel coordinates never enter the model (Law-1-clean) | LIT-BACKED mechanism; concept-scale coverage EXTRAPOLATION | Tier 2; MEDIUM-HIGH readiness | arXiv:2310.15213 (2023); arXiv:2312.06681 (2023) [memory]; reliability caveat arXiv:2410.17245 (2024) |
| B3 | VSA-algebra rule evaluation inside the kot-axiom engine (NVSA shape) with X3-safe cleanup (exact hash, never similarity) | L3a engine internals (implementation/efficiency, not a new seam) | evaluate sidecar rules by TPR/HRR binding/unbinding over kernel vectors; NVSA measured 100× cheaper than symbolic search on its domain | LIT-BACKED precedent (outside LLMs); kernel-algebra port EXTRAPOLATION; cleanup trap STIPULATED as blocking unless exact | Tier 0–1 (CPU); MEDIUM readiness (blocked on X3-safe cleanup design) | arXiv:2203.04571 (2022/NatMI 2023); arXiv:2401.16024 (2024) |
| B4 | Trained VSA/kernel bridge at depth (2502.01657 replication, kernel space replacing ad-hoc VSA; run the missing text-null control) | L2-family rung (trained-bridge cell, Law-1-compliant); sibling of L2a | trained encoder/decoder hidden-state↔kernel-space at one layer; symbolic compute; 50-50 merge back; MUST add engine-as-text-input null the original lacked | LIT-BACKED [claimed, single-group, unreplicated]; kernel variant EXTRAPOLATION | Tier 2–3; MEDIUM readiness (code released; POST-F2 gate advisable) | arXiv:2502.01657 (2025) |
| B5 | Back-patching diagnostic: are covered-slice failures layer-timing failures? (informs L2 placement + B1 write-channel choice) | instrument over N1-A L2 rungs; pre-experiment for B1 | replicate back-patch sweep on kernel-covered multi-hop slices; fraction-rescuable = ceiling estimate for inter-layer intervention value | LIT-BACKED method (measured up to 66% rescuable on general 2-hop) | Tier 1–2; HIGH readiness (open weights + hooks) | arXiv:2406.12775 (2024) |
| B6 | Coconut-wiring + deterministic engine + no training (the "latent loop with an engine in it" cell) — logged as the far ambition of B1, gated on B1 | horizon rung above B1; NOT proposed for prereg | Coconut's hidden-state→input-embedding loop with kot-axiom engine interposed; nobody has run the training-free variant | line LIT-BACKED (trained versions only); this cell EXTRAPOLATION, empty | Tier 2–3; LOW readiness (gate on B1 result) | arXiv:2412.06769 (2024); arXiv:2505.16782 (2025) |
| X1 | Boundary condition (non-adoption): serialized-AST/deep-static-analysis INPUT injection at LLM scale | closes cells in N0's map | parity/no-transfer measured; do not spend budget on AST-serialization input arms except as controls | LIT-BACKED negative | — | arXiv:2602.06671 (2026); arXiv:2505.12118 (2025) |

---

## 5. Capability-limited vs fundamental (the §7 method, applied)

- **Grammar-action decoders (TreeGen/TranX) displaced by token decoding + constraints**:
  capability-*obviated* — stronger LMs made token syntax a non-problem; the surviving
  deterministic role moved to the output filter. A stronger model does not resurrect
  AST-action decoding. [established pattern, our inference]
- **Encoder-side structure injection fading at scale**: same absorption mechanism as the
  KEPLM line (L3 §2) — the host learns the structure from raw text; fundamental as
  formulated, capability-obviated. What survives is structure in *objectives* (AST-FIM,
  IRCoder) — i.e., training-time scaffolding, which is exactly our F6-shaped cell.
- **SATNet's grounding failure**: fundamental for label-free trained-through grounding at
  that scale; NOT obviated by stronger hosts — but our design sidesteps it because the
  mapper/P10 interface is deterministic-by-construction rather than learned. The failure
  transfers to us only through the extraction-validity hazard (§2.4-i), which is
  measurable and gated.
- **Format tax**: partially capability-limited (closed frontier models resist it;
  "Capacity, Not Format") and largely *procedure-fixable* (two-stage decoupling) —
  neither fundamental nor a reason to avoid constrained record emission, provided the
  decouple arm is standard.
- **2502.01657's narrowness**: unknown — single-group; the missing text-null control is
  precisely what would separate "symbolic offload at depth is special" from "the engine's
  answer helps however delivered" (Law 2). Treat as motivation, never as a premise.

*Cross-references:* `reports/lit-llm-injection-priorart.md` (L3 laws);
`docs/next/arch-survey.md` (N0 §§2–4); `docs/next/architecture-ladder.md` (N1-A rungs
L1a/L1b/L2/L3); `docs/next/kernel-introduction-schedule.md` (N1-S §alignment-metric
discipline); `docs/design-lean-route.md` (deterministic Lean extraction, MEASURED
sample); `docs/design-constraint-layer.md` (kot-axiom/1); `docs/kernel-design-directives.md`
(binding; §1 no-semantic-web-legacy, §2 metric vector V, §4 forks, §6 stats).
