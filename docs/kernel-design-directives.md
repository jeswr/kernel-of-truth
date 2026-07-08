# Kernel design & research directives (2026-07-08)

Standing directives from Jesse (@jeswr) governing all kernel design and the research
programme. These SUPERSEDE any earlier framing that conflicts with them. In particular
they demote the "SHACL/DL as destination" language in `docs/design-constraint-layer.md`
and the "DL is the right interchange format" language in
`docs/design-dl-from-nsm-and-lean-reconstruction.md` — see §1.

## 1. No semantic-web legacy

- The kernel and its axiom/constraint layer are designed **natively from first principles**
  — NSM-derived constructors (F3's AxiomSchema + semantic-pins path), with formal
  semantics defined on the kernel's **own** terms.
- **RDF, OWL, SHACL, and description logics are NOT design targets, NOT validation
  references, and NOT a "destination."** At most they are an *optional, explicitly-labelled,
  lossy EXPORT projection* for external interoperability — deferred and non-authoritative.
- No semantic-web convention may shape the kernel's identity, vectorisation, or axiom
  formalism. Reusing sparq's *engineering* periphery (canonicaliser, partitioned-row store,
  numeric/enum/taxonomy encoders) is fine; adopting its RDF/SHACL *semantics* as ours is not.
- Clarification of earlier loose wording: where prior docs called DL/SHACL the "right
  interchange format" or where constraint semantics "land"/"the destination," that is
  downgraded here. Meaning lives in the native kernel formalism; any DL/SHACL rendering is a
  downstream lossy view only. Evidence this is the right call: the litmus axiom ("a human has
  exactly two parents, one male, one female") is expressible in the NSM-pinned form but in
  **no** tractable OWL 2 profile — the semantic-web export is the lossy side, not the kernel.

## 2. Two value theses, both measured

- **(A) Correctness** — kernel as external verifier/instrument improves accuracy/correctness
  (the primary track).
- **(B) Efficiency** — kernel makes models **smaller** and/or cuts **inference & training
  compute** at matched-or-better accuracy.
- Every relevant experiment reports the full metric vector: **accuracy/correctness, model
  size (params), memory consumption, compute cost (inference FLOPs/latency/$, training
  FLOPs/steps-to-target)** — Pareto-frontier reporting, not a single number.
- Efficiency claims must beat **strong** baselines: RAG-over-text, distillation,
  quantization/pruning, smaller-model-alone, and the kernel-as-**text** null — not just
  no-intervention. Confront the literature: fixed-semantic concept I/O paid a scaling penalty
  (Meta LCM → CALM dropped it); injected benefits can migrate into weights (InstructRetro).

## 3. The research plan must be operationalisable and follow the scientific method

The plan is not acceptable unless it specifies, up front:

- **Pre-registered HYPOTHESES** — falsifiable; the design-space forks are first-class
  hypotheses, not decisions to defend.
- **Decisive EXPERIMENTS** — each with pre-declared pass/fail **KILL CRITERIA** and an
  explicit model-**SCALE** axis (does the effect appear/vanish/scale with model size?).
- **DATA TRACKING & REPORTING fixed UP FRONT** — a machine-readable experiment **registry**
  (hypothesis, independent vars, dependent metrics, thresholds, analysis all pre-specified),
  an **append-only raw-results log**, and reports **auto-generated from the registry**, so
  outcomes cannot be reframed post-hoc to overstate. This is the primary honesty guardrail.
- **A full STEP + DEPENDENCY plan (a DAG)** so execution is largely **automatable**.
- **GUARDRAILS on the agent(s)** — encoder+corpus **hash-pinning** per run; budget/kill
  caps; concurrency cap; **negative results committed with full statistics**; and
  **separation of run-from-audit** (the agent that runs an experiment never grades its own
  result — positives get independent adversarial verification before any "pass").
- **RESOURCES provisioned up front** — compute, model access across the scale ladder, data,
  budget, with concrete access routes.
- **An OPERATIONAL PLAN** that sees the research to completion.
- **The SKILLS to develop** — reusable automation procedures (e.g. `prereg`,
  `run-experiment`, `flop-meter`, `decode-verify`, `audit-result`, `report-gen`).
- **Specialised AGENT ROLE definitions**, and a map of which role is needed at which stage.

## 4. Don't guess — test

Where confidence is low, do not pick a design and defend it: register it as a **fork**
(options + why-uncertain + deciding experiment + kill-criterion) and let the experiment
decide. The programme's two top questions: (1) is the kernel principle useful to LLMs at all?
(2) if so, which kernel structure is most useful?

## 5. Purely definitional

The kernel is a base set of concept definitions meant to be **agreed upon and widely
understood**. Facts about the world, provenance, and discovery history live in the **world
layer** (stratum 4), never folded into the definitional content-hash. Axiomatic *laws* over
concepts (e.g. the parents rule) live in the endorsed **axiom sidecar** (stratum 3), separate
from concept definitions and out of the canonical vector.

## 6. Honest statistics & literature-grounded extrapolation

- Every experiment carries a **pre-registered statistical analysis plan**: the primary test
  (with justification), **effect size + confidence interval** (never p-values alone), the
  alpha, **multiple-comparison correction** (Holm/FDR) across the pre-declared family, and —
  for any **null claim** — an **equivalence test** (e.g. TOST) with a pre-declared equivalence
  margin. Power / sample size (seeds, corpus size, #concepts) is justified *before* running.
- The per-hypothesis verdict is a **pure function of the pre-declared statistic vs threshold**.
  Negative and inconclusive results are reported with the **same rigor and prominence** as
  positives; no post-hoc test selection.
- **Model-scale extrapolation must be explicit and literature-grounded.** Fit each result as a
  **trend across the scale ladder** (≥3 rungs before any scale adjective), compare it against
  **published scaling-law trends** in the related literature, and state, per finding, the
  model-scale range to which it can **reasonably be extrapolated**, with the uncertainty and
  the assumption that licenses the extrapolation. No toy-scale effect may be presented as
  holding at frontier scale without a measured supporting trend or an explicit,
  literature-referenced caveat.

## 7. Write-up & reporting are part of the programme, not an afterthought

- The programme includes an explicit **write-up phase** producing a scientific paper of a
  standard that could **score well and be accepted at a top-tier venue** in the space — while
  being **completely honest about results, including negative ones** (a rigorous negative
  result is a publishable contribution; do not spin).
- It also includes an **accessible explainer-back step**: after the write-up, the results and
  conclusion are explained to the maintainer in the **clearest possible terms** (plain-language
  what-we-found / what-it-means / what-scale-it-holds-at / go-no-go recommendation).
- Both are **first-class nodes in the operational DAG**, each with an owning agent role and a
  reporting skill, and both are **gated by the honesty system**: every paper claim must trace
  to a registry entry + auto-report, and no claim may exceed what the pre-registered analysis
  supports.

## 8. Auditor identity (maintainer decision, 2026-07-08)

The role-separated auditor of §3 (run-vs-audit separation) is **Codex/GPT-5.5, invoked via
the `codex` CLI** — chosen over a backup Claude account because a different vendor's model
is stronger independence. The audit, adversarial-verification (red-team), and paper.review
roles all run under this cross-vendor identity (P5 R8/R10; P2 G-6/RT-9 as upgraded); the
run-vs-audit separation is therefore cross-vendor, and "independent" is reserved for this
cross-vendor audit, maintainer-level audits, and external replication.
