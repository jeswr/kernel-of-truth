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
                    "inverseOf", "functional", "cardinality")
IMPLEMENTED_KINDS = ("disjointWith", "domain", "range", "inverseOf",
                     "functional", "cardinality")
DIRECTIONS = ("forward", "inverse")

QUERY_OPS = ("unique", "lookup", "count", "instance")

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

    def __init__(self, axiom_records, world_records):
        # axiom_records: list of (ref, record); world_records: list of record.
        self.axioms = {}            # ref -> record
        self.functional = {}        # rel -> [axiom refs] (forward direction)
        self.inverse_of = {}        # rel -> (partner rel, axiom ref)
        self.disjoint = {}          # concept -> {other concept: axiom ref}
        self.range_of = {}          # rel -> (target concept, axiom ref)
        self.domain_of = {}         # rel -> (target concept, axiom ref)
        self.cardinality = []       # (subject concept, constraint dict, axiom ref)
        self.licensed_rels = set()  # relations admitted to the axiom layer
        self.licensed_classes = set()

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
        if op == "instance":
            wanted = {"op", "entity", "concept"}
        elif op == "count":
            wanted = {"op", "rel", "direction", "subject", "qualifier"}
        else:
            wanted = {"op", "rel", "direction", "subject"}
        if set(q) - wanted:
            return self._refuse("ERR_BAD_QUERY", "unexpected fields %s" % sorted(set(q) - wanted))

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


def build_engine(root):
    axioms, world = load_corpora(root)
    return Engine(axioms, world)
