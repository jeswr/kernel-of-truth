#!/usr/bin/env python3
"""ddc0 (G0) statistics-stage runner — docs/next/design/DDC.md §2.3/§6/§8;
DRAFT record registry/experiments/ddc0.json (freeze-before-run).

Produces exactly the three inputs the PINNED analysis (analysis/ddc0.py)
consumes — candidates.jsonl, maxstat-null.json, sidecar.json — plus the
A2 hand-off artifact for ddc1 (a2-directions*.json: every candidate's
model-space direction u and the shared threshold t*; ADMISSION itself is
computed only by the pinned analysis, never here — this runner emits raw
fields and no verdict).

Two execution stages (cost split; ddc0 budget $5 / 2 GPU-h):
  --stage probe   GPU: one fp32 pass over the carrier-controlled probe
                  fixture (H arrays, both poolings + carrier halves,
                  empty-carrier subtraction, grand-mean centring) + the
                  K-static and C4 corpus second moments (C4 overlap,
                  ASM-1662 diagnostic) + massive-activation census
                  (ASM-1658). Writes probe-artifact.npz.
  --stage stats   CPU: g0_stats.run_g0 — ridge-CCA + Procrustes fits, the
                  B=1000 joint max-stat permutation family (seed 1, FULL
                  pipeline re-run per replicate, checkpointed/resumable),
                  admission-criteria raw statistics. Writes the analysis
                  inputs.

Probe fixture (data/ddc-probe-fixture-v1/probe-fixture.json, built +
hash-pinned at T0 by poc/ddc/t0/build_kernel_assets.mjs; determinism-
checked by building twice — gate /gates/probe_fixture_deterministic):
  {"schema": "kot-ddc-probe-fixture/1",
   "determinism": {"sha_run1": <64hex>, "sha_run2": <64hex>},
   "empty_carriers": [4 carrier-only texts],
   "concepts": [{"id", "class" ("prime"|"kernel-v0"|
                 "synthetic-minimal-contrast"),
                 "vector": [d floats]  (canonical kot-enc-Bq/1, D=576),
                 "bag_vector": [d floats] (structure-destroyed),
                 "carriers": [[>=2 seeded render texts] x 4]}],
   "minimal_contrast_pairs": [[id, id], ...]}
  T0-pinned inventory (PROPOSED-ASM-1790/1792): 119 committed paired
  concepts (65 primes + 54 kernel-v0; molecules-v0 records carry no
  explication AST, hence no canonical vector — corpus text only) + 30
  synthetic single-edit minimal-contrast pairs (60 concepts; committed
  records contain zero single-edit pairs, detector-verified), the §2.3
  stratum housed in SEL by the stage_stats intersection below.

MOCK (--mock, $0, stdlib+numpy, no torch, no network): emits SYNTHETIC
mechanics-only outputs with a PLANTED gradient (12 ridge-CCA layers with
one structural admission each >= ceil(L/3) = 10) so the pinned analysis,
gates and verdict mapping resolve end-to-end. NEVER a measurement.

Fail-closed: ERR_DDC0_UNPINNED (null pins on a real run), ERR_DDC0_FIXTURE
(fixture missing/malformed), ERR_DDC0_COST (dry-plan over the $5 / 2 GPU-h
carve-out). This module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

MANIFEST_PATH = os.path.join(_HERE, "inputs", "ddc-manifest.json")


def log(msg):
    print(msg, flush=True)


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    raise SystemExit(1)


def det_u(*keys):
    h = hashlib.sha256(("|".join(str(k) for k in keys)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path):
    with open(path) as f:
        return json.load(f)


# --------------------------------------------------------------------------
# MOCK path — synthetic mechanics-only outputs, planted gradient
# --------------------------------------------------------------------------

MOCK_L = 30
MOCK_DIRS_PER_CELL = 3
MOCK_RIDGE_LAYERS = list(range(12))     # planted: 12 >= ceil(30/3) -> PASS
MOCK_PROC_LAYERS = list(range(5))
MOCK_LEXICAL = [(20, "ridge-cca", 0)]   # criteria 1-3 pass, bag fails


def run_mock(out_dir, manifest):
    os.makedirs(out_dir, exist_ok=True)
    suffix = "-mock"
    t_b = [0.5 * det_u("ddc0-tb", b) for b in range(1000)]
    rows = []
    for layer in range(MOCK_L):
        for method in ("ridge-cca", "procrustes"):
            planted = (method == "ridge-cca" and layer in MOCK_RIDGE_LAYERS) \
                or (method == "procrustes" and layer in MOCK_PROC_LAYERS)
            for j in range(MOCK_DIRS_PER_CELL):
                lex = (layer, method, j) in MOCK_LEXICAL
                if planted and j == 0:
                    row = {"test_score": 0.9, "carrier_half_cos": 0.95,
                           "minimal_contrast_p": 0.005,
                           "bag_delta_ci90_low": 0.05}
                elif lex:
                    row = {"test_score": 0.9, "carrier_half_cos": 0.9,
                           "minimal_contrast_p": 0.01,
                           "bag_delta_ci90_low": -0.02}
                else:
                    row = {"test_score":
                           0.30 * det_u("ddc0-s", layer, method, j),
                           "carrier_half_cos":
                           0.5 * det_u("ddc0-c", layer, method, j),
                           "minimal_contrast_p": 0.5,
                           "bag_delta_ci90_low": -0.1}
                row.update({"layer": layer, "method": method,
                            "dir_index": j})
                rows.append(row)
    cand_path = os.path.join(out_dir, "candidates-ddc0%s.jsonl" % suffix)
    with open(cand_path, "w") as f:
        for r in sorted(rows, key=lambda r: (r["layer"], r["method"],
                                             r["dir_index"])):
            f.write(json.dumps(r, sort_keys=True) + "\n")
    null_path = os.path.join(out_dir, "maxstat-null-ddc0%s.json" % suffix)
    with open(null_path, "w") as f:
        json.dump({"B": 1000, "seed": 1,
                   "family": "directions x layers x methods",
                   "mock_disclosure": "SYNTHETIC mechanics-only null — "
                                      "never a measurement",
                   "t_b": t_b}, f, sort_keys=True)
    probe_sha = hashlib.sha256(b"ddc0-mock-probe-fixture").hexdigest()
    sidecar = {
        "L": MOCK_L,
        "probe_fixture_sha_run1": probe_sha,
        "probe_fixture_sha_run2": probe_sha,
        "split": {"fit_sha256": hashlib.sha256(b"ddc0-mock-fit").hexdigest(),
                  "sel_sha256": hashlib.sha256(b"ddc0-mock-sel").hexdigest(),
                  "test_sha256":
                      hashlib.sha256(b"ddc0-mock-test").hexdigest(),
                  "n_fit": 71, "n_sel": 24, "n_test": 24,
                  "overlap_empty": True},
        "expected_methods": ["ridge-cca", "procrustes"],
        "expected_layers": MOCK_L,
        "expected_dirs_per_layer_per_method": 64,
        "c4_subspace_overlap_per_layer": {
            str(l): 0.55 + 0.3 * det_u("ddc0-c4", l) for l in range(MOCK_L)},
        "template_variance_top_pc": {"mean-pool": 0.31, "last-token": 0.44},
        "k_cap": 256,
        "mock_disclosure": "SYNTHETIC mechanics-only sidecar",
    }
    side_path = os.path.join(out_dir, "sidecar-ddc0%s.json" % suffix)
    with open(side_path, "w") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
    # A2 hand-off: t* + every candidate's model-space direction (mock:
    # coordinate unit vectors at the donor dimension)
    ts = sorted(t_b)
    t_star = ts[min(max(int(math.ceil(0.95 * (len(ts) + 1))) - 1, 0),
                    len(ts) - 1)]
    d = manifest["donors"]["r135"]["d_model"]
    dirs = {}
    for r in rows:
        if r["test_score"] > t_star:
            u = [0.0] * d
            u[(r["layer"] * 7 + r["dir_index"]) % d] = 1.0
            dirs["%d:%s:%d" % (r["layer"], r["method"],
                               r["dir_index"])] = u
    with open(os.path.join(out_dir, "a2-directions-ddc0%s.json" % suffix),
              "w") as f:
        json.dump({"t_star": t_star, "d": d, "directions": dirs,
                   "note": "candidate model-space directions; ADMISSION is "
                           "computed only by analysis/ddc0.py",
                   "mock_disclosure": "SYNTHETIC"}, f, sort_keys=True)
    results = {
        "experiment": "ddc0", "mode": "MOCK",
        "outcome": "MOCK-OK",
        "mock_disclosure": "SYNTHETIC mechanics-only stub outputs with a "
                           "planted gradient so gates/analysis/verdict "
                           "mapping resolve — never a measurement",
        "files": {"candidates": os.path.basename(cand_path),
                  "maxstat_null": os.path.basename(null_path),
                  "sidecar": os.path.basename(side_path)},
        "candidates_sha256": sha256_file(cand_path),
        "n_candidate_rows": len(rows),
        "pins": {"ddc_manifest_sha256": sha256_file(MANIFEST_PATH)},
        "wallClockHours": 0.0,
        "usd": 0.0,
    }
    with open(os.path.join(out_dir, "results-ddc0%s.json" % suffix),
              "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    log("ddc0 MOCK -> %s (%d candidate rows, planted "
        "n_layers_admitted=12)" % (out_dir, len(rows)))


# --------------------------------------------------------------------------
# dry-plan (fail-closed on the ddc0 carve-out)
# --------------------------------------------------------------------------

def dry_plan(manifest):
    cm = manifest["cost_model"]
    bud = manifest["budgets"]
    # probe stage (GPU): ~119 concepts x 4 carriers x 2 renders x 2 runs
    # + 4 empty carriers + 2 corpora x 4096 sequences of <=256 tokens
    probe_fwd = 119 * 4 * 2 + 4 + 2 * 4096
    gpu_h = probe_fwd * (256.0 / 8.0) / 3600.0 / 100.0  # tok-batched est.
    gpu_h = max(gpu_h, cm["g0_gpu_hours"] * 0.4)
    gpu_h = cm["g0_gpu_hours"]              # conservative pinned figure
    usd_gpu = gpu_h * cm["usd_per_gpu_hour_a10g"]
    # stats stage (CPU container): B=1000 full-pipeline replicates,
    # measured locally at small scale then scaled; planning figure below
    cpu_h = 6.0
    usd_cpu = cpu_h * 0.20                  # Modal CPU-core pricing band
    usd = usd_gpu + usd_cpu
    print("ddc0 DRY PLAN (conservative):")
    print("  probe stage: ~%d forwards, est %.2f GPU-h, $%.2f"
          % (probe_fwd, gpu_h, usd_gpu))
    print("  stats stage: est %.1f CPU-h (checkpointed, resumable), $%.2f"
          % (cpu_h, usd_cpu))
    print("  TOTAL est $%.2f vs usd_cap $%.2f; %.2f GPU-h vs cap %.2f"
          % (usd, bud["ddc0_usd_cap"], gpu_h, bud["ddc0_gpu_hours_cap"]))
    if usd > bud["ddc0_usd_cap"]:
        die("ERR_DDC0_COST", "estimate $%.2f exceeds the ddc0 $%.2f "
            "carve-out — DO NOT LAUNCH" % (usd, bud["ddc0_usd_cap"]))
    if gpu_h > bud["ddc0_gpu_hours_cap"]:
        die("ERR_DDC0_COST", "GPU estimate %.2f h exceeds the %.2f GPU-h "
            "carve-out" % (gpu_h, bud["ddc0_gpu_hours_cap"]))
    print("  dry-plan GREEN (fail-closed caps honoured)")
    return {"usd": usd, "gpu_hours": gpu_h, "cpu_hours": cpu_h}


# --------------------------------------------------------------------------
# REAL path — probe stage (GPU) and stats stage (CPU)
# --------------------------------------------------------------------------

def _load_fixture(path):
    if not os.path.isfile(path):
        die("ERR_DDC0_FIXTURE", "no probe fixture at %r (built + pinned at "
            "T0; see module docstring for the schema)" % path)
    fx = json.load(open(path))
    for k in ("determinism", "empty_carriers", "concepts",
              "minimal_contrast_pairs"):
        if k not in fx:
            die("ERR_DDC0_FIXTURE", "fixture missing %r" % k)
    if len(fx["empty_carriers"]) != 4:
        die("ERR_DDC0_FIXTURE", "P=4 fixed carriers required (ASM-1700)")
    return fx


def stage_probe(args, manifest):
    import numpy as np

    import ddc_selection as sel
    donor = manifest["donors"]["r135"]
    if not donor.get("revision"):
        die("ERR_DDC0_UNPINNED", "r135 donor revision is null — pin the "
            "BASE revision at T0 before any real run")
    fx = _load_fixture(args.probe_fixture)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(donor["repo"],
                                        revision=donor["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        donor["repo"], revision=donor["revision"],
        torch_dtype=torch.float32).to(args.device).eval()
    L = donor["n_layers"]
    d = donor["d_model"]
    concepts = fx["concepts"]
    n = len(concepts)
    log("probe stage: %d concepts, L=%d, d=%d" % (n, L, d))
    # empty-carrier activations (matched subtraction, §2.3)
    empt = sel.collect_boundary_activations(model, tok,
                                            fx["empty_carriers"],
                                            args.device)
    H = {"mean": np.zeros((L, n, d)), "last": np.zeros((L, n, d))}
    H12 = np.zeros((L, n, d))
    H34 = np.zeros((L, n, d))
    for ci, c in enumerate(concepts):
        per_carrier = {"mean": [], "last": []}
        for k in range(4):
            acts = sel.collect_boundary_activations(model, tok,
                                                    c["carriers"][k],
                                                    args.device)
            for pool in ("mean", "last"):
                inst = acts[pool].mean(axis=0)          # avg render insts
                inst = inst - empt[pool][k]             # empty-carrier sub
                per_carrier[pool].append(inst)
        for pool in ("mean", "last"):
            stack = np.stack(per_carrier[pool])         # (4, L, d)
            H[pool][:, ci, :] = stack.mean(axis=0)
        H12[:, ci, :] = np.stack(per_carrier["mean"][:2]).mean(axis=0)
        H34[:, ci, :] = np.stack(per_carrier["mean"][2:]).mean(axis=0)
        if (ci + 1) % 10 == 0:
            log("  probes %d/%d" % (ci + 1, n))
    for arr in (H["mean"], H["last"], H12, H34):        # grand-mean centre
        arr -= arr.mean(axis=1, keepdims=True)
    V = np.array([c["vector"] for c in concepts], dtype=np.float64)
    V_bag = np.array([c["bag_vector"] for c in concepts], dtype=np.float64)
    V -= V.mean(axis=0)                                 # column-centred
    V_bag -= V_bag.mean(axis=0)
    # corpus second moments: K-static + C4 (overlap diagnostic, ASM-1662)
    corpora = manifest["corpora"]
    mom = {}
    for name in ("ddc-kernel-static-v1", "ddc-c4-sample-v1"):
        texts = sel.load_corpus_texts(
            os.path.join(args.data_root, os.path.basename(
                corpora[name]["path"])))
        mom[name], _ntok = sel.collect_second_moments(
            model, tok, texts, args.device, batch_log=log)
    ker_spec, _ev = sel.pca_full_bases(mom["ddc-kernel-static-v1"],
                                       "ddc-kernel-static-v1")
    c4_spec, _ev2 = sel.pca_full_bases(mom["ddc-c4-sample-v1"],
                                       "ddc-c4-sample-v1")
    import g0_stats as G
    r_work = int(math.ceil(manifest["primary_rho"] * d))
    c4_overlap = G.c4_subspace_overlap(ker_spec["bases"], c4_spec["bases"],
                                       r_work)
    census = sel.massive_activation_directions(mom["ddc-kernel-static-v1"])
    os.makedirs(args.out_dir, exist_ok=True)
    np.savez_compressed(
        os.path.join(args.out_dir, "probe-artifact.npz"),
        H_mean=H["mean"], H_last=H["last"], H12=H12, H34=H34,
        V=V, V_bag=V_bag,
        concept_ids=np.array([c["id"] for c in concepts]),
        classes=np.array([c["class"] for c in concepts]),
        census=np.array(census),
        template_mean=G.template_variance_top_pc(H["mean"]),
        template_last=G.template_variance_top_pc(H["last"]))
    with open(os.path.join(args.out_dir, "c4-overlap.json"), "w") as f:
        json.dump({"r_work": r_work, "overlap": c4_overlap}, f,
                  sort_keys=True)
    log("probe artifact -> %s" % args.out_dir)


def stage_stats(args, manifest):
    import numpy as np

    import g0_stats as G
    art_path = os.path.join(args.artifact or args.out_dir,
                            "probe-artifact.npz")
    if not os.path.isfile(art_path):
        die("ERR_DDC0_FIXTURE", "no probe artifact at %r (run --stage "
            "probe first)" % art_path)
    art = np.load(art_path, allow_pickle=False)
    fx = _load_fixture(args.probe_fixture)
    g0cfg = manifest["g0"]
    ids = [str(x) for x in art["concept_ids"]]
    classes = [str(x) for x in art["classes"]]
    splits = G.make_splits(ids, classes, seed=g0cfg["split_seed"])
    id_to_idx = {cid: i for i, cid in enumerate(ids)}
    sel_set = set(splits["sel"])
    mc_idx = sorted({id_to_idx[a] for pair in fx["minimal_contrast_pairs"]
                     for a in pair if id_to_idx.get(a) in sel_set
                     and id_to_idx.get(pair[0]) is not None})
    # FORK-2 routing: last-token joins the max-stat family ONLY if the
    # mean-pool diagnostic is template-dominated (§2.3 / ASM-1701)
    tmpl_mean = float(art["template_mean"])
    poolings = ("mean",) if tmpl_mean <= g0cfg["template_var_max"] \
        else ("mean", "last")
    ck_path = os.path.join(args.out_dir, "null-checkpoint.jsonl")
    done = {}
    if os.path.exists(ck_path):
        for line in open(ck_path):
            if line.strip():
                rec = json.loads(line)
                done[int(rec["b"])] = float(rec["t"])
        log("resuming null from checkpoint: %d/%d replicates" %
            (len(done), g0cfg["B"]))
    ck_fh = open(ck_path, "a")

    def checkpoint(b, t):
        ck_fh.write(json.dumps({"b": b, "t": t}) + "\n")
        ck_fh.flush()

    H_by_pool = {"mean": art["H_mean"], "last": art["H_last"]}
    t0 = time.time()
    rows, t_b, lambdas = G.run_g0(
        H_by_pool, art["H12"], art["H34"], art["V"], art["V_bag"],
        splits, mc_idx, B=g0cfg["B"], perm_seed=g0cfg["perm_seed"],
        crit_seed=g0cfg["perm_seed"], family_poolings=poolings,
        log=log, workers=args.workers, null_done=done,
        null_checkpoint=checkpoint)
    ck_fh.close()
    os.makedirs(args.out_dir, exist_ok=True)
    cand_path = os.path.join(args.out_dir, "candidates-ddc0.jsonl")
    with open(cand_path, "w") as f:
        for r in rows:
            slim = {k: v for k, v in r.items() if k != "u"}
            f.write(json.dumps(slim, sort_keys=True) + "\n")
    with open(os.path.join(args.out_dir, "maxstat-null-ddc0.json"),
              "w") as f:
        json.dump({"B": g0cfg["B"], "seed": g0cfg["perm_seed"],
                   "family": "directions x layers x methods"
                             + (" x poolings" if len(poolings) > 1 else ""),
                   "t_b": t_b}, f, sort_keys=True)
    ts = sorted(t_b)
    t_star = ts[min(max(int(math.ceil(0.95 * (len(ts) + 1))) - 1, 0),
                    len(ts) - 1)]
    with open(os.path.join(args.out_dir, "a2-directions-ddc0.json"),
              "w") as f:
        json.dump({"t_star": t_star, "d": int(art["V"].shape[1]),
                   "directions": {"%d:%s:%d" % (r["layer"], r["method"],
                                                r["dir_index"]): r["u"]
                                  for r in rows},
                   "note": "candidate model-space directions; ADMISSION is "
                           "computed only by analysis/ddc0.py"},
                  f, sort_keys=True)

    def split_sha(idx):
        return hashlib.sha256(
            ("\n".join(ids[i] for i in idx)).encode()).hexdigest()

    overlap = json.load(open(os.path.join(
        args.artifact or args.out_dir, "c4-overlap.json")))["overlap"]
    fx_sha = fx["determinism"]
    sidecar = {
        "L": int(art["H_mean"].shape[0]),
        "probe_fixture_sha_run1": fx_sha["sha_run1"],
        "probe_fixture_sha_run2": fx_sha["sha_run2"],
        "split": {"fit_sha256": split_sha(splits["fit"]),
                  "sel_sha256": split_sha(splits["sel"]),
                  "test_sha256": split_sha(splits["test"]),
                  "n_fit": len(splits["fit"]), "n_sel": len(splits["sel"]),
                  "n_test": len(splits["test"]),
                  "overlap_empty": not (set(splits["fit"])
                                        & set(splits["sel"])
                                        | set(splits["fit"])
                                        & set(splits["test"])
                                        | set(splits["sel"])
                                        & set(splits["test"]))},
        "expected_methods": ["ridge-cca", "procrustes"],
        "expected_layers": int(art["H_mean"].shape[0]),
        "expected_dirs_per_layer_per_method":
            min(g0cfg["j_max"], len(splits["fit"]) - 1),
        "c4_subspace_overlap_per_layer": overlap,
        "template_variance_top_pc": {"mean-pool": tmpl_mean,
                                     "last-token":
                                         float(art["template_last"])},
        "k_cap": g0cfg["k_cap"],
        "lambda_selected": lambdas,
        "family_poolings": list(poolings),
    }
    with open(os.path.join(args.out_dir, "sidecar-ddc0.json"), "w") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
    wall = (time.time() - t0) / 3600.0
    with open(os.path.join(args.out_dir, "results-ddc0.json"), "w") as f:
        json.dump({"experiment": "ddc0", "mode": "REAL",
                   "outcome": "STATS-COMPLETE",
                   "candidates_sha256": sha256_file(cand_path),
                   "n_candidate_rows": len(rows),
                   "pins": {"ddc_manifest_sha256":
                            sha256_file(MANIFEST_PATH),
                            "probe_fixture_sha": fx_sha["sha_run1"]},
                   "wallClockHours": wall}, f, indent=1, sort_keys=True)
    log("ddc0 stats -> %s (%d rows, t*=%.4f, %.2f h)"
        % (args.out_dir, len(rows), t_star, wall))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--stage", default="stats",
                    choices=("probe", "stats"))
    ap.add_argument("--manifest", default=MANIFEST_PATH)
    ap.add_argument("--probe-fixture",
                    default=os.path.join(_ROOT, "data",
                                         "ddc-probe-fixture-v1",
                                         "probe-fixture.json"))
    ap.add_argument("--data-root", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--artifact", default="",
                    help="dir holding probe-artifact.npz (default out-dir)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    manifest = load_manifest(args.manifest)
    if args.dry_plan:
        dry_plan(manifest)
        return
    if args.mock:
        run_mock(args.out_dir, manifest)
        return
    if args.stage == "probe":
        stage_probe(args, manifest)
    else:
        stage_stats(args, manifest)


if __name__ == "__main__":
    main()
