# Molecule-augmented generation S5 — DESIGN v2 (post-readiness-review revision + PROCEED decision)

**Status: DESIGN + DECISION ONLY — nothing run, nothing frozen, nothing committed by the
author.** This file REVISES `DESIGN.md` (v1) per the GPT-5.6-sol readiness review
(`docs/next/analysis/s5-readiness-review.md`, verdict NOT-YET-confirmatory) and the
ast-sweep interpretation (`docs/next/analysis/ast-sweep-interpretation.md`). The
maintainer has DELEGATED the pivot decision ("proceed based on Fable/Sol's best
judgement"); §0 below is that decision, made by fable (lead scientist). The coordinator
executes: build (§9) → adjudicate → freeze (§7) → run (§10) → commit.

v1 remains the record for the lexicon construction (§3), prompt/gate mechanics (§§4–5),
and the ALGORITHM_VERSION analysis (§9-v1). **v2 supersedes v1 §§2, 6, 7, 8** (arms,
judging, endpoint/stats, run plan). v1's Stage-2 (fitted-100 + held-out-30) is
**superseded and will not run as designed.**

Binding memory constraint honoured throughout: **no human fidelity judges are available
on this box.** The programme's stand-in is the **GPT-5.6 annotator-proxy** (standing
arrangement; measured anchor: human-vs-gpt-5.6 agreement κ≈0.756 on the g3 q1 face,
`docs/next/analysis/g3-human-proxy-reconciliation.md` — MEASURED, different task, so an
anchor not a guarantee), with human reconciliation of frozen artefacts deferred. Every
verdict this design produces is therefore **PROXY-PROVISIONAL** (same tag discipline as
g3). Tags: [MEASURED] cites an artefact by path; [STIPULATED] is a design choice;
[EXTRAPOLATION] is labelled arithmetic.

---

## 0. The PROCEED decision (delegated; this is what the coordinator runs)

**DECISION [STIPULATED, fable]: run ONE revised campaign — a right-sized,
fully-frozen, matched flat-ensemble-vs-molecule-ensemble comparison at n=200 fresh
concepts, judged by the LLM proxy panel standing in for Sol's two human fidelity
judges — explicitly labelled PROXY-PROVISIONAL, i.e. NOT confirmatory, but built so
that the identical frozen artefacts can later be human-re-judged to UPGRADE the same
run to confirmatory without regenerating anything.** A small pre-frozen pilot (n=24,
exploratory) runs first as an instrument shakedown with a direction-only futility
gate.

Why this and not the two obvious alternatives:

- **Not a small exploratory-only run (n≤30):** at n=30 the paired ensemble test needs
  ≥6 improvements with zero reversals just to cross p=.05 (readiness review, item 2 —
  MEASURED-from-review). It cannot move the programme decision ("is the lexicon worth
  maintaining/scaling?") in either direction, and its generated artefacts are too few
  to ever be upgraded by human judging. It spends real money to stay ignorant.
- **Not "wait for human judges":** none are available on the box and no arrival date
  exists. Waiting parks the programme's main open question indefinitely.
- **Why n=200 specifically:** it is Sol's own fixed design for the 15pp MCID
  (review item 3), and — the load-bearing economy — **generation is judge-agnostic**.
  The frozen 200-concept sample, the 800 frozen generated records, and the frozen
  expanded renderings are exactly the substrate two human judges would need. Generate
  once, judge twice: proxy now (this campaign), humans later (pure re-judging, zero
  regeneration, zero new design cycle). An n=30 run buys none of that.
- **Two-generator arms, not six:** the claim is anchored to the **Luna+Fable 2-model
  ensemble ceiling (14/24)**, NOT the six-generator 16/24 ceiling
  (`ast-sweep-interpretation.md` §2: the other four generators add only two successes).
  Sol's review explicitly permits this anchoring (item 1). Six-vs-six triples
  generation cost for two successes of headroom. [STIPULATED]

Headline numbers (details §§5, 8): **n=200 fresh + n=24 pilot; generators
gpt-5.6-luna + claude-fable-5; judges = F1 gpt-5.6-sol (annotator-proxy), F2
claude-opus-4-8, F3 gpt-5.6-terra adjudicator; ~3,800 LLM calls; ≈$90–260 (point
estimate ~$150); ~6–8 days elapsed, API-bound, resumable.** What a PASS/FAIL does and
does not license: §6 — read it before quoting any result.

---

## 1. Disposition of Sol's 7 revision items

| # | Sol's item | Disposition | Where |
|---|---|---|---|
| 1 | Matched E2-vs-E2 (or 6-vs-6) sole primary | **ADOPT** (2-generator E2; 6-vs-6 rejected on cost; claim anchored to the 2-model ceiling) | §2 |
| 2 | Both arms fresh, matched budgets, gate failures ITT | **ADOPT** for the n=200 main; pilot reuses existing flat records (Sol explicitly allowed this for exploratory), disclosed | §2, §5 |
| 3 | n≈200 for 15pp MCID (or 420 for 10pp) | **ADOPT n=200 / MCID 15pp.** 420-for-10pp rejected: a <15pp lift is below the materiality bar for maintaining a curated lexicon, and doubles cost | §5 |
| 4 | Two independent HUMAN fidelity judges + human adjudicator; LLM panel secondary | **ADAPT (constraint: no humans on box).** The fidelity protocol is implemented exactly as specced (independent judges, separate candidates, randomized order, frozen rubric, calibration, κ/AC1 reporting) but with the GPT-5.6 annotator-proxy + cross-vendor Opus as the two legs and Terra as adjudicator. Claims narrowed to PROXY-PROVISIONAL; human re-judging of the frozen artefacts is the pre-declared upgrade path | §3, §6 |
| 5 | Human-adjudicate all 31 bridges + dependency chains; provisional labels; conditional vs end-to-end fidelity separated | **ADOPT with proxy adjudicators** (same constraint, same narrowing): all 31 + their reference closure, ACCEPT/REPAIR/REJECT, relabel `provisional/model-authored`, chain-lossiness table, and a separated conditional-vs-expanded endpoint | §4, §3.3 |
| 6 | Freeze lexicon, sample, collisions, judges, prompts, ensemble rule, MCID, n, exclusions, CI/test, multiplicity, stopping — before generation | **ADOPT**: FREEZE-v2.json spec; the coordinator executes the freeze (the author freezes nothing) | §7 |
| 7 | Fitted-100 and per-generator results exploratory only | **ADOPT**: the fitted-100 in-sample arm is DROPPED from the campaign entirely; per-generator pairs are secondary on the fresh sample; the n=24 pilot is exploratory by construction | §2, §5 |

Sol's finding 4 (blinding / eval-fitting) is addressed structurally: the primary
instrument judges an **arm-neutral recursively-expanded rendering** (references
inlined, ids stripped), which both removes the gloss-credit bias (finding 3) and
restores approximate arm blindness; residual structural signature is disclosed (§3.4).
The fitted-evaluation problem is addressed by making the fresh n=200 the ONLY primary
sample. The `initiation`/`institution` lemma collision is resolved by a frozen
exclusion rule (§4.3).

## 2. Arms, cells, and the primary endpoint

Four matched cells per concept, all generated **fresh and interleaved** (per-concept
inner loop over cells, so arms share the generation period), same model snapshots, one
call per cell via the pinned `define_concept.py` runner with its default decoding and
internal retry budget — identical across arms; only the system prompt differs:

- **flat-Luna, flat-Fable** — pinned `concept-def-prompt.md`, pinned gate.
- **mol-Luna, mol-Fable** — composed `s5-prompt.md` (v1 §4), variant gate
  `validate-record-ref.mjs` (v1 §5).

**Ensemble outcomes (primary endpoint), per concept, intention-to-treat:**

```
Flat-E2 = 1  iff any of {flat-Luna, flat-Fable} has final verdict FAITHFUL
Mol-E2  = 1  iff any of {mol-Luna,  mol-Fable}  has final verdict FAITHFUL
```

under the PRIMARY instrument (§3). **ITT rule [STIPULATED]:** a cell that gate-fails,
returns no record, or is unjudgeable after retries counts NOT-FAITHFUL for its
ensemble (fail-closed; the count is reported). Every one of the 200 pairs is therefore
analyzable — no exclusions.

- **Primary test:** exact two-sided McNemar on the 200 (Flat-E2, Mol-E2) pairs.
  Effect: paired risk difference Δ̂ = (c−b)/n with a **Tango (1998) asymptotic score
  95% CI** (replaces v1's Wilson-on-discordant, per review item 2).
- **Decision rule [STIPULATED, frozen]:** SIGNIFICANT iff p<0.05 with Δ̂>0; MATERIAL
  iff Δ̂ ≥ +15pp (MCID). **PROXY-PASS = SIGNIFICANT ∧ MATERIAL.** Significant-but-
  submaterial and reversal outcomes are reported as such, not spun.
- **Honesty caveat, pre-stated:** E2 is a best-of-two **oracle ceiling, not a
  deployable yield** (`ast-sweep-interpretation.md` §2). The comparison is fair
  because both arms get the same oracle.
- **Secondary endpoints** (nominal p-values, no multiplicity claim): (a) deployable
  **cascade** outcome per arm with the frozen S1-mirror selector — take the Luna cell
  if it gate-passed AND self-flags faithful, else the Fable cell — same McNemar;
  (b) per-generator paired deltas (Sol item 1: single-generator pairs are secondary);
  (c) self-flag lossy-rate delta (descriptive — the lossy bar moves with the
  vocabulary, v1 §10.5); (d) mean quality delta; (e) reference-usage stats incl.
  zero-ref share (if mol cells barely reference, a null is about prompt uptake, not
  composition — v1 §7.3); (f) gate pass rates incl. `ERR_REF_*`; (g) the
  conditional-vs-expanded **credit gap** (§3.2); (h) judge agreement (§3.3).
- **Multiplicity:** exactly one primary. **Stopping rule:** fixed n=200, no interim
  looks at stage-3 data; the only gate is the pre-stage-3 pilot futility gate (§5).

**Predicted effect [STIPULATED, recorded before any run — Sol item 2 requires an
ensemble-level prediction]:** from v1 §7.4's single-generator chain: Flat-E2 ≈
45–58/100, Mol-E2 ≈ 60–75/100, lift **+12–20pp** at 25–40% discordance. Honest
guesses to be scored against, not claims.

## 3. Judging — the v2 instrument (proxy fidelity protocol)

### 3.1 Arm-neutral expanded rendering (fixes the semantic-credit bias)

A deterministic expander (`run_s5.py expand`, §9) rewrites every candidate into a
canonical rendering: each `{"kind":"concept","id":…}` node is replaced by a
self-contained nested block `{"kind":"subExplication", frame, referents, clauses}`
holding the referenced record's explication, **recursively, memoised, fail-closed** on
unresolved ids/cycles (mirroring `encodeConceptSet` semantics — the rendering shows
what is actually encoded, not the gloss). All ids, labels, `references` fields, notes,
and self-flags are stripped. Flat candidates pass through byte-identically. Rendering
sha256s are recorded. Consequences:

- Judges credit **only meaning present in the recursively encoded AST** — Sol
  finding 3's endpoint bias is structurally removed for the primary.
- The rendering is prime-only, so the unmodified base rubric applies.
- **Blinding improves but is not perfect:** no reference markers survive, but an
  inlined sub-explication has a recognizable structural signature. Call this
  candidate-label blinding + arm-neutralized rendering; residual signature DISCLOSED.
  (Presentation-only change; `encoder/` untouched, no ALGORITHM_VERSION bump.)

### 3.2 Two instruments, two endpoints (Sol item 5)

- **PRIMARY — end-to-end expanded-AST fidelity:** base `judge_prompt.md` +
  `judge-addendum-v2.md` (this directory): **one candidate per judge call** (kills
  within-concept anchoring), expanded rendering only, seeded-shuffled queue order,
  blind candidate ids, verdict format unchanged (FAITHFUL/LOSSY, missing, quality
  0–3, reason).
- **SECONDARY — conditional composition fidelity:** the v1 `judge-addendum.md`
  gloss-credit protocol, also single-candidate, run ONLY on reference-bearing mol
  cells (flat and zero-ref cells are identical under both instruments). Per-candidate
  `conditional-FAITHFUL ∧ expanded-LOSSY` = the **credit gap** — the meaning the gloss
  promises but the encoded AST does not carry. Reported separately; never enters the
  primary.

### 3.3 The panel (proxy stand-in for Sol's two humans + adjudicator)

| leg | model | role |
|---|---|---|
| F1 | gpt-5.6-sol | fidelity judge 1 — the standing **GPT-5.6 annotator-proxy** (measured human-agreement anchor κ≈0.756 on the g3 q1 face; reconciled against a human sheet later per the standing directive) |
| F2 | claude-opus-4-8 | fidelity judge 2 — cross-vendor |
| F3 | gpt-5.6-terra | adjudicator, F1/F2 disagreements only; final verdict = majority |

Frank statement of what this is NOT [STIPULATED]: two LLM legs are cross-vendor but
NOT independent in the human sense — they share training-corpus bias with each other
and with the generators (F1 shares a family with luna; F2 with fable, both
directions). Correlated pro- or anti-composition bias will not fully surface as
disagreement. That is precisely why every verdict is PROXY-PROVISIONAL and why the
human re-judge path exists.

**Calibration + rubric freeze:** before the freeze, 6 calibration concepts (drawn
from consensus-100 — never in the fresh sample) run through the fidelity instrument;
rubric edits are allowed ONLY pre-freeze. **Reliability reporting [frozen]:** raw
agreement, Cohen's κ, and Gwet's AC1 with seeded-bootstrap 95% CIs — overall, by arm,
and by reference status (Sol item 2's protocol, verbatim where implementable).

## 4. Bridge-lexicon adjudication (before anything is generated)

### 4.1 Proxy adjudication of all 31 + dependency chains

Every `urn:molaug-v0:*` record AND every kernel-v0 record in the bridges' reference
closure (≈10: give, take, make, death, birth, right, wrong, event, learn, …computed
mechanically from `lexicon/manifest.json`) is independently reviewed by F1 and F2
(F3 on disagreement) against a frozen bridge-review rubric: (a) gloss meets the
scholarly bar; (b) the explication (judged on its OWN expanded rendering) carries the
gloss's criterial content; (c) the faithful/lossy self-flag is correct; (d) the
record's sense collides with no evaluation sense. Verdicts **ACCEPT / REPAIR /
REJECT**; REPAIR/REJECT go back through the explicator + validator loop; the manifest
is rebuilt (new `lexiconSetHash`), prompts recomposed, changed records re-adjudicated.
This replaces v1 §3.3.5's "≥5 spot-check".

### 4.2 Labels and chain-lossiness

All 31 records are relabelled **`provisional/model-authored (proxy-adjudicated)`** —
nothing is called validated or research-grade on mechanical validation + proxy review
alone (Sol finding 3). A per-bridge **chain-status table** is published: a bridge is
*chain-lossy* if any record in its reference closure is self- or adjudicated-lossy
(e.g. `institution` is chain-lossy via `law`→`authority` even though self-faithful).
Generated outputs referencing chain-lossy bridges are marked conditional/provisional
in the readout. Item-level human acceptance remains required before any output enters
a "validated inventory" — out of scope here, pre-declared.

### 4.3 Collision rule (frozen) — resolves initiation/institution

**Frozen rule [STIPULATED]:** a candidate concept is eligible for the fresh sample
only if NONE of its lemma slugs matches any of the 85 lexicon id slugs
(already implemented — `run_s5.py cmd_sample` builds `slugs` from ALL lemmas; this
mechanically excludes `initiation`, whose lemma list contains `institution`). The
manifest's anti-leakage gate is re-run with the fresh sample present so
`slugCollisionGate` covers it. Consensus-100's `initiation` is flagged and confined
to exploratory analyses (its sample is dropped from the campaign anyway, §1 item 7).

## 5. Samples, power, and the pilot gate

- **Fresh sample (PRIMARY): n=200**, drawn by the frozen deterministic rule:
  `f1k-eligibility/candidate-pool.json` (28,818 candidates — MEASURED) sorted by URN
  byte order; exclude consensus-100 URNs, all-lemma lexicon collisions (§4.3), and
  the 6 calibration concepts; stride indices `floor(i·n_elig/200)`. Frozen (file +
  sha256 in FREEZE-v2.json) before any generation.
- **Power [EXTRAPOLATION, from the review's sizing]:** at 30–40% discordance, an
  observed 15pp lift needs n≈141–187 for 90% power → **n=200 gives >90% for the MCID
  as observed.** If judge noise attenuates a true 15pp to ~10.5pp (the review's
  illustrative 63.2%-agreement scenario), 80% power needs n≈214–285 → n=200 is
  **modestly underpowered (~70–80%) in that worst case — disclosed.** Two reasons not
  to inflate n further: (i) the single-candidate + expanded-rendering instrument is
  designed to beat the pooled instrument's 63.2% agreement floor (measured κ/AC1 will
  say — we do not assume it); (ii) the run is PROXY-PROVISIONAL either way; the
  confirmatory power question is settled at human re-judge time on the same n=200
  substrate.
- **Pilot (Step A, exploratory): n=24** — the existing `ast-pipeline/sample.json`
  (stratified 4/12/8, fitted, disclosed). Mol cells generated fresh (48 calls); flat
  cells reuse the existing consensus-100 records (0 calls; budget mismatch disclosed —
  Sol explicitly allows existing flat records for the exploratory pilot). Judged under
  the frozen v2 instrument. Purpose: instrument shakedown + futility only.
  **Futility gate [STIPULATED, frozen]: proceed to Step B unless (a) pilot
  Mol-E2 − Flat-E2 ≤ 0pp (direction-only kill — n=24 can kill, never confirm), or
  (b) mol-arm zero-ref share ≥ 80% (uptake failure ⇒ fix the prompt, do not burn the
  fresh sample).**

## 6. What a result licenses (read this before quoting anything)

**PROXY-PASS licenses [MEASURED, proxy instrument]:** "On fresh WordNet-stride
concepts, letting the generators compose from the provisional molaug-v0 reference
inventory raises judge-confirmed best-of-two **AST-faithful YIELD** over a matched
flat ensemble by Δ̂ [CI], under a frozen, blinded, expanded-rendering LLM proxy
panel." Per Sol's finding 3, the claim is exactly the narrowed one: **composition
improves yield on this approximate inventory.**

It does **NOT** license:
1. "Prime-grounded formal fidelity improved" as a human-grade claim — the fidelity
   judges are LLM proxies; PROXY-PROVISIONAL until the frozen artefacts are
   human-re-judged (the pre-declared upgrade path).
2. Any **deployable** yield claim — E2 is an oracle ceiling; the cascade secondary is
   informative but unpowered.
3. "The inventory is validated" — bridges remain provisional/model-authored;
   chain-lossy conditionality applies (§4.2).
4. Anything about the six-generator ceiling (claim anchored to the 2-model ceiling),
   or about distributions beyond the candidate pool.

**PROXY-FAIL licenses:** "No evidence at MCID that composition beats the flat ensemble
under this instrument" ⇒ deprioritize lexicon scaling (v1 §7.3 interpretation rule)
pending human reconciliation — with two pre-stated outs: attenuation can mask true
effects ≲10pp, and a high zero-ref share re-scopes the null to generation-policy
uptake. A significant **reversal** (composition hurts) is reported as such and kills
FULL-tier work outright.

**Either way:** the frozen sample, records, renderings, and verdicts are packaged as a
human-adjudication kit (`s5-run/stage3/human-rejudge-kit/`); the human pass upgrades or
overturns THIS run — no regeneration, mirroring the g3 reconcile-and-re-run pattern.

## 7. Freeze manifest (coordinator executes; the author freezes nothing)

`FREEZE-v2.json`, written by `run_s5.py freeze` AFTER adjudication+repairs+calibration
and BEFORE any stage-1/stage-3 generation, sha256-pinning: `lexiconSetHash`
(post-adjudication) + `encoderContentHash`; `s5-prompt.md`; both judge prompts
(fidelity + conditional); expander code hash; the fresh-sample file + its selection
rule text; the collision rule + adjudicated warnings; generator ids + decoding/retry
budget; judge ids F1/F2/F3 + majority rule; ensemble rule; cascade rule; MCID=15pp;
n=200; ITT rule; primary test + Tango CI; multiplicity; stopping rule; pilot futility
gate; calibration transcript hashes. Any post-freeze change to a pinned input ⇒ the
run is exploratory, full stop.

## 8. Cost + timeline [EXTRAPOLATION from ast-pipeline/DESIGN §7 cost anchors]

Anchors (MEASURED there): claude-fable-5 gen median $0.034 / mean $0.073 per call;
codex-side calls are subscription quota (~$0.004–0.01 nominal); opus judge calls
scale with input (single-candidate inputs are small: ~$0.05–0.15).

| item | calls | est. $ |
|---|---|---|
| Bridge adjudication: ~41 records × (F1+F2) + ~F3 | ~100 | $6–20 (opus leg) + quota |
| Bridge repairs (explicator sessions) | ~5–10 | $2–8 |
| Calibration: 6 concepts (12 gen + judging) | ~60 | $3–6 |
| Pilot gen: 24×2 mol cells | 48 | $2–3 |
| Pilot judging (96 cands × 2 + F3) | ~220 | $6–16 |
| Main gen: 200×4 fresh interleaved | 800 | $16–33 |
| Main fidelity judging (800 cands × 2 + ~30% F3) | ~1,840 | $45–130 (opus 800) + quota |
| Main conditional pass (~240–320 ref-bearing cands × 2 + F3) | ~640–800 | $13–48 |
| **Total** | **~3,800** | **≈ $90–260 (point ~$150)** |

Wall-clock: build+selftest ~1 day; adjudication+repairs ~1–1.5; calibrate+freeze ~0.5;
pilot ~0.5–1; main gen ~1; judging ~2–3 (API-bound, per-file resumable, `nice -n 10`
on this box's 2 shared cores); score ~0.5 ⇒ **~6–8 days elapsed.**

## 9. run_s5.py v2 code changes (TO BUILD by the coordinator/builder; selftest-gated)

Additions (~400 lines; the v1 verbs and the offline selftest stay green; every new
path fails closed):

1. **`cmd_sample --stage 3`** — the §5 frozen rule (generalize the existing stage-2
   sampler: `n=200`, add calibration-concept exclusion; write
   `s5-run/stage3-fresh.json`). Stage-2 sampling is retired.
2. **`cmd_gen --stage 3`** — per-concept interleaved inner loop over the 4 cells:
   flat legs via pinned prompt + pinned gate (existing `rp.run_define` report),
   mol legs via `s5-prompt.md` + `s5_gate`; dirs `stage3/gen-flat-fresh/`,
   `stage3/gen-s5-fresh/`; identical attempt budget both arms.
3. **`expand_ast(doc, lexicon_docs)` + `cmd_expand --stage N`** — recursive memoised
   ConceptRef→`subExplication` inliner per §3.1 (fail closed: unresolved id, cycle,
   depth>6); strips ids/labels/notes/references; byte-stable output +
   `expanded-manifest.json` sha256s; flat records must pass through byte-identical.
4. **`cmd_prep --stage N --instrument fidelity|conditional`** — ONE judge-input file
   per candidate (`judge-inputs-<instrument>/<blindid>.txt`, blindid = seeded 6-hex),
   fidelity = header + expanded rendering (no REFERENCED CONCEPTS block); conditional
   = header + raw AST + gloss block (v1 addendum), ref-bearing mol cells only; seeded
   global queue-order file; blind key held back (`judge-key-v2.json`).
5. **`cmd_judge --stage N --instrument … --judge F1|F2|F3 --i-am-the-coordinator`** —
   per-candidate loop over the queue order, composed prompt
   (`s5-judge-fidelity.md` = base `judge_prompt.md` + `judge-addendum-v2.md`;
   `s5-judge-conditional.md` = base + v1 `judge-addendum.md` + single-candidate note),
   reusing `rp.judge_one`'s call plumbing with pool-of-one inputs; F3 judges only
   F1/F2-disagreement blindids; resumable per blindid.
6. **`cmd_score --stage N --v2`** — per-concept cell verdicts (ITT: missing/gate-fail
   ⇒ NOT-FAITHFUL, counts reported) → Flat-E2/Mol-E2; exact McNemar (reuse
   `mcnemar_exact`); **new `tango_ci(b, c, n)`** paired-difference score CI (unit
   test: known reference value); cascade + per-generator secondaries; κ + Gwet AC1 +
   seeded bootstrap CIs overall/by arm/by ref status; credit-gap table
   (conditional∧¬expanded); pilot futility-gate verdict on `--stage 1`; writes
   `results-s5-v2.{json,md}` + the human-rejudge kit.
7. **`cmd_adjudicate_lexicon`** — closure computation from the manifest; F1/F2 review
   calls with a frozen bridge rubric; F3 on disagreement; verdicts to
   `lexicon/adjudication/`; `--summarize` ACCEPT/REPAIR/REJECT + chain-status table;
   relabels records `provisional/model-authored (proxy-adjudicated)`.
8. **`cmd_compose --v2`**, **`cmd_calibrate`**, **`cmd_freeze`** (writes
   FREEZE-v2.json per §7; every later verb verifies the pins and dies on mismatch).
9. **Selftest additions (must be green before any call):** expander goldens (teacher-
   ref record expands; flat byte-identical; synthetic cycle fails closed), Tango CI
   unit value, single-candidate prep shape + blindid determinism, ITT/E2 scoring
   truth-table on synthetic verdicts, freeze-pin mismatch dies.

## 10. Coordinator run commands (build → adjudicate → freeze → pilot → main → score)

```bash
cd poc/scale/molecule-aug
# 0 BUILD: implement §9 in run_s5.py (+ judge-addendum-v2 already in this dir), then:
python3 run_s5.py selftest                                   # green incl. v2 checks, or stop
# 1 LEXICON ADJUDICATION (all 31 + closure; repairs loop until clean)
nice -n 10 python3 run_s5.py adjudicate-lexicon --judge F1 --i-am-the-coordinator
nice -n 10 python3 run_s5.py adjudicate-lexicon --judge F2 --i-am-the-coordinator
nice -n 10 python3 run_s5.py adjudicate-lexicon --judge F3 --i-am-the-coordinator   # disagreements only
python3 run_s5.py adjudicate-lexicon --summarize             # ACCEPT/REPAIR/REJECT + chain table
#   explicator repairs REPAIR/REJECT records, then re-pin + recompose:
node lexicon/build_manifest.mjs
python3 run_s5.py compose --v2
# 2 SAMPLE + CALIBRATE + FREEZE
python3 run_s5.py sample --stage 3                           # 200 fresh (frozen rule §5)
node lexicon/build_manifest.mjs                              # anti-leakage gate now covers the fresh sample
python3 run_s5.py calibrate --i-am-the-coordinator           # 6 non-eval concepts; rubric edits ONLY before freeze
python3 run_s5.py freeze                                     # FREEZE-v2.json — after this, nothing changes
# 3 STEP A — pilot shakedown (n=24, exploratory; futility gate only)
nice -n 10 python3 run_s5.py gen --stage 1
python3 run_s5.py expand --stage 1
python3 run_s5.py prep --stage 1 --instrument fidelity
for J in F1 F2 F3; do nice -n 10 python3 run_s5.py judge --stage 1 --instrument fidelity --judge $J --i-am-the-coordinator; done
python3 run_s5.py score --stage 1 --v2      # STOP iff Mol-E2−Flat-E2 ≤ 0pp OR zero-ref share ≥ 0.8
# 4 STEP B — main (n=200 fresh, 4 matched cells, interleaved)
nice -n 10 python3 run_s5.py gen --stage 3
python3 run_s5.py expand --stage 3
python3 run_s5.py prep --stage 3 --instrument fidelity
for J in F1 F2 F3; do nice -n 10 python3 run_s5.py judge --stage 3 --instrument fidelity --judge $J --i-am-the-coordinator; done
python3 run_s5.py prep --stage 3 --instrument conditional
for J in F1 F2 F3; do nice -n 10 python3 run_s5.py judge --stage 3 --instrument conditional --judge $J --i-am-the-coordinator; done
python3 run_s5.py score --stage 3 --v2      # PROXY-PASS/FAIL readout + human-rejudge kit
```

Long legs: launch with `nohup`+`setsid` (per the standing Modal/E5 lesson — the
harness timeout must not orphan a half-judged stage).

## 11. Limitations (v1 §10 still applies; v2 adds)

1. **The judges are proxies.** Cross-vendor LLM legs, not humans; correlated bias is
   possible and unmeasurable from agreement alone. Everything is PROXY-PROVISIONAL.
2. **Expansion blinding is imperfect** — structural signature of inlined blocks.
3. **E2 is an oracle ceiling** — the deployable question rides the unpowered cascade
   secondary.
4. **n=200 is underpowered (~70–80%) under worst-case attenuation** of a true 15pp
   effect — disclosed; the instrument redesign targets exactly that attenuation.
5. **Bridges remain provisional** even after proxy adjudication; chain-lossy
   conditionality caps what "faithful" means for outputs that import them.
