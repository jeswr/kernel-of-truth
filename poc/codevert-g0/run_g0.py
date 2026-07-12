#!/usr/bin/env python3
"""CODEVERT G0 runner — extraction + full-census kappa_q^indep + resources.

MEASURED outputs (results/g0-metrics.json):
  - kappa_q^indep per family x repo over the FULL frozen census (population
    value on the pinned pool — no sampling error on the pool itself);
  - repo-cluster bootstrap CI (n=6 clusters, 10k resamples, seed-pinned) for
    the pooled figures — the honest generalization uncertainty; wide by
    construction and disclosed as such;
  - unknown-edge mass by construct family (reason code), share unrestricted;
  - identifier-collision / candidate-set-growth stats;
  - resource facts: extraction wall time, peak RSS, SQLite packed store
    bytes, bytes/edge, per-family query latency p50/p95 (this Python
    reference engine, pinned 2-core rig, nice -n 10).
Statuses: proved counts toward kappa; unknown_incomplete / target_not_found
do not. proved-EMPTY negatives count as proved (valid negative answers).
"""
import json, os, random, resource, sqlite3, sys, time

sys.setrecursionlimit(100000)
from extractor import Extractor
from engine import World, run_query

BASE = os.path.dirname(os.path.abspath(__file__))
BOOT_SEED = 20260711
FAMILIES = ["callees_of", "imports_of", "contains", "contained_in",
            "callers_of", "imported_by", "where_defined", "instance_of"]
FORWARD = set(FAMILIES[:4])


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def store_sqlite(path, edges):
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE edges (rel TEXT, src TEXT, dst TEXT, status TEXT,"
                " cand TEXT, file TEXT, span_a INT, span_b INT, reason TEXT)")
    con.executemany("INSERT INTO edges VALUES (?,?,?,?,?,?,?,?,?)",
                    [e.row() for e in edges])
    con.execute("CREATE INDEX ix_dst ON edges(rel, dst)")
    con.execute("CREATE INDEX ix_src ON edges(rel, src)")
    con.commit()
    con.execute("VACUUM")
    con.close()
    return os.path.getsize(path)


def main():
    exclude_tests = os.environ.get("G0_EXCLUDE_TESTS") == "1"
    census = json.load(open(os.path.join(BASE, "results", "census.json")))
    out = {"repos": {}, "pooled": {}}
    per_repo_family = {}       # repo -> family -> (proved, total)
    lat = {f: [] for f in FAMILIES}
    all_unknown = {}
    unrestricted = {"call": 0, "import": 0, "binding": 0, "instantiate": 0}
    unknown_by_rel = {"call": 0, "import": 0, "binding": 0, "instantiate": 0}
    cand_growth = []           # (repo, cand_name, n_defs_with_that_name)
    tot_edges = tot_proved = tot_unknown = 0
    tot_store = 0

    for repo, cdata in sorted(census["repos"].items()):
        root = os.path.join(BASE, "corpus", repo)
        t0 = time.time()
        ex = Extractor(root, repo)
        edges = ex.extract()
        t_extract = time.time() - t0
        world = World(edges, ex.modules)
        store_bytes = store_sqlite(os.path.join(BASE, "results",
                                                repo + ".sqlite"), edges)
        tot_store += store_bytes

        # --- edge stats ---
        n_p = sum(1 for e in edges if e.status == "proved")
        n_u = len(edges) - n_p
        tot_edges += len(edges)
        tot_proved += n_p
        tot_unknown += n_u
        reasons = {}
        for e in edges:
            if e.status == "unknown":
                reasons[e.reason] = reasons.get(e.reason, 0) + 1
                all_unknown[e.reason] = all_unknown.get(e.reason, 0) + 1
                if e.rel in unknown_by_rel:
                    unknown_by_rel[e.rel] += 1
                    if e.cand == "*":
                        unrestricted[e.rel] += 1

        # --- candidate-set growth: for unknown call candidates, how many
        # same-named defs exist in the repo (ambiguity-set pressure) ---
        name_def_count = {}
        for mi in ex.modules.values():
            for qual in mi.defs:
                nm = qual.split(".")[-1]
                name_def_count[nm] = name_def_count.get(nm, 0) + 1
        seen_c = {}
        for e in edges:
            if e.status == "unknown" and e.rel == "call" and e.cand and e.cand != "*":
                seen_c[e.cand] = name_def_count.get(e.cand, 0)
        for c, n in seen_c.items():
            cand_growth.append((repo, c, n))

        # --- full-census kappa per family + latency ---
        fam_stats = {}
        from extractor import _is_test_path
        for fam in FAMILIES:
            u = cdata["universes"][fam]
            if exclude_tests:
                u = [t for t in u if "file" not in t or not _is_test_path(t["file"])]
                if fam == "where_defined":
                    u = []  # name-keyed; not file-stratifiable, disclosed
            proved = 0
            statuses = {"proved": 0, "unknown_incomplete": 0,
                        "target_not_found": 0, "proved_empty": 0}
            t_fam = []
            for tgt in u:
                q0 = time.perf_counter()
                st, listing, blocking = run_query(world, fam, tgt)
                t_fam.append(time.perf_counter() - q0)
                if st == "proved":
                    proved += 1
                    statuses["proved"] += 1
                    if not listing:
                        statuses["proved_empty"] += 1
                else:
                    statuses[st] += 1
            fam_stats[fam] = {"n": len(u), "proved": proved,
                              "kappa": proved / len(u) if u else None,
                              "statuses": statuses}
            if not u:
                fam_stats[fam]["kappa"] = 0.0  # placeholder; excluded from macro below
            lat[fam].extend(t_fam)
        per_repo_family[repo] = {f: (fam_stats[f]["proved"], fam_stats[f]["n"])
                                 for f in FAMILIES}
        out["repos"][repo] = {
            "extract_wall_s": round(t_extract, 3),
            "n_modules": len(ex.modules),
            "n_parsed": sum(1 for m in ex.modules.values() if m.parsed),
            "edges_total": len(edges), "edges_proved": n_p, "edges_unknown": n_u,
            "unknown_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
            "sqlite_bytes": store_bytes,
            "bytes_per_edge": round(store_bytes / len(edges), 1) if edges else None,
            "exec_tainted_modules": [m.rel for m in ex.modules.values()
                                     if m.parsed and m.exec_taint],
            "star_import_modules": [m.rel for m in ex.modules.values()
                                    if m.parsed and m.star_import],
            "families": fam_stats,
            "extractor_stats": dict(ex.stats),
        }
        print(repo, "edges=%d (proved %d / unknown %d) store=%dB" %
              (len(edges), n_p, n_u, store_bytes),
              {f: round(fam_stats[f]["kappa"], 3) for f in FAMILIES}, flush=True)

    # ---------- pooled kappa ----------
    def pooled(repos):
        agg_q = [0, 0]          # query-pooled
        fam_p = {f: [0, 0] for f in FAMILIES}
        for r in repos:
            for f in FAMILIES:
                p, n = per_repo_family[r][f]
                agg_q[0] += p
                agg_q[1] += n
                fam_p[f][0] += p
                fam_p[f][1] += n
        nfam = sum(1 for f in FAMILIES if fam_p[f][1])
        macro = sum((fam_p[f][0] / fam_p[f][1]) for f in FAMILIES
                    if fam_p[f][1]) / nfam
        return agg_q[0] / agg_q[1], macro, {f: (fam_p[f][0] / fam_p[f][1])
                                            for f in FAMILIES if fam_p[f][1]}

    repos = sorted(per_repo_family)
    k_query, k_macro, k_fam = pooled(repos)

    rng = random.Random(BOOT_SEED)
    boots_q, boots_m = [], []
    for _ in range(10000):
        sample = [repos[rng.randrange(len(repos))] for _ in repos]
        q, m, _ = pooled(sample)
        boots_q.append(q)
        boots_m.append(m)
    boots_q.sort()
    boots_m.sort()

    def ci(v):
        return [round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v)) - 1], 4)]

    out["pooled"] = {
        "kappa_q_indep_query_pooled": round(k_query, 4),
        "kappa_q_indep_query_pooled_ci95_repo_cluster_bootstrap": ci(boots_q),
        "kappa_q_indep_family_macro": round(k_macro, 4),
        "kappa_q_indep_family_macro_ci95_repo_cluster_bootstrap": ci(boots_m),
        "kappa_by_family_pooled": {f: round(v, 4) for f, v in k_fam.items()},
        "kappa_forward_families_pooled": round(
            sum(k_fam.get(f, 0) for f in FAMILIES if f in FORWARD)
            / max(1, sum(1 for f in FORWARD if f in k_fam)), 4),
        "kappa_inverse_families_pooled": round(
            sum(k_fam.get(f, 0) for f in FAMILIES if f not in FORWARD)
            / max(1, sum(1 for f in FAMILIES if f not in FORWARD and f in k_fam)), 4),
        "n_census_queries_total": sum(n for r in repos
                                      for _, n in per_repo_family[r].values()),
        "bootstrap": {"seed": BOOT_SEED, "resamples": 10000, "clusters": len(repos),
                      "note": "repo-level cluster bootstrap; n=6 clusters -> wide CI, honest"},
        "edges": {"total": tot_edges, "proved": tot_proved, "unknown": tot_unknown,
                  "disproved": 0, "conflict": 0,
                  "unknown_share": round(tot_unknown / tot_edges, 4)},
        "unknown_by_reason": dict(sorted(all_unknown.items(), key=lambda kv: -kv[1])),
        "unknown_by_relation": unknown_by_rel,
        "unrestricted_unknowns_by_relation": unrestricted,
        "store_bytes_total": tot_store,
        "bytes_per_edge_pooled": round(tot_store / tot_edges, 1),
    }

    # candidate-set growth summary
    grow = sorted((n for _, _, n in cand_growth), reverse=True)
    n_multi = sum(1 for n in grow if n > 1)
    out["candidate_set_growth"] = {
        "n_distinct_unknown_call_candidates": len(grow),
        "share_matching_ge1_repo_def": round(
            sum(1 for n in grow if n >= 1) / len(grow), 4) if grow else None,
        "share_matching_ge2_repo_defs": round(n_multi / len(grow), 4) if grow else None,
        "max_same_name_defs": grow[0] if grow else 0,
        "top10": sorted(cand_growth, key=lambda x: -x[2])[:10],
    }

    # latency percentiles (population census reruns)
    lat_out = {}
    for f in FAMILIES:
        v = sorted(lat[f])
        if v:
            lat_out[f] = {"n": len(v),
                          "p50_us": round(v[len(v) // 2] * 1e6, 1),
                          "p95_us": round(v[int(len(v) * 0.95)] * 1e6, 1),
                          "max_ms": round(v[-1] * 1e3, 3)}
    out["latency_python_reference_engine"] = lat_out
    out["peak_rss_mb"] = round(rss_mb(), 1)
    out["rig"] = {"host": "2 shared vCPU EC2 (programme pinned box)",
                  "nice": 10, "python": sys.version.split()[0],
                  "note": "latency is for THIS Python dict-index reference engine, not the measured 5.29-7.82us compiled a5 engine; comparable only to itself"}

    outname = "g0-metrics-srconly.json" if exclude_tests else "g0-metrics.json"
    with open(os.path.join(BASE, "results", outname), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["pooled"], indent=1))
    print("peak RSS MB:", out["peak_rss_mb"])


if __name__ == "__main__":
    main()
