EXPLORATORY / QUARANTINED — g2-import-v2 pre-freeze pilot diagnostics, 2026-07-12.

Context: the sanctioned Stage-P pilot run (runs/pilot-20260712/) ABORTED at
preflight-pB: judge-pB (haiku-4.5) missed hedge-calibration item cal:hedge-1
("Every bird hatches from an egg. Normally a bird can fly." expected yes, got
no) — hedge-calibration 11/12 < 12 == pilot-gate FAIL, calibration channel.
That mechanical result stands and is the result of record for this pilot.

This directory contains an EXPLORATORY diagnostic run ONLY, executed pre-freeze
at coordinator direction to answer the sizing question the pilot was built for:
does the v2 sentence-force rubric raise pilot kappa_A3 to >= 0.40 at the
operating point, and what still drives disagreement?

Mechanics: poc/ontology-import-g2-v2/run-ontg2v2.py imported as a module and
its phase_pilot() executed VERBATIM (pinned order seeds, pinned pilot manifest
items, blinding scans, validity/retry contracts, checkpointing, per-dir budget
counter) with EXACTLY ONE deviation: the preflight-pass requirement is bypassed
(the gate already failed; that failure is recorded, not overridden). Plus 4
fresh stateless repeats of cal:hedge-1 for pB (flakiness check).

These labels are instrument evidence only, may NOT be scored, may NOT seed any
frozen record, and the kappa computed here is diagnostic — the frozen v2 (or
v3) record must re-run its own Stage-P pilot from scratch.
