#!/usr/bin/env python3
"""kot_axiom — the kot-axiom/1 v0 engine: closed-world validator + rules-engine
oracle over the axiom sidecar (stratum 3) and the world layer (stratum 4).

Design sources (every semantic choice cites its record):
  docs/design-constraint-layer.md §3.3     the kot-axiom/1 closed constraint
                                           inventory + caps + validation-procedure
                                           semantics (CWA over asserted records)
  docs/design-l3a-rules-engine-oracle.md   the kot-world/1 record shape, the
                                           kot-query/1 closed query grammar, the
                                           licensing rules and refusal codes
                                           (this file implements that spec; the
                                           spec is the pre-registration anchor)
  docs/next/architecture-ladder.md §5.1    L3a — engine answers covered queries
                                           by deterministic index lookup with
                                           provenance + axiom license; fail-closed
                                           ABSTAIN everywhere else
  docs/kernel-design-directives.md §1/§5   native formalism (no RDF/OWL/SHACL
                                           semantics imported); facts live in the
                                           world layer, never in concept identity

House rules honoured: zero runtime deps; no silent fallbacks — every refusal
carries a named ERR_* code; determinism (dict/set iteration is never allowed to
leak into outputs: all collections are sorted before use).

v0 constraint inventory implemented: functional, cardinality, disjointWith,
inverseOf, domain, range. `subClassOf` is IN the kot-axiom/1 grammar
(design-constraint-layer.md §3.3) but NOT implemented by this v0 engine: a
record carrying it is refused at load (ERR_AXIOM_UNIMPLEMENTED) — fail-closed,
never partially honoured.

define-op (docs/design-kot-query-define-op.md, the FROZEN memo): a fifth
kot-query/1 op — DEFINE (retrieve a concept's endorsed genus-differentia
definition, at one level, verbatim) and DEFINE-MATCH (exact structural
set-equality of a candidate against it). It is licensed by a new stratum-3
`definitional` constraint kind: a corpus-scoped endorsement admitting a pinned
onto-obo shard's logicalDefinitions as a definitional-source. The endorsement
is an ENDORSEMENT, not an extension-constraint (memo §3, ASM-DEF-4): it is
consumed ONLY by the define-op index and NEVER enters the CWA store-validation
pass over world-layer facts. No subsumption / no transitive closure — that is
the refused `subClassOf` op (memo §6 C1). No OWL/DL model theory, no cosine
(memo §6 C2/C3). Fail-closed resolution through the pinned relation-shorthand
alias table + the onto-obo mint bridge (ERR_DEFN_UNRESOLVED, memo §6 C4).
"""

import json
import os
import re

SCHEMA_AXIOM = "kot-axiom/1"
SCHEMA_WORLD = "kot-world/1"
CONCEPT_URN_RE = re.compile(r"^urn:kot:[a-z2-7]{10,}$")
ENTITY_URN_RE = re.compile(r"^urn:kotw:v0:[a-z0-9][a-z0-9-]*$")

# design-constraint-layer.md §3.3 caps (conformance-defining)
MAX_CONSTRAINTS_PER_RECORD = 32
MAX_CARD_BOUND = 64

CONSTRAINT_KINDS = ("subClassOf", "disjointWith", "domain", "range",
                    "inverseOf", "functional", "cardinality", "definitional")
IMPLEMENTED_KINDS = ("disjointWith", "domain", "range", "inverseOf",
                     "functional", "cardinality", "definitional")
# `definitional` is a stratum-3 ENDORSEMENT kind (memo §3, ASM-DEF-4): disjoint
# from the extension-constraint kinds below; consumed only by the define-op,
# never by the CWA store pass. Extension kinds that drive store validation:
EXTENSION_KINDS = ("disjointWith", "domain", "range", "inverseOf",
                   "functional", "cardinality")
DIRECTIONS = ("forward", "inverse")

QUERY_OPS = ("unique", "lookup", "count", "instance", "define")
DEFINITION_FORM = "obo-genus-differentia"

# design-kot-query-define-op.md §3.3 — the pinned relation-shorthand alias table.
# An OBO differentia `property` is stored as a bare shorthand string, NOT a URN;
# it is resolved shorthand -> relation IRI (here) -> minted urn:kot: URN (via the
# onto-obo mint bridge) at index-build time. Closed 10-value inventory over the
# whole GO+PO differentia corpus (memo §1/§3.3, MEASURED histogram). LIT-BACKED
# against the OBO Relation Ontology; resolution fails closed (ERR_DEFN_UNRESOLVED)
# if the IRI is not present + minted in the endorsed shard's mint bridge — the
# table is never trusted over the data.
PINNED_RELATION_ALIASES = {
    "part_of": "urn:onto-obo:BFO_0000050",
    "regulates": "urn:onto-obo:RO_0002211",
    "positively_regulates": "urn:onto-obo:RO_0002213",
    "negatively_regulates": "urn:onto-obo:RO_0002212",
    "occurs_in": "urn:onto-obo:BFO_0000066",
    "has_part": "urn:onto-obo:BFO_0000051",
    "happens_during": "urn:onto-obo:RO_0002092",
    "participates_in": "urn:onto-obo:RO_0000056",
    "has_participant": "urn:onto-obo:RO_0000057",
    "develops_from": "urn:onto-obo:RO_0002202",
}

# Refusal codes (closed set — the eval set's expected.code values come from here)
REFUSAL_CODES = (
    "ERR_BAD_QUERY",          # malformed: unknown op / missing field / bad URN
    "ERR_TERM_UNLICENSED",    # relation/concept not in the endorsed axiom layer
    "ERR_UNKNOWN_ENTITY",     # entity id never asserted in the world layer
    "ERR_CONFLICT",           # query touches a store region with a validated
                              # axiom violation — surfaced, never resolved
                              # (design-constraint-layer.md fail-closed rule;
                              # architecture-ladder.md §5 risk 4)
    "ERR_UNLICENSED_UNIQUE",  # no functional/cardinality-1 axiom licenses a
                              # unique answer in the queried direction
    "ERR_UNLICENSED_COUNT",   # no exact-cardinality axiom licenses a total count
    "ERR_COUNT_MISMATCH",     # asserted count != axiom-licensed exact total
    "ERR_NO_RECORD",          # licensed and well-formed, but no asserted record
    "ERR_NO_DEFINITION",      # define: subject licensed but carries no
                              # logicalDefinition (memo §2.1)
    "ERR_DEFN_UNRESOLVED",    # define: a differentia shorthand / genus / filler
                              # fails to resolve to a licensed urn:kot: URN under
                              # the pinned tables — a partially-resolvable
                              # definition is refused, never half-answered
                              # (memo §2.1/§6 C4, fail-closed)
)


class KotAxiomError(Exception):
    def __init__(self, code, msg):
        super().__init__("%s: %s" % (code, msg))
        self.code = code


def _require(cond, code, msg):
    if not cond:
        raise KotAxiomError(code, msg)


# ---------------------------------------------------------------- axiom layer


def validate_axiom_record(rec, ref):
    """Fail-closed structural validation of one kot-axiom/1 record
    (grammar + caps per design-constraint-layer.md §3.3)."""
    _require(isinstance(rec, dict), "ERR_AXIOM_GRAMMAR", "%s: not an object" % ref)
    _require(rec.get("schema") == SCHEMA_AXIOM, "ERR_AXIOM_GRAMMAR",
             "%s: schema != %s" % (ref, SCHEMA_AXIOM))
    _require(CONCEPT_URN_RE.match(rec.get("subject", "")) is not None,
             "ERR_AXIOM_GRAMMAR", "%s: subject is not a urn:kot: concept URN" % ref)
    cs = rec.get("constraints")
    _require(isinstance(cs, list) and 1 <= len(cs) <= MAX_CONSTRAINTS_PER_RECORD,
             "ERR_AXIOM_GRAMMAR", "%s: constraints must be 1..%d" % (ref, MAX_CONSTRAINTS_PER_RECORD))
    for i, c in enumerate(cs):
        where = "%s#%d" % (ref, i)
        _require(isinstance(c, dict), "ERR_AXIOM_GRAMMAR", "%s: not an object" % where)
        kind = c.get("kind")
        _require(kind in CONSTRAINT_KINDS, "ERR_AXIOM_GRAMMAR",
                 "%s: unknown kind %r" % (where, kind))
        _require(kind in IMPLEMENTED_KINDS, "ERR_AXIOM_UNIMPLEMENTED",
                 "%s: kind %r is in the kot-axiom/1 grammar but not implemented "
                 "by engine v0 — record refused (fail-closed)" % (where, kind))
        if kind in ("disjointWith", "domain", "range", "inverseOf"):
            _require(CONCEPT_URN_RE.match(c.get("target", "")) is not None,
                     "ERR_AXIOM_GRAMMAR", "%s: %s.target must be a concept URN" % (where, kind))
            extra = set(c) - {"kind", "target"}
            _require(not extra, "ERR_AXIOM_GRAMMAR", "%s: unexpected fields %s" % (where, sorted(extra)))
        elif kind == "functional":
            extra = set(c) - {"kind"}
            _require(not extra, "ERR_AXIOM_GRAMMAR", "%s: unexpected fields %s" % (where, sorted(extra)))
        elif kind == "cardinality":
            _require(CONCEPT_URN_RE.match(c.get("path", "")) is not None,
                     "ERR_AXIOM_GRAMMAR", "%s: cardinality.path must be a concept URN" % where)
            _require(c.get("direction") in DIRECTIONS,
                     "ERR_AXIOM_GRAMMAR", "%s: cardinality.direction must be forward|inverse" % where)
            _require("min" in c or "max" in c, "ERR_AXIOM_GRAMMAR",
                     "%s: cardinality needs min and/or max" % where)
            for b in ("min", "max"):
                if b in c:
                    _require(isinstance(c[b], int) and 0 <= c[b] <= MAX_CARD_BOUND,
                             "ERR_AXIOM_GRAMMAR", "%s: %s must be int 0..%d" % (where, b, MAX_CARD_BOUND))
            if "min" in c and "max" in c:
                _require(c["min"] <= c["max"], "ERR_AXIOM_GRAMMAR", "%s: min > max" % where)
            if "qualifier" in c:
                _require(CONCEPT_URN_RE.match(c.get("qualifier", "")) is not None,
                         "ERR_AXIOM_GRAMMAR", "%s: qualifier must be a concept URN "
                         "(depth-1 rule, §3.3 caps)" % where)
            extra = set(c) - {"kind", "path", "direction", "min", "max", "qualifier"}
            _require(not extra, "ERR_AXIOM_GRAMMAR", "%s: unexpected fields %s" % (where, sorted(extra)))
        elif kind == "definitional":
            # stratum-3 corpus-scoped endorsement (memo §3.1): admits a pinned
            # onto-obo shard's logicalDefinitions as a definitional-source.
            _require(c.get("form") == DEFINITION_FORM, "ERR_AXIOM_GRAMMAR",
                     "%s: definitional.form must be %r" % (where, DEFINITION_FORM))
            src = c.get("source")
            _require(isinstance(src, dict), "ERR_AXIOM_GRAMMAR",
                     "%s: definitional.source must be an object" % where)
            _require(isinstance(src.get("corpus"), str) and src["corpus"],
                     "ERR_AXIOM_GRAMMAR", "%s: source.corpus required" % where)
            _require(isinstance(src.get("shard"), str) and src["shard"],
                     "ERR_AXIOM_GRAMMAR", "%s: source.shard required" % where)
            _require(isinstance(src.get("sourceVersion"), str)
                     and src["sourceVersion"].startswith("sha256:"),
                     "ERR_AXIOM_GRAMMAR", "%s: source.sourceVersion must be a "
                     "sha256: pin" % where)
            src_extra = set(src) - {"corpus", "shard", "sourceVersion"}
            _require(not src_extra, "ERR_AXIOM_GRAMMAR",
                     "%s: unexpected source fields %s" % (where, sorted(src_extra)))
            extra = set(c) - {"kind", "form", "source"}
            _require(not extra, "ERR_AXIOM_GRAMMAR", "%s: unexpected fields %s" % (where, sorted(extra)))


def validate_world_record(rec, ref):
    """Fail-closed structural validation of one kot-world/1 record
    (shape per design-l3a-rules-engine-oracle.md §2)."""
    _require(isinstance(rec, dict), "ERR_WORLD_GRAMMAR", "%s: not an object" % ref)
    _require(rec.get("schema") == SCHEMA_WORLD, "ERR_WORLD_GRAMMAR",
             "%s: schema != %s" % (ref, SCHEMA_WORLD))
    _require(isinstance(rec.get("id"), str) and rec["id"], "ERR_WORLD_GRAMMAR",
             "%s: missing id" % ref)
    _require(isinstance(rec.get("provenance"), dict) and rec["provenance"].get("source"),
             "ERR_WORLD_GRAMMAR", "%s: provenance.source required (directives §5: "
             "world-layer facts carry provenance)" % ref)
    kind = rec.get("kind")
    if kind == "class":
        _require(ENTITY_URN_RE.match(rec.get("entity", "")) is not None,
                 "ERR_WORLD_GRAMMAR", "%s: entity must be urn:kotw:v0:*" % ref)
        _require(CONCEPT_URN_RE.match(rec.get("concept", "")) is not None,
                 "ERR_WORLD_GRAMMAR", "%s: concept must be urn:kot:*" % ref)
    elif kind == "relation":
        _require(CONCEPT_URN_RE.match(rec.get("relation", "")) is not None,
                 "ERR_WORLD_GRAMMAR", "%s: relation must be urn:kot:*" % ref)
        for side in ("subject", "object"):
            _require(ENTITY_URN_RE.match(rec.get(side, "")) is not None,
                     "ERR_WORLD_GRAMMAR", "%s: %s must be urn:kotw:v0:*" % (ref, side))
    else:
        raise KotAxiomError("ERR_WORLD_GRAMMAR", "%s: kind must be class|relation" % ref)


class Engine(object):
    """The L3a oracle. Deterministic index lookups; every answer carries
    provenance (world-record ids) and license (axiom constraint refs);
    everything else is a named refusal (fail-closed ABSTAIN)."""

    def __init__(self, axiom_records, world_records, obo_shards=None,
                 mint_bridge=None):
        # axiom_records: list of (ref, record); world_records: list of record.
        # obo_shards: {shard_name: [onto-obo records]} — the endorsed
        #   definitional substrate (memo §2.3/§3); optional, define-op only.
        # mint_bridge: {urn:onto-obo:<id>: urn:kot:<urn>} — the mint bridge
        #   (data/onto-obo/minted-urns.jsonl); optional, define-op only.
        self.axioms = {}            # ref -> record
        self.functional = {}        # rel -> [axiom refs] (forward direction)
        self.inverse_of = {}        # rel -> (partner rel, axiom ref)
        self.disjoint = {}          # concept -> {other concept: axiom ref}
        self.range_of = {}          # rel -> (target concept, axiom ref)
        self.domain_of = {}         # rel -> (target concept, axiom ref)
        self.cardinality = []       # (subject concept, constraint dict, axiom ref)
        self.licensed_rels = set()  # relations admitted to the axiom layer
        self.licensed_classes = set()

        # define-op (memo §2.3): the stratum-3 `definitional` endorsements and
        # the definitional index they license. DISJOINT from the store pass
        # above — no definitional data touches licensed_rels/classes or any CWA
        # index (ASM-DEF-4).
        self.obo_shards = obo_shards or {}
        self.mint_bridge = mint_bridge or {}
        self.definitional_endorsements = []  # (license_ref, source_shard, subject)
        self.defn_licensed = set()  # urn:kot: subjects admitted by an endorsement
        self.defn = {}              # subj -> {genus, differentiae, provenance, license}
        self.defn_unresolved = set()  # subj with a logicalDefinition that fails to resolve

        for ref, rec in sorted(axiom_records):
            validate_axiom_record(rec, ref)
            _require(ref not in self.axioms, "ERR_AXIOM_GRAMMAR", "duplicate axiom ref %s" % ref)
            self.axioms[ref] = rec
            subj = rec["subject"]
            for i, c in enumerate(rec["constraints"]):
                cref = "%s#%d" % (ref, i)
                kind = c["kind"]
                if kind == "functional":
                    self.functional.setdefault(subj, []).append(cref)
                    self.licensed_rels.add(subj)
                elif kind == "inverseOf":
                    _require(subj not in self.inverse_of, "ERR_AXIOM_GRAMMAR",
                             "%s: second inverseOf for %s" % (cref, subj))
                    self.inverse_of[subj] = (c["target"], cref)
                    self.licensed_rels.add(subj)
                    self.licensed_rels.add(c["target"])
                elif kind == "disjointWith":
                    self.disjoint.setdefault(subj, {})[c["target"]] = cref
                    self.disjoint.setdefault(c["target"], {})[subj] = cref  # symmetric
                    self.licensed_classes.add(subj)
                    self.licensed_classes.add(c["target"])
                elif kind == "range":
                    self.range_of[subj] = (c["target"], cref)
                    self.licensed_rels.add(subj)
                    self.licensed_classes.add(c["target"])
                elif kind == "domain":
                    self.domain_of[subj] = (c["target"], cref)
                    self.licensed_rels.add(subj)
                    self.licensed_classes.add(c["target"])
                elif kind == "cardinality":
                    self.cardinality.append((subj, c, cref))
                    self.licensed_rels.add(c["path"])
                    self.licensed_classes.add(subj)
                    if "qualifier" in c:
                        self.licensed_classes.add(c["qualifier"])
                elif kind == "definitional":
                    # ENDORSEMENT (memo §3): collected for the define-op index
                    # only. Deliberately NOT added to licensed_rels/classes or
                    # any store index — it never enters the CWA pass (ASM-DEF-4).
                    self.definitional_endorsements.append(
                        (cref, c["source"]["shard"], subj))

        # inverseOf canonicalisation: assertions under either name are stored
        # under the lexicographically-smaller URN (deterministic; documented in
        # design-l3a-rules-engine-oracle.md §3). Cross-name conflicts are
        # thereby impossible by construction.
        self.canonical = {}
        for rel, (partner, _cref) in sorted(self.inverse_of.items()):
            canon = min(rel, partner)
            self.canonical[rel] = canon
            self.canonical[partner] = canon

        # World indexes.
        self.rel_fwd = {}   # (rel, subj entity) -> [(obj entity, rec id)]
        self.rel_inv = {}   # (rel, obj entity) -> [(subj entity, rec id)]
        self.classes = {}   # entity -> {concept: rec id}
        self.entities = set()
        self.world_ids = set()
        for rec in world_records:
            ref = rec.get("id", "?")
            validate_world_record(rec, ref)
            _require(ref not in self.world_ids, "ERR_WORLD_GRAMMAR", "duplicate world id %s" % ref)
            self.world_ids.add(ref)
            if rec["kind"] == "class":
                e, c = rec["entity"], rec["concept"]
                self.entities.add(e)
                self.classes.setdefault(e, {})
                # duplicate class assertion: keep first (deterministic; sorted input)
                self.classes[e].setdefault(c, ref)
            else:
                rel = rec["relation"]
                s, o = rec["subject"], rec["object"]
                if rel in self.canonical and self.canonical[rel] != rel:
                    rel, s, o = self.canonical[rel], o, s  # flip into canonical
                self.entities.add(s)
                self.entities.add(o)
                self.rel_fwd.setdefault((rel, s), []).append((o, ref))
                self.rel_inv.setdefault((rel, o), []).append((s, ref))
        for idx in (self.rel_fwd, self.rel_inv):
            for k in idx:
                idx[k].sort()

        self._validate_store()
        self._build_definitional_index()

    # ---------------------------------------------------- definitional index

    def _build_definitional_index(self):
        """Build defn[urn:kot:X] -> resolved genus-differentia tuple from the
        endorsed onto-obo shard(s) via the mint bridge + the pinned relation
        alias table (memo §2.3/§3.3). Licensing = shard membership: every minted
        concept in an endorsed shard is admitted (defn_licensed). Fail-closed
        (memo §6 C4): a licensed concept whose logicalDefinition has any
        unresolvable genus / differentia-shorthand / filler is recorded in
        defn_unresolved (query -> ERR_DEFN_UNRESOLVED), NEVER half-answered; a
        licensed concept with no logicalDefinition is admitted but absent from
        defn/defn_unresolved (query -> ERR_NO_DEFINITION). Consumed here and
        NOWHERE in the CWA store pass (ASM-DEF-4)."""
        for lic_ref, shard, _subj in sorted(self.definitional_endorsements):
            records = self.obo_shards.get(shard, [])
            for rec in sorted(records, key=lambda r: r.get("id", "")):
                rid = rec.get("id")
                subj_urn = self.mint_bridge.get(rid)
                if subj_urn is None:
                    continue  # unminted concept: not admittable to the define-op
                if subj_urn in self.defn or subj_urn in self.defn_unresolved:
                    self.defn_licensed.add(subj_urn)
                    continue  # first endorsement wins (deterministic, sorted)
                self.defn_licensed.add(subj_urn)
                ld = rec.get("logicalDefinition")
                if not isinstance(ld, dict):
                    continue  # admitted, no definition -> ERR_NO_DEFINITION
                tup = self._resolve_logical_definition(ld)
                if tup is None:
                    self.defn_unresolved.add(subj_urn)
                    continue
                genus, diffs = tup
                self.defn[subj_urn] = {
                    "genus": genus, "differentiae": diffs,
                    "provenance": rid, "license": lic_ref}

    def _resolve_logical_definition(self, ld):
        """Resolve one onto-obo logicalDefinition to
        (sorted genus urn:kot: list, sorted (relation-urn, filler-urn) list).
        Returns None (fail-closed, memo §6 C4) if the genus is empty or any
        component fails to resolve to a minted urn:kot: URN under the mint
        bridge + pinned alias table. Retrieval only — no closure, no OWL/DL."""
        genus_urns = []
        for g in (ld.get("genus") or []):
            gu = self.mint_bridge.get(g)
            if gu is None:
                return None
            genus_urns.append(gu)
        if not genus_urns:
            return None
        diffs = []
        for d in (ld.get("differentiae") or []):
            if not isinstance(d, dict):
                return None
            iri = PINNED_RELATION_ALIASES.get(d.get("property"))
            rel_urn = self.mint_bridge.get(iri) if iri is not None else None
            fil_urn = self.mint_bridge.get(d.get("filler"))
            if rel_urn is None or fil_urn is None:
                return None
            diffs.append((rel_urn, fil_urn))
        return sorted(set(genus_urns)), sorted(set(diffs))

    # ---------------------------------------------------------- store validation

    def _edges(self, rel, entity, direction):
        """Edge accessor honouring inverseOf canonicalisation: querying the
        non-canonical partner flips the direction (part-of(a,b) <=> has-part(b,a),
        design-constraint-layer.md §3.3 inverseOf semantics)."""
        canon = self.canonical.get(rel, rel)
        if canon != rel:
            rel = canon
            direction = "inverse" if direction == "forward" else "forward"
        if direction == "forward":
            return self.rel_fwd.get((rel, entity), [])
        return self.rel_inv.get((rel, entity), [])

    def _qualified_edges(self, rel, entity, direction, qualifier):
        edges = self._edges(rel, entity, direction)
        if qualifier is None:
            return edges
        return [(x, ref) for (x, ref) in edges if qualifier in self.classes.get(x, {})]

    def _validate_store(self):
        """CWA validation pass (design-constraint-layer.md §3.3 semantics).
        Violations are SURFACED, never resolved (§5 risk 4): every violation
        implicates (entity, term) pairs; queries touching an implicated pair
        refuse with ERR_CONFLICT. min-cardinality shortfalls are recorded as
        INCOMPLETENESS (count queries refuse ERR_COUNT_MISMATCH), not conflict."""
        self.violations = []   # {code, detail, implicated: [(entity, term)]}
        self.incomplete = set()  # (entity, rel) with min shortfall
        implicated = set()

        # functional: at most one asserted object per subject (forward).
        # Scanned through _edges so inverseOf canonicalisation cannot skew it.
        for rel in sorted(self.functional):
            for s in sorted(self.entities):
                objs = sorted(set(o for (o, _ref) in self._edges(rel, s, "forward")))
                if len(objs) > 1:
                    pairs = [(s, rel)]
                    self.violations.append({
                        "code": "VIOLATION_FUNCTIONAL",
                        "detail": "%s has %d asserted values for functional %s" % (s, len(objs), rel),
                        "implicated": pairs})
                    implicated.update(pairs)

        # disjointWith: no entity asserted two disjoint classes.
        for e in sorted(self.classes):
            asserted = sorted(self.classes[e])
            for i, c1 in enumerate(asserted):
                for c2 in asserted[i + 1:]:
                    if c2 in self.disjoint.get(c1, {}):
                        pairs = [(e, c1), (e, c2)]
                        self.violations.append({
                            "code": "VIOLATION_DISJOINT",
                            "detail": "%s asserted both %s and %s" % (e, c1, c2),
                            "implicated": pairs})
                        implicated.update(pairs)

        # range / domain: the far end must not be asserted a class disjoint
        # with the declared target. (Absent class assertions = incompleteness,
        # not violation — CWA validates what is written down, §3.3.)
        for rel, target, side in \
                [(r, t[0], "range") for r, t in sorted(self.range_of.items())] + \
                [(r, t[0], "domain") for r, t in sorted(self.domain_of.items())]:
            for s in sorted(self.entities):
                for (o, _ref) in self._edges(rel, s, "forward"):
                    end = o if side == "range" else s
                    for c in sorted(self.classes.get(end, {})):
                        if target in self.disjoint.get(c, {}):
                            pairs = [(s, rel), (end, rel)]
                            self.violations.append({
                                "code": "VIOLATION_%s" % side.upper(),
                                "detail": "%s of %s: %s asserted %s, disjoint with declared %s"
                                          % (side, rel, end, c, target),
                                "implicated": pairs})
                            implicated.update(pairs)

        # cardinality: per entity asserted the subject class.
        for subj_class, c, _cref in self.cardinality:
            for e in sorted(self.classes):
                if subj_class not in self.classes[e]:
                    continue
                n = len(self._qualified_edges(c["path"], e, c["direction"], c.get("qualifier")))
                if "max" in c and n > c["max"]:
                    pairs = [(e, c["path"])]
                    self.violations.append({
                        "code": "VIOLATION_CARD_MAX",
                        "detail": "%s: %d %s edges > max %d" % (e, n, c["path"], c["max"]),
                        "implicated": pairs})
                    implicated.update(pairs)
                elif "min" in c and n < c["min"]:
                    self.incomplete.add((e, c["path"]))

        self.implicated = implicated

    # ---------------------------------------------------------- query answering

    def _refuse(self, code, reason):
        assert code in REFUSAL_CODES
        return {"status": "refuse", "code": code, "reason": reason}

    def _answer(self, value, provenance, license_refs):
        return {"status": "answer", "value": value,
                "provenance": sorted(set(provenance)),
                "license": sorted(set(license_refs))}

    def _conflict_hit(self, entity, term):
        return (entity, term) in self.implicated

    def query(self, q):
        """Evaluate one kot-query/1 query. Validation order is pre-registered
        (design-l3a-rules-engine-oracle.md §4): shape -> term licensing ->
        entity existence -> conflict -> op license -> records."""
        # 1. shape
        if not isinstance(q, dict) or q.get("op") not in QUERY_OPS:
            return self._refuse("ERR_BAD_QUERY", "unknown or missing op")
        op = q["op"]
        if op == "define":
            wanted = {"op", "subject", "candidate"}
        elif op == "instance":
            wanted = {"op", "entity", "concept"}
        elif op == "count":
            wanted = {"op", "rel", "direction", "subject", "qualifier"}
        else:
            wanted = {"op", "rel", "direction", "subject"}
        if set(q) - wanted:
            return self._refuse("ERR_BAD_QUERY", "unexpected fields %s" % sorted(set(q) - wanted))

        if op == "define":
            return self._query_define(q)

        if op == "instance":
            e, c = q.get("entity", ""), q.get("concept", "")
            if not (ENTITY_URN_RE.match(e) and CONCEPT_URN_RE.match(c)):
                return self._refuse("ERR_BAD_QUERY", "bad entity/concept URN")
            if c not in self.licensed_classes:
                return self._refuse("ERR_TERM_UNLICENSED", "concept not in the axiom layer")
            if e not in self.entities:
                return self._refuse("ERR_UNKNOWN_ENTITY", "entity not in the world layer")
            if self._conflict_hit(e, c):
                return self._refuse("ERR_CONFLICT", "entity/class pair implicated in a store violation")
            if c in self.classes.get(e, {}):
                return self._answer(True, [self.classes[e][c]], ["asserted"])
            # a licensed "no" needs a disjointness axiom (CWA: absence is not falsity)
            for asserted in sorted(self.classes.get(e, {})):
                if self._conflict_hit(e, asserted):
                    return self._refuse("ERR_CONFLICT", "supporting class assertion is implicated")
                if c in self.disjoint.get(asserted, {}):
                    return self._answer(False, [self.classes[e][asserted]],
                                        [self.disjoint[asserted][c]])
            return self._refuse("ERR_NO_RECORD", "not asserted and no disjointness license")

        # relational ops
        rel, direction, subject = q.get("rel", ""), q.get("direction"), q.get("subject", "")
        if direction not in DIRECTIONS or not CONCEPT_URN_RE.match(rel) \
                or not ENTITY_URN_RE.match(subject):
            return self._refuse("ERR_BAD_QUERY", "bad rel/direction/subject")
        qualifier = q.get("qualifier")
        if op == "count" and qualifier is not None and not CONCEPT_URN_RE.match(qualifier):
            return self._refuse("ERR_BAD_QUERY", "bad qualifier URN")
        if rel not in self.licensed_rels:
            return self._refuse("ERR_TERM_UNLICENSED", "relation not in the axiom layer")
        if subject not in self.entities:
            return self._refuse("ERR_UNKNOWN_ENTITY", "entity not in the world layer")
        if self._conflict_hit(subject, rel):
            return self._refuse("ERR_CONFLICT", "entity/relation pair implicated in a store violation")

        edges = self._edges(rel, subject, direction)
        # refuse if any returned edge's far side is itself implicated
        for (other, _ref) in edges:
            if self._conflict_hit(other, rel):
                return self._refuse("ERR_CONFLICT", "a supporting record's far end is implicated")

        if op == "lookup":
            if not edges:
                return self._refuse("ERR_NO_RECORD", "no asserted records (no completeness claim)")
            lic = self._layer_license(rel)
            return self._answer(sorted(set(o for (o, _r) in edges)),
                                [r for (_o, r) in edges], lic)

        if op == "unique":
            lic = self._unique_license(rel, direction, subject)
            if not lic:
                return self._refuse("ERR_UNLICENSED_UNIQUE",
                                    "no functional/cardinality-1 axiom in this direction")
            objs = sorted(set(o for (o, _r) in edges))
            if not objs:
                return self._refuse("ERR_NO_RECORD", "licensed but no asserted record")
            if len(objs) > 1:
                return self._refuse("ERR_CONFLICT", "multiple values for a licensed-unique relation")
            return self._answer(objs[0], [r for (_o, r) in edges], lic)

        # count: licensed only by an exact-cardinality axiom whose scope matches
        # (the "a gloss file cannot count parents" claim, operationalised —
        # design-constraint-layer.md §5.2).
        lic_exact = None
        for subj_class, c, cref in self.cardinality:
            if c["path"] != rel or c["direction"] != direction:
                continue
            if c.get("qualifier") != qualifier:
                continue
            if "min" not in c or "max" not in c or c["min"] != c["max"]:
                continue
            if subj_class in self.classes.get(subject, {}):
                lic_exact = (c["min"], cref)
                break
        if lic_exact is None:
            return self._refuse("ERR_UNLICENSED_COUNT", "no matching exact-cardinality axiom")
        exact, cref = lic_exact
        qedges = self._qualified_edges(rel, subject, direction, qualifier)
        if len(qedges) != exact or (subject, rel) in self.incomplete:
            return self._refuse("ERR_COUNT_MISMATCH",
                                "asserted count %d != licensed exact %d" % (len(qedges), exact))
        return self._answer(exact, [r for (_o, r) in qedges], [cref])

    # ------------------------------------------------------- define-op answering

    def _canonicalise_candidate(self, cand):
        """Validate + canonicalise a DEFINE-MATCH candidate (memo §2.2). Returns
        {genus: sorted urn set, differentiae: sorted (rel,filler) set} or None on
        a malformed candidate (-> ERR_BAD_QUERY). Every genus/relation/filler
        must be a urn:kot: concept URN; equality is set-equality (no ordering
        dependence, no partial credit)."""
        if not isinstance(cand, dict) or (set(cand) - {"genus", "differentiae"}):
            return None
        genus, diffs = cand.get("genus"), cand.get("differentiae")
        if not isinstance(genus, list) or not isinstance(diffs, list):
            return None
        gset = []
        for g in genus:
            if not isinstance(g, str) or CONCEPT_URN_RE.match(g) is None:
                return None
            gset.append(g)
        dset = []
        for d in diffs:
            if not isinstance(d, dict) or (set(d) - {"relation", "filler"}):
                return None
            r, f = d.get("relation"), d.get("filler")
            if not isinstance(r, str) or CONCEPT_URN_RE.match(r) is None:
                return None
            if not isinstance(f, str) or CONCEPT_URN_RE.match(f) is None:
                return None
            dset.append((r, f))
        return {"genus": sorted(set(gset)), "differentiae": sorted(set(dset))}

    def _query_define(self, q):
        """DEFINE / DEFINE-MATCH (memo §2). Deterministic index lookup + exact
        structural set-equality — no search, no similarity (X3 ban), no
        subsumption / transitive closure (memo §6 C1). Pre-registered validation
        order: shape -> term licensing -> definition presence -> resolution."""
        subj = q.get("subject", "")
        if CONCEPT_URN_RE.match(subj) is None:
            return self._refuse("ERR_BAD_QUERY", "subject is not a urn:kot: concept URN")
        has_candidate = "candidate" in q
        cand_canon = None
        if has_candidate:
            cand_canon = self._canonicalise_candidate(q.get("candidate"))
            if cand_canon is None:
                return self._refuse("ERR_BAD_QUERY", "malformed candidate")

        # term licensing: subject must be admitted by a definitional endorsement
        if subj not in self.defn_licensed:
            return self._refuse("ERR_TERM_UNLICENSED",
                                "subject not in a definitional endorsement's admitted set")
        # a licensed subject whose definition failed to resolve is refused, never
        # half-answered (fail-closed, memo §6 C4)
        if subj in self.defn_unresolved:
            return self._refuse("ERR_DEFN_UNRESOLVED",
                                "subject's logicalDefinition has an unresolvable "
                                "genus/differentia/filler")
        if subj not in self.defn:
            return self._refuse("ERR_NO_DEFINITION",
                                "subject is licensed but carries no logicalDefinition")

        entry = self.defn[subj]
        prov, lic = [entry["provenance"]], [entry["license"]]
        if not has_candidate:
            # DEFINE: return the endorsed definition at one level, verbatim.
            value = {
                "form": "genus-differentia",
                "genus": list(entry["genus"]),
                "differentiae": [{"relation": r, "filler": f}
                                 for (r, f) in entry["differentiae"]],
            }
            return self._answer(value, prov, lic)
        # DEFINE-MATCH: a definitive true/false is licensed because a
        # logicalDefinition is a CLOSED, complete object about its definiendum
        # (memo §2.2, ASM-DEF-2) — unlike the CWA world-layer absence rule.
        equal = (cand_canon["genus"] == entry["genus"]
                 and cand_canon["differentiae"] == entry["differentiae"])
        return self._answer(bool(equal), prov, lic)

    def _layer_license(self, rel):
        refs = []
        refs.extend(self.functional.get(rel, []))
        if rel in self.inverse_of:
            refs.append(self.inverse_of[rel][1])
        for other, (partner, cref) in sorted(self.inverse_of.items()):
            if partner == rel:
                refs.append(cref)
        if rel in self.range_of:
            refs.append(self.range_of[rel][1])
        if rel in self.domain_of:
            refs.append(self.domain_of[rel][1])
        for _s, c, cref in self.cardinality:
            if c["path"] == rel:
                refs.append(cref)
        return refs or ["asserted"]

    def _unique_license(self, rel, direction, subject):
        """Uniqueness must be axiom-licensed (the maintainer's worked case:
        mother is functional cardinality-1, hence mother(Elvis) is a
        unique-answer lookup — architecture-ladder.md §5)."""
        refs = []
        if direction == "forward" and rel in self.functional:
            refs.extend(self.functional[rel])
        for subj_class, c, cref in self.cardinality:
            if c["path"] == rel and c["direction"] == direction \
                    and c.get("max") == 1 and c.get("min", 0) >= 1 \
                    and "qualifier" not in c \
                    and subj_class in self.classes.get(subject, {}):
                refs.append(cref)
        return refs


# ---------------------------------------------------------------- loading


def load_corpora(root):
    """Load data/axioms-v0 (stratum 3) + data/world-v0 (stratum 4)."""
    axiom_dir = os.path.join(root, "data", "axioms-v0")
    axioms = []
    for name in sorted(os.listdir(axiom_dir)):
        if not name.endswith(".json") or name == "manifest.json":
            continue
        with open(os.path.join(axiom_dir, name), "r", encoding="utf-8") as f:
            axioms.append(("axioms-v0/%s" % name, json.load(f)))
    world = []
    with open(os.path.join(root, "data", "world-v0", "world.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                world.append(json.loads(line))
    return axioms, world


def load_mint_bridge(root):
    """The onto-obo mint bridge {urn:onto-obo:<id>: urn:kot:<urn>}
    (data/onto-obo/minted-urns.jsonl). READ-ONLY — the define-op never mints."""
    bridge = {}
    path = os.path.join(root, "data", "onto-obo", "minted-urns.jsonl")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                bridge[r["id"]] = r["urn"]
    return bridge


def load_obo_shard(root, shard):
    """Load one onto-obo shard (jsonl) as a list of records. READ-ONLY."""
    recs = []
    path = os.path.join(root, "data", "onto-obo", shard)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                recs.append(json.loads(line))
    return recs


def build_engine(root):
    axioms, world = load_corpora(root)
    # Lazily load the define-op substrate ONLY when a `definitional` endorsement
    # references it — with no endorsement present, behaviour is byte-identical to
    # the four-op engine (no onto-obo read).
    needed_shards = set()
    for _ref, rec in axioms:
        cs = rec.get("constraints") if isinstance(rec, dict) else None
        for c in (cs if isinstance(cs, list) else []):
            if isinstance(c, dict) and c.get("kind") == "definitional":
                src = c.get("source")
                if isinstance(src, dict) and src.get("shard"):
                    needed_shards.add(src["shard"])
    obo_shards, mint_bridge = None, None
    if needed_shards:
        mint_bridge = load_mint_bridge(root)
        obo_shards = {s: load_obo_shard(root, s) for s in sorted(needed_shards)}
    return Engine(axioms, world, obo_shards=obo_shards, mint_bridge=mint_bridge)
