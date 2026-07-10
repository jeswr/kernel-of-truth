#!/usr/bin/env python3
"""audit-status — list the per-experiment execution/audit ledger and flag the
experiments that still await a FABLE interpretive assessment.

Reads registry/audit-status.jsonl (one JSON object per line, schema in
docs/next/opus-execution-practices.md practice 3). Pure reader; writes nothing.

Run-STATE is DERIVED from registry ground truth, not trusted from the note text
(design-claims-envelope-corrections.md §4): for each ledger id the tool reads
registry/experiments/<id>.json (status), results-log/<id>.jsonl (a phase:"final"
line = ran) and registry/verdicts/<id>.json (verdicted), so FROZEN-but-UNRUN,
DRAFT, RUN-AWAITING-VERDICT and VERDICTED rows are visibly distinct and a
verdicted experiment can never silently miss the ledger.

Usage:
  python3 tools/registry/audit-status.py            # full table
  python3 tools/registry/audit-status.py --pending  # only rows genuinely
                                                     # pending a Fable assessment
                                                     # (state==VERDICTED, fable==pending)
  python3 tools/registry/audit-status.py --json      # machine-readable dump
                                                     # (each row gains derived_state)

Exit code: 0 on a well-formed, self-consistent ledger; 2 if the ledger is
malformed OR a fail-closed governance lint fires (fail closed — a governance
ledger that does not parse or is internally inconsistent is a hard error).
"""
import argparse
import glob
import json
import os
import sys

FIELDS = ("experiment_id", "executed_by", "executor_model", "codex_audited",
          "fable_interpretive_assessed", "run_log_path", "run_script_path",
          "verdict_path", "note")

# Statuses that count as "frozen" for run-state derivation and ledger coverage
# (mirrors tools/registry/registry-check.py FROZEN_STATUSES).
FROZEN_STATUSES = ("FROZEN", "RUNNING", "READOUT", "BUDGET-HALT", "CLOSED")


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", ".."))


def load(root):
    path = os.path.join(root, "registry", "audit-status.jsonl")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                print("ERR_AUDIT_STATUS_PARSE: line %d: %s" % (i, e),
                      file=sys.stderr)
                sys.exit(2)
            missing = [k for k in FIELDS if k not in row]
            if missing:
                print("ERR_AUDIT_STATUS_SCHEMA: %s missing %s"
                      % (row.get("experiment_id", "line %d" % i),
                         ", ".join(missing)), file=sys.stderr)
                sys.exit(2)
            rows.append(row)
    return rows


def experiment_status(root, eid):
    """The `status` field of registry/experiments/<id>.json, or None if the
    record is missing/unreadable."""
    p = os.path.join(root, "registry", "experiments", "%s.json" % eid)
    if not os.path.isfile(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh).get("status")
    except (OSError, json.JSONDecodeError):
        return None


def has_verdict(root, eid):
    return os.path.isfile(os.path.join(root, "registry", "verdicts", "%s.json" % eid))


def has_final_run(root, eid):
    """True iff results-log/<id>.jsonl exists and has >=1 phase:"final" line."""
    p = os.path.join(root, "results-log", "%s.jsonl" % eid)
    if not os.path.isfile(p):
        return False
    try:
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    if json.loads(line).get("phase") == "final":
                        return True
                except json.JSONDecodeError:
                    continue
    except OSError:
        return False
    return False


def derive_state(root, eid):
    """Pure read of registry ground truth -> one derived run-state.

    VERDICTED > RUN-AWAITING-VERDICT > FROZEN-UNRUN > DRAFT; UNKNOWN when the
    experiment record is missing or carries an unrecognised status (lint error).
    """
    status = experiment_status(root, eid)
    if has_verdict(root, eid):
        return "VERDICTED"
    if has_final_run(root, eid):
        return "RUN-AWAITING-VERDICT"
    if status in FROZEN_STATUSES:
        return "FROZEN-UNRUN"
    if status == "DRAFT":
        return "DRAFT"
    return "UNKNOWN"


def flag_for(state, fa):
    if state == "VERDICTED":
        return "  <- PENDING fable-assess" if fa == "pending" else ""
    if state == "FROZEN-UNRUN":
        return "  (frozen-unrun)"
    if state == "DRAFT":
        return "  (draft)"
    if state == "RUN-AWAITING-VERDICT":
        return "  (run-awaiting-verdict)"
    return "  (%s)" % state.lower()


def ledger_coverage(root, rows):
    """Frozen or verdicted experiment records with no ledger row.

    Returns (missing_verdicted, missing_frozen_only): ids with a verdict file
    but no row (hard, exit-2) and frozen-unrun ids with no row (warning).
    """
    ledger_ids = {r["experiment_id"] for r in rows}
    exp_ids = {os.path.basename(p)[:-len(".json")]
               for p in glob.glob(os.path.join(root, "registry", "experiments", "*.json"))}
    frozen_ids = {e for e in exp_ids if experiment_status(root, e) in FROZEN_STATUSES}
    verdict_ids = {os.path.basename(p)[:-len(".json")]
                   for p in glob.glob(os.path.join(root, "registry", "verdicts", "*.json"))}
    missing = sorted((frozen_ids | verdict_ids) - ledger_ids)
    missing_verdicted = [e for e in missing if e in verdict_ids]
    missing_frozen_only = [e for e in missing if e not in verdict_ids]
    return missing_verdicted, missing_frozen_only


def main():
    ap = argparse.ArgumentParser(description="List the experiment audit ledger.")
    ap.add_argument("--root", default=None)
    ap.add_argument("--pending", action="store_true",
                    help="only rows genuinely awaiting a Fable interpretive "
                         "assessment (state==VERDICTED and fable==pending)")
    ap.add_argument("--json", action="store_true", help="machine-readable dump")
    args = ap.parse_args()
    root = args.root or repo_root()
    rows = load(root)

    # Attach the derived state to every row (pure reads, no writes).
    states = {r["experiment_id"]: derive_state(root, r["experiment_id"]) for r in rows}

    # ---- Fail-closed governance lints (exit 2), matching the tool's ethos. ----
    errors = []
    warnings = []
    for r in rows:
        eid = r["experiment_id"]
        state = states[eid]
        fa = r.get("fable_interpretive_assessed")
        vpath = r.get("verdict_path")
        vfile = has_verdict(root, eid)
        if state == "UNKNOWN":
            errors.append(("ERR_AUDIT_STATE_UNKNOWN_RECORD",
                           "%s: no experiment record (or unrecognised status) — cannot derive run-state"
                           % eid))
        if fa == "pending" and state != "VERDICTED":
            errors.append(("ERR_AUDIT_STATE_PENDING_NO_VERDICT",
                           "%s: fable_interpretive_assessed==pending but derived state is %s (no verdict)"
                           % (eid, state)))
        if state == "VERDICTED" and fa not in ("pending", "done"):
            errors.append(("ERR_AUDIT_STATE_VERDICT_UNTRACKED",
                           "%s: derived state VERDICTED but fable_interpretive_assessed==%r (want pending/done)"
                           % (eid, fa)))
        if vfile and not vpath:
            errors.append(("ERR_AUDIT_VERDICT_PATH_DRIFT",
                           "%s: verdict_path is null but registry/verdicts/%s.json exists" % (eid, eid)))
        if vpath and not vfile:
            errors.append(("ERR_AUDIT_VERDICT_PATH_DRIFT",
                           "%s: verdict_path is set but registry/verdicts/%s.json is absent" % (eid, eid)))

    missing_verdicted, missing_frozen_only = ledger_coverage(root, rows)
    for eid in missing_verdicted:
        errors.append(("ERR_AUDIT_LEDGER_MISSING_VERDICTED",
                       "%s: registry/verdicts/%s.json exists but there is no audit-status ledger row"
                       % (eid, eid)))
    for eid in missing_frozen_only:
        warnings.append("%s: FROZEN experiment record with no ledger row (frozen-unrun; add a row)" % eid)

    pending = [r for r in rows
               if states[r["experiment_id"]] == "VERDICTED"
               and r.get("fable_interpretive_assessed") == "pending"]
    shown = pending if args.pending else rows

    if args.json:
        out = [dict(r, derived_state=states[r["experiment_id"]]) for r in shown]
        print(json.dumps(out, sort_keys=True, indent=2))
        # Even in --json mode, governance lints fail closed.
        for code, msg in errors:
            print("%s: %s" % (code, msg), file=sys.stderr)
        if errors:
            sys.exit(2)
        return

    print("%-16s %-21s %-8s %-9s %-8s  %s"
          % ("experiment", "state", "by", "codex", "fable", "note"))
    print("-" * 100)
    for r in shown:
        eid = r["experiment_id"]
        state = states[eid]
        fa = r.get("fable_interpretive_assessed")
        print("%-16s %-21s %-8s %-9s %-8s%s"
              % (eid, state, r["executed_by"], r["codex_audited"], fa, flag_for(state, fa)))
    print("-" * 100)

    verdicted = [r for r in rows if states[r["experiment_id"]] == "VERDICTED"]
    assessed = [r for r in verdicted if r.get("fable_interpretive_assessed") == "done"]
    run_await = [r for r in rows if states[r["experiment_id"]] == "RUN-AWAITING-VERDICT"]
    frozen_unrun = [r for r in rows if states[r["experiment_id"]] == "FROZEN-UNRUN"]
    draft = [r for r in rows if states[r["experiment_id"]] == "DRAFT"]
    unknown = [r for r in rows if states[r["experiment_id"]] == "UNKNOWN"]
    summary = ("%d row(s): %d verdicted (%d assessed, %d pending), "
               "%d run-awaiting-verdict, %d frozen-unrun, %d draft"
               % (len(rows), len(verdicted), len(assessed), len(pending),
                  len(run_await), len(frozen_unrun), len(draft)))
    if unknown:
        summary += ", %d unknown" % len(unknown)
    print(summary)

    # Ledger-coverage line: ALWAYS printed.
    n_missing = len(missing_verdicted) + len(missing_frozen_only)
    if n_missing == 0:
        print("ledger-coverage: every frozen/verdicted experiment record has a ledger row")
    else:
        parts = []
        if missing_verdicted:
            parts.append("verdicted-with-no-row: %s" % ", ".join(missing_verdicted))
        if missing_frozen_only:
            parts.append("frozen-unrun-with-no-row: %s" % ", ".join(missing_frozen_only))
        print("ledger-coverage: %d frozen/verdicted record(s) missing a ledger row (%s)"
              % (n_missing, "; ".join(parts)))

    for w in warnings:
        print("WARN %s" % w)
    for code, msg in errors:
        print("%s: %s" % (code, msg), file=sys.stderr)

    if not args.pending and pending:
        print("(run with --pending to list only those)")

    if errors:
        sys.exit(2)


if __name__ == "__main__":
    main()
