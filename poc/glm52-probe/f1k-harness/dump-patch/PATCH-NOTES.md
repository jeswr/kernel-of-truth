# kot-f1k-dump/1 — construction-only moe()-input dump patch  [REVISION-0]

> **DRAFT — AUTHORED + MOCK-VALIDATED ONLY, NOT DEPLOYED.**
> This model-engine C patch MUST pass a **gate-0 Codex review** before any
> real Modal run (exactly as the gate-0 KaE patch `11f8b458` did — the
> handoff bead kernel-of-truth-xq0h item 2 makes this explicit). Nothing
> here has touched a governed model, weights, Modal, or any frozen record.
> All validation below is **$0**: a mock engine + compile-level checks.

Authored by engineer-1, 2026-07-16, against the run-log scoping in
`../opus-runs/20260716T161222Z/run-log.jsonl` (`bringup-scope` entry) and
the ENGINE HIDDEN-STATE DUMP CONTRACT frozen in the pinned generator
`../build_carriers.py` (sha `cda62364`, REG A(vii)). DES anchor:
`docs/next/design/glm52-followup-experiment.md` §2.4 / §2.8 item-3.

## What it is

The F1-K carrier construction needs, for every construction pass, the SUM
over gated token positions of GLM-5.2's hidden state **at the moe() input**
(`c/glm.c:1277`, row `s` at `x + s*D`), per candidate splice layer.
`build_carriers.py` turns those sums into the §2.4 f64 mean-difference KaE
tables. This patch adds that dump mode — `run_kae_dump`, env-gated by
`KAE_DUMP=<manifest>` — **on top of** the gate-0 KaE patch
(`kae-add-path.patch`, sha `11f8b458`, colibri base `a78a06fc`).

A wrong moe()-input dump silently corrupts every carrier and wastes the
whole paid run, so the byte-identity and f64 re-derivation checks below are
load-bearing and were **measured**, not asserted.

## Files

| File | What it is |
|---|---|
| `kot-f1k-dump.patch` | Unified diff **vs the KaE-patched tree** (apply order: colibri@a78a06fc → `kae-add-path.patch` → this). Adds `c/kae_dump.h` + `c/tests/test_kae_dump.c`; edits `c/glm.c` (+107) and `c/Makefile` (1 dep line). sha256 `066565d5…` (registered in `f1k.json` pins at deploy as an ops amendment, like the KaE patch). |
| `kae_dump.h` | Reference copy of the dump core (accumulator + capture + KAED writer; reuses `kae.h` span binding). `real-checks.sh` asserts it is byte-identical to the patch payload. |
| `test_kae_dump.c` | Reference copy of the in-patch unit suite (43 checks). |
| `mock_glm_dump.c` | MOCK-ONLY tiny engine linking the SAME `kae_dump.h`, with an exact-in-f32, causal, independently re-derivable toy hidden state. |
| `validate.py` | The $0 mock validation battery (V1–V6 below). |
| `real-checks.sh` | The $0 real-source battery: patch applies on the pinned KaE tree, engine builds, unit suites green, objdump per-function inertness. Re-run on Modal at bring-up before any real dump. |
| `validate.log`, `real-checks.log`, `tok-selftest.log` | Measured outputs of the three batteries (2026-07-16, all PASS). |
| `asm-f1k-dump-2485-2491.json` | Companion assumption block ASM-2485..2485 (owner engineer-1), for the coordinator to register with the landing commit. |

The kot-f1k-tok/1 tokenizer wrapper is `../tok_glm52.py` (see below).

## The exact glm.c span touched (patched-file line numbers)

1. **glm.c:39** — `#include "kae_dump.h"` (after `kae.h`).
2. **glm.c:576–582** — file-scope `static KaEDump *g_kdump = NULL;` next to
   `g_kae`. Deliberately **not** a `Model` field (ASM-2486): `sizeof(Model)`
   and `model_init` stay byte-identical (the KaE patch's `model_init` delta
   came from its appended `KaE*` field; this patch has none).
3. **glm.c:1286–1291** — the ONE hook in `moe()` (KaE-tree anchor
   glm.c:1277, shifted to 1284 by hunks 1–2), at its head, on its input:
   `if(g_kdump) kaed_capture(g_kdump, layer, pos_base, S, D, x);`
   READ-ONLY (`const float *x` in `kaed_capture`). `moe()`'s signature is
   unchanged, so `layer_forward` is untouched (unlike the KaE patch).
4. **glm.c:1994–2056** — `run_kae_dump(Model*, const char*)`, placed after
   `run_kae_score` and mirroring its manifest parser (`T t_0..t_{T-1}
   s_0..s_{T-1}`, the KAE_SCORE span convention) and its
   one-`layers_forward`-prefill-per-line / `kv_alloc(maxT)` pattern — the
   pattern gate-0 already reviewed. Differences from the scorer: parse
   errors and zero-gated lines **abort with nonzero exit** instead of
   skipping the item (ASM-2489 — a silently dropped pass would corrupt the
   §2.4 means), and nothing is printed to stdout (results go only to
   `KAE_DUMP_OUT`; codex blocker-1 discipline).
5. **glm.c:2793–2801** — phase-separation guard in `main()` BEFORE model
   load (ASM-2487): `KAE_DUMP` + (`KAE_SCORE` or `KAE=1`) → abort.
6. **glm.c:2872–2886** — arming after `model_init` (geometry known):
   `kaed_arm(KAE_DUMP_LAYERS, KAE_DUMP_OUT, hidden, n_layers)`; NULL →
   **abort** (a construction run must never silently proceed undumped —
   contrast `kae_load`, whose NULL lawfully degrades for scoring); then the
   REQUIRED stderr provenance echo.
7. **glm.c:2923–2929** — dispatch `if(getenv("KAE_DUMP")) run_kae_dump(...)`
   ahead of (and mutually exclusive with) `KAE_SCORE`/`SCORE`/`SERVE`.
8. **Makefile:88** — `kae_dump.h` added to the `glm` dependency line.

## Additive / phase-separation argument

- **Scoring binaries stay KaE-patch-only.** The Modal harness builds the
  SCORING engine from colibri + `kae-add-path.patch` alone; this dump patch
  is applied only in the CONSTRUCTION build (bead xq0h item 1's image
  applies both, but the scoring entrypoints run with `KAE_DUMP` unset and
  the objdump proof below bounds what that code path can differ by; if the
  gate-0 reviewer prefers two physical binaries, the patch supports that
  trivially — it is the runner's build choice, not a code constraint).
- **With `KAE_DUMP` unset** the only added executed code is: one false
  `getenv("KAE_DUMP") && …` guard in `main()`, one more NULL `getenv` test
  at dispatch, and the `if(g_kdump)` false branch per `moe()` call. No
  computed activation changes. [MEASURED] at machine level (`real-checks.sh`
  step 6, gcc 11.5 `-O2 -march=x86-64-v3`): **79 shared functions; only
  `moe` and `main` differ** — exactly the two wired; none removed;
  `layer_forward` and `model_init` byte-identical. (The three "new" symbols
  `kae_load`/`run_score`/`kaed_arm` are outlining artifacts: they existed
  before but were inlined into `main`; with `main` larger, gcc emits them
  standalone. Address-normalized per-function comparison, clone-aware
  parser — see "bringup.sh parser note" below.)
- **With `KAE_DUMP` set** the forward is STILL untouched: the capture reads
  `x` and never writes engine state, and `KAE=1` (the only thing that
  writes activations) is excluded by the guard. [MEASURED] mock check V1:
  armed-run forward output byte-identical to the pre-dump engine's.
- The dumped states are therefore the **UNMODIFIED** model's — required,
  since the §2.4 mean difference is between plain WITH/WITHOUT-explication
  prefills (no carrier exists yet at construction time).

## Env contract (exactly build_carriers.py's frozen dump contract)

| Var | Required | Meaning |
|---|---|---|
| `KAE_DUMP` | arms | manifest path; one pass per line `T t_0..t_{T-1} s_0..s_{T-1}` (-1 = ungated) |
| `KAE_DUMP_OUT` | yes (when armed) | KAED output: `"KAED" i32 n_lines, nl, D, layer_id[nl]`, then per line `i32 gated_count, f32 sum[nl*D]` (little-endian, ASM-2491) |
| `KAE_DUMP_LAYERS` | yes (when armed) | csv of dump layer ids = the A(iv) candidate splice-layer union (real runs: 3..78); **csv order = slot order** in the file |
| `KAE_SEED` | echo only | echoed verbatim in the arm line; the dump path consults **no RNG**; `run_dump` exports the registered `CONSTRUCTION_SEED=20260716` and fails closed on mismatch |
| `KAE` / `KAE_SCORE` | must be unset | phase separation (ASM-2487): either one present with `KAE_DUMP` → abort before load |

Arm-time stderr echo (REQUIRED, carrier-HOLD fix 5), matching the pinned
`ECHO_RE` in build_carriers.py byte-for-byte in format:

```
[KAE-DUMP] armed: <nl> layers, D=<D>, seed=<KAE_SEED> (provenance echo; dump path consults no RNG)
```

## How build_carriers.py consumes the dump

`construct` → `run_dump()` writes the per-batch manifest (token ids +
per-position slots from the kot-f1k-tok/1 offsets ∩ template char-spans),
exports the env above, executes `--engine-cmd`, then **fails closed**
unless: exit 0, echo present with `seed == CONSTRUCTION_SEED`, magic
`KAED`, `layer ids == requested`, `n_lines == passes`, `D == 6144`,
`gated_count > 0`, no trailing bytes. Per line it computes
`mean = sum / gated_count` in f64, then the registered §2.4 / §R2
mean-difference + reference-norm arithmetic. `verify --expect-mode real`
re-derives everything cell-by-cell (the #46 integrity guarantee).
Engine-side accumulation is f64 over gated positions in ascending
absolute-position order, cast to f32 at write (ASM-2485) — cell-for-cell
the arithmetic of the repo mock `mock_colibri_dump.py`, so the $0 pipeline
and the real engine share one contract.

## Mock validation — MEASURED results (2026-07-16, this box, $0)

`python3 validate.py` → **MOCK VALIDATION PASS, 32/32 checks** (`validate.log`):

- **V1 byte-identity** [MEASURED]: pre-dump reference engine vs dump engine
  with `KAE_DUMP` unset: forward outputs **byte-identical**; armed dump run:
  **still byte-identical** (read-only capture).
- **V2 f64 re-derivation** [MEASURED]: all **192 dumped cells** (4 lines ×
  3 layers × D=16, exact-in-f32 causal toy states) == an independent pure-
  Python float64 re-derivation, **bit-exact** after the f32 cast.
- **V3 echo** [MEASURED]: echo fires on stderr, matches the pinned
  `ECHO_RE` **literal** (asserted still present in build_carriers.py),
  `seed == KAE_SEED == 20260716`; seed-absent run yields `seed=-` which the
  harness comparison rejects.
- **V4 gating semantics** [MEASURED]: single-gated line == exactly that
  position's hidden vector; `CHUNK=3` prefill (advancing `pos_base`) gives a
  **byte-identical** `.kaed` (absolute-position gating).
- **V5 fail-closed battery**: 9/9 abort cases exit nonzero (both
  phase-separation cases, missing OUT/LAYERS, duplicate/out-of-range layer,
  zero-gated line, malformed token, dump layer that never reaches `moe()` —
  the ASM-2488 per-slot count invariant).
- **V6 unit suite**: `test_kae_dump.c` **43/43** plain and under
  **ASan+UBSan+LSan** (clean, zero diagnostics, zero warnings).

`bash real-checks.sh` (COLIBRI_TREE = pristine base, blob-pinned
`1d74f788`) → **REAL-SOURCE CHECKS OK** (`real-checks.log`): KaE patch sha
verified + applied → dump patch applies cleanly → reference copies
byte-identical to patch payload → `make glm ARCH=x86-64-v3` builds →
`test_kae` **44/44 unchanged** → `test_kae_dump` **43/43** → objdump
inertness as above.

`python3 ../tok_glm52.py --selftest` → **TOK SELFTEST PASS, 8/8**
(`tok-selftest.log`): kot-f1k-tok/1 contract on a constructed tokenizer —
JSONL round-trip, multibyte **char** offsets (é/CJK), template-spec
intersection rule, sha-pin + malformed-input fail-closed.

**[STIPULATED] scope limit:** no check above touched GLM-5.2, its weights,
or the real 6144-dim geometry. Modal bring-up MUST re-run: `real-checks.sh`
battery on the build box, `test_kae` 44/44 + `test_kae_dump` 43/43, the
objdump proof on the production binary, tokenizer-vs-engine id consistency,
and a tiny real dump sanity pass — all BEFORE `construct --mode real`.

## kot-f1k-tok/1 (`../tok_glm52.py`)

`build_carriers.py`'s `--tokenizer-cmd` is a seam, not an implementation:
the repo's `mock_tokenizer.py` is **mock-only**, so the real construction
DOES need this wrapper (bead xq0h item 3). It wraps the pinned GLM-5.2
`tokenizer.json` (staged with the weights; `TOK_SHA256` pin fail-closed,
ASM-1971 discipline) behind the frozen contract: stdin JSONL `{"text"}`,
stdout JSONL `{"ids","offsets"}`, Python-str char offsets validated
fail-closed (ASM-2490), `add_special_tokens=False`.

## Open questions for the gate-0 Codex review

1. **ASM-2485 precision reading.** The frozen contract says sums are "in
   the engine's own f32". Implemented as: f32 summands (the engine's own
   hidden values, untouched), **f64 accumulation**, f32 emit — matching the
   repo mock's arithmetic exactly. Confirm this reading (the alternative,
   pure-f32 accumulation, would diverge from the mock and lose precision at
   6144-dim/many-gated-token scale).
2. **bringup.sh §5 parser note.** The existing bringup.sh function-label
   regex (`<(\w+)>`) does not match gcc clone symbols (`moe.constprop.0`);
   on gcc 11.5 that mis-attributed clone bodies and false-flagged
   `layers_forward`/`read_arr` until fixed. `real-checks.sh` carries the
   corrected parser (`<([\w.]+)>`, clone-suffix-aware allowed-set). The
   coordinator should port this one-line fix into bringup.sh's step 5 for
   the Modal runs (bringup.sh untouched here — frozen-experiment harness
   discipline).
3. **Allowed-diff set for the dump equivalence gate** = `{moe, main}`
   (plus new/outlined symbols), NOT the KaE set `{moe, layer_forward,
   main, model_init}` — confirm as the registered expectation.
4. **kv-cache reuse across manifest lines** mirrors `run_kae_score`
   (per-line full re-prefill from position 0). Confirm the same acceptance
   argument transfers to the dump path.
5. **One image, two binaries?** Decide whether the Modal image builds the
   scoring binary KaE-only (strict phase separation by artifact) or relies
   on the env gating + objdump proof (phase separation by measured
   inertness). Authoring supports either.
