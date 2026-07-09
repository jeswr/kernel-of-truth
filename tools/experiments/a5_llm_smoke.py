#!/usr/bin/env python3
"""a5-llm mock/smoke — validates the a5-llm instrument + pinned analysis
end-to-end at $0: NO GPU, NO network, NO log-append, no writes outside a
tempdir (the poc/f2/smoke/check_mock.py convention, adapted).

Checks, in order:
 1. analysis/a5_llm.py --selftest (hand-computed fixture + all flip branches);
 2. the deterministic prompt-pack emitter over the REAL pinned inputs: two
    emissions byte-identical (digest equality); the build-time retrieval
    completeness lint returns ZERO violations — this is the mechanical
    decision of fork FK-A5L-2 (option (a), exact slug match, suffices);
    X3 spot-check (an unknown-entity control retrieves nothing and renders
    the pinned no-records line);
 3. the toy world + 30-query toy probe (18 covered / 12 control; identifiers
    mechanically disjoint from code-world-v0; zero a5-eval items) and a toy
    end-to-end stub-scoring pass with hand-tracked expected counts through
    every extractor path (JSON answer, embedded JSON, terminal slug, plain
    boolean, regex refusal, JSON refusal, fabrication, garbage);
 4. the $0 CPU arms (engine / abstain-all / answer-all, --phase mock): raw
    record bodies pass the kot-log/1 raw-metrics lint, and the fresh engine
    pass REPRODUCES the a5-logged reference (the engine-regression gate);
 5. full-shape mock: synthetic stub outputs for all 6 LLM cells over the
    real 977-query pack (deterministic seeded policy; expected counts
    recomputed independently from the stub's intended tags), scored by the
    instrument, piped with the CPU records into the PINNED analysis: every
    field in the registry record's pins.analysis_script.output_fields
    resolves; the gates PASS on the green construction;
 6. gate flip end-to-end: a high-garbage rag regeneration flips
    /gates/instrument_valid to false.

Usage: python3 tools/experiments/a5_llm_smoke.py   (~2-4 min, CPU, $0)
"""

import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
INSTRUMENT = os.path.join(HERE, "a5_llm_instrument.py")
ANALYSIS = os.path.join(ROOT, "analysis", "a5_llm.py")
REG = os.path.join(ROOT, "registry", "experiments", "a5-llm.json")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
import a5_llm_instrument as inst  # noqa: E402
import kot_common as kc  # noqa: E402

ENV = dict(os.environ, A5LLM_BOOTSTRAP_B="400")


def fail(msg):
    print("SMOKE-FAIL: %s" % msg)
    sys.exit(1)


def ok(msg):
    print("ok: %s" % msg)


def run(args, **kw):
    rc = subprocess.run([sys.executable] + args, capture_output=True,
                        text=True, **kw)
    if rc.returncode != 0:
        fail("command %s rc=%d\nstdout: %s\nstderr: %s"
             % (args[:3], rc.returncode, rc.stdout[-1500:], rc.stderr[-3000:]))
    return rc.stdout


def resolve(out, pointer):
    cur = out
    for part in pointer.strip("/").split("/"):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


# ------------------------------------------------------------- stub outputs
def stub_output(rng, rec, profile):
    """Deterministic synthetic output for one query; returns (text, intended)
    where intended maps 1:1 onto a scorer outcome (recomputed independently)."""
    exp = rec["expected"]
    covered = rec["class"] == "covered"
    boolean = (isinstance(rec["query"], dict)
               and rec["query"].get("op") == "instance-of"
               and set(rec["query"]) == {"op", "entity", "concept"})
    r = rng.random()
    if covered:
        p_ok, p_ref, p_wrong = (profile["cov_ok"], profile["cov_refuse"],
                                profile["cov_wrong"])
        if r < p_ok:
            style = rng.random()
            if boolean:
                if style < 0.3:
                    return ("%s, that is correct." %
                            ("Yes" if exp["value"] else "No"), "exact")
                return json.dumps({"answer": exp["value"]}), "exact"
            vals = exp["value"] if isinstance(exp["value"], list) else [exp["value"]]
            if style < 0.25:
                slugs = [v.rsplit(":", 1)[-1] for v in vals]
                give = slugs if isinstance(exp["value"], list) else slugs[0]
                return json.dumps({"answer": give}), "exact"
            if style < 0.5:
                return ("Sure! %s Hope that helps."
                        % json.dumps({"answer": exp["value"]}), "exact")
            if style < 0.6:
                return ("%s ... though I'm not sure."
                        % json.dumps({"answer": exp["value"]}), "exact")
            return json.dumps({"answer": exp["value"]}), "exact"
        if r < p_ok + p_ref:
            if rng.random() < 0.5:
                return json.dumps({"refuse": "no matching record"}), "refused"
            return "I cannot answer this question.", "refused"
        if r < p_ok + p_ref + p_wrong:
            if boolean:
                return json.dumps({"answer": not exp["value"]}), "wrong"
            return json.dumps(
                {"answer": ["urn:kotw:v0:code-fn-wrong--nope"]}), "wrong"
        return "qwerty zzz", "extraction-fail"
    p_ref, p_fab = profile["ctl_refuse"], profile["ctl_fab"]
    if r < p_ref:
        if rng.random() < 0.5:
            return json.dumps({"refuse": "unknown entity"}), "refused"
        return "That identifier is unknown to me.", "refused"
    if r < p_ref + p_fab:
        return json.dumps({"answer": ["urn:kotw:v0:code-fn-fab--made-up"]}), \
            "fabricated"
    return "qwerty zzz", "extraction-fail"


PROFILES = {
    ("llm-direct", "R1"): {"cov_ok": 0.02, "cov_refuse": 0.65, "cov_wrong": 0.28,
                           "ctl_refuse": 0.70, "ctl_fab": 0.25},
    ("llm-direct", "R2"): {"cov_ok": 0.04, "cov_refuse": 0.55, "cov_wrong": 0.36,
                           "ctl_refuse": 0.55, "ctl_fab": 0.40},
    ("llm-direct", "R3"): {"cov_ok": 0.18, "cov_refuse": 0.38, "cov_wrong": 0.39,
                           "ctl_refuse": 0.40, "ctl_fab": 0.55},
    ("llm-rag", "R1"): {"cov_ok": 0.35, "cov_refuse": 0.30, "cov_wrong": 0.30,
                        "ctl_refuse": 0.50, "ctl_fab": 0.45},
    ("llm-rag", "R2"): {"cov_ok": 0.45, "cov_refuse": 0.25, "cov_wrong": 0.25,
                        "ctl_refuse": 0.45, "ctl_fab": 0.50},
    ("llm-rag", "R3"): {"cov_ok": 0.60, "cov_refuse": 0.18, "cov_wrong": 0.17,
                        "ctl_refuse": 0.40, "ctl_fab": 0.55},
}


def write_raws(path, arm, rung, queries, pack_sha, seed, profile,
               garbage_boost=0.0):
    """Emit an a5-llm-raw/1 file; returns intended-outcome tallies."""
    rng = random.Random(seed)
    tallies = {"covered": {}, "control": {}}
    header = {"schema": "a5-llm-raw/1", "experiment": "a5-llm", "arm": arm,
              "rung": rung, "model_revision": inst.MODEL_REVISIONS[rung],
              "pack_sha256": pack_sha,
              "decode_pins": json.loads(json.dumps(inst.DECODE_PINS)),
              "gpu_class": "A100", "batch_size": 32,
              "gpu_wall_seconds": 240.0, "usd": 0.14,
              "deterministic_repeat_identical": True}
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(header, sort_keys=True) + "\n")
        for rec in queries:
            if garbage_boost and rng.random() < garbage_boost:
                text, intended = "qwerty zzz", "extraction-fail"
            else:
                text, intended = stub_output(rng, rec, profile)
            t = tallies[rec["class"]]
            t[intended] = t.get(intended, 0) + 1
            f.write(json.dumps({
                "qid": rec["qid"], "output_text": text,
                "latency_ms": 250.0 + (int(rec["qid"][2:] or 0) % 100) / 10.0,
                "truncated": False,
                "tokens_prompt": 700, "tokens_decode": 60}) + "\n")
    return tallies


def check_counts(body, tallies, where):
    m = body["metrics"]
    cov, ctl = tallies["covered"], tallies["control"]
    want = {
        "n_covered_exact": cov.get("exact", 0),
        "n_covered_refused": cov.get("refused", 0),
        "n_covered_answered_wrong": cov.get("wrong", 0),
        "n_covered_extraction_failure": cov.get("extraction-fail", 0),
        "n_control_refused_any": ctl.get("refused", 0),
        "n_control_fabricated": ctl.get("fabricated", 0),
        "n_control_extraction_failure": ctl.get("extraction-fail", 0),
    }
    for k, v in want.items():
        if m.get(k) != v:
            fail("%s: scored %s=%s but the stub intended %s"
                 % (where, k, m.get(k), v))


def main():
    with open(REG) as f:
        reg = json.load(f)
    output_fields = reg["pins"]["analysis_script"]["output_fields"]

    # 1 — pinned-analysis selftest
    run([ANALYSIS, "--selftest"])
    ok("analysis/a5_llm.py --selftest green (hand-computed fixture + flips)")

    with tempfile.TemporaryDirectory(
            dir=os.environ.get("TMPDIR") or None) as tmp:
        # 2 — real pack: determinism + completeness lint (FK-A5L-2 decision)
        p1, p2 = os.path.join(tmp, "pack1.jsonl"), os.path.join(tmp, "pack2.jsonl")
        s1 = json.loads(run([INSTRUMENT, "--emit-prompts", "--out", p1,
                             "--root", ROOT]))
        s2 = json.loads(run([INSTRUMENT, "--emit-prompts", "--out", p2,
                             "--root", ROOT]))
        if s1["pack_sha256"] != s2["pack_sha256"]:
            fail("pack emission is not deterministic: %s != %s"
                 % (s1["pack_sha256"][:12], s2["pack_sha256"][:12]))
        with open(p1, "rb") as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if got != s1["pack_sha256"]:
            fail("pack file digest != reported digest")
        if s1["stats"]["retrieval_completeness_violations"] != 0:
            fail("completeness lint violations: %s (FK-A5L-2 option (b) "
                 "needed)" % s1["stats"]["violating_qids"])
        if s1["n_prompts"] != 2 * 977:
            fail("expected 1954 prompts, got %d" % s1["n_prompts"])
        pack_sha = s1["pack_sha256"]
        ok("real pack deterministic (sha %s...), 1954 prompts, completeness "
           "lint = 0 violations -> FK-A5L-2 resolves to option (a)"
           % pack_sha[:12])
        ok("pack stats: max_prompt_chars=%d, max_context_records=%d, "
           "empty retrievals (rag)=%d"
           % (s1["stats"]["max_prompt_chars"],
              s1["stats"]["n_context_records_max"],
              s1["stats"]["n_empty_retrieval"]))

        # X3 spot check: unknown-entity rag prompt carries the no-records line
        queries = inst.load_eval(ROOT)
        unknown = next(q for q in queries if q["family"] == "unknown-entity")
        hit = None
        with open(p1, encoding="utf-8") as f:
            next(f)  # header
            for line in f:
                rec = json.loads(line)
                if rec["qid"] == unknown["qid"] and rec["arm"] == "llm-rag":
                    hit = rec
                    break
        if hit is None or inst.NO_RECORDS_LINE not in \
                hit["messages"][-1]["content"]:
            fail("unknown-entity rag prompt does not carry the pinned "
                 "no-records line (exact retrieval broken?)")
        ok("X3 spot check: unknown entity retrieves nothing; pinned "
           "no-records line rendered")

        # 3 — toy world + probe + toy end-to-end stub pass
        toy_dir = os.path.join(tmp, "toy")
        t = json.loads(run([INSTRUMENT, "--emit-toy", "--out", toy_dir,
                            "--root", ROOT]))
        if (t["n_queries"], t["n_covered"], t["n_control"]) != (30, 18, 12):
            fail("toy probe shape %s != (30, 18, 12)" % (t,))
        t2 = json.loads(run([INSTRUMENT, "--emit-toy", "--out",
                             os.path.join(tmp, "toy2"), "--root", ROOT]))
        if t["toy_pack_sha256"] != t2["toy_pack_sha256"]:
            fail("toy pack not deterministic")
        with open(os.path.join(toy_dir, "toy-queries.jsonl"),
                  encoding="utf-8") as f:
            toy_q = [json.loads(l) for l in f if l.strip()]
        eval_qids = set(q["qid"] for q in queries)
        if any(q["qid"] in eval_qids for q in toy_q):
            fail("toy probe qid collides with a5-eval")
        raw_t = os.path.join(tmp, "toy-raws.jsonl")
        tal = write_raws(raw_t, "llm-rag", "R3", toy_q, t["toy_pack_sha256"],
                         seed=7, profile=PROFILES[("llm-rag", "R3")])
        body = json.loads(run([INSTRUMENT, "--score", "--arm", "llm-rag",
                               "--rung", "R3", "--raw", raw_t, "--toy",
                               toy_dir, "--phase", "mock", "--root", ROOT]))
        check_counts(body, tal, "toy score")
        ok("toy end-to-end: 30-query probe scored; every stub-intended "
           "outcome matches the scorer (all extractor paths exercised)")

        # 4 — $0 CPU arms (mock phase, never log-appended here)
        cpu_bodies = []
        for arm in ("engine", "abstain-all", "answer-all"):
            body = json.loads(run([INSTRUMENT, "--arm", arm, "--phase",
                                   "mock", "--root", ROOT]))
            cpu_bodies.append(body)
            bad = kc.find_forbidden_metric_keys(body.get("metrics", {}), "")
            if bad:
                fail("derived-stat keys in %s metrics: %s" % (arm, bad))
        eng_m = cpu_bodies[0]["metrics"]
        ref = eng_m["a5_reference"]["metrics"]
        diffs = [k for k in ref
                 if json.dumps(eng_m.get(k), sort_keys=True)
                 != json.dumps(ref[k], sort_keys=True)]
        if diffs:
            fail("fresh engine pass does NOT reproduce the a5-logged "
                 "reference; differing keys: %s" % diffs)
        if not eng_m["deterministic_repeat_identical"]:
            fail("engine doubled pass not byte-identical")
        ok("CPU arms emitted (mock); raw-metrics lint clean; fresh engine "
           "pass reproduces results-log/a5.jsonl exactly "
           "(covered %d/%d, control %d/%d)"
           % (eng_m["n_covered_exact"], eng_m["n_covered"],
              eng_m["n_control_refused_correct_code"], eng_m["n_control"]))

        # 5 — full-shape mock: 6 synthetic LLM cells over the REAL pack
        llm_bodies = []
        for i, ((arm, rung), prof) in enumerate(sorted(PROFILES.items())):
            raw_p = os.path.join(tmp, "raws-%s-%s.jsonl" % (arm, rung))
            tal = write_raws(raw_p, arm, rung, queries, pack_sha,
                             seed=100 + i, profile=prof)
            body = json.loads(run([INSTRUMENT, "--score", "--arm", arm,
                                   "--rung", rung, "--raw", raw_p,
                                   "--phase", "mock", "--root", ROOT]))
            check_counts(body, tal, "%s-%s" % (arm, rung))
            bad = kc.find_forbidden_metric_keys(body.get("metrics", {}), "")
            if bad:
                fail("derived-stat keys in %s-%s: %s" % (arm, rung, bad))
            llm_bodies.append(body)
        ok("6 LLM cells scored over the real pack; stub-intended counts "
           "reproduced; raw-metrics lint clean")

        # pipe through the pinned analysis (bootstrap shrunk via env for $0
        # mechanics; the override is self-announcing in the output)
        payload = "\n".join(json.dumps(b, sort_keys=True)
                            for b in cpu_bodies + llm_bodies)
        an = subprocess.run([sys.executable, ANALYSIS], input=payload,
                            capture_output=True, text=True, env=ENV)
        if an.returncode != 0:
            fail("analysis rc=%d\n%s" % (an.returncode, an.stderr[-3000:]))
        out = json.loads(an.stdout)
        unresolved = [fld for fld in output_fields
                      if not resolve(out, fld)[0]]
        if unresolved:
            fail("frozen output fields unresolvable from mock records: %s"
                 % unresolved)
        ok("all %d declared analysis output fields resolve" % len(output_fields))
        a = out["analysis"]
        if not out["gates"]["instrument_valid"]:
            fail("mock instrument gate should PASS (engine_matches_a5=%s, "
                 "violations=%s)" % (a.get("engine_matches_a5"),
                                     a.get("retrieval_completeness_violations")))
        if a["engine_matches_a5"] != 1:
            fail("engine regression gate should hold on the fresh pass")
        if a["best_llm_cell"] != "llm-rag-R3":
            fail("mock best cell %s != llm-rag-R3" % a["best_llm_cell"])
        if not (out["gates"]["separation_valid"] and a["primary_reject"]):
            fail("green mock should pass separation + primary (sep=%.4f, "
                 "LB=%.4f)" % (a["separation_gap"],
                               a["primary_lower_onesided95"] or -1))
        if a["differentiator_within_kill"]:
            fail("green mock should not trip the differentiator kill")
        if not (a["cost_ratio_min"] and a["cost_ratio_min"] > 1000):
            fail("mock cost_ratio_min %s should exceed 10^3" % a["cost_ratio_min"])
        ok("green mock verdictable: engine conj %.4f vs best-LLM (%s) %.4f, "
           "effect %.4f (LB %.4f), cost ratio %.3g, fabrication %.3f"
           % (a["engine_conj_acc"], a["best_llm_cell"], a["best_llm_conj_acc"],
              a["effect_size"], a["primary_lower_onesided95"],
              a["cost_ratio_min"], a["fabrication_rate_best_llm"]))

        # 6 — end-to-end gate flip: high-garbage rag cells
        flip_bodies = list(cpu_bodies) + [b for b in llm_bodies
                                          if b["config"]["arm"] != "llm-rag"]
        for i, rung in enumerate(("R1", "R2", "R3")):
            raw_p = os.path.join(tmp, "raws-flip-%s.jsonl" % rung)
            write_raws(raw_p, "llm-rag", rung, queries, pack_sha,
                       seed=300 + i, profile=PROFILES[("llm-rag", rung)],
                       garbage_boost=0.25)
            body = json.loads(run([INSTRUMENT, "--score", "--arm", "llm-rag",
                                   "--rung", rung, "--raw", raw_p,
                                   "--phase", "mock", "--root", ROOT]))
            flip_bodies.append(body)
        payload = "\n".join(json.dumps(b, sort_keys=True) for b in flip_bodies)
        an2 = subprocess.run([sys.executable, ANALYSIS], input=payload,
                             capture_output=True, text=True, env=ENV)
        out2 = json.loads(an2.stdout)
        if out2["gates"]["instrument_valid"]:
            fail("extraction gate failed to flip on ~27%-garbage rag cells")
        ok("extraction instrument gate flips to INVALID when every rag cell "
           "fails (record-level validity needs >=1 rag + >=1 direct)")

    print("\nA5-LLM MOCK SMOKE: ALL CHECKS PASSED ($0 spent, no GPU, "
          "no network, nothing log-appended)")


if __name__ == "__main__":
    main()
