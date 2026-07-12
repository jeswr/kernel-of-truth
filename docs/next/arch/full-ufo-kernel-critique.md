# full-ufo-kernel — adversarial critique (round-2 architecture exploration)

> **Provenance.** Extracted 2026-07-12 from the `neurosym-arch-exploration` workflow run
> `wf_3870703d-0bb` (journal: `~/.claude/projects/-home-ec2-user-css/85798a0b-4e71-4020-b0b9-ac1fed9631d0/subagents/workflows/wf_3870703d-0bb/journal.jsonl`).
> Agent-output text is **verbatim**; only markdown scaffolding (headings, lists, tables) was added.
> [PROPOSED-ASM-1500] The journal carries no label field; outputs were mapped to the script's agent
> labels by structural schema match + the `name` field inside each result, cross-checked against the
> persisted workflow script (`workflows/wf_3870703d-0bb.json`). [PROPOSED-ASM-1501] Verbatim-extraction
> fidelity: no substantive text was altered, dropped, or paraphrased in this transcription.

> Workflow agent label: `critique:full-ufo-kernel` (adversarial-but-fair; independent of the design
> author pass). Target: `docs/next/arch/full-ufo-kernel-design.md`. Note the critique's "feasible"
> field is a design-level buildability judgment, NOT a programme feasibility verdict — CORRECTNESS
> and EFFICIENCY remain INCONCLUSIVE-PENDING.

## Verdicts

| Field | Value |
|---|---|
| Novel | yes |
| Feasible (design-level: buildable) | yes |
| Cheapest test valid as stated | no |
| GPU-runnable now | no |
| Verdict | **queue** |

## Failure modes

1. Benchmark circularity: the same agent pool authors the UFO rules, the 144-192 cases, AND the gold dispositions; the doc's mitigation ('two UFO-competent reviewers reconciling independently') is not credibly available on an all-LLM programme — two correlated LLM reviewers can pass the go rule by construction. Needs cross-model gold (GPT-5.6 authors gold, Fable authors rules) plus the near-miss counterfactual pairs as the real check.
2. Inference-free information leakage past A1: for most UFO families the authored witness facts (counterworld, closedFor scope, relator participants) are one join away from the gold answer, so the 'checker' acts as a lookup over facts the case author supplied. A1 (same representation, no UFO rules) does not catch this; a trivial witness-lookup baseline arm or a case-design constraint requiring >=2 chained rule applications is missing.
3. 'Zero-authoring derived constraint mass' is conditional, not zero: Kind-pairwise disjointness and the rigid-cannot-specialise-anti-rigid mask fire only over ENDORSED Kind/rigidity classifications, and the bridge protocol defaults to `underdetermined`. At realistic endorsement rates the masks are sparse and the efficiency mechanism (candidate-set shrinkage) largely vanishes; the claim quietly assumes a dense, endorsed bridge that is itself the dominant authoring cost.
4. Repeat of the g2 lesson one level up: rigidity/anti-rigidity flags authored as necessary when reality is semi-rigid or typical produce false CONTRADICTED verdicts. The go rule bounds dangerous false ACCEPTS but not unsupported hard REJECTS entering downstream masks — and mask errors are answer-destroying, not answer-safe, if the underlying classification is wrong (answer-safety is proven only w.r.t. the authored axioms, not w.r.t. the world).
5. sameContinuant identity merges have the largest blast radius: an incorrect executable identity criterion contaminates closure, vector training pairs, and every downstream proof; the doc admits incorrect identity rules are worse than missing ones but the experiment has no endpoint measuring wrong-merge damage propagation.
6. Illegitimate-closure creep: closedFor scopes are authored per case by the same people who know the gold answer; converting UNDERDETERMINED to CONTRADICTED via convenient closure is named as a no-go but 'legitimately declared closed' has no operationalisation.
7. Family-level attribution (A3 module removal) is unpowered: ~24-32 cases per family cannot resolve a 10pp family-specific delta (needs ~150+ per comparison); the module-removal gate as written will produce noise reads that either falsely kill or falsely license modules. Only the aggregate ~180-case paired endpoint is marginally powered.
8. Relator/qua and proposition-node graph blow-up: substantial annotation + runtime cost with no existing task endpoint sensitive to it; the eval families are constructed to need relators, so a pass there does not evidence value on any real workload.
9. L4 statement-vector work has no eval protocol: the vectors estate has no statements-about-statements synthetic slice, no inner-vs-outer corruption semantics for negative sampling, and the in-tree KGE is a CPU trainer with no conditioning machinery for situation-conditioned role/phase blocks — the modal block exceeds what the house pattern (prior reader + sampler behind an ablation) supports without trainer surgery.
10. Portfolio double-spend: the correctness mechanism targets exactly the measured g2 failure (0.39-sound hard typing) that the built-but-unrun g2-import experiment addresses more directly and more cheaply; starting full-UFO before reading g2-import and RULES-1 evidence violates the programme's own reuse/read-before-spend gate, and a g2-import success would remove this proposal's only MEASURED motivation anchor.

## Rationale

NOVELTY: qualified yes. Against the RUN portfolio (RULES-1 kinship Horn vertical, g2-import sort-lattice remedy, DECONF/f2b verifier-offload, CASC — measured dead at f2 scope) nothing has tried executable modal/identity/relator checking or UFO-theorem-derived vector priors. But dedup is mandatory against the programme's own DESIGN estate: this is ~70% a restatement of the already-GO'd UFO-SN3 plan (docs/next/arch/ufo-rdf12-expressibility.md — L2/L3 are that verdict verbatim) plus nsm-ufo-bridge.md (L1) plus the in-repo CK-UFO proposal (docs/next/arch/full-ufo-kernel-ck-ufo.md), which contains the same six-layer design, sequencing, and A0-A4 experiment. Register as ONE candidate, not two. The genuinely new increments are L4(ii) theorem-derived disjointness/subsumption masks, L4(iii) identity-provider ER mask, and L4(vi) compositional statement rows — the last fills a verified real gap (train.rs:353/eval.rs:116 is_entity drops triple terms; grounding.rs renders them empty; taxonomy.rs:33 defers the gufo prior; eval.rs:301,543 gufo_prior hard-false). FEASIBILITY: yes, via the doc's own staging — the ordinary-node adapter lets the decisive CPU experiment run without the 4-8-week native quoted-triple rule engine, and the sparq seams (prior-reader pattern, ablation axis, UFO-SN3 fit) are real. The full native stack is ~3-5 engineering months; the true bottleneck is gold authoring and dense endorsed bridge records, not code. CHEAPEST TEST: well-constructed (representation-matched null A1, module-removal A3, dangerous-false-accept guard, beats-A1 requirement) but NOT valid as stated: (a) gold-authoring circularity with no credible independent-reviewer mitigation on this programme, (b) missing witness-lookup baseline — UFO rules over author-supplied witnesses can be inference-free lookup and A1 doesn't catch it, (c) the family-level A3 attribution gates are unpowered at 24-32 cases/family for a 10pp threshold; only the aggregate paired endpoint is marginally powered. All three are repairable (cross-model gold, one extra trivial-baseline arm, pool attribution or enlarge families). VERDICT: queue. The proposal's own §4.3 says the same: RULES-1 and g2-import are the live evidence gates, g2-import targets the identical measured failure more directly, and the reuse/read-before-spend discipline forbids opening a third correctness front before those reads. Queue behind the g2-import read with the repaired experiment design pre-registered. GPU: no. The decisive experiment is explicitly CPU-only (doc §3.6: 'no required GPU'); the GPU-shaped A4 leg is gated behind the correctness result, needs a 4-8-week encoder plus a statement-slice eval protocol that does not exist, and the in-tree KGE trainer is CPU anyway — nothing here freezes+builds in <1 day to usefully occupy an idle Modal account.
