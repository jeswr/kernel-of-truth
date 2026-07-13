# Independent quality review of the concept-def-agent output (GPT-5.6, coordinator-custody)

Coordinator record of an independent adversarial quality check of the
concept-def-agent's 5-concept smoke output, run because the agent graded its
own scholarly-bar compliance (`TEST-RESULTS.md`: self-judged 5/5 "meets"). An
independent grader is required before the generator is trusted at ~100-concept
scale (the scholarly-definition standard is a HARD, methodologically load-bearing
bar). Raw verdict: `quality-review-gpt56.json`.

## Result: GPT-5.6 says 0/5 meet the bar (on an exacting, excellent-only rubric)

The reviewer was instructed to be exacting ("if merely adequate rather than
excellent, say so and show the better wording"). Under that instruction it judged
**all five as sense-correct but failing the scholarly standard** — the recurring
defect is **explanatory prose rather than lexicographic definition**: padding,
redundant paraphrase, evaluative filler, awkward category tails, and small
extension shifts. Its tighter revisions:

| concept | agent gloss (abridged) | GPT-5.6 revision |
|---|---|---|
| builder | "…brings a large enterprise or country into being and makes it grow, so that…great…bigger and stronger" | "A person who creates and develops an enterprise or nation." |
| pull | "…so that it moves toward oneself or in the direction of one's own movement" | "An act of applying force to move something toward or along with the agent." |
| expensiveness | "…such that one must give much in exchange to obtain the thing" | "The quality of costing a great deal." |
| candidate | "A person under active consideration as a possible choice for a position, award, honor, or other role or benefit." | "A person being considered for a position, award, honor, or other opportunity or benefit." |
| dig | "The act of touching someone abruptly and sharply…pressing into their body for a brief moment." | "A sudden, sharp prod with a finger or elbow." |

GPT-5.6 summary: *"An automated generator producing this pattern would not be
trustworthy at roughly 100-concept scale without expert review, because
superficially plausible definitions repeatedly conceal precision and register
defects."*

## Coordinator disposition (NOT a conclusion — routed to design)

- **Stark dual-model disagreement** (agent self-judged 5/5 vs GPT-5.6 0/5). This
  is exactly why the independent check was run; the agent's self-grade is too
  lenient and cannot be the acceptance signal.
- **The true reading is between the two.** The definitions are sense-correct,
  non-circular, and gate-passing (real strengths); the shortfall is register —
  they read explanatory, not lexicographic. GPT-5.6's revisions are clearly the
  better dictionary form. The "0/5" is on an excellent-only bar I explicitly set.
- **Two open questions for the designer (Fable) + the maintainer, NOT decided here:**
  1. **Is the gloss load-bearing for F1-K?** For kernel-v1 the encoded artifact
     is the AST (`kot-ast/1`); the prose gloss is a human label. The scholarly
     bar bites hardest on the knull *plain-dictionary control arm* (where prose
     IS the artifact), less on kernel AST records. Severity depends on this.
  2. **Prompt revision before scale:** add a lexicographic-concision discipline
     (tightest genus–differentia; cut elaboration, evaluative words, and
     redundant paraphrase; no "the thing"/"other … or …" tails) and re-test. The
     re-queue-on-another-model path already exists; a two-grader accept gate
     (generator + independent GPT-5.6/Fable, agree-to-accept) is the natural
     acceptance rule.
- **No scale generation until:** (a) the prompt-concision revision + re-test, and
  (b) the maintainer's #33 AST-lossy ruling. The generator stays cheap either way
  (~$3–4 / 100).

Status: **PROVISIONAL — methodology flagged, queued for a Fable revise-or-note
pass when Fable capacity returns** (Fable hit its session cap during the smoke).
