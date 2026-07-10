# truthstyle-2x2 + f2b-errors — truth×style adjudication probe and the pre-frozen F2-line failure-cause taxonomy

> STATUS: **DRAFT, freeze-READY, NOT FROZEN.** Designed by FABLE
> (`kern/fable-designer`, experiment-designer role), 2026-07-10, as investigation line
> `truthstyle-2x2-f2-taxonomy`. Freeze is a coordinator/maintainer gate
> (`prereg-freeze.py`, NOT run here; `--dry-run` verified green). No GPU, no judge
> invocation, no spend has occurred; both harnesses are mock-green at $0.
>
> **TIMING-CRITICAL (the reason this exists now):** both artifacts protect the
> interpretation of `f2b-transfer` (FROZEN, frozen_sha256
> `b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879`) and lose
> confirmatory standing FOREVER once its Stage-2 unblinds — the R-2 superset-logging
> rule (`docs/next/resource-optimization-plan.md` §3.5) means an instrument not
> hash-pinned before outputs are inspected is retrospective storytelling. Freeze BOTH
> records before any Stage-2 GPU cell runs.

Dedup check (hard rule 1): re-verified against `registry/ideas.jsonl` (47+ ideas),
`registry/experiments/*.json`, and `docs/design-*.md` — no existing idea, record, or
design covers either artifact. Provenance: GPT-5.6 external review adoptions N2 and
N14 (`poc/gpt56-review/SYNTHESIS.md` §5 items 2–3; feasibility-synthesis §3d/§5 row 2).
This document is the `prereg_doc` for BOTH draft records.

Every load-bearing claim is tagged per the honesty-guard; marker lines are lintable.

---

## 1. Claim and hypotheses

### 1.1 What is at stake

PREMISE: the programme's only positive end-task result chain (f2b-replicate PASS +0.1507, audit CONFIRMED; f2b-transfer FROZEN in flight) is adjudicated by judge endorsement readings — the human judge-1 Stage-1 statistic A, and the llmproxy stand-in A₁ₚ = 0.95 (PASS-PENDING-AUDIT) [MEASURED: registry/verdicts/f2b-replicate.json; registry/verdicts/f2b-transfer-llmproxy.json].

PREMISE: the llmproxy verdict's own envelope names an uncontrolled channel — judges may endorse a familiar NSM explication STYLE rather than judge content (ASM-0021, kernel-tradition familiarity), and the deranged-gloss probe bounds only the crudest form (grossly wrong content); the live threat, "a semantically wrong answer written in canonical NSM shape", is untested [MEASURED: registry/verdicts/f2b-transfer-llmproxy.json, envelope clause 2 + H-PROXY-STYLE].

PREMISE: no registered control on the f2b line crosses truth with style; the 2×2 factorial is NEW (external review G2/N2, adopted; internal dedup re-verified above) [MEASURED: poc/gpt56-review/SYNTHESIS.md G2 cross-reference "NEW"].

### 1.2 truthstyle-2x2 — hypotheses (falsifiable)

- **H-STYLE-ROBUST (primary):** at matched truth and matched content, the NSM-shaped
  vs plain surface does not change judge acceptance by more than ±0.10 absolute
  (TOST equivalence at the pre-declared margin) for the pinned judge pool. If TRUE,
  judge endorsement readings on the f2b line are not materially style/familiarity-leaky
  at this margin, for this judge class.
- **H-STYLE-LEAKY (the alternative under test, symmetric):** the style main effect
  exceeds the margin (in either direction). If demonstrated, every f2b-line
  LLM-judge endorsement reading (A₁ₚ = 0.95 included) carries a measured style-bias
  band and cannot be read as pure content endorsement.
- **H-FALSE-ACCEPT-INFLATION (Holm secondary, the sharpest threat):** NSM shaping
  RAISES acceptance of semantically WRONG content (style effect on truth-wrong cells
  > 0, one-sided). This is the exact channel that would fabricate endorsement under
  H-CIRC.

### 1.3 f2b-errors — hypotheses

- **H-ROBUST (primary, conditional):** the f2b-transfer Stage-2 external-gold primary
  lift, if its frozen SAP rejects, survives concept-cluster resampling (one-sided 95%
  cluster-bootstrap lower bound > 0). This prices the G6 pseudo-replication risk
  (250 items over 108 concepts × 4 templates are not 250 independent units).
- **H-COMPOSITION (descriptive, no test):** Stage-2 verify-arm failures distribute
  over a CLOSED, pre-frozen cause taxonomy with residual X-OTHER ≤ 2%, with
  harmful-flip accounting — so post-hoc failure narratives are pinned before anyone
  sees an output.

### 1.4 Registered forks (design-space uncertainties, never silently decided)

- **FORK-1 (which tier carries the primary).** Options: (a) tier-1 wn31-external
  content (cleanest gold independence, but the deterministic open-vocabulary NSM
  transform is MEASURED near-null — 10/192 pairs differ beyond the preamble — so an
  equivalence primary there is dilution-biased toward false reassurance); (b) tier-2
  kernel-bytes content (the ACTUAL register at issue; manipulation strength MEASURED
  0.94 of pairs differ; truth gold is own/donor construction, STIPULATED).
  **DECIDED: (b)**, because an equivalence claim on a null manipulation is worthless —
  the false-reassurance failure mode dominates the gold-purity concern, and the primary
  estimand (a within-truth style CONTRAST on content-matched pairs) never scores
  against kernel-defined gold (§6.1). Deciding-experiment if contested: strengthen the
  tier-1 transform (new rules version) and re-run as a successor; kill for the tier-2
  choice = style-fidelity gate failure.
- **FORK-2 (judge pool composition).** Options: (a) f2b-line family only
  (GPT-5.6-Sol + GPT-5.5 — maximally decision-relevant, family-correlated);
  (b) + one non-GPT judge (Claude Haiku 4.5, pinned) for cross-vendor span, with the
  designer-family caveat disclosed (designer is Anthropic-family; the judge labels are
  raw DATA graded by a pinned pure-function script, not a grading/audit role — RUN≠AUDIT
  is not touched, and the cross-vendor AUDITOR remains Codex). **DECIDED: (b)**,
  equal-weight pool of 3; per-judge effects are Holm/reported members so a
  family-specific leak cannot hide in the pool mean. Kill: pool gate (any judge
  inverted or <90% labelled ⇒ INSTRUMENT-INVALID).
- **FORK-3 (human judges).** The probe CANNOT clear the pending human judge-1
  (envelope-bound). Options: (a) LLM-only now; (b) add a human rider on a subsample.
  **DECIDED: (a)** — LLM-only, because any human who judges d-ts items becomes
  permanently ineligible as an f2b-transfer judge (LS-4; tier-2 reuses canonical-gloss
  bytes) and kernel-naive humans are the scarcest resource on the line. The human
  style question transfers as a registered EXTRAPOLATION with resolution path = a
  post-Stage-1 human rider on fresh items (never before f2b-transfer Stage-1 completes).
- **FORK-4 (single-stimulus acceptance vs f2b's MCQ/claim formats).** Options:
  (a) replicate the f2b MCQ format (style varies WITHIN an option set — but then style
  is confounded with the S2 best-fit comparison, and acceptance-rate cells are not
  independent); (b) single-stimulus yes/no/cannot-say acceptance (clean factorial
  cells; format transfer to MCQ is a stipulation). **DECIDED: (b)** with the format
  transfer registered as STIPULATED (ASM to be minted at freeze; resolution path = an
  MCQ-format successor cell if the probe reads LEAKY).
- **FORK-5 (margin choice).** ±0.10 absolute (see §4.3 power/justification). A
  stricter 0.05 margin needs ~4× the adjudication budget; register 0.05 as the
  successor margin if the readout lands between.

---

## 2. What already exists (inputs, all hash-pinned)

| artifact | path | sha256 |
|---|---|---|
| d-ts items (808, built, pinned) | `data/d-ts/items.jsonl` | `9194f61713cc6cf01c34fa1ca97e01cd25b6b6d8c3bbae7db9a1772ac0c57a2d` |
| d-ts manifest | `data/d-ts/manifest.json` | `9fc7abbf25c871fb5ba66e18aa4e9c4c8dab1f339eb7be76749127341d88c600` |
| d-ts corpus pin (kot-corpus-hash/1) | `data/d-ts/` | `e4cac4571da392ac26b4d63f0653ec724ccbba70bb30a3346e47a2e87d93a900` |
| deterministic builder | `poc/truthstyle-2x2/build-dts.py` | `1edb96f46e726c5a961b042810a0ebcfdfc3be9a44547f50bb75861ee19d2849` |
| pinned style-rule tables | `poc/truthstyle-2x2/style-rules.json` | `b65837d4a1915a85b7632391e1b368398c9c79f7e3490e585d781e7d3478c902` |
| probe analysis (mock-green) | `analysis/truthstyle_2x2.py` | `bf171ed951c2100e0a768c9ecea571da604e912a08164e2dd563e103f1c071c8` |
| taxonomy (CLOSED set) | `poc/f2b-errors/taxonomy.json` | `4326ae11a60f097f24f93b0c26883df823861c022566344d64a72dca8285164c` |
| taxonomy analysis (mock-green) | `analysis/f2b_errors.py` | `ce9d15de59100aa235d4c5b04f1f43327de315740f9b9069b49f1fc158ab7d0e` |
| content source (external gold) | `data/lexical-wn31/` | corpus pin `5e76def82e38221a3b7deb3b39fd60adbd1e87b3b9905dd0055739b47a492799` |
| covered concepts + canonical renderings | `data/d-qa-t/` | corpus pin `7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27` (byte-identical to the frozen f2b-transfer pin) |

Mock commands (both exit 0, print `MOCK GREEN`, $0, no network):

```
python3 analysis/truthstyle_2x2.py --mock --labels <scratch>/dts-mock-labels.jsonl
python3 analysis/f2b_errors.py --mock --cells <scratch>/f2be-mock-cells.jsonl
```

---

## 3. truthstyle-2x2 design (minimal decisive form)

### 3.1 The 2×2 (×2 tiers), all items deterministic, NO LLM authorship

Factors: **truth** {correct, wrong} × **style** {nsm, plain}, content-matched within
pair (the same definition text in two registers), truth-matched in length (deranged
donor = cyclic shift +1 in gloss-length-sorted order within POS/tier — fixed-point-free
and length-adjacent by construction; length gate §3.6).

- **tier-2 (PRIMARY; 100 covered concepts × 4 cells = 400 items):** nsm pole = the
  canonical gloss VERBATIM (the exact bytes the f2b judges endorse); plain pole = the
  pinned `tier2_plainify_substitutions` (the INVERSE of the f2b-transfer §4.7 S6
  reading key — a closed controlled vocabulary, so the deterministic inverse is
  high-fidelity). Manipulation strength MEASURED at build: 188/200 content pairs
  differ (0.94 ≥ 0.80 gate). Truth gold = own vs deranged-donor gloss
  [STIPULATED: own-gloss-is-correct; under H-CIRC some "correct" labels would be
  false — but the primary is a style CONTRAST WITHIN truth level on content-matched
  pairs, which stays identified regardless of whether the truth labels are right].
- **tier-1 (INSTRUMENT + diagnostics; 96 wn31 words × 4 cells = 384 items):**
  content = WordNet 3.1 main-clause glosses; truth gold is fixed by the EXTERNAL
  lexicographic authority + derangement — fully independent of every kernel accept
  test (no probe word is a covered concept; LS-1). Its role: the
  truth-manipulation instrument gate (judges must separate own from deranged
  definitions on kernel-free ground, pooled truth effect ≥ 0.30) and per-judge
  inversion checks. Its style factor is reported as a diagnostic ONLY — the
  deterministic open-vocabulary NSM transform is MEASURED near-null (10/192 bodies
  differ), disclosed, and never carries an endpoint (FORK-1).
- **retest:** 24 seeded duplicates (":dup"), gate-only.

Question stem (pinned in the builder, identical bytes across cells) asks the S1
fit+identification question with the S6 register-immunity instruction INCLUDED — the
probe measures residual style leakage UNDER the same reading standards the f2b judges
operate with, which is the condition actually in force on the line. Escape token
(cannot-say) mandatory; acceptance := "yes"; "no" and escapes are non-acceptance
(escape rates reported per cell).

### 3.2 Judge pool (pinned, cross-vendor, blind)

| judge | model + pin | role |
|---|---|---|
| judge-p1-gpt56sol | `gpt-5.6-sol` via `npx -y @openai/codex@0.144.1`, effort low — byte-level invocation form of `data/d-adj-t-llmproxy/judge-1p-invocation.md` | the f2b-line judge whose A₁ₚ reading is being protected; own Holm member |
| judge-p2-gpt55 | GPT-5.5 via the same npx-pinned codex (catalog slug verified at staging; the GLOBAL codex 0.142.5 is NEVER touched while f2b judge runs are in flight) | second f2b-line family judge |
| judge-p3-haiku45 | Claude Haiku 4.5, pinned model id, temperature 0, pinned prompt (staged) | out-of-GPT-family span (FORK-2 disclosure applies) |

Blinding: per-item stateless invocations (no session memory ⇒ full within-content
crossing is clean); item order shuffled per judge with pinned seeds
`dts/1|judge-<p>|20260710`; judges see ONLY the question bytes — never tier, truth,
style, donor, provenance, or the word "kernel". Exact per-judge invocation specs are
staged as an ops amendment filling the record's declared `harness_manifest`
placeholder BEFORE any adjudication call (the f2b-transfer PINNED-AT-INPUTS pattern).

### 3.3 Estimand and primary endpoint (EXACTLY ONE)

**Primary:** style main effect on acceptance at matched truth =
mean over evaluable (judge, tier-2 content-pair) of [accept(nsm) − accept(plain)],
pooled equal-weight over the 3 judges, both truth levels. Inference: concept-cluster
percentile bootstrap (resample the 100 concepts, B=10000, seed 20260710); TOST per
P8 §1.5 (two one-sided tests at α=0.05 ⇔ the 5th–95th percentile interval inside
(−0.10, +0.10)).

Pre-declared trichotomy (mutually exclusive, verdict-rule ordered):
- **PASS (style-robust):** TOST passes.
- **FAIL (style-leaky):** the 90% interval lies entirely beyond +0.10 or entirely
  below −0.10 (leak demonstrated at the margin).
- **INCONCLUSIVE:** neither (straddle/underpowered).

**Consumer rule (conservative, pre-declared):** ONLY a PASS lifts the style-leak
guard on f2b-line judge-endorsement readings. FAIL *or* INCONCLUSIVE leaves the guard
in force: any citation of A₁ₚ = 0.95 (or the human Stage-1 A, for the stipulated
format-transfer scope) must carry the probe's measured interval as a style-bias band.
This asymmetry is deliberate — the probe is powered for equivalence, and a mid-size
leak reading INCONCLUSIVE must not silently pass as reassurance.

**Holm family (one family, 3 members, α=0.05):** (1) wrong-cell style inflation
(one-sided, tier-2 truth-wrong pairs — H-FALSE-ACCEPT-INFLATION); (2) correct-cell
style TOST (tier-2 truth-correct pairs); (3) judge-p1 (GPT-5.6-Sol) style TOST — the
llmproxy reading's own judge. Reported-only, never verdict-bearing: tier-1 style
diagnostic, truth effects both tiers, per-judge effects, escape rates by cell, retest
agreement, fidelity metrics.

### 3.4 Instrument gates (each with its own bound; failure ⇒ INSTRUMENT-INVALID, never a hypothesis outcome)

| gate | bound | why |
|---|---|---|
| label_coverage | ≥ 0.95 of 2,352 scored (item,judge) pairs labelled | missing labels are instrument events |
| pool | every judge ≥ 0.90 labelled AND per-judge tier-1 truth effect > 0 | an inverted or non-responsive judge invalidates the pool, not the hypothesis |
| truth_manipulation | tier-1 pooled truth effect ≥ 0.30 at n ≥ 200 | if judges cannot separate own from deranged definitions on KERNEL-FREE ground, acceptance is not measuring content and no style reading is interpretable |
| style_fidelity | tier-2 differing-pair fraction ≥ 0.80 AND marker-reduction ≥ 0.80 | an equivalence verdict on a null manipulation is forbidden by construction (FORK-1 lesson) |
| length_match | ≥ 0.90 of wrong-cells within ±35% of the correct twin's length | truth must not be cued by length |
| retest | agreement ≥ 0.85 over ≥ 48 duplicate judgments | label stability floor |

### 3.5 Power (justified on the item budget, planning constants STIPULATED)

Primary: 100 concept clusters × 2 truth levels × 3 judges = up to 600 paired
differences. With paired-discordance rate q and ICC ≈ 0.2 (design effect ≈ 2,
effective n ≈ 300): SE ≈ √q/√300. TOST power at margin 0.10
[STIPULATED planning constants, never emitted as measurements]:

| q (discordance) | true Δ = 0 | true Δ = 0.03 |
|---|---|---|
| 0.15 | ≈ 0.99 | ≈ 0.93 |
| 0.20 | ≈ 0.99 | ≈ 0.86 |
| 0.30 | ≈ 0.94 | ≈ 0.72 |

The FAIL direction is only well-powered for leaks ≥ ~0.15; that asymmetry is priced
into the conservative consumer rule (§3.3). Holm member 1 (one-sided) at these ns
detects inflation ≥ ~0.08 with power ≥ 0.85 at q ≤ 0.2.

### 3.6 Margin justification (why ±0.10)

The margin ties to the decision it protects: f2b-transfer Stage-1 expects A ≈ 0.85
against the kill-d bar 0.70 at n=360 (Wilson). A style bias ≤ 0.10 absolute cannot
carry an expected-A reading across that bar (0.85 − 0.10 = 0.75; Wilson LB ≈ 0.71 >
0.70 — the reading survives), while a bias > 0.10 could materially manufacture or
destroy an endorsement verdict. For the llmproxy reading (A₁ₚ = 0.95, bar 0.70) the
headroom is 0.25, so 0.10 is conservative there. [STIPULATED margin choice; FORK-5
registers 0.05 as the successor margin.]

### 3.7 Cost and compute

CPU only + bounded LLM adjudication: 808 items × 3 judges = 2,424 stateless
invocations (llmproxy anchor: 360 codex low-effort items ≈ $1–3 ⇒ ~$7–20 for the two
GPT judges; Haiku ≈ $1–3). Budget cap **$40**, zero GPU. Runtime: hours,
rate-limited, on the shared box. Owner to run: Opus runner (mechanical, after
freeze + maintainer sign-off). **No GPU ask.**

---

## 4. What a truthstyle-2x2 outcome licenses (envelope, binding)

- A **PASS** licenses exactly: "for THIS pinned 3-LLM judge pool, under the S1/S6
  standards in single-stimulus acceptance format, on d-ts (100 covered-concept
  canonical glosses + the pinned plainification, and 96 wn31 words), the style main
  effect is within ±0.10" — and therefore lifts the style-leak guard on f2b-line
  LLM-judge endorsement readings AT THAT MARGIN. It does NOT: validate kernel content
  (no endpoint scores agreement with gold); adjudicate H-TRANSFER vs H-CIRC; extend to
  HUMAN judges (registered extrapolation, FORK-3); extend to MCQ format beyond the
  FORK-4 stipulation; extend to margins < 0.10; or touch any frozen record.
- A **FAIL** licenses: "f2b-line LLM-judge endorsement readings carry a measured
  style bias band" — an interpretive guard on A₁ₚ and on any LLM-fallback judge-2
  reading; it AMENDS NOTHING frozen and does not by itself refute kernel content
  (a style-leaky judge is an instrument fact about judges).
- Coverage restatement (mandatory): kernel-expressibility coverage 0.3542 at rung
  molecules-v0, MEASURED by m0b on ONE incomplete kernel-v0 instance — the tier-2
  concepts are 100 of the same 108 covered concepts; nothing here extends coverage.
- Scale language: R0 (no host model anywhere); no rung claims of any kind.

---

## 5. f2b-errors design (taxonomy + declared re-analysis)

The CLOSED category set, deterministic assignment tree, required logged fields
(the R-2 superset-logging declaration toward Stage-2's harness staging), orthogonal
harmful/benign-flip accounting, cluster keys, and the declared concept-cluster
bootstrap re-analysis are specified machine-readably in
`poc/f2b-errors/taxonomy.json` (sha pinned in §2 and in the record) and implemented
verbatim by `analysis/f2b_errors.py`. Categories: X-EXTRACT, X-NONENGAGE,
X-GOLDCONFLICT (the H-CIRC-diagnostic mass: verifier-accepted ⇒ canonical content,
yet ext-wrong), X-EXHAUST-STABLE, X-EXHAUST-WANDER, X-OTHER (fail-closed residual,
gate ≤ 2%).

- **Primary (conditional):** concept-cluster bootstrap one-sided 95% LB of the
  Stage-2 primary effect > 0, evaluated ONLY if the Stage-2 frozen SAP rejects
  (else INCONCLUSIVE by rule — robustness of a lift is undefined without a lift).
  PASS = cluster-robust; FAIL = the Stage-2 PASS does not survive concept-cluster
  resampling (its inference is pseudo-replication-fragile). NEITHER outcome can flip
  the frozen f2b-transfer verdict (the verdict is a pure function of ITS frozen SAP);
  the consumer rule is that any claim citing a Stage-2 PASS must co-cite this record's
  `cluster_robust`.
- **Descriptive outputs (never verdict-bearing):** the composition table, gold-conflict
  rate, harmful/benign-flip accounting, cluster-CI width ratio (the measured price of
  pseudo-replication, feeding every successor SAP), leave-one-seed-out jackknife.
- **Retrospective twin:** the same procedure over `results-log/f2b-replicate.jsonl`
  is `phase:"exploratory"` (that record is already unblinded) — pricing information
  only, quarantined, uncitable as confirmation.
- **Cost:** ~$0 (CPU, minutes). **No GPU ask.** The only external dependency is the
  R-2 logging handoff (§7 item 2).

Envelope: scoped to the Stage-2 pipeline mechanics (string-equality verifier,
abstention off-coverage, fixed k=4, R1 host, d-qa-t items, blind external gold);
the taxonomy does not name causes outside what the logged fields can decide
(no "ambiguity"/"mapper" categories — this pipeline has no such stages, and inventing
them would be storytelling).

---

## 6. Pre-freeze skeptic memo (attack, then answer)

1. **Oracle leakage (the named class): does judge gold coincide with any kernel
   accept test?** The kernel accept test is string-equality to canonical records.
   Attack: tier-2 "correct-nsm" cells ARE canonical records, so a yes there is
   endorsement of kernel bytes — is the probe re-measuring A? Answer: **no endpoint
   scores agreement with truth gold at all** — the primary and every Holm member are
   style CONTRASTS within truth level on content-matched pairs; the analysis never
   consults canonical-record equality, and the tier-1 instrument gate that DOES use
   truth gold uses WordNet-external gold on words with NO kernel record (LS-1 makes
   coincidence impossible there). The tier-2 truth labels (own/donor) enter only the
   wrong-cell/correct-cell split, and they are construction-fixed, not
   verifier-computed. Residual honestly stated: the tier-2 split's MEANING leans on
   the STIPULATED own-is-correct reading; the split remains well-defined under H-CIRC
   (it is a provenance split), and the primary pools both levels so no verdict rests
   on the stipulation.
2. **False reassurance via null manipulation** (the strongest attack, found during
   design): an equivalence primary on a weak style transform trivially passes. Caught
   and neutralised: the primary moved to tier-2 (0.94 measured pair-difference rate),
   a style_fidelity gate forbids reading equivalence off a null manipulation, and the
   near-null tier-1 transform was demoted to a disclosed diagnostic (FORK-1).
3. **Baseline asymmetry / length cue:** donors are length-adjacent by the sorted
   cyclic-shift construction and gated (±35%); preambles differ by 1 token between
   tier-1 poles and are absent in tier-2; the S6-instruction is byte-identical across
   cells so it cannot cue.
4. **Endpoint gameability:** acceptance := "yes" only, escapes count against
   acceptance symmetrically in both poles of a pair; a judge who escapes everywhere
   fails the truth-manipulation or pool gate (instrument, not evidence). The
   trichotomy's FAIL requires the interval BEYOND the margin — it cannot be reached
   by adding noise (noise widens intervals toward INCONCLUSIVE, which keeps the guard
   in force by the conservative consumer rule).
5. **Family correlation:** two of three judges are one vendor family; a family-shared
   style prior could dilute toward the family mean. Answer: judge-p1 has its own Holm
   TOST member; per-judge effects are reported; the pool gate catches inversion. The
   Haiku judge's designer-family caveat is disclosed (FORK-2) — its labels are data
   graded by a pinned pure function, and the cross-vendor AUDITOR (Codex) is untouched.
6. **Retest gameability:** duplicates share exact text, so a text-hash-deterministic
   judge (temperature 0) trivially passes retest — the gate is a stability FLOOR, not
   evidence of judge quality; disclosed as such.
7. **Taxonomy gaming / degenerate gates (f2b-errors):** the tree is total by
   construction with a fail-closed X-OTHER ≤ 2% gate; assignment is a pure function of
   logged fields so no post-hoc category invention is possible; the conditional
   primary cannot fire on a Stage-2 non-PASS (no way to convert a null into a
   robustness claim); the record consumes only fields declared BEFORE unblinding —
   if the logging handoff fails, the record reads INSTRUMENT-INVALID rather than
   permitting inspect-then-analyse.
8. **Does the probe leak into f2b-transfer?** LLM judges are stateless per item;
   LS-4 makes any human probe judge permanently ineligible as an f2b-transfer judge;
   d-ts questions are byte-disjoint from d-qa/d-qa-r/d-qa-t questions (LS-2 checked at
   build, fail-closed). The probe reads NO f2b outputs, so it cannot condition on them.
9. **Underpowered FAIL direction:** real (§3.5); priced by the conservative consumer
   rule — the probe cannot be used to certify "no leak" via an underpowered
   INCONCLUSIVE, because only PASS lifts the guard.

---

## 7. Handoff (freeze urgency + gates)

1. **FREEZE URGENCY (coordinator):** freeze BOTH records (`prereg-freeze.py`,
   coordinator identity, external timestamp) BEFORE any f2b-transfer Stage-2 GPU cell
   is launched and before any Stage-2 output is inspected. After Stage-2 unblinds,
   f2b-errors is dead as a confirmatory instrument (R-2) and truthstyle-2x2 degrades
   to exploratory commentary on an already-read result. Both dry-run green as of this
   commit.
2. **R-2 logging handoff (Opus runner, ops):** when staging the Stage-2 harness
   (filling the frozen record's PINNED-AT-INPUTS `harness_manifest` placeholder),
   include the per-attempt superset logging fields declared in
   `poc/f2b-errors/taxonomy.json` `required_logged_fields` — an ops-level logging
   addition that changes no arm, endpoint, or analysis of the frozen design. Fallback:
   persist raw per-attempt decoded outputs + verifier decisions content-addressed
   (R-2's default). If neither lands, f2b-errors reads INSTRUMENT-INVALID — never
   retro-fitted.
3. **Assumptions to mint at freeze (registry/assumptions.jsonl):** (i) STIPULATED —
   FORK-4 format transfer (single-stimulus acceptance ↔ f2b MCQ/claim endorsement);
   (ii) STIPULATED — §3.5 planning constants (q, ICC); (iii) EXTRAPOLATION,
   load_bearing:false — LLM-judge style robustness → human judges, resolution path =
   post-Stage-1 human rider; (iv) STIPULATED — tier-2 own-gloss-is-correct reading
   (§6.1 residual).
4. **Run gates:** maintainer sign-off (adjudication spend ≤ $40); judge-p2/p3 exact
   catalog/model-id pins verified at staging (fail-closed); the in-flight f2b judge
   runs' GLOBAL codex install is never upgraded (llmproxy operational constraint).
5. **Not in scope here:** K-NULL (separate line, needs the content-injection map
   first); the human f2b-transfer Stage-1 (human-blocked, standing item); any
   modification to any frozen record, verdict, or engine code (none made).
