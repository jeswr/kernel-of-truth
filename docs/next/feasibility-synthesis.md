# Cross-experiment feasibility synthesis — the programme's verdict on both value theses

- **Author:** Fable (`kern/fable-analyst`), 2026-07-11. This is the CAPSTONE — FABLE's
  definitive cross-experiment feasibility verdict on both value theses, the "Done"
  deliverable of the programme-completion loop (`docs/next/programme-completion-loop.md`
  GOAL). Opus never writes this conclusion; it reports mechanical facts. This document
  SUPERSEDES the 2026-07-10 INTERIM stub of the same path: the frozen set is now far more
  complete (the two NL-boundary FAILs, the a5-llm head-to-head, the truthstyle instrument
  PASS, the four weak-proxy stand-ins, and the A-E2 efficiency census all read out since),
  so the standing verdict below is the definitive current-evidence verdict, not an interim
  sketch.
- **Evidence base (all read at source):** every `registry/assessments/*.json`
  (a-e2-census, a5-llm, a5-nl, b-cov-define-lane, compression-census, define-op-census,
  f-efficiency, f2b-replicate, f2b-transfer-llmproxy, g-series, g8, g9-llmproxy,
  l3a-parse, l3a-parse-recoverability, m0a-llmproxy, nsk1-{stage1,bprime,bprime2,g2d},
  oracle-coverage, truthstyle-2x2); the verdict objects in `registry/verdicts/*.json`;
  the ledger `python3 tools/registry/audit-status.py`; `registry/frozen-index.json`;
  the frozen experiment records; and `docs/next/knull-plain-arm-quality.md` (the
  surface-realization gap finding). No registry record, verdict, correction, audit,
  frozen object, or ASM outside my reserved block is modified by this document.
- **Epistemic discipline (governance):** every PREMISE / DECISION / LOAD-BEARING line
  carries its `[TAG: ref]` on the same logical line. I own the tags and the conclusion.
  **MEASURED** restates a measured fact strictly within its own verdict's envelope; a
  MEASURED number cited outside its envelope re-classifies as EXTRAPOLATION (engine law 9).
  **Cross-experiment readings are EXTRAPOLATION** — direction-only, never a premise for a
  verdict. **STIPULATED** marks scoping / decision choices I make here. Negatives and
  nulls carry equal prominence with positives; a FAIL is scoped to its envelope, a
  PASS that is instrument-only is not a kernel-content win, and an efficiency upper bound
  is never achievable savings.

---

## 0. The one sentence that still governs everything

LOAD-BEARING: Across the entire registry there are ZERO audited end-task wins over the kernel-as-text null that are attributable to the kernel's content, and the question the whole programme exists to answer — *does grounding a model in the kernel make that model measurably more correct or more efficient at matched budget, on real input?* — remains, as of 2026-07-11, UNSETTLED on both theses [MEASURED: registry/assessments/oracle-coverage.json null-bound + registry/assessments/f-efficiency.json — every end-task-adjacent verdict is either R0 (no host model), a landed FAIL, or a PASS confined to a self-authored oracle-favourable *formal* slice whose content-attribution is confounded].

The single most robust cross-experiment fact, and the one that shapes both verdicts:

LOAD-BEARING (direction-only): the kernel's deterministic machinery is EXACT and sound *inside its own closed grammar / self-authored substrate*, and every MEASURED crossing of a boundary into real or natural input either FAILs or is INCONCLUSIVE [EXTRAPOLATION: ASM-0762, extending ASM-0721; each figure is index-bound to its own verdict's envelope and this cross-reading is never a premise — machinery side l3a/a5 gold-replication identical 527/527 & 855/855, g8 F/B round-trip 33/33; boundary side (i) NL input l3a-parse 47.6% / a5-nl 41.6% both FAIL, (ii) wild-formal g8 0/1000 FAIL, (iii) model-internal nsk1 INCONCLUSIVE, (iv) compute-matched verifier-offload f2 FAIL].

I call this shape the **reachability-wall-on-coverage-wall**: there is a *coverage* wall
(does the kernel even contain the target — g8 0/1000, m0b 0.3542, compression-census
~0.6%, b-cov-define-lane 0/1,550) and, stacked on top of it, a *reachability* wall (even
for content the kernel demonstrably CONTAINS and CAN decide perfectly under gold parse,
natural language cannot reliably ADDRESS it through the pinned deterministic front-end).
The programme is much further along on *building a defensible checker* than on *showing
the checker reaches, or helps, anyone*.

---

## 1. CORRECTNESS thesis — the verdict

> **VERDICT (verbatim): INCONCLUSIVE — PENDING (a) an NL-reaching parser [FK-NLB-3] and (b) the semantics core [g2 Π-soundness vs human gold, g3 necessity]. The instrument sub-claim is FEASIBLE-and-DEMONSTRATED but INSTRUMENT-ONLY; every MEASURED crossing from the instrument into real or natural input is, so far, NEGATIVE. SCOPE: the kernel-v0 / molecules-v0 instance, R0–1.7B hosts, the two tested verticals (family/world, code), the one pinned a1-hybrid deterministic front-end, the self-authored covered slice. CONFIDENCE: high on the instrument sub-claim (cross-vendor CONFIRMED); high that the current-build NL boundary and wild-formal boundary are negative at scope; the thesis-level verdict is INCONCLUSIVE because its two decisive legs (semantics core, a better parser) are unrun, not failed.**

The thesis decomposes into two claims that the evidence separates cleanly, and honesty
requires keeping them apart:

**Claim C1 — "a training-free deterministic engine that grounds/checks claims EXISTS,
is sound where covered, fails closed off it, and ports across domains" — FEASIBLE,
MEASURED, cross-vendor CONFIRMED, but INSTRUMENT-ONLY.**

PREMISE: [MEASURED: registry/verdicts/l3a.json + registry/verdicts/a5.json, both audit CONFIRMED; registry/assessments/oracle-coverage.json] The kot-axiom/1 v0 engine is exact and fail-closed on its covered slice at microsecond cost and ports across a domain vertical with a BYTE-IDENTICAL engine binary: l3a (family/world, R0) 600/600 covered-exact (Wilson LB 0.9955) + 300/300 strict refusals (LB 0.9911) + 6/6 planted violations surfaced + 5.29 µs/query; a5 (code, R0) 855/855 covered-exact (LB 0.9968) + 122/122 strict refusals (LB 0.9783) + 3/3 planted violations + 7.82 µs/query, engine byte-identical to the l3a pin and extended only by data + a pure desugaring layer over a no-LLM-extracted code world.

LOAD-BEARING: This is the strongest, cleanest evidence in the whole registry — and it is evidence about the INSTRUMENT, not about usefulness to any model [MEASURED: both evals are authored against the engines' own stores ("coverage by construction"), so exactness is a consistency-and-licensing property, never world-accuracy; both verdicts are R0 with scale_language_licensed = none; and the a5 map is STRUCTURAL definitions not NSM explications (ASM-0007), l3a directions are stipulated readings (ASM-0004) — the results exercise the FORMALISM, not the NSM SEMANTICS].

**Claim C2 — "that grounding reaches real/natural input and makes a model measurably more
correct" — INCONCLUSIVE, and every MEASURED boundary crossing is NEGATIVE so far.**

The measured boundary results, at full prominence and each scoped to its own envelope:

- PREMISE: [MEASURED: registry/verdicts/l3a-parse.json, verdict FAIL] NL-boundary, family/world vertical: the a1-hybrid deterministic front-end retains only 251/527 = 47.6% of gold-parse covered exactness (Wilson UB 0.5121 vs the 0.90 bar) — a decisive FAIL. The mechanism is a STRUCTURAL paraphrase ceiling: the label-verbatim stratum parses 76.4% but the PARAPHRASE stratum parses 0/261 = 0.0% (single-label mapper, no synonym table). The failure is SAFE here — the S2 dangerous-wrong KILL did NOT fire (8/527 wrong, LB 0.0086 < 0.02); mis-parses become refusals.
- PREMISE: [MEASURED: registry/verdicts/a5-nl.json, verdict FAIL, two independent causes] NL-boundary, code vertical: 356/855 = 41.6% (UB 0.4443) — FAIL — AND the S2 dangerous-wrong KILL FIRED (43/855 = 5.0% wrong, LB 0.0394 ≥ 0.02). This is the DANGEROUS failure mode the design named worse than any refusal: the frame-layer ROLE_DIR direction table flips containment orientation (contained-in 24, where-defined 18) into a real-but-wrong answer *with provenance attached*. Same front-end as l3a-parse, opposite safety outcome, because on the code vertical the frame direction table carries the semantics.
- PREMISE: [MEASURED: registry/assessments/nsk1-{g2d,bprime2,stage1}.json — exploratory read (nsk1 record status DRAFT, no frozen verdict); the flagship's exploratory stages] Model-internal grounding, INCONCLUSIVE two-sided: text-delivered grounding is NET-HARMFUL (g2d: host composes 0.76 text-only, appending the engine's correct fact drops it to 0.43, 0/24 text-only failures rescued — a defective channel at every scale tested); the internal residual-stream channel DELIVERS at ECHO grade (keyacc 0.81/0.85, replicated across three derangement seeds) but whether that delivered content INTEGRATES into free generation is UNRESOLVED (the echo-proof R− rescue endpoint fired 0/8, at-or-below the content-free coin null; no KILL because the echo-confounded R+ endpoint sits above the kill bound). Delivery topology, not content, was the binding failure — now measured from both sides, and integration is not settled either way.
- PREMISE: [MEASURED: registry/verdicts/g8.json, verdict FAIL, audit CONFIRMED] Wild-formal-content boundary: the profile-M fragment captures 0 of 1,000 random Mathlib declarations (UB 0.0027 vs the 1% gate) and the locator places 5/39 math concepts in Mathlib top-5 (12.8% vs the 80% gate), wrapped around a clean machinery PASS (F/B round-trip 33/33). Lean-minting is DEAD AT SCOPE (kernel size 39, signature-layer extraction) with a pre-registered bulk-authoring re-entry — not dead as a formalism claim.
- PREMISE: [MEASURED: registry/verdicts/g9-llmproxy.json, verdict FAIL-analog] Authoring capability, PROXY: a kernel-instance-naive cross-vendor LLM reviewer endorsed the composite (substitutable ∧ cross-translatable ∧ legal) on 9/50 Fable-authored explication sheets (0.18; UB 0.2850 vs the 0.34 bar). WEAK proxy only (STIPULATED: ASM-0550) — it can neither fire nor discharge the frozen g9's own kill; the blinded HUMAN g9 (GATE-H) is the sole HS-A adjudicator and is UNRUN. Response: authoring-cost claims PAUSED, maintainer escalated [STIPULATED: ASM-0648].

The one PASS in the correctness neighbourhood is not a kernel-content win:

PREMISE: [MEASURED: registry/verdicts/truthstyle-2x2.json, verdict PASS, audit CONFIRMED] truthstyle-2x2 is an INSTRUMENT-ADEQUACY result: the LLM-judge style main effect at matched truth is +0.025 (90% interval [0.0033, 0.0467]), inside the ±0.10 margin — so LLM-judge endorsement is not materially style-leaky at that margin [STIPULATED: ASM-0680 consumption discipline — "style-robust AT MARGIN 0.10", never "zero style effect"; the measured effect is nonzero and NSM-favoring]. It scores ZERO kernel content (no endpoint measures gold agreement); it makes OTHER readings trustworthy, it is not itself evidence the kernel is correct.

The a5-llm head-to-head is real but is a substrate comparison on FORMAL inputs, and its
NL leg is now separately measured as a FAIL:

PREMISE: [MEASURED: registry/verdicts/a5-llm.json verdict PASS, audit CONFIRMED per ledger] On the pinned 977-query kot-query-code/1 slice the deterministic engine scored conj 1.0 vs the best gate-valid LLM cell 0.3398 (+0.6602, one-sided LB +0.6346) at cost_ratio_min 22,836× and fabrication 78.7% on controls vs the engine's 0/122. DECISION: [MEASURED: registry/assessments/a5-llm.json does_not_license — the assessment's own scope ceiling, adopted verbatim] this is "a deterministic engine over its own extracted typed records beats a small closed-book/RAG LLM on a self-authored oracle-favourable code slice whose queries are already FORMAL" — there is no NL, no parse step, and NO conventional-substrate arm, so nothing distinguishes the kot-axiom kernel from ANY typed store + checker; the NL leg a5-llm deferred is exactly what a5-nl now measures = FAIL, so no code-vertical NL-usefulness claim survives the a5-llm PASS [MEASURED: a5-nl.json tree_impact].

**The knull surface-realization gap — a named, unmeasured value gap the correctness thesis
must carry openly:**

LOAD-BEARING: the kernel's OWN definitional output is the NSM gloss verbatim (e.g. "this someone lives now; the body can move; this someone can feel something."); NO scholarly-English surface layer exists anywhere in the system, and no verdict licenses any claim that the system produces proper-English definitions [STIPULATED: ASM-0702 (knull scope audit) — NSM is a controlled metalanguage by design; a surface-realization layer (NSM record → edited English) is a missing, unmeasured programme-wide component, and its output when built falls under the maintainer's language-quality standard and needs its own blind quality gate]. Separately, the knull *plain-dictionary control* was measured mechanically defective (3/10 blind) which one-sidedly CONFOUNDS the un-run knull ablation toward a false content-win [STIPULATED: ASM-0700]; the rewrite is in flight on a maintainer-ratified split gate and the ablation itself is UNRUN.

---

## 2. EFFICIENCY thesis — the verdict

> **VERDICT (verbatim): INCONCLUSIVE — PENDING (a) de-confounding the one end-task positive [the knull K-NULL aligned-non-NSM ablation, or the human f2b-transfer Stage-1], (b) the mint-cost side [A-F0, key-gated unrun], and (c) the consumption channel [A-E2 K-A3/K-A4, unmeasured]. There is a real, audited efficiency SIGN on FORMAL inputs and a real, large membership UPPER BOUND from cross-lingual minting — but the one positive is correct-ALIGNMENT-specific (not shown kernel-content-specific), the compression number is an upper bound not achievable savings, and every cost + consumption side is unmeasured. SCOPE: ≤1.7B hosts, the self-authored covered/formal slice, one PRM size class, the 10k-concept census anchor. CONFIDENCE: high that a verifier-offload SIGN exists at scope; high that it is not yet attributable to kernel content; high that the compression figure is an upper bound only.**

The evidence, at full prominence:

**The one end-task PASS (verifier-offload) — real, audited, but attribution-confounded and
formal-only.**

PREMISE: [MEASURED: registry/verdicts/f2b-replicate.json, verdict PASS, audit CONFIRMED] SmolLM2-135M + kernel-verify-retry (fixed k=4) beats SmolLM2-1.7B-alone by +0.1507 absolute (one-sided 95% BCa LB +0.1053) at cost_ratio_vs_R3 = 0.103 (~10% of the 1.7B per-query cost); a seed-pinned derangement of the record→item map recovers ~0 of the lift (point −0.021), and the kernel arm beats gloss-self-verify (0.4893), the trained Skywork PRM-1.5B (0.5267), and the passive kernel-as-text null (0.4920).

LOAD-BEARING: this lift is correct-ALIGNMENT-specific, NOT shown kernel-content-specific, and its canonical de-confound has NOT read out [MEASURED: registry/assessments/f2b-replicate.json does_not_license — the verifier accepts iff the answer string-equals the canonical record and d-qa-r gold is DEFINED by that same equality, so under BOTH the real-content reading and the self-consistent-circularity reading a derangement destroys the lift; the shuffled control provably cannot discriminate NSM content from correct record↔item alignment. The open question is gold-label independence, and the only experiments that could settle it — the human f2b-transfer Stage-1, or the K-NULL aligned-non-NSM-store ablation (knull) — are unrun].

PREMISE: [MEASURED: registry/verdicts/f2b-transfer-llmproxy.json verdict PASS, audit CONFIRMED; STIPULATED: ASM-0022 weak proxy] The transfer stand-in reads A_1p = 0.95 (Wilson LB 0.9275 ≥ 0.70) — but it is a WEAK feasibility proxy: single LLM judge family (GPT-5.x), kernel-tradition (not instance) familiarity (ASM-0021), a letter-level circularity break at proxy strength only; it does NOT adjudicate H-TRANSFER vs H-CIRC, does NOT substitute for the human Stage-1, and licenses only continued investment. Its most durable value is as the pinned comparator the human round will difference against.

LOAD-BEARING: even at full strength the f2b efficiency line inherits the NL-boundary FAIL for any real (non-formal) deployment [MEASURED: f2b inputs are templated formal QA over the 108 covered concepts; the path from natural language to that formal slice is l3a-parse/a5-nl, both FAIL at scope — so the "135M+verifier beats 1.7B" economics are demonstrated only where the input is already formal].

Landed negatives on the same line, carried at full prominence:

PREMISE: [MEASURED: registry/verdicts/f2.json, verdict FAIL] The compute-matched f2 HE1 gap-closure primary FAILED as pre-registered (gap_closed_fraction −40.13) — diagnostically because its denominator was degenerate (R2-alone ≤ R1-alone, no s→S gap to close), but the FAIL stands unmodified. HE2 cascade-dominance is DEAD at scope (the verifier-gated cascade was not strictly dominant over the model's own free calibration baselines — logprob gate + gloss self-check).

**The compression / dense-I/O side — one audited model-free byte premise, and one large
but UPPER-BOUND membership census.**

PREMISE: [MEASURED: registry/verdicts/f1.json, verdict PASS, audit CONFIRMED] KOTK/2 entropy-columnar storage beats the compressed glosses-only text of the SAME records by 6.7369× bytes — but it is a premise-RETAINER, not an efficiency win: bytes alone were pre-declared unable to carry the M4 claim, the latency half is UNDECIDED (deferred to F5), there is no model/task/accuracy anywhere in f1, and the ratio extrapolates upward on store size only (contradicted at the 2.3k-record tier).

PREMISE: [MEASURED: registry/assessments/a-e2-census.json — a Tier-0 GATING census, NO frozen SAP, NO verdict object; every figure is an interpretive exploratory read, quarantined from every verdict chain] Cross-lingual minting (idea A) is ALIVE at the selection stage: the blended prefill-savings MEMBERSHIP bound at the 10k-concept anchor is ~18.5–24.0% (Qwen2.5 tokenizer) / 33.4–41.7% (SmolLM2), fertility-driven and concentrated overwhelmingly in non-English cells (English near the floor ~4–6%); the K-A2 5% floor does NOT fire anywhere. This is a stark contrast with the PARKED idea B (~0.4% word-mass, ~5× below its floor).

LOAD-BEARING: the A-E2 figure is a MEMBERSHIP UPPER BOUND and must never be quoted as achievable savings [MEASURED: registry/assessments/a-e2-census.json — exploratory census read; mappability (K-A4) is UNPRICED in every cell, and the entire consumption channel (K-A3 tokenizer-extension null, trained-compressor null, 1-token-per-concept delivery, accuracy non-inferiority) is ENTIRELY UNMEASURED]. The mint-cost side is also unmeasured [MEASURED: registry/experiments/a-f0-mint-economics.json — the direct Messages-API definer economics experiment is FROZEN but KEY-GATED unrun (its hard precondition is an Anthropic API key not present on the box), so mint-cost per legal record is unmeasured].

The mapper-quality measurement now exists but stands on a weak proxy:

PREMISE: [MEASURED: registry/verdicts/m0a-llmproxy.json PASS (instrument gates), audit confirmed; STIPULATED: ASM-0649] A blind cross-vendor proxy of the mapper's precision/recall EXISTS — strict P 0.7143, strict R 0.8419 — but it is a WEAK proxy pending the human M0a gold; the precision is ruled materially low (advisory early-warning: downstream mapper-consumers carry a "precision possibly ~0.7" risk line).

---

## 3. Completeness ledger — DONE vs PENDING, and reversal analysis

**DONE (mechanical verdict + cross-vendor audit + Fable interpretation) — 17 verdicted rows
+ the census/exploratory assessments:**

| record | verdict | audit | bears on |
|---|---|---|---|
| l3a, a5 | PASS | CONFIRM | C1 instrument exists (the substrate positive) |
| l3a-parse | FAIL (safe) | interp done | C2 NL boundary — decisive negative, family/world |
| a5-nl | FAIL (dangerous) | interp done | C2 NL boundary — decisive negative + safety break, code |
| g8 | FAIL | CONFIRM | C2 wild-formal boundary; Lean-minting dead at scope |
| g6 / g7 | INCONCLUSIVE / FAIL | done | formalism-capacity design selections, NOT semantics |
| g9-llmproxy | FAIL-analog | (proxy) | authoring capability, weak proxy; human g9 pending |
| truthstyle-2x2 | PASS | CONFIRM | instrument adequacy (style guard); zero kernel content |
| a5-llm | PASS | CONFIRM | substrate comparison on FORMAL inputs; NL leg = a5-nl FAIL |
| f1 | PASS | CONFIRM | efficiency byte premise (model-free, one corpus) |
| f2 | FAIL | (FAIL-no-audit) | compute-matched verifier-offload negative; HE2 dead |
| f2b-replicate | PASS | CONFIRM | the one end-task positive (alignment-specific, formal) |
| f2b-transfer-llmproxy | PASS | CONFIRM | weak transfer proxy (A_1p 0.95); not H-TRANSFER |
| m0a-llmproxy | PASS | confirmed | mapper P/R proxy (P~0.71); human M0a pending |
| m0b | PASS | CONFIRM | coverage 0.3542 (friendliest corpus, one instance) |
| a-e2-census, compression-census, define-op-census, b-cov-define-lane, oracle-coverage, g-series, f-efficiency, l3a-parse-recoverability, nsk1-* | (exploratory / census — no verdict object) | interp done | efficiency breadth bound; coverage gradient; the boundary picture |

**PENDING — and how each bears on the verdicts:**

| pending item | state | bears on | reversal power |
|---|---|---|---|
| **g3-llmproxy-v3** | DRAFT, proxy re-run IN-FLIGHT (blinding-scan fix, ASM-0740/0741) | correctness semantics (g3 necessity) | **Refine only.** A WEAK proxy that "can neither fire nor discharge g3's own kill"; cannot reverse the correctness verdict. |
| **knull** (K-NULL ablation) | FROZEN-UNRUN; plain-arm rewrite IN-FLIGHT (ASM-0700/0703), ablation itself unrun | efficiency — de-confounds the +0.1507 | **Verdict-moving, unrun.** Decides whether the one positive is kernel-content or generic aligned-key. The in-flight *rewrite* is control-quality repair, NOT a verdict; nothing to wait for yet. |
| **A-F0** (mint economics) | FROZEN, KEY-GATED unrun | efficiency — mint-cost side | Refine (prices one cost side). |
| **human g9** (GATE-H) | human-blocked | correctness — sole HS-A adjudicator | Verdict-moving on the authoring leg; g9-llmproxy stands in (FAIL-analog). |
| **human M0a** | human-blocked | efficiency/mapper — gold the proxy stands in for | Refine (attributes the P~0.71). |
| **f2b-transfer (human judge-1)** | FROZEN-UNRUN, human-blocked | efficiency — THE H-TRANSFER vs H-CIRC adjudicator | **Verdict-moving.** The canonical de-confound; the A_1p proxy explicitly is not it. |
| **g2** (Π read-out soundness vs human gold) | FROZEN-UNRUN, input-blocked | correctness — the semantics core | **Verdict-moving.** Whether the kernel's semantics are sound at all. |
| **g3** (semantics-pin necessity) | FROZEN-UNRUN, input-blocked | correctness — gates g2 | Verdict-moving on necessity. |
| **f2b-errors, g4, g5, b-cov-smol** | FROZEN-UNRUN / DRAFT | robustness / authoring / external-benchmark coverage | Refine. |

DECISION: [STIPULATED: ASM-0761] No IN-FLIGHT item is load-bearing enough to defer this synthesis. The two in-flight items (g3-llmproxy-v3, the knull plain-arm rewrite) are, respectively, a weak proxy that cannot discharge g3's kill and a control-quality repair that produces no verdict; the genuinely verdict-moving items (g2, human f2b-transfer, the knull *ablation*, human g9) are all UNRUN and human/input-blocked, not in flight. Therefore I author the DEFINITIVE STANDING verdict now. Both per-thesis verdicts are already INCONCLUSIVE-PENDING, so no pending item can *reverse* a FEASIBLE/NOT-FEASIBLE call (there is none to reverse); each verdict-moving item RESOLVES the pending INCONCLUSIVE toward FEASIBLE or NOT-FEASIBLE, and each refine-only item narrows an envelope without moving the standing call.

---

## 4. Strongest defensible positive and negative, per thesis (tagged)

**CORRECTNESS**
- Strongest defensible POSITIVE: a sound, fail-closed, provenance-carrying, ~µs deterministic checker EXISTS and ports across two verticals with a byte-identical engine [MEASURED, cross-vendor CONFIRMED: l3a 600/600, a5 855/855]. Honest ceiling: INSTRUMENT-ONLY, self-authored substrate, formalism-not-NSM-semantics (ASM-0004/0007).
- Strongest defensible NEGATIVE: every MEASURED crossing from that instrument into real/natural input is negative — NL boundary FAIL on BOTH verticals (47.6% / 41.6%), one of them DANGEROUS (a5-nl S2 kill fired), wild-formal FAIL (g8 0/1000), text-delivered grounding net-harmful (nsk1 g2d) — and the system produces no scholarly-English surface layer at all [MEASURED, each scoped to its verdict; the boundary conjunction is EXTRAPOLATION per ASM-0762, direction-only].

**EFFICIENCY**
- Strongest defensible POSITIVE: on FORMAL self-authored inputs a 135M host + kernel-verify-retry beats a 12×-larger 1.7B host by +0.1507 at ~10% FLOPs, and the lift is content-alignment-specific (a seed-pinned derangement kills it) [MEASURED, CONFIRMED: f2b-replicate]; cross-lingual minting shows a real, large MEMBERSHIP upper bound (~18–42% @10k) [MEASURED-exploratory: a-e2-census].
- Strongest defensible NEGATIVE: the one end-task positive is correct-ALIGNMENT-specific not kernel-content-specific (a generic aligned answer-key + retry would reproduce it), its de-confound is unrun, and it inherits the NL-boundary FAIL for real deployment; the compute-matched f2 primary FAILED and HE2 cascade-dominance DIED; the A-E2 figure is an upper bound with the consumption AND mint-cost sides unmeasured [MEASURED / MEASURED-exploratory, each scoped].

---

## 5. The next decisive experiment, per thesis (pre-registered re-entries)

**CORRECTNESS.** Two, in order:
1. **FK-NLB-3 — an LLM-assisted (or deterministic synonym/frame-direction-repair) parser** for the NL boundary, re-clearing both the 0.90 exactness bar and the a5-nl S2 fail-closed gate per vertical [the pre-registered re-entry the l3a-parse/a5-nl kills route investment to; ASM-0720 discipline]. If NL cannot reach the closed grammar cheaply and safely, the checker is a permanent internal instrument regardless of everything else.
2. **g2 (Π read-out soundness vs blind human gold), g3-gated** — whether the kernel's semantics are sound at all; g3 necessity is generated first to protect the g2 gold-annotation budget. Human-annotation-blocked, Tier-0 compute.

**EFFICIENCY.** The single decisive test is the **de-confound of the +0.1507**:
- **the knull K-NULL aligned-non-NSM-store ablation** (its plain control re-authored to the maintainer's quality standard FIRST, per ASM-0700 — the un-rewritten control confounds it one-sidedly), which decides what the lift IS evidence of at ~$0–250; OR
- **the human f2b-transfer Stage-1**, the canonical H-TRANSFER vs H-CIRC adjudicator.
Then, to price the compression side: **A-F0-run** (mint cost, needs the maintainer's API key) and a **consumption-channel measurement for A-E2** (K-A3 delivery + accuracy non-inferiority), which convert the upper bound toward achievable savings or kill it.

---

## 6. Bottom line

LOAD-BEARING: Neither thesis is dead; neither is established. Both stand at INCONCLUSIVE-PENDING within explicit scopes: correctness has a MEASURED, CONFIRMED *instrument* and a wall of MEASURED negatives at every boundary it has tried to cross, with its semantics core unrun; efficiency has one MEASURED, CONFIRMED end-task SIGN on formal inputs that is not yet attributable to kernel content, plus a large but upper-bound compression membership number, with its de-confound, cost, and consumption sides unrun [MEASURED: §1–§2 verdicts (registry/verdicts/*) restated; the cross-thesis reachability-wall-on-coverage-wall shape is separately an EXTRAPOLATION (ASM-0762), direction-only and never a premise]. The binding constraint on both verdicts is not compute — it is human annotation (f2b-transfer, g2 gold, human g9/M0a), one API key (A-F0), input-material generation (g3), and one cheap ablation (knull, after its control rewrite). Every decisive next step is already designed and pre-registered.

---

## Epistemic register (what this synthesis relied on)

- **STIPULATED (ASM-0760):** the two standing per-thesis feasibility verdicts and their scopes/confidences (the capstone decision) — both INCONCLUSIVE-PENDING within the stated envelopes.
- **STIPULATED (ASM-0761):** no in-flight item (g3-llmproxy-v3, knull plain-arm rewrite) is verdict-moving; the standing verdict is authored now, not deferred.
- **EXTRAPOLATION (ASM-0762, never a premise):** the reachability-wall-on-coverage-wall cross-thesis reading; each constituent figure is index-bound to its own verdict's envelope.
- **STIPULATED, adopted verbatim from the source assessments:** the f2b lift is correct-alignment-specific not kernel-content-specific; A_1p 0.95 is a WEAK proxy (ASM-0022); the A-E2 figure is a membership upper bound; the truthstyle PASS is instrument-only (ASM-0680); the knull surface-realization gap is a named unmeasured component (ASM-0702).
- **MEASURED, fully indexed and never widened:** every §1–§2 number carries its corpus/rung/kernel-state/vertical indices verbatim; m0b 0.3542 is restated only as a corpus-indexed gate, never as "natural coverage".

This is the definitive standing feasibility verdict on the current evidence. It moves from
INCONCLUSIVE toward FEASIBLE or NOT-FEASIBLE only when the verdict-moving PENDING items
(§3) read out; it changes no frozen object, no verdict, and no audit.
