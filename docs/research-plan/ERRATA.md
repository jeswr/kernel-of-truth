# Research-plan errata (append-only; the pinned P1/P8 bytes are NEVER edited)

Authority: registry verdict objects + corrections > frozen prereg > design docs.
Each entry narrows a P1/P8 clause to measured scope; the original rows stay
byte-identical in place so frozen-record pins and family-membership provenance
(P1 §4b) remain verifiable against git history.

- **E-1 (2026-07-10, P1 §4b row HE5).** "Measured range: Store 10³–10⁶ records" is
  STALE: correction c-f1-1 removed the 1e3/1e6 rungs pre-freeze (never built); the
  f1 verdict records rungs_measured=["S1e5"], scale_language_licensed="none"
  (registry/verdicts/f1.json; f-efficiency D1).
- **E-2 (2026-07-10, P1 §4b row HE5).** "store-size axis extrapolates freely
  (measured B/rec is size-independent)" is WITHDRAWN as stated: size-independence
  is contradicted below ~1e4 records by the measured 2,348-record haiku-tier
  table+header overhead (docs/design-compact-kernel-serialization-v2.md §3.3).
  Binding reading: upward-only within the same stationary corpus process;
  elsewhere EXTRAPOLATION (assumption register, f1-scope entry). RETRO anchors
  mechanism existence only, not this representation's direction/effect.
- **E-3 (2026-07-10, P1 §4b row HS-A / g9).** "Extrapolates forward monotonically
  with author capability" is reclassified EXTRAPOLATION (unsupported projection;
  registered in registry/assumptions.jsonl, g9-monotonicity entry). Note also:
  g9 is a cross-study comparison — the ≥10-point margin vs DeepNSM-8B's published
  point substitutes for, but does not equal, a controlled head-to-head.
- **E-4 (2026-07-10, P8 §1.6-adjacent worked example + all HC3 narration).**
  Verdict/claim wording must index PRM comparisons to the NAMED tested checkpoint
  (Skywork-o1-Open-PRM-Qwen-2.5-1.5B, math-domain process PRM, zero-shot, pinned
  revision), never to "the 1.5B class" / "the tested PRM class" as a class claim
  (registry/corrections/f2b-replicate/3-claims-language-erratum.json; GPT-5.6 G4).
