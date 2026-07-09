"""Unit tests for the kot-query/1 `define`-op (DEFINE + DEFINE-MATCH), its
stratum-3 `definitional` endorsement kind, and the pinned relation-shorthand
alias table (docs/design-kot-query-define-op.md — the FROZEN memo).

Style: tools/kb/test_kb.py / tools/registry/test_fixtures.py (stdlib unittest,
fail-closed paths pinned). Engine built directly from small in-memory fixtures
(no onto-obo read; the live 45MB shard + a production endorsement record are the
Opus/census step, not exercised here).

Run: python3 -m unittest discover -s tools/axiom -p 'test_kot_axiom.py'
"""

import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import kot_axiom  # noqa: E402


def kurn(tag):
    """A valid urn:kot: concept URN (^urn:kot:[a-z2-7]{10,}$) from a short tag."""
    body = (tag + "aaaaaaaaaaaaaaaa")[:16]
    urn = "urn:kot:" + body
    assert kot_axiom.CONCEPT_URN_RE.match(urn), urn
    return urn


# --- minted urn:kot: URNs (the resolved side of the mint bridge) ---
X = kurn("termx")        # the definiendum, has a resolvable definition
G = kurn("genusg")       # its genus
F = kurn("fillerf")      # its differentia filler
F2 = kurn("filler2")     # a different filler (for the DEFINE-MATCH false case)
R = kurn("relregulat")   # the resolved `regulates` relation URN
NODEF = kurn("nodefn")   # admitted, but no logicalDefinition
UNRES = kurn("unresolv")  # admitted, definition has an unresolvable filler
BADREL = kurn("badreln")  # admitted, definition has an unknown differentia shorthand
MARKER = kurn("corpusmk")  # the endorsement's corpus-marker subject
OTHER = kurn("otherxx")  # a valid urn:kot: URN outside the admitted set

# `regulates` resolves shorthand -> RO_0002211 (pinned) -> R (mint bridge).
REGULATES_IRI = kot_axiom.PINNED_RELATION_ALIASES["regulates"]

MINT_BRIDGE = {
    "urn:onto-obo:GO_TERMX": X,
    "urn:onto-obo:GO_GENUS": G,
    "urn:onto-obo:GO_FILLER": F,
    "urn:onto-obo:GO_FILLER2": F2,
    REGULATES_IRI: R,
    "urn:onto-obo:GO_NODEF": NODEF,
    "urn:onto-obo:GO_UNRES": UNRES,
    "urn:onto-obo:GO_BADREL": BADREL,
    # NOTE: urn:onto-obo:GO_MISSINGFILLER is deliberately NOT minted.
}


def _ld(genus, diffs):
    return {"form": "obo-genus-differentia", "operator": "intersection_of",
            "genus": genus, "differentiae": diffs}


SHARD_RECORDS = [
    {"id": "urn:onto-obo:GO_TERMX", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:GO_GENUS"],
                              [{"property": "regulates", "filler": "urn:onto-obo:GO_FILLER"}])},
    {"id": "urn:onto-obo:GO_NODEF", "schema": "kot-obo/1",
     "axioms": [{"rel": "is_a", "target": "urn:onto-obo:GO_GENUS"}]},  # no logicalDefinition
    {"id": "urn:onto-obo:GO_UNRES", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:GO_GENUS"],
                              [{"property": "regulates", "filler": "urn:onto-obo:GO_MISSINGFILLER"}])},
    {"id": "urn:onto-obo:GO_BADREL", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:GO_GENUS"],
                              [{"property": "totally_unknown_rel", "filler": "urn:onto-obo:GO_FILLER"}])},
]

ENDORSEMENT_REF = "axioms-v0/endorse-go.json"
ENDORSEMENT = {
    "schema": "kot-axiom/1",
    "subject": MARKER,
    "constraints": [
        {"kind": "definitional", "form": "obo-genus-differentia",
         "source": {"corpus": "onto-obo", "shard": "go.jsonl",
                    "sourceVersion": "sha256:" + "0" * 64}},
    ],
}
# the license ref the answer carries: <endorsement ref>#<constraint index>
LICENSE_REF = ENDORSEMENT_REF + "#0"


def build():
    return kot_axiom.Engine(
        [(ENDORSEMENT_REF, ENDORSEMENT)], [],
        obo_shards={"go.jsonl": SHARD_RECORDS}, mint_bridge=MINT_BRIDGE)


class TestDefineAnswerPath(unittest.TestCase):
    def setUp(self):
        self.eng = build()

    def test_define_retrieve(self):
        r = self.eng.query({"op": "define", "subject": X})
        self.assertEqual(r["status"], "answer")
        self.assertEqual(r["value"], {
            "form": "genus-differentia",
            "genus": [G],
            "differentiae": [{"relation": R, "filler": F}],
        })
        self.assertEqual(r["provenance"], ["urn:onto-obo:GO_TERMX"])
        self.assertEqual(r["license"], [LICENSE_REF])

    def test_index_membership(self):
        # licensing = shard membership: every minted concept is admitted, even
        # the no-definition / unresolvable ones (they refuse at query, not here).
        self.assertEqual(self.eng.defn_licensed,
                         {X, NODEF, UNRES, BADREL})
        self.assertEqual(set(self.eng.defn), {X})
        self.assertEqual(self.eng.defn_unresolved, {UNRES, BADREL})


class TestDefineRefusals(unittest.TestCase):
    def setUp(self):
        self.eng = build()

    def _code(self, q):
        r = self.eng.query(q)
        self.assertEqual(r["status"], "refuse")
        return r["code"]

    def test_bad_query_unknown_op(self):
        self.assertEqual(self._code({"op": "nonsense"}), "ERR_BAD_QUERY")

    def test_bad_query_missing_subject(self):
        self.assertEqual(self._code({"op": "define"}), "ERR_BAD_QUERY")

    def test_bad_query_subject_not_urn(self):
        self.assertEqual(self._code({"op": "define", "subject": "not-a-urn"}),
                         "ERR_BAD_QUERY")

    def test_bad_query_unexpected_field(self):
        self.assertEqual(self._code({"op": "define", "subject": X, "rel": R}),
                         "ERR_BAD_QUERY")

    def test_term_unlicensed(self):
        self.assertEqual(self._code({"op": "define", "subject": OTHER}),
                         "ERR_TERM_UNLICENSED")

    def test_no_definition(self):
        self.assertEqual(self._code({"op": "define", "subject": NODEF}),
                         "ERR_NO_DEFINITION")

    def test_defn_unresolved_missing_filler(self):
        self.assertEqual(self._code({"op": "define", "subject": UNRES}),
                         "ERR_DEFN_UNRESOLVED")

    def test_defn_unresolved_unknown_shorthand(self):
        self.assertEqual(self._code({"op": "define", "subject": BADREL}),
                         "ERR_DEFN_UNRESOLVED")


class TestDefineMatch(unittest.TestCase):
    def setUp(self):
        self.eng = build()

    def test_match_true(self):
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": [G], "differentiae": [{"relation": R, "filler": F}]}})
        self.assertEqual(r["status"], "answer")
        self.assertIs(r["value"], True)
        self.assertEqual(r["provenance"], ["urn:onto-obo:GO_TERMX"])
        self.assertEqual(r["license"], [LICENSE_REF])

    def test_match_false_is_licensed(self):
        # a licensed, definitive FALSE — the load-bearing distinction from the
        # four CWA ops (memo §2.2, ASM-DEF-2): different filler.
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": [G], "differentiae": [{"relation": R, "filler": F2}]}})
        self.assertEqual(r["status"], "answer")
        self.assertIs(r["value"], False)

    def test_match_false_missing_differentia(self):
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": [G], "differentiae": []}})
        self.assertIs(r["value"], False)

    def test_match_order_and_dup_independence(self):
        # set-equality: reordered + duplicated genus/differentiae still True.
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": [G, G],
            "differentiae": [{"relation": R, "filler": F}, {"relation": R, "filler": F}]}})
        self.assertIs(r["value"], True)

    def test_match_malformed_candidate_is_bad_query(self):
        # shape precedes licensing: malformed candidate -> ERR_BAD_QUERY.
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": [G], "differentiae": [{"relation": R}]}})  # no filler
        self.assertEqual(r["code"], "ERR_BAD_QUERY")

    def test_match_non_urn_candidate_component_is_bad_query(self):
        r = self.eng.query({"op": "define", "subject": X, "candidate": {
            "genus": ["not-a-urn"], "differentiae": []}})
        self.assertEqual(r["code"], "ERR_BAD_QUERY")

    def test_licensing_precedes_match_for_wellformed_candidate(self):
        # well-formed candidate on an unlicensed subject -> ERR_TERM_UNLICENSED.
        r = self.eng.query({"op": "define", "subject": OTHER, "candidate": {
            "genus": [G], "differentiae": [{"relation": R, "filler": F}]}})
        self.assertEqual(r["code"], "ERR_TERM_UNLICENSED")


class TestStrataSeparationAndBoundary(unittest.TestCase):
    def test_definitional_never_enters_cwa_pass(self):
        # ASM-DEF-4: the endorsement adds nothing to the store indexes and
        # produces no violation.
        eng = build()
        self.assertNotIn(MARKER, eng.licensed_classes)
        self.assertNotIn(MARKER, eng.licensed_rels)
        self.assertEqual(eng.violations, [])
        self.assertEqual(eng.incomplete, set())
        self.assertEqual(len(eng.definitional_endorsements), 1)

    def test_subclassof_still_refused(self):
        # memo §6 C1: the subClassOf refusal is untouched and unreachable
        # through define — a subClassOf record is still refused at load.
        rec = {"schema": "kot-axiom/1", "subject": MARKER,
               "constraints": [{"kind": "subClassOf", "target": G}]}
        with self.assertRaises(kot_axiom.KotAxiomError) as cm:
            kot_axiom.Engine([("axioms-v0/sc.json", rec)], [])
        self.assertEqual(cm.exception.code, "ERR_AXIOM_UNIMPLEMENTED")

    def test_define_not_reachable_from_subclassof(self):
        self.assertIn("define", kot_axiom.QUERY_OPS)
        self.assertNotIn("subClassOf", kot_axiom.QUERY_OPS)


class TestEndorsementGrammar(unittest.TestCase):
    def _bad(self, constraint):
        rec = {"schema": "kot-axiom/1", "subject": MARKER, "constraints": [constraint]}
        with self.assertRaises(kot_axiom.KotAxiomError) as cm:
            kot_axiom.Engine([("axioms-v0/bad.json", rec)], [])
        return cm.exception.code

    def test_bad_form(self):
        self.assertEqual(self._bad(
            {"kind": "definitional", "form": "owl-equivalent",
             "source": {"corpus": "onto-obo", "shard": "go.jsonl",
                        "sourceVersion": "sha256:" + "0" * 64}}),
            "ERR_AXIOM_GRAMMAR")

    def test_missing_source(self):
        self.assertEqual(self._bad(
            {"kind": "definitional", "form": "obo-genus-differentia"}),
            "ERR_AXIOM_GRAMMAR")

    def test_unpinned_source_version(self):
        self.assertEqual(self._bad(
            {"kind": "definitional", "form": "obo-genus-differentia",
             "source": {"corpus": "onto-obo", "shard": "go.jsonl",
                        "sourceVersion": "not-a-sha"}}),
            "ERR_AXIOM_GRAMMAR")

    def test_valid_endorsement_accepts(self):
        eng = build()  # the good endorsement builds without raising
        self.assertEqual(len(eng.axioms), 1)


class TestDeterminism(unittest.TestCase):
    def test_repeat_identical(self):
        eng = build()
        q = {"op": "define", "subject": X}
        a = json.dumps(eng.query(q), sort_keys=True)
        b = json.dumps(build().query(q), sort_keys=True)
        self.assertEqual(a, b)

    def test_alias_table_targets_are_pinned_iris(self):
        # closed 10-value inventory (memo §3.3), each a urn:onto-obo: IRI.
        self.assertEqual(len(kot_axiom.PINNED_RELATION_ALIASES), 10)
        for iri in kot_axiom.PINNED_RELATION_ALIASES.values():
            self.assertTrue(iri.startswith("urn:onto-obo:"))


class TestRealCorporaSmoke(unittest.TestCase):
    def test_build_engine_unaffected(self):
        # build_engine on the real repo still works (no endorsement present ->
        # no onto-obo read), the four ops behave, and define integrates.
        eng = kot_axiom.build_engine(_ROOT)
        self.assertEqual(eng.query({"op": "bogus"})["code"], "ERR_BAD_QUERY")
        # no definitional endorsement in axioms-v0 -> every define is unlicensed.
        self.assertEqual(eng.query({"op": "define", "subject": OTHER})["code"],
                         "ERR_TERM_UNLICENSED")
        self.assertEqual(eng.defn_licensed, set())


if __name__ == "__main__":
    unittest.main()
