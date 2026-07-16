# Molecule-S5 RE-PILOT pre-registration (REPILOT-v2.1) — repaired uptake + upgraded panel

**Status:** built & frozen 2026-07-16 (Fable, design/build only; the coordinator runs it).
Repairs the two instrument faults behind the S5-v2 pilot STOP per the approved
REPAIR-THEN-RE-PILOT fork (docs/next/analysis/molecule-s5-pilot-stop-interpretation.md;
ASM-2379). Freeze: `poc/scale/molecule-aug/FREEZE-v2.1.json` (supersedes FREEZE-v2.json for
stage 1+; every v2-pinned artefact is byte-unchanged and still verified). Selftest: **69/69
PASS** pre- and post-freeze (`s5-run/selftest/SELFTEST.md`). Nothing committed this session
per maintainer instruction.

## 1. What the pilot measured (MEASURED, pinned scorer output)

- Judged ref-bearing mol cells **4/48**; zero-ref share **0.681**; all 11 gate failures one
  class (`ERR_REF_NOT_CLOSURE_SAFE`); attempted-ref histogram dominated by
  non-referenceable ids (institution ×5, give, money, work, write, material, make,
  part-of, trustworthy). The 85-id listing delivered 65 reject-bait ids.
- F1/F2 agreement raw **0.5714**, κ **0.2038** (boot95 lower 0.033), AC1 **0.1472** (n=84)
  — genuinely poor, not the prevalence paradox (contrast calibration: raw 0.8125, κ 0.0
  degenerate, AC1 0.774).
- E2 primary −12.5pp, p=0.453, Tango95 [−29.4, +11.1] — noise-level; STOP stands
  procedurally (direction clause).

## 2. Repair 1 — closure-safe ref UPTAKE (load-bearing)

`run_s5.py gen --stage 1` (repilot mode) now runs **REJECT-AND-RESAMPLE**
(`gen_arm_resample`): a molecule record is admitted iff it passes
`validate-record-ref.mjs` + the pinned mechanical checks AND carries **≥1 reference** AND
**every** reference is closure-safe. Zero-ref records are rejected (`ERR_ZERO_REFS`) —
never silently admitted (the pilot's defect); non-closure-safe refs reject as before;
every rejected attempt is preserved (`resample-attempts/…/attempt-gate.json`) and the cell
is regenerated, up to **MAX_RESAMPLE=4** fresh attempts [STIPULATED, ASM-2401]. Exhaustion
⇒ canonical `ERR_REF_UPTAKE_EXHAUSTED`, an ITT NOT-FAITHFUL cell that counts **against**
the 80% floor. Prompt side (`s5-prompt-v2.1.md` = base + `ref-addendum-v2.md` + listing):
the listing is restricted to the **20 closure-safe ids only**, and `references: []` is
declared a hard reject with discipline rules against padded references.

**Mock evidence (MEASURED-ON-MOCK, selftest §13c, real gate + stub generator):** 24 mol
cells under deterministic schedules (admit@1 / zero-ref rejects / unsafe rejects /
exhaustion) → **22/24 = 91.7% ref-bearing admitted ≥ 80% floor**, 2 exhausted cells fail
closed with no canonical record, 46-call attempt ledger exact, only closure-safe
ref-bearing records ever admitted, fully resumable (second pass: zero calls). This proves
the LOOP; real-model uptake is precisely what the re-pilot measures under the kill below.

## 3. Repair 2 — upgraded fidelity panel

`s5-judge-fidelity-v2.1.md` (= base judge prompt + `judge-addendum-fidelity-v2.1.md`):
mandatory **criterial-feature checklist** — enumerate 2–6 features from the sense-fixing
gloss, audit each PRESENT/MISSING/CONTRADICTED against rendered material only, then a
**MECHANICAL verdict rule** (FAITHFUL iff all PRESENT, none CONTRADICTED; no holistic
override), audit recorded in `reason`/`missing`; two synthetic anchors. **F3 upgraded to
INFORMED adjudication**: on F1/F2 disagreement it re-derives the checklist from scratch,
then resolves each disputed feature seeing both anonymized reviewer audits
(`adjudication_msg_v21`; candidate stays blind). Judge **models unchanged** (F1
gpt-5.6-sol / F2 claude-opus-4-8 / F3 gpt-5.6-terra): the only stronger same-vendor
option, claude-fable-5, is a generator here and would contaminate judge independence.

**Expected agreement [STIPULATED, ASM-2402]:** F1/F2 raw ≥ 0.75, κ ≥ 0.45 (the checklist
removes the free holistic threshold that the 0.204 κ indicted; readiness-review arithmetic
puts the pilot's raw 0.57 near the two-judge chance floor). UNMEASURED until the re-pilot:
`score` reports measured raw/κ/AC1 + seeded boot95 overall, by arm, and by ref status; a
measured κ < 0.40 labels the readout **instrument-unreliable** (disclosure only — NOT a
kill clause; the binding kill is §4 verbatim and nothing else).

## 4. Re-pilot pre-registration (pinned in FREEZE-v2.1.json)

- Same fitted n=24 (`ast-pipeline/sample.json`, sha `ff5a3113…6655c`); flat cells reuse
  consensus-100 (disclosed, unchanged); scoring unchanged v2 (E2 primary, ITT,
  exact McNemar + Tango95). PROXY-PROVISIONAL: the re-pilot can **PIVOT** or **motivate a
  larger run**; it **cannot confirm** at n=24.
- **PRE-DECLARED KILL (verbatim, binding):** "PIVOT iff, after repair, EITHER ref-bearing
  molecule cells < 80% OR the E2 primary delta <= 0pp again."
- Operationalization (frozen): ref-bearing mol cell = admitted gate-clean (`s5_ok`) record
  with n_refs ≥ 1 that expands clean; denominator = ALL 48 mol cells (ITT — exhausted/
  GATE-FAIL cells count against the floor); delta = Mol-E2 − Flat-E2 in pp. Evaluated
  mechanically by `repilot_gate_eval` (unit truth table in selftest §13d, boundaries exact).
- Key pins (FREEZE-v2.1.json, all live-verified by every stage-1 verb, which ALSO
  re-verifies the untouched v2 freeze): `s5_prompt_v21_sha256 e7c56b45…53c0`,
  `s5_judge_fidelity_v21_sha256 6fa6da2e…2ec4`, `pilot_sample_sha256 ff5a3113…655c`,
  `resample_code_sha256 142aa169…9f97` (source hash of gen_arm_resample + s5_gate +
  repilot_gate_eval + adjudication_msg_v21 + the verbatim kill + policy constants).
- Working dir `s5-run/stage1-repilot/`; the superseded v2 pilot's `s5-run/stage1/` is
  untouched evidence. `gen --stage 3` refuses to run under repilot mode until the
  interleaved runner is resample-upgraded and re-pinned (fail closed, no silent policy mix).

## 5. Coordinator commands (exact; repilot mode is automatic — FREEZE-v2.1.json exists)

```bash
cd poc/scale/molecule-aug
python3 run_s5.py selftest                    # must be 69/69 PASS before spending
nice -n 10 python3 run_s5.py gen --stage 1    # mol cells, reject-and-resample (<=192 calls, expect ~60-100)
python3 run_s5.py expand --stage 1
python3 run_s5.py prep --stage 1 --instrument fidelity
for J in F1 F2 F3; do nice -n 10 python3 run_s5.py judge --stage 1 --instrument fidelity --judge $J --i-am-the-coordinator; done
python3 run_s5.py score --stage 1 --v2        # prints RE-PILOT PRE-DECLARED KILL verdict (verbatim rule)
```

Budget [ESTIMATE]: ≤192 gen + ~200–290 judge calls — same order as the pilot, inside the
priced $90–260 path. Long legs via nohup+setsid (standing E5 lesson). CORRECTNESS
verdict-word untouched either way (ASM-2379); a PIVOT kills the molecule-S5 *instrument*,
not the molecule hypothesis broadly and not any thesis verdict-word.
