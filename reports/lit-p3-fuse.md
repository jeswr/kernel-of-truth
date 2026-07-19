# P3-LR-FUSE — GNN–LLM fusion + neurosymbolic integration survey (formalized)

**Bead:** P3-LR-FUSE (Programme-3, Phase-0 [LIT]; absorbs rev-1 P3-LR-NSA + P3-LR-GNN).
**Deliverable path:** `reports/lit-p3-fuse.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is frozen,
registered, or scheduled; no registry record / ASM / KB shard is touched; no bd/git operations.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §3.2
(H-GNN-{ST,KV,LF} over the kernel+world graph), §5 table row P3-LR-FUSE, ASM-0805.
**Feeds:** P3-D-GNN (lead input), P3-D-GU (co-input); answers the open item RAG.md §7.4 left
("GNN-to-LM fusion has no source in this ledger … P3-D-GNN's empirical premise stays open").

> **Relationship to `docs/next/lit/FUSE.md`.** A prior, careful FUSE review exists (Fable,
> 2026-07-11, bead …s55r.7, already once-revised on a GPT-5.6 review, with source ledger
> `FUSE.sources.jsonl`, 26 entries). **This report is not a redo.** It is (a) an independent
> re-verification of the draft's load-bearing citations at their primary sources this session,
> (b) an explicit divergence log, and (c) a formalization at the requested `reports/` path,
> epistemic-tagged and refreshed to 2026-07-19. Where I re-fetched a source I say so; where I
> accepted the 07-11 verification without re-fetch (uncontested abstract-level anchors) I mark
> `[prior-verified: 2026-07-11]`. **Headline result of the verification pass: the draft's
> load-bearing numbers hold at source** — including the one apparent discrepancy I chased
> (G-Retriever's ablation), which reconciled *in the draft's favour* and exposed a WebFetch
> extraction artifact, not a factual error. Divergences found are minor and provenance-level
> (§ Divergences).

## Epistemic tag convention

- `[established]` — external empirical/methodological fact confirmed at a primary source this
  session or prior. `[claimed]` — asserted in a source but single-source, abstract-only, or not
  independently corroborated. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified at source via WebSearch/WebFetch this
  session; `[prior-verified: 2026-07-11]` = verified at source in the 07-11 FUSE.md, accepted here
  without re-fetch; `[memory]` = from the parent doc / in-repo verdicts, not a literature source.
- `[UNVERIFIED]` = could not be confirmed at primary source (paywall or fetcher failure).
- A note on measurement register (inherited from the draft, kept): a "MEASURED" number below is the
  *authors'* published measurement restated inside that paper's own envelope — never *our*
  measurement, and never a premise for a KoT verdict. Cross-paper readings are direction-only.

---

## Top findings (read this first)

1. **The crux — has any neurosymbolic / GNN–LLM system beaten a *matched-resource* neural baseline
   under fair accounting? Honest answer: not clearly, and never for the property the programme
   needs.** `[established][search: 2026-07-19]` Across the fusion literature re-verified this
   session, every headline win is confounded on at least one of {added information, added trainable
   parameters, added training compute, added retrieval machinery, structure-causality not
   demonstrated}. The strongest same-system candidate (G-Retriever's dual ablation, §3) shows
   **component contribution, not topological causality**, and **two** independent perturbation
   probes (Deceive-KG; GTEval's PRBCD attack) actively argue *against* assuming the structure
   channel is what carries the win. This is the single most important finding for Programme-3: the
   H-GNN family's empirical premise is **plausible, replicated as a trained-bridge seam, but
   unproven as structural integration, and twice undercut by causality probes.** The §3.2 sweep is
   therefore a genuine first experiment, not a replication. This concurs with the Fable draft's §3
   audit verdict; I found nothing at source that softens it.

2. **The trained bridge demonstrably carries *useful learned* signal in the frozen-host setting —
   that much is real.** `[established][search: 2026-07-19]` GraphToken, GNP and G-Retriever all
   beat frozen-host prompt-tuning baselines by wide *relative* margins (GNP +13.5% rel / +8.4–9.3
   pts abs; G-Retriever +23–48% rel / +17.9–27.5 pts abs; GraphToken large on algorithmic GraphQA).
   The signal shrinks by ~an order of magnitude once the host is allowed LoRA (G-Retriever
   +1.95–11.74% rel; GNP +1.8% rel) — i.e. **much of the "fusion win" is "someone finally trained
   something on this task distribution."** The seam works; its *marginal* value over an adapted host
   is small and unquantified for topology.

3. **The programme's own "delivery ≠ integration" (nsk1) lesson is now a published, field-level
   result on exactly the H-GNN-ST architecture class.** `[established][search: 2026-07-19]` GTEval
   (2026) shows graph-token LLMs drop up to ~50% under instruction rephrasing and below 10% on
   content-level variants; under a PRBCD structural attack the text-carrying fused models are
   *almost unchanged* while a GCN baseline collapses (−73.65% overall) — the fused models were
   reading the text, not the structure — **yet** a probe shows the graph tokens *contain* the
   structural signal (link-prediction from graph tokens ≈ from original embeddings) the LLM fails
   to use. This is the strongest single external warrant for the §3.2 four-stage instrumentation and
   the mandatory structure-attack + shuffle controls.

4. **The KV-injection lineage (KBLaM → AtlasKV) is alive and scaling — but every member trains the
   bridge.** `[established][search: 2026-07-19]` KBLaM (ICLR 2025) reads KB triples as continuous
   KV pairs via *trained linear adapters*, linear (not quadratic) in KB size, >10K triples into an
   8B/8K host on one A100; AtlasKV (ICLR 2026, venue confirmed on the arXiv page) scales the same
   shape to 1B triples under <20GB VRAM. **No training-free KV-injection precedent surfaced** — the
   injection report's interface-locality law holds in this lineage too. The reported KBLaM
   fail-open OOD behaviours remain **secondary-only / UNVERIFIED at primary** (§ Divergences), so
   they may motivate but must not anchor the fail-closed design argument.

5. **Field-map placement is confirmed and unchanged:** the programme's distinctive cell — a
   *deterministic, training-free, provenance-carrying* engine as the symbolic half, store versioned
   externally — is thinly populated in both the Kautz integration taxonomy and Jin et al.'s graph
   taxonomy; the fusion literature almost universally *trains* the symbolic-side interface. No
   missing H-* family surfaced within this sweep. `[established][search: 2026-07-19]`

---

## 1. Field map — taxonomies and where the H-* families sit

- **Canonical integration taxonomy — Kautz's six types** (Kautz, "The third AI summer: AAAI Robert
  S. Engelmore Memorial Lecture", *AI Magazine* 43(1), 2022, DOI 10.1002/aaai.12036).
  `[established: bibliographic record + attribution][search: 2026-07-19]` The bibliographic record
  and the attribution of the six-type scheme to Kautz are confirmed via multiple secondary sources
  (Wikipedia "Neuro-symbolic AI"; independent "Kautz taxonomy" field guides). The **verbatim
  six-type wording remains `[UNVERIFIED]` at primary** — the Wiley full text returned HTTP 402
  again this session, matching the draft. Six types (restated, *not* quotable as Kautz):
  (1) symbolic-in/out neural processing; (2) Symbolic[Neuro] (symbolic solver, neural subroutine —
  AlphaGo); (3) Neuro|Symbolic (neural perception → symbolic reasoner via I/O); (4)
  Neuro:Symbolic→Neuro (symbolic knowledge compiled into training); (5) Neuro_Symbolic (logic
  tensorised into the network); (6) Neuro[Symbolic] (combinatorial reasoning engine inside the
  network). *(Minor bib note: a secondary listing gives the page range as 43(1):93–104 vs the
  draft's 105–125; unresolved behind the paywall, non-load-bearing — see § Divergences.)*
- **Field statistics — PRISMA review** (Colelough & Regli, arXiv:2501.05435, 2025).
  `[established][search: 2026-07-19]` PRISMA, 1,428 papers screened → 167 analysed; concentration
  in learning-and-inference **63%**, knowledge-representation **44%**, logic-and-reasoning **35%**,
  explainability/trustworthiness **28%**, meta-cognition **5%** — all figures confirmed at source.
  Reading: the field's centre of mass is **training-time integration**, not the **runtime-checker**
  shape the programme builds. The "3rd wave" agenda (Garcez & Lamb, arXiv:2012.05876)
  `[claimed][prior-verified: 2026-07-11]` frames the same gap (sound reasoning + interpretability
  atop learned representations).
- **Graph-specific taxonomy** (Jin et al., "LLMs on Graphs: A Comprehensive Survey", IEEE TKDE
  2024, arXiv:2312.02783). `[established][search: 2026-07-19]` Confirmed verbatim: scenarios
  {pure graphs, text-attributed graphs, text-paired graphs} × roles {LLM-as-Predictor,
  LLM-as-Encoder, LLM-as-Aligner}.

**Placement of the programme's families** `[speculative — my mapping, confers no evidence]`:
H-VL (external verifier loop) ≈ Kautz type-3; H-GNN-{ST,KV,LF} are all "LLM-as-Predictor over
text-attributed graphs" (Jin), with the kernel+world layer as the graph; H-RULE-CD ≈ type-2/3
(engine-derived continuation sets delivered by masking); H-RULE-HL aims at type-6, already deferred
by the §3.3 ladder ruling. The programme's distinctive cell (deterministic/training-free/provenance
engine + externally-versioned store) is thinly populated in both taxonomies. Consistent with
`reports/lit-llm-injection-priorart.md`'s interface-locality law. `[memory]`

---

## 2. The fusion lineages — condensed, with 2026-07-19 verification status

The four lineages the §3.2 designs descend from. Each row's load-bearing numbers were re-checked at
source this session unless marked otherwise.

- **2a. Weight-fusion / KEPLM era (ERNIE → KnowBERT → K-Adapter, 2019–21).** ERNIE (Zhang et al.,
  ACL 2019) fused KG entity embeddings into BERT-class encoders. `[claimed][prior-verified:
  2026-07-11]` The lineage verdict is *inherited*, not re-derived: the KEPLM line stalled at BERT
  scale, probes showing marginal integration (`lit-llm-injection-priorart.md` §1). Ancestor of
  "weld structure into the weights" — the H-RULE-HL shape the programme already deprioritised.

- **2b. GNN–LM co-attention era (QA-GNN → GreaseLM → DRAGON, 2021–22).**
  - **QA-GNN** (Yasunaga et al., NAACL 2021): LM-scored KG relevance + joint message passing;
    improves over fine-tuned LMs and prior LM+KG. `[claimed][prior-verified: 2026-07-11]` (abstract).
  - **GreaseLM** (Zhang et al., ICLR 2022): multi-layer bidirectional LM↔GNN fusion.
    `[established][search: 2026-07-19]` **Re-verified at source (ar5iv):** CSQA 74.2 vs RoBERTa-L
    68.7 (**+5.5**) and vs QA-GNN 73.4 (**+0.9**); OBQA 84.8 vs AristoRoBERTa 78.4 (**+6.4**) and vs
    QA-GNN 82.8 (**+2.0**); ConceptNet subgraphs pruned to **top-200 nodes** (confirmed). Shape: the
    big step is *any* KG machinery over the bare LM; the *fusion-architecture* increment over the
    prior KG method is **≤2 points**.
  - **DRAGON** (Yasunaga et al., NeurIPS 2022): self-supervised bidirectional text-KG pretraining.
    `[established][search: 2026-07-19]` **Verbatim confirmed:** "+5% absolute gain on average" and
    "+10% on questions involving long contexts or multi-step reasoning" — the best single published
    hint that the fusion advantage grows with reasoning depth (§4). Envelope: gains **include
    uncharged KG-linked pretraining compute** (confound).
  - **Skeptic anchor — Deceive-KG** (Raman et al., ICLR 2021, arXiv:2010.12872).
    `[established][search: 2026-07-19]` **Verbatim confirmed:** an RL policy (or heuristics)
    produces *targeted* perturbed KGs that "maintain downstream performance … while significantly
    deviating from the original KG's semantics and structure", on **question-answering and item
    recommendation** models, "rais[ing] doubts about KG-augmented models' ability to reason about KG
    information". **Scope (kept precise):** *targeted/learned* perturbation, not a uniform
    shuffled-edge control; GreaseLM/DRAGON postdate it and were untested. Supports: KG-perturbation
    controls have published bite; content-attribution cannot be assumed. Does *not* support: that a
    uniform shuffle passes, or that GreaseLM/DRAGON wins are specifically unattributed.

- **2c. Frozen-LLM soft-token era (GraphToken → G-Retriever / GNP / GraphPrompter; GraphGPT, LLaGA),
  2024–.**
  - **GraphToken** (Perozzi et al., arXiv:2402.05862; **no peer-reviewed venue** — treat as arXiv).
    `[established][search: 2026-07-19]` **Re-verified at source (ar5iv):** headline "across the
    board improvements — up to 73% points" is stated **baseline-free in the abstract** (confirmed —
    the abstract names no baseline for that figure). Table 1 fragments confirmed: edge existence
    0.738 vs soft-prompt 0.544; node degree 0.962 vs soft-prompt 0.098; cycle check 0.956 vs
    zero-shot 0.760 — baseline columns are zero-shot/CoT/soft-prompt on a **frozen PaLM-2**.
    Trainable side confirmed: GNN body **17,152–198,788 params** + a **~11M-param projector**.
    Envelope: algorithmic tasks over small synthetic graphs. **Audit-conflict retained:** KB record
    `arxiv:2402.05862` is SPOT-REFUTED for assigning the 73-point headline to a soft-prompt baseline
    the paper does not support; this review keeps it baseline-free. Direct precedent for **H-GNN-ST**
    and the E5/A2 adapter seam.
  - **G-Retriever** (He et al., NeurIPS 2024, arXiv:2402.07630; venue confirmed).
    `[established][search: 2026-07-19]` **Re-verified at source (arXiv HTML, Table 6) — matches the
    draft exactly.** WebQSP ablation (relative to full model): **w/o graph encoder → 54.62
    (↓22.51%)**; **w/o textualized graph → 56.96 (↓19.19%)** — removing the **graph encoder is the
    *larger* drop**; frozen prompt-tuning baseline 48.34. Main-results improvements are **relative**
    (≈23–48%), not absolute. The paper frames the two channels as **complementary components** —
    which is *all* the ablation shows: **component contribution, not causal use of topology** (the
    encoder also consumes textual node/edge attributes; **no edge/label shuffle is run**). WebQSP
    graphs average ~1,371 nodes; retrieval cuts input tokens 83–99%. *Closest thing in the sweep to
    a matched comparison, and still not a topology-causality result.*
  - **GNP** (Tian et al., AAAI 2024, arXiv:2309.15427). `[established][search: 2026-07-19]`
    **Re-verified at source (ar5iv):** +13.5% over prompt tuning (LLM frozen) and +1.8% over LoRA —
    both **relative**, averaged over six commonsense/biomedical datasets. Table 1 aggregate:
    **68.55 → 77.84** (FLAN-T5-xxlarge 11B, **+9.29 pts**), **65.95 → 74.36** (xlarge 3B, **+8.41
    pts**). Same shrinking-delta shape as G-Retriever.
  - **GraphPrompter** (Liu et al., WWW 2024 short, arXiv:2402.10359): GNN-as-soft-prompt on node
    classification / link prediction. `[claimed][prior-verified: 2026-07-11]` (qualitative).
  - **Instruction-tuned cousins:** GraphGPT (Tang et al., SIGIR 2024) `[claimed][prior-verified:
    2026-07-11]`; **LLaGA** (Chen et al., ICML 2024, PMLR v235:7809-7823) `[established][search:
    2026-07-19]` — **confirmed at source:** structure-aware node *sequences* + a versatile projector,
    surpassing graph models in supervised **and** zero-shot settings and generalizing to unseen
    datasets/tasks. Its mechanism is projector-on-sequences; the draft's "**no GNN at all**" is a
    fair characterization of the primary mechanism, mildly stronger than the abstract's literal
    wording (see § Divergences). Evidence that ordering-templates + a trained projector deliver much
    of what "the graph encoder" is credited with.
  - **Skeptic anchor — GTEval** (Zhang et al., arXiv:2605.03514; submitted 2026-05-05).
    `[established at HTML level][search: 2026-07-19]` **Re-verified at source (arXiv HTML):**
    graph-token LLMs "rely heavily on text for reasoning"; drops up to ~50% under instruction
    rephrasing (InstructGLM ↓50.07% on Cora) and below 10% on content-level variants; **PRBCD
    structural attack (Table 3): GCN baseline ↓73.65% overall while text-carrying fused models are
    almost unchanged** (GraphGPT ↑, TEA-GLM ≈0; LLaGA, a structure-sequence method, ↓39.30%);
    **probe (Fig. 4): a GCN on graph tokens ≈ a GCN on graph embeddings**, so the structural signal
    is present but unused. Field-level replication of the nsk1 delivery-without-integration failure
    mode, on exactly the H-GNN-ST class. **Venue divergence:** the arXiv page shows **no venue** this
    session (the draft's "ICML 2026, stated by source" is not reproducible today — § Divergences);
    substantively unchanged since the draft already flags the venue UNVERIFIED.

- **2d. KV-injection lineage (KBLaM → AtlasKV) — the H-GNN-KV / H-RULE-KV precedent.**
  - **KBLaM** (Wang et al., ICLR 2025). `[established: mechanism/scaling][search: 2026-07-19]`
    **Re-verified at source (arXiv:2410.10450):** KB triples → continuous KV pairs via a pre-trained
    sentence encoder + **trained linear adapters**, read through **rectangular attention**; overhead
    **linear** in KB size (vs quadratic in-context); >10K triples into an 8B / 8K-window LLM on one
    A100; **dynamic updates without retraining**. Named **limitations** (precision-decay-with-size /
    refusal drift, OOD/Enron degradation, rewording drift) remain **`[UNVERIFIED]`** at primary —
    restated from uncited secondary sources, not in the paper body I read — direction-only, do not
    build on specifics.
  - **AtlasKV** (Huang et al., ICLR 2026). `[established: abstract][search: 2026-07-19]`
    **Re-verified (arXiv:2510.17934):** scales KV injection to **1B triples under <20GB VRAM** via
    KG2KV + HiKVP, "sub-linear time and memory", no external retriever / long-context prior /
    retraining. **Venue "ICLR 2026" is confirmed in the arXiv Comments field** (matches the draft's
    07-11 upgrade).
  - Decision relevance: the L2b / H-GNN-KV / H-RULE-KV seam has a **live, scaling lineage — but
    every member trains the bridge.** No training-free KV-injection precedent surfaced.
    `[speculative — absence-claim within this bounded sweep]`

- **2e. Adjacent — GNN-as-retriever (structure consumed *before* the boundary).** **GNN-RAG**
  (Mavromatis & Karypis, arXiv:2405.20139; no peer-reviewed venue). `[established: abstract][search:
  2026-07-19]` **Confirmed:** a GNN reasons over a dense KG subgraph, extracts shortest reasoning
  paths, verbalises them; a tuned 7B LLaMA2 matches/exceeds GPT-4 on WebQSP/CWQ, **+8.9–15.5 F1
  points on multi-hop / multi-entity questions.** Architecturally *not* fusion (no vector crosses
  the boundary): it avoids the graph-token delivery-integration risk but **fully retains the nsk1
  text-channel risk** (grounding delivered as text). Candidate H-GNN-RET variant (§7).

---

## 3. The crux — what actually beat a MATCHED baseline (the accounting audit)

The bead's central skeptical question. Ledger per headline (each row's numbers MEASURED from its §2
source; the "matched?" reading is my `[speculative]` audit):

| Headline win | Baseline it beat | Matched | NOT matched | Structure-causality survive? |
|---|---|---|---|---|
| GreaseLM +5.5 CSQA | fine-tuned RoBERTa-L | base LM, task data | +GNN params, +KG access, +retrieval | Deceive-KG (earlier models, *targeted* perturbation; GreaseLM untested) ⇒ content-attribution **unestablished**, not disproven |
| GreaseLM +0.9 / +2.0 | QA-GNN (same KG, same LM) | LM, KG, subgraph budget | fusion-layer params (small) | honest *architecture* increment: **≤2 pts** |
| DRAGON +5 avg / +10 multi-step | RoBERTa + prior LM+KG | task data | +KG-linked **pretraining compute** (large, uncharged) | pretraining-compute confound; depth signal real but envelope-bound |
| GraphToken "up to 73% pts" | **not identified in abstract**; table fragments vs soft-prompt / zero-shot | LLM (frozen), graph info | +trained GNN+projector on the task distribution; baselines untrained | headline baseline unattributable (KB record SPOT-REFUTED); **training-compute-unmatched**; tiny algorithmic graphs |
| G-Retriever frozen +23–48% rel (+17.9–27.5 pts abs) | prompt tuning (trained soft prompt, same data) | trainable-prompt shape, task data, frozen LLM | GNN+projector params > prompt params; retrieval step | **closest to matched in the sweep**; dual ablation −22.5% / −19.2% rel ⇒ **component contribution only** — encoder also reads text attributes, no topology shuffle |
| GNP +13.5% rel frozen (+8.4/9.3 pts abs) | prompt tuning | frozen LLM, task data | GNN+projector params; KG access | same shape; **+1.8% rel** over LoRA when tuned — delta nearly vanishes once the host adapts |
| KBLaM linear-scaling | in-context text of same KB | knowledge content | KBLaM adds instruction-tuned adapters; ICL pays quadratic attention | the win is **cost-shape, not accuracy**; decay/OOD reports secondary-level (UNVERIFIED) |
| GNN-RAG ≈ GPT-4 (7B) | GPT-4 zero/few-shot; prior KGQA retrievers | benchmark | tuned 7B + KG access vs closed-book GPT-4 — **unmatched substrate** | cost story favourable; not a fusion-causality result |

**Audit verdict** `[speculative — direction-only; this purposive sweep, not a systematic search]`:

1. **No GNN-fusion result in this sweep beats a matched baseline under full accounting** (same
   information, same trainable-parameter budget, same training compute, structure-causality shown by
   perturbation). The two perturbation probes both argue *against* the structure channel: Deceive-KG
   (earlier KG-augmented models, targeted perturbation) and GTEval's PRBCD result (soft-token era).
   Neither runs the programme's uniform shuffle; neither *settles* attribution — they show it was
   never established. **This is the crux answer, and it is "not clearly."**

2. The **recurring delta pattern**, in consistent units: relative gains **+13.5% to ~48%** over
   frozen-host prompt-tuning (absolute **+8.4 to +27.5 accuracy pts**; GraphToken's baseline-free
   "up to 73 pts" on algorithmic GraphQA sits *outside* this matched set), **shrinking to
   +1.8–11.7% relative once the host is allowed LoRA.** Much of the fusion win is "someone finally
   trained something on this task distribution."

3. **Strongest defensible positives** for the H-GNN bet: (a) G-Retriever's dual ablation on a
   ~1.4k-node KGQA task — removing *either* channel costs double-digit relative Hit@1, so the
   trained soft-token channel carries **useful learned signal at scale** — but **component
   contribution only**, not shown *structural/topological* (encoder also reads text; no shuffle);
   (b) DRAGON's +10 on multi-step (pretraining-confounded); (c) GNP/GraphToken confirming the
   trained-bridge seam works frozen-host (field-level replication of the A2/E5 result).

4. **The strongest single candidate, stated as strongly as honesty allows, and why it still
   fails the bar:** *G-Retriever, frozen host.* It beats a **trained** prompt-tuning baseline (not a
   strawman zero-shot) by +22.15 Hit@1 points on a real ~1,371-node KGQA task, and its own ablation
   shows both channels are load-bearing. **Caveats that keep it below the programme's bar:** the
   comparison is not trainable-parameter-matched (GNN+projector > soft prompt); the graph encoder
   consumes textual node/edge attributes, so "graph encoder contributes" ≠ "topology contributes";
   **no edge/relabel shuffle is run**, so structure-causality is untested here; and the whole delta
   collapses toward +10% relative under LoRA. It is the best evidence that *the seam is worth
   building and testing* — it is **not** evidence that structure has beaten matched text.

5. **Beyond fusion — is there ANY neurosymbolic matched-baseline win? An honest widening.**
   `[speculative][memory]` Outside the GNN-fusion slice, task-solving neurosymbolic systems
   (e.g. logic-tensor / probabilistic-logic hybrids, and search-augmented provers of the
   AlphaGeometry class) *do* beat neural baselines on their tasks — but they win by **adding a
   capability the neural baseline structurally lacks** (exact search, sound deduction, guaranteed
   constraint satisfaction), typically with hand-built domain knowledge, on narrow domains, and
   **not at matched information/resources**. That is a *different and legitimate* value
   proposition — and, notably, it is precisely the one the programme's **correctness thesis** rests
   on (a deterministic fail-closed checker priced against its own falsifier), *not* the efficiency
   thesis. The honest programme-level reading: **no neurosymbolic system has been shown to beat a
   matched-resource neural baseline at the same task and information; the demonstrated wins come
   from adding an exact-reasoning capability, which is where the kernel's defensible value most
   plausibly lives.** I did not re-verify the AlphaGeometry-class examples at source this session —
   tagged speculative accordingly; a dedicated NeSy-wins pass (P3-LR-NSA scope, now folded here)
   would be the place to harden or refute this.

6. For P3-D-GNN this settles the **control design** (§6) and hardens **ASM-0805** as
   `[speculative]/EXTRAPOLATION`: the family's empirical premise is **plausible, unproven, twice
   undercut by causality probes** — the §3.2 sweep is a genuine experiment. `[speculative: adopted
   as this review's core decision input]`

---

## 4. Fusion vs text serialisation — measured results + size / depth dependence

**The control arm's own literature (what optimised text can and cannot do):**

- **Serialisation is a first-order variable** — *the text control must be its best self, not a
  strawman.* Talk-like-a-Graph (Fatemi et al., ICLR 2024, arXiv:2310.04560).
  `[established][search: 2026-07-19]` **Verbatim confirmed:** "the correct choice of encoders can
  boost performance on graph reasoning tasks inside LLMs by **4.8% to 61.8%**, depending on the
  task."
- **LLM graph ability is real but brittle.** NLGraph (Wang et al., NeurIPS 2023 spotlight,
  arXiv:2305.10037). `[established: core claims][search: 2026-07-19]` **Confirmed:** 29,370 problems
  / 8 tasks; LLMs show "preliminary graph reasoning abilities"; "the benefit of advanced prompting
  and in-context learning diminishes on more complex graph problems"; "brittle in the face of
  spurious correlations"; Build-a-Graph / Algorithmic prompting recover only **+3.07–16.85%**.
  *(The draft's "37–58% above random on easy tasks" is a body-level figure not reconfirmed at
  abstract level this session — non-load-bearing, see § Divergences.)*
- **LLM graph reasoners are not re-serialisation-invariant.** Lost in Serialization (Herbst et al.,
  arXiv:2511.10234; page states **ICML 2026 GFM Workshop**). `[established][search: 2026-07-19]`
  **Confirmed:** different outputs under node reindexing / edge reordering / formatting; larger
  non-fine-tuned models more robust; fine-tuning reduces relabeling sensitivity but **increases
  structure/format sensitivity** and does not consistently transfer to unseen tasks.

**What fusion adds over serialisation, where measured:** GraphToken's "up to 73%" is baseline-free
on algorithmic tasks over small synthetic graphs; G-Retriever's ablation is the cleanest same-system
decomposition but is **component-contribution, not topology-causality**; GTEval shows the same
architecture class **leaning on text when both are present**. `[established][search: 2026-07-19]`

**Size dependence — what exists:** the text-side ceiling degrades as graphs grow (NLGraph
complexity gradient; WebQSP graphs average ~1,371 nodes and G-Retriever's retrieval cuts input
tokens up to 99% *before* fusion). The **fusion**-side evidence at size is confounded — G-Retriever
"scales well with larger graph sizes" but the gain bundles retrieval + soft tokens; **no source
isolates the encoder at size.** `[established][search: 2026-07-19]`

**Depth dependence — three direction-consistent fragments, none a sweep:** CLUTRR (Sinha et al.,
EMNLP-IJCNLP 2019, `[established][search: 2026-07-19]` — "substantial performance gap between …
BERT and MAC … and a graph neural network model that works directly with symbolic inputs — the
graph-based model exhibiting both stronger generalization and greater robustness") — an
*input-modality* result, not fusion; DRAGON +10 on multi-step (pretraining-confounded); GNN-RAG
+8.9–15.5 on multi-hop / multi-entity (retrieval, not fusion).

**Load-bearing conclusion for P3-E-GNN-1** `[speculative — direction-only]`: the literature supports
"**structure pays increasingly with reasoning depth, and text serialisation degrades with graph
size**" as a *hypothesis with scattered, confounded support* — CLUTRR (modality), DRAGON
(pretraining), GNN-RAG (retrieval). **No published matched-information size×depth sweep of
GNN-fusion vs optimised text serialisation surfaced in this bounded, purposive 26-source sweep.** A
non-systematic search cannot *establish* the negative: treat the §3.2 sweep as **"no prior found",
not confirmed-novel**, and power it as a first measurement either way. The rescoped falsifier (kill
only on a flat-or-text-favouring curve *across the whole sweep*) is well-aimed: tiny-graph text
wins are exactly what GraphQA-class results predict; a depth-increasing fusion advantage is exactly
what the three fragments hint at.

---

## 5. Graph-encoder scaling at small sizes, and the GNN's own depth ceiling

- **Encoders are small relative to their *published* hosts — not relative to R-0.**
  `[established][search: 2026-07-19]` GraphToken: 17K–199K-param GNN body + **~11M-param projector**
  against a frozen PaLM-2-class host; GreaseLM's KG side operates on ≤200-node subgraphs of a
  ~800k-node/2.5M-edge ConceptNet. Against a multi-billion-param host, 11M is negligible; against
  Programme-3's **R-0-scale host (~135M), an 11M projector is ~8% of the host — material, and must
  be booked per-arm in KOT-SIZE/2 accounting**, alongside the trained-bridge *training compute* and
  the *store itself*. `[speculative: R-0 arithmetic]`
- **Graph scaling behaviour differs from NLP.** Liu et al., "Towards Neural Scaling Laws on Graphs"
  (arXiv:2402.02054; arXiv-only). `[established][search: 2026-07-19]` **Confirmed:** up to 100M
  params / 50M samples; **model depth affects scaling beyond parameter count** (unlike CV/NLP);
  data volume better measured in **nodes/edges than graph count**. Directly usable: vary GNN depth
  deliberately; count data in edges.
- **The depth ceiling is real and named — over-squashing.** Alon & Yahav, ICLR 2021
  (arXiv:2006.05205). `[established][search: 2026-07-19]` **Confirmed verbatim:** message passing
  "over-squash[es] … exponentially growing information into fixed-size vectors", failing to
  propagate long-range info; **GCN/GIN more susceptible than GAT/GGNN**; relieving the bottleneck
  "improves … state-of-the-art results without any tuning or additional weights". **Decision
  consequence** `[speculative]`: the §3.2 deep-composition cells must carry a **GNN-capability
  control** — verify the encoder can solve the depth-*d* cell *symbolically* (GNN-alone probe)
  before attributing a fusion-arm failure at depth *d* to the fusion seam; otherwise a real fusion
  effect is masked by an over-squashing encoder. The kernel+world graph's typed, sparse, tree-ish
  structure is the favourable case — an expectation, not a measurement.

---

## 6. Relational-benchmark practice and the control set the literature validates

**Benchmark practice worth adopting** (benchmark *selection* is EVAL.md's settled ground; this is
*practice*):

1. **Procedural generation with a depth dial.** CLUTRR (parametric clause length k, held-out rule
   combinations, curated noise; its headline is itself a modality result) `[established]`; RuleTaker
   (Clark et al., IJCAI 2020, arXiv:2002.05867 — `[established][search: 2026-07-19]` **confirmed:**
   99% at trained depths, **95%+ transferring to deeper chains than seen in training**, transfer to
   hand-authored + paraphrased rulebases); GraphQA/NLGraph (task-difficulty + structure gradients).
   Adopt: generator-pinned, depth-stratified, contamination-safe-by-refresh items for the D4 legs —
   with the CLUTRR CC-BY-NC-4.0 licence caveat (`reports/lit-eval-benchmarks.md`).
2. **Input-arm factorials.** CLUTRR's text-vs-symbolic-graph arms are the direct precedent for the
   §3.2 oracle-subgraph vs NL-extracted-subgraph factorial. `[established → adopted]`
3. **Perturbation controls with teeth.** The literature validates every §3.2 pre-registered control
   and adds two:
   - *Shuffled edges/relations* — Deceive-KG is precedent that KG-perturbation controls **can pass
     while semantics are destroyed** (measured under *targeted* perturbation on earlier models; the
     uniform shuffle itself untested there). A fusion win that survives the shuffle is thereby
     *dis*-confirmed as a structure win; pre-registering it as a kill is correct. `[established,
     scope-bounded]`
   - *Structural adversarial attack (PRBCD-style)* — GTEval's cheap "does it read structure at all"
     gate: if attacking topology leaves the fused arm unchanged, it is reading text. **Add as a
     Stage-4 instrument** to the four-stage decomposition. `[established → adopt]`
   - *Serialisation-invariance battery for the text arm* — report the text control across
     serialisation variants (Lost-in-Serialization; Talk-like-a-Graph encoder set) so the text arm
     is its *best* self. `[established → adopt]`
   - *Probe-vs-use separation* — GTEval's link-prediction-from-graph-tokens probe *is* the nsk1
     "delivery probe"; the literature now independently shows delivery without behavioural use in
     this class — keep the causal behavioural endpoint primary. `[established → adopt]`
   - *Parameter-parity prompt control* — trained soft prompt of equal parameter count *without*
     graph input (GraphToken/G-Retriever/GNP practice, upgraded to parameter-matched). `[adopt]`
4. **Accounting rules for the arms** `[speculative — extends §3]`: book GNN+projector params **and
   their training compute** per arm; run the **LoRA-parity cell** (the literature's deltas shrink
   ~an order of magnitude there — if H-GNN's advantage vanishes under host adaptation, that is
   decision-relevant for the whole family); charge subgraph retrieval identically in fusion and text
   arms.

---

## 7. Implication for P3-D-GNN (the hand-off)

**What this review supplies to P3-D-GNN (lead input):**
- The empirical premise RAG.md §7.4 left open is now surveyed: the trained bridge **carries useful
  learned signal in some frozen-host settings** (GraphToken/GNP/G-Retriever) — **structural
  integration is NOT established**; G-Retriever's dual-channel ablation *motivates* a topology-causal
  experiment but does not answer it (component contribution only).
- Depth-direction fragments (CLUTRR modality gap; DRAGON +10 multi-step; GNN-RAG +8.9–15.5 multi-hop)
  make a **size×depth sweep** the right shape and the rescoped falsifier well-aimed.
- The **two perturbation-probe negatives** (Deceive-KG targeted; GTEval PRBCD) make the shuffled-edge
  and structure-attack controls **mandatory kills**, and the serialisation-optimised text arm
  mandatory.
- **Accounting rules**: encoder+projector params **and training compute** booked per-arm — *material
  at R-0 scale (~8% of a 135M host, §5)*; LoRA-parity cell; identical retrieval charging.
- A **GNN-capability control at depth** (over-squashing) before attributing deep-cell failures to the
  fusion seam.
- Encoder-sweep design inputs: depth-first scaling, edges-as-data-metric; and the **LLaGA finding**
  (templates+projector, no GNN) means the §3.2 MLP/DeepSets/Transformer encoder controls are
  well-aimed and **may themselves be the finding**.

**Candidate variant — H-GNN-RET** (belongs primarily under the retrieval/executor controls, cross-
referenced from P3-D-GNN): GNN as *retriever/path-reasoner*, verbalised paths cross the boundary as
text (GNN-RAG shape). Risk accounting, precise: it **avoids the graph-token delivery-integration
risk** (no vector crosses the boundary) but **fully retains the nsk1 text-channel risk** — the
programme's own evidence is that text-delivered grounding measured net-harmful
(`feasibility-synthesis.md` §0), so it needs text-boundary integration controls of its own, not a
free pass. A *deterministic engine* as exact typed-path extractor is a cell the literature leaves
empty — an **unmeasured expectation**, not a measured "cheapest member" (and, once deterministic, no
longer a GNN design at all). `[speculative]`

**What this review settled vs only bounded** `[speculative — the bead's exit claim]`:
(1) the H-GNN premise is **surveyed** — trained bridge carries useful learned signal, structural
integration never established, the pre-registered controls are exactly what the two probes motivate;
(2) the size×depth sweep has **no prior found in this bounded, non-systematic 26-source search** —
RAG.md's open item answered as "none surfaced", novelty **unverified, not settled** (no search
strings / databases / inclusion criteria / citation-chasing); (3) the KV lineage (KBLaM→AtlasKV) is
alive and scaling as the H-GNN-KV/H-RULE-KV precedent, trained bridges its verified named risk
(fail-open OOD reports secondary-level, UNVERIFIED); (4) H-GNN-RET proposed with published precedent
but retaining the nsk1 text-channel risk; (5) no *other* missing H-* family surfaced within this
sweep — remaining type-5/6 cells owned by H-RULE-HL/P3-D-GU and deferred; also bounded by the search,
not a field-level negative.

---

## 8. Open questions for Phase-1 (what the literature could not close)

1. **The size×depth interaction is open — no prior surfaced in this bounded search** (§4). Treat
   P3-E-GNN-1 as a first measurement; straddle the depth threshold the fragments hint at rather than
   assuming it. `[speculative]`
2. **No published fusion win survives full matched accounting with structure-causality** — so the
   family's Phase-2 bar (fusion > optimised-text at matched information *and* resources, causal by
   perturbation) is **above anything in the literature.** Expect the null; design so the null is
   informative (per-stage instrumentation localises the failure). `[speculative]`
3. **Whether the trained bridge can be certified fail-closed is unstudied.** KBLaM's reported OOD
   behaviour (rewording/refusal drift — secondary-level, UNVERIFIED at primary, §2d) is the candidate
   failure mode; no source measures a *calibrated abstention* layer on a KV-injection channel.
   H-GNN-KV design must add one; nothing to cite. `[speculative]`
4. **Whether the encoder must be a GNN at all is live in the field** (LLaGA no-GNN vs GraphToken
   GNN) — the §3.2 MLP/DeepSets/Transformer controls are well-aimed and may be the finding.
   `[established inputs, speculative reading]`
5. **The broader neurosymbolic "matched-baseline win" question is not fully closed by a
   fusion-scoped sweep** (§3 point 5) — a dedicated NeSy-wins pass (folded P3-LR-NSA scope) should
   harden or refute the "wins come from added exact-reasoning capability, not matched-resource
   superiority" reading, which if correct is the strongest argument for locating the kernel's value
   in the correctness (checker) thesis rather than the efficiency thesis. `[speculative]`
6. **Kautz taxonomy verbatim wording remains UNVERIFIED at primary** (paywall, both 07-11 and today);
   if a Phase-1 doc quotes the six types verbatim, someone with library access must confirm the
   wording and the page range (§ Divergences). `[speculative]`

---

## Citation-verification table (2026-07-19)

Legend: **V@src** = re-verified at primary source this session; **V-HTML** = verified at arXiv-HTML /
ar5iv (table/body level) this session; **prior** = accepted from the 07-11 FUSE.md verification,
not re-fetched (uncontested abstract-level); **UNVERIFIED** = could not confirm at primary.

| # | Source (short) | URL | What it anchors here | Status (2026-07-19) |
|---|---|---|---|---|
| 1 | GraphToken (Perozzi) | arxiv.org/abs/2402.05862 | H-GNN-ST precedent; "73% pts" baseline-free; Table 1 fragments; 17K–199K + ~11M params | **V-HTML** — headline baseline-free, table fragments, param counts all confirmed; venue = arXiv (no peer venue) |
| 2 | G-Retriever (He) | arxiv.org/abs/2402.07630 | strongest matched candidate; dual ablation | **V-HTML (Table 6)** — 54.62/56.96, ↓22.51%/↓19.19%, graph-encoder-removal larger drop, 48.34 PT — **exact match to draft** |
| 3 | GNP (Tian) | arxiv.org/abs/2309.15427 | frozen-host bridge; +13.5%/+1.8% rel | **V-HTML** — 68.55→77.84, 65.95→74.36; +13.5%/+1.8% relative confirmed |
| 4 | GreaseLM (Zhang) | arxiv.org/abs/2201.08860 | co-attention deltas; ≤2 pt arch increment | **V-HTML** — 74.2/68.7/73.4, 84.8/78.4/82.8, top-200 nodes confirmed |
| 5 | DRAGON (Yasunaga) | arxiv.org/abs/2210.09338 | depth signal (+10 multi-step) | **V@src** — "+5% avg", "+10% … long contexts or multi-step" verbatim |
| 6 | QA-GNN (Yasunaga) | aclanthology.org/2021.naacl-main.45 | co-attention ancestor | **prior** (abstract-level) |
| 7 | KBLaM (Wang) | arxiv.org/abs/2410.10450 | KV lineage mechanism | **V@src** mechanism/scaling; **limitations UNVERIFIED** (secondary-only) |
| 8 | AtlasKV (Huang) | arxiv.org/abs/2510.17934 | KV lineage at scale; ICLR 2026 | **V@src** — 1B triples/<20GB, KG2KV+HiKVP; **venue ICLR 2026 confirmed in Comments** |
| 9 | Deceive-KG (Raman) | arxiv.org/abs/2010.12872 | perturbation-control precedent | **V@src** — RL/heuristics, QA + recommendation, "raise doubts", *targeted* scope confirmed |
| 10 | Talk-like-a-Graph (Fatemi) | arxiv.org/abs/2310.04560 | serialisation is first-order | **V@src** — "4.8% to 61.8%" verbatim |
| 11 | NLGraph (Wang) | arxiv.org/abs/2305.10037 | LLM graph brittleness | **V@src** — 29,370/8 tasks, +3.07–16.85% (37–58%-above-random figure body-level, not reconfirmed) |
| 12 | CLUTRR (Sinha) | aclanthology.org/D19-1458 | modality gap; depth benchmark | **V@src** — BERT/MAC vs GNN-over-symbolic gap, held-out rules + noise confirmed |
| 13 | RuleTaker (Clark) | arxiv.org/abs/2002.05867 | depth-controlled benchmark | **V@src** — 99% trained depth, 95%+ deeper transfer confirmed |
| 14 | Kautz (third AI summer) | doi 10.1002/aaai.12036 | canonical integration taxonomy | **bib + attribution V@src (secondary)**; **six-type verbatim UNVERIFIED** (Wiley 402); page-range 105–125 vs 93–104 unresolved |
| 15 | Colelough & Regli (PRISMA) | arxiv.org/abs/2501.05435 | field statistics | **V@src** — 1,428→167; 63/44/35/28/5% confirmed |
| 16 | Garcez & Lamb (3rd wave) | arxiv.org/abs/2012.05876 | agenda framing | **prior** (abstract-level) |
| 17 | Jin et al. (LLMs on graphs) | arxiv.org/abs/2312.02783 | graph taxonomy | **V@src** — {pure/text-attributed/text-paired} × {Predictor/Encoder/Aligner} confirmed |
| 18 | GraphGPT (Tang) | arxiv.org/abs/2310.13023 | instruction-tuned cousin | **prior** (abstract-level) |
| 19 | LLaGA (Chen) | proceedings.mlr.press/v235/chen24bh | no-GNN result | **V@src** — projector-on-sequences, surpasses graph models sup.+zero-shot ("no GNN" = fair char., see divergences) |
| 20 | GraphPrompter (Liu) | arxiv.org/abs/2402.10359 | GNN-as-soft-prompt | **prior** (abstract-level) |
| 21 | Over-squashing (Alon & Yahav) | arxiv.org/abs/2006.05205 | GNN depth ceiling | **V@src** — over-squashing, GCN/GIN>GAT susceptibility, no-extra-params relief confirmed |
| 22 | Graph scaling laws (Liu) | arxiv.org/abs/2402.02054 | small-size encoder scaling | **V@src** — 100M/50M, depth-matters, nodes/edges metric confirmed |
| 23 | GNN-RAG (Mavromatis) | arxiv.org/abs/2405.20139 | H-GNN-RET precedent | **V@src** — GNN path-reasoner, 7B ≈ GPT-4, +8.9–15.5 F1 multi-hop confirmed |
| 24 | Lost in Serialization (Herbst) | arxiv.org/abs/2511.10234 | serialisation-invariance battery | **V@src** — claims confirmed; venue "ICML 2026 GFM Workshop" stated on page |
| 25 | GTEval (Zhang) | arxiv.org/abs/2605.03514 | delivery≠integration; PRBCD; probe | **V-HTML** — ~50% rephrase drop, PRBCD GCN −73.65% vs text-carrying stable, Fig.4 probe confirmed; **venue NOT shown on arXiv page today (divergence)** |
| 26 | ERNIE (Zhang) | aclanthology.org/P19-1139 | KEPLM anchor | **prior** (abstract-level; lineage verdict inherited) |

**Coverage:** 21 / 26 re-verified at source this session (18 fully; Kautz bib-only; KBLaM
mechanism-only; NLGraph core-only); 5 accepted as `[prior-verified: 2026-07-11]` (uncontested,
abstract-level, non-load-bearing: QA-GNN, Garcez-Lamb, GraphGPT, GraphPrompter, ERNIE). **No
load-bearing citation failed source-verification.**

---

## Divergences from the Fable draft (`docs/next/lit/FUSE.md`)

All divergences found are **minor / provenance-level**; none changes a conclusion. Listed for the
critique record.

1. **G-Retriever ablation — chased, reconciled *in the draft's favour*.** An intermediate ar5iv
   fetch this session reported different ablation numbers (0.5963 / 0.5414, and the *opposite*
   ordering) — but the authoritative **arXiv HTML (Table 6)** reproduces the draft **exactly**:
   w/o graph encoder 54.62 (↓22.51%), w/o textualized graph 56.96 (↓19.19%), graph-encoder removal
   the *larger* drop, PT baseline 48.34. **Verdict: the draft is correct; the divergent ar5iv read
   was a WebFetch small-model extraction artifact.** Recorded as a **numeric-extraction reliability
   caution** (echoing the sibling `lit-p3-sys.md` Q6 finding), not a factual dispute — treat any
   single WebFetch table extraction as provisional.
2. **GTEval venue.** The draft records the venue as "ICML 2026, stated by source only". The arXiv
   abstract page (2605.03514) shows **no venue string** this session (submitted 2026-05-05, no
   conference comment). Substantively unchanged — the draft already flags the venue as UNVERIFIED
   against the ICML programme — but the specific claim "stated by source" is **not reproducible
   today**; downgrade the provenance to "no venue currently listed on arXiv".
3. **Kautz page range.** Draft §1 / `.sources.jsonl` give *AI Magazine* 43(1):**105–125**; a
   secondary listing found this session gives **93–104**. Unresolvable behind the Wiley paywall
   (HTTP 402), non-load-bearing. Flag for whoever has library access.
4. **LLaGA "no GNN at all".** The draft's phrasing is slightly stronger than the PMLR abstract's
   literal wording (which describes projector-on-node-sequences as the *primary* mechanism without
   an explicit "zero GNN anywhere" claim). Substantively fair as a characterization of the
   mechanism; noted as a mild over-precision.
5. **NLGraph "37–58% above random on easy tasks".** A body-level figure in the draft not
   reconfirmed at abstract level this session; the load-bearing NLGraph claims (29,370 / 8 tasks;
   +3.07–16.85%; diminishing prompting benefit; brittleness) *are* confirmed. Non-load-bearing.

**Points of full concordance worth stating:** the draft's central audit verdict (§3 — no matched-
baseline structure-causality win; twice undercut by perturbation probes), its GraphToken
SPOT-REFUTED handling (headline kept baseline-free), its KBLaM mechanism/limitations split
(mechanism primary, limitations UNVERIFIED), its AtlasKV ICLR-2026 upgrade, and its rescoped-
falsifier reasoning all **hold at source**. This formalization adopts them, adds the epistemic
tagging + citation-verification table + the honest broadening to non-fusion neurosymbolic wins
(§3 point 5), and leaves the draft's conclusions intact.
