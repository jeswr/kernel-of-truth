# Kernel of Truth — Research Programme (master overview)

Status: **GNG-0 CANDIDATE — pre-freeze, awaiting maintainer sign-off.** Assembled 2026-07-08 from
eleven components (P1–P11, incl. P10 model↔record interface and P11 funding/compute) by Fable
agents, bound by [`docs/kernel-design-directives.md`](../kernel-design-directives.md). The red-team
verdict was **FIX-THEN-EXECUTE**; the 3 critical + major fixes have since been applied across all
components and an **independent re-verification returned READY-TO-FREEZE** (§8 and `07-redteam.md`).
Nothing is provisioned or spent until the maintainer signs off the ratification list (§9).

## 0. The two questions

1. **Is the kernel principle useful to LLMs at all?** (the go/no-go gate, H0)
2. **If so, which kernel structure is most useful?** (the design-fork hypotheses, HS)

Two value theses, both measured with the full metric vector (accuracy · params · memory ·
compute): **(A) correctness** — kernel as an external verifier/instrument; **(B) efficiency**
— kernel makes models smaller / cheaper at matched-or-better accuracy.

## 1. Hypothesis suite (`01-hypotheses-experiments.md`)

- **H0** — the kernel helps beyond the *kernel-as-text* null AND the strongest industrial
  baseline (RAG / distillation / quantization / smaller-model-alone), at ≥2 scale rungs.
- **HC1–HC5** (correctness, endorsed primary): decode-verify beats text verification;
  axiom-sidecar catches what text cannot; **deterministic verifier ≥ trained PRM** (the narrow
  claim the literature leaves open); kernel ↔ SAE label space (A6); verifier lift non-vanishing
  with scale.
- **HE1–HE7** (efficiency, mechanisms M1–M6 + scale gate): **verifier-offload buys parameters
  (HE1 = the pivot experiment)**; verifier-gated cascade; dense concept input; adapter
  onboarding (builds on E5 PASS); external-store memory offload; scaffolded training; and the
  scale-slope gate.
- **HS1–HS13 + HS-A** (structure/design forks — *don't-guess, test-it*): NSM-pinning vs random
  codebook / Numberbatch; native axiom read-out (Π) vs bolt-on sidecar; NSM-native axiom syntax
  vs `kot-axiom/1`; constraints-out-of-the-vector; grammar-capacity; Lean minting viability;
  external-store vs in-weights; efficiency-at-interface vs dense-I/O; and the "Fable-class
  authoring beats DeepNSM-8B" why-now check.

Every hypothesis carries a stable ID, a falsifiable statement, a decisive experiment, the full
baseline set (including the mandatory kernel-as-text null), a **statistically-framed kill
criterion** (named test + effect-size threshold + α; TOST for any null), scale rungs, and a
**literature-grounded extrapolation envelope** (the model-scale range each result can reasonably
reach, with the cited anchor and direction of bias).

## 2. Tiered kill-tree — cheapest-decisive-first

| Tier | What | Cost | Decides |
|---|---|---|---|
| **0** | Byte/coverage/formalism forks on this box (R0) | **≤$20** | structure forks, coverage gate |
| **1** | **F2 verifier-offload — the pivot** | **≤$80** | HE1/HE2/HC3/HS12 — the make-or-break |
| **2** | E9 correctness, F4 onboarding, E8 SAE | ≤$400 | HC1/HC2/HE4/HC4 |
| **3** | F3 dense-I/O, F6 scaffolding | ≤$400 | HE3/HE6 + sign-level scale trends |
| **4** | F5 store hull-test (double-gated) | ≤$900 | HE5 |
| **5** | **F7/E7 scale study (maintainer-gated)** | **$2–10k** | the *only* tier that licenses scale adjectives / a frontier pitch |

A **decisive NO costs ~$200–700** all-in (Tiers 0–3), inside the cumulative Tiers 0–3 cap of
**$900** (worst-case all-tiers-0–3 spend ~$760). The cheapest decisive spend is the pivot
(Tier 0 + F2, ≤$100 under the caps).

## 3. Global go/no-go decision tree

First match wins → **take-to-frontier-lab** (≥1 mechanism PASS at ≥2 rungs + measured
flat/growing slope over ≥3 rungs + novelty re-search + role-separated re-derivation) · **narrow-and-continue**
(PASS but slope unmeasured — fund exactly the missing rung) · **pivot** (mechanisms text-null-killed
but A6 SAE replicates → interpretability instrument; or HC2 alone passes → assurance product) ·
**kill** (H0-NO → negative-results publication with full statistics). *Every route ends in a paper.*

## 4. Honesty backbone (`02-data-and-reporting.md`) + statistics (`08-stats-and-extrapolation.md`)

- **Pre-registered registry** (`kot-reg/1`): every experiment frozen (hash-pinned) before it runs
  — IVs/DVs, one primary endpoint + one Holm family, all pins (encoder `40e8c8ba…`, corpus,
  model, analysis-script), verbatim kill text + extrapolation envelope, machine-evaluable verdict
  rules.
- **Append-only, hash-chained raw-results log** (`kot-log/1`): raw metrics only — a p-value in a
  run record *fails schema validation*. Derived stats live only in the pinned analysis output.
- **Verdict = pure function** of pre-declared thresholds vs measured values, executed in a grammar
  with no arithmetic so judgement can't hide in it. A PASS is **PASS-PENDING-AUDIT** until a
  role-separated re-derivation confirms it.
- **14 enforceable guardrails** (prereg-before-run, run-vs-audit separation, negatives at equal
  prominence, no post-hoc threshold changes, coverage disclosure, budget halts, scale-language
  license…).
- **Statistics**: effect sizes + CIs (never p alone), Holm/FDR families (incl. a cross-experiment
  Holm family gating the programme-level H0 claim), TOST with pre-declared margins for every null,
  **power computed up front**. **Scale extrapolation** fits ≥3 rungs, selects a functional form,
  quotes a prediction interval, classifies agreement against named published scaling laws (Snell,
  Kaplan/Hoffmann, LCM/CALM, frozen-embedding), and **prohibits ≥70B claims below Tier 5**.

## 5. Operations (`03-operational-dag.md`), resources (`06-resources.md`)

- ~190-node DAG, 1:1 with the registry; every experiment = reg→inputs→mock→run→log→readout→audit→close.
- **Automation boundary**: agent-executable end-to-end *except* 7 human-gate classes (budget caps,
  freeze signature, credentials, ~30–40 annotator-hours, spend approvals, programme decisions,
  external exposure).
- Harness: Modal `jmwright-045` primary (per-second billed, validated), AWS fallback.
- Model ladder (all open-weight, revision-pinned, ungated defaults): SmolLM2 135M/360M/1.7B ·
  Qwen2.5 0.5B/1.5B/3B/7B · Pythia 70M/160M/410M.
- **Timeline**: M0 freeze Jul 22 → M2 pivot (F2) Aug 01 → M5 GNG-2 decision Sep 25 → … → M9
  paper + explainer Jan 30 2027. Early pivot/kill pulls the write-up forward to ~Oct 2026.

## 6. Skills (`04-skills.md`) + agent roles (`05-agent-roles.md`)

- **14 skills**, honesty-enforcing by construction (thin wrappers over pinned tools): `prereg`,
  `run-experiment`, `flop-meter`, `decode-verify`, `run-stats`, `audit-result`, `report-gen`,
  `paper-claims`, `paper-draft`, `explain-back` + supporting. Items 1–8 land before GNG-0.
- **11 agent roles** over Opus/Fable/Haiku, with a machine-enforced separation matrix: run ≠ audit,
  write ≠ grade, produce ≠ record, author ≠ certify, only-Coordinator-commits. ≤5 concurrent
  subagents. Four `.claude/agents/*.md` skeletons ready to commit.

## 7. Publication + explainer (`09-publication-reporting.md`)

- Route-mapped venues (main-track on a PASS; interpretability on the A6 pivot; **TMLR negative-
  results paper on a KILL — a pre-declared success mode**). TMLR is the standing fallback.
- **Every paper claim must resolve to a verdict object**; a banned-spin vocabulary hard-fails for
  non-PASS verdicts; the abstract must state the measured scale range + the 1-OOM cap.
- **Plain-language explainer-back** to the maintainer (what-we-found / what-it-means / what-scale /
  go-no-go), delivered on every route.

## 8. Red-team (`07-redteam.md`) — FIX-THEN-EXECUTE (fixes required before GNG-0)

**Critical (block the affected freezes):**
- **RT-2** — add the *gloss-text self-verify + retry at matched budget* baseline to E9/F2; without
  it an HC1 "PASS" can't distinguish "kernel helps" from "any verification-with-retry helps" (the
  most likely way the flagship dies at frontier review).
- **RT-1** — the decision tree is non-exhaustive: the most probable outcome (no PASS, but H0-NO
  blocked by an INCONCLUSIVE) matches no route. Add a STOP-AND-PUBLISH-UNDECIDED route + a
  replication-buy cap.
- **RT-3** — the **model→checkable-record interface** (how a model's output becomes something the
  kernel can verify) is unspecified, yet the whole correctness track hinges on it. Needs a one-page
  spec + an extraction-failure instrument gate before E9/F2 freeze.

**Major (pre-freeze):** amendment cutoff must move to first raw-data exposure (RT-5); supersession
lineage + 2-revision cap (RT-6); ecological validity — add ≥1 external eval slice + natural-violation
secondary + a coverage *gate* not just disclosure (RT-7); G2 is under-powered as scheduled (RT-4);
kernel authoring cost missing from the metric vector (RT-11); E8-D needs a ground-truth design
(RT-10); relabel agent "independence" + externally timestamp freezes (RT-9/15); anonymization would
break the hash chains — anonymize by overlay (RT-14); budget-cap arithmetic inconsistencies (RT-8);
family-h0 Holm node missing from the DAG (RT-13). **Directive compliance is otherwise clean: no
semantic-web creep, both value theses measured, forks testable.** No redesign needed; recommend M0
slips Jul 15 → Jul 22 to protect quality.

*Status update (pre-freeze): the red-team fixes above have been applied across the plan components
and verified; M0 is now Jul 22.*

## 9. Decisions needed from the maintainer

Consolidated from all components — grouped by when they bite:

**Now (to start Tier 0 / reach GNG-0):**
- Approve the direction + authorize applying the red-team fixes to the frozen text.
- Budget caps (T0 $20 · T1 $80 · T2 $400 · T3 $400 · Tiers 0–3 cumulative $900, worst-case ~$760)
  + set the Modal spend limit to match.
- Annotators for ~30–40 human-hours (yourself + one colleague at $0, or a paid platform ≈$500–900).
- Confirm the **backup Fable account** as the role-separated auditor identity performing
  re-derivations (Tier ≥2 positives + paper review).
- Enable **branch protection** on `jeswr/kernel-of-truth` (closes the log-rewrite risk).
- Two statistics sign-offs: the cross-experiment **F-H0 Holm family** (C-3) and the **≥4/5 seed
  sign-consistency** PASS gate (C-4).

**Later (gated, with the evidence in hand):**
- GATE-T4 spend ≤$900 (~Sep 25, on the GNG-2 dossier).
- GATE-T5 spend $2–10k (~Oct, the only frontier-relevant tier).
- Venue + authorship/AI-disclosure policy (provisional at GNG-2, final at submission).

**Standing:** the 6 stopped EC2 instances still need manual termination (IAM denies me
`ec2:TerminateInstances`); and these plan commits are local-only until push-to-main is authorized.

---

Component index: [01 hypotheses](01-hypotheses-experiments.md) · [02 data/honesty](02-data-and-reporting.md)
· [03 operational DAG](03-operational-dag.md) · [04 skills](04-skills.md) · [05 agent roles](05-agent-roles.md)
· [06 resources](06-resources.md) · [07 red-team](07-redteam.md) · [08 stats+extrapolation](08-stats-and-extrapolation.md)
· [09 publication](09-publication-reporting.md).
