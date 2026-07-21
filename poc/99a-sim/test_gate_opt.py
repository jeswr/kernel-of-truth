"""Numerical-equivalence + timing check for the optimized gate test.

Compares the optimized gate_pvalue (fast closed-form orthant) against a
reference that uses scipy.stats.multivariate_normal.cdf for the orthant, on
>=200 randomized (pi, rho-triple, counts) cases with IDENTICAL bootstrap RNG
state.  Reports max abs diff of the gate p-value.  Then profiles per-rep cost.
"""
import numpy as np
import time
from scipy.stats import multivariate_normal
import pins, seeds, dgm, grid
import gate_test

_REV_OFF = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
_fast_orthant = gate_test.orthant_p11


def _ref_orthant(rho, z):
    if rho <= 0.0:
        from scipy.special import ndtr
        return float(ndtr(-z) ** 2)
    return float(multivariate_normal.cdf([-z, -z], cov=[[1.0, rho], [rho, 1.0]]))


def equivalence(ncases=250):
    rng = np.random.default_rng(12345)
    maxd = 0.0; worst = None; n_diff = 0
    # generate realistic gate datasets across pi and rho by sampling grid cells
    cells = [('GATECAL', 0.1, 96), ('GATECAL', 0.8, 160), ('F5', 0.1, 96),
             ('F4', 0.8, 96), ('P3', 0.5, 96)]
    for i in range(ncases):
        lab, rho, nn = cells[i % len(cells)]
        idx, t = grid.cell_by_label(lab, rho=rho, n='base' if nn == 96 else 'esc')
        t.n_nonce = nn; t.n_nat = pins.N_NAT if nn == 96 else pins.N_NAT_ESC
        ss = seeds.rep_substreams(idx, i)
        _, gate = dgm.gen_composite_and_gate(t, ss)
        gi = i % 4
        a = pins.GATE_ARMS[gi]
        g = gate[gi]
        pi0 = pins.PI0
        # two generators in the SAME state so bootstrap draws are identical
        base = ss[pins.SS_GATE_BOOT]
        st = base.bit_generator.state
        gen1 = np.random.Generator(np.random.Philox()); gen1.bit_generator.state = st
        gen2 = np.random.Generator(np.random.Philox()); gen2.bit_generator.state = st
        gate_test.orthant_p11 = _fast_orthant
        p_new = gate_test.gate_pvalue(g, _REV_OFF[a], pi0, gen1)
        gate_test.orthant_p11 = _ref_orthant       # monkeypatch: invert_orthant uses this
        p_ref = gate_test.gate_pvalue(g, _REV_OFF[a], pi0, gen2)
        gate_test.orthant_p11 = _fast_orthant
        d = abs(p_new - p_ref)
        if d > 0:
            n_diff += 1
        if d > maxd:
            maxd = d; worst = (lab, rho, nn, a, p_new, p_ref)
    print(f"gate p-value equivalence over {ncases} cases:")
    print(f"  max abs diff = {maxd:.3e}   (# cases differing at all: {n_diff}/{ncases})")
    print(f"  worst: {worst}")
    print(f"  bootstrap granularity 1/(B+1) = {1/(pins.B_BOOT+1):.4f} (one-count step)")


def profile_rep():
    import cProfile, pstats, io
    idx, t = grid.cell_by_label('F3', rho=0.1)
    import pipeline
    def run():
        for r in range(5):
            pipeline.run_replication(t, seeds.rep_substreams(idx, r))
    t0 = time.time(); run(); dt = (time.time() - t0) / 5
    print(f"\nper-rep wall time (F3 base, fast orthant): {dt*1000:.1f} ms/rep")
    pr = cProfile.Profile(); pr.enable(); run(); pr.disable()
    s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(12)
    for line in s.getvalue().splitlines():
        if any(k in line for k in ('gate_pvalue', 'invert_orthant', 'orthant_p11',
                                   'standard_normal', 'FamilyAnova', 'run_replication',
                                   '_concordances', 'ndtr', 'contrast')):
            print('  ', line.strip())


if __name__ == '__main__':
    equivalence(250)
    profile_rep()
