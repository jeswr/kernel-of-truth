# F1-K Kernel-as-Expert (KaE) — ADD-path glm.c patch

> **DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.**
> This directory holds a pre-built, reviewable patch for **MAINTAINER GATE 0**
> (the maintainer/kernel-of-truth #28; design `docs/next/design/glm52-followup-experiment.md`
> §2.2). The patch is exactly what GATE 0 approves: it lets code write a
> **kernel-derived content vector into GLM-5.2's MoE-block activations** — a
> **Law-1-amendment-gated action**. It is drafted here for review; it was **not
> applied to, nor run against, any governed model**, it downloads no weights, and
> it launches no instance. On the maintainer's GO, execution is apply-freeze-run.
> The patch is **inert unless `KAE=1`** (see the inert-by-default proof below).

## What this is

The first rung of F1-K (design §1.1, §2.3, §2.5): the **ADD path** — a
training-free lexical concept **gate** that fires on known-concept tokens, and a
**carrier splice** that *adds* a grounded per-concept content-vector into
colibri's MoE output for those tokens, **leaving the native experts fully
intact** (pure quality intervention, no expert removed).

It is drafted against a fresh, out-of-tree **colibri** checkout, pinned by commit:

```
colibri base commit: a78a06fc5acc4b0dc0f9ef03987c66b0559d1250
splice function:     moe()  (glm.c:1270 in this checkout; call site glm.c:1500)
```

The colibri clone is **not** vendored into this repo (third-party; account-lint
forbids committing the upstream org string — the base is referenced by sha only).

## Files

| File | What it is |
|---|---|
| `kae-add-path.patch` | Unified diff vs the pinned colibri commit (git-style `a/` `b/` paths under `c/`). Adds `c/kae.h` + `c/tests/test_kae.c`, edits `c/glm.c` (+32/-3) and `c/Makefile` (1 line). |
| `kae.h` | Reference copy of the new header: the gate + carrier loader + ADD splice (self-contained, no Model dependency). |
| `test_kae.c` | Reference copy of the mock unit tests (30 checks). |
| `build-test.log` | Compile log (patched engine builds warning-clean with the same make target; upstream baseline builds too) + full unit-test run (ALL PASSED). |
| `asm-kae-patch-2180-2187.json` | Companion assumption block ASM-2180..2187 (owner designer-5), for the coordinator to register with the landing commit. |

## The patch, precisely

**Splice point** (design §2.3). Inside `moe()`, at the tail (FASE E), *after* the
routed top-8 weighted sum and the shared expert are accumulated into `out` and
*before* `layer_forward()` adds `out` back into the residual stream:

```c
    /* out now holds routed-sum + shared-expert (native MoE output) */
    if(g_kae && m->kae) kae_apply_add(m->kae, layer, pos_base, S, D, out);
```

`kae_apply_add` does, for each batch row `s` whose absolute position
`pos_base+s` is gated to concept `c`, at a splice layer with carrier slot `l`:

```
out[s] += g * K[c][l]     (ADD; native experts untouched)
```

**Gate (G-lex).** The phrase→concept matching is harness-side; the engine only
reads a **frozen per-position concept-id sidecar** (`KAE_SPANS`). The gate is a
table lookup (`kae_concept_at`) — zero learned components, deterministic,
auditable byte-for-byte.

**Carrier.** A binary sidecar (`KAE_CARRIER`), self-describing and dim-checked:

```
[4]="KAEC" | i32 nc | i32 nl | i32 D | i32 layer_id[nl] | f32 K[nc*nl*D]
KAE_SPANS  : ASCII, one int per token position (index = absolute position), -1 = ungated
```

The loader validates `D == model hidden` and every splice layer id in
`[0, n_layers)`, and **returns NULL on any malformed input**; the engine then
**disables KaE and runs the unmodified model** (never a silent partial arm).

**Env knobs** (all default to inert):

| Var | Default | Meaning |
|---|---|---|
| `KAE` | `0` (unset) | `1` arms the ADD splice; `0`/unset ⇒ byte-identical to upstream |
| `KAE_CARRIER` | — | path to the `KAEC` carrier table |
| `KAE_SPANS` | — | path to the frozen per-position concept-id sidecar |
| `KAE_G` | `1.0` | blend weight `g` (applied after carrier norm) |
| `KAE_MODE` | `0` | `0`=ADD (implemented); `1`=REPLACE (documented no-op stub) |

## Inert-by-default proof (the gate-0 safety claim)

With `KAE` unset, the ONLY code the patch executes is: two `getenv` calls that
return NULL (leaving `g_kae=0`, `g_kae_g=1.0`), `m.kae=NULL`, and the guard
`if(g_kae && m->kae)` in `moe()` evaluating **false** at every layer. **No
computed activation changes; the decoded token ids are byte-identical to
upstream.** Every functional insertion in the diff is behind `g_kae` (default 0)
or `m->kae` (NULL unless a valid carrier loaded). The added `pos_base` parameter
to `moe()` is consumed only inside the guarded splice.

This is corroborated mechanically by the unit tests (Test C): a non-splice
layer, `KAE_MODE=1` (REPLACE stub), the `g_kae==0` guard, and every ungated row
all leave the output buffer **bit-for-bit unchanged** (`memcmp == 0`); an enabled
splice perturbs **exactly** the gated rows and nothing else.

## Mock unit tests (mechanics only — NOT a feasibility result)

`test_kae.c` links the **same `kae.h`** the engine links and runs on a synthetic
tiny setup (3 concepts, `D=4`, splice layers `{3,7}`) — **no model, no weights,
no instance.** 30 checks, ALL PASSED:

- **A. gate fires on the right tokens/layers** — `kae_concept_at` returns the
  frozen concept id per position (and −1 out of range); `kae_slot_of_layer`
  identifies splice layers only.
- **B. carrier adds correctly** — `out += g*K[c][l]` at gated rows only; the
  per-layer table is distinct (slot 0 vs slot 1); `pos_base` shifts gating by
  absolute position.
- **C. inert-by-default** — no-op whenever the splice must not fire (see proof
  above); enabled splice touches exactly the gated rows.
- **D. candidate-independent** — the gate/splice take **no** candidate/option/
  label argument; identical spans+carrier ⇒ byte-identical activations; the
  readout-row delta is `g*K[c][l]` with no label term (design §R1.1).
- **E. loader fail-safe** — 6 malformed-input cases (missing path, dim mismatch,
  out-of-range layer, bad magic, out-of-range span id) all return NULL.

Reproduce (from the pinned colibri checkout, `c/`):

```
make glm ARCH=x86-64-v3                                   # patched engine, same target
gcc -O2 -Wall -Wextra -Wno-unused-function -o test_kae tests/test_kae.c -lm
./test_kae
```

## Out of scope for this draft (documented, deferred by the design)

- **REPLACE path** (§2.5): admitted only after ADD passes K-1 and its own
  non-inferiority power gate (REVISION-4 §R-REV4.3). Present as a no-op stub
  (`kae_replace_note`; `KAE_MODE=1` makes the ADD splice inert). REPLACE needs
  `moe()`'s expert loop to expose per-token dropped-weight bookkeeping — not
  wired for gate 0.
- **Hidden-state dump mode** (§2.4/§2.8) for carrier *construction* — harness-side.
- **G-emb** cosine gate variant (§2.3) — budget-permitting, a later rung.

## What GATE 0 is being asked to approve

1. the scoped **Law-1 amendment** (kernel-derived content vectors may enter model
   activations only within the KaE track, only via this registered splice, with
   the §2.6 deflator ladder mandatory); and
2. **this ~200-line glm.c patch** (it exceeds the P0 trace-dump C envelope,
   ASM-1986/1989, so it rides GATE 0; fork etiquette per ASM-1989).

No feasibility conclusion is stated here. The F1-K accuracy ladder
(K-1/K-2/K-3), its deflator arms, the freeze manifest, and the $550-ceiling run
are all separate, maintainer-gated steps that fire only on GO.
