# Programme-3 Phase-0 cross-pathway synthesis — the matched-resource crux across the ten pathway reviews (delta to feasibility-synthesis-v9) — Rev2

> **Status: ANALYSIS ONLY — a labelled steering read, not a mechanical verdict.**
> **Rev2 (2026-07-23): applies the nine cross-vendor (GPT-5.6) review corrections
> itemised in the closing "Revision 2" section. The bottom line is unchanged and
> cross-model-concordant — re-weight toward the correctness/add-capability thesis, #57
> option (a) first — but the evidential-breadth calibration is corrected: the four
> audit-bearing sweeps move priors MODESTLY, not decisively, and are not
> statistically-independent replications; RAG and STORE are OPEN in both directions.**
> Author: Fable, chief-architect role, 2026-07-23. Nothing here is committed, frozen,
> registered, or ratified by this document; no registry row, verdict, audit, or frozen
> object is touched; the coordinator commits after the cross-vendor review gate and
> surfaces the decision content to the maintainer. Participants are named by role only.
>
> **Relationship to `docs/next/feasibility-synthesis-v9.md` (the standing capstone).**
> v9 §2 already states the Phase-0 crux: the four audit-bearing pathway reviews (FUSE,
> RULE, NTP, PARSE) concordantly locate **no qualifying matched-resource win over a
> neural baseline** in their purposive sweeps, and find every clean reasoning win to be
> **ADD-CAPABILITY**. **This document is not a redo and does not supersede v9.** It is
> the delta the maintainer's steering post (#57) flagged as pending: (a) an independent
> re-read of all ten Phase-0 reviews confirming that v9's statement is faithful to its
> sources; (b) the one thing v9 deliberately does not contain — an explicit
> **per-pathway matched-resource ledger across all ten reviews**, including the six
> pathways outside v9 §2.1's four-sweep scope; and (c) the resulting cross-pathway
> verdict and decision framing, stated in one place for the #57 record.
>
> **Provenance discipline.** Every literature finding below carries the
> **verification status inherited exactly from its owning review** — the reviews'
> citation-verification tables mix `[search: 2026-07-19]` (re-verified at source this
> session), `[prior-verified: 2026-07-11]` (accepted from the earlier pass), secondary,
> `[memory]`, `[claimed]`, and `[UNVERIFIED]`; this document does **not** re-fetch or
> upgrade any of them and does not claim blanket primary-source verification. Findings
> are recalled from the review texts, re-read in full this session. Where a review
> flagged `[UNVERIFIED]`, that flag is carried, never upgraded. The reviews' own
> `[established]/[claimed]/[speculative]` subtags are preserved on every use.
> **Sentence discipline:** where a row states a published number it is a source-fact at
> the review's inherited status; where it states "matched? / clears the bar?" it is a
> cross-paper **audit-judgement** (the owning review's, carrying its
> `[speculative]/direction-only` subtag), never a source-fact.

Epistemic tags: **[MEASURED]** — programme instrument output, cited to its registry
object; **[LIT-BACKED]** — literature finding via a named source-verified review;
**[STIPULATED]** — a scoping choice or reading discipline adopted here;
**[EXTRAPOLATION]** — direction-only, never a premise of anything in this document.

---

## 1. What v9 already settles — confirmed, not duplicated

**[STIPULATED — reconciliation audit, performed over the full texts of the ten reviews
and v9 this session]**

1. **v9 §2.1 (the concordant 4-pathway finding) is faithful to its sources.** I re-read
   `reports/lit-p3-{fuse,rule,ntp,parse}.md` in full against v9's statement. Each review
   ran the same fair-accounting audit (same information + trainable parameters +
   training compute + structure-causality by perturbation) and each returned the same
   answer at the same honestly-bounded scope: *no qualifying matched-resource win
   located in a purposive, non-systematic sweep; every clean reasoning win found is
   add-capability*. No overstatement was found in v9's rendering; its co-read
   scope-tightenings (sweep-scoped language; the memory-layers exception named; the
   reviews' [speculative] subtags carried) are all present and correct.
   **Critical calibration [STIPULATED], carried into every downstream sentence:** the
   four sweeps are **not statistically-independent replications** — they share an audit
   frame (the RULE review explicitly adopted FUSE's accounting frame so the pathways
   could be read side by side), a common pipeline and reviewer role, and a prior-draft
   lineage. Concordance across them therefore **moves priors modestly, not decisively**;
   a defect in the shared frame would correlate across all four. "Reproduce the bounded
   FUSE result" is the correct phrase; "independent confirmation" is not.
2. **v9 §2.2–§2.4, §3, §6–§7 already carry the licensing statement, the H-DD-specific
   deflation, the peripheral convergences, and the #57 (a)/(b)/(c) decision framing**
   (with a labelled lean to (a) as [EXTRAPOLATION]). Those sections remain the standing
   text; nothing below amends them.
3. **What v9 does not contain**, and this delta supplies: v9 scopes its concordance
   claim to the four audit-bearing sweeps and treats the other six reviews as
   convergences (§2.4). The #57 crux question — *does the FUSE finding hold across the
   OTHER pathway reviews, or does some pathway break it?* — deserves an explicit
   per-pathway answer over all ten, including the honest statement of what kind of
   evidence each non-audit pathway could even have contributed. That ledger is §2.

---

## 2. The per-pathway matched-resource ledger (all ten Phase-0 reviews)

**[LIT-BACKED throughout, via the named review; each row's audit verdict carries the
owning review's own [speculative]/direction-only subtag; the "verdict" column is that
review's, confirmed by re-read — not a new audit]**

| Pathway (review) | Strongest matched-resource candidate located | Why it does / does not clear the bar | Matched-resource win? |
|---|---|---|---|
| **FUSE** — GNN–LLM fusion (`lit-p3-fuse.md` §3) | G-Retriever, frozen host: +22.15 Hit@1 abs over a *trained* prompt-tuning baseline on ~1.4k-node KGQA; dual ablation shows both channels load-bearing `[established]` | Not trainable-param-matched (GNN+projector > soft prompt); the graph encoder also reads text attributes, so component contribution ≠ topology causality; **no edge/label shuffle run**; delta collapses to +1.8–11.7% relative under LoRA. Two **external warnings** make structure-attribution unsafe — Deceive-KG (targeted perturbation, on *earlier* KG-augmented systems) and GTEval's PRBCD result (on *related* soft-token models) — but **neither directly perturbs G-Retriever**, so they are warnings, not negative replications of it | **No** — trained-bridge signal is real; structural integration never established |
| **RULE** — rule-injection (`lit-p3-rule.md` §4) | Memory Layers at Scale: beats dense at >2× compute AND beats MoE at **matched compute + total params** — a genuine learned-memory *architecture* efficiency precedent `[established]` | It **does break the broadest formulation** ("no matched-resource architecture win located"): the MoE comparison matches total params, so "params-up" does not defeat it, and the paper reports gains beyond facts (multi-hop QA, coding, MMLU). Its reach is bounded, not dismissed: it is a *trained-from-pretraining* architecture (not a training-free frozen-host store); deployment bytes / bandwidth / optimizer state / lifecycle are **outside the paper's match**; and transfer to kernel-style *rule inference / exact reasoning* is **unestablished**. Elsewhere on the pathway: CD+executor wins are same-host ablations with unpriced engine work (CRANE emits *more* tokens than unconstrained CoT); steering and editing **lose** their matched comparisons (AxBench: prompting wins; RippleEdits: in-context wins) | **No for the programme-relevant claim** (symbolic rule inference / exact reasoning / training-free frozen-host store); Memory Layers is a real learned-memory-architecture exception whose transfer to reasoning is unestablished |
| **NTP** — theorem proving / differentiable logic / NAR (`lit-p3-ntp.md` §6a) | Polu expert-iteration: the field's only "same compute budget" claim (verified verbatim) `[established]` | Both arms already have the sound checker — a **within-executor allocation** result, not NeSy-vs-baseline-lacking-the-executor. Discrete-NAR (strongest overall: perfect scores + provable correctness for any test data) gets its guarantee from a hard discrete interface + state supervision the baseline structurally lacks — add-capability. Goedel-8B / Pythagoras-4B > 671B are sample-count-pinned parameter-efficiency results between two *neurosymbolic* systems (MoE comparator ⇒ ~5×/9× active-param, not 80×/167×) | **No** — every demonstrated win adds an exact-reasoning capability |
| **PARSE** — semantic parsing / program synthesis (`lit-p3-parse.md` §2b, §3) | Grammar-constrained decoding: same frozen host + masked softmax; beats even task-specific fine-tuned models where data is scarce, with **real task-F1/accuracy gains** (entity disambiguation, constituency-parsing F1), not merely fewer invalid outputs `[established]` | A **strong same-host, near-compute-matched, add-structure candidate whose full matched-information/resource status is UNESTABLISHED** — it adds an incremental parser + CPU (material overhead on some tasks), and the grammar/candidate set supplies external task structure whose total compute/information parity is unaudited; it is *not* "compute-matched by construction" and *not* "validity-only". It does not close the S2 correctness gap (a valid-but-wrong program — the a5-nl ROLE_DIR class — passes every grammar). Execution-feedback wins (EGD, MBR-EXEC, LEVER, TinyGSM) add the executor and/or unmatched teacher data (TinyGSM: 12.3M GPT-3.5-synthesized problems) — add-capability, and the **cleanest add-capability attribution of any pathway**: the executor's contribution is architecturally explicit, with no "is it really using the structure?" confound | **No matched win established**; the strongest sub-candidate (grammar-constrained decoding) is near-matched add-structure, parity unaudited |
| **RAG** — retrieval / tool-use baselines (`lit-p3-rag.md` Q1/Q6) | Non-identification: every "small beats large" retrieval result (kNN-LM, RETRO, Atlas, MassiveDS) charges parameters but not the index; ≤2B tool-use wins are domain-narrow (TinyAgent: 16 tools, off-ledger selector) or task-scoped (APIGen) `[established]` per system; the deployment-bytes-inclusive synthesis is the review's `[EXTRAPOLATION]` | **NOT corroborating negative evidence.** The deployment-bytes-inclusive, matched-total-resource fair comparison **has been run by no one, in either direction** — so this is non-identification, not a concordant register. Companion warning (a design input, not evidence for the crux): the kernel's most dangerous comparator is a boringly-competent typed-store RAG at matched bytes, a cell the field supplies no instrument to separate from "kernel semantics" | **OPEN / UNESTABLISHED BOTH DIRECTIONS** — never counted as a concordant register |
| **SURG** — compression / model surgery, the H-DD shrink pathway (`lit-p3-surg.md` §1, §4) | **Two strong candidates lacking a complete ledger:** (i) LmLm-382M ≈ LLaMA2-7B on factual-precision benchmarks `[established]` — a store-backed small model, the closest published analogue to H-DD's *end state*; (ii) Minitron — real iso-compute pruning+KD, comparable to Mistral-7B/Gemma-7B/Llama-3-8B `[established]` | Both are **candidates whose full ledger is not matched**: LmLm trains a *new* model (no donor surgery, no identified subspace, flat fact-DB not a typed kernel) and its DB bytes are outside the size claim; Minitron is iso-compute with *unequal tokens* (KD pays the teacher's forward passes) and Sheared-LLaMA's "3%" *excludes donor pretraining* — derived-artifact economics, not matched-total-resource wins. On the crux the pathway adds three verified geometry-level threats to the H-DD chain (superposition ⇒ concept↔coordinate granularity mismatch; the located store-backfill evidence concerns **facts** — no computation-restoration result was located; localisation ≠ editability), plus small donors having *less* slack (SliceGPT ~99% retention at 66–70B → 90% at 2.7B). Threats, not impossibility proofs; the cheap interventional gate P3-E-DD-0 is correctly targeted | **No matched win established**; strong candidates lack a complete ledger; pathway-specific deflation of the efficiency bet |
| **EVAL** — index methodology (`lit-p3-eval.md`) | n/a — a methodology review; contains no architecture-win claims | Conditions *how* any future win could be claimed: a scalar-defined win condition inherits the scalar's construct-validity indefensibility; proxy-rung (R-0/R-1) results **kill reliably but certify nothing** | **N/A** — no counterexample |
| **TINY** — tiny-model training (`lit-p3-tiny.md` §1) | n/a — methodology; no NeSy-vs-baseline claims in scope | Constrains W1 claim shape: no academic-budget twin can be compute-matched to a released anchor (SmolLM2-1.7B is ~325× Chinchilla-overtrained), so twin claims are from-scratch-vs-from-scratch only; ~20% of small-scale decisions flip at 8× scale (DataDecide) | **N/A** — no counterexample |
| **STORE** — store economics (`lit-p3-store.md` §1) | Non-identification: the sweep located no matched-cost store-vs-learned-baseline comparison in either direction (absence-of-evidence, stated as such) | Store maintenance is a **proven risk, unproven doom** (XCON was a success with a tooling fix; Freebase consolidated on Wikidata's success, not a stated unsustainability finding); the genuinely open cost is refresh TCO — measure, don't assume. Prices the lifecycle side of any claim on either thesis, and does not corroborate the crux in either direction | **OPEN / UNESTABLISHED BOTH DIRECTIONS** — never counted as a concordant register |
| **SYS** — lifecycle / systems measurement (`lit-p3-sys.md`) | n/a — measurement methodology (MLPerf scenarios, power, latency percentiles, warm/cold, Sardana volume-dependent sizing carried qualitative-only) | Supplies the cost-measurement rig any matched-resource claim would need; makes no win claims | **N/A** — no counterexample |

**Reading notes on the ledger [STIPULATED]:**

- The bar the four audit-bearing reviews applied is **stricter than field practice** —
  each says explicitly that a win clearing it would be "above anything in the
  literature." That is the correct bar for Programme-3's W1, and it is why "no
  qualifying win located" is informative rather than trivially true: the reviews *did*
  locate many wins; the audit is about what those wins are wins *of*.
- The **kernel-as-text null** belongs in this frame wherever a store-touching win is
  read: the FUSE control set carries it as mandatory (control (g), kernel-as-text at
  matched token budget), and the programme's own measured record is that text-delivered
  grounding was **net-harmful** at the seam tested (nsk1-g2d 0.76 → 0.43, 0/24 rescues)
  and that kernel content was TOST-equivalent to matched generic stores at the content
  seam (knull-v2 NULL/PASS-GENERIC) **[MEASURED: registry/assessments/nsk1-g2d.json;
  knull-v2 per v9 §4 Tier-1]**. No literature row above weakens either datum.

---

## 3. The cross-pathway verdict

**Does the P3-LR-FUSE finding hold across the other Phase-0 pathway reviews?**

> **The bounded FUSE result is reproduced by the three other audit-bearing sweeps and is
> contradicted by none of the remaining six — but the evidence topology is narrower than
> "holds across all ten," and is stated precisely as follows.**
>
> **(i) Four audit-bearing sweeps (FUSE, RULE, NTP, PARSE)** each ran the fair-accounting
> audit and each **reproduces the same bounded result**: no qualifying matched-resource
> win over a neural baseline was *located* for the programme-relevant capabilities, and
> every clean reasoning win found is **add-capability** (an engine supplying soundness,
> exhaustive/exact deduction, a provable OOD guarantee, or a hard exact interface the
> baseline structurally lacks). These four are **not statistically-independent
> replications** — they share an audit frame (the RULE review explicitly adopted FUSE's),
> a pipeline, a reviewer role, and a prior-draft lineage — so they move priors
> **modestly, not decisively**; a shared-frame defect would correlate across all four.
>
> **(ii) The one located matched-resource exception — Memory Layers (RULE)** — breaks the
> *broadest* formulation ("no matched-resource architecture win"): it beats MoE at
> matched total params/compute and reports gains beyond facts (multi-hop QA, coding,
> MMLU). It does **not** break the **narrow, programme-relevant crux**, which is what the
> re-weight rests on: *no matched-resource win was located for symbolic rule inference,
> exact reasoning, topology-causal fusion, or a training-free frozen-host store* — Memory
> Layers is a trained-from-pretraining learned-memory architecture whose
> deployment-bytes / bandwidth / optimizer-state / lifecycle match is absent from the
> paper and whose transfer to kernel-style reasoning is unestablished.
>
> **(iii) RAG and STORE are OPEN in both directions** — the fair, ledger-complete
> comparison has been run by no one; these are non-identification, **not** concordant
> corroborating registers. The remaining reviews (SURG, EVAL, TINY, SYS) **establish no
> contradiction** but do **not independently confirm** the crux either; SURG additionally
> deflates the H-DD efficiency architecture on geometry grounds and surfaces store-backed
> candidates (LmLm-382M, Minitron) that lack a complete ledger.
>
> **Net:** the narrow crux is **reproduced by four non-independent audit sweeps,
> contradicted by none of the ten, and independently confirmed by none of the other
> six** — a modest, honestly-bounded prior shift toward add-capability, not a decisive
> cross-pathway law.
>
> **[LIT-BACKED: via the ten reviews `reports/lit-p3-*.md` at their inherited
> verification statuses; the audit verdicts carry the reviews' own
> [speculative]/direction-only subtags; all sweeps are purposive and non-systematic, so
> every verdict is "no qualifying win LOCATED", never "none exists" — a lower bound on
> the literature, not an impossibility theorem]**

Two honest boundary statements, so the verdict cannot be over-read:

1. **Concordance is not independence-of-error** (load-bearing). The four audits share an
   accounting frame (deliberately — the RULE review adopted FUSE's frame so the pathways
   could be read side by side), a pipeline, and a prior-draft lineage, so a defect in the
   frame would correlate across them. The frame's components (params, training compute,
   information, perturbation-causality) are standard fair-comparison practice
   individually; the correlated-error risk is judged low but is named, and is the reason
   the shift is characterised as **modest**. **[STIPULATED]**
2. **The verdict moves priors and designs, never verdict-words.** Both programme theses
   remain INCONCLUSIVE-PENDING; the four-condition scoreboard is 0–0; nothing here is a
   measurement of this programme's kernel (v9 §0, §5 — carried, not restated).
   **[MEASURED (registry state) + STIPULATED (discipline), per v9]**

---

## 4. The steering implication — correctness vs efficiency

**[STIPULATED reading of LIT-BACKED and MEASURED constituents. The weighting is
[EXTRAPOLATION]: it is a premise of no MECHANICAL verdict, but — stated honestly — it
**is** a premise of this document's #57 recommendation and the HOLD/sequencing calls
below; those are DECISION INPUTS, not literature-backed consequences. This is a labelled
steering read, not a ratified verdict.]**

The evidence **does** re-weight Programme-3 toward the correctness (checker) thesis and
the add-capability framing, and away from the efficiency/fusion framing — on three
legs, at the modest strength §3 established:

1. **The efficiency thesis is without located precedent at matched resources** in the
   four audit-bearing sweeps (with the narrow-crux scoping of §3: Memory Layers is a
   located learned-memory-architecture exception whose transfer to reasoning is
   unestablished; RAG/STORE are OPEN, not corroborating), and its most aggressive
   architecture (H-DD) carries three verified geometry-level threats. An efficiency win,
   if it exists, would be above anything located: expect the null, and design so the
   null is informative (the RULE review's own words). This does not retire W1 — lack of
   located precedent is not impossibility, and W1 remains a legitimate, falsifiable
   target — but it prices W1-first sequencing as the option most likely to spend the
   programme's budget where the located literature predicts a null. **[LIT-BACKED as §3]**
2. **Every clean win the sweeps located instantiates the correctness thesis's shape** —
   a deterministic engine owning a class of exact reasoning, fail-closed behaviour, or
   provenance the baseline cannot have (Logic-LM, CD+executor, Discrete-NAR, the
   AlphaGeometry-class systems). The kernel programme's distinctive assets (µs
   deterministic engine, exact fail-closed checking, byte-identical portability,
   provenance-carrying records) are add-capability assets. Two candidate seams where the
   µs property may be a genuine differentiator are flagged by the reviews as **empty
   cells with no located precedent**: per-token semantic-executor consultation in the
   decode loop, and coverage-aware abstention-preserving constrained decoding.
   **[LIT-BACKED: lit-p3-ntp §6, lit-p3-rule §2.1 — "no precedent found in this
   search", not "none exists"]**
3. **What the re-weight does NOT license — the attribution boundary [MEASURED].** The
   literature's add-capability wins belong to *engines and executors generally*, not to
   NSM-kernel semantics specifically. The programme's own record is unmoved: zero
   audited end-task wins over the kernel-as-text null attributable to kernel content;
   knull-v2 content-interchangeability; the f2b alignment confound; the RAG review's
   warning that the field has no instrument separating "kernel semantics" from "any
   typed store + checker" — that instrument is the programme's own (the F1-K K-3
   co-primary and the gsx0 diagonal, both frozen, neither run; F1-K condition-(i)
   carrier validity unresolved, any result proxy-provisional). A correctness re-weight
   is a re-weight of *where to look*, not a finding that the kernel is what will be
   found there.

**The one-sentence steering read:** the **most defensible place to test for** the
kernel's value is a **priced, fail-closed, add-capability correctness claim** (risk /
coverage / dangerous-wrong machinery, adjudicated against the kernel's own falsifiers —
matched generic stores above all), with efficiency retained as a falsifiable secondary
target rather than the headline; the **most relevant currently frozen probes** for
whether *this kernel specifically* carries that value already exist (F1-K, gsx0) and are
the correct next spend — **conditional on their stated validity and asymmetric-licensing
limits** (F1-K condition-(i) carrier validity is unresolved so any result is
proxy-provisional, and its K-3 leg carries no licensed-negative rule; these are not
"deciding" instruments while those hold). **[EXTRAPOLATION — direction-only; a premise of
this document's recommendation, of no mechanical verdict]**

---

## 5. The material decision for the maintainer (the #57 record, confirmed and completed)

**[STIPULATED framing; the decision is the maintainer's and is NOT taken here. Per the
2026-07-22 handoff state, #57 is surfaced and unanswered; this document is the
"pending Fable synthesis" input the steering post named. The coordinator should attach
§2–§4 (or this document) to the #57 thread as the completing evidence.]**

**Decision:** what standing does a correctness endpoint family get in Programme-3's
success criteria and the KOT-FAIR/2 freeze, now that the Phase-0 crux is reproduced
(modestly, per §3) across the audit-bearing pathways?

| Option | Content | Chief consequence |
|---|---|---|
| **(a) Co-equal claim family** | A second, non-composite, claim-capable correctness family (unconditional dangerous-wrong bounds, selective risk, coverage at frozen risk — the freeze-readiness review's Part C machinery) stands beside an intact W1 | The thesis the evidence points at becomes adjudicable without conjoining it to an efficiency bar with no located precedent; W1 survives as a falsifiable target; two claim surfaces to govern |
| **(b) Conjunctive W1 gate** | Correctness endpoints become an additional condition on the existing W1 claim | One claim surface; but a defensible correctness win would remain unclaimable absent a simultaneous W1 pass — the conjunction the sweeps price as most likely to leave real value unclaimed (lack of located precedent is not impossibility) |
| **(c) Separate Pareto axis** | Correctness joins bytes/cost/index as an axis of a published Pareto surface | Maximally informative; **not gaming-resistant as written** — a Pareto surface with no frozen dominance/reference rule invites post-hoc narrative selection; to rival (a) it would need a frozen reference point + a frozen decision rule bolted on |

**Recommendation [EXTRAPOLATION — direction-only, concurring with the independent GPT-5.6
review, which ranks (a) > (b) > (c), and with v9 §3's labelled lean]: (a), with
anti-gaming guardrails.** The cross-pathway reproduction and the correctness-shape of the
programme's only frozen candidate instrument both point at (a); the
efficiency-conjunction cost of (b) is priced by the audit sweeps. **(a) is only
defensible with the following guardrails frozen with it [STIPULATED requirements]:**
(1) a **frozen endpoint hierarchy** (primary correctness endpoint pinned before any run,
no post-hoc promotion); (2) a **coverage floor** (a correctness claim is void below a
pre-registered covered fraction, so a high score on a thin covered slice cannot headline
— the coverage rider does binding work here); (3) an **unconditional dangerous-wrong
bound** (not only selective risk — abstention must not launder confident-wrong outputs);
(4) **multiplicity control** across correctness endpoints and comparators (family-wise,
pinned at freeze); (5) **explicit reporting language** that distinguishes a
**"correctness-only success"** from a **"W1 (efficiency-frontier) success"** on every
claim surface, so neither is ever read as the other. **(c) is the defensible alternative
only if a frozen reference point + decision rule are added** (without them it is
gaming-exposed, not gaming-resistant); **(b)** is the option this synthesis's evidence
argues against.

**Bundled second-order components** (name them in the same ruling so execution unblocks
cleanly) **[EXTRAPOLATION / DECISION INPUT — plan-shaping, not a literature-backed
consequence]**:

1. **Efficiency-architecture design work** (P3-D-DD / P3-D-GNN / P3-D-RULE — deliberately
   not designed pending #57): confirm HOLD until a correctness-first wave produces its
   first four-condition number, or explicitly release. The cross-pathway read supports
   HOLD; the H-DD cheap interventional gate (P3-E-DD-0) remains the correct first probe
   *if* released. **[EXTRAPOLATION / DECISION INPUT]**
2. **Sequencing:** the correctness instruments that already exist frozen (F1-K on its
   maintainer GO, proxy-provisional on carrier validity; gsx0) are the next informative
   spend on this decision's critical path; Phase-1 revisions and the KOT-FAIR/2 Part-C
   machinery unblock on the (a)/(b)/(c) ruling itself. **[EXTRAPOLATION / DECISION
   INPUT]**

---

## 6. What would change this read

**[STIPULATED — falsifiers for the steering read, so it dies cleanly if wrong]**

1. A systematic (logged-protocol) search locating a qualifying matched-resource
   reasoning win the purposive sweeps missed — the verdict is a lower bound and says so.
2. The programme's own sweeps producing one: a P3-E-GNN-1 depth-increasing fusion
   advantage surviving shuffle + structure-attack at matched budgets, or a glm-s4drop-0
   PASS surviving its kernel-vs-generic follow-up — either would put the efficiency
   thesis above the literature and force a re-weight back.
3. F1-K returning a licensed K-3 negative (which would additionally require the
   pre-registered futility/equivalence rule the frozen record does not contain — v9 §7)
   plus a gsx0 close-out against kernel attribution: that would deflate the
   *kernel-specific* correctness bet even as the add-capability frame stands.

---

## Revision 2 — cross-vendor review corrections applied

**[STIPULATED — revision record. The GPT-5.6 cross-vendor review returned
NEEDS-REVISION on Rev1; the bottom line (re-weight toward correctness/add-capability;
#57 option (a) first) is cross-model-concordant and unchanged. All nine items applied;
disposition below.]**

1. **Recalibrate the evidence topology — ADOPTED.** "Five concordant registers" and
   "holds across all ten" removed programme-wide. §3 restated as: four audit-bearing
   sweeps (FUSE/RULE/NTP/PARSE) **reproduce** the bounded FUSE result; the other six
   **establish no contradiction but do not independently confirm** it; RAG and STORE are
   **OPEN both directions**. The four audits are flagged as **not
   statistically-independent replications** (shared frame/pipeline/prior-draft lineage) →
   they move priors **modestly, not decisively**. Downstream (§4, §5) recalibrated to
   this structure.
2. **Memory Layers (RULE) — ADOPTED-WITH-MODIFICATION.** No longer "params-up / factual
   recall only." Reframed as a **genuine learned-memory-architecture efficiency precedent
   at matched total params/compute vs MoE, reporting gains beyond facts** — it **breaks
   the broadest formulation**. The crux is narrowed to the programme-relevant claim (no
   matched-resource win located for symbolic rule inference / exact reasoning /
   topology-causal fusion / training-free frozen-host store), with deployment
   bytes/bandwidth/optimizer/lifecycle disclosed as outside the paper's match and
   reasoning-transfer unestablished.
3. **PARSE grammar-constrained decoding — ADOPTED.** Reclassified from "compute-matched
   by construction / validity-only" to a **strong same-host, near-compute-matched,
   add-structure candidate whose full matched-information/resource status is
   unestablished** (incremental parser + CPU overhead; grammar supplies external task
   structure; real task-F1/accuracy gains cited) — the cleanest add-capability
   attribution of any pathway.
4. **FUSE probe language — ADOPTED.** Deceive-KG and GTEval relabelled as **two external
   warnings that make structure attribution unsafe**, explicitly **not** negative
   replications of G-Retriever (neither perturbs it directly).
5. **RAG — ADOPTED.** Relabelled **OPEN / UNESTABLISHED BOTH DIRECTIONS** (non-
   identification; fair comparison never run either way); removed from any "concordant
   register" role.
6. **SURG ledger — ADOPTED.** Now surfaces **LmLm-382M (≈ LLaMA2-7B factual precision)
   and Minitron (real iso-compute)** as **strong candidates lacking a complete ledger**
   (DB bytes / training data / total compute / lifecycle unmatched), replacing "no win
   claim."
7. **Steering-implication overreach — ADOPTED (three phrases).** "literature-supported
   home of the kernel's value" → "most defensible place to test for value"; "the deciding
   instruments" → "the most relevant currently frozen probes, conditional on their stated
   validity + asymmetric-licensing limits"; HOLD + sequencing re-tagged
   **[EXTRAPOLATION / DECISION INPUT]**, not literature-backed consequences.
8. **Epistemic hygiene — ADOPTED.** [EXTRAPOLATION] disclosed as a premise of the
   recommendation/HOLD/sequencing (of no mechanical verdict); "backfill proven only for
   facts" → "the located evidence concerns facts; no computation-restoration result was
   located"; blanket "primary-source verified" → **"verification status inherited exactly
   from the owning review"**; source-facts vs cross-paper audit-judgements separated in
   the provenance discipline.
9. **#57 recommendation — ADOPTED (a) STANDS + guardrails.** (a) kept (GPT-5.6
   independently ranks (a) > (b) > (c)); the five anti-gaming guardrails now specified
   (frozen endpoint hierarchy; coverage floor; unconditional dangerous-wrong bound;
   multiplicity control; explicit correctness-only-vs-W1-success reporting language); (c)
   flagged **not gaming-resistant as written** (needs a frozen reference point + decision
   rule to rival (a)).

---

## Self-check (mandatory, performed last)

1. **Every pathway addressed on the matched-resource question** — §2's ledger has one
   row per review, all ten (FUSE, RULE, NTP, PARSE, RAG, SURG, EVAL, TINY, STORE, SYS),
   each with its strongest candidate (or an explicit n/a with the reason) and a
   does/doesn't-clear-the-bar statement. ✅
2. **The cross-pathway verdict is explicit and epistemically tagged** — §3 states it in
   a single block-quoted verdict carrying [LIT-BACKED] with the reviews'
   [speculative]/direction-only subtags and the "located, never none-exists" scope
   bound; the two over-reading guards are stated. ✅
3. **Reconciled with feasibility-synthesis-v9 — confirm/extend, not duplicate** — §1
   records the faithfulness audit of v9 §2 against the ten source texts (confirmed, no
   overstatement) and adds the load-bearing non-independence calibration; the delta
   contributes only what v9 lacks (the ten-pathway ledger, the explicit
   reproduced-not-independently-confirmed statement, the RAG/STORE OPEN labelling, the
   completed #57 framing + guardrails); v9's sections are pointed to, not restated. ✅
4. **The maintainer decision is framed with options and a recommendation** — §5:
   (a)/(b)/(c) with consequences, recommendation (a)+guardrails tagged [EXTRAPOLATION],
   concurring with (not replacing) the independent GPT-5.6 ranking and v9's lean; the
   five anti-gaming guardrails and the (c)-needs-a-frozen-reference-rule caveat are
   stated; the decision is marked as the maintainer's and not taken; two bundled
   second-order components tagged [EXTRAPOLATION / DECISION INPUT]. ✅
5. **Evidence topology stated at its true strength** — no "five concordant registers"
   and no "holds across all ten" survive; §3 states reproduced-by-four-non-independent /
   contradicted-by-none / independently-confirmed-by-none, with RAG+STORE OPEN and Memory
   Layers scoped to the narrow crux. ✅
6. **Epistemic hygiene** — verification status is stated as inherited-from-owning-review
   (no blanket primary-source claim); source-facts vs audit-judgements are separated in
   the provenance discipline; [EXTRAPOLATION] is disclosed as a premise of the
   recommendation/HOLD/sequencing (not of any mechanical verdict); "backfill proven only
   for facts" is replaced with "the located evidence concerns facts; no
   computation-restoration result was located." ✅
7. **No minted `ASM-` ids** — checked over the final text: no `ASM-<number>` string
   appears anywhere; registry rows are referred to only via their owning documents. ✅
8. **No account or handle strings** — checked: participants appear only as
   Fable / coordinator / maintainer / the owning review's role; no emails, no handles. ✅
9. **Nothing committed, registered, frozen, or ratified** — this document performs no
   git, registry, bead, or freeze operation and says so in Status; every conclusion is
   tagged as a labelled steering read; the #57 decision remains the maintainer's. ✅
