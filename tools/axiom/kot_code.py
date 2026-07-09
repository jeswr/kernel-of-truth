#!/usr/bin/env python3
"""kot_code — the kot-query-code/1 layer: the A5 code-structure query grammar
over the UNCHANGED kot-axiom/1 v0 engine (tools/axiom/kot_axiom.py).

Design sources:
  docs/design-a5-code-worldlayer-oracle.md   the grammar, corpora, refusal
                                             semantics (the prereg anchor)
  docs/design-l3a-rules-engine-oracle.md     the core engine + kot-query/1 this
                                             layer desugars into (L3a, PASS)
  docs/next/idea-registry.md (A5)            idea-code-worldlayer-cpg

Eight named operators, each a pure deterministic DESUGARING to one core
kot-query/1 query answered by the L3a engine's index lookups — provenance and
axiom license flow through untouched; every refusal keeps the engine's named
ERR_* code; anything outside the closed grammar refuses ERR_BAD_QUERY
(fail-closed ABSTAIN — semantic asks like type-of / data-flow-of are
deliberately NOT in the grammar).

  callers-of    {op, of: fn}      -> lookup(code-calls,   inverse, fn)
  callees-of    {op, of: fn}      -> lookup(code-calls,   forward, fn)
  where-defined {op, of: c}       -> unique(code-defines, inverse, c)
  imports-of    {op, of: mod}     -> lookup(code-imports, forward, mod)
  imported-by   {op, of: mod}     -> lookup(code-imports, inverse, mod)
  contains      {op, of: scope}   -> lookup(part-of,      inverse, scope)
  contained-in  {op, of: c}       -> lookup(part-of,      forward, c)
  instance-of   {op, entity, concept} -> instance(entity, concept)

X3 TRAP (binding, restated): the op -> relation-concept table is built from
data/code-v0/minted-urns.jsonl + data/kernel-v0/minted-urns.jsonl by EXACT
sourceId match (content-hash identity). No nearest-neighbour, no similarity,
anywhere. House rules: zero runtime deps; no silent fallbacks; deterministic.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import kot_axiom  # noqa: E402

SCHEMA_QUERY = "kot-query-code/1"


def _minted(root, corpus, source_ids):
    """sourceId -> minted URN by EXACT match; fail closed on any miss."""
    path = os.path.join(root, "data", corpus, "minted-urns.jsonl")
    table = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                table[rec["sourceId"]] = rec["urn"]
    out = {}
    for sid in source_ids:
        if sid not in table:
            raise kot_axiom.KotAxiomError(
                "ERR_CODE_MINT_LOOKUP", "sourceId %r not minted in %s" % (sid, corpus))
        out[sid] = table[sid]
    return out


def load_code_corpora(root):
    """data/code-axioms-v0 (stratum 3) + data/code-world-v0 (stratum 4)."""
    ax_dir = os.path.join(root, "data", "code-axioms-v0")
    axioms = []
    for name in sorted(os.listdir(ax_dir)):
        if not name.endswith(".json") or name == "manifest.json":
            continue
        with open(os.path.join(ax_dir, name), "r", encoding="utf-8") as f:
            axioms.append(("code-axioms-v0/%s" % name, json.load(f)))
    world = []
    with open(os.path.join(root, "data", "code-world-v0", "world.jsonl"),
              "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                world.append(json.loads(line))
    return axioms, world


class CodeOracle(object):
    """The A5 code-structure oracle: kot-query-code/1 in, engine answers out."""

    def __init__(self, root):
        code = _minted(root, "code-v0", ["code-calls", "code-defines", "code-imports"])
        kernel = _minted(root, "kernel-v0", ["part-of"])
        # (core op, relation URN, direction) per named operator
        self.ops = {
            "callers-of":    ("lookup", code["code-calls"],   "inverse"),
            "callees-of":    ("lookup", code["code-calls"],   "forward"),
            "where-defined": ("unique", code["code-defines"], "inverse"),
            "imports-of":    ("lookup", code["code-imports"], "forward"),
            "imported-by":   ("lookup", code["code-imports"], "inverse"),
            "contains":      ("lookup", kernel["part-of"],    "inverse"),
            "contained-in":  ("lookup", kernel["part-of"],    "forward"),
        }
        axioms, world = load_code_corpora(root)
        self.engine = kot_axiom.Engine(axioms, world)

    def desugar(self, q):
        """kot-query-code/1 -> kot-query/1, or a refusal dict. Fail-closed:
        the grammar is CLOSED — unknown ops, missing/extra fields, and
        non-string arguments all refuse ERR_BAD_QUERY here; everything
        admitted is then subject to the core engine's full pre-registered
        validation order (licensing, entity, conflict, op license, records)."""
        if not isinstance(q, dict):
            return {"status": "refuse", "code": "ERR_BAD_QUERY",
                    "reason": "query is not an object"}
        op = q.get("op")
        if op == "instance-of":
            if set(q) != {"op", "entity", "concept"}:
                return {"status": "refuse", "code": "ERR_BAD_QUERY",
                        "reason": "instance-of takes exactly {op, entity, concept}"}
            if not isinstance(q["entity"], str) or not isinstance(q["concept"], str):
                return {"status": "refuse", "code": "ERR_BAD_QUERY",
                        "reason": "entity/concept must be strings"}
            return {"op": "instance", "entity": q["entity"], "concept": q["concept"]}
        if op in self.ops:
            if set(q) != {"op", "of"}:
                return {"status": "refuse", "code": "ERR_BAD_QUERY",
                        "reason": "%s takes exactly {op, of}" % op}
            if not isinstance(q["of"], str):
                return {"status": "refuse", "code": "ERR_BAD_QUERY",
                        "reason": "of must be a string entity URN"}
            core_op, rel, direction = self.ops[op]
            return {"op": core_op, "rel": rel, "direction": direction,
                    "subject": q["of"]}
        return {"status": "refuse", "code": "ERR_BAD_QUERY",
                "reason": "op %r is not in the closed kot-query-code/1 grammar" % (op,)}

    def query(self, q):
        core = self.desugar(q)
        if core.get("status") == "refuse":
            return core
        return self.engine.query(core)


def build_code_oracle(root):
    return CodeOracle(root)
