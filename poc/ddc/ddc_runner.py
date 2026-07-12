#!/usr/bin/env python3
"""ddc1 arm-campaign runner — docs/next/design/DDC.md §§2-5, §8; DRAFT
record registry/experiments/ddc1.json (freeze-before-run; the coordinator
freezes BEFORE any final-phase run).

One invocation scores one or more (rung, arm, rho, seed) CELLS: builds
the arm's basis (ddc_selection — LAW-1: selection only), performs the
rotate-and-slice / magnitude surgery (ddc_surgery — the only
weights-touching module, kernel-blind by construction), evaluates through
the PINNED poc/pubeval scoring path (byte-identical prompts/seed/scoring
across arms; per-item emission via the ASM-1655 sidecar), and emits:

  items-ddc1[-mock].jsonl   one row per scored item x cell
                            {task,item_id,rung,arm,rho,seed,correct,subset}
  cells-ddc1[-mock].json    per-cell {gold_ppl_arc_easy, params_retained,
                            energy_capture, present, ...}
  results-ddc1[-mock].json  shard metadata: pins, i1 results, t0_block,
                            cost — the merge_shards.py contract

The campaign launches as INDEPENDENT Modal jobs (one per cell; see
modal/modal_ddc.py --print-jobs) splittable across accounts; poc/ddc/
merge_shards.py reconstructs the canonical analysis inputs, byte-identical
to a monolithic run (validate_mock.py proves parity at $0).

MOCK (--mock, $0, stdlib, no torch): pubeval's OWN mock fixtures and
scoring mechanics with a planted per-arm skill gradient (A1 > M1/R1 at
rho=0.75; C1@0.9 above the I-2 tripwire) so every pinned-analysis field,
gate and verdict-rule resolves end-to-end. SYNTHETIC — never a
measurement.

REAL cells additionally require: --t0-block (the T0 campaign block:
filter_set, power_sim_result, license/parity gates — assembled by the
runner identity at T0 and staged byte-identical to every shard), pinned
donor revisions + corpus shas in inputs/ddc-manifest.json, and for A2 the
ddc0 analysis output + a2-directions artifact. Everything fails closed:
ERR_DDC_UNPINNED, ERR_DDC_T0_BLOCK, ERR_DDC_A2_INPUTS,
ERR_DDC_BASIS_DEFICIENT (never silently patched), ERR_DDC_LAW1_TAINT.

This module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_PUBEVAL = os.path.join(_ROOT, "poc", "pubeval")
sys.path.insert(0, _HERE)
sys.path.insert(0, _PUBEVAL)

import benchmarks as B  # noqa: E402  (pubeval, stdlib-only)
import ddc_common as C  # noqa: E402
import pubeval_runner as PE  # noqa: E402

MOCK_BASE_SKILL = 0.75

# Planted MOCK retention factors (SYNTHETIC; A1 > M1/R1 so the primary
# resolves PASS on mock mechanics; C1@0.9 > 1 so tripwire I-2 passes).
MOCK_FACTORS = {
    "A0": {1.0: 1.0},
    "A1": {0.9: 0.99, 0.75: 0.97, 0.5: 0.90, 0.3: 0.62, 0.15: 0.42},
    "A2": {0.75: 1.00, 0.5: 0.93},
    "A3": {0.9: 0.98, 0.75: 0.95, 0.5: 0.88, 0.3: 0.60, 0.15: 0.40},
    "M1": {0.9: 0.90, 0.75: 0.50, 0.5: 0.44, 0.3: 0.30, 0.15: 0.22},
    "M2": {0.75: 0.48, 0.5: 0.42},
    "R1": {0.9: 0.91, 0.75: 0.55, 0.5: 0.48, 0.3: 0.32, 0.15: 0.24},
    "C1": {0.9: 1.15, 0.75: 0.88, 0.5: 0.78, 0.3: 0.52, 0.15: 0.36},
    "C2": {0.9: 0.94, 0.75: 0.84, 0.5: 0.74, 0.3: 0.48, 0.15: 0.33},
    "C3": {0.9: 0.90, 0.75: 0.66, 0.5: 0.55, 0.3: 0.40, 0.15: 0.28},
}

MOCK_BASE_PARAMS = {"r135": 134515008, "r360": 361821120}


def log(msg):
    print(msg, flush=True)


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    raise SystemExit(1)


class ArmStub(PE.StubLM):
    """pubeval StubLM with a planted arm/rho-dependent skill — the mock
    gradient rides through pubeval's REAL scoring mechanics. score_options
    is overridden so the planted pick reliably wins BOTH argmaxes (the
    stock stub's noise band can swamp a planted cross-arm gradient at
    mock item counts); higher skill also yields lower gold_ppl, so the
    fluency-guard ordering is exercised too."""

    def __init__(self, seed_key, skill):
        super().__init__(seed_key)
        self.SKILL = skill
        self.name = "stub-ddc1:%s" % seed_key

    def score_options(self, context, options, gold, item_id):
        pick = gold if PE.det_u("mc", self.seed, item_id) < self.SKILL \
            else ((gold + 1) % len(options))
        outs = []
        for i, opt in enumerate(options):
            n = max(1, len(opt.split()))
            per_char = -3.0 - PE.det_u("lp", self.seed, item_id, i)
            if i == pick:
                per_char = -1.0 - 0.5 * PE.det_u("lp2", self.seed, item_id)
            outs.append((per_char * len(opt), n))
        return outs


def parse_cells(manifest, rungs, arms, rhos, seeds):
    cells = []
    for rung in [r.strip() for r in rungs.split(",") if r.strip()]:
        if rung not in manifest["arm_coverage"]:
            die("ERR_DDC_ARGS", "unknown rung %r" % rung)
        cov = manifest["arm_coverage"][rung]
        want_arms = [a.strip() for a in arms.split(",") if a.strip()] \
            if arms else sorted(cov)
        for arm in want_arms:
            if arm not in cov:
                die("ERR_DDC_ARGS", "arm %r not in %s coverage (ASM-1654)"
                    % (arm, rung))
            spec = cov[arm]
            arm_rhos = [float(r) for r in rhos.split(",") if r.strip()] \
                if rhos else spec["rhos"]
            arm_seeds = [int(s) for s in seeds.split(",") if s.strip()] \
                if seeds else spec["seeds"]
            for rho in arm_rhos:
                if float(rho) not in [float(x) for x in spec["rhos"]]:
                    die("ERR_DDC_ARGS", "rho %r not in %s/%s coverage"
                        % (rho, rung, arm))
                for seed in arm_seeds:
                    if seed not in spec["seeds"]:
                        die("ERR_DDC_ARGS", "seed %r not in %s/%s coverage"
                            % (seed, rung, arm))
                    cells.append((rung, arm, float(rho), int(seed)))
    return cells


def eval_cell(lm, manifest, rung, arm, rho, seed, subset, mock):
    """One pubeval pass; returns (rows, bench_results). The scoring path
    is pubeval's own (ASM-1655): prompts, few-shot exemplars, seed and
    scoring code byte-identical across every arm."""
    rows = []

    def item_log(rec):
        rows.append({"task": rec["bench"], "item_id": rec["item_id"],
                     "rung": rung, "arm": arm, "rho": rho, "seed": seed,
                     "correct": int(rec["acc_norm"] if rec["kind"] == "mc"
                                    else rec["em"]),
                     "subset": 1 if subset else 0})

    n = manifest["subset_items_per_task"] if subset else 0
    results, _agg = PE.evaluate(
        lm, manifest["eval"]["benchmarks"], os.path.join(_PUBEVAL, "data"),
        n, manifest["eval"]["shots"], manifest["eval"]["seed"], mock,
        log=lambda *_a, **_k: None, item_log=item_log)
    return rows, results


def cell_outputs(results, rung, arm, rho, seed, params, energy, extra=None):
    entry = {"rung": rung, "arm": arm, "rho": rho, "seed": seed,
             "gold_ppl_arc_easy": results["arc_easy"]["gold_ppl"],
             "params_retained": params, "energy_capture": energy,
             "present": True}
    if extra:
        entry.update(extra)
    return entry


# --------------------------------------------------------------------------
# MOCK cells
# --------------------------------------------------------------------------

def run_cell_mock(manifest, rung, arm, rho, seed):
    factor = MOCK_FACTORS[arm].get(rho)
    if factor is None:
        die("ERR_DDC_ARGS", "no mock factor for %s@%s" % (arm, rho))
    skill = min(0.98, MOCK_BASE_SKILL * factor)
    subset = rho in manifest["subset_rhos"]
    lm = ArmStub("ddc1|%s|%s|%g|%d" % (rung, arm, rho, seed), skill)
    rows, results = eval_cell(lm, manifest, rung, arm, rho, seed, subset,
                              mock=True)
    base = MOCK_BASE_PARAMS[rung]
    if arm == "A0":
        params = base
    else:
        params = int(base * (0.30 + 0.70 * rho))
        if arm == "M1":
            params += 4096          # raised r' covers bridge overhead
    energy = None if arm == "M2" else 0.999
    cell = cell_outputs(results, rung, arm, rho, seed, params, energy,
                        {"mock": True})
    i1 = None
    if arm in ("A1", "A2", "A3", "C1", "C2", "C3", "R1"):
        i1 = {"median_kl": 1e-07, "top1_agreement": 1.0,
              "n_positions": 64, "pass": True, "mock": True}
    return rows, cell, i1


# --------------------------------------------------------------------------
# REAL cells (torch; runs on the pinned Modal image)
# --------------------------------------------------------------------------

def _load_donor(manifest, rung, device):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    donor = manifest["donors"][rung]
    if not donor.get("revision"):
        die("ERR_DDC_UNPINNED", "%s donor revision is null — pinned at T0 "
            "before any real run (ERR_UNPINNED_MODEL discipline)" % rung)
    tok = AutoTokenizer.from_pretrained(donor["repo"],
                                        revision=donor["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        donor["repo"], revision=donor["revision"],
        torch_dtype=torch.float32).to(device).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, tok, donor


def _basis_for(manifest, args, arm, seed, model, tok, donor):
    """Arm -> BasisSpec (LAW-1: only model-side constructions reach the
    surgery seam). Returns (spec, census_dirs)."""
    import ddc_selection as sel
    L = donor["n_layers"]
    d = donor["d_model"]
    if arm == "R1":
        return sel.haar_full_bases(d, L, seed), None
    corpus_name = manifest["arms_calibration"][arm if arm != "A2" else "A1"]
    corpus_dir = os.path.join(args.data_root,
                              os.path.basename(
                                  manifest["corpora"][corpus_name]["path"]))
    texts = sel.load_corpus_texts(corpus_dir)
    moments, _ntok = sel.collect_second_moments(
        model, tok, texts, args.device,
        max_tokens=manifest["surgery"]["max_seq_tokens"], batch_log=log)
    spec, _eigvals = sel.pca_full_bases(moments, corpus_name)
    census = sel.massive_activation_directions(moments)
    if arm != "A2":
        return spec, census
    # A2: max-stat-admitted directions from the ddc0 READOUT (analysis
    # output; admission never recomputed here) + complement top-up
    if not (args.ddc0_analysis and os.path.isfile(args.ddc0_analysis)
            and args.ddc0_directions
            and os.path.isfile(args.ddc0_directions)):
        die("ERR_DDC_A2_INPUTS", "A2 needs --ddc0-analysis (pinned "
            "analysis stdout of the ddc0 run) and --ddc0-directions "
            "(a2-directions artifact)")
    a0 = json.load(open(args.ddc0_analysis))["analysis"]
    if a0.get("killed_by_g0"):
        die("ERR_DDC_A2_INPUTS", "ddc0 read out killed-by-G0 — the A2 arm "
            "is dropped, not run (G0 routing, DDC.md section 8)")
    dirs = json.load(open(args.ddc0_directions))
    winning = a0["winning_method"]
    lexical = set(a0["bag_of_primes_lexical_flags"])
    admitted = []
    for key in a0["max_stat_p_admitted"]:
        if key in lexical:
            continue                     # lexical-only: never basis-eligible
        layer_s, method, dir_s = key.split(":")
        if method != winning:
            continue
        u = dirs["directions"].get(key)
        if u is None:
            die("ERR_DDC_A2_INPUTS", "admitted key %r missing from the "
                "a2-directions artifact" % key)
        admitted.append({"layer": int(layer_s), "dir_index": int(dir_s),
                         "test_score": 1.0, "u": u})
    # null-beating ordering uses TEST score - t*; scores live in the
    # candidates file — the directions artifact stores them alongside
    for a in admitted:
        key = "%d:%s:%d" % (a["layer"], winning, a["dir_index"])
        a["test_score"] = dirs.get("scores", {}).get(
            key, a["test_score"])
    a2 = sel.a2_assemble(admitted, dirs["t_star"], spec,
                         1.0, d)          # full-width; sliced at surgery
    a2["meta"]["ddc0_winning_method"] = winning
    return a2, census


def run_cell_real(manifest, args, rung, arm, rho, seed):
    import ddc_surgery as S
    subset = rho in manifest["subset_rhos"]
    t_start = time.time()
    model, tok, donor = _load_donor(manifest, rung, args.device)
    i1 = None
    extra = {}
    if arm == "A0":
        lm = PE.HFLM.from_model(model, tok, "ddc1-a0-%s" % rung,
                                device=args.device)
        params = sum(p.numel() for p in model.parameters())
        energy = 1.0
    else:
        spec = None
        if arm in ("M1", "M2"):
            # matched retained count (ASM-1657): rotated-arm count at this
            # grid point, computed exactly from a throwaway rotated twin
            twin = copy.deepcopy(model)
            import ddc_selection as sel
            haar = sel.haar_full_bases(donor["d_model"],
                                       donor["n_layers"], 0)
            S.assert_basis_provenance(haar)
            info = S.rotate_and_slice(twin, haar, rho)
            target = info["params_retained"]
            del twin
            if arm == "M1":
                info = S.magnitude_structured(model, target)
                extra["r_prime"] = info["r_prime"]
            else:
                info = S.magnitude_unstructured(model, target)
                extra["dense_param_count"] = info["dense_param_count"]
            params = info["params_retained"]
            energy = None
        else:
            spec, census = _basis_for(manifest, args, arm, seed, model,
                                      tok, donor)
            S.assert_basis_provenance(spec)      # LAW-1 mechanical gate
            # gate I-1: rotation-only (r=d) logit equivalence vs donor
            import torch
            probe_dir = os.path.join(
                args.data_root, os.path.basename(
                    manifest["corpora"]["ddc-kernel-static-v1"]["path"]))
            import ddc_selection as sel
            probe_texts = sel.load_corpus_texts(
                probe_dir)[:manifest["gates"]["i1_probe_sequences"]]
            batches = []
            for t in probe_texts:
                ids = tok.encode(t, add_special_tokens=False)[
                    :manifest["surgery"]["max_seq_tokens"]]
                if ids:
                    batches.append(torch.tensor([ids], device=args.device))
            rot = copy.deepcopy(model)
            S.rotate_and_slice(rot, spec, 1.0)
            i1 = S.i1_check(model, rot, batches,
                            manifest["gates"]["i1_kl_median_max"])
            del rot
            if not i1["pass"]:
                log("GATE I-1 FAILED for %s@%s (median_kl=%.3e, top1=%.4f)"
                    " — recorded; kill (a) fires after one debugging "
                    "iteration (DDC.md section 8)"
                    % (arm, rho, i1["median_kl"], i1["top1_agreement"]))
            info = S.rotate_and_slice(model, spec, rho)
            params = info["params_retained"]
            extra["bridges"] = info["bridges"]
            if arm == "A2":
                extra["aligned_budget_fraction"] = \
                    spec["meta"]["aligned_budget_fraction"]
            r = info["r"]
            if census is not None:
                import numpy as np
                energy = min(
                    sel.energy_capture(
                        np.asarray(spec["bases"][l])[:, :r], census[l])
                    for l in range(donor["n_layers"]))
            else:
                energy = None
        extra["packed_bytes_fp32"] = S.packed_bytes_fp32(model)
        lm = PE.HFLM.from_model(model, tok,
                                "ddc1-%s-rho%g-s%d" % (arm, rho, seed),
                                device=args.device)
    rows, results = eval_cell(lm, manifest, rung, arm, rho, seed, subset,
                              mock=False)
    cell = cell_outputs(results, rung, arm, rho, seed, params, energy,
                        extra)
    wall = (time.time() - t_start) / 3600.0
    return rows, cell, i1, wall


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--tier", default="all",
                    help="dry-plan tier: t0|ddc0|s1|s2|all")
    ap.add_argument("--rungs", default="r135",
                    help="csv of rungs (r135,r360); monolithic full "
                         "campaign = --rungs r135,r360")
    ap.add_argument("--arms", default="")
    ap.add_argument("--rhos", default="")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--shard-tag", default="")
    ap.add_argument("--t0-block", default="",
                    help="REAL runs: path to the staged T0 campaign block")
    ap.add_argument("--ddc0-analysis", default="")
    ap.add_argument("--ddc0-directions", default="")
    ap.add_argument("--data-root", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--manifest", default=C.MANIFEST_PATH)
    ap.add_argument("--gpu-class", default="A10G")
    args = ap.parse_args()
    manifest = C.load_manifest(args.manifest)

    if args.dry_plan:
        if args.tier == "all":
            C.dry_plan_campaign(manifest)
        else:
            C.dry_plan_tier(manifest, args.tier)
        return

    cells = parse_cells(manifest, args.rungs, args.arms, args.rhos,
                        args.seeds)
    if args.mock:
        t0_block = C.mock_t0_block(manifest)
    else:
        only_a0 = all(arm == "A0" for (_rg, arm, _rho, _s) in cells)
        if args.t0_block and os.path.isfile(args.t0_block):
            t0_block = json.load(open(args.t0_block))
        elif only_a0:
            t0_block = None       # the A0 baseline job PRODUCES the T0
                                  # inputs (filter fixing); it cannot need
                                  # them — merger requires >=1 non-null
        else:
            die("ERR_DDC_T0_BLOCK", "real non-A0 runs need --t0-block "
                "(the T0 campaign block staged byte-identical to every "
                "shard)")
        for name, pin in manifest["corpora"].items():
            if name.startswith("_"):
                continue
            if pin["sha256"] is None and name not in (
                    "ddc-probe-fixture-v1",):
                die("ERR_DDC_UNPINNED", "corpus %s sha is null — corpora "
                    "are built + pinned at T0 (gate I-3)" % name)

    all_rows, all_cells, i1_map = [], [], {}
    gpu_hours = 0.0
    t_run = time.time()
    for (rung, arm, rho, seed) in cells:
        tag = "%s/%s@rho%g/s%d" % (rung, arm, rho, seed)
        log("cell %s ..." % tag)
        if args.mock:
            rows, cell, i1 = run_cell_mock(manifest, rung, arm, rho, seed)
            wall = 0.0
        else:
            rows, cell, i1, wall = run_cell_real(manifest, args, rung,
                                                 arm, rho, seed)
        all_rows.extend(rows)
        all_cells.append(cell)
        if i1 is not None:
            i1_map["%s:%s:%g:%d" % (rung, arm, rho, seed)] = i1
        gpu_hours += wall
        log("cell %s done (%d item rows)" % (tag, len(rows)))

    rate = manifest["cost_model"]["usd_per_gpu_hour_a10g"]
    results = {
        "experiment": "ddc1",
        "mode": "MOCK" if args.mock else "REAL",
        "outcome": "MOCK-OK" if args.mock else "SHARD-COMPLETE",
        "shard_tag": args.shard_tag or None,
        "rungs": args.rungs,
        "cells_run": [[rg, a, r, s] for (rg, a, r, s) in cells],
        "pins": {
            "ddc_manifest_sha256": C.sha256_file(args.manifest),
            "corpora": {k: (v["sha256"] or "PINNED-AT-INPUTS")
                        for k, v in manifest["corpora"].items()
                        if not k.startswith("_")},
            "donor_revisions": {k: (v["revision"] or "PINNED-AT-INPUTS")
                                for k, v in manifest["donors"].items()},
        },
        "t0_block": t0_block,
        "i1": i1_map,
        "wallClockHours": round((time.time() - t_run) / 3600.0, 4),
        "gpu_hours": round(0.0 if args.mock else gpu_hours, 4),
        "usd_estimate": round(0.0 if args.mock else gpu_hours * rate, 4),
        "mock_disclosure": ("SYNTHETIC mechanics-only stub outputs with a "
                            "planted gradient — never a measurement"
                            if args.mock else None),
    }
    os.makedirs(args.out_dir, exist_ok=True)
    suffix = "-mock" if args.mock else ""
    all_rows.sort(key=C.row_sort_key)
    items_path = os.path.join(args.out_dir,
                              "items-ddc1%s.jsonl" % suffix)
    with open(items_path, "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    results["n_rows"] = len(all_rows)
    results["records_file"] = os.path.basename(items_path)
    results["records_sha256"] = C.sha256_file(items_path)
    with open(os.path.join(args.out_dir, "cells-ddc1%s.json" % suffix),
              "w") as f:
        json.dump({"cells": sorted(
            all_cells, key=lambda c: (c["rung"], c["arm"],
                                      float(c["rho"]), int(c["seed"])))},
            f, indent=1, sort_keys=True)
    with open(os.path.join(args.out_dir, "results-ddc1%s.json" % suffix),
              "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    log("shard -> %s (%d cells, %d rows)" % (args.out_dir, len(cells),
                                             len(all_rows)))
    # monolithic convenience: a full-coverage single invocation also emits
    # the canonical finalised analysis inputs (parity target for merger)
    if not args.shard_tag:
        rows_by = [json.loads(l) for l in open(items_path)]
        cells_by = json.load(open(os.path.join(
            args.out_dir, "cells-ddc1%s.json" % suffix)))["cells"]
        C.finalize([(results, rows_by, cells_by)],
                   os.path.join(args.out_dir, "final"), args.mock,
                   manifest)
        log("monolithic finalisation -> %s/final" % args.out_dir)


if __name__ == "__main__":
    main()
