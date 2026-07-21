"""S2 determinism artifact: 100 pinned (config, rep) pairs -> bit-identical
rejection vectors on re-run (independent of execution order / parallelism).

Runs each pinned (config_index, replication_index) pair TWICE (fresh substreams
each time) and asserts the rejected-claim set is identical.  Emits a JSON
artifact with the 100 pairs, their rejection vectors, and a pass flag.
"""
import json
import os
import hashlib
import grid, seeds, pipeline, dgm


def pinned_pairs():
    """100 pinned (config_index, replication_index) pairs spanning cell kinds."""
    cells = grid.enumerate_cells()
    pairs = []
    # spread across the first FWER cells, some power, some gate-cal-ish, varied reps
    reps = [0, 1, 7, 13, 42, 99, 100, 250, 499, 999]
    picks = [0, 3, 9, 15, 27, 43, 58, 70, 75, 87]      # config_index samples
    for ci in picks:
        for rp in reps:
            pairs.append((ci, rp))
    return pairs[:100]


def _cell_for_index(config_index):
    for (idx, kind, label, rho, regime, n_nat, n_nonce) in grid.enumerate_cells():
        if idx == config_index:
            return grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
    raise KeyError(config_index)


def main():
    pairs = pinned_pairs()
    records = []
    n_mismatch = 0
    thr_cache = {}
    for (ci, rp) in pairs:
        t = _cell_for_index(ci)
        if ci not in thr_cache:
            thr_cache[ci] = dgm.compute_gate_thresholds(t, ci)
        thr = thr_cache[ci]
        r1 = sorted(pipeline.run_replication(t, seeds.rep_substreams(ci, rp), gate_thr=thr)['rejected'])
        r2 = sorted(pipeline.run_replication(t, seeds.rep_substreams(ci, rp), gate_thr=thr)['rejected'])
        ident = (r1 == r2)
        if not ident:
            n_mismatch += 1
        records.append({'config_index': ci, 'replication_index': rp,
                        'rejected': r1, 'bit_identical': ident})
    artifact = {'note': 'S2 determinism check — 100 pinned (config, rep) pairs, '
                        'each run twice; rejection vectors must be bit-identical.',
                'n_pairs': len(records), 'n_mismatch': n_mismatch,
                'PASS': n_mismatch == 0, 'pairs': records}
    blob = json.dumps(artifact['pairs'], sort_keys=True).encode()
    artifact['rejection_vectors_sha256'] = hashlib.sha256(blob).hexdigest()
    os.makedirs('results', exist_ok=True)
    with open('results/99a-r8-simspec-determinism.json', 'w') as f:
        json.dump(artifact, f, indent=2)
    print(f"determinism: {len(records)} pairs, mismatches = {n_mismatch}  "
          f"-> {'PASS (all bit-identical)' if n_mismatch == 0 else 'FAIL'}")
    print(f"rejection-vectors sha256: {artifact['rejection_vectors_sha256'][:16]}...")
    print("wrote results/99a-r8-simspec-determinism.json")


if __name__ == '__main__':
    main()
