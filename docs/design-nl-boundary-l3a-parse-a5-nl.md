# Design + pre-registration spec — the NL-boundary leg: l3a-parse / a5-nl

**Line id:** `nl-boundary-l3a-parse-a5-nl`. **Status: DRAFT — NOT FROZEN.** No
prereg-freeze has run; no final phase may run against this document. Author:
Kern (Fable designer role), 2026-07-10.
**Consolidates/advances:** the pre-declared successors `l3a-parse` (frozen in
`registry/experiments/l3a.json` → `design.n_planned.successors`) and `a5-nl`
(frozen in `registry/experiments/a5.json` → same field), both
registered-as-successor with NO records until this draft
(`docs/next/reuse-ordering-analysis.md` §1.1); feasibility-synthesis §3b and
§5 row 5 (the highest-mortality unmeasured correctness leg).
**Dedup check (2026-07-10):** `registry/experiments/` has no `l3a-parse.json`
/ `a5-nl.json`; `registry/ideas.jsonl` contains no NL-boundary experiment idea
(the mapper front-end appears only as a *shared component* of
`idea-l1a-canonicaliser` and `idea-kernel-precision-linter`); no
`docs/design-*` covers this. NOT a duplicate — this is the first design record
for the pre-declared successor pair.

**Binding constraints:** `docs/kernel-design-directives.md` (§1 native
formalism, §6 honest stats); `docs/next/architecture-ladder.md` §5.1 (HL3a
clause 2 — the NL-parse kill) and §8 item 14 (stage indictment);
`docs/research-plan/08-stats-and-extrapolation.md` §1.6 (decidability lint);
the designer-role MUSTs (absolute/non-inferiority primary — the F2
degenerate-denominator lesson; power on the covered slice; coverage restated).

---

## 0. What this experiment is — and is not

The parents banked, per vertical, an audited instrument-adequacy PASS on
*gold-parsed* closed-grammar queries against a byte-identical engine:

- PREMISE: l3a engine covered exactness 600/600 (one-sided Wilson 95% LB
  0.9955) and strict-code refusal 300/300 (LB 0.9911), audit CONFIRMED
  [MEASURED: registry/verdicts/l3a.json].
- PREMISE: a5 engine covered exactness 855/855 (LB 0.9968) and strict-code
  refusal 122/122 (LB 0.9783), audit CONFIRMED
  [MEASURED: registry/verdicts/a5.json].
- PREMISE: both parent verdicts extrapolate to NO natural-language behaviour
  — verbatim in both envelopes [MEASURED: the two verdict
  `extrapolation_envelope_verbatim` fields].

This record pair tests the NEXT pre-declared stage and nothing else: **can a
deterministic NL front-end (mapper `a1-hybrid` + entity gazetteer + closed
frame layer) replace the gold parse on the SAME frozen eval queries against
the byte-identical engine, at a pre-declared maximum loss, without breaking
the fail-closed contract?** HL3a clause 2 verbatim (frozen in l3a):
*"mapper-parse loses > a pre-declared fraction of gold-parse accuracy (the NL
boundary eats the rung; L3 waits for a better parser, not more GPU)"* — this
record instantiates that clause (and its HA5 analog) with the pre-declared
fraction set in §6.

It is NOT: an LLM experiment (no model anywhere — R0), a cost-ratio or
engine-vs-LLM claim (successors `l3a-cost` / `a5-llm`), a natural-user-
distribution NL-robustness claim (phrasings are agent-authored under a blind
protocol — §5, ASM-NLB-1), or a real-world coverage claim.

## 1. Hypotheses

- **H-NLB-L3 (family/world vertical, record `l3a-parse`):** the deterministic
  front-end retains ≥ 0.90 of gold-parse covered exactness on the frozen l3a
  eval (equivalently, absolute covered-exact rate > 0.90 — the gold ceiling
  is MEASURED at 1.0, so retained fraction ≡ absolute rate; see §6), while
  keeping the fail-closed contract (controls refused; mis-parses become
  refusals, not wrong answers).
- **H-NLB-A5 (code vertical, record `a5-nl`):** the same, on the frozen a5
  eval, with the same engine + `kot_code` desugaring layer.

Falsifiable both ways: FAIL fires the parent kill clause verbatim
("L3 waits for a better parser, not more GPU"); PASS licenses only the §8
envelope.

## 2. Registered forks (design-space uncertainties, never silently decided)

| Fork | Options | Decision + why | Re-opens when |
|---|---|---|---|
| **FK-NLB-1** record topology | (a) one record, vertical as IV; (b) two records, one shared harness | **(b).** The frozen parents each pre-declare a SEPARATE successor id gated on their own verdict; the two kills (HL3a clause 2 / HA5 NL analog) must be able to fire independently; pooling verticals would smuggle a cross-vertical average into a per-vertical kill. Shared harness + shared analysis helper, pinned byte-identically in both records. | never (frozen parents bind) |
| **FK-NLB-2** primary floor | 0.80 / 0.90 / 0.95 | **0.90** (§6 justification). Genuinely uncertain where "reachable" flips; 0.90 is decidable at both frozen n and instantiates the clause-2 "pre-declared fraction" at 10% max loss. | a measured point in (0.80, 0.90) → INCONCLUSIVE re-opens the fork WITH data |
| **FK-NLB-3** front-end class | deterministic-only (mapper a1-hybrid + gazetteer + closed frames) vs LLM-assisted parse | **deterministic-only.** Clause 2 is ABOUT the deterministic boundary; an LLM parser re-imports stochasticity ahead of the determinism pitch and is the pre-declared SUCCESSOR if the kill fires. | kill fires |
| **FK-NLB-4** phrasings per query | K=1 / K=3 | **K=1** held-out phrasing per eval query: keeps n identical to the parents' powered slices, keeps items independent (K=3 clusters), keeps cost ~$10. Paraphrase-diversity is enforced by quota (§5) instead of by K. | a PASS→ paraphrase-robustness successor may use K>1 |
| **FK-NLB-5** malformed stratum | render as gibberish NL vs exclude | **exclude.** Malformedness is a property of the structured query; it has no faithful NL rendering, and the parents already banked shape-validation. Control n becomes 270 (l3a) / 106 (a5). Registered scope cut. | never for this pair |
| **FK-NLB-6** control refusal scoring | strict engine code (parents') vs pipeline-acceptable set | **pipeline-acceptable**: refused with {the pre-authored expected engine code} ∪ {ERR_PARSE}. Under an NL front-end the refusal may legitimately fire EARLIER (e.g. unknown-entity → gazetteer miss → ERR_PARSE, never reaching the engine's ERR_UNKNOWN_ENTITY). Strict engine-code match is reported descriptively. The dangerous direction (control ANSWERED) is what the gate must exclude. | never |
| **FK-NLB-7** refusal-gate level per record | 0.95 both / 0.95 + 0.90 | **l3a-parse 0.95; a5-nl 0.90.** At a5's frozen control n=106 (after FK-NLB-5) a 0.95 gate is UNDECIDABLE under the Holm-worst-case bound (even 105/106 observed fails; only a perfect 106/106 passes — a gate that only a perfect score can pass fails the P8 §1.6 lint). 0.90 at n=106 passes from 102/106 (§7). Registered asymmetry, driven by n, not by preference. | a5 control set ever grows |

## 3. The pipeline under test (one shared harness)

```
NL phrasing (held-out, blind-authored)
  → [1] entity gazetteer     (deterministic longest-match over surface text;
                              built from the pinned world stores' entity URN
                              slugs + declared surface variants; ambiguity or
                              miss → ERR_PARSE/gazetteer-miss)
  → [2] mapper a1-hybrid     (@jeswr/kernel-mapper, policyPreset('a1-hybrid'),
                              policy sha e13dc838… pinned; lexicon compiled
                              from the PINNED manifests: kernel-v0 +
                              molecules-v0 for l3a-parse; + code-v0 for a5-nl;
                              abstention in a required slot → ERR_PARSE/mapper-abstain)
  → [3] closed frame layer   (deterministic rule set: wh/op keywords → op +
                              direction; exactly one mapped concept URN fills
                              the rel/concept slot; 0 or ≥2 → ERR_PARSE/frame-miss)
  → kot-query/1 (l3a-parse) or kot-query-code/1 (a5-nl)
  → byte-identical engine    (tools/axiom/kot_axiom.py sha d2064989…;
                              + tools/axiom/kot_code.py sha 9fbe2a50… for a5-nl
                              — the SAME pins as the frozen parents; the engine
                              is NOT modified by this experiment)
```

Fail-closed contract of the front-end: every non-parse is a **refusal** with
code `ERR_PARSE` and a stage tag (`gazetteer-miss` | `mapper-abstain` |
`frame-miss` | `frame-ambiguous`); the front-end NEVER guesses a slot. Stage
distribution is reported descriptively (architecture-ladder §8 item 14 stage
indictment: a FAIL must say WHICH stage ate the rung).

Honesty note (registered): on the code vertical the mapper's lexicon leg is
thin — the seven relational ops are carried by frame keywords + identifier
gazetteer, and the mapper's concept mapping decides only the `instance-of`
concept slot. a5-nl therefore stresses frame+entity-linking more than
lexicon mapping; l3a-parse stresses lexicon mapping (relation/concept words).
Together they cover the boundary; separately each licenses only its vertical.

The frame layer's rule set is **DRAFT until freeze**: it may be revised
against the blind DEV phrasing set only (§5), then its sha256 is pinned in
the record BEFORE the held-out eval phrasings are authored (ordering is part
of the blindness protocol, §5/§10).

## 4. Eval material (frozen, reused byte-identically)

- `data/l3a-eval/queries.jsonl` — 600 covered + 300 control, corpus digest
  53eb788b… (pinned in the frozen l3a record). NL leg uses 600 covered + 270
  control (malformed excluded, FK-NLB-5).
- `data/a5-eval/queries.jsonl` — 855 covered + 122 control, corpus digest
  3676d689… (pinned in the frozen a5 record). NL leg: 855 + 106.
- World/axiom corpora and engine: identical pins to the parents (world-v0,
  axioms-v0, code-world-v0, code-axioms-v0, kernel-v0, molecules-v0,
  code-v0). NOTHING in `data/` owned by the parents is modified.
- NEW input corpora (built pre-freeze, hash-pinned at freeze):
  `data/nlb-phrasings-l3a/` and `data/nlb-phrasings-a5/` — one held-out
  phrasing per included eval query (`{qid, text}`), plus a DEV file of 60
  phrasings per vertical over a stratified query sample, plus the authoring
  transcripts + manifest (§5).

Coverage restatement (mandatory): as in the parents, coverage of the covered
slice is **by construction** (queries authored against the stores); no m0b
concept-coverage gate applies, and m0b's 0.3542 token-mass number (one corpus,
one rung, one incomplete kernel instance) is not a premise here. What this
experiment adds is the NL reachability of that constructed slice — NOT any
natural-corpus coverage claim.

## 5. Blind phrasing protocol (the load-bearing input discipline)

Authoring identities and blindness:

1. **Phrasing authors** are FRESH agent identities (not the designer, not the
   front-end author, not the runner) invoked with a PINNED prompt whose
   context contains ONLY, per query: the family name, a one-line op semantics
   gloss (fixed table in the prompt), the relation/concept LABEL (e.g.
   "mother", "python function"), the entity LABEL(s) (URN slug rendered
   human-readable, e.g. "Elvis Presley", "check_doc in claims-check.py"),
   and — for controls — the instruction to phrase the QUESTION faithfully
   (never the expected refusal). Authors get NO repo access, NO mapper
   lexicon, NO front-end code, NO expected answers, NO other line's output.
   The prompt file is committed and hash-pinned; transcripts are committed.
2. **Blind-to-lexicon** (the memo's required attack, §10.1): authors cannot
   tune phrasings to mappable surface forms because they never see which
   forms map. Since relation LABELS are themselves lexicon surface forms
   (unavoidable — the label is the concept's name), the prompt additionally
   imposes a **paraphrase quota**: within each covered family, at most 50% of
   phrasings may contain the relation label verbatim; the rest must
   paraphrase ("who gave birth to X", "X's male parent", "which routines
   invoke f"). Exactness is reported stratified by label-verbatim vs
   paraphrase (descriptive) so the quota's effect is visible, not assumed.
3. **DEV/EVAL split + ordering**: DEV = 60 phrasings per vertical over a
   stratified sample of queries, authored FIRST, by a batch of author
   identities disjoint from the EVAL batch. The front-end author may iterate
   the frame layer against DEV only. Then the front-end sha is pinned (commit
   + record), THEN the EVAL phrasings (one per included query, fresh
   identities) are authored, hashed, and the record freezes. Any front-end
   edit after EVAL phrasings exist = a new record id.
4. **Mechanical lints on the phrasing corpus** (part of the instrument gate):
   exactly one phrasing per included qid; no `urn:` substring; no grammar
   keyword leakage (`op`, `direction`, `unique(`, JSON braces); no expected
   answer value string on covered items (e.g. the phrasing for q0001 must not
   contain "gladys"); UTF-8, single line, ≤ 200 chars.
5. **Recoverability audit** (pre-freeze, instrument-side): a 60-item random
   sample per vertical is given to an independent judge identity (no lexicon
   access) who must recover (op, relation/concept label, entity label) from
   the phrasing alone; < 95% recovery blocks freeze (the phrasings, not the
   parser, would be indicted — a FAIL must not be manufacturable by
   unanswerable phrasings). Recorded in the phrasing manifest.
6. Mock phrasings (`--mock`) are template-generated scaffold English,
   quarantined under `poc/nlb-mock/`, never under `data/`, and never shown to
   any authoring identity. They exercise mechanics only (§9).

Cost of the protocol: ~1,831 eval + ~120 dev phrasings + audits ≈ **$8–12 of
agent API spend, the only spend in this experiment**.

## 6. Endpoints (EXACTLY ONE primary per record) and verdict rules

All bounds: one-sided Wilson (kot_common formula), z = 1.645 for primary and
kill rules; the two gated secondaries form ONE Holm family per record
(step-down over their one-sided p-values at family α = 0.05; the analysis
script exports booleans, §6.3).

### 6.1 Primary (per record) — retained covered exactness, non-inferiority form

`/analysis/retained_covered_exact_wilson_lb` — one-sided Wilson 95% LB of the
**mapper-parse arm's covered-exact rate** over the SAME covered queries the
parent froze (l3a-parse n=600; a5-nl n=855), scored EXACTLY as the parent
(status=answer ∧ value=expected ∧ provenance⊆world-ids ∧ license≠∅), tested
against **floor 0.90**.

- **Retained-fraction ≡ absolute rate, by measurement:** the gold ceiling is
  MEASURED at 600/600 and 855/855 [registry/verdicts/l3a.json, a5.json], so
  the retained fraction's denominator is the full n — the F2
  degenerate-denominator lesson is discharged by construction, and the
  primary is stated in absolute non-inferiority form (margin δ = 0.10 vs the
  measured ceiling 1.0). No TOST upper leg exists (the pipeline cannot exceed
  its own gold ceiling); the one-sided NI bound IS the equivalence machinery.
- **Floor justification (from the parents' measured baselines):** the parents
  gate the instrument at 0.98 (covered) / 0.95 (refusal); their measured
  ceilings are 1.0. Floor 0.90 = measured ceiling − 0.10, instantiating HL3a
  clause 2's "pre-declared fraction" at **10% maximum NL-boundary loss** —
  the level at which the pipeline still answers ≥9/10 covered NL queries
  exactly while every miss is (separately gated) a refusal, not a wrong
  answer. Below it, the exactness premium the engine leg banked stops being
  the pipeline's property, and the pre-declared programme response is parser
  investment, not GPU (kill text verbatim). The 10% number itself is a
  programme POLICY choice, registered as ASM-NLB-2 (STIPULATED), with
  FK-NLB-2 re-opening on an INCONCLUSIVE landing.
- Planning value 0.95 → LB 0.9332 (n=600) / 0.9351 (n=855): clears the floor;
  passes the P8 §1.6 decidability lint (§7).

### 6.2 Gated secondaries (one Holm family per record; m = 2)

- **S1 — control refusal retention:** rate of included control queries
  (l3a 270 / a5 106) refused with an ACCEPTABLE code — the pre-authored
  expected engine code or `ERR_PARSE` (FK-NLB-6) — gate **> 0.95 (l3a-parse)
  / > 0.90 (a5-nl)** (FK-NLB-7). Strict engine-code match and refused-any are
  reported descriptively.
- **S2 — the dangerous half of the fail-closed split:** covered
  **mis-parse→wrong-answer rate** (status=answer ∧ value≠expected, any arm
  stage) — one-sided Wilson UB gate **< 0.02**. A wrong answer under NL parse
  carries provenance and license strings and is therefore WORSE than a
  refusal (false authority); it gets its own gate rather than riding the
  primary. The safe half (mis-parse→refusal) is the primary's complement and
  is reported by stage (descriptive).

### 6.3 Instrument gates (each with its own bound; any failure ⇒ INSTRUMENT-INVALID)

- **G1** arm presence + per-stratum counts match the manifest (600/270,
  855/106 + dev 60).
- **G2 gold-replication:** the gold-parse arm re-runs the parent's FULL eval
  (incl. malformed) on the byte-identical engine and must reproduce the
  parent-perfect outcome (l3a 600/600 covered + 300/300 strict-code control;
  a5 855/855 + 122/122) — the ceiling is re-verified in-run, not assumed.
- **G3 phrasing-corpus lints + blindness artifacts** (§5.4): manifest hash
  match, one-per-qid, no-URN/grammar/answer leakage, transcripts + pinned
  prompt + recoverability-audit record present.
- **G4 dev-set front-end abstention ≤ 0.20** (≤12/60) — the mapper-abstention
  instrument bound. On the DEV set the front-end was allowed to iterate, so
  exceeding 0.20 there means the shipped artifact is broken/pin-drifted, not
  that NL is hard. On the EVAL set abstention is SUBSTANCE (it lowers the
  primary and is reported by stage) — deliberately NOT an instrument gate, so
  the experiment cannot dodge the kill by declaring itself invalid.
- **G5 deranged-lexicon leakage guard:** the deranged arm (§6.4) must retain
  covered exactness **< 0.10**; otherwise the eval is answerable without
  correct concept mapping (frame/entity shape alone) and the instrument—not
  the mapper—is generating the signal ⇒ INSTRUMENT-INVALID.
- **G6 determinism:** full mapper-parse pass run twice, byte-identical.

### 6.4 Arms (per record)

| Arm | Role |
|---|---|
| `mapper-parse` | the pipeline under test (§3) |
| `gold-replication` | measured ceiling + G2 regression check (parent's gold queries) |
| `deranged-lexicon` | scramble control: seed-pinned fixed-point-free permutation of the front-end's semantic bindings — concept-URN targets (l3a-parse); op→op derangement + concept targets (a5-nl, because its op keywords carry the relational semantics). Analog of the mandatory shuffled-kernel control at R0: correct concept BINDING, not pipeline shape, must carry the result. |
| `abstain-all` | trivial policy: refuses every phrasing (perfect refusal, zero exactness) |
| `answer-all` | trivial policy: never refuses (parent fabrication policy on parsed queries; deterministic global default on parse failures) — high-answer/zero-refusal bracket |

The kernel-as-text null is NOT instantiable here (no model consumes anything
— R0, no host; same registered adaptation as the frozen parents, which the
parents' records carry in `arms_mandatory_baselines`). The two trivial
policies + deranged arm are the registered null/scramble set.

### 6.5 Verdict rules (per record, mechanical)

1. **INSTRUMENT-INVALID** iff NOT `/gates/instrument_valid` (G1–G6).
2. **FAIL** iff `/analysis/retained_covered_exact_wilson_ub` ≤ floor(0.90)
   **OR** `/analysis/covered_wrong_answer_wilson_lb` ≥ 0.02 (fail-closed
   demonstrably broken — the second, independent way the NL boundary kills
   the rung). Kill text inherited verbatim from the parent (§1).
3. **PASS** iff `/analysis/retained_covered_exact_wilson_lb` > 0.90 AND
   `/analysis/holm_s1_pass` AND `/analysis/holm_s2_pass` AND
   `/analysis/gold_replication_identical`.
4. else **INCONCLUSIVE** (re-opens FK-NLB-2 with data).

## 7. Power / decidability (P8 §1.6 lint, computed on the frozen n)

One-sided Wilson, z=1.645 (primary/kill), z=1.96 shown for the Holm
worst-case on secondaries:

| Quantity | l3a-parse | a5-nl |
|---|---|---|
| primary n | 600 | 855 |
| PASS needs (LB > 0.90) | ≥ 553/600 (0.9217) | ≥ 784/855 (0.9170) |
| FAIL fires (UB ≤ 0.90) | ≤ 527/600 (0.8783) | ≤ 755/855 (0.8830) |
| INCONCLUSIVE band | 528–552 (~4.2 pp) | 756–783 (~3.3 pp) |
| planning value 0.95 → LB | 0.9332 ✓ | 0.9351 ✓ |
| S1 n (FK-NLB-5) | 270, gate 0.95 | 106, gate 0.90 |
| S1 passes from (z=1.96) | ≥ 264/270 | ≥ 102/106 |
| S1 planning 0.99 → LB (z=1.96) | 0.9695 ✓ | 0.9640 ✓ |
| S2 gate UB < 0.02 passes up to (z=1.96) | ≤ 5/600 wrong | ≤ 9/855 wrong |
| S2 kill fires (LB ≥ 0.02, z=1.645) | ≥ 18/600 wrong | ≥ 25/855 wrong |
| S2 planning value | 3/600 → UB 0.0141 ✓ | 4/855 → UB 0.0132 ✓ |

Every gate is passable at its planning value and failable well inside the
support — no vacuous gates. (FK-NLB-7 records why a5's S1 sits at 0.90.)

## 8. Extrapolation envelope (verbatim into both records)

Measured range: R0 — no host model; ONE deterministic front-end build
(mapper a1-hybrid pin + one gazetteer + one frozen frame rule set), ONE
blind-authored phrasing set per vertical (K=1 per query, agent-authored under
the §5 protocol), the parents' frozen evals/stores/engine byte-identical.
A PASS licenses: "the closed grammar is reachable from THESE held-out NL
phrasings by a deterministic training-free front-end with ≤10% exactness
loss and an intact fail-closed contract, per vertical" — the gate the
successors l3a-cost / a5-llm need to include an NL leg honestly. A PASS does
NOT license: any natural-user-distribution robustness claim, any other
phrasing distribution/corpus/domain/language, any paraphrase-set-size
scaling, any LLM-comparative accuracy or cost claim, any statement about
kernel usefulness to any model, or a cross-vertical "NL is solved" claim
(each record licenses ONLY its vertical; the programme-level reachability
narrative requires both AND survives only within agent-authored-phrasing
scope). A FAIL indicts the named pipeline stage (stage tags, §3) and licenses
exactly the parent kill's routing: parser investment, not GPU.

## 9. Harness, mock, and runner constraints

Shared harness (this line's files; nothing owned by another line touched):

- `tools/experiments/nlb/nlb_map.mjs` — mapper bridge (builds the pinned
  lexicon, applies a1-hybrid policy — pin verified at import; `--derange N`
  applies the seed-pinned derangement).
- `tools/experiments/nlb/nlb_frontend.py` — gazetteer + frame layer (DRAFT
  rules; finalised on DEV only; sha pinned at freeze).
- `tools/experiments/nlb/nlb_instrument.py` — arms, scoring, kot-log/1 body
  (RAW OUTPUT ONLY; knows no thresholds).
- `tools/experiments/nlb/gen_mock_phrasings.py` — scaffold-English mock
  phrasings (quarantined, `--mock` only).
- `analysis/l3a_parse.py`, `analysis/a5_nl.py` (+ shared helper) — pinned at
  freeze; output fields listed in the records.

`--mock` (green required before freeze; $0): template phrasings → full
5-arm pipeline → mechanics asserted (G2 parent-perfect replication, G5
deranged collapse, G6 determinism, count integrity). The mock demonstrates
MECHANICS ONLY — mock phrasings are non-blind scaffold English and cannot
preview the primary.

Runner: `r0-local-cpu`, shared 2-core box, `nice -n 10`, foreground gates,
concurrency cap 5. Full 5-arm pass ≈ minutes (engine ~6–8 µs/query measured
in parents; mapper ~ms/phrasing). Budget: usd_cap 12 (phrasing authoring),
wall-clock cap 2 h. **No GPU, no model, Tier-0.** Opus-runnable immediately
after freeze (run ≠ design; the runner never edits the front-end).

## 10. Pre-freeze skeptic attack memo (freeze is BLOCKED without this)

**10.1 Phrasing-authoring leakage (the required attack).** Threat: phrasings
tuned (consciously or not) to what the mapper can parse → primary inflated;
or tuned to defeat it → kill manufactured. Defences, in order of strength:
(i) author identities never see lexicon/front-end/mapper code (§5.1) and the
pinned prompt is itself audited for smuggled surface-form lists (G3);
(ii) the paraphrase quota FORCES ≥50% of covered phrasings off the one
surface form the authors do legitimately see (the label), and the
label-verbatim vs paraphrase stratification makes any residual inflation
VISIBLE in the report rather than deniable; (iii) the recoverability audit
(§5.5) blocks the symmetric attack (unanswerable phrasings manufacturing a
FAIL); (iv) transcripts are committed, so the auditor can re-derive
blindness. RESIDUAL RISK, registered: agent authors share training
distribution with the mapper's label vocabulary — a human-authored phrasing
set would be stricter; scoped out by ASM-NLB-1 and carved out of the envelope
(§8). The designer (this identity) has READ the lexicon docs and therefore
MUST NOT author any dev/eval phrasing — enforced by identity separation in
the build plan (§11).

**10.2 Reverse leakage (front-end tuned to eval phrasings).** Threat: frame
rules fitted to the exact held-out sentences. Defence: pin ORDER (§5.3) —
front-end sha committed before eval phrasings exist; any later edit mints a
new id. The DEV set the rules MAY fit is 60 items authored by a disjoint
identity batch, and DEV items are never scored in the final analysis.

**10.3 Oracle-leakage class (N0 §5 checklist).** The parents' known
construction circularity (evals authored against the same stores that define
gold answers) is INHERITED and already registered there (ASM-0006/0008); this
record adds no new answer-side oracle: the mapper never sees answers, and its
accept test (a parse exists) is independent of the gold label. The NEW
oracle risk is frame/entity SHAPE answering the eval without semantics — G5
(deranged bindings must collapse to <0.10) is the executable refutation, and
its failure invalidates the instrument rather than passing the record.

**10.4 Endpoint gameability.** Abstention cannot game the primary (every
abstention is a covered miss). Answer-happiness cannot game it either (wrong
answers are gated by S2 at 2% with their own kill leg). Entity-only
answering is excluded by G5. Choosing easy strata is impossible: the query
set is the parents' frozen eval, count-locked by G1.

**10.5 Gate decidability / brittleness.** All gates shown passable-and-
failable at frozen n (§7). The one brittle candidate found (a5 S1 at 0.95,
undecidable at n=106 under Holm worst case) was repaired by FK-NLB-7 BEFORE
freeze rather than discovered after. Malformed exclusion (FK-NLB-5) removes
the one stratum whose NL rendering would be undecidable-by-construction.

**10.6 Mock contamination.** Mock scaffold phrasings live under
`poc/nlb-mock/`, never under `data/`; G3's manifest pins the authored corpus
only; authoring identities never receive mock text (§5.6). A grep-lint in G3
additionally rejects any eval phrasing byte-identical to a mock template
instantiation.

**10.7 Envelope overreach (the m0b lesson).** The tempting headline "NL
reaches the kernel's checker" is NOT licensed by K=1 agent-authored
phrasings on two self-authored verticals; §8's carve-outs are verbatim in
both records, and the per-vertical licensing split blocks a silent
conjunction claim.

Skeptic conclusion: with G2–G6 + the §5 ordering protocol in place, the
remaining unmitigated risks are ASM-NLB-1 (agent-authored proxy) and the
inherited parent stipulations — all registered, none load-bearing for the
verdict function itself. CLEAR TO PROCEED TO FREEZE once §11 items 1–6 are
green. (This memo attacks the DESIGN; the pre-freeze skeptic pass must be
re-run by a non-designer identity against the BUILT inputs.)

## 11. Build plan to freeze (this record STOPS before item 7)

1. Harness skeleton + mock green (`--mock`, both verticals) — **DONE in this
   draft** (`poc/nlb-mock/` receipts).
2. DEV phrasing authoring (60/vertical, fresh identities, pinned prompt).
3. Frame-layer finalisation against DEV only; commit; record front-end sha.
4. EVAL phrasing authoring (1,831 total, fresh identities); lints; manifest;
   recoverability audit; corpus-pin `data/nlb-phrasings-*`.
5. Analysis scripts finalised; output-field list matches records; second
   mock pass green end-to-end including analysis.
6. Independent skeptic re-attack on the BUILT inputs (non-designer identity).
7. `prereg-freeze.py` on `l3a-parse` then `a5-nl` (or batch), external
   timestamp, frozen_sha into the index. **NOT EXECUTED — draft stops here.**
8. Handoff to Opus runner (foreground gates; run ≠ design ≠ grade ≠ audit;
   Codex cross-vendor audit on any computed PASS).

## 12. Assumptions to register at freeze (`registry/assumptions.jsonl`)

- **ASM-NLB-1 (STIPULATED):** agent-authored phrasings under the §5 blind
  protocol are an adequate held-out proxy for NL phrasings of these queries;
  natural-user-distribution claims are excluded from the envelope regardless.
- **ASM-NLB-2 (STIPULATED):** the 0.10 maximum NL-boundary loss (floor 0.90)
  is the programme's reachability policy instantiating HL3a clause 2's
  "pre-declared fraction"; an INCONCLUSIVE landing re-opens FK-NLB-2.
- **ASM-NLB-3 (MEASURED-backed premise, restated):** entity labels given to
  authors are the entities' only names; the mapper lexicon contains no entity
  names (lexicon = concept labels + prime exponents — mapper/README.md,
  mapper/src/lexicon.ts), so providing them is not lexicon leakage.
- **ASM-NLB-4 (STIPULATED):** ERR_PARSE counts as a refusal (fail-closed) for
  S1; conservative-direction note: this eases S1 but the dangerous direction
  is separately gated by S2 and the S2 kill leg.
- Inherited, still open, relied on: ASM-0004/0005/0006 (l3a),
  ASM-0007/0008/0009 (a5) — restated at verdict time per the honesty guard.

## 13. Registered scope statement

Everything measured here is a property of THIS front-end build, THESE two
blind-authored phrasing sets, and the parents' frozen evals/stores/engine.
DECISION: two records, two per-vertical verdicts, one shared harness
(FK-NLB-1) [premises: the frozen parents' successor pre-declarations —
MEASURED: registry/experiments/l3a.json + a5.json `n_planned.successors`].
It extrapolates to no other phrasing distribution, corpus, domain, or
language; no LLM-comparative claim; no kernel-usefulness-to-model claim.
