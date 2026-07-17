# F1-K inertness-gate resolution — functional gate authoritative, objdump demoted (OPS change, no re-freeze)

**Decision owner:** Fable design (this memo). **Date:** 2026-07-17.
**Trigger:** runner-7 run-log `poc/glm52-probe/f1k-harness/opus-runs/20260717T003208Z/`
(+ preserved `gate-pull/bringup/f1k-gate/kae-bringup.log`): `bringup_gcp.sh` step 5/5
objdump per-function byte-equivalence FAILS on the GCP VM (AMD EPYC 7B13, VM gcc,
`-O2 -march=native`): `functions differ OUTSIDE allowed [layer_forward, main,
model_init, moe]: [attention, run_serve, tok_load]`, plus `kae_load` emitted
un-inlined and `kae_free.part.0` partially outlined. Everything else on the VM
PASSED (colibri pinned a78a06fc, KaE patch sha 11f8b458 verified+applied, build OK,
test_kae 44/44). The identical chain PASSES on the control box (Intel, gcc 11.5)
and at `-march=znver2` / `-march=znver3` — only the 4 allowed functions differ
[MEASURED, run-log `local-repro` entry].

## 1. Decision

**Option 1, with a flag-pinned remnant of option 3 applied to the CHECK (never to
the production build):**

- **AUTHORITATIVE inertness gate = FUNCTIONAL:** with `KAE`/`KAE_SCORE`/`KAE_DUMP`
  unset, the KaE-patched PRODUCTION binary's forward/scoring output must be
  **byte-identical** to the pristine (pre-patch) engine's on the real box, real
  weights, identical inputs — preceded by a same-binary determinism pre-check.
  Fail-closed (`ERR_F1K_BRINGUP_FUNC`).
- **objdump machine-code equivalence is DEMOTED to a patch-shape check:**
  - it stays **fail-closed at the pinned REFERENCE flags** `-O2 -march=x86-64-v3`
    (the exact basis on which the allowed sets were MEASURED: ASM-2486 for the
    dump set {moe, main}; the gate-0 88/92 proof for the KaE set
    {moe, layer_forward, main, model_init}; also `real-checks.sh`'s existing
    default) — deterministic there across every toolchain tried;
  - it additionally runs at production-equivalent `-O2 -march=native` as
    **ADVISORY only**: full differing-function list logged to `$GATE` for audit,
    never fatal.
- The production build keeps `-O3 -march=native` (the affordability window is
  tight; never constrain the paid campaign to satisfy a proxy check).

### Why not option 2 (widen the allowed set)

`attention` and `tok_load` are ON the scoring path. Adding them to the allowed
set converts the gate into "any byte diff in the forward pass is fine", i.e. it
guts the one thing the gate exists to catch — and the widened set would be
reactive (the next gcc point-release can spill a different function), requiring
a new widening each time with a hand-written "codegen-only" argument each time.
An argument is exactly what the functional gate replaces with a measurement.

### Why not option 3 (pin compiler + -march for everything)

To keep the objdump gate sound it must compare objects built the way the
production binary is built; pinning `-march=x86-64-v3`/a fixed gcc for the REAL
runs surrenders native codegen on a CPU-bound $73–155 campaign (260.6–900
instance-hour window) to preserve a proxy, and pinning the exact gcc build on an
apt-provisioned Spot VM adds ops fragility for zero scientific gain. Runner-7's
repro also shows `-march` alone is not the trigger (znver3 passes off-box; the
VM's own gcc at native fails) — the deterministic-codegen premise is exactly the
toolchain-brittleness being escaped.

### Why the functional gate is the right authority

- The guarantee the science needs is functional, and the FROZEN record already
  encodes inertness functionally everywhere it speaks: the registered VOID is
  the SS2.5/SS7.4 **off-concept guard byte-identity** (60 items, strict-boolean,
  hard-coded fail-closed in the pinned `analysis/f1k.py`,
  `GUARD_N_REGISTERED = 60`); the dump contract's V1 is forward-output
  byte-identity; PATCH-NOTES precondition (b) is "output byte-identical".
  Machine-code equivalence was always a $0 **proxy** chosen when no weights were
  on-box; at bring-up the weights ARE on-box, so the direct property is
  measurable.
- Mechanism of the observed spill (why it is codegen, not behaviour): the patch
  adds file-scope symbols and env-gated branches; gcc's inlining/outlining and
  scheduling decisions are global, so on a different toolchain the perturbation
  lands in neighbouring functions (`kae_load` un-inlined and `kae_free.part.0`
  are the same outlining artifact class PATCH-NOTES already documents for
  `run_score`/`kaed_arm`). With KAE unset, `kae_load`/`kae_free` are never
  called and the `moe()` gate branch is false — and instead of ARGUING that,
  the new gate MEASURES it on the production binary.

## 2. Re-freeze or ops? — **OPS-HARNESS EDIT. No re-freeze.**

Checked against the frozen record `registry/experiments/f1k.json`
(sha256 505165ee… per `registry/frozen-index.json`):

- The frozen record contains **zero** occurrences of `objdump`, no allowed-diff
  set, no per-box machine-equivalence obligation, and no hash pin of
  `bringup.sh`/`bringup_gcp.sh`/`real-checks.sh`.
- The only inertness sentence in the record is in `/pins/harness_manifest`:
  *"inert-by-default proven (88/92 functions byte-identical at KAE=0)"* — a
  **past-tense gate-0 provenance fact** (measured on the gate-0 toolchain). It
  remains true and is not touched.
- The registered pre-run gates are the freeze-manifest ordering items
  ("(7) bring-up s/prefill + affordability gate"); the registered inertness
  instrument is the run-time functional guard VOID above. Neither changes.
- The allowed-diff sets live only in: `bringup.sh` (frozen-harness-discipline
  copy — stays untouched), its authorized ops port `poc/gcp/bringup_gcp.sh`,
  `dump-patch/real-checks.sh`, and assumption row ASM-2486 (register entry,
  MEASURED at gcc 11.5 `-O2 -march=x86-64-v3` — the demotion **aligns** the ops
  gate with that registered measurement basis rather than contradicting it).
- There is no `results-log/f1k.jsonl` and no phase:final run, so a lawful
  reset-refreeze WOULD be available — but nothing frozen needs changing, so it
  is not used.

## 3. Exact change (coordinator steps — nothing frozen is touched)

1. **`poc/gcp/bringup_gcp.sh` step 5** (ops edit, run-logged):
   - change `CFLAGS_EQ` default `-O2 -march=native` → `-O2 -march=x86-64-v3`;
     keep the clone-aware parser and the allowed set
     `{moe, layer_forward, main, model_init}`; this pass stays **fail-closed**;
   - add a second, clearly-labelled **ADVISORY** parser pass at
     `-O2 -march=native`: print the full differing/added/removed lists, write
     them to `$GATE/objdump-native-advisory.log`, never exit nonzero;
   - after the KaE build, also build the PRISTINE engine (from the
     `/tmp/glm_pristine.c` snapshot / a pristine tree copy) with the SAME
     production flags (`make glm ARCH=native`) and leave it at a declared path
     (e.g. `$WORK/c/glm_pristine`) for step 2 below.
2. **`poc/gcp/f1k_worker.sh`** (ops edit): insert a new fail-closed step after
   estate staging + both engine builds — **"functional inert-by-default gate
   (KAE unset) — AUTHORITATIVE"**:
   - env: `KAE`, `KAE_SCORE`, `KAE_DUMP` all unset; `OMP_NUM_THREADS` pinned to
     a fixed value used for both binaries;
   - (i) **determinism pre-check**: the patched binary, one fixed prefill input,
     run twice → byte-identical output; a failure here is a real instrument
     stop (it would equally invalidate the registered SS2.5/SS7.4 guard
     byte-identity VOID instrument) and MUST surface before any spend;
   - (ii) **pristine vs patched**: identical prefill inputs — reuse the ≥20-item
     affordability sample spanning the short (b0) and long (d3-prepend) shapes —
     through `glm_pristine` and the patched `glm`; outputs compared
     byte-for-byte (this also yields the affordability timing sample at no
     extra cost);
   - any mismatch → `ERR_F1K_BRINGUP_FUNC`, `die` (the runner-7 EXIT trap,
     commit 7af46417, already mirrors `$GATE` on every exit path).
3. **Register a new ASM row** (MEASURED, owner: this decision) recording: the
   native-flags spill on EPYC 7B13 (`attention, run_serve, tok_load` + outlined
   `kae_load`/`kae_free.part.0`), the control-box gcc 11.5 + znver2 + znver3
   PASS repro, and the new gate hierarchy (functional authoritative on-box;
   objdump fail-closed at reference flags `-O2 -march=x86-64-v3`; advisory at
   native). backing_ref: run-log 20260717T003208Z `diagnosis` entry +
   `kae-bringup.log` + this memo.
4. **Run-log** the ops change on the next runner entry (frozen-run discipline).
5. **Do NOT touch**: `registry/experiments/f1k.json`, `registry/frozen-index.json`,
   `poc/glm52-probe/f1k-harness/bringup.sh`, `dump-patch/real-checks.sh`
   (the $0 off-box batteries stay exactly as gate-0 reviewed them; they remain
   the fail-closed patch-shape regression gates at their pinned flags).

## 4. Residual risk

1. **Sampled, not exhaustive:** functional byte-identity over a finite prefill
   set cannot exclude a data-dependent divergence on unexercised paths.
   Layered mitigation: the fail-closed reference-flags objdump gate still bounds
   the patch's machine-level footprint; the advisory native diff-list is
   preserved for audit; and the registered 60-item off-concept guard
   byte-identity VOID re-measures functional inertness at run time, fail-closed
   in the pinned analysis. (`run_serve` is not reachable from the scoring path;
   `attention`/`tok_load` are exercised by every prefill in the sample.)
2. **Threading nondeterminism:** if the determinism pre-check fails under
   OpenMP, the comparison method is void — but that failure is a true positive
   (it also invalidates the registered guard instrument) and must stop bring-up
   anyway. Pin `OMP_NUM_THREADS` for the check.
3. **Reference-flags objdump on the VM's own gcc is untested for the KaE
   patch** (the VM died at step 5 before any x86-64-v3 compile there; the
   znver2/znver3/x86-64-v3 passes are control-box gcc 11.5). If Ubuntu 22.04's
   gcc 11.4 spills even at the pinned flags, the fail-closed reference pass will
   stop bring-up again — cheaply (~minutes at $0.17/h, log preserved by the
   EXIT trap) and with a genuinely new datum; that outcome would justify moving
   the reference pass off-box-only, not widening the set.
4. **Advisory drift:** the native-flags advisory will keep listing extra
   functions on this toolchain; it must stay labelled ADVISORY so a future
   runner neither re-promotes it nor reads it as a red flag.
5. **Cost:** one extra native build (minutes) + ~2× a ≥20-prefill sample on the
   CPU-bound 384 GB model — bounded, and step (ii) doubles as the affordability
   timing sample.

## 5. Addendum (2026-07-17, runner-8 datum) — reference-flags objdump moved off-box-only

**New measured datum** (runner-8 run-log `poc/glm52-probe/f1k-harness/opus-runs/20260717T015601Z/`,
`gate-pull/bringup/f1k-gate/kae-bringup.log`): step 5 objdump FAILS **even at the
reference flags** `-O2 -march=x86-64-v3` on the GCP VM's Ubuntu gcc —
`functions differ OUTSIDE allowed [layer_forward,main,model_init,moe]:
[attention, run_serve, tok_load]` (shared 78; patch-added `kae_free.part.0`,
`kae_load`). This is exactly residual-risk §4.3 above, and the outcome that risk
pre-committed to: the equivalence is **gcc-VERSION-brittle**, not merely
-march-brittle — the allowed set reproduces fail-closed only on the toolchain
that measured it (control-box gcc 11.5). Worse, step 5 ran BEFORE the
authoritative functional gate in `f1k_worker.sh`, so the proxy was blocking the
real measurement (bring-up died at ~$0.05 without the functional gate ever
executing).

**Decision (option A, per §4.3's pre-registration and ASM-2503's
resolution_path):**

- `poc/gcp/bringup_gcp.sh` step 5 is now **ADVISORY-ONLY on the run box at BOTH
  flag sets** (reference `-O2 -march=x86-64-v3` AND production-equivalent
  `-O2 -march=native`): the clone-aware parser logs the full
  differing/OUTSIDE-allowed/added/removed lists to
  `$GATE/objdump-{reference,native}-advisory.log` and never exits nonzero.
- The **fail-closed reference-flags objdump pass moves OFF-BOX-ONLY**: the
  frozen `bringup.sh` and `dump-patch/real-checks.sh` stay untouched and remain
  the fail-closed patch-shape regression gates on the gate-0 gcc-11.5
  measurement basis (where they PASS).
- The **sole fail-closed inertness gate on the run box** is the functional
  KAE-unset pristine-vs-patched byte-identity gate in `f1k_worker.sh`
  (`ERR_F1K_BRINGUP_FUNC`) — toolchain-independent, real binary, real weights.
- The allowed set is **never widened** (§1 "why not option 2" stands: the next
  gcc point-release would just spill a different function).
- **Same principle applied downstream before it masks again:**
  `dump-patch/real-checks.sh` step 6/6 is the identical proxy class (objdump at
  `-O2 -march=x86-64-v3`, allowed `{moe, main}` per ASM-2486) and runs on-box
  at worker step 4/5 — BEFORE the functional gate. `real-checks.sh` itself
  stays untouched (gate-0-reviewed; its step-6 proof stands fail-closed
  off-box at gcc 11.5). Instead, `f1k_worker.sh` now tolerates exactly ONE
  failure signature from it: steps 1–5 provably passed (`test_kae: 44/44` +
  `test_kae_dump: 43/43` lines present) AND the sole `ERR_F1K_DUMP_CHECK` is
  the step-6 "functions differ OUTSIDE the allowed set" spill (never
  "functions REMOVED") → logged to `$GATE/objdump-dump-advisory.log`, bring-up
  continues. Any other failure stays fail-closed. (Dump-unarmed inertness is
  not campaign-load-bearing: the construction engine is only ever used ARMED;
  the scoring engine carries no dump patch and has the functional gate.)
- Rejected: pinning the exact gcc (§1 "why not option 3" stands — and the
  measurement gcc may not exist in the VM's apt universe); re-measuring a
  VM-local allowed baseline (still not fail-closed across environments, and the
  advisory logs already capture exactly that information for audit without
  inventing a new pinned artifact).

**Ops vs re-freeze: still OPS. No re-freeze.** §2's check is unchanged by this
edit — the frozen `registry/experiments/f1k.json` (505165ee) carries no objdump
obligation, no allowed-diff set, and no hash pin of `bringup_gcp.sh`. ASM-2503
amended in place (its resolution_path pre-registered this exact outcome and
response); bead kernel-of-truth-f2uk.

*Unrelated observation left for the coordinator (out of scope here): the
run-log `provenance-note` about the GCS-restore path folding the `COMPLETE`
sentinel into the ASM-1971 weights manifest hash (19f1a3d0… / 454 files vs
75d53c7d… / 453) — worth an ops fix so the manifest hash is
restore-path-invariant before it is ever compared to a pinned value.*
