#!/usr/bin/env python3
"""registry-check — the honesty lint (P2 §4 G-2/G-3, S12s). Pre-push-hook safe.

    python3 tools/registry/registry-check.py [--root <repo>]
        [--chain] [--frozen-drift] [--account-lint] [--append-only]

With no selector flags, ALL checks run. Exit 0 only if every check passes;
any violation prints a named ERR_* finding and exits 1.

Checks:
  --chain         every results-log/*.jsonl chain-verifies (prev_sha256 over the
                  previous line's exact bytes incl. newline; genesis 64 zeros;
                  seq strictly increasing from 0) and every line parses,
                  schema-validates, and (for runs) contains no derived stats.
  --frozen-drift  every id in registry/frozen-index.json has a record file whose
                  recomputed frozen hash (canonical bytes minus status +
                  frozen_sha256) equals the index entry AND the in-record
                  frozen_sha256, with status >= FROZEN.
  --account-lint  RT-14: no account-identifying material (fixed pattern list in
                  kot_common.ACCOUNT_PATTERNS) inside any hashed byte range:
                  frozen experiment records, log lines, amendments, verdicts,
                  audit records; identity fields are pseudonyms.
  --append-only   results-log/*.jsonl in the working tree must have their
                  git-HEAD content as a byte prefix (repository-level
                  append-only witness). SKIPs with a warning when git or HEAD
                  history is unavailable — the hash chain remains the primary,
                  git-independent witness.

Usable as a pre-push hook:
  ln -s ../../tools/registry/registry-check.py .git/hooks/pre-push
"""

import argparse
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

FROZEN_STATUSES = ("FROZEN", "RUNNING", "READOUT", "BUDGET-HALT", "CLOSED")


class Findings:
    def __init__(self):
        self.items = []

    def err(self, code, msg):
        self.items.append((code, msg))
        print("FAIL %s: %s" % (code, msg))

    def ok(self, msg):
        print("  ok %s" % msg)

    def warn(self, msg):
        print("WARN %s" % msg)


def check_chain(root, f):
    log_schema = None
    schema_path = os.path.join(root, "registry", "schema", "kot-log-1.json")
    if os.path.isfile(schema_path):
        with open(schema_path, "r", encoding="utf-8") as fh:
            log_schema = json.load(fh)
    logs = sorted(glob.glob(os.path.join(root, "results-log", "*.jsonl")))
    if not logs:
        f.ok("chain: no logs present")
    for path in logs:
        rel = os.path.relpath(path, root)
        try:
            records, _ = kc.read_log(path)
        except kc.KotError as e:
            f.err(e.code, str(e))
            continue
        for rec in records:
            if log_schema is not None:
                errs = kc.validate_schema(rec, log_schema)
                if errs:
                    f.err("ERR_P2_SCHEMA", "%s seq %s: %s" % (rel, rec.get("seq"), "; ".join(errs[:5])))
            if rec.get("event") == "run":
                forbidden = kc.find_forbidden_metric_keys(rec.get("metrics", {}))
                if forbidden:
                    f.err("ERR_P2_DERIVED_STAT", "%s seq %s: %s" % (rel, rec.get("seq"), ", ".join(forbidden)))
        f.ok("chain: %s (%d records)" % (rel, len(records)))


def check_frozen_drift(root, f):
    index_path = os.path.join(root, "registry", "frozen-index.json")
    if not os.path.isfile(index_path):
        f.ok("frozen-drift: no frozen-index.json yet")
        return
    with open(index_path, "r", encoding="utf-8") as fh:
        index = json.load(fh)
    for exp_id, want in sorted(index.items()):
        if exp_id.startswith("_"):
            f.ok("frozen-drift: %s (reserved metadata key, not an experiment)" % exp_id)
            continue
        rec_path = os.path.join(root, "registry", "experiments", "%s.json" % exp_id)
        if not os.path.isfile(rec_path):
            f.err("ERR_P2_FROZEN_DRIFT", "%s: indexed as frozen but registry/experiments/%s.json is missing"
                  % (exp_id, exp_id))
            continue
        with open(rec_path, "r", encoding="utf-8") as fh:
            record = json.load(fh)
        got = kc.frozen_hash(record)
        if got != want:
            f.err("ERR_P2_FROZEN_DRIFT", "%s: recomputed frozen hash %s != frozen-index %s — "
                  "frozen bytes changed" % (exp_id, got, want))
        elif record.get("frozen_sha256") != want:
            f.err("ERR_P2_FROZEN_DRIFT", "%s: in-record frozen_sha256 %r != frozen-index %s"
                  % (exp_id, record.get("frozen_sha256"), want))
        elif record.get("status") not in FROZEN_STATUSES:
            f.err("ERR_P2_FROZEN_DRIFT", "%s: indexed as frozen but status=%r" % (exp_id, record.get("status")))
        else:
            f.ok("frozen-drift: %s (%s)" % (exp_id, want[:8]))


def _lint_json_file(path, root, f, hashed_subset=None):
    rel = os.path.relpath(path, root)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            obj = json.load(fh)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        f.err("ERR_P2_IO", "%s: unparseable (%s)" % (rel, e))
        return
    try:
        kc.check_identity_fields(obj)
        scan = obj
        if hashed_subset:
            scan = {k: v for k, v in obj.items() if k not in hashed_subset}
        kc.require_no_account_strings(kc.canonical_bytes(scan), rel)
        f.ok("account-lint: %s" % rel)
    except kc.KotError as e:
        f.err(e.code, str(e))


def check_account_lint(root, f):
    groups = [
        (os.path.join(root, "registry", "experiments", "*.json"), ("status", "frozen_sha256")),
        (os.path.join(root, "registry", "verdicts", "*.json"), None),
        (os.path.join(root, "registry", "amendments", "*", "*.json"), None),
        (os.path.join(root, "registry", "audits", "*", "*.json"), None),
    ]
    any_found = False
    for pattern, hashed_subset in groups:
        for path in sorted(glob.glob(pattern)):
            any_found = True
            _lint_json_file(path, root, f, hashed_subset)
    for path in sorted(glob.glob(os.path.join(root, "results-log", "*.jsonl"))):
        any_found = True
        rel = os.path.relpath(path, root)
        with open(path, "rb") as fh:
            data = fh.read()
        try:
            kc.require_no_account_strings(data, rel)
            for line in data.splitlines():
                if line.strip():
                    kc.check_identity_fields(json.loads(line.decode("utf-8")))
            f.ok("account-lint: %s" % rel)
        except kc.KotError as e:
            f.err(e.code, str(e))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            f.err("ERR_P2_IO", "%s: unparseable (%s)" % (rel, e))
    if not any_found:
        f.ok("account-lint: nothing to scan yet")


def check_append_only(root, f):
    try:
        subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        f.warn("append-only: git/HEAD unavailable — SKIPPED (hash chain remains the primary witness)")
        return
    for path in sorted(glob.glob(os.path.join(root, "results-log", "*.jsonl"))):
        rel = os.path.relpath(path, root)
        p = subprocess.run(["git", "-C", root, "show", "HEAD:%s" % rel], capture_output=True)
        if p.returncode != 0:
            f.ok("append-only: %s (new file, not in HEAD)" % rel)
            continue
        with open(path, "rb") as fh:
            now = fh.read()
        if not now.startswith(p.stdout):
            f.err("ERR_P2_APPEND_ONLY", "%s: HEAD content is not a byte-prefix of the working copy — "
                  "log was edited, not appended" % rel)
        else:
            f.ok("append-only: %s (+%d bytes)" % (rel, len(now) - len(p.stdout)))


def main():
    ap = argparse.ArgumentParser(description="Verify registry + results-log integrity (fail-closed).")
    ap.add_argument("--root", default=None)
    ap.add_argument("--chain", action="store_true")
    ap.add_argument("--frozen-drift", action="store_true")
    ap.add_argument("--account-lint", action="store_true")
    ap.add_argument("--append-only", action="store_true")
    # pre-push hooks pass "<remote> <url>" positionals; accept and ignore them.
    ap.add_argument("hook_args", nargs="*", help=argparse.SUPPRESS)
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_all = not (args.chain or args.frozen_drift or args.account_lint or args.append_only)

    f = Findings()
    if run_all or args.chain:
        check_chain(root, f)
    if run_all or args.frozen_drift:
        check_frozen_drift(root, f)
    if run_all or args.account_lint:
        check_account_lint(root, f)
    if run_all or args.append_only:
        check_append_only(root, f)

    if f.items:
        print("registry-check: %d violation(s)" % len(f.items))
        sys.exit(1)
    print("registry-check: PASS")


if __name__ == "__main__":
    main()
