# WMRE-1 — World-Model + Rules-Engine Architecture, and the RULES-1 Minimal Viable Experiment

**Status: PROVISIONAL first draft** (designer-1, 2026-07-11). This document synthesises two divergent architecture proposals (WM-1 "world-memory-layer" and KOTC "activation/decode/train compiler") against the grounding dossier (kernel inventory, sparq-inference survey, LLM-integration prior art, RULES-1 skeleton). It is an input to an independent GPT-5.6 proposal round and the GPT-5.6 review gate. **No feasibility conclusion is stated or implied anywhere in this document; verdicts belong to the maintainer and the review gate.** All epistemic tags are provisional. ASM ids in the block PROPOSED-ASM-1120..1139 are EMITTED here (Appendix A) for central registration by the coordinator; this document has no write access to `registry/assumptions.jsonl`.

Maintainer redirect: issue #15. Related open maintainer threads: issue #6 (knull fork), issue #7 (programme-3 governance).

**Amendment notice (2026-07-11):** the section *Cross-model synthesis (GPT-5.6 fold-in)* below adjudicates an independent GPT-5.6 proposal against this draft and amends specific decisions (MD-5 flipped; ASM-1130's depth bound superseded; arm A7 and control c6 added; A6 dropped from the MVE). Where that section states an old→new delta, the new value governs; the body above is retained unedited as the first-draft record.

---

## 1. Problem framing: the kernel is inert because it has no world to act on and no rules to act with

Two measured results define the problem.

- **The kernel's authored content carries value.** f2b-t measured a +0.2507 lift on external gold from the kernel's authored answer key [MEASURED: f2b-t verdict, `poc/f2b/`] — the *prose* of the kernel transfers.
- **The kernel's formal machinery does nothing.** DECONF-A1 measured C_dec = 1.0: every runtime decision the structured engine made was extensionally reproducible from a flat projection of the store's stated bytes [MEASURED: `poc/deconf-a1/audit_a1.py` certificate]. The machinery is, in the audit's mechanical sense, inert.

The root cause is visible in the engine source. `tools/axiom/kot_axiom.py` is a constraint **checker and fact-retriever**: it validates functional/cardinality/disjointWith/domain/range at load, canonicalises inverseOf, and answers a closed query grammar single-hop, fail-closed. Its own comments state *"No subsumption / no transitive closure … subClassOf REFUSED (ERR_AXIOM_UNIMPLEMENTED)"* [MEASURED: source, `tools/axiom/kot_axiom.py`]. In `poc/nsk1/nsk1_runner.py`, the two-hop grandfather gold is generator-computed; the engine resolves only hop 1 [MEASURED: source, `poc/nsk1/nsk1_runner.py`]. Nothing in the estate **materialises entailments** — nothing ever produces a fact that was not stated.

The redirect names the two missing organs precisely:

1. **A world model** — a place to hold formalised INSTANCE data (an ABox) inside the structured engine, in two regimes: a **default world** (persistent; entailments may be materialised at train/build time) and a **temporary world** (facts supplied in the prompt, valid only for that prompt; inference must run at prompt time).
2. **A formal rules engine** — OWL/RDFS/N3-like deterministic inference that turns how concepts are DEFINED (the properties of classes: person, photo, cat) into derivations. Canonical target: from `mother-of(andy) = hazza` and `parent-of(andy) = bazza`, derive `father-of(andy) = bazza`.

The hypothesis under design (not under conclusion) is that adding these two organs flips the flagship story: from "authored content lifts, machinery inert" to "authored definitions + deterministic rules derive facts nobody stated" — machinery measured load-bearing for the first time. The mechanical operationalisation of "non-inert" is the DECONF-A1 instrument run in reverse: an engine whose decisions on **entailed-but-never-stated** facts cannot be reproduced by any projection of the stated bytes (C_dec < 1.0 on entailed cells) while remaining exact on stated ones (C_dec = 1.0).

The estate already holds most of the parts [MEASURED: kernel-inventory grounding, verified this session]: a frozen kinship TBox (`data/axioms-v0/`, 6 machine-checkable records), a kinship ABox with a Presley anchor (`data/world-v0/`, 598 records / 324 entities), a formalised real-data multi-hop evaluation world (`data/nsk1-clutrr/`, 5,090 facts, 958 items with proof-state gold, third-party answer key), a redistributable synthetic twin (`data/nsk1-eval/`), much larger built-out ontology kernels (`data/onto-obo/` 96,192 records incl. a 684-relation RO shard with property chains; `data/onto-sumo/` 15,595 KIF axioms), a conformance-tested deterministic reasoner (sparq-reason: RDFS, OWL 2 RL incl. `prp-spo2` property chains and `prp-fp` functional, N3/RIF-Core Horn rules, incremental closure maintenance, `why()` proof trees; local checkout `/home/ec2-user/css/kernel/sparq`), and the certificate + GPU harnesses (`poc/deconf-a1/audit_a1.py`, `poc/f2b/runner/f2b_runner.py`, `poc/nsk1/nsk1_runner.py`). What is missing is small and enumerable: a `parent` relation, a `person` class, a covering axiom, a materialisation pass, and the experiment that connects them to a host model.

---

## 2. Recommended architecture

### 2.1 WMRE-1 in one paragraph

Kernel definitions (molecules-v0 / kernel-v0 explications) are compiled — via authored, endorsed constraint records, never automatic NL→OWL — into a **TBox** of OWL-RL-expressible axioms plus a small set of compiled Horn rules for the definitional content OWL 2 RL provably cannot derive. Formalised instance data forms a scoped **ABox** in two regimes: a persistent default world (closure materialised once at build time; runtime is lookup) and a temporary world (per-prompt facts; delta closure computed at prompt time). A **deterministic rules engine** — sparq-reason as primary, with a ~200-LOC Python forward chainer as a differential twin that must agree exactly — materialises proof-carrying entailments *outside* the frozen host model. The entailments enter the host at the **memory/retrieval slot**: as verbalised derived facts prepended to context (injection arm), and as a licensed-rejection oracle in verify-retry (the load-bearing arm). A decode-time logit-mask variant (imported from the KOTC lens) is carried as an optional arm at marginal cost; the train-time fine-tune slot and the activation-write slot are explicitly deferred.

```
KERNEL (definitions)                          WORLD (instances)
molecules-v0 / kernel-v0 explications         kot-world/1 records
axioms-v0  +  minted axioms-kinship-v1        world-v0 · nsk1-clutrr · nsk1-eval
        │                                             │
  [C1] TBox COMPILER                            [C2] ABox EMITTER
  endorsed kot-axiom/1 records → tbox.nt        kot-world/1 → abox.nt per scope
  + rules.n3 (compiled Horn for non-RL          + UNA sidecar (owl:differentFrom,
  definitional content); every rule cites       item-scoped)
  its endorsing explication sha                       │
        └───────────────────┬─────────────────────────┘
                            ▼
  [C3] RULES ENGINE (outside the model; deterministic; proof-carrying)
  sparq-reason (OwlRl + N3 fixpoint, why() proof trees) ∥ Python twin
  DEFAULT world:  materialise once at build → persisted closure → runtime lookup
  TEMPORARY world: ruleset compiled once → per-prompt delta closure (µs-scale)
                            │
                            ▼
  [C4] THE SLOT — memory/retrieval layer between store and context
  item → S (stated) + Cl(S)\S (derived, with one-line proofs)
  arm A2: verbalised derivations prepended (token-matched)
  arm A3: Cl(S) as verify-retry oracle (f2b_runner.py, k=4)   ← load-bearing
  arm A6 (optional): decode-time logit mask over the closed answer vocab
                            │
                            ▼
             FROZEN HOST MODEL (R1 SmolLM2-135M · R3 1.7B comparator)
                            │
  [C5] CERTIFICATE (CPU): audit_a1.py inverted — C_dec vs stated-bytes
  projection; non-inert iff C_dec < 1.0 on entailed cells with the engine
  correct against third-party gold at Wilson-LB ≥ 0.98
```

**C1 — how definitions become axioms.** Mechanical kind table from `kot-axiom/1`: `functional` → `owl:FunctionalProperty`; `range`/`domain` → `rdfs:range`/`rdfs:domain`; `disjointWith` → `owl:disjointWith`; `inverseOf` → `owl:inverseOf`; cardinality → `owl:maxQualifiedCardinality`. The `urn:kot:`/`urn:kotw:` URNs are already IRIs, so emission is string formatting. Two things must be **minted** as `data/axioms-kinship-v1/` (~6 records, the gap already named as successor task 3 in `docs/design-l3a-rules-engine-oracle.md` §7): the `parent` relation and `person` class; `mother ⊑ parent`, `father ⊑ parent` (new kind `subPropertyOf`); and `parent coveredBy {mother, father}` (new kind `coveredBy`). Every record cites the endorsing molecules-v0 explication sha, on the `axioms-definitional-v0` endorsement precedent — the compiler compiles *endorsed constraint records*, and the explication is the cited warrant, because NSM explications are prose and automatic NL→OWL is out of scope. DECISION D6 [STIPULATED: PROPOSED-ASM-1126].

**C1, the non-RL residue.** Covering + functional + UNA jointly license a case elimination ("bazza is not the mother, therefore the father") that OWL 2 RL is documented as provably incomplete for (assertion-only rule heads; no disjunction elimination) [MEASURED: sparq `inference-conformance-report.md`, PR1 divergences]. C1 therefore partially evaluates that case elimination into one **monotone Horn rule** in `rules.n3` (§3 below), sound *given* the covering and UNA premises — which are named, registered stipulations, not hidden lemmas. DECISION D1 [STIPULATED: PROPOSED-ASM-1120], DECISION D2 [STIPULATED: PROPOSED-ASM-1121].

**C3 — engine build path.** sparq-reason is primary: it is the deterministic OWL/RDFS/N3 stack the redirect names, it is conformance-tested, and its `why()` proof trees give per-derivation provenance. A ~200-LOC Python forward chainer implementing only this rule inventory rides along as a **differential twin**: both engines must agree on Cl(S) exactly on every item, giving an independent-implementation audit and de-risking Rust-build friction on a 2-core shared box. DECISION D4 [STIPULATED: PROPOSED-ASM-1124]. The closed rule inventory (R-SUBP, R-DOMRNG, R-INV, R-CHAIN at depth ≤ 2, R-COVER, refusal on anything else) terminates by construction; the depth bound is a frozen envelope term, not an incidental detail — closure blow-up is the known scale cliff (a published benchmark expands 237K explicit to ~150M inferred triples under RDFS-Plus [LIT-BACKED: GraphDB inference documentation]). DECISION D11 [STIPULATED: PROPOSED-ASM-1130].

**C4 — the slot, and why verify-retry is load-bearing.** Injecting the derived fact verbatim (A2) risks reducing the host's task to reading comprehension. The arm that carries the model-level claim is therefore **verify-retry** (A3): the model must *generate* its answer; the engine only licenses rejection of answers inconsistent with Cl(S), triggering a resample (k=4, direct reuse of `f2b_runner.py`). A2 is reported strictly as a *systems* claim (model + world-model together derive what the model alone cannot), never a model-reasoning claim. DECISION D9 [STIPULATED: PROPOSED-ASM-1128].

### 2.2 The two lenses, labelled comparison

| Criterion | **WM-1** (external world-memory layer) | **KOTC** (compiled decode/train/activation) |
|---|---|---|
| Where the reasoner sits | Outside the frozen model, between store and context (positions a/d-prompt) | Inside the computation: decode-time logit mask (K3); train-time closure distillation (K2); activation read-only probes |
| Decisiveness for "derive what the model misses" | Highest in the prior art: hard external solvers in the loop are what decisively produce missed inferences; near-ceiling existence proofs on CLUTRR-family kinship [LIT-BACKED: Yang/Ishay/Lee 2023 (LLM→ASP, CLUTRR); Pan et al. 2023 Logic-LM +39.2%] | Decode mask: high but at tautology risk — with \|L\| = 1 the mask *is* the symbolic answer in model skin. Train slot: makes the *data* complete, not the machinery non-inert; the reasoning stays offline [LIT-BACKED: framing split in llm-integration survey; Herron et al. 2025 caveat that materialised entailments can degrade downstream] |
| Cost to first readout | ~$0 certificate + $1–3 GPU; no training | Decode arm ≈ $1–3; train arm adds LoRA fine-tune ($2–5) and a memorisation-vs-rule confound requiring its own controls |
| Correctness story | Proof-carrying derivations, fail-closed refusal, provenance on every answer | Same engine underneath; provenance survives, but the mask hides how much the model contributed |
| Efficiency story | Reasoner-offload: µs-scale CPU engine + small model vs large model — direct noninferiority test | Train slot amortises inference to weights (attractive long-term); decode mask adds near-zero runtime cost |
| Known instrument risk at this position | Injection tautology (managed by making A3 load-bearing) | Activation-write already measured INSTRUMENT-INVALID — shuffled control out-rescued real, 0.525 vs 0.400 [MEASURED: nsk1 B′] |
| What it uniquely contributes to the synthesis | The architecture itself; the default/temporary world split; the certificate leg; the knull ablation discipline | The \|L\| decisiveness ledger (mandatory honesty instrument); the decode-mask arm as a cheap same-position variant; the weights-resident question, properly deferred as a follow-on |

**Synthesis verdict (design-level, not feasibility):** adopt WM-1 as the architecture; import from KOTC the \|L\| ledger and the optional decode-mask arm; defer KOTC's train-slot fine-tune to a named follow-on (RULES-2) and keep the activation slot read-only-if-at-all. The deciding considerations: (i) the prior-art asymmetry — external deterministic solvers in the loop are the mechanism with demonstrated decisive lifts on exactly this task family, while soft/weight-side injection is the regime that already measured inert or invalid here [LIT-BACKED: llm-integration survey, items 1–3, 8]; (ii) the train slot answers a different question (is the rule *in the weights*?) which is worth asking only after the engine's derivations are shown to matter at all; (iii) cost and reuse — WM-1 reaches a decisive readout on verified assets with ~500 LOC of new glue and no training. DECISION D3 [STIPULATED: PROPOSED-ASM-1122], DECISION D16 [STIPULATED: PROPOSED-ASM-1136], DECISION D17 [STIPULATED: PROPOSED-ASM-1135].

### 2.3 Which architectural position to test first

**Prompt-time, temporary-world, external-reasoner-at-the-memory-slot.** Reasons, in order of weight:

1. It is the maintainer's temporary-world case verbatim: facts supplied in the prompt, valid only for that prompt, inference at prompt time.
2. It is the only position where the *non-inertness* claim can attach: the default-world position is runtime-inert **by design** (closure precomputed; runtime is lookup), so its claim is a cost ledger, not a machinery claim. DECISION D20 [STIPULATED: PROPOSED-ASM-1139].
3. It is the cheapest decisive test: the certificate leg is ~$0 CPU, the smallest GPU contrast $1–3 [EXTRAPOLATION: PROPOSED-ASM-1134].
4. It has the strongest prior-art existence proofs on the exact task family [LIT-BACKED: Yang/Ishay/Lee 2023 on CLUTRR; Logic-LM].
5. Its failure modes indict nameable components (axiom set too weak → KILL-a; derivations don't help the host → KILL-b) rather than the instrument, unlike the activation-write position [MEASURED: nsk1 B′ INSTRUMENT-INVALID].

The default-world regime is still *run* in the same campaign — as the priced cost-ledger arm (A4) — so the maintainer's train-time/prompt-time distinction gets an empirical price tag without any claim inflation. DECISION D5 [STIPULATED: PROPOSED-ASM-1123 (scope), PROPOSED-ASM-1139 (claim restriction)].

---

## 3. Worked example: parent → father, end-to-end through WMRE-1

**Input (temporary world, one prompt).** Stated facts, gold-parsed to three triples plus the item-scoped UNA sidecar:

```
:andy kot:mother :hazza .
:andy kot:parent :bazza .
:hazza owl:differentFrom :bazza .     # UNA, item-scoped  [STIPULATED: PROPOSED-ASM-1120]
```

**C1 output (TBox + rules).** From `axioms-v0` (frozen L3a pair) and minted `axioms-kinship-v1`:

```
kot:mother rdfs:subPropertyOf kot:parent .        # R-SUBP,  endorsed by molecule 'mother'
kot:father rdfs:subPropertyOf kot:parent .
kot:mother a owl:FunctionalProperty .             # from rel-mother.json (kot-axiom/1)
kot:father a owl:FunctionalProperty .             # from rel-father.json
kot:mother rdfs:range kot:Woman .                 # R-DOMRNG
kot:father rdfs:range kot:Man .
kot:Man owl:disjointWith kot:Woman .              # from class-man.json
# R-COVER-ELIM — compiled from: coveredBy-parent [PROPOSED-ASM-1121]
#                + rel-mother(functional) + UNA [PROPOSED-ASM-1120]
{ ?c kot:mother ?m . ?c kot:parent ?p . ?m owl:differentFrom ?p }
  => { ?c kot:father ?p } .
```

Soundness of R-COVER-ELIM, given the two stipulated premises: covering says bazza, being a parent of andy, is andy's mother or andy's father; functionality of `mother` says andy's only mother is hazza; UNA says bazza ≠ hazza; therefore bazza is not the mother; therefore the father. The disjunction elimination that OWL 2 RL cannot perform [MEASURED: sparq conformance report, PR1] has been pre-compiled into one monotone Horn rule whose contestable premises are named ASMs, visible in every proof tree.

**C3 fixpoint (temporary world, per-prompt delta closure).**

```
step 1  prp-spo1      :andy kot:parent :hazza .          (mother ⊑ parent)
step 2  prp-rng       :hazza a kot:Woman .               (range of mother)
step 3  R-COVER-ELIM  :andy kot:father :bazza .          ← THE TARGET, never stated
step 4  prp-rng       :bazza a kot:Man .                 (range of father)
```

Every derived triple carries `derivation: {rule_id, premise_ids, axiom_refs}`; `why()` returns the proof tree down to asserted facts. Had the world also asserted `bazza a kot:Woman`, `cax-dw` would surface an inconsistency (the E5 refusal stratum); had gender/functionality premises been absent, the engine refuses with a named code rather than guessing — fail-closed is part of the design, inherited from the L3a discipline [MEASURED: `registry/verdicts/l3a.json` — PASS, covered-exact Wilson LB 0.9955, control-refusal LB 0.9911, 5.3 µs/query].

**C4, what each arm sees.**

- **A1 (model alone):** the two stated facts, plus neutral padding to match A2's token count [STIPULATED: PROPOSED-ASM-1127]. The shortcut literature predicts systematic failure at composition [LIT-BACKED: Ju et al. 2024, latent multi-hop / factual shortcuts]; the measured R1 CLUTRR baseline is the inert floor.
- **A2 (injection):** stated facts + the derivations rendered canonically: *"Derived: Bazza is Andy's father — Andy's only mother is Hazza (mother is functional, per the definition of 'mother'); Bazza is Andy's parent; Bazza ≠ Hazza; and a parent is a mother or a father (definition of 'parent'). Derived: Bazza is a man."* Scored as a systems claim only.
- **A3 (verify-retry, load-bearing):** the model answers from stated facts alone; if the answer contradicts Cl(S) (e.g. "mother", "parent"), the engine issues a licensed rejection with its proof, and the model resamples, up to k = 4.
- **C5 (certificate):** the decision grid over engine-v1 vs the GS-B stated-bytes projection shows the `father` cell is not computable from any projection of the stated facts — C_dec < 1.0 on entailed cells, C_dec = 1.0 on stated cells: mechanical non-inertness, no GPU involved.

The same machinery with R-CHAIN (`parent ∘ parent ⊑ grandparent`, gendered via range — OWL-RL `prp-spo2`) covers all 958 nsk1-clutrr two-hop items whose gold today is generator-computed because the native engine is hop-1-only — precisely the measured inertness this architecture exists to remove.

---

## 4. RULES-1: the minimal viable experiment

### 4.1 Data (from the kernel inventory)

| Role | Artifact | Why |
|---|---|---|
| TBox core | `data/axioms-v0/` (frozen L3a pair) + minted `data/axioms-kinship-v1/` (~6 records: `parent`, `person`, 2× `subPropertyOf`, `coveredBy`; each citing its endorsing explication) | Smallest native TBox; already the parent/father domain. DECISION D6 [STIPULATED: PROPOSED-ASM-1126] |
| ABox, canonical case | `data/world-v0/world.jsonl` (598 records / 324 entities, Presley anchor, 6 planted violations) | The maintainer's worked case lives here |
| ABox + items, primary eval | `data/nsk1-clutrr/` (5,090 facts; 858 covered + 100 control items; proof-state gold; per-item fresh names; third-party answer key predating the kernel; CC-BY-NC-4.0 **eval-side only**) | Real data, external gold — no gold circularity. DECISION D7 [STIPULATED: PROPOSED-ASM-1125] |
| Redistributable twin | `data/nsk1-eval/` (1,000 covered + 100 control, 140 families, RNG-seeded) | Anything that must be redistributed reports on this twin |
| Pre-registered SECOND vertical (not in the MVE) | `data/onto-obo/` RO shard (684 relations with `inverse_of`, `transitive_over`, `holds_over_chain`) + `axioms-definitional-v0` GO/MONDO/SO endorsements | The "much more built-out kernels" leg; generality probe after the family vertical reads out. DECISION D8 [STIPULATED: PROPOSED-ASM-1125 notes] |

`data/onto-sumo/` is excluded from the MVE: its 15,595 axioms are canonical KIF strings needing a KIF→rule translation step — new surface, separate bead.

### 4.2 Success entailments (entailed, never stated; held out by construction)

- **E1** gendered-parent completion via R-COVER-ELIM — the canonical hazza/bazza derivation (world-v0 families + constructed cells).
- **E2** type inference from domain/range — `mother(x,y) ⊢ woman(y) ∧ person(x)`.
- **E3** property-chain grandparent over the 958 nsk1-clutrr items (proof-state gold already present).
- **E5** refusal stratum — insufficient-premise queries (parent stated, no gender or functionality path) must draw the named refusal from the engine and abstention from the model arm. Fail-closed is scored, not decorative.
- **E4** (defined-class membership, the person/photo/cat leg) is deferred to the OBO second vertical. DECISION D8 [STIPULATED: PROPOSED-ASM-1125].

A generator emits, per item, the stated set S and closure Cl(S); eval cells are sampled from Cl(S)\S (entailed), from S (stated sanity anchors), and E5 negatives. Cl(S)\S is nonempty by construction (E1 + E3), so the kill condition below cannot fire vacuously.

### 4.3 Arms and controls

Hosts: R1 = SmolLM2-135M; R3 = SmolLM2-1.7B; greedy, fp32, seeds {0,1,2}. R3 text-only headroom on this world: 0.7912 [MEASURED: nsk1 R3 run].

| Arm | Contents | Claim it carries |
|---|---|---|
| A1 | model alone; stated facts + neutral token-matching padding | inert floor |
| A2 | model + engine-derived facts injected (canonical verbalisation + one-line proofs) | systems claim only |
| **A3** | model + engine verify-retry, k = 4 (`f2b_runner.py` reuse) | **the model-level claim** |
| A4 | default world: closure pre-materialised offline; runtime lookup-only | cost ledger only; runtime-inert by design [STIPULATED: PROPOSED-ASM-1139] |
| A5 | R3 alone | efficiency comparator |
| A6 (optional) | decode-time logit mask over the closed 23-relation vocab, with the mandatory \|L\| decisiveness ledger (distribution of licensed-answer-set sizes; \|L\| = 1 cells flagged) | same-position variant; honesty instrument imported from KOTC. DECISION D14 [STIPULATED: PROPOSED-ASM-1137] |

Controls:

- **c1 shuffled-rules** — Sattolo-deranged axiom set at identical topology and token cost; lift must collapse (recovery UB95 < 0.30, H-STRUCT discipline). DECISION D10 [STIPULATED: PROPOSED-ASM-1129].
- **c2 paraphrase/lexical** — K ≥ 2 held-out phrasings per item + fresh entity names every item (native to nsk1-clutrr) — anti-surface-matching.
- **c3 GS-B stated-bytes projection** — the certificate comparator.
- **c4 trivial policies** — abstain-all / answer-all floors (L3a discipline).
- **c5 knull-sourced-rules ablation** — rules re-derived from plain-dictionary definitions; pre-registered now, run in phase 2 (pending the knull-fork decision, issue #6). Until it runs, any positive result is labelled "machinery non-inertness", **not** "kernel-specific value". DECISION D15 [STIPULATED: PROPOSED-ASM-1138].
- **Deferred:** activation-layer writes — nsk1 B′ landed INSTRUMENT-INVALID (shuffled control out-rescued real, 0.525 vs 0.400) [MEASURED: nsk1 B′]; no respend at that position until the memory-slot position reads out. DECISION D17 [STIPULATED: PROPOSED-ASM-1135].

Scope guard: gold-parse only. The NL→ABox front-end is a named separate wall (l3a-parse retention 0.44, FAIL [MEASURED: l3a-parse verdict]); nothing in RULES-1 claims NL robustness. DECISION D5 [STIPULATED: PROPOSED-ASM-1123].

### 4.4 Metrics and pre-registered decision rules

- **Certificate primary (CPU, ~$0).** Inverted DECONF-A1 grid (reuse `poc/deconf-a1/audit_a1.py` + `build_gsa.py`): SUCCESS = C_dec = 1.0 on stated cells AND C_dec < 1.0 on entailed cells AND engine correct against third-party gold at Wilson-LB ≥ 0.98 (the L3a bar). **KILL-a:** Cl(S)\S empty or trivial — indicts the axiom set, spends no GPU. DECISION D12 [STIPULATED: PROPOSED-ASM-1131].
- **Host-lift primary (GPU).** A3 − A1 (and A2 − A1, reported as systems-level) on entailed cells; paired item BCa bootstrap, B = 10⁴, one-sided 95% LB > 0, scored against the CLUTRR third-party gold (predates the kernel — no circularity). **KILL-b:** LB ≤ 0 — the derivations do not help the host; engine value remains oracle-only (route to L3b; no model claim). DECISION D13 [STIPULATED: PROPOSED-ASM-1132].
- **Holm-corrected secondaries.** (s1) c1 shuffled recovery UB95 < 0.30; (s2) A3 > A1; (s3) **efficiency**: noninferiority of R1+engine (best of A2/A3) vs A5 (R3-alone) on the entailed slice, margin 0, sign-only language, two rungs — the reasoner-offload leg, tested exactly where the mechanism should bind (multi-hop composition; R3 headroom 0.7912 keeps the separation gate live). DECISION D18 [STIPULATED: PROPOSED-ASM-1133].
- **Descriptives.** Engine µs/query (L3a datum 5.3 µs/query [MEASURED: `registry/verdicts/l3a.json`]); default-world one-off materialisation cost vs per-prompt delta-closure cost (the priced train-time/prompt-time trade); refusal-stratum correctness; \|L\| distribution if A6 runs.
- **Instrument gates carried over.** R1 headroom ≤ 0.85; separation R3 > R1 by ≥ 0.05; engagement gate on A3 (verifier decidably engaged); byte-identical repeat; differential-twin exact agreement on Cl(S) for every item.

### 4.5 Cost band

[EXTRAPOLATION: PROPOSED-ASM-1134 — all figures scale from the one measured datum: nsk1 B′, 32,958 rows = 0.457 A10G-h ≈ $0.50.]

| Tier | Contents | Band |
|---|---|---|
| Certificate only | engine v1 + E1/E3/E5 over 958 items + GS-B projection | **~$0 (CPU)** — decides non-inertness mechanically on its own |
| Smallest decisive GPU | A1 vs A2 + c1, 958 × 3 × 3 seeds ≈ 9k generations | **$1–3** (0.5–1.5 A10G-h) |
| Full skeleton | A1–A6, k = 4 on A3, one R3 arm ≈ 25–60k generations | **$3–10** (2–6 A10G-h) |
| Worst case | + OBO second vertical + paraphrase K = 2 | **$15–25** (12–15 A10G-h) |

All tiers sit inside the standing Tier-0/F2 authorization; no new provisioning. Build effort: C1+C2 ≈ 250 LOC Python; C3 wrapper ≈ 100 LOC; twin ≈ 200 LOC; C4 ≈ 150 LOC reusing `f2b_runner.py`; C5 reuses `audit_a1.py` near-verbatim — roughly 1–2 agent-days.

### 4.6 What makes it freezable

Pins: shas on corpus (`nsk1-clutrr`, `nsk1-eval`, `world-v0`), axioms (`axioms-v0` + minted `axioms-kinship-v1`), engine (sparq commit + twin source), rule inventory, cell generator, prompts, seeds, and the decision rules above. ASMs: registration of PROPOSED-ASM-1120..1139 (Appendix A) — the load-bearing stipulations are UNA (1120), covering (1121), gold-parse scope (1123), token-matching (1127), the depth-≤2 closed inventory (1130), and the claim-restriction rows (1128, 1136, 1137, 1139). Envelope limits frozen in: gold-parse only; this rule inventory, this world, this vertical; two rungs sign-only; A4 carries no non-inertness claim; a positive result before c5 runs is "machinery non-inert", not "kernel-specific value". The maintainer's requested survey of real-world inference-engine applications (SNOMED/ELK classification, GO annotation propagation, RDFox/GraphDB enterprise materialisation — the families motivating R-SUBP/R-CHAIN/R-CLASS [LIT-BACKED: sparq-inference survey §3]) is a separate lit-review deliverable feeding the axiom inventory, not a gate on this MVE.

---

## 5. How RULES-1 advances both theses

**Correctness (deterministic grounded inference).** f2b-t showed the kernel's *authored answer key* transfers (+0.2507 on external gold [MEASURED: f2b-t]). RULES-1 tests the strictly stronger claim: that authored **definitions**, compiled to axioms and driven through a deterministic engine, **derive** answers nobody stated — proof-carrying, provenance-licensed, fail-closed, scored on third-party gold. If E1/E3 survive the certificate, the bootstrap, and the shuffled-rules control, the kernel's formal machinery is measured load-bearing for the first time — the direct structural answer to DECONF-A1's C_dec = 1.0. If they do not, the kill conditions say precisely which organ failed (axiom set, host coupling, or control), and the negative is informative rather than diffuse.

**Efficiency (reasoner-offload).** The composition step — the part small models measurably miss [LIT-BACKED: Ju et al. 2024] — is offloaded to a CPU engine in the 5-µs/query class [MEASURED: `registry/verdicts/l3a.json`]. Secondary s3 re-litigates the small-matches-big headline exactly where the mechanism should bind: noninferiority of R1(135M)+engine against R3(1.7B)-alone on the entailed slice. Independently of the host result, the A4/temporary-world contrast prices the maintainer's train-time-vs-prompt-time distinction with real numbers: one-off materialisation cost + storage against per-prompt delta closure — the reasoner-offload leg of the efficiency thesis acquires an explicit cost ledger either way.

---

## 6. Maintainer decision points

Each point lists options and a recommendation; none is decided here.

**MD-1 — Which built-out kernel/world for the MVE core?**
(a) world-v0 + axioms-v0 (+ minted axioms-kinship-v1) with nsk1-clutrr as the eval world — native, smallest, already the parent/father domain, third-party gold. (b) onto-obo RO shard (biomedical; genuine property-chain axioms at scale). (c) onto-sumo (richest logic, but KIF strings need a translation step).
**Recommendation:** (a), with (b) pre-registered as the second vertical and (c) deferred to its own bead. [STIPULATED: PROPOSED-ASM-1125, PROPOSED-ASM-1126]

**MD-2 — Which architectural position first?**
(a) Prompt-time external reasoner at the memory slot (this design). (b) Decode-time logit mask. (c) Train-time closure fine-tune. (d) Activation-layer write.
**Recommendation:** (a) first; (b) as optional arm A6 in the same campaign; (c) as the named follow-on RULES-2, run only if RULES-1's engine derivations prove valuable; (d) deferred — the position measured INSTRUMENT-INVALID (nsk1 B′). [STIPULATED: PROPOSED-ASM-1122, PROPOSED-ASM-1136, PROPOSED-ASM-1135]

**MD-3 — Default world or temporary world first?**
(a) Temporary-world first: the non-inertness claim can only attach there; default-world runs alongside as the cost-ledger arm A4. (b) Default-world first: cheaper runtime, but its runtime is inert by design, so it cannot answer the redirect's central question.
**Recommendation:** (a). [STIPULATED: PROPOSED-ASM-1139]

**MD-4 — Engine build path?**
(a) sparq-reason primary + ~200-LOC Python differential twin with an exact-agreement gate. (b) Extend `kot_axiom.py` with a native materialiser only (no sparq). (c) sparq only (no twin).
**Recommendation:** (a) — sparq is the conformance-tested OWL/RDFS/N3 stack the redirect names and supplies proof trees; the twin provides an independent-implementation audit and de-risks Rust build friction on the shared box. [STIPULATED: PROPOSED-ASM-1124]

**MD-5 — Include the decode-mask arm A6 in the MVE?**
(a) Include, with the mandatory \|L\| ledger, if marginal cost stays under ~$2. (b) Defer to RULES-2.
**Recommendation:** (a) — it is the cheapest way to bracket the same position from the other side, and the \|L\| ledger disciplines it against tautology. [STIPULATED: PROPOSED-ASM-1137]

**MD-6 — Scope/cost ceiling for RULES-1?**
(a) Certificate only (~$0). (b) Smallest decisive GPU ($1–3). (c) Full skeleton ($3–10). (d) Full + second vertical + paraphrase multiplier ($15–25).
**Recommendation:** authorize (c) with a $10 ceiling; gate (d) on the E1/E3 readout. All tiers are within the standing Tier-0/F2 authorization. [EXTRAPOLATION: PROPOSED-ASM-1134]

**MD-7 — Timing of the knull-sourced-rules ablation (kernel-specificity control)?**
(a) Inside the MVE. (b) Pre-registered now, run in phase 2 pending the knull-fork decision (issue #6), with the interim claim explicitly capped at "machinery non-inert, kernel-specific value unshown".
**Recommendation:** (b) — the fork decision is open, and the claim cap preserves honesty at zero cost. [STIPULATED: PROPOSED-ASM-1138]

**MD-8 — License posture for the eval world?**
(a) nsk1-clutrr (real data, CC-BY-NC-4.0) primary, eval-side only, with nsk1-eval (redistributable synthetic twin) reported in parallel and used for anything redistributed. (b) nsk1-eval only.
**Recommendation:** (a) — real-data external gold is the stronger correctness evidence; the twin covers redistribution. [STIPULATED: PROPOSED-ASM-1125]

---

## Cross-model synthesis (GPT-5.6 fold-in)

**Input:** `poc/gpt56-review/wmre-propose/last-message.json` — GPT-5.6's independent proposal ("Scoped Proof Memory"), produced without access to this document's decision rationale beyond the draft itself, with an explicit agree/differ section. The file is substantive (full architecture + two-stage experiment); nothing was refused. **Status of this section: PROVISIONAL, designer-1, 2026-07-11. No feasibility conclusion is stated or implied; verdicts belong to the maintainer and the review gate.** New assumptions are emitted as PROPOSED-ASM-1160..1164 (JSON below) for central registration; this document still writes nothing to `registry/assumptions.jsonl`.

### 1. Convergences

Two models, prompted independently, converged on the following. Independent convergence raises **design-level confidence** in these choices (two search processes landing on the same point); it is *not* evidence that the architecture will measure positive — that remains the experiment's job.

| # | Converged choice | WMRE-1 anchor |
|---|---|---|
| CV-1 | External, deterministic, **proof-carrying reasoner outside the frozen model**; the LM parses, retrieves, renders — it does not imitate inference | §2.1, PROPOSED-ASM-1122 |
| CV-2 | **Authored + endorsed** definition→axiom compilation; NL definitions are evidence/warrant, never automatically authoritative OWL | D6, PROPOSED-ASM-1126 |
| CV-3 | **Default world materialised at build time / temporary world delta-closed at prompt time**, with strict scope separation and no silent cross-scope writes | §2.3, PROPOSED-ASM-1139 |
| CV-4 | **Fail-closed** discipline: insufficient premises → `unknown`/named refusal (never `father` by guess); contradictions → named conflict | E5, L3a precedent |
| CV-5 | **Memory/retrieval boundary as the first LM integration position**; activation writes and weight distillation deferred | MD-2(a), PROPOSED-ASM-1135/1136 |
| CV-6 | **Gold-parse-only** first experiment; the NL→ABox wall is a separate named problem | D5, PROPOSED-ASM-1123 |
| CV-7 | Evaluation on **entailed-but-never-stated** targets, with rule-ablation/shuffle controls | §4.2, PROPOSED-ASM-1129/1131 |
| CV-8 | The parent→father case elimination is **not plain OWL-RL entailment** (functionality yields `owl:sameAs`, not role assignment); it must be an explicit rule whose covering/uniqueness/inequality/completeness premises are named and visible in every proof | §2.1 "non-RL residue", PROPOSED-ASM-1120/1121; GPT-5.6 §2C derives the same PR1 point independently |
| CV-9 | The **decode-mask tautology risk** — with \|L\| = 1 the mask is the engine's answer in model skin — flagged by both models (resolutions differ; see DV-5) | D14, PROPOSED-ASM-1137 |
| CV-10 | The existing **958-item CLUTRR slice with third-party gold** is the right property-chain evidence base ("use it instead of generating a larger set") | MD-1(a), PROPOSED-ASM-1125 |

CV-8 deserves emphasis: the single most error-prone technical judgment in this design (what OWL 2 RL can and cannot license) was reproduced independently, including the specific failure mode (assertion-only heads, no disjunction elimination) and the same remedy (a monotone rule with stipulated premises). That materially de-risks the C1 compiler design.

### 2. Divergences and adjudications

**DV-1 — Three semantic strata vs one blended rule layer.** GPT-5.6 separates (A) open-world OWL-RL entailment, (B) safe Horn/Datalog definitional rules, and (C) complete-domain *policy* rules (the parent→father family), and exposes the regime in the API and every proof, "so local closure assumptions never acquire the authority of ontology semantics." WMRE-1 compiled all of these into one `rules.n3` layer with ASM-tagged premises.
**Adjudication: ADOPT.** This is a strict honesty improvement at near-zero cost: WMRE-1 already named the premises (ASM-1120/1121); tagging every compiled rule and every proof node with `regime ∈ {owl-rl, horn-def, policy}` makes the epistemically weakest stratum machine-visible instead of comment-visible, and gives the certificate and the readout a free stratification axis. GPT-5.6's per-case completeness marker (`CompleteBinaryParentRoles(z)`) is **not** adopted as a replacement for the endorsed TBox covering axiom — a global endorsed axiom with item-scoped UNA is more auditable than per-item completeness assertions — but the *policy* regime tag records exactly what GPT-5.6 wanted recorded. Two riders adopted with it: (i) SHACL-like validation constraints are emitted as a **separate artifact** that detects bad data and never becomes an entailment rule (formalising what `kot_axiom.py` already does at load); (ii) the compiler distinguishes **classification from entity generation** — existential heads refuse (no skolem/bnode minting) rather than inventing named individuals. → PROPOSED-ASM-1162.

**DV-2 — Which arm is load-bearing: direct executor vs verify-retry.** GPT-5.6 argues the primary arm should be **direct symbolic execution** (engine answers, LM renders): "if the formal subsystem can answer the query, hiding that answer behind repeated LM sampling adds cost and creates a misleading 'model reasoning' claim." WMRE-1 made verify-retry (A3) load-bearing precisely to earn a *model-level* claim (D9, ASM-1128).
**Adjudication: HYBRID — both, with a sharpened claim split.** GPT-5.6 is right that the *systems* claim ("the combined system derives what nobody stated") is carried most honestly by direct execution, not by injection (A2), and its proposed inert-kernel baseline — facts + serialized axioms as **text, no execution** — is exactly the estate's mandatory kernel-as-text null, which WMRE-1's control set was missing. But GPT-5.6 is answering a narrower question: a direct-executor-only design is close to the already-measured L3a oracle (PASS, Wilson-LB 0.9955) with an LM renderer attached; the redirect's open question includes whether the derivations help a *host*. So: **add arm A7** (direct executor: engine answers with proof, LM renders only) as the attribution-clean systems arm, **add control c6** (axioms-as-text: stated facts + serialized TBox/rules prose, no engine — the execution-vs-text contrast), **demote A2** (injection) from "systems claim carrier" to descriptive comparison arm, and **keep A3** (verify-retry) as the sole carrier of the model-level claim and of the GPU primary (KILL-b unchanged). One-primary discipline is preserved: the new execution-vs-text contrast `exact(A7) > exact(c6)` enters as Holm-corrected secondary **s4**, not as a second primary. → PROPOSED-ASM-1161 (refines 1128), PROPOSED-ASM-1164.

**DV-3 — Hybrid materialisation / query-directed evaluation.** GPT-5.6: full closure is right for a stable default world and tiny prompt overlays but is "not a universal rule"; use relevant-subgraph retrieval and query rewriting (Stardog-style lazy reasoning) to prevent closure explosion.
**Adjudication: ADOPT at the architecture level; no MVE change.** WMRE-1 already named closure blow-up as the scale cliff (D11) but offered only a semantic bound as the mitigation. The north-star architecture gains two named components: a **symbolic retrieval adapter** (entity-linked slice `relevant(D+) ∪ T`, returning a compact proof bundle rather than a closure dump) and **query-directed evaluation** as the escape hatch when materialisation is too large. RULES-1 is unaffected — its worlds are item-scoped and tiny, and full delta closure at the measured 5-µs class is the simpler pinned behaviour. GPT-5.6's four-graph nomenclature (`K / D / D+ / T,DT+ per request`) and its explicit rule "no temporary assertion or entailment writes back into D without a separate promotion workflow" are adopted as the canonical statement of the scoped world store (WMRE-1 implied both; now they are stated).

**DV-4 — Differential twin in the first experiment.** GPT-5.6 would drop the ~200-LOC Python twin from the MVE: use the conformance-tested engine plus hand-checkable proof fixtures and independent gold; differential execution becomes mandatory only before production or rule-language expansion.
**Adjudication: KEEP WMRE-1 (MD-4(a) stands).** GPT-5.6's argument is sound *as semantics* but blind to an operational fact it could not see: sparq-reason is a Rust build on a 2-shared-core box, and the twin is simultaneously (i) an independent-implementation instrument gate in the run-vs-audit tradition, (ii) the fallback engine if the Rust build fights the box, and (iii) ~1 day of work covering a 5-rule closed inventory. The exact-agreement halt (ASM-1124) stays. GPT-5.6's proof-fixture idea is adopted *additively*: a small set of hand-checked golden proofs rides along as fixtures regardless. No ASM change.

**DV-5 — Decode-mask arm A6 in the MVE.** GPT-5.6: skip it — on a closed 23-relation kinship vocabulary it "risks becoming the engine's answer disguised as model output; a direct executor provides the same correctness with clearer attribution."
**Adjudication: ADOPT GPT-5.6.** Both models independently flagged the tautology (CV-9); WMRE-1's mitigation was a ledger, GPT-5.6's is removal, and once A7 exists the ledger's honest endpoint is already occupied: on this vocabulary \|L\| will frequently be 1, at which point A6 *is* A7 with worse attribution. **MD-5 recommendation flips (a)→(b):** A6 is dropped from RULES-1 and deferred to RULES-2, where an open answer surface could make masking non-tautological. PROPOSED-ASM-1137 should be registered with its notes amended to "deferred to RULES-2 per cross-model synthesis; \|L\| ledger remains mandatory if it ever runs." The general slot-table guidance survives: decode constraints only for typed JSON / entity IDs / genuinely finite sets, always reporting \|L\| = 1 cells.

**DV-6 — The depth-≤2 bound.** GPT-5.6: "ontology semantics should not change merely because a proof needs three rule applications" — termination should come from a safe, function-free rule fragment plus explicit resource budgets, with evaluation stratified by proof depth.
**Adjudication: HYBRID, mostly ADOPT.** GPT-5.6 is correct in principle: the RULES-1 inventory is function-free safe Datalog, so the fixpoint terminates without any depth cap, and WMRE-1's D11 conflated a *semantic* restriction with a *resource* control. Replaced as follows — termination is guaranteed by the safe fragment; blow-up is controlled by explicit per-item budgets (max derived triples, wall-clock), failing closed with `ERR_BUDGET_EXCEEDED`; proof depth becomes an **evaluation stratification axis** (and the envelope statement becomes "evaluated cells cover proof depth ≤ 4", which is what E1/E3 actually need), not an engine semantics term. The closed rule *inventory* (refuse unknown rule kinds) is retained — that part of D11 was fail-closed discipline, not the offending bound. → PROPOSED-ASM-1160 (supersedes PROPOSED-ASM-1130 on registration).

**DV-7 — Certificate design: counterfactual gates and classification cells.** GPT-5.6's Stage-1 certificate adds per-target checks WMRE-1 lacked — "removing the relevant compiled definition makes the target disappear" and "a meaning-preserving rule mutation changes exactly the predicted outputs" — and includes 32 person/photo/cat defined-class cells (`CatPhoto ≡ Photo ⊓ ∃depicts.Cat`) in the CPU stage, where WMRE-1 deferred all of E4 to the OBO vertical. It also proposes much smaller sealed sets (32/64/128) than WMRE-1's 958-item slice.
**Adjudication: HYBRID.** Adopt the two **per-target counterfactual gates** into the C5 certificate — they upgrade the certificate from "the engine derives X" to "the engine derives X *because of that endorsed definition*", which is provenance made mechanical, at CPU-only cost (→ PROPOSED-ASM-1163, extends 1131). Adopt **E4-lite** as an *optional, CPU-only* certificate extension: a handful of defined-class cells (person/photo/cat) directly instantiating the maintainer's own example, gated on the marginal minting effort (~4 extra endorsed records) and carrying no GPU eval and no kill rule — full E4 stays with the OBO vertical (D8 unchanged). Reject the small-N sealed sets for the GPU stage: 958 items with third-party gold dominate 128 hand-built items on power and on gold independence, and GPT-5.6 itself concedes this ("if the existing 958-item CLUTRR slice is already runnable, use it instead").

### 3. Resulting changes (old → new)

**Recommended architecture (§2):**
- C3 termination: ~~closed inventory with chain depth ≤ 2 as an envelope term~~ → closed inventory (refusal on unknown kinds retained) + safe function-free fragment for termination + explicit per-item resource budgets (`ERR_BUDGET_EXCEEDED`); proof depth is an eval stratification axis only [DV-6].
- C3 scale path: full-materialisation-only → materialisation for default world + **query-directed evaluation** escape hatch; new **symbolic retrieval adapter** (relevant-subgraph slice, compact proof bundles) [DV-3].
- C4 arms at the slot: A2/A3/A6 → **A2 (descriptive) / A3 (model-level, load-bearing) / A7 (direct executor, systems arm)**; A6 removed from the MVE [DV-2, DV-5].
- Proof/provenance schema: `derivation:{rule_id, premise_ids, axiom_refs}` → adds `regime ∈ {owl-rl, horn-def, policy}`; constraints emitted as a separate validation artifact; existential heads refuse (no entity generation) [DV-1].
- Scoped store: two regimes, implicitly separated → four named graphs `K / D / D+ / T,DT+ per request`; asserted and inferred never indistinguishable; no write-back from T to D without a promotion workflow [DV-3].

**RULES-1 MVE (§4):**
- Arms table: + **A7** — direct executor: engine answers from Cl(S) with proof, LM renders only; carries the systems claim. A2's row changes from "systems claim only" → "descriptive comparison (injection vs execution)". A6 row: ~~optional~~ → removed (deferred to RULES-2).
- Controls: + **c6 axioms-as-text** — stated facts + serialized TBox/rules as prose, no engine execution; the kernel-as-text null at the axiom layer [DV-2].
- Certificate (C5): + per-target definition-removal counterfactual and meaning-preserving-mutation gates; + optional E4-lite defined-class cells (CPU-only, no kill rule) [DV-7].
- Metrics: primaries **unchanged** (certificate primary per ASM-1131 + counterfactual gates; host-lift primary A3−A1 with KILL-b per ASM-1132). Secondaries: + **s4** `exact(A7) > exact(c6)` (execution-vs-text), Holm-corrected with s1–s3. \|L\| descriptive drops with A6.
- Cost: A6 removal ≈ offsets A7 + c6 addition (engine output already computed; render/text passes are small); bands in §4.5 unchanged [EXTRAPOLATION: PROPOSED-ASM-1134 still governs].

**The 8 maintainer decision points:**
- MD-1, MD-2, MD-3, MD-6, MD-7, MD-8 — recommendations **unchanged** (MD-1 gains a note: optional E4-lite CPU cells may pull a sliver of the person/photo/cat leg forward without touching the vertical sequencing; MD-2's position table gains "direct tool/executor — co-primary at the same boundary", per GPT-5.6's slot table).
- MD-4 — recommendation **unchanged (a)**, now explicitly *against* a considered GPT-5.6 alternative (drop the twin); the disagreement and rationale are recorded in DV-4 for the maintainer to overrule.
- MD-5 — recommendation **CHANGED (a) → (b)**: drop A6 from the MVE; defer to RULES-2 [DV-5].

### 4. New maintainer decision point surfaced

**MD-9 — Claim assignment across the three integration arms (surfaced by DV-2).**
(a) A7 (direct executor) carries the systems claim via secondary s4 (A7 vs c6); A3 (verify-retry) carries the model-level claim and remains the GPU primary; A2 is descriptive. (b) GPT-5.6's original position: A7 is the *primary* arm outright and the model-level question is postponed to a separate experiment. (c) WMRE-1's original position: no A7; A2 carries the systems claim; A3 primary.
**Recommendation:** (a) — it keeps one primary endpoint, adds the attribution-clean systems contrast and the missing axioms-as-text null at negligible cost, and reserves (b) as the fallback framing if the maintainer wants the cheapest possible flagship story. [STIPULATED: PROPOSED-ASM-1161, PROPOSED-ASM-1164]

### 5. New proposed ASM rows (PROPOSED-ASM-1160..1164)

Emitted for central registration by the coordinator; this document does not write to `registry/assumptions.jsonl`. PROPOSED-ASM-1160 supersedes PROPOSED-ASM-1130 on registration; PROPOSED-ASM-1161 refines PROPOSED-ASM-1128; PROPOSED-ASM-1163 extends PROPOSED-ASM-1131; PROPOSED-ASM-1137 should be registered with the notes amendment stated in DV-5.

```json
[
  {"id":"PROPOSED-ASM-1160","tag":"STIPULATED","claim":"Engine termination comes from the safe, function-free (Datalog-safe) rule fragment plus explicit per-item resource budgets (max derived triples, wall-clock) failing closed with ERR_BUDGET_EXCEEDED; proof depth is an evaluation stratification axis only, never an engine semantics term. The closed rule inventory with refusal on unknown kinds is retained. Supersedes PROPOSED-ASM-1130's chain-depth-<=2 semantic bound.","backing_ref":"poc/gpt56-review/wmre-propose/last-message.json#6.6; docs/next/arch/world-model-rules-engine.md#cross-model-synthesis DV-6","rationale":"GPT-5.6 correctly identified that WMRE-1 conflated a semantic restriction with a resource control; ontology semantics should not change because a proof needs three rule applications. Blow-up control moves to budgets; evaluated cells still cover proof depth <= 4.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Cross-model fold-in, adjudication HYBRID (mostly adopt GPT-5.6)."},
  {"id":"PROPOSED-ASM-1161","tag":"STIPULATED","claim":"Arm A7 (direct executor: engine answers from Cl(S) with proof, LM renders only) is added to RULES-1 and carries the systems claim via Holm-corrected secondary s4 (exact(A7) > exact(c6)); A3 (verify-retry) remains sole carrier of the model-level claim and of the GPU primary (KILL-b unchanged); A2 (injection) is demoted to a descriptive comparison arm. Refines PROPOSED-ASM-1128.","backing_ref":"poc/gpt56-review/wmre-propose/last-message.json#4,#6.2; docs/next/arch/world-model-rules-engine.md#cross-model-synthesis DV-2, MD-9","rationale":"Direct execution is the attribution-clean carrier of the systems claim (GPT-5.6); verify-retry is retained because the redirect's open question includes whether derivations help a host, which a renderer-only design cannot answer. One-primary discipline preserved.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-9 recommendation (a)."},
  {"id":"PROPOSED-ASM-1162","tag":"STIPULATED","claim":"Every compiled rule and every proof node carries a semantic-regime tag, regime in {owl-rl, horn-def, policy}; complete-domain policy rules (R-COVER-ELIM family) are never reported as ontology entailment; SHACL-like constraints are emitted as a separate validation artifact that never becomes an entailment rule; existential definition heads refuse rather than mint individuals (classification vs entity generation).","backing_ref":"poc/gpt56-review/wmre-propose/last-message.json#2,#6.1; W3C OWL 2 Profiles (owl2-profiles)","rationale":"Prevents local closure assumptions (covering, UNA, completeness) from acquiring the authority of standards semantics; makes the epistemically weakest stratum machine-visible and gives certificate and readout a free stratification axis.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Adopted from GPT-5.6 DV-1. The endorsed TBox covering axiom + item-scoped UNA is retained over per-case completeness markers."},
  {"id":"PROPOSED-ASM-1163","tag":"STIPULATED","claim":"The C5 certificate adds two per-target counterfactual gates: (i) removing the endorsing compiled definition makes the entailed target disappear from Cl(S); (ii) a meaning-preserving rule mutation changes exactly the predicted outputs. Optional E4-lite defined-class cells (person/photo/cat, CPU-only, no kill rule) may ride along gated on minting effort. Extends PROPOSED-ASM-1131; SUCCESS/KILL-a rules unchanged.","backing_ref":"poc/gpt56-review/wmre-propose/last-message.json#7 stage 1; docs/next/arch/world-model-rules-engine.md#cross-model-synthesis DV-7","rationale":"Upgrades the certificate from 'the engine derives X' to 'the engine derives X because of that endorsed definition' — provenance made mechanical at CPU-only cost.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"GPT-5.6's small-N sealed GPU sets were rejected in favour of the 958-item third-party-gold slice (GPT-5.6 concurs when the slice is runnable)."},
  {"id":"PROPOSED-ASM-1164","tag":"STIPULATED","claim":"Control c6 (axioms-as-text) is added to RULES-1: stated facts plus the serialized TBox/rules as prose in context, no engine execution — the kernel-as-text null at the axiom layer, token-matched per PROPOSED-ASM-1127 conventions. It is the comparator for secondary s4.","backing_ref":"poc/gpt56-review/wmre-propose/last-message.json#7 stage 2 (arm A1); estate kernel-as-text control discipline","rationale":"Distinguishes 'execution of definitions matters' from 'definition text in context matters'; WMRE-1's control set lacked this mandatory null and GPT-5.6's independent design supplied it.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Adopted from GPT-5.6 DV-2/DV-8."}
]
```

**Self-check gate:** no feasibility conclusion stated or implied anywhere above; all tags provisional; convergence framed as design-confidence only; primaries and kill rules unchanged except where an old→new delta is explicitly stated; no @handle/account strings; new assumptions confined to the disjoint block 1160..1164; registry untouched.

---

## Expressivity boundary and the Lean seam (maintainer #19; future work, OUT of RULES-1 scope)

Recorded per the maintainer's approval note on issue #19: **the current rules
engine may lack expressivity for some cases — mathematics is the named
example.** The RULES-1 inventory (subPropertyOf, domain/range typing,
length-2 property chains, the R-COVER-ELIM Horn policy rule) is a closed,
safe, function-free fragment chosen for the kinship vertical; it cannot
express arithmetic, induction, quantifier alternation, or anything in the
neighbourhood of real mathematical inference, and it REFUSES (fail-closed,
`ERR_RULE_UNIMPLEMENTED`) rather than approximating. This is a documented
boundary, not an oversight.

The future-work seam is already sketched in the estate: **Lean libraries were
once brought into core** (`data/math-lean-sample/`, `data/mathlib-1000-sample/`,
and the profile-M math corpora `data/math-v0/` + `data/math-mm/` minted under
`kot-pm-*` profiles), and complex mathematical inference remains a long-term
goal **via the axiom/world-layer Lean seam** — i.e. a later stratum where
endorsed formal content compiles to a proof-assistant backend rather than to
this Horn/OWL-RL fragment, entering at the same authored/endorsed C1 boundary
(never auto-extraction) and returning the same proof-carrying, regime-tagged
derivations (a fourth regime tag would name it). This is **a much-later
consideration, explicitly out of RULES-1 scope**: nothing in RULES-1's
worlds, arms, endpoints, or kill rules touches it, and no claim made under
RULES-1 extends past the registered rule inventory. Registered as
PROPOSED-ASM-1196 (emitted in `poc/rules-1/RESULT.md`).

---

## Appendix A — Proposed ASM rows (PROPOSED-ASM-1120..1139)

Emitted for central registration; this document does not write to `registry/assumptions.jsonl`.

```json
[
  {"id":"PROPOSED-ASM-1120","tag":"STIPULATED","claim":"Unique-name assumption (UNA) holds within each item scope: distinct entity names in one item's fact set denote distinct individuals; emitted as pairwise owl:differentFrom within the item's family (bounded, <=5 entities).","backing_ref":"docs/next/arch/world-model-rules-engine.md#3","rationale":"Required premise for R-COVER-ELIM case elimination; contestable world-modelling, so named and sidecar-endorsed rather than hidden in the rule.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Visible in every why() proof tree that uses it."},
  {"id":"PROPOSED-ASM-1121","tag":"STIPULATED","claim":"Covering axiom: parent is covered by {mother, father} (every parent is a mother or a father) — minted as kind coveredBy in data/axioms-kinship-v1, endorsed by the molecules-v0 parent-family explications.","backing_ref":"docs/design-l3a-rules-engine-oracle.md#7","rationale":"Load-bearing premise for the canonical parent->father derivation; a modelling choice about the kinship domain, not a measurement.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"OWL 2 RL cannot use it directly (assertion-only heads); compiled into the monotone Horn rule R-COVER-ELIM."},
  {"id":"PROPOSED-ASM-1122","tag":"STIPULATED","claim":"The first architectural position tested is the prompt-time, temporary-world, external-reasoner memory slot (derivations enter as context injection and as a verify-retry oracle).","backing_ref":"Yang/Ishay/Lee 2023 arXiv:2307.07696 (CLUTRR via LLM->ASP); Pan et al. 2023 arXiv:2305.12295 (Logic-LM)","rationale":"Cheapest decisive position; strongest prior-art existence proofs on the exact task family; the only position where the non-inertness claim can attach at runtime.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Design choice informed by literature; the literature claims themselves are LIT-BACKED in-doc."},
  {"id":"PROPOSED-ASM-1123","tag":"STIPULATED","claim":"RULES-1 is gold-parse only: facts arrive as structured kot-world/1 records or pre-parsed triples; the NL->ABox front-end is out of scope and no NL-robustness claim attaches.","backing_ref":"l3a-parse verdict (retention 0.44, FAIL)","rationale":"Isolates the derivation question from the measured parse wall; keeps the failure modes attributable.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Scope limit frozen into the envelope."},
  {"id":"PROPOSED-ASM-1124","tag":"STIPULATED","claim":"Engine build path: sparq-reason (OwlRl + N3, why() proof trees) is the primary reasoner; a ~200-LOC Python forward chainer implementing only the RULES-1 inventory is a differential twin; both must agree exactly on Cl(S) for every item or the run halts.","backing_ref":"reports/sparq-estate.md; sparq crates/sparq-reason","rationale":"Conformance-tested engine + independent-implementation audit; de-risks Rust build friction on the 2-core shared box.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-4."},
  {"id":"PROPOSED-ASM-1125","tag":"STIPULATED","claim":"Primary eval world is data/nsk1-clutrr (real CLUTRR, third-party gold predating the kernel, CC-BY-NC-4.0 eval-side only); data/nsk1-eval is the redistributable twin; the onto-obo RO shard is the pre-registered second vertical, not in the MVE.","backing_ref":"data/nsk1-clutrr/manifest.json; data/nsk1-eval/; data/onto-obo/","rationale":"Real-data external gold removes gold circularity; twin covers redistribution; second vertical is a generality probe gated on the first readout.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-1, MD-8. onto-sumo excluded: KIF strings need a translation step (separate bead)."},
  {"id":"PROPOSED-ASM-1126","tag":"STIPULATED","claim":"A new module data/axioms-kinship-v1 (~6 kot-axiom/1 records) is minted: parent relation, person class, mother subPropertyOf parent, father subPropertyOf parent, parent coveredBy {mother,father}; each record cites the endorsing molecules-v0 explication sha (axioms-definitional-v0 endorsement precedent).","backing_ref":"docs/design-l3a-rules-engine-oracle.md#7 successor task 3","rationale":"Fills the named gaps (no parent, no person) required by the canonical target; endorsement keeps the definitions->axioms mapping authored and auditable, never automatic NL->OWL.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"New kinds subPropertyOf and coveredBy extend kot-axiom/1; unknown kinds elsewhere still refuse (fail-closed)."},
  {"id":"PROPOSED-ASM-1127","tag":"STIPULATED","claim":"Token-budget matching: arm A1 prompts are padded with neutral text to the token count of arm A2, so injection lift is not attributable to prompt length.","backing_ref":"docs/next/arch/world-model-rules-engine.md#4.3","rationale":"Standard confound control; padding text pinned by sha.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":""},
  {"id":"PROPOSED-ASM-1128","tag":"STIPULATED","claim":"Claim assignment across arms: A3 (verify-retry) carries the model-level claim; A2 (injection) is reported strictly as a systems claim (model+world-model derives what the model alone cannot), never as model reasoning.","backing_ref":"docs/next/arch/world-model-rules-engine.md#2.1","rationale":"Injection of the derived fact verbatim reduces the host task to reading comprehension; verify-retry forces the model to generate while the engine only licenses rejection.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Adopted from the WM-1 risk analysis."},
  {"id":"PROPOSED-ASM-1129","tag":"STIPULATED","claim":"Structural control: a Sattolo-deranged axiom set at identical topology and token cost (shuffled-rules) must collapse the lift, with recovery UB95 < 0.30, per the H-STRUCT discipline.","backing_ref":"H-STRUCT discipline (prior kernel-of-truth controls); nsk1 B' precedent","rationale":"Distinguishes content-driven lift from structure/bulk artefacts; the threshold is a design choice.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":""},
  {"id":"PROPOSED-ASM-1130","tag":"STIPULATED","claim":"The RULES-1 rule inventory is closed and terminating by construction: R-SUBP, R-DOMRNG, R-INV, R-CHAIN (chain depth <= 2, no recursion), R-COVER-ELIM; anything else refuses with ERR_RULE_UNIMPLEMENTED.","backing_ref":"tools/axiom/kot_axiom.py subClassOf-refusal precedent","rationale":"Bounds closure size (the known scale cliff) and keeps the engine fail-closed; the depth bound is an envelope term, not incidental.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Closure blow-up datum (237K->~150M triples) is LIT-BACKED in-doc (GraphDB documentation)."},
  {"id":"PROPOSED-ASM-1131","tag":"STIPULATED","claim":"Non-inertness is operationalised as the inverted DECONF-A1 certificate: SUCCESS = C_dec = 1.0 on stated cells AND C_dec < 1.0 on entailed cells AND engine correct vs third-party gold at Wilson-LB >= 0.98; KILL-a fires if Cl(S)\\S is empty or trivial.","backing_ref":"poc/deconf-a1/audit_a1.py; registry/verdicts/l3a.json (the 0.98 bar)","rationale":"Reuses the same instrument that measured inertness, so the flip is measured on the maintainer's own definition; CPU-only, ~$0.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":""},
  {"id":"PROPOSED-ASM-1132","tag":"STIPULATED","claim":"Host-lift primary decision rule: A3-A1 (and A2-A1, systems-level) on entailed cells, paired item BCa bootstrap B=10^4, one-sided 95% LB > 0 against the CLUTRR third-party gold; KILL-b fires on LB <= 0 (engine value remains oracle-only; route to L3b).","backing_ref":"f2b/nsk1 statistical discipline (paired BCa, pre-registered kills)","rationale":"Pre-registered, sign-safe, external-gold-scored; the specific rule is a design choice.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":""},
  {"id":"PROPOSED-ASM-1133","tag":"STIPULATED","claim":"Efficiency secondary: noninferiority of R1(135M)+engine (best of A2/A3) vs R3(1.7B)-alone on the entailed slice, margin 0, sign-only language, two rungs, Holm-corrected with the other secondaries.","backing_ref":"nsk1 R3 headroom 0.7912 (separation gate live)","rationale":"Re-tests the small-matches-big thesis exactly where the offloaded mechanism should bind (multi-hop composition).","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":""},
  {"id":"PROPOSED-ASM-1134","tag":"EXTRAPOLATION","claim":"GPU cost bands for RULES-1: certificate ~$0 (CPU); smallest decisive contrast $1-3 (0.5-1.5 A10G-h); full skeleton $3-10 (2-6 A10G-h); worst case with second vertical + paraphrase K=2 $15-25 (12-15 A10G-h).","backing_ref":"nsk1 B' measured datum: 32,958 rows = 0.457 A10G-h ~= $0.50 (Modal)","rationale":"Linear scaling from the one measured throughput datum on the same harness and instance class; bands widened to absorb k=4 retry variance.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"All tiers inside the standing Tier-0/F2 authorization."},
  {"id":"PROPOSED-ASM-1135","tag":"STIPULATED","claim":"The activation-write position is deferred: no spend there until the memory-slot position reads out.","backing_ref":"nsk1 B' verdict: INSTRUMENT-INVALID (shuffled control out-rescued real, 0.525 vs 0.400)","rationale":"The one measured attempt at that position invalidated its own instrument; repeating before a working comparison point exists would be uninformative spend.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-2 option (d)."},
  {"id":"PROPOSED-ASM-1136","tag":"STIPULATED","claim":"The train-time slot (fine-tuning on materialised default-world closure, KOTC arm C) is deferred to a named follow-on (RULES-2), gated on RULES-1 showing the engine's derivations matter at the memory slot.","backing_ref":"Herron et al. 2025 (materialised entailments can degrade downstream); llm-integration survey d-train assessment","rationale":"The train slot answers a different question (are the rules in the weights?) and carries a memorisation-vs-rule confound needing its own controls; sequencing it second avoids paying for it before the engine's value is established.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-2 option (c)."},
  {"id":"PROPOSED-ASM-1137","tag":"STIPULATED","claim":"The decode-time logit-mask arm (A6) is optional in RULES-1, admitted only with the mandatory |L| decisiveness ledger (per-item licensed-answer-set size distribution; |L|=1 cells flagged) and a marginal-cost cap of ~$2.","backing_ref":"KOTC proposal, risk 1 (engine-in-a-trenchcoat) + c2 ledger","rationale":"Brackets the same position from the constrained-decoding side while the ledger guards against reporting the mask's answer as the model's.","load_bearing":false,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-5."},
  {"id":"PROPOSED-ASM-1138","tag":"STIPULATED","claim":"The knull-sourced-rules ablation (rules re-derived from plain-dictionary definitions) is pre-registered now and run in phase 2, pending the knull-fork maintainer decision (issue #6); until it runs, any positive RULES-1 result is capped at 'machinery non-inert', never 'kernel-specific value'.","backing_ref":"WM-1 risk 1; issue #6","rationale":"The rules could in principle be authored without the NSM kernel; the ablation is the only test of kernel-specificity, and the claim cap preserves honesty while it is pending.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-7."},
  {"id":"PROPOSED-ASM-1139","tag":"STIPULATED","claim":"The default-world arm (A4: closure pre-materialised offline, runtime lookup-only) is runtime-inert by design; no non-inertness claim attaches to it — its deliverable is the priced train-time-vs-prompt-time cost ledger.","backing_ref":"docs/next/arch/world-model-rules-engine.md#2.3","rationale":"Prevents claim inflation on the position whose runtime, by construction, cannot exhibit the property under test, while still answering the maintainer's default/temporary pricing question.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"MD-3."}
]
```

---

## Appendix B — Key paths

`/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py` · `/home/ec2-user/css/kernel/kernel-of-truth/data/axioms-v0/` · `/home/ec2-user/css/kernel/kernel-of-truth/data/world-v0/` · `/home/ec2-user/css/kernel/kernel-of-truth/data/nsk1-clutrr/` · `/home/ec2-user/css/kernel/kernel-of-truth/data/nsk1-eval/` · `/home/ec2-user/css/kernel/kernel-of-truth/data/onto-obo/` · `/home/ec2-user/css/kernel/kernel-of-truth/poc/deconf-a1/audit_a1.py` · `/home/ec2-user/css/kernel/kernel-of-truth/poc/f2b/runner/f2b_runner.py` · `/home/ec2-user/css/kernel/kernel-of-truth/poc/nsk1/nsk1_runner.py` · `/home/ec2-user/css/kernel/kernel-of-truth/registry/verdicts/l3a.json` · `/home/ec2-user/css/kernel/kernel-of-truth/docs/design-l3a-rules-engine-oracle.md` · `/home/ec2-user/css/kernel/kernel-of-truth/docs/next/architecture-ladder.md` · `/home/ec2-user/css/kernel/kernel-of-truth/reports/sparq-estate.md` · `/home/ec2-user/css/kernel/sparq/crates/sparq-reason/`
