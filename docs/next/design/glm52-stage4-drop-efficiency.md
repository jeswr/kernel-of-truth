# GLM-5.2 Stage-4 expert-drop efficiency — glm-s4drop-0 pre-registration (designer-15 R1, designer-18 R2, 2026-07-16)

Bead kernel-of-truth-1xqd.2 (fix wave: kernel-of-truth-84gg). The DECISIVE kill-or-validate for
"expert-drop as a real throughput lever" on the GLM-5.2 int4 / colibri estate. R1 was redesigned per
the GPT-5.6 dual-model review and frozen 2026-07-16; the pre-run CROSS-MODEL review returned HOLD
(estimand confound + spurious-verdict paths + a layer-count bug + power/budget defects, §11) and R2
fixes ALL of them under the lawful pre-final reset-refreeze window (no results-log row of any phase
exists; the id is not GNG-0-signed; correction record registry/corrections/glm-s4drop-0/).
UNCOMMITTED — the coordinator commits; the runner executes AFTER prereg-freeze. This document is
both the prereg doc and the analysis plan of registry record `glm-s4drop-0` (kot-reg/1).

- PREMISE: Stage-3 produced a 16-cell skiplist from individually-ablated cells at a stipulated 0.05
  nats/tok mean-ΔNLL line on an enriched gate-failed-atlas shortlist; no population rate, no
  simultaneous-drop guarantee, zero deterministic-replaceable cells. [STIPULATED: ASM-2383]
- PREMISE: the review's six design requirements (telemetry cost weighting, joint masks, matched
  removed-I/O blind, disjoint suite, one Pareto primary, separate remap arm) are adopted verbatim
  as requirements. [STIPULATED: ASM-2384]
- PREMISE: stage-3 measured cost basis ~$1.15/h, ~11.0 s/prefill on the pinned OCI config.
  [MEASURED: poc/glm52-probe/stage3/results/full_run.log sha256 bf7faad49e62118edb2232379b0e04c866b3ce09d9a01f9f878ff6de27acc595]
- PREMISE: the MoE trunk has 76 sparse MoE layers, 3..78 INCLUSIVE. [MEASURED: ASM-2342 R3
  amendment — committed stats files span layers 3-78; the R1 builder hard-coded 3..77 (75 layers),
  review finding C1, fixed in R2]

## §1 Question, ESTIMAND, and hypotheses

Q: Is the Stage-4 COMPOSITE expert-drop mask a REAL throughput lever — i.e., at a removed-I/O dose
big enough to matter, does the composite (causal-core + atlas-extension) mask preserve more quality
than a deployable concept-free blind mask that removes the SAME measured I/O, while actually
decoding faster than baseline?

DECISION — estimand option (b) of the cross-model review, adopted with honest labelling
[STIPULATED: ASM-2397]: the primary contrast is **"the Stage-4 composite mask (22 causally-validated
cells + the UNVALIDATED atlas rare/unseen cost-weighted extension) vs the deployable
ascending-frequency blind mask at matched removed I/O"**. It does NOT isolate causal evidence per
se: the composite consumes ~2 orders of magnitude more routing evidence (480-probe atlas + 244-item
causal data) than the blind arm's 3,072-token telemetry, and the atlas extension supplies almost
all of the dose. Every licensed sentence names the composite; no sentence of the form "causal
evidence beats frequency ranking" is licensed by any outcome. Option (a) — restricting SEM-D to the
22 causally-validated cells at matched telemetry — was REJECTED as physically undoseable: those
cells carry ~0.1% of decode expert-miss-I/O (full-scale mock estimate: 16-cell core = 0.06%,
SYNTHETIC telemetry, STIPULATED), so an (a)-design fires kill trigger 2 by construction — a verdict
fixed in advance, which the no-spurious-verdict discipline forbids.

- **H-P (primary, falsifiable):** at matched removed miss-bytes/token (registered dose, §3.3), the
  composite mask `s4-semd` beats the frequency-heuristic blind mask `s4-bldf-d` on paired per-item
  quality by ≥ +0.05 nats/target-token (one-sided 95% lower bound > 0 AND T ≥ +0.05). The pre-named
  null (stated, not asserted): on a cache-constrained box the miss tail IS the rare tail, so
  frequency-blind and composite masks largely coincide in effect and the contrast ties → the
  composite pipeline adds nothing deployable over colibri's existing concept-free heuristic. Under
  the R2 decision rule this null KILLS when the data AFFIRM it (one-sided 95% upper bound < +0.05),
  and resolves INCONCLUSIVE when the data merely fail to resolve it (§5.2, §7).
- **H-J (joint safety):** dropping all 16 skiplist cells SIMULTANEOUSLY is quality-safe:
  mean ΔNLL(s4-sem16 − s4-b0) one-sided 95% upper bound < 0.05 nats/tok — the ASM-2383
  simultaneity gap, tested directly.
- **H-R (remap, secondary):** CACHE_ROUTE-analog substitution (`s4-remap16`) does not degrade
  quality vs drop-only (`s4-sem16`) — descriptive; never confounded with drop (separate arm).
- **H-D (dose feasibility):** a composite mask reaching ≥ 10% of measured decode expert-miss-I/O
  exists within causal+rare-tail coverage; if the achievable dose is < 2%, the lever is
  physically negligible and the direction dies (kill trigger 2, §7 — issuable at the PRE-SPEND
  point from telemetry+masks alone via the pinned analysis in phase="construction" mode, §6.1).

## §2 Pinned inputs

| input | pin | status |
|---|---|---|
| Quality suite (300 items, 10 domains × 3 families) | corpus `glm-s4drop-quality-suite-v1` = `4723f7c40d4fa377a8dbc80213476afa4cb50a986b4898340cf5b5ff81dad11e` | MATERIALIZED |
| Decode corpus (T-build 16×192, T-eval 8×96) | corpus `glm-s4drop-decode-corpus-v1` = `60fe747ad5cc573a08c1239faafeccc75ae12822ad6b5b0c7d7fecc94daa0233` | MATERIALIZED |
| Stage-3 analysis + atlas index (frozen copies) | corpus `glm-s4drop-stage3-inputs-v1` = `59bb0b70d0002df9281c6a84f607828bae1dbbc7dc2529fc845dc88b6f53ca2f` | MATERIALIZED |
| Mask builder (pure function) | `poc/glm52-probe/stage4/build_masks.py` (sha256 in record harness manifest) | COMMITTED with record |
| Analysis script | `analysis/glm_s4drop_stdin.py` (sha256 in record pins) | COMMITTED with record |
| T-build telemetry (kot-s4tel/1) | `glm-s4drop-telemetry-v1` | PINNED-AT-INPUTS (needs the box) |
| Mask tables (7 arms) | `glm-s4drop-masks-v1` (pure function of telemetry+stage3+atlas) | PINNED-AT-INPUTS |
| colibri base commit | `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250` + committed stage-3 patches | PINNED |
| S4_TABLE decode-mask patch diff | sha256 | PINNED-AT-INPUTS (ASM-2394; ops amendment before spend) |
| GLM-5.2 int4 weights content hash | pinned at bring-up before any scored token | PINNED-AT-INPUTS |
| Runner script + staged-bytes manifest | sha256s, ops-amended BEFORE any spend | PINNED-AT-INPUTS (review C2; ASM-2398) |
| T-eval reference trajectories (s4-b0 pass-1 greedy) | sha256, pinned in-run BEFORE any replay | PINNED-AT-INPUTS (ASM-2398) |

- DECISION: the suite is disjoint (exact + 24-char prefix, both directions) from BOTH the 244
  stage-3 selection items and all 480 wave-A probes, mechanically enforced by the generator and
  re-verified at bring-up. [STIPULATED: ASM-2391] (Cross-model review: CONFIRMED sound; unchanged.)
- DECISION: the pinned analysis FAIL-CLOSES if any consumed input arrives without a real digest:
  meta.pins must carry 64-hex sha256s for telemetry, masks manifest, S4_TABLE patch, weights,
  runner script, staged-bytes manifest (+ reference trajectories at final phase); placeholder
  digests are rejected (`pins_present_valid`). [STIPULATED: ASM-2398]

## §3 Arms (8 quality / 4 throughput) and mask construction

### 3.1 Arms
| arm | mask | quality (300 prefills) | throughput (T-eval decode + replay) |
|---|---|---|---|
| `s4-b0` | none | ✓ | ✓ |
| `s4-sem16` | 16-cell skiplist, DROP-only | ✓ | ✓ |
| `s4-remap16` | 16 cells; 9 SWAP (stage-3 swap_to), 7 DROP | ✓ | — |
| `s4-semd` | PRIMARY composite, dose §3.3 | ✓ | ✓ |
| `s4-bldf-d` | PRIMARY blind: frequency heuristic, matched I/O | ✓ | ✓ |
| `s4-bldr-d-r1..r3` | random cost-proportional blind, matched I/O (seeds 20260803/4/5) | ✓ | — |

All arms: DRAFT=0, greedy, TOPK=8 config default, EXPERT_BUDGET off, CACHE_ROUTE off, identical
pinned cache config (RAM_GB=55); ONLY the S4_TABLE differs. Drop = stage-3 route-around (mode-2)
semantics; swap = module-swap (mode-3) semantics [STIPULATED: ASM-2394].

### 3.2 Composite mask (SEM-D) — tiered, cost-weighted
Tier-0: the 16 skiplist cells (desc causal_confidence). Tier-1: the 6 SAFE-below-SKIP_MIN_CONF
cells. Tier-2: atlas `label_class` ∈ {rare, unseen} or atlas-absent cells, cost-weighted
descending c(cell), EXCLUDING stage-3 LOAD-BEARING and CHARACTERISE-MORE cells. Greedy until the
dose window. Universe: 76 MoE layers 3..78 × 256 experts = 19,456 cells [MEASURED: ASM-2342]. The
tier-2 extension is UNVALIDATED (gate-failed atlas; 4/4 control_rare causal anchor), supplies
almost all of the dose (full-scale mock: 426 − 22 = 404 of 426 cells), and is itself part of the
composite under test — the arm label is "composite", never "causal" [STIPULATED: ASM-2397].
Degenerate builds fail closed: a zero achievable dose emits a REGISTERED construction-kill
manifest (never a crash); a blind mask identical to SEM-D — or any pair of blind arms identical to
each other — is refused (ERR_S4_MASK_IDENTICAL) — review finding B4, skeptic-5 finding 5.
DISCLOSURE (skeptic-5 finding 6): the committed atlas index spans layers 3..77 only, so all 256
layer-78 cells are atlas-ABSENT and tier-2-eligible ranked purely by cost; this is conservative
for H-P (an unpriced load-bearing layer-78 drop hurts SEM-D, not the blind) and is covered by the
UNVALIDATED-extension label, but a layer-78 cell entering SEM-D carries zero atlas evidence.

### 3.3 Dose and matching
Target dose = 10% of total measured expert miss-bytes/token; projected blind-vs-composite matching
±2% (builder fills a ±1% window inside it); kill floor 2% (projected achievable at construction).
REALIZED dose currency (review finding A3) = COMMON-TOKEN REPLAY: after the free-running T-eval
passes, every throughput arm teacher-forces the SAME pinned reference trajectories (s4-b0 pass-1
greedy continuations, sha256-pinned in-run before any replay), so per-arm miss-bytes/token
differences are attributable to the MASK, not to divergent generated tokens. Realized removed dose
= (replay-missbytes/tok(`s4-b0`) − replay-missbytes/tok(arm)) / replay-missbytes/tok(`s4-b0`).
COMMONALITY IS MECHANICAL (re-review item 2, ASM-2401): every kot-s4row/3 replay row carries
`traj_sha256` — the sha256 over the exact forced TOKEN-ID SEQUENCE it replayed — and io_match
gates on digest IDENTITY against the pinned per-prompt reference digests
(meta.replay_reference.digests, source file pinned in meta.pins.reference_trajectories). Equal
token COUNTS over different forced sequences VOID io_match; the per-prompt count-equality check
is retained only as a cheap coherence cross-check.
GATES on this currency: the PASS floor (≥ 8%) and the semd-vs-bldf matching gate at tolerance
**≤ 5% of the dose** (was 25% — the R1 gate admitted a blind arm removing 24.9% more I/O, which
confounds the quality comparison; review finding A3). PROJECTED matching is likewise mechanical
(re-review item 2, ASM-2401): the analysis RECOMPUTES each blind arm's projected mismatch from
the audit's own `removed_frac` and `removed_bytes_per_tok` fields (both bases; gate on the max ≤
2%) and never trusts the supplied `match_rel_err`, which is only cross-checked for
self-consistency against the byte-basis recompute (|supplied − recomputed| ≤ 0.005; a
contradictory audit — e.g. blind 0.05 vs SEM-D 0.098 with a claimed 1% — VOIDS io_match).
REALIZED/PROJECTED COHERENCE (re-review item 5, ASM-2403): at a lawful (≥ 8%) projected dose the
realized replay dose may not exceed the projection by more than 15% relative (3× the stipulated
transfer σ_rel = 0.05, ASM-2399) and may not collapse below the 2% band floor — either
combination is REFUSED fail-closed (ERR_S4A_DOSE_INCOHERENT), never graded; shortfall within
[2%, 8%) stays lawful and resolves INCONCLUSIVE via the dose floor. Free-running decode
miss-bytes and greedy match-rate remain DESCRIPTIVE only. Zero-cost cells are NEVER added by any
fill; SEM-D tier-0/1 enter unconditionally. All stipulated, not derived.
[STIPULATED: ASM-2386] [STIPULATED: ASM-2396] [STIPULATED: ASM-2398] [STIPULATED: ASM-2401]
[STIPULATED: ASM-2403]

### 3.4 Blind baselines
Primary comparator `s4-bldf-d`: ascending T-build selection count (the deployable EXPERT_BUDGET-
analog; colibri #254 heuristic family), greedily cost-matched to SEM-D over positive-cost cells
only. Secondary `s4-bldr-d-r*`: seeded cost-proportional random, matched the same way. EVIDENCE
ASYMMETRY (skeptic-4 finding 1; review finding A — now part of the CLAIM, not only the envelope):
the composite arm consumes ~2 orders of magnitude more routing evidence than the blind arm's
3,072-token telemetry. Equalizing evidence was considered and REJECTED: an atlas-informed
"frequency" blind converges with tier-2 BY CONSTRUCTION (both select the rare tail), guaranteeing
a tie and fixing the verdict in advance. The honest design keeps the deployable blind and labels
the contrast composite-pipeline-vs-deployable-heuristic [STIPULATED: ASM-2397].

## §4 Telemetry prerequisite (runs FIRST, pins an input)

Decode the 16 T-build prompts (192 new tokens each, pinned config) and record per-cell selection
counts + cache-miss bytes → `glm-s4drop-telemetry-v1` (kot-s4tel/1; tier M = per-cell miss
attribution, tier P = sel×bytes fallback, disclosed; same tier both sides of every matched
comparison). c(cell) = miss-bytes/token. Masks are then built by the pinned pure function
(`build_masks.py`) and pinned by ops amendment BEFORE any quality/throughput spend.
[STIPULATED: ASM-2385]
DISCLOSURE (skeptic-5 finding 7): T-build and T-eval prompts share template style (one pair shares
a 24-char prefix); "held-out" means the T-eval PROMPTS are not in T-build — no distribution-level
independence is claimed, and no gate covers T-build↔T-eval overlap. Decode/replay rows BIND to the
pinned corpus: prompt ids must equal s4d-e00..e07 and every decode/replay row must carry ONE common
token budget ∈ {96, 64-after-ladder-rung-2} (skeptic-5 finding 4; mechanical in the analysis).

## §5 Endpoints, statistics, power (the analysis plan)

### 5.1 Instrument
Quality: ONE teacher-forced prefill per (item × quality arm) on the pinned suite; DV = mean NLL
per target token (the stage-3-validated final-logit readout). Decode-loop drift: descriptive
greedy match-rate vs `s4-b0` on T-eval; the GATED decode-side quantity is the common-token replay
dose (§3.3); MTP out of scope (DRAFT=0 everywhere). [STIPULATED: ASM-2390]
LIVENESS (review finding B1 + re-review item 3): a broken readout must be distinguishable from a
real tie — the `quality_liveness_valid` gate requires, per primary arm, ≥ 50 distinct NLL values
over the 300 items and stdev ≥ the REGISTERED MEANINGFUL floor 1e-3 nats/tok, and for the primary
deltas stdev ≥ the same floor with ≤ 10% exactly-zero values. "Mathematically positive variance"
was not enough (a 1e-12 jitter passed liveness and fired KILL with T = 0, re-review item 3): an
effectively inert / near-zero-variance primary pair is a dead instrument → INSTRUMENT-INVALID,
never a KILL on lb ≈ 0. The floor is ≥ 100× below the planning per-item spread (σ ≈ 0.30,
ASM-2396), so no live readout can trip it. [STIPULATED: ASM-2398] [STIPULATED: ASM-2402]
Item rows must also carry a validated positive-int `n_target_toks` (required at ingestion,
ERR_S4A_ITEM — re-review item 3, ASM-2402): a stream missing the winsorization-motivating target
lengths is refused, never silently graded.

### 5.2 Primary (EXACTLY ONE)
T = pooled mean over the 300 paired items of the WINSORIZED (±2.0 nats/tok) delta
d_i = NLL_i(`s4-bldf-d`) − NLL_i(`s4-semd`), nats/target-token (positive = composite better at
matched removed-I/O); raw mean + winsorized count disclosed. The primary needs ONLY the two
primary arms; its completeness gate is ZERO missing primary-pair rows, and secondary/random-arm
missingness cannot move it (review finding B2). Families come from the PINNED id→family mapping
(30 families × 10 items, checked against runner labels — review finding B3). CI: FAMILY-CLUSTER
seeded SHA-256-DRBG percentile bootstrap (resample the 30 template families with replacement;
items are near-clones within a family and NOT independent), B = 10,000, seed 20260806.
Decision: VALIDATE-track iff one-sided 95% lower bound (5th pct) > 0 AND T ≥ SESOI +0.05.
KILL trigger 1 (REVISED, review finding D1) iff the one-sided 95% UPPER bound (95th pct) < +0.05
**AND the realized (replay) dose ≥ 8%** (skeptic-5 finding 1: lower doses shrink deltas
monotonically, so an unfloored ub-kill is a spurious-kill gradient — a quality tie observed at a
sub-floor dose is INCONCLUSIVE, the lever question was not asked at lever scale): the data must
AFFIRM the absence of any effect as large as the SESOI at a physically meaningful dose. lb ≤ 0
with upper bound ≥ +0.05 is INCONCLUSIVE (underpowered region, reported at its resolution) — a
true-SESOI effect is now killed with prob ≈ 5% (was ≈ 36.6% under the R1 lb≤0 rule, a
no-spurious-KILL violation).
TOST margin ±0.05 on the 90% CI (the powered equivalence sentence is "no composite-mask selective
advantage at the 0.05 nats/tok resolution on this suite at this telemetry budget"). TOST/KILL
relationship (CORRECTED, re-review item 5 — the R2 "coincides by construction" sentence was FALSE
once kill-1 acquired the 8% dose floor): a TOST pass implies upper bound < +0.05, but TOST is
DOSE-INDEPENDENT while kill trigger 1 additionally requires realized (replay) dose ≥ 8% — so a
TOST pass coincides with the kill ONLY at lever-scale realized dose; at a sub-floor realized dose
a TOST equivalence is reported alongside an INCONCLUSIVE verdict (descriptive resolution
statement, never a kill; selftest branch tost-lowdose). [STIPULATED: ASM-2403]
Honest cluster power [STIPULATED: ASM-2396/2399]: planning within-family σ = 0.30, between-family
τ = 0.10 → se(T) ≈ 0.025; joint VALIDATE MDE_80 ≈ 0.071 nats/tok. Verdict split under the R2
rule: at true +0.10 → validate ≈ 0.977 / kill ≈ 1e-4; at true +0.05 (SESOI) → kill ≈ 0.05 /
validate ≈ 0.50 / inconclusive ≈ 0.45; at true 0 → kill ≈ 0.64 / validate ≈ 0.02 / inconclusive
≈ 0.34. The stale R1 iid figure (MDE ≈ 0.043) is RETIRED, and its carrier ASM-2389 is formally
SUPERSEDED (status superseded, successor ASM-2399) so the register is consistent — re-review
item 5. [SUPERSEDED: ASM-2389 → ASM-2399]

### 5.3 Full-verdict power (review finding D2 + skeptic-5 finding 2)
The record VERDICT PASS = quality joint pass AND realized (replay) dose ≥ 8% AND the two-pass
tok/s clause; each non-quality clause carries a STIPULATED noise model [STIPULATED: ASM-2399]:
realized-dose transfer error (T-build→T-eval shift after common-token replay removes trajectory
noise) σ_rel = 0.05 per arm → P(dose ≥ 8% | projected 9.8%) ≈ 0.9999; io_match 5%-of-dose gate:
between-arm transfer errors stipulated correlated ρ = 0.9 (common forced trajectory, matched rare
tails) → sd(rel diff) ≈ 0.022 → P(io_match) ≈ 0.975 — SENSITIVITY DISCLOSED: at ρ = 0.5 P falls
to ≈ 0.68, and an io_match miss is a VOID (coordinator rerun under void budget 1), never a
verdict; per-pass tok/s gain se = 0.02 → P(two-pass clause | true gain +8%) ≈ 0.99. Design-point
FULL-VERDICT validate ≈ 0.94; at true tok/s gain +4% the tok/s clause falls to ≈ 0.7 and the full
verdict to ≈ 0.66 (disclosed: the tok/s clause is the weakest link, and a tok/s miss yields
INCONCLUSIVE, never a kill).

### 5.4 Secondaries
joint-16 non-inferiority (upper 95% bound < 0.05 vs `s4-b0`); random-blind contrast (per-item mean
over PRESENT realizations vs semd; n_realizations disclosed); remap-vs-drop; per-arm tok/s +
free-running miss-bytes/token + replay miss-bytes/token on T-eval (T-eval runs TWICE per arm in
seeded interleaved blocks; the PASS tok/s clause is pooled gain ≥ +3% AND a positive gain in each
pass; magnitudes descriptive); decode match-rate; realized + projected dose; power scope. Every
secondary contrast is computed on its OWN pairwise-complete item set (sizes disclosed in
/analysis/secondary_n_items) so secondary missingness never propagates. All quality contrasts are
winsorized and family-clustered like the primary. All output fields are declared in the record;
verdict pointers resolve only to them.

## §6 Instrument gates (any failure → INSTRUMENT-INVALID, never reinterpreted)

pins_valid (image/commit/patch/weights/table hashes re-verified fail-closed at engine start;
runner-attested, bound by sidecar + cross-vendor audit); pins_present_valid (MECHANICAL: meta.pins
carries real 64-hex digests for telemetry/masks/patch/weights/runner-script/staged-bytes
[+ reference-trajectories at final]; placeholders rejected); telemetry_valid (tier ∈ {M,P},
total > 0, ≥ 2,000 decode tokens; counter semantics pinned, ASM-2395); suite_disjoint_valid
(re-verified at bring-up); mask_construction_valid (masks re-derive byte-identical from pinned
inputs at bring-up); family_valid (MECHANICAL: runner family labels equal the PINNED id→family
mapping; exactly 30 families × 10 items — a collapsed set FAILS); quality_liveness_valid
(MECHANICAL: §5.1, incl. the registered 1e-3 stdev floor); io_match_valid (MECHANICAL, re-review
item 2: projected ≤ 2% every present blind arm RECOMPUTED from the audit's removed_frac +
removed_bytes_per_tok with `match_rel_err` cross-checked for self-consistency at ≤ 0.005;
REALIZED common-token-replay removed-dose semd-vs-bldf within 5% of the dose; TRAJECTORY-DIGEST
identity of every replay row against the pinned per-prompt reference digests — equal counts over
divergent sequences VOID; common forced-token counts retained as a coherence cross-check);
decode_config_valid (runner boolean AND the mechanical decode-row shape
check: DRAFT=0 greedy, identical cache config, arm-order block randomization seed 20260802, two
T-eval passes per arm); inertness_valid (empty-table byte-identity to the stage-3 build on a
seeded 8-item spot set at bring-up); completeness_valid (MECHANICAL: exactly the pinned id set
s4q-0000..0299 with ZERO missing primary-pair rows; each secondary arm ≤ 5 incomplete;
degradation-ladder drops lawful ONLY for {r2, r3} and disclosed in meta.degradation.dropped_arms);
seeds_valid (bootstrap + present blind-realization seeds checked in-band); cost_ledger_valid
(MECHANICAL live ledger, review finding D3 + re-review item 5: the checkpoints must be the
REGISTERED PHASE-BOUNDARY SEQUENCE — telemetry, masks, bring-up, quality-<arm> × 8 in arm order,
t-eval, replay (construction: telemetry, masks) — with DISTINCT labels in registered order, a
quality checkpoint absent ONLY for a lawfully dropped ladder arm; duplicate/placeholder trails
('x' × 13) are rejected; monotone, every checkpoint ≤ $40, final figure equals the last
checkpoint, within (5, 40] USD and (0, 36] h at campaign scale, (0.5, 40] USD at construction;
the runner ABORTS (salvage-stop) the moment accrued spend reaches the cap; ASM-2403). Everything computable from the rows is
recomputed in-script; residual runner booleans are explicitly scoped to the sidecar + the
cross-vendor audit. VOID BUDGET (ASM-2396): an INSTRUMENT-INVALID readout obligates a coordinator
rerun decision; a second VOID on this record escalates to the maintainer — VOID is never a quiet
exit from an impending kill.

### 6.1 Construction phase (pre-spend verdict point — review finding B5)
The pinned analysis accepts a meta-ONLY stream with phase="construction" (zero item/decode/replay
rows) at the point where only telemetry + masks exist (ledger ~$2-8): kill trigger 2 (achievable
dose capped < 2%) and the [2%, 8%) dose-band PRE-SPEND STOP are computed from telemetry+masks
alone — the kill is issuable by the frozen executable BEFORE any quality item or $5 of ledger.
Gates that need run data are scoped out (disclosed via /analysis/phase); PASS is unreachable in
this mode, and a construction stream whose projected dose is ≥ 8% REFUSES to emit a verdict
(ERR_S4A_PHASE — the campaign must proceed, not grade itself). [STIPULATED: ASM-2400]
The band binds BOTH phases (re-review item 5, ASM-2403): a FINAL stream whose projected dose lies
in [2%, 8%) bypassed the registered pre-spend stop and is REFUSED fail-closed
(ERR_S4A_DOSE_BAND), never graded — together with the realized/projected coherence refusals
(§3.3) this closes the projected-0.05/realized-0.098 spurious PASS.

## §7 Kill criterion (verbatim in the record) and envelope

KILL (either trigger, gates valid): (1) the primary one-sided 95% UPPER bound < +0.05 AT a
realized (replay) dose ≥ 8% — the data affirm the composite mask has no selective advantage as
large as the SESOI over the matched-removed-I/O frequency-blind mask at lever-scale dose, so
expert-drop is not a SELECTIVE lever at this telemetry budget (a tie at a sub-floor dose is
INCONCLUSIVE — skeptic-5 finding 1); (2) the achievable composite dose is capped below 2% of
measured decode expert-miss-I/O (tier-scoped; issuable at construction from telemetry+masks
alone; an UNCAPPED sub-2% dose is incoherent input and is REFUSED, ERR_S4A_DOSE_INCOHERENT) —
the lever is physically negligible at full causal+rare-tail coverage. VALIDATE: primary joint pass (lb > 0 AND T ≥ +0.05)
AND REALIZED (common-token replay) dose ≥ 8% AND the two-pass tok/s clause (pooled ≥ +3%, positive
each pass) — unlocks ONLY a narrow composite-pruning method post (#207 stays PAUSED; deterministic
replacement stays unevidenced, per stage-3). INCONCLUSIVE: everything else — including lb ≤ 0 with
upper bound ≥ +0.05 (underpowered region; NEVER a kill, review finding D1). Dose dead zone
[2%, 8%) at construction = PRE-SPEND STOP, not a run (ASM-2396); in a FINAL stream the same band
(and realized/projected incoherence) is a fail-closed REFUSAL (ERR_S4A_DOSE_BAND /
ERR_S4A_DOSE_INCOHERENT — re-review item 5, ASM-2403). TOST does NOT unconditionally coincide
with kill trigger 1: TOST is dose-independent, the kill is 8%-dose-floored (§5.2).
Envelope: see the record's `extrapolation_envelope_verbatim` (binding text lives there).

## §8 Cost and sequencing

Planning point ≈ $18 / 16 h; worst-case ≤ the caps usd_cap = $40 AND wall = 36 h (whichever binds
first) — inside the bead's $25–40 ceiling; decode rate unknown until telemetry, degradation
ladder registered. [STIPULATED: ASM-2393]. Components (planning): telemetry ~$2–8; quality
2,400 prefills ~$8.4–12.3; throughput 4 arms × 2 passes × 768 tokens ~$4–16 pessimistic (ladder
covers the corner); common-token replay 4 arms × 768 forced tokens ~$1–4; staging ~$1.4.
LIVE ledger (review finding D3): the runner appends a checkpoint after every registered phase
boundary (telemetry, masks, bring-up, each quality arm, T-eval, replay) and ABORTS (salvage-stop,
never retry) the moment accrued realized spend reaches $40 or 36 h; the analysis re-checks the
checkpoint trail mechanically against the REGISTERED label sequence (§6; distinct, in order,
duplicates/placeholders rejected — re-review item 5, ASM-2403). Degradation ladder (ANALYSIS-COMPATIBLE, review finding D3):
(1) T-build 192→128 tokens/prompt, (2) T-eval 96→64, (3) drop `s4-bldr-d-r2`/`r3` — lawful
because the primary completeness gate is PAIR-ONLY, so dropping random arms removes only their
own secondary rows and cannot zero the primary complete cases, (4) STOP and return to the
coordinator; the 300-item suite, s4-b0/s4-semd/s4-bldf-d, s4-sem16, and the replay pass are never
cut.

Sequencing: freeze → S4_TABLE patch authored + ops-amended in (ASM-2394; counter semantics
pre-pinned, ASM-2395) + runner-script/staged-bytes hashes ops-amended (ASM-2398) → bring-up gates
(inertness, pin re-verification, suite disjointness, mask re-derivation) → telemetry → masks
pinned by ops amendment → PRE-SPEND STOPS via phase="construction" analysis: cost projection vs
caps (degrade or STOP per ASM-2393), kill-2 if capped dose < 2%, dose-band STOP on [2%, 8%) —
never burn the campaign on a verdict fixed in advance → quality prefills → throughput decode (two
seeded interleaved passes) → common-token replay (reference trajectories pinned first) →
verdict-gen (rows as a D10 role:"rows" artifact) → cross-vendor audit. The runner is the OPUS
execution role; this designer never runs, grades, or audits.

## §9 Review record

- 2026-07-16 designer-15: R1 drafted; initial green mocks; prereg-freeze --dry-run OK.
- 2026-07-16 skeptic-4 pre-freeze attack: verdict HOLD, 2 BLOCKERs + 5 MAJORs + 4 MINORs (§10);
  designer-15 dispositioned all 11; R1 frozen (superseded sha
  0f21965fb6ed2d9212483bc0c2a4d1a94c755782c05e1251ec270e1219d61bce).
- 2026-07-16 pre-run CROSS-MODEL review: verdict HOLD (§11) — estimand confound, spurious-verdict
  paths, layer-count bug, power/budget defects. R1 reset to DRAFT under the lawful pre-final
  window (no results-log of any phase; not GNG-0-signed; correction record
  registry/corrections/glm-s4drop-0/1-prefreeze-correction.json).
- 2026-07-16 designer-18: R2 fixes ALL §11 findings. ASM-2397..2400 registered.
- 2026-07-16 skeptic-5 pre-freeze re-attack on R2: HOLD — 1 BLOCKER + 2 MAJORs + 4 MINORs (§12);
  designer-18 dispositioned all 7 (5 fixed, 2 disclosed). Post-fix verification: `build_masks.py
  --selftest` 25/25 green (incl. construction-kill + identical-mask (semd/bldf/mutual) + layer-78
  checks); full-scale mock on real stage-3+atlas inputs, SYNTHETIC 76-layer telemetry (19,456
  cells) → semd 426 cells @ 9.81% dose, all blind arms matched ≤ 1.0%; `glm_s4drop_stdin.py
  --selftest` 67/67 green, 68 output fields on every branch (9 decision branches incl.
  tie-at-sub-floor-dose → INCONCLUSIVE), all §11 adversarial replays gated. Refreeze recorded in
  registry/corrections/glm-s4drop-0/1-prefreeze-correction.json.
- 2026-07-16 Stage-4 CROSS-MODEL RE-REVIEW of R2: estimand + layer/pin fixes CONFIRMED; HOLD on
  THREE residual spurious-verdict paths (§13, items 2/3/5). Maintainer approved proceeding
  (issue #43; the $40 cap is non-AWS in-kind). R2 reset to DRAFT under the lawful pre-final
  window (still no results-log of any phase; still not GNG-0-signed).
- 2026-07-16 designer-19: R3 fixes all §13 items (kot-s4row/3; ASM-2401/2402/2403 registered;
  ASM-2389 formally superseded by ASM-2399). `glm_s4drop_stdin.py --selftest` 86/86 green, 68
  output fields on every branch (10 decision branches, adding tost-at-sub-floor-dose →
  INCONCLUSIVE), byte-deterministic; every §13 adversarial replay that previously PASSed/KILLed
  now INSTRUMENT-INVALID / voided / refused. Refreeze recorded in
  registry/corrections/glm-s4drop-0/2-prefreeze-correction.json.

## §10 Pre-freeze skeptic attack (skeptic-4, 2026-07-16) — findings + dispositions (R1, retained)

1. BLOCKER, blind-strawman (zero-cost free-append; info asymmetry): ACCEPTED-FIXED — no fill may
   add a zero-cost cell (builder + selftest); PASS/kill sentences scoped "at this telemetry
   budget"; asymmetry disclosed in §3.4 (R2 promotes it into the claim itself, ASM-2397).
2. BLOCKER, matched-I/O gate near-vacuous (total-miss ratio; projected PASS dose): ACCEPTED-FIXED
   — realized REMOVED-dose currency (R2: common-token replay at ≤ 5%, §3.3).
3. MAJOR, iid bootstrap over 30 template families: ACCEPTED-FIXED — family-cluster bootstrap.
4. MAJOR, joint-rule power misstated: ACCEPTED-FIXED — honest cluster power registered (R2
   re-derives the split under the revised kill rule, §5.2).
5. MAJOR, heavy-tail/outlier fragility + silent exclusions: ACCEPTED-FIXED — winsorization ±2.0
   with raw mean + count disclosed; per-arm missingness reported.
6. MAJOR, counter semantics unpinned at freeze: ACCEPTED-FIXED — ASM-2395 pins the miss-bytes
   definition + unit-test-vector requirement pre-freeze.
7. MAJOR, tok/s single point in PASS: ACCEPTED-FIXED — two seeded interleaved T-eval passes;
   pooled gain ≥ 3% AND positive in each pass.
8. MINOR, honor-system gates / partial seed check: ACCEPTED-FIXED — blind seeds + pinned id set
   checked in-band (R2 adds pins_present/family/liveness/ledger mechanical gates).
9. MINOR, dose dead zone / tier-P scoping / capped balloon: ACCEPTED-FIXED — pre-spend stop on
   [2%, 8%); kill text tier-scoped; zero-cost fix removes the balloon.
10. MINOR, VOID escape hatch: ACCEPTED-FIXED — void budget 1 + escalation registered.
11. MINOR, "strictly disjoint" overstated / knife-edge projected gate: ACCEPTED-PARTIAL —
    item-level disjointness wording retained but distribution-level overlap DISCLOSED; builder
    fills a ±1% window inside the 2% gate.

## §11 Pre-run cross-model review (2026-07-16, coordinator-relayed HOLD) — findings + R2 dispositions

A. ESTIMAND confound (BLOCKER): SEM-D is a data-richer composite mislabelled as a causal isolate;
   "matched I/O" admitted 25% mismatch (an adversarial replay PASSed with the blind removing
   24.9% more I/O). ACCEPTED-FIXED — option (b): honest composite labelling everywhere (title,
   H-P, kill, envelope; ASM-2397; §1); option (a) rejected as undoseable (mock: causal core ≈
   0.06-0.1% of miss-I/O); realized matching moved to COMMON-TOKEN replay, GATED at ≤ 5% of the
   dose (ASM-2398; §3.3); the 24.9% replay now VOIDS io_match (selftest).
B1. NLL liveness (BLOCKER): all-equal/inert/rounded NLLs could KILL on lb == 0. ACCEPTED-FIXED —
   quality_liveness_valid gate (§5.1); inert + rounded adversarial replays now INSTRUMENT-INVALID
   with kill_fired false (selftest).
B2. Primary completeness (MAJOR): 5 dropped secondary rows flipped T 0.0178→0.0520. ACCEPTED-
   FIXED — primary is PAIR-ONLY with ZERO missing; secondaries pairwise-complete; replayed:
   secondary drops leave T bit-identical (selftest).
B3. Family gate (MAJOR): collapsed/one-family sets PASSed. ACCEPTED-FIXED — PINNED id→family
   mapping checked against runner labels; 30×10 required; collapse now FAILS (selftest).
B4. Mask builder (MAJOR): zero dose crashed div-by-zero; identical SEM-D/blind masks accepted in
   production. ACCEPTED-FIXED — registered construction-kill manifest + ERR_S4_MASK_IDENTICAL
   (builder selftest).
B5. KILL-trigger-2 unfireable pre-spend (MAJOR): needed quality items + all gates + ≥$5 ledger.
   ACCEPTED-FIXED — phase="construction" analysis mode computes it from telemetry+masks alone at
   a ~$3 ledger (§6.1; selftest).
C1. LAYER COUNT BUG (MAJOR): builder hard-coded 75 MoE layers (3..77) vs the registered MEASURED
   76 (3..78, ASM-2342). ACCEPTED-FIXED — MAIN_LAYERS = 3..78; universe 19,456; layer-78
   eligibility + 76-layer universe asserted in selftest; mock telemetry regenerated at 76 layers.
C2. Pins/gates (MAJOR): runner-supplied booleans not recomputed; runner/staged bytes unpinned.
   ACCEPTED-FIXED — family/liveness/io-match/completeness/seeds/ledger/decode-shape/pins-present
   all mechanically recomputed; runner script + staged-bytes manifest + reference trajectories
   added as PINNED-AT-INPUTS; analysis fail-closes on absent/placeholder digests (§2, §6).
D1. ~36.6% KILL at the +0.05 SESOI (BLOCKER, no-spurious-KILL violation). ACCEPTED-FIXED — kill
   boundary moved to upper95 < SESOI; at true SESOI: kill ≈ 5% / validate ≈ 0.50 / inconclusive
   ≈ 0.45; lb ≤ 0 with ub ≥ SESOI is INCONCLUSIVE (selftest lb0-notkill).
D2. Full-verdict power missing; stale iid MDE 0.043. ACCEPTED-FIXED — §5.3 registers noise models
   for dose + tok/s clauses; design-point full-verdict ≈ 0.96; iid figure retired everywhere.
D3. Post-hoc ledger; ladder analysis-incompatible. ACCEPTED-FIXED — live monotone checkpoint
   ledger enforced during the run and re-checked mechanically; ladder rung 3 (drop r2/r3) proven
   primary-neutral (selftest).

## §12 Pre-freeze skeptic re-attack on R2 (skeptic-5, 2026-07-16) — findings + dispositions

1. BLOCKER, kill-1 unfloored on dose (spurious-kill gradient at sub-8% realized dose; final phase
   never re-checked the dose band): ACCEPTED-FIXED — kill-1 now requires realized (replay) dose
   ≥ 8%; a quality tie at a sub-floor dose is INCONCLUSIVE (selftest tie-lowdose branch).
2. MAJOR, full-verdict power omitted P(io_match) and silently assumed between-arm error
   correlation: ACCEPTED-FIXED — ρ = 0.9 STIPULATED (common forced trajectory), P(io_match) ≈
   0.975 registered with ρ = 0.5 sensitivity disclosed; design-point full-verdict 0.96 → 0.94
   (§5.3; ASM-2399 revised in the register, last-line-current).
3. MAJOR, uncapped sub-2% dose fell through the construction verdict point as "proceed":
   ACCEPTED-FIXED — ERR_S4A_DOSE_INCOHERENT refusal in BOTH phases (the pinned builder cannot
   produce that combination; selftest).
4. MINOR, decode/replay rows unbound to the pinned T-eval corpus: ACCEPTED-FIXED — prompt ids
   must equal s4d-e00..e07 and one common token budget ∈ {96, 64} across every decode/replay row
   (mechanical; selftest positive + negative).
5. MINOR, builder mutual blind-identity unchecked in production: ACCEPTED-FIXED — every random
   realization is refused if identical to semd, bldf, or an earlier realization.
6. MINOR, layer-78 cells are atlas-absent (universe widened without evidence coverage):
   ACCEPTED-AS-DISCLOSURE — §3.2; conservative for H-P; covered by the UNVALIDATED-extension
   label.
7. MINOR, docstring schema staleness + one T-build/T-eval 24-char shared prefix: ACCEPTED-FIXED
   (docstring) + ACCEPTED-AS-DISCLOSURE (§4: "held-out" = prompt-level only; no distribution
   independence claimed).
skeptic-5 explicitly verified: pins/corpus digests match on disk; PINNED_FAMILIES matches
items.json exactly; record output_fields = analysis OUTPUT_FIELDS; verdict-rule pointers resolve;
power arithmetic internally consistent; primary provably immovable by non-primary rows; no
further blockers.

## §13 Stage-4 cross-model RE-REVIEW of R2 (2026-07-16) — residual HOLD items + R3 dispositions

Estimand relabelling (A), layer/universe fix (C1), and the pin discipline (C2) were CONFIRMED
sound. HOLD on three residual spurious-verdict paths; all fixed in R3 (kot-s4row/3):

2a. I/O MATCHING not mechanically common-token (MAJOR): replay rows carried only prompt id +
   token COUNT + miss bytes, so equal-length-but-DIVERGENT forced sequences passed io_match (the
   "divergent-trajectory" selftest only changed a count 96→80). ACCEPTED-FIXED — every replay
   row carries `traj_sha256` (digest over the exact forced token-id sequence); io_match gates on
   digest identity vs the pinned per-prompt s4-b0 reference digests
   (meta.replay_reference.digests; ASM-2401); equal-count divergent-digest replay now VOIDS
   io_match (selftest).
2b. Projected matching TRUSTED the supplied `match_rel_err` (MAJOR): a contradictory audit
   (blind 0.05 vs SEM-D 0.098 with match_rel_err = 0.01) PASSed. ACCEPTED-FIXED — the analysis
   recomputes the mismatch from removed_frac + removed_bytes_per_tok (gate on the max) and
   cross-checks the supplied figure at ≤ 0.005 (ASM-2401); the contradictory audit now FAILS
   io_match (selftest, both directions).
3a. `n_target_toks` never validated at ingestion (MAJOR): dropping it from all 2,400 rows still
   PASSed. ACCEPTED-FIXED — required positive-int on every item row, refusal ERR_S4A_ITEM
   (ASM-2402; selftest: all-rows strip, non-int, zero).
3b. Liveness accepted mathematically-positive-but-inert variance (MAJOR): 1e-12 jitter passed
   liveness and fired KILL with T = 0. ACCEPTED-FIXED — registered MEANINGFUL floor stdev ≥ 1e-3
   nats/tok on each primary arm and the primary deltas (ASM-2402); the jitter replay is now
   INSTRUMENT-INVALID with kill_fired false (selftest).
5a. Dose band + coherence unenforced in FINAL mode (MAJOR): a final stream with projected 0.05 /
   realized 0.098 PASSed. ACCEPTED-FIXED — final-phase [2%, 8%) projected dose REFUSED
   (ERR_S4A_DOSE_BAND); realized > 1.15× projected or realized < 2% at lawful projection REFUSED
   (ERR_S4A_DOSE_INCOHERENT; ASM-2403); all three replays refused (selftest).
5b. Ledger accepted 13 duplicate "x" checkpoints at $16.20 (MAJOR): the prereg requires
   PHASE-BOUNDARY checkpoints. ACCEPTED-FIXED — registered checkpoint label sequence enforced
   (distinct, registered order, absence lawful only for dropped ladder arms; ASM-2403); the
   duplicate-placeholder, out-of-order, skipped-boundary, and undeclared-absence replays all fail
   the ledger gate (selftest).
5c. ASM-2389 stated the retired iid MDE ≈ 0.043 / power ≈ 0.89 without formal supersession
   (MINOR). ACCEPTED-FIXED — ASM-2389 status = superseded, successor ASM-2399 (register
   append-only update).
5d. "TOST coincides with kill" prose FALSE under the 8% kill dose floor (MINOR): TOST is
   dose-independent; a TOST = true / realized 0.06 / kill = false case exists. ACCEPTED-FIXED —
   frozen prose corrected here (§5.2, §7), in the record's kill text, and in ASM-2403; the
   tost-lowdose selftest branch pins the corrected behaviour (TOST + INCONCLUSIVE, no kill).
