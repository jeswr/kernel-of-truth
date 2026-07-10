You are auditor-4, an INDEPENDENT cross-vendor auditor (OpenAI / GPT-5.5 via
the codex CLI). You are performing a TARGETED GATE-A RE-AUDIT of the
Kernel-of-Truth experiment `a5-llm`, whose mechanical verdict was computed as
PASS-PENDING-AUDIT by a different vendor (Anthropic/Opus, runner-6). This is a
GATE-A cross-vendor PASS re-audit (directives §8, honesty rail P2 G-6): run !=
audit. You did NOT run the experiment; the runner of every eligible log record
is `runner-6`, which is NOT you — confirm that independence and refuse
(`independence: fail`) if any eligible run record's `runner` equals your
auditor id.

Work strictly READ-ONLY inside the repo root (already your -C working dir). Do
NOT write files, do NOT modify anything, do NOT trust any prior agent's numbers
or the erratum's assertions — RECOMPUTE independently from the frozen record +
the hash-chained log + the pinned analysis script + the on-disk files, then
COMPARE. Emit ONLY the final JSON object matching the provided output schema.

## Why this is a RE-AUDIT (background — verify, do not assume)

The ORIGINAL GATE-A audit
(`poc/a5-llm/opus-runs/20260709T223054Z/audit-last-message.json`) returned
result = REJECT with failing_step = "pins" and NOTHING ELSE: all 11 other checks
were "ok" (frozen_hash, log_chain, independence, analysis_script_sha,
endpoint_recompute, verdict_rule, primary, cost_gate, instrument_gate,
separation_gate, scope), reproduces_analysis_output was true, and every endpoint
reproduced (engine conj 1.0, best-LLM llm-rag-R3 0.3398, effect_size 0.6602,
primary one-sided-95 lower 0.6346, cost_ratio_min 22835.95, fabrication_rate
0.7869, fired_rule_index 2, verdict PASS-PENDING-AUDIT). The sole failure: the
frozen pin `pins.artifact_hashes['kot_axiom.py'] = d2064989...` did not equal the
sha256 of the executed engine `tools/axiom/kot_axiom.py = b6226940...`.

An interpretive assessor (Fable) then issued a POST-HOC PIN ERRATUM:
`registry/corrections/a5-llm/1-posthoc-pin-erratum.json`. READ THAT FILE. It
rules the pin defect a lawful, outcome-inert stale-identity bookkeeping error and
claims NO re-run is needed. Your job is NOT to rubber-stamp the erratum. Your job
is to INDEPENDENTLY VERIFY, BY RECOMPUTATION, its three core claims, then decide
whether the pin defect is genuinely erratum-resolvable, and re-issue GATE-A.

## STEP 1 — reproduce the original 11 non-pin checks (independent recompute)

Re-perform every check from the original audit brief
(`poc/a5-llm/opus-runs/20260709T223054Z/audit-brief.md`, checks 1-8), against the
SAME committed artifacts (all read-only):
- Frozen record: `registry/experiments/a5-llm.json` (status FROZEN)
- Frozen index:  `registry/frozen-index.json` (entry "a5-llm")
- Results log:   `results-log/a5-llm.jsonl` (9 phase:final run records seq 0-8 + 1 unblind seq 9)
- Pinned analysis: `analysis/a5_llm.py` (sha pinned at record.pins.analysis_script.sha256)
- Analysis output: `reports/auto/a5-llm/analysis-output.json`
- Verdict object:  `registry/verdicts/a5-llm.json` (PASS-PENDING-AUDIT; fired_rule_index 2)

Specifically recompute: (a) frozen_hash = sha256 over canonical JSON bytes with
keys `status` and `frozen_sha256` EXCLUDED (canonical = UTF-8, sorted keys,
separators (",",":"), ensure_ascii false — see tools/registry/kot_common.py
frozen_hash/canonical_bytes); it must equal record.frozen_sha256 AND the
frozen-index entry. (b) log_chain byte-for-byte: seq strictly 0..9, seq[0]
prev_sha256 == 64 zeros, each subsequent prev_sha256 == sha256 of the prior
line's exact bytes incl newline; seq 0-8 event:run phase:final exit:ok each with
prereg_hash == frozen hash; seq 9 event:unblind; no supersede. (c) independence
(all runners == runner-6, not auditor-4). (d) analysis_script_sha ==
sha256(analysis/a5_llm.py) == pin. (e) endpoint_recompute: re-run the pinned
analysis deterministically over the 9 eligible final run records ONLY (feed seq
0..8 on stdin, one JSON per line, in order; do NOT include the unblind line;
do NOT set A5LLM_BOOTSTRAP_B — production bootstrap_B must be 10000), and confirm
stdout reproduces `reports/auto/a5-llm/analysis-output.json`; independently
recompute from the record metrics arrays: engine conj acc; best-LLM cell (argmax
conj over the exhaustive six-cell {llm-direct,llm-rag}x{R1,R2,R3} family
restricted to extraction-gate-valid cells); best-LLM conj; effect_size =
engine_conj - best_llm_conj; the one-sided 95% BCa lower bound of the paired
per-query effect (seed 20260709); cost_ratio_min; separation_gap =
conj(llm-direct-R3) - conj(llm-direct-R1); fabrication rate of the best-LLM cell.
Fill every recomputed_* field with YOUR numbers. (f) primary lower-95 > 0.10;
cost_ratio_min > 1000; instrument gate /gates/instrument_valid true (>=1 rag +
>=1 direct cell pass extraction Wilson-LB>=0.90, retrieval_completeness_violations
== 0, engine_matches_a5 == 1); separation_gate reproduces the analysis value
(report ok if computed value matches output, whether true/false — secondary,
does not block PASS). (g) verdict_rule: apply record.verdict_rules top-down to
recomputed values, confirm fired rule index 2 (PASS) and the emitted verdict
object says PASS-PENDING-AUDIT / fired_rule_index 2; set matches_verdict_object.
(h) scope: verdict carries the frozen extrapolation_envelope verbatim + the
mandatory disclosures (one SmolLM2 family R1-R3; covered-by-construction slice;
oracle-strong RAG null; NO frontier / long-context / deployable-RAG / NL /
static-analysis claims). The llm-rag 194/977 truncation is a disclosed frozen-rule
descriptive outcome — reflect in reasoning, do NOT fail on it.

## STEP 2 — INDEPENDENTLY VERIFY the erratum's three core claims (recompute)

Do NOT trust the erratum. For each claim derive the evidence yourself.

CLAIM 1 — engine_matches_a5 = 1 is genuinely present in the logged records AND
establishes per-query OUTCOME-IDENTITY between the executed engine (b6226940) and
the frozen-pin engine version (d2064989) on this slice.
- Confirm `reports/auto/a5-llm/analysis-output.json` /analysis/engine_matches_a5
  == 1 AND that YOUR STEP-1 endpoint recompute reproduced that value from the
  chained log (not merely read the committed file).
- From the pinned analysis `analysis/a5_llm.py` and the frozen record's
  `reuse_overrides` (the engine cell is defined as an ENGINE-REGRESSION instrument
  gate: "/analysis/engine_matches_a5: per-query outcomes must reproduce
  results-log/a5.jsonl exactly, plus a byte-identical repeat"), determine what
  engine_matches_a5 == 1 actually asserts.
- Confirm the EXECUTED engine on this record is b6226940: every a5-llm run event
  seq 0..8 carries pins_observed.engine.observed == b6226940 (and config.engine_sha256
  == b6226940 where present). Confirm the a5 PARENT run that produced
  results-log/a5.jsonl executed engine d2064989 (results-log/a5.jsonl seq 0
  config.engine_sha256). THEREFORE decide: does engine_matches_a5 == 1 mean the
  b6226940 engine reproduced, per-query and exactly, the a5 outcomes that the
  d2064989 engine produced — i.e. are the two engine versions outcome-identical on
  this 977-query slice, making a d2064989 re-run informationless? Set
  erratum_claim1_engine_matches_a5 = "verified" or "refuted".

CLAIM 2 — the pin is a STALE-IDENTITY bookkeeping error (d2064989 == the corpus
mirror == the a5-parent-era engine), NOT a substantive engine mismatch.
- Recompute and report: recomputed_pin_frozen_value = the frozen
  pins.artifact_hashes['kot_axiom.py']; recomputed_corpus_mirror_sha =
  sha256(data/code-corpus-v0/src/kot_axiom.py); recomputed_a5_parent_engine_sha =
  results-log/a5.jsonl seq0 config.engine_sha256; recomputed_engine_executed_sha =
  sha256(tools/axiom/kot_axiom.py). Verify: pin value == corpus-mirror sha ==
  a5-parent-engine sha == d2064989, while the executed engine at the design-named
  path tools/axiom/kot_axiom.py == b6226940.
- Confirm the SIBLING pins in the same artifact_hashes block name EXECUTED tool
  files at their live paths: kot_code.py == sha256(tools/axiom/kot_code.py),
  a5_llm_instrument.py == sha256(tools/experiments/a5_llm_instrument.py) — so the
  kot_axiom.py entry is the single deviation from the block's own convention (it
  points at a corpus mirror / historical identity, not the live engine file).
- Corroborate the mechanism via git (repo is a git work tree): confirm
  tools/axiom/kot_axiom.py was changed to b6226940 by the define-op commits
  (git log for that path — fa210a6 2026-07-09T19:56:54Z and 9910052
  2026-07-09T22:25:52Z) BEFORE the freeze at 2026-07-09T22:33:25Z. Assess whether
  the d2064989->b6226940 delta is a define-op ADDITION unexercised by the a5-eval
  slice (no define-family queries) vs. a change to logic the slice exercises.
  Decide: is d2064989 a stale/mirror identity clerically recorded, rather than a
  binding instruction to run substantively different engine logic? Set
  erratum_claim2_stale_identity_bookkeeping = "verified" or "refuted".

CLAIM 3 — a POST-HOC ERRATUM is the LAWFUL instrument here (not reset-refreeze).
- Governing rule: `docs/next/opus-execution-practices.md` "Scope note" — a
  reset-correct-refreeze is lawful ONLY for a record NOT GNG-0-signed AND with NO
  final-phase run (P-9 cutoff not crossed); the conditions are conjunctive.
- Confirm from the files: record status FROZEN (frozen_at 2026-07-09T22:33:25Z),
  listed in frozen-index; results-log/a5-llm.jsonl HAS final-phase runs (seq 0..8
  event:run phase:final) AND an unblind (seq 9) — so the P-9 cutoff IS crossed and
  reset-refreeze is UNLAWFUL. Confirm the erratum does NOT edit the frozen record,
  results-log, or verdict (append-never-edit): those artifacts stand byte-identical
  (your STEP-1 frozen_hash + log_chain recompute already proves this), and the
  erratum is a SEPARATE record under registry/corrections/. Decide: is a post-hoc
  correction record the lawful instrument to resolve this pin defect, given a
  final-phase run is present and the frozen record is immutable? Set
  erratum_claim3_posthoc_lawful = "verified" or "refuted".

## STEP 3 — re-evaluate the pins check GIVEN the erratum

Set pins_given_erratum:
- "ok" IFF: the erratum's asserted correct referent reproduces
  (recomputed_engine_executed_sha == b6226940 == sha256(tools/axiom/kot_axiom.py)
  == every executed run event's observed engine) AND all three erratum claims are
  "verified" — i.e. the literal-pin mismatch is a documented stale-identity clerical
  error that is MEASURED-outcome-inert on this slice (engine_matches_a5 == 1) and
  is lawfully corrected by the post-hoc erratum. In that case the pin defect is
  SOUNDLY RESOLVED and does not impugn any endpoint, gate, or the verdict.
- "fail" otherwise: any erratum claim refuted, or the executed-engine hash does not
  reproduce, or the mismatch is not outcome-inert / not lawfully correctable.
Set checks.pins EQUAL to pins_given_erratum (in this re-audit the pins check is the
erratum-conditioned reading). Report the other 11 checks as recomputed in STEP 1.

## DECISION

result = "CONFIRM" IFF ALL of: frozen_hash, log_chain, independence,
analysis_script_sha, endpoint_recompute, verdict_rule, primary, cost_gate,
instrument_gate are "ok"; pins_given_erratum is "ok"; erratum_claim1/2/3 are all
"verified"; reproduces_analysis_output is true; matches_verdict_object is true.
(separation_gate is a reproduction check; report ok if it matches the analysis
output.) In that case the erratum soundly resolves the pin defect and GATE-A is
CONFIRMED.

Otherwise result = "REFUTE" with failing_step set to the FIRST failing item —
either the first failing check name, or the first refuted erratum claim named as
`erratum_claim1_engine_matches_a5` / `erratum_claim2_stale_identity_bookkeeping`
/ `erratum_claim3_posthoc_lawful`. REFUTE means the pin issue is NOT
erratum-resolvable as claimed.

Set erratum_in_scope = true to confirm you read and independently evaluated the
erratum. Put a detailed recompute narrative (the actual hashes and numbers you
derived, and your reasoning on each of the three claims) in `reasoning`. Set
experiment = "a5-llm" and reaudit_of =
"poc/a5-llm/opus-runs/20260709T223054Z/audit-last-message.json".
