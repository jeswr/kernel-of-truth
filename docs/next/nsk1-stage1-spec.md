# nsk1 Stage-1 — free-generation KEYED-RESCUE probe at R3 (runner-ready spec)

- **Author:** Fable experiment-designer role, 2026-07-10. Successor to
  `docs/next/nsk1-bprime2-spec.md` (B″), commissioned at the post-B″ fork per
  the rank-1 recommendation of the B″ interpretation
  (`registry/assessments/nsk1-bprime2.json` `fork_recommendation`) and the
  Stage-1 sequencing gate (ASM-0342). Written under the honesty-guard; every
  load-bearing line tagged; new assumptions registered as ASM-0400..0404.
- **What this is:** the integration probe the B″ PASS-KEYED result licenses
  and requires. B″ established that a residual-stream write DELIVERS
  item-specific content readable at echo grade (teacher-forced logprob
  margin) at exactly two grid cells. It did NOT measure whether internally
  delivered grounding INTEGRATES — whether it helps the model actually
  GENERATE the correct answer on items it otherwise fails — because the B″
  generation secondaries were spec-fixed at the pivot cell, which the margin
  sweep measured dead. Stage-1 measures free-generation keyed emission and
  keyed RESCUE of text-only failures at the two measured keying cells only,
  over an α ladder below 1.0 (the keying-vs-damage frontier), with three
  derangement seeds (control independence) and the role-consistent arm as
  covariate/control.
- **What this is NOT:** a freeze, a verdict-bearing run, a new grid search, a
  scale successor, or a campaign calibration. nsk1 stays DRAFT. Every row is
  `phase:"exploratory"` — quarantined, uncitable, flips no verdict. Stage-1
  decides the registered post-B″ fork (rank-1 sequencing) and discharges
  ASM-0342 when it reads out; freezing ever happens only through a redesigned
  nsk1 DRAFT record with its own gates and skeptic memo, never off this run.
- **Sequencing authority:** ASM-0342 makes this probe the binding next
  measurement in the nsk1 line; spend fits the standing compute authorization
  (planning estimate well inside the ≤ USD 25 B″-class envelope, target band
  USD 1–5). The runner executes; the runner decides nothing (§2); mechanical
  facts come back to the designer for interpretation (run ≠ interpret).

---

## 1. Premises (why this probe, at these cells, with these arms)

- PREMISE: B″ is PASS-KEYED on a valid instrument: keyed accuracy 0.810/0.850
  at (ℓh,ℓt) = (12,16)/(16,16) vs coin 0.510/0.505 (paired p 1.35e-10 /
  4.11e-13) and role 0.595/0.580 (p 8.87e-07 / 9.06e-11), FWER ≤ 0.05 over 9
  cells; every ℓt ∈ {8,12} cell dead (real 0.42–0.50 ≈ coin), (20,16)
  attenuated (0.605, ns after correction); margin effect m(+)−m(−) real
  +2.82/+2.80 vs role +0.59/+0.81 vs coin ≈ 0
  [MEASURED: poc/nsk1/out/bprime2/bprime2_summary.json sha256
  0ee800f7f7d1aec0aa245986aa9a27a15017ebc33d5780a9cb4104da366f76f1; scope: R3
  pinned checkpoint, entity form, α=1.0, teacher-forced margins, n=200,
  phase:exploratory].
- PREMISE: keyed free-generation rescue at the two keying cells is UNMEASURED
  — the B″ generation secondaries (keyed emission + rescue, real+ 22/200 vs
  deranged+ 33/200) ran at the pivot (16,12), which the margin sweep measured
  dead (real 0.46 ≈ coin 0.455), so they are uninformative about the pass
  cells; the B″ PASS licenses content-delivery statements only, never
  "internal steering fixes answers" [STIPULATED: ASM-0340 (the B″ scope
  rule); measured backing inside its register entry].
- PREMISE: free-generation breakage at the keying cells is sign-asymmetric
  toward the injected identity at α=1.0: minus sign (toward bridge) breaks
  32/100 and 34/100 correct items with 28 and 26 of the broken generations
  emitting the bridge name, plus sign breaks 16/100 and 13/100; no such
  asymmetry at dead cells; name-emission collapse at α=1.0 is 0.0156
  (calibration) and 0–4 per 200 (C100 cells) — content survives into
  generation at the keying cells, at a measured damage floor of 13–16 percent
  even under the helpful sign
  [MEASURED: poc/nsk1/out/bprime2/bprime2_rows.jsonl sha256
  dadabaaea914485e387b9c1f558f5f938a7b9905159b35000957aea2a340eeba (breakage +
  calib rows; recount in registry/assessments/nsk1-bprime2.json); same scope].
- PREMISE: keying below α=1.0 is unmeasured — the B″ α ladder calibrated
  name-collapse only (collapse 0 at α ≤ 0.5, 0.0156 at 1.0) and every margin
  was taken at α*=1.0, so the keying-vs-damage frontier (does keying survive
  at strengths where the plus-sign damage fades?) is open in both directions
  [MEASURED: poc/nsk1/out/bprime2/bprime2_summary.json sha256
  0ee800f7f7d1aec0aa245986aa9a27a15017ebc33d5780a9cb4104da366f76f1
  (alpha_table); the frontier-openness consequence is part of ASM-0340's
  scope bounds].
- PREMISE: the B″ control robustness rests on a single derangement seed
  (σ₂ = Sattolo, seed 20260712) — the cheapest remaining attack on the B″
  reading — and the role control sits mildly elevated (0.55–0.595 at 6 of 9
  Swept cells), a candidate generic role-direction transfer that Stage-1 must
  carry as a measured covariate rather than leave ambiguous
  [MEASURED: poc/nsk1/out/bprime2/bprime2_summary.json sha256
  0ee800f7f7d1aec0aa245986aa9a27a15017ebc33d5780a9cb4104da366f76f1
  (per_cell_metrics keyacc_role); the carry-as-covariate consequence is the
  ASM-0342 sequencing clause].
- PREMISE: the text-channel comparator on the same items and host is measured
  net-harmful: the same fact class delivered as prompt text drove correct→
  wrong at scale with zero rescues (g2d: 0.76 → 0.43, 0/24 rescued), so
  "deliver the fact as text" is not the alternative hypothesis Stage-1 needs
  to beat — the open question is whether the INTERNAL channel, the only
  measured-positive delivery mode, integrates
  [MEASURED: poc/nsk1/out/g2d/g2d_summary.json sha256
  93a6e951f6f8c9bcf648f704686c289241a5ac3238955df9d9846336b10b12d0; scope:
  R1/R2/R3 text-delivery cells, phase:exploratory].
- PREMISE: donor semantics are construction-verified in the committed B″
  harness: D_bridge is byte-equal to the g2/g2b/g2d feedback sentence — the
  TRUE hop-1 fact "Note: the <hop1-rel> of <base> is <BRIDGE>." — and D_top
  is the same frame with the answer slot holding TOP (the 2-hop gold
  surface), donors byte-identical except the name slot (asserted per item);
  Δv = v_top − v_bridge, so sign +1 pushes toward the gold-name-in-fact-frame
  counterfactual and sign −1 pushes toward the true hop-1 fact
  [MEASURED: poc/modal/modal_nsk1_g2.py sha256
  b524ff574e82877ae11022c9cb7024d80530fcc0796cacf1e0bb035d4f21abbc
  (_build_specs_bprime2 asserts, run committed at b404754); scope: this
  harness, this corpus].
- The question Stage-1 answers: **does internally delivered grounding
  INTEGRATE into the host's computation — does it rescue free-generation
  failures content-specifically?** Two pre-separated readings (§2, ASM-0404):
  rescue under the −(true-fact) sign is integration-grade (echo of the
  injected identity yields BRIDGE, which is wrong — only using the fact to
  compose the 2-hop answer yields gold), while rescue under the +(gold-name)
  sign is emission-grade (echo-confounded: the pushed name IS the gold
  surface). The deranged-coin arm anchors content-free rescue; the
  role-consistent arm separates item-specific content from generic
  role-direction help. A pass makes the redesigned nsk1 DRAFT record's rung
  logic real (powered by measured rescue rates, per ASM-0342); a kill
  redirects the internal-write line toward read-out placement with a measured
  reason; either way the record is written once, on measurements.

## 2. Decisions (all fixed here; the runner decides nothing)

- DECISION: host, config, corpus, prompts, donors, scorer, injection
  operator, and hook mechanics are carried over from B″ UNCHANGED: R3 =
  SmolLM2-1.7B-Instruct at commit pin 31b70e2e869a7173562077fd711b654946d38674
  (ABORT otherwise), zero-shot CLUTRR entity form (form 2), all 958 covered
  items (same input-pin sha256s as B″ §2, ABORT on drift), Modal 1× A10G fp32
  chat template, greedy `max_new_tokens=16`, batch 16 with OOM auto-halving,
  specs built by `_build_specs_bprime2()` verbatim including all its asserts,
  additive norm-matched contrastive injection h_p ← h_p + s·α·‖h_p‖·Δ̂v at
  the final prompt-token position, prefill only, per the B″ operator
  [STIPULATED: ASM-0400; operator per ASM-0201, read-out family per
  ASM-0200, host per ASM-0040].
- DECISION: cells = the two measured keying cells ONLY, hard-fixed as
  (ℓh,ℓt) ∈ {(12,16), (16,16)} with ASSERT L == 24; no grid derivation, no
  new cell search (7 of 9 B″ cells are cleanly dead twice over — Swept and
  disc-c100) [STIPULATED: ASM-0400].
- DECISION: α ladder = {0.25, 0.5, 0.75, 1.0}, all four run at both cells for
  margins, rescue, and breakage. 1.0 is the anchor (the only measured keying
  strength — dropping it would leave rescue at the measured keying point
  unmeasured); 0.75/0.5/0.25 descend through the band where name-collapse is
  measured ≈ 0 but keying and damage are unmeasured; 0.125 is dropped (B″'s
  margin effect already attenuates sharply off-peak, and the frontier
  question lives in the upper half of the ladder). No α* selection step —
  the ladder itself is the design variable [STIPULATED: ASM-0400].
- DECISION: item sets — F = text-only failures of THIS run; Swept = F when |F|
  is ≤ 300, else a seed-pinned uniform 300-sample (seed 20260712); C100 =
  seed-pinned (20260712) uniform 100-sample of text-only-correct items,
  disjoint from Swept (ASSERT). Report `swept_overlap_bprime2` (count of
  Swept items also in B″'s swept_item_ids) — reported, never gated
  [STIPULATED: ASM-0400; contact discipline ASM-0402].
- DECISION: derangement seeds = THREE independent Sattolo derangements over
  Swept ascending order: σ_a (seed 20260712 — reproduces B″'s σ₂ exactly iff
  Swept is identical), σ_b (seed 20260713), σ_c (seed 20260714); ASSERT each
  fixed-point-free; report pairwise agreement counts. Per-(seed, item, cell)
  coin bit =
  `int(sha256(("%d|%s|%d|%d" % (seed, item_id, lh, lt)).encode()).hexdigest(), 16) & 1`
  — the B″ recipe with the derangement seed in the seed
  slot; α-independent (one bit per seed×item×cell, reused across the ladder)
  [STIPULATED: ASM-0400; recipe family per ASM-0200].
- DECISION: arms and shared-generation controls — per item × cell × α:
  REAL arm generates under s ∈ {+1, −1} with the item's own Δ̂v (2 gens);
  DERANGED arm generates under s ∈ {+1, −1} with Δ̂v_{σ_s(i)} for each of
  the three seeds (6 gens). The COIN control series (content-free null: coin
  bit picks which deranged generation counts) and the ROLE control series
  (role-consistent: fixed sign mapping, + for the plus endpoint, − for the
  minus endpoint) are both DERIVED from the same six deranged generations —
  no extra GPU calls [STIPULATED: ASM-0400].
- DECISION: two rescue endpoints with pre-fixed sign semantics — R− (
  "integration rescue": correct generation under real −, the true-hop-1-fact
  direction; echo cannot pass it; conservative because the name-push works
  against the gold surface) and R+ ("delivered-conclusion rescue": correct
  generation under real +, the gold-name direction; echo-confounded; never
  licenses integration claims). Both scored by `_score_entity` byte-verbatim
  against gold = top. The two endpoints carry separate gate labels (§5) and
  separate claim boundaries fixed NOW so the outcome cannot be re-narrated
  [STIPULATED: ASM-0404].
- DECISION: gate statistics — paired exact one-sided sign tests on discordant
  items (as B″); Bonferroni families = the 8 (cell × α) combos PER ENDPOINT,
  coin-conjunct threshold p < 0.05/8 = 0.00625 required at ALL THREE seeds;
  role conjunct p < 0.05 at all three seeds (mechanism separator, raw as in
  B″); effect floors mean_s Δ_s ≥ 0.10 AND min_s Δ_s ≥ 0.05 where Δ_s =
  rescue_real − rescue_coin_s = (b_s − c_s)/n; KILL margin = per-combo UB95
  (Δ̄ + 1.6449·max_s SE_s) < 0.10 at every combo, SE_s =
  sqrt(b_s + c_s − (b_s − c_s)²/n)/n; keying-replication check at α=1.0 with
  the B″ floor 0.70 on margin keyacc (UB95, z=1.6449); control-validity
  tripwire z = 3.2790 (two-sided 0.05 over the 48 coin series × 2 sides) on
  both margin-coin and emission-coin; ties/non-finite/empty generations count
  as failure everywhere [STIPULATED: ASM-0401].
- DECISION: outputs under `poc/nsk1/out/stage1/` with gate label `NSK1-S1`;
  every margin/baseline row stores both raw candidate logprobs (gate
  recomputable offline); every generation row stores the full generation,
  emission category, and correctness bit; new entrypoint appended to
  `poc/modal/modal_nsk1_g2.py` (existing content byte-untouched) or a sibling
  module reusing its helpers — runner's operational choice, disclosed in the
  summary [STIPULATED: ASM-0402].

## 3. Exact procedure

**Step 0 — build.** `specs = _build_specs_bprime2()` verbatim (958 items,
prompts, D_top/D_bridge donors, all build asserts, input-pin asserts as in the
B″ entrypoint, byte-equality check vs `_build_specs_g2b` f2_to). Scorer =
`_score_entity` byte-verbatim. ABORT on any assert breach.

**Step 1 — text-only pass + repro gate.** One greedy generation per item (958
gens). REPRODUCIBILITY CHECK: compare the 958-item correctness vector against
B″'s `probe=="text-only"` rows in `poc/nsk1/out/bprime2/bprime2_rows.jsonl`
(sha256 dadabaaea914485e387b9c1f558f5f938a7b9905159b35000957aea2a340eeba);
agreement < 910/958 ⇒ ABORT (environment drift), report disagreements.
`headroom_ok` = acc(text-only) ∈ [0.05, 0.85] with ≥ 900 scored items.

**Step 2 — cells.** ASSERT `config.num_hidden_layers == 24`. Cells =
[(12,16), (16,16)] literal (per §2). Hook semantics identical to B″: additive
pre-hook on decoder module ℓt at the final prompt-token position, prefill
only (seq==1 guard), norm-matched.

**Step 3 — sets, derangements, coins.** F, Swept, C100 per §2 (seed
20260712); ASSERT Swept ∩ C100 = ∅ and |C100| = 100. σ_a/σ_b/σ_c = Sattolo
over Swept ascending order with seeds 20260712/20260713/20260714; ASSERT each
fixed-point-free; compute the per-(seed, item, cell) coin bits per §2. Report
`swept_overlap_bprime2` and pairwise σ agreement counts.

**Step 4 — donor harvest.** For every item in Swept ∪ C100: tokenize each
donor RAW, one forward per donor, harvest `hidden_states[ℓh]` for ℓh ∈
{12, 16} at the last token of the last occurrence of the donor's answer-slot
name (offset mapping; ABORT if not found). Δv = v_top − v_bridge per (item,
ℓh); ASSERT ‖Δv‖ > 0; store Δ̂v (fp32 unit). ≈ 2×|Swept ∪ C100| ≈ 600
forwards, no generation.

**Step 5 — baselines.** Unhooked teacher-forced candidate-pair logprobs for
every item in Swept ∪ C100 (both candidates; ≈ 600 forwards); margins stored;
ABORT on non-finite.

**Step 6 — per-α tiers, α DESCENDING [1.0, 0.75, 0.5, 0.25]; within each α,
cells in order [(12,16), (16,16)]; wall-guard check between (α, cell) units.**
For each (α, cell) unit, in this order:

- (6a) **Margin sweep (Swept).** Per item, teacher-forced candidate-pair
  logprobs under the additive hook at position w = maxlen − len(cand) − 1
  (write-index ASSERT as B″): REAL ± (4 forwards), DERANGED ± per seed
  (12 forwards). Margins m(v) = lp(top|v) − lp(bridge|v); success bits
  real = [m_r(+) > m_r(−)], role_s = [m_d,s(+) > m_d,s(−)], coin_s = role_s
  XOR-flipped by the seed-s coin bit; ties/non-finite = failure (ABORT on
  NaN). 16 forwards per item per unit.
- (6b) **Rescue generations (Swept).** Greedy 16-token generations under the
  hook: REAL +, REAL −, and DERANGED ± for each of the three seeds (8 gens
  per item per unit). Per generation record `gen`, emission category
  (`_emit_cat`: top/bridge/other/none), and `correct` (`_score_entity`).
  Derived bits per item: R+_real, R−_real; per seed s: K_s = correct(deranged
  generation at the coin-s-chosen sign), role+_s = correct(deranged, +),
  role−_s = correct(deranged, −); keyed-emission bits per §4.
- (6c) **Breakage generations (C100).** REAL ± greedy generations (2 gens per
  item per unit); breakage = correct→wrong flip; collapse = no per-item
  lexicon surface emitted; bridge-emission count under − reported (the B″
  sign-asymmetry, now on the frontier).

**Volume + planning (|Swept| = 200 planning value = B″'s measured |F|; worst
case 300):** generations = 958 + 200×2×4×8 (rescue 12,800) + 100×2×4×2
(breakage 1,600) ≈ 15,358 (worst 21,758); forwards = donors ≈ 600 (worst
800) + margins 200×2×4×16 = 25,600 (worst 38,400) + baselines ≈ 600 (worst
800) ≈ 26,800 (worst 40,000). Generation-heavy: ≈ 1.9× B″'s measured
call-mix, planning band §7.

## 4. Metrics (all computed in-run, mechanical; all recomputable from rows)

Per (cell, α):

- **Margins:** keyacc_real, keyacc_coin_s, keyacc_role_s (per seed), tie
  counts, mean/median m(+)−m(−) per arm; Wilson UB95(keyacc_real, z=1.6449)
  (replication read at α=1.0); Wilson LB(keyacc_coin_s, z=3.2790)
  (validity tripwire). Baseline margin distribution once (Step 5).
- **Rescue:** rescue_real_plus, rescue_real_minus; per seed: rescue_coin_s,
  rescue_role_plus_s, rescue_role_minus_s; per endpoint e ∈ {plus, minus}
  and seed: paired b_es/c_es and exact one-sided p vs coin and vs the
  endpoint's role series; Δ_es = (b_es − c_es)/n vs coin; SE_es and UB95 per
  §2; the per-combo pooled UB (Δ̄ + 1.6449·max_s SE_s).
- **Keyed emission (reported endpoint, never rescue-gate-bearing):**
  strict-both bit f(x, y) = [cat(x)=="top" AND cat(y)=="bridge"];
  keyem_real = f(gen_real+, gen_real−); keyem_role_s = f(gen_drg_s+,
  gen_drg_s−); keyem_coin_s = f applied in coin-s order (bit=1 keeps the
  (+,−) order, bit=0 swaps) — E[keyem_coin] ≤ 0.5 by arithmetic since
  f(x,y)·f(y,x) = 0 for any fixed pair; Wilson LB(keyem_coin_s, z=3.2790)
  is the second validity tripwire; paired real-vs-coin and real-vs-role sign
  tests reported. Full emission-category tables per arm × sign.
- **Damage frontier (C100):** breakage and collapse counts per sign;
  bridge-emission count under −.
- `headroom_ok`, repro tally, `swept_overlap_bprime2`, σ pairwise agreement,
  per-step timing, cost.

## 5. Decision rule (pre-declared; fork-deciding gate labels, NOT verdicts)

Why the controls carry the content question: the deranged arms deliver a
same-operator, same-norm, same-role-frame write whose content belongs to a
WRONG item (fixed-point-free), so any content-free rescue mechanism
(perturbation kicks the model out of a wrong basin — exactly what B″ measured
at the dead pivot, deranged 33/200 ≥ real 22/200) appears in the coin series
in expectation; the coin sign-assignment removes the one asymmetry a deranged
vector retains (its own role direction), and the role series measures that
retained asymmetry explicitly. Rescue that beats BOTH, at three independent
derangements, with the −(true-fact) endpoint, cannot be produced by
perturbation frequency, generic role steering, or name echo.

FIRE(e, cell, α) for endpoint e ∈ {minus, plus} iff the (cell, α) unit
completed AND: (i) ∀ seed s: paired exact one-sided p(real_e > coin_s) <
0.00625; (ii) ∀ s: p(real_e > role_e_s) < 0.05; (iii) mean_s Δ_es ≥ 0.10 AND
min_s Δ_es ≥ 0.05. Family-wise error per endpoint ≤ 8 × 0.05/8 = 0.05 by the
Bonferroni conjunct alone (the all-seeds requirement and the other conjuncts
only shrink the rejection region).

Evaluated in order:

1. **INSTRUMENT-INVALID** iff any ABORT fired (commit pin, input pins, build
   asserts, L ≠ 24, name-location, Δ = 0, write-index, NaN margins,
   derangement fixed point, C100 short, repro < 910/958), or NOT
   `headroom_ok`, or at ANY completed unit and seed a validity tripwire
   fires: Wilson-LB(keyacc_coin_s, z=3.2790) > 0.5 or
   Wilson-LB(keyem_coin_s, z=3.2790) > 0.5 (both series are ≤ 0.5 in
   expectation by arithmetic; a statistical exceedance means broken
   plumbing, not signal).
2. **KEYING-NOT-REPLICATED** iff the α=1.0 margin sweeps completed at both
   cells AND at BOTH cells Wilson-UB95(keyacc_real at α=1.0, z=1.6449) <
   0.70. B″'s core measurement failing to reproduce is the finding; all
   rescue metrics are still reported but no rescue label may fire on a run
   where delivery itself is absent.
3. **PASS-INTEGRATION-RESCUE** iff FIRE(minus, cell, α) at some completed
   unit — internally delivered TRUE-fact content rescues failures it cannot
   rescue by echo, content-specifically, beyond both controls at all three
   derangements.
4. **PASS-EMISSION-RESCUE-ONLY** iff no minus-endpoint fire but FIRE(plus,
   cell, α) at some completed unit — content-specific delivered-conclusion
   rescue (echo-confounded by construction; the claim boundary of ASM-0404
   applies verbatim).
5. **ROLE-RESCUE-ONLY** iff no FIRE anywhere, but some completed unit and
   endpoint satisfies (i) + (iii) while failing (ii) — rescue beyond the
   content-free null that the role-consistent control matches: generic
   role-direction help, not item-specific grounding.
6. **KILL-NO-KEYED-RESCUE** iff all 8 units completed AND for BOTH endpoints
   at EVERY unit the pooled UB95 (Δ̄ + 1.6449·max_s SE_s) < 0.10 — the
   channel delivers (label 2 did not fire) but the content-specific rescue
   increment is bounded below campaign-usable size everywhere on the
   measured frontier: echo without integration, with a measured reason to
   redirect.
7. Anything else: **INCONCLUSIVE** (report all bounds; no adjective;
   `partial:true` on a wall-cap trip; maintainer fork on any extension —
   none fires automatically).

Decidability (design-time arithmetic, not evidence; sizing prior ASM-0403):
at n = 200 with a content-free rescue band ≈ 0.10–0.17 (measured at the dead
pivot at α=1.0, extrapolated here sizing-only), the per-seed coin conjunct at
p < 0.00625 fires with probability ≈ 0.98 at true Δ = 0.20, ≈ 0.84 at Δ =
0.15, ≈ 0.45–0.57 at Δ = 0.10; the all-three-seeds conjunction (positively
correlated through the shared real arm) is reliable at Δ ≳ 0.15 and lands
INCONCLUSIVE-prone in Δ ∈ (0.05, 0.15) — honestly, as a bounded exploratory
probe should. The KILL side: per-seed SE ≈ 0.036 at those base rates, so a
true-zero world clears each unit's UB95 < 0.10 with probability ≈ 0.88–0.98
and the 16-way conjunction is conservative — a true-nothing world may land
INCONCLUSIVE with tight reported bounds rather than KILL; KILL never fires
against a true Δ ≥ 0.10 at any unit except with vanishing probability. The
keying-replication check: at B″'s measured 0.81–0.85 the per-cell UB95 falls
below 0.70 with negligible probability; at a truly dead 0.5 channel it falls
below 0.70 near-certainly (per-cell miss ≈ 3e-5, B″ arithmetic). Partial
runs: labels 3–5 may fire on completed units (corrections kept — 
conservative); label 6 requires all units; label 2 requires both α=1.0
margin sweeps.

Interpretation boundary, fixed now (ASM-0404): PASS-INTEGRATION-RESCUE
licenses "internally delivered true-fact grounding integrates into free
generation at R3 at the measured cells" at MEASURED-exploratory grade within
this run's scope (one host, one form, one task family, one operator/position,
these α, n ≤ 300, quarantined) and nothing wider; PASS-EMISSION-RESCUE-ONLY
licenses only content-specific delivered-conclusion emission (an
engine-verified-answer use-mode candidate) and NEVER an integration or
grounding-composition claim; no label resolves ASM-0042's latent-timing band
beyond its own scope; no label is a verdict or feeds a freeze without the
redesigned DRAFT record and its own gates.

## 6. Outputs + custody

`poc/nsk1/out/stage1/stage1_rows.jsonl` — one row per GPU call: `item_id`,
`probe` ∈ {text-only, baseline, margin, rescue-gen, breakage}, `arm` ∈
{real, drg, null}, `sign` ∈ {1, −1, null}, `cell` [ℓh, ℓt] (null where n/a),
`alpha`, `seed` (derangement seed on drg rows; null elsewhere), `coin`
(drg rows: that seed's bit), `lp_top`/`lp_bridge` (margin + baseline rows),
`gen`/`correct`/`emitted` (generation rows), `gold`, `phase`:"exploratory",
`gate`:"NSK1-S1", `host`:"R3", `model`, `surface`:"clutrr", `form`:"2".
`stage1_summary.json` — config echo (pins, cells, ladder, seeds, coin recipe,
z values, floors, caps), input pins, |F|/|Swept|/|C100|, repro tally,
`swept_overlap_bprime2`, σ agreement, all §4 metrics per unit, the §5 gate
label with per-trigger booleans, cost. Plus the run log. Runner reports
sha256s of rows + summary and mechanical facts ONLY — interpretation,
epistemic tags, and the fork recommendation are designer work on these
outputs (run ≠ interpret).

## 7. Budget, infra, phase

Modal, 1× A10G, fp32. Planning estimate from B″'s measured throughput
(0.206 GPU-h for ≈ 22k calls, generation-light): Stage-1's mix ≈ 15.4k gens
+ 26.8k forwards (worst 21.8k + 40k) ≈ **0.4–1.5 GPU-h ≈ USD 0.5–2**
(STIPULATED-grade planning, never a measurement), inside the target band
USD 1–5. Hard caps unchanged from B″: **USD 25 / 10 GPU-h / 12 h
wall-clock**; in-container soft wall guard 19,800 s; α-descending execution
order guarantees the α=1.0 anchor (replication + rescue at the measured
keying strength) completes first; abort-and-return (partial outputs kept,
labelled) on any cap trip. Foreground gates per the standing ops rule.
Phase: `exploratory` — pre-freeze fork diagnostic under the same licence as
G2/G2d/B′/B″; third disclosed contact with the covered corpus (ASM-0402).

## 8. Post-Stage-1 paths (pre-stated so the outcome cannot be re-narrated)

Any label except INSTRUMENT-INVALID discharges ASM-0342 per its own revisit
condition (the Stage-1 probe has read out); the fork below is the
maintainer's.

- PASS-INTEGRATION-RESCUE → the redesigned nsk1 DRAFT record (the B″ §8 PASS
  path): internal-arm primary, rung logic and power derived from the MEASURED
  rescue rates at the fired units, all three corpus contacts (B′, B″, S1)
  disclosed verbatim with the skeptic memo attacking them (ASM-0203 clause iv
  via ASM-0402), 360M-few-shot as candidate second rung (ASM-0040 revisit),
  ASM-0025 extractability at that record's calibration stage.
- PASS-EMISSION-RESCUE-ONLY → maintainer fork: a DRAFT record limited to the
  delivered-conclusion use-mode (engine-verified answer delivered internally)
  under ASM-0404's boundary; the integration question redirects to read-out
  placement / multi-position / fact-frame operator designs under a new spec,
  not more spend on this operator.
- ROLE-RESCUE-ONLY → grounding-delivery claims blocked; a generic
  role-direction steering line becomes a candidate under its own spec
  (mirrors B″'s CHANNEL-ROLE-ONLY path).
- KEYING-NOT-REPLICATED → the B″ single-run fragility is itself the measured
  finding; diagnosis (environment drift vs run fragility — the repro gate
  bounds the former) before ANY successor spend; maintainer fork.
- KILL-NO-KEYED-RESCUE → echo-without-integration is measured at the only
  positive delivery cells: the internal-write GROUNDING line pauses with a
  two-stage ledger (B″: delivery positive; S1: integration bounded < 0.10
  everywhere measured), the flagship redirects toward engine-external
  topologies per the feasibility synthesis, and any revival requires a new
  operator/read-out family, not a re-run.
- INCONCLUSIVE / INSTRUMENT-INVALID → maintainer fork on any extension; no
  automatic spend; an INSTRUMENT-INVALID from a validity tripwire would
  impeach the coin construction itself and must be diagnosed before any
  successor spec.
