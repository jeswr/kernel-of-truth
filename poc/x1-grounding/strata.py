#!/usr/bin/env python3
"""
X1-grounding stage 3 (PREREG §4.1-4.3): Kernel / Core / Satellites / Rest and
the construction-anomaly corridor gates. Emits strata.json.gz.

No prime information (no-peeking, PREREG §7).
"""
import argparse
import gzip
import json
import os
import sys

import x1g_lib as L


def build_in_adj(n, out_adj):
    in_adj = [[] for _ in range(n)]
    for u in range(n):
        for w in out_adj[u]:
            in_adj[w].append(u)
    return in_adj


def compute(graph):
    nodes = graph["nodes"]
    out_adj = graph["out"]
    n = len(nodes)
    single_word = graph["single_word"]
    n_sw = sum(single_word)

    in_adj = build_in_adj(n, out_adj)

    # --- Kernel (PREREG §4.1) --------------------------------------------
    kernel = L.kernel_peel(n, out_adj, in_adj)
    rest = set(range(n)) - kernel

    # --- Cycle-containment assertion (PREREG §4.1) -----------------------
    # (a) every kernel node has out-degree >= 1 within the kernel subgraph.
    min_out_ok = True
    for v in kernel:
        if not any(w in kernel for w in out_adj[v]):
            min_out_ok = False
            break
    # (b) no Rest->Kernel out-edge (guaranteed by construction; verify).
    rest_to_kernel_edges = 0
    for v in rest:
        for w in out_adj[v]:
            if w in kernel:
                rest_to_kernel_edges += 1
    # (c) Rest induced subgraph is acyclic.
    rest_acyclic = L.is_acyclic(rest, out_adj)
    cycle_containment_ok = bool(min_out_ok and rest_to_kernel_edges == 0
                                and rest_acyclic)

    # --- Core & Satellites (PREREG §4.2) ---------------------------------
    sccs = L.tarjan_scc(sorted(kernel), out_adj, alive=kernel)
    scc_sizes = sorted((len(c) for c in sccs), reverse=True)
    max_size = scc_sizes[0] if scc_sizes else 0
    second_size = scc_sizes[1] if len(scc_sizes) > 1 else 0
    largest = [c for c in sccs if len(c) == max_size]
    # tie-break: SCC containing lexicographically smallest lemma == smallest id
    # (node ids are the lexicographic rank of the lemma).
    core = min(largest, key=lambda c: min(c)) if largest else []
    core_set = set(core)
    ties = len(largest)
    satellites = kernel - core_set

    # --- Rest reachability sanity (PREREG §4.2, non-gate) ----------------
    reached = set(kernel)
    stack = list(kernel)
    while stack:
        v = stack.pop()
        for w in out_adj[v]:
            if w not in reached:
                reached.add(w)
                stack.append(w)
    rest_defined_unreachable = sum(
        1 for v in rest if len(in_adj[v]) > 0 and v not in reached)

    # --- §4.3 corridor gates ---------------------------------------------
    k_over_vsw = len(kernel) / n_sw if n_sw else 0.0
    core_over_k = len(core_set) / len(kernel) if kernel else 0.0
    core_unique_2x = (max_size >= 2 * second_size)

    gates = {
        "kOverVsw": k_over_vsw,
        "kOverVsw_range": [0.01, 0.40],
        "kOverVsw_pass": (0.01 <= k_over_vsw <= 0.40),
        "coreOverK": core_over_k,
        "coreOverK_min": 0.20,
        "coreOverK_pass": (core_over_k >= 0.20),
        "coreMaxSize": max_size,
        "secondSccSize": second_size,
        "coreUnique2x_pass": bool(core_unique_2x),
        "cycleContainment_pass": cycle_containment_ok,
        "cycleContainment_detail": {
            "kernelMinOutDegreeOk": bool(min_out_ok),
            "restToKernelEdges": rest_to_kernel_edges,
            "restAcyclic": bool(rest_acyclic),
        },
    }
    anomaly = not (gates["kOverVsw_pass"] and gates["coreOverK_pass"]
                   and gates["coreUnique2x_pass"] and gates["cycleContainment_pass"])

    strata = {
        "schema": "x1g-strata/1",
        "inputsSha256": graph.get("inputsSha256", {}),
        "V": n,
        "V_sw": n_sw,
        "kernelSize": len(kernel),
        "coreSize": len(core_set),
        "satellitesSize": len(satellites),
        "restSize": len(rest),
        "sccCount": len(sccs),
        "sccSizesTop20": scc_sizes[:20],
        "coreTieCount": ties,
        "restDefinedUnreachableCount": rest_defined_unreachable,
        "gates": gates,
        "constructionAnomaly": bool(anomaly),
        "kernel": sorted(kernel),
        "core": sorted(core_set),
        "satellites": sorted(satellites),
    }
    return strata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default=os.path.join(L.HERE, "graph.json.gz"))
    ap.add_argument("--out", default=os.path.join(L.HERE, "strata.json.gz"))
    args = ap.parse_args()

    with gzip.open(args.graph, "rt") as f:
        graph = json.loads(f.read())
    strata = compute(graph)

    with gzip.open(args.out, "wt") as f:
        f.write(json.dumps(strata, sort_keys=True, separators=(",", ":")))
        f.write("\n")

    g = strata["gates"]
    print("strata: |V|=%d |V_sw|=%d |K|=%d |Core|=%d |Sat|=%d |Rest|=%d" % (
        strata["V"], strata["V_sw"], strata["kernelSize"], strata["coreSize"],
        strata["satellitesSize"], strata["restSize"]))
    print("  gate |K|/|V_sw|      = %.4f  in[0.01,0.40] -> %s" % (
        g["kOverVsw"], g["kOverVsw_pass"]))
    print("  gate |Core|/|K|      = %.4f  >=0.20        -> %s" % (
        g["coreOverK"], g["coreOverK_pass"]))
    print("  gate Core unique 2x  = %d vs %d            -> %s" % (
        g["coreMaxSize"], g["secondSccSize"], g["coreUnique2x_pass"]))
    print("  gate cycle-contain   =                     -> %s (%s)" % (
        g["cycleContainment_pass"], g["cycleContainment_detail"]))
    if strata["constructionAnomaly"]:
        print("VERDICT: CONSTRUCTION-ANOMALY (a §4.3 gate tripped) -- STOP",
              file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
