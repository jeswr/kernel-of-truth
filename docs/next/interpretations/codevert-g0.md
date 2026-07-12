# FABLE INTERPRETATION — CODEVERT G0 (κ_q^indep = 0.4361 [0.3610, 0.5364] on 6 pinned repos, BELOW the G1 0.5 planning floor; the shortfall is STRUCTURAL — inverse/exhaustive families 0.0000 on all six repos from unrestricted '*' unknown edges — while the forward/lexical subset clears at κ ≈ 0.72; the vertical as DESIGNED does not survive on this pool; a re-scope-or-drop decision now sits with the maintainer; neither programme thesis moves)

- **Author:** Fable (interpretation agent), 2026-07-11. This document
  interprets the MEASURED G0 result; it registers nothing, edits no frozen
  object, no verdict, no registry line, and performs no git/bd/kb operation.
  The coordinator commits and surfaces the maintainer-gated items in §5.
- **Sources (read at source, in full):** `poc/codevert-g0/RESULT.md` (the
  measured spike readout — authoritative for every number below),
  `docs/next/analysis/codevert-g0.md` (the verdict-input framing +
  PROPOSED-ASM ASM-1050–1059), `docs/next/design/CODEVERT.md` rev 2 (the
  binding interpretive frame: §2.2 completeness-precondition semantics
  [PROPOSED-ASM: ASM-1031], §7-G0/§7-G1 gate ladder + kill floors
  [PROPOSED-ASM: ASM-1030], §9 honest limits),
  `docs/next/analysis/round2-steering.md` (the code-vertical-primary bet
  framing and the two maintainer-gated strategic decisions).
- **Epistemic discipline:** **[MEASURED]** restates a counted/computed fact
  strictly from a cited artifact, never recomputed; **[STIPULATED]** marks a
  registered or proposed design choice consumed as-is (all G0 method choices
  are ASM-1030/1031 as built plus PROPOSED-ASM ASM-1050–1059, coordinator
  registration pending); **[DERIVED]** marks an analytic observation made in
  THIS document from MEASURED facts and the design text; **[IMPLICATION]**
  marks a decision-relevant consequence stated for the coordinator/maintainer,
  never a conclusion of this document; **[EXTRAPOLATION]** marks a
  conditional forward projection, never a premise; **[UNMEASURED]** marks an
  honest gap.
- **Governance status, stated first because it bounds everything:** G0 is
  the NON-SCORED engineering spike authorized by the 2026-07-11 GPT-5.6
  review-gate ruling [STIPULATED: CODEVERT.md rev-2 header + §7-G0]. Its
  pool is the agent-selected 6-repo G0 pool [STIPULATED: ASM-1050], NOT the
  G1 pinned-before-looking pool; per ASM-1039's epistemic demotion of cheap
  rungs and the RESULT.md's own status line, **no number here is a
  registered G1 verdict and no G0 number binds G1**. Everything below is
  interpretation of a verdict INPUT.

---

## 1. What the below-floor κ means for the code vertical AS DESIGNED

**The fact** [MEASURED: RESULT.md §1]: κ_q^indep = 0.4361, repo-cluster
bootstrap 95% CI [0.3610, 0.5364] (family-macro 0.4286 [0.3712, 0.5168]),
over the full frozen extractor-independent census (16,722 queries, 8
families × 6 repos, 52,073 LOC). The package-source sensitivity slice is
0.4537 with CI [0.3986, 0.4912] — **entirely below the 0.5 floor**. The
full-repo CI straddles the floor; the point estimate sits below it on both
slices.

**The reading** [DERIVED]: the G1 kill criterion is κ_q^indep < 0.5 on the
pinned G1 pool [STIPULATED: ASM-1030 floors; the floors themselves are
ESTIMATED planning values, maintainer-adjustable at prereg]. G0 cannot fire
that kill — wrong pool, non-scored rung — but it is the best available
predictor of whether it WOULD fire. The prediction is conditional and
should be stated exactly: **[EXTRAPOLATION] if the pinned G1 pool behaves
like this pool, the G1 kill fires on κ_q^indep under the registered
full-8-family semantics**, and the full-distribution product claim dies
before any model exists — which is precisely the cheapest-first outcome
ASM-1004/1030 was built to buy. Three qualifiers keep this honest:

1. **n = 6 repos is the honest cluster count** [MEASURED]; the CI is wide
   by construction and disclosed as the generalization band. A pool of
   20–30 repos (the G1 rule) could land above 0.5. But the mechanism in §2
   makes that unlikely for the two zeroed families: their failure is not a
   sampling accident on this pool, it is a semantics-level property
   observed at saturation (0/3,783 and 0/503, all six repos).
2. **The floor is a planning value, not a measured requirement**
   [STIPULATED: ASM-1030, tagged ESTIMATED in CODEVERT §9.3]. The
   maintainer may adjust it at prereg — but adjusting a floor AFTER seeing
   a spike number that misses it would need explicit disclosure and
   justification, or it is floor-shopping. Any G1 that proceeds with a
   changed floor must carry the G0 number beside the change.
3. **G0 measured only κ_q^indep and mechanical soundness stand-ins.** The
   other three G1 kill legs — R_q ≥ 0.90, precision ≥ 0.95,
   negative-answer validity ≥ 0.90 against adjudicated human gold — are
   [UNMEASURED]; they remain G1's ~70–130 annotator-hour spend (ASM-1038).
   A below-floor κ on the first leg makes spending those hours on the
   OTHER legs of the full-8-family design hard to justify — that is the
   economic force of the result, distinct from its evidential force.

**Bounded, not vindicated, not killed** [DERIVED]: EXTRAPOLATION ASM-1008
("Python is a friendlier extraction domain") is now bounded by fact in both
directions. Friendlier: 0.44 ≫ the measured walls (g8 0/1000; comparable in
magnitude to m0b's 0.3542, different metric — [MEASURED: RESULT.md §5.1]).
Not friendly enough: the full-8-family product semantics does not clear its
own floor on real repos. The extrapolation is spent; what replaces it is a
number.

## 2. The kill is structural, not statistical — and annotation cannot buy it back

This is the interpretively load-bearing finding, more than the headline.

**The per-family decomposition** [MEASURED: RESULT.md §1]: lexical families
(contains, contained-in) 1.0000; forward families 0.2326–0.6466 (pooled
0.7198 over the 4 forward families); inverse/exhaustive families:
imported-by 0.1504, where-defined 0.3994 (bimodal 0/1 per repo),
**callers-of 0.0000 (0/3,783) and instance-of 0.0000 (0/503) on ALL six
repos**. Inverse/exhaustive pooled: 0.1412.

**The mechanism** [MEASURED: RESULT.md §2]: 38.4% of extracted edges are
`unknown`; of these, 1,682 call edges carry an unrestricted ('*')
candidate set — parametrized-decorator result-applications, local-value
calls, call-result calls, constructs where no candidate name is
syntactically derivable [STIPULATED: ASM-1056 candidate discipline]. Under
the §2.2 repo-wide completeness precondition [STIPULATED: ASM-1031], a
single unrestricted call unknown zeroes callers-of AND instance-of for the
entire repo; every repo carries 22–869 of them.

**Why this is structural** [DERIVED]:

- It is not noise: a 0/4,286 outcome across six independently chosen real
  repos is a deterministic consequence of (PY-STAT/1 inventory) ×
  (§2.2 precondition) × (real Python idiom frequency), not a draw from a
  distribution. Re-rolling the repo pool re-rolls the 22–869 count, not
  its positivity — any realistic Python repo contains at least one
  parametrized decorator or local-value call.
- It is not an annotation artifact and **a fail-closed property annotation
  cannot fix it**: annotation (G1's spend) measures precision/R_q against
  gold; it does not change what the extractor proves. The zeros are on the
  extractor's own honest output. No amount of human labelling raises a κ
  that is zeroed by the extractor's own `unknown` mass — the RESULT.md
  states this as "a semantics-level fact about PY-STAT/1 + §2.2 on real
  Python" [MEASURED: RESULT.md §5.2], and the reading is endorsed here.
- It is also not a defect of the candidate-name mechanism: the mechanical
  ablation ('*' mass excluded, restricted candidates kept) recovers
  callers-of to 0.54–0.92 per repo [MEASURED: RESULT.md §2]. The mechanism
  works; the '*' mass is the whole kill. But the ablation is a
  counterfactual, NOT achievable κ — a sound version requires dataflow
  tracking outside the PY-STAT/1 inventory (an extractor version change),
  and the tier-b spec gap (28,051 untracked Load references) binds any
  attempt to soften §2.2 instead [MEASURED: RESULT.md §2, ASM-1057].

**Against this, the subset that clears** [MEASURED]: the forward/lexical 4
families pool at κ ≈ 0.72, with contains/contained-in exact (1.00) and the
instrument itself validated — extractor-independent census satisfied
without conditioning on extraction, dynamic probe 0/5,718 query-level
completeness violations (disclosed vacuity where fail-closed blocking
prevents proved answers), one true validity bug caught and closed via the
pre-registered fix-once path, zero contradictions of 1,415
dynamically-exercised proved facts, all at ~$0 [MEASURED: RESULT.md §3].
[DERIVED] The correct summary is therefore **asymmetric**: the DESIGN's
full-8-family product semantics fails structurally; the INSTRUMENT
(census + fail-closed extractor + probe) passes its own engineering test,
and the forward/lexical half of the query surface is genuinely covered on
real repos. G0 killed a claim and validated a tool in the same run.

## 3. The re-scope options the result leaves open — design choices, not G0 outputs

RESULT.md §5.3 enumerates three defensible G1 universes [MEASURED as
enumerated there; the enumeration itself is analysis, and CHOOSING among
them is a design/maintainer decision — nothing in G0 selects one]:

- **(a) Forward/lexical subset.** Re-scope the product to contains,
  contained-in, imports-of, callees-of, where-defined (the last bimodal —
  hazard-free repos only): pooled κ ≈ 0.72 measured on this pool. [DERIVED]
  Consequences: the product boundary shrinks from "8 measured query
  families" [STIPULATED: ASM-1002] to ~5-with-caveats; callers-of — the
  flagship inverse query and arguably the highest-utility one for a
  developer — is dropped; the G1/G4 workload model and the 82.4/17.6
  query-product denominator [ASM-1035] must be re-derived; the design
  document's product claim must be re-scoped BEFORE G1 freezes, or G1
  measures a dead denominator. Whether 0.72 clears a floor depends on
  whether the maintainer re-registers the floor for the subset — a fresh
  planning choice, not an inheritance.
- **(b) UNKNOWN-INCOMPLETE as a first-class product answer.** Every blocked
  inverse query in G0 still returned `UNKNOWN-INCOMPLETE(partial_listing,
  blocking_count)` — a labelled lower bound plus an honest incompleteness
  certificate [MEASURED: RESULT.md §5.3(b)]. Re-scoping "answered" to
  include this changes the ENDPOINT, not the extractor. [DERIVED] This is
  the most product-honest option and the most epistemically dangerous one:
  it converts a κ-failure into a κ-success by definitional change, which is
  legitimate ONLY if the utility of partial answers is independently
  measured (a G2/G4 question — RESULT.md §5.5 explicitly does not license
  it) and if the re-definition is registered before, and disclosed on,
  every subsequent readout. Done silently it is exactly the
  denominator-shrinking move ASM-1003 exists to forbid.
- **(c) PY-STAT/2 with bounded local dataflow.** Convert the '*' mass to
  candidates; measured ablation headroom callers-of 0.54–0.92
  [MEASURED]. [DERIVED] This is an extractor VERSION change — new
  enumerated inventory, new content hash, new G0-class spike before any
  G1 — and the headroom number is an upper bound from a counterfactual
  that assumed the conversion succeeds; the tier-b Load-reference closure
  (ASM-1057) is the named risk that a sound PY-STAT/2 pushes candidate
  mass back toward '*'. Engineering cost is real but compute-cheap;
  calendar cost is another design-build-spike cycle in a programme the
  steering note says has too many designs and too few results.

[DERIVED] The options are not exclusive — (a)+(b) compose naturally (a
forward-proved core plus certified-partial inverse answers), and (c) can
follow either. But every one of them changes a registered or proposed
design object (ASM-1002 product boundary, ASM-1030 endpoints/floors,
ASM-1031 inventory), so **any of them re-enters the external review gate**
per the rev-2 ruling — none is a quiet amendment.

## 4. What this does to the code-vertical-primary bet and to both theses

**The theses do not move** [DERIVED, and stated deliberately]: both
programme theses remain INCONCLUSIVE-PENDING, exactly as the round-2
steering note holds. G0 is non-scored, off the pinned pool, and — by
registered stipulation ASM-1000 — NO CODEVERT outcome in either direction
is evidence about kernel CONTENT. The result says nothing about NL entry
(out of scope entirely), nothing about g2/g3/knull-v2, and supplies no
new evidence on thesis-level questions.

**But it materially constrains the vertical the bet is placed on**
[DERIVED]:

- The round-2 steering rated G0 "the single highest-value substantive next
  experiment" precisely because "a bad κ_q result stops the vertical
  before any annotation spend; a good one defines a defensible G1
  universe." The measured outcome is the FIRST branch for the design as
  written and — nuance the steering did not pre-state — simultaneously the
  SECOND branch for a subset: the defensible universe exists, but it is
  smaller than the designed product. The bet's payoff distribution just
  narrowed at both ends.
- The steering's maintainer-gated decision A (annotation portfolio) ranked
  CODEVERT G1's 70–130 annotator-hours as candidate #1 for the bounded
  human budget. [IMPLICATION] That ranking is now stale as stated:
  spending those hours on the full-8-family G1 would adjudicate gold for a
  product claim whose coverage headline is already structurally below
  floor on the best available evidence. The hours are only well-spent
  AFTER a re-scope decision fixes what G1 measures. G0 thereby did its job
  in the portfolio: it protected the binding resource.
- The steering's decision B ("is the kernel becoming optional?") is
  UNTOUCHED in logic but sharpened in flavor [DERIVED]: the
  kernel-free-win observation (ASM-1000) still holds, and G0 now shows
  that even the kernel-free vertical, at its designed scope, has a
  structural coverage ceiling on real Python. The "small model + aligned
  typed store" success story survives only in the forward/lexical or
  partial-answer form.

**The decision this surfaces — labelled implication, not a conclusion**:

> **[IMPLICATION — for the coordinator to surface to the maintainer]** The
> code vertical as DESIGNED (full-8-family proved-complete product
> semantics) should be treated as measured-infeasible on real Python at
> PY-STAT/1 + §2.2 semantics, subject only to the (weak) chance that the
> pinned G1 pool is atypically decorator-free. The live choice is
> **re-scope or drop**: (a) forward/lexical subset, (b)
> UNKNOWN-INCOMPLETE-as-product, (c) PY-STAT/2 spike, or (d) drop the
> vertical and reallocate the G1 annotation hours to the other
> decision-A candidates (g2 Π-soundness gold, knull-v2 plain-arm). This
> document recommends none of them; it notes only that (i) every option
> re-enters the external review gate, (ii) option (b) requires a
> registered endpoint change to stay honest, (iii) option (d) interacts
> with decision B — dropping the strongest kernel-free line changes the
> shape of the "kernel optional?" question rather than answering it, and
> (iv) the G1 annotation spend should not be authorized for the
> full-8-family design in any case.

## 5. Honest gaps, carried verbatim

1. **Precision vs adjudicated human gold: [UNMEASURED].** G0's mechanical
   stand-ins (1,415 proved facts dynamically confirmed, zero
   contradictions; 0/5,718 completeness violations with disclosed vacuity)
   are encouraging but are machine-only proxies [STIPULATED: ASM-1059];
   the registered precision ≥ 0.95 leg is G1 annotation work.
2. **R_q vs human gold: [UNMEASURED]** — same reason, same spend.
3. **Pool non-representativeness:** 6 agent-selected small permissive
   repos [STIPULATED: ASM-1050]; nothing licenses a statement about the
   pinned G1 pool beyond the explicitly conditional extrapolation of §1.
4. **Product utility of partial answers: [UNMEASURED]** — option (b)'s
   entire value rests on a G2/G4-class question G0 cannot touch.
5. **The census universe is constructed** [STIPULATED: CODEVERT §9.3]: it
   enumerates what is syntactically visible, not what developers ask; a
   real workload could weight the zeroed families more OR less than the
   census does. The 0.4361 headline inherits the census's stratification.
6. **The floors are planning values** [ESTIMATED in the design]; this
   interpretation treats 0.5 as binding only because it is the registered
   planning floor the result was commissioned against.

## 6. One-paragraph summary

G0 did exactly what a cheapest-first kill rung is for: at ~$0 and zero
annotation hours it converted the programme's largest unmeasured
extrapolation into a number, and the number is below the floor —
κ_q^indep = 0.4361 [0.3610, 0.5364], package-source CI entirely below 0.5
[MEASURED]. The shortfall is structural, family-specific, and
annotation-proof: unrestricted unknown call edges (22–869 per repo,
inherent to real Python under the PY-STAT/1 inventory) zero the
inverse/exhaustive families on all six repos under the §2.2 completeness
precondition, while the forward/lexical subset clears at κ ≈ 0.72 and the
measurement instrument itself validated cleanly [MEASURED/DERIVED]. If the
pinned G1 pool behaves likewise, the G1 kill fires on the full-8-family
design [EXTRAPOLATION, conditional]. Neither thesis moves; the
code-vertical-primary bet is not dead but is materially constrained to
re-scoped forms — forward/lexical subset, certified-partial answers, or a
PY-STAT/2 extractor generation — each a maintainer design decision that
re-enters the external review gate, none a G0 output [IMPLICATION]. The
G1 annotation budget should not be spent until that decision is made.
