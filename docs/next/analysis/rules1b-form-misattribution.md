# RULES-1-B host-validity floor failure — form mis-attribution (diagnosis + fix)

**Status: diagnosed and fixed 2026-07-12 (Fable); successor DRAFT
`registry/experiments/rules-1-c.json` (supersedes rules-1-b, frozen
`2b81375e…`), dry-run-clean; re-freeze is the coordinator's.** Companion to
`docs/next/analysis/rules1-void-degenerate-instrument.md` (the rules-1 void).
No final-phase GPU was spent: the launch gate refused fail-closed
(`ERR_GATE_PILOT: pilot acc(A5)=0.0000 below the frozen host-validity floor
0.15`).

## 1. What happened

rules-1-b carried the two-defect prompt-frame fix (direction-explicit cue,
menu moved to the task header) and a new host-validity gate. Its pilots read:

| arm | frame | pilot (n=24, seed 0) |
|-----|-------|---------------------:|
| A7 (135M + injected derivation) | fixed relation-word | 20/24 = 0.833 ✔ (floor 0.30) |
| A1 (135M alone) | fixed relation-word | 0/24 = 0.000 (no floor; chance 1/23) |
| A5 (1.7B alone, Modal A10G fp32) | fixed relation-word | **0/24 = 0.000 ✗ (floor 0.15)** |

The A5 floor was premised on "the four-times-replicated nsk1 R3 headroom
datum 0.7912 on these items".

## 2. Root cause: the 0.7912 datum is the ENTITY form, not the relation form

The nsk1 lineage measured TWO task forms on these items:

- **Form 2 (entity)**: "Who is the `<gold_rel>` of `<base>`?" → answer a
  NAME. 1.7B zero-shot **0.76** (g2d, n=100 story) replicated **0.7912**
  (bprime, n=958). THIS is the 0.7912 datum.
- **Form 1/1b (relation word)**: "How is A related to B?" → one of 23
  relation words. The nsk1-g2d assessment records it **"dead-at-floor at
  every tested host"** (1.7B 0.00–0.10).

rules-1 and rules-1-b asked the RELATION-WORD form while citing the
entity-form datum for the A5 floor — a floor no prompt frame can reach.

**Measured 2026-07-12 (pinned R3 @ `31b70e2e`, A10G fp32, runner's own
prompt builder + f2bt scorer bytes, ~$0.25 of probes):** across 8 frame
variants — as-built, no-pad, padding-above-question, chat-template,
chat+pad, story content, story+chat, and the EXACT nsk1 generation channel
(chat template + greedy 16 + first-vocab-word) — the gold relation word was
top-1 in 1/72 scorings; the host answers the ONE-HOP relation
(father/mother) or a sibling word every time; gold ranks 2–14. The same
holds at R1 (135M, CPU fp32, 5 variants, 0/30). Ruled out again: padding
placement, chat template, multi-token option-logprob normalisation (gold
words are single tokens), story-vs-facts content, generation-vs-forced-
choice channel. The FORM is the divergence.

**Entity form on the SAME stated-facts world, SAME f2bt forced-choice
scorer (pinned R3, n=12): 11/12.** (Positive control, the exact g2b story
cell: 8/12 ≈ the 0.76 datum.)

## 3. The fix (rules-1-c harness, `poc/rules-1/rules1_runner.py` + manifest)

1. **Entity-form host surface** (nsk1 g2b form 2): question
   `Who is the <gold_rel> of <base>?`; per-item **2-option forced choice**
   over the non-base lexicon surfaces (bridge + chain-top; anti-echo
   structural, matching the g2b scorer's base exclusion); answer = the
   chain-top NAME (third-party CLUTRR proof_state gold, predates the
   kernel). Direction-explicit infill cue `the {rel} of {a_name} is`; no
   option enumeration anywhere in prompt text. **Chance floor 0.5,
   disclosed everywhere.**
2. **A7 render-only** (the LM "only renders", now literally): bare derived
   fact + question + cue, no stated-facts block, no proof prose in-prompt.
   Measured at the pinned R1 (n=12): facts+proof 4/12, facts+bare 3/12
   (bridge-frequency capture — the g2d pathology), render-only+proof 7/12,
   **render-only+bare 12/12**. The proof stays in the engine payload and
   run-record ledger.
3. **Entity-form licensed rejections** (A3/c1): accept = the engine-derived
   chain-top; the functional-uniqueness ground is DROPPED (it would name
   the gold entity); range/gender ground retained; gold-leak guard now
   guards the gold NAME.
4. **Floors re-derived for chance 0.5** (`analysis/rules_1c.py`, pinned):
   `host_validity_valid := acc(A7) >= 0.85 AND acc(A5) >= 0.75`. s1 is the
   ratio-based recovery operationalisation (A1-paired lifts), so it is
   chance-floor-invariant and byte-carried.
5. **ALL arms pilot-gated**: the mandatory pre-launch pilot must cover
   every GPU arm in the launch set (rules-1-b's pilot covered A1/A7 only;
   the A5 failure surfaced post-freeze).

## 4. Pilot confirmation (fixed instrument, Modal A10G fp32, ~$0.10)

`--pilot-n 24`, seed 0, arms A1+A5+A7, PILOT-labelled end-to-end; artifacts
`poc/rules-1/results-incoming/pilot-20260712-rules1c-v2/` (rows sha
`db40193088cb…`):

| arm | entailed acc (n=24) | rules-1-b pilot | note |
|-----|--------------------:|----------------:|------|
| A5 (1.7B alone)  | **24/24 = 1.000** | 0/24 | floor 0.75 CLEARED |
| A7 (135M render-only) | **24/24 = 1.000** | 0.833 (rel-form) | floor 0.85 CLEARED |
| A1 (135M alone)  | 13/24 = 0.542 | 0/24 | chance-consistent (0.5); headroom ≤0.85 clear |

`analysis/rules_1c.py` over these rows: `host_validity_valid: true`,
`headroom_valid: true`, `separation_valid: true` (engagement null — no A3
rows in this pilot; the full-arm pilot covers it pre-launch).

Disclosed limitation: at chance 0.5 the primary lift headroom (A3−A1) is
bounded by ~0.46; the 0.05 smallest-effect-of-interest is unchanged.

## 5. Re-freeze path (coordinator)

1. Review + commit the rules-1-c harness bytes (runner, manifest,
   `analysis/rules_1c.py`) and the DRAFT record.
2. `python3 tools/registry/prereg-freeze.py --experiment rules-1-c
   --agent-id coordinator-1` (dry-run already green 2026-07-12; non-fatal
   PAUSE on open EXTRAPOLATION ASM-1134, same as rules-1-b); post the hash
   to the coordination issue (RT-15).
3. Ops amendment pins the staged-bytes manifest sha
   (`modal_rules1.py --print-manifest`).
4. Full-arm pilot (A1/A3/A5/A7/c1, `--pilot-n 24`) green vs the rules_1c
   floors, THEN `bash poc/rules-1/modal/launch_rules1b_parallel.sh --launch
   --pilot-results <dir>` — note the launcher's hardcoded floor echo (0.30/
   0.15) needs the rules-1-c floors before use.
