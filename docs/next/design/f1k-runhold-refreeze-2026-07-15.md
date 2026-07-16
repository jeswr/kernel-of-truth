# F1-K RUN-HOLD fix + reset-refreeze memo (2026-07-15)

> **Status at emission (fable/writer-2, 2026-07-15):** the GPT-5.6 F1-K/K-3
> pre-run review-gate returned **RUN-HOLD** on the frozen record
> (`4541966640b3…`, C=96/n=1573). All three defects are FIXED, verified, and
> the record is **RESET-REFROZEN** (lawful pre-final window: not
> GNG-0-signed, no results-log). New
> `frozen_sha256 = 77e7a6a865030197e231bbfff90960ef46060957f0ac9dbcc3f89f021d8a8278`.
> Everything LEFT UNCOMMITTED; the coordinator re-reviews the critical
> geometry fix and commits. $0 spend, no GPU, no model call this pass.

## Defect 1 — CRITICAL geometry gate (fixed, regression-proven)

- **Was:** `analysis/f1k.py` computed `power_gate_valid = (c_ge8 >= 96 AND
  n == 1573)`. A planted **97-cluster** universe at n=1573 passed EVERY gate
  and reached `pass_gate=true` [MEASURED:
  `tools/registry/_f1k_geometry_regress_20260715.py` vs the superseded
  script — `power_gate_valid=True all_gates=True pass_gate=True`].
- **Now:** any realized cluster count ≠ **C_REGISTERED = 96** is
  hard-rejected fail-closed (`ERR_P2_ANALYSIS`) in the hardened-validation
  block *before any statistic runs*; the gate itself is equality-form
  (`n_clusters == 96 AND clusters_with_m>=8 == 96 AND n == 1573`).
  Off-geometry data can NEVER receive a valid verdict of any kind.
- **Selftest:** extended to **8/8** fail-closed rejections, including the
  97-cluster (the exploit shape) and 95-cluster probes at n=1573; green
  [MEASURED]. New pinned sha `3478a6c020b4…`; `output_fields` unchanged
  (50/50), so every frozen metric pointer resolves as before.

## Defect 2 — intersection power (sim run; prose figure withdrawn)

- The "~0.70–0.75" all-three-rungs figure is **WITHDRAWN** (unsupported).
- **Joint-dependence sim** [MEASURED, ASM-2376; seed 20260713, N_sim=10⁴,
  B=10⁴]: `poc/f1k-askability/power_intersection_n1573.py` — shared-K
  equicorrelated Gaussian-copula family over cluster means, registered
  marginal law preserved exactly; **λ=0 marginals reproduce the committed
  0.8043/0.8058/0.8001 EXACTLY** (byte-identical PRNG replay).
  P(all three fire at μ*): λ-grid {0,.25,.5,.75,1} →
  {0.5220, 0.5675, **0.6165**, 0.6763, 0.7984}; assumption-free Fréchet
  bounds from the marginals **[0.4102, 0.8001]** [MEASURED arithmetic].
  The honest central figure (~0.62 at λ=0.5) is LOWER than the withdrawn
  prose figure — the reviewer's hold was substantively correct.
- **Executable, not prose:** `/analysis/power_scope/intersection_all_three`
  now COMPUTES the Fréchet bounds from the sidecar-carried per-rung powers
  and carries the sim block; selftest asserts the shape. Per-rung ≥ 0.80
  criterion (ASM-2371) unchanged; consequence stays elevated INCONCLUSIVE
  (2-of-3) risk, never a false null.

## Defect 3 — input pins + Law-1 (resolved)

- **Pins** [MEASURED, ASM-2377]: 96-concept REVISION-6 rebuilds via
  `poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` (reuses the
  frozen screen machinery; 14/14 fidelity checks; byte-deterministic):
  - `f1k-trigger-map-v1` → `296e50dbf018…` (REAL pin; 153-concept joined
    v0+v1 universe, 1155 phrases);
  - `f1k-eval-v1` → `aba3f111efc9…` (REAL pin; test/dev/guard =
    1573/96/60; per-cluster test counts equal the pinned
    `m_list_by_rank` element-by-element; redacted-input hash `4f7cf1c6…`
    re-verified; token-level fields still BLOCKED to the bring-up
    tokenizer, as registered);
  - `f1k-carriers-v1` stays PINNED-AT-INPUTS **by the frozen ordering**
    (realized tables ARE construction spend, B0 addendum); the (A)-time
    96-slot generator components are committed NOW at digest
    `cac24e18c895…` (concept texts byte-identical to the pinned
    `f1k-contrast-v1`; derangements 11/101/102/103 fixed-point-free).
- **Law-1** [STIPULATED, ASM-2378]: the scoped amendment is now an explicit
  registry event — `registry/governance/law-1/1-kae-scoped-amendment.json`
  ("kernel-derived content vectors may enter model activations ONLY within
  the KaE track, only via the registered splice, deflator ladder
  mandatory"; authorized by the maintainer GATE-0 GO per #28; **binding on
  the coordinator's landing commit** — no run before that commit exists).

## Reset-refreeze

- Lawful pre-final window verified: f1k absent from
  `registry/gng0-signoff.json`; `results-log/f1k.jsonl` does not exist.
- `prereg-freeze --dry-run` → **DRY-RUN-OK**; freeze → **FROZEN**
  2026-07-15T23:42:21Z by writer-2, `frozen_sha256 = 77e7a6a8…8278`
  (index updated; supersedes `45419666…8079`). Same non-fatal PAUSE flags
  + ASM-2373 (now centrally registered). Correction record:
  `registry/corrections/f1k/1-prefreeze-correction.json`.
- **Unchanged, verified post-freeze:** power table K-1 0.8043 / K-2 0.8058 /
  K-3 0.8001 at C=96/n=1573/μ*=+4.09/R=(1,3,1) (all ≥ 0.80);
  `kill_criterion_verbatim` and `extrapolation_envelope_verbatim`
  BYTE-IDENTICAL (PROXY-PROVISIONAL validity scope intact verbatim);
  budget $155; seeds; verdict rules.
- RT-15 post line (coordinator, hash-only):
  `prereg freeze f1k frozen_sha256=77e7a6a865030197e231bbfff90960ef46060957f0ac9dbcc3f89f021d8a8278`.

## ADDENDUM — 2026-07-16 GPT-5.6 pre-run HOLD pass (supersedes the frozen sha above)

> The pre-run review-gate re-ran on the refrozen record and returned **HOLD**
> with 4 blockers (it CONFIRMED the geometry/intersection/refreeze fixes
> above — those are untouched). All fixed this pass, same lawful pre-final
> window (still no GNG-0 signature, still no `results-log/f1k.jsonl`):
>
> 1. **Blocker 1 (CRITICAL, fixed)** — `analysis/f1k.py` sidecar validity
>    gates used Python truthiness: the JSON STRING `"false"` was a passing
>    attestation (`guard.byte_identical="false"` → official PASS,
>    reproduced [MEASURED]), and `guard.n_items` was ignored (0 items +
>    byte_identical=true → PASS). Now: every validity flag strict
>    JSON-boolean (`x is True`; strings/ints/null fail the gate CLOSED to
>    INSTRUMENT-INVALID), `off_concept_guard_valid` requires
>    `n_items == 60`, string `replace.ran` is a shape defect. Selftest
>    9/9 hardened rejections + 14/14 strict-bool/guard probes, green
>    [MEASURED]. New pinned sha `e80c4190cd59…`; `output_fields` unchanged
>    (50/50).
> 2. **Blocker 2 (fixed)** — the campaign driver
>    `poc/glm52-probe/f1k-harness/f1k_driver.py` was still on the
>    superseded geometry. REVISION-3 ([R6-n] anchors): N_TEST=1573 EXACT,
>    EQUALITY-form 96/96/1573 power gate (matches the analysis), USD_CAP
>    $155 (ASM-2374), per-rung `joint_power` dict + required ASM-2376
>    intersection block, ΔR_max re-derived ~0.0397 at n_max=1573, mock
>    fixtures at the frozen geometry (37×17 + 59×16 = 1573). Worst-case $
>    recomputed [MEASURED arithmetic]: mandatory campaign **$145.94 ≤
>    $155**; +REPLACE $156.13 > cap at the pessimistic corner ⇒ REPLACE
>    runs only if the measured (7) projection keeps the ledger ≤ cap
>    (pre-registered ASM-2374 resolution — cap never silently raised).
>    `--mock` end-to-end green incl. ingest by the FIXED analysis
>    [MEASURED].
> 3. **Blocker 3 (fixed)** — the correction record's `changes[0]` carried a
>    MISTRANSCRIBED analysis sha (`…a5f3…48814`, matching no file); it now
>    carries the true chain `9d01468e… → 3478a6c020b421cc… → e80c4190…`.
>    Because blocker 1 edits the pinned analysis, the record was
>    **reset-refrozen again**: `frozen_sha256 = 77e7a6a8…8278 →`
>    **`45e316e9925263e323090429e9d5f830dd5df71e1b5e68c19ffd57442b084235`**
>    (2026-07-16T00:21:51Z, writer-2; DRY-RUN-OK first; index + correction
>    record + this memo updated; kill criterion / envelope / budget /
>    geometry / power table byte-identical). Build artifact:
>    `tools/registry/_f1k_holdfix_20260716.py`.
> 4. **Blocker 4** is the coordinator's landing commit — everything left
>    uncommitted and internally consistent for it. RT-15 post line becomes:
>    `prereg freeze f1k frozen_sha256=45e316e9925263e323090429e9d5f830dd5df71e1b5e68c19ffd57442b084235`.

## Coordinator checklist (this pass hands off)

1. Re-review the CRITICAL geometry fix (`analysis/f1k.py` diff + regression
   script) — the review-gate asked for exactly this re-review.
2. Land the commit: the Law-1 event (ASM-2378) and the refreeze become
   binding on the landing commit; post the RT-15 hash line.
3. ASM-2376/2377/2378 appended to `registry/assumptions.jsonl` this pass
   (uncommitted) — carried with the landing commit.
4. Residual, unchanged: ASM-2373 human-fidelity proxy bar (open
   EXTRAPOLATION, PAUSE-flagged, conclusions hard-gated); reserve
   substitution rule still due at the (A) ops amendment (skeptic residual 6
   of the geometry memo); B0/bring-up completions (realized carriers,
   tokenizer-derived fields, weights hash) unchanged.

## HOLD ROUND-3 addendum (2026-07-16, fable/writer-2) — default-deny + the real seam

> **Status:** the round-2 re-review returned **HOLD**: the strict-bool fix
> was CONFIRMED real but **INCOMPLETE**, plus a **structural ingestion
> break**. CONFIRMED-GOOD and untouched: the exact-C geometry gate, the
> ASM-2376 intersection sim, and the reset-refreeze/provenance chain. All
> residual defects are FIXED under one class-closing principle and the
> record is **reset-refrozen a third time** (same lawful window, re-verified:
> not GNG-0-signed, `results-log/f1k.jsonl` absent). New
> `frozen_sha256 = cf19b52a5361d0f3939385ac4c516d4341bd9408bae20e63085df340ae5e624b`.
> Everything LEFT UNCOMMITTED for the round-3 re-review. $0, no GPU.

1. **Analysis default-DENY** (`analysis/f1k.py`, new pinned sha
   `5b5801664bb3…`; `output_fields` unchanged 50/50): `validate_sidecar()`
   runs before any gate/statistic — closed top-level whitelist of the 9
   mandatory blocks, every block a JSON object, every mandatory field
   present; `replace.ran` must be a strict bool (a "valid defer" now
   REQUIRES the block present with `ran === false` — `.get("ran", False)`
   fail-opened absence into a PASS); power pinned EXACTLY to the ASM-2371
   marginals + non-empty ASM-2376 block; cost numeric within the $155
   ASM-2374 ceiling; carriers at C=96. Structural defects ⇒
   `ERR_P2_ANALYSIS` (no verdict producible); value defects keep failing
   gates CLOSED (INSTRUMENT-INVALID). Selftest [MEASURED, green]: 83-probe
   structural sweep (every block × missing/null/int/string; every field
   missing) + 47 value-level gate probes + the retained strict-bool set;
   the all-present/all-true fixture still PASSES.
2. **Driver laundering CLOSED** (`f1k_driver.py` [R3-ATTEST]): `bool()`
   removed from the whole attestation surface — emission via `attest_bool`
   (non-bool ⇒ run FAILS, `true` never fabricated), reads via `is True`.
   [R3-POWER]: sidecar power block pinned EXACTLY (arbitrary 0.9-marginals
   and empty `mc_intersection` REJECTED). [R3-COST]: realized-ledger $155
   stop at init/resume + EVERY accumulation + sidecar emission (spend
   recorded, run STOPPED, no success record). All probed in `--mock`
   [MEASURED, green].
3. **Official seam made real** ([R3-SEAM]): driver now emits a
   kot-log/1-conformant run-record BODY with the **D10-PAIRED** artifacts
   ARRAY (`role:"rows"` + `role:"sidecar"`, repo-relative, prereg_hash from
   the frozen index); `kot-log-1.json` role enum extended to
   `["rows","sidecar"]` (non-run scope guard unchanged); `verdict-gen`
   step 5a verifies BOTH pins fail-closed at consumption
   (`ERR_P2_SIDECAR_MISSING/DRIFT/MALFORMED/AMBIGUOUS/ORPHAN`) and feeds
   the RECORD LINE, disclosed as `inputs.paired_artifacts_verified`;
   rows-only/unmarked records byte-identical (all 123 pre-existing
   registry-tool tests green [MEASURED]). **Tested through the REAL path**
   (sandboxed repo root): PASS-eligible mock → log-append → verdict-gen →
   pinned analysis → **PASS-PENDING-AUDIT**; attacker-consistent tampered
   sidecar (guard.n_items=0, sha re-pinned, all hashes green) →
   **INSTRUMENT-INVALID** [MEASURED].
4. Kill criterion, envelope, budget, geometry, power table byte-identical
   (asserted by `tools/registry/_f1k_round3fix_20260716.py`);
   `registry-check` PASS. RT-15 post line becomes:
   `prereg freeze f1k frozen_sha256=cf19b52a5361d0f3939385ac4c516d4341bd9408bae20e63085df340ae5e624b`.

## HOLD ROUND-4 addendum (2026-07-16, fable/writer-2) — the complete kot-f1k-record/1 schema

> **Status:** the round-3 re-review returned **HOLD** a fourth time — each
> round validated one level and the next review found the NEXT level
> unvalidated (round 1 geometry; round 2 top-level truthiness + guard;
> round 3 top-level default-deny; round 3b NESTED sidecar interiors + ROW
> schema + missing paired-sidecar tests). CONFIRMED-GOOD and untouched:
> driver attest_bool + exact power pin + realized-cost stop; the
> reset-refreeze discipline; the provenance chain. Round 4 STOPS patching
> levels and closes the DEPTH CLASS. Reset-refrozen a fourth time (same
> lawful window, re-verified: not GNG-0-signed, `results-log/f1k.jsonl`
> absent). New
> `frozen_sha256 = d4d58cb6355838996a5abe885b3db53a6f3301e9101b6585af5ab5b91f9b9da5`.
> Everything LEFT UNCOMMITTED for the round-4 re-review. $0, no GPU.

1. **Complete declarative schema** (`analysis/f1k.py`, new pinned sha
   `8d05201fac55…`; `output_fields` unchanged 50/50; ASM-2382): the ENTIRE
   run record is validated recursively against `kot-f1k-record/1`,
   default-deny at EVERY depth (`additionalProperties:false` + required at
   every object node; a type/registered-pin/bound on every leaf) —
   (a) SIDECAR interiors: `replace` requires ALL of {ran strict-bool,
   delta_r_dev, n_ni, io_saving} with run/defer coherence;
   `mc_exact_power` interior pinned EXACTLY to {mu\*=4.09, n_sim=10000,
   seed=20260713, pass=true, ASM-2371 marginals}; `mc_intersection` must
   equal the registered ASM-2376 content EXACTLY (`{"bogus":1}` rejected);
   `cost` fully typed (integer prefills; hours ≤ the 900 h REG wall-clock
   cap) AND resume-safe-ledger-coherent (usd_total ≈ usd_spent_prior +
   run_hours×rate — usd_total=0 with positive metered time rejected);
   `carriers` bound by the frozen kaec_format arithmetic — params_added ==
   C·layers·D for an INTEGER D (the real-run D=6144 binds at the
   generator-spec/driver seam) and table_bytes == the exact KAEC fp32
   file size. INTRA-PASS CORRECTION (pre-review): the first application
   over-pinned n_ni (int == 1573) and carriers (D == 6144); the untouched
   driver's $0 `--mock` — run against the new schema as the
   emission-surface oracle — caught both at its official-seam step (n_ni
   is the rounded §R-REV4.3 NI-power NUMBER, RUN iff ≤ 1573; the stub
   engine lawfully runs at its own D). A second intermediate (`a7f971…`) additionally
   required the kot-log/1 chain fields on the record line, which the
   mock's lawful bare-body direct shape-check cannot carry (log-append
   stamps them) — they are now typed WHEN PRESENT, presence owned by
   kot-log-1/log-append. Both superseded intermediate freezes (`e2022a…`,
   `a7f971…`; neither posted/reviewed/committed) were normalized away by
   the same one-shot; `--mock` now runs end-to-end green. (b) ROWS: closed row schema — 7-arm enum (an
   UNKNOWN-ARM row was silently ignored before), `pass` a STRICT integer in
   its per-arm range (the `int()` string-coercion path REMOVED), all fields
   required, registered tags, no unknown keys. (c) RECORD LINE: config
   pinned, `metrics.rows_emitted` == rows actually pinned, strict seam
   (non-eligible stdin lines rejected, never skipped). Channels unchanged:
   structural ⇒ `ERR_P2_ANALYSIS`; present-but-invalid attestation values ⇒
   gates fail closed (INSTRUMENT-INVALID). Selftest [MEASURED, green]: a
   **159-probe full-depth structural sweep derived from the schema itself**
   (every required key at every depth popped; every nested block ×
   null/int/string; unknown keys injected at every object/map node) + 47
   value-level gate probes + 11 row-schema + 10 record-level rejections;
   the all-true/all-present fixture still PASSES; round-trip byte-stable.
2. **Paired-sidecar tests added** (round-3b independent HOLD reason —
   neither registry suite had one): a 12-test class through the REAL CLIs
   covering success (+`inputs.paired_artifacts_verified`), each failure
   mode (`ERR_P2_SIDECAR_MISSING/DRIFT/MALFORMED/AMBIGUOUS/ORPHAN`), the
   rows-dup guard on paired records, the kot-log/1 non-run scope guard for
   `role:"sidecar"`, and the rows-only/unmarked preservation controls.
   Direct suites: **135 tests, 135 passed, 0 failed, 0 skipped**
   [MEASURED]. The reviewer's 23/100-skip run reproduces only in a sandbox
   with NO writable temp dir — every skip is loud
   (`make_temp_root` → `skipTest`) and names `KOT_TEST_TMPDIR` as the cure.
3. **REAL seam round-trip** [MEASURED]
   (`tools/registry/_f1k_seam_roundtrip_20260716.py`, sandboxed repo root,
   real log-append → verdict-gen → pinned analysis): valid campaign →
   **PASS-PENDING-AUDIT**; `guard.byte_identical=false` (value) →
   **INSTRUMENT-INVALID** (rule 0); `mc_intersection={"bogus":1}` (nested),
   row `pass="0"` (row), `rows_emitted` off-by-one (record) → each
   **ERR_P2_ANALYSIS with NO verdict emitted**.
4. Kill criterion, envelope, budget, geometry, power table byte-identical
   (asserted by `tools/registry/_f1k_round4fix_20260716.py`);
   `registry-check` PASS. RT-15 post line becomes:
   `prereg freeze f1k frozen_sha256=d4d58cb6355838996a5abe885b3db53a6f3301e9101b6585af5ab5b91f9b9da5`.

---

## HOLD round-6 — final static review (2026-07-16, fable/writer-2)

> The F1-K final static review CONFIRMED provenance consistency (schema
> architecture, driver, geometry, intersection, seam, provenance chain
> sound) and found TWO residual static-validation defects in the pinned
> `analysis/f1k.py`. Both are FIXED as a CLASS; sixth lawful pre-final
> reset-refreeze (still no GNG-0 signature, no `results-log/f1k.jsonl`,
> no spend, no unblind). New
> `frozen_sha256 = 974f403176216f3221b12583b70816880d357d5ae58e0f1d7d3b0642d6106987`
> (analysis pin `55eafe34…` → `54924cfd…`; `output_fields` unchanged
> 50/50). $0 spend, no GPU. Left UNCOMMITTED for coordinator re-verify.

### Defect 1 — regex anchor: trailing-newline bypass (class fix)

- **Was:** every "strict" pattern on a validity/provenance-bearing field
  (`RUNNER_RE`, `HEX64_RE`, `TS_RE`, the `pins_observed` key pattern) was
  applied via `re.match(...$)`. Python `$` matches BEFORE a terminal
  newline, so `"runner-1\n"`, 64-hex+`"\n"` (prev_sha256 / prereg_hash /
  artifacts / pins_observed values), a trailing-newline timestamp, and a
  trailing-newline pin KEY all satisfied the declared patterns.
- **Now:** all four patterns are `\Z`-anchored and BOTH `_sv` call sites
  (string `pattern`, map `key_pattern`) use `re.fullmatch` — no
  trailing- or embedded-newline value validates; NO regex on a
  validity/provenance field uses `$` (grep-verified: zero remaining
  `re.match`/`$"`-anchored uses).
- **Selftest [MEASURED, green]:** 7 new record-level probes — trailing-`\n`
  runner / ts / prev_sha256 / prereg_hash / pins_observed key /
  pins_observed observed-sha + an embedded-`\n` runner, each REJECTED
  fail-closed; the clean-value round-trip still passes byte-identically.

### Defect 2 — zero / under-reported ledger validated (budget honesty)

- **Was:** the ledger checks were purely RELATIVE identities with rounding
  tolerances ($0.01 / 0.001 h) and `min=0` schema bounds: with
  `prefills=1`, 1 s phases, rate 0.28 and all totals ZERO, run_h =
  0.000833 h sat within `HOURS_TOL` of `instance_hours=0` and the $0.000233
  expected spend within `COST_TOL_USD` of `usd_total=0` — an all-zero (or
  coherently 10×-under-reported) cost ledger validated beside an
  otherwise-PASS record.
- **Now:** BUDGET-HONESTY SCALE FLOORS at the registered campaign scale
  (REG `budget_note`, ASM-2374/-2205 corner: 22,516 prefills → 521.2
  instance-h → ~$146): `usd_total ≥ $73.0` and `instance_hours ≥ 260.6 h`
  [STIPULATED at HALF the corner — admits up to 2× better-than-corner
  realized throughput, rejects any ≥2× under-report], `prefills ≥ 11,011`
  (= 1573 × 7 mandatory arm-passes, a deterministic COUNT under the
  frozen design [MEASURED arithmetic]), `construction_instance_hours > 0`.
  The $155 ceiling and every round-4/5 coherence identity unchanged.
- **Selftest [MEASURED, green]:** the all-zero ledger (the review's
  exploit verbatim), the positive-hours/zero-dollars ledger, and the
  coherently 10×-under-reported ledger ($14.60) each REJECTED; the
  full-scale corner ledger ($145.968 / 521.2 h / 19,444 prefills) is the
  passing fixture (mock A + byte-stable round-trip).
- The driver's `$0 --mock` cost CONFIG now carries the ASM-2374
  planning-scale prior/construction figures (146.0 / 521.2 — real
  registered figures, not mock inventions, same [R6-4] precedent as the
  power table) so the emission-surface oracle runs end-to-end green at
  $0 real spend. Only these two config values changed in the driver.

### Verification [MEASURED]

- `python3 analysis/f1k.py --selftest` green: 173-probe structural sweep
  + 47 gate + 11 row + 26 record-level rejections, 50/50 output fields.
- `registry-check` PASS after refreeze; frozen index == record.
- Correction chain (`registry/corrections/f1k/1-prefreeze-correction.json`)
  amended: chain terminated at `974f4031…`, round-6 change entry +
  build-artifact (`tools/registry/_f1k_round6fix_20260716.py`) appended.
- 135 registry tests + the real-seam round-trip one-shot: see the
  hand-off report (run in the writable env; coordinator re-verifies).
