# SUBJECTIVE STEERING ANALYSIS — Programme-3, post-batch-2 milestone (2026-07-11)

**[OPINION throughout unless tagged otherwise. This never overrides a mechanical verdict or a frozen envelope; both theses remain INCONCLUSIVE-PENDING and nothing below moves them.]**

---

## 1. Well vs poorly — and the code-vertical bet

**Going well:**

- **The round-1 steering was partly obeyed, and it worked.** Since the "stop building scaffolding, start measuring" note, four cheap measurements actually landed: f2b-transfer stage-1 (A=0.9610, LB 0.9395, kill-d not fired [MEASURED: f2b-transfer-stage1.md §0]), DECONF-A1 grid (11,848/11,848 [MEASURED: deconf-a1.md §0]), the D3 upper-sieve census (κ=0.6665 [MEASURED: coverage-census.md]), and the NTP probe (traces partially replayable, 464/600 / 438/855 file-granular [MEASURED: NTP-GATE.md §0]). That's the best measurement-per-review-cycle ratio the programme has had.
- **Stage-1 is a real, earned positive.** The programme's first ground-truth-independent contact went well — and the tie-break moved A *down* (0.978→0.961), which is what a conservative instrument looks like when it's working. The counterfactual worst case (0.889, LB 0.859) means no re-litigation of the unresolved 27 can undo it. This is the correctness thesis's first non-self-referential datum, on exactly one axis (gold authority, not input).
- **Kill discipline held under temptation twice.** The coverage census could have quietly kept the mapper 0/1550 as a domain kill; instead it reported that the kill-sound lane *dissolved* the cheap kill (D3 own-axis 0.8825 ≫ 0.05). DECONF-A1 could have been billed as the complete certificate; it was rescoped to grid-only with the replay/init-order gap stated first. No kill manufactured, no win manufactured.

**Going poorly:**

- **The NL wall — the thing round-1 said should be THE main experiment — has received zero new measurements.** Everything that landed is attribution, census, or instrument work. a5-nl 41.6% + S2 fired and l3a-parse 47.6% are still the last words on the wall. NLB-0/G2 sits behind a review-acceptance chain; G0 (the only authorized code-vertical work) appears designed but not yet run. The steering note's own diagnosis — "building the courtroom before running the cheap forensic tests" — has partially recurred as three same-day design revisions (CODEVERT rev-2, DECONF rev-B, NTP-GATE rev-2).
- **The code-vertical-primary bet (issue #8): structurally sound, showing real strain.** Three strains, in order of severity: (i) honest repricing destroyed the "cheap decisive" story — no rung is both cheap and decisive [STIPULATED: ASM-1039], and the one decisive rung costs 400–900 annotator-hours / $8k–25k [ESTIMATED: ASM-1038] of the programme's *measured binding resource*; (ii) coverage on Python repos is completely unmeasured while every coverage number the programme owns is brutal (g8 0/1000, m0b 0.3542) — "Python is friendlier" is pure EXTRAPOLATION (ASM-1008), and G1's κ_q^indep ≥ 0.5 floor could kill the whole vertical for ~70–130 hours; (iii) **a full CODEVERT win is kernel-free** [STIPULATED: ASM-1000] — the bet's best-case outcome vindicates an architecture family, not the kernel. The bet is still right (it's the only tractable NL-boundary attack), but issue #8 should be re-read with clear eyes: the vertical can save Programme-3's *architecture* thesis while leaving the kernel-content question exactly where it is.

---

## 2. Promising vs dead-end; the f2b stage-2 EV question

**Most promising, in order:**

1. **f2b-transfer stage-2 — run it, and the EV question is nearly a category error.** The honest answer to "is it worth the GPU spend": the spend is ~$1 point estimate, $15 cap [STIPULATED: design.md §9], and no human step remains. The *information* EV is genuinely modest — with A=0.961, external and membership gold nearly coincide on the eval prefix, so a large lift_mem≫lift_ext gap is arithmetically unlikely [EXTRAPOLATION, and the frozen design forbids treating that as a result] — but that cuts the other way too: at ~$1 you buy either the programme's first ground-truth-independent end-task PASS or a sharp scoped kill (a/b/c), by frozen rules, on the *only* line whose human constraint is fully discharged. Cheapest verdict-moving compute in the registry. The slice-narrowness objection (kernel-covered/kernel-rendered/≤1.7B/k=4) is real but is an argument about what a PASS *licenses*, not about whether to spend $1. Do not let the narrowness argument delay a trivially cheap registered adjudication.
2. **The attribution pair: DECONF §3.1(b)+(c) completion, then Stage B / knull-v2.** This is where the actual verdict-relevant uncertainty now lives. A1's grid result sharpened the deflationary reading to near-executable form: at grid scope the F2 lift survives as "verify-retry against an aligned deterministic answer key, with the kernel as one way to author such a key" [MEASURED at grid scope + STIPULATED reading: deconf-a1.md §4]. Even a stage-2 PASS will be worth little to either thesis until Δ_align and authored-content value are measured. Completing the certificate is cheap CPU; it should be finished before its conclusions get informally consumed anyway.
3. **G0 + G1 on the code vertical.** G0 is ~$0 and authorized; G1 at 70–130 annotator-hours is the cheapest possible kill of the entire vertical *before* any parser exists. This is the correct next annotation spend (see §4).

**Dead-end or de-facto dead:**

- **The general-index W1 — now demoted by measurement, and I'd say functionally dead.** The census showed the cheap kill isn't available (completing the sound lane *raised* the ceiling to 0.986), the suite isn't even enumerated, and the only kill-sound tightening lane is a human-annotated oracle census [MEASURED/COMPUTED: coverage-census.md]. Spending the binding resource (human hours) to *maybe kill* an index nobody intends to win anymore is the worst annotation trade available. Recommend: freeze the general index as unfalsified-and-unpursued; put zero further hours into the oracle census; the vertical fork is the W1 target, full stop.
- **NTP consumers beyond what the gate can clear.** The probe answered the question: no continuation interface exists, traces are file-granular-partial, and the gate can serve lookup-derivation traces and formal-field continuations — *not* proof states or search transitions [MEASURED: NTP-GATE §0/§3]. B1+B3 is a bounded build; everything downstream (mask decoding, trace distillation for P6) stays frozen until the gate passes, and the proof-state consumers should be quietly retired from planning documents.
- **Already-dormant lines stay dormant** (H-DD, deep-internal placements, broad GNN fusion). Nothing landed to revive them.

---

## 3. Single highest-value next experiment; what to drop

**Highest value: finish the f2b-transfer line — the mechanical tail (d-adj-t pin → record append → verdict-gen) plus the single ~$1 stage-2 GPU run.** It's licensed, frozen, human-unblocked, and by the frozen verdict rules it's the only near-term event that can put a registered PASS or a registered kill on the efficiency thesis's decisive experiment. Everything else is preparation; this is adjudication. Run G0 (~$0, already authorized) concurrently — it converts the largest block of [UNMEASURED] in two documents into numbers.

**Drop / deprioritise:**
- The oracle coverage census (human hours into a dead index).
- **Any further design/review cycles on CODEVERT, DECONF, NTP until their authorized measurements land.** The CASK-PY/1 episode is the tell: an entire external proposal round produced ~85% re-derivation of the existing design plus two small rules [OPINION, per codevert-arch-critique.md §0]. Design has converged; marginal review cycles are now consuming the scarce resource to produce convergence certificates.
- The g9/GATE-H authoring line stays paused (correctly) — but see §4: it can't stay paused forever and still support a verdict.

---

## 4. Biggest risk to a defensible verdict on BOTH theses

**The risk: asymmetric adjudication by cost structure.** Every *deflationary* leg is cheap and keeps landing (DECONF ~$0, census ~$0, shuffled controls ~free, stage-2 ~$1), while every *affirmative decisive* leg on both theses is human-annotation-gated: g2 Π-soundness and g3 necessity (correctness), GATE-H (authoring), G1/G4 gold (the vertical), knull-v2's plain-arm quality ruling. The capstone itself says the binding constraint is annotation, not compute [MEASURED: feasibility-synthesis §6]. On the current trajectory the programme will accumulate ever-more-precise measured deflation against never-run affirmative legs, and the "defensible feasibility verdict" degrades into FAIL-by-attrition — defensible-sounding, but not actually adjudicated. A verdict reached because only one side's evidence was affordable is not defensible.

**What most reduces it:** a pre-registered *annotation portfolio* — one document, maintainer-ratified, that ranks every human-gated decisive leg by verdict-movement-per-annotator-hour and commits a bounded budget to the top of the list. My ranking: (1) CODEVERT G1 census (70–130h — can kill the vertical before any other vertical spend), (2) g2 Π-soundness human gold (the correctness thesis's decisive leg; no amount of architecture work substitutes for it), (3) knull-v2 plain-arm ruling (unblocks the authored-content attribution that decides what any f2b result is worth). Everything else waits. Without this, the sequencing will keep being decided by what's free, which is exactly the bias.

**Secondary risk, worth naming plainly: single-vendor epistemics.** Judge-2 and judge-3 are one model family (disclosed, caveat 2), *and* GPT-5.6 is simultaneously the sole external review gate for every design *and* the author of the rival architecture proposal. The critique bills CASK-PY/1's convergence as "evidence the rev-2 corrections are stable under independent derivation" — but rev-2's corrections *came from a GPT-5.6 review*, so the same model re-deriving them is substantially self-agreement, not independence [OPINION]. Cheap mitigation: route one review per major design, and any future judge fallback, through a third vendor family. The stage-1 result survives its same-family caveat because the human anchors every resolved label; the design-review pipeline has no such anchor.

---

## 5. What the programme may be fooling itself about

1. **Interpretive volume as progress.** The epistemic hygiene is genuinely the best I've seen in this class of work — and it has a failure mode: DECONF-A1, a result the design itself called "nearly true by construction" [STIPULATED: DECONF §9.1], received a multi-thousand-word two-revision interpretation. The tagging discipline is load-bearing; the *length* is not. Some fraction of the governance apparatus is motion that feels like rigor.
2. **The stage-1 glow.** 96.1% blind endorsement of templated definitional QA about 108 everyday concepts is what competent dictionary-grade content *should* score; it removes a confound (huge) but is weak evidence of distinctive value (the documents say this correctly — the risk is in how the result gets *summarized* in future momentum decisions, where "first strong POSITIVE" will outlive its envelope).
3. **The unfunded affirmative path** (§4 above) — the deepest one. The programme behaves as if the affirmative legs will eventually run while never scheduling their cost against a budget. Kill-ladders that make kills cheap and wins expensive are honest science and, under a fixed budget, a one-way ratchet.
4. **The kernel is quietly becoming optional to its own programme.** Compose the measured record: the F2 lift survives at grid scope as an aligned-answer-key property [MEASURED: deconf-a1.md §4]; the a5 world is structural-not-NSM (ASM-0007); a full CODEVERT win is kernel-free (ASM-1000); the NSM semantics core (g2/g3) is unrun. Every live, funded line either doesn't consume NSM semantics or is agnostic to them. Nobody has decided this — it's emerging from cost gradients. If it's the right call, it should be *made*, not drifted into; if it's wrong, only g2/g3/knull-v2 spending reverses it.
5. **Coverage growth economics remain unpriced.** Everything rides on coverage 0.3542 of one incomplete instance over 108 concepts, and A-F0 (mint cost) is untouched. "Coverage can be grown" has still never been given a $/concept or hours/concept number — GPT-5.6 flagged this in round-1 and it is still true.

**Bottom line [OPINION]:** the programme is healthier than at round-1 — it measured things, and one of them came back positive. Spend the $1, finish the certificate, run G0, and then force the one decision the cost structure is currently making by default: which affirmative human-gated leg gets funded. That decision, not any experiment, is the current bottleneck to a defensible verdict on both theses.