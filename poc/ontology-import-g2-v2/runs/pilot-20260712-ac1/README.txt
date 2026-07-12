g2-import-v2 Stage-P AC1 PILOT — 2026-07-12, coordinator-directed instrument validation.

Redesigned gate (kappa-paradox repair, docs/next/design/g2-import-v2-repair.md section 11;
registry/experiments/g2-import-v2.json sec-pilot-gate): hedge-calibration 12/12 on the
REPAIRED set (cal:hedge-1 head made analytic, PROPOSED-ASM-1688), Gwet AC1_A3 >= 0.65 over
the both-decisive pair table of the 40 pinned stratified real A3 items (pilot-manifest.json,
R3=20/R4=16/R1=4), decisive >= 36/40 per judge, hedge-flip false-sat <= 2/8 per judge on the
DOUBLED 8-probe block. Cohen kappa / PABAK / p_pos / p_neg / independence-ceiling AC1
co-reported, never gated.

Executed via the pinned harness poc/ontology-import-g2-v2/run-ontg2v2.py
(sha ce2ab5a632b2...) verbatim: preflight pA, preflight pB, pilot pA, pilot pB, pilotgate.
Record status at run time: DRAFT (pre-freeze). Purpose: validate the redesigned instrument
BEFORE the coordinator freezes and launches the full 788-call run. Pilot labels are
instrument evidence only, never scored. Runner: Fable (claude), issue kernel-of-truth-ui9t.

OUTCOME (2026-07-12): mechanical pilotgate FAIL on the calibration channel ONLY (11/12) --
a claude.ai MCP connector leak into 1/62 pB headless sessions rejected a semantically
CORRECT answer (cal:hedge-6, raw '{"answer": "no"}') under the tools==[] contract; 5/5
diagnostic repeats clean+correct (hedge6-repeats-pB.json). Every substantive instrument
channel PASSED: AC1_A3 0.6909 >= 0.65 (above the 0.6222 independence ceiling at the
measured marginals), decisive 40/40 per judge, hedge-flip false-sat 0/8 per judge,
12/12 semantically correct calibration answers. See ac1-pilot-metrics.json.
