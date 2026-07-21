"""Emit the S8 normative resolved-configuration table (mock artifact).

config_index -> complete parameter vector -> truth-engine-derived truth set,
PLUS the consumer/reviewer rotation tables per n-level (R8a).  The full frozen
run must emit + HASH this before any replication (any hand edit invalidates the
run); here it demonstrates the truth engine and grid are wired correctly.
"""
import json
import hashlib
from dataclasses import asdict
import pins
import grid
from hypotheses import truth_set


def rotation_tables():
    out = {}
    for n_nat in (pins.N_NAT, pins.N_NAT_ESC):
        cons = {a: [((i + ai) % pins.N_CONSUMERS) for i in range(n_nat)]
                for ai, a in enumerate(pins.UCT_ARMS)}
        out['consumer_n%d' % n_nat] = cons
    for n_nonce in (pins.N_NONCE, pins.N_NONCE_ESC):
        rev = {a: [((i + ai) % pins.N_REVIEWERS) for i in range(n_nonce)]
               for ai, a in enumerate(pins.REVIEWED_ARMS)}
        out['reviewer_n%d' % n_nonce] = rev
    return out


def _vec_dict(t):
    d = asdict(t)
    # tuple keys -> strings for JSON
    d['fmt'] = {f'{c}|{f}': v for (c, f), v in t.fmt.items()}
    d['kappa_a'] = {k: list(v) for k, v in t.kappa_a.items()}
    return d


def main():
    cells = grid.enumerate_cells()
    records = []
    for (idx, kind, label, rho, regime, n_nat, n_nonce) in cells:
        t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
        records.append({
            'config_index': idx, 'kind': kind, 'label': label,
            'rho': rho, 'regime': regime, 'n_nat': n_nat, 'n_nonce': n_nonce,
            'vector': _vec_dict(t),
            'truth_set': sorted(truth_set(t)),   # COMPUTED, never authored
        })
    artifact = {
        'note': 'MOCK S8 resolved-config table (99a SIM-SPEC). '
                'Truth sets are computed by hypotheses.truth_set (S5), never authored.',
        'base_seed': pins.BASE_SEED,
        'n_cells': len(records),
        'rotation_tables': rotation_tables(),
        'cells': records,
    }
    blob = json.dumps(artifact, sort_keys=True, default=str).encode()
    artifact['sha256'] = hashlib.sha256(blob).hexdigest()
    import os
    os.makedirs('results', exist_ok=True)
    with open('results/99a-r8-simspec-config.json', 'w') as f:
        json.dump(artifact, f, indent=2, default=str)
    print('wrote results/99a-r8-simspec-config.json')
    print('cells:', len(records), 'sha256:', artifact['sha256'][:16], '...')
    # spot-check a couple of truth sets
    for r in records:
        if r['label'] in ('F3', 'F11', 'P3') and r['config_index'] in (27, 58, 87):
            print(f"  idx {r['config_index']} {r['label']}: truth={r['truth_set']}")


if __name__ == '__main__':
    main()
