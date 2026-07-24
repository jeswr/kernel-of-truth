# S3 grounding-checker — FREEZE-READY pre-registration design (crossed 2×2, plain-v5-natural opponent, P-strict primary)

> **Status: PREREG DESIGN — freeze-ready, NOT frozen.** Authored by the
> architecture-advisor role (Fable) on coordinator request after the maintainer
> RATIFIED (issue #60) the S3 scoping's seven questions: host portable-first
> (Q1), λ within the KOT-HON/1 band (Q2), TOST/futility mandatory at first
> freeze (Q3), freeze gated on certified cluster count not calendar (Q4),
> opponent = plain-v5-natural extended under matched expressivity (Q5),
> P-strict confirmatory primary (Q6), and the CROSSED 2×2 design funded (Q7).
> Source document: `docs/next/design/colibri-s3-grounding-checker-scoping.md`
> (Rev3, ratified) — every open value there is PINNED here. Nothing in this
> document is committed, registered, frozen, or run by its author; the
> coordinator commits; the experiment-designer performs the prereg-freeze after
> the cross-vendor review and the pre-freeze gates (§10); the executor runs.
> All rows carry `PROPOSED-PREREG-ROW-S3-*` / `PROPOSED-CRIT-S3-*` labels; no
> ASM-number ids are minted here — [STIPULATED] choices are proposed assumption
> rows the coordinator registers at the landing commit.
>
> Companion artifact: `docs/next/design/s3-prereg-power-sim.py`
> (sha256 `6d5d0ce9d6bcfa3d1b1c59824df8ff1ab2ef574869e87c5c516aefccc7b8f7b9`),
> the executed planning power simulation (seed 20260724, $0, this box).

---

## 0. Inherited premises (restated from the ratified scoping; sources authoritative)

PREMISE: the S3 seam exists and is net-new — colibri-pattern GBNF admissibility machinery, no grounding hook, grammar never a hard sampler constraint [MEASURED: reports/colibri-recon-2026-07-21.md §S3].

PREMISE: incremental constraint checking at decode removes an error class at matched model and compute (PICARD, Spider-dev execution errors 12%→2%) [LIT-BACKED: arXiv:2109.05093 (2021), verified reports/lit-structured-parsing-and-inner-symbolic.md]; grammar-constrained decoding without finetuning substantially outperforms unconstrained LMs on structured tasks [LIT-BACKED: arXiv:2305.13971 (2023), verified per docs/next/lit/PARSE.sources.jsonl].

PREMISE: store content is interchangeable on a related checking seam under self-authored gold [MEASURED: registry/verdicts/knull-v2.json TOST-equivalent]; the runtime-judgment ledger is 0-for-5 [MEASURED: feasibility-synthesis v6 §2.3 via v9]; every claim is bounded by the covered slice — coverage 0.3542 at molecules-v0 on ONE pinned corpus [MEASURED: registry/verdicts/m0b.json], exploratory α_point 0.24 on the WordNet-10k draw [MEASURED: feasibility-synthesis-v9 §7].

PREMISE: the deterministic engine's exactness at certified scope is the programme's working instrument — l3a engine leg covered-exact Wilson-LB 0.9955, audit CONFIRMED, on ONE engine build over a 598-record world layer [MEASURED: registry/verdicts/l3a.json].

PREMISE: the F1-K power geometry is the calibration anchor — C = 96 clusters, n = 1,573 items for ~80% per-rung power at μ* = +4.09 accuracy points with +3.0 as licensing floor only; an effect exactly at the floor fires ~50% [MEASURED: registry/experiments/f1k.json `analysis_plan_ref` + `n_planned` — a record-of-registration citation (the geometry as registered), not a run outcome]; and eligible-inventory can gate a campaign [MEASURED-as-record: programme memory, F1-K askability knife-edge, ~116 authored kernels].

STIPULATED: this is a correctness-thesis experiment; any speed co-benefit is reported in the metric vector V and is not the claim.

---

## 1. Claims and estimands (pinned)

**PROPOSED-PREREG-ROW-S3-01 (final form).** Two registered claims, each with ONE
primary licensing rule, both reported at equal prominence whatever their outcome:

- **C-MECH (mechanism):** on the frozen covered item universe, the P-strict
  store-compiled admissibility mask at the answer span adds KOT-HON/1 utility
  beyond the same facts as prompt text AND beyond format-only constraint.
  Confirmatory contrast pair: Δ(M_K − T) and Δ(M_K − G); licensing is the
  CONJUNCTION (both fire).
- **C-KERN (kernel-specific mask; registered only if PRECERT-S3-1 certifies):**
  holding context text fixed, the kernel-compiled mask beats the identical
  mechanism compiled from the matched non-kernel store. Confirmatory estimand
  = the mask-source MAIN EFFECT over the crossed 2×2
  {context: kernel-text, N-text} × {mask: K-mask, N-mask}:

  > Δ_mask = ½ · [ (S(M_K) − S(X_KN)) + (S(X_NK) − S(M_NN)) ]

  computed over ALL confirmatory items (mask-agreement items contribute exact
  zeros; the dilution is disclosed and priced into power, §8). Both simple
  effects, the context×mask interaction
  I = (S(M_K)−S(X_KN)) − (S(X_NK)−S(M_NN)) with cluster-bootstrap CI, and the
  certified-disagreement-subset subgroup read are co-reported (descriptive).
  The full-package contrast S(M_K) − S(M_NN) is a SECONDARY
  "kernel-source-stack" reading in package language only — never
  mask-at-the-seam language.

STIPULATED (pin, ratified Q7): the crossed 2×2 isolates the mask channel because each simple effect holds the context text byte-fixed and swaps ONLY the compiled mask; averaging the two simple effects removes the context main effect by construction. The Rev2 bundled-contrast defect and its correction are recorded in the scoping §10. Proposed for registration at the landing commit.

**Registered secondary readings (named in advance, never promoted):**
REGISTERED-READING-1: if Δ(M_K−T) fires but TOST concludes equivalence on
Δ(M_K−G), the licensed reading is "the lift is format-borne, not
semantic-content-borne". REGISTERED-READING-2: the package contrast
S(M_K)−S(M_NN). REGISTERED-READING-3: risk–coverage geometry per arm.

**Scope rule (binding):** the mechanism guarantees structural/enumerated
consistency inside constrained spans, never general factual truth of free
prose; no "hallucination elimination" narration [STIPULATED, carried verbatim
from scoping §1.4].

---

## 2. Host model and stack (pinned)

**PROPOSED-PREREG-ROW-S3-09 (host pin).**

- **Host:** `Qwen2.5-7B-Instruct` (Apache-2.0), F16 GGUF, run under
  **llama.cpp** — pinned llama.cpp commit, build flags, GGUF file sha256, and
  HF weights revision sha recorded in the freeze manifest at bring-up (recording
  them is itself a freeze blocker). Decoding: temperature 0 (greedy), top-p 1.0,
  single-stream per item (batch 1), fixed thread count, pinned stop sequences,
  `max_new_tokens` 192 (pass 1) / 16 (pass 2).
- **Candidates considered:** Llama-3.1-8B-Instruct (meta), Gemma-2-9B-it
  (google), Phi-4-mini (unmapped family under `kot-family-map/1` — UNKNOWN
  fails closed in the estate's seat machinery), OLMo-2-7B (weaker
  instruction-following floor). STIPULATED (pin): Qwen2.5-7B-Instruct, because (i) per-request GBNF grammars + logits access are first-class in llama.cpp for this model with no thinking-mode toggle confound; (ii) strong small-model instruction compliance protects the T/B extraction legs; (iii) FAMILY-ROLE DISJOINTNESS — under the pinned family map the host resolves `alibaba`, the N-store author resolves `openai`, every LLM judge seat resolves `anthropic`: no vendor family occupies two of {system-under-test, opponent-author, evaluator}; (iv) permissive licence and a Q8_0 fallback of the SAME weights if F16 throughput busts the cost ceiling (quantisation swap = ops amendment, logged pre-powered-run). Proposed for registration at the landing commit.
- **Pinned fallback host:** Llama-3.1-8B-Instruct, switchable ONLY on a named
  bring-up failure (grammar hook defect, chat-template defect, GATE-0(d)
  behaviour gate failure), before any powered decode, logged as an ops
  amendment; a post-powered-run switch is prohibited.
- **Mechanism implementation (insertion point 1, per the scoping):** because
  the item format fixes (s, r) before decode (§4), each arm×item admissibility
  mask compiles OFFLINE to a per-item static GBNF grammar enforced at the
  sampler during the answer pass. This realises the hard sampler mask with
  identical accept/reject decisions to a per-token dynamic hook; free-running
  dynamic re-masking mid-generation is OUT OF SCOPE of this prereg and said so
  in every readout [STIPULATED implementation choice; the estimand is the
  checker at the answer span].
- **Two-pass protocol (all arms identically):** pass 1 = unconstrained
  reasoning (byte-pinned instruction template per arm, ≤192 tokens); pass 2 =
  answer-only continuation in the same context, grammar per the arm roster
  (§5). DRAFT/MTP off. No hosted-completion API anywhere in the decode path
  (ratified Q1; the scoping §5.4 logits-hook constraint).

STIPULATED (instrument expectation, gated not assumed): with per-item single-stream greedy decoding, run-to-run token-level determinism is an achievable instrument property; it is VERIFIED at bring-up by the reproducibility gate (§10 G-R), and a failure there is an instrument defect to fix before freeze, never a waived check.

---

## 3. Stores, compile pipeline, and the matching manifest (pinned)

### 3.1 Kernel side

Stratum-2 concept inventory (54 kernel-v0 + 54 molecules-v0 = the 108 covered
concepts), stratum-3 `kot-axiom/1` sidecar, and a stratum-4 world-layer record
set AUTHORED for this experiment by the explicator role over the pinned domain
slice (§4.1), validated by the pinned deterministic engine (the l3a
`kot_axiom.py` lineage, build sha pinned); the admissibility closure is the
engine's materialised entailment closure. The verifier stays outside the vector
and the model; no similarity computation appears anywhere in the mask path
(X3 cosine ban) [STIPULATED, carried from scoping §1.2].

### 3.2 Non-kernel opponent (ratified Q5)

**PROPOSED-PREREG-ROW-S3-07 (final form).** The opponent store is
**plain-v5-natural-TYPED (PV5T)**: the plain-v5-natural store contract
(`docs/next/design/plain-v5-natural-store-contract.md` — authoring blindness,
lint, gates, seat ledger, disclosure) extended with a typed fact/constraint
layer over the SAME pinned domain slice, under matched semantic expressivity:

- typed relation inventory of matched breadth (at minimum the answer-bearing
  relations of §4.1 plus the same constraint families the kernel sidecar uses:
  subClassOf-like, disjointWith-like, domain/range, functional, cardinality —
  expressed natively in the PV5T record grammar, not in any RDF/OWL formalism);
- the SAME deterministic closure engine runs over PV5T records exactly as over
  kernel records (asserted-only opponents disallowed);
- compiler/checker code paths BYTE-IDENTICAL (same programs, different input
  records); same source-quality gates; runtime accounting in the same V columns;
- authoring parity: PV5T's typed layer is authored by GPT-5.6-Sol under the
  plain-v5 blind-envelope discipline; kernel stratum-4 by the explicator role;
  each side's authoring budget logged and within ±25% of the other (proposed
  parity number: 12 agentic-hours-equivalent per side — maintainer micro-
  decision M-2, §12); an impoverished strawman opponent voids C-KERN;
- coverage certified per-item over the frozen universe: every item's presented
  options are evaluable (derivable-or-not) under BOTH closures — 100%, fail
  closed;
- store bytes reported; admissible-set size distributions at the answer slot
  reported per store; any mismatch disclosed and bounded (the §5.2 cardinality
  floors bind under EACH mask separately).

**Opponent-expressivity certification (pinned, $0, offline, pre-freeze):** a
deterministic manifest check that PV5T instantiates every constraint family the
kernel-side axiom records use on the frozen slice, plus closure-engine parity
(same engine build sha on both stores). Failure = fix PV5T or STOP; an
expressivity-deficient opponent cannot enter the crossed cells.

### 3.3 Compile

`A_store(item) = { o ∈ options(item) : closure_store ⊨ assertion(item, o) } ∪ {UNKNOWN}`
computed offline by the pinned engine per store per item; compiled to the
answer-pass GBNF. UNKNOWN (the fail-closed abstention production) is admissible
in EVERY masked arm on EVERY item, verified mechanically at compile time
(ROW-S3-08). Completability holds by construction (options are complete
strings). Mask-build determinism: sorted enumeration order pinned; the full
per-item mask table (item × arm × admissible set) is a sha-pinned frozen
artifact, and PRECERT/KILL-2 Stage-1 read it, never recompute ad hoc.

---

## 4. Item universe (T-A pinned as primary; FORK-S3-B resolved by pin)

### 4.1 Domain and gold

**PROPOSED-PREREG-ROW-S3-10 (item source pin).**

- **External domain source:** Open English WordNet 2024, the release archive
  already sha-pinned in the estate (`poc/plainv5/inputs/oewn-pin.json` chain) —
  content fixed years before any programme item; CC-BY 4.0. Domain slice D* =
  noun synsets reachable within ≤2 hypernym steps BELOW the pinned synsets of
  the 54 molecules-v0 concepts (per the pinned plain-v5 sense map), plus their
  OEWN-asserted part-meronyms and attribute links; the slice extraction is a
  pinned deterministic script whose output is sha-frozen before either store's
  world layer is authored. Using an external structured source as a FACT
  source imports no semantic-web formalism: both stores represent the slice
  natively (kot records / PV5T records) [STIPULATED; directives §1 respected].
- **Answer-bearing relations:** `kind` (hypernymy) and `part` (meronymy) —
  both covered kernel concepts — plus attribute links as differentia material.
- **Item form (selection with abstention):** stem = a differentia question
  about a subject entity (differentia drawn from OEWN glosses/relations, NOT
  from either store's records); k = 6 presented options + UNKNOWN; exactly one
  gold option per OEWN; ≥2 options certified NON-derivable under BOTH closures
  (the fabrication error class the mask can remove); remaining options
  derivable true-facts that fail the differentia (real ways to be wrong inside
  the mask).
- **Gold independence (T-A discipline):** gold = the OEWN assertion,
  deterministically extracted; a single Claude-family sense-fit read
  (veto-only, ledgered under the estate's seat discipline) may VETO an item,
  never re-key it. Gold is never computed from either store's closure; engine
  certification of item consistency is a construction check, never the gold
  source. Items whose gold cannot be OEWN-certified are dropped, not re-keyed.
  Where this fails wholesale the endpoint renames to closed-world store
  conformance and cannot carry the correctness headline [carried verbatim from
  scoping §3.2].
- **Cluster key:** each item carries `primary_cluster` = the covered concept
  anchoring its subject entity (the molecules-v0/kernel-v0 concept whose pinned
  synset dominates the subject in D*), assigned by a pinned deterministic
  function at build time. Sensitivity co-report: re-analysis under
  subject-entity clustering (descriptive robustness read).

STIPULATED (pin, resolves FORK-S3-B): T-A is the primary and ONLY powered family; T-B (contradiction-avoidance slot-fill) runs as a 50-item descriptive pilot probe only; T-C is dropped. Any promotion of T-B is a new prereg; the GATE-0(d) behaviour gates are the guard. Proposed for registration at the landing commit.

### 4.2 Effective non-degeneracy (pinned thresholds)

**PROPOSED-PREREG-ROW-S3-05 (final form).** Per item, offline, pre-
randomisation, certified SEPARATELY under the K-mask and the N-mask on the
common item set (only items passing under BOTH enter the confirmatory set):

(a) admissible gold, and every independently-valid alternative is keyed into
the gold set (OEWN multi-gold items are excluded rather than multi-keyed);
(b) ≥1 admissible certified-incorrect competitor;
(c) prefix-forcing audit through the compiled automaton — no forced prefix
determines gold before the answer slot;
(d) plausibility/length controls — gold and competitors within pinned surface
bands (character-length ratio ≤ 1.6 between gold and competitor median;
distractor plausibility screened by one Haiku-seat read, veto-only);
(e) cardinality floors under EACH mask: admissible options ≥ 3 (incl. gold),
set median ≥ 4 of 6.

### 4.3 Geometry (the f1k lesson, applied)

**Pinned N:** EXACTLY **n = 1,920** certified confirmatory items over
**C ∈ [54, 96]** realized clusters, EVERY cluster ≥ 12 items, realized C and
all per-cluster counts frozen pre-decode. Planning geometry 96×20; the C=54
inventory-collapse case is simulated and survives (§8). The 50-item pilot
(stratified, ≤1 item per cluster) is drawn by seeded random BEFORE the
confirmatory freeze and QUARANTINED — pilot items never enter the confirmatory
set (greedy decoding makes pilot outcomes deterministic re-runs, so exclusion
is the only clean wash). Candidate pool required ≈ 3,000–3,500 template-
generated items pre-certification; the INVENTORY GATE (§10 G-I) is a freeze
blocker, not a footnote.

---

## 5. Arms (final roster) and matched-arms protocol

**PROPOSED-PREREG-ROW-S3-02 (final form).** All arms: matched model, matched
decoding parameters, matched two-pass protocol, matched item set, paired.

| Arm | Context text | Answer-pass grammar | Status |
|---|---|---|---|
| **M_K** | kernel facts as text (pinned renderer) | K-mask (A_K ∪ UNKNOWN) | confirmatory (C-MECH + 2×2 cell) |
| **X_KN** | kernel facts as text | N-mask | confirmatory (2×2) — decoded only if PRECERT passes |
| **X_NK** | PV5T facts as text (same renderer discipline) | K-mask | confirmatory (2×2) — idem |
| **M_NN** | PV5T facts as text | N-mask | confirmatory (2×2) — idem |
| **T** | kernel facts as text | none (format instruction only) | confirmatory null (Law 2 opponent) |
| **G** | kernel facts as text | presented-options grammar (all 6 + UNKNOWN; no store input) | confirmatory null (format-only) |
| **B** | no store facts | none | mandatory second null |
| **D^policy** | kernel facts as text | deranged-K masks, 3 pinned seeds | validity gate arm (240-item subset, §7 KILL-2) |
| T_N, M0_K, M0_N | — | — | EXCLUDED from this run [STIPULATED: cost discipline; neither estimand needs them; listed so their absence is a decision, not an omission] |

Context rendering: ONE pinned renderer, store-symmetric; per-item context = the
item's cluster records + one-hop closure neighbourhood, deterministic selection
rule, hard cap 1,400 prompt tokens, token counts reported per arm (F0
accounting, ROW-S3-03 unchanged from scoping). B's shorter prompt is a reported
token credit.

**PROPOSED-PREREG-ROW-S3-08 (final form).** Identical across ALL arms:
explicit abstention availability (UNKNOWN admissible in every grammar and
instructed in every arm), instructions, stopping rules, token budgets, decoding
parameters, seed handling, arm-blind deterministic extraction and scoring.
T/B answer extraction: pinned liberal regex over the pass-2 output; an output
matching no option and not UNKNOWN scores WRONG (KOT-HON/1: a non-abstention
non-answer on an answerable item is a wrong answer); non-parse counts reported
per arm with a sensitivity re-analysis excluding non-parse items. Any protocol
asymmetry is a validity defect.

---

## 6. Primary endpoint (fully operational)

**PROPOSED-PREREG-ROW-S3-01 endpoint block (final form).** Primary endpoint =
paired difference in KOT-HON/1 utility S_λ between arms over the confirmatory
item set, concept-clustered, scored against the store-independent gold of §4.1
by arm-blind deterministic extraction.

- **λ = 3, pinned NOW, pre-pilot, pre-outcome.** Justification (ratified Q2,
  band [2,5]): no measured harm ratio exists for this surface, so the band
  default applies; the direction is anchored by the programme's standing
  evidence that wrong-with-provenance is worse than refusal [MEASURED:
  registry/verdicts/a5-nl.json S2 kill, 5.0% wrong-with-provenance] — masked-
  span answers read as store-licensed, so the wrong:correct harm ratio is
  materially above 1, excluding λ = 2 complacency; no declared deployment
  ratio licenses 4–5; single-item influence (1+λ)/n = 4/1920 ≈ 0.0021 keeps
  the score out of the noisy-wrong-counter regime. Changing λ after any
  readout is endpoint-shopping and prohibited.
- **Scoring:** +1 correct; 0 explicit UNKNOWN abstention (stays in the
  denominator); −3 wrong. Silent empty/non-parse on an answerable item is
  WRONG.
- **Mandatory co-reports (every S_3 readout, every arm):** S_2 and S_5;
  answer rate a; precision-on-answered p; abstention rate (reasoned vs
  reasonless split); wrong-rate W/N; raw recall r; the full risk–coverage
  curve.
- **Degenerate-abstention guard:** per-arm answer-rate co-floor **a ≥ 0.50**
  on the confirmatory set; a confirmatory arm breaching it renders every
  contrast touching that arm INSTRUMENT-DEGENERATE (no PASS, no equivalence,
  maintainer escalation) — the score is never gamed by abstention.
- **Margin semantics (the registered F1-K convention):** a contrast FIRES iff
  the exact cluster sign-flip test against zero (B = 10,000, add-one
  corrected, two-sided) gives p < 0.05 AND the observed Δ meets the registered
  floor. Disclosed property: an effect exactly at the floor fires ~50%.
- Secondary endpoints (reported, never promoted): grounded-precision of
  emitted assertions (by construction 1.0 under P-strict inside spans —
  forbidden as primary, carried as the tautology it is); T/B/G span
  well-formedness; full metric vector V (engine compute, prompt-token deltas,
  tok/s with/without mask, mask compile time, $ per arm).

---

## 7. Decision rules (pinned numbers, disjoint regions)

**Margins, pinned:**

| Contrast family | δ_floor | δ_eq | constraint |
|---|---|---|---|
| C-MECH: Δ(M_K−T), Δ(M_K−G) | **+0.10** S_3 points | **±0.08** | δ_eq < δ_floor ✓ |
| C-KERN: Δ_mask (all-items scale) | **+0.05** | **±0.04** | δ_eq < δ_floor ✓ |

STIPULATED (pin): δ_floor(C-MECH) = +0.10 re-derives the scoping's +0.03 anchor from planning utility variance as the scoping instructed. Interpretation at λ=3: +0.10 = converting 2.5% of all items wrong→correct, or 10% abstain→correct — about one-sixth of the maximum headroom at the planning T-arm wrong-rate (0.15); smaller floors are not honestly powerable against the mandatory equivalence test at an authorable N (§8), and a mechanism that moves less than this is not deployment-meaningful at this seam. δ_floor(C-KERN) = +0.05 on the ρ-diluted all-items scale ≈ a per-disagreement-item effect of ~0.17 at the PRECERT floor ρ_item = 0.30/0.25 — co-reported undiluted so the dilution is never hidden. Proposed for registration at the landing commit.

**Evaluation order (both trees, fixed):** superiority → harm → equivalence;
first licensed outcome taken; with δ_eq < δ_floor the TOST-equivalence and
observed-floor-superiority regions are disjoint by construction (checked in
simulation: TOST fires at true μ = δ_floor with probability 0.008).

**PROPOSED-CRIT-S3-KILL-1 (C-MECH, final):**
- **PASS:** Δ(M_K−T) fires AND Δ(M_K−G) fires (each: sign-flip p < 0.05 AND
  observed Δ ≥ +0.10). Scope: this host, this item universe, the §11 coverage
  rider.
- **HARM:** one-sided 95% UCB (cluster sign-flip CI) of Δ(M_K−T) < 0 → the
  "kernel's home is the output/logits seam" claim FAILS its pricing here.
- **EQUIVALENCE:** TOST on Δ(M_K−T): 90% sign-flip CI ⊂ (−0.08, +0.08) → the
  facts, not the mechanism, carry the value (licensed negative; equal
  prominence).
- **INCONCLUSIVE:** none licensed → home-status UNBANKED; the 2026-07-21 steer
  ranking may not be carried forward as evidence; no attribution narration
  either direction. REGISTERED-READING-1 (format-borne lift) applies only when
  Δ(M_K−T) fires and TOST concludes equivalence on Δ(M_K−G).

**PROPOSED-CRIT-S3-KILL-3 (C-KERN, final; conditional on PRECERT):** identical
ordered tree on Δ_mask with (+0.05, ±0.04): PASS → kernel-specific mask value,
scoped to the certified disagreement surface; EQUIVALENCE → the kernel mask is
source-interchangeable at this seam (the knull pattern at the mask seam; the
modal expectation [EXTRAPOLATION — flagged, premise of nothing, resolution =
this experiment]); HARM (95% UCB < 0) → the kernel mask HARMS vs the N-mask,
reported at equal prominence; INCONCLUSIVE → no kernel-attribution narration.

**PROPOSED-CRIT-S3-PRECERT-1 (final threshold):** on the frozen item universe,
computed offline from the sha-pinned mask table, BEFORE any powered decode:
- ρ_item (fraction of confirmatory items with A_K ≠ A_N over the presented
  options) **≥ 0.25**, AND
- ρ_opt (fraction of item×option pairs where the two masks disagree) **≥ 0.05**,
  AND
- disagreeing items span ≥ ⌈C/2⌉ realized clusters;
- direction split (K-only-admits / N-only-admits / both-differ) reported.
FAIL ⇒ C-KERN is NOT identifiable/powerable under this design (strict
unidentifiability only at literal set identity); the crossed cells and M_NN are
NOT decoded; the experiment proceeds on C-MECH alone; the narrowed headline
"structured-store admissibility is load-bearing" is claimable ONLY on a
subsequent C-MECH PASS. [Carried verbatim from scoping Rev3 with the threshold
now pinned.]

**PROPOSED-CRIT-S3-KILL-2 (derangement gates, final numbers):**
- *Stage 1 (offline, $0):* 3 seeded P-strict derangements (seeds 20260724001/
  002/003) of the kernel store's admissible sets; each certified: item-level
  mask-disagreement vs the true K-mask ≥ 0.5; gold-exclusion rate ≥ 0.9;
  completability 100% (UNKNOWN always admissible); per-item admissible
  cardinality within ±1 of the true K-mask's per-item cardinality; deranged
  closure internally consistent. No certifiable derangement ⇒ kernel-content
  attribution INSTRUMENT-INVALID (C-KERN and D-based validity statements); a
  separately valid C-MECH result stands.
- *Stage 2 (model-side):* 240-item subset (pinned seeded draw spanning
  ≥ ⌈C/2⌉ clusters) × 3 seeds under kernel context: mask-obedience 100% (any
  emission outside the deranged-admissible set = harness defect =
  INSTRUMENT-INVALID); correct-emission rate on gold-excluded items = 0 (any
  correct answer inside a gold-excluding mask = scoring/leak defect =
  INSTRUMENT-INVALID). D-collapse is an implementation check, never grounding
  evidence.

**Multiplicity (declared hierarchy):** two registered claims, each with one
primary licensing rule; C-MECH's conjunction is an intersection-union test
(conservative, no correction); the TOSTs are the same-contrast complements
inside the ordered trees; C-KERN is a separate claim tested regardless of the
C-MECH outcome and interpreted confirmatorily only if PRECERT passed; all other
quantities are descriptive. The P-consistent policy is NOT part of this
experiment: pilot measures its exposure rate (fraction of unconstrained pilot
outputs containing ≥1 store-contradicted assertion); a P-consistent study is a
separately-frozen follow-on and is descoped now if exposure < 0.05
[STIPULATED, per FORK-S3-A resolved-with-hierarchy].

---

## 8. Power (simulated at the real geometry; the complete licensing rule)

**PROPOSED-PREREG-ROW-S3-04 (final form).** Executed planning simulation:
`docs/next/design/s3-prereg-power-sim.py` (sha
`6d5d0ce9d6bcfa3d1b1c59824df8ff1ab2ef574869e87c5c516aefccc7b8f7b9`), seed
20260724, 4,000 reps/cell, $0. Model: discrete per-item paired utility
differences d ∈ {0, ±1, ±3, ±4} (abstain↔correct, wrong↔abstain,
wrong↔correct at λ=3), cluster random effect, movability copula for the
C-MECH conjunction (ρ_move = 0.5) and for the two Δ_mask simple effects
(ρ = 0.3), mask-disagreement dilution for C-KERN, cluster-mean t-test as the
large-C surrogate for the exact sign-flip (frozen analysis uses the exact
sign-flip, B = 10,000). Planning parameters ALL [STIPULATED], re-estimated at
GATE-0: movable fraction f = 0.20; |d| mix {1: 0.55, 3: 0.20, 4: 0.25}
(σ_item ≈ 1.13); τ_cluster = 0.05 (C-MECH), 0.03 (Δ_mask); ρ_item = 0.30.

Results at the pinned geometry (n = 1,920; C = 96 × m = 20):

| Quantity | Result |
|---|---|
| C-MECH single-contrast licensing power at μ = +0.12 / +0.13 / +0.14 | 0.785 / 0.884 / 0.934 |
| **C-MECH CONJUNCTION power** at μ = +0.13 / **+0.14** / +0.15 (both contrasts) | 0.767 / **0.876** / 0.940 |
| **C-MECH 80%-powered effect (conjunction)** | **μ* ≈ +0.135** on each contrast (single-contrast 80% at ≈ +0.121) |
| C-MECH TOST(±0.08) power at true 0 | **0.822** (m=16/n=1536 gives 0.719 — why m=20 is pinned) |
| C-MECH licensing type-I at 0 / TOST-fires-at-floor | 0.0000 / 0.008 |
| **C-KERN licensing power** at Δ_mask = +0.06 (all-items) | **0.808** (0.828 at ρ_item = 0.25) → 80%-powered effect ≈ **+0.06** |
| C-KERN TOST(±0.04) power at true 0 | **0.968** (0.989 at ρ_item = 0.25) |
| Harm-test type-I at 0 (both families) | ≈ 0.05 (one-sided 95% UCB) |
| Inventory-collapse sensitivity C = 54 × m = 36 (n = 1944) | TOST 0.829; conjunction at +0.13/+0.14 = 0.753/0.881; C-KERN TOST 0.957, licensing at +0.06 = 0.811 |
| Pessimistic heterogeneity τ = 0.10 (C = 96×20) | TOST 0.776; conjunction at +0.14 = 0.856 (disclosed shortfall; G-P re-sim gates it) |

Superiority and equivalence are powered separately, as required; the
equivalence targets are the binding constraint on N — this is exactly why the
δ pins of §7 are what they are. The F1-K anchor is respected: n here (1,920)
sits above the F1-K n = 1,573 at a comparable cluster count, on a
higher-variance (λ-amplified) endpoint, with the cluster-count limit honoured
by gating C, not assuming it.

**Freeze blockers from this section:** the inventory gate (G-I) and the GATE-0
re-simulation (G-P): re-run the SAME pinned simulation at the REALIZED
geometry (realized C, realized unequal m_c, pilot-estimated f, |d| mix, τ,
abstention transitions, realized ρ_item) — every primary licensing rule and
every TOST must show power ≥ 0.75, else STOP and re-freeze with maintainer
sign-off. Pilot estimates feed nuisance parameters ONLY; λ, δ_floor, δ_eq,
margins, and trees are pinned by THIS document and do not move post-pilot.

---

## 9. Cost (pinned projections, caps, and the measured-ceiling rule)

**PROPOSED-PREREG-ROW-S3-11 (budget pin).** [EXTRAPOLATION — planning
forecast, premise of nothing; the binding number is the GATE-0(e) measured
$/paired-item, which freezes the powered-phase ceiling.]

- Decode volume (PRECERT-pass path): 7 confirmatory arms × 1,920 = 13,440
  paired decodes + D^policy 720 + pilot ≈ 500 + reproducibility gate 140 ≈
  **14.8k item-decodes** (×2 passes each). PRECERT-fail path: 4 × 1,920 + 720
  + 500 + 140 ≈ 9.0k.
- **Modal (GPU):** llama.cpp F16 7B single-stream ≈ 35–45 tok/s gen;
  ≈ 3.1M output + ≈ 32M prefill tokens → ≈ 25–35 A10G-hours, parallelised
  across containers (per-item single-stream preserves determinism) →
  **projected $40–80; hard cap $150**.
- **LLM API (Claude-family seats only: sense-fit veto, distractor-plausibility
  veto, audit spot-legs):** ≈ 4–8k Haiku + ≤1k Sonnet calls → **projected
  $25–75; hard cap $150**. N-store typed-layer authoring rides the codex
  subscription lane ($0 marginal).
- **Worst-case ceiling: $300 all-in** — above the Tier-1 cap (80), inside
  Tier-2 (400) [MEASURED-as-record: registry/status.json tier_caps_usd];
  tier registration is coordinator/maintainer business (micro-decision M-1).
- **Measured-ceiling rule:** GATE-0(e) measures $/paired-item at bring-up;
  the powered-phase ceiling freezes at 1.25 × (planned decodes × measured
  rate), and if that exceeds $300 the run STOPS pre-spend for a maintainer
  decision. No number from this section is spendable authority; the measured
  number is.

---

## 10. Gates before freeze and spend (all fail-closed)

**PROPOSED-CRIT-S3-GATE-0 (final).** Order: G-A/G-B/G-C/G-I/G-X offline or
cheap first; the freeze CONSUMES their outputs (the real-model pilot precedes
prereg-freeze — mocks calibrate plumbing, not semantics [MEASURED-as-record:
programme memory/largekern]).

- **G-A (bring-up, tiny real model):** mask machinery end-to-end on the pinned
  host; dead-end rate = 0 across pilot decodes; UNKNOWN admissible in every
  masked arm on every pilot item (100%); measured per-item mask/grammar
  overhead reported (feasibility STOP if answer-pass overhead > 5× the
  unconstrained answer pass).
- **G-B (non-degeneracy):** §4.2 certification under BOTH masks; survivors
  feed G-I.
- **G-I (inventory gate):** n = 1,920 certified items, C ∈ [54, 96], every
  cluster ≥ 12, AFTER pilot quarantine — else STOP (grow inventory or
  maintainer re-freeze at re-simulated geometry). Calendar never substitutes
  (ratified Q4).
- **G-X (offline artifact gates):** PRECERT-S3-1; KILL-2 Stage-1; the §3.2
  opponent-expressivity certification; the mask-table sha freeze.
- **G-D (pilot, 50 quarantined items, all arms + 50-item T-B probe):**
  behaviour gates — per-arm answer rate ≥ 0.50; T-arm raw accuracy ≤ 0.90
  (ceiling guard) and T-arm wrong-rate ≥ 0.05 (exposure/futility floor: if the
  target error class is absent the mechanism cannot show value → STOP, futility,
  before powered spend); sane abstention distributions in ALL arms;
  P-consistent exposure rate measured (§7 descope rule).
- **G-E (cost):** measured $/paired-item; powered ceiling frozen per §9.
- **G-P (power re-simulation):** §8 rule, ≥ 0.75 everywhere, else STOP.
- **G-R (reproducibility):** 20 pilot items × all arms re-decoded: 100%
  token-identical or INSTRUMENT flag and fix-before-freeze.

Failure of any gate = fix or stop; no powered spend. PRECERT failure alone
descopes C-KERN without stopping C-MECH (§7).

---

## 11. Determinism, seeds, pins; coverage rider

**PROPOSED-PREREG-ROW-S3-12 (determinism pin).** Master seed **20260724**.
Derived sub-seeds (pinned verbatim in the frozen record): item-template
sampling 20260724100; pilot draw 20260724200; D^policy subset 20260724300;
derangements 20260724001/002/003; sign-flip MC 20260724400 (B = 10,000,
add-one); cluster bootstrap 20260724500 (B = 10,000). Decode: greedy, seeds
moot but llama.cpp seed pinned 20260724 anyway. The freeze manifest pins
sha256 for: OEWN archive; D* slice artifact; both store record sets; engine
build; compiler; per-item mask table; item file + gold file; prompt/renderer
templates (per arm); GGUF weights + HF revision; llama.cpp commit + build
flags; extraction/scoring script; analysis script; the planning sim. Verdict
generation is the pure-function pipeline on the pinned analysis script;
anything off-script is quarantined exploratory.

**Coverage rider (binding on every readout):** claims are indexed to the
frozen OEWN-slice item universe over the ≤108-concept instance; kernel
coverage 0.3542 at molecules-v0 on ONE pinned corpus [MEASURED: m0b] and
α_point 0.24 (Wilson-95 [0.1150, 0.4343]) on the WordNet-10k draw [MEASURED:
v9 §7] bound all generalisation; a single-host result licenses that host only
— any cross-host, cross-corpus, or "natural coverage" narration is
[EXTRAPOLATION] and prohibited as a premise. A C-MECH PASS without the
cross-vendor audit is MEASURED-UNAUDITED (PASS-pending-audit) until the Codex
audit lands.

---

## 12. Residual maintainer micro-decisions (small, named, non-blocking to review)

- **M-1 budget/tier:** ratify the $300 worst-case ceiling and its tier
  registration (recommendation: Tier-2-class registration or an explicit
  maintainer envelope; the measured-ceiling rule of §9 governs actual spend).
- **M-2 authoring parity number:** ratify 12 agentic-hours-equivalent ±25% per
  store for the two world-layer/typed extensions (§3.2). The parity PRINCIPLE
  is pinned; the hour figure is the ratifiable knob.
- **M-3 host fallback policy:** confirm the pre-powered-run-only swap to
  Llama-3.1-8B-Instruct on named bring-up failure (§2).
- **M-4 dual-role disclosure:** OEWN-2024 now serves two estate roles —
  plain-v5 sense-annotation source and this experiment's domain/gold source.
  Both uses are item-blind-by-construction and disclosed; confirm comfort or
  direct a different external source (which would re-open §4.1 only).

---

## 13. Label index (for the experiment-designer freeze)

- ROW-S3-01 endpoint+margins: KOT-HON/1 S_3, λ=3 pinned pre-pilot; F1-K
  licensing convention; ordered trees; δ_eq < δ_floor. — §6, §7
- ROW-S3-02 arms: M_K/X_KN/X_NK/M_NN/T/G/B + D^policy; T_N/M0 excluded. — §5
- ROW-S3-03 F0 accounting: unchanged from scoping §4.2. — §5
- ROW-S3-04 power: pinned sim, geometry n=1920/C∈[54,96]/≥12, G-P re-sim ≥0.75. — §8
- ROW-S3-05 non-degeneracy: thresholds pinned; both masks; common set. — §4.2
- ROW-S3-06 TOST margins: ±0.08 (C-MECH), ±0.04 (C-KERN), each < its floor. — §7
- ROW-S3-07 opponent: PV5T, matched expressivity, byte-identical machinery,
  parity budget, expressivity certification. — §3.2
- ROW-S3-08 matched-arms protocol: incl. two-pass, extraction rules. — §5
- ROW-S3-09 host pin: Qwen2.5-7B-Instruct/llama.cpp; fallback policy. — §2
- ROW-S3-10 item source: OEWN D* slice, T-A form, gold independence, cluster
  key. — §4.1
- ROW-S3-11 budget: projections, caps, measured-ceiling rule. — §9
- ROW-S3-12 determinism: seeds + sha manifest. — §11
- CRIT-S3-PRECERT-1: ρ_item ≥ 0.25 ∧ ρ_opt ≥ 0.05 ∧ ≥⌈C/2⌉ clusters. — §7
- CRIT-S3-KILL-1 / KILL-3: ordered three-outcome trees with pinned numbers. — §7
- CRIT-S3-KILL-2: two-stage derangement gates, pinned thresholds/seeds. — §7
- CRIT-S3-GATE-0: G-A/B/I/X/D/E/P/R, all fail-closed, pre-freeze. — §10

---

## 14. MANDATORY SELF-CHECK (run before hand-off)

1. **Every open scoping value pinned?** PASS — host (Qwen2.5-7B-Instruct +
   stack + fallback, §2); λ = 3 with harm-ratio justification (§6); δ_floor
   +0.10/+0.05 and δ_eq ±0.08/±0.04 with δ_eq < δ_floor (§7); superiority
   margin semantics = F1-K convention restated (§6); N = 1,920 with geometry
   gate (§4.3, §8); PRECERT threshold ρ_item ≥ 0.25 ∧ ρ_opt ≥ 0.05 ∧ ⌈C/2⌉
   clusters (§7); opponent-expressivity certification pinned as a fail-closed
   offline gate (§3.2); item family, domain, gold, cluster key, option
   geometry pinned (§4); D^policy seeds/subset pinned (§7); budget caps and
   measured-ceiling rule pinned (§9); seeds/pins manifest pinned (§11).
2. **Crossed 2×2 estimand isolates the mask channel?** PASS — Δ_mask averages
   two simple effects that each hold context text byte-fixed and swap only the
   compiled mask; context main effect cancels by construction; interaction
   co-reported, package contrast demoted to secondary package language (§1).
3. **Disjoint decision regions?** PASS — δ_eq < δ_floor in both families plus
   fixed evaluation order; simulation check: TOST fires at true μ = δ_floor
   with p ≈ 0.008 (§7, §8).
4. **KOT-HON/1 fully applied + store-independent gold?** PASS — λ pinned
   pre-outcome with justification; S_2/S_5; full co-report vector;
   answer-rate co-floor 0.50 with INSTRUMENT-DEGENERATE consequence;
   risk–coverage curves; abstention-in-denominator; silent-empty = WRONG;
   gold = OEWN assertions extracted deterministically, never from either
   store's closure, veto-only adjudication (§4.1, §6).
5. **Power simulated at the real cluster count?** PASS — executed sim at
   96×20 AND the 54-cluster inventory-collapse case AND τ = 0.10 pessimism;
   superiority and equivalence powered separately; conjunction simulated
   jointly; C-KERN dilution modelled; 80%-powered effects reported
   (+0.135 conjunction / +0.06 Δ_mask); G-P re-simulation gate at realized
   geometry (§8). The F1-K C=96/n=1573/μ*=+4.09 lesson is cited and honoured.
6. **Load-bearing claims tagged?** PASS — PREMISE lines tagged MEASURED /
   LIT-BACKED / MEASURED-as-record with refs; design choices [STIPULATED];
   the two forecasts (§9 cost, §7 C-KERN modal expectation) are
   [EXTRAPOLATION], neither a premise; no MEASURED number quoted outside its
   envelope (m0b restated with corpus index; knull-v2 as precedent only).
7. **No ASM ids minted; no handle/account strings; nothing committed/run?**
   PASS — labels are PROPOSED-PREREG-ROW-S3-01..12 and PROPOSED-CRIT-S3-*;
   grep for at-sign tokens returns zero; this document and the sim script are
   working-tree artifacts for coordinator review and commit; no registry
   write, no freeze, no spend ($0 simulation on this box only).
