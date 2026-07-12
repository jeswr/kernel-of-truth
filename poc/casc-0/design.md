# CASC-0' — prereg design note: the STATIC-CASE / M2-isolator factorial

> **Status: DRAFT, freeze-ready** — registry record
> `registry/experiments/casc-0.json` (status DRAFT, no frozen_sha256; the
> coordinator freezes). Design source, adopted verbatim where quoted:
> `docs/next/arch/cascade-synthesis.md` §3 (CASC-0', the REDESIGN-THEN-DECIDE
> ruling) — itself the adjudication of CASC/1
> (`docs/next/arch/cascade-naturalisation.md`) against the GPT-5.6 critique.
> Author: Fable, experiment-engineering role (designer-1), 2026-07-11.
> This document performs no freeze, no registry edit, no bd write, no GPU run.

## 0. The question (maintainer issue-#15 follow-up — "properly understand the static case")

f2b-transfer measured (pending Gate-A audit) a real **+0.2507** external-gold
verifier-offload lift for a 135M host over the kernel's ALIGNED AUTHORED
store — and simultaneously **failed `noninferiority_vs_r3`** (135M+verify vs
1.7B-alone at margin 0) [MEASURED: registry/verdicts/f2b-transfer.json].
DECONF-A1 certified kernel runtime STRUCTURE inert at the checker; the value,
if any, lives in the authored, aligned, canonical content. The untested bet
is **M2** [EXTRAPOLATION: ASM-1078]: does presenting that authored content in
a structured canonical medium — "naturalised" INTO the smaller model's input
— give the SMALLER reasoner a gain the larger one does not share, so that
"small model + aligned authored store/checker" can approach the larger model?
CASC-0' measures exactly the SIGN of that size×medium interaction, plus the
honest successor of the failed noninferiority read, now WITH an internal
structured medium.

## 1. Class, scope, riders

- **Class:** G2 `oracle-diagnostic`, gold-dialect inbound; the front-end F is
  NOT exercised (its price is NLB's subject; composed analytically after,
  tagged EXTRAPOLATION). NO renderer, NO fid_R (deferred rear-seam
  instrument, cascade-synthesis §1.5). NO W1 / real-input claim (ASM-0814
  riders verbatim).
- **Rider on EVERY verdict sentence:** SELF-AUTHORED / kernel-STYLE /
  engine-derived-gold — items and store are procedurally generated from this
  design's own authored facts; gold is engine-derived, never external
  [PROPOSED-ASM-1157]. This probe intentionally steps back from external
  adjudication: it prices a REPRESENTATION effect, not ground-truth
  independence (that residual was f2b-transfer's job and stays discharged or
  not there).
- No feasibility conclusion is licensed by any outcome; a PASS licenses only
  the M2 sign at scope (§7).

## 2. Factors and cells [PROPOSED-ASM-1140/1141/1142/1145]

| Factor | Levels |
|---|---|
| size | R2 = SmolLM2-360M-Instruct@a10cc151, R3 = SmolLM2-1.7B-Instruct@31b70e2e (in-programme rungs; sign-not-slope) |
| medium | `nl` (naturalised prose, content-matched), `gloss` (raw-kernel Option-A structured gloss), `plain` (distilled knull-grade typed dialect) |
| verifier | off, on — on ONLY for structured mediums (NL has no IR-hard islands) |

10 factorial cells + `ttc-deflator` (R2/nl + self-consistency, cost-matched
to the FIXED reference cell R2/gloss/verifier-on) + `deranged-control`
(R2/gloss/verifier-on against a Sattolo-deranged closure; reported-only).
3 seeds {0,1,2}; same paired 300-item eval set everywhere. All cells STOCK
(no tuning; ASM-0852 satisfied at T_k=0) [PROPOSED-ASM-1150]. A 1.7B-NL+TTC
reference MAY later be co-reported at its own cost, never as a matched
baseline (the old CASC-0 A2 contract is arithmetically impossible and stays
dropped).

## 3. Corpus, protocol, verifier

- **Corpus** `data/d-casc0` [PROPOSED-ASM-1143]: seed-pinned
  (`dcasc0/1|casc-0|20260711`, single-draw rule) CLUTRR-shaped depth-2/3/4
  relation-composition items (400 built; eval = rank prefix 300, floor 250;
  prefix depth mix 75/113/112), engine-derivable gold by construction from a
  pinned composition table under stipulated closed-world assumptions;
  held-out compositions (eval depth-2 paths hash-disjoint from exemplar
  paths) and held-out depths (exemplars depth-2 only). Kernel-coverage
  mapping of the relation concepts is a stipulated pre-freeze explicator
  check [PROPOSED-ASM-1158]; the rider rides regardless.
- **Protocol** (identical in every cell): the model asserts each INTERMEDIATE
  cumulative relation rel(X0,Xt), t=2..depth−1, as a constrained 7-option
  choice; each assertion is appended to the context in the cell's own medium;
  then the final relation is a constrained choice on the same surface.
  Constrained sequence-logprob decoding (attempt 0 argmax; retries/TTC
  seeded multinomial). Per-medium token counts MEASURED (ρ_in converts to
  MEASURED; planning read from rendered templates: gloss≈3.0, plain≈0.9).
- **Verifier** (M4 at step grain) [PROPOSED-ASM-1144]: checks asserted
  INTERMEDIATES against the engine closure derived from the authored store;
  ANY rejection ⇒ resample the whole item, retry budget k=2; final answer =
  last attempt. **The final relation is NEVER checked** — the anti-oracle
  rule; a final-hop check against engine-derivable gold would manufacture
  exactly the oracle-structured win that killed CASC-0 (synthesis §1.2).
- **TTC deflator** [PROPOSED-ASM-1148]: N = clamp(round(ref_flops/nl_flops),
  2, 9) from the same run's seed-0 measured cells; majority vote, pinned tie
  order; `/gates/ttc_match_valid` requires the measured relative flops gap
  ≤ 0.30 (DRAFT band; integer-N quantization bounds achievable gap ~0.5/N).
- **Deranged control** [PROPOSED-ASM-1152]: Sattolo 3-cycle over the atomic
  relation types (seed 20260711, map recorded), closure decoupled from items
  at identical topology/cost; expected collapse of the verifier benefit.

## 4. Endpoints (statistics per programme §2.5: paired item bootstrap
B=10000, PRNG seed 20260711, BCa; Holm within each 2-member family)
[PROPOSED-ASM-1146/1147/1151]

1. **Primary — the M2 sign** (verifier OFF, the pure medium leg; the
   verifier-on interaction is a named secondary so M4 never masquerades as
   M2): for m ∈ {gloss, plain},
   `inter_m = (acc(R2,m) − acc(R2,nl)) − (acc(R3,m) − acc(R3,nl))`;
   reject iff one-sided 95% BCa LB > 0 for ≥1 medium under Holm.
2. **Co-primary — practical shrink** (the honest successor to f2b-transfer's
   failed `noninferiority_vs_r3`, now WITH an internal structured medium):
   acc(R2, m, verifier on) non-inferior to acc(R3, nl) at margin 0.05
   (DRAFT pin, maintainer-adjustable at freeze) AND measured cost strictly
   below the R3-nl cell's; Holm across the two mediums; CONDITIONAL on the
   separation gate (else unevaluable, never a fail).
3. **Secondaries:** verifier main effects + verifier×size interaction;
   verifier-on interactions; gloss-vs-plain TOST at ±0.05 (attribution rung
   2, deflationary prior disclosed — a within-band result kills
   kernel-content attribution NON-fatally, K3'); the TTC deflator contrasts;
   realised ρ_in, retry overhead r, full KOT-COST vector per cell (γ is NOT
   exercised here — constrained answer surface, disclosed limitation);
   deranged-control delta; per-seed sign consistency.

## 5. Instrument gates (never hypothesis outcomes) [PROPOSED-ASM-1156]

engagement (RT-7a structural: decidable fraction ≥0.70 — decidable = depth≥3
items, 0.75 of the prefix; attempt-0 rejection in [0.05,0.95]; ≥1 final
differs), headroom (acc(R2,nl) ≤ 0.85), separation (R3−R2 on nl ≥ 0.05 with
LB>0 — gates ONLY the co-primary's membership), ttc-match (±0.30 flops
band). P10 extraction gate N/A: constrained key selection makes extraction
failure structurally impossible.

## 6. Kills [PROPOSED-ASM-1149 — adopted from cascade-synthesis §3 verbatim]

- **K1' (M2 kill):** primary interaction LCB95 ≤ 0 for BOTH structured
  mediums AND the co-primary NI fails ⇒ M2 dead at scope; **H-CN shelved;
  V-DEC/V-LL do not unlock**; the cost goal reverts to the a-e2 trim bound.
- **K2' (compute-deflator kill):** primary passed but no Holm-passing medium
  beats the cost-matched 360M-NL+TTC deflator (LCB ≤ 0) ⇒ the medium effect
  is purchased compute; treated as K1'.
- **K3' (attribution kill, NON-fatal):** gloss ≈ plain within the TOST band
  ⇒ kernel-content attribution dead at scope; any surviving family continues
  as a GENERIC structured cascade; the kernel claim routes to knull-v2/A-F0.
  Reported-only (`kernel_attribution_dead`), never verdict-bearing.
- NULL: both primary interactions TOST-equivalent to 0 at ±0.05.

## 7. What a PASS licenses / envelope

Only that the M2 sign exists at oracle-inbound, self-authored covered-corpus,
engine-derived-gold, ≤1.7B, stock-checkpoint, k=2, constrained-surface scope
— the gate to build the renderer instrument and plan G3 behind G-NLB. It
licenses NO W1 claim, NO cost headline, NO kernel-attribution claim (K3''s
separate read), NO coverage-general claim (m0b 0.3542 restated mandatorily),
NO scale slope (2 rungs = sign only), NO ground-truth-independence claim
(engine-derived gold), NO feasibility conclusion. A K1'/K2' kill is
symmetrically scoped: M2 dead AT THIS SCOPE, not the verify-retry mechanism
(f2b-replicate's audited PASS stands untouched).

## 8. Budget & infra

≤15 GPU-h, ≤$30, wall-clock ≤36 h, Tier-1 cap $80; Modal single GPU
(A100-40GB or A10G), pinned f2b image reuse (im-6uXR6RyVQV15h2B3gtpOG2 +
requirements-image.txt) [PROPOSED-ASM-1153/1154]. Dry-plan (A100,
2026-07-11): 4.58 h point, 9.16 h with 2.0× overhead, $19.24 worst — inside
every cap. Engine/analysis legs are CPU, local box, standing nice/checkpoint
discipline. Mock run green 2026-07-11; analysis-consumable end-to-end
(PASS-shaped on the planted stub surface — MOCK, never a measurement).

## 9. Self-check (mandatory)

Every DECISION line above cites a PROPOSED-ASM-114x/115x id; every MEASURED
figure names its artifact and stays in-envelope; forward expectations are
EXTRAPOLATION (ASM-1078's resolver becomes this record's primary); no
account handles; no frozen object, verdict, log or registry entry is edited
by this document; freeze + registration + run are the coordinator's.
