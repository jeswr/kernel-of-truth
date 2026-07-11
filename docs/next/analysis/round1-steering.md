# Programme-3 — Round-1 subjective steering note (coordinator synthesis)

**What this is:** a synthesis of the two independent subjective analyses run at the batch-2 analysis
phase — Fable (`round1-fable-subjective.md`) and GPT-5.6 (`poc/gpt56-review/round1-subjective/`). It
REPORTS where the two models converge and diverge; it is OPINION/steering input (labelled as such per
[[subjective-dual-model-analysis]]), not a mechanical verdict or an epistemic conclusion. Its job is to
steer where effort goes next. The material redirection below is surfaced to the maintainer (issue #8).

## Where the two models CONVERGE (high-confidence steering signals)

1. **Scaffolding has outrun measurement.** GPT-5.6: Programme-3 "is in danger of becoming an
   evaluation-and-governance programme with a neurosymbolic experiment attached… the documentation and
   measurement superstructure are now far ahead of the experimental evidence." Fable: "since the NL
   FAILs landed the programme has produced four review cycles of measurement scaffolding and **zero new
   measurements against either wall**." → **Stop building scaffolding; start measuring.**

2. **The portfolio is too broad — cut it.** Both say scarce attention is spread over too many
   speculative families before the two existential questions are answered. Fable names the clearest
   probable **dead ends**: H-DD dimension-drop ("dead several times over" — recommend DORMANT, cancel
   design spend), general-NL GNN fusion (deltas shrink ~10× under LoRA-parity; causality probes show
   models reading text not structure), deep-internal rule placements (delivery-without-integration).

3. **Coverage is the existential risk, and the general-index ambition is probably already dead.**
   Measured external coverage is ~zero everywhere it's been measured (0/1550; g8 0/1000). Fable: "the
   honest normalised-scale G1 bound will likely kill every store-dependent family on any general index
   … the general-index W1 ambition is probably already dead and the **vertical-index fork should be
   pre-registered before the numbers force it**." GPT-5.6: "coverage can be grown" is meaningless
   without bytes and authoring cost.

4. **Attack the NL wall NOW, and make it THE main experiment.** Both: the design respects the wall
   (NLB gates everything) but the actual attack hasn't started — "building the courtroom before running
   the cheap forensic tests" (Fable) / "in design terms yes; in resource allocation and experimental
   urgency, no" (GPT-5.6). NLB should receive most of the next wave's attention, not be one gated
   workstream.

5. **The single biggest risk (both, nearly verbatim):** the kernel's distinctive semantics contribute
   nothing beyond what a generic typed store + executor + strong tool/RAG baseline already provide. →
   the **aligned-generic-store deconfound** is the highest-value early experiment.

6. **The single most promising direction (both converge):** a **narrow structured-domain (e.g. code)
   selective coprocessor** — deterministic extraction + a learned contract front-end that produces an
   ambiguity set + exact execution + bounded verify-retry / span-scoped speculative decoding — and
   demand a matched end-to-end win THERE, where syntax + deterministic extraction + clarification make
   the NL boundary tractable.

## Divergence
Minimal. The two analyses are unusually aligned. Fable adds the most explicit "kill list" (H-DD DORMANT,
NTP engine-trace gate, freeze scaffolding until a G2 result) and flags the a5-llm audit-ledger
contradiction; GPT-5.6 adds the sharpest framing of "delivery≠use / a correct checker cannot repair a
wrong formalization" and the positive-value abstention concern. No contradiction between them.

## Recommended steering for the next wave (pending maintainer ratification, issue #8)
- **Freeze new measurement-scaffolding design.** No more MF0/FRONT/ORACLE-class docs until a family
  produces a G2 (real-input) result.
- **Cut / DORMANT:** H-DD dimension-drop; deprioritise broad general-NL GNN fusion and deep-internal
  rule placements. Redirect that Fable spend to measurement.
- **Run the cheap decisive kills now (all ~$0 / CPU):** (a) the coverage-ceiling paper-kill (POWER rig,
  `poc/p3-power/`) on the existing censuses; (b) the aligned-generic-store deconfound; (c) the NTP
  "can the engine actually emit continuation sets / traces" gate; (d) stand up the real held-out NLB
  gate on the code vertical.
- **Pre-register the vertical (code) fork** as the primary W1 target; treat the general index as a
  stretch/secondary.
- **Human-annotation = P0 workstream** (the human-eval workbook is now delivered — aligned).

Concrete next beads to create once ratified: P3-E-POWER-0 (coverage-ceiling run), P3-E-DECONF-0
(aligned-generic-store deconfound), P3-E-NTP-GATE-0 (engine-trace emission), P3-D-NLB → P3-E-NLB-1 on
the code vertical; mark H-DD/SURG-design DORMANT.
