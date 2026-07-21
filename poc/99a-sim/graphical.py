"""§4.6(2)(3)(4) graphical multiple-test procedure (Bretz et al. 2009).

Initial weights w0 = (C-VAL: 1.0, else 0); the pinned transition matrix G
(§4.6(3)); the sequentially-rejective update algorithm (§4.6(4)); claims tested
by IUT (claim p = max of component one-sided p-values; reject at local level
w(j)*alpha iff EVERY component p <= w(j)*alpha).  Total alpha = 0.05.

Weighted-Bonferroni intersection tests need no dependence model, so the crossed
random-effects correlation cannot invalidate the level (§4.6(2)(v)).
"""
import pins

CLAIMS = pins.CLAIMS

# initial weights (§4.6(3)): all mass on C-VAL
W0 = {c: (1.0 if c == 'C-VAL' else 0.0) for c in CLAIMS}

# transition matrix G (§4.6(3)); entries not shown are 0, rows sum <= 1
def _build_G():
    G = {i: {j: 0.0 for j in CLAIMS} for i in CLAIMS}
    G['C-VAL']['C-DEF-NSUP'] = 0.50
    for c in pins.CANDIDATES:
        G['C-VAL']['C-CON-SUP-%s' % c] = 0.125
    G['C-DEF-NSUP']['C-DEF-SUP'] = 1.00
    G['C-DEF-SUP']['C-GRAPH'] = 1.00
    for c in pins.CANDIDATES:
        G['C-CON-SUP-%s' % c]['C-GRAPH'] = 0.50
        G['C-CON-SUP-%s' % c]['C-FMT-%s' % c] = 0.50
    # C-GRAPH and C-FMT-c are terminal (no outgoing edges)
    return G

G_MATRIX = _build_G()


def validate_graph():
    """Verify the cited-theorem conditions (§4.6(2)(ii)(iii)): nonneg initial
    weights summing to 1; nonneg transitions, zero diagonal, row sums <= 1."""
    assert abs(sum(W0.values()) - 1.0) < 1e-12, 'initial weights must sum to 1'
    assert all(w >= 0 for w in W0.values())
    for i in CLAIMS:
        assert G_MATRIX[i][i] == 0.0, 'zero diagonal required'
        rowsum = sum(G_MATRIX[i].values())
        assert rowsum <= 1.0 + 1e-12, f'row {i} sums to {rowsum} > 1'
        assert all(v >= 0 for v in G_MATRIX[i].values())
    return True


class GraphState:
    """Mutable state of the sequentially-rejective graphical procedure."""
    def __init__(self, alpha=pins.ALPHA):
        self.alpha = alpha
        self.w = dict(W0)
        self.g = {i: dict(G_MATRIX[i]) for i in CLAIMS}
        self.active = set(CLAIMS)
        self.rejected = set()

    def _reject(self, j):
        self.rejected.add(j)
        wj = self.w[j]
        gj = self.g[j]
        for k in list(self.active):
            if k == j:
                continue
            self.w[k] += wj * gj[k]
        # standard graphical weight-update of the remaining edges
        new_g = {l: dict(self.g[l]) for l in self.active if l != j}
        for l in self.active:
            if l == j:
                continue
            glj = self.g[l][j]
            for k in self.active:
                if k == j or k == l:
                    continue
                denom = 1.0 - self.g[l][j] * self.g[j][l]
                if denom > 1e-15:
                    new_g[l][k] = (self.g[l][k] + glj * self.g[j][k]) / denom
        for l in self.active:
            if l == j:
                continue
            self.g[l] = new_g[l]
            self.g[l][j] = 0.0
        self.w[j] = 0.0
        self.active.discard(j)

    def run(self, comp_pvals, testable):
        """Iterate to a fixed point given current component p-values and
        testability.  comp_pvals[j] is a list of the claim's IUT component
        p-values (or None if not computable this replication)."""
        changed = True
        while changed:
            changed = False
            for j in list(self.active):
                if self.w[j] <= 0.0 or not testable.get(j, False):
                    continue
                ps = comp_pvals.get(j)
                if ps is None:
                    continue
                local = self.w[j] * self.alpha
                if all(p <= local for p in ps):     # IUT rejection
                    self._reject(j)
                    changed = True
                    break                            # restart scan after a rejection
        return self.rejected
