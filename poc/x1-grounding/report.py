#!/usr/bin/env python3
"""
X1-grounding stage 6 (PREREG §7): render results/x1g-report.md from whatever
artifacts exist. Handles the T2-halt state (stages 1-3 + audit, no endpoint)
as well as the full post-nsm_test state.
"""
import gzip
import json
import os

import x1g_lib as L

R = os.path.join(L.HERE, "results")


def load(path, gz=False):
    if not os.path.exists(path):
        return None
    if gz:
        with gzip.open(path, "rt") as f:
            return json.loads(f.read())
    return json.loads(open(path).read())


def main():
    stats = load(os.path.join(L.HERE, "graph-stats.json"))
    strata = load(os.path.join(L.HERE, "strata.json.gz"), gz=True)
    primes = load(os.path.join(L.HERE, "primes-mapping.json"))
    t2 = load(os.path.join(L.HERE, "t2-audit-result.json"))
    minsets = load(os.path.join(L.HERE, "minset-summary.json"))
    results = load(os.path.join(R, "x1g-results.json"))

    out = []
    A = out.append
    A("# X1-grounding — results report\n")
    A("Rendered from committed artifacts. Method: PREREG.md (frozen). "
      "Reference: Vincent-Lamarre et al. 2016, *The Latent Structure of Dictionaries*.\n")

    if stats:
        A("## Census (stages 1-3)\n")
        A("| quantity | value |\n|---|---|")
        A("| synsets | %d |" % stats["synsetCount"])
        A("| \\|V\\| (all lemma nodes) | %d |" % stats["V"])
        A("| \\|V_sw\\| (single-word nodes) | %d |" % stats["V_sw"])
        A("| edges (definer->defined) | %d |" % stats["edgeCount"])
        A("| self-reference tokens removed | %d |" % stats["selfRefCount"])
        A("| empty cleaned glosses | %d |" % stats["emptyGlossCount"])
        A("| OOV token occurrences | %d |" % stats["oovTokenCount"])
        A("| undefined nodes (in-deg 0) | %d |" % stats["undefinedNodeCount"])
        A("")

    if strata:
        g = strata["gates"]
        A("## Kernel / Core / Satellites and §4.3 corridor gates\n")
        A("| stratum | size | fraction |\n|---|---|---|")
        A("| Kernel K | %d | %.4f of V_sw |" % (strata["kernelSize"], g["kOverVsw"]))
        A("| Core | %d | %.4f of K |" % (strata["coreSize"], g["coreOverK"]))
        A("| Satellites | %d | |" % strata["satellitesSize"])
        A("| Rest | %d | |" % strata["restSize"])
        A("")
        A("**2016-shape comparison:** paper found Kernel ~10%%, Core = large fraction "
          "of Kernel, MinSets ~1%%. Here Kernel = %.1f%% of V_sw, Core = %.1f%% of K.\n"
          % (g["kOverVsw"] * 100, g["coreOverK"] * 100))
        A("| §4.3 gate | value | pass |\n|---|---|---|")
        A("| \\|K\\|/\\|V_sw\\| in [0.01,0.40] | %.4f | %s |" % (g["kOverVsw"], g["kOverVsw_pass"]))
        A("| \\|Core\\|/\\|K\\| >= 0.20 | %.4f | %s |" % (g["coreOverK"], g["coreOverK_pass"]))
        A("| Core unique-largest >= 2x | %d vs %d | %s |" % (
            g["coreMaxSize"], g["secondSccSize"], g["coreUnique2x_pass"]))
        A("| cycle-containment | %s | %s |" % (
            g["cycleContainment_detail"], g["cycleContainment_pass"]))
        A("| **CONSTRUCTION-ANOMALY** | | %s |" % strata["constructionAnomaly"])
        A("")

    if primes:
        A("## Prime -> node mapping (§5.1, frozen)\n")
        A("Evaluable primes: **%d** (coverage gate: %s, min 45). Excluded: %d.\n"
          % (primes["evaluableCount"], primes["coverageGate"], primes["excludedCount"]))
        if primes["removedByVerification"]:
            A("Removed by mechanical verification: %s\n" %
              ", ".join(r["prime"] for r in primes["removedByVerification"]))

    if t2:
        A("## T2 lemmatization audit (§8)\n")
        A("- population = %d resolutions; sample = %d (seed 7); pipeline = %s."
          % (t2["populationSize"], t2["sampleSize"], t2.get("pipeline", "n/a")))
        rate = t2.get("errorRate", t2.get("errorRateStrict"))
        A("- error rate = **%.0f%%** (gate = %.0f%%)."
          % (rate * 100, t2["gateThreshold"] * 100))
        prior = t2.get("priorAuditPreStoplist")
        if prior:
            A("- pre-stoplist audit was %.0f%% (strict) / %.0f%% (function-word); "
              "resolved by §9 Amendment 3."
              % (prior["errorRateStrict"] * 100, prior["errorRateFunctionWordOnly"] * 100))
        A("- gate tripped: **%s** -> %s\n" % (t2["gateTripped"], t2["verdict"]))

    if minsets:
        A("## MinSets (§4.4)\n")
        A("N_MS=%d, distinct=%d, sizes min/med/max=%d/%d/%d, I0.9=%d, exact=%d\n" % (
            minsets["N_MS"], minsets["distinctCount"], minsets["sizeMin"],
            minsets["sizeMedian"], minsets["sizeMax"], minsets["I09Size"],
            minsets["exactIntersectionSize"]))

    if results:
        A("## NSM test — endpoints and verdict (§5.4, §6)\n")
        A("**VERDICT: %s**\n" % results["verdict"])
        pr = results["primaryNull_outdeg"]
        A("| statistic | observed | null mean | p | ER |\n|---|---|---|---|---|")
        for name in ("T_core", "T_kern", "T_ms", "T_inv"):
            if name in pr["results"]:
                r = pr["results"][name]
                A("| %s | %.4f | %.4f | %.5f | %s |" % (
                    name, r["observed"], r["nullMean"], r["p"], r["ER"]))
        A("")
        A("Endpoints: %s\n" % json.dumps(
            {k: v.get("holds") for k, v in pr["endpoints"].items()}))
        A("Sensitivity null (usage-matched) agrees on E-core direction: %s\n"
          % results["sensitivityAgreesDirection"])
        # Interpretation (saturation / ceiling effect).
        tc = pr["results"]["T_core"]
        if strata and results["verdict"].startswith("FAIL"):
            A("**Interpretation (flag).** 50/51 primes ARE in the Core (T_core=%.4f; "
              "only MAYBE is absent, out-degree 0 — used in no gloss). But the "
              "frequency-matched null lands in the Core %.1f%% of the time, so ER=%s "
              "and p=%.3f: **no enrichment**. The Core spans %.1f%% of the Kernel and "
              "~97%% of frequency-matched high-out-degree content words, so Core "
              "membership is near-universal and carries almost no information — a "
              "ceiling/saturation effect, not evidence that primes are absent from the "
              "grounding floor. The FAIL is 'no detectable selectivity', decisive under "
              "the pre-registered mechanical criteria (E-core fails AND E-kern fails, "
              "§6), and independent of the MinSet secondaries.\n"
              % (tc["observed"], tc["nullMean"] * 100, tc["ER"], tc["p"],
                 strata["gates"]["coreOverK"] * 100))
    else:
        A("## NSM test\n")
        A("**Not run.** Held by the T2 audit gate (see above and PREREG §9 "
          "Amendment 2). nsm_test and stage-4 MinSets await the coordinator's "
          "remediation decision.\n")

    A("## Threats (PREREG §8)\n")
    A("T1 WordNet != full dictionary (14 primes excluded, logical/deictic-skewed); "
      "T2 lemmatization noise (audited above); T3 word-form not sense; "
      "T4 sense-collapse; T5 sampled minimal != minimum FVS; T6 null granularity "
      "(usage-matched sensitivity null); T7 analyst d.o.f. (frozen PREREG).\n")

    os.makedirs(R, exist_ok=True)
    with open(os.path.join(R, "x1g-report.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    print("report: wrote results/x1g-report.md")


if __name__ == "__main__":
    main()
