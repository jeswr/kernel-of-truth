# P10 — The model↔record interface (how a model output becomes kernel-checkable)

**Status:** pre-registration component, 2026-07-08. Closes P7 RT-3 (CRITICAL). Governed by
`docs/kernel-design-directives.md` (binding). **Blocking for the e9.reg and f2.reg freezes:**
HC1, HC2, and HE1 (P1 §§2–3) may not freeze without pinning this interface choice and its
gate thresholds. Extends the S4 `decode-verify` skill contract (P4).
**Author:** Fable planning agent, for @jeswr. Coordination: sparq-org/sparq#1683.

## 1. The problem this page settles

Every correctness-track result hinges on the step where **a model's output becomes a record
the kernel can check**. That step was previously unspecified — and the one measured decode
number, **X2's 51/54, was measured on *encoder-produced* vectors, NOT on model outputs**. No
decode/extraction fidelity number exists yet for model-produced content. The interface is
therefore part of the *instrument*, its fidelity must be measured before hypothesis readout,
and its failures must never be scored as kernel successes or kernel failures.

## 2. The three candidate paths (enumerated)

| ID | Path | What is checked | Principal risk |
|---|---|---|---|
| **IF-A** | **Output extraction** — the model emits free text; a deterministic parser (optionally a leak-checked extractor model) converts it into candidate concept-records | extracted records | The verifier's catch rate is upper-bounded by extraction quality on free text — the hard, unmeasured part; extraction quietly becomes the experiment |
| **IF-B** | **Inverse-adapter** — the model emits soft vectors mapped back through an inverted E5 adapter into kernel space | decoded vectors | The adapter has never been built or validated in reverse; highest risk, zero prior evidence |
| **IF-C** | **Constrained-decoding format** — the model is constrained (grammar/JSON-schema decoding) to emit records directly in a pinned structured surface syntax | emitted records | The format affordance itself may help or hurt the host — a confound unless every arm gets the same affordance |

## 3. Pre-declared default and fork

- **Default: IF-C (constrained decoding)**, under the **shared-affordance rule** (§5). It
  makes extraction near-trivial, makes extraction failure *measurable* (a malformed record is
  an observable event, not a silent parse miss), and neutralises the format confound by
  granting the identical affordance to every arm.
- **Registered fork IF-1 (IF-C vs IF-A), deciding measurement pre-declared:** on a pilot
  slice (n = 200 outputs per rung, before e9/f2 final phase), measure (i) the
  **constrained-format tax** — the model-alone arm's accuracy delta with vs without the
  format constraint — and (ii) IF-A extraction fidelity on the held-out labelled set (§4).
  IF-A replaces IF-C **only if** the format tax is a degradation of Cohen's h ≥ 0.2 on
  model-alone accuracy (paired bootstrap, α = 0.05) AND IF-A extraction F1 ≥ 0.95 on the
  labelled set. Otherwise IF-C stands. The fork is decided once, before final-phase runs,
  and the choice is pinned in e9.reg/f2.reg.
- **IF-B is out of scope for v0**: excluded from HC1/HC2/HE1; it may be re-opened only by a
  new pre-registration, and only if F3/HE3 evidence establishes the adapter path it depends
  on.

## 4. The EXTRACTION-FAILURE INSTRUMENT GATE (binding; extends P8 `/gates/instrument_valid`)

- **Held-out labelled extraction set:** ≥300 model outputs per rung, annotated with gold
  records (annotation blind to arm identity), built before the final phase of the consuming
  experiment.
- **Two pre-declared rates**, measured on that set before any hypothesis readout:
  **extraction-failure rate** (output yields no well-formed record) and **extraction-error
  rate** (well-formed but wrong record vs gold).
- **Gate:** if the extraction-failure rate's Wilson 95% lower bound exceeds **10%** on the
  held-out set, the consuming experiment's verdict is **INSTRUMENT-INVALID** — an instrument
  event, never a kernel failure and never a kernel pass.
- **Accounting rule (no free wins, no free losses):** in hypothesis endpoints, unparseable
  outputs are excluded from BOTH the numerator and the denominator of catch/accuracy rates
  and logged on the instrument ledger; the verifier arm can neither harvest wins
  (unparseable ⇒ "caught" is forbidden) nor absorb losses. The exclusion count is rendered
  in every generated verdict.
- **Interaction with the decision tree (P1 §§1, 6):** an INSTRUMENT-INVALID here buys the
  single pre-declared replication (the repair itself pre-registered), per the replication-buy
  cap. E9/F2 carry **no** F6-style carve-out: a repeated extraction-instrument failure blocks
  a clean H0-NO and routes to STOP-AND-PUBLISH-UNDECIDED (P1 §6 route 5).

## 5. The shared-affordance rule

Any output-format constraint, schema, grammar, or few-shot format demonstration granted to
the kernel decode-verify arm is granted **verbatim** to every baseline arm — model-alone,
RAG-with-citations, gloss-dictionary, and gloss-text self-verify + retry. Arms differ only in
their verification instrument, never in their output affordances.

## 6. Scope note

This interface governs the **output side** (checking what a model asserts: HC1/E9, HC2/E9-C,
HE1–HE2/F2). It does not touch the input-side injection paths (E5/F3/F4 adapter), which are
separately validated. X2's 51/54 remains a valid measurement of the encoder→decoder path
only; no document may cite it as evidence about model-output decode fidelity.
