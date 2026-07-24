#!/usr/bin/env python3
"""S3 grounding-checker prereg — planning power simulation, REV 2 (design-only, $0).

Rev2 repairs the Rev1 artifact per the cross-vendor review (blocking item 1):
  - implements the FROZEN inference procedures, not a t surrogate:
      * licensing test  = Monte-Carlo cluster sign-flip on the EQUAL-CLUSTER
        mean statistic (mean of per-cluster mean paired differences),
        add-one corrected, two-sided;
      * TOST / harm     = cluster percentile bootstrap CI on the same
        statistic (TOST: 90% CI within (-d_eq, +d_eq); harm: one-sided 95%
        UCB < 0);
    (frozen analysis uses B = 10,000 for both; this planning script uses
     B_TEST = 2,000 / B_BOOT = 1,000 as its own MC resolution — disclosed);
  - supports ARBITRARY cluster layouts (unequal m_c): every scenario sums to
    EXACTLY n = 1,920 (the C=54 layout is 24x35 + 30x36 = 1,920, not 54x36);
  - no fixed-df critical values anywhere (sign-flip + bootstrap only);
  - C-KERN has TWO disagreement modes (Rev3 — the Rev2 delta-check's binding
    defect was that only the first existed):
      * MARGINAL planning mode (`dis_frac_c=` per-cluster probabilities):
        disagreement incidence is Bernoulli-redrawn per replication — used
        for the iid/concentrated PLANNING rows only;
      * FROZEN realized mode (`dis_counts=` per-cluster integer counts):
        the disagreement incidence — per-cluster counts AND item locations —
        is built ONCE and held CONSTANT across all replications; only the
        superpopulation outcome draw varies, and the sign-flip/bootstrap
        resample signs/cluster assignment, never the incidence. Item
        locations within a cluster are exchangeable in this generative
        model, so the frozen table's full information content is exactly
        (m_c, k_c); locations are pinned first-k for determinism. This is
        the CONDITIONAL G-P check the prereg registers.
  - REALIZED-ARTIFACT INPUT PATH (Rev3): `--realized <table.json>` runs the
    conditional G-P block on a frozen table:
      {"m_c": [...], "dis_counts": [...],
       "mu_grid_kern": [...], "mu_grid_mech": [...],      # optional grids
       "f_move":, "mag_probs":, "tau_mech":, "tau_mask":}  # optional overrides
    The pre-freeze G-P step feeds the table computed from the sha-pinned
    mask-table artifact; BOTH claim families are re-simulated at the
    realized geometry and the pinned margins, C-KERN in frozen-incidence
    mode.
  - run() (no args) executes EVERY published planning row: C=96 and C=54
    layouts, tau = 0.10 pessimism, rho_item in {0.30, 0.25}, concentrated
    marginal layout, PLUS a FROZEN-INCIDENCE demo (fixed 10-of-20 in 48 of
    96 clusters, realized rho = 0.25 exactly) exercising the same code path
    G-P uses. The demo block is APPENDED at the end of the seed stream, so
    every previously published row is bit-identical to Rev2.

Note on the answer-rate co-floor: it is a deterministic validity gate on
realized data, not a stochastic component of the licensing rule; its
power-relevant channel (abstention transitions) enters through the |d| mix,
which G-P re-estimates from the pilot.

MC shortcut, disclosed: within a scenario cell the sign-flip matrix and the
bootstrap index matrix are drawn once and shared across replications. Power
estimates remain unbiased; only the MC error of the power estimate is mildly
correlated across reps.

All parameters are STIPULATED planning values; G-P re-runs THIS script at the
realized geometry with pilot-estimated parameters (and, for C-KERN, the
realized disagreement table). Master seed pinned: 20260724.
"""
import argparse
import json
import math

import numpy as np

MASTER_SEED = 20260724

# ---------- pinned planning parameters (STIPULATED; G-P re-estimates) ----------
F_MOVE = 0.20                       # P(item outcome differs between paired arms)
MAG_VALS = np.array([1.0, 3.0, 4.0])   # |d|: abstain<->correct, wrong<->abstain, wrong<->correct
MAG_PROBS = np.array([0.55, 0.20, 0.25])
E_ABS = float((MAG_VALS * MAG_PROBS).sum())          # 2.15
TAU_MECH = 0.05                     # SD of cluster-level true means (C-MECH)
TAU_MASK = 0.03                     # idem, Delta_mask
RHO_MOVE = 0.5                      # movability copula corr across the two C-MECH contrasts
RHO_D12 = 0.3                       # idem across the two Delta_mask simple effects
RHO_ITEM = 0.30                     # planning mask-disagreement item fraction (PRECERT floor 0.25)

# ---------- pinned margins (Rev2) ----------
DFLOOR_MECH, DEQ_MECH = 0.09, 0.08
DFLOOR_KERN, DEQ_KERN = 0.05, 0.04

# ---------- pinned layouts (every layout sums to n = 1,920 exactly) ----------
LAYOUT_96 = np.full(96, 20, dtype=int)                                  # 96 x 20
LAYOUT_54 = np.array([35] * 24 + [36] * 30, dtype=int)                  # 24x35 + 30x36
assert LAYOUT_96.sum() == 1920 and LAYOUT_54.sum() == 1920

# ---------- MC resolution (planning; frozen analysis uses B = 10,000) ----------
REPS = 2000
B_TEST = 2000
B_BOOT = 1000
ALPHA = 0.05


def norm_ppf(p):
    """Acklam rational approximation (planning-grade)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - plow:
        return -norm_ppf(1 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


Z_MOVE = norm_ppf(F_MOVE)


def q_for_mu(mu, scale):
    """Direction bias q solving mu = scale * F_MOVE * (2q-1) * E_ABS."""
    return 0.5 * (mu / (scale * F_MOVE * E_ABS) + 1.0)


def _draw_d(rng, reps, m_c, qc, move_z, active):
    """Per-item paired differences for one contrast.
    move_z: (reps, C, mm) latent; active: (reps, C, mm) bool (valid & eligible)."""
    C, mm = len(m_c), int(m_c.max())
    move = (move_z < Z_MOVE) & active
    mag = MAG_VALS[rng.choice(len(MAG_VALS), size=(reps, C, mm), p=MAG_PROBS)]
    sign = np.where(rng.random((reps, C, mm)) < qc[:, :, None], 1.0, -1.0)
    return np.where(move, sign * mag, 0.0)


def _cluster_means(d, m_c):
    return d.sum(axis=2) / m_c[None, :]


def _valid_mask(reps, m_c):
    mm = int(m_c.max())
    return (np.arange(mm)[None, None, :] < m_c[None, :, None]) & np.ones((reps, 1, 1), bool)


def draw_mech_pair(rng, mu, m_c, tau=TAU_MECH, reps=REPS):
    """Cluster-mean matrices (reps, C) for the two C-MECH contrasts (shared
    cluster effect; item-level movability copula RHO_MOVE)."""
    C, mm = len(m_c), int(m_c.max())
    q0 = q_for_mu(mu, 1.0)
    s = tau / (F_MOVE * 2 * E_ABS)
    qc = np.clip(q0 + rng.normal(0, s, (reps, C)), 0.02, 0.98)
    valid = _valid_mask(reps, m_c)
    z_sh = rng.normal(size=(reps, C, mm))
    out = []
    for _ in range(2):
        z = math.sqrt(RHO_MOVE) * z_sh + math.sqrt(1 - RHO_MOVE) * rng.normal(size=(reps, C, mm))
        out.append(_cluster_means(_draw_d(rng, reps, m_c, qc, z, valid), m_c))
    return out[0], out[1]


def _fixed_incidence(m_c, dis_counts):
    """FROZEN disagreement incidence: (C, mm) bool with exactly dis_counts[c]
    True entries among the first m_c[c] valid positions of cluster c.
    Within-cluster item positions are exchangeable in this generative model,
    so (m_c, k_c) is the frozen table's full information content; first-k
    placement keeps the incidence byte-stable across replications and runs."""
    mm = int(m_c.max())
    dis_counts = np.asarray(dis_counts, dtype=int)
    if np.any(dis_counts > m_c) or np.any(dis_counts < 0):
        raise ValueError("dis_counts must satisfy 0 <= k_c <= m_c per cluster")
    return np.arange(mm)[None, :] < dis_counts[:, None]


def draw_mask(rng, mu_all, m_c, dis_frac_c=None, dis_counts=None,
              tau=TAU_MASK, reps=REPS):
    """Cluster-mean matrices (reps, C) for Delta_mask. Two modes:

    dis_counts (FROZEN realized mode — the G-P path, Rev3): per-cluster
      integer disagreement counts from the sha-pinned mask table; the
      incidence (counts AND locations) is FIXED across all replications —
      only the superpopulation outcome draw varies; the sign-flip/bootstrap
      later resample signs/cluster assignment, never the incidence. Effect
      scale = mean_c(k_c/m_c), matching the equal-cluster estimand.
    dis_frac_c (MARGINAL planning mode): per-cluster probabilities;
      incidence Bernoulli-redrawn each replication (planning rows only).
    mu_all is the all-items (equal-cluster) true mean."""
    C, mm = len(m_c), int(m_c.max())
    if dis_counts is not None:
        dis_fixed = _fixed_incidence(m_c, dis_counts)
        rho_bar = float(np.mean(np.asarray(dis_counts, dtype=float) / m_c))
        if rho_bar <= 0:
            raise ValueError("zero realized disagreement: C-KERN unidentifiable (PRECERT)")
        dis = np.broadcast_to(dis_fixed[None, :, :], (reps, C, mm))
    else:
        if dis_frac_c is None:
            dis_frac_c = np.full(C, RHO_ITEM)
        rho_bar = float(np.mean(dis_frac_c))
    q0 = q_for_mu(mu_all, rho_bar)
    s = tau / (rho_bar * F_MOVE * 2 * E_ABS)
    qc = np.clip(q0 + rng.normal(0, s, (reps, C)), 0.02, 0.98)
    valid = _valid_mask(reps, m_c)
    if dis_counts is None:
        dis = (rng.random((reps, C, mm)) < dis_frac_c[None, :, None]) & valid
    z_sh = rng.normal(size=(reps, C, mm))
    dd = np.zeros((reps, C, mm))
    for _ in range(2):
        z = math.sqrt(RHO_D12) * z_sh + math.sqrt(1 - RHO_D12) * rng.normal(size=(reps, C, mm))
        dd += _draw_d(rng, reps, m_c, qc, z, dis)
    return _cluster_means(dd / 2.0, m_c)


# ---------- the FROZEN procedures ----------

def signflip_p(cm, rng, b=B_TEST):
    """MC cluster sign-flip, equal-cluster mean statistic, add-one corrected,
    two-sided. cm: (reps, C). Returns (obs (reps,), p (reps,)).
    Valid under the cluster sign-symmetry assumption stated in the prereg;
    'exact' only conditional on that assumption and up to MC resolution."""
    reps, C = cm.shape
    obs = cm.mean(axis=1)
    flips = rng.choice(np.array([-1.0, 1.0]), size=(b, C))
    null = cm @ flips.T / C                       # (reps, b)
    p = (1.0 + (np.abs(null) >= np.abs(obs)[:, None]).sum(axis=1)) / (b + 1.0)
    return obs, p


def boot_ci(cm, rng, b=B_BOOT, chunk=200):
    """Cluster percentile bootstrap of the equal-cluster mean.
    Returns (lo5, hi95) percentiles, shape (reps,) each."""
    reps, C = cm.shape
    idx = rng.integers(0, C, size=(b, C))
    lo = np.empty(reps)
    hi = np.empty(reps)
    for s in range(0, reps, chunk):
        e = min(s + chunk, reps)
        stats = cm[s:e][:, idx].mean(axis=2)      # (chunk, b, C) -> (chunk, b)
        lo[s:e] = np.percentile(stats, 5.0, axis=1)
        hi[s:e] = np.percentile(stats, 95.0, axis=1)
    return lo, hi


def license_rate(cm, rng, floor):
    obs, p = signflip_p(cm, rng)
    return float(((p < ALPHA) & (obs >= floor)).mean())


def conjunction_rate(cm1, cm2, rng, floor):
    o1, p1 = signflip_p(cm1, rng)
    o2, p2 = signflip_p(cm2, rng)
    return float((((p1 < ALPHA) & (o1 >= floor)) & ((p2 < ALPHA) & (o2 >= floor))).mean())


def tost_rate(cm, rng, deq):
    lo, hi = boot_ci(cm, rng)
    return float(((lo > -deq) & (hi < deq)).mean())


def harm_rate(cm, rng):
    _, hi = boot_ci(cm, rng)
    return float((hi < 0.0).mean())


# ---------- scenario runner (every published table row) ----------

def run():
    rm = np.random.default_rng(MASTER_SEED)

    def r():
        return np.random.default_rng(rm.integers(2**63))

    print("Rev2 planning sim: n=1920 exact in every layout; frozen sign-flip "
          f"(B_TEST={B_TEST}) + cluster bootstrap (B_BOOT={B_BOOT}); REPS={REPS}")
    print(f"layouts: 96x20 and 24x35+30x36; f={F_MOVE}, |d| mix 1/3/4 = "
          f"{list(MAG_PROBS)}, tau_mech={TAU_MECH}, tau_mask={TAU_MASK}")
    print(f"margins: C-MECH floor {DFLOOR_MECH}/eq {DEQ_MECH}; "
          f"C-KERN floor {DFLOOR_KERN}/eq {DEQ_KERN}")

    for name, m_c in (("96x20", LAYOUT_96), ("54(24x35+30x36)", LAYOUT_54)):
        for mu in (DFLOOR_MECH, 0.11, 0.115, 0.12, 0.13):
            g = r()
            c1, c2 = draw_mech_pair(g, mu, m_c)
            print(f"C-MECH [{name}] mu={mu:.3f}: single {license_rate(c1, g, DFLOOR_MECH):.3f}, "
                  f"CONJUNCTION {conjunction_rate(c1, c2, g, DFLOOR_MECH):.3f}")
        g = r()
        c1, _ = draw_mech_pair(g, 0.0, m_c)
        print(f"C-MECH [{name}] at mu=0: TOST(+/-{DEQ_MECH}) {tost_rate(c1, g, DEQ_MECH):.3f}, "
              f"harm type-I {harm_rate(c1, g):.3f}, "
              f"licensing type-I {license_rate(c1, g, DFLOOR_MECH):.4f}")
        g = r()
        c1, _ = draw_mech_pair(g, DFLOOR_MECH, m_c)
        print(f"C-MECH [{name}] TOST fires at mu=floor: {tost_rate(c1, g, DEQ_MECH):.4f} (want ~0)")

    # tau = 0.10 pessimism (96x20)
    g = r()
    c1, _ = draw_mech_pair(g, 0.0, LAYOUT_96, tau=0.10)
    print(f"C-MECH [96x20, tau=0.10] TOST at 0: {tost_rate(c1, g, DEQ_MECH):.3f}")
    for mu in (0.12, 0.13):
        g = r()
        c1, c2 = draw_mech_pair(g, mu, LAYOUT_96, tau=0.10)
        print(f"C-MECH [96x20, tau=0.10] mu={mu:.2f}: CONJUNCTION "
              f"{conjunction_rate(c1, c2, g, DFLOOR_MECH):.3f}")

    # C-KERN: iid disagreement at rho 0.30 and 0.25 (96x20)
    for rho in (0.30, 0.25):
        dis = np.full(96, rho)
        for mu in (DFLOOR_KERN, 0.055, 0.06):
            g = r()
            cm = draw_mask(g, mu, LAYOUT_96, dis_frac_c=dis)
            print(f"C-KERN [96x20, iid rho={rho}] mu_all={mu:.3f}: "
                  f"licensing {license_rate(cm, g, DFLOOR_KERN):.3f}")
        g = r()
        cm = draw_mask(g, 0.0, LAYOUT_96, dis_frac_c=dis)
        print(f"C-KERN [96x20, iid rho={rho}] at 0: TOST(+/-{DEQ_KERN}) "
              f"{tost_rate(cm, g, DEQ_KERN):.3f}, harm type-I {harm_rate(cm, g):.3f}")

    # C-KERN: CONCENTRATED layout stress — same item-level rho = 0.25, but all
    # disagreements confined to HALF the clusters (per-cluster rate 0.50 vs 0).
    dis_conc = np.array([0.50] * 48 + [0.0] * 48)
    for mu in (0.055, 0.06):
        g = r()
        cm = draw_mask(g, mu, LAYOUT_96, dis_frac_c=dis_conc)
        print(f"C-KERN [96x20, CONCENTRATED 48@0.50] mu_all={mu:.3f}: "
              f"licensing {license_rate(cm, g, DFLOOR_KERN):.3f}")
    g = r()
    cm = draw_mask(g, 0.0, LAYOUT_96, dis_frac_c=dis_conc)
    print(f"C-KERN [96x20, CONCENTRATED] at 0: TOST {tost_rate(cm, g, DEQ_KERN):.3f}")

    # C-KERN on the 54-cluster layout (iid rho=0.30)
    g = r()
    cm = draw_mask(g, 0.06, LAYOUT_54, dis_frac_c=np.full(54, 0.30))
    print(f"C-KERN [54-layout, iid rho=0.30] mu_all=0.060: "
          f"licensing {license_rate(cm, g, DFLOOR_KERN):.3f}")
    g = r()
    cm = draw_mask(g, 0.0, LAYOUT_54, dis_frac_c=np.full(54, 0.30))
    print(f"C-KERN [54-layout, iid rho=0.30] at 0: TOST {tost_rate(cm, g, DEQ_KERN):.3f}")

    # Rev3 — FROZEN-INCIDENCE demo (the G-P code path): fixed 10-of-20 in 48
    # of 96 clusters, 0 elsewhere; realized rho = 480/1920 = 0.25 exactly;
    # incidence constant across replications. APPENDED after all Rev2 rows so
    # the published Rev2 numbers are bit-identical.
    counts_demo = np.array([10] * 48 + [0] * 48)
    for mu in (0.055, 0.06):
        g = r()
        cm = draw_mask(g, mu, LAYOUT_96, dis_counts=counts_demo)
        print(f"C-KERN [96x20, FROZEN 10-of-20 in 48 clusters] mu_all={mu:.3f}: "
              f"licensing {license_rate(cm, g, DFLOOR_KERN):.3f}")
    g = r()
    cm = draw_mask(g, 0.0, LAYOUT_96, dis_counts=counts_demo)
    print(f"C-KERN [96x20, FROZEN 10-of-20 in 48 clusters] at 0: "
          f"TOST {tost_rate(cm, g, DEQ_KERN):.3f}, harm type-I {harm_rate(cm, g):.3f}")


def run_realized(path):
    """The conditional G-P block (Rev3): re-simulate BOTH claim families at
    the FROZEN realized geometry. `path` is the realized-artifact JSON the
    pre-freeze G-P step derives from the sha-pinned mask table:
      m_c            per-cluster certified item counts (required)
      dis_counts     per-cluster mask-disagreement counts (required)
      mu_grid_kern   C-KERN true-effect grid (default [DFLOOR_KERN, .055, .06])
      mu_grid_mech   C-MECH grid (default [DFLOOR_MECH, .11, .12, .13])
      f_move, mag_probs, tau_mech, tau_mask   pilot-estimated overrides
    Incidence is FIXED (counts + first-k locations) across replications; the
    gate rule (prereg §8/§10 G-P) is power >= 0.75 for every primary
    licensing rule and every TOST."""
    global F_MOVE, MAG_PROBS, TAU_MECH, TAU_MASK, Z_MOVE
    with open(path, "r", encoding="utf-8") as fh:
        t = json.load(fh)
    m_c = np.asarray(t["m_c"], dtype=int)
    dis_counts = np.asarray(t["dis_counts"], dtype=int)
    if len(dis_counts) != len(m_c):
        raise ValueError("m_c and dis_counts must have equal length C")
    F_MOVE = float(t.get("f_move", F_MOVE))
    MAG_PROBS = np.asarray(t.get("mag_probs", MAG_PROBS), dtype=float)
    TAU_MECH = float(t.get("tau_mech", TAU_MECH))
    TAU_MASK = float(t.get("tau_mask", TAU_MASK))
    Z_MOVE = norm_ppf(F_MOVE)
    rho_real = float(np.mean(dis_counts / m_c))
    rm = np.random.default_rng(MASTER_SEED)

    def r():
        return np.random.default_rng(rm.integers(2**63))

    print(f"G-P CONDITIONAL RE-SIM on frozen realized table {path}")
    print(f"C={len(m_c)}, n={int(m_c.sum())}, disagreement items={int(dis_counts.sum())}, "
          f"equal-cluster rho_real={rho_real:.4f}; f={F_MOVE}, "
          f"mag_probs={list(MAG_PROBS)}, tau_mech={TAU_MECH}, tau_mask={TAU_MASK}")
    for mu in t.get("mu_grid_mech", [DFLOOR_MECH, 0.11, 0.12, 0.13]):
        g = r()
        c1, c2 = draw_mech_pair(g, float(mu), m_c)
        print(f"  C-MECH mu={float(mu):.3f}: CONJUNCTION "
              f"{conjunction_rate(c1, c2, g, DFLOOR_MECH):.3f}")
    g = r()
    c1, _ = draw_mech_pair(g, 0.0, m_c)
    print(f"  C-MECH TOST(+/-{DEQ_MECH}) at 0: {tost_rate(c1, g, DEQ_MECH):.3f}")
    for mu in t.get("mu_grid_kern", [DFLOOR_KERN, 0.055, 0.06]):
        g = r()
        cm = draw_mask(g, float(mu), m_c, dis_counts=dis_counts)
        print(f"  C-KERN [FROZEN incidence] mu_all={float(mu):.3f}: "
              f"licensing {license_rate(cm, g, DFLOOR_KERN):.3f}")
    g = r()
    cm = draw_mask(g, 0.0, m_c, dis_counts=dis_counts)
    print(f"  C-KERN [FROZEN incidence] TOST(+/-{DEQ_KERN}) at 0: "
          f"{tost_rate(cm, g, DEQ_KERN):.3f}, harm type-I {harm_rate(cm, g):.3f}")
    print("  gate rule: every primary licensing power and every TOST >= 0.75 (prereg G-P)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="S3 prereg planning power sim (Rev3)")
    ap.add_argument("--realized", metavar="TABLE_JSON", default=None,
                    help="run the conditional G-P block on a frozen realized "
                         "item-x-cluster disagreement table")
    args = ap.parse_args()
    if args.realized:
        run_realized(args.realized)
    else:
        run()
