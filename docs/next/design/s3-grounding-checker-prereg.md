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
> (sha256 `1d8645e3c554b1c4b73b33ad62e5aa3d69974e7f22da93ab09e032cc30a1dea9`, Rev2),
> the executed planning power simulation (seed 20260724, $0, this box).
>
> **This is Revision 2.** The GPT-5.6 cross-vendor review of Rev1 returned
> REVISE (verdict: `poc/gpt56-review/s3-prereg-review/last-message.json`) —
> estimand structure sound; two flagged items (the δ_floor derivation error and
> the static-GBNF claim boundary) plus seven blocking items, all dispositioned
> in §15 and applied in place. Headline Rev2 changes: the claim is NARROWED
> everywhere to the answer-span allowlist instantiation; δ_floor(C-MECH) is
> re-derived to +0.09 and the Rev1 "smaller floors are not honestly powerable"
> line is RETRACTED as a tagging error (§15); the power sim now implements the
> FROZEN sign-flip + cluster-bootstrap procedures with every published table
> row reproducible from the committed script at exactly n = 1,920; the
> inferential population, cluster weighting, and sign-symmetry basis are
> pinned; PV5T gains a full audit-artifact block; the pilot gains
> within-cluster replication; the KOT-HON risk–coverage ranking score and the
> reasoned-abstention rule are pinned; a G-arm headroom gate and the G-EQ
> compiler-equivalence gate are added; the author/judge family quad is
> completed with store-blind screens. Next consumer: the delta-check
> re-review, then the experiment-designer pipeline.

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

- **C-MECH (mechanism, NARROWED — Rev2):** on the frozen covered item
  universe, a **per-item, store-derived closed-world answer ALLOWLIST enforced
  as a hard mask at the sampler during the answer pass** adds KOT-HON/1
  utility beyond the same facts as prompt text AND beyond format-only
  constraint. Confirmatory contrast pair: Δ(M_K − T) and Δ(M_K − G);
  licensing is the CONJUNCTION (both fire). A PASS supports exactly: "a
  per-item store-derived closed-world answer allowlist improves fixed-slot
  answer selection" — NOT a general dynamic grounding-checker claim (no
  dynamic checking of model-emitted subjects, relations, or arbitrary
  assertions is tested). This boundary is carried in EVERY headline and
  readout; the static-compile/dynamic-hook equivalence is a MECHANICAL GATE
  (G-EQ, §10), never an assertion.
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
from scoping §1.4]. Two Rev2 scope clauses, adopted from the review's
passing-items note: (i) eligibility conditions on gold being admissible under
BOTH stores, so every claim is restricted to the **common-covered slice** of
the two stores; (ii) items where a store's mask would EXCLUDE gold (mask
false negatives) are excluded pre-randomisation — this design therefore
**cannot observe mask-false-negative harm**; the count and per-store split of
such exclusions are reported as a store-quality descriptive (§4.2), and no
readout may claim mask harmlessness beyond the certified slice.

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
  instruction-following floor). STIPULATED (pin): Qwen2.5-7B-Instruct, because (i) per-request GBNF grammars + logits access are first-class in llama.cpp for this model with no thinking-mode toggle confound; (ii) strong small-model instruction compliance protects the T/B extraction legs; (iii) FAMILY-ROLE ACCOUNTING (Rev2 — the full quad, not a triad): host `alibaba`; N-store author `openai`; KERNEL world-layer author `anthropic` (the explicator role runs on the Claude family — pinned, not left implicit); judge/screen seats `anthropic`. The host and the two store authors are pairwise disjoint; the residual shared edge (kernel-author ↔ screens, both anthropic) is cut by the STORE-BLINDNESS rule of §3.1 — every LLM screen sees item + OEWN materials only, never store records, store identity, or arm labels — and final scoring is deterministic; a third-family screen seat (e.g. a pinned GLM-family form) is the named restoration path, per the plain-v5 §4 disclosed-degradation pattern; (iv) permissive licence and a Q8_0 fallback of the SAME weights if F16 throughput busts the cost ceiling (quantisation swap = ops amendment, logged pre-powered-run). Proposed for registration at the landing commit.
- **Pinned fallback host:** Llama-3.1-8B-Instruct, switchable ONLY on a named
  bring-up failure (grammar hook defect, chat-template defect, GATE-0(d)
  behaviour gate failure), before any powered decode, logged as an ops
  amendment; a post-powered-run switch is prohibited.
- **Mechanism implementation (insertion point 1, per the scoping; Rev2
  boundary):** because the item format fixes (s, r) before decode (§4), each
  arm×item admissibility mask compiles OFFLINE to a per-item static GBNF
  grammar enforced at the sampler during the answer pass. It IS a real hard
  mask at the logits seam, and with (s, r) fixed the static grammar over the
  precomputed admissible set has the same intended token language as a
  dynamic hook computing the same set at span entry — but that equivalence is
  NOT assumed: gate **G-EQ** (§10) mechanically verifies, per item×arm,
  prefix-by-prefix, that the compiled automaton's admissible-next-token sets
  equal those of a reference incremental admissibility evaluator over the
  same mask table. What this experiment tests is precomputed answer-span
  allowlisting; dynamic checking of model-emitted subjects/relations/free
  assertions is OUT OF SCOPE and stated so in every readout [STIPULATED
  implementation choice; the estimand is the narrowed §1 claim].
- **Confidence logging (for the §6 risk–coverage curve):** the answer pass
  logs per-token logprobs; the pinned ranking score is the length-normalised
  sum of the emitted answer's token logprobs under the arm's own decode.
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

**Author family + seat blindness (Rev2 — blocking item 7):** the kernel
world-layer author is the explicator role on the **Claude (anthropic)
family** — pinned in the freeze manifest with the exact dated model id. Since
the item screens are also anthropic, EVERY LLM screen seat (sense-fit veto,
distractor-plausibility veto, audit spot-legs) is bound to a STORE-BLIND
envelope: prompt contains the item surface and the pinned OEWN renderings
only; a blinding grep (store record markers, `kot-axiom`, `pv5t`, store file
paths, arm labels) must be zero-hit on every screen prompt and output,
fail-closed; all seats ledgered under the estate's seat discipline. Screens
therefore cannot favour either store's mask cells; the residual same-family
edge is disclosed in every readout (§2(iii)).

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

**PV5T audit-artifact block (Rev2 — blocking item 4; the plain-v5 contract
governs dictionary definitions, so the typed layer gets its OWN pinned
artifacts, all committed BEFORE the authoring session and all freeze
blockers under gate PV5T-AUDIT, §10 G-X):**

1. **Typed schema:** `kot-pv5t/1`, a pinned record grammar for the typed
   layer (entities, the §4.1 relations, and each constraint family), with a
   fail-closed lint (schema conformance, closed vocabulary over the D* slice,
   no free text in typed records).
2. **Blind authoring protocol:** pinned prompt-template bytes (placeholders
   only), pinned per-entity input = the SAME deterministic D*-slice rendering
   the kernel-side author receives (item-blind by the §4.1 temporal argument),
   pinned authoring ORDER (sorted entity id), the plain-v5 §3 isolation
   envelope and blinding grep, full transcript sha-pinned. The author never
   sees kernel records, items, or this document.
3. **Construct mapping table:** a committed one-to-one table kernel construct
   ↔ PV5T construct for every relation and axiom family in use on the slice;
   the expressivity certification checks against THIS table, not against
   prose.
4. **Realized closure-conformance tests:** a pinned golden-test suite run on
   the AUTHORED PV5T records (not merely the engine sha): closure
   well-formedness, transitivity spot-checks against hand-computed cases,
   and a per-relation derivability census over D* compared side-by-side with
   the kernel store's census (large unexplained census gaps are a finding,
   disclosed and bounded before PRECERT).
5. **Source-quality gates:** every typed PV5T fact must be traceable to a D*
   assertion (deterministic provenance check, fail-closed); facts beyond the
   slice are lint failures; the same rule binds the kernel stratum-4 records.
6. **Auditable parity accounting:** both authoring sessions log wall-clock,
   call counts, and token counts; transcripts sha-pinned; the ±25% parity
   check (M-2 hour figure) is computed FROM THE LOGS by a pinned script, not
   attested.

### 3.3 Compile

`A_store(item) = { o ∈ options(item) : closure_store ⊨ assertion(item, o) } ∪ {UNKNOWN}`
computed offline by the pinned engine per store per item; compiled to the
answer-pass GBNF. UNKNOWN (the fail-closed abstention production) is admissible
in EVERY masked arm on EVERY item, verified mechanically at compile time
(ROW-S3-08). Completability holds by construction (options are complete
strings). Mask-build determinism: sorted enumeration order pinned; the full
per-item mask table (item × arm × admissible set) is a sha-pinned frozen
artifact, and PRECERT/KILL-2 Stage-1 read it, never recompute ad hoc. Gate
G-EQ (§10) verifies the compiled grammars against this table prefix-by-prefix
via the reference incremental evaluator before any decode.

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

**Inferential population, estimand weighting, and randomization basis (Rev2 —
blocking item 2).** Under greedy decoding the frozen 1,920-item universe
yields Δ EXACTLY; the descriptive finite-universe difference is therefore
reported as a plain number with no test. The CONFIRMATORY inference targets a
**superpopulation**: the item-generating process defined by the pinned
template family over the covered D* slice, with concepts as the exchangeable
units — the frozen universe is modelled as one realized draw of per-concept
item sets from that process. STIPULATED (pin, proposed for registration at
the landing commit): under H0 the cluster-level paired-difference
distribution is symmetric about zero (cluster **sign-symmetry**); the
sign-flip test is exact CONDITIONAL on that assumption and is MC-approximated
at B = 10,000 — the word "exact" is used nowhere without this conditioning.
**Estimand weighting:** the confirmatory estimand is the **EQUAL-CLUSTER
mean** (unweighted mean of per-cluster mean paired differences) — the
statistic the sign-flip permutes and the bootstrap resamples; the
item-weighted grand mean is co-reported descriptively (the two differ under
unequal m_c, and the observed-floor comparison is applied to the
equal-cluster estimate only). Scope: licensed conclusions read "on items of
this family over the covered slice", never wider.

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

Exclusion reporting (Rev2): the counts of candidate items excluded at (a)
because gold is NOT admissible under the K-mask, under the N-mask, or under
both are reported per store as a store-quality/coverage descriptive — these
are exactly the mask-false-negative cases the confirmatory design cannot
observe (§1 scope clause ii).

### 4.3 Geometry (the f1k lesson, applied)

**Pinned N:** EXACTLY **n = 1,920** certified confirmatory items over
**C ∈ [54, 96]** realized clusters, EVERY cluster ≥ 12 items, realized C and
all per-cluster counts frozen pre-decode. Planning layouts (both n = 1,920
exactly): 96×20 and the inventory-collapse layout 24×35 + 30×36 — both
simulated and both survive (§8). **Pilot (Rev2 — within-cluster replication
for τ estimation, blocking item 5): 120 items = 24 clusters × 5 items**,
clusters and items drawn by seeded random, QUARANTINED — pilot items never
enter the confirmatory set (greedy decoding makes pilot outcomes
deterministic re-runs, so exclusion is the only clean wash). The 24×5 shape
gives a real within/between variance decomposition for the G-P τ estimate;
additionally G-P uses the CONSERVATIVE rule τ_used = max(τ̂_pilot,
τ_planning) per family (§10 G-P), so a noisy pilot τ̂ can only tighten,
never loosen, the power claim. Candidate pool required ≈ 3,100–3,600
template-generated items pre-certification (1,920 + 120 pilot + 50 T-B probe
+ attrition); the INVENTORY GATE (§10 G-I) is a freeze blocker, not a
footnote.

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
**Abstention surface (Rev2):** every arm is instructed, and every masked
arm's grammar admits, both the bare form `UNKNOWN` and the reason-coded form
`UNKNOWN: <code>` with `<code>` from the pinned closed enum
{`NOT-DERIVABLE`, `AMBIGUOUS`, `INSUFFICIENT`}; classification is
deterministic — a valid code ⇒ REASONED abstention, bare or invalid-code
`UNKNOWN` ⇒ REASONLESS abstention (still ABSTAIN-class for scoring, flagged
in the co-report per KOT-HON/1 §1.1).
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
  reasonless split per the ROW-S3-08 deterministic rule); wrong-rate W/N; raw
  recall r; the full risk–coverage curve. **Risk–coverage operationalisation
  (Rev2):** answered items are ranked by the pinned confidence score — the
  length-normalised sum of the emitted answer's token logprobs under the
  arm's own decode (§2) — and the curve traces precision-on-answered against
  coverage as the answer set shrinks along that ranking; descriptive, never
  licensing-bearing.
- **Degenerate-abstention guard:** per-arm answer-rate co-floor **a ≥ 0.50**
  on the confirmatory set; a confirmatory arm breaching it renders every
  contrast touching that arm INSTRUMENT-DEGENERATE (no PASS, no equivalence,
  maintainer escalation) — the score is never gamed by abstention.
- **Margin semantics (the registered F1-K convention):** a contrast FIRES iff
  the cluster sign-flip test against zero (exact conditional on the §4.1
  sign-symmetry assumption; MC-approximated at B = 10,000, add-one corrected,
  two-sided) gives p < 0.05 AND the observed equal-cluster Δ meets the
  registered floor. Disclosed properties: an effect exactly at the floor
  fires ~50% PER CONTRAST — and the C-MECH CONJUNCTION at the floor fires
  only ~26% (§8); TOST/harm use the cluster percentile bootstrap
  (B = 10,000) on the same equal-cluster statistic.
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
| C-MECH: Δ(M_K−T), Δ(M_K−G) | **+0.09** S_3 points | **±0.08** | δ_eq < δ_floor ✓ |
| C-KERN: Δ_mask (all-items scale) | **+0.05** | **±0.04** | δ_eq < δ_floor ✓ |

STIPULATED (pin, Rev2 re-derivation — the Rev1 derivation is RETRACTED, §15):
the honest structure is two separate pins. (1) **δ_eq(C-MECH) = ±0.08** is
the smallest equivalence margin the mandatory TOST supports at ≥ 0.80 power
at n = 1,920 under the planning parameters (simulated: 0.846 at 96×20, 0.830
at the 54-cluster layout, §8) — THIS is the quantity the power arithmetic
constrains. (2) **δ_floor(C-MECH) = +0.09 = δ_eq + 0.01** (one reporting-grid
step, preserving region disjointness) is a MINIMUM-IMPORTANT-EFFECT
JUDGMENT, not a mathematical consequence: at λ = 3 it equals converting
2.25% of all items wrong→correct at zero abstention cost (or 9%
miss→correct). Rev1's claim that "smaller floors are not honestly powerable"
was FALSE (it transferred the TOST constraint on δ_eq onto the floor) and
was a load-bearing tagging error; retracted and recorded in §15. Realism
guard: because the M-grammar is a subset of the G-grammar under greedy
decoding, M can beat G only on items where G emits a mask-excluded wrong
option — the powered effect therefore REQUIRES a sufficient G-arm
mask-addressable error rate, which is now gated pre-spend (G-D headroom
floor, §10) instead of assumed. δ_floor(C-KERN) = +0.05 on the ρ-diluted
all-items scale ≈ a per-disagreement-item effect of **+0.167 at the
planning ρ_item = 0.30 and +0.20 at the PRECERT floor ρ_item = 0.25**
(arithmetic corrected per the review) — co-reported undiluted so the
dilution is never hidden. Proposed for registration at the landing commit.

**Evaluation order (both trees, fixed):** superiority → harm → equivalence;
first licensed outcome taken. Logical disjointness: a percentile-bootstrap
90% CI inside (−δ_eq, +δ_eq) implies the observed equal-cluster Δ < δ_eq <
δ_floor, so no single result can satisfy both the superiority and the
equivalence criteria; the ordered rule additionally guarantees a unique
classification at every boundary. Simulated mis-classification rate: at true
μ = δ_floor, TOST concludes equivalence in ~2.0–2.5% of draws (§8) —
disclosed, not hidden behind the word "disjoint".

**PROPOSED-CRIT-S3-KILL-1 (C-MECH, final):**
- **PASS:** Δ(M_K−T) fires AND Δ(M_K−G) fires (each: sign-flip p < 0.05 AND
  observed equal-cluster Δ ≥ +0.09). Scope: this host, this item universe,
  the NARROWED §1 claim, the §11 coverage rider.
- **HARM:** one-sided 95% UCB (cluster percentile bootstrap) of Δ(M_K−T) < 0
  → the "kernel's home is the output/logits seam" claim FAILS its pricing
  here.
- **EQUIVALENCE:** TOST on Δ(M_K−T): 90% cluster-bootstrap CI ⊂
  (−0.08, +0.08) → the facts, not the mechanism, carry the value (licensed
  negative; equal prominence).
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
- disagreeing items span ≥ ⌈C/2⌉ realized clusters (coarse screen only);
- direction split (K-only-admits / N-only-admits / both-differ) reported.
**Layout rule (Rev2 — blocking item 3):** these floors do NOT by themselves
guarantee the §8 power (disagreements may concentrate); the guarantee
mechanism is G-P — the C-KERN power re-simulation MUST consume the FROZEN
realized item×cluster disagreement table (the sim's `dis_frac_c` input),
never an iid assumption. The concentrated-layout stress row in §8 (all
disagreement confined to half the clusters) is the planning bound for this
effect; the realized-table re-sim is the binding check.
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

**PROPOSED-PREREG-ROW-S3-04 (final form, Rev2 — the Rev1 artifact is
superseded; blocking item 1 applied).** Executed planning simulation:
`docs/next/design/s3-prereg-power-sim.py` (sha
`1d8645e3c554b1c4b73b33ad62e5aa3d69974e7f22da93ab09e032cc30a1dea9`), seed
20260724, 2,000 reps/cell, $0, runtime ~44 s on this box. The Rev2 script
implements the FROZEN procedures — MC cluster sign-flip on the equal-cluster
mean (add-one, two-sided; B_TEST = 2,000 planning resolution vs B = 10,000
frozen) and cluster percentile bootstrap for TOST/harm (B_BOOT = 1,000
planning vs 10,000 frozen) — supports arbitrary unequal-m_c layouts (every
scenario sums to EXACTLY n = 1,920; the 54-cluster layout is 24×35 + 30×36,
correcting Rev1's 54×36 = 1,944 contradiction), uses no fixed-df critical
values, accepts a per-cluster disagreement table for C-KERN (`dis_frac_c` —
the G-P input), and executes EVERY published row below in `run()`. Outcome
model: discrete per-item paired utility differences d ∈ {0, ±1, ±3, ±4},
cluster random effect, movability copulas (ρ_move = 0.5 across the C-MECH
contrasts, shared cluster effect; ρ = 0.3 across the Δ_mask simple effects).
Planning parameters ALL [STIPULATED], re-estimated at GATE-0: movable
fraction f = 0.20; |d| mix {1: 0.55, 3: 0.20, 4: 0.25} (σ_item ≈ 1.13);
τ_cluster = 0.05 (C-MECH), 0.03 (Δ_mask); ρ_item = 0.30.

Results (margins: C-MECH +0.09/±0.08; C-KERN +0.05/±0.04; every row printed
by the committed script at the pinned seed):

| Quantity | 96×20 | 54-layout (24×35+30×36) |
|---|---|---|
| C-MECH single-contrast licensing power at μ = +0.11 / +0.115 / +0.12 / +0.13 | 0.781 / 0.833 / 0.893 / 0.938 | 0.796 / 0.820 / 0.876 / 0.935 |
| **C-MECH CONJUNCTION power** at μ = +0.11 / +0.115 / **+0.12** / +0.13 | 0.612 / 0.704 / **0.787** / 0.874 | 0.644 / 0.686 / 0.773 / 0.879 |
| **C-MECH 80%-powered effect (conjunction)** | **μ* ≈ +0.122** | ≈ +0.123 |
| C-MECH at-floor (μ = +0.09) single / conjunction | 0.500 / **0.262** | 0.507 / 0.239 |
| C-MECH TOST(±0.08) power at true 0 | **0.846** | **0.830** |
| C-MECH licensing type-I at 0 / harm type-I at 0 | 0.0005 / 0.049 | 0.0010 / 0.051 |
| TOST concludes equivalence at true μ = δ_floor (mis-classification, §7) | 0.020 | 0.025 |
| Pessimistic τ = 0.10: TOST at 0; conjunction at +0.12 / +0.13 | 0.789; 0.761 / 0.874 | — |

| C-KERN (Δ_mask, all-items scale) | result |
|---|---|
| licensing power at +0.05 / +0.055 / **+0.06**, iid ρ_item = 0.30 (96×20) | 0.491 / 0.666 / **0.832** → 80%-powered ≈ **+0.059** |
| licensing at +0.06, iid ρ_item = 0.25 / 54-layout ρ = 0.30 | 0.831 / 0.823 |
| **CONCENTRATED stress** (all disagreement in 48 of 96 clusters at 0.50): licensing at +0.055 / +0.06; TOST at 0 | 0.662 / **0.807**; 0.972 |
| TOST(±0.04) at true 0: iid ρ = 0.30 / ρ = 0.25 / 54-layout | 0.973 / 0.982 / 0.953 |
| harm type-I at 0 | 0.049–0.057 |

Readings, stated honestly: the at-floor CONJUNCTION power is ~0.26 (the
~50% at-floor convention holds per contrast, NOT for the conjunction —
disclosed in §6); the conjunction is 80%-powered at μ* ≈ +0.122 per
contrast, which at λ = 3 corresponds to ≈ 3.05% of items moving
wrong→correct against EACH null — hence the G-D headroom gate on the G-arm's
mask-addressable error rate (§10), without which the design could be
structurally unable to show the powered effect. The τ = 0.10 TOST shortfall
(0.789) and the concentration cost (0.832 → 0.807 at +0.06) are planning
bounds; both are re-checked by G-P at realized values. Superiority and
equivalence are powered separately, as required. The F1-K anchor is
respected: n = 1,920 sits above the F1-K n = 1,573 at a comparable cluster
count, on a higher-variance (λ-amplified) endpoint, with the cluster-count
limit honoured by gating C, not assuming it.

**Freeze blockers from this section:** the inventory gate (G-I) and the
GATE-0 re-simulation (G-P): re-run the SAME committed script at the REALIZED
geometry — realized C and unequal m_c vector, pilot-estimated f, |d| mix,
and abstention transitions, τ_used = max(τ̂_pilot, τ_planning) per family
(§4.3), and for C-KERN the FROZEN realized item×cluster disagreement table
via `dis_frac_c` (§7) — every primary licensing rule and every TOST must
show power ≥ 0.75, else STOP and re-freeze with maintainer sign-off. Pilot
estimates feed nuisance parameters ONLY; λ, δ_floor, δ_eq, margins, and
trees are pinned by THIS document and do not move post-pilot.

---

## 9. Cost (pinned projections, caps, and the measured-ceiling rule)

**PROPOSED-PREREG-ROW-S3-11 (budget pin).** [EXTRAPOLATION — planning
forecast, premise of nothing; the binding number is the GATE-0(e) measured
$/paired-item, which freezes the powered-phase ceiling.]

- Decode volume (PRECERT-pass path): 7 confirmatory arms × 1,920 = 13,440
  paired decodes + D^policy 720 + pilot (120 items × 7 arms + 50 T-B probe)
  ≈ 890 + reproducibility gate 140 ≈ **15.2k item-decodes** (×2 passes
  each). PRECERT-fail path: 4 × 1,920 + 720 + 890 + 140 ≈ 9.4k.
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
  opponent-expressivity certification **+ the PV5T-AUDIT block (schema lint,
  blind-protocol pins, construct-mapping table, realized closure-conformance
  golden tests + derivability census, source-quality provenance check,
  parity-from-logs)**; the mask-table sha freeze; **G-EQ (Rev2): per
  item×arm, prefix-by-prefix equality of the compiled GBNF automaton's
  admissible-next-token sets against the reference incremental admissibility
  evaluator over the frozen mask table — any mismatch = fix or STOP, $0,
  offline**.
- **G-D (pilot, 120 quarantined items = 24 clusters × 5, all arms + 50-item
  T-B probe):** behaviour gates — per-arm answer rate ≥ 0.50; T-arm raw
  accuracy ≤ 0.90 (ceiling guard); T-arm wrong-rate ≥ 0.05 (exposure/
  futility floor); **G-arm HEADROOM gate (Rev2 — flagged item 1c): the
  G-arm's mask-addressable error rate — the fraction of pilot items where
  G's emitted answer is an option excluded by the K-mask — must be ≥ 0.05,
  else STOP (futility): under greedy decoding M can only beat G on exactly
  those items, so below this floor the design is structurally unable to show
  the powered effect vs G**; sane abstention distributions in ALL arms;
  P-consistent exposure rate measured (§7 descope rule).
- **G-E (cost):** measured $/paired-item; powered ceiling frozen per §9.
- **G-P (power re-simulation):** §8 rule — the SAME committed script at the
  realized geometry (unequal m_c), τ_used = max(τ̂_pilot, τ_planning), and
  the realized disagreement table for C-KERN; ≥ 0.75 everywhere, else STOP.
- **G-R (reproducibility):** 20 pilot items × all arms re-decoded: 100%
  token-identical or INSTRUMENT flag and fix-before-freeze.
- **Screen-blindness enforcement (§3.1):** the store-blindness grep runs on
  every screen prompt/output as part of staging, fail-closed.

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
flags; extraction/scoring script; analysis script; the planning sim (Rev2);
the PV5T audit artifacts (§3.2: schema, prompt template, mapping table,
golden-test suite, provenance-check script, parity script); the
screen-blindness grep pattern list; the reference incremental evaluator used
by G-EQ. Verdict generation is the pure-function pipeline on the pinned
analysis script; anything off-script is quarantined exploratory.

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

## 12. Residual maintainer micro-decisions (Rev2 — load-bearing status per the cross-vendor review)

- **M-1 budget/tier (OPERATIONAL only, per the review):** ratify the $300
  worst-case ceiling and its tier registration (recommendation: Tier-2-class
  registration or an explicit maintainer envelope; the measured-ceiling rule
  of §9 governs actual spend). Not scientifically load-bearing.
- **M-2 authoring parity number (LOAD-BEARING — must be resolved BEFORE
  freeze):** ratify 12 agentic-hours-equivalent ±25% per store for the two
  world-layer/typed extensions (§3.2). The parity PRINCIPLE and the
  from-logs accounting are pinned; the hour figure is the ratifiable knob.
  Opponent fairness — and therefore what a C-KERN outcome MEANS — rests on
  it; the freeze is blocked until the number is ratified.
- **M-3 host fallback policy (CONDITIONALLY load-bearing):** confirm the
  pre-powered-run-only swap to Llama-3.1-8B-Instruct on named bring-up
  failure (§2) — with the Rev2 rider that exercising the fallback CHANGES
  THE HOST ESTIMAND and therefore requires the full pilot/GATE-0/G-P
  sequence to be re-run and a fresh freeze; no gate output carries over.
- **M-4 dual-role disclosure (LOAD-BEARING — must be resolved BEFORE
  freeze):** OEWN-2024 serves two estate roles — plain-v5 sense-annotation
  source and this experiment's domain/gold source. Reuse is defensible ONLY
  if the temporal/item-blind chain is certified (the §4.1 pins: sha-frozen
  archive predating all programme items; D* extraction deterministic and
  sha-frozen before either store's world layer is authored) — ratify that
  certification, or direct a different external source (re-opens §4.1 only).
  This cannot remain an open comfort decision at freeze.

---

## 13. Label index (for the experiment-designer freeze)

- ROW-S3-01 endpoint+margins: KOT-HON/1 S_3, λ=3 pinned pre-pilot; F1-K
  licensing convention on the equal-cluster statistic; ordered trees;
  δ_eq < δ_floor; risk–coverage ranking score; reasoned-abstention rule. —
  §5, §6, §7
- ROW-S3-02 arms: M_K/X_KN/X_NK/M_NN/T/G/B + D^policy; T_N/M0 excluded. — §5
- ROW-S3-03 F0 accounting: unchanged from scoping §4.2. — §5
- ROW-S3-04 power (Rev2): frozen-procedure sim (sign-flip + cluster
  bootstrap), exact-n layouts 96×20 and 24×35+30×36, τ=0.10 + concentrated
  scenarios, realized-layout G-P input; ≥0.75 gate. — §8
- ROW-S3-05 non-degeneracy: thresholds pinned; both masks; common set;
  false-negative exclusion reporting. — §4.2
- ROW-S3-06 TOST margins: ±0.08 (C-MECH), ±0.04 (C-KERN), each < its floor;
  cluster-bootstrap CI procedure. — §7
- ROW-S3-07 opponent: PV5T, matched expressivity, byte-identical machinery,
  parity-from-logs, expressivity certification + PV5T-AUDIT artifact block. —
  §3.2
- ROW-S3-08 matched-arms protocol: two-pass, extraction rules, reason-coded
  abstention surface. — §5
- ROW-S3-09 host pin: Qwen2.5-7B-Instruct/llama.cpp; family QUAD +
  store-blind screens; fallback policy (M-3 rider). — §2, §3.1
- ROW-S3-10 item source: OEWN D* slice, T-A form, gold independence, cluster
  key, inferential population + equal-cluster estimand + sign-symmetry
  basis. — §4.1
- ROW-S3-11 budget: projections, caps, measured-ceiling rule. — §9
- ROW-S3-12 determinism: seeds + sha manifest. — §11
- CRIT-S3-PRECERT-1: ρ_item ≥ 0.25 ∧ ρ_opt ≥ 0.05 ∧ ≥⌈C/2⌉ clusters +
  realized-layout G-P rule. — §7
- CRIT-S3-KILL-1 / KILL-3: ordered three-outcome trees with pinned numbers
  (+0.09/±0.08; +0.05/±0.04). — §7
- CRIT-S3-KILL-2: two-stage derangement gates, pinned thresholds/seeds. — §7
- CRIT-S3-GATE-0: G-A/B/I/X(+G-EQ, PV5T-AUDIT)/D(+G-arm headroom)/E/P/R,
  all fail-closed, pre-freeze. — §10

---

## 14. MANDATORY SELF-CHECK (Rev2 re-run; the Rev1 result is honestly recorded)

Honest record: **Rev1 items 1, 3, and 5 were PASS-as-worded but WRONG in
substance** — item 1 pinned a δ_floor whose stated derivation was false (the
"+0.10 is forced by TOST" reasoning, retracted in §15); item 3's "disjoint by
construction ... p ≈ 0.008" understated the TOST-at-floor rate produced by
the frozen bootstrap procedure (~0.02–0.025) because the Rev1 sim used a t
surrogate; item 5 claimed table rows (C=54, τ=0.10) that the committed
script could not reproduce, and cited n = 1,944 against the pinned
n = 1,920. All three are corrected here, not papered over. Rev2 re-run:

1. **Every open scoping value pinned?** PASS — host + stack + fallback-with-
   re-freeze-rider (§2, §12 M-3); λ = 3 with harm-ratio justification (§6);
   δ_floor +0.09/+0.05 and δ_eq ±0.08/±0.04 with δ_eq < δ_floor and the
   floor honestly labelled a minimum-important-effect judgment (§7);
   N = 1,920 exact in every layout with geometry gate (§4.3, §8); PRECERT
   thresholds + realized-layout G-P rule (§7); opponent-expressivity
   certification + PV5T-AUDIT block (§3.2); item family, domain, gold,
   cluster key, inferential population, estimand weighting pinned (§4);
   D^policy seeds/subset pinned (§7); budget caps and measured-ceiling rule
   pinned (§9); seeds/pins manifest pinned (§11); risk–coverage score and
   reasoned-abstention rule pinned (§5, §6).
2. **Crossed 2×2 estimand isolates the mask channel?** PASS — unchanged
   (review confirmed); interaction co-reported, package contrast demoted (§1).
3. **Decision regions?** PASS with honest disclosure — logical disjointness
   argued from CI-contains-estimate + δ_eq < δ_floor + ordered evaluation;
   the ~2.0–2.5% TOST-at-true-floor mis-classification rate is DISCLOSED
   (§7, §8), not hidden behind "disjoint".
4. **KOT-HON/1 fully applied + store-independent gold?** PASS — Rev1 content
   plus the Rev2 completions: pinned risk–coverage ranking score (§2, §6)
   and the deterministic reasoned/reasonless rule via the reason-coded
   abstention enum (§5).
5. **Power simulated at the real cluster count, reproducibly?** PASS — the
   committed Rev2 script implements the frozen sign-flip + cluster-bootstrap
   procedures, runs EVERY published row (96×20, 24×35+30×36, τ = 0.10,
   ρ_item ∈ {0.30, 0.25}, concentrated layout) at exactly n = 1,920, and
   accepts the realized disagreement table for G-P; 80%-powered effects
   reported (conjunction ≈ +0.122; Δ_mask ≈ +0.059); at-floor conjunction
   power (~0.26) disclosed. The F1-K C=96/n=1573/μ*=+4.09 lesson is cited
   and honoured.
6. **Load-bearing claims tagged?** PASS — PREMISE lines tagged with refs;
   design choices on STIPULATED pin lines proposed for registration; the
   Rev1 load-bearing tagging errors (the false floor-derivation sentence and
   the asserted static/dynamic equivalence) are respectively RETRACTED (§7,
   §15) and converted to the mechanical gate G-EQ (§2, §10); forecasts
   remain [EXTRAPOLATION], premises of nothing.
7. **No ASM ids minted; no handle/account strings; nothing committed/run?**
   PASS — labels remain PROPOSED-PREREG-ROW-S3-01..12 and PROPOSED-CRIT-S3-*;
   grep for at-sign tokens returns zero; this document and the Rev2 sim are
   working-tree artifacts for coordinator review and commit; no registry
   write, no freeze, no spend ($0 simulation on this box only).

---

## 15. Revision 2 — cross-vendor review dispositions

Verdict REVISE (`poc/gpt56-review/s3-prereg-review/last-message.json`); no
finding is rebutted; one is partially rebutted with the rebuttal stated.

| # | Finding (compressed) | Disposition | Where |
|---|---|---|---|
| F-1 | δ_floor = +0.10 not forced; "smaller floors not honestly powerable" FALSE (TOST constrains δ_eq, not the floor); at-floor conjunction ~0.26 not 50%; realism of the required wrong→correct movement unestablished; no G-arm headroom gate | **ADOPTED.** δ_eq re-derived as the TOST-constrained pin (±0.08); δ_floor lowered to +0.09 = δ_eq + one grid step, honestly labelled a minimum-important-effect judgment (2.25% items wrong→correct); the false sentence RETRACTED and recorded as a Rev1 load-bearing tagging error; at-floor conjunction power disclosed in §6/§8; G-arm mask-addressable headroom gate ≥ 0.05 added to G-D; conjunction 80%-powered effect now ≈ +0.122 (≈ 3.05% items wrong→correct per null), stated next to the gate that makes it observable | §6, §7, §8, §10 |
| F-2 | Static per-item GBNF tests only precomputed answer-span allowlisting, not dynamic checking; the static/dynamic equivalence was a load-bearing assertion | **ADOPTED.** Claim NARROWED in the C-MECH statement, scope rule, KILL-1 scope, coverage rider ("answer-span allowlist instantiation"); equivalence converted to the mechanical prefix-by-prefix gate G-EQ against a reference incremental evaluator ($0, offline, fail-closed) | §1, §2, §10, §11 |
| B-1 | Power artifact: missing scenarios, 1,944-vs-1,920 contradiction, no unequal m_c, df=95 hardcoded, t surrogate not the frozen procedure, no layout/answer-rate consumption | **ADOPTED.** Script rewritten: frozen sign-flip + cluster percentile bootstrap implemented; every published row executed by `run()`; all layouts sum to exactly 1,920 (54-cluster layout = 24×35 + 30×36); unequal m_c native; no df constants; `dis_frac_c` consumes the realized disagreement table. Answer-rate floor: PARTIAL REBUTTAL, stated — it is a deterministic validity gate on realized data, not a stochastic component of the licensing rule; its power-relevant channel (abstention transitions) enters through the |d| mix G-P re-estimates from the pilot | §8; s3-prereg-power-sim.py |
| B-2 | Inferential population/weighting/exactness undefined for a finite exhaustively-evaluated universe | **ADOPTED.** Superpopulation target pinned (item-generating process over the covered D* slice, concepts exchangeable); cluster sign-symmetry stipulated as the randomization basis, "exact" used only conditionally; equal-cluster mean pinned as the confirmatory estimand, item-weighted mean descriptive; finite-universe Δ reported as a plain number | §4.1, §6 |
| B-3 | PRECERT floors don't guarantee power under concentration; dilution arithmetic wrong | **ADOPTED.** G-P must consume the FROZEN realized item×cluster disagreement table (iid assumption removed); concentrated-layout stress row added (0.832 → 0.807 at +0.06); arithmetic corrected: +0.05 → +0.167 at ρ = 0.30 / +0.20 at ρ = 0.25; +0.06 powered → +0.24 undiluted at ρ = 0.25 | §7, §8 |
| B-4 | PV5T typed layer not auditable under the plain-v5 contract alone | **ADOPTED.** PV5T-AUDIT block: `kot-pv5t/1` schema + lint; blind authoring prompt/inputs/order pins; kernel↔PV5T construct mapping table; realized closure-conformance golden tests + per-relation derivability census; source-quality provenance gates (both stores); parity computed from logged transcripts by a pinned script; all freeze blockers under G-X | §3.2, §10, §11 |
| B-5 | 50-item ≤1-per-cluster pilot cannot estimate τ | **ADOPTED.** Pilot = 120 items (24 clusters × 5, quarantined) giving a real within/between decomposition, PLUS the conservative rule τ_used = max(τ̂_pilot, τ_planning) | §4.3, §10 |
| B-6 | Risk–coverage score and reasoned/reasonless rule unpinned | **ADOPTED.** Ranking score = length-normalised answer-token logprob sum (logged at decode); abstention surface = bare `UNKNOWN` vs `UNKNOWN: <code>` from a closed enum; classification deterministic | §2, §5, §6 |
| B-7 | Kernel-author family unpinned; screens could overlap a store author | **ADOPTED.** Quad pinned (host alibaba / N-author openai / K-author anthropic / screens anthropic); every screen bound to a store-blind envelope with a fail-closed blinding grep, ledgered; residual same-family edge disclosed in every readout; third-family seat named as restoration path | §2, §3.1, §10 |
| + | Passing-note scope: common-covered-slice restriction + unobservable mask-false-negative harm | **ADOPTED** as binding scope clauses with exclusion-count reporting | §1, §4.2 |
| + | M-1 operational; M-2/M-4 load-bearing pre-freeze; M-3 conditionally (fallback ⇒ full re-run + re-freeze) | **ADOPTED** verbatim into §12 | §12 |
