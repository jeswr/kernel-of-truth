# F1-K freeze-readiness checklist (coordinator custody path)

> **Status:** freeze PACKAGE emitted (designer-5, 2026-07-13); record is
> `registry/experiments/f1k.json` (DRAFT, kot-reg/1). Everything below is
> the COORDINATOR's, in order, before/at `tools/registry/prereg-freeze.py`.
> This pass took no git action, wrote no `registry/assumptions.jsonl` entry,
> and ran no freeze. Companion ASMs: ASM-2270..2278
> (`docs/next/design/asm-f1k-freeze-2270-2278.json`). No feasibility
> conclusion anywhere in this package.

## A. Before prereg-freeze (blocking)

1. **Budget (the one open number).** `budget.usd_cap` currently carries the
   REGISTERED §R6/ASM-2048 worst-case ceiling **$550**.
   `docs/next/design/glm52-f1k-cost-reduction.md` (the codex reduced-cost
   design the GO in #28 anticipates) is **not yet in-repo**. Either land it
   and replace `usd_cap` with its validated ceiling, or freeze at $550 as a
   cap-not-target with the reduction (spot + expert-pinning/warm-cache +
   R 5→3) recorded as ops discipline. Constraint either way (§R6): the
   reduction may never cut n below 1,440 or drop a ladder arm
   (b0/d0/d1-drng/d2/K). [ASM-2277]
2. **Central ASM registration.** Register with the landing commit, after the
   standing review gate: the design blocks still pending centralisation
   (ASM-2024..2033, 2034..2042, 2043..2048, 2049/2113/2114, 2122..2124,
   2130), the patch block ASM-2180..2190, and this package's ASM-2270..2278.
   Central tail at emission: ASM-2202.
3. **Law-1 scoped amendment as an explicit registry event** (GATE 0,
   ASM-2025): "kernel-derived content vectors may enter model activations
   ONLY within the KaE track, only via the registered splice, deflator
   ladder mandatory." The #28 GO signals intent; the amendment must still be
   an explicit event, never an inference.
4. **Verify the analysis pin.** Recompute
   `sha256(analysis/f1k.py) == c5edd0bd1dea70f4a7e0be85e4e107cce27ff49af1b42324a2bef58ff4e6b12c`
   and re-run `python3 analysis/f1k.py --selftest` (must print
   `MOCK-SELFTEST PASS`, exit 0). Any byte change = new sha = re-freeze.
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
7. **Run `prereg-freeze.py`** (coordinator only). Expected to pass its
   lints (locally replicated green at emission: schema, single primary,
   pointer closure, catch-all, five-V, kernel-v0 corpus pin reproduces,
   placeholders accepted). Then commit + push per session protocol.

## B. Ops amendments the freeze pre-declares (P-9 placeholders — complete
## in this order, per the §R-REV4.2 corrected sequence)

8. **Freeze-manifest (A)** — committed **before ANY F1-K spend** (carrier
   construction included): all rules + the complete carrier GENERATOR
   (§R-REV3.3), template bytes+sha, single-token label verification,
   tie-break, trigger-map hash, guard/dev/test id-list hashes, ALL seeds
   (construction; pilot-panel derangement **11**; d0 table **7**; main
   derangements **101, 102, 103** — must equal the record's `design.seeds`
   and `analysis/f1k.py DRNG_SEEDS`, the dose gate fails closed otherwise),
   the deterministic derivation rules for addenda 5/6/7, and the §R-REV5
   Monte-Carlo procedure + seed.
   → completes corpus pin **`f1k-trigger-map-v1`** (kot-corpus-hash/1 over
   `data/f1k-trigger-map-v1/`).
9. **Concept→carrier map inputs** (the record's carrier chain): construction
   spend → **B0 addendum** = realized carrier tables for every arm + raw and
   rescaled norms, each a pure function of an (A) generator rule.
   → completes **`f1k-carriers-v1`**.
10. **Eval item lists**: mechanical filter output frozen as test/dev-96/
    guard-60 id lists + frozen scored templates + per-item span sidecars.
    → completes **`f1k-eval-v1`** (before any test prefill, with (6)).
11. **Bring-up (addendum 7, PRE-test gate)**: measured s/prefill +
    affordability projection vs the frozen cap (degradation order applies
    deterministically), colibri knob-semantics re-verification (ASM-1971),
    and **`glm52-weights`** content hash pinned on the relaunched instance.
12. **Power freeze (addendum 6, PRE-test)**: dev δ̂ → n_required; the hard
    power gate = **≥65 clusters EACH with ≥8 items within n ≤ 1,440**
    (each-cluster reading, ASM-2271); sign-flip-vs-bootstrap choice from the
    dev sign-symmetry check (§R-REV4.1a); REPLACE run/defer at ρ_U = 0.10
    (RUN only if dev δ_R ≤ ~0.038, §R-REV4.3); execute the frozen §R-REV5
    exact-power Monte-Carlo (pass ≥ 0.80 at μ* = +4.09 pts; realized power
    into the sidecar → `/analysis/power_scope`).

## C. Run-time contract the freeze binds (for the runner, FYI)

- Verdict path: eligible results-log records → `analysis/f1k.py` on STDIN;
  each record's `artifacts` pins `rows_path/rows_sha256` +
  `sidecar_path/sidecar_sha256` (all records must pin the same tuple);
  rows/sidecar shapes documented in the script docstring.
- Off-concept guard: 60 items byte-identical to b0 in every spliced arm —
  one mismatch voids (gate, not kill). d0 placebo fires at p < 0.05 alone
  (no +3 floor, ASM-2273) — void.
- KAE knob unset everywhere except registered F1-K arms; DRAFT=0; scoring
  via `KAE_SCORE` (one prefill/item/arm, label-logit argmax).

## Gaps at emission (honest list)

- `glm52-f1k-cost-reduction.md` absent → `usd_cap` unresolved between $550
  (registered) and the reduced ceiling (item 1).
- ASM blocks 2010..2130 (design), 2180..2190 (patch), 2270..2278 (this
  package) all pending central registration (item 2).
- Law-1 amendment not yet a registry event (item 3).
- Three corpus placeholders + `glm52-weights` pin await their ordered ops
  amendments (items 8–11) — by design, not by omission.
