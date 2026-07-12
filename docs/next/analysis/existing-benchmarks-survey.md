# Existing human-built benchmarks survey — escaping the LLM-proxy-gold trap

**Status:** analysis/survey only. Composed 2026-07-12 by a Fable research agent under the
maintainer directive (2026-07-12): *"find existing benchmarks that have already been built by
humans where possible"* — so that the two programme theses can be evaluated on openly-licensed,
externally-authored gold instead of custom LLM-proxy-gold evals. This document changes no frozen
record, issues no verdict, and states no feasibility conclusion; **CORRECTNESS and EFFICIENCY
remain INCONCLUSIVE-PENDING** (ASM-1380 lineage). ASM rows are PROPOSED only
(PROPOSED-ASM-1590..1609 block reserved); `registry/assumptions.jsonl` is untouched.

**Epistemic tags:** every license/provenance fact below is tagged **[search 2026-07-12]**
(verified at source or via search today) or **[memory — VERIFY AT ADOPTION]** (from training
memory; must be re-verified against the shipped LICENSE file before any freeze). Gold-provenance
classes used throughout:

- **HUMAN-AUTHORED** — items and labels written/adjudicated by people for this dataset.
- **HUMAN-SOURCED (EXAM)** — items taken from real human exams; labels are the official keys.
- **HYBRID** — synthetic label generation + human surface authoring/paraphrase or human validation.
- **SYNTHETIC-SOLVER** — labels computed by a symbolic engine over generated worlds.
- **SYNTHETIC-TEMPLATE** — items and labels emitted by a program/grammar.
- **LLM-PROXY** — labels produced by an LLM judge. **This is the trap the directive targets; none
  of the adopted benchmarks below may be in this class.**

Two distinct defensibility notes, so they are not conflated later:

1. **SYNTHETIC ≠ LLM-PROXY.** Solver-derived gold (ProofWriter, ProntoQA, CLADDER, bAbI) is
   deterministic and reproducible, not judge-opinion. It escapes the *proxy* trap but re-imports a
   version of the CASC-0′ `d-casc0` concern: when the system under test is itself a rules engine,
   grading against another engine's output measures engine–engine agreement, not human meaning.
   Third-party authorship (the generating engine predates us and is not ours) makes this far
   stronger than self-authored gold, but it is still not human adjudication. All SYNTHETIC rows
   below are flagged accordingly.
2. **Human SURFACE vs human LABELS.** CLUTRR's stories are human (AMT) paraphrases, but its
   *labels* are graph-sampled synthetic kinship facts — human-validated surface over synthetic
   gold (HYBRID). The 858/858 RULES-1 leg is therefore "exact against third-party
   synthetic-graph gold with human-paraphrased surface", not "exact against human judgment".
   This survey exists to add benchmarks whose *labels* are human.

---

## 1. Harness reuse facts (measured in-repo)

What "wiring effort" is scored against — all [MEASURED: in-repo, 2026-07-12]:

- **Forced-choice scorer:** `poc/f2b-transfer/runner/f2bt_runner.py` `HFLM._option_logprobs` /
  `HFLM.choose` + seeded resampler (SEED_BASE 20260710) + verify-retry topology (k retries,
  memory-slot injection, gold-leak guard). Reused byte-identical by rules-1 / rules-2 / deconf-b.
  Any benchmark that reduces to *choose-one-of-N surface options* wires in at LOW effort.
- **Corpus-build pattern:** `poc/nsk1/build_clutrr_corpus.py` — a pure mechanical function of the
  fetched dataset bytes + pinned seed, consuming only *released structured columns* (never
  parsing NL), fail-closed on format assertions, emitting `world.jsonl`/`items.jsonl` +
  manifest + LICENSE-NOTICE, kot-corpus-hash/1 pinned. New benchmarks follow this template.
- **Engine profile boundary:** the RULES-1 inventory is closed, safe, function-free
  (R-SUBP/R-DOM/R-RNG/R-INV/R-CHAIN/R-COVER-ELIM; owl-rl/horn-def/policy regimes) and *refuses*
  outside it (`poc/rules-1/RESULT.md`; expressivity boundary: no arithmetic, no quantifier
  alternation, no full FOL). Benchmarks needing full FOL or arithmetic can still be used at the
  **host verify-retry seam**, but the engine leg must carry a measured OUT-OF-PROFILE /
  coverage disclosure (four-valued contract, round2-arch-synthesis §1.1).
- **Input envelope:** all current positive results are gold-parse / structured-input scoped.
  A benchmark whose premises exist *only* as free NL (no released structure/formal annotation)
  forces an NL front-end — a natural-input boundary crossing that is currently unresolved
  programme-wide, so it scores HIGH wiring effort for any engine-bearing claim.

Effort bands: **LOW** ≈ ≤1 agent-day (builder script + f2b scorer reuse); **MEDIUM** ≈ 2–5
agent-days (new scoring path or structure compiler with disclosed coverage); **HIGH** ≈ needs an
NL front-end or new engine capability.

---

## 2. Correctness family — relational / entailment / ontology / deductive reasoning

### 2.1 Summary table

| Benchmark | Tests | License | Size | Gold provenance | Claim map | Wiring effort |
|---|---|---|---|---|---|---|
| **CLUTRR** (in use) | multi-hop kinship relational reasoning | CC-BY-NC-4.0 [MEASURED: in-repo manifest] | 6k+ items (858 covered 2-hop in nsk1) | **HYBRID** — synthetic graph-sampled labels, human AMT-paraphrased stories | CORRECTNESS: entailed-beyond-stated (RULES-1) | DONE |
| **FOLIO** | NL deductive entailment (True/False/Unknown) with expert FOL annotations | MIT [search 2026-07-12] | 1,430 conclusions / 487 premise sets | **HUMAN-AUTHORED** (expert-written NL + FOL; labels prover-checked over the *human* formulas) | CORRECTNESS: both host seam and engine leg (partial profile) | LOW (host seam) / MEDIUM (engine leg) |
| **EntailmentBank** | multi-step entailment trees for science QA | code Apache-2.0 [search 2026-07-12]; dataset license on allenai.org page [memory: CC BY 4.0 — VERIFY AT ADOPTION] | 1,840 expert trees (over ARC questions) | **HUMAN-AUTHORED** (expert annotators) | CORRECTNESS: checking-engine/aligned-store adds entailed steps; attribution vs kernel-authored keys | MEDIUM |
| **ARC** (Easy/Challenge) | grade-school science MC QA | CC BY-SA 4.0 [search 2026-07-12] | 7,787 questions | **HUMAN-SOURCED (EXAM)** | CORRECTNESS end-task carrier (pairs with EntailmentBank); host forced-choice | LOW |
| **ProofWriter** | rule+fact theories, T/F/Unknown with proofs, CWA+OWA, depth-graded | CC BY [search 2026-07-12] | ~500k QA pairs across D0–D5 | **SYNTHETIC-SOLVER** ⚠ | CORRECTNESS: engine soundness at depth; host lift from injected proofs | LOW–MEDIUM |
| **RuleTaker** (D* datasets) | same family, predecessor of ProofWriter | CC BY [memory — VERIFY] | ~100k+ | **SYNTHETIC-TEMPLATE/SOLVER** ⚠ | subsumed by ProofWriter | (use ProofWriter) |
| **ProntoQA / ProntoQA-OOD** | syllogistic chains over (fictional) ontologies, parseable CoT | repo asaparov/prontoqa; license file unconfirmed [search 2026-07-12 — VERIFY; memory: Apache-2.0] | generator (arbitrary size) | **SYNTHETIC-TEMPLATE** ⚠ | CORRECTNESS: hop-depth generalisation; formally parseable | LOW–MEDIUM |
| **LogicNLI** | multi-step FOL NLI (entail/contradict/neutral/paradox) | repo omnilabNLP/LogicNLI — no confirmed license [search 2026-07-12 — BLOCKER until verified] | 20k | **HYBRID (semi-synthetic)** ⚠ | CORRECTNESS: FOL robustness/generalisation diagnostics | MEDIUM |
| **bAbI (tasks 1–20)** | 20 toy reasoning skills incl. deduction, induction, path-finding | CC BY 3.0 [search 2026-07-12] | 1k–10k per task | **SYNTHETIC-TEMPLATE** ⚠ | weak; saturated benchmark, low defensibility | LOW (but not recommended) |
| **CLADDER** | causal ladder (assoc./interv./counterfactual) yes/no | HF causalNLP/cladder; license unconfirmed [search 2026-07-12 — VERIFY; memory: MIT] | 10k | **SYNTHETIC-SOLVER** (causal-inference engine) ⚠ | future world-layer/causal claims; out of current engine profile | HIGH (engine) / LOW (host) |
| **StrategyQA** | implicit multi-hop yes/no with human decompositions | dataset via AI2; repo MIT [memory — VERIFY AT ADOPTION] | 2,780 | **HUMAN-AUTHORED** (crowdworkers + evidence annotation) | weak map: implicit-strategy + world-knowledge, not deductive closure | HIGH for engine; LOW for host (but claim map poor) |

⚠ = synthetic gold: escapes LLM-proxy but not the engine-derived-gold rider; must never be
reported as human-validated.

### 2.2 Per-benchmark notes (what the table can't carry)

**FOLIO** — the strongest human-gold deductive benchmark available. Premises and conclusions are
written by humans (experts + trained annotators, much of it about real-world topics), each with a
human-written FOL formalisation; labels come from running a prover over the *human-authored*
formulas, so the label chain is human-meaning → human-formalisation → mechanical check — exactly
the authored/endorsed → deterministic-closure discipline this programme already uses, but
executed by an independent third party before this programme existed. Two seams:
(i) *host seam* (LOW): 3-way forced choice (True/False/Unknown) over NL premises — direct
`HFLM.choose` reuse, works for A1/A3/A5-shaped arms immediately;
(ii) *engine leg* (MEDIUM): a mechanical FOL→profile compiler from the released FOL annotations
(no NL parsing — the structure is a released column, satisfying the build-recipe discipline).
Full FOL exceeds the safe Horn inventory, so a measured fraction of items will be
OUT-OF-PROFILE; that fraction is a *disclosed coverage statistic*, and the four-valued contract
(ENTAILED/CONTRADICTED/UNDERDETERMINED/OUT-OF-PROFILE) reports it honestly. Even a partial-profile
engine leg on FOLIO would be the first *human-gold* analogue of the CLUTRR 858/858 soundness leg.
Known caveat from the literature: a small number of FOLIO label/formalisation errors have been
reported by downstream users [memory]; adoption should pin a specific release + errata list.

**EntailmentBank** — 1,840 expert-annotated entailment trees showing how an ARC science answer is
entailed from WorldTree-derived premises. This is human gold for *entailment structure*, not just
answers, which is precisely the shape of the checking-engine claim ("adds correct entailed
decisions beyond stated lookup"). Three published task settings (T1: leaves given; T2: leaves +
distractors; T3: full-corpus retrieval) give a difficulty ladder that stays inside the structured
envelope for T1/T2. Second, strategically important use: EB trees are a *third-party-authored
aligned store*. f2b/DECONF left open whether "independently authored non-kernel content matches
the useful kernel-authored key" (synthesis-v5 §5.2) — projecting EB premises/trees into the
aligned verify-retry store and measuring host lift on ARC gold attacks that attribution gap with
human-built content at zero authoring cost. Effort MEDIUM: tree→store/world projection script +
ARC forced-choice scoring. Dataset license must be read off the allenai.org page at adoption
(code repo is Apache-2.0; the dataset page carries its own terms).

**ARC** — the end-task carrier for EntailmentBank (EB hypotheses are built from ARC QA pairs).
Human exam questions, official keys, CC BY-SA 4.0, 4-way MC → byte-level f2b scorer fit. On its
own it tests science knowledge + reasoning (not isolatable closure); paired with EB trees it
becomes the natural human-gold end-task for the aligned-store and checking-engine mechanisms.

**ProofWriter / RuleTaker** — the standard depth-graded deduction suite. NL is templated from an
underlying formal theory (released), so a mechanical theory→profile compiler needs no NL parsing;
CWA/OWA and "Unknown" labels exercise exactly the fail-closed refusal discipline the engine
already certifies. Best use is *diagnostic*: engine soundness/refusal at depth d ∈ {0..5}, and
host-lift arms where the engine injects licensed rejections — not as a headline correctness
claim, because gold is solver-derived (⚠ above). CC BY, huge n, effectively free statistical
power. ProntoQA-OOD adds controlled out-of-distribution deduction rules for generalisation
probes; same synthetic caveat, plus its license file must be confirmed before any freeze.

**LogicNLI** — semi-synthetic FOL NLI with four labels including *paradox* (contradiction
detection — maps to the engine's ERR_CONFLICT/CAX-DW behaviour). Interesting diagnostics but:
no confirmed open license found today (adoption blocker until resolved) and gold is
generator-derived.

**bAbI** — historically important, CC BY 3.0, but template-synthetic, largely saturated, and its
deduction tasks are strictly weaker than ProofWriter's. Not recommended; listed for completeness.

**CLADDER** — the gold is computed by a causal-inference engine over generated graphs (the paper
is explicit about the oracle). It maps to a *future* world-layer/causal-regime claim, not to the
current closed inventory (do-calculus is out of profile). Park for the Lean-seam/world-layer era.

**StrategyQA** — genuinely human gold, but the reasoning it tests is implicit-strategy +
open-world knowledge; there is no released formal structure, so an engine-bearing claim needs the
unresolved NL front-end, and even host-seam results would not isolate entailment. Poor claim map
despite good provenance.

**Considered and deprioritised (one line each):** SNLI/MNLI (human gold, CC BY-SA 4.0 [memory],
but single-step lexical entailment — doesn't exercise closure); ANLI (human adversarial, CC-BY-NC
[memory]); LogiQA 2.0 / ReClor / AR-LSAT (human exam gold but non-commercial/restrictive terms
[memory] — license posture conflicts with "openly-licensed" directive; ReClor requires agreement);
WANLI (LLM-generated with human review — partially inside the proxy trap, excluded); LogicBench /
SimpleLogic (synthetic-template, dominated by ProofWriter/ProntoQA).

---

## 3. Efficiency family — small-model verifier-offload / compression

The EFFICIENCY thesis needs a human-gold task where (small host + cheap deterministic checker) is
compared against a larger host at matched cost — the registered s3-noninferiority shape
(`noninferiority_vs_r3=false` is the standing open result).

| Benchmark | Tests | License | Size | Gold provenance | Claim map | Wiring effort |
|---|---|---|---|---|---|---|
| **GSM8K** | multi-step grade-school math word problems | MIT [search 2026-07-12] | 8.5k (7.5k/1k test) | **HUMAN-AUTHORED** (contracted problem writers; full NL solutions) | EFFICIENCY: verify-retry with a *deterministic arithmetic checker*; the original OpenAI verifier paper is the published precedent for exactly this offload | MEDIUM |
| **SVAMP** | robustness variations on 1-step math WPs | MIT [memory — VERIFY] | 1k | HUMAN-curated variations over human items | secondary robustness leg for the same seam | LOW–MEDIUM |
| **ASDiv** | diverse math WPs | CC BY-NC 4.0 [memory — VERIFY] | 2.3k | HUMAN | same, NC restriction noted | LOW–MEDIUM |
| **ARC / FOLIO reused** | as §2 | as §2 | as §2 | HUMAN | EFFICIENCY: A5-style 1.7B comparator arms on the *same* human-gold items as the correctness legs — one corpus, both theses | LOW increment |

Notes:

- **GSM8K caveat (expressivity):** the RULES-1 engine *cannot* check arithmetic (documented
  boundary, PROPOSED-ASM-1196) and must not be dressed up as if it could. The cheap checker at
  this seam is an extraction+calculator/consistency verifier (à la the published
  verifier/self-consistency literature) — still deterministic, still ~$0, but it tests the
  *verifier-offload architecture claim*, not the rules engine. That is a legitimate EFFICIENCY
  probe (the thesis is "small host + cheap checker matches a bigger model", not "the kinship
  engine does math") and it must be labelled as such. Scoring is generative exact-match on the
  final number, not forced-choice — a new (small) scoring path beside `HFLM.choose`, hence
  MEDIUM.
- **Self-consistency baselines:** GSM8K/SVAMP/ARC are the canonical self-consistency datasets, so
  the pinned self-consistency-at-matched-budget control (already precedented in DECONF-B) has
  published reference numbers to sanity-check against.
- The **cheapest defensible efficiency move** is not GSM8K but reusing the §2 human-gold
  correctness corpora with an added big-host comparator arm: same items, same scorer, and the
  noninferiority endpoint lands on human gold for free.

---

## 4. Recommendation — top adoptions

**TOP RECOMMENDATION (single): FOLIO.** Human-authored premises, conclusions, *and*
formalisations; MIT-licensed; 3-way forced choice that reuses the f2b scorer at LOW effort for an
immediate host-seam experiment; released FOL structure that permits a no-NL-parsing engine leg
with honestly-disclosed profile coverage. It is the only benchmark surveyed that upgrades the
programme's flagship correctness leg (CLUTRR 858/858 — hybrid gold) to fully human gold while
staying inside the structured-input envelope. Size (1,430) is modest but comparable to current
campaign sizes and above the g2 n≥500 instrument bar if the full set is used.

**Adopt second: EntailmentBank + ARC (as one package).** Human expert entailment trees over human
exam questions; attacks two open gaps at once — (i) a human-gold test of "checking adds entailed
decisions" on natural science content, and (ii) the f2b attribution gap, by substituting a
third-party human-authored aligned store for the kernel-authored key. MEDIUM effort. Verify the
EB dataset license on the allenai.org page at adoption.

**Adopt third (efficiency lane): GSM8K.** Human gold, MIT, and the published verifier-offload
precedent makes it the defensible arena for the s3-noninferiority shape — with the explicit
disclosure that the checker there is an arithmetic verifier, not the rules engine.

**Keep as diagnostics, never headlines: ProofWriter (and ProntoQA-OOD).** Free statistical power
for depth/refusal/generalisation curves, but synthetic solver gold — flag ⚠ in every readout.

Suggested sequencing (cheapest-decisive-first, consistent with round-2 constraints; all subject
to the standard prereg-freeze discipline, and none delaying the in-flight gates): FOLIO host-seam
build + prereg (~1–2 days, $0 CPU mock → small GPU arm) → EB/ARC store-projection build →
GSM8K verifier lane when the efficiency comparator is next scheduled.

---

## 5. Proposed ASM rows (PROPOSED-ASM-1590..1609 block; nothing written to registry)

```json
[
 {"id":"PROPOSED-ASM-1590","tag":"STIPULATED","claim":"Gold-provenance taxonomy for benchmark adoption: HUMAN-AUTHORED, HUMAN-SOURCED(EXAM), HYBRID, SYNTHETIC-SOLVER, SYNTHETIC-TEMPLATE, LLM-PROXY. Per the 2026-07-12 maintainer directive, new evals prefer existing human-built benchmarks; LLM-PROXY gold is excluded for adopted benchmarks; SYNTHETIC-* gold may be used for diagnostics only and must carry an explicit non-human-gold flag in every readout.","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md","rationale":"Makes the proxy-trap escape mechanical rather than rhetorical.","load_bearing":true,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"SYNTHETIC-SOLVER escapes the LLM-proxy trap but retains an engine-derived-gold rider (d-casc0 lineage)."},
 {"id":"PROPOSED-ASM-1591","tag":"STIPULATED","claim":"CLUTRR gold-provenance rider: nsk1-clutrr labels are synthetic graph-sampled kinship facts with human AMT-paraphrased surface (HYBRID). The RULES-1 858/858 third-party-gold leg is exact against third-party synthetic-graph gold, not against human adjudication; any 'human-validated' wording is unlicensed.","backing_ref":"poc/nsk1/build_clutrr_corpus.py; Sinha et al. 2019 arXiv:1908.06177; poc/rules-1/RESULT.md","rationale":"Prevents silent upgrade of the flagship correctness leg's gold class.","load_bearing":true,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"Third-party + predates-programme still holds; only the HUMAN class claim is barred."},
 {"id":"PROPOSED-ASM-1592","tag":"STIPULATED","claim":"FOLIO is the top adoption candidate: HUMAN-AUTHORED gold (expert NL + human-written FOL, labels prover-checked over the human formulas), MIT license [search 2026-07-12], 1,430 conclusions / 487 premise sets, 3-way forced choice reusing the f2b HFLM scorer at LOW effort (host seam), with a MEDIUM-effort engine leg via a mechanical FOL-to-profile compiler over the released FOL column and a measured OUT-OF-PROFILE coverage disclosure under the four-valued contract.","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md sec 2.2; github.com/Yale-LILY/FOLIO; arXiv:2209.00840","rationale":"Only surveyed benchmark that gives the deductive-closure claim fully human gold inside the structured-input envelope.","load_bearing":false,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"Pin a specific release + errata list at freeze; a minority of reported label errors exist in the literature [memory]."},
 {"id":"PROPOSED-ASM-1593","tag":"STIPULATED","claim":"EntailmentBank(+ARC) is the second adoption: 1,840 expert-annotated entailment trees (HUMAN) over ARC exam questions (HUMAN, CC BY-SA 4.0), usable both as a human-gold checking-engine eval (T1/T2 stay inside the structured envelope) and as a third-party human-authored aligned store to test the open f2b attribution question of whether independently authored non-kernel content matches the kernel-authored key. EB dataset license must be verified on the allenai.org page before freeze (code repo Apache-2.0).","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md sec 2.2; github.com/allenai/entailment_bank; arXiv:2104.08661","rationale":"One dataset attacks both the entailed-decisions claim and the authoring-attribution gap on human gold.","load_bearing":false,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"MEDIUM effort: tree-to-store projection + ARC forced-choice reuse."},
 {"id":"PROPOSED-ASM-1594","tag":"STIPULATED","claim":"GSM8K (HUMAN-AUTHORED, MIT, 8.5k) is the efficiency-lane adoption for the s3-noninferiority shape, WITH the mandatory disclosure that the cheap deterministic checker there is an arithmetic extraction/consistency verifier, not the RULES-1 engine, whose documented expressivity boundary excludes arithmetic (PROPOSED-ASM-1196). Results test the verifier-offload architecture claim only.","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md sec 3; github.com/openai/grade-school-math; huggingface.co/datasets/openai/gsm8k","rationale":"Human-gold arena with published verifier precedent for the small-host-plus-checker efficiency claim; the disclosure prevents engine-capability over-read.","load_bearing":false,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"Generative exact-match scoring is a new small path beside HFLM.choose (MEDIUM)."},
 {"id":"PROPOSED-ASM-1595","tag":"STIPULATED","claim":"ProofWriter (CC BY) and ProntoQA/-OOD are diagnostics-only: SYNTHETIC-SOLVER/TEMPLATE gold gives free statistical power for depth-graded soundness, refusal (CWA/OWA Unknown), and OOD-rule generalisation curves, but no headline correctness claim may rest on them, and every readout carries the synthetic-gold flag. ProntoQA's repo license must be confirmed before any freeze.","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md secs 2.1-2.2; allenai.org/data/proofwriter; github.com/asaparov/prontoqa","rationale":"Keeps cheap synthetic power available without re-entering a proxy-shaped gold dependency.","load_bearing":false,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"RuleTaker subsumed by ProofWriter; bAbI not recommended (saturated, template-synthetic)."},
 {"id":"PROPOSED-ASM-1596","tag":"STIPULATED","claim":"Adoption blockers recorded: LogicNLI has no confirmed open license [search 2026-07-12] and is HYBRID gold; CLADDER gold is causal-engine-derived and out of the current engine profile; StrategyQA is human-gold but maps poorly (implicit-strategy, NL-only premises, natural-input boundary); LogiQA-2.0/ReClor/AR-LSAT carry restrictive/non-commercial terms conflicting with the openly-licensed directive; WANLI is partially LLM-generated and excluded. None may be adopted without resolving the named blocker.","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md secs 2.2, 3, 4","rationale":"Prevents re-litigating rejected candidates without new facts.","load_bearing":false,"status":"open","owner":"research-agent","date":"2026-07-12","notes":"Every [memory]-tagged license in the survey must be re-verified at source before its benchmark freezes."}
]
```

*(PROPOSED-ASM block 1597..1609 unused; reserved per instruction.)*

---

## Sources ([search 2026-07-12])

- FOLIO: [github.com/Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO/blob/main/README.md), [arXiv:2209.00840](https://arxiv.org/abs/2209.00840), [HF paper page](https://huggingface.co/papers/2209.00840)
- EntailmentBank: [github.com/allenai/entailment_bank](https://github.com/allenai/entailment_bank), [arXiv:2104.08661](https://arxiv.org/pdf/2104.08661), [aclanthology 2021.emnlp-main.585](https://aclanthology.org/2021.emnlp-main.585.pdf)
- ARC: [EleutherAI lm-evaluation-harness ARC README](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/arc/README.md)
- ProofWriter/RuleTaker: [aclanthology 2021.findings-acl.317](https://aclanthology.org/2021.findings-acl.317.pdf), [github.com/allenai/ruletaker](https://github.com/allenai/ruletaker)
- ProntoQA: [github.com/asaparov/prontoqa](https://github.com/asaparov/prontoqa)
- LogicNLI: [github.com/omnilabNLP/LogicNLI](https://github.com/omnilabNLP/LogicNLI), [aclanthology 2021.emnlp-main.303](https://aclanthology.org/2021.emnlp-main.303/)
- bAbI: [facebook/babi_qa on HF](https://huggingface.co/datasets/facebook/babi_qa), [Wolfram Data Repository (CC BY 3.0)](https://datarepository.wolframcloud.com/resources/The-20-Task-bAbI-Question-Answering-Dataset-v1.2)
- CLADDER: [github.com/causalNLP/cladder](https://github.com/causalNLP/cladder), [arXiv:2312.04350](https://arxiv.org/abs/2312.04350)
- StrategyQA: [aclanthology 2021.tacl-1.21](https://aclanthology.org/2021.tacl-1.21/), [HF voidful/StrategyQA](https://huggingface.co/datasets/voidful/StrategyQA)
- GSM8K: [huggingface.co/datasets/openai/gsm8k](https://huggingface.co/datasets/openai/gsm8k), [github.com/openai/grade-school-math](https://github.com/openai/grade-school-math)
- CLUTRR: in-repo `poc/nsk1/build_clutrr_corpus.py` manifest (CC-BY-NC-4.0; Sinha et al. 2019, arXiv:1908.06177)
