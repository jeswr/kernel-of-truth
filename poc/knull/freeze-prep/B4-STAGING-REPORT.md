# B-4 staging report — knull-v2 record delta applied to a STAGED copy

**Prepared 2026-07-13 by the designer role (designer-30). $0, CPU-only. This session wrote exactly
two files — `poc/knull/freeze-prep/knull-v2-staged.json` (this delta applied) and this report. No
registry file was edited, nothing was frozen, `prereg-freeze.py` was never executed (not even
`--dry-run` — that step is the coordinator's G-5), no git, no spend, no launch.**

Inputs read in full: `registry/experiments/knull-v2.json` (DRAFT, sha256 at staging time
`8708ca12a8cb24d4824af13d7f08febf33433d2a360ba0fcb5c1efbd4053ac85`),
`poc/knull/freeze-prep/record-delta-v4.md` (the 9-part delta + invariants),
`poc/knull/freeze-prep/B1-B3-DONE.md` (the built-pin shas), `docs/next/design/knull-optionb-analysis.md`
(sections 3, 4.1–4.6, 6), `analysis/knull_v3.py` (`OUTPUT_FIELDS` + holm emission),
`tools/registry/prereg-freeze.py` + `kot_common.py` (the exact freeze-time constraint semantics),
`registry/schema/kot-reg-1.json`, `registry/assumptions.jsonl` (ASM-1080..1088 as registered),
`poc/knull/inputs-v4/manifest.json` + `g3-token-band.json` + the four item files.

---

## 1. Deliverable

`poc/knull/freeze-prep/knull-v2-staged.json` = the committed DRAFT with **all 9 delta items applied
and every `PINNED-AT-BUILD` resolved to its real sha**, `status` still `DRAFT`, ready to be copied
verbatim to `registry/experiments/knull-v2.json` by the coordinator. Every sha below was
**recomputed from the committed bytes this session** (not copied blind from B1-B3-DONE.md); all
matched.

### Delta items 1–9, as applied

| # | delta item | applied as |
|---|---|---|
| 1 | store IV += plain-padded; cell restriction; baselines | `store.levels` gains `plain-padded(alone-R1 + verify-retry-R1 cells only, seeds {0,1,2}, ... ASM-1086)` (the v2 `shuffled-verify-retry-R1(kernel store only)` annotation pattern — the IV item schema admits only `name`+`levels`, so the restriction lives in the level string); `arms_mandatory_baselines` gains the ASM-1082 padded-arm entry with the section-3(b) rationale pointer + disclosed conservative bias direction |
| 2 | item_source → inputs-v4 + re-derived type mix | `poc/knull/inputs-v4/items/{kernel,plain,plain-padded,opaque}.jsonl`; type mix re-derived and REQUIRED identical across all four arms: all-1080 = 324/324/43/389 (def/term/claim-true/claim-false), rank-prefix-1000 consumed = 300/304/39/357 — **verified identical across all four arms by direct recount of the committed item files this session**; all-108-single-segment claim-true scarcity disclosed (v3 had 81/108) |
| 3 | prefreeze_gates_evidence rewrite | G-1 v4 store `97609abe…` + report `92e2e159…` + linter `8049459c…`; G-2 manifest `ae52862d…`; G-3 four-arm re-check PASS, band scoped per ASM-1085 (kernel 110.5 ref; plain-padded 109.4 / 0.990 BOUND; opaque 111.0 / 1.004 BOUND; plain 73.2 / 0.662 DESCRIPTIVE-disclosed), artifact `2a8d2f70…` + sidecar `d9312f19…`, margin call 0.05 STANDS, projection `c150270e…` non-binding; G-4 `analysis/knull_v3.py` `54528cd4…`; G-5 prereg_doc + `prefreeze-checklist.json`; QUALITY GATE: MEASURED gate_met false (GPT-5.6 4/10, Haiku 3/10, tally `d10373c6…`) **ESCALATED clause replaced by RESOLVED** via the maintainer issue-17 acceptance ruling + blind style sign-off 10/10 (`295bf427…`; bookmark item-5 caveat carried, non-blocking) |
| 4 | assumptions | v2 G-3 parity claim → ASM-1085/1088-scoped statement with the v4 MEASURED numbers (STIPULATED, MEASURED components cited — the ASM-1088 pattern); plain-store claim → v4.0.0 + full acceptance lineage (STIPULATED); new entry citing ASM-1080..1088 as REGISTERED, tags exactly as registered (all STIPULATED); entries 1, 2, 4 (power bound), 6, 7 carried verbatim |
| 5 | endpoints + hypotheses | primary test gains the ASM-1083 IUT conjunction verbatim-in-substance (D_matched, best_matched = plain-padded else opaque, no Holm resize, `length_guard_available` forcing, outcome space NULL/FAIL/INCONCLUSIVE when unavailable); gate-difficulty + gate-extraction extended to plain-padded (`/gates/difficulty_band_plain_padded`, `/gates/extraction_wilson_lb_plain_padded`); gate-flops-parity re-scoped per ASM-1085 (binds `flops_ratio_plain_padded` + `flops_ratio_opaque`; plain metered DESCRIPTIVE 0.662); the two section-4.5 descriptive secondaries added (`desc-length-effect`, `desc-length-sensitivity`); H-KN2 restated with the token-matched guard |
| 6 | kill + envelope | kill (b) and (c) gain the "at no greater token budget" clause (ASM-1084); envelope gains the natural-length scope sentence and the NULL relabel adopts "at no greater token budget"; the final sentence "Two host rungs license a SIGN, not a slope." kept byte-verbatim (the scale-language freeze lint is a no-op here anyway — no `scale_language_max` is declared, verified against `check_scale_language`) |
| 7 | pins | `analysis_script` → `analysis/knull_v3.py` sha `54528cd4…`, output_fields = 68-field list (see section 2); `harness_manifest` → v4 manifest/builder/linter/checker/artifact/sidecar paths + shas with the v1-custody, opaque-byte-identity, decision-isomorphism, and 36-cell runner-role notes; **`corpus_hashes` and `model_revisions` byte-untouched** |
| 8 | title | restated per the delta: Option-B natural-length re-authoring (issue-17-accepted v4) + deterministic length-matched plain-padded secondary arm + length-guarded superiority read; v1 supersession + frozen_sha carried |
| 9 | budget / runner_constraints | caps unchanged (60 USD / 8 GPU-h / 24 h — asserted equal to the DRAFT at build); `runner_constraints.gate` estimate note → 30 + 6 plain-padded 135M cells = 36 GPU cells (planning estimates, never measurements) |

### PINNED-AT-BUILD → real sha resolution (all recomputed + matched this session)

| PINNED-AT-BUILD slot | resolved to |
|---|---|
| G-2 inputs-v4 manifest | `poc/knull/inputs-v4/manifest.json` `ae52862d9f95c83238230ed555628318140f69f9c456eb95fc82b25fcac2ebfe` |
| G-3 token-band artifact | `poc/knull/inputs-v4/g3-token-band.json` `2a8d2f7018787a0ec4c81cfe3ee483bd441a200700ba1263561e1512a4dbafcc` |
| G-3 per-item sidecar | `poc/knull/inputs-v4/prompt-tokens.json` `d9312f19a3a7338dbee1f5f7113803544e38218c30524f9d226b05edf09aa179` |
| G-4 / pins.analysis_script | `analysis/knull_v3.py` `54528cd42485effd8a08c6472b7f1f1bff6074ad1b62cf24604b9a8dbedfa181` |
| harness builder | `poc/knull/build_inputs_v4.py` `5d15e3379adb537a9563047bf518a93f47d857dda89123c6cd8de58f6ee7bdd4` |
| harness G-3 checker | `poc/knull/check_token_band_v4.py` `30d87d53f0baf15013fd73fe974d37a3d137294b5db652f4e3735f183a503ad6` |
| (prefilled by the delta, re-verified) v4 store / lint report / linter | `97609abe…` / `92e2e159…` / `8049459c…` |
| (prefilled, re-verified) quality tally / sign-off / flops recheck | `d10373c6…` / `295bf427…` / `c150270e…` |

## 2. One disclosed judgment call: the output_fields list

B1-B3-DONE.md calls the module constant `OUTPUT_FIELDS` "copy-ready" for the pin. **Copied verbatim
it would REFUSE the freeze**: `OUTPUT_FIELDS` carries the container pointer `/analysis/holm` but not
the `/analysis/holm/...` subfield pointers, while two endpoint metrics (`sec-shuffled-bridge`,
`sec-f2b-form-bridge`) are `/analysis/holm/shuffled_low_recovery` and `/analysis/holm/f2b_form_positive`
— and `prereg-freeze.py` constraint 2 is **exact set membership** (`prereg-freeze.py` lines 424–436),
so `ERR_P2_UNKNOWN_POINTER` would fire. The delta itself states the governing rule: "Every metric
pointer in `verdict_rules`/`endpoints` must stay inside the new field list (freeze constraint 2)",
and section 4.6 of the optionb design note defines the new list as **"Add: …" to the DRAFT list** —
i.e. the 8 holm subfield pointers are carried, not dropped.

Staged list = the 60-entry module `OUTPUT_FIELDS` (byte-imported from `analysis/knull_v3.py`, so
the section-4.6 additions incl. `/analysis/holm`, `/analysis/sap`, `/analysis/margin` are exact)
**plus the 8 DRAFT holm subfield pointers** inserted after `/analysis/holm` = **68 fields**.
Resolvability proven, not assumed: `analysis/knull_v3.py` sets all 8 subkeys (`shuffled_low_recovery`,
`shuffled_low_recovery_p`, `f2b_form_positive`, `f2b_form_positive_p`, `shuffled_recovery_fraction`,
`shuffled_recovery_ub95`, `f2b_form_effect`, `f2b_form_lb95_1s`; source lines 495–530), and trip-wire
T11 below resolves **all 68** pointers against a live emitted document from the pinned script.

## 3. Coherence adaptations inside the delta's items (disclosed for the coordinator's review)

Four spots where the delta's named change forces a co-located text fix; each is inside a field the
delta already rewrites, none changes design substance:

1. **kill (d)** "BOTH aligned arms fail the difficulty band" → "ALL aligned arms (plain,
   plain-padded, opaque) fail the difficulty band" — delta item 5 extends the difficulty gate to
   three aligned arms and `/gates/any_aligned_arm_eligible` now ranges over all three (ASM-1085);
   "BOTH" would be incoherent with the gate that decides this kill.
2. **n_planned.best_comparator_rule** → the three-arm comparator set {plain, plain-padded, opaque}
   per optionb-analysis section 4.2 (the primary's `best` selection the delta's item 5 references).
3. **n_planned.power** margin-call citation `poc/knull/inputs/g3-token-band.json` (the stale v1
   artifact path in the DRAFT) → `poc/knull/inputs-v4/g3-token-band.json`, which carries the
   re-affirmed `margin 0.05 STANDS (n_planned 1000 >= 900)` block.
4. **assumption 5** "the Fable designer role" → "the designer role" — engine names are not
   load-bearing for this record (colibri convention); the vendor/family-disclosure substance is kept.

Everything else the delta does not name is **byte-identical to the DRAFT** (proven by T12a–T12i:
field-level diff of staged vs DRAFT).

## 4. Trip-wire verification — 25/25 PASS

Run via granular `kot_common` / `prereg-freeze` **library** checks against the staged copy (and a
`frozen_by`/`frozen_at`-stamped simulation of it). The `prereg-freeze.py` **tool** was not executed.

| # | invariant | result |
|---|---|---|
| T1 | staged JSON parses; kot-reg/1 schema valid (`kot_common.validate_schema`, additionalProperties enforced at every level) | **PASS** (0 violations) |
| T2a | exactly one `role:"primary"` endpoint | **PASS** (id `primary`) |
| T2b | last verdict rule == the INCONCLUSIVE catch-all `{"verdict":"INCONCLUSIVE","when":{"const":true}}` | **PASS** |
| T3 | pointer closure (ERR_P2_UNKNOWN_POINTER): 13 unique metric pointers enumerated below, each a member of the 68-field `output_fields` | **PASS** |
| T4 | NULL rule present AND primary keeps `smallest_effect_of_interest` = {absolute_lift_difference, 0.05} | **PASS** |
| T5a | `pins.corpus_hashes` byte-identical to the DRAFT | **PASS** |
| T5b | all four corpus digests + the `_recipe` string reproduce from `data/` TODAY (`kot_common.corpus_hash`) | **PASS** (d-qa, d-qa-r, kernel-v0, molecules-v0) |
| T6 | RT-14: `require_no_account_strings` over the exact hashed byte range AND the whole staged file; `check_identity_fields` (no identity fields present — none needed pre-freeze) | **PASS** (zero hits) |
| T6b | no `PINNED-AT-BUILD` placeholder remains anywhere in the staged bytes | **PASS** |
| T7 | P-6 pins reproduce: `analysis/knull_v3.py`, `analysis_plan_ref`, `prereg_doc` shas match committed bytes | **PASS** |
| T8 | Wilson gate powered at planned n (threshold .90, expected .95, n 3000) | **PASS** |
| T9 | **full `check_record()` freeze-constraint suite** (constraints 1–10 incl. scale-language, reuse-collision, signoff, baselines) green on the stamped staged copy | **PASS** |
| T10 | PAUSE scan (`scan_open_extrapolations`): predicted `pause_flags` | **[] — no open-EXTRAPOLATION citation; no PAUSE flag expected at freeze** |
| T11 | every one of the 68 `output_fields` (incl. the 8 holm subfields) **resolves in a live document emitted by the pinned `analysis/knull_v3.py`** | **PASS** (68/68) |
| T12a–g | delta-scope diff: changed = exactly {design.{independent_vars, arms_mandatory_baselines, n_planned.{item_source, prefreeze_gates_evidence, assumptions, best_comparator_rule, power}}, endpoints, hypotheses, kill, envelope, pins.{analysis_script, harness_manifest}, title, runner_constraints}; verdict_rules structurally untouched; budget caps unchanged; status DRAFT; id/supersedes/schema_version/depends_on/coverage/efficiency/analysis_plan_ref/prereg_doc unchanged; DVs/scale_rungs/seeds/sap_prng_seed/bootstrap_B/holm_family/pairing/per_arm_items unchanged | **PASS** |
| T12h | envelope ends with the byte-verbatim sentence "Two host rungs license a SIGN, not a slope."; mandatory coverage disclosure intact | **PASS** |
| T13a | frozen v1 record `knull` reproduces its `frozen_sha256` `9b2065c6…` against `frozen-index.json` | **PASS** (untouched) |
| T13b | all 14 pinned v1/v2 files (C-2 list: v1/v2 builders, linters, checker, runner, f2b runner, `analysis/knull.py`, inputs-v2 manifest/store/reports/artifact, both pinned docs) reproduce their shas; `poc/knull/inputs/` tree untouched | **PASS** |

### T3 enumeration (all 13 unique pointers → MEMBER)

From `verdict_rules`: `/gates/instrument_valid`, `/gates/bridge_kernel_lift`,
`/gates/any_aligned_arm_eligible`, `/analysis/tost_equivalent`,
`/analysis/kernel_superior_beyond_margin`, `/analysis/kernel_inferior_beyond_margin`.
From `endpoints`: `/analysis/tost_equivalent`, `/gates/bridge_kernel_lift`,
`/gates/any_aligned_arm_eligible`, `/gates/extraction_ok`, `/gates/flops_parity`,
`/analysis/holm/shuffled_low_recovery`, `/analysis/holm/f2b_form_positive`,
`/analysis/length_effect`, `/analysis/length_sensitivity`, `/analysis/per_type_breakdown`.

## 5. The freeze the coordinator will run (G-5; NOT run here)

Precondition: copy the staged record over the DRAFT — content-identical copy; the frozen hash is
computed over **canonical** JSON of the parsed record, so file formatting cannot change it:

```bash
cp poc/knull/freeze-prep/knull-v2-staged.json registry/experiments/knull-v2.json

# 1. verify, writing nothing
python3 tools/registry/prereg-freeze.py --experiment knull-v2 --agent-id coordinator-1 --dry-run

# 2. the freeze (RECOMMENDED: pin the timestamp for a pre-verifiable, byte-deterministic hash)
python3 tools/registry/prereg-freeze.py --experiment knull-v2 --agent-id coordinator-1 \
    --frozen-at 2026-07-13T00:00:00Z
```

**frozen_sha256 the coordinator will get** (computed this session with `kot_common.frozen_hash`
over the staged record stamped `frozen_by=coordinator-1`, `frozen_at=2026-07-13T00:00:00Z`,
`status`/`frozen_sha256` excluded per P2 section 1.1 — pure hash arithmetic, nothing frozen):

```
e2cf8687ca9bffaaee557793db550dbb1fbf2cdae78349a78dea9e173b928633
```

RT-15 line to post (hash-only) to the coordination issue, then note the UTC post time on d0hq:

```
prereg freeze knull-v2 frozen_sha256=e2cf8687ca9bffaaee557793db550dbb1fbf2cdae78349a78dea9e173b928633
```

Caveats, exact:
- The hash above is **conditional on those two stamps**. If the coordinator freezes WITHOUT
  `--frozen-at` (the README G-5 form), `frozen_at` = the wall-clock UTC minute and the sha WILL
  differ; the tool prints the authoritative value either way — post THAT. Any other `--agent-id`
  also changes it. And if even one byte of the staged content is edited before freezing, the sha
  moves — re-verification is then required.
- Predicted `pause_flags: []` (T10) — no open-EXTRAPOLATION citation, so no non-fatal PAUSE line
  is expected. (If one appears after future register edits, it does not block the run — guard
  conclusions, not experiments.)
- The old checklist dry-run hash `22ed0ce1…` is the SUPERSEDED three-arm record — do not post it.
- **Commit gap (coordinator, before freeze):** the B-1/B-2 outputs `poc/knull/inputs-v4/items/*.jsonl`
  (all four), `poc/knull/inputs-v4/prompt-tokens.json`, and `poc/knull/inputs-v4/stores/` exist on
  disk with exactly the pinned shas (re-verified this session) but are **git-UNTRACKED**; the
  scripts, manifest, G-3 artifact, store and `analysis/knull_v3.py` are tracked. `prereg-freeze.py`
  reads disk bytes so the freeze itself is unaffected, but the README G-5 precondition ("B-1..B-3
  landed and committed") and pin custody require committing them together with the B-4 record edit
  (this session took no git action, per its mandate).

**READY confirmation** for the coordinator's sequence: (a) copy staged → `registry/experiments/
knull-v2.json`: READY (T1–T12); (b) `--dry-run`: expected `DRY-RUN-OK` (T9 ran the tool's entire
`check_record` constraint set on the stamped staged copy, green; C-1/C-2-class pin recomputes green
today, T5b/T7/T13b); (c) freeze: READY (sha above if stamps pinned); (d) RT-15: line above;
(e) launch (kernel-of-truth-1np7, Modal, cap $60): record-side READY — remaining work is the
**runner-role** campaign wrapper per the staged `harness_manifest` (re-point to the FROZEN record +
`inputs-v4`, re-verify every pin fail-closed, 36 GPU cells incl. the 6 ASM-1086 plain-padded cells;
item_meta must carry `kernel.types`, `kernel.prompt_tokens`, `plain.prompt_tokens` from the pinned
sidecar or `knull_v3` fails closed with `KNULL_SAP_ERR_TOKEN_META`); launch with nohup+setsid and
remember `modal app stop ap-<id>` if the local client dies (standing memory). Caps unchanged:
$60 / 8 GPU-h / 24 h; planning estimate 4–6 GPU-h + ~1/5 for the padded cells — never measurements.

## 6. Governance self-check (printed, per the task instruction)

- **No registry-file edit**: `registry/` byte-untouched (T13a; git status shows only the two new
  freeze-prep files). **No freeze**: `prereg-freeze.py` never executed, dry-run included; only
  library functions were imported for verification. **No registry/*.jsonl writes. No git actions.
  No spend** ($0, CPU-only, niced).
- **Staged file + report only**: exactly `poc/knull/freeze-prep/knull-v2-staged.json` and
  `poc/knull/freeze-prep/B4-STAGING-REPORT.md` written; build/verify scratch scripts lived in /tmp.
- **Every PINNED-AT-BUILD resolved to a real sha**, each recomputed from committed bytes this
  session and cross-checked against B1-B3-DONE.md (section 1 table); T6b proves no placeholder
  remains.
- **All trip-wires checked pass/fail**: 25/25 PASS (section 4), incl. the five named in the task:
  one-primary + catch-all (T2), pointer membership enumerated (T3), SESOI kept (T4), corpus pins
  untouched + reproducing (T5), RT-14 clean + schema shape (T6/T1), custody of frozen v1 +
  `poc/knull/inputs/` + all pinned v1/v2 bytes (T13).
- **No account/handle strings**: RT-14 pattern lint zero hits over the staged hashed bytes, the
  full staged file, and this report's authored content; no identity fields present in the staged
  record (the freeze adds pseudonymous `frozen_by=coordinator-1`). The judge-family model-name
  disclosure strings ("GPT-5.6", "Haiku") follow the committed v2-record pattern and the delta's
  own replacement clause; they are product names, not accounts or handles. Engine naming: colibri
  convention respected — no engine name in either new file (one was removed from a rewritten
  assumption, disclosed in section 3 item 4).
- **Epistemic tags**: MEASURED only for recomputed/committed-byte facts; STIPULATED design choices
  cite their registered ASMs (0700–0706, 1080–1088); projections marked non-binding with their
  binding resolution named (ASM-1088 pattern). No new ASM registered by this session.
