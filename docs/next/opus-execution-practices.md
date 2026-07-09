# Opus-execution practices (governing doc)

Status: BINDING for every Opus-executed experiment. Authorised by Jesse
(2026-07-09) while Fable is out of quota. Opus may EXECUTE routine experiment
work — right-size / freeze / GPU-launch / mechanical-verdict / Codex-audit —
under the five practices below. Design law is unchanged: `tools/registry` is
law; the honesty discipline binds; run-vs-audit separation stands (the
Codex / GPT-5.5 auditor is a different vendor, invoked via the `codex` CLI).

Practices (1)–(4) are recorded here verbatim-in-substance; practice (5) was
added by the Fable resource-optimization plan (bead kernel-of-truth-utq,
2026-07-09, `docs/next/resource-optimization-plan.md`), fulfilling the
maintainer's directive that the reuse mechanisms be enforced, not advisory.

## (1) Provenance / audit-trail

The Opus agent that RUNS an experiment writes a committed run-log to
`poc/<exp>/opus-runs/<UTC-timestamp>/run-log.md` recording:

- every command it ran, plus key stdout;
- the exact reproducible launch command;
- references (paths + shas) to ALL inputs and ALL outputs.

The run-log is a BACKUP so a Fable agent can audit the run later. Use
`date -u +%Y%m%dT%H%M%SZ` in bash for the timestamp (a script cannot stamp
itself).

## (2) Reproducibility

The experiment is driven by a SINGLE committed script that runs the whole
thing end-to-end with all inputs pinned (frozen record sha + corpus + model
ids) and all outputs going to declared paths (results-log + verdict). A Fable
agent must be able to re-run that one script and audit inputs -> outputs. For
f2b-replicate the script is `poc/f2/run-f2b-replicate.sh`.

## (3) Audit-tracking

`registry/audit-status.jsonl` carries one JSON line per experiment:

```
{experiment_id, executed_by:"opus"|"fable", executor_model,
 codex_audited:"CONFIRM"|"REFUTE"|"pending"|"n/a",
 fable_interpretive_assessed:"pending"|"done",
 run_log_path, run_script_path, verdict_path, note}
```

This tracks which experiments have — and have NOT — had a FABLE interpretive
assessment. `tools/registry/audit-status.py` lists the experiments and flags
those still awaiting a Fable interpretive assessment.

## (4) No conclusive analysis by Opus

An Opus agent NEVER writes, saves, or commits a conclusive interpretation of an
outcome. Two outputs ARE allowed because they are deterministic or
cross-vendor, not an Opus analysis:

- the mechanical verdict-gen output (a pure function of the frozen rules over
  the run records);
- the Codex / GPT-5.5 cross-vendor audit.

The INTERPRETIVE assessment — what the outcome MEANS, the kill-chain read, any
EXTRAPOLATION -> MEASURED promotion, the kot-assess narrative — WAITS for Fable
and is marked pending. Opus reports only the mechanical numbers and the
pre-declared gate pass/fails (which are pure functions), never a narrative
conclusion.

## (5) Pre-spend reuse gate (BINDING — revision-1, post-Codex-audit)

Before ANY GPU/paid launch, the Runner runs the gate — `--gate` is MANDATORY
on BOTH forms (without it the tool is discovery-only and licenses nothing):

```
python3 tools/registry/reuse-check.py check --record registry/experiments/<id>.json --gate
python3 tools/registry/reuse-check.py check --arm <arm> --rung <rung> [--corpus <c>] --gate
```

and records the full output in the run-log. Exit 3 = STOP, fail closed: a
declared cell is already logged at identical or unproven-different pins with
no frozen reuse decision (cells at PROVABLY different pins do not block; the
predicate is the same one `prereg-freeze` refuses with
`ERR_P2_REUSE_COLLISION`, derived live from `results-log/`). The only lawful
responses are FROZEN-RECORD surfaces, never a run-log or chat note: a
kot-reg/2 `reused_from` block satisfying RC-1..RC-8
(`docs/next/resource-optimization-plan.md` §3.3, revision-1), a frozen
`reuse_overrides` entry (deliberate re-run, machine-recorded reason), or
shrinking the run. Whether logged data may serve as the new record's own arm
output is governed by the RC conditions and adjudicated at FREEZE by the
machinery — the Opus agent never adjudicates it (authoring a reuse block is
Fable design work); Opus's duty is to RUN the gated check, RECORD it, STOP on
exit 3, and — when a frozen record does declare `reused_from` — append the
`event:"reuse"` witness via `log-append.py` before `verdict-gen` (which
refuses consumption without the witness, without maintainer ratification of
the ruling, or on any RC re-verification failure). After every final-phase
append, the Runner re-runs `reuse-check.py build` so
`registry/artifact-ledger.jsonl` stays a current pure-function inventory
(the gates themselves never trust the committed ledger — they re-derive).

## Scope note

A reset-correct-refreeze (design right-size) is lawful for a record that is
NOT GNG-0-signed and has NO final-phase run in its results-log (the P-9 cutoff
is not crossed): reset to DRAFT, correct, re-freeze through `prereg-freeze`,
and log the correction under `registry/corrections/<exp>/`. This is a
pre-registration correction, not a post-hoc amendment.
