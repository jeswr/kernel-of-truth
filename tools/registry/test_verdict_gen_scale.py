#!/usr/bin/env python3
"""Scale-language licensing tests for verdict-gen (a5-llm REFUTE remediation).

    python3 tools/registry/test_verdict_gen_scale.py [-v]

Pins the per-record min-rule fix adjudicated in
docs/next/a5-llm-refute-adjudication.md section 2.2 (maintainer-approved
2026-07-11, issue #5), documented in
registry/corrections/a5-llm/2-scale-license-erratum.json, and REMEDIATED per
the cross-vendor Gate-A re-audit
poc/gpt56-review/a5llm-reaudit-20260711/last-message.json (points 3-6):

  REGRESSION    — the a5-llm configuration (4 rung labels incl. the R0
                  baseline, envelope ceiling sign-only, failed trend gates)
                  licenses "sign-only", never "slope"; verified (a) directly
                  against the real frozen a5-llm record + its real analysis
                  output, (b) end-to-end through the verdict-gen CLI on a
                  prereg-frozen fixture mirroring that configuration, and
                  (c) by REGENERATING a5-llm through the REAL verdict-gen CLI
                  against a copy of the real frozen artifacts in a throwaway
                  root (re-audit point 5) — the regenerated object differs
                  from the issued one in EXACTLY the license field. (The real
                  registry/verdicts/a5-llm.json is NOT regenerated in place —
                  S7 regeneration is coordinator-gated, adjudication decision
                  #1b/#6 — and its bytes are asserted unchanged below.)
  MINIMUM RULE  — re-audit point 3: the G-12 tier is computed over the COUNT
                  OF COMPARABLE rungs (measured rungs inside
                  design.model_scale_rungs), not raw labels — non-model
                  labels can inflate NEITHER "sign-only"->"slope" NOR
                  "none"->"sign-only" ({measured=BASE0,BASE1,R1;
                  model_scale_rungs=[R1]; ceiling=slope; trend valid} =>
                  "none").
  PRESERVATION  — G-12 (02-data-and-reporting.md:664) and 08-stats section
                  2.1 are UNCHANGED: >=3 COMPARABLE model-scale rungs with a
                  valid trend result and a slope ceiling STILL license
                  "slope" — the fix is not a blunt ">=4 rungs" rule. All 17+
                  issued verdicts sweep byte-consistent (only a5-llm and f2
                  move slope->sign-only, exactly the two errata).
  CEILING       — a frozen per-record ceiling of sign-only refuses "slope"
                  even with many comparable rungs and a valid trend result.
  SCHEMA/FREEZE — re-audit point 4: both kot-reg schemas now admit the three
                  OPTIONAL design fields (scale_language_max,
                  model_scale_rungs, scale_trend_valid_metrics), every
                  existing frozen record still validates without them, and
                  prereg-freeze refuses a machine-readable ceiling that
                  exceeds the extrapolation_envelope_verbatim text
                  (ERR_P2_SCALE_LANGUAGE, fail closed). The e2e fixtures
                  below are frozen through the REAL prereg-freeze CLI — no
                  hand-freeze bypass remains.

NOTE (conservative reading): existing FROZEN records cannot be re-run through
prereg-freeze --dry-run (status!=DRAFT / already indexed, by design), so the
backward-compatibility property "records without the fields still validate"
is pinned here as a full-index schema-validation sweep — exactly the check
prereg-freeze, the amendment overlay, and registry-check re-apply.
"""

import glob
import importlib.util
import json
import os
import shutil
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import kot_common as kc

from test_fixtures import (SpineFixture, make_temp_root, run_cli, sha256_file,
                           VERDICT_GEN, LOG_APPEND)

_spec = importlib.util.spec_from_file_location("verdict_gen", VERDICT_GEN)
vg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vg)

SCHEMA_FILES = {"kot-reg/1": "kot-reg-1.json", "kot-reg/2": "kot-reg-2.json"}

# HAND-COMPUTED this session (sha256sum registry/verdicts/{a5-llm,f2}.json);
# each is also the sha the binding correction record cites, cross-checked in
# TestIssuedVerdictSweep.test_issued_verdict_bytes_unchanged — the frozen-
# bytes-unchanged assertion the remediation is required to carry.
A5LLM_VERDICT_SHA256 = "f893cf4752389e15c72d881ac779f30677aa25e5db48796acadace7ae0e7945e"
F2_VERDICT_SHA256 = "38422b3caf5df8a339d723eaa198a26f783465667fb920c34dbb697071dd6b2e"

# Analysis mocks: same byte-accounting ratio as the spine fixture (1980/600 =
# 3.3 -> PASS rule) plus a gates block the trend-validity cap reads.
MOCK_ANALYSIS_TREND_OK = """\
import json, sys
recs = [json.loads(l) for l in sys.stdin if l.strip()]
k = sum(r["metrics"]["kernel_pack_bytes"] for r in recs)
g = sum(r["metrics"]["gloss_zstd_bytes"] for r in recs)
print(json.dumps({"ratio": g / k, "n_runs": len(recs),
                  "gates": {"separation_valid": True, "scale_trend": True}}))
"""
MOCK_ANALYSIS_TREND_FAIL = MOCK_ANALYSIS_TREND_OK.replace(
    '"separation_valid": True, "scale_trend": True',
    '"separation_valid": False, "scale_trend": False')


def load_json(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


class TestRealRecordRegression(unittest.TestCase):
    """The a5-llm / f2 regressions against the REAL frozen artifacts."""

    def setUp(self):
        self.index = load_json("registry/frozen-index.json")

    def test_a5llm_licenses_sign_only_not_slope(self):
        # REGRESSION: the exact frozen a5-llm inputs (design, measured rungs
        # incl. R0, real analysis output with failed trend gates) now yield
        # sign-only — matching the frozen envelope ("never a slope law") and
        # correction/2's binding reading.
        record = load_json("registry/experiments/a5-llm.json")
        verdict = load_json("registry/verdicts/a5-llm.json")
        analysis = load_json("reports/auto/a5-llm/analysis-output.json")
        self.assertEqual(verdict["rungs_measured"], ["R0", "R1", "R2", "R3"])
        self.assertEqual(verdict["scale_language_licensed"], "slope",
                         "the issued (defective) verdict object must stay byte-identical")
        got = vg.scale_language_license(record["design"], verdict["rungs_measured"], analysis)
        self.assertEqual(got, "sign-only")

    def test_a5llm_failed_trend_instrument_blocks_slope_regardless_of_ceiling(self):
        # Even if a5-llm HAD declared a slope ceiling and its model-scale
        # rungs, the failed trend instrument (separation_valid=false,
        # scale_trend_rag=false) alone forces sign-only (cap iii).
        record = load_json("registry/experiments/a5-llm.json")
        analysis = load_json("reports/auto/a5-llm/analysis-output.json")
        self.assertIs(analysis["gates"]["separation_valid"], False)
        self.assertIs(analysis["analysis"]["holm"]["scale_trend_rag"], False)
        design = dict(record["design"])
        design["scale_language_max"] = "slope"
        design["model_scale_rungs"] = ["R1", "R2", "R3"]
        design["scale_trend_valid_metrics"] = ["/gates/separation_valid",
                                               "/analysis/holm/scale_trend_rag"]
        got = vg.scale_language_license(design, ["R0", "R1", "R2", "R3"], analysis)
        self.assertEqual(got, "sign-only")

    def test_f2_licenses_sign_only_not_slope(self):
        # f2 hygiene regression (correction registry/corrections/f2/2-*):
        # genuine model-scale rungs, but no machine-readable ceiling and no
        # valid trend fit in the analysis output => sign-only.
        record = load_json("registry/experiments/f2.json")
        verdict = load_json("registry/verdicts/f2.json")
        analysis = load_json("reports/auto/f2/analysis-output.json")
        self.assertEqual(verdict["rungs_measured"], ["R1", "R2", "R3"])
        self.assertEqual(verdict["scale_language_licensed"], "slope")
        got = vg.scale_language_license(record["design"], verdict["rungs_measured"], analysis)
        self.assertEqual(got, "sign-only")

    def test_frozen_records_unchanged(self):
        # Corrections are separate files: the frozen record bytes must still
        # hash to their frozen-index entries.
        for exp in ("a5-llm", "f2"):
            record = load_json("registry/experiments/%s.json" % exp)
            self.assertEqual(kc.frozen_hash(record), self.index[exp],
                             "%s frozen record bytes drifted" % exp)
            self.assertEqual(record["frozen_sha256"], self.index[exp])

    def test_correction_records_well_formed(self):
        for rel, exp in (("registry/corrections/a5-llm/2-scale-license-erratum.json", "a5-llm"),
                         ("registry/corrections/f2/2-scale-license-erratum.json", "f2")):
            corr = load_json(rel)
            self.assertEqual(corr["experiment"], exp)
            self.assertEqual(corr["seq"], 2)
            self.assertEqual(corr["schema_version"], "kot-correction/1")
            self.assertEqual(corr["binding_reading"]["value_as_issued"], "slope")
            self.assertEqual(corr["binding_reading"]["binding_value"], "sign-only")
            self.assertIn("2026-07-11", corr["authorized_by"])
            self.assertIn("issue #5", corr["authorized_by"])
            self.assertEqual(corr["corrective_action"]["record_mutation"][:5], "NONE.")
            # RT-14: no account-identifying strings in correction bytes.
            kc.require_no_account_strings(kc.canonical_bytes(corr), rel)


class TestIssuedVerdictSweep(unittest.TestCase):
    """Re-audit point 3 close-out: the sweep over EVERY issued verdict.

    Under the comparable-rung minimum rule, every issued 0/1/2-rung license
    regenerates unchanged; only a5-llm and f2 move slope -> sign-only —
    exactly the two records the errata bind. And the issued verdict FILES for
    both are byte-identical to the shas their binding corrections cite (no
    frozen/issued byte was touched by this remediation)."""

    ERRATA_BOUND = {"a5-llm": "sign-only", "f2": "sign-only"}

    def verdict_paths(self):
        paths = sorted(glob.glob(os.path.join(REPO, "registry", "verdicts", "*.json")))
        self.assertGreaterEqual(len(paths), 17, "the issued-verdict sweep lost records")
        return paths

    def test_all_issued_licenses_reproduce_under_the_fixed_helper(self):
        for vp in self.verdict_paths():
            with open(vp, encoding="utf-8") as f:
                verdict = json.load(f)
            exp = verdict["experiment"]
            record = load_json("registry/experiments/%s.json" % exp)
            ap = os.path.join(REPO, "reports", "auto", exp, "analysis-output.json")
            analysis = None
            if os.path.exists(ap):
                with open(ap, encoding="utf-8") as f:
                    analysis = json.load(f)
            got = vg.scale_language_license(
                record["design"], verdict.get("rungs_measured", []), analysis)
            want = self.ERRATA_BOUND.get(exp, verdict["scale_language_licensed"])
            self.assertEqual(got, want,
                             "%s: fixed helper licenses %r, expected %r (issued %r)"
                             % (exp, got, want, verdict["scale_language_licensed"]))

    def test_issued_verdict_bytes_unchanged(self):
        # The frozen-bytes-unchanged assertion: the two errata-bound verdict
        # objects stand byte-identical as issued, pinned to the exact shas the
        # binding corrections cite (append-never-edit; regeneration is
        # coordinator-gated per adjudication decision #1b/#6).
        for exp, want, corr_rel in (
                ("a5-llm", A5LLM_VERDICT_SHA256,
                 "registry/corrections/a5-llm/2-scale-license-erratum.json"),
                ("f2", F2_VERDICT_SHA256,
                 "registry/corrections/f2/2-scale-license-erratum.json")):
            got = sha256_file(os.path.join(REPO, "registry", "verdicts", "%s.json" % exp))
            self.assertEqual(got, want, "%s issued verdict bytes drifted" % exp)
            with open(os.path.join(REPO, corr_rel), encoding="utf-8") as f:
                self.assertIn(want, f.read(),
                              "%s does not cite the pinned issued-verdict sha" % corr_rel)


class TestScaleLicenseUnit(unittest.TestCase):
    """Pure-function truth table for the three caps."""

    DESIGN_FULL = {
        "scale_language_max": "slope",
        "model_scale_rungs": ["R1", "R2", "R3", "R4"],
        "scale_trend_valid_metrics": ["/gates/separation_valid", "/gates/scale_trend"],
    }
    ANALYSIS_OK = {"gates": {"separation_valid": True, "scale_trend": True}}
    ANALYSIS_BAD = {"gates": {"separation_valid": False, "scale_trend": True}}

    def lic(self, design, rungs, analysis=None):
        return vg.scale_language_license(design, rungs, analysis)

    def test_g12_low_counts_unchanged(self):
        # Byte-identical legacy behaviour below 3 rungs (f2b-replicate et al.).
        self.assertEqual(self.lic({}, []), "none")
        self.assertEqual(self.lic({}, ["R1"]), "none")
        self.assertEqual(self.lic({}, ["R1", "R3"]), "sign-only")
        self.assertEqual(self.lic(self.DESIGN_FULL, ["R1", "R3"], self.ANALYSIS_OK), "sign-only")

    def test_preservation_three_comparable_rungs_license_slope(self):
        # PRESERVATION (G-12 / 08-stats 2.1): exactly 3 comparable rungs +
        # slope ceiling + valid trend => slope. NOT a blunt >=4 rule.
        d = dict(self.DESIGN_FULL, model_scale_rungs=["R1", "R2", "R3"])
        self.assertEqual(self.lic(d, ["R1", "R2", "R3"], self.ANALYSIS_OK), "slope")

    def test_baseline_rung_label_never_inflates_the_count(self):
        # The a5-llm R0 defect: 3 measured labels, only 2 comparable => no slope.
        d = dict(self.DESIGN_FULL, model_scale_rungs=["R1", "R2", "R3"])
        self.assertEqual(self.lic(d, ["R0", "R1", "R2"], self.ANALYSIS_OK), "sign-only")
        # 4 labels incl. R0, 3 comparable => slope still licensable when valid.
        self.assertEqual(self.lic(d, ["R0", "R1", "R2", "R3"], self.ANALYSIS_OK), "slope")

    def test_reaudit_point3_single_comparable_rung_licenses_none(self):
        # The 2026-07-11 re-audit's exact counterexample: measured
        # {BASE0,BASE1,R1}, model_scale_rungs=[R1], ceiling slope, valid trend
        # => "none" (G-12 over ONE comparable rung), NOT "sign-only" — non-
        # model labels no longer inflate the tier at ANY level.
        d = {"scale_language_max": "slope",
             "model_scale_rungs": ["R1"],
             "scale_trend_valid_metrics": ["/gates/separation_valid",
                                           "/gates/scale_trend"]}
        self.assertEqual(self.lic(d, ["BASE0", "BASE1", "R1"], self.ANALYSIS_OK), "none")

    def test_zero_comparable_rungs_license_none(self):
        # No measured rung is a declared model-scale rung => nothing licensed,
        # however many baseline labels were measured.
        d = dict(self.DESIGN_FULL, model_scale_rungs=["R9"])
        self.assertEqual(self.lic(d, ["BASE0", "BASE1", "BASE2"], self.ANALYSIS_OK), "none")
        # A DECLARED-EMPTY comparable list counts zero (conservative reading,
        # fail closed) — it is not the legacy raw-count fallback.
        d = dict(self.DESIGN_FULL, model_scale_rungs=[])
        self.assertEqual(self.lic(d, ["R1", "R2", "R3"], self.ANALYSIS_OK), "none")

    def test_two_comparable_rungs_cap_sign_only_regardless_of_extra_labels(self):
        d = dict(self.DESIGN_FULL, model_scale_rungs=["R1", "R2"])
        self.assertEqual(self.lic(d, ["BASE0", "BASE1", "R1", "R2"], self.ANALYSIS_OK),
                         "sign-only")

    def test_ceiling_caps_slope(self):
        # CEILING: sign-only ceiling refuses slope even with many rungs.
        d = dict(self.DESIGN_FULL, scale_language_max="sign-only")
        self.assertEqual(self.lic(d, ["R1", "R2", "R3", "R4"], self.ANALYSIS_OK), "sign-only")
        # A declared "none" ceiling caps even a 2-rung sign.
        d = dict(self.DESIGN_FULL, scale_language_max="none")
        self.assertEqual(self.lic(d, ["R1", "R3"], self.ANALYSIS_OK), "none")

    def test_absent_ceiling_fails_closed(self):
        d = {k: v for k, v in self.DESIGN_FULL.items() if k != "scale_language_max"}
        self.assertEqual(self.lic(d, ["R1", "R2", "R3", "R4"], self.ANALYSIS_OK), "sign-only")

    def test_unintelligible_declared_ceiling_fails_fully_closed(self):
        # A declared ceiling OUTSIDE the license vocabulary (schema +
        # prereg-freeze refuse it at freeze time) caps at "none" here too —
        # the most conservative reading of an unintelligible frozen field.
        d = dict(self.DESIGN_FULL, scale_language_max="trend")
        self.assertEqual(self.lic(d, ["R1", "R2", "R3"], self.ANALYSIS_OK), "none")

    def test_invalid_trend_result_fails_closed(self):
        self.assertEqual(self.lic(self.DESIGN_FULL, ["R1", "R2", "R3"], self.ANALYSIS_BAD),
                         "sign-only")
        # Declared pointer missing from the analysis output => fail closed.
        d = dict(self.DESIGN_FULL, scale_trend_valid_metrics=["/gates/nonexistent"])
        self.assertEqual(self.lic(d, ["R1", "R2", "R3"], self.ANALYSIS_OK), "sign-only")
        # No declared trend metrics => fail closed.
        d = {k: v for k, v in self.DESIGN_FULL.items() if k != "scale_trend_valid_metrics"}
        self.assertEqual(self.lic(d, ["R1", "R2", "R3"], self.ANALYSIS_OK), "sign-only")
        # No analysis at all (INCOMPLETE-DATA path) => fail closed.
        self.assertEqual(self.lic(self.DESIGN_FULL, ["R1", "R2", "R3"], None), "sign-only")

    def test_legacy_record_without_fields_never_slopes(self):
        # Pre-fix records (a5-llm/f2 as frozen) carry none of the three
        # fields: slope is unreachable, sign-only is the max.
        self.assertEqual(self.lic({}, ["R0", "R1", "R2", "R3"], self.ANALYSIS_OK), "sign-only")


class TestSchemaIntegration(unittest.TestCase):
    """Re-audit point 4: the three fields are OPTIONAL design properties in
    BOTH registry schemas; every frozen record without them still validates."""

    def schema(self, name):
        return load_json("registry/schema/%s" % name)

    def test_design_admits_the_three_optional_fields_in_both_schemas(self):
        for name in ("kot-reg-1.json", "kot-reg-2.json"):
            design = self.schema(name)["properties"]["design"]
            props = design["properties"]
            self.assertEqual(props["scale_language_max"]["enum"],
                             ["none", "sign-only", "slope"], name)
            self.assertEqual(props["model_scale_rungs"]["items"]["type"], "string", name)
            self.assertEqual(props["scale_trend_valid_metrics"]["items"]["pattern"], "^/", name)
            # OPTIONAL: none of the three is required — legacy records validate.
            for field in ("scale_language_max", "model_scale_rungs",
                          "scale_trend_valid_metrics"):
                self.assertNotIn(field, design["required"], "%s must stay optional" % name)

    def test_every_frozen_record_still_validates_without_the_fields(self):
        # The prereg-freeze --dry-run equivalent for already-FROZEN records
        # (which by design cannot re-enter the freeze path): the exact schema
        # validation prereg-freeze / the amendment overlay / registry-check
        # apply, over the full frozen index.
        index = load_json("registry/frozen-index.json")
        schemas = {sv: self.schema(fn) for sv, fn in SCHEMA_FILES.items()}
        swept = 0
        for exp in sorted(k for k in index if not k.startswith("_")):
            record = load_json("registry/experiments/%s.json" % exp)
            errs = kc.validate_schema(record, schemas[record["schema_version"]])
            self.assertEqual(errs, [], "%s no longer validates: %s" % (exp, errs[:5]))
            swept += 1
        self.assertGreaterEqual(swept, 17)

    def test_records_with_the_fields_validate_and_bad_shapes_are_refused(self):
        for exp in ("f2", "a5-llm"):  # one kot-reg/1, one kot-reg/2
            base = load_json("registry/experiments/%s.json" % exp)
            schema = self.schema(SCHEMA_FILES[base["schema_version"]])
            rec = json.loads(json.dumps(base))
            rec["design"]["scale_language_max"] = "sign-only"
            rec["design"]["model_scale_rungs"] = ["R1", "R2", "R3"]
            rec["design"]["scale_trend_valid_metrics"] = ["/gates/separation_valid"]
            self.assertEqual(kc.validate_schema(rec, schema), [], exp)
            # bad enum value refused
            rec["design"]["scale_language_max"] = "trend"
            self.assertNotEqual(kc.validate_schema(rec, schema), [], exp)
            rec["design"]["scale_language_max"] = "slope"
            # non-string rung label refused
            rec["design"]["model_scale_rungs"] = [1]
            self.assertNotEqual(kc.validate_schema(rec, schema), [], exp)
            rec["design"]["model_scale_rungs"] = ["R1"]
            # a trend metric that is not a JSON pointer refused
            rec["design"]["scale_trend_valid_metrics"] = ["gates/separation_valid"]
            self.assertNotEqual(kc.validate_schema(rec, schema), [], exp)


class ScaleFixture(SpineFixture):
    """SpineFixture + rung-ladder records frozen through the REAL prereg-freeze
    CLI (no hand-freeze bypass — re-audit point 4: the fixtures prove a
    LAWFULLY preregistered record reaches each licensing path)."""

    def rung_record(self, exp_id, rung_levels, design_extra=None, trend_ok=True,
                    envelope=None):
        script = "analysis/mock_trend_%s.py" % ("ok" if trend_ok else "fail")
        self.write(script, MOCK_ANALYSIS_TREND_OK if trend_ok else MOCK_ANALYSIS_TREND_FAIL)
        rec = self.base_record(exp_id=exp_id)
        rec["design"]["independent_vars"].append({"name": "rung", "levels": rung_levels})
        rec["design"]["scale_rungs"] = rung_levels
        rec["design"]["seeds"] = list(range(len(rung_levels)))
        rec["design"].update(design_extra or {})
        if envelope is not None:
            rec["extrapolation_envelope_verbatim"] = envelope
        rec["pins"]["analysis_script"] = {
            "path": script, "sha256": sha256_file(self.path(script)),
            "output_fields": ["/ratio", "/n_runs", "/gates/separation_valid",
                              "/gates/scale_trend"],
        }
        return rec

    def freeze_ok(self, rec):
        p = self.freeze(rec)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def append_rung_run(self, exp_id, seed, rung):
        body = {
            "event": "run", "phase": "final",
            "prereg_hash": self.frozen_sha(exp_id),
            "config": {"arm": "kotk2-vs-gloss", "seed": seed, "rung": rung},
            "metrics": {"kernel_pack_bytes": 300, "gloss_zstd_bytes": 990, "n_records": 10},
            "exit": "ok",
        }
        p = run_cli(LOG_APPEND, "--experiment", exp_id, "--agent-id", "runner-1",
                    "--record", "-", "--root", self.root,
                    "--ts", "2026-07-08T00:00:0%dZ" % seed, stdin=json.dumps(body))
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def generate(self, exp_id):
        p = run_cli(VERDICT_GEN, "--experiment", exp_id, "--agent-id", "coordinator-1",
                    "--root", self.root, "--computed-at", "2026-07-08T01:00:00Z")
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(self.path("registry/verdicts/%s.json" % exp_id), encoding="utf-8") as f:
            return json.load(f)


class TestVerdictGenEndToEnd(ScaleFixture):
    """The fixed generator through the real CLI on prereg-frozen fixtures."""

    def test_regression_a5llm_configuration_yields_sign_only(self):
        # REGRESSION (e2e): the a5-llm shape — 4 rung labels incl. the R0
        # baseline, machine-readable ceiling sign-only per the envelope
        # ("never a slope law"), trend gates FAILED — licenses sign-only.
        rec = self.rung_record(
            "mock-a5llm", ["R0", "R1", "R2", "R3"], trend_ok=False,
            envelope="4 measured rung labels incl. the R0 baseline cells; a "
                     "SIGN at R1-R3 only, never a slope law",
            design_extra={
                "scale_language_max": "sign-only",
                "model_scale_rungs": ["R1", "R2", "R3"],
                "scale_trend_valid_metrics": ["/gates/separation_valid",
                                              "/gates/scale_trend"]})
        self.freeze_ok(rec)
        for seed, rung in enumerate(["R0", "R1", "R2", "R3"]):
            self.append_rung_run("mock-a5llm", seed, rung)
        v = self.generate("mock-a5llm")
        self.assertEqual(v["rungs_measured"], ["R0", "R1", "R2", "R3"])
        self.assertEqual(v["scale_language_licensed"], "sign-only")

    def test_regression_legacy_record_shape_yields_sign_only(self):
        # The as-frozen a5-llm/f2 shape: NO machine-readable fields at all;
        # 4 rung labels must no longer emit slope (fail closed).
        rec = self.rung_record("mock-legacy", ["R0", "R1", "R2", "R3"], trend_ok=True)
        self.freeze_ok(rec)
        for seed, rung in enumerate(["R0", "R1", "R2", "R3"]):
            self.append_rung_run("mock-legacy", seed, rung)
        v = self.generate("mock-legacy")
        self.assertEqual(v["scale_language_licensed"], "sign-only")

    def test_reaudit_point3_one_comparable_rung_yields_none_e2e(self):
        # The re-audit's exact counterexample, end-to-end through a LAWFULLY
        # frozen record: measured {BASE0,BASE1,R1}, model_scale_rungs=[R1],
        # ceiling slope, VALID trend => "none". Non-model labels can no longer
        # inflate none -> sign-only.
        rec = self.rung_record(
            "mock-onecomp", ["BASE0", "BASE1", "R1"], trend_ok=True,
            envelope="one comparable model-scale rung measured; the design "
                     "licenses a slope law only at >=3 comparable rungs",
            design_extra={
                "scale_language_max": "slope",
                "model_scale_rungs": ["R1"],
                "scale_trend_valid_metrics": ["/gates/separation_valid",
                                              "/gates/scale_trend"]})
        self.freeze_ok(rec)
        for seed, rung in enumerate(["BASE0", "BASE1", "R1"]):
            self.append_rung_run("mock-onecomp", seed, rung)
        v = self.generate("mock-onecomp")
        self.assertEqual(v["rungs_measured"], ["BASE0", "BASE1", "R1"])
        self.assertEqual(v["scale_language_licensed"], "none")

    def test_preservation_g12_slope_still_reachable(self):
        # PRESERVATION (e2e): 3 comparable model-scale rungs + slope ceiling +
        # valid trend result STILL license slope — not the blunt >=4 rule
        # (which would contradict G-12 / 08-stats 2.1) — and the record
        # carrying the machine-readable fields froze through the REAL
        # prereg-freeze path (re-audit point 4).
        rec = self.rung_record(
            "mock-slope", ["R1", "R2", "R3"], trend_ok=True,
            envelope="3 comparable model-scale rungs (R1,R2,R3); a fitted "
                     "slope law is licensed within R1-R3",
            design_extra={
                "scale_language_max": "slope",
                "model_scale_rungs": ["R1", "R2", "R3"],
                "scale_trend_valid_metrics": ["/gates/separation_valid",
                                              "/gates/scale_trend"]})
        self.freeze_ok(rec)
        for seed, rung in enumerate(["R1", "R2", "R3"]):
            self.append_rung_run("mock-slope", seed, rung)
        v = self.generate("mock-slope")
        self.assertEqual(v["rungs_measured"], ["R1", "R2", "R3"])
        self.assertEqual(v["scale_language_licensed"], "slope")

    def test_ceiling_sign_only_blocks_slope_despite_many_rungs(self):
        # CEILING (e2e): 4 genuine comparable rungs + valid trend, but the
        # frozen per-record ceiling caps at sign — never slope.
        rec = self.rung_record(
            "mock-ceiling", ["R1", "R2", "R3", "R4"], trend_ok=True,
            envelope="R1-R4 measured; a SIGN only, never a slope law",
            design_extra={
                "scale_language_max": "sign-only",
                "model_scale_rungs": ["R1", "R2", "R3", "R4"],
                "scale_trend_valid_metrics": ["/gates/separation_valid",
                                              "/gates/scale_trend"]})
        self.freeze_ok(rec)
        for seed, rung in enumerate(["R1", "R2", "R3", "R4"]):
            self.append_rung_run("mock-ceiling", seed, rung)
        v = self.generate("mock-ceiling")
        self.assertEqual(v["rungs_measured"], ["R1", "R2", "R3", "R4"])
        self.assertEqual(v["scale_language_licensed"], "sign-only")

    def test_two_rung_sign_only_preserved(self):
        # f2b-replicate-shape behaviour byte-identical: 2 rungs => sign-only.
        rec = self.rung_record("mock-2rung", ["R1", "R3"], trend_ok=True)
        self.freeze_ok(rec)
        for seed, rung in enumerate(["R1", "R3"]):
            self.append_rung_run("mock-2rung", seed, rung)
        v = self.generate("mock-2rung")
        self.assertEqual(v["scale_language_licensed"], "sign-only")


class TestFreezeScaleLanguage(ScaleFixture):
    """Re-audit point 4 (second half): prereg-freeze validates a declared
    machine-readable ceiling against the envelope text, fail-closed
    (ERR_P2_SCALE_LANGUAGE; adjudication section 2.2 item 1)."""

    SLOPE_EXTRA = {
        "scale_language_max": "slope",
        "model_scale_rungs": ["R1", "R2", "R3"],
        "scale_trend_valid_metrics": ["/gates/separation_valid", "/gates/scale_trend"],
    }

    def test_slope_ceiling_against_prohibiting_envelope_refused(self):
        rec = self.rung_record(
            "mock-badceil", ["R1", "R2", "R3"],
            envelope="3 rungs => SIGN plus direction language, never a slope law",
            design_extra=dict(self.SLOPE_EXTRA))
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)

    def test_slope_ceiling_with_envelope_silent_on_slope_refused(self):
        # Fail closed: an envelope that never mentions slope language cannot
        # be verified to license a slope ceiling.
        rec = self.rung_record(
            "mock-silent", ["R1", "R2", "R3"],
            envelope="three rungs measured; trend language within R1-R3",
            design_extra=dict(self.SLOPE_EXTRA))
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)

    def test_slope_ceiling_without_companion_machinery_refused(self):
        rec = self.rung_record(
            "mock-nomach", ["R1", "R2", "R3"],
            envelope="a fitted slope law is licensed within R1-R3",
            design_extra={"scale_language_max": "slope"})
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)

    def test_model_scale_rung_outside_ladder_refused(self):
        rec = self.rung_record(
            "mock-stray", ["R1", "R2", "R3"],
            envelope="a fitted slope law is licensed within R1-R3",
            design_extra=dict(self.SLOPE_EXTRA, model_scale_rungs=["R1", "R2", "R9"]))
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)

    def test_trend_metric_outside_declared_outputs_refused(self):
        rec = self.rung_record(
            "mock-badptr", ["R1", "R2", "R3"],
            envelope="a fitted slope law is licensed within R1-R3",
            design_extra=dict(self.SLOPE_EXTRA,
                              scale_trend_valid_metrics=["/gates/undeclared"]))
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)

    def test_consistent_declarations_freeze_and_legacy_records_unaffected(self):
        # sign-only ceiling under a slope-prohibiting envelope is CONSISTENT
        # (does not exceed) — freezes.
        rec = self.rung_record(
            "mock-okceil", ["R0", "R1", "R2"],
            envelope="SIGN at R1-R2 only, never a slope law",
            design_extra={"scale_language_max": "sign-only",
                          "model_scale_rungs": ["R1", "R2"]})
        self.freeze_ok(rec)
        # and a legacy record with none of the fields freezes exactly as before
        rec = self.rung_record("mock-legacyok", ["R1", "R2", "R3"])
        self.freeze_ok(rec)

    def test_dry_run_checks_scale_language_too(self):
        rec = self.rung_record(
            "mock-dry", ["R1", "R2", "R3"],
            envelope="never a slope law",
            design_extra=dict(self.SLOPE_EXTRA))
        self.write("registry/experiments/%s.json" % rec["id"], json.dumps(rec) + "\n")
        from test_fixtures import PREREG_FREEZE
        p = run_cli(PREREG_FREEZE, "--experiment", rec["id"], "--agent-id", "coordinator-1",
                    "--root", self.root, "--frozen-at", "2026-07-08T00:00:00Z", "--dry-run")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)


class TestFreezeScaleLanguageFailClosed(ScaleFixture):
    """Re-audit-2 (poc/gpt56-review/a5llm-reaudit2-20260711) residuals 1-3:
    the freeze-time ceiling/envelope validation must be genuinely FAIL-CLOSED.
    These are the re-audit's EXACT counterexamples, adversarial by design:
    prohibition phrasings the old regexes missed, unrelated declared Booleans
    standing in for the registered trend machinery, and the unreachable named
    enum error."""

    SLOPE_LICENSED_ENVELOPE = "a fitted slope law is licensed within R1-R3"
    SLOPE_EXTRA = {
        "scale_language_max": "slope",
        "model_scale_rungs": ["R1", "R2", "R3"],
        "scale_trend_valid_metrics": ["/gates/separation_valid", "/gates/scale_trend"],
    }

    def refuse(self, rec):
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)
        return p

    # -- residual 1: prohibition wording the old regexes did not recognize --

    def test_no_fitted_slope_may_be_reported_refuses_slope_ceiling(self):
        # The re-audit-2 counterexample verbatim: the old regexes saw the word
        # "slope" and ACCEPTED; the prohibition must now refuse the freeze.
        rec = self.rung_record(
            "mock-noslope", ["R1", "R2", "R3"],
            envelope="No fitted slope may be reported.",
            design_extra=dict(self.SLOPE_EXTRA))
        self.refuse(rec)

    def test_no_sign_may_be_reported_refuses_sign_only_ceiling(self):
        # The sign analogue verbatim: a sign-only ceiling against an explicit
        # sign prohibition was ACCEPTED before; it must refuse.
        rec = self.rung_record(
            "mock-nosign", ["R1", "R2", "R3"],
            envelope="No sign may be reported.",
            design_extra={"scale_language_max": "sign-only",
                          "model_scale_rungs": ["R1", "R2", "R3"]})
        self.refuse(rec)

    def test_more_prohibition_phrasings_refuse(self):
        # A broad family, not a phrasebook: each variant must refuse.
        for i, envelope in enumerate((
                "a slope is not licensed at these rungs",
                "reporting a fitted slope is prohibited",
                "the design may not report a slope",
                "slope language is forbidden outside R1-R3")):
            rec = self.rung_record(
                "mock-prohib%d" % i, ["R1", "R2", "R3"],
                envelope=envelope, design_extra=dict(self.SLOPE_EXTRA))
            self.refuse(rec)

    def test_ambiguous_licensing_refuses_fail_closed(self):
        # The key discipline: no AFFIRMATIVE license of the declared level =>
        # refuse. A slope mention without a licensing phrase is ambiguous.
        rec = self.rung_record(
            "mock-ambig", ["R1", "R2", "R3"],
            envelope="the slope question is discussed at R1-R3",
            design_extra=dict(self.SLOPE_EXTRA))
        self.refuse(rec)
        # sign-only against an envelope silent on sign/direction language.
        rec = self.rung_record(
            "mock-signsilent", ["R1", "R2", "R3"],
            envelope="results hold within R1-R3 on the pinned corpus",
            design_extra={"scale_language_max": "sign-only",
                          "model_scale_rungs": ["R1", "R2", "R3"]})
        self.refuse(rec)

    def test_affirmative_license_positive_controls_freeze(self):
        # Positive control: an affirmatively licensing envelope + the matching
        # ceiling ACCEPTS (the fail-closed rule must not refuse everything).
        rec = self.rung_record(
            "mock-slopeok", ["R1", "R2", "R3"],
            envelope=self.SLOPE_LICENSED_ENVELOPE,
            design_extra=dict(self.SLOPE_EXTRA))
        self.freeze_ok(rec)
        rec = self.rung_record(
            "mock-signok", ["R1", "R2", "R3"],
            envelope="a SIGN within R1-R3 is licensed, never a slope law",
            design_extra={"scale_language_max": "sign-only",
                          "model_scale_rungs": ["R1", "R2", "R3"]})
        self.freeze_ok(rec)

    # -- residual 2: the registered trend machinery must be genuinely gated --

    def test_unrelated_declared_boolean_cannot_stand_in_for_trend_result(self):
        # The re-audit-2 counterexample: /analysis/primary_reject IS a
        # declared output field, but it is not the registered scale-trend-
        # validity result — a slope ceiling gated on it must refuse.
        rec = self.rung_record(
            "mock-boolptr", ["R1", "R2", "R3"],
            envelope=self.SLOPE_LICENSED_ENVELOPE,
            design_extra=dict(self.SLOPE_EXTRA,
                              scale_trend_valid_metrics=["/analysis/primary_reject"]))
        rec["pins"]["analysis_script"]["output_fields"].append("/analysis/primary_reject")
        self.refuse(rec)

    def test_separation_gate_alone_cannot_stand_in_for_trend_result(self):
        # Only a separation gate, omitting the registered trend result: refuse.
        rec = self.rung_record(
            "mock-seponly", ["R1", "R2", "R3"],
            envelope=self.SLOPE_LICENSED_ENVELOPE,
            design_extra=dict(self.SLOPE_EXTRA,
                              scale_trend_valid_metrics=["/gates/separation_valid"]))
        self.refuse(rec)

    def test_registered_trend_pointer_present_accepts(self):
        # Positive control: the registered pointer present (even alongside an
        # extra declared Boolean — MORE restrictive at verdict time) freezes.
        rec = self.rung_record(
            "mock-trendok", ["R1", "R2", "R3"],
            envelope=self.SLOPE_LICENSED_ENVELOPE,
            design_extra=dict(self.SLOPE_EXTRA,
                              scale_trend_valid_metrics=["/analysis/primary_reject",
                                                         "/gates/separation_valid",
                                                         "/gates/scale_trend"]))
        rec["pins"]["analysis_script"]["output_fields"].append("/analysis/primary_reject")
        self.freeze_ok(rec)

    def test_no_registered_trend_result_declared_refuses_slope(self):
        # An analysis script that declares NO scale-trend-validity result at
        # all can never carry a slope ceiling (the machinery cannot be shown
        # to run).
        rec = self.rung_record(
            "mock-notrend", ["R1", "R2", "R3"],
            envelope=self.SLOPE_LICENSED_ENVELOPE,
            design_extra=dict(self.SLOPE_EXTRA,
                              scale_trend_valid_metrics=["/gates/separation_valid"]))
        rec["pins"]["analysis_script"]["output_fields"] = [
            "/ratio", "/n_runs", "/gates/separation_valid"]
        self.refuse(rec)

    # -- residual 3: ERR_P2_SCALE_LANGUAGE reachable through the normal CLI --

    def test_invalid_enum_fails_as_the_named_error_not_schema(self):
        # The enum/consistency check runs BEFORE generic schema validation:
        # an invalid scale_language_max must fail as ERR_P2_SCALE_LANGUAGE,
        # never as ERR_P2_SCHEMA, through the normal freeze CLI.
        rec = self.rung_record(
            "mock-badenum", ["R1", "R2", "R3"],
            design_extra={"scale_language_max": "trend"})
        p = self.freeze(rec)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ERR_P2_SCALE_LANGUAGE", p.stderr)
        self.assertNotIn("ERR_P2_SCHEMA", p.stderr)


class TestSiblingGenerators(unittest.TestCase):
    """Re-audit point 6: the specialized truthstyle-2x2 driver and report-gen
    no longer carry the raw-rung-count logic/statement."""

    def test_dts_driver_delegates_to_the_fixed_spine_helper(self):
        # verdict-gen-dts previously duplicated the raw-label-count expression
        # (~line 272) and could emit "slope" from raw rung count. It must now
        # call the IMPORTED spine helper — same code, not a copy — and that
        # helper must be the fixed one (the re-audit point-3 case licenses
        # "none" through the dts module's own vg binding).
        spec = importlib.util.spec_from_file_location(
            "verdict_gen_dts", os.path.join(HERE, "verdict-gen-dts.py"))
        dts = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dts)
        with open(os.path.join(HERE, "verdict-gen-dts.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("vg.scale_language_license", src)
        self.assertNotIn('len(rungs) == 2 else "slope"', src,
                         "the duplicated raw-count license expression must be gone")
        d = {"scale_language_max": "slope", "model_scale_rungs": ["R1"],
             "scale_trend_valid_metrics": ["/gates/separation_valid"]}
        got = dts.vg.scale_language_license(
            d, ["BASE0", "BASE1", "R1"], {"gates": {"separation_valid": True}})
        self.assertEqual(got, "none")

    def test_report_gen_no_longer_states_the_raw_count_rule(self):
        with open(os.path.join(HERE, "report-gen.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"(>=3 rungs for slope adjectives', src,
                         "the stale raw-count statement must not be renderable")
        self.assertIn("MINIMUM of", src)
        self.assertIn("design.scale_language_max", src)
        self.assertIn("design.model_scale_rungs", src)
        self.assertIn("design.scale_trend_valid_metrics", src)


class TestRealCliA5llmRegeneration(unittest.TestCase):
    """Re-audit point 5: regenerate a5-llm through the REAL verdict-gen CLI.

    A copy of the real frozen artifacts (frozen record, frozen index, chained
    results log, the sha-pinned analysis script) is placed in a throwaway
    root and verdict-gen runs against it with the ISSUED computed_at. The
    regenerated verdict object must differ from the issued one in EXACTLY the
    scale_language_licensed field (slope -> sign-only): every measured
    number, gate, log/analysis hash, and the PASS-PENDING-AUDIT verdict rule
    reproduce byte-identically, and the real repo's issued artifacts are
    untouched. Skips loudly (never silently passes) when no writable temp dir
    exists (set KOT_TEST_TMPDIR) or the live analysis script has drifted from
    the frozen pin (PROPOSED-ASM-C discipline: verify pins, not the working
    tree)."""

    COPIES = ("registry/experiments/a5-llm.json", "registry/frozen-index.json",
              "results-log/a5-llm.jsonl")

    def test_regenerated_a5llm_differs_only_in_the_license_field(self):
        root = make_temp_root(prefix="kot-a5llm-regen-")
        if root is None:
            self.skipTest("no writable temp dir for the CLI regeneration "
                          "(set KOT_TEST_TMPDIR to a writable path)")
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)

        record = load_json("registry/experiments/a5-llm.json")
        pin = record["pins"]["analysis_script"]
        live = os.path.join(REPO, pin["path"])
        if not os.path.isfile(live) or sha256_file(live) != pin["sha256"]:
            self.skipTest("live %s drifted from the frozen pin %s — the real-CLI "
                          "regeneration needs the pinned bytes" % (pin["path"], pin["sha256"][:12]))

        for rel in self.COPIES + (pin["path"],):
            dst = os.path.join(root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(REPO, rel), dst)

        issued = load_json("registry/verdicts/a5-llm.json")
        self.assertEqual(issued["scale_language_licensed"], "slope",
                         "the issued (defective) object is the regression baseline")
        p = run_cli(VERDICT_GEN, "--experiment", "a5-llm", "--agent-id", "coordinator-1",
                    "--root", root, "--computed-at", issued["computed_at"])
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(os.path.join(root, "registry", "verdicts", "a5-llm.json"),
                  encoding="utf-8") as f:
            regen = json.load(f)

        self.assertEqual(regen["scale_language_licensed"], "sign-only")
        expected = json.loads(json.dumps(issued))
        expected["scale_language_licensed"] = "sign-only"
        self.assertEqual(regen, expected,
                         "regeneration must change EXACTLY the license field")
        # the real repo's issued verdict and log are untouched (fresh hashes)
        self.assertEqual(sha256_file(os.path.join(REPO, "registry", "verdicts", "a5-llm.json")),
                         A5LLM_VERDICT_SHA256)
        self.assertEqual(regen["inputs"]["log_tail_sha256"], issued["inputs"]["log_tail_sha256"])
        self.assertEqual(regen["inputs"]["analysis_output_sha256"],
                         issued["inputs"]["analysis_output_sha256"])


if __name__ == "__main__":
    unittest.main()
