#!/usr/bin/env python3
"""orchestrator.py — components 3, 6, 7: the Batch orchestrator against the
MOCK backend (spec §6 r5 idempotency), P4a/P4b inline gates (§7), kill ladder
(§10.2), and terminal accounting (§10.3).

§6 obligations implemented here:
* every paid (mock-)submission rides a Batch JOB whose outbox row — jobKey =
  "kv1d-job-" + sha256(wave ‖ attempt ‖ sorted member idempotencyKeys)[:24],
  with the load-bearing (wave, attempt) discriminator — is committed with its
  §10.2 reservation in ONE transaction BEFORE batches.create;
* metadata.idempotency_key = jobKey on the created batch; custom_id is
  correlation WITHIN one job's input file only;
* restart reconciliation = EXHAUSTIVE `after`/`has_more` pagination of
  batches.list() until has_more == false OR the page sequence verifiably
  passes the far edge of the window (oldest page created_at predates the
  oldest unsettled outbox row's commit ts); ANY failed page call or
  unexhausted cursor => ERR_RECONCILE_UNVERIFIED, NO resubmission;
* found token => adopt that batch's result (no double spend); verified-absent
  JOB_PENDING => the crash was pre-create, safe resubmission of the SAME job;
* requestId recorded from the Batch output line's response.request_id (§8 r5).

Crash-injection (P5): env LK_CRASH=pre_create — SIGKILL after the job-outbox
commit, before create; LK_CRASH=post_create — the provider persists the batch
then the client dies before recording batchId (provider hook). Used by the
subprocess crash tests and the e2e crash demo.
"""

import hashlib
import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import prompt as prompt_mod
import mock_batch
import mock_drafter
import accept as accept_mod
from common import PipelineError
from ledger import Ledger

sys.path.insert(0, os.path.join(common.REPO_ROOT, "poc", "plainv5"))
import invoke_seat  # noqa: E402 — pinned P8 machinery (a4f65edd)


def compute_line_cost(usage):
    """Settlement cost of one Batch output line from its usage fields, at the
    REGISTERED §5.2 prices (Batch 0.5x; cached read 0.1x; cache write 1.25x on
    the populated prefix). Mock accounting uses registered figures only."""
    p = common.PRICE_PER_MTOK
    cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    if usage.get("prefix_write"):
        prefix = min(8000, inp)
        cost = prefix * p["cache_write"] + (inp - prefix) * p["input"]
    else:
        cost = cached * p["cached_read"] + (inp - cached) * p["input"]
    cost += out * p["output"]
    return cost * p["batch_multiplier"] / 1e6


class Pilot(object):
    def __init__(self, out_dir=None, ledger_path=None, provider_dir=None,
                 store_dir=None, cap_usd=None, reconcile_timeout=0.0):
        self.out_dir = out_dir or common.OUT_DIR
        self.ledger = Ledger(ledger_path, cap_usd=cap_usd)
        self.provider = mock_batch.MockBatchProvider(provider_dir)
        self.builder = prompt_mod.RequestBuilder()
        self.store = accept_mod.DraftStore(store_dir)
        self.reconcile_timeout = reconcile_timeout   # pinned at prereg for real (§6)
        self.worklist = {}         # conceptId -> row
        self.by_idem = {}          # idempotencyKey -> context dict
        self.usage_totals = {"input": 0, "cached": 0, "output": 0}
        self.kill_ladder_log = []
        self._ladder_crossed = set()
        self.p4a = None
        self.p4b = None
        self._bench_done = False

    # -------------------------------------------------------------- worklist

    def load_worklist(self, path=None, limit=None):
        path = path or os.path.join(self.out_dir, "worklist.jsonl")
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        if limit:
            rows = rows[:limit]
        for row in rows:
            vh, ik = self.builder.version_ids(row)
            self.worklist[row["conceptId"]] = row
            self.by_idem[ik] = {
                "row": row, "versionHash": vh, "idem": ik, "wave": 0,
                "conceptVersion": 1, "repairCalls": 0, "providerAttempts": 0,
                "prevOutput": None, "errCodes": None, "usage": [],
                "state": "pending",   # pending|repair|provider_retry|done
            }
            self.ledger.claim_row(row["conceptId"], 1, vh, ik)   # §6.1 step 1
        return len(rows)

    def init_seat_ledger(self):
        """§9.1: kot-seat-ledger/1 with entry 0 = the author seat (the exact
        dated gpt-5.6-sol id), via the PINNED invoker."""
        if os.path.exists(common.SEAT_LEDGER):
            return
        manifest_path = os.path.join(self.out_dir, "sample-manifest.json")
        with open(manifest_path, "rb") as f:
            out_sha = hashlib.sha256(f.read()).hexdigest()
        invoke_seat.init_author(
            common.SEAT_LEDGER, common.FAMILY_MAP, common.MODEL_SNAPSHOT_ID,
            prompt_sha256=self.builder.cache_prefix_hash,
            output_sha256=out_sha,
            invocation_form="batch-draft-author")

    # ------------------------------------------------------------ submission

    def _members_for_wave(self, wave):
        want = ("pending",) if wave == 0 else ("repair", "provider_retry")
        return [ik for ik, c in sorted(self.by_idem.items())
                if c["state"] in want and c["wave"] == wave]

    def build_input(self, member_keys, wave):
        lines = []
        for ik in member_keys:
            c = self.by_idem[ik]
            line, _ = self.builder.build_line(
                c["row"], ik, wave=wave,
                previous_output=c["prevOutput"], err_codes=c["errCodes"])
            lines.append(line)
        return b"".join(lines)

    def submit_job(self, wave, attempt, member_keys):
        """Outbox-before-call (§6): reservation + JOB_PENDING committed, THEN
        batches.create with metadata.idempotency_key = jobKey."""
        input_bytes = self.build_input(member_keys, wave)
        input_sha = hashlib.sha256(input_bytes).hexdigest()
        input_ref = os.path.join(self.out_dir, "inputs", "wave%d-att%d-%s.jsonl" % (wave, attempt, input_sha[:8]))
        d = os.path.dirname(input_ref)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(input_ref, "wb") as f:
            f.write(input_bytes)
        jk = self.ledger.reserve_and_open_job(wave, attempt, member_keys, input_sha, input_ref)
        if os.environ.get("LK_CRASH") == "pre_create":
            os.kill(os.getpid(), signal.SIGKILL)          # P5 window (a)
        if os.environ.get("LK_CRASH") == "post_create":
            self.provider.crash_on_create = True          # P5 window (b)
        batch = self.provider.create(input_bytes, metadata={
            "idempotency_key": jk, "wave": str(wave), "attempt": str(attempt)})
        self.ledger.record_batch_id(jk, batch["id"])
        for ik in member_keys:
            self.ledger.mark_submitted(ik, batch["id"], wave)
        return jk, batch["id"]

    # ---------------------------------------------------------- reconciliation

    def reconcile(self):
        """The r5 sweeper. Returns list of (jobKey, action) taken. Fails
        closed ERR_RECONCILE_UNVERIFIED on ANY incomplete listing."""
        actions = []
        unsettled = [j for j in self.ledger.unsettled_jobs()
                     if time.time() - j["ts"] >= self.reconcile_timeout]
        if not unsettled:
            return actions
        oldest_ts = min(j["ts"] for j in unsettled)
        # EXHAUSTIVE pagination (r5 completeness rule)
        found = {}
        after = None
        covered = False
        self.provider.reset_list_counters()
        while True:
            try:
                page = self.provider.list(after=after, limit=5)
            except mock_batch.MockListError as e:
                raise PipelineError("ERR_RECONCILE_UNVERIFIED",
                                    "incomplete batches.list() pagination (%s); no resubmission" % e)
            for b in page["data"]:
                k = b["metadata"].get("idempotency_key")
                if k:
                    found.setdefault(k, b)
            if page["data"] and min(b["created_at"] for b in page["data"]) < oldest_ts:
                covered = True    # verifiably past the window's far edge
                break
            if not page["has_more"]:
                covered = True    # provider-attested end of listing
                break
            if page["last_id"] is None:
                break
            after = page["last_id"]
        if not covered:
            raise PipelineError("ERR_RECONCILE_UNVERIFIED",
                                "pagination ended without verified coverage; no resubmission")
        for j in unsettled:
            jk = j["jobKey"]
            hit = found.get(jk)
            if j["state"] == "JOB_PENDING":
                if hit is not None:
                    self.ledger.record_batch_id(jk, hit["id"])     # adopt, no double spend
                    actions.append((jk, "adopted:" + hit["id"]))
                else:
                    # verified absent under the completeness rule => the crash
                    # was pre-create; the SAME outbox row backs a safe submit.
                    with open(j["inputFileRef"], "rb") as f:
                        input_bytes = f.read()
                    batch = self.provider.create(input_bytes, metadata={
                        "idempotency_key": jk, "wave": str(j["wave"]), "attempt": str(j["attempt"])})
                    self.ledger.record_batch_id(jk, batch["id"])
                    actions.append((jk, "resubmitted:" + batch["id"]))
            elif j["state"] == "JOB_SUBMITTED":
                if hit is None or hit["id"] != j["batchId"]:
                    raise PipelineError("ERR_RECONCILE_UNVERIFIED",
                                        "submitted job %s (batch %s) not found in verified listing"
                                        % (jk, j["batchId"]))
                actions.append((jk, "verified:" + hit["id"]))
        return actions

    # ------------------------------------------------------------ processing

    def poll_to_completion(self, drafter):
        # "completed" and "failed" (whole-batch validation failure, §10.4) are
        # both terminal provider states the settle step must be able to reach.
        for _ in range(8):
            batches = self.provider.tick(drafter)
            if all(b["status"] in ("completed", "failed") for b in batches):
                return
        raise PipelineError("ERR_PROVIDER_TIMEOUT", "mock batches did not complete")

    def settle_and_process(self, job_key, batch_id, wave):
        """Download the batch result, settle cost (§10.2 step 3), run the
        acceptance stack (§4.1), route outcomes; kill-ladder checks at
        settlement.

        Real OpenAI Batch splits per-request outcomes across TWO files —
        SUCCEEDED requests in `output_file_id`, FAILED/EXPIRED requests in
        `error_file_id` — and signals a whole-batch input-validation failure
        via status=="failed" with NO files and an `errors` array (§10.4). Both
        files are downloaded and merged by custom_id; error-file lines and
        every member of a failed batch take the §10.4 provider-retry /
        PROVIDER_FAILED path. Every submitted custom_id MUST resolve to a
        terminal | retry state — a gap fails closed rather than silently
        leaving a SUBMITTED ledger row that would break §10.3."""
        batch = self.provider.retrieve(batch_id)
        member_cids = set()
        for raw in self.provider.input_bytes(batch_id).decode("utf-8").splitlines():
            if raw.strip():
                member_cids.add(json.loads(raw)["custom_id"])

        # ---- whole-batch input-validation failure (§10.4): no output/error
        # file; every request in the job is retried / PROVIDER_FAILED.
        if batch.get("status") == "failed":
            for ik in sorted(member_cids):
                c = self.by_idem.get(ik)
                if c is None:
                    raise PipelineError("ERR_LEDGER_TX",
                                        "failed-batch member %s matches no claimed row" % ik)
                self._route_provider_failure(ik, c, wave)
            self.ledger.settle_job(job_key, 0.0)     # nothing billed on a failed batch
            self._kill_ladder_check()
            return 0.0

        # ---- completed batch: merge SUCCEEDED (output) + FAILED/EXPIRED (error)
        out_lines = []
        if batch.get("output_file_id"):
            out_lines += [json.loads(l) for l in
                          self.provider.output_bytes(batch_id).decode("utf-8").splitlines() if l.strip()]
        if batch.get("error_file_id"):
            out_lines += [json.loads(l) for l in
                          self.provider.error_bytes(batch_id).decode("utf-8").splitlines() if l.strip()]
        total_cost = 0.0
        drafts, contexts = {}, {}
        processed = set()
        for line in out_lines:
            ik = line["custom_id"]
            processed.add(ik)
            c = self.by_idem.get(ik)
            if c is None:
                raise PipelineError("ERR_LEDGER_TX", "output custom_id %s matches no claimed row" % ik)
            if line.get("error"):
                self._route_provider_failure(ik, c, wave)   # §10.4 (error-file line)
                continue
            resp = line["response"]
            usage = resp["body"]["usage"]
            cost = compute_line_cost(usage)
            total_cost += cost
            self.usage_totals["input"] += usage["input_tokens"]
            self.usage_totals["cached"] += usage["input_tokens_details"]["cached_tokens"]
            self.usage_totals["output"] += usage["output_tokens"]
            entry = {"requestId": resp["request_id"], "batchId": batch_id,
                     "inputTokens": usage["input_tokens"],
                     "cachedTokens": usage["input_tokens_details"]["cached_tokens"],
                     "outputTokens": usage["output_tokens"], "costUSD": round(cost, 6)}
            c["usage"].append(entry)
            self.ledger.add_row_cost(ik, cost, entry)
            output_text = resp["body"]["output_text"]
            c["lastRequestId"] = resp["request_id"]
            c["lastResponseSha"] = hashlib.sha256(output_text.encode("utf-8")).hexdigest()
            c["lastBatchId"] = batch_id
            c["returnedModelId"] = resp["body"]["model"]
            if wave > 0 and c["state"] == "repair":
                c["repairCalls"] += 1
            kind, payload = accept_mod.parse_output(output_text)
            if kind == "abstain":
                self.ledger.complete_row(ik, "QUARANTINED", quarantine_code="ABSTAINED",
                                         request_id=resp["request_id"],
                                         response_sha=c["lastResponseSha"],
                                         usage=c["usage"], repair_calls=c["repairCalls"])
                self.store.quarantine(c["row"], "ABSTAINED", payload, wave)
                c["state"] = "done"
            elif kind == "malformed":
                self._route_failure(ik, c, payload, output_text, wave)
            else:
                gloss_errs = accept_mod.lint_gloss(payload["gloss"], c["row"]["lemma"])
                contexts[ik] = (payload, gloss_errs, output_text)
                drafts[ik] = payload["explication"]
        # every submitted request MUST appear across output+error (a real
        # completed batch covers them all); an un-accounted custom_id is a
        # provider/ledger gap — fail closed, never leave a SUBMITTED row.
        unaccounted = member_cids - processed
        if unaccounted:
            raise PipelineError("ERR_UNACCOUNTED_REQUEST",
                                "%d submitted custom_id(s) absent from output+error files: %s"
                                % (len(unaccounted), sorted(unaccounted)[:5]))
        # ---- sharded encoder/validator leg (§4.1 items 1-3, §7.1)
        per_id, reports = ({}, [])
        if drafts:
            per_id, reports = accept_mod.validate_shards(drafts)
            if not self._bench_done:
                self._maybe_p4a(reports)
        for ik, (payload, gloss_errs, output_text) in sorted(contexts.items()):
            ok, code = per_id.get(ik, (False, "ERR_SHARD_MISSING"))
            errs = list(gloss_errs) + ([] if ok else [code])
            c = self.by_idem[ik]
            if "ERR_LEAKAGE" in errs:
                # hard reject (§2.3) — terminal, never repaired
                self._quarantine_row(ik, c, "ERR_LEAKAGE", wave)
            elif errs:
                self._route_failure(ik, c, errs, output_text, wave)
            else:
                self._accept_row(ik, c, payload, output_text, wave)
        self.ledger.settle_job(job_key, total_cost)          # §10.2 step 3
        self._kill_ladder_check()
        return total_cost

    def _route_provider_failure(self, ik, c, wave):
        """§10.4 provider/transport failure (error-file line or whole-batch
        failed): ≤ PROVIDER_RETRY_LIMIT re-inclusions in a follow-up job, then
        PROVIDER_FAILED. Distinct from the R=2 CONTENT-repair budget."""
        c["providerAttempts"] += 1
        if wave >= common.R_REPAIR or c["providerAttempts"] > common.PROVIDER_RETRY_LIMIT:
            self.ledger.complete_row(ik, "PROVIDER_FAILED",
                                     provider_attempts=c["providerAttempts"])
            c["state"] = "done"
        else:
            c["state"] = "provider_retry"
            c["wave"] = wave + 1

    def _route_failure(self, ik, c, errs, output_text, wave):
        if wave < common.R_REPAIR:
            c["state"] = "repair"
            c["wave"] = wave + 1
            c["prevOutput"] = output_text[:2000]
            c["errCodes"] = [str(e) for e in errs]
        else:
            self._quarantine_row(ik, c, str(errs[0]).split(":")[0], wave)

    def _quarantine_row(self, ik, c, code, wave):
        self.ledger.complete_row(ik, "QUARANTINED", quarantine_code=code,
                                 request_id=c.get("lastRequestId"),
                                 response_sha=c.get("lastResponseSha"),
                                 usage=c["usage"], repair_calls=c["repairCalls"])
        self.store.quarantine(c["row"], code, "", wave)
        c["state"] = "done"

    def _accept_row(self, ik, c, payload, output_text, wave):
        """Mint the immutable ModelDrafted record with the full §8 block."""
        tref, tbytes = self.store.append_transcript(
            c["row"]["conceptId"],
            {"suffix": prompt_mod.draft_suffix(c["row"]), "output": output_text})
        _, prompt_hash = self.builder.build_line(c["row"], ik, wave=0)
        provenance = {
            "draftAuthor": common.MODEL_SNAPSHOT_ID,
            "returnedModelId": c.get("returnedModelId"),
            "authorFamily": "openai",          # asserted == resolver output at mint
            "pipelineOperator": "runner-1 (kb-pipeline-runner)",
            "endorser": None,
            "conceptId": c["row"]["conceptId"], "conceptVersion": c["conceptVersion"],
            "versionHash": "sha256:" + c["versionHash"],
            "idempotencyKey": ik, "batchId": c.get("lastBatchId"), "customId": ik,
            "requestId": c.get("lastRequestId"),          # §8 r5: response.request_id
            "promptHash": "sha256:" + prompt_hash,
            "cachePrefixHash": "sha256:" + self.builder.cache_prefix_hash,
            "genSettings": {k: v for k, v in self.builder.gen_settings.items() if not k.startswith("_")},
            "sourceRowSha256": c["row"]["sourceRowSha256"],
            "responseSha256": c.get("lastResponseSha"),
            "transcriptRef": tref,
            "usage": c["usage"],
            "repairCalls": c["repairCalls"],
            "validatorHash": self.builder._validator_hash(),
            "lintHash": "sha256:" + self.builder.lint_hash,
            "acceptancePath": "validateExplication+catalogLint+encodeShard+lint",
            "seatLedgerRef": os.path.relpath(common.SEAT_LEDGER, common.REPO_ROOT) + "#0",
        }
        draft_id, rec_sha, rec_bytes = self.store.mint(c["row"], payload, provenance)
        c["recordBytes"] = rec_bytes
        c["transcriptBytes"] = tbytes
        self.ledger.complete_row(ik, "ACCEPTED",
                                 request_id=c.get("lastRequestId"),
                                 response_sha=c.get("lastResponseSha"),
                                 usage=c["usage"], repair_calls=c["repairCalls"])
        c["state"] = "done"

    # ------------------------------------------------------------- P4 gates

    def _maybe_p4a(self, reports):
        """P4a (§7.1): the FIRST full B=1,000-record shard report is the
        representative benchmark; gates launch of the remaining worklist.
        Smoke runs (n < B) bench their largest shard, marked representative:
        False — a real PROCEED may only cite a representative=True artifact."""
        smoke = len(self.by_idem) < common.VALIDATOR_SHARD_B
        for rep in reports:
            if rep["records"] == common.VALIDATOR_SHARD_B or smoke:
                proj = common.SAMPLE_N / rep["timing"]["recordsPerSec"]
                self.p4a = {
                    "recordsPerSec": rep["timing"]["recordsPerSec"],
                    "wallSec": rep["timing"]["wallSec"],
                    "catalogEncodeSec": rep["timing"]["catalogEncodeSec"],
                    "maxRssBytes": rep["timing"]["maxRssBytes"],
                    "shardB": rep["records"],
                    "representative": rep["records"] == common.VALIDATOR_SHARD_B,
                    "projectedFull10kSec": proj,
                    "boundSec": common.P4A_MAX_FULL10K_SECONDS,
                    "boundRssBytes": common.P4A_MAX_RSS_BYTES,
                    "pass": (proj <= common.P4A_MAX_FULL10K_SECONDS
                             and rep["timing"]["maxRssBytes"] <= common.P4A_MAX_RSS_BYTES),
                    "encoderPin": rep["encoderPin"],
                }
                common.write_json(os.path.join(self.out_dir, "p4a-benchmark.json"), self.p4a)
                self._bench_done = True
                return

    def p4b_measure(self):
        """P4b (§7.2): record-size + transcript-size distribution on the REAL
        (mock) kernel-v1-draft/1 records of the first batch."""
        recs = sorted(c["recordBytes"] for c in self.by_idem.values() if "recordBytes" in c)
        trs = sorted(c["transcriptBytes"] for c in self.by_idem.values() if "transcriptBytes" in c)

        def dist(xs):
            if not xs:
                return None
            return {"n": len(xs), "meanB": sum(xs) / float(len(xs)),
                    "medianB": xs[len(xs) // 2], "p90B": xs[int(len(xs) * 0.9)], "maxB": xs[-1]}
        self.p4b = {"recordBytes": dist(recs), "transcriptBytes": dist(trs),
                    "pass": bool(recs and trs)}
        common.write_json(os.path.join(self.out_dir, "p4b-sizes.json"), self.p4b)
        return self.p4b

    def require_p4_gates(self):
        """§7/§10.3: P4a + P4b artifacts must be ON FILE and green before the
        remaining ~9,000 launch; a verdict computed without them is INVALID."""
        if not (self.p4a and self.p4a["pass"]):
            raise PipelineError("ERR_P4A_GATE", "P4a benchmark missing or out of bounds: %s" % self.p4a)
        if not (self.p4b and self.p4b["pass"]):
            raise PipelineError("ERR_P4B_GATE", "P4b size distribution missing: %s" % self.p4b)

    # ------------------------------------------------------------ kill ladder

    def _kill_ladder_check(self):
        b = self.ledger.budget()
        spent = b["spentUSD"]
        states = self.ledger.rows_by_state()
        attempted = sum(n for (st, oc), n in states.items()
                        if st == "COMPLETED" and oc in ("ACCEPTED", "QUARANTINED")) \
            + sum(n for (st, oc), n in states.items() if st == "SUBMITTED")
        accepted = states.get(("COMPLETED", "ACCEPTED"), 0)
        kappa = (self.usage_totals["cached"] / float(self.usage_totals["input"])
                 if self.usage_totals["input"] else 0.0)
        for rung in common.KILL_LADDER:
            key = rung["atUSD"]
            if spent >= key and key not in self._ladder_crossed:
                self._ladder_crossed.add(key)
                entry = {"atUSD": key, "spentUSD": round(spent, 4),
                         "attempted": attempted, "kappa": round(kappa, 4)}
                ok = True
                if "minAttempted" in rung and attempted < rung["minAttempted"]:
                    ok = False
                if "minKappa" in rung and kappa < rung["minKappa"]:
                    ok = False
                if "minAcceptRunning" in rung and attempted and accepted / float(attempted) < rung["minAcceptRunning"]:
                    ok = False
                if "minAttemptedFrac" in rung and attempted < rung["minAttemptedFrac"] * len(self.by_idem):
                    ok = False
                entry["pass"] = ok
                self.kill_ladder_log.append(entry)
                if not ok:
                    raise PipelineError("ERR_KILL_LADDER",
                                        "INVALID-INSTRUMENT abort at $%.0f checkpoint: %s" % (key, entry))
        if spent > common.BUDGET_CAP_USD:
            raise PipelineError("ERR_KILL_LADDER", "hard-abort: spend $%.2f > cap" % spent)
