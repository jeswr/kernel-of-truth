#!/usr/bin/env python3
"""S3 grounding-checker prereg — planning power simulation (design-only, $0).

Simulates the COMPLETE licensing rule of the S3 prereg at the pinned geometry:
  - endpoint: paired per-item KOT-HON/1 utility difference, lambda=3
    (per-item paired diff d in {0, +/-1, +/-3, +/-4}; +/-1 abstain<->correct,
     +/-3 wrong<->abstain, +/-4 wrong<->correct)
  - clustering: C concept clusters x m items; cluster random effect on the
    direction bias; inference = one-sample t on cluster means (large-C
    surrogate for the exact cluster sign-flip; C=96 => close agreement)
  - licensing (F1-K convention): two-sided p < 0.05 AND observed mean >= dfloor
  - C-MECH: CONJUNCTION over two contrasts (M_K-T, M_K-G) with cross-contrast
    item-level dependence (Gaussian copula on movability, rho_move)
  - C-KERN: Delta_mask = mean over items of 0.5*(d1+d2), only mask-disagreement
    items (prob rho_item) can move; d1,d2 correlated within item
  - TOST: 90% CI (t on cluster means) inside (-deq, +deq), power at true mu=0
  - HARM: 95% UCB < 0 (type-I checked at mu=0)

All parameters are STIPULATED planning values; GATE-0 re-estimates from pilot.
Seed pinned: 20260724.
"""
import numpy as np

rng_master = np.random.default_rng(20260724)

# ---------- planning parameters (STIPULATED) ----------
C = 96          # concept clusters (hard geometry gate)
M = 20          # items per cluster
N = C * M       # 1920 paired items
F_MOVE = 0.20   # P(item outcome differs between the two arms of a contrast)
MAG_P = {1: 0.55, 3: 0.20, 4: 0.25}   # |d| distribution given movement
E_ABS = sum(k * v for k, v in MAG_P.items())          # 2.15
E_SQ = sum(k * k * v for k, v in MAG_P.items())       # 6.35
TAU = 0.05      # SD of cluster-level true means (C-MECH contrasts)
RHO_MOVE = 0.5  # copula corr of movability across the two C-MECH contrasts
# C-KERN
RHO_ITEM = 0.30   # planning mask-disagreement item fraction (PRECERT floor 0.25)
RHO_D12 = 0.30    # copula corr of movability across the two simple effects
TAU_MASK = 0.03
# margins
DFLOOR_MECH, DEQ_MECH = 0.10, 0.08
DFLOOR_KERN, DEQ_KERN = 0.05, 0.04
REPS = 4000
ALPHA = 0.05


# scipy-free: fixed quantiles for df=95 (C=96 clusters) and the movability threshold
T95_ONE = 1.6611   # t(0.95, df=95)  -- one-sided 0.05 / 90% CI half-width
T95_TWO = 1.9853   # t(0.975, df=95) -- two-sided 0.05
Z_MOVE = -0.8416212335729143   # norm.ppf(0.20); recomputed if F_MOVE changes
import math
def norm_ppf(p):
    # Acklam rational approximation, sufficient for planning use
    a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,6.680131188771972e+01,-1.328068155288572e+01]
    c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,-2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00]
    plow=0.02425
    if p<plow:
        q=math.sqrt(-2*math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p>1-plow:
        q=math.sqrt(-2*math.log(1-p)); return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q=p-0.5; r=q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def q_for_mu(mu, f=F_MOVE, scale=1.0):
    # mu = f*scale*(2q-1)*E_ABS  -> q
    return 0.5 * (mu / (f * scale * E_ABS) + 1.0)

def draw_contrast_pair(rng, mu, C=C, M=M, tau=TAU):
    """Two correlated C-MECH contrasts, both at true mean mu.
    Returns cluster means (C,) for each contrast."""
    q0 = q_for_mu(mu)
    s = tau / (F_MOVE * 2 * E_ABS)          # cluster jitter on q -> tau on mean
    qc = np.clip(q0 + rng.normal(0, s, C), 0.02, 0.98)
    # movability copula across contrasts
    z_shared = rng.normal(size=(C, M))
    z1 = RHO_MOVE**0.5 * z_shared + (1-RHO_MOVE)**0.5 * rng.normal(size=(C, M))
    z2 = RHO_MOVE**0.5 * z_shared + (1-RHO_MOVE)**0.5 * rng.normal(size=(C, M))
    thr = norm_ppf(F_MOVE)
    mags = np.array(list(MAG_P.keys())); probs = np.array(list(MAG_P.values()))
    out = []
    for z in (z1, z2):
        move = z < thr
        mag = rng.choice(mags, size=(C, M), p=probs)
        sign = np.where(rng.random((C, M)) < qc[:, None], 1.0, -1.0)
        d = np.where(move, sign * mag, 0.0)
        out.append(d.mean(axis=1))
    return out[0], out[1]

def draw_mask_contrast(rng, mu_all, C=C, M=M, rho_item=RHO_ITEM, tau=TAU_MASK):
    """Delta_mask cluster means; only disagreement items move; mu_all is the
    ALL-ITEMS true mean (diluted scale)."""
    q0 = q_for_mu(mu_all, f=F_MOVE, scale=rho_item)
    s = tau / (rho_item * F_MOVE * 2 * E_ABS)
    qc = np.clip(q0 + rng.normal(0, s, C), 0.02, 0.98)
    dis = rng.random((C, M)) < rho_item
    thr = norm_ppf(F_MOVE)
    zs = rng.normal(size=(C, M))
    za = RHO_D12**0.5 * zs + (1-RHO_D12)**0.5 * rng.normal(size=(C, M))
    zb = RHO_D12**0.5 * zs + (1-RHO_D12)**0.5 * rng.normal(size=(C, M))
    mags = np.array(list(MAG_P.keys())); probs = np.array(list(MAG_P.values()))
    dd = np.zeros((C, M))
    for z in (za, zb):
        move = (z < thr) & dis
        mag = rng.choice(mags, size=(C, M), p=probs)
        sign = np.where(rng.random((C, M)) < qc[:, None], 1.0, -1.0)
        dd += np.where(move, sign * mag, 0.0)
    return (dd / 2.0).mean(axis=1)

def t_p(cm):
    se = cm.std(ddof=1) / np.sqrt(len(cm))
    t = cm.mean() / se if se > 0 else 0.0
    p = 0.04 if abs(t) > T95_TWO else 0.5   # only the <0.05 THRESHOLD is used
    return cm.mean(), p, se

def license_fire(cm, dfloor):
    mean, p, _ = t_p(cm)
    return (p < ALPHA) and (mean >= dfloor)

def tost_fire(cm, deq):
    mean, _, se = t_p(cm)
    tcrit = T95_ONE
    return (mean + tcrit * se < deq) and (mean - tcrit * se > -deq)

def harm_fire(cm):
    mean, _, se = t_p(cm)
    tcrit = T95_ONE
    return mean + tcrit * se < 0

def run():
    global M, RHO_ITEM
    print(f"geometry C={C} m={M} n={N}; f={F_MOVE} mag={MAG_P} tau={TAU}")
    print(f"analytic sigma_item(C-MECH) = {np.sqrt(F_MOVE*E_SQ):.3f}")
    # --- C-MECH conjunction power curve ---
    for mu in (0.10, 0.11, 0.12, 0.13, 0.14, 0.15):
        rng = np.random.default_rng(rng_master.integers(2**63))
        both = one = 0
        for _ in range(REPS):
            c1, c2 = draw_contrast_pair(rng, mu)
            f1, f2 = license_fire(c1, DFLOOR_MECH), license_fire(c2, DFLOOR_MECH)
            both += f1 and f2
            one += f1
        print(f"C-MECH mu*={mu:.2f}: single-contrast power {one/REPS:.3f}, "
              f"CONJUNCTION power {both/REPS:.3f}")
    # --- C-MECH TOST power at 0 + harm/licensing type-I ---
    rng = np.random.default_rng(rng_master.integers(2**63))
    tost = harm = lic = 0
    for _ in range(REPS):
        c1, _ = draw_contrast_pair(rng, 0.0)
        tost += tost_fire(c1, DEQ_MECH)
        harm += harm_fire(c1)
        lic += license_fire(c1, DFLOOR_MECH)
    print(f"C-MECH at mu=0: TOST(+/-{DEQ_MECH}) power {tost/REPS:.3f}, "
          f"harm type-I {harm/REPS:.3f}, licensing type-I {lic/REPS:.4f}")
    # TOST must NOT fire when true effect = dfloor (region sanity)
    rng = np.random.default_rng(rng_master.integers(2**63))
    tost_at_floor = sum(tost_fire(draw_contrast_pair(rng, DFLOOR_MECH)[0], DEQ_MECH)
                        for _ in range(REPS))
    print(f"C-MECH TOST fires at mu=dfloor({DFLOOR_MECH}): {tost_at_floor/REPS:.4f} (want ~0)")
    # --- geometry sensitivity: m=16 ---
    for m_alt in (16,):
        rng = np.random.default_rng(rng_master.integers(2**63))
        tost = sum(tost_fire(draw_contrast_pair(rng, 0.0, M=m_alt)[0], DEQ_MECH) for _ in range(REPS))
        print(f"[geometry m={m_alt}, n={C*m_alt}] C-MECH TOST power at 0: {tost/REPS:.3f}")
    # --- C-KERN ---
    for mu in (0.05, 0.06, 0.07):
        rng = np.random.default_rng(rng_master.integers(2**63))
        lic = sum(license_fire(draw_mask_contrast(rng, mu), DFLOOR_KERN) for _ in range(REPS))
        print(f"C-KERN mu_mask(all-items)={mu:.2f}: licensing power {lic/REPS:.3f}")
    rng = np.random.default_rng(rng_master.integers(2**63))
    tost = harm = lic0 = 0
    for _ in range(REPS):
        cm = draw_mask_contrast(rng, 0.0)
        tost += tost_fire(cm, DEQ_KERN)
        harm += harm_fire(cm)
        lic0 += license_fire(cm, DFLOOR_KERN)
    print(f"C-KERN at mu=0: TOST(+/-{DEQ_KERN}) power {tost/REPS:.3f}, "
          f"harm type-I {harm/REPS:.3f}, licensing type-I {lic0/REPS:.4f}")
    # C-KERN at PRECERT floor rho_item=0.25
    rng = np.random.default_rng(rng_master.integers(2**63))
    tost = sum(tost_fire(draw_mask_contrast(rng, 0.0, rho_item=0.25), DEQ_KERN) for _ in range(REPS))
    for mu in (0.05, 0.06):
        rng2 = np.random.default_rng(rng_master.integers(2**63))
        lic = sum(license_fire(draw_mask_contrast(rng2, mu, rho_item=0.25), DFLOOR_KERN) for _ in range(REPS))
        print(f"C-KERN [rho_item=0.25] mu={mu:.2f}: licensing power {lic/REPS:.3f}")
    print(f"C-KERN [rho_item=0.25] TOST power at 0: {tost/REPS:.3f}")

if __name__ == "__main__":
    run()
