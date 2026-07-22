"""S4.2/R10a — EXACT REML of the registered composite-family (family B) 6-component
model, the Rev10 B2 fix.  Replaces the pooled-ANOVA closed form (retired to a
starting value) as the family-(B) engine ESTIMATOR.

Registered model (§4.6/(1b)(B)), per composite replication on the fully-crossed
single-replicate (arm x concept x seed) grid Y[a,i,s]:

    Y = mu_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} + w_{r(a,i)}*1[a reviewed] + eps

with phi = (s2_b, s2_ab, s2_v, s2_av, s2_w, s2_eps) >= 0, a SINGLE residual
s2_eps, and the reviewer block w present on REVIEWED arm-records only (a
structurally-partial random-effect block; reviewer index r(a,i) = (rev_off(a)+i)
mod n_reviewers).  This partial block is why balanced ANOVA-MS matching != REML on
the composite family (SPEC-DEFECTS B2 / R10a); the pooled form spread s2_w across
the pooled mean squares.

Outputs, per R10a:
  theta_hat = GLS arm-mean difference (= OLS on this design; verified);
  Var(theta_hat; phi) = (2/I) s2_ab + (2/S) s2_av + kappa*s2_w/n_rev + (2/(I*S)) s2_eps
      with kappa = 1 iff EXACTLY ONE of the two contrasted arms is reviewed, else 0;
  nu (Satterthwaite / Giesbrecht-Burns): nu = Var^2 / (g^T Cov(phi_hat) g)/... with
      the CONSTANT gradient g = (0, 2/I, 0, 2/S, kappa/n_rev, 2/(I*S)) and
      Cov(phi_hat) from the REML information (observed information = the Hessian of
      the REML deviance, matching the lmerTest oracle's Satterthwaite computation).

Fast structured evaluation (grid-feasible): seed splits into seed-mean (dim A*I)
and (S-1) seed-contrast copies; each block's covariance is Kronecker in the
(arm, concept) contrast basis EXCEPT the seed-mean block carries the rank-n_rev
reviewer update W = G G^T, handled by Woodbury.  A dense reference (build the
A*I blocks explicitly) cross-checks the structured path (see __main__).
"""
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import cho_factor, cho_solve

import pins
from inference import ContrastFit


class CompositeREML:
    """Per-cell precomputed exact-REML fitter for a family whose registered model
    is the balanced (arm x concept x seed) crossed model PLUS one extra crossed
    random-effect block (the reviewer block for family B, the consumer block for
    family A) carried on a subset (or all) of the arms via a published rotation.

    phi = (s2_b, s2_ab, s2_v, s2_av, s2_block, s2_eps).  The contrast-variance map
    charges the block term (kappa*s2_block/n_block) ONLY when EXACTLY ONE of the
    two contrasted arms is covered by the block (partial block, e.g. reviewer):
    for a FULL block (e.g. consumer, all arms covered) no contrast is ever
    exactly-one-covered so kappa == 0 (the block cancels in every arm contrast).
    """

    def __init__(self, A, I, S, level_of, covered_arms, n_block):
        """level_of(a, i) -> block level in {0..n_block-1} for covered arm a, else
        ignored; covered_arms = set of arm indices the block touches."""
        self.A, self.I, self.S = A, I, S
        self.N = A * I * S
        self.p = A                    # arm fixed effects
        self.n_rev = n_block          # kept name for the Woodbury rank
        self.reviewed_idx = set(covered_arms)   # 'covered by the extra block'
        G = np.zeros((A * I, n_block))
        for a in range(A):
            if a in self.reviewed_idx:
                for i in range(I):
                    G[a * I + i, level_of(a, i)] = 1.0
        self.G = G                                   # (A*I, n_block)
        self.Gmat = G.reshape(A, I, n_block)         # (A, I, n_block)
        self._dense_ready = False

    # ---------- fast structured linear algebra -----------------------------
    def _dmean_inv_apply(self, v, phi):
        """Apply D_mean(phi)^{-1} to v (shape (A,I)); D_mean = Kronecker part of
        the seed-mean covariance (no reviewer block)."""
        A, I, S = self.A, self.I, self.S
        s2b, s2ab, s2v, s2av, s2e = phi[0], phi[1], phi[2], phi[3], phi[5]
        lam_mm = s2e + S * s2b * A + s2v * A * I + S * s2ab + s2av * I
        lam_mc = s2e + S * s2b * A + S * s2ab
        lam_cm = s2e + S * s2ab + s2av * I
        lam_cc = s2e + S * s2ab
        g = v.mean()
        cmean = v.mean(axis=0, keepdims=True)          # (1,I) mean over arms
        rmean = v.mean(axis=1, keepdims=True)          # (A,1) mean over concepts
        out = ((1.0 / lam_mm) * g
               + (1.0 / lam_mc) * (cmean - g)
               + (1.0 / lam_cm) * (rmean - g)
               + (1.0 / lam_cc) * (v - cmean - rmean + g))
        return out, (lam_mm, lam_mc, lam_cm, lam_cc)

    def _dmean_logdet(self, phi):
        A, I, S = self.A, self.I, self.S
        s2b, s2ab, s2v, s2av, s2e = phi[0], phi[1], phi[2], phi[3], phi[5]
        lam_mm = s2e + S * s2b * A + s2v * A * I + S * s2ab + s2av * I
        lam_mc = s2e + S * s2b * A + S * s2ab
        lam_cm = s2e + S * s2ab + s2av * I
        lam_cc = s2e + S * s2ab
        return (np.log(lam_mm) + (I - 1) * np.log(lam_mc)
                + (A - 1) * np.log(lam_cm) + (A - 1) * (I - 1) * np.log(lam_cc))

    def _vmean_pieces(self, phi):
        """Return callables/data to apply V_mean^{-1} (Woodbury) + logdet."""
        A, I, S = self.A, self.I, self.S
        s2w = phi[4]
        c = S * s2w
        # G_reshaped columns -> D^{-1} G
        DinvG = np.empty((A, I, self.n_rev))
        for r in range(self.n_rev):
            DinvG[:, :, r], _ = self._dmean_inv_apply(self.Gmat[:, :, r], phi)
        # 8x8 Gram: G^T D^{-1} G
        Gt = self.Gmat.reshape(A * I, self.n_rev)
        DinvG_flat = DinvG.reshape(A * I, self.n_rev)
        M8 = Gt.T @ DinvG_flat                              # (n_rev, n_rev) = G^T D^{-1} G
        cap = np.eye(self.n_rev) + c * M8                   # I + c G^T D^{-1} G
        cap_cf = cho_factor(cap)
        logdet_vmean = self._dmean_logdet(phi) + 2.0 * np.sum(
            np.log(np.diag(np.linalg.cholesky(cap))))
        return DinvG_flat, cap_cf, c, logdet_vmean

    def _vmean_inv_apply(self, v, phi, pieces):
        """Apply V_mean^{-1} to v (A,I) via Woodbury."""
        DinvG_flat, cap_cf, c, _ = pieces
        Dinv_v, _ = self._dmean_inv_apply(v, phi)
        Gt_Dinv_v = self.G.T @ v.reshape(-1)               # G^T v  (n_rev,)
        # Woodbury middle: cap^{-1} (G^T D^{-1} v).  Note G^T D^{-1} v = (D^{-1}G)^T v
        rhs = DinvG_flat.T @ v.reshape(-1)                 # (D^{-1}G)^T v = G^T D^{-1} v
        z = cho_solve(cap_cf, rhs)                         # cap^{-1} rhs
        corr = c * (DinvG_flat @ z).reshape(self.A, self.I)
        return Dinv_v - corr

    def _vcontrast_inv_apply(self, v, phi):
        A, I = self.A, self.I
        s2v, s2av, s2e = phi[2], phi[3], phi[5]
        lam_mm = s2e + s2v * A * I + s2av * I
        lam_cm = s2e + s2av * I
        lam_cc = s2e
        g = v.mean()
        rmean = v.mean(axis=1, keepdims=True)              # mean over concepts (A,1)
        # concept-mean subspace: grand (arm-mean) + arm-contrast; concept-contrast: lam_cc
        out = ((1.0 / lam_mm) * g
               + (1.0 / lam_cm) * (rmean - g)
               + (1.0 / lam_cc) * (v - rmean))
        return out

    def _vcontrast_logdet(self, phi):
        A, I = self.A, self.I
        s2v, s2av, s2e = phi[2], phi[3], phi[5]
        lam_mm = s2e + s2v * A * I + s2av * I
        lam_cm = s2e + s2av * I
        lam_cc = s2e
        return (np.log(lam_mm) + (A - 1) * np.log(lam_cm)
                + A * (I - 1) * np.log(lam_cc))

    # ---------- batched fast linear algebra (numerics identical) -----------
    def _dmean_inv_batch(self, V, phi):
        """Apply D_mean(phi)^{-1} to V of shape (A, I, K) column-wise."""
        A, I, S = self.A, self.I, self.S
        s2b, s2ab, s2v, s2av, s2e = phi[0], phi[1], phi[2], phi[3], phi[5]
        lam_mm = s2e + S * s2b * A + s2v * A * I + S * s2ab + s2av * I
        lam_mc = s2e + S * s2b * A + S * s2ab
        lam_cm = s2e + S * s2ab + s2av * I
        lam_cc = s2e + S * s2ab
        g = V.mean(axis=(0, 1), keepdims=True)
        cmean = V.mean(axis=0, keepdims=True)
        rmean = V.mean(axis=1, keepdims=True)
        return ((1.0 / lam_mm) * g + (1.0 / lam_mc) * (cmean - g)
                + (1.0 / lam_cm) * (rmean - g)
                + (1.0 / lam_cc) * (V - cmean - rmean + g))

    def _vmean_prep(self, phi):
        """Woodbury prep: cap Cholesky, logdet(V_mean), DinvG (A,I,n_rev)."""
        A, I, S = self.A, self.I, self.S
        c = S * phi[4]
        DinvG = self._dmean_inv_batch(self.Gmat, phi)             # (A,I,n_rev)
        DinvG_flat = DinvG.reshape(A * I, self.n_rev)
        M8 = self.G.T @ DinvG_flat
        cap = np.eye(self.n_rev) + c * M8
        cap_cf = cho_factor(cap)
        logdet_cap = 2.0 * np.sum(np.log(np.diag(np.linalg.cholesky(cap))))
        logdet_vmean = self._dmean_logdet(phi) + logdet_cap
        return dict(DinvG=DinvG_flat, cap_cf=cap_cf, c=c, logdet=logdet_vmean)

    def _vmean_inv_batch(self, V, phi, pre):
        """Apply V_mean^{-1} (Woodbury) to V of shape (A,I,K)."""
        A, I = self.A, self.I
        K = V.shape[2]
        Dinv_V = self._dmean_inv_batch(V, phi)
        Vf = V.reshape(A * I, K)
        rhs = pre["DinvG"].T @ Vf                                 # (n_rev, K) = G^T D^{-1} V
        z = cho_solve(pre["cap_cf"], rhs)                         # (n_rev, K)
        corr = pre["c"] * (pre["DinvG"] @ z)                      # (A*I, K)
        return Dinv_V - corr.reshape(A, I, K)

    def _vcontrast_inv_batch(self, V, phi):
        A, I = self.A, self.I
        s2v, s2av, s2e = phi[2], phi[3], phi[5]
        lam_mm = s2e + s2v * A * I + s2av * I
        lam_cm = s2e + s2av * I
        lam_cc = s2e
        g = V.mean(axis=(0, 1), keepdims=True)
        rmean = V.mean(axis=1, keepdims=True)
        return ((1.0 / lam_mm) * g + (1.0 / lam_cm) * (rmean - g)
                + (1.0 / lam_cc) * (V - rmean))

    def deviance_fast(self, phi, data):
        """Batched -2 REML log-lik (numerically identical to deviance())."""
        A, I, S = self.A, self.I, self.S
        Ybar, Yc = data
        Ym = np.sqrt(S) * Ybar                                   # (A,I)
        pre = self._vmean_prep(phi)
        # stack [Ym | 8 arm-indicator fields] -> apply V_mean^{-1} once
        cols = np.zeros((A, I, 1 + A))
        cols[:, :, 0] = Ym
        for a in range(A):
            cols[a, :, 1 + a] = np.sqrt(S)
        Vinv_cols = self._vmean_inv_batch(cols, phi, pre)        # (A,I,1+A)
        Vinv_Ym = Vinv_cols[:, :, 0]
        # X^T Vinv X (A,A): col j = sqrt(S)*sum_concepts Vinv(indicator_j)[arm,:]
        Xind = np.sqrt(S) * Vinv_cols[:, :, 1:].sum(axis=1)      # (A, A): rows=arm, cols=indicator
        XtVinvX = 0.5 * (Xind + Xind.T)
        XtVinvYm = np.sqrt(S) * Vinv_Ym.sum(axis=1)              # (A,)
        cf = cho_factor(XtVinvX)
        beta = cho_solve(cf, XtVinvYm)
        logdet_XtVinvX = 2.0 * np.sum(np.log(np.diag(np.linalg.cholesky(XtVinvX))))
        Xbeta = np.sqrt(S) * beta[:, None] * np.ones((1, I))
        r_m = Ym - Xbeta
        Vinv_rm = self._vmean_inv_batch(r_m[:, :, None], phi, pre)[:, :, 0]
        q_mean = float((r_m * Vinv_rm).sum())
        Vc_inv_Yc = self._vcontrast_inv_batch(Yc, phi)           # (A,I,S)
        q_contrast = float((Yc * Vc_inv_Yc).sum())
        logdetV = pre["logdet"] + (S - 1) * self._vcontrast_logdet(phi)
        return logdetV + logdet_XtVinvX + q_mean + q_contrast, beta, XtVinvX

    # ---------- REML deviance (unprofiled, all 6 variances) -----------------
    def deviance(self, phi, data):
        """-2 * REML log-likelihood (up to an additive constant) at phi.
        data = (Ybar (A,I), Yc (A,I,S centered over seed))."""
        A, I, S = self.A, self.I, self.S
        Ybar, Yc = data
        Ym = np.sqrt(S) * Ybar                             # seed-mean data (A,I)
        pieces = self._vmean_pieces(phi)
        logdet_vmean = pieces[3]
        # X_m columns: arm indicators * sqrt(S).  X_m^T Vinv X_m (A x A), X_m^T Vinv Ym
        # Vinv applied to each arm-indicator e_a (x sqrt(S)); vectorize by applying
        # Vinv to Ym and to the A indicator fields.
        # Build Vinv @ Ym:
        Vinv_Ym = self._vmean_inv_apply(Ym, phi, pieces)
        # X_m^T Vinv Ym : for arm a = sqrt(S)*sum over concepts of Vinv_Ym[a,:]
        XtVinvYm = np.sqrt(S) * Vinv_Ym.sum(axis=1)        # (A,)
        # X_m^T Vinv X_m : need Vinv applied to each arm-indicator field
        XtVinvX = np.empty((A, A))
        for a in range(A):
            ind = np.zeros((A, I)); ind[a, :] = np.sqrt(S)
            Vinv_ind = self._vmean_inv_apply(ind, phi, pieces)
            XtVinvX[a, :] = np.sqrt(S) * Vinv_ind.sum(axis=1)
        XtVinvX = 0.5 * (XtVinvX + XtVinvX.T)
        cf = cho_factor(XtVinvX)
        beta = cho_solve(cf, XtVinvYm)                     # GLS arm means
        logdet_XtVinvX = 2.0 * np.sum(np.log(np.diag(np.linalg.cholesky(XtVinvX))))
        # residual r_m = Ym - X_m beta ; X_m beta[a,i] = sqrt(S)*beta[a]
        Xbeta = np.sqrt(S) * beta[:, None] * np.ones((1, I))
        r_m = Ym - Xbeta
        Vinv_rm = self._vmean_inv_apply(r_m, phi, pieces)
        q_mean = float((r_m * Vinv_rm).sum())
        # seed-contrast quadratic: sum_s vec(Yc_s)^T Vc^{-1} vec(Yc_s)
        logdet_vc = self._vcontrast_logdet(phi)
        q_contrast = 0.0
        for s in range(S):
            vc = Yc[:, :, s]
            q_contrast += float((vc * self._vcontrast_inv_apply(vc, phi)).sum())
        logdetV = logdet_vmean + (S - 1) * logdet_vc
        N, p = self.N, self.p
        dev = logdetV + logdet_XtVinvX + q_mean + q_contrast
        return dev, beta, XtVinvX

    # ---------- fit + contrast ---------------------------------------------
    def _prep(self, Ycomp):
        Ybar = Ycomp.mean(axis=2)                          # (A,I)
        Yc = Ycomp - Ybar[:, :, None]                      # centered over seed
        return Ybar, Yc

    def _moment_start(self, Ycomp):
        """Pooled-ANOVA-ish moment start (clipped >= 0), R10a start-1."""
        A, I, S = self.A, self.I, self.S
        Y = Ycomp
        M = Y.mean()
        Ma = Y.mean(axis=(1, 2)); Mi = Y.mean(axis=(0, 2)); Ms = Y.mean(axis=(0, 1))
        Mai = Y.mean(axis=2); Mas = Y.mean(axis=1)
        SS_i = A * S * np.sum((Mi - M) ** 2)
        SS_ab = S * np.sum((Mai - Ma[:, None] - Mi[None, :] + M) ** 2)
        SS_s = A * I * np.sum((Ms - M) ** 2)
        SS_av = I * np.sum((Mas - Ma[:, None] - Ms[None, :] + M) ** 2)
        SS_tot = np.sum((Y - M) ** 2)
        SS_arm = I * S * np.sum((Ma - M) ** 2)
        SS_e = SS_tot - SS_arm - SS_i - SS_ab - SS_s - SS_av
        df_i = I - 1; df_ab = (A - 1) * (I - 1); df_s = S - 1
        df_av = (A - 1) * (S - 1)
        df_e = A * I * S - A - df_i - df_ab - df_s - df_av
        MSi = SS_i / df_i; MSab = SS_ab / df_ab; MSs = SS_s / max(df_s, 1)
        MSav = SS_av / max(df_av, 1); MSe = SS_e / max(df_e, 1)
        s2e = max(MSe, 1e-6)
        s2ab = max((MSab - MSe) / S, 0.0)
        s2b = max((MSi - MSab) / (A * S), 0.0)
        s2av = max((MSav - MSe) / I, 0.0)
        s2v = max((MSs - MSav) / (A * I), 0.0)
        s2w = max(0.5 * s2e, 1e-4)                         # generic reviewer start
        return np.array([s2b, s2ab, s2v, s2av, s2w, s2e])

    def fit(self, Ycomp, tol_dev=1e-12, tol_par=1e-9):
        data = self._prep(Ycomp)
        x0 = self._moment_start(Ycomp)
        scale = max(x0[5], 1e-3)
        floor = 1e-12 * scale

        def obj(x):
            phi = np.maximum(x, floor)
            dev, _, _ = self.deviance_fast(phi, data)
            return dev

        # R10a: profiled REML over nonneg variances; start-1 moments, tight tol.
        res = minimize(obj, x0, method="L-BFGS-B",
                       bounds=[(0.0, None)] * 6,
                       options={"ftol": 1e-15, "gtol": 1e-10, "maxiter": 500})
        phi = np.maximum(res.x, floor)
        # second start (equal split) if not converged well
        if not res.success:
            tot = float(np.var(Ycomp))
            x1 = np.array([tot / 6] * 6)
            res2 = minimize(obj, x1, method="L-BFGS-B", bounds=[(0.0, None)] * 6,
                            options={"ftol": 1e-15, "gtol": 1e-10, "maxiter": 500})
            if res2.fun < res.fun:
                phi = np.maximum(res2.x, floor)
        # observed information = Hessian of the REML deviance at phi (central diff)
        H = self._hessian(phi, data)
        Hinv = np.linalg.inv(H)
        self._last = dict(phi=phi, Hinv=Hinv, data=data, Ybar=data[0], converged=res.success)
        return self

    def _hessian_at(self, phi, data, h):
        """Central-difference Hessian at step vector h (numerically identical
        deviance_fast)."""
        n = 6
        H = np.zeros((n, n))
        eye = np.eye(n)

        def dev(p):
            return self.deviance_fast(np.maximum(p, 1e-14), data)[0]

        f0 = dev(phi)
        fp = np.array([dev(phi + h[j] * eye[j]) for j in range(n)])
        fm = np.array([dev(phi - h[j] * eye[j]) for j in range(n)])
        for j in range(n):
            H[j, j] = (fp[j] - 2 * f0 + fm[j]) / (h[j] ** 2)
        for j in range(n):
            for k in range(j + 1, n):
                fpp = dev(phi + h[j] * eye[j] + h[k] * eye[k])
                fpm = dev(phi + h[j] * eye[j] - h[k] * eye[k])
                fmp = dev(phi - h[j] * eye[j] + h[k] * eye[k])
                fmm = dev(phi - h[j] * eye[j] - h[k] * eye[k])
                H[j, k] = H[k, j] = (fpp - fpm - fmp + fmm) / (4 * h[j] * h[k])
        return H

    def _nu_monitor(self, phi, Hinv):
        """The two possible R11a Satterthwaite df (kappa in {0,1}) that the
        Richardson ladder must converge (rel change <= 1e-6, R11a)."""
        I, S, nb = self.I, self.S, self.n_rev
        s2ab, s2av, s2blk, s2e = phi[1], phi[3], phi[4], phi[5]
        out = []
        for kappa in (0.0, 1.0):
            var = (2.0 / I) * s2ab + (2.0 / S) * s2av + kappa * s2blk / nb + (2.0 / (I * S)) * s2e
            g = np.array([0.0, 2.0 / I, 0.0, 2.0 / S, kappa / nb, 2.0 / (I * S)])
            gCg = float(g @ (2.0 * Hinv) @ g)
            out.append((2.0 * var * var / gCg) if gCg > 1e-300 else float(self.N - self.p))
        return np.array(out)

    def _hessian(self, phi, data, rel=1e-3, tol_nu=1e-6, max_levels=4):
        """R11a: central-difference Hessian, Richardson-extrapolated by
        STEP-HALVING carried to CONVERGENCE -- successive Richardson diagonals
        must agree to relative change <= 1e-6 in the resulting nu-hat (both
        kappa=0 and kappa=1).  Returns the converged Hessian."""
        base_scale = np.maximum(np.abs(phi), np.max(phi) * 1e-3 + 1e-9)
        # Romberg tableau over step-halved central-difference Hessians.  Because
        # the deviance is finite-precision, deep step-halving eventually hits
        # ROUNDOFF (the 2nd-difference cancels catastrophically); the accurate
        # estimate is the diagonal at the truncation/roundoff BALANCE point, i.e.
        # the level of minimal successive nu-change.  Return that (converge early
        # if it clears tol_nu).
        raw = [self._hessian_at(phi, data, base_scale * rel)]
        tab = [[raw[0]]]
        diags = [raw[0]]                                   # T[k][k], the level-k estimate
        prev_nu = self._nu_monitor(phi, np.linalg.inv(raw[0]))
        best = (np.inf, raw[0], 0)                         # (successive rel-change, H, level)
        for k in range(1, max_levels + 1):
            raw.append(self._hessian_at(phi, data, base_scale * rel / (2 ** k)))
            row = [raw[k]]
            for j in range(1, k + 1):
                fac = 4.0 ** j
                row.append((fac * row[j - 1] - tab[k - 1][j - 1]) / (fac - 1.0))
            tab.append(row); diags.append(row[k])
            nu = self._nu_monitor(phi, np.linalg.inv(row[k]))
            rel_change = np.max(np.abs(nu - prev_nu) / np.maximum(np.abs(nu), 1e-30))
            if rel_change < best[0]:
                best = (rel_change, diags[k - 1], k - 1)   # estimate at the balance = the level BEFORE the min-change step
            if rel_change <= tol_nu:
                self._nu_ladder_relchange = float(rel_change); self._nu_ladder_levels = k
                return diags[k]
            prev_nu = nu
        self._nu_ladder_relchange = float(best[0]); self._nu_ladder_levels = best[2]
        return best[1]

    def contrast(self, xi, yi):
        """Registered arm-mean contrast theta = alpha_xi - alpha_yi (R10a map)."""
        phi = self._last["phi"]; Hinv = self._last["Hinv"]; Ybar = self._last["Ybar"]
        I, S, n_rev = self.I, self.S, self.n_rev
        theta = float(Ybar[xi].mean() - Ybar[yi].mean())   # OLS = GLS on this design
        rev_x = xi in self.reviewed_idx
        rev_y = yi in self.reviewed_idx
        kappa = 1.0 if (rev_x != rev_y) else 0.0           # exactly one reviewed
        s2ab, s2av, s2w, s2e = phi[1], phi[3], phi[4], phi[5]
        var = (2.0 / I) * s2ab + (2.0 / S) * s2av + kappa * s2w / n_rev + (2.0 / (I * S)) * s2e
        var = max(var, 1e-30)
        se = float(np.sqrt(var))
        # constant gradient g = (0, 2/I, 0, 2/S, kappa/n_rev, 2/(I*S))
        g = np.array([0.0, 2.0 / I, 0.0, 2.0 / S, kappa / n_rev, 2.0 / (I * S)])
        # Cov(phi_hat) = 2 * Hinv (observed info = H/2); nu = 2 Var^2 / (g^T Cov g)
        gCg = float(g @ (2.0 * Hinv) @ g)
        nu = (2.0 * var * var / gCg) if gCg > 1e-300 else float(self.N - self.p)
        nu = max(nu, 1.0)
        return ContrastFit(theta_hat=theta, se=se, nu=float(nu))

    # ---------- dense reference (correctness cross-check) ------------------
    def _build_dense(self):
        A, I = self.A, self.I
        Ione = np.eye(A * I)
        JA_II = np.kron(np.ones((A, A)), np.eye(I))
        JA_JI = np.kron(np.ones((A, A)), np.ones((I, I)))
        IA_JI = np.kron(np.eye(A), np.ones((I, I)))
        W = self.G @ self.G.T
        self._dense = dict(Ione=Ione, JA_II=JA_II, JA_JI=JA_JI, IA_JI=IA_JI, W=W)
        self._dense_ready = True

    def deviance_dense(self, phi, data):
        """Reference -2 REML log-lik via explicit A*I block matrices."""
        if not self._dense_ready:
            self._build_dense()
        A, I, S = self.A, self.I, self.S
        d = self._dense
        s2b, s2ab, s2v, s2av, s2w, s2e = phi
        Vmean = (s2e * d["Ione"] + S * s2b * d["JA_II"] + S * s2ab * d["Ione"]
                 + s2v * d["JA_JI"] + s2av * d["IA_JI"] + S * s2w * d["W"])
        Vcont = s2e * d["Ione"] + s2v * d["JA_JI"] + s2av * d["IA_JI"]
        Ybar, Yc = data
        Ym = np.sqrt(S) * Ybar.reshape(-1)
        cfm = cho_factor(Vmean); cfc = cho_factor(Vcont)
        Xm = np.sqrt(S) * np.kron(np.eye(A), np.ones((I, 1)))   # (AI, A)
        VmiX = cho_solve(cfm, Xm)
        XtVmiX = Xm.T @ VmiX
        beta = np.linalg.solve(XtVmiX, VmiX.T @ Ym)
        rm = Ym - Xm @ beta
        q_mean = float(rm @ cho_solve(cfm, rm))
        logdet_vm = 2 * np.sum(np.log(np.diag(np.linalg.cholesky(Vmean))))
        logdet_vc = 2 * np.sum(np.log(np.diag(np.linalg.cholesky(Vcont))))
        logdet_XtX = 2 * np.sum(np.log(np.diag(np.linalg.cholesky(XtVmiX))))
        q_c = 0.0
        for s in range(S):
            vc = Yc[:, :, s].reshape(-1)
            q_c += float(vc @ cho_solve(cfc, vc))
        dev = logdet_vm + (S - 1) * logdet_vc + logdet_XtX + q_mean + q_c
        return dev, beta, XtVmiX


def build_for_cell(t):
    """Composite family (B): reviewer block on reviewed arms, rotation
    (rev_off(a)+i) mod n_reviewers.  Uses n_nonce."""
    comp = list(pins.COMP_ARMS)
    rev_off = {comp.index(a): off for off, a in enumerate(pins.REVIEWED_ARMS)}
    covered = set(rev_off.keys())
    n_rev = pins.N_REVIEWERS

    def level_of(a, i):
        return (rev_off[a] + i) % n_rev
    return CompositeREML(A=len(comp), I=t.n_nonce, S=pins.N_SEEDS,
                         level_of=level_of, covered_arms=covered, n_block=n_rev)


_CACHE = {}


def get_comp(t):
    """Cached composite-family (B) exact-REML fitter (keyed by n_nonce)."""
    key = ("comp", t.n_nonce)
    if key not in _CACHE:
        _CACHE[key] = build_for_cell(t)
    return _CACHE[key]


def get_uct(t):
    """Cached UCT-family (A) exact-REML fitter (keyed by n_nat)."""
    key = ("uct", t.n_nat)
    if key not in _CACHE:
        _CACHE[key] = build_for_uct(t)
    return _CACHE[key]


def build_for_uct(t):
    """UCT family (A): consumer block on ALL arms, rotation (uct_arm_index+i) mod
    n_consumers (DIAGNOSTIC — R10a leaves family A on the pooled ANOVA; this exact
    fitter is used to test whether family A shares the family-B defect).  Uses n_nat."""
    A = len(pins.UCT_ARMS)
    n_cons = pins.N_CONSUMERS

    def level_of(a, i):
        return (a + i) % n_cons
    return CompositeREML(A=A, I=t.n_nat, S=pins.N_SEEDS,
                         level_of=level_of, covered_arms=set(range(A)), n_block=n_cons)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # local self-test: fast vs dense on config-0 composite data (host, any numpy).
    import seeds, grid, dgm
    idx, t = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
    R = build_for_cell(t)
    print(f"config_index={idx} A={R.A} I={R.I} S={R.S} n_rev={R.n_rev} "
          f"reviewed={sorted(R.reviewed_idx)}")
    max_dev = max_phi = 0.0
    for r in range(4):
        ss = seeds.rep_substreams(idx, r)
        Ycomp, _ = dgm.gen_composite_and_gate(t, ss, gate_thr=None)
        data = R._prep(Ycomp)
        phi_test = R._moment_start(Ycomp) + 1e-3
        df_dev, _, _ = R.deviance(phi_test, data)
        dd_dev, _, _ = R.deviance_dense(phi_test, data)
        max_dev = max(max_dev, abs(df_dev - dd_dev))
        # verify GLS == OLS and map == GLS-var at a fitted phi
        R.fit(Ycomp)
        phi = R._last["phi"]
        _, beta_f, XtVinvX = R.deviance(phi, data)
        _, beta_d, XtVmiX_d = R.deviance_dense(phi, data)
        ols = data[0].mean(axis=1)
        gls_err = np.max(np.abs(beta_f - ols))
        # map var for H-A2IR (kappa 0) and H-S(H) (kappa 1)
        H_i = pins.COMP_ARMS.index("H"); A2IR_i = pins.COMP_ARMS.index("A2IR")
        SH_i = pins.COMP_ARMS.index("S(H)")
        c1 = np.zeros(R.A); c1[H_i] = 1; c1[A2IR_i] = -1
        gls_var1 = float(c1 @ np.linalg.solve(XtVinvX, c1))
        map_var1 = (2/R.I)*phi[1] + (2/R.S)*phi[3] + 0.0 + (2/(R.I*R.S))*phi[5]
        c2 = np.zeros(R.A); c2[H_i] = 1; c2[SH_i] = -1
        gls_var2 = float(c2 @ np.linalg.solve(XtVinvX, c2))
        map_var2 = (2/R.I)*phi[1] + (2/R.S)*phi[3] + phi[4]/R.n_rev + (2/(R.I*R.S))*phi[5]
        print(f" rep{r}: |dev_fast-dev_dense|={abs(df_dev-dd_dev):.2e} "
              f"|beta_fast-OLS|={gls_err:.2e} "
              f"GLSvar-map (kap0)={abs(gls_var1-map_var1):.2e} "
              f"(kap1)={abs(gls_var2-map_var2):.2e} "
              f"phi={np.array2string(phi, precision=4)}")
        cf = R.contrast(H_i, A2IR_i)
        print(f"        H-A2IR: theta={cf.theta_hat:.5f} se={cf.se:.5f} nu={cf.nu:.3f}")
    print(f"max |dev_fast - dev_dense| over reps/phi = {max_dev:.2e}")
