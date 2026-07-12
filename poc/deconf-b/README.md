# poc/deconf-b — DECONF/1 Stage B (P3-E-DECONF-B), FREEZE-READY package

**Status: DRAFT — nothing here is frozen, registered, or run on GPU.** Built
per docs/next/design/deconf-stageb-spec.md (the freeze-ready spec) and
DECONF.md rev-B §5. Author: Fable, experiment-engineering agent, 2026-07-11.

**Rider (verbatim, on every Stage-B sentence):** *self-authored items,
kernel-covered slice, oracle-addressed store; external adjudication removes
membership-gold circularity, not item-generation or store-addressing
circularity.* G2-class covered-slice diagnostic; BM25-only is a cheap lexical
precursor; R-1/135M only.

## Contents

| File | Role | sha256 (at authoring) |
|---|---|---|
| `stageb_runner.py` | the NEW Stage-B module (BM25 + query-fn + ERR_QUERY_LEAK + GR-D-lite loop; imports the PINNED f2b/f2bt machinery + A1 GSAVerifier, all sha-verified before import) | `dbe8c72e…` |
| `inputs/deconfb-manifest.json` | input pins + design constants | `6e840364…` |
| `modal_deconfb.py` | Modal wrapper (same image reqs as the pinned f2b image; `--print-manifest` prints pins.harness_manifest) | `15c5e2df…` |
| `power_sim.py` + `power-sim-result.json` | the §1.6 MANDATORY freeze-time simulation (seeded 20260711; GOVERNS on conflict) | `b767b649…` / `b55cddbf…` |
| `../../analysis/deconf_b.py` | pinned analysis (paired BCa B=10000 seed 20260711, TOST, Holm; `--selftest` green) | `299954de…` |
| `../../registry/experiments/deconf-b.json` | the DRAFT record (kot-reg/2, schema-VALID, account-lint ok, no frozen_sha256) | — |
| `results-incoming/20260711-201500-local-mock/` | green local mock + its analysis output (all output_fields resolve; MOCK, never measurements) | — |

**Power simulation result [DERIVED, seeded]:** empirical power at Δ=0.10,
n=333×5: **0.929 at the Holm worst-case floor α/4** (≥0.90 target ✔; normal
approx said 0.922), 0.975 with the realised Holm family, 0.797 at the
disclosed pessimistic-σ corner (spec's internal-inconsistency note applies);
TOST power at Δ=0: 0.944. `floor_meets_target: true` — no size revision.

**Mock [MEASURED mechanics, MOCK numbers]:** 333-item eval set resolves
(ERR_EVAL_N/ERR_EVAL_IDS pins hold); ERR_QUERY_LEAK byte-equality check
passes on every real pinned item; hit@j 16/16 on the mock slice; fallback
`--kernel-arm reinstate` mock gives GS-A↔kernel identity 1.0 (the A1
prediction, mechanically confirmed); analysis + verdict-rule grammar evaluate
end-to-end (mock lands INCONCLUSIVE, as synthetic numbers should).

**Byte-identity contract (PROPOSED-ASM-1108):** `poc/f2b/runner/f2b_runner.py`
stays at `b62c3a72…` (the A1 lemma anchor) and
`poc/f2b-transfer/runner/f2bt_runner.py` at `810dcbc5…` (the stage-2 staged
sha) — verified untouched; the runner fail-closes on both before import.

## EXACTLY what the coordinator must do to freeze + run (in order)

1. **Register assumptions** — append PROPOSED-ASM-1100…1109 (the deconf-stageb-spec.md §6 block, verbatim) to `registry/assumptions.jsonl` (ASM-1010…1017 are already registered; ASM-0960…0966 registered with rev-A).
2. **Decide the kernel-arm field (PROPOSED-ASM-1105)** — if the P3-E-DECONF-0/A1 registration + registered runner-role re-run have landed: keep `runner_constraints.kernel_arm = "omit"`. Else set it to `"reinstate"` (+~0.45 GPU-h worst case, still ≤3) — the runner's `--kernel-arm` flag MUST match.
3. **Freeze** — experiment-designer role: pre-freeze skeptic pass, then `python3 tools/registry/prereg-freeze.py` on `registry/experiments/deconf-b.json` (schema-valid now; all artifact pins are real digests incl. the power-sim result `b55cddbf…`; the sim is deterministic — re-running it reproduces the bytes).
4. **Reuse-check** — `python3 tools/registry/reuse-check.py check --record registry/experiments/deconf-b.json --gate`, recorded pre-spend (the reuse_overrides fresh-runs pre-commitment is the recorded decision).
5. **Ops-amend harness_manifest** — `python3 poc/deconf-b/modal_deconfb.py --print-manifest` (currently `abd4fd36b22d787bc8e89f983f4c43a59b8459d3ae4beb3f1472548573ef7574` over 163 staged files; re-print at amendment time — any staged-byte change moves it) and write the value into the frozen record's `pins.harness_manifest` placeholder by ops amendment.
6. **Runner role, Modal (image reuse per PROPOSED-ASM-1106 — no image build):**
   - `.venv/bin/modal run poc/deconf-b/modal_deconfb.py --dry-plan` ($0; worst case 2.65–2.77 GPU-h ≤ 3, ≤ ~$6 ≤ $25 ✔)
   - `.venv/bin/modal run poc/deconf-b/modal_deconfb.py --mock` (transport smoke, ~pennies)
   - `nohup setsid .venv/bin/modal run poc/deconf-b/modal_deconfb.py --gpu a100 [--kernel-arm reinstate]` — the single ≤3 GPU-h final run; `modal app stop ap-<id>` after every attached run (standing memory).
7. **Readout** — `analysis/deconf_b.py < run-records-deconfb.jsonl`, then verdict-gen (mechanical) + the cross-vendor Codex audit. Verdict-name mapping is pinned in the record: PASS=ALIGNMENT-SPECIFIC, NULL=ATTRIBUTION-COLLAPSE-AT-SCOPE (equal prominence; K-P3v2(4) input at this scope), INCONCLUSIVE=INCONCLUSIVE-UNDERPOWERED, INSTRUMENT-INVALID=INSTRUMENT-INVALID-at-B — every sentence carries the rider verbatim.

Spend stop (PROPOSED-ASM-1109): exhaustion before the primary readout =
scientific stop + salvage, no retry.
