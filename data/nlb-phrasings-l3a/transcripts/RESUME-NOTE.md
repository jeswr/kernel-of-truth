# l3a EVAL/PROBE build — resume note (Opus runner, 2026-07-10)

A prior build attempt was interrupted by a session limit. This note records
what was resumed vs. re-authored, per EVAL-BUILD-SPEC.md.

## Resumed as-is (prior fresh-identity transcripts, unchanged)
- eval.jsonl: all 9 batches (eval-000..008) authored by the prior run; verified
  complete (870/870 qids, packet order, `{qid,text}`, zero malformed) and lint
  GREEN on EVAL. No re-authoring.
- eval family re-authors from the prior run (reauthor-instance-true,
  reauthor-instance-false-disjoint, reauthor-unique-maker) are already folded
  into eval.jsonl and pass EVAL lints.

## probe.jsonl — assembled from two prior fresh identities (PROBE-NO-LABEL fix)
The interrupted run left probe.jsonl carrying reauthor-1's phrasings, which
tripped PROBE-NO-LABEL on the 6 `man`-concept items (q0511-q0514, q0562,
q0564): "Is X a male human?" — the label `man` is a substring of `human`.
- 54 non-`man` items: taken from probe-reauthor-1 (session 74b7596c) — these
  pass PROBE-NO-LABEL (e.g. the `father` items use "male parent", not
  "fathered").
- 6 `man`-concept items: taken from probe-reauthor-4 (session 41080391), which
  authored "Is X male?" — clean (no `man` substring).
  reauthor-4's OWN `father` items ("Who fathered X?") trip `father` ⊂
  `fathered`, so reauthor-4 was NOT adopted wholesale; only its clean
  `man`-family items were used. No hand-editing of any phrasing.
Result: nlb_lint --vertical l3a → GREEN (dev/eval/probe checked, 0 findings).

## audit.txt — recoverability audit (this session)
Fresh blind judge (session fb966c8b) under prompt-audit.md over the
deterministic 60-item sample. See audit-recoverability.json.
