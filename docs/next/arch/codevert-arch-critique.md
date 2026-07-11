# Fable architecture critique — GPT-5.6 CASK-PY/1 proposal (bidirectional-design round, code vertical)

> **Status: [ARCHITECTURE CRITIQUE — steering input to the coordinator's
> synthesis; the synthesis, not this critique, goes through the GPT-5.6 review
> gate].** Author: Fable, architecture-critic role, 2026-07-11. This document
> changes no frozen object, registers nothing, runs nothing, and performs no
> git/bd/kb operation.
>
> **Object under critique:** the GPT-5.6 proposal **CASK-PY/1** in
> `poc/gpt56-review/arch-codevert-propose-20260711/last-message.json` (read in
> full).
>
> **Inputs read at source:** that proposal; `docs/next/design/CODEVERT.md`
> rev 2 (the registered synthesis it must be judged against, incl. the R1–R12
> review-response table and ASM-1000–1008 / PROPOSED-ASM-1030–1039);
> `docs/next/design/NLB.md` §6–§7 (score-class protocol; NLB-0 non-decisive
> discipline, ASM-0943/0944); `docs/next/design/FRONT.md` §5–§6 (Rules 1–5,
> shared/matched vs native cells, NL-boundary discipline, anti-budget-shopping
> §1.2); `docs/next/design/RAGC.md` §2.3–§2.4 (parity instrument,
> anti-weak-control); `docs/next/programme-3-neurosymbolic-architecture.md`
> §1.2/§1.3/§1.3a/§1.4 (KOT-SIZE/2, KOT-COST/2, KOT-LIFE/1, W1);
> `docs/next/analysis/round1-steering.md`; the coverage-census readout
> (`scratchpad/coverage-census.result`: STILL-INCOMPLETE + NO-KILL, as scoped
> by the GPT-5.6 covcensus review).
>
> **Tag convention:** [MEASURED: ref] = registry verdict/artifact restated
> inside its envelope; [STIPULATED: ASM-id] = registered design choice;
> [ESTIMATED] = planning number, no measurement; [UNMEASURED] = a claim in the
> proposal that would need a measurement we do not have; [OPINION] = my
> architectural judgement.

---

## 0. Verdict in one paragraph

CASK-PY/1 is not a rival architecture — it is **~85% convergent re-derivation
of the already-registered CODEVERT/1 rev-2 synthesis**, independently arriving
at PY-STAT/1-equivalent conservative extraction with typed `unknown`
candidate-name sets and `UNKNOWN_INCOMPLETE`, evidence-gated orientation
alternatives (abandoning the mandatory-inverse defect its own lineage
introduced), numeric clarification caps (0.05/0.20) with the
clarification-adjusted utility U (λ=0.25), deterministic no-retry v1 edits with
a finite hazard scan, an identical-front-end→SQLite control, and
extractor-independent raw-byte census sampling of targets. That convergence is
evidence the rev-2 corrections are stable under independent derivation — the
most useful thing about the proposal [OPINION]. It contributes **two genuine
improvements** the synthesis should absorb (the empty-agreement→CLARIFY rule;
the crisp `UNKNOWN_INCOMPLETE(partial_lower_bound, blocking_count)` API) and
**five regressions** it should reject: (1) re-billing the pilot as "the single
most decisive cheap falsifier" — it is a screen, and it is not cheap on the
programme's measured binding resource (annotation, not GPU-hours); (2) folding
the G1 census INTO the pilot, losing the cheap-kill-first ordering; (3) pulling
the 15% edit share back into the first scored run, against the registered
design-track demotion; (4) rebuilding a standalone front-end/pilot with no
mention of NLB-FE/1 unification (re-importing the pilot-duplication defect
rev-1 already removed); (5) unclustered pilot statistics and a kill list that
omits the deflationary GEN-EXEC arm while enumerating four CASK-favourable
kills. The matched-baseline win remains **asserted mechanism plausibility**
with a well-designed test attached — no measured number anywhere in the
registry or the literature supports it, and one budget-vector choice (the
500 ms p95 cap) risks manufacturing the win by construction.

---

## 1. Component / boundary / model-size choices: SOUND vs UNSUPPORTED

Judged against the measured record: f2b-transfer stage-1 endorsement PASS
(A = 0.9784, LB 0.9606 — **gold-authority/membership-gold axis only; no
evidence for code extraction or NL entry** [MEASURED:
poc/f2b-transfer/judge-1-results/stage1-analysis.json, scoped per the review]);
coverage census STILL-INCOMPLETE / NO-KILL (general-index kill not supported,
suite not even enumerated; D3 sound-lane 0.8825 ≫ 0.05 [MEASURED:
scratchpad/coverage-census.result, as re-scoped by rev-covcensus]); the NL wall
still the standing measured FAIL (a5-nl 41.6% retention + S2 kill; l3a-parse
47.6%, paraphrase 0/261 [MEASURED: registry/verdicts/a5-nl.json,
l3a-parse.json]).

| Choice | Verdict | Basis |
|---|---|---|
| Two typed seams only (`InterpretationSet`, contract-only executor); no prose past the boundary | **SOUND** | The only seam class with a measured green anywhere (f2b-replicate verify-retry accept seam, +0.1507 / LB +0.1053 at cost 0.103 [MEASURED: registry/verdicts/f2b-replicate.json]); text-appended and internal-delivery seams measured net-harmful/unresolved. |
| Conservative enumerated static extractor, 4-state facts, candidate-name `unknown`s, completeness precondition for inverse/exhaustive + negative answers | **SOUND design; coverage UNSUPPORTED** | Converges on ASM-1031 verbatim. But every measured coverage number the programme owns is brutal (g8 0/1000; m0b 0.3542 corpus-indexed [MEASURED]), and the census NO-KILL cuts both ways: the general index is not killed, and nothing is measured on Python repos either. "Python is a friendlier extraction target" remains EXTRAPOLATION (ASM-1008). κ_q^indep ≥ ~0.5 is a planning floor, not a number [UNMEASURED]. |
| 110M encoder + 4 heads, int8, deterministic constructor; never emits SQL/code | **SOUND as first build; the joint bar UNSUPPORTED** | Matches NLB's registered primary parser class (ASM-0905). Lit band 0.85–0.95 whole-frame on closed grammars; **no cited work reports retention-at-S2-bound for a ≤360M parser on a grammar like ours** [LIT-BACKED via CODEVERT §2.3 / PARSE.md §5a]. The proposal itself tags this its "riskiest learned assumption" — correct epistemics, keep the tag. |
| Evidence-gated orientation alternatives (added only when cues absent/conflicting) | **SOUND** | Adopts ASM-0940/0941 semantics; fixes CASK-CODE/1's mandatory-inverse defect (CODEVERT rev-2 §2.4). Motivated by the measured a5-nl directional kill (contained-in 24 / where-defined 18). |
| **Empty-agreement exception** ("all agree only by being empty" → CLARIFY, never answer) | **SOUND — and an improvement over rev 2** | Rev 2 only *disclosed* the empty-denotation laundering subclass as a residual (§9.6); CASK-PY/1 makes it an executable acceptance rule. Absorb into the synthesis [OPINION]. |
| Deterministic v1 edits, no neural draft/retry; hazard scan; pinned insert_import | **SOUND spec** | Converges on ASM-1037's RENAME-SAFE/1 + H1–H8 shape. But see §4: putting edits in the FIRST scored pilot is a regression. |
| Clarification caps 0.05/0.20 + U with λ=0.25 | **SOUND shape; numbers UNSUPPORTED** | Identical to ASM-1033 — but there tagged [ESTIMATED], maintainer-adjustable. CASK states them bare, as if settled. No measurement behind either cap or λ [UNMEASURED]. |
| 70/15/15 workload; symbols-or-aliases-only questions | **STIPULATED, disclosed** | Same stipulation as ASM-1002. Descriptive references out-of-contract is an honest coverage cost. The workload model is a constructed universe, not measured developer demand — the residual rev-2 §9.3 names; CASK's final-paragraph scoping ("on a pinned static-Python query/edit distribution") is acceptable. |
| ≤0.75 GB packed / ≤1 GB RSS / warm p95 ≤500 ms; ~256 MB fact allocation | **Consistent with pins; arithmetic UNMEASURED — and one gaming risk** | Matches NLB ASM-0946 ceilings. No measured bytes-per-edge or p95 on the pinned rig exists (G0's job). **Risk:** if the 500 ms p95 cap is part of B_k, it may EXCLUDE the strongest ≤360M generic decoder on CPU *by construction* — budget-vector shopping, exactly what FRONT §1.2's derivation rule exists to prevent. B_k must be derived by rule, not chosen where the generic arm is weak [OPINION; see §3]. |
| "Repositories exceeding the cap are rejected **or sharded**" | **UNSOUND as written** | Sharding silently changes the "analyzed scope" over which the completeness precondition quantifies — an inverse query across shards can go `proved`-empty per shard while cross-shard unknowns exist. Either drop sharding or pin cross-shard `unknown` semantics [OPINION]. |
| Amortization of extraction over repeated repo use as a win argument | **UNSUPPORTED** | No measured query-volume model; KOT-LIFE/1 requires amortization at pinned volumes (10³/10⁶/10⁹) from measured KOT-COST/2 figures, not assumed [UNMEASURED]. |
| Architecture-family framing ("not evidence for distinctive kernel content") | **SOUND** | Converges on ASM-1000. Note one loss: CASK's `instance_of` is Python-class-level only; the kernel-concept `instance-of` stratum — CODEVERT's single future kernel seam — is silently gone. Keep the stratum [OPINION]. |

---

## 2. Is the claimed "single most decisive cheap falsifier" decisive, cheap, and NL-wall-compliant?

**NL-wall compliance: YES structurally, with two unpinned residuals.** NL
enters only through the front-end's accepted `InterpretationSet`; the executor
receives serialized contracts and no prose; no arm receives gold contracts or
gold SQL; task targets are sampled from a raw-byte syntactic census frozen
before extraction — the proposal genuinely internalizes the
extractor-relative-coverage repair (ASM-1030) rather than repeating the trap.
Residuals: (a) **who answers the clarification turn at eval time is
unspecified** — without rev-2 §3.1's pre-annotated scripted-response protocol
the turn is an open NL oracle channel into the measured system; (b) phrasing
authors' blindness to extractor output is implied, never pinned. Both are
one-line fixes; both must be pinned before any scored run [OPINION].

**Decisive: NO — and the proposal half-concedes it, then un-concedes it.** The
header says "kill **this instantiation**" and the closing paragraph correctly
says a positive pilot cannot establish the matched-budget claim. But the prose
also says a negative result "can cheaply kill **the proposed mechanism**" and
the whole rung is billed as "the single most decisive cheap falsifier." That is
the G2-non-decisiveness trap re-entering through the kill side:

1. **Kill ≠ mechanism kill at pilot budget.** Both learned arms share a ≤5
   GPU-h tuning allowance. A fired kill discriminates "this instantiation at
   pilot training scale" from "typed parsing + exact execution" not at all —
   under the registered NLB-0 discipline (ASM-0944, inherited by ASM-1039)
   pilot thresholds are STOP-SIGNALS routing to redesign, never mechanism
   evidence. Rev 2 already withdrew "cheap decisive" (R3, ASM-1039); CASK-PY/1
   re-asserts it under a new name.
2. **The vs-tool futility kill is biased AGAINST firing.** Condition 4 (UB95
   of the paired advantage < +5 → kill) reads on a *pilot-strength* tool arm —
   which the proposal admits. An under-built comparator makes the futility
   kill too easy to survive: survivorship bias TOWARD the expensive rung, the
   opposite of conservative. Symmetrically, an under-trained CASK front-end
   can false-fire it. Neither direction is mechanism evidence.
3. **Statistics are unclustered.** 3 phrasings per base task are correlated;
   a "paired 95% bound" without base-task-level clustering overstates n ~3×,
   so both the kill and its survival read wrong. The ASM-1034 machinery
   (paired hierarchical cluster bootstrap; TOST/NI for the 2-pt legs; CP only
   for single-arm rare-event legs) must apply verbatim.
4. **Not cheap on the binding resource.** "≤5 GPU-hours" prices compute; the
   programme's MEASURED binding constraint is human annotation
   [MEASURED: docs/next/feasibility-synthesis.md §6]. ~300 base tasks × 3
   independently-authored phrasings ≈ 900 items across 10–15 held-out repos,
   with adjudicated **query-level** gold (a callers-of gold set is a
   whole-repo judgement), ambiguity/answerability labels, AND edit-patch gold
   + hazard-scan audits. By the G1 repricing arithmetic (~200 queries ≈ 70–130
   annotator-hours, ASM-1038), this pilot is order **200–500 annotator-hours —
   several $k**, i.e. the same class as G1 + G2 + a slice of G4 combined.
   Billing it "cheap" repeats rev-1's R7 cost error in a new location
   [ESTIMATED arithmetic, flagged as such].
5. **It collapses the ladder's ordering.** Folding the census endpoints
   (completeness/negative-answer audits, dynamic-trace soundness) into the
   pilot loses exactly what census-first buys: a ~70–130-hour kill of the
   whole domain BEFORE any parser is trained, any phrasing authored, any tool
   arm built. It also shrinks the repo pool (10–15 vs the pinned 20–30) and
   silently deletes G3 (the registered G-NLB parser gate) from the path.
6. **The kill list is asymmetric.** Four enumerated kills read on CASK's own
   performance; the deflationary condition — GEN-EXEC/SQLite within the NI
   band ⇒ the special executor/store contributes nothing — appears in prose
   but NOT in the kill list. At pilot scope it can only be a routing signal
   (ASM-1032), but it must be an enumerated stop-signal with the same status
   as the others. Also missing: the deranged/shuffled-store control (house
   discipline from the f2b derangement lesson; ~free) and any RAG cell.

**Net:** as a SCREEN, the micro-G4 pilot is well-shaped and close to the
registered merged G2 + G1 endpoints. As "the decisive cheap falsifier" it is
neither decisive nor cheap, and the coordinator should strip the billing while
keeping most of the content.

---

## 3. Does it beat a matched generic tool-use baseline at equal budget, or assert it?

**It asserts, with unusually good manners.** The mechanism story (one
discriminative pass vs repeated autoregressive plan/serialize/interpret;
cannot emit invalid calls; amortized structure) is plausible engineering logic
— and carries **zero measured support**: no registry number bears on it, and
the internal RAG lit review's headline is that **no bytes-honest published
small-model retrieval/tool win exists to cite** [LIT-BACKED via CODEVERT
§4.2(2) / RAG.md §1]. The proposal earns credit for (a) naming the strong
comparator set (best local ≤360M tool-caller at the same byte/RSS/latency/
tuning budget, no gold contracts; BM25 + small-dense RAG cells; the
identical-front-end→SQLite deconfound), (b) pre-registering its own deflation
("equivalence within the preregistered margin kills the distinctive
architecture claim even if CASK remains a useful engineering product"), and
(c) scoping the win sentence narrowly. That is a designed test, not a hollow
assertion. Three gaps keep "equal budget" from being real yet:

1. **No builder machinery.** "The best local ≤360M tool-calling model" is a
   weak-control gaming surface unless the comparator is built by the FRONT/1
   pipeline under the T_k meter, pinned harness defaults, nomination window +
   challenger gate, and published build logs (RAGC §2.4 counters). The
   proposal never invokes any of this. Equal-GPU-hours is also not
   equal-maturity: 5 GPU-h near-converges an encoder-classifier and barely
   touches tool-use tuning of a 360M decoder — matched compute, unmatched
   recipe fit, disclosed nowhere [OPINION].
2. **Budget-vector shopping risk (the one place the win could be
   manufactured by construction).** If warm CPU p95 ≤ 500 ms is a B_k
   admission criterion, the strongest generic decoder may be excluded before
   the comparison starts. FRONT §1.2's derivation rule exists precisely for
   this; the synthesis must either derive the latency cap by rule or run the
   generic arm at its native latency and report the frontier point with the
   cap as a separate disclosed dimension.
3. **The final claim is only available at the expensive rung.** By the
   proposal's own admission the pilot cannot establish it, and the pilot's
   tool arm is pilot-strength. So the honest current status of "beats a
   matched generic baseline" is: **an open empirical question with a
   well-specified test and an honest deflationary branch — nothing more**
   [UNMEASURED].

---

## 4. Top failure modes the proposal under-weights

It names three good ones (static-coverage collapse, agreement laundering,
generic-arm parity) with real counters. Under-weighted:

1. **Annotation-cost blindness** (§2 item 4) — the binding resource is priced
   nowhere; every cost sentence in the proposal is GPU/latency-denominated.
   This is the programme's ONE measured resource finding and the proposal
   walks past it.
2. **False-kill / false-survive from budget-confounded pilots** (§2 items
   1–2) — the pilot can neither kill the mechanism nor clear it; the proposal
   sometimes says so and sometimes doesn't.
3. **Latency-cap comparator exclusion** (§3 item 2) — the only place the
   design could win by construction rather than by measurement.
4. **Common-name trie blowup.** Real repos are saturated with `run`, `main`,
   `test`, `__init__`, `setup`. Trie collisions add all type-valid bindings;
   the ≤8-contract cap then forces abstention on exactly the most common
   identifiers, and the ambiguity-set mechanism's headline benefit
   (set-execution ≥ +5 over top-1) could invert into a coverage tax.
   Unmeasured; cheap to census in G0/G1 (identifier-collision histogram per
   repo) [UNMEASURED; OPINION].
5. **Edit-gold cost + hazard-scan false negatives in the first scored run.**
   The 15% edit stratum needs patch-level gold and a blind hazard-scan audit
   (H5's "exact-identifier string anywhere in source/config" scan alone will
   dominate false-positive abstention on short names — also unmeasured).
   Rev 2 demoted the edit path to design-track-until-G4 (ASM-1037) for
   exactly this reason; CASK re-promotes it without new evidence.
6. **Grammar-relative retention.** Training on synthetic grammar
   recombination and evaluating on phrasings authored over the same closed
   grammar means every retention number is grammar-relative; naturally
   occurring developer queries are out of scope of ANY rung of this design.
   Disclosed once (final paragraph); must ride every readout (ASM-0945
   discipline).

---

## 5. KEEP / DROP / CHANGE, and the single most valuable next step

**KEEP (absorb into the synthesis where not already registered):**
- The convergent core — it is the registered CODEVERT/1 rev-2 stack and its
  independent re-derivation is the strongest available evidence the rev-2
  corrections are stable [OPINION].
- **The empty-agreement→CLARIFY acceptance rule** — an executable upgrade of
  a rev-2 disclosed residual. Adopt into the acceptance-layer spec
  (amendment to ASM-1001's acceptance semantics; coordinator registers).
- **The `UNKNOWN_INCOMPLETE(partial_lower_bound, blocking_count)` API shape**
  — cleaner than rev-2's prose; adopt as the pinned output schema (ASM-1031).
- The abstention-cost honesty (§ final), the narrow win sentence, and the
  named product-loss inventory (framework-heavy Python, descriptive
  references, small repos in-context, one-off queries).

**DROP:**
- The "single most decisive cheap falsifier" billing — G2-class rungs are
  screens; ASM-1039 stands. No rung is both cheap and decisive.
- Edits from the first scored pilot (design-track until G4; ASM-1037 stands).
- The standalone pilot front-end/corpus — the front-end IS NLB-FE/1 on the
  code vertical and the pilot IS the merged G2 (ASM-1001/1005); CASK-PY/1
  never mentions NLB-FE/1 and would rebuild the duplication rev-1 removed.
- "…or sharded" (repo-cap handling) unless cross-shard `unknown` semantics
  are pinned.

**CHANGE:**
- Reprice the pilot in annotator-hours (order 200–500 h as proposed; ~½ that
  if edits drop and phrasings reuse the merged-G2 authoring); restore
  census-first ordering (G1's ~70–130 h can kill the domain before any model
  exists).
- Cluster the statistics at base-task level per ASM-1034; state the NI legs.
- Add the deranged-store arm and the GEN-EXEC NI stop-signal to the
  enumerated kill list.
- Derive B_k (esp. the 500 ms cap) by FRONT §1.2's rule; never as a
  comparator filter.
- Pin the scripted clarification protocol and author-blindness at eval.
- Build TOOL-NL under FRONT/1 + RAGC §2.4 (T_k meter, harness defaults,
  challenger gate, published logs).

**Single most valuable next step (unchanged by this proposal):** run **G0 —
the authorized NON-SCORED PY-STAT/1 extractor spike + extractor-independent
census tooling** (P3-T-CODEVERT-XT), now extended with two cheap additions
from this critique: the identifier-collision histogram (§4.4) and a
bytes-per-edge / p95 measurement on the pinned rig to replace the [UNMEASURED]
envelope arithmetic. It is the only work externally authorized, it feeds every
kill floor, and it converts the largest block of [UNMEASURED] claims in BOTH
documents into numbers before any annotation dollar or GPU-hour is spent.

---

## 6. Flag list — every proposal claim needing a measurement we don't have

| # | Claim (as made in CASK-PY/1) | Missing measurement |
|---|---|---|
| 1 | 110M parser approaches 0.90-retention/S2 after synthetic+paraphrase training | G2/G3 themselves; no cited work reports it (proposal concedes — keep the tag) |
| 2 | Independent coverage ≳0.5 on real Python repos ("product claim should die" below it) | G1 κ_q^indep; floor itself is a planning value |
| 3 | ~256 MB facts+indexes for repos in band; ≤0.75 GB packed total | G0 bytes-per-edge on real repos; canonical packing run |
| 4 | Warm CPU p95 ≤500 ms for int8 110M + heads + constructor | P3-D-HW pinned-rig measurement |
| 5 | Extraction amortizes over repeated repository use | KOT-LIFE/1 amortization at pinned volumes; no query-volume model exists |
| 6 | Clarification caps 0.05/0.20 and λ=0.25 as workable operating values | Nothing — planning values (mirror ASM-1033's [ESTIMATED] tags) |
| 7 | 70/15/15 workload mix | Stipulated; no measured developer-demand distribution |
| 8 | Ambiguity-set adds ≥5 pts safe coverage over top-1 | G2 arm contrast; also threatened by the §4.4 collision blowup |
| 9 | "A negative pilot can cheaply kill the proposed mechanism" | Nothing can — at ≤5 GPU-h it kills the instantiation-at-budget only (ASM-0944/1039 discipline) |
| 10 | Beats best local ≤360M tool-caller at equal budget | G4 only; no published bytes-honest precedent; comparator must be FRONT-built |
| 11 | Hazard scan H1–H8 has acceptably low false-positive abstention (esp. H5 on short names) | G5a blind audit; no rate measured in either direction |
| 12 | 10⁴–10⁵ synthetic examples suffice within the ≤5 GPU-h pilot allowance | Pilot itself; training-curve unmeasured for this grammar |

---

## Epistemic register

- **[MEASURED] consumed (each inside its envelope):** f2b-transfer stage-1
  endorsement A=0.9784 / LB 0.9606, adjudication_valid — gold-authority axis
  ONLY, no evidence for code extraction or NL entry; coverage census
  STILL-INCOMPLETE + NO-KILL as re-scoped by rev-covcensus (D3 upper-sieve
  lane; general index not killed, not enumerated); a5-nl 41.6% + S2 kill;
  l3a-parse 47.6%, paraphrase 0/261; f2b-replicate +0.1507 / LB +0.1053 at
  cost 0.103; g8 0/1000; m0b 0.3542 (corpus-indexed, ASM-0001); engine
  5.29–7.82 µs / Tier-0 250–267 µs timings; annotation-as-binding-resource
  (feasibility-synthesis §6).
- **[STIPULATED] consumed:** ASM-1000–1008 + PROPOSED-ASM-1030–1039
  (CODEVERT rev 2); ASM-0903/0905/0940–0947 (NLB); ASM-0852/0853 + FRONT §1.2
  derivation rule; ASM-0921/0922/0950–0957 (RAGC); ASM-0810 (KOT-SIZE/COST/
  LIFE); ASM-0007, ASM-0001.
- **[ESTIMATED] introduced here:** the 200–500 annotator-hour pilot repricing
  (derived from ASM-1038's G1 arithmetic, scaled; no measurement).
- **[OPINION]:** all KEEP/DROP/CHANGE judgements, the convergence-as-evidence
  reading, the collision-blowup and latency-cap-shopping risks (both flagged
  as needing cheap measurement, not asserted as facts).
- Nothing in this critique licenses any claim about kernel CONTENT; a
  CODEVERT/CASK win in any form remains an architecture-family result
  (ASM-1000).
