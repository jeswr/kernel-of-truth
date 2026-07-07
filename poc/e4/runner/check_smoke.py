#!/usr/bin/env python3
"""Runner mock-smoke assertions (bead kernel-of-truth-hkp). INDEPENDENT of
the fine-tuner's own in-run checks: reloads the E1 source checkpoints and the
E4 fine-tuned checkpoints from disk and verifies

  1. ALL arms: the 1,054 frozen concept rows in the fine-tuned model are
     BIT-IDENTICAL (torch.equal) to the rows RECOMPUTED here from the vector
     tables (same numpy ops), i.e. the freezing mask held through emission
     fine-tuning;
  2. KERNEL arm: the 54 authored concept rows are BIT-IDENTICAL to the E1
     checkpoint's frozen kernel rows — E1 -> E4 continuity through the vocab
     surgery AND the fine-tune;
  3. the model actually trained: the EMIT row moved off its recorded init,
     non-frozen base embedding rows changed, and transformer weights changed;
  4. every fine-tune summary reports frozenRowsBitIdentical=true;
  5. eval files exist for all arms x seeds with full tier-2 coverage, and the
     mock verdict exists and is mock-labelled.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
import torch

ARMS = ("kernel", "shuffled", "random")


def load(path):
    return torch.load(path, map_location="cpu", weights_only=False)


def expected_rows(man, K, base, arm, seed):
    """Same arithmetic as finetune_e4.rows_for_arm (recomputed independently)."""
    scale = float(man["frozenScale"])
    if arm == "kernel":
        return K * scale
    if arm == "shuffled":
        entry = next(e for e in man["shuffled"] if e["seed"] == seed)
        return K[entry["perm"]] * scale
    entry = next(e for e in man["randomFrozen"] if e["seed"] == seed)
    return np.fromfile(os.path.join(base, entry["file"]),
                       dtype="<f4").reshape(man["rows"], man["D"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1-ckpts", required=True)
    ap.add_argument("--e4-ckpts", required=True)
    ap.add_argument("--e4-data", required=True)
    ap.add_argument("--evals", required=True)
    ap.add_argument("--tables", required=True)
    ap.add_argument("--verdict", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--seeds", default="0,1")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    failures = []
    log = []

    def ok(msg):
        log.append(f"OK  {msg}")
        print(f"OK  {msg}")

    with open(args.tables) as f:
        man = json.load(f)
    tbase = os.path.dirname(os.path.abspath(args.tables))
    K = np.fromfile(os.path.join(tbase, man["kernel"]["file"]),
                    dtype="<f4").reshape(man["rows"], man["D"])
    with open(os.path.join(args.e4_data, "e4-vocab.json")) as f:
        vocab = json.load(f)
    tids = [vocab["conceptTokenIds"][s] for s in man["slugs"]]
    tids_t = torch.tensor(tids, dtype=torch.long)
    n_rows = 0

    for arm in ARMS:
        for seed in seeds:
            ck4 = load(os.path.join(args.e4_ckpts, f"ckpt-e4-{arm}-seed{seed}-final.pt"))
            w4 = ck4["model"]["wte.weight"]
            exp = torch.from_numpy(np.ascontiguousarray(expected_rows(man, K, tbase, arm, seed)))
            ck1 = load(os.path.join(args.e1_ckpts, f"ckpt-kernel-frozen-seed{seed}-100pct.pt"))
            w1 = ck1["model"]["wte.weight"]
            lo, hi = ck1["conceptLo"], ck1["conceptHi"]
            if arm == "kernel":
                # authored rows are KEPT from E1 (continuity); table equality of
                # the authored slice was the fine-tuner's own gate — check the
                # E1 continuity here, synthetic slice against the table.
                if not torch.equal(w4[lo:hi], w1[lo:hi]):
                    failures.append(f"{arm} seed{seed}: authored rows NOT bit-identical to E1 "
                                    "checkpoint through vocab surgery + fine-tune")
                synth_mask = [i for i, s in enumerate(man["slugs"]) if s.startswith("e4-")]
                if not torch.equal(w4[tids_t[synth_mask]], exp[synth_mask]):
                    failures.append(f"{arm} seed{seed}: frozen synthetic rows != expected table rows")
                n_rows += (hi - lo) + len(synth_mask)
            else:
                if not torch.equal(w4[tids_t], exp):
                    failures.append(f"{arm} seed{seed}: frozen rows != expected table rows "
                                    "(mask failed or wrong table applied)")
                n_rows += len(tids)
            emit = w4[ck4["emitId"]]
            if torch.equal(emit, ck4["emitRowInit"]):
                failures.append(f"{arm} seed{seed}: EMIT row did NOT move (nothing trained?)")
            V = ck4["baseVocabSize"]
            base_mask = torch.ones(V, dtype=torch.bool)
            base_mask[lo:hi] = False
            if torch.equal(w4[:V][base_mask], w1[base_mask]):
                failures.append(f"{arm} seed{seed}: non-frozen base embedding rows did not train")
            if torch.equal(ck4["model"]["blocks.0.fc.weight"], ck1["model"]["blocks.0.fc.weight"]):
                failures.append(f"{arm} seed{seed}: transformer weights did not train")

    ok(f"{n_rows} frozen-row bit-identity comparisons over {len(ARMS)} arms x {len(seeds)} seeds")

    for p in glob.glob(os.path.join(args.e4_ckpts, "summary-e4-*.json")):
        s = json.load(open(p))
        if s.get("frozenRowsBitIdentical") is not True:
            failures.append(f"{os.path.basename(p)}: frozenRowsBitIdentical != true")

    n_tier2 = None
    for arm in ARMS:
        for seed in seeds:
            path = os.path.join(args.evals, f"eval-e4-{arm}-seed{seed}.json")
            if not os.path.exists(path):
                failures.append(f"missing eval {path}")
                continue
            e = json.load(open(path))
            t2 = e["tiers"]["tier2"]["n"]
            if n_tier2 is None:
                n_tier2 = t2
            if t2 != n_tier2 or t2 == 0:
                failures.append(f"{arm} seed{seed}: tier-2 eval item count {t2} inconsistent")
    ok(f"eval files present for all arms/seeds (tier-2 items per model: {n_tier2})")

    if not os.path.exists(args.verdict):
        failures.append(f"{args.verdict} missing")
    else:
        v = json.load(open(args.verdict))
        if not v.get("mock"):
            failures.append("verdict not labelled mock")
        if "MOCK" not in v.get("verdict", ""):
            failures.append("verdict string not MOCK-labelled")
        ok(f"verdict present + mock-labelled: {v.get('verdict')}")

    if failures:
        print("RUNNER SMOKE FAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    os.makedirs(args.results, exist_ok=True)
    with open(os.path.join(args.results, "runner-smoke-log.txt"), "w") as f:
        f.write("E4 RUNNER smoke (mechanics only: mock E1 checkpoint, mock tables, d=64)\n")
        f.write("\n".join(log) + "\nPASS\n")
    print("RUNNER SMOKE PASS: frozen rows bit-identical through emission fine-tuning "
          "(incl. E1->E4 authored-row continuity in the kernel arm); EMIT + base rows "
          "trained; evals complete; verdict emitted (mock-labelled)")


if __name__ == "__main__":
    main()
