# kot-f1k-dump/1 — construction-only moe()-input dump patch  [REVISION-3]

> **REVISION-3 (2026-07-24, engineer-1)** — hardens r2 against the gate-0
> **REJECT** (`poc/gpt56-review/f1k-2zh8-dumppatch-VERDICT.md`), finding by
> finding; regenerated via `git diff --cached` on the pinned KaE tree
> (base `a78a06fc`, KaE patch `11f8b458` applied + committed), so the
> `index` post-image hashes match the real applied blobs.
>
> **r3 patch sha256 `e4e04177068d0d8563ecdd24a4bc1f2c25be93a97992c173207ae760f7543887`**
> (supersedes r2 `fb5d2f35…`, which is REJECTED for construction use; any
> construction pin MUST name the full r3 hash above — see "Downstream pin
> sites" below).
>
> - **(finding 3, integer hardening)** ALL manifest integers now parse
>   ONLY through the new strict `kaed_parse_int` (kae_dump.h): clears
>   `errno`, rejects `strtol` ERANGE, and bounds every value so the
>   `(int)` cast is always exact ([STIPULATED] uniform bound: span slots
>   and pass-1 T reject `v >= INT_MAX`, i.e. hi = INT_MAX-1; token ids
>   bound by `[0, vocab)`). The r2 defect — a span like `2147483648`
>   wrapped negative in the `long→int` cast, `kae_bind_spans` normalised
>   it to `-1`, and the line SUCCEEDED with the malformed position
>   silently ungated, contradicting ASM-2489 — can no longer parse
>   [MEASURED: V5 span-wrap case aborts; unit Test G 9 checks; the exact
>   `2147483648` reproducer is a pinned negative]. Pass-1 T is validated
>   representable BEFORE `(int)t` and before any kv/alloc sizing; manifest
>   READ errors (`ferror`) now abort both passes. Engine + mock hardened
>   identically (`mock_glm_dump.c` links the same helper in the dump
>   build and a byte-equivalent local copy in the ref build).
> - **(finding 4, non-finite fail-closed)** `kaed_write_line` now rejects
>   any NON-FINITE f64 accumulator AND any f32 cast that overflows to
>   Inf, per cell, with a nonzero exit BEFORE the line is written
>   [MEASURED: unit Tests H (NaN via capture, Inf via capture,
>   1e300 cast-overflow, clean-control) and I (/dev/full output failure
>   surfaces nonzero)]. The immediate consumer `build_carriers.py
>   run_dump` INDEPENDENTLY re-verifies every KAED sum is finite AND
>   `gated_count == count(span >= 0)` from its own token rows before any
>   mean-difference arithmetic [MEASURED: selftest probes 4c/4d, 21/21].
>   Truncated-output handling was reviewed sound and is untouched.
> - **(finding 8.2, clone regex)** the dotted-symbol objdump parser
>   (`<([\w.]+)>` + clone-suffix-aware allowed set) is now PORTED into
>   `bringup.sh` step 5 [MEASURED on the r3 build's dis: the old `<(\w+)>`
>   regex matched 66 function labels, the ported one 82 — 16 clone
>   symbols were previously swallowed into preceding bodies].
> - **(finding 6, code-fixable half)** `tok_glm52.py`: the `TOK_SHA256`
>   pin is now MANDATORY — absent/non-hex/mismatched pin ⇒ nonzero exit,
>   no output (r2 warned and proceeded unpinned) [MEASURED: tok selftest
>   10/10 incl. the new absent-pin and non-hex-pin negatives]. The worker
>   bring-up gate (a)
>   contract now requires FULL-CORPUS tokenizer-vs-engine token-id
>   equality (EVERY unique construction text, zero mismatches), never
>   "a few samples". The measurement itself still needs the real engine —
>   see the MANDATORY-BEFORE-PAID-CONSTRUCTION gates below.
> - **(finding 1, identity)** validation counts are r3-true:
>   `test_kae_dump` **64/64** (was 43/43), mock battery **40/40** checks
>   with V5 = **16 fail-closed cases + 1 boundary-accept control** (was
>   34/34, 11 cases), tok selftest **10/10** (was 8/8), generator selftest
>   **22/22** probes (was 19/19; +4c/4d negatives, +4e positive control
>   proving the new consumer checks do not over-reject a valid dump).
>   All [MEASURED] 2026-07-24, this box,
>   gcc 11.5 (the pinned objdump-proof basis), $0 — logs regenerated in
>   place (`validate.log`, `real-checks.log`, `tok-selftest.log`).
> - Findings 5/8.3, the finding-6 measurement half, and finding 7 are NOT
>   code-fixable here: they are REAL-ENGINE measurement gates, kept as
>   explicit MANDATORY-BEFORE-PAID-CONSTRUCTION runner obligations below.
>
> PROPOSED assumption-register amendments (coordinator registers with the
> landing commit; no ASM ids minted here):
> - **PROPOSED-AMEND ASM-2489**: extend the fatal-malformation list to
>   include "an integer that overflows long (ERANGE) or is not exactly
>   representable as int, and a manifest read error" — with r3 the claim
>   "every malformed line aborts" now actually holds (the re-review
>   showed it did NOT hold for r2).
> - **PROPOSED-NEW (dump non-finite invariant)**: every KAED line is
>   finite at write (engine-side, per-cell f64 AND f32-cast checks in
>   `kaed_write_line`) and re-verified finite with a matching
>   `gated_count` consumer-side in `run_dump` before any §2.4 arithmetic.
> - **PROPOSED-AMEND ASM-2490**: the kot-f1k-tok/1 fail-closed posture
>   now covers the `TOK_SHA256` pin itself (MANDATORY in executable
>   behaviour), not only offset validation; and the bring-up
>   engine-equality check is FULL-CORPUS over every unique construction
>   text.
>
> r2's own notes (below) are retained for provenance; where counts/shas
> conflict, THIS r3 block governs.

> **REVISION-2 (2026-07-16, engineer-1)** — clears the two NEEDS-WORK items
> from the gate-0 correctness review of r1 (commit `8fcf7e6a`, in-file
> "REVISION-0"): **(review item 5)** the `run_kae_dump` manifest parser now
> REJECTS a wholly non-numeric/garbage line and trailing junk after the
> required 2T+1 integers (r1 silently `continue`d past garbage lines and
> ignored trailing fields) — engine + mock hardened identically, two new
> [MEASURED] negatives added (V5 is now 11 cases; battery 34/34);
> **(review item 7)** every reference to this patch's LOCKED assumption
> range corrected to **ASM-2485..2491** (the seven ASM rows themselves are
> unchanged); the real bring-up gate is now an explicit runner checklist
> (see "Real bring-up gate" below). The patch file changed, so its sha256
> changed (r1 `066565d5…` → r2 `fb5d2f35…`; the r2 patch was regenerated
> from a fresh `git diff --cached` on the pinned KaE tree so its `index`
> post-image hashes match the real applied blobs — payload hunks unchanged,
> superseding the interim r2 file `4ac48e90…` whose index metadata was
> stale); glm.c line anchors below are
> r2 numbering (+10 in `main()` vs r1).

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
| `kot-f1k-dump.patch` | Unified diff **vs the KaE-patched tree** (apply order: colibri@a78a06fc → `kae-add-path.patch` → this). Adds `c/kae_dump.h` + `c/tests/test_kae_dump.c`; edits `c/glm.c` (+123) and `c/Makefile` (1 dep line). **r3 sha256 `e4e04177068d0d8563ecdd24a4bc1f2c25be93a97992c173207ae760f7543887`** (registered in `f1k.json` pins at deploy as an ops amendment, like the KaE patch; supersedes r2 `fb5d2f35…`). |
| `kae_dump.h` | Reference copy of the dump core (accumulator + strict `kaed_parse_int` + capture + finiteness-checked KAED writer; reuses `kae.h` span binding). `real-checks.sh` asserts it is byte-identical to the patch payload. r3 sha256 `485cd497…`. |
| `test_kae_dump.c` | Reference copy of the in-patch unit suite (64 checks; r3 adds Tests G/H/I). r3 sha256 `4ee325c8…`. |
| `mock_glm_dump.c` | MOCK-ONLY tiny engine linking the SAME `kae_dump.h`, with an exact-in-f32, causal, independently re-derivable toy hidden state. |
| `validate.py` | The $0 mock validation battery (V1–V6 below). |
| `real-checks.sh` | The $0 real-source battery: patch applies on the pinned KaE tree, engine builds, unit suites green, objdump per-function inertness. Re-run on Modal at bring-up before any real dump. |
| `validate.log`, `real-checks.log`, `tok-selftest.log` | Measured outputs of the three batteries (2026-07-16, all PASS). |
| `asm-f1k-dump-2485-2491.json` | Companion assumption block ASM-2485..2491 (owner engineer-1), for the coordinator to register with the landing commit. |

The kot-f1k-tok/1 tokenizer wrapper is `../tok_glm52.py` (see below).

## The exact glm.c span touched (patched-file line numbers, r3)

1. **glm.c:39** — `#include "kae_dump.h"` (after `kae.h`).
2. **glm.c:577–582** — file-scope `static KaEDump *g_kdump = NULL;` next to
   `g_kae`. Deliberately **not** a `Model` field (ASM-2486): `sizeof(Model)`
   and `model_init` stay byte-identical (the KaE patch's `model_init` delta
   came from its appended `KaE*` field; this patch has none).
3. **glm.c:1286–1291** — the ONE hook in `moe()` (KaE-tree anchor
   glm.c:1277, shifted to 1284 by hunks 1–2), at its head, on its input:
   `if(g_kdump) kaed_capture(g_kdump, layer, pos_base, S, D, x);`
   READ-ONLY (`const float *x` in `kaed_capture`). `moe()`'s signature is
   unchanged, so `layer_forward` is untouched (unlike the KaE patch).
4. **glm.c:1994–2072** — `run_kae_dump(Model*, const char*)`, placed after
   `run_kae_score` and using its manifest format (`T t_0..t_{T-1}
   s_0..s_{T-1}`, the KAE_SCORE span convention) and its
   one-`layers_forward`-prefill-per-line / `kv_alloc(maxT)` pattern — the
   pattern gate-0 already reviewed. Differences from the scorer: the parse
   is STRICT — every line must be EXACTLY the 2T+1 whitespace-separated
   integers, parsed ONLY via the r3 `kaed_parse_int` (errno/ERANGE
   cleared+checked, every value bounded so the `(int)` cast is exact,
   finding 3), and a wholly non-numeric/garbage line, a bad/overflowing
   T / token id / span slot, trailing junk after the last span, a
   zero-gated line and a manifest READ error (`ferror`, both passes) ALL
   **abort with nonzero exit** instead of being skipped (ASM-2489 +
   PROPOSED-AMEND above — a silently dropped, partially-parsed or
   silently-ungated pass would corrupt the §2.4 means), and nothing is
   printed to stdout (results go only to `KAE_DUMP_OUT`; codex blocker-1
   discipline).
5. **glm.c:2809–2817** — phase-separation guard in `main()` BEFORE model
   load (ASM-2487): `KAE_DUMP` + (`KAE_SCORE` or `KAE=1`) → abort.
6. **glm.c:2888–2902** — arming after `model_init` (geometry known):
   `kaed_arm(KAE_DUMP_LAYERS, KAE_DUMP_OUT, hidden, n_layers)`; NULL →
   **abort** (a construction run must never silently proceed undumped —
   contrast `kae_load`, whose NULL lawfully degrades for scoring); then the
   REQUIRED stderr provenance echo.
7. **glm.c:2939–2945** — dispatch `if(getenv("KAE_DUMP")) run_kae_dump(...)`
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
| `KAE_DUMP` | arms | manifest path; one pass per line `T t_0..t_{T-1} s_0..s_{T-1}` (-1 = ungated); EXACTLY 2T+1 integers per line — garbage lines and trailing junk abort (ASM-2489) |
| `KAE_DUMP_OUT` | yes (when armed) | KAED output: `"KAED" i32 n_lines, nl, D, layer_id[nl]`, then per line `i32 gated_count, f32 sum[nl*D]` (little-endian, ASM-2491) |
| `KAE_DUMP_LAYERS` | yes (when armed) | csv of dump layer ids = the A(iv) candidate splice-layer union (real runs: 3..77; layer 78 = MTP head, unreachable at DRAFT=0 [ASM-2504]); **csv order = slot order** in the file |
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
`gated_count > 0`, **and (r3, finding 4) per line: `gated_count ==` the
manifest's own `span>=0` count (consumer-side ASM-2488 re-check) and
EVERY sum cell finite** — both re-derived harness-side, independent of
the engine's checks — no trailing bytes. Per line it computes
`mean = sum / gated_count` in f64, then the registered §2.4 / §R2
mean-difference + reference-norm arithmetic. `verify --expect-mode real`
re-derives everything cell-by-cell (the #46 integrity guarantee).
Engine-side accumulation is f64 over gated positions in ascending
absolute-position order, cast to f32 at write (ASM-2485) — cell-for-cell
the arithmetic of the repo mock `mock_colibri_dump.py`, so the $0 pipeline
and the real engine share one contract.

## Mock validation — MEASURED results (r3: 2026-07-24, this box, $0)

`python3 validate.py` → **MOCK VALIDATION PASS, 40/40 checks** (`validate.log`):

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
- **V5 fail-closed battery** [MEASURED]: **16/16** abort cases exit nonzero
  (both phase-separation cases, missing OUT/LAYERS, duplicate/out-of-range
  layer, zero-gated line, malformed token, dump layer that never reaches
  `moe()` — the ASM-2488 per-slot count invariant — the two r2 negatives:
  a wholly non-numeric GARBAGE manifest line and TRAILING JUNK after the
  required 2T+1 integers — plus the five r3 finding-3 negatives: span slot
  `2147483648` (the exact int-wrap the re-review proved r2 silently
  UNGATED with exit 0), ERANGE span slot, ERANGE token id, pass-1
  `T=2147483648`, and a manifest READ ERROR via a directory path), plus
  **1 boundary-accept POSITIVE control** (span slot `2147483646` =
  INT_MAX-1 still parses, binds and gates — no over-rejection).
- **V6 unit suite**: `test_kae_dump.c` **64/64** plain and under
  **ASan+UBSan+LSan** (clean, zero diagnostics, zero warnings) — r3 adds
  Test G (9 strict-parse checks incl. ERANGE both signs + the
  `2147483648` reproducer), Test H (NaN-via-capture, Inf-via-capture,
  finite-f64-overflows-f32-cast, clean-control), Test I (/dev/full:
  output failure surfaces nonzero by `kaed_finish` at the latest).

`bash real-checks.sh` (COLIBRI_TREE = pristine base, blob-pinned
`1d74f788`) → **REAL-SOURCE CHECKS OK** (`real-checks.log`, r3): KaE patch
sha verified + applied → dump patch applies cleanly → reference copies
byte-identical to patch payload → `make glm ARCH=x86-64-v3` builds →
`test_kae` **44/44 unchanged** → `test_kae_dump` **64/64** → objdump
inertness: **79 shared functions; only `moe` and `main` differ; none
removed** (same signature as r2; gcc 11.5, the pinned proof basis).

`python3 ../tok_glm52.py --selftest` → **TOK SELFTEST PASS, 10/10**
(`tok-selftest.log`): kot-f1k-tok/1 contract on a constructed tokenizer —
JSONL round-trip, multibyte **char** offsets (é/CJK), template-spec
intersection rule, sha-pin fail-closed on wrong AND absent AND non-hex
pin (r3: `TOK_SHA256` is MANDATORY), malformed-input fail-closed.

`python3 ../build_carriers.py selftest` → **22/22 probes PASS** — r3 adds
probes 4c/4d: a KAED with a NaN sum cell, and a KAED whose `gated_count`
disagrees with the manifest's `span>=0` count, are each REJECTED
consumer-side even though the engine exited 0 with a valid echo
(finding 4's consumer leg); and probe 4e: an UNCORRUPTED dump is ACCEPTED
(positive control — the new checks do not over-reject).

**[STIPULATED] scope limit:** no check above touched GLM-5.2, its weights,
or the real 6144-dim geometry. See the explicit runner checklist below.

## MANDATORY-BEFORE-PAID-CONSTRUCTION measurement gates (RUNNER/executor obligations at bring-up — NOT code-fixable, NOT executed here)

**[STIPULATED]** The gate-0-confirmed additive structure and the toy
re-derivation authorize a **controlled real BRING-UP only — NOT full table
generation**. These four gates need the REAL engine/VM and therefore
remain OUTSTANDING obligations of the executor (experiment-runner role) at
construction bring-up; every one is MEASURED on the real box, any failure
stops the run — fail closed, no retry-to-green. The r3 code hardening does
NOT discharge any of them:

- [ ] **(a) Tiny real dump + FULL-CORPUS tokenizer-vs-engine token-ID
  equality** (re-review finding 6, measurement half): a small real dump (a
  few manifest lines, a small layer subset) completes with the correct
  seed echo, AND the kot-f1k-tok/1 wrapper's token ids are IDENTICAL to
  the ids the real engine (colibri `tok.h` prefill path) produces for
  **EVERY unique construction text** in the pinned
  construction-manifest.jsonl — full corpus, zero mismatches tolerated,
  never a sample (the open half of ASM-2490; a byte- or normalizer-shifted
  tokenization would gate the wrong positions silently). `TOK_SHA256` is
  exported and the wrapper fails closed without it (r3).
- [ ] **(b) Real unarmed BYTE-IDENTITY vs the KaE-only engine —
  FUNCTIONAL, not objdump** (re-review findings 5/8.3): with `KAE_DUMP`
  unset, the dump-patched production binary's output must be
  byte-identical to the KaE-only engine's on the real box, real weights,
  identical inputs, pinned threads. The objdump comparator only BOUNDS
  the blast radius to `{moe, main}` (it exempts `moe`'s numeric body and
  normalizes multi-digit immediates) — it does NOT prove inertness;
  only this functional test does. Re-run the `real-checks.sh` battery
  there too (`test_kae` 44/44 + `test_kae_dump` **64/64** + objdump on
  the production build flags).
- [ ] **(c) Independent MoE-input sum cross-check on MIXED positions**
  (re-review finding 6, second measurement): an INDEPENDENTLY captured
  moe()-input sum (separate instrumentation path, not `kae_dump.h`) over
  at least one construction line with MIXED gated/ungated positions
  matches the engine's dumped sums cell-for-cell after the f32 cast.
- [ ] **(d) Independent rebuild from the pinned Git HEAD** (re-review
  finding 7): rebuild the construction binary from a FRESH clone at the
  pinned base commit `a78a06fc` (verify `git rev-parse HEAD`, not only
  the `glm.c` blob hash) + KaE patch `11f8b458` + THIS r3 patch
  `e4e04177…`, and reproduce the unit counts (44/44 + 64/64) — the $0
  authoring-box build is evidence of coherence, not an independent
  rebuild.

These gates are owned by the executor at bring-up (frozen-run
discipline); the paid construction run itself is SEPARATELY
maintainer-gated and additionally requires the GPT-5.6 re-review of this
r3 patch to PASS first.

## Downstream pin sites (update ONLY at the separately-gated pinning act — deliberately NOT updated here)

The r3 hash/counts invalidate the r2 values embedded in the landed
execution harness. All of these are FAIL-CLOSED against r3 (they refuse,
never silently accept), which is intended: updating them IS the pinning
act and needs the maintainer-gated GO + the passed re-review. At that
point move, as one ops amendment:

- `poc/gcp/f1k_gcp.py` `PINS`: `kot-f1k-dump.patch` → `e4e04177…`,
  `kae_dump.h` → `485cd497…`, `build_carriers.py` → `91baba62…`.
- `poc/gcp/f1k_worker.sh`: `DUMP_PATCH_PIN` (→ `e4e04177…`) and every
  `test_kae_dump: 43/43` expectation (→ `64/64`; grep sites incl. the
  gate-(b) advisory-demotion block and the identity fixture).
- `registry/experiments/f1k.json` harness pins (ops amendment, like the
  KaE patch's).
- Doc tables that quote the r2 sha/counts:
  `poc/gcp/F1K-LAYER-REFREEZE.md`, `poc/gcp/F1K-PIN-FILE-FIX.md`,
  `docs/next/design/f1k-inertness-gate-resolution.md`.

## kot-f1k-tok/1 (`../tok_glm52.py`)

`build_carriers.py`'s `--tokenizer-cmd` is a seam, not an implementation:
the repo's `mock_tokenizer.py` is **mock-only**, so the real construction
DOES need this wrapper (bead xq0h item 3). It wraps the pinned GLM-5.2
`tokenizer.json` (staged with the weights; `TOK_SHA256` pin **MANDATORY
in executable behaviour since r3** — absent/non-hex/mismatched pin ⇒
nonzero exit, no output; ASM-1971 discipline) behind the frozen contract:
stdin JSONL `{"text"}`, stdout JSONL `{"ids","offsets"}`, Python-str char
offsets validated fail-closed (ASM-2490), `add_special_tokens=False`.
r3 sha256 `148db108…`.

## r2 open questions — RESOLVED by the gate-0 re-review (finding 8)

1. **ASM-2485 precision reading** — **ACCEPTED** (finding 2/8.1): f32
   summands, f64 accumulation, f32 emit is the governing arithmetic; the
   reviewer independently re-derived all 192 mock cells bit-exact.
   Non-issue now that the r3 non-finite checks are in.
2. **bringup.sh §5 parser** — was a **real blocker** (finding 8.2);
   **PORTED in r3** (this deliverable): `bringup.sh` step 5 now uses the
   dotted-symbol regex `<([\w.]+)>` + the clone-suffix-aware allowed set
   ([MEASURED] on the r3 build's disassembly: 66 → 82 function labels;
   16 clone symbols were previously swallowed into preceding bodies).
3. **Allowed-diff set `{moe, main}`** — **structurally correct** but it is
   a BLAST-RADIUS bound only, NOT an inertness proof (finding 8.3): the
   comparator exempts `moe`'s numeric body and normalizes immediates.
   The functional gate (b) above is the inertness measurement.
4. **kv-cache reuse across manifest lines** — **acceptable** for the
   current full-prefill-from-position-zero path (finding 8.4); the real
   gate should additionally compare batched vs isolated/reordered lines
   to exclude stale-cache contamination (folded into gate (b)/(c)
   execution notes for the runner).
5. **One image, two binaries** — **DECIDED: two physical binaries**
   (finding 8.5): KaE-only scoring, KaE+dump construction; the landed
   worker already expresses this separation.
