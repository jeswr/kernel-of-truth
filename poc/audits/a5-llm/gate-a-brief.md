# Cross-vendor GATE-A audit — a5-llm mechanical verdict recompute

You are the cross-vendor auditor (Codex / GPT-5.5) for the "Kernel of Truth" programme. Run-vs-audit
separation: the a5-llm experiment was RUN by Opus (runner); you are a different vendor and independently
recompute its mechanical verdict. Read-only sandbox; read files, run read-only recomputation, no mutations.
This is a mechanical GATE-A recompute (like the f2b-replicate audit at
`registry/audits/f2b-replicate/1-gate-a-codex.json`), NOT an interpretation.

## Target
`registry/verdicts/a5-llm.json` — the mechanical verdict `PASS-PENDING-AUDIT`. The experiment:
engine (deterministic kot-axiom) vs pinned SmolLM2 LLM arms (135M/360M/1.7B, direct + oracle-strong RAG)
on the a5 code-oracle 977-query slice; primary = absolute conjunctive-accuracy difference (engine − best-LLM),
PASS iff effect LB95 > 0.10 AND cost_ratio_min > 1000 AND the arm/instrument gates hold.

## Read + recompute
- `registry/experiments/a5-llm.json` (FROZEN, frozen_sha256 11c3dc4e...; the arms, primary, verbatim kills,
  gates, envelope, pins incl analysis_script 8f7aa880, pack 41182691, instrument 94c5403f, harness_manifest f58874fa).
- `results-log/a5-llm.jsonl` (the final-phase records with per-item metric arrays) + `poc/a5-llm/results-incoming/`
  (the a5-llm-raw/1 cells) + `analysis/a5_llm.py` (the pinned analysis) + `reports/auto/a5-llm/` (the analysis output).
- RECOMPUTE the endpoints directly from the logged per-item data: the primary effect_size (reported 0.6602),
  cost_ratio_min (22,836), and each gate/secondary (separation_valid, covered_superiority, refusal_superiority,
  rag_lift_r3, scale_trend_rag, fabrication_material, instrument_valid). Verify: the frozen canonical hash
  reproduces 11c3dc4e; the analysis-script sha is 8f7aa880; the log hash-chain/eligibility; the pack_sha /
  model_revision / decode_pins headers on every cell; runner-vs-auditor independence.
- Re-evaluate the frozen verdict rule top-down and confirm it fires to the recorded outcome.

## Two things to scrutinise specially (report even if the verdict object matches)
1. **scale_language_licensed = "slope".** The design envelope is SIGN-ONLY, and `separation_valid = false`
   + `scale_trend_rag = false` (the LLM arms do NOT show a valid scale trend). Is licensing "slope" correct,
   or should the verdict license "sign" given the FAILED scale gate? Is this a verdict-gen logic defect?
2. **Truncated-RAG.** 194/977 llm-rag prompts truncated at the 8192 ctx limit (the "oracle-strong" retrieval
   overflows). Do the recomputed numbers correctly treat/record the truncated rows, and does the truncation
   materially affect the recomputed primary (best-LLM identity / rag_lift)? Report the truncation's effect on
   the recompute — you are NOT interpreting whether it invalidates the claim (Fable's), only whether the
   mechanical recompute is affected.

## Verdict
CONFIRM (recompute matches the verdict object within tolerance and the rule fires as recorded) or REFUTE
(a recompute mismatch or a verdict-rule defect — e.g. the scale-language licensing). Return ONLY the JSON
object matching the output schema as your final message.
