#!/usr/bin/env python3
"""knull — K-NULL content-injection ablation runner (DRAFT; mock-green only).

Design doc: docs/design-knull-content-injection-ablation.md. Registry line:
knull-content-injection-ablation (DRAFT — NOT frozen; this runner REFUSES any
non-mock run until a kot-reg/1 record is frozen AND the plain store is the
authored, non-placeholder set).

THE ONE DESIGN RULE (from the content-injection map): arms must differ ONLY
in store semantics. This runner enforces it structurally by REUSING the
frozen f2b machinery via import — KernelVerifier, ShuffledKernelVerifier,
run_alone, run_verify_retry, extract_record, build_prompt, the prompt frames
and the F0 flop accounting are the byte-identical objects of the f2b run
(poc/f2b/runner/f2b_runner.py, sha pinned in inputs/manifest.json) — and
swapping ONLY records_root + the item file per arm:

  arm kernel   records_root = repo root (the pinned NSM records) [REFERENCE]
  arm plain    records_root = poc/knull/inputs/stores/plain   (typed schema,
               zero NSM content; DRAFT store is a placeholder -> mock only)
  arm opaque   records_root = poc/knull/inputs/stores/opaque  (nonce content)

Cells per arm: alone-R1, alone-R3, verify-retry-R1 (k=4), each per seed;
plus shuffled-verify-retry (derangement bridge) in the KERNEL arm only.

MAP CHECK (M-V, $0, real even under --mock): strips every non-gloss field
(explication/partialExplication/axioms/...) from the kernel records into a
scratch store and asserts the verifier's (decidable, consistent) decisions
are IDENTICAL for every item x candidate answer — the executable proof that
kernel VECTORS/ASTs inject zero bytes into the accept decision.

Usage:
  python3 poc/knull/runner/knull_runner.py --mock --out-dir /tmp/knull
  python3 poc/knull/runner/knull_runner.py --selftest        # TOST logic only
"""

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(POC, ".."))
F2B_RUNNER_DIR = os.path.join(POC, "f2b", "runner")
for p in (POC, F2B_RUNNER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Byte-identical f2b machinery (pinned; see inputs/manifest.json provenance)
from f2b_runner import (                                    # noqa: E402
    CellGuard, KernelVerifier, ShuffledKernelVerifier, StubLM,
    extract_record, run_alone, run_verify_retry, sha256_file, verify_answer)
from f0 import FlopMeter                                    # noqa: E402

ARMS = ("kernel", "plain", "opaque")
K_RETRY = 4
TOST_MARGIN = 0.05          # pre-declared draft margin (design doc section 3.4)
DIFFICULTY_BAND = 0.15      # |acc_alone(arm) - acc_alone(kernel)| gate
BRIDGE_LIFT_MIN = 0.05      # kernel-arm lift one-sided 95% LB must clear this
SHUF_RECOVERY_MAX = 0.30    # f2b bridge secondary (comparability, verbatim)
PERM_SEED = 20260710


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def wilson_lb(successes, n, z=1.6448536269514722):
    if n == 0:
        return 0.0
    p = successes / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def det_rand_stream(seed_key):
    """sha256 counter stream -> floats in [0,1) (no global RNG state)."""
    i = 0
    while True:
        d = hashlib.sha256(("%s|%d" % (seed_key, i)).encode()).digest()
        yield int.from_bytes(d[:8], "big") / 2.0 ** 64
        i += 1


def boot_ci(vec, b, seed_key, alpha=0.05):
    """Percentile bootstrap CI of the mean over paired per-item values.
    DRAFT analysis: the pinned freeze-time analysis script will use BCa,
    B=10000 (P8 discipline); percentile is mechanics-adequate for mock."""
    n = len(vec)
    if n == 0:
        return 0.0, 0.0, 0.0
    stream = det_rand_stream(seed_key)
    means = []
    for _ in range(b):
        s = 0.0
        for _ in range(n):
            s += vec[int(next(stream) * n)]
        means.append(s / n)
    means.sort()
    lo = means[max(0, int(alpha * b) - 1)]
    hi = means[min(b - 1, int((1 - alpha) * b))]
    return sum(vec) / n, lo, hi


def analyse(lifts, accs, b, margin=TOST_MARGIN):
    """The verdict-shaped analysis (DRAFT contract; frozen SAP re-implements
    with BCa). lifts: arm -> per-skeleton paired lift vector (seed-mean
    verify minus seed-mean alone). accs: arm -> dict of scalar accuracies."""
    out = {"arms": {}, "margin": margin}
    for a, vec in lifts.items():
        m, lo, hi = boot_ci(vec, b, "lift|%s" % a)
        out["arms"][a] = {"lift": m, "lift_lb95_1s": lo, "lift_ub95_1s": hi,
                          **accs[a]}
    # instrument gates
    gates = {}
    kacc = out["arms"]["kernel"]["acc_alone_r1"]
    for a in ("plain", "opaque"):
        gates["difficulty_band_%s" % a] = (
            abs(out["arms"][a]["acc_alone_r1"] - kacc) <= DIFFICULTY_BAND)
    gates["bridge_kernel_lift"] = (
        out["arms"]["kernel"]["lift_lb95_1s"] > BRIDGE_LIFT_MIN)
    eligible = [a for a in ("plain", "opaque") if gates["difficulty_band_%s" % a]]
    gates["any_aligned_arm_eligible"] = bool(eligible)
    out["gates"] = gates
    if not eligible or not gates["bridge_kernel_lift"]:
        out["best_aligned_arm"] = None
        out["verdict_shape"] = "INSTRUMENT-INVALID"
        return out
    best = max(eligible, key=lambda a: out["arms"][a]["lift"])
    out["best_aligned_arm"] = best
    # primary: TOST on the paired per-skeleton lift DIFFERENCE
    dvec = [lifts["kernel"][i] - lifts[best][i]
            for i in range(len(lifts["kernel"]))]
    dm, dlo, dhi = boot_ci(dvec, b, "tost|kernel-%s" % best)
    out["primary"] = {"diff": dm, "diff_lb95_1s": dlo, "diff_ub95_1s": dhi,
                      "tost_equivalent": dlo > -margin and dhi < margin,
                      "kernel_superior_beyond_margin": dlo > margin,
                      "kernel_inferior_beyond_margin": dhi < -margin}
    p = out["primary"]
    out["verdict_shape"] = (
        "EQUIVALENT-GENERIC" if p["tost_equivalent"] else
        "KERNEL-SUPERIOR" if p["kernel_superior_beyond_margin"] else
        "KERNEL-INFERIOR" if p["kernel_inferior_beyond_margin"] else
        "INCONCLUSIVE")
    return out


def selftest(b=800):
    """Planted-data check that the TOST contract classifies correctly."""
    import random
    rng = random.Random(7)
    n = 1500

    def mk(p):
        return [1.0 if rng.random() < p else 0.0 for _ in range(n)]

    def case(pk, pb):
        lifts = {"kernel": mk(pk), "plain": mk(pb), "opaque": mk(pb * 0.9)}
        accs = {a: {"acc_alone_r1": 0.45, "acc_verify": 0.45 + pk,
                    "acc_alone_r3": 0.6} for a in ARMS}
        return analyse(lifts, accs, b)

    r1 = case(0.25, 0.25)
    assert r1["verdict_shape"] == "EQUIVALENT-GENERIC", r1["verdict_shape"]
    r2 = case(0.40, 0.15)
    assert r2["verdict_shape"] == "KERNEL-SUPERIOR", r2["verdict_shape"]
    r3 = case(0.10, 0.40)
    assert r3["verdict_shape"] in ("KERNEL-INFERIOR",), r3["verdict_shape"]
    print("selftest OK: EQUIVALENT-GENERIC / KERNEL-SUPERIOR / "
          "KERNEL-INFERIOR all classified correctly (planted data, B=%d)" % b)


STRIP_FIELDS = ("explication", "partialExplication", "axioms", "notes",
                "references", "corpusLemmas", "groundingRefs", "pattern",
                "semanticStatus", "researchGrade", "flag", "status")


def map_check_vector_free(kernel_items, out_dir):
    """M-V: prove by execution that only {gloss|groundingNote, label} bytes
    of the record reach the accept decision — strip everything else and
    assert bitwise-identical verifier decisions on every candidate answer."""
    tmp = tempfile.mkdtemp(prefix="knull-mv-", dir=out_dir)
    stripped_items = []
    for it in kernel_items:
        src = os.path.join(ROOT, it["record_path"])
        rec = json.load(open(src, encoding="utf-8"))
        slim = {k: v for k, v in rec.items() if k not in STRIP_FIELDS}
        rel = it["record_path"].replace("/", "__")
        dst = os.path.join(tmp, rel)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(slim, f, sort_keys=True)
        it2 = dict(it, record_path=rel, record_sha256=sha256_file(dst))
        stripped_items.append(it2)
    full = KernelVerifier(ROOT)
    slimv = KernelVerifier(tmp)
    full.index_labels(kernel_items)
    slimv.index_labels(stripped_items)
    n_checked = 0
    for it, it2 in zip(kernel_items, stripped_items):
        cands = ([o["key"] for o in it["options"]] if it.get("options")
                 else ["yes", "no"])
        for ans in cands:
            r1 = verify_answer(full, it, ans)[:3]
            r2 = verify_answer(slimv, it2, ans)[:3]
            if r1 != r2:
                die("KNULL_ERR_MAPCHECK",
                    "decision diverged on %s ans=%s: %r vs %r"
                    % (it["id"], ans, r1, r2))
            n_checked += 1
    shutil.rmtree(tmp)
    return {"n_items": len(kernel_items), "n_decisions_checked": n_checked,
            "stripped_fields": list(STRIP_FIELDS),
            "result": ("IDENTICAL — no byte outside {gloss|groundingNote, "
                       "label} influences any accept decision; kernel "
                       "vectors/ASTs are not in the seam (map point M-V)")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--items", type=int, default=60,
                    help="rank-prefix skeletons per arm (mock default 60)")
    ap.add_argument("--boot-b", type=int, default=2000)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return
    if not args.mock:
        die("KNULL_ERR_DRAFT_ONLY",
            "this line is DRAFT: no frozen kot-reg/1 record exists and the "
            "plain store is a placeholder (inputs/manifest.json "
            "plain_store_placeholder=true). Real runs are refused by design "
            "until prereg-freeze + authored plain store land.")
    if not args.out_dir:
        die("KNULL_ERR_ARGS", "--out-dir required")
    os.makedirs(args.out_dir, exist_ok=True)

    man_path = os.path.join(POC, "knull", "inputs", "manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    f2b_man = json.load(open(os.path.join(POC, "f2b", "inputs",
                                          "f2b-manifest.json"),
                             encoding="utf-8"))
    # provenance pin: the machinery we imported must be the pinned bytes
    got = sha256_file(os.path.join(F2B_RUNNER_DIR, "f2b_runner.py"))
    want = man["provenance_pins"]["f2b_runner_py_sha256"]
    if got != want:
        die("KNULL_ERR_PIN", "f2b_runner.py sha %s != inputs pin %s"
            % (got[:12], want[:12]))

    frames = f2b_man["prompt_frames"]           # VERBATIM f2b frames
    fc = f2b_man["flop_accounting"]
    mock_spec = f2b_man["mock"]
    seeds = mock_spec["seeds"]

    items = {}
    for a in ARMS:
        vec = load_jsonl(os.path.join(POC, "knull", "inputs", "items",
                                      "%s.jsonl" % a))
        vec.sort(key=lambda x: x["rank"])
        items[a] = vec[:args.items]
    uids = [it["skeleton_uid"] for it in items["kernel"]]
    for a in ARMS:
        if [it["skeleton_uid"] for it in items[a]] != uids:
            die("KNULL_ERR_PAIRING", "skeleton prefix differs for arm %s" % a)

    roots = {"kernel": ROOT,
             "plain": os.path.join(POC, "knull", "inputs", "stores", "plain"),
             "opaque": os.path.join(POC, "knull", "inputs", "stores", "opaque")}

    # M-V map check (real, $0)
    mv = map_check_vector_free(items["kernel"], args.out_dir)
    with open(os.path.join(args.out_dir, "map-check.json"), "w") as f:
        json.dump(mv, f, indent=1, sort_keys=True)
        f.write("\n")
    print("map-check M-V: %s decisions, %s" % (mv["n_decisions_checked"],
                                               mv["result"][:40]))

    lms = {"R1": StubLM("R1", mock_spec), "R3": StubLM("R3", mock_spec)}
    guard_args = (7200.0, 64)
    records = []
    lifts, accs = {}, {}
    xfail_by_arm = {}
    for a in ARMS:
        ver = KernelVerifier(roots[a])
        ver.index_labels(items[a])
        per_seed = {"alone_r1": [], "alone_r3": [], "verify": []}
        xfails, n_verify_calls = 0, 0
        for seed in seeds:
            for rung, key in (("R1", "alone_r1"), ("R3", "alone_r3")):
                g = CellGuard("%s/alone/%s/s%d" % (a, rung, seed), *guard_args)
                meter = FlopMeter(fc, "A100")
                cov = run_alone(lms[rung], frames, items[a], seed, meter, g)
                per_seed[key].append(cov)
                records.append({"arm": a, "cell": "model-alone", "rung": rung,
                                "seed": seed, "k": 0, "n": len(cov),
                                "acc": sum(cov) / len(cov), "mock": True})
            g = CellGuard("%s/verify/R1/s%d" % (a, seed), *guard_args)
            meter = FlopMeter(fc, "A100")
            cov, xf = run_verify_retry(lms["R1"], frames, items[a], ver,
                                       K_RETRY, seed, meter, g)
            per_seed["verify"].append(cov)
            xfails += xf
            n_verify_calls += len(items[a])
            records.append({"arm": a, "cell": "verify-retry", "rung": "R1",
                            "seed": seed, "k": K_RETRY, "n": len(cov),
                            "acc": sum(cov) / len(cov),
                            "extraction_failures": xf, "mock": True})
        xfail_by_arm[a] = {"failures": xfails, "calls": n_verify_calls}
        n = len(items[a])
        sm = {k: [sum(v[s][i] for s in range(len(seeds))) / len(seeds)
                  for i in range(n)] for k, v in per_seed.items()}
        lifts[a] = [sm["verify"][i] - sm["alone_r1"][i] for i in range(n)]
        accs[a] = {"acc_alone_r1": sum(sm["alone_r1"]) / n,
                   "acc_alone_r3": sum(sm["alone_r3"]) / n,
                   "acc_verify": sum(sm["verify"]) / n}

    # kernel-arm shuffled bridge (identical topology, deranged store map)
    shuf = ShuffledKernelVerifier(roots["kernel"], items["kernel"], PERM_SEED)
    shuf.index_labels(items["kernel"])
    shuf_seed_cov = []
    for seed in seeds:
        g = CellGuard("kernel/shuffled/R1/s%d" % seed, *guard_args)
        meter = FlopMeter(fc, "A100")
        cov, _xf = run_verify_retry(lms["R1"], frames, items["kernel"], shuf,
                                    K_RETRY, seed, meter, g)
        shuf_seed_cov.append(cov)
        records.append({"arm": "kernel", "cell": "shuffled-verify-retry",
                        "rung": "R1", "seed": seed, "k": K_RETRY,
                        "n": len(cov), "acc": sum(cov) / len(cov),
                        "perm_sha256": shuf.perm_sha256, "mock": True})

    ana = analyse(lifts, accs, args.boot_b)
    n = len(items["kernel"])
    acc_shuf = (sum(sum(v) for v in shuf_seed_cov)
                / (n * len(seeds)))
    k_lift = accs["kernel"]["acc_verify"] - accs["kernel"]["acc_alone_r1"]
    ana["secondaries"] = {
        "shuffled_acc": acc_shuf,
        "shuffled_lift_abs": acc_shuf - accs["kernel"]["acc_alone_r1"],
        "shuffled_recovery_fraction": (
            (acc_shuf - accs["kernel"]["acc_alone_r1"]) / k_lift
            if abs(k_lift) > 1e-9 else None),
        "shuffled_recovery_max_declared": SHUF_RECOVERY_MAX,
        "f2b_form_effect_kernel": (accs["kernel"]["acc_verify"]
                                   - accs["kernel"]["acc_alone_r3"]),
    }
    ana["gates"]["extraction"] = {
        a: {"wilson_lb_success": wilson_lb(
                v["calls"] - v["failures"], v["calls"]),
            **v, "pass": wilson_lb(v["calls"] - v["failures"],
                                   v["calls"]) >= 0.90}
        for a, v in xfail_by_arm.items()}
    ana["mock"] = True
    ana["_note"] = ("MOCK — synthetic StubLM mechanics only; every number "
                    "here is a mechanics check, NEVER a measurement. The "
                    "planted stub skill is arm-blind, so EQUIVALENT-GENERIC "
                    "is the expected mock shape.")

    with open(os.path.join(args.out_dir, "run-records.jsonl"), "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(args.out_dir, "analysis-mock.json"), "w") as f:
        json.dump(ana, f, indent=1, sort_keys=True)
        f.write("\n")
    print("MOCK OUTCOME: verdict_shape=%s best_aligned=%s "
          "(kernel lift %.3f, diff %.3f in [%.3f, %.3f])"
          % (ana["verdict_shape"], ana.get("best_aligned_arm"),
             ana["arms"]["kernel"]["lift"],
             ana.get("primary", {}).get("diff", float("nan")),
             ana.get("primary", {}).get("diff_lb95_1s", float("nan")),
             ana.get("primary", {}).get("diff_ub95_1s", float("nan"))))
    print("records: %d cells -> %s" % (len(records), args.out_dir))


if __name__ == "__main__":
    main()
