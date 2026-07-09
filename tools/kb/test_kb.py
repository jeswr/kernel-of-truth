"""Fixtures for the Pillar-C KB tooling (style of tools/registry/test_fixtures.py).

Pins the fail-closed paths of kb-check record validation, the evidence-upgrade
rule (N-C §0/§2.2), canonical-bytes discipline, the rubric prescore parser, and
the kb filter dotted-path semantics.

Run: python3 -m unittest discover -s tools/kb -p 'test_kb.py'
"""

import importlib.util
import json
import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "ingest"))

import kb_common as K  # noqa: E402


def _load_script(name, path):
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    mod.__dict__["__file__"] = path
    exec(compile(code, path, "exec"), mod.__dict__)
    return mod


KB_CHECK = _load_script("kb_check_mod", os.path.join(_HERE, "kb-check"))


def good_record():
    rec = {
        "schema_version": "kot-lit/1",
        "id": "arxiv:2410.10450",
        "identity": {"doi": None, "arxiv": "2410.10450", "openalex": "W123", "s2": None, "pdf_sha256": None},
        "biblio": {"title": "Example", "authors": ["A. Author"], "year": 2024, "venue": "ICLR"},
        "architecture": {
            "summary": "A trained projector injects KB vectors into attention.",
            "seam_cell": "trained-bridge",
            "trained_components": ["projector"],
            "frozen_components": ["host LLM"],
            "mechanism_tags": ["kv-injection"],
        },
        "claims": [
            {
                "claim_id": "c1",
                "type": "quantitative",
                "statement": "accuracy 0.62 vs 0.85 text baseline on NQ-open",
                "metric": "accuracy",
                "value": 0.62,
                "unit": "fraction",
                "baseline": {"name": "text-in-context", "value": 0.85},
                "dataset": "NQ-open",
                "scale": {"params": 7e9, "rungs_measured": 1},
                "compute_reported": False,
                "evidence": "claimed",
                "evidence_ref": None,
            }
        ],
        "relation_to_kernel": {"hypotheses": [], "ledger_refs": [], "seams": [], "note": None},
        "reproduction": {"code_url": None, "weights_url": None},
        "provenance": {
            "extractor_model": "claude-haiku-4-5",
            "prompt_sha256": "0" * 64,
            "extracted_at": "2026-07-09",
            "source_scope": "abstract-only",
            "audit": {"state": "UNAUDITED", "by": None},
        },
    }
    rec["record_sha256"] = K.record_hash(rec)
    return rec


class TestRecordCheck(unittest.TestCase):
    def setUp(self):
        self.schema = K.load_schema("kot-lit-1.json")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, rec, name="arxiv_2410.10450.json", raw=None):
        path = os.path.join(self.tmp.name, name)
        with open(path, "wb") as f:
            f.write(raw if raw is not None else K.canonical_bytes(rec) + b"\n")
        return path

    def _errors(self, path):
        errors = []
        KB_CHECK.check_record_file(path, self.schema, errors)
        return errors

    def test_good_record_passes(self):
        self.assertEqual(self._errors(self._write(good_record())), [])

    def test_non_canonical_bytes_fail(self):
        rec = good_record()
        raw = json.dumps(rec, indent=2).encode() + b"\n"
        errs = self._errors(self._write(rec, raw=raw))
        self.assertTrue(any("ERR_KB_CANONICAL" in e for e in errs))

    def test_bad_hash_fails(self):
        rec = good_record()
        rec["record_sha256"] = "f" * 64
        errs = self._errors(self._write(rec))
        self.assertTrue(any("ERR_KB_HASH" in e for e in errs))

    def test_evidence_upgrade_needs_lit_report_anchor(self):
        rec = good_record()
        rec["claims"][0]["evidence"] = "established"  # no evidence_ref
        rec["record_sha256"] = K.record_hash(rec)
        errs = self._errors(self._write(rec))
        self.assertTrue(any("ERR_KB_EVIDENCE_UPGRADE" in e for e in errs))
        rec["claims"][0]["evidence_ref"] = "reports/lit-llm-injection-priorart.md#s3"
        rec["record_sha256"] = K.record_hash(rec)
        self.assertEqual(self._errors(self._write(rec)), [])

    def test_quantitative_claim_needs_anchors(self):
        rec = good_record()
        rec["claims"][0]["dataset"] = None
        rec["record_sha256"] = K.record_hash(rec)
        errs = self._errors(self._write(rec))
        self.assertTrue(any("ERR_KB_CLAIM_FIELDS" in e for e in errs))

    def test_seam_cell_enum_closed(self):
        rec = good_record()
        rec["architecture"]["seam_cell"] = "vibes"
        rec["record_sha256"] = K.record_hash(rec)
        errs = self._errors(self._write(rec))
        self.assertTrue(any("ERR_KB_SCHEMA" in e for e in errs))

    def test_audit_by_must_be_pseudonym(self):
        rec = good_record()
        rec["provenance"]["audit"] = {"state": "SPOT-CONFIRMED", "by": "someuser123"}
        rec["record_sha256"] = K.record_hash(rec)
        errs = self._errors(self._write(rec))
        self.assertTrue(any("ERR_P2_ACCOUNT_IN_RECORD" in e for e in errs))

    def test_id_filename_agreement(self):
        errs = self._errors(self._write(good_record(), name="arxiv_9999.00001.json"))
        self.assertTrue(any("ERR_KB_ID_PATH" in e for e in errs))


class TestCanonicalIds(unittest.TestCase):
    def test_arxiv_beats_doi(self):
        self.assertEqual(K.canonical_paper_id(arxiv="2410.10450v2", doi="10.1/x"), "arxiv:2410.10450")

    def test_datacite_arxiv_doi_folds(self):
        self.assertEqual(K.canonical_paper_id(doi="10.48550/arXiv.2410.10450"), "arxiv:2410.10450")

    def test_plain_doi(self):
        self.assertEqual(K.canonical_paper_id(doi="https://doi.org/10.18653/V1/D19-1250"), "doi:10.18653/v1/d19-1250")


class TestPrescore(unittest.TestCase):
    def test_rubric_parses_and_scores(self):
        import prescore as PS

        terms = PS.load_terms()
        self.assertGreater(len(terms), 30)
        self.assertTrue(any(w < 0 for _, w in terms), "anti terms must load")
        s, matched = PS.prescore("KV cache injection into frozen LLM", "", terms)
        self.assertGreater(s, 0)
        s0, _ = PS.prescore("Wireless recommender for autonomous driving", "", terms)
        self.assertEqual(s0, 0)


class TestLitBackedGate(unittest.TestCase):
    """The LIT-BACKED backing gate (assumption-register.md §6 item 3, ENABLED
    2026-07-09 on Pillar-C landing): a claim tagged LIT-BACKED — a register
    entry or a PREMISE/DECISION/LOAD-BEARING marker line — must resolve to a
    committed kot-lit/1 record (a kot-lit/kb-records citation whose record
    file exists) or carry a paper id/year. A citation that CLAIMS KB backing
    but does not resolve fails closed (recall infrastructure != evidence, and
    a KB citation that points at nothing is worse than no citation)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "registry"))
        os.makedirs(os.path.join(self.root, "docs"))
        os.makedirs(os.path.join(self.root, "kb", "records"))

    def tearDown(self):
        self.tmp.cleanup()

    def _register(self, backing_ref, tag="LIT-BACKED"):
        entry = {"id": "ASM-0042", "claim": "published result X", "tag": tag,
                 "backing_ref": backing_ref, "load_bearing": True,
                 "status": "open", "owner": "writer-1"}
        with open(os.path.join(self.root, "registry", "assumptions.jsonl"), "w") as f:
            f.write(json.dumps(entry) + "\n")

    def _doc(self, text):
        with open(os.path.join(self.root, "docs", "design.md"), "w") as f:
            f.write(text)

    def _record_stub(self, rec_id="arxiv:2410.10450"):
        path = os.path.join(self.root, "kb", "records",
                            rec_id.replace(":", "_").replace("/", "_") + ".json")
        with open(path, "w") as f:
            f.write("{}\n")

    def _errors(self):
        errors = []
        KB_CHECK.check_lit_backed(self.root, errors)
        return errors

    def test_resolving_kot_lit_citation_passes(self):
        self._record_stub()
        self._register("kot-lit:arxiv:2410.10450")
        self.assertEqual(self._errors(), [])

    def test_unresolved_kot_lit_citation_fails(self):
        self._register("kot-lit:arxiv:9999.00001")
        errs = self._errors()
        self.assertTrue(any("ERR_KB_LIT_UNRESOLVED" in e for e in errs), errs)

    def test_unresolved_kb_records_path_fails(self):
        self._register("kb/records/arxiv_9999.00001.json")
        errs = self._errors()
        self.assertTrue(any("ERR_KB_LIT_UNRESOLVED" in e for e in errs), errs)

    def test_paper_id_year_passes_without_kb_record(self):
        self._register("arXiv:2412.09764 (2024), [claimed - unreplicated]")
        self.assertEqual(self._errors(), [])
        self._register("W3C SHACL REC 2017")
        self.assertEqual(self._errors(), [])

    def test_no_backing_shape_fails(self):
        self._register("trust me, everyone knows this")
        errs = self._errors()
        self.assertTrue(any("ERR_KB_LIT_BACKING" in e for e in errs), errs)

    def test_marker_line_citation_resolves_or_fails(self):
        self._register("arXiv:2412.09764 (2024)")  # keep the register clean
        self._doc("PREMISE: injected arms lose to text baselines at 7B\n"
                  "  [LIT-BACKED: kot-lit:arxiv:2410.10450]\n")
        errs = self._errors()
        self.assertTrue(any("ERR_KB_LIT_UNRESOLVED" in e for e in errs), errs)
        self._record_stub()
        self.assertEqual(self._errors(), [])

    def test_off_marker_prose_tag_not_enforced(self):
        # Same surface as claims-check: the convention binds premise/decision
        # marker lines; an off-marker recall annotation is not a premise.
        self._doc("Background: see [LIT-BACKED: kot-lit:arxiv:9999.00001] for context.\n")
        self.assertEqual(self._errors(), [])

    def test_non_lit_backed_entries_ignored(self):
        self._register("registry/verdicts/m0b.json sha256 da475e98", tag="MEASURED")
        self.assertEqual(self._errors(), [])


class TestFilterSemantics(unittest.TestCase):
    def test_dotted_path_any_element(self):
        kb_cli = _load_script("kb_cli_mod", os.path.join(_HERE, "kb"))
        rec = good_record()
        self.assertTrue(kb_cli._match_pred(rec, "claim.metric", "=", "accuracy"))
        self.assertTrue(kb_cli._match_pred(rec, "claims.scale.params", ">=", "1e9"))
        self.assertFalse(kb_cli._match_pred(rec, "claims.scale.params", ">=", "1e10"))
        self.assertTrue(kb_cli._match_pred(rec, "architecture.seam_cell", "=", "trained-bridge"))


if __name__ == "__main__":
    unittest.main()
