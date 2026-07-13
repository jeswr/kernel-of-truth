# g3 human-vs-proxy reconciliation — the FAIL verdict is likely a proxy (judge-pB Haiku) artifact

Coordinator custody record of the human-gold reconciliation of the registered **g3-llmproxy-v3 = FAIL**
verdict, against the maintainer's 15-item human sample (workbook `1KS_5h3jZbPumHnR6w3aBFwUSV0Oa_FuJ`,
the issue-#32 fill). Produced by a 3-stage workflow (extract → reconcile → adversarial verify);
**every count independently reproduced by the verify stage (AGREEMENT-CONFIRMED).** This records the
mechanical reconciliation; the re-run decision follows the standing annotator-proxy directive.

## What the FAIL rests on
`registry/verdicts/g3-llmproxy-v3` fired rule 1 (`/analysis/proxy_fail`), NECESSITY endpoint: the
**concordant** necessity-violation rate (both judges: Pass A q1=yes AND Pass B q2=no) = 36/195 = 0.1846,
one-sided 95% Wilson LB 0.1433 > the 0.10 kill bar. (Sufficiency was secondary/INCONCLUSIVE.) The design is
a cross-family two-annotator pair: **judge-pA = gpt-5.6-sol** (Pass A designee), **judge-pB = claude-haiku-4-5**
(Pass B designee). Corroboration therefore hinges on the necessity pattern A=TRUE ∧ B=no.

## Human-vs-proxy agreement (15-item sample; verified)
| Face | Agreement | Note |
|---|---|---|
| Pass A (q1, "target claim true in ordinary usage") | **14/15 = 93.3%** | sole miss g3-end-03; consistent with the measured human-vs-gpt-5.6 q1 κ≈0.756 |
| Pass B (q2, "every condition holds") | **10/15 = 66.7%** | 5 misses, ALL one-directional: proxy(judge-pB Haiku) B=no where human B=yes |
| Both-match (A∧B) | 9/15 = 60.0% | |
| **Necessity violations (q1=yes ∧ q2=no)** | **human 1/15 = 6.67%** vs **proxy 7/15 = 46.7%** | only g3-end-01 is a shared genuine violation |
| Sufficiency violations | 0 on both sides | full agreement |

## Finding: corroborates_fail = FALSE (verified)
The human sample points **opposite** to the FAIL on aggregate. Human necessity-violation rate **6.67% sits
BELOW the 0.10 kill bar**; the proxy's 46.7% is inflated by judge-pB (Haiku) over-flagging Pass B — on 5 of
the 6 extra flags (end-06/07/09, begin-01/03) the human says all conditions hold, and on 1 (end-03) the
human says the concept does not even apply (A=FALSE). Every extra proxy flag is FAIL-inflating and traces to
Pass-B hyper-literalism — exactly the "harder, literalism-sensitive q2 face" both g3 interpretation docs
flagged as **unvalidated in direction**. This is a 15/200 sample: corroborative, not decisive — but it is
adversarially-verified and one-directional, which is a strong signal the registered FAIL is a proxy artifact.

## Disposition (standing directive: reconcile & re-run on material disagreement)
- The registered g3 FAIL is **NOT overturned by this record** — overturning needs a formal re-run + re-verdict.
- It is flagged **PROXY-PROVISIONAL-SUSPECT**: a registered FAIL whose decisive statistic (concordant
  necessity rate) is not reproduced by human Pass-B judging on the sample.
- **Recommended re-run:** re-judge g3 **Pass B on the full 200** with a stronger judge (Opus, per the
  standing "judge upgraded Haiku→Opus for any further g3 pilot" note), recompute the concordant
  necessity-violation rate, and re-verdict. If the corrected rate falls below 0.10, g3 flips FAIL → not-FAIL,
  which materially changes the correctness-thesis picture (the kernel's typing would be adequately NECESSARY
  on human judging). Surfaced to the maintainer for awareness; the re-run itself is authorized + cheap.

## Opus-pB re-judge outcome (2026-07-13) — the FAIL STANDS; proxy-artifact hypothesis REFUTED

To test whether the g3 FAIL was a judge-pB (Haiku) Pass-B over-flagging artifact, the full 200-item Pass B
leg was re-judged with a stronger judge (claude-opus-4-8, temp 0, identical Pass B prompt — model swapped
only). Coordinator-run checkpointed job; labels sha256 `514ae261…`; 200/200 decisive (2 cannot-say).
Analysis: `poc/g3-llmproxy-v3/opus-pb-rejudge/analysis.json`.

**Result: FAIL-STANDS.** The concordant necessity-violation rate with Opus-pB = **39/193 = 0.2021**
(one-sided 95% Wilson LB **0.1588**), still **above the 0.10 kill bar** — even slightly higher than the
registered Haiku-pB rate (0.1846, LB 0.1433). So the FAIL is **confirmed by an independent stronger judge**,
not a Haiku-specific artifact.

Cross-judge detail: Opus-pB vs Haiku-pB agree **153/198 = 77.3%** (κ on q2=no = 0.53); Opus is NOT
systematically more lenient (24 Haiku-no/Opus-yes vs 21 Haiku-yes/Opus-no — balanced). On the recoverable
human items Opus matches human 4/6 and itself over-flags some (e.g. begin-01: human yes, Opus no).

**Reconciliation disposition:** the earlier 15-item human sample (6.7% necessity, below bar) raised a
legitimate concern, but it was **concept-specific** (only the low-violation `end`/`begin` concepts) and too
small to generalise; on the FULL 200 items a second, stronger LLM judge reproduces the FAIL. The registered
g3 = FAIL is therefore **upheld** and the PROXY-PROVISIONAL-SUSPECT flag is **cleared** (validated, not
overturned). Residual honest caveat: on the handful of human labels both LLM judges sometimes run stricter
than the human on Pass B, so a fully human-graded g3 could differ — but establishing that needs far more
than 15 human labels, and the pre-registered verdict rests on the LLM-concordant rate, which holds under two
independent judges. **No re-verdict; the frozen record is untouched.**
