# FABLE INTERPRETATION — g3-llmproxy-v3 (mechanical verdict: FAIL; instrument: VALID)

- **Author:** Fable (chief architect), 2026-07-11. This is the interpretive assessment the
  frozen record's stage discipline calls for ("verdict-gen → … → Fable interpretive
  assessment"). The coordinator computed the mechanical verdict; I own the epistemic
  reading. This document changes NO frozen record, NO verdict object, NO log, NO analysis
  output, and NO registry assumption; it runs no experiment.
- **Sources (read at source, in full):** `registry/verdicts/g3-llmproxy-v3.json`
  (verdict FAIL, computed 2026-07-11T10:37:19Z, fired rule `/analysis/proxy_fail`;
  envelope + kill criterion read verbatim), `reports/auto/g3-llmproxy-v3/analysis-output.json`
  (sha256 553cd50b…, matching the verdict's pin), `registry/experiments/g3-llmproxy-v3.json`
  (FROZEN, sha256 f8725577…), `docs/next/feasibility-synthesis.md` (the capstone), and the
  cited assumptions ASM-0530/0531/0532/0533/0534/0550/0552/0553/0650/0651/0740/0741.
- **Epistemic discipline:** every load-bearing line carries its `[TAG: ref]` on the same
  logical line. **MEASURED** restates a measured fact strictly within this record's own
  envelope; **STIPULATED** marks framing choices; **EXTRAPOLATION** is direction-only and
  never load-bearing. The extrapolation envelope below is BINDING on every number cited
  here; any citation of these figures elsewhere inherits it.

---

## 0. The mechanical facts, restated inside the envelope

PREMISE: [MEASURED: registry/verdicts/g3-llmproxy-v3.json + reports/auto/g3-llmproxy-v3/analysis-output.json] Over the 200 pinned instances (20 non-knownWeak kernel-v0 concepts × 10), 195 were dual-decisive (floor 170 met); the CONCORDANT necessity-violation rate — both blind judges independently deriving q1=yes ∧ q2=no on the same item — is 36/195 = 0.1846, one-sided 95% Wilson LB 0.1433 > 0.10, so the pre-declared FAIL-analog fired under the bracket rule's LEAST favourable combination for FAIL. The UNION rate is 70/195 = 0.3590 (Wilson UB 0.4171), so no PASS-analog was reachable either. Per-judge necessity rates: judge-pA (GPT-5.6-Sol) 0.2410, judge-pB (Haiku 4.5) 0.3026.

PREMISE: [MEASURED: same sources — instrument gates] The instrument is VALID on every pre-registered gate: `adjudication_valid` and `probe_valid` both true; κ_pair 0.5616 (> the 0.4 instability trip); probe-B false-satisfaction 1/30 = 0.0333 per judge (bar 0.30); escapes tiny (worst cell: judge-pB pass-A cannot-say 0.025; no-label 0 everywhere). The FAIL is a clean reading of a working instrument, not a degeneracy.

PREMISE: [MEASURED: same sources — secondary] Sufficiency straddles its own bracket: concordant UB 0.0901 (≤ 0.10) but union UB 0.1727 (> 0.10), so `sufficiency_equivalence_survives_proxy` = false under its pre-declared union rule; never verdict-bearing. The pass-B failing-cid histogram spreads across clause positions (c1 38, c2 59, c3 40, c4 52, c5 15) — reported-only taxonomy seed for the human round.

PREMISE: [MEASURED: verdict object, mandatory restatement] Coverage 0.3542 at rung molecules-v0, measured by m0b on one incomplete kernel-v0 instance; `rungs_measured: none`; `scale_language_licensed: none`; audit N/A per the record (mechanical recomputation path per its stage discipline).

---

## 1. What the FAIL means — precisely, and only this

LOAD-BEARING: the FAIL-analog means exactly this and no more: a blind, cross-family, pinned LLM pair (GPT-5.6-Sol + Haiku 4.5), filling the two-human g3.annotate GATE-H role as a WEAK FEASIBILITY PROXY, judged — under the frozen two-pass blind rendering, on the 200 pinned instances, with all instrument gates green — that in at least 14.3% of dual-decisive instances (Wilson LB; point 18.5%) the target claim is TRUE in ordinary usage while at least one of the kernel's enumerated conditions FAILS on a literal reading, with BOTH judges independently concurring per item [MEASURED: verdict FAIL within the extrapolation_envelope_verbatim; proxy status STIPULATED: ASM-0550/0530]. That is the g3-kill early-warning ANALOG at this proxy id: the kernel's condition scripts, read literally, were judged NOT necessary for ordinary-usage truth at nearly twice the frozen 10% survives-bar, even under the conservative concordant count.

LOAD-BEARING: what it does NOT license — each item verbatim from the binding envelope [STIPULATED: ASM-0550 — the shared weak-proxy stand-in policy, plus extrapolation_envelope_verbatim clauses 3–5, restated without widening]:

- It does NOT adjudicate HS3. The HS3 estimand is native-speaker HUMAN competence; these rates ARE two LLMs' judgments [STIPULATED: envelope preamble; ASM-0532].
- It does NOT resolve HS2, does NOT prune or un-prune g5, does NOT demote or confirm Π beyond lint. HS2 auto-resolution, g5 pruning and Π demotion can be triggered ONLY by the human-annotated g3 [STIPULATED: kill_criterion_verbatim].
- It does NOT substitute for the GATE-H human annotation. g3 (frozen_sha256 ef9608c6…) remains FROZEN, unconsumed, and is the ONLY experiment on this line whose readout adjudicates HS3 [STIPULATED: envelope preamble; ASM-0553 quarantines proxy labels from any future human annotator].
- It does NOT extend to human annotators, other concepts, other instance distributions, or ANY coverage-general claim (coverage 0.3542 at molecules-v0, one incomplete kernel-v0 instance) [STIPULATED: envelope clause 5; MEASURED: m0b].
- It can neither FIRE nor DISCHARGE g3's own human kill ("necessity failures >10% ⇒ defeasible-script stands, Π is lint, HS2 auto-resolves sidecar-only") — the mirroring is in FORM ONLY [STIPULATED: kill_criterion_verbatim].

LOAD-BEARING (instrument asymmetry the reader must carry): the probe-B gate bounds only the FALSE-SATISFACTION channel — the failure mode that would FABRICATE A LOW violation rate (a spurious PASS). Nothing in the instrument bounds the opposite channel: hyper-literal FALSE NON-SATISFACTION, which would INFLATE the violation rate toward a spurious FAIL [MEASURED: probe construction per ASM-0534 — correct answer 'no' by construction, only q2=yes counts as false satisfaction; the inflation channel is exactly the pass-B literalism direction ASM-0532 leaves UNPROVEN]. The FAIL direction's conservatism therefore comes entirely from the CONCORDANT bracket (ASM-0531) — both judges, independently, per item — not from any probe. Cross-family concordance at 0.1846 with κ 0.56 makes a single judge's idiosyncratic literalism an unlikely sole cause, but a COMMON-MODE literalism offset shared by two web-scale-trained LLMs is uncontrolled and explicitly disclosed [STIPULATED: envelope clause 2 — κ is judge-pair stability, never human-agreement evidence; both judges share ordinary-language training exposure; judge-pB's vendor family overlaps the materials' authors, disclosed]. The low sufficiency-concordant rate (0.056) is CONSISTENT with global pass-B hyper-literalism (fewer q2=yes overall deflates sufficiency violations too) and so does not discriminate; nothing here can [EXTRAPOLATION: diagnostic reading of the secondary rates, never a premise].

---

## 2. The asymmetric reading (envelope clause 6) and the programme response

LOAD-BEARING: because the LLM-vs-human offset direction is UNPROVEN here — unlike the endorsement-style proxy records, where the disclosed channels push one known way — the envelope pre-assigned the conservatism to the bracket rule, and it pre-declared how each outcome reads: a FAIL-analog (concordant LB > 0.10 despite the LOWER bracket) is a STRONG EARLY WARNING; a PASS-analog would have licensed only continued investment and upgraded nothing [STIPULATED: ASM-0531 — the pre-declared bracket rule carries the conservatism; extrapolation_envelope_verbatim clause 6, restated]. This run produced the strong-early-warning branch, and not marginally: the LB clears the bar by 4.3 points, the point estimate by 8.5, and the FAIL-analog decidability threshold (~27 concordant violations at n=195) was exceeded at 36 [MEASURED: analysis-output + the record's decidability note].

DECISION (the response the envelope and kill criterion specify, executed at exactly their scope): **pause Π-hardening investment and escalate to the maintainer, formally scoped to this proxy id** [STIPULATED: kill_criterion_verbatim — "A proxy FAIL-analog warrants pausing Pi-hardening investment and escalating to the maintainer, formally scoped to this proxy id"; envelope clause 6 concurs]. Concretely, and mirroring the ASM-0648 precedent from the g9-llmproxy FAIL-analog: no new spend on hardening Π (the necessity-conditions read-out line) beyond its current lint status until the maintainer weighs in; the human g3 (GATE-H) is NOT accelerated, decelerated, or altered by this — its record, materials pins and open decisions stand exactly as frozen [STIPULATED: ASM-0553 non-contamination; the operationalisation itself is proposed for registration below, not registered here]. What the FAIL does NOT pause: the human-annotation sourcing effort itself (O-3), which this result makes MORE valuable, not less — the human round now also prices a pinned per-item human-vs-proxy bias measurement for free [STIPULATED: ASM-0553; envelope clause 7].

---

## 3. Bearing on the correctness thesis — a distinct wall, not another brick in the same one

The capstone's governing shape is the reachability-wall-on-coverage-wall: the machinery is exact inside its own closed grammar (l3a 600/600, a5 855/855, cross-vendor CONFIRMED), and every measured crossing into real or natural input has been negative or inconclusive (l3a-parse FAIL 47.6%, a5-nl FAIL 41.6% with the dangerous-wrong kill fired, g8 FAIL 0/1000, nsk1 INCONCLUSIVE) [MEASURED: each figure index-bound to its own verdict per the capstone §1; the conjunction is EXTRAPOLATION per ASM-0762/0721, direction-only].

LOAD-BEARING (interpretive framing, direction-only — never a premise): g3-llmproxy-v3 is NOT another instance of that same wall, and folding it in would blur a distinction the programme needs. The NL-boundary FAILs are REACHABILITY failures: natural language could not reliably ADDRESS content the kernel demonstrably contains and decides perfectly under gold parse — the semantic commitments themselves were never tested (the capstone is explicit that l3a/a5 exercised the FORMALISM, not the NSM SEMANTICS; ASM-0004/0007). This proxy tests the previously untested flank: the CONTENT VALIDITY of the condition scripts themselves — whether the kernel's clause-wise necessary conditions actually match ordinary usage of the concepts, on instances rendered blind, with no parser anywhere in the loop [STIPULATED: this framing; MEASURED: the design has no host model, no parse step — item bytes byte-identical to the pinned human materials]. A necessity violation here means: ordinary usage counts the claim TRUE while the kernel's script says a condition literally fails — the script OVER-SPECIFIES relative to usage. That is a defect (if it survives human adjudication) in what the kernel SAYS, not in what can reach it [EXTRAPOLATION: mechanism reading; the human g3 is the adjudicator].

LOAD-BEARING (the honest cross-reading, direction-only): at proxy strength, the programme now has its FIRST measured signal on the semantics-content leg of the correctness thesis, and it points the same way as every other contact with ordinary/real input: negative [EXTRAPOLATION: extends the ASM-0721/0762 boundary-pattern reading to a THIRD, distinct axis — a content wall alongside the coverage wall and the reachability wall; never a premise, load-bearing for nothing, and doubly weakened here because the constituent is itself a weak proxy under ASM-0532's unproven offset]. Two features sharpen the warning without upgrading it: (i) the 20 concepts are a FAVOURABLE slice (non-knownWeak kernel-v0 concepts, per the record's own coverage disclosure), so this is not an adversarial concept selection [MEASURED: record assumption, restated]; (ii) the failing-cid histogram spreads across all clause positions rather than concentrating in one reparable clause, suggesting — if the human round concurs — distributed over-specification rather than a single bad clause pattern [MEASURED: histogram; the "distributed over-specification" reading is EXTRAPOLATION, reported-only diagnostics]. And one feature bounds it: everything rides on LLM literal-reading behaviour whose offset from human judgment is unproven in DIRECTION, so the true human rate could sit below the bar; that is precisely why this record can only warn, never kill [STIPULATED: ASM-0532; envelope clause 1].

The g2 dependency chain makes the warning operationally significant even at proxy strength: g3 gates g2 (Π read-out soundness vs human gold), and g2 is one of the two decisive unrun legs of the correctness verdict [MEASURED: capstone §3/§5]. If the human g3 lands where the proxy points, the frozen consequence is "defeasible-script stands, Π is lint, HS2 auto-resolves sidecar-only" — a materially weaker semantics story than the equivalence reading. Spending on Π-hardening before the human round would be spending against the current evidence gradient; that is exactly what the pre-registered pause prevents [STIPULATED: response scoped per §2; EXTRAPOLATION: the gradient reading].

---

## 4. CAPSTONE DELTA — recommendation only (do NOT edit feasibility-synthesis.md here)

DECISION (recommendation only, applied by the coordinator or a later synthesis pass — this document does not modify the capstone): [STIPULATED: consistent with the capstone's own maintenance discipline under ASM-0761] The capstone (`docs/next/feasibility-synthesis.md`) should incorporate g3-llmproxy-v3 as follows:

1. **Completeness ledger — move the row from PENDING to DONE.** §3's PENDING table currently carries "g3-llmproxy-v3 | DRAFT, proxy re-run IN-FLIGHT (blinding-scan fix, ASM-0740/0741) | correctness semantics (g3 necessity) | Refine only." Replace with a DONE row: `g3-llmproxy-v3 | FAIL (proxy FAIL-analog) | (proxy; verdict computed, interp done) | correctness semantics (g3 necessity), weak proxy; human g3 pending` — symmetric with the existing g9-llmproxy row. The g3 (human) row in PENDING stands unchanged.
2. **§1 Claim C2 — add a sixth measured-boundary bullet**, parallel to the g9-llmproxy bullet: semantics-content PROXY, FAIL-analog — concordant necessity-violation rate 0.1846 (Wilson LB 0.1433 > 0.10) from a blind cross-family LLM pair on the 200 pinned g3 instances; weak proxy (ASM-0550), cannot fire or discharge g3's kill; response: Π-hardening paused, maintainer escalated, scoped to the proxy id. It should be flagged as a DISTINCT failure axis (content validity of the condition scripts) rather than another reachability instance — the §0 "reachability-wall-on-coverage-wall" prose gains a third named wall (content wall) only as EXTRAPOLATION, via a successor or extension to ASM-0762 (assumption registration is the coordinator's, not mine — see PROPOSED-ASM below).
3. **§4 strongest defensible NEGATIVE (correctness) — append** "…and the first measured signal on the semantics-content leg (g3 necessity, at weak-proxy strength) is also negative" with the proxy caveat inline.
4. **§5 next decisive experiments — unchanged in content, sharpened in motivation**: the g2/g3 human leg was already listed; the proxy FAIL raises its information value (it now also buys the human-vs-proxy bias measurement, ASM-0553) and the Π-hardening pause removes a competing spend.
5. **The INCONCLUSIVE-PENDING correctness verdict does NOT reverse, and must not.** The capstone's own DECISION (ASM-0761) pre-committed that this proxy "can neither fire nor discharge g3's own kill; cannot reverse the correctness verdict" — the outcome confirms that call was scoped correctly. The verdict's two decisive legs (g2 soundness, an NL-reaching parser) remain unrun, not failed; a weak proxy with an unproven-direction estimand gap cannot move a thesis-level verdict [STIPULATED: envelope clauses 1, 5, 6]. What it DOES do, within evidential limits: it strengthens the negative real-input picture directionally — the correctness thesis previously had a wall of negatives on reachability and coverage with the semantics core dark; the semantics core now has a first, weak, negative light on it. The honest phrasing for the capstone is: "the pending human g3 is now a warned leg, not a dark one" [EXTRAPOLATION: direction-only, never a premise].

---

## 5. Epistemic register (what this interpretation relied on)

- **MEASURED, never widened:** every rate, bound, κ, gate, histogram and coverage figure in §0–§3, each strictly inside `extrapolation_envelope_verbatim` of the verdict object.
- **STIPULATED, adopted verbatim from the frozen record:** the weak-proxy status (ASM-0550/0530), the bracket rule and its conservatism assignment (ASM-0531), the estimand gap with unproven offset direction (ASM-0532), probe construction and its one-sided channel coverage (ASM-0534), non-contamination/comparator discipline (ASM-0553), tradition familiarity (ASM-0552), the v2/v3 supersession fixes (ASM-0650/0651/0740/0741), and the FAIL-analog response (kill_criterion_verbatim + envelope clause 6).
- **EXTRAPOLATION, direction-only, load-bearing for nothing:** the "content wall" third-axis reading (§3, extending ASM-0721/0762), the distributed-over-specification reading of the cid histogram, the hyper-literalism non-discrimination note, and the "warned leg" phrasing recommended for the capstone.

---

## PROPOSED-ASM (coordinator to register — NOT written to registry/assumptions.jsonl by this document)

- **PROPOSED-ASM-A (response operationalisation, mirrors ASM-0648):** "g3-llmproxy-v3 FAIL-analog response operationalisation (executes the frozen kill-criterion/envelope-clause-6 response at exactly its frozen scope): (a) Π-hardening investment is PAUSED — no new design, engineering, or spend on strengthening the necessity-conditions read-out line beyond its current lint status — pending maintainer input; (b) the pause is formally scoped to proxy id g3-llmproxy-v3 and is lifted or converted only by the maintainer or by the human-annotated g3 readout; (c) the human g3 record, its GATE-H path, materials pins, and open decisions are untouched; human-annotator sourcing (O-3) is explicitly NOT paused; (d) proxy labels remain quarantined from any future human annotator per ASM-0553."
- **PROPOSED-ASM-B (cross-reading extension, successor/extension to ASM-0762):** "Content-wall extension of the boundary-pattern reading (interpretive colour only; never a premise, load-bearing for nothing): alongside the coverage wall and the reachability wall, the first measured signal on the semantics-content axis — whether the kernel's condition scripts match ordinary usage — is negative at weak-proxy strength (g3-llmproxy-v3 FAIL-analog, concordant LB 0.1433), on a favourable concept slice, with the offset direction to human judgment unproven (ASM-0532); the axis is DISTINCT from parser fidelity and is adjudicated only by the human g3."

---

*This interpretation changes no frozen object, no verdict, no log, no analysis output, and
no registered assumption. Next decisive step on this line: the human-annotated g3 (GATE-H),
which both adjudicates HS3 and prices the proxy's bias against pinned per-item labels.*
