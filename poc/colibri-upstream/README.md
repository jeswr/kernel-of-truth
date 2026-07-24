# colibri upstream — maintainer-review handoff

**Status: PREPARED, HELD LOCALLY. Nothing has been pushed, forked, branched, or opened.**
Two contributions to `github.com/JustVugg/colibri`, prepared as apply-clean patches
against the current default branch. Review the patches + PR descriptions below; a
one-line "go" opens them (exact `gh`/`git` commands are in the last section — **do not
run them until you approve**).

Source of the recommendation: `reports/novelty-assessment-2026-07-24.md` identified exactly
two upstreamable items — (1) the per-expert causal-ablation harness `abl.h`, (2) a stale
`docs/api.md` tools sentence. Everything else in the programme is internal-only or unpublishable.

| # | PR | Files | Kind | Validation |
|---|----|-------|------|------------|
| 1 | Per-expert causal-ablation harness (`ABLATE_SCORE`) | `c/abl.h` (new), `c/colibri.c`, `c/Makefile`, `c/tests/test_ablate.c` (new) | Feature (opt-in research instrument) | Builds clean `-Wall -Wextra`; unit gate 18/18; inert when off |
| 2 | Docs: OpenAI path DOES support tool-calling | `docs/api.md` | One-paragraph doc fix | grep-verified against `c/openai_server.py` |

Patch files in this dir:
- `01-abl-harness.patch` — item 1 (440 insertions across 4 files)
- `02-api-md-tools-fix.patch` — item 2 (6 insertions / 4 deletions, 1 file)

Both were generated against, and `git apply --check`'d clean against, a **pristine checkout of
colibri HEAD `81f08a09e5651ce52616dc720f68810f9021c0be`** (2026-07-24). They touch disjoint
files, so order does not matter and they can be one PR or two (recommended: **two** — the doc
fix is trivial and should not wait on review of the feature).

---

## Provenance / adaptation note (important)

The harness was originally written (2026-07-15) against colibri's old `c/glm.c`. Since then the
**#391 refactor renamed `glm.c` → `colibri.c`** and heavily restructured `moe()`'s expert-compute
path (block-of-64, Metal/CUDA/CPU splits). **This handoff is a fresh re-port of the harness against
current `colibri.c`**, not the stale glm.c patch. What changed in the port, and what I had to
assume about colibri's current API, is documented under "Assumptions" in the item-1 section.

Epistemic tags: `[MEASURED-from-source]` = read/tested against colibri HEAD `81f08a0`;
`[ASSUMED]` = design choice or expectation not exhaustively proven.

---

## PR 1 — Per-expert causal-ablation harness for `moe()` (`ABLATE_SCORE`)

**Suggested title:** `Add opt-in per-expert causal-ablation harness (ABLATE_SCORE) for moe()`

**Branch:** `causal-ablation-harness`

### What it adds

An **off-by-default research instrument** that measures the *causal* effect of individual
experts on the model's real output, complementing the routing-affinity **Expert Atlas** (#175):
the Atlas shows what routes *where*; this shows what an expert actually *does*.

- **`c/abl.h`** (new, ~100 lines, self-contained, zero deps): a per-item ablation config with
  three modes and a fail-closed per-item reset (`abl_reset` → OFF; `abl_set_item`; the three
  predicate helpers). Holds no cross-item state.
- **`c/colibri.c`**: four small guarded insertions —
  1. `#include "abl.h"` next to `grammar.h`; `static Abl g_abl = {0};` next to `g_topk`/`g_topp`.
  2. **FASE A** (right after the TOPP block, before the eusage counters + `norm_topk`):
     - *mode 2 route-around* — drop the ablated cell from the selected set so survivors
       renormalise (mirrors an `EXPERT_BUDGET`-style per-token drop of a chosen expert);
     - *mode 3 module-swap* — remap the slot's expert id to a substitute, keeping the routed weight.
     Both act **before** counters / `norm_topk` / `routed_scale` / `ROUTE_TRACE`, so all downstream
     accounting reflects the post-ablation routing.
  3. **FASE C** (CPU accumulate, right after `if(!nr) continue;`):
     - *mode 1 contribution* — routing/counters/trace unchanged; skip this expert's
       `matmul`+accumulate so its weighted output is zero.
  4. `run_ablate_score()` — a teacher-forced path reached via `ABLATE_SCORE=<manifest>` that,
     per item, resets `g_abl`, configures the ablated `(layer,expert)` cells, runs **one** prefill
     (so `moe()` applies the ablation), and reads out the **final logits** at every target position
     to `ABLATE_OUT=<file>` (JSONL, schema `coli-ablate/1`: exact per-token NLL, gold-vs-best
     logit margin, argmax correctness, plus a top-32 for an approximate next-token KL). Dispatched
     just before `SCORE`. If `ROUTE_TRACE=<file>` is also set, the existing tracer dumps the
     **post-ablation** routing for free.
- **`c/Makefile`**: `abl.h` added to the `colibri` prerequisite list; a standalone
  `tests/test_ablate` target added to `TEST_BINS`.
- **`c/tests/test_ablate.c`** (new): a no-model unit gate that drives a faithful miniature of
  `moe()`'s routing+accumulate against the **same** `abl.h` the engine links, asserting the
  inertness + semantics properties (below).

### Motivation

colibri already reasons about which experts matter — `EXPERT_BUDGET` (#254, quarantined behind
`EXPERT_BUDGET_EXPERIMENTAL=1` after an empty operating window), the Expert Atlas (#175, routing
affinity only, "no engine changes needed"), `CACHE_ROUTE`. What's missing is a **causal**
instrument: a way to ask "if this specific expert is dropped / zeroed / substituted for *this*
token, how do the final logits move?" That is exactly the evidence needed to tell a
*safe-to-drop* expert from a *load-bearing* one — i.e. to give expert-pruning/budgeting an
empirical basis rather than a blind gate-weight cap. The harness is small, contained, and does
nothing unless a run explicitly opts in.

### How it's tested `[MEASURED-from-source]`

Built and run on this box against pristine colibri HEAD `81f08a0`:
- **Full CPU build** `make colibri` — compiles clean under the project's own
  `-O3 -march=native -Wall -Wextra` flags (0 warnings from the patch). `ABLATE_SCORE`/`ABLATE_OUT`/
  `coli-ablate/1` confirmed present in the resulting binary.
- **`make tests/test_ablate` → ALL PASS (18/18)**. The gate proves:
  - **P1** mode 0 output is byte-identical to the un-hooked reference (inert when off);
  - **P2** ablating an *unused* (this token doesn't select it) cell is a no-op, in all 3 modes,
    and the `(layer,expert)` key is respected;
  - **P3** `abl_reset()` restores OFF and no spec leaks into the next item;
  - **S1/S2/S3** each mode has exactly its intended arithmetic (contribution removes just that
    term; route-around drops the expert and renormalises survivors to `routed_scale`;
    module-swap substitutes at the same weight).
- Recommend adding `tests/test_ablate` to `make test` (done via `TEST_BINS`) so the inertness
  guarantee is a permanent CI gate.

### Caveats / scope (state these in the PR)

- **Inert by default `[MEASURED-from-source]`.** All hooks are guarded by `g_abl.mode`, which is
  only ever set on the `ABLATE_SCORE` path. With `ABLATE_SCORE` unset the forward is unchanged.
- **mode 1 (contribution) is CPU-path only `[MEASURED-from-source]`.** The zero-contribution skip
  lives in the CPU expert loop; under `COLI_CUDA`/`COLI_METAL` an expert may compute on the GPU
  before that skip. This matches how the harness is meant to run (deterministic CPU forward, atlas
  discipline). Modes 2 and 3 edit the selected set in FASE A and are therefore backend-agnostic.
  *If you'd prefer mode 1 to be backend-agnostic too, an alternative is to zero `ws[]` for the
  ablated cell right after `routed_scale` — one line, all backends honour it — at the cost of the
  route trace then showing weight 0 for that cell. Flagged for your call.* `[ASSUMED]`
- **Research instrument, not a hot-path feature.** Teacher-forced, one prefill per item, final-logit
  read-out; not wired into serve/generate. No claim about pruning is bundled — the harness produces
  the evidence, it doesn't act on it.
- **Prior art (full disclosure, from the novelty assessment).** Per-expert causal MoE ablation via
  router-masking + gate renormalisation is a published *method* (e.g. arXiv:2606.25092, on a
  comparable frontier MoE, with released tooling). The upstreamable value here is a clean,
  engine-native, inert-by-default **implementation for colibri specifically** — no per-expert causal
  instrument exists in the repo today (checked #175, #254). Worth stating plainly so the maintainer
  isn't sold novelty it doesn't have.

### Assumptions about colibri's current API surface

- `[MEASURED-from-source]` `moe()` signature at HEAD is
  `static void moe(Model*, Layer*, int layer, float*x, int S, float*out, int with_shared)`; the
  plain top-K selection, `TOPP` shrink, `norm_topk`, `routed_scale`, and the `ROUTE_TRACE`
  (`g_route_fp`) emit are all in the per-position FASE-A loop — the insertion point used.
- `[MEASURED-from-source]` `run_ablate_score()` reuses only long-standing engine helpers that
  `run_score()` uses: `kv_alloc`, `falloc`, `embed_row`, `layers_forward(m,x,T,0)`,
  `rmsnorm(...,m->final_norm,...)`, `matmul_qt(lo,row,&m->lm_head,1)`, `now_s`, `rss_gb`. No new
  dependency; **it does NOT use the programme's private `rtrace.h`** (colibri's built-in
  `ROUTE_TRACE` covers tracing).
- `[ASSUMED]` The manifest tokens are pre-tokenised by the host including any GLM `[gMASK]<sop>`
  prefix (mirrors the eval harness); `run_ablate_score` deliberately does no prefix injection so
  the teacher-forced sequence is exactly what the host specifies.
- `[ASSUMED]` If the maintainer later drops `colibri.c` line stability, the anchors are symbolic
  (`moe`, the TOPP block, `if(!nr) continue;`, the `SCORE` dispatch) and easy to re-locate.

---

## PR 2 — Docs: the OpenAI path supports tool-calling

**Suggested title:** `docs(api): OpenAI server supports tool-calling (correct stale "returns an error" note)`

**Branch:** `docs-api-tools`

### What / motivation `[MEASURED-from-source]`

`docs/api.md` (OpenAI `coli serve` section) currently says:

> "Tools, image/audio input, custom stop sequences, log probabilities, and token penalties return
> an explicit error rather than being silently ignored."

This is stale for **Tools**: `c/openai_server.py` at HEAD ships full tool-calling —
`parse_tool_calls()` (renders GLM tool markers back into OpenAI `tool_calls`),
`render_chat(..., tools, tool_choice)` (injects the `<tools>` XML and honours
`tool_choice` incl. `none`/`required`/forced-function), and there's a dedicated
`test_openai_tools_e2e.py`. Tool schemas only 400 when *malformed*. (Landed via #401/#408.) The
Anthropic section of the same doc already documents full tools support, so the OpenAI paragraph
contradicts both the code and its sibling section. The other items in the sentence
(image/audio, custom stop sequences, logprobs, token penalties) are left unchanged.

### The diff (full)

```diff
--- a/docs/api.md
+++ b/docs/api.md
@@ -30,10 +30,12 @@ completion requests support JSON responses, SSE streaming, usage counts,
 
 The server is deliberately text-only and serves one generation at a time: the
 744B model stays in one persistent process, so concurrent HTTP requests queue
-instead of loading duplicate model copies. Tools, image/audio input, custom
-stop sequences, log probabilities, and token penalties return an explicit error
-rather than being silently ignored. The default bind address is localhost; set
-`COLI_API_KEY` before exposing the server beyond the machine.
+instead of loading duplicate model copies. Tool-calling **is** supported on this
+path — pass OpenAI `tools` and (optionally) `tool_choice`, mirroring the
+Anthropic endpoint below. Image/audio input, custom stop sequences, log
+probabilities, and token penalties return an explicit error rather than being
+silently ignored. The default bind address is localhost; set `COLI_API_KEY`
+before exposing the server beyond the machine.
```

---

## Exact commands that WOULD open these — DO NOT RUN until approved

These assume `gh` is authed and a fork of `JustVugg/colibri` under your account. Replace
`YOURFORK` with your fork's remote if it differs. Each PR is opened separately (recommended).
Nothing below has been run.

```bash
# 0. one-time: fork + clone (skip if you already have a fork checkout)
gh repo fork JustVugg/colibri --clone=true --remote=true
cd colibri
git fetch origin
PATCHDIR=/home/ec2-user/css/kernel/kernel-of-truth/poc/colibri-upstream

# ---- PR 2 (doc fix) — trivial, open first ----
git checkout -b docs-api-tools origin/main         # or origin/HEAD default branch
git apply "$PATCHDIR/02-api-md-tools-fix.patch"
git add docs/api.md
git commit -m "docs(api): OpenAI server supports tool-calling

The OpenAI coli serve section said tools 'return an explicit error'; the
server ships full tool-calling (parse_tool_calls / render_chat tool_choice,
test_openai_tools_e2e.py, #401/#408). Correct the stale sentence; leave the
image/audio/stop/logprob/penalty items unchanged."
git push -u YOURFORK docs-api-tools
gh pr create --repo JustVugg/colibri --base main --head YOURFORK:docs-api-tools \
  --title "docs(api): OpenAI server supports tool-calling" \
  --body-file -   # paste the PR-2 "What / motivation" section

# ---- PR 1 (ablation harness) ----
git checkout main && git checkout -b causal-ablation-harness origin/main
git apply "$PATCHDIR/01-abl-harness.patch"
git add c/abl.h c/tests/test_ablate.c c/colibri.c c/Makefile
git commit -m "Add opt-in per-expert causal-ablation harness (ABLATE_SCORE) for moe()

Off-by-default research instrument: ABLATE_SCORE=<manifest> runs a teacher-forced
prefill per item with a chosen (layer,expert) cell ablated in one of three modes
(contribution-zero / route-around / module-swap) and reads out the final logits
(ABLATE_OUT). Inert unless enabled (guarded by g_abl.mode); standalone unit gate
tests/test_ablate proves inertness + per-mode semantics (18/18). Causal complement
to the Expert Atlas (#175)."
# sanity before pushing:  make colibri && make tests/test_ablate && ./c/tests/test_ablate
git push -u YOURFORK causal-ablation-harness
gh pr create --repo JustVugg/colibri --base main --head YOURFORK:causal-ablation-harness \
  --title "Add opt-in per-expert causal-ablation harness (ABLATE_SCORE) for moe()" \
  --body-file -   # paste the PR-1 "What it adds" + "Motivation" + "Caveats" sections
```

### Optional PR footer (per programme convention)

> Prepared for review; expect a delay before active review. Happy to adjust scope — in particular
> whether mode-1 contribution ablation should be made backend-agnostic (see the caveat), and
> whether you'd like `tests/test_ablate` in the default `make test` gate (it is, via `TEST_BINS`).

---

## Reproduce the validation locally

```bash
# fresh pristine checkout + apply + build + test
git clone --depth 1 https://github.com/JustVugg/colibri /tmp/colibri-check
cd /tmp/colibri-check
git apply /home/ec2-user/css/kernel/kernel-of-truth/poc/colibri-upstream/01-abl-harness.patch
git apply /home/ec2-user/css/kernel/kernel-of-truth/poc/colibri-upstream/02-api-md-tools-fix.patch
cd c && make colibri && make tests/test_ablate && ./tests/test_ablate
```

Expected: `colibri` builds clean; `test_ablate` prints `ALL PASS (0 failures)`.
Verified here against HEAD `81f08a09e5651ce52616dc720f68810f9021c0be` (2026-07-24).
