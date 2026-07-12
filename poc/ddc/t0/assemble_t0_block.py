#!/usr/bin/env python3
"""DDC T0 ops — measured-pool extraction, power-sim invocation, and
mechanical t0-block assembly (docs/next/design/DDC.md section 6 T0 row;
gate I-5 v3 ASM-1720; runner-identity tooling — no design judgement here).

Two phases (both $0, CPU):

PHASE 1 — after the t0 tier's A0 r135 shard is collected:
    python3 poc/ddc/t0/assemble_t0_block.py --a0-shard <collected-dir> \
        --pool-out poc/ddc/t0/t0-pool.json --pool-only
  Recomputes per-task A0 accuracy from the per-item rows, applies the
  ASM-1655 informative-task filter (accuracy >= chance + 0.10, chance from
  inputs/ddc-manifest.json), writes the measured pool
  {"tasks":[{"task","n_items","a0_accuracy"}...]} over the FILTERED tasks,
  and prints the exact pinned gate I-5 v3 invocation:
    python3 poc/ddc/power_sim_ddc1.py --pool <pool> --out <result> \
        --campaigns 2000 --bootstrap 10000 --seed 20260712
  (NEVER --quick: analysis/ddc1.py rejects quick_mode results. The
  simulation is CPU-heavy — hours on a 2-core box; nice it or run it on a
  Modal CPU container.)

PHASE 2 — after the power sim AND the ddc0 readout:
    python3 poc/ddc/t0/assemble_t0_block.py --a0-shard <dir> \
        --power-result <result.json> --ddc0-analysis <ddc0-analysis.json> \
        --licenses-verified --out poc/ddc/inputs/t0-block.json
  Assembles the campaign t0-block (the ddc_runner --t0-block input, staged
  byte-identical to every s1/s2 shard). i3 comes from the pinned
  poc/ddc/t0/i3-token-parity.json; i4 is asserted by the operator AFTER
  re-verifying every benchmark license at source (--licenses-verified);
  per-item emission validity is recomputed from the shard rows.

  NOTE (pin choreography): landing poc/ddc/inputs/t0-block.json (and later
  inputs/ddc0-analysis.json + inputs/a2-directions-ddc0.json for A2)
  CHANGES the staged-bytes sha — re-run poc/ddc/validate_mock.py and
  re-pin pins.harness_manifest in the affected DRAFT record(s) BEFORE the
  coordinator freezes (modal_ddc launch gates 1+3 enforce this).

This module states NO feasibility conclusion.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DDC = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(DDC, "..", ".."))

MANIFEST = os.path.join(DDC, "inputs", "ddc-manifest.json")
I3_PARITY = os.path.join(HERE, "i3-token-parity.json")
FILTER_MARGIN = 0.10   # ASM-1655: donor >= chance + 10 points


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    raise SystemExit(1)


def load_a0(shard_dir, expect_rung):
    items = os.path.join(shard_dir, "items-ddc1.jsonl")
    if not os.path.isfile(items):
        die("ERR_T0B_SHARD", "no items-ddc1.jsonl under %r" % shard_dir)
    rows = [json.loads(l) for l in open(items) if l.strip()]
    a0 = [r for r in rows if r["arm"] == "A0" and r["rung"] == expect_rung
          and r["subset"] == 0]
    if not a0:
        die("ERR_T0B_SHARD", "no A0/%s full-item rows in %r"
            % (expect_rung, shard_dir))
    per_task = {}
    for r in a0:
        per_task.setdefault(r["task"], []).append(float(r["correct"]))
    return {t: {"n_items": len(v), "a0_accuracy": sum(v) / len(v)}
            for t, v in sorted(per_task.items())}


def apply_filter(per_task, chance):
    kept, dropped = [], []
    for t, s in sorted(per_task.items()):
        if t not in chance:
            die("ERR_T0B_CHANCE", "no chance entry for task %r" % t)
        (kept if s["a0_accuracy"] >= chance[t] + FILTER_MARGIN
         else dropped).append(t)
    return kept, dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--a0-shard", required=True,
                    help="collected t0 A0 r135 shard dir")
    ap.add_argument("--a0-shard-r360", default="",
                    help="collected s2 A0 r360 shard dir (S2 phase only)")
    ap.add_argument("--pool-out", default=os.path.join(HERE, "t0-pool.json"))
    ap.add_argument("--pool-only", action="store_true")
    ap.add_argument("--power-result", default="")
    ap.add_argument("--ddc0-analysis", default="",
                    help="saved stdout JSON of analysis/ddc0.py")
    ap.add_argument("--ddc0-verdict-ref",
                    default="registry/verdicts/ddc0.json")
    ap.add_argument("--licenses-verified", action="store_true",
                    help="operator assertion: every primary-suite license "
                         "re-verified at source (gate I-4)")
    ap.add_argument("--i1-debug-iterations", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(DDC, "inputs",
                                                  "t0-block.json"))
    args = ap.parse_args()

    manifest = json.load(open(MANIFEST))
    chance = manifest["eval"]["chance"]

    per_task = load_a0(args.a0_shard, "r135")
    kept, dropped = apply_filter(per_task, chance)
    if not kept:
        die("ERR_T0B_FILTER_EMPTY",
            "informative-task filter is EMPTY — ddc1 kill (c) fires at T0 "
            "(donor too weak for the instrument); report, do not launch")
    pool = {"tasks": [{"task": t, "n_items": per_task[t]["n_items"],
                       "a0_accuracy": per_task[t]["a0_accuracy"]}
                      for t in kept]}
    with open(args.pool_out, "w") as f:
        json.dump(pool, f, indent=1, sort_keys=True)
        f.write("\n")
    print("measured A0 pool (r135): kept=%s dropped=%s -> %s"
          % (kept, dropped, args.pool_out))
    for t in sorted(per_task):
        print("  %-14s n=%5d acc=%.4f chance=%.4f  %s"
              % (t, per_task[t]["n_items"], per_task[t]["a0_accuracy"],
                 chance[t],
                 "KEPT" if t in kept else "filter-dropped"))
    power_out = os.path.join(HERE, "power-sim-result.json")
    print("\ngate I-5 v3 invocation (pinned; NEVER --quick):\n"
          "  nice -n 10 python3 poc/ddc/power_sim_ddc1.py --pool %s \\\n"
          "      --out %s \\\n"
          "      --campaigns 2000 --bootstrap 10000 --seed 20260712"
          % (args.pool_out, power_out))
    if args.pool_only:
        return

    # ---- PHASE 2: full t0-block assembly ----
    if not (args.power_result and os.path.isfile(args.power_result)):
        die("ERR_T0B_ARGS", "--power-result required (run the printed "
            "invocation first, or --pool-only)")
    psr = json.load(open(args.power_result))
    if psr.get("quick_mode"):
        die("ERR_T0B_POWER", "power result is quick_mode — can never gate "
            "(ASM-1720)")
    if psr.get("config", {}).get("q_ref") != 0.25:
        die("ERR_T0B_POWER", "power result q_ref != 0.25")
    if not (args.ddc0_analysis and os.path.isfile(args.ddc0_analysis)):
        die("ERR_T0B_ARGS", "--ddc0-analysis required (the saved pinned-"
            "analysis stdout of the ddc0 run)")
    d0 = json.load(open(args.ddc0_analysis))["analysis"]
    if not args.licenses_verified:
        die("ERR_T0B_ARGS", "--licenses-verified required: re-verify every "
            "benchmark license at source first (gate I-4)")
    if not os.path.isfile(I3_PARITY):
        die("ERR_T0B_I3", "no %s — run poc/ddc/t0/build_corpora.py" %
            I3_PARITY)
    i3 = json.load(open(I3_PARITY))

    emission_tasks = set(per_task)
    per_item_ok = emission_tasks == set(manifest["eval"]["benchmarks"])

    filter_set = {"r135": kept}
    if args.a0_shard_r360:
        pt360 = load_a0(args.a0_shard_r360, "r360")
        kept360, _dropped360 = apply_filter(pt360, chance)
        filter_set["r360"] = kept360

    block = {
        "assembled_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "assembler": "poc/ddc/t0/assemble_t0_block.py (mechanical)",
        "filter_set": filter_set,
        "filter_dropped_r135": dropped,
        "measured_a0_r135": per_task,
        "chance": chance,
        "i1_debug_iterations_used": args.i1_debug_iterations,
        "i3_corpus_parity_valid": bool(i3["i3_corpus_parity_valid"]),
        "i3_parity_ref": "poc/ddc/t0/i3-token-parity.json",
        "i4_licenses_valid": True,
        "i4_note": "operator re-verified every primary-suite license at "
                   "source (--licenses-verified)",
        "per_item_emission_valid": bool(per_item_ok),
        "power_sim_result": psr,
        "ddc0_verdict_ref": args.ddc0_verdict_ref,
        "max_stat_outputs": {
            "winning_method": d0["winning_method"],
            "t_star": d0["max_stat_threshold"],
            "n_layers_admitted": d0["n_layers_admitted"],
            "source": args.ddc0_analysis,
        },
    }
    with open(args.out, "w") as f:
        json.dump(block, f, indent=1, sort_keys=True)
        f.write("\n")
    print("\nt0-block -> %s" % args.out)
    print("i5 gate from embedded result: superiority_min_over_c=%s (c*=%s) "
          "equivalence=%s i5_pass=%s"
          % (psr.get("superiority_power_min_over_c"),
             psr.get("least_favourable_c"),
             psr.get("equivalence_power"),
             psr.get("gate", {}).get("i5_pass")))
    print("REMEMBER: inputs/ changed -> re-run poc/ddc/validate_mock.py and "
          "re-pin pins.harness_manifest in the DRAFT record(s) before "
          "freeze (launch gates 1+3).")


if __name__ == "__main__":
    main()
