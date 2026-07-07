#!/usr/bin/env python3
"""
X1-grounding stage 4 (PREREG §4.4): sampled inclusion-minimal grounding sets
(feedback vertex sets) over the Kernel subgraph. Checkpointed per §4.4.

Modes:
  --benchmark N   : time N samples (seeds 0..N-1); project wall-clock.
  --seed-start/--seed-end : run a seed range, append to a checkpoint shard
                    (flushed every 25 samples); resumable (skips done seeds).
  --aggregate     : combine all shards -> minset-summary.json (m(v), I0.9,
                    exact intersection, size distribution, distinct count).
"""
import argparse
import gzip
import json
import os
import time
from collections import Counter

import x1g_lib as L
import fvs

MINSET_DIR = os.path.join(L.HERE, "minsets")


def load_kernel_subgraph(graph_path, strata_path):
    with gzip.open(graph_path, "rt") as f:
        graph = json.loads(f.read())
    with gzip.open(strata_path, "rt") as f:
        strata = json.loads(f.read())
    kernel_ids = strata["kernel"]
    inv, loc, kout, kin = fvs.build_kernel_subgraph(kernel_ids, graph["out"])
    return graph, strata, inv, loc, kout, kin


def benchmark(inv, kout, kin, n):
    times = []
    sizes = []
    for seed in range(n):
        t0 = time.time()
        Fg, Fl = fvs.sample_fvs(inv, kout, kin, seed)
        dt = time.time() - t0
        times.append(dt)
        sizes.append(len(Fg))
        print("  seed %d: %.2fs  |F|=%d" % (seed, dt, len(Fg)))
    avg = sum(times) / len(times)
    print("benchmark: avg %.2fs/sample over %d seeds; |F| min/med/max = %d/%d/%d"
          % (avg, n, min(sizes), sorted(sizes)[len(sizes) // 2], max(sizes)))
    for N in (1000, 300):
        h1 = avg * N / 3600.0
        print("  projected wall-clock N_MS=%d: 1 worker %.2f h | 2 workers %.2f h"
              % (N, h1, h1 / 2))
    return avg


def shard_path(seed_start):
    return os.path.join(MINSET_DIR, "shard-%05d.jsonl" % seed_start)


def run_range(inv, kout, kin, seed_start, seed_end, flush_every=25):
    os.makedirs(MINSET_DIR, exist_ok=True)
    path = shard_path(seed_start)
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)["seed"])
    buf = []
    with open(path, "a") as f:
        for seed in range(seed_start, seed_end):
            if seed in done:
                continue
            t0 = time.time()
            Fg, Fl = fvs.sample_fvs(inv, kout, kin, seed)
            rec = {"seed": seed, "F": Fg, "size": len(Fg),
                   "sec": round(time.time() - t0, 3)}
            buf.append(json.dumps(rec, sort_keys=True, separators=(",", ":")))
            if len(buf) >= flush_every:
                f.write("\n".join(buf) + "\n")
                f.flush()
                os.fsync(f.fileno())
                print("checkpoint: seeds ..%d written (%d in buffer)" % (seed, len(buf)))
                buf = []
        if buf:
            f.write("\n".join(buf) + "\n")
            f.flush()
            os.fsync(f.fileno())
    print("run_range done: seeds [%d,%d)" % (seed_start, seed_end))


def aggregate(strata_path, n_ms):
    with gzip.open(strata_path, "rt") as f:
        strata = json.loads(f.read())
    kernel = set(strata["kernel"])
    records = []
    for fn in sorted(os.listdir(MINSET_DIR)):
        if not fn.startswith("shard-") or not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(MINSET_DIR, fn)) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    records = sorted(records, key=lambda r: r["seed"])[:n_ms]
    counts = Counter()
    distinct = set()
    sizes = []
    for r in records:
        F = r["F"]
        sizes.append(len(F))
        distinct.add(tuple(F))
        for v in F:
            counts[v] += 1
    n = len(records)
    m = {v: counts[v] / n for v in counts}
    i09 = sorted(v for v in kernel if m.get(v, 0.0) >= 0.9)
    exact = sorted(v for v in kernel if m.get(v, 0.0) >= 0.999999)  # m==1
    sizes_sorted = sorted(sizes)
    out = {
        "schema": "x1g-minset-summary/1",
        "inputsSha256": strata.get("inputsSha256", {}),
        "N_MS": n,
        "distinctCount": len(distinct),
        "sizeMin": sizes_sorted[0] if sizes else 0,
        "sizeMedian": sizes_sorted[len(sizes_sorted) // 2] if sizes else 0,
        "sizeMax": sizes_sorted[-1] if sizes else 0,
        "sizeMean": sum(sizes) / n if n else 0,
        "I09": i09,
        "I09Size": len(i09),
        "exactIntersection": exact,
        "exactIntersectionSize": len(exact),
        "m": {str(v): m[v] for v in sorted(m)},
    }
    L.dump_json(out, os.path.join(L.HERE, "minset-summary.json"))
    print("aggregate: N_MS=%d distinct=%d sizes(min/med/max)=%d/%d/%d I0.9=%d exact=%d"
          % (n, len(distinct), out["sizeMin"], out["sizeMedian"], out["sizeMax"],
             len(i09), len(exact)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default=os.path.join(L.HERE, "graph.json.gz"))
    ap.add_argument("--strata", default=os.path.join(L.HERE, "strata.json.gz"))
    ap.add_argument("--benchmark", type=int, default=0)
    ap.add_argument("--seed-start", type=int, default=None)
    ap.add_argument("--seed-end", type=int, default=None)
    ap.add_argument("--aggregate", action="store_true")
    ap.add_argument("--n-ms", type=int, default=1000)
    args = ap.parse_args()

    if args.aggregate:
        aggregate(args.strata, args.n_ms)
        return

    graph, strata, inv, loc, kout, kin = load_kernel_subgraph(args.graph, args.strata)
    print("kernel subgraph: |K|=%d edges=%d" % (
        len(inv), sum(len(s) for s in kout)))
    if args.benchmark:
        benchmark(inv, kout, kin, args.benchmark)
    elif args.seed_start is not None:
        run_range(inv, kout, kin, args.seed_start, args.seed_end)


if __name__ == "__main__":
    main()
