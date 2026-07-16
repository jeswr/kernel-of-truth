# GLM-5.2 expert-profiling — Stage-3 causal characterisation summary

**EXPLORATORY infra** (rigor relaxed vs a frozen experiment). This turns the Stage-2
routing-affinity atlas (evidence_level 0 — what routes *where*) into **causal**
evidence (what an expert actually *does*), for a stratified ~32-expert shortlist, to
validate a first **safe-to-drop / substitute skip-list** for colibri's `EXPERT_BUDGET`.
All classification thresholds are STIPULATED (documented, not measured); the primary
causal endpoints (target-NLL, gold-logit margin, exact correctness) are exact, the
top-K KL is an approximation.

## What was built + proven ($0)

- **`abl.h` + `ablation-add-path.patch`** — extends the rtrace approach. `moe()` gains
  three guarded hooks: route-around (drop the cell from the selected set before
  renormalise, FASE A), module-swap (remap the slot to a substitute expert, FASE A),
  contribution-zero (skip the weighted accumulate, FASE C). All inert when
  `g_abl.mode==0` → **byte-identical to the rtrace build for unlisted experts.** New
  `ABLATE_SCORE`/`ABLATE_OUT` path reads out the FINAL logits per target position.
- **`test_ablate.c` — 18/18 checks pass**: baseline==unpatched, ablating an unused cell
  is a no-op, per-item reset, and each arm's exact semantics.
- **Real-model inertness proof** (`stage3_tiny`, tiny GlmMoeDsa): baseline vs
  ablating-an-UNUSED-cell = **0.0 logit diff (byte-identical)**; ablating a SELECTED
  cell moved logits by 0.215. Both unit tests are fail-closed gates at image build.

## The shortlist (32 experts, 9 strata)

| stratum | n | cells (main\|layer\|expert) |
|---|---|---|
| lead_format (xml/csv → grammar/emitter) | 5 | 56\|45, 63\|217, 17\|233, 69\|149, 60\|243 |
| lead_copy (chinese copy → pointer/index) | 5 | 43\|152, 41\|141, 44\|177, 32\|119, 63\|204 |
| lead_arithmetic (→ exact evaluator) | 5 | 36\|239, 44\|227, 18\|224, 45\|245, 42\|66 |
| specialist_science | 2 | 61\|193, 59\|9 |
| specialist_legal_fin | 2 | 19\|15, 72\|206 |
| specialist_multiling | 2 | 15\|131, 57\|190 |
| generalist (high-load, flat domain) | 5 | 16\|108, 15\|159, 36\|38, 38\|98, 15\|48 |
| control_rare (low-load, expect inert) | 4 | 60\|196, 46\|250, 70\|222, 73\|120 |
| control_mid_none (mid-load non-specialist) | 2 | 37\|89, 26\|246 |

Each expert gets 10 activation-max on-domain items (Stage-2 `top_contexts` + label-matched)
and 8 matched off-domain controls; the 15 format/copy/arith leads also get a module-swap
arm to a generic same-layer substitute expert. **244 unique items → 1,546 prefills**
(244 baseline + 1,152 contrib/route + 150 swap).

## Ablation design (per shortlisted cell)

- **baseline** (once per item) · **contribution-ablation** (routing kept, output→0) ·
  **route-around** (dropped + renormalised) · **module-swap** (leads; generic substitute).
- Per target position, paired vs baseline: **ΔNLL** (nats/tok), **Δgold-logit-margin**,
  **top-K KL**, **Δexact-correctness**. Item-level bootstrap CIs.

## Classification rules (STIPULATED thresholds — `stage3_analyze.py::TH`)

Route-around ΔNLL is the primary drop proxy (what dropping the expert actually does);
contribution-ablation is the upper bound. LOW=0.05, MID=0.15, HIGH=0.40 nats/tok;
correctness-drop 5%; swap "holds" if it leaves ≤40% of the route harm.

- **SAFE-TO-DROP** — low harm on-domain AND off-domain, no correctness loss.
- **LOAD-BEARING** — large on-domain harm, or a correctness drop, or broad off-domain harm.
- **DETERMINISTIC-REPLACEABLE** — harm concentrated on-domain (off-domain low) AND the
  module-swap arm recovers quality.
- **CHARACTERISE-MORE** — the ambiguous middle.

Causal confidence = evidence agreement (coverage · route-sign stability · contrib↔route
sign agreement · on-vs-off contrast), bucketed high ≥0.66 / med ≥0.40 / low.

## Cost

Config: OCI, 4 cores / 64 GiB / 900 GiB ephemeral, RAM_GB=55 (proven GO-FULL-GLM52
backend). Projection: $9 (16 s/prefill) – $18 (35 s/prefill); 22 h / $55 in-runner
wall stop-loss, $60 hard cap. Staging 383.8 GB ≈ 23 min.

---

## RESULTS

_[PENDING run completion — filled from `stage3_analysis.json` on the output Volume
`kot-glm52-stage3-out/full`. Headline: label counts (SAFE-TO-DROP / LOAD-BEARING /
DETERMINISTIC-REPLACEABLE), skip-list size + causal-confidence, measured $/h, and
honest scope. Recompute locally: `stage3_analyze.py --deltas … --shortlist …`.]_
