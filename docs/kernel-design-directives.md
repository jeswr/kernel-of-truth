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
