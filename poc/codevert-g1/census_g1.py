#!/usr/bin/env python3
"""CODEVERT G0 — extractor-INDEPENDENT syntactic query census generator.

Per docs/next/design/CODEVERT.md §7-G1 [PROPOSED-ASM: ASM-1030]:
  - ONLY input is raw repo bytes (the pinned working trees).
  - Purely SYNTACTIC enumeration: every def/class name, every module-/class-
    level assignment name, every attribute-access name, every import-statement
    target, every module file. NO name resolution, NO symtable, NO import
    resolver, NO access to any extractor output. `ast.parse` is used strictly
    as a tokeniser/parser (syntax only) [STIPULATED: PROPOSED-ASM ASM-1052 —
    ast.parse counts as syntactic; it performs no binding or resolution].
  - Content-hashed (this file) and seed-pinned; frozen BEFORE the extractor
    runs on these repos (enforced by run ordering, recorded in
    results/freeze-manifest.json).

Query universes instantiated per family (8 families of the measured
kot-query-code/1 grammar, CODEVERT §1/§2):
  forward  : callees-of(f), imports-of(m), contains(s), contained-in(x)
  inverse/exhaustive : callers-of(f), imported-by(m), where-defined(n),
                       instance-of(C)
Targets are identified purely syntactically as (relpath, qualpath|name);
whether the extractor can even locate the target is part of what kappa_q^indep
measures (anti-circularity).

Seed: 20260711 (sampling of the per-cell latency/adjudication sample only;
kappa is computed over the FULL universes downstream).
"""
import ast, hashlib, io, json, os, random, sys, tokenize

SEED = 20260716  # G1 seed, pinned in DESIGN-PIN.md sect 3
SAMPLE_PER_CELL = 25  # per family x repo, for latency/adjudication sampling

TEST_PATH_MARKERS = ("/test/", "/tests/", "/docs/")


def is_test_path(rel):
    p = "/" + rel.replace(os.sep, "/")
    base = os.path.basename(rel)
    return (any(m in p for m in TEST_PATH_MARKERS)
            or base.startswith("test_") or base.endswith("_test.py")
            or base in ("conftest.py", "setup.py"))


def iter_py_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                yield os.path.relpath(os.path.join(dirpath, fn), root)


class SyntacticVisitor(ast.NodeVisitor):
    """Collects purely syntactic facts; no resolution of any kind."""

    def __init__(self, relpath):
        self.rel = relpath
        self.stack = []          # lexical qualpath, syntactic only
        self.defs = []           # (qualpath, name, kind, lineno)
        self.assigns = []        # (scope_qualpath, name, lineno) module/class level
        self.attr_names = {}     # name -> count (Load-context attribute access)
        self.imports = []        # (kind, target, member, lineno)
        self.scope_kind = ["module"]

    def _q(self, name):
        return ".".join(self.stack + [name]) if self.stack else name

    def visit_FunctionDef(self, node):
        self._def(node, "function")

    def visit_AsyncFunctionDef(self, node):
        self._def(node, "function")

    def visit_ClassDef(self, node):
        self._def(node, "class")

    def _def(self, node, kind):
        self.defs.append((self._q(node.name), node.name, kind, node.lineno))
        self.stack.append(node.name)
        self.scope_kind.append(kind)
        self.generic_visit(node)
        self.scope_kind.pop()
        self.stack.pop()

    def _bind_targets(self, tgt, lineno):
        if isinstance(tgt, ast.Name):
            self.assigns.append((".".join(self.stack), tgt.id, lineno))
        elif isinstance(tgt, (ast.Tuple, ast.List)):
            for e in tgt.elts:
                self._bind_targets(e, lineno)

    def visit_Assign(self, node):
        if self.scope_kind[-1] in ("module", "class"):
            for t in node.targets:
                self._bind_targets(t, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if self.scope_kind[-1] in ("module", "class"):
            self._bind_targets(node.target, node.lineno)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if self.scope_kind[-1] in ("module", "class"):
            self._bind_targets(node.target, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            self.attr_names[node.attr] = self.attr_names.get(node.attr, 0) + 1
        self.generic_visit(node)

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append(("import", a.name, None, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = ("." * node.level) + (node.module or "")
        for a in node.names:
            self.imports.append(("from", mod, a.name, node.lineno))
        self.generic_visit(node)


def census_repo(root):
    modules, parse_failures = [], []
    per_file = {}
    for rel in iter_py_files(root):
        modules.append(rel)
        try:
            src = open(os.path.join(root, rel), "rb").read()
            tree = ast.parse(src, filename=rel)
        except (SyntaxError, ValueError):
            parse_failures.append(rel)
            continue
        v = SyntacticVisitor(rel)
        v.visit(tree)
        per_file[rel] = {
            "defs": v.defs, "assigns": v.assigns,
            "attr_names": v.attr_names, "imports": v.imports,
        }
    return modules, parse_failures, per_file


def build_universes(repo_name, modules, parse_failures, per_file):
    fn_defs, cls_defs, all_defs = [], [], []
    name_sites = {}   # name -> [(rel, scope, lineno, how)]
    for rel in sorted(per_file):
        pf = per_file[rel]
        for q, name, kind, ln in pf["defs"]:
            e = {"file": rel, "qual": q, "name": name, "line": ln}
            all_defs.append(dict(e, kind=kind))
            (fn_defs if kind == "function" else cls_defs).append(e)
            name_sites.setdefault(name, []).append((rel, q, ln, kind))
        for scope, name, ln in pf["assigns"]:
            name_sites.setdefault(name, []).append((rel, scope, ln, "assign"))

    universes = {
        "callers_of":   [{"file": d["file"], "qual": d["qual"]} for d in fn_defs],
        "callees_of":   [{"file": d["file"], "qual": d["qual"]} for d in fn_defs],
        "imports_of":   [{"file": m} for m in modules],
        "imported_by":  [{"file": m} for m in modules],
        "contains":     ([{"file": m, "qual": None} for m in modules]
                         + [{"file": d["file"], "qual": d["qual"]} for d in cls_defs]),
        "contained_in": [{"file": d["file"], "qual": d["qual"]}
                         for d in all_defs],
        "where_defined": [{"name": n} for n in sorted(name_sites)],
        "instance_of":  [{"file": d["file"], "qual": d["qual"]} for d in cls_defs],
    }
    # identifier-collision census (extractor-independent): definition sites per
    # name, and attribute-access name pressure against def-name collisions.
    attr_counts = {}
    for pf in per_file.values():
        for n, c in pf["attr_names"].items():
            attr_counts[n] = attr_counts.get(n, 0) + c
    collisions = {n: len(s) for n, s in name_sites.items() if len(s) > 1}
    return universes, {
        "def_name_sites": {n: len(s) for n, s in sorted(name_sites.items())},
        "collision_names": dict(sorted(collisions.items(),
                                       key=lambda kv: -kv[1])[:50]),
        "n_names": len(name_sites),
        "n_collision_names": len(collisions),
        "attr_access_distinct": len(attr_counts),
        "attr_access_total": sum(attr_counts.values()),
        "top_attr_names": dict(sorted(attr_counts.items(),
                                      key=lambda kv: -kv[1])[:25]),
    }


def main(corpus_dir, out_dir):
    rng = random.Random(SEED)
    lock = json.load(open(os.path.join(os.path.dirname(out_dir), "repos.lock.json")))
    result = {}
    for spec in lock["selected"]:
        name = spec["name"]
        root = os.path.join(corpus_dir, name)
        modules, failures, per_file = census_repo(root)
        universes, ident = build_universes(name, modules, failures, per_file)
        sample = {}
        for fam in sorted(universes):
            u = universes[fam]
            idx = list(range(len(u)))
            rng.shuffle(idx)
            sample[fam] = sorted(idx[:SAMPLE_PER_CELL])
        result[name] = {
            "sha": spec["sha"],
            "n_modules": len(modules),
            "modules": modules,
            "n_test_modules": sum(1 for m in modules if is_test_path(m)),
            "parse_failures": failures,
            "universe_sizes": {f: len(u) for f, u in sorted(universes.items())},
            "universes": universes,
            "identifier_census": ident,
            "sample_indices": sample,
        }
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "census-g1.json")
    with open(out, "w") as f:
        json.dump({"seed": SEED, "generator": "census_g1.py (census.py logic, G1 seed/paths)", "repos": result}, f,
                  sort_keys=True, indent=1)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(json.dumps({r: result[r]["universe_sizes"] for r in result}, indent=1))
    print("census.json sha256:", h)


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    main(os.path.join(base, "corpus"), os.path.join(base, "results"))
