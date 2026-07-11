# P3-LR-FUSE — GNN–LLM fusion + neurosymbolic integration survey

- **Bead:** kernel-of-truth-s55r.7 (Phase-0 [LIT], Programme-3 revision 2, §5 table row P3-LR-FUSE;
  absorbs rev-1 P3-LR-NSA + P3-LR-GNN).
- **Author:** Fable (autonomous worker), 2026-07-11. **Revised 2026-07-11** per the independent
  GPT-5.6 review (`poc/gpt56-review/rev-FUSE-20260711b/`): attribution narrowed (G-Retriever
  ablation, Deceive-KG scope), units disambiguated (relative vs points), GraphToken headline
  restated baseline-free + KB SPOT-REFUTED conflict surfaced, KBLaM limitations demoted to
  UNVERIFIED, ledger statuses split (fetched ≠ verified), closure/novelty claims bounded to this
  non-systematic sweep, H-GNN-RET risk accounting corrected (nsk1 risk retained).
- **Deliverable pair:** this review + `docs/next/lit/FUSE.sources.jsonl` (one JSON per source).
- **Purpose (decision-oriented):** supply the empirical premise that `docs/next/lit/RAG.md` §7.4
  explicitly left OPEN ("GNN-to-LM fusion has no source in this ledger … P3-D-GNN's empirical
  premise stays open pending P3-LR-FUSE"), map the neurosymbolic field so any missing H-* family is
  surfaced, and audit — skeptically, under matched-resource accounting — what GNN–LLM fusion has
  actually beaten. Feeds P3-D-GNN (lead input) and P3-D-GU (co-input); §8 states the hand-off.
- **Epistemic discipline:** every empirical claim below carries a primary citation
  (venue + year + URL fetched 2026-07-11); anything I could not verify at source is marked
  **UNVERIFIED**. Load-bearing lines carry [MEASURED | STIPULATED | EXTRAPOLATION]. In this
  document MEASURED = a published number restated strictly from a source I fetched today, inside
  that paper's own envelope (it is the *authors'* measurement, not ours); EXTRAPOLATION = a
  cross-paper reading, direction-only, never a premise for a verdict; STIPULATED = a scoping or
  design decision made here.
- **Governance:** writes only this file + the sources JSONL; no KB ingest/embed, no registry or
  assumption mutation, no bd/git operations, no child agents.

---

## 0. Dedup — what already exists (surveyed first, built on, not duplicated)

- **Lit-KB (`kb/records/`, 551 records):** a scan over titles + full-record text finds ~36
  fusion/neurosymbolic-adjacent records, including the two anchor papers of this review already
  extracted in structured form (GraphToken `arxiv_2402.05862`, KBLaM `arxiv_2410.10450`,
  AtlasKV `arxiv_2510.17934`), the KEPLM-era lineage (ERNIE `arxiv_1905.07129`, KnowBERT
  `arxiv_1909.04164`, K-Adapter `arxiv_2002.01808`), soft-prompt infrastructure
  (`arxiv_2104.08691`), Logic-LM `arxiv_2305.12295`, and assorted applied-neurosymbolic entries.
  Per the KB honesty boundary (`docs/next/literature-kb.md` §0) those records are **recall
  infrastructure, not evidence** — every load-bearing claim below was re-verified at its primary
  venue today; nothing here is ingested back. [STIPULATED: dedup protocol]
- **`reports/lit-llm-injection-priorart.md`** (2026-07-08) — the channel-level prior-art review.
  Its **interface-locality law** ("the representation crossing into the model is text, the model's
  own activations, or vectors through a *trained* projector — no working system feeds a foreign
  fixed coordinate system raw") and its KEPLM-line verdict ("dead at BERT scale with probes
  showing only marginal knowledge actually integrated") are inherited, not re-derived. This review
  covers what that one deliberately did not: the **GNN-side** of the seam (what the graph encoder
  buys), the **fusion-vs-text-serialisation** evidence, matched-baseline accounting, and
  relational-benchmark practice.
- **`docs/next/lit/RAG.md`** (2026-07-11, P3-LR-RAG) — graph-*retrieval* systems (GraphRAG,
  HippoRAG, MiniRAG). Its scope limit is this review's mandate: "every graph source in this ledger
  concerns graph-based retrieval/indexing … none studies GNN-to-LM fusion vs text serialisation."
  §4 and §8 below answer exactly that open item.
- **`docs/next/lit/EVAL.md`** + `reports/lit-eval-benchmarks.md` — CLUTRR as a *benchmark
  selection* (D4, generator-pinned, CC-BY-NC-4.0 licence constraint). This review uses CLUTRR as
  *methodological precedent* (text-vs-graph input arms, depth splits), not as an index choice.
- **Internal evidence this review must stay consistent with:** `docs/next/feasibility-synthesis.md`
  §0 (the nsk1 lesson: internal delivery reached ECHO grade while integration into behaviour was
  unresolved; text-delivered grounding measured net-harmful) and
  `docs/next/programme-3-neurosymbolic-architecture.md` §3.2 (H-GNN-{ST,KV,LF} designs, the
  rescoped falsifier, ASM-0805). [MEASURED: repo-internal, each within its own envelope]

**What this review adds over all of the above:** the fusion-lineage field map (§2), the
matched-accounting audit of fusion wins (§3), the fusion-vs-serialisation evidence including
size/depth dependence (§4), graph-encoder scaling and depth limits (§5), relational-benchmark
practice (§6), and the P3-D-GNN hand-off (§8).

---

## 1. Field map — taxonomies, and where the H-* families sit

**The canonical integration taxonomy** is Kautz's six-type scheme from the AAAI Robert S.
Engelmore Memorial Lecture ("The third AI summer", *AI Magazine* 43(1):105–125, 2022, DOI
10.1002/aaai.12036, https://onlinelibrary.wiley.com/doi/abs/10.1002/aaai.12036). **UNVERIFIED at
primary today**: the Wiley full text returned HTTP 402 on fetch; the bibliographic record is
confirmed via the Wiley listing, but the six type-definitions below are restated from widely
consistent secondary sources and must not be quoted as verbatim Kautz: (1) symbolic-in/symbolic-out
neural processing (standard deep NLP); (2) Symbolic[Neuro] — a symbolic solver with neural
subroutines (AlphaGo-style); (3) Neuro | Symbolic — a neural perception module coupled to a
symbolic reasoner via I/O; (4) Neuro:Symbolic → Neuro — symbolic knowledge compiled into training;
(5) Neuro_Symbolic — logic tensorised into the network; (6) Neuro[Symbolic] — full combinatorial
reasoning engines embedded inside the network.

- Field statistics: the PRISMA systematic review of 2020–2024 neurosymbolic work (Colelough &
  Regli, arXiv:2501.05435, fetched; 1,428 papers screened → 167 analysed) finds research
  concentrated in learning-and-inference (63%), knowledge representation (44%), logic-and-reasoning
  (35%), with explainability/trustworthiness at 28% and meta-cognition at 5% — i.e. the field's
  own centre of mass is training-time integration, not the runtime-checker shape the programme
  builds [MEASURED]. The "third wave" agenda paper (Garcez & Lamb, arXiv:2012.05876, fetched;
  journal venue not verified today) frames the same gap as sound reasoning + interpretability
  atop learned representations [MEASURED, abstract-level].
- **The graph-specific taxonomy** the fusion literature itself uses: Jin et al., "Large Language
  Models on Graphs: A Comprehensive Survey" (IEEE TKDE 2024, https://arxiv.org/abs/2312.02783,
  fetched) — scenarios {pure graphs, text-attributed graphs, text-paired graphs} × roles
  {LLM-as-Predictor, LLM-as-Encoder, LLM-as-Aligner} [MEASURED].

**Placement of the programme's families** [STIPULATED — my mapping, confers no evidence]:
H-VL (external verifier loop) is Kautz type-3-shaped; H-GNN-ST/KV/LF are all
"LLM-as-Predictor over text-attributed graphs" in Jin's scheme, with the kernel+world layer as
the graph; H-RULE-CD is type-2/3 (engine-derived continuation sets delivered by masking);
H-RULE-HL aims at type-6, which the ladder already defers (§3.3 ruling). The kernel programme's
distinctive cell — a *deterministic, training-free, provenance-carrying* engine as the symbolic
half, with the store versioned externally — is thinly populated in both taxonomies; the fusion
literature almost universally trains the symbolic-side interface (§2–§3), consistent with the
injection report's interface-locality law.

---

## 2. The four fusion lineages (GraphToken / KBLaM / graph-adapter, plus their ancestor)

### 2a. Weight-fusion era (KEPLM: ERNIE → KnowBERT → K-Adapter), 2019–2021

ERNIE (Zhang et al., ACL 2019, https://aclanthology.org/P19-1139/, fetched) fused KG entity
embeddings into BERT-class encoders and "achieves significant improvements on various
knowledge-driven tasks, and meanwhile is comparable with … BERT on other common NLP tasks"
[MEASURED]. The lineage verdict is inherited from `reports/lit-llm-injection-priorart.md`: the
KEPLM line stalled at BERT scale, with probing work showing only marginal knowledge actually
integrated [MEASURED: repo-internal, that report's §1]. Decision relevance: this is the ancestor
of "weld the structure into the weights" — the shape the programme already deprioritised (H-RULE-HL
last in the placement order).

### 2b. GNN–LM co-attention era (QA-GNN → GreaseLM → DRAGON), 2021–2022

- **QA-GNN** (Yasunaga et al., NAACL 2021, https://aclanthology.org/2021.naacl-main.45/, fetched):
  LM-scored KG node relevance + a joint QA-context/KG graph updated by message passing; improves
  over fine-tuned LMs and prior LM+KG models on CommonsenseQA/OpenBookQA; handles negation more
  robustly [MEASURED, qualitative at abstract level].
- **GreaseLM** (Zhang et al., ICLR 2022, https://arxiv.org/abs/2201.08860, fetched incl. results):
  multi-layer bidirectional fusion between LM token states and GNN node states. The deltas, from
  the paper: CommonsenseQA 74.2% vs fine-tuned RoBERTa-Large 68.7% (**+5.5**) and vs QA-GNN 73.4%
  (**+0.9**); OpenBookQA 84.8% vs AristoRoBERTa 78.4% (**+6.4**) and vs QA-GNN 82.8% (**+2.0**);
  ConceptNet subgraphs pruned to top-200 nodes per example [MEASURED]. Note the shape: the big
  step is *any* KG machinery over the bare LM; the *fusion-architecture* increment over the prior
  KG method is ≤2 points.
- **DRAGON** (Yasunaga et al., NeurIPS 2022, https://arxiv.org/abs/2210.09338, fetched):
  self-supervised bidirectional text-KG pretraining (MLM + link prediction); **+5% absolute
  average** over prior LM and LM+KG models, and notably **+10% on questions involving long
  contexts or multi-step reasoning** [MEASURED] — the single best published hint that the fusion
  advantage grows with reasoning depth (§4).
- **The era's skeptic anchor:** "Learning to Deceive Knowledge Graph Augmented Models via Targeted
  Perturbation" (Raman et al., ICLR 2021 — venue per the OpenReview/proceedings listing, fetch of
  the forum blocked today; claims verified at https://arxiv.org/abs/2010.12872): an RL policy (or
  simple heuristics) produces perturbed KGs that "maintain the downstream performance of the
  original KG while significantly deviating from the original KG's semantics and structure",
  raising "doubts about KG-augmented models' ability to reason about KG information" [MEASURED].
  Scope, stated precisely: the perturbations are **learned/heuristic targeted** ones, not the
  programme's uniform shuffled-edge control, and the models tested are earlier KG-augmented
  QA/recommendation models — GreaseLM and DRAGON postdate the paper and were not tested. What it
  supports: for some KG-augmented models, performance can survive substantial semantic/structural
  perturbation of the KG, so a KG-perturbation control has published bite and content-attribution
  cannot be assumed for this lineage. What it does not support: that the uniform shuffle passes,
  or that the GreaseLM/DRAGON wins specifically are unattributed to graph content — that remains
  an open attribution question the §3.2 controls exist to answer.

### 2c. Frozen-LLM soft-token era (GraphToken → G-Retriever / GNP / GraphPrompter; GraphGPT, LLaGA), 2024–

- **GraphToken** ("Let Your Graph Do the Talking", Perozzi et al., arXiv:2402.05862, fetched; **no
  peer-reviewed venue verified today** — treat as arXiv): a GNN trained against a *frozen* LLM
  emits soft tokens replacing text serialisation of the graph. The abstract's headline is
  "across the board improvements — up to 73% points — on node, edge and graph-level tasks from
  the GraphQA benchmark" — **the abstract does not name the baseline for that headline figure**;
  the verified table-level fragments are e.g. edge existence 0.738 vs soft-prompt 0.544, node
  degree 0.962 vs soft-prompt 0.098, cycle check 0.956 vs zero-shot 0.760 (Table 1). Trainable
  side: GNN encoder body 17K–199K params plus a **~11M-parameter projector** [MEASURED].
  **Audit-conflict disclosure:** the repo's KB spot-audit (`kb/eval/spot-audit-2026-07-09.json`)
  marked the KB record `arxiv:2402.05862` **SPOT-REFUTED** precisely for assigning the 73-point
  headline to a soft-prompt baseline the paper does not support; this review restates the
  headline baseline-free for the same reason. This is the direct published precedent for
  **H-GNN-ST** and for the E5/A2 adapter seam.
- **G-Retriever** (He et al., NeurIPS 2024, https://arxiv.org/abs/2402.07630 + poster page
  fetched): subgraph retrieval via Prize-Collecting Steiner Tree + GNN soft prompt over a frozen
  or LoRA-tuned LLM. Frozen-LLM gains vs prompt tuning (units stated explicitly): ExplaGraphs
  0.8516 vs 0.5763, SceneGraphs 0.8131 vs 0.6341, WebQSP Hit@1 70.49 vs 48.34 — the paper's
  28.23–47.77% figures are **relative** improvements; in absolute terms +17.9 to +27.5 accuracy
  points and +22.15 Hit@1 points. With LoRA the deltas shrink to +1.95%/+11.74%/+10.44%
  (relative). Ablations (WebQSP Hit@1, from 70.49): removing the graph encoder → 54.62 (−22.51%
  relative, −15.87 pts); removing the *textualized graph* → 56.96 (−19.19% relative, −13.53 pts).
  The paper frames these as **complementary representation components**, and that is all the
  ablation shows: **component contribution, not causal use of topology** — the graph encoder also
  consumes textual node/edge attributes, and no edge/label shuffle is run in this ablation.
  Retrieval slashes input size (tokens −83% to −99%) [MEASURED]. Datasets span 5-node
  (ExplaGraphs) to ~1,371-node average graphs (WebQSP).
- **GNP** (Graph Neural Prompting, Tian et al., AAAI 2024, https://arxiv.org/abs/2309.15427 + HTML
  fetched): GNN + cross-modality pooling + projector as a plug-in prompt for FLAN-T5-xl class
  models; **+13.5% average over prompt tuning with the LLM frozen, and +1.8% over plain LoRA when
  tuned — both RELATIVE improvements** across six commonsense/biomedical datasets. In absolute
  aggregate accuracy (Table 1): 68.55 → 77.84 for the 11B host (**+9.29 pts**) and 65.95 → 74.36
  for the 3B host (**+8.41 pts**) [MEASURED]. Same shrinking-delta shape as G-Retriever.
- **GraphPrompter** ("Can we Soft Prompt LLMs for Graph Learning Tasks?", Liu et al., WWW 2024
  short, https://arxiv.org/abs/2402.10359, fetched): GNN-as-soft-prompt validated on node
  classification/link prediction [MEASURED, qualitative].
- **Instruction-tuned cousins:** GraphGPT (Tang et al., SIGIR 2024, https://arxiv.org/abs/2310.13023,
  fetched) — dual-stage graph instruction tuning + graph-text projector, strong zero-shot transfer
  claims; LLaGA (Chen et al., ICML 2024, PMLR v235:7809–7823, fetched) — notably achieves its
  cross-dataset generality with structure-aware node *sequences* + a projector and **no GNN at
  all** [MEASURED] — evidence that some of what the "graph encoder" buys is delivered by ordering
  templates + a trained projector alone.
- **The era's skeptic anchor:** "Revisiting Graph-Tokenizing Large Language Models: A Systematic
  Evaluation of Graph Token Understanding" (Zhang et al., arXiv:2605.03514, HTML fetched; venue
  stated as ICML 2026 on the page — **UNVERIFIED against the ICML programme today**): graph-token
  LLMs "do not fully understand graph tokens" — performance drops up to ~50% under instruction
  rephrasing and below 10% on content-level variants; under PRBCD structural attack the
  text-carrying models are "almost unchanged" while a GCN baseline collapses (−73.65%) — i.e. the
  fused models were **reading the text, not the structure**; yet probes show the graph tokens
  *contain* task-relevant structural signal (link prediction from graph tokens ≈ from original
  embeddings) that the LLM fails to use [MEASURED]. This is the published, field-level version of
  the programme's own nsk1 lesson — **delivery ≠ integration** — measured on exactly the H-GNN-ST
  architecture class.

### 2d. KV-injection lineage (KBLaM → AtlasKV) — the H-GNN-KV / H-RULE-KV precedent

- **KBLaM** (Wang et al., ICLR 2025,
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/803485352e61e3ebf41221e4776c9fd4-Abstract-Conference.html,
  fetched): KB triples → continuous KV pairs via a pre-trained sentence encoder + **trained linear
  adapters**, read through rectangular attention; overhead **linear** in KB size (vs quadratic for
  in-context); >10K triples into an 8B LLM with an 8K window on one A100; dynamic KB updates
  without retraining; retrieval-free; interpretable attention over records [MEASURED]. Named
  limitations — precision decays as triple count grows (models start refusing), degradation on
  out-of-distribution KBs (Enron), and answers can be reworded or wrong when the deployment KB
  differs from the (synthetic) instruction-tuning KB — are restated from secondary sources
  (repo documentation and reviews) that were not individually cited, and were NOT re-verified in
  the paper body today: **UNVERIFIED**, direction-only, do not build on the specifics.
- **AtlasKV** (Huang et al., **ICLR 2026** — venue confirmed 2026-07-11: camera-ready on
  OpenReview (forum id 6i1jVAYbHs) and listed in the iclr.cc 2026 materials, upgraded from the
  earlier "stated on arXiv page" status; https://arxiv.org/abs/2510.17934, fetched): scales the
  same KV shape to **billion-triple KGs under ~20GB VRAM** via KG2KV + HiKVP hierarchical
  pruning, "sub-linear time and memory", no external retriever, no retraining for new knowledge
  [MEASURED, abstract-level].
- Decision relevance: the L2b / H-GNN-KV / H-RULE-KV seam has a live, scaling lineage — but note
  **every member trains the bridge** (linear adapters instruction-tuned on KB-QA data), and the
  reported KBLaM failure modes (OOD KB → refusal drift / rewording; UNVERIFIED at primary, per
  above) are, if accurate, exactly the fail-open behaviours the kernel's fail-closed discipline
  exists to prevent. No training-free KV injection precedent
  was found — the interface-locality law holds in this lineage too [EXTRAPOLATION, absence-claim
  within this sweep].

### 2e. Adjacent, for completeness

**GNN-as-retriever** (structure consumed *before* the boundary, text crosses it): GNN-RAG
(Mavromatis & Karypis, arXiv:2405.20139, fetched; no peer-reviewed venue verified today): a GNN
reasons over a dense KG subgraph, extracts candidate reasoning paths, verbalises them, and a
tuned 7B LLaMA2 reasons over the text — matches or exceeds GPT-4 on WebQSP/CWQ KGQA, with
**+8.9–15.5 points on multi-hop and multi-entity questions** [MEASURED]. Architecturally this is
*not* fusion: no vector crosses the model boundary, so it avoids the graph-token-specific
delivery-integration risk (the GTEval failure mode) — but it delivers grounding as **text**, so
it fully retains the nsk1 text-channel risk (§8 row 2). §8 proposes it as a candidate variant
under RAG/executor controls.

---

## 3. What actually beat MATCHED baselines — the accounting audit

The bead's central skeptical question. Ledger per headline [each row MEASURED from the §2 source;
the audit reading is EXTRAPOLATION]:

| Headline win | Baseline it beat | What was matched | What was NOT matched | Does structure-causality survive? |
|---|---|---|---|---|
| GreaseLM +5.5 CSQA | fine-tuned RoBERTa-L | base LM, task data | +GNN params, +KG access, +retrieval machinery | Deceive-KG (on *earlier* KG-augmented models, under *targeted* perturbation — GreaseLM itself untested) shows content-attribution cannot be assumed for this lineage → **unestablished**, not disproven |
| GreaseLM +0.9/+2.0 | QA-GNN (same KG, same LM) | LM, KG, subgraph budget | fusion-layer params (small) | the honest *architecture* increment: ≤2 pts |
| DRAGON +5 avg, +10 multi-step | RoBERTa + prior LM+KG | task data | +KG-linked *pretraining* compute (large, uncharged) | pretraining-compute confound; depth signal is real but envelope-bound |
| GraphToken "up to 73% points" (headline, quoted verbatim) | **not identified in the abstract** — headline stated baseline-free; verified table fragments are vs soft-prompt and zero-shot (Table 1) | LLM (frozen), graph information | +trained GNN+projector (trained *on the task distribution*); baselines untrained | headline baseline unattributable (the KB record claiming otherwise was SPOT-REFUTED); **training-compute-unmatched**; tasks are algorithmic GraphQA, tiny graphs |
| G-Retriever frozen +28.2–47.8% *relative* (+17.9–27.5 pts, +22.15 Hit@1 pts absolute) | prompt tuning (trained soft prompt, same task data) | trainable-prompt shape, task data, frozen LLM | GNN+projector params > prompt params; retrieval step | closest to matched in the sweep; ablation shows graph encoder −22.5% / text graph −19.2% (relative) → **component contribution only** — encoder also reads textual attributes, no topology shuffle run |
| GNP +13.5% *relative* frozen (+8.4/+9.3 pts absolute) | prompt tuning | frozen LLM, task data | GNN+projector params; KG access | same shape; +1.8% relative over LoRA when tuned — the delta nearly vanishes once the host adapts |
| KBLaM linear-scaling | in-context text of the same KB | knowledge content | KBLaM adds instruction-tuned adapters; ICL pays quadratic attention | the win is **cost-shape**, not accuracy; accuracy-decay-with-KB-size and OOD reports are secondary-level (UNVERIFIED, §2d) |
| GNN-RAG ≈ GPT-4 (7B) | GPT-4 zero/few-shot; prior KGQA retrievers | benchmark | tuned 7B + KG access vs closed-book GPT-4 — classic unmatched-substrate comparison | cost story favourable but not a fusion-causality result |

**Audit verdict** [EXTRAPOLATION, direction-only — this sweep, not a systematic search]:

1. **No GNN-fusion result found in this sweep beats a matched baseline under full accounting**
   (same information, same trainable-parameter budget, same training compute, structure-causality
   demonstrated by perturbation). The two published perturbation probes both raise doubt *against*
   assuming the structure channel: Deceive-KG (earlier KG-augmented models, targeted perturbation)
   and GTEval's PRBCD result (soft-token era). Neither runs the programme's uniform shuffle;
   neither *settles* attribution — they show it has never been established.
2. The **recurring delta pattern**, in consistent units: relative gains of **+13.5% to +47.8%**
   over frozen-host prompt-tuning baselines (absolute: **+8.4 to +27.5 accuracy points**, +22.15
   Hit@1 points; GraphToken's baseline-free headline "up to 73% points" on algorithmic GraphQA
   sits outside this matched set), shrinking to **+1.8% to +11.7% relative** once the host is
   allowed LoRA — i.e. much of the fusion win is "someone finally trained something on this task
   distribution".
3. The strongest defensible positives for the H-GNN bet: (a) G-Retriever's dual ablation — on a
   1.4k-node-average KGQA task, removing *either* the graph-encoder channel or the text channel
   costs double-digit relative Hit@1, so the trained soft-token channel demonstrably carries
   **useful learned signal** at scale — though as component contribution only: it does not show
   the signal is *structural/topological* (the encoder also reads textual attributes; no shuffle
   was run) [MEASURED]; (b) DRAGON's +10 on multi-step questions [MEASURED,
   pretraining-confounded]; (c) GNP/GraphToken confirming the trained-bridge seam works
   frozen-host (the E5/A2 replication at field level).
4. For P3-D-GNN this settles the *control design* (§6) and hardens ASM-0805's status as
   EXTRAPOLATION: the family's empirical premise is **plausible, unproven in the literature, and
   twice undercut by causality probes** — the §3.2 sweep is a genuine experiment, not a
   replication. [STIPULATED: adopted as this review's core decision input]

---

## 4. Fusion vs text serialisation — measured results, and graph-size / reasoning-depth dependence

**What text serialisation can and cannot do (the control arm's own literature):**

- Serialisation choice is a first-order variable: encoding function, task, and **graph structure
  itself** all shift LLM graph-reasoning accuracy, with the right encoder worth **+4.8% to
  +61.8%** depending on task (Talk like a Graph, Fatemi et al., ICLR 2024,
  https://arxiv.org/abs/2310.04560 + ICLR poster page fetched) [MEASURED]. A text-arm control
  built on one arbitrary serialisation is a strawman; the control must be serialisation-optimised.
- LLMs have real but brittle graph ability: on NLGraph (Wang et al., NeurIPS 2023 spotlight,
  https://arxiv.org/abs/2305.10037, fetched), 29,370 problems / 8 tasks — LLMs sit 37–58% above
  random on easy tasks (connectivity, cycle, shortest path), but **the benefit of advanced
  prompting diminishes on more complex problems**, and models are "brittle to spurious
  correlations in graph and problem settings"; Build-a-Graph / algorithmic prompting recover only
  +3.07–16.85% [MEASURED].
- LLM graph reasoners are not invariant to meaning-preserving re-serialisation (node reindexing,
  edge reordering, format): "Lost in Serialization" (Herbst et al., arXiv:2511.10234, fetched;
  page states ICML 2026 GFM workshop) — larger non-fine-tuned models are more robust; fine-tuning
  reduces label sensitivity but *increases* structural/format sensitivity and does not reliably
  transfer to unseen tasks [MEASURED].

**What fusion adds over serialisation, where measured:** GraphToken's headline "up to 73% points"
is stated **baseline-free** in the abstract (the earlier attribution to serialised-graph prompting
was the exact error the KB spot-audit refuted — see §2c); the verified fusion-vs-baseline
fragments are the Table 1 comparisons vs soft-prompt and zero-shot, *on algorithmic tasks over
small synthetic graphs* [MEASURED]; G-Retriever's ablation gives the cleanest same-system
decomposition available — both components contribute double-digit relative Hit@1 on the
large-graph dataset — but it is a **component-contribution** result, not a topology-causality
one (§2c) [MEASURED]; GTEval shows the same architecture class leaning on text when both are
present (§2c) [MEASURED].

**Size dependence — what exists:** the text-side ceiling degrades as graphs grow (NLGraph
complexity gradient; context-window arithmetic — WebQSP graphs average ~1,371 nodes and
G-Retriever's retrieval cuts input tokens by up to 99% *before* any fusion happens) [MEASURED].
The fusion-side evidence at size is confounded: G-Retriever "scales well with larger graph sizes"
but its gain bundles retrieval + soft tokens; no source isolates the encoder at size.

**Depth dependence — what exists:** three direction-consistent fragments, none a sweep:
CLUTRR's paper-era result — a GAT over *symbolic* graph inputs beats BERT/MAC over text on
systematic generalisation to longer clause lengths and on noise robustness (Sinha et al.,
EMNLP-IJCNLP 2019, https://aclanthology.org/D19-1458/, fetched) [MEASURED]; DRAGON's +10 on
multi-step/long-context questions [MEASURED]; GNN-RAG's +8.9–15.5 concentrated on multi-hop /
multi-entity questions [MEASURED].

**The load-bearing conclusion for P3-E-GNN-1** [EXTRAPOLATION, direction-only]: the literature
supports "structure pays increasingly with reasoning depth, and text serialisation degrades with
graph size" as a *hypothesis with scattered, confounded support* — CLUTRR (input-modality, not
fusion), DRAGON (pretraining-confounded), GNN-RAG (retrieval, not fusion). **No published
matched-information size×depth sweep of GNN-fusion vs optimised text serialisation surfaced in
this bounded, purposive 26-source sweep** — this extends RAG.md §7.4's open item to the
fusion-side literature, but a non-systematic search cannot *establish* the negative: treat the
§3.2 sweep as having **no prior found**, not as confirmed-novel, and power it as a first
measurement either way.
The rescoped falsifier (kill only on a flat-or-text-favouring curve across the whole sweep) is
well-aimed: tiny-graph text wins are exactly what GraphQA-class results predict, and a
depth-increasing fusion advantage is exactly what the three fragments hint at.

---

## 5. Graph-encoder scaling at small sizes, and the GNN's own depth ceiling

- **Encoders are small relative to their PUBLISHED hosts — not relative to R-0.** GraphToken
  trains a 17K–199K-param GNN body plus a **~11M-param projector** against a frozen PaLM-2-class
  LLM [MEASURED]; GreaseLM's whole KG side operates on ≤200-node subgraphs of a
  799,273-node/2.5M-edge ConceptNet [MEASURED]. Against a multi-billion-param host, 11M is
  negligible; against Programme-3's R-0-scale host (~135M) an 11M projector is **~8% of the host
  — material, and must be booked per-arm in KOT-SIZE/2 accounting**, alongside the two other
  ledger items that matter: the trained-bridge training compute and the store itself
  [EXTRAPOLATION].
- **Scaling behaviour differs from NLP.** On graph models up to 100M params / 50M samples, model
  *depth* matters for scaling beyond raw parameter count, and data volume is better measured in
  nodes/edges than in graph count (Liu et al., "Towards Neural Scaling Laws on Graphs",
  https://arxiv.org/abs/2402.02054, fetched; arXiv-only — no venue verified) [MEASURED]. Directly
  usable for the H-GNN encoder sweep: vary depth deliberately, count data in edges.
- **The depth ceiling is real and named: over-squashing.** Message passing compresses an
  exponentially growing receptive field into fixed-size vectors, so GNNs "fail to propagate
  long-range information"; GCN/GIN suffer more than attention-based GNNs; relieving the bottleneck
  improves long-range tasks without extra parameters (Alon & Yahav, ICLR 2021,
  https://arxiv.org/abs/2006.05205, fetched) [MEASURED]. Decision consequence [STIPULATED]: the
  §3.2 sweep's deep-composition cells must include a **GNN-capability control** — verify the graph
  encoder can solve the depth-d cell *symbolically* (GNN-alone probe) before attributing a
  fusion-arm failure at depth d to the fusion seam; otherwise a real fusion effect is masked by an
  encoder that over-squashes. The kernel+world graph's typed, sparse, tree-ish structure is the
  favourable case, but that is an expectation, not a measurement.

---

## 6. Relational-benchmark practice — and the control set the literature validates

**Benchmark practice worth adopting** (selection itself is EVAL.md's settled ground; this is
*practice*):

1. **Procedural generation with a depth dial.** CLUTRR: kinship stories generated at parametric
   clause length k, with systematic splits (held-out rule combinations) and curated noise facts;
   its headline finding is itself a modality result (GAT-over-symbolic-graphs ≫ BERT/MAC-over-text
   on generalisation + robustness) [MEASURED]. RuleTaker: rule/fact theories at controlled
   inference depth; 99% at trained depths, 95%+ transfer to greater depths, zero-shot transfer to
   hand-authored rulebases (Clark et al., IJCAI 2020, https://arxiv.org/abs/2002.05867, fetched)
   [MEASURED]. GraphQA/NLGraph: task difficulty + graph-structure gradients for pure-structure
   reasoning [MEASURED]. Adopt: generator-pinned, depth-stratified, contamination-safe-by-refresh
   item production for the D4 legs — plus the licence caveat (CLUTRR CC-BY-NC-4.0,
   `reports/lit-eval-benchmarks.md`).
2. **Input-arm factorials.** CLUTRR's text-vs-symbolic-graph arms are the direct precedent for the
   §3.2 oracle-subgraph vs NL-extracted-subgraph factorial [MEASURED → STIPULATED adoption].
3. **Perturbation controls with teeth.** The literature validates every §3.2 pre-registered
   control and adds two:
   - *Shuffled edges/relations*: Deceive-KG is precedent that KG-perturbation controls **can pass
     while the semantics are destroyed** — measured under *targeted* (RL/heuristic) perturbation
     on earlier KG-augmented QA/recommendation models; the uniform shuffle itself is untested
     there [MEASURED, scope as stated]. A fusion win that survives the shuffle is thereby
     *dis*-confirmed as a structure win; pre-registering it as a kill is correct and the
     perturbation-control family has published bite.
   - *Structural adversarial attack (PRBCD-style)*: GTEval's cheap "does it read structure at
     all" gate — if attacking topology leaves the fused arm unchanged, the arm is reading text
     [MEASURED → STIPULATED: add as a Stage-4 instrument to the §3.2 four-stage decomposition].
   - *Serialisation-invariance battery for the text arm*: report the text control across
     serialisation variants (Lost in Serialization; Talk-like-a-Graph encoder set) so the text arm
     is its *best* self, not a strawman [STIPULATED].
   - *Probe-vs-use separation*: GTEval's link-prediction-from-graph-tokens probe is exactly the
     "delivery probe" of the nsk1 protocol; the literature now independently shows delivery
     without behavioural use in this architecture class — the causal behavioural endpoint stays
     primary [MEASURED → STIPULATED].
   - *Parameter-parity prompt control*: trained soft prompt of equal parameter count *without*
     graph input (the GraphToken/G-Retriever/GNP baseline practice, upgraded to parameter-matched)
     [STIPULATED].
4. **Accounting rules for the arms** [STIPULATED, extending §3]: book GNN+projector parameters
   AND their training compute per arm; run the LoRA-parity cell (the literature's deltas shrink
   ~an order of magnitude there — if H-GNN's advantage vanishes under host adaptation, that is
   decision-relevant for the whole family); charge subgraph retrieval identically in fusion and
   text arms.

---

## 7. Open questions for Phase-1 (what this review could not close from the literature)

1. **The size×depth interaction is an open empirical question — no prior surfaced in this
   bounded search** (§4's conclusion; a purposive 26-source sweep cannot establish that none
   exists). Treat P3-E-GNN-1 as a first measurement; power it as such, and straddle the depth
   threshold the fragments hint at rather than assuming it. [EXTRAPOLATION]
2. **No published fusion win survives full matched accounting with structure-causality** — so the
   family's Phase-2 bar (fusion > optimised-text at matched information *and* resources, causal by
   perturbation) is above anything in the literature. Expect the null; design so the null is
   informative (per-stage instrumentation localises the failure). [EXTRAPOLATION]
3. **Whether the trained bridge can be certified fail-closed is unstudied.** KBLaM's reported OOD
   behaviour (rewording/refusal drift — secondary-level, UNVERIFIED at primary, §2d) is the
   candidate failure mode; no source measures a *calibrated abstention* layer on a KV-injection
   channel. H-GNN-KV design must add one; nothing to cite. [STIPULATED]
4. **LLaGA's no-GNN result vs GraphToken's GNN**: whether the encoder must be a GNN at all is
   live in the field — the §3.2 MLP/DeepSets/Transformer encoder controls are well-aimed and may
   themselves be the finding. [MEASURED inputs, EXTRAPOLATION reading]
5. **Kautz taxonomy text remains UNVERIFIED at primary** (paywall); if a Phase-1 doc quotes the
   six types verbatim, someone with library access must check the wording. [STIPULATED]
6. **GTEval and Lost-in-Serialization venues** ("ICML 2026" claims on their pages) were not
   confirmed against conference programmes today; claims are verified at arXiv/HTML level only.
   [STIPULATED, provenance note]

---

## 8. Phase-1 hand-off — design beads to bd-create (recommendation; creation is the coordinator's, not this bead's)

| Bead | One-line scope | What this review supplies — and what it leaves OPEN |
|---|---|---|
| **P3-D-GNN** (lead input, with P3-LR-RAG co-feeding retrieval) | H-GNN-{ST,KV,LF(,RET)} designs + the size×depth sweep + controls + four-stage instrumentation (§3.2) | **Supplies:** the empirical premise RAG.md left open, now surveyed: the trained bridge is demonstrated to carry **useful learned signal in some settings** (GraphToken/GNP/G-Retriever frozen-host wins) — **structural integration is NOT established**; G-Retriever's dual-channel ablation *motivates* a topology-causal experiment but does not answer it (component contribution only, §2c); depth-direction fragments (CLUTRR modality gap, DRAGON +10 multi-step, GNN-RAG +8.9–15.5 multi-hop); the two perturbation-probe negatives (Deceive-KG — targeted, earlier models; GTEval PRBCD) that make the shuffled-edge and structure-attack controls mandatory kills; serialisation-optimised text arm requirement; parameter/LoRA-parity accounting rules (encoder+projector params booked per-arm — material at R-0 scale, §5); GNN-capability control at depth (over-squashing); encoder-sweep design inputs (depth-first scaling, edges-as-data-metric). **OPEN:** the size×depth interaction itself (no prior *found* in this bounded search, §7.1); fail-closed certification of any trained bridge (§7.3); whether the encoder needs to be a GNN (§7.4). |
| **Candidate variant: H-GNN-RET** (a RAG/executor-shaped variant — belongs primarily under P3-D-RAGC's retrieval/tool/executor controls, cross-referenced from P3-D-GNN) | GNN as *retriever/path-reasoner*, verbalised paths cross the boundary as text — GNN-RAG shape | **Supplies:** precedent with measured multi-hop gains at 7B (GNN-RAG); architecturally distinct from ST/KV/LF because **no vector crosses the model boundary**. Risk accounting, stated precisely: it avoids the graph-token-specific delivery-integration risk (the GTEval failure mode) — but it **fully retains the nsk1 text-channel risk**: the programme's own evidence is that text-delivered grounding measured net-harmful (`feasibility-synthesis.md` §0), so this variant needs text-boundary integration controls of its own, not a free pass. Build-cost intuition (deterministic engine as path extractor — no trained GNN needed for exact typed traversal, a cell the literature leaves empty) is an **unmeasured expectation**, not a measured "cheapest member"; note deterministic path extraction is no longer a GNN design at all. **OPEN:** whether deterministic path extraction + verbalisation beats learned GNN retrieval at matched budgets — no source compares them; whether verbalised paths clear the nsk1 bar at all. |
| **P3-D-GU** (co-input, with P3-LR-TINY + P3-LR-NTP) | Ground-up R-0 architecture families | **Supplies:** the field map (§1) locating ground-up neurosymbolic training as Kautz type-5/6 territory, where the systematic review shows effort concentrated (learning-and-inference 63%) yet the injection report's KEPLM/LCM history warns welded-in structure stalls; the LLaGA finding (templates+projector without GNN) as a cheap architecture variant. **OPEN:** everything R-0-specific — defer to P3-LR-TINY/NTP. |

**What this review settled — and what it only bounded** [STIPULATED, the bead's exit claim]:
(1) the H-GNN family's empirical premise is now surveyed — the trained bridge demonstrably
carries useful learned signal in some settings, *structural* integration has never been
established in the field, and the programme's pre-registered controls are precisely the ones the
two published perturbation probes motivate; (2) the size×depth sweep has **no prior found in this
bounded, non-systematic 26-source search** — the RAG.md open item is answered as "none surfaced",
and novelty is **unverified, not settled** (no search strings, databases, inclusion criteria, or
citation-chasing protocol were used, so the negative cannot be established); (3) the KV lineage
(KBLaM→AtlasKV) is alive and scaling as the H-GNN-KV/H-RULE-KV precedent, with trained bridges as
its verified named risk (the fail-open OOD reports are secondary-level, §2d); (4) one candidate
variant (H-GNN-RET) is proposed with published precedent — as a RAG/executor-shaped design
retaining the nsk1 text-channel risk (§8 row 2); (5) no *other* missing H-* family surfaced
**within this sweep** — the field map's remaining cells (type-5/6 tensorised logic, ground-up)
are already owned by H-RULE-HL/P3-D-GU and deliberately deferred; this too is bounded by the
search, not a field-level negative.

---

## Source count

- **Ledger:** 26 entries in `FUSE.sources.jsonl`. The earlier single `verified: true` flag
  conflated "fetched" with "claim verified" and is replaced (2026-07-11 revision, on independent
  review) by separate statuses per entry: `bib_verified`, `venue_verified`, `claims_verified`
  (primary / primary-abstract / secondary-only / mixed), `fetched` date, and an `anchor`
  (table/section) where claims were checked. Highlights: Kautz 2022 is bib/venue-verified but
  claims are **secondary-only** (Wiley HTTP 402 twice); KBLaM is **mixed** (mechanism primary,
  limitation claims secondary-only, UNVERIFIED); GraphToken carries an explicit `audit_conflict`
  field disclosing the KB record's SPOT-REFUTED status; AtlasKV's venue is upgraded to
  **ICLR 2026 confirmed**; GTEval/Lost-in-Serialization venues are `stated-by-source-only`.
- **UNVERIFIED claims flagged inline:** Kautz six-type wording (§1, §7.5); KBLaM limitation
  claims (§2d — secondary-only, sources uncited, paper-body not re-verified: UNVERIFIED, not
  MEASURED); GTEval + Lost-in-Serialization venue claims (§7.6); GraphToken, GNN-RAG, and
  graph-scaling-laws peer-reviewed venues (none found — treated as arXiv).
- **Repo-internal evidence** (`feasibility-synthesis.md`, `lit-llm-injection-priorart.md`,
  `lit-eval-benchmarks.md`, `RAG.md`, `EVAL.md`) cited as [MEASURED: repo-internal] within their
  own envelopes; KB records consulted for recall only, per the honesty boundary; none cited as
  evidence.
