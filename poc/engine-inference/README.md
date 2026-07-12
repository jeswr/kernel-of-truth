# ENGINE-INF E0 — engine inference under typing (D2/D3), FREEZE-READY

Build agent: writer-4, 2026-07-12. Design:
`docs/next/design/engine-inference-under-typing.md` (ASM-1950..1967);
build operationalisations: `asm-1990-2009.json` (this dir, owner writer-4,
for central registration by the coordinator). DRAFT record:
`registry/experiments/engine-inference.json` — **prereg-freeze --dry-run =
DRY-RUN-OK** (frozen-shape verified; not frozen — the freeze is the
coordinator's).

**The question:** on items where kernel-v1's sense-split per-sense typing
and matched non-kernel sources derive DIVERGENT closures over the certified
RULES-1 engine, whose closure is correct by third-party-derived gold?
("You can break a promise (break.violate, normative), but a promise cannot
shatter into pieces (break.shatter, material); a word-level `break` over-
or under-derives.") Deterministic channel end to end: pinned bytes →
certified twin engine → string-equality scoring. **No LLM anywhere. $0.**

## Layout

| path | role |
|---|---|
| `engineinf_lib.py` | WN31 mechanical parsing, item extractor, gold (G1-G4), arm compilation, world compiler, engine adapter, scoring, divergence |
| `extract_items.py` | → `results/items.json` (212 items: 21 attested / 35 cross-pair anomaly / 156 excluded-sense refusal), `results/gold.json` (no compiler may read it — poisoned-gold canary), `results/exclusions.json` |
| `compile_arms.py` | → `arms/{dword-dom,dword-union,bwn,kshuf}/` + `arms/arm-manifest.json` (mechanical baseline sources; zero kernel authoring) |
| `engineinf_runner.py` | `--dry-plan` (cost plan, $0) or full run → `results/rows.jsonl`, `results/divergence-certificate.json` (the ASM-1851 re-activation artifact), `results/run-result.json` (double-run byte-identity) |
| `instr_pilot.py` | mandatory blocking pilot (protocol ASM-1830/1831), mode REAL, CPU, $0 → `results/instrpilot-result.json` = **PILOT-PASS-WITH-FLAGS** (flag: kernel-as-text structurally N/A) |
| `mock_validation.py` | $0 MOCK mechanics validation incl. the stdin analysis verdict path (PASS-shaped + DEFLATE-shaped synthetic rows) → `results/mock-validation.json` |
| `../../data/axioms-engineinf-v0/` | AUTHORED kernel hard module (explication-clause-cited, ASM-1952) + shared class vocabulary; experiment-scoped, dies with the experiment |
| `../../analysis/engine_inference_stdin.py` | pinned pre-registered analysis (verdict-gen stdin contract; bands PASS-affirm / FAIL-deflate / KILL-e1 / KILL-e2 verbatim from design §2.3) |

Arms: **K** (kernel) vs **D-word-dom**, **D-word-union**, **B-wn** (the
kernel-specificity decider) + **K-shuf** control + **oracle**. Primary
endpoint: K − B-wn closure-correctness on the decision-level divergent
frame restricted to decisive-gold cells (ASM-1999). Both readings are
pre-registered verbatim in the record's hypotheses (H-EI-1 kernel-win =
first kernel-specific datum; H-EI-2 = the D3(b) reframe trigger).

QUARANTINE (ASM-1990): the builder's full mechanical execution here is
harness validation only — EXPLORATORY, never quotable. The verdict comes
from verdict-gen over the frozen record's registered run.

## Coordinator freeze + run (CPU, ~$0, minutes)

```bash
# 0. register the ASM blocks (design 1950-1967 already central; build block:)
#    merge poc/engine-inference/asm-1990-2009.json rows into registry/assumptions.jsonl
# 1. verify the pilot + mock artifacts and the DRAFT record
python3 tools/registry/prereg-freeze.py --experiment engine-inference \
    --agent-id coordinator-1 --dry-run          # expect DRY-RUN-OK
# 2. FREEZE (drops --dry-run), post the frozen hash to the coordination issue (RT-15)
python3 tools/registry/prereg-freeze.py --experiment engine-inference --agent-id coordinator-1
# 3. registered run (experiment-runner role; pins verified fail-closed first)
cd poc/engine-inference && python3 engineinf_runner.py --dry-plan   # $0 plan
python3 engineinf_runner.py                                          # ~2 s CPU
# 4. log the run (log-append) with artifacts.rows_path/rows_sha256 =
#    poc/engine-inference/results/rows.jsonl + its sha; then
python3 tools/registry/verdict-gen.py --experiment engine-inference --agent-id coordinator-1
# 5. commit + push everything (build emitted no git actions)
```
