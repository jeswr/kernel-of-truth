#!/usr/bin/env python3
"""CODEVERT G0 — PY-STAT/1 extractor (enumerated static subset, fail-closed).

Implements the construct inventory in inventory.json (content-hashed) per
docs/next/design/CODEVERT.md §2.2 [PROPOSED-ASM: ASM-1031]. ast + symtable
only; pinned import resolver; 4-state facts (v0 emits proved/unknown only);
byte-span provenance; candidate-name sets on unknown edges ('*' =
unrestricted). Everything outside the inventory emits unknown fail-closed.
"""
import ast, builtins, os, symtable, sys

BUILTIN_NAMES = set(dir(builtins))


def _is_test_path(rel):
    p = "/" + rel.replace(os.sep, "/")
    base = os.path.basename(rel)
    return (any(m in p for m in ("/test/", "/tests/", "/docs/"))
            or base.startswith("test_") or base.endswith("_test.py")
            or base in ("conftest.py", "setup.py"))
EXEC_NAMES = {"exec", "eval", "compile"}
DYN_IMPORT_NAMES = {"__import__"}
ATTR_HOOKS = {"__getattr__", "__getattribute__", "__setattr__",
              "__init_subclass__", "__new__"}
ALLOWLIST = {"staticmethod", "classmethod", "abstractmethod",
             "abc.abstractmethod", "functools.wraps", "functools.lru_cache",
             "functools.cache", "typing.final", "final"}


class Edge:
    __slots__ = ("rel", "src", "dst", "status", "cand", "file", "span", "reason")

    def __init__(self, rel, src, dst, status, cand, file, span, reason):
        self.rel, self.src, self.dst = rel, src, dst
        self.status, self.cand = status, cand
        self.file, self.span, self.reason = file, span, reason

    def row(self):
        return (self.rel, self.src, self.dst, self.status, self.cand,
                self.file, self.span[0], self.span[1], self.reason)


def bind_names(t):
    """Simple-name assignment targets (incl. tuple/list unpacking, starred)."""
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, (ast.Tuple, ast.List)):
        out = []
        for e in t.elts:
            out.extend(bind_names(e))
        return out
    if isinstance(t, ast.Starred):
        return bind_names(t.value)
    return []


def dotted(expr):
    """Syntactic dotted name of a Name/Attribute chain, else None."""
    parts = []
    while isinstance(expr, ast.Attribute):
        parts.append(expr.attr)
        expr = expr.value
    if isinstance(expr, ast.Name):
        parts.append(expr.id)
        return ".".join(reversed(parts))
    return None


class ModuleInfo:
    def __init__(self, rel, dotted_name, pkg):
        self.rel = rel                  # relpath (module id)
        self.dotted = dotted_name       # dotted name via pinned resolver
        self.pkg = pkg                  # package dotted prefix for relative imports
        self.parsed = False
        self.tree = None
        self.src = b""
        self.line_off = [0]
        self.bindings = {}              # name -> [record]; record: dict
        self.defs = {}                  # qual -> {kind, line, span, decorated_bad, cond}
        self.classes = {}               # qual -> class info
        self.star_import = False
        self.exec_taint = False
        self.module_getattr = False     # PEP 562

    def span(self, node):
        try:
            a = self.line_off[node.lineno - 1] + node.col_offset
            b = self.line_off[node.end_lineno - 1] + node.end_col_offset
            return (a, b)
        except Exception:
            return (0, 0)


class Extractor:
    def __init__(self, root, repo):
        self.root, self.repo = root, repo
        self.modules = {}               # rel -> ModuleInfo
        self.by_dotted = {}             # dotted -> rel
        self.edges = []
        self.subclass_overrides = {}    # (ancestor_qualid, member) -> True
        self.stats = {"attr_load_untracked": 0, "name_load_untracked": 0,
                      "value_escape_edges": 0}

    # ---------- pinned import resolver [P1] ----------
    def _discover(self):
        exclude_tests = os.environ.get("G0_EXCLUDE_TESTS") == "1"
        files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(d for d in dirnames if d != ".git")
            for fn in sorted(filenames):
                if fn.endswith(".py"):
                    rel = os.path.relpath(os.path.join(dirpath, fn), self.root)
                    if exclude_tests and _is_test_path(rel):
                        continue
                    files.append(rel)
        # pinned resolver roots: repo root, src/, plus every directory that
        # holds .py files but is NOT a package (no __init__.py) — models the
        # sys.path insertion pytest/scripts perform for bare sibling imports
        # (probe-detected resolver-scope fix [ASM-1058])
        nonpkg = set()
        for rel in files:
            d = os.path.dirname(rel)
            if d and not os.path.exists(os.path.join(self.root, d, "__init__.py")):
                nonpkg.add(d.replace(os.sep, "/"))
        roots = ["", "src"] + sorted(nonpkg)
        for rel in files:
            parts = rel.replace(os.sep, "/").split("/")
            dot = None
            for r in roots:
                rp = [p for p in r.split("/") if p]
                if parts[:len(rp)] == rp:
                    body = parts[len(rp):]
                    ok = True
                    # every intermediate dir must be a package (has __init__.py)
                    for i in range(1, len(body)):
                        d = os.path.join(self.root, *(rp + body[:i]))
                        if not os.path.exists(os.path.join(d, "__init__.py")):
                            ok = False
                            break
                    if not ok:
                        continue
                    mods = body[:-1] + ([] if body[-1] == "__init__.py"
                                        else [body[-1][:-3]])
                    dot = ".".join(mods) if mods else None
                    break
            pkg = None
            if dot is not None:
                pkg = dot if rel.endswith("__init__.py") else ".".join(dot.split(".")[:-1])
            mi = ModuleInfo(rel, dot, pkg or "")
            self.modules[rel] = mi
            if dot and dot not in self.by_dotted:
                self.by_dotted[dot] = rel

    def resolve_import(self, mi, target, level=0):
        """Resolve a dotted import target to a repo rel-path or ('ext', name)."""
        if level:
            base = mi.pkg.split(".") if mi.pkg else []
            base = base[:len(base) - (level - 1)] if level - 1 else base
            if level - 1 > 0 and not base:
                return ("ext", target)
            name = ".".join([p for p in base if p] + ([target] if target else []))
        else:
            name = target
        if not name:
            return ("ext", target or "?")
        if name in self.by_dotted:
            return ("repo", self.by_dotted[name])
        # import a.b -> binds a; but the edge target is a.b; try prefixes too
        return ("ext", name)

    # ---------- pass 1: parse, bindings, defs, classes, taints ----------
    def parse_all(self):
        self._discover()
        for rel, mi in self.modules.items():
            path = os.path.join(self.root, rel)
            try:
                mi.src = open(path, "rb").read()
                off, tot = [0], 0
                for line in mi.src.splitlines(keepends=True):
                    tot += len(line)
                    off.append(tot)
                mi.line_off = off
                mi.tree = ast.parse(mi.src, filename=rel)
                mi.parsed = True
            except (SyntaxError, ValueError):
                for rel_kind in ("call", "import", "binding", "instantiate"):
                    self.edges.append(Edge(rel_kind, rel, None, "unknown", "*",
                                           rel, (0, 0), "MODULE_UNPARSED"))
                continue
            self._collect(mi)

    def _collect(self, mi):
        def add_bind(name, rec):
            mi.bindings.setdefault(name, []).append(rec)

        def walk(body, stack, scope_kind, cond):
            for node in body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qual = ".".join(stack + [node.name]) if stack else node.name
                    kind = "class" if isinstance(node, ast.ClassDef) else "function"
                    decs = [dotted(d.func) if isinstance(d, ast.Call) else dotted(d)
                            for d in node.decorator_list]
                    bad_dec = any(d is None or d not in ALLOWLIST for d in decs)
                    mi.defs[qual] = {"kind": kind, "line": node.lineno,
                                     "span": mi.span(node), "decorated_bad": bad_dec,
                                     "cond": cond, "node": node}
                    if scope_kind in ("module", "class"):
                        add_bind(node.name, {"kind": kind, "qual": qual,
                                             "cond": cond or scope_kind == "class",
                                             "top": scope_kind == "module" and not cond,
                                             "bad_dec": bad_dec, "line": node.lineno,
                                             "span": mi.span(node)})
                    if kind == "class":
                        members = {}
                        for c in node.body:
                            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                cdecs = [dotted(d.func) if isinstance(d, ast.Call) else dotted(d)
                                         for d in c.decorator_list]
                                members[c.name] = {
                                    "qual": qual + "." + c.name,
                                    "bad_dec": any(x is None or x not in ALLOWLIST
                                                   for x in cdecs)}
                        mi.classes[qual] = {
                            "bases": node.bases, "line": node.lineno,
                            "members": members,
                            "member_names": {c.name for c in node.body
                                             if isinstance(c, (ast.FunctionDef,
                                                               ast.AsyncFunctionDef,
                                                               ast.ClassDef))}
                                            | {t.id for c in node.body
                                               if isinstance(c, ast.Assign)
                                               for t in c.targets
                                               if isinstance(t, ast.Name)},
                            "kwds": bool(node.keywords),
                            "decorated": bool(node.decorator_list),
                            "multi": len(node.bases) > 1,
                            "hooks": bool({c.name for c in node.body
                                           if isinstance(c, (ast.FunctionDef,
                                                             ast.AsyncFunctionDef))}
                                          & ATTR_HOOKS)}
                        walk(node.body, stack + [node.name], "class", cond)
                    else:
                        if scope_kind == "module" and node.name == "__getattr__":
                            mi.module_getattr = True
                        walk(node.body, stack + [node.name], "function", cond)
                    continue
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    top = scope_kind == "module" and not cond
                    if isinstance(node, ast.Import):
                        for a in node.names:
                            res = self.resolve_import(mi, a.name)
                            bound = (a.asname or a.name.split(".")[0])
                            add_bind(bound, {"kind": "import", "target": res,
                                             "raw": a.name, "top": top,
                                             "cond": not top, "line": node.lineno,
                                             "span": mi.span(node),
                                             "sub": a.asname is None and "." in a.name})
                    else:
                        base = node.module or ""
                        for a in node.names:
                            if a.name == "*":
                                mi.star_import = True
                                res = self.resolve_import(mi, base, node.level)
                                self.edges.append(Edge("import", mi.rel,
                                                       None, "unknown",
                                                       res[1] if res[0] == "ext" else res[1],
                                                       mi.rel, mi.span(node), "IMPORT_STAR"))
                                continue
                            full = (base + "." + a.name) if base else a.name
                            res = self.resolve_import(mi, full, node.level)
                            if res[0] == "ext":
                                # member may be a symbol of a repo module
                                mres = self.resolve_import(mi, base, node.level)
                                res = ("member", mres, a.name)
                            add_bind(a.asname or a.name,
                                     {"kind": "from", "target": res, "raw": full,
                                      "top": top, "cond": not top,
                                      "line": node.lineno, "span": mi.span(node)})
                    # import EDGES emitted in pass 2 (need final resolver state)
                    walk_children(node, stack, scope_kind, cond)
                    continue
                if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    if scope_kind in ("module", "class"):
                        tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                        for t in tgts:
                            for nm in bind_names(t):
                                add_bind(nm, {"kind": "assign",
                                              "top": scope_kind == "module" and not cond,
                                              "cond": cond or scope_kind == "class",
                                              "scope": ".".join(stack),
                                              "line": node.lineno, "span": mi.span(node)})
                    walk_children(node, stack, scope_kind, cond)
                    continue
                if isinstance(node, ast.Global) and scope_kind == "function":
                    for nm in node.names:
                        add_bind(nm, {"kind": "assign", "top": False, "cond": True,
                                      "line": node.lineno, "span": mi.span(node)})
                    continue
                # compound statements -> conditional context
                walk_children(node, stack, scope_kind, cond=True
                              if isinstance(node, (ast.If, ast.Try, ast.While,
                                                   ast.For, ast.AsyncFor, ast.With,
                                                   ast.AsyncWith))
                              else cond)

        def walk_children(node, stack, scope_kind, cond):
            for fname, val in ast.iter_fields(node):
                if isinstance(val, list) and val:
                    if isinstance(val[0], ast.stmt):
                        walk(val, stack, scope_kind, cond)
                    elif isinstance(val[0], ast.excepthandler):
                        for h in val:
                            walk(h.body, stack, scope_kind, cond)

        walk(mi.tree.body, [], "module", False)
        # exec/eval/compile taint scan (over-approximate, fail-closed)
        for node in ast.walk(mi.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in EXEC_NAMES:
                mi.exec_taint = True
                break

    # ---------- module-level lookup helpers ----------
    def unique_top_binding(self, mi, name):
        recs = mi.bindings.get(name)
        if not recs or len(recs) != 1 or not recs[0].get("top"):
            return None
        return recs[0]

    def resolve_global_name(self, mi, name, depth=0):
        """Resolve module-scope name -> ('def'|'class', mi2, qual) |
        ('ext', dotted) | ('module', rel) | None (unknown)."""
        if depth > 4 or mi.star_import or mi.exec_taint:
            return None
        rec = self.unique_top_binding(mi, name)
        if rec is None:
            if name not in mi.bindings and name in BUILTIN_NAMES:
                return ("ext", "builtins." + name)
            return None
        if rec["kind"] in ("function", "class"):
            if rec.get("bad_dec"):
                return None
            return (rec["kind"], mi, rec["qual"])
        if rec["kind"] == "import":
            tgt = rec["target"]
            if rec.get("sub"):
                return None  # 'import a.b' binds a with submodule side effects
            if tgt[0] == "repo":
                return ("module", tgt[1])
            return ("extmodule", tgt[1])
        if rec["kind"] == "from":
            tgt = rec["target"]
            if tgt[0] == "repo":
                return ("module", tgt[1])  # from pkg import module_file
            if tgt[0] == "member":
                mres, member = tgt[1], tgt[2]
                if mres[0] == "repo":
                    mi2 = self.modules[mres[1]]
                    if not mi2.parsed:
                        return None
                    return self.resolve_member(mi2, member, depth + 1)
                return ("ext", mres[1] + "." + member)
            return ("ext", tgt[1])
        return None  # assign-bound or other

    def resolve_member(self, mi2, member, depth=0):
        if mi2.star_import or mi2.exec_taint or mi2.module_getattr:
            return None
        rec = self.unique_top_binding(mi2, member)
        if rec is None:
            return None
        if rec["kind"] in ("function", "class"):
            if rec.get("bad_dec"):
                return None
            return (rec["kind"], mi2, rec["qual"])
        return self.resolve_global_name(mi2, member, depth + 1)

    # ---------- class chain (single inheritance, fully analyzed) [P7/P8] ----------
    def class_chain(self, mi, qual, seen=None):
        """Return list of (mi, qual) ancestors incl. self, or None on hazard."""
        seen = seen or set()
        if (mi.rel, qual) in seen:
            return None
        seen.add((mi.rel, qual))
        ci = mi.classes.get(qual)
        if ci is None or ci["kwds"] or ci["decorated"] or ci["multi"] or ci["hooks"]:
            return None
        chain = [(mi, qual)]
        if not ci["bases"]:
            return chain
        base = ci["bases"][0]
        if isinstance(base, ast.Name) and base.id == "object":
            return chain
        d = dotted(base)
        if d is None:
            return None
        res = None
        if "." not in d:
            res = self.resolve_global_name(mi, d)
        else:
            head, tail = d.split(".", 1)
            g = self.resolve_global_name(mi, head)
            if g and g[0] == "module" and "." not in tail:
                mi2 = self.modules[g[1]]
                res = self.resolve_member(mi2, tail) if mi2.parsed else None
        if not res or res[0] != "class":
            return None
        rest = self.class_chain(res[1], res[2], seen)
        return None if rest is None else chain + rest

    def mro_lookup(self, mi, qual, member):
        """('ok', mi2, qual2) | None (hazard/unresolved)."""
        chain = self.class_chain(mi, qual)
        if chain is None:
            return None
        for cmi, cq in chain:
            ci = cmi.classes[cq]
            m = ci["members"].get(member)
            if m is not None:
                if m["bad_dec"]:
                    return None
                # repo-internal override check [ASM-1054]
                key = (cmi.rel + "::" + cq, member)
                if self.subclass_overrides.get(key):
                    return None
                return ("ok", cmi, m["qual"])
            if member in ci["member_names"]:
                return None  # bound to a non-def class attr -> untracked value
        return None  # not found in analyzed chain: could be instance attr

    def build_override_index(self):
        for rel, mi in self.modules.items():
            if not mi.parsed:
                continue
            for qual in mi.classes:
                chain = self.class_chain(mi, qual)
                if not chain or len(chain) < 2:
                    continue
                for member in mi.classes[qual]["member_names"]:
                    for ami, aq in chain[1:]:
                        self.subclass_overrides[(ami.rel + "::" + aq, member)] = True

    # ---------- pass 2: emit edges ----------
    def extract(self):
        self.parse_all()
        self.build_override_index()
        for rel, mi in sorted(self.modules.items()):
            if mi.parsed:
                self._emit_module(mi)
        return self.edges

    def _emit_module(self, mi):
        E = self.edges
        rel = mi.rel
        if mi.exec_taint:
            for rk in ("call", "import", "binding", "instantiate"):
                E.append(Edge(rk, rel, None, "unknown", "*", rel, (0, 0), "TAINT_EXEC"))

        # ---- import edges + binding facts ----
        def ancestors(target_rel):
            """Repo __init__.py files of every ancestor package: importing
            a.b.c also imports a and a.b (parent-package closure — Python
            import semantics; probe-detected validity fix)."""
            out = []
            parts = target_rel.replace(os.sep, "/").split("/")
            for i in range(1, len(parts)):
                cand = "/".join(parts[:i]) + "/__init__.py"
                if cand in self.modules and cand != target_rel:
                    out.append(cand)
            return out

        for name, recs in mi.bindings.items():
            for r in recs:
                if r["kind"] in ("import", "from"):
                    tgt = r["target"]
                    if tgt[0] == "member":
                        repo_rel = tgt[1][1] if tgt[1][0] == "repo" else None
                    else:
                        repo_rel = tgt[1] if tgt[0] == "repo" else None
                    if repo_rel is not None:
                        dst, cand = "repo:" + repo_rel, repo_rel
                        closure = [repo_rel] + ancestors(repo_rel)
                    else:
                        extname = tgt[1][1] if tgt[0] == "member" else tgt[1]
                        dst, cand = "ext:" + extname, extname
                        closure = []
                    if r.get("top"):
                        E.append(Edge("import", rel, dst, "proved", None, rel,
                                      r["span"], "P1"))
                        for anc in (closure[1:] if closure else []):
                            E.append(Edge("import", rel, "repo:" + anc,
                                          "proved", None, rel, r["span"], "P1"))
                    else:
                        E.append(Edge("import", rel, dst, "unknown", str(cand),
                                      rel, r["span"], "IMPORT_CONDITIONAL"))
                        for anc in (closure[1:] if closure else []):
                            E.append(Edge("import", rel, None, "unknown", anc,
                                          rel, r["span"], "IMPORT_CONDITIONAL"))
                elif r["kind"] in ("function", "class", "assign"):
                    pass  # binding facts emitted from defs/assign walk below

        # binding facts: defs at any nesting (syntactic sites)
        for qual, d in mi.defs.items():
            E.append(Edge("binding", rel, rel + "::" + qual, "proved", None, rel,
                          d["span"], "P3"))
            # containment (lexical)
            parent = rel if "." not in qual else rel + "::" + qual.rsplit(".", 1)[0]
            E.append(Edge("contains", parent, rel + "::" + qual, "proved", None,
                          rel, d["span"], "P2"))
        for name, recs in mi.bindings.items():
            for r in recs:
                if r["kind"] == "assign":
                    scope = r.get("scope", "")
                    dst = rel + "::" + (scope + "." + name if scope else name)
                    E.append(Edge("binding", rel, dst, "proved",
                                  None, rel, r["span"], "P3"))
                    parent = rel + "::" + scope if scope else rel
                    E.append(Edge("contains", parent, dst, "proved", None,
                                  rel, r["span"], "P2"))

        # ---- walk expressions for calls/instantiations/dynamic hazards ----
        table = symtable.symtable(mi.src.decode("utf-8", "replace"), rel, "exec")
        st_index = {}

        def index_tables(t):
            for c in t.get_children():
                st_index.setdefault((c.get_name(), c.get_lineno()), c)
                index_tables(c)
        index_tables(table)

        def scope_id(stack):
            return rel + "::" + ".".join(stack) if stack else rel

        def classify_name(name, sstack):
            """'global'|'local'|None using symtable scope chain."""
            if not sstack:
                return "global"
            t = sstack[-1]
            try:
                s = t.lookup(name)
            except KeyError:
                return "global"
            if s.is_global():
                return "global"
            if s.is_local() or s.is_parameter() or s.is_free():
                return "local"
            return "global"

        def handle_call(node, stack, sstack, cls_ctx):
            func = node.func
            call_funcs.add(id(func))
            span = mi.span(node)
            src = scope_id(stack)

            def unk(reason, cand):
                E.append(Edge("call", src, None, "unknown", cand, rel, span, reason))

            def emit_call(res, reason):
                kind, tmi, tqual = res[0], None, None
                if res[0] in ("function",):
                    E.append(Edge("call", src, res[1].rel + "::" + res[2], "proved",
                                  None, rel, span, reason))
                elif res[0] == "class":
                    chain = self.class_chain(res[1], res[2])
                    if chain is None:
                        E.append(Edge("instantiate", src, None, "unknown",
                                      res[2].rsplit(".", 1)[-1], rel, span,
                                      "CALL_MRO_HAZARD"))
                    else:
                        E.append(Edge("instantiate", src,
                                      res[1].rel + "::" + res[2], "proved", None,
                                      rel, span, "P7"))
                elif res[0] in ("ext", "extmodule"):
                    E.append(Edge("call", src, "ext:" + res[1], "proved", None,
                                  rel, span, reason))
                elif res[0] == "module":
                    unk("CALL_NONNAME_CALLEE", "*")  # calling a module: nonsense/fail-closed
                else:
                    unk("CALL_NONNAME_CALLEE", "*")

            if isinstance(func, ast.Name):
                nm = func.id
                if nm in EXEC_NAMES:
                    return  # taint already emitted module-wide
                if nm in DYN_IMPORT_NAMES:
                    cand = lit_str(node.args[0]) if node.args else None
                    E.append(Edge("import", rel, None, "unknown", cand or "*",
                                  rel, span, "IMPORT_DYNAMIC"))
                    return
                if nm == "getattr":
                    return  # handled at parent Call if result is called
                if nm in ("setattr", "delattr"):
                    cand = lit_str(node.args[1]) if len(node.args) > 1 else None
                    E.append(Edge("binding", rel, None, "unknown", cand or "*",
                                  rel, span, "BIND_SETATTR"))
                    return
                cls = classify_name(nm, sstack)
                if cls == "local":
                    # runtime callee name NOT derivable from a local variable
                    # name -> unrestricted [ASM-1056 candidate discipline]
                    unk("CALL_LOCAL_VALUE", "*")
                    return
                if mi.star_import:
                    # star import binds by def name -> name preserved
                    unk("CALL_STARIMPORT_TAINT", nm)
                    return
                res = self.resolve_global_name(mi, nm)
                if res is None:
                    if nm not in mi.bindings and nm in BUILTIN_NAMES:
                        E.append(Edge("call", src, "ext:builtins." + nm, "proved",
                                      None, rel, span, "P6"))
                    else:
                        # candidate restricted to {nm} ONLY if every binding
                        # record provably preserves the def name (def/class
                        # stmts or non-aliased from-imports); else the runtime
                        # callee could be ANY def (aliasing/assignment/
                        # decorator wrapper) -> '*' [ASM-1056]
                        recs = mi.bindings.get(nm, [])
                        preserved = bool(recs) and all(
                            r["kind"] in ("function", "class")
                            or (r["kind"] == "from"
                                and r.get("raw", "").split(".")[-1] == nm)
                            for r in recs) and not any(
                            r.get("bad_dec") for r in recs)
                        unk("CALL_MODULE_BINDING_UNRESOLVED",
                            nm if preserved else "*")
                    return
                emit_call(res, "P4")
                return

            if isinstance(func, ast.Attribute):
                attr = func.attr
                recv = func.value
                # self.m() [P8]
                if isinstance(recv, ast.Name):
                    if recv.id == "self" and cls_ctx is not None:
                        r = self.mro_lookup(cls_ctx[0], cls_ctx[1], attr)
                        if r:
                            E.append(Edge("call", src, r[1].rel + "::" + r[2],
                                          "proved", None, rel, span, "P8"))
                        else:
                            unk("CALL_MRO_UNRESOLVED", attr)
                        return
                    if classify_name(recv.id, sstack) == "local":
                        unk("CALL_ATTR_RECEIVER_UNTYPED", attr)
                        return
                    if mi.star_import:
                        unk("CALL_STARIMPORT_TAINT", attr)
                        return
                    res = self.resolve_global_name(mi, recv.id)
                    if res is None:
                        unk("CALL_ATTR_RECEIVER_UNTYPED", attr)
                        return
                    if res[0] == "module":
                        mi2 = self.modules[res[1]]
                        if not mi2.parsed:
                            unk("CALL_ATTR_MODULE_MEMBER_UNRESOLVED", attr)
                            return
                        r = self.resolve_member(mi2, attr)
                        if r is None:
                            unk("CALL_ATTR_MODULE_MEMBER_UNRESOLVED", attr)
                        else:
                            emit_call(r, "P5")
                        return
                    if res[0] == "extmodule" or res[0] == "ext":
                        E.append(Edge("call", src, "ext:" + res[1] + "." + attr,
                                      "proved", None, rel, span, "P5"))
                        return
                    if res[0] == "class":
                        r = self.mro_lookup(res[1], res[2], attr)
                        if r:
                            E.append(Edge("call", src, r[1].rel + "::" + r[2],
                                          "proved", None, rel, span, "P8"))
                        else:
                            unk("CALL_MRO_UNRESOLVED", attr)
                        return
                    unk("CALL_ATTR_RECEIVER_UNTYPED", attr)
                    return
                # C().m() — directly-chained literal instantiation [P8]
                if isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name):
                    nm = recv.func.id
                    if classify_name(nm, sstack) == "global" and not mi.star_import:
                        res = self.resolve_global_name(mi, nm)
                        if res and res[0] == "class":
                            r = self.mro_lookup(res[1], res[2], attr)
                            if r:
                                E.append(Edge("call", src, r[1].rel + "::" + r[2],
                                              "proved", None, rel, span, "P8"))
                                return
                unk("CALL_ATTR_RECEIVER_UNTYPED", attr)
                return

            if isinstance(func, ast.Call) and isinstance(func.func, ast.Name) \
                    and func.func.id == "getattr":
                cand = lit_str(func.args[1]) if len(func.args) > 1 else None
                unk("CALL_GETATTR", cand or "*")
                return
            unk("CALL_NONNAME_CALLEE", "*")

        def lit_str(n):
            return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None

        call_funcs = set()

        def escape_check(node, stack, sstack, cls_ctx):
            """A Load-context reference to a repo def/class OUTSIDE call
            position lets the callable ESCAPE as a value: it may be invoked
            later from any scope (callbacks, map/sorted, storage). Fail-closed
            per ASM-1031: emit an unknown call edge with the RESOLVED def's
            name as candidate [tier a]. Unresolvable references are counted,
            not edged [tier b — reported as a spec-gap metric, ASM-1057]."""
            src = scope_id(stack)
            span = mi.span(node)

            def esc(cand):
                self.stats["value_escape_edges"] += 1
                E.append(Edge("call", src, None, "unknown", cand, rel, span,
                              "CALL_VALUE_ESCAPE"))

            if isinstance(node, ast.Name):
                nm = node.id
                if classify_name(nm, sstack) == "local":
                    self.stats["name_load_untracked"] += 1
                    return
                if mi.star_import or mi.exec_taint:
                    self.stats["name_load_untracked"] += 1
                    return
                res = self.resolve_global_name(mi, nm)
                if res and res[0] in ("function", "class"):
                    esc(res[2].split(".")[-1])
                elif res is None and nm in mi.bindings:
                    self.stats["name_load_untracked"] += 1
                return
            # Attribute loads: only typed receivers resolve [P5/P8 scope]
            attr, recv = node.attr, node.value
            if isinstance(recv, ast.Name):
                if recv.id == "self" and cls_ctx is not None:
                    r = self.mro_lookup(cls_ctx[0], cls_ctx[1], attr)
                    if r:
                        esc(r[2].split(".")[-1])
                    else:
                        self.stats["attr_load_untracked"] += 1
                    return
                if classify_name(recv.id, sstack) == "global" \
                        and not mi.star_import:
                    res = self.resolve_global_name(mi, recv.id)
                    if res and res[0] == "module":
                        mi2 = self.modules[res[1]]
                        r = self.resolve_member(mi2, attr) if mi2.parsed else None
                        if r and r[0] in ("function", "class"):
                            esc(r[2].split(".")[-1])
                        else:
                            self.stats["attr_load_untracked"] += 1
                        return
                    if res and res[0] == "class":
                        r = self.mro_lookup(res[1], res[2], attr)
                        if r:
                            esc(r[2].split(".")[-1])
                        else:
                            self.stats["attr_load_untracked"] += 1
                        return
            self.stats["attr_load_untracked"] += 1

        def visit(node, stack, sstack, cls_ctx):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                st = st_index.get((node.name, node.lineno))
                # decorators / bases / defaults / annotations execute in the
                # ENCLOSING scope. A decorator APPLICATION is a call at
                # def-execution time: bare @d -> call d(f); parametrized
                # @d(args) -> call d(args) (walked below) PLUS an unrestricted
                # result-application call (the returned callable is untracked)
                for d in node.decorator_list:
                    dd = dotted(d.func) if isinstance(d, ast.Call) else dotted(d)
                    if dd is not None and dd in ALLOWLIST:
                        continue  # allowlisted, identity-preserving [ASM-1031]
                    if isinstance(d, ast.Call):
                        walk_expr_only(d, stack, sstack, cls_ctx)
                        E.append(Edge("call", scope_id(stack), None, "unknown",
                                      "*", rel, mi.span(d),
                                      "CALL_NONNAME_CALLEE"))
                    else:
                        fake = ast.Call(func=d, args=[], keywords=[])
                        ast.copy_location(fake, d)
                        fake.end_lineno, fake.end_col_offset = d.end_lineno, d.end_col_offset
                        handle_call(fake, stack, sstack, cls_ctx)
                if isinstance(node, ast.ClassDef):
                    for b in list(node.bases) + [k.value for k in node.keywords]:
                        walk_expr_only(b, stack, sstack, cls_ctx)
                    q = ".".join(stack + [node.name]) if stack else node.name
                    inner_ctx = (mi, q)
                else:
                    a = node.args
                    for dflt in list(a.defaults) + [d for d in a.kw_defaults if d]:
                        walk_expr_only(dflt, stack, sstack, cls_ctx)
                    inner_ctx = cls_ctx
                for stmt in node.body:
                    visit(stmt, stack + [node.name],
                          sstack + ([st] if st else []), inner_ctx)
                return
            if isinstance(node, ast.Call):
                handle_call(node, stack, sstack, cls_ctx)
            elif isinstance(node, (ast.Name, ast.Attribute)) \
                    and isinstance(node.ctx, ast.Load) \
                    and id(node) not in call_funcs:
                escape_check(node, stack, sstack, cls_ctx)
                if isinstance(node, ast.Attribute):
                    for child in ast.iter_child_nodes(node):
                        visit(child, stack, sstack, cls_ctx)
                    return
            elif isinstance(node, ast.Subscript):
                # globals()['x'] = ... / vars()[..] writes
                if isinstance(node.ctx, (ast.Store, ast.Del)) and \
                        isinstance(node.value, ast.Call) and \
                        isinstance(node.value.func, ast.Name) and \
                        node.value.func.id in ("globals", "locals", "vars"):
                    E.append(Edge("binding", rel, None, "unknown", "*", rel,
                                  mi.span(node), "BIND_DYNAMIC_NS"))
            for child in ast.iter_child_nodes(node):
                visit(child, stack, sstack, cls_ctx)

        def walk_expr_only(node, stack, sstack, cls_ctx):
            visit(node, stack, sstack, cls_ctx)

        for stmt in mi.tree.body:
            visit(stmt, [], [], None)
