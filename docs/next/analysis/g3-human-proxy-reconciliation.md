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
