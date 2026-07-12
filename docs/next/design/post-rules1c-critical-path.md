# Post-rules-1-c critical path (planning doc)

**Role: Fable planning/design agent, 2026-07-12. This document states NO
feasibility conclusion on either thesis; mechanical verdicts belong to the
pinned analyses + `tools/registry/verdict-gen.py`, and the feasibility
verdict is the maintainer's.** Epistemic tags: [MEASURED] = read from
committed/landed bytes; [MECHANICAL-PENDING] = determined by frozen rules but
not yet executed by the owning role; [PREDICTED] = my extrapolation, could be
wrong; [STIPULATED] = a plan choice; [DESIGN-OPEN] = a decision this plan
deliberately does not make.

## 1. State of the board (verified against the tree, this tick)

1. **rules-1-c is FROZEN** (`registry/experiments/rules-1-c.json`,
   `frozen_sha256 09b246dc…`) and its 4-way host-lift campaign has
   **already LANDED, not merely launched**: all four slices in
   `poc/rules-1/results-incoming/20260712-142704-rules1b-parallel/` carry
   `RUNNER_EXIT rc=0`, 13,470 rows total, full 3-seed grid for
   A1/A3/A5/A7/c1. [MEASURED]
2. Descriptive row aggregate (planning read only — NOT the verdict):
   entailed accuracy A1 0.7028, A3 0.5315, c1 0.5315, A5 0.9441, A7 1.0000.
   A3 and c1 are correctness-**identical on all 2574 item×seed cells**, and
   **every A3 row has `attempts = 1`** — the verify-retry channel never
   rejected once. [MEASURED]
3. `analysis/rules_1c.py:186` defines `engagement_valid := any A3 row with
   attempts > 1`; the frozen verdict rules place `/gates/engagement_valid`
   inside the INSTRUMENT-INVALID conjunction. On these rows the mechanical
   verdict therefore resolves **INSTRUMENT-INVALID** (engagement gate false),
   not FAIL/KILL-b — the entity-form acceptance ground (range/gender only;
   functional-uniqueness dropped as gold-leaking) is vacuous at the 2-option
   surface. [PREDICTED from MEASURED rows + the frozen rule; the owning role
   must still run merge + pinned analysis + verdict-gen]
4. **knull-hostlift** (`rules-1-knull-hostlift.json`, DRAFT) has a hard
   ACTIVATION gate: if the parent analysis does not carry
   `/analysis/primary_pass true`, "this record must never be frozen or run …
   a run anyway resolves INSTRUMENT-INVALID and licenses NOTHING". Under
   either predicted parent branch (INSTRUMENT-INVALID or negative lift) that
   condition fails. Its in-flight entity-form propagation build is therefore
   at risk of being moot. [MEASURED gate text; PREDICTED mootness]
5. **RULES-2** is DRAFT; verdict on its frame inheritance in §2. **DDC**
   ddc0/ddc1 are DRAFT ($5/$60 caps), independent of the rules lane.
   **g2-import-v2** is FROZEN, judge campaign blocked on the codex quota
   (external gate). **Scale track** (`poc/scale`) and sparq PRs are
   unconditional background lanes per maintainer direction. [MEASURED]

## 2. RULES-2 frame propagation — verdict: **YES, it inherits the defect, and it cannot currently run at all**

RULES-2's entire prompt surface — training and eval — is the rules-1-B
relation-word host-frame that rules-1-c diagnosed as form-dead for unaided
hosts (`docs/next/analysis/rules1b-form-misattribution.md` §2: gold top-1 in
1/72 R3 probes, 0/30 at R1; same model entity-form 11/12). Evidence:

| Locus | Evidence | Consequence |
|---|---|---|
| B4 import pin | `poc/rules-2/inputs/rules2-manifest.json` `pins.rules1RunnerPySha256 = 1f423ac0…` (rules-1-b bytes); on-disk `poc/rules-1/rules1_runner.py` is now `91d780f3…` (rules-1-c) | `verify_pins_pre_import` (`rules2_runner.py:146-154`) fails ERR_PIN — **fail-closed, no run possible** [MEASURED] |
| Frame contract | `rules2_runner.py:236-244` asserts frame equality with `poc/rules-1/inputs/rules1-manifest.json`, whose frames are now entity-form (`task_prefix` "…exactly one name", `answer_cue` `'the {rel} of {a_name} is'`) vs rules-2's relation-word `'{b_name} is {a_name}'s'` + `{menu}` header | second fail-closed break, ERR_FRAME_DRIFT [MEASURED] |
| Own eval/train surface | `rules2_runner.py:293-325` (question `How is A related to B?`, 23-word menu + refusal, relation-word infill cue), used for ALL arms at train and eval | B0/B5 are unaided hosts on the measured-dead form: B0 ≈ 0 (form-dead, not chance) inflates the primary B2−B0 with form-rescue; B5 (1.7B) reads ~0 where the entity form measures 0.94 — the big-model comparator becomes a form artefact [MEASURED form data; PREDICTED arm readings] |
| gap23 / s3′ | `rules2_runner.py:434-459, 896-908` score the "rules-1-b A1-verbatim" 23-option surface; the s3′ conditional requires "RULES-1-B A3 lift LB > 0" and `modal_rules2.py:231-240` gates launch on `registry/verdicts/rules-1-b.json` | rules-1-b was superseded pre-GPU and will never have a verdict file — **the gap leg and the launch gate are unsatisfiable as written** [MEASURED] |

**So: repointing to the rules-1-c ENTITY-FORM bytes (as knull is doing) is
necessary before RULES-2 can produce valid host numbers — but with one new
caveat this tick: rules-1-c's own A3 acceptance ground just measured vacuous
(§1.2-1.3). The rework must repoint B4 to an instrument-valid successor of
A3, or drop B4/gap23.** [MEASURED + DESIGN-OPEN]

### Change set (REWORK-3; rules-2 is DRAFT so this is a rework + first freeze, not a thaw)

Mechanical repins: (a) `rules1RunnerPySha256` → the instrument-valid
successor bytes; (b) registry record references rules-1-b → successor;
(c) `modal_rules2.py` sequencing gate → `registry/verdicts/rules-1-c.json`
(or successor) with the branch semantics re-registered (ASM-1420 correction).

Substantive rebuild (forces **re-mock and re-freeze — yes**):
1. Frames → entity form at train AND eval (`parse_cue_names`/`render_cue`
   rewritten for `Who is the <rel> of <base>?`; per-item 2-option anti-echo
   name decode + trained refusal ⇒ 3-option decode; no menu enumeration).
2. `materialise_closure.py` re-renders families 1/2/3 as entity-form QA
   (NAME targets) → regenerate `data/rules2-train`, `b1-upsample`,
   `c1shuf-map` → new kot-corpus-hashes.
3. c1p derangement re-derivation: at 2 candidate names a "derangement" is a
   forced flip (anti-correlated, not shuffled) — s1′ recovery must be
   re-operationalised. [DESIGN-OPEN — nontrivial]
4. c8 gate re-run on the new bytes (fresh-name S-out recovery should stay 0,
   but the 0.10 ceiling must be re-argued against chance 0.5) + c4 floors,
   G3 headroom threshold, SESOI band, and KILL-d arithmetic re-derived for
   chance 0.5 (rules-1-c precedent: lift headroom bounded ≈0.46).
5. New shortcut-audit obligation: on the entity form the gold NAME is
   in-context; a trained host could learn "pick the non-bridge name". The
   rework design must argue (or gate) against this — B1/c1p only partially
   cover it. [DESIGN-OPEN — must go through the GPT-5.6 review gate]
6. B4/gap23 fate: keep (repointed to a repaired A3) or drop (B5-entity as
   the sole efficiency comparator, s3′ struck). Depends on the rules-1-d
   decision in §3. [DESIGN-OPEN]
7. Re-mock (monolithic + sharded parity), new staged-bytes manifest sha,
   dry-plan both tiers, ASM block corrections, GPT-5.6 review, coordinator
   freeze. Budget shape unchanged (~$14 worst R1 tier). [STIPULATED]

## 3. Critical path to a defensible verdict on both theses

The serial chain this tick is: **rules-1-c mechanical readout → (branch) →
one instrument-valid host-integration experiment**. Everything else
parallelises.

```
NOW ($0, parallel)                    GATED
─ merge slices → rules_1c.py →  ──►  branch:
  verdict-gen (mechanical, Opus)       IV (predicted): rules-1-d repair design
─ Fable interpretation of landed             OR declare inference-time slot
  rows + dual-model subjective read          unresolved; maintainer issue
─ PAUSE knull-hostlift build           FAIL: knull moot; rules-2 GPU =
─ RULES-2 REWORK-3 build ($0)                maintainer re-auth, s3′ struck
─ DDC: ddc0 freeze + launch ($5)  ──► ddc1 ($60, gated on ddc0 admission)
─ scale track, sparq PRs (background)
─ g2-import-v2 judge (gated: codex quota; reviews first on quota return)
```

**CORRECTNESS thesis** — components: engine-level correctness is already
MEASURED (certificate 858/858 vs third-party gold, C_dec(entailed)=0.0,
carried by the frozen chain); host-integration is the open component and its
instrument just failed (predicted). Fewest-experiments completion: **one**
instrument-valid host-integration experiment — either rules-1-d (repaired
verification ground with teeth at the 2-option surface) or rules-2-rework as
the replacement slot (train-time internalisation does not require the host
to cooperate with an inference-time verifier, which is exactly the measured
failure mode) — **plus its knull ablation analog** for the kernel-specificity
cap (ASM-1138/1438). Minimum: 1 GPU experiment (~$10-14) + 1 cheap ablation
(~$4). g2-import-v2 adds kernel-growth correctness but is not on the minimal
path. [STIPULATED plan; PREDICTED branch]

**EFFICIENCY thesis** — components: (a) verifier-offload: rules-1-c s3
(135M+engine vs 1.7B, sign-only) is unevaluable under an INSTRUMENT-INVALID
verdict, so this leg re-lands only with the repaired host-integration
experiment; (b) train-time offload (k=4→k=1, engine removed at deployment):
rules-2 rework, sequencing-gated; (c) compression: **DDC is the only
immediately executable efficiency leg and is gated on nothing external —
prioritise ddc0 freeze+launch now**, ddc1 on its admission gate. Minimum:
ddc0 + ddc1, plus whichever of (a)/(b) rides the correctness-side GPU run's
efficiency ledger for free. [STIPULATED]

What genuinely parallelises: readout, interpretation, REWORK-3 build, DDC
lane, scale/sparq, g2-import-v2 (own quota gate). What is genuinely serial:
readout → host-integration decision → (knull fate, rules-2 launch-gate
re-registration, B4 fate) → the one GPU experiment → its knull analog →
Fable interpretation → maintainer verdict synthesis.

## 4. Claim caps (what each track will and will NOT license)

- **rules-1-c (landed)**: if INSTRUMENT-INVALID, it licenses nothing about
  either thesis; it licenses only the instrument finding (vacuous acceptance
  ground) and the host-validity result that the ENTITY form is engageable
  (A5 0.94, A7 1.00, A1 0.70 — descriptive). Even under PASS-shaped rows it
  could never license kernel-specific value (ASM-1138, needs knull), NL
  robustness (l3a wall), or a scale slope (sign only). The A7=1.00 render-only
  read is a rendering-competence datum, never an inference claim.
- **knull-hostlift**: resolves ONLY the host-level wording of the
  kernel-specificity cap, conditional on a parent host lift existing; "one
  comparator licenses NO universal" (its own text). Never an efficiency claim.
- **rules-2 (post-rework)**: at most "engine-materialised entailments are
  internalisable by a small host" (ASM-1438) — never kernel-specific value
  pending the knull-closure analog (issue #6); efficiency ledger is a price
  table with no direction presumed; scoped to LoRA-at-pinned-HPs, this
  kinship vertical, closed inventory, gold-parse prompts, depth ≤4.
- **DDC**: ddc0 licenses only the admission of kernel-aligned directions
  (gate for ddc1's A2 arm); ddc1 at most "kernel-guided direction choice
  beats magnitude/random at matched sparsity on SmolLM2-135M/360M BASE,
  public benchmarks" — sign not slope, no correctness claim, training-free
  regime only.
- **g2-import-v2**: instrument repair; licenses judge-measurement validity
  for import quality, nothing about host reasoning or efficiency.
- **scale track**: infrastructure feasibility only; no hypothesis verdict.
- Programme-wide: no extrapolation across model families, forms, or
  verticals; every affirmative host claim carries its chance floor and the
  form it was measured on.

## 5. Coordinator next actions (in order)

1. **Merge + mechanical readout of rules-1-c** (`merge_rules1b_slices.py` →
   `analysis/rules_1c.py` → verdict-gen → `registry/verdicts/rules-1-c.json`).
   $0, owning role: experiment-runner. Everything branches on this.
2. **Pause the knull-hostlift propagation build now** (one message):
   activation gate makes it unfreezable/unrunnable unless the parent carries
   `primary_pass true`. Cheap to resume if the readout surprises.
3. **Commission Fable interpretation** of the landed rows (the A3≡c1,
   attempts=1, A3<A1 signature: vacuous ground + why A3's attempt-0 surface
   underperforms A1's) + the dual-model subjective read (Fable + GPT-5.6)
   per standing governance. This drives decision 4.
4. **Host-integration slot decision** (Fable design → GPT-5.6 review →
   maintainer ISSUE, per maintainer-decisions-as-issues): rules-1-d repair
   (a non-gold-leaking acceptance ground with teeth at 2 options — e.g.
   k-option enlargement or a structural ground) vs shifting the slot's
   weight to rules-2. Maintainer-gated. Also fixes B4/gap23 fate (§2.6) and
   the re-registration of rules-2's sequencing gate (ASM-1420) and, under a
   FAIL branch, rules-2's "re-auth with s3′ struck" clause.
5. **Launch the DDC lane**: freeze ddc0 ($5 cap; launch pre-authorized) and
   run it; ddc1 on its admission gate. This is the efficiency thesis's
   unblocked leg and should not wait on the rules lane.
6. **Commission RULES-2 REWORK-3** (§2 change set) as a $0 build now, with
   the §2.3/2.5 design-opens assigned to a Fable design agent under the
   5-rule design-agent governance + GPT-5.6 review gate; hold at DRAFT until
   (4) resolves the gate/B4 questions.
7. **g2-import-v2 judge campaign** on codex-quota return; on quota return,
   run small review-gate jobs (items 4, 6) before the bulk judge campaign.
8. Background: scale track, sparq PRs (unconditional), retro-noting that
   rules-2's pinned green-mock and staged-manifest sha are stale against the
   current tree (they break fail-closed; no silent hazard, but the freeze
   artifacts must be regenerated in REWORK-3).

Maintainer-gated items in this plan: action 4 (slot decision + gate
re-registration + any KILL-b re-authorization); the knull fork question
(issue #6) if the knull-closure analog is pursued for rules-2. Everything
else sits inside standing authorizations (compute pre-auth, DDC sign-off,
sparq pre-auth).
