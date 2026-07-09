"""Unit tests for the kot-query/1 `define`-op (DEFINE + DEFINE-MATCH), its
stratum-3 `definitional` endorsement kind, the resolved-`relation`-field
resolution (bead 8es/o6pj) with the pinned relation-shorthand alias table as
fallback, and the endorsement home data/axioms-definitional-v0/ (bead bmtq)
(docs/design-kot-query-define-op.md — the FROZEN memo).

Style: tools/kb/test_kb.py / tools/registry/test_fixtures.py (stdlib unittest,
fail-closed paths pinned). Most tests build the engine from small in-memory
fixtures; TestEndorsementHome + TestRealCorporaSmoke read the real corpus
(build_engine loads the endorsed GO/SO/MONDO shards, ~4s) — the census that
MEASURES the checkable delta is the separate Opus step, not exercised here.

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


# --- relation-field resolution fixture (bead 8es/o6pj) ---
# A SEPARATE shard/bridge from SHARD_RECORDS above, so the exact-set assertions
# in TestDefineAnswerPath.test_index_membership are untouched. Exercises the
# resolved `relation` URN the onto-obo extractor now writes per differentia.
RQUAL = kurn("relqual")   # resolved `has_quality` relation URN (OUTSIDE the alias table)
RALT = kurn("relalt")     # a resolved relation URN that DIVERGES from the alias target
RELX = kurn("relconx")    # subject: relation-only resolvable (property not in alias table)
GOSTYLE = kurn("gostylx")  # subject: property in alias table AND relation == alias target
DIVERGE = kurn("divergx")  # subject: property is a known alias but relation points elsewhere
RELUNM = kurn("relunmx")   # subject: relation field present but unminted -> unresolved

# has_quality is NOT one of the 10 pinned alias-table shorthands: without the
# resolved `relation` field it could never resolve (this is the SO/MONDO unlock).
HAS_QUALITY_IRI = "urn:onto-obo:RO_0000086"
assert "has_quality" not in kot_axiom.PINNED_RELATION_ALIASES
# an alias-table shorthand whose resolved `relation` we make DIVERGE, to prove
# the relation field takes precedence over the shorthand alias lookup.
ALT_REL_IRI = "urn:onto-obo:RO_9999999"

MINT_BRIDGE_REL = {
    "urn:onto-obo:R_TERMX": RELX,
    "urn:onto-obo:R_GOSTYLE": GOSTYLE,
    "urn:onto-obo:R_DIVERGE": DIVERGE,
    "urn:onto-obo:R_UNMINTED": RELUNM,
    "urn:onto-obo:R_GENUS": G,
    "urn:onto-obo:R_FILLER": F,
    HAS_QUALITY_IRI: RQUAL,
    ALT_REL_IRI: RALT,
    REGULATES_IRI: R,  # the alias-table target for `regulates`
    # NOTE: urn:onto-obo:RO_NOTMINTED (the unmintable relation) is absent by design.
}

SHARD_RECORDS_REL = [
    # relation field present, property OUTSIDE the alias table -> resolves ONLY
    # because of the resolved `relation` URN.
    {"id": "urn:onto-obo:R_TERMX", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:R_GENUS"],
                              [{"property": "has_quality", "relation": HAS_QUALITY_IRI,
                                "filler": "urn:onto-obo:R_FILLER"}])},
    # relation field present AND equal to the alias-table target for `regulates`:
    # the GO case — resolves identically down either path (byte-unchanged).
    {"id": "urn:onto-obo:R_GOSTYLE", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:R_GENUS"],
                              [{"property": "regulates", "relation": REGULATES_IRI,
                                "filler": "urn:onto-obo:R_FILLER"}])},
    # property is a known alias (`regulates`) but the resolved relation DIVERGES:
    # precedence — the relation field wins, not the alias lookup.
    {"id": "urn:onto-obo:R_DIVERGE", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:R_GENUS"],
                              [{"property": "regulates", "relation": ALT_REL_IRI,
                                "filler": "urn:onto-obo:R_FILLER"}])},
    # relation field present but its IRI is not minted -> fail-closed (memo §6 C4).
    {"id": "urn:onto-obo:R_UNMINTED", "schema": "kot-obo/1",
     "logicalDefinition": _ld(["urn:onto-obo:R_GENUS"],
                              [{"property": "has_quality", "relation": "urn:onto-obo:RO_NOTMINTED",
                                "filler": "urn:onto-obo:R_FILLER"}])},
]

ENDORSEMENT_REL = {
    "schema": "kot-axiom/1", "subject": MARKER,
    "constraints": [
        {"kind": "definitional", "form": "obo-genus-differentia",
         "source": {"corpus": "onto-obo", "shard": "so.jsonl",
                    "sourceVersion": "sha256:" + "0" * 64}},
    ],
}


def build_rel():
    return kot_axiom.Engine(
        [("axioms-definitional-v0/endorse-so.json", ENDORSEMENT_REL)], [],
        obo_shards={"so.jsonl": SHARD_RECORDS_REL}, mint_bridge=MINT_BRIDGE_REL)


class TestRelationFieldResolution(unittest.TestCase):
    """The resolved `relation` URN field (bead 8es) is read at index build, the
    §3.3 alias table is the fallback, and resolution still fails closed."""

    def setUp(self):
        self.eng = build_rel()

    def test_relation_field_unlocks_outside_alias_table(self):
        # has_quality is not in the alias table; the concept resolves anyway
        # because the extractor wrote a resolved `relation` URN. This is the
        # SO/MONDO unlock, in miniature.
        r = self.eng.query({"op": "define", "subject": RELX})
        self.assertEqual(r["status"], "answer")
        self.assertEqual(r["value"]["differentiae"], [{"relation": RQUAL, "filler": F}])

    def test_relation_field_equal_to_alias_target_is_byte_identical(self):
        # GO case: property regulates, relation == the alias-table target -> the
        # resolved relation URN is exactly what the alias path would have produced.
        r = self.eng.query({"op": "define", "subject": GOSTYLE})
        self.assertEqual(r["value"]["differentiae"], [{"relation": R, "filler": F}])

    def test_relation_field_takes_precedence_over_shorthand(self):
        # property regulates (a known alias -> would resolve to R) but the resolved
        # relation diverges to RALT: the field wins.
        r = self.eng.query({"op": "define", "subject": DIVERGE})
        self.assertEqual(r["value"]["differentiae"], [{"relation": RALT, "filler": F}])
        self.assertNotEqual(RALT, R)

    def test_relation_field_unminted_fails_closed(self):
        # relation present but unmintable -> ERR_DEFN_UNRESOLVED, never half-answered.
        self.assertIn(RELUNM, self.eng.defn_licensed)
        self.assertIn(RELUNM, self.eng.defn_unresolved)
        self.assertEqual(self.eng.query({"op": "define", "subject": RELUNM})["code"],
                         "ERR_DEFN_UNRESOLVED")

    def test_alias_fallback_still_used_when_relation_absent(self):
        # the original SHARD_RECORDS carry NO relation field: the alias-table
        # fallback still resolves them (regression that the fallback survives).
        eng = build()
        r = eng.query({"op": "define", "subject": X})
        self.assertEqual(r["value"]["differentiae"], [{"relation": R, "filler": F}])


class TestEndorsementHome(unittest.TestCase):
    """The endorsement corpus lives in its OWN home (data/axioms-definitional-v0/),
    NOT l3a's frozen data/axioms-v0/; build_engine loads it from there."""

    def test_loader_reads_new_home(self):
        recs = kot_axiom.load_definitional_endorsements(_ROOT)
        self.assertEqual(len(recs), 3)
        shards = set()
        for ref, rec in recs:
            self.assertTrue(ref.startswith("axioms-definitional-v0/"))
            self.assertEqual(rec["schema"], "kot-axiom/1")
            cons = rec["constraints"]
            self.assertEqual(len(cons), 1)
            c = cons[0]
            self.assertEqual(c["kind"], "definitional")
            self.assertEqual(c["form"], "obo-genus-differentia")
            self.assertTrue(c["source"]["sourceVersion"].startswith("sha256:"))
            shards.add(c["source"]["shard"])
        self.assertEqual(shards, {"go.jsonl", "so.jsonl", "mondo.jsonl"})

    def test_l3a_store_corpus_carries_no_endorsements(self):
        # scoping: load_corpora (l3a's axioms-v0 store path) must contain NO
        # definitional endorsement — the two corpora are disjoint, so l3a's
        # frozen pin is untouched.
        axioms, _world = kot_axiom.load_corpora(_ROOT)
        for _ref, rec in axioms:
            for c in rec.get("constraints", []):
                self.assertNotEqual(c.get("kind"), "definitional")


class TestRealCorporaSmoke(unittest.TestCase):
    def test_build_engine_loads_endorsement_home(self):
        # build_engine on the real repo loads the definitional endorsement corpus
        # (data/axioms-definitional-v0/) and the referenced onto-obo shards, so the
        # define-op is LIVE: the four ops still behave and define resolves real
        # concepts. (~4s: reads the endorsed GO/SO/MONDO shards.)
        eng = kot_axiom.build_engine(_ROOT)
        self.assertEqual(eng.query({"op": "bogus"})["code"], "ERR_BAD_QUERY")
        # a made-up urn:kot: outside every endorsed shard is still unlicensed.
        self.assertEqual(eng.query({"op": "define", "subject": OTHER})["code"],
                         "ERR_TERM_UNLICENSED")
        # the endorsement home is now populated -> the define-op admits real
        # concepts and resolves a non-empty set of them.
        self.assertEqual(len(eng.definitional_endorsements), 3)
        self.assertGreater(len(eng.defn_licensed), 0)
        self.assertGreater(len(eng.defn), 0)
        # a resolved subject answers with a well-formed genus-differentia record.
        subj = sorted(eng.defn)[0]
        r = eng.query({"op": "define", "subject": subj})
        self.assertEqual(r["status"], "answer")
        self.assertEqual(r["value"]["form"], "genus-differentia")
        self.assertTrue(r["value"]["genus"])


if __name__ == "__main__":
    unittest.main()
