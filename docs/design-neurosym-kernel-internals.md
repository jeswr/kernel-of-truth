# Design: kernel-powered neurosymbolic internals (flagship line) — nsk1

**Kernel of Truth programme — investigation-line design + DRAFT pre-registration spec.**
Author: Kern (Claude Fable 5, experiment-designer role, `kern/fable-designer-nsk`).
Date: 2026-07-10.
**Status: DRAFT design. NOT frozen. No GPU spent. The run is Tier-2 GPU-gated on
maintainer sign-off (§8).** Registry artifacts this document anchors:
`registry/experiments/nsk1.json` (DRAFT kot-reg/1),
`registry/ideas.jsonl` (`idea-neurosym-kernel-internals` + nine superseding lines),
`registry/assumptions.jsonl` (ASM-0023..ASM-0025).
Binding constraints honoured throughout: `docs/kernel-design-directives.md` (§1
no-semantic-web-legacy, §2 two theses/metric-vector V, §4 forks, §6 stats), Laws 1–3,
X3 cosine ban, run≠audit.

**Maintainer flagship this line serves:** "an actual neurosymbolic architecture where
hidden layers / activation functions are powered by the kernel."

---

## 0. One-paragraph summary

This line consolidates the whole "symbolic inference between layers" family (B1–B6 of
`reports/lit-structured-parsing-and-inner-symbolic.md`, plus the decode-time and latent
relatives) into ONE umbrella idea with staged variants, and designs its first decisive
experiment, `nsk1`: a training-free forward-hook loop on SmolLM2-135M/360M (R1–R2) in
which, mid-forward-pass, the hidden state is patchscope-decoded to text, EXACT-matched
against a closed lexicon (no kernel-space similarity anywhere), handed to the
`kot-axiom/1` engine (the l3a artifact) which resolves the axiom-licensed hop-1 fact of
a 2-hop question, and written back as a kernel-keyed cached steering vector (B2
channel). The decisive comparator is not text-only: it is **the same engine feedback
rendered as text through an external F2-topology loop at matched token budget** — the
experiment isolates exactly one bit: *does putting the kernel's engine inside the
network's forward pass beat handing the identical kernel content to the model from
outside?* A pre-registered Stage-0 back-patch diagnostic (B5) with a rescuable-fraction
floor is the family-level cheap kill that runs first inside the same record.

---

## 1. Consolidation record — the B-family becomes one line with staged variants

`idea-neurosym-kernel-internals` (appended to `registry/ideas.jsonl`) absorbs nine
constituents as staged variants; each constituent gets a superseding line pointing at
the umbrella (last-line-wins; nothing deleted; none of them is killed — they are
sequenced):

| Stage | Variant | Absorbed idea | Role in the line |
|---|---|---|---|
| V0 | back-patch diagnostic | `idea-backpatch-diagnostic` (B5) | Stage-0 of nsk1: the instrument gate + family cheap kill |
| V1 | training-free loop, steering write-back | `idea-inter-layer-loop-trainingfree` (B1) + `idea-kernel-keyed-steering-dict` (B2) + parent `idea-symbolic-inference-between-layers` | Stage-1 of nsk1: the decisive experiment |
| V2 | kernel-gated activation modulation channel | (new option registered under FK-NSK-1) | fallback/second write channel; runs only if V1's cache gate fails or as a later arm |
| V3 | VSA-algebra engine internals | `idea-vsa-engine-internals` (B3) | engine-implementation efficiency; independent of the loop; blocked on X3-safe cleanup |
| V4 | kernel-keyed embedding injection | `idea-concept-toolkens` | input-edge relative of the write channel (frozen kernel-derived toolken embeddings); LATER stage |
| V5 | engine-in-decode | `idea-l3c-engine-in-decode` | decode-time write channel; gated on L3b per the ladder |
| V6 | latent loop with engine | `idea-coconut-engine-loop` (B6) | horizon; gated strictly on V1's result |
| V7 | trained-bridge latent | `idea-calm-hybrid-latent` (+ B4 kinship, which stays a separate idea) | Law-1 trained-bridge cell; POST-F2/scaling-kill gates; LATER stage, out of nsk1 |

- PREMISE: the l3a engine exists, is correct on its covered slice, and refuses
  correctly on controls — covered exact-answer Wilson-LB 0.9955 (gate 0.98), control
  correct-refusal Wilson-LB 0.9911 (gate 0.95), ~5.3 us/query, PASS, cross-vendor
  CONFIRMED [MEASURED: registry/verdicts/l3a.json]. This discharges B1's "L3a engine"
  blocker. Its envelope licenses engine-correctness properties only — NO
  natural-language behaviour and NO claim of usefulness to any model; nsk1 exists to
  measure the latter, not to assume it.
- PREMISE: training-free read/write instruments on mid-network state are established —
  patchscope decoding of hidden states [LIT-BACKED: arXiv:2401.06102 (2024), verified
  in reports/lit-structured-parsing-and-inner-symbolic.md §2.2], function/steering
  vectors with causal effects [LIT-BACKED: arXiv:2310.15213 (2024); arXiv:2306.03341
  (2023), same report], and back-patching rescuing up to 66% of failed general 2-hop
  queries [LIT-BACKED: arXiv:2406.12775 (2024), same report].
- PREMISE: the central programme question — does the kernel make any model more
  correct or efficient at matched budget — is fully unmeasured; there are zero audited
  end-task wins over the kernel-as-text null [MEASURED:
  registry/assessments/oracle-coverage.json null-bound, restated in
  docs/next/feasibility-synthesis.md §2a].
- The COMPOSITION of the established instruments (the loop itself) is EXTRAPOLATION
  and premises nothing; nsk1 is the measurement that resolves it (ASM-0024, ASM-0025
  carry the two instrument-transfer extrapolations, both `load_bearing: false`, each
  with its resolution path inside nsk1).

**Dedup check (2026-07-10):** `registry/ideas.jsonl` has no umbrella id and none of the
constituents carries a `candidate_ref`; `registry/experiments/` contains no record for
any B-family experiment; `docs/` contains no design doc for this line. This design is
new, not a refinement of an existing record.

---

## 2. Claim and hypotheses

**Claim.** For kernel-covered content, a deterministic symbolic engine placed *inside*
the forward pass (read hidden state → exact concept identification → engine → write
model-native state) delivers engine content to the computation more effectively than
the same engine content delivered as input text — because the write lands at the layer
where the computation fails (the back-patching layer-timing evidence), not at the
input where it must survive re-encoding.

**HNSK0 (Stage-0, instrument/family gate).** On kernel-covered 2-hop items that the
text-only host fails, a back-patch sweep (later-layer hidden state moved to an earlier
layer) rescues at least the pre-declared floor fraction: Wilson-LB(rescued/swept) ≥
0.15 at each rung. Below the floor, layer-timing intervention has no headroom on this
slice and the family's expensive variants are deprioritised — the cheap kill.

**HNSK1 (Stage-1, decisive).** At R1 and R2, on the covered stratum, the internal loop
(patchscope-read → exact-match → engine hop-1 → kernel-keyed cached steering
write-back) beats the external F2-topology loop (identical engine hop-1 feedback as
appended text, matched extra-token budget) on paired exact-answer accuracy:
one-sided 95% BCa lower bound of Δ = acc(internal) − acc(external-text) > 0 at BOTH
rungs (IUT conjunction), with the shuffled-kernel specificity co-gate (§4.5) held.

**The honest null (equally publishable).** If the 90% BCa CI of Δ lies within ±0.02
(TOST) at both rungs, the reading is: *at these rungs and this task family, kernel
content helps only as much inside the network as outside* — the internal-loop family
retreats to F2-topology seams (L0/L3), and that is recorded as the line's result.

---

## 3. Forks (every silent choice registered; directives §4)

**FK-NSK-1 — write channel (THE fork this tasking names).**
*(a)* kernel-keyed cached steering vector (B2): per-(model, entity) vector extracted
once, training-free, by contrastive activation arithmetic over the model's OWN
activations on carrier prompts; injection = activation addition at the intervention
layer; addressed by EXACT world-record identity (entity URN / concept hash).
*(b)* kernel-gated activation modulation: multiplicative gating of the intervention
layer's activations by an engine-conditioned mask.
- DECISION: option (a) is PRIMARY for nsk1. Criterion, stated: pick the channel whose
  *causal write effect is already measured in the literature at matched training-free
  cost* — activation addition/steering has measured causal effects (function vectors;
  ITI's TruthfulQA 32.5%→65.1%) [LIT-BACKED: arXiv:2310.15213 (2024); arXiv:2306.03341
  (2023)], while concept-granular multiplicative gating has no established occupant we
  could find (it would stack a novel write mechanism on top of an unmeasured
  composition — two unknowns in one experiment). Option (b) is staged as variant V2,
  and becomes the fallback if (a)'s cache-extraction gate fails.
- The steering-evaluation fragility literature is priced, not ignored: the
  random-direction and no-op-hook controls exist precisely because steering evals are
  documented as fragile [LIT-BACKED: arXiv:2410.17245 (2024), carried via
  reports/lit-structured-parsing-and-inner-symbolic.md §2.2].

**FK-NSK-2 — intervention layer L\*.** Options: fixed mid-network layer; per-model
sweep; Stage-0-derived. Resolved procedurally (no evidence claim — a pre-declared
selection procedure): L\* is selected by a pre-declared MECHANICAL rule on
a disjoint calibration split (10% of covered items, excluded from the final analysis):
L\* = the earliest layer at which (i) patchscope extraction success on the calibration
split ≥ 0.70 and (ii) the Stage-0 rescue heatmap's marginal rescue rate for
target-layer = L is within 90% of its maximum. No post-hoc layer shopping: the rule,
not a person, picks L\*; the chosen L\* is logged before the final campaign
(instrument row), and the final analysis never compares layers.

**FK-NSK-3 — task family.** Options: (a) synthetic world-layer 2-hop composition
(chosen); (b) TinyStories-covered grounding tasks; (c) public multi-hop benchmark
filtered to covered items. DECISION: option (a), stipulated with rationale [STIPULATED: ASM-0023].
2-hop composition is the one shape where the layer-timing
failure mode is measured (B5's literature), hop-1 is engine-resolvable with an axiom
license, and gold labels are structurally independent of the engine accept test.
(b)/(c) import the unrun NL-parse boundary and sub-0.36 corpus-indexed coverage into
the first decisive experiment; they are later variants, not this record.

**FK-NSK-4 — loop cadence.** Options: single intervention at the pre-answer position,
k=1 (chosen — minimal decisive); multi-round re-entry (Coconut-shaped, V6). Resolved
procedurally: k=1. Every additional round adds budget-matching ambiguity against the
external arm; the minimal question needs one write.

**FK-NSK-5 — steering strength α.** Resolved procedurally: swept on the calibration
split over {2, 4, 8}
(vector-norm multiples); pre-declared selection rule: largest α whose calibration
accuracy on UNCOVERED controls degrades < 2pp vs no-op hook. α is then frozen for the
final campaign. (Same discipline as L\*: rule-selected, calibration-only, logged.)

---

## 4. The nsk1 experiment (two stages, one DRAFT kot-reg/1 record)

### 4.1 Hosts, rungs, inputs

- Hosts: SmolLM2-135M (R1), SmolLM2-360M (R2) — open weights, forward hooks. Two
  rungs; any PASS is "a sign", never a slope (P8 discipline).
- Inputs: `data/nsk1-eval` (NEW corpus, pinned digest
  `5c7c4dfe28cf0c2e131fcb232a8a9cd36132e8fcef9f4e0c2557ab1f7a7b53aa`): 140 seeded
  synthetic 3-generation families → 2,240 clean kot-world/1 records (zero planted
  violations) reusing the ALREADY-MINTED kernel concepts (mother-of, father-of, man,
  woman — the same URNs axioms-v0/world-v0 use); 1,000 covered 2-hop items
  ("Who is the mother of the father of X?"; all facts present in-context among
  distractors) + 100 uncovered controls (out-of-scope relation / unknown entity);
  closed exact-match lexicon (unique surface forms).
- **Gold-label independence (the f2b oracle-leakage lesson, designed out):** gold =
  generator graph traversal, computed at corpus build. The engine at run time resolves
  and licenses ONLY hop-1 (the bridge parent); it never sees, produces, or scores the
  2-hop answer in any arm. The feedback (internal or text) therefore never contains
  the gold label, and the accept test (axiom-licensed hop-1 uniqueness) is disjoint
  from the scoring function (exact match against traversal gold).
- Coverage, restated per the standing rule: m0b measured coverage_fraction 0.3542 at
  rung molecules-v0, corpus-indexed on the pinned TinyStories task family, on ONE
  incomplete kernel instance [MEASURED: registry/verdicts/m0b.json; ASM-0001] — that
  number does NOT describe nsk1-eval and extrapolates nowhere. nsk1-eval's covered
  stratum has coverage BY CONSTRUCTION (verified by a run-time harness gate that every
  covered item's hop-1 resolves with a license), which is a design property of a
  synthetic corpus, not a claim about natural text.

### 4.2 Stage 0 — B5 back-patch diagnostic (instrument gate + family cheap kill)

Per rung: run text-only on the 1,000 covered items; take the failure set; on up to 300
failures (pre-declared cap), sweep back-patches over a pinned (source-layer,
target-layer) grid; an item is *rescuable* if any grid cell yields the exact gold
answer. Gate: Wilson-LB(rescuable) ≥ 0.15 at each rung, else the record lands as the
Stage-0 FAIL (family-level kill: no Stage-1 spend). Headroom gate: text-only covered
accuracy must lie in [0.05, 0.85] with ≥500 scored items, else INSTRUMENT-INVALID
(no room to detect anything). Stage-0 also produces the rescue heatmap and patchscope
calibration data that mechanically fix L\* (FK-NSK-2).

### 4.3 Stage 1 — the decisive loop, seven arms per rung

| Arm | What it is |
|---|---|
| internal | hook at L\*: patchscope-decode → EXACT lexicon match (abstain out-of-lexicon; X3: no cosine/kNN anywhere) → engine hop-1 (licensed unique lookup) → cached steering vector keyed by the engine's answer record, h ← h + α·v at L\* |
| external-text | SAME pipeline through the engine, feedback rendered as one text sentence appended to the context, answer regenerated (F2 topology), extra tokens ≤ the matched budget (24); the PRIMARY comparator |
| text-only | no feedback, no hook |
| kernel-as-text | static kernel/world records for the item's family rendered as text at matched extra-token budget, NO engine resolution (Law-2 null: same content, no computation) |
| shuffled | internal with a seed-pinned DERANGEMENT of the entity→vector map (kernel-keying semantics destroyed, plumbing identical) |
| random-dir | internal with a random vector at matched norm |
| noop-hook | hook installed, zero vector (prices the intervention plumbing itself) |

Budget matching: internal's extra cost = patchscope side-decode (≤8 tokens) + hook
overhead; external-text's = feedback sentence tokens (≤24) + regeneration. Both extra
token and FLOP ledgers are logged per arm; the V-vector cost report is a secondary,
never the primary.

Law 1 (interface locality), restated as implemented: NO raw kernel/encoder coordinates
ever enter the model. The steering vectors are the model's OWN activations (contrastive
extraction on carrier prompts, cached once per model+entity); the kernel's role is to
*choose which vector to inject and when* (exact record-keyed addressing, engine
licensing). Trained-bridge variants (B4 kinship, V7/idea-calm-hybrid-latent) and
decode/latent variants (V5/V6) are explicitly OUT of this record.

Refusal-honesty rail: on uncovered controls the mapper must abstain and the loop
no-op; intervention false-fire Wilson-UB ≤ 0.05 is an instrument gate, so "the loop
helps by firing indiscriminately" is excluded by construction.

### 4.4 Endpoints

- PRIMARY (exactly one): paired absolute accuracy delta Δ = acc(internal) −
  acc(external-text) on the covered stratum, per rung; one-sided 95% BCa bootstrap
  (B=2000, seed pinned). ABSOLUTE difference — no ratios, no gap-closure denominators
  (the F2 degenerate-primary lesson) [MEASURED context: registry/verdicts/f2.json FAIL
  fired on a degenerate ratio denominator].
- TOST equivalence margin ±0.02 (90% CI) pre-declared for the null reading.
- Secondaries (one Holm family): internal−text-only; external−text-only (replicates
  the F2 shape at hop-1 granularity); internal−kernel-as-text; internal−shuffled
  (specificity, §4.5); internal−random-dir; cost ledger deltas.
- Instrument gates, each with its own bound: patchscope extraction-failure Wilson-UB ≤
  0.30 (covered, loop arms); mapper abstention on covered ≤ 0.20; steering-cache
  extraction success ≥ 0.90 of entities (calibration); false-fire Wilson-UB ≤ 0.05;
  Stage-0 floor; headroom.

### 4.5 Pre-declared verdict logic (draft; margins final at freeze)

1. INSTRUMENT-INVALID if any instrument gate fails.
2. FAIL (family cheap kill) if Stage-0 Wilson-LB < 0.15 at either rung.
3. KILL-semantics-free co-gate: PASS additionally requires one-sided 95% LB of
   acc(internal) − acc(shuffled) > 0 at both rungs; if the primary clears but this
   does not, the verdict is FAIL-attribution (the write channel works but
   kernel-keying adds nothing — the E9-defl discipline).
4. PASS: primary LB > 0 at both rungs AND (3) holds.
5. NULL-EQUIV: TOST holds at both rungs → equivalence recorded with the same
   prominence as a PASS.
6. Anything else: INCONCLUSIVE (report CIs; no adjective).

### 4.6 Power (on the covered slice, per the designer MUST)

Paired binary design, n = 1,000 covered items per rung. Planning values (mechanism
targets, not predictions): acc(external-text) ≈ 0.45–0.60 (feedback names the bridge
but composition must still happen), detectable Δ = +0.05 absolute. With discordant
pair rate ≈ 0.25–0.35, McNemar-style power at one-sided α=0.05 is ≈ 0.8–0.9 at
n=1,000; the TOST ±0.02 margin at n=1,000 is decidable for accuracies in the headroom
window (this is exactly what the headroom gate enforces). If Stage-0 leaves the
text-only accuracy outside [0.05, 0.85], the record self-declares INSTRUMENT-INVALID
rather than reporting an underpowered comparison.

### 4.7 Extrapolation envelope (verbatim in the record)

Measured range on a PASS: R1–R2 (SmolLM2-135M/360M), ONE synthetic covered 2-hop task
family (nsk1-eval, in-context facts), ONE kernel instance's minted concepts, ONE write
channel (B2 steering, α and L\* rule-selected), k=1 loop cadence. A PASS licenses:
"at these two rungs, on this covered synthetic family, kernel-engine content delivered
by internal steering beat the same content delivered as text at matched budget" — a
sign, no scale language. It does NOT license: natural-corpus claims, NL-parse claims,
any statement at R3+, multi-hop beyond 2, other write channels, training-time claims,
or any "the kernel powers the network" headline. A FAIL/NULL-EQUIV kills or demotes
the training-free internal-write family at these rungs and licenses redirection of the
line's budget to external seams (L0/L3) and later staged variants under their own
gates.

---

## 5. Inputs, harness, mock ($0) — built and green

- Generator: `poc/nsk1/gen_nsk1_corpus.py` (seeded, RNG-pinned, stdlib-only) →
  `data/nsk1-eval/` (digest above; manifest carries counts + the gold-independence
  statement).
- Harness: `poc/nsk1/nsk1_runner.py` — two stages, seven arms, `--mock` mode. Mock
  exercises the REAL kot-axiom engine (all 1,000 hop-1 queries resolve exactly and
  licensed), the REAL exact-match mapper (abstains on all uncovered controls), the
  REAL derangement/keying/budget-ledger/logging schema, and the REAL pinned analysis;
  only the host model is a deterministic stub with clearly-fake accuracy profiles.
  Real mode fail-closes (`ERR_NSK1_GPU_GATED`) — the final campaign belongs to the
  runner role against the frozen record, never to this designer (run≠audit).
- Analysis (pinned): `analysis/nsk1.py` — Wilson gates, paired BCa (bias-corrected,
  jackknife-accelerated), TOST, specificity delta; sha256
  `aba06bbee99dd7b85295cefcaa129acba9dd5a66cb4c2e4baeb03013a63631c0` (re-pinned at
  freeze if it changes; the mock-stage analysis computes single-rung fields — the
  freeze-stage revision computes per-rung fields and the IUT minimum across R1/R2).
- Mock run 2026-07-10: `python3 poc/nsk1/nsk1_runner.py --mock` → 9,000 rows, all
  pinned endpoint fields present and decidable, exit 0 ("MOCK GREEN"). $0 spent.

---

## 6. What this experiment decides for the flagship (the envelope's upside)

The maintainer's flagship needs, before any trained variant is worth building, an
answer to the cheapest form of its core question: *is there any value at all in the
kernel touching the computation from inside rather than from the prompt?* nsk1 is that
question with every established instrument and every programme lesson (oracle
leakage, degenerate denominators, shuffled controls, refusal validity, coverage
honesty) already priced in. A PASS opens V2–V7 in order of cost with a measured
existence proof behind them; a clean NULL-EQUIV/FAIL saves the entire family's Tier-3+
budget and redirects the flagship toward the external-engine topologies that already
have a CONFIRMED artifact (l3a) — either outcome moves the programme.

---

## 7. Skeptic memo (pre-freeze attack — freeze stays BLOCKED until re-run after amendments)

1. **Oracle leakage (the f2b class).** Attack: does any feedback contain the gold?
   No — engine resolves hop-1 only; gold is the hop-2 traversal. Residual risk: for
   items where outer=inner relation chains collide (e.g. mother-of-mother and the
   family generator's naming), the bridge might equal the gold — AUDITED at corpus
   build: generator structure makes bridge (a parent) and gold (a grandparent)
   distinct entities always. VERIFIED in-corpus (1,000/1,000 distinct).
2. **Baseline asymmetry / strawman external arm.** Attack: the external arm could be
   weakened by clumsy feedback phrasing. Mitigation: feedback sentence is the SAME
   deterministic renderer both arms' ledger uses; its phrasing matches the corpus's
   fact-sentence surface grammar exactly; the external arm regenerates with the
   feedback placed adjacent to the question (best-known position). Pre-freeze
   REQUIREMENT: a calibration-split check that external-text > text-only by ≥ 2pp —
   if the external loop does not visibly work, the comparison is vacuous and the
   design must be revisited (this is a freeze-blocker check, not a verdict gate).
3. **Endpoint gameability via abstention.** Attack: internal arm could gain by firing
   only on easy items. Mitigation: paired analysis scores ALL covered items in every
   arm (an unfired loop = baseline behaviour, still scored); abstention is a gate,
   not an exclusion.
4. **Steering-eval fragility (arXiv:2410.17245 class).** Attack: steering "wins" that
   are actually distribution damage. Mitigation: random-dir and noop-hook controls at
   matched norm/plumbing; uncovered-control degradation bound inside FK-NSK-5's α
   rule; specificity co-gate (§4.5.3) makes semantics-free wins un-passable.
5. **Layer/α shopping.** Attack: L\* and α selected to flatter the primary.
   Mitigation: both rule-selected on a disjoint calibration split, logged before the
   final campaign, never varied in the final analysis.
6. **Patchscope readout bias (Faithful-Patchscopes class).** Attack: the read channel
   hallucinating bridges the state does not encode. Priced: extraction-failure gate +
   false-fire gate on uncovered controls; and note the loop's engine step REFUSES
   unlicensed/unknown entities (fail-closed), so a hallucinated read cannot mint
   feedback — it can only no-op or resolve a REAL record's hop-1.
7. **Mock overfit.** The mock's accuracy profile is fake by construction and is
   labelled as such everywhere; nothing in the record's verdict logic references mock
   numbers. Mock proves mechanics only.
8. **Residual honest weakness (stands, disclosed):** the synthetic in-context task
   family is the design's largest external-validity cost (ASM-0023). It is the price
   of gold-independence + coverage-by-construction in the FIRST experiment; natural
   task families are staged behind it.

---

## 8. Compute ask (Tier 2; design-stage estimate, no spend authorised by this doc)

- GPU: 1× A10G (or L4) on Modal, the existing poc/modal harness pattern.
- Stage 0: baseline pass (2 rungs × 1,100 items, short generations) + back-patch
  sweep (≤300 failures × ~40 grid cells × 2 rungs) ≈ 3–5 GPU-h.
- Stage 1: steering-cache extraction (~1,120 entities × 16 carrier prompts, forwards
  only) + 7 arms × 1,100 items × 2 rungs + patchscope side-decodes ≈ 4–6 GPU-h.
- Estimate: **8–12 GPU-h ≈ $12–20 at A10G rates; requested cap $60 / wall-clock 30 h**
  (retries, calibration split, checkpointing).
- Gate: maintainer sign-off (Tier-2 spend) + prereg-freeze of nsk1 (with skeptic
  item 2's calibration check satisfied) + runner-role execution. Nothing runs off
  this document.

---

## 9. Out of scope for nsk1 (recorded so nobody smuggles them in)

Trained bridges of any kind (B4 replication, V7 CALM-hybrid — both carry their own
POST-F2/scaling-kill gates); decode-time integration (V5, gated on L3b);
multi-round latent loops (V6, gated on V1); NL-parse of natural questions
(l3a-parse's territory); any public-benchmark claim; any efficiency-thesis headline
(cost ledgers here are secondaries). Directives §1 restated: nothing in this line
imports RDF/OWL/SHACL semantics — the engine is `kot-axiom/1` native, and the X3
cosine ban holds at every step (all addressing is exact match).
