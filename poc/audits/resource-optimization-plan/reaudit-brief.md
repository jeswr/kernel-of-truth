# Cross-vendor RE-AUDIT — Kernel-of-Truth resource-optimization plan, REVISION-1

You are the cross-vendor adversarial auditor (Codex / GPT-5.5) for the "Kernel of Truth"
programme. You (a prior auditor session) audited this plan's logged-result-reuse honesty ruling
and returned CONFIRM_WITH_CONDITIONS: 2 CRITICAL loopholes + 4 more, 6 required amendments. The
designer (Fable, different vendor) has now produced REVISION-1 claiming to close all six. Your
job: **verify closure adversarially, and hunt for loopholes the revision may have introduced.**
Read-only sandbox; read the actual files; run no mutations. Default stance: skeptical — a
maintainer is about to RATIFY based on your verdict, and nothing reuse-permissive goes live
until they do.

## Your prior findings (the six things that had to be fixed)

1. CRITICAL — RC-4 Case-B comparator laundering: comparator/config could be chosen AFTER
   unblinding (pick the weakest known baseline). Fix claimed: **RC-7** — data-blind comparator
   selection from a closed set (frozen mandatory-baseline law / exhaustive declared family /
   prior frozen rule), pinned + byte-reverified at freeze; post-unblinding choice refuses
   (`ERR_P2_REUSE_RC7`); no disclosure-only path.
2. CRITICAL — f7/ASM-0010 survivor data in a confirmatory slope. Fix claimed: **RC-8** +
   §3.4-3 rewrite + ASM-0010 `load_bearing:true`; outcome_selected_arms=true requires
   pre-specified selection_adjusted_inference anchored to a pinned analysis field, else
   `ERR_P2_REUSE_SURVIVOR`; permanent-exploratory rows may not enter `reused_from` at all; f7
   lower-rung reuse is now a gate-t5 maintainer decision presenting BOTH accountings.
3. MAJOR — RC-5 overlap under-specified / CPU waiver trusts producer repeat-claims. Fix
   claimed: overlap must cover each reused producer × each material (arm×rung) stratum or carry
   a frozen representativeness_justification; CPU waiver now requires a committed
   `consumed_output_hashes` artifact recomputed+matched by the tool.
4. MAJOR — kot-reg/1 had no lawful slot for the reuse declaration (D9 not landed). Fix claimed:
   **kot-reg/2** (`reused_from`, `reuse_overrides`, `pins.artifact_hashes`); kot-log/1 reuse
   witness; verdict-gen step 3b re-verifies all RCs at consumption; prereg-freeze +
   registry-check `--reuse` collision refusal; `reuse-check audit` producer-chain traversal.
5. MAJOR — reuse-check.py was a name-level discovery tool, not the RC gate; `--record` omitted
   `--gate`. Fix claimed: documented command is `check --record … --gate` (exit 3, fails
   run-scripts closed); pin-identity-tiered matcher derived LIVE from results-log; false
   pos/neg fixed; renamed-identical arms surfaced by impl-pin cross-match.
6. MAJOR/collateral — ASM-0010 load-bearing; ASM-0011 L must derive from structured edges. Fix
   claimed: both done; `reuse-check lscore` surfaces 17 free-text mismatches.

## Read the actual revision

- `docs/next/resource-optimization-plan.md` — §3.0 post-audit changelog, RC-1…RC-8, the Case-B
  prose, §3.4-2/3/4, §3.6, wire format, §5.
- `registry/schema/kot-reg-2.json`, `registry/schema/kot-log-1.json` — the new reuse fields +
  witness.
- `tools/registry/reuse-check.py`, `verdict-gen.py`, `prereg-freeze.py`, `registry-check.py`,
  `kot_common.py` (esp. the shared `check_record_reuse`) — does the CODE enforce RC-1…RC-8,
  RC-5 hash recompute, RC-7 basis re-verification, RC-8 survivor refusal, and the collision
  refusal? Trace at least one refusal path per RC.
- The ratification interlock: `registry/reuse-ratification.json` is ABSENT — confirm every
  consumption path is fail-closed (`ERR_P2_REUSE_UNRATIFIED`) today, AND that editing the ruling
  doc would void a signature (sha binding).
- `registry/assumptions.jsonl` (ASM-0010/0011), `docs/next/research-engine.md` §2.7.
- `tools/registry/test_fixtures.py` — do the 10 new TestReuse cases actually exercise each
  refusal path, or are they shallow?

## Judgment calls the designer flagged — scrutinise each for a new hole

(a) Case A (producer data not yet seen) pins no rows; the row set derives at consumption as ALL
matching final rows; freeze verifies the producer has zero final rows + no verdict. — Can this
be gamed by staging producer rows to appear after freeze?
(b) RC-2 tolerates consumer pin placeholders at freeze but requires affirmative real-vs-real
identity at consumption. — Any indeterminate-pin path that still licenses consumption?
(c) RC-4 fresh-arm = ≥1 declared arm with no reused rows; a verdict requires ≥1 fresh eligible
run row even for reuse records. — Enough to stop an all-but-one-reused primary?
(d) "identical" pin classification requires corpus AND model proof; shared encoder pin alone
proves nothing. — Correct, or exploitable?
(e) kot-reg/2 scope = exactly the audit's reuse fields + artifact_hashes (D6 stays gated). — Any
gap this leaves open for reuse specifically?

## Answer

1. **Amendment closure**: for each of the 6, is the loophole CLOSED, PARTIALLY closed, or NOT
   closed? Cite the enforcing code/prose.
2. **New loopholes**: does REVISION-1 introduce any new path (in RC-7/RC-8 mechanics, the
   interlock, the matcher, the judgment calls) to launder already-seen data into a confirmatory
   claim, or to bypass the interlock?
3. **Code-vs-policy**: does the tooling now bind as the prose says?
4. **Verdict**: CONFIRM (ratifiable as-is), CONFIRM_WITH_CONDITIONS (list the remaining
   amendments), or REFUTE. Be specific and terse; cite file/section. Return ONLY the JSON object
   matching the output schema as your final message.
