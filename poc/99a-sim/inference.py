"""S4.2 registered-analysis contrast inference — balanced closed-form path.

The ledger (S4.6/(1b)) pins REML + Giesbrecht-Burns Satterthwaite with an
R/lme4/lmerTest reference implementation as the executable oracle, and S9
permits ANY numerically exact algorithm SUBJECT to a one-time fixture check
against lme4.  R is NOT available on this box and the fixture check is a
SEPARATE, DEFERRED validation (see SPEC-DEFECTS.md / README).

For the mock build we implement the OPERATIVE balanced closed-form contrast
test.  For any registered two-arm paired contrast theta = alpha_x - alpha_y the
matched record-level difference g_{i,s} = Y_{x,i,s} - Y_{y,i,s} follows a
balanced two-way (concept x seed) random-effects model
    g_{i,s} = theta + A_i + B_s + E_{i,s},
where A_i absorbs the concept x arm coordinates (and, when the arm is reviewed,
the concept-indexed reviewer effect r(a,i)), B_s the seed x arm effect, and
E_{i,s} the residual.  theta_hat = mean(g) is unbiased (= the GLS estimate under
balance); Var(theta_hat) and its Satterthwaite df are the classical balanced
combination of the concept/seed/residual mean squares (equal to REML in the
interior for balanced data).  Variance components are truncated at the
nonnegativity boundary (S4.2 pin).

Deviation from the letter of S4.2 (disclosed): a per-contrast difference fit
rather than the single joint arm-side REML fit; it yields a VALID (super-
uniform) t test — the property the FWER simulation validates — but is not
byte-identical to lme4, so the 1e-7 fixture check is deferred, not asserted.
"""
from dataclasses import dataclass
import numpy as np
from stats_util import t_cdf, t_ppf

_EPS = 1e-12


class FamilyAnova:
    """Balanced crossed-family ANOVA fitted ONCE per family per replication
    (arm fixed; concept, concept x arm, seed, seed x arm random; residual).
    Variance components are pooled across ALL arms — so the seed x arm
    component (the df bottleneck at n_seeds = 3) is estimated with
    (A-1)(S-1) df instead of the 2 df a single paired contrast would give.
    This is the balanced closed-form that equals REML in the interior for
    balanced data (S4.2 operative path).

    Documented conservatisms (deferred to the joint-lme4 fixture check):
      * consumer (UCT) / reviewer (composite reviewed arms) are crossed
        nuisance effects folded into the concept x arm / residual strata here;
        they CANCEL in every registered arm-mean contrast, so folding them in
        only mildly inflates the estimated contrast SE (conservative);
      * the composite residual is heteroscedastic across reviewed/unreviewed
        arms; the pooled residual is an average (affects only shuffle
        reviewed-vs-unreviewed components, never the UCT/Delta^G true nulls).
    """
    def __init__(self, Y):
        A, I, S = Y.shape
        self.A, self.I, self.S = A, I, S
        M = Y.mean()
        M_a = Y.mean(axis=(1, 2))
        M_i = Y.mean(axis=(0, 2))
        M_s = Y.mean(axis=(0, 1))
        M_ai = Y.mean(axis=2)
        M_as = Y.mean(axis=1)
        self.arm_mean = M_a

        SS_arm = I * S * np.sum((M_a - M) ** 2)
        SS_concept = A * S * np.sum((M_i - M) ** 2)
        SS_seed = A * I * np.sum((M_s - M) ** 2)
        SS_ab = S * np.sum((M_ai - M_a[:, None] - M_i[None, :] + M) ** 2)
        SS_av = I * np.sum((M_as - M_a[:, None] - M_s[None, :] + M) ** 2)
        SS_total = np.sum((Y - M) ** 2)
        SS_e = SS_total - SS_arm - SS_concept - SS_seed - SS_ab - SS_av

        self.df_ab = (A - 1) * (I - 1)
        self.df_av = (A - 1) * (S - 1)
        self.df_e = (A * I * S - 1) - (A - 1) - (I - 1) - (S - 1) - self.df_ab - self.df_av
        self.MS_ab = SS_ab / self.df_ab if self.df_ab > 0 else 0.0
        self.MS_av = SS_av / self.df_av if self.df_av > 0 else 0.0
        self.MS_e = SS_e / self.df_e if self.df_e > 0 else 0.0

    def contrast(self, xi, yi):
        """Registered arm-mean contrast theta = alpha_xi - alpha_yi."""
        I, S = self.I, self.S
        IS = I * S
        theta = float(self.arm_mean[xi] - self.arm_mean[yi])
        ab_active = self.MS_ab > self.MS_e
        av_active = (self.df_av > 0) and (self.MS_av > self.MS_e)
        var_ab = 2.0 * (self.MS_ab - self.MS_e) / IS if ab_active else 0.0
        var_av = 2.0 * (self.MS_av - self.MS_e) / IS if av_active else 0.0
        var_e = 2.0 * self.MS_e / IS
        var = max(var_ab + var_av + var_e, _EPS)
        se = float(np.sqrt(var))
        # Satterthwaite over the active mean squares
        lam = 2.0 / IS
        lamA = lam if ab_active else 0.0
        lamV = lam if av_active else 0.0
        lamE = lam * (1.0 - (1.0 if ab_active else 0.0) - (1.0 if av_active else 0.0))
        den = 0.0
        if ab_active:
            den += (lamA * self.MS_ab) ** 2 / self.df_ab
        if av_active:
            den += (lamV * self.MS_av) ** 2 / self.df_av
        if self.df_e > 0 and lamE != 0.0:
            den += (lamE * self.MS_e) ** 2 / self.df_e
        nu = (var ** 2 / den) if den > _EPS else float(self.df_e if self.df_e > 0 else 1.0)
        nu = max(nu, 1.0)
        return ContrastFit(theta_hat=theta, se=se, nu=float(nu))


@dataclass
class ContrastFit:
    theta_hat: float
    se: float
    nu: float

    def p_upper(self, theta0: float) -> float:
        """One-sided p for upper null H0: theta >= theta0 (S4.6/(1b))."""
        tstat = (self.theta_hat - theta0) / self.se
        return t_cdf(tstat, self.nu)

    def p_lower(self, theta0: float) -> float:
        """One-sided p for lower null H0: theta <= theta0."""
        tstat = (self.theta_hat - theta0) / self.se
        return 1.0 - t_cdf(tstat, self.nu)

    def upper_bound(self, gamma: float) -> float:
        """One-sided (1-gamma) UPPER confidence bound (test-CI duality)."""
        return self.theta_hat + t_ppf(1.0 - gamma, self.nu) * self.se

    def lower_bound(self, gamma: float) -> float:
        return self.theta_hat - t_ppf(1.0 - gamma, self.nu) * self.se


def paired_contrast(Yx: np.ndarray, Yy: np.ndarray) -> ContrastFit:
    """Balanced two-way random-effects test of theta = mean(Yx) - mean(Yy).

    Yx, Yy : (n_concepts, n_seeds) matched arm-side observations.
    """
    g = Yx - Yy
    I, S = g.shape
    grand = g.mean()
    gi = g.mean(axis=1)         # concept (row) means
    gs = g.mean(axis=0)         # seed (col) means

    df_A = I - 1
    df_B = S - 1
    df_E = (I - 1) * (S - 1)
    SS_A = S * np.sum((gi - grand) ** 2)
    SS_B = I * np.sum((gs - grand) ** 2)
    resid = g - gi[:, None] - gs[None, :] + grand
    SS_E = np.sum(resid ** 2)
    MS_A = SS_A / df_A
    MS_B = SS_B / df_B if df_B > 0 else 0.0
    MS_E = SS_E / df_E if df_E > 0 else 0.0

    # variance components with nonnegativity boundary (S4.2 pin)
    a_active = MS_A > MS_E
    b_active = (df_B > 0) and (MS_B > MS_E)
    a_hat = (MS_A - MS_E) / S if a_active else 0.0
    b_hat = (MS_B - MS_E) / I if b_active else 0.0

    var_hat = a_hat / I + b_hat / S + MS_E / (I * S)
    var_hat = max(var_hat, _EPS)
    se = float(np.sqrt(var_hat))

    # Satterthwaite df over the ACTIVE mean squares (Giesbrecht-Burns for the
    # balanced case reduces to the linear-combination Satterthwaite).
    #   lambda_A = 1/(IS) if a active else 0
    #   lambda_B = 1/(IS) if b active else 0
    #   lambda_E = (1 - [a active] - [b active]) / (IS)
    IS = I * S
    lamA = (1.0 / IS) if a_active else 0.0
    lamB = (1.0 / IS) if b_active else 0.0
    lamE = (1.0 - (1.0 if a_active else 0.0) - (1.0 if b_active else 0.0)) / IS
    num = var_hat ** 2
    den = 0.0
    if a_active:
        den += (lamA * MS_A) ** 2 / df_A
    if b_active:
        den += (lamB * MS_B) ** 2 / df_B
    if df_E > 0 and lamE != 0.0:
        den += (lamE * MS_E) ** 2 / df_E
    nu = num / den if den > _EPS else float(df_E if df_E > 0 else 1.0)
    nu = max(nu, 1.0)
    return ContrastFit(theta_hat=float(grand), se=se, nu=float(nu))
