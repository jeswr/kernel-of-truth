#!/usr/bin/env python3
"""E4 pre-registered statistics + verdict (docs/poc-design.md E4 rev 2;
bead kernel-of-truth-hkp). The pre-registration artifact is
poc/e4/inputs/holdout-manifest.json `statistics`; its criteria strings are
quoted VERBATIM (loaded from the manifest itself) in the emitted verdict.

  PRIMARY   manifest.statistics.primaryEndpoint — tier-2 top-1 over the
            1,054-way candidate set, kernel vs shuffled-kernel, one-sided
            exact paired sign-flip permutation across the paired seeds,
            alpha = 0.05.
  SECONDARY manifest.statistics.secondaryEndpoints — tier-2 top-10 and
            tier-1 top-1/top-10 (same paired test, Holm over the family);
            per-seed one-sided Fisher exact on pooled item counts, Holm over
            seeds per tier; compositional subsets DESCRIPTIVE only.
  VALIDITY  manifest.statistics.controlFloorCheck — the shuffled arm's
            pooled tier-2 accuracy must sit inside the exact binomial 95%
            acceptance region of 1/|C|; otherwise INVALID, not a positive.
  ADVANCE   manifest.statistics.advanceRule (MAJOR 16).

No third-party stats deps: the exact sign-flip permutation test and Holm are
imported READ-ONLY from poc/e1/eval/stats_e1.py; Fisher exact and the
binomial acceptance region are exact (math.comb), self-contained here.
"""

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E4_DIR = os.path.dirname(HERE)
E1_DIR = os.path.join(os.path.dirname(E4_DIR), "e1")
sys.path.insert(0, os.path.join(E1_DIR, "eval"))
from stats_e1 import holm, paired_permutation_one_sided  # noqa: E402  (read-only reuse)

ARMS = ("kernel", "shuffled", "random")


def fisher_one_sided(k1, n1, k2, n2):
    """Exact Fisher test, H1: rate(arm1) > rate(arm2). Hypergeometric upper tail."""
    K, N = k1 + k2, n1 + n2
    denom = math.comb(N, K)
    lo, hi = max(0, K - n2), min(K, n1)
    p = sum(math.comb(n1, x) * math.comb(n2, K - x) for x in range(max(k1, lo), hi + 1)) / denom
    return {"k": [k1, k2], "n": [n1, n2], "p": min(1.0, p),
            "test": "one-sided Fisher exact (pooled items, kernel > shuffled)"}


def binom_acceptance(n, p0, alpha=0.05):
    """Equal-tailed exact binomial acceptance region [lo, hi] under rate p0:
    lo = smallest k with P(X<=k) > alpha/2; hi = smallest k with
    P(X<=k) >= 1-alpha/2. A count inside [lo, hi] is consistent with p0."""
    cdf, c = [], 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * (p0 ** k) * ((1 - p0) ** (n - k))
        cdf.append(min(c, 1.0))
    lo = next(k for k in range(n + 1) if cdf[k] > alpha / 2)
    hi = next(k for k in range(n + 1) if cdf[k] >= 1 - alpha / 2)
    return lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evals", required=True, help="dir with eval-e4-<arm>-seed<S>.json")
    ap.add_argument("--manifest", default=os.path.join(E4_DIR, "inputs", "holdout-manifest.json"))
    ap.add_argument("--meta", required=True, help="build_emission.py meta.json (OOV rate etc.)")
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--out-prefix", required=True)
    ap.add_argument("--mock", action="store_true",
                    help="label the verdict as a MOCK pipeline check, not a result")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    with open(args.manifest) as f:
        manifest = json.load(f)
    if manifest.get("artifact") != "e4-holdout-manifest":
        raise SystemExit("ERR_ARTIFACT: not an e4-holdout-manifest")
    spec = manifest["statistics"]
    with open(args.meta) as f:
        meta = json.load(f)
    if bool(meta.get("mock")) != args.mock:
        raise SystemExit(f"ERR_MOCK: data meta mock={meta.get('mock')} but stats --mock={args.mock}")

    db = {}
    for path in sorted(glob.glob(os.path.join(args.evals, "eval-e4-*.json"))):
        with open(path) as f:
            e = json.load(f)
        db[(e["arm"], e["seed"])] = e

    def ev(arm, seed):
        e = db.get((arm, seed))
        if e is None:
            raise SystemExit(f"ERR_MISSING_EVAL: ({arm}, seed {seed})")
        return e

    n_cand = ev("kernel", seeds[0])["candidateSetSize"]
    if n_cand != spec["candidateSetSize"] and not args.mock:
        raise SystemExit(f"ERR_CANDIDATES: {n_cand} != pre-registered {spec['candidateSetSize']}")

    def series(arm, tier, key):
        out = []
        for s in seeds:
            v = ev(arm, s)["tiers"][tier][key]
            if v is None:
                raise SystemExit(f"ERR_NULL_METRIC: {arm}/{tier}/{key} seed {s}")
            out.append(v)
        return out

    def contrast(tier, key):
        a = series("kernel", tier, key)
        b = series("shuffled", tier, key)
        d = [x - y for x, y in zip(a, b)]
        return {"kernel": a, "shuffled": b, "diffs": d,
                **paired_permutation_one_sided(d)}

    # ---- primary: tier-2 top-1, kernel vs shuffled-kernel -------------------
    primary = contrast("tier2", "top1")
    primary_pass = primary["p"] < 0.05

    # ---- paired-permutation secondaries (Holm over the family) --------------
    sec_raw = {
        "tier2_top10": contrast("tier2", "top10"),
        "tier1_top1": contrast("tier1", "top1"),
        "tier1_top10": contrast("tier1", "top10"),
    }
    sec = holm([(k, v["p"]) for k, v in sec_raw.items()])
    for k in sec_raw:
        sec[k].update({m: sec_raw[k][m] for m in ("meanDiff", "kernel", "shuffled")})

    # ---- Fisher secondaries: per-seed pooled item counts, Holm over seeds ---
    def counts(arm, seed, tier):
        rows = [r for r in ev(arm, seed)["items"] if r["tier"] == tier]
        return sum(1 for r in rows if r["rank"] == 0), len(rows)

    fisher = {}
    for tier in ("tier2", "tier1"):
        per_seed = {}
        for s in seeds:
            k1, n1 = counts("kernel", s, tier)
            k2, n2 = counts("shuffled", s, tier)
            per_seed[f"seed{s}"] = fisher_one_sided(k1, n1, k2, n2)
        adj = holm([(name, v["p"]) for name, v in per_seed.items()])
        for name in per_seed:
            per_seed[name].update(adj[name])
        fisher[tier] = per_seed

    # ---- control-floor validity check (shuffled must sit at 1/|C|) ----------
    p0 = 1.0 / n_cand
    pooled = {}
    for arm in ARMS:
        k = n = 0
        for s in seeds:
            dk, dn = counts(arm, s, "tier2")
            k, n = k + dk, n + dn
        pooled[arm] = {"correct": k, "n": n, "acc": k / n if n else None}
    lo, hi = binom_acceptance(pooled["shuffled"]["n"], p0)
    control_ok = lo <= pooled["shuffled"]["correct"] <= hi
    control = {
        "shuffledPooledTier2": pooled["shuffled"],
        "p0": p0,
        "acceptanceRegion": [lo, hi],
        "interpretation": "equal-tailed exact binomial 95% acceptance region under "
                          "rate 1/|C|; the shuffled arm's pooled tier-2 correct count "
                          "must fall inside it",
        "pass": control_ok,
        "kernelPooledTier2": pooled["kernel"],
        "randomPooledTier2": pooled["random"],
    }

    # ---- descriptives --------------------------------------------------------
    def tier_means(arm, tier):
        out = {"top1": sum(series(arm, tier, "top1")) / len(seeds),
               "top10": sum(series(arm, tier, "top10")) / len(seeds)}
        comp = {}
        for sub in ("shared", "novel"):
            t1 = [ev(arm, s)["tiers"][tier]["composition"][sub]["top1"] for s in seeds]
            if all(v is not None for v in t1):
                comp[sub] = {"top1": sum(t1) / len(t1),
                             "n": ev(arm, seeds[0])["tiers"][tier]["composition"][sub]["n"]}
        if comp:
            out["composition"] = comp
        return out

    descriptive = {
        arm: {"tier2": tier_means(arm, "tier2"), "tier1": tier_means(arm, "tier1"),
              "seenHeldglossTop1": sum(series(arm, "seen-heldgloss", "top1")) / len(seeds)}
        for arm in ARMS
    }

    # ---- verdict --------------------------------------------------------------
    if not control_ok:
        verdict = "INVALID — CONTROL FLOOR VIOLATED"
        reason = (f"shuffled-kernel pooled tier-2 = {pooled['shuffled']['correct']}/"
                  f"{pooled['shuffled']['n']} lies outside the exact binomial 95% acceptance "
                  f"region [{lo}, {hi}] of 1/|C| — per the pre-registration, a \"positive\" "
                  f"with a hot control is INVALID, not a result")
    elif primary_pass:
        verdict = "TIER-2 PRIMARY PASS"
        reason = (f"primary p = {primary['p']:.4f} < 0.05 with the control at empirical "
                  f"chance; ADVANCE RULE STILL BINDS: \"{spec['advanceRule']}\"")
    else:
        verdict = "TIER-2 NULL (AT/NEAR CHANCE)"
        reason = (f"primary p = {primary['p']:.4f} >= 0.05 — no pre-registered "
                  f"kernel-vs-shuffled advantage on tier-2 top-1 (kill-chain input: "
                  f"\"E4 tier-2 at chance\")")
    if args.mock:
        verdict = f"MOCK RUN — machinery check only, not a result. ({verdict})"

    out = {
        "experiment": "E4", "mock": args.mock, "seeds": seeds,
        "candidateSetSize": n_cand,
        "chance": spec["chance"],
        "preRegisteredCriteria": {   # quoted VERBATIM from the holdout manifest
            "primaryEndpoint": spec["primaryEndpoint"],
            "secondaryEndpoints": spec["secondaryEndpoints"],
            "controlFloorCheck": spec["controlFloorCheck"],
            "advanceRule": spec["advanceRule"],
            "candidateSet": spec["candidateSet"],
            "arms": spec["arms"],
            "trainingDataRule": manifest["trainingDataRule"],
        },
        "provenance": {**meta.get("provenance", {}),
                       "glossOovRate": meta["counts"].get("glossOovRate"),
                       "glossOovTokens": meta["counts"].get("glossOovTokens"),
                       "glossTokens": meta["counts"].get("glossTokens")},
        "primary": {**primary, "pass": primary_pass},
        "secondariesHolm": sec,
        "fisherPerSeedHolm": fisher,
        "controlFloor": control,
        "descriptive": descriptive,
        "verdict": verdict, "verdictReason": reason,
    }
    with open(args.out_prefix + ".json", "w") as f:
        json.dump(out, f, indent=2)

    md = [
        f"# E4 verdict{' (MOCK — pipeline check only)' if args.mock else ''}",
        "",
        "Pre-registered criteria (poc/e4/inputs/holdout-manifest.json `statistics`, quoted verbatim):",
        f"- **Primary:** \"{spec['primaryEndpoint']}\"",
        *[f"- **Secondary:** \"{s}\"" for s in spec["secondaryEndpoints"]],
        f"- **Control-floor validity:** \"{spec['controlFloorCheck']}\"",
        f"- **Advance rule:** \"{spec['advanceRule']}\"",
        f"- **Training-data rule:** \"{manifest['trainingDataRule']}\"",
        "",
        f"## Verdict: {verdict}",
        "",
        reason,
        "",
        "| quantity | value |",
        "|---|---|",
        f"| candidate set | {n_cand}-way (chance top-1 {1.0/n_cand:.6f}, top-10 {10.0/n_cand:.6f}) |",
        f"| tier-2 top-1 kernel (per seed) | {', '.join(f'{v:.4f}' for v in primary['kernel'])} |",
        f"| tier-2 top-1 shuffled (per seed) | {', '.join(f'{v:.4f}' for v in primary['shuffled'])} |",
        f"| paired mean diff | {primary['meanDiff']:.4f} |",
        f"| one-sided exact permutation p | {primary['p']:.4f} (min attainable {primary['minAttainableP']:.4f}) |",
        f"| control floor (shuffled pooled tier-2) | {pooled['shuffled']['correct']}/{pooled['shuffled']['n']} in [{lo}, {hi}] -> {'OK' if control_ok else 'VIOLATED'} |",
        f"| kernel pooled tier-2 | {pooled['kernel']['correct']}/{pooled['kernel']['n']} |",
        f"| random-frozen pooled tier-2 (descriptive) | {pooled['random']['correct']}/{pooled['random']['n']} |",
        f"| gloss OOV rate (recorded at build) | {out['provenance']['glossOovRate']} |",
        "",
        "## Secondaries (paired sign-flip, Holm-corrected)",
        "",
        "| contrast | mean diff | p | p (Holm) | reject |",
        "|---|---|---|---|---|",
    ]
    for k, v in sec.items():
        md.append(f"| {k} | {v['meanDiff']:.4f} | {v['p']:.4f} | {v['pAdj']:.4f} | {v['reject']} |")
    md += ["", "## Fisher exact per seed (pooled items, Holm over seeds)", ""]
    for tier, per_seed in fisher.items():
        md.append(f"**{tier}:**")
        md.append("")
        md.append("| seed | kernel k/n | shuffled k/n | p | p (Holm) | reject |")
        md.append("|---|---|---|---|---|---|")
        for name, v in per_seed.items():
            md.append(f"| {name} | {v['k'][0]}/{v['n'][0]} | {v['k'][1]}/{v['n'][1]} "
                      f"| {v['p']:.4f} | {v['pAdj']:.4f} | {v['reject']} |")
        md.append("")
    md += ["## Descriptive (per-arm means over seeds; compositional split)", ""]
    md.append("| arm | tier2 top1 | tier2 top10 | tier1 top1 | tier1 top10 | "
              "t2 shared/novel top1 | t1 shared/novel top1 | seen-heldgloss top1 |")
    md.append("|---|---|---|---|---|---|---|---|")
    for arm in ARMS:
        d = descriptive[arm]
        def compstr(tier):
            c = d[tier].get("composition", {})
            if not c:
                return "-"
            return " / ".join(f"{c[s]['top1']:.4f}" if s in c else "-" for s in ("shared", "novel"))
        md.append(f"| {arm} | {d['tier2']['top1']:.4f} | {d['tier2']['top10']:.4f} "
                  f"| {d['tier1']['top1']:.4f} | {d['tier1']['top10']:.4f} "
                  f"| {compstr('tier2')} | {compstr('tier1')} "
                  f"| {d['seenHeldglossTop1']:.4f} |")
    md.append("")
    md.append("Compositional subsets are DESCRIPTIVE only (no inferential claim), per the "
              "pre-registration. seen-heldgloss top-1 is the task-learned sanity readout "
              "(should be far above chance in ALL arms if emission fine-tuning worked).")
    md.append("")
    with open(args.out_prefix + ".md", "w") as f:
        f.write("\n".join(md))
    print(f"verdict: {verdict}")
    print(f"wrote {args.out_prefix}.json / .md")


if __name__ == "__main__":
    main()
