# FALSIFIER-1 Stage-0a readout — $0 routing-trace re-analysis (DESCRIPTIVE ONLY)

**Verdict: `PROVISIONAL-NEEDS-0b` (hard-coded at this tier — spec §3 A6).**
Stage-0a CANNOT license DEAD or GREENLIGHT: no predictability estimate exists in
committed bytes; the ASM-2505 kill line applies only at Stage-0b/Stage-1.

Spec: `docs/next/design/candidate-a-stage0-measurement.md` §3 (v3; GPT-5.6
re-review approved Stage-0a to run as designed). Script:
`poc/glm52-probe/analyze_residual_v1.py` (stdlib, deterministic, seed 20260712,
repeat-run byte-identical). Data: committed bytes only, read-only, at commit
`d594844`; sha256 of every input pinned in the JSON provenance block. Full
numbers: `poc/glm52-probe/results/falsifier1-stage0a.json`.

## A1 — Pin reconstruction + residual (verification anchor: PASSED)

- Top-2,696 cells of `accum20.stats` (count desc, tie-break (layer,expert) asc)
  reproduce **h_pin = 0.762844 → 0.7628** [MEASURED, = m4.json G50 anchor;
  fail-closed check passed; G40 = 0.7132 and G100 = 0.9032 also reproduce].
- Residual mass **0.237156** [MEASURED, in-sample] — an **optimistically
  LOW-biased in-sample point estimate, NOT an out-of-sample floor**: the pin is
  ranked and scored on the same histogram; the true out-of-sample residual is
  likely higher.

## A2 — Residual concentration / STATIC-residency GB economics

Scope: bounds **static / prompt-level residency levers only** (ASM-2511
[STIPULATED]); token/layer-conditioned swapping is not bounded here.

| Target (total selection hit) | Extra cells | Extra GB beyond the 50 GB pin | Total GB |
|---|---|---|---|
| +5pp (→ 0.8129) | 705 | **13.07** | 63.07 |
| +10pp (→ 0.8629) | 1,650 | **30.59** | 80.59 |
| → 0.90 | 2,600 | 48.21 | 98.21 |
| → 0.95 | 4,557 | 84.49 | 134.49 |
| → 0.99 | 8,244 | 152.86 | 202.86 |
| full observed tail (1.00) | 13,488 | 250.09 | 300.09 |

All [MEASURED, in-sample on the F1-K accum20 histogram; per-expert tensor
18.54 MB decimal-GB accounting per m4.json]. The next 5pp is ~26% extra static
RAM; the tail flattens hard after that.

## A3 — Hot-set stability on the 23 differenced D1 fingerprints

**Prompt-fixed diagnostic under a DISCLOSED corpus + execution-config mismatch**
(D1: MTP-active draft=3, experts INT8, 78 layers [MEASURED, f000.out:2,9] vs
the target 75-layer int4 DRAFT=0 config; layer-78 cells excluded both sides,
excluded mass ≈ 1.25% of D1 selections). NOT clean OOD evidence: a low hit is
ambiguous between concept-corpus shift and config shift.

- Per-prompt hit of the A1 pin: **median 0.2466, min 0.2241, max 0.2673,
  mean 0.2461**; BCa 95% CI for the median **[0.2392, 0.2518]** (n=23 — wide
  by construction, reported anyway) [all MEASURED].
- Read: on this shifted prompt set the static G50 pin captures only ~25% of
  selections vs 76% in-sample — a large descriptive stability gap whose cause
  (corpus vs config) this tier cannot apportion.

## A4 — Prompt-level oracle gap (same disclosure)

- Oracle per-prompt pin at the matched 2,696-cell budget: hit 0.7266–0.7816
  (median 0.7602) against static 0.2461 mean → **Δ_oracle mean 0.5146**
  (median 0.5143), BCa 95% CI **[0.5109, 0.5187]** [MEASURED].
- Each fingerprint touches only ~4,924–5,977 positive cells, so a
  prompt-conditioned pin at the same budget covers ~76% of that prompt's
  selections. Δ_oracle bounds **prompt-conditioned** residency policies on this
  config-mismatched prompt set only; it is NOT a bound on within-sequence
  token-level swapping (ASM-2511 [STIPULATED]), and disk bandwidth caps
  swapping in practice.

## Honest read

Descriptively, the exploitable static headroom looks real but priced: ~24pp of
selection traffic (in-sample, biased low) sits outside the 50 GB pin, and the
next 5pp/10pp of static coverage cost ~13/~31 GB of additional resident RAM
(the tail flattens hard after ~0.86). The prompt-level oracle gap (~51pp on the
shifted D1 set) says prompt-conditioned residency could in principle capture
far more than the static pin — but whether any of that residual is
*predictable* (the actual FALSIFIER-1 question) is **not measurable from
committed bytes**: the committed atlas drops the family-conditional maps, and
its own coverage gates FAILED (0.825 mass on ≥100-event cells vs ≥0.95 gate;
0% of layers pass the Spearman ≥0.8 gate; 10,266/19,200 cells rare
[MEASURED, coverage_gates.json]) exactly in the non-resident region at issue.
**The FALSIFIER-1 verdict awaits Stage-0b** (raw D6 trace retrieval,
ASM-2509); the kill/greenlight thresholds (5pp/10pp, ASM-2505 [STIPULATED])
apply there, not here.

Caveats carried in full in the JSON `caveats[]`: descriptive-only; in-sample
pin bias; A3/A4 config confound; no predictability estimate at this tier;
A2 static-scope limit; failed atlas coverage gates; n=23; session-cumulative
D1 recovered by fail-closed first-differencing.
