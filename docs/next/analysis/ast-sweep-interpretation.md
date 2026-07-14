# AST-generation ensemble sweep — interpretation (GPT-5.6-sol; Fable co-read owed ~07-18)

**Status:** GPT-5.6-sol interpretation of the flat-baseline AST ensemble sweep (`poc/scale/ast-pipeline/results.md`, n=24, blind cross-vendor judges). Transcribed by the coordinator from the read-only-sandbox GPT-5.6 output (Fable is org-capped ~07-18; the dual-model Fable co-read is **owed**). Exploratory methodology finding, **not** a thesis verdict.

## Headline read
1. **S1 (cascade Luna→Claude) is the recommended bulk pipeline** — 11/24 vs S0's 6/24, at **zero extra generation cost**, the best observed cost/yield trade-off. [MEASURED: results.md]
2. **S2's 16/24 (67%) is an ORACLE-selected flat-ensemble CEILING, not a deployable yield** — it keeps the judge-confirmed-faithful one of six single-shots, which requires the judge to already know which is faithful. Retaining just **Luna+Fable** candidates gives a 14/24 post-hoc ceiling; the other four generators add only **two** further successes. So a 2-model ensemble captures most of the gain; the 67% is an upper bound, not a shippable number. [MEASURED + STIPULATED-interpretive]
3. **S3 (forcing-retry) and S4 (merge) do not justify further scaling** in their tested forms (7/24, 8/24 — barely above S0, at real call cost). [MEASURED]

## Cost model (EXTRAPOLATION — explicitly labelled)
- S1 cascade: ~**$30k–$76k per million concepts**.
- Six-way generation (S2 ceiling): ~**$114k–$249k per million**, before selector/judge costs.

## Implication for the molecule pivot (S5) — a design correction
**S5 (reference-composition) must beat a concurrently re-judged FLAT ENSEMBLE, not single-shot Luna.** The decisive comparison is **flat-ensemble vs matched molecule-ensemble**; the per-generator single-shot pairs in S5's current design are secondary diagnostics. [STIPULATED — feeds a Fable revision of `poc/scale/molecule-aug/DESIGN.md`]

## The load-bearing caveat: judge reliability
**Blind A/B (sol vs opus) agreement was only 84/133 candidate verdicts = 63.2%.** Forty-nine disagreements across **20 of 24** concepts required the T tie-break. So the FAITHFUL/LOSSY judgments are **noisy**, and every headline percentage above carries wide error bars — the 25%→67% spread is directionally real but the point values are not precise. This is the central limitation. [MEASURED: judgments/]

## Other caveats (MEASURED / STIPULATED)
- **n=24, single run, exploratory** — no confidence intervals; a confirmatory version needs a larger sample, pre-registered judges, and inter-judge reliability reported up front.
- **Stratification** (4 unanimous-faithful / 12 split / 8 unanimous-lossy) shapes the headline percentages — the 8 unanimous-lossy are hard by construction; report per-stratum.
- **Quality ≠ faithfulness** — S2 leads on both (q2.08), but they are distinct axes.

## Bottom line
The ensemble/cascade approach **does** raise AST-faithful yield (direction robust); the cheap cascade (S1) is the deployable recommendation, best-of-N is a ceiling not a product, forcing-retry is not worth it — but the judge-reliability floor (63.2%) means these are interim, wide-error-bar findings. The molecule arm's decisive test is flat-ensemble vs molecule-ensemble. **Fable dual-model co-read owed ~07-18.**
