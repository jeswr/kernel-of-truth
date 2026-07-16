#!/usr/bin/env python3
"""test_family_disjoint.py — GREEN fail-path tests for the family-disjointness
machinery (largekern pilot precondition P8).

Per docs/next/design/gpt56-draft-pipeline-large-kernel.md §9.1 P8 and
docs/next/design/plain-v5-register-lint-spec.md §7 (code numbering = the
pinned plain-v5 list: FD-1 UNKNOWN, FD-2 same-family): each test drives the
REAL runnable surface (CLI subprocess or library) with the malformed /
ineligible input the specs define and asserts the machinery fails closed —
a passing (green) test here means the fail path fires. Owner: coordinator-1,
2026-07-16. Stdlib only.

Run: python3 poc/plainv5/test_family_disjoint.py -v
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_family_disjoint as cfd  # noqa: E402
import invoke_seat as iseat  # noqa: E402

PY = sys.executable
MAP = os.path.join(HERE, "family-map.json")
INVOKER = os.path.join(HERE, "invoke_seat.py")
VALIDATOR = os.path.join(HERE, "check_family_disjoint.py")

AUTHOR_ID = "gpt-5.6-sol-20260601"          # exact dated author id (largekern §8 shape)
CLAUDE_ID = "claude-opus-4-20250514"        # anthropic seat
GEMINI_ID = "gemini-2.5-pro-20250605"       # google seat
UNKNOWN_ID = "mystery-net-20260101"          # matches no pinned rule => UNKNOWN
SAME_FAMILY_ID = "gpt-4.1-2025-04-14"        # openai, same family as the author

sha = lambda b: hashlib.sha256(b).hexdigest()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def run(argv, **kw):
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw)


class LedgerFixture(unittest.TestCase):
    """Shared green fixture: entry 0 (gpt author) + two disjoint seats."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="p8-fd-")
        self.ledger = os.path.join(self.tmp, "seat-ledger.jsonl")
        self.outputs = os.path.join(self.tmp, "outputs")
        os.makedirs(self.outputs)
        r = run([PY, INVOKER, "init-author", "--ledger", self.ledger, "--family-map", MAP,
                 "--model-id", AUTHOR_ID,
                 "--prompt-sha256", sha(b"authoring-prompt"),
                 "--output-sha256", sha(b"drafted-store")])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.declared = os.path.join(self.tmp, "declared.json")
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": CLAUDE_ID},
                       {"seat_role": "fidelity-seat", "model_id": GEMINI_ID}], f)
        self.manifest = os.path.join(self.tmp, "manifest.json")
        with open(self.manifest, "w") as f:
            json.dump({"draftAuthor": AUTHOR_ID, "authorFamily": "openai"}, f)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cli_invoke(self, role, model_id, prompt=b"seat prompt bytes", dispatch=None):
        pfile = os.path.join(self.tmp, "prompt-%s.txt" % role)
        ofile = os.path.join(self.outputs, "out-%s.txt" % role)
        with open(pfile, "wb") as f:
            f.write(prompt)
        r = run([PY, INVOKER, "invoke", "--ledger", self.ledger, "--family-map", MAP,
                 "--seat-role", role, "--model-id", model_id,
                 "--prompt-file", pfile, "--output-file", ofile,
                 "--dispatch-cmd", dispatch or "cat"])
        return r, ofile

    def green_ledger(self):
        r1, _ = self.cli_invoke("gate-judge", CLAUDE_ID)
        self.assertEqual(r1.returncode, 0, r1.stdout)
        r2, _ = self.cli_invoke("fidelity-seat", GEMINI_ID)
        self.assertEqual(r2.returncode, 0, r2.stdout)

    def validate(self, extra=()):
        return run([PY, VALIDATOR, "--family-map", MAP, "--manifest", self.manifest,
                    "--declared", self.declared, "--runtime-ledger", self.ledger,
                    "--outputs-dir", self.outputs] + list(extra))


class TestResolveFamily(unittest.TestCase):
    """The largekern authorFamily provenance anchor: ^gpt- => "openai"."""

    def test_gpt_resolves_openai(self):
        self.assertEqual(cfd.resolve_family("gpt-5.6-sol-20260601"), "openai")
        self.assertEqual(cfd.resolve_family(AUTHOR_ID), "openai")
        self.assertEqual(cfd.resolve_family("gpt-4.1-2025-04-14"), "openai")
        self.assertEqual(cfd.resolve_family("o3-2025-04-16"), "openai")
        self.assertEqual(cfd.resolve_family("codex-mini-20250516"), "openai")
        # never the r2 mistake "gpt" (ASM-2478)
        self.assertNotEqual(cfd.resolve_family("gpt-5.6-sol-20260601"), "gpt")

    def test_other_families_and_normalization(self):
        self.assertEqual(cfd.resolve_family(CLAUDE_ID), "anthropic")
        self.assertEqual(cfd.resolve_family("us.anthropic.claude-3-7-sonnet-20250219-v1:0"), "anthropic")
        self.assertEqual(cfd.resolve_family("openai/gpt-4o-2024-08-06"), "openai")
        self.assertEqual(cfd.resolve_family("GLM-5-20260210"), "zhipu")
        self.assertEqual(cfd.resolve_family(GEMINI_ID), "google")
        self.assertEqual(cfd.resolve_family("deepseek-r1-20250120"), "deepseek")
        self.assertEqual(cfd.resolve_family("qwen3-235b-20250428"), "alibaba")
        self.assertEqual(cfd.resolve_family("mistral-large-2411"), "mistral")
        self.assertEqual(cfd.resolve_family("grok-4-20250709"), "xai")
        self.assertEqual(cfd.resolve_family("meta-llama-4-20250405"), "meta")

    def test_unmatched_is_unknown_never_default(self):
        self.assertEqual(cfd.resolve_family(UNKNOWN_ID), "UNKNOWN")
        self.assertEqual(cfd.resolve_family(""), "UNKNOWN")
        self.assertEqual(cfd.resolve_family(None), "UNKNOWN")

    def test_cli_resolve(self):
        r = run([PY, VALIDATOR, "--resolve", "gpt-5.6-sol-20260601"])
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.decode().strip(), "openai")
        r = run([PY, VALIDATOR, "--resolve", UNKNOWN_ID])
        self.assertEqual(r.returncode, 1)  # UNKNOWN fails closed even here


class TestFD1UnknownRefused(LedgerFixture):
    """FD-1 (plain-v5 §7): any model id resolving UNKNOWN refuses pre-dispatch."""

    def test_invoker_refuses_unknown_seat_no_api_call(self):
        canary = os.path.join(self.tmp, "canary")
        before = read_bytes(self.ledger)
        r, ofile = self.cli_invoke("gate-judge", UNKNOWN_ID, dispatch="touch %s" % canary)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-1", r.stdout.decode())
        self.assertFalse(os.path.exists(canary), "dispatch ran despite FD-1 — API call not refused")
        self.assertFalse(os.path.exists(ofile))
        self.assertEqual(read_bytes(self.ledger), before, "refused call must not enter the ledger")

    def test_validator_flags_unknown_declared_seat(self):
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": UNKNOWN_ID}], f)
        # runtime ledger untouched (author only) => also role-set mismatch, but FD-1 must be present
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-1", r.stdout.decode())

    def test_init_author_refuses_unknown_author(self):
        ledger2 = os.path.join(self.tmp, "l2.jsonl")
        r = run([PY, INVOKER, "init-author", "--ledger", ledger2, "--family-map", MAP,
                 "--model-id", UNKNOWN_ID, "--prompt-sha256", sha(b"p"), "--output-sha256", sha(b"o")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL FD-1", r.stdout.decode())


class TestFD2SameFamilyRefused(LedgerFixture):
    """FD-2 (plain-v5 §7): family(seat) == family(entry 0) refuses pre-dispatch."""

    def test_invoker_refuses_same_family_no_api_call(self):
        canary = os.path.join(self.tmp, "canary")
        before = read_bytes(self.ledger)
        r, _ = self.cli_invoke("gate-judge", SAME_FAMILY_ID, dispatch="touch %s" % canary)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-2", r.stdout.decode())
        self.assertFalse(os.path.exists(canary), "dispatch ran despite FD-2 — API call not refused")
        self.assertEqual(read_bytes(self.ledger), before)

    def test_validator_flags_same_family_declared_seat(self):
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": SAME_FAMILY_ID}], f)
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-2", r.stdout.decode())


class TestFD5Orphans(LedgerFixture):
    """FD-5 (plain-v5 §7 r3): orphan output files and never-completed entries."""

    def test_orphan_output_file_detected(self):
        self.green_ledger()
        with open(os.path.join(self.outputs, "rogue.txt"), "wb") as f:
            f.write(b"output of a direct (un-ledgered) model call")
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-5", r.stdout.decode())
        self.assertIn("rogue.txt", r.stdout.decode())

    def test_pending_entry_detected_and_blocks_invoker(self):
        self.green_ledger()
        # simulate a crash mid-dispatch: correctly-chained entry, output never completed
        rows = iseat.read_ledger(self.ledger)
        pend = dict(rows[-1][0])
        pend.update(seq=len(rows), prev_sha256=sha(rows[-1][1]),
                    seat_role="screen-seat", model_id=GEMINI_ID, output_sha256=None)
        with open(self.ledger, "ab") as f:
            f.write(iseat.entry_line(pend))
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": CLAUDE_ID},
                       {"seat_role": "fidelity-seat", "model_id": GEMINI_ID},
                       {"seat_role": "screen-seat", "model_id": GEMINI_ID}], f)
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-5", r.stdout.decode())
        # and the invoker refuses to keep working over a pending tail
        r2, _ = self.cli_invoke("another-judge", CLAUDE_ID)
        self.assertEqual(r2.returncode, 1)
        self.assertIn("FAIL FD-5", r2.stdout.decode())


class TestFD6Integrity(LedgerFixture):
    """FD-6 (plain-v5 §7 r3): hash-chain break and role-set mismatch."""

    def test_rewritten_line_breaks_chain(self):
        self.green_ledger()
        lines = read_bytes(self.ledger).splitlines(True)
        e1 = json.loads(lines[1])
        e1["model_id"] = GEMINI_ID  # tamper a non-final entry (rewrite)
        e1["resolved_family"] = "google"
        lines[1] = iseat.entry_line(e1)
        with open(self.ledger, "wb") as f:
            f.writelines(lines)
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-6", r.stdout.decode())
        # invoke_seat verify — the run-point every consumer re-uses — agrees
        r2 = run([PY, INVOKER, "verify", "--ledger", self.ledger])
        self.assertEqual(r2.returncode, 1)
        self.assertIn("FAIL FD-6", r2.stdout.decode())

    def test_deleted_line_breaks_chain(self):
        self.green_ledger()
        lines = read_bytes(self.ledger).splitlines(True)
        with open(self.ledger, "wb") as f:
            f.writelines([lines[0], lines[2]])  # delete entry 1
        r = run([PY, INVOKER, "verify", "--ledger", self.ledger])
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL FD-6", r.stdout.decode())

    def test_declared_role_never_ledgered(self):
        self.green_ledger()
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": CLAUDE_ID},
                       {"seat_role": "fidelity-seat", "model_id": GEMINI_ID},
                       {"seat_role": "tie-break", "model_id": GEMINI_ID}], f)
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-6", r.stdout.decode())
        self.assertIn("tie-break", r.stdout.decode())

    def test_undeclared_runtime_role(self):
        self.green_ledger()
        with open(self.declared, "w") as f:
            json.dump([{"seat_role": "gate-judge", "model_id": CLAUDE_ID}], f)
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL FD-6", r.stdout.decode())


class TestStatusIneligible(LedgerFixture):
    """ERR_STATUS_INELIGIBLE (largekern §9.2): a ModelDrafted record reaching
    a slot requiring Explicated fails closed against the explicit allowlist."""

    def _records(self, *statuses):
        d = os.path.join(self.tmp, "kernel-v1-draft")
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(statuses):
            rec = {"schema": "kot-record/1", "label": "rec-%d" % i}
            if s is not None:
                rec["status"] = s
            with open(os.path.join(d, "rec-%d.json" % i), "w") as f:
                json.dump(rec, f)
        return d

    def test_modeldrafted_fails_explicated_slot(self):
        self.green_ledger()
        d = self._records("Explicated", "ModelDrafted")
        r = self.validate(extra=["--records", d, "--eligible-status", "Explicated"])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL ERR_STATUS_INELIGIBLE", r.stdout.decode())
        self.assertIn("ModelDrafted", r.stdout.decode())

    def test_missing_status_fails_closed(self):
        d = self._records(None)
        findings = cfd.check_status_eligibility(d, {"Explicated"})
        self.assertTrue(any(c == "ERR_STATUS_INELIGIBLE" for c, _ in findings))

    def test_empty_allowlist_never_default_passes(self):
        d = self._records("Explicated")
        findings = cfd.check_status_eligibility(d, set())
        self.assertTrue(any(c == "ERR_STATUS_INELIGIBLE" for c, _ in findings))

    def test_all_eligible_is_green(self):
        self.green_ledger()
        d = self._records("Explicated", "Explicated")
        r = self.validate(extra=["--records", d, "--eligible-status", "Explicated"])
        self.assertEqual(r.returncode, 0, r.stdout)


class TestProvenanceAgreement(LedgerFixture):
    """largekern §8: authorFamily == resolve_family(draftAuthor) == "openai"."""

    def test_gpt_string_family_rejected(self):
        # the exact r2 mistake: authorFamily "gpt" instead of the resolver's "openai"
        with open(self.manifest, "w") as f:
            json.dump({"draftAuthor": AUTHOR_ID, "authorFamily": "gpt"}, f)
        self.green_ledger()
        r = self.validate()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL ERR_FAMILY_PROVENANCE", r.stdout.decode())

    def test_resolver_output_satisfies_assertion(self):
        # the P8 provenance-agreement assertion, satisfiable exactly when
        # authorFamily carries the resolver's output
        self.assertEqual(cfd.resolve_family(AUTHOR_ID), "openai")
        findings, _ = cfd.check_provenance({"draftAuthor": AUTHOR_ID, "authorFamily": "openai"},
                                           cfd.load_family_map(MAP))
        self.assertEqual(findings, [])

    def test_plainv5_disclosure_shape(self):
        findings, _ = cfd.check_provenance(
            {"authoring_model": {"family": "wrong-family", "model": CLAUDE_ID}},
            cfd.load_family_map(MAP))
        self.assertTrue(any(c == "ERR_FAMILY_PROVENANCE" for c, _ in findings))


class TestFD3FD4AndGreenPath(LedgerFixture):
    """FD-3/FD-4 coverage + the full green end-to-end path."""

    def test_fd3_undated_model_id(self):
        r, _ = self.cli_invoke("gate-judge", "claude-opus")  # no dated snapshot token
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL FD-3", r.stdout.decode())
        findings = cfd.check_declared([{"seat_role": "gate-judge", "model_id": None}],
                                      "openai", cfd.load_family_map(MAP))
        self.assertTrue(any(c == "FD-3" for c, _ in findings))

    def test_fd4_absent_declared_ledger_and_undeclared_protocol_role(self):
        findings = cfd.check_declared(None, "openai", cfd.load_family_map(MAP))
        self.assertTrue(any(c == "FD-4" for c, _ in findings))
        findings = cfd.check_protocol_roles(
            "protocol: the gate-judge reads each unit; ties go to the tie-break seat.",
            [{"seat_role": "gate-judge", "model_id": CLAUDE_ID}])
        self.assertTrue(any(c == "FD-4" and "tie-break" in m for c, m in findings))

    def test_green_path_end_to_end(self):
        self.green_ledger()
        proto = os.path.join(self.tmp, "protocol.md")
        with open(proto, "w") as f:
            f.write("protocol: the gate-judge reads one unit per call; the fidelity-seat verifies the selector's synset.")
        r = self.validate(extra=["--record-text", proto])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("OK", r.stdout.decode())
        r2 = run([PY, INVOKER, "verify", "--ledger", self.ledger])
        self.assertEqual(r2.returncode, 0, r2.stdout)


if __name__ == "__main__":
    unittest.main()
