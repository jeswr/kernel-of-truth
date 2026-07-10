# B′ — nsk1 Stage-0 internal-channel diagnostic at R3 (runner-ready spec)

- **Author:** Fable experiment-designer role (`kern/fable-designer-nsk`), 2026-07-10.
  Companion to `registry/assessments/nsk1-g2d.json` (the G2d interpretive assessment
  this spec's host choice rests on). Written under the honesty-guard; every
  load-bearing claim tagged; new assumptions registered as ASM-0040..0043.
- **What this is:** the finalized, execution-ready form of ladder-exhaustion fork
  rank 3 (`docs/next/nsk1-ladder-exhaustion.md` §6 "B′"), i.e. the nsk1 design's
  Stage-0 back-patch rescuable-fraction diagnostic (`docs/design-neurosym-kernel-internals.md`
  §4.2), amended post-G2d in exactly three pre-declared ways: (i) host moves from
  R1/R2 to R3 = SmolLM2-1.7B-Instruct (ASM-0040); (ii) the rescue criterion gains a
  shuffled-source control conjunct (ASM-0041); (iii) the item set is the full
  958-item covered CLUTRR set under the disclosed contact discipline (ASM-0043).
  Everything else (grid shape, sweep cap, floor value 0.15, greedy fp32 chat-template
  max_new_tokens=16 config) is carried unchanged from the design + the G2 ladder.
- **What this is NOT:** a freeze, a verdict-bearing run, or a Stage-1 steering test.
  nsk1 stays DRAFT. Every row is `phase:"exploratory"` — quarantined, uncitable,
  flips no verdict. B′ decides a registered maintainer fork, nothing more.
- **Sequencing authority:** the maintainer chose the G2d → B′ sequence when adopting
  the ladder-exhaustion fork; G2d is done (assessment above); B′ is the named next
  step. Spend fits the standing compute authorization (est. ≤ USD 25, caps §7).

---

## 1. Premises (why this run, on this cell)

- PREMISE: the G2 ladder + G2d found no (form, host, shot) cell where the text-delivery comparator passes the two-clause headroom gate at two rungs, so the text-comparator nsk1 design does not freeze at any tested host [MEASURED: poc/nsk1/out/g2d/g2d_summary.json sha256 93a6e951f6f8c9bcf648f704686c289241a5ac3238955df9d9846336b10b12d0; scope: n=100/cell, phase:exploratory, pinned Instruct checkpoints, greedy fp32].
- PREMISE: at R3 = SmolLM2-1.7B-Instruct, zero-shot, CLUTRR entity form, text-only accuracy is 0.76 (in-window) while the external-text arm is 0.43 — and the paired recount shows 0/24 failures rescued and 33/76 correct items broken by bridge substitution [MEASURED: poc/nsk1/out/g2d/g2d_rows.jsonl sha256 304a0f49290760d9c85b0bf92a0acd99b950127e214a6dd1c63f7edd47d21f40, recount in registry/assessments/nsk1-g2d.json; same scope + quarantine].
- PREMISE: training-free back-patching (a later layer's hidden state moved to an earlier layer, same position) rescued up to 66% of failed 2-hop queries on larger hosts, establishing the instrument class this diagnostic reuses [LIT-BACKED: arXiv:2406.12775 (2024), verified in reports/lit-structured-parsing-and-inner-symbolic.md §2.2].
- PREMISE: the extension of that rescue magnitude to 1.7B on this slice is an open projection used ONLY for sizing, registered with resolution path = this run [STIPULATED: ASM-0042 carries it as a non-load-bearing EXTRAPOLATION; no line below premises a rescue magnitude].
- The question B′ answers: does the composition capability that R3 demonstrably has
  fail on the residual-timing axis the internal channel can reach (rescuable ≥ floor),
  and can residual-stream delivery of the engine's content rescue failures WITHOUT
  the substitution damage the text channel shows? A floor-pass opens the nsk1
  redesign at R3; a floor-kill retires the training-free internal-write family at
  the most favourable measured host, with a measured reason.

## 2. Decisions (all fixed here; the runner decides nothing)

- DECISION: single host R3 = `HuggingFaceTB/SmolLM2-1.7B-Instruct` (the G2d revision pin — record the resolved commit hash in the summary), zero-shot, CLUTRR entity form (form 2) only; no custom surface, no form 1b, no few-shot arms in this run [STIPULATED: ASM-0040].
- DECISION: item set = all 958 covered CLUTRR items (858 covered rows of `data/nsk1-clutrr/items.jsonl` sha256 0e1f5c6bad6f97b575e3c354803713c3efef2a25cf76a9745e79b3d584f5839e + 100 rows of `data/nsk1-clutrr/headroom.jsonl` sha256 8b8e99e48cce5fd40a8b7e858b4b75730c9a2d66e9237034f0d3b3b4468c4d8d), under the disclosed pre-freeze contact discipline [STIPULATED: ASM-0043].
- DECISION: the Stage-0 floor VALUE stays 0.15 as pre-declared, and the criterion becomes the two-conjunct rule of §5 (Wilson-LB ≥ 0.15 AND paired excess over the shuffled-source control) [STIPULATED: ASM-0041].
- DECISION: two probe families, both replacement-transplants of the model's OWN activations (Law 1: no raw kernel/encoder coordinates ever enter the model) — P1 self back-patch (the §4.2 V0 diagnostic, gate-bearing) and P2 oracle bridge-patch (the mechanism-shaped probe, reported-only). P2 uses cross-prompt replacement (patchscope-style transplant), deliberately NOT the Stage-1 B2 additive steering channel: B′ tests whether the residual-stream delivery CHANNEL exists; the cached-steering instantiation (addition, α, carrier extraction, ASM-0025) stays Stage-1 work [STIPULATED: ASM-0041 covers the control/criterion; channel-vs-instantiation split restated from docs/design-neurosym-kernel-internals.md §4.2/§4.3].
- Config carried unchanged from G2d: Modal, 1× A10G, fp32, chat template, greedy,
  `max_new_tokens=16`; new entrypoint appended to `poc/modal/modal_nsk1_g2.py`
  (existing content byte-untouched) or a sibling `poc/modal/modal_nsk1_bprime.py`
  reusing its helpers by import/copy — runner's operational choice, disclosed in
  the summary.

## 3. Exact procedure

**Step 0 — prompts.** Render the form-2 (entity) TEXT-ONLY prompt for every covered
item, byte-identical in construction to `_build_specs_g2b`'s `f2_to` (question
`"Who is the %s of %s?" % (gold_surface, base)`, instruction = the g2b
`INSTRUCTION_ENTITY`, no feedback sentence), where base/bridge/top derive from
`lexicon` + `hop1` + `hop1_bridge` exactly as in `_build_specs_g2b`. Gold = the
chain-top surface. Scorer = `_score_entity` byte-identical (first per-item-lexicon
surface excluding the queried base; no non-base name = incorrect).
ASSERT (ABORT on failure): for the 100 headroom items, the rendered prompt is
byte-equal to `_build_specs_g2b`'s `f2_to` output; every item is 3-name-distinct.

**Step 1 — text-only pass + harvest.** One prefill+generate per item (958 gens).
During each prefill, harvest the residual stream at the FINAL PROMPT-TOKEN position
for the layer set of Step 2 (HF convention: `hidden_states[ℓ]` = output of decoder
layer ℓ, `hidden_states[0]` = embeddings; store fp32 vectors).
REPRODUCIBILITY CHECK: the 100 headroom items' text-only correctness must agree
with the G2d R3/clutrr/form-2 `correct_text_only` vector on ≥ 95/100 items
(greedy + byte-identical prompts; tolerance covers batching-order numerics);
< 95 ⇒ ABORT (environment drift), report the disagreements.

**Step 2 — layer grid.** L = `config.num_hidden_layers` (ASSERT L ≥ 12; expected 24).
`lay(f) = min(L−1, max(1, round(f·L)))`. Sources S = {lay(f): f ∈ {1/2, 7/12, 2/3,
3/4, 5/6, 11/12}}; targets T = {lay(f): f ∈ {1/12, 1/6, 1/4, 1/3, 5/12, 1/2}}
(dedup each). P1 cells = {(ℓs, ℓt) ∈ S×T : ℓs > ℓt}; P2 cells = S×T (no ordering
constraint). ASSERT 20 ≤ |P1 cells| ≤ 40 and |P2 cells| ≤ 40. (At L=24: S =
{12,14,16,18,20,22}, T = {2,4,6,8,10,12}, |P1| = 35, |P2| = 36.)

**Step 3 — swept sets.** Failure set F = text-only-wrong items. Swept = F if
|F| ≤ 300 else a seed-pinned uniform sample of 300 (seed 20260711). Correct
subsample C100 = seed-pinned (20260711) uniform sample of 100 text-only-correct
items, disjoint from Swept by construction. Derangement σ over Swept, seed
20260711, ASSERT fixed-point-free.

**Step 4 — P1 self back-patch (gate-bearing).** For each item i ∈ Swept and cell
(ℓs, ℓt): re-run the text-only prompt with a forward-pre-hook on decoder layer
module index ℓt (0-indexed module list, so the hook edits the INPUT of the layer
whose `hidden_states` output index is ℓt+1 — equivalently the residual carrying
`hidden_states[ℓt]`) replacing the final-prompt-position vector with item i's OWN
harvested `hidden_states[ℓs]`; greedy-generate 16 tokens; score. Patch applies at
prefill only (decode steps run unhooked). CONTROL: identical sweep, the patch
vector taken from item σ(i)'s harvest at the same ℓs.

**Step 5 — P2 oracle bridge-patch (reported-only).** Carrier per item = the item's
feedback sentence from the byte-identical g2/g2b renderer, `"Note: the %s of %s is
%s." % (hop1-relation-surface, base, bridge)`, tokenized RAW (no chat template —
it is a declarative fact, not a chat turn), one forward pass, harvest
`hidden_states[ℓh]` at the LAST token of the LAST occurrence of the bridge surface
(locate via tokenizer offset mapping; ASSERT found, ABORT otherwise). Per-carrier
asserts (ABORT): gold-name-not-in-feedback; feedback word-count ≤ 24. For each
i ∈ Swept and (ℓh, ℓt) ∈ P2 cells: patch the carrier vector into the text-only
prompt's final-prompt-position residual at ℓt (same hook semantics as P1); generate;
score. CONTROL: carrier from item σ(i) (deranged bridge — the keying-specificity
miniature). BREAKAGE: the real bridge-patch sweep additionally runs on C100
(no control), measuring per-cell correct→wrong flips.

**Volume (planning, |Swept| ≈ 230 [STIPULATED: ASM-0042 planning band; sized from the G2d failure rate 24/100]):**
958 text-only + 230×35×2 (P1 real+ctrl) + 230×36×2 (P2 real+ctrl) + 100×36 (breakage)
≈ 38,000 short greedy generations; worst case (|Swept| = 300) ≈ 48,600. Batch per
cell; carrier forwards ≈ 330 (no generation).

## 4. Metrics (all computed in-run, mechanical)

Per item over its sweep: `rescued_p1` = 1 iff ANY P1-real cell yields exact gold;
likewise `rescued_p1_ctrl`, `rescued_p2`, `rescued_p2_ctrl`. Aggregates:
`rescue_*` = mean over Swept; one-sided Wilson 95% bounds (z = 1.6449) both
directions. Paired excess test (real vs ctrl, per probe family): b = #(real ∧
¬ctrl), c = #(¬real ∧ ctrl); one-sided exact binomial p = P(X ≥ b | n = b+c,
p = 0.5); `excess_pass` = (b > c) ∧ (p < 0.05). Per-cell heatmaps: rescue rate per
cell for all four sweeps; breakage rate per cell on C100. `headroom_ok` =
acc(text-only) ∈ [0.05, 0.85] with ≥ 900 scored items.

## 5. Decision rule (pre-declared; fork-deciding gate labels, NOT verdicts)

1. INSTRUMENT-INVALID iff NOT `headroom_ok`, or any ABORT fired, or
   `rescue_p1_ctrl` Wilson-LB ≥ 0.15 (control-rescues-at-floor ⇒ the metric is
   uninterpretable on this form, per the ASM-0041 revisit clause).
2. PASS iff Wilson-LB95(`rescue_p1`) ≥ 0.15 AND `excess_pass`(P1) — the latent
   layer-timing headroom floor, control-guarded.
3. KILL-NO-LATENT-HEADROOM iff Wilson-UB95(`rescue_p1`) < 0.15.
4. Anything else: INCONCLUSIVE (report bounds; no adjective; maintainer fork on
   any extension — none fires automatically).

Decidability note (design-time arithmetic, not evidence): at n_swept = 230 the
floor is clearly decidable for true rescue ≥ 0.20 (Wilson-LB ≈ 0.16) and correctly
undecided near 0.15 — matching the floor's role as a cheap kill, not an estimator.
P2 results, the heatmaps, and the channel-comparison block gate NOTHING: they are
reported beside the G2d text-channel benchmark (rescue 0/24, breakage 33/76) for
the fork discussion and the eventual redesign's skeptic memo.

## 6. Outputs + custody

`poc/nsk1/out/bprime/bprime_rows.jsonl` — one row per generation: `item_id`,
`probe` ∈ {text-only, p1, p1-ctrl, p2, p2-ctrl, p2-breakage}, `cell` [ℓs|ℓh, ℓt]
(null for text-only), `gen`, `correct`, `gold`, `phase`:"exploratory",
`gate`:"BPRIME", `host`:"R3", `model`, `surface`:"clutrr", `form`:"2".
`bprime_summary.json` — config echo (model revision hash, L, grids, seeds, caps),
input pins (items/headroom sha256s above), |F|, |Swept|, all §4 metrics + §5 gate
label, per-cell heatmaps, the reproducibility-check tally, wall-clock + cost.
Plus the run log. Runner reports sha256s of both files in the handoff; the runner
reports mechanical facts ONLY — interpretation, epistemic tags, and the fork
recommendation are designer work on these outputs (run ≠ interpret).

## 7. Budget, infra, phase

Modal, 1× A10G, fp32; est. 3–8 GPU-h ≈ USD 8–25 (planning estimate from G2d
throughput; STIPULATED-grade, never a measurement). Caps: **USD 25 / 10 GPU-h /
12 h wall-clock**; foreground gates per the standing ops rule; abort-and-return
(partial outputs kept, labelled) if any cap trips. Phase: `exploratory` —
pre-freeze fork diagnostic under the same licence as G2/G2d. Not a freeze
candidate: whatever B′ shows, freezing happens only through a redesigned nsk1
record (new/amended DRAFT → §5.2-style gates → skeptic memo → `prereg-freeze.py`),
never off this run.

## 8. Post-B′ paths (pre-stated so the outcome cannot be re-narrated)

- PASS → nsk1 redesign at R3: internal-arm primary against the text comparator
  with the G2d-revised reading (text is the measured-harmful channel; the internal
  arm must show rescue-without-substitution), rung logic and power redone by the
  designer, B′ contact disclosed verbatim (ASM-0043 clause iv), 360M-few-shot as
  the candidate second rung (ASM-0040 revisit clause).
- KILL → the training-free internal-write family is retired at the most favourable
  measured host with a measured reason; the flagship line redirects to
  engine-external topologies (L0/L3) and the staged trained-bridge variants under
  their own gates; ASM-0042 resolves negative in-scope.
- INCONCLUSIVE → maintainer fork on extension; no automatic spend.
