# d-xif — the P10 held-out labelled extraction set + IF-1 fork pilot record

**What this is** (P10, `docs/research-plan/10-model-record-interface.md` §§3–4; consumed by
the F2 final phase and, per P10, the same interface governs E9): ≥300 **real model outputs
per rung** — here 500 kernel-covered + 150 control outputs per rung — from the pinned
SmolLM2-Instruct models (R1 135M `12fd25f7…`, R2 360M `a10cc151…`) over the pinned d-qa
items, with the model→record extraction step labelled **mechanically** (no LLM, no human in
the labelling loop), plus the pre-registered **IF-1 fork pilot** measurement
(constrained-format tax + IF-A extraction fidelity, n = 200 per rung).

Built 2026-07-08 by a single Modal A10G run (`poc/modal/modal_f2_xif.py`, run stamp
`20260708-190006-modal-xif`, provenance sidecar copied here) — **before any F2 final-phase
run** (operational DAG: `d-xif ≺ f2.iface ≺ f2.run`). Per output, TWO decodes from the
IDENTICAL shared-affordance prompt (P10 §5 frames, pinned in `poc/f2/inputs/f2-manifest.json`):

1. **IF-C** (the deployed default surface): constrained selection over the pinned option set
   by sequence logprob — the harness's own `HFLM.choose`, greedy — then extraction into a
   kernel-checkable record via the harness's own `extract_record` + `KernelVerifier`
   (per-item `record_sha256` pin, fail closed). SUCCESS = a well-formed record was produced
   AND the deterministic verifier could decide it (covered items).
2. **Unconstrained**: greedy free decode (max 24 new tokens), then the strict deterministic
   IF-A parser **IFA-PARSE/1** and the lenient mechanical reference annotation **GOLD-ANN/1**
   (both pinned in `builder/xif_runner.py`).

## The measured numbers (recomputed fail-closed by `build-dxif.py`; see `gate.json`, `if1-fork.json`)

| | R1 (135M) | R2 (360M) |
|---|---|---|
| extraction failures (IF-C, gate) | **0 / 500** | **0 / 500** |
| failure rate Wilson-LB (one-sided 95%, z=1.645) | 0.0000 | 0.0000 |
| extraction errors (well-formed-but-wrong, round-trip) | 0 | 0 |
| **P10 instrument gate (LB ≤ 0.10)** | **PASS** | **PASS** |
| IF-1: acc constrained (IF-C) | 0.360 | 0.415 |
| IF-1: acc unconstrained (GOLD-ANN/1-graded) | 0.350 | 0.115 |
| IF-1: format-tax h (− = constraint HELPS) | −0.021 [−0.116, 0.074] | −0.708 [−0.877, −0.545] |
| IF-A strict-parse yield (free decode) | 315/500 | 216/500 |
| IF-A F1 vs GOLD-ANN/1 | 0.824 | 0.919 |
| **IF-1 fork** (needs tax h-LB ≥ 0.2 AND F1 ≥ 0.95) | not fired | not fired |

**IF-1 fork decision: IF-C STANDS** (the pre-declared default is confirmed at both rungs;
neither condition fires at either rung).

## Honest reading (do not over-claim)

- The **0/500 failure rate is partly a property of the IF-C surface itself**: constrained
  selection over a pinned option set cannot emit an out-of-format answer, so residual failure
  modes are structural (malformed items, record-pin mismatches, unresolvable term labels) —
  all measured here as absent over the full pinned item set at both rungs. That is exactly
  what P10 chose IF-C **for**; the gate certifies the deployed instrument, it does not claim
  free-text extraction is solved.
- The free-decode columns show what the alternative would cost: under IF-A, 37–57% of raw
  outputs surrender **no** record to the strict parser, and at R2 the model's unconstrained
  accuracy collapses (0.115 vs 0.415 constrained) — free decode from these raw-completion
  prompts mostly produces continuations, not answers. The "format tax" is strongly negative
  (the constraint HELPS), the opposite of the fork's firing direction.
- **GOLD-ANN/1 is a mechanical reference annotation**, not human gold (P10 §4 envisioned
  gold-record annotation; this is its no-human-in-the-loop pilot instantiation — adequate for
  the failure-rate gate, which needs no gold at all, and for the fork, which did not fire).
  Had the fork condition fired on the F1 number, human audit of the annotation would have
  been required before adopting IF-A. It did not fire.
- Outputs here are **instrument-ledger data only**: never scored as kernel successes or
  failures, never entering any hypothesis endpoint (P10 §4 no-free-wins/losses rule).
  "Held-out" per P10: generated greedily, pre-final-phase, disjoint from the readout
  outputs of the frozen seed set.

## Files

| Path | What |
|---|---|
| `outputs/r1.jsonl`, `outputs/r2.jsonl` | one line per output: both decodes, all mechanical labels (650 lines each) |
| `gate.json` | per-rung P10 gate arithmetic, RE-DERIVED from the outputs by `build-dxif.py` (fail-closed vs the runner summary) |
| `if1-fork.json` | IF-1 pilot statistics + the fork decision, re-derived the same way |
| `results-xif.json` | the runner's own summary (byte copy from the run) |
| `provenance-modal.json`, `run-log.txt` | Modal provenance sidecar + full run log (byte copies) |
| `builder/xif_runner.py` | the pilot runner (imports the FROZEN harness machinery from `poc/f2/runner/f2_runner.py` so the measured instrument is the deployed one) |
| `builder/modal_f2_xif.py`, `builder/build-dxif.py` | the Modal wrapper + this corpus's assembly script (byte copies; d-qa/d-ext discipline: builders inside the hashed bytes) |
| `manifest.json` | kot-dxif/1 manifest: per-file sha256s, model pins, constants, source run stamp |

**Reproduce the labels**: `python3 data/d-xif/build-dxif.py --from poc/f2/results-incoming/20260708-190006-modal-xif`
re-derives every parse flag from the stored `gen_text` and every gate/fork number from the
per-output records, failing closed on any mismatch. (The raw model outputs themselves are the
one non-reproducible-by-construction input — they are GPU inference outputs, pinned here by
bytes + provenance.)
