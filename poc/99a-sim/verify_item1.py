"""B3 verification: Stage-1 futility (S4.6) + Rung-0 (S4.8/§7) wiring.

Checks: (a) regression on a non-firing cell (ON == OFF, bit-identical);
(b) a cell where gate-futility fires -> FWER_ON <= FWER_OFF; (c) a cell where
graph-futility fires -> FWER_ON <= FWER_OFF; (d) a cell where Rung-0 terminates
-> confirmatory rejections reduced.  All paired on identical seeds.
"""
import copy
import grid, seeds, pipeline, dgm, pins
from hypotheses import truth_set


def _paired(t, idx, R, gate_thr):
    """Return (fwer_on, fwer_off, fire_rate, cval_on, cval_off, mism)."""
    T = truth_set(t)
    on_e = off_e = fire = cval_on = cval_off = mism = 0
    for r in range(R):
        ss = seeds.rep_substreams(idx, r)
        on = pipeline.run_replication(t, ss, use_futility=True, use_rung0=True, gate_thr=gate_thr)
        ss2 = seeds.rep_substreams(idx, r)
        off = pipeline.run_replication(t, ss2, use_futility=False, use_rung0=False, gate_thr=gate_thr)
        if on['rejected'] != off['rejected']:
            mism += 1
        if on['rejected'] & T:
            on_e += 1
        if off['rejected'] & T:
            off_e += 1
        if on['futility_dropped'] or on['graph_futile'] or on['rung0_terminated']:
            fire += 1
        if 'C-VAL' in on['rejected']:
            cval_on += 1
        if 'C-VAL' in off['rejected']:
            cval_off += 1
    return (on_e / R, off_e / R, fire / R, cval_on / R, cval_off / R, mism)


def main():
    R = 300
    print("== (a) regression: F3 (binding futility fires only harmlessly) ==")
    idx, t = grid.cell_by_label('F3', rho=0.1)
    thr = dgm.compute_gate_thresholds(t, idx)
    fon, foff, fire, con, coff, mism = _paired(t, idx, R, thr)
    print(f"   mismatches ON vs OFF = {mism}/{R}  (fire rate {fire:.3f})  "
          f"FWER on={fon:.4f} off={foff:.4f}  -> {'REGRESSION OK' if mism==0 else 'MISMATCH'}")

    print("== (b) gate-futility FIRES: custom cell pi_a = 0.40 (< pi0), shuffles hi ==")
    idx, t = grid.cell_by_label('F3', rho=0.1)
    for a in t.pi:
        t.pi[a] = 0.40
    thr = dgm.compute_gate_thresholds(t, idx)
    fon, foff, fire, con, coff, mism = _paired(t, idx, R, thr)
    print(f"   futility fire rate = {fire:.3f}  FWER on={fon:.4f} off={foff:.4f}  "
          f"-> {'FWER_ON <= FWER_OFF' if fon <= foff + 1e-12 else 'VIOLATION'}")

    print("== (c) graph-futility FIRES: F9 (Delta^G = 0) ==")
    idx, t = grid.cell_by_label('F9', rho=0.1)
    thr = dgm.compute_gate_thresholds(t, idx)
    # measure graph_futile rate directly + paired FWER
    gf = 0
    for r in range(R):
        res = pipeline.run_replication(t, seeds.rep_substreams(idx, r), gate_thr=thr)
        if res['graph_futile']:
            gf += 1
    fon, foff, fire, con, coff, mism = _paired(t, idx, R, thr)
    print(f"   graph_futile rate = {gf/R:.3f}  FWER on={fon:.4f} off={foff:.4f}  "
          f"-> {'FWER_ON <= FWER_OFF' if fon <= foff + 1e-12 else 'VIOLATION'}")

    print("== (d) Rung-0 TERMINATES: custom cell d0(r) = -0.5 (routes clearly futile) ==")
    idx, t = grid.cell_by_label('F3', rho=0.1)
    for r_ in pins.RUNG0_ROUTES:
        t.rung_d0[r_] = -0.5
    thr = dgm.compute_gate_thresholds(t, idx)
    fon, foff, fire, con, coff, mism = _paired(t, idx, R, thr)
    print(f"   rung0-terminate/fire rate = {fire:.3f}  C-VAL reject on={con:.4f} off={coff:.4f}  "
          f"FWER on={fon:.4f} off={foff:.4f}")
    print(f"   -> Rung-0 zeroes confirmatory rejections when it terminates "
          f"({'reduced' if con < coff else 'no reduction'})")


if __name__ == '__main__':
    main()
