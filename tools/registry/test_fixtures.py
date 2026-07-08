#!/usr/bin/env python3
"""Fixture tests for the P2 honesty-tooling spine (P2 §5.7 item 1; R-4 discipline).

    python3 tools/registry/test_fixtures.py [-v]

Every expected value marked HAND-COMPUTED was derived independently of the
implementation under test:
  - sha256 constants via `printf '<bytes>' | sha256sum` on this box;
  - Wilson lower bounds via the closed-form score bound evaluated by hand
    (z=1.645): p=0.95, n=50  -> 0.87238 (< 0.9 threshold: UNDECIDABLE, the
    RT-4 example); p=0.95, n=500 -> 0.9314 (> 0.9: powered);
  - the mock analysis ratio: two runs of {gloss_zstd_bytes: 990,
    kernel_pack_bytes: 300} -> 1980/600 = 3.3, which fires verdict rule
    index 1 (PASS, gte 2.0) and never rule 0 (FAIL, lt 2.0).

Tests exercise the real CLIs via subprocess against a throwaway root, so the
argparse surface, exit codes, and ERR_* codes are part of what is pinned.
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
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import kot_common as kc

PREREG_FREEZE = os.path.join(HERE, "prereg-freeze.py")
LOG_APPEND = os.path.join(HERE, "log-append.py")
REGISTRY_CHECK = os.path.join(HERE, "registry-check.py")
VERDICT_GEN = os.path.join(HERE, "verdict-gen.py")
REPORT_GEN = os.path.join(HERE, "report-gen.py")

MOCK_ANALYSIS = """\
import json, sys
recs = [json.loads(l) for l in sys.stdin if l.strip()]
k = sum(r["metrics"]["kernel_pack_bytes"] for r in recs)
g = sum(r["metrics"]["gloss_zstd_bytes"] for r in recs)
print(json.dumps({"ratio": g / k, "n_runs": len(recs)}))
"""


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_cli(script, *args, stdin=None):
    return subprocess.run([sys.executable, script] + list(args),
                          input=stdin, capture_output=True, text=True)


class SpineFixture(unittest.TestCase):
    """Shared throwaway-root scaffolding."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="kot-fixture-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        for d in ("registry/schema", "registry/experiments", "registry/verdicts",
                  "results-log", "reports/auto", "docs", "analysis", "data/mock-corpus"):
            os.makedirs(os.path.join(self.root, d), exist_ok=True)
        for schema in ("kot-reg-1.json", "kot-log-1.json"):
            shutil.copy(os.path.join(REPO, "registry", "schema", schema),
                        os.path.join(self.root, "registry", "schema", schema))
        self.write("docs/prereg.md", "mock prereg text\n")
        self.write("docs/sap.md", "mock statistical analysis plan\n")
        self.write("analysis/mock_analysis.py", MOCK_ANALYSIS)
        self.write("data/mock-corpus/records.jsonl", '{"id":"mock-1"}\n')

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def path(self, rel):
        return os.path.join(self.root, rel)

    def base_record(self, exp_id="mock-f1", **overrides):
        rec = {
            "schema_version": "kot-reg/1",
            "id": exp_id,
            "title": "mock byte accounting experiment",
            "hypotheses": ["HE5"],
            "prereg_doc": {"path": "docs/prereg.md", "anchors": ["HE5"],
                           "sha256": sha256_file(self.path("docs/prereg.md"))},
            "design": {
                "independent_vars": [{"name": "arm", "levels": ["kotk2-vs-gloss"]}],
                "dependent_vars": [
                    {"name": "kernel_pack_bytes", "unit": "bytes", "better": "lower",
                     "definition": "bytes of the packed kernel store"},
                    {"name": "gloss_zstd_bytes", "unit": "bytes", "better": "n/a",
                     "definition": "bytes of the zstd-compressed gloss text store"},
                ],
                "arms_mandatory_baselines": ["compressed-text-store"],
                "scale_rungs": ["S3"],
                "seeds": [0, 1],
                "n_planned": {"per_arm_items": 1},
            },
            "pins": {
                "corpus_hashes": {"_recipe": kc.CORPUS_RECIPE,
                                  "mock-corpus": kc.corpus_hash(self.root, "mock-corpus")},
                "analysis_script": {
                    "path": "analysis/mock_analysis.py",
                    "sha256": sha256_file(self.path("analysis/mock_analysis.py")),
                    "output_fields": ["/ratio", "/n_runs"],
                },
            },
            "analysis_plan_ref": {"path": "docs/sap.md", "anchor": "mock-f1",
                                  "sha256": sha256_file(self.path("docs/sap.md"))},
            "endpoints": [
                {"id": "primary", "role": "primary", "metric": "/ratio",
                 "test": "raw byte ratio vs the pre-registered 2.0 line"},
            ],
            "verdict_rules": [
                {"verdict": "FAIL", "when": {"op": "lt", "a": {"metric": "/ratio"}, "b": {"const": 2.0}}},
                {"verdict": "PASS", "when": {"op": "gte", "a": {"metric": "/ratio"}, "b": {"const": 2.0}}},
                {"verdict": "INCONCLUSIVE", "when": {"const": True}},
            ],
            "kill_criterion_verbatim": "byte claim dropped if <2x vs compressed gloss text",
            "extrapolation_envelope_verbatim": "store-size axis extrapolates freely; no model-scale claim",
            "budget": {"usd_cap": 0},
            "status": "DRAFT",
        }
        rec.update(overrides)
        return rec

    def freeze(self, rec):
        self.write("registry/experiments/%s.json" % rec["id"], json.dumps(rec) + "\n")
        return run_cli(PREREG_FREEZE, "--experiment", rec["id"], "--agent-id", "coordinator-1",
                       "--root", self.root, "--frozen-at", "2026-07-08T00:00:00Z")

    def frozen_sha(self, exp_id):
        with open(self.path("registry/frozen-index.json"), encoding="utf-8") as f:
            return json.load(f)[exp_id]

    def append_run(self, exp_id, seed, metrics=None, exit_code="ok", phase="final"):
        body = {
            "event": "run", "phase": phase,
            "prereg_hash": self.frozen_sha(exp_id),
            "config": {"arm": "kotk2-vs-gloss", "seed": seed},
            "metrics": metrics or {"kernel_pack_bytes": 300, "gloss_zstd_bytes": 990, "n_records": 10},
            "exit": exit_code,
        }
        return run_cli(LOG_APPEND, "--experiment", exp_id, "--agent-id", "runner-1",
                       "--record", "-", "--root", self.root,
                       "--ts", "2026-07-08T00:00:0%dZ" % seed, stdin=json.dumps(body))


class TestCanonicalHash(SpineFixture):
    def test_canonical_hash_determinism(self):
        # HAND-COMPUTED: printf '{"a":"x","b":1}' | sha256sum
        self.assertEqual(kc.canonical_dumps({"b": 1, "a": "x"}), '{"a":"x","b":1}')
        self.assertEqual(kc.canonical_sha256({"b": 1, "a": "x"}),
                         "cdab067e9f3beb32d1252cfd63e492592fecbf591b0d08cadb24bb17f3864246")
        # HAND-COMPUTED (UTF-8, not \\u-escaped): printf '{"a":[1,2],"z":"café"}' | sha256sum
        self.assertEqual(kc.canonical_dumps({"z": "café", "a": [1, 2]}), '{"a":[1,2],"z":"café"}')
        self.assertEqual(kc.canonical_sha256({"z": "café", "a": [1, 2]}),
                         "10dd2543ed2e061af2db7f3ce20993a1466011a19247977f67ab7355dfcd93bd")
        # key-order independence
        self.assertEqual(kc.canonical_sha256(json.loads('{"x":1,"y":{"b":2,"a":3}}')),
                         kc.canonical_sha256(json.loads('{"y":{"a":3,"b":2},"x":1}')))
        # frozen hash excludes exactly status + frozen_sha256 (P2 §1.1)
        self.assertEqual(kc.frozen_hash({"b": 1, "a": "x", "status": "FROZEN", "frozen_sha256": "f" * 64}),
                         kc.canonical_sha256({"b": 1, "a": "x"}))

    def test_freeze_is_reproducible(self):
        rec = self.base_record()
        p = self.freeze(rec)
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(self.path("registry/experiments/mock-f1.json"), encoding="utf-8") as f:
            frozen = json.load(f)
        self.assertEqual(frozen["status"], "FROZEN")
        self.assertEqual(kc.frozen_hash(frozen), self.frozen_sha("mock-f1"))
        self.assertEqual(frozen["frozen_sha256"], self.frozen_sha("mock-f1"))
        # re-freezing an already-frozen id is refused
        p2 = self.freeze(frozen)
        self.assertNotEqual(p2.returncode, 0)
        self.assertIn("ERR_P2_ALREADY_FROZEN", p2.stderr)


class TestChainTamper(SpineFixture):
    def test_chain_tamper_detection(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        for seed in (0, 1):
            p = self.append_run("mock-f1", seed)
            self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(REGISTRY_CHECK, "--root", self.root)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

        # Tamper with a mid-log byte, preserving length and JSON validity:
        # 990 -> 991 in seq 0's metrics (the edited-mid-log-line fixture, P2 §5.7).
        log = self.path("results-log/mock-f1.jsonl")
        with open(log, "rb") as f:
            lines = f.readlines()
        self.assertIn(b'"gloss_zstd_bytes":990', lines[0])
        lines[0] = lines[0].replace(b'"gloss_zstd_bytes":990', b'"gloss_zstd_bytes":991')
        with open(log, "wb") as f:
            f.writelines(lines)

        p = run_cli(REGISTRY_CHECK, "--chain", "--root", self.root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_CHAIN", p.stdout + p.stderr)
        # and log-append itself refuses to extend a broken chain (fail closed)
        p = self.append_run("mock-f1", 1)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_CHAIN", p.stderr)


class TestAccountStrings(SpineFixture):
    def test_account_string_refusal(self):
        # an email address inside the hashed byte range refuses the freeze (RT-14)
        rec = self.base_record(title="mock experiment, contact someone@example.com")
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_ACCOUNT_IN_RECORD", p.stderr)
        # the maintainer account string anywhere in hashed bytes also refuses
        rec = self.base_record(title="as requested by jeswr")
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_ACCOUNT_IN_RECORD", p.stderr)

    def test_non_pseudonym_identity_refused(self):
        rec = self.base_record()
        self.write("registry/experiments/%s.json" % rec["id"], json.dumps(rec) + "\n")
        p = run_cli(PREREG_FREEZE, "--experiment", rec["id"], "--agent-id", "kern-agent",
                    "--root", self.root, "--frozen-at", "2026-07-08T00:00:00Z")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_ACCOUNT_IN_RECORD", p.stderr)


class TestVerdictGrammar(SpineFixture):
    def test_verdict_rules_evaluation(self):
        doc = {"analysis": {"gap": 0.63, "flag": True}, "ratio": 3.3}
        gte = {"op": "gte", "a": {"metric": "/ratio"}, "b": {"const": 2.0}}
        lt = {"op": "lt", "a": {"metric": "/ratio"}, "b": {"const": 2.0}}
        self.assertTrue(kc.eval_expr(gte, doc))
        self.assertFalse(kc.eval_expr(lt, doc))
        self.assertTrue(kc.eval_expr({"op": "and", "a": gte, "b": {"metric": "/analysis/flag"}}, doc))
        self.assertTrue(kc.eval_expr({"op": "or", "a": lt, "b": gte}, doc))
        self.assertFalse(kc.eval_expr({"op": "not", "a": gte}, doc))
        self.assertTrue(kc.eval_expr({"op": "eq", "a": {"metric": "/analysis/gap"}, "b": {"const": 0.63}}, doc))
        self.assertTrue(kc.eval_expr({"const": True}, doc))
        # missing pointer fails closed
        with self.assertRaises(kc.MissingMetric):
            kc.eval_expr({"op": "gt", "a": {"metric": "/analysis/absent"}, "b": {"const": 0}}, doc)
        # a non-boolean bare metric is a grammar error, not a truthiness guess
        with self.assertRaises(kc.KotError):
            kc.eval_expr({"metric": "/ratio"}, doc)
        # first-match-wins over the mock F1 rule list (HAND-COMPUTED: 3.3 -> index 1 PASS; 1.5 -> index 0 FAIL)
        rules = self.base_record()["verdict_rules"]
        fired = next(i for i, r in enumerate(rules) if kc.eval_expr(r["when"], {"ratio": 3.3}))
        self.assertEqual((fired, rules[fired]["verdict"]), (1, "PASS"))
        fired = next(i for i, r in enumerate(rules) if kc.eval_expr(r["when"], {"ratio": 1.5}))
        self.assertEqual((fired, rules[fired]["verdict"]), (0, "FAIL"))


class TestDerivedStatRejection(SpineFixture):
    def test_derived_stat_rejection(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        # clean raw metrics append fine
        p = self.append_run("mock-f1", 0)
        self.assertEqual(p.returncode, 0, p.stderr)
        # a p-value at any depth under metrics is refused (P2 §2.4)
        p = self.append_run("mock-f1", 1, metrics={"acc": 0.5, "stats": {"p_value": 0.03}})
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_DERIVED_STAT", p.stderr)
        # so is an effect size at the top level
        p = self.append_run("mock-f1", 1, metrics={"effect_size": 0.5})
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_DERIVED_STAT", p.stderr)


class TestFreezeLints(SpineFixture):
    def test_two_primaries_refused(self):
        rec = self.base_record()
        rec["endpoints"].append({"id": "second", "role": "primary", "metric": "/n_runs", "test": "dup"})
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_ENDPOINTS", p.stderr)

    def test_missing_catchall_refused(self):
        rec = self.base_record()
        rec["verdict_rules"] = rec["verdict_rules"][:-1]
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_RULES_NOT_EXHAUSTIVE", p.stderr)

    def test_unknown_pointer_refused(self):
        rec = self.base_record()
        rec["verdict_rules"][0]["when"]["a"]["metric"] = "/undeclared_field"
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_UNKNOWN_POINTER", p.stderr)

    def test_wilson_unpowered_gate_refused(self):
        # HAND-COMPUTED (z=1.645): lb(0.95, n=50) = 0.87238 <= 0.9 -> undecidable (RT-4's example);
        #                          lb(0.95, n=500) = 0.9314  >  0.9 -> powered.
        self.assertAlmostEqual(kc.wilson_lower_bound(0.95, 50), 0.87238, places=5)
        self.assertAlmostEqual(kc.wilson_lower_bound(0.95, 500), 0.9314, places=4)
        rec = self.base_record()
        rec["endpoints"][0]["wilson_gate"] = {"threshold": 0.9, "n_planned": 50, "expected_rate": 0.95}
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_UNPOWERED_GATE", p.stderr)
        rec = self.base_record()
        rec["endpoints"][0]["wilson_gate"] = {"threshold": 0.9, "n_planned": 500, "expected_rate": 0.95}
        p = self.freeze(rec)
        self.assertEqual(p.returncode, 0, p.stderr)


class TestFrozenDrift(SpineFixture):
    def test_frozen_drift_detection(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(REGISTRY_CHECK, "--frozen-drift", "--root", self.root)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        with open(self.path("registry/experiments/mock-f1.json"), encoding="utf-8") as f:
            frozen = json.load(f)
        frozen["title"] = "quietly relaxed title"
        self.write("registry/experiments/mock-f1.json", json.dumps(frozen) + "\n")
        p = run_cli(REGISTRY_CHECK, "--frozen-drift", "--root", self.root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_FROZEN_DRIFT", p.stdout + p.stderr)


class TestEndToEnd(SpineFixture):
    def test_verdict_pass_pending_audit(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        for seed in (0, 1):
            p = self.append_run("mock-f1", seed)
            self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(VERDICT_GEN, "--experiment", "mock-f1", "--agent-id", "coordinator-1",
                    "--root", self.root, "--computed-at", "2026-07-08T01:00:00Z")
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(self.path("registry/verdicts/mock-f1.json"), encoding="utf-8") as f:
            verdict = json.load(f)
        # HAND-COMPUTED: 2 x (990 gloss / 300 kernel) = 1980/600 = 3.3 >= 2.0 -> rule 1, PASS,
        # emitted as PASS-PENDING-AUDIT because no CONFIRMED audit record exists (G-6).
        self.assertEqual(verdict["verdict"], "PASS-PENDING-AUDIT")
        self.assertEqual(verdict["fired_rule_index"], 1)
        self.assertEqual(verdict["inputs"]["eligible_runs"], 2)
        self.assertEqual(verdict["inputs"]["excluded_runs"], [])
        self.assertEqual(verdict["kill_criterion_verbatim"],
                         "byte claim dropped if <2x vs compressed gloss text")
        with open(self.path("reports/auto/mock-f1/analysis-output.json"), encoding="utf-8") as f:
            analysis = json.load(f)
        self.assertEqual(analysis, {"ratio": 3.3, "n_runs": 2})
        # the unblind line was appended through the single write path
        records, _ = kc.read_log(self.path("results-log/mock-f1.jsonl"))
        self.assertEqual([r["event"] for r in records], ["run", "run", "unblind"])
        # and the whole tree still lints
        p = run_cli(REGISTRY_CHECK, "--root", self.root)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_incomplete_data_when_no_eligible_runs(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        # an exploratory run exists but nothing final -> INCOMPLETE-DATA, exclusion named
        p = self.append_run("mock-f1", 0, phase="exploratory")
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(VERDICT_GEN, "--experiment", "mock-f1", "--agent-id", "coordinator-1",
                    "--root", self.root, "--computed-at", "2026-07-08T01:00:00Z")
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(self.path("registry/verdicts/mock-f1.json"), encoding="utf-8") as f:
            verdict = json.load(f)
        self.assertEqual(verdict["verdict"], "INCOMPLETE-DATA")
        self.assertEqual(verdict["inputs"]["eligible_runs"], 0)
        self.assertEqual(verdict["inputs"]["excluded_runs"],
                         [{"seq": 0, "reason": "phase!=final ('exploratory')"}])


class TestCorpusPins(SpineFixture):
    def test_wrong_digest_refused_at_freeze(self):
        rec = self.base_record()
        rec["pins"]["corpus_hashes"]["mock-corpus"] = "0" * 64
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_CORPUS_PIN", p.stderr)

    def test_legacy_recipe_refused_at_freeze(self):
        rec = self.base_record()
        rec["pins"]["corpus_hashes"]["_recipe"] = "sha256 over some ambiguous prose recipe"
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_CORPUS_PIN", p.stderr)

    def test_pinned_at_inputs_placeholder_allowed(self):
        rec = self.base_record()
        rec["pins"]["corpus_hashes"]["future-inputs"] = "PINNED-AT-INPUTS:mock.inputs (ops amendment)"
        p = self.freeze(rec)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_registry_check_detects_post_freeze_corpus_drift(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(REGISTRY_CHECK, "--corpus-pins", "--root", self.root)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        # corpus bytes change after the freeze -> ERR_P2_CORPUS_PIN
        self.write("data/mock-corpus/records.jsonl", '{"id":"mock-1","quietly":"grown"}\n')
        p = run_cli(REGISTRY_CHECK, "--corpus-pins", "--root", self.root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_CORPUS_PIN", p.stdout + p.stderr)


class TestReportGen(SpineFixture):
    def test_report_renders_kill_beside_verdict(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        for seed in (0, 1):
            p = self.append_run("mock-f1", seed)
            self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(VERDICT_GEN, "--experiment", "mock-f1", "--agent-id", "coordinator-1",
                    "--root", self.root, "--computed-at", "2026-07-08T01:00:00Z")
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run_cli(REPORT_GEN, "--experiment", "mock-f1", "--root", self.root)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        with open(self.path("reports/auto/mock-f1/verdict-mock-f1.md"), encoding="utf-8") as f:
            md = f.read()
        # fixed template invariants (P2 section 3.3): outcome copied from the
        # verdict object, kill criterion verbatim beside it, endpoints table,
        # excluded-runs section, coverage disclosure, envelope verbatim.
        self.assertIn("## OUTCOME: **PASS-PENDING-AUDIT**", md)
        self.assertIn("byte claim dropped if <2x vs compressed gloss text", md)
        self.assertIn("| primary | primary | `/ratio` | 3.3 |", md)
        self.assertIn("## Eligible & excluded runs", md)
        self.assertIn("2 eligible final run(s).", md)
        self.assertIn("## Coverage disclosure (mandatory)", md)
        self.assertIn("store-size axis extrapolates freely", md)
        self.assertIn("Not citable as PASS until", md)

    def test_report_refuses_drifted_record(self):
        p = self.freeze(self.base_record())
        self.assertEqual(p.returncode, 0, p.stderr)
        self.append_run("mock-f1", 0)
        p = run_cli(VERDICT_GEN, "--experiment", "mock-f1", "--agent-id", "coordinator-1",
                    "--root", self.root, "--computed-at", "2026-07-08T01:00:00Z")
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(self.path("registry/experiments/mock-f1.json"), encoding="utf-8") as f:
            frozen = json.load(f)
        frozen["title"] = "quietly relaxed title"
        self.write("registry/experiments/mock-f1.json", json.dumps(frozen) + "\n")
        p = run_cli(REPORT_GEN, "--experiment", "mock-f1", "--root", self.root)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_FROZEN_DRIFT", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
