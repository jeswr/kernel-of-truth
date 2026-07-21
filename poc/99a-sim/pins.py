"""S3 pinned parameters (planning defaults) + S2 seed/version pins.

All values are the SIM-SPEC S3 "planning default" column of proposal-99a Rev8.
They are implemented as configuration constants (freeze-repinnable), never
hard-wired into algorithm logic.  Cross-references are to the sections of
docs/next/design/kernel-construction-methodology-proposal-99a.md.

NOTE on environment (reportable version mismatch, S2/R8g): the spec pins
CPython 3.12.x / numpy 2.1.3 / scipy 1.14.1.  This box runs CPython 3.9 /
numpy 2.0.2 / scipy 1.13.1.  Recorded here and in SPEC-DEFECTS.md; not a
resolution, a disclosed deviation for the mock build.
"""

# ---- S2 determinism / seed pins (R8g) ----
BASE_SEED = 990_066_001                # S2 pinned base seed
N_SUBSTREAMS = 13                      # .spawn(13) named children (S2)
# named substream indices (zero-based spawn order, normative, S2)
SS_NAT_CONCEPT   = 0   # natural-stratum concept-layer copula draws
SS_NONCE_CONCEPT = 1   # nonce concept layer + gate concept dimensions
SS_SEED_EFFECTS  = 2   # v_s and (av)_{a,s}, both strata
SS_REVIEWER      = 3   # reviewer effects
SS_CONSUMER      = 4   # consumer effects
SS_RESID_NAT     = 5   # residuals, natural
SS_RESID_NONCE   = 6   # residuals, nonce
SS_GATE_NOISE    = 7   # gate seed/reviewer/record latents
SS_STAGE2_FMT    = 8   # Stage-2 format data
SS_RUNG0         = 9   # rung-0 dataset
SS_PILOT         = 10  # pilot estimates
SS_COST_NOISE    = 11  # S4.9 cost-vector measurement noise
SS_GATE_BOOT     = 12  # S4.4 parametric-bootstrap draws

# per-cell bounded-Beta gate-threshold calibration stream (S4.4)
BETA_CAL_STREAM_TAG = 999_999_999

# ---- S3 pinned parameters (planning defaults) ----
ALPHA        = 0.05          # total FWER level
DELTA_S      = 0.10          # shuffle superiority margin (delta_S)
M_T          = 0.05          # T-contrast noninferiority margin
DELTA_T      = 0.08          # T-contrast superiority margin (>= m_T)
DELTA_G      = 0.08          # graph superiority margin
M_F          = 0.05          # format equivalence margin
PI0          = 0.60          # safety-gate floor (gate-pass rate)

N_NAT        = 48            # natural concepts, base
N_NAT_ESC    = 96            # natural concepts, escalated
N_NONCE      = 96            # nonce concepts, base
N_NONCE_ESC  = 160           # nonce concepts, escalated

SIGMA_UCT    = 0.15          # total SD, per-record paired UCT macro-BA diffs
SIGMA_COMP   = 0.20          # total SD, per-record paired composite diffs
SIGMA_F      = 0.10          # total SD, per-record paired Stage-2 host diffs

# variance-fraction decomposition (S4.1); families lacking a layer fold into resid
F_CONCEPT    = 0.50
F_SEED       = 0.10
F_REVIEWER   = 0.10
F_CONSUMER   = 0.10
F_RESID      = 0.20

N_SEEDS      = 3             # author seeds per arm (one matched list)
N_CONSUMERS  = 24            # UCT consumer pool
N_REVIEWERS  = 8             # reviewer pool (re-pinned 6->8 in Rev8)

RHO_REGIMES  = (0.0, 0.1, 0.5, 0.8)   # concept-layer copula correlation regimes
RHO_W        = 0.8           # block-sensitivity within-block correlation
RHO_B        = 0.3           # block-sensitivity between-block correlation

R_IR         = 0.10          # true rung-increment contrasts (nonce composite scale)
R_CIT        = 0.10
R_REV        = 0.10
M_IR         = 0.05          # rung-bar increment margins (selection hierarchy)
M_CIT        = 0.05
M_REV        = 0.05

ALPHA0       = 0.05          # Rung-0 futility level
L_LOOKS      = 3             # Rung-0 looks
F_FUT        = 0.05          # Rung-0 futility threshold f
# integer look table (S3 / S4.8 / S7-R8f): n_max -> (n1,n2,n3)
LOOK_TABLE = {96: (39, 68, 96), 160: (64, 112, 160)}

N_PILOT      = 12            # pilot concepts for Delta_rev estimation
SIGMA_PILOT  = 0.20          # pilot per-concept SD (s_p = sigma_pilot / sqrt(n_p))
KAPPA_POOL   = 0.25
KAPPA_MIX    = 0.25
KAPPA_BUDGET = 0.10
DELTA_MIN    = 0.02

D0_DEFAULT     = 0.20        # rung-0 true screen contrast default
DP0_DEFAULT    = 0.05        # rung-0 true pilot increment default
SB_DEFAULT     = 0           # transfer-shift sign default
SIGMA_SCR      = 0.20        # rung-0 screen-scale SD (= sigma_comp, R8f)
RHO_P          = 0.5         # pilot-estimate cross-route correlation

SELECTION_LEVEL = 0.95       # rung-bar one-sided selection level

# S4.9 TRUE per-arm component cost vectors (authoring, review, consumer, storage, ORC)
KAPPA_A = {
    'T':    (2, 0, 3, 2, 1),
    'A0':   (4, 0, 3, 1, 2),
    'A1':   (4, 6, 3, 1, 2),
    'A2':   (5, 6, 3, 1, 2),
    'A2IR': (6, 7, 3, 1, 2),
    'H':    (8, 10, 3, 2, 3),
    'E':    (12, 4, 3, 1, 2),
}
SIGMA_KAPPA = (0.1, 0.2, 0.1, 0.02, 0.2)   # per-component cost measurement SD
P_PRICE = (                                 # robustness PRICE-VECTOR set (5)
    (1, 1, 1, 1, 1),        # declared base prices
    (1, 2.5, 1, 1, 1),      # review-expensive
    (1, 0.4, 1, 1, 1),      # review-cheap
    (3, 0.5, 1, 1, 1),      # authoring-expensive
    (0.5, 1, 2.5, 1, 2.5),  # consumer/maintenance-expensive
)

DELTA_E      = -0.10         # true E-arm fidelity contrast default
M_SHEQ       = 0.05          # row-2 shuffle-equivalence margin
B_BOOT       = 999           # gate-test parametric-bootstrap replicates
TAU_TERM0    = 0.055         # F10 Rung-0 false-termination acceptance tolerance
TAU_FWER     = 0.055         # S6 FWER acceptance tolerance
TAU_TERM     = 0.025         # S7 P6 termination acceptance tolerance
POWER_FLOOR  = 0.90          # S7 floored-cell lower-bound acceptance

# bounded-Beta shape (S4.3/R8d)
BETA_A0, BETA_B0 = 2, 5

# replication counts (S6/S7)
R_FWER  = 40_000
R_POWER = 10_000

# ---- arm / candidate / claim indexing ----
# UCT family (natural), fixed order 0..9
UCT_ARMS = ['T', 'A1', 'A2', 'A2IR', 'H', 'S(T)', 'S(A1)', 'S(A2)', 'S(A2IR)', 'S(H)']
# composite family (nonce), fixed order 0..7
COMP_ARMS = ['A0', 'A1', 'A2', 'A2IR', 'H', 'E', 'S(H)', 'S(A2IR)']
# candidates
CANDIDATES = ['H', 'A2IR', 'A2', 'A1']
# reviewed arms (composite), fixed order 0..3
REVIEWED_ARMS = ['A1', 'A2', 'A2IR', 'H']
# gate arms
GATE_ARMS = ['H', 'A2IR', 'A2', 'A1']
# format versions per candidate
FORMATS = ['AST', 'VEC']
# rung-0 arms (5), fixed order
RUNG0_ARMS = ['T', 'A1', 'A2', 'A2IR', 'H']   # unreviewed forms of A1..H
RUNG0_ROUTES = ['A1', 'A2', 'A2IR', 'H']       # the four reviewed routes screened

# natural-stratum C-VAL shuffle arms
SH_NAT_ARMS = ['T', 'A1', 'A2', 'A2IR', 'H']
# nonce-stratum C-VAL shuffle arms
SH_NONCE_ARMS = ['H', 'A2IR']

# the 12 confirmatory claims
CLAIMS = [
    'C-VAL',
    'C-DEF-NSUP', 'C-DEF-SUP',
    'C-CON-SUP-H', 'C-CON-SUP-A2IR', 'C-CON-SUP-A2', 'C-CON-SUP-A1',
    'C-GRAPH',
    'C-FMT-H', 'C-FMT-A2IR', 'C-FMT-A2', 'C-FMT-A1',
]
STAGE1_CLAIMS = [c for c in CLAIMS if not c.startswith('C-FMT-')]
FMT_CLAIMS = [c for c in CLAIMS if c.startswith('C-FMT-')]
