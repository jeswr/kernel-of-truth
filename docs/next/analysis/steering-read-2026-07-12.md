# Steering read — 2026-07-12 (Fable strategic-analysis agent)

> **SUBJECTIVE OPINION, in its entirety.** This is a qualitative steering read of the
> programme by the Fable strategic-analysis role. It is opinion labelled as opinion,
> per [[subjective-dual-model-analysis]] practice: it **never overrides a mechanical
> verdict, a frozen envelope, a rider, or a registered assumption**, and it states
> **NO feasibility conclusion on either thesis** — CORRECTNESS and EFFICIENCY remain
> **INCONCLUSIVE-PENDING** exactly as the registry says. Where I cite a number it is
> a measured anchor from the sources below; everything wrapped around those numbers
> is my judgment and should be weighed as such.

**Sources read at source:** `docs/next/feasibility-synthesis-v5.md`;
`docs/next/arch/round2-arch-synthesis.md`; `registry/verdicts/*.json` (deconf-b PASS,
audit CONFIRMED; casc-0, g2, g2-import INSTRUMENT-INVALID); `poc/rules-1/RESULT.md`;
`docs/next/interpretations/{g2-import,casc-0,deconf-b,g2}.md`;
`docs/next/analysis/round2-steering.md` (prior steering note, for continuity).

**Assumptions:** any assumption proposed here is emitted as PROPOSED-ASM-1540..1549 in
§5 for coordinator registration. Nothing was written to `registry/assumptions.jsonl`.

---

## 1. What is going well — SUBJECTIVE OPINION

**The programme now has three genuinely different positive signals, and they rhyme.**
That is new. Round-1 had one mechanism and a pile of designs; today there are three
measured (or measured-shaped) results in three different value locations:

1. **Authored aligned content works, at verdict grade.** f2b-transfer: external-gold
   lift **+0.2507** for 135M + aligned verify-retry over 135M alone, endorsement
   **320/333 = 0.961**, controls passed [MEASURED, VERDICT-GRADE; f2b riders].
   DECONF-B replicated and localized it: **Δ_align = +0.2697**, bridge lift **+0.285
   (LB95 +0.255)**, pinned BM25/self-consistency alternatives stuck near **0.41**,
   audit **CONFIRMED** (`registry/verdicts/deconf-b.json`). This is the programme's
   bedrock: a real, replicated, audited ~+0.25–0.28 effect with a located mechanism
   (item-aligned deterministic acceptance), not an artifact of one run.

2. **The rules engine is provably not decorative.** The RULES-1 CPU certificate
   (registered re-run, `poc/rules-1/RESULT.md`): stated-cell C_dec **1.0 (1,716/1,716)**
   vs entailed-cell C_dec **0.0 (0/3,680)** — on the *same mechanical definition* under
   which DECONF-A1 measured the old estate inert — with **858/858** against third-party
   CLUTRR gold (Wilson-LB95 0.9955), 100/100 named refusals, all four counterfactual
   gates behaving exactly as predicted, deterministic to the byte, <2 s, ~$0. In my
   opinion this is the single most under-appreciated result in the repo: it converts
   "the structure is inert" from a programme-killing pattern into a *tested and passed*
   precondition. The inversion of the inertness instrument against itself is also just
   good science.

3. **The typing repair points the right way, loudly.** g2-import A3 (imported soft
   BFO/SUMO/FrameNet typing) scored **57/84 = 0.679** blind ordinary-meaning soundness
   vs the frozen hard-4-sort baseline **33/84 = 0.393**, McNemar **p = 7.0×10⁻⁵**,
   recovery concentrated exactly where g2 localized the failure (R3: 27/42 vs ~0),
   non-vacuity guard clean (83/84). Mechanically INSTRUMENT-INVALID (κ_A3 = 0.286) and
   PROVISIONAL-ON-LLM-PROXY throughout — so it licenses nothing — but as *steering*
   information a GO-shaped signal at p=7e-5 whose conservative pair-concordant bracket
   (42/84) still clears the gate is about as strong as unlicensed evidence gets.

**What they collectively suggest (opinion, direction-only):** the modular through-line
in synthesis-v5 §5.3 is not wishful — each layer of it now has its own independent
positive. Authored meaning → aligned answer-bearing stores (f2b/DECONF, verdict-grade)
→ deterministic proof-carrying inference that adds decisions lookup cannot (RULES-1
certificate) → *soft*, provenance-bearing typing instead of hard laws (g2-import
direction). Three teams of evidence arriving at the same architecture from three sides
is the pattern you hope to see when a design is real rather than narrated. Also worth
crediting: the epistemic machinery itself — verdict-gen fired INSTRUMENT-INVALID three
times on results people *wanted* (including a p=7e-5 result), and nobody argued with
it. That discipline is the programme's most valuable asset.

---

## 2. What is concerning — SUBJECTIVE OPINION

1. **Both theses are still INCONCLUSIVE-PENDING, and the pendency is aging.** After
   f2b, DECONF-A1/B, CASC-0′, g2, g2-import, RULES-1-CPU and two architecture rounds,
   neither CORRECTNESS nor EFFICIENCY has moved off INCONCLUSIVE-PENDING [STIPULATED:
   ASM-1380]. The honest cause is that the affirmative decisive legs keep being the
   ones that don't run. Round-2 steering named this risk **FAIL-by-attrition** —
   deflationary legs are cheap and keep landing; affirmative legs are annotation- or
   build-gated and keep not landing — and in my opinion that risk is *more* live today,
   not less.

2. **The instrument-failure pattern.** Three of the last four graded runs died at the
   instrument gate, each on a different channel: casc-0 (TTC deflator mismatch 0.3537 >
   0.30 + failed size separation), g2 (n=84 < 500), g2-import (κ_A3 = 0.286 < 0.40).
   Each was correct to fire, and each was arguably foreseeable at freeze time: the TTC
   band was frozen DRAFT with a known integer-N quantisation problem; g2's n≥500 gate
   was *known unattainable on this corpus*; g2-import froze a κ floor without piloting
   judge stability on the hardest (soft-hedged) rendering. The pattern is that
   experiments are being frozen with instruments that have never been exercised at the
   operating point, so the expensive pass buys an instrument diagnosis instead of an
   answer, and everything needs a rework/build pass before it is actually runnable.
   The discipline is right; the *ordering* is wasteful.

3. **LLM-proxy gold is carrying too much of the interesting load.** Everything on the
   g2/g2-import line — including the programme's best current adverse signal (hard Π
   0.39-sound) and best current repair signal (soft 0.68) — is PROVISIONAL-ON-LLM-PROXY,
   with the two-human panel as sole adoption authority and *zero human panels run to
   date*. If the proxies are directionally wrong, a large fraction of current steering
   (including parts of this document) is steering on noise. The g2-import κ_A3 collapse
   is a concrete warning that the proxy pair itself gets unstable exactly where the
   content gets interesting.

4. **Natural-input reach and coverage remain the walls they were.** RULES-1 worlds are
   gold-parsed (ASM-1123); CASC-0′ never exercised a front end and the standing ret_F
   0.42–0.48 FAILs are untouched; kernel-expressibility coverage is **0.3542 at
   molecules-v0** on one incomplete kernel-v0 instance. Every positive above lives on
   covered, self-authored, formally-addressed slices. The programme is getting very
   good at winning inside a fence it has not yet shown it can move.

5. **Kernel-specific attribution keeps dying at every seam it is tested.** DECONF-A1
   C_dec=1.0; DECONF-B GS-A–kernel identity **1.0**; CASC-0′ K3′ gloss ≡ plain typed
   dialect (TOST inside ±0.05); g2-import's own breadth control A1 (BFO-only) lifted to
   55/84, within noise of A3. The measured value keeps being *aligned content* and
   *actual closure*, never kernel-STYLE structure per se — and now even the ontology
   lift may be mostly "soft routing + any broad anchoring". Round-2 steering asked "is
   the kernel becoming optional to its own programme?" That question is still being
   answered by cost gradients rather than by decision, and the pending deciders
   (knull rules-source ablation, g2/g2-import human gold, knull-v2 rulings) are
   exactly the legs that keep queueing.

---

## 3. Directions: promising vs dead-end — SUBJECTIVE OPINION, ranked

**Live bets, in my order of expected steering value:**

1. **RULES-1 host-lift grade (GPU A3-vs-A1) + the knull rules-source ablation.** The
   freeze-ready record exists (DRY-RUN-OK, $10 budget, KILL-b pre-registered, certificate
   pinned as passed precondition), the gold is third-party (CLUTRR — it escapes the
   LLM-proxy trap entirely), and it is the only pending experiment that can attach a
   genuinely *new kind* of positive (entailment → host accuracy) to the correctness
   line. Synthesis-v5 already calls it the nearest direct resolver; I agree and would
   go further — see §4.

2. **g2-import instrument repair + re-mint (~$10, annotation lane).** Best
   evidence-per-dollar on the board (round2-arch-synthesis is right about this). One κ
   repair (rubric tightening for soft-hedged modality) + one re-run converts a p=7e-5
   GO-shaped signal into either a licensed engineering GO or an honest kill. Must carry
   the A1-vs-A3 separation endpoint this time, or the breadth caveat will eat the result.

3. **RULES-2 / the rules-engine build-out** — but only *behind* the RULES-1 host grade.
   If A3−A1 reads positive, this line inherits everything; if it reads null, a second
   engine campaign before understanding why would be spend without a question.

4. **Aligned-content stores (the f2b/DECONF mechanism).** Already the strongest
   measured thing in the programme; what it needs now is not more mechanism replication
   but its *economics and authoring-attribution* legs (mint cost, knull-v2 content
   arms, independent-author comparison). Promising precisely because it is boring.

5. **KUFO-1 / full-UFO thin slice.** Well-designed as a bet (representation-matched
   null + deranged control answer the circularity critique; ≤$25 + ~1 agent-week;
   engine spend gated behind a measured GO). I endorse the round-2 shortlist's shape —
   but as opinion I'd hold Wave-1 until the two items above have read out. It is the
   most speculative live line, its value case is entirely [EXTRAPOLATION], and the
   programme's scarce resource right now is attention on affirmative *graded* legs,
   not another handsome instrument.

6. **Aligned-store human-gold reconciliations (g2 84-panel; any GO-shaped g2-import
   follow-up).** Not an "experiment" but the single biggest de-risking purchase
   available against §2.3. Should be scheduled as work, not held as an aspiration.

**Deflated / dead-end (do not re-fund without new cause):**

- **Static prompted naturalisation (CASC-0′ scope).** No positive M2 sign in either
  raw interaction (gloss +0.0033, plain −0.0333, primary_reject=false), gloss ≡ plain
  at R2 — and note carefully this is *descriptive* deflation under an INSTRUMENT-INVALID
  verdict, not a licensed NULL. My opinion: accept the interpretation doc's
  recommendation — do not rerun unless clean static adjudication becomes
  decision-critical. Retire it from the default portfolio.
- **Hard universal 4-sort Π typing.** 0.39 proxy-sound, with the repair arm nearly
  doubling it on the same slots. Keep Π only as the frozen baseline it now is; final
  demotion still awaits human gold (the authority rule stands).
- **gUFO-labels-only prior.** Correctly ranked "dominated; subsumed" in the arch
  synthesis; class names without theorems.
- **Kernel-STYLE gloss as a runtime medium.** Killed non-fatally by K3′ at its tested
  scope; any surviving structured-medium account must remain generic there.

---

## 4. How the programme runs, and the single next experiment — SUBJECTIVE OPINION

**Is the review→rework cycle worth its latency?** Mostly yes — the freeze/verdict-gen
/audit discipline is why the three INSTRUMENT-INVALIDs are clean diagnoses instead of
motivated readings, and it must not be weakened. But the cycle is currently paying its
latency in the wrong place: instruments fail *after* the run instead of *before* the
freeze. Concrete change I'd make: add a mandatory cheap **instrument pilot** to the
prereg protocol — exercise the gate channel at the operating point before freezing
(e.g. a 15–20-item κ pilot per arm-rendering for judge-pair designs; a synthetic-counts
dry-run of any deflator/matching band; a decidability lint on every n-gate against the
actually-available corpus, which the g2 case shows was knowable in advance). That is
hours of work per experiment against the multi-day rework passes casc-0/g2-import are
now buying.

**Where to consolidate:** (i) *Stop new architecture rounds* — round-2 steering said
this and a second arch round happened anyway; the round-2 synthesis itself is good, but
the design shelf is now years deep and the marginal arch cycle produces convergence
certificates, not information. Freeze the shortlist as-is. (ii) *One annotation lane
with a ratified ranking* — the FAIL-by-attrition mitigation (verdict-movement-per-
annotator-hour ranking + bounded budget) was endorsed by both models last round and
still isn't operating; every week it doesn't, the proxy-gold overhang in §2.3 grows.
(iii) *Fold the UFO checking work into the existing lanes* (as the arch synthesis
already proposes) rather than letting it become a fourth parallel programme.

**The single highest-value next experiment: freeze and grade the RULES-1 GPU host-lift
campaign (A3 vs A1), with the knull rules-source ablation queued immediately behind a
positive read.** Reasoning, in plain language:

- It is the fastest *licensed* movement available on either thesis. The record is
  freeze-ready today (dry-run green, zero pause flags), the budget is $10, and the
  passed CPU certificate is already pinned as its precondition — no rework pass stands
  between here and a graded result, which is not true of anything else affirmative on
  the board (g2-import needs an instrument repair; KUFO-1 needs a week of Rust; NLB
  needs ~50 GPU-h).
- It is adjudicated on **third-party gold** (CLUTRR), so its outcome — either way —
  is immune to the LLM-proxy caveat that quarantines the whole g2 line. A positive
  A3−A1 (paired BCa LB > 0) would be the programme's first measured *host* benefit
  from genuine entailment; KILL-b gives an equally clean, equally cheap kill.
- It is the keystone dependency: the knull ablation (kernel-specific value), RULES-2,
  and the engine half of the KUFO decision are all conditioned on this one number.
  The g2-import repair, by contrast — though the best evidence-per-dollar — is a
  G2-class diagnostic that can never touch a thesis under its own envelope (never W1,
  never G4, no host model) and stays proxy-provisional even on a clean pass.
- Run the g2-import κ repair **in parallel** in the annotation lane (~$10); the two
  don't compete for resources. But if forced to name one, it is RULES-1's grade.

*(To be explicit once more: a RULES-1 GPU pass would license "rules-assisted host lift
at the registered scope" — not kernel-specific value, not efficiency, not a thesis
verdict. This section is prioritization opinion, not prediction.)*

---

## 5. Proposed assumptions (coordinator to register; NOT written to assumptions.jsonl)

```json
[
  {"id":"PROPOSED-ASM-1540","tag":"OPINION","load_bearing":false,"claim":"Steering-read 2026-07-12 standing header: this document is SUBJECTIVE OPINION by the Fable strategic-analysis role; it overrides no mechanical verdict, frozen envelope, or rider; it states no feasibility conclusion; CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING per ASM-1380.","backing_ref":"docs/next/analysis/steering-read-2026-07-12.md","owner":"fable-steering","date":"2026-07-12","status":"open"},
  {"id":"PROPOSED-ASM-1541","tag":"OPINION","load_bearing":false,"claim":"Convergence reading (direction-only, never a premise): the f2b/DECONF authored-content lift (+0.2507 / +0.285 LB95 +0.255, audited), the RULES-1 non-inertness certificate (stated C_dec 1.0 vs entailed 0.0; CLUTRR 858/858 Wilson-LB95 0.9955), and the g2-import soft-typing signal (0.679 vs 0.393, McNemar p=7e-5, INSTRUMENT-INVALID, proxy-provisional) independently support the same modular architecture (aligned stores + proof-carrying inference + soft typing); three independent positives arriving at one design is treated here as steering evidence of a real direction, licensing nothing.","backing_ref":"registry/verdicts/{deconf-b,f2b-transfer,g2-import}.json; poc/rules-1/RESULT.md; docs/next/feasibility-synthesis-v5.md §5.3","owner":"fable-steering","date":"2026-07-12","status":"open"},
  {"id":"PROPOSED-ASM-1542","tag":"OPINION","load_bearing":false,"claim":"Instrument-failure pattern flag: three of the last four graded runs (casc-0 TTC 0.3537>0.30; g2 n=84<500; g2-import kappa_A3 0.286<0.40) died at instrument gates that were plausibly diagnosable pre-freeze. Proposed process change: a mandatory cheap instrument pilot (gate channel exercised at the operating point — judge-kappa pilot, deflator dry-run, n-gate decidability lint against the available corpus) before any prereg-freeze.","backing_ref":"registry/verdicts/{casc-0,g2,g2-import}.json","owner":"fable-steering","date":"2026-07-12","status":"open"},
  {"id":"PROPOSED-ASM-1543","tag":"OPINION","load_bearing":false,"claim":"FAIL-by-attrition risk restated as still-live: all affirmative decisive legs (human-gold g2/g2-import panels, knull rules-source ablation, knull-v2 rulings, RULES-1 host grade until now) remain ungraded while deflationary legs keep landing; the round-2 mitigation (ratified annotation ranking by verdict-movement-per-annotator-hour + bounded budget) is endorsed again and is not yet operating.","backing_ref":"docs/next/analysis/round2-steering.md §A; docs/next/feasibility-synthesis-v5.md §6","owner":"fable-steering","date":"2026-07-12","status":"open"},
  {"id":"PROPOSED-ASM-1544","tag":"OPINION","load_bearing":false,"claim":"Single-highest-value-next-experiment recommendation: freeze and grade the RULES-1 GPU host-lift campaign (A3 vs A1, third-party CLUTRR gold, $10, freeze-ready, KILL-b pre-registered), with the knull rules-source ablation queued behind a positive read and the g2-import kappa repair run in parallel in the annotation lane. Rationale: fastest licensed movement on either thesis, proxy-gold-immune adjudication, and keystone dependency for RULES-2 / knull / KUFO engine decisions. A pass would license rules-assisted host lift at scope only — never kernel-specific value, efficiency, or a thesis verdict.","backing_ref":"registry/experiments/rules-1.json; poc/rules-1/RESULT.md; docs/next/feasibility-synthesis-v5.md §6.1","owner":"fable-steering","date":"2026-07-12","status":"open"},
  {"id":"PROPOSED-ASM-1545","tag":"OPINION","load_bearing":false,"claim":"Portfolio hygiene recommendations: retire static prompted naturalisation (CASC-0-prime scope) from the default portfolio per the interpretation doc's accept-INSTRUMENT-INVALID recommendation; keep hard 4-sort Pi only as the frozen baseline pending human gold; hold KUFO-1 Wave-1 until the RULES-1 host grade and g2-import repair read out; freeze the architecture-design shelf (no round-3 arch cycle) — designs now exceed the programme's grading throughput by years.","backing_ref":"docs/next/interpretations/casc-0.md §6; docs/next/arch/round2-arch-synthesis.md §1; docs/next/analysis/round2-steering.md item 5","owner":"fable-steering","date":"2026-07-12","status":"open"}
]
```

*(PROPOSED-ASM block 1546..1549 reserved, unused.)*

---

*This steering read changes no frozen object, no verdict, no log, and no registered
assumption. Supersede it when the RULES-1 host grade, the g2-import re-mint, or any
human-gold reconciliation lands.*
