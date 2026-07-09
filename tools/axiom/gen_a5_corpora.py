#!/usr/bin/env python3
"""gen_a5_corpora — deterministic builder of the A5 code-vertical corpora:

  data/code-axioms-v0/   stratum-3 kot-axiom/1 sidecar records (code axiom layer)
  data/code-world-v0/    stratum-4 kot-world/1 records EXTRACTED from the pinned
                         code corpus (data/code-corpus-v0/src) + planted
                         instrument-validity violations (flagged by provenance)
  data/a5-eval/          the pre-registered eval query set (kot-query-code/1)

Spec: docs/design-a5-code-worldlayer-oracle.md. Registry id `a5`
(idea-code-worldlayer-cpg, docs/next/idea-registry.md NOW-list item 5).

EXTRACTOR (kot-code-extract/1, this file, CODE-based — no LLM anywhere):
CPython stdlib `ast` over the pinned snapshot corpus. Fully deterministic and
RNG-FREE: file order is sorted, every collection is sorted before emission,
slug collisions fail closed. The registered seed 0 is a placeholder for the
pinned extractor constants (no stochastic step exists).

Extraction semantics (each mirrors the minted kot-code-construct/1 definition
it instantiates — data/code-v0/concepts/):
  python-module    one src/*.py file (ast.Module)
  python-function  ast.FunctionDef / ast.AsyncFunctionDef (named; lambdas never)
  python-class     ast.ClassDef
  code-defines     defining scope -> construct, IMMEDIATE child statement of the
                   scope body only (a def nested under if/try gets class +
                   containment records but NO defines edge — counted, not silent)
  code-imports     module -> corpus-internal module (ast.Import/ImportFrom
                   anywhere in the file; extra-corpus imports assert nothing)
  code-calls       caller function -> callee function, EXACT-name resolution
                   only: bare name bound by a same-module top-level function, a
                   from-import of a corpus module's top-level function, or
                   attribute access through an imported corpus module's alias.
                   Nested named scopes are excluded from a caller's call walk
                   (their calls belong to them); class-body and module-level
                   calls are attributed to no caller; decorator expressions of
                   nested defs are excluded; unresolvable calls assert NOTHING.
  containment      kernel-v0 part-of (EXACT minted URN, reused — nothing new
                   minted): construct -> every enclosing named scope
                   (transitive lexical containment).

X3 TRAP (binding, restated): every construct -> concept mapping below is an
EXACT content-hash URN loaded from the minted-urns files by exact sourceId
match. No kernel-space nearest-neighbour, no similarity step, anywhere.

EXPECTED ANSWERS are computed from this generator's own construction tables,
NOT by calling the engine (tools/axiom/kot_code.py is never imported here) —
the engine is the system under test. Residual single-author circularity is
registered as ASM-0008; the cross-vendor audit is the check.
"""

import ast
import json
import os
import sys

EXTRACTOR_VERSION = "kot-code-extract/1"

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = "urn:kotw:v0:%s"

SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FUNC_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def load_minted(root, corpus, source_ids):
    """sourceId -> minted urn:kot: URN, by EXACT match only (X3 trap)."""
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
            fail("ERR_A5_MINT_LOOKUP", "sourceId %r not minted in %s" % (sid, corpus))
        out[sid] = table[sid]
    return out


def sanitise(name):
    """Deterministic, injective-on-Python-identifiers segment encoding:
    lowercase kept, A-Z lowered, digits kept, '_' -> '-'; anything else fails
    closed. Case-fold or join collisions are caught globally (fail-closed)."""
    out = []
    for ch in name:
        if ch.islower() or ch.isdigit():
            out.append(ch)
        elif ch.isupper():
            out.append(ch.lower())
        elif ch in ("_", "-"):
            out.append("-")
        else:
            fail("ERR_A5_SLUG", "unencodable character %r in name %r" % (ch, name))
    return "".join(out)


class Construct(object):
    def __init__(self, kind, entity, module, qual, lineno):
        self.kind = kind          # "module" | "function" | "class"
        self.entity = entity
        self.module = module
        self.qual = qual          # dotted qualname within module ("" for module)
        self.lineno = lineno
        self.definer = None       # entity of the IMMEDIATE defining scope (or None)
        self.ancestors = []       # enclosing named-scope entities, innermost first
        self.node = None          # the ast node (pass-2 call walk)


def extract(root):
    src_dir = os.path.join(root, "data", "code-corpus-v0", "src")
    files = sorted(f for f in os.listdir(src_dir) if f.endswith(".py"))
    if not files:
        fail("ERR_A5_CORPUS", "no .py files under data/code-corpus-v0/src")

    modules = {}              # modname -> Construct
    constructs = {}           # entity -> Construct
    slug_owner = {}           # entity -> qual (collision fail-closed)
    toplevel_funcs = {}       # modname -> {name: entity}
    alias_map = {}            # modname -> {alias: target modname}
    from_map = {}             # modname -> {bound name: (target modname, name)}
    import_edges = {}         # (src mod entity, dst mod entity) -> lineno
    non_immediate_defs = 0

    mod_names = [os.path.splitext(f)[0] for f in files]
    mod_set = set(mod_names)

    def claim(entity, qual):
        if entity in slug_owner:
            fail("ERR_A5_SLUG_COLLISION", "%s claimed by both %r and %r"
                 % (entity, slug_owner[entity], qual))
        slug_owner[entity] = qual

    trees = {}
    for fname in files:
        modname = os.path.splitext(fname)[0]
        with open(os.path.join(src_dir, fname), "r", encoding="utf-8") as f:
            trees[modname] = ast.parse(f.read(), filename=fname)
        entity = E % ("code-mod-%s" % sanitise(modname))
        claim(entity, modname)
        c = Construct("module", entity, modname, "", 1)
        modules[modname] = c
        constructs[entity] = c
        toplevel_funcs[modname] = {}
        alias_map[modname] = {}
        from_map[modname] = {}

    # ---- pass 1: scopes (classes/functions), defines, containment, imports
    for modname in mod_names:
        tree = trees[modname]
        mod_c = modules[modname]

        def visit_stmts(stmts, scope, immediate, path):
            # scope: innermost enclosing named-scope Construct;
            # immediate: True iff stmts is the direct body of `scope`.
            for node in stmts:
                if isinstance(node, SCOPE_NODES):
                    kind = "class" if isinstance(node, ast.ClassDef) else "function"
                    qual = ".".join(path + [node.name])
                    slug = "--".join(sanitise(s) for s in path + [node.name])
                    entity = E % ("code-%s-%s--%s"
                                  % ("cls" if kind == "class" else "fn",
                                     sanitise(modname), slug))
                    claim(entity, "%s:%s" % (modname, qual))
                    c = Construct(kind, entity, modname, qual, node.lineno)
                    anc = [scope]
                    while anc[-1].kind != "module":
                        anc.append(constructs[anc[-1].ancestors[0]])
                    c.ancestors = [a.entity for a in anc]
                    if immediate:
                        c.definer = scope.entity
                    else:
                        nonlocal_counter[0] += 1
                    c.node = node
                    constructs[entity] = c
                    if kind == "function" and scope.kind == "module" and immediate:
                        toplevel_funcs[modname][node.name] = entity
                    visit_stmts(node.body, c, True, path + [node.name])
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in mod_set:
                            bound = alias.asname or alias.name
                            alias_map[modname].setdefault(bound, alias.name)
                            key = (mod_c.entity, modules[alias.name].entity)
                            import_edges.setdefault(key, node.lineno)
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module in mod_set:
                        key = (mod_c.entity, modules[node.module].entity)
                        import_edges.setdefault(key, node.lineno)
                        for alias in node.names:
                            bound = alias.asname or alias.name
                            from_map[modname].setdefault(bound, (node.module, alias.name))
                else:
                    # recurse into compound statements: defs found there are
                    # NOT immediate children of the enclosing scope body
                    for field in ("body", "orelse", "finalbody", "handlers"):
                        sub = getattr(node, field, None)
                        if isinstance(sub, list):
                            inner = []
                            for x in sub:
                                if isinstance(x, ast.excepthandler):
                                    inner.extend(x.body)
                                elif isinstance(x, ast.stmt):
                                    inner.append(x)
                            if inner:
                                visit_stmts(inner, scope, False, path)

        nonlocal_counter = [0]
        visit_stmts(tree.body, mod_c, True, [])
        non_immediate_defs += nonlocal_counter[0]

    # ---- pass 2: calls (exact-name resolution; tables complete now)
    call_edges = {}  # (caller entity, callee entity) -> lineno

    def resolve_call(modname, func_expr):
        if isinstance(func_expr, ast.Name):
            n = func_expr.id
            if n in from_map[modname]:
                tmod, tname = from_map[modname][n]
                return toplevel_funcs[tmod].get(tname)
            return toplevel_funcs[modname].get(n)
        if isinstance(func_expr, ast.Attribute) and isinstance(func_expr.value, ast.Name):
            v = func_expr.value.id
            if v in alias_map[modname]:
                return toplevel_funcs[alias_map[modname][v]].get(func_expr.attr)
        return None

    def calls_in(fn_node):
        """ast.Call nodes in fn_node's body, excluding nested named scopes
        (incl. their decorators); lambdas and comprehensions are walked."""
        out = []
        stack = list(fn_node.body)
        while stack:
            node = stack.pop()
            if isinstance(node, SCOPE_NODES):
                continue
            if isinstance(node, ast.Call):
                out.append(node)
            for child in ast.iter_child_nodes(node):
                stack.append(child)
        return out

    for entity in sorted(constructs):
        c = constructs[entity]
        if c.kind != "function":
            continue
        for call in calls_in(c.node):
            callee = resolve_call(c.module, call.func)
            if callee is not None:
                key = (c.entity, callee)
                if key not in call_edges or call.lineno < call_edges[key]:
                    call_edges[key] = call.lineno

    return {"files": files, "modules": modules, "constructs": constructs,
            "toplevel_funcs": toplevel_funcs, "import_edges": import_edges,
            "call_edges": call_edges, "non_immediate_defs": non_immediate_defs}


# ------------------------------------------------------------------ emission

PLANTED = {
    "both": E % "code-planted-both",
    "scope_a": E % "code-planted-scope-a",
    "scope_b": E % "code-planted-scope-b",
    "fn_x": E % "code-planted-fn-x",
    "mod_i": E % "code-planted-mod-i",
    "fn_t": E % "code-planted-fn-t",
}
PLANT_SRC = "planted-violation/1 instrument-validity plant (not extracted)"


def world_records(x, urns):
    """Ordered kot-world/1 records: extracted (sorted) then planted (flagged)."""
    recs = []

    def add(kind, **kw):
        recs.append(dict(schema="kot-world/1", kind=kind, **kw))

    concept_of = {"module": urns["python-module"], "function": urns["python-function"],
                  "class": urns["python-class"]}
    cs = x["constructs"]
    for entity in sorted(cs):
        c = cs[entity]
        add("class", entity=entity, concept=concept_of[c.kind],
            provenance={"source": "%s src/%s.py:%d" % (EXTRACTOR_VERSION, c.module, c.lineno)})
    for entity in sorted(cs):
        c = cs[entity]
        if c.definer is not None:
            add("relation", relation=urns["code-defines"], subject=c.definer, object=entity,
                provenance={"source": "%s src/%s.py:%d" % (EXTRACTOR_VERSION, c.module, c.lineno)})
    for entity in sorted(cs):
        c = cs[entity]
        for anc in c.ancestors:
            add("relation", relation=urns["part-of"], subject=entity, object=anc,
                provenance={"source": "%s src/%s.py:%d" % (EXTRACTOR_VERSION, c.module, c.lineno)})
    for (s, o) in sorted(x["import_edges"]):
        add("relation", relation=urns["code-imports"], subject=s, object=o,
            provenance={"source": "%s src/%s.py:%d"
                        % (EXTRACTOR_VERSION, cs[s].module, x["import_edges"][(s, o)])})
    for (s, o) in sorted(x["call_edges"]):
        add("relation", relation=urns["code-calls"], subject=s, object=o,
            provenance={"source": "%s src/%s.py:%d"
                        % (EXTRACTOR_VERSION, cs[s].module, x["call_edges"][(s, o)])})
    n_extracted = len(recs)

    # planted instrument-validity violations (3, pre-declared):
    #   VIOLATION_DISJOINT   planted-both asserted python-function AND python-module
    #   VIOLATION_CARD_MAX   planted-fn-x has TWO code-defines definers (max 1)
    #   VIOLATION_RANGE      planted-mod-i imports planted-fn-t (a python-function,
    #                        disjoint with the declared range python-module)
    p = {"source": PLANT_SRC}
    add("class", entity=PLANTED["both"], concept=urns["python-function"], provenance=p)
    add("class", entity=PLANTED["both"], concept=urns["python-module"], provenance=p)
    add("class", entity=PLANTED["scope_a"], concept=urns["python-module"], provenance=p)
    add("class", entity=PLANTED["scope_b"], concept=urns["python-module"], provenance=p)
    add("class", entity=PLANTED["fn_x"], concept=urns["python-function"], provenance=p)
    add("class", entity=PLANTED["mod_i"], concept=urns["python-module"], provenance=p)
    add("class", entity=PLANTED["fn_t"], concept=urns["python-function"], provenance=p)
    add("relation", relation=urns["code-defines"], subject=PLANTED["scope_a"],
        object=PLANTED["fn_x"], provenance=p)
    add("relation", relation=urns["code-defines"], subject=PLANTED["scope_b"],
        object=PLANTED["fn_x"], provenance=p)
    add("relation", relation=urns["code-imports"], subject=PLANTED["mod_i"],
        object=PLANTED["fn_t"], provenance=p)

    for i, rec in enumerate(recs):
        rec["id"] = "cw%05d" % (i + 1)
    return recs, n_extracted


def axiom_records(urns):
    """Stratum 3: the endorsed code axiom layer (5 records)."""
    return {
        "class-python-function.json": {
            "schema": "kot-axiom/1", "subject": urns["python-function"],
            "constraints": [
                {"kind": "disjointWith", "target": urns["python-module"]},
                {"kind": "disjointWith", "target": urns["python-class"]},
                {"kind": "cardinality", "path": urns["code-defines"],
                 "direction": "inverse", "min": 1, "max": 1},
            ]},
        "class-python-class.json": {
            "schema": "kot-axiom/1", "subject": urns["python-class"],
            "constraints": [
                {"kind": "disjointWith", "target": urns["python-module"]},
                {"kind": "cardinality", "path": urns["code-defines"],
                 "direction": "inverse", "min": 1, "max": 1},
            ]},
        "rel-code-calls.json": {
            "schema": "kot-axiom/1", "subject": urns["code-calls"],
            "constraints": [
                {"kind": "domain", "target": urns["python-function"]},
                {"kind": "range", "target": urns["python-function"]},
            ]},
        "rel-code-imports.json": {
            "schema": "kot-axiom/1", "subject": urns["code-imports"],
            "constraints": [
                {"kind": "domain", "target": urns["python-module"]},
                {"kind": "range", "target": urns["python-module"]},
            ]},
        "rel-part-of.json": {
            "schema": "kot-axiom/1", "subject": urns["part-of"],
            "constraints": [{"kind": "inverseOf", "target": urns["has-part"]}]},
    }


# ------------------------------------------------------------------ eval set

def build_eval(x, urns, control_urns):
    cs = x["constructs"]
    concept_of = {"module": urns["python-module"], "function": urns["python-function"],
                  "class": urns["python-class"]}

    callers = {}
    callees = {}
    for (s, o) in x["call_edges"]:
        callees.setdefault(s, set()).add(o)
        callers.setdefault(o, set()).add(s)
    imports_of = {}
    imported_by = {}
    for (s, o) in x["import_edges"]:
        imports_of.setdefault(s, set()).add(o)
        imported_by.setdefault(o, set()).add(s)
    contains = {}
    for entity in cs:
        for anc in cs[entity].ancestors:
            contains.setdefault(anc, set()).add(entity)

    covered, control = [], []

    def cov(family, query, value):
        covered.append({"class": "covered", "family": family, "query": query,
                        "expected": {"kind": "answer", "value": value}})

    def ctl(family, query, code):
        control.append({"class": "control", "family": family, "query": query,
                        "expected": {"kind": "refuse", "code": code}})

    fns = sorted(e for e in cs if cs[e].kind == "function")
    clss = sorted(e for e in cs if cs[e].kind == "class")
    mods = sorted(e for e in cs if cs[e].kind == "module")

    # ---- covered (answers derivable from the construction tables)
    for f in fns:
        if f in callers:
            cov("callers-of", {"op": "callers-of", "of": f}, sorted(callers[f]))
        if f in callees:
            cov("callees-of", {"op": "callees-of", "of": f}, sorted(callees[f]))
    for e in fns + clss:
        if cs[e].definer is not None:
            cov("where-defined", {"op": "where-defined", "of": e}, cs[e].definer)
    for m in mods:
        if m in imports_of:
            cov("imports-of", {"op": "imports-of", "of": m}, sorted(imports_of[m]))
        if m in imported_by:
            cov("imported-by", {"op": "imported-by", "of": m}, sorted(imported_by[m]))
    for e in sorted(contains):
        cov("contains", {"op": "contains", "of": e}, sorted(contains[e]))
    for e in fns + clss:
        cov("contained-in", {"op": "contained-in", "of": e}, sorted(cs[e].ancestors))
    for e in sorted(cs):
        cov("instance-true", {"op": "instance-of", "entity": e,
                              "concept": concept_of[cs[e].kind]}, True)
    for m in mods:
        cov("instance-false-disjoint", {"op": "instance-of", "entity": m,
                                        "concept": urns["python-function"]}, False)
    for c in clss:
        cov("instance-false-disjoint", {"op": "instance-of", "entity": c,
                                        "concept": urns["python-module"]}, False)

    # ---- control: licensed-but-no-record (deterministic caps: first-K sorted)
    for f in [f for f in fns if f not in callers][:15]:
        ctl("no-record-callers", {"op": "callers-of", "of": f}, "ERR_NO_RECORD")
    for f in [f for f in fns if f not in callees][:15]:
        ctl("no-record-callees", {"op": "callees-of", "of": f}, "ERR_NO_RECORD")
    for m in [m for m in mods if m not in imports_of][:10]:
        ctl("no-record-imports", {"op": "imports-of", "of": m}, "ERR_NO_RECORD")
    for m in [m for m in mods if m not in imported_by][:10]:
        ctl("no-record-imported-by", {"op": "imported-by", "of": m}, "ERR_NO_RECORD")
    for f in [f for f in fns if f not in contains][:10]:
        ctl("no-record-contains", {"op": "contains", "of": f}, "ERR_NO_RECORD")

    # unknown entity (well-formed, never asserted)
    for i in range(6):
        ctl("unknown-entity", {"op": "callers-of", "of": E % ("code-fn-ghost-%d" % i)},
            "ERR_UNKNOWN_ENTITY")
        ctl("unknown-entity", {"op": "where-defined", "of": E % ("code-fn-ghost-%d" % i)},
            "ERR_UNKNOWN_ENTITY")
        ctl("unknown-entity", {"op": "imports-of", "of": E % ("code-mod-ghost-%d" % i)},
            "ERR_UNKNOWN_ENTITY")
        ctl("unknown-entity", {"op": "instance-of", "entity": E % ("code-cls-ghost-%d" % i),
                               "concept": urns["python-class"]}, "ERR_UNKNOWN_ENTITY")

    # unlicensed unique: where-defined on modules (no cardinality license there)
    for m in mods:
        ctl("unlicensed-unique", {"op": "where-defined", "of": m}, "ERR_UNLICENSED_UNIQUE")

    # out-of-scope concept: minted kernel concepts NOT in the code axiom layer
    for i, m in enumerate(mods[:3]):
        ctl("out-of-scope-concept", {"op": "instance-of", "entity": m,
                                     "concept": control_urns["bookmark"]}, "ERR_TERM_UNLICENSED")
    for i, f in enumerate(fns[:3]):
        ctl("out-of-scope-concept", {"op": "instance-of", "entity": f,
                                     "concept": control_urns["friend"]}, "ERR_TERM_UNLICENSED")

    # planted-conflict queries (store violations surface, never resolve)
    ctl("conflict", {"op": "instance-of", "entity": PLANTED["both"],
                     "concept": urns["python-function"]}, "ERR_CONFLICT")
    ctl("conflict", {"op": "instance-of", "entity": PLANTED["both"],
                     "concept": urns["python-module"]}, "ERR_CONFLICT")
    ctl("conflict", {"op": "where-defined", "of": PLANTED["fn_x"]}, "ERR_CONFLICT")
    ctl("conflict", {"op": "imports-of", "of": PLANTED["mod_i"]}, "ERR_CONFLICT")
    ctl("conflict", {"op": "imported-by", "of": PLANTED["fn_t"]}, "ERR_CONFLICT")

    # malformed / out-of-scope ops (the closed-grammar fail-closed boundary):
    # semantic/static-analysis asks the grammar deliberately does NOT cover
    some_fn = fns[0]
    for q in [
        {"op": "type-of", "of": some_fn},
        {"op": "data-flow-of", "of": some_fn},
        {"op": "docstring-of", "of": some_fn},
        {"op": "what-does-this-function-do", "of": some_fn},
        {"op": "callers"},
        {"op": "callers-of"},
        {"op": "callers-of", "of": some_fn, "extra": 1},
        {"op": "callers-of", "of": "not-a-urn"},
        {"op": "callers-of", "of": 42},
        {"op": "where-defined", "entity": some_fn},
        {"op": "instance-of", "entity": some_fn},
        {"op": "instance-of", "entity": some_fn, "concept": "urn:kot:UPPER"},
        {"op": "contains"},
        {"no-op": True},
        {"op": None},
        {"op": "lookup", "rel": urns["code-calls"], "direction": "forward",
         "subject": some_fn},
    ]:
        ctl("malformed", q, "ERR_BAD_QUERY")

    queries = covered + control
    for i, q in enumerate(queries):
        q["qid"] = "a%04d" % (i + 1)
    return queries


def main():
    root = ROOT
    urns = load_minted(root, "code-v0", ["python-module", "python-function", "python-class",
                                         "code-calls", "code-defines", "code-imports"])
    kernel = load_minted(root, "kernel-v0", ["part-of", "has-part", "bookmark", "friend"])
    urns["part-of"] = kernel["part-of"]
    urns["has-part"] = kernel["has-part"]
    control_urns = {"bookmark": kernel["bookmark"], "friend": kernel["friend"]}

    x = extract(root)
    world, n_extracted = world_records(x, urns)
    axioms = axiom_records(urns)
    queries = build_eval(x, urns, control_urns)

    # ---- write code-axioms-v0
    ax_dir = os.path.join(root, "data", "code-axioms-v0")
    os.makedirs(ax_dir, exist_ok=True)
    for name, rec in sorted(axioms.items()):
        with open(os.path.join(ax_dir, name), "w", encoding="utf-8") as f:
            f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    with open(os.path.join(ax_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "corpus": "code-axioms-v0", "schema": "kot-axiom/1", "stratum": 3,
            "recordCount": len(axioms),
            "endorsement": "research-grade, agent-authored; NOT federation-endorsed",
            "grammar": "docs/design-constraint-layer.md section 3.3",
            "spec": "docs/design-a5-code-worldlayer-oracle.md",
        }, indent=1, sort_keys=True) + "\n")

    # ---- write code-world-v0
    w_dir = os.path.join(root, "data", "code-world-v0")
    os.makedirs(w_dir, exist_ok=True)
    with open(os.path.join(w_dir, "world.jsonl"), "w", encoding="utf-8") as f:
        for rec in world:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    n_entities = len(set(
        [r["entity"] for r in world if r["kind"] == "class"] +
        [r[k] for r in world if r["kind"] == "relation" for k in ("subject", "object")]))
    with open(os.path.join(w_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "corpus": "code-world-v0", "schema": "kot-world/1", "stratum": 4,
            "extractor": EXTRACTOR_VERSION,
            "extractorScript": "tools/axiom/gen_a5_corpora.py",
            "sourceCorpus": "data/code-corpus-v0 (pinned snapshot; kot-corpus-hash/1)",
            "recordCount": len(world), "extractedRecordCount": n_extracted,
            "plantedRecordCount": len(world) - n_extracted,
            "plantedViolations": {"VIOLATION_DISJOINT": 1, "VIOLATION_CARD_MAX": 1,
                                  "VIOLATION_RANGE": 1},
            "entityCount": n_entities,
            "nonImmediateDefsWithoutDefinesEdge": x["non_immediate_defs"],
            "spec": "docs/design-a5-code-worldlayer-oracle.md",
        }, indent=1, sort_keys=True) + "\n")

    # ---- write a5-eval
    e_dir = os.path.join(root, "data", "a5-eval")
    os.makedirs(e_dir, exist_ok=True)
    with open(os.path.join(e_dir, "queries.jsonl"), "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps(q, sort_keys=True) + "\n")
    strata = {}
    for q in queries:
        strata[q["family"]] = strata.get(q["family"], 0) + 1
    n_cov = sum(1 for q in queries if q["class"] == "covered")
    n_ctl = len(queries) - n_cov
    with open(os.path.join(e_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "corpus": "a5-eval", "schema": "kot-query-code/1-eval",
            "spec": "docs/design-a5-code-worldlayer-oracle.md",
            "n_covered": n_cov, "n_control": n_ctl,
            "strata": dict(sorted(strata.items())),
        }, indent=1, sort_keys=True) + "\n")

    print(json.dumps({
        "extractor": EXTRACTOR_VERSION,
        "files": len(x["files"]),
        "constructs": {"modules": sum(1 for c in x["constructs"].values() if c.kind == "module"),
                       "functions": sum(1 for c in x["constructs"].values() if c.kind == "function"),
                       "classes": sum(1 for c in x["constructs"].values() if c.kind == "class")},
        "edges": {"defines": sum(1 for c in x["constructs"].values() if c.definer),
                  "part_of": sum(len(c.ancestors) for c in x["constructs"].values()),
                  "imports": len(x["import_edges"]), "calls": len(x["call_edges"])},
        "non_immediate_defs": x["non_immediate_defs"],
        "world_records": len(world), "entities": n_entities,
        "eval": {"covered": n_cov, "control": n_ctl},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
