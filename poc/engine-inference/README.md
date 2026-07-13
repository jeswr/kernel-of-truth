# ENGINE-INF E0 — engine inference under typing (D2/D3), REVISION-1/2/3 BUILD

Build agents: writer-4 (2026-07-12 original), writer-5 (2026-07-13 R1/R2/R3
rebuild). Design: `docs/next/design/engine-inference-under-typing.md`
through REVISION-3 (ASM-1950..1967 + 2100..2112 [R1] + 2113..2117 [R2] +
2120..2121 [R3]); build operationalisations: `asm-1990-2009.json` +
`asm-engineinf-build2-2135-2144.json` (this dir, for central registration
by the coordinator). DRAFT record:
`registry/experiments/engine-inference.json` (coordinator custody; needs
the §R1/§R2/§R3 registry deltas at re-pin).

**The question:** on items where kernel-v1's sense-split per-sense typing
and matched non-kernel sources derive DIVERGENT closures over the certified
RULES-1 engine, whose closure is correct by third-party-derived gold?
Co-primary decomposition [R1]: **EP-A** (sense-splitting per se — K vs its
own mechanical lemma-collapses) and **EP-B** (kernel-authored content given
splitting — K vs B-wn). Deterministic channel end to end: pinned bytes →
certified twin engine → string-equality scoring. **No LLM anywhere. $0.**

## Layout

| path | role |
|---|---|
| `engineinf_wn.py` | ENGINE-FREE core: WN31 parsing, item extractor, outcome-equivalence cell key (ASM-2106). Exists so the holdout extractor imports neither engine nor scorer (ASM-2104 custody) |
| `engineinf_lib.py` | arm compilation (incl. the matched K-lemma-dom/union collapses, ASM-2101), the 960-member C-SHUF orbit (ASM-2114/2120), world compiler, engine adapter, scoring (ASM-2116 G4 rule), divergence; re-exports engineinf_wn |
| `extract_items.py` | → `results/items.json` (212 SEEN items — exploratory-forever, ASM-2104), `results/gold.json` (no compiler may read it), `results/exclusions.json` |
| `compile_arms.py` | → `arms/{klemma-dom,klemma-union,dword-dom,dword-union,bwn}/` + `arms/arm-manifest.json` + `arms/orbit-manifest.json` (960 members, 80 distinct TBoxes, identity ≡ K). The ASM-1996 single-rotation kshuf arm is RETIRED |
| `extract_holdout.py` | SEPARATE ENGINE-FREE ENTRYPOINT → `holdout/items-h.json`, `holdout/gold-h.json`, `holdout/exclusions-h.json`, `holdout/decoy-items.json`, `holdout/holdout-manifest.json` (SemCor H1/H2/H3 + decontamination + novel-cell H* flags + the $0 KILL-e1 count). NO outcome is computed on any H item pre-freeze |
| `engineinf_runner.py` | `--dry-plan` / exploratory run / `--holdout` (the registered run). EVERY mode refuses on H-id contamination (exit 3); `--holdout` additionally refuses without the coordinator's `FREEZE-AUTHORIZED` marker (exit 4) and emits the H divergence certificates BEFORE scoring. Emits `rows*.jsonl` + `orbit-rows*.jsonl` (960-member orbit over the frame cells) |
| `instr_pilot.py` | mandatory blocking pilot RE-RUN, PC-1..PC-7 (ASM-2111) → `results/instrpilot-result.json`. Includes the PC-4' sense-tag insensitivity canary, the PC-3' orbit + A_union invariance checks, PC-6 decoys (draw/hold/cut → `results/decoy/`, quarantined), PC-7 custody demonstrations |
| `mock_validation.py` | $0 MOCK mechanics validation incl. the stdin analysis verdict path (binding-frame PASS-shaped + DEFLATE-shaped synthetic rows + synthetic orbits) → `results/mock-validation.json` |
| `../../data/axioms-engineinf-v0/` | AUTHORED kernel hard module (explication-clause-cited, ASM-1952) + shared class vocabulary |
| `../../data/semcor30/` | pinned SemCor 3.0 zip (brown1/brown2/brownv) — the confirmatory-holdout source |
| `../../analysis/engine_inference_stdin.py` | pinned pre-registered analysis (verdict-gen stdin contract): exact-census EP-A/EP-B gates, DIST-SPAN, no-net-harm, KILL-e1/e2a/e2b, C-SHUF calibrated orbit p over the orbit-invariant A_union (design §2.3 [R2]/[R3] verbatim) |

Arms: **K**, **K-lemma-dom**, **K-lemma-union** (the matched sense-split
isolators), **D-word-dom**, **D-word-union** (descriptive only), **B-wn**
(the kernel-source decider) + **oracle**; the **C-SHUF orbit** is a
960-member control-evaluation set, not an arm.

QUARANTINE (ASM-1990/2104): every execution in this dir pre-freeze is
harness validation on SEEN/decoy frames only — EXPLORATORY, never
quotable. The registered verdict comes from verdict-gen over the frozen
record's `--holdout` run on the pinned unseen items-H.

## Coordinator freeze + registered run (CPU, ~$0, minutes)

```bash
# 0. register the ASM blocks (2135-2144 build block in this dir) and apply
#    the §R1/§R2/§R3 registry deltas to registry/experiments/engine-inference.json
# 1. KILL-e1 gate: holdout/holdout-manifest.json .kill_e1 — if fired, the
#    freeze DOES NOT PROCEED (ASM-2105); extend the inventory/construction first
# 2. verify the pilot (results/instrpilot-result.json, must be
#    PILOT-PASS-WITH-FLAGS) + mock artifacts + the DRAFT record, then freeze
python3 tools/registry/prereg-freeze.py --experiment engine-inference \
    --agent-id coordinator-1 --dry-run   # then without --dry-run
# 3. authorize + run the REGISTERED holdout run
touch poc/engine-inference/FREEZE-AUTHORIZED   # the freeze marker
cd poc/engine-inference && python3 engineinf_runner.py --holdout
# 4. log the run with artifacts.{rows_path,rows_sha256,orbit_rows_path,
#    orbit_rows_sha256} = results/rows-h.jsonl + results/orbit-rows-h.jsonl
#    (+ shas); then
python3 tools/registry/verdict-gen.py --experiment engine-inference --agent-id coordinator-1
# 5. commit + push everything (build emitted no git actions)
```
