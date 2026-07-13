# nsk1 B′ Stage-0 interpretation — fork recommendation (internal-write family)

- **Author:** Fable interpretation role (owner id: designer-11), 2026-07-13.
- **Task:** beads `kernel-of-truth-bh1n` — interpret the nsk1 B′ Stage-0 output (both runs) and
  issue the registered fork recommendation for the training-free internal-write family.
- **Registered outcomes (exactly three):** PASS (redesign at R3) | KILL (retire family) |
  INCONCLUSIVE (maintainer fork).
- **Scope guard:** This is a B′-scoped interpretation and fork recommendation ONLY. It authors no
  programme-level feasibility conclusion; the FINAL feasibility synthesis (d8p8) owns that. This
  role wrote no registry entry and took no git action (coordinator-owned).
- **Evidentiary grade of every number below:** MEASURED-exploratory — both runs are pre-freeze
  fork diagnostics, every row `phase:"exploratory"` (quarantined, uncitable in any verdict; nsk1
  stays DRAFT). The fork *decision procedure* itself is confirmatory: the thresholds were frozen
  in the specs before each run and are applied verbatim here.

---

## 1. BLUF

**Fork recommendation: PASS — redesign the internal-write family at R3.**

The single most decisive number: at grid cell (ℓh, ℓt) = (16, 16), **keyed accuracy 0.850 with
Bonferroni-corrected one-sided Wilson lower bound 0.775 ≥ the frozen 0.70 floor** (chance = 0.5
exactly by construction), with paired real > coin p = 4.1×10⁻¹³ and paired real > role
p = 9.1×10⁻¹¹ — all three conjuncts of the pre-registered PASS-KEYED rule, on a run whose
instrument-validity gates all passed [MEASURED: `poc/nsk1/out/bprime2/bprime2_summary.json`
sha256 `0ee800f7f7d1aec0aa245986aa9a27a15017ebc33d5780a9cb4104da366f76f1`, `verdict.cell_reports`].
A second cell, (12, 16), independently clears the same rule (0.810, LB 0.730, p = 1.4×10⁻¹⁰ /
8.9×10⁻⁷). This is a real, control-guarded, FWER-controlled signal that a residual-stream write
delivers item-specific content the host reads out — exactly what the PASS branch was registered
to mean: worth a hardened re-run/redesign, not a verdict.

---

## 2. What B′ measured (mechanics + custody)

**The question.** Stage-0 of the nsk1 "internal-write" family (flagship line
neurosym-kernel-internals) asks the cheap-kill question: does a usable internal
(residual-stream) delivery channel exist at all at the most favourable measured host, before any
money is spent on the full internal-vs-external campaign? Host: R3 = SmolLM2-1.7B-Instruct,
pinned commit `31b70e2e869a7173562077fd711b654946d38674` (identical in both runs); surface: the
CLUTRR entity form (form 2) over the 958-item covered set (items/headroom sha256s pinned in both
specs and echoed in both summaries); Modal 1×A10G, fp32, greedy, chat template.

**Run 1 — B′** (spec `docs/next/nsk1-bprime-stage0-spec.md`, ASM-0040..0043; outputs
`poc/nsk1/out/bprime/`, rows sha256 `f45b12e0…22ea4`, summary sha256 `539040e9…f1ef7c`,
verified against the run-log handoff). Probe: replacement transplant of the item's OWN later-layer
hidden state into an earlier layer at the final prompt position (P1, gate-bearing, 35 cells) plus
an oracle bridge-carrier transplant (P2, reported-only, 36 cells); readout = any-cell exact-gold
rescue of text-only failures; control = seed-pinned derangement (shuffled donor). 32,958
generations, |F| = |Swept| = 200 (full failure set), no abort, no cap trip, 0.457 GPU-h /
~USD 0.50.

**Run 1 outcome: INSTRUMENT-INVALID by its own pre-registered clause.** The shuffled-source
control rescued MORE than the real arm (0.525 vs 0.400; discordant pairs c = 29 vs b = 4), and
`rescue_p1_ctrl` Wilson-LB = 0.467 ≥ 0.15 tripped §5 rule 1's control-rescues-at-floor clause
(the ASM-0041 revisit clause) [MEASURED: bprime_summary.json `verdict`]. Mechanism, relevant to
what follows: the any-cell exact-gold readout scored perturbation *frequency*, not content — and
the replacement transplant was destructive (mean correct-item breakage ≈ 98.5% per cell,
`heatmap_breakage_c100`) and content-indifferent (P2 real 0.040 vs deranged 0.050). **Run 1 is an
adequacy stop on the instrument, not a merits verdict on the family** — it licenses statements
about its own operationalization only.

**Run 2 — B″** (spec `docs/next/nsk1-bprime2-spec.md`, ASM-0200..0204; commissioned by the
maintainer's REDESIGN choice at the post-B′ fork, `registry/assessments/nsk1-bprime.json`;
outputs `poc/nsk1/out/bprime2/`, rows sha256 `dadabaae…0eeba`, summary sha256 `0ee800f7…f76f1`).
It repaired exactly the two measured failure modes: (i) readout → source-keyed
counterfactual-pair discrimination on a teacher-forced logprob margin, with a coin-assigned
deranged control whose expected success is ≤ 0.5 **by arithmetic** (a content-free perturbation
of any magnitude cannot pass it in expectation), plus a role-consistent deranged control as the
mechanism separator; (ii) operator → additive norm-matched contrastive injection
(h ← h + s·α·‖h‖·Δ̂v) instead of the measured-destructive replacement transplant. 9 cells,
Bonferroni-corrected any-cell PASS / all-cells KILL, floor 0.70 on keyed accuracy. 14,914 rows,
0.206 GPU-h / ~USD 0.23, 752.7 s wall.

**Run 2 custody/validity: clean.** No abort; not partial; all 9 cells completed;
commit pin matched; reproducibility gate 958/958 against B′'s text-only vector (threshold ≥
910); `headroom_ok` true (text-only acc 0.7912 ∈ [0.05, 0.85], 958 ≥ 900 scored); coin control
≤ chance at every cell (max coin Wilson-LB at z = 2.7730 was 0.423 < 0.5 — the
instrument-invalid trigger never fired); zero ties in every arm at every cell; α* = 1.0 selected
by the mechanical ladder (name-collapse 0.0156 ≤ 0.10); every disc/baseline row stores both raw
candidate logprobs, so the gate is recomputable offline without GPU — and the prior interpretive
record (`registry/assessments/nsk1-bprime2.json`) reports an offline recount from the rows with
EXACT agreement at all 9 cells (corroborating custody; this recommendation does not depend on
it). One runner operational instantiation was disclosed (the reported-only disc-c100 deranged
arm reused the pinned Sattolo operator over C100 order): it touches no §5 gate quantity, C100
and Swept are disjoint by construction, and it is confirmed benign for this interpretation.

**No adequacy or host-validity gate failure caps run 2.** The only adequacy failure in the B′
lineage is run 1's own instrument, which run 2 was pre-registered to replace.

---

## 3. The pre-registered decision rules, verbatim, and the observed statistics

### 3.1 Run 1 (B′ spec §5 — quoted)

> "1. INSTRUMENT-INVALID iff NOT `headroom_ok`, or any ABORT fired, or `rescue_p1_ctrl`
> Wilson-LB ≥ 0.15 (control-rescues-at-floor ⇒ the metric is uninterpretable on this form, per
> the ASM-0041 revisit clause). 2. PASS iff Wilson-LB95(`rescue_p1`) ≥ 0.15 AND
> `excess_pass`(P1)… 3. KILL-NO-LATENT-HEADROOM iff Wilson-UB95(`rescue_p1`) < 0.15.
> 4. Anything else: INCONCLUSIVE…"

| Clause | Frozen threshold | Observed (bprime_summary.json) | Result |
|---|---|---|---|
| headroom_ok | acc(text-only) ∈ [0.05, 0.85], ≥ 900 scored | 0.7912, n = 958 | met |
| ABORT | none fired | aborted = false | met |
| control-rescue trip | Wilson-LB(rescue_p1_ctrl) ≥ 0.15 ⇒ INVALID | rate 0.525, **LB 0.467** | **TRIPPED** |
| (PASS clause, moot) | LB(rescue_p1) ≥ 0.15 AND excess_pass | LB 0.345 but b = 4 < c = 29, p ≈ 1.0 | would fail anyway |
| (KILL clause, moot) | UB(rescue_p1) < 0.15 | UB 0.458 | would not fire |

**Run-1 gate label: INSTRUMENT-INVALID** (mechanical verdict in the run log). Neither PASS nor
KILL is licensed from run 1.

### 3.2 Run 2 (B″ spec §5 — quoted)

> "1. **INSTRUMENT-INVALID** iff any ABORT fired…, or NOT `headroom_ok`, or at ANY completed
> cell keyacc_coin's one-sided Wilson LB at z = 2.7730 exceeds 0.5…
> 2. **PASS-KEYED** iff at some completed cell: Wilson-LB(keyacc_real, z=2.5427) ≥ 0.70 AND
> paired real > coin (p < 0.05) AND paired real > role (p < 0.05)…
> 3. **CHANNEL-ROLE-ONLY** iff no cell meets rule 2 but…
> 4. **KILL-NO-USABLE-CHANNEL** iff all 9 cells completed AND at every cell
> Wilson-UB95(keyacc_real, z=1.6449) < 0.70. 5. Anything else: **INCONCLUSIVE**…"

Instrument gates (rule 1): aborted false; repro 958/958 ≥ 910; headroom_ok true; coin-LB > 0.5
at no cell (max 0.423). **All met — instrument VALID.**

Rule 2, per qualifying cell (floor 0.70; all from `verdict.cell_reports`):

| Cell (ℓh, ℓt) | keyacc_real | Wilson-LB (z = 2.5427) vs 0.70 | paired real>coin p (<0.05) | paired real>role p (<0.05) | Rule 2 |
|---|---|---|---|---|---|
| **(12, 16)** | 0.810 | **0.730 ≥ 0.70** ✓ | 1.35×10⁻¹⁰ ✓ | 8.87×10⁻⁷ ✓ | **PASS** |
| **(16, 16)** | 0.850 | **0.775 ≥ 0.70** ✓ | 4.11×10⁻¹³ ✓ | 9.06×10⁻¹¹ ✓ | **PASS** |
| (20, 16) | 0.605 | 0.515 ✗ | 0.031 | 0.413 | fail |
| other 6 cells (ℓt ∈ {8, 12}) | 0.42–0.50 | 0.34–0.41 ✗ | ≥ 0.30 | ≥ 0.41 | fail |

Coin control across all 9 cells: 0.43–0.52 (consistent with the arithmetic ≤ 0.5 bound). Role
control at the pass cells: 0.595 / 0.580 — far below real, and the real>role conjunct is what
makes the signal item-keyed rather than generic-direction. Effect sizes at the pass cells:
mean margin shift m(+)−m(−) ≈ +2.82 / +2.80 (real) vs +0.59 / +0.81 (role) vs ≈ 0 (coin).
KILL check (rule 4): fails — the two pass cells have UB95 0.851 / 0.887 ≥ 0.70.

**Run-2 gate label: PASS-KEYED** (mechanical verdict in the run log; `pass_cell` records
(12, 16), the first qualifying cell in sweep order; (16, 16) also qualifies in full).

### 3.3 The run-1 vs run-2 "discrepancy"

There is no evidential contradiction. Run 1's readout (any-cell exact-gold rescue under a
wholesale replacement transplant) was structurally passable by content-free perturbation, and
its own frozen rule declared it uninterpretable when the control demonstrated exactly that.
Run 2 is the pre-registered successor (commissioned at the recorded maintainer fork) whose
control cannot exceed chance in expectation and whose operator does not destroy the state it
writes into. The two runs agree wherever they overlap: same host commit, text-only accuracy
0.7912 reproduced 958/958, and both show the replacement transplant to be useless (run 1
directly; run 2 by retiring it on run 1's measurement). Under the first valid instrument the
family has produced, the channel keys cleanly at 2 of 9 cells — and only at injection depth
ℓt = 16 (2/3 of L = 24) with harvest ℓh ∈ {12, 16}, i.e. the signal comes with a measured layer
topology rather than a diffuse everywhere-effect (a pattern much harder to produce by artifact).

---

## 4. Fork recommendation, with epistemic status

**PASS — redesign the internal-write family at R3.**

**Epistemic status: confirmatory *as a fork decision*, exploratory *as evidence*.** Precisely:
the recommendation is the verbatim application of B″'s frozen §5/§8 rule (thresholds quoted
above, none moved, none invented) to a run that passed every one of its own instrument-validity
gates — the decision procedure is confirmatory and pre-registered, and this is NOT an
adequacy-limited call: the adequacy stop was run 1, and its registered remedy (the
control-unpassable successor) was executed and passed. At the same time, every underlying number
is MEASURED-exploratory (pre-freeze, `phase:"exploratory"`, quarantined), so the PASS licenses
exactly what the registered PASS branch says — *a real signal worth a hardened re-run/redesign* —
and nothing of verdict grade.

Why not the other two registered outcomes:

- **Not KILL.** KILL requires no viable signal; run 2's own kill rule (all-cells UB95 < 0.70)
  demonstrably does not fire, and the pass-cell evidence is strong under FWER ≤ 0.05 with both
  controls beaten at p ≤ 8.9×10⁻⁷. Retiring the family now would contradict the frozen rule.
- **Not INCONCLUSIVE.** INCONCLUSIVE is registered for evidence that licenses neither branch —
  ambiguous rules, unmet adequacy gates, or bounds straddling the floor. None of that obtains:
  the B″ rule is unambiguous, its gates are met, and two cells clear the corrected floor
  outright. Defaulting to INCONCLUSIVE here would be over-conservatism that re-narrates a
  pre-registered PASS, which the §8 "post-B″ paths" section exists to prevent. (Had run 1 stood
  alone, INCONCLUSIVE/maintainer-fork would have been the honest call — and that is in fact the
  path the programme already took, producing run 2.)

Conservatism checks against over-reading, all acknowledged and none fork-blocking: the gate
readout is a teacher-forced logprob margin, not free generation; the generation secondary was
spec-fixed at the pivot cell (16, 12), which the sweep measured as dead, so keyed free-generation
rescue at the two pass cells is unmeasured *in these runs*; keying was measured only at α = 1.0;
single derangement seed; one host, one form, n = 200. These bound what PASS means (below) and
define what the redesign must harden (rescue-in-generation at the pass cells, an α ladder below
1.0, additional derangement seeds), but they do not convert a clean pre-registered pass into an
adequacy stop. Downstream context, cited for completeness and carrying **no weight in this
B′-scoped decision** (out of this task's evidence scope): a Stage-1 free-generation probe has
since run under the PASS path and read out mechanically INCONCLUSIVE
(`registry/assessments/nsk1-stage1.json`); interpreting it is its own task, and under the
registered outcome set here it belongs to the redesign's risk register, not to this fork.

No new assumptions are registered by this interpretation; it cites existing ones only
(ASM-0040..0043, ASM-0200..0204, and the B″ assessment's ASM-0340/0341 scope/ratification
records). The one forward-looking sentence above about what a redesign "must harden" is design
guidance, not a premise — nothing in the PASS chain rests on it.

---

## 5. What this does and does NOT license for the CORRECTNESS-thesis feasibility synthesis

**Licenses (MEASURED-exploratory, scope exactly as stated):**

- A **channel-existence positive**: at R3 (SmolLM2-1.7B-Instruct, pinned commit), a
  single-position additive norm-matched contrastive residual write at the final prompt token
  delivers *item-specific* content (which of two counterfactual names was injected) that the
  host's forward computation reads out at keyed accuracy 0.81–0.85 (chance 0.5) at 2 of 9 grid
  cells (ℓt = 16, ℓh ∈ {12, 16}), beating an arithmetic-chance coin control and a
  role-consistent control, FWER ≤ 0.05. The internal-write delivery cell of the synthesis's
  delivery topology moves EMPTY → POSITIVE-WITH-SCOPE, exploratory grade.
- The **instrument fact**: the coin-XOR keyed readout is a validated, cheap (~USD 0.23) Stage-0
  instrument class; B′'s confound (perturbation frequency scoring as content) had no path to
  keyed success and produced none.
- The **fork fact**: the internal-write family proceeds to redesign at R3 under the
  pre-registered PASS path (both corpus contacts disclosed verbatim at any future freeze, per
  the ASM-0203 clause).

**Does NOT license (and the synthesis must not cite it as):**

- **Any correctness/accuracy improvement claim.** No statement of the form "internal steering
  fixes answers" or "improves correctness on any task" — the gate is a margin discrimination;
  free-generation rescue at the pass cells is unmeasured in these runs, and the write measurably
  breaks correct generations at α = 1.0 (C100 breakage 48/200 and 47/200 at the pass cells,
  reported-only). Readable ≠ safe ≠ integrated.
- **Any internal-vs-external superiority claim.** The nsk1 primary endpoint
  (acc(internal) − acc(external-text)) was never run; nsk1 has no frozen record, no results-log,
  no verdict object. The text channel's measured harm (G2d) and the engine-external f2b positive
  are both untouched by B′/B″.
- **Any verdict-grade citation.** Every row is quarantined exploratory data; the programme's
  verdict-grade bottom line (zero audited end-task wins over the kernel-as-text null) is
  unchanged by this PASS.
- **Any breadth or scale claim.** One host, one commit, one task form (two-candidate CLUTRR
  entity), one operator at one position, α = 1.0 only, n = 200, single derangement seed, 2 of 9
  cells. Every widening — other hosts, R3+ scale statements, other forms, α < 1.0, grounding
  integration, latent-timing rescuability (ASM-0042 explicitly unresolved per the spec's own
  interpretation boundary) — is EXTRAPOLATION (load_bearing: false; resolution path = the
  redesigned record's Stage-1/campaign measurements), and must be tagged as such if the
  synthesis mentions it at all.

---

*Self-check: fork = PASS ∈ {PASS, KILL, INCONCLUSIVE}; both decision rules quoted verbatim from
the frozen specs with no thresholds invented or moved; epistemic status labelled (confirmatory
fork procedure over MEASURED-exploratory evidence; not adequacy-limited); no new ASM registered;
no registry/*.jsonl written; no git action taken; no programme-level feasibility conclusion
authored; no GitHub handles or account names in this file.*
