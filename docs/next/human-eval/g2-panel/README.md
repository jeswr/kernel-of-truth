# g2 / g2-import HUMAN-GOLD reconciliation package (84-slot panel, arms A0–A3)

**What this is.** The two-human blind panel that replaces the directive-#11
LLM-proxy stand-in as gold for the g2 (Π read-out soundness) and g2-import
(ONT-TYPE-G2/1 soft-typing) results. Two independent human annotators judge
blind ordinary-meaning soundness on the **same 84 frozen kernel-v0 slots**,
each rendered under all four arms (A0 hard-4-sort baseline; A1 BFO-only;
A2 +SUMO; A3 +FrameNet). Their reconciled gold is the **sole adoption
authority** (frozen g2-import envelope: "the later two-human adjudicated panel
is the sole authority for any permanent scientific adoption; a proxy GO
followed by a human-gold failure is governed by the human result").

**Who runs it.** THE MAINTAINER. The maintainer recruits the two annotators,
distributes workbooks, runs adjudication, and performs **any** gist/file
upload. The coordinator never uploads anything and never contacts annotators.

## Package contents

| file | role |
|---|---|
| `build_workbooks.py` | builds the two blind workbooks + sealed blind key (deterministic; already run — outputs committed) |
| `workbooks/annotator-H1.{xlsx,csv}`, `annotator-H2.{xlsx,csv}` | the blind workbooks (xlsx = convenience; csv = canonical pinned bytes) |
| `INSTRUCTIONS-annotator.md` | the 1-page annotator sheet (tightened hedged-modality rubric — see deviation note below) |
| `blind-key.json` | **SEALED, MAINTAINER-ONLY** — row → (arm, item) map, orders, vacuity flags. Never send any part of it to an annotator. |
| `reconcile.py` | step 1 `kappa` (agreement + blind adjudication sheet), step 2 `score` (reconciled gold + A0–A3 re-score) |
| `package-manifest.json` | sha256 pins of all inputs and outputs |

Workbook shape: 2 PRACTICE rows, then **342 blind scored rows** in a
seed-pinned per-annotator order — 322 real rows (the 336 item×arm renderings,
deduplicated where two arms render byte-identical text; the answer is copied
to every member pair at reconciliation) + 20 deranged-sort probe rows
(5 per arm, seed-pinned sample; expected "no"; instrument check only, never
gold). Columns: `n`, `row_id`, `statement`, `answer`, `reason`.

## Maintainer runbook

1. **Recruit** two independent annotators (competent everyday-English speakers;
   not project contributors; no exposure to kernel materials or any LLM-proxy
   output — quarantine per ASM-0553 pattern).
2. **Send each annotator**: their workbook (`annotator-H1.xlsx` /
   `annotator-H2.xlsx`) + `INSTRUCTIONS-annotator.md`. **Nothing else.**
   (If a gist is used to hand files over, the MAINTAINER creates it — secret
   gist, these two files only, delete after the run.)
3. **Collect** the completed workbooks. Spot-check: no blank answers, only
   yes/no/cannot-say.
4. **Step 1 — agreement + adjudication sheet:**
   ```bash
   cd docs/next/human-eval/g2-panel
   python3 reconcile.py kappa <H1-completed> <H2-completed>
   ```
   Emits `results/agreement.json` (κ 3-cat + binary, overall and per arm;
   probe false-satisfaction; practice check — fails closed if either
   annotator missed a practice item) and `results/adjudication-sheet.csv`.
5. **Blind adjudication:** the two annotators jointly re-judge each
   disagreement row (still blind — no arm labels, no provenance) and fill
   `consensus`. No consensus → write `cannot-say` (scores 0; conservative).
6. **Step 2 — gold + re-score:**
   ```bash
   python3 reconcile.py score <H1-completed> <H2-completed> results/adjudication-sheet-completed.csv
   ```
   Emits `results/human-gold-labels.jsonl`, `results/human-gold-report.{json,md}`:
   per-arm sound/84 (vacuity-zeroed, fixed denominator 84), two-sided 95%
   Wilson, exact McNemar vs the **human-rescored A0**, human-pair κ per arm,
   and a post-gold pricing of the LLM proxy against the human labels.
7. **Hand results to the coordinator** for interpretation + ASM registration.
   Do not edit any frozen record.

No openpyxl on the annotators' machines is needed (xlsx opens in
Excel/LibreOffice/Google Sheets). If the maintainer's machine lacks openpyxl,
use the CSV workbooks; `reconcile.py` ingests either.

## Binding caveats (do not lose these)

- **Rubric deviation, disclosed.** The core question is verbatim the pinned
  g2 rubric (`poc/g2/materials/prompt-template.txt`). The instruction sheet
  ADDS the guarantee-vs-default clause rule — the instrument repair for the
  κ_A3 = 0.286 stability failure on soft-hedged "Normally…/Typically…"
  renderings. The LLM-proxy judges never saw this guidance; any
  human-vs-proxy comparison must price that difference.
- **What the result can and cannot do.** Human gold is the sole adoption
  authority and governs any proxy GO (plan §7.7 last row) — but it does not
  by itself flip a frozen verdict: the g2 `n_gold ≥ 500` instrument gate is
  unattainable on this 84-item corpus for ANY annotator (ops amendment
  pending), and the g2-import κ_A3 INSTRUMENT-INVALID verdict is repaired
  only by a NEW frozen run. This package produces the gold and the honest
  estimation readout; verdict changes go through the registry.
- **Quarantine.** Annotators must never see: arm labels, `rule`/`form`/
  `subject` fields, any LLM-proxy label, `blind-key.json`, any `results/`
  file, or any statement that these items came from a derivation system or
  ontology import.
- **Denominators.** Scoring mirrors the frozen ONT-TYPE-G2/1 plan §7.3:
  sound = (gold yes) AND (non-vacuous in that arm); cannot-say/vacuous = 0;
  fixed denominator 84. A0 has no vacuity concept. A0 is **re-scored by the
  humans** (the frozen proxy 33/84 is co-reported as context only).

## Provenance

Inputs pinned in `package-manifest.json`: `poc/g2/materials/` (items,
probes, calibration, rubric), `poc/ontology-import-g2/materials/`
(arm-a1/a2/a3 renderings + probes), vacuity flags from
`poc/ontology-import-g2/labels-ontg2.jsonl` (structure only — no labels
copied). Predecessor handoff: `poc/g2/gold-rescoring-handoff.md`.
Interpretations: `docs/next/interpretations/{g2,g2-import}.md`.
Status of everything downstream of annotation: **HUMAN-GOLD** (replaces
PROVISIONAL-ON-LLM-PROXY on these 84 slots once reconciled).
