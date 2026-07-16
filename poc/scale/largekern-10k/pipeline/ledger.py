#!/usr/bin/env python3
"""ledger.py — components 3+4 core: the transactional SQLite ledger (spec §6.1)
and the ATOMIC pre-submit worst-case budget reservation (spec §10.2, ASM-2473).

Store: SQLite, WAL mode — transactional, single-file (§6.1; correct for this
box's 2 shared cores). draft-ledger.jsonl is a derived, append-only PASSIVE
export for audit (DB authoritative, JSONL passive — the beads architecture).

Row identity: primary key (conceptId, conceptVersion); immutable versionHash;
lookups key on the PK only; a computed-vs-stored versionHash mismatch FAILS
CLOSED (ERR_VERSION_DRIFT) — no silent redraft under a drifted contract.

Row states: CLAIMED -> SUBMITTED(batchId) -> COMPLETED(outcome) with outcomes
ACCEPTED | QUARANTINED(code) [terminal content rejection] | PROVIDER_FAILED
[retryable §10.4]; plus FROZEN (irreversible, §9.3 — never enters the 10k).

Job outbox (§6, r5): {jobKey = "kv1d-job-" + sha256(wave ‖ attempt ‖ sorted
member idempotencyKeys)[:24], wave, attempt, state, memberCount, worstCaseUSD,
inputFileSha256, ts}, committed BEFORE batches.create; JOB_PENDING ->
JOB_SUBMITTED(batchId) -> JOB_SETTLED (reservation remainder released).

Budget (§10.2): one transaction (BEGIN IMMEDIATE) checks
spentUSD + reservedUSD + newReservation <= $500.00 and debits the reservation;
failure => ERR_BUDGET_RESERVE, the submission does not happen. Unreserved
liability cannot exist. On settlement the actual cost is written to spentUSD
and the unused remainder released in the same transaction.
"""

import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import PipelineError

ROW_STATES = ("CLAIMED", "SUBMITTED", "COMPLETED", "FROZEN")
OUTCOMES = ("ACCEPTED", "QUARANTINED", "PROVIDER_FAILED")
JOB_STATES = ("JOB_PENDING", "JOB_SUBMITTED", "JOB_SETTLED")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS rows (
  conceptId TEXT NOT NULL,
  conceptVersion INTEGER NOT NULL,
  versionHash TEXT NOT NULL,
  idempotencyKey TEXT NOT NULL UNIQUE,
  state TEXT NOT NULL,
  outcome TEXT,
  quarantineCode TEXT,
  wave INTEGER NOT NULL DEFAULT 0,
  providerAttempts INTEGER NOT NULL DEFAULT 0,
  repairCalls INTEGER NOT NULL DEFAULT 0,
  batchId TEXT,
  requestId TEXT,
  responseSha256 TEXT,
  usageJson TEXT,
  costUSD REAL NOT NULL DEFAULT 0,
  owner TEXT NOT NULL,
  ts REAL NOT NULL,
  supersedes TEXT,
  PRIMARY KEY (conceptId, conceptVersion)
);
CREATE TABLE IF NOT EXISTS jobs (
  jobKey TEXT PRIMARY KEY,
  wave INTEGER NOT NULL,
  attempt INTEGER NOT NULL,
  state TEXT NOT NULL,
  memberCount INTEGER NOT NULL,
  worstCaseUSD REAL NOT NULL,
  inputFileSha256 TEXT NOT NULL,
  inputFileRef TEXT,
  batchId TEXT,
  settledUSD REAL,
  ts REAL NOT NULL,
  settledTs REAL
);
CREATE TABLE IF NOT EXISTS budget (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  capUSD REAL NOT NULL,
  spentUSD REAL NOT NULL DEFAULT 0,
  reservedUSD REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
);
"""


class Ledger(object):
    def __init__(self, path=None, cap_usd=None):
        self.path = path or common.LEDGER_PATH
        d = os.path.dirname(os.path.abspath(self.path))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        self.db = sqlite3.connect(self.path)
        self.db.isolation_level = None            # explicit BEGIN IMMEDIATE only
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(_SCHEMA)
        cur = self.db.execute("SELECT capUSD FROM budget WHERE id=1")
        row = cur.fetchone()
        if row is None:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute("INSERT INTO budget (id, capUSD, spentUSD, reservedUSD) VALUES (1, ?, 0, 0)",
                            (cap_usd if cap_usd is not None else common.BUDGET_CAP_USD,))
            self.db.execute("COMMIT")
        elif cap_usd is not None and abs(row[0] - cap_usd) > 1e-9:
            raise PipelineError("ERR_BUDGET_RESERVE",
                                "ledger cap %.2f != requested %.2f (cap is frozen)" % (row[0], cap_usd))

    # ------------------------------------------------------------- row outbox

    def claim_row(self, concept_id, concept_version, version_hash, idem_key, owner="runner-1"):
        """§6.1 step 1: BEGIN IMMEDIATE atomic claim. The UNIQUE PK makes the
        claim atomic; a second worker's insert fails and it moves on.
        This row IS the transactional outbox entry for the candidate.
        Existing row with a different versionHash => ERR_VERSION_DRIFT."""
        try:
            self.db.execute("BEGIN IMMEDIATE")
            cur = self.db.execute(
                "SELECT versionHash FROM rows WHERE conceptId=? AND conceptVersion=?",
                (concept_id, concept_version))
            existing = cur.fetchone()
            if existing is not None:
                self.db.execute("COMMIT")
                if existing[0] != version_hash:
                    raise PipelineError("ERR_VERSION_DRIFT",
                                        "%s v%d stored versionHash %s… != computed %s… (bump directive required)"
                                        % (concept_id, concept_version, existing[0][:12], version_hash[:12]))
                return False
            self.db.execute(
                "INSERT INTO rows (conceptId, conceptVersion, versionHash, idempotencyKey, state, owner, ts)"
                " VALUES (?,?,?,?, 'CLAIMED', ?, ?)",
                (concept_id, concept_version, version_hash, idem_key, owner, time.time()))
            self.db.execute("COMMIT")
            return True
        except sqlite3.Error as e:
            self.db.execute("ROLLBACK")
            raise PipelineError("ERR_LEDGER_TX", "claim failed: %s" % e)

    # -------------------------------------------------------- job outbox (§6)

    def reserve_and_open_job(self, wave, attempt, member_keys, input_sha, input_ref,
                             reserve_per_request=None):
        """§10.2 step 1+2 and §6 job outbox, ONE transaction: check
        spent+reserved+new <= cap, debit the reservation, and commit the
        JOB_PENDING outbox row — all BEFORE batches.create. Returns jobKey."""
        per = reserve_per_request if reserve_per_request is not None else common.RESERVE_PER_REQUEST_USD
        worst = per * len(member_keys)
        jk = common.job_key(wave, attempt, member_keys)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            cur = self.db.execute("SELECT capUSD, spentUSD, reservedUSD FROM budget WHERE id=1")
            cap, spent, reserved = cur.fetchone()
            if spent + reserved + worst > cap + 1e-9:
                self.db.execute("ROLLBACK")
                raise PipelineError("ERR_BUDGET_RESERVE",
                                    "reservation $%.2f would exceed cap: spent $%.2f + reserved $%.2f + new $%.2f > $%.2f"
                                    % (worst, spent, reserved, worst, cap))
            cur = self.db.execute("SELECT state FROM jobs WHERE jobKey=?", (jk,))
            if cur.fetchone() is not None:
                self.db.execute("ROLLBACK")
                raise PipelineError("ERR_JOB_EXISTS", "job outbox row %s already exists" % jk)
            self.db.execute("UPDATE budget SET reservedUSD = reservedUSD + ? WHERE id=1", (worst,))
            self.db.execute(
                "INSERT INTO jobs (jobKey, wave, attempt, state, memberCount, worstCaseUSD,"
                " inputFileSha256, inputFileRef, ts) VALUES (?,?,?,?,?,?,?,?,?)",
                (jk, wave, attempt, "JOB_PENDING", len(member_keys), worst, input_sha, input_ref, time.time()))
            self.db.execute("COMMIT")
            return jk
        except sqlite3.Error as e:
            self.db.execute("ROLLBACK")
            raise PipelineError("ERR_LEDGER_TX", "reserve failed: %s" % e)

    def record_batch_id(self, job_key, batch_id):
        """JOB_PENDING -> JOB_SUBMITTED(batchId) (§6.1 step 3, job level)."""
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute("UPDATE jobs SET state='JOB_SUBMITTED', batchId=? WHERE jobKey=? AND state='JOB_PENDING'",
                        (batch_id, job_key))
        n = self.db.execute("SELECT changes()").fetchone()[0]
        self.db.execute("COMMIT")
        if n != 1:
            raise PipelineError("ERR_LEDGER_TX", "job %s not in JOB_PENDING" % job_key)

    def settle_job(self, job_key, actual_usd):
        """§10.2 step 3: actual cost -> spentUSD, unused reservation remainder
        released, JOB_SETTLED — one transaction. The reservation never leaks."""
        self.db.execute("BEGIN IMMEDIATE")
        cur = self.db.execute("SELECT worstCaseUSD, state FROM jobs WHERE jobKey=?", (job_key,))
        row = cur.fetchone()
        if row is None or row[1] not in ("JOB_SUBMITTED", "JOB_PENDING"):
            self.db.execute("ROLLBACK")
            raise PipelineError("ERR_LEDGER_TX", "job %s not settleable (%s)" % (job_key, row and row[1]))
        worst = row[0]
        if actual_usd > worst + 1e-9:
            self.db.execute("ROLLBACK")
            raise PipelineError("ERR_BUDGET_RESERVE",
                                "settlement $%.4f exceeds the job's committed worst case $%.4f" % (actual_usd, worst))
        self.db.execute("UPDATE budget SET spentUSD = spentUSD + ?, reservedUSD = reservedUSD - ? WHERE id=1",
                        (actual_usd, worst))
        self.db.execute("UPDATE jobs SET state='JOB_SETTLED', settledUSD=?, settledTs=? WHERE jobKey=?",
                        (actual_usd, time.time(), job_key))
        self.db.execute("COMMIT")

    def release_job_unsubmitted(self, job_key):
        """A job VERIFIED-ABSENT at reconciliation and re-planned under a new
        attempt: release its reservation, settle at $0 (nothing was billed)."""
        self.settle_job(job_key, 0.0)

    # ----------------------------------------------------------- row updates

    def mark_submitted(self, idem_key, batch_id, wave):
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute(
            "UPDATE rows SET state='SUBMITTED', batchId=?, wave=? WHERE idempotencyKey=? AND state IN ('CLAIMED','SUBMITTED')",
            (batch_id, wave, idem_key))
        self.db.execute("COMMIT")

    def complete_row(self, idem_key, outcome, quarantine_code=None, request_id=None,
                     response_sha=None, usage=None, cost_usd=0.0, repair_calls=None,
                     provider_attempts=None):
        if outcome not in OUTCOMES:
            raise PipelineError("ERR_LEDGER_TX", "bad outcome %r" % outcome)
        self.db.execute("BEGIN IMMEDIATE")
        sets = ["state='COMPLETED'", "outcome=?", "quarantineCode=?", "requestId=?",
                "responseSha256=?", "usageJson=?", "costUSD=costUSD+?"]
        vals = [outcome, quarantine_code, request_id, response_sha,
                json.dumps(usage or [], sort_keys=True), cost_usd]
        if repair_calls is not None:
            sets.append("repairCalls=?"); vals.append(repair_calls)
        if provider_attempts is not None:
            sets.append("providerAttempts=?"); vals.append(provider_attempts)
        vals.append(idem_key)
        self.db.execute("UPDATE rows SET %s WHERE idempotencyKey=?" % ", ".join(sets), vals)
        self.db.execute("COMMIT")

    def add_row_cost(self, idem_key, cost_usd, usage_entry=None):
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute("UPDATE rows SET costUSD=costUSD+? WHERE idempotencyKey=?", (cost_usd, idem_key))
        if usage_entry is not None:
            cur = self.db.execute("SELECT usageJson FROM rows WHERE idempotencyKey=?", (idem_key,))
            u = json.loads(cur.fetchone()[0] or "[]")
            u.append(usage_entry)
            self.db.execute("UPDATE rows SET usageJson=? WHERE idempotencyKey=?",
                            (json.dumps(u, sort_keys=True), idem_key))
        self.db.execute("COMMIT")

    # ------------------------------------------------------------- inspection

    def budget(self):
        cap, spent, reserved = self.db.execute(
            "SELECT capUSD, spentUSD, reservedUSD FROM budget WHERE id=1").fetchone()
        return {"capUSD": cap, "spentUSD": spent, "reservedUSD": reserved}

    def unsettled_jobs(self):
        cur = self.db.execute(
            "SELECT jobKey, wave, attempt, state, memberCount, worstCaseUSD, batchId, ts, inputFileSha256, inputFileRef"
            " FROM jobs WHERE state IN ('JOB_PENDING','JOB_SUBMITTED') ORDER BY ts")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def oldest_unsettled_ts(self):
        r = self.db.execute(
            "SELECT MIN(ts) FROM jobs WHERE state IN ('JOB_PENDING','JOB_SUBMITTED')").fetchone()
        return r[0]

    def rows_by_state(self):
        out = {}
        for st, outcome, n in self.db.execute(
                "SELECT state, outcome, COUNT(*) FROM rows GROUP BY state, outcome"):
            out[(st, outcome)] = n
        return out

    def terminal_accounting(self, expected_total):
        """§10.3 PROCEED precondition #0: accepted + quarantined +
        provider_failed = expected_total, every row terminal."""
        counts = {"ACCEPTED": 0, "QUARANTINED": 0, "PROVIDER_FAILED": 0}
        nonterminal = 0
        for (st, outcome), n in self.rows_by_state().items():
            if st == "COMPLETED" and outcome in counts:
                counts[outcome] += n
            elif st == "FROZEN":
                raise PipelineError("ERR_TERMINAL_ACCOUNTING",
                                    "FROZEN row inside the worklist (builder guarantee violated)")
            else:
                nonterminal += n
        jobs_open = len(self.unsettled_jobs())
        total = sum(counts.values())
        ok = (nonterminal == 0 and jobs_open == 0 and total == expected_total)
        return {"ok": ok, "counts": counts, "total": total,
                "expected": expected_total, "nonterminalRows": nonterminal,
                "unsettledJobs": jobs_open}

    def export_jsonl(self, path=None):
        """§6.1: derived, append-only passive export (audit surface)."""
        path = path or common.LEDGER_EXPORT
        with open(path, "w", encoding="utf-8") as f:
            for table in ("rows", "jobs"):
                cur = self.db.execute("SELECT * FROM %s ORDER BY 1" % table)
                cols = [c[0] for c in cur.description]
                for r in cur.fetchall():
                    f.write(common.canonical_dumps(dict(zip(cols, r), _table=table)) + "\n")
        return path

    def close(self):
        self.db.close()
