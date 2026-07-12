# UFO-CHECK-0 — does a small host actually USE a UFO checker? (design + prereg doc)

**Status: DESIGN-ONLY, DRAFT registry entry `registry/experiments/ufo-check-0.json` (kot-reg/2).**
The coordinator HOLDS the build-to-freeze pipeline's run step pending the maintainer's
issue-#22 decision (adopt KUFO/1; gold ruling D2; GPU-wave budget ratification Q6 —
arch-synthesis §4). **No feasibility conclusion on CORRECTNESS or EFFICIENCY is stated
or implied anywhere in this document; both remain INCONCLUSIVE-PENDING.** All tags are
provisional. Epistemic tags: [MEASURED] pinned artifact in-repo; [STIPULATED] design
choice made here; [EXTRAPOLATION] expectation to be tested, never a premise;
[ARCHITECTURE-VERDICT] docs/next/arch/ufo-rdf12-expressibility.md.

Label (mandatory, carried on every readout): **ORACLE-DIAGNOSTIC** (ASM-0814 lineage).
Gold is engine-derived; the AU checker is the same engine family; inputs are formal
templated synthetic items. **No natural-input-reach claim is licensed by any outcome.**

Lineage: round-2 architecture synthesis §3 item 1 (the KUFO/1 thin slice's $5–20 GPU
rider); CK-UFO candidate (docs/next/arch/full-ufo-kernel-ck-ufo.md — four-valued
result contract §1.7, gold discipline §3.2, representation-matched null §3.3);
RULES-1 twin engine + A3 verify-retry precedent (poc/rules-1/, frozen record
registry/experiments/rules-1.json); f2b HFLM scorer + seeded retry sampler
(poc/f2b-transfer/runner/f2bt_runner.py, reused read-only); Modal wrapper pattern
(poc/rules-1/modal/modal_rules1.py, poc/modal/modal_f2b.py).

---

## 1. Question and hypotheses

**[STIPULATED] Question.** Given two-situation modal/rigidity items whose gold
disposition is derivable by a bounded UFO-SN3 checker, does a frozen small host
(SmolLM2-135M primary rung; SmolLM2-360M second rung) **use** a UFO checker at the
verify-retry seam — i.e. does checker-gated verify-retry lift the host's exact
three-way disposition accuracy over host-alone, beyond (a) a representation-matched
null checker, (b) a seed-pinned deranged-meta-typing checker, and (c) a
gUFO-taxonomy-only checker?

It does NOT ask whether full UFO improves natural-language parsing, host reasoning in
general, programme-wide efficiency, or anything about the programme theses.

**Hypotheses (falsifiable, registered):**

- **H-U1 (primary, the "uses the checker" claim):** UFO-SN3 checker verify-retry
  (retry budget k=1) lifts SmolLM2-135M exact disposition accuracy on engine-derived
  gold over host-alone: paired-item BCa one-sided 95% LB > 0.
- **H-U2 (content-not-structure):** the AU lift exceeds the representation-matched
  null arm AN: LB(acc(AU) − acc(AN)) > 0 — a lift cannot be attributed to "a checker
  rejected something" over the same materialised representation.
- **H-U3 (content destruction):** the lift collapses under the seed-pinned
  deranged-meta-typing checker AD: recovery UB95 < 0.30 (the f2b/rules-1 bound
  verbatim).
- **H-U4 (distinctive-content contrast, secondary):** the full-UFO checker beats the
  gUFO-taxonomy-only checker: LB(acc(AU) − acc(AG)) > 0 — derived
  disjointness/rigidity semantics, not class labels, carry the value.
- **H-U5 (safety, non-inferiority):** AU does not increase the dangerous-wrong rate
  over A0: one-sided UB95 of the increase < +0.02.
- **H-U6 (mechanism strength, secondary, claim-cap only):** the AU lift exceeds the
  analytic max-trivial retry floor: LB(acc(AU) − floor_max(AU)) > 0 — the host uses
  the rejection REASON, not merely the rejection bit (see §5.3).

**CLAIM CAP (binding):** any positive result is capped at "this host uses THIS
checker's signal on THIS templated item family at this scope" — oracle-diagnostic,
never a thesis conclusion, never a natural-input claim, never a promotion. Promotion
of any UFO-checking claim beyond diagnostic requires the independently-authored,
human-reconciled CK-UFO gold set (arch-synthesis decision D2; CK-UFO §3.2).

---

## 2. Items and generator

**[STIPULATED] Corpus `data/ufo-sn3-items-v0/`** — synthetic, seed-pinned, formal
templated. Generator `poc/ufo-check-0/gen_items.py`, seed string
`ufo-check-0/1|two-situation-modal-rigidity|20260712` (explicit seed per repo
convention; the encoder itself remains seedless — CLAUDE.md).

Every item has exactly **two situations** S1, S2 with: an accessibility fact
(S2 possible-from S1, or absent), existence facts existsAt(x, Si), a small type
inventory with **explicit meta-typing** (kind/subkind/role/phase — first-class
stated facts, never inferred from names; CK-UFO §1.2), per-situation membership
propositions carried as holds/notHolds records (the UFO-SN3 finite-world carrier
[ARCHITECTURE-VERDICT]), optional closedFor scope declarations, and ONE candidate
conclusion. The host answers three-way: ENTAILED / CONTRADICTED / UNDERDETERMINED.

**Four families × 150 scored items = 600 scored** (+ 30 OUT-OF-PROFILE probes,
§4.3), balanced within family to ≈50 E / 50 C / 50 U golds; 300 of the 600 are
**near-miss companions**: each pairs with a base item differing by exactly one
load-bearing fact that flips the gold (CK-UFO §3.2 discipline).

| Family | Load-bearing UFO content | Example gold pattern |
|---|---|---|
| **F-RIG** rigid persistence | rigid membership propagates to accessible situations where the individual exists | holds(S1, x:K), kind(K), existsAt(x,S2), acc(S1,S2) ⊢ **E** for "x is K in S2"; drop existsAt(x,S2) → **U** |
| **F-ANTI** anti-rigid counterworld | role/phase membership needs no propagation; necessity claims need closed scope | candidate "x must be R in every declared situation" with witness notHolds(S2, x:R) ∧ existsAt(x,S2) → **C**; no witness, open scope → **U** |
| **F-DISJ** derived Kind disjointness | unique-ultimate-sortal theorem: distinct Kinds pairwise disjoint with ZERO authored disjointness | holds(S1, x:K1), kind(K1), kind(K2), K1≠K2, candidate "x is K2 in S1" → **C**; make K2 a subkind of K1 → not disjoint → **U/E** per statement |
| **F-SPEC** rigidity subsumption mask | rigid type cannot specialise an anti-rigid type | stated K ⊑ R with kind(K), role(R), candidate membership consequence licensed only through the illegal edge → **C** (validation regime); legal R ⊑ K direction → per closure |

Named scope omissions [STIPULATED]: relators/qua-individuals, identity criteria,
dispositions, events (CK-UFO families 2,4,5,6) are NOT tested — this is the
modal/rigidity rider only. An axioms-as-text arm (rules-1 c6) is NOT run at this
scope (arm budget fixed at five by the synthesis); AN covers representation, not
rule-text — a disclosed limitation any promotion experiment must repair.

**Prompt surface** (identical bytes across ALL arms; canonical deterministic
templates, one fact per line, fixed order): stated facts (situations, accessibility,
existence, meta-types verbalised as "'Student' is a role type" etc., per-situation
memberships incl. explicit negatives), then the candidate claim, then
`Answer with exactly one word: ENTAILED, CONTRADICTED, or UNDERDETERMINED.`
Gold is derivable from the stated facts under §4's closed rule inventory; the rules
themselves never appear in any prompt.

---

## 3. Mechanism — verify-retry, k=1, shared first pass

**[STIPULATED]** rules-1 A3 / f2b form: the host answers; the arm's checker either
accepts or issues a **licensed rejection** (with a one-line proof/violation reason,
never the correct disposition); on rejection the host retries once (k=1) with the
rejection message appended; the retry answer is final.

- **Licensed-rejection contract (four-valued-faithful):** each checker arm has a
  per-item arm-disposition d_arm ∈ {ENTAILED, CONTRADICTED, UNDERDETERMINED,
  OUT-OF-PROFILE} computed offline (§4). The checker rejects an answer **only when
  it holds a proof the answer is wrong**: d=E rejects {C, U}; d=C rejects {E, U};
  **d=U rejects NOTHING** (no proof either way — UNDERDETERMINED is never converted
  into a rejection; CK-UFO §1.7); d=OOP rejects nothing and logs OOP.
- **Why k=1 [STIPULATED]:** the answer space has three values, so any k ≥ 2 with an
  exact-oracle accept table is gameable by pure answer-elimination (a cycling
  automaton reaches gold in ≤ 3 tries regardless of understanding). At k=1 the
  trivial-policy floors are analytic and the "uses the reason, not the bit" contrast
  (H-U6) is well-posed. k > 1 cells are NOT run; if ever run they are
  quarantined-exploratory.
- **Shared first pass:** first-pass decoding is greedy (deterministic) on the
  identical prompt bytes, so it is computed ONCE per (item, host) and shared across
  all five arms — exact pairing by construction and a ~4× generation saving. Seeds
  {0,1,2} govern retry sampling only (f2bt seeded sampler, temperature per its
  pinned defaults).
- **Extraction:** pinned regex over the completion's first answer token; extraction
  failure counts the generation incorrect and feeds the extraction gate (P10
  discipline, Wilson-LB ≥ 0.90).

---

## 4. Gold, the Python twin, and the four-valued contract

### 4.1 Engine

**[STIPULATED]** `poc/ufo-check-0/twin_ufo.py` — a CPU differential-twin extension in
the poc/rules-1 style. It **imports `poc/rules-1/twin_engine.py` read-only at its
pinned sha** (399fcd8d…, the rules-1 frozen pin) for the owl-rl core (subsumption,
domain/range) and adds a CLOSED UFO-SN3 modal inventory (anything else refuses
ERR_RULE_UNIMPLEMENTED; every rule carries a regime tag and a source citation):

| Rule | Content | Regime | Source |
|---|---|---|---|
| U-RIGID | holds(w1, x:K) ∧ kind∨subkind(K) ∧ existsAt(x,w2) ∧ accessible(w1,w2) → holds(w2, x:K) | ufo-modal | arch-synthesis §2 item 1; [ARCHITECTURE-VERDICT] |
| U-ANTI-WIT | necessity candidate over anti-rigid T + witness notHolds(w2, x:T) ∧ existsAt(x,w2) → violation (CONTRADICTED) | ufo-modal | CK-UFO §1.3 |
| U-KIND-DISJ | kind(K1) ∧ kind(K2) ∧ K1≠K2 ∧ neither subkind-related → disjoint(K1,K2) | horn-def | unique-ultimate-sortal [LIT-BACKED: Guizzardi 2005 via arch-synthesis §2 item 2] |
| U-SPEC-MASK | rigid(T1) ∧ T1 ⊑ T2 ∧ antiRigid(T2) → violation | validation | CK-UFO §1.3 |
| U-EXIST | holds(w, x:T) → existsAt(x,w) | ufo-modal | existence propagation, arch-synthesis §2 item 1 |
| U-CLOSED | missing-witness checks fire ONLY inside declared closedFor scopes (stratified) | validation | CK-UFO §4.1 ("no counterworld supplied" ≠ "none exists") |
| U-OOP | candidate quantifies beyond the declared finite situation set, or invokes an unimplemented commitment (identity criteria, mereology, unrestricted modality) → OUT-OF-PROFILE | reference-only guard | CK-UFO §1.7 |

**Four-valued mapping (CK-UFO §1.7 verbatim contract):** ENTAILED iff the candidate
is derivable; CONTRADICTED iff its negation is derivable or a violation fires in a
legitimately closed scope; OUT-OF-PROFILE iff the commitment exceeds the executable
inventory; else UNDERDETERMINED. **Neither UNDERDETERMINED nor OUT-OF-PROFILE is
ever converted into a negative answer or a rejection.** Fail-closed codes:
ERR_RULE_UNIMPLEMENTED, ERR_AXIOM_GRAMMAR, ERR_BUDGET_EXCEEDED, ERR_CONFLICT,
ERR_FIXTURE_SHA. Every disposition carries a why() proof tree with regime-tagged
premises.

### 4.2 Gold and its disclosed circularity

**[STIPULATED]** Gold = the AU (full-inventory) twin disposition. This is
**engine-derived gold**: the same engine family defines the gold AND powers the AU
checker — the benchmark-circularity failure mode both round-2 critiques lead with.
It is answered here **by controls, not by argument**: AD (same rules, deranged
meta-typing) and AN (same representation, no rules) attack it from both directions,
and AG isolates the taxonomy-only share. The residual circularity is exactly why the
record is labelled ORACLE-DIAGNOSTIC and why promotion requires the CK-UFO
independently-reconciled 144–192-case gold set (annotation lane, GPT-5.6
annotator-proxy authoring + human reconciliation — proceeds in parallel, decision
D2; it does not block this record).

### 4.3 Pre-materialisation (the NO-sparq contract)

**[STIPULATED]** `poc/ufo-check-0/materialise.py` runs the twin ONCE on CPU before
any GPU spend and writes `poc/ufo-check-0/inputs/fixtures/`:

- `gold.jsonl` — item_id, family, gold disposition, proof sha;
- `accept-tables.jsonl` — per item × arm ∈ {AG, AU, AD, AN} × answer ∈ {E, C, U}:
  accept | reject + the EXACT rejection message bytes (see §5.2 token parity);
- `floors.jsonl` — per item × arm: analytic expected correctness of the three
  trivial retry policies (§5.3), computed from the accept tables alone;
- `fixtures-sha.json` — double-run determinism proof: materialise.py runs twice,
  both canonical-JSON shas recorded, MUST match (else ERR_FIXTURES_PRECONDITION —
  no GPU spend).

The GPU runner does **zero symbolic work** — checker decisions are byte lookups.
**No sparq code is touched, built, or invoked anywhere on this path** (the engine-only
sparq programme is PR-5, gated separately; arch-synthesis §2). The twin↔sparq
conformance question is deliberately NOT on this record.

### 4.4 Worked examples (build gate: twin must reproduce all four byte-exactly)

1. **F-RIG/E** — facts: situations S1,S2; acc(S1,S2); kind(Person); role(Student);
   holds(S1, bo:Person); existsAt(bo,S1); existsAt(bo,S2). Candidate: "In S2, bo is
   a Person." → U-RIGID ⊢ **ENTAILED** (premises: holds(S1,bo:Person), kind(Person),
   existsAt(bo,S2), acc(S1,S2)). Near-miss companion: delete existsAt(bo,S2) →
   **UNDERDETERMINED**.
2. **F-ANTI/C** — facts as above + holds(S1, bo:Student); notHolds(S2, bo:Student).
   Candidate: "bo is a Student in every declared situation." → U-ANTI-WIT ⊢
   **CONTRADICTED** (witness S2). Companion: delete notHolds(S2, bo:Student), no
   closedFor → **UNDERDETERMINED** (open scope; U-CLOSED does not fire).
3. **F-DISJ/C** — facts: kind(Person); kind(Rock); holds(S1, bo:Person). Candidate:
   "In S1, bo is a Rock." → U-KIND-DISJ ⊢ **CONTRADICTED** (derived disjointness,
   nothing authored). Companion: subkind(Rock, Person) stated instead of
   kind(Rock) → no derived disjointness → **UNDERDETERMINED**.
4. **F-SPEC/C** — facts: kind(Person); role(Student); stated Person ⊑ Student.
   Candidate: "every Person in S1 is thereby a Student in S1 (via the stated
   specialisation)." → U-SPEC-MASK violation ⊢ **CONTRADICTED**. Companion: reverse
   the edge (Student ⊑ Person) → closure-licensed → **ENTAILED**.
5. **OOP probe** — candidate: "bo is a Person in ALL possible situations
   whatsoever." → **OUT-OF-PROFILE** (quantifies beyond the declared finite set);
   checker accepts everything, logs OOP; item excluded from the scored 600.

---

## 5. Arms (five, fixed by the synthesis)

Prompt bytes identical in all arms; arms differ ONLY in checker behaviour.

| Arm | Checker | Purpose |
|---|---|---|
| **A0** no-checker | none (first-pass answer is final) | baseline; headroom gate |
| **AG** gUFO-taxonomy checker | twin restricted to asserted-taxonomy rules only: stated subsumption propagation within a situation + STATED disjointness; NO derived Kind disjointness, NO cross-situation propagation, NO rigidity/witness/scope semantics | what class labels alone buy (the dormant gufo_prior axis, taxonomy.rs:33 lineage) |
| **AU** UFO-SN3 checker | full §4.1 closed inventory, four-valued | the experimental arm |
| **AD** deranged meta-typing | AU's rules over a **seed-pinned Sattolo derangement** (seed 20260712) of the meta-type assignment (every type's kind/role/phase label moved); dispositions re-derived under the derangement | content-destruction control (rules-1 c1 form); coincidence rate with true tables REPORTED |
| **AN** representation-matched null | same materialised proposition/situation/reifier representation; rules = **stated-fact lookup only** (reject E unless candidate literally stated in-situation; reject C unless its notHolds literally stated; accept U always) | the CK-UFO A1 fold-in: "more explicit structure + a rejection channel" without UFO inference (GS-B stated-bytes lineage) |

### 5.2 Token parity

**[STIPULATED]** The only arm-varying surface is the rejection message. AG/AD/AN
rejection messages are padded/templated to the AU message token band: per-arm mean
rejection-message tokens within ±20% of AU at the pinned SmolLM2 tokenizer
(pre-freeze check artifact + run-time gate /gates/token_parity_valid; knull G-3
pattern). AN messages carry no rule content ("REJECTED: your answer conflicts with
the recorded facts about S1 and S2." + neutral padding).

### 5.3 Trivial-policy floors (the elimination confound, made mechanical)

**[STIPULATED]** For each item × arm, from the accept table + the host's ACTUAL
first answer, the runner emits the expected final correctness of three trivial
retry policies: (i) uniform-over-non-rejected-answers; (ii) always-retry-to-U;
(iii) cycle-next in the fixed order E→C→U→E. floor_max = max of the three.
H-U6 tests acc(AU) − floor_max(AU) paired per item. **H-U6 failing is a CLAIM CAP,
not a kill:** the claim degrades verbatim to "the host uses the rejection BIT, not
the reason" — still a registered, reportable answer to the §1 question.

---

## 6. Endpoints, statistics, gates (the pinned analysis plan)

Analysis script: `analysis/ufo_check_0.py` (pinned by sha in the registry entry) —
a pure function over the runner's run-records; paired-item BCa bootstrap B=10000,
PRNG seed 20260712, one-sided α=0.05; Holm over the secondary family
{s1,s2,s3,s4,s5}; Wilson bounds for rate gates. Scored slice = the 600 scored items,
host 135M unless named; the 360M rung reports a SIGN only.

**Primary (exactly one):** `/analysis/primary_lift_lb95` — acc(AU) − acc(A0), exact
three-way disposition correctness vs engine-derived gold, paired by item (shared
first pass makes pairing exact), seed-averaged; PASS requires LB > 0. Smallest
effect of interest: 0.05 absolute [STIPULATED planning margin; resolution: realized
CI width at analysis].

**Holm secondaries:**

- s1 `/analysis/s1_content_over_bit_lb95` — acc(AU) − floor_max(AU) LB > 0 (H-U6;
  claim-cap only, never verdict-bearing);
- s2 `/analysis/s2_vs_null_lb95` — acc(AU) − acc(AN) LB > 0 (H-U2; PASS-necessary);
- s3 `/analysis/s3_deranged_recovery_ub95` — lift(AD)/lift(AU) conservative ratio
  (UB of AD lift over LB of AU lift, rules-1 s1 form) < 0.30 (H-U3; PASS-necessary);
- s4 `/analysis/s4_vs_gufo_lb95` — acc(AU) − acc(AG) LB > 0 (H-U4; claim-cap only:
  failing caps the claim at "checker value not distinctively full-UFO at this
  scope");
- s5 `/analysis/s5_dangerous_wrong_increase_ub95` — dangerous-wrong(AU) −
  dangerous-wrong(A0) UB < +0.02 (H-U5; KILL-bearing).

**Dangerous-wrong [STIPULATED]:** final answer ENTAILED on gold CONTRADICTED, or a
hard answer (E or C) on gold UNDERDETERMINED — the CK-UFO dangerous-false-accept +
illegitimate-closure directions. (On gold-U items no checker ever rejects, so any
AU-arm increase is host-behavioural and must be caught, not assumed away.)

**Instrument gates (any failure ⇒ INSTRUMENT-INVALID, never a hypothesis event):**
headroom acc(A0, 135M) ≤ 0.85; engagement (AU rejection rate on scored items in
[0.02, 0.98] and ≥1 retry observed); extraction Wilson-LB ≥ 0.90 over all
generations; token parity (§5.2); fixture determinism (§4.3 double-run shas match,
verified again in-run).

**Descriptives (never verdict-bearing):** per-family × per-disposition accuracy per
arm; near-miss pair consistency; AD coincidence rate; OOP probe checker-refusal
correctness; 360M sign; per-query cost ledger — tokens in/out, FLOPs formula,
checker-lookup µs, GPU-h, $/query (F0 conventions) — **descriptive only, no
efficiency claim is tested in this record** (efficiency_relevant=false).

**Power [STIPULATED planning bound, never a measurement]:** n=600 paired items,
3-way chance ≈ 0.33; at plausible A0 accuracy 0.35–0.55 the rejected-item mass gives
detectable-lift resolution well below the 0.05 margin; resolution: realized CI width
at analysis (registered as PROPOSED-ASM row 1489).

---

## 7. Kill criteria, verdict mapping, envelope

### 7.1 Kill criteria (verbatim; equal prominence for all outcomes)

- **KILL-U1:** primary LB ≤ 0 ⇒ the host does not use the checker at this scale;
  UFO-checker value at this scope remains oracle-only (the engine answers, the host
  doesn't improve); the surviving KUFO/1 value case for checking routes to the
  engine-only assessment (arch-synthesis §1 item 4), and NO host-integration claim
  survives. Verdict FAIL.
- **KILL-U2:** s5 fails (dangerous-wrong increase UB ≥ +0.02) ⇒ NO-GO regardless of
  accuracy — a checker that buys accuracy by converting abstentions into confident
  errors is disqualifying. Verdict FAIL.
- **KILL-U3 (attribution kills, cap PASS→INCONCLUSIVE):** s2 fails (AU ≤ AN: the
  lift is generic rejection/structure, not UFO content) or s3 fails (deranged
  recovery ≥ 0.30: not content-driven). Primary may be positive; the UFO
  attribution is dead at this scope.
- Claim caps (not kills): s1 fail ⇒ "rejection bit, not reason"; s4 fail ⇒ "not
  distinctively full-UFO beyond taxonomy labels".

### 7.2 Verdict mapping

INSTRUMENT-INVALID if any §6 gate fails; FAIL if KILL-U1 or KILL-U2; PASS iff
primary ∧ s2 ∧ s3 ∧ s5; else INCONCLUSIVE. Nulls get equal prominence.

### 7.3 Pre-freeze skeptic-attack seed list (experiment-designer role, before freeze)

(1) elimination gaming despite k=1 (floors §5.3 correctly maximal?); (2) rejection
messages leaking the gold disposition (audit message templates byte-level);
(3) AD coincidence rate high enough to mute s3 (report + re-derange if > 0.35);
(4) AN reject-everything-E degeneracy making AN actively harmful and s2 trivially
easy (engagement band applies to AN too; disclose AN rejection rate); (5) gold-U
share making headroom artificially low; (6) prompt-order artifacts (fixed canonical
fact order — vary NOTHING; disclose as scope); (7) 135M three-way format compliance
(mock extraction rate before freeze).

### 7.4 Extrapolation envelope (verbatim, binding on ANY outcome)

Claims are scoped to: SmolLM2-135M/360M (two rungs license a SIGN, not a slope);
formal templated two-situation synthetic items from THIS seed-pinned generator;
engine-derived gold from the SAME engine family as the AU checker
(ORACLE-DIAGNOSTIC, ASM-0814 lineage — the eval's construction favours the checker
by design and is HELD FIXED across arms; controls answer attribution, not
diagnosticity); the closed §4.1 rule inventory; retry budget k=1; the four-valued
contract with licensed-rejection discipline; families F-RIG/F-ANTI/F-DISJ/F-SPEC
only — relators, qua-individuals, identity criteria, dispositions, and events are
NOT tested; the axioms-as-text null is NOT run at this scope. NO outcome speaks to
natural-language inputs, externally-authored items, hosts above 360M, engine-side
sparq work, kernel content, or either programme thesis. A PASS feeds the issue-#22
GO decision as ONE input and licenses no thesis conclusion; a FAIL/NULL kills only
the host-uses-checker mechanism at this scope.

---

## 8. Harness spec (the build-worker contract)

**Status: SPEC-ONLY — no harness code exists yet.** A build worker implements this
section verbatim; deviations require a design amendment before freeze.

```
poc/ufo-check-0/
  gen_items.py            # §2 generator → data/ufo-sn3-items-v0/items.jsonl
                          #   (+ meta.json: seed string, counts, balance table)
  twin_ufo.py             # §4.1 engine; imports poc/rules-1/twin_engine.py
                          #   READ-ONLY at pinned sha 399fcd8d… (assert at import,
                          #   ERR_TWIN_PIN on mismatch); poc/rules-1 bytes untouched
  materialise.py          # §4.3 fixtures; --self-test runs §4.4 worked examples
                          #   (byte-exact) + double-run sha proof; CPU, $0
  ufo_check0_runner.py    # GPU runner: HFLM scorer + seeded retry sampler imported
                          #   from poc/f2b-transfer/runner/f2bt_runner.py READ-ONLY
                          #   at pinned sha b62c3a72… (f2b/knull/rules-1 pattern);
                          #   --mock (StubLM, $0 local), --dry-plan (cost plan vs
                          #   caps, $0), --arms, --hosts, --seeds; checkpointed
                          #   per-arm×host×seed (2-shared-core box discipline);
                          #   refuses real mode until the record is FROZEN
                          #   (ERR_RUNNER_ROLE) and fixtures pass ERR_FIXTURES_
                          #   PRECONDITION + ERR_FIXTURE_SHA fail-closed
  modal/modal_ufo_check0.py  # modal_rules1.py pattern VERBATIM: stage bytes,
                          #   in-container staged-manifest assert (ERR_STAGING_
                          #   MISMATCH), --print-manifest ($0, fills
                          #   pins.harness_manifest), image from poc/modal/
                          #   requirements-image.txt UNCHANGED (no new deps),
                          #   kot-hf-cache volume, results → results-incoming/,
                          #   never auto-committed
  inputs/                 # manifest.json + fixtures/ (committed pre-freeze)
  results-incoming/
```

Run-record row (one per item × arm × host × seed): `{item_id, family, gold, host,
arm, seed, first_answer, rejected, retried, final_answer, correct, dangerous_wrong,
extracted_ok, floor_uniform, floor_always_u, floor_cycle, tokens_in, tokens_out,
rejection_msg_tokens, flops_formula, checker_us}` + a run-level sidecar
`{fixtures_sha_run1, fixtures_sha_run2, model_revisions, extraction_counts}`.
Output feeds `analysis/ufo_check_0.py` unchanged.

Mock discipline: `--mock` must go green end-to-end (StubLM, fixtures, analysis
script producing all pinned output fields) BEFORE freeze; the mock's StubLM token
counts are a disclosed stipulated artifact (knull precedent) — token-parity
pre-freeze evidence is the pinned-tokenizer artifact, not the mock.

Estimated build effort: 2–4 agent-days [EXTRAPOLATION] (twin_ufo ≈ 250 LOC over the
rules-1 twin; generator ≈ 200 LOC; runner is f2bt reuse + lookup loop).

---

## 9. Cost and budget

**[EXTRAPOLATION, planning only]** Generations: shared greedy first pass 630 × 2
hosts = 1,260 + retries ≤ 600 × 4 checker arms × 3 seeds × 2 hosts ≈ 14,400 ⇒
~16k short generations (prompts ~200–350 tokens, completions ≤ 48). Against the
nsk1/rules-1 datum (32,958 rows ≈ 0.457 A10G-h ≈ $0.50 [MEASURED lineage,
PROPOSED-ASM-1134]) this is well under 1 GPU-h of pure decode; the registered band
**2–6 GPU-h / $5–20 (a10g)** covers model loads, the 360M rung, checkpoint overhead,
and a 3× planning margin. Caps: **usd_cap $20, gpu_hours_cap 6, wall-clock 12 h** —
within the standing authorization per arch-synthesis §4 Q6 (spend-and-report-after
once ratified). Worst case strands ≤ $20 + 2–4 agent-days.

---

## 10. Roles, freeze + run steps, Modal account

Frozen-design discipline (run ≠ audit): this DRAFT is authored by the
**experiment-designer role**; it never runs, grades, or audits this record.

**Coordinator steps (in order):**

1. **HOLD-GATE:** obtain the maintainer's issue-#22 decision (adopt KUFO/1; gold
   ruling D2 — engine-derived gold now under the oracle-diagnostic label; budget
   ratification Q6). Steps 2–5 (agent-time, ~$0) MAY proceed while held; **step 6
   (GPU) MUST NOT start before the decision.**
2. Spawn a build worker on §8; gate on: materialise.py --self-test green (§4.4
   byte-exact + double-run sha), runner --mock green through the analysis script,
   items committed to data/ufo-sn3-items-v0/ and pinned via
   `tools/registry/corpus-pin.py ufo-sn3-items-v0`.
3. Pre-freeze skeptic attack (§7.3 list as the seed; experiment-designer role).
4. Resolve the PINNED-AT-INPUTS placeholders in the DRAFT record: corpus digest;
   artifact_hashes (twin_ufo.py, fixtures-sha.json, accept-tables sha, generator);
   pins.model_revisions (135M carried verbatim from the f2b frozen record
   12fd25f7…; **360M = HuggingFaceTB/SmolLM2-360M-Instruct revision pinned at
   freeze**); pins.harness_manifest from `modal_ufo_check0.py --print-manifest`;
   re-verify prereg_doc/analysis_plan_ref/analysis_script shas after any edit.
   Register ASM rows 1480..1493 (§11) centrally — **this design bead wrote nothing
   to registry/assumptions.jsonl**.
5. `prereg-freeze.py --experiment ufo-check-0 --agent-id coordinator-1` (dry-run
   first); post the frozen sha to the coordination issue.
6. **RUN (experiment-runner role, post-#22 GO only):** `--dry-plan` vs caps → green
   `--mock` on Modal → single a10g full run. **Modal account: lane M1** per the
   one-lane-per-account stipulation (arch-synthesis §3 lists UFO-CHECK-0 first;
   the prior M1 occupant in the standing lane map, the knull ablation, has moved
   into the rules-1/knull-v2 lanes per §3 items 2–3) — **coordinator confirms the
   free lane at launch; the assignment, not the one-lane rule, is the adjustable
   part.** Standing Modal hygiene (bd memory): nohup+setsid for long runs;
   `modal app stop ap-<id>` after killing ANY attached client.
7. verdict-gen (mechanical) + analyst readout (full metric vector, coverage
   disclosure, verbatim kill criteria, envelope) + cross-vendor Codex audit;
   anything off the pinned script is quarantined exploratory.

---

## 11. Proposed ASM rows (PROPOSED-ASM rows 1480..1493; block 1480..1499 reserved)

Emitted for central registration by the coordinator at freeze (step 4). This bead
wrote nothing to `registry/assumptions.jsonl`. Owner strings use the pseudonymous
role convention.

The 14 rows are emitted VERBATIM in `poc/ufo-check-0/asm-proposed-1480-1493.json`
(the rules-1 `asm-1190-1197.json` convention — kept OUT of docs/ so the claims-check
unknown-id lint stays green until the coordinator registers them at freeze). Row map:
1480 item generator/scope · 1481 engine-derived gold + oracle-diagnostic label +
promotion gate (D2) · 1482 closed UFO-SN3 inventory + four-valued contract ·
1483 pre-materialisation, lookup-only GPU path, NO sparq · 1484 five arms, shared
first pass, token parity · 1485 Sattolo deranged meta-typing · 1486 representation-
matched null · 1487 k=1 licensed rejections + trivial-policy floors · 1488
dangerous-wrong definition + 0.02 margin · 1489 statistics plan · 1490 cost band
[EXTRAPOLATION] · 1491 host/scorer pins · 1492 roles + issue-#22 hold + lane M1 ·
1493 scope omissions + envelope binding.

**Self-check gate:** no feasibility conclusion stated or implied; all tags
provisional; ORACLE-DIAGNOSTIC label + envelope verbatim; no @handle/account
strings; assumptions confined to the reserved 1480..1499 block and NOT written to
assumptions.jsonl; no frozen object touched; NO sparq changes on this path; the GPU
run is explicitly held pending issue #22.
