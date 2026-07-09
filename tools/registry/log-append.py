#!/usr/bin/env python3
"""log-append — the ONLY writer to results-log/<id>.jsonl (P2 §2, S11s).

    python3 tools/registry/log-append.py --experiment <id> --agent-id runner-1 \
        --record <partial.json | -> [--root <repo>] [--ts 2026-07-11T09:14:12Z]

The caller supplies the record BODY (event, phase, config, metrics, cost,
artifacts, exit, error, prereg_hash, ...). The tool stamps what the caller may
never set: `seq` (strictly increasing from 0), `prev_sha256` (sha256 of the
previous line's exact bytes, incl. its newline; genesis = 64 zeros), `ts`
(UTC, unless overridden for tests), `runner` (from --agent-id), and
`schema_version`. It then chain-verifies the whole existing file, validates
the stamped record, and appends one canonical-JSON line.

Fail-closed refusals:
  ERR_P2_CHAIN            existing log fails chain verification — nothing is appended
  ERR_P2_SCHEMA           record does not validate against kot-log/1, or an
                          event-conditional requirement is missing
  ERR_P2_NOT_FROZEN       experiment absent from registry/frozen-index.json
  ERR_P2_PREREG_HASH      record's prereg_hash != frozen_sha256 in the index (G-1)
  ERR_P2_DERIVED_STAT     metrics contain derived/verdict-adjacent statistics
                          (p-values, effect sizes, CIs, TOST/Holm outputs, ...) — §2.4
  ERR_P2_STAMPED_FIELD    caller tried to supply seq/prev_sha256/ts/runner
  ERR_P2_SUPERSEDE_OK     supersede targets a successful run (exit=="ok") —
                          you cannot re-roll results you don't like
  ERR_P2_ACCOUNT_IN_RECORD  account-identifying material in the line bytes (RT-14)
  ERR_P2_REUSE_*          event:"reuse" witness fails the D9 checks: ruling not
                          maintainer-ratified (ERR_P2_REUSE_UNRATIFIED), no
                          matching frozen reused_from block
                          (ERR_P2_REUSE_UNDECLARED), or the witnessed seqs /
                          row_hashes do not equal the re-verified producer row
                          set (ERR_P2_REUSE_ROWS / ERR_P2_REUSE_PRODUCER)

Minimal-spine simplification (documented): P2's status machine (refuse
phase:"final" unless status is RUNNING) is reduced to "the experiment is
FROZEN and the prereg hash matches" — the status-event index
(registry/status.json) is not built yet. Defence in depth is unchanged:
verdict-gen re-filters eligibility.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

STAMPED = ("seq", "prev_sha256", "ts", "runner", "schema_version")
RUN_REQUIRED = ("phase", "config", "metrics", "exit")


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def append_record(root, experiment, agent_id, body, ts=None):
    """Core append path (importable by verdict-gen for the unblind line).

    Returns the stamped record. Raises kc.KotError on any refusal.
    """
    kc.require_pseudonym(agent_id, "--agent-id")
    for k in STAMPED:
        if k in body:
            raise kc.KotError("ERR_P2_STAMPED_FIELD", "%r is tooling-stamped and may not be supplied" % k)

    index_path = os.path.join(root, "registry", "frozen-index.json")
    if not os.path.isfile(index_path):
        raise kc.KotError("ERR_P2_NOT_FROZEN", "registry/frozen-index.json does not exist")
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    if experiment not in index:
        raise kc.KotError("ERR_P2_NOT_FROZEN", "%s is not FROZEN (absent from frozen-index.json); "
                          "nothing run pre-freeze can feed a verdict (G-1)" % experiment)
    if body.get("prereg_hash") != index[experiment]:
        raise kc.KotError("ERR_P2_PREREG_HASH", "record prereg_hash %r != frozen_sha256 %s (G-1)"
                          % (body.get("prereg_hash"), index[experiment]))

    log_path = os.path.join(root, "results-log", "%s.jsonl" % experiment)
    records, raw_lines = kc.read_log(log_path)  # raises ERR_P2_CHAIN on tamper

    record = dict(body)
    record["schema_version"] = "kot-log/1"
    record["experiment"] = experiment
    record["seq"] = len(records)
    record["prev_sha256"] = kc.sha256_hex(raw_lines[-1]) if raw_lines else kc.GENESIS
    record["ts"] = ts or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    record["runner"] = agent_id

    schema_path = os.path.join(root, "registry", "schema", "kot-log-1.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    errs = kc.validate_schema(record, schema)
    if errs:
        raise kc.KotError("ERR_P2_SCHEMA", "; ".join(errs[:10]))

    event = record["event"]
    if event == "run":
        missing = [k for k in RUN_REQUIRED if k not in record]
        if missing:
            raise kc.KotError("ERR_P2_SCHEMA", "run record missing: %s" % ", ".join(missing))
        forbidden = kc.find_forbidden_metric_keys(record["metrics"])
        if forbidden:
            raise kc.KotError(
                "ERR_P2_DERIVED_STAT",
                "raw run metrics may not contain derived statistics (P2 §2.4): %s" % ", ".join(forbidden),
            )
        # config_sha256 is derivable; stamp it if absent, verify it if present.
        want = kc.canonical_sha256(record["config"])
        if record.setdefault("config_sha256", want) != want:
            raise kc.KotError("ERR_P2_SCHEMA", "config_sha256 does not match canonical hash of config")
    elif event == "reuse":
        # D9 (resource-optimization-plan.md §3 revision-1): the RC-6 in-chain
        # witness that another record's logged rows are consumed. Lawful ONLY
        # when (a) the reuse ruling is maintainer-ratified, (b) the FROZEN
        # consumer record is kot-reg/2 and declares a reused_from block for
        # this producer, and (c) the witnessed seqs/row_hashes equal the
        # block's verified row set RIGHT NOW (producer chain re-verified).
        witness = record.get("reuse")
        if not isinstance(witness, dict):
            raise kc.KotError("ERR_P2_SCHEMA", "reuse event requires a reuse block")
        kc.require_reuse_ratified(root, "appending a reuse witness line")
        rec_path = os.path.join(root, "registry", "experiments", "%s.json" % experiment)
        with open(rec_path, "r", encoding="utf-8") as f:
            frozen_record = json.load(f)
        blocks = [b for b in frozen_record.get("reused_from") or []
                  if b.get("producer") == witness.get("producer")
                  and b.get("producer_frozen_sha256") == witness.get("producer_frozen_sha256")]
        if not blocks:
            raise kc.KotError("ERR_P2_REUSE_UNDECLARED",
                              "no reused_from block in the frozen record matches producer %r @ %r — "
                              "a reuse witness may only restate a frozen declaration"
                              % (witness.get("producer"), witness.get("producer_frozen_sha256")))
        block = blocks[0]
        _rows, seqs = kc.verify_reuse_block(root, frozen_record, block, mode="append")
        if sorted(witness.get("seqs", [])) != seqs:
            raise kc.KotError("ERR_P2_REUSE_ROWS",
                              "witness seqs %s != verified matching row set %s"
                              % (sorted(witness.get("seqs", [])), seqs))
        raws = {rec["seq"]: raw for rec, raw in _rows}
        want = [kc.sha256_hex(raws[s]) for s in witness.get("seqs", [])]
        if witness.get("row_hashes") != want:
            raise kc.KotError("ERR_P2_REUSE_ROWS",
                              "witness row_hashes do not match the producer log's exact line bytes")
    elif event == "supersede":
        if "target_seq" not in record or "reason" not in record:
            raise kc.KotError("ERR_P2_SCHEMA", "supersede requires target_seq and reason")
        t = record["target_seq"]
        if t >= len(records):
            raise kc.KotError("ERR_P2_SCHEMA", "supersede target_seq %d does not exist" % t)
        target = records[t]
        if target.get("event") != "run":
            raise kc.KotError("ERR_P2_SCHEMA", "supersede target seq %d is not a run record" % t)
        if target.get("exit") == "ok":
            raise kc.KotError("ERR_P2_SUPERSEDE_OK",
                              "supersede is valid only when the target's exit != \"ok\" (P2 §2.2)")

    kc.check_identity_fields(record)
    line = (kc.canonical_dumps(record) + "\n").encode("utf-8")
    kc.require_no_account_strings(line, "log line bytes")

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "ab") as f:
        f.write(line)
    return record


def main():
    ap = argparse.ArgumentParser(description="Append one record to the hash-chained results log (fail-closed).")
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--agent-id", required=True, help="pseudonymous identity, e.g. runner-1")
    ap.add_argument("--record", required=True, help="path to partial record JSON, or - for stdin")
    ap.add_argument("--root", default=None)
    ap.add_argument("--ts", default=None, help="UTC timestamp override (tests/determinism)")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        if args.record == "-":
            body = json.load(sys.stdin)
        else:
            with open(args.record, "r", encoding="utf-8") as f:
                body = json.load(f)
        rec = append_record(root, args.experiment, args.agent_id, body, ts=args.ts)
        print(kc.canonical_dumps(rec))
    except kc.KotError as e:
        fail(e.code, str(e).split(": ", 1)[1])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        fail("ERR_P2_IO", str(e))


if __name__ == "__main__":
    main()
