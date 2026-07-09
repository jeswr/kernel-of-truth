#!/usr/bin/env python3
"""audit-status — list the per-experiment execution/audit ledger and flag the
experiments that still await a FABLE interpretive assessment.

Reads registry/audit-status.jsonl (one JSON object per line, schema in
docs/next/opus-execution-practices.md practice 3). Pure reader; writes nothing.

Usage:
  python3 tools/registry/audit-status.py            # full table
  python3 tools/registry/audit-status.py --pending  # only rows pending a
                                                     # Fable interpretive assessment
  python3 tools/registry/audit-status.py --json      # machine-readable dump

Exit code: 0 always on a well-formed ledger; 2 if the ledger is malformed
(fail closed — a governance ledger that does not parse is a hard error).
"""
import argparse
import json
import os
import sys

FIELDS = ("experiment_id", "executed_by", "executor_model", "codex_audited",
          "fable_interpretive_assessed", "run_log_path", "run_script_path",
          "verdict_path", "note")


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


def main():
    ap = argparse.ArgumentParser(description="List the experiment audit ledger.")
    ap.add_argument("--root", default=None)
    ap.add_argument("--pending", action="store_true",
                    help="only rows awaiting a Fable interpretive assessment")
    ap.add_argument("--json", action="store_true", help="machine-readable dump")
    args = ap.parse_args()
    root = args.root or repo_root()
    rows = load(root)

    pending = [r for r in rows
               if r.get("fable_interpretive_assessed") != "done"]
    shown = pending if args.pending else rows

    if args.json:
        print(json.dumps(shown, sort_keys=True, indent=2))
        return

    print("%-16s %-8s %-9s %-8s  %s"
          % ("experiment", "by", "codex", "fable", "note"))
    print("-" * 92)
    for r in shown:
        flag = "" if r.get("fable_interpretive_assessed") == "done" else "  <- PENDING fable-assess"
        print("%-16s %-8s %-9s %-8s%s"
              % (r["experiment_id"], r["executed_by"], r["codex_audited"],
                 r["fable_interpretive_assessed"], flag))
    print("-" * 92)
    print("%d experiment(s); %d PENDING a Fable interpretive assessment"
          % (len(rows), len(pending)))
    if not args.pending and pending:
        print("(run with --pending to list only those)")


if __name__ == "__main__":
    main()
