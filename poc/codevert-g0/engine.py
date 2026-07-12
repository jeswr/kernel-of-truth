#!/usr/bin/env python3
"""CODEVERT G0 — query engine over PY-STAT/1 facts.

Implements the 8 kot-query-code/1 families with the CODEVERT §2.2
completeness-precondition semantics [PROPOSED-ASM: ASM-1031]:
  - inverse/exhaustive queries return `proved` ONLY if every listed edge is
    proved AND no unknown edge of the relevant relation kind(s) exists
    anywhere in the analyzed scope whose candidate set contains the target's
    name (or is unrestricted '*');
  - otherwise UNKNOWN-INCOMPLETE(partial_lower_bound, blocking_unknown_count);
  - proved-EMPTY negative answers require the SAME precondition;
  - census targets the extractor cannot locate count TARGET-NOT-FOUND
    (never silently dropped).
Statuses returned: 'proved' | 'unknown_incomplete' | 'target_not_found'.
"""


class World:
    def __init__(self, edges, modules):
        """edges: list of Edge; modules: rel -> ModuleInfo (for defs/parse)."""
        self.modules = modules
        self.proved_call_by_dst = {}
        self.proved_inst_by_dst = {}
        self.proved_call_by_src = {}
        self.proved_import_by_src = {}
        self.proved_import_by_dst = {}
        self.contains_by_parent = {}
        self.contains_child_parent = {}
        self.binding_by_name = {}       # name -> [(module, edge)]
        self.unk_call_cand = {}         # cand -> count ('*' incl.)
        self.unk_call_by_src = {}
        self.unk_inst_cand = {}
        self.unk_import_cand = {}       # candidate (relpath | dotted | '*') -> count
        self.unk_import_by_src = {}
        self.unk_bind_cand = {}
        self.n_unparsed = sum(1 for m in modules.values() if not m.parsed)
        for e in edges:
            if e.status == "proved":
                if e.rel == "call":
                    self.proved_call_by_dst.setdefault(e.dst, []).append(e)
                    self.proved_call_by_src.setdefault(e.src, []).append(e)
                elif e.rel == "instantiate":
                    self.proved_inst_by_dst.setdefault(e.dst, []).append(e)
                    self.proved_call_by_src.setdefault(e.src, []).append(e)
                elif e.rel == "import":
                    self.proved_import_by_src.setdefault(e.src, []).append(e)
                    self.proved_import_by_dst.setdefault(e.dst, []).append(e)
                elif e.rel == "contains":
                    self.contains_by_parent.setdefault(e.src, []).append(e)
                    self.contains_child_parent[e.dst] = e.src
                elif e.rel == "binding":
                    name = e.dst.split("::")[-1].split(".")[-1]
                    self.binding_by_name.setdefault(name, []).append(e)
            else:  # unknown
                if e.rel == "call":
                    self.unk_call_cand[e.cand] = self.unk_call_cand.get(e.cand, 0) + 1
                    self.unk_call_by_src.setdefault(e.src, []).append(e)
                elif e.rel == "instantiate":
                    self.unk_inst_cand[e.cand] = self.unk_inst_cand.get(e.cand, 0) + 1
                    self.unk_call_by_src.setdefault(e.src, []).append(e)
                elif e.rel == "import":
                    self.unk_import_cand[e.cand] = self.unk_import_cand.get(e.cand, 0) + 1
                    self.unk_import_by_src.setdefault(e.src, []).append(e)
                elif e.rel == "binding":
                    self.unk_bind_cand[e.cand] = self.unk_bind_cand.get(e.cand, 0) + 1

    # ---------- helpers ----------
    def _sym(self, file, qual):
        mi = self.modules.get(file)
        if mi is None or not mi.parsed:
            return None
        if qual is None:
            return file
        if qual in mi.defs:
            return file + "::" + qual
        return None

    def _blocked(self, counters, name):
        n = 0
        for c in counters:
            n += c.get("*", 0) + (c.get(name, 0) if name is not None else 0)
        return n

    # ---------- forward families ----------
    def callees_of(self, file, qual):
        sym = self._sym(file, qual)
        if sym is None:
            return ("target_not_found", [], 0)
        listed = [e.dst for e in self.proved_call_by_src.get(sym, [])]
        blocking = len(self.unk_call_by_src.get(sym, []))
        # module-wide exec taint edges attach to the MODULE scope; a function
        # inside a tainted module is still fail-closed blocked:
        blocking += sum(1 for e in self.unk_call_by_src.get(file, [])
                        if e.reason in ("TAINT_EXEC", "MODULE_UNPARSED"))
        st = "proved" if blocking == 0 else "unknown_incomplete"
        return (st, sorted(set(listed)), blocking)

    def imports_of(self, file):
        mi = self.modules.get(file)
        if mi is None or not mi.parsed:
            return ("target_not_found", [], 0)
        listed = [e.dst for e in self.proved_import_by_src.get(file, [])]
        blocking = len(self.unk_import_by_src.get(file, []))
        st = "proved" if blocking == 0 else "unknown_incomplete"
        return (st, sorted(set(listed)), blocking)

    def contains(self, file, qual):
        sym = self._sym(file, qual)
        if sym is None:
            return ("target_not_found", [], 0)
        listed = [e.dst for e in self.contains_by_parent.get(sym, [])]
        return ("proved", sorted(set(listed)), 0)  # lexical relation [ASM-1053]

    def contained_in(self, file, qual):
        sym = self._sym(file, qual)
        if sym is None:
            return ("target_not_found", [], 0)
        parent = self.contains_child_parent.get(sym)
        if parent is None and qual is not None:
            parent = file  # top-level def -> module (defensive; edges cover this)
        return ("proved", [parent], 0)

    # ---------- inverse / exhaustive families ----------
    def callers_of(self, file, qual):
        sym = self._sym(file, qual)
        if sym is None:
            return ("target_not_found", [], 0)
        name = qual.split(".")[-1]
        listed = [e.src for e in self.proved_call_by_dst.get(sym, [])]
        blocking = self._blocked([self.unk_call_cand], name) + self.n_unparsed
        st = "proved" if blocking == 0 else "unknown_incomplete"
        return (st, sorted(set(listed)), blocking)

    def imported_by(self, file):
        mi = self.modules.get(file)
        if mi is None or not mi.parsed:
            return ("target_not_found", [], 0)
        listed = [e.src for e in self.proved_import_by_dst.get("repo:" + file, [])]
        # candidates may be recorded as relpath (resolved) or dotted (dynamic)
        names = {file}
        if mi.dotted:
            names.add(mi.dotted)
        blocking = self.unk_import_cand.get("*", 0) + self.n_unparsed
        for n in names:
            blocking += self.unk_import_cand.get(n, 0)
        st = "proved" if blocking == 0 else "unknown_incomplete"
        return (st, sorted(set(listed)), blocking)

    def where_defined(self, name):
        listed = [(e.file, e.span) for e in self.binding_by_name.get(name, [])]
        blocking = self._blocked([self.unk_bind_cand], name) + self.n_unparsed
        st = "proved" if blocking == 0 else "unknown_incomplete"
        if not listed and st == "proved":
            st = "target_not_found" if name is None else st  # keep proved-empty
        return (st, sorted(set(listed)), blocking)

    def instance_of(self, file, qual):
        sym = self._sym(file, qual)
        if sym is None:
            return ("target_not_found", [], 0)
        name = qual.split(".")[-1]
        listed = [(e.file, e.span) for e in self.proved_inst_by_dst.get(sym, [])]
        # an unresolved CALL could instantiate this class -> quantify over both
        blocking = self._blocked([self.unk_inst_cand, self.unk_call_cand], name) \
            + self.n_unparsed
        st = "proved" if blocking == 0 else "unknown_incomplete"
        return (st, sorted(set(listed)), blocking)


def run_query(world, family, target):
    if family == "callers_of":
        return world.callers_of(target["file"], target["qual"])
    if family == "callees_of":
        return world.callees_of(target["file"], target["qual"])
    if family == "imports_of":
        return world.imports_of(target["file"])
    if family == "imported_by":
        return world.imported_by(target["file"])
    if family == "contains":
        return world.contains(target["file"], target.get("qual"))
    if family == "contained_in":
        return world.contained_in(target["file"], target["qual"])
    if family == "where_defined":
        return world.where_defined(target["name"])
    if family == "instance_of":
        return world.instance_of(target["file"], target["qual"])
    raise ValueError(family)
