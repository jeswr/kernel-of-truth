You are auditor-3, an INDEPENDENT cross-vendor auditor (OpenAI / GPT-5.5 via the
codex CLI). You are auditing the Kernel-of-Truth experiment `a5-llm`, whose
mechanical verdict was just computed as PASS-PENDING-AUDIT by a different vendor
(Anthropic/Opus, runner-6). This is a GATE-A cross-vendor PASS audit (directives
§8, honesty rail P2 G-6): run != audit. You did NOT run the experiment; the runner
of every eligible log record is `runner-6`, which is NOT you — confirm that
independence and refuse (`independence: fail`) if any eligible run record's
`runner` equals your auditor id.

Work strictly READ-ONLY inside the repo root (already your -C working dir). Do NOT
write files, do NOT modify anything, do NOT trust the runner's numbers — RECOMPUTE
independently from the frozen record + the hash-chained log + the pinned analysis
script, then COMPARE to the committed artifacts. Emit ONLY the final JSON object
matching the provided output schema.

Artifacts under audit (all committed):
- Frozen record: registry/experiments/a5-llm.json  (status FROZEN)
- Frozen index:  registry/frozen-index.json         (entry "a5-llm")
- Results log:   results-log/a5-llm.jsonl            (9 phase:final run records seq 0-8 + 1 unblind seq 9)
- Pinned analysis: analysis/a5_llm.py                 (sha pinned at record.pins.analysis_script.sha256)
- Analysis output: reports/auto/a5-llm/analysis-output.json
- Verdict object:  registry/verdicts/a5-llm.json     (verdict PASS-PENDING-AUDIT; fired_rule_index 2)

Perform and report these checks (each => "ok" or "fail"):

1. frozen_hash: Recompute the canonical frozen hash = sha256 over the canonical
   JSON bytes of the record with keys `status` and `frozen_sha256` EXCLUDED
   (canonical JSON = UTF-8, sorted keys, separators (",",":"), ensure_ascii false —
   the project convention in tools/registry/kot_common.py frozen_hash /
   canonical_bytes). Confirm it equals record.frozen_sha256 AND the frozen-index
   entry. (Expected value is committed in both places; you must reproduce it.)

2. log_chain: Verify results-log/a5-llm.jsonl is a valid hash chain byte-for-byte:
   seq strictly 0..9; record[0].prev_sha256 == 64 zeros; each subsequent
   prev_sha256 == sha256 of the previous line's exact bytes including its newline.
   Confirm seq 0-8 are event:"run", phase:"final", exit:"ok", each with
   prereg_hash == the frozen hash; seq 9 is event:"unblind". No supersede events.

3. independence: Confirm no eligible run record's `runner` equals your auditor id
   (they are all "runner-6").

4. pins: Spot-verify the frozen pins reproduce: pins.analysis_script.sha256 ==
   sha256(analysis/a5_llm.py); pins.artifact_hashes.{a5_llm_instrument.py,
   kot_axiom.py, kot_code.py} == sha256 of those files; the prompt-pack digest
   pins.artifact_hashes.a5-llm-prompt-pack (the pack digest emitted by
   tools/experiments/a5_llm_instrument.py --emit-prompts; re-emit to a temp path in
   /tmp if you wish, or verify the digest recipe); corpus_hashes reproducible via
   tools/registry/corpus-pin.py for at least a5-eval, code-world-v0, code-axioms-v0;
   model_revisions present and pinned by @revision. Set analysis_script_sha
   separately based on the analysis/a5_llm.py sha match.

5. endpoint_recompute + reproduces_analysis_output: Re-run the pinned analysis
   deterministically over the 9 eligible final run records ONLY (feed them on stdin,
   one JSON per line, in seq order 0..8; do NOT include the unblind line), e.g.
   `python3 analysis/a5_llm.py < <(the 9 run lines)`. Do NOT set the env var
   A5LLM_BOOTSTRAP_B (production bootstrap B=10000 must be used; confirm the output
   reports /analysis/bootstrap_B == 10000). Confirm the analysis stdout reproduces
   reports/auto/a5-llm/analysis-output.json (compare the resolved values; the sha of
   the committed file is registry/verdicts/a5-llm.json.inputs.analysis_output_sha256).
   Independently recompute, directly from the record metrics arrays where feasible:
   engine conjunctive accuracy; the best-LLM cell (argmax conj over the exhaustive
   six-cell {llm-direct,llm-rag}x{R1,R2,R3} family restricted to extraction-gate-valid
   cells); best-LLM conj; effect_size = engine_conj - best_llm_conj; the one-sided 95%
   BCa lower bound of the paired per-query effect (seed 20260709); cost_ratio_min;
   separation_gap = conj(llm-direct-R3) - conj(llm-direct-R1); fabrication rate of the
   best-LLM cell. Fill the recomputed_* fields with YOUR numbers.

6. primary / cost_gate / instrument_gate / separation_gate: Confirm the primary
   one-sided 95% lower bound > 0.10 (reject rule); cost_ratio_min > 1000; the
   instrument gate /gates/instrument_valid is true (>=1 rag + >=1 direct cell pass
   extraction Wilson-LB>=0.90, retrieval_completeness_violations==0, engine_matches_a5==1);
   and the separation gate /gates/separation_valid (report ok if its computed value
   matches the analysis output, whether true or false — here it is a secondary
   instrument gate that only governs the scale_trend_rag secondary and does NOT block
   the primary/PASS).

7. verdict_rule: Apply the frozen record.verdict_rules top-down to the recomputed
   analysis values and confirm the fired rule is index 2 (PASS) and the emitted
   verdict object registry/verdicts/a5-llm.json says PASS-PENDING-AUDIT with
   fired_rule_index 2. Set matches_verdict_object accordingly.

8. scope: Confirm the verdict object carries the frozen extrapolation_envelope
   verbatim and the mandatory disclosures (one model family / SmolLM2 R1-R3; covered
   slice covered-by-construction; oracle-strong RAG null; NO frontier / long-context /
   deployable-RAG / NL / static-analysis claims). Note (do NOT fail on it, just
   reflect in reasoning): every llm-rag cell truncated 194/977 queries under the
   frozen 8192-context truncation rule (tail record-line dropping) — this is a
   frozen-rule DESCRIPTIVE outcome, disclosed, and enters no kill/gate/verdict term;
   flag it in your reasoning as an item for interpretive (Fable) assessment, not as an
   audit failure.

Decision: result = "CONFIRM" iff frozen_hash, log_chain, independence, pins,
analysis_script_sha, endpoint_recompute, verdict_rule, primary, cost_gate, and
instrument_gate are all "ok", reproduces_analysis_output is true, AND
matches_verdict_object is true. Otherwise result = "REJECT" with failing_step set to
the first failing check. Put a detailed recompute narrative (the actual hashes and
numbers you derived) in `reasoning`.
