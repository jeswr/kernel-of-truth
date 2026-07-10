You are auditor-5, an INDEPENDENT cross-vendor auditor (OpenAI / GPT-5.5 via the
codex CLI). You are auditing the Kernel-of-Truth experiment `g8`, whose mechanical
verdict was just computed as FAIL by a different vendor (Anthropic/Opus, runner-9).
This is a GATE-A cross-vendor audit (directives sec.8, honesty rail P2 G-6): run !=
audit. You did NOT run the experiment; the runner of the eligible run record is
`runner-9`, which is NOT you — confirm that independence and set
`independence: fail` if the eligible run record's `runner` equals your auditor id.

Note this verdict is a FAIL (a decisive kill on the primary fragment gate), not a
PASS. Your job is exactly the same: RECOMPUTE independently and confirm the
mechanical verdict object is the pure function of the frozen record + the ops
amendment overlay + the hash-chained log + the pinned analysis script. A CONFIRM
means "the mechanical FAIL is correctly computed", NOT any judgement about the
science.

Work strictly READ-ONLY inside the repo root (already your -C working dir). Do NOT
write files, do NOT modify anything, do NOT trust the runner's numbers — RECOMPUTE
independently, then COMPARE to the committed artifacts. Emit ONLY the final JSON
object matching the provided output schema.

Artifacts under audit (all committed):
- Frozen record:   registry/experiments/g8.json   (status FROZEN)
- Frozen index:    registry/frozen-index.json      (entry "g8")
- Ops amendment:   registry/amendments/g8/1-pin-mathlib-1000-sample.json
- Results log:     results-log/g8.jsonl            (1 phase:final run seq 0 + 1 unblind seq 1)
- Pinned analysis: analysis/g8.py                  (sha pinned at record.pins.analysis_script.sha256)
- Analysis output: reports/auto/g8/analysis-output.json
- Verdict object:  registry/verdicts/g8.json       (verdict FAIL; fired_rule_index 1)
- Instrument:      tools/experiments/g8_instrument.py (+ g8_fragment.py)

Perform and report these checks (each => "ok" or "fail"):

1. frozen_hash: Recompute the canonical frozen hash = sha256 over the canonical
   JSON bytes of the record with keys `status` and `frozen_sha256` EXCLUDED
   (canonical JSON = UTF-8, sorted keys, separators (",",":"), ensure_ascii false;
   project convention in tools/registry/kot_common.py frozen_hash / canonical_bytes).
   Confirm it equals record.frozen_sha256 AND the frozen-index entry
   (expected a3c4510113513525c8e5aaff4f7a0f27c2ee6edaed9463c3b0e25d8da3b2b41c).

2. amendment: Confirm registry/amendments/g8/1-pin-mathlib-1000-sample.json is a
   LAWFUL ops amendment (P2 P-9): schema kot-amend/1; kind "ops"; seq 1 (filename
   prefix matches); experiment "g8"; its single patch op is a `replace` whose target
   /pins/corpus_hashes/mathlib-1000-sample currently holds a value beginning
   "PINNED-AT-INPUTS:" in the frozen record; the replacement value is a bare 64-char
   lowercase hex digest that EQUALS the kot-corpus-hash/1 digest of data/mathlib-1000-sample/
   (recompute via tools/registry/corpus-pin.py mathlib-1000-sample; expected
   9c2a3a888b98593d999adb65c7a32cba0cdbf092bcdb5f2b9c738e4cff2a80c2). Apply the
   amendment as an overlay in seq order and confirm the amended effective-record
   canonical hash equals registry/verdicts/g8.json.inputs.amended_record_sha256
   (expected a2b46a0e9dbddc1dd8c47cffada119e56a51a8484507d75e53180589af8b3bd2). Confirm
   the amendment touches ONLY /pins/ (no design/endpoint/verdict-rule field) and the
   frozen file's own bytes + frozen_sha256 are untouched.

3. log_chain: Verify results-log/g8.jsonl is a valid hash chain byte-for-byte: seq
   strictly 0..1; record[0].prev_sha256 == 64 zeros; record[1].prev_sha256 == sha256
   of line 0's exact bytes incl. newline. Confirm seq 0 is event:"run", phase:"final",
   exit:"ok", prereg_hash == the frozen hash, runner "runner-9"; seq 1 is
   event:"unblind". No supersede events.

3b. independence: Confirm the eligible run record's `runner` (runner-9) is NOT your
   auditor id.

4. pins + analysis_script_sha: Spot-verify the frozen pins reproduce:
   pins.analysis_script.sha256 == sha256(analysis/g8.py) (expected
   e5769612fc072faf38e7155abf13f3d7e76515036a5fe29dde2a4cbd9dc03674 — set
   analysis_script_sha ok/fail on this); corpus_hashes reproducible via
   tools/registry/corpus-pin.py for math-v0, math-lean-sample, math-mm, kernel-v0
   (the non-placeholder pins) AND mathlib-1000-sample (the amendment-resolved pin).
   The run record's config.host_model pins model Qwen/Qwen2.5-7B-Instruct @ revision
   a09a35458c702b33eeacc393d103063234e8bc28, decode temperature 0 — confirm present
   (the frozen record is R0 and pins NO host model, so the model/revision/decode are
   legitimately pinned in the run config, not the frozen record).

5. endpoint_recompute + reproduces_analysis_output: Re-run the pinned analysis
   deterministically over the 1 eligible final run record ONLY (feed seq 0 on stdin
   as one JSON line; do NOT include the unblind line):
   `python3 analysis/g8.py < <(sed -n '1p' results-log/g8.jsonl)`. Confirm the stdout
   reproduces reports/auto/g8/analysis-output.json (compare resolved values;
   registry/verdicts/g8.json.inputs.analysis_output_sha256 is the committed output sha).
   Independently recompute directly from the run record's metrics counts:
   fragment_rate = n_in_fragment / n_mathlib_decls = 0/1000 = 0.0; one-sided 95% Wilson
   (z=1.645) lb=0.0, ub ~= 0.0027; location_rate = n_location_top5 / n_location_targets
   = 5/39 ~= 0.1282, Wilson lb ~= 0.0638, ub ~= 0.2408; roundtrip_holds = (n_roundtrip_fixed
   == n_roundtrip) = (33==33) = true; f_verification_rate = n_f_verified / n_llm_candidates
   = 7/139 ~= 0.0504. Fill the recomputed_* fields with YOUR numbers.

6. fragment_gate / location_gate / fverification_gate / instrument_gate: Confirm the
   pre-registered gate terms as pure functions:
   - fragment_gate ok iff fragment_wilson_ub <= 0.01 is TRUE (the FAIL leg fires;
     equivalently the primary fragment_wilson_lb=0.0 does NOT clear 0.01).
   - location_gate ok iff location_wilson_ub <= 0.80 is TRUE (the FAIL leg fires;
     equivalently location_wilson_lb=0.0638 does NOT clear 0.80).
   - fverification_gate ok iff your recomputed f_verification_rate >= 0.01 (i.e. the
     near-zero-F-verification kill did NOT fire; report ok when your value matches the
     analysis output, whether or not it is >= 0.01).
   - instrument_gate ok iff /gates/instrument_valid is true (n_mathlib_decls >= 1000
     AND n_location_targets >= 39).

7. verdict_rule: Apply the frozen record.verdict_rules top-down to the recomputed
   analysis values and confirm the FIRST firing rule is index 1 (FAIL), because
   fragment_wilson_ub <= 0.01. Confirm the emitted verdict object
   registry/verdicts/g8.json says verdict "FAIL" with fired_rule_index 1. Set
   matches_verdict_object accordingly.

8. scope: Confirm the verdict object carries the frozen extrapolation_envelope_verbatim
   and kill_criterion_verbatim unchanged, rungs_measured ["R0"], scale_language_licensed
   "none", and the coverage restatement (fraction 0.3542, rung molecules-v0 — the m0b
   census restated per P2 G-7, not a new measurement).

Decision: result = "CONFIRM" iff frozen_hash, amendment, log_chain, independence,
pins, analysis_script_sha, endpoint_recompute, verdict_rule, fragment_gate,
location_gate, fverification_gate, and instrument_gate are all "ok",
reproduces_analysis_output is true, AND matches_verdict_object is true. Otherwise
result = "REJECT" with failing_step set to the first failing check. Put a detailed
recompute narrative (the actual hashes and numbers you derived) in `reasoning`.
