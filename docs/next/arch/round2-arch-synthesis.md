# Kernel-of-Truth round-2 architecture SYNTHESIS — the full-UFO question

> **Provenance + transcription note.** Composed 2026-07-12 by the `synthesis` agent of workflow run
> `wf_3870703d-0bb` (`neurosym-arch-exploration`); reviewed by its independent refutation-stance
> `review` agent — verdict **SHIP-WITH-FIXES**. This transcription applies three of the review's
> fixes: (i) the inputs paragraph now cites the exact committed paths of the design/critique/landscape
> docs (extracted to `docs/next/arch/` alongside this file); (ii) the DECONF Stage-B line is corrected —
> Stage B was still listed as future GPU spend, but it had already run and holds a registered **PASS**
> verdict (`registry/verdicts/deconf-b.json`, computed 2026-07-11T21:51Z); (iii) the "frozen" wording
> on UFO-KGE-1 is softened — **no UFO-KGE-1 pre-registration exists yet**. [PROPOSED-ASM-1502] The
> remaining SHIP-WITH-FIXES items (sparq code-pin commit SHAs, the g2-import A2-vs-A3 κ-channel
> sentence, the CASC-0 post-INSTRUMENT-INVALID next step, issue-#20 open/closed wording, the sparq PR
> dedup check, a UFO-KGE-1 wall-clock bound on the 2-core box) are recorded as open review items and
> are NOT yet applied. All other text is verbatim from the workflow output.

**Role of this document:** composition only. It ranks the candidates, merges their strongest parts, and sequences the work. **No feasibility conclusion on either programme thesis is stated or implied anywhere; CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING.** Verdicts belong to the maintainer, verdict-gen, and the review gates. Epistemic tags: [MEASURED] = pinned artifact in-repo; [ARCHITECTURE-VERDICT] = docs/next/arch/ufo-rdf12-expressibility.md; [STIPULATED] = a composition/sequencing choice made here; [EXTRAPOLATION] = expectation to be tested, never a premise; [LIT-BACKED] = published result.

**Inputs composed:** the six-layer `full-ufo-kernel` design (`docs/next/arch/full-ufo-kernel-design.md`) + its adversarial critique (`docs/next/arch/full-ufo-kernel-critique.md`; design-level verdict: novel, buildable; failure modes led by benchmark circularity — the same agent pool authoring UFO rules, fixtures, and gold); the other five candidate designs + critiques (`docs/next/arch/round2-candidate-designs.md`); the `CK-UFO` candidate (docs/next/arch/full-ufo-kernel-ck-ufo.md) with its own honest-risk section; the sparq estate report — vectors + reason — and the portfolio-gap analysis (`docs/next/arch/sparq-estate-landscape.md`); the UFO-SN3 expressibility verdict [ARCHITECTURE-VERDICT: YES-WITH-EXTENSION]; the foundational-ontology-import design (issue #20); and the fresh g2-import mechanical verdict [MEASURED: registry/verdicts/g2-import.json, computed 2026-07-12].

---

## 1. Ranked shortlist (best first), value x feasibility x cost

### 1. KUFO/1 — the MERGED full-UFO thin slice (adopt; run now)
[STIPULATED merge] Take the six-layer `full-ufo-kernel` skeleton and its experiment-first economics (Wave-1 sparq ≈ 1 agent-week; UFO-KGE-1 at ~$0 CPU; UFO-CHECK-0 rider at $5–20 GPU; engine L-band spend gated behind a measured GO), and repair it with exactly the two things CK-UFO does better: (i) a **representation-matched null arm** — same proposition/world/reifier node budget, no UFO rules — so a lift cannot be attributed to "more explicit nodes" (this plus the seed-pinned deranged-meta-typing arm answers the lead critique failure mode, benchmark circularity, from both directions); and (ii) CK-UFO's **four-valued result contract** (ENTAILED / CONTRADICTED / UNDERDETERMINED / OUT-OF-PROFILE) and versioned per-concept record, which is the right bridge-record shape and keeps "the logic lacks facts" distinct from "the commitment exceeds the executable profile". This ranks first because it is the only candidate that buys an attributable, decisive readout on the distinctive full-UFO content (derived disjointness theorems, rigidity semantics, relator structure, statement visibility) at ≤ ~$25 cash, exploits an ablation axis the harness has been carrying dormant [MEASURED: eval.rs gufo_prior hard-wired false; taxonomy.rs:33 deferral], and strands at most one agent-week if it dies. Both critiques rate the direction feasible; both converge on the same top risks (circularity, annotation scarcity, marginal lift over the strong closure+type-negatives baseline), and all three are answered inside the design by controls rather than by argument.

### 2. g2-import instrument repair + re-mint (not a full-UFO candidate; competes for the same type-layer slot; cheapest evidence on the board)
[MEASURED, PROVISIONAL-ON-LLM-PROXY] The imported-soft-typing arm A3 (BFO+SUMO+FrameNet) scored 57/84 = 0.679 sound vs the frozen 33/84 = 0.393 hard-typing baseline, McNemar p = 7.0e-5, non-vacuous 83/84 — a GO-shAPED signal — but the mechanical verdict is **INSTRUMENT-INVALID** on exactly one channel (judge-pair κ_A3 = 0.286 < 0.40), which per the pinned decision table means "no conclusion; repair and mint a new frozen run". Ranked second because the marginal cost of converting a GO-shaped signal into a licensed engineering GO is one instrument repair + one ~$10 annotation-lane re-run — the best evidence-per-dollar available anywhere in this synthesis — and because its result directly conditions how much layer-2 typing work the full-UFO bridge must carry. It is **complementary, not competing** [STIPULATED]: the import fixes layer-2 per-argument typing (the measured g2 failure), full UFO supplies layer-1 modal/identity/dependence discipline that no lexical resource carries (foundational-ontology-import.md §2.1).

### 3. CK-UFO as a standalone checker-first programme (do not run separately; fold in)
CK-UFO's distinctive spend — a 144–192-case independently-reconciled gold set across six UFO families before any other work — is the right *promotion instrument* but the wrong *first dollar*: its first signal costs 1–3 engineering weeks plus reviewer-days [CK-UFO §3.6, EXTRAPOLATION], where UFO-KGE-1 + UFO-CHECK-0 produce attributable signal in about a week for ≤ ~$25. Its A1 null, result contract, gold-independence discipline, and go/no-go thresholds (≥10pp over baseline, proof validity ≥98%, judgeable coverage ≥80%, no dangerous-false-accept increase) are adopted into KUFO/1; the gold-set build proceeds in the annotation lane in parallel (decision D2 below) and becomes the gate any *promotion* must pass. Ranked third as a standalone bet, first as a source of controls.

### 4. Engine-only UFO-SN3 reference implementation (defer; the surviving fallback)
[ARCHITECTURE-VERDICT] UFO-SN3 is expressible and decidable as a finite-world profile, and the expressibility doc says GO on a bounded sparq reference implementation opened as a clearly-labelled draft PR. But the engine work (quoted-triple destructuring/construction, situation indexing, closed-scope validation stratum) is the L-band item (~4–8 weeks in CK-UFO's estimate), its value case is entirely unmeasured, and both designs agree it must not be bought before the cheap experiments read out. If the vector legs die (A3 ≈ deranged A4 everywhere), this is the surviving "checking, not embedding" value case, assessed on UFO-CHECK-0's own endpoints. Rank reflects cost and stranding risk, not doubt about expressibility.

### 5. gUFO-labels-only prior (dominated; subsumed)
Wiring the dormant gufo_prior axis with taxonomy labels alone buys class names without theorems — precisely the limitation the expressivity analysis records and the reason the axis has sat unimplemented [MEASURED: taxonomy.rs:33]. It survives only as the c1 reader inside Wave-1, never as a candidate.

**Standing constraint carried from both designs [STIPULATED]:** nothing above modifies, widens, or delays the in-flight evidence gates — RULES-1's frozen inputs, the RULES-2 build, knull-v2, or the g2-import repair. Attribution beats enthusiasm.

---

## 2. The full-UFO kernel, treated explicitly

**Now vs later — split the candidate at the money line [STIPULATED].** NOW: the thin slice — Wave-1 sparq vector work (~1 agent-week), the ~$0 CPU decisive experiment UFO-KGE-1, the $5–20 GPU rider UFO-CHECK-0, and the record-schema + gold-set spike in the annotation lane. LATER, strictly behind the pre-registered GO: rigidity-aware training and the compositional statement encoder (Wave 2), the sparq-reason engine programme and situation-indexed scoring (Wave 3). Rationale in plain terms: the current stack cannot use full-UFO content *even in principle* (quoted triples are structurally invisible to the embedding layers; the oracle reads only asserted disjointness), so a small, reversible widening is enough to find out whether the distinctive content earns anything — and if it earns nothing, we will have spent a week and twenty dollars learning that, instead of two months building an engine for it.

**What full UFO buys over gUFO** (the contrast both designs agree on; all lifts [EXTRAPOLATION]):
1. **Executable modal content** — world-indexed rigidity checking, anti-rigidity counterworld witnessing, existence propagation: statable nowhere in the gUFO/OWL rendering, executable as safe Horn rules once worlds are data (RDF 1.2 quoted triples + reifiers) [ARCHITECTURE-VERDICT].
2. **Derived constraint mass with zero authoring** — all distinct Kinds pairwise disjoint (unique-ultimate-sortal theorem) plus rigid-cannot-specialise-anti-rigid as a subsumption mask [LIT-BACKED: Guizzardi 2005], where gUFO yields only what someone asserted.
3. **Identity criteria** — an answer-safe entity-resolution mask (shared identity provider required) and sameContinuant discipline; gUFO has no executable identity semantics.
4. **Relators and qua-individuals** — mediation/dependence/derivation axioms instead of faked binary edges.
5. **Endurant/perdurant/trope discipline as geometry**, not labels.
6. **Claims-about-claims** — beliefs, situations, and explicit negative facts held without assertion (opacity conformance-tested).
What it does NOT buy: decision procedures for unrestricted modal/deontic validity, arbitrary identity formulae, or unrestricted mereology [ARCHITECTURE-VERDICT boundaries]; and no typing-soundness improvement by itself — the g2 lesson [MEASURED: 0.39-sound, PROVISIONAL-ON-LLM-PROXY] is that discipline, not vocabulary, is what helps, so every UFO commitment enters as an authored, endorsed bridge judgment with `underdetermined` default, never read off prime occurrences.

**The concrete sparq upstream programme** (draft-PR-able on the fork; bands S ≈ ≤1 agent-day, M ≈ 2–5 agent-days, L ≈ 1–3 agent-weeks):

| PR bundle | Contents | Band | Gate to open |
|---|---|---|---|
| **PR-1: quoted-triple visibility in sparq-vectors** | b1 widen is_entity→is_embeddable (train.rs:353, eval.rs:116, structure.rs:409) behind a `quoted_terms` ablation flag, byte-stable baselines; verbalisation fix (grounding.rs:793 empty-string bug); vec: bindings (rewrite.rs:649); b3 position-aware negative sampling + `synthetic_rdf12` eval slice | S + S–M | Now |
| **PR-2: UFO prior reader + derived constraints** | c1 `ufo_priors.rs` read-only reader (meta-type, rigidity, identity-provider, mediation, inherence; wires the dormant gufo_prior axis); c2 UFO-provable disjointness + subsumption mask into DisjointnessOracle (answer-safe) | M + S | Now |
| **PR-3: opacity conformance in sparq-reason** | a1 tests pinning "quoting never asserts" + closure non-interference for triple-term ids | S | Now |
| **PR-4: rigidity-aware training + compositional statement encoder** | c3 CKRL-style rigid/anti-rigid weighting + refined negatives; b2 statement encoder Block (learned-row vs deterministic compositional variants) | M + M | UFO-KGE-1 GO only |
| **PR-5: engine — quoted-triple inference** | a2 destructure/construct restricted to reifying existing base triples (Herbrand base kept finite); a3 situation indexing + `ufo-sn3` regime tag + rule modules; a4 closed-scope validation stratum (stratified NAF inside declared closedFor only, violations never entailments) | L (phased M/M/M) | GO + rider signal |
| **PR-6: relator/inherence priors + situation-indexed scoring** | c4, c5 | M + M | Last, on GO |

Sequencing: Wave 1 = PR-1 + PR-2 + PR-3 ≈ 1 agent-week, which fully unblocks the decisive experiment (RDFS closure suffices; no engine work on that path). PR posture per standing practice: staged on the fork, consolidated (three drafts now, not six), each carrying the review-timing footer; the L-band engine bundle is deliberately not opened until the measured GO exists.

**Decisive experiment + gate (to be pre-registered before any run, per the standard prereg protocol — no frozen record exists yet; the frozen entry will live at registry/experiments/ufo-kge-1.json; summarised):** UFO-KGE-1 — 2x2 + attribution controls (A0 strong baseline / +UFO prior / +quoted-term visibility / both / both-with-deranged-meta-typing / representation-matched null), filtered MRR + Hits@k, ≥5 paired seeds, ComplEx primary; primary endpoint the pre-registered composite slice (anti-rigid role/phase edges + relator-derived material edges); overall-slice non-inferiority margin pre-registered. GO requires beating baseline with per-seed-paired LCB95 > 0 AND beating the deranged control AND beating the representation-matched null; a GO licenses Wave-2/3 spend and a transfer gate onto the kernel+world graph — **it licenses no thesis conclusion**, and a standing synthetic-slice scope rider attaches (schema-bearing synthetic wins do not extrapolate to other corpora). NO-GO kills the UFO-specific vector work at this scope and leaves only the engine-only checking case for separate assessment.

---

## 3. Next-wave plan (freeze + run now vs design-first)

**GPU-runnable NOW — one lane per Modal account [STIPULATED assignment; all within the standing compute authorization; freeze before run; report after]:**
1. **UFO-CHECK-0** (new; 2–6 GPU-h, $5–20, a10g class): SmolLM2-135M/360M verify-retry on two-situation modal/rigidity items, gold and UFO-SN3 fixtures pre-materialised by a Python twin (rules-1 twin_engine + modal wrapper + f2b HFLM scorer precedents; **no sparq changes on its path**). Five arms: no-checker / gUFO-taxonomy checker / UFO-SN3 checker / deranged meta-typing / representation-matched null (the CK-UFO fold-in). Endpoints: accuracy on engine-derived gold, dangerous-wrong rate, per-query cost. Labelled oracle-diagnostic (ASM-0814 lineage); formal templated inputs; no NL-reach claim.
2. **RULES-1 GPU arm + knull-sourced-rules ablation**: the freeze-ready draft exists [MEASURED: poc/rules-1/RESULT.md — engine + worlds + $0 certificate executed 2026-07-11] and the k1/k2 ablation bead is ready; freeze and run.
3. **knull-v2 completion**: knull-v2 modal cells began landing 2026-07-11 [MEASURED: poc/knull/results-incoming, pinned image]; finish the cell matrix and analysis. (DECONF Stage B, listed here as future spend in the workflow's original composition, had in fact **already run and PASSED** — registered verdict `registry/verdicts/deconf-b.json`, computed 2026-07-11T21:51Z, audit CONFIRMED; it is a completed anchor, not a pending lane, and its verdict sentence + extrapolation envelope live in that record.)
4. **NLB-0B pilot leg** (≤5 GPU-h + ≤$25 API), feeding the NLB-1 freeze — the only structurally large GPU sink on the board (~50 GPU-h) and the correctness-crux leg.
RULES-2's Modal LoRA harness (in build) joins whichever account frees first once freeze-ready.

**Design-first (no GPU yet):** UFO-KGE-1 (needs Wave-1 Rust; CPU-only by design — do not dress it up as GPU work); the CK-UFO record schema + 144–192-case gold set (annotation lane: independent authoring via the GPT-5.6 annotator-proxy pattern, human reconciliation later, derangement probes included); the g2-import κ repair + re-mint (annotation lane, ~$10); the PR-5 engine contract (a2 semantics: depth-restricted construction, opacity conformance — write the contract, build nothing); CASC-0 prereg completion.

---

## 4. Open decisions for the maintainer (with recommendations)

1. **Adopt KUFO/1 (merged thin slice) as the round-2 portfolio entry, with cost ceiling ≤$25 cash + ~1 agent-week Wave-1 Rust, engine work gated behind the pre-registered GO?** Recommendation: yes — it is the cheapest attributable test of the maintainer-proposed direction, and its worst case is a bounded, informative kill.
2. **Gold authorship for the UFO checking experiments** — accept engine-derived gold now (oracle-diagnostic label) for UFO-CHECK-0, with the independently-reconciled CK-UFO gold set (GPT-5.6-proxy authored, human-reconciled later) required before any *promotion*? Recommendation: yes; this is the concrete repair for the benchmark-circularity failure mode both critiques lead with, at no delay to the first signal.
3. **Anchor family** (ties to the open issue-#20 decision): BFO-now/gUFO-when-ingested as one anchor family, vs waiting on a pinned gUFO ingestion? Recommendation: BFO-now/gUFO-later; do not block Wave-1 on ingestion — the synthetic slice and bridge records carry the classifications either way.
4. **sparq PR posture**: open PR-1/PR-2/PR-3 as consolidated draft PRs on the fork now, engine PRs only on GO? Recommendation: yes — three drafts maximum, review-timing footer on each, consistent with the upstream-volume constraint.
5. **Relationship between full-UFO and the import-soft-typing route**: treat as complementary layers (layer-1 modal/identity vs layer-2 argument typing) and proceed with the g2-import instrument repair + re-mint independently? Recommendation: yes — the repair is the best evidence-per-dollar on the board, and its outcome tells the bridge how much layer-2 weight it must carry.
6. **Budget ratification for the GPU wave** (UFO-CHECK-0 $5–20; RULES-1 arm + knull ablation ~$15–30; NLB-0B ≤$25 + API — DECONF-B is removed from this list: it already ran and holds a registered PASS, `registry/verdicts/deconf-b.json`): within the standing authorization, spend-and-report-after? Recommendation: yes, per the no-re-surface-once-approved practice, with per-experiment caps as listed.

**Closing restatement:** every expected lift named above is [EXTRAPOLATION] and licenses nothing; the measured anchors are the g2 0.39-sound readout, the g2-import GO-shaped-but-INSTRUMENT-INVALID result, the RULES-1 certificate, the DECONF Stage-B PASS (scope-limited per its own envelope), the f2b lineage numbers, and the sparq code-state pins. **No feasibility conclusion on CORRECTNESS or EFFICIENCY is stated or implied; both remain INCONCLUSIVE-PENDING.**
