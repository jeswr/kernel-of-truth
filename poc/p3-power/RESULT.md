# P3-D-POWER — coverage-ceiling paper-kill: execution RESULT

**Run by:** Fable (autonomous worker), 2026-07-11 · **Rig:** `poc/p3-power/power.py`
· **Design:** `docs/next/design/POWER.md` (rev 2) · **Steering:** `docs/next/analysis/round1-steering.md`
(the top cheap decisive kill) · **Governance:** no git / no bd / no kb-sync ·
**registry-check: PASS** (no frozen registry object touched; outputs confined to `poc/p3-power/`;
no verdict / no KB shard written).

Tags per line: **[MEASURED]** = observed count / computed upper bound · **[STIPULATED]** =
registered design placeholder · **[EXTRAPOLATION]** = a forward conclusion the coordinator/maintainer
must draw, not this rig.

---

## The number

| Quantity | Value | Tag |
|---|---|---|
| **Δ_max (general index, simUCB95)** — MEASURED define-lane census | **0.8095** | **[MEASURED upper bound]** |
| δ_k (provisional win margin) | 0.03 | [STIPULATED] |
| **Kill arithmetic** `simUCB95(Δ_max) < δ_k`? | **0.8095 < 0.03 = FALSE** | [MEASURED] |
| **Clears δ_k for a kill?** | **NO** | [MEASURED] |
| Verdict | **ILLUSTRATIVE-ONLY — no G1 verdict** | [MEASURED: rig gate] |

The run is **NOT verdict-eligible**: provisional pin `frozen=false`, no census pin block, no
registered Form-A eligibility. By POWER.md §4 step 0 the rig emits no verdict of any kind — as designed.

## What actually happened (and why it is NOT the free general-index kill the premise expected)

The steering note (item 3) says *"the general-index W1 ambition is probably already dead"* and books
this as the cheap zero-GPU kill. **Run honestly, the rig does not deliver a general-index kill from the
existing censuses** — and the reason is decisive and worth surfacing:

- The measured census covers **exactly one domain (D3)** of a **six-domain** index.
- The kill-soundness completeness rule (POWER.md §3.1, review blocking finding 1) imputes **FULL
  HEADROOM** to every uncensused component — no silent zeros. So the 0.8095 general-index ceiling
  decomposes as:

  | Component | Δ_max contribution | Status |
  |---|---:|---|
  | D3 — 7 define-lane benchmarks, **0/1550 covered** | **0.0000** | **[MEASURED]** censused |
  | D4 CLUTRR + ProofWriter (uncensused) | 0.2595 | full headroom |
  | D1, D2, D5, D6 (empty weighted domains) | 0.5500 | full headroom |
  | **Σ = Δ_max (simUCB95)** | **0.8095** | |

  **0.81 of the 0.81 is imputation for what was never measured; the MEASURED slice contributes 0.**

- Consequence (the rig's own guarantee): *a partial census can only make a whole-index kill **harder**,
  never easier.* A general-index kill (`Δ_max < δ_k`) is **arithmetically impossible** while any
  material index weight is uncensused. **[MEASURED]**

## What the MEASURED data DOES support

- **D3 domain-own-axis ceiling = 0.0000** vs δ_k^D3 = 0.05 **[MEASURED]**. On the censused biomedical-
  define slice, perfect covered-item correction yields **exactly zero** index gain because 0/1550 items
  are covered. A **domain-scoped D3 kill** (`0.0000 < 0.05`) **would fire** — but only on a verdict-
  eligible run. It is currently **CONTINGENT** (mapper-parse lane) and **ILLUSTRATIVE-ONLY**.
- **Route statement, per-benchmark:** κ*_b = **0.682** **[EXTRAPOLATION, provisional pin]** — no single
  D3 benchmark can carry δ_1 = 0.03 below ~68% coverage under the provisional weights. An ingestion-
  scale fact, not a verdict.

Branch-exercise only (RUN-2, `census-D4-hypothetical.STIPULATED.json`): Δ_max simUCB95 = **0.8658**,
NO KILL, D4 own-axis 0.3402, κ* 0.1453 — **[STIPULATED]**, placeholder inputs, not evidence.

## Does it kill the general-index-mover claim?

**Not for free from the existing censuses. [MEASURED bound → EXTRAPOLATION is the coordinator's.]**
The rig proves you *cannot* get a general-index kill from a one-domain census. What it hands the
coordinator is: (1) a MEASURED zero-coverage D3 slice that supports a **domain-scoped** kill once
eligibility lands, and (2) arithmetic that a whole-index kill needs a whole-index census first.
**The free kill that exists here is domain-scoped, not general-index** — a material correction to the
steering premise. Whether "the general index is dead" is the maintainer's/coordinator's call, and it
is **not licensed by this data**.

## Real data still needed (for a verdict-eligible GENERAL-index kill)

1. A **frozen** P3-D-INDEX pin (`frozen=true`) enumerating chance/ceiling/metric_type for **every**
   benchmark of **every** weighted domain (the provisional pin has 4 empty weighted domains).
2. A coverage census over the **whole frozen R-1 suite** — `P3-X-SIEVE-CENSUS` (mechanical lemma-touch
   sieve; cheap; gives UNCONDITIONAL kills) and/or `P3-X-ORACLE-CENSUS` (human-annotated; budgeted; not
   ~$0). The existing censuses are one-domain and biomedical-skewed.
3. The full **census pin block** (§2.2) and a **registered Form-A eligibility** ref per family (P3-D-ELIG).
4. Covered-subset baseline counts (`correct_cov`/`n_cov`, P3-X-COVBASE) — only where κ > 0.

**For the cheap near-term DOMAIN-SCOPED D3 kill:** only #1 (frozen pin) + census pin block + eligibility
ref are missing; the coverage measurement (0/1550) already exists. That is the reachable free kill.

## Inputs adequacy

The MEASURED input (`census-define-lane.MEASURED.json`, provenance
`registry/assessments/b-cov-define-lane.json`) is **real and sufficient to compute the bound** and to
establish the D3-slice zero. The **index pin is a demonstration placeholder** (`frozen=false`), which is
why no verdict issues. This is not a rig or data failure — it is the designed fail-closed posture: the
existing censuses are adequate for a *domain-scoped, contingent* reading, and **structurally inadequate
for a general-index verdict** until the frozen-suite census + pin land.
