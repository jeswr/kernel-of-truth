# knull-v2 freeze-readiness report (pre-freeze gates d0hq G-2..G-5)

**Prepared 2026-07-13 by the Fable designer role (designer-26). $0, CPU-only. No git, registry,
freeze, spend, or launch action was taken by this session; the freeze + RT-15 belong to the
coordinator.** Feeds: `kernel-of-truth-d0hq` (pre-freeze gates) → `kernel-of-truth-1np7`
(knull GPU run, matched-FLOP retry topology, GPU AUTHORIZED, cap $60).

Record under review: `registry/experiments/knull-v2.json` (DRAFT).
Accepted control store: `poc/knull/inputs-v4/plain-authored.json` v4.0.0
(sha256 `97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2`) — maintainer issue-17
acceptance + maintainer blind style sign-off **10/10**
(`poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md`). G-1 is DONE and out of scope here.

Artifacts in this directory:

| file | what | sha256 |
|---|---|---|
| `flops_recheck_v4.py` | G-2 recompute script (pinned-methodology, fail-closed pins) | see git |
| `flops-recheck-v4.json` | G-2 FLOPs re-check artifact on the v4 store | `c150270e9f7d59220d86052874fba787a4544943259a8934bb16e2bbf7c91011` |
| `prefreeze-checklist.json` | G-4 checklist results (C-1..C-12, pass/fail per item) | see git |
| `record-delta-v4.md` | the §6 freeze delta re-stated for v4, shas prefilled | see git |

---

## VERDICT: **NOT freeze-READY** — mechanically green, substantively blocked

The DRAFT record passes **every mechanical freeze check today**
(`prereg-freeze.py --dry-run` → `DRY-RUN-OK`, zero pause flags; checklist C-3). But it still pins
the **superseded** v2 Option-A plain store and the three-arm design, and its own
`prefreeze_gates_evidence` ends "...the freeze precondition is ESCALATED to the maintainer
(ASM-0706)". Freezing those bytes would contradict the registered Option-B block (ASM-1080..1088),
the issue-17 v4 acceptance, and the style sign-off the maintainer just granted. **The tooling will
not stop this wrong freeze — do not run prereg-freeze until blockers B-1..B-4 land.**

### Blockers (exact, ordered)

- **B-1 — four-arm v4 input build** (designer/builder, $0 CPU): `build_inputs_v4.py` per
  optionb-analysis §5 (custody pattern; reads the v4 store; adds the ASM-1082 plain-padded store,
  fail-closed `KNULL_ERR_PAD_*`; segment floor ≥1 for plain/plain-padded; word band dropped for
  plain, ENFORCED for plain-padded; four item files, joint substitution, LC8 fail-closed; type mix
  re-derived and identical across arms; manifest re-pinned under `inputs-v4/`). Feasibility is
  proven: ASM-1082 padding lands 108/108 on the v4 bytes (this session's recompute).
- **B-2 — binding G-3 artifact**: `check_token_band_v4.py` on the B-1 build; band binds
  plain-padded + opaque only (ASM-1085), plain measured + disclosed.
- **B-3 — ratified SAP script**: `analysis/knull_v3.py` implementing optionb-analysis §4 — the
  ASM-1083 IUT superiority guard, `/gates/length_guard_available`, four-arm difficulty/extraction/
  flops gates, the two §4.5 descriptive reads, full §4.6 output-field list. The pinned
  `analysis/knull.py` stays byte-untouched (v1-frozen).
- **B-4 — record delta** (coordinator, registry write): apply `record-delta-v4.md` to the DRAFT.
- Then G-5 (coordinator): dry-run → freeze → RT-15 (sequence below).

---

## G-2 — FLOPs re-check: **PASS on the accepted v4 store** (with one required record fix)

Recomputed this session on committed bytes, pinned SmolLM2-135M tokenizer (sha verified), pinned
f2b `build_prompt`, identical methodology to the pinned `project_tokens_optionb.py` (which measured
v3, not the accepted v4 — that staleness was the gap G-2 had to close). Artifact:
`flops-recheck-v4.json`.

| arm (vs kernel prompt tokens) | ratio | grade | band |
|---|---|---|---|
| plain-padded (v4, ASM-1082 rule) | **0.9907** | PROJECTED | inside ±10% pre-freeze band ✓ (and ±20% run-time) |
| opaque | **1.0043** | MEASURED (v2 G-3 artifact; arm logic byte-identical) | inside ±10% ✓ |
| plain concise (v4) | **0.6628** | PROJECTED, DESCRIPTIVE | exempt by design (ASM-1085); outside ±20% as the Option-B ruling intends |

Gloss level (MEASURED): kernel 40.21 mean tokens; plain-v4 14.16 (ratio 0.3522; v3 was 0.3091).
ASM-1082 padded-arm feasibility on v4: **108/108** (102 padded, 6 degenerate no-pad; all 108 v4
definitions are single-segment — disclose in the record; v3 had 81/108).

**Matched-FLOP retry topology:** matched by construction — every verify arm runs the identical
imported f2b verify-retry machinery (k=4) on the same pinned 135M host; the verifier is the CPU
string-matcher metered at the pinned rate; only store-injected bytes differ (map D-2). With the
padded + opaque arms inside band, the kernel arm's token-matched comparators exist, so the control
IS FLOP-matched to the kernel arm under the registered scope.

**Discrepancy to fix (B-4):** the DRAFT's flops-parity gate text still binds the ±10%/±20% bands on
the *plain* arm (v2 numbers 0.948/1.004). Under ASM-1085 that scope is wrong for the accepted
design — re-scope to plain-padded/opaque. Binding resolution of all projections = the B-2 artifact
+ the run-time F0 ledger (ASM-1088). Epistemic tags used here: MEASURED for tokenizer counts on
committed bytes, everything projected is pre-freeze evidence only and never a premise.

## G-3 — pinned SAP: **BLOCKED** (complete + coherent, but for the superseded design)

What IS complete and pinned (verified this session): `analysis_plan_ref`
(08-stats-and-extrapolation.md §1.5) sha match; prereg doc sha match; exactly one primary endpoint
(TOST at ±0.05 absolute, BCa B=10000, `sap_prng_seed` 20260710, one shared resampling plan);
pre-declared comparator rule; Holm family membership pre-declared ({shuffled_low_recovery,
f2b_form_positive}); N pinned (1000 paired skeletons × 3 seeds); instrument gates with numeric
thresholds (bridge LB > +0.05; difficulty ±0.15; extraction Wilson-LB ≥ 0.90 powered at planned n;
flops ±20%); verbatim kill criterion covering all outcomes with the NULL/PASS/FAIL/
INSTRUMENT-INVALID enum mapped; exhaustive machine verdict rules ending in the INCONCLUSIVE
catch-all; every metric pointer inside the declared `output_fields` (constraint-2 dry-run green) —
the mechanical verdict path (`verdict-gen.py` pure function) is intact.

**Gap:** the pinned script `analysis/knull.py` implements the three-arm SAP. The **ratified** SAP
(ASM-1081/1083/1085/1086) adds the plain-padded arm, the IUT superiority conjunction
(`kernel_superior_beyond_margin` = [LB95_1s(D_full) > +0.05] AND [LB95_1s(D_matched) > +0.05]),
`length_guard_available` forcing, the re-scoped flops gate, and the §4.5 descriptive length reads —
none of which exists in code. **G-3 closes when B-3 + B-4 land** (no statistical redesign is
needed; the SAP itself is fully specified in registered ASMs + the pinned-at-freeze prereg doc).

## G-4 — checklists: **11 items run, 8 PASS / 3 BLOCKED** (`prefreeze-checklist.json`)

| item | status |
|---|---|
| C-1 corpus pins recompute (d-qa, d-qa-r, kernel-v0, molecules-v0) | PASS — all four reproduce exactly |
| C-2 harness + doc pins (14 shas incl. tokenizer) | PASS — all reproduce |
| C-3 prereg-freeze --dry-run (full fail-closed constraint set) | PASS mechanically (stale-design caveat) |
| C-4 accepted v4 store integrity + Option-B lint re-run | PASS (108/108) |
| C-5 maintainer gate evidence chain (issue-17 + 10/10 sign-off) | PASS (granted; bookmark caveat carried) |
| C-6 account-lint RT-14 (record hashed bytes + all knull v4/freeze-prep artifacts) | PASS — zero hits |
| C-7 ASM register (claims-check; knull ASMs 0700–0707, 1080–1088 tags lawful) | PASS |
| C-8 G-2 FLOPs re-check | PASS (artifact above) |
| C-9 binding G-3 token-band artifact on the v4 build | **BLOCKED** (B-1/B-2) |
| C-10 item files + LC8 leak checks + manifest re-pin | **BLOCKED** (B-1) |
| C-11 analysis/knull_v3.py pin | **BLOCKED** (B-3) |
| C-12 runner dry-plan smoke ($0) | PASS (v1-scope; campaign re-point is runner-role) |

## G-5 — coordinator freeze + RT-15 (NOT executed here; the exact sequence)

Preconditions: B-1, B-2, B-3 landed and committed; B-4 delta applied to
`registry/experiments/knull-v2.json` per `record-delta-v4.md`.

```bash
# 1. verify everything again, writing nothing
python3 tools/registry/prereg-freeze.py --experiment knull-v2 --agent-id coordinator-1 --dry-run

# 2. the freeze (writes the FROZEN record + frozen-index.json entry)
python3 tools/registry/prereg-freeze.py --experiment knull-v2 --agent-id coordinator-1

# 3. RT-15 external timestamp: post the tool's printed line, HASH-ONLY, to the
#    coordination issue (the standing RT-15 venue per docs/research-plan/02 §"External
#    freeze-timestamping" and 07-redteam RT-15) and note the UTC post time on d0hq:
#      "prereg freeze knull-v2 frozen_sha256=<hash from step 2>"

# 4. close the gate bead; the run bead unblocks
bd close kernel-of-truth-d0hq --reason="G-1..G-5 complete; frozen_sha256 + RT-15 posted"
```

Do **not** post the dry-run hash recorded in the checklist (`22ed0ce1…`) — the final
`frozen_sha256` differs (delta + freeze timestamp are inside the hashed bytes). If the freeze
emits a non-fatal PAUSE flag (open-EXTRAPOLATION citation), it does not block the run — guard
conclusions, not experiments.

## Launch readiness (kernel-of-truth-1np7, Modal, cap $60)

**Exists now:** mock-green CPU runner `poc/knull/runner/knull_runner.py` (dry-plan re-verified
green this session: pins verified, stores load fail-closed) which imports the f2b machinery
read-only at the pinned sha; the f2b Modal harness precedent `poc/modal/modal_f2b.py` (A100-40GB
function, pinned image, HF cache volume, 12 h timeout — the image the knull record's I-MODAL
rebuild reuses); Modal client 1.2.6 in `poc/modal/.venv`; token env files under `~/.config/kot/`
(`modal.env`, plus `modal2..4.env` / `account2..4.env` — agents hold no Modal tokens; the
coordinator/runner sources the env). Both SmolLM2 revisions are already Modal-smoked under f2b.

**Missing (runner-role work at campaign start, by design per the record's `harness_manifest`):**
the real-mode campaign wrapper (`poc/modal/modal_knull.py` on the `modal_f2b.py` pattern) that
re-points the runner at the FROZEN knull-v2 + `inputs-v4`, re-verifies every pin fail-closed, and
runs the **36** GPU cells (30 + the 6 plain-padded cells of ASM-1086). The run≠audit separation
holds: this designer identity never runs, grades, or audits the record.

**Launch shape (once the wrapper exists; single account suffices — the profile is pinned in the
`modal_f2b.py` header and docs/research-plan/06-resources.md, not repeated here):**

```bash
source ~/.config/kot/modal.env
nohup setsid poc/modal/.venv/bin/modal run poc/modal/modal_knull.py --gpu a100 &
# standing memory: if the local client dies, `modal app stop ap-<id>` — the remote task outlives it
```

Caps: $60 / 8 GPU-h / 24 h wall (tier 1); planning estimate 4–6 GPU-h, $15–30 + ~1/5 more for the
padded cells — planning numbers, never measurements.

## Governance self-check

- G-2 verified: PASS on the v4 store (artifact + one record fix named). G-3 verified: BLOCKED
  (B-3/B-4, gaps enumerated). G-4 verified: 8 PASS / 3 BLOCKED, itemized. G-5: sequence stated
  verbatim above; **not** executed.
- Freeze-READY: **NO** — precise blockers B-1..B-4 listed with owners.
- No git/registry/freeze/spend/launch action taken; frozen v1 bytes and all pinned files
  untouched; new files live only under `poc/knull/freeze-prep/` (this directory).
- Engine naming: colibri (the engine is not load-bearing for this record; no other engine name
  appears). No author/org handle in any file here (RT-14 lint run over all artifacts: zero hits).
- Epistemic tags: MEASURED / STIPULATED only, projections disclosed as pre-freeze evidence with
  their binding resolution named (ASM-1088 pattern); no new ASM registered by this session.
