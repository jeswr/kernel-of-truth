# N-H — The idea + permutation registry (never-lose ideas; make them permutation-testable)

**Kernel of Truth programme — meta-mechanism, node N-H.**
Author: architecture-advisor (Fable), for @jeswr, at Kern's request. Date: 2026-07-09.
Status: **DESIGN + partial build.** This document + `registry/ideas.jsonl` (the machine-
readable seed) exist as of this node. It creates NO experiment entry, freezes nothing,
spends nothing. Binding constraints: `docs/kernel-design-directives.md` §§1-4/6;
`docs/next/research-engine.md` (N-B — the candidate backlog this feeds);
`docs/next/assumption-register.md` (N-G — the epistemic-tag gate that binds it).

**Purpose in one sentence.** A structured registry so that every architectural idea —
across kernel / encoder / model / seam, and *parts* thereof — is (1) never lost and
(2) comprehensively permutation-testable, with a resource-aware NOW-list feeding the
research engine and a mechanically-enumerable DEFERRED full sweep for when the programme
is less compute-constrained.

## 0. Honesty boundary (binding, mirrors N-C §0 and N-G)

The idea registry is **ideation / backlog infrastructure, NOT evidence.** An idea entry's
`epistemic` tag reports the status of its *core claim* per its refs; it is NOT a claim that
the idea works. No idea entry may be cited as evidence, and an idea is NOT a decision: it
carries none of N-G's load-bearing markers and premises nothing (the marker-lint therefore
does not fire on it). An idea becomes load-bearing only when it is promoted to a research-
engine **candidate** (N-B §1.1) and pre-registered — at which point its STIPULATED premises
are registered in `registry/assumptions.jsonl` (ASM-ids) and its status is decided by a
verdict, not by this file. Reconciliation note: the existing `architecture-ladder.md`
(L0-L4 + L2c) is a **partial, hand-built instance** of this registry — its rungs are
seeded here (`ladder_ref`), and its cheapest-decisive-first ranking is one view of §4's
NOW-list.

---

## 1. The decomposition taxonomy — (architecture x part) slots

An architecture is decomposed into **slots**: loci where a design choice is made. A slot is
`(architecture, part)`. Four architectures, their parts (refined from the tasking):

| architecture | part | what varies at this slot |
|---|---|---|
| **kernel** (definitional identity content) | `vocabulary-basis` | the atomic basis: NSM-65 + optional molecule / physics-Z7 / math-Metamath / code-construct extensions |
| | `construction-op` | the record grammar (kot-ast/1 caps, frames, AND-under-op X1, apply-clause X5) |
| | `axiom-layer` | kot-axiom/1 sidecar expressivity (stratum 3): v0 validation ops vs +bounded rules |
| | `world-layer` | stratum-4 fact store: population route + coverage |
| **encoder** (definition -> vector, deterministic) | `input-parse-canonicalise` | the mapper: phrase->concept, input canonicalisation |
| | `basis-assignment` | atom->codebook-row assignment, D, whitener |
| | `binding-op` | the composition algebra (construction B; alt: TPR-exact, WL+CS; +box taxonomy lane) |
| | `structured-data-parser` | deterministic code/math/config -> concept parser (idea A) |
| | `similarity-decode` | decode-verify, polarity-aware / structural-decode similarity (X3 mitigation) |
| **model** (the LLM) | `embedding-tokenisation` | input embedding table (A1 frozen rows), concept-dense input (L1b) |
| | `inter-layer-activation` | kernel-labelled bottleneck (L2a), symbolic inference between layers (idea B) |
| | `attention` | kernel-addressed memory layer (L2b), MoE expert labelling |
| | `output-head-decoder` | output head; concept-hash emission; record-constrained decode; structured output (idea A) |
| | `training-schedule` | from-scratch vs frozen; scaffolding; gradual-introduction; axiom/RDM regularisers |
| **seam** (kernel<->model topology) | `verifier` | external decode-verify (A5/F2) |
| | `adapter` | trained affine bridge (A2), concept-toolkens |
| | `in-tokenisation` | input canonicaliser (L1a), concept-dense I/O (L1b) |
| | `in-layer` | bottleneck (L2a), phi-fixedness (L2c), A6/MoE instruments |
| | `rules-engine` | the L3 family (oracle / routed / in-decode), idea B's inference step |
| | `memory-layer` | kernel-addressed KV (L2b) |

The split that resolves the tasking's kernel/encoder overlap: **kernel = symbolic identity
content** (`construction-op` is the record grammar, in the hash); **encoder = the
symbolic->vector map** (`binding-op` is the vector algebra). An idea usually touches several
slots — the schema (`slots[]`) carries a list, each with a `role` ∈
{add, replace, toggle, parametric}.

---

## 2. The idea-entry schema — `kot-idea/1`

One JSON object per line in `registry/ideas.jsonl` (canonical, append-history like the rest
of `registry/`; for a given `id` the last line is current). Fields:

| field | meaning |
|---|---|
| `id` | stable slug `idea-<slug>` (referenced by other entries' compatibility/deps) |
| `title`, `idea` | short name; one-paragraph statement of the idea |
| `slots[]` | `{architecture, part, role}` — which (architecture,part) it modifies, and how |
| `mechanism` | what computes what, where |
| `epistemic` | MEASURED / LIT-BACKED / STIPULATED / EXTRAPOLATION — status of the CORE claim |
| `epistemic_refs[]` | backing: `verdict:<id>`, `poc:<exp>`, `lit:arXiv:...`, `doc:<path>`, `assume:ASM-####` |
| `compatibility` | `{alternative_to[], orthogonal_to[], requires[], conflicts_with[]}` — the permutation-filter graph |
| `dependencies[]` | ideas/artifacts that must exist first |
| `feasibility` | `{cost_tier 0-4, readiness ready|blocked, blocked_on[]}` |
| `decisiveness` (1-5) | how many live routes/laws a result would move |
| `uncertainty` (1-5) | genuine coin-flip (5) vs literature/ledger effectively decides it (1) |
| `leverage` (1-3) | does the work product (engine, corpus, instrument) serve other ideas |
| `source` | maintainer / literature / advisor / experiment |
| `ladder_ref` | link to an architecture-ladder rung (L0-L4) if any |
| `candidate_ref` | filled when promoted to a research-engine candidate / experiment id |
| `status` | idea / scoped / candidate / anchored / unsupported / open / retired / parked |
| `assumption_refs[]` | ASM-ids registered when this idea premises a prereg |
| `notes` | free text |

`epistemic` uses the N-G tags exactly, so an idea's status is honest by construction:
`MEASURED` only with a verdict/poc ref, `LIT-BACKED` only with a paper, `STIPULATED` is the
default for an untested idea. Compatibility is the load-bearing part for §3.

---

## 3. The permutation model, and the honest combinatorial size

A **permutation** = one selection of compatible idea-choices across the slots:
- one choice per **exclusive** slot (`alternative_to` members are mutually exclusive — e.g.
  `binding-op` ∈ {construction-B, TPR-exact, WL+CS}; the primary `seam` topology),
- on/off per **orthogonal** toggle (`orthogonal_to` ideas stack — e.g. input-canonicaliser,
  regularisers, box-lane),
- a value per **parametric** knob (phi ∈ {0,.25,.5,.75,1}; coverage psi; D; grammar level),
filtered by `requires` / `conflicts_with` and by the standing laws (N0 §1.4).

**Naive size (architecture only, honest).** Counting the seeded slots — ~5 exclusive slots
(binding 3-4, primary-seam ~11, axiom 3, grammar 4, structured-parser 3) ≈ 1.6k; vocabulary
extension toggles 2^4 = 16; ~8 orthogonal toggles 2^8 = 256; parametric phi5 x psi5 x D3 =
75 — product ≈ **5 x 10^8 architecture permutations.** Times the mandatory scale ladder
(≥2 rungs/claim, up to 7) and the mandatory nulls (each permutation is tested WITH its
kernel-as-text null + shuffled-kernel/scramble control — 2-3 arms), a truly exhaustive
sweep is **order 10^9 experiment-cells.** That is the honest statement: **exhaustive
permutation testing is not affordable now, and likely never at experiment granularity.**

**Coherent size (after filtering).** Most cells are incoherent or law-dead: a `binding-op`
choice is irrelevant to a pure-verifier seam; a memory-layer `phi` is meaningless without an
in-layer seam; any cell with a load-bearing kernel-cosine step is dead until
`idea-polarity-similarity` passes (X3 ban); any raw-foreign-coords cell is a Law-1
falsification-only cell. After `requires`/`conflicts_with` + the §1.4 laws + de-duplication,
the coherent, non-redundant, law-legal permutation space is **O(10^2-10^3)** — still far
beyond current budget, which is exactly why §4 prioritises. The permutation *generator* (a
future build delta, §6) enumerates coherent permutations mechanically from
`registry/ideas.jsonl`; nothing about the sweep is lost, it is deferred.

**Standing rule (permutation testing meets the honesty discipline):** every permutation
under test carries, as mandatory arms, its **kernel-as-text null** (Law 2) and its
**shuffled-kernel / scramble control** (E9-defl). These are not permutation choices; they
are the semantics controls that separate "the kernel content did it" from "any structure /
retry-oracle did it" — the exact discipline the f2b-REPLICATE design added after the F2
oracle-leakage finding.

---

## 4. Feasibility prioritisation (resource-aware)

Two gates, then a score. A permutation is **NOW-eligible** iff (a) every dependency is
`ready` and (b) its max `cost_tier` ≤ the current budget tier. NOW-eligible permutations are
ranked by the N-B backlog scorer, reused verbatim so there is one prioritisation function,
not two:

```
score = (D x U x L) / max(C, C_floor)      # D decisiveness, U uncertainty, L leverage, C cost tier
ties break cheapest-decisive-first
```

### 4.1 The NOW-list (feasible + decisive; becomes research-engine candidates)

| # | idea | slots | tier | why now |
|---|---|---|---|---|
| 1 | **idea-l3a-oracle** (in progress) | seam.rules-engine + kernel.axiom/world | 0-1 | cheapest-decisive; builds the kot-axiom engine owed anyway; underpins idea B |
| 2 | **idea-verifier-external / f2b-REPLICATE** (running) | seam.verifier | 1 | the programme's central efficiency claim, being re-tested clean (oracle-leakage controlled) |
| 3 | **idea-structured-data-parser — math/Lean slice** (idea A) | encoder.structured-data-parser + model.output-head | 2 | precedent exists (Lean->kernel); cheap slice of the sub-programme |
| 4 | **idea-l1a-canonicaliser** | seam.in-tokenisation + encoder.input-parse | 2 | cheapest model-facing rung; mapper ready; de-risks L3 parse |
| 5 | **idea-l2c-phi-fixedness — LITE** | seam.in-layer (phi) | 3 | de-confounds the LCM anchor for the WHOLE L1b/L2a/L2b family; machinery exists |
| 6 | **idea-polarity-similarity / structural-decode** | encoder.similarity-decode | 1 | ENABLER (CPU, cheap) that unblocks the whole similarity-based deferred family + idea B |
| 7 | **idea-concept-toolkens** | seam.adapter + model.embedding | 2 | cheap unrun A2 variant |

This reconciles with `architecture-ladder.md` §6.1 (L3a -> L1a -> ... -> L2c-lite): the
ladder ranking IS this NOW-list over the seam/model subset; N-H adds the encoder-side
enablers (polarity/structural-decode) and idea A's math slice.

### 4.2 The DEFERRED full-permutation set (unlock when less resource-constrained)

Flagged `readiness: blocked` or `cost_tier >= 3`, and the exhaustive sweep itself:
- **idea-symbolic-inference-between-layers (idea B)** — blocked on {L3a engine, reliable
  model-side decode, X3 mitigation}; naturally sequences AFTER the NOW-list items 1 and 6.
- **idea-structured-data-parser — general-code (idea A)** — needs its own benchmark build; a
  SUB-PROGRAMME (see §5).
- **idea-l1b-dense-io, idea-l2a-bottleneck, idea-l2b-memory-layer, idea-l2c-full,
  idea-l3c-engine-in-decode** — training/tier-3-4, gated post-F2 + maintainer.
- **idea-calm-hybrid-latent, idea-gradual-introduction, idea-axiom-rdm-regulariser,
  idea-moe-expert-instrument** — training-side or rider experiments.
- **alt binding-ops (TPR-exact, WL+CS, box-lane), grammar extensions (X1/X5), vocab
  extensions** — encoder/kernel research; decide when a concrete blocked case arrives.
- **the full O(10^2-10^3) coherent sweep** — enumerated mechanically by the permutation
  generator (§6); DEFERRED pending a resource unlock, then run as a batched generation.

---

## 5. Seed contents + the two new maintainer ideas

`registry/ideas.jsonl` seeds **30 ideas**: 5 MEASURED (construction-B, A2, verifier, A1,
A6), 7 LIT-BACKED (binding alternatives, toolkens, bottleneck, memory-layer, regularisers,
MoE), 18 STIPULATED (the ladder rungs, grammar/axiom/world forks, similarity enablers, the
two new ideas). Coverage across the full slot grid is complete (all 4 architectures x their
parts). The L0-L4 ladder rungs and L2c phi-sweep are seeded with `ladder_ref`; the
gradual-introduction schedule axis is seeded as `idea-gradual-introduction`.

**Idea A — deterministic structured-data -> concept parsing** (`idea-structured-data-parser`,
source maintainer): a CODE-based (not LLM) deterministic parser mapping structured
input/output (code, math/Lean, config) to kernel concepts at inference time, extending the
proven Lean->kernel math pipeline. Slots: `encoder.structured-data-parser` +
`model.output-head-decoder` + `kernel.vocabulary-basis` (code constructs). Benchmark:
code-understanding + code-writing WITH vs WITHOUT the deterministic parser in encoder/decoder.
**Flagged a SUB-PROGRAMME**: the general-code generalisation warrants its own benchmark; the
"generalises to most programming languages" claim is STIPULATED and must be registered as an
assumption before any prereg premises it. NOW = math/Lean slice; DEFERRED = general code.

**Idea B — symbolic inference between layers** (`idea-symbolic-inference-between-layers`,
source maintainer): decode hidden-state -> concepts, run symbolic inference (rules-engine)
over the concept set, re-encode -> vector -> next layer; variant = a dedicated hidden layer.
Slots: `model.inter-layer-activation` + `seam.rules-engine` + `encoder.similarity-decode`.
Its rules step IS L3a's engine placed in the forward pass, so it `requires` idea-l3a-oracle
and a reliable model-side decode (X2's 51/54 was ENCODER-side only) and X3 mitigation — it is
correctly DEFERRED until the NOW-list lands those, and it is Law-1 exposed (modifies the
forward pass).

**Advisor adds:** `idea-polarity-similarity` and `idea-structural-decode-similarity` (the
X3-mitigation enabler family — high leverage, cheap, unblocks similarity-based ideas and
idea B's decode step); `idea-box-taxonomy-lane` (constructed geometric-entailment lane for
the negation-free fragment). A literature-researcher mining prior-art for the idea-A / idea-B
threads (AST/structure-aware code models, grammar-constrained decoding, neurosymbolic
in-network layers) will produce additional entries to append.

---

## 6. Integration + build status

**Pipeline (idea -> evidence).** idea (`status:idea`) -> feasibility filter (§4) ->
NOW-list selection -> N-B **candidate** (`candidates/<id>/`, `status:scoped/candidate`) ->
`prereg-freeze` -> run -> verdict -> N-B assessment (`kot-assess/1`) writes the result BACK,
flipping the idea's `epistemic` to MEASURED and its `status` to anchored/retired. The idea's
`decisiveness/uncertainty/leverage/cost_tier` ARE the backlog scorer's D/U/L/C, so
`ideas.jsonl` is the upstream of the N-B backlog, not a competing surface.

**Assumption-register binding (N-G).** Every STIPULATED idea whose premise a prereg will rest
on gets an ASM-id in `registry/assumptions.jsonl` at candidate time (e.g. idea A's
`code-parse-generalises`; L3a's ASM-0004 relational-alias stipulation already exists). Until
then the idea is ideation and premises nothing — the N-G RULE is honoured by keeping ideas
non-load-bearing.

**Build status.** DONE: this doc + `registry/ideas.jsonl` (30 seeded, validated — all valid
JSON, unique ids, references resolve, full slot coverage). DEFERRED build deltas (follow-up
beads, not built here): (D-i) a `kot-idea/1` JSON schema + `ideas-check` lint in the
`tools/registry/` house style; (D-ii) a permutation generator that enumerates coherent
permutations from `ideas.jsonl` (filter by compatibility + §1.4 laws) and emits the DEFERRED
sweep + the NOW-list scores; (D-iii) `candidate-new` wiring so an idea promotes to an N-B
candidate with its ASM registration. D-i/D-ii are ~0.5 agent-day each, $0.

## 7. Honesty footer

Creates no experiment entry, freezes nothing, spends nothing. Every idea's status is the
N-G tag of its core claim; no idea is evidence and none premises a decision until promoted,
pre-registered, and (for STIPULATED premises) ASM-registered. The combinatorial sizes in §3
are honest order-of-magnitude counts over the seeded slots, flagged as EXTRAPOLATION-free
arithmetic (they count design options, not results). The NOW-list is a design recommendation
in the directives-§4 sense: a pre-registered experiment, not this document, decides each.

---

*Cross-references:* `registry/ideas.jsonl` (the seed); `docs/next/research-engine.md` (N-B
candidate backlog + scorer); `docs/next/assumption-register.md` (N-G epistemic gate);
`docs/next/architecture-ladder.md` (L0-L4 + L2c — the partial hand-built instance);
`docs/next/arch-survey.md` (N0 seam ledger + laws §1.4); `docs/kernel-design-directives.md`
(binding).
