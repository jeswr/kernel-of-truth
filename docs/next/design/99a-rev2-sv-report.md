# 99a Rev2 — source-verification [SV] report (PARTIAL: repo-citation half)

> Bead-prescribed stage after Rev2: critique → Rev2 → **source-verify [SV]** → maintainer.
> This report covers the **repository-citation half** of the [SV] worklist (the newly
> prior-setting repo citations Finding 4 of the critique added), verified **mechanically**
> by the coordinator (exact source values matched against the proposal's claims — no
> literature judgement). The **external `[LIT-BACKED][SV]` literature items** (arXiv/DOI,
> proposal §5) are **NOT yet verified** — they require a web-capable literature-researcher
> lane, which was Fable-capped at the time of writing (2026-07-20). Do not treat 99a as
> maintainer-ready on the [SV] axis until the external-lit half is also confirmed.

## Overall verdict (partial)

**Repo-citation half: BOTH HOLD (CONFIRMED-AT-SOURCE).** No miscitation found in the two
repository citations the proposal makes load-bearing. **External-lit half: PENDING**
(capacity-blocked). No Rev3 is triggered by the repo half; the maintainer-readiness verdict
waits on the external-lit half.

## Per-citation findings (repo half)

### 1. RULES-2 — `registry/verdicts/rules-2.json` — **CONFIRMED-AT-SOURCE**
Proposal claims (§0b/§6/§8, e.g. lines 121–122, 820–821, 1138): "PASS, audit CONFIRMED
(2026-07-12), primary lift lower bound +0.316; content-drivenness secondary passed (a
forced-flip deranged closure did not retain the lift); permanent never-kernel-specific cap."

Verified at source:
- `verdict` = **PASS** ✓
- `audit.state` = **CONFIRMED** (`registry/audits/rules-2/1-gate-a-codex.json`) ✓
- `endpoint_results[primary]` (`/analysis/primary_lift_lb95`) = **0.31585081585…** → rounds
  to the quoted **+0.316** ✓
- content-drivenness secondary `sec-s1p-shuffled-closure` (`/analysis/s1p_pass`) = **true**
  → matches "a forced-flip deranged closure did not retain the lift" ✓
- The cap: `extrapolation_envelope_verbatim` scopes to "THIS closed rule inventory and THIS
  kinship vertical… license a SIGN, not a slope"; `scale_language_licensed` = **none** →
  consistent with the proposal's "never kernel-specific" characterisation ✓
- (Note for completeness: one secondary `sec-s4p-degradation-guard` = false; the proposal
  does **not** claim all secondaries passed, only the primary lift + the shuffled-closure
  secondary, both of which hold — so no over-claim.)

### 2. K-NULL 0.565× verifier-side FLOPs — `reports/auto/knull-v2/analysis-output.json` + `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md` — **CONFIRMED-AT-SOURCE**
Proposal claims (§0b, lines 110–118, 128–130, 299): the concise plain store was nominally
more accurate and used "~0.565× the verifier-side [FLOPs]", cited to the K-NULL dual-model
reconcile; framed "within its mechanism envelope"; figures tagged [MEASURED]; the
K-NULL→construction bridge retagged [EXTRAPOLATION] (critique Finding 4).

Verified at source:
- `reports/auto/knull-v2/analysis-output.json` contains **0.5652432440146643** → the quoted
  **~0.565×** ✓
- The cited reconcile doc `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`
  contains the **0.565×** figure and the "content can matter" half framing the proposal
  attributes to it ✓
- The proposal scopes it "within its mechanism envelope" and tags the figure [MEASURED] and
  the construction bridge [EXTRAPOLATION] — consistent with a descriptive-by-design read ✓

## Notes for the external-lit half (next stage)

The remaining [SV] scope (a web-capable literature-researcher lane must do these):
- The external `[LIT-BACKED][SV]` items enumerated in proposal **§5** — for each, reach the
  actual source (arXiv/DOI/publisher) and judge whether it supports the **specific** claim,
  watching the attribution caveat the proposal itself flags (dictionary-study figures ≠
  Harnad 1990).
- Surface the strongest published baseline/null if the proposal's lit framing omits one.

Only when the external-lit half also returns ALL-HOLD is 99a clear on the [SV] axis to go to
the maintainer; any MISCITED/UNVERIFIABLE external item triggers a targeted Rev3.
