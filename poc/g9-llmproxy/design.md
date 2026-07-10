# g9-llmproxy — design note + pre-registration text (prereg_doc for registry/experiments/g9-llmproxy.json)

> STATUS: DESIGN (record DRAFT). STAND-IN, NOT THE ADJUDICATING REVIEW. The
> maintainer requested (2026-07-10) blind-LLM stand-ins for the outstanding
> human annotation passes so the experiments can run now and be human-verified
> later, on the exact model of `f2b-transfer-llmproxy` [STIPULATED: ASM-0550].
> This record puts a pinned, kernel-instance-naive, cross-vendor LLM in the
> g9.review blinded-reviewer role. `registry/experiments/g9.json`
> (frozen_sha256 cf56c5ce…) is byte-untouched: its GATE-H blinded HUMAN review
> remains the ONLY discharger of its `blinded_review_done` instrument gate and
> the ONLY adjudicator of HS-A. Designed by FABLE (designer-1,
> experiment-designer role); execution is Opus-runner work, mechanical,
> post-freeze; any situation this design does not decide is a BOUNDARY STOP
> back to Fable, never runner improvisation.

## S1. Fresh id, human record untouched

DECISION: mint `g9-llmproxy`; g9 stays FROZEN-UNRUN with its review round
unconsumed [STIPULATED: ASM-0550, ASM-0520]. The f2b-transfer-llmproxy S1
grounds carry over verbatim: reviewer identity is design scope (a different
estimand — LLM endorsement, not blinded human review); consuming g9's single
review stage on the weaker instrument would exile the definitive human review
to a new id; the proxy takes the suffixed id.

## S2. The judged task (per-sheet, blind)

Items: the 50 BLINDED review sheets of
`data/authored-explication-set/review/sheets.json`
(sha256 55082b1588c1c4f55b15fd07c6fbbc1b941d8fcb948de94e69b3f0e1d05b8c7c;
inside the g9-pinned corpus digest 6a51f44a…). These are byte-identical to the
human g9.review materials: word, dictionary def, examples, ambig_examples
(`<UNK>` gaps), candidate explication; dataset reference explication and all
authoring notes withheld by the selection-manifest blinding rule.

Per-sheet prompt (mechanical template, staged at run time as
`poc/g9-llmproxy/judge-invocation.md` + prompt template + output schema, pinned
by ops amendment before any real call): render the sheet fields verbatim, with
`candidate_explication` re-labelled "proposed paraphrase" (the term
"explication" is an NSM term of art and a tradition cue; renaming reduces — it
cannot eliminate — style cueing) [STIPULATED: ASM-0521]. Two questions, one
call, server-side output schema `{substitutable, cross_translatable}`, each
`yes / no / cannot-say`:

- Q-SUB (substitutability, Baartmans-et-al. metric definition as carried on
  the human sheets): if the proposed paraphrase replaces the word in each
  example, and fills the `<UNK>` gap in each ambiguous example, is the meaning
  of each passage preserved — i.e. can the paraphrase stand in for this word
  in these uses?
- Q-XT (cross-translatability, judged form): does the paraphrase use only
  simple words that could be said in more or less any language, avoiding
  words more complex or more culture-specific than the word being defined?

Composite pass per sheet = mechanical legality (MEASURED:
`data/authored-explication-set/validation/mechanical-summary.json`, 50/50,
sha256 a8c8ef69…) AND `substitutable = yes` AND `cross_translatable = yes`.
`cannot-say` counts against composite pass (endorsement withheld — the f2b
escape-as-disagreement rule; conservative against PASS).

## S3. Judge mechanism and why

judge-r1p-gpt56sol: `gpt-5.6-sol`, reasoning effort `low`, via npx-pinned
`@openai/codex@0.144.1` `exec`, invocation form byte-derived from
`poc/truthstyle-2x2/judges-invocation.md` §4.1 (itself byte-derived from
`data/d-adj-t-llmproxy/judge-1p-invocation.md` §3): per-item stateless call,
empty out-of-repo workdir, `--ignore-user-config`, memories + web search
disabled, read-only sandbox, server-side output-schema enum, zero-tool
tripwire, first-valid-answer-final, ≤ 3 content attempts then no-label (never
mapped to an answer). CROSS-VENDOR IS MANDATORY here, not a convenience: the
50 explications are Fable-authored (arm `fable-class-authoring`), so any
Claude-family judge would grade its own family's authoring — the
design-vs-judge separation that governed f2b-transfer-llmproxy forbids it
[STIPULATED: ASM-0520]. The in-session Agent-tool sub-agent form is FORBIDDEN
(it injects project CLAUDE.md + auto-memory; ASM-0240 finding, carried over).

Blinding audit (mechanical, per call): grep prompt bytes + captured events for
`kernel`, `nsm`, `deepnsm`, `baartman`, `explication` — any hit ⇒ ABORT to
Fable. Item order: seed-pinned shuffle `g9lp/1|judge-r1p|20260710` (sha256
ranking as in the truthstyle spec). Preflight: 2 pinned calibration sheets
(trivially easy; one plainly substitutable + translatable paraphrase expected
yes/yes, one plainly wrong paraphrase expected no on Q-SUB) must pass
first-attempt before any real item.

## S4. Instrument controls

- Deranged-explication probe (content-scramble control, house idiom): 50 probe
  items — sheet i's word/def/examples paired with sheet σ(i)'s proposed
  paraphrase, σ a seed-pinned Sattolo cycle (`g9lp/1|probe|20260710`) so no
  sheet keeps its own paraphrase. Correct Q-SUB answer is `no` by construction
  (50 distinct DeepNSM test-split words; near-synonym collision risk disclosed
  as negligible-but-nonzero) [STIPULATED: ASM-0523]. Gate: probe coverage
  ≥ 45/50 AND Q-SUB false-endorsement (yes) rate < 0.30, else
  INSTRUMENT-INVALID. Probe Q-XT is REPORTED-ONLY: cross-translatability is a
  text-intrinsic property, so the probe cannot control it — the Q-XT leg has
  NO content-scramble control by construction, disclosed as a binding
  weakening [STIPULATED: ASM-0523].
- Retest stability floor: 10 seed-pinned duplicate sheets
  (`g9lp/1|retest|20260710`, first 10) re-asked after the probe pass; raw
  per-field self-agreement ≥ 0.80 required, else INSTRUMENT-INVALID. FAIL
  direction only; its pass direction validates nothing (single judge).
- Coverage: n_labelled (both fields valid) ≥ 45/50, no-label ≤ 5, else
  INSTRUMENT-INVALID.

## S5. Statistic, gate, decidability

A_g9p = n_composite_pass_proxy / n_labelled. One-sided 95% Wilson bounds
(z = 1.645, the pinned analysis/g9.py closed form). margin_threshold = the
frozen g9 bar verbatim: DeepNSM-8B published point 0.24 + 0.10 = 0.34.
PASS-analog iff Wilson LB ≥ 0.34; FAIL-analog iff Wilson UB < 0.34; else
INCONCLUSIVE. Decidability at the frozen expected rate 0.60, n = 50: LB ≈
0.484 ≥ 0.34 (clears); FAIL-analog reachable from true rates ≲ 0.22 (UB at
0.20, n = 50 ≈ 0.307 < 0.34); both branches live at the n_labelled floor 45.
Analysis script `analysis/g9_llmproxy.py` (PINNED-AT-FREEZE) consumes the
run-log counts; outputs listed in the record's pins.

## S6. What the outcome can and cannot mean

The record's `extrapolation_envelope_verbatim` is the binding text; summary:
the estimand is one cross-vendor LLM's blind endorsement, NOT the g9 GATE-H
human review; severity is uncalibrated to the published DeepNSM evaluation
protocol, so the ±10-point margin comparison is form-preserving only
[EXTRAPOLATION: ASM-0522 — resolved by the human g9.review on identical
sheets]; the Q-XT leg is the weakest (judged property, no content control);
tradition familiarity plausibly inflates endorsement (ASM-0552). A PASS-analog
licenses ONLY continued investment (human reviewer recruitment, authoring
pipeline continuation); it does not adjudicate HS-A, does not touch the
why-now argument, does not set `blinded_review_done` for g9, and is
quarantined as a WEAK FEASIBILITY PROXY pending the human review. Proxy
per-sheet labels are pinned so the eventual human review yields a free
human-vs-proxy bias measurement (ASM-0553); proxy outputs must never be shown
to the human reviewer beforehand.

Budget: ≈ 112 calls (50 + 50 probe + 10 retest + 2 preflight), Tier 0,
usd_cap 10, zero GPU.
