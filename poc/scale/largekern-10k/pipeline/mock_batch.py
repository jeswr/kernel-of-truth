#!/usr/bin/env python3
"""mock_batch.py — component 8 (half 1): the MOCK OpenAI Batch backend.

$0, no network, file-backed (so a killed client can 'restart' and reconcile
against durable provider state — exactly the §6 crash windows). Implements
the three primitives the §6 idempotency design needs:

  create(input_file_bytes, metadata)  -> batch object (id, created_at, ...)
  list(after=None, limit=N)           -> newest-first page + has_more/after
                                         cursor (EXHAUSTIVE pagination is the
                                         r5 completeness rule's substrate)
  retrieve(batch_id) / output_bytes() -> status + output file lines

Output synthesis is delegated to a drafter callback (mock_drafter), per
input line: {custom_id, response:{status_code, request_id, body}} or
{custom_id, error:{...}} — requestId is recorded from response.request_id
(§8, r5).

Injection hooks (P5, §10.6):
  crash_on_create        — persist the batch, then raise CrashInjected BEFORE
                           returning the id (client dies post-acceptance /
                           pre-batchId-record: crash window (b)).
  fail_list_on_page N    — the Nth list() page call raises MockListError
                           (mid-pagination failure => ERR_RECONCILE_UNVERIFIED).
  truncate_list_pages N  — after N pages, report has_more=True but make the
                           next page unavailable (unexhausted cursor case).
Crash window (a) — post-job-outbox / pre-create — is injected client-side
(orchestrator LK_CRASH=pre_create), since the provider never sees that job.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common


class CrashInjected(Exception):
    """Simulated client death (P5). Provider state is already durable."""


class MockListError(Exception):
    """Simulated batches.list() failure mid-pagination."""


class MockBatchProvider(object):
    def __init__(self, state_dir=None):
        self.dir = state_dir or common.PROVIDER_DIR
        self.files = os.path.join(self.dir, "files")
        for d in (self.dir, self.files):
            if not os.path.isdir(d):
                os.makedirs(d)
        self.index = os.path.join(self.dir, "batches.jsonl")
        # injection hooks (in-process; env LK_CRASH drives subprocess tests)
        self.crash_on_create = False
        self.fail_list_on_page = None
        self.truncate_list_pages = None
        self._list_page_calls = 0

    # ---------------------------------------------------------------- state

    def _load(self):
        if not os.path.isfile(self.index):
            return []
        with open(self.index, "r", encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def _append(self, obj):
        with open(self.index, "a", encoding="utf-8") as f:
            f.write(common.canonical_dumps(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _rewrite(self, batches):
        tmp = self.index + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for b in batches:
                f.write(common.canonical_dumps(b) + "\n")
        os.replace(tmp, self.index)

    def created_count(self, idempotency_key=None):
        """Test oracle: how many batches has the provider EVER accepted
        (optionally for one metadata.idempotency_key)? Duplicate-submission
        assertions key on this."""
        bs = self._load()
        if idempotency_key is None:
            return len(bs)
        return sum(1 for b in bs if b["metadata"].get("idempotency_key") == idempotency_key)

    # ------------------------------------------------------------------ api

    def create(self, input_file_bytes, metadata):
        """Accept + durably persist the job, THEN maybe crash the client
        (window (b)): provider acceptance precedes the client recording the
        returned id, exactly the window the r5 sweeper exists for."""
        bs = self._load()
        bid = "batch_mock%06d" % (len(bs) + 1)
        fid = "file_%s_in" % bid
        with open(os.path.join(self.files, fid), "wb") as f:
            f.write(input_file_bytes)
        import time
        obj = {
            "id": bid, "object": "batch",
            "created_at": time.time(),        # epoch — comparable with outbox
            "seq": len(bs) + 1,               # commit ts (r5 far-edge rule)
            "status": "validating",
            "metadata": dict(metadata or {}),
            "input_file_id": fid, "output_file_id": None,
            "request_counts": {"total": input_file_bytes.count(b"\n")},
        }
        self._append(obj)
        if self.crash_on_create:
            self.crash_on_create = False
            raise CrashInjected("client died after provider acceptance of %s, before recording batchId" % bid)
        return dict(obj)

    def list(self, after=None, limit=20):
        """Newest-first cursor pagination (`after`/`has_more`), per the Batch
        guide. Injection: mid-pagination failure / unexhausted cursor."""
        self._list_page_calls += 1
        if self.fail_list_on_page is not None and self._list_page_calls >= self.fail_list_on_page:
            raise MockListError("batches.list() failed (injected, page call %d)" % self._list_page_calls)
        if self.truncate_list_pages is not None and self._list_page_calls > self.truncate_list_pages:
            raise MockListError("next page unavailable (injected unexhausted has_more cursor)")
        bs = sorted(self._load(), key=lambda b: (-b["created_at"], -b.get("seq", 0)))
        start = 0
        if after is not None:
            ids = [b["id"] for b in bs]
            if after not in ids:
                raise MockListError("unknown list cursor %r" % after)
            start = ids.index(after) + 1
        page = bs[start:start + limit]
        has_more = start + limit < len(bs)
        if self.truncate_list_pages is not None and self._list_page_calls >= self.truncate_list_pages:
            has_more = True   # lie: cursor points past a page that will fail
        return {"data": [dict(b) for b in page], "has_more": has_more,
                "last_id": page[-1]["id"] if page else None}

    def reset_list_counters(self):
        self._list_page_calls = 0

    def retrieve(self, batch_id):
        for b in self._load():
            if b["id"] == batch_id:
                return dict(b)
        raise KeyError(batch_id)

    def input_bytes(self, batch_id):
        b = self.retrieve(batch_id)
        with open(os.path.join(self.files, b["input_file_id"]), "rb") as f:
            return f.read()

    def output_bytes(self, batch_id):
        b = self.retrieve(batch_id)
        if not b.get("output_file_id"):
            raise KeyError("batch %s has no output yet" % batch_id)
        with open(os.path.join(self.files, b["output_file_id"]), "rb") as f:
            return f.read()

    # ------------------------------------------------------------- lifecycle

    def tick(self, drafter):
        """Advance every non-terminal batch one lifecycle step:
        validating -> in_progress -> completed (output synthesized via the
        drafter callback per input line). Mirrors the 24h window at 0 cost."""
        bs = self._load()
        changed = False
        for b in bs:
            if b["status"] == "validating":
                b["status"] = "in_progress"
                changed = True
            elif b["status"] == "in_progress":
                with open(os.path.join(self.files, b["input_file_id"]), "rb") as f:
                    lines = [l for l in f.read().splitlines() if l.strip()]
                out = []
                for i, raw in enumerate(lines):
                    req = json.loads(raw.decode("utf-8"))
                    out.append(common.canonical_dumps(
                        drafter.respond(req, batch_id=b["id"], line_no=i, meta=b["metadata"])))
                fid = "file_%s_out" % b["id"]
                with open(os.path.join(self.files, fid), "wb") as f:
                    f.write(("\n".join(out) + "\n").encode("utf-8"))
                b["status"] = "completed"
                b["output_file_id"] = fid
                changed = True
        if changed:
            self._rewrite(bs)
        return bs
