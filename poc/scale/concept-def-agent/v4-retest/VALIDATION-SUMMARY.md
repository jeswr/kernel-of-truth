# concept-def concision v4 — validation summary (coordinator custody, 2026-07-13)

Validation of the GPT-5.6 concision-discipline draft (`../concision-discipline-v4-draft.md`) added to
the concept-def prompt (v4 = `../concept-def-prompt-v4.md`, subordinate §1A; v3 sense/non-circularity/AST
rules intact). Re-ran the 5 test concepts on claude-opus-4-8 (temp 0); then an INDEPENDENT GPT-5.6 grade
(the accept-gate's second grader) on the exacting scholarly rubric.

## Result: marginal improvement, not a fix
- **Mechanical gate:** 5/5 pass first attempt, **zero re-queues** (v3 needed a gpt-5.6 re-queue for
  `candidate`; v4 opus passes it first-attempt — the discipline steered off the fragile nested-quote
  phrasing). No sense drift / circularity; AST-adequacy identical (1 faithful / 4 lossy). ~$0.03/~12s each.
- **Exacting GPT-5.6 bar:** v3 = **0/5** → v4 = **1/5** (only `dig` clears; builder/candidate/expensiveness/
  pull still "diffuse, explanatory, redundant"). GPT-5.6: "at this standard the generator is not
  trustworthy at ~100-concept scale because it repeatedly adds redundant explanations and mechanically
  abstract phrasing."

## Honest reading (NOT a conclusion — routed to Fable)
1. The concision block removes some padding (2 clear tightenings, `dig` now ideal) and improves gate
   robustness, but does NOT lift the agent to a first-rate lexicographic register on the exacting bar.
2. **Two caveats temper even the 1/5:** (a) 3 of the 5 concepts (pull/expensiveness/dig) appear verbatim
   in the concision exemplars — a clean generalisation read needs HELD-OUT concepts; (b) this is n=5.
3. **The viable pipeline is unchanged and already budgeted:** the concept-def agent replaces the *authoring*
   (6-10 Fable-agent-days → ~$3-4) with cheap, sense-correct, gate-valid DRAFTS; the register polish to the
   scholarly bar is the maintainer's already-planned ~20-35h human review (or a stronger judge-in-the-loop
   accept gate). The agent is a draft-generator, not a final-register author.
4. **Open Fable call:** whether to invest in a deeper prompt rewrite toward terse genus-differentia (beyond
   the concision block) OR accept draft+human-polish. Recommend the latter given the review is already
   budgeted and a prompt chasing an excellent-only bar has diminishing returns.

Files: `../concept-def-prompt-v4.md`, `*.opus48.json` (v4 records), `codex-grade-v4.json`, `RETEST.md`.
