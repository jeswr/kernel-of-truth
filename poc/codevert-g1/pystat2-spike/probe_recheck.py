#!/usr/bin/env python3
"""PY-STAT/2-SPIKE — dynamic-probe soundness GUARD (mechanical, NON-SCORED).

Re-runs the poc/codevert-g0/probe_check.py classification logic against the
EXISTING saved traces (poc/codevert-g0/results/probe/*.trace.json) for BOTH
extractors (PY-STAT/1 and PY-STAT/2-SPIKE) in one pass and reports:
  (a) proved-fact / proved-answer validity violations under each world
      (spike adds no proved edges, so any v2-vs-v1 change here is a bug);
  (b) NEW candidate-compatibility misses: observed call edges whose callee
      name WAS covered under PY-STAT/1 (via '*' or a candidate) but is
      EXCLUDED by the narrowed PY-STAT/2-SPIKE candidate sets — the spike's
      key soundness risk. Counted and listed.
The per-edge frame->def mapping is identical across the two extractors
(pass-1 parsing is untouched); it is built once from the PY-STAT/1 instance.
Nothing under poc/codevert-g0/ is written.
"""
import bisect, json


def line_of(mi, byte_off):
    return bisect.bisect_right(mi.line_off, byte_off)


class EdgeIndex:
    """The probe_check.py per-extractor indexes (proved pairs, unknown
    candidate sets per src, taint modules)."""

    def __init__(self, edges):
        self.proved_pairs = set()
        self.inst_by_src = {}
        self.unk_by_src = {}
        self.taint_mods = set()
        for e in edges:
            if e.status == "proved" and e.rel in ("call", "instantiate"):
                self.proved_pairs.add((e.src, e.dst))
                if e.rel == "instantiate":
                    self.inst_by_src.setdefault(e.src, set()).add(e.dst)
            elif e.status == "unknown":
                if e.rel in ("call", "instantiate"):
                    self.unk_by_src.setdefault(e.src, set()).add(e.cand)
                if e.reason in ("TAINT_EXEC", "MODULE_UNPARSED"):
                    self.taint_mods.add(e.src)


def recheck(repo, ex1, edges1, world1, ex2, edges2, world2, probe_json,
            out_json):
    # ---- frame->def mapping (from ex1; identical in ex2 by construction) --
    defidx, ranges = {}, {}
    for rel, mi in ex1.modules.items():
        if not mi.parsed:
            continue
        rr = []
        for qual, d in mi.defs.items():
            nm = qual.split(".")[-1]
            defidx.setdefault((rel, nm), []).append((d["line"], qual, d["kind"]))
            rr.append((line_of(mi, d["span"][0]),
                       line_of(mi, d["span"][1] - 1), qual))
        ranges[rel] = sorted(rr)

    def map_def(rel, name, firstlineno):
        cands = defidx.get((rel, name), [])
        best = None
        for line, qual, kind in cands:
            diff = line - firstlineno
            if -2 <= diff <= 20 and (best is None or abs(diff) < abs(best[0])):
                best = (diff, qual, kind)
        if best:
            return best[1], best[2]
        if len(cands) == 1:
            return cands[0][1], cands[0][2]
        return None

    def innermost(rel, lineno):
        best = None
        for a, b, qual in ranges.get(rel, []):
            if a <= lineno <= b and (best is None or (b - a) < best[0]):
                best = (b - a, qual)
        return rel + "::" + best[1] if best else rel

    def map_caller(rel, name, firstlineno):
        if name == "<module>":
            return rel
        if name.startswith("<"):
            return innermost(rel, firstlineno)
        m = map_def(rel, name, firstlineno)
        return rel + "::" + m[0] if m else innermost(rel, firstlineno)

    def chain_ids(ex, file, qual):
        mi = ex.modules.get(file)
        ch = ex.class_chain(mi, qual) if mi and mi.parsed else None
        return {cmi.rel + "::" + cq for cmi, cq in ch} if ch else \
            {file + "::" + qual}

    idx1, idx2 = EdgeIndex(edges1), EdgeIndex(edges2)

    def classify(ex, idx, src, dst, equal, ef, name, cf):
        """probe_check.py matches() verbatim, parameterized by extractor."""
        if (src, dst) in idx.proved_pairs:
            return "confirmed_proved"
        if name in ("__init__", "__new__") and "." in equal:
            kq = equal.rsplit(".", 1)[0]
            kid = ef + "::" + kq
            for c in idx.inst_by_src.get(src, ()):
                parts = c.split("::")
                if c == kid or (len(parts) == 2
                                and kid in chain_ids(ex, parts[0], parts[1])):
                    return "confirmed_instantiation"
        cands = idx.unk_by_src.get(src, set())
        if "*" in cands or name in cands:
            return "unknown_compatible"
        if name in ("__init__", "__new__") and "." in equal \
                and equal.rsplit(".", 1)[0].split(".")[-1] in cands:
            return "unknown_compatible"
        if cf in idx.taint_mods or (src.split("::")[0] in idx.taint_mods):
            return "unknown_compatible"
        if name.startswith("__") and name.endswith("__") \
                and name not in ("__init__", "__new__", "__call__"):
            return "protocol_dispatch"
        d = ex.modules[ef].defs.get(equal)
        if d and d.get("decorated_bad"):
            return "descriptor_or_decorated"
        return "miss"

    def query_ok(world, ex, idx, src, equal, ef, name):
        """probe_check.py query-level (ASM-1030-shape) check."""
        if name in ("__init__", "__new__") and "." in equal:
            kq = equal.rsplit(".", 1)[0]
            stq, _, _ = world.instance_of(ef, kq)
            return stq != "proved" or any(
                c == ef + "::" + kq for c in idx.inst_by_src.get(src, ()))
        stq, listing, _ = world.callers_of(ef, equal)
        return stq != "proved" or src in listing

    probe = json.load(open(probe_json))
    keys = ("confirmed_proved", "confirmed_instantiation",
            "unknown_compatible", "miss", "protocol_dispatch",
            "descriptor_or_decorated")
    stats1 = {k: 0 for k in keys}
    stats2 = {k: 0 for k in keys}
    shared = {"class_body_exec": 0, "unmapped_callee": 0,
              "resumption_total": 0}
    q1 = {"covered": 0, "violation": 0}
    q2 = {"covered": 0, "violation": 0}
    transitions = {}
    new_misses = []          # v1 non-miss -> v2 miss (non-generator)
    new_misses_gen = 0       # same, generator resumptions
    validity_viol1, validity_viol2 = [], []

    for (cf, cn, cl, ef, en, el, is_gen) in probe["call_edges"]:
        if cf not in ex1.modules or ef not in ex1.modules:
            continue
        m = map_def(ef, en, el)
        if en.startswith("<") or m is None:
            shared["unmapped_callee"] += 1
            continue
        equal, kind = m
        if kind == "class":
            shared["class_body_exec"] += 1
            continue
        src = map_caller(cf, cn, cl)
        dst = ef + "::" + equal
        name = equal.split(".")[-1]

        r1 = classify(ex1, idx1, src, dst, equal, ef, name, cf)
        r2 = classify(ex2, idx2, src, dst, equal, ef, name, cf)
        if not is_gen:
            if query_ok(world1, ex1, idx1, src, equal, ef, name):
                q1["covered"] += 1
            else:
                q1["violation"] += 1
                validity_viol1.append({"family": "call", "target": dst,
                                       "observed_src": src})
            if query_ok(world2, ex2, idx2, src, equal, ef, name):
                q2["covered"] += 1
            else:
                q2["violation"] += 1
                validity_viol2.append({"family": "call", "target": dst,
                                       "observed_src": src})
        if is_gen:
            shared["resumption_total"] += 1
            if r1 != "miss" and r2 == "miss":
                new_misses_gen += 1
            continue
        stats1[r1] += 1
        stats2[r2] += 1
        if r1 != r2:
            key = r1 + "->" + r2
            transitions[key] = transitions.get(key, 0) + 1
        if r1 != "miss" and r2 == "miss":
            new_misses.append({"caller": src, "callee": dst, "v1": r1,
                               "caller_frame": [cf, cn, cl],
                               "callee_line": el})

    # ---- imports (spike touches no import edges: expected unchanged) ----
    def imp_check(ex, world, idx):
        istats = {"confirmed": 0, "unknown_compatible": 0, "miss": 0,
                  "external": 0}
        observed_importers = {}
        for (rel, name, level, pkg, fromlist) in probe["import_events"]:
            if rel not in ex.modules or not ex.modules[rel].parsed:
                continue
            mi = ex.modules[rel]
            targets = []
            r0 = ex.resolve_import(mi, name, level)
            if r0[0] == "repo":
                targets.append(r0[1])
            for fm in fromlist:
                if fm == "*":
                    continue
                rf = ex.resolve_import(mi, (name + "." + fm) if name else fm,
                                       level)
                if rf[0] == "repo":
                    targets.append(rf[1])
            if not targets:
                istats["external"] += 1
                continue
            unk_imp = {e.cand for e in world.unk_import_by_src.get(rel, ())}
            for t in targets:
                observed_importers.setdefault(t, set()).add(rel)
                tmi = ex.modules.get(t)
                names = {t} | ({tmi.dotted} if tmi and tmi.dotted else set())
                if any(e.dst == "repo:" + t
                       for e in world.proved_import_by_src.get(rel, ())):
                    istats["confirmed"] += 1
                elif "*" in unk_imp or (names & unk_imp) \
                        or rel in idx.taint_mods:
                    istats["unknown_compatible"] += 1
                else:
                    istats["miss"] += 1
        viol = []
        for t, importers in observed_importers.items():
            st, listing, _ = world.imported_by(t)
            if st == "proved":
                for i in importers - set(listing):
                    viol.append({"family": "imported_by", "target": t,
                                 "observed_src": i})
        return istats, viol

    ist1, iv1 = imp_check(ex1, world1, idx1)
    ist2, iv2 = imp_check(ex2, world2, idx2)
    validity_viol1.extend(iv1)
    validity_viol2.extend(iv2)

    out = {"repo": repo, "pytest_exit": probe["pytest_exit"],
           "n_observed_call_edges": len(probe["call_edges"]),
           "shared_exclusions": shared,
           "call_soundness_v1": stats1, "call_soundness_v2": stats2,
           "call_query_level_v1": q1, "call_query_level_v2": q2,
           "import_soundness_v1": ist1, "import_soundness_v2": ist2,
           "classification_transitions_v1_to_v2": dict(
               sorted(transitions.items())),
           "n_new_misses_nongen": len(new_misses),
           "n_new_misses_generator": new_misses_gen,
           "new_misses": new_misses,
           "n_validity_violations_v1": len(validity_viol1),
           "n_validity_violations_v2": len(validity_viol2),
           "validity_violations_v2": validity_viol2}
    with open(out_json, "w") as fh:
        json.dump(out, fh, indent=1)
    return out
