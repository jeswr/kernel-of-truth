#!/usr/bin/env python3
"""test_pipeline.py — mock-validation suite for the WordNet-10k drafting
pipeline (spec r5). Covers the P5 crash windows + r5 negative cases (§6,
§10.6), the §10.2 reservation, §1 frame fail-closed, §6.1 version drift,
P8 family fail paths (§9.1), the §9.2 consumer gate, and the §4.1
acceptance failure modes. $0 — everything runs against the mock backend.

Run: cd poc/scale/largekern-10k && nice -n 10 python3 -m unittest tests.test_pipeline -v
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

PKG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(PKG, "pipeline"))

import common                    # noqa: E402
import frame_sample              # noqa: E402
import accept as accept_mod      # noqa: E402
import mock_batch                # noqa: E402
import mock_drafter              # noqa: E402
import orchestrator              # noqa: E402
import prompt as prompt_mod      # noqa: E402
from common import PipelineError  # noqa: E402
from ledger import Ledger        # noqa: E402

sys.path.insert(0, os.path.join(common.REPO_ROOT, "poc", "plainv5"))
import invoke_seat               # noqa: E402
import check_family_disjoint as cfd  # noqa: E402

WORKLIST = os.path.join(common.OUT_DIR, "worklist.jsonl")
CRASH_DRIVER = os.path.join(PKG, "pipeline", "crash_driver.py")


def setUpModule():
    if not os.path.exists(WORKLIST):
        frame_sample.build()


def scratch_pilot(tmp, n, cap=None):
    shutil.copyfile(WORKLIST, os.path.join(tmp, "worklist.jsonl"))
    p = orchestrator.Pilot(out_dir=tmp,
                           ledger_path=os.path.join(tmp, "ledger.sqlite"),
                           provider_dir=os.path.join(tmp, "provider"),
                           store_dir=os.path.join(tmp, "store"),
                           cap_usd=cap)
    p.load_worklist(os.path.join(tmp, "worklist.jsonl"), limit=n)
    return p


def run_all_waves(pilot, drafter):
    for wave in (0, 1, 2):
        members = pilot._members_for_wave(wave)
        if not members:
            continue
        jk, bid = pilot.submit_job(wave, 0, members)
        pilot.poll_to_completion(drafter)
        pilot.settle_and_process(jk, bid, wave)


class TestFrameAndSample(unittest.TestCase):
    def test_frame_hash_tamper_fails_closed(self):
        frame, total, _ = frame_sample.load_frame()
        orig = common.FRAME_SHA256
        try:
            common.FRAME_SHA256 = "0" * 64
            with self.assertRaises(PipelineError) as cm:
                frame_sample.verify_frame(frame, total)
            self.assertEqual(cm.exception.code, "ERR_FRAME_HASH")
        finally:
            common.FRAME_SHA256 = orig
        # untampered: green
        self.assertEqual(frame_sample.verify_frame(frame, total), common.FRAME_SHA256)

    def test_frame_count_tamper_fails_closed(self):
        frame, total, _ = frame_sample.load_frame()
        victim = sorted(frame)[0]
        frame = dict(frame)
        del frame[victim]
        with self.assertRaises(PipelineError) as cm:
            frame_sample.verify_frame(frame, total)
        self.assertEqual(cm.exception.code, "ERR_FRAME_HASH")

    def test_frozen_overlap_fails_closed(self):
        deny = frame_sample.load_denylist()
        self.assertEqual(len(deny), 107)   # §9.3 [MEASURED]
        victim = sorted(deny)[0]
        with self.assertRaises(PipelineError) as cm:
            frame_sample.check_frozen_overlap([victim], deny)
        self.assertEqual(cm.exception.code, "ERR_FROZEN_OVERLAP")

    def test_sample_manifest_pins(self):
        m = common.read_json(os.path.join(common.OUT_DIR, "sample-manifest.json"))
        self.assertEqual(m["frameSha256"], common.FRAME_SHA256)
        self.assertEqual(m["sampleSeed"], common.SAMPLE_SEED)
        self.assertEqual(m["sampleN"], common.SAMPLE_N)


class TestJobKey(unittest.TestCase):
    def test_wave_attempt_discriminator(self):
        """r5 §6: identical membership across (wave, attempt) => DISTINCT
        jobKeys (the round-4 collision CONCERN, closed)."""
        members = ["kv1d-aaa", "kv1d-bbb", "kv1d-ccc"]
        k00 = common.job_key(0, 0, members)
        k10 = common.job_key(1, 0, members)      # repair wave, same membership
        k01 = common.job_key(0, 1, members)      # §10.4 retry, same membership
        self.assertEqual(len({k00, k10, k01}), 3)
        # order-insensitive in members, deterministic across calls
        self.assertEqual(k00, common.job_key(0, 0, list(reversed(members))))
        self.assertTrue(k00.startswith("kv1d-job-") and len(k00) == len("kv1d-job-") + 24)


class TestBudget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=common.OUT_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_reserve_fails_closed_and_atomic(self):
        led = Ledger(os.path.join(self.tmp, "l.sqlite"), cap_usd=100.0)
        members = ["kv1d-%04d" % i for i in range(2000)]   # worst case $125 > $100
        with self.assertRaises(PipelineError) as cm:
            led.reserve_and_open_job(0, 0, members, "0" * 64, None)
        self.assertEqual(cm.exception.code, "ERR_BUDGET_RESERVE")
        b = led.budget()
        self.assertEqual((b["spentUSD"], b["reservedUSD"]), (0, 0))   # nothing debited
        self.assertEqual(led.unsettled_jobs(), [])                    # no outbox row

    def test_settle_releases_remainder_never_leaks(self):
        led = Ledger(os.path.join(self.tmp, "l.sqlite"), cap_usd=100.0)
        members = ["kv1d-%04d" % i for i in range(100)]    # reserve $6.25
        jk = led.reserve_and_open_job(0, 0, members, "0" * 64, None)
        self.assertAlmostEqual(led.budget()["reservedUSD"], 6.25)
        led.record_batch_id(jk, "batch_x")
        led.settle_job(jk, 1.10)
        b = led.budget()
        self.assertAlmostEqual(b["spentUSD"], 1.10)
        self.assertAlmostEqual(b["reservedUSD"], 0.0)
        # settlement above the committed worst case is refused
        jk2 = led.reserve_and_open_job(1, 0, members, "0" * 64, None)
        with self.assertRaises(PipelineError):
            led.settle_job(jk2, 99.0)

    def test_version_drift_fails_closed(self):
        led = Ledger(os.path.join(self.tmp, "l.sqlite"))
        led.claim_row("urn:x", 1, "a" * 64, "kv1d-x")
        self.assertFalse(led.claim_row("urn:x", 1, "a" * 64, "kv1d-x"))  # idempotent re-claim
        with self.assertRaises(PipelineError) as cm:
            led.claim_row("urn:x", 1, "b" * 64, "kv1d-y")
        self.assertEqual(cm.exception.code, "ERR_VERSION_DRIFT")


class TestCrashWindows(unittest.TestCase):
    """P5 (§10.6): both crash windows via subprocess SIGKILL + the r5
    fail-closed listing cases + the same-membership collision case."""

    N = 40

    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=common.OUT_DIR)
        shutil.copyfile(WORKLIST, os.path.join(self.tmp, "worklist.jsonl"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _restart_pilot(self):
        p = orchestrator.Pilot(out_dir=self.tmp,
                               ledger_path=os.path.join(self.tmp, "ledger.sqlite"),
                               provider_dir=os.path.join(self.tmp, "provider"),
                               store_dir=os.path.join(self.tmp, "store"))
        p.load_worklist(os.path.join(self.tmp, "worklist.jsonl"), limit=self.N)
        return p

    def _crash(self, mode):
        env = dict(os.environ, LK_CRASH=mode)
        proc = subprocess.run([sys.executable, CRASH_DRIVER, self.tmp, str(self.N)],
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, -signal.SIGKILL,
                         "driver must die by SIGKILL, got %r %s" % (proc.returncode, proc.stderr[:200]))

    def _finish_and_close(self, pilot):
        drafter = mock_drafter.MockDrafter({ik: c["row"] for ik, c in pilot.by_idem.items()})
        # settle the recovered wave-0 job, then run the repair waves
        job = pilot.ledger.unsettled_jobs()[0]
        pilot.poll_to_completion(drafter)
        pilot.settle_and_process(job["jobKey"], job["batchId"], 0)
        for wave in (1, 2):
            members = pilot._members_for_wave(wave)
            if not members:
                continue
            jk, bid = pilot.submit_job(wave, 0, members)
            pilot.poll_to_completion(drafter)
            pilot.settle_and_process(jk, bid, wave)
        acct = pilot.ledger.terminal_accounting(self.N)
        self.assertTrue(acct["ok"], acct)   # zero orphaned rows, books close

    def test_window_a_pre_create(self):
        """Kill -9 after job-outbox commit, before batches.create: restart
        sweeper verifies ABSENCE by exhaustive pagination, resubmits the SAME
        outbox job once — zero duplicate paid submissions."""
        self._crash("pre_create")
        pilot = self._restart_pilot()
        jobs = pilot.ledger.unsettled_jobs()
        self.assertEqual([j["state"] for j in jobs], ["JOB_PENDING"])
        jk = jobs[0]["jobKey"]
        self.assertEqual(pilot.provider.created_count(), 0)   # provider never saw it
        actions = pilot.reconcile()
        self.assertEqual([a[0] for a in actions], [jk])
        self.assertTrue(actions[0][1].startswith("resubmitted:"))
        self.assertEqual(pilot.provider.created_count(jk), 1)
        # sweeper is idempotent: a second sweep verifies, never resubmits
        actions2 = pilot.reconcile()
        self.assertTrue(all(a[1].startswith("verified:") for a in actions2))
        self.assertEqual(pilot.provider.created_count(jk), 1)
        self._finish_and_close(pilot)

    def test_window_b_post_create(self):
        """Kill -9 after provider acceptance, before the batchId is recorded:
        restart sweeper FINDS the batch by metadata.idempotency_key and adopts
        it — zero duplicate paid submissions."""
        self._crash("post_create")
        pilot = self._restart_pilot()
        jobs = pilot.ledger.unsettled_jobs()
        self.assertEqual([j["state"] for j in jobs], ["JOB_PENDING"])
        jk = jobs[0]["jobKey"]
        self.assertEqual(pilot.provider.created_count(jk), 1)  # provider HAS it
        actions = pilot.reconcile()
        self.assertEqual(len(actions), 1)
        self.assertTrue(actions[0][1].startswith("adopted:"), actions)
        self.assertEqual(pilot.provider.created_count(jk), 1)  # no double spend
        self._finish_and_close(pilot)

    def test_midpagination_failure_fails_closed(self):
        """r5 §6: a failed list call mid-pagination is an INCOMPLETE listing
        => ERR_RECONCILE_UNVERIFIED, NO resubmission."""
        self._crash("pre_create")
        pilot = self._restart_pilot()
        # seed unrelated batches so pagination has pages to fail on
        for i in range(12):
            pilot.provider.create(b'{"custom_id":"pad%d"}\n' % i, {"idempotency_key": "pad-%d" % i})
        before = pilot.provider.created_count()
        pilot.provider.fail_list_on_page = 2
        with self.assertRaises(PipelineError) as cm:
            pilot.reconcile()
        self.assertEqual(cm.exception.code, "ERR_RECONCILE_UNVERIFIED")
        self.assertEqual(pilot.provider.created_count(), before)   # nothing resubmitted

    def test_unexhausted_cursor_fails_closed(self):
        """r5 §6: has_more=true with the next page unavailable is an
        unexhausted cursor => ERR_RECONCILE_UNVERIFIED, NO resubmission."""
        self._crash("pre_create")
        pilot = self._restart_pilot()
        for i in range(12):
            pilot.provider.create(b'{"custom_id":"pad%d"}\n' % i, {"idempotency_key": "pad-%d" % i})
        before = pilot.provider.created_count()
        pilot.provider.truncate_list_pages = 1     # page 1 lies has_more, page 2 unavailable
        with self.assertRaises(PipelineError) as cm:
            pilot.reconcile()
        self.assertEqual(cm.exception.code, "ERR_RECONCILE_UNVERIFIED")
        self.assertEqual(pilot.provider.created_count(), before)

    def test_same_membership_distinct_jobkeys_reconcile(self):
        """r5 §6 collision case: a repair wave with byte-identical membership
        carries a DISTINCT jobKey and reconciliation adopts each wave's OWN
        batch, never the other's."""
        pilot = self._restart_pilot()
        members = sorted(pilot.by_idem.keys())[:5]
        jk0, bid0 = pilot.submit_job(0, 0, members)
        # repair wave, same membership, crash post-create
        pilot.provider.crash_on_create = True
        input_bytes = pilot.build_input(members, 1)
        import hashlib as _h
        jk1 = pilot.ledger.reserve_and_open_job(1, 0, members,
                                                _h.sha256(input_bytes).hexdigest(), None)
        self.assertNotEqual(jk0, jk1)
        with self.assertRaises(mock_batch.CrashInjected):
            pilot.provider.create(input_bytes, metadata={"idempotency_key": jk1, "wave": "1", "attempt": "0"})
        actions = dict(pilot.reconcile())
        self.assertTrue(actions[jk0].startswith("verified:" + bid0))
        adopted_bid = actions[jk1].split(":", 1)[1]
        self.assertNotEqual(adopted_bid, bid0)     # never the draft wave's batch
        self.assertEqual(pilot.provider.retrieve(adopted_bid)["metadata"]["idempotency_key"], jk1)


class TestFamilyAndStatusGates(unittest.TestCase):
    """P8 fail paths (§9.1) + the §9.2 consumer gate, on the PINNED plainv5
    machinery (never re-typed)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=common.OUT_DIR)
        self.ledger_path = os.path.join(self.tmp, "seat.jsonl")
        invoke_seat.init_author(self.ledger_path, common.FAMILY_MAP,
                                common.MODEL_SNAPSHOT_ID,
                                prompt_sha256="a" * 64, output_sha256="b" * 64)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_fd2_same_family_refused_pre_dispatch(self):
        called = []

        def dispatch(_):
            called.append(1)
            return b"x"
        with self.assertRaises(invoke_seat.SeatRefusal) as cm:
            invoke_seat.invoke(self.ledger_path, common.FAMILY_MAP, "review-seat",
                               "gpt-5.6-turbo-20260401", b"prompt", dispatch)
        self.assertEqual(cm.exception.code, "FD-2")
        self.assertEqual(called, [])               # REFUSED before any call

    def test_fd1_unknown_family_refused(self):
        with self.assertRaises(invoke_seat.SeatRefusal) as cm:
            invoke_seat.invoke(self.ledger_path, common.FAMILY_MAP, "review-seat",
                               "frontier-mystery-20260101", b"prompt", lambda b: b"x")
        self.assertEqual(cm.exception.code, "FD-1")

    def test_cross_family_seat_allowed_and_ledgered(self):
        out, entry = invoke_seat.invoke(self.ledger_path, common.FAMILY_MAP, "review-seat",
                                        "claude-opus-4-20250514", b"prompt", lambda b: b"ok")
        self.assertEqual(out, b"ok")
        self.assertEqual(entry["resolved_family"], "anthropic")
        self.assertEqual(invoke_seat.verify(self.ledger_path), [])   # chain green

    def test_provenance_gpt_not_a_family(self):
        fmap = invoke_seat.load_family_map(common.FAMILY_MAP)
        findings, _ = cfd.check_provenance(
            {"draftAuthor": common.MODEL_SNAPSHOT_ID, "authorFamily": "gpt"}, fmap)
        self.assertTrue(any(c == "ERR_FAMILY_PROVENANCE" for c, _ in findings))
        findings_ok, _ = cfd.check_provenance(
            {"draftAuthor": common.MODEL_SNAPSHOT_ID, "authorFamily": "openai"}, fmap)
        self.assertEqual(findings_ok, [])
        self.assertEqual(cfd.resolve_family(common.MODEL_SNAPSHOT_ID, fmap), "openai")

    def test_status_ineligible_consumer_gate(self):
        shard = os.path.join(self.tmp, "shard-0000.jsonl")
        with open(shard, "w") as f:
            f.write(json.dumps({"id": "urn:kernel-v1-draft:x@v1", "semanticStatus": "ModelDrafted"}) + "\n")
        fail = accept_mod.check_status_eligibility_jsonl([shard], {"Explicated"})
        self.assertTrue(fail and fail[0][0] == "ERR_STATUS_INELIGIBLE")
        ok = accept_mod.check_status_eligibility_jsonl([shard], {"ModelDrafted"})
        self.assertEqual(ok, [])
        empty = accept_mod.check_status_eligibility_jsonl([shard], set())
        self.assertTrue(empty and empty[0][0] == "ERR_STATUS_INELIGIBLE")  # never default-pass


class TestAcceptanceStack(unittest.TestCase):
    def test_failure_modes_route_to_the_right_codes(self):
        row = {"conceptId": "urn:lexical-wn31:n-99999999", "lemma": "widget", "pos": "n",
               "wnGloss": "a made thing used in examples", "sourceRowSha256": "0" * 64}
        good = mock_drafter.make_ast("urn:x-good", "n")
        drafts = {
            "good": good,
            "badprime": mock_drafter.make_ast("urn:x-bp", "n", broken="bad_prime"),
            "badref": mock_drafter.make_ast("urn:x-br", "n", broken="bad_ref"),
            "outcat": mock_drafter.make_ast("urn:x-oc", "n", broken="out_of_catalog"),
        }
        per_id, reports = accept_mod.validate_shards(drafts)
        self.assertTrue(per_id["good"][0])
        self.assertEqual(per_id["badprime"], (False, "ERR_PRIME_UNKNOWN"))
        self.assertIn(per_id["badref"][1], ("ERR_REF_UNDECLARED", "ERR_REF_NOT_INTRODUCED"))
        self.assertEqual(per_id["outcat"], (False, "ERR_REF_OUTSIDE_CATALOG"))
        self.assertGreater(reports[0]["encode"]["attempted"], 0)  # opts.concepts path ran
        # gloss lints (§4.1 item 4)
        self.assertIn("ERR_GLOSS_TOO_SHORT", accept_mod.lint_gloss("too short", "widget"))
        self.assertIn("ERR_GLOSS_CIRCULAR", accept_mod.lint_gloss(
            "a widget is exactly the thing that this gloss must never name and yet here it is named twice widget", "widget"))
        leak = accept_mod.MOCK_EVAL_ITEMS[0]
        self.assertIn("ERR_LEAKAGE", accept_mod.lint_gloss(
            "surrounding words " + leak + " more words to reach the floor easily now", "widget"))
        ok_gloss = mock_drafter.make_gloss("urn:x-good", "widget", "n", "a made thing used in examples")
        self.assertEqual(accept_mod.lint_gloss(ok_gloss, "widget"), [])
        # output protocol (§2.3, §10.3)
        self.assertEqual(accept_mod.parse_output('{"cannot_draft":{"reason":"r"}}')[0], "abstain")
        self.assertEqual(accept_mod.parse_output('{"gloss": "tru')[0], "malformed")

    def test_request_bytes_deterministic(self):
        rb1, rb2 = prompt_mod.RequestBuilder(), prompt_mod.RequestBuilder()
        self.assertEqual(rb1.cache_prefix_hash, rb2.cache_prefix_hash)
        row = {"conceptId": "urn:lexical-wn31:n-00001740", "lemma": "entity", "pos": "n",
               "wnGloss": "g", "sourceRowSha256": "0" * 64}
        self.assertEqual(rb1.build_line(row, "kv1d-t"), rb2.build_line(row, "kv1d-t"))
        self.assertEqual(rb1.version_ids(row), rb2.version_ids(row))


class TestKillLadder(unittest.TestCase):
    def test_250_checkpoint_aborts_invalid_instrument(self):
        tmp = tempfile.mkdtemp(dir=common.OUT_DIR)
        try:
            pilot = scratch_pilot(tmp, 20)
            # force spend past both rungs with almost nothing attempted
            pilot.ledger.db.execute("BEGIN IMMEDIATE")
            pilot.ledger.db.execute("UPDATE budget SET spentUSD=260 WHERE id=1")
            pilot.ledger.db.execute("COMMIT")
            pilot.usage_totals.update(input=1000, cached=900, output=10)
            with self.assertRaises(PipelineError) as cm:
                pilot._kill_ladder_check()
            self.assertEqual(cm.exception.code, "ERR_KILL_LADDER")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
