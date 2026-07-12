#!/usr/bin/env python3
"""CODEVERT G0 — dynamic-probe soundness/validity checker (mechanical).

Spec basis: CODEVERT §7-G1 endpoint 5 [PROPOSED-ASM: ASM-1030] run here as a
NON-SCORED mini-probe: every OBSERVED intra-repo call/import edge must appear
in proved ∪ unknown-compatible; an observed edge absent from both is an
extractor SOUNDNESS miss. Additionally checks proved (completeness-claiming)
answers against observations: an observed importer absent from a
proved imported-by listing, or an observed caller absent from a proved
callers-of listing, is a NEGATIVE-ANSWER VALIDITY violation.

Generator/coroutine frame activations are classified separately (a resumption
is not a call statement; disclosed, not hidden).
"""
import bisect, json, os, sys

sys.setrecursionlimit(100000)
from extractor import Extractor
from engine import World


def line_of(mi, byte_off):
    return bisect.bisect_right(mi.line_off, byte_off)


def main(repo, probe_json, out_json):
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(base, "corpus", repo)
    ex = Extractor(root, repo)
    edges = ex.extract()
    world = World(edges, ex.modules)

    # --- indexes ---
    proved_pairs = set()
    inst_by_src = {}
    unk_by_src = {}      # src -> set of cands
    taint_mods = set()
    for e in edges:
        if e.status == "proved" and e.rel in ("call", "instantiate"):
            proved_pairs.add((e.src, e.dst))
            if e.rel == "instantiate":
                inst_by_src.setdefault(e.src, set()).add(e.dst)
        elif e.status == "unknown":
            if e.rel in ("call", "instantiate"):
                unk_by_src.setdefault(e.src, set()).add(e.cand)
            if e.reason in ("TAINT_EXEC", "MODULE_UNPARSED"):
                taint_mods.add(e.src)

    defidx = {}          # (rel, name) -> [(line, qual, kind)]
    ranges = {}          # rel -> [(start_line, end_line, qual)]
    for rel, mi in ex.modules.items():
        if not mi.parsed:
            continue
        rr = []
        for qual, d in mi.defs.items():
            nm = qual.split(".")[-1]
            defidx.setdefault((rel, nm), []).append((d["line"], qual, d["kind"]))
            rr.append((line_of(mi, d["span"][0]), line_of(mi, d["span"][1] - 1), qual))
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

    def chain_ids(file, qual):
        mi = ex.modules.get(file)
        ch = ex.class_chain(mi, qual) if mi and mi.parsed else None
        return {cmi.rel + "::" + cq for cmi, cq in ch} if ch else {file + "::" + qual}

    probe = json.load(open(probe_json))
    stats = {"confirmed_proved": 0, "confirmed_instantiation": 0,
             "unknown_compatible": 0, "miss": 0, "protocol_dispatch": 0,
             "descriptor_or_decorated": 0,
             "class_body_exec": 0, "unmapped_callee": 0,
             "resumption_total": 0, "resumption_unmatched": 0}
    qstats = {"covered": 0, "violation": 0}
    misses = []
    validity_viol = []

    for (cf, cn, cl, ef, en, el, is_gen) in probe["call_edges"]:
        if cf not in ex.modules or ef not in ex.modules:
            continue
        m = map_def(ef, en, el)
        if en.startswith("<") or m is None:
            if en in ("__init__", "__new__") or en.startswith("<"):
                stats["unmapped_callee"] += 1
                continue
            stats["unmapped_callee"] += 1
            continue
        equal, kind = m
        if kind == "class":
            stats["class_body_exec"] += 1
            continue
        src = map_caller(cf, cn, cl)
        dst = ef + "::" + equal
        name = equal.split(".")[-1]

        def matches():
            if (src, dst) in proved_pairs:
                return "confirmed_proved"
            # instantiation: observed __init__/__new__ of class K, proved
            # instantiate edge src -> C with K in C's analyzed chain
            if name in ("__init__", "__new__") and "." in equal:
                kq = equal.rsplit(".", 1)[0]
                kid = ef + "::" + kq
                for c in inst_by_src.get(src, ()):
                    parts = c.split("::")
                    if c == kid or (len(parts) == 2
                                    and kid in chain_ids(parts[0], parts[1])):
                        return "confirmed_instantiation"
            cands = unk_by_src.get(src, set())
            if "*" in cands or name in cands:
                return "unknown_compatible"
            # a call site naming the CLASS is the candidate for its __init__
            if name in ("__init__", "__new__") and "." in equal \
                    and equal.rsplit(".", 1)[0].split(".")[-1] in cands:
                return "unknown_compatible"
            if cf in taint_mods or (src.split("::")[0] in taint_mods):
                return "unknown_compatible"
            # implicit language-protocol dispatch (x[k], with, ==, descriptor
            # ...) has NO syntactic call site: outside the call relation's
            # domain as spec'd; classified separately, disclosed [ASM-1057]
            if name.startswith("__") and name.endswith("__") \
                    and name not in ("__init__", "__new__", "__call__"):
                return "protocol_dispatch"
            # property/descriptor invocation: attribute ACCESS runs the def
            # (no syntactic call site); decorated defs classified separately
            d = ex.modules[ef].defs.get(equal)
            if d and d.get("decorated_bad"):
                return "descriptor_or_decorated"
            return "miss"

        r = matches()
        # ---- QUERY-LEVEL soundness (the ASM-1030-relevant criterion):
        # the observed edge is a query violation ONLY if the corresponding
        # inverse query answers `proved` while missing it (fail-closed
        # blocking otherwise protects the answer)
        if not is_gen:
            if name in ("__init__", "__new__") and "." in equal:
                kq = equal.rsplit(".", 1)[0]
                stq, _, _ = world.instance_of(ef, kq)
                ok = stq != "proved" or any(
                    c == ef + "::" + kq for c in inst_by_src.get(src, ()))
            else:
                stq, listing, _ = world.callers_of(ef, equal)
                ok = stq != "proved" or src in listing
            if ok:
                qstats["covered"] += 1
            else:
                qstats["violation"] += 1
                validity_viol.append({"family": "call", "target": dst,
                                      "observed_src": src})
        if is_gen:
            stats["resumption_total"] += 1
            if r == "miss":
                stats["resumption_unmatched"] += 1
            else:
                stats[r] += 1
            continue
        stats[r] += 1
        if r == "miss" and len(misses) < 40:
            misses.append({"caller": src, "callee": dst,
                           "caller_frame": [cf, cn, cl], "callee_line": el})

    # --- imports ---
    istats = {"confirmed": 0, "unknown_compatible": 0, "miss": 0, "external": 0}
    imisses = []
    observed_importers = {}   # repo module rel -> set of importer rels
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
            rf = ex.resolve_import(mi, (name + "." + fm) if name else fm, level)
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
            elif "*" in unk_imp or (names & unk_imp) or rel in taint_mods:
                istats["unknown_compatible"] += 1
            else:
                istats["miss"] += 1
                if len(imisses) < 20:
                    imisses.append({"importer": rel, "target": t,
                                    "stmt": [name, level, list(fromlist)]})

    # imported-by completeness validity on proved answers
    for t, importers in observed_importers.items():
        st, listing, _ = world.imported_by(t)
        if st == "proved":
            for i in importers - set(listing):
                validity_viol.append({"family": "imported_by", "target": t,
                                      "observed_src": i})

    out = {"repo": repo, "pytest_exit": probe["pytest_exit"],
           "n_observed_call_edges": len(probe["call_edges"]),
           "n_observed_import_events": len(probe["import_events"]),
           "call_soundness": stats, "call_query_level": qstats,
           "call_miss_examples": misses,
           "import_soundness": istats, "import_miss_examples": imisses,
           "validity_violations": validity_viol,
           "n_validity_violations": len(validity_viol)}
    with open(out_json, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("repo", "pytest_exit",
                                          "call_soundness", "call_query_level",
                                          "import_soundness",
                                          "n_validity_violations")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
