# F1-K freeze-readiness checklist (coordinator custody path)

> **Status:** freeze package emitted (designer-5, 2026-07-13) and REVISED the
> same day after the cross-vendor codex review returned **FIX-FIRST**; all
> five review items are applied. Record: `registry/experiments/f1k.json`
> (DRAFT, kot-reg/1); `tools/registry/prereg-freeze.py --dry-run` is
> **DRY-RUN-OK** on the revised record (every freeze-time lint green; the
> PAUSE flags are the non-fatal open-extrapolation scan, by design).
> This pass took no git action, wrote no `registry/assumptions.jsonl` entry,
> and ran no freeze. Companion ASMs: ASM-2270..2278 (centrally REGISTERED)
> + **ASM-2280..2283** (`docs/next/design/asm-f1k-freeze-2280-2283.json`,
> emitted, PENDING central registration). No feasibility conclusion anywhere
> in this package.

## What the FIX-FIRST revision changed (so the coordinator re-verifies the right things)

- **K-2 exactness basis made explicit (ASM-2280):** the K-2 sign-flip is
  exact only under an EXPLICIT cluster sign-symmetry assumption on
  D_c = mean(K − mean_R d1-drng); four-arm exchangeability alone yields
  ~6.28% type-I at C = 72 (the review's counterexample). Registered in the
  record's K-2 endpoint text + `n_planned.statistics`.
- **BCa fallback branch IMPLEMENTED (ASM-2281):** `analysis/f1k.py` now
  carries both branches; the sidecar `inference {method,
  dev_sign_symmetry_pass}` block (§R-REV4.1a dev-selected choice, frozen at
  addendum (6)) is mandatory and coherence-checked fail-closed; method
  reported at `/analysis/inference_method`; K-1/K-2/K-3 cluster-BCa 95% CIs
  are registered outputs (`/analysis/k1_ci95`, `k2_ci95`, `k3_ci95`).
- **Validation hardened (ASM-2282):** n = 1,440 EXACT (a 520-item campaign
  is rejected, not analyzed), arm item supersets rejected, strictly binary
  correctness, ceiling threshold immutable at 0.95, REPLACE run/coverage
  coherence — all fail-closed `ERR_P2_ANALYSIS`. Output surface 47 → **50**
  fields; script re-pinned (new sha below).
- **Budget resolved (ASM-2283, successor of ASM-2277):**
  `budget.usd_cap = 149` — the validated reduced ceiling of
  `docs/next/design/glm52-f1k-cost-reduction.md` (ASM-2205, in-repo,
  centrally registered). No superseded-ceiling figure remains in the record
  or the analysis.
- **Freeze manifest (A)/(B0) specified in the record:**
  `design.n_planned.freeze_manifest` — (A) = the complete carrier GENERATOR
  (contexts, texts, layers, formulas, norm/rescale rules) + map/trigger/
  template inputs + id-list hashes + ALL seeds + the dev sign-symmetry check
  procedure, committed **before ANY spend**; (B0) = realized carrier tables
  + raw/rescaled norms, committed **before the pilot**.

## A. Before prereg-freeze (blocking) — pin/verify list, in order

1. **Verify the analysis pin (re-pinned this revision).** Recompute
   `sha256(analysis/f1k.py) ==`
   `5dbf896cffaf9ed3a9dad34f884489f2b252f0a5b8c22275427cb8a2cde8e5eb`
   and re-run `python3 analysis/f1k.py --selftest` (must print
   `MOCK-SELFTEST PASS`, exit 0, ~9 s: PASS shape on BOTH inference
   branches, TOST NULL shape, 6/6 hardened rejections, 50/50 fields). Any
   byte change = new sha = re-freeze. [ASM-2282]
2. **Verify the budget.** `budget.usd_cap == 149` (ASM-2205 reduced-cost
   protocol; cap-not-target). Constraint (§R6): no reduction may cut n
   below 1,440 or drop a ladder arm (b0/d0/d1-drng/d2/K). [ASM-2283]
3. **Central ASM registration (the one PENDING block).** Register
   **ASM-2280..2283** (`docs/next/design/asm-f1k-freeze-2280-2283.json`)
   with the landing commit, after the standing review gate. ASM-2282/2283
   are supersede-by-citation SUCCESSORS of ASM-2276/2277 — register them so
   the chain resolves. All earlier blocks (design 2024..2130, patch
   2180..2190, package 2270..2278, cost 2205) are ALREADY in
   `registry/assumptions.jsonl` (verified 2026-07-13).
4. **Law-1 scoped amendment — a DISTINCT GOVERNANCE EVENT, coordinator-
   registered (GATE 0, ASM-2025).** "Kernel-derived content vectors may
   enter model activations ONLY within the KaE track, only via the
   registered splice, deflator ladder mandatory." This is NOT part of this
   freeze package and is NOT implied by the #28 GO or by prereg-freeze: the
   coordinator registers it as its own explicit registry event BEFORE any
   run. Nothing in this package performs or substitutes for it.
5. **Verify the KaE patch pins** (gate-0 artifact, REVISION-1):
   `poc/glm52-probe/kae-patch-draft/kae-add-path.patch` sha256
   `11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb`,
   `kae.h` sha256
   `e2574873115b5109ca87123e29286ea89ce8955655a31fc158225be52fb21ddd`,
   colibri base commit `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`. The
   record's envelope binds to exactly these; if gate-0 review amends the
   patch, re-pin BEFORE freeze.
6. **Verify the two doc pins** (`prereg_doc` + `analysis_plan_ref` both =
   `docs/next/design/glm52-followup-experiment.md` sha256
   `9f18e5e09f5c8a2a933f3446697daf5849676447004540398237da7f8e67f2b6`).
   Any further design revision re-hashes the doc → update both pins.
7. **Verify the kernel corpus pin reproduces**: `pins.corpus_hashes["kernel-v0"]
   == 8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809`
   (kot-corpus-hash/1 over `data/kernel-v0/`; the three `PINNED-AT-INPUTS:*`
   placeholders are P-9 and exempt at freeze).
8. **Run `prereg-freeze.py`** (coordinator only). `--dry-run` was green at
   emission of this revision (schema, single primary, pointer closure over
   all 50 declared fields, catch-all, five-V, pins byte-verified, kernel-v0
   reproduced, placeholders accepted; expect the non-fatal PAUSE flags for
   the open extrapolations incl. ASM-2205 — conclusions stay hard-gated,
   experiments are not blocked). Then commit + push per session protocol.

## B. Ops amendments the freeze pre-declares (P-9 placeholders — complete
## in this order, per the §R-REV4.2 corrected sequence; full component spec
## now in the record at `design.n_planned.freeze_manifest`)

9. **Freeze-manifest (A)** — committed **before ANY F1-K spend**
   (construction included): the complete carrier GENERATOR — (i) m = 16
   construction contexts/concept, (ii) explication + d2 definition texts
   (hashes), (iii) prepend/gated-position rules, (iv) the candidate splice-
   layer set, (v) the mean-difference formula, (vi) the reference-norm +
   per-(c,l) rescaling rules, (vii) ALL seeds (construction; pilot-panel
   derangement **11**; d0 table **7**; main derangements **101, 102, 103**
   — must equal `design.seeds` and `analysis/f1k.py DRNG_SEEDS`, the dose
   gate fails closed otherwise) — plus template bytes+sha, single-token
   label verification, tie-break, trigger-map hash, guard/dev/test id-list
   hashes, derivation rules for addenda 5/6/7, the §R-REV5 Monte-Carlo
   procedure + seed, and the **§R-REV4.1a dev sign-symmetry check
   procedure** (whose outcome (6) freezes `inference.method`).
   → completes corpus pin **`f1k-trigger-map-v1`**.
10. **Construction spend → B0 addendum** — committed **before the pilot**:
    realized carrier tables for every arm (K, 3 derangements, d0, d2) + raw
    and rescaled norms, each a pure function of an (A) generator rule.
    → completes **`f1k-carriers-v1`**.
11. **Eval item lists**: mechanical filter output frozen as test-1440/dev-96/
    guard-60 id lists + frozen scored templates + per-item span sidecars.
    → completes **`f1k-eval-v1`** (before any test prefill, with (6)).
12. **Bring-up (addendum 7, PRE-test gate)**: measured s/prefill +
    affordability projection vs the frozen **$149** cap (degradation order
    applies deterministically), colibri knob-semantics re-verification
    (ASM-1971), and **`glm52-weights`** content hash pinned on the
    relaunched instance.
13. **Power freeze (addendum 6, PRE-test)**: dev δ̂ → n_required; the hard
    power gate = **≥65 clusters EACH with ≥8 items at exactly n = 1,440**
    (each-cluster reading, ASM-2271; the analysis REJECTS any other n);
    **freeze `inference.method` from the dev sign-symmetry check**
    (§R-REV4.1a — sign-flip iff the check passes, else the implemented BCa
    fallback; the sidecar block must be coherent or the analysis fails
    closed); REPLACE run/defer at ρ_U = 0.10 (RUN only if dev
    δ_R ≤ ~0.038, §R-REV4.3); execute the frozen §R-REV5 exact-power
    Monte-Carlo (pass ≥ 0.80 at μ* = +4.09 pts; realized power into the
    sidecar → `/analysis/power_scope`).

## C. Run-time contract the freeze binds (for the runner, FYI)

- Verdict path: eligible results-log records → `analysis/f1k.py` on STDIN;
  each record's `artifacts` pins `rows_path/rows_sha256` +
  `sidecar_path/sidecar_sha256` (all records must pin the same tuple);
  rows/sidecar shapes documented in the script docstring. The sidecar MUST
  carry `inference {method, dev_sign_symmetry_pass}` and may echo but never
  move `b0_ceiling_threshold` (0.95, immutable).
- Hardened rejections (ERR_P2_ANALYSIS, not verdicts): n ≠ 1,440; any arm
  scoring items outside the b0 universe; non-binary correctness; mutated
  ceiling threshold; REPLACE rows/sidecar incoherence or partial coverage.
- Off-concept guard: 60 items byte-identical to b0 in every spliced arm —
  one mismatch voids (gate, not kill). d0 placebo fires at p < 0.05 alone
  (no +3 floor, ASM-2273) — void.
- KAE knob unset everywhere except registered F1-K arms; DRAFT=0; scoring
  via `KAE_SCORE` (one prefill/item/arm, label-logit argmax).

## Gaps at this revision (honest list)

- ASM-2280..2283 pending central registration (item 3) — the only pending
  ASM block.
- Law-1 amendment not yet a registry event (item 4) — a distinct governance
  event the coordinator will register; deliberately NOT bundled here.
- Three corpus placeholders + `glm52-weights` pin await their ordered ops
  amendments (items 9–12) — by design, not by omission.
- ASM-2205's $149 is an open EXTRAPOLATION resolved only by the metered
  run's cost ledger; the bring-up gate (item 12) is where a miss surfaces
  pre-test.
