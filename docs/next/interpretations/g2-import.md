# FABLE INTERPRETATION — g2-import (PROVISIONAL-ON-LLM-PROXY; mechanical verdict: INSTRUMENT-INVALID by the κ_A3 stability gate; primary point-estimate gate met decisively — a GO-SHAPED signal, NOT a licensed GO)

- **Author:** Fable (interpretation role), 2026-07-12. This is the interpretive assessment
  for the ONT-TYPE-G2/1 run (registry `g2-import`, issue #20). The coordinator computed
  the mechanical verdict (verdict-gen); this document changes NO frozen record, NO verdict
  object, NO log, NO analysis output, and NO registry assumption.
- **Sources (read at source, in full):** `registry/experiments/g2-import.json` (FROZEN,
  sha256 862e374a…), `registry/verdicts/g2-import.json` (computed 2026-07-12T03:01:27Z),
  `poc/ontology-import-g2/result.json` (labels sha256 ed0c000e…),
  `poc/ontology-import-g2/analysis-output.json` (sha256 ccbdf2f6…), the pinned
  `analysis/ontg2.py` (sha256 5cca4b5c…, matching the frozen pin), and
  `docs/next/design/ontology-import-plan.md` §§7.3–7.8 (sha256 ef1df814…, matching).
- **Status tag, binding on every gold-dependent number below:** **PROVISIONAL-ON-LLM-PROXY.**
  "Gold" here is the directive-#11 blind cross-family LLM pair (judge-pA GPT-5.6-Sol via
  pinned codex CLI = primary stand-in; judge-pB Claude Haiku 4.5, vendor-family overlap
  with the materials' authoring agents DISCLOSED, never sole gold). κ is judge-pair
  stability, never human-agreement evidence. The later two-human adjudicated panel is the
  sole authority for any permanent scientific adoption.
- **Rider, verbatim, on every verdict-adjacent sentence in this document:**
  *"PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; point-estimate
  engineering gate, not statistical superiority; soft non-binding typing only — never hard
  laws; no feasibility conclusion."*

---

## 0. The mechanical facts, restated inside the envelope

PREMISE: [MEASURED: analysis-output.json, verdict endpoints] Over the SAME 84 self-authored
kernel-v0-derived slots the g2 readout scored, judge-pA construction, vacuity-zeroed
scoring, fixed denominator 84, both judges 84/84 decisive on every arm, deranged-probe
false-satisfaction 0/20 per judge per arm, all pins matched, zero blinding hits:

| Arm | Sound (pA) | Precision | Wilson 95% | κ (pair) | McNemar vs A0 | Non-vacuous |
|---|---|---|---|---|---|---|
| A0 frozen hard-4-sort baseline | 33/84 | **0.3929** | (frozen; estimation-only) | — | — | — |
| A1 BFO-only (breadth control) | 55/84 | 0.6548 | [0.5483, 0.7477] | 0.5273 | not tested | 67/84; R3 26/42 |
| A2 BFO+SUMO | 53/84 | 0.6310 | [0.5242, 0.7263] | 0.4296 | b=5, c=25, p=3.2×10⁻⁴ | 83/84; R3 42/42 |
| A3 BFO+SUMO+FrameNet (adoption arm) | **57/84** | **0.6786** | [**0.5728**, 0.7687] | **0.2859** | b=6, c=30, **p=7.0×10⁻⁵** | 83/84; R3 42/42 |

- **Primary endpoint** (plan §7.5, verbatim gate `sound_A3 ≥ 34/84`): **PASSED** —
  57 ≥ 34, `/analysis/primary_pass = true`, Δ vs baseline +24/84 = +0.2857. A2 also
  passed (53 ≥ 34). [rider verbatim above]
- **Informativeness guard** (plan §7.6): **PASSED** — A3 non-vacuous 83/84 ≥ 67,
  R3 non-vacuous 42/42 ≥ 34, zero hard operational laws emitted
  (`forbidden_effects_ok = true`). The A3 lift is NOT vacuity — the guard built to catch
  breadth-masquerading-as-soundness is clean.
- **Instrument gate** (plan §7.6; `analysis/ontg2.py` lines 140–144): **FAILED**, on
  exactly ONE channel: **κ_A3 = 0.2859 < 0.40**. Every other channel passed
  (κ_A1 = 0.527, κ_A2 = 0.430, decisive_min = 1.00 against the 0.90 bar, probe
  false-satisfaction 0.0 against 0.30, pins ok). The frozen verdict rules fire in order;
  rule 0 (`not /gates/instrument_valid`) fires, so the mechanical verdict is
  **INSTRUMENT-INVALID** — per the pinned decision table (plan §7.7): *"No conclusion;
  repair and mint a new frozen run."*
- Record note, moot at the measured values: the frozen `kill_criterion_verbatim` names a
  "decisive < 95%" trip while the frozen endpoint and pinned script use the RT-4-decidable
  0.90 bar; decisiveness measured 1.00, so no channel turns on the discrepancy. Flagged
  for the record only.
- Provenance note: one logged run row (seq 0) was excluded by verdict-gen on the declared
  arm-levels check; eligible_runs = 1 (the scored run). No amendments applied.
- **Coverage disclosure, mandatory:** kernel-expressibility coverage **0.3542** at rung
  molecules-v0, measured by m0b on one incomplete kernel-v0 instance — NOT general
  coverage. Scale language licensed: none. Rungs measured: R0.
- **Baseline caveat, inherited and restated** [STIPULATED: frozen record]: the frozen A0
  readout 33/84 is itself estimation-only (the predecessor g2's own n ≥ 500 instrument
  gate was unattainable on this corpus) and is consumed as a pinned constant, not a
  re-run arm.

---

## 1. The tension, exactly

LOAD-BEARING: [MEASURED: results-log/g2-import.jsonl; poc/ontology-import-g2/analysis-output.json] The primary passed **decisively**, not marginally. The
imported SOFT BFO/SUMO/FrameNet typing scored 0.6786 blind ordinary-meaning soundness
against the hand-authored HARD 4-sort scheme's 0.3929 on the identical 84 slots — nearly
double. The co-reported (never verdict-bearing) statistics all point the same way: the A3
Wilson 95% lower bound (0.5728) sits above even the baseline POINT estimate; the paired
exact McNemar table is 30 slots flipped sound vs 6 flipped unsound (p = 7.0×10⁻⁵); the
most conservative bracket — pair-concordant yes, 42/84 = 0.50 — still clears both the
34/84 gate and the 33/84 baseline; the pB sensitivity score (53/84) agrees in direction.
The failure the predecessor g2 localized in R3 domain/range renderings (0/21 and 2/21
concordant-yes under the hard scheme) is precisely where the soft imported layer recovers:
A3 R3 = 27/42 sound with 42/42 non-vacuous. In DIRECTION this is strong support for
H-SOFT — the issue-#20 bet that the measured 0.39 over-constraint is a property of the
hard-law ROUTING, not of typing as such. [rider verbatim above]

LOAD-BEARING: [MEASURED: verdict object] AND YET the mechanical verdict is
**INSTRUMENT-INVALID**, and that is the correct reading, not a technicality:

- The judge pair went UNSTABLE on exactly the arm that matters. κ_A3 = 0.2859 is below
  the 0.40 floor the design froze as the premise H-INSTRUMENT; raw disagreement on A3 is
  27/84 items (pA-yes/pB-no 16, pA-no/pB-yes 11). The pair was stable on A1 and A2 and
  degraded monotonically with rendering richness (0.53 → 0.43 → 0.29) — consistent with
  the soft-hedged "Normally…/Typically…" A3 renderings being harder to adjudicate
  consistently, and disclosed as such [MEASURED: agreement tables; EXTRAPOLATION:
  the monotone-degradation mechanism reading, load-bearing for nothing].
- An unstable instrument cannot mint the very number that passed the gate. The 57/84 is a
  judge-pA construction; when the pair disagrees on a third of the adoption arm, the
  frozen design says the reading is "no conclusion — repair and mint a new frozen run,"
  and equal prominence for deflationary outcomes requires saying so in the same breath as
  the headline. [STIPULATED: plan §7.7 row 5; kill_criterion_verbatim INSTRUMENT-INVALID
  clause]
- Every number above is **PROVISIONAL-ON-LLM-PROXY**: proxy stand-ins, not the two-human
  adjudicated gold; κ is pair stability, never human agreement; a proxy GO followed by a
  human-gold failure is governed by the human result (plan §7.7 last row). And at n = 84
  a κ estimate is itself noisy — which cuts BOTH ways and rescues nothing.

**So the licensed reading, in one sentence:** a strong GO-SHAPED signal, NOT a licensed
GO — the maintainer-ratified point-estimate ENGINEERING gate (≥ 34/84) is met, no
statistical-superiority claim of any form is licensed even so (Wilson/McNemar are
co-reported for honesty, not licensing), no PASS verdict exists, and permanent adoption
stays gated on (i) **human-gold re-adjudication of the SAME frozen 84-slot package** and
(ii) **a re-run on a repaired, powered instrument** (the κ_A3 stability failure repaired
under a NEW frozen record; the inherited estimation-only baseline caveat priced in).
[rider verbatim above]

What this does NOT license [STIPULATED: extrapolation_envelope_verbatim]: hard imported
laws; identity changes; automatic bridge endorsement; Π-replacement (open maintainer
decision 10); gUFO claims (not loaded; separately gated); any statement about ontology
correctness; any W1/G4/host-model/competitiveness sentence; **any feasibility conclusion
about either programme thesis**. Even a clean PASS would license only bounded promotion
of the winning non-binding soft-preference shard (advisory rank/lint/explain only,
outside hard closure, provenance exposed) — and there is no clean PASS here.

---

## 2. The breadth-control caveat (equal prominence)

LOAD-BEARING: [MEASURED: poc/ontology-import-g2/analysis-output.json] **A1 also lifted.** The BFO-only breadth control scored 55/84 =
0.6548 — above the engineering gate and within noise of A3's 57. By frozen design A1 can
NEVER authorize adoption, and it would independently flunk the informativeness guard on
R3 (26/42 non-vacuous < 34); its lift rides on only 67/84 non-vacuous slots. But the
honest reading of the arm ladder (55 → 53 → 57) is that the bulk of the improvement over
A0 comes from the SOFT, non-binding routing plus broad categorial anchoring — not from
the source-specific SUMO/FrameNet content, whose measurable contribution at this n is
(a) informativeness coverage (non-vacuous 67→83 overall, 26→42 on R3) and (b) a small
soundness edge for FrameNet over SUMO-only (A3−A2 = +4 overall, +5 on R3; H-SRC reads
GO-combined, descriptively). This SHARPENS H-SOFT (even breadth-only soft typing escapes
the over-constraint) while flattening any claim that the imported ontologies' specific
content is what carries the effect. A powered re-run must be able to separate these; at
n = 84 it cannot. [REPORTED-ONLY: arm deltas are not verdict-bearing anywhere in the
frozen design]

---

## 3. Bearing on the CORRECTNESS thesis — scoped

INTERPRETIVE FRAMING (direction-only, never a premise): this experiment is about where to
SOURCE the kernel's type layer, NOT a thesis verdict. The predecessor g2 (proxy strength)
warned that the Π hard-typing read-out is not a sound source of ordinary-meaning axioms;
this run points, at the same proxy strength and on the same 84 slots, at a candidate
repair whose shape matters: keep typing, drop hard-law routing, import soft expectations
with exposed provenance. That is a CONTENT-SOURCING gradient on the content-validity
flank — no parser, no host model, no NL crossing, no reachability claim is in this loop,
and nothing here confirms or disconfirms the correctness thesis itself. The g2 demotion
question (Π to lint, option b) is untouched: it reads HUMAN gold only, and this record
adds no human labels. [EXTRAPOLATION: gradient reading; load-bearing for nothing]

What would move this: (i) the two-human adjudicated panel on the SAME frozen 84-slot
package (all four arms' materials are hash-pinned for exactly this); (ii) a repaired
instrument — the κ_A3 stability failure diagnosed and fixed (rubric tightening for
soft-hedged modality is the obvious first suspect) under a NEW frozen record, with n
sized so the stability and soundness questions are both decidable; (iii) the A1-vs-A3
separation test the breadth caveat demands.

---

## 4. Epistemic register

- **MEASURED:** every count, precision, Wilson bound, κ, McNemar entry, probe, coverage
  and non-vacuity figure in §0–§2, strictly at n = 84 / R0 on pinned kernel-v0; labels
  sha ed0c000e…, analysis output sha ccbdf2f6…, frozen record sha 862e374a….
- **STIPULATED:** the directive-#11 LLM-proxy stand-in policy; PROVISIONAL-ON-LLM-PROXY
  on every gold-dependent number; κ as pair stability only; the frozen verdict-name
  mapping and rule order; the 34/84 gate as a maintainer-ratified point-estimate
  engineering gate; the soft-only routing invariants (binding:false, rank-only, five
  forbidden effects, validator fail-closed); the inherited estimation-only status of the
  33/84 baseline.
- **EXTRAPOLATION, direction-only, load-bearing for nothing:** the GO-shaped-signal
  reading of H-SOFT; the κ-degradation-with-rendering-richness mechanism; the
  breadth-vs-content decomposition in §2; the content-sourcing gradient in §3.

## PROPOSED-ASM (coordinator to register — NOT written to registry/assumptions.jsonl here)

```json
{"id":"PROPOSED-ASM-1460","class":"STIPULATED","load_bearing":true,"text":"g2-import proxy readout record: over the SAME frozen 84 kernel-v0 slots as g2, judge-pA construction, vacuity-zeroed, the soft imported type arms scored A1 55/84=0.6548, A2 53/84=0.6310, A3 57/84=0.6786 (Wilson [0.5728,0.7687]; McNemar vs the frozen A0 33/84 baseline b=6 c=30 p=6.96e-05) with informativeness guard passed (A3 non-vacuous 83/84, R3 42/42, zero hard laws) — but the mechanical verdict is INSTRUMENT-INVALID because kappa_A3 = 0.2859 < 0.40 (sole failing channel; decisive 1.00, probes 0.0, pins ok; kappa_A1 0.527, kappa_A2 0.430). Per the frozen decision table this is NO CONCLUSION: no PASS/GO exists; repair and mint a new frozen run. Every number is PROVISIONAL-ON-LLM-PROXY (judge-pA GPT-5.6-Sol primary stand-in, judge-pB Claude Haiku 4.5 sensitivity, vendor overlap disclosed); kappa is pair stability, never human agreement; the two-human panel on the SAME frozen package is the sole authority for permanent adoption. Rider verbatim: PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; point-estimate engineering gate, not statistical superiority; soft non-binding typing only — never hard laws; no feasibility conclusion."}
{"id":"PROPOSED-ASM-1461","class":"EXTRAPOLATION","load_bearing":false,"resolution_path":"human-gold re-adjudication of the SAME frozen 84-slot package (all arms hash-pinned) PLUS a repaired-instrument powered re-run under a NEW frozen record (kappa_A3 stability failure diagnosed/fixed; n sized so stability and soundness are both decidable)","text":"g2-import gradient reading (interpretive colour only; never a premise): at proxy strength the imported SOFT BFO/SUMO/FrameNet typing nearly doubles blind ordinary-meaning soundness over the hand-authored HARD 4-sort scheme on the identical slots, with the recovery concentrated exactly where the hard scheme failed (R3 27/42 vs ~0), and even the conservative pair-concordant bracket (42/84) clears both gate and baseline — strong DIRECTIONAL support for H-SOFT (the g2 over-constraint is a property of hard-law routing, not of typing as such). This is a GO-SHAPED signal, not a licensed GO: the verdict is INSTRUMENT-INVALID, the gate is a point-estimate engineering gate, and no superiority or adoption claim is licensed. No feasibility conclusion."}
{"id":"PROPOSED-ASM-1462","class":"EXTRAPOLATION","load_bearing":false,"resolution_path":"the powered re-run must include an A1-vs-A3 separation test (or a pre-registered A3-vs-A1 paired endpoint) so breadth-plus-softness is distinguishable from source-specific SUMO/FrameNet content","text":"g2-import breadth-control caveat (equal prominence): the A1 BFO-only breadth control also lifted (55/84, within noise of A3's 57), so at n=84 the bulk of the improvement over A0 is attributable to SOFT routing plus broad categorial anchoring rather than to imported source-specific content, whose measured contribution is informativeness coverage (non-vacuous 67->83; R3 26->42) plus a small A3-A2 edge (+4). A1 can never authorize adoption (frozen design) and would flunk the R3 informativeness guard; this caveat sharpens H-SOFT while flattening any claim that the ontologies' specific content carries the effect."}
```

---

*This interpretation changes no frozen object, no verdict, no log, no analysis output,
and no registered assumption. Next decisive steps on this line: (i) the two-human
adjudicated panel on the SAME frozen 84-slot four-arm package; (ii) instrument repair for
soft-modality adjudication (κ_A3 = 0.2859) and a powered re-run under a NEW frozen
record; (iii) the A1-vs-A3 separation the breadth caveat demands. Until then: the soft
imported type layer is the leading candidate repair for the g2 over-constraint, and
nothing is adopted.*
