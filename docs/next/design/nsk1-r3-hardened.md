# nsk1-R3 hardened — CONFIRMATORY re-run of the internal-write keyed-delivery finding (design)

- **Author:** Fable experiment-designer role, 2026-07-13. Successor to the
  internal-write measurement arc B′ → B″ → Stage-1
  (`docs/next/nsk1-bprime-stage0-spec.md`, `docs/next/nsk1-bprime2-spec.md`,
  `docs/next/nsk1-stage1-spec.md`), commissioned by the coordinator to convert
  the **PASS-QUALIFIED, Gate-A-verified** B″ delivery positive into a
  **pre-registered confirmatory** record that repairs the three qualifications
  the cross-vendor Gate-A audit carried into R3
  (`docs/next/analysis/nsk1-bprime-gatea-verdict.md`).
- **Status:** DESIGN, launch-prep only. nsk1-r3 is **DRAFT / NOT FROZEN**. No
  prereg-freeze, no GPU/Modal spend, no git action is taken by this document.
  The draft registry skeleton is `registry/experiments/nsk1-r3.json` and the
  pinned analysis is `analysis/nsk1_r3.py` (both uncommitted, for coordinator
  review).
- **Honesty-guard:** every load-bearing line is tagged
  MEASURED / MEASURED-exploratory / STIPULATED / LIT-BACKED / EXTRAPOLATION.
  Design choices are STIPULATED, never presented as measured. New assumptions
  ASM-2353..ASM-2359 are named here and registered by the coordinator **at
  commit** (§10); this document writes no register entry and takes no git
  action. No account handles or vendor identities appear below.

---

## 1. BLUF

Re-run the B″ internal-write **delivery-existence** finding as a
**pre-registered confirmatory experiment on fresh, independent data**, keeping
the exact endpoint (keyed accuracy `real > coin` at the 0.70 floor, co-gated by
`real > role`) and every control guard, and repairing the three Gate-A
qualifications:

- **(a) FWER.** A **complete** grid-wide multiplicity plan: Bonferroni across
  **all six** elementary tests `{2 cells} × {floor, real>coin, real>role}`
  (per-test α = 0.05/6, z_floor = 2.3940), so the **paired-control tests are
  corrected across cells too** — not only the Wilson floor (the B″ defect).
- **(b) Independence.** The two confirmatory cells are read out on **disjoint
  fresh item partitions** with **distinct derangement-seed families**, and the
  fresh items are drawn from a **held-out corpus never contacted** by
  B′/B″/Stage-1. The two cells become genuinely independent confirmations, not
  the corroborating same-items/same-seed pair B″ reported.
- **(c) Confirmatory, not exploratory.** No cell search: the two cells, the
  hypotheses, and every floor/threshold are declared up front (§3), frozen by
  `prereg-freeze`, run at `phase:"final"` with `prereg_hash` on every row, and a
  fired PASS is held at **PASS-PENDING-AUDIT until a non-runner audit CONFIRMS**
  (`verdict-gen` step 8). The evidence grade of the RESULT is thereby
  confirmatory — unlike B″, whose evidence stayed MEASURED-exploratory.

**What a PASS licenses (and only this):** *the B″ internal-write keyed-DELIVERY
finding replicates on fresh independent items at R3 at the two pre-registered
cells.* It licenses **no** integration / real-generation / correctness claim
(that is Stage-1's question, read INCONCLUSIVE, and this record does not
re-open it), **no** internal-vs-external superiority claim (the original nsk1
primary was never run), and **no** breadth or scale claim. This is the
programme's one live kernel-specific-structure positive; the point of R3 is to
find out whether it survives an honest confirmation.

---

## 2. The finding being confirmed (custody + exact numbers)

[MEASURED-exploratory — B″ = "run 2 / B″" of the internal-write arc;
`poc/nsk1/out/bprime2/bprime2_summary.json` sha256
`0ee800f7f7d1aec0aa245986aa9a27a15017ebc33d5780a9cb4104da366f76f1`, rows sha256
`dadabaaea914485e387b9c1f558f5f938a7b9905159b35000957aea2a340eeba`; interpretation
`registry/assessments/nsk1-bprime2.json`; Gate-A custody
`docs/next/analysis/nsk1-bprime-gatea-verdict.md`.]

B″ measured, at R3 = SmolLM2-1.7B-Instruct (commit
`31b70e2e869a7173562077fd711b654946d38674`), on the CLUTRR entity form:

| cell (ℓh, ℓt) | keyacc_real | Bonf. Wilson LB (z=2.5427, /9) | real>coin p | real>role p |
|---|---|---|---|---|
| **(16, 16)** | **0.850** | **0.775** ≥ 0.70 | 4.11×10⁻¹³ | 9.06×10⁻¹¹ |
| **(12, 16)** | 0.810 | 0.730 ≥ 0.70 | 1.35×10⁻¹⁰ | 8.87×10⁻⁷ |
| other 7 cells | 0.42–0.61 | < 0.70 | — | — |

Coin control 0.43–0.52 at every cell (E[coin] ≤ 0.5 by the coin-XOR
construction). Role control 0.58–0.595 at the pass cells. The
delivery read-out is a **teacher-forced logprob margin** `m = lp_top − lp_bridge`,
success `[m(+) > m(−)]`; the injection is **additive norm-matched contrastive**,
`h_p ← h_p + s·α·‖h_p‖·Δ̂v` at the final prompt token, α = 1.0. Gate-A
independently recomputed every decisive number from the raw rows and upheld the
PASS under corrections **stricter** than the plan; Stage-1 later replicated the
α = 1.0 keying (0.810/0.850) on a fresh run against three derangement seeds
[MEASURED-exploratory: `registry/assessments/nsk1-stage1.json`].

**The three Gate-A qualifications carried into R3**
(`docs/next/analysis/nsk1-bprime-gatea-verdict.md` checks 6 & 8), verbatim in
substance:

1. **FWER spec defect.** The frozen B″ rule (`docs/next/nsk1-bprime2-spec.md`
   line 226 / §4) corrected only the Wilson floor across the 3×3 grid; the two
   paired-control tests stood at `p < 0.05` **per searched cell** with no
   multiplicity correction. R3 must pre-register a complete multiplicity plan
   **covering the paired-control tests**.
2. **"Independent second cell" is inaccurate.** (12,16) used the **same 200
   items, model, α, and derangement seed** as (16,16) — corroborating, not
   independent. Genuine independence needs **fresh items/seed**.
3. **"Confirmatory" wording.** B″ was "confirmatory as a fork decision" only in
   the sense that a predeclared rule was mechanically applied; the study was
   adaptive, pre-freeze, single-run **exploratory** evidence and must never be
   shortened to "confirmatory result".

R3 fixes (1) in §4, (2) in §3.2–§3.3, and (3) by being an actual pre-registered
frozen record (§7–§8).

---

## 3. Confirmatory hypotheses, cells, and floors — declared up front (fix c)

### 3.1 The endpoint (kept verbatim from B″)

[STIPULATED: ASM-2353 — endpoint carry-over.] The dependent variable is the
**source-keyed counterfactual-pair discrimination** success bit on the
teacher-forced logprob margin `m = lp(top | v) − lp(bridge | v)`, real success
`[m_real(+) > m_real(−)]`; **ties and non-finite margins count as failure**. The
**keyed-accuracy floor is 0.70** (kept from B″). The three control guards are
kept exactly:

- **coin** (null anchor): `coin bit = int(sha256("<seed>|<item>|<ℓh>|<ℓt>")…)&1`;
  `coin_success = (bit==1 ? m_drg(+)>m_drg(−) : m_drg(−)>m_drg(+))`. E[coin] ≤ 0.5
  by arithmetic for a content-free perturbation of any magnitude.
- **role** (mechanism separator / item-specificity co-gate):
  `role_success = [m_drg(+) > m_drg(−)]` with fixed key→sign on the deranged
  donor.
- **coin-validity tripwire** (instrument gate): a coin control statistically
  above 0.5 impeaches the construction, not the family (§5.1).

### 3.2 The two pre-registered cells (no search)

[STIPULATED: ASM-2354 — cells fixed a priori from B″/Stage-1, no grid.]

- **C1 = (ℓh, ℓt) = (16, 16)** — the **PRIMARY** confirmatory cell (B″'s
  strongest, keyacc 0.850). Read out on **fresh partition A only**.
- **C2 = (12, 16)** — the **independent-replication** cell (B″ 0.810). Read out
  on **fresh partition B only**, disjoint from A.

ASSERT `config.num_hidden_layers == 24` (the cells are literal layer indices).
No other cell is evaluated; there is no cell-selection step and therefore no
search multiplicity to correct beyond the two declared cells.

### 3.3 The confirmatory hypotheses and floors (BLUF-level, up front)

- **H1 (PRIMARY).** At C1 on fresh independent partition A, keyed accuracy of
  the real arm clears all three conjuncts under the complete /6 plan (§4):
  - **floor:** one-sided Wilson LB(keyacc_real, z = 2.3940) **≥ 0.70**;
  - **beats coin:** paired exact one-sided sign-test `p(real > coin) < 0.0083333`
    at **all three** derangement seeds;
  - **beats role:** paired `p(real > role) < 0.0083333` at **all three** seeds.
  `H1 true ⇒ PASS` (→ PASS-PENDING-AUDIT until a non-runner CONFIRMS).
- **H2 (co-primary INDEPENDENT REPLICATION).** The identical three conjuncts at
  **C2 on the disjoint fresh partition B** with its own derangement-seed family.
  `H1 ∧ H2 ⇒ CONFIRMED-REPLICATED`, reported with the same prominence as the
  primary PASS.
- **Refutation floor (pre-registered decisive negative).** If **both** cells'
  one-sided 95 % Wilson UB(keyacc_real) **< 0.70**, the B″ delivery finding did
  **not** replicate on fresh independent items → **FAIL (REFUTED)**.
- **Specificity failure.** If H1's floor + coin clear but `real > role` fails at
  C1, delivery is generic-direction, **not** item-specific → **FAIL**
  (`primary_role_generic`; the E9-defl / B″ CHANNEL-ROLE discipline).
- **SESOI.** The smallest effect of interest is the keyed-accuracy floor itself,
  0.70 (real vs a 0.50 coin baseline; a +0.20 absolute margin). This is the
  effect B″ measured at ~0.31–0.35 above coin — R3 asks only whether the LB
  clears 0.70 on fresh data, not whether a smaller effect exists.

---

## 4. The complete FWER / multiplicity plan (fix a)

[STIPULATED: ASM-2355 — complete Bonferroni family.]

- **Family.** The pre-registered family is the **six elementary tests**
  `{C1, C2} × {floor, real>coin, real>role}`. Every test — including **both
  paired-control tests at both cells** — is a family member. This is precisely
  the coverage B″ lacked (it corrected only the two Wilson floors).
- **Correction.** Bonferroni, per-test α = 0.05/6 = **0.0083333**. The floor
  test is the one-sided Wilson LB at `z = Φ⁻¹(1 − 0.0083333) = 2.3940`; the two
  paired tests require `p < 0.0083333`.
- **All-seeds conjunct.** Each paired conjunct must hold at **all three**
  derangement seeds of its cell's partition (the Stage-1 lesson: content-free
  behaviour can be seed-heterogeneous; the all-seeds requirement only shrinks
  the rejection region, so it needs no further correction) [MEASURED-exploratory
  backing: `registry/assessments/nsk1-stage1.json` `single_seed_counterfactual`].
- **Why this is conservative, stated honestly.** Each cell's PASS is an
  **intersection-union test** (a conjunction of three tests), so the true FWER of
  the family is **strictly below 0.05** — declaring CONFIRMED requires *all*
  conjuncts to reject simultaneously. The /6 Bonferroni is deliberately the
  strong, simple, auditable choice; the correct-but-less-conservative reading
  (a union over two cells needs only /2 on each cell's IUT conjunct) is noted
  and **dominated** by /6, so nothing rests on the distinction. All arithmetic
  is done inside the pinned analysis script; the verdict rules only read the
  resulting booleans (the `eval_expr` grammar has no arithmetic).
- **Coin-validity family.** The tripwire uses a separate two-sided correction
  over the `2 cells × 3 seeds = 6` coin series, `z = Φ⁻¹(1 − 0.05/12) ≈ 2.638`
  (§5.1).

**Design-time power** (arithmetic, not evidence; one-sided Wilson LB ≥ 0.70 at
the /6 z = 2.3940; verified by the binomial power computation logged during
design):

| n per cell | power @ true 0.78 | @ 0.81 | @ 0.85 |
|---|---|---|---|
| 175 | 0.43 | 0.80 | 0.99 |
| 200 | 0.54 | 0.88 | ~1.00 |
| **300** | **0.74** | **0.97** | **0.99+** |

The paired coin/role conjuncts are **non-binding** at these separations (B″
`real>coin` p = 4.1×10⁻¹³ and `real>role` p = 9.1×10⁻¹¹ at n = 200, ≪ 0.0083333).
The **floor test is the binding test**, and it is sized at a **conservative
planning keyacc of 0.81** (the *weaker* B″ cell's failures-only value); the
pooled fresh set is expected higher (~0.85–0.87), so n = 300/cell carries
comfortable margin.

---

## 5. Instrument-validity gates and control guards (kept)

### 5.1 Gates (all computed in-run on the fresh confirmatory surfaces)

- **headroom_ok:** text-only accuracy on the fresh set ∈ [0.05, 0.85] with ≥ 300
  scored items. (R3 measured 0.7912 on the old covered set four times;
  same-distribution fresh items are expected in-window — a near-certain pass, but
  a genuine gate.) [MEASURED-exploratory backing: repro 958/958 across
  B′/B″/Stage-1.]
- **coin-validity tripwire:** for no cell × seed does the coin keyacc one-sided
  Wilson LB at `z ≈ 2.638` exceed 0.5. E[coin] ≤ 0.5 by arithmetic; an
  above-chance coin means broken plumbing (seed leakage), so this is
  INSTRUMENT-INVALID, not signal.
- **finiteness:** zero non-finite margins (ABORT on NaN; counted otherwise).
- **n floor:** n ≥ 175 at each cell (below this the floor test is underpowered;
  fail closed to INSTRUMENT-INVALID rather than issue an underpowered verdict).

`instrument_valid = headroom_ok ∧ coin_validity_ok ∧ (nonfinite == 0) ∧ (n_C1 ≥
175) ∧ (n_C2 ≥ 175)`.

### 5.2 The decision rule (pre-declared; the kill-criterion verbatim in the record)

Evaluated in order, first match wins (mirrors `registry/experiments/nsk1-r3.json`
`verdict_rules`):

1. **INSTRUMENT-INVALID** iff `¬instrument_valid`.
2. **PASS (CONFIRMED)** iff H1 holds (`primary_confirmed`). → PASS-PENDING-AUDIT
   until a non-runner CONFIRMED audit exists.
3. **FAIL** iff `refuted` (both cells UB < 0.70) **or** `primary_role_generic`
   (H1 floor+coin clear, real>role fails).
4. **INCONCLUSIVE** otherwise (report all bounds; no adjective).

`confirmed_replicated` (H1 ∧ H2) is reported as a secondary endpoint with the
same prominence; it does not change the verdict label but is the strong
independent-replication reading.

---

## 6. Arms, seeds, n, procedure

### 6.1 Host, operator, arms

[STIPULATED: ASM-2356 — host/operator carry-over.] Host R3 =
`HuggingFaceTB/SmolLM2-1.7B-Instruct` at commit
`31b70e2e869a7173562077fd711b654946d38674` (ABORT on mismatch); Modal 1×A10G (or
L4), fp32, chat template. Operator = additive norm-matched contrastive injection
`h_p ← h_p + s·α·‖h_p‖·Δ̂v` at the final prompt-token residual at ℓt, prefill
only (seq==1 guard), **α = 1.0** fixed — the only measured keying strength;
Stage-1 showed keying decays into the control band below α = 1.0
[MEASURED-exploratory: `registry/assessments/nsk1-stage1.json` `keying_frontier`].
**Law 1 holds:** no raw kernel/encoder coordinates enter the model — only
harvested activations of the item's own two donor sentences
`D_top`/`D_bridge` (built by `_build_specs_bprime2` verbatim; the two donors
differ only in the answer-slot name), from which `Δv = v_top − v_bridge`,
`Δ̂v = Δv/‖Δv‖`.

Per item × cell: **REAL** arm (item's own Δ̂v, both signs) and **DERANGED** arm
(Δ̂v of σ_seed(i), both signs, for each of three seeds). The **coin** and
**role** control series are **derived from the shared deranged forwards** — no
extra GPU calls. **Baselines:** one unhooked candidate-pair margin per item
(reported). **Text-only:** one greedy generation per item (headroom gate +
failure/correct substratum labels).

### 6.2 Fresh corpus, disjoint partitions, seeds (fix b)

[STIPULATED: ASM-2357 — fresh held-out corpus + disjoint partitions +
independent seeds.]

- **Fresh corpus `data/nsk1-clutrr-r3`:** a covered slice **never contacted** by
  B′/B″/Stage-1, built pre-freeze by the pinned CLUTRR generator
  (`generator_commit d045fae289d3746503677ceed7631c999202501e`) at **new seed
  20260720** under the **same S4 covered predicate** as `data/nsk1-clutrr`
  (clean k = 2 up-edge-only chains over {mother, father}, released gold in
  {grandmother, grandfather}; all facts in-context). This is required because
  the pinned-config covered pool is **exhausted** —
  `data/nsk1-clutrr/manifest.json` `counts.remainder_unused = 0`,
  `covered_pool_deduped = 958`, all consumed by the discovery contacts (§8
  BLOCKER-1) [MEASURED: manifest, provenance-only]. The generator path yields
  distributionally identical fresh items in unlimited quantity; the alternative
  (drawing additional pinned release configs beyond the six in
  `manifest.json.source.config_order`) is the fallback if regeneration is
  disallowed.
- **Disjoint partitions:** the fresh covered corpus is split by **seed 20260726**
  into two disjoint partitions **A** and **B**. C1 = (16,16) is read out on **A
  only**; C2 = (12,16) on **B only**. The cell↔partition pairing is intentional:
  each cell confirms its own B″ finding on its own fresh data, so the two
  confirmations are statistically independent (disjoint items). No cross
  comparison between cells is made or claimed, so the confound is harmless.
- **Derangement seeds:** partition A uses three independent Sattolo derangements
  with seeds **{20260720, 20260721, 20260722}**; partition B uses
  **{20260723, 20260724, 20260725}** — distinct from each other and from
  B″/Stage-1 (20260712/13/14). ASSERT each fixed-point-free.
- **Endpoint measured on the FULL fresh covered partition** (both text-only
  correct and failure items), a **DISCLOSED** change from B″'s failures-only
  Swept [STIPULATED: ASM-2358]. Rationale: the delivery read-out is a property of
  the item's counterfactual pair, not of host failure — B″'s disc-c100 showed
  the keying replicates on *correct* items at 0.90/0.88, even higher than on
  failures — and the failure population alone (~21 % of a 300-item set ≈ 63
  items) is too small for the confirmatory floor test. The failure-substratum
  and correct-substratum keyacc are reported (never gated), preserving exact
  comparability with B″.

### 6.3 n and the count gate

[STIPULATED: ASM-2359 — n target + count-gate branches.] Target **n = 300 per
cell** (600 fresh covered items total, split disjoint). Pre-freeze count gate:

- `n_final ≥ 300/cell` → **full-power branch** (power ≥ 0.97 at planning keyacc
  0.81 under the /6 floor; ≥ 0.99 at 0.85).
- `175 ≤ n_final < 300` → power **redone at achieved n** and written into the
  record **before** freeze; freeze only if power ≥ 0.80 at planning 0.81.
- `n_final < 175/cell` → **do not freeze**; escalate to the maintainer (generate
  more fresh items or reconsider). The count is a to-measure build fact,
  deliberately not estimated at design time.

### 6.4 Procedure (runner-role, against the FROZEN record)

1. **Build** `data/nsk1-clutrr-r3` (generator + seed 20260720 + S4 filter),
   dedup, split A/B by seed 20260726, run S9-style build asserts
   (engine resolves every item's hop-1; gold-not-in-`D_bridge`; 3-name distinct;
   `D_top`/`D_bridge` differ only in the name slot), pin corpus digest, count
   gate. **(Pre-freeze; own sign-off — §8.)**
2. **Text-only pass** on all fresh items (headroom gate + substratum labels).
3. **Donor harvest** for every item (Δ̂v per (item, ℓh ∈ {12,16})).
4. **Margin sweep** per cell on its partition: REAL ± (4 forwards) + DERANGED ±
   per seed (12 forwards) = 16 teacher-forced forwards/item; write index
   `w = maxlen − len(cand) − 1`, ASSERT `input_ids[w] == prompt_ids[−1]`; ABORT
   on non-finite.
5. **Baselines** (unhooked margins). Emit rows; every margin/baseline row stores
   both raw candidate logprobs so the entire gate recomputes offline without GPU.
6. `analysis/nsk1_r3.py` over the rows (via `verdict-gen`); non-runner audit.

---

## 7. The pinned, verdict-gen-compatible stdin analysis

**Path:** `analysis/nsk1_r3.py` (draft sha256
`eb3042b361759379c8cf16c959b5f10b7bcb8103c73f4bb1ae5c8cd5a7ae1402`; **recompute
and re-pin at freeze** after any review edit).

**I/O contract** (verified against `tools/registry/verdict-gen.py` step 5): the
pinned script **reads eligible run rows as JSONL on STDIN** and **writes one
analysis JSON object to STDOUT** — no argv, no files. (Note: the legacy
`analysis/nsk1.py` uses `--rows/--out` argparse and is **not** verdict-gen
compatible; the R3 script is written to the stdin/stdout contract every frozen
record obeys, e.g. `analysis/f2.py`, `analysis/a5.py`.) Stdlib only; all
statistics (Wilson bounds, exact one-sided sign tests, the /6 correction, the
booleans) are computed there — the verdict rules only compare emitted booleans
to constants.

**Row schema (runner emits; analysis consumes):** `item_id`, `probe ∈
{text-only, baseline, margin}`, `cell` = `[ℓh, ℓt]` (or null), `arm ∈ {real,
drg, null}`, `sign ∈ {1, −1, null}`, `seed` (derangement seed on drg rows; null
else), `coin` (drg rows: that seed's bit), `lp_top`, `lp_bridge` (margin/baseline
rows), `correct`/`gold` (text-only rows), plus `phase:"final"`, `gate:"NSK1-R3"`,
`host:"R3"`, `prereg_hash`, `config:{cell, seed}`.

**Emitted fields the verdict rules read:** `/gates/instrument_valid`,
`/gates/headroom_ok`, `/gates/coin_validity_ok`, `/analysis/primary_confirmed`,
`/analysis/confirmed_replicated`, `/analysis/refuted`,
`/analysis/primary_role_generic`, plus the reported per-cell keyacc / Wilson
bounds / paired-p fields (full list in the record `pins.analysis_script.output_fields`).

**Verdict rules (in the record; `eval_expr` grammar):**

```
[INSTRUMENT-INVALID]  not /gates/instrument_valid
[PASS]                /analysis/primary_confirmed == true
[FAIL]                /analysis/refuted == true  OR  /analysis/primary_role_generic == true
[INCONCLUSIVE]        (catch-all)
```

A fired PASS → **PASS-PENDING-AUDIT** until `registry/audits/nsk1-r3/` holds a
CONFIRMED audit by a non-runner identity (`verdict-gen` step 8). The pinned
analysis was smoke-tested end-to-end on synthetic rows during design: a
0.86/0.82 world yields `primary_confirmed = confirmed_replicated = true` with C1
floor-LB 0.816, C2 0.776; a 0.50/0.50 world yields `refuted = true`,
`primary_confirmed = false`, instrument still valid — confirming both branches
fire correctly.

---

## 8. GPU/Modal estimate, freeze-readiness, and blockers

### 8.1 Cost estimate

[STIPULATED planning, from B″'s MEASURED throughput 0.206 GPU-h for ~22k forwards;
never a measurement.] R3's call mix at n = 300/cell: margins ≈ 2 cells × 300 ×
16 = **9,600 forwards**, donor harvest ≈ 1,200, baselines ≈ 1,200, text-only ≈
600 gens ≈ **~12.6k GPU calls** — roughly **half** of B″. Estimate **0.15–0.5
GPU-h ≈ USD 0.20–1.50**; padded confirmatory ceiling **≤ USD 3** including the
headroom pass. Hard caps in the record: **USD 25 / 10 GPU-h / 12 h wall**
(unchanged from B″/Stage-1). The fresh-corpus build is **CPU-only** (generator +
filter), ~USD 0.

### 8.2 Freeze-readiness

**Design-complete and launch-ready in structure:** the endpoint, hypotheses,
floors, complete FWER plan, independence design, controls, arms/cells/seeds,
count gate, verdict-gen-compatible analysis (smoke-tested), verdict rules, kill
criterion, and extrapolation envelope are all specified and self-consistent. The
draft record `registry/experiments/nsk1-r3.json` validates against `kot-reg/1`
except for the intentional `PINNED-AT-FREEZE` placeholders (corpus digest,
harness sha, prereg-doc sha) that only a build + freeze can fill.

### 8.3 Blockers the coordinator must clear before freeze/run

- **BLOCKER-1 (data, hard).** The covered pool is **exhausted**
  (`remainder_unused = 0`). A **fresh held-out covered corpus** must be built —
  by regenerating with the pinned CLUTRR generator at seed 20260720 under the S4
  predicate (primary), or by drawing additional pinned release configs
  (fallback). This is **runner-role** work with a **committed builder pinned at
  build** and its **own maintainer sign-off** (a new corpus contact + the NC
  licence-quarantine notice). Until it exists, n and the corpus digest are
  unknown and the count gate cannot run.
- **BLOCKER-2 (count gate).** n and the finalized power must be written into the
  record **before** freeze per §6.3; if `n_final < 175/cell`, do not freeze.
- **BLOCKER-3 (pins).** Fill `pins.corpus_hashes.nsk1-clutrr-r3`,
  `pins.harness_manifest` (real-mode Modal entrypoint + builder shas), and
  recompute `pins.analysis_script.sha256` and `prereg_doc.sha256` after review.
- **BLOCKER-4 (hypotheses).** Register `HNSKR3D` (delivery) and `HNSKR3S`
  (specificity) in the hypothesis registry, or re-map to existing ids.
- **BLOCKER-5 (governance).** Register ASM-2353..2359 at commit; obtain maintainer
  Tier-2 GPU sign-off; run the pre-freeze gates (build+count, harness/analysis
  pins, green mock of the pinned analysis on the built corpus) then
  `prereg-freeze.py`.
- **NON-BLOCKER (audit).** A **non-runner CONFIRMED audit** is required only to
  finalize a fired PASS (PASS-PENDING-AUDIT otherwise) — it does not block the
  freeze or the run.

### 8.4 What the coordinator does, in order

1. Review this design + the draft record + `analysis/nsk1_r3.py`.
2. Sign off the fresh-corpus build; the runner builds `data/nsk1-clutrr-r3`
   (generator/seed/filter pinned), runs build asserts + count gate, pins the
   corpus digest, and reports n.
3. Fill the record pins (corpus, harness, analysis sha, prereg-doc sha), finalize
   n/power, register ASMs + hypotheses.
4. Green-mock the pinned analysis on the built corpus's row schema; run the RT-14
   registry lint.
5. `prereg-freeze.py nsk1-r3`; obtain Tier-2 GPU sign-off.
6. Runner executes on Modal (`phase:"final"`, foreground gates).
7. Non-runner runs `verdict-gen`; if PASS, a non-runner auditor files the
   CONFIRMED audit.

---

## 9. Extrapolation envelope (what a verdict licenses)

**A PASS licenses exactly:** *the B″ internal-write keyed-DELIVERY finding
replicates on fresh independent items at R3 at the two pre-registered cells* — a
norm-matched additive contrastive residual write of a counterfactual name-pair
difference vector, injected at the final prompt token, delivers item-specific
content the host reads out at keyed accuracy beating an arithmetic-chance coin
control and a role-consistent control above the 0.70 floor, under a complete
grid-wide FWER correction, with the two cells confirmed on disjoint fresh data.

**It does NOT license:** any **integration / real-generation / correctness**
claim (the read-out is a teacher-forced margin; Stage-1 read integration
INCONCLUSIVE and this record does not re-open it); any **internal-vs-external
superiority** claim (the original nsk1 primary was never run); any **breadth or
scale** claim (other hosts, R3+ scale, other forms, α < 1.0, other operators or
positions, other cells, multi-hop beyond 2, natural-corpus / NL-parse); any
**CLUTRR leaderboard / SOTA** claim; any **efficiency-thesis** claim; any "the
kernel powers the network" headline.

**A FAIL/REFUTED means** the programme's one live kernel-specific-structure
positive did **not** survive an honest independent confirmation, and the
internal-write line redirects to engine-external seams (per the feasibility
synthesis) under their own gates. Either verdict is confirmatory-grade for the
delivery-existence claim **and nothing wider**; every widening is EXTRAPOLATION
(load_bearing: false).

---

## 10. New assumptions (STIPULATED; coordinator registers at commit)

- **ASM-2353** — endpoint carry-over (keyed `real>coin` margin, floor 0.70, coin
  + role guards) from B″ verbatim.
- **ASM-2354** — the two confirmatory cells (16,16)/(12,16) are fixed a priori
  from B″/Stage-1; no grid search.
- **ASM-2355** — the complete /6 Bonferroni family over
  {2 cells}×{floor,coin,role}, all-seeds paired conjuncts (fixes Gate-A qual. a).
- **ASM-2356** — host/operator/α = 1.0 carry-over from B″/Stage-1.
- **ASM-2357** — fresh held-out corpus + disjoint partitions + independent
  derangement seeds (fixes Gate-A qual. b); the exhausted-pool build blocker.
- **ASM-2358** — endpoint measured on the FULL fresh covered partition (disclosed
  change from B″ failures-only Swept), substrata reported.
- **ASM-2359** — n = 300/cell target + count-gate branches + non-freeze floor.

---

*Self-check: this is a CONFIRMATORY (pre-registered, frozen-record) design, not
an exploratory diagnostic; the three Gate-A qualifications are each repaired
(a: complete /6 FWER over all six tests incl. paired controls; b: fresh
never-contacted corpus, disjoint per-cell partitions, distinct derangement
seeds; c: frozen record + phase:final + prereg_hash + mandatory non-runner audit,
so the RESULT is confirmatory-grade); the endpoint (keyed real>coin, 0.70 floor)
and all control guards are kept; arms/cells/seeds/n and the pinned
verdict-gen-compatible stdin analysis are specified; the GPU/Modal estimate and
the freeze blockers are reported; every design choice is STIPULATED (ASM-2353..
2359, registered by the coordinator at commit), every cited B″/Stage-1 number is
MEASURED-exploratory with a sha ref, no measurement is asserted by this document,
no register entry is written, no git action is taken, no GPU is spent, no frozen
record is edited, and no account handles or vendor identities appear.*
