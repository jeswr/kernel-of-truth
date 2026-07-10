# Design + pre-registration spec — the NL-boundary leg: l3a-parse / a5-nl

**Line id:** `nl-boundary-l3a-parse-a5-nl`. **Status: DRAFT →
FREEZE-CANDIDATE (2026-07-10) — NOT FROZEN.** No prereg-freeze has run; no
final phase may run against this document. Freeze-candidate pass completed
§11 items 1–5 (DEV corpora committed, frame layer finalised on DEV only and
sha-pinned in both records, analysis scripts pinned, mocks + analysis
end-to-end green); still owed before freeze: the blind EVAL/PROBE input build
(Opus, `tools/experiments/nlb/EVAL-BUILD-SPEC.md`), the independent
non-designer skeptic re-attack (item 6), then prereg-freeze (item 7). Author:
Kern (Fable designer role), 2026-07-10.
**2026-07-10 post-build amendment:** the blind EVAL build landed (b4a21fc)
and hit two freeze-blocking findings; adjudicated in §14 +
`registry/assessments/l3a-parse-recoverability.json` (l3a re-scoped to the
shape-recoverable covered set n=527, FK-NLB-10; a5 forced-substring lint
exemption, FK-NLB-11; ASM-0420..0425).
**2026-07-10 skeptic round 2:** the §11 item-6 independent re-attack
returned 8 freeze-blocking + 3 should-fix defects
(`poc/nlb-skeptic/skeptic-output.txt`); remediated in §14.8 (fail-closed
scorer hardening + supersede semantics + harness-pin gate, ASM-0621;
post-outcome-registration framing honestly downgraded, ASM-0620; l3a
envelope restricted to the 7-family slice; byte-identical-engine claim
replaced by the G2 behavioural claim). The independent re-attack gate
re-runs on this revision before any freeze.
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
*gold-parsed* closed-grammar queries against the engine:

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
the same engine (G2-verified parent-identical behaviour — §10.9), at a
pre-declared maximum loss, without breaking the fail-closed contract?** HL3a clause 2 verbatim (frozen in l3a):
*"mapper-parse loses > a pre-declared fraction of gold-parse accuracy (the NL
boundary eats the rung; L3 waits for a better parser, not more GPU)"* — this
record instantiates that clause (and its HA5 analog) with the pre-declared
fraction set in §6.

It is NOT: an LLM experiment (no model anywhere — R0), a cost-ratio or
engine-vs-LLM claim (successors `l3a-cost` / `a5-llm`), a natural-user-
distribution NL-robustness claim (phrasings are agent-authored under a blind
protocol — §5, ASM-0140), or a real-world coverage claim.

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
| **FK-NLB-8** paraphrase discipline (FREEZE-CANDIDATE fork, amends the draft §5 quota) | forced ≥50% no-label quota / syntactic-diversity quotas + descriptive no-label probe | **quotas + probe.** The mapper lexicon is single-label-per-concept with a rule lemmatizer and no synonym table [MEASURED: mapper/src/lexicon.ts + mapper/src/lemmatize.ts; probe runs 2026-07-10 — "who gave birth to X" maps give+birth not mother, "makers of"/"parts of" map nothing], so no-label phrasings are unmappable BY CONSTRUCTION and a forced 50% no-label stratum would predetermine FAIL arithmetically and break the §7 planning-value decidability the design binds itself to. Replaced by: free natural use of the relation's name + mechanically linted syntactic-diversity quotas (≥ min(6, n) distinct masked templates per covered family; no template > 50%; canonical scaffold ≤ 50%) + a 60-item/vertical no-label synonym PROBE, descriptive only, never gated, carved out of the envelope. Label-verbatim vs paraphrase stratification stays a reported endpoint. [STIPULATED: ASM-0144] | a parser-investment successor adds a synonym/alias layer (new record id) |
| **FK-NLB-9** DEV-set basis (FREEZE-CANDIDATE fork, amends the draft §5.3) | DEV sampled from scored eval queries, disjoint author identities / DEV over FRESH identities disjoint from every scored item | **fresh-disjoint.** DEV = 60 designer-authored phrasings per vertical over freshly minted entities (`data/nlb-phrasings-*/dev-entities.jsonl`) absent from both world stores and every eval item (linted, DEV-FRESH); DEV items are never scored; the dev-pass gazetteer augmentation never enters a scored arm. Item-level disjointness replaces author-identity separation for DEV: with the front-end pinned before any EVAL phrasing exists, designer-DEV has no channel into the blind EVAL distribution and its only failure mode LOWERS the primary (conservative). EVAL/PROBE authoring keeps the full fresh-identity blind protocol. [STIPULATED: ASM-0145] | never for this pair; the skeptic re-attack (§11 item 6) attacks it against the built corpus |

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
  → engine                   (tools/axiom/kot_axiom.py sha d2640881…;
                              + tools/axiom/kot_code.py sha 9fbe2a50… for a5-nl.
                              kot_code is byte-identical to the frozen parent
                              pin; kot_axiom is NOT — the define-op line
                              extended it post-parent-freeze, so behavioural
                              identity on the parent evals is re-verified
                              IN-RUN by gate G2 instead of asserted
                              [STIPULATED: ASM-0147]. The engine is NOT
                              modified by this experiment.)
```

**Frame-layer closed knowledge (finalised on DEV, pinned):** the frame layer
carries (i) a per-relation surface-orientation table `ROLE_DIR` — which
engine direction realises the role reading "the R of E" for the five
relations with world edges (mother/father forward; maker-of, part-of
inverse; has-part forward); every other relation defaults to a direction the
engine refuses fail-closed; (ii) a label-variant matcher over the mapped
concept's OWN label (inflections + the closed two-irregular table
made→make, children→child); (iii) the closed a5 op-keyword cascade; and
(iv) a fail-closed op default: inverse-possessive shapes parse as `lookup`
(the set-valued, non-guessing op) unless the phrasing carries an explicit
exactly-one marker — a `unique` guess on a set-valued family would fabricate
a scalar answer (an S2 wrong answer), which is exactly what the front-end
must never do. The frame layer performs **NO concept aliasing** ("made" maps
to the distinct `make` concept and dies at the engine as a safe refusal, not
a rescue): the mapper stays the sole concept-binding component, so stage
indictment and the G5 derangement stay clean. All of this is grammar-like
closed knowledge, none of it answer knowledge. [STIPULATED: ASM-0146]

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
  phrasings per vertical over FRESH identities disjoint from every scored
  item (FK-NLB-9), plus a 60-item no-label synonym PROBE (FK-NLB-8,
  descriptive only), plus the pinned prompts, author packets, authoring
  transcripts, lint receipts, recoverability-audit record and manifest (§5).
  DEV portion + prompts committed at freeze-candidate; EVAL/PROBE portion
  built by the Opus runner per `tools/experiments/nlb/EVAL-BUILD-SPEC.md`.

Coverage restatement (mandatory): as in the parents, coverage of the covered
slice is **by construction** (queries authored against the stores); no m0b
concept-coverage gate applies, and m0b's 0.3542 token-mass number (one corpus,
one rung, one incomplete kernel instance) is not a premise here. What this
experiment adds is the NL reachability of that constructed slice — NOT any
natural-corpus coverage claim.

## 5. Blind phrasing protocol (the load-bearing input discipline)

Authoring identities and blindness:

1. **Phrasing authors** are FRESH agent identities (not the designer, not the
   front-end author, not the runner) invoked with a PINNED prompt
   (`data/nlb-phrasings-*/prompt-eval.md`) whose context contains ONLY, per
   query, the AUTHOR PACKET line (`tools/experiments/nlb/gen_author_packets.py`,
   deterministic): a semantic SHAPE id (op + which side of the relation the
   entity sits on — rendered via the same closed orientation semantics the
   eval was authored under), the relation/concept LABEL (e.g. "mother",
   "maker of", "python function"), and the entity LABEL — the URN slug
   verbatim (the entity's canonical and ONLY name; hyphens may be written as
   spaces; a5 identifiers are used verbatim, e.g.
   `code-fn-claims-check--check-doc`, because the identifier IS the name).
   FREEZE-CANDIDATE strengthening over the draft: packets carry NO family
   name and NO covered/control class — controls are phrased faithfully as
   questions without the author knowing they are controls. Authors get NO
   repo access, NO mapper lexicon, NO front-end code, NO expected answers,
   NO other line's output. One fresh identity per 100-packet batch;
   transcripts committed.
2. **Blind-to-lexicon** (the memo's required attack, §10.1): authors cannot
   tune phrasings to mappable surface forms because they never see which
   forms map. Since relation LABELS are themselves lexicon surface forms
   (unavoidable — the label is the concept's name), authors use the
   relation's name NATURALLY and freely; what the lint forces instead is
   SYNTACTIC diversity (FK-NLB-8): per covered family ≥ min(6, n) distinct
   masked templates, no single template > 50%, canonical
   "wh… the <label> of <entity>" scaffold ≤ 50%. The systematic no-label
   question is measured by the separate synonym PROBE (item 7 below),
   descriptive only. Exactness is reported stratified by label-verbatim vs
   paraphrase so residual label-use inflation is visible, not deniable.
   The draft's forced ≥50% no-label quota is registered-replaced: it would
   have predetermined FAIL against a lexicon that is single-label by
   construction [STIPULATED: ASM-0144].
3. **DEV/EVAL split + ordering** (FK-NLB-9): DEV = 60 phrasings per vertical
   over FRESH minted identities disjoint from every scored item and both
   world stores (`dev-entities.jsonl`; linted DEV-FRESH), authored FIRST —
   at freeze-candidate, by the designer under the ASM-0145 allowance
   (disclosed in the corpus manifests; admissible because DEV items are
   never scored and the only designer-DEV failure mode lowers the primary).
   The front-end author may iterate the frame layer against DEV only; the
   dev-pass gazetteer (world ∪ dev entities) never enters a scored arm. Then
   the front-end sha is pinned (commit + record — DONE 2026-07-10, sha
   5903777…), THEN the EVAL phrasings (one per included query, fresh
   identities) are authored, hashed, and the record freezes. Any front-end
   edit after EVAL phrasings exist = a new record id.
4. **Mechanical lints on the phrasing corpus**
   (`tools/experiments/nlb/nlb_lint.py`, receipt embedded in run bodies and
   gated as G3): exactly one phrasing per included qid; no `urn:` substring;
   no grammar keyword leakage (`op`, `direction`, `unique(`, JSON braces,
   the scaffold token `inverse`); no expected answer value string on covered
   items (e.g. the phrasing for q0001 must not contain "gladys"); UTF-8,
   single line, ≤ 200 chars; the FK-NLB-8 diversity/scaffold quotas;
   DEV-FRESH disjointness; no phrasing byte-identical to a mock template.
5. **Recoverability audit** (pre-freeze, instrument-side): a 60-item random
   sample per vertical is given to an independent judge identity (no lexicon
   access) who must recover (op, relation/concept label, entity label) from
   the phrasing alone; < 95% recovery blocks freeze (the phrasings, not the
   parser, would be indicted — a FAIL must not be manufacturable by
   unanswerable phrasings). Recorded in the phrasing manifest.
6. Mock phrasings (`--mock`) are template-generated scaffold English,
   quarantined under `poc/nlb-mock/`, never under `data/`, and never shown to
   any authoring identity. They exercise mechanics only (§9).
7. **Synonym-boundary PROBE** (FK-NLB-8): 60 covered qids per vertical
   (deterministic largest-remainder stratified sample), each phrased a
   second time by a further fresh identity under
   `data/nlb-phrasings-*/prompt-probe.md`, which FORBIDS the relation/
   concept label (l3a) or the op's keyword family (a5). Reported as
   `/analysis/synonym_probe` (parse + exactness rates), **descriptive only,
   never gated, carved out of the envelope** — it bounds the known
   single-label-lexicon synonym penalty without letting it decide the
   verdict in either direction. Probe items never enter the primary's
   denominator (the gated K=1 eval phrasings are a disjoint authoring pass).

Cost of the protocol: ~1,831 eval + 120 dev + 120 probe phrasings + audits ≈
**$8–12 of agent API spend, the only spend in this experiment**.

## 6. Endpoints (EXACTLY ONE primary per record) and verdict rules

All bounds: one-sided Wilson (kot_common formula), z = 1.645 for primary and
kill rules; the two gated secondaries form ONE Holm family per record
(step-down over their one-sided p-values at family α = 0.05; the analysis
script exports booleans, §6.3).

### 6.1 Primary (per record) — retained covered exactness, non-inferiority form

`/analysis/retained_covered_exact_wilson_lb` — one-sided Wilson 95% LB of the
**mapper-parse arm's covered-exact rate** over the SAME covered queries the
parent froze (l3a-parse n=527 — the FK-NLB-10 shape-recoverable in-scope
slice of the 600 executed, §14.2; a5-nl n=855), scored EXACTLY as the parent
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
  programme POLICY choice, registered as ASM-0141 (STIPULATED), with
  FK-NLB-2 re-opening on an INCONCLUSIVE landing.
- Planning value 0.95 → LB 0.9320 (l3a-parse, n=527 — FK-NLB-10 re-scope,
  §14.2) / 0.9363 (a5-nl, n=855; the draft's 0.9351 was corrected at the
  freeze-candidate recomputation, §7): clears the floor; passes the P8 §1.6
  decidability lint (§7).

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
  (incl. malformed) on the engine that actually runs (§10.9) and must reproduce the
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
| primary n | 527 (FK-NLB-10 in-scope; 600 executed) | 855 |
| PASS needs (LB > 0.90) | ≥ 486/527 (0.9222) | ≥ 784/855 (0.9170) |
| FAIL fires (UB ≤ 0.90) | ≤ 462/527 (0.8767) | ≤ 755/855 (0.8830) |
| INCONCLUSIVE band | 463–485 (~4.4 pp) | 756–783 (~3.3 pp) |
| planning value 0.95 → LB | 0.9320 ✓ | 0.9363 ✓ |
| S1 n (FK-NLB-5) | 270, gate 0.95 | 106, gate 0.90 |
| S1 passes from (z=1.96) | ≥ 264/270 | ≥ 102/106 |
| S1 planning 0.99 → LB (z=1.96) | 0.9695 ✓ | 0.9476 ✓ |
| S2 gate UB < 0.02 passes up to (z=1.96) | ≤ 4/527 wrong | ≤ 9/855 wrong |
| S2 kill fires (LB ≥ 0.02, z=1.645) | ≥ 16/527 wrong | ≥ 24/855 wrong |
| S2 planning value | 3/527 → UB 0.0166 ✓ | 4/855 → UB 0.0120 ✓ |

Every gate is passable at its planning value and failable well inside the
support — no vacuous gates. (FK-NLB-7 records why a5's S1 sits at 0.90.)
FREEZE-CANDIDATE correction (2026-07-10): four informative planning-value
restatements in the draft table (a5 primary LB, a5 S1 LB, both S2 planning
UBs) and the a5 S2 kill count (draft said ≥25) were recomputed and corrected
above; the pinned analysis scripts' `--selftest` fixtures sit ON these
recomputed boundaries. No decision boundary of the l3a column changed AT
THAT CORRECTION. FK-NLB-10 re-base (2026-07-10, §14.8 item 9): the l3a
column now shows the LIVE n=527 boundaries of §14.2 — the superseded
600-item numbers (553/527/0.9332/≤5/≥18/0.0146) survive only in document
history, so this section and §14.2 no longer disagree on the binding l3a
endpoint.

## 8. Extrapolation envelope (verbatim into both records)

Measured range: R0 — no host model; ONE deterministic front-end build
(mapper a1-hybrid pin + one gazetteer + one frozen frame rule set), ONE
blind-authored phrasing set per vertical (K=1 per query, agent-authored under
the §5 protocol), the parents' frozen evals/stores byte-identical and the
engine behaviourally parent-perfect on the parent evals, re-verified in-run
by G2 (the engine sha differs from the parent pin — §10.9/§14.8 item 8;
kot_code alone is byte-identical). A PASS licenses: "the closed grammar —
for l3a-parse, the 7-family shape-recoverable slice of it ONLY (n=527,
FK-NLB-10/§14.2; the two dropped families ride along as a measured
partial-negative) — is reachable from THESE held-out NL phrasings by a
deterministic training-free front-end with ≤10% exactness loss and an
intact fail-closed contract, per vertical" — the gate the successors
l3a-cost / a5-llm need to include an NL leg honestly, inherited on l3a-cost
ONLY at the same 7-family slice with the exclusion restated. A PASS does
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
  lexicon, applies a1-hybrid policy — pin verified at import; `--derange`
  applies the seed-pinned derangement).
- `tools/experiments/nlb/nlb_frontend.py` — gazetteer + frame layer
  (**finalised on DEV only 2026-07-10; sha 5903777… pinned in both
  records**; any later edit mints a new record id).
- `tools/experiments/nlb/nlb_instrument.py` — arms, scoring, dev/probe
  passes, kot-log/1 body (RAW OUTPUT ONLY; counts, no derived stats, knows
  no thresholds).
- `tools/experiments/nlb/nlb_lint.py` — the G3 corpus lints (receipt
  committed next to the corpus and embedded in run-body pins).
- `tools/experiments/nlb/nlb_devtune.py` — DEV frame-finalisation runner
  (receipt committed with the corpus).
- `tools/experiments/nlb/gen_author_packets.py` — deterministic author
  packets for the blind EVAL/PROBE build.
- `tools/experiments/nlb/gen_mock_phrasings.py` — scaffold-English mock
  phrasings (quarantined, `--mock` only).
- `analysis/l3a_parse.py`, `analysis/a5_nl.py` — pinned (shas in the
  records); **deviation from the draft's "+ shared helper": the two scripts
  are deliberately SELF-CONTAINED byte-twins** (per-record constants; no
  shared import), so each record's analysis pin is a complete artifact with
  no unpinned import surface. Both carry `--selftest` fixtures on the §7
  decision boundaries.

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
(ii) the FK-NLB-8 diversity quotas force the phrasings off any single
syntactic template (the channel a surface-form-tuned author would exploit),
the label-verbatim vs paraphrase stratification makes any residual
label-use inflation VISIBLE in the report rather than deniable, and the
never-gated synonym probe bounds the no-label penalty separately — the
draft's forced no-label quota was replaced because it measured a
by-construction zero and would have manufactured the kill
[STIPULATED: ASM-0144]; (iii) the recoverability audit
(§5.5) blocks the symmetric attack (unanswerable phrasings manufacturing a
FAIL); (iv) transcripts are committed, so the auditor can re-derive
blindness. RESIDUAL RISK, registered: agent authors share training
distribution with the mapper's label vocabulary — a human-authored phrasing
set would be stricter; scoped out by ASM-0140 and carved out of the envelope
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

**10.8 Designer-authored DEV (freeze-candidate attack).** Threat: the
designer (who has read the lexicon and the mapper) authors the DEV set and
tunes the frame on it — could that inflate the primary? Channel analysis:
inflation requires the DEV distribution to predict the EVAL distribution's
*idiosyncrasies*; EVAL phrasings do not exist at tuning time and are later
authored blind by fresh identities from packets the designer's phrasings
never touch, and DEV items are over fresh entities never scored anywhere
(linted). What designer-DEV *can* do is fit the frame to unrepresentative
syntax — which shows up as EVAL misses, i.e. LOWERS the primary
(conservative). The symmetric attack (designer authors deliberately easy DEV
so G4 passes while the artifact is broken) is bounded by G4's role: it is an
instrument gate, not evidence for the primary; a broken front-end still
fails on EVAL where it counts. Residual risk registered as ASM-0145; the
non-designer skeptic re-attacks this against the BUILT corpus before freeze.

**10.9 Engine drift since the parents froze.** The define-op line extended
`kot_axiom.py` after the parents' freeze, so the "byte-identical engine"
premise of the draft is FALSE at head. Repair: the records pin the engine
that actually runs (sha d2640881…) and make behavioural identity on the
parent surface an EXECUTABLE in-run gate — G2 must reproduce the
parent-perfect 600/600+300/300 and 855/855+122/122 on the byte-identical
parent evals/stores, and G2 failure is INSTRUMENT-INVALID while G2 success
is a PASS conjunct. Measured green on the 2026-07-10 mock receipts
[STIPULATED: ASM-0147]. A byte-identity claim that is not re-verified would
have been weaker than this gate.

Skeptic conclusion: with G2–G6 + the §5 ordering protocol in place, the
remaining unmitigated risks are ASM-0140 (agent-authored proxy), ASM-0145
(designer-DEV, conservative direction), ASM-0147 (engine continuity via G2)
and the inherited parent stipulations — all registered, none load-bearing
for the verdict function itself. CLEAR TO PROCEED TO FREEZE once §11 items
1–6 are green. (This memo attacks the DESIGN; the pre-freeze skeptic pass
must be re-run by a non-designer identity against the BUILT inputs.)

## 11. Build plan to freeze (this record STOPS before item 7)

1. Harness skeleton + mock green (`--mock`, both verticals) — **DONE
   (draft)** (`poc/nlb-mock/` receipts).
2. DEV phrasing authoring — **DONE (freeze-candidate, 2026-07-10)**:
   60/vertical over fresh disjoint identities (FK-NLB-9), committed with
   dev-entities, dev-tune receipts and lint receipts.
3. Frame-layer finalisation against DEV only; front-end sha pinned in both
   records — **DONE (2026-07-10)**: dev abstention 7/60 (l3a) and 4/60 (a5),
   zero wrong-slot parses among expect-parse DEV items, mocks re-greened
   (600/600 + 855/855 scaffold exactness, zero wrong answers).
4. EVAL + PROBE phrasing authoring (1,831 + 120, fresh identities); lints;
   manifest; recoverability audit; corpus-pin `data/nlb-phrasings-*` —
   **SPECIFIED for the Opus runner** (`tools/experiments/nlb/
   EVAL-BUILD-SPEC.md`; pinned prompts + deterministic packet generator
   committed). NOT design work; the designer must not author any phrasing.
5. Analysis scripts finalised; output-field list matches records; mock pass
   green end-to-end including analysis — **DONE (2026-07-10)**: selftests on
   the §7 boundaries pass; mock bodies → analysis produce every output
   field with all gates green.
6. Independent skeptic re-attack on the BUILT inputs (non-designer
   identity) — **OWED; routed by the coordinator; blocks freeze.**
7. `prereg-freeze.py` on `l3a-parse` then `a5-nl` (or batch), external
   timestamp, frozen_sha into the index. **NOT EXECUTED — the
   freeze-candidate stops here by design.**
8. Handoff to Opus runner (foreground gates; run ≠ design ≠ grade ≠ audit;
   Codex cross-vendor audit on any computed PASS).

## 12. Registered assumptions (`registry/assumptions.jsonl`)

All registered 2026-07-10 (freeze-candidate pass; reserved block
ASM-0140…0159), owner designer-1, plus the draft-time ASM-0026:

- **ASM-0026** — FK-NLB-1 record topology (two records, one shared harness);
  cited by the §13 DECISION line.
- **ASM-0140** (draft name ASM-NLB-1) — agent-authored blind phrasings as an
  adequate held-out proxy; natural-user-distribution claims excluded from
  the envelope regardless.
- **ASM-0141** (draft name ASM-NLB-2) — the 0.10 maximum NL-boundary loss
  (floor 0.90) as the programme's reachability policy instantiating HL3a
  clause 2's "pre-declared fraction"; INCONCLUSIVE re-opens FK-NLB-2.
- **ASM-0142** (draft name ASM-NLB-3) — entity labels given to authors are
  the entities' only names; the mapper lexicon contains no entity surface
  forms, so providing them is not lexicon leakage (choice STIPULATED, backed
  by the inspectable lexicon content).
- **ASM-0143** (draft name ASM-NLB-4) — ERR_PARSE is an acceptable control
  refusal for S1 (FK-NLB-6); the dangerous direction is separately gated.
- **ASM-0144** — FK-NLB-8: paraphrase quota replaced by syntactic-diversity
  quotas + the never-gated synonym probe.
- **ASM-0145** — FK-NLB-9: designer-authored DEV over fresh identities
  disjoint from every scored item.
- **ASM-0146** — the frame layer's closed knowledge (orientation table,
  label-variant matcher, op defaults; NO concept aliasing).
- **ASM-0147** — engine continuity via the executable G2 gate (kot_axiom
  extended post-parent-freeze by the define-op line).
- Inherited, still open, relied on: ASM-0004/0005/0006 (l3a),
  ASM-0007/0008/0009 (a5) — restated at verdict time per the honesty guard.

## 13. Registered scope statement

Everything measured here is a property of THIS front-end build, THESE two
blind-authored phrasing sets, and the parents' frozen evals/stores/engine.
It extrapolates to no other phrasing distribution, corpus, domain, or
language; no LLM-comparative claim; no kernel-usefulness-to-model claim.

- DECISION: two records, two per-vertical verdicts, one shared harness
  (FK-NLB-1) [STIPULATED: ASM-0026] — the registered record-topology
  methodology stipulation, backed by (not constituted by) the frozen
  parents' per-vertical successor pre-declarations
  (registry/experiments/l3a.json + a5.json `design.n_planned.successors`).

---

## 14. Post-build adjudication (2026-07-10) — the two freeze-blocking findings

Author: Kern (Fable designer role). The blind EVAL build (Opus runner,
EVAL-BUILD-SPEC) surfaced two freeze blockers; adjudicated in
`registry/assessments/l3a-parse-recoverability.json` (the interpretive
record) and amended here. Both records remain DRAFT; nothing frozen is
touched; the corpora at commit b4a21fc are byte-untouched; no phrasing is
edited or re-rolled outside the spec's own remedies.

### 14.1 Finding 1 — l3a recoverability 0.7167 < 0.95: GENUINE FINDING

- PREMISE: strict blind recovery 43/60 = 0.7167; shape+entity-only ceiling
  52/60 = 0.8667 < 0.95 with rel-label matching ignored entirely; all 8
  genuine shape failures fall in unique-maker (3/4 sampled), made-lookup
  (4/4 sampled) and out-of-scope-rel (1 control) — zero shape misses in the
  other 13 sampled families (28/28 sampled in-scope covered items
  shape+entity-correct; the earlier revision's 27/27 was an off-by-one
  against the committed artifact — corrected §14.8 item 10)
  [MEASURED: data/nlb-phrasings-l3a/audit-recoverability.json sha256
  d6365bd95e7d61a1cce7585bb446aa8f905b2b8eec08d0756a446e2e70a09bf5].
- Adjudication: NOT a scorer artifact, NOT an authoring defect. English
  unmarked wh-questions are number-neutral and, for agentive noun relations
  (maker of), orientation-flexible; the grammar's unique-vs-lookup and
  role-vs-flip distinctions on NON-functional relations are not injectively
  recoverable from faithful natural phrasings. Functional relations
  (mother/father) recover cleanly via world-knowledge defaults. The finding
  is a MEASURED instrument-level partial-negative on NL-boundary
  reachability; the irreducibility reading is designer interpretation with
  stated bounds (one judge, agent authors, K=1, English) — see the
  assessment record for the full epistemic-status statement.
- Registered hazard the gate preempted: by the pinned S2 definition, a
  faithful unmarked unique-maker phrasing fail-closed-parsed to `lookup`
  answers a singleton list against scalar gold and scores as a DANGEROUS
  wrong answer; 43 such items sit above the S2 kill trigger (18/600) — an
  un-re-scoped run could have manufactured the fail-closed kill from
  information the phrasings never carried.

### 14.2 FK-NLB-10 — l3a shape-recoverable scope cut (re-scope, new fork)

- DECISION: l3a-parse scores its primary and S2 over the shape-recoverable
  covered set only: DROP unique-maker (43) and made-lookup (30) from the
  gated denominators → n_scored = 527 over 7 families (children-lookup 100,
  count-maker 43, instance-false-disjoint 40, instance-true 50, part-lookup
  50, unique-father 122, unique-mother 122). The run still executes all 600
  covered phrasings; the two dropped strata are reported as a DESCRIPTIVE
  quarantined shape-ambiguous stratum (`/analysis/shape_ambiguous_stratum`),
  never gated, carved out of the envelope. Corpus, packets, phrasings,
  front-end, instrument, G2 arm: byte-identical; the scope lives in the
  pinned analysis script alone. Controls unchanged (270, S1 gate 0.95).
  Precedent: FK-NLB-5 (malformed excluded as having no faithful NL
  rendering); here the absence of a shape-faithful rendering is MEASURED
  rather than a priori. [STIPULATED: ASM-0420]
- Re-opens when: a successor adds marked-English phrasings or answer-shape
  equivalence scoring (new record id); the quarantined stratum's descriptive
  results inform it.
- Envelope edit (verbatim into the record at freeze): the PASS claim covers
  the 7-family shape-recoverable slice ONLY, and the record carries the
  measured partial-negative for the dropped shapes as a registered finding,
  not silence.

Updated §7 decidability (l3a column; a5 unchanged; kot_common Wilson):

| Quantity | l3a-parse (n=527) |
|---|---|
| PASS needs (LB > 0.90, z=1.645) | ≥ 486/527 (0.9222) |
| FAIL fires (UB ≤ 0.90) | ≤ 462/527 (0.8767) |
| INCONCLUSIVE band | 463–485 (~4.4 pp) |
| planning value 0.95 → LB | 0.9320 ✓ |
| S2 gate UB < 0.02 passes up to (z=1.96) | ≤ 4/527 wrong |
| S2 kill fires (LB ≥ 0.02, z=1.645) | ≥ 16/527 wrong |
| S2 planning value | 3/527 → UB 0.0166 ✓ |

Every gate remains passable at its planning value and failable inside the
support. S1 unchanged (n=270, gate 0.95, passes from 264/270, planning 0.99
→ LB 0.9695 at z=1.96).

### 14.3 Recoverability-audit gate: split + extension (amends §5.5)

- DECISION: the audit gate is the SHAPE+ENTITY recovery rate over a 60-item
  COVERED-only in-scope sample, gate ≥ 0.95 (≥ 57/60). Rel/concept-label
  recovery and control-item recovery become DESCRIPTIVE. Rationale: the
  gate's registered purpose is answerability (a FAIL must not be
  manufacturable by unanswerable phrasings); shape+entity carries that.
  Gating on label recovery under stem-overlap would force label-verbatim
  authoring through the back door — re-imposing what FK-NLB-8
  registered-removed — and double-counts the synonym penalty that the
  experiment itself measures (label-verbatim stratification + probe).
  Controls are insensitive to shape recovery in the dangerous direction
  (any parse of an out-of-scope/unknown item still refuses).
  [STIPULATED: ASM-0421]
- DECISION: no judge re-roll. l3a audit r1 = mechanical re-score of the
  COMMITTED judge transcript restricted to in-scope covered sampled items
  (28/28 shape+entity-correct — 4 per in-scope family; the earlier
  revision's 27/27, echoed in the ASM-0422 register rationale, was an
  off-by-one against the committed artifact, corrected §14.8 item 10) + a
  FRESH judge identity on NEW in-scope items only (32 items), topping the
  covered-only sample to 60 (same pinned prompt-audit.md, same
  deterministic sample rule over the 7 in-scope families, skipping
  already-judged qids). Artifact: `audit-recoverability-r1.json`; the
  original artifact stays committed as the driving evidence. The a5 audit
  (not yet run at that point) uses the split gate from the start —
  genuinely pre-data on that vertical. [STIPULATED: ASM-0422]
- Sizing honesty (non-gating): in-sample natural-synonym phrasing on
  in-scope covered items is 9/28 = 0.3214 (denominator corrected §14.8
  item 10; ASM-0425's register line says 9/27 = 0.333 — superseded by the
  artifact's 28-item in-scope sample, direction and consequence unchanged)
  [MEASURED: audit sha256
  d6365bd95e7d61a1cce7585bb446aa8f905b2b8eec08d0756a446e2e70a09bf5 +
  audit-recoverability-r1.json sha256
  57e9d8d12826ae6ba28da4289fcc703109b2fb9994ef99eb589655874ea6da6d];
  against the single-label lexicon this makes the 0.95 planning value
  implausible and an INCONCLUSIVE/FAIL primary landing live
  (ASM-0425, EXTRAPOLATION, load-bearing for nothing). The re-scope does
  NOT remove synonym-phrased items; a FAIL routes to parser investment per
  the frozen kill text.

### 14.4 Finding 2 — a5 lint RED, 28 structural leaks: FK-NLB-11 (new fork)

- PREMISE: all 28 EVAL-NO-ANSWER items verified structural — every leaked
  answer surface occurs only inside the mandatory verbatim entity
  identifier and is a substring of (or equal to) it: nested-function name
  prefixes (where-defined 9, contained-in 9) and self-recursive call edges
  (callers-of 5, callees-of 5); recomputed 28/28 on 2026-07-10
  [MEASURED: data/nlb-phrasings-a5/lint-receipt.json sha256
  da8c693da230f8dd6fdc75917ccbd40a476fcb28bddc5076ef477e64fda9acc8 +
  eval.jsonl sha256
  074b686cb5b0d8227c21f966f7c935e18fab002eb5d245033558e2321a5f1ba8].
- DECISION (remedy): EXEMPT forced-substring leaks in the lint, disclosed —
  EVAL-NO-ANSWER masks all occurrences of the item's entity surfaces
  (longest-first, the existing mask_template discipline) and flags only
  answer surfaces that SURVIVE masking; every exempted qid is listed in a
  new receipt field `waived_forced_substring` (never silent). The 28 items
  STAY in the a5-nl scored set: they are NL-faithful and answerable, they
  are the only items covering nested-definition and self-recursion
  semantics, and no arm in this record can exploit the leak (the
  deterministic pipeline extracts nothing from surfaces; answer-all's
  fabrication policy is surface-blind). Alternatives rejected: dropping the
  28 deletes a real semantic slice to satisfy a guard aimed at
  surface-reading arms this record does not have; accepting a RED receipt
  kills gate G3 permanently. MANDATORY REUSE CAVEAT: any successor with a
  model-based arm (a5-llm re-freeze) MUST exclude or re-phrase the waived
  qids — an LLM can read the answer off the question; the caveat is written
  into the a5-nl record's successors field. l3a re-lints under the new rule
  and must stay green with an EMPTY waived list. [STIPULATED: ASM-0423]
- EVAL-DIVERSITY (instance-true 111/216): no new decision — EVAL-BUILD-SPEC
  step 4's fresh-identity re-authoring remedy applies as written; the
  coordinator executes it, then re-lints, THEN runs the a5 recoverability
  audit (step 5) under the §14.3 split gate.

### 14.5 Blindness invariant for the post-data edits

- DECISION: the blindness ordering this design binds itself to (§5.3/§10.2)
  is carried by the FRONT-END artifacts and the phrasing corpora:
  nlb_frontend.py, nlb_map.mjs, the mapper policy pin, and every committed
  phrasing byte stay untouched from the pre-EVAL pin through freeze.
  Scorer-side artifacts (nlb_lint.py, analysis/l3a_parse.py, analysis/
  a5_nl.py, record JSONs) MAY change in this pre-freeze design iteration in
  response to instrument-side findings, because the front-end cannot have
  adapted to the phrasings. Both records re-pin the new shas; the
  independent skeptic re-attack (§11 item 6) is EXPLICITLY tasked to attack
  ASM-0420..0425 as potential forking-paths moves; the maintainer holds a
  veto at freeze. [STIPULATED: ASM-0424]
- ROUND-2 QUALIFICATION of the clause "no scored outcome exists" that this
  section previously relied on: it held only until the 0847ce0
  mapper-parse diagnostic (§14.7 disclosure). Scorer-side edits ratified
  AFTER that commit — the ASM-0480 enrichment ratification and the §14.8
  round-2 hardening — are POST-OUTCOME-DISCLOSED edits; their lawfulness
  rests on the disclosed-deviation terms of ASM-0620 (pre-diagnostic
  commit chronology of the carve-out and schema requirement, byte-frozen
  front-end/phrasings, deterministic outcomes, skeptic gate + maintainer
  veto), NOT on outcome-blindness, which this design no longer claims for
  them. [STIPULATED: ASM-0620]

### 14.6 Coordinator change-list (exact; nothing else changes)

1. `tools/experiments/nlb/nlb_lint.py`: EVAL-NO-ANSWER → masked
   forced-substring rule + `waived_forced_substring` receipt field (14.4).
   Re-run BOTH verticals: l3a green + empty waived list; a5 green after
   step 3 below.
2. `analysis/l3a_parse.py`: gated denominators restricted to the 7
   in-scope families (n=527); new descriptive output fields
   `/analysis/shape_ambiguous_stratum` (per-family exactness/refusal/wrong
   over unique-maker + made-lookup) and `/analysis/audit_r1_ref`; selftest
   fixtures moved to the 14.2 boundaries (486/462/4/16). `analysis/a5_nl.py`
   unchanged except EXPECTED_PHRASINGS_SHA256 at step 6 as already spec'd.
   Implementation consumes the per-family covered-outcome buckets ratified
   in §14.7 (exact mechanical spec there; amendment of 2026-07-10).
3. a5 instance-true re-authoring per EVAL-BUILD-SPEC step 4 (fresh
   identity, same packets, appended transcripts); never hand-edit text.
4. l3a audit r1 per 14.3 (mechanical re-score + fresh-judge extension to
   60 covered-only in-scope; gate ≥ 57/60). a5 audit per step 5 under the
   split gate.
5. Record edits (both DRAFT): re-pin nlb_lint.py + nlb_instrument.py
   (§14.7 enrichment, ASM-0480) + analysis shas in harness_manifest/pins;
   l3a-parse n_planned gains
   `n_covered_run: 600, n_covered_scored: 527`,
   `shape_ambiguous_strata: {unique-maker: 43, made-lookup: 30}`, endpoint
   texts and wilson_gate n updated to 527 per 14.2; a5-nl successors field
   gains the FK-NLB-11 reuse caveat; both records cite ASM-0420..0425 +
   ASM-0480.
6. Then corpus pins (spec step 6), smoke (step 7), skeptic re-attack
   (§11 item 6, scope extended per 14.5), prereg-freeze (item 7).

Deferred: `ERR_KB_INTERNAL`-only kb-sync (coordinator heals; not run here
per the standing instruction).

### 14.7 Scorer enrichment ratification (2026-07-10) — unblocks §14.6 step 2

Author: Kern (Fable designer role), adjudicating the runner's blocker from
the §14.6 partial. Amends the §14.6 change-list (items 2 and 5 as edited
above); everything else in §14 stands.

- PREMISE: §14.6 step 2 needs the S2 numerator restricted to the 7
  in-scope families and a per-family descriptive `shape_ambiguous_stratum`,
  but the pinned instrument's `score_nl` emits `by_family` as `{n, ok}`
  only (ok = exact on covered families), so neither quantity is derivable
  from the pinned emission plus run totals; substituting the run-level
  `n_covered_answered_wrong` would rest on the contingent fact that the
  dropped families abstained — the manufactured-kill pathway §14.1
  preempts, should that fact ever fail on a re-run
  [MEASURED: runner build report, commit
  0847ce079189b4d1244911fe026b0799e1db4da7; pre-EVAL instrument pin
  426722aa813a7843190849348a6b309f3e898d19a0b979f354d5207dc85c6073].
- DECISION (ratifies the runner-proposed fix): `score_nl.by_family` gains
  four ADDITIVE per-family covered-outcome buckets
  `{exact, wrong, refused_parse, refused_engine}` — a pure re-bucketing of
  outcomes score_nl already classifies, each bucket incremented on exactly
  the branch of its existing run-level counterpart; `n`/`ok` semantics
  unchanged; buckets stay zero on control families; no parse, outcome,
  phrasing, or front-end behaviour changes; frame files stay byte-frozen.
  Extends the ASM-0424 lawful scorer-side edit set by this one named,
  diff-scoped edit and no other [STIPULATED: ASM-0480].

Outcome→bucket mapping (covered items; each row is the SAME branch as its
run-level twin — no new predicate exists):

| bucket | increments when | run-level twin |
|---|---|---|
| `exact` | status=answer AND value==expected AND (mapper/deranged arms) provenance⊆world + license non-empty | `n_covered_exact` (== `ok` on covered) |
| `wrong` | status=answer AND not exact | `n_covered_answered_wrong` |
| `refused_parse` | status≠answer AND code==ERR_PARSE | `n_covered_refused_parse` |
| `refused_engine` | status≠answer AND code≠ERR_PARSE (incl. policy ABSTAIN on the abstain-all arm, mirroring the run total) | `n_covered_refused_engine` |

Invariants (mechanically checkable, folded into G1 per the step-2 spec
below): per covered family `exact + wrong + refused_parse + refused_engine
== n` and `exact == ok`; summed over the 9 covered families each bucket
equals its run-level twin; control families hold zeros and keep `ok` =
acceptable-refusal.

- Lawfulness: `score_nl` runs strictly AFTER `run_nl_arm` has produced
  every outcome; it neither parses nor answers, so the edit cannot leak
  eval content into the system under test. The §14.5 blindness invariant
  is carried by nlb_frontend.py, nlb_map.mjs, the mapper policy pin and
  the phrasing bytes — all byte-untouched (diff confined to `score_nl`;
  `run_nl_arm`, `fabricate`, oracle construction and the parse invocation
  byte-unchanged). The G6 determinism gate compares outcomes, not metrics,
  so it is unaffected. ASM-0424's enumeration named the lint/analysis
  scripts but not the instrument's aggregation function; ASM-0480 closes
  that gap for this single edit — any OTHER nlb_instrument.py edit still
  mints a new record id.
- Verification: both green-mocks re-run GREEN under the enriched
  instrument with receipts byte-identical except the wall-clock
  `frontend_total_ns` (timing, run-varying by nature); new instrument
  sha256 3d92e1ab7ef71ae577f63f8955f4381bc90a7c257e44102089220b96e25853d2
  [MEASURED: poc/nlb-mock/l3a/mock-receipt.json sha256
  9122a6d10fc5fc35860be2c569d72a0ec8b4d92e6bad9e6c6173b956b5895f46 +
  poc/nlb-mock/a5/mock-receipt.json sha256
  57b96de51e09c030f37797132e8b57d757260776d3884654e308241e0b8ac8d9,
  checks all green].
- Diagnostic disclosure (load-bearing for NOTHING in this ratification):
  the runner reported — commit-message only, no committed artifact — that
  on a mapper-parse diagnostic pass the dropped families all abstained
  (unique-maker 43/43 refused, 0 wrong; in-scope wrong = total wrong = 8)
  [MEASURED: commit 0847ce079189b4d1244911fe026b0799e1db4da7 message;
  non-verdict]. The enrichment's SCHEMA was forced by the step-2
  requirement registered before that diagnostic ran, and the family
  carve-out itself was declared (924bf6b) before the diagnostic (0847ce0)
  [MEASURED: commit chronology, independently confirmed by the round-2
  skeptic]. ROUND-2 CORRECTION (§14.8 item 1): this bullet previously
  claimed the edit was "OUTCOME-INVARIANT … the same edit would be
  ratified whatever the diagnostic had shown" — that counterfactual is an
  after-the-fact stipulation with no enforcement mechanism; it is
  WITHDRAWN as a premise and relied on nowhere. What stands is the honest
  framing: ratifying scorer details and freezing AFTER the diagnostic is
  post-outcome registration with respect to the disclosed quantities — a
  registered protocol deviation the records carry under the disclosed
  terms of ASM-0620, not a blind-constraint claim. [STIPULATED: ASM-0620]
  The pre-freeze peek at scored outcomes remains a protocol deviation to
  disclose: the independent skeptic re-attack scope (§14.5) extends to
  ASM-0480, ASM-0620 and this diagnostic disclosure.

Exact step-2 spec for `analysis/l3a_parse.py` (mechanical; implements
§14.6 item 2 using the buckets):

1. Constants: `IN_SCOPE_FAMILIES = ("children-lookup", "count-maker",
   "instance-false-disjoint", "instance-true", "part-lookup",
   "unique-father", "unique-mother")`; `SHAPE_AMBIGUOUS_FAMILIES =
   ("unique-maker", "made-lookup")`; `N_SCORED = 527`.
2. Numerators from `by_family` sums over IN_SCOPE_FAMILIES:
   `n_scored = Σ n` (must equal 527), `exact_in = Σ exact`,
   `wrong_in = Σ wrong`. Primary = `exact_in/527` with Wilson LB/UB at
   z=1.645 vs floor 0.90 (boundaries: PASS ≥486, FAIL-UB ≤462). S2 =
   `wrong_in/527` in the unchanged m=2 Holm family with S1 (270 controls,
   gate 0.95, run-level totals as today); S2 gate UB < 0.02 (passes ≤4 at
   z=1.96), kill leg LB ≥ 0.02 (fires ≥16 at z=1.645, exported
   unadjusted). Boundaries independently recomputed 2026-07-10: LB(486) =
   0.9008 > 0.90 vs 485 → 0.8987; UB(462) = 0.8983 ≤ 0.90 vs 463 →
   0.9001; S2 UB(4) = 0.0194 < 0.02 vs 5 → 0.0220; kill LB(16) = 0.0203 ≥
   0.02 vs 15 → 0.0187; planning 0.95 → LB 0.9320, 3/527 → UB 0.0166.
3. G1 extension (counts-integrity, same gate): existing checks PLUS
   (i) `n_scored == 527`; (ii) per covered family the bucket partition
   `exact + wrong + refused_parse + refused_engine == n` and
   `exact == ok`; (iii) covered-family bucket sums equal the run-level
   twins (`n_covered_exact`, `n_covered_answered_wrong`,
   `n_covered_refused_parse`, `n_covered_refused_engine`). Any failure ⇒
   instrument-invalid.
4. Outputs: `/analysis/n_covered_run` (600) and `/analysis/n_covered_scored`
   (527) REPLACE `/analysis/n_covered` (the record's output_fields list is
   updated at step 5 — no silently reinterpreted field);
   `/analysis/shape_ambiguous_stratum` = per family in
   SHAPE_AMBIGUOUS_FAMILIES `{n, exact, wrong, refused_parse,
   refused_engine, exact_rate}` + a note string "descriptive only; never
   gated; carved out of the envelope (FK-NLB-10, ASM-0420)";
   `/analysis/audit_r1_ref` =
   `{path: "data/nlb-phrasings-l3a/audit-recoverability-r1.json", sha256:
   "57e9d8d12826ae6ba28da4289fcc703109b2fb9994ef99eb589655874ea6da6d"}`.
   Full-run descriptives (parse_ok_rate over 870, label strata,
   stage breakdown, dev, probe, cost) stay full-run, disclosed as such.
5. Selftest: fixture builder emits enriched by_family; boundary fixtures
   at 486/462 (primary) and 4/16 (S2/kill) with the varied counts placed
   in in-scope families; S1 fixtures unchanged (264/263 Holm-worst, 263
   nominal); PLUS an isolation fixture placing `wrong > 0` in a
   SHAPE_AMBIGUOUS family and asserting it moves NO gate and NO gated
   numerator and appears only in `shape_ambiguous_stratum`; PLUS a G1
   fixture where a bucket partition is broken ⇒ instrument-invalid.
6. `analysis/a5_nl.py`: UNCHANGED now (additive by_family keys are ignored
   by its reads and fixtures); EXPECTED_PHRASINGS_SHA256 at step 6 as
   already spec'd.

Re-pin instruction (executed at §14.6 item 5, both DRAFT records,
harness_manifest): replace the nlb_instrument.py pin
`426722aa813a7843190849348a6b309f3e898d19a0b979f354d5207dc85c6073`
with
`3d92e1ab7ef71ae577f63f8955f4381bc90a7c257e44102089220b96e25853d2`
annotated "(14.7 score_nl by_family enrichment, ASM-0480; supersedes the
pre-EVAL pin)", alongside the already-owed nlb_lint.py re-pin
`c141004caed2d855ac74deb62ab3c0648f97c77be3f82ccd3116d3cf8b65e112`
and the analysis-script re-pins. (The nlb_lint.py pin was superseded again
by the §14.8 item-11 arms-profile guard.)

### 14.8 Independent-skeptic round-2 remediation (2026-07-10)

Author: Kern (Fable designer role). The §11 item-6 independent re-attack
(non-designer identity, cross-vendor) returned 8 freeze-blocking + 3
should-fix defects against the freeze-candidate
(`poc/nlb-skeptic/skeptic-output.txt`, committed verbatim); its findings 3,
5 and part of 6 were empirically REPRODUCED against the pinned scorers. All
11 are remediated below; the independent re-attack gate re-runs on this
revision before any freeze. The ASM-0424 boundary holds: front-end
artifacts, the mapper policy pin and every committed phrasing/eval byte are
untouched; every edit here is scorer-side or record-side. The round-2
skeptic CONFIRMED all Wilson bound arithmetic — nothing in this section
moves an endpoint, a threshold, or a decision boundary.

1. **Post-outcome registration framing (finding 1).** DECISION: the
   "would-ratify-under-every-outcome" counterfactual in the previous §14.7
   revision is WITHDRAWN — it is an after-the-fact stipulation with no
   enforcement mechanism, and this design does not claim an enforceable
   blind constraint over the post-diagnostic edits. The honest framing now
   carried by §14.5, §14.7 and both records: scorer-side edits and pins
   ratified after the 0847ce0 diagnostic are POST-OUTCOME-DISCLOSED (the
   diagnostic disclosed that the dropped families abstained and that 8
   in-scope items answered wrong), a registered protocol deviation whose
   residual risk — the designer knew those disclosed quantities while
   finalising scorer details — is NOT claimed to be zero. The deviation's
   disclosed terms: (i) the FK-NLB-10 carve-out and the enrichment schema
   requirement pre-date the diagnostic in the commit record [MEASURED:
   924bf6b / 0847ce0 chronology, independently confirmed by the round-2
   skeptic]; (ii) front-end, phrasing and eval bytes were pinned before
   the diagnostic and are now G7-enforced at analysis time; (iii) the
   pipeline is deterministic, so no selection-among-stochastic-outcomes
   channel exists; (iv) the independent skeptic gate and the maintainer
   veto remain the final control. [STIPULATED: ASM-0620]
2. **Envelope restricted to the 7-family slice (finding 2).** DECISION:
   the l3a-parse record's PASS-licenses text and successor inheritance are
   restricted VERBATIM to the 7-family shape-recoverable slice (n=527): a
   PASS licenses reachability of that slice ONLY, the 73 excluded items
   ride along as a measured partial-negative (never silence), and any
   l3a-cost NL leg inherits ONLY the slice and must restate the exclusion
   — executing the §14.2 envelope edit that the record text had failed to
   carry, so the excluded families can no longer game a
   whole-closed-grammar claim. [STIPULATED: ASM-0420]
3. **Fail-closed one-row-per-arm (finding 3, REPRODUCED).** DECISION: both
   pinned scorers open with gate G0: duplicate/retry rows for the same arm
   are never resolved by log order; a re-run row must EXPLICITLY supersede
   every row it replaces via a top-level `supersedes: [<sha256 of the
   replaced body's sorted-keys JSON>]`; more than one non-superseded row
   per arm, or a dangling supersede target, is INSTRUMENT-INVALID in both
   log orders (selftested on the skeptic's good+bad-row reproduction in
   both orders). [STIPULATED: ASM-0621]
4. **Harness pins enforced (finding 4).** DECISION: new gate G7 in both
   pinned scorers compares the instrument-emitted `pins_observed` —
   engine (+ kot_code on a5), nlb_instrument.py, nlb_frontend.py,
   nlb_map.mjs, the parents' corpus digests, the phrasing corpus files
   (eval/dev/dev-entities/probe/manifest), the lint receipt and the
   kot-corpus-hash/1 recipe string — against frozen constants byte-copied
   from the records, on EVERY arm body; any drift or a missing pins block
   fails closed to INSTRUMENT-INVALID. The lint-receipt sha pin
   transitively enforces receipt content: l3a waived_forced_substring
   EMPTY, a5 exactly the 28 disclosed qids (ASM-0423).
   [STIPULATED: ASM-0621]
5. **Deranged arm must exist (finding 5, REPRODUCED).** DECISION: G5 now
   requires the deranged-lexicon arm to EXIST with well-formed integer
   counts over the full planned covered set before its collapse is tested;
   a missing arm, empty metrics, or absent n_covered_exact is a broken
   instrument, never "perfect collapse" (selftested on the skeptic's
   empty-metrics reproduction). [STIPULATED: ASM-0621]
6. **Full counts integrity in BOTH scorers (finding 6, partly
   REPRODUCED).** DECISION: both scorers gate, fail-closed in G1: the
   run-level covered outcome partition (exact + wrong + refused_parse +
   refused_engine == 600 l3a / 855 a5); the run-level control partition
   (answered + acceptable + other == 270/106, refused_any == acceptable +
   other, acceptable == strict + parse on the mapper arm, which never
   emits ABSTAIN); family-key set equality (unexpected families rejected);
   the per-family bucket partition + exact == ok; covered bucket sums ==
   run-level twins; zero covered buckets on control families; and
   non-negative-integer buckets everywhere. The skeptic's reproduced a5
   conflict (n_covered_exact=855 AND n_covered_refused_parse=855 both
   green) is now a selftest fixture asserting INSTRUMENT-INVALID.
   [STIPULATED: ASM-0621]
7. **Mechanical freezability (finding 7).** Record-side repairs: both
   records now carry the exact kot-corpus-hash/1 recipe string in
   `pins.corpus_hashes._recipe`; `prereg_doc.sha256` is pinned to this
   document revision (placeholder replaced); the schema-rejected
   `pins.analysis_script.sha_note` is removed with its provenance prose
   folded into `harness_manifest`. One further mechanical repair surfaced
   by the dry-run itself: the RT-4 constraint-9 checker only powers
   LB-exceeds-threshold gates, so the S2 endpoint's `wilson_gate` is
   declared in COMPLEMENT form — {expected_rate 0.995, threshold 0.98} —
   which is the IDENTICAL gate by the Wilson complement identity
   LB(1−p, n, z) ≡ 1 − UB(p, n, z) (verified numerically at both n: the
   4/527 and 9/855 pass boundaries are bit-equal under both forms); the
   tested quantity, the 0.02 bound and every decision boundary are
   unchanged, and the endpoint metric stays
   `/analysis/holm_s2_pass` computed from the UB as registered. Second
   dry-run-surfaced repair: the D9 collision refusal fires on the
   trivial-policy cells (abstain-all / answer-all at R0 are already logged
   by the parents at mechanically indeterminate pins), so both records are
   upgraded to kot-reg/2 with a `reuse_overrides` DELIBERATE-FRESH-RE-RUN
   entry (the a5-llm precedent): reuse-permission is deferred
   programme-wide (the ratification interlock), and the logged parent rows
   could not serve as these records' arm outputs even in principle — here
   the trivial policies run over the NL PHRASINGS through the front-end
   (answer-all parses, then fabricates), not over the parents' gold
   structured queries, and they are $0 deterministic CPU cells.
   `prereg-freeze.py --dry-run` passes on both records at this revision.
8. **Honest engine claim (finding 8).** DECISION: record titles, envelopes
   and baseline-arm texts no longer assert a byte-identical parent engine;
   the carried claim is "behaviourally parent-perfect on the parents'
   frozen evals, re-verified IN-RUN by gate G2" — the engine sha differs
   from the parent pin (§10.9) and only kot_code is byte-identical; the
   already-honest harness_manifest text is now the record's ONLY engine
   identity claim. [STIPULATED: ASM-0147]
9. **Denominator sync + anchors (finding 9).** §6.1 and the §7 table now
   carry the live l3a n=527 boundaries (§14.2) and the corrected a5
   planning LB 0.9363 (the superseded 0.9351 removed from §6); both
   records' `prereg_doc.anchors` gain "section 14" so the binding
   amendment is inside the pinned anchor set.
10. **r1 audit provenance (finding 10).** Correction: the original-audit
    sample contains 28 (not 27) in-scope covered items; r1 = 28
    mechanically re-scored + 32 fresh-judge items (4 per in-scope family
    in the rescored subset), and the in-sample natural-synonym rate is
    9/28 = 0.3214 (not 9/27 = 0.333); the 60/60 r1 gate result is
    unchanged [MEASURED: data/nlb-phrasings-l3a/audit-recoverability-r1.json
    sha256 57e9d8d12826ae6ba28da4289fcc703109b2fb9994ef99eb589655874ea6da6d].
    The 27/33 and 9/27 counts inside the ASM-0422 / ASM-0425 register
    rationales are superseded by the artifact's 28/32 and 9/28; the
    register lines are append-only history and stand there uncorrected —
    §14.1/§14.3 as amended are the authoritative restatement.
11. **Model-arm lint guard fail-closed (finding 11).** DECISION:
    nlb_lint.py now DEFAULTS to `--arms-profile model`, under which a
    nonempty `waived_forced_substring` list is itself a blocking finding
    (green=False) — reusing this lint for any successor with a model-based
    arm fails closed instead of relying on the prose caveat; the explicit
    attestation `--arms-profile deterministic-r0` (lawful ONLY for records
    whose every arm is deterministic and surface-blind, i.e. THIS pair) is
    the pinned invocation, and the committed receipts regenerate
    byte-identically under it (verified 2026-07-10, both verticals), so
    all corpus digests are unchanged. [STIPULATED: ASM-0621]

Gate-list amendment: the §6.3 instrument-gate set G1–G6 is extended by G0
(one-row-per-arm) and G7 (harness-pin enforcement); both fold into
`/gates/instrument_valid`, so the records' verdict rules and output-field
lists are unchanged. Re-pins executed in this change (both DRAFT records):
analysis/l3a_parse.py and analysis/a5_nl.py at their round-2 shas,
nlb_lint.py at the arms-profile-guard sha, and prereg_doc.sha256 at this
document revision. G6 determinism, G2 gold replication, every Wilson
threshold and every planned n are byte-unchanged from §14.2/§7.
