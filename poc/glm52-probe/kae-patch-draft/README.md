# F1-K Kernel-as-Expert (KaE) — ADD-path glm.c patch  [REVISION-1]

> **DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.**
> Pre-built, reviewable patch for **MAINTAINER GATE 0** (the maintainer's
> kernel-of-truth #28; design `docs/next/design/glm52-followup-experiment.md`
> §2.2). The patch is exactly what GATE 0 approves: it lets code write a
> **kernel-derived content vector into GLM-5.2's MoE-block activations** — a
> **Law-1-amendment-gated action**. Drafted for review; **not applied to, nor
> run against, any governed model**; downloads no weights; launches no instance.
> On the maintainer's GO, execution is apply-freeze-run. The patch is **inert
> unless `KAE=1`** (independent byte-equivalence proof below). $0 prep.

**REVISION-1** remediates 3 findings from an independent codex code-review
(ADD-splice correctness + inert-by-default were confirmed OK and are unchanged):

1. **Design-conformance — scoring hook.** The design's §R1.1 candidate-independent
   **single-prefill label-token-logit** scoring path was missing (the draft left
   colibri's continuation-loglikelihood scorer). Now implemented as
   `run_kae_score` (glm.c) + `kae_argmax_label` (kae.h), reached via `KAE_SCORE`.
2. **Request-aware gating.** Spans were a process-global reused from position 0.
   Now **bound per item** (`kae_bind_spans`/`kae_reset_spans`): item N uses item
   N's frozen sidecar; no cross-item reuse.
3. **C-safety.** Checked size products (`kae_szmul`), all allocations checked,
   `realloc`-via-temp, malformed span text rejected, `<stdint.h>` added — every
   rejection is fail-safe (KaE disabled, engine unmodified).

## What this is

The first rung of F1-K (design §1.1, §2.3, §2.5): the **ADD path** — a
training-free lexical concept **gate** that fires on known-concept tokens, and a
**carrier splice** that *adds* a grounded per-concept content-vector into
colibri's MoE output for those tokens, **leaving the native experts intact**;
plus the frozen **§R1.1 scoring** the F1-K arms would run.

Drafted against a fresh, out-of-tree **colibri** checkout, pinned by commit:

```
colibri base commit: a78a06fc5acc4b0dc0f9ef03987c66b0559d1250
splice function:     moe()  (glm.c:1270 in this checkout; call site glm.c:1500)
```

The colibri clone is **not** vendored into this repo (third-party; the base is
referenced by sha only — no upstream org string committed).

## Files

| File | What it is |
|---|---|
| `kae-add-path.patch` | Unified diff vs the pinned colibri commit. Adds `c/kae.h` + `c/tests/test_kae.c`; edits `c/glm.c` (+95/-2: splice, KaE loader wiring, `run_kae_score`, `KAE_SCORE` dispatch) and `c/Makefile` (1 line). |
| `kae.h` | Reference copy: gate + carrier loader + ADD splice + `kae_argmax_label` + per-item span binding (self-contained, no Model dependency). |
| `test_kae.c` | Reference copy of the mock unit tests (44 checks). |
| `build-test.log` | Patched + upstream clean builds; the 88/92 binary-equivalence proof; the 44-check unit run; the ASan+UBSan+LSan run. |
| `asm-kae-patch-2180-2187.json` | Companion assumption block ASM-2180..2190 (owner designer-5), for the coordinator to register with the landing commit. |

## The patch, precisely

**Splice point** (design §2.3). At the tail of `moe()` (FASE E), after the routed
top-8 weighted sum and the shared expert are accumulated into `out` and before
`layer_forward()` adds `out` back into the residual stream:

```c
    if(g_kae && m->kae) kae_apply_add(m->kae, layer, pos_base, S, D, out);
```

`kae_apply_add`: for each row `s` whose absolute position `pos_base+s` is gated
to concept `c` at a splice layer with slot `l`, `out[s] += g * K[c][l]` (ADD;
native experts untouched).

**Gate (G-lex).** Harness-side phrase→concept matching; the engine only reads a
**frozen per-position concept-id sidecar**, and — for the benchmark scoring path
— that sidecar is **bound per item** (`kae_bind_spans`). The gate is a table
lookup (`kae_concept_at`): deterministic, auditable byte-for-byte.

**Scoring (§R1.1, `KAE_SCORE=<manifest>`).** One item per line:
`T K  t_0..t_{T-1}  l_0..l_{K-1}  s_0..s_{T-1}` (template tokens, K answer-label
token ids, per-position spans). Per item: bind the item's spans, ONE prefill,
read next-token logits at the answer cue, `argmax` over the K label-token logits
(published order, tie-break lowest index). Candidate-independent (no per-candidate
forward); runs for **every arm** (KAE=0 baseline included) — only the splice
differs by arm.

**Carrier** (`KAE_CARRIER`), self-describing + dim-checked:

```
[4]="KAEC" | i32 nc | i32 nl | i32 D | i32 layer_id[nl] | f32 K[nc*nl*D]
KAE_SPANS  : ASCII ints, one per token position, -1 = ungated
             (single-request default only; the scoring path binds per item)
```

The loader validates `D == model hidden`, `nl ≤ n_layers`, every layer id in
range, every concept id in range, and rejects malformed span text and any size
overflow — **returning NULL on any failure**, which disables KaE and runs the
unmodified model (never a silent partial arm).

**Env knobs** (all default to inert):

| Var | Default | Meaning |
|---|---|---|
| `KAE` | `0` (unset) | `1` arms the ADD splice; `0`/unset ⇒ byte-identical to upstream |
| `KAE_CARRIER` | — | path to the `KAEC` carrier table (required when `KAE=1`) |
| `KAE_SPANS` | — | optional default sidecar (scoring path binds per item instead) |
| `KAE_SCORE` | — | manifest for the §R1.1 single-prefill label-logit scorer |
| `KAE_G` | `1.0` | blend weight `g` (applied after carrier norm) |
| `KAE_MODE` | `0` | `0`=ADD (implemented); `1`=REPLACE (documented no-op stub) |

## Inert-by-default: independent byte-equivalence proof

With `KAE` unset the only code the patch runs is two NULL-returning `getenv`s
(`g_kae=0`, `g_kae_g=1.0`), `m.kae=NULL`, and the `if(g_kae && m->kae)` guard in
`moe()` evaluating **false** every layer. **No computed activation changes.**

Independent machine-level check (in `build-test.log §3`, reproducible): pristine
and patched `glm.c` are compiled to objects, disassembled, address-normalized,
and compared **per function** — **88 of 92 shared functions are byte-identical**.
The only functions that changed are the ones the patch wires (`moe`,
`layer_forward`, `main`) plus `model_init`, whose **sole** delta is the
`sizeof(Model)` immediate `0x6278→0x6280` (the appended 8-byte `KaE*` field; no
logic change — the field is only *appended*, so every pre-existing offset is
preserved). Corroborated at unit level (Test C: `memcmp==0` for non-splice
layer, REPLACE mode, `g_kae==0` guard, and every ungated row).

## Mock unit tests (mechanics only — NOT a feasibility result)

`test_kae.c` links the **same `kae.h`** the engine links; synthetic tiny setup
(3 concepts, `D=4`, splice layers `{3,7}`); **no model/weights/instance.**
**44 checks, ALL PASSED**, and a clean **AddressSanitizer + UBSan + LeakSanitizer**
run (exit 0, no diagnostics):

- **A. gate** fires on the right tokens/layers.
- **B. carrier** adds `g*K[c][l]` at gated rows only; per-layer table distinct;
  `pos_base` honoured.
- **C. inert-by-default** (unit companion to the binary proof above).
- **D. candidate-independent scoring** — `kae_argmax_label` picks the max-logit
  label; is deterministic; depends **only** on the k label logits (perturbing
  non-label logits doesn't change it); tie-break = lowest index; invariant to any
  candidate context (no candidate parameter).
- **E. loader fail-safe** — missing carrier, dim mismatch, out-of-range layer,
  bad magic, out-of-range span id, non-integer span text all → NULL; carrier-only
  load (spans per item) is valid.
- **F. request-aware span binding** — item B's spans replace item A's; a shorter
  item shows no stale tail; out-of-range concept id rejected (spans left empty).

Reproduce (from the pinned colibri checkout, `c/`):

```
make glm ARCH=x86-64-v3
gcc -O2 -Wall -Wextra -Wno-unused-function -o test_kae tests/test_kae.c -lm && ./test_kae
```

## Out of scope for this draft (documented, deferred by the design)

- **REPLACE path** (§2.5): deferred behind a K-1 pass + its NI power gate
  (REVISION-4 §R-REV4.3); a no-op stub (`kae_replace_note`; `KAE_MODE=1` inert).
- **Hidden-state dump mode** (§2.4/§2.8) for carrier construction — harness-side.
- **G-emb** cosine gate variant (§2.3) — budget-permitting, a later rung.

## What GATE 0 is being asked to approve

1. the scoped **Law-1 amendment** (kernel-derived content vectors may enter model
   activations only within the KaE track, only via this registered splice, with
   the §2.6 deflator ladder mandatory); and
2. **this glm.c patch** (it exceeds the P0 trace-dump C envelope, ASM-1986/1989,
   so it rides GATE 0; fork etiquette per ASM-1989).

No feasibility conclusion is stated here. The F1-K accuracy ladder
(K-1/K-2/K-3), its deflator arms, the freeze manifest, and the $550-ceiling run
are separate, maintainer-gated steps that fire only on GO.
