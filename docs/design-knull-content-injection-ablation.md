# knull — K-NULL ablation with the content-injection map FIRST

- **Line id:** `knull-content-injection-ablation` (feasibility-synthesis §5 row 3 / §3d;
  GPT-5.6 review G1 / backlog row N1; sibling of the human f2b-transfer path — either one
  settles attribution of the f2b lift).
- **Status:** DRAFT design + green mock + **pre-freeze gates G-1..G-5 satisfied
  (2026-07-10; evidence in §6.2/§6.5) — FREEZE-READY**: registry record
  `registry/experiments/knull.json` (DRAFT) awaits coordinator
  `prereg-freeze.py`. **NOT frozen. No GPU spent.** No frozen record, verdict, or
  engine file is touched by this line.
- **Author:** Fable experiment-designer role (`kern/fable-designer`), 2026-07-10.
- **Owner type:** Fable-design (this spec); the run is **GPU-gated** (maintainer sign-off,
  $0–250 envelope; exact ask in §6.3).
- **Artifacts owned by this line:** this doc, `poc/knull/**` (builder, stores, items,
  runner, linter, G-3 checker), `analysis/knull.py` (the pinned SAP),
  `registry/experiments/knull.json`. Nothing else.
- **Dedup verification (hard rule 1):** re-checked before design. `registry/ideas.jsonl`
  (47 ideas, last-line-wins): no K-NULL / content-injection / opaque-ID / conventional-store
  idea exists. `registry/experiments/*.json` (32 records): no ablation of the f2b verifier's
  store semantics exists — the near neighbours are `truthstyle-2x2` (surface-style
  adjudication probe, different question), `f2b-errors` (failure taxonomy), `g1`
  (random-atom/Numberbatch nulls — rides F4's endpoint, explicitly cannot rescue the f2b
  license, per SYNTHESIS G1), and `f2b-transfer` (gold-label independence, the sibling).
  `poc/gpt56-review/SYNTHESIS.md` N1 marks K-NULL **NEW**. → **No duplication; this is the
  first design artifact on this line.**

## 0. What this experiment decides, in one paragraph

The programme's only positive end-task result — SmolLM2-135M + kernel-verify-retry beats
SmolLM2-1.7B-alone by +0.1507 absolute (one-sided 95% BCa LB +0.1053), audit-CONFIRMED
[MEASURED: registry/verdicts/f2b-replicate.json] — is currently licensed only as
**correct-alignment-specific**, not kernel-content-specific: the f2b shuffled-derangement
control destroys record↔item *alignment*, not NSM *content*, so any aligned deterministic
answer store might produce the same lift and die under the same derangement
[feasibility-synthesis §2b; poc/gpt56-review/SYNTHESIS.md G1]. K-NULL re-runs the frozen
verify-retry mechanism with the record store's CONTENT swapped — same alignment, same
retry topology, same accept machinery, matched budgets — for a plain-typed non-NSM store
and a semantically empty opaque store. TOST-equivalence of the kernel arm's absolute lift
with the best aligned non-NSM arm's absolute lift ⇒ the +0.1507 is a **generic
aligned-deterministic-answer-key + retry effect**; kernel superiority beyond the margin ⇒
**kernel content carries real weight** at this scope. Before any arm could be designed, the
content-injection map (§1) had to exist: without it, ablation arms collapse into no-ops
(two of the four requested arms turn out to be exactly that — see §1.4).

---

## 1. THE CONTENT-INJECTION MAP (deliverable 1 — normative for the arm design)

Every point where kernel-derived bytes (any byte causally downstream of
`data/kernel-v0/concepts/*.json` or `data/molecules-v0/molecules/*.json` content) touch
(a) the model or (b) the accept decision, across the **frozen f2b pipeline**.

### 1.1 Pins (the map is a statement about these exact bytes)

| Object | Path | sha256 |
|---|---|---|
| Frozen f2b record | `registry/experiments/f2b-replicate.json` | frozen_sha256 `21d401777d2b11bca98b0528a58ebb23e774e4d7e4bee5434a746be76a66771d` |
| The pipeline code | `poc/f2b/runner/f2b_runner.py` | `b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666` (the staged-bytes manifest pinned at freeze is `pins.harness_manifest` `cffd61049bd6f6a08adf1dbe6ee3a2aa7dd3d032c630de10060edfbca5431d9c`) |
| Prompt frames + FLOP accounting | `poc/f2b/inputs/f2b-manifest.json` | `da1fe9dddd9cbddc13143a7f7931ae3f0ced2548df8e36042244ee043fcb61f9` |
| Item generator | `data/d-qa-r/build-dqar.py` | `d4fc3a0fc9b56fd0bf740937bd89bd9b67951976dc8b76e266a1b77b0de5b1eb` |
| Item corpus | `data/d-qa-r` | kot-corpus-hash `0d548bf18ac78f9d7b2abb6686c567f0930acd494c5ca03cee49806c4996ec5e` |
| Record stores | `data/kernel-v0`, `data/molecules-v0` | `8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809`, `69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4` |

Line references below are to `f2b_runner.py` (sha above) and `build-dqar.py` (sha above).

### 1.2 Model-facing injection points (kernel bytes that reach the LM)

- **I-1 — ITEM SURFACES (authoring-time; the dominant channel; ARM-CONSTANT in f2b).**
  Every d-qa-r item's text is rendered from record glosses at build time:
  def-match options — the correct option is the canonical gloss **verbatim**, distractors
  are other covered concepts' glosses (`build-dqar.py::def_match_item`, L215–234);
  term-match questions embed the concept's own gloss (L237–256); claim-true claims are
  verbatim gloss segments (L264–281); claim-false claims are donor-concept gloss segments
  (L284–311). The gloss is `rec["gloss"]` (kernel-v0) or `render_plain(rec["groundingNote"])`
  (molecules-v0) — L146–170. In f2b these bytes reach the model **identically in every
  arm** (the items are shared), so f2b could not and did not vary them.
- **I-2 — kernel-as-text context block** (kernel-as-text arm ONLY): gloss docs rendered as
  `"- term: text"` lines inside the prompt (`f2b_runner.py::build_prompt` L577–590;
  `cell_text` L1193–1201).
- **I-3 — gloss-self-verify frame** (gloss-self-verify arm ONLY): `self_verify_frame`
  interpolates term + gloss + question + answer into a yes/no check prompt
  (`run_self_verify_retry` L712–744).
- **I-NOT-A — retry messages: THERE ARE NONE.** The verify-retry loop is a **silent
  resample**: rejection changes only the attempt index, which changes only the sampling
  seed (greedy at attempt 0, seeded multinomial over the SAME option logprobs at
  attempt > 0 — `HFLM.choose` L554–567; loop `run_verify_retry` L654–676). No verifier
  feedback, no record byte, not even a "wrong, try again" token reaches the model. The
  only model-facing signal of the verifier's existence is *how many times sampling
  repeats*.
- **I-NOT-B — vectors/ASTs/hashes: ZERO bytes anywhere.** The verifier reads only
  `{gloss | render_plain(groundingNote), label}` from each record
  (`KernelVerifier._load` L257–275); the item generator uses hash-seeded index picks and
  token-set Jaccard — it never imports the encoder; prompts contain no vector-derived
  content. Executable proof M-V in §1.4.

### 1.3 Accept-decision-facing injection points (kernel bytes that reach the accept test)

- **A-1 — canonical record text, as an opaque string.** def-match accept:
  `norm_text(chosen option text) == norm_text(record gloss)` (`check` L287–307;
  `norm_text` = whitespace-collapse + strip trailing "." + lowercase, L239–241).
- **A-2 — the label→record map.** term-match accept: the record of the CHOSEN label's
  gloss must equal the definition embedded in the question
  (`check` L296–299; `shown_definition` L282–285; `extract_record` fills
  `rec["definition"]` from the item, L392–409 + `verify_answer` L646–649).
- **A-3 — claim segmentation.** claim accept:
  `(norm(claim) ∈ segments(gloss)) == (verdict == "yes")` (L300–303; `segments` splits on
  `[.;]`, ≥15 chars, no quotes, deduped — L230–236).
- **A-4 — record rendering.** `render_plain` strips `{urn:...|surface}` markup and `[m]`
  markers (L224–227) — the single transformation between record bytes and the accept
  string.
- **A-5 — the store-bytes ledger** (metric-facing, not decision-facing): unique canonical
  record file bytes enter the memory component of V (`run_cells` L1076–1080).

### 1.4 What the map forces on the ablation design (the two no-op traps)

- **D-1.** In the winning arm (kernel-verify-retry), kernel bytes reach the MODEL only
  via I-1 (item authoring — arm-constant in f2b) and reach the DECISION only via A-1..A-4,
  **always as opaque strings under normalized string identity/membership**. The accept
  test never parses NSM structure, never touches an explication AST, never touches a
  vector. Mechanically, the f2b verifier is an aligned deterministic answer table whose
  values happen to be NSM-shaped strings.
- **D-2 (trap 1 — the trivially-identical conventional arm).** A "conventional typed
  store" holding the SAME canonical strings under a different schema produces a **bitwise
  identical accept function** (A-1..A-3 read only the string). A meaningful ablation must
  change the STORED CONTENT — and therefore, through I-1, the item surfaces authored from
  it — while holding alignment, template family, distractor/donor coordinates, option-slot
  layout, retry topology, and budgets fixed. Arms are stores + their induced surfaces,
  never stores alone.
- **D-3 (trap 2 — the vector-free arm is a no-op, proven, $0).** Requested arm
  "vector-free variant" is **MAP-RESOLVED**: stripping every non-gloss field
  (explication, partialExplication, axioms, notes, references, ...) from all 108 records
  and re-running the verifier over every item × every candidate answer yields
  **3456/3456 bitwise-identical (extract, decidable, consistent) decisions**
  (`poc/knull/runner/knull_runner.py::map_check_vector_free`, run in the mock:
  `map-check.json`).
  DECISION: the vector-free arm is settled by the map at $0 and is not run on GPU; the f2b lift was never attributable to kernel vectors because no vector byte is in the seam [MEASURED: poc/knull mock map-check.json, 3456/3456 identical decisions]. (This also discharges GPT-5.6's "canonical AST/record-ID verifier with vectors removed" arm.)
- **D-4 (what K-NULL can and cannot decide).** Gold in every arm is DEFINED by the arm's
  own store (the oracle-favourable construction) — deliberately, because that holds the
  leakage structure FIXED while only content semantics varies. K-NULL therefore
  attributes the lift *within* the oracle-favourable design; it can never certify
  gold-label independence. Verbatim, the standing caveat this design inherits and does
  NOT remove: *on the D-QA slice the verifier's accept test is string-equality to the
  same canonical record that DEFINED the gold answer, so its measured lift is inflated by
  the eval's construction.* That question belongs to f2b-transfer (human judge-1,
  in flight) — the sibling line.

---

## 2. Claim and hypotheses (deliverable 2)

### 2.1 What is at stake

PREMISE: the f2b lift is real on fresh covered items in denominator-free form — +0.1507 absolute vs 1.7B-alone (LB95 +0.1053), at cost_ratio_vs_R3 = 0.103, audit CONFIRMED [MEASURED: registry/verdicts/f2b-replicate.json].

PREMISE: the f2b derangement control cannot discriminate NSM content from correct record↔item alignment — the adopted licence is "correct-alignment-specific" [MEASURED: registry/assessments/f2b-replicate.json does_not_license; adopted in docs/next/feasibility-synthesis.md §2b].

PREMISE: no experiment that could de-confound the attribution has read out; the llmproxy A₁ₚ=0.95 explicitly is not that experiment [MEASURED: registry/assessments/f2b-replicate.json; STIPULATED: ASM-0022 weak-proxy status].

PREMISE: coverage disclosure, verbatim and binding on every claim below — kernel-expressibility coverage 0.3542 at rung molecules-v0, MEASURED by m0b on one incomplete kernel-v0 instance, NOT general coverage [MEASURED: registry/verdicts/m0b.json].

If the lift is generic (aligned answer key + retry), the CORRECTNESS/semantics pitch for
the F2 line dies at this scope while the narrowed EFFICIENCY reading survives (a 135M
model plus an authored deterministic answer key beating 1.7B-alone at ~10% cost is still
an offload result — the open question becomes authoring cost, per SYNTHESIS G1's
consolation). If the kernel arm is superior beyond the margin, NSM-shaped canonical
content measurably earns its place in the store — the first content-attribution evidence
in the programme.

### 2.2 Hypotheses (falsifiable)

- **H-KN1 (equivalence — the deflationary reading):** the absolute verify-retry lift is
  store-content-generic: |lift(kernel) − lift(best aligned non-NSM arm)| < 0.05, TOST.
- **H-KN2 (superiority — the content reading):** lift(kernel) − lift(best aligned
  non-NSM arm) > 0.05, one-sided. (The inverse, kernel-INFERIOR beyond margin, is also a
  registered outcome: NSM surface is a net cost at matched alignment — deflationary a
  fortiori.)
- **H-KN3 (bridge to f2b-replicate):** on the regenerated kernel-arm surfaces the
  mechanism reproduces its signature — verify-retry lift over R1-alone with one-sided
  95% LB > +0.05, and shuffled-derangement recovery below 0.30 (the f2b bound, verbatim).

Per the standing one-primary law (docs/kernel-design-directives.md; P8): the TOST in
§3.4 is the ONLY primary endpoint; H-KN3's components enter as an instrument gate + Holm
secondaries, never as co-primaries.

### 2.3 Registered forks (design-space uncertainties, never silently decided)

- **F-KN-A — plain-store authoring source.** Options: (i) maintainer/human-authored
  plain-dictionary definitions; (ii) LLM-drafted then linter-gated + human-spot-checked;
  (iii) adapted from an existing open dictionary (licence + coverage risk).
  Why uncertain: authoring cost vs style-purity trade-off; (ii) risks LLM-idiom leakage
  correlated with the host model's priors. Deciding experiment: none needed for the
  choice itself — a pre-freeze gate (§6.2) requires whichever source passes the store
  linter (length band, LC1, segmentability, uniqueness) + a 10-item blind style
  spot-check. Kill: if no source passes the linter within budget, the plain arm falls
  back to opaque-only (weaker but still decisive against the pure-alignment reading).
  **RESOLVED 2026-07-10 → option (ii).**
  - DECISION: the plain store is authored under option (ii) — 108 dictionary-register
    definitions LLM-drafted by this designer role, committed with full disclosure in
    `poc/knull/inputs/plain-authored.json`, and the G-1 linter passes every check
    (D-1, L-1..L-5, R-1..R-4; non-NSM register ratio min 0.333 vs canonical-gloss max
    0.069 at threshold 0.25) [MEASURED: `python3 poc/knull/lint_plain_store.py
    --report` over committed store sha256
    df4a17cff6c6da70ddb19c1ef2f4d25b5868ac352318162e8e68f9982848cf58].
  - The drafting model family (Claude/Fable) differs from the SmolLM2 host family, so
    attack-9's same-family idiom-leakage channel does not apply in its strong form;
    the residual style-familiarity axis stays a stipulation until truthstyle-2x2
    reads out — an ASM for this is REPORTED for registration at freeze (§6.4), not
    silently assumed.
  - The 10-item blind style spot-check file is prepared at
    `poc/knull/inputs/plain-spotcheck.json` (deterministic sample; answer key
    separated) — a maintainer sign-off step, not a designer step.
- **F-KN-B — opaque arm difficulty.** Options: keep opaque as a co-primary candidate
  comparator (current) vs demote to descriptive pole. Why uncertain: nonce surfaces may
  push R1-alone accuracy outside the ±0.15 difficulty band (mock cannot tell — stub is
  arm-blind). Decided BY the pre-declared gate at analysis time (§3.5), not by a person.
- **F-KN-C — TOST margin 0.05 vs 0.075.** Why uncertain: power depends on the unmeasured
  cross-arm item correlation (§3.6). Deciding rule: margin 0.05 is frozen unless the
  pre-freeze tokenizer/FLOPs re-check forces n below 900 per arm, in which case 0.075 is
  used and stated. Kill: neither margin powered ⇒ do not freeze; re-design.
- **F-KN-D — claim-type mix.** The fresh claim-true surface pool over the 108 concepts is
  nearly exhausted by d-qa + d-qa-r (LC8): only 56/1080 skeletons could be claim-true
  (§4.1). Options: accept the no-heavy mix (current; disclosed; identical across arms) vs
  drop claim items entirely. Why uncertain: claim items carry a known mechanical
  polarity channel in the SHUFFLED bridge cell (§5, attack 6). Deciding rule: the channel
  is symmetric across the arms of the PRIMARY, so the mix stands; the shuffled bridge is
  interpreted with the disclosed asymmetry. Kill: if the bridge gate fails only via
  claim items (per-type breakdown, descriptive), the rerun drops claims and mints a new id.

---

## 3. DRAFT `kot-reg/1` record (deliverable 3 — NOT frozen; freeze gates §6.2 now satisfied)

**The registered record file is `registry/experiments/knull.json`** (added at
gate-satisfaction, 2026-07-10; `prereg-freeze.py --dry-run` green). It is the
schema-legal `kot-reg/1` rendering of the design-shaped draft below; where the two
differ on FIELD SHAPE, the record file governs. The mapping, verbatim:

- verdict enum (the schema's closed set): **NULL** carries the PASS-GENERIC outcome
  (TOST equivalence ⇒ the lift is store-content-generic — a decisive null, recorded
  with the same prominence as a PASS); **PASS** carries PASS-CONTENT (kernel superior
  beyond margin); **FAIL** carries KERNEL-INFERIOR (deflationary a fortiori);
  INSTRUMENT-INVALID and the INCONCLUSIVE catch-all are unchanged.
- the draft's `assumptions[]` block lives at `design.n_planned.assumptions` (the
  f2b-replicate pattern; kot-reg/1 has no top-level assumptions field), and the
  per-type breakdown endpoint is registered as a secondary whose test text declares
  it DESCRIPTIVE-only (the schema's role enum has no "descriptive").
- `pins.analysis_script` = `analysis/knull.py` (gate G-4) with its declared
  output_fields; prereg/plan docs + corpus digests + model revisions pinned as in
  the record file.

```json
{
  "schema_version": "kot-reg/1",
  "id": "knull",
  "status": "DRAFT",
  "title": "knull — K-NULL store-content ablation of the f2b verify-retry mechanism: kernel-NSM vs aligned plain-typed vs opaque-ID stores at identical alignment, retry topology and matched budgets; content-injection map first (docs/design-knull-content-injection-ablation.md section 1); decides whether the f2b +0.1507 is a generic aligned-deterministic-answer-key + retry effect or carries NSM-content weight, WITHIN the oracle-favourable construction (gold-label independence stays with f2b-transfer)",
  "depends_on": ["f2b-replicate", "m0b", "f0-harness"],
  "hypotheses": [
    "H-KN1 equivalence: |lift(kernel) - lift(best aligned non-NSM store)| < 0.05 (TOST) => the lift is store-content-generic",
    "H-KN2 superiority: lift(kernel) - lift(best) > 0.05 one-sided => NSM content carries weight beyond alignment at this scope",
    "H-KN3 bridge: kernel arm reproduces the f2b mechanism signature on regenerated surfaces (lift LB > 0.05; shuffled recovery < 0.30)"
  ],
  "design": {
    "independent_vars": [
      {"name": "store", "levels": ["kernel", "plain", "opaque"],
       "note": "store = record content + the item surfaces authored from it (map D-2); alignment, skeletons, distractor/donor coordinates, option-slot layout, templates, retry topology identical across levels; the requested vector-free level is MAP-RESOLVED at $0 (map D-3) and not run"},
      {"name": "cell", "levels": ["alone-R1", "alone-R3", "verify-retry-R1", "shuffled-verify-retry-R1(kernel store only)"]},
      {"name": "retry_budget", "levels": [0, 4]},
      {"name": "seed", "levels": [0, 1, 2]}
    ],
    "dependent_vars": [
      {"name": "item_correct", "unit": "0/1 per item", "better": "higher",
       "definition": "per-item correctness on the arm's own rank-prefix item set (n=1000 skeletons, paired across arms by skeleton_uid)"},
      {"name": "lift_abs", "unit": "fraction", "better": "n/a",
       "definition": "acc(verify-retry-R1, k=4) - acc(alone-R1), item-paired within arm, seed-averaged; ABSOLUTE, no denominator anywhere"},
      {"name": "V components", "unit": "per F0", "better": "lower",
       "definition": "FLOPs/query, latency, usd/query, store bytes per arm (F0 ledger; verifier CPU metered)"}
    ],
    "arms_mandatory_baselines": [
      "alone-R1 per store arm (each arm's own surfaces - the within-arm baseline that makes lifts comparable)",
      "alone-R3 per store arm (bridge restatement of the f2b-form effect; no ratio, no gate)",
      "shuffled-verify-retry on the kernel store (derangement bridge to f2b-replicate, verbatim mechanism)",
      "NOTE kernel-as-text + gloss-self-verify text nulls are NOT re-run: Law-2 nulls were measured against this mechanism in f2b-replicate (beats_text_null, beats_gloss_self_verify both passed, audit CONFIRMED) and no claim here exceeds that scope; this record varies STORE CONTENT within the already-nulled mechanism"
    ],
    "scale_rungs": ["R1", "R3"],
    "seeds": [0, 1, 2],
    "n_planned": {
      "per_arm_items": 1000,
      "item_source": "poc/knull/inputs/items/{kernel,plain,opaque}.jsonl - 1080 skeletons over the 108 covered concepts, generator seed knull/1|knull-content-injection-ablation|20260710, LC8 prompt-surface-disjoint from all 650 d-qa + 1000 d-qa-r logged surfaces IN EVERY ARM, rank-prefix 1000 consumed",
      "pairing": "skeleton_uid - identical concept, template type, distractor/donor concept coordinates and option-slot layout across arms; only store-injected bytes differ",
      "bootstrap_B": 10000, "sap_prng_seed": 20260710,
      "power": "see design doc section 3.6 - 0.65 to 0.95 at margin 0.05 depending on cross-arm item correlation (STIPULATED planning bound, resolution at analysis)"
    }
  },
  "endpoints": [
    {"id": "primary", "role": "primary", "metric": "/analysis/tost_equivalent",
     "test": "TOST equivalence, margin +/-0.05 ABSOLUTE, on D = mean_i [ lift_i(kernel) - lift_i(best) ] where lift_i(a) = seedmean(verify_i) - seedmean(alone_i) in arm a, i indexes skeletons (paired), and best = the aligned non-NSM arm (plain or opaque) passing the difficulty gate with the larger point lift (pre-declared selection); paired skeleton-level BCa bootstrap B=10000 seed 20260710; equivalent iff one-sided 95% LB > -0.05 AND one-sided 95% UB < +0.05. Superiority read: LB > +0.05. Inferiority read: UB < -0.05. ABSOLUTE lifts only - no ratio appears in any verdict-bearing quantity",
     "smallest_effect_of_interest": {"type": "absolute_lift_difference", "value": 0.05}},
    {"id": "gate-bridge", "role": "secondary", "metric": "/gates/bridge_kernel_lift",
     "test": "INSTRUMENT gate: kernel-arm lift one-sided 95% BCa LB > +0.05 - the ablation cannot attribute a lift that failed to reproduce; on failure the primary is INSTRUMENT-INVALID (nothing to attribute), never a hypothesis event"},
    {"id": "gate-difficulty", "role": "secondary", "metric": "/gates/difficulty_band",
     "test": "INSTRUMENT gate per aligned arm: |acc(alone-R1, arm) - acc(alone-R1, kernel)| <= 0.15 (3-seed mean); a failing arm leaves the comparator set BEFORE selection; both failing => INSTRUMENT-INVALID"},
    {"id": "gate-extraction", "role": "secondary", "metric": "/gates/extraction",
     "test": "INSTRUMENT gate per arm: extraction-success Wilson-LB >= 0.90 over all verify calls (P10 discipline, measured in-run)"},
    {"id": "gate-flops-parity", "role": "secondary", "metric": "/gates/flops_parity",
     "test": "INSTRUMENT gate: per-query mean FLOPs of each aligned verify arm within +/-20% of the kernel verify arm (F0 ledger) - the matched-budget guarantee, enforced at build by the +/-25% gloss word-band and verified here",
     "wilson_gate": null},
    {"id": "sec-shuffled-bridge", "role": "secondary", "metric": "/analysis/holm/shuffled_low_recovery",
     "test": "Holm family F-sec(knull): shuffled-derangement recovery on the kernel store < 0.30 (one-sided 95% BCa UB), the f2b-replicate secondary verbatim, on the regenerated surfaces; interpreted with the disclosed claim-polarity asymmetry (design doc section 5 attack 6)"},
    {"id": "sec-f2b-form-bridge", "role": "secondary", "metric": "/analysis/holm/f2b_form_positive",
     "test": "Holm family F-sec(knull): kernel-arm acc(verify-retry R1) - acc(alone R3) one-sided 95% BCa LB > 0 - the f2b-replicate primary's form restated on regenerated surfaces (absolute, no denominator)"},
    {"id": "desc-per-type", "role": "descriptive", "metric": "/analysis/per_type_breakdown",
     "test": "DESCRIPTIVE ONLY, never verdict-bearing: per item-type accuracies and lifts per arm; headroom-normalized lifts reported here and nowhere else"}
  ],
  "kill_criterion_verbatim": "K-NULL verbatim kills: (a) bridge gate fails (kernel-arm lift LB <= +0.05 on regenerated surfaces) => INSTRUMENT-INVALID - the f2b mechanism did not reproduce, nothing to attribute, and the f2b-replicate PASS is NOT thereby contradicted (different surfaces) but a surface-sensitivity flag is raised on the F2 line; (b) TOST passes => the kernel-content attribution DIES at this scope - the f2b lift is licensed as a generic aligned-deterministic-answer-key + retry effect, all forward narration adopts that phrase, and F2-line investment re-routes to authoring-cost economics (the narrowed efficiency reading) and to f2b-transfer; (c) kernel-INFERIOR beyond margin (UB < -0.05) => same deflationary consequence as (b) PLUS NSM surface is a measured net cost at matched alignment - the strongest anti-content outcome; (d) BOTH aligned arms fail the difficulty band => INSTRUMENT-INVALID, redesign the stores (fork F-KN-B/F-KN-C), mint a new id; nulls and positives get equal prominence.",
  "coverage_requirement": {"source": "m0b", "rung_field": "coverage_rung"},
  "extrapolation_envelope_verbatim": "Binding on ANY outcome: claims are scoped to <=1.7B hosts (verify host 135M; 1.7B only as the bridge baseline), the kernel-covered SELF-AUTHORED templated definitional-QA family over the same 108 covered concepts, k=4, this normalization/accept machinery (norm_text string identity + segment membership), and the oracle-favourable construction HELD FIXED BY DESIGN in every arm - verbatim: on the D-QA slice the verifier's accept test is string-equality to the same canonical record that DEFINED the gold answer, so its measured lift is inflated by the eval's construction; K-NULL varies only WHAT the store says, never that construction, so NO outcome here speaks to gold-label independence (f2b-transfer's question), to externally-authored items, to non-templated phrasings, to hosts >1.7B, or to any other corpus. Equivalence licenses the relabel of the f2b lift as a generic aligned-deterministic-answer-key + retry effect AT THIS SCOPE and nothing wider; superiority licenses NSM-content contribution >= 0.05 absolute AT THIS SCOPE and says nothing about semantics-in-general or transfer. Coverage disclosure (mandatory, verbatim): kernel-expressibility coverage 0.3542 at rung molecules-v0 - MEASURED by m0b on one incomplete kernel-v0 instance, NOT general coverage; every accuracy claim is bounded to the kernel-covered slice. Two host rungs license a SIGN, not a slope.",
  "verdict_rules": [
    {"verdict": "INSTRUMENT-INVALID", "when": {"op": "not", "a": {"op": "and",
      "a": {"metric": "/gates/instrument_valid"},
      "b": {"op": "and", "a": {"metric": "/gates/bridge_kernel_lift"},
             "b": {"metric": "/gates/any_aligned_arm_eligible"}}}}},
    {"verdict": "PASS-GENERIC", "when": {"metric": "/analysis/tost_equivalent"},
     "_note": "PASS of H-KN1: attribution resolved DEFLATIONARY - alignment+retry, not NSM content"},
    {"verdict": "PASS-CONTENT", "when": {"metric": "/analysis/kernel_superior_beyond_margin"},
     "_note": "PASS of H-KN2: NSM content carries >= 0.05 absolute at this scope"},
    {"verdict": "PASS-GENERIC", "when": {"metric": "/analysis/kernel_inferior_beyond_margin"},
     "_note": "deflationary a fortiori: NSM surface is a net cost at matched alignment"},
    {"verdict": "INCONCLUSIVE", "when": {"const": true}}
  ],
  "budget": {"usd_cap": 60, "gpu_hours_cap": 8, "wall_clock_cap_hours": 24},
  "runner_constraints": {"provider": "modal", "infra": "modal", "tier": 1,
    "tier_cap_usd": 60, "hardware": "1x A100-40GB (f2b image, I-MODAL rebuild)",
    "harness": "poc/knull (imports poc/f2b/runner/f2b_runner.py machinery read-only at pinned sha b62c3a72...; poc/f2b is not modified)",
    "concurrency_cap": 5, "foreground_gates": true},
  "assumptions": [
    {"tag": "MEASURED", "claim": "f2b lift +0.1507 (LB +0.1053), audit CONFIRMED; derangement recovers ~0; licence = correct-alignment-specific (registry/verdicts/f2b-replicate.json + assessments + feasibility-synthesis 2b)"},
    {"tag": "MEASURED", "claim": "map M-V: 3456/3456 verifier decisions bitwise identical after stripping all non-gloss record fields (poc/knull mock map-check.json) - kernel vectors/ASTs inject zero bytes into the accept seam"},
    {"tag": "MEASURED", "claim": "coverage 0.3542 at molecules-v0 on one incomplete kernel-v0 instance (m0b) - NOT general coverage"},
    {"tag": "STIPULATED", "claim": "power planning bound 0.65-0.95 at margin 0.05, n=1000, from f2b-measured variance scaled + the mock half-width under arm-independent stub noise; planning constant, never a measurement; resolution: realized CI width at analysis"},
    {"tag": "STIPULATED", "claim": "the plain store, once authored (fork F-KN-A), is dictionary-register English with zero NSM-legal syntax, linter-gated; placeholder store is mock-only and the runner refuses non-mock runs on it (KNULL_ERR_DRAFT_ONLY / KNULL_ERR placeholder gate)"},
    {"tag": "STIPULATED", "claim": "holding the oracle-favourable construction fixed across arms isolates the content variable; gold-label independence is explicitly out of scope (f2b-transfer owns it)"}
  ]
}
```

### 3.4 Why THIS primary (estimand notes)

- **Absolute lifts, no denominators** — the F2 lesson, inherited verbatim. `lift(a)` is a
  within-arm paired difference against the arm's OWN alone baseline on the arm's OWN
  surfaces; the cross-arm estimand is a difference of differences. No ratio is
  verdict-bearing anywhere.
- **Within-arm alone baselines** absorb the level difference in surface difficulty that
  I-1 makes unavoidable (plain/opaque surfaces are easier/harder for the host); the
  difficulty-band gate bounds the residual headroom asymmetry (§5 attack 2).
- **Best-comparator selection** is pre-declared (larger point lift among gate-passers) and
  is conservative for the PASS-CONTENT claim (kernel must beat the stronger competitor);
  its ~+0.01–0.03 selection bias on the diff is inside the margin and disclosed (§5
  attack 5).

### 3.5 Instrument gates (each with its own bound; failure ⇒ INSTRUMENT-INVALID, never a hypothesis event)

| Gate | Bound | Rationale |
|---|---|---|
| bridge (kernel lift reproduces) | one-sided 95% LB > +0.05 | can't attribute a lift that isn't there |
| difficulty band per aligned arm | \|Δ acc(alone-R1)\| ≤ 0.15 | bounds retry-headroom asymmetry |
| extraction per arm | success Wilson-LB ≥ 0.90 (all verify calls) | P10 discipline |
| FLOPs parity | per-query FLOPs within ±20% of kernel arm | matched-budget guarantee |
| store completeness | fail-closed at load (sha-pinned record per item) | KernelVerifier ERR_RECORD_PIN, inherited |

Power on the covered slice, coverage restated: all items are drawn from the same 108
covered concepts as d-qa-r; the coverage number bounding every claim is, verbatim,
**kernel-expressibility coverage 0.3542 at rung molecules-v0 — MEASURED by m0b on one
incomplete kernel-v0 instance, NOT general coverage.**

### 3.6 Power (justified before freeze; planning constants STIPULATED, never emitted as measurements)

Two independent bounds on se(D) at n = 1000 paired skeletons, 3 seeds:

- From f2b-measured variance [MEASURED: f2b-replicate primary CI half-width 0.0454 at
  n=250 ⇒ se(lift) ≈ 0.0276 ⇒ at n=1000, se(lift) ≈ 0.0138]: se(D) = 0.0138·√(2(1−ρ))
  for cross-arm item correlation ρ. TOST power at true D=0, margin 0.05:
  ρ=0 → ≈0.65; ρ=0.4 → ≈0.87; ρ=0.5 → ≈0.95.
- From the mock (arm-independent stub noise, a conservative ρ≈0 floor for the pairing
  machinery only): observed one-sided CI half-width of D was 0.025 at n=1080 ⇒
  se(D) ≈ 0.0152 ⇒ TOST power ≈ 0.90. STIPULATED as a planning bound — the stub's
  variance is synthetic.

The skeleton pairing (same concept, type, coordinates, option layout) is designed to make
ρ substantially positive. Honest statement: **power ∈ [0.65, 0.95] at margin 0.05**;
fork F-KN-C pre-declares the fallback if the pre-freeze re-check degrades n.
Superiority (H-KN2) power: for a true content effect of 0.10 (two-thirds of the f2b
headline), one-sided power > 0.99 at any ρ ≥ 0; for a true effect at the margin 0.05,
power = 0.5 by construction (boundary) — H-KN2 is only claimable when content earns
clearly more than the margin, which is the point.

---

## 4. Inputs + harness + green mock (deliverable 4)

### 4.1 Inputs (built, deterministic, hash-pinned)

`python3 poc/knull/build_inputs.py` — $0, CPU, no wall-clock dependence; rebuild is
byte-identical. Manifest: `poc/knull/inputs/manifest.json`, sha256
`ee3a93f5e4a7a6ec871420f9184f7e2dfa7749111a13ae55c819bd7b6306c422` (pins every store
file + item file + the authored plain source + the f2b/build-dqar provenance shas).
Superseded pre-G-1 build (placeholder plain store): manifest sha `fd08807b...` —
retained here only as provenance of the earlier mock transcript.

- **1080 skeletons × 3 arms** over the 108 covered concepts; identical skeleton_uid
  sequence, template types, distractor/donor concept coordinates, and option-slot layout
  across arms (asserted at build: KNULL_ERR_PAIRING); LC8 prompt-surface disjointness vs
  all 1650 logged d-qa + d-qa-r surfaces enforced in EVERY arm (fail-closed).
- Type mix (disclosed): 324 def-match / 324 term-match / 56 claim-true / 376 claim-false,
  IDENTICAL across arms. The claim-true scarcity is real LC8 pressure: d-qa + d-qa-r
  already consumed most of the finite verbatim-segment claim-true surface pool over these
  108 concepts (d-qa-r itself recorded 39 claim-true→claim-false substitutions); 160
  joint substitutions recorded in the manifest. Fork F-KN-D governs this.
- **Opaque store** (`inputs/stores/opaque/`): REAL arm content — deterministic nonce
  definitions, ≥ 2 segments, word target **token-calibrated** (factor
  `OPAQUE_TOKEN_CALIB = 0.48`, band ±25% vs the calibrated target,
  KNULL_ERR_WORDBAND fail-closed), uniqueness asserted. Why calibrated: nonce
  syllable text tokenizes at ~2.09x the rate of NSM English under the pinned
  SmolLM2 tokenizer, so an uncalibrated word band silently broke the FLOPs-parity
  budget the word band was proxying — exactly the failure mode gate G-3 exists to
  catch (measured in `inputs/g3-token-band.json`; §6.2 G-3).
- **Plain store** (`inputs/stores/plain/`): **AUTHORED** plain-dictionary definitions
  (`plain_store_placeholder: false`; source file `inputs/plain-authored.json`, sha256
  `df4a17cff6c6da70ddb19c1ef2f4d25b5868ac352318162e8e68f9982848cf58`, fork F-KN-A
  option (ii), disclosure block inside the file). Linted fail-closed at build by
  `poc/knull/lint_plain_store.py` (gate G-1): LC1 (full label AND headword), ±25%
  word band vs the NSM gloss, ≥2 admissible segments, pairwise + vs-canonical
  uniqueness, no-verbatim-NSM-line (both directions), the register check
  ("zero NSM-legal syntax": every segment carries ≥1 token outside the 65-prime
  exponent surface + closed function words + the 108 concept headwords; whole-def
  non-NSM ratio ≥ 0.25 — authored min 0.333, canonical-gloss max 0.069),
  own-gloss Jaccard < 0.5, ASCII/quote/account hygiene, disclosure presence.
  Blind style spot-check file: `inputs/plain-spotcheck.json` (maintainer step).
- **Kernel store**: the existing pinned records (`data/kernel-v0` + `data/molecules-v0`),
  untouched; items carry the same record_path + record_sha256 pins the verifier
  fail-closes on.

### 4.2 Harness

`poc/knull/runner/knull_runner.py` — enforces "arms differ ONLY in store semantics"
**structurally**, by importing the frozen f2b machinery (KernelVerifier,
ShuffledKernelVerifier, run_alone, run_verify_retry, extract_record, verify_answer, the
verbatim f2b prompt frames and F0 flop accounting) at the pinned sha
(`KNULL_ERR_PIN` fail-closed) and swapping only `records_root` + the item file per arm.
`poc/f2b/**` is never modified. Real-mode is refused (`KNULL_ERR_DRAFT_ONLY`) until a
frozen record for `knull` is in `registry/frozen-index.json` AND the plain store is
non-placeholder — and even then this designer-built harness stops at
`KNULL_ERR_RUNNER_ROLE`: the real HF-backend campaign is runner-role work against the
frozen record (run ≠ audit), re-pinned at campaign start exactly as f2b did.
`--dry-plan` (gate G-2's $0 real-path smoke) verifies every pin, loads the full
n=1000 rank-prefix item sets + stores fail-closed, and prints the 30-GPU-cell plan
with its cost envelope. Cells emit per-item coverage vectors + metered per-query
FLOPs, the exact input contract of the pinned SAP `analysis/knull.py` (G-4).

### 4.3 Green mock (mechanics only, $0 — never measurements)

```
python3 poc/knull/runner/knull_runner.py --selftest
  -> selftest OK: EQUIVALENT-GENERIC / KERNEL-SUPERIOR / KERNEL-INFERIOR all
     classified correctly (planted data)
python3 poc/knull/runner/knull_runner.py --mock --out-dir <scratch> --items 1080
  -> map-check M-V: 3456 decisions IDENTICAL (the $0 vector-free result, real;
     re-proven on the authored-store build 2026-07-10)
  -> 20 cells green (3 arms x [alone-R1, alone-R3, verify] x 2 mock seeds
     + 2 shuffled bridge cells); all gates computed; extraction 0 failures;
     MOCK verdict shape INCONCLUSIVE (diff -0.025, CI [-0.050, 0.000]) under an
     ARM-BLIND stub - the expected mock shape is equivalence-noise, and every
     analysis path (gates, TOST, superiority, inferiority, Holm secondaries,
     per-type breakdown) executed; ~22 s CPU
python3 poc/knull/runner/knull_runner.py --dry-plan            (gate G-2)
  -> dry-plan OK: 30 GPU cells over 1000 paired items x 3 arms; all pins
     verified; stores load fail-closed
python3 analysis/knull.py --selftest                           (gate G-4)
  -> analysis selftest OK: equivalence / superiority / inferiority /
     difficulty-gate / shuffled-bridge all classified correctly (planted covs)
python3 analysis/knull.py --records <mock>/run-records.jsonl
    --item-meta <mock>/item-meta.json --out <mock>/analysis-sap.json
  -> knull SAP: n=1080 best=opaque diff=-0.0255 [-0.0514, -0.0009]
     tost/sup/inf all False (INCONCLUSIVE shape); bridge + difficulty +
     extraction gates green; Holm + per-type paths executed; ~9 s CPU
```

Known mock-only artifact, disclosed in advance: the SAP's `flops_parity` gate reads
FALSE **on mock records only** (`flops_ratio_opaque` ≈ 0.61) because the StubLM
meters tokens by a chars/4 proxy, which undercounts nonce text roughly 2x. The
authoritative pre-freeze parity evidence is the pinned-tokenizer G-3 measurement
(opaque/kernel mean-prompt-token ratio **1.004**, plain 0.948 —
`inputs/g3-token-band.json`); at run time the real HFLM meters real token counts.
The SAP is not bent to make the mock pretty: the gate stays strict.

Mock artifacts worth recording (stub-level, labelled MOCK, never measurements): the
shuffled bridge cell showed recovery ≈ 0.25 under the stub — a mechanical consequence of
the claim-polarity channel (§5 attack 6) amplified by the no-heavy mix and the stub's
uniform skill; f2b's MEASURED recovery on the real model was −0.021. The bridge secondary
inherits the f2b bound (< 0.30) with this asymmetry disclosed in advance.

---

## 5. Pre-freeze skeptic memo (deliverable 5 — freeze is BLOCKED without this)

**Attack 1 — "your arms differ in more than store semantics" (the tasked special
attention).** True and unavoidable, and the map says exactly where: I-1 makes item
surfaces store-derived, so changing the store changes the surfaces. Defence: (i) the
skeleton pairing holds concept, template, distractor/donor coordinates and option-slot
layout fixed — the ONLY differing bytes are store-injected; (ii) the estimand is a
difference of WITHIN-ARM lifts, so each arm is scored against its own surfaces' baseline;
(iii) the difficulty band gate bounds residual headroom asymmetry; (iv) FLOPs parity is
gated. Residual honest risk: retry-resample lift is not perfectly headroom-invariant even
inside the band; the descriptive per-type/headroom table is pre-declared so a boundary
case is visible. VERDICT-RELEVANT: yes, this is the design's irreducible approximation,
and the margin (0.05) was chosen larger than the plausible residual (≤ ~0.02 inside a
0.15 band).

**Attack 2 — trivial-identity (the reason the map came first).** A conventional store
holding the same strings is bitwise the same verifier (map D-2); a vector-free arm is a
no-op (map D-3, proven 3456/3456). Defence: the plain arm stores DIFFERENT strings
(authored plain-dictionary register), the opaque arm stores nonces; the vector-free arm
is not run. Without §1 this experiment would have "passed" trivially and meant nothing.

**Attack 3 — oracle leakage survives in every arm.** Correct, BY DESIGN (map D-4): gold
is each arm's own store string; the construction is held fixed so only content varies.
Restated verbatim in the envelope; no outcome licenses any gold-label-independence claim.
The design would be BROKEN if one arm's gold were external — that would confound content
with the leakage structure itself.

**Attack 4 — the placeholder plain store could silently ship.** Blocked twice:
`plain_store_placeholder: true` in the manifest + `KNULL_ERR_DRAFT_ONLY` in the runner;
freeze gate G-2 requires the authored store + linter pass + re-pinned manifest. A frozen
record pointing at a placeholder sha cannot pass registry lint against G-2's checklist.
*Resolution 2026-07-10: the authored store LANDED (G-1/G-2 satisfied; §6.2); the flag
is false in the re-pinned manifest; the runner still refuses real runs until the
record is in `registry/frozen-index.json`, and then stops at `KNULL_ERR_RUNNER_ROLE`
— the campaign belongs to the runner identity, not this designer.*

**Attack 5 — best-comparator selection gameability.** Selecting the max-lift aligned arm
after seeing lifts is a post-hoc choice INSIDE the frozen SAP (a deterministic function
of the data, pre-declared). It biases D downward by ~E[max of two ≈0-mean noises] ≈
+0.01–0.03 on the comparator, i.e. AGAINST PASS-CONTENT and toward
PASS-GENERIC/INFERIOR; the margin covers it and the direction is conservative for the
claim we'd most want to protect against overclaiming (content). Disclosed here; not
correctable without dropping to a single fixed comparator (rejected: fork F-KN-B risk
would then make the whole run hostage to one arm's difficulty gate).

**Attack 6 — the shuffled bridge has a mechanical claim-polarity channel.** On claim
items the deranged verifier still computes membership against SOME gloss; a donor claim
is almost never a member of the deranged gloss, so the shuffled arm systematically
accepts "no" — which is CORRECT on claim-false items. With this no-heavy mix (376/56)
the channel is stronger than in d-qa-r (363/177). It is symmetric across the PRIMARY's
arms (each arm's shuffle would face it identically — only the kernel store's shuffle is
run) and touches only the BRIDGE secondary, whose interpretation carries this disclosure.
f2b's measured recovery (−0.021) says the real model's alone-arm already captures most of
that channel. If the bridge secondary fails ONLY via claims (per-type breakdown), fork
F-KN-D's kill applies.

**Attack 7 — underpowered TOST masquerading as equivalence-evidence.** TOST cannot
"pass by noise" (that is its point — low power ⇒ INCONCLUSIVE, not EQUIVALENT), but an
INCONCLUSIVE could be spun as "no difference found". Pre-commitment: INCONCLUSIVE
licenses NOTHING except a power note and (if CI width > 2× planned) a design-defect flag.
Refusal-valid: INCONCLUSIVE and INSTRUMENT-INVALID are registered outcomes with
pre-written meanings.

**Attack 8 — claim-true scarcity makes the item family drift from d-qa-r's.** Disclosed
(§4.1, fork F-KN-D); the mix is identical across arms so the PRIMARY is internally valid;
the BRIDGE gate is where family drift would show (a kernel-arm lift that fails to
reproduce), and its failure is pre-declared INSTRUMENT-INVALID with a surface-sensitivity
flag — explicitly NOT a contradiction of the f2b-replicate PASS.

**Attack 9 — LLM-authored plain store imports host-model idiom (fork F-KN-A, option ii
risk).** If the plain definitions are drafted by a model from the same family/tradition
as the host, familiarity could inflate the plain arm's alone accuracy (harmless — within-
arm baseline) or its verify acceptance dynamics (not harmless). Mitigation: authoring
source must be disclosed in the frozen record; linter includes a no-verbatim-NSM-line
check; the truthstyle-2x2 sibling measures the style-familiarity axis directly and its
read informs F-KN-A before freeze.
*Resolution 2026-07-10: option (ii) taken with the mitigations realized — disclosure
block committed inside `plain-authored.json` and copied into the manifest + record;
the drafting family (Claude/Fable) differs from the SmolLM2 host family; the
no-verbatim-NSM-line check (R-1) and the register check (R-2) pass on all 108
definitions. The residual style-familiarity stipulation is REPORTED for ASM
registration at freeze (§6.4) with truthstyle-2x2 as its resolution path; if
truthstyle-2x2 reads out before the knull campaign launches, its read is attached to
the run packet as context (it does not amend this record).*

**Attack 10 — run≠audit and ownership.** This line touches only `poc/knull/**` + this
doc. The designer identity (this role) will not run the final campaign, grade, or audit;
the verdict is the pinned SAP's pure function; a computed PASS is PASS-PENDING-AUDIT
until the cross-vendor auditor confirms.

---

## 6. Envelope, licensing, compute ask, handoff

### 6.1 What each outcome licenses (and does not)

| Outcome | Licenses (at THIS scope only) | Does NOT license |
|---|---|---|
| PASS-GENERIC (TOST) | relabel the f2b lift "generic aligned-deterministic-answer-key + retry effect"; re-route F2-line effort to authoring-cost economics + f2b-transfer | any kernel-content kill beyond this scope; no statement about gold-label independence; the narrowed efficiency reading of f2b SURVIVES |
| PASS-CONTENT (superiority) | "NSM-shaped canonical store content contributes ≥ 0.05 absolute to the verify-retry lift" at this scope — first content-attribution evidence | semantics-in-general; transfer; anything off-slice, off-template, >1.7B, or off the oracle-favourable construction |
| KERNEL-INFERIOR | PASS-GENERIC's consequences + "NSM surface is a measured net cost at matched alignment" | as above |
| INCONCLUSIVE / INSTRUMENT-INVALID | a power/design note; fork re-entry | any attribution statement in either direction |

Scale language: two host rungs ⇒ sign-only, verbatim inherited. Every claim bounded to
the covered slice with the m0b coverage sentence restated (§3.5).

### 6.2 Pre-freeze gates — ALL SATISFIED 2026-07-10 (evidence per gate)

1. **G-1 SATISFIED**: fork F-KN-A decided → option (ii) (§2.3); authored plain store
   landed (`poc/knull/inputs/plain-authored.json`, sha256
   `df4a17cff6c6da70ddb19c1ef2f4d25b5868ac352318162e8e68f9982848cf58`); linter
   `poc/knull/lint_plain_store.py` green on all checks — LC1 (full label AND
   headword), ±25% word band, ≥2 segments, uniqueness (pairwise + vs canonical),
   no-verbatim-NSM-line, register/no-NSM-legal-syntax (authored min ratio 0.333 vs
   canonical max 0.069, threshold 0.25), own-gloss Jaccard, hygiene, disclosure.
   Blind spot-check file prepared (maintainer sign-off step, §2.3).
2. **G-2 SATISFIED**: `plain_store_placeholder: false`; manifest re-pinned
   (`ee3a93f5e4a7a6ec871420f9184f7e2dfa7749111a13ae55c819bd7b6306c422`); runner
   real-path smoke green via `--dry-plan` ($0 analog: every pin verified, full
   n=1000 rank-prefix item sets + all three stores loaded fail-closed, 30-cell plan
   emitted). The Modal-side I-MODAL image rebuild smoke remains a runner-role step
   at campaign start (same posture as nsk1's real-mode HF harness) — it is a spend
   step, not a design step, and is listed in the dry-plan's
   `residual_runner_role_steps`.
3. **G-3 SATISFIED**: tokenizer-level re-check run with the pinned
   SmolLM2-135M-Instruct tokenizer (revision `12fd25f7...`, tokenizer.json sha256
   `9ca9acdd...`): the word-band proxy had silently left the opaque store at
   **2.09x** kernel tokens; the opaque generator was token-calibrated
   (`OPAQUE_TOKEN_CALIB = 0.48`) and the rebuilt stores measure — mean prompt
   tokens per item, exact f2b `build_prompt` rendering — kernel 110.5, plain
   104.8 (ratio 0.948), opaque 110.9 (ratio 1.004), all inside the pre-declared
   ±10% pre-freeze band (run-time gate ±20%). Artifact:
   `poc/knull/inputs/g3-token-band.json`. Fork F-KN-C margin call FINALIZED:
   n stays 1000 ≥ 900 ⇒ **margin 0.05 stands**.
4. **G-4 SATISFIED**: pinned SAP `analysis/knull.py` (sha256
   `683f3e06189da0856565b1c6cd1053a9116dabaa21d65488919955458951f3bf`) — BCa,
   B=10000, seed 20260710, ONE shared skeleton-level resampling plan across all
   statistics; output fields declared in the record
   (`pins.analysis_script.output_fields`); selftest green (5 planted regimes);
   full run over the 1080-item mock green (§4.3).
5. **G-5 SATISFIED**: N0 §5 / N1-A §8 checklists run — item-by-item record in
   §6.5; this skeptic memo re-read against the final record 2026-07-10 (attacks 4
   and 9 updated in place with their resolutions; no new attack found; the one new
   design fact — opaque token calibration — is attack-1-relevant and disclosed in
   §4.1/G-3). The freeze itself is the COORDINATOR'S step:
   `python3 tools/registry/prereg-freeze.py --experiment knull --agent-id
   coordinator-1` + RT-15 external timestamp (post the printed hash line to the
   coordination issue).

### 6.3 Compute ask (GPU-gated; maintainer sign-off requested)

- **Hardware:** 1× A100-40GB on Modal (the f2b image, I-MODAL rebuild from the pinned
  requirements).
- **Size:** 30 GPU cells (3 arms × 3 cells × 3 seeds + 3 shuffled bridge cells) at
  n=1000 items; scaling the MEASURED f2b wall-clock (0.604 GPU-h for 20 cells at n=250,
  incl. heavier arms we drop) ⇒ **≈ 4–6 GPU-h, ≈ $15–30**; caps requested:
  **usd_cap 60, gpu_hours_cap 8, wall-clock 24 h** — comfortably inside the $0–250
  envelope. $0 spent to date (mock + map are CPU).
- **What the spend buys:** the cheapest attribution decision available on the F2 line —
  it settles what the programme's only positive end-task number is evidence of, ahead of
  any further F2-line spend, and is decision-relevant regardless of direction.

### 6.4 Handoff

- Runner identity for the campaign: an Opus runner role (never this designer); grading by
  the pinned SAP; audit by `codex-gpt5.5/*`.
- Sibling coordination: f2b-transfer (human) proceeds independently — either line settles
  attribution; if the human read lands first, K-NULL's freeze decision is revisited
  (it may still be worth running for the content-vs-alignment axis, which f2b-transfer
  does not measure).
- Everything here persists in-repo: this doc, `poc/knull/**`, `analysis/knull.py`,
  `registry/experiments/knull.json`. Temporary mock outputs live in the session
  scratchpad only.
- **ASMs to REGISTER at freeze** (reported here for the coordinator — this designer
  does not append to `registry/assumptions.jsonl`; mint at the next free ids, watching
  the flagged id-collision queue):
  1. STIPULATED — power planning bound for the knull TOST primary: power 0.65–0.95 at
     margin 0.05, n=1000 paired skeletons, from f2b-measured variance scaled +
     mock half-width under arm-independent stub noise; a planning constant, never a
     measurement; owner designer-1; resolution_path: realized CI width at analysis.
  2. STIPULATED — plain-store style-familiarity residual: the authored
     dictionary-register store (LLM-drafted, Claude/Fable family ≠ SmolLM2 host
     family, linter-gated) does not advantage/disadvantage the plain arm's verify
     acceptance dynamics beyond what the within-arm baseline and difficulty gate
     absorb; owner designer-1; resolution_path: truthstyle-2x2 readout (style axis)
     + knull's own difficulty-gate + per-type descriptive table.
  3. STIPULATED — construction-held-fixed licence: holding the oracle-favourable
     construction fixed across arms isolates the content variable; gold-label
     independence is explicitly out of scope (f2b-transfer owns it); owner
     designer-1; resolution_path: f2b-transfer Stage-2 human read.
  4. STIPULATED — StubLM chars/4 token proxy is mock-mechanics only; the mock
     flops_parity=false artifact (§4.3) carries no information about the real gate,
     whose pre-freeze evidence is the pinned-tokenizer G-3 artifact (opaque ratio
     1.004); owner designer-1; resolution_path: run-time HFLM-metered FLOPs ledger.
- **Coordinator freeze sequence**: (1) register the 4 ASMs; (2)
  `python3 tools/registry/prereg-freeze.py --experiment knull --agent-id
  coordinator-1` (drop `--dry-run` only when ready — dry-run is green as of
  2026-07-10); (3) post the printed `external_timestamp_post` hash line to the
  coordination issue (RT-15); (4) `tools/kb/kb-sync-internal` for this doc's edits
  (this designer does not run it).

### 6.5 G-5 checklist run (N0 §5 items 1–10; N1-A §8 items 11–15) — 2026-07-10

1. **Law / interface-locality cell**: Law 2 (kernel-as-text is the real opponent) is
   the line's SUBJECT — knull ablates store content inside an already-nulled
   mechanism; interface cell = text-in/text-out (verifier reads strings, model sees
   text; map §1). No raw-coordinate cell is touched (map M-V: zero vector bytes in
   the seam).
2. **X3 cosine ban**: no kernel-vector cosine anywhere — the verifier is string
   identity/membership (map A-1..A-4); the item generator is hash+Jaccard on tokens.
3. **Kernel-as-text null**: measured against THIS mechanism in f2b-replicate
   (beats_text_null, audit CONFIRMED); not re-run — no claim here exceeds that
   scope, and the record's arms_mandatory_baselines carries the justification
   verbatim (§3 record NOTE).
4. **Shuffled-kernel / scramble controls**: shuffled-derangement bridge cell on the
   kernel store (H-KN3 + Holm secondary), claim-polarity asymmetry disclosed
   (attack 6); the plain/opaque arms ARE the content-scramble axis.
5. **Metric vector V + strong baselines**: V components logged per arm (F0 ledger,
   descriptive); baselines = within-arm alone-R1, alone-R3 (1.7B), the f2b-frozen
   nulls by reference; authoring cost of the plain store is part of the
   PASS-GENERIC consequence analysis (re-route to authoring-cost economics).
6. **Scale rungs + envelope + anchor**: R1 + R3 declared ⇒ sign-only language,
   envelope verbatim in the record; literature anchor inherited from f2b-replicate's
   envelope (P1 §4b HE1 cascade/verification-routing anchors) — knull makes no
   scale claim of its own.
7. **No semantic-web smuggling**: stores are flat JSON {label, gloss}; no RDF/OWL
   anywhere (directives §1).
8. **Absorption framing**: outcomes license attribution/efficiency statements only
   (§6.1); no permanent-residence claim in any outcome.
9. **Coverage + power on the covered slice**: all items over the 108 covered
   concepts; m0b coverage sentence restated verbatim in §3.5 and in the record's
   envelope + n_planned; power ∈ [0.65, 0.95] at margin 0.05 (§3.6, STIPULATED
   planning bound, ASM 1 above); decidability: TOST cannot pass by noise
   (attack 7), Wilson extraction gate powered at n=3000 verify calls/arm.
10. **Run ≠ audit route**: designer (this role) → Opus runner → SAP pure function →
    Codex/GPT-5.5 cross-vendor audit; identities named in §6.4.
11. **Composition accounting (N1-A 11)**: no composed arm is claimed; the only
    composition is the frozen f2b mechanism itself, declared as the unit under
    ablation.
12. **Routing/mis-route gate (N1-A 12)**: n/a — no router in this design.
13. **Workload-mix sensitivity (N1-A 13)**: the type mix is fixed and IDENTICAL
    across arms (324/324/56/376), disclosed with the claim-true scarcity fork
    F-KN-D; no mixed-workload claim is made, and the per-type table is descriptive.
14. **Stage indictment (N1-A 14)**: per-stage instruments present — extraction gate
    (P10), difficulty band (headroom stage), bridge gate (mechanism-reproduction
    stage), FLOPs parity (budget stage); each failure names its stage as
    INSTRUMENT-INVALID rather than a hypothesis event.
15. **Dose–response discipline (N1-A 15)**: n/a — no swept knob; k=4 fixed,
    inherited pre-registered from f2b-replicate.
