# g3 — human PASS-A gold run: measured result, verdict-input, human-vs-proxy agreement

**Run date:** 2026-07-11. **Runner:** Fable experiment agent.
**Frozen record:** `registry/experiments/g3.json` (frozen_sha256 `ef9608c6…`), run FAITHFULLY: pinned analysis
`analysis/g3.py` verified on disk (sha256 `eac8fd81…`, selftest OK); materials `data/instance-descriptions/`
(200 items, id-set equality with both label sources checked fail-closed).
**QUARANTINE (ASM-0553):** this document and `poc/g3/` contain proxy-derived quantities. Do NOT expose any of
it to the g3 human annotator(s) before their remaining passes are complete.

## 1. Annotation state (MEASURED)

- Human annotator **A1, Pass A: COMPLETE** — 200/200 q1 concept judgments extracted from the returned workbook
  (Drive dump, tab `g3 - Pass A`, column `Annotator A1: q1`): **163 yes / 29 no / 8 cannot-say** (4.0%
  cannot-say, under the protocol's 5% re-examination trigger). Extraction provenance and a sheet-state anomaly
  (10 answered rows relocated above the header; flag for coordinator to confirm with the annotator) are recorded
  in `poc/g3/human-passA-a1-q1.json`.
- Human **A1 Pass B: NOT DONE**; human **A2: NOT STARTED**. The frozen two-human instrument therefore cannot yet
  be computed from human data alone. Per the weak-proxy stand-in policy (ASM-0550/ASM-0530; the task brief's
  "issue #11" rule — no in-repo issue-#11 mirror exists, flagged), the missing seats are filled by the pinned
  llmproxy-v3 labels (`data/g3-annot-llmproxy-v3/labels-proxy.jsonl`, sha256 `685ce118…` verified; judge-pA =
  GPT-5.6-Sol, judge-pB = Claude Haiku 4.5; byte-identical materials). No new judge invocation was made: the
  pinned labels ARE the proxy; a fresh run would add nondeterminism, not information.

## 2. Verdict-input (PROVISIONAL — every violation quantity rests on proxy q2)

Hybrid annotator = **human q1 (authority) x GPT-5.6 q2 (stand-in)**; cannot-say = neither violation nor
satisfaction (the protocol's own proposed rule, STIPULATED); Wilson bounds z=1.645 from the pinned script.

| Quantity | violations / n | rate | Wilson LB | Wilson UB |
|---|---|---|---|---|
| **Necessity (primary)** | 46 / 200 | 0.230 | **0.1848** | 0.2824 |
| — decisive-only sensitivity | 46 / 192 | 0.2396 | 0.1928 | 0.2937 |
| — haiku-q2 substitution | 65 / 200 | 0.325 | 0.2732 | 0.3815 |
| — pure GPT-5.6 proxy | 49 / 199 | 0.2462 | 0.1996 | 0.2997 |
| **Sufficiency (secondary)** | 18 / 200 | 0.090 | 0.0620 | 0.1290 |

Against the frozen `verdict_rules` (I do not issue the verdict — coordinator's mechanical step):

- **Necessity:** `necessity_wilson_lb 0.1848 > 0.10` — the **FAIL row matches** (kill side decidable), with
  `instrument_valid` TRUE on both n=200 mappings. The direction is **invariant** across two cross-family q2
  sources, the decisive-only mapping, the pure GPT-5.6 leg, and the frozen llmproxy-v3 verdict (FAIL-analog,
  concordant 36/195, LB 0.1433). Per the frozen kill criterion this direction means: defeasible-script stands,
  Π is lint, HS2 auto-resolves sidecar-only — **once confirmed by human Pass B**, which remains the sole
  adjudicator.
- **Sufficiency:** UB 0.1290 > 0.10 (equivalence does not survive) and LB 0.0620 ≤ 0.10 (kill not decidable) —
  the **INCONCLUSIVE band** ("buys more annotations, not a verdict").
- **Kappa gate:** hybrid-vs-haiku (independent label sources) κ = **0.525**; hybrid-vs-GPT-5.6 κ = 0.876
  (structurally inflated — shared q2; flagged). Both ≥ 0.4, so no INSTRUMENT-INVALID trip; the true two-HUMAN κ
  is still unmeasured. The decisive-only mapping (n=192 < 200) mechanically fails the n-gate — a mapping
  artifact, not an instrument finding.

Pinned-script inputs/outputs for all three mappings: `poc/g3/analysis-input-records.jsonl`,
`poc/g3/analysis-output.json`.

## 3. Human-vs-proxy agreement on q1 (MEASURED — the proxy-validation number)

| Pair | exact 3-way | decisive agree | Cohen's κ | disagreements |
|---|---|---|---|---|
| human vs **GPT-5.6-Sol** | 0.895 | 0.9372 (n=191) | **0.7561** | 12 items |
| human vs Haiku-4.5 | 0.870 | 0.9202 (n=188) | 0.7069 | 15 items |

Substantial (0.6–0.8 band) agreement on the ordinary-usage concept judgment, GPT-5.6 slightly the closer of the
pair. This **supports — it does not prove —** the GPT-5.6 stand-in for the programme legs where human gold is
absent; it validates only the q1 face of the proxy (no human q2 exists yet to validate Pass B). Disagreement item
ids and the 2x2 tables are in `poc/g3/metrics.json`.

## 4. What is still owed

1. Human A1 **Pass B** (and ideally A2 both passes) — converts every PROVISIONAL quantity above to MEASURED and
   alone licenses the real g3 verdict.
2. Coordinator: mechanical verdict-gen over `poc/g3/analysis-output.json`; decide whether the relocated-rows
   anomaly needs annotator confirmation; note the missing issue-#11 mirror.
3. Diagnostic lead for interpretation (not a conclusion): hybrid necessity violations concentrate in
   *reminder* (6/10) and *useful* (4/10); per-concept counts in `poc/g3/metrics.json`.
