# Blockers B-1..B-3: DONE (builder session, designer-27, 2026-07-13)

**Prepared by the Fable model-code/builder role (designer-27). $0, CPU-only. No git, registry,
freeze, spend, or launch action was taken by this session; B-4 (record delta per
`record-delta-v4.md`) and G-5 (dry-run → freeze → RT-15) remain the coordinator's.**

This note appends to `README.md` in this directory: the three pre-freeze blockers it names are
built, run, and verified. Checklist items C-9, C-10, C-11 close on these artifacts.

## B-1 — four-arm v4 input build: DONE

`poc/knull/build_inputs_v4.py` (sha256 `5d15e3379adb537a9563047bf518a93f47d857dda89123c6cd8de58f6ee7bdd4`),
per optionb-analysis §5 adapted v3→v4 (custody pattern; pinned v1/v2 builders + frozen inputs
byte-untouched). Verified: deterministic (two runs, identical manifest sha); fail-closed
(tampered v4 store pin → `KNULL_ERR_STORE_PIN`; `pad_gloss` failure statuses →
`KNULL_ERR_PAD_*`; pairing/type-mix/claim-identity trip-wires enforced post-build).

- Reads the ACCEPTED v4 store (sha `97609abe…` verified fail-closed) gated by the pinned
  `lint_plain_store_v4.py` relaxed contract run at build (ASM-1080).
- ASM-1082 plain-padded store: **102 PADDED + 6 DEGENERATE_NO_PAD = 108/108** — exactly the G-2
  recompute's feasibility numbers. Segment-set equality, LC1, band landing, uniqueness all
  fail-closed (`KNULL_ERR_PAD_*`). Decision-isomorphism enforced: plain-padded re-uses the PLAIN
  arm's hash keys for claim-segment selection; post-build check proves claim items are
  byte-identical plain vs plain-padded (the only differing items are the 630 def/term items where
  the full gloss is injected; the 18 identical term-match items are the 6 degenerate concepts × 3
  term slots — disclosed, expected).
- Segment floor ≥1 for plain/plain-padded (opaque keeps ≥2); word band dropped for plain,
  ENFORCED for plain-padded vs the kernel gloss.
- Four item files, 1080 skeletons each, joint substitution, LC8 fail-closed vs all 1650 logged
  surfaces; **type mix re-derived and enforced identical across arms**:
  def-match 324 / term-match 324 / claim-true 43 / claim-false 389 (claim-true scarcity from the
  all-single-segment v4 store — disclose in the record per record-delta item 2).
- Opaque store bytes verified **identical to inputs-v2** (same GEN_SEED) — the MEASURED v2 G-3
  opaque numbers carry, as the G-2 note assumed.

| artifact | sha256 |
|---|---|
| `poc/knull/inputs-v4/manifest.json` | `ae52862d9f95c83238230ed555628318140f69f9c456eb95fc82b25fcac2ebfe` |
| `poc/knull/inputs-v4/items/kernel.jsonl` | `2543c367781e2c2d9c6e9050735eae2d33a8b4fdb7e8997f32f526ac965bed39` |
| `poc/knull/inputs-v4/items/plain.jsonl` | `3449c2fc80e67f2ef2220beae759c14192975cff2966ebe30ddebc40fa399006` |
| `poc/knull/inputs-v4/items/plain-padded.jsonl` | `721e8a027df9ec370c57523e08466e527153244feeff90ad18a9e41892dc6476` |
| `poc/knull/inputs-v4/items/opaque.jsonl` | `2effc5390a4326fd50634b5f1a677e5abb844eba05393cb57b18565799e7287f` |

Per-store per-record shas are pinned inside the manifest. No new spot-check file was emitted:
the maintainer blind style sign-off on this store already exists and is pinned
(`poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md`).

## B-2 — binding G-3 token-band artifact: DONE, **PASS**

`poc/knull/check_token_band_v4.py` (sha256 `30d87d53f0baf15013fd73fe974d37a3d137294b5db652f4e3735f183a503ad6`)
run on the B-1 build with the pinned SmolLM2-135M-Instruct tokenizer (sha verified fail-closed;
tamper test → `KNULL_ERR_G3_TOKENIZER_PIN`). Deterministic (re-run, identical artifact sha).
Band scope per ASM-1085: **BINDS plain-padded + opaque only; plain measured + disclosed.**

| arm | mean prompt tokens | ratio vs kernel | status |
|---|---|---|---|
| kernel | 110.5 | 1.000 | reference |
| plain-padded | 109.4 | **0.990** | BOUND, inside ±10% ✓ |
| opaque | 111.0 | **1.004** | BOUND, inside ±10% ✓ |
| plain (concise v4) | 73.2 | **0.662** | DESCRIPTIVE, exempt by design (ASM-1085) |

MEASURED on the built v4 item files — resolving the G-2 projections (0.9907 / 1.0043 / 0.6628)
at build level; the run-time F0 FLOPs ledger remains the final binding resolution (ASM-1088).
Margin call: n_planned 1000 ≥ 900 → TOST margin 0.05 STANDS.

| artifact | sha256 |
|---|---|
| `poc/knull/inputs-v4/g3-token-band.json` | `2a8d2f7018787a0ec4c81cfe3ee483bd441a200700ba1263561e1512a4dbafcc` |
| `poc/knull/inputs-v4/prompt-tokens.json` (per-item token sidecar) | `d9312f19a3a7338dbee1f5f7113803544e38218c30524f9d226b05edf09aa179` |

The sidecar is new: per-arm per-item prompt token counts in skeleton-rank order — the MEASURED
source for the knull_v3 `item_meta` prompt-token contract (below). Runner note: item_meta for the
SAP must now carry `kernel.types`, `kernel.prompt_tokens`, `plain.prompt_tokens` (this sidecar's
arrays); knull_v3 fails closed without them (`KNULL_SAP_ERR_TOKEN_META`).

## B-3 — ratified SAP script: DONE

`analysis/knull_v3.py` (sha256 `54528cd42485effd8a08c6472b7f1f1bff6074ad1b62cf24604b9a8dbedfa181`),
implementing optionb-analysis §4 in full:

- ASM-1083 IUT superiority guard: `kernel_superior_beyond_margin` = [LB95_1s(D_full) > +0.05]
  AND [LB95_1s(D_matched) > +0.05]; `/gates/length_guard_available` forcing (no eligible
  token-matched arm ⇒ superiority forced false); Holm family NOT resized.
- Four-arm difficulty/extraction gates; flops gate re-scoped (ASM-1085): parity binds
  `flops_ratio_plain_padded` + `flops_ratio_opaque`; `flops_ratio_plain` metered DESCRIPTIVE.
- ASM-1086 cell scope fail-closed: any plain-padded cell other than alone-R1/verify-retry-R1 →
  `KNULL_SAP_ERR_PADDED_CELL_SCOPE`.
- Both §4.5 descriptive reads: `length_effect` (paired BCa, two-sided 95%) and
  `length_sensitivity` (Spearman vs Δt from the B-2 sidecar).
- The full §4.6 output-field list is the module constant `OUTPUT_FIELDS` (copy-ready for
  `pins.analysis_script.output_fields` in the B-4 delta); the selftest resolves every pointer
  against the emitted document (freeze constraint 2 checked at build).
- Selftest green (planted covs, 9 regimes): equivalence / superiority(IUT) / inferiority /
  difficulty-gate / **length-guard-forced-false** (raw kernel win vs plain beyond margin, no
  eligible matched arm ⇒ superiority false) / shuffled-bridge / length-effect sign /
  padded-cell-scope trip-wire / token-meta trip-wire.
- All v1 machinery byte-carried (BCa bootstrap B=10000, seed 20260710, one shared resampling
  plan, TOST ±0.05, Holm family membership). **The pinned `analysis/knull.py` is byte-untouched**
  (git diff empty; sha256 `683f3e06189da0856565b1c6cd1053a9116dabaa21d65488919955458951f3bf`).

## Hand-off to the coordinator (B-4 + G-5)

The `PINNED-AT-BUILD` slots in `record-delta-v4.md` now resolve to:
manifest `ae52862d…` (item 3 G-2), G-3 artifact `2a8d2f70…` + sidecar `d9312f19…` (item 3 G-3),
builder `5d15e337…` / checker `30d87d53…` (item 7 harness_manifest),
`analysis/knull_v3.py` `54528cd4…` + its `OUTPUT_FIELDS` list (items 3 G-4 and 7).
Then G-5 exactly as sequenced in README.md. The run-bead item_meta contract change (prompt-token
arrays) is disclosed above for the runner-role campaign wrapper.

## Governance self-check

- Three scripts + outputs built; each verified deterministic (byte-identical re-runs) and
  fail-closed (store-pin, tokenizer-pin, pad-generator, cell-scope, token-meta tamper tests all
  fire). New files live only under `poc/knull/` (v4 paths), `analysis/knull_v3.py`, and this
  directory.
- No git, registry, freeze, spend, or launch action taken. Frozen v1 bytes, pinned v1/v2
  builder/checker/linter bytes, `analysis/knull.py`, and the accepted v4 store all byte-untouched
  (verified).
- Engine naming: colibri convention respected — no engine name appears in any new file (the
  engine is not load-bearing for this record). No author/org handle in any new file
  (RT-14 pattern lint run: zero hits in authored bytes; the two drafting-model-family disclosure
  strings inside `inputs-v4/manifest.json` are carried VERBATIM from the accepted, sha-pinned v4
  store's own `authoring_disclosure` — the identical pattern already in the committed v2
  manifest, and part of the C-6-linted accepted bytes).
- Epistemic tags: MEASURED for token counts/feasibility on committed bytes; STIPULATED design
  choices cite their registered ASMs (1080–1088); no new ASM registered by this session; the
  ASM-1088 binding-resolution pattern carried (run-time F0 ledger).
