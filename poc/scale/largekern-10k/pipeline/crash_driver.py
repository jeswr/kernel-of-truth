#!/usr/bin/env python3
"""crash_driver.py — P5 subprocess crash-window driver (spec §6, §10.6 P5).

Run under a scratch dir with env LK_CRASH set; the process commits the job
outbox row (window (a): then SIGKILLs itself BEFORE batches.create) or lets
the mock provider accept the job (window (b): then SIGKILLs before the
returned batchId is recorded). The test harness then 'restarts' by opening a
fresh Pilot over the same durable state and running the r5 sweeper.

usage: LK_CRASH=pre_create|post_create python3 crash_driver.py <scratch_dir> <n>
(worklist.jsonl must already exist in <scratch_dir>)
"""

import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mock_batch
import orchestrator


def main():
    scratch, n = sys.argv[1], int(sys.argv[2])
    pilot = orchestrator.Pilot(
        out_dir=scratch,
        ledger_path=os.path.join(scratch, "ledger.sqlite"),
        provider_dir=os.path.join(scratch, "provider"),
        store_dir=os.path.join(scratch, "store"))
    pilot.load_worklist(os.path.join(scratch, "worklist.jsonl"), limit=n)
    members = pilot._members_for_wave(0)
    try:
        pilot.submit_job(0, 0, members)   # LK_CRASH=pre_create SIGKILLs inside
    except mock_batch.CrashInjected:
        # window (b): provider state durable, batchId never recorded — die as
        # a real client would (kill -9 semantics; no cleanup, no ledger write)
        os.kill(os.getpid(), signal.SIGKILL)
    print("no crash injected (LK_CRASH=%r)" % os.environ.get("LK_CRASH"))
    return 1


if __name__ == "__main__":
    sys.exit(main())
