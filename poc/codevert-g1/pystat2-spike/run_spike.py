#!/usr/bin/env python3
"""PY-STAT/2-SPIKE runner (NON-SCORED; CODEVERT issue #16 option C).

Measures, on the FROZEN G0 census (poc/codevert-g0/results/census.json,
read-only) and the pinned G0 corpus (read-only):
  1. unrestricted '*' unknown call/instantiate mass, PY-STAT/1 vs
     PY-STAT/2-SPIKE, by source reason code + conversion counts (D1/D2/D3);
  2. kappa_q^indep per family x repo for BOTH extractors, same
     proved-counting rule as run_g0.py (proved-EMPTY counts as proved);
     pooled query-pooled + family-macro;
  3. soundness guard: probe re-check on the saved dynamic traces
     (probe_recheck.py) — proved-answer validity + NEW candidate-narrowing
     misses;
  4. wall time + peak RSS.
HARD ASSERTION: the PY-STAT/2-SPIKE proved-edge set is IDENTICAL to
PY-STAT/1 on every repo (the spike only changes unknown-edge candidates).
All outputs -> poc/codevert-g1/pystat2-spike/results/. Nothing under
poc/codevert-g0/ is modified.
"""
import json, os, resource, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.abspath(os.path.join(BASE, "..", "..", "codevert-g0"))
sys.path.insert(0, G0)
sys.path.insert(0, BASE)
sys.setrecursionlimit(100000)

from extractor import Extractor as Ex1        # PY-STAT/1 (read-only, from g0)
from extractor2 import Extractor as Ex2       # PY-STAT/2-SPIKE (this dir)
from engine import World, run_query           # g0 engine, read-only
import probe_recheck

FAMILIES = ["callees_of", "imports_of", "contains", "contained_in",
            "callers_of", "imported_by", "where_defined", "instance_of"]
FORWARD = set(FAMILIES[:4])
INVERSE = ["callers_of", "instance_of", "imported_by", "where_defined"]
STAR_CALL_REASONS = None    # report all reasons seen


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def star_by_reason(edges):
    out = {}
    for e in edges:
        if e.status == "unknown" and e.rel in ("call", "instantiate") \
                and e.cand == "*":
            out[e.reason] = out.get(e.reason, 0) + 1
    return out


def fam_kappa(world, cdata):
    """run_g0.py proved-counting rule over the full frozen census."""
    fam_stats = {}
    blocking_means = {}
    for fam in FAMILIES:
        u = cdata["universes"][fam]
        proved = 0
        statuses = {"proved": 0, "unknown_incomplete": 0,
                    "target_not_found": 0, "proved_empty": 0}
        btot = 0
        for tgt in u:
            st, listing, blocking = run_query(world, fam, tgt)
            btot += blocking
            if st == "proved":
                proved += 1
                statuses["proved"] += 1
                if not listing:
                    statuses["proved_empty"] += 1
            else:
                statuses[st] += 1
        fam_stats[fam] = {"n": len(u), "proved": proved,
                          "kappa": proved / len(u) if u else 0.0,
                          "statuses": statuses}
        blocking_means[fam] = round(btot / len(u), 2) if u else None
    return fam_stats, blocking_means


def pooled(per_repo_family, repos):
    agg_q = [0, 0]
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
    return (agg_q[0] / agg_q[1], macro,
            {f: (fam_p[f][0] / fam_p[f][1]) for f in FAMILIES if fam_p[f][1]})


def main():
    t_start = time.time()
    census = json.load(open(os.path.join(G0, "results", "census.json")))
    ablation = json.load(open(os.path.join(G0, "results",
                                           "g0-ablation-unrestricted.json")))
    resdir = os.path.join(BASE, "results")
    os.makedirs(resdir, exist_ok=True)

    out = {"label": "PY-STAT/2-SPIKE (NON-SCORED)", "repos": {},
           "proved_set_identical_all_repos": True}
    per_repo_family = {"v1": {}, "v2": {}}
    conv_tot = {}
    star_tot = {"v1": 0, "v2": 0}
    probe_summary = {"n_new_misses_nongen": 0, "n_new_misses_generator": 0,
                     "n_validity_violations_v1": 0,
                     "n_validity_violations_v2": 0, "per_repo": {}}

    for repo, cdata in sorted(census["repos"].items()):
        root = os.path.join(G0, "corpus", repo)
        t0 = time.time()
        ex1 = Ex1(root, repo)
        edges1 = ex1.extract()
        t1 = time.time()
        ex2 = Ex2(root, repo)
        edges2 = ex2.extract()
        t2 = time.time()

        # ---- HARD ASSERTION: identical proved-edge sets ----
        p1 = sorted(e.row() for e in edges1 if e.status == "proved")
        p2 = sorted(e.row() for e in edges2 if e.status == "proved")
        assert p1 == p2, "proved-edge sets differ on %s" % repo

        world1 = World(edges1, ex1.modules)
        world2 = World(edges2, ex2.modules)

        s1, s2 = star_by_reason(edges1), star_by_reason(edges2)
        n1, n2 = sum(s1.values()), sum(s2.values())
        star_tot["v1"] += n1
        star_tot["v2"] += n2
        conv = {k: v for k, v in ex2.stats.items() if k.startswith("d")}
        for k, v in conv.items():
            conv_tot[k] = conv_tot.get(k, 0) + v

        f1, b1 = fam_kappa(world1, cdata)
        f2, b2 = fam_kappa(world2, cdata)
        per_repo_family["v1"][repo] = {f: (f1[f]["proved"], f1[f]["n"])
                                       for f in FAMILIES}
        per_repo_family["v2"][repo] = {f: (f2[f]["proved"], f2[f]["n"])
                                       for f in FAMILIES}

        pr = probe_recheck.recheck(
            repo, ex1, edges1, world1, ex2, edges2, world2,
            os.path.join(G0, "results", "probe", repo + ".trace.json"),
            os.path.join(resdir, repo + ".probe-recheck.json"))
        for k in ("n_new_misses_nongen", "n_new_misses_generator",
                  "n_validity_violations_v1", "n_validity_violations_v2"):
            probe_summary[k] += pr[k]
        probe_summary["per_repo"][repo] = {
            "miss_v1": pr["call_soundness_v1"]["miss"],
            "miss_v2": pr["call_soundness_v2"]["miss"],
            "new_misses_nongen": pr["n_new_misses_nongen"],
            "new_misses_generator": pr["n_new_misses_generator"],
            "query_violations_v1": pr["call_query_level_v1"]["violation"],
            "query_violations_v2": pr["call_query_level_v2"]["violation"],
            "import_miss_v1": pr["import_soundness_v1"]["miss"],
            "import_miss_v2": pr["import_soundness_v2"]["miss"]}

        out["repos"][repo] = {
            "extract_wall_s_v1": round(t1 - t0, 3),
            "extract_wall_s_v2": round(t2 - t1, 3),
            "edges_total_v1": len(edges1), "edges_total_v2": len(edges2),
            "unrestricted_call_inst_v1": n1,
            "unrestricted_call_inst_v2": n2,
            "unrestricted_by_reason_v1": dict(sorted(s1.items())),
            "unrestricted_by_reason_v2": dict(sorted(s2.items())),
            "pct_unrestricted_converted": round(100.0 * (n1 - n2) / n1, 2)
            if n1 else None,
            "conversions": conv,
            "kappa_v1": {f: round(f1[f]["kappa"], 4) for f in FAMILIES},
            "kappa_v2": {f: round(f2[f]["kappa"], 4) for f in FAMILIES},
            "statuses_v2": {f: f2[f]["statuses"] for f in FAMILIES},
            "mean_blocking_v1": b1, "mean_blocking_v2": b2,
            "ablation_ceiling": ablation.get(repo, {}).get("ablated", {}),
        }
        print(repo, "'*' %d -> %d (-%.1f%%)" % (n1, n2,
              100.0 * (n1 - n2) / n1 if n1 else 0.0),
              "conv:", conv, flush=True)
        print("   kappa v1", {f: round(f1[f]["kappa"], 3) for f in INVERSE})
        print("   kappa v2", {f: round(f2[f]["kappa"], 3) for f in INVERSE})

    repos = sorted(out["repos"])
    pooled_out = {}
    for tag in ("v1", "v2"):
        kq, km, kf = pooled(per_repo_family[tag], repos)
        pooled_out[tag] = {
            "kappa_q_indep_query_pooled": round(kq, 4),
            "kappa_q_indep_family_macro": round(km, 4),
            "kappa_by_family_pooled": {f: round(v, 4) for f, v in kf.items()},
            "kappa_inverse_families_macro": round(
                sum(kf[f] for f in FAMILIES if f not in FORWARD)
                / sum(1 for f in FAMILIES if f not in FORWARD), 4),
        }
    out["pooled"] = pooled_out
    out["unrestricted_call_inst_pooled"] = dict(
        star_tot, pct_converted=round(
            100.0 * (star_tot["v1"] - star_tot["v2"]) / star_tot["v1"], 2))
    out["conversions_pooled"] = conv_tot

    # ---- ablation-headroom recovery (callers_of etc., per repo) ----
    recov = {}
    for repo in repos:
        r = {}
        for fam in INVERSE:
            k1 = out["repos"][repo]["kappa_v1"][fam]
            k2 = out["repos"][repo]["kappa_v2"][fam]
            ab = out["repos"][repo]["ablation_ceiling"].get(fam)
            if ab is not None and ab > k1:
                r[fam] = {"v1": k1, "v2": k2, "ablation": ab,
                          "headroom_recovered": round((k2 - k1) / (ab - k1), 4)}
        recov[repo] = r
    out["ablation_headroom_recovery"] = recov
    out["probe_guard"] = probe_summary
    out["wall_s_total"] = round(time.time() - t_start, 1)
    out["peak_rss_mb"] = round(rss_mb(), 1)
    out["rig"] = {"host": "2 shared vCPU EC2 (programme pinned box)",
                  "nice": 10, "python": sys.version.split()[0]}
    out["governance"] = ("NON-SCORED spike; no kappa here is verdict "
                         "evidence; extractor version change per ASM-1031 "
                         "would require new inventory + G1 rerun.")

    with open(os.path.join(resdir, "spike-metrics.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({"pooled": out["pooled"],
                      "unrestricted": out["unrestricted_call_inst_pooled"],
                      "conversions": conv_tot,
                      "probe_guard": {k: v for k, v in probe_summary.items()
                                      if k != "per_repo"}}, indent=1))
    print("wall_s", out["wall_s_total"], "peak RSS MB:", out["peak_rss_mb"])


if __name__ == "__main__":
    main()
