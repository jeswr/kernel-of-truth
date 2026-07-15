# F1-K REVISION-6 freeze memo — maintainer-approved powered geometry (2026-07-15)

> **Status at emission (designer-32, 2026-07-15):** freeze-ready build of the
> deciding four-condition kernel-vs-generic CORRECTNESS test (F1-K rungs
> K-1/K-2/K-3) on the maintainer-approved geometry **C=96, n=1573,
> mu\*=+4.09 pts, R=(1,3,1)**; K-3 promoted to **CO-PRIMARY**. Companion ASM
> block: `docs/next/design/asm-f1k-geometry-2369-2375.json` (central
> registration = coordinator action with the landing commit). Everything in
> this pass is LEFT UNCOMMITTED for the coordinator. No campaign was run; no
> GPU; $0 spend this pass.

## What changed vs the 2026-07-13 freeze package (ASM-2270..2283)

| Item | Was | Now (REVISION-6) | ASM |
|---|---|---|---|
| n (test, exact) | 1440 (cap) | **1573** (cap raised by maintainer after the registered pre-run power return: K-3 0.7955 at n=1440) | 2369 |
| Power gate | C>=65 each m>=8 @ n<=1440 | **>=96 clusters each m>=8 @ exactly n=1573** | 2369 |
| Concept universe | kernel-v0-frame (49 realized clusters — gate unsatisfiable) | the frozen 96-concept askability selection (45 v0 + 51 v1), redacted-input hash `4f7cf1c6…` | 2369/2372 |
| K-3 role | secondary ("elevates wording, never verdict") | **CO-PRIMARY: pass_gate = k1 AND k2 AND k3; a K~d2 tie DENIES PASS** | 2370 |
| Power at mu*=+4.09 | K-3 0.7955 (FAIL) | **K-1 0.8043 / K-2 0.8058 / K-3 0.8001 (all PASS)** [MEASURED, seed 20260713] | 2371 |
| Budget | $149 | **$155 / ~555 instance-h / 0 GPU-h**; REPLACE runs only if ledger projection stays <= cap | 2374 |
| Text pins | (A)-deferred | **data/f1k-contrast-v1** pinned NOW (`c6eb8294…`); kernel-v1 pinned (`f2c84727…`) | 2375 |
| analysis/f1k.py | sha `5dbf896c…` (n=1440, pass=k1&k2) | sha **`9d01468e…`** (n=1573 exact, C=96 gate, pass=k1&k2&k3, K~d2-tie mock) | — |

Unchanged, deliberately: mu\* (+4.09 pts), the +3.0-pt licensing floor, the
TOST ±3.0-pt SESOI on K-1, alpha, seeds (101/102/103; pilot 11; d0 7; power
20260713), B=10000, the dev-selected sign-flip-vs-BCa machinery
(SSR-REV4.1a), all instrument gates (placebo-voids-at-any-magnitude, guard
byte-identity, dose exactness, template checks), the kill criterion's harm
rule, the verdict-rule tree, and the freeze-manifest (A)/(B0)/5/7/6 ordering.
**The geometry was re-powered; no bar was lowered.**

## Power table at the frozen geometry (MEASURED, `power-report-n1573.json`)

| Rung | Contrast | R | Joint power @ mu*=+4.09 | MC-SE | 80%-MDE (pts) |
|---|---|---|---|---|---|
| K-1 | K vs b0 | 1 | **0.8043** | 0.0040 | 4.072 |
| K-2 | K vs mean of 3 derangements | 3 | **0.8058** | 0.0040 | 4.063 |
| K-3 | K vs matched dictionary (d2) | 1 | **0.8001** | 0.0040 | 4.090 |

Procedure byte-identical to the screen's pre-registered SSR-REV5 sim (exact
cluster sign-flip, fire iff p<0.05 AND T>=0.03, delta=rho_U=0.10, seed
20260713, N_sim=10000, B=10000 add-one); the ONLY change is N_TEST 1440→1573.
Allocation realizes n=1573 exactly at C=96: m_min 10, m_mean 16.3854, m_max
18, every m>=8. Selection re-derived byte-identically from the pinned
corpora; redacted-input hash re-verified before the sim.

## Condition ledger (the four-condition test)

- **(i) validated instrument — NOT MET; disclosed, not waived [ASM-2373,
  open EXTRAPOLATION].** The 96 explications are kernel-v0
  (explicator-authored) + kernel-v1 (pipeline-minted) texts validated
  mechanically (kot-ast/1, encoder loop) and by LLM proxy only. **No human
  fidelity validation exists.** Verdict: PROXY instrument → **any F1-K PASS
  is PROXY-PROVISIONAL**, stated verbatim in the record, the K-3 endpoint,
  and the envelope. A PASS licenses "these 96 kernel-record texts, as
  carriers, beat matched dictionary glosses at this model/box" — not
  "validated NSM explications beat dictionaries". Resolution path: human
  fidelity pass over the pinned `data/f1k-contrast-v1` texts.
- **(ii) kernel-as-text control — met by design** (d3-text arm, mandatory).
- **(iii) shuffled-kernel control — met by construction** (d1-drng: R=3
  seeded label-derangements of the IDENTICAL carrier set, dose-exact; K-2).
- **(iv) certified kernel-vs-generic contrast — met, MEASURED** (96/96:
  hashes differ, NLD>=0.20 min 0.387 median 0.738, prompt-hash-diff rate
  1.00, outside-payload diff 0) [ASM-2372].

## Pre-freeze skeptic self-attack (what survives, verbatim residuals)

1. **K-3 knife-edge (RESIDUAL, disclosed).** 0.8001 clears 0.80 by 1e-4 at
   MC-SE 4e-3. The frozen-seed point estimate under the pre-registered
   procedure is the registered pass rule and it passes; but true K-3 power
   plausibly sits anywhere in ~0.79–0.81. Consequence if unlucky: a K-3
   non-fire under a true +4.09 effect — scoped by the MDE wording, never a
   clean null; the record cannot overclaim from it.
2. **Co-primary intersection (RESIDUAL, now in the record).** Per-rung
   power >=0.80 does NOT give >=0.80 probability that ALL THREE rungs fire
   together (correlated through the shared K arm; unmodelled). Full-PASS
   power at mu\* is plausibly ~0.70–0.75. Consequence: elevated
   INCONCLUSIVE risk (2-of-3 shapes), never a false null. Registered as an
   n_planned assumption; the maintainer criterion (per-rung >=0.80) is what
   was approved.
3. **Geometry chosen after seeing the shortfall (ATTACK DEFEATED).** The
   n=1440→1573 raise followed the screen's power verdict — but the screen
   is gold-label- and model-outcome-BLIND ($0, no model call), the pre-run
   return→maintainer-amend path was itself pre-registered (SSR-REV2.2), and
   n moves power only, never the statistic or the bar. No outcome data
   existed to fork on.
4. **delta=0.10 planning variance shared across rungs (RESIDUAL).**
   Conservative for K-2 (averaging lowers variance); for K-3 the realized
   K-vs-d2 paired-diff variance is unmeasured until dev. If it exceeds
   0.10, realized power drops; the addendum-(6) re-execution + power_scope
   MDE wording carry the honest scope. No licensing quantity depends on it.
5. **Length/richness confound K vs d2 (RESIDUAL, inherent).** Kernel
   explications are longer than WordNet glosses (lengths disclosed in the
   distinctness report). Carrier DOSE is norm-matched per (c,l) (SSR2), but
   information content cannot be "matched" without destroying the contrast
   — the dictionary IS the generic comparator. Triangulation: K-2 holds
   content constant and breaks alignment; d0 holds dose and removes
   content; d3-text carries the identical text through the prompt seam. A
   K-3-only win with a K-2 fail cannot happen under the co-primary rule.
6. **Reserve substitution not yet operationalised (OPEN → (A)).** Ranks
   097–116 are pinned, but the substitution rule (when a selected concept
   dies at construction) must be written into freeze-manifest (A) verbatim
   before any spend. Flagged for the (A) ops amendment; not a freeze
   blocker (the 96 selected all pass every screen gate today).
7. **Analysis constants doubly stated (CHECKED).** n=1573/C=96/pass-rule
   live in analysis/f1k.py (sha-pinned) AND the record text; selftest
   asserts the geometry and the K~d2-tie denial shape, so drift fails the
   mock, and any script edit is a new sha = re-freeze.

## Dry-run / freeze result

- `prereg-freeze.py --dry-run` (writer-2, 2026-07-15): **DRY-RUN-OK** — every
  freeze-time lint green (schema, single role:primary, pointer closure over
  all 50 declared fields, catch-all, five-V, kill+envelope, pins
  byte-verified incl. the re-pinned analysis sha, corpus pins kernel-v0 /
  kernel-v1 / f1k-contrast-v1 reproduced, 3 PINNED-AT-INPUTS placeholders
  accepted, no reuse collision, RT-14 clean).
- **FROZEN** 2026-07-15T16:42:27Z by writer-2 (= this designer pass; the
  RT-14 pseudonym enum has no `designer-*` role, so the record-authoring
  `writer` role is used):
  `frozen_sha256 = 4541966640b391e50824765955447bcef103f94241e32b70e76a5c7f77e18079`
  → `registry/frozen-index.json`. RT-15 post line (coordinator, hash-only):
  `prereg freeze f1k frozen_sha256=4541966640b391e50824765955447bcef103f94241e32b70e76a5c7f77e18079`.
- Non-fatal PAUSE flags (open extrapolations, by design; recorded in
  `registry/pause-flags.jsonl`): ASM-2021, ASM-2032, ASM-2041, ASM-2048,
  ASM-2205. ASM-2373 (the proxy-instrument extrapolation) will join this
  set once the coordinator centrally registers ASM-2369..2375 — the
  PROXY-PROVISIONAL discipline is carried in the frozen record text either
  way, and conclusions stay hard-gated at claims-check/verdict-gen.

## Coordinator checklist delta (vs f1k-freeze-readiness.md items A.1–A.8)

- A.1 analysis pin: sha is now `9d01468e99c61d71fd47235614795ea3bb976e3ea184e96899d4dd11b86286a7`; selftest green 2026-07-15 (~17 s).
- A.2 budget: `usd_cap == 155` (ASM-2374, successor of ASM-2283).
- A.3 central ASM registration: **ASM-2369..2375** pending (coordinator, with
  the landing commit); 2270..2283 already registered.
- A.4 Law-1 scoped amendment: STILL OUTSTANDING, still a distinct
  coordinator governance event before any run. Unchanged by this pass.
- A.5/A.6 KaE patch + doc pins: unchanged, re-verified at dry-run.
- A.7 corpus pins: kernel-v0 reproduces; NEW pins f1k-contrast-v1 +
  kernel-v1 reproduce; 3 PINNED-AT-INPUTS placeholders remain (by design).
- A.8 freeze: performed by designer-32 per the maintainer build order IF
  dry-run green + no validity red-flag (the ASM-2373 proxy bar is a
  disclosed caveat carried in the record, not a red-flag that blocks the
  freeze); coordinator commits.
