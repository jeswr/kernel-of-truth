# Design: kernel-powered neurosymbolic internals (flagship line) — nsk1

**Kernel of Truth programme — investigation-line design + DRAFT pre-registration spec.**
Author: Kern (Claude Fable 5, experiment-designer role, `kern/fable-designer-nsk`).
Date: 2026-07-10.
**Status: DRAFT design. NOT frozen. No GPU spent. The run is Tier-2 GPU-gated on
maintainer sign-off (§8).** Registry artifacts this document anchors:
`registry/experiments/nsk1.json` (DRAFT kot-reg/1),
`registry/ideas.jsonl` (`idea-neurosym-kernel-internals` + nine superseding lines),
`registry/assumptions.jsonl` (ASM-0024, ASM-0025, ASM-0027; ASM-0023 superseded).
Binding constraints honoured throughout: `docs/kernel-design-directives.md` (§1
no-semantic-web-legacy, §2 two theses/metric-vector V, §4 forks, §6 stats), Laws 1–3,
X3 cosine ban, run≠audit.

**Revision 2026-07-10 (b) — CLUTRR pivot.** Per the maintainer-adjudicated
eval-necessity decision (`docs/next/eval-necessity-adjudication.md` §2), the PRIMARY
eval surface moves from the self-authored `nsk1-eval` corpus to a covered slice of the
public CLUTRR data (Sinha et al. 2019, arXiv:1908.06177, CC-BY-NC-4.0): clean k=2
up-edge-only chains over {mother, father} with gold in {grandmother, grandfather},
engine world store derived MECHANICALLY from the structured columns (no NL parse).
The custom corpus is demoted to (i) the L\*/α calibration split and (ii) a named
self-authored secondary stratum. The seven arms, the training-free forward-hook loop,
the endpoints, and the verdict logic are UNCHANGED [STIPULATED: ASM-0027, which
supersedes ASM-0023]. New in this revision: §5.1 the mechanical corpus build recipe
(runner role), §5.2 the pre-freeze gates + fallback ladder, the rewritten §4.7
extrapolation envelope (leaderboard/SOTA language stays forbidden).

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
floor is the family-level cheap kill that runs first inside the same record. The
primary eval surface is THIRD-PARTY: the CLUTRR covered slice (§4.1, §5.1), with the
custom `nsk1-eval` corpus demoted to calibration + a named secondary stratum
[STIPULATED: ASM-0027].

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

**HNSK1 (Stage-1, decisive).** At R1 and R2, on the PRIMARY covered stratum — the
CLUTRR covered slice of §4.1/§5.1 — the internal loop (patchscope-read → exact-match →
engine hop-1 → kernel-keyed cached steering write-back) beats the external F2-topology
loop (identical engine hop-1 feedback as appended text, matched extra-token budget) on
paired exact-answer accuracy: one-sided 95% BCa lower bound of Δ = acc(internal) −
acc(external-text) > 0 at BOTH rungs (IUT conjunction), with the shuffled-kernel
specificity co-gate (§4.5) held. The custom `nsk1-eval` covered items are a NAMED
secondary stratum (same contrast, reported alongside, never the primary).

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
a disjoint calibration split drawn from the CUSTOM corpus ONLY (100 `nsk1-eval` covered
items, excluded from the final analysis — the CLUTRR surface is never touched by any
selection rule, §5.3): L\* = the earliest layer at which (i) patchscope extraction
success on the calibration split ≥ 0.70 and (ii) the CUSTOM-stratum Stage-0 rescue
heatmap's (§4.2b) marginal rescue rate for target-layer = L is within 90% of its
maximum. No post-hoc layer shopping: the rule, not a person, picks L\*; the chosen L\*
is logged before the final campaign (instrument row), and the final analysis never
compares layers.

**FK-NSK-3 — task family.** Options: (a) synthetic world-layer 2-hop composition;
(b) TinyStories-covered grounding tasks; (c) public multi-hop benchmark filtered to
covered items. Originally decided (a) under ASM-0023. RE-DECIDED 2026-07-10, before
freeze, on maintainer challenge + external review (the record is DRAFT; re-deciding a
registered fork is exactly what forks are for — `docs/next/eval-necessity-adjudication.md` §2):
DECISION: option (c) restricted to the CLUTRR covered slice is the PRIMARY task family, with option (a) demoted to the calibration split + a named secondary stratum [STIPULATED: ASM-0027].
The original objection to (c) — "imports the unrun NL-parse boundary and sub-0.36
corpus-indexed coverage" — is discharged for CLUTRR specifically: the ENGINE never
parses NL (its world store is derived mechanically from the released `story_edges` +
`genders` columns, §5.1), and coverage is restored by the committed slice filter.
2-hop composition remains the shape (that IS CLUTRR's construction); what changes is
item/gold provenance, which becomes third-party. What (c) imports instead —
patchscope-extraction difficulty on natural-ish story text and public-data
contamination — is priced by the pre-freeze headroom blocker + fallback ladder (§5.2)
and the symmetric within-item arm contrast (§7 item 9).

**FK-NSK-4 — loop cadence.** Options: single intervention at the pre-answer position,
k=1 (chosen — minimal decisive); multi-round re-entry (Coconut-shaped, V6). Resolved
procedurally: k=1. Every additional round adds budget-matching ambiguity against the
external arm; the minimal question needs one write.

**FK-NSK-5 — steering strength α.** Resolved procedurally: swept on the CUSTOM-corpus
calibration split over {2, 4, 8}
(vector-norm multiples); pre-declared selection rule: largest α whose calibration
accuracy on the CUSTOM uncovered controls degrades < 2pp vs no-op hook. α is then
frozen for the final campaign. (Same discipline as L\*: rule-selected,
custom-calibration-only, logged; zero CLUTRR contact before the final campaign except
the discarded §5.2 headroom slice.)

---

## 4. The nsk1 experiment (two stages, one DRAFT kot-reg/1 record)

### 4.1 Hosts, rungs, inputs

- Hosts: SmolLM2-135M (R1), SmolLM2-360M (R2) — open weights, forward hooks. Two
  rungs; any PASS is "a sign", never a slope (P8 discipline).
- **PRIMARY inputs: `data/nsk1-clutrr`** (to be BUILT by the runner per the §5.1
  mechanical recipe, then pinned via `tools/registry/corpus-pin.py`; the record carries
  a PINNED-AT-INPUTS placeholder until then and freeze is blocked on the real digest):
  the CLUTRR covered slice — clean k=2 rows whose proof chain is up-edge-only over
  {mother, father} and whose released gold relation word (`target_text`) ∈
  {grandmother, grandfather} — 1,000 covered items (count gate §5.2) + 100 third-party
  uncovered controls (sibling/spouse/in-law-only chains) + a discarded 100-item
  headroom-calibration slice. Item text (`story`) and question are third-party bytes
  verbatim; the answer space is CLUTRR's closed 24-relation vocabulary (exact match,
  X3-compatible); each item carries a per-item closed name lexicon for the read
  channel. The engine world store is derived MECHANICALLY from the released
  `story_edges` + `genders` columns onto the ALREADY-MINTED kernel concepts (mother-of,
  father-of, man, woman — the same URNs axioms-v0/world-v0 use); the engine never sees
  story text. CC-BY-NC-4.0, eval-side quarantine (§5.1 S11).
- **SECONDARY inputs (demoted, self-authored): `data/nsk1-eval`** (pinned digest
  `5c7c4dfe28cf0c2e131fcb232a8a9cd36132e8fcef9f4e0c2557ab1f7a7b53aa`): 140 seeded
  synthetic 3-generation families → 2,240 clean kot-world/1 records; roles per §5.3 —
  a 100-item calibration split (L\*/α selection, excluded from final analysis), 900
  covered items as the NAMED secondary stratum, 100 uncovered controls (reported with
  the secondary stratum). Entity-answer questions ("Who is the mother of the father of
  X?"), closed exact-match lexicon.
- **Gold-label independence (the f2b oracle-leakage lesson, designed out; now with
  third-party provenance on top):** primary gold = CLUTRR's released `target_text`,
  never recomputed, relabelled, or filtered-by-answer; secondary gold = generator
  graph traversal. The engine at run time resolves and licenses ONLY hop-1 (the bridge
  parent); it never sees, produces, or scores the target relation / 2-hop answer in
  any arm. The rendered feedback names a bridge ENTITY and a hop-1 relation word
  ("mother"/"father"), never the gold word ("grandmother"/"grandfather" — token-exact
  distinctness asserted at build, §5.1 S9). The accept test (axiom-licensed hop-1
  uniqueness) stays disjoint from the scoring function (exact match against
  third-party gold).
- Provenance triple (the adjudication's §6 disclosure): primary — items THIRD-PARTY
  (CLUTRR), gold THIRD-PARTY (CLUTRR generator), grader PROGRAMME (exact-match
  harness over the closed released vocabulary); secondary — items/gold/grader all
  programme (that is why it is secondary).
- Coverage, restated per the standing rule: m0b measured coverage_fraction 0.3542 at
  rung molecules-v0, corpus-indexed on the pinned TinyStories task family, on ONE
  incomplete kernel instance [MEASURED: registry/verdicts/m0b.json; ASM-0001] — that
  number does NOT describe either nsk1 corpus and extrapolates nowhere. The CLUTRR
  covered stratum has coverage BY FILTER (a committed mechanical predicate, verified
  at build by engine resolution of every covered item's hop-1 and re-verified by the
  run-time harness gate); the custom stratum has coverage BY CONSTRUCTION. Both are
  design properties of the filtered/synthetic corpora, not claims about natural text.

### 4.2 Stage 0 — B5 back-patch diagnostic (instrument gate + family cheap kill; dual surface)

Stage 0 runs the same procedure on BOTH strata, with distinct roles:

**(a) PRIMARY floor (CLUTRR covered stratum — the family kill).** Per rung: run
text-only on the 1,000 CLUTRR covered items; take the failure set; on up to 300
failures (pre-declared cap), sweep back-patches over a pinned (source-layer,
target-layer) grid; an item is *rescuable* if any grid cell yields the exact gold
answer. Gate: Wilson-LB(rescuable) ≥ 0.15 at each rung on THIS stratum, else the
record lands as the Stage-0 FAIL (family-level kill: no Stage-1 spend). Headroom
gate (instrument): text-only accuracy on the CLUTRR covered stratum must lie in
[0.05, 0.85] with ≥500 scored items, else INSTRUMENT-INVALID (no room to detect
anything) — the campaign-scale re-check of the §5.2 pre-freeze headroom blocker.
This touches CLUTRR only through the frozen record's own mechanical pipeline
(post-freeze, runner role) — it is a gate, never a selection rule.

**(b) CALIBRATION heatmap (custom secondary stratum — the L\* input).** Per rung: the
same text-only pass + back-patch sweep (cap 300 swept) on the 900 custom covered
items. This sweep's rescue heatmap + the patchscope calibration data from the
custom calibration split are the ONLY inputs to the FK-NSK-2 L\* rule and the
FK-NSK-5 α rule (selection stays custom-only; §5.3). Its rescuable fraction is
reported as a secondary alongside the custom stratum — it gates nothing.

### 4.3 Stage 1 — the decisive loop, seven arms per rung

| Arm | What it is |
|---|---|
| internal | hook at L\*: patchscope-decode → EXACT match against the item's closed name lexicon (per-item on CLUTRR, built from its own `story_edges`/`genders` name set; abstain out-of-lexicon; X3: no cosine/kNN anywhere) → engine hop-1 (licensed unique lookup in the item's converted world store) → cached steering vector keyed by the engine's answer record, h ← h + α·v at L\* |
| external-text | SAME pipeline through the engine, feedback rendered as one text sentence appended adjacent to the question, answer regenerated (F2 topology), extra tokens ≤ the matched budget (24); the PRIMARY comparator. On CLUTRR the sentence uses the corpus's own fact-sentence surface grammar ("P is the mother of X.") and NEVER contains the gold relation word (build assertion §5.1 S9) |
| text-only | no feedback, no hook |
| kernel-as-text | the item's converted kot-world records rendered as canonical text at matched extra-token budget (pre-declared record order, truncated at budget), NO engine resolution (Law-2 null: same content, no computation — on third-party items, strictly more meaningful than before) |
| shuffled | internal with a seed-pinned DERANGEMENT of the entity→vector map (kernel-keying semantics destroyed, plumbing identical) |
| random-dir | internal with a random vector at matched norm |
| noop-hook | hook installed, zero vector (prices the intervention plumbing itself) |

Question form on the primary stratum: CLUTRR's native "How is [A] related to [B]?"
(released `text_query` verbatim where present, else the fixed stem instantiated with
the released `query` order), scored by exact match of the generated relation word
against `target_text` over the closed 24-relation vocabulary. The engine-side hop-1 is
NOT parsed from the question: the run-time loop rule is "for each of the two query
endpoints, attempt the licensed unique lookup of each minted up-relation (mother-of,
father-of) in the item store; exactly one (endpoint, relation) pair resolves on a
covered item (asserted at build, §5.1 S9) and its answer is the bridge". The item's
`hop1` field is a converter-precomputed cache of that derivation (build-asserted
equal), so carrying it leaks nothing the store does not already determine.

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
  acc(external-text) on the PRIMARY covered stratum (the CLUTRR covered slice), per
  rung; one-sided 95% BCa bootstrap (B=2000, seed pinned). ABSOLUTE difference — no
  ratios, no gap-closure denominators (the F2 degenerate-primary lesson) [MEASURED
  context: registry/verdicts/f2.json FAIL fired on a degenerate ratio denominator].
- TOST equivalence margin ±0.02 (90% CI) pre-declared for the null reading.
- Secondaries (one Holm family): internal−text-only; external−text-only (replicates
  the F2 shape at hop-1 granularity); internal−kernel-as-text; internal−shuffled
  (specificity, §4.5); internal−random-dir; cost ledger deltas.
- Named secondary STRATUM (outside the Holm family, reported with CIs, licenses only a
  consistency statement): the same seven-arm contrast on the 900 custom covered items
  (strata labels `custom-covered`/`custom-uncovered` in the row log), plus the custom
  Stage-0(b) rescuable fraction.
- Instrument gates, each with its own bound, all computed on the PRIMARY surfaces:
  patchscope extraction-failure Wilson-UB ≤ 0.30 (CLUTRR covered, loop arms); mapper
  abstention on CLUTRR covered ≤ 0.20; steering-cache extraction success ≥ 0.90 of
  entities (custom calibration split); false-fire Wilson-UB ≤ 0.05 on the CLUTRR
  third-party uncovered controls; Stage-0(a) floor; headroom.

### 4.5 Pre-declared verdict logic (draft; margins final at freeze)

1. INSTRUMENT-INVALID if any instrument gate fails.
2. FAIL (family cheap kill) if Stage-0 Wilson-LB < 0.15 at either rung on the primary
   (CLUTRR covered) stratum.
3. KILL-semantics-free co-gate: PASS additionally requires one-sided 95% LB of
   acc(internal) − acc(shuffled) > 0 at both rungs; if the primary clears but this
   does not, the verdict is FAIL-attribution (the write channel works but
   kernel-keying adds nothing — the E9-defl discipline).
4. PASS: primary LB > 0 at both rungs AND (3) holds.
5. NULL-EQUIV: TOST holds at both rungs → equivalence recorded with the same
   prominence as a PASS.
6. Anything else: INCONCLUSIVE (report CIs; no adjective).

### 4.6 Power (on the covered slice, per the designer MUST)

Paired binary design, n = 1,000 CLUTRR covered items per rung (the §5.2 count gate's
full-power branch). Planning values (mechanism targets, not predictions):
acc(external-text) ≈ 0.45–0.60 (feedback names the bridge but composition must still
happen), detectable Δ = +0.05 absolute. With discordant pair rate ≈ 0.25–0.35,
McNemar-style power at one-sided α=0.05 is ≈ 0.8–0.9 at n=1,000; the TOST ±0.02 margin
at n=1,000 is decidable for accuracies in the headroom window (this is exactly what
the headroom gate enforces). The covered-slice count is a TO-MEASURE build fact,
deliberately not estimated here: if the §5.2 count gate lands 600 ≤ n_final < 1,000,
this power computation is REDONE at the achieved n and recorded in the record BEFORE
freeze; below 600 the fallback ladder fires instead. If Stage-0 leaves the text-only
accuracy outside [0.05, 0.85], the record self-declares INSTRUMENT-INVALID rather
than reporting an underpowered comparison. The 900-item custom secondary stratum
inherits the original power shape at slightly reduced n (reported, not verdict-bearing).

### 4.7 Extrapolation envelope (verbatim in the record)

Measured range on any outcome: R1–R2 (SmolLM2-135M/360M), ONE third-party covered
task slice — the CLUTRR covered stratum (clean k=2 up-edge-only chains over {mother,
father} with released gold in {grandmother, grandfather}, drawn from the pinned
release configs named in `data/nsk1-clutrr/manifest.json`, all facts in-context) —
plus ONE named self-authored secondary stratum (nsk1-eval), ONE kernel instance's
minted concepts (mother-of/father-of/man/woman), ONE write channel (B2 kernel-keyed
cached steering, α and L\* rule-selected on the custom calibration split only), k=1
loop cadence, ONE engine build. A PASS licenses exactly: "at these two rungs, on the
CLUTRR covered stratum as filtered here, kernel-engine content delivered by internal
steering beat the same content delivered as text at matched budget" — a sign (2
rungs), no scale adjectives, no slope. It does NOT license: any CLUTRR
leaderboard/SOTA/benchmark-performance claim (an inference-only filtered covered
subset is NOT the published CLUTRR task; published CLUTRR numbers may be cited as
context only, never as a comparison claim), any claim about uncovered CLUTRR strata
(k>2, noise configs, sibling/spouse/in-law relations), natural-corpus or NL-parse
claims, any statement at R3+, multi-hop beyond 2, other write channels, training-time
or trained-bridge claims, efficiency-thesis claims, or any "the kernel powers the
network" headline. The custom secondary stratum licenses nothing on its own beyond
"the same sign/null was or was not also observed on the self-authored stratum" (a
consistency report). A FAIL or NULL kills/demotes the training-free internal-write
family at these rungs and redirects the line's budget to external seams (L0/L3) and
later staged variants under their own gates. Stage-0's rescuable fraction
extrapolates only to the strata measured at these rungs (ASM-0024 resolution).

---

## 5. Inputs, harness, gates, mock ($0 design-side)

### 5.1 BUILD RECIPE — `data/nsk1-clutrr` (runner role; mechanical, $0, CPU-only)

Every step is a pure function of the fetched bytes + pinned seeds; NOTHING here reads
or parses natural language — all structure comes from CLUTRR's released structured
columns. The converter script is committed as `poc/nsk1/build_clutrr_corpus.py`
(runner-authored, then pinned in the record's harness manifest alongside its output
digest). ABORT = stop and return to the designer (a failed assertion means the format
understanding is wrong — never patch around it); DROP = exclude the row and count it
in the manifest.

**S1 — fetch + pin.** Source of record: `facebookresearch/clutrr` (the GitHub repo;
pin the commit sha you read it at, in the manifest). Fetch the released generated
dataset the README links: `data_emnlp_final.zip` (hosted on dl.fbaipublicfiles.com).
Record in `data/nsk1-clutrr/manifest.json`: the resolved URL, the zip sha256, per-CSV
sha256s, and the in-zip directory → config-name mapping (directory names are internal
hashes; derive the mapping from the zip's own metadata/README and record it — do NOT
guess it). Also fetch `clutrr/store/relations_store.yaml` from the pinned repo commit
(the closed 24-relation vocabulary; copy verbatim into the manifest). FALLBACK (only
if the zip URL is dead): the HF mirror dataset `CLUTRR/v1` with a pinned revision,
disclosed in the manifest as the substituted source. Licence: CC-BY-NC-4.0 — write
`data/nsk1-clutrr/LICENSE-NOTICE` (attribution: CLUTRR, Sinha et al. 2019,
arXiv:1908.06177; licence name + link).

**S2 — parse (structured columns only).** Read every train/test CSV of every config
in the zip. Required columns (ABORT if any is missing): `id, story, query, target,
clean_story, proof_state, f_comb, story_edges, edge_types, query_edge, genders,
task_name, task_split`; the gold relation-word column is `target_text` if present
else `text_target` (record which name was found; take its bytes VERBATIM — the gold
is never recomputed, relabelled, or filtered-by-answer); use `text_query` verbatim
for the question if present. Python-literal columns (`story_edges`, `edge_types`,
`query_edge`, `proof_state`) are parsed with `ast.literal_eval` ONLY; `genders`
("Name:gender,Name:gender,...") is split mechanically.

**S3 — orientation determination (self-verifying; no convention is assumed).** An
edge `((a,b), r)` could mean "b is the r of a" (C1) or "a is the r of b" (C2), and the
query/gold pair `(A,B) → target` could be read in either direction (Q1/Q2). Score all
four (edge-convention × query-convention) combos over EVERY pooled row whose proof
chain has exactly 2 edges with both types in {mother, father}: under the combo,
identify base X (chain start), bridge P, top G; predict the gold word from the second
edge type (mother→grandmother, father→grandfather); count agreement with the released
gold word. Require exactly ONE combo with agreement ≥ 0.995 (ABORT otherwise); record
all four scores in the manifest. Cross-check `genders[G]` against the second edge
type's implied gender and report the (expected ~0) disagreement count.

**S4 — covered filter (the committed predicate, verbatim).** A pooled row is COVERED
iff, under the determined convention: (a) its `proof_state` chain has exactly 2
edges; (b) `story_edges` contains exactly those 2 edges and no others
(clean-by-structure — no noise/distractor facts; noise configs' perturbed rows fail
this mechanically); (c) both `edge_types` ∈ {mother, father}, and `f_comb` agrees
with `edge_types` (DROP disagreement, count it); (d) the released gold word ∈
{grandmother, grandfather}; (e) the query pair equals {chain base, chain top} as a
set; (f) the item's surface names (entities of `story_edges` ∪ `query`) are pairwise
distinct strings (DROP duplicates-in-item, count — expected ~0). Licensing note (why
up-edges only, restated from the adjudication): hop-1 on an up-edge ("the mother of
X") is axiom-licensed UNIQUE under the functional-parent axioms the engine carries;
hop-1 on a down-edge ("a son of X") is not functionally unique, so
grandson/granddaughter targets are EXCLUDED rather than smuggled in with
store-contingent uniqueness.

**S5 — third-party uncovered controls.** A pooled row is a CONTROL candidate iff (a),
(b), (e), (f) hold and NEITHER edge type is in {mother, father, son, daughter} —
sibling/spouse/in-law-only chains, zero convertible parent material, so the item's
converted store contains NO parent records and the engine MUST refuse every up-edge
lookup (this is what makes `fired` ≈ 0 the correct behaviour and keeps the
false-fire gate ≤ 0.05 sharp). Seed-pinned sample n=100 (seed 20260710), stratified
by `f_comb` pattern; composition table in the manifest. MIXED chains (one parent
edge + one other type) are EXCLUDED from this record entirely — their
store-contingent firing semantics would blur the false-fire gate; they are named
Phase-B successor material (§2.3 of the adjudication).

**S6 — pooling + dedup + split.** Pool covered rows across ALL configs and BOTH
`task_split` values (no training happens — train rows are legitimate inference-only
eval items; per-item official-test membership is carried and additionally reported
separately for literature comparability). Dedup by sha256 of the verbatim `story`
bytes, keeping the first occurrence under the manifest's config listing order (log
the collision count). Then carve, seed-pinned (seed 20260710): (1) the 100-item
HEADROOM-CALIBRATION slice (discarded from all final analysis; also the only
permitted source of any few-shot exemplars, fixed at freeze); (2) the final covered
set n_final = min(1000, pool − 100), sampled stratified by (`f_comb` pattern ×
config); (3) the remainder unused (listed in the manifest). The §5.2 count gate reads
n_final.

**S7 — world-store conversion (mechanical; the engine never sees story text).**
Entity URNs: `urn:kotw:v0:clutrr-<config>-<csvrow>-<name-slug>` (name-slug =
lowercased name, non-alphanumerics → `-`; URNs are item-scoped so cross-story name
reuse cannot collide). Records emitted per item into a single `world.jsonl`
(kot-world/1, same shapes as `data/nsk1-eval`): for every entity in `story_edges` ∪
`query`, one class record (man/woman by `genders`; skip-and-count if the gender is
missing); for every story edge under the determined convention: `mother` →
relation record {subject: child, relation: mother-of URN, object: parent}; `father`
→ same with father-of; `son`/`daughter` → the REVERSED parent record (parent edge
child→parent with the relation chosen by `genders[parent]`) plus the child's class
record; ALL other edge types → NOT converted (no minted kernel concepts — Phase B
mints sibling-of/spouse-of, out of this record). The minted concept URNs are exactly
the ones `data/nsk1-eval/axioms/` uses (mother-of, father-of, man, woman); copy the
axiom files from `data/nsk1-eval/axioms/` BYTE-VERBATIM into
`data/nsk1-clutrr/axioms/`. The kernel side is untouched: CLUTRR bytes are EVAL-side
only (S11).

**S8 — item emission (the nsk1 harness format).** `items.jsonl`, one object per item:
`item_id` (`clutrr-c%04d` covered / `clutrr-u%04d` control); `context` = [the
released `story` bytes verbatim] (single-element list); `question` = released
`text_query` verbatim if present, else `How is [A] related to [B]?` instantiated in
the released `query` order (manifest records which path); `gold_surface` = the
released gold relation word verbatim; `gold_relation` = the raw `target` column;
`gold_entity` = null; `hop1` = {subject: URN(X), rel: minted URN(first edge type),
direction: "forward", op: "unique"} and `hop1_bridge` = URN(P) for covered items,
both null for controls; `hop2_rel_surface` = the gold word (report field);
`lexicon` = the item's closed name lexicon {URN: surface} (the read-channel match
set); `stratum` = "covered"/"uncovered"; `provenance` = {config, task_name,
task_split, csv row id, story sha256, and the §2.4-preserved columns VERBATIM:
f_comb, edge_types, story_edges, query_edge, genders, proof_state, target,
gold word}. Global `lexicon.json` carries the closed 24-relation ANSWER vocabulary
(from relations_store.yaml) plus a pointer that name-matching is per-item; scoring is
exact match over the closed vocabulary — no cosine anywhere (X3).

**S9 — build assertions (all mechanical; run before pinning).**
1. Engine resolution: load `world.jsonl` + `axioms/` with the REAL `kot_axiom.Engine`;
   for every covered item, `query(hop1)` returns status "answer" with value ==
   `hop1_bridge`, licensed. 100% or ABORT.
2. Run-time-rule equivalence (why `hop1` is a cache, not leakage): for every covered
   item, of the four (query-endpoint × {mother-of, father-of}) licensed unique
   lookups, EXACTLY ONE resolves, and it equals (`hop1.subject`, `hop1.rel`) → bridge.
   100% or ABORT.
3. Control refusal: for every control item, all four lookups refuse. 100% or ABORT.
4. Gold-not-in-feedback: the deterministic feedback renderer's output for each
   covered item's hop-1 never contains the item's gold word as a TOKEN
   ("mother" vs "grandmother" is token-distinct; substring is not the test). 100% or
   ABORT.
5. Report-only: count covered items whose story bytes contain the gold word as a
   token (surface-contamination note in the manifest).

**S10 — counts, manifest, pin, mock.** Write `manifest.json` (source pins, directory
mapping, orientation scores, per-config/split counts, dedup collisions, drop counts
by reason, control composition table, headroom-slice ids, licence + attribution).
Run `tools/registry/corpus-pin.py` over `data/nsk1-clutrr/` and REPLACE the
`PINNED-AT-INPUTS` placeholder in `registry/experiments/nsk1.json` with the real
kot-corpus-hash/1 digest (the record is DRAFT — lawful pre-freeze edit). Then
`python3 poc/nsk1/nsk1_runner.py --mock --data data/nsk1-clutrr` MUST print
MOCK GREEN ($0; exercises the real engine + per-item mappers + analysis on the real
converted corpus with the stub host).

**S11 — licence quarantine (load-bearing for licence hygiene).** CLUTRR bytes are
EVAL-side only: nothing fetched or derived here may enter kernel concepts,
explications, molecules, or axiom content — the kernel artifact stays licence-clean.
`data/nsk1-clutrr/` carries the LICENSE-NOTICE + provenance manifest; the NC
constraint (no commercial packaging of this eval data) is a standing flag.

### 5.2 PRE-FREEZE GATES + fallback ladder (all BEFORE `prereg-freeze.py`; outcomes decide the rung, never post-hoc)

**G1 — build gates ($0, CPU).** All S1–S10 assertions green, plus the COUNT GATE on
n_final: n_final ≥ 1,000 → full-power branch (§4.6). 600 ≤ n_final < 1,000 → REDO the
§4.6 power computation at the achieved n and write it into the record before freeze.
n_final < 600 → the ladder moves to rung 2 with NO GPU spent on rung 1.

**G2 — headroom calibration (~$2–5 GPU; maintainer sign-off REQUIRED for even this
spend).** Per rung (both R1 and R2), on the discarded 100-item headroom slice, run
exactly two arms with the real hosts (greedy decode, prompt format fixed and logged):
text-only and external-text. PASS iff at BOTH rungs: (i) acc(text-only) ∈
[0.05, 0.85] AND (ii) acc(external-text) ≥ acc(text-only) + 0.02. Clause (ii) IS the
§7 skeptic-item-2 external-arm vacuousness check pointed at the new surface. Every
row is logged `phase:"exploratory"` (quarantined, uncitable, can never flip a
verdict); the 100 items and anything computed on them are excluded from the final
analysis. Cost bound: 2 rungs × 2 arms × 100 items × short generations ≪ 1 GPU-h.

**G3 — lit-report deliverable (designer side, $0).** `reports/lit-eval-benchmarks.md`
minting the source-verified CLUTRR facts (licence, fields, relation vocabulary) as a
proper lit-report — the adjudication's §5 pre-freeze deliverable. Freeze is blocked
without it.

**G4 — freeze mechanics.** Corpus digest real (S10), harness manifest re-pinned to
the final runner/converter shas, analysis script re-pinned (freeze revision computes
per-rung fields + IUT minima + the custom-stratum secondary fields), skeptic memo
re-run (§7), THEN `prereg-freeze.py`. The frozen record NAMES the ladder rung that
passed G2.

**FALLBACK LADDER (pre-declared; each rung re-runs G2 before freezing):**
- **Rung 1 — CLUTRR native relation task** (this design as specified). Freeze here iff
  G1 + G2 pass.
- **Rung 2 — entity-question form** (fires if G1 count < 600 or G2 fails at rung 1):
  questions become "Who is the grandmother of [X]?" over the SAME CLUTRR covered
  graphs (third-party items/graphs retained; the question template is
  programme-authored and DISCLOSED as such in the record); gold = the chain-top
  entity name by mechanical traversal of the released `story_edges` (still disjoint
  from the engine's hop-1); the answer lexicon becomes the per-item name lexicon.
  Re-run G2 on the same 100 discarded graphs in entity form (~$2–5 more).
- **Rung 3 — custom primary** (fires if rung 2 fails G2): the pre-pivot design —
  `nsk1-eval` returns to primary, CLUTRR demoted to a reported stratum. This rung
  has already passed its analog of G2's shape by construction and freezes directly;
  the record discloses that the third-party surface failed headroom at both rungs of
  the ladder. (AMENDED 2026-07-10 — see §5.2.1: rung 3 no longer freezes directly;
  it must first pass its own measured two-clause G2 check on the custom calibration
  split. The rung-1 outcome showed shape-by-construction does not predict measured
  headroom.)

### 5.2.1 LADDER RESOLUTION — rung-1 G2 adjudication (2026-07-10, designer)

**Outcome (recorded).** The rung-1 G2 headroom calibration was run by the runner role
(Modal A10G, `poc/modal/modal_nsk1_g2.py`, greedy, max_new_tokens=16, chat template,
400 generations) on the discarded 100-item headroom slice, after all S1–S10 build
gates landed green.

- PREMISE: rung-1 G2 FAILED at both rungs and on both clauses —
  acc(text-only) = 0.000 and acc(external-text) = 0.000 at R1 (SmolLM2-135M-Instruct)
  and R2 (SmolLM2-360M-Instruct), n = 100 per arm per rung
  [MEASURED: poc/nsk1/out/g2/g2_summary.json sha256
  3971708481bdc895ed01cf9e893d53d5afccf33b9334dc72f8ff3d7638095b24; scope: these two
  Instruct checkpoints, zero-shot, greedy, the as-built S8 prompt, this one 100-item
  discarded CLUTRR slice; phase:exploratory — quarantined from verdicts, licensed
  only to decide this pre-freeze gate as §5.2 pre-declares].

**Diagnosis (from the 400 logged generations).** Row-level facts, all
[MEASURED: poc/nsk1/out/g2/g2_rows.jsonl sha256
e0d75e1c626eb861f60f592a72cbd30d80e09ae87e1affd118f030111e3b7c48; same scope and
quarantine as above]:

1. *Not a scoring artifact.* The models never emit the gold word: grandparent-word
   first-match is 0/100 in ALL four rung×arm cells; ANY grand-token
   (grandmother/-father/-son/-daughter) appears in ≤3/100 generations per cell. The
   closed-vocab first-match scorer is not what zeroed the accuracy.
2. *Not format collapse.* The models engage with the task shape: 59–90% of
   generations per cell contain some closed-vocabulary relation word; R2 obeys the
   short-answer instruction in 72/100 cases. They produce relation words — just
   never the right one (R1 mode: story-surface echoes and hallucinated in-laws,
   e.g. h0001 text-only "Joe is related to Gabrielle through a mother-in-law
   relationship"; R2 mode: bare "aunt", 26/100 text-only). Gold-gender agreement of
   the produced relation word is ≈ chance (43/86 at R1 text-only) — no partial
   compositional signal in the relation channel.
3. *The external channel is DELIVERED but not COMPOSED.* The appended hop-1 feedback
   visibly moves behaviour: at R1 the first relation word equals the fed hop-1
   relation (mother/father) in 46/100 external generations vs 20/100 text-only, and
   bridge-entity mentions rise 44→76/100 (e.g. h0002 external: "Joe's family
   relationship is with his mother, Lisa." — a verbatim paraphrase of the feedback
   "Note: the mother of Joe is Lisa."). The models read the fed fact and parrot it;
   they do not compose it with the second story edge. Clause (ii) therefore cannot
   pass at these rungs on this task form for ANY delivery mechanism — the vacuousness
   check did exactly its job.
4. *A real S8 template-direction confound, documented and disposed.* Under the
   build-determined convention C1/Q1 (manifest `orientation_S3`), the released gold
   is the TOP entity's relation to the BASE ("Gabrielle is Joe's grandmother"), while
   the S8 fallback stem "How is [A] related to [B]?" instantiated in released query
   order (A=base, B=top) naturally reads as A's relation to B — whose correct answer
   is grandson/granddaughter, the inverse of gold. This is a genuine instrument bug
   (the question asks the inverse of what the gold scores). It is NOT, however, the
   measured cause of the failure: per fact 1, the models produce the
   direction-corrected reading's answer (grandson/granddaughter) in ≤3/100
   generations per cell too, so under EITHER reading the text-only accuracy of these
   generations is ≤0.03 < the 0.05 floor. Whether a prompt whose question is
   direction-corrected would elicit different generations is a counterfactual this
   run cannot measure — that residual is tagged EXTRAPOLATION, is deliberately NOT a
   premise of any decision below, and is resolved by the rung-1b rider in the re-run
   (proposed ASM, coordinator registration pending).
5. *Positive pre-signal for the entity form (rung 2).* Despite being asked a
   relation question, R2 answered with a bare in-lexicon NAME in 35/100 text-only
   generations, and 12 of those named the chain-top — the correct grandparent entity
   (vs 4 bridge, 19 question-echo; e.g. h0002 text-only at R2: "Gabrielle", which IS
   Joe's grandmother). Under feedback the name answers shift toward the fed bridge
   (4→12) — the same deliver-then-parrot pattern. The entity channel carries signal
   at R2 that the relation-word channel does not.

Adjudication: the failure is primarily (c) genuine incapacity of these hosts, at
these sizes, zero-shot, to compose two in-context parent edges into the grandparent
RELATION WORD — with (a) the S8 direction confound real but evidentially non-causal,
and (b) the entity-question form holding the only measured positive signal. This is
the flagship's first feasibility datum: on the native CLUTRR relation surface there
is no headroom at R1–R2 for ANY grounding mechanism to be measured against.

**AMENDMENTS to the ladder (pre-declared here, BEFORE the re-run; the record is
DRAFT and G2 is a pre-freeze gate, so this is a lawful pre-freeze amendment — the
decision rule is fixed now, not after the data):**

- DECISION: one combined G2 re-run (spec below) measures TWO forms on the same
  discarded 100-item slice — rung 1b (the rung-1 relation task with the S8 direction
  bug fixed) and rung 2 (the pre-declared entity-question form); the freeze
  candidate is the FIRST form in the order [1b, 2] that passes both G2 clauses at
  both rungs; if neither passes, rung 3 fires
  [MEASURED: poc/nsk1/out/g2/g2_summary.json sha256
  3971708481bdc895ed01cf9e893d53d5afccf33b9334dc72f8ff3d7638095b24 — the basis for
  amending rather than proceeding: the
  pre-declared rung-1 form failed its gate, and diagnosis fact 4 shows the rung-1
  G2 tested a direction-inverted instantiation of the intended construct, so the
  corrected form inherits rung 1's ladder priority (third-party gold retained)
  rather than being skipped]. Rung 1b is a bug-fix re-test of the SAME ladder rung,
  not a new design; rung 2 is unchanged from the pre-declaration.
- DECISION: rung 3 no longer "freezes directly": before any rung-3 freeze, the same
  two-clause G2 check (text-only ∈ [0.05, 0.85] AND external ≥ text-only + 2pp, both
  rungs) must be run and passed on the 100-item CUSTOM calibration split
  (`nsk1-eval`, already excluded from final analysis), ~$2–5, phase:exploratory
  [MEASURED: poc/nsk1/out/g2/g2_summary.json sha256
  3971708481bdc895ed01cf9e893d53d5afccf33b9334dc72f8ff3d7638095b24 — the lesson
  forcing this: rung 1 was
  believed adequate "by construction" and measured 0.000; shape-by-construction is
  not measured headroom]. If rung 3 ALSO fails its G2, the record does NOT freeze:
  the ladder is exhausted, the no-headroom result is written up as the feasibility
  finding, and host scale vs task family becomes a registered fork for the
  maintainer (no silent host upgrade inside this record).
- DECISION: the record's hosts are reconciled to the Instruct variants —
  R1 = HuggingFaceTB/SmolLM2-135M-Instruct, R2 = HuggingFaceTB/SmolLM2-360M-Instruct
  (revisions pinned at freeze) [MEASURED: the G2 calibration and the verified Modal
  transport path ran these checkpoints — poc/nsk1/out/g2/g2_summary.json sha256
  3971708481bdc895ed01cf9e893d53d5afccf33b9334dc72f8ff3d7638095b24 `model` fields;
  the task is chat-shaped and base variants were never exercised on this surface].
  All G2 evidence and the eventual campaign then share one host family.

**Combined G2 re-run — exact spec (runner role; maintainer sign-off required per the
standing §5.2 G2 spend gate before launch):**

- Harness: extend `poc/modal/modal_nsk1_g2.py` (same Modal app, A10G or L4, fp32,
  chat template, greedy, max_new_tokens=16, seed-free greedy decode as run 1).
- Items: the SAME 100 discarded headroom items (`data/nsk1-clutrr/headroom.jsonl`);
  all rows `phase:"exploratory"`; outputs to `poc/nsk1/out/g2b/g2b_rows.jsonl` +
  `g2b_summary.json` (per-form × per-rung accuracies, gate clauses, and PASS fields).
- Form 1b (direction-corrected relation question): question = the S8 stem
  instantiated in REVERSED released query order — `"How is %s related to %s?" %
  (top_surface, base_surface)` (under Q1 the released query is (base, top); the
  reversal makes the natural reading ask for top's relation to base, which is what
  the released gold scores). Instruction, closed 24-word vocabulary, first-match
  scorer, and gold (`gold_surface`, the released target verbatim) all UNCHANGED from
  run 1.
- Form 2 (entity question, the pre-declared rung 2): question =
  `"Who is the %s of %s?" % (gold_surface, base_surface)` (gold_surface ∈
  {grandmother, grandfather}, released target verbatim — the programme-authored
  template is DISCLOSED as such); instruction = `"Answer with exactly one word: the
  name of the person. Answer:"`; gold = the chain-top surface, derived mechanically
  as the item-lexicon entry that is neither `hop1.subject` nor `hop1_bridge` (all
  100 headroom items verified 3-name with pairwise-distinct surfaces); scorer =
  first per-item-lexicon surface occurring in the generation EXCLUDING the queried
  base surface (a mechanical anti-question-echo rule, identical across arms;
  diagnosis fact 5 measured 19/35 bare-name answers echoing the base) — correct iff
  it equals the chain-top surface; no non-base lexicon name in the generation =
  incorrect.
- Both forms, two arms each: text-only and external-text; the feedback sentence is
  byte-identical to run 1 (`"Note: the %s of %s is %s."` — hop-1 relation surface,
  base, bridge). Gold-not-in-feedback is asserted per form at render time: form 1b
  by relation-word token distinctness (S9.4, unchanged); form 2 by the gold NAME not
  appearing among the feedback tokens (holds by S4(f) pairwise-distinct names;
  assert anyway, ABORT on violation).
- Volume and cost: 2 rungs × 2 forms × 2 arms × 100 items = 800 short generations,
  ≪ 1 GPU-h, ~$2–5 — within the standing G2 envelope (run 1's 400 generations
  completed in minutes); the doubling vs the original G2 cost line is disclosed here.
- Gate application (pre-declared): a FORM passes iff at BOTH rungs
  (i) acc(text-only) ∈ [0.05, 0.85] AND (ii) acc(external-text) ≥ acc(text-only) +
  0.02. Freeze candidate = first passing form in the order [1b, 2]; neither passes →
  rung 3 fires (with its own G2 check per the amendment above).
- Post-G2 mechanics for whichever form freezes (runner role, before G4): rebuild
  `data/nsk1-clutrr/items.jsonl` per the corresponding S8 revision — S8-1b: covered
  AND control questions instantiated in reversed released query order; S8-2: covered
  questions in the entity template with `gold_entity` = top URN and `gold_surface` =
  top surface, controls given the same stem instantiated with released `query[0]`
  and `gold_entity` null (their role — the false-fire gate — is unchanged and
  unscored) — then re-pin the corpus digest, re-run S9 (with the per-form S9.4
  extension above) + the S10 mock, REDO the §4.6 power computation with planning
  values anchored to the winning form's G2 point estimates (exploratory numbers used
  as planning inputs only, never as evidence), update the record's DV
  definition/envelope to NAME the frozen form, re-run the §7 skeptic memo, and only
  then `prereg-freeze.py`.

**Feasibility note (what this outcome already means, within its scope).** At R1–R2,
zero-shot, on the native CLUTRR grandparent relation task, there is no measurable
headroom for the flagship's question — not because feedback fails to arrive (fact 3
shows it arrives and is echoed) but because these hosts cannot execute the 2-hop
compose step in the relation-word output space. That is itself programme evidence:
if the ladder exhausts, the honest finding is "at 135M–360M the direct
internal-vs-external grounding contrast is unmeasurable on this task family because
the hosts lack the composition capability the grounding is meant to assist", and the
flagship's direct test moves to either an easier covered task form or a host with
measured headroom — by registered fork, not by silent redesign. No claim beyond
these two checkpoints, this slice, zero-shot greedy decoding is licensed; published
CLUTRR baselines are all TRAINED models and say nothing about zero-shot tiny-instruct
capability (context only, per the §4.7 envelope).

**ASM registration pending (coordinator).** Four proposed register entries are
reported in the adjudication handoff (entity-form construct validity; the
two-candidate ≈0.5 guess-floor disclosure for form 2; the 1b counterfactual as a
flagged non-load-bearing extrapolation resolved by the rider; Instruct-host
reconciliation). Freeze-time premises resting on them must cite the assigned ASM ids
once registered.

### 5.3 The demoted custom corpus (calibration + named secondary stratum)

- Generator: `poc/nsk1/gen_nsk1_corpus.py` (seeded, RNG-pinned, stdlib-only) →
  `data/nsk1-eval/` (digest above; manifest carries counts + the gold-independence
  statement). Unchanged bytes; unchanged pin.
- Roles, exhaustively: (i) the 100-item calibration split — FK-NSK-2 L\* rule +
  FK-NSK-5 α rule inputs, excluded from final analysis; (ii) the custom Stage-0(b)
  heatmap (§4.2); (iii) the 900 remaining covered items + 100 custom uncovered
  controls as the NAMED secondary stratum (row-log strata `custom-covered` /
  `custom-uncovered`), keeping the literature-matched entity-bridge task shape so an
  extraction-driven INSTRUMENT-INVALID on CLUTRR cannot zero out the family's
  information [LIT-BACKED: arXiv:2406.12775 (2024), via
  reports/lit-structured-parsing-and-inner-symbolic.md]. Selection rules never touch
  the third-party surface (strict tuning/eval provenance separation).

### 5.4 Harness, analysis, mock — built and green

- Harness: `poc/nsk1/nsk1_runner.py` — two stages, seven arms, `--mock` mode, and (this
  revision) a `--data` corpus-root argument, per-item lexicon support (items carrying
  a `lexicon` field get their own ExactMapper — the CLUTRR read channel), and a
  null-`hop1` guard (a control item with a matched name but no licensed query
  no-ops instead of crashing). Mock exercises the REAL kot-axiom engine, the REAL
  exact-match mapper (abstains on all uncovered controls), the REAL
  derangement/keying/budget-ledger/logging schema, and the REAL pinned analysis; only
  the host model is a deterministic stub with clearly-fake accuracy profiles. Real
  mode fail-closes (`ERR_NSK1_GPU_GATED`) — the final campaign belongs to the runner
  role against the frozen record, never to this designer (run≠audit).
- Analysis (pinned): `analysis/nsk1.py` — Wilson gates, paired BCa (bias-corrected,
  jackknife-accelerated), TOST, specificity delta; sha256
  `aba06bbee99dd7b85295cefcaa129acba9dd5a66cb4c2e4baeb03013a63631c0` (re-pinned at
  freeze; the mock-stage analysis computes single-pseudo-rung fields over the
  `covered`/`uncovered` strata — the freeze-stage revision computes per-rung fields,
  their IUT minima across R1/R2, and the `custom-covered`/`custom-uncovered`
  secondary-stratum fields).
- Mock run 2026-07-10 (post-revision): `python3 poc/nsk1/nsk1_runner.py --mock` →
  9,000 rows, all pinned endpoint fields present and decidable, exit 0
  ("MOCK GREEN"). $0 spent. The CLUTRR-format path (per-item lexicons, null-hop1
  controls) re-runs the same mock against `data/nsk1-clutrr` at build time (§5.1 S10).

---

## 6. What this experiment decides for the flagship (the envelope's upside)

The maintainer's flagship needs, before any trained variant is worth building, an
answer to the cheapest form of its core question: *is there any value at all in the
kernel touching the computation from inside rather than from the prompt?* nsk1 is that
question with every established instrument and every programme lesson (oracle
leakage, degenerate denominators, shuffled controls, refusal validity, coverage
honesty) already priced in — and, after the CLUTRR pivot, answered on a THIRD-PARTY
primary surface, so whatever the outcome is, it cannot extend the documented
"PASS confined to a self-authored slice" pattern. A PASS opens V2–V7 in order of cost with a measured
existence proof behind them; a clean NULL-EQUIV/FAIL saves the entire family's Tier-3+
budget and redirects the flagship toward the external-engine topologies that already
have a CONFIRMED artifact (l3a) — either outcome moves the programme.

---

## 7. Skeptic memo (pre-freeze attack — freeze stays BLOCKED until re-run after amendments)

1. **Oracle leakage (the f2b class).** Attack: does any feedback contain the gold?
   No — engine resolves hop-1 only. On the PRIMARY stratum the gold is a relation
   WORD (grandmother/grandfather) and the feedback names a bridge ENTITY and a hop-1
   relation word (mother/father): token-exact distinctness is a build assertion
   (§5.1 S9.4), so the feedback can never contain the gold string. On the custom
   stratum, generator structure makes bridge (a parent) and gold (a grandparent)
   distinct entities always — VERIFIED in-corpus (1,000/1,000 distinct). And the gold
   itself is third-party on the primary stratum (`target_text` verbatim), so
   gold-vs-accept-test provenance is disjoint BY SOURCE, not just by construction.
2. **Baseline asymmetry / strawman external arm.** Attack: the external arm could be
   weakened by clumsy feedback phrasing. Mitigation: feedback sentence is the SAME
   deterministic renderer both arms' ledger uses; on CLUTRR its phrasing follows the
   corpus's own fact-sentence surface grammar ("P is the mother of X."); the external
   arm regenerates with the feedback placed adjacent to the question (best-known
   position). Pre-freeze REQUIREMENT: the §5.2 G2 check that external-text ≥
   text-only + 2pp on the discarded CLUTRR headroom slice — if the external loop does
   not visibly work on the new surface, the comparison is vacuous and the fallback
   ladder (not an ad-hoc redesign) decides what freezes (a freeze-blocker check,
   not a verdict gate).
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
8. **Filter authorship (the residual programme-authored surface).** Attack: the
   covered-slice filter is programme-authored — could it be tuned to flatter the
   internal arm? Mitigation: the predicate (§5.1 S4) is pre-declared HERE, before any
   model has touched any CLUTRR item; it is a committed pure function of released
   structured columns; and its terms (k=2, up-only, grandparent targets) are forced
   by the engine's licensing algebra (functional-parent axioms), not by observed
   accuracies. The remaining programme-authored surfaces are exactly the mechanism
   under test and this filter — both auditable bytes.
9. **Contamination (new, benchmark-specific).** Attack: CLUTRR is public since 2019
   and may be in SmolLM2 pretraining. Priced, not ignored: the primary is a
   WITHIN-ITEM arm contrast, so contamination is symmetric across arms in first
   order; its main first-order effect is headroom compression, which G2 + the
   campaign headroom gate measure directly. A names-swapped scramble diagnostic
   (consistent global name permutation on a covered subsample, text-only arm,
   reported-only, `phase:"exploratory"`) is recommended as a memorization probe; it
   gates nothing. [STIPULATED: ASM-0027 carries this residual.]
10. **Residual honest weakness (stands, disclosed):** the primary is still a
   synthetic-construction task family (third-party, but generated), all facts
   in-context, natural-ish template/AMT-paraphrase text; and the read channel now
   faces ordinary first names instead of invented unique surnames — the custom
   corpus's easy lexicon was itself a mild oracle-favourable authoring choice, so the
   harder read is the honest one (priced by the extraction-failure gate ≤ 0.30 and
   the G2 ladder). Natural-corpus task families remain staged behind this record
   (ASM-0027 residuals).

---

## 8. Compute ask (Tier 2; design-stage estimate, no spend authorised by this doc)

- GPU: 1× A10G (or L4) on Modal, the existing poc/modal harness pattern.
- Pre-freeze G2 headroom blocker: 2 rungs × 2 arms × 100 items ≪ 1 GPU-h ≈ **$2–5**
  (its own maintainer sign-off; §5.2).
- Stage 0, dual surface: baseline passes (2 rungs × (1,100 CLUTRR + 1,000 custom)
  items, short generations) + back-patch sweeps (≤300 failures × ~40 grid cells × 2
  strata × 2 rungs) ≈ 5–8 GPU-h.
- Stage 1: steering-cache extraction (≈3,300 CLUTRR item-scoped entities + ≈1,120
  custom entities × 16 carrier prompts, forwards only) + 7 arms × (1,100 CLUTRR +
  1,000 custom) items × 2 rungs + patchscope side-decodes ≈ 8–12 GPU-h.
- Estimate: **14–20 GPU-h ≈ $20–35 at A10G rates; requested caps $60 / 20 GPU-h /
  wall-clock 40 h** (retries, calibration, checkpointing). Same order of magnitude
  as the pre-pivot ask; the caps in the record are updated to match.
- Gate: maintainer sign-off (Tier-2 spend) + the §5.2 pre-freeze gates (G1 build,
  G2 headroom, G3 lit-report) + prereg-freeze of nsk1 + runner-role execution.
  Nothing runs off this document.

---

## 9. Out of scope for nsk1 (recorded so nobody smuggles them in)

Trained bridges of any kind (B4 replication, V7 CALM-hybrid — both carry their own
POST-F2/scaling-kill gates); decode-time integration (V5, gated on L3b);
multi-round latent loops (V6, gated on V1); NL-parse of natural questions
(l3a-parse's territory — the CLUTRR converter reads structured columns, never story
text); any CLUTRR leaderboard/SOTA/benchmark-performance claim (the covered slice is
an inference-only filtered subset, NOT the published task — §4.7); uncovered CLUTRR
strata (k>2, noise configs, sibling/spouse/in-law — Phase B mints sibling-of/spouse-of
under its own record); any efficiency-thesis headline (cost ledgers here are
secondaries). Directives §1 restated: nothing in this line imports RDF/OWL/SHACL
semantics — the engine is `kot-axiom/1` native, and the X3 cosine ban holds at every
step (all addressing is exact match).
