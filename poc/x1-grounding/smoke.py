#!/usr/bin/env python3
"""
X1-grounding self-test (PREREG §7). MUST pass before stage 1 runs on real data.
1) toy dictionary fixture with hand-computed truth (Kernel/Core/Satellites,
   >=2 distinct minimal grounding sets, each verified grounding + minimal);
2) ~30 Morphy-lite spot checks;
3) real-slice run (first 2000 noun synsets): non-empty kernel + determinism.
Exits nonzero on any failure.
"""
import json
import os
import sys
import time

import x1g_lib as L
import fvs
import strata as strata_mod
import build_graph

HERE = L.HERE
FIX = os.path.join(HERE, "fixtures")
fails = []


def check(cond, msg):
    status = "ok " if cond else "FAIL"
    print("  [%s] %s" % (status, msg))
    if not cond:
        fails.append(msg)


# ---------------------------------------------------------------------------
def smoke_toy():
    print("[1] toy dictionary fixture")
    toy = json.load(open(os.path.join(FIX, "toy_dict.json")))
    exp = json.load(open(os.path.join(FIX, "toy_expected.json")))
    vocab = sorted(toy["vocab"])
    nid = {v: i for i, v in enumerate(vocab)}
    n = len(vocab)
    out = [[] for _ in range(n)]
    for u, w in toy["edges"]:
        out[nid[u]].append(nid[w])
    for i in range(n):
        out[i] = sorted(set(out[i]))
    graph = {"nodes": vocab, "out": out, "single_word": [1] * n,
             "inputsSha256": {}}
    st = strata_mod.compute(graph)
    names = lambda ids: sorted(vocab[i] for i in ids)
    check(names(st["kernel"]) == sorted(exp["kernel"]),
          "kernel == expected %s (got %s)" % (exp["kernel"], names(st["kernel"])))
    check(names(st["core"]) == sorted(exp["core"]),
          "core == expected %s (got %s)" % (exp["core"], names(st["core"])))
    check(names(st["satellites"]) == sorted(exp["satellites"]),
          "satellites == expected %s (got %s)" % (
              exp["satellites"], names(st["satellites"])))
    rest = sorted(set(vocab) - set(names(st["kernel"])))
    check(rest == sorted(exp["rest"]), "rest == expected %s (got %s)" % (
        exp["rest"], rest))
    check(st["kernelSize"] < n, "kernel strictly smaller than vocabulary")
    check(st["gates"]["secondSccSize"] == exp["secondSccSize"],
          "second SCC size == %d" % exp["secondSccSize"])
    check(st["gates"]["cycleContainment_pass"], "cycle-containment holds")

    # FVS sampling over 20 seeds.
    inv, loc, kout, kin = fvs.build_kernel_subgraph(st["kernel"], out)
    m = len(inv)
    distinct = set()
    all_grounding = True
    all_minimal = True
    all_size = True
    for seed in range(20):
        Fg, Fl = fvs.sample_fvs(inv, kout, kin, seed)
        g, mn = fvs.verify_grounding_and_minimal(m, kout, Fl)
        all_grounding = all_grounding and g
        all_minimal = all_minimal and mn
        all_size = all_size and (len(Fg) == exp["minFvsSize"])
        distinct.add(frozenset(vocab[i] for i in Fg))
    check(all_grounding, "every sampled set is a verified grounding set")
    check(all_minimal, "every sampled set is inclusion-minimal")
    check(all_size, "every sampled set has size == minFvsSize (%d)" % exp["minFvsSize"])
    check(len(distinct) >= 2, "at least 2 distinct minimal grounding sets (got %d): %s" % (
        len(distinct), sorted(sorted(s) for s in distinct)))


# ---------------------------------------------------------------------------
def smoke_morphy():
    print("[2] Morphy-lite spot checks")
    per_pos, union = L.load_index()
    exc = L.load_exc()
    morphy = L.Morphy(per_pos, union, exc)
    cases = json.load(open(os.path.join(FIX, "morphy_spotchecks.json")))["cases"]
    n_ok = 0
    for tok, expected in cases:
        got = morphy.resolve(tok)
        ok = (got == expected)
        n_ok += ok
        if not ok:
            check(False, "morphy(%r) == %r (got %r)" % (tok, expected, got))
    check(n_ok == len(cases), "%d/%d Morphy spot checks pass" % (n_ok, len(cases)))


# ---------------------------------------------------------------------------
def smoke_slice():
    print("[3] real-slice run (first 2000 noun synsets)")
    t0 = time.time()
    g1, s1 = build_graph.build(noun_limit=2000, pos_subset=["noun"])
    dt = time.time() - t0
    ser1 = json.dumps(g1, sort_keys=True, separators=(",", ":"))
    g2, s2 = build_graph.build(noun_limit=2000, pos_subset=["noun"])
    ser2 = json.dumps(g2, sort_keys=True, separators=(",", ":"))
    check(ser1 == ser2, "graph output byte-identical across re-run (determinism)")
    # stats carry volatile metadata (build timestamp/seconds); compare content.
    volatile = ("builtAt", "buildSeconds")
    s1c = {k: v for k, v in s1.items() if k not in volatile}
    s2c = {k: v for k, v in s2.items() if k not in volatile}
    check(json.dumps(s1c, sort_keys=True) == json.dumps(s2c, sort_keys=True),
          "stats content identical across re-run (excl. timestamp/timing)")
    check(s1["edgeCount"] > 0, "slice produced edges (%d)" % s1["edgeCount"])
    # kernel of the slice
    n = len(g1["nodes"])
    in_adj = strata_mod.build_in_adj(n, g1["out"])
    kernel = L.kernel_peel(n, g1["out"], in_adj)
    print("    slice: V=%d edges=%d kernelSize=%d (%.1fs/run)" % (
        n, s1["edgeCount"], len(kernel), dt))
    check(len(kernel) > 0, "slice kernel is non-empty (%d nodes)" % len(kernel))


def main():
    smoke_toy()
    smoke_morphy()
    smoke_slice()
    print()
    if fails:
        print("SMOKE FAILED (%d):" % len(fails))
        for m in fails:
            print("  -", m)
        sys.exit(1)
    print("SMOKE PASSED")


if __name__ == "__main__":
    main()
