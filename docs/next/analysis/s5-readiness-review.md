# Molecule S5 — GPT-5.6 readiness review (Fable revision owed ~07-18)

**Status:** GPT-5.6-sol independent readiness review of the molecule-augmented (S5) design, incorporating the AST-sweep interpretation. Verdict: **NOT YET for a confirmatory run** (exploratory pilot OK, non-decisive). The 7-item revision spec below is owed to Fable (org-capped ~07-18). Transcribed verbatim by the coordinator from the read-only GPT-5.6 output.

S5 is **not ready for a decisive run as designed**. It is suitable only for an exploratory engineering pilot. The current design would not yet support a defensible answer to whether reference-composition beats the flat ensemble.

## Findings

1. **The decisive comparison is missing — holds.**

The interpretation explicitly requires a concurrently re-judged flat ensemble versus a matched molecule ensemble ([interpretation:15](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/ast-sweep-interpretation.md:15)). S5 instead makes Luna-vs-Luna and Fable-vs-Fable single shots primary ([DESIGN:57](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:57), [DESIGN:300](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:300), [DESIGN:320](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:320)).

Required correction: define four matched candidate cells per concept:

- flat-Luna, flat-Fable;
- molecule-Luna, molecule-Fable.

“Matched” means the same model snapshots, one call per model, decoding settings, attempt/retry budget, generation period, gate-failure treatment, and judge protocol; only the reference prompt/lexicon differs. Generate all four fresh and interleaved for the confirmatory sample—existing flat records are acceptable only for the exploratory pilot.

Define `Flat-E2 = any(flat-Luna, flat-Fable) judged FAITHFUL` and `Mol-E2 = any(molecule-Luna, molecule-Fable) judged FAITHFUL`. The primary endpoint is the paired concept-level difference `Mol-E2 − Flat-E2`, tested with McNemar on those two binary ensemble outcomes. Single-generator pairs become secondary.

This is an oracle/best-of-two ceiling, not a deployable selector. If the claim specifically invokes the six-generator S2 ceiling of 16/24 rather than the Luna+Fable 14/24 ceiling, both arms must instead use the same six generators. A deployable claim additionally needs one frozen selector or cascade applied identically to both arms ([interpretation:6–7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/ast-sweep-interpretation.md:6)).

2. **Judge reliability and planned sample are inadequate for confirmation — holds.**

A/B agreement was only 84/133 = 63.2%, with disagreements on 20/24 concepts ([interpretation:17](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/ast-sweep-interpretation.md:17)). The proposed response—same LLM A/B/T panel plus roughly ten human spot-checks—is insufficient ([DESIGN:266](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:266), [DESIGN:439](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:439)). Agreement is not accuracy, and correlated cross-model bias—especially toward visible references—will not necessarily appear as disagreement.

The n=24 pilot cannot resolve the predicted effects. The only genuinely prospective generalization sample is n=30; at that size, exact two-sided McNemar needs at least six improvements and no reversals merely to cross p=.05. The fitted n=100 may detect the upper predicted single-model lift under favorable discordance, but not robustly, and it cannot establish held-out generalization.

Approximate paired sizing, assuming a 30–40% discordant-pair fraction:

- For a 15-point observed lift: n≈105–140 for 80% power; n≈141–187 for 90%.
- For a 10-point observed lift: n≈236–314 for 80%; n≈316–421 for 90%.

A practical fixed design is therefore about **200 analyzable fresh concepts for a 15-point MCID**, or about **420 for a 10-point MCID**, plus a missing/gate-failure margin. The corrected ensemble’s expected lift must itself be specified; the current predictions concern single generators only ([DESIGN:341](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:341)).

For illustration only, 63.2% agreement corresponds under optimistic independent, symmetric error assumptions to about 24% error per judge and about 15% after three-vote majority, attenuating a true 15-point difference to roughly 10.5 points. That would push required n toward roughly 214–285 for 80% power. Actual correlated bias may be worse.

Required protocol: two independent, domain-qualified human fidelity judges for every confirmatory candidate, with a third human adjudicator; calibrate on non-evaluation examples, freeze the rubric, and judge candidates separately in randomized order. Use the LLM panel as a secondary robustness measure. Report raw agreement and κ/AC1 with confidence intervals overall and by arm/reference status. The statement that n=100 “resolves ~14pp” and the proposed Wilson CI on discordant proportion should be replaced: power depends on total discordance, and the paired risk difference needs an appropriate paired-binomial/score or exact CI ([DESIGN:318](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:318)).

3. **The bridge lexicon creates differential semantic-credit bias — holds and is load-bearing.**

The manifest records 13 self-flagged faithful and 18 self-flagged lossy bridges ([manifest:7](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/lexicon/manifest.json:7)), yet all are labelled `research-grade`; for example, `money` explicitly drops major criterial content ([money.json:4](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/lexicon/records/money.json:4)). Some locally “faithful” bridges depend on lossy bridges: `institution` is self-faithful while importing `group` and `law` ([institution.json:7](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/lexicon/records/institution.json:7)); `law` is itself self-lossy ([law.json:7](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/lexicon/records/law.json:7)).

More seriously, judges see only the gloss and are instructed to credit it at face value, never the formal referenced explication ([judge addendum:3](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/judge-addendum.md:3), [judge addendum:33](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/judge-addendum.md:33)). Thus S5 can receive credit for meaning absent from the recursively encoded AST. The design acknowledges conditionality ([DESIGN:433](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:433)), but disclosure does not cure the endpoint bias.

Required correction:

- Independently human-adjudicate all 31 bridge records and their dependency chains, not ≥5 ([DESIGN:168](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:168)).
- Mark them `provisional/model-authored` until accepted; do not call them validated or research-grade solely from mechanical validation.
- Judge confirmatory outputs against recursively expanded formal semantics, preferably through an arm-neutral canonical rendering, rather than awarding the gloss’s full meaning.
- Report separate outcomes for conditional composition fidelity and end-to-end expanded-AST fidelity.
- Every output admitted to a “validated inventory” requires item-level human acceptance. Outputs importing unvalidated/lossy bridges should remain conditional/provisional.

If lossy bridges remain intentionally endorsed as new semantic atoms, the defensible claim narrows to “composition improves yield conditional on this approximate inventory,” not “prime-grounded formal fidelity improved.”

4. **Arm blinding does not hold; evaluation-set fitting does — both are disclosed but insufficiently controlled.**

Generator and strategy labels are hidden, but reference-bearing candidates reveal the augmented arm ([DESIGN:288](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:288)). Same-pool judging keeps the nominal prompt constant but does not prevent shared pro-reference bias or within-concept anchoring. Call this candidate-label blinding, not arm blinding. Use independent presentation and recursively expanded/anonymized judge renderings where feasible.

The bridge list was selected from the same 100 concepts’ lossy notes ([DESIGN:77](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:77), [DESIGN:191](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/DESIGN.md:191)). Therefore both the 24-concept pilot and 100-concept main set are fitted evaluations; only a prospectively frozen fresh sample can support generalization.

Zero slug collisions does not fully close leakage. The manifest contains an unresolved lemma-level warning: evaluation concept `initiation` has lemma `institution`, matching the bridge label ([manifest:47](/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/molecule-aug/lexicon/manifest.json:47)). Resolve this with sense/WordNet-URN mapping and a frozen rule—exclude the item, disambiguate the bridge, or document a pre-run noncollision adjudication. The held-out sample and all lemma/synset collision results must be frozen before generation; the current manifest only records checking consensus-100.

## Bottom line

**NOT YET for confirmatory S5.** As written, it cannot defensibly answer “does reference-composition beat flat generation?” An exploratory pipeline shakedown is reasonable, but it must not be reported as the decisive test.

Fable’s revision spec is:

1. Make matched E2-vs-E2—or six-vs-six—the sole primary comparison.
2. Generate both arms fresh with matched budgets; count gate failures intention-to-treat.
3. Use a sufficiently large prospectively held-out sample: approximately n=200 for a 15-point MCID or n=420 for 10 points.
4. Replace proxy-only judging with full independent human adjudication; LLM judgments secondary.
5. Human-review all 31 bridge records and distinguish conditional from end-to-end fidelity.
6. Freeze the lexicon, fresh sample, collision adjudications, judges, prompts, ensemble rule, MCID, n, exclusions, CI/test, multiplicity, and stopping rule before generation.
7. Keep fitted-100 and per-generator results explicitly exploratory.

The Fable dual-model co-read/revision remains owed around **07-18** because of the organization cap ([interpretation:1–3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/ast-sweep-interpretation.md:1)); the confirmatory freeze should wait for that revision.