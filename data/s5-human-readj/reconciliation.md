# Reconciliation rule (s5-human-readj/1) — VERBATIM, pinned

> INSTRUMENT ARTEFACT, frozen under registry/experiments/s5-human-readj.json.
> This rule is the ONLY discussion channel in the design and replaces the
> proxy panel's F3 adjudicator. It is applied exactly once, after both
> independent passes are complete and pinned. Any deviation puts the run
> off-protocol (exploratory, full stop).

**RECONCILIATION RULE [STIPULATED, verbatim, binding]:** "After BOTH
adjudicators have returned complete answer sheets for all 95 items and the
coordinator has hash-pinned both raw sheets (sha256 recorded in the run log
BEFORE any discordant item is revealed), the coordinator lists the DISCORDANT
items — every item whose two verdicts are not both FAITHFUL and not both
LOSSY; any pair containing CANNOT-SAY is discordant unless BOTH are
CANNOT-SAY. For each discordant item, in the pinned queue order, the two
adjudicators hold a structured BLIND discussion: the item text and the rubric
only; arm, provenance, cell identity, proxy verdicts, and all other items stay
hidden; no third person and no machine assistance may be consulted. Each
adjudicator states their numbered criterial-feature audit; each disputed
feature is resolved against the rendered material by citing the clause(s) that
decide it; the mechanical verdict rule (rubric Step 3) is then applied to the
agreed feature classification, and ONE consensus verdict — FAITHFUL or LOSSY —
is recorded with the agreed audit. If after discussion the adjudicators do not
agree on the feature classification, the item is recorded UNRESOLVED and
scores LOSSY (intention-to-treat, fail-closed), and is counted and disclosed.
A CONCORDANT CANNOT-SAY pair is not discussed: it scores LOSSY
(intention-to-treat) and is counted as a concordant escape, not as
UNRESOLVED. The exhausted molecule cell (conception.mol-fable,
ERR_REF_UPTAKE_EXHAUSTED) is never shown to any adjudicator and scores LOSSY
(intention-to-treat) in every analysis."

## Why fail-closed, and the pinned bias bound

UNRESOLVED→LOSSY and concordant-escape→LOSSY mirror the registered re-pilot
ITT rule (DESIGN-v2 §2: GATE-FAIL/UNJUDGED/UNRESOLVED all count NOT-FAITHFUL),
so the human channel scores the same estimand the proxy channel scored.
Fail-closed can only depress the arm with more unresolved cells, so the
analysis (pinned, `analysis/s5_human_readj.py`) mandatorily reports:

- `n_unresolved` overall and per arm (flat / mol);
- the sensitivity bound `delta_pp_unresolved_flipped` — the primary delta
  recomputed with every UNRESOLVED cell flipped to FAITHFUL (the other
  extreme). The two deltas bracket every possible resolution.

An UNRESOLVED count > 4 of 95 (>~5%) fails the instrument gate G-HRA:
the readout is INSTRUMENT-INVALID, never a hypothesis outcome.

## Sequencing (coordinator)

1. Both raw sheets complete → sha256 both files → record hashes → only then
   compute and reveal the discordant list (arm-blind: item ids + text only).
2. Run the discussions in pinned queue order; record consensus rows in a
   third sheet (`item_id, consensus, audit`), consensus ∈ {FAITHFUL, LOSSY,
   UNRESOLVED}.
3. Hand all three sheets to the pinned analysis. No verdict may be edited
   after its sheet is hashed; corrections require a fresh sheet and a fresh
   hash, disclosed in the run log.
