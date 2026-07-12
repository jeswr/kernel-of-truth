# RULES-1 build + THE INVERTED-DECONF-A1 CERTIFICATE — result

**Design:** `docs/next/arch/world-model-rules-engine.md` (WMRE-1 + GPT-5.6
fold-in), maintainer-APPROVED with all nine RULES-1 decisions on issue #19
(MD-1..MD-9). This bead executed the approved cheapest-decisive-first plan:
engine → worlds → the ~$0 CPU certificate → the freeze-ready GPU-arm draft.
**Executed:** 2026-07-11, local CPU, ~$0, zero model calls, zero GPU.
**Status: EXPLORATORY (pre-freeze execution).** Every step is deterministic
and pin-gated (double-run sha match measured), so a registered re-run
reproduces these bytes for $0. Nothing here appends to results-log, touches
any frozen record, or issues a verdict. **No feasibility conclusion is stated
or implied anywhere in this document**; verdicts belong to the
maintainer/verdict-gen.

## Question

DECONF-A1 measured C_dec = 1.0 — every decision the structured engine made
was reproducible from a flat projection of the store's STATED bytes
(KERNEL-RUNTIME-STRUCTURE-INERT). The same instrument, INVERTED, on the
RULES-1 engine: does the engine make decisions on ENTAILED-but-never-stated
facts that NO projection of the stated bytes reproduces (C_dec < 1.0 on
entailed cells) while staying exact on stated cells (C_dec = 1.0), with the
engine correct against third-party gold at Wilson-LB ≥ 0.98
(PROPOSED-ASM-1131), plus the per-target counterfactual gates
(PROPOSED-ASM-1163)?

## Results — the certificate (poc/rules-1/results/certificate-result.json)

| Statistic | Value | Tag |
|---|---|---|
| **C_dec on STATED cells** | **1.0 exactly — 1,716/1,716** | [MEASURED] (exhaustive; no sampling) |
| **C_dec on ENTAILED cells** | **0.0 — 0/3,680 reproducible from stated bytes** | [MEASURED] |
| — E3 two-hop CLUTRR (858) + E1 cover-elim (248) + E2 person-typing (2,574) | all non-reproducible | [MEASURED] |
| **Engine vs THIRD-PARTY CLUTRR gold (E3)** | **858/858, Wilson-LB95 0.9955 ≥ 0.98 bar** | [MEASURED] |
| Engine vs held-out world-v0 edge (E1, R-COVER-ELIM policy rule) | 248/248, Wilson-LB95 0.9847 (gold is kernel-authored, NOT third-party — disclosed) | [MEASURED] |
| E5 control refusal (100 up-edge items) | 100/100 named refusals (ERR_INSUFFICIENT_PREMISES), Wilson-LB95 0.9630 | [MEASURED] |
| **KILL-a (Cl(S)\\S empty or trivial)** | **did NOT fire** (858/858 items non-empty; 0 targets stated) | [MEASURED] |
| CF-1 definition-removal (ASM-1163 i) | remove gendered chains → 858/858 E3 refuse; remove covering axiom → 248/248 E1 refuse | [MEASURED] |
| CF-2a chain-only mutation | 858/858 decisions flip to ERR_CONFLICT — the mutated definitions contradict the stated gender data (fail-closed, CAX-DW) | [MEASURED] |
| CF-2b coherent chain+range label swap | 858/858 answers flip grandfather↔grandmother EXACTLY, 0 conflicts | [MEASURED] |
| CF-3 meaning-preserving no-op (record+constraint order permuted) | decisions byte-identical | [MEASURED] |
| Determinism | double full run, decision-payload sha identical | [MEASURED] |
| Cost | main pass 0.4 s / 958 items + 248 cells on 2 shared cores; total < 2 s, $0 | [MEASURED] |

**Reading (flagged, NOT concluded):** on the same mechanical definition under
which DECONF-A1 measured the estate's machinery inert, the RULES-1 engine's
entailed-cell decisions are NOT reproducible from any stated-bytes
projection while its stated-cell behaviour is bit-exact — with soundness on
third-party gold above the pre-registered bar and the provenance gates
(definition-removal / targeted-mutation / no-op) behaving exactly as
predicted. Per PROPOSED-ASM-1138/MD-7 the claim is capped at **machinery
non-inertness**, never "kernel-specific value", until the phase-2 knull
ablation runs; and per the frozen-design discipline this exploratory
execution licenses nothing until the registered re-run.

## Engine identity (PROPOSED-ASM-1124 / MD-4a) — DISCLOSED

- **Both engines ran.** Certificate decisions were computed by the Python
  differential twin (`twin_engine.py`, ~200 LOC, closed inventory R-SUBP /
  R-DOM / R-RNG / R-INV / R-CHAIN(len 2) / R-COVER-ELIM, regime tags
  {owl-rl, horn-def, policy} on every rule and proof node, per-item budgets
  ERR_BUDGET_EXCEEDED, fail-closed ERR_* codes, `why()` proof trees).
- **sparq-reason (primary) built** on this box after installing gcc + a
  minimal rust toolchain (no toolchain was preinstalled; the first attempt
  failed on the missing C linker). Its N3 fixpoint (`reason_n3`) consumed
  the SAME compiled `rules.n3` artifact and **exactly agreed with the twin
  on Cl(S) for all 1,207 conformance cases** (958 nsk1-clutrr items + 248
  world-v0 E1 cells + the §3 worked example) —
  `results/conformance-result.json`. The twin-governs fallback was NOT
  needed. Disclosure: the N3 entry point was exercised, not the OwlRl
  materializer; sparq commit `0ab87b2a5910fe0c783a73dcc043e93ed39c9f58`.
- E1 proofs are policy-regime with the UNA (ASM-1120) and covering
  (ASM-1121) premises named in every `why()` tree; E3 proofs are owl-rl
  only; the horn-def regime is unused in RULES-1 (disclosed).

## Worlds compiled

- **TBox (pinned):** `data/axioms-v0/{rel-mother, rel-father, class-man}` +
  minted **`data/axioms-kinship-v1/`** (this bead): 5 authored molecule-style
  concept records (parent, person, grandparent, grandfather, grandmother)
  minted content-addressed under the exact molecules-v0 `kot-mol/1`
  algorithm (mint self-check reproduced the committed mother/father/man/woman
  URNs byte-exactly first), + 8 `kot-axiom/1` records using extension kinds
  {subPropertyOf, coveredBy, propertyChain, domain, classDeclaration}, each
  citing its endorsing explication sha. **PROVISIONAL — pending explicator
  loop + maintainer endorsement (PROPOSED-ASM-1190); re-pin at freeze.**
  The frozen `kot_axiom.py` refuses the new kinds by design (ASM-1126).
  Non-kinship axioms-v0 records (cardinality etc.) are NOT pinned and
  refuse at load if passed (fail-closed, never skipped).
- **ABox:** nsk1-clutrr per-item temporary worlds (gold-parse only,
  ASM-1123; eval-side only, CC-BY-NC-4.0, ASM-1125) + item-scoped UNA
  sidecar (ASM-1120); world-v0 for the 248 E1 abstraction cells.

## The GPU-arm draft (freeze-ready)

`registry/experiments/rules-1.json` — status **DRAFT**, schema kot-reg/2,
**validated end-to-end by `prereg-freeze.py --dry-run` (DRY-RUN-OK, zero
pause flags)**. Arms A1/A2(descriptive)/A3(model-level primary, k=4)/A4(cost
ledger)/A5/A7(systems); controls c1 Sattolo shuffled-rules (recovery UB95 <
0.30), c2 paraphrase K≥2, c3 GS-B, c4 trivial policies, c6 axioms-as-text;
c5 knull-ablation pre-registered for phase 2 (MD-7); A6 removed (MD-5 as
amended). Primary: A3−A1 paired BCa one-sided 95% LB > 0, KILL-b on LB ≤ 0.
Budget $10 (MD-6c). The certificate is pinned in `pins.artifact_hashes` as
the PASSED precondition; the certificate gate endpoint fires
INSTRUMENT-INVALID (no GPU spend) if its bytes don't carry SUCCESS.

**Freeze steps (coordinator):** (1) route axioms-kinship-v1 through
explicator/maintainer endorsement, re-mint if prose changes, re-run
`corpus-pin.py axioms-kinship-v1` and update the pin; (2) commit
poc/rules-1/* + analysis/rules_1.py + the arch-doc edit, then re-verify the
two PINNED-AT-INPUTS artifact placeholders (twin sha, rules.n3 sha) and the
doc shas in analysis_plan_ref/prereg_doc; (3) registered $0 re-run of
certificate.py + conformance.py under runner-role separation; (4)
`prereg-freeze.py --experiment rules-1 --agent-id coordinator-1` (dry-run
already green) and post the frozen sha to the coordination issue (RT-15);
(5) fill harness_manifest + model_revisions from the nsk1 frozen record
before any final-phase run. NOTE: `poc/rules-1/conformance/target/` (110 MB
rust build dir) is gitignored via `conformance/.gitignore`.

## Expressivity boundary

Recorded in `docs/next/arch/world-model-rules-engine.md`, new section
"Expressivity boundary and the Lean seam" (before Appendix A), per the
maintainer's #19 note: the engine may lack expressivity for e.g.
mathematics; Lean libraries were once brought into core; complex
mathematical inference is a long-term goal via the axiom/world-layer Lean
seam — a much-later consideration, out of RULES-1 scope
(PROPOSED-ASM-1196).

## Proposed ASM rows (PROPOSED-ASM-1190..1197; block 1190..1209 reserved)

Emitted for central registration by the coordinator; this bead wrote nothing
to `registry/assumptions.jsonl`.

```json
[
 {"id":"PROPOSED-ASM-1190","tag":"STIPULATED","claim":"data/axioms-kinship-v1 is minted as: 5 AUTHORED molecule-style concept records (parent, person, grandparent, grandfather, grandmother) content-addressed under the exact molecules-v0 kot-mol/1 identity algorithm (profile header, JCS/NFC identity payload, sha2-256 multihash multibase32; mint self-check reproduced the committed mother/father/man/woman URNs byte-exactly before minting), plus 8 kot-axiom/1 records using extension kinds {subPropertyOf, coveredBy, propertyChain, domain, classDeclaration}, each citing its endorsing explication sha. The concept records are PROVISIONAL authored content by the build role, pending the explicator loop and maintainer endorsement; any registered run must re-pin after endorsement. The frozen tools/axiom/kot_axiom.py refuses the extension kinds (fail-closed), per ASM-1126 notes.","backing_ref":"poc/rules-1/mint_kinship.py; data/axioms-kinship-v1/manifest.json; PROPOSED-ASM-1126","rationale":"Fills the named parent/person gap on the approved MD-1 path without waiting on an explicator session; content-addressing keeps identity honest; the provisional tag and re-pin requirement keep endorsement authority with the explicator/maintainer.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"grandparent/grandfather/grandmother added beyond ASM-1126's ~6 because E3's answer vocabulary is gendered; see PROPOSED-ASM-1191."},
 {"id":"PROPOSED-ASM-1191","tag":"STIPULATED","claim":"E3 gendered-grandparent completion is encoded as pure OWL-RL property chains — parent∘father ⊑ grandfather, parent∘mother ⊑ grandmother, parent∘parent ⊑ grandparent (each with range typing) — rather than a post-hoc gendering Horn rule. Consequence: every E3 proof is regime owl-rl; the policy regime is confined to E1's R-COVER-ELIM; the horn-def regime is unused in RULES-1 (disclosed, not hidden).","backing_ref":"data/axioms-kinship-v1/chain-*.json; docs/next/arch/world-model-rules-engine.md §3 (prp-spo2)","rationale":"Keeps the epistemically strongest stratum carrying the 858-item third-party-gold leg; the contested premises (UNA, covering) touch only the E1 cells that need them.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"Realisation of the §3 'gendered via range' sketch."},
 {"id":"PROPOSED-ASM-1192","tag":"STIPULATED","claim":"Engine identity for the certificate execution: decisions computed by the Python differential twin; sparq-reason (primary, MD-4a) built on-box (after installing gcc + a minimal rust toolchain) and its N3 fixpoint exactly agreed with the twin on Cl(S) for all 1,207 conformance cases over the same compiled rules.n3; the twin-governs fallback (ASM-1124) was NOT used. Scope limit: the N3 entry point was exercised, not the OwlRl materializer; sparq commit 0ab87b2a5910fe0c783a73dcc043e93ed39c9f58.","backing_ref":"poc/rules-1/results/conformance-result.json; poc/rules-1/conformance/","rationale":"ASM-1124's exact-agreement gate executed and disclosed rather than assumed; the entry-point scope limit is named so the conformance claim is not over-read.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"Registered re-run should repeat both engines under runner-role separation."},
 {"id":"PROPOSED-ASM-1193","tag":"STIPULATED","claim":"The certificate's stated-bytes comparator (GS-B) is operationalised as the aligned flat lookup over the item's stated kot-world/1 records projected onto the query read-set: for a relation query (a,b), the lexicon word of a STATED relation record linking a to b (else no-answer); for a class cell, membership of the STATED class record — DECONF-A1's GS-A construction, inverted (the engine's decisions are the reference the projection tries to reproduce).","backing_ref":"poc/rules-1/certificate.py projection_answer(); poc/deconf-a1/build_gsa.py","rationale":"'No projection of the stated bytes' must be made mechanical to be measurable; this is the same projection family the inertness verdict used, so the flip is measured on the maintainer's own definition.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":""},
 {"id":"PROPOSED-ASM-1194","tag":"STIPULATED","claim":"E1 cells are constructed from world-v0 by ABSTRACTION: for each of 124 children with both gendered parent edges stated and distinct, the held-out gendered edge is restated as plain parent (2x124 cells, both directions) with the item-scoped UNA sidecar; gold is the held-out world-v0 stated edge — kernel-authored, NOT third-party. The external-gold soundness bar (Wilson-LB >= 0.98) therefore rests solely on the E3/CLUTRR leg.","backing_ref":"poc/rules-1/certificate.py build_e1_cells(); data/world-v0/","rationale":"Gives R-COVER-ELIM a measured, held-out-by-construction cell family at zero authoring cost while keeping the gold-provenance distinction explicit.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"Gender class records are EXCLUDED from E1 stated sets so the cover-elimination premises are exactly the §3 triple."},
 {"id":"PROPOSED-ASM-1195","tag":"STIPULATED","claim":"ASM-1163's mutation gate is realised as three arms: CF-2a chain-only swap -> PREDICTED outcome is ERR_CONFLICT on every covered decision (the mutated definitions contradict the stated gender records; CAX-DW fail-closed), measured 858/858; CF-2b coherent chain+range label swap -> predicted exact grandfather<->grandmother flip with zero conflicts, measured 858/858; CF-3 meaning-preserving no-op (record + constraint order permuted) -> byte-identical decisions, measured. A chain-only swap CANNOT produce clean flips because range(father)=Man regenerates gender typing — conflict is the only sound outcome; this replaces the naive 'flip' prediction.","backing_ref":"poc/rules-1/certificate.py CF sections; poc/rules-1/results/certificate-result.json counterfactual_gates","rationale":"Makes the 'changes exactly the predicted outputs' gate well-posed; the CF-2a arm additionally measures that the definitions bind against the data (contradiction surfaces, never resolves).","load_bearing":false,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"Extends PROPOSED-ASM-1163."},
 {"id":"PROPOSED-ASM-1196","tag":"STIPULATED","claim":"The RULES-1 engine's expressivity boundary is documented in the architecture record: the closed safe function-free inventory cannot express mathematics (arithmetic, induction, quantifier alternation) and refuses rather than approximates; the future-work seam is the axiom/world-layer Lean route (Lean libraries were once brought into core: data/math-lean-sample, data/mathlib-1000-sample, the kot-pm-* math corpora), entering at the same authored/endorsed C1 boundary with proof-carrying regime-tagged output — a much-later consideration, OUT of RULES-1 scope; no RULES-1 claim extends past the registered inventory.","backing_ref":"docs/next/arch/world-model-rules-engine.md section 'Expressivity boundary and the Lean seam'; maintainer note issue #19","rationale":"Records the maintainer's requested boundary verbatim as a named seam instead of scope silence.","load_bearing":false,"status":"open","owner":"builder-1","date":"2026-07-11","notes":""},
 {"id":"PROPOSED-ASM-1197","tag":"STIPULATED","claim":"The 2026-07-11 certificate + conformance executions are EXPLORATORY pre-freeze runs by the build role; registry/experiments/rules-1.json is a DRAFT (prereg-freeze dry-run green, zero pause flags) and freezing, the registered $0 CPU re-run, the GPU campaign, verdict-gen and audit are the coordinator/runner/analyst/auditor roles' respectively. No result in poc/rules-1/ licenses any claim until the registered re-run under role separation.","backing_ref":"poc/rules-1/RESULT.md; registry/experiments/rules-1.json runner_constraints.roles; deconf-a1 exploratory precedent","rationale":"Run-vs-audit separation and frozen-design discipline preserved while still delivering the decisive free result now.","load_bearing":true,"status":"open","owner":"builder-1","date":"2026-07-11","notes":"Block PROPOSED-ASM-1190..1209 reserved; 1198..1209 unused."}
]
```

## Artifacts & pins

`poc/rules-1/`: `mint_kinship.py`, `twin_engine.py`, `certificate.py`,
`conformance.py`, `conformance/` (rust driver; `target/` gitignored),
`results/certificate-result.json` (sha
`e0071e9e4952f915c461206d514afa555d683bc22985fad2273821f37176d379`,
registered 2026-07-11 re-run on the endorsed+revised corpus; the
pre-revision exploratory run's sha was `01a1943f…ea9505c`),
`results/conformance-result.json` (sha
`0ed1769a774da3cc3d292d1621a12b5d9f2e2c363d2ccf00714b4fc3c0c1bbd9`,
byte-identical across pre-/post-revision runs — counts are
corpus-count-invariant; rewritten by the 2026-07-11 re-run),
`results/rules.n3` (sha `9857da89…6a22f98`, regenerated — carries the
revised grandparent URN); `data/axioms-kinship-v1/` (corpus digest
`be3f2d40c1ad06fe7d706c0e36b4f9290d515e798d8e9e2fbb94dc3a02a1508d`,
kot-corpus-hash/1, POST-endorsement re-pin; the stale pre-revision digest
was `bcff4c80…f3ffa287`); `analysis/rules_1.py` (sha
`6c62f8bd…e5e4870`); `registry/experiments/rules-1.json` (DRAFT,
FREEZE-READY). Input pins verified in the
certificate JSON (items/world/world-v0 shas). No frozen object, verdict,
ruling, or results-log line was modified; `registry/assumptions.jsonl`
untouched.

**Self-check gate:** no feasibility conclusion stated or implied; all tags
provisional/exploratory; claim capped at machinery non-inertness pending c5;
no @handle/account strings; new assumptions confined to the disjoint block
1190..1209; run-vs-audit separation preserved.

## Freeze finalization addendum (2026-07-11, runner role)

The endorse follow-ups are APPLIED; the sections above are preserved as the
pre-revision exploratory record and this addendum is authoritative where they
differ.

1. **Endorsement outcome.** Explicator loop COMPLETED 2026-07-11: parent,
   person, grandfather, grandmother endorsed unchanged; **grandparent
   REVISED** — groundingNote `'the parent' -> 'a parent'` (the definite
   article implied a uniqueness that is false under ordinary meaning; no
   functionality axiom licenses it, unlike 'the father'/'the mother') — and
   re-minted `urn:kot:bciqlzfmtaa5… -> urn:kot:bciqobx6ivvu…`, with the
   dependent chain-* axiom records regenerated. All 8 kot-axiom/1 records
   endorsed sound and correctly scoped. Maintainer endorsement rides the
   freeze approval.
2. **Corpus re-pin.** `tools/registry/corpus-pin.py axioms-kinship-v1` →
   `be3f2d40c1ad06fe7d706c0e36b4f9290d515e798d8e9e2fbb94dc3a02a1508d`
   (supersedes stale `bcff4c80…f3ffa287`); updated in
   `registry/experiments/rules-1.json` pins.corpus_hashes and above.
3. **ASM-1121 pointer fix.** The covering premise's pointer now resolves to
   the minted `data/axioms-kinship-v1/cover-parent.json`, whose endorsement
   block cites the endorsed explication `concepts/parent.json` (sha
   `60508432…7d5cf2`) — covering clause endorsed as read RELATION-LEVEL (to
   be someone's parent is to be that someone's mother or that someone's
   father; the exact form R-COVER-ELIM uses; a disclosed stipulation, never
   claimed analytic) — superseding the bare design-doc-gap backing_ref
   (`docs/design-l3a-rules-engine-oracle.md#7`).
4. **Registered $0 CPU re-run on the revised corpus (runner role,
   pre-freeze precondition pin — NOT a results-log append; rules-1 is not
   frozen).** `certificate.py`: C_dec stated 1.0 (1716/1716), C_dec entailed
   0.0 (0/3680), E3 858/858 vs third-party CLUTRR gold Wilson-LB95 0.9955 ≥
   0.98, E1 248/248 Wilson-LB95 0.9847 (kernel-authored gold, disclosed), E5
   100/100 named refusals, KILL-a NOT fired, CF-1/CF-2a/CF-2b/CF-3 all pass,
   deterministic double-run (decision-payload sha `fce753ba…b070aee5`),
   success_asm_1131=true / gates_asm_1163_all_pass=true / kill_a_fired=false
   — result sha `e0071e9e…7176d379`, pinned in the record as THE PASSED
   PRECONDITION. `conformance.py`: sparq-reason (commit `0ab87b2a…`) vs twin
   exact agreement **1207/1207** over the regenerated `rules.n3`
   (`9857da89…6a22f98`); result bytes identical to the pre-revision run
   (sha `0ed1769a…c0c1bbd9`).
5. **Record finalized FREEZE-READY.** artifact_hashes placeholders resolved
   (twin `399fcd8d…f887e8dea8` — coordinator re-verifies after commit;
   rules.n3 `9857da89…`; sparq-commit bare 40-hex); harness_manifest and
   model_revisions REMAIN PINNED-AT-INPUTS by design (ops amendment from the
   nsk1 frozen record before any final-phase run). The ASM-1190..1197 rows
   as finally worded for registration (owner `designer-1`, per the pseudonym
   check) are emitted in the freeze hand-off, superseding the
   `owner:"builder-1"` draft block above.

Self-check (addendum): runner role only; fail-closed pins throughout; no
@handle/account strings; NO feasibility conclusion stated or implied.
