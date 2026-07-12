PROVISIONAL-ON-FABLE-PROXY-pA  (kernel-of-truth-29nb, 2026-07-12)
=================================================================
EARLY READ ONLY -- NOT THE FROZEN-INSTRUMENT GRADE.

The frozen g2-import-v2 instrument (c8742dc5) is pA=GPT-5.6-Sol (codex) +
pB=Haiku-4.5 (headless claude). The codex path is usage-capped (~1h) as of
2026-07-12 ~13:20Z. Per maintainer directive, this campaign runs judge-pA as
claude-fable-5 through the SAME headless-claude machinery as judge-pB,
guarded behind `--pa-proxy fable` (the frozen codex path is untouched when
the flag is absent).

Known deviations from the frozen instrument (all disclosed in result.json):
  1. judge-pA model/vendor: claude-fable-5 (Anthropic) instead of
     GPT-5.6-Sol (OpenAI). BOTH judges are therefore Anthropic-family:
     AC1/kappa here are same-family pair stability, NOT cross-vendor.
  2. modelUsage identity check for pA tolerates the claude CLI's background
     haiku helper key ({claude-fable-5, claude-haiku-4-5-20251001} subset);
     the pB exact-single-key check is unchanged.
  3. All response files are kept inside this run_dir (never the canonical
     BASE locations, which stay reserved for the frozen run).
  4. Judge lanes pA/pB run in parallel (frozen driver was sequential);
     the shared call-count.json can only UNDERcount on a write race,
     never spuriously abort.

RECONCILE (coordinator): when the GPT-5.6 cap resets, run the FROZEN
instrument (pA=GPT-5.6-Sol) over the same 84 items (fresh run dir / the
canonical BASE flow, NO --pa-proxy), then compare AC1_A3, arm soundness,
and the fired verdict against this preview. If the AC1 or verdict differs
materially, the GPT-5.6 FROZEN grade GOVERNS; this preview is discarded as
evidence and retained only as a process record.
