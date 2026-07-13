# ufo-check-0 (INSTRUMENT-INVALID via token-parity) — interpretation

> **Provenance (coordinator, 2026-07-13).** The mechanical verdict is established separately: the
> chain-verified pipeline (`collect_to_log.py` → `log-append` [30 records] → pinned stdin adapter
> `analysis/ufo_check_0_stdin.py` → `verdict-gen`) fired `verdict_rules` rule 0 → **INSTRUMENT-INVALID**,
> the sole failed instrument gate being **token-parity** (`registry/verdicts/ufo-check-0.json`,
> `reports/auto/ufo-check-0/analysis-output.json`; commit `8309fffc`). Interpretation below authored by
> **GPT-5.6 (xhigh)** standing in for Fable (capped) — **PROVISIONAL-ON-LLM-PROXY**, to be reconciled
> against an independent Fable read (dual-model); material divergence triggers a re-do. The coordinator
> does NOT author the feasibility conclusion. Claims tagged MEASURED / PRE-SPECIFIED (frozen design) /
> INTERPRETATION.

## 1. Meaning of the failed gate

**[MEASURED]** The mechanical verdict is **INSTRUMENT-INVALID** because rule 0 fired; token parity was the sole failed instrument gate. The primary lower bound was 0.0, s1–s4 were false, s5 true, but none is verdict-bearing after that gate failure.

**[PRE-SPECIFIED]** The design's token-parity gate (`docs/next/design/ufo-check-0.md`) required each checker control's mean rejection-message length within ±20% of AU under the pinned SmolLM2 tokenizer, both before freeze and at runtime — the rejection message being the only arm-varying surface, so length matching is a validity precondition.

**[INTERPRETATION]** Without realized token parity, checker content is bundled with unequal context length, token budget, and potentially different retry behavior, so an AU lift/no-lift cannot be cleanly attributed to the checker's modal/identity/rigidity structure rather than token exposure. The observed zero primary lift carries no evidential weight for H-U1.

**[MEASURED]** Not a degenerate-frame failure. Fixture determinism, headroom, AU engagement, extraction, completeness, representation matching, AN non-degeneracy, AD coincidence, and message discipline all passed. AU rejected and retried on 33.3% of scored rows, so the checker entered the verify-retry loop and the host produced retries.

**[INTERPRETATION]** "Engagement" here = operational invocation, not the H-U1 sense of beneficially using the checker's signal. The passed mechanics rule out "host ignored the seam" and "frame collapsed"; they do not establish causal checker use.

## 2. Repairability

**[MEASURED]** Pre-freeze templates were length-matched (AG/AU, AD/AU, AN/AU ≈ 0.915, 0.937, 0.915). At runtime AD/AU = 1.008 and AN/AU = 0.810 (both in band), but **AG/AU was undefined because AG rejected no scored items**.

**[INTERPRETATION]** That points first to a mismatch between template-level parity and realized exposure, not an intrinsic UFO-construct defect. A token-matched `ufo-check-1` with a neutral padding/length-control arm (analogous to knull's plain-padded) is the natural repair.

**[INTERPRETATION]** Cheapest diagnostic (no GPU): a realized-exposure audit over the frozen rows + accept tables — per-item retry-context tokens, rejection incidence, and post-first-pass token distributions, including zero-rejection cells. If exact neutral matching is mechanically constructible, run a small blocking pilot at the operating point to verify the padded control stays non-degenerate before freezing the successor.

## 3. Pattern significance

**[MEASURED]** ufo-check-0 joins E0 (adequacy stop), CASC-0′ (compute-match gate), DDC (power gate), rules-1-c (instrument gate): successive structure-sensitive or compute-matching attempts stopped at pre-registered validity conditions rather than returning a hypothesis-bearing answer.

**[INTERPRETATION]** The recurrence increases evidence weight for a **methodological** conclusion — isolating kernel-specific structure from content, token budget, host cooperation, and control-arm behavior is unusually difficult — NOT for either substantive answer. The structure question remains unmeasured because the gates prevented the endpoint statistics from answering it.

## 4. Recommended move and claim boundary

**[INTERPRETATION]** Proceed only through a blocked `ufo-check-1`: require realized (not merely templated) token/exposure parity; include the neutral length control; exercise every gate on a small real-host pilot; freeze + run the full factorial only if all gates pass.

**[PRE-SPECIFIED]** Under the frozen verdict ordering, instrument validity precedes FAIL/PASS/INCONCLUSIVE.

**[INTERPRETATION]** Ledger entry: checker invocation and extraction mechanics were observed, but whether these hosts USE the UFO checker in the hypothesis-bearing sense is unresolved. **INSTRUMENT-INVALID licenses neither "yes" nor "no," and no feasibility conclusion.**

---

**Coordinator disposition (not a conclusion):** routed to Fable for the dual-model reconcile + the `ufo-check-1` repair-design call (token-matched successor + neutral padding arm). The AG-zero-rejection root cause is a MEASURED, cheaply-confirmable finding (the no-GPU realized-exposure audit over the committed `run-records-ufo0.jsonl`). No re-verdict; the frozen record + INSTRUMENT-INVALID stand.
