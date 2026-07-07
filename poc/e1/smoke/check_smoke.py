#!/usr/bin/env python3
"""Mock-smoke assertions (bead kernel-of-truth-bk0). Independent of the
trainer's own in-run checks: reloads checkpoints from disk and verifies

  1. FROZEN arms: concept rows BIT-IDENTICAL between the step-0 and the
     50%/100% checkpoints (torch.equal on the raw tensors);
  2. frozen arms actually trained: NON-concept embedding rows changed and
     final val loss < step-0 val loss;
  3. TRAINABLE arms (trainable, kernel-init): concept rows DID move (the
     mask is not stuck on);
  4. every train summary reports frozenRowsBitIdentical=true for frozen arms;
  5. the mock verdict exists and is labelled mock.
"""

import glob
import json
import os
import sys

import torch

FROZEN = ("kernel-frozen", "shuffled-frozen", "random-frozen")
TRAINABLE = ("trainable", "kernel-init")


def load(path):
    return torch.load(path, map_location="cpu", weights_only=False)


def rows(ck):
    w = ck["model"]["wte.weight"]
    return w[ck["conceptLo"]:ck["conceptHi"]], w


def main():
    ckpts_dir, results_dir, seeds = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    failures = []
    checks = 0

    for arm in FROZEN + TRAINABLE:
        for seed in seeds:
            base = os.path.join(ckpts_dir, f"ckpt-{arm}-seed{seed}")
            ck0 = load(f"{base}-step0.pt")
            r0, w0 = rows(ck0)
            for tag in ("50pct", "100pct"):
                ck = load(f"{base}-{tag}.pt")
                r, w = rows(ck)
                same = torch.equal(r0, r)
                checks += 1
                if arm in FROZEN and not same:
                    failures.append(f"{arm} seed{seed} {tag}: FROZEN concept rows moved")
                if arm in TRAINABLE and same and tag == "100pct":
                    failures.append(f"{arm} seed{seed} {tag}: trainable concept rows did NOT move")
            ck100 = load(f"{base}-100pct.pt")
            _, w100 = rows(ck100)
            nonconcept = slice(ck0["conceptHi"], None)
            if torch.equal(w0[nonconcept], w100[nonconcept]):
                failures.append(f"{arm} seed{seed}: non-concept rows did not train")
            if not ck100["val"]["valLoss"] < ck0["val"]["valLoss"]:
                failures.append(f"{arm} seed{seed}: val loss did not improve "
                                f"({ck0['val']['valLoss']:.4f} -> {ck100['val']['valLoss']:.4f})")

    for p in glob.glob(os.path.join(ckpts_dir, "summary-*.json")):
        s = json.load(open(p))
        if s["arm"] in FROZEN and s.get("frozenRowsBitIdentical") is not True:
            failures.append(f"{os.path.basename(p)}: frozenRowsBitIdentical != true")

    vpath = os.path.join(results_dir, "verdict-e1-mock.json")
    if not os.path.exists(vpath):
        failures.append("verdict-e1-mock.json missing")
    else:
        v = json.load(open(vpath))
        if not v.get("mock"):
            failures.append("verdict not labelled mock")
        if "MOCK" not in v.get("verdict", ""):
            failures.append("verdict string not MOCK-labelled")

    print(f"smoke assertions: {checks} row-identity comparisons over "
          f"{len(FROZEN + TRAINABLE)} arms x {len(seeds)} seeds")
    if failures:
        print("SMOKE FAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("SMOKE PASS: frozen rows bit-identical (step0 vs 50% vs 100%); trainable rows moved; "
          "losses improved; verdict emitted (mock-labelled)")


if __name__ == "__main__":
    main()
