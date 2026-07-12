#!/usr/bin/env python3
"""CODEVERT G1-FORWARD runner — PY-STAT/1 (byte-identical G0 extractor) on the
pinned G1 pool; kappa_q^indep over the FULL frozen G1 census (census-g1.json,
seed 20260716). Primary aggregate = FL-4 {contains, contained_in, imports_of,
where_defined} per DESIGN-PIN.md sect 1 [PROPOSED-ASM: ASM-1110/1112];
callees_of co-reported as the pinned sensitivity slice; all 8 families
co-reported for disclosure. Adapted from ../codevert-g0/run_g0.py (logic
identical; paths/seed/aggregates/report keys only).
"""
import json, os, random, resource, sqlite3, sys, time

sys.setrecursionlimit(100000)
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "codevert-g0"))
from extractor import Extractor, _is_test_path  # pinned sha b508d844...
from engine import World, run_query             # pinned sha 4b62413d...

BOOT_SEED = 20260716
FAMILIES = ["callees_of", "imports_of", "contains", "contained_in",
            "callers_of", "imported_by", "where_defined", "instance_of"]
FL4 = {"contains", "contained_in", "imports_of", "where_defined"}
SENS = "callees_of"


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
    census = json.load(open(os.path.join(BASE, "results", "census-g1.json")))
    out = {"repos": {}, "pooled": {}}
    per_repo_family = {}
    all_unknown = {}
    unrestricted = {"call": 0, "import": 0, "binding": 0, "instantiate": 0}
    unknown_by_rel = {"call": 0, "import": 0, "binding": 0, "instantiate": 0}
    tot_edges = tot_proved = tot_unknown = 0
    tot_store = 0
    t_all = time.time()

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

        fam_stats = {}
        for fam in FAMILIES:
            u = cdata["universes"][fam]
            if exclude_tests:
                u = [t for t in u if "file" not in t or not _is_test_path(t["file"])]
                if fam == "where_defined":
                    u = []  # name-keyed; not file-stratifiable, disclosed (as G0)
            proved = 0
            statuses = {"proved": 0, "unknown_incomplete": 0,
                        "target_not_found": 0, "proved_empty": 0}
            for tgt in u:
                st, listing, blocking = run_query(world, fam, tgt)
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
        per_repo_family[repo] = {f: (fam_stats[f]["proved"], fam_stats[f]["n"])
                                 for f in FAMILIES}
        out["repos"][repo] = {
            "extract_wall_s": round(t_extract, 3),
            "n_modules": len(ex.modules),
            "n_parsed": sum(1 for m in ex.modules.values() if m.parsed),
            "edges_total": len(edges), "edges_proved": n_p, "edges_unknown": n_u,
            "unknown_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
            "sqlite_bytes": store_bytes,
            "exec_tainted_modules": [m.rel for m in ex.modules.values()
                                     if m.parsed and m.exec_taint],
            "families": fam_stats,
        }
        print(repo, "edges=%d (p%d/u%d)" % (len(edges), n_p, n_u),
              {f: (round(fam_stats[f]["kappa"], 3)
                   if fam_stats[f]["kappa"] is not None else None)
               for f in FAMILIES}, flush=True)

    def pooled(repos, fams):
        agg = [0, 0]
        fam_p = {f: [0, 0] for f in fams}
        for r in repos:
            for f in fams:
                p, n = per_repo_family[r][f]
                agg[0] += p
                agg[1] += n
                fam_p[f][0] += p
                fam_p[f][1] += n
        nfam = sum(1 for f in fams if fam_p[f][1])
        macro = sum((fam_p[f][0] / fam_p[f][1]) for f in fams
                    if fam_p[f][1]) / nfam if nfam else None
        return (agg[0] / agg[1] if agg[1] else None), macro, \
            {f: (fam_p[f][0] / fam_p[f][1]) for f in fams if fam_p[f][1]}

    repos = sorted(per_repo_family)
    fl_fams = sorted(FL4)
    k_q_fl, k_m_fl, k_fam_fl = pooled(repos, fl_fams)
    k_q_all, k_m_all, k_fam_all = pooled(repos, FAMILIES)

    rng = random.Random(BOOT_SEED)
    boots = {"fl_q": [], "fl_m": [], "all_q": [], "all_m": []}
    for _ in range(10000):
        sample = [repos[rng.randrange(len(repos))] for _ in repos]
        q, m, _ = pooled(sample, fl_fams)
        boots["fl_q"].append(q)
        boots["fl_m"].append(m)
        q, m, _ = pooled(sample, FAMILIES)
        boots["all_q"].append(q)
        boots["all_m"].append(m)

    def ci(v):
        v = sorted(v)
        return [round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v)) - 1], 4)]

    out["pooled"] = {
        "PRIMARY_kappa_q_indep_FL4_query_pooled": round(k_q_fl, 4),
        "PRIMARY_kappa_q_indep_FL4_query_pooled_band95": ci(boots["fl_q"]),
        "PRIMARY_kappa_q_indep_FL4_family_macro": round(k_m_fl, 4),
        "PRIMARY_kappa_q_indep_FL4_family_macro_band95": ci(boots["fl_m"]),
        "kappa_by_family_pooled": {f: round(v, 4) for f, v in k_fam_all.items()},
        "SENSITIVITY_callees_of_kappa": round(k_fam_all.get(SENS), 4)
            if k_fam_all.get(SENS) is not None else None,
        "disclosure_all8_query_pooled": round(k_q_all, 4),
        "disclosure_all8_query_pooled_band95": ci(boots["all_q"]),
        "disclosure_all8_family_macro": round(k_m_all, 4),
        "n_census_queries_total": sum(n for r in repos
                                      for _, n in per_repo_family[r].values()),
        "bootstrap": {"seed": BOOT_SEED, "resamples": 10000,
                      "clusters": len(repos),
                      "note": "repo-cluster resampling SENSITIVITY band over the"
                              " agent-selected pinned pool; NOT a generalization CI"},
        "edges": {"total": tot_edges, "proved": tot_proved,
                  "unknown": tot_unknown, "disproved": 0, "conflict": 0},
        "unknown_by_reason": dict(sorted(all_unknown.items(), key=lambda kv: -kv[1])),
        "unrestricted_unknowns_by_relation": unrestricted,
        "store_bytes_total": tot_store,
        "wall_s_total": round(time.time() - t_all, 1),
    }
    out["peak_rss_mb"] = round(rss_mb(), 1)
    out["rig"] = {"host": "2 shared vCPU EC2 (programme pinned box)",
                  "nice": 10, "python": sys.version.split()[0]}
    outname = "g1-metrics-srconly.json" if exclude_tests else "g1-metrics.json"
    with open(os.path.join(BASE, "results", outname), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["pooled"], indent=1))
    print("peak RSS MB:", out["peak_rss_mb"])


if __name__ == "__main__":
    main()
