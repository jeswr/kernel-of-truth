# B″ — nsk1 Stage-0 KEYED internal-channel probe at R3 (runner-ready spec)

- **Author:** Fable experiment-designer role, 2026-07-10. Successor to
  `docs/next/nsk1-bprime-stage0-spec.md` (B′), commissioned by the maintainer's
  **REDESIGN** choice at the post-B′ fork (`registry/assessments/nsk1-bprime.json`
  `fork_recommendation`, rank 1). Written under the honesty-guard; every
  load-bearing line tagged; new assumptions registered as ASM-0200..0204.
- **What this is:** the control-unpassable replacement for B′'s Stage-0
  internal-channel diagnostic. B′ was INSTRUMENT-INVALID because its any-cell
  exact-gold read-out was passable by a content-free perturbation (the shuffled
  control rescued 0.525 ≥ real 0.400). B″ replaces the read-out with
  **source-keyed counterfactual-pair discrimination** whose chance level is
  exactly 0.5 by construction and whose shuffled control **cannot exceed 0.5 in
  expectation** — the control fails by construction, per the ASM-0111
  successor-probe constraints. It also replaces the delivery operator: additive
  norm-matched contrastive injection instead of the measured-destructive
  final-position replacement transplant.
- **What this is NOT:** a freeze, a verdict-bearing run, a Stage-1 steering
  calibration, or a re-run of B′ (the B′ confound is structural; more items or
  seeds cannot fix it). nsk1 stays DRAFT. Every row is `phase:"exploratory"` —
  quarantined, uncitable, flips no verdict. B″ decides the registered
  post-B′ maintainer fork, nothing more. Freezing ever happens only through a
  redesigned nsk1 record (DRAFT → gates → skeptic memo → `prereg-freeze.py`),
  never off this run.
- **Sequencing authority:** the maintainer chose REDESIGN on 2026-07-10 and
  authorized the GPU run within the caps of §7. Spend fits the standing compute
  authorization (planning estimate well inside the ≤ USD 25 B′ envelope).

---

## 1. Premises (why this probe, on this cell)

- PREMISE: B′ is INSTRUMENT-INVALID with the confound mechanistically closed:
  conditional on the patch changing the output, gold-hit rate is ~0.43–0.53 in
  every (arm × source-layer) stratum, real and shuffled alike, so the any-cell
  exact-gold metric read perturbation FREQUENCY, not content; the shuffled
  control out-rescued the real arm 0.525 vs 0.400 (discordants 29 vs 4)
  [MEASURED: poc/nsk1/out/bprime/bprime_summary.json sha256
  539040e93c78ec244ad20f77ee32ab7cf19358add5033c525851cea799f1ef7c + recount in
  registry/assessments/nsk1-bprime.json; scope: R3 pinned checkpoint, entity
  form, 958 covered items, phase:exploratory].
- PREMISE: wholesale replacement transplant of a foreign-context vector into
  the final prompt position is destructive (98.5 percent mean correct-item cell
  breakage) and content-indifferent (real 0.040 vs deranged 0.050), so B″ must
  not use it [MEASURED: heatmap_breakage_c100 + rescue_p2/rescue_p2_ctrl in
  poc/nsk1/out/bprime/bprime_summary.json sha256
  539040e93c78ec244ad20f77ee32ab7cf19358add5033c525851cea799f1ef7c].
- PREMISE: the internal-write delivery cell remains UNTESTED — B′ licenses
  statements about its own operationalization only, and the successor probe
  must have a read-out a content-free perturbation cannot pass in expectation,
  with bounded cell multiplicity and a breakage-informed delivery operator
  [STIPULATED: ASM-0110 (scope rule) and ASM-0111 (constraint set); this spec
  is the object ASM-0111 binds].
- PREMISE: R3 = SmolLM2-1.7B-Instruct composes the entity form text-only at
  0.7912 on all 958 covered items (100/100 agreement with the G2d headroom
  vector), so the host-selection logic of ASM-0040 carries to B″ unchanged
  [MEASURED: poc/nsk1/out/bprime/bprime_rows.jsonl sha256
  f45b12e06ec7010d9148611f4dd11a833d69ecac4855d3452109ad8b76522ea4; scope:
  zero-shot, greedy fp32 chat template, this covered set, phase:exploratory].
- PREMISE: additive contrastive activation injection (difference of paired
  activations, added at low strength) is an established steering instrument
  class that preserves generation coherence at moderate strengths
  [LIT-BACKED: contrastive activation addition, arXiv:2312.06681 (2023)].
- PREMISE: token-level content transplanted between hidden states is readable
  out of mid-stack representations on larger hosts, which is the instrument-
  class precedent for a keyed read-out; the MAGNITUDE at 1.7B is an open
  projection used ONLY for floor/power sizing, never as evidence
  [STIPULATED: ASM-0204 registers it as a non-load-bearing EXTRAPOLATION with
  resolution path = this run; no line below premises a keying magnitude].
- The question B″ answers: **does a residual-stream write deliver
  item-specific CONTENT that the host's computation can read out** — the
  channel-existence half of the flagship's internal-vs-external question that
  B′ failed to measure? Keyed success = the model's top-vs-bridge preference
  tracks WHICH of two counterfactual sources was injected. A pass opens the
  nsk1 redesign at R3 around internal delivery; a kill retires the
  single-position additive internal-write instrument at the most favourable
  measured host with a measured reason; the role-control separates
  item-keyed delivery from generic role-direction steering.

## 2. Decisions (all fixed here; the runner decides nothing)

- DECISION: single host R3 = `HuggingFaceTB/SmolLM2-1.7B-Instruct`, resolved
  commit MUST equal the B′/G2d pin 31b70e2e869a7173562077fd711b654946d38674
  (ABORT otherwise); zero-shot, CLUTRR entity form (form 2) only; Modal 1×
  A10G, fp32, chat template, greedy `max_new_tokens=16` for all generations;
  batch 16 with OOM auto-halving; the B′ plumbing is reused wherever it is not
  explicitly superseded here [STIPULATED: ASM-0040 (host cell), ASM-0203
  (config carry-over is part of the disclosed contact discipline)].
- DECISION: item set = all 958 covered CLUTRR items (858 covered rows of
  `data/nsk1-clutrr/items.jsonl` sha256
  0e1f5c6bad6f97b575e3c354803713c3efef2a25cf76a9745e79b3d584f5839e + 100 rows
  of `data/nsk1-clutrr/headroom.jsonl` sha256
  8b8e99e48cce5fd40a8b7e858b4b75730c9a2d66e9237034f0d3b3b4468c4d8d), second
  disclosed pre-freeze contact [STIPULATED: ASM-0203].
- DECISION: gate read-out = source-keyed counterfactual-pair discrimination
  with a paired teacher-forced logprob margin; per-(item, cell) success bit =
  m(+) > m(−); ties/non-finite count as failure; coin-assigned deranged
  control (the null anchor, ≤ 0.5 in expectation by construction) plus a
  reported-only role-consistent deranged control [STIPULATED: ASM-0200].
- DECISION: delivery operator = additive norm-matched contrastive injection at
  the final prompt-token position, h_p ← h_p + s·α·‖h_p‖·(Δv/‖Δv‖), forward/
  prefill only; α picked by the mechanical calibration of §3 Step 5 from the
  ladder {0.125, 0.25, 0.5, 1.0}; replacement transplants are retired
  [STIPULATED: ASM-0201].
- DECISION: grid = 9 cells, ℓh ∈ {lay(1/2), lay(2/3), lay(5/6)} × ℓt ∈
  {lay(1/3), lay(1/2), lay(2/3)} with `lay(f)=min(L−1,max(1,round(f·L)))`
  (at L=24: ℓh ∈ {12,16,20}, ℓt ∈ {8,12,16}); pivot cell (lay(2/3), lay(1/2))
  = (16,12) for calibration and generation secondaries; floor 0.70 on keyed
  accuracy; Bonferroni-corrected any-cell PASS, all-cells KILL
  [STIPULATED: ASM-0202].
- DECISION: seeds — BPRIME2_SEED = 20260712 pins the σ₂ derangement (single-
  cycle Sattolo over Swept order), the C100 sample, and any 300-cap subsample;
  the per-(item, cell) coin bit is
  `int(sha256(("%d|%s|%d|%d" % (20260712, item_id, lh, lt)).encode()).hexdigest(), 16) & 1`
  — deterministic, auditable, content-independent [STIPULATED: ASM-0200].
- DECISION: outputs under `poc/nsk1/out/bprime2/` with gate label `BPRIME2`;
  every disc/baseline row stores BOTH raw candidate logprobs so the entire
  gate is recomputable offline without GPU; new entrypoint appended to
  `poc/modal/modal_nsk1_g2.py` (existing content byte-untouched) or a sibling
  `poc/modal/modal_nsk1_bprime2.py` reusing its helpers — runner's operational
  choice, disclosed in the summary [STIPULATED: ASM-0203].

## 3. Exact procedure

**Step 0 — prompts + donors.** Render the form-2 TEXT-ONLY prompt for every
covered item byte-identically to `_build_specs_bprime` (which is byte-verified
against `_build_specs_g2b` `f2_to`): question `"Who is the %s of %s?" %
(gold_surface, base)`, instruction `INSTRUCTION_ENTITY`, no feedback sentence.
Scorer for all generations = `_score_entity` byte-identical. For every item
build TWO donor sentences with the g2/g2b feedback renderer template:
`D_top = "Note: the %s of %s is %s." % (hop1-rel-surface, base, TOP)` and
`D_bridge = "Note: the %s of %s is %s." % (hop1-rel-surface, base, BRIDGE)` —
byte-identical except the answer-slot name. ASSERT (ABORT on failure): 3-name
pairwise-distinct per item; the two donors differ only in the name slot; the
headroom-100 rendered prompts byte-equal `_build_specs_g2b` `f2_to`. NOTE,
deliberate and disclosed: B′'s gold-not-in-feedback assert is WAIVED for
`D_top` only — the donor text is never shown to the model as prompt text for
the swept item; only its harvested activations are injected (Law 1 holds: no
raw kernel/encoder coordinates ever enter the model), and injecting the gold
identity is the point of the key=top arm. `D_top` is never used in any text
arm; there is no text arm.

**Step 1 — text-only pass + repro gate.** One prefill+generate per item (958
gens); no harvesting here (donor vectors come from donor forwards, Step 4).
REPRODUCIBILITY CHECK: compare the 958-item correctness vector against B′'s
`probe=="text-only"` rows in `poc/nsk1/out/bprime/bprime_rows.jsonl` (sha256
f45b12e06ec7010d9148611f4dd11a833d69ecac4855d3452109ad8b76522ea4); agreement
< 910/958 ⇒ ABORT (environment drift), report disagreements. `headroom_ok` =
acc(text-only) ∈ [0.05, 0.85] with ≥ 900 scored items.

**Step 2 — grid.** L = `config.num_hidden_layers` (ASSERT L ≥ 12; expected
24). Grid per §2 (9 cells; ASSERT |cells| ≤ 9 after dedup). Hook semantics
identical to B′: a forward-pre-hook on decoder module index ℓt edits the
residual carrying `hidden_states[ℓt]`; harvest at `hidden_states[ℓh]`.

**Step 3 — sets, derangement, coins.** F = text-only-wrong items; Swept = F if
|F| ≤ 300 else a seed-pinned uniform 300-sample (seed 20260712). C100 =
seed-pinned (20260712) uniform 100-sample of text-only-correct items (ASSERT
≥ 100 correct; disjoint from Swept by construction). C_cal = the first 32
items of C100 in ascending covered-set order. σ₂ = Sattolo derangement over
Swept order, seed 20260712, ASSERT fixed-point-free. Coin bits per §2.

**Step 4 — donor harvest.** For every item in Swept ∪ C100: tokenize each
donor RAW (no chat template), one forward pass each, harvest
`hidden_states[ℓh]` for all three ℓh at the LAST token of the LAST occurrence
of the donor's answer-slot name (tokenizer offset mapping; ASSERT found).
Per (item, ℓh): Δv = v_top − v_bridge; ASSERT ‖Δv‖ > 0; store the unit vector
Δ̂v = Δv/‖Δv‖ (fp32). ≈ 2 × 300 = 600 short forwards, no generation.

**Step 5 — α calibration (mechanical, pivot cell only).** For each α in
{0.125, 0.25, 0.5, 1.0}, each item in C_cal, each sign s ∈ {+1, −1}:
greedy-generate 16 tokens from the item's text-only prompt with the additive
hook at the pivot cell writing s·α·‖h_p‖·Δ̂v (own item's Δ̂v) into the final
prompt position at prefill (decode steps unhooked, seq==1 guard as in B′).
`collapse(α)` = fraction of the 64 generations containing NO per-item lexicon
surface (word-boundary, case-insensitive). α* = the LARGEST α with
collapse(α) ≤ 0.10; if none qualifies, α* = 0.125. Report the full table.
α* is used for EVERY subsequent injection. 256 generations.

**Step 6 — gate sweep (margins, no generation).** For each item i ∈ Swept and
cell (ℓh, ℓt), 8 teacher-forced forwards, batched:
- Candidate rows: `full_ids = prompt_ids + cand_ids` where `prompt_ids` =
  chat-template ids (add_generation_prompt=True) and `cand_ids = tok(" " +
  surface, add_special_tokens=False).input_ids` for surface ∈ {top_i,
  bridge_i} (ASSERT len ≥ 1). With left-padding to maxlen, the per-row write
  index is `w = maxlen − len(cand_ids) − 1`; ASSERT `input_ids[row][w] ==
  prompt_ids[−1]`. The hook adds `s·α*·‖h[row,w]‖·Δ̂v` to position w only.
- `lp(surface | v)` = Σ_j log_softmax(logits[row, w+j, :])[cand_ids[j]]
  (logits at w+j predict candidate token j). ASSERT all finite (ABORT on NaN).
- Margins: m(v) = lp(top_i | v) − lp(bridge_i | v). Arms from 8 forwards:
  REAL: v = ±α-scaled Δ̂v_i → m_r(+), m_r(−) (key=top ↦ +, fixed semantics).
  DERANGED: v = ±α-scaled Δ̂v_{σ₂(i)} → m_d(+), m_d(−); the COIN control and
  the ROLE control are both derived from these two margins (shared forwards):
  coin bit b=1 ⇒ key=top ↦ +, b=0 ⇒ key=top ↦ −; role control fixes
  key=top ↦ + always.
- Success bits (ties/non-finite = 0): real_i,c = [m_r(+) > m_r(−)];
  coin_i,c = [b==1 ? m_d(+) > m_d(−) : m_d(−) > m_d(+)];
  role_i,c = [m_d(+) > m_d(−)].
Baselines: per item one unhooked forward pair (both candidates), margins
stored. Same sweep, real + deranged arms only, on C100 (reported-only
discrimination on items where the computation succeeds). Cell order: pivot
first, then row-major (ℓh asc, ℓt asc); wall-guard checks between cells.
Volume at |Swept| = 200: 200×9×8 = 14,400 + C100 100×9×8 = 7,200 + baselines
600 ≈ 22,200 forwards.

**Step 7 — generation secondaries (reported-only, never gate-bearing).**
(a) Keyed emission + rescue at the pivot cell: for each i ∈ Swept, arms
{real, deranged-coin} × signs {+, −}: greedy 16-token generation under the
additive hook; record emitted-name category (top/bridge/other/none), `correct`
(exact `_score_entity` gold), and rescue = correct under the key=top sign.
800 generations. (b) Breakage: for each i ∈ C100, all 9 cells, real arm, both
signs: greedy generation; breakage = correct→wrong flip; also record the
no-lexicon-name collapse flag separately (damage vs steered-to-bridge is a
designer distinction, not a runner one). 1,800 generations.

**Volume + planning (|Swept| = 200 planning value = B′'s measured |F|):**
≈ 22,800 forwards + ≈ 3,814 generations ≈ 26.6k GPU calls, comparable to B′'s
32,958 generations, which cost 0.457 GPU-h / USD 0.503
[MEASURED: poc/nsk1/out/bprime/bprime_summary.json sha256
539040e93c78ec244ad20f77ee32ab7cf19358add5033c525851cea799f1ef7c].
Worst case (|Swept| = 300): ≈ 30k forwards + 4.6k generations.

## 4. Metrics (all computed in-run, mechanical; all recomputable from rows)

Per cell c and arm a ∈ {real, coin, role}: keyacc_a(c) = mean over Swept of
the success bits; tie counts reported per cell per arm. Wilson bounds on
keyacc: PASS-side one-sided LB at confidence 1 − 0.05/9 (z = 2.5427);
KILL-side one-sided UB at 95% (z = 1.6449); control-validity two-sided bound
at 1 − 0.05/(2·9) per side (z = 2.7730). Paired tests at each cell, real vs
each control: b = #(real ∧ ¬ctrl), c = #(¬real ∧ ctrl), one-sided exact
binomial p = P(X ≥ b | n = b+c, 0.5). Effect sizes (reported): mean and
median of [m(+) − m(−)] per cell per arm; baseline margin distribution.
Secondaries: keyed-emission rates, rescue real vs deranged at pivot, breakage
and collapse heatmaps on C100, the α calibration table. `headroom_ok` and the
repro tally per §3 Step 1.

## 5. Decision rule (pre-declared; fork-deciding gate labels, NOT verdicts)

Why the control fails by construction (the property B′ lacked): the coin
control's success bit equals a fair coin XOR a key-independent margin
ordering, so E[keyacc_coin] = 0.5·P(no tie) ≤ 0.5 exactly — for a content-free
perturbation of ANY magnitude. Perturbation frequency/magnitude, which fully
explained B′'s control advantage, has no path to keyed success here; only
key-locked content does. The role control is NOT a null anchor (a transferring
role-direction is content of a generic kind) — it is the mechanism separator.

Evaluated in order:

1. **INSTRUMENT-INVALID** iff any ABORT fired (commit-pin mismatch, repro
   drift < 910/958, donor/name-location or write-index assert, NaN margins),
   or NOT `headroom_ok`, or at ANY completed cell keyacc_coin's one-sided
   Wilson LB at z = 2.7730 exceeds 0.5 (a coin control statistically above
   chance means the construction itself is broken — seed leakage or plumbing —
   since its expectation is ≤ 0.5 by arithmetic).
2. **PASS-KEYED** iff at some completed cell: Wilson-LB(keyacc_real, z=2.5427)
   ≥ 0.70 AND paired real > coin (p < 0.05) AND paired real > role (p < 0.05).
   Family-wise error ≤ 9 × 0.05/9 = 0.05 by the corrected LB conjunct alone;
   the sign-test conjuncts only shrink the rejection region.
3. **CHANNEL-ROLE-ONLY** iff no cell meets rule 2 but some completed cell has
   Wilson-LB(keyacc_real, z=2.5427) ≥ 0.70 AND paired real > coin (p < 0.05)
   — i.e. strong keying that the role-consistent deranged control matches:
   the channel delivers at most generic role-direction content, not
   item-specific grounding.
4. **KILL-NO-USABLE-CHANNEL** iff all 9 cells completed AND at every cell
   Wilson-UB95(keyacc_real, z=1.6449) < 0.70.
5. Anything else: **INCONCLUSIVE** (report bounds; no adjective; maintainer
   fork on any extension — none fires automatically).

Decidability (design-time arithmetic, not evidence): at n = 200, observed
keyacc ≥ ~0.785 clears the corrected 0.70 LB (power ≈ 0.95 at true 0.83,
≈ 0.70 at true 0.80, per ASM-0204's sizing-only band); a dead channel (true
0.5) yields per-cell UB95 ≈ 0.558 < 0.70 with per-cell miss probability
~3×10⁻⁵, so KILL is near-certain when nothing keys anywhere; true keying in
(0.55, 0.78) lands INCONCLUSIVE — honestly, as a Stage-0 cheap gate should.
Partial runs (wall guard): PASS/CHANNEL-ROLE-ONLY may fire on completed cells
(the /9 correction is kept — conservative); KILL requires all 9; otherwise
INCONCLUSIVE with `partial:true`. Interpretation boundary, fixed now: a
PASS-KEYED establishes content DELIVERY (at least echo-grade readable
content); whether the computation integrates it as grounding is Stage-1's
question, and ASM-0042's latent-timing band is NOT resolved by any B″ outcome
(B″ probes deliverability, not latent rescuability; ASM-0112 IS resolved by
B″ per its own resolution path).

## 6. Outputs + custody

`poc/nsk1/out/bprime2/bprime2_rows.jsonl` — one row per GPU call:
`item_id`, `probe` ∈ {text-only, baseline, disc, disc-c100, calib, keyed-gen,
breakage}, `arm` ∈ {real, drg, null}, `sign` ∈ {1, −1, null}, `cell` [ℓh, ℓt]
(null where n/a), `alpha`, `coin` (deranged disc rows only), `lp_top`,
`lp_bridge` (margin rows), `gen`/`correct`/`emitted` (generation rows),
`gold`, `phase`:"exploratory", `gate`:"BPRIME2", `host`:"R3", `model`,
`surface`:"clutrr", `form`:"2".
`bprime2_summary.json` — config echo (model commit, L, grid, α ladder + table
+ α*, seeds, coin-bit recipe, caps), input pins (items/headroom sha256s of
§2), |F|, |Swept|, repro tally, all §4 metrics per cell per arm, the §5 gate
label + triggers, cost. Plus the run log. Runner reports sha256s of rows +
summary in the handoff and mechanical facts ONLY — interpretation, epistemic
tags, and the fork recommendation are designer work on these outputs
(run ≠ interpret).

## 7. Budget, infra, phase

Modal, 1× A10G, fp32. Planning estimate: 0.3–1.5 GPU-h ≈ **USD 0.4–2**
(from B′'s measured throughput; STIPULATED-grade planning, never a
measurement), comfortably inside the ≤ USD 25 B′ envelope. Hard caps
unchanged: **USD 25 / 10 GPU-h / 12 h wall-clock**; in-container soft wall
guard 19,800 s; foreground gates per the standing ops rule; abort-and-return
(partial outputs kept, labelled) on any cap trip. Phase: `exploratory` —
pre-freeze fork diagnostic under the same licence as G2/G2d/B′.

## 8. Post-B″ paths (pre-stated so the outcome cannot be re-narrated)

- PASS-KEYED → nsk1 redesign at R3: internal-arm primary with the keyed
  contrastive delivery mechanism, Stage-1 calibration (α/ℓ, carrier
  extraction, ASM-0025's extractability question) under a new/amended DRAFT
  record with rung logic and power redone by the designer; B′ AND B″ contact
  disclosed verbatim (ASM-0203 clause iv); 360M-few-shot stays the candidate
  second rung (ASM-0040 revisit clause).
- CHANNEL-ROLE-ONLY → registered maintainer fork: grounding-delivery redesign
  is NOT licensed; a generic role-steering line (cheaper mechanism, different
  claim) becomes a candidate under its own spec; the internal-write
  grounding cell records "role-generic transfer only" with measured backing.
- KILL-NO-USABLE-CHANNEL → the single-position additive internal-write
  instrument is retired at the most favourable measured host with a measured
  reason; the training-free internal-write family's retirement goes to the
  maintainer with a two-probe ledger (B′: instrument constraints; B″: no
  readable content at any of 9 mid-stack cells); the flagship redirects to
  engine-external topologies (K-NULL first) per the feasibility synthesis.
- INCONCLUSIVE / INSTRUMENT-INVALID → maintainer fork on any extension; no
  automatic spend; an INSTRUMENT-INVALID here would additionally falsify the
  coin-control construction and must be diagnosed before any successor spec.
